# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-11-06. **Owner of this file:** the reviewer. The running session only *reads* it, except for the
Status line.

**Previous task — FR1: DONE, UNGATED** (both rater branches merged; analysis `analysis/FR1_agreement.py`; write-up
[`results/FR1/results_FR1.md`](results/FR1/results_FR1.md)). The reviewer session wrote and ran the analysis, so step 1
below is an independent re-derivation by this session before anything else. Plan:
[`briefs/NEXT_EXPERIMENTS/README.md`](briefs/NEXT_EXPERIMENTS/README.md) (order now X8 → O1 → R1).

## Do these steps, in order

1. `git pull` on `main`. **Re-derive FR1 from the two CSVs with your own code** (do not import or modify
   `analysis/FR1_agreement.py`): the both-rater exclusions (4 / 17 / 23; 41 cases), the PE denominator (36), the
   3-way κ over all rated cases (0.19) and over PE (0.55), the conservative PE fraction > 80 s (28 %, Wilson
   [16, 44]), and the base-rate fractions (A 96 % vs B 7 %). Write `results/FR1/review/rederivation.md` with your
   numbers beside the published ones; if any differ, stop with `BLOCKED: FR1 rederivation <item>` and push. Commit the
   re-derivation.
2. Open [`briefs/X8/README.md`](briefs/X8/README.md) and follow its START HERE box. **First stage only:** the profile
   (`results/X/X8_profile.md`, brief §3) and the pre-registration (`results/X/X8_preregistration.md`, brief §4 with every
   threshold filled in), then STOP. Reuse the McMaster/Changan loaders and the per-cell R identification, κ calibration
   and held-out safety scoring in `analysis/X2F_replay.py`.
3. Commit both with "before limiter code" in the commit message. **Write no limiter or scoring code.**
4. Set the Status line below to `AWAITING APPROVAL <commit-hash>`, push, and stop.

## Rules that always apply
- Pre-register before analysis code. Never move a threshold after seeing results. Number every deviation.
- Tag every number MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED.
- X8 uses Changan (CC BY-NC-SA, research only); carry that onto every verdict. Beihang (CC BY) only if the profile
  shows current and per-cell voltage at low SOC during discharge.
- X8's resolution gate (brief §3.4) comes before its power gate: median sag at the admitted current ≥ 10 voltage LSB.
- Lessons now standing for every rating or replay design: give "not observable / not applicable" its own state;
  closed lists, not free text, for anything that will be counted.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `AWAITING APPROVAL <commit-hash>` or `BLOCKED: <one-line reason>`, then commit
and push.

**Status:** AWAITING APPROVAL 600b296 (FR1 re-derivation 1fda86b: all match; X8 first stage)
