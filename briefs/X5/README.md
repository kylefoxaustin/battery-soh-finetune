> ## ▶ UPDATE 2026-10-30 — the audit and pre-registration have been reviewed
> **Read [`REVIEW_DECISION.md`](REVIEW_DECISION.md) first.** X5 is approved with two deviations (D-1, D-2). It also
> records a correction to X4's reserve tail. The brief below is unchanged and kept for the record.

---

# Build Brief — Experiment X5: can per-cell history shrink an uncertainty reserve? (clean-label test)

**Licence of this document:** public domain (CC0). Copy, modify and redistribute freely.
**For:** the Claude Code session that runs the `battery-soh-finetune` repository.
**Prerequisite reading, in order:** `results/X/X2F/results_X2F.md`, then the three result packs attached to this brief
(`lifecost/`, `convsim/`, `x4/`, each with `README.md`, code and JSON). Copy them into `results/X/` before starting.

---

## 0. Why this experiment exists

### 0.1 The question has changed
For months the programme looked for an **efficiency** gain from per-cell, history-based control. A converter replay
(`convsim/`) found that a load-indexed factory table stays within 0–1 % of optimal converter loss in every case. That
route is closed for quasi-static operation.

A lifetime cost model (`lifecost/`, Monte Carlo, all inputs ASSUMED) tested three public-style claims for consistency:

| Claim | Model result |
|---|---|
| "1 °C cooler charging ≈ $100 per vehicle" | Median $58 per kelvin (p10 26, p90 124). Plausible, at the optimistic end. |
| "Two ECUs removed" | ≈ $148 per vehicle |
| "A 20 % reserve can shrink to 5 %" | **If it is an uncertainty reserve: ≈ 14.8 kWh of cells avoided, ≈ $1,700 per vehicle.** It needs a usable-energy estimate about **4× more precise**. If it is a durability reserve, cooling cannot deliver it. |

So the dominant value is a **state-estimation** problem. Usable energy is set by the **weakest cell**. The reserve
protects against not knowing that cell's true remaining capacity. Halving the uncertainty roughly halves the reserve.

### 0.2 Why field data could not answer it
X4 (`x4/`) tested the question on one field EV with all 96 cells over 66,000 km. Result: **NO GAIN** (per-cell vs pack
precision ratio 1.05, shuffle control identical). But the labels are the problem, not the estimators:

- derived capacity labels scatter **~6 % between consecutive discharges**;
- they **rise** with mileage, which real capacity cannot do.

You cannot resolve a ~1 % precision question against 6 % label noise. **X5 needs per-cell capacity measured in a lab.**

### 0.3 What X5 is
The X4 question, on data whose labels are measured, not derived:

> Given each cell's own history, does a per-cell estimator predict the **weakest cell's capacity** (and so the pack's
> usable energy) precisely enough to shrink the reserve, compared with an estimator that sees only pack-level data?

All three outcomes are useful. A clean NO GAIN on good labels would be a strong result: it would mean the reserve claim
needs something other than per-cell history.

---

## 1. Rules of engagement (unchanged)

1. A pleasing number is a suspected defect until gated.
2. Tag every figure MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED.
3. Gate in the same run as the measurement.
4. Verify the rendered artefact, not the build log.
5. State CHOSEN versus IMPOSED inputs.
6. Show sensitivity, not one hero number.
7. A clean INCONCLUSIVE or UNDERPOWERED is a valid outcome.
8. **Commit `X5_preregistration.md` and `X5_profile.md` before any estimator code exists.** Never move a threshold after
   seeing results. Every later change is a numbered deviation.
9. No regulatory, economic, range or real-reserve claim. The reserve is a statistic of prediction error.
10. Carry each dataset's licence onto every verdict.

---

## 2. Data — in priority order

The first task is a **dataset audit**. For each candidate, report: number of cells, whether they were tested as one
pack/module or separately, how capacity was measured (method, rate, temperature), how often, the stated label
uncertainty, and the licence. Then pick per §2.4.

### 2.1 Candidate A — cells aged together, with repeated capacity checks (best fit)
Datasets where **several cells of one string or module** are cycled together and each cell's capacity is re-measured at
intervals (reference performance tests). These match the question exactly: a pack's weakest cell, tracked over life.

Look for, at minimum:
- **UMich parallel-module set** (Mendeley, doi `10.17632/ssrgfmb8vw.2`, arXiv `2604.16769`, CC BY 4.0): 78 modules,
  70 cells, accurate cell-level capacity and internal-resistance labels, designed sweep of cell-to-cell variation.
  Earlier search tagged it LIKELY; the file schema was not inspected. **Inspect it first.**
- Any other module- or string-level ageing set with per-cell reference tests. State what you searched.

### 2.2 Candidate B — a snapshot with very good per-cell labels
- **Yuasa second-life BESS** (Zenodo `10.5281/zenodo.22281620`, arXiv `2609.04487`, MIT): 324 cells in 27 modules,
  each with measured capacity Q and uncertainty Q_sigma, plus ~12.7 h of 10 s cycling.

There is **no ageing trajectory** here, so it cannot test history-based prediction. It **can** test the snapshot form:
from operational telemetry alone, can a per-cell estimator identify each module's weakest cell and its capacity more
precisely than a module-level estimator? That bounds the reserve at one point in life.

### 2.3 Candidate C — single-cell ageing sets as a synthetic pack (fallback only)
Large single-cell ageing sets (for example the 124-cell fast-charge set of Severson et al., 2019, or other public
cycling sets) can be **grouped into synthetic "packs"** of cells with the same protocol. The weakest cell's measured
capacity is then the ground truth.

