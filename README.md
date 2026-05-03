# Darkroom

A photo archival skill for [Hermes Agent](https://github.com/NousResearch/hermes-agent) that turns your accumulated photos into designed editorial artifacts -- a 9:16 MP4 recap video and a companion A3 PDF poster -- delivered straight to Telegram.

Drop photos into chat at whatever pace suits you -- daily, after a trip, over weeks. When you're ready, trigger `/darkroom wrap` and Darkroom clusters them by time and similarity, writes editorial captions, scores ambient music, renders both formats, and runs an anti-slop critique loop before delivery.

The design standard is a *Monocle* feature spread, not a year-in-review infographic. Every frame teaches the eye where to look. Hierarchy is built with scale and weight; colour is the last lever, never the first. If a designer cannot tell this was generated, we passed.

> Over time, individual wraps accumulate -- a future update will compile them into a single book.

## Install

```bash
# Clone into your Hermes skills directory
git clone https://github.com/wildtypotomato/darkroom ~/.hermes/skills/darkroom

# Install Python dependencies
cd ~/.hermes/skills/darkroom
pip install -e .

# Node dependencies install automatically on first video render.
# To pre-install manually:
cd templates/wrapped/video && npm install

# Install Playwright browser (for PDF rendering)
playwright install chromium
```

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `MEMORY_BOOK_API_KEY` | Vision captioning and critique (any OpenAI-compatible provider) | Yes (see below) |
| `MEMORY_BOOK_API_URL` | API endpoint URL | No (defaults to OpenRouter) |
| `HERMES_MODEL` | Model ID for vision calls | No (defaults to `nousresearch/hermes-4-405b`) |
| `SUNO_API_KEY` | Music generation | No (falls back to bundled ambient audio) |
| `MEMORY_BOOK_HOME` | Data directory | No (defaults to `~/.memory_book`) |

**API key resolution:** checks `MEMORY_BOOK_API_KEY` then `OPENROUTER_API_KEY` then `HERMES_API_KEY` in order. Set whichever matches your provider. On Hermes, the `delegate_task` path uses the agent's own configured model for orchestration -- the API key is only needed for the vision captioning fallback.

**Provider examples:**
```bash
# OpenRouter (default)
MEMORY_BOOK_API_KEY=sk-or-...

# Together AI
MEMORY_BOOK_API_URL=https://api.together.xyz/v1/chat/completions
MEMORY_BOOK_API_KEY=...
HERMES_MODEL=meta-llama/Llama-4-Scout-17B-16E-Instruct

# Any OpenAI-compatible endpoint
MEMORY_BOOK_API_URL=https://your-provider/v1/chat/completions
MEMORY_BOOK_API_KEY=...
HERMES_MODEL=your-model-id
```

**Stub modes** for testing without API calls:
- `MEMORY_BOOK_VISION_STUB=1` -- returns placeholder captions
- `MEMORY_BOOK_RENDER_STUB=1` -- skips Playwright/Remotion rendering

## Runtime Dependencies

- Python 3.11+
- Node.js 18+ (Remotion video rendering)
- ffmpeg (audio muxing and score generation)
- Playwright + Chromium (`playwright install chromium`)

> **Note:** First video render installs ~500 MB of Node dependencies automatically. Subsequent runs are instant.

## Commands

| Command | What it does |
|---------|-------------|
| `/darkroom teach` | One-time taste interview -- saves your aesthetic preferences |
| `/darkroom wrap` | Main pipeline -- clusters, captions, scores, renders, delivers |
| `/darkroom critique` | Standalone anti-slop evaluation of a rendered artifact |
| `/darkroom reset` | Clear saved preferences |
| `/darkroom schedule` | Register a Hermes cron -- you pick the rhythm |

### Flags

```
/darkroom wrap --since 1d           # assets from today
/darkroom wrap --since 7d           # last week
/darkroom wrap --since 30d          # last month
/darkroom wrap --style editorial-typographic
/darkroom wrap --mode memorial      # vs archival
```

## Architecture

```
RECALL --> CLUSTER --> +--> CAPTION --+
                      +--> SCORE   --+--> RENDER --> CRITIQUE --> DELIVER
                                     |
                                 COMPOSE
```

**RECALL** -- Query the asset store by date range, tags, or semantic similarity. On Hermes, hits FTS5 cross-session memory. Off Hermes, falls back to SQLite FTS5 on local store.

**CLUSTER** -- Group assets by EXIF date, location, and visual similarity (CLIP embeddings with colour-histogram fallback). Each cluster becomes a scene. Discard duplicates and low-signal assets.

**CAPTION / SCORE** -- Two parallel sub-agents via Hermes `delegate_task`. Captions (one per scene, via vision model) and a 30-second music bed (Suno with ambient fallback) generated concurrently. Off Hermes, falls back to sequential execution.

**COMPOSE** -- Merge caption scenes, score, and asset references into a render manifest. Resolves style, grid, typography, and palette from taste file and flags.

**RENDER** -- PDF poster (HTML + Jinja2 via Playwright) and 9:16 MP4 (Remotion + ffmpeg mux).

**CRITIQUE** -- Anti-slop evaluation via vision model against a 34-pattern rubric. Details in `references/anti_slop.md`. Up to 2 revision cycles before delivery.

**DELIVER** -- Both artifacts to Telegram with an edition label.

## Style Presets

Five locked presets, each derived from a canonical design source. Full specs in `references/styles.md`.

| Preset | Source | Vibe |
|--------|--------|------|
| `dark-editorial` | Built-in template | Fraunces + Inter, warm ink on near-black -- the default |
| `restrained-modernist` | Vignelli Canon | Pure geometry, primary colour as identifier |
| `functional-minimalism` | Refactoring UI | Hierarchy through systematic constraint, HSL-precise colour |
| `editorial-grid-authority` | Caldwell & Zappaterra | Dominant image, proportional grid, paced magazine spreads |
| `editorial-typographic` | Ellen Lupton | Baseline-aware grid, serif body, one disciplined display partner |

## Design Philosophy

Darkroom ships with an opinionated design system documented across four reference files:

- **`references/design-philosophy.md`** -- 10 universal rules drawn from Vignelli, Lupton, Refactoring UI, and Caldwell/Zappaterra. The floor under every artifact.
- **`references/anti_slop.md`** -- 34 named anti-patterns across visual, typographic, caption, and motion domains. The Gallery of Shame that CRITIQUE evaluates against.
- **`references/captions.md`** -- Caption writing guide with 5 voice modes, 8 worked examples, length budgets, and a 15-point critique checklist.
- **`references/motion.md`** -- Motion and pacing specification for video output. Timing vocabulary, camera movement rules, transition grammar, and the five-act pacing structure.

The creative standard in short: two typefaces maximum, one ink plus one accent, white space is structural, captions are sentences that stand alone without the image, and constraint carries personality.

## Hermes Integration

Five capabilities that light up on Hermes and degrade gracefully elsewhere:

1. **Native media gateway** -- Photos, voice memos, and screenshots arrive pre-indexed from Telegram (and 16 other platforms). Off Hermes, provide file paths manually.
2. **`delegate_task` fan-out** -- CAPTION and SCORE run as parallel sub-agents. Off Hermes, sequential execution.
3. **FTS5 cross-session memory** -- RECALL queries span sessions. Off Hermes, local SQLite FTS5 only.
4. **Natural language cron** -- `/darkroom schedule "every Sunday evening"` registers automatic wraps. Off Hermes, manual invocation only.
5. **Self-evolving skills** -- After repeated use, the agent authors specialised sub-skills to disk for detected patterns. Off Hermes, taste preferences persist but sub-skill authoring is skipped.

## Project Structure

```
darkroom/
  SKILL.md                  # Skill specification
  pyproject.toml            # Python dependencies
  skills/                   # Sub-skill definitions
    teach/SKILL.md
    wrap/SKILL.md
    critique/SKILL.md
    reset/SKILL.md
    schedule/SKILL.md
  references/               # Design guides and anti-patterns
  src/                      # 12 Python modules
    compose.py              # Orchestrator
    ingest.py               # Photo ingestion + EXIF
    cluster.py              # CLIP/histogram clustering
    caption.py              # Vision captioning
    narrative.py            # Intro/closing/stats generation
    music.py                # Suno + ambient fallback
    render_pdf.py           # HTML --> PDF via Playwright
    render_video.py         # Remotion --> MP4
    deliver.py              # Telegram delivery + cron
    taste.py                # Preference persistence
    critique.py             # Anti-slop evaluation
    store.py                # SQLite asset DB
  tests/                    # 35 tests
  templates/wrapped/        # Poster HTML + Remotion video project
  assets/ambient/           # Bundled fallback audio
```

## Testing

```bash
# Install test dependencies
pip install -e ".[test]"

# Run tests (stub mode, no API calls needed)
MEMORY_BOOK_VISION_STUB=1 MEMORY_BOOK_RENDER_STUB=1 pytest

# Run with rendering (requires Playwright + Node.js)
MEMORY_BOOK_VISION_STUB=1 pytest
```

## License

MIT
