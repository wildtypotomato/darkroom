"""Unit tests for the critique module (anti-slop quality gate)."""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture()
def critique_env(monkeypatch, tmp_path):
    """Set MEMORY_BOOK_HOME and MEMORY_BOOK_VISION_STUB, reload module."""
    monkeypatch.setenv("MEMORY_BOOK_HOME", str(tmp_path))
    monkeypatch.setenv("MEMORY_BOOK_VISION_STUB", "1")
    import memory_book.src.critique as critique
    importlib.reload(critique)
    return critique, tmp_path


# ---------------------------------------------------------------------------
# Stub-mode tests
# ---------------------------------------------------------------------------

def test_critique_pdf_stub_mode(critique_env):
    critique, home = critique_env
    result = critique.critique_pdf("/nonexistent/poster.pdf")
    assert result["verdict"] == "PASS"
    assert result["issues"] == []
    assert result["summary"] == "stub mode"


def test_critique_video_stub_mode(critique_env):
    critique, home = critique_env
    result = critique.critique_video("/nonexistent/recap.mp4")
    assert result["verdict"] == "PASS"
    assert result["issues"] == []
    assert result["summary"] == "stub mode"


def test_critique_artifact_stub_mode(critique_env):
    critique, home = critique_env
    result = critique.critique_artifact("/nonexistent/poster.pdf", "/nonexistent/recap.mp4")
    assert result["verdict"] == "PASS"
    assert result["issues"] == []
    assert result["summary"] == "stub mode"


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------

def test_parse_critique_response_valid(critique_env):
    critique, _ = critique_env
    raw = json.dumps({
        "verdict": "WARN",
        "issues": [
            {
                "pattern": "#5 The Gradient Wash",
                "severity": "cosmetic",
                "corrective": "Replace gradient with flat color",
            }
        ],
        "summary": "minor gradient issue detected",
    })
    result = critique._parse_critique_response(raw)
    assert result["verdict"] == "WARN"
    assert len(result["issues"]) == 1
    assert result["issues"][0]["pattern"] == "#5 The Gradient Wash"
    assert result["issues"][0]["severity"] == "cosmetic"
    assert result["summary"] == "minor gradient issue detected"


def test_parse_critique_response_malformed(critique_env):
    critique, _ = critique_env
    result = critique._parse_critique_response("this is not json at all!!!")
    assert result["verdict"] == "PASS"
    assert result["issues"] == []
    assert "could not parse" in result["summary"]


# ---------------------------------------------------------------------------
# Verdict computation
# ---------------------------------------------------------------------------

def test_compute_verdict_critical(critique_env):
    critique, _ = critique_env
    issues = [
        critique.CritiqueIssue(
            pattern="#1 The Spotify Wrapped Clone",
            severity="critical",
            corrective="redesign layout",
        ),
        critique.CritiqueIssue(
            pattern="#10 Minor thing",
            severity="cosmetic",
            corrective="tweak color",
        ),
    ]
    assert critique._compute_verdict(issues) == "FAIL"


def test_compute_verdict_cosmetic_only(critique_env):
    critique, _ = critique_env
    issues = [
        critique.CritiqueIssue(
            pattern="#12 Soft Shadow",
            severity="cosmetic",
            corrective="reduce shadow radius",
        ),
    ]
    assert critique._compute_verdict(issues) == "WARN"


def test_compute_verdict_no_issues(critique_env):
    critique, _ = critique_env
    assert critique._compute_verdict([]) == "PASS"


# ---------------------------------------------------------------------------
# Rubric loading
# ---------------------------------------------------------------------------

def test_rubric_loading(critique_env):
    critique, _ = critique_env
    rubric = critique._load_rubric()
    assert rubric is not None, "anti_slop.md should exist in references/"
    assert len(rubric) > 100, "rubric should be a substantial document"
    assert "slop" in rubric.lower() or "#" in rubric, "rubric should contain anti-slop patterns"
