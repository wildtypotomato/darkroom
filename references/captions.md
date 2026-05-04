# Caption Writing Guide — Darkroom NARRATE Stage

Reference for the captioning agent. Loaded as context during NARRATE. Every rule has a concrete example. Cross-references point to `design-philosophy.md` (DP), `anti_slop.md` (AS), and `styles.md` (ST) within this `references/` directory.

---

## 1. Caption Voice Spectrum

Five voices across two modes. The voice is set by `--mode` and optionally refined by the mood detected during CLUSTER.

### Memorial Mode Voices

Used when `--mode=memorial`. Warm, reflective, intimate. The user is revisiting their own life.

#### Voice A — Intimate Present

Speaks as if the moment is still happening. Present tense. Sensory. Close.

> **Photo:** Three friends at a dinner table, candles lit, plates mostly empty.
>
> "The candles have burned past the label. Nobody has checked the time in two hours."

#### Voice B — Reflective Past

Speaks from a distance. Past tense. Warm but not sentimental. The narrator remembers clearly.

> **Same photo:**
>
> "They stayed until the restaurant turned the lights up. The conversation had outlasted the food by an hour."

#### Voice C — Wry Observer

Speaks with understated humour. Affectionate but dry. Notices the small absurdity.

> **Same photo:**
>
> "Three adults who swore they'd leave by ten, photographed at midnight with empty bottles and no regrets."

### Archival Mode Voices

Used when `--mode=archival`. Factual, contextual, restrained. The user is curating a record.

#### Voice D — Documentary

Names, dates, places, facts. No emotion. The caption is a record.

> **Same photo:**
>
> "Dinner at Chez Maman, Wan Chai. 14 November 2025. L–R: Amy Cheung, Mark Lai, David Ho."

#### Voice E — Contextual

Facts with one sentence of context that extends the record. Still restrained — no warmth, just information that the image alone cannot supply.

> **Same photo:**
>
> "Monthly dinner, fourteenth consecutive. The restaurant changed ownership in September; they kept the reservation anyway."

---

### Voice Examples — Travel Landscape

> **Photo:** Mountain road at dawn, fog in the valley, motorcycle parked at a viewpoint.

| Voice | Caption |
|-------|---------|
| **A — Intimate Present** | "The fog sits in the valley like water in a bowl. The engine ticks as it cools." |
| **B — Reflective Past** | "He pulled over because the fog had filled the valley and the light was doing something he knew wouldn't last." |
| **C — Wry Observer** | "Stopped for the view. Stayed for twenty minutes. Arrived late to everything after." |
| **D — Documentary** | "Route 108, Doi Inthanon. 6:47 AM, 3 December 2025. Elevation 2,120 m." |
| **E — Contextual** | "Morning ascent of Doi Inthanon, the highest point in Thailand. The fog clears by eight; arriving before seven is the only way to see this." |

### Voice Examples — Pet

> **Photo:** A cat asleep inside an open suitcase, clothes pushed aside.

| Voice | Caption |
|-------|---------|
| **A — Intimate Present** | "She's claimed the suitcase again. The packing will have to wait." |
| **B — Reflective Past** | "Every trip started this way — ten minutes of negotiating a cat out of a suitcase." |
| **C — Wry Observer** | "Mochi has opinions about the trip. She's voting no." |
| **D — Documentary** | "Mochi, domestic shorthair, age 4. Photographed during packing, October 2025." |
| **E — Contextual** | "A recurring pattern across twelve trip preparations. The suitcase was never packed without intervention." |

---

## 2. Sentence-Level Craft Rules

Drawn from Editorial Design (Caldwell & Zappaterra), Thinking with Type (Lupton), and the universal rules in `design-philosophy.md`.

### 2.1 Full sentences, never labels or fragments

A caption is a complete thought with a subject and verb. Not a noun phrase. Not a date stamp alone. Not a hashtag.

**BAD:** "Beach sunset."
**BAD:** "Tokyo, 2025."
**BAD:** "The gang."
**GOOD:** "The tide pulled out far enough to reach the sandbar — first time in three years."
**GOOD:** "Shinjuku station at rush hour, moving the way water moves through a bottleneck."

Fragment date stamps belong in the small-caps tag above the caption (e.g. `OCTOBER 2025`), not in the caption body itself. See DP Rule 8, AS #21.

