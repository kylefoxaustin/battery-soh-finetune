# Experiment X2-F: a fair comparison of per-cell and min/max charge limiting

**Why this exists.** X2-C ([`X2C/results_X2C.md`](X2C/results_X2C.md)) showed that the X2 design is circular:

- the per-cell limiter carried no margin, and
- "unsafe" was judged against the per-cell limiter itself.

So a per-cell limiter given the **wrong** cells' R gained as much as the real one (11.7 % against 10.8 %). X2-F fixes
both faults. Every limiter gets its own margin, calibrated the same way, and safety is judged against a reference that
none of the limiters sees.

**Ordering.** This file is committed **before any X2-F code exists**. Kyle asked for it on 2026-10-28 ("do both").

**Tags.** All outputs are DERIVED. Every limit is ASSUMED. These are replay limiter currents. No regulatory, economic
or real charge-rate claim will be made.

## 0. Disclosure: this is a pre-registered re-analysis, not a confirmation on unseen data

- **No unseen data with usable steps remains.**
  - Changan was used by X2. It is also too sparse for this design (a median of 7 steps in a 30-day window, so an
    even/odd split leaves too few).
  - Weihai has no steps. BATSS has no prior history.
  - Beihang QAS and DTI were used by X2-C: per-cell R, limiters, κ and S were computed on **both halves**.
- **What is new.** The comparison, the margins and the safety reference. None of them has been computed.
- **What is not new.** The data. X2-C's results are known, so X2-F's result is a **pre-registered re-analysis**. It
  is not independent confirmation, and the write-up will say so in its first paragraph.

## 1. Data, split and frozen inputs (all reused from X2-C, unchanged)

| Item | Value |
|---|---|
| Primary | Beihang **QAS, 335 normal vehicles**, X2-C's split (`X2C/split.json`, seed 0): κ calibrated on the 167-vehicle calibration half, scored on the 168-vehicle evaluation half |
| Secondary (reported, same rules) | Beihang DTI, 77 normal vehicles, same split file |
| Frozen | `X2C/frozen.json`: QAS V_lim 3.51 V, Q_ref 84.4 Ah; DTI V_lim 4.16 V, Q_ref 140.6 Ah (ASSUMED) |
| Definitions | Valid frame, current sign, charge session, step (≥ 0.3·Q_ref, \|ΔT\| ≤ 1 °C, consecutive valid rows), history window (previous 86,400 valid frames), C_T map, Rule D2 floor (0.05 C): **as X2-C §2–3** |
| Licence | CC BY 4.0 |

## 2. The change: disjoint estimation and reference steps

For each session, take the steps strictly inside its history window, **in time order**.

| Set | Steps | Used by |
|---|---|---|
| **E** (estimation) | even-index steps (0, 2, 4, …) | all three limiters: R_k^E (per-cell median), R_mm^E (pack-mean ΔV/ΔI median) |
| **F** (reference) | odd-index steps (1, 3, 5, …) | the safety reference only: R_k^F |

- **History** means at least 20 steps in **each** set (≥ 40 in the window).
- **Sessions without history are excluded** from calibration and scoring. Their count is reported. X2-C's profile
  says this is about 1 %. X2-C's Rule D3 is therefore not needed.
- **R hygiene (as X2-C):** an R_k ≤ 0.05 mΩ or non-finite falls back to the same set's R_mm. An R_mm ≤ 0.05 mΩ falls
  back to the vehicle's median pack-mean R over all its steps.

## 3. Limiters and reference

The per-cell headroom term is `h(V, I, R) = max(V_lim − (V − I·R), 0) / R`. Every limiter is
`max( min(C_T(T)·Q_ref, headroom), 0.05·C·Q_ref )`. Beihang has one temperature column, so the temperature cap is
identical for all of them.

| Limiter | Headroom term | Margin |
|---|---|---|
| **L_ref** (safety reference) | min_k h(V_k, I, R_k^F) | **none** |
| **L_mm(κ_mm)** | h(Vmax, I, R) with R = R_mm^E·κ_mm when Vmax ≤ V_lim, else R_mm^E/κ_mm (X2 Rule D1) | κ_mm |
| **L_cell(κ_c)** | min_k h(V_k, I, R) with R = R_k^E·κ_c when V_k ≤ V_lim, else R_k^E/κ_c (**Rule D1 applied per cell**) | κ_c, its **own** |
| **L_sh(κ_s)** (shuffle control) | as L_cell, with R_k^E permuted across cells: one fixed permutation per vehicle, `default_rng(vehicle ID)`, as X2-C | κ_s, its **own** |

