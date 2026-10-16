# Numeric audit — batt_finetune write-ups vs. JSON/npz/log sources

Audited 2026-10-15 against local `master` (731c2b7). Read-only; no repo files modified. Recomputations ran on CPU
(`nice -n 10`, numpy only) from `results/**` outputs and `runs/changan_cells.log` — never from raw datasets.

**Documents audited:** `results/RESEARCH_DOSSIER.md`, `README.md`, `results/results.md`, `results/results_large.md`,
`results/dataset_profile.md`, `results/E/*.md`, `results/F/*.md`, `results/G/*.md`, `results/G2/*.md`, `results/H/*.md`,
`results/H2/*.md`.

**Sources used:** `results/summary.json`, `results/raw/{e4,e4_ft10}.json`, `results/raw/probe/*.json`,
`results/large/summary_large.json`, `results/large/rolling_evb_ds1.json`, `results/large/e4_{primary,strict}_k*.json`,
`results/large/expD/e{2,3}/*.json` + census, `runs/chf_*_k*.train.log`, `runs/changan_cells.log`,
`results/E/{power_changan,power_yuasa,precheck,precheck_diag}.json`, `results/F/{events,forecast,agreement,consequence,diag}.json`,
`results/G2/{g2.json,features.csv}`, `results/H/{replay.json,footprint.json,replay_sessions.npz,board/*}`,
`results/H2/{replay.json,footprint.json,replay_sessions.npz,board/*}`, `git log`.

## 0. Bottom line

- **Critical: 0.** No verdict or headline in any document is contradicted by its sources. All pre-registered
  decision rules (E, F, G.2, H, H2, Study 2 Bonferroni) are applied as written and the stated verdicts follow.
- **Major: 3.** One transcribed count is wrong in two documents (F event count for vin272: 12 → 11); one dossier
  dataset claim (BATSS inspection result) is supported by no write-up or committed output; one dossier ratio
  (fade/noise 1.6–2.3×) does not follow from the numbers the dossier itself shows.
- **Minor: 17.** Rounding, unit-basis (KB vs KiB), tag-definition drift, attribution of a margin figure, and
  small repeatability-spread overstatements.
- Board numbers (Study 1 E1–E4, Study 2 §D, H-b, H2-b) all trace to board JSON with census files and passing
  gates (`results/raw/census_*.json`, `results/large/expD/census_*.json`, `results/H/board/`, `results/H2/board/`).

## 1. Discrepancy table

Severity: **Critical** = verdict/headline wrong · **Major** = quoted number wrong or unsupported · **Minor** =
rounding / wording / tag / unit basis.