### 2.2 Independently meaningful

The caption must make sense if you cover the image with your hand. If it requires the image to parse, it has failed.

**BAD:** "This was such a great day."
**BAD:** "Look at that view!"
**GOOD:** "Thirty-two degrees and no shade for a kilometre — but the water at the end was cold enough to make the walk worth it."

The reader should learn something from the caption that the image alone does not tell them: weather, temperature, duration, a name, a fact, a feeling that isn't visible.

### 2.3 Extend the story, never describe the obvious

If the image shows a sunset, the caption must not say "a sunset." Name what the image cannot show: the temperature, who was there, what happened next, why it mattered.

**BAD:** "A beautiful sunset over the ocean."
**GOOD:** "Last light before the ferry. They had twenty minutes to make the dock."

See AS #21 (Museum Label), AS #22 (Generic AI Caption).

### 2.4 No first person

Darkroom captions use second person ("you") or third person. First person ("I went to...") breaks the editorial voice and reads as diary entry, not designed artifact.

**BAD:** "I loved this place so much."
**BAD:** "We had the best time here."
**GOOD:** "The kind of courtyard you find by accident and return to on purpose."
**GOOD:** "They ordered everything on the left side of the menu and regretted nothing."

Exception: a direct quote pulled from a voice memo may use first person if attributed. Set in italics with attribution.

### 2.5 One caption, one thought

No compound sentences joined by semicolons. No "and then... and then." Each caption carries a single observation, fact, or moment.

**BAD:** "The market opened at dawn; they arrived early and bought mangoes; the light was golden."
**GOOD:** "The market opened at dawn. They were the only ones not selling something."

If there are three things to say, write three captions for three images — or pick the strongest one.

### 2.6 Vary sentence structure

Do not start every caption with a noun or "The." Mix openings: prepositional phrases, temporal markers, verb-first, conditional, inverted.

**Monotonous:**
- "The river was frozen."
- "The bridge was empty."
- "The light was blue."

**Varied:**
- "By January the river had frozen solid enough to walk on."
- "Not a single person on the bridge — unusual for a Saturday."
- "Blue light, the kind that only lasts ten minutes before it turns grey."

### 2.7 Concrete over abstract

Name the specific. Not "beautiful" — what kind of beautiful? Not "amazing food" — what dish? Not "great weather" — what temperature, what sky?

**BAD:** "An amazing meal at a wonderful restaurant."
**GOOD:** "Grilled octopus and a carafe of white at a table they set up on the pavement because the inside was full."

**BAD:** "Beautiful autumn colours."
**GOOD:** "The ginkgo trees on Meiji-dori had turned overnight. Yellow everywhere, ankle-deep on the pavement."

### 2.8 Active verbs over state verbs

Prefer verbs that move ("pulled," "carried," "climbed," "turned") over verbs that sit ("was," "is," "had," "seemed").

**BAD:** "The street was busy."
**GOOD:** "Taxis jammed the street from the station to the harbour."

**BAD:** "The children were happy."
**GOOD:** "The youngest ran straight into the wave and came up laughing."

---

## 3. Anti-Patterns — Caption Failures

Expands AS #21–24 with additional named failures and more examples.

### 3.1 Museum Label

Restates what the image shows without adding anything.

**BAD:** "A photograph of a sunset over the ocean."
**BAD:** "Group photo at the restaurant."
**BAD:** "Birthday cake with candles."
**BAD:** "Mountain landscape with clouds."

