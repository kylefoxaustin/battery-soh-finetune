# Independent adversarial review of Experiment G.2 (Beihang QAS: per-cell drift A vs min/max drift B)

Reviewer: independent, biostatistics / battery-fault-detection stance. Date 2026-10-15.
Scope: `results/G2/{G2_preregistration.md,results_G2.md,g2.json,features.csv}`, `analysis/G2_beihang.py`, `analysis/G2_plots.py`,
`results/RESEARCH_DOSSIER.md` §6, `results/G/G_dataset_search_extended.md`, the authors' released code (`Train_.py`, `Test_.py`,
`Function_.py`, Zenodo 14555916, local copy in scratchpad `dl_caocode/`), and the raw QAS tensors (393 vehicles), re-read through the
repo's restricted unpickler (`G2_beihang.load`, map_location=cpu). No repo file was modified; everything ran on CPU, niced, 8 procs.

Tagging: **[file]** = read from a repo file; **[recomputed: …]** = computed by me in this review. Scripts and outputs live in
`<scratch>/review/g2/` (`rescan.py`, `rescan2.py`, `stats_lib.py`, `adjust*.py`, `analyse*.py`, `*.out`, `rescan*_qas.csv`).

**Reproduction check.** My re-implementation reproduces the repo's A and B for all 393 QAS vehicles to ≤ 8e-13
[recomputed: `analyse_rescan.out` line 2]. The arithmetic in `G2_beihang.py` is correct; the dispute below is about what A measures
and about the cohort, not about bugs in the feature code.

---

## Bottom line

**The G.2 positive weakens substantially; the mechanistic claim collapses; the "A beats B" ordering survives only as a borderline,
confound-laden hint.**

- The faulty (335–392) and normal (0–334) vehicles were **not processed through the same pipeline**: 335/335 normals contain
  current-sentinel frames (median 14 % of rows), only 17/58 faulty do (median 0 %) — AUC of "sentinel fraction" = 0.14
  [recomputed]. Faulty records are also twice as fragmented (127 vs 62 contiguous runs, AUC 0.83), run hotter (T_max 41 vs
  31 °C, AUC 0.83), and reach deeper SOC (0.105 vs 0.23, AUC 0.25). The authors' own derived columns (x, z) differ by 2–3 orders of
  magnitude between cohorts. **The pre-registered five controls missed all of this** (they caught only temperature and rest fraction).
- The pre-registered primary (early-window A − B, CI excluding 0) **does not survive stratification**: within 2 °C temperature
  strata the A − B permutation p = 0.11; within temperature × rest-count strata p = 0.067 [recomputed]. A alone early stays at a
  stratified AUC ≈ 0.59–0.60 with p ≈ 0.03–0.05 — borderline, and the primary was the *difference*, not A alone.
- The headline late-window A (0.73) is **not drift**: shuffling block order (destroys any monotone trend) still gives AUC 0.71;
  an explicit between-block-variability feature gives 0.73; the up-drifting cell (max z) gives 0.62 [recomputed]. A is picking
  up "one cell whose rest deviation jumps around between blocks", and that feature collapses to 0.52 (p = 0.45) when stratified
  on late temperature × SOC-gap count. Late A itself falls to 0.60 (p = 0.11) under that stratification and to 0.59 in caliper
  matching.
- The early A − B edge is fragile to a one-word change in the definition: block **mean** instead of block **median** gives
  A 0.58 vs B 0.59 (A − B = −0.007) [recomputed].
- The "mileage sanity" check that supports row-order is vacuous for QAS: vin_1 column 2 is identically zero in every QAS vehicle
  [recomputed], so "non-decreasing in 100 % of QAS" is a tautology.

What survives: a weak early-window per-cell signal (AUC ≈ 0.59–0.61 in stratified/matched analyses) that is *not* explained by
the covariates I could measure, and a consistent (if small) B ≤ A ordering. That is a hypothesis for a properly controlled
follow-up, not a result. The dossier's one-line summary "Per-cell > min/max … survives adjustment" overstates it.

