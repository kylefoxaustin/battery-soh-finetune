# Experiment X8 pre-registration: the bottom reserve

**Question.** On low-SOC discharge frames, how much more discharge current does a per-cell-R limiter admit than a
min/max limiter, at equal held-out safety against an independent per-cell reference? Does the gain survive a shuffle of
cell identity?

**Status of this file.**
- Brief: `briefs/X8/README.md`. Profile: [`X8_profile.md`](X8_profile.md).
- Committed together with the profile **before any limiter or scoring code exists.** The only code so far is the
  loader `data/changan_lowsoc.py` and `analysis/X8_profile.py`; neither computes a limiter quantity.
- Requested by NEXT_TASK (reviewer, 2026-11-06), step 2.
- It mirrors `X2F_preregistration.md`. Every departure from X2-F is named.

**Tags.**
- Every output is **DERIVED**. V_cut, 1 C and every limit are **ASSUMED**: these are replay currents, not discharge
  ratings.
- No kWh, range, cost or C2 percentage will be computed (brief §6).

**Caveat carried onto every verdict.** *Changan, CC BY-NC-SA, research only; NMC; 10 s telemetry; warm-climate fleet;
the limits are ASSUMED replay quantities.*

---

## 0. What is new and what is not

- **New data use.** Low-SOC **discharge** frames. No programme experiment has scored them on any fleet: X2, X2-C and
  X2-F used charging frames only.
- **The step source is also new.** Changan per-cell steps exist at the bottom only because of the new every-frame
  loader.
- **Known facts.** The profile is known (`X8_profile.md`), including that the minimum-voltage cell is rarely the
  highest-R cell (median 2 %).
- **Known to fail elsewhere.** On Beihang QAS, min/max's margin failed to transfer at the top of charge (X2-F).
- **Nothing limiter-side has been computed** on any of these frames.

## 1. Data, populations and fixed inputs

| Item | Changan (primary) | Beihang DTI (replication) | Beihang QAS (replication) |
|---|---|---|---|
| Source | `data/changan/lowsoc/` (every frame, SOC < 30 %) | `vin_2.pkl` via `X2C_profile.load` (restricted unpickler) | same |
| Vehicles | 300 | 77 normal | 335 normal |
| Licence | CC BY-NC-SA 4.0 | CC BY 4.0 | CC BY 4.0 |
| Chemistry | NMC | NMC | LFP |
| Frame period | 10 s (timestamps) | 30 s (no timestamps; as X2-C) | 30 s |
| Valid frame | sync **and** every cell 2.0–4.5 V | X2-C validity | X2-C validity |
| **Discharge frame** (source sign) | I > 1 A (discharge-positive source) and status ≠ 1 | charge-positive I < −1 A | same |
| **V_cut** (ASSUMED; p0.1 of discharge-frame minimum cell, rounded down to 10 mV) | **3,350 mV** | **2,900 mV** | **2,840 mV** |
| **1 C** (ASSUMED) | 120 A (X2 OPEN-3) | Q_ref 140.6 Ah (X2-C frozen) | Q_ref 84.4 Ah (X2-C frozen) |
| Folds | `X8/split.json` "changan" | `X8/split.json` "beihang/DTI" | `X8/split.json` "beihang/QAS" |

**Sessions.**
- A **session** is a discharge segment: a run of contiguous discharge frames with gaps ≤ 30 s (Changan) or
  consecutive rows (Beihang), at least 6 frames long.
- Its **scored frames** are its frames at SOC < 20 %.

## 2. Identification and the disjoint step sets (as X2-F, at the bottom)

**Step definition.**
- Consecutive valid frames, ≤ 30 s apart (Changan) or adjacent rows (Beihang).
- Both frames non-charging: status ≠ 1 (Changan) or charge-positive I < 1 A (Beihang).
- |ΔI| ≥ **0.3 C**.
- Pack-mean temperature change ≤ **1 K**.
- The later frame at SOC < **30 %**.
- Per step: **r_c = ΔV_c / ΔI_charge-positive** (mΩ) for each cell, and the pack-mean step R **r_p = Δ(mean-cell V) / ΔI**.

