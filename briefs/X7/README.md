# Build Brief — Experiment X7: does a per-cell electro-thermal observer remove hottest-cell temperature margin?

**Licence of this document:** public domain (CC0). **Written:** 2026-10-30. **Origin:** ANGLES report §B.5 / §C.4
([`results/OPEN_PROBLEM/ANGLES_REPORT.md`](../../results/OPEN_PROBLEM/ANGLES_REPORT.md)), ranked first in
[`briefs/NEXT_EXPERIMENTS/README.md`](../NEXT_EXPERIMENTS/README.md).

> ## ▶ CLOSED 2026-10-30 — UNDERPOWERED at the profile stage; reviewer accepted; do not run
>
> The first stage was done at `8a468ad` ([`results/X/X7_profile.md`](../../results/X/X7_profile.md),
> [`results/X/X7_preregistration.md`](../../results/X/X7_preregistration.md)). The §3.5 power gate fails under any fold
> assignment (3 of 14 McMaster runs reach a 3 K hot spot for ≥ 10 % of frames; 8 needed), and two structural facts cap
> the recoverable margin at the decision bar regardless of the gate: the thermistors read in **1 K steps**, and a
> one-probe-per-three-cells view is **never more than 1.0 K below the hottest cell** in any frame. The hot spots sit at
> fixed, probed positions (cells 1, 28, 29). The reviewer agrees with the session's recommendation: **relaxing the gate
> would not lift the ceiling**, so no observer is fitted. The question is not answerable on public data at this sensor
> resolution (rule 9).
>
> **Kept from X7 for any future thermal brief:** (a) put sensor resolution and the raw probe-max gap in the profile gate,
> because they can decide the experiment before any model exists; (b) score the **mean issued bound**
> `B = mean(T̂_hot + κ_T − T_hot)`, not the margin κ_T alone, because a biased-high estimator earns κ_T = 0 for free
> (X7-P1). The original first-stage instructions are kept below for the record.
>
> ## ▶ START HERE (superseded: first stage done; see the CLOSED box above)
>
> 1. `git pull` on `main`.
> 2. Read this brief end to end, then `results/X/README.md` (the McMaster corrections), `results/X/X2M2_preregistration.md`
>    and the McMaster loader and per-cell-R identification in `analysis/X2_replay.py`. Reuse them; do not re-derive R.
> 3. Write `results/X/X7_profile.md` (§3) and `results/X/X7_preregistration.md` (§4 with every threshold filled in).
> 4. Commit both with "before observer code" in the commit message. **Write no model or scoring code.**
> 5. Set the Status line in `NEXT_TASK.md` to `AWAITING APPROVAL <commit-hash>`, push, and stop.
>
> The reviewer will then edit this box to "APPROVED, run it now" or send changes.

---

## 0. Why X7 exists

The programme's one robust positive is that **per-cell resistance is a stable, identifiable property** that removes
margin: X2-F needed κ ≈ 1.10 for a per-cell limiter against κ ≈ 1.35–1.45 for min/max, and min/max's margin did not
transfer to unseen vehicles. That was cashed out only at the top of charge, on voltage.

The customer's C1 ("1 °C cooler charging is worth ~$100") was valued by `lifecost` at $26 / $58 / $124 per kelvin, but
nothing asked **how a controller gets a kelvin.** One way is not cooling at all: a probe-based limiter must charge to
*T_probe + margin* because it sees one probe per several cells (Changan: 32 probes for 96 cells) and only their
surfaces. A per-cell electro-thermal observer, driven by each cell's own I²R (which needs the per-cell R that X2-F
showed is real), estimates every cell's temperature and removes part of that margin — the thermal twin of X2-F.

X7 asks the testable half of that on data in hand:

> **On a pack with a thermistor on every cell, how much hottest-cell margin does probe interpolation carry that a
> per-cell observer does not, and does a coupled (neighbour and coolant) model beat a lumped one?**

The second clause is the **tier readout**: a lumped per-cell model is an MCU workload; a coupled high-order model is
where an A-core might matter. Both clauses have clean kill criteria.

**What X7 cannot test, stated up front.** McMaster's thermistors are **surface** sensors. X7 measures the
*unobserved-cell* (spatial) margin, not the *core-vs-surface* margin. No public dataset with embedded core
thermocouples on a multi-cell pack is known; if the session finds one, name it in the profile with licence and ask
before using it.

---

## 1. Rules of engagement (unchanged from X5/X6)

1. A pleasing number is a suspected defect until gated.
2. Tag every figure MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED.
3. Gate in the same run as the measurement.
4. State CHOSEN versus IMPOSED inputs.
5. Show sensitivity, not one hero number.
6. A clean NO GAIN, TIER M SUFFICES or UNDERPOWERED is a valid outcome.
7. **Pre-register before observer code.** Never move a threshold after seeing results. Every later change is a numbered
   deviation.
