# ▶ NEXT TASK — read this first, then do it. No other prompt is needed.

**Updated:** 2026-10-30 · **Owner of this file:** the reviewer. The running session only *reads* it.

## Do these steps, in order

1. `git pull` on `main`.
2. **Housekeeping (X5, closed).** In `results/X/X5/results_X5.md`, replace every `bd7a2af` with `624e4ee` (the real
   D-1/D-2 commit). Commit: `X5: fix D-1/D-2 commit reference (bd7a2af -> 624e4ee)`. No other X5 edits.
3. **Start X6.** Open [`briefs/X6/README.md`](briefs/X6/README.md) and follow its START HERE box:
   - read the brief, then `results/X/X5/results_X5.md`;
   - do **§3 only** (knee definition and profile);
   - write `results/X/X6_profile.md` and `results/X/X6_preregistration.md`;
   - commit both with a message containing **"before forecasting code"**.
4. **Stop and push.** Do **not** write `analysis/X6_forecast.py` or run any forecast. Wait for the reviewer, who will
   replace this file with the next task.

## Rules that always apply
- Pre-register before analysis code; never move a threshold after seeing results; number every deviation.
- Tag every number MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED.
- No kWh, cost, range or regulatory claims. Carry each dataset's licence and caveats onto every verdict.
- Do not start any experiment that this file does not name.

## When you finish
Edit only the **Status** line below to `DONE <commit-hash>` (or `BLOCKED: <one-line reason>`), commit, and push.

**Status:** DONE 2188950 (X5 hash fix 78d5956; X6 profile + pre-registration 2188950, before forecasting code; stopped for review)
