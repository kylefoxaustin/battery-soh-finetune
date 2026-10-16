# Adversarial review — Experiments E and F (Changan 300-EV per-cell work)

Reviewer lens: battery diagnostics + statistics. Repo at `<repo>`, commit `731c2b7`.
Nothing in the repo was modified. Recomputations were run on CPU from `data/changan/cells/vinN.npz`,
`data/changan/labels_full`, the frozen fold models (`runs/chf_*`) and the committed JSON outputs; scripts and raw
outputs are in `scratchpad/review/ef/` (`fleet_scan.py/.json`, `label_noise.py/.out`, `resid_autocorr.py/.out`,
`module_structure.py/.out`, `selfdischarge.py/.out`).

Every number below is tagged **[file]** (read from a committed file) or **[recomputed: how]**.

---

## Critical

### C1. F's headline "min/max sees 98 % of per-cell anomaly-days" is a mathematical identity, not a finding

The per-cell detector flags day *d* if `min_k mean_{frames in d} dv_k < −60 mV`; the min-only detector flags day *d*
if `mean_{frames in d} (vmin − V/96) < −60 mV`, and `vmin − V/96` is (up to the 0.1 V truncation of V) the
per-frame `min_k dv_k`. For any fixed cell *k*, `min_k dv_k ≤ dv_k` on every frame, so
`mean_d(min_k dv_k) ≤ min_k mean_d(dv_k)`. Whenever per-cell flags, min-only must flag. The direction of the
reported 97.9 % is guaranteed to be 100 % on identical frames; the 2.1 % shortfall is purely a frame-set
difference (slim files keep malformed/desynced frames and every 10 s frame; the cells file keeps synced frames,
every 6th).

- **[recomputed: `fleet_scan.py` (a), all 300 vehicles, same rest synced full-vector frames for both detectors]**
  per-cell event-days 730, caught by min-only 730/730 = **100.0 %**, inequality violations 0.
- **[file `results/F/agreement.json`]** 715/730 = 97.9 %.

The write-up (`results_F.md` §3, dossier §4 and §9 "Detecting anomalies (F): Min/max sees 98 % — Strong") presents
this as empirical evidence that min/max suffices for detection. It is a consequence of defining the anomaly as an
absolute threshold on the pack-mean deviation: any cell 60 mV below the mean *is* the minimum cell (fleet median
cross-cell SD is 3.7 mV, **[recomputed: fleet_scan (c)]**). The detection question that per-cell data could
actually answer — a cell moving relative to **its own history** while another cell is the minimum — was never
tested at the detection level (only indirectly via forecast feature A, which was underpowered). When I ran that
test, per-cell-only detections exist (see M1). **Required change:** reword §3 / dossier row as "by construction, an
absolute −60 mV deviation is always the minimum cell; detection parity is definitional", and downgrade the
"Strong" strength tag.

### C2. E's pre-check was unpassable by construction; the verdict wording should say so

The pre-check (`E_power_analysis.md` §5) demanded out-of-fold R² ≥ 0.26 (primary) / 0.39 (strict) of the
**within-unit fleet residual** from features computed over the **5 k km before** each label's charge session. That
target is essentially white noise from label to label:

- **[recomputed: `resid_autocorr.py`, same `E_power.residuals` on `runs/chf_{ls}_k{0..3}`]** median lag-1
  autocorrelation of the within-unit residual **+0.056** (primary, 94 units) / **+0.090** (strict). Excess
  variance of a 5-label running mean over the white-noise expectation: +0.20 Ah² of 16.6 Ah² (≈ 1 %) primary,
  +0.09 of 10.1 strict.
- Consecutive labels ≤ 300 km apart (true capacity cannot have changed): SD(diff)/√2 = 3.41 Ah vs within-unit SD
  4.08 Ah → at most ~30 % of within-unit variance is anything but session-to-session scatter, and the
  autocorrelation says the slowly varying part is closer to 5–10 %.
- **[recomputed: `label_noise.py`, labels_full, primary band]** raw labels: close-pair noise 3.9 Ah (robust 2.9)
  vs 4.67 Ah SD about a linear fit. Session covariates excluded by the pre-check design (vmax at charge end,
  log segment length, BMS SOC at end, start SOC, temperature) explain OOF R² = **0.18** of the within-unit label
  deviation; labels started below 15 % SOC are biased **+2.4 Ah** (OCV-table edge).

