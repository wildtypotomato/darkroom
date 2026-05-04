---
name: darkroom-reset
description: Clear DARKROOM_TASTE.md and start fresh
user-invocable: true
---

## Execute

1. **Confirm** — Ask the user: "This will clear your taste profile. Next `/darkroom wrap` will use defaults. Proceed?"
2. **If yes:** Call `darkroom.src.taste.clear_taste()` to delete `DARKROOM_TASTE.md`.
3. **Confirm deletion** — "Taste profile cleared. Run `/darkroom teach` to set up a new one, or `/darkroom wrap` will use the `editorial-grid-authority` preset with neutral voice."
4. **If no:** Exit without changes.
