# Gallery of Shame — Darkroom Anti-Slop

Concrete failure modes for the PDF poster and 9:16 MP4. Each is checkable against a rendered artifact. This file is the rubric for `/darkroom critique`.

Sources cited by shorthand:
- **DP** = `design-philosophy.md` (Rule N)
- **Vignelli** = `distill_vignelli.md` (Canon page N)
- **RUI** = `distill_refactoring_ui.md` (~page N)
- **Editorial** = `distill_editorial_design.md` (Rule N / pages N)
- **TwT** = `distill_thinking_with_type.md` (page N)
- **Impeccable** = `skill_structure_research.md` (Gallery of Shame)

---

## Visual Slop

### 1. The Spotify Wrapped Clone

**What it looks like.** Purple-to-blue gradient background. Big centered stat ("You took 1,247 photos!"). Rounded-corner cards floating over the gradient. Playful sans in white.

**Why it's bad.** The single most common AI-generated "year in review" aesthetic — it signals the model defaulted. Violates DP Rule 10 (reject decoration; constraint carries personality), DP Rule 6 (one ink, one accent — no gradients). Impeccable names purple gradients and AI color palettes as top-tier slop. Vignelli pp. 11–14: gradients and shadows are visual pollution.

**What to do instead.** Near-black on off-white. One earned accent color. Typography and white space carry the personality. The Darkroom is an editorial artifact, not a tech product wrap-up.

### 2. Gradient Text

**What it looks like.** Headline filled with a hue ramp (cyan→magenta, gold→bronze). Sometimes with a glow or outer shadow.

**Why it's bad.** Impeccable's named anti-pattern. Vignelli p. 55: type is a carrier of information, not a pictorial exercise. DP Rule 6 (no gradients). Gradient fills reduce contrast and degrade under video re-encoding.

**What to do instead.** Solid color. Make everything else quieter instead (DP Rule 4: de-emphasise to emphasise). A 100pt title in #1A1A1A on #FAF7F2 commands more attention than any gradient.

### 3. Drop-Shadow on Everything

**What it looks like.** Every card, text block, and image floats above its surface with a heavy 12px shadow. Multiple elements, multiple shadows, no consistent light source.

**Why it's bad.** Vignelli pp. 11–14: shadows add no semantic value. RUI ~pp. 156–166: shadows must have a consistent light source and be subtle; maximalist shadows look amateur. DP Rule 10: no drop shadows used decoratively.

**What to do instead.** Separate with spacing and tonal shifts (5% L change in background). If a shadow is semantically needed (one floating card), use a subtle consistent-source pair: `0 4px 6px rgba(0,0,0,.07)` (RUI Rule 8).

### 4. The Cardocalypse

**What it looks like.** Every element wrapped in a rounded-corner card. Cards nested inside cards. The layout looks like a Trello board.

**Why it's bad.** Impeccable names nested cards as a primary anti-pattern. Cards are interactive UI, not editorial. RUI ~pp. 198–206: borders are a crutch. DP Rule 10: no decoration that doesn't serve hierarchy.

**What to do instead.** Separate with the grid and white space. If a card is semantically needed (a pull quote that must float), one per poster, minimal shadow, consistent light source.

### 5. Pure Black on Pure White

**What it looks like.** Body text in #000000 on #FFFFFF. Maximum contrast, harsh, clinical.

**Why it's bad.** RUI anti-slop rule 1: pure extremes feel unrefined. DP Rule 6 specifies #1A1A1A on #FAF7F2.

**What to do instead.** Near-black (L5–10%) on warm off-white (L95–98%). Captions at 70% black. The warmth signals editorial intention.

### 6. The AI Color Palette

**What it looks like.** Teal + coral + lavender + sage green + dusty rose. The "harmonious" five-color palette every LLM generates by default.

**Why it's bad.** Impeccable flags this explicitly. Five colors = five competing signals = no hierarchy. Violates DP Rule 6 (one ink, one accent). Vignelli p. 78: color as decoration is vulgarity.

**What to do instead.** #1A1A1A on #FAF7F2. One accent — brick-red, deep navy, or burnt sienna — for section labels, drop caps, or rules. Earn every additional color with a semantic reason.

### 7. The Sentimental Blur

**What it looks like.** Photos treated with heavy Gaussian blur, soft vignettes, warm color overlays, lens flares. The "golden hour Instagram filter" applied uniformly.

**Why it's bad.** Effects that don't serve hierarchy are decoration (DP Rule 10). Uniform blur destroys editorial value — the viewer can't see the image. Editorial Rule 8 demands image treatment as a system, not a blanket effect.

