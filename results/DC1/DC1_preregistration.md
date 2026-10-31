# Experiment DC1: does remembering the last seconds of an AI-training load shrink the storage that holds it inside a ramp spec?

**Brief.** [`briefs/DC1/README.md`](../../briefs/DC1/README.md). **Profile:** [`DC1_profile.md`](DC1_profile.md) and
[`profile.json`](profile.json).

**Ordering.** This file and the profile are committed **before controller code exists**.
`analysis/DC1_storage.py` is not written, and nothing below runs until the reviewer approves.

**Data.**

- NLR *Dataset of Generative AI Workload Power Profiles* (OpenEI 8651, DOI 10.7799/3025227), **CC BY 4.0**, plus the
  DOE/NLR/Alliance catalogue notice ([`LICENCE_record.txt`](LICENCE_record.txt)). Credit DOE/NLR/ALLIANCE and cite
  arXiv:2604.07345.
- The unit is each multi-node training job's total power: the provider's per-job aggregate at 0.2 s, cross-checked
  against the raw logs in the profile.
- The modelled whole-facility profiles are never used.

**Caveat on every verdict:** *node-level power at 5–10 Hz on an HPC cluster; 0.2–3 Hz band only; not phase-level; not a
GB200 rack.* Here the rate is 5 Hz, so the band ends at 2.5 Hz.

**Tags.** Every output is **DERIVED from SOURCED traces under ASSUMED specs**, and every table says so. There are no
$, capex, kW-of-capex or rack-count claims, and nothing about GPU-side smoothing or phase-level dynamics.

## 0. Departures from the brief's text (fixed now)

| # | Brief | DC1 | Why |
|---|---|---|---|
| **DC1-P1** | §3.2 profiles "per job trace"; §4 does not name a segment | **Primary segment: the active segment.** It runs from the first to the last frame with `P ≥ 0.6 · max(P)`. The whole trace is a sensitivity (§7). | The whole trace's swing is set by idle → load and load → idle transitions (profile §2). These are job start and end, which no W ≤ 30 s forecaster can anticipate and no controller form here addresses. They would take most of the 0.1 % violation budget and decide E* by themselves. |
| **DC1-P2** | §3.4 gate counts jobs with A ≥ 0.30; §3.5 folds "jobs … balanced by workload type and A" | **Decision population: all 41 training jobs**, out of fold. The gated 20 (all SD) are reported beside it with the full table but **do not decide**. | The gate is a count (it passes: 20 ≥ 10), and the folds are over all jobs by workload. Llama LoRA is the cleanest synchronous swing in the set (periodic at ~10 s), but its swing is 19–24 % of max, under the 30 % bar. **If the reviewer reads §3.4 as a population filter, flipping this row makes the gated 20 decide. Nothing else changes.** |
| **DC1-P3** | §4.3 K0 fits the SoE target only | **K0 also fits its recovery time constant** T_rec ∈ {2, 5, 10, 30} s, jointly with the SoE target, on the calibration fold. | The brief's "best reactive option" rule (§1.4). A fixed T_rec could leave K0 a strawman. This only strengthens the comparator. |
| **DC1-P4** | §4.3 table: K1-sh uses the "same fitted parameters"; §4.6.1: "with its own fitted parameters" | **The deciding G_sh uses K1's fitted parameters unchanged** (the table's version). G_sh with K1-sh's own fitted gain is reported, not deciding. | The brief contradicts itself. The table defines the control as "same predictor, same fitted parameters", which tests whether the *order* of the history carries the gain. |
| **DC1-P5** | §4.3 K∞: "optimal pre-positioning with perfect foresight", H = the primary W | **K∞ is K1's pre-positioning form fed the true future** over the same 5 s horizon, with its own fitted gain. It is the foresight ceiling *of this controller form*, not a global optimum over all policies. | A global optimum with a violation budget is a mixed-integer problem. The form-ceiling is what G is honestly read against: it says how much of the available pre-positioning gain the predictor captures. |
| **DC1-P6** | §4.4 W ∈ {1, 5, 30} s | **W = 60 s is added as a reported, non-deciding point.** W* is computed on {1, 5, 30} only. | SD's 19.7 s cycle needs a lag beyond W/2 = 15 s. W = 60 s shows whether a longer memory would matter, without moving the decision grid. |
| **DC1-P7** | §4.6.5 G by workload, "inference vs training" | **G is reported for Llama LoRA vs SD training.** Inference cannot be scored. | Every inference run is single-node and under 10 min (profile §1). |

