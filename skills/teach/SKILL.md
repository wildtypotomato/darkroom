---
name: darkroom-teach
description: One-time taste interview that captures aesthetic preferences into MEMORY_BOOK_TASTE.md
user-invocable: true
---

## MANDATORY PREPARATION

Check whether `MEMORY_BOOK_TASTE.md` already exists in the user's Hermes config directory.

- **If it exists:** Show the user their current preferences in a compact summary. Ask: "Override these, or keep them?" If keep, exit early.
- **If absent:** Proceed directly to the interview.

---

## Assess

The interview captures six dimensions that shape every `/darkroom wrap` output — style, voice, prohibitions, mood, colour, and framing mode. Each question maps to a field in the taste file. The goal is a profile specific enough that two different users would produce visually distinct wraps from the same assets.

## Plan

Ask these questions in order. Each maps to a `MEMORY_BOOK_TASTE.md` field. Adapt phrasing to the conversation, but cover every field.

### Q1 → `preferred_style`
"What's the closest magazine or publication to the feel you want? Think about the layouts, not the content. *Monocle*, *Kinfolk*, *Bloomberg Businessweek*, a museum catalogue — anything."

If the user doesn't read magazines, offer the four presets by description:
- Pure geometry, primary colour as identifier (restrained-modernist)
- Hierarchy through systematic constraint, HSL-precise colour (functional-minimalism)
- Dominant image, proportional grid, paced spreads (editorial-grid-authority)
- Baseline-aware grid, serif body, one disciplined display partner (editorial-typographic)

### Q2 → `caption_voice`
"Describe the tone of voice you'd use to caption your own photos — not for Instagram, for yourself. Short and dry? Warm and specific? Poetic? Give me a sentence that sounds like you."

### Q3 → `banned_moves`
"What design moves do you hate? Gradients on text? Centred everything? Ken Burns on every photo? Name the things that make you wince."

### Q4 → `mood_vocabulary`
"Pick three words that describe the mood of your best moments. Not 'happy' — more like 'understated', 'wry', 'warm without being sentimental', 'chaotic but alive'."

### Q5 → `accent_color`
"Is there a colour that feels like yours? A colour you'd recognise as your own if you saw it in a layout. Name or describe it — 'brick red', 'the blue on old Greek shutters', 'no colour, just black and cream'."

### Q6 → `default_mode`
"Last one. Memorial or archival — do you want your wraps to feel emotional and voiced, or curated and restrained? Warm and personal, or museum-catalogue precision?"

## Execute

After the interview:

1. Map answers to the `MEMORY_BOOK_TASTE.md` schema:

| Field | Type | Source |
|-------|------|--------|
| `preferred_style` | slug | Q1 → nearest preset slug |
| `caption_voice` | free text | Q2 → verbatim or lightly edited |
| `banned_moves` | list | Q3 → array of named moves |
| `mood_vocabulary` | list | Q4 → array of 3+ words |
| `accent_color` | HSL or name | Q5 → resolved to a usable value |
| `default_mode` | `memorial` or `archival` | Q6 → one of two values |

2. Write the file using `memory_book.src.taste.save_taste()`.

## Verify

Read back the saved `MEMORY_BOOK_TASTE.md` and print it to the user in a compact block. Ask: "This look right? You can re-run `/darkroom teach` or `/darkroom reset` any time."
