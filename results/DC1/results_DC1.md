# DC1 results: does remembering the last seconds of an AI-training load shrink the storage that holds it inside a ramp spec?

**Brief:** [`briefs/DC1/README.md`](../../briefs/DC1/README.md).
**Pre-registration:** [`DC1_preregistration.md`](DC1_preregistration.md), including deviations D-1 and D-2.
**Profile:** [`DC1_profile.md`](DC1_profile.md).
**Code:** [`analysis/DC1_storage.py`](../../analysis/DC1_storage.py) and [`analysis/DC1_sim.c`](../../analysis/DC1_sim.c).
**Data:** [`dc1.json`](dc1.json). **Log:** [`storage.out`](storage.out). Run on 2026-10-31 on the x86 host, CPU only.

**Tags.** Every number in this file is **DERIVED from SOURCED traces under ASSUMED specs**:

- The traces are the NLR GenAI power profiles.
- The specs are the ramp limit, the violation budget, the storage power limit and losses (pre-registration §2).
- No number here is MEASURED, and none is compared against a MEASURED number.

**Licence.** CC BY 4.0. Credit DOE / NLR / ALLIANCE. Cite arXiv:2604.07345 and DOI 10.7799/3025227. The record is in
[`LICENCE_record.txt`](LICENCE_record.txt).

**Resolution caveat, which applies to every verdict below.** The data is node-level power at 5 Hz on an HPC cluster
(4 GPUs per node, 2–16 nodes). Only the 0.05–2.5 Hz band is visible. The data is not phase-level and not from a
GB200-class rack.

## 1. Verdicts (D-1: co-primary per workload, W = 30 s, out of fold)

| Workload | Jobs | median G [95 % CI] | G_sh | G_∞ (form ceiling) | **Verdict** | Memory readout (D-2): M = G(K1, 30 s) / G(K1-r, 1 s) [95 % CI] | W* |
|---|---|---|---|---|---|---|---|
| **Llama-2-70B LoRA** | 21 | **1.022** [1.003, 1.048] | 1.000 | 1.393 | **REACTIVE SUFFICES** | 1.011 [0.984, 1.059]: **NO HISTORY NEEDED** | 1 s (K1-r) |
| **Stable Diffusion training** | 20 | **1.001** [0.997, 1.054] | 1.000 | 1.373 | **REACTIVE SUFFICES** | 1.000 [0.985, 1.048]: **NO HISTORY NEEDED** | 1 s (K1-r) |

*Every value in the table is DERIVED from SOURCED traces under ASSUMED specs. G = E\*(K0) / E\*(K1). Each median is
the mean of the two fold medians. The CIs come from 1,000 job resamples within fold (seed 0).*

**Llama caveat (disclosed in advance, D-1).** Llama's active-segment swing is 0.19–0.24 of P_max. That is below the
0.30 amplitude used in the count gate.

**In words.**

- Under the pre-registered spec, a seasonal-naive forecaster with 30 s of history saves **2.2 %** of the storage a
  well-tuned reactive controller needs on Llama, and **0.1 %** on Stable Diffusion. Both are below the 10 % bar.
- A 1 s ramp extrapolator (K1-r) does as well: 1.1 % and 0.1 %. So the memory readout is NO HISTORY NEEDED on both
  workloads.
- The ceiling of the same pre-positioning form, fed the true 5 s future, would save **28 %** (1 − 1/1.393) and **27 %**
  (1 − 1/1.373). So pre-positioning has room to pay; this causal predictor captures almost none of it.
- Read against ANGLES §C.2's kill line ("< 10 % reduction at any W"), K1 is under it at every W:

  | | 1 s (K1-r) | 5 s | 30 s | 60 s |
  |---|---|---|---|---|
  | Llama | 1.011 | 1.000 | 1.022 | 1.008 |
  | SD | 1.001 | 1.000 | 1.001 | 1.003 |

**Non-deciding populations (D-1), from the same fit.**

| Population | n | median G [95 % CI] | G_sh | G_∞ | G_r | M | Verdict / memory |
|---|---|---|---|---|---|---|---|
| Pooled | 41 | 1.008 [1.000, 1.045] | 1.000 | 1.383 | 1.005 | 1.003 | REACTIVE SUFFICES / NO HISTORY NEEDED |
| Gated (all SD) | 20 | 1.001 [0.997, 1.054] | 1.000 | 1.373 | 1.001 | 1.000 | REACTIVE SUFFICES / NO HISTORY NEEDED |
| Periodic | 26 | 1.019 [1.003, 1.045] | 1.000 | 1.385 | 1.011 | 1.008 | REACTIVE SUFFICES / NO HISTORY NEEDED |

*All DERIVED from SOURCED traces under ASSUMED specs. The gated 20 are exactly the SD jobs, so that row repeats SD's.*

## 2. What sits under the headline

**The fit chose "no forecast" on one fold.**

- On fold A's calibration jobs, K1's best gain at W = 30 s was **g = 0**, which is K0 exactly. So every fold-B job
  has G = 1.000.