So a feature that varies on a 5 k km scale could not have explained 26 % of a target whose autocorrelated share is
≤ 10 %, however the per-cell state was summarised (dQ/dV, rest relaxation, cell IR, charge-end spread included).
The R² threshold was derived correctly from the MDE (see S1), but the **target** should have been checked for
autocorrelation before pre-registering a threshold on it — a one-line check with the residuals already in hand
(`E_power.py` computes them). The result is then not "per-cell data does not explain the label scatter" (results_E
§ Verdict item 3, "failed decisively") but "the label scatter is session noise that no pre-session feature can
explain; this fleet's labels cannot test E4". The dossier's "the per-cell route adds nothing measurable on this fleet"
(results_E, Honest verdict) over-reads a test that could not have passed. The INCONCLUSIVE verdict itself is right.

---

## Major

### M1. F missed the one detection class per-cell data owns: relative drift of a non-minimum cell

**[recomputed: `fleet_scan.py` (b), all 300 vehicles]** Detector: per cell, daily rest mean minus the median of
the cell's own first 60 valid days; flag runs ≥ 3 valid days below −30 mV.
- 23 vehicles / 76 cells / 1,542 flag-days. The flagged cell is the daily minimum on only **57 %** of flag-days;
  the min-only series (daily min, relative to its own baseline) moved by < −30 mV on only **39 %**.
- **40 cells in 5 vehicles are fully silent to min/max** (argmin on < 50 % of days and no min-only drift): vin272
  (a ≈ 30-cell block at −35…−48 mV around day −20…0 while other cells remain the minimum), **vin23 cells 28, 30,
  31** (−48 mV, day 720, not in F's catalogue), vin158 cell 89 (−183 mV, 3 days, not in the catalogue), two more.
  4 of the 5 vehicles are absent from F's 20-vehicle catalogue.

This is exactly G.2's later finding ("a cell drifting relative to its siblings while not being the weakest") and it
was available in F's data. F's own pre-registration (§6) lists "cells drifting while not the minimum" as something
per-cell adds "by construction" but never quantified it.

### M2. The post-hoc label-rise finding is confounded by label type and rests on 2–4 "before" labels

- `F_faults.py:184-186` and `F_diag.py:352` take **all** labels from `labels_full` (every charge current). The
  dossier's primary label set is fast-charge 48–51 A because slow-charge labels are biased: **[recomputed:
  `resid_autocorr.py`]** slow-charge (< 25 A) labels sit **+6.8 Ah** (IQR +5.0…+9.1, 137 units) above the same
  unit's fast-charge trend.
- **[recomputed: `label_noise.py` decomposition]** vin116 — the largest "rise" (+9.7 Ah) — switched from
  median 48 A charging before onset to **14.8 A** after. vin266's "before" labels were at 28.6 A. The "before"
  windows hold **2, 2, 13, 3, 4, 3** labels (vin19, 93, 116, 120, 169, 266) against a per-label noise of ~4 Ah.
- **[recomputed: D3 re-run with 48–51 A, 95–145 Ah labels]** vin116 drops out (no fast labels after onset);
  n = 5, median excess **+2.4 Ah**, Wilcoxon **p = 0.062**, i.e. not resolvable even at the minimum attainable p.
- In 5 of 6 vehicles the median start SOC fell after onset (49→44, 34→19, 41→35, 48→32, 44→34 %), consistent
  with changed charging habits rather than a pack change.

The dossier §4 "Post-hoc surprise … +4.4 Ah … p = 0.031" should be withdrawn or restated as "not significant on the
primary label set; confounded by charge-current mix".

### M3. The "SOC-like" class is mostly a restatement of the threshold through an ASSUMED, non-physical OCV table

- **[file `data/changan/ocv_full.json`, recomputed slopes]** The table is max-cell voltage at wake vs **BMS
  SOC** (coulomb-counted, pinned at 100 % for 4185–4245 mV). Its implied slope is 2.5–3.3 mV/% at 24–46 % SOC and
  a uniform **10 mV/%** from 55 % to 99 % — the inverse of a thermodynamic NMC OCV (steep at low SOC, flat
  mid-range). It is a BMS-indexed curve, not an OCV.
