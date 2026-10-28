# Experiment X2-C: pre-registered confirmation of the per-cell-history charge-limit gain

**Source brief:** *Build Brief — Experiment X2-C* (rev 6, 2026-10-28; not included).

**What X2-C asks.** On data never used for a limiter, does a per-cell limiter that uses each cell's history-derived R
admit more charge current than an equally safe min/max limiter, in the sessions where the voltage-headroom term can
bind? κ is calibrated on vehicles that are not scored.

**Ordering.** This file and [`X2C_profile.md`](X2C_profile.md) are committed **before any X2-C limiter code
exists**. The profile script (`analysis/X2C_profile.py`) computes no limiter quantity.

**Tags.** All outputs are DERIVED. Every limit (C_T map, V_lim, Q_ref) is ASSUMED. Results are replay limiter
currents. No regulatory, economic or real charge-rate claim will be made.

## 0. Disclosure: what has and has not been seen

**Beihang (primary data):**

- **G.2** computed rest-frame per-cell voltage deviations, slopes and min/max scalars on QAS and DTI. It also read raw
  rows of a handful of vehicles.
- **The review** found the 58 faulty QAS records were processed differently, and that the `z` columns are not
  temperatures.
- **This profile** computed frames, steps, sessions, charge depth, V_lim and Q_ref (see `X2C_profile.md`).
- **Never computed on Beihang:** per-cell R, any limiter value, κ, S, or any binding-cell statistic.

**The prior (seen):**

- X2 on Changan, post-hoc: median **+5.5 %** in history sessions (CI 4.7–6.4 %), κ_mm 1.65.
- The gain tracks how often headroom binds (X2-M2), and X2's 20-step R was noisy (X2-P: ρ 0.85).

**Profile facts that shape the design:**

- QAS looks like **LFP** (V_lim 3.51 V). That is inferred from voltages, not stated by the source.
- Steps are plentiful, and about 99 % of sessions have history in any window.
- Charge depth is bimodal: about 14 % of sessions reach V_lim.

## 1. Data and arms

| Arm | Data | Role | Licence |
|---|---|---|---|
| **X2-C primary** | Beihang **QAS, 335 normal vehicles**; scored on the 168-vehicle **evaluation half** | Verdict | CC BY 4.0 |
| X2-C-DTI | Beihang DTI, 77 normal vehicles (38 / 39 split) | Secondary, same rules, reported | CC BY 4.0 |
| X2-C-McM | McMaster 72S with the SOURCED power-cell map | **Carried over from X2-M2, not re-run.** Already run on 2026-10-16 (0.00 % at 6 C, descriptive). Re-running it would not be a confirmation. The brief's DOI 10.5683/SP3/THZTJC resolves to the same dataset as UYPYDJ (checked). | CC BY 4.0 |
| X2-C-BatICM | BatICM car1 (1 s, 96 V) and car4 (30 s, 87 V) | Report-only case study on sampling interval and R estimation | MIT |

**Not used:** Changan (all sessions seen), Weihai (no steps), BATSS (no prior history), and the 58 faulty QAS
vehicles. The faulty vehicles are **not reported**; the brief's optional cohort report is not taken up.

**Frozen inputs** (`X2C/frozen.json`, calibration half, ASSUMED):

| Fleet | V_lim | Q_ref |
|---|---|---|
| QAS | **3.51 V** | **84.4 Ah** |
| DTI | **4.16 V** | **140.6 Ah** |

**Vehicle split:** `X2C/split.json`, seed 0, made before anything else was loaded.

## 2. Definitions (fixed)

| Term | Definition |
|---|---|
| **Valid frame** | |I| < 900 A, every cell in [2.0, 4.5] V, finite temperature |
| **Current sign** | The file's discharge-positive I is negated to charge-positive |
| **Charge session** | Consecutive valid rows with charge current > 1 A (OPEN-P1), ending after ≥ 2 non-charge or invalid rows (OPEN-P2), ≥ 0.5 Ah. ΔAh assumes 30 s rows. |
| **Step (OPEN-1)** | Between **consecutive valid rows** only: \|ΔI\| ≥ 0.3·Q_ref and \|ΔT\| ≤ 1 °C. r_k = ΔV_k / ΔI (charge-positive), in mΩ. |
| **History window** | The previous **86,400 valid frames** before the session's first frame (brief §4.2). R_k is the median of r_k over steps strictly inside the window. ≥ 20 steps means "history"; otherwise rule D3 applies. |
| **R_mm** | Median over the same steps of pack-mean ΔV / ΔI (the X2 definition) |
| **Primary population** | Sessions with history, ≥ 0.5 Ah, and **session-max Vmax ≥ V_lim − 50 mV**, which includes sessions above V_lim |

**Temperature.** Beihang has **one** temperature column, so the temperature cap is identical for both limiters. **This
isolates the resistance mechanism.**

## 3. Limiters (X2 formulas; X2's deviations adopted as rules)

`I_k = min( C_T(T)·Q_ref , (V_lim − V_k + I·R_k) / R_k )`, with H's C_T map unchanged (ASSUMED).

