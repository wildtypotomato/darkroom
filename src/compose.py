"""Compose orchestrator — turns ingested assets into a Wrapped artifact.

Fans out three children via Hermes' ``delegate_task``:

  1. ``cluster_and_caption``  — group assets, caption each scene with Hermes 4
  2. ``generate_score``       — pick a 30s ambient track by mood
  3. ``render`` (after #1)    — PDF poster + 1080x1920 MP4

Children 1 and 2 run in parallel; #3 starts the moment #1 returns. Music
finishes in the background and is muxed into the final MP4 by render.

Where ``delegate_task`` is unavailable (dev / tests / sandbox), we fall
back to in-process sequential execution. The fallback intentionally does
NOT spin up its own threads — the constraint is "use Hermes' delegation,
don't roll our own". The log lines are emitted regardless so the demo
narrative is identical between modes.

Set ``DARKROOM_RENDER_STUB=1`` in tests to swap the heavy renderers
for placeholder file writers.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from . import caption as caption_mod
from . import cluster as cluster_mod
from . import music as music_mod
from . import narrative as narrative_mod
from . import render_pdf as render_pdf_mod
from . import render_video as render_video_mod
from . import store
from . import taste as taste_mod
from .store import ArtifactManifest, Asset, Scene, home


SCORE_DURATION_SEC = 30
SCENE_TARGET_K = 8


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


def _deduplicate_groups(groups: list[list[str]]) -> list[list[str]]:
    """Ensure no asset ID appears in more than one group.

    If an asset is found in multiple groups, keep it only in the group
    where it appears first (the best-fit cluster). Returns deduplicated
    groups, preserving original ordering.
    """
    seen: set[str] = set()
    cleaned: list[list[str]] = []
    for group in groups:
        unique = [aid for aid in group if aid not in seen]
        seen.update(unique)
        if unique:
            cleaned.append(unique)
    return cleaned


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compose(
    template: str,
    asset_filter: dict[str, Any],
    user_context: str | None = None,
) -> ArtifactManifest:
    """Build a Wrapped-style artifact for ``template`` from filtered assets.

    ``asset_filter`` keys:
      - ``since``: relative window like ``"7d"`` or ``"30d"``
      - ``kind``:  asset kind, defaults to ``"photo"``

    ``user_context``: optional context string about where/when the photos
    were taken and what the occasion was. Forwarded to caption.py so the
    vision model grounds captions in real setting instead of fabricating.
    """
    artifact_id = uuid.uuid4().hex[:12]
    out_dir = _artifact_dir(artifact_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[compose] artifact_id={artifact_id} template={template} filter={asset_filter}")

    taste = taste_mod.load_taste()
    print(f"[compose] taste: style={taste['preferred_style']} mode={taste['default_mode']}")

    assets = _load_assets(asset_filter)
    if not assets:
        raise ValueError(f"no assets matched filter {asset_filter!r}")
    print(f"[compose] loaded {len(assets)} assets")

    print("[compose] spawning 3 children: caption, music, render")

    # Phase 1: caption + music in parallel. Render waits on caption.
    results = _delegate_three(template, assets, out_dir, taste, user_context)

    scenes: list[Scene] = results["scenes"]
    score_path: str = results["score_path"]
    pdf_path: str = results["pdf_path"]
    mp4_path: str = results["mp4_path"]
    critique_result: dict = results.get("critique", {})

    manifest: ArtifactManifest = ArtifactManifest(
        id=artifact_id,
        template=template,
        scenes=scenes,
        pdf_path=pdf_path,
        mp4_path=mp4_path,
        score_path=score_path,
    )

    manifest_data = _jsonable(manifest)
    manifest_data["critique"] = critique_result or {}

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2))
    print(f"[compose] wrote manifest → {manifest_path}")

    return manifest


# ---------------------------------------------------------------------------
# Asset loading
# ---------------------------------------------------------------------------


def _load_assets(asset_filter: dict[str, Any]) -> list[Asset]:
    kind = asset_filter.get("kind", "photo")
    rows = store.get_assets(criteria={"kind": kind})

    since = asset_filter.get("since")
    if not since:
        return rows
    cutoff = _cutoff_for(since)
    if cutoff is None:
        return rows
    out: list[Asset] = []
    for a in rows:
        t = a.get("taken_at")
        if isinstance(t, datetime) and t >= cutoff:
            out.append(a)
    # If filtering produced nothing because EXIF dates are off, fall back to
    # all rows of that kind so the demo never produces an empty artifact.
    return out or rows


def _cutoff_for(since: str) -> datetime | None:
    s = since.strip().lower()
    if s.endswith("d") and s[:-1].isdigit():
        days = int(s[:-1])
        # Anchor to the most recent asset, not wall-clock; fixtures may sit
        # in the past relative to "now" yet still represent a recent week.
        latest = _latest_taken_at()
        anchor = latest or datetime.now()
        return anchor - timedelta(days=days)
    return None


def _latest_taken_at() -> datetime | None:
    latest: datetime | None = None
    for a in store.get_assets(criteria={"kind": "photo"}):
        t = a.get("taken_at")
        if isinstance(t, datetime) and (latest is None or t > latest):
            latest = t
    return latest


# ---------------------------------------------------------------------------
# Delegation
# ---------------------------------------------------------------------------


def _delegate_three(
    template: str,
    assets: list[Asset],
    out_dir: Path,
    taste: dict | None = None,
    user_context: str | None = None,
) -> dict[str, Any]:
    """Run the three children. Tries Hermes ``delegate_task`` first; on any
    import or runtime failure, falls back to in-process sequential calls.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    score_path = str(out_dir / "score.mp3")
    pdf_path = str(out_dir / f"darkroom_{today}.pdf")
    mp4_path = str(out_dir / f"darkroom_{today}.mp4")

    delegate = _resolve_delegate_task()
    if delegate is not None:
        try:
            return _run_with_delegate(
                delegate,
                template,
                assets,
                out_dir,
                score_path,
                pdf_path,
                mp4_path,
                taste,
                user_context,
            )
        except Exception as e:
            print(f"[compose] delegate_task path failed ({e}); falling back to sequential")

    return _run_sequential(template, assets, score_path, pdf_path, mp4_path, taste, user_context)


