# X5 results review — ACCEPTED (2026-10-30)

> ## ▶ START HERE — instructions for the session running this repo
>
> 1. `git pull` on `main`. This file is the reviewer's acceptance of X5 (`b20dab3`).
> 2. **X5 is closed. Do not re-run, re-tune or extend it.** The verdict UNCLEAR stands as pre-registered.
> 3. Make the one housekeeping fix in §3 (commit-hash reference). Nothing else in X5 changes.
> 4. **Do not start any new experiment** until the reviewer posts the next brief. Stop after §3.

## 1. Process checks (all pass)

| Check | Result |
|---|---|
| D-1 and D-2 committed before estimator code | **Pass.** `624e4ee` touches only `X5_preregistration.md`; `analysis/X5_estimate.py` does not exist at that commit. |
| D-3 recorded before any run | Pass (alignment of an all-empty Q(V) column; no feature imputed). |
| X4 correction (`7857faf`) kept in `main` | Pass. |
| Thresholds, split, W, α, model family unchanged | Pass. |
| Coupling caveat on every verdict | Pass. |
| **Independent recompute** from `x5_targets_full.csv` | **Matches exactly:** r1 % P1 29.6, P3 19.8, P4 16.3, P3-shuffled 19.1; G(P3) 1.50, G(P4) 1.82, G_sh 1.55, P2/P3 1.02. Unit-bootstrap CI of G(P3) 1.29–2.49 reproduced. |
| Added reviewer statistic | r(P3 shuffled) / r(P3 real) at α 1 %: unit-bootstrap CI **0.85–1.40**. It spans 1, so cell identity adds nothing measurable. |

## 2. Accepted reading

- **UNCLEAR, both readouts, both P3 and P4.** No estimator reaches 4×.
- The gain over a pack-mean estimator is real (~1.5×), but **a min/max view captures all of it** (P2 ≈ P3) and it
  survives scrambling cell identity. Per-cell *history* adds nothing measurable beyond observing the weakest cell.
- Reserves sit 6–55× above the label-noise floor: the limit is **unpredictable late-life knees**, not measurement.
- Upper bound only: synthetic packs, no coupling.

## 3. One housekeeping fix

`results/X/X5/results_X5.md` cites `bd7a2af` as the D-1/D-2 commit. No such object exists in this repository; the
commit is **`624e4ee`**. Replace the hash in that file (two places if it appears twice) and commit with the message
`X5: fix D-1/D-2 commit reference (bd7a2af -> 624e4ee)`. No other edits.
