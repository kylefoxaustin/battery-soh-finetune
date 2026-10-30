# Build Brief — Experiment X6: can history forecast a cell's knee before it arrives?

**Licence of this document:** public domain (CC0).

> ## ▶ START HERE — instructions for the session running this repo
>
> 1. `git pull` on `main`. First, finish the one housekeeping fix in `briefs/X5/REVIEW_RESULTS.md` §3 if not done.
> 2. Read this brief in full, then `results/X/X5/results_X5.md`.
> 3. Do **§3 (profile and knee definition) only**, then write `results/X/X6_preregistration.md` and
>    `results/X/X6_profile.md`. **Commit both before any forecasting code exists.** Message must say "before
>    forecasting code".
> 4. **Stop and push for review.** Do not write `analysis/X6_forecast.py` until the reviewer approves.
> 5. Reuse X5's data (ISU-ILCC, already in `data/raw/isu_ilcc`), split (`X5/split.json`) and estimators unchanged.

---

## 0. Why X6 exists

X5 (`results/X/X5/`) found, on the cleanest public per-cell data:

- per-cell history gives ~1.5× over a pack-mean estimator, but **a min/max view gets the same** (P2 ≈ P3) and a
  **shuffled control gets the same** (1.55×). Cell identity over life adds nothing measurable;
- nothing reaches the ~4× a 20 % → 5 % uncertainty-reserve cut needs (best: 1.82×);
- reserves sit 6–55× above the label-noise floor. **The reserve is set by unpredictable late-life knees**, not by
  measurement error.

Reviewer checks on X5's committed targets (`x5_targets_full.csv`, DERIVED, post-hoc) support that last point:

| | Value |
|---|---|
| P3's top-5 % over-statement errors: median capacity relative to the unit's start | **0.69** (all targets: 0.88) |
| Week-to-week drop of the weakest cell: median / p95 / p99 | 3.1 % / 15.5 % / 25.2 % |
| Correlation of P3's error with the next check's drop | **0.77** |

So the remaining question is narrow:

> **Can a cell's history predict that it is about to knee, early enough to hold reserve against it, better than
> watching the weakest cell's level and trend (P2)?**

If yes, history earns something a min/max view cannot: knee precursors are subtle curve-shape features that need
per-cell history. If no, history-based estimation gives the reserve claim no support on public data. **Both outcomes
close the question.**

---

## 1. Rules of engagement (unchanged)

1. A pleasing number is a suspected defect until gated.
2. Tag every figure MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED.
3. Gate in the same run as the measurement.
4. State CHOSEN versus IMPOSED inputs.
5. Show sensitivity, not one hero number.
6. A clean NO GAIN or UNDERPOWERED is a valid outcome.
7. **Pre-register before forecasting code.** Never move a threshold after seeing results. Every later change is a
   numbered deviation.
8. No kWh, cost, range or regulatory claim.
9. Carry the licence (ISU-ILCC, CC BY 4.0) and the coupling caveat on every verdict:
   *"synthetic packs of separately tested cells; no thermal or electrical coupling; an upper bound."*

---

## 2. Data

ISU-ILCC exactly as X5: the same 61 groups, the same 30 / 31 split, the same RPT C/5 capacity labels and Q(V) curves.
No new dataset. The point is to change the question, not the data.

**If** the §3 power gate fails and a second public single-cell ageing set with dense capacity checks and voltage
curves would rescue it, name it in the profile, with licence and label noise, and **ask the reviewer** before using
it.

---

## 3. Mandatory first step — knee definition and profile (commit before forecasting code)

### 3.1 Define a knee event (fix in the pre-registration)
For each cell, a **knee onset** is the first check k where the capacity drop over the next **H** checks exceeds **T**
of the cell's starting capacity, with the drop rate at least **2×** the cell's own median weekly drop so far.

- Propose H and T from the data *without* looking at any forecast. Defaults to justify or replace: **H = 2 checks,
  T = 5 %**.
- Report how many cells and units have a knee in the evaluation half, both full life and before `U < 0.8·U_0`.