**What to do instead.** Respect the photograph. Crop deliberately. One consistent treatment (aspect ratio, border, color profile) across all images. If depth-of-field is needed, it should exist in the original photo.

### 8. Low-Contrast Subtitle Burn

**What it looks like.** White text over bright sky. Light grey on a light photo. Any text-on-image pairing below 4.5:1.

**Why it's bad.** WCAG AA requires 4.5:1 (RUI Rule 5, ~pp. 118–124). DP Rule 6 specifies scrims to guarantee contrast. Unreadable subtitles signal carelessness.

**What to do instead.** Always use a scrim: semi-transparent dark overlay (60% opacity black bar) behind subtitles. Test every frame.

---

## Typographic Crimes

### 9. The Font Salad

**What it looks like.** Title in Playfair Display. Subtitle in Montserrat. Body in Lora. Captions in Roboto. Date in Oswald.

**Why it's bad.** DP Rule 3: two typefaces, maximum. TwT p. 54: three or more families on a page = chaos. Every additional family dilutes the system.

**What to do instead.** One serif body, one contrasting sans for display. Hierarchy from size, weight, and italic — not from switching families.

### 10. The Overused-Font Tell

**What it looks like.** Display set in Inter, Geist, Mona Sans, Plus Jakarta Sans, Space Grotesk, Recoleta, Instrument Sans, or Fraunces.

**Why it's bad.** Impeccable names these as "every model learned from the same slop." They scream AI-generated. DP Rule 3 demands typeface choice carry personality through constraint.

**What to do instead.** Families with editorial heritage: Sabon, Miller, Garamond Premiere Pro for body; Futura, Verlag, Gill Sans for display. The typeface choice is a design decision, not a default.

### 11. Two Cousins

**What it looks like.** Adobe Garamond Pro Bold paired with Adobe Jenson Pro Bold. Or Inter paired with Söhne. Two near-identical faces that cancel each other out.

**Why it's bad.** TwT p. 54: "too close for comfort… too similar to provide a counterpoint." The reader sees noise, not contrast.

**What to do instead.** Pair across genres: serif + sans, humanist + geometric. The contrast must be obvious.

### 12. The Indecisive Scale Jump

**What it looks like.** Title 36pt. Subtitle 30pt. Body 24pt. Caption 20pt. Everything in a narrow band.

**Why it's bad.** TwT p. 42: "Minimal differences in type size make this design look tentative and arbitrary." DP Rule 2: use a 1.5–2× ratio between levels. "Decisive jumps read as confidence; tiny jumps read as indecision."

**What to do instead.** PDF: 10pt → 18pt → 32pt → 80pt. Video: 36pt → 56pt → 200pt. Three to four levels with big gaps. No mid-sizes.

### 13. Faux Typography

**What it looks like.** Pseudo-italic (mechanically slanted roman). Pseudo-bold (stroke added by software). Pseudo small caps (shrunken full caps). Horizontally scaled type faking condensed.

**Why it's bad.** TwT p. 52: "puny and starved; they are an abomination against nature." TwT p. 38: scaling destroys the type designer's optical balance. These look wrong even to non-designers.

**What to do instead.** Real italic, real bold, real small caps, real condensed from the chosen family. If the family doesn't have them, change family.

### 14. The Emphasis Pile-Up

**What it looks like.** A word simultaneously bold, italic, underlined, colored, and in a different typeface. Or a headline that's bold + all-caps + large + colored + shadowed.

**Why it's bad.** TwT p. 132: "Emphasis can be created with just one shift." DP Rule 9: italic, OR weight change, OR colour shift — never two, never three.

**What to do instead.** One signal per level. Body emphasis = italic. Header = weight change. Title = size jump. Never stack.

### 15. Justified Narrow Columns

**What it looks like.** Body text justified on a column under 60 characters. Rivers of white between words.

**Why it's bad.** Vignelli p. 66: justified is "fundamentally contrived." TwT p. 112: "ugly gaps appear when the line length is too short." DP Rule 7: never justify under 60 characters. In 9:16 video, the measure is always too short.

**What to do instead.** Flush-left, ragged-right. Always. Poster: 45–75 characters per line. Video: accept the rag.

### 16. Display Type at Caption Size

**What it looks like.** A typeface with delicate hairlines (designed for 48pt+) used at 8pt for credits. Thin strokes disappear.

**Why it's bad.** TwT p. 41: "Some typefaces that work well at large sizes look too fragile when reduced." Display cuts have hairlines that fall below rendering threshold after PDF compression or video encoding.

