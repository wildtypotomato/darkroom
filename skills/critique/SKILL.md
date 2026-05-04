---
name: darkroom-critique
description: Standalone anti-slop evaluation of a rendered PDF or MP4
args:
  - name: artifact-path
    description: Path to the PDF or MP4 file to evaluate
    required: true
user-invocable: true
---

## MANDATORY PREPARATION

Load the evaluation rubric from `references/anti_slop.md` (34 named anti-patterns) and `references/design-philosophy.md` (10 universal rules). Both must be in context before scoring.

---

## Assess

Determine artifact type from file extension:

| Extension | Type | Evaluation method |
|-----------|------|-------------------|
| `.pdf` | PDF poster | Full-page screenshot via Playwright |
| `.mp4` | Video | Sample 5 evenly-spaced frames via ffmpeg |

If the extension is unrecognised, reject with: "CRITIQUE only evaluates PDF and MP4 artifacts."

## Plan

The evaluation runs three passes against each screenshot or frame:

1. **Anti-slop scan** — Match against every entry in `references/anti_slop.md`. Each match logged with the entry's name, severity, and "What to do instead" corrective.
2. **Design-philosophy check** — Verify compliance with the 10 rules in `references/design-philosophy.md`. Focus on hierarchy, white space, type discipline, and grid adherence.
3. **Caption audit** — For any visible text: does it name specifics (place, weather, detail), or fall into the "beautiful moment captured in time" void? Captions that cannot stand alone without the image are failures.

## Execute

Call the appropriate critique function:

- **PDF:** `darkroom.src.critique.critique_pdf(artifact_path)` — screenshots the full page, runs vision analysis, returns `CritiqueResult`.
- **MP4:** `darkroom.src.critique.critique_video(artifact_path)` — extracts 5 frames, runs vision analysis on each, aggregates into `CritiqueResult`.

The `CritiqueResult` contains:
- `verdict`: PASS | WARN | FAIL
- `issues`: list of `{pattern_name, severity, location, corrective}`
- `score`: 0–100 composite

## Report

Format the `CritiqueResult` as a human-readable report:

```
VERDICT: [PASS | WARN | FAIL]
SCORE:   [0–100]

CRITICAL (must fix)
  - [pattern_name]: [description]. Fix: [corrective].

WARNING (cosmetic)
  - [pattern_name]: [description]. Fix: [corrective].

PASSED CHECKS
  - [count] / 34 anti-patterns clear
  - [count] / 10 design rules satisfied

CAPTION AUDIT
  - [pass/fail per visible caption with reason]
```

If the verdict is FAIL and this critique was invoked as part of `/darkroom wrap`'s Generator–Critic Loop, the correctives feed back into COMPOSE → RENDER automatically. If invoked standalone, the report is delivered to the user as-is.