### 3.2 Profile (`X6_profile.md`)
1. Knee events per half, per readout (full life; first life).
2. Lead time available: checks between the earliest "warning" point (k − L, L = 1, 2, 3) and the onset.
3. **Is the cell that knees already the weakest?** How often the first cell to knee in a unit is *already* the
   weakest at onset − L. If almost always, a min/max view sees it coming for free; say so.
4. **Power gate:** at least **30 knee events** in the evaluation half (full life). Fewer is UNDERPOWERED; report and
   stop. Report the first-life count too; under 30 makes the first-life readout descriptive only.

---

## 4. Method (to be pre-registered after §3)

### 4.1 Two tasks
**Task A — warning.** At each check, for each cell, predict whether a knee onset occurs within the next L checks
(L = 1, 2). Score with AUC, and precision at a fixed 10 % false-alarm rate, against all cell-checks not within L
checks of an onset.

**Task B — reserve.** Re-run X5's reserve metric (weakest-cell capacity at the next check, `q(1−α)(e)`, α = 1 %),
with each estimator allowed to **add a knee-risk adjustment**: when its warning score for any cell exceeds a
threshold fixed on the calibration half, the forecast for that cell is lowered by that cell's calibration-half median
post-onset drop. This asks whether warnings turn into a smaller reserve.

### 4.2 Forecasters (all strictly causal)
| ID | Sees | Warning score |
|---|---|---|
| **K0** | nothing | constant (base rate) |
| **K1 (min/max view)** | the weakest cell's capacity series only | slope and curvature of its last W checks |
| **K2 (per-cell trend)** | every cell's capacity series | each cell's slope and curvature, max over cells |
| **K3 (per-cell curve features)** | K2 plus each cell's RPT Q(V) curve | K2's features plus Q(V) shape features: the variance of ΔQ(V) between the latest RPT and W checks earlier, and the shift of the main dQ/dV peak. **Regularised logistic regression**, features standardised, fit on calibration cells only. |
| **K3-sh (shuffle)** | K3, with each cell's Q(V) history permuted across cells within the unit at every past check | same model |

W = 4 (as X5); sensitivity at 3 and 6. Model family, features and regularisation are fixed in the pre-registration
and never tuned.

### 4.3 Decision (fill exact thresholds in the pre-registration)
| Verdict | Condition |
|---|---|
| UNDERPOWERED | < 30 knee events in the evaluation half |
| **HISTORY FORECASTS KNEES** | K3's warning AUC exceeds K1's by ≥ 0.10 (unit-bootstrap CI of the difference > 0) **and** K3-sh does not (difference < 0.05) **and** Task B gain r(K1-adjusted) / r(K3-adjusted) ≥ 1.5 |
| **WEAKEST-CELL VIEW SUFFICES** | K1's warning AUC is within 0.05 of K3's |
| **UNCLEAR** | anything else |

Report separately whether any adjusted reserve reaches **4×** over the pack-mean estimator P1 from X5.

### 4.4 Controls
1. **Shuffle** (K3-sh): if knee warning survives scrambling cell identity, it is not per-cell history.
2. **Who knees:** repeat Task A restricted to knees in cells that are **not** the weakest at onset − L. This is where
   a min/max view is structurally blind. Report n; under 10 events is descriptive only.
3. **Lead-time honesty:** report L = 1 and L = 2 separately. One check ahead at weekly lab RPTs is not a field lead
   time.

---

## 5. Deliverables
1. `results/X/X6_profile.md` and `results/X/X6_preregistration.md`, committed before forecasting code.
2. After approval: `results/X/X6/results_X6.md` (verdict first), JSON, plots (warning ROC per forecaster; reserve vs
   α with and without knee adjustment), README and dossier updates.

## 6. What not to do
- Do not change X5's split, data or labels.
- Do not tune the knee definition (H, T) after any forecast exists.
- Do not report a warning AUC without K1 and K3-sh beside it.
- Do not claim a field lead time from weekly lab RPTs.
- Do not start a new dataset without asking the reviewer.

---

*Define the knee first. Gate on knee count. Beat the weakest-cell view, and survive the shuffle. Pre-register
everything, and report whatever comes out.*