**What to do instead.** Caption or text optical cuts at small sizes. If no optical sizes exist, choose a sturdier family for captions.

### 17. Dumb Quotes and Hyphens-as-Dashes

**What it looks like.** Straight quotes ("like this") instead of curly. Hyphens in ranges (2019-2025). Double hyphens for em dashes (word -- word).

**Why it's bad.** TwT p. 211: "incorrectly used prime marks must be routed out and destroyed." At poster display sizes, a straight quote is unmistakable. In subtitles, hyphens-as-dashes signal machine generation.

**What to do instead.** Curly quotes always. En dash for ranges (2019–2025). Em dash for breaks. Automate in the rendering pipeline.

### 18. All-Caps Body Text

**What it looks like.** Multiple sentences or a full paragraph in ALL CAPITALS.

**Why it's bad.** TwT p. 52: "A LONG PASSAGE SET ENTIRELY IN CAPITALS CAN LOOK UTTERLY INSANE." Caps destroy word shape. Reading speed drops 13–20%. On a video frame where reading time is limited, this is hostile.

**What to do instead.** Caps for short labels only (2–4 words max), tracked +75 to +100. Body in sentence case. Section tags in small caps.

### 19. Stacked Lowercase

**What it looks like.** A side label set one letter per line, reading downward in lowercase.

**Why it's bad.** TwT pp. 120–122: "stacks of lowercase letters are especially awkward because the ascenders and descenders make the vertical spacing appear uneven." Named TYPE CRIME.

**What to do instead.** Rotate the baseline 90°. Or use square caps. Never stack lowercase.

### 20. Indent Plus Paragraph Space

**What it looks like.** Paragraphs both indented and separated by a blank line.

**Why it's bad.** TwT p. 127: "squanders space and gives the text block a flabby, indefinite shape." Named TYPE CRIME.

**What to do instead.** Pick one. Em-quad indent or half-line space. First paragraph never indented.

---

## Caption Failures

### 21. The Museum Label

**What it looks like.** "A photograph of the family at the beach, summer 2025." Or worse: "Beach. Summer 2025."

**Why it's bad.** DP Rule 8: captions are sentences, not labels. TwT p. 130: captions are the most-read text. Editorial Rule 4: captions extend the story with craft and voice. A label tells the viewer nothing they can't already see.

**What to do instead.** A sentence that stands alone: "The tide was out far enough to walk to the sandbar — first time in three years anyone remembers that happening." Lead with a small-caps date tag, then a written line.

### 22. The Generic AI Caption

**What it looks like.** "A beautiful moment captured in time." "Memories that will last forever." "A perfect day."

**Why it's bad.** Vignelli p. 10: semantics demands every element carry meaning. These are the absence of meaning. Impeccable calls this pattern an AI slop signature.

**What to do instead.** Name the place, the time, the weather, or a specific detail. If the agent cannot name something concrete, the caption stage failed and CRITIQUE must reject.

### 23. Caption Far From Image

**What it looks like.** Image at top of poster, caption at the bottom margin, separated by a body block.

**Why it's bad.** TwT p. 130: "if captions are essential to understanding the visual content, keep them close to the pictures."

**What to do instead.** Caption adjacent to or directly under the image. Never wrapping under the next image.

### 24. Caption Echoing the Headline

**What it looks like.** Headline: "Our trip to Tokyo." Caption under hero photo: "Our trip to Tokyo."

**Why it's bad.** Editorial Rule 4: captions extend, not echo. Wasted real estate.

**What to do instead.** The caption tells you something the headline doesn't — a date, a fact, a sensory detail.

---

## Motion Slop (9:16 MP4 only)

### 25. Ken Burns Everywhere

**What it looks like.** Every photo gets the same slow zoom-in. Same speed. Same direction. Same duration. No variation, no pauses, no cuts.

**Why it's bad.** Pacing requires contrast (Editorial Rule 5; DP Rule 5: white space is structural). Uniform motion is the video equivalent of a cramped layout — no breathing room. The viewer zones out by the third identical pan.

**What to do instead.** Vary the motion vocabulary. Hold still for 2s before a slow pan. Cut between tight crop and wide shot. Reserve zoom for the single most important image per chapter. Motion reveals information; it doesn't perform itself (DP Rule 10).

### 26. Bounce-Swipe Transitions

**What it looks like.** Every scene change uses a bouncy spring animation, a swipe with overshoot, a zoom-rotate combo, or a page flip. Multiple transition types in one video.

