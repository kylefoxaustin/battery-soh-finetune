# X6 profile: knee definition and power (brief §3)

Run 2026-10-30 by `analysis/X6_profile.py`. Output: `X6/profile.json`.

**No forecaster (K0–K3), warning score, AUC or reserve has been computed.** All values are DERIVED from MEASURED lab
labels. Data, units and split are X5's, unchanged: ISU-ILCC, CC BY 4.0, 61 groups, 30 / 31 split. Coupling caveat:
*synthetic packs of separately tested cells; no thermal or electrical coupling; an upper bound.*

## Summary

| §3 item | Value (H = 2, T = 5 %) | Gate |
|---|---|---|
| **Knee events, evaluation half, full life** | **66** cells in 26 of 31 units (of 123 cells) | **≥ 30: PASS** |
| Knee events, evaluation half, first life (U ≥ 0.8·U₀) | **6** cells in 6 units | < 30: **first-life readout is descriptive only** |
| Calibration half, full life / first life | 64 (28 of 30 units) / 4 | |
| Warnable at L = 1 / 2 / 3, evaluation full life | 60 / 55 / 50 | |
| **The knee cell is already the weakest at onset − L** (evaluation, L = 1 / 2 / 3) | **22 % / 20 % / 22 %** of knee cells. For the **first cell to knee** in each unit: 35 % / 22 % / 25 %. | |
| Knees in cells that are **not** the weakest at onset − 1 (control 2) | 47 (evaluation) | ≥ 10: control 2 is scored, not descriptive |
| Task A cell-checks, evaluation full life | L = 1: 60 positive / 1,229 negative. L = 2: 115 / 1,117. | |
| Drop over the 2 checks after onset (median) | 8.2 % of Q₀ | |
| Capacity at onset (median) | 0.84·Q₀ | |

**Headline of the profile:** about **four in five knees start in a cell that is not the weakest** one check before.

- A min/max view watches only the weakest cell, so it is structurally blind to most knee onsets until they have
  already happened.
- That is the opening per-cell history would need. It does **not** yet say that history can see them coming.

## 1. Knee definition (§3.1), chosen without any forecast

A cell's **knee onset** is the first check k, with at least 3 earlier intervals, where both:

1. **Size:** the drop over the next H = 2 checks exceeds T = 5 % of the cell's starting capacity:
   `(Q_k − Q_{k+2}) / Q_0 > 0.05`.
2. **Rate:** that drop per unit time is **≥ 2×** the median of the cell's own per-interval drop rates up to k.

Only a cell's first onset counts.

**Why the brief's defaults (H = 2, T = 5 %) are kept.** All of the following are calibration half, all cells and
checks:

| | H = 1 | **H = 2** | H = 3 |
|---|---|---|---|
| Drop over H checks, p50 / p90 / p99 | 1.5 / 4.9 / 12.6 % | **3.1 / 9.3 / 21.6 %** | 4.6 / 13.5 / 28.0 % |
| Rate vs the cell's running median, p50 / p90 | 1.15× / 2.87× | **1.18× / 2.90×** | 1.19× / 2.95× |

- **T = 5 %** is about 20× the label noise (0.24 %). It sits above the median 2-check fade (3.1 %) and below p90
  (9.3 %), so ordinary fade alone does not trigger it.
- **The 2× rate condition** selects roughly the top decile of acceleration relative to each cell's own history (p90
  ≈ 2.9×). It does most of the work.
- **H = 2** spans two weekly RPTs, so one noisy check cannot make a knee.

**Robustness of the count** (evaluation, full life; events / units):

| | T = 3 % | **T = 5 %** | T = 8 % |
|---|---|---|---|
| H = 1 | 63 / 24 | 53 / 23 | 29 / 15 |
| **H = 2** | 75 / 30 | **66 / 26** | 56 / 24 |
| H = 3 | 75 / 29 | 73 / 29 | 60 / 25 |

The gate passes for every combination except H = 1, T = 8 % (29). Two alternatives are pre-registered as sensitivity:
H1/T3 and H3/T8.

## 2. Lead time (§3.2.2)

- A warning at check j = onset − L needs j ≥ W = 4, so that both a 4-check window and the Q(V) curve W checks
  earlier exist.
- Warnable events, evaluation full life: **60 / 55 / 50** at L = 1 / 2 / 3.
- **Lead-time honesty:** one check is about one week of a lab cycling regime with weekly RPTs (the "Time" column is
  in the dataset's units, about 1.1 per check). It is **not** a field lead time.

## 3. Is the knee cell already the weakest? (§3.2.3)

| Evaluation, full life | L = 1 | L = 2 | L = 3 |
|---|---|---|---|
| All knee cells: already weakest at onset − L | 22 % (n 60) | 20 % (55) | 22 % (50) |
| First cell to knee in its unit: already weakest | 35 % (26) | 22 % (23) | 25 % (20) |
| Calibration, all knee cells | 20 % (59) | 21 % (52) | 22 % (46) |

- **No**, mostly the knee cell is not already the weakest. A min/max view does not see these coming for free.
- **First life:** all 5 warnable evaluation events (and all 3 warnable calibration events) are in cells that were *not* the weakest.
  That is structural. Once the weakest cell knees, U crosses 0.8·U₀ and the first-life window ends, so first-life
  knees can only be visible in other cells.

## 4. Power (§3.2.4)

- **Full life: 66 evaluation events, so PASS.** Gate: ≥ 30.
- **First life: 6 events.** That readout is **descriptive only**, as the brief specifies.
- No second dataset is needed, so none is proposed.

## Notes for the reviewer

- The **K1 (min/max) score is per cell only for the cell that is currently weakest**. That is all a min/max view
  observes. Given §3, K1's Task A AUC is structurally limited.
  - That is the point of the question, but it means **an AUC win by K3 over K1 is expected on structure alone**.
  - The pre-registration therefore keeps the brief's two further conditions as the real test: the shuffle must not
    win, and Task B must turn warnings into a ≥ 1.5× smaller reserve.
- The pre-registration departs from the brief in **one** place (the shuffle permutes capacity and Q(V) jointly). The
  reason is given there (X6-P1).