## 1. Population, folds and segment

- **Jobs.** The 41 jobs in `profile.json`, with the folds fixed in profile §5 (A: 21, B: 20).
- **Out of fold.** Every fitted quantity comes from the other fold. Each job is evaluated exactly once, with the
  parameters fitted on the fold it is not in.
- **Segment.** The active segment (DC1-P1). Its frame count N is the denominator of the violation budget.
- **Normalisation.** `P_max` = the job's maximum power on the segment. `swing` = p95 − p5 of the segment. E is
  reported in units of `P_max × 1 s`.

## 2. Plant and spec (brief §4.1–§4.2; ASSUMED)

- **Time step.** dt = 0.2 s, the trace's sampling period.
- **Upstream power.** `P_up(t) = P_load(t) − P_s(t)`. P_s > 0 is discharge.
- **State of energy.** 0 ≤ SoE ≤ E. |P_s| ≤ P_max_s, with **P_max_s = 2 × swing** (sensitivity: 1 × swing).
- **Losses.** Lossless in the primary. η = 0.90 is a sensitivity: √0.9 on charge and √0.9 on discharge.
- **Spec (ASSUMED, not SOURCED from any utility).** `|P_up(t) − P_up(t−1)| ≤ R · P_max · dt` with **R = 0.10 /s**
  (sensitivity 0.05 and 0.20 /s). A frame **violates** if the step exceeds this bound by more than 10⁻⁹ · P_max.
- **Violation budget.** ≤ **0.1 %** of N frames, i.e. ⌊0.001 · N⌋ (sensitivity: 0.5 %).
- **Common step, applied by every controller.** Given a reference r(t):
  1. `P_up* = clip(r, P_up(t−1) − R·P_max·dt, P_up(t−1) + R·P_max·dt)`
  2. `P_s = clip(P_load − P_up*, lo, hi)`, where lo = max(−P_max_s, −(E − SoE)/(η_c·dt)) and
     hi = min(P_max_s, SoE·η_d/dt)
  3. `P_up = P_load − P_s`, then update SoE.

  When the storage saturates, the rate limit gives way. That is the violation.
- **Initial state.** P_up(0) = P_load(0). SoE(0) = s_tgt · E.
- **Dynamic range (secondary, reported only).** (p95 − p5) of P_up, divided by P_max, at E = E*.

## 3. Storage requirement E* (brief §4.4)

- **E\*.** The smallest E with violations ≤ budget.
  - Bisection on log₁₀ E over [10⁻², 600] × P_max·1 s, stopping at a relative bracket < 1 %; the upper end is
    reported.
  - If E = 600 still fails, E* is **censored at 600**. The censoring count is reported, and the ratios use 600.
  - E* < 10⁻² is floored at 10⁻² before any ratio.
- **Monotonicity is checked, not assumed.** For every job and controller, violations are also evaluated at 12
  log-spaced E values. Any non-monotone case is reported, and E* is not changed.
- **Ratios.** G = E*(K0) / E*(K1). G_sh = E*(K0) / E*(K1-sh). G_∞ = E*(K0) / E*(K∞). All per job.

## 4. Controllers (forms fixed here; all causal except K∞)

### 4.1 K0: reactive (the Tier M comparator)

`r(t) = P_load(t) + (s_tgt · E − SoE(t)) / T_rec`

