# Darkroom — Style Presets

Five locked presets. `dark-editorial` is the default and the only fully-implemented template; the remaining four are reference specifications for future template work. Each is fully specified so that `/darkroom wrap --style=<slug>` produces a reproducible visual output. Each preset extends the universal floor in `design-philosophy.md`; nothing here contradicts it.

Voice carries through. `dark-editorial` is warm cinematic restraint. Vignelli's preset is absolutist. Lupton's is typographically precise. Refactoring UI's is anti-slop pragmatism. Editorial Design's is paced storytelling.

---

## Comparison Matrix

| Dimension | **dark-editorial** (default) | restrained-modernist (Vignelli) | functional-minimalism (Refactoring UI) | editorial-grid-authority (Caldwell & Zappaterra) | editorial-typographic (Lupton) |
|---|---|---|---|---|---|
| **One-liner** | Dark-field warmth, variable serif, grain | Pure geometry, primary colour as identifier | Hierarchy through systematic constraint | Dominant image, proportional grid, paced spreads | Baseline-aware grid, serif body, ruthless type hierarchy |
| **Display font** | Fraunces 360, stretch 110 % | Helvetica / Bodoni / Futura, single weight | Söhne / Inter / SF Pro, Bold | Serif high-contrast (Tiempos / Canela), Medium–Bold | Sans display (Futura / Verlag / Thesis), heavy condensed |
| **Body font** | Inter 400–600 | Same family as display | Same sans family, Regular 400 | Serif or contemporary sans, 10–12 pt | Serif with optical sizes (Sabon / Miller / Garamond Premiere) |
| **Body size / leading** | 8.5 pt / 1.4 (poster) · 30 pt / 1.4 (video) | 14 pt / 18 pt (poster) · 24 pt / 30 pt (video) | 13 px / 1.5 (poster) · 28 pt / 1.4 (video) | 11 pt / 16 pt (poster) · 28 pt / 1.5 (video) | 10 pt / 13 pt (poster) · 56 pt / 130 % (video) |
| **Type families** | 2 (serif display + sans body) | 1 only | 1, sometimes 2 | 1 family with full optical range | 2 (serif body + sans display) |
| **Palette** | Near-black bg + warm off-white ink + red-orange accent | Pure red, blue, yellow + black + white | HSL system, muted base + 1 saturated accent | Black + 1 bold accent (emerald / navy / sienna) + 10–15K rule | Near-black on warm off-white + brick-red accent |
| **Accent rule** | Kickers, stat highlights, closing signature | Identifier only, never decoration | One 100 %-saturated pop, rest muted | Pull quotes and cross-heads only | Drop caps, rules, captions only |
| **Grid** | 12-column proportional, A3 portrait | Strict 6×8 modular, narrow margins | 8 px / 16 px base, fixed scale | 8–12 column proportional, 60 / 40 image-text | 6-column multicolumn + baseline grid + hang line |
| **Whitespace** | Generous; hairline rules as separators | ≥ 40 % | Fixed-ratio (1:1, 2:1, 3:1) | ≥ 15 %, generous around hero | Margins as UI; asymmetric outer/inner |
| **Voice** | Warm, understated, concrete | Anti-rhetorical, declarative | Direct, utilitarian, no waffle | Authoritative, narrative captions | Editorial, declarative, structurally clear |
| **Motion (video)** | Variable duration; zoom OR pan; fade-in text | None except along grid axis | Crossfade + opacity scrim, no easing tricks | Paced cuts: hero → caption → quote → close | Type cuts on baseline; never floats |
| **Best for mode** | memorial *or* archival | archival | archival | memorial | memorial *or* archival |
| **Default for** | All wraps (implemented template) | Institutional / professional wraps | Data-heavy or productivity wraps | Year-in-review with strong photography | Photo essay with written captions |

---

## Preset 0 — `dark-editorial` (default)

*The implemented template. Warm cinematic restraint on a near-black field — Fraunces' optical warmth meets Inter's clarity.*

**One-liner.** Dark-field editorial with variable optical serif, grain texture, and warm accent — designed to feel like a printed artefact photographed in low light.

