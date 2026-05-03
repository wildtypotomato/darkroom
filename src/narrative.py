"""Intro line, closing line, and stats summary for an artifact.

Template-based on purpose: deterministic output is easier to QA the day
before submission, and the captions (which carry the writing weight) come
from Hermes 4 in caption.py. If you want a riskier, model-written intro,
swap the bodies for a delegate_task call — the signatures stay the same.
"""
from __future__ import annotations

import math
from collections import Counter
from datetime import datetime

from .store import Asset, Scene

INTRO_TEMPLATES = (
    "Here's how it went: {n} scenes, one stretch of life.",
    "{n} scenes from the last little while.",
    "A short look back — {n} scenes worth keeping.",
)

CLOSING_TEMPLATES = (
    "That's the cut. Onto the next one.",
    "Nothing precious about it — just what stuck.",
    "A small archive, set aside.",
)


def build_intro(scenes: list[Scene]) -> str:
    n = len(scenes)
    if n == 0:
        return "Nothing in the archive yet."
    moods = [m for s in scenes if (m := s.get("mood"))]
    dominant = Counter(moods).most_common(1)
    template = INTRO_TEMPLATES[n % len(INTRO_TEMPLATES)]
    line = template.format(n=n)
    if dominant and dominant[0][1] >= max(2, n // 2):
        line += f" Mostly {dominant[0][0]}."
    return line


def build_closing(scenes: list[Scene]) -> str:
    if not scenes:
        return "Nothing to close out yet."
    return CLOSING_TEMPLATES[len(scenes) % len(CLOSING_TEMPLATES)]


def build_stats(assets: list[Asset]) -> dict:
    """Return a summary dict including a one-liner like
    '42 photos · 3 cities · 7 days'."""
    photos = sum(1 for a in assets if a.get("kind") == "photo")
    cities = _count_cities(assets)
    days = _count_days(assets)

    parts: list[str] = [f"{photos} photos"]
    if cities:
        parts.append(f"{cities} {'cities' if cities != 1 else 'city'}")
    if days:
        parts.append(f"{days} {'days' if days != 1 else 'day'}")
    summary = " · ".join(parts)

    return {
        "photos": photos,
        "cities": cities,
        "days": days,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _count_cities(assets: list[Asset]) -> int:
    """Coarse 'city' count: bucket GPS to ~50km cells. ~0.5° lat/lon at the
    equator. Good enough for the stats line; not a geocoder."""
    cells: set[tuple[int, int]] = set()
    for a in assets:
        lat, lon = a.get("lat"), a.get("lon")
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            cells.add((int(math.floor(lat * 2)), int(math.floor(lon * 2))))
    return len(cells)


def _count_days(assets: list[Asset]) -> int:
    days: set[str] = set()
    for a in assets:
        t = a.get("taken_at")
        if isinstance(t, datetime):
            days.add(t.date().isoformat())
    return len(days)