- The rate-limiter tracks the load. The storage absorbs the difference and is steered back toward the target.
- **Fitted on the calibration fold:** s_tgt ∈ {0.3, 0.4, 0.5, 0.6, 0.7} × T_rec ∈ {2, 5, 10, 30} s (DC1-P3).
- **Objective.** Minimise the median of E*/(P_max·1 s) over calibration jobs. Ties go to the earlier grid entry
  (s_tgt ascending, then T_rec ascending).

### 4.2 K1: forecaster, history window W ∈ {1, 5, 30} s (decision grid), plus 60 s (reported)

At each frame, the window is `w = P_load[t − n_W + 1 … t]`, with n_W = W/dt samples.

1. **Period detection.**
   - For each lag L from L_min = 5 samples (1 s) to ⌊n_W / 2⌋, compute ρ(L) = the Pearson correlation of
     w[L:] with w[:−L].
   - If the lag range is empty, or max ρ < **ρ_min = 0.5**: **persistence**, `P̂(t + h) = P_load(t)`.
   - Otherwise L* = argmax ρ (smallest L on ties).
2. **Seasonal-naive forecast.** `P̂(t + h) = P_load(t + h − k·L*)`, with k = ⌈h / L*⌉. This repeats the last
   observed cycle.
3. **Pre-positioning.**
   - Horizon **H_p = 5 s** (25 frames).
   - `Δ̂(t)` = the value of `P̂(t + h) − P_load(t)` with the largest magnitude over h = 1 … 25.
   - Target: `s(t) = clip(s_tgt + g · sign(Δ̂) · Δ̂² / (2 · R · P_max · E), 0.05, 0.95)`.
   - Δ̂² / (2·R·P_max) is the energy a step of Δ̂ draws from the storage under the ramp limit (DERIVED). A predicted
     rise raises the SoE target; a predicted fall lowers it.
4. **Then K0's law with s(t):** `r(t) = P_load(t) + (s(t) · E − SoE(t)) / T_rec`.
5. **Fitted.** s_tgt and T_rec are K0's fitted values from the same calibration fold, not refitted.
   **g ∈ {0, 0.25, 0.5, 1, 1.5, 2}** is fitted per W on the calibration fold, with K0's objective and ties to the
   smaller g. g = 0 is K0 exactly.

**Disclosed in advance (from the profile).**

- Every dominant period in the data is ≥ 6.6 s, and the detectable lag is at most W/2.
- **At W = 1 s the lag range is empty**, so K1 is persistence: Δ̂ = 0, K1 ≡ K0, and G = 1 exactly.
- **At W = 5 s** the lags reach only 2.4 s. K1 can only lock onto sub-period structure, such as the SD 16-node 1.8 s
  autocorrelation (profile §2), or fall back to persistence.
- So any gain is expected at W = 30 s. W* is then likely 30 s if the gain is real, or undefined if it is not.

### 4.3 K1-sh: shuffle control (DC1-P4)

- Same as K1, but the window w is randomly permuted before period detection and forecasting, at every frame.
- RNG: `numpy.random.default_rng(1000 · job_idx + W)`, one permutation per frame in frame order.
- The forecast reads from the permuted window. The cycle is replayed from w's permuted last L* samples.
- **Deciding version:** K1's fitted g, s_tgt and T_rec, unchanged. **Reported:** K1-sh with its own fitted g.

### 4.4 K∞: foresight ceiling of the form (DC1-P5)

K1's steps 3–4, with `P̂(t + h) = P_load(t + h)` (the true future over H_p = 5 s). Its own g is fitted on the
calibration fold, from the same grid extended by {3, 5}. It is non-causal, a ceiling only.

### 4.5 Computation

- The forecast Δ̂(t) does not depend on E or the controller state. It is computed once per (job, W, controller).
- The plant loop then runs per E. It may be written in C (`analysis/DC1_sim.c`, called via ctypes), with a
  pure-Python reference implementation.
- **Gate:** the C and Python loops agree on violation counts exactly, and on SoE to 10⁻⁹ · E, on 3 jobs × 3 E values,
  before any E* is reported.

## 5. Readouts