**History window.**
- The steps strictly before the session's first frame, within **30 days** (Changan, by timestamp) or **86,400
  frames** (Beihang), taken in time order.
- **E** = even-index steps; all three limiters use them:
  - R_c^E = per-cell median;
  - R_pack^E = median of r_p, i.e. the pack ΔV/ΔI divided by cell count.
- **F** = odd-index steps; only the reference uses them: R_c^F.
- **History** means ≥ **20** steps in each set. Sessions without history are excluded, and their count is reported.

**R hygiene (as X2-F).**
- R_c ≤ 0.05 mΩ, or non-finite, falls back to the same set's R_pack.
- R_pack ≤ 0.05 mΩ falls back to the vehicle's median r_p over all of its low-SOC steps.

R is held for the whole session: it is estimated once, at session start.

## 3. Reference and limiters

Notation:
- V in mV; R in mΩ; currents in A, as **discharge magnitudes**;
- I_t = the present discharge current;
- `E_c(t) = V_c(t) + I_t · R_c`, the cell's estimated open-circuit voltage;
- every admissible current is clamped at ≥ 0. There is no floor (departure from X2-F's 0.05 C floor, which was a
  charge-taper artefact).

| Quantity | Formula | Margin |
|---|---|---|
| **Reference** I_ref(t) | min_c (V_c + I_t R_c^F − V_cut) / R_c^F | **none** |
| **Per-cell** I_cell(t; κ_c) | min_c (V_c + I_t R_c^E − V_cut) / (κ_c R_c^E) | κ_c |
| **Min/max (Tier M comparator)** I_mm(t; κ_mm) | (V_min + I_t R_pack^E − V_cut) / (κ_mm R_pack^E) | κ_mm |
| **Shuffled per-cell** I_sh(t; κ_s) | as per-cell, with R_c^E **permuted across cells at every frame** (fresh permutation per frame; `default_rng([vehicle, frame index])`) | κ_s |

The κ multiplies only the resistance in the denominator, not the estimate of E_c, exactly as brief §4.3.

**Horizon (CHOSEN reading of brief §4.1 "at the 10 s horizon").** A limit issued at t must hold until the next frame.
- **Unsafe frame:** I_adm(t) > **1.001** · min(I_ref(t), I_ref(t+1)). The 1.001 is X2-F's float tolerance.
- t+1 is the next frame of the same session. At a session's last frame, only I_ref(t) is used.
- On Beihang, "the next frame" is 30 s; this is disclosed as a horizon difference, not adjusted.

## 4. Margin calibration (each limiter separately, same rule)

- **Grid:** κ ∈ {1.00, 1.01, …, 2.00} (0.01 steps, brief §4.3).
- **Calibration:** κ is the smallest grid value with an unsafe fraction ≤ **0.05 %** over all scored frames of all
  history sessions in the calibration half. If none qualifies, κ = 2.00 and the limiter is **flagged**.
- **Held-out safety:** the unsafe fraction at that κ over the other half's scored frames. **Bar 0.2 %.**
- **Both directions:** A→B and B→A.
- Both curves (calibration and held-out unsafe fraction at every κ) are reported for every limiter: the margin table.

## 5. Outcomes

Each session uses the limiters at their calibrated κ, over its scored frames.

| Quantity | Definition |
|---|---|
| **S_s** | Σ_t I_cell / Σ_t I_mm − 1. Sessions with Σ I_mm = 0 are excluded and counted. |
| **S_sh,s** | Σ_t I_sh / Σ_t I_mm − 1 |
| **D_s** (paired) | S_s − S_sh,s |
| S_ref,s (ceiling, reported) | Σ I_ref / Σ I_mm − 1 |

**Aggregation.**
- **S, S_sh, D** = the median over the evaluation half's history sessions, computed in each fold direction and then
  **averaged across the two directions**.
