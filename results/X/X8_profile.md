# X8 profile: the bottom of the SOC range (brief §3)

**Written:** 2026-11-06, **before any limiter or scoring code exists.** No admissible current, κ, S or reference limit
has been computed. **Code:** `data/changan_lowsoc.py` (loader) and `analysis/X8_profile.py` (profile statistics).
**Outputs:** `X8/profile.json` (fleet summary plus one row per vehicle) and `X8/split.json` (folds, fixed here).

**Tags.**
- Every figure is **DERIVED** from field telemetry unless it is marked otherwise.
- V_cut and 1 C are **ASSUMED**.
- Changan is **CC BY-NC-SA 4.0, research only**. Beihang is **CC BY 4.0**.

## 0. Loader: why a new one was needed

- **What the old loader kept.** `changan_cells.py` (Experiment E) keeps the 96-cell vector only every 6th frame
  (about 1 min), plus every frame near the top of charge.
- **Why that rules out steps at the bottom.** X2's identification needs consecutive frames ≤ 30 s apart. This is why
  X2-F found Changan too sparse (a median of 7 steps in 30 days).
- **What the new loader does.** `data/changan_lowsoc.py` re-streams each `vinN.rar` through libarchive, never writing
  the CSV to disk. It keeps **every** valid frame with SOC < 30 %, with all 96 cell voltages and all 32 probes.
  - The cut-off is 30 %, CHOSEN, so that the R history and the 20–30 % context exist.
- **Counts.** 820,695,014 raw rows; 790,976 placeholders; 53,646,105 low-SOC rows; 2,558,942 malformed (cell or probe
  list incomplete); **51,087,163 kept**.
- **Validity filters.**
  - The cell list must match the scalar min/max columns within 0.5 mV (`sync`, as Experiment E).
  - Every cell must lie within **2.0–4.5 V** (as X2-C). This drops 1,032 synced frames that carry a 0 mV cell
    reading.
- **Sign.** The Changan source current is **discharge-positive**. The brief's "I < 0" is in X2's charge-positive
  convention. A **discharge frame** is valid, I > 1 A in the source sign, and status ≠ 1 (charging). CHOSEN.

## 1. Low-SOC discharge segments (§3.1)

**Definitions.**
- A **segment** is a run of contiguous discharge frames with gaps ≤ 30 s (CHOSEN), at least 6 frames long (brief).
- **1 C = 120 A, ASSUMED.** This is X2's OPEN-3, the median of the fleet's fast-charge capacity labels. It is not a
  SOURCED nameplate: `dataset_profile.md` carries only DERIVED labels (≈ 120–126 Ah). The brief asked for SOURCED, and
  none exists.

| Quantity (300 vehicles) | Fleet total | Per vehicle p10 / p50 / p90 |
|---|---|---|
| Segments reaching SOC < 20 % | 504,101 (all 300 vehicles) | 424 / 1,274 / 3,486 |
| Segments reaching SOC < 10 % | 88,251 (295 vehicles) | |
| Discharge frames at SOC < 20 % in those segments | 5,504,732 | 4,434 / 13,989 / 38,912 |
| Discharge frames at SOC < 10 % | 977,104 | |
| Segment length, frames (median of vehicle medians) | 8 (city stop-start, 10 s frames) | |
| Current at SOC < 20 %, in C: p5 | | 0.011 / 0.013 / 0.017 |
| Current at SOC < 20 %, in C: p50 | | 0.045 / 0.082 / 0.142 |
| Current at SOC < 20 %, in C: p95 | | 0.51 / 0.65 / 0.79 |
| Minimum cell voltage reached at SOC < 20 % (mV) | | 3,069 / 3,338 / 3,392 |
| Coldest probe at SOC < 20 % (°C, vehicle minimum) | | 0 / 8 / 12 |

**Reading.** Driving at the bottom is mostly light: the median current is about 0.08 C. The p95 current is about
0.65 C (≈ 78 A).

## 2. The cut-off (§3.2; ASSUMED, fixed now)

| | mV |
|---|---|
| Lowest valid cell voltage in any low-SOC frame | 2,011 (a validity-floor outlier) |
| Frame minimum cell voltage over low-SOC discharge frames: p0.1 / p1 / p50 | **3,353** / 3,432 / 3,563 |
| **V_cut** (p0.1 rounded down to 10 mV) | **3,350** |
| Sensitivity | 3,300 and 3,400 |

169 of 300 vehicles go below 3,350 mV at least once at SOC < 20 %. V_cut is a replay quantity, not the BMS's floor.

## 3. Per-cell R at low SOC (§3.3)

**Identification (as X2):**
- consecutive valid frames ≤ 30 s apart;
- |ΔI| ≥ 0.3 C (36 A);
- pack-mean probe temperature change ≤ 1 K;
- R_c = ΔV_c / ΔI.

**Steps used: driving only (status ≠ 1).** CHOSEN, because the limiter acts on discharge. All-status steps would add
only about 1.5 % (median 31,346 against 30,873 per vehicle at SOC < 30 %).

| Quantity (per vehicle p10 / p50 / p90) | Value |
|---|---|
| Driving steps at SOC < 30 % | 10,605 / 30,873 / 69,633 |
| Driving steps at SOC < 20 % | 2,825 / 9,808 / 27,463 |
| Median R_c at SOC < 20 % (mΩ) | 0.437 / **0.475** / 0.528 |
| R_max / R_median across the 96 cells | 1.13 / **1.27** / 1.46 |
| Split-half (even vs odd steps) Spearman ρ of R across cells | 0.974 / **0.995** / 0.999 |
| Fraction of SOC < 20 % discharge frames where the **minimum-voltage cell is also the highest-R cell** | 0.004 / **0.019** / 0.121 |