- **[file events.json]** The 23 SOC-like events have fitted δ = 6.5–12.8 %, i.e. δ ≈ depth / 10 mV/%; depth is
  itself selected to be below −60 mV. "Offsets of δ ≈ 6–12 % SOC … consistent with a real cell at lower SOC"
  (results_F §2) is the threshold divided by the table slope, not independent evidence.
- The classifier has no model for the other cell-physics alternative (a lower-capacity cell balanced at top, whose
  deviation grows toward low SOC) or for a sensor gain error. With one-parameter M_off vs one-parameter M_soc the
  comparison is fair, but "SOC-like ⇒ real cell at lower SOC" is over-interpreted. The admitted selection bias
  toward SOC-like is not fatal — a constant sensor offset still cannot win M_soc — but the class label should be
  "co-varies with pack SOC per the table", with no δ quoted as physical.

### M4. 22 of the 41 "qualifying events" are chronic cells crossing a fixed threshold, not onsets

**[recomputed from events.json `shift`]** Own-cell shift vs its baseline: ≤ −30 mV in **19** events; −30…−15 mV
in 9; > −15 mV in **13** (vin169/89 is +2.8 mV, i.e. the cell was *higher* during its "event" than in its baseline,
because the baseline is contaminated by the previous run). vin272 contributes 7 of the 13. The catalogue counts
("41 events", "vin272 accounts for 12") therefore mix two populations; a relative-to-own-baseline criterion (M1)
would have given a cleaner count. The write-up notes vin272 "looks module-wide" but still reports 41.

### M5. Cell 31 recurrence is under-tested and is nominally significant when tested properly

- `F_diag.py:336-345` counts only the **deepest** event per vehicle (cell 31 in 3 of 20, p = 0.10). Counting any
  qualifying event: cell 31 appears in **4 of 20** vehicles (vin19, 50, 272, 277) and cells 30–31 in 5 (adding
  vin283). **[recomputed: 20,000 draws of each vehicle's observed number of distinct event cells, uniform over 96]**
  P(any cell reaches multiplicity ≥ 4) = **0.021**; for cell 31 named in advance, 5×10⁻⁵.
- Cell 31 is **not** a generally weak position: it is the modal rest-minimum cell in only 2 of 300 vehicles and the
  weakest mean-rest cell in 2 (uniform expectation 3.1) **[recomputed: fleet_scan (c)]**. The weakest cells cluster
  at indices 82–89 and 18 (cell 84 weakest in 10 vehicles, 88 in 9, 82 in 8).
- Cell 31's deep events are offset-like (constant mV, no SOC dependence, no neighbour movement, two onsets near day
  356–362) — the profile of a sense-channel/connector fault, not a cell. vin23 (M1) also drifts on cells 28/30/31.
- Module geometry **[recomputed: `module_structure.py`, day-to-day rest-deviation correlation]**: best block fit is
  12 cells, offset 0 (vin100: within−between 0.35; vin200: 0.43; vin200's adjacency dips at links 11→12, 23→24,
  35→36, 59→60, 83→84). Relative-resistance hotspots **[fleet_scan (d)]** sit at indices 4, 8, 28, 40, 56, 84, 88,
  92 (cell 88 in 31 vehicles) — every 4th position, i.e. inter-group busbars inside the 12-cell modules. Cell 31 is
  the last cell before the 32 boundary of such a 4-group. This is worth a follow-up because it is a **platform**
  (harness/connector position) hypothesis that min/max can never raise.

### M6. Pre-check regression design penalises per-cell features for between-unit variance

`E_precheck.py:132-144`: the target is centred per unit (first 10 labels) but the features are not. Features that
are nearly unit-constant (weak_dev, cross_sd, probe_spread) let the pooled OLS learn between-unit relations
(diag: between-unit in-sample R² 0.08 / 0.22) and project them onto a target with no between-unit variance,
producing OOF R² of −0.02 / **−0.18**. A within-unit (fixed-effects) regression was the fair test. Given in-sample
R² of 0.011 it would not have changed the decision, but the negative R² is a design artefact, not evidence.

### M7. Timing of F's "pre-registration before code"