8. No kWh, cost, range or regulatory claim. (The $/K conversion stays in `lifecost`, not here.)
9. Carry the licence (McMaster, **CC BY 4.0**) and the caveat on every verdict:
   *"surface thermistors on a 72S PHEV pack under drive cycles at ~0.9 SOC; spatial margin, not core margin."*
10. Every comparison uses Tier M's **best option**: probe interpolation with a *fitted* margin, not a fixed guess.
11. Every per-cell claim gets a **shuffle control** that scrambles cell identity at every time step.

---

## 2. Data

McMaster 72S (SB LiMotive 5.2 Ah PHEV cells, 72 in series; dataset README Naguib et al., Borealis
doi:10.5683/SP3/UYPYDJ; **CC BY 4.0**), already downloaded. 14 runs of 1 Hz drive-cycle data (758–11,188 s each),
charge-sustaining at about 0.9 SOC, with per-cell voltage and a per-cell thermistor; current sign I > 0 = charge
(regen). Known facts from `results/X/README.md` (DERIVED, read-only probes, 2026-10-15):

- Thermistors on cells **12 and 35 are dead** (constant 1.0 °C in `HWFET_15C_ModuleBlocked_Long`). Exclude them from
  truth and from any probe set in every run; check every run for stuck channels in the profile.
- Real per-cell spread: median 5 °C, p95 8 °C, max 9 °C in the module-blocked run; at most 11 °C across all runs
  (Fan-off/on run); minimum cell temperature ≥ 10 °C. The Fan-off run reaches 46 °C.
- There are no charge sessions and no cold regime. X7 does not need either.

No new dataset without asking.

---

## 3. Mandatory first step — profile (`results/X/X7_profile.md`, commit before observer code)

1. **Per run:** duration, ambient/chamber temperature and fan or blocking condition as the file names and README give
   them (SOURCED), current p5/p50/p95 in A and C, number of current steps |ΔI| ≥ 0.3 C (the R-identification events),
   hottest-cell minus median temperature p50/p95/max, stuck or missing thermistor channels.
2. **Spread available to recover:** per run, the time fraction in which (T_hot − T_median) ≥ 2 K and ≥ 4 K.
3. **Probe emulation layout (CHOSEN, fix now):** the Tier M comparator sees **one thermistor per three cells**, cells
   1, 4, 7, …; if a chosen probe cell is dead, take the next cell up and record it. Report the mean distance (in cells)
   from each unobserved cell to its nearest probe.
4. **Fold assignment (CHOSEN, fix now):** split the 14 runs into two folds of 7, balanced by condition (fan state,
   blocking, chamber temperature) so that each fold contains at least one high-spread run; list the folds.
5. **Power gate:** at least **4 runs per fold** with (T_hot − T_median) ≥ 3 K for ≥ 10 % of frames. Fewer is
   UNDERPOWERED: report and stop.
6. **Is the hottest cell already a probe cell?** Fraction of frames in which the hottest cell is in the emulated probe
   set. If ≈ 1, the Tier M comparator sees it for free and the margin question is nearly moot; say so.

---

## 4. Method (to be pre-registered after §3)

### 4.1 Truth and the quantity scored

Truth is the measured thermistor temperature of every live cell at 1 Hz. The scored quantity is the **hottest live
cell's temperature** at each frame, T_hot(t), and each model's estimate T̂_hot(t). The error is e(t) = T_hot − T̂_hot
(positive = model under-estimates the hottest cell: the unsafe direction).

### 4.2 Models (all strictly causal at 1 Hz)

| ID | Sees | Estimate of each cell's temperature |
|---|---|---|
| **M0 (Tier M comparator)** | the 24 emulated probes; pack current | linear interpolation along the cell index between probes; T̂_hot = max over cells **plus a margin κ_T** fitted on the calibration fold (§4.4) |
| **M1 (lumped per cell)** | the 24 probes; pack current; each cell's R identified from current steps as in `X2_replay.py` (≥ 0.3 C steps, re-estimated every 60 s, ≥ 20 steps for history) | a 2-state (core, surface) lumped model per cell driven by I²·R_cell, with the probe cells' measurements assimilated by a fixed-gain observer; parameters (thermal capacitances, resistances, ambient coupling) fitted **once** on the calibration fold, shared across cells; T̂_hot = max over cells plus its own fitted κ_T |
| **M2 (coupled)** | as M1 | M1 plus nearest-neighbour conduction and a common coolant/ambient node, as a sparse state-space model of order ≈ 2 × 72 + 1; same fitting discipline; its own κ_T |
| **M1-sh, M2-sh (shuffle)** | as M1 / M2 with **R_cell permuted across cells independently at every time step** | same models, same fitting; their own κ_T |

