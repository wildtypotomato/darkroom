"""End-to-end test for cluster → caption → narrative.

Creates 8 EXIF-tagged JPEGs across two days, runs them through the full
generation pipeline with vision stubbed out, and asserts the output Scene
dicts match the TypedDict contract from store.py.
"""
from __future__ import annotations

import datetime as dt
import importlib
from pathlib import Path

import piexif  # type: ignore[import-untyped]
import pytest
from PIL import Image


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def env(monkeypatch, tmp_path):
    monkeypatch.setenv("DARKROOM_HOME", str(tmp_path))
    monkeypatch.setenv("DARKROOM_VISION_STUB", "1")
    monkeypatch.setenv("DARKROOM_EMBED_FALLBACK", "1")

    # Reload so module-level paths re-evaluate against the tempdir.
    import darkroom.src.store as store
    import darkroom.src.ingest as ingest
    import darkroom.src.cluster as cluster
    import darkroom.src.caption as caption
    import darkroom.src.narrative as narrative
    for m in (store, ingest, cluster, caption, narrative):
        importlib.reload(m)
    store.init_db()
    return {
        "store": store,
        "ingest": ingest,
        "cluster": cluster,
        "caption": caption,
        "narrative": narrative,
        "home": tmp_path,
    }


# Hand-picked fixtures: 8 photos, 2 days, varying colors so the histogram
# embedder produces meaningfully different vectors. Names include mood
# keywords so the stub picks varied moods.
FIXTURES: list[tuple[str, dt.datetime, tuple[int, int, int], tuple[float, float] | None]] = [
    # Day 1 morning — coffee + books, near-identical times → one scene
    ("01_coffee", dt.datetime(2026, 4, 10, 8, 30), (180, 140, 90), (40.7, -74.0)),
    ("02_books",  dt.datetime(2026, 4, 10, 9, 15), (160, 120, 80), (40.7, -74.0)),
    # Day 1 evening — concert + city, ≤4h apart with each other only
    ("03_concert", dt.datetime(2026, 4, 10, 21, 0),  (40, 20, 200), (40.7, -74.0)),
    ("04_city",    dt.datetime(2026, 4, 10, 23, 30), (60, 30, 220), (40.7, -74.0)),
    # Day 2 — beach + sunset (warm), friends (rowdy), mountain (quiet)
    ("05_beach",   dt.datetime(2026, 4, 12, 14, 0), (240, 200, 120), (34.0, -118.2)),
    ("06_sunset",  dt.datetime(2026, 4, 12, 18, 30), (250, 130, 70),  (34.0, -118.2)),
    ("07_friends", dt.datetime(2026, 4, 12, 20, 0), (200, 80, 80),    (34.0, -118.2)),
    ("08_mountain", dt.datetime(2026, 4, 13, 9, 0),  (100, 130, 110), (39.5, -106.0)),
]


def _make_jpeg(path: Path, taken: dt.datetime, color: tuple[int, int, int]) -> None:
    img = Image.new("RGB", (64, 64), color=color)
    exif_dict = {
        "0th": {},
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: taken.strftime("%Y:%m:%d %H:%M:%S").encode()
        },
        "GPS": {},
        "1st": {},
        "thumbnail": None,
    }
    img.save(path, format="JPEG", exif=piexif.dump(exif_dict))


def _ingest_fixtures(env_) -> dict[str, str]:
    """Returns a name → asset_id map (e.g. "coffee" → "<uuid>")."""
    src_dir = env_["home"] / "src_imgs"
    src_dir.mkdir()
    name_to_id: dict[str, str] = {}
    asset_ids: list[str] = []
    for name, taken, color, _gps in FIXTURES:
        p = src_dir / f"{name}.jpg"
        _make_jpeg(p, taken, color)
        aid = env_["ingest"].ingest_photo(str(p))
        asset_ids.append(aid)
        short = name.split("_", 1)[1]
        name_to_id[short] = aid
    # Patch GPS in the DB rows manually (ingest.py doesn't accept GPS-less
    # JPEGs cleanly via piexif round-trip without extra rigging).
    store = env_["store"]
    import sqlite3
    with sqlite3.connect(env_["home"] / "darkroom.db") as c:
        for (name, _t, _c, gps), aid in zip(FIXTURES, asset_ids):
            if gps is not None:
                c.execute(
                    "UPDATE assets SET lat = ?, lon = ? WHERE id = ?",
                    (gps[0], gps[1], aid),
                )
    return name_to_id


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

SCENE_KEYS = {"id", "title", "caption", "hero_asset_id", "asset_ids", "mood"}
VALID_MOODS = {"golden", "rainy", "rowdy", "quiet", "electric"}


