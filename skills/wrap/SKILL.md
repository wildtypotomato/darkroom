---
name: darkroom-wrap
description: "Main pipeline: RECALL → CLUSTER → CAPTION/SCORE → COMPOSE → RENDER → CRITIQUE → DELIVER"
args:
  - name: style
    type: string
    description: "Style preset slug (default: dark-editorial)"
    required: false
  - name: mode
    type: string
    description: "memorial or archival (default: auto-detect)"
    required: false
    enum: [memorial, archival]
  - name: since
    type: string
    description: "Date window, e.g. 1d, 7d, 30d (default: 30d)"
    required: false
user-invocable: true
argument-hint: [--style · --mode · --since]
---

## MANDATORY PREPARATION

Load `DARKROOM_TASTE.md` from the user's Hermes config directory.

- **If present:** Print a one-line summary of loaded preferences (style, mode, accent). Continue.
- **If absent:** Inform the user: "No taste profile found — using defaults (dark-editorial, neutral voice, auto mode). Run `/darkroom teach` any time to personalise." Continue with defaults.

---

## Assess

Parse command flags and resolve defaults:

| Flag | Default (no taste file) | Default (taste file present) |
|------|------------------------|------------------------------|
| `--style` | `dark-editorial` | `preferred_style` from taste file |
| `--mode` | auto-detect from content mood | `default_mode` from taste file |
| `--since` | 30 days ago | 30 days ago |

Log resolved settings before proceeding.

## Pipeline Stages

### RECALL
Query the asset store by date range (`--since`), tags, or semantic similarity. On Hermes, this hits FTS5 cross-session memory — semantic queries resolve across months of accumulated media. Off Hermes, falls back to SQLite full-text search on local `~/.darkroom` store.

**Module:** `darkroom.src.recall`
**Output:** Ranked asset list with metadata (EXIF, captions, source platform).

### CLUSTER
Group assets by EXIF date, location, and semantic similarity. Each cluster becomes a chapter. Discard duplicates and low-signal assets. Minimum 4 assets required — if fewer survive clustering, abort with a message suggesting a collage instead.

**Module:** `darkroom.src.cluster`
**Output:** Ordered chapter list with ranked hero candidates per chapter.

### CAPTION / SCORE (parallel)

These two stages run concurrently via `delegate_task`. Each sub-agent writes to the shared filesystem. Progress lines appear in Telegram: `[compose] delegate_task batch: caption + music`.

Off Hermes: sequential execution. Same output, longer wall time.

Before captioning begins, ask the user one brief question: "Quick context — where were these taken and what was the occasion?" The reply is stored as `user_context` in the wrap manifest and forwarded to `_build_system_prompt()` in `caption.py`, so captions are grounded in real context instead of hallucinated.

#### CAPTION
Write captions per scene using Hermes 4 vision. Captions follow `DARKROOM_TASTE.md` voice rules and the `references/captions.md` guide.

**Module:** `darkroom.src.caption`
**Output:** Scene list with titles, captions, moods, and hero asset IDs.

#### SCORE
Pick background music from three bundled tracks (warm, melancholy, upbeat) based on the dominant mood detected from scenes. Loop/trim to 30 seconds with ffmpeg.

**Module:** `darkroom.src.music`
**Output:** Audio file path (MP3).

### COMPOSE
Merge caption scenes, scored audio, and asset references into a render manifest (JSON). Resolves style preset, layout grid, typography, and palette from the taste file + `--style` flag. Full preset specs live in `references/styles.md`.

**Module:** `darkroom.src.compose`
**Output:** Render manifest JSON.

### RENDER
Produce both artifacts in parallel:

- **PDF poster:** HTML + Jinja2 → Playwright `page.pdf()`. A3 portrait, the style preset's grid and typography.
- **9:16 MP4:** Remotion (React → MP4) + ffmpeg audio mux. 1080×1920, scored audio, paced cuts per the style preset's motion guidance (`references/motion.md`).

**Modules:** `darkroom.src.render_pdf`, `darkroom.src.render_video`
**Output:** PDF file path + MP4 file path.

### CRITIQUE
Automatically invoked after RENDER. Runs the Generator–Critic Loop (see below). If both artifacts pass, proceeds to DELIVER. If either fails, feeds correctives back into COMPOSE → RENDER and re-critiques.

**Module:** `darkroom.src.critique`

### DELIVER
Send both artifacts to the user's Telegram thread via Hermes gateway. Include a one-line edition label in tracked small caps: `AUTUMN 2025 — EDITION 04`.

**Module:** `darkroom.src.deliver`

---

## Generator–Critic Loop

After RENDER, the agent automatically invokes `/darkroom critique`. The loop:

1. **Screenshot** the PDF (full page) and sample 5 evenly-spaced MP4 frames.
2. **Score** each against `references/anti_slop.md` — 34 named anti-patterns across visual slop, typographic crimes, caption failures, motion slop, and pacing.
3. **Classify**: PASS (ship it), WARN (cosmetic issues logged but not blocking), FAIL (critical pattern detected).
4. On FAIL: feed the specific corrective ("What to do instead" from the anti-slop entry) back into COMPOSE → RENDER. Re-critique.
5. **Cap at 2 retries.** If still failing after 2 rounds, deliver with a WARN note to the user naming the unresolved issue.

Cost per critique pass: one vision call (~$0.02). Worth it every time.

---

## Two-Mode Framing

### `--mode=memorial`
Emotional. Year-in-review energy. Warmer palettes (accent skews warm). More pull quotes. Varied pacing — hero frames linger at 4–5s, intercut with 1.5s kickers. Intro and closing lines written with voice. Best presets: `editorial-grid-authority`, `editorial-typographic`.

### `--mode=archival`
Curated. Museum-catalogue restraint. Neutral palette. Dense grid, more images per spread. Captions as factual extensions — place, date, detail. Uniform pacing with deliberate holds on hero images only. Best presets: `restrained-modernist`, `functional-minimalism`.

Default: each style preset has a natural mode (see `references/styles.md`). The `--mode` flag overrides.
