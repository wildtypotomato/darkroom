"""Evaluate rendered artifacts against the anti-slop rubric.

Screenshots the PDF and samples video frames, then sends them to Hermes 4
vision via delegate_task to check for named anti-patterns from
``references/anti_slop.md``.

Test mode: set ``DARKROOM_VISION_STUB=1`` to short-circuit the API call
and return PASS with no issues. Same env var as ``caption.py``.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import TypedDict

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class CritiqueIssue(TypedDict):
    pattern: str       # e.g. "#1 The Spotify Wrapped Clone"
    severity: str      # "critical" or "cosmetic"
    corrective: str    # what to fix


class CritiqueResult(TypedDict):
    verdict: str       # "PASS", "WARN", or "FAIL"
    issues: list[CritiqueIssue]
    summary: str       # one-line human summary


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_RUBRIC_PATH = Path(__file__).resolve().parent.parent / "references" / "anti_slop.md"

VIDEO_SAMPLE_FRAMES = 5


def _resolve_delegate_task():
    try:
        from hermes.tools import delegate_task  # type: ignore[import-not-found]
        return delegate_task
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def critique_pdf(pdf_path: str) -> CritiqueResult:
    """Screenshot the PDF and run anti-slop check."""
    if _is_stub():
        return _stub_result()

    rubric = _load_rubric()
    if rubric is None:
        return _rubric_missing_result()

    screenshot = _screenshot_pdf(pdf_path)
    if screenshot is None:
        return _pass_with_warning("could not screenshot PDF; skipping critique")

    try:
        return _vision_critique(
            images=[screenshot],
            rubric=rubric,
            artifact_type="PDF poster",
        )
    finally:
        Path(screenshot).unlink(missing_ok=True)


def critique_video(mp4_path: str) -> CritiqueResult:
    """Sample 5 evenly-spaced frames from the MP4 and run anti-slop check."""
    if _is_stub():
        return _stub_result()

    rubric = _load_rubric()
    if rubric is None:
        return _rubric_missing_result()

    frames = _extract_video_frames(mp4_path)
    if not frames:
        return _pass_with_warning("could not extract video frames; skipping critique")

    try:
        return _vision_critique(
            images=frames,
            rubric=rubric,
            artifact_type="9:16 MP4 video",
        )
    finally:
        for f in frames:
            Path(f).unlink(missing_ok=True)
        if frames:
            parent = Path(frames[0]).parent
            if parent.name.startswith("critique_frames_"):
                shutil.rmtree(parent, ignore_errors=True)


def critique_artifact(pdf_path: str, mp4_path: str) -> CritiqueResult:
    """Combined critique of both outputs. FAIL if either fails."""
    if _is_stub():
        return _stub_result()

    pdf_result = critique_pdf(pdf_path)
    video_result = critique_video(mp4_path)

    all_issues = pdf_result["issues"] + video_result["issues"]
    verdict = _compute_verdict(all_issues)
    parts = [r["summary"] for r in (pdf_result, video_result) if r["summary"]]
    summary = "; ".join(parts) or "no issues detected"

    return CritiqueResult(
        verdict=verdict,
        issues=all_issues,
        summary=summary,
    )


# ---------------------------------------------------------------------------
# Stub / skip helpers
# ---------------------------------------------------------------------------

def _is_stub() -> bool:
    return os.environ.get("DARKROOM_VISION_STUB") == "1"


def _stub_result() -> CritiqueResult:
    return CritiqueResult(verdict="PASS", issues=[], summary="stub mode")


def _rubric_missing_result() -> CritiqueResult:
    return CritiqueResult(
        verdict="PASS",
        issues=[],
        summary="anti_slop.md not found; skipping critique",
    )


def _pass_with_warning(message: str) -> CritiqueResult:
    return CritiqueResult(verdict="PASS", issues=[], summary=message)


# ---------------------------------------------------------------------------
# Rubric loading
# ---------------------------------------------------------------------------

def _load_rubric() -> str | None:
    """Read anti_slop.md from the package directory. Returns None if missing."""
    if _RUBRIC_PATH.exists():
        return _RUBRIC_PATH.read_text(encoding="utf-8")
    return None


# ---------------------------------------------------------------------------
# PDF screenshot (Playwright)
# ---------------------------------------------------------------------------

def _screenshot_pdf(pdf_path: str) -> str | None:
    """Render the PDF's companion HTML as a PNG. Returns the PNG path or None.

    The render_pdf step writes an HTML file alongside the PDF — we screenshot
    that rather than the PDF itself, which gives us a pixel-accurate view
    of what Playwright rendered.
    """
    html_path = Path(pdf_path).with_suffix(".html")
    if not html_path.exists():
        # Fall back: try to screenshot the PDF directly via a file:// URL.
        # Chromium can display PDFs but the result is less reliable.
        target = Path(pdf_path)
        if not target.exists():
            return None
        html_path = target

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    tmp = tempfile.NamedTemporaryFile(suffix=".png", prefix="critique_pdf_", delete=False)
    tmp.close()
    screenshot_path = Path(tmp.name)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1080, "height": 1920})
            page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
            page.wait_for_timeout(500)
            page.screenshot(path=str(screenshot_path), full_page=True)
            browser.close()
        return str(screenshot_path)
    except Exception:
        screenshot_path.unlink(missing_ok=True)
        return None


# ---------------------------------------------------------------------------
# Video frame extraction (ffmpeg)
# ---------------------------------------------------------------------------

def _extract_video_frames(mp4_path: str) -> list[str]:
    """Extract evenly-spaced frames from the video. Returns list of PNG paths."""
    if not Path(mp4_path).exists():
        return []

    # Get total frame count via ffprobe.
    total = _get_frame_count(mp4_path)
    if total <= 0:
        return []

    n = min(VIDEO_SAMPLE_FRAMES, total)
    if n == 0:
        return []

    # Calculate evenly-spaced frame numbers.
    if total == 1:
        frame_nums = [0]
    else:
        step = (total - 1) / (n - 1) if n > 1 else 0
        frame_nums = [round(step * i) for i in range(n)]

    # Build ffmpeg select filter.
    selects = "+".join(f"eq(n\\,{f})" for f in frame_nums)
    out_dir = Path(tempfile.mkdtemp(prefix="critique_frames_"))
    out_pattern = str(out_dir / "frame_%d.png")

    try:
        subprocess.run(
            [
                "ffmpeg", "-i", mp4_path,
                "-vf", f"select='{selects}'",
                "-vsync", "vfr",
                out_pattern,
            ],
            check=True,
            capture_output=True,
            timeout=30,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return []

    frames = sorted(out_dir.glob("frame_*.png"))
    frame_paths = [str(f) for f in frames]
    if not frame_paths:
        shutil.rmtree(out_dir, ignore_errors=True)
    return frame_paths


def _get_frame_count(mp4_path: str) -> int:
    """Use ffprobe to get the number of video frames."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-count_frames",
                "-select_streams", "v:0",
                "-show_entries", "stream=nb_read_frames",
                "-of", "csv=p=0",
                mp4_path,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return int(result.stdout.strip())
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
            FileNotFoundError, ValueError):
        return 0


