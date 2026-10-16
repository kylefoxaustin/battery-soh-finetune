# Experiment E — power analysis (brief §3): can these data resolve a tighter worst-case bound?

Run 2026-10-13, **before any bound estimator was built**. Brief: [`Experiment E Brief.md`](../../Experiment%20E%20Brief.md).
Scripts: `analysis/E_power.py` (Changan → `power_changan.json`), `analysis/E_power_yuasa.py` (Yuasa →
`power_yuasa.json`), `data/changan_cells.py` (per-cell re-ingest). Tags: MEASURED / DERIVED / ASSUMED / SOURCED /
UNGATED. **Every Changan number is relative to DERIVED labels with ≈ 3–4 % per-unit noise.**

## Bottom line

| Dataset | E1 / E2 / E3 (per-unit bound, coverage-gated) | E4 (per-cell vs pack-scalar) | E5 | Verdict |
|---|---|---|---|---|
| **Changan** (CC BY-NC-SA) | **NO-GO.** Even an *oracle* that knows each unit's true offset and spread recovers ≤ 0.4 % of capacity at α = 0.05 and ≈ 1 % at α = 0.01 — at or below the ≈ 0.8–0.9 % the data can resolve. α = 0.001 cannot be verified at all. | **Conditional GO** — one pre-registered pre-check (§5), which can only fail or open the door | follows E4 | |
| **Yuasa** (MIT) | **NO-GO.** One 12.5 h snapshot: no time axis, so no forecast and no held-out coverage test; 27 modules can't verify any α ≤ 0.1. Its labels are model estimates, not ground truth. | **Descriptive only (UNGATED)** — mean-vs-weakest-cell per module | descriptive only | |
| **Both** | | | | **If the §5 pre-check fails: INCONCLUSIVE**, with an upper bound — on Changan, pack-scalar per-unit information cannot tighten the bound by more than ~1 % of capacity at any α we can verify. |

**Outcome (added after the pre-check ran):** the §5 pre-check **failed** — out-of-fold R² −0.02 (primary) / −0.18
(strict) vs thresholds 0.26 / 0.39. **E4 NO-GO → final verdict INCONCLUSIVE.** See [`results_E.md`](results_E.md).

## 1. Corrections to the brief, found while executing it

1. **Yuasa `Q` is not ground truth** (brief §2.2 says "per-cell capacity ground truth … rig-validated, lab-grade").
   The 324 `Q`/`Q_sigma` values in `validation_cells.json` are the paper's own **model estimates** — written by
   `main.jl` from its 324-cell recursive-GP fit to the 12.5 h field window (`build_validation_export`,
   `yuasa/src/ocv.jl`). The reference check covers 96 cells (8 modules of phase P3) using a low-power cycle
   *on the same onboard sensors*: RMSE **1.25 Ah absolute, 0.55 Ah module-centred** (SOURCED, paper §Validation).
   The authors write that it "shares the extrapolated reference points, leaving the absolute capacity scale
   unverified. A conclusive assessment would require characterizing cells individually in the laboratory."
   `Q_sigma` (median 0.48 Ah = 0.64 %) is the fit's own posterior uncertainty — a lower bound on label error, not
   a measured error. → Tag Yuasa `Q` as **SOURCED (model estimate)**, never MEASURED.
2. **Yuasa is LMO/graphite second-life** (GS Yuasa LEV50N, 2P → 100 Ah logical cells, 12s per module, 27 modules;
   SOURCED). Changan is NMC. "Corroboration" across them is cross-chemistry at best.
3. **The 31 % figure is a different metric from ours.** It is lumped-module SOH vs cell-aggregated module SOH,
   where module capacity = min over cells of chargeable + min of dischargeable capacity, so it **includes SOC
   imbalance** (paper Eq. 16–17). It is 4–16 % for 25 of 27 modules, and 24 % / 31 % for the two modules with a faulty
   cell (P1M6, P3M5). It is not a coverage or bound result.
4. **Changan per-cell columns: confirmed, but they were dropped by choice, not missed.** `changan_slim.py` decodes
   RAR5 fine via libarchive (no `unrar` needed; 7z is not used). It discarded the list columns deliberately, and
   `dataset_profile.md` lists "96 series cells, 32 temperature probes" as measured. What *is* new: the lists are
   **less clean than the brief says.** On vin3 (all 2,556,550 frames):
   - 6.0 % of non-placeholder frames have valid scalar telemetry but **no cell list**, clustered in 46 days around 130 k km.
   - 2.1 % of the later-life frames checked (28 of 332 days) carry a cell list whose min/max is **up to 0.4 V away**
     from the same frame's scalar min/max — a stale or misaligned vector. The brief's "matched to < 1e-6 V" held on
     the first ~1.2 M frames only.
   - The extractor flags every frame (`sync`) and keeps full vectors from synced frames only. Fleet-wide rates: §4.