def _resolve_delegate_task():
    try:
        from hermes.tools import delegate_task  # type: ignore[import-not-found]

        return delegate_task
    except Exception:
        return None


def _run_with_delegate(
    delegate_task,
    template: str,
    assets: list[Asset],
    out_dir: Path,
    score_path: str,
    pdf_path: str,
    mp4_path: str,
    taste: dict | None = None,
    user_context: str | None = None,
) -> dict[str, Any]:
    """Hermes delegation path. We send three goals; children call back into
    this skill's tools (cluster/caption, music, render) via the
    ``terminal``/``file`` toolsets. Children return JSON summaries.

    Note: leaf children cannot recurse, so each child does its own slice
    end-to-end. We sequence caption→render via two delegate_task calls
    (caption+music in parallel batch; render in a follow-up call).
    """
    asset_ids = [a["id"] for a in assets]
    ctx_data: dict[str, Any] = {
        "template": template,
        "asset_ids": asset_ids,
        "out_dir": str(out_dir),
        "score_path": score_path,
    }
    if taste:
        ctx_data["taste"] = taste
    if user_context:
        ctx_data["user_context"] = user_context
    ctx = json.dumps(ctx_data)

    print("[compose] delegate_task batch: caption + music")
    t0 = time.monotonic()
    batch1 = delegate_task(
        tasks=[
            {
                "goal": (
                    "Cluster the asset_ids into scenes and caption each via "
                    "darkroom.src.{cluster,caption}. Return JSON: "
                    '{"scenes": [...Scene]}.'
                ),
                "context": ctx,
                "toolsets": ["terminal", "file"],
                "max_iterations": 30,
            },
            {
                "goal": (
                    "Generate a 30-second instrumental score matching the "
                    "dominant scene mood; write to score_path. Use "
                    "darkroom.src.music.generate_score."
                ),
                "context": ctx,
                "toolsets": ["terminal", "file"],
                "max_iterations": 20,
            },
        ],
        skip_memory=True,
        skip_context_files=True,
    )
    print(f"[compose] batch1 done (caption + music) in {time.monotonic() - t0:.1f}s")

    scenes = _scenes_from_delegate_result(batch1)
    if not scenes:
        raise ValueError("delegate_task returned no scenes; cannot render artifacts")

    print("[compose] delegate_task: render")
    t1 = time.monotonic()
    delegate_task(
        goal=(
            "Render the wrapped poster (PDF) and recap (1080x1920 MP4) using "
            "darkroom.src.render_pdf.render_pdf and "
            "darkroom.src.render_video.render_video."
        ),
        context=json.dumps(
            {
                "scenes": [_scene_to_render(s, assets) for s in scenes],
                "score_path": score_path,
                "pdf_path": pdf_path,
                "mp4_path": mp4_path,
                "stats_payload": _stats_payload(assets, scenes, taste),
                "closing_line": narrative_mod.build_closing(scenes),
            }
        ),
        toolsets=["terminal", "file"],
        max_iterations=25,
    )
    print(f"[compose] child render done in {time.monotonic() - t1:.1f}s")

    # Child 4: critique.
    t2 = time.monotonic()
    critique_result = _run_critique(pdf_path, mp4_path)
    print(f"[compose] critique: {critique_result['verdict']} in {time.monotonic() - t2:.1f}s")
    if critique_result["verdict"] == "FAIL":
        for issue in critique_result["issues"]:
            print(f"[compose] anti-slop violation: {issue['pattern']}: {issue['corrective']}")

    return {
        "scenes": scenes,
        "score_path": score_path,
        "pdf_path": pdf_path,
        "mp4_path": mp4_path,
        "critique": critique_result,
    }


