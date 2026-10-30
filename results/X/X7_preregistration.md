# Experiment X7: does a per-cell electro-thermal observer remove hottest-cell temperature margin?

**Brief.** `briefs/X7/README.md`. **Profile:** `X7_profile.md` and `X7/profile.json`.

**Ordering.** This file and the profile are committed **before observer code exists**. `analysis/X7_thermal.py` is not
written. Nothing below runs until the reviewer approves.

**Data.** McMaster 72S, the 14 drive-cycle runs: SB LiMotive 5.2 Ah PHEV cells; 1 Hz; per-cell surface thermistor and
voltage; pack current, with I > 0 = charge. **Licence CC BY 4.0** (Naguib et al., Borealis doi:10.5683/SP3/UYPYDJ).

**Caveat on every verdict:** *surface thermistors on a 72S PHEV pack under drive cycles at ~0.9 SOC; spatial margin, not
core margin.* **Tags:** every output is DERIVED from MEASURED channels. Chamber and cooling conditions are SOURCED.
There are no kWh, cost, range or regulatory claims, and no $/K conversion.

## 0. Status: the power gate has already failed

- **Profile §5:** only 3 of 14 runs have T_hot − T_median ≥ 3 K for ≥ 10 % of frames. The gate needs ≥ 4 per fold.
  **No fold assignment can pass.**
- **Brief §3.5 and §4.4 give the verdict now: UNDERPOWERED. No observer is fitted.**
- The profile also shows a hard ceiling. The thermistors read in **1 K steps**, and the emulated probes' maximum is
  **never more than 1.0 K below T_hot**. So κ_T(M0) = 1.0 K, and Δκ(M0 − M1) ≤ 1.0 K, which equals the decision bar
  and one sensor step.
- **Everything below is filed complete, as the task asks.** It runs only if the reviewer changes §3.5 by a numbered
  deviation.
- **The session's recommendation is not to run it** (profile, note 2). Relaxing the gate would not lift the ceiling.

## 1. Departures from the brief (fixed now)

| # | Brief | X7 | Why |
|---|---|---|---|
| **X7-P1** | The margin outcome is Δκ = κ_T(M0) − κ_T(M1) | **The primary margin outcome is the mean issued bound** `B = mean_t (T̂_hot + κ_T − T_hot)` on evaluation frames, and the decision uses **ΔB = B(M0) − B(M1)**. Δκ is reported beside it, as the brief asks. | κ_T rewards bias. A model whose estimate runs 1 K high gets κ_T = 0 without knowing anything. B is the margin a controller would actually charge to, so it cannot be gamed by an offset. |
| **X7-P2** | Noise floor: "1 Hz thermistor noise at rest" | **Floor = max(median channel SD at rest, q / √12)**, with q = 1 K the thermistor step. That gives **0.29 K**, so **twice the floor is 0.58 K**. | The measured SD at rest is 0.0 K in 26 of 28 windows (profile §5) because the sensor rounds. An SD-only floor would be 0 and vacuous. |
| **X7-P3** | R "as in `X2_replay.py`" | **X2's identification rule, applied within each run only.** R is not pooled across runs in a chamber group, as X2-M did. | X2-M's cross-run pooling crosses the folds. Within-run R keeps every fold independent, and with 246 to 3,565 steps per run (profile §1) no run lacks history for long. |

## 2. Truth and the quantity scored (brief §4.1)

- **Truth:** `CellTemp_R` of every live cell at 1 Hz.
  - Live means not dead under X2's rule. Cells 12 and 35 are dead in HWFET_15C_ModuleBlocked_Long only.
  - `Temp_Est` and `Temp_Smooth` are never read.
- **T_hot(t)** is the maximum over live cells.
- **Error** `e(t) = T_hot − T̂_hot`. Positive means the model under-estimates: the unsafe direction.
- **Frames scored:** all frames from t = 60 s, so every model has had one R block. The first 60 s of each run are
  warm-up and are not scored.

## 3. Models (strictly causal at 1 Hz; forms and parameter counts fixed here)

### 3.1 Shared inputs

**Probes:**

- **Primary:** cells 1, 4, 7, …, 70 (1-indexed), 24 probes. A dead probe moves to the next live cell up.
- **Sensitivity:** the offset layout 2, 5, 8, …; one probe per 2 cells; and every cell.

