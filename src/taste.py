"""Read and write DARKROOM_TASTE.md — persistent user aesthetic preferences.

The file lives at ``{DARKROOM_HOME}/DARKROOM_TASTE.md``.  Format is YAML
frontmatter (delimited by ``---``) inside a Markdown file.  Parsed without
PyYAML — the schema is flat enough for hand-rolled key/value + list parsing.

Loaded at the start of every ``/darkroom wrap``; written by ``/darkroom teach``.
"""
from __future__ import annotations

import re
from typing import TypedDict

from .store import home


class TasteProfile(TypedDict):
    preferred_style: str
    caption_voice: str
    banned_moves: list[str]
    mood_vocabulary: list[str]
    accent_color: str
    default_mode: str


# ---------------------------------------------------------------------------
# Defaults (from SKILL.md §Persistent-Context)
# ---------------------------------------------------------------------------

_DEFAULTS: TasteProfile = TasteProfile(
    preferred_style="dark-editorial",
    caption_voice="Warm and understated. Name the place, the weather, the specific detail.",
    banned_moves=[],
    mood_vocabulary=["warm", "understated"],
    accent_color="",
    default_mode="memorial",
)

_TASTE_FILENAME = "DARKROOM_TASTE.md"

# Keys whose values are lists (YAML ``- item`` lines).
_LIST_KEYS = {"banned_moves", "mood_vocabulary"}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_taste() -> TasteProfile:
    """Load ``DARKROOM_TASTE.md`` from the user's config dir.

    Returns sensible defaults when the file is absent or unparseable.
    """
    path = _taste_path()
    if not path.exists():
        return TasteProfile(**_DEFAULTS)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return TasteProfile(**_DEFAULTS)
    return _parse_frontmatter(raw)


def save_taste(profile: TasteProfile) -> Path:
    """Write ``DARKROOM_TASTE.md`` to the user's config dir.

    Returns the path written to.
    """
    path = _taste_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_frontmatter(profile), encoding="utf-8")
    return path


def clear_taste() -> None:
    """Delete ``DARKROOM_TASTE.md`` (for ``/darkroom reset`` command)."""
    path = _taste_path()
    if path.exists():
        path.unlink()


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def _taste_path() -> Path:
    return home() / _TASTE_FILENAME


# ---------------------------------------------------------------------------
# YAML frontmatter parser (no PyYAML)
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> TasteProfile:
    """Extract YAML frontmatter between ``---`` delimiters and parse it into a
    ``TasteProfile``.  Falls back to defaults for missing or malformed keys.
    """
    parts = text.split("---")
    if len(parts) < 3:
        return TasteProfile(**_DEFAULTS)

    body = parts[1]
    data: dict[str, str | list[str]] = {}
    current_key: str | None = None

    for line in body.splitlines():
        # List continuation: ``  - value``
        list_match = re.match(r"^\s+-\s+(.+)$", line)
        if list_match and current_key and current_key in _LIST_KEYS:
            existing = data.get(current_key)
            if not isinstance(existing, list):
                data[current_key] = []
            data[current_key].append(list_match.group(1).strip())  # type: ignore[union-attr]
            continue

        # Scalar: ``key: value`` or ``key: "value"``
        scalar_match = re.match(r"^([a-z_]+)\s*:\s*(.*)$", line)
        if scalar_match:
            key = scalar_match.group(1)
            val = scalar_match.group(2).strip()
            # Strip optional surrounding quotes.
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                val = val[1:-1]
            if key in _LIST_KEYS:
                # Key declared but value on same line is empty → start list.
                if val:
                    data[key] = [val]
                else:
                    data[key] = []
                current_key = key
            else:
                data[key] = val
                current_key = key
            continue

        # Anything else: ignore (blank lines, comments, prose).

    # Merge with defaults; pass through extra keys (user_name, wrap_label, etc.)
    result = dict(_DEFAULTS)
    for k in result:
        if k in data:
            result[k] = data[k]
    for k in data:
        if k not in result:
            result[k] = data[k]
    return result  # type: ignore[return-value]


def _render_frontmatter(profile: TasteProfile) -> str:
    """Serialise a ``TasteProfile`` to YAML-frontmatter Markdown."""
    lines = ["---"]
    for key in (
        "preferred_style",
        "caption_voice",
        "banned_moves",
        "mood_vocabulary",
        "accent_color",
        "default_mode",
    ):
        val = profile[key]  # type: ignore[literal-required]
        if isinstance(val, list):
            lines.append(f"{key}:")
            for item in val:
                lines.append(f"  - {item}")
        else:
            # Quote values that contain characters YAML would misparse.
            if any(c in str(val) for c in (":", '"', "'", "#", "{", "}", "[", "]")):
                lines.append(f'{key}: "{val}"')
            else:
                lines.append(f"{key}: {val}")
    lines.append("---")
    lines.append("")  # trailing newline
    return "\n".join(lines)