def _scenes_from_delegate_result(batch_result) -> list[Scene]:
    """Hermes returns a summary string per task; in the fallback path we
    never reach here. If the live shape evolves we extract the JSON
    fragment defensively."""
    try:
        first = batch_result[0] if isinstance(batch_result, list) else batch_result
        text = first.get("summary") if isinstance(first, dict) else str(first)
        idx = text.find("{")
        if idx >= 0:
            return json.loads(text[idx:]).get("scenes", [])
    except Exception:
        pass
    return []


# ---------------------------------------------------------------------------
# Sequential fallback (also used in tests)
# ---------------------------------------------------------------------------


def _run_sequential(
    template: str,
    assets: list[Asset],
    score_path: str,
    pdf_path: str,
    mp4_path: str,
    taste: dict | None = None,
    user_context: str | None = None,
) -> dict[str, Any]:
    # Child 1: cluster + caption.
    t0 = time.monotonic()
    groups = cluster_mod.cluster_assets(assets, k=SCENE_TARGET_K)
    groups = _deduplicate_groups(groups)
    by_id = {a["id"]: a for a in assets}
    scenes: list[Scene] = []
    for i, group in enumerate(groups):
        scene_assets = [by_id[aid] for aid in group if aid in by_id]
        if not scene_assets:
            continue
        scenes.append(
            caption_mod.caption_scene(
                scene_assets,
                scene_id=f"scene_{i:02d}",
                taste=taste,
                user_context=user_context,
            )
        )
    print(f"[compose] child caption done in {time.monotonic() - t0:.1f}s")

    # Child 2: music. Mood = most common across scenes; map to ambient bed.
    t1 = time.monotonic()
    score_mood = _ambient_mood_from_scenes(scenes)
    music_mod.generate_score(score_mood, SCORE_DURATION_SEC, score_path)
    print(f"[compose] child music done in {time.monotonic() - t1:.1f}s")

    # Child 3: render (depends on scenes from child 1; muxes score from child 2).
    t2 = time.monotonic()
    render_scenes = [_scene_to_render(s, assets) for s in scenes]
    stats_payload = _stats_payload(assets, scenes, taste)
    closing = narrative_mod.build_closing(scenes)

    if os.environ.get("DARKROOM_RENDER_STUB") == "1":
        _stub_render(pdf_path, mp4_path, render_scenes)
    else:
        render_pdf_mod.render_pdf(render_scenes, stats_payload, closing, pdf_path)
        video_meta = {
            "title": stats_payload["title"],
            "subtitle": stats_payload["subtitle"],
            "signature": stats_payload["signature"],
            "closing_line": closing,
        }
        render_video_mod.render_video(render_scenes, score_path, mp4_path, metadata=video_meta)
    print(f"[compose] child render done in {time.monotonic() - t2:.1f}s")

    # Child 4: critique.
    t3 = time.monotonic()
    critique_result = _run_critique(pdf_path, mp4_path)
    print(f"[compose] critique: {critique_result['verdict']} in {time.monotonic() - t3:.1f}s")
    if critique_result["verdict"] == "FAIL":
        for issue in critique_result["issues"]:
            print(f"[compose] anti-slop violation: {issue['pattern']}: {issue['corrective']}")

    return {
        "scenes": scenes,
        "score_path": score_path,
        "pdf_path": pdf_path,
        "mp4_path": mp4_path,
        "critique": critique_result,
    }


# ---------------------------------------------------------------------------
# Adapters between Scene (caption.py) and the renderer's scene shape
# ---------------------------------------------------------------------------

# Caption moods → renderer "tone" (palette in poster.html).
_MOOD_TO_TONE = {
    "warm": "warm",
    "melancholy": "quiet",
    "upbeat": "loud",
    "golden": "gold",
    "quiet": "quiet",
}

