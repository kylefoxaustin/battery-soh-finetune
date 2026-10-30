# Experiment X5: can per-cell history shrink an uncertainty reserve? (clean-label test)

**Brief.** `briefs/X5/README.md` (public `x5-brief` branch, commit `8eb30b4`).

**Ordering.** This file, `X5_profile.md`, `X5/profile.json` and `X5/split.json` are committed **before any estimator
code exists**. They go to the reviewer before anything runs. **Nothing below is run until the reviewer approves.**

**Tags.** All outputs are DERIVED from MEASURED lab labels. The reserve is a statistic of prediction error, never a
kWh, cost, range or regulatory figure (brief §1.9, §7).

## 0. Departures from the brief's text (fixed now, before any results)

| # | Brief | X5 | Why |
|---|---|---|---|
| P-1 | Use Candidate A if it passes | **Candidate C (ISU-ILCC) is primary** | No candidate re-measures each cell's capacity inside a string that aged together (`X5_profile.md` §1–3). By the brief's own definition, A fails, so C runs (§2.4). |
| P-2 | Shuffle: "permute capacity series across cells within each unit" | **Permute the cells independently at each past check** (as X4's code did) | Moving whole series between cells leaves `min over cells` unchanged, so P3 would be identical by construction. The control would test nothing. |
| P-3 | `r_α = q(1−α)(−e)`, `e = U_pred − U_true` | **`r_α = q(1−α)(e) / median(U)`**. The brief's form is reported beside it as "under-prediction tail". | The reserve must cover **over-statement**, where U_pred > U_true. The brief's form is the other tail. X4 used it (`x4.py` L104–106). |
| P-4 | Sensitivity: linear vs last-value trend in P3 | Reported, but **it equals P0** | The minimum of each cell's last value is the last minimum. It is degenerate, not informative. |
| P-5 | Group size 4, 8 and 16 cells | **4 only** (3 for the one 3-cell group) | ISU has 4 cells per test condition. Larger groups would mix protocols, which the brief's "same protocol" rule forbids. |

## 1. Data, units and split

| Item | Value |
|---|---|
| **Dataset** | ISU-ILCC, figshare `10.25380/iastate.22582234`, **CC BY 4.0**. 251 Li-polymer NMC/graphite cells, 250 mAh rated, in a 30 °C chamber. |
| **Label** | `Q_c,k`: the RPT **C/5 discharge capacity** of cell c at check k (`capacity_fade/` files), **MEASURED**. Label noise is 0.24 % median (profile). |
| **Unit** | One test condition ("group"): its 3–4 cells form a **synthetic pack**. Checks are aligned across cells within 0.5 time units. The unit ends at the first check where any cell is missing. |
| **Usable units** | 61 groups with ≥ 3 cells and ≥ 6 common checks. Groups 11 and 14 are excluded. |
| **Split** | `X5/split.json`: a seed-0 permutation. **Calibration (fit) 30 groups; evaluation (score) 31 groups.** |
| **Coupling caveat** | It is carried on every verdict: *"synthetic packs of separately tested cells; no thermal or electrical coupling; an upper bound on what per-cell history can do."* |

## 2. Targets

For each unit and check k:

- `U_k = min over cells of Q_c,k`;
- `t_k` = that check's time on test, in the dataset's units.

A target is scored when k ≥ ⌈0.3·n⌉ (warm-up: the first 30 % of the unit's n checks) **and** k ≥ W. With W = 4, the
evaluation half has 374 targets (profile).

## 3. Estimators (strictly causal: only checks before k)

Here `trend_W(x)` is an ordinary least-squares line of x against t over the last W checks, evaluated at t_k.

| ID | Sees | Prediction of U_k |
|---|---|---|
| **P0** | U history | `U_{k−1}` |
| **P1 (pack)** | The unit's mean cell capacity `M_j` only | `ρ · trend_W(M)`. **ρ = the median of U_j / M_j over all calibration-half checks**, a constant. A pack-level BMS never observes U on its own pack, so ρ must come from other packs. |
| **P1-h** (reported, not deciding) | M and the unit's own past U | `trend_W(M) · median(U_j / M_j, j < k)`. The brief's "historical ratio". It uses per-cell knowledge of the same unit. |
| **P2 (min/max)** | The weakest cell's capacity at each past check | `trend_W(U)` |
| **P3 (per-cell)** | Every cell's own series | `min over c of trend_W(Q_c)` |
| **P4 (per-cell + curve)** | P3, plus each cell's RPT Q(V) curve (`Q_interpolated/`, 1,000 points from 3.0 to 4.2 V) | Per cell: `Q̂_c = Q_c,k−1 + Δ̂_c`. **Ridge model** (α = 1.0, standardised features, fit on calibration cells and targets only) of `Δ = Q_c,k − Q_c,k−1`, with three features: (1) the P3 slope × (t_k − t_{k−1}); (2) `log10 var_V(Q_c,k−1(V) − Q_c,k−1−W(V))`; (3) `Q_c,k−1 / Q_c,0`. Then `min over c`. |

The model family and features are fixed here, and nothing is tuned afterwards. If a cell's Q(V) column count does not
match its capacity checks, P4 is not scored for that unit, and the unit is counted.

## 4. Metric

- **Error:** `e = U_pred − U_true`. **Over-statement is e > 0.**
- **Reserve:** `r_α = q_(1−α)(e) / median(U_true)` over evaluation targets, for **α = 5 %, 1 % and 0.1 %**.
  - α = 0.1 % is flagged as an extrapolation (374 < 1,000 targets).
  - The brief's `q_(1−α)(−e)` is reported beside it as the under-prediction tail (P-3).
- **Precision gain:** `G = r_α(P1) / r_α(P3)`, and the same for P4. Any r ≤ 0 is floored at 0.1 % of median U before
  the ratio, and flagged.
- **CI:** 2,000 bootstrap resamples **of evaluation units** (groups), seed 0, percentile 95 %.
- **Also reported:**
  - MAE;
  - the share of targets where P3's |e| is less than P1's;
  - per-estimator `r_α`, both tails;
  - G for P3 against P2 and P0.

## 5. Decision (α = 1 %, checked in order)

| Verdict | Condition |
|---|---|
| **UNDERPOWERED** | < 40 scored evaluation targets |
| **LABELS TOO NOISY** | Label noise > 1 % (profile: 0.24 %, so not triggered) |
| **PER-CELL HELPS** | G(P3) ≥ 1.5, unit-bootstrap CI lower bound > 1, **and** the shuffle control's G < 1.2 |
| **NO GAIN** | G(P3) < 1.2 |
| **UNCLEAR** | Anything else |

- The same table is applied to P4 and reported as a second line.
- **4× reached?** This is stated separately for P3 and P4. Below 4× bounds what the data supports; it does not refute
  the reserve claim.

## 6. Controls

1. **Shuffle** (P-2): for each evaluation unit, a fresh seed-0-derived generator (`default_rng(group)`) permutes the
   cell order **independently at every past check**. P3 is then run unchanged. That gives `G_sh = r(P1) / r(P3_sh)`.
2. **Label-noise floor:** `floor_α = z_(1−α) · σ`, where σ = 0.24 %, the median cell label noise from the profile. That
   gives 0.39 % at α 5 %, 0.55 % at α 1 % and 0.74 % at α 0.1 %. Each estimator's reserve is reported against it. This
   is a Gaussian approximation.
3. **Pack-level truth:** score every estimator against `M_k`, the unit mean:
   - P1 and P1-h unscaled;
   - P2 is `trend_W(U) / ρ`;
   - P3 and P4 are the **mean** over cells instead of the min.

## 7. Sensitivity (pre-registered, each re-run end to end)

- W = 3 and W = 6.
- Warm-up 20 % and 40 %.
- P3 last-value. This equals P0 (P-4) and is reported as such.
- **Added:** truncate each unit at the first check where U < 0.8·U_0 (end of first life). Cells here run to a median
  51 % fade, beyond any automotive use.

## 8. Outputs

- **Code:** `analysis/X5_estimate.py`, written only after approval.
- **Write-up:** `results/X/X5/results_X5.md`, verdict first.
- **Contents:**
  - the reserve table (P0–P4 × α × tail);
  - gains with CIs;
  - all three controls;
  - the sensitivity table;
  - a plain statement of whether 1.5× and 4× are reached.
- **Plots:**
  - reserve vs α for each estimator;
  - U over life, predicted vs measured, for 3 evaluation units (the first three in `split.json` order, fixed now).
- **Also updated:** `results/X/README.md` and `results/RESEARCH_DOSSIER.md`.
- **No board run.**

## 9. Not run unless the reviewer asks

- **BatICM lab packs:** a descriptive secondary, with the measured pack charge capacity as target and 3 scored packs
  (profile §3–4).
- **Yuasa:** fails the label gate.
- **UMich:** no history.

## 10. Deviations

Any change after this commit is a numbered deviation. Thresholds, W, warm-up, α, the model family and the split never
move.