**Interpolation `P_c(t)`:**

- linear in the live-cell index between neighbouring probes;
- flat beyond the first and last probe (cells 71–72 take cell 70's reading).

**R_c(t) (X7-P3):**

- X2's rule within the run: steps with |ΔI| ≥ 0.3 C between consecutive frames, the pack-mean temperature changing by
  ≤ 1 K, and finite voltages;
- `r_c = ΔV_c / ΔI`, re-estimated every 60 s as the median over steps strictly before the block;
- per-cell values once ≥ 20 steps exist; before that, the pack-mean value from the same steps (1.0 mΩ if there are
  none);
- floor 0.05 mΩ.

**Heat input:** `q_c(t) = I(t)² · R_c(t) / 1000` in W, with R in mΩ.

**Ambient `T_amb`:** the chamber temperature, 15 or 25 °C. This is SOURCED from the file name and is constant within a
run.

### 3.2 M0: the Tier M comparator

- `T̂_c = P_c(t)` and `T̂_hot = max_c T̂_c`. Because interpolation never exceeds its endpoints, this equals the probe
  maximum.
- No fitted parameters other than κ_T.

### 3.3 M1: lumped two-state model per cell, with a fixed-gain observer

Discrete at Δt = 1 s, for each live cell c:

```
Tcore_c ← Tcore_c + [ a · q_c − (Tcore_c − Tsurf_c) ] / τ_c
Tsurf_c ← Tsurf_c + [ (Tcore_c − Tsurf_c) − b · (Tsurf_c − T_amb) ] / τ_s  +  L · ρ_c
```

- **Observer residual ρ_c:**
  - at a probe cell, `ρ_c = T_meas,c − Tsurf_c`;
  - at an unobserved cell, ρ_c is the linear interpolation, along the index, of the probe cells' residuals.
- **Gain:** **L = 0.05 s⁻¹**, a fixed 20 s correction time constant. **Not fitted.**
- **Estimate:** `T̂_c = Tsurf_c`, so the model estimates the surface, which is what truth measures.
- **Initial state:** both states equal P_c at t = 0.
- **Fitted parameters (4, shared by all cells):** a (K per J, scaled), τ_c (s), τ_s (s), b (dimensionless).
- **Fit:**
  - minimise the mean squared surface error at **unobserved** live cells, over all frames of the calibration-fold runs
    from t = 60 s;
  - Nelder–Mead on log-parameters;
  - fixed start a = 1, τ_c = 60, τ_s = 600, b = 1;
  - at most 2,000 evaluations, from that one start.
- **Reported:** the parameter values and the converged loss, per direction.

### 3.4 M2: coupled model

M1 plus two couplings: nearest-neighbour conduction along the index between adjacent live cells (across a dead cell,
the next live neighbours couple), and a common coolant-air node.

```
Tsurf_c ← … + g · (Tsurf_{c−1} + Tsurf_{c+1} − 2 Tsurf_c) / τ_s         (end cells: one neighbour)
          with T_amb replaced by T_air in the b-term
T_air   ← T_air + [ (T_amb − T_air) + h · mean_c (Tsurf_c − T_air) ] / τ_a
```

- **State order:** 2 × (live cells) + 1, i.e. 145 with 72 live cells.
- **Fitted parameters (7):** a, τ_c, τ_s, b, g, h, τ_a.
- **Fit:** as M1, starting from M1's fitted values for the shared parameters, with g = 0.1, h = 0.1 and τ_a = 300.
- **Observer:** the same gain L = 0.05 s⁻¹ and the same residual rule.

### 3.5 M1-sh and M2-sh (shuffle)

- R_c(t) is **permuted across live cells independently at every 1 s step**, using `default_rng(0)` per run, in run
  order.
- The model is **refit** on the shuffled calibration data, with the same procedure and its own κ_T, so that fitting
  cannot favour the real assignment.

## 4. Tasks

**Task A (accuracy).** The p50 and p95 of |e(t)| on evaluation frames, per model, pooled and per run. Reported; not
deciding.

**Task B (margin):**

- **κ_T** is the smallest value on the grid **0.0–10.0 K in 0.1 K steps** such that the fraction of
  **calibration**-fold frames with `T_hot > T̂_hot + κ_T` is **≤ 0.2 %**.
- It is then applied unchanged to the evaluation fold. Reported per model: κ_T, the realised evaluation unsafe
  fraction, **B** (X7-P1) and Δκ.
- **Two directions:** fit on A and score on B, then fit on B and score on A. **The headline is the mean of the two.**
- **CIs:** a run-level bootstrap, 1,000 resamples, seed 0.
  - Δκ: resample calibration runs and re-pick each κ_T. Models are not refit.
  - ΔB: resample evaluation runs at fixed κ_T.
  - The resampling is done within each direction; the two directions' bootstrap means are then averaged.

## 5. Decision (checked in order)

| Verdict | Condition |
|---|---|
| **UNDERPOWERED** | The §3.5 gate fails. **It has already failed (§0).** |
| **NOT INTERPRETABLE** | Any model's realised evaluation unsafe fraction is > **0.3 %** at its calibrated κ_T, in either direction. Margins are reported anyway. |
| **NO MARGIN TO RECOVER** | ΔB(M0 − M1) < **1.0 K**, **or** the hottest value is seen by a probe in > **90 %** of frames (profile: 84 %) |
| **SPATIAL MARGIN RECOVERABLE** | ΔB(M0 − M1) ≥ **1.0 K** with CI lower bound > 0, **and** ΔB(M0 − M1-sh) < **0.5 K** |
| ↳ **TIER M SUFFICES** | SPATIAL MARGIN RECOVERABLE **and** ΔB(M1 − M2) < **0.5 K** |
| ↳ **COUPLING NEEDED** | SPATIAL MARGIN RECOVERABLE **and** ΔB(M1 − M2) ≥ **0.5 K** with CI > 0, **and** ΔB(M2-sh − M2) ≥ 0.5 K |
| **UNCLEAR** | Anything else |

**Floor rule (X7-P2).** Any Δ below **0.58 K** is reported as "below twice the noise floor" and is never called a gain.

**Disclosed in advance (profile §5).**

- κ_T(M0) = 1.0 K in both folds, and M0's estimate is the probe maximum.
- So B(M0) is fixed by the data: 1.0 K minus the mean probe-max gap, about **0.84 K** on the primary layout.
- ΔB(M0 − M1) ≥ 1.0 K would need **B(M1) ≤ about −0.16 K**. That is impossible for a safe bound, because B ≥ 0
  whenever the bound covers T_hot.
- **So SPATIAL MARGIN RECOVERABLE cannot occur on this dataset.** The best possible verdict is NO MARGIN TO RECOVER.
  That is the reason for the recommendation in §0.

## 6. Controls and sensitivity

1. **Shuffle:** M1-sh and M2-sh, as in §3.5.
2. **Held-out runs:** every fitted quantity, including κ_T, is fitted on one fold and scored on the other, in both
   directions.
3. **Best Tier M option:** M0 with a fitted κ_T. M0 sensitivity layouts: one probe per 2 cells, and per cell (the
   ceiling: per-cell M0 should need κ_T = 0.0 K).
4. **Noise floor:** X7-P2.
5. **Sensitivity, each reported with its verdict:**
   - probe layout offset by one cell (2, 5, 8, …);
   - κ_T bar at 0.1 % and 0.5 %;
   - R held fixed from the first 60 s of each run (per-cell if ≥ 20 steps, else the pack mean) instead of being
     re-estimated.

## 7. Outputs (only if run)

- **Code:** `analysis/X7_thermal.py`.
- **Write-up:** `results/X/X7/results_X7.md`, verdict first, with the licence and the surface/spatial caveat.
- **Data:** `x7.json`.
- **Plots:**
  - per run, T_hot against each model's T̂_hot + κ_T;
  - κ_T and B per model, with CIs;
  - ΔB against spread.
- **Also updated:** one row each in `results/X/README.md` and `results/RESEARCH_DOSSIER.md`. Those rows are written
  even if the verdict stays UNDERPOWERED without a run.

## 8. Deviations

Any change after this commit is a numbered deviation. The gate, probe layout, folds, κ grid and bars, model forms,
parameter counts, observer gain and floor never move after results.