---

## CRITICAL

### C1. The two cohorts came through different data-processing paths; the pre-registered controls could not see it
Evidence [recomputed: `rescan.py` → `analyse_rescan.out`, "COHORT FINGERPRINTS"; DeLong 95 % CIs]:

| Fingerprint (whole record) | AUC faulty vs normal | faulty median | normal median |
|---|---|---|---|
| fraction of frames with current sentinel (|I| ≥ 900) | **0.138** (0.07–0.21) | **0.000** | 0.141 |
| vin_3 q[3] (current) minimum | 0.86 | −70 A | −1005 A (sentinel present) |
| authors' x[0] std | 0.19 | 0.041 | 1.39 |
| authors' z std (per-column median) | 0.20 | 0.0037 | 0.527 |
| authors' z abs max | 0.25 | 1.9 | 460 |
| number of contiguous runs (break at |ΔSOC| > 0.02 or |ΔT| ≥ 3 °C) | **0.83** | 127 | 62 |
| median run length (frames) | 0.22 | 88 | 258 |
| SOC jumps > 0.02 | 0.82 | 55.5 | 25 |
| T_max | 0.83 | 41 °C | 31 °C |
| T in last 10 % of rows | 0.83 | 28 °C | 22 °C |
| T in first 10 % of rows | 0.52 | 15 °C | 15 °C |
| SOC min | 0.25 | 0.105 | 0.23 |
| V min | 0.30 | 2.778 V | 2.896 V |
| early-window temperature slope across blocks | 0.82 | +1.2 °C/block | +0.44 °C/block |

