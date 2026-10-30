# Experiment X2-S: replication of X2-F on a second LFP dataset (Schaeffer et al., 28 systems)

**Question.** Does X2-F's design, with the settings the fine-grid exploration pointed to, show the per-cell gain and
mechanism on **different** LFP data?

**Data.** Schaeffer et al., 28 LFP systems, zenodo 13715694, **CC BY-NC 4.0**.

**Ordering.** This file, `XS/freeze.json`, `XS/split.json` and `XS/frozen.json` are committed **before any X2-S
limiter code exists**. Kyle approved on 2026-10-29 ("Yes do it my friend").

**What was computed before this file** (`analysis/XS_profile.py`, `analysis/XS_freeze.py`):

- rows, sampling interval, current range and sign;
- current-step counts;
- charge-session depth and history counts;
- balancing activity.

**What was not computed:** per-cell R, any limiter, κ or S.

**Tags.** All outputs are DERIVED. All limits are ASSUMED. Q_ref is SOURCED. These are replay limiter currents only.

## 0. What this can and cannot show (disclosed in advance)

- **New data.** None of the 28 systems has been used by any limiter analysis.
- **Bias.** Every system was returned to the manufacturer for "unsatisfactory behaviour" (dataset README). Several
  charged cells to 3.8–4.1 V. They are **not representative** of healthy packs.
- **Few effective units.**

  | Half | Top-of-charge sessions (within 50 mV) | Of which |
  |---|---|---|
  | Evaluation | 12,570 | systems 6 and 18: 99 % |
  | Calibration | 1,273 | systems 8, 9 and 10: 95 % |

  This is the reason for the cross-fitted, system-weighted design below.
- **Balancing.** Active balancing runs in 0–72 % of charging rows, depending on the system.
- **Small packs.** These are 8S packs, so there are fewer cells for the binding cell to differ from the max-V cell.
- **Reading a null.** A null here is weak evidence against the effect. A positive result means "repeats on a second,
  biased LFP dataset". It is not a fleet-representative confirmation.

## 1. Data, split and frozen inputs

| Item | Value |
|---|---|
| Rows | 5 s on 25 systems; 60 s on systems 24, 25 and 28; 7 s on system 27. Current and the 8 cell voltages are in the same row. |
| Current sign | The file is **charge-positive**. The median pack-mean ΔV/ΔI over steps is positive on all 28 systems (0.21–1.0 mΩ). |
| Split (`XS/split.json`) | **Stratified**: systems ranked by ≥ 0.3 C step count, adjacent ranks paired, one of each pair assigned to each half by a seed-0 coin |
| Calibration half (A) | 1, 3, 4, 8, 9, 10, 11, 14, 16, 17, 20, 22, 23, 27 |
| Evaluation half (B) | 2, 5, 6, 7, 12, 13, 15, 18, 19, 21, 24, 25, 26, 28 |
| **V_lim** | **3,650 mV**, ASSUMED. Rule: p99.5 of the per-frame max cell V over charge-direction frames of half A, rounded down to 10 mV, **capped at 3,650 mV** (a typical LFP charge limit). The uncapped value was 3,762 mV, pulled up by overcharging systems, so the cap binds. |
| **Q_ref** | **160 Ah**, SOURCED from the README ("approx. 160 Ah"). 1 C = 160 A. |
| Temperature | Pack minimum of the 4 sensors, **one value shared by all limiters**, so the temperature cap is identical. C_T map: H's, ASSUMED. |

## 2. Definitions (as in X2-F unless stated)

These are implemented in `analysis/XS_common.py`, which is committed with this file and used unchanged by the
replay.

| Term | Definition |
|---|---|
| **Valid frame** | All 8 cells in (2,000, 4,500) mV, \|I\| < 500 A, finite temperature |
| **Charge session** | Valid rows with I > 1 A. A session breaks on a gap > 60 s or after ≥ 2 non-charge or invalid rows. It must deliver ≥ 0.5 Ah. dAh uses the actual dt, clipped to ≤ 10 s. |
| **Step** | Between consecutive valid rows 0 < dt ≤ 10 s apart, with \|ΔI\| ≥ **0.3 C (48 A)** and \|ΔT\| ≤ 1 °C. **Neither row may be balancing** (any \|I_CNV_Cell_k\| > 10 mA). r_k = ΔV_k / ΔI (mΩ). |
| **History window** | Steps in the previous **30 days** (wall clock) before the session's first row. They are taken in time order: **E** = even-index steps, **F** = odd-index steps. History needs ≥ 20 steps in each set. Sessions without history are excluded and counted. |
| **Session exclusion** | Sessions with session-max cell V **> 3,650 mV** (overcharge) are excluded from calibration and scoring, and counted. |
| **Primary population** | History sessions with session-max cell V ≥ V_lim − 50 mV (and ≤ 3,650 mV) |

