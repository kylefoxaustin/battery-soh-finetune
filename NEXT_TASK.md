# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-10-30. **Owner of this file:** the reviewer. The running session only *reads* it, except for the
Status line.

## Do these steps, in order

1. `git pull` on `main`.
2. Read [`briefs/X6/REVIEW_DECISION.md`](briefs/X6/REVIEW_DECISION.md). **X6 is approved** as pre-registered
   (`2188950`), with the reported additions R-1 and R-2.
3. Commit R-1 and R-2 as deviations **D-1 and D-2** in `results/X/X6_preregistration.md`, **before forecasting
   code**. The commit message must contain "before forecasting code".
4. Write and run `analysis/X6_forecast.py` exactly as pre-registered, plus R-1 and R-2.
5. Commit `results/X/X6/results_X6.md` (verdict first, with the coupling caveat and licence), `x6.json`, the plots,
   and the `results/X/README.md` and `results/RESEARCH_DOSSIER.md` updates.
6. **Stop and push.** Do not start any other experiment.

## Rules that always apply
- Pre-register before analysis code. Never move a threshold after seeing results. Number every deviation.
- Tag every number MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED.
- No kWh, cost, range or regulatory claims. Carry each dataset's licence and caveats onto every verdict.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `DONE <commit-hash>` or `BLOCKED: <one-line reason>`, then commit and push.

**Status:** OPEN
