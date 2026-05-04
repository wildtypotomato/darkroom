# Darkroom

A [Hermes Agent](https://github.com/NousResearch/hermes-agent) skill that turns your phone photos into something worth keeping -- a 9:16 recap video and a printed-feel A3 poster, delivered to Telegram.

Most "year in review" tools produce the same purple-gradient card layout. Darkroom goes the other way: the references directory contains 10 design rules, 34 named anti-patterns, and five locked style presets sourced from Vignelli, Lupton, and actual editorial design textbooks. The CRITIQUE stage evaluates every render against that rubric before anything gets delivered. The goal is output that looks like it came from a design studio, not a template.

You drop photos into chat over days or weeks. When you want a wrap, `/darkroom wrap` clusters them by time and visual similarity, writes captions, picks a music bed, renders both formats, critiques the result, and sends it back.

On Hermes, Darkroom gets:

- **Parallel captioning and scoring** via `delegate_task` -- roughly halves render time
- **Cross-session memory** -- `/darkroom wrap --since 30d` pulls photos from weeks-old conversations
- **17-channel ingestion** -- photos arrive pre-indexed from Telegram and other platforms, no file paths needed
- **NL cron** -- `/darkroom schedule "every Sunday evening"` and it just shows up
- **Self-evolving skills** -- after repeated use, the agent writes new sub-skills to disk for patterns it detects

| Skill | What it does |
|-------|-------------|
| `/darkroom wrap` | Main pipeline -- cluster, caption, score, render, critique, deliver |
| `/darkroom teach` | One-time taste interview -- saves aesthetic preferences for future wraps |
| `/darkroom critique` | Standalone anti-slop evaluation of a rendered artifact |
| `/darkroom schedule` | Register a Hermes cron -- pick your rhythm |
| `/darkroom reset` | Clear saved preferences |

> Individual wraps accumulate over time -- a future update will compile them into a single book.

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

### Update

```bash
cd ~/.hermes/skills/darkroom && git pull
```

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `DARKROOM_HOME` | Data directory | No (defaults to `~/.darkroom`) |

No API keys needed. Vision captioning and critique run through Hermes `delegate_task`. Background music is selected from three bundled tracks based on detected mood.

**Stub modes** for testing without API calls:
- `DARKROOM_VISION_STUB=1` -- returns placeholder captions
- `DARKROOM_RENDER_STUB=1` -- skips Playwright/Remotion rendering

## Runtime Dependencies

- Python 3.11+
- Node.js 18+ (Remotion video rendering)
- ffmpeg (audio muxing and score generation)
- Playwright + Chromium (`playwright install chromium`)

> **Note:** First video render installs ~500 MB of Node dependencies automatically. Subsequent runs are instant.

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

**CAPTION / SCORE** -- Two parallel sub-agents via Hermes `delegate_task`. Captions (one per scene, via vision model) and background music (selected from bundled tracks by mood) generated concurrently. Off Hermes, falls back to sequential execution.

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

## Design References

The `references/` directory is where most of the opinionated decisions live:

- **`design-philosophy.md`** -- 10 rules sourced from Vignelli Canon, Thinking with Type (Lupton), Refactoring UI, and Editorial Design (Caldwell & Zappaterra). These are the hard constraints -- two typefaces max, no gradients, captions must read without the image.
- **`anti_slop.md`** -- 34 named anti-patterns. Gradient text, AI colour palettes, Ken Burns on every frame, "a beautiful moment captured in time" captions. CRITIQUE checks renders against this list.
- **`captions.md`** -- Five caption voices (intimate, reflective, wry, documentary, contextual), worked before/after examples, and length budgets per format.
- **`motion.md`** -- Timing, camera movement, transitions, and pacing for the video output. Includes Remotion implementation patterns.

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
    music.py                # Ambient track selection
    render_pdf.py           # HTML --> PDF via Playwright
    render_video.py         # Remotion --> MP4
    deliver.py              # Telegram delivery + cron
    taste.py                # Preference persistence
    critique.py             # Anti-slop evaluation
    store.py                # SQLite asset DB
  tests/                    # 35 tests
  templates/wrapped/        # Poster HTML + Remotion video project
  assets/ambient/           # Bundled music tracks (warm, melancholy, upbeat)
```

## Testing

```bash
# Install test dependencies
pip install -e ".[test]"

# Run tests (stub mode, no API calls needed)
DARKROOM_VISION_STUB=1 DARKROOM_RENDER_STUB=1 pytest

# Run with rendering (requires Playwright + Node.js)
DARKROOM_VISION_STUB=1 pytest
```

## License

MIT
