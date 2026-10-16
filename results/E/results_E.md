# Results E — can per-cell data tighten a worst-case capacity bound?

Experiment E (rev 2), run 2026-10-13. Brief: [`Experiment E Brief.md`](../../Experiment%20E%20Brief.md). Read
[`E_power_analysis.md`](E_power_analysis.md) first. It is the experiment's main deliverable, because the brief's
§3 stop rule fired.

## Verdict: **INCONCLUSIVE** — the public data cannot resolve the effect, and its upper bound is small

**Changan numbers are against DERIVED labels with ≈ 3–4 % per-unit noise (4.76 Ah primary / 3.84 Ah strict on ≈ 122 Ah).**

1. **Pack-scalar per-unit bounds (E1–E3): cannot reach a resolvable effect, even as an oracle.** Changan
   (CC BY-NC-SA). A bound told each unit's *true* offset and spread from the test data recovers −0.6 % to +1.5 % of
   capacity at the verifiable α (0.10–0.01). The minimum detectable change is ≈ 0.8–0.9 %. Any real estimator does worse
   than the oracle. Only 22–25 % of fleet-model residual variance is persistent per-unit offset; the rest is scatter
   the size of the label noise. (DERIVED, `power_changan.json`.)
2. **α = 0.001 is unverifiable** on any dataset this size. It means ≈ 6 / 2 expected violations across every label,
   in 3 / 1 units. Rejected; α = 0.05 chosen instead (CHOSEN, committed before the pre-check).
3. **Per-cell data (E4) does not explain the label scatter. The pre-registered pre-check failed decisively** (below).
   This closes the only path by which Changan could have produced a resolvable tightening.
4. **Yuasa cannot test E1–E3/E5.** One 12.5 h snapshot (no forecast horizon), 27 modules (no α ≤ 0.1 verifiable), and
   per-cell `Q` that are the paper's own model estimates with an unverified absolute scale (SOURCED). It supports one
   descriptive, UNGATED number — below.

Per the brief's §3 rule (NO-GO on both datasets), the bound estimators, coverage gate, horizons, controls and E6
board footprint were **not built**. There is no bound whose upkeep could be measured, and running them anyway would
produce exactly the ungated tightness numbers §8 forbids.

## The pre-registered per-cell pre-check (E_power_analysis.md §5, committed fc9c79c before any per-cell/label join)

Question: do causal per-cell features — from synced frames strictly *before* each label's charge session, over the
preceding 5 k km — explain enough of the within-unit residual (the part pack-scalar data calls noise) to lift even
an oracle bound above the MDE? Script `analysis/E_precheck.py`, output `precheck.json`. DERIVED.

| | Primary (94 units, 4,610 scored labels) | Strict (45 units, 1,599) |
|---|---|---|
| Out-of-fold R², 6 per-cell features | **−0.020** | **−0.176** |
| Out-of-fold R², 2 min/max-only features | −0.010 | −0.129 |
| Per-cell gain over min/max | −0.009 | −0.047 |
| Pre-registered threshold (R² / gain) | 0.26 / 0.05 | 0.39 / 0.05 |
| **Result** | **FAIL** | **FAIL** |

Labels matched to a charge-session time: 100 % (0 unmatched). Missing features: ≤ 1.5 % per feature, imputed with
the training-fold median. That was the one implementation choice the pre-registration left open, and is disclosed
in the script.

**Post-hoc diagnostic (does not change the decision; `analysis/E_precheck_diag.py`, `precheck_diag.json`):** was
the failure a broken pipeline? No. All eight features are populated and vary. Their correlations with the target
are small but non-zero (|r| ≤ 0.08). Even *in-sample* — fitting and scoring on the same data, which can only
flatter the model — R² is 0.011 (primary) / 0.004 (strict), 20–100× below threshold. Between units, the six per-cell
features explain R² = 0.08 / 0.22 of unit-mean residuals in-sample, about what six random regressors give on
94 / 45 units (≈ p / (n − 1) = 0.07 / 0.14). The per-cell spread features and their scalar min/max equivalents
correlate identically with the target, as expected: max − min is the same number from either source.

## Per-cell signal fleet-wide (brief §2.1 asked to re-verify the sample table)

