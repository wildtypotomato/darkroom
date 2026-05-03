"""End-to-end render checks: sample.json → poster.pdf + recap.mp4.

Heavy dependencies (Playwright Chromium, Node + Remotion, ffmpeg) are
optional — tests skip when they're missing rather than fail.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from memory_book.src.render_pdf import render_pdf
from memory_book.src.render_video import render_video

TEMPLATES = Path(__file__).resolve().parent.parent / "templates" / "wrapped"
SAMPLE = TEMPLATES / "sample.json"
OUT = Path("/tmp/render_test")


@pytest.fixture(autouse=True)
def _out_dir():
    OUT.mkdir(parents=True, exist_ok=True)
    yield


def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _load_sample() -> dict:
    return json.loads(SAMPLE.read_text())


def test_render_pdf_from_sample():
    pytest.importorskip("playwright.sync_api")
    pytest.importorskip("jinja2")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch().close()
    except Exception as e:
        pytest.skip(f"chromium not available: {e}")

    data = _load_sample()
    scenes = data["scenes"]
    stats = {k: v for k, v in data.items() if k not in ("scenes", "closing_line")}

    pdf = OUT / "poster.pdf"
    result = render_pdf(scenes, stats, data["closing_line"], str(pdf))

    assert result == str(pdf)
    assert pdf.exists()
    assert pdf.stat().st_size > 10_000
    assert pdf.read_bytes()[:4] == b"%PDF"


def test_render_pdf_idempotent():
    pytest.importorskip("playwright.sync_api")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch().close()
    except Exception as e:
        pytest.skip(f"chromium not available: {e}")

    data = _load_sample()
    scenes = data["scenes"]
    stats = {k: v for k, v in data.items() if k not in ("scenes", "closing_line")}

    a = OUT / "poster_a.pdf"
    b = OUT / "poster_b.pdf"
    render_pdf(scenes, stats, data["closing_line"], str(a))
    render_pdf(scenes, stats, data["closing_line"], str(b))
    # Same inputs produce same-size PDFs (timestamps differ inside; size is stable enough).
    assert abs(a.stat().st_size - b.stat().st_size) < a.stat().st_size * 0.05


@pytest.mark.skipif(not _have("npx") or not _have("ffmpeg") or not _have("ffprobe"),
                    reason="needs npx + ffmpeg + ffprobe")
def test_render_video_from_sample():
    if not (TEMPLATES / "video" / "node_modules").exists():
        pytest.skip("Remotion deps not installed (run render_sample.sh once)")

    data = _load_sample()
    score = OUT / "score.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi",
         "-i", "anullsrc=r=44100:cl=stereo", "-t", "30", str(score)],
        check=True, capture_output=True,
    )

    out = OUT / "recap.mp4"
    result = render_video(data["scenes"], str(score), str(out))

    assert result == str(out)
    assert out.exists()

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(out)],
        check=True, capture_output=True, text=True,
    )
    assert probe.stdout.strip().rstrip(",") == "1080,1920"
