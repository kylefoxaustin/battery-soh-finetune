# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-10-31. **Owner of this file:** the reviewer. The running session only *reads* it, except for the
Status line.

**Previous task — B1: DONE at `0c4b61e`, reviewed and accepted** ([`results/B1/results_B1.md`](results/B1/results_B1.md);
the reviewer re-derived rates, depths, dump gates and RT ratios from `results/B1/raw/` and they match). Plan:
[`briefs/NEXT_EXPERIMENTS/README.md`](briefs/NEXT_EXPERIMENTS/README.md) (order now DC1 → FR1 → X8 → O1 → R1; FR1 may
run in a parallel session from its own brief and never touches this file).

## Do these steps, in order

1. `git pull` on `main`.
2. Open [`briefs/DC1/README.md`](briefs/DC1/README.md) and follow its START HERE box. **First stage only:** download the
   primary dataset, record its licence verbatim, write `results/DC1/DC1_profile.md` (brief §3) and
   `results/DC1/DC1_preregistration.md` (brief §4 with every threshold filled in), then STOP.
3. Commit both with "before controller code" in the commit message. **Write no controller, predictor or scoring code.**
   A loader and the profile statistics are allowed.
4. Set the Status line below to `AWAITING APPROVAL <commit-hash>`, push, and stop. The reviewer approves by editing the
   brief's START HERE box.

## Rules that always apply
- Pre-register before analysis code. Never move a threshold after seeing results. Number every deviation.
- Tag every number MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED. DC1's outputs are DERIVED from SOURCED traces under
  ASSUMED specs; say so on every table.
- Use only the measured node/job profiles; the dataset's modelled whole-facility profiles are not data for this task.
- The unit of analysis is one multi-node job's total power, never a sum of unrelated jobs.
- Carry the licence and the resolution caveat onto every verdict: node-level power at 5–10 Hz on an HPC cluster;
  0.2–3 Hz band only; not phase-level; not a GB200-class rack.
- No $ or capex claims here; the conversion stays in the ANGLES report.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `AWAITING APPROVAL <commit-hash>` or `BLOCKED: <one-line reason>`, then commit
and push.

**Status:** OPEN