- Fold B's calibration chose g = 1.0, and that is applied to fold-A jobs:

  | Fold-A jobs | median G | per-job range |
  |---|---|---|
  | Llama | 1.044 | 0.96–1.78 |
  | SD | 1.003 | 0.72–1.23 |

- The headline is the mean of the two fold medians, as pre-registered.
- The per-fold fits are below.

**Fitted parameters (primary spec; each fold's values evaluate the other fold).**

| Fitted on | K0 s_tgt, T_rec | g, K1 at 5 / 30 / 60 s | g, K1-r | g, K∞ | g, K1-sh at 30 s (own fit) |
|---|---|---|---|---|---|
| A | 0.3, 2 s | 0.25 / **0** / 0 | 0 | 0.25 | 1.5 |
| B | 0.3, 5 s | 0.25 / **1.0** / 0.5 | 1.5 | 0.25 | 0.25 |

**Storage requirement (DERIVED).**

| E\*(K0), units of P_max × 1 s | median | range |
|---|---|---|
| Llama | 0.44 | 0.23–1.75 |
| SD | 2.0 | 1.0–7.7 |

- No job was censored at 600 and none was floored, for any controller.
- Monotonicity was checked on a 12-point E grid:
  - The violation count rose with E somewhere on the grid in 2 jobs for K1 (30 s), 3 for K1-r-sh and 2 for K∞.
  - There was **no pass/fail reversal**, so no E\* is ambiguous.
  - E\* was not changed, as pre-registered.

**Dynamic-range readout (secondary).** This is the median over jobs of (p95 − p5) of P_up / P_max at each job's E\*:

| K0 | K1 (30 s) | K1-r | K∞ |
|---|---|---|---|
| 0.248 | 0.242 | 0.246 | 0.217 |

**What the shuffle control actually tested (G_sh = 1.000 everywhere).**

- Once its window is permuted, the seasonal detector almost never finds ρ ≥ 0.5. On three spot-checked jobs (idx 0,
  21, 37; W = 30 s), K1 locks onto a period in 95 %, 91 % and 35 % of frames, against 0.05 %, 0.6 % and 1.5 % for
  K1-sh.
- So K1-sh falls back to persistence, i.e. to K0.
- As built, the control therefore separates "a forecast" from "no forecast", rather than "ordered history" from "the
  same values in the wrong order".
- Its condition in §6 (G_sh < 1.10) is met trivially in every run. It never decided anything here, because G itself
  stayed below 1.25 in the primary.

**Sanity check from the disclosure.** G(K1, 1 s) = 1.000 on both workloads, as §4.2 said it must.

## 3. Sensitivities (§7; each re-fit end to end; none decides)

| Run | Llama: G [CI] / G_sh / G_∞ / M | Llama verdict / memory | SD: G [CI] / G_sh / G_∞ / M | SD verdict / memory |
|---|---|---|---|---|
| **Primary** | 1.022 [1.003, 1.048] / 1.000 / 1.39 / 1.011 | REACTIVE / NO HISTORY | 1.001 [0.997, 1.054] / 1.000 / 1.37 / 1.000 | REACTIVE / NO HISTORY |
| R = 0.05 /s | 1.003 [1.000, 1.094] / 1.000 / 2.25 / 0.996 | REACTIVE / NO HISTORY | 1.000 [0.975, 1.005] / 1.000 / 1.57 / 1.000 | REACTIVE / NO HISTORY |
| R = 0.20 /s | 1.134 [1.090, 1.236] / 1.000 / 1.33 / 1.070 | UNCLEAR / NO HISTORY | 1.000 [0.987, 1.022] / 1.000 / 1.34 / 0.984 | REACTIVE / NO HISTORY |
| η = 0.90 | 1.040 [1.015, 1.154] / 1.000 / 1.40 / 1.029 | REACTIVE / NO HISTORY | 1.003 [0.942, 1.024] / 1.000 / 1.39 / 0.993 | REACTIVE / NO HISTORY |
| P_max_s = 1 × swing | 1.000 [1.000, 1.000] / 1.000 / 22.4 / 1.000 † | REACTIVE / NO HISTORY † | 1.188 [1.074, 1.326] / 1.000 / 1.41 / 1.188 | UNCLEAR / NEEDS HISTORY |
| Budget 0.5 % | 1.137 [1.126, 1.244] / 1.000 / 1.27 / 1.140 | UNCLEAR / NEEDS HISTORY | **1.270 [1.147, 1.277]** / 1.000 / 1.28 / 1.279 | **FORECASTING SAVES / NEEDS HISTORY** |
| 1 Hz decimation | 1.000 [1.000, 1.005] / 1.000 / 1.11 / 1.000 | REACTIVE / NO HISTORY | 1.000 [1.000, 1.004] / 1.028 / 1.68 / 1.000 | REACTIVE / NO HISTORY |
| Whole trace | 1.000 [1.000, 1.000] / 1.000 / 1.31 / 1.000 | REACTIVE / NO HISTORY | 1.000 [1.000, 1.000] / 1.000 / 1.44 / 1.000 | REACTIVE / NO HISTORY |

*All DERIVED from SOURCED traces under ASSUMED specs. W\* per run is in `dc1.json`; it is 30 s wherever the memory
readout says NEEDS HISTORY.*

† With P_max_s = 1 × swing, **17 of 21 Llama jobs are censored at E = 600** for every causal controller, and 8 for
K∞. Llama's active-segment excursions go beyond its p5–p95 swing, so a storage element capped at 1 × swing cannot hold
the ramp at any size. Ratios of censored values are 1 by construction, so the Llama row is uninformative. No SD job is
censored.

**Reading.**

- The forecaster's advantage appears in the specs that leave it slack:
  - a 5× looser violation budget, where SD crosses every FORECASTING SAVES bar and both workloads read NEEDS HISTORY
    at W* = 30 s;
  - a faster ramp limit (Llama, UNCLEAR);
  - a storage power limit that binds (SD, UNCLEAR).
- These are pre-registered sensitivities. They do not move the primary verdicts, and nothing here promotes them.
- The pattern is consistent with E\* at a 0.1 % budget being set by a few frames that no 5 s-horizon predictor
  foresees. With 5× as many violations allowed, the bulk of the cycles, where the seasonal forecast is right, takes
  over.
- The 1 Hz run cannot serve as a "did 5 Hz carry it" test, because G was already ≈ 1 at 5 Hz. G_∞ falls from 1.39 to
  1.11 on Llama at 1 Hz, so the resolution does matter for the ceiling.

**Monotonicity and censoring in the sensitivities.** Full counts are in `dc1.json`.

- No pass/fail reversals, except:
  - whole trace: 1 job per controller;
  - R = 0.05: 2 jobs for K∞.
- Count increases without a reversal:
  - 1 Hz decimation: 16–18 jobs per controller;
  - η = 0.90: up to 8 jobs.
- Censoring outside †: 1 job, for K1-sh at 5 s and for K1-r-sh, at R = 0.05.

## 4. Gate (§4.5)

The C and Python implementations were compared on three jobs (idx 0, 21 and 37) before any E\* was computed.

- **Plant loop.** At 3 E values (0.3, 3 and 30 × P_max·s), with K0, K1 (30 s, g = 1) and K1-r (g = 1): violation
  counts are identical in 27 of 27 cases, and the maximum SoE difference is **0.0** × E.
- **Forecasters.** K1 and K1-sh at 5, 30 and 60 s, plus K1-r and K1-r-sh, were compared on 1,000 frames per job
  (warm-up, mid-segment and end). The forecast step is identical (maximum difference 0.0), with 0 L* mismatches.
- Result: **PASS**.

## 5. Implementation choices the pre-registration did not spell out

1. **Warm-up.** Before a controller's window is full (the first W s of the segment), K1, K1-sh, K1-r and K1-r-sh use
   persistence (Δ̂ = 0), i.e. K0. The shuffle RNG draws its first permutation at the first full-window frame.
2. **K∞ near the end.** Near the segment's end, K∞'s horizon is truncated to the frames that exist.
3. **K1-r at 1 Hz.** Under 1 Hz decimation, K1-r's 1 s window is 2 samples (one 1 s difference), since a 1-sample slope
   does not exist. At 5 Hz it is 5 samples, as D-2 fixes.
4. **Subset populations.** Gated, periodic and pooled are readouts from the primary fit; they are not re-fitted. The
   sensitivities are re-fitted end to end.
5. **Monotonicity grid.** The 12-point grid is log-spaced on [10⁻², 600] × P_max·s.
6. **Dynamic range.** It is evaluated at each job's own E\* for that controller.

## 6. Plots

- [`dc1_estar.png`](dc1_estar.png): E\* per job for K0, K1 (30 s), K1-sh (30 s), K1-r and K∞, out of fold.
- [`dc1_G_vs_W.png`](dc1_G_vs_W.png): median G against W per workload, with the shuffled curve, G_∞ and the 30 s CI.
- [`dc1_traces.png`](dc1_traces.png): 120 s of Llama job 0 and SD job 21 at E = E\*(K0), showing P_load, P_up and SoE
  under K0, K1 (30 s) and K∞. Both jobs are in fold B, where K1's fitted g is 0, so K1's lines lie exactly on K0's. The
  plot shows K∞'s pre-positioning against a controller that chose not to forecast.

## 7. What this does and does not say

- **It says:**
  - On public node-level 5 Hz training traces, under an ASSUMED 0.10 P_max/s ramp limit with a 0.1 % violation budget,
    a causal seasonal-naive forecaster does not buy a smaller storage element than a tuned reactive controller.
  - A 1 s ramp extrapolator does as well as 30 s of history.
  - The perfect-foresight ceiling of the same form is about 1.38×, so the gap is the predictor's, not the mechanism's.
- **It does not say:**
  - anything about phase-level (ms) dynamics or the ~20 Hz component;
  - anything about GB200-class racks or GPU-side smoothing;
  - anything about a better predictor than seasonal-naive;
  - any $, capex or rack-count figure.
- The budget-0.5 % run is the one place where history pays (SD 1.27×, W* = 30 s). It is a pre-registered sensitivity,
  and a reason to ask what violation budget a real ramp spec allows. It is not a result.
