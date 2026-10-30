# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-10-30. **Owner of this file:** the reviewer. The running session only *reads* it, except for the
Status line.

**Previous task — open-problem ANGLES report: DONE at `f30a3be`**
([`results/OPEN_PROBLEM/ANGLES_REPORT.md`](results/OPEN_PROBLEM/ANGLES_REPORT.md)). The ranked plan that came out of it is
[`briefs/NEXT_EXPERIMENTS/README.md`](briefs/NEXT_EXPERIMENTS/README.md); this task is its item 1.

## Do these steps, in order

1. `git pull` on `main`.
2. Open [`briefs/X7/README.md`](briefs/X7/README.md) and follow its START HERE box. **First stage only:** the profile
   (`results/X/X7_profile.md`, brief §3) and the pre-registration (`results/X/X7_preregistration.md`, brief §4 with every
   threshold filled in), then STOP.
3. Commit both with "before observer code" in the commit message. **Write no model, observer or scoring code.**
4. Set the Status line below to `AWAITING APPROVAL <commit-hash>`, push, and stop. The reviewer approves (or sends
   changes) by editing the brief's START HERE box, as was done for X6.

## Rules that always apply
- Pre-register before analysis code. Never move a threshold after seeing results. Number every deviation.
- Tag every number MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED.
- No kWh, cost, range or regulatory claims from a replay without saying they are modelled. Carry each dataset's
  licence and caveats onto every verdict (X7: McMaster CC BY 4.0; surface thermistors; spatial margin, not core).
- Reuse the McMaster loader and per-cell R identification in `analysis/X2_replay.py`; do not re-derive R.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `AWAITING APPROVAL <commit-hash>` or `BLOCKED: <one-line reason>`, then commit
and push.

**Status:** AWAITING APPROVAL 8a468ad