**[git log]** `2b9e629` (pre-registration) 17:32:04; `F_faults.py` mtime 17:33; results `7e1f052` 17:49 — a
304-line analysis written, run on 71 GB across 300 vehicles, diagnosed (`F_diag.py` 17:47) and written up in 17
minutes. Thresholds were plausibly fixed before results (events.json 17:45), which is what matters, but the claim
"committed before analysis/F_faults.py exists" is not credible on the timestamps; say "before any output existed".

---

## Minor

- **E oracle sign:** shift-oracle median recovery at α = 0.05 is **−0.08 %** (primary) although Gaussian theory
  predicts centring tightens the 5 % quantile by ≈ 0.89 Ah (**[recomputed]**). The centred pooled quantile is
  *more* negative than the uncentred one (6.50 vs 6.14 Ah, [file power_changan.json]) because the lower tail is
  within-unit and heavy. Not a bug, but the write-up should say the oracle numbers are tail-driven, not
  variance-driven.
- `power_changan.json` `frac_within_that_is_label_noise = 1.0` is a clipped value; the raw ratio is 1.34
  (primary) / 1.43 (strict) — the "noise floor" exceeds the residual variance because the fleet model already
  removes ~25 % of the within-unit scatter via session inputs. The text "no larger than the noise estimate" hides
  that the noise estimate is not pure measurement noise.
- F tap test: `comp = max(neighbour shift)/−drop` has no sum-preservation term. vin272 cell 49 ({+22, −47, +21},
  sum −4 mV, ratio of neighbour sum to drop 0.91) is a second clean sum-preserving case missed at comp = 0.474;
  the 3 artefact flags were correctly called out. Also the OCV table uses `vmax` while 2b feeds `vmean` into it
  (~15–20 mV bias → a few % SOC), immaterial for classification.
- F "valid day" = 20 full vectors ≈ 20 min of rest; "rest" includes frames right after key-off, so relaxation of
  high-IR cells enters the daily mean. Fine for anomaly flagging, confounds 2b toward "more negative at low SOC".
- Dossier §3 "MDE about 0.8–0.9 %": recomputed 0.757 / 0.942 %; "0.8–0.9" rounds both toward each other.
- Dossier §9 strength tag for F detection ("Strong") contradicts C1; F early warning "—" is fine.
- Pre-check imputation (training-fold median) and `label_times` float32 equality matching: both work (0 unmatched),
  disclosed.
- `F_faults.py:149` "abrupt" requires the first valid day after the end to be > −30 mV **and** ≤ 3 days later:
  a vehicle that is simply not driven for 4 days after a repair is scored "not abrupt". Minor sensitivity.

---

## Missed opportunities (ranked by expected value)

1. **Relative-drift / sibling-referenced anomaly detector on Changan (M1).** Already prototyped: 23 vehicles,
   40 silent cells in 5 vehicles. Expected payoff: the only Changan result that can show per-cell > min/max for
   detection, and it links F directly to G.2's A-feature. Cost: hours.
2. **Per-cell relative resistance map (dv_k vs I over driving frames)** **[recomputed: fleet_scan (d)]**: 139/300
   vehicles have a cell with |z| > 6; hotspots at every 4th index → structural (busbar) signature, plus genuine
   outliers (vin155 cell 4, z = 29; vin277 cell 40, −0.37 mΩ). Trend of a cell's ΔR over odometer is a per-cell
   ageing signal min/max cannot provide. Cost: a day; the extraction already exists.
3. **Cell-31 / platform-position investigation (M5)**: tabulate event cells against the inferred 12-cell / 4-cell
   geometry and the probe map; test whether offset-like events (constant mV, no neighbour, abrupt) concentrate at
   group-boundary channels. Payoff: a harness-level diagnosis claim that is testable without ground truth.
4. **Self-discharge across parking gaps (ISC signature)** — see the prototype result below. Payoff if positive:
   the canonical per-cell-only fault signal (BATSS cells show 0.8–1.1 mV/h).
5. **Label de-noising instead of residual-explaining (E):** start-SOC bias (+2.4 Ah below 15 %), slow-charge bias
   (+6.8 Ah), segment-length and vmax-at-end effects explain 18 % of within-unit label scatter; a corrected label
   would cut the noise floor and raise the attainable R² of any later per-cell test.