**Why it fails:** The viewer can see the image. A label tells them nothing new. It is the absence of caption craft. (DP Rule 8, AS #21, Editorial Design Rule 4.)

**Fix:** Name what the image cannot show — the time, the temperature, the name, the story behind the moment.

**GOOD (memorial):** "Thirty-one candles, and the wish was the same as last year."
**GOOD (archival):** "Birthday dinner, 8 October 2025. The cake was from Holborn Dining Room; the candles from a corner shop that was already closing."

### 3.2 Generic AI

Uses placeholder language that could apply to any image. The hallmark of LLM default output.

**BAD:** "A beautiful moment captured in time."
**BAD:** "This stunning capture showcases the vibrant colors of autumn."
**BAD:** "Memories that will last forever."
**BAD:** "A perfect day spent with loved ones."
**BAD:** "Nature at its finest."

**Why it fails:** These phrases carry zero information. They are semantic nulls — the textual equivalent of a gradient background. A reader learns nothing; a designer cringes. (AS #22, Vignelli p. 10: every element must carry meaning.)

**Fix:** Delete the entire caption and start over. Ask: what is the one concrete detail the image cannot convey? Write that.

**GOOD:** "The maple turned a week early. The photograph catches the moment between colour and ground."

### 3.3 Echo

Caption repeats the headline or section title.

**BAD:**
> Headline: "Summer in Lisbon"
> Caption: "Our summer in Lisbon"

**Why it fails:** The caption has surrendered its real estate. It extends nothing, reveals nothing, adds nothing. (AS #24, Editorial Design Rule 4.)

**Fix:** The caption tells the reader something the headline does not — a date, a neighbourhood, a sensory detail, a fact.

**GOOD:**
> Headline: "Summer in Lisbon"
> Caption: "Alfama after the rain. The tiles reflected everything, even the laundry."

### 3.4 Distant

Uses third person about the user's own life as if narrating a stranger's behaviour. Clinical, anthropological, alienating.

**BAD:** "The subject appears to be enjoying a meal with friends."
**BAD:** "A group of individuals gathered around a dining table."
**BAD:** "The person in the foreground seems to be looking at the camera."

**Why it fails:** This is the voice of a surveillance camera, not a personal archive. The user sent their own photos. Writing about them as "the subject" is hostile distance.

**Fix:** Use "you" (second person) for memorial mode, or name people directly. For archival mode, use names or roles ("the eldest," "the host"), never "the subject."

**GOOD (memorial):** "You always sit in the same chair — back to the wall, facing the door."
**GOOD (archival):** "Amy Cheung, seated left. She ordered for the table without asking, as usual."

### 3.5 Emotive Overload

Piles on adjectives and emotional language until the caption collapses under its own weight.

**BAD:** "An absolutely breathtaking, soul-stirring moment of pure joy and boundless happiness."
**BAD:** "The most incredibly beautiful and awe-inspiring sunset anyone has ever witnessed."
**BAD:** "A deeply moving, profoundly touching scene that speaks volumes about the human spirit."

**Why it fails:** Emotion is the reader's job. The caption's job is to supply the concrete detail that lets the reader feel something on their own. Every adjective you add is one the reader can't supply. (Vignelli p. 72: "In a world where everybody screams, silence is noticeable.")

**Fix:** Remove every adjective. Write the fact. Trust the photo to carry the feeling.

**GOOD:** "She didn't say anything. She just held the letter and sat down."

### 3.6 The Cliche Machine

Relies on stock phrases that have been emptied of meaning through overuse.

**BAD:** "Making memories."
**BAD:** "Living our best life."
**BAD:** "Wanderlust vibes."
**BAD:** "Squad goals."
**BAD:** "It's the journey, not the destination."

**Why it fails:** Cliches are borrowed language. They signal that nobody bothered to look at the actual image and write something specific to it.

**Fix:** Describe what is literally happening, in concrete terms. The specificity is the voice.

**GOOD:** "Four hours on a bus with no air conditioning, and she's still smiling — which tells you everything about the waterfall at the end."

### 3.7 The Narrator Intrusion

The caption draws attention to the act of captioning, photographing, or designing.

**BAD:** "This image perfectly captures the essence of the evening."
**BAD:** "No caption could do justice to this moment."
**BAD:** "Words can't describe how beautiful this was."

**Why it fails:** The caption has become self-referential. It is talking about itself instead of doing its job. If words can't describe it, don't use words — let the image stand alone with a date tag.

**Fix:** Write about the subject, not about the act of writing.

**GOOD:** "The last light hit the water at the angle that turns everything gold. Five minutes later it was gone."

---

## 4. Worked Examples — Before/After

Eight scenarios. Each shows a BAD caption, a GOOD memorial-mode caption, and a GOOD archival-mode caption.

### 4.1 Group Dinner Photo

> **Image:** Six people around a round table. Chinese restaurant. Lazy susan with half-eaten dishes. Someone mid-laugh.

**BAD:** "A wonderful dinner with amazing friends. So blessed!"

**GOOD (memorial — Voice A):** "The lazy susan hasn't stopped spinning all night. Someone keeps ordering more than the table can hold."

**GOOD (archival — Voice E):** "Monthly dinner at Fook Lam Moon, Wan Chai. Sixth consecutive. The group has grown from four to six since March."

### 4.2 Landscape / Travel

> **Image:** Terraced rice fields in morning light. Fog in the lower terraces. A single farmer visible in the middle distance.

**BAD:** "Stunning rice terraces. Nature is truly amazing. #wanderlust"

**GOOD (memorial — Voice B):** "The farmer was already working when the fog was still waist-high. The light had about ten minutes left before it flattened."

**GOOD (archival — Voice D):** "Tegallalang rice terraces, Bali. 7:12 AM, 19 August 2025. Subak irrigation system, UNESCO-listed since 2012."

### 4.3 Pet Photo

> **Image:** Golden retriever asleep on a couch, one ear flipped inside out, a chewed toy beside its paw.

**BAD:** "The cutest doggo ever!! We don't deserve dogs."

**GOOD (memorial — Voice C):** "Bean has destroyed every toy in the house except this one. Nobody knows why it survived."

**GOOD (archival — Voice E):** "Bean, golden retriever, 3 years. The toy is the last of a set of six purchased in January. Lifespan of the others: two to eleven days."

### 4.4 Screenshot / Meme

> **Image:** Screenshot of a WhatsApp conversation — someone sent a photo of a parking ticket with a laughing emoji, reply says "worth it."

**BAD:** "Hilarious text exchange lol."

**GOOD (memorial — Voice C):** "The parking ticket cost more than the lunch. Both agreed the lunch was better value."

**GOOD (archival — Voice E):** "WhatsApp exchange, 3 March 2025. Parking fine: HK$320. The car was parked on Elgin Street for ninety minutes during a dim sum lunch at Tim Ho Wan."

Note: Screenshots and memes require the archival voice to name the platform, date, and context that the screenshot alone doesn't always carry (app name, conversation participants if relevant, what prompted the exchange). See ST `functional-minimalism` voice: "Information, not feeling."

### 4.5 Wedding / Ceremony

> **Image:** Couple exchanging rings. Outdoor ceremony. Afternoon sun through trees.

**BAD:** "The most magical, beautiful, perfect day of their lives."

**GOOD (memorial — Voice A):** "His hands are shaking. Hers are steady. She's been ready for this part."

**GOOD (archival — Voice D):** "Ring exchange, 2:47 PM. Ceremony at Repulse Bay Garden. Officiant: Rev. Catherine Yeung."

### 4.6 Food Photo

> **Image:** Close-up of a bowl of ramen. Steam visible. Chopsticks resting across the rim.

**BAD:** "Delicious ramen! So yummy!"

**GOOD (memorial — Voice A):** "Still too hot to eat. The steam fogs the glasses every time."

**GOOD (archival — Voice E):** "Tonkotsu ramen at Fuunji, Shinjuku. The tsukemen version has a twenty-minute queue; the regular does not."

### 4.7 Childhood / Family

> **Image:** A toddler standing in rain boots in a puddle, arms out, face up to the rain.

**BAD:** "Precious little angel enjoying the rain! So adorable!"

**GOOD (memorial — Voice B):** "She stood in that puddle for fifteen minutes. The boots were new; ruining them was the point."

**GOOD (archival — Voice D):** "Mei, age 2. Victoria Park, 11 October 2025. Rainfall that afternoon: 28 mm."

### 4.8 Cityscape / Architecture

> **Image:** Hong Kong skyline at blue hour, shot from the Star Ferry.

**BAD:** "The stunning Hong Kong skyline at night. What a view!"

**GOOD (memorial — Voice B):** "The crossing takes seven minutes. Long enough to watch the buildings trade daylight for electricity."

**GOOD (archival — Voice E):** "Victoria Harbour from the Star Ferry, Tsim Sha Tsui to Central. Blue hour, 6:38 PM. The ICC tower had not yet switched to its evening light pattern."

---

## 5. Caption Length Guidelines

Three contexts, three budgets. Enforce strictly — overlong captions break layout and readability.

### 5.1 PDF Poster Caption

**Budget:** 15–30 words.

Space is the constraint. The caption shares a narrow column with the image. At 7.5/9.5 pt italic (per DP Rule 8 and ST `editorial-typographic` specs), 30 words fills approximately 3 lines on a 55 mm column. More than that and the caption competes with the image for dominance.

**Too short (9 words):** "They stayed late. The candles burned down."
Reads as a fragment at poster scale. Needs one more beat.

**Right length (22 words):** "They stayed until the restaurant turned the lights up. The conversation had outlasted the food by an hour."

**Too long (41 words):** "They stayed at the restaurant until well past midnight, long after the food was finished, talking about everything and nothing, while the candles burned down to stubs and the waiters started stacking chairs around them."
Will not fit the column. Cut to the strongest clause.

### 5.2 Video Caption Overlay

**Budget:** 8–15 words.

Must be readable in 2–3 seconds at 36 pt on a 1080-wide frame. The average reader processes 3–4 words per second on screen. More than 15 words and the frame either lingers too long or the reader can't finish.

**Too short (4 words):** "The candles burned down."
Feels orphaned on a video frame. Pair with a longer hold or a second card.

**Right length (11 words):** "Nobody checked the time. The candles had burned past the label."

**Too long (19 words):** "The candles had burned all the way past the label and nobody at the table had bothered to check the time."
Reader cannot finish in 3 seconds. Split into two cards or cut.

### 5.3 Full Narrative Caption (Intro / Closing)

**Budget:** 30–60 words.

Used for the opening frame and closing frame of the video, and for the poster's introductory paragraph. This is the only context where the caption can breathe. Still one thought — but it can develop the thought across two or three sentences.

**Right length (47 words):** "October started cold and stayed cold. The photos are mostly indoors — kitchens, restaurants, the living room with the heater on. But the last week opened up. Three days of sun, and everyone went outside as if they'd been released from something."

**Too long (72 words):** Cut. If it doesn't fit 60 words, it has two thoughts in it. Split them.

---

## 6. Mood-to-Voice Mapping

The CLUSTER stage detects an overall mood from the media. That mood inflects how every caption is written, regardless of which voice (A–E) is active. Think of mood as the colour temperature of the voice — it doesn't change what the voice says, but how it says it.

Mood vocabulary is drawn from the user's `DARKROOM_TASTE.md` field `mood_vocabulary`. These five are the defaults.

### Warm

Present tense. Active verbs. Sensory details — temperature, texture, smell, sound. The reader should feel physically present.

**Voice B + Warm mood:**
"The kitchen smelled like garlic and sesame oil. Someone had opened the window, and the curtain moved in a way that meant autumn."

**Voice D + Warm mood:**
"Dinner preparation, 6:30 PM. Kitchen window open. Temperature outside: 18 degrees, dropping."

Even the documentary voice picks up warmth — it selects warmer facts (temperature, sensory conditions) rather than cold data (addresses, full names).

### Melancholy

Past tense. Reflective. Longer rhythm — the sentences slow down. Subordinate clauses are permitted. The reader should feel the weight of time passing.

**Voice A + Melancholy mood:**
"The chair where she always sat is still turned toward the window."

**Voice E + Melancholy mood:**
"Last visit to the flat before the lease ended. The furniture had already been collected; only the marks on the wall remained."

Handle with care. Melancholy must never tip into sentimentality. If you find yourself writing "bittersweet" or "poignant," delete the sentence and write a concrete image instead.

### Upbeat

Short sentences. Punchy. Present tense. An exclamation is permitted — one per entire wrap, maximum, and only in Voice C (Wry Observer). Energy comes from rhythm, not from adjectives.

**Voice A + Upbeat mood:**
"The queue was forty minutes. The rollercoaster was ninety seconds. They went twice."

**Voice C + Upbeat mood:**
"Four adults on a trampoline. Nobody got hurt. This time."

### Golden

Warm but restrained. Nostalgic without sentimentality. The golden hour of emotions — things are good, and you know they won't last, but you don't say that out loud.

**Voice B + Golden mood:**
"The last Sunday before school started. They spent it doing nothing in particular, which was exactly the point."

**Voice D + Golden mood:**
"Final weekend of summer break, 31 August 2025. No scheduled activities. Fifteen photos taken; twelve of them outdoors."

The golden mood is the most dangerous — it borders on sentimentality. Test every caption: if you removed the mood and the caption still works as a factual statement, it passes. If it only works with the emotional framing, rewrite.

### Quiet

Minimal. Observational. Almost haiku-like. Short sentences or fragments (the only mood where a fragment is permitted, if it reads as deliberate compression rather than laziness). The reader should feel stillness.

**Voice A + Quiet mood:**
"Rain on the window. No one talking."

**Voice B + Quiet mood:**
"The house was empty by noon. The light stayed."

**Voice D + Quiet mood:**
"Apartment interior. 2 PM. No occupants."

Quiet captions are the shortest. In video, pair them with the longest holds — the silence of the caption matches the stillness of the frame. See ST `editorial-grid-authority` motion guidance: "the hold *is* the emphasis."

---

## 7. Format Rules

### Date Tags

Always precede a caption with a small-caps date tag on the PDF poster. Format: `MONTH YEAR` or `DAY MONTH YEAR` for archival mode.

```
OCTOBER 2025
They stayed until the restaurant turned the lights up.
```

In video, the date tag is a separate text element at the chapter label position (top 80 px), not part of the caption overlay.

### Attribution for Quotes

If a voice memo or message is quoted, use italics with a dash attribution:

```
*"I think this might be the best meal I've ever had."*
— Amy, 14 November 2025
```

Quotes in memorial mode use Voice A or B framing. Quotes in archival mode include full name and date.

### Caption Numbering

Do not number captions visually. Internally, the NARRATE agent assigns each caption an ID (`c-001`, `c-002`, ...) for the COMPOSE manifest. This ID never appears in the rendered output.

### Fallback

If the captioning agent cannot identify enough concrete detail to write a meaningful caption (blurry image, no EXIF, no context from memory), write a minimal honest caption rather than inventing detail:

**GOOD fallback:** "Somewhere in autumn. The rest of the details have gone."

Never fabricate names, dates, locations, or details that aren't supported by the image, EXIF data, or cross-session memory. Honest gaps are better than confident lies.

---

## 8. CRITIQUE Checklist for Captions

The CRITIQUE stage checks every caption against this list. Any failure triggers a re-NARRATE for that caption.

| # | Check | Fail condition |
|---|-------|---------------|
| 1 | Full sentence | Caption is a fragment, label, or noun phrase |
| 2 | Independently meaningful | Caption requires the image to parse |
| 3 | No obvious description | Caption describes what the image already shows |
| 4 | No first person | Caption uses "I" or "we" (unless attributed quote) |
| 5 | Single thought | Caption contains semicolons joining multiple ideas |
| 6 | Concrete detail | Caption contains no specific names, dates, places, or sensory details |
| 7 | No generic AI phrases | Caption matches any phrase in AS #22 |
| 8 | No echo | Caption repeats the headline or section title (AS #24) |
| 9 | No distant voice | Caption refers to the user as "the subject" or "the individual" |
| 10 | No emotive overload | Caption stacks three or more adjectives before a noun |
| 11 | No cliches | Caption uses stock phrases ("making memories," "best life," etc.) |
| 12 | Length in budget | PDF: 15–30 words. Video: 8–15 words. Narrative: 30–60 words |
| 13 | Mood-consistent | Caption tense and rhythm match the detected mood |
| 14 | Voice-consistent | Caption matches the selected voice (A–E) across all captions in the wrap |
| 15 | No fabrication | Caption asserts a fact not supported by EXIF, memory, or image content |

Two or more fails on the same caption = reject and re-NARRATE. One fail = WARN and flag for human review if time allows.

---

## Cross-References

| Reference | Relevant sections |
|-----------|------------------|
| `design-philosophy.md` Rule 8 | Captions are sentences, not labels — the foundational rule |
| `anti_slop.md` #21 | Museum Label |
| `anti_slop.md` #22 | Generic AI Caption |
| `anti_slop.md` #23 | Caption Far From Image (layout, not writing — but affects how much space the caption gets) |
| `anti_slop.md` #24 | Caption Echoing the Headline |
| `styles.md` — each preset's "Voice / caption tone" | Voice calibration per style: restrained-modernist is anti-rhetorical; functional-minimalism is utilitarian; editorial-grid-authority is narrative; editorial-typographic is editorial-declarative |
| Editorial Design (Caldwell & Zappaterra) Rule 4 | "Captions extend the story... deserve craft, voice, and completeness" |
| Thinking with Type (Lupton) p. 130 | "Captions are the most-read text on a magazine page" |
| Thinking with Type (Lupton) Rule 12 | Captions close to image, editorially written |