# ---------------------------------------------------------------------------
# Vision API call
# ---------------------------------------------------------------------------

def _vision_critique(
    images: list[str],
    rubric: str,
    artifact_type: str,
) -> CritiqueResult:
    """Send images to Hermes vision via delegate_task with the anti-slop rubric."""
    delegate = _resolve_delegate_task()
    if delegate is None:
        return _pass_with_warning("no delegate_task available; skipping critique")

    system_prompt = (
        "You are a design quality reviewer. You evaluate rendered artifacts "
        "against a specific anti-slop rubric.\n\n"
        "## Anti-Slop Rubric\n\n"
        f"{rubric}\n\n"
        "## Instructions\n\n"
        f"Evaluate this {artifact_type} against the anti-slop rubric. "
        "For each detected violation, name the specific anti-pattern number "
        "and name. Respond in JSON: "
        '{"verdict": "PASS|WARN|FAIL", '
        '"issues": [{"pattern": "#N Pattern Name", '
        '"severity": "critical|cosmetic", '
        '"corrective": "what to fix"}], '
        '"summary": "one line"}.\n\n'
        "Severity guide:\n"
        "- critical: fundamentally undermines design quality (slop patterns "
        "#1-#8, #21-#22, #25-#28)\n"
        "- cosmetic: noticeable but not disqualifying (#9-#20, #23-#24, #29-#34)\n\n"
        "Return ONLY the JSON, no prose."
    )

    try:
        result = delegate(
            goal=system_prompt,
            context=json.dumps({"image_paths": images, "artifact_type": artifact_type}),
            toolsets=["terminal", "file"],
            max_iterations=15,
        )
        text = result.get("summary") if isinstance(result, dict) else str(result)
        return _parse_critique_response(text)
    except Exception as e:
        msg = f"delegate_task critique failed: {type(e).__name__}"
        return _pass_with_warning(msg)


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------

def _parse_critique_response(text: str) -> CritiqueResult:
    """Parse the JSON response from the vision model. Handles malformed
    responses gracefully by returning PASS with a warning."""
    text = text.strip()

    # Strip markdown code fences if present.
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

    parsed = None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        # Try extracting the first JSON object.
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group(0))
            except json.JSONDecodeError:
                pass

    if not isinstance(parsed, dict):
        return _pass_with_warning("could not parse critique response as JSON")

    # Validate and normalize the response.
    verdict = parsed.get("verdict", "").upper()
    if verdict not in ("PASS", "WARN", "FAIL"):
        # Infer from issues if verdict is missing/invalid.
        issues = _normalize_issues(parsed.get("issues", []))
        verdict = _compute_verdict(issues)
    else:
        issues = _normalize_issues(parsed.get("issues", []))
        # Override verdict based on actual severity of issues.
        verdict = _compute_verdict(issues) if issues else verdict

    summary = parsed.get("summary", "")
    if not isinstance(summary, str):
        summary = str(summary)

    return CritiqueResult(verdict=verdict, issues=issues, summary=summary)


def _normalize_issues(raw: list) -> list[CritiqueIssue]:
    """Normalize issue dicts, tolerating missing or misspelled keys."""
    if not isinstance(raw, list):
        return []

    issues: list[CritiqueIssue] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        pattern = str(item.get("pattern", item.get("name", "unknown")))
        severity = str(item.get("severity", "cosmetic")).lower()
        if severity not in ("critical", "cosmetic"):
            severity = "cosmetic"
        corrective = str(item.get("corrective", item.get("fix", "")))
        issues.append(CritiqueIssue(
            pattern=pattern,
            severity=severity,
            corrective=corrective,
        ))
    return issues


def _compute_verdict(issues: list[CritiqueIssue]) -> str:
    """Any critical issue → FAIL. Only cosmetic → WARN. None → PASS."""
    if not issues:
        return "PASS"
    for issue in issues:
        if issue.get("severity") == "critical":
            return "FAIL"
    return "WARN"


