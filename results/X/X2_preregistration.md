# Experiment X2 (H3) — pre-registration: per-cell limiting with per-cell parameters learned from history

**What X2 asks.** Does a charge-direction limiter whose **per-cell resistance (and, secondarily, capacity) are
estimated from each cell's own past data** allow more current or a shorter charge than a min/max limiter? The min/max
limiter is given the same history, but only as pack-level scalars, and must stay equally safe.

**Origin.** Kyle's brief §5 X2 ([`README.md`](README.md)). Approved to draft 2026-10-15; **running X2 needs Kyle's
go-ahead**.

**Ordering.** This file is committed **before** any X2 analysis code exists. `analysis/H_replay.py` (H) exists and is
reused.

**Tags.** As in H: every number is DERIVED, and every limit is ASSUMED. No regulatory, economic or real charge-rate
claim will be made.

## 0. What is known in advance (disclosure)

- **Already seen:**
  - H and H2 results, and the review's post-hoc per-cell-R limiter: median +2.0 % admissible current at vmax ≥ 4.0 V
    on 38 Changan vehicles (`review_2026-10-15/h_report.md`). The main session has **not** re-checked that figure.
  - The McMaster and BATSS probes in [`README.md`](README.md): McMaster's spread is at most 11 °C, with dead
    thermistors at cells 12 and 35 in the module-blocked run; McMaster has only regen charging; BATSS thermocouple
    mapping is unknown.
  - Changan has 2,855 sessions with coldest probe < 10 °C.
- **Not yet computed for any X2 dataset:** per-cell R or capacity, any limiter value, any saving.
- **Why H could not show a benefit.** H's design gives `L_cell ≥ L_mm` by construction, with one shared map. X2
  changes exactly that: cells differ through their own estimated R_k and Q_k.

## 1. Datasets and arms

| Arm | Data | Regime | Metric | Licence |
|---|---|---|---|---|
| **X2-C (primary)** | Changan per-cell (`data/changan/cells`), charge sessions with session-median coldest probe < 10 °C | Cold, real charging, NMC 96s | Session charge-time saving | CC BY-NC-SA (non-commercial) |
| X2-C-all | Same, all charge sessions | All | Same | Same |
| X2-M | McMaster 72S, all 14 drive-cycle runs, 1 Hz | Hot to 46 °C; regen near 4.2 V; per-cell thermistors (mapping known) | Mean admissible regen current over charge-direction frames | CC BY 4.0 |
| X2-B (report-only) | BATSS fast-charge runs 16–19 | Hot to 79 °C | Session charge-time saving, under H's M1 / M2 thermocouple mapping | CC BY 4.0 |

**McMaster exclusions.** In the module-blocked run, cells 12 and 35 are excluded from the temperature input. Their
thermistors read a constant 1.0 °C. Each cell instead takes the median of its two string neighbours. The same rule
applies to any channel whose temperature never changes during a run.

## 2. Estimating per-cell parameters from history (causal only)

**Per-cell resistance R_k.**

- At each current step with |ΔI| ≥ 0.3 C between consecutive frames, and |ΔT| ≤ 1 °C:
  `r_k = −ΔV_k / ΔI` (charge-positive convention after sign normalisation).
- R_k(t) is the **median of r_k over the trailing window** W_R, using only steps strictly before t:
  - Changan: W_R is the previous 30 days of the vehicle's record.
  - McMaster and BATSS: W_R is the earlier part of the same run, or of earlier runs at the same chamber temperature,
    in file order.
- At least 20 steps are required. Otherwise R_k falls back to the pack-median R, and that frame counts as "no
  history".

**Per-cell capacity Q_k (secondary arm only; Changan only).**

- Q_k is the per-cell ΔAh between two rests (> 1 h) divided by the cell's ΔSOC from H's ASSUMED OCV table.
- It uses the trailing 90 days, needs at least 3 rest pairs, and must have ΔSOC ≥ 20 %.

**Sign conventions:**

| Dataset | Convention |
|---|---|
| McMaster | I > 0 is charge (verified: dV/dI < 0 for I > 0) |
| Changan | I > 0 is discharge, as in H |
| BATSS | Charge current is positive in CC-CV steps |

All are normalised to charge-positive before use.

## 3. The limiters, per frame

**Charge-direction admissible current** for cell k:

`I_k = min( C_T(T_k) · Q_ref , (V_lim − V_k + I·R_k) / R_k )`

