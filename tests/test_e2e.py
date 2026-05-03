"""E2E wiring test for compose + deliver.

8 fixture photos → ``compose("wrapped", {"since": "7d"})`` → manifest
references existing PDF + MP4 files. Renderers are heavy (Chromium /
Remotion / ffmpeg); we set ``MEMORY_BOOK_RENDER_STUB=1`` so the renderer
step writes lightweight placeholder files instead of invoking the real
toolchain. The wiring under test is the orchestration, not the renderers
(those are covered in test_render.py).
"""
from __future__ import annotations

import datetime as dt
import importlib
import json
import time
from pathlib import Path

import piexif  # type: ignore[import-untyped]
import pytest
from PIL import Image


FIXTURES: list[tuple[str, dt.datetime, tuple[int, int, int]]] = [
    ("01_coffee",   dt.datetime(2026, 4, 28,  8, 30), (180, 140,  90)),
    ("02_books",    dt.datetime(2026, 4, 28,  9, 15), (160, 120,  80)),
    ("03_concert",  dt.datetime(2026, 4, 28, 21,  0), ( 40,  20, 200)),
    ("04_city",     dt.datetime(2026, 4, 28, 23, 30), ( 60,  30, 220)),
    ("05_beach",    dt.datetime(2026, 4, 30, 14,  0), (240, 200, 120)),
    ("06_sunset",   dt.datetime(2026, 4, 30, 18, 30), (250, 130,  70)),
    ("07_friends",  dt.datetime(2026, 4, 30, 20,  0), (200,  80,  80)),
    ("08_mountain", dt.datetime(2026, 5,  1,  9,  0), (100, 130, 110)),
]


def _make_jpeg(path: Path, taken: dt.datetime, color: tuple[int, int, int]) -> None:
    img = Image.new("RGB", (64, 64), color=color)
    exif = {
        "0th": {},
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: taken.strftime("%Y:%m:%d %H:%M:%S").encode()
        },
        "GPS": {},
        "1st": {},
        "thumbnail": None,
    }
    img.save(path, format="JPEG", exif=piexif.dump(exif))


@pytest.fixture()
def env(monkeypatch, tmp_path):
    monkeypatch.setenv("MEMORY_BOOK_HOME", str(tmp_path))
    monkeypatch.setenv("MEMORY_BOOK_VISION_STUB", "1")
    monkeypatch.setenv("MEMORY_BOOK_EMBED_FALLBACK", "1")
    monkeypatch.setenv("MEMORY_BOOK_RENDER_STUB", "1")
    monkeypatch.setenv("SUNO_API_KEY", "")  # force ambient fallback

    # Reload modules so module-level paths re-evaluate against the tempdir.
    import memory_book.src.store as store
    import memory_book.src.ingest as ingest
    import memory_book.src.cluster as cluster
    import memory_book.src.caption as caption
    import memory_book.src.narrative as narrative
    import memory_book.src.compose as compose
    for m in (store, ingest, cluster, caption, narrative, compose):
        importlib.reload(m)
    store.init_db()

    src = tmp_path / "incoming"
    src.mkdir()
    for name, taken, color in FIXTURES:
        p = src / f"{name}.jpg"
        _make_jpeg(p, taken, color)
        ingest.ingest_photo(str(p))

    return {"home": tmp_path, "compose": compose, "store": store}


def test_compose_wrapped_writes_manifest_with_pdf_and_mp4(env):
    t0 = time.monotonic()
    manifest = env["compose"].compose("wrapped", {"since": "7d"})
    elapsed = time.monotonic() - t0

    assert elapsed < 180, f"compose took {elapsed:.1f}s (budget 180s)"

    # Manifest TypedDict shape.
    for key in ("id", "template", "scenes", "pdf_path", "mp4_path", "score_path"):
        assert key in manifest, f"manifest missing {key!r}"
    assert manifest["template"] == "wrapped"
    assert isinstance(manifest["scenes"], list) and manifest["scenes"], "no scenes"

    # Files exist on disk.
    pdf = Path(manifest["pdf_path"])
    mp4 = Path(manifest["mp4_path"])
    score = Path(manifest["score_path"])
    assert pdf.exists() and pdf.stat().st_size > 0, f"missing PDF: {pdf}"
    assert mp4.exists() and mp4.stat().st_size > 0, f"missing MP4: {mp4}"
    assert score.exists() and score.stat().st_size > 0, f"missing score: {score}"

    # Manifest persisted under ~/.memory_book/artifacts/<id>/manifest.json.
    manifest_file = env["home"] / "artifacts" / manifest["id"] / "manifest.json"
    assert manifest_file.exists(), f"manifest not written to {manifest_file}"
    payload = json.loads(manifest_file.read_text())
    assert payload["id"] == manifest["id"]


def test_deliver_emits_media_tags(env, tmp_path):
    import memory_book.src.deliver as deliver
    importlib.reload(deliver)

    pdf = tmp_path / "p.pdf"; pdf.write_bytes(b"%PDF-1.4\n")
    mp4 = tmp_path / "v.mp4"; mp4.write_bytes(b"\x00\x00\x00")
    score = tmp_path / "s.mp3"; score.write_bytes(b"\xff\xfb")
    manifest = {
        "id": "demo",
        "template": "wrapped",
        "scenes": [],
        "pdf_path": str(pdf),
        "mp4_path": str(mp4),
        "score_path": str(score),
    }
    msg = deliver.send_to_telegram(manifest, chat_id="123")
    assert isinstance(msg, str) and msg
    assert f"MEDIA:{pdf}" in msg
    assert f"MEDIA:{mp4}" in msg


def test_register_recap_cron_writes_schedule(env, tmp_path):
    import memory_book.src.deliver as deliver
    importlib.reload(deliver)

    sid = deliver.register_recap_cron(
        cadence="0 21 * * 0",
        chat_id="123",
        template="wrapped",
    )
    assert isinstance(sid, str) and sid

    sched_file = env["home"] / "schedules" / f"{sid}.json"
    assert sched_file.exists()
    body = json.loads(sched_file.read_text())
    assert body["cadence"] == "0 21 * * 0"
    assert body["chat_id"] == "123"
    assert body["template"] == "wrapped"