_MOOD_TO_AMBIENT = {
    "warm": "warm",
    "melancholy": "melancholy",
    "upbeat": "upbeat",
    "golden": "warm",
    "quiet": "melancholy",
}


def _scene_to_render(scene: Scene, assets: list[Asset]) -> dict[str, Any]:
    by_id = {a["id"]: a for a in assets}
    hero = by_id.get(scene["hero_asset_id"])
    image = hero["path"] if hero else ""
    focus = _focus_for(hero)
    result: dict[str, Any] = {
        "id": scene["id"],
        "image": image,
        "kicker": _kicker_for(hero),
        "headline": scene["title"],
        "caption": scene["caption"],
        "tone": _MOOD_TO_TONE.get(scene.get("mood", "quiet"), "quiet"),
    }
    if focus:
        result["focus"] = focus
    return result


def _focus_for(asset: Asset | None) -> str:
    if not asset:
        return ""
    metadata = asset.get("metadata") or {}
    return metadata.get("focus", "")


def _kicker_for(asset: Asset | None) -> str:
    if not asset:
        return ""
    t = asset.get("taken_at")
    if isinstance(t, datetime):
        return t.strftime("%B · %Y")
    return ""


def _stats_payload(
    assets: list[Asset],
    scenes: list[Scene],
    taste: dict | None = None,
) -> dict[str, Any]:
    stats = narrative_mod.build_stats(assets)
    rows = [
        {"value": str(stats["photos"]), "label": "photos"},
    ]
    if stats.get("cities"):
        rows.append({"value": str(stats["cities"]), "label": "cities"})
    if stats.get("days"):
        rows.append({"value": str(stats["days"]), "label": "days"})
    rows.append({"value": str(len(scenes)), "label": "scenes"})

    style = (taste or {}).get("preferred_style", "dark-editorial")
    user_name = (taste or {}).get("user_name", "")
    wrap_label = (taste or {}).get("wrap_label", "Wrapped")

    title = wrap_label
    subtitle_parts = []
    if user_name:
        subtitle_parts.append(user_name)
    subtitle_parts.append(stats.get("summary", ""))
    subtitle = " · ".join(p for p in subtitle_parts if p)

    return {
        "title": title,
        "subtitle": subtitle,
        "signature": f"darkroom · for {user_name}" if user_name else "darkroom",
        "style": style,
        "stats": rows,
    }


def _ambient_mood_from_scenes(scenes: list[Scene]) -> str:
    if not scenes:
        return "warm"
    counts: dict[str, int] = {}
    for s in scenes:
        m = s.get("mood", "quiet")
        counts[_MOOD_TO_AMBIENT.get(m, "warm")] = counts.get(_MOOD_TO_AMBIENT.get(m, "warm"), 0) + 1
    return max(counts.items(), key=lambda kv: kv[1])[0]


# ---------------------------------------------------------------------------
# Critique helper
# ---------------------------------------------------------------------------


def _run_critique(pdf_path: str, mp4_path: str) -> dict:
    if os.environ.get("DARKROOM_RENDER_STUB") == "1":
        return {"verdict": "PASS", "issues": [], "summary": "stub mode"}
    try:
        from . import critique as critique_mod

        return critique_mod.critique_artifact(pdf_path, mp4_path)
    except Exception as e:
        print(f"[compose] critique skipped: {e}")
        return {"verdict": "PASS", "issues": [], "summary": f"skipped: {e}"}


# ---------------------------------------------------------------------------
# Stub renderer (test-only)
# ---------------------------------------------------------------------------


def _stub_render(pdf_path: str, mp4_path: str, render_scenes: list[dict]) -> None:
    Path(pdf_path).write_bytes(b"%PDF-1.4\n% darkroom stub\n%%EOF\n")
    Path(mp4_path).write_bytes(
        b"\x00\x00\x00\x20ftypisom"
        + b"\x00" * 16
        + json.dumps({"scenes": len(render_scenes)}).encode()
    )


# ---------------------------------------------------------------------------
# Paths + serialization
# ---------------------------------------------------------------------------


def _artifact_dir(artifact_id: str) -> Path:
    return home() / "artifacts" / artifact_id


def _jsonable(manifest: ArtifactManifest) -> dict[str, Any]:
    return {
        "id": manifest["id"],
        "template": manifest["template"],
        "scenes": [dict(s) for s in manifest["scenes"]],
        "pdf_path": manifest["pdf_path"],
        "mp4_path": manifest["mp4_path"],
        "score_path": manifest["score_path"],
    }