- `C_T` is H's temperature map. It is ASSUMED and unchanged.
- `Q_ref` is the nominal capacity.
- `V_lim` is the cell limit: 4.20 V for Changan and McMaster, 4.20 V for BATSS.
- The second term is the voltage-headroom limit, using the cell's open-circuit estimate `V_k − I·R_k` at the current
  frame current I.

**The four limiters:**

| Limiter | Definition |
|---|---|
| **L_cell,hist** (per-cell with history) | `min_k I_k` with each cell's own R_k(t) and its own probe temperature. In the secondary arm, `Q_ref` becomes `Q_k`. |
| **L_mm,hist** (min/max with history, the fair comparator) | `min( C_T(Tmin)·Q_ref, C_T(Tmax)·Q_ref, (V_lim − Vmax + I·R_mm)/R_mm )` |
| L_mm (H's) | Reported for continuity |
| L_cell,uniform (H's) | Reported for continuity |

**How R_mm is set.** R_mm is the pack-level R estimated from pack ΔV/ΔI over the same trailing window, divided by N,
times a safety factor κ_mm. κ_mm is the **smallest** value in {1.00, 1.05, …, 2.00} for which L_mm,hist exceeds
L_cell,hist in at most 0.1 % of the dataset's charge-direction frames. This is H's unsafe-frame criterion.

**Why this comparator is fair.** A min/max BMS does not know which cell has the highest R, so it must carry margin. κ_mm
is calibrated on the same data, which favours min/max. That is deliberate, and it can only make a per-cell benefit
harder to show.

**Probe mapping.**

- McMaster: known, one thermistor per cell.
- Changan: H's M1 (⌊k/3⌋), plus M2 (100 permutations).
- BATSS: M1 is a contiguous split of the 55 thermocouples across 10 cells; M2 is 100 permutations. Both are ASSUMED.

## 4. Outcome measures

| Arm | Primary measure |
|---|---|
| X2-C, X2-C-all, X2-B | `S = 1 − t_cell,hist / t_mm,hist` per session, with `t = Σ dAh / max(L, 1e-6)` as in H. Sessions < 0.5 Ah skipped. |
| X2-M | `G = mean(L_cell,hist) / mean(L_mm,hist) − 1` over charge-direction frames (I > 0.05 C), per run |

**Secondary measures (all arms):**

- The fraction of frames where the binding cell under L_cell,hist is **not** the max-V cell and **not** on the
  hottest or coldest probe. This is the "information min/max cannot carry" control from H, made tie-aware.
- κ_mm itself.
- Results by real temperature-spread band: < 5, 5–10, 10–20, > 20 °C. Empty bands are reported as empty.

## 5. PRIMARY decision (X2-C cold arm; same rule as H)

| Verdict | Condition |
|---|---|
| **NO BENEFIT from per-cell history** | Median session S < 1 % under M1 **and** under the M2 median |
| **PER-CELL HISTORY RECOVERS X** | Median S ≥ 1 % under M1 **and** the M2 median, with the M1 bootstrap CI lower bound > 0 |
| **MAPPING-DEPENDENT** | Any other outcome |
| **UNDERPOWERED** (checked first) | Fewer than 200 cold sessions have ≥ 20 R-steps of history |

**Uncertainty.** Bootstrap 1,000 resamples (seed 0), resampling vehicles.

**Secondary verdicts** (X2-C-all, X2-M; X2-B is report-only):

- Same thresholds.
- For X2-M, the rule is applied to the median over the 14 runs of G, with a run-level bootstrap.
- With 14 runs, X2-M is descriptive if the CI spans 0.

## 6. Sensitivity (pre-registered)

- W_R of 7 and 90 days (Changan).
- Step threshold of 0.2 C and 0.5 C.
- `C_T` breakpoints shifted ±5 °C.
- κ_mm unsafe tolerance of 0.01 % and 1 %.

## 7. Gate and board (optional)

**Gate.** If X2 finds a benefit, the per-cell-history limiter is ported to `board/h_limiter.c` as an R_k array: 4 B
per cell, and already resident in H's 10 B per cell. It is then re-gated on the FRDM under H's procedure:

- hard reservation;
- census before and after;
- 5 repeats;
- argmin tie-aware 100 %.

**Board latency** would be MEASURED. Without a benefit, no board run.

## 8. Deviations policy

Any change after this commit is a numbered deviation in the results file, with its reason. Thresholds are never moved
after results are seen.

**Licence.** X2-C is non-commercial (Changan). X2-M and X2-B are CC BY 4.0.
