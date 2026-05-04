"""Tests for music score generation (Suno + ambient fallback)."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest import mock

import pytest

from darkroom.src import music


def _duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        check=True, capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def test_empty_key_uses_fallback(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("SUNO_API_KEY", "")
    out = tmp_path / "score.mp3"

    result = music.generate_score("warm", 5, str(out))

    assert result == str(out)
    assert out.exists() and out.stat().st_size > 0
    assert abs(_duration(str(out)) - 5) < 0.5


def test_suno_error_falls_back_to_ambient(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("SUNO_API_KEY", "fake-key")
    out = tmp_path / "score.mp3"

    with mock.patch.object(music, "_suno", side_effect=RuntimeError("boom")):
        result = music.generate_score("melancholy", 4, str(out))

    captured = capsys.readouterr()
    assert "[music] suno failed" in captured.out
    assert "ambient/" in captured.out
    assert result == str(out)
    assert out.exists()
    assert abs(_duration(str(out)) - 4) < 0.5


def test_unknown_mood_defaults_to_warm(tmp_path, monkeypatch):
    monkeypatch.setenv("SUNO_API_KEY", "")
    out = tmp_path / "score.mp3"
    result = music.generate_score("nonexistent_mood", 3, str(out))
    assert Path(result).exists()
    assert abs(_duration(result) - 3) < 0.5


def test_ambient_beds_present():
    base = Path(music.__file__).resolve().parent.parent / "assets" / "ambient"
    for mood in ("warm", "melancholy", "upbeat"):
        assert (base / f"{mood}.mp3").exists(), f"missing {mood}.mp3"