Only 17 of 58 faulty vehicles have *any* sentinel rows; all 335 normals do. Whatever cleaning removed the invalid-current frames
from the other 41 faulty records was not applied to the normals. Removing rows also creates discontinuities, which is consistent
with the 2× fragmentation. The derived x/z columns (which the authors' MC-AE consumes) are on a completely different scale in
the faulty cohort, again pointing to a different model/processing run.

Why it matters for A: both cohorts start at the same temperature (15 °C) but the faulty records end hotter (28 vs 22 °C) and
warm up 3× faster across early blocks with the *same* number of frames. A block of N rest frames therefore spans more calendar
time in a faulty vehicle; any genuinely drifting cell accumulates more drift per block, so z of that cell is larger. "Signal
grows towards record end" is indistinguishable from "faulty records are sparser towards the end."

The prereg controls were C1 temp, C2 SOC, C3 n_valid, C4 rest fraction, C5 |I|. Two flagged; the adjusted logistic used only these
five. None of them captures sentinel presence, fragmentation, temperature *range/trajectory*, or SOC minimum. "A survives
adjustment" [file: results_G2.md §4; g2.json `adjusted.A` +0.30 (+0.04, +0.51)] is therefore adjustment for the wrong things.

### C2. The pre-registered primary does not survive stratification; the late "drift" signal is not drift
Primary = early A − B with bootstrap CI excluding 0 [file: g2.json +0.071 (+0.009, +0.136)]. DeLong agrees unstratified
(+0.071, +0.007 to +0.135, p = 0.030) [recomputed]. But:

| Analysis [recomputed] | early A | early B | early A−B | late A | late B | late A−B |
|---|---|---|---|---|---|---|
| unstratified (DeLong) | 0.591 | 0.521 | +0.071 p=.030 | 0.733 | 0.574 | +0.159 p=.0008 |
| within 2 °C temp strata (perm, 5000) | 0.587 p=.047 | 0.532 | +0.055 **p=.11** | 0.637 p=.036 | 0.474 | +0.163 p=.019 |
| within 2 °C temp × rest-frac tertile | 0.579 p=.077 | 0.540 | — | 0.645 p=.029 | 0.470 | — |
| within 3 °C temp × (early n_rest / late SOC-jump) tertile | 0.600 p=.028 | 0.528 | +0.073 **p=.067** | **0.595 p=.11** | **0.441** | +0.154 p=.021 |
| caliper matching (|ΔL_T| ≤ 2 °C, |ΔSOC-jumps| ≤ 10; 31 faulty, 1910 pairs) | 0.615 | 0.532 | — | 0.589 | 0.448 | — |
| same-processing-path subset (17 sentinel-bearing faulty vs 335 normals) | 0.587 (0.44–0.74) | 0.524 | — | 0.612 (0.49–0.73) | 0.458 | — |

Note what keeps "A − B" alive in the late window: **B drops below 0.5 inside strata** (0.44–0.47). "A beats B" late is
one-third "B is anti-predictive once cohort is controlled", which nobody pre-registered as the claim.

Block-order permutation control [recomputed: `*_perm_*` columns; block order shuffled with a per-vehicle seed before the OLS slope]:
late A_perm = **0.706** (0.63–0.78) vs late A = 0.733; early A_perm = 0.545 vs early A = 0.591. An explicit "robust z of
between-block std per cell, max over cells" (A_var) gives late 0.726, and Spearman(A, A_var) = 0.53–0.64 within both cohorts.
Max |z| gives late 0.759; max z (the cell drifting *up*) gives 0.615. So the late per-cell signal is "one cell is erratic
between blocks", not "one cell drifts down against its siblings". Under the temperature × SOC-jump stratification A_var collapses
to 0.517 (p = 0.45) and late A to 0.595 (p = 0.11). Within faulty vehicles, late A is much higher in the 41 sentinel-free
records than in the 17 sentinel-bearing ones (MWU p = 0.010); for early A there is no such split (p = 0.81).

Adjusted logistic with season/gap covariates (E_T, L_T, T_max, SOC-jumps, SOC-min, early n_rest; 600 bootstraps) [recomputed:
`adjust2.out`]: early A +0.28 (−0.08, +0.59); late A +0.23 (+0.01, +0.90); late A_perm +0.47 (+0.12, +0.95). The surviving
late coefficient is carried by the non-drift component. (Including `has_sent` quasi-separates the model, as 335/335 vs 17/58, so it
was excluded; the 17-vs-335 subset analysis is the honest version: early A +0.12 (−0.96, +0.37), late A +0.07 (−1.59, +0.37).)

### C3. The write-up's headline overstates the pre-registered outcome
- The pre-registered decision was *one* test (early A − B). AUC_A = 0.59 fails the 0.70 "SUPPORTED" bar, the result is
  flagged "cohort-distinguishable" by the prereg's own rule, and the late window was explicitly "report-only". Yet the dossier's
  summary table [file: RESEARCH_DOSSIER.md line 363] reads "**Per-cell > min/max**: AUC 0.59 vs 0.52 early, 0.73 vs 0.57 late …
  survives adjustment", and results_G2.md's bottom line is "per-cell sees something min/max doesn't, before failure".
  "Before failure" is ASSUMED (no dates); "survives adjustment" is true only for the five pre-registered covariates.
- The dossier dataset table [file: RESEARCH_DOSSIER.md line 66] says Beihang provides "per-cell V and T snapshots". It does not:
  the 110 z columns are a continuous model-derived quantity (range −24919…0.10, median 0, 4.8 M distinct values in one vehicle)
  [recomputed: `inspect_layout.py`], not temperatures. Only one pack temperature exists (integer °C, q[0]).

---

## MAJOR

### M1. Fragility of the early A − B edge to reasonable definition changes (post-hoc sensitivity, not a new primary)
[recomputed: `analyse_rescan.out`, "SENSITIVITY VARIANTS"; DeLong CI on A − B]

| Variant (early window) | A | B | A − B (95 % CI) | p |
|---|---|---|---|---|
| pre-registered (10 blocks, rest < 1 A, median, OLS) | 0.591 | 0.521 | +0.071 (+0.007, +0.135) | .030 |
| 5 blocks | 0.590 | 0.497 | +0.092 (+0.024, +0.161) | .009 |
| 20 blocks | 0.589 | 0.514 | +0.075 (+0.014, +0.137) | .016 |
| rest < 0.5 A | 0.608 | 0.509 | +0.099 (+0.031, +0.167) | .004 |
| rest < 3 A | 0.577 | 0.516 | +0.061 (−0.012, +0.133) | .099 |
| rest < 10 A | 0.534 | 0.474 | +0.060 (−0.013, +0.134) | .107 |
| all frames (no rest filter) | 0.513 | 0.484 | +0.029 (−0.041, +0.100) | .42 |
| Theil–Sen slope instead of OLS | 0.598 | 0.521 | +0.077 (+0.000, +0.154) | .049 |
| **block mean instead of block median** | 0.583 | **0.590** | **−0.007** (−0.085, +0.071) | .86 |
| block order shuffled (drift destroyed) | 0.545 | 0.523 | +0.022 (−0.068, +0.112) | .63 |
| first 1500 rest frames (fixed count) | 0.539 | 0.426 | — | — |
| first 25 % of record | 0.551 | 0.419 | — | — |
| rest frames restricted to SOC 0.35–0.90 | 0.594 | 0.549 | +0.044 (−0.027, +0.116) | .23 |

The edge survives block count and Theil–Sen, dies with mean aggregation, with looser rest thresholds, with a fixed-count or
shorter early window, and with mid-SOC restriction. Half of the "robustness" space kills it. A pre-registered test whose p-value
sits at 0.03 and flips sign under median→mean is not a resolvable edge.

Late window: survives most variants (A 0.64–0.77, A − B +0.08 to +0.20), *including* block permutation (+0.168) — which is the
problem, not reassurance (see C2).

### M2. Faulty vehicles have more early rest frames; A's precision scales with that
early n_rest AUC 0.622 (faulty 3590 vs normal 2882) [recomputed; also [file] features.csv `E_n_rest`]. Each block median is
estimated from ~25 % more frames and spans more calendar time (C1), both of which inflate z for any real or spurious outlier
cell. The fixed-count window (first 1500 rest frames) brings early A to 0.539 (0.456–0.621).

### M3. The late-window gain is not a record-end artefact in the narrow sense, but the "signal grows toward failure" story is not supported
Final 10 % alone: A 0.538, B 0.462; final 5 %: A 0.521. Quarters Q1→Q4: A 0.551, 0.609, 0.588, 0.700; late window excluding
the last 10 %: 0.689 [recomputed]. So the last rows do not carry fault-mode behaviour; the late gain comes from the longer
window (more blocks of more fragmented, hotter data). Meanwhile the up-drift control rises monotonically Q1→Q4 (0.52, 0.56,
0.63, 0.58; last-10 % window 0.67) — the direction-agnostic "erratic cell" reading fits better than directional drift.

### M4. Statistics
- CI method: the repo uses 2000 stratified vehicle bootstraps, percentile. DeLong gives essentially identical CIs
  (early A 0.509–0.674 vs bootstrap 0.511–0.671; early A − B +0.007/+0.135 vs +0.009/+0.136) [recomputed]. No issue there.
- Multiplicity: one pre-registered test. But the write-up reports and interprets ≥ 12 AUCs (A, B, A−B × early/late; A_lvl,
  B_lvl, B_spr; 5 controls; concordance; DTI ranks) and headlines the one that is largest (late A). With 2 windows × 2 features
  the family-wise bar for the "A − B" claim is already ~0.025; the early primary at p = 0.030 does not clear it, and the late
  p = 0.0008 is the one that fails stratification.
- Deviation 1 (decision-table gap) is handled honestly in results_G2.md and g2.json (`verdict` string); the first run's
  mislabelling is disclosed. But the correct prereg-faithful reading of "AUC_A < 0.70" is **not SUPPORTED**; the gap row the
  authors added ("exists, weak; per-cell resolvably better") is a post-hoc category and should be labelled as such in the dossier,
  not folded into "Per-cell > min/max".
- The adjusted logistic uses `C=1e6` (unpenalised) with 58 events and 6 parameters: acceptable, but percentile bootstrap CIs of
  logistic coefficients with quasi-separating covariates are unstable (I hit this with `has_sent`). Stratified permutation or
  matching is the better tool here and gives a different answer (C2).

### M5. The "concordance" argument is weaker than presented
"In only 28 % of faulty vehicles is the A-flagged cell the modal-min cell; the A cell sits at the minimum in 2.5 % of rest
frames" [file: results_G2.md §1]. Among *normal* vehicles the same numbers are 0 % modal-min (median) and 0.1 % min-fraction
[file: features.csv `E_A_cell_is_modal_min`, `E_A_cell_minfrac` medians by label; recomputed AUC 0.53 / 0.56]. So A points
away from the min cell in both cohorts; this is a property of the feature, not evidence that per-cell data sees a hidden
drifting cell in faulty packs specifically.

---

## MINOR

- m1. **Mileage sanity (prereg §5.5) is vacuous for QAS**: vin_1 column 2 is constant zero in all 393 QAS vehicles
  [recomputed: `v1c2_const` = 1.0 for both labels]; the 83 % figure in g2.json comes entirely from DTI. results_G2.md presents it as
  support for row order. Row order is nevertheless plausible from SOC continuity (median |ΔSOC| = 0 between rows, 99th pct 0.01;
  the 1-mV voltage grid and −0.63 median corr(ΔV_pack, I) are also consistent with discharge-positive current) [recomputed].
- m2. **Layout check passes**: y = 110 cell voltages, 1 mV resolution, 2.77–3.65 V with per-frame spread 6–14 mV (LFP range —
  worth stating: this is an LFP fleet, which matters for how flat OCV is and how small rest deviations are); q = [integer temp,
  SOC 0–1, current with noisy ≈ −1000 sentinel]. The code's |I| < 900 sentinel rule is right (sentinel values spread −995…−1005).
  z is not temperature (see C3). vin_3 is a 226-column variant whose q has 4 columns; q[3] is the current.
- m3. Sentinel noise: the sentinel is −1000 ± ~1.3 A, i.e. the authors added noise or interpolated across invalid rows. The
  normals' valid current may therefore also be lightly processed. Not material to A, but it is another sign the release is
  "processed", not raw, and that processing differed by cohort.
- m4. No cross-vehicle duplicates found (0 vehicles share n_rows, V/T/SOC unique-value counts) [recomputed].
- m5. No single cell index dominates the A flag in either cohort (top cell in faulty: 4/58; in normals: 14/335) [recomputed];
  "always-odd index" style trivialities are absent.
- m6. Normals are homogeneous along the ID axis (median E_A, L_A, L_T, SOC-jumps, sentinel fraction flat in every 50-ID window;
  Spearman of A vs ID among normals r = 0.09 / −0.005); the faulty block differs sharply on every one of those [recomputed]. This is
  a textbook batch, not a gradient — "restrict to IDs near the boundary" cannot deconfound it (AUCs for normals 280–334 are the
  same as for 0–100).
- m7. `G2_plots.py` ROC code is fine; the AUC figure's control band is the prereg one.
- m8. The repo dossier line 66 "per-cell V and T snapshots" should read "per-cell V; one pack temperature".

---

## MISSED OPPORTUNITIES (ranked)

1. **Fault-type labels exist in the authors' database but not in the release.** The paper reports a 4-digit fault code
   (TR/EL/ISC/EA) and says ISC is the most common, EL the rarest, some vehicles with 3 faults. A one-line request to the authors
   for the per-vehicle code (and, critically, the **date range of each record and the failure date**) would convert G.2 from
   "unknown lead time, unknown fault" into a real early-warning test. It would also allow the ISC-only subset, where a monotone
   per-cell self-discharge drift is the physically expected signature.
2. **Characterise the batch before testing.** The sentinel-presence, fragmentation and temperature-trajectory fingerprints took
   one pass over the data to compute and would have been obvious pre-registration covariates. Any follow-up should pre-register a
   "cohort indistinguishability" gate: if trivially computable non-fault fingerprints reach AUC > 0.8, the per-cell test is
   downgraded to exploratory *before* looking at A.
3. **Use the authors' released code as a comparator**, not just a layout reference. Their MC-AE residual features per cell
   (`DiagnosisFeature`) are the published per-cell detector; running their pipeline and a min/max-only version of it on the same
   frames is the direct answer to "does per-cell beat min/max" on this data. Their own models/ paths are not in the release, but the
   training script is per-vehicle and self-contained.
4. **DTI as a processing-path control.** DTI (80 vehicles, 3 faulty, mV units, short records) was only ranked. Checking whether
   DTI's faulty records share the sentinel-free / fragmented signature would tell whether the processing-path difference is a
   Beihang-wide artefact of how faulty samples were curated.
5. **SOC-dependence of rest deviation** (LFP). The deviation of an SOC-offset cell is amplified at SOC extremes. My
   `dsoc_absmax_z` (max robust z of per-cell deviation-vs-SOC slope) has late AUC 0.69 and correlates with A (r = 0.3–0.4) —
   a cleaner, physically interpretable per-cell feature than block-slope z, and one whose cohort sensitivity can be modelled.
6. **GIS (41 vehicles, unlabelled)** could serve as a second "normal" population to test whether the normal-QAS A distribution is
   typical or whether the faulty cohort merely came from a different fleet.
7. **BatICM / BATSS** (already in hand per `G_dataset_search_extended.md`) give cell-located ISC cases with timestamps: a tiny
   but date-bearing check of whether the per-cell block-variability feature precedes a known event.

### What a proper follow-up pre-registration should contain
- Obtain or reconstruct record dates (ask authors; or, failing that, use the temperature trajectory as a season proxy and
  **match** faulty to normal vehicles on it before any feature is computed).
- Gate: cohort-fingerprint AUC (sentinel presence, run count, T_max, T trajectory, SOC min, n_rest) must lie in [0.35, 0.65]
  after matching; otherwise the experiment is exploratory.
- Primary: stratified (matched-set) AUC difference A − B with a within-stratum permutation p-value; strata fixed in advance.
- Pre-register the **block-permutation control** and the **direction-agnostic control** (max |z|): a drift claim requires
  A ≫ A_perm; otherwise the claim must be re-worded as "erratic cell".
- Fix aggregation (median vs mean) and rest threshold *and* state that sign-flips across these are disqualifying.
- Use fixed rest-frame counts per window, not a fraction of a record of unknown calendar span.
- Fault-type-specific secondary (ISC subset) if codes are obtained.

---

## SOLID (credit where due)
- Pre-registration before code; label counts and ID contiguity disclosed up front; the cohort confound was anticipated and
  a flag rule existed and fired. The decision-table gap was disclosed as a deviation rather than silently re-labelled.
- Restricted unpickler with map_location=cpu for CUDA pickles; correct sentinel handling; correct layout for y and q
  [recomputed]; the feature code reproduces exactly from an independent implementation.
- Bootstrap CIs agree with DeLong to the third decimal; the stratified bootstrap and seed are stated.
- The post-hoc temperature-stratified AUCs reported in results_G2.md (A 0.59 early / 0.66 late) are correct and already hinted
  at the late-window shrinkage [recomputed: 2 °C strata A 0.587 / 0.637].
- Licence and provenance tracking (CC BY 4.0, md5) is clean.

---

## Verdict wording I would accept
"On Beihang QAS the pre-registered early-window test is **NOT SUPPORTED** at the 0.70 bar. A small early per-cell signal
(AUC ≈ 0.59–0.61) persists after stratification and matching on the measurable cohort differences, but the pre-registered
A − B difference does not (stratified p ≈ 0.07–0.11), and the late-window 0.73 is largely non-drift block-to-block variability
that disappears under cohort stratification. The faulty and normal cohorts were processed differently (sentinel removal,
fragmentation, season), so no claim about lead time or about per-cell superiority can be made from this release without
record dates and matched cohorts."