**Readings.**
- **Per-cell R is a stable, identifiable property at the bottom,** as X2-F found at the top (split-half ρ 0.995).
- **The present minimum-voltage cell is almost never the highest-R cell (median 2 % of frames).** This runs against
  the brief's stated expectation. At low SOC, the cell at the bottom of the voltage spread is the most discharged
  (lowest capacity or SOC) cell, not the most resistive. Min/max therefore does **not** see the high-R cell for free.
- This is a profile statistic, not a limiter result. It uses whole-vehicle R (non-causal) and does not say which cell
  binds under a larger current.

## 4. Resolution gate (§3.4)

| | Value |
|---|---|
| Cell voltage LSB | **1 mV** (from the data) |
| Current LSB | **0.1 A** (from the data) |
| Median sag \|I_t · R\| at the **observed** current (median vehicle) | 4.7 mV (**4.7 LSB**) |
| Sag at the **admitted-current approximation** (fleet-median R 0.475 mΩ × median-vehicle p95 current 77.6 A) | 36.8 mV (**36.8 LSB**) |
| Cell-to-cell R difference at that current (R_max/R_med 1.27 → 0.13 mΩ × 77.6 A) | ≈ 10 mV (≈ 10 LSB) |
| Smallest identification step (0.3 C × 0.475 mΩ) | ≈ 17 mV (17 LSB) |

- **Gate (≥ 10 LSB at the admitted current, per NEXT_TASK and brief §3.4): PASSES (36.8 LSB).**
- **Disclosed.** At the currents the fleet actually draws, the median sag is below 10 LSB. The per-cell difference the
  limiter would exploit is about 10 LSB even at the p95 current. The dither control (§4.6.5) is therefore a binding
  check on this data, not a formality.

## 5. Power gate (§3.5)

**Definitions.**
- A **scored frame** is a discharge frame at SOC < 20 % inside a segment.
- **R history** means at least 40 driving steps at SOC < 30 % in the 30 days before the frame. That is ≥ 20 in each
  even/odd half, the X2-F rule, and stricter than the brief's ≥ 20.

| | Vehicles with ≥ 20 such frames | Frames |
|---|---|---|
| **SOC < 20 % (primary)** | **300** (gate 30) | 5,450,298 |
| With ≥ 20 steps only (brief wording) | 300 | |
| SOC < 10 % | 294 | 959,566 |
| Cold (coldest probe < 10 °C) | 190 | 299,227 |

**Gate: PASSES.** The < 10 % and cold subsets are each above 10 vehicles, so both are analysable as secondaries.

## 6. Folds (§3.6; CHOSEN, fixed now)

- **Rule.** All 300 vehicles are sorted by scored-frame count (descending; ties by VIN number) and assigned in a
  serpentine A, B, B, A, … order.
- **Result.** 150 vehicles per half; 2,724,258 scored frames in A and 2,726,040 in B.
- **Use.** κ is calibrated on one half and scored on the other, in both directions. The lists are in `X8/split.json`.

## 7. Beihang eligibility (§3.7)

**Is it eligible: yes.** Beihang carries current and per-cell voltage at low SOC during discharge.
- These frames were never used before. X2-C and X2-F used charging frames only.
- Same profile rules, normal vehicles only (as X2-C).
- **Frames are 30 s with no timestamps.** "30 days" is X2-C's 86,400-frame window.
- **Discharge** means charge-positive current < −1 A. There is no status column.
- SOC < 20 % and < 10 % are 0.20 and 0.10 on the file's fractional scale.

| | QAS (LFP; V_lim 3.51 V in X2-C) | DTI (NMC) |
|---|---|---|
| Normal vehicles | 335 | 77 |
| Discharge frames at SOC < 20 % | 7,289 | 39,098 |
| Vehicles with ≥ 20 such frames | 75 | 57 |
| **Vehicles with ≥ 20 frames carrying R history (≥ 40 steps at SOC < 30 %)** | **32** | **48** |
| Scored frames with history | 3,428 | 34,593 |
| Median steps at SOC < 30 % per vehicle | 6 | 69 |
| Cell LSB | 1 mV | 1 mV |
| Mean-cell R at low SOC (fleet median) | 1.94 mΩ | 0.376 mΩ |
| p95 discharge current at SOC < 20 % (median vehicle) | 46.9 A | 65.9 A |
| Sag at the admitted-current approximation | 90.9 mV (91 LSB) | 24.8 mV (25 LSB) |
| V_cut (p0.1 of discharge minimum cell at SOC < 30 %, rounded down) | 2,840 mV | 2,900 mV |
| Folds (same serpentine rule), scored frames A / B | 1,757 / 1,671 | 17,596 / 16,997 |

**Reading.** Both fleets pass the power and resolution gates on their own counts.
- **DTI** (NMC, 48 vehicles) is the usable replication arm.
- **QAS** passes narrowly: 32 vehicles, 3,428 frames, a median of 6 steps. It is also LFP, so its flat OCV makes
  "V + I·R" a different estimator.

The pre-registration treats both as replication arms under the same rules. Under CC BY 4.0, their verdicts are
citable. Changan's are not.