### Typography
- **Display.** Fraunces (variable serif, opsz 9–144), weight 360, stretch 110 %. Title 78 pt poster · 168 pt video. Tight leading (0.92–0.95).
- **Body / kicker.** Inter, weight 400–600. Kickers tracked +0.2 em, uppercase.
- **Caption.** Inter 8.5 pt poster · 30 pt video. Muted ink (#B0A99A).
- **Tracking.** Kickers +0.2 em. Display –0.025 em.
- **Alignment.** Flush-left throughout.

### Palette
- **Background.** Near-black #0E0B08.
- **Ink.** Warm off-white #F4EFE6.
- **Accent.** Warm red-orange #F25C3D.
- **Muted.** #8C8579 for kickers and secondary text.
- **Hairline.** #2A2520.
- **Grain.** 3 px radial dot pattern at 2.5 % white, mix-blend overlay.

### Layout
- **Grid.** 12-column proportional (Tailwind `grid-cols-12`). A3 portrait.
- **Margins.** 16 mm horizontal, 14 mm top, 12 mm bottom.
- **Structure.** Title block (7+5 split) → stat strip → scene row 1 (5+4+3) → scene row 2 (4+4+4) → closing + optional scene 8.
- **Whitespace.** Generous between sections; hairline rules as separators.

### Voice / caption tone
- Warm, understated. Concrete details over adjectives. "The pour-over ritual that outlasted every other morning habit." No museum labels, no marketing voice.

### Motion guidance (video)
- Variable scene durations (2.5–4 s). Ken Burns: zoom OR pan per scene, never both.
- Headline fades in (opacity + translateY). No typewriter effects.
- Grain overlay on every frame.

### When to use
- Default template. Year-in-review with photography. Personal wraps, travel recaps, any context where warmth and restraint coexist.

---

## Preset 1 — `restrained-modernist`

*Vignelli Canon. Absolutist. The preset for someone who would rather skip a wrap than ship a gradient.*

**One-liner.** Pure geometry, disciplined typography, primary colour as identifier — form stripped to semantic essence.

### Typography
- **Family.** One only. Helvetica Neue, Bodoni 72, Futura, or Garamond. No third option.
- **Weights.** Bold for headline, Regular for body. Two weights total.
- **Scale (poster).** Title 120 pt → subhead 36 pt → body 14 pt → caption 9 pt. Roughly 3× jumps.
- **Scale (video).** Title 200 pt → body 56 pt → caption 32 pt.
- **Leading.** Title 100 % (tight). Body 130 %. Caption 125 %.
- **Tracking.** Caps tracked +75. Lowercase metric (zero).
- **Alignment.** Flush-left only. Headlines may centre. Justified is forbidden.

### Palette
- **Background.** Pure white #FFFFFF or pure black #000000.
- **Text.** Pure black on white, or pure white on black.
- **Accent.** Exactly one of: red HSL(0, 100, 50), blue HSL(220, 100, 45), yellow HSL(52, 100, 50). Used as identifier (date stamp, section marker), never as field.
- **Forbidden.** Tints, gradients, overlays, secondary accents.

### Layout
- **Grid.** 6×8 modular grid. A3 portrait → 6 columns × 8 rows. Narrow outer margins (15 mm).
- **Hierarchy.** One large hero (image or headline), one supporting block, one identifier mark. That is all.
- **Whitespace.** ≥ 40 % of surface left empty.

### Voice / caption tone
- Anti-rhetorical. No emotional language. Captions name and place: "WARSAW. SEPTEMBER 2025." Then a single sentence of fact. Never adjectives.

### Motion guidance (video)
- No easing. Cuts only. Text appears and stays static for its duration, then cuts to black or white.
- If movement is required, elements translate along a single grid axis (left-right or top-bottom). Never diagonal. Never scaled.
- Frame rhythm: hero (3 s) → cut to white (0.5 s) → caption (3 s) → cut.

### When to use
- Institutional retrospectives. Annual reports as wraps. A wrap for someone whose taste is "Knoll catalogue, not Spotify Wrapped." Default for `--mode=archival` when the user's `MEMORY_BOOK_TASTE.md` reads "modernist", "rigorous", "Swiss".

### When NOT to use
- Anything emotional, warm, intimate, or playful. Children's milestones. Personal grief. A wedding. Anything that benefits from narrative pacing — Vignelli's preset has no pacing, only presence.

---

## Preset 2 — `functional-minimalism`

*Refactoring UI. Pragmatic anti-slop. The preset that always passes a contrast check.*

**One-liner.** Disciplined visual hierarchy through systematic constraint, HSL-precise colour, and ruthless de-emphasis.

### Typography
- **Family.** One sans (Söhne, Inter, SF Pro). Optionally a serif accent for pull quotes only.
- **Weights.** Regular 400, Medium 500, Bold 700. Three maximum.
- **Scale (poster).** Title 52 pt → subhead 28 pt → body 13 pt → caption 11 pt.
- **Scale (video).** Title 96 pt → subtitle 48 pt → caption 28 pt.
- **Leading.** Body 1.5–1.6× size. Title 1.1×.
- **Tracking.** Default (zero). Caps +50.
- **Alignment.** Flush-left.

### Palette
- **Base.** Cool grey HSL(209, 15, 28) or warm grey HSL(41, 15, 28).
- **Background.** Off-white HSL(40, 20, 96) or near-black HSL(220, 15, 12). Never pure #FFF or #000.
- **Accent.** One desaturated primary at S 60–70 % for body field, one S 100 % accent for the single magnetic moment per artefact (the call-to-action, the hero stat).
- **Contrast.** WCAG AA minimum: 4.5:1 text, 3:1 UI elements. Run a checker; never eyeball.

### Layout
- **Grid.** 8-px base grid. Padding multiples: 8, 16, 24, 32, 48, 64.
- **Spacing ratios.** Use 3:1 or 4:1 between groups. 16-32-8, not 16-16-16.
- **Hierarchy.** Headline is a magnet because the body field has retreated.
- **Whitespace.** Active. Asymmetric. Ratio-based.

### Voice / caption tone
- Direct, utilitarian. Microcopy as functional clarity. Captions name what is happening; no apology, no flourish. "Three days in Lisbon. Twelve photos kept." Information, not feeling.

### Motion guidance (video)
- Crossfades and scrim only. No bounce, no swoosh, no morphing.
- Background photo opacity drops to 35 % under text; text sits in full-white on the muted plate.
- Text appears and holds; no entrance animation other than 200 ms fade.

### When to use
- Productivity and review wraps. Yearly stats. Quantified-self artefacts. A wrap that needs to read on a phone in daylight. Default for `--mode=archival` when the user is colour-blind, low-vision, or just allergic to maximalism.

### When NOT to use
- A wrap with emotional weight where the muted palette will read as cold. Decorative or storytelling artefacts. Anything where a serif body matters more than a contrast ratio.

---

## Preset 3 — `editorial-grid-authority`

*Caldwell & Zappaterra. The magazine spread. The preset that paces.*

**One-liner.** Proportional grids with dominant hierarchy, generous negative space, and authoritative typography that respects classical design.

### Typography
- **Headline / deck.** High-contrast serif (Tiempos Headline, Canela, Miller Display) at Bold or Medium. 48–72 pt poster. 60 pt video.
- **Body.** Serif body (Tiempos Text) or contemporary sans (Söhne) at 10–12 pt poster · 16–18 px digital. Line height 1.5–1.65.
- **Captions.** Full sentences in italic, 8–9 pt. Different colour (70 % black) — not just smaller.
- **Cross-heads.** Bold, 11–13 pt, max 2–3 lines.
- **Alignment.** Flush-left for body; headlines may align to image edges or break across the grid.

### Palette
- **Primary.** Black or 90–100 K grey for text.
- **Accent.** One bold colour — emerald HSL(150, 50, 30), deep navy HSL(220, 60, 22), or burnt sienna HSL(15, 65, 40). Used for cross-heads, pull quotes, rule lines.
- **Tertiary.** Light grey HSL(40, 5, 88) for separations.
- **Background.** White or warm off-white HSL(40, 25, 97).

### Layout
- **Grid.** 8–12 column proportional grid. Margin ratio 1:1.5:1.5:1 (in/top/out/bottom).
- **Dominance.** 60 / 40 image-to-text on hero spreads; reverse for data features.
- **Negative space.** ≥ 15 %; generous around hero and pull quotes.
- **Hierarchy.** Three to four discrete levels (headline → subhead → body → caption).

### Voice / caption tone
- Authoritative without coldness. Informative without explanation. Captions extend the narrative; they are sentences with voice. "Designer Sarah Chen works from her studio in Brooklyn, where natural light and an analog light table inform her approach."

### Motion guidance (video)
- Pacing is the design. Hero (3 s, full frame) → kicker (1 s) → headline (2 s) → body caption (3 s) → pull quote moment (2.5 s) → close.
- Use full-bleed images alternating with type-only frames to create rhythm.
- Pull quote frame holds longer than its neighbours; that hold *is* the emphasis.

### When to use
- Year-in-review wraps with strong photography. Travel essays. A wrap that wants to feel like a *Wallpaper* or *Monocle* feature. Default for `--mode=memorial`.

### When NOT to use
- Sparse archives with weak imagery. Data-heavy wraps that would read as noisy in a magazine grid. Anything where speed of scanning matters more than pacing of reading.

---

## Preset 4 — `editorial-typographic`

*Ellen Lupton. Type as content given a body. The preset that respects the baseline.*

**One-liner.** Ink-on-paper restraint, ruthless hierarchy, and a baseline-aware grid carrying serif body type with one disciplined display partner.

### Typography
- **Body.** Serif text family with optical sizes — Sabon, Adobe Garamond Premiere Pro, Scala Pro, or Miller. Use the *Regular* optical cut at 9–11 pt; use the *Caption* cut at 6–8 pt; use the *Display* cut at ≥ 24 pt.
- **Display partner.** A contrasting sans — Futura, Verlag, Gill Sans, or Thesis Sans Bold. Heavy or condensed for titles.
- **Body size / leading.** 10 pt / 13 pt (130 %) for poster. 56 pt / 130 % for video subtitles.
- **Tracking.** Lowercase body: zero. ALL CAPS labels: +75 to +100. White-on-black caps: +10 to +20 looser.
- **Italic.** Real italic only; never pseudo-italic. Single signal of emphasis.
- **Numerals.** Old-style numerals in body; lining numerals in display. OpenType Pro features required.
- **Alignment.** Flush-left, ragged-right. Centred only for ceremonial single lines.

### Palette
- **Body.** Near-black ink HSL(20, 5, 10) on warm off-white HSL(40, 25, 97).
- **Accent.** One — brick-red HSL(10, 55, 40) or deep ochre HSL(35, 60, 38). Used for drop caps, rules, section labels, captions. Sparingly.
- **Background fields.** Pale grey HSL(40, 5, 93) for example or quote panels only.

### Layout
- **Grid.** 6-column multicolumn grid with 5 mm gutters. Asymmetric margins (18 mm outer, 22 mm top, 25 mm bottom). Baseline grid set to body leading (13 pt). Hang line at upper third — title datum lives there.
- **Hierarchy.** Big size jumps (1.5–2× per level). Body 10 → subhead 18 → header 32 → title 80.
- **Captions.** Italic small text adjacent to image, leading with a small-caps label.

### Voice / caption tone
- Editorial, declarative, structurally clear. Captions describe what the image *is* and what it is *doing*. "Kyoto, autumn 2025. The maple drops a week early; the photograph catches the moment between colour and ground." Short. Specific. No marketing voice.

### Motion guidance (video)
- Type cuts on baseline. Subtitles always at y=1500 px in 1080×1920. End-card label tracked caps.
- Two-line subtitle maximum. Hold for ≥ 2.5 s.
- The Display cut is for the title card. The Caption cut is for burned-in subtitles (it survives compression).
- No floating type. Every text element appears at a fixed grid coordinate.

### When to use
- Photo essays with written captions. Archival wraps that want gravitas. A wrap for a reader who notices italics. Default for `--mode=archival` when `MEMORY_BOOK_TASTE.md` reads "editorial", "literary", "magazine".

### When NOT to use
- Wraps where the user wants warmth and emotion to dominate over typographic precision. Animation-heavy outputs. Social-feed wraps where compressed type and small frames make optical-size distinctions invisible.
