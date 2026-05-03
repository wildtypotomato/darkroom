"""Mood-aware music score generation.

Primary: Suno API via configurable base URL (POST /generate, poll for audio).
Fallback: a bundled royalty-free ambient bed under assets/ambient/<mood>.mp3,
looped/trimmed to the requested duration with ffmpeg.

Any error in the Suno path -> automatic fallback with a [music] log line.
Empty SUNO_API_KEY -> straight to fallback, no error.

Set MEMORY_BOOK_SUNO_BASE_URL to override the default Suno API endpoint.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import requests

SUNO_BASE = os.environ.get(
    "MEMORY_BOOK_SUNO_BASE_URL",
    "https://api.sunoapi.org/api/v1",
)
AMBIENT = Path(__file__).resolve().parent.parent / "assets" / "ambient"
DEFAULT_MOOD = "warm"
KNOWN_MOODS = ("warm", "melancholy", "upbeat")
POLL_INTERVAL_SEC = 3
POLL_MAX_SEC = 120


def generate_score(mood: str, duration_sec: int, out_path: str) -> str:
    """Generate a music file for `mood` of `duration_sec` seconds at `out_path`.

    Returns the output path. Always succeeds via fallback unless ffmpeg fails
    or the bundled ambient beds are missing.
    """
    key = os.getenv("SUNO_API_KEY", "").strip()
    if not key:
        return _use_fallback(mood, duration_sec, out_path)

    try:
        return _suno(key, mood, duration_sec, out_path)
    except Exception as e:
        return _use_fallback(mood, duration_sec, out_path, reason=str(e))


def _suno(key: str, mood: str, duration_sec: int, out_path: str) -> str:
    prompt = f"Instrumental {mood} cinematic ambient piece, no vocals, ~{duration_sec}s"
    payload = {
        "prompt": prompt,
        "tags": f"{mood}, ambient, instrumental, cinematic",
        "instrumental": True,
        "customMode": True,
        "model": "V4",
        "wait_audio": False,
        "callBackUrl": "https://localhost/noop",
    }

    r = requests.post(
        f"{SUNO_BASE}/generate",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    r.raise_for_status()
    body = r.json()

    task_id = _extract_task_id(body)
    if not task_id:
        raise RuntimeError(f"suno: no taskId in response: {body}")

    audio_url = _poll_for_audio(key, task_id)
    if not audio_url:
        raise TimeoutError(f"suno: no audio after {POLL_MAX_SEC}s for task {task_id}")

    raw = Path(out_path).with_suffix(".raw.mp3")
    try:
        raw.write_bytes(requests.get(audio_url, timeout=60).content)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(raw),
                "-t",
                str(duration_sec),
                "-acodec",
                "libmp3lame",
                out_path,
            ],
            check=True,
            capture_output=True,
        )
    finally:
        raw.unlink(missing_ok=True)
    return out_path


def _extract_task_id(body: dict) -> str | None:
    """Defensively extract a task/ID from the Suno response, covering
    known variations in sunoapi.org response shapes."""
    # Standard path: {"data": {"taskId": "..."}}
    data = body.get("data") or {}
    if isinstance(data, dict):
        task_id = data.get("taskId") or data.get("task_id") or data.get("id")
        if task_id:
            return str(task_id)
    # Top-level taskId
    task_id = body.get("taskId") or body.get("task_id") or body.get("id")
    return str(task_id) if task_id else None


def _poll_for_audio(key: str, task_id: str) -> str | None:
    deadline = time.monotonic() + POLL_MAX_SEC
    while time.monotonic() < deadline:
        time.sleep(POLL_INTERVAL_SEC)
        try:
            d = requests.get(
                f"{SUNO_BASE}/generate/record-info",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                params={"taskId": task_id},
                timeout=15,
            ).json()
            clips = _extract_clips(d)
            for clip in clips:
                url = clip.get("audioUrl") or clip.get("audio_url") or clip.get("url")
                if url:
                    return url
        except (requests.exceptions.RequestException, ValueError, KeyError):
            continue
    return None


def _extract_clips(body: dict) -> list[dict]:
    """Defensively extract clip data from known Suno response shapes."""
    data = body.get("data") or {}
    if isinstance(data, dict):
        # sunoapi.org shape: data.response.sunoData
        response = data.get("response") or {}
        if isinstance(response, dict):
            clips = response.get("sunoData") or response.get("clips") or []
            if isinstance(clips, list):
                return clips
        # Flat: data.clips or data.results
        clips = data.get("clips") or data.get("results") or data.get("items") or []
        if isinstance(clips, list):
            return clips
    # Top-level clips list
    clips = body.get("clips") or body.get("results") or []
    return clips if isinstance(clips, list) else []


def _use_fallback(mood: str, duration_sec: int, out_path: str, reason: str | None = None) -> str:
    bed_mood = mood if mood in KNOWN_MOODS else DEFAULT_MOOD
    bed = AMBIENT / f"{bed_mood}.mp3"
    if not bed.exists():
        bed = AMBIENT / f"{DEFAULT_MOOD}.mp3"
    if not bed.exists():
        msg = (
            "No music source available: Suno API failed and no ambient audio "
            f"files found in {AMBIENT}. Place {DEFAULT_MOOD}.mp3 (or "
            "warm.mp3 / melancholy.mp3 / upbeat.mp3) in that directory."
        )
        print(f"[music] ERROR: {msg}")
        raise RuntimeError(msg) from None

    if reason is not None:
        print(f"[music] suno failed ({reason}), using ambient/{bed.name}")
    else:
        print(f"[music] using ambient/{bed.name}")

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-stream_loop",
                "-1",
                "-i",
                str(bed),
                "-t",
                str(duration_sec),
                "-acodec",
                "libmp3lame",
                out_path,
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg is required for music generation but was not found on PATH"
        ) from None
    except subprocess.TimeoutExpired:
        raise RuntimeError("ffmpeg timed out while generating ambient score") from None
    return out_path
