# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-11-10. **Owner of this file:** the reviewer. The running session only *reads* it, except for the
Status line.

**X8 first stage (`600b296`) is APPROVED without changes.** The FR1 re-derivation (`1fda86b`) matched every published
number and is closed. Read the APPROVED box in [`briefs/X8/README.md`](briefs/X8/README.md): it records three
expectations (zero-reference frames; headroom not realised current; the binding dither check) that the write-up must
address. Plan: [`briefs/NEXT_EXPERIMENTS/README.md`](briefs/NEXT_EXPERIMENTS/README.md).

## Do these steps, in order

1. `git pull` on `main`. Read the APPROVED box, then `results/X/X8_preregistration.md` once more.
2. Write `analysis/X8_bottom.py` and run the Changan primary exactly as pre-registered (§2–§7 of the pre-registration):
   both fold directions, every limiter's κ curve (calibration and held-out), S / S_sh / D with vehicle-bootstrap CIs,
   the reported-not-deciding quantities (binding-cell fraction, I_ref = 0 fraction, SOC < 10 % and cold subsets,
   usable depth), the sensitivities (V_cut ± 50 mV, 20 s horizon, R held vs re-estimated, 0.1 % and 0.5 % bars) and
   the **dither check**.
3. Run the Beihang **DTI** arm, then **QAS**, with their own V_cut, folds and gates; each gets its own verdict.
4. Commit `results/X/X8/results_X8.md` (verdict first, Changan then DTI then QAS; the NC-SA caveat on Changan; the
   three APPROVED-box expectations each answered in a sentence), `results/X/X8/x8.json`, the margin table, the plots
   (κ vs unsafe fraction per limiter and direction; the S distribution; one session's admissible currents), one row
   each in `results/X/README.md` and `results/RESEARCH_DOSSIER.md` §9, and a dated note under ANGLES §1.1 / §B.
5. Set the Status line below to `DONE <commit-hash>`, push, and stop. Do not start O1.

## Rules that always apply
- Nothing in the pre-registration moves after results are seen; any change is a numbered deviation (X8-D1, …).
- Tag every number DERIVED (replay) / ASSUMED (V_cut, 1 C, limits). No kWh, range, cost or C2 percentage.
- Carry the licence: Changan CC BY-NC-SA, research only; Beihang CC BY 4.0, citable.
- If the dither check moves S by more than its CI width, the verdict carries the "rounding" label.
- Report the κ each limiter needed and whether min/max's margin transferred, as X2-F did.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `DONE <commit-hash>` or `BLOCKED: <one-line reason>`, then commit and push.

**Status:** DONE f5296cb (X8: NOT INTERPRETABLE on Changan, DTI and QAS)