- **Headline, at the primary W = 30 s.**
  - The median G over each fold's evaluation jobs, **averaged over the two fold directions**.
  - 95 % CI: 1,000 bootstrap resamples (seed 0), resampling jobs with replacement within each fold and recomputing
    both medians.
  - Medians of G_sh and G_∞ are reported beside it, computed the same way.
- **Memory readout.** W* is the smallest W in {1, 5, 30} at which the headline median G ≥ 0.95 × its maximum over
  {1, 5, 30}. G at W = 60 s is reported (DC1-P6).
- **Also reported, none deciding:**
  - by workload (Llama, SD);
  - the "periodic" subset (26 jobs; 5 among the gated);
  - the gated-20 population (DC1-P2);
  - E* per controller per job;
  - the censoring and monotonicity counts;
  - the dynamic-range readout;
  - the fitted parameters per fold.

## 6. Decision (checked in order; brief §4.5 defaults kept)

| Verdict | Condition (at W = 30 s, all 41 jobs, out of fold) |
|---|---|
| **UNDERPOWERED** | The §3.4 gate fails. It passed in the profile (20 ≥ 10), so this is not expected to trigger. |
| **FORECASTING SAVES STORAGE** | median G ≥ **1.25**, **and** its CI lower bound > **1.0**, **and** median G_sh < **1.10** |
| **REACTIVE SUFFICES** | median G < **1.10** |
| **UNCLEAR** | Anything else, including G ≥ 1.25 with G_sh ≥ 1.10 (the gain is not from history) |
| ↳ **NEEDS HISTORY** | FORECASTING SAVES STORAGE **and** W* > 1 s |
| ↳ **NO HISTORY NEEDED** | FORECASTING SAVES STORAGE **and** W* ≤ 1 s. By §4.2's disclosure this cannot occur: G(1 s) = 1. |

- G_∞ is printed beside every G.
- Read against ANGLES §C.2's kill line: "< 10 % reduction at any W" is G < 1.11. The REACTIVE SUFFICES bar is G < 1.10.

## 7. Controls and sensitivity (pre-registered; each re-fit end to end; verdict reported, none deciding)

1. **Shuffle:** K1-sh, both versions (§4.3).
2. **Held-out jobs:** two folds, both directions (§1).
3. **Best reactive:** K0 with fitted s_tgt and T_rec (DC1-P3).
4. **Spec:** R = 0.05 /s and 0.20 /s.
5. **Losses:** η = 0.90.
6. **Storage power:** P_max_s = 1 × swing.
7. **Violation budget:** 0.5 %.
8. **1 Hz decimation.** Block means of 5 samples, dt = 1 s; W, L_min = 1 s and H_p = 5 s keep their meaning in
   seconds. If G collapses, the 5 Hz resolution was load-bearing.
9. **Whole trace instead of the active segment** (DC1-P1).
10. **Population:** the gated 20 (DC1-P2).
11. **By workload** (DC1-P7) and the **periodic subset**.

## 8. Outputs (only after approval)

- **Code:** `analysis/DC1_storage.py` (and `DC1_sim.c` if used).
- **Write-up:** `results/DC1/results_DC1.md`, verdict first, with the licence and the resolution caveat.
- **Data:** `dc1.json`.
- **Plots:**
  - E* per controller per job;
  - median G vs W, with G_sh and G_∞;
  - one Llama and one SD job showing P_load, P_up and SoE under K0, K1 and K∞.
- **Index rows:** one row each in `results/X/README.md` and `results/RESEARCH_DOSSIER.md` §9, and a dated note under
  ANGLES §B.2.
- **No board run.**

## 9. Deviations

Any change after this commit is a numbered deviation (D-1, D-2, …). The segment rule, the population, the folds, R,
the budget, P_max_s, the controller forms, the grids, ρ_min, L_min, H_p, the bisection bounds and the thresholds never
move after results are seen.

### D-1 (reviewer, 2026-10-31, before controller code): co-primary decisions per workload

Replaces DC1-P2's decision population. Nothing else in §1–§4 moves.