Model forms, parameter counts and the observer gain structure are fixed in the pre-registration and never tuned on
the evaluation fold. Report the parameter values.

### 4.3 Two tasks

**Task A — accuracy.** p50 and p95 of |e(t)| on the evaluation fold, per model, pooled over runs and per run.

**Task B — margin.** For each model, the smallest κ_T (K, grid 0.0–10.0 in 0.1 K steps) such that the fraction of
evaluation-fold frames with T_hot > T̂_hot + κ_T is ≤ **0.2 %** (X2-F's bar), with κ_T **fitted on the calibration
fold** and checked on the evaluation fold (held-out safety, as X2-F). Report both the calibration κ_T and the realised
evaluation unsafe fraction. The quantity of interest is **Δκ = κ_T(M0) − κ_T(M1)** and **κ_T(M1) − κ_T(M2)**.

Two folds, both directions (fit on A, score on B; fit on B, score on A); the headline is the mean of the two
directions, with a run-level bootstrap (1,000 resamples, seed 0) for CIs.

### 4.4 Decision (fill exact numbers in the pre-registration; defaults below)

| Verdict | Condition |
|---|---|
| UNDERPOWERED | §3.5 gate fails |
| NOT INTERPRETABLE | any model's realised evaluation unsafe fraction > 0.3 % at its calibrated κ_T (report margins anyway, as X2-F did) |
| **SPATIAL MARGIN RECOVERABLE** | Δκ(M0 − M1) ≥ **1.0 K**, CI lower bound > 0, **and** M1-sh recovers < 0.5 K of it |
| **TIER M SUFFICES** | SPATIAL MARGIN RECOVERABLE holds **and** κ_T(M1) − κ_T(M2) < **0.5 K** (lumped ≈ coupled) |
| **COUPLING NEEDED** | SPATIAL MARGIN RECOVERABLE holds **and** κ_T(M1) − κ_T(M2) ≥ 0.5 K with CI > 0 and M2-sh does not match M2 |
| NO MARGIN TO RECOVER | Δκ(M0 − M1) < 1.0 K, or the hottest cell is a probe cell in > 90 % of frames (§3.6) |
| UNCLEAR | anything else |

Both TIER M SUFFICES and COUPLING NEEDED are complete, publishable answers. TIER M SUFFICES means the mechanism (B.5)
is real but moves to the tier-neutral list; COUPLING NEEDED is the first per-cell result in the programme where the
model order, not the information, carries the gain.

### 4.5 Controls

1. **Shuffle** (M1-sh, M2-sh): if the margin recovery survives scrambling which R belongs to which cell, it is not
   per-cell knowledge; it is the thermal model's smoothing.
2. **Held-out runs** (two folds) for every fitted quantity, including κ_T.
3. **Best Tier M option** (M0 with a fitted margin, not a fixed one). Sensitivity: M0 with **one probe per two cells**
   and **per cell** (the latter is the ceiling: M0 with a probe on every cell should need κ_T ≈ thermistor noise).
4. **Thermistor noise floor:** report the 1 Hz noise of the thermistor channels at rest (first 30 s of each run or the
   quietest window); no Δκ below twice that floor is claimed.
5. **Sensitivity:** probe layout offset by one cell (cells 2, 5, 8, …); κ_T bar at 0.1 % and 0.5 %; R held fixed from
   the first 60 s instead of re-estimated.

---

## 5. Deliverables

1. `results/X/X7_profile.md` and `results/X/X7_preregistration.md`, committed before observer code (first stage).
2. After approval: `analysis/X7_thermal.py`; `results/X/X7/results_X7.md` (verdict first, with the licence and the
   surface/spatial caveat), `x7.json`, plots (per-run T_hot vs each model's T̂_hot + κ_T; κ_T per model with CIs;
   Δκ vs spread), and the `results/X/README.md` and `results/RESEARCH_DOSSIER.md` updates (one row each).

## 6. What not to do

- Do not tune model forms, observer gains or κ_T on the evaluation fold.
- Do not report a Δκ without the shuffle controls and the thermistor noise floor beside it.
- Do not claim a core-temperature or charging-time result; this is a spatial, surface, drive-cycle margin.
- Do not convert kelvin to dollars here.
- Do not add a dataset without asking the reviewer.

---

*Profile first. Fix the probe layout and folds before any model exists. Beat the fitted-margin probe comparator,
survive the shuffle, and say whether lumped was enough.*
