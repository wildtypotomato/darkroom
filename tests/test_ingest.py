"""Unit tests for the ingestion path: photo upload → asset row in SQLite."""
from __future__ import annotations

import datetime as dt
import io
import os
import sqlite3
import tempfile
from pathlib import Path

import pytest
from PIL import Image
import piexif  # type: ignore[import-untyped]

# Tests must run before the modules pin a permanent DB path. We redirect
# both the asset directory and the SQLite path to a per-test tempdir via env.
TEST_HOME = None  # populated in fixture


@pytest.fixture()
def isolated_store(monkeypatch, tmp_path):
    """Point store + ingest at a tempdir so we don't touch ~/.darkroom."""
    monkeypatch.setenv("DARKROOM_HOME", str(tmp_path))
    # Force re-import so module-level constants pick up the env var.
    import importlib
    import darkroom.src.store as store
    import darkroom.src.ingest as ingest
    importlib.reload(store)
    importlib.reload(ingest)
    store.init_db()
    return store, ingest, tmp_path


def _make_jpeg_with_exif(path: Path, taken: dt.datetime) -> None:
    """Write a minimal JPEG with DateTimeOriginal set to `taken`."""
    img = Image.new("RGB", (32, 32), color=(180, 90, 60))
    exif_dict = {
        "0th": {},
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: taken.strftime("%Y:%m:%d %H:%M:%S").encode()
        },
        "GPS": {},
        "1st": {},
        "thumbnail": None,
    }
    exif_bytes = piexif.dump(exif_dict)
    img.save(path, format="JPEG", exif=exif_bytes)


def test_ingest_photo_creates_db_row_with_exif(isolated_store):
    store, ingest, home = isolated_store
    src = home / "incoming.jpg"
    taken = dt.datetime(2026, 4, 1, 14, 30, 0)
    _make_jpeg_with_exif(src, taken)

    asset_id = ingest.ingest_photo(str(src))

    assert asset_id, "ingest_photo must return a non-empty id"
    # File copied into <home>/assets/<id>.jpg
    assets_dir = home / "assets"
    saved = list(assets_dir.glob(f"{asset_id}*"))
    assert len(saved) == 1, f"expected one saved asset, found {saved}"

    rows = store.get_assets({})
    assert len(rows) == 1
    row = rows[0]
    assert row["id"] == asset_id
    assert row["kind"] == "photo"
    assert row["path"] == str(saved[0])
    assert row["taken_at"] == taken
    assert row["tags"] == []
    assert row["embedding"] is None


def test_get_assets_filters_by_kind(isolated_store):
    store, ingest, home = isolated_store
    src = home / "p.jpg"
    _make_jpeg_with_exif(src, dt.datetime(2026, 1, 1, 0, 0, 0))
    ingest.ingest_photo(str(src))

    photos = store.get_assets({"kind": "photo"})
    voices = store.get_assets({"kind": "voice"})
    assert len(photos) == 1
    assert voices == []


def test_update_embedding_writes_blob(isolated_store):
    store, ingest, home = isolated_store
    src = home / "p.jpg"
    _make_jpeg_with_exif(src, dt.datetime(2026, 2, 2, 0, 0, 0))
    asset_id = ingest.ingest_photo(str(src))

    blob = b"\x01\x02\x03fakeembedding"
    store.update_embedding(asset_id, blob)

    rows = store.get_assets({})
    assert rows[0]["embedding"] == blob


def test_ingest_photo_without_exif_still_succeeds(isolated_store):
    store, ingest, home = isolated_store
    src = home / "no_exif.jpg"
    Image.new("RGB", (16, 16), color=(20, 20, 20)).save(src, format="JPEG")

    asset_id = ingest.ingest_photo(str(src))
    rows = store.get_assets({})
    assert len(rows) == 1
    assert rows[0]["taken_at"] is None
    assert rows[0]["lat"] is None
    assert rows[0]["lon"] is None
