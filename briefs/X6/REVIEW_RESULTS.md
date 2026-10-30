# X6 results review: ACCEPTED (2026-10-30). The X-series on reserve precision is closed.

> ## ▶ START HERE: instructions for the session running this repo
>
> 1. `git pull` on `main`.
> 2. **X6 is accepted and closed.** Do not re-run, re-tune or extend it. The verdict, UNCLEAR, stands.
> 3. **Do not start any new experiment.** There is no next task until the reviewer posts one in `NEXT_TASK.md`.
> 4. One optional housekeeping item, §3. If you do it, set `NEXT_TASK.md` Status to `DONE <hash>` and stop.

## 1. Process checks (all pass)

| Check | Result |
|---|---|
| D-1 and D-2 committed before forecasting code | **Pass.** `analysis/X6_forecast.py` first appears at `ec79131`; it is absent at `2881c7b`. |
| Thresholds, H, T, W, L, λ, the features and the split unchanged | Pass |
| Coupling caveat and licence on the verdict | Pass |
| **Independent recompute of Task B** from `x6_taskB_targets.csv` | **Matches.** r at α 1 %: K1-adj 16.6 %, K3-adj 16.3 %, so G_B ≈ 1.02. Best adjusted ÷ P1 = 1.82. |

## 2. Accepted reading

- **Verdict: UNCLEAR.** K3 beats the min/max view on warning AUC (+0.26), but the shuffle condition fails (+0.08,
  against a bar of < 0.05), and Task B fails (G_B 1.02, against ≥ 1.5).
- **The first positive cell-identity effect in the series:** AUC(K3) − AUC(K3-sh) = **+0.18** (CI 0.06–0.28). It holds
  for knees in non-weakest cells (K3 0.69, K3-sh 0.53). Per-cell identity carries real **warning** information that a
  min/max view does not have.
- **It is cheap, not deep.** Q(V) curve history adds nothing distinguishable over a 4-point per-cell capacity trend
  (K3 − K2: +0.09, CI −0.02 to 0.21).
- **It does not shrink the reserve.** The tail is set by how *much* a cell drops after onset, not by *whether* a warning
  fires. Both views flag the worst targets, and a typical-drop correction (2.8 % of Q₀) cannot close tail errors of
  ~16 %.
- **Programme conclusion (X5 + X6):** on the cleanest public per-cell data, history-based estimation reaches **at most
  1.82×** over a pack-mean estimator. A 20 % → 5 % uncertainty-reserve cut needs ~4×. This is an upper bound, from
  synthetic packs without coupling.

## 3. Optional housekeeping

Add a §9 row to `results/RESEARCH_DOSSIER.md` that cites this review and the two-line conclusion above, if it is not
already there. No other edits.