| # | Document:line | Stated | Value in source (file → key) | Severity |
|---|---|---|---|---|
| 1 | `results/F/results_F.md:42` | "**vin272 accounts for 12** of them, on cells 31–51 — one contiguous block" | `results/F/events.json → events[]`: **11** events with `car == 272` (cells 31, 32, 34, 37, 39, 40, 40, 41, 42, 49, 51). Per-car counts: 272:11, 93:6, 26:3, 169:3, 266:3, +15 singletons = 41. | **Major** |
| 2 | `results/RESEARCH_DOSSIER.md:199` | "vin272 alone accounts for 12, on contiguous cells" | same as #1 → **11**; and the cells are not contiguous (gaps at 33, 35–36, 38, 43–48, 50) | **Major** (count), Minor (wording) |
| 3 | `results/RESEARCH_DOSSIER.md:68`, `:236`, `:383` | BATSS "**Downloaded, inspected** … cells 2 and 8 both self-discharge 0.8–1.1 mV/h"; §10.6 "downloaded and inspected but not used" | No write-up supports this. `results/G/G_dataset_search_extended.md:42` tags BATSS **READ (metadata)** and `:15` says "no large downloads". Files exist in `data/raw/batss/` (fetched 2026-10-14 23:xx) and a `batss_rest.py` exists only in another session's uncommitted scratchpad. The 0.8–1.1 mV/h figure appears nowhere in the repo. | **Major** (unsupported claim) |
| 4 | `results/RESEARCH_DOSSIER.md:127` | "So fade is only **~1.6–2.3×** the label noise" directly under a table giving noise **SD 4.76 / 3.84 Ah** and fade 6.5 / 6.3 Ah | From the dossier's own table: 6.5/4.76 = **1.37×**, 6.3/3.84 = **1.64×**. The 1.6–2.3× figure is the MAD-based ratio (6.5/3.91 = 1.66, 6.3/2.76 = 2.28; `dataset_profile.md:82–84`), but the dossier omits the MAD column. | **Major** (ratio does not follow from shown numbers; fix by adding MAD or restating as 1.4–1.6× on SD) |
| 5 | `results/H/results_H.md:135` | "p99 varies by **≤ 1.5 %**" across repeats | `results/H/footprint.json → per_N.324.lat_ns_p99_range` = [10,459, 10,667] → **2.0 %** (others 0–1.3 %) | Minor |
| 6 | `results/H2/results_H2.md:103` | "p99 varies **≤ 0.2 %**" | `results/H2/footprint.json → per_N.396.p99_range` = [11,834, 11,875] → **0.35 %**; N=3564 is 0.16 % | Minor |
| 7 | `results/H2/results_H2.md:106`; `RESEARCH_DOSSIER.md:342` | "Scaling is about **14.7 ns per cell**" | (52,126 − 5,834)/(3,564 − 396) = **14.6 ns/cell** (`footprint.json`). H's own 14.66 does round to 14.7; H2's does not. | Minor |
| 8 | `results/H/results_H.md:21,126–129` vs `results/results.md:12` | "13.6 KB … 14.6 KB … 23.6 KB" (decimal: 13,608 B, 14,576 B, 23,616 B) | `results.md:12` declares "MB/KB = MiB/KiB (1024-based)" for the repo. In KiB these are 13.3 / 14.2 / 23.1. | Minor (unit basis) |
| 9 | `results/H2/results_H2.md:100–101` | "State + LUTs **17.2 KB** / **48.1 KB**" while the same section says "13.6 KB of tables" | 3,968 + 13,608 = 17,576 B = 17.6 KB (decimal) or **17.2 KiB**; 35,648 + 13,608 = 49,256 B = 49.3 KB or **48.1 KiB**. H2 uses KiB for totals but decimal for the LUT — inconsistent within one table and with H (#8). | Minor |
| 10 | `results/RESEARCH_DOSSIER.md:302–303` | "pack-mean needs **30 mV / 10 °C** margins … At those margins, limiting from the extremes charges a median **26–34 %** faster" | `results/H/replay.json → margin_sweep`: 30_10 → 33.9 % (unsafe 0.033 %); **26 % belongs to 50_5** (26.1 %, unsafe 0.036 %). `results_H.md:90–91` states this correctly. | Minor (attribution) |
| 11 | `results/G2/results_G2.md:53–55` | "Two negative controls fall **outside the [0.35, 0.65] band**: … **rest fraction: AUC 0.60**" | `g2.json → early.E_C4_restfrac.auc` = 0.601, CI [0.529, 0.679]. 0.60 is *inside* the band; only its CI upper end exceeds 0.65. Pre-registration §4 (`G2_preregistration.md:115`) says flag if a control's "AUC CI **excludes** [0.35, 0.65]" — C4's CI does not. The code evidently applied "CI not contained in band". Temperature (AUC 0.74, CI 0.66–0.81) triggers the flag under either reading, so the verdict is unaffected. | Minor (rule wording vs. application; disclose) |
| 12 | `results/E/E_power_analysis.md:12` | oracle "recovers **≤ 0.4 %** of capacity at α = 0.05" | `power_changan.json → primary.alphas.0.05.oracle_shift_scale_recovered_pct_median` = **0.441 %** (strict 0.23 %) | Minor (rounding) |
| 13 | `results/RESEARCH_DOSSIER.md:69` | McMaster "72 cells, per-cell V and T, **14 drive cycles** … Downloaded, inspected" | `G_dataset_search_extended.md:43`: "72S PHEV pack … **14 cases**; 15 / 25 °C", verified **READ (README)** only. Files exist in `data/raw/mcmaster/` but no inspection is written up. | Minor (unsupported wording) |
| 14 | `results/RESEARCH_DOSSIER.md:239` | "Not pursued: a ZJU dataset available by email. **Kyle said not to send it.**" | `G_dataset_search.md:84–87`: draft email "has **not been sent** and needs Kyle's approval". No write-up records a decision. | Minor (unsupported) |
| 15 | `results/RESEARCH_DOSSIER.md:358` | "Strong (2 datasets, **94 + 20** units, Bonferroni)" | `rolling_evb_ds1.json → summary[].n_units` = **19** (18 at 40–80 k km) | Minor |
| 16 | `results/results_large.md:172`, `:118–119`; `RESEARCH_DOSSIER.md:143` | persistence "matches it **exactly** (0.73 Ah)" | `rolling_evb_ds1.json`: last 0.7347 vs persist_recent 0.7334 Ah (last beats persistence 6/19, p = 0.17). "Exactly" is a 2-dp coincidence. | Minor (wording) |
| 17 | `results/E/E_power_analysis.md:126–127` | per-vehicle malformed **p90 8.76 %**; unsynced **p90 5.5 %** | Recomputed from `runs/changan_cells.log` (300 vins): p90 8.82 % / 5.7 % (nearest-rank). Median 5.79 %, max 23.2 %, 56 vehicles > 0.1 %, max 29.8 % all match. | Minor (percentile method) |
| 18 | `README.md:12–13` | Tag legend lists MEASURED / DERIVED / ASSUMED / UNGATED only | Every later document (E–H2, dossier) also uses **SOURCED**. | Minor (legend incomplete) |

## 2. Tag issues

| Where | Issue |
|---|---|
| `RESEARCH_DOSSIER.md:11` vs `:177` | The dossier defines MEASURED as "ran it on the NXP FRDM-IMX95-PRO, output gated in the same run", then tags the fleet-wide Changan data-quality and weakest-cell statistics (5.62 %, 1.22 %, −18.8/−19.4 mV, 55/94) **"MEASURED, fleet-wide"**. These are host computations on raw telemetry (`runs/changan_cells.log`, `precheck.json → percell_signal_fleetwide`), not board runs. Under the dossier's own definition they are DERIVED (or need a broader definition). |
| `results/E/results_E.md:58,70`; `results/F/results_F.md:26,75`; `F_preregistration.md:58,150` | Same drift: event catalogue and detector agreement tagged MEASURED. Consistent with the README's broader definition ("ran it; output verified in the same run") but not with `results.md:10` or the dossier. **Systemic:** three definitions of MEASURED coexist (README:12, results.md:10, dossier:11). |
| `RESEARCH_DOSSIER.md:365` | "about 14.7 ns per cell per update; 52 µs for 3,564 cells — MEASURED". The 52 µs is MEASURED (`footprint.json`); the ns/cell slope is DERIVED from two MEASURED points. |
| `RESEARCH_DOSSIER.md:314, :343` | "At 100 Hz, 1,000 cells use about 0.3 % … full cluster 1.1 % of one core" sit under MEASURED headings; `results_H.md:162` and `results_H2.md:112` correctly label these "DERIVED from MEASURED" and specify p99. Dossier drops both qualifiers. |
| `results/raw/probe/last_sgd_steps1_r*.json → tag` | File tag is "MEASURED" (gate passed) while `results.md:109` quotes the 1-step runs as UNGATED. The write-up is the stricter and correct reading (the *full* 1-step gate failed; both are used only for decomposition). No change needed, noted for completeness. |

## 3. Mixed-tier comparisons

| Where | Assessment |
|---|---|
| `results.md:46` (H2 row) | DERIVED B/param accounting (1.63/3.27 MB) set against MEASURED training increment (43–46 MB) to say the brief's model "under-predicts by ~14–27×". This is a prediction-vs-measurement check and both tiers are named; acceptable. 46.4/3.27 = 14.2, 43.3/1.63 = 26.6 — numbers correct. |
| `results_H.md:162–169`, `results_H2.md:112` | Limiter latency/state (MEASURED) vs E1 inference latency/model bytes (MEASURED). Same tier; ratios check: 22.84 ms / 14.75 µs = 1,548×; / 1.50 µs = 15,227×; 225,544 / 23,616 = 9.6×, / 14,576 = 15.5×. |
| `E_power_analysis.md:77–88, 110–113` | Fleet buffer vs z·σ_noise: both DERIVED; comparison labelled "approximate". OK. |
| `results_large.md` throughout | "MEASURED vs DERIVED labels" tag used consistently. OK. |
| `RESEARCH_DOSSIER.md:186–189` | Yuasa "DERIVED from SOURCED, UNGATED" — correct and not compared to any MEASURED number. OK. |

No instance found of a DERIVED/SOURCED number being presented as equivalent to a MEASURED one without labelling.

## 4. Dossier claims not supported by any write-up

1. **BATSS inspection** (`:68`, `:236–237`, `:383`): "cells 2 and 8 both self-discharge 0.8–1.1 mV/h", "Downloaded, inspected". Only READ (metadata) in `G_dataset_search_extended.md`. See #3.
2. **McMaster inspection** (`:69`, `:237`, `:383`): "Downloaded, inspected", "14 drive cycles". Only READ (README), "14 cases". See #13.
3. **ZJU decision** (`:239`): "Kyle said not to send it." See #14.
4. **Partial routes "downloaded"** (`:233`): the G.1b write-up says only BatICM was cloned; Beihang and Weihai downloads happened later (fetch logs in `data/raw/`) and are evidenced by G.2/H2, but BATSS/McMaster downloads are evidenced only by files on disk, not by any write-up.

Everything else in the dossier traces to a write-up. Specifically verified line-by-line: §2 (Study 1 table, E4 numbers, erratum range 25–30 / 59–60 MB), §2.2 (label counts, units, noise, A/C results, EVBattery), §3 (oracle range −0.6 to +1.5 %, MDE 0.76/0.94 → "0.8–0.9 %", 22–25 %, pre-check R² and thresholds, side-finding values, Yuasa 0.85 % / 24–44 %), §4 (41 events, 97.9 %, 3 positives, AUC 0.31/0.35, classes 23/2/4/12, vin116 −195/+116/+57 mV, +4.4 Ah, p = 0.031), §6 (all AUCs/CIs, +0.30 (+0.04, +0.51), temp 20 vs 17 °C, 28 %, DTI 3/72), §7 (286,832 / 40.1 M, 0.008 % CI 0.004–0.011, 13.3 %, bands 0.7–3.3 %, 79 %, 1.50/14.75 µs, 10 B + 13.6 KB), §8 (1,929 / 1.59 M, 0.00 %, 20–28 °C, 3.377 V, 12 mV, 1.95 %, 75 mV/10 °C, 45–54 %, 5.83/52.1 µs, 1.1 %, 24 dropped).

## 5. Pre-registered thresholds: prereg vs results

| Experiment | Threshold(s) in prereg | In results | Match |
|---|---|---|---|
| E (`E_power_analysis.md §5`, fc9c79c) | R² ≥ 0.26 (primary) / 0.39 (strict) on both; per-cell − min/max ≥ 0.05 | `precheck.json → thresholds {0.26, 0.39}, margin 0.05`; `results_E.md:39` | ✓ |
| F (`F_preregistration.md`, 2b9e629) | −60 mV event-day; ≥ 3 event-days; ≤ 14-day gaps; comp ≥ 0.5; SSE ratio 2×; < 8 positives → UNDERPOWERED; AUC_A ≥ 0.70 | `results_F.md:28–29, 50–54, 99`; `forecast.json → decision` | ✓ |
| G.2 (`G2_preregistration.md`, 05af194) | ≥ 20 / ≥ 100 eligible; AUC_A ≥ 0.70 & CI_lb > 0.5 & diff CI_lb > 0; confound band [0.35, 0.65] | 58/335; thresholds unchanged (`results_G2.md:98–102`); band applied as "CI not within band" rather than "CI excludes band" (see #11) | ✓ thresholds; ⚠ band rule wording |
| H (`H_preregistration.md`, 43485e8) | median S_mm < 1 % under M1 and M2; unsafe ≤ 0.1 %; L_pack > 1.001·L_cell; margins grid | `results_H.md:97`; `replay.json → safe_margins` consistent with 0.1 % rule (30_10 = 0.033 %, 50_5 = 0.036 %; 20_10 = 0.20 % correctly excluded) | ✓ (the "differs" typo fix is disclosed as deviation 2) |
| H2 (`H2_preregistration.md`, bf6ca52) | same 1 % rule; ≥ 30 frames; < 0.5 Ah skipped; knee 3.35/3.45 V; bands | `results_H2.md:19, 73, 117`; `replay.json → safe_margins = [75_10, 100_10]` (50_10 = 0.117 % correctly excluded) | ✓ |
| Study 2 (`results_large.md:20–21`) | Bonferroni 0.05/20 = 0.0025; majority; median | `summary_large.json → bonferroni_alpha 0.0025, n_tests 20, helps_robustly all false` | ✓ (rule itself was added post-preliminary; disclosed) |

## 6. Does each verdict follow from its own decision table?

- **E:** R² −0.020/−0.176 < 0.26/0.39 → NO-GO → INCONCLUSIVE. ✓
- **F:** 3 positives < 8 → UNDERPOWERED; no claim either way. ✓
- **G.2:** AUC_A = 0.591, CI [0.511, 0.671]; A−B = +0.071, CI [+0.009, +0.136]. Row 1 fails (< 0.70); row 2 fails (diff CI excludes 0); row 3 fails (CI excludes 0.5). Genuinely uncovered; disclosed as deviation 1; no threshold moved; verdict wording ("beats min/max modestly; not SUPPORTED") is the only honest reading. ✓ Note both lower bounds are thin (0.011 above 0.5; 0.009 above 0) — worth saying in the dossier.
- **H:** 7.6e-5 (M1) and 8.3e-5 (M2 median of medians) < 1 % → NO BENEFIT. ✓
- **H2:** 0.0 / 0.0 < 1 % → NO BENEFIT; cold band empty → "unanswerable" correctly not read as a null. ✓
- **Study 2:** no method has `helps_robustly = true` in any band/label set → "none". The one p < 0.0025 vs frozen that favours a method does not exist (best is strict last_guard 0–5 k, p = 0.011); against persistence, methods are significant but that is the wrong direction for a positive claim. ✓
- **Study 1:** H4 "not supported" from 6/20 improved, median −12.6 %. ✓

## 7. What reconciled (spot-check inventory)

- **Study 1 (`summary.json`, `raw/e4*.json`, `raw/probe/*.json`):** 225,544 B; 22.84/22.95 ms; 37.45/37.91 ms; 3.4/3.8 MB; 43.7 MB; full SGD 405.8 (403.0–408.2), +43.3 (42.8–46.6); full Adam 408.8 (405.8–409.2), +46.4 (43.9–46.9); last 372.5/373.6, +10.8/11.8; 520 B; 1,713,160 B; 1.19/0.44 s; E4 all seven rows (medians, IQRs, 6/20, 10/20); −12.6 % (−56.8…+3.6); noise 0.648; FT10 row; no-odometer 1.25 Ah / −44 % / 6/20; test-window gap 2.5–45 k (median 21), end median 77 k (max 154), label drop median 2.0 (−0.1…4.3); car 65 0.94 → 3.73; erratum 24.9/27.2 and 60.4 MB (median HWM − median RSS); probe 8.1/9.3 and 41.7/42.9 MB; E5 table arithmetic; 915/2,221 examples → 1.6/3.8 MB and 232/564 KB.
- **Study 2 (`summary_large.json`, `rolling_evb_ds1.json`, `e4_*_k*.json`, `expD/*`, train logs):** every cell of the A table (incl. tie counts 32/39 and 11/15), both C tables (all 5×6 cells per label set), EVBattery table incl. all sign-test p-values recomputed exactly (0.0007, 0.0044, 0.17, 0.064, 0.0013, 0.0075), fleet validation ranges 4.36–4.59 vs 5.45–5.87 and 3.96–4.62 vs 4.94–5.88, §D 520/66,568/1,713,160 B, 445/442/445/1,192 ms, 27.2/29.7/31.4/59.0 MB, gates 2/2 each, census present.
- **E:** every row of the α tables (both label sets), SDs 2.18/4.11 and 1.87/3.22, SEs, MDE 0.757 %/0.942 % (0.93/1.15 Ah), n_labels 5,550/2,049 → scored 4,610/1,599, missing ≤ 1.5 %, in-sample 0.011/0.004, between-unit 0.08/0.22, Yuasa table, fleet-wide 820,695,014 frames / 5.62 % / 1.22 % / 148 M vectors.
- **F:** 300/50/20/232/41/41/7 (abrupt vins exact), classes, deepest events and shifts, tap artefacts 5–11 mV, 97.9 %/98.9 %/20-25-19, forecast numbers, consequence 18 events from 7 vehicles (272:7, 93:5), +3.6 vs −1.5, p 2.4e-6, D3 +4.4/0.031, D4 13/20 colder, −1.7 °C, D2 p 0.10, ΔR max 0.42.
- **G.2:** every AUC/CI, adjusted coefficients, concordance, DTI ranks, 83 %; recomputed from `features.csv`: median temp 20 vs 17 °C, Spearman 0.013, temperature-stratified AUCs 0.587/0.532 early and 0.661/0.480 late (write-up 0.59/0.53, 0.66/0.48; late uses early-window temperature bins).
- **H:** all replay headline numbers, tie-aware and raw fractions, sensitivity, margin sweep, temperature-band table recomputed from `replay_sessions.npz` (2,855/18,351/38,397/226,690/539; medians 0.70/0.93/0.88/0.00/3.30 %; p90s), 79.0 %; footprint table all 20 cells; gate 20/20, max dR 4.8e-7; spikes 57–724 µs; p50 range ≤ 1 ns.
- **H2:** 1,929 sessions = 217×9 − 24; 1.59 M frames; 404 kAh; temperature percentiles; bands 0/69/1,067/793/0; 1.95 %; 36.1/75.6/20.5 %; 3,377 mV / 12 mV; sensitivity; 76 % unsafe at zero margin; footprint table; gate 10/10, dR 2.4e-7; spikes 61–217 µs; p50 spread ≤ 42 ns; VLIM 3650 in `board/build.json`.
- **Git:** fc9c79c, 2b9e629, 43485e8, 05af194, bf6ca52, b9b4e66 exist with the stated dates and precede the corresponding results commits.

## 8. Recommended edits (smallest set)

1. `results_F.md:42` and `RESEARCH_DOSSIER.md:199`: 12 → **11**; drop "contiguous".
2. `RESEARCH_DOSSIER.md:68–69, 236–237, 383`: either add the BATSS/McMaster inspection to a G write-up (with the script and the 0.8–1.1 mV/h computation) or downgrade to "downloaded, metadata read; not analysed".
3. `RESEARCH_DOSSIER.md:124–127`: add the MAD column (3.91 / 2.76 Ah) or restate the ratio as 1.4–1.6× on SD.
4. `RESEARCH_DOSSIER.md:177`: retag side findings DERIVED (or define MEASURED once, repo-wide, and align README/results.md).
5. `RESEARCH_DOSSIER.md:302–303`: "(30 mV, 10 °C) → 34 %; (50 mV, 5 °C) → 26 %".
6. `results_G2.md:53–57`: state the applied flag rule ("CI not contained in [0.35, 0.65]") and note it is stricter than the prereg wording.
7. `results_H.md:135`, `results_H2.md:103`: ≤ 2.0 % and ≤ 0.4 %.
8. Pick one KB basis for H/H2 tables (results.md says KiB).
