---
name: darkroom
description: "Personal archivist: ingests photos, voice memos, screenshots → designed 9:16 MP4 + PDF poster via Hermes delegate_task fan-out, FTS5 recall, and NL cron."
version: 1.0.0
user-invocable: true
argument-hint: [wrap · teach · critique · reset · schedule]
---

# Darkroom Production Pipeline

## Requirements

- Python 3.11+
- ffmpeg
- Node.js 18+ (video rendering — `npm install` runs automatically on first use)
- Playwright (`playwright install chromium`)
- Three bundled ambient tracks (warm, melancholy, upbeat) are selected based on detected mood

## When to use

Use when users have accumulated personal media — photos, voice memos, screenshots, links — and want them shaped into a designed artifact. Triggers: end of a trip, end of a week, a pile of unsorted photos, "make something from these," a life milestone, or a recurring cron tick. The cadence is the user's choice — daily, weekly, monthly, per-trip, seasonal, or yearly. The output is a 9:16 MP4 and a companion PDF poster, delivered via Telegram.

> Over time, individual wraps accumulate — a future update will compile them into a single book.

## When NOT to use

- Single photo editing or filters. This is an archivist, not a photo editor.
- Real-time event coverage. Darkroom works retrospectively.
- Content moderation or NSFW detection. Not in scope.
- Fewer than 4 assets. Below that threshold, the clustering stage has nothing to work with — suggest a collage instead.
- When the user wants a slide deck, a blog post, or a social caption. Different tool, different format.

## Creative Standard

**A Darkroom wrap is an editorial artifact, not a tech product wrap-up.** The moment it looks like Spotify Wrapped — purple gradient, floating cards, playful sans — it has failed. The bar is a *Monocle* feature spread, not a year-in-review infographic.

Every frame teaches the eye where to look. Hierarchy is built with scale and weight; color is the last lever, never the first. Two typefaces maximum — one body, one display partner. The grid is the contract: every element snaps to it, no exceptions. White space is structural, not leftover. Reserve at least a third of the surface for breathing room, because **the emptiness is where authority lives.**

Captions are sentences, not labels. "A beautiful moment captured in time" is the absence of meaning — name the place, the weather, the specific detail the camera caught. If you cannot write a caption that stands alone without the image, the caption stage failed and CRITIQUE must reject.

**Pacing is the difference between a slideshow and a story.** Hero frames linger. Caption cards breathe. Pull-quote moments hold longer than their neighbours — the hold *is* the emphasis. Uniform 3-second cuts are the temporal equivalent of a cramped layout.

Constraint carries personality. No gradients. No lens flares. No bounce-swipe transitions. No five-color AI palettes. **The frame's strength is what it omits.** One ink, one accent, earned with a semantic reason. If a designer cannot tell this was AI-generated, we passed.

The full design floor: `references/design-philosophy.md` (10 rules). The failure gallery: `references/anti_slop.md` (34 named anti-patterns). Both are loaded into CRITIQUE automatically.

## Pipeline

```
RECALL → CLUSTER → ┬→ CAPTION ─┐
                    └→ SCORE   ─┼→ RENDER → CRITIQUE → DELIVER
                                │
                            COMPOSE
```

**RECALL** — Query the asset store by date range, tags, or semantic similarity. On Hermes, hits FTS5 cross-session memory. Off Hermes, falls back to SQLite FTS5 on local store.

**CLUSTER** — Group assets by EXIF date, location, and semantic similarity. Each cluster becomes a scene. Discard duplicates and low-signal assets.

**CAPTION / SCORE** — Two parallel sub-agents via `delegate_task`. Captions (one per scene, via Hermes 4 vision) and background music (selected from bundled ambient tracks by mood) generated concurrently.

**COMPOSE** — Merge caption scenes, score, and asset references into a render manifest. Resolves style, grid, typography, palette from taste file + flags.

**RENDER** — PDF poster (HTML + Jinja2 → Playwright) and 9:16 MP4 (Remotion + ffmpeg mux) sequentially.

**CRITIQUE** — Anti-slop evaluation via vision model. Details in `skills/critique/SKILL.md`.

**DELIVER** — Both artifacts to Telegram with an edition label.

Full stage specs, module mappings, and the Generator–Critic Loop: `skills/wrap/SKILL.md`.

## Command Format

All commands use `/darkroom <subcommand>` syntax with space-separated arguments:

```
/darkroom wrap --since 7d --style editorial-typographic
/darkroom teach
/darkroom critique /path/to/artifact.pdf
/darkroom reset
/darkroom schedule "every Sunday evening"
```

## Commands

| Command | Description | Skill file |
|---------|-------------|------------|
| `/darkroom teach` | One-time taste interview — captures aesthetic preferences to `DARKROOM_TASTE.md` | [`skills/teach/SKILL.md`](skills/teach/SKILL.md) |
| `/darkroom wrap` | Main pipeline — RECALL through DELIVER. Accepts `--style`, `--mode`, `--since` flags | [`skills/wrap/SKILL.md`](skills/wrap/SKILL.md) |
| `/darkroom critique` | Standalone anti-slop evaluation of a rendered PDF or MP4 | [`skills/critique/SKILL.md`](skills/critique/SKILL.md) |
| `/darkroom reset` | Clear `DARKROOM_TASTE.md` and revert to defaults | [`skills/reset/SKILL.md`](skills/reset/SKILL.md) |
| `/darkroom schedule` | Register a Hermes NL cron job for automatic wraps | [`skills/schedule/SKILL.md`](skills/schedule/SKILL.md) |