**The safety reference is a per-cell model.** That is deliberate: the physical limit is per cell. Its R comes only
from steps none of the limiters sees. R_k^F is itself an estimate (X2-C split-half ρ 0.99), so "unsafe" means
**exceeds an independent per-cell estimate**, not exceeds the true physical limit.

## 4. Margin calibration (each limiter separately, same rule)

- **Grid:** κ ∈ {1.00, 1.05, …, 3.00}. The grid is wider than X2-C's, because a shuffled limiter may need a large
  margin.
- **Unsafe frame:** L > 1.001·L_ref.
- **Calibration:** for each of L_mm, L_cell and L_sh, κ is the smallest grid value with ≤ **0.1 %** unsafe frames over
  all frames of all history sessions in the **calibration half**. If none qualifies, κ = 3.00 and the limiter is
  flagged.
- **Realised unsafe fraction:** the same statistic over all evaluation-half history-session frames, at the calibrated
  κ, for each limiter.

## 5. Outcome

Per session, with `t = Σ dAh / max(L, 1e-6)` and every limiter at its calibrated κ:

| Quantity | Definition |
|---|---|
| **S** | 1 − t_cell / t_mm |
| **S_sh** | 1 − t_sh / t_mm |
| **D** (paired, per session) | S − S_sh |
| S_ref (reported, ceiling) | 1 − t_ref / t_mm: the gain an exact, margin-free per-cell limiter would get |

**Primary population:** evaluation half, history sessions, ≥ 0.5 Ah, session-max Vmax ≥ V_lim − 50 mV (as X2-C).

**Uncertainty:** 1,000 vehicle-level bootstrap resamples, seed 0, for the medians of S, S_sh and D.

## 6. Decision (QAS evaluation half; checked in this order)

| Verdict | Condition |
|---|---|
| **UNDERPOWERED** | Fewer than 200 primary sessions |
| **NOT INTERPRETABLE** | Any of L_mm, L_cell or L_sh has a realised evaluation-half unsafe fraction > **0.2 %**, or was flagged at κ = 3.00 |
| **NO BENEFIT** | Median S < **1 %** |
| **NOT CONFIRMED (CI)** | Median S ≥ 1 % but the S bootstrap CI lower bound ≤ 0 |
| **CONFIRMED** | Median S ≥ 1 %, S CI lower bound > 0, **and** median D ≥ **1 percentage point** with D CI lower bound > 0 |
| **MECHANISM UNCLEAR** | Median S ≥ 1 % with S CI lower bound > 0, but the D condition fails |

**What CONFIRMED would mean.** With equal, independently calibrated margins, knowing which cell has which R lets a
limiter admit more current than both a pack-scalar limiter and a per-cell limiter with the cells mixed up.

## 7. Reported, not deciding

- The calibrated κ_mm, κ_c and κ_s, with calibration and evaluation κ curves for each.
- Median S among primary sessions above and below V_lim.
- Median S over all evaluation history sessions.
- The binding cell: the fraction of primary frames where L_cell's binding cell is not the max-V cell.
- Counts of excluded sessions (no history).

## 8. Sensitivity (κ recalibrated on the calibration half for each)

| Factor | Values |
|---|---|
| κ unsafe tolerance | 0.01 % and 1 % |
| Step threshold | 0.2 C and 0.5 C |
| Depth band | 25 mV and 100 mV (population only) |
| **Reference from the whole record** | R_k^F from **all odd-index steps of the vehicle's whole record** (past and future), estimation unchanged. This tests whether the result depends on the reference being local in time. |

**DTI** follows the same rules and is reported only.

## 9. Board (only if CONFIRMED)

Port L_cell with κ_c into `board/h_limiter.c` and re-gate on the A55 under H's procedure: hard reservation, census
before and after, 5 repeats, at 110 and 96 cells. Skipped for any other verdict.

## 10. Outputs

- **Code:** `analysis/X2F_replay.py`.
- **Write-up:** `X2F/results_X2F.md`, verdict first, with the re-analysis disclosure in the first paragraph.
- **Data:** `X2F/x2f.json`, plus plots: κ curves for all three limiters, S and S_sh by depth band, the D histogram.
- **Also updated:** `X/README.md` and the dossier §9.

## 11. Deviations

Any change after this commit is a numbered deviation. Thresholds never move.

**Licence:** Beihang is CC BY 4.0, so the verdict is commercially citable.