- **Two decisions, co-primary:** one for **Llama LoRA** (21 jobs: fold A 11, B 10) and one for **Stable Diffusion
  training** (20 jobs: A 10, B 10). Each is decided by the §6 table at W = 30 s, out of fold.
- **Within each workload,** the headline median is the median G over that workload's evaluation jobs in each fold,
  averaged over the two fold directions. The 95 % CI uses 1,000 bootstrap resamples (seed 0), drawn within fold within
  workload. G_sh and G_∞ are computed the same way.
- **Fitting is unchanged:** every parameter (K0's s_tgt and T_rec; g per controller and W) is still fitted on the whole
  calibration fold, both workloads, with the §4.1 objective. D-1 changes the population a decision is read over. It
  does not change what is fitted, or on what.
- **Reported beside the two verdicts, non-deciding:** the pooled 41 and the gated 20, each run through the §6 table
  with its verdict printed.
- **Caveat on the Llama verdict, disclosed in advance:** Llama's active-segment swing (0.19–0.24 of max) is below the
  0.30 amplitude used in the §3.4 count gate. The gate passed as a count and is not reopened.

### D-2 (reviewer, 2026-10-31, before controller code): 1 s ramp comparator for the memory readout

As pre-registered, G(K1, 1 s) = 1 by construction, so the memory readout could only come out one way. D-2 adds a
short-memory comparator.

- **K1-r (ramp, W = 1 s).**
  - Window: the last n = 5 samples, P_load[t−4 … t].
  - Slope b̂: the least-squares slope of the window against time, in W per frame.
  - Forecast: `P̂(t + h) = P_load(t) + b̂ · h`, for h = 1 … 25 (H_p = 5 s).
  - Then §4.2 steps 3–4 unchanged: Δ̂ = the largest-magnitude `P̂(t + h) − P_load(t)` over the horizon; same target
    law; same r(t).
  - s_tgt and T_rec are K0's fitted values. **g ∈ {0, 0.25, 0.5, 1, 1.5, 2}** is fitted on the calibration fold with
    §4.1's objective, ties to the smaller g.
- **K1-r-sh.** The same, but the 5 window values are randomly permuted before the slope fit; the slope is fitted
  against the original time positions. The anchor P_load(t) is the current reading, not history, and is not permuted.
  RNG: `numpy.random.default_rng(1000 · job_idx + 1001)`, one permutation per frame in frame order. The deciding
  version uses K1-r's fitted g. A version with its own fitted g is reported. Like K1-sh, it is reported, not deciding.
- **Memory readout (replaces the §6 sub-verdict rows), per workload and at W = 30 s:**
  - M = median G(K1, 30 s) / median G(K1-r, 1 s). Both medians are the headline medians, i.e. the mean of fold
    medians. The CI comes from the same 1,000 bootstrap resamples, recomputing both medians in each resample.
  - **NEEDS HISTORY** if M ≥ **1.10** and its CI lower bound > 1.
  - **NO HISTORY NEEDED** if M < **1.10**, i.e. K1-r comes within 10 % of K1. If M < 1/1.10, the write-up says that
    K1-r beat K1.
  - **UNCLEAR on memory** otherwise: M ≥ 1.10, but the CI lower bound is ≤ 1.
  - The readout is computed and printed for both workloads whatever the main verdict. It qualifies the main verdict
    only when that verdict is FORECASTING SAVES STORAGE.
- **W\*.** W* is computed over {1 s (K1-r), 5, 30, 60} s, per workload: the smallest W at which the headline median
  G ≥ 0.95 × its maximum over that set. At 1 s, G means G(K1-r). This supersedes DC1-P6's "W* on {1, 5, 30} only".
  The headline stays at W = 30 s. G(K1, 1 s) = 1 is still printed, as a check of §4.2's disclosure.
- **Where it appears:** K1-r and K1-r-sh are evaluated in every §7 sensitivity alongside K1. G(K1-r) and G(K1-r-sh)
  are printed beside every W* readout.