## 2. Changan — is the per-unit signal big enough?

Frozen fleet models (the four fold models from `results_large.md`, unchanged) scored on their held-out units; residual
r = label − prediction. DERIVED from MEASURED predictions against DERIVED labels.

| | Primary (94 units, 5,550 labels) | Strict (45 units, 2,049 labels) |
|---|---|---|
| Residual SD between units (persistent per-unit offset) | 2.18 Ah | 1.87 Ah |
| Residual SD within units | 4.11 Ah | 3.22 Ah |
| Share of residual variance that is between-unit | **22 %** | **25 %** |
| Label-noise estimate (`dataset_profile.md`) | 4.76 Ah | 3.84 Ah |
| Within-unit scatter vs label noise | **no larger than the noise estimate** | **no larger** |
| Sampling SE of a per-unit offset from its first 5 / 10 / 20 labels | 1.84 / 1.30 / 0.92 Ah | 1.44 / 1.02 / 0.72 Ah |

**Label noise vs genuine variation (brief §3, third bullet):** at most ~¼ of the residual variance is genuine,
persistent unit-to-unit difference the fleet model misses. The other ~¾ is within-unit scatter the same size as the
label noise. A per-unit bound can at best remove the ¼. And estimating a unit's offset from 5–10 labels carries
a sampling error (1.0–1.8 Ah) comparable to the offset itself (1.9–2.2 Ah) — which the bound has to give back to
stay calibrated.

**One caveat cuts the other way, and it is the reason for §5:** the label is *charge capacity to the first cell
reaching 4.2 V*. Part of its "noise" may be real charge-to-charge variation in which cell limits, and how early —
cell imbalance. Pack-scalar data cannot separate that from measurement error. Per-cell data, in principle, can.

## 3. Changan — the oracle ceiling vs what can be resolved

**Oracle bounds** (DERIVED, upper bounds on any real estimator): the fleet bound is pred − q, with one offset q
calibrated so a fraction α of labels fall below it (unit-balanced, in-sample — the most favourable case for the
fleet bound too). The *shift* oracle is told each unit's true mean offset; the *shift + scale* oracle is told its
true mean and SD — both taken from the test data. Recovered % = (L_oracle − L_fleet) / C_nominal (122.6 / 122.1 Ah).

| α | Fleet bound offset (buffer) | Gaussian label-noise floor z·σ | Oracle shift (median % / units tighter) | Oracle shift+scale (median % / units tighter) | Expected violations, all labels | Realized α, 95 % cluster-bootstrap CI (× α) |
|---|---|---|---|---|---|---|
| **Primary** | | | | | | |
| 0.10 | 4.35 Ah (3.5 %) | 6.10 Ah | +0.13 % · 50/94 | +0.18 % · 54/94 | 555 | 0.84–1.17 |
| 0.05 | 6.14 Ah (5.0 %) | 7.83 Ah | −0.08 % · 45/94 | +0.44 % · 55/94 | 278 | 0.79–1.21 |
| 0.01 | 10.91 Ah (8.9 %) | 11.08 Ah | −0.61 % · 34/94 | +1.08 % · 64/94 | 56 | 0.67–1.33 |
| 0.001 | 21.34 Ah (17.4 %) | 14.71 Ah | +1.74 % · 80/94 | +4.18 % · 77/94 | **5.6 (in 3 units)** | **0–1.70** |
| **Strict** | | | | | | |
| 0.10 | 4.26 Ah (3.5 %) | 4.93 Ah | +0.33 % · 27/45 | +0.12 % · 24/45 | 205 | 0.76–1.25 |
| 0.05 | 5.51 Ah (4.5 %) | 6.32 Ah | +0.05 % · 23/45 | +0.23 % · 27/45 | 102 | 0.69–1.36 |
| 0.01 | 10.21 Ah (8.4 %) | 8.94 Ah | +0.85 % · 32/45 | +1.49 % · 34/45 | 20 | 0.37–1.64 |
| 0.001 | 17.22 Ah (14.1 %) | 11.88 Ah | +0.36 % · 27/45 | +4.20 % · 38/45 | **2.0 (in 1 unit)** | **0–0.88** |

**Smallest resolvable buffer change (brief §3, first bullet):** a paired gap across units, two-sided, Bonferroni
over the brief's grid (4 estimators × 3 horizons × 2 label sets × 2 datasets = 48 → α′ = 0.00104), 80 % power,
with the gap's across-unit SD optimistically set to the between-unit residual SD:
**≈ 0.76 % of capacity (0.93 Ah) primary, ≈ 0.94 % (1.15 Ah) strict** (DERIVED). A real estimator's gap varies
more than that, so the true MDE is larger.