- **CIs:** 1,000 vehicle-bootstrap resamples (seed 0), resampling vehicles within each evaluation half. The statistic
  is the direction-averaged median; the CI is its 2.5–97.5 percentiles.

**Reported, not deciding.**
- Each limiter's κ in each direction, and whether min/max's (and each limiter's) margin transferred to the held-out
  half.
- The fraction of scored frames where the per-cell limiter's **binding cell is not the minimum-voltage cell**.
- The fraction of scored frames with I_ref = 0.
- S, S_sh and D on the **SOC < 10 %** and **cold (coldest probe < 10 °C; Beihang: its one temperature < 10 °C)**
  subsets, with the same κ. These are descriptive if a subset has fewer than 10 vehicles.
- **Usable depth (DERIVED, not kWh).** Per session and limiter, the highest SOC at which the admissible current is
  below the session's p95 discharge current. Reported as a median per limiter, together with the fraction of sessions
  where this never happens.

## 6. Decision (Changan; both fold directions averaged; checked in this order)

| Verdict | Condition |
|---|---|
| **UNDERPOWERED** | Profile resolution gate (≥ 10 LSB at the admitted-current approximation) or power gate (≥ 30 vehicles with ≥ 20 scored frames with history) fails. *At the profile: both pass (36.8 LSB; 300 vehicles).* |
| **NOT INTERPRETABLE** | Any limiter's held-out unsafe fraction > **0.2 %** in **either** direction, or any limiter flagged at κ = 2.00. The margin table is reported anyway. |
| **PER-CELL HELPS AT THE BOTTOM** | S ≥ **1 %** with CI lower bound > 0, **and** D ≥ **1 pp** with CI lower bound > 0 |
| **NO BENEFIT** | S < 1 % with CI upper bound < 1 %, **or** median S_sh ≥ median S |
| **UNCLEAR** | anything else |

**Replication arms.**
- **DTI first, then QAS.** Each takes the same rules, its own V_cut and folds, and its own gates. Each is reported as
  its own verdict, citable under CC BY.
- **A replication never overturns the Changan verdict.** Agreement or disagreement is stated in words.

## 7. Controls and sensitivity (κ recalibrated for each; none deciding)

1. **Shuffle control** with its own κ (§3).
2. **Held-out vehicles**, both fold directions (§4).
3. **Best Tier M option.** Min/max with a pack-level R and a fitted margin (the comparator itself).
4. **Sensitivity:**
   - V_cut **3,300 and 3,400 mV** (Beihang ± 50 mV);
   - horizon **20 s**: min over t, t+1, t+2 (Changan only);
   - R **re-estimated per session** (primary) against R **held from the vehicle's first 20 E and 20 F low-SOC steps**
     for the whole record;
   - unsafe calibration bar **0.1 %** and **0.5 %**;
   - the SOC < 10 % and cold subsets (§5).
5. **Resolution (dither) check.**
   - Every cell voltage (frames and steps) gets uniform ±0.5 LSB noise (`default_rng(0)`), and the whole primary is
     repeated, κ calibration included.
   - **If S moves by more than its CI width, the result is labelled rounding** and the verdict carries that label.
   - The profile makes this binding, not decorative: the per-cell R difference the limiter exploits is about 10 LSB.

## 8. Outputs (after approval)

- **Code:** `analysis/X8_bottom.py`.
- **Write-up:** `results/X/X8/results_X8.md`. Verdict first, with the NC-SA caveat, chemistry, the margin table, S
  beside S_sh and D, and the replication arms.
- **Data:** `x8.json`.
- **Plots:**
  - κ against unsafe fraction per limiter (calibration and held-out, both directions);
  - the S distribution;
  - one session's admissible currents.
- **Also updated:** one row each in `results/X/README.md` and `results/RESEARCH_DOSSIER.md` §9, and a dated note under
  ANGLES §1.1 / §B.

## 9. Deviations

Any change after this commit is a numbered deviation (X8-D1, …). V_cut, the κ grid, the bars, the horizon, the folds
and the decision thresholds never move after results are seen.