## Persistent Context: DARKROOM_TASTE.md

Written by `/darkroom teach`, loaded at the start of every `/darkroom wrap`. Schema:

| Field | Type | Example |
|-------|------|---------|
| `preferred_style` | slug | `editorial-typographic` |
| `caption_voice` | free text | "Short. Specific. Name the weather." |
| `banned_moves` | list | `["gradient text", "centered body", "Ken Burns on every photo"]` |
| `mood_vocabulary` | list | `["understated", "wry", "warm without sentimental"]` |
| `accent_color` | HSL or name | `brick-red` |
| `default_mode` | `memorial` or `archival` | `memorial` |

If absent, `/darkroom wrap` uses `dark-editorial`, neutral voice, no banned moves, and auto-detects mode.

## Style Presets

Five locked presets, each derived from a canonical design source. Full specs in `references/styles.md`.

| Slug | Source | One-liner |
|------|--------|-----------|
| `dark-editorial` | Built-in template | Fraunces + Inter, warm ink on near-black, hairline dividers — the default |
| `restrained-modernist` | Vignelli Canon | Pure geometry, primary colour as identifier — form stripped to semantic essence |
| `functional-minimalism` | Refactoring UI | Hierarchy through systematic constraint, HSL-precise colour, ruthless de-emphasis |
| `editorial-grid-authority` | Caldwell & Zappaterra | Dominant image, proportional grid, paced spreads — the magazine feature |
| `editorial-typographic` | Ellen Lupton | Baseline-aware grid, serif body, one disciplined display partner |

Select via `--style=<slug>` or persist in `DARKROOM_TASTE.md`. Each preset specifies typography, palette, grid, voice, and motion rules for both PDF and MP4.

## Hermes-Only Beats

Five capabilities that light up on Hermes and degrade gracefully elsewhere.

### 1. 17-Channel Native Gateway

Hermes receives photos, voice memos, screenshots, and links from Telegram (and 16 other platforms) natively. No upload flow, no web UI. The user drops media into chat; RECALL indexes it automatically. Off Hermes: user provides file paths manually.

**Visible in:** RECALL stage. Assets arrive pre-indexed with platform metadata.

### 2. `delegate_task` Fan-Out

CAPTION and SCORE run as parallel sub-agents via `delegate_task` with `max_spawn_depth=2`. Each sub-agent writes to the shared filesystem. The orchestrator log shows fan-out and join — visible in Telegram as progress lines.

**Visible in:** CAPTION/SCORE parallel stage. Log lines: `[compose] delegate_task batch: caption + music`, `[compose] batch1 done`.

**Off Hermes:** Falls back to sequential execution. Same output, longer wall time.

### 3. FTS5 Cross-Session Memory

Hermes built-in memory stores every ingested asset with full-text search (FTS5). RECALL queries span sessions — "that café in Lisbon last March" resolves across months of accumulated media without the user re-uploading anything.

**Visible in:** RECALL stage. Semantic queries return assets from prior sessions.

**Off Hermes:** SQLite FTS5 on local `~/.darkroom` store. Same query interface, but only assets explicitly ingested in prior runs.

### 4. NL Cron + Multi-Channel Delivery

`/darkroom schedule` registers a Hermes cron using natural language ("every Sunday evening", "first of the month", "after every trip"). The cron auto-runs `/darkroom wrap` and delivers to the same Telegram thread — or any of Hermes' 17 supported channels.

**Visible in:** `/darkroom schedule` command. The user gets wraps at whatever rhythm they choose without lifting a finger.

**Off Hermes:** Cron registration unavailable. User runs `/darkroom wrap` manually.

### 5. Self-Evolving Skills

After the first `/darkroom wrap`, if the agent detects a repeating caption pattern (e.g., the user always shoots food, always wants location + dish name), it authors a `darkroom-batch-caption` sub-skill to disk — a `.py` file in the Hermes skills directory that handles that pattern directly on future runs. The skill tree grows with use.

**Visible in:** Post-DELIVER stage. File tree shows a new `.py` skill appearing. This is the centerpiece demo beat — Hermes skills that write Hermes skills.

**Off Hermes:** Sub-skill authoring skipped. Taste preferences still persist in `DARKROOM_TASTE.md`.

## References

| File | Contents |
|------|----------|
| `references/design-philosophy.md` | 10 universal design rules — the floor under every artifact |
| `references/styles.md` | 5 style presets with full typography, palette, grid, voice, motion specs |
| `references/anti_slop.md` | 34 named anti-patterns — the Gallery of Shame and CRITIQUE rubric |
| `references/captions.md` | Caption writing guide — specificity, voice, and anti-patterns |
| `references/motion.md` | Motion and pacing rules for MP4 output — timing, easing, transitions |