**Why it's bad.** DP Rule 10: no "swipe-bounce" transitions. Vignelli p. 72: "In a world where everybody screams, silence is noticeable." Transitions that call attention to themselves distract from the content. Will look dated within 18 months.

**What to do instead.** Clean cuts. Or a single consistent transition (200ms crossfade) used throughout. One vocabulary, not a catalog.

### 27. Lens Flare, Glow, Bloom

**What it looks like.** Hero photo has a god-ray overlay. Headline glows. End card has a particle field or animated bokeh.

**Why it's bad.** DP Rule 10: no lens flares, no bloom, no background motion-graphic loops. Vignelli pp. 11–14: these are "visual vulgarities." They communicate nothing.

**What to do instead.** Trust the photo. Trust the type. The frame's strength is what it omits.

### 28. Motion-Graphic Background Loop

**What it looks like.** Animated particles, floating circles, slow geometric patterns, or parallax star fields behind the content. The background is always moving.

**Why it's bad.** DP Rule 10: no background motion-graphic loops. Continuous background motion competes with content for attention and makes text harder to read. Signals "template," not "editorial artifact."

**What to do instead.** Static or near-static backgrounds. A 0.5% scale shift over 8s is the ceiling. The photos and words are the motion. Everything else holds still.

### 29. Text Animation as Emphasis

**What it looks like.** A word in the caption pulses in size and colour. Or: every line of text kinetically enters the frame letter-by-letter.

**Why it's bad.** TwT p. 132: animation counts as a signal of emphasis. Combining it with size + colour stacks three signals. DP Rule 9: one signal is enough.

**What to do instead.** Text appears and stays. If a word matters, italicise it. One signal per shot.

---

## Pacing & Composition

### 30. Centered-Everything Poster

**What it looks like.** Title centered. Subtitle centered. Body centered. Caption centered. Every element on a vertical axis, tombstone-like.

**Why it's bad.** Vignelli p. 66: flush-left is the default. TwT p. 112: centering = formal, classical, tombstone-like — not for continuous reading. DP Rule 7: never centre body copy. RUI ~pp. 59–65: equal positioning is static and boring.

**What to do instead.** Flush-left, ragged-right for body and captions. Anchor to the grid's left edge. Use unequal spacing ratios (3:1, 4:1) for rhythm. Centre only ceremonial single lines (end-card, title if symmetrical).

### 31. No Dominance

**What it looks like.** Three images at the same size, three headlines at the same weight, no clear entry point. Equal visual weight everywhere.

**Why it's bad.** Editorial Rule 1: one element must command attention; all others support it. DP Rule 2: size is the first lever. Without dominance the eye wanders and comprehension fails.

**What to do instead.** One hero at 50–70% of the surface. Everything else proportionally smaller and quieter.

### 32. Slideshow Pacing

**What it looks like.** Every video frame exactly 3s. No moment lingers; no moment punctuates.

**Why it's bad.** Editorial pacing principle: alternation between dense and sparse, fast and slow. Equal duration is the absence of pacing. DP Rule 5: white space (temporal silence) is structural.

**What to do instead.** Vary. Hero frames 3–4s. Caption cards 2.5s. Pull-quote moments 4–5s (the hold is the emphasis). End card 2s. The variation itself carries meaning.

### 33. Filling the Corners

**What it looks like.** Every corner of the poster has content. No outer breathing room. Content bleeds to every edge.

**Why it's bad.** Vignelli p. 92: white space is architecture. TwT p. 153: margins are the user interface. DP Rule 5: reserve 15–40% as white space.

**What to do instead.** ≥15mm outer margins on A3. Reserve at least one corner as pure field. The poster should look ⅓ empty when squinted at.

### 34. End Card With Logo Only

**What it looks like.** Final 3s is a centered logo on white. No date. No edition. No closing thought.

**Why it's bad.** Editorial pacing requires closure, not branding. Vignelli p. 90: a date stamp is an identifier that carries meaning. An empty logo card wastes the last impression.

**What to do instead.** Edition label (tracked small caps: "AUTUMN 2025 — EDITION 04"), one-line closing sentence, fade.

---

## How to Use This File

**In `/darkroom critique`:** After rendering, screenshot the PDF and sample 3–5 MP4 frames. Check each against this list. Any match → flag for re-render with the specific corrective from "What to do instead." Cap at 2 retries.

**Self-review gate:** If an anti-pattern name alone (without reading the description) doesn't tell you exactly what's wrong, the name is too vague. Fix it.
