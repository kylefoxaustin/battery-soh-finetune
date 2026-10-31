# Build Brief — DC1: how much rack-side storage does forecasting save when holding synchronous-AI power swings inside a ramp spec, and how much history does it need?

**Licence of this document:** public domain (CC0). **Written:** 2026-10-31. **Origin:** ANGLES report §B.2 / §C.2
([`results/OPEN_PROBLEM/ANGLES_REPORT.md`](../../results/OPEN_PROBLEM/ANGLES_REPORT.md)), item 3 in
[`briefs/NEXT_EXPERIMENTS/README.md`](../NEXT_EXPERIMENTS/README.md); promoted after B1 (MEASURED) completed.

> ## ▶ DONE 2026-10-31 — `cf94244`: REACTIVE SUFFICES on both workloads; NO HISTORY NEEDED (reviewer accepted)
>
> Results: [`results/DC1/results_DC1.md`](../../results/DC1/results_DC1.md). The reviewer re-derived G, G_sh, G_∞ and the
> memory ratio per workload from the per-job E* values in `dc1.json` (primary and three sensitivities); they match.
> Reading and follow-ups are in [`briefs/NEXT_EXPERIMENTS/README.md`](../NEXT_EXPERIMENTS/README.md) (status block). The
> approval text is kept below for the record.
>
> ## ▶ APPROVED 2026-10-31, with two reviewer additions — commit them as D-1 and D-2, then run (superseded: done)
>
> The first stage (`09051a5`: [`results/DC1/DC1_profile.md`](../../results/DC1/DC1_profile.md),
> [`results/DC1/DC1_preregistration.md`](../../results/DC1/DC1_preregistration.md), licence record) is accepted. The
> reviewer re-derived the gate (20 of 41, all SD, 10 per fold), the periodic counts (26 of 41; 5 among the gated, A 2 /
> B 3), the per-workload A and period ranges and the folds from `profile.json`; they match. DC1-P1, P3, P4, P5 and P7
> are accepted as written. Two additions, fixed now before any controller code:
>
> - **D-1 (replaces DC1-P2's decision population).** The profile shows two structurally different populations: Llama
>   LoRA (21 jobs, periodic ~10 s, swing 19–24 %) and Stable Diffusion training (20 jobs, deep burst phases, mostly
>   aperiodic). A pooled median over 41 would be decided by whichever population sits in the middle, not by the
>   mechanism. **Decide co-primary, per workload**, each by the §6 table at W = 30 s, out of fold: one verdict for Llama,
>   one for SD. The pooled 41 and the gated 20 are reported beside them, non-deciding. Llama's verdict carries the
>   disclosed caveat that its active-segment swing is below the 0.30 amplitude used in the count gate (the gate itself
>   passed, as a count, and is not reopened).
> - **D-2 (makes the memory readout a test rather than a tautology).** As pre-registered, G(1 s) = 1 by construction,
>   so "NEEDS HISTORY" could only ever come out one way. Add **K1-r**, a short-memory comparator: linear extrapolation
>   of the last **1 s** slope over the same horizon H_p = 5 s, the same pre-positioning law (§4.2 steps 3–4), its own g
>   fitted on the calibration fold from the same grid; **K1-r-sh** (window shuffled) reported beside it. Memory
>   readout: **NEEDS HISTORY** if median G(K1, 30 s) / median G(K1-r, 1 s) ≥ **1.10** with CI lower bound > 1;
>   **NO HISTORY NEEDED** if K1-r is within 10 % of K1; otherwise UNCLEAR on memory. W* is computed over
>   {1 s (K1-r), 5, 30, **60**} s (DC1-P6's 60 s point joins the W* grid; the headline stays at W = 30 s).
>
> **Run order:** commit D-1 and D-2 into `results/DC1/DC1_preregistration.md` with "before controller code" in the
> message; then write and run `analysis/DC1_storage.py` (and `DC1_sim.c` if used, gated as §4.5) exactly as
> pre-registered; commit `results/DC1/results_DC1.md` (verdicts first — two of them — with the licence and the
> resolution caveat), `dc1.json`, the plots, the index rows and the ANGLES §B.2 note; set `NEXT_TASK.md` Status to
> `DONE <commit-hash>`; push; stop.
>
> ## ▶ START HERE (superseded: first stage done at `09051a5`; see the APPROVED box above)
>
> 1. `git pull` on `main`.
> 2. Read this brief end to end, then ANGLES §B.2 and §C.2 and `results/X/X6_preregistration.md` (the decision-table
>    style to copy).
> 3. **Stage 1.** Download the primary dataset (§2), record its licence text verbatim, and write
>    `results/DC1/DC1_profile.md` (§3) and `results/DC1/DC1_preregistration.md` (§4 with every threshold filled in).
> 4. Commit both with "before controller code" in the commit message. **Write no controller, predictor or scoring
>    code.** A loader and the profile statistics are allowed.
> 5. Set the Status line in `NEXT_TASK.md` to `AWAITING APPROVAL <commit-hash>`, push, and stop.
>
> The reviewer will then edit this box to "APPROVED, run it now" or send changes.

---

## 0. Why DC1 exists

ANGLES §B.2 argues that the data-centre analogue of the EV uncertainty reserve is **provisioned power held back against
load uncertainty**, that the money there is public (Google: 9–25 % oversubscription, "hundreds of millions of dollars";
power infrastructure ≈ $4.5–5.7 per watt of an $11.3 M/MW build), and that the rack-level stabilisation of synchronous
AI training (swings of tens to hundreds of MW at 0.2–3 Hz) is being solved with rack energy storage plus fast telemetry
(Choukse et al., arXiv 2508.14318). The storage element on the 800 VDC bus is an EV-class pack with a predictable load.

The claim that needs a number is narrow: **does a controller that remembers the last few seconds of the load buy a
smaller storage element than a reactive one, and how many seconds does it need?** The second half is the memory
readout. If every gain saturates with one second of history, the mechanism may be real but any MCU can host it; if it
needs tens of seconds across hundreds of phases, the brief §7 arithmetic (12 MB/s per GPU, ~100 MB/s per board) puts
the window in LPDDR territory, and B1 has now measured what that tier holds.

**What DC1 cannot test, stated up front.** The public data is **node-level at 5–10 Hz** (primary) and **100 ms**
(secondary). It resolves the 0.2–3 Hz band of the swings but not phase-level (ms) dynamics and not the ~20 Hz component.
Phase-level anticipation stays out of scope and must be said to be. The racks are HPC nodes, not GB200-class racks.

---

## 1. Rules of engagement (unchanged from X5/X6/X7)

1. A pleasing number is a suspected defect until gated.
2. Tag every figure MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED. Everything here is DERIVED from SOURCED traces
   under ASSUMED specs; say so on every table.
3. Pre-register before controller code. Never move a threshold after seeing results. Number every deviation.
4. Every comparison uses the **best reactive option** (a tuned rate limiter with a fitted pre-charge), not a strawman.
5. Every "history helps" claim needs a **time-shuffle control** (the history window's order destroyed) and **held-out
   jobs**.
6. Report the **oracle ceiling** beside every gain.
7. No $ or kW-of-capex claims here; the conversion stays in ANGLES §B.2. No claims about GPU-side smoothing, which
   cannot be emulated from a power trace.
8. Carry the licence and the resolution caveat on every verdict: *"node-level power at 5–10 Hz on an HPC cluster;
   0.2–3 Hz band only; not phase-level; not a GB200 rack."*
9. A clean REACTIVE SUFFICES or UNDERPOWERED is a result.

---

## 2. Data

**Primary (SOURCED from the data.gov catalogue entry; confirm on the submission page before use).** National Laboratory
of the Rockies, *Dataset of Generative AI Workload Power Profiles*, OpenEI submission 8651
(<https://data.openei.org/submissions/8651>), issued 2026-03-31: high-resolution (5 Hz / 10 Hz) power profiles of
generative-AI workloads (LLM and image generation; training and inference; several node counts) on the Kestrel HPC
system, plus **modelled** whole-facility profiles from a bottom-up energy model. **Use only the measured node/job
profiles. The modelled facility profiles are a model's output and are not data for this experiment; name them, tag
them SOURCED-model, and leave them out of every readout.** Record the licence text verbatim in the profile. If the
licence restricts redistribution of derived results, carry that onto every verdict.

**Secondary (use only if the profile shows the primary is thin).** MIT Supercloud Dataset (GPU power via `nvidia-smi` at
100 ms intervals; licence per the repository, confirm). ClusterWise (OLCF Summit; CC BY 4.0; per-GPU power; sampling
rate to confirm — if ≥ 1 s, it is too slow and is excluded).

**Excluded.** Scheduler-level traces (Alibaba, Philly, Acme): minute-scale.

**The "rack".** Synchronous swings are a property of one job, not of a sum of unrelated nodes. The unit of analysis is
**one multi-node job's total power** (sum of its nodes' traces at the same timestamps), never a sum of unrelated jobs.
If the primary files are per node, the profile must show how nodes map to jobs; if they are already per job, say so.

---

## 3. Mandatory first step — profile (`results/DC1/DC1_profile.md`, commit before controller code)

1. **Dataset facts:** licence (verbatim), file list with sizes, per-file sampling rate, duration, node count, workload
   type (training / inference; LLM / image), and how nodes map to jobs.
2. **Per job trace:** power p5 / p50 / p95 / max (W); relative swing amplitude `A = (p95 − p5) / max`; the two-state
   structure (fraction of time above the midpoint; median dwell in each state); dominant periodicity (spectral peak in
   0.05–2.5 Hz and its share of variance); step steepness (p95 of |ΔP| per sample, as a fraction of max).
3. **Aggregate:** distribution of A and of the dominant period across jobs; how many jobs have a spectral peak carrying
   ≥ 20 % of variance (the "periodic" subset).
4. **Power gate:** at least **10 jobs** with A ≥ 30 %, duration ≥ 10 min and sampling ≥ 5 Hz. Fewer is UNDERPOWERED:
   report and stop. Report separately how many of them are "periodic" by the §3.3 definition; under 5 makes the
   forecasting readout descriptive only.
5. **Folds (CHOSEN, fix now):** split jobs into two folds balanced by workload type and A; list them.
6. **Fix the spec and the controller forms (§4) with the numbers filled in.**

---

## 4. Method (to be pre-registered after §3)

### 4.1 Plant

Upstream power `P_up(t) = P_load(t) − P_s(t)`, where `P_s` is the storage element's discharge power (negative when
charging). State of energy `0 ≤ SoE(t) ≤ E`; `|P_s| ≤ P_max_s`. Lossless storage in the primary; round-trip efficiency
0.90 as a sensitivity. Time step = the trace's sampling period.

### 4.2 Spec (ASSUMED; fix the numbers in the pre-registration; sensitivity at two more settings)

A **ramp-rate limit** on the upstream power: `|ΔP_up / Δt| ≤ R_max`, with R_max = **10 % of the job's max power per
second** as the primary (sensitivity: 5 %/s and 20 %/s). This is the style of utility constraint described by Choukse
et al.; the number is not SOURCED from any utility and is tagged ASSUMED. A **dynamic-range** readout (p95 − p5 of
P_up as a fraction of max) is reported as secondary, not decided on.

### 4.3 Controllers (all causal except the oracle; forms fixed here, never tuned on evaluation jobs)

| ID | Sees | Action |
|---|---|---|
| **K0 reactive (Tier M comparator)** | `P_load(t)`, `SoE(t)` | Rate-limits `P_up` toward `P_load` at R_max; the storage absorbs the difference while SoE allows; recharges or discharges toward a **fixed SoE target** at ≤ R_max when the load is steady. The SoE target (fraction of E) is **fitted on the calibration fold** (grid 0.3–0.7). |
| **K1 forecaster** | K0's inputs plus the last **W** seconds of `P_load` (W ∈ {1, 5, 30} s) | A fixed-form predictor: **seasonal-naive** with the period taken from the autocorrelation peak of the window (fallback: persistence when no peak clears a fixed threshold). Pre-positions SoE ahead of the predicted next step (raise SoE before a predicted rise, lower it before a predicted fall), then acts as K0. One gain parameter fitted on the calibration fold. |
| **K1-sh (shuffle)** | as K1, with the W-second window **time-shuffled** before prediction | Same predictor, same fitted parameters. Destroys the periodicity the forecaster lives on. |
| **K∞ oracle** | the next H seconds of `P_load` (H = the primary W) | Optimal pre-positioning with perfect foresight (ceiling). |

### 4.4 Primary outcome

For each controller and job, the **minimum storage energy `E*`** (J) at which the spec is violated in **≤ 0.1 %** of
frames, found by bisection on E with `P_max_s` set to twice the job's swing (sensitivity: equal to the swing). Report
`E*` as a multiple of (job max power × 1 s) so jobs are comparable.

- **G = E*(K0) / E*(K1)** per job; **G_sh = E*(K0) / E*(K1-sh)**; **G_∞ = E*(K0) / E*(K∞)**.
- Headline: median G over evaluation jobs with a job-bootstrap CI (1,000 resamples, seed 0), both fold directions
  averaged.
- **Memory readout:** the smallest W at which median G is within 5 % of its maximum over the W grid, `W*`.

### 4.5 Decision (fill the numbers in the pre-registration; defaults below)

| Verdict | Condition |
|---|---|
| UNDERPOWERED | §3.4 gate fails |
| **FORECASTING SAVES STORAGE** | median G ≥ **1.25**, CI lower bound > 1, **and** median G_sh < **1.10** |
| **REACTIVE SUFFICES** | median G < **1.10** |
| **UNCLEAR** | anything else (including G ≥ 1.25 with G_sh ≥ 1.10: the gain is not from history) |
| ↳ **NEEDS HISTORY** | FORECASTING SAVES STORAGE **and** W* > 1 s |
| ↳ **NO HISTORY NEEDED** | FORECASTING SAVES STORAGE **and** W* ≤ 1 s |

Report G_∞ beside every G so the gain is read against its ceiling. Report the "periodic" subset separately.

### 4.6 Controls and sensitivity

1. **Time-shuffle** (K1-sh) with its own fitted parameters.
2. **Held-out jobs:** every fitted quantity (SoE target, forecaster gain) comes from the calibration fold; two folds,
   both directions.
3. **Best reactive option:** K0 with a fitted SoE target, not a fixed 50 %.
4. **Sensitivity:** R_max at 5 %/s and 20 %/s; η = 0.90; `P_max_s` equal to the swing; violation budget 0.5 %;
   decimating the primary traces to 1 Hz (if G collapses, the 5–10 Hz resolution was load-bearing, which is itself a
   memory/bandwidth statement).
5. **Inference vs training:** report G by workload type; the mechanism is expected to live in training.

---

## 5. Deliverables

1. `results/DC1/DC1_profile.md` and `results/DC1/DC1_preregistration.md`, committed before controller code (first stage).
2. After approval: `analysis/DC1_storage.py`; `results/DC1/results_DC1.md` (verdict first, with the licence and the
   resolution caveat), `dc1.json`, plots (E* per controller per job; G vs W; one job's P_load / P_up / SoE for each
   controller), and one row each in `results/X/README.md` and `results/RESEARCH_DOSSIER.md` §9, plus a dated note under
   ANGLES §B.2.

## 6. What not to do

- Do not use the modelled whole-facility profiles as data.
- Do not sum unrelated jobs to make a "rack".
- Do not tune the predictor form, the spec or the SoE target on evaluation jobs.
- Do not report G without G_sh and G_∞ beside it, or without W*.
- Do not convert E* to dollars, kW of capex or rack counts here.
- Do not claim anything at phase level or about GPU-side smoothing.

---

*Confirm the licence. Profile the swings. Fix the spec and the predictor before any controller exists. Beat a fitted
reactive controller, survive the time-shuffle, and say how many seconds of history it took.*
