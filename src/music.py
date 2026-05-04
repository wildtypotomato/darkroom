"""Mood-aware background music selection.

Picks from three bundled royalty-free ambient tracks (warm, melancholy, upbeat)
based on the dominant mood detected from the scenes. Loops/trims to the
requested duration with ffmpeg.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

AMBIENT = Path(__file__).resolve().parent.parent / "assets" / "ambient"
DEFAULT_MOOD = "warm"
KNOWN_MOODS = ("warm", "melancholy", "upbeat")


def generate_score(mood: str, duration_sec: int, out_path: str) -> str:
    """Pick the best-matching ambient track for `mood`, trim to `duration_sec`.

    Returns the output path.
    """
    bed_mood = mood if mood in KNOWN_MOODS else DEFAULT_MOOD
    bed = AMBIENT / f"{bed_mood}.mp3"
    if not bed.exists():
        bed = AMBIENT / f"{DEFAULT_MOOD}.mp3"
    if not bed.exists():
        msg = (
            f"No ambient audio files found in {AMBIENT}. "
            f"Place warm.mp3, melancholy.mp3, or upbeat.mp3 in that directory."
        )
        print(f"[music] ERROR: {msg}")
        raise RuntimeError(msg) from None

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


