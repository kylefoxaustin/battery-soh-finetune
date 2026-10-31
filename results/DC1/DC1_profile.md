# DC1 profile: swing structure, periodicity, folds and power (brief §3)

Run 2026-10-31 by `analysis/DC1_profile.py`. Outputs: [`profile.json`](profile.json), [`profile.out`](profile.out) and
[`profile.png`](profile.png).

**No controller, predictor, storage simulation or score has been computed.** The script contains a loader and profile
statistics only.

- **Tags.** Every value is **DERIVED from SOURCED traces** (node GPU + CPU power measured by the dataset's authors).
  Workload labels and node counts are SOURCED from the dataset's metadata.
- **Licence.** **CC BY 4.0**, per the OpenEI submission. The NLR Data Catalog, which serves the archive, carries a
  DOE/NLR/Alliance notice that yields to separate licence terms. Both texts are verbatim in
  [`LICENCE_record.txt`](LICENCE_record.txt).
  - Neither restricts derived results.
  - The notice asks that publications credit **DOE/NLR/ALLIANCE**, and that the notice travel with any copy of the
    *data*. The raw data stays under the git-ignored `data/raw/` and is not redistributed.
  - Cite Vercellino et al., arXiv:2604.07345, and DOI 10.7799/3025227.
- **Caveat carried on every verdict:** *node-level power at 5–10 Hz on an HPC cluster; 0.2–3 Hz band only; not
  phase-level; not a GB200 rack.* For the jobs used here the rate is 5 Hz, so the resolvable band ends at 2.5 Hz.

## Summary

| §3 item | Value | Reading |
|---|---|---|
| Usable unit (§2) | **41 multi-node training jobs**: 21 Llama-2-70B LoRA fine-tuning and 20 Stable Diffusion training, at 2, 4, 8 and 16 nodes (4 GPUs per node), 5 Hz, 21–249 min | One job's total power: GPU + CPU summed over its nodes, as the brief requires |
| Inference | 2,426 single-node runs, 9.6–180 s each | **Not usable.** Single-node, and every run is under 10 min. G cannot be reported for inference (§4.6.5). |
| **Swing A on the whole trace** | 0.64–0.85; all 41 jobs ≥ 0.30 | Dominated by job start-up (idle and model loading) and teardown, not by the training swing |
| **Swing A on the active segment (DC1-P1)** | **Llama 0.19–0.24** (all < 0.30); **SD 0.59–0.75** (all ≥ 0.30) | Llama swings about ±10 % around 85–93 % of max, every ~10 s. SD's swing comes from long burst phases (dips to 25–40 % of max). |
| **Power gate (§3.4), active segment** | **20 jobs** (all SD; 10 per fold) | ≥ 10: **PASSES**. On the whole trace, 41 pass. |
| Periodic (spectral peak ≥ 20 % of variance) | **26 of 41** (all 21 Llama, 5 SD); **5 of the 20 gated** | Gated count is exactly 5, so not "under 5": the forecasting readout is not descriptive-only, but it rests on 5 jobs |
| Dominant period | Llama **9.9–10.7 s** (peak share 0.67–0.81); SD **6.6 / 13.5 / 19.7 s** (share 0.04–0.68) | All in the brief's band. **Every period exceeds 2.5 s**, which matters for the history windows (pre-registration §4). |
| Step steepness (|ΔP| per 0.2 s, / max) | p95: Llama 0.039–0.048, SD 0.006–0.128; max 0.14–0.21 per sample | The largest steps are 70–107 % of max per second (DERIVED), against the ASSUMED 10 %/s spec |
| Data integrity | 3 jobs re-aggregated independently from the raw per-node logs: they match the provider's per-job files to **≤ 1.7 × 10⁻⁷ of max** | Every training job has exactly 2 × nodes raw files. The CPU (RAPL) logs contain isolated NaN readings, skipped in the sum as the provider's code does (64–144 cells per job checked). |

**Headline of the profile.** The dataset holds two kinds of synchronous-training swing:

- **Llama LoRA:** a clean, strongly periodic ~10 s square-ish wave of about 20 % of the job's maximum.
- **Stable Diffusion:** deep (60–75 %) swings in burst phases that last minutes. Most of these jobs are not periodic
  by the §3.3 definition.

The power gate passes on the active segment, but only on the SD jobs. That makes the choice of evaluation population a
question for the reviewer (pre-registration §1, DC1-P2).

## 1. Dataset facts (§3.1)

- **Archive.** `dataset.zip`: 1,070,866,623 bytes, SHA-256
  `dcad6de800fb565d850b163902e2eddae48aabd1ed1c7336f9a1cdaf3012f137`, from the NLR Data Catalog link on the OpenEI
  page. The catalogue lists it as 1021.3 MB, version 2. It unpacks to 3,191 entries, 2.9 GB.
- **Excluded at extraction.** A bundled `.git/` directory and an `.activate.sh` shell script. Nothing from the archive
  was executed: the provider's `postprocess.py` and `utilities.py` were read, not run.

| Folder | Files | Size | Content | Used |
|---|---|---|---|---|
| `00_raw_datasets/training_llama2_70b_lora` | 316 | 451 MB | Per-node WattAMeter logs: `nvml_*` (4 GPUs, mW, ~5 Hz) and `rapl_*` (2 CPU sockets, W). One Slurm ID per job. 2/4/8/16 nodes. | Cross-check only |
| `00_raw_datasets/training_stable_diffusion` | 282 | 711 MB | As above; 1/2/4/8/16 nodes | Cross-check only |
| `01_aggregated_datasets/training` | 43 | 16 MB | **41 per-job parquet files**: total power (GPU + CPU over all nodes), linearly interpolated to a 0.2 s grid over the window common to all of the job's nodes; `metadata.csv` (model, nodes, repeat, Slurm ID) | **Primary input** |
| `00_raw_…/inference_*`, `01_aggregated_…/inference_*` | 17 raw, 2,432 aggregated | 809 MB, 549 MB | Llama-3-70B inference (offline, online-finite, online-rate), one node per run | Profiled for eligibility only |
| `02_analysis_scripts` | 16 | 5 MB | Provider's plotting scripts | No |
| `03_whole-facility_profiles/*/simulated_data` | 8 CSV | 224 MB | **SOURCED-model**: the DIPLOEE bottom-up facility model's output (1 MW inference, 10 MW colocation) | **Never** (brief §2) |

**Nodes to jobs.**

- The raw file names carry the Slurm ID and node name. A job is one Slurm ID.
- Every training job has exactly `2 × nodes` files (one GPU and one CPU log per node). There are 5 jobs at each
  configuration, except Llama at 8 nodes (6), SD at 2 nodes (6) and SD at 16 nodes (4).
- The 5 single-node SD jobs exist raw but have no aggregated file. They are single-node, so they are not multi-node
  jobs and are not used.
- The provider's per-job file is exactly the brief's unit. Re-aggregating jobs 0, 21 and 37 from the raw logs with an
  independent loader (linear interpolation onto the same grid, then a plain sum) reproduces it to a maximum absolute
  difference of 8.7 × 10⁻⁸, 1.7 × 10⁻⁷ and 5.0 × 10⁻⁸ of the job's maximum.
- The rate is 0.2 s for every training job. The "10 Hz" in the dataset description applies to some inference
  aggregates, not to the jobs used here.

## 2. Per job (§3.2): whole trace and active segment

**Active segment (DC1-P1, defined before any controller exists).** From the first to the last frame with
`P ≥ 0.6 · max(P)`. It removes the idle and model-loading start (1–6 min) and the teardown. Mid-job pauses and burst
phases stay in.

**Definitions** (constants in the script):

- **A** = (p95 − p5) / max.
- **Midpoint** = (p5 + p95) / 2. Dwell is the median run length above or below it.
- **Spectrum.** Welch PSD: Hann window, 256 s segments, 50 % overlap, mean removed.
  - The dominant peak is the PSD maximum in 0.05–2.5 Hz.
  - Its **share** is the PSD within ±10 % of the peak frequency, divided by the PSD summed over all non-zero
    frequencies.
  - Share with the first 7 harmonics, and the autocorrelation peak over 2–60 s lags, are **descriptive only**.
- **Step steepness** = p95 and max of |ΔP| per sample, divided by max.

**Ranges by workload, DERIVED** (per-job values in `profile.json`):

| | Llama LoRA (21) | Stable Diffusion (20) |
|---|---|---|
| Max power | 6.1–48.4 kW | 6.0–47.6 kW |
| Duration, whole / active | 33.9–97.2 / 29.4–92.4 min | 23.4–252 / 21.4–249 min |
| A, whole / active | 0.70–0.82 / **0.19–0.24** | 0.64–0.85 / **0.59–0.75** |
| p5 / max, active | 0.76–0.80 | 0.25–0.40 |
| p50 / max, active | 0.86–0.93 | 0.81–0.98 |
| Fraction above the midpoint, active | 0.48–0.53 | 0.73–0.93 |
| Median dwell above / below the midpoint, active | 5.6–5.8 s / 4.4–4.8 s | 11.8–12.0 s / 1.2–8.0 s |
| Dominant period, active | 9.9–10.7 s | 6.6 s (12 jobs), 13.5 s (3), 19.7 s (5) |
| Peak share, active (with harmonics, descriptive) | **0.67–0.81** (0.82–0.94) | 0.04–0.68 (0.12–0.83) |
| ACF peak, 2–60 s, active (descriptive) | 0.78–0.89 at 10.0–10.8 s | 0.65–0.89 at 1.8–20 s |
| |ΔP| per sample, p95 / max, active | 0.039–0.048 / 0.14–0.16 | 0.006–0.128 / 0.15–0.21 |

**What the traces look like** (`profile.png`):

- **Llama.** A square-ish wave between about 19 and 24 kW (8 nodes), period about 10.5 s. It has ~2 s ramps and a short
  undershoot on each fall, with a pause of tens of seconds to minutes every 5–10 min.
- **Stable Diffusion.** Long flat stretches near max, interrupted by **burst phases** lasting minutes, then a return to
  the flat level.
  - **2-node jobs:** 1.4 s dips to ~30 % every 13 s.
  - **4- and 8-node "periodic" jobs (27, 32, 33):** ~20 s square cycles between 25 % and 100 %.
  - **16-node jobs:** a single burst phase near the end.
  - SD's 6.6 s "dominant period" in 12 jobs is the second harmonic of the 13 s dip train. That is why its share is low
    although the dips are regular.

## 3. Aggregate (§3.3)

| | Whole trace | Active segment |
|---|---|---|
| A: min / q1 / median / q3 / max | 0.64 / 0.73 / 0.75 / 0.76 / 0.85 | **0.19 / 0.21 / 0.24 / 0.68 / 0.75** (bimodal by workload) |
| Dominant period: min / q1 / median / q3 / max | 6.6 / 6.6 / 10.2 / 10.7 / 19.7 s | same |
| Periodic (share ≥ 0.20) | 26 of 41 | 26 of 41 (21 Llama, 5 SD) |

## 4. Power gate (§3.4)

**Gate:** A ≥ 0.30, duration ≥ 10 min, sampling ≥ 5 Hz. Every training job meets the duration and rate parts.

| Segment | Jobs passing | By workload | By fold | Periodic among them |
|---|---|---|---|---|
| **Active (primary, DC1-P1)** | **20** | Llama 0, SD 20 | A 10, B 10 | **5** (A 2, B 3) |
| Whole trace | 41 | Llama 21, SD 20 | A 21, B 20 | 26 |

- **The gate PASSES on the primary segment** (20 ≥ 10).
- The "periodic" count among gated jobs is exactly 5, so by §3.4 the forecasting readout is not descriptive-only. It
  rests on 5 SD jobs. On the whole-trace segment or the all-jobs population (DC1-P2), 26 periodic jobs are available.

## 5. Folds (§3.5, CHOSEN and fixed)

**Rule.** Within each workload, sort jobs by active-segment A (ties broken by index), then assign A, B, B, A, A, B, B, A
and so on. It is in `folds()` in the script and was run once.

| Fold | Llama jobs (idx) | SD jobs (idx) | Median active A, Llama / SD |
|---|---|---|---|
| **A** | 1, 2, 4, 5, 6, 10, 13, 14, 16, 18, 19 (11) | 22, 23, 25, 31, 32, 34, 35, 36, 38, 39 (10) | 0.209 / 0.682 |
| **B** | 0, 3, 7, 8, 9, 11, 12, 15, 17, 20 (10) | 21, 24, 26, 27, 28, 29, 30, 33, 37, 40 (10) | 0.207 / 0.679 |

Jobs are held out, but configurations are not: every (model, nodes) configuration has repeats in both folds. The split
is uneven for SD 4-node (4 of 5 jobs in B) and SD 8-node (4 of 5 in A). This is disclosed, and not changed.

## 6. Spec and controller forms

These are fixed in [`DC1_preregistration.md`](DC1_preregistration.md) §2–§4, with every number filled in.

## Notes for the reviewer

1. **DC1-P1: active segment.** On the whole trace, every job's A is set by idle-to-load and load-to-idle transitions
   that no W ≤ 30 s forecaster can see coming. They would also likely dominate E* through the 0.1 % violation budget.
   The pre-registration makes the active segment primary and the whole trace a sensitivity.
2. **DC1-P2: population.**
   - Llama LoRA is the cleanest synchronous-training swing in the set (periodic, ~10 s), but its swing is ~20 % of max,
     under the 30 % gate bar.
   - The brief's gate is a count, and its folds are over all jobs by workload. The pre-registration therefore decides
     on **all 41 jobs** and reports the gated-20 (SD) population beside it.
   - If the reviewer reads §3.4 as a population filter, flipping this one line makes the gated 20 decide.
3. **Window grid vs periods.** Every dominant period is ≥ 6.6 s. A seasonal-naive predictor can only detect a period
   ≤ W/2, so **W = 1 s and W = 5 s cannot see any of these periods**, and K1 falls back to persistence there. This is
   disclosed in advance in the pre-registration (§4.2), not discovered afterwards. W = 60 s is added as a reported,
   non-deciding point so that SD's 19.7 s cycle is in reach.
