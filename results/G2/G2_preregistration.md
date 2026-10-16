# Experiment G.2 — pre-registration: does per-cell data flag teardown-confirmed faulty packs better than min/max?

This file is committed **before** `analysis/G2_beihang.py` exists, and before any feature has been computed for any
vehicle or compared with any label. Kyle approved the run on 2026-10-15 ("lets do the run as you suggest").

**What G.2 re-runs.** It is a re-run of Experiment F's primary question (F §5). On Changan that question was
UNDERPOWERED, with 3 positives. G.2 asks it on data whose labels are **independent of the telemetry**.

**Tags:** MEASURED / DERIVED / ASSUMED / SOURCED, as in E–H. No regulatory or economic claim will be made.

## 0. Data, and what has already been seen (disclosure)

**Dataset.** Cao et al., *Nat Commun* 2025, doi 10.1038/s41467-025-56832-8, Zenodo 10656500, **CC BY 4.0**. All
files passed md5 verification. The paper on labels (SOURCED): *"determined by product engineers after
disassembling the battery pack samples and characterizing failures retroactively."*

**Files.** One torch-pickled tensor per vehicle. They are loaded through a restricted unpickler that allows only
tensor/OrderedDict rebuild, with `map_location=cpu`.

**Layout** (taken from the authors' `Train_.py` and `Test_.py`, Zenodo 14555916). vin_2 = `[x(2) | y(k) | z(k) | q]`.

| Maker | Cell voltages y | q columns | Rows | Labels |
|---|---|---|---|---|
| **QAS** | k = 110 cell voltages, in V | [temperature °C, SOC 0–1, current A] | — | 393 vehicles: **58 faulty (Label 1), 335 normal** |
| **DTI** | k = 85, in mV | [temperature, SOC %, current] | Some vehicles have < 100 rows | 80 vehicles: 3 faulty |
| **GIS** | — | — | — | No label file: **excluded** |

**Format notes.**

- The label is **vehicle-level and binary**. It carries no cell, no fault type, and no failure time.
- QAS current uses **−1000 as an invalid sentinel**.
- **There are no timestamps.** Rows are 30 s frames in order, with unknown gaps.
- In vin_1 (normalised), column 2 is non-decreasing in every vehicle checked, so it is probably mileage. It is not
  used, except for the descriptive check in §5.

**Seen before this commit:**

- the label counts;
- that the QAS faulty IDs are **contiguous (335–392)**;
- raw rows and column ranges for QAS vehicles 0, 5, 20, 335 and 360, and DTI vehicles 0, 5 and 20;
- one count of tied columns in vehicle 360.

No per-cell deviation, slope, min/max feature, or any other per-vehicle summary has been computed for any vehicle or
set against labels.

## 1. Limitations stated up front

1. **There is no failure time.** We cannot know how long before the failure each record ends. "Early" can therefore
   only mean the **first half of each vehicle's record**, not a fixed lead time. If records end at the failure, then
   the first half is at least half a record early. That is **ASSUMED**, not known.
2. **Possible cohort confound.** The contiguous faulty IDs suggest the faulty vehicles may have been collected
   separately. They could differ in season, mileage, firmware, or data-processing path, and any of those can leak
   into features. §4 adds negative controls.
3. **The labels don't say which cell or what fault type.** G.2 tests *flagging the pack*. It does not test F's
   4-class diagnosis.

## 2. Definitions (fixed)

**Valid frame.** Current is not the sentinel (|I| < 900 A). All k cells lie in [2.0, 4.5] V (QAS) or
[2000, 4500] mV (DTI); DTI is converted to V.

**Rest frame.** A valid frame with |I| < 1 A.

**Per-cell deviation.** `d_k = V_k − mean_j V_j` per frame, in mV.

**Early window E.** The first 50 % of a vehicle's valid frames, in row order. E is divided into **10 blocks** with
equal counts of rest frames. A vehicle is **eligible** if each block has ≥ 20 rest frames.

**Block value.** For each cell, the median `d_k` over the block's rest frames. The min/max scalars use the same
frames:

- `m = min_k V_k − mean V`
- `s = max_k V_k − min_k V_k`

**Features** (all computed on E only, and all oriented so that larger = more suspicious):

| Feature | Data | Definition |
|---|---|---|
| **A (primary, per-cell drift)** | per-cell | Per cell, the OLS slope of its block values against block index. Robust z of the slopes across the pack: `(slope − median) / (1.4826·MAD)`. **A = −min z**. This is identical in spirit to F §5. |
| **B (primary comparator, min/max drift)** | min/max scalars | **B = −(OLS slope of block-median `m`)**. A scalar monitor could compute this. |
| A_lvl (secondary) | per-cell | −min over cells of the robust z of each cell's median `d_k` over E (a static weak cell) |
| B_lvl (secondary) | min/max scalars | −median `m` over E |
| B_spr (secondary) | min/max scalars | median `s` over E |

## 3. PRIMARY test (QAS only; the one decision)

**Metric.** AUC_A and AUC_B, faulty vs normal, over eligible QAS vehicles. Uncertainty from a **2,000-resample
vehicle bootstrap** stratified by label, seed 0, giving 95 % percentile CIs for AUC_A, AUC_B and AUC_A − AUC_B.

**Power gate.** The test needs **≥ 20 eligible faulty vehicles and ≥ 100 eligible normal ones**; otherwise it is
UNDERPOWERED. At 58 / 335 the AUC SE is about 0.04.

**Decision.** This is F §5 unchanged:

| Verdict | Condition |
|---|---|
| **Per-cell early flagging SUPPORTED over min/max** | AUC_A ≥ 0.70 **and** AUC_A CI lower bound > 0.5 **and** (AUC_A − AUC_B) CI lower bound > 0 |
| **Early flagging exists but per-cell adds nothing resolvable** | AUC_A CI lower bound > 0.5, but the difference CI includes 0 |
| **NOT SUPPORTED** | AUC_A CI includes 0.5 |

There is one extra **report-only** outcome: "**min/max better**", if the upper bound of the difference CI is < 0.

**Prior.** As in F, I expect AUC_A ≈ AUC_B.

## 4. Confound controls (pre-registered; they qualify the verdict but do not change it)

**Negative controls.** These features should not relate to a cell fault. Each is computed on E:

- C1: median temperature;
- C2: median SOC;
- C3: number of valid frames (record length);
- C4: rest-frame fraction;
- C5: median |I| on non-rest frames.

**Confound flag.** If any control's AUC CI excludes [0.35, 0.65], the result is **flagged "cohort-distinguishable"**.
Any SUPPORTED or "exists" verdict then carries the caveat that the labels may be partly predictable from
non-fault differences.

**Adjusted check.** A logistic regression of label on [A, C1..C5] and on [B, C1..C5] (standardised). Report each
coefficient's bootstrap CI for A and for B. A flag-robust signal is a CI excluding 0 with controls in.

## 5. Secondary and descriptive

1. **Late window** (last 50 %). Repeat AUC_A, AUC_B and their difference. Late-minus-early AUC hints at whether the
   signal grows towards the record end, which is consistent with records ending near the failure.
2. **Secondary features** A_lvl, B_lvl and B_spr on E. Report AUCs only; no decision.
3. **Concordance.** For faulty vehicles, how often the A-flagged cell (argmin z) is also the cell most often at `min`
   over E. This is a direct "does min/max already point at the same cell" check, and mirrors F's 98 % overlap.
4. **DTI** (3 faulty): rank of each faulty vehicle's A and B among DTI eligible vehicles. Descriptive; no CI.
5. **Mileage sanity.** Whether vin_1 column 2 is non-decreasing for all vehicles. This only supports the row-order
   assumption.

## 6. Deviations policy

Any change after this commit is listed in the results as a numbered deviation, with the reason, and the verdict is
computed under the pre-registered rule where possible. No threshold changes after seeing results.
