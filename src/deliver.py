"""Delivery: send a finished artifact to Telegram + register a recap cron.

Outbound files use Hermes' ``MEDIA:`` tag protocol — the gateway extracts
the tags from the agent's final reply string and sends the referenced
files as native attachments. See docs/RESEARCH_NOTES.md §2.6.

Cron registration writes a small descriptor under ``$MEMORY_BOOK_HOME/
schedules/<id>.json``. If Hermes' ``schedule`` tool is importable at
runtime the descriptor is also registered with it; otherwise the file
alone is enough for the demo (the gateway picks descriptors up on start
and a sibling tool can resync them).
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from .store import home


# ---------------------------------------------------------------------------
# Telegram delivery
# ---------------------------------------------------------------------------

def send_to_telegram(manifest: dict[str, Any], chat_id: str) -> str:
    """Build the agent reply that ships the artifact to ``chat_id``.

    Returns the message string the runtime should emit. The Hermes Telegram
    adapter reads ``MEDIA:<path>`` tags and uploads each file as a native
    attachment. Returning the string keeps this function side-effect-free
    (and trivially testable); the runtime is responsible for the actual
    network call.
    """
    pdf = manifest["pdf_path"]
    mp4 = manifest["mp4_path"]
    template = manifest.get("template", "wrapped")
    n_scenes = len(manifest.get("scenes") or [])

    body = (
        f"Your {template} is ready — {n_scenes} scenes, PDF poster + 9:16 video below.\n"
        f"MEDIA:{pdf}\n"
        f"MEDIA:{mp4}"
    )

    log_path = _log_dir() / "deliveries.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as f:
        f.write(
            json.dumps({
                "ts": time.time(),
                "chat_id": chat_id,
                "artifact_id": manifest.get("id"),
                "template": template,
                "pdf_path": pdf,
                "mp4_path": mp4,
            })
            + "\n"
        )
    print(f"[deliver] queued artifact {manifest.get('id')} → chat {chat_id}")
    return body


# ---------------------------------------------------------------------------
# Cron registration
# ---------------------------------------------------------------------------

def register_recap_cron(cadence: str, chat_id: str, template: str) -> str:
    """Register a recurring recap with Hermes' scheduler.

    ``cadence`` is a 5-field cron expression (e.g. ``"0 21 * * 0"`` for
    Sunday 9pm). On each fire the gateway should run::

        manifest = compose(template, {"since": "7d"})
        send_to_telegram(manifest, chat_id)

    Returns the schedule id.
    """
    sid = uuid.uuid4().hex[:12]
    descriptor = {
        "id": sid,
        "cadence": cadence,
        "chat_id": chat_id,
        "template": template,
        "skill": "darkroom",
        "tool": "compose_and_deliver",
        "args": {"asset_filter": {"since": "7d"}},
    }

    sched_dir = home() / "schedules"
    sched_dir.mkdir(parents=True, exist_ok=True)
    (sched_dir / f"{sid}.json").write_text(json.dumps(descriptor, indent=2))

    _try_register_with_hermes(descriptor)
    print(f"[deliver] registered cron {sid} cadence={cadence!r} chat={chat_id}")
    return sid


def _try_register_with_hermes(descriptor: dict[str, Any]) -> None:
    """Best-effort hand-off to Hermes' built-in scheduler. The exact symbol
    name varies by Hermes version; we try the documented surface and stay
    silent on absence — the JSON descriptor is the source of truth."""
    try:
        from hermes.tools import schedule  # type: ignore[import-not-found]
        schedule(
            cadence=descriptor["cadence"],
            skill=descriptor["skill"],
            tool=descriptor["tool"],
            args=descriptor["args"],
            id=descriptor["id"],
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def _log_dir() -> Path:
    return home() / "logs"