The brief's table showed one vehicle whose weakest cell (#20) drifted −21 → −79 mV over 31 k km. Across the 94
primary target vehicles (rest frames, first vs last third of each vehicle's history; MEASURED):

| | First third | Last third |
|---|---|---|
| Weakest cell's mean deviation from pack mean (median over vehicles) | −18.8 mV | −19.4 mV |
| Cross-cell SD of per-cell mean deviation (median) | 4.0 mV | 3.9 mV |
| Rest-frame max − min spread (median) | 31.5 mV | 30.0 mV |
| Same cell weakest in both thirds | 55 / 94 vehicles | |

**The sample vehicle is not typical.** Fleet-wide, a persistent weak cell exists in a majority of vehicles, but
neither its deviation nor the pack's spread grows with age at the median. That matches the pre-check: per-cell
voltage state in this fleet doesn't carry the capacity information the hypothesis needs.

## Data quality of the per-cell columns (brief §2.1; MEASURED, all 300 vehicles, 820.7 M frames)

| Defect | Fleet rate | Brief's figure |
|---|---|---|
| Malformed (cell list ≠ 96 / probe list ≠ 32 / unparseable) | **5.62 %** (per vehicle: median 5.8 %, max 23 %) | 0.4 % (one 200 k-frame sample) |
| Cell list out of sync with scalar min/max (> 0.5 mV, up to 0.4 V) | **1.22 %** (0 in most vehicles; > 0.1 % in 56 of 300; max 30 %) | "< 1e-6 V, all frames" |

## Pre-registered comparison point (Yuasa 31 % / 23 %), with ours beside it

| | Value | Tag |
|---|---|---|
| Paper: lumped-module SOH overestimate vs cell-aggregated module SOH | 4–16 % (25 of 27 modules); 24 % and 31 % (the two faulty-cell modules); SOC up to 23 % | SOURCED |
| Ours: module-mean Q vs weakest-cell Q (perfect-balancing view, paper's Eq. 17 limit) | 0.6–2.2 % (25 of 27 modules, median 0.85 %); 24.4 % and 44.2 % (the same two modules) | DERIVED from SOURCED estimates, **UNGATED** |

The metrics differ: the paper's figure includes SOC imbalance (3.5–6.5 Ah per module); ours isolates capacity
heterogeneity. Read together, they say capacity heterogeneity costs ~1 % of module capacity in a healthy module and
tens of percent only when a physical cell has failed. In this system, the large per-cell effect is a **fault
signal**, not a gradual buffer-sizing signal. That is a different use case from the one this brief tests. It
fits with — but, on 2 faulty modules, does not show — per-cell monitoring earning its keep through fault detection.

## What would settle it

All four together; no public set found meets more than two (details: `E_power_analysis.md` §7):
lab-grade capacity labels (noise ≪ 1 %) · repeated over long field histories per unit · with per-cell telemetry ·
on enough units to verify coverage (≳ 10/α unit-level trials: ≥ 200 units at α = 0.05).

## Inputs — chosen vs imposed

| Input | Value | Chosen / imposed |
|---|---|---|
| Fleet models, labels, folds | unchanged from `results_large.md` | imposed by prior runs |
| α | 0.05 primary (0.01 secondary); 0.001 rejected as unverifiable | chosen, committed before the pre-check |
| Effect range of interest | 1–10 % of C_nominal | chosen |
| Bonferroni family for MDE | 48 (4 estimators × 3 horizons × 2 label sets × 2 datasets) | chosen per brief §5.5 |
| Pre-check features, window, centring, model, thresholds | E_power_analysis.md §5 | chosen, committed before running |
| Per-cell frame filter | synced frames only | chosen, forced by the 1.2 % desync |

## Honest verdict

The brief asked whether per-unit and per-cell data can bound the worst case of usable capacity more tightly than a
fleet prior, at matched, verified risk. On the best public data available — the Changan 300-EV fleet, where the
capacity labels are ones we derived ourselves (≈ 3–4 % per-unit noise), and the Yuasa second-life system, whose
per-cell capacities are the authors' model estimates over one 12.5 h window — that cannot be shown.

Pack-level per-unit information has an oracle ceiling of about 1 % recovered capacity at any α we can verify,
which is at the resolution limit. Per-cell voltage features, under a test we fixed in advance, explain none of the
within-unit label scatter that limits the bound. The brief's example α of 0.001 cannot be verified on datasets of
this size at all.

This is **INCONCLUSIVE, with an informative bound**. It does not show that per-cell bounds can never help. It shows
that on these data the most a per-unit bound could plausibly recover is ~1 % of capacity, too small to detect,
and that the per-cell route adds nothing measurable on this fleet.

Caveats: the Changan labels are DERIVED and charge-limited by construction; the Yuasa numbers are SOURCED model
estimates on a different chemistry (LMO); the optional UMich and NREL sets were not examined; the E6 board footprint
was not measured because no bound was built.

**Licence:** every Changan-based conclusion (1, 3 and the per-cell data quality) is **non-commercial only**
(CC BY-NC-SA 4.0). The α-verifiability arithmetic is dataset-independent. The Yuasa comparison is MIT-licensed data,
but rests on the authors' model estimates.

**No regulatory or economic consequence is claimed or implied.**

## Post-review addendum (2026-10-15, independent review)

See [`review_2026-10-15/REVIEW.md`](../review_2026-10-15/REVIEW.md). The original text above is unchanged except where marked.

1. **The verdict stays INCONCLUSIVE.**
2. **The per-cell pre-check was close to unpassable by construction, so "failed decisively" overstates it.**
   - The within-unit residual it targets is nearly white: median lag-1 autocorrelation is +0.06 (primary) and +0.09
     (strict).
   - So no slowly varying 5 k km-window feature could explain 26 % of it (reviewer).
   - The OLS was fitted on un-centred features against a unit-centred target. That alone pushes out-of-fold R²
     negative.
   - Read §"pre-check" as "this test could not detect the effect", not as "per-cell adds nothing".
3. **Session covariates explain far more.** These are the covariates the design excluded: start SOC, segment
   duration, charge type. They explain out-of-fold R² ≈ 0.18 of label scatter (reviewer). The scatter is largely
   label construction, not cell state.
4. **"≤ 0.4 %" in the power analysis is 0.44 %.**
