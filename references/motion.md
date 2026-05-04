# Motion Design Reference — 9:16 MP4

Unified motion specification for Darkroom video output. Consolidates and deepens the per-preset motion specs in `styles.md` and the five motion anti-patterns (#25–29) in `anti_slop.md`. This is the single source of truth for how things move.

Cross-references:
- `design-philosophy.md` — universal design rules (DP Rule N)
- `styles.md` — per-preset typography, palette, grid, voice, motion
- `anti_slop.md` — 34 named anti-patterns (entries #25–29 are motion-specific)

---

## 1. Timing Vocabulary

Every duration in Darkroom is expressed in seconds at 30 fps. One second = 30 frames. These are the constants.

### Scene Duration

Each photo scene runs **2.5–4 s**. Never uniform across scenes.

| Photo count | Target total | Avg scene duration |
|---|---|---|
| 5–8 photos | 15 s | 2.5–3 s |
| 10–20 photos | 30 s | 2.5–3.5 s |
| 20–50 photos | 60 s | 2.5–4 s |

- **DO:** Scene 1 at 3.5 s, scene 2 at 2.5 s, scene 3 at 3 s, scene 4 at 4 s (hero), scene 5 at 2.5 s.
- **DON'T:** Every scene at 3 s. See anti-pattern #32 (Slideshow Pacing) and #25 (Ken Burns Everywhere) in `anti_slop.md`.

### Transition Duration

Type-dependent. These are the ceilings.

| Transition | Duration | When |
|---|---|---|
| Hard cut | 0 s (0 frames) | Default. Keeps energy. |
| Cross-dissolve | 0.5–0.8 s (15–24 frames) | Reflective or melancholy beats. |
| Fade to black | 0.3 s out + 0.3 s in (9 + 9 frames) | Chapter break. Section change. |
| Opacity ramp (text) | 0.1–0.3 s (3–9 frames) | Text entry/exit. |

- **DO:** 0.5 s cross-dissolve between two quiet scenes. Hard cut into an upbeat scene.
- **DON'T:** 1.2 s dissolve (sluggish). 0.1 s dissolve (indistinguishable from a cut — just cut).

### Text Overlay Duration

All text must be readable at 1x playback speed.

| Text type | Minimum hold | Maximum hold |
|---|---|---|
| Title card | 2 s | 3 s |
| Caption overlay | 2 s | 3 s |
| Stat/number | 1.5 s per stat | 2 s per stat |
| Kicker/label | 1.5 s | 2.5 s |
| End card | 2 s | 4 s |

Reading-speed rule: **12 words per second** is the upper bound for comfortable comprehension. A 24-word caption needs at least 2 s on screen.

- **DO:** Hold a 20-word caption for 2.5 s with 0.3 s fade-in and 0.3 s fade-out.
- **DON'T:** Flash a caption for 0.8 s. If the viewer can't finish reading, the text failed.

### Music Cue Alignment

Transitions should land on beat boundaries when possible. At 120 BPM (common for ambient beds), beats land every 0.5 s. At 90 BPM, every 0.67 s.

- **DO:** Shift a cut by 2–3 frames to land on the nearest beat. This costs nothing and adds cohesion.
- **DON'T:** Ignore the score entirely. Transitions that land between beats create subliminal unease. See anti-pattern #7 below (Music-Ignorant Cuts).

---

## 2. Camera Movement Vocabulary

Camera movements on still photos. Every movement serves a purpose: revealing information, directing attention, or establishing emotional register.

### Ken Burns (Slow Zoom + Pan)

The default movement for photo-based video. A gentle zoom and/or pan that gives life to a still image.

**Rules:**
- MUST vary direction per scene. Alternate: zoom-in left, zoom-out right, pan left-to-right, static hold.
- MUST vary speed per scene (within the preset's range).
- Never combine zoom AND pan simultaneously on the same scene. Pick one axis of motion.
- The zoom percentage and speed are mood-dependent (see Section 5).

**Remotion implementation:**
```tsx
// Zoom-in from 1.0 to 1.08 over the scene duration
const scale = interpolate(progress, [0, 1], [1.0, 1.08]);
// Pan: translate along ONE axis only
const tx = interpolate(progress, [0, 1], [0, 20 * direction]);
// Apply:
transform: `scale(${scale}) translate(${tx}px, 0)`
```

- **DO:** Scene 1 slow zoom-in (1.0 → 1.06), scene 2 slow pan right (tx 0 → 18), scene 3 static hold, scene 4 push-in (1.0 → 1.12).
- **DON'T:** Every scene zooms in from center at the same speed. Anti-pattern #25 (Ken Burns Everywhere).

### Static Hold

No camera movement. The photo fills the frame and stays.

**When to use:**
- Text-heavy scenes where camera motion distracts from reading.
- Breathing room between two moving scenes.
- The `quiet` mood preset (dominant movement type).
- After a sequence of 3+ moving scenes — the pause resets the viewer's attention.

- **DO:** Hold a text card completely still for 3 s. Let the words do the work.
- **DON'T:** Add a 1% zoom "just to keep it alive." Stillness is a deliberate choice, not a bug.

### Push-In

A more aggressive zoom toward the subject. Reserves emphasis for a single emotional beat.

**Rules:**
- Maximum 1–2 push-ins per video.
- Zoom range: 1.0 → 1.10–1.15 (larger than standard Ken Burns).
- Speed: slightly faster than standard Ken Burns for the same duration.
- Use on the "hero" photo — the image the pacing architecture peaks on.

- **DO:** Push-in on the single strongest photo in the set. One per video.
- **DON'T:** Push-in on three consecutive scenes. It dilutes the emphasis to nothing.

### Pull-Out

Zoom from a tight crop to the full image. Reveals context.

**When to use:**
- Opening shot (reveal the scene).
- Establishing shots (landscape, group, architecture).
- Closing shot (pulling away as farewell).

**Remotion implementation:**
```tsx
// Start zoomed in, pull out to full frame
const scale = interpolate(progress, [0, 1], [1.12, 1.0]);
```

- **DO:** Open with a pull-out on a landscape to establish place. Close with a slow pull-out on the final image.
- **DON'T:** Pull-out on a tight portrait — the crop won't have enough content to reveal.

### Pan

Horizontal or vertical movement across the image. No zoom.

**When to use:**
- Panoramic photos where the full width matters.
- Group photos where the pan reveals faces.
- Landscape/cityscape establishing shots.

**Rules:**
- Horizontal pan only on images with a landscape aspect ratio.
- Vertical pan only on tall subjects (buildings, trees, standing groups).
- Speed: 15–25 px per second. Slow enough to read details.

- **DO:** Slow left-to-right pan across a group photo at a dinner table.
- **DON'T:** Pan a tight portrait. There's nowhere to go.

### Forbidden Movements

These never appear in a Darkroom video:

| Movement | Why forbidden |
|---|---|
| Zoom + pan simultaneously | Competing vectors confuse the eye. Pick one. |
| Bounce/spring easing | Calls attention to the transition, not the content. Anti-pattern #26. |
| Jitter/shake | Simulates handheld for a still photo — dishonest and distracting. |
| Rotation | Photos are documents. Rotating them signals carelessness, not creativity. |
| Diagonal translation | Violates the grid axis constraint (DP Rule 1, Rule 10). |

---

## 3. Transition Vocabulary

Transitions mark the boundary between scenes. Their job is to be invisible — to serve the emotional register without calling attention to themselves.

### Hard Cut (0 s)

Scene A's last frame → Scene B's first frame. No interpolation.

**Emotional register:** Energetic, forward-moving, confident. The default.

- **DO:** Use hard cuts for 60–80% of transitions in an upbeat video. They keep pace.
- **DON'T:** Hard cut from a bright scene to a dark scene without considering the visual shock. If the luminance gap is extreme, use a 0.3 s dissolve instead.

### Cross-Dissolve (0.5–0.8 s)

Scene A fades out as Scene B fades in. Overlapping opacity.

**Emotional register:** Reflective, melancholy, time-passing, gentle.

**Remotion implementation:**
```tsx
// Using <Series> with overlap:
<Series>
  <Series.Sequence durationInFrames={sceneADur}>
    <SceneA />
  </Series.Sequence>
  <Series.Sequence
    durationInFrames={sceneBDur}
    offset={-18} // 0.6s overlap at 30fps = 18 frames
  >
    <SceneB />
  </Series.Sequence>
</Series>

// Inside each scene, fade tail/head:
// Scene A fade-out (last 18 frames):
const fadeOut = interpolate(
  frame,
  [durationInFrames - 18, durationInFrames],
  [1, 0],
  { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
);
// Scene B fade-in (first 18 frames):
const fadeIn = interpolate(
  frame,
  [0, 18],
  [0, 1],
  { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
);
```

- **DO:** Cross-dissolve between two quiet, thematically linked scenes.
- **DON'T:** Cross-dissolve between every scene. It turns the video into mush.

### Fade to Black (0.3 s out + 0.3 s in)

Scene A fades to black. Hold black for 0–0.2 s. Scene B fades in from black.

**Emotional register:** Chapter break. Marks a shift in time, place, or mood. The semicolon of video.

- **DO:** Fade to black between the "rising" section and the "peak" section. Once or twice per video.
- **DON'T:** Fade to black between every scene. It creates a funeral slideshow.

### The 2-Transition Rule

Use at most **2 different transition types** per video. Consistency over variety.

Allowed combinations:
- Cut + cross-dissolve (most common)
- Cut + fade-to-black (energetic with chapter breaks)
- Cross-dissolve + fade-to-black (reflective throughout)

- **DO:** Choose your two transitions before the first render. Apply consistently.
- **DON'T:** Use cut, dissolve, fade-to-black, AND a wipe in the same video. See anti-pattern #26 (Bounce-Swipe Transitions).

### Forbidden Transitions

| Transition | Why forbidden |
|---|---|
| Wipe (any direction) | Corporate slideshow tell. Screams "template." |
| Slide/push | PowerPoint tell. No editorial artifact uses these. |
| Zoom transition | The scene zooms out → next scene zooms in. Gimmick. |
| Page flip/curl | Skeuomorphic kitsch. |
| Morph/shape transition | Motion graphics territory. Not editorial. |
| Star wipe / iris | Self-explanatory. |

---

## 4. Pacing Architecture

How to structure the rhythm of a video. This section describes the default 30 s structure; scale proportionally for 15 s and 60 s.

### The Five-Act Default

```
Opening (3–5 s) → Rising (10–15 s) → Peak (3–5 s) → Falling (5–8 s) → Closing (3–5 s)
```

#### Opening (3–5 s)

The dominant image. Sets emotional tone. Slow camera movement or pull-out.

- Title overlay fades in at 0.3 s, holds for 2 s, fades out at 0.3 s.
- Music begins here — usually a soft intro or ambient bed.
- Movement: slow Ken Burns or pull-out. Never static (the opening needs life).
- One scene. One image. One title.

- **DO:** Full-bleed hero photo with slow 3% pull-out. Title in tracked caps at y=640. Music fades in from silence over 1 s.
- **DON'T:** Open with a stat card. Open with text on a solid background. Open with a rapid montage. The first frame sells or kills the video.

#### Rising (10–15 s)

3–5 scenes at moderate pace. Energy increases scene by scene.

- Scene durations shorten slightly: 3.5 s → 3 s → 2.5 s.
- Camera movements get incrementally faster.
- Transitions: mostly hard cuts. One cross-dissolve allowed for variety.
- Captions appear and disappear cleanly. No lingering.

- **DO:** Three scenes with Ken Burns at increasing zoom percentages: 5%, 7%, 9%. Hard cuts between them.
- **DON'T:** Five scenes at uniform 3 s with identical zoom. The rising section must rise.

#### Peak (3–5 s)

The hero photo. The single strongest image in the set.

- Longest hold: 4–5 s.
- Most dramatic camera movement: push-in at 10–12% zoom.
- Music aligns — a swell, a beat drop, or a key change lands here.
- If there's a pull quote or key caption, it appears here.

- **DO:** Push-in on the best photo. Caption holds for the full duration. Music swells. This is the emotional center of the video.
- **DON'T:** Treat the peak like any other scene. If every scene is a peak, none is. (DP Rule 4: de-emphasise to emphasise.)

#### Falling (5–8 s)

Energy winds down. The viewer exhales.

- Scene durations lengthen: 3 s → 3.5 s → 4 s.
- Camera movements slow. Ken Burns at 3–5%.
- Cross-dissolves replace hard cuts.
- Fewer captions. More breathing room.

- **DO:** Two scenes with slow Ken Burns, connected by a 0.6 s cross-dissolve. Minimal text.
- **DON'T:** Maintain the peak's energy. The falling section earns its name.

#### Closing (3–5 s)

Final image + closing text. The farewell.

- Camera pulls out slowly (pull-out at 3–4%).
- Closing text: edition label in tracked caps ("AUTUMN 2025 — EDITION 04") + one-line closing sentence.
- Music fades out over the last 2 s.
- Final frame holds for 0.5 s of silence before the video ends.

- **DO:** Final image with slow pull-out. Edition label at y=1500. Music fades. 0.5 s of black silence at the end.
- **DON'T:** End on a logo. End with the same energy as the peak. Anti-pattern #34 (End Card With Logo Only).

### Mood Overrides to the Default

The five-act structure is a default, not a straitjacket.

- **Melancholy wraps:** Flatten the arc. No real peak — energy stays low throughout. Longer holds. More fades to black.
- **Upbeat wraps:** Multiple peaks. Shorter falling section. Energy stays high until the closing.
- **Quiet wraps:** Almost no arc. Static holds dominate. The pacing is meditative.
- **Archival wraps:** Uniform moderate pacing with deliberate holds on hero images only. Data-forward.

---

## 5. Mood-to-Motion Mapping

Each mood preset modifies the base motion vocabulary. These are the specific parameters.

### Warm

The default emotional register. Comfortable, present, human.

| Parameter | Value |
|---|---|
| Ken Burns zoom | 5–8% over 3 s |
| Ken Burns speed | Moderate |
| Dominant transition | Cross-dissolve (0.5 s) |
| Secondary transition | Hard cut |
| Scene duration range | 2.5–3.5 s |
| Static holds | 1 in 5 scenes |
| Push-ins | 1 per video |
| Pacing | Standard five-act |

- **DO:** Alternate Ken Burns directions. Use cross-dissolves between thematically linked scenes.
- **DON'T:** Let the warmth become monotonous. Vary within the range.

### Melancholy

Slow, reflective, weighted. Time feels suspended.

| Parameter | Value |
|---|---|
| Ken Burns zoom | 3–5% over 4 s |
| Ken Burns speed | Slow |
| Dominant transition | Cross-dissolve (0.6–0.8 s) |
| Secondary transition | Fade to black (0.3 s + 0.3 s) |
| Scene duration range | 3–4 s |
| Static holds | 1 in 3 scenes |
| Push-ins | 0–1 per video |
| Pacing | Flattened arc — no sharp peak |

- **DO:** Let scenes breathe. Hold the hero photo for a full 4 s with barely perceptible zoom.
- **DON'T:** Add hard cuts. They break the melancholy spell.

### Upbeat

Energetic, forward-moving, celebratory. Shorter scenes, faster cuts.

| Parameter | Value |
|---|---|
| Ken Burns zoom | 8–12% over 2.5 s |
| Ken Burns speed | Fast |
| Dominant transition | Hard cut |
| Secondary transition | Cross-dissolve (0.5 s) — sparingly |
| Scene duration range | 2–3 s |
| Static holds | 0–1 per video (breathing room only) |
| Push-ins | 1–2 per video |
| Pacing | Multiple peaks, short falling section |

- **DO:** Quick cuts between dynamic photos. Let the music drive the rhythm. 2.5 s average scenes.
- **DON'T:** Use cross-dissolves as the dominant transition. They slow the energy. Hard cuts keep pace.

### Golden

Nostalgic, warm-toned, amber. The "looking back through time" register.

| Parameter | Value |
|---|---|
| Ken Burns zoom | 4–7% over 3.5 s |
| Ken Burns speed | Moderate-slow |
| Dominant transition | Cross-dissolve (0.5–0.7 s) |
| Secondary transition | Fade to black (chapter breaks only) |
| Scene duration range | 3–4 s |
| Static holds | 1 in 4 scenes |
| Push-ins | 1 per video (slow, deliberate) |
| Pacing | Standard five-act, extended falling section |

- **DO:** Slow push-ins. Dissolves with warm-toned fades. Linger on the hero.
- **DON'T:** Use hard cuts. They break the nostalgic continuity.

### Quiet

Meditative, almost still. Motion is the exception, not the rule.

| Parameter | Value |
|---|---|
| Ken Burns zoom | 0–3% over 4 s |
| Ken Burns speed | Barely perceptible |
| Dominant transition | Hard cut (clean, no fanfare) |
| Secondary transition | None — cuts only |
| Scene duration range | 3–4 s |
| Static holds | 3 in 5 scenes (dominant) |
| Push-ins | 0 per video |
| Pacing | Flat — minimal arc, meditative |

- **DO:** Hold still. Let the photo speak. Cuts between scenes should feel like turning a page, not a montage.
- **DON'T:** Add motion "to keep it interesting." Stillness IS the aesthetic. See `restrained-modernist` in `styles.md`: "No easing. Cuts only."

---

## 6. Text Animation Rules

Text in Darkroom videos appears and disappears. It does not perform.

### Title Card

- Fade in: 0.3 s (9 frames) opacity ramp from 0 → 1.
- Hold: 2–3 s.
- Fade out: 0.3 s opacity ramp from 1 → 0.

**Remotion implementation:**
```tsx
const titleOp = interpolate(frame, [0, 9], [0, 1], {
  extrapolateRight: "clamp",
  extrapolateLeft: "clamp",
});
// For fade-out (at end of sequence):
const titleFade = interpolate(
  frame,
  [durationInFrames - 9, durationInFrames],
  [1, 0],
  { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
);
// Combined:
const opacity = Math.min(titleOp, titleFade);
```

- **DO:** Fade in, hold, fade out. That's it.
- **DON'T:** Slide the title in from the left. Scale it up from 80% to 100%. Blur-to-sharp. Any entrance beyond opacity is a violation. Anti-pattern #29 (Text Animation as Emphasis).

### Caption Overlay

- Enter: cut in with 0.1 s (3 frames) opacity ramp. Faster than titles — captions are functional, not ceremonial.
- Hold: 2–3 s (must be readable at 12 words/second).
- Exit: cut out with 0.1 s opacity ramp.
- Position: fixed at y=1500 px in 1080x1920 (per `editorial-typographic` in `styles.md`). Never floats.

- **DO:** Caption appears near-instantly, holds, disappears near-instantly. Clean and functional.
- **DON'T:** Animate caption position. Slide it up from below. Reveal it word-by-word.

### Stats / Numbers

- Sequential reveal: one stat at a time.
- Each stat: fade in 0.2 s, hold 1.5 s, fade out 0.2 s.
- 0.1 s gap between stats (or overlap slightly for rhythm).
- Position: centered or flush-left in the stat display area.

- **DO:** "247 photos" fades in, holds 1.5 s, fades out. "12 cities" fades in next.
- **DON'T:** Count up from 0 to 247. Numbers don't animate — they appear.

### Kicker / Label

- Fade in: 0.2 s.
- Hold: 1.5–2.5 s.
- No fade out if the scene cuts away (the cut handles the exit).

### Edition Label (End Card)

- Fade in: 0.3 s.
- Hold: 2–4 s (the closing lingers).
- Tracked caps. Fixed position. No motion.

### Forbidden Text Animations

| Animation | Why forbidden |
|---|---|
| Typewriter / letter-by-letter | Draws attention to the reveal, not the content. Feels "tech demo." |
| Scale-in (grow from small) | DP Rule 10: no decoration. Size change is emphasis — use it as a hierarchy lever, not an animation. |
| Rotate-in | Photos and text are documents. Rotation signals carelessness. |
| Blur-to-sharp | Post-processing effect that screams template. |
| Bounce / spring easing | Overshoot on text is never editorial. Anti-pattern #26. |
| Word-by-word reveal | Karaoke-style. Never. |
| Color shift / pulse | Animated emphasis stacks with size, violating DP Rule 9 (one signal). |
| Parallax text layers | Background text moving at different speeds. Motion-graphic territory. |

**Exception in current Recap.tsx:** The existing `SceneCard` component uses a typewriter effect for the headline (character-by-character reveal with a cursor). This predates this reference and should be migrated to a simple fade-in on the next refactor pass. Flag it but don't break the current build.

---

## 7. Anti-Patterns Expanded

Cross-references `anti_slop.md` entries #25–29 and adds new motion-specific failures.

### From anti_slop.md (canonical)

**#25 — Ken Burns Everywhere.** Same zoom direction on every scene. Same speed. Same duration. The viewer zones out by the third identical pan. Fix: vary direction, speed, and duration per scene. Reserve zoom for the hero image.

**#26 — Bounce-Swipe Transitions.** Any transition that calls attention to itself: bouncy spring, swipe with overshoot, zoom-rotate, page flip. Fix: clean cuts or one consistent crossfade.

**#27 — Lens Flare, Glow, Bloom.** God-ray overlays, headline glow, particle fields, animated bokeh. Fix: trust the photo and the type.

**#28 — Motion-Graphic Background Loop.** Animated particles, floating circles, slow geometric patterns, parallax star fields behind content. Fix: static or near-static backgrounds.

**#29 — Text Animation as Emphasis.** A word pulses in size and colour. Lines enter kinetically, letter-by-letter. Fix: text appears and stays. Italic for emphasis. One signal per shot.

### New motion anti-patterns

**#M1 — Uniform Timing.** Every scene exactly 3 s. Creates a metronome feel — the brain anticipates the cut and disengages. The temporal equivalent of a cramped layout with no white space (DP Rule 5).

Fix: vary scene durations within the mood's range. Hero frames linger. Kicker frames are short. The variation itself carries meaning.

- **DO:** 3.5 s, 2.5 s, 3 s, 4 s, 2.5 s.
- **DON'T:** 3 s, 3 s, 3 s, 3 s, 3 s.

**#M2 — Music-Ignorant Cuts.** Transitions landing between beats. The score and the edit feel unrelated, like two separate tracks layered arbitrarily.

Fix: shift cuts 2–5 frames to align with beat boundaries. At 30 fps and 120 BPM, a beat lands every 15 frames. Small adjustments, large payoff.

- **DO:** Scene cut at frame 450 (beat boundary at 120 BPM) instead of frame 447.
- **DON'T:** Ignore the waveform entirely. If you're muxing a score, respect it.

**#M3 — Lens Flare as Transition.** A light leak or lens flare used to bridge two scenes. Signals "wedding video template" or "stock footage pack."

Fix: cut or dissolve. The transition vocabulary is small on purpose.

- **DO:** Hard cut.
- **DON'T:** White flash. Light leak. Film burn. These are effects, not transitions.

**#M4 — Motion-Graphic Background Loop.** (Extends anti_slop.md #28.) Any animated element behind the content: moving gradients, pulsing shapes, slow-rotating geometry, floating dust particles.

Fix: backgrounds are solid color, or a static photo at reduced opacity. The content moves; the stage does not. Maximum background animation: a 0.5% scale shift over 8 s.

**#M5 — Zoom + Pan Combo.** Applying both zoom and pan to the same scene simultaneously. Creates competing motion vectors that confuse the eye.

Fix: one axis per scene. Zoom OR pan. Never both.

- **DO:** Zoom in slowly on a portrait. Pan slowly across a landscape. Different photos, different movements.
- **DON'T:** Zoom in while panning right on the same photo.

**#M6 — Speed Ramping.** Camera movement that accelerates or decelerates dramatically within a single scene. Common in action/sports editing, wrong for editorial.

Fix: constant speed within each scene. Speed varies between scenes, not within them. Linear interpolation, not eased.

- **DO:** `interpolate(progress, [0, 1], [1.0, 1.08])` — constant rate.
- **DON'T:** Spring easing on Ken Burns. The photo is not a UI element.

**#M7 — Closing Without Deceleration.** The video ends at the same energy it peaked at. No wind-down, no farewell. Feels like the export was truncated.

Fix: the falling section exists for a reason. Slow the camera. Lengthen the holds. Let the music fade. End with 0.5 s of black or a held final frame.

---

## 8. Remotion Implementation Notes

Practical patterns for translating this reference into Remotion code.

### Resolution and Frame Rate

```tsx
// Root.tsx composition config
width: 1080,
height: 1920,  // 9:16
fps: 30,       // Sufficient for photo-based video
```

30 fps is the floor and ceiling. Photo-based video has no motion blur benefit from 60 fps, and the file size doubles.

### Ken Burns via interpolate()

The core pattern for all camera movements on still images.

```tsx
const { durationInFrames } = useVideoConfig();
const frame = useCurrentFrame();
const progress = frame / durationInFrames; // 0 → 1

// Zoom-in (e.g., warm mood, 6% over 3s)
const scale = interpolate(progress, [0, 1], [1.0, 1.06]);

// Direction alternation (even scenes zoom-in, odd scenes zoom-out)
const zoomIn = interpolate(progress, [0, 1], [1.0, 1.06]);
const zoomOut = interpolate(progress, [0, 1], [1.06, 1.0]);
const scale = index % 2 === 0 ? zoomIn : zoomOut;

// Pan (one axis only — horizontal)
const direction = index % 2 === 0 ? 1 : -1;
const tx = interpolate(progress, [0, 1], [0, 20 * direction]);

// Apply to image container:
style={{
  transform: `scale(${scale}) translate(${tx}px, 0)`,
  transformOrigin: "center",
}}
```

**Key constraint:** `interpolate()` is linear by default. Do NOT add easing for Ken Burns. Linear = constant speed = editorial. Eased = accelerating/decelerating = motion graphics.

### Transitions via Series with Overlap

```tsx
import { Series } from "remotion";

// Cross-dissolve between scenes A and B (0.6s overlap = 18 frames)
<Series>
  <Series.Sequence durationInFrames={90}> {/* 3s scene */}
    <SceneCard scene={scenes[0]} fadeOutFrames={18} />
  </Series.Sequence>
  <Series.Sequence durationInFrames={90} offset={-18}>
    <SceneCard scene={scenes[1]} fadeInFrames={18} />
  </Series.Sequence>
</Series>
```

For hard cuts, use `offset={0}` (or omit it). For fade-to-black, insert a black `<Sequence>` of 9–12 frames between scenes.

### Fade-to-Black as a Sequence

```tsx
// Insert between two scenes for a chapter break
<Series.Sequence durationInFrames={18}> {/* 0.6s total */}
  <AbsoluteFill style={{ background: "#000" }} />
</Series.Sequence>
```

Each scene handles its own opacity ramp for the fade edges:

```tsx
// First 9 frames: fade in from black
const fadeIn = interpolate(frame, [0, 9], [0, 1], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});
// Last 9 frames: fade out to black
const fadeOut = interpolate(
  frame,
  [durationInFrames - 9, durationInFrames],
  [1, 0],
  { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
);
const opacity = Math.min(fadeIn, fadeOut);
```

### Variable Scene Durations

Scene durations should be computed per scene, not constant. The COMPOSE stage writes a duration per scene in the render manifest.

```tsx
// Manifest shape (from COMPOSE):
type SceneManifest = {
  image: string;
  caption: string;
  durationSec: number;      // 2.5–4.0
  movement: "zoom-in" | "zoom-out" | "pan-left" | "pan-right" | "static";
  movementPercent: number;   // 3–12 (Ken Burns zoom %)
  transition: "cut" | "dissolve" | "fade-to-black";
};

// Convert to frames:
const durationInFrames = Math.round(scene.durationSec * fps);
```

### Audio Mixing

- Music track: full mix level (0 dB reference).
- TTS narration (if present): music ducks to -6 dB under voice.
- Silence buffer: 0.5 s of silence (or music tail fade) at the end.

In ffmpeg (called in `render_video.py`):

```bash
# Music only (current default):
ffmpeg -y -i silent.mp4 -i score.mp3 -c:v copy -c:a aac -shortest output.mp4

# Music + TTS with ducking:
ffmpeg -y -i silent.mp4 -i score.mp3 -i narration.mp3 \
  -filter_complex "[1:a]volume=0.5[music];[music][2:a]amix=inputs=2:duration=first[out]" \
  -map 0:v -map "[out]" -c:v copy -c:a aac output.mp4
```

The `-6 dB` duck on music (volume=0.5 in linear, roughly -6 dB) keeps narration intelligible without killing the score.

### Scrim for Text Legibility

Every photo scene needs a gradient scrim to guarantee subtitle contrast (WCAG AA 4.5:1 per DP Rule 6).

```tsx
// Bottom gradient scrim (current pattern in Recap.tsx):
<AbsoluteFill
  style={{
    background:
      "linear-gradient(180deg, rgba(14,11,8,0.55) 0%, rgba(14,11,8,0) 25%, rgba(14,11,8,0) 55%, rgba(14,11,8,0.85) 100%)",
  }}
/>
```

This scrim provides 85% opacity at the bottom where captions live and 55% at the top where kickers appear. Never rely on photo brightness for text contrast — scrims are mandatory.

---

## Quick Reference: Timing at a Glance

| Element | Duration | Frames (30fps) |
|---|---|---|
| Scene (shortest) | 2 s | 60 |
| Scene (default) | 3 s | 90 |
| Scene (hero) | 4–5 s | 120–150 |
| Cross-dissolve | 0.5–0.8 s | 15–24 |
| Fade to black (each direction) | 0.3 s | 9 |
| Title fade in/out | 0.3 s | 9 |
| Caption opacity ramp | 0.1 s | 3 |
| Stat hold | 1.5 s | 45 |
| Music fade-out (closing) | 2 s | 60 |
| End silence | 0.5 s | 15 |
| Full video (short) | 15 s | 450 |
| Full video (medium) | 30 s | 900 |
| Full video (long) | 60 s | 1800 |
