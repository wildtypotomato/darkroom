"""Render the Wrapped recap (Remotion) to a 1080x1920 MP4 with score muxed in.

Writes scene data to a temporary props file and passes it via
``--props`` to ``npx remotion render``, then muxes the score with ffmpeg.
The source-tree ``sample.json`` is never modified.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any, Sequence

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "wrapped"
VIDEO_DIR = TEMPLATES_DIR / "video"
DATA_JSON = TEMPLATES_DIR / "sample.json"


def _ensure_node_modules():
    nm = VIDEO_DIR / "node_modules"
    if not nm.exists():
        subprocess.run(
            ["npm", "install"],
            cwd=str(VIDEO_DIR),
            check=True,
            capture_output=True,
            timeout=120,
        )


def render_video(
    scenes: Sequence[dict[str, Any]],
    score_path: str,
    out_path: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    _ensure_node_modules()
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    pub_dir = VIDEO_DIR / "public"
    if pub_dir.exists():
        for old in pub_dir.iterdir():
            if old.is_file():
                old.unlink(missing_ok=True)
    pub_dir.mkdir(exist_ok=True)
    rewritten: list[dict[str, Any]] = []
    for sc in scenes:
        sc = dict(sc)
        img = Path(sc.get("image", ""))
        if img.is_absolute() and img.exists():
            unique_name = f"{uuid.uuid4().hex[:8]}{img.suffix}"
            dest = pub_dir / unique_name
            shutil.copy2(str(img), str(dest))
            sc["image"] = unique_name
        rewritten.append(sc)

    existing = json.loads(DATA_JSON.read_text())
    payload = {**existing, "scenes": rewritten}
    if metadata:
        payload.update(metadata)

    props_file = out.parent / f"_props_{out.stem}.json"
    props_file.write_text(json.dumps({"data": payload}, indent=2))

    silent = out.with_name(out.stem + "_silent.mp4")
    try:
        subprocess.run(
            [
                "npx", "remotion", "render", "src/index.ts", "Recap",
                str(silent.resolve()),
                "--concurrency=1", "--overwrite", "--log=error",
                f"--props={props_file.resolve()}",
            ],
            cwd=str(VIDEO_DIR),
            check=True,
            capture_output=True,
            timeout=300,
        )
    finally:
        props_file.unlink(missing_ok=True)

    if score_path and Path(score_path).exists():
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(silent),
                "-i", score_path,
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                str(out),
            ],
            check=True,
            capture_output=True,
            timeout=300,
        )
        silent.unlink(missing_ok=True)
    else:
        shutil.move(str(silent), str(out))

    return str(out)