6. **Module inference from correlation (prototyped)**: 12-cell blocks, hottest probes 3/0/16 carry 74 % of
   hottest-probe frames, weakest cells cluster at 82–89. A thermal-gradient vs weakest-cell analysis is cheap.
7. **Onset vs season/odometer** is impossible with per-vehicle re-based clocks; state this as a dataset limit
   rather than attempting D1.
8. **Case–control forecast design** (features in a window L before each of the 20 onsets vs matched pseudo-onsets)
   would have used ~15 positives instead of 3; it could be pre-registered as F.2.

### Self-discharge prototype (`selfdischarge.py`)
Method: for every telemetry gap ≥ 6 h with rest frames on both sides, Δdv_k = (first rest full vector after wake)
− (last before the gap); per cell, OLS of Δdv_k on gap hours → slope = relative self-discharge (mV/h), relaxation
goes to the intercept; flag z < −3 against the pack's 96 slopes. 9 vehicles had ≥ 30 usable gaps
**[recomputed: `selfdischarge.out`]**:

| vin | gaps (p50 h) | flagged cells | worst slope |
|---|---|---|---|
| 272 (F: 12 events, cells 31–51) | 71 (8.5) | **31, 32, 34, 37–42, 49, 51, 55, 88** | cell 49: **−0.81 mV/h**, z = −20 |
| 200 (no F event) | 54 (11.7) | 29, 82 | cell 82: −0.13 mV/h, z = −6.4 |
| 19 (F: cell 31 offset-like) | 92 (9.2) | 31 | −0.009 mV/h, z = −4.0 (at resolution; weak) |
| 93 | 235 (12.8) | 64 | −0.007 mV/h, z = −3.2 (weak) |
| 3 | 38 | 34, 85, 91, 93 | −0.0009 mV/h (noise) |
| 120 (F: −774 mV abrupt) | 234 (11.3) | none | z = −2.5 |
| 139, 23, 100 | 97 / 212 / 73 | none | — |

vin272's block loses charge relative to its siblings at up to 0.8 mV/h during parking — the same magnitude as the
BATSS internal-short cells (0.8–1.1 mV/h, dossier §1). On a *contiguous block* this points at a slave-board /
balancing-circuit drain rather than 13 simultaneous internal shorts — a diagnosis only per-cell rest data can make,
and a far stronger "module-wide" statement than F's. vin200 cell 82 is a candidate single-cell drain in a vehicle F
never flagged. Caveats: 10 h median gaps, 1 mV resolution, relaxation only partly removed; needs a fleet-wide run
with a longer-gap subset before any claim.

---

## Solid

- **S1. E arithmetic checks out [recomputed].** MDE = (z_{1−0.00104/2} + z_0.8)·σ_b/√n = 0.928 Ah = 0.757 %
  (primary), 1.150 Ah = 0.942 % (strict); R² thresholds 0.256 / 0.185 (primary α = 0.05 / 0.01), 0.387 / 0.284
  (strict). Variance decomposition, sampling SEs and realised-α bootstrap CIs match `power_changan.json`.
  α = 0.001 unverifiability (5.6 expected violations in 3 units) is correctly argued.
- Stop rule honoured: no estimator/E6 built after NO-GO; pre-check thresholds not moved; deviations numbered.
- E's corrections to the brief (Yuasa Q are model estimates; 31 % is a different metric; per-cell columns dropped
  by choice; 5.6 % malformed, 1.2 % desynced) are accurate and important; the extractor's `sync` flag is the right
  response.
- F pre-registration is specific, states the prior (AUC_A ≈ AUC_B), the power floor (8 positives) and
  "no fault-rate claim"; the UNDERPOWERED call is correct and honestly reported.
- F's tap-signature case vin116 cell 21 (+116 / −195 / +57) is real and well described; vin120 cell 47
  (−774 mV, neighbours flat, abrupt recovery) is correctly left unresolved. **[recomputed]** vin120 shows no
  anomalous self-discharge (worst z −2.5), consistent with a sensor/intervention reading.
- Code quality: `F_faults.py` implements the pre-registration faithfully (runs, baselines, split, A/B features,
  bootstrap); OPEN-1..4 are disclosed; label time base matches the cell time base (both per-vehicle seconds).
- Licence and no-economic-claim discipline is consistent throughout.
