---
name: darkroom-schedule
description: Register a Hermes NL cron job for automatic wraps at whatever cadence the user wants
args:
  - name: cadence
    description: "Natural language or cron expression for the schedule"
    required: true
user-invocable: true
---

## MANDATORY PREPARATION

Verify the agent is running on Hermes. If not, inform the user: "Cron scheduling requires Hermes. Run `/darkroom wrap` manually instead." Exit.

---

## Assess

The user picks their own rhythm — daily, weekly, monthly, per-trip, seasonal, yearly, or anything in between. Parse the cadence argument. Accept either:

- **Natural language:** "every Sunday evening", "first of the month", "every two weeks on Friday", "daily at 9pm"
- **Cron expression:** `0 9 1 * *` (9 AM on the 1st of every month)

Resolve to a Hermes NL cron specification.

## Execute

1. **Register** the cron job via Hermes cron API. The job runs `/darkroom wrap` with the user's current taste profile defaults (no flag overrides — the taste file provides everything).
2. **Confirm** — Show the user the resolved schedule in plain English and the next three run dates.

## Examples

| User input | Resolved schedule | Next run |
|------------|-------------------|----------|
| `"every Sunday evening"` | Sunday 21:00 local | May 4 |
| `"first of the month"` | 1st of each month, 09:00 local | Jun 1 |
| `"every two weeks on Friday"` | Biweekly Friday, 09:00 local | May 16 |
| `"daily at 9pm"` | Every day, 21:00 local | tonight |
| `"0 9 1 * *"` | 1st of each month, 09:00 UTC | Jun 1 |

## Cancel

To cancel a scheduled wrap, the user runs `/darkroom schedule cancel`. List active cron jobs and confirm which to remove.