**Range being tested (brief §3, second bullet) — CHOSEN, stated now:** a recovered-capacity effect of
**1 – 10 % of C_nominal**. Below 1 %, it is at or under resolution here, and too small to matter against a few-percent buffer.

**Reading:**

- **α = 0.001 (the brief's example) cannot be verified.** About 5.6 (primary) / 2.0 (strict) violations are expected
  across *every* label, concentrated in 3 / 1 units. The realized-α CI runs from 0 to 1.7× nominal, so a bound
  that under-covers 1.7× passes and one that never violates also passes. The coverage gate (§5.3) would be
  decorative. The oracle's apparent 1.7–4.2 % at α = 0.001 is set by the same handful of extreme labels. It is
  the "pleasing number" RoE #1 warns about. **α = 0.001 is rejected for this experiment.**
- **At the α values that can be verified (0.10–0.01), coverage CIs are ±16–33 % relative (primary).** The
  *oracle* recovers −0.6 to +1.1 % (primary) and +0.05 to +1.5 % (strict). That is at or below the MDE, and it is
  the ceiling — a real per-unit estimator must estimate what the oracle is given, and pay the 1–1.8 Ah sampling
  error.
- **The fleet bound is already at the label-noise floor.** For α = 0.10 and 0.05 (both label sets) and α = 0.01
  (primary), the fleet offset is at or *below* z·σ_noise. The noise estimate is a median per-unit SD about a
  linear fit, so this comparison is approximate; strict at α = 0.01 is the exception (10.2 vs 8.9 Ah). A bound
  checked against labels cannot be tighter than the labels' own scatter.
- **So: Changan NO-GO for E1/E2/E3 with pack-scalar information.** That is not a finding that the effect is absent.
  It is a finding that with these labels, no estimator using pack-level history can produce an effect this test
  could see.

## 4. Changan per-cell re-ingest (brief §2.1) — fleet-wide rates

All 300 vehicles, 820,695,014 raw frames (MEASURED, `runs/changan_cells.log`; 0 extraction errors after the
corrupted-token fix):

| Defect | Fleet rate | Per vehicle |
|---|---|---|
| Placeholder frames (totalvoltage ≤ 0) | 0.10 % of raw | — |
| **Malformed** (cell list ≠ 96 or probe list ≠ 32 values, or an unparseable token) | **5.62 %** of non-placeholder | median 5.79 %, p90 8.76 %, max 23.2 % |
| **Unsynced** (cell-list min/max ≠ scalar min/max by > 0.5 mV) | **1.22 %** of valid | 0 % in most vehicles; > 0.1 % in 56 of 300; p90 5.5 %, max 29.8 % |

The brief's 0.4 % malformed rate (one 200 k-frame sample) understates the fleet rate ~14×. Desync is concentrated:
most vehicles have none, a minority have a lot. Every downstream per-cell feature uses synced frames only.
148 M full 96-cell vectors are kept (71 GB).

## 5. The one open door: does per-cell data explain the "label noise"? — PRE-REGISTERED PRE-CHECK

Per §2's caveat, the only way Changan can support a resolvable tightening is if per-cell state explains a
substantial share of the within-unit residual that pack-scalar data treats as noise. The test below is
**declared and committed before the per-cell data has been joined to a single label.**

- **Data:** held-out units and frozen fleet residuals exactly as in §2–3 (same 4 fold models, same labels).
- **Features (CHOSEN), causal only:** computed from synced per-cell frames **strictly before the label's charge
  session began**, over the preceding 5 k km of the unit's history (fallback: preceding 30 days if < 5 k km of
  data). Nothing from the label's own charge session is used — its top-of-charge spread is mechanically part of
  the label definition.
  1. median top-of-charge cell spread (max − min, mV, frames in charge with max cell ≥ 4.15 V)
  2. median rest-frame cell spread (|I| < 1 A)
  3. weakest cell's mean deviation from the pack mean, rest frames (mV)
  4. cross-cell SD of per-cell mean deviation, rest frames (mV)
  5. the slope of feature 3 over the preceding 30 k km (mV per 10 k km)
  6. median probe-temperature spread (°C)
- **Model (CHOSEN):** ordinary least squares on the six features, plus the same six for the *min/max-only*
  equivalent where one exists (1, 2 from the scalar columns), cross-validated **by unit** (the same 4 folds as the
  fleet models).
- **Target:** within-unit residual (residual minus the unit's own mean residual from its *training-side* labels
  only — i.e., each held-out unit is centred with its first 10 labels, and scored on the rest).
