# X4 pre-registration — does per-cell history make a pack's usable-energy estimate more precise?

Public domain (CC0). Written before any X4 analysis code exists.

## Question
The lifecost model found that cutting an **uncertainty reserve** from 20 % to 5 % is worth about $1,700 per vehicle, and
needs a usable-energy estimate about **4× more precise**. Usable energy is limited by the **weakest cell**: discharge
stops when the first cell reaches its low-voltage limit.

**X4 asks:** given the same history, does an estimator that sees every cell predict the pack's next usable-energy
measurement more precisely than one that sees only pack-level min/max/mean?

## Data
One Changan EV (CC BY-NC-SA 4.0, non-commercial): the six public sample files, 1.2 M frames at 10 s, 1,322 days,
0 → 66,297 km, 96 cell voltages per frame. **One vehicle only.** Every conclusion is a single-unit case study.

## Ground truth (DERIVED)
A **labelled discharge** is a run that starts at rest (|I| < 1 A for ≥ 30 min) and covers ≥ 40 % of SOC.
For each labelled discharge:
- Charge throughput `Ah` by integrating current (discharge positive).
- **Per-cell capacity** `Q_k = Ah / (SOC_k,start − SOC_k,end)`, with each cell's SOC read from its own **rest** voltage
  through an OCV table built from this vehicle's rests (ASSUMED, as in E/F). End state is the first rest after the run.
- **Usable-energy proxy** `U = min_k Q_k`, the weakest cell's capacity. This is the quantity the reserve protects.

## Estimators (all causal: only labelled discharges strictly before the target)
| ID | Sees | Prediction of the next U |
|---|---|---|
| **P0** | nothing | last observed U |
| **P1 (pack scalar)** | per-discharge pack `Q_pack = Ah / ΔSOC_pack` from BMS SOC | linear trend of the last W values of Q_pack, scaled by its historical ratio to U |
| **P2 (min/max)** | Vmin, Vmax only | U estimated using the min-voltage cell at each rest, linear trend over the last W |
| **P3 (per-cell)** | all 96 cells | per-cell linear trend of Q_k over the last W, then min over cells |

W = 8 labelled discharges (pre-registered). Sensitivity: W = 4, 16.

## Metric and decision
- Error `e = U_pred − U_true` on every target after a warm-up of the first 30 % of labelled discharges.
- **Reserve needed** at 1-in-1000 risk: `r = q_0.999(−e) / U`. This is the uncertainty reserve, expressed as a
  fraction of usable energy.
- **Precision gain** = `r(P1) / r(P3)`.

| Verdict | Condition |
|---|---|
| UNDERPOWERED | fewer than 40 labelled targets after warm-up |
| PER-CELL HELPS | gain ≥ 1.5 and P3 beats P1 on ≥ 60 % of targets |
| NO GAIN | gain < 1.2 |
| UNCLEAR | otherwise |

The 0.999 quantile on a few hundred targets is an extrapolation. Report it, with the empirical 0.95 and 0.99
quantiles beside it.

## Controls
- **Shuffle:** permute each cell's Q_k series across cell indices, then run P3. A gain that survives shuffling is not
  coming from tracking which cell is weakest.
- **Label circularity:** U is built from per-cell rest voltages, so P3 has a structural advantage. To check this,
  also score every estimator against a **pack-level** truth `Q_pack` from the same discharge. If P3 only wins against
  its own kind of label, report that.

## What X4 cannot show
- Fleet generality: one vehicle.
- The 4× needed: a gain below 4 does not refute the claim; it bounds what this data supports.
- Any real reserve, range or cost.

## Deviation 1 (recorded before any estimator code; found in the profile step)
The rest-to-rest rule found **0** labelled discharges. The logger stops while the car is parked, so ≥ 40 % SOC
discharges span several trips separated by logging gaps (median 5 gaps > 10 min per segment). **Fix:** a labelled
discharge is a non-charging segment (`chargestatus` ≠ 1) between two charges, with ΔSOC ≥ 40 %. Current is integrated
over logged frames only; gaps are treated as zero current (parked). Start and end states are each cell's voltage
at the first and last frames with |I| < 1 A inside the segment. Everything else is unchanged.
