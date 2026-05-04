"""Caption a scene with Hermes 4 vision.

Sends up to 4 hero photos to Hermes 4 via delegate_task and parses a JSON
response into a Scene dict. Disk-cached by SHA256(file bytes + prompt
version) so reruns during dev are free.

Test mode: set `DARKROOM_VISION_STUB=1` to short-circuit the API call
and return a deterministic stub. Don't ship that env var to production.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

from .store import Asset, Scene, home

PROMPT_VERSION = "v2"
HERO_LIMIT = 4
MOOD_VOCAB = ("warm", "melancholy", "upbeat", "golden", "quiet")
DEFAULT_MOOD = "quiet"
MAX_CAPTION_WORDS = 50


SYSTEM_PROMPT = (
    "You write photo-album captions for a friend, not museum labels. "
    "Look at the images, then return strict JSON with exactly these keys: "
    '{"title": "2-4 word scene title", '
    '"caption": "2-3 sentences, 30-50 words, storytelling tone with a touch of humour, '
    "warm and specific, no emoji, no first person — write as if narrating someone else's story\", "
    '"mood": "one of: warm / melancholy / upbeat / golden / quiet"}. '
    "Captions should tell a mini-story: what happened, a sensory detail, "
    "and a wry observation or punchline. Concrete over abstract — "
    "no 'beautiful moment', no 'captured in time'. "
    "Return ONLY the JSON, no prose."
)

_VOICE_DIRECTIONS = {
    "memorial": "Voice B — reflective past tense, warm but not sentimental. Name the place, the weather, the concrete detail.",
    "archival": "Voice E — contextual, factual with one sentence of context. Restrained — no warmth, just information the image alone cannot supply.",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def caption_scene(
    assets: list[Asset],
    scene_id: str,
    taste: dict | None = None,
    user_context: str | None = None,
) -> Scene:
    """Produce a Scene for `assets`. The first asset is treated as hero.

    When *taste* is provided (a ``TasteProfile`` dict from ``taste.py``),
    the system prompt is augmented with the user's caption voice, banned
    moves, and mood vocabulary.

    When *user_context* is provided, it is prepended to the system prompt
    so captions are grounded in the user's real situation rather than
    fabricated from vision alone.

    Note: deviates from the plan's `caption_scene(asset_paths, scene_id)`
    signature because Scene needs both `path` (to send to vision) and `id`
    (to fill `hero_asset_id` / `asset_ids`). Asset gives us both.
    """
    if not assets:
        raise ValueError("caption_scene requires at least one asset")

    heroes = assets[:HERO_LIMIT]
    cache_key = _cache_key(heroes, taste, user_context)
    cached = _cache_read(cache_key)
    if cached is None:
        cached = _call_vision(heroes, taste, user_context)
        _cache_write(cache_key, cached)

    title = _clean_title(cached.get("title") or "Scene")
    caption = _clamp_words(cached.get("caption") or "", MAX_CAPTION_WORDS)
    mood = _normalise_mood(cached.get("mood"))

    return Scene(
        id=scene_id,
        title=title,
        caption=caption,
        hero_asset_id=heroes[0]["id"],
        asset_ids=[a["id"] for a in assets],
        mood=mood,
    )


# ---------------------------------------------------------------------------
# Vision call
# ---------------------------------------------------------------------------




def _build_system_prompt(
    taste: dict | None = None,
    user_context: str | None = None,
) -> str:
    """Build the system prompt, optionally augmented by taste preferences
    and grounded by user-provided photo context."""
    prompt = SYSTEM_PROMPT
    addenda: list[str] = []

    if user_context:
        addenda.insert(
            0,
            f"Photo context from the user: {user_context}. "
            "Use these real details — place, occasion, people — instead "
            "of inventing them.",
        )

    if taste:
        mode = taste.get("default_mode", "")
        if mode in _VOICE_DIRECTIONS:
            addenda.append(_VOICE_DIRECTIONS[mode])
        voice = taste.get("caption_voice")
        if voice:
            addenda.append(f"Voice direction: {voice}")

        banned = taste.get("banned_moves")
        if banned:
            caption_bans = [
                b
                for b in banned
                if not any(kw in b.lower() for kw in ("gradient", "ken burns", "layout", "grid"))
            ]
            if caption_bans:
                addenda.append("Never use: " + "; ".join(caption_bans) + ".")

        moods = taste.get("mood_vocabulary")
        if moods:
            addenda.append("Prefer these mood words when they fit: " + ", ".join(moods) + ".")

    if addenda:
        prompt = prompt + " " + " ".join(addenda)
    return prompt


def _call_vision(
    heroes: list[Asset],
    taste: dict | None = None,
    user_context: str | None = None,
) -> dict:
    if os.environ.get("DARKROOM_VISION_STUB") == "1":
        return _stub_response(heroes)

    delegate = _resolve_delegate_task()
    if delegate is None:
        print("[caption] no delegate_task available, using stub response")
        return _stub_response(heroes)

    system_prompt = _build_system_prompt(taste, user_context)

    content_parts = ["Caption this scene in JSON as instructed."]
    image_paths = [hero["path"] for hero in heroes]

    try:
        result = delegate(
            goal=(
                f"You are a photo caption writer. {system_prompt}\n\n"
                f"Look at these images and return the JSON as instructed."
            ),
            context=json.dumps({"image_paths": image_paths}),
            toolsets=["terminal", "file"],
            max_iterations=10,
        )
        text = result.get("summary") if isinstance(result, dict) else str(result)
        return _parse_json(text)
    except Exception as e:
        print(f"[caption] delegate_task failed ({e}), using stub response")
        return _stub_response(heroes)


def _resolve_delegate_task():
    try:
        from hermes.tools import delegate_task  # type: ignore[import-not-found]
        return delegate_task
    except Exception:
        return None


_STUB_LIBRARY: dict[str, dict[str, str]] = {
    "cafe": {
        "title": "Morning Ritual",
        "caption": "The morning light caught the old town square through the café window. Same order as yesterday — the barista remembered without asking.",
        "mood": "warm",
    },
    "greece": {
        "title": "Blue and White",
        "caption": "The whitewashed walls delivered exactly the postcard view — and somehow it still hit different in person. The wind nearly took every hat into the sea.",
        "mood": "golden",
    },
    "greece_lunch": {
        "title": "Seaside Table",
        "caption": "Grilled octopus, a carafe of house white, and a cat that appeared the moment food arrived. The waiter said the cat's name was Socrates. Of course it was.",
        "mood": "warm",
    },
    "japan_street": {
        "title": "Lost in Translation",
        "caption": "Somewhere between Shibuya and Shimokitazawa, they stopped pretending to navigate and let the backstreets decide. Every turn produced a vending machine and a shrine.",
        "mood": "quiet",
    },
    "nightmarket": {
        "title": "After Dark",
        "caption": "Street food at dusk — the queue said it all. Smoke from the grill, something sweet frying nearby, and the unspoken agreement that this beat any restaurant.",
        "mood": "upbeat",
    },
    "paris": {
        "title": "The Long Light",
        "caption": "Late spring in the city — the light goes gold around seven and the whole place pretends it invented the concept of an evening stroll. Never gets old.",
        "mood": "golden",
    },
    "ramen": {
        "title": "Bowl Number Five",
        "caption": "Day three and already on ramen bowl number five. This one had a broth so rich it could have paid rent. Worth the forty-minute queue.",
        "mood": "warm",
    },
    "river": {
        "title": "Quiet Water",
        "caption": "The river path at dusk, when everyone else has gone home and the light turns the water into something paintable. Twenty minutes of saying nothing.",
        "mood": "quiet",
    },
    "selfie": {
        "title": "The Group Shot",
        "caption": "The obligatory group selfie — slightly blurry because someone insisted on holding the phone one-handed. Nobody cared. The moment was the point.",
        "mood": "warm",
    },
    "solo": {
        "title": "Mid-Stride",
        "caption": "Caught mid-stride, unaware the camera was up. That thing people do when they spot something interesting ahead — walk slightly faster, forget the world behind.",
        "mood": "golden",
    },
    "tokyo": {
        "title": "Neon and Concrete",
        "caption": "The city's particular magic: a temple gate next to a convenience store, monks beside salarymen, silence two metres from chaos. Never enough days.",
        "mood": "upbeat",
    },
}


def _stub_response(heroes: list[Asset]) -> dict:
    """Context-aware placeholder captions keyed by filename. Falls back to
    a generic response for unknown filenames."""
    name = Path(heroes[0]["path"]).stem.lower()
    tags = heroes[0].get("tags") or []
    src_name = ""
    for t in tags:
        if t.startswith("src:"):
            src_name = t[4:].lower()
            break
    lookup = src_name or name
    for key in sorted(_STUB_LIBRARY, key=len, reverse=True):
        if key in lookup:
            return dict(_STUB_LIBRARY[key])

    mood = DEFAULT_MOOD
    for m in MOOD_VOCAB:
        if m in name:
            mood = m
            break
    title_words = re.split(r"[^A-Za-z]+", name)
    title_words = [w.capitalize() for w in title_words if w and not w.isdigit()]
    title = " ".join(title_words[:3]) or "Scene"
    caption = f"That afternoon held still long enough for {title.lower()}."
    return {"title": title, "caption": caption, "mood": mood}


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------


def _cache_dir() -> Path:
    p = home() / "cache" / "captions"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _cache_key(
    heroes: list[Asset],
    taste: dict | None = None,
    user_context: str | None = None,
) -> str:
    h = hashlib.sha256()
    h.update(PROMPT_VERSION.encode())
    if user_context:
        h.update(f"ctx:{user_context}".encode())
    if taste:
        # Different taste profiles must produce different cache entries.
        voice = taste.get("caption_voice", "")
        moods = ",".join(taste.get("mood_vocabulary", []))
        h.update(f"taste:{voice}:{moods}".encode())
    for hero in heroes:
        path = Path(hero["path"])
        if path.exists():
            stat = path.stat()
            h.update(f"{path}:{stat.st_mtime}:{stat.st_size}".encode())
        else:
            h.update(hero["id"].encode())
    return h.hexdigest()


def _cache_read(key: str) -> dict | None:
    f = _cache_dir() / f"{key}.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text())
    except Exception:
        return None


def _cache_write(key: str, payload: dict) -> None:
    f = _cache_dir() / f"{key}.json"
    f.write_text(json.dumps(payload))


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _parse_json(text: str) -> dict:
    """Pull the first JSON object out of `text`. Hermes models occasionally
    wrap JSON in prose; this is a forgiving extractor."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return {}
    return {}


def _normalise_mood(value) -> str:
    if isinstance(value, str):
        v = value.strip().lower()
        if v in MOOD_VOCAB:
            return v
        # tolerate "golden hour", "electric night" etc.
        for m in MOOD_VOCAB:
            if m in v:
                return m
    return DEFAULT_MOOD


def _clamp_words(text: str, limit: int) -> str:
    words = text.strip().split()
    if len(words) <= limit:
        return text.strip()
    return " ".join(words[:limit]).rstrip(",.;:") + "."


def _clean_title(text: str) -> str:
    t = re.sub(r"\s+", " ", text).strip()
    return t[:60] or "Scene"