- **Metric:** out-of-fold R² of the within-unit residual, per label set.
- **Threshold (DERIVED from §3, Gaussian approximation):** the explained share needed for the shift+scale gain
  to reach the MDE: z·σ_w·(1 − √(1 − R²)) ≥ MDE.

  | Label set | R² needed at α = 0.05 | at α = 0.01 |
  |---|---|---|
  | Primary | **≥ 0.26** | ≥ 0.19 |
  | Strict | **≥ 0.39** | ≥ 0.28 |

- **Decision rule:** **E4 GO** on Changan only if out-of-fold R² ≥ the α = 0.05 threshold on **both** label sets
  **and** the per-cell features beat the min/max-only features by ≥ 0.05 R². Otherwise **NO-GO on both datasets →
  final verdict INCONCLUSIVE.** No re-running with other features, windows or thresholds after seeing the result.
- **If GO, the main experiment's α (CHOSEN now, not later):** primary **α = 0.05**, secondary α = 0.01; tolerance
  for the coverage gate = realized α inside its own 95 % cluster-bootstrap CI containing nominal, and point
  estimate ≤ 1.25 × nominal. Horizons: 0–5 k, 5–10 k, 40–80 k km (the rolling bands from `results_large.md`).

## 6. Yuasa — does the labelled set change the answer? (brief §3, fourth bullet)

| Item | Value | Tag |
|---|---|---|
| Cells / modules / cells per module | 324 / 27 / 12 in series (each a 2P logical cell, 100 Ah nominal) | SOURCED |
| Per-cell Q, median (range) | 75.4 Ah (38.0–79.3) | SOURCED (model estimate) |
| Between-cell SD of Q (excluding the 2 faulty cells) | 3.66 Ah (2.66 Ah) | DERIVED |
| Q_sigma median / max | 0.48 Ah (0.64 %) / 1.79 Ah | SOURCED (fit posterior) |
| Reference check, 96 cells: RMSE absolute / module-centred | 1.25 Ah (1.7 %) / 0.55 Ah (0.7 %) | SOURCED |
| Module (mean − min) Q / mean, median (range) | **0.85 %** (0.63–2.17 % for 25 modules; **24.4 % and 44.2 %** for the two faulty-cell modules) | DERIVED |
| Time axis | one 12.5 h snapshot; one Q per cell | SOURCED |
| P(zero violations \| perfectly calibrated), 27 modules, α = 0.10 / 0.05 / 0.01 | 0.06 / 0.25 / 0.76 | DERIVED |

**Answer: it changes the label-precision question, not the testability question.** Yuasa's *relative* (within-module)
label precision is ~5× better than Changan's (0.55 Ah of 75 Ah vs 4–5 Ah of 122 Ah), but its absolute scale is
unverified per the authors. Its structure can't support E1–E3/E5 as the brief defines them: no forecast origin or
horizon exists, and 27 units can't verify coverage at any α ≤ 0.1. **NO-GO for the gated hypotheses.**

It *can* support a **descriptive, UNGATED E4 figure**: how much a module-mean (lumped) view overstates the
weakest-cell capacity. That is 0.6–2.2 % in 25 of 27 modules, and 24–44 % only where a physical cell has failed. That shape — small
everywhere except at a fault — is worth reporting beside the pre-registered 31 %/23 % reference point, with the
metric difference in §1.3 stated.

## 7. What data would settle it (for the INCONCLUSIVE branch)

All four needs at once; no public set found so far meets more than two:
1. **Lab-grade capacity labels** (noise ≪ 1 % of capacity) — Yuasa's reference check, UMich CtCV, NREL/INL pack tests;
2. **repeated over a long field history per unit** (many labels per unit, so per-unit bounds have something to learn
   from) — Changan only;
3. **per-cell telemetry** alongside — Changan, Yuasa, UMich;
4. **enough units for coverage at the α of interest** — roughly ≥ 10/α independent unit-level trials (≥ 200 units
   for α = 0.05; ≥ 10,000 for α = 0.001).

The optional §2.3 sets (UMich CtCV, NREL/INL) were **not downloaded**. From the brief's own descriptions they meet
(1) and (3) or (1) only, and neither has (2), so they cannot rescue E1–E3. UMich could strengthen a descriptive
E4/E5 (capacity vs cell-to-cell spread under lab labels) if wanted.

## 8. Licence map

| Conclusion | Rests on |
|---|---|
| Pack-scalar per-unit bounds can't resolvably tighten (§3) | Changan (CC BY-NC-SA) — **non-commercial only** |
| α = 0.001 unverifiable at these N | Arithmetic; applies to any dataset of this size |
| Weakest-cell vs module-mean gap: ~1 % normally, 24–44 % at a fault | Yuasa (MIT) — permissive, but labels are SOURCED model estimates |
| Per-cell pre-check (§5), if run | Changan — non-commercial only |