| Limiter | Definition |
|---|---|
| **L_cell,hist** | min_k I_k |
| **L_mm,hist** | min( C_T(T)·Q_ref , (V_lim − Vmax + I·R)/R ), with R = R_mm·κ when Vmax ≤ V_lim and R_mm/κ above (**Rule D1**) |

- **Rule D2:** both limiters are floored at 0.05 C·Q_ref.
- **Rule D3:** a session without history gives the per-cell limiter min/max's uniform R and κ.
- **R hygiene (as X2):** R_k ≤ 0.05 mΩ or non-finite falls back to R_mm. R_mm ≤ 0.05 mΩ falls back to the vehicle's
  median R_mm over all its steps.

## 4. κ calibration on held-out vehicles

- **Calibration frames:** all frames of all sessions (any depth, with or without history) in the **calibration half**.
- **κ_mm** is the smallest value in {1.00, 1.05, …, 2.00} for which L_mm,hist > 1.001·L_cell,hist in ≤ **0.1 %** of
  those frames. If none qualifies, κ = 2.00 and the result is flagged.
- **Score on the evaluation half only.**
- **Realised unsafe fraction:** the same statistic on all evaluation-half session frames, at the calibration κ. It is
  also reported within primary-population frames.
- κ calibrated on the evaluation half is reported **for comparison only**.

## 5. Outcome and controls

**Outcome.** Per session, `S = 1 − t_cell,hist / t_mm,hist`, with `t = Σ dAh / max(L, 1e-6)`, at the calibration κ.

**Controls (all on the evaluation half, primary population):**

1. **Binding cell.** The fraction of frames where the binding cell under L_cell,hist is not the max-V cell
   (tie-aware).
2. **Shuffle.**
   - Each vehicle gets one fixed random permutation (seed 0 + vehicle ID), applied to its R_k vector at every
     session. L_cell is recomputed, then S_shuffle against the **same** L_mm and κ.
   - **Pre-registered expectation (the brief's):** median S_shuffle < 1 %.
   - **Disclosed prior to the contrary:** the per-cell limiter carries **no κ margin**, so shuffled R values with the
     same distribution may keep much of the gain. If so, the verdict is MECHANISM UNCLEAR, and that is a valid result.
   - Also reported: the shuffled limiter's unsafe fraction against the true per-cell limiter.
3. **Split-half stability** (as X2 §2b, per vehicle, all steps). R_k is estimated from even-index and odd-index steps
   separately: Spearman ρ across cells, and the same worst cell. Reported against X2-P's Changan figures.

## 6. Primary decision (QAS evaluation half; checked in this order)

| Verdict | Condition |
|---|---|
| **UNDERPOWERED** | Fewer than 200 primary-population sessions in the evaluation half. The profile shows 1,621, so this is not expected. |
| **NOT INTERPRETABLE** | Realised unsafe fraction on the evaluation half > **0.2 %** |
| **CONFIRMED** | Median S ≥ **1 %** **and** vehicle-bootstrap CI lower bound > 0 **and** shuffle median S < **1 %** |
| **NOT CONFIRMED** | Median S < 1 % |
| **MECHANISM UNCLEAR** | Median S ≥ 1 % but shuffle median S ≥ 1 % |

**Edge case.** Median S ≥ 1 % with the CI lower bound ≤ 0, and the shuffle < 1 %, fits no row. It is reported as
**NOT CONFIRMED (CI)**, and that is disclosed here.

**Uncertainty.** 1,000 vehicle-level bootstrap resamples, seed 0.

**Also reported, not deciding:**

- median S over all evaluation sessions (not a headline);
- S among primary sessions **above** V_lim and **below** it.

**DTI** follows the same rules and is reported only.

## 7. Sensitivity (pre-registered; κ recalibrated on the calibration half for each)

| Factor | Values |
|---|---|
| History window | 20,160 and 259,200 frames. Expected to be identical to the base, because records are about 33 k rows (profile §4). |
| Step threshold | 0.2 C and 0.5 C |
| Depth band | 25 mV and 100 mV, population only |
| V_lim | ±20 mV, limiter and population |
| κ unsafe tolerance | 0.01 % and 1 % |

## 8. BatICM report-only (sampling interval)

- **car1, 1 s:** R_k from steps with |ΔI| ≥ 0.3 C (ASSUMED 50 Ah, as X3 DEV-1) at native 1 s. Again after decimating
  to every 30th row.
- Reported:
  - median R_k level;
  - Spearman ρ of R_k between 1 s and 30 s;
  - the same worst cell.
- **car4, 30 s:** split-half stability only.
- car1 is 1.6 days long, so this is a case study only.

## 9. Board (only if CONFIRMED)

Port R_k into `board/h_limiter.c` and re-gate on the A55 under H's procedure: hard reservation, census before and
after, 5 repeats, at 110 and 96 cells. Skipped for any other verdict.

## 10. Outputs

**Write-up:** `X2C/results_X2C.md`, with the verdict first.

**Plots:**

- S by depth band;
- κ curves for the calibration and evaluation halves;
- shuffle against real.

**Also updated:** `X/README.md` and the dossier §9.

## 11. Deviations

Any change after this commit is a numbered deviation. Thresholds never move.

**Licence:** CC BY 4.0 for Beihang and McMaster, MIT for BatICM. X2-C uses no Changan data, so the verdict is
commercially citable.