## 3. Limiters

The limiters are **exactly X2-F §3**:

- **L_ref**: per-cell, R_k^F, no margin.
- **L_mm(κ_mm)**: Vmax and R_mm^E, Rule D1.
- **L_cell(κ_c)**: per-cell R_k^E, Rule D1 per cell.
- **L_sh(κ_s)**: as L_cell with R_k^E permuted once per system, `default_rng(system ID)`.

The 0.05 C floor (8 A) and R hygiene are as X2-F.

## 4. Margin calibration: two-fold cross-fitting

- **Grid:** κ ∈ {1.00, 1.01, …, 2.00} (step 0.01). A κ at 2.00 that still fails is flagged.
- **Unsafe frame:** L > 1.001·L_ref.
- **Fold 1:** κ_mm, κ_c and κ_s are each calibrated on all history-session frames of half **A**, at **≤ 0.01 %**
  unsafe. Half **B** is scored.
- **Fold 2:** the same with A and B swapped.
- **Realised held-out unsafe fraction:** for each limiter in each fold, on the scored half's history-session frames.

Every system is scored exactly once, by margins it did not help set.

## 5. Outcome and statistics

Per session, at the fold's calibrated κ, with `t = Σ dAh / max(L, 1e-6)`:

| Quantity | Definition |
|---|---|
| S | 1 − t_cell / t_mm |
| S_sh | 1 − t_sh / t_mm |
| D | S − S_sh |

**Qualifying system:** at least 20 primary sessions in its scored fold.

**Primary statistics, each system weighted equally:**

- **S_sys** = the median over qualifying systems of each system's median S;
- **D_sys** = the same for D;
- **95 % CI:** 2,000 system-level bootstrap resamples, seed 0.

**Sign count:** the number of qualifying systems with system-median D > 0.

**Also reported, not deciding:**

- session-pooled medians of S, S_sh and D, as in X2-F;
- per-system medians;
- each fold separately;
- the calibrated κ values;
- S_ref;
- the fraction of frames where the binding cell is not the max-V cell;
- leave-one-system-out S_sys.

## 6. Decision (checked in this order)

| Verdict | Condition |
|---|---|
| **UNDERPOWERED** | Fewer than **6** qualifying systems across both folds, or fewer than 200 primary sessions. The freeze counts give 8 systems with ≥ 20 sessions (4 per half). |
| **NOT INTERPRETABLE** | In either fold, any limiter's realised held-out unsafe fraction is > **0.2 %**, or any κ is flagged |
| **NO BENEFIT** | S_sys < **1 %** |
| **NOT CONFIRMED (CI)** | S_sys ≥ 1 % but the CI lower bound ≤ 0 |
| **REPLICATED** | S_sys ≥ 1 %, CI lower bound > 0, D_sys ≥ **1 pp** with CI lower bound > 0, **and** D > 0 in ≥ 75 % of qualifying systems |
| **MECHANISM UNCLEAR** | S_sys ≥ 1 % with CI lower bound > 0, but the D conditions fail |

## 7. Sensitivity (κ recalibrated per fold for each)

| Factor | Values |
|---|---|
| κ tolerance | 0.1 % (X2-F's rule) |
| History window | 7 days |
| Balancing rows | Allowed in steps |
| Step threshold | 0.2 C |
| Depth band | 25 and 100 mV (population only) |

## 8. Board

There is no board run, whatever the verdict. CC BY-NC data and a biased, returned-unit population cannot justify
porting.

## 9. Outputs

- **Code:** `analysis/XS_replay.py`.
- **Write-up:** `XS/results_X2S.md`, verdict first, with §0's caveats in its first paragraph.
- **Data:** `XS/x2s.json` and `XS/x2s_plots.png`.
- **Also updated:** `X/README.md` and the dossier.

## 10. Deviations

Any change after this commit is a numbered deviation. Thresholds never move.