**This fallback has a known flaw: the cells did not share a pack, so there is no thermal or electrical coupling, and
cell-to-cell spread may not resemble a real pack.** If used, state that on every verdict, and treat the result as an
upper bound on what history could do.

### 2.4 Choice rule (fix in the pre-registration)
Use the highest-priority candidate that passes the audit gates in §3. If both A and B pass, run both: A is the primary
(history), B is a secondary (snapshot). C runs only if A fails.

---

## 3. Mandatory first step — profile and power check

Before any estimator code, write `X5_profile.md`:

1. **Label noise.** The repeatability of the capacity measurement: from repeated tests at the same state if available,
   otherwise the dataset's stated uncertainty. **Gate: label noise must be ≤ 1 % of capacity.** Above that, the dataset
   cannot resolve the question. Report it and move to the next candidate.
2. **Units.** Packs, modules or synthetic groups; cells per unit; capacity checks per cell.
3. **Spread.** The distribution of (max − min)/mean capacity within each unit, at the first and last check. If spread
   stays below the label noise, per-cell information has nothing to find. Report that as the finding.
4. **Weakest-cell persistence.** How often the weakest cell at one check is still the weakest at the next.
5. **Power.** **Gate: ≥ 40 scored prediction targets after warm-up** (as in X4). Fewer is UNDERPOWERED.

---

## 4. Method

### 4.1 Targets
For each unit and each capacity check k after warm-up, predict `U_k = min over cells of Q_cell,k`: the weakest cell's
measured capacity.

### 4.2 Estimators (all strictly causal: use only checks before k)
| ID | Sees | Prediction |
|---|---|---|
| **P0** | nothing | last observed U |
| **P1 (pack)** | the unit's total or mean capacity series only | linear trend over the last W checks, scaled by the historical ratio U / pack |
| **P2 (min/max)** | only the cell that was weakest at each past check | linear trend of that series |
| **P3 (per-cell)** | every cell's own capacity series | per-cell linear trend over the last W checks, then min over cells |
| **P4 (per-cell + telemetry)** | P3 plus each cell's operational features between checks (e.g. resistance from current steps, rest-voltage drift), if the data has them | pre-register the model family; keep it simple (regularised linear) |

W = the last 4 checks (fix in the pre-registration; sensitivity at 3 and 6). Warm-up: the first 30 % of checks per
unit.

### 4.3 Splits
Units, not checks, are the unit of evaluation. Split units 50/50 at random (seed 0) **before any estimator runs**, and
record the IDs. Fit any learned parameter (P1's ratio, P4's coefficients) on the first half; score on the second.

### 4.4 Metric
- Error `e = U_pred − U_true`.
- **Reserve needed** at risk level α: `r_α = q_(1−α)(−e) / median(U)`, the fraction of usable energy that must be held back
  so the prediction overstates the weakest cell no more than α of the time. Report α = 5 %, 1 % and 0.1 %. Flag
  0.1 % as an extrapolation when there are fewer than ~1,000 targets.
- **Precision gain** = `r_α(P1) / r_α(P3)`, and the same for P4.

### 4.5 Decision (checked in order)
| Verdict | Condition |
|---|---|
| UNDERPOWERED | fewer than 40 scored targets in the evaluation half |
| LABELS TOO NOISY | label noise > 1 % |
| PER-CELL HELPS | gain at α = 1 % ≥ 1.5, vehicle/unit-bootstrap CI lower bound > 1, **and** the shuffle control's gain < 1.2 |
| NO GAIN | gain at α = 1 % < 1.2 |
| UNCLEAR | anything else |

Report separately whether the gain reaches **4×**, the level the reserve claim needs. Below 4× is not a refutation; it
bounds what the data supports.

### 4.6 Controls
1. **Shuffle:** permute capacity series across cells within each unit, then run P3. If the gain survives shuffling, it
   is not coming from tracking the weakest cell.
2. **Label-noise floor:** compute P3's reserve against the measurement noise alone (the best any estimator could do).
   Report how close each estimator gets to it.
3. **Pack-level truth:** also score every estimator against the unit's total capacity, as in X4.

---

## 5. Sensitivity (pre-registered)
- W = 3 and 6.
- Warm-up 20 % and 40 %.
- Linear versus last-value trend in P3.
- For Candidate C: group size 4, 8 and 16 cells.

---

## 6. Deliverables
1. `results/X/X5_preregistration.md` and `results/X/X5_profile.md`, committed before any estimator code.
2. `results/X/X5/results_X5.md`: verdict first; the reserve table (P0–P4 × α); precision gains with CIs; all three
   controls; the sensitivity table; and a plain statement of whether per-cell history reaches 1.5× and 4×.
3. Plots: reserve vs α for each estimator; weakest-cell capacity over life, predicted vs measured, for 3 example units.
4. Update `results/X/README.md` and `results/RESEARCH_DOSSIER.md`.

---

## 7. What not to do
- Do not use field-derived capacity labels (Changan, Beihang, EVBattery). X4 showed their noise is too large.
- Do not score on units used to fit anything.
- Do not tune W, warm-up, α or model family after seeing results.
- Do not skip the shuffle control. Two earlier positives in this programme were later explained by artefacts.
- Do not convert the reserve fraction into kWh, dollars, range or a regulatory statement.
- Do not present a synthetic-pack (Candidate C) result without its coupling caveat.

---

*Audit first. Gate on label noise. Predict the weakest cell. Shuffle the cells. Pre-register everything, and report
whatever comes out.*
