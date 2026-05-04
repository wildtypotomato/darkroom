"""Unit tests for the taste profile system (load / save / clear / parse)."""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest


@pytest.fixture()
def taste_env(monkeypatch, tmp_path):
    """Point DARKROOM_HOME at a temp directory and reload the taste module."""
    monkeypatch.setenv("DARKROOM_HOME", str(tmp_path))
    import darkroom.src.taste as taste
    importlib.reload(taste)
    return taste, tmp_path


def test_load_taste_defaults(taste_env):
    taste, home = taste_env
    profile = taste.load_taste()
    assert profile["preferred_style"] == "dark-editorial"
    assert profile["caption_voice"].startswith("Warm and understated")
    assert profile["banned_moves"] == []
    assert profile["mood_vocabulary"] == ["warm", "understated"]
    assert profile["accent_color"] == ""
    assert profile["default_mode"] == "memorial"


def test_save_and_load_roundtrip(taste_env):
    taste, home = taste_env
    custom = taste.TasteProfile(
        preferred_style="brutalist-mono",
        caption_voice="Terse, factual, no adjectives.",
        banned_moves=["gradient-wash", "emoji-captions"],
        mood_vocabulary=["stark", "cold"],
        accent_color="#FF0000",
        default_mode="celebration",
    )
    taste.save_taste(custom)
    loaded = taste.load_taste()
    assert loaded == custom


def test_clear_taste(taste_env):
    taste, home = taste_env
    custom = taste.TasteProfile(
        preferred_style="hand-drawn",
        caption_voice="Playful.",
        banned_moves=[],
        mood_vocabulary=["fun"],
        accent_color="",
        default_mode="memorial",
    )
    taste.save_taste(custom)
    assert (home / "DARKROOM_TASTE.md").exists()

    taste.clear_taste()
    assert not (home / "DARKROOM_TASTE.md").exists()

    defaults = taste.load_taste()
    assert defaults["preferred_style"] == "dark-editorial"


def test_parse_frontmatter_with_lists(taste_env):
    taste, home = taste_env
    md = (
        "---\n"
        "preferred_style: bold\n"
        "caption_voice: Short.\n"
        "banned_moves:\n"
        "  - gradient-wash\n"
        "  - drop-shadow\n"
        "mood_vocabulary:\n"
        "  - bright\n"
        "  - sharp\n"
        "accent_color:\n"
        "default_mode: memorial\n"
        "---\n"
    )
    path = home / "DARKROOM_TASTE.md"
    path.write_text(md, encoding="utf-8")

    profile = taste.load_taste()
    assert profile["banned_moves"] == ["gradient-wash", "drop-shadow"]
    assert profile["mood_vocabulary"] == ["bright", "sharp"]


def test_parse_frontmatter_quoted_values(taste_env):
    taste, home = taste_env
    md = (
        '---\n'
        'preferred_style: editorial-grid-authority\n'
        'caption_voice: "Warm: name the place, the weather."\n'
        'banned_moves:\n'
        'mood_vocabulary:\n'
        '  - warm\n'
        'accent_color:\n'
        'default_mode: memorial\n'
        '---\n'
    )
    path = home / "DARKROOM_TASTE.md"
    path.write_text(md, encoding="utf-8")

    profile = taste.load_taste()
    assert profile["caption_voice"] == "Warm: name the place, the weather."


def test_missing_keys_filled_with_defaults(taste_env):
    taste, home = taste_env
    md = (
        "---\n"
        "preferred_style: minimal\n"
        "---\n"
    )
    path = home / "DARKROOM_TASTE.md"
    path.write_text(md, encoding="utf-8")

    profile = taste.load_taste()
    assert profile["preferred_style"] == "minimal"
    # All other keys should have defaults.
    assert profile["caption_voice"].startswith("Warm and understated")
    assert profile["banned_moves"] == []
    assert profile["mood_vocabulary"] == ["warm", "understated"]
    assert profile["accent_color"] == ""
    assert profile["default_mode"] == "memorial"