def test_full_pipeline_produces_valid_scenes(env):
    _ingest_fixtures(env)
    assets = env["store"].get_assets({"kind": "photo"})
    assert len(assets) == 8

    groups = env["cluster"].cluster_assets(assets, k=4)

    assert len(groups) >= 2, "expected multi-cluster output for 8 photos"
    assert sum(len(g) for g in groups) == 8
    flat = [aid for g in groups for aid in g]
    assert len(set(flat)) == 8, "asset IDs must not appear in multiple groups"

    by_id = {a["id"]: a for a in assets}
    scenes = []
    for i, group in enumerate(groups):
        scene = env["caption"].caption_scene(
            [by_id[aid] for aid in group], scene_id=f"scene_{i:02d}"
        )
        scenes.append(scene)

    for scene in scenes:
        assert isinstance(scene, dict)
        assert SCENE_KEYS.issubset(scene.keys())
        assert isinstance(scene["id"], str) and scene["id"]
        assert isinstance(scene["title"], str) and scene["title"]
        assert isinstance(scene["caption"], str) and scene["caption"]
        assert len(scene["caption"].split()) <= 14
        assert scene["mood"] in VALID_MOODS
        assert scene["hero_asset_id"] in scene["asset_ids"]


def test_clustering_keeps_close_in_time_assets_together(env):
    name_to_id = _ingest_fixtures(env)
    assets = env["store"].get_assets({"kind": "photo"})

    groups = env["cluster"].cluster_assets(assets, k=4)

    def cluster_of(name: str) -> int:
        target = name_to_id[name]
        for i, g in enumerate(groups):
            if target in g:
                return i
        raise AssertionError(name)

    # Coffee + books are 45 minutes apart, both warm-toned → same cluster.
    assert cluster_of("coffee") == cluster_of("books")
    # Mountain is two days later from everything → own cluster
    mountain_cluster = cluster_of("mountain")
    coffee_cluster = cluster_of("coffee")
    assert mountain_cluster != coffee_cluster


def test_caption_scene_returns_typed_dict_shape(env):
    _ingest_fixtures(env)
    assets = env["store"].get_assets({"kind": "photo"})
    scene = env["caption"].caption_scene(assets[:3], scene_id="solo")
    assert scene["id"] == "solo"
    assert scene["asset_ids"] == [a["id"] for a in assets[:3]]
    assert scene["hero_asset_id"] == assets[0]["id"]


def test_caption_scene_caches_to_disk(env):
    _ingest_fixtures(env)
    assets = env["store"].get_assets({"kind": "photo"})
    cap_mod = env["caption"]
    scene1 = cap_mod.caption_scene(assets[:2], scene_id="x")

    cache_dir = env["home"] / "cache" / "captions"
    files_after_first = list(cache_dir.glob("*.json"))
    assert len(files_after_first) == 1

    # Second call should hit the cache (same files, no new ones).
    scene2 = cap_mod.caption_scene(assets[:2], scene_id="x")
    files_after_second = list(cache_dir.glob("*.json"))
    assert files_after_second == files_after_first
    assert scene1["caption"] == scene2["caption"]
    assert scene1["mood"] == scene2["mood"]


def test_narrative_intro_closing_and_stats(env):
    _ingest_fixtures(env)
    assets = env["store"].get_assets({"kind": "photo"})
    groups = env["cluster"].cluster_assets(assets, k=4)
    by_id = {a["id"]: a for a in assets}
    scenes = [
        env["caption"].caption_scene(
            [by_id[aid] for aid in g], scene_id=f"s{i}"
        )
        for i, g in enumerate(groups)
    ]

    intro = env["narrative"].build_intro(scenes)
    closing = env["narrative"].build_closing(scenes)
    stats = env["narrative"].build_stats(assets)

    assert isinstance(intro, str) and intro
    assert isinstance(closing, str) and closing
    assert "\n" not in intro and "\n" not in closing

    assert stats["photos"] == 8
    # Three GPS clusters: NYC, LA, Colorado.
    assert stats["cities"] == 3
    # Three distinct calendar days in the fixture set.
    assert stats["days"] == 3
    assert "8 photos" in stats["summary"]
    assert "·" in stats["summary"]


def test_empty_inputs_dont_crash(env):
    cluster = env["cluster"]
    narrative = env["narrative"]
    assert cluster.cluster_assets([], k=4) == []
    assert narrative.build_intro([])
    assert narrative.build_closing([])
    assert narrative.build_stats([])["photos"] == 0
