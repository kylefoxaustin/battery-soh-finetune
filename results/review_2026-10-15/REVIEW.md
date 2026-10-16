# Independent review of the programme — consolidated findings (2026-10-15)

**What this is.** Six independent reviewers, running on Claude Fable 5.1, each audited one part of the programme
against `results/RESEARCH_DOSSIER.md` (commit 731c2b7), the write-ups, the code and the data.

| Reviewer | Scope | Report |
|---|---|---|
| s12 | Studies 1–2 | [`s12_report.md`](s12_report.md) |
| ef | Experiments E and F | [`ef_report.md`](ef_report.md) |
| g2 | Experiment G.2 | [`g2_report.md`](g2_report.md) |
| h | Experiments H and H2 | [`h_report.md`](h_report.md) |
| audit | Numbers across all documents | [`audit_report.md`](audit_report.md) |
| big | Big picture: framing, missed datasets, next experiments | [`big_report.md`](big_report.md) |

Reviewer scripts and outputs are in `scripts/<reviewer>/`. They were CPU-only, did not modify the repo and did not
touch the board.

**How findings were checked.** Each critical finding was **independently re-checked by the main session** before
being accepted. The check is recorded in the "Checked" column:

| Status | Meaning |
|---|---|
| ✔ reproduced | Re-ran it or recomputed it ourselves |
| ✔ logic | Verified by argument or inspection |
| ✘ refuted | We checked and the claim is wrong |
| — | Reviewer-only and not yet re-checked. Treat it as plausible, not established. |

Reviewer numbers are DERIVED and post-hoc unless stated. None of them is a new pre-registered result.

---

## 1. Verdict changes (what the programme now says differently)

| # | Item | Before | After | Checked |
|---|---|---|---|---|
| 1 | **G.2: the one positive result** | Per-cell beats min/max (AUC 0.59 vs 0.52, survives adjustment) | **Substantially weakened; treat it as a hypothesis.** See below. | ✔ reproduced (sentinel and temperature split) |
| 2 | **F: "min/max sees 98 % of per-cell anomaly-days"** | Strong evidence that min/max suffices for detection | **Near-tautology.** See below. | ✔ logic |
| 3 | **Study 2: "per-unit adaptation does not help"** | No method helps robustly | **Too broad.** See below. | ✔ reproduced (`scripts/s12/d2_shrink_eb.py`) |
| 4 | **H2's pack-mean margin result** | Needs 75 mV / 10 °C; extremes 45–54 % faster | **Artefact of stale cell data in November 2024.** See below. | ✔ reproduced (monthly count) |
| 5 | **F's post-hoc label rise after events** | +4.4 Ah, p = 0.031 (flagged as post-hoc) | **Withdraw.** See below. | — |
| 6 | **E pre-check "failed decisively"** | Per-cell route adds nothing measurable | **The test was nearly unpassable by construction.** See below. | — |
| 7 | **Synthesis one-liner** | "On every public dataset we could find…" | **Over-generalises.** See below. | ✔ logic |

**1. G.2.**

- **The faulty and normal records were produced differently.** We confirmed this ourselves:
  - every one of the 335 normal vehicles has current-sentinel (−1000) frames, but only 17 of the 58 faulty ones do;
  - median maximum temperature is 41 °C faulty vs 31 °C normal.
- **The reviewer adds that faulty records:**
  - have about 2× the contiguous runs (AUC 0.83);
  - end hotter;
  - have derived x/z columns that differ by 2–3 orders of magnitude.
- **Effect on the result:**
  - Under cohort stratification, the pre-registered A − B edge is no longer significant (perm p = 0.07–0.11).
  - The late-window gain is *not drift*: shuffling the block order keeps it.
  - Early A − B fails under several reasonable alternative definitions; switching block median to block mean gives
    A − B = −0.007.
- **What survives:** a weak early per-cell signal (AUC ≈ 0.6) persists after matching. No lead-time claim and no
  per-cell-superiority claim can be made from this release.
- **Also:** z columns are model-derived, not cell temperatures. vin_1 column 2 is identically zero for QAS, so the
  "mileage sanity" check was vacuous.

**2. F's 98 % overlap.**

- A cell's daily mean deviation below −60 mV implies the daily mean of (vmin − mean) is also below −60 mV. So on
  identical frames, overlap is 100 % by arithmetic; the reviewer recomputed 730 of 730.
- The 2 % gap came only from slim-vs-cell frame-set differences.
- The detection question was never actually tested. See finding 8 below for a per-cell-only detector.

**3. Study 2.**

- A *shrunken* per-unit residual offset (closed form, a few bytes of state, κ = 3.55 taken from E's variance split)
  passes **every clause** of the pre-declared "helps robustly" rule at 0–5 k km on Changan primary:
  - median 3.85 vs 4.10 Ah frozen (−5.4 %);
  - beats frozen on 67 of 89 units, p = 1.9e-6;
  - beats persistence on 70 of 89 units.
- **Caveats:**
  - The method family is post hoc; the reviewer tried several variants.
  - κ comes from a whole-data variance decomposition.
  - It passes in that one band only; on strict labels it points the same way but does not pass (24 of 37, sign
    p = 0.10).
- **Corrected wording:** "on-device *training* does not help; a bytes-of-state shrunken running offset is a credible
  small short-horizon gain that needs a pre-registered confirmation."
- **Related (reviewer only, —):**
  - "Persistence matches the only gain" holds for EVBattery only. On Changan, recent-label persistence is the worst
    control.
  - "The fleet model sits at the noise floor" is unsupported. The floor is an upper bound: frozen RMSE is below the
    unit's own floor in 54 of 94 units, and covariate correction lowers the floor 4.76 → 4.49 Ah.

**4. H2's pack-mean margin result.**

- We counted frames with any cell more than 100 mV from the median:

| Month | Such frames |
|---|---|
| November 2024 | **44,905** |
| Any other month | ≤ 515 |

- The cause is cell series that log once and then go stale for about 37 h, or whose only log predates `StartTime`.
  These pass the extractor's "has logged" guard (`analysis/H2_replay.py:75-76`).
- Excluding them (reviewer recomputation), the safe margin becomes **30 mV / 10 °C with a median 33 % saving,
  identical to H**.
- **The primary H2 verdict (NO BENEFIT over min/max) is unaffected.**
- Also: deviation 1's explanation is partly wrong. Rack 3's empty session is missing rack current, not cell series.

**5. F's post-hoc label rise.** The analysis used all labels, including slow-charge labels that sit about 6.8 Ah
above the fast-charge trend. vin116 switched from 48 A to 14.8 A charging. On the 48–51 A band it becomes n = 5,
+2.4 Ah, p = 0.062.

**6. E's pre-check.**

- The within-unit residual is nearly white: lag-1 autocorrelation is about +0.06 to +0.09. A 5 k km-window feature
  cannot explain 26 % of it.
- E_precheck's OLS is not centred against a unit-centred target, which explains the negative R².
- **INCONCLUSIVE stands; the wording should say "unpassable test", not "decisive failure".**

**7. Synthesis one-liner.** Most datasets *could not have shown* the effect:
- warm climate;
- HVAC-controlled container;
- labels we derived ourselves;
- no fault ground truth;
- uniform per-cell limit maps, which make L_cell ≥ L_mm by construction.

BATSS, McMaster and BatICM were found but not used. The story needs a "could this data have shown it?" column.

## 2. Other major findings (not verdict-changing)

| Area | Finding | Checked |
|---|---|---|
| **H/H2 design** | `L_cell ≥ L_mm` by construction; one shared map excludes the mechanism per-cell limiting exists for (per-cell R / capacity). Post-hoc Changan per-cell R from current steps (38 vehicles): R_max / R_med = 1.20; a per-cell-R headroom limiter gains median +2.0 % (p90 +4.4 %) admissible current at vmax ≥ 4.0 V. Recorded currents are 0.14 C (Changan) and 0.46 C (Weihai), against a 1.5 C assumed ceiling. | — |
| **H pack-mean** | A straw man: GB/T frames carry min/max *and* their indices. The 26–54 % is mostly the 10 °C margin derating `C_T` at 18–21 °C. "34 % faster" should read "34 % shorter". | ✔ logic (wording) |
| **Board timing** | Every latency is an integer multiple of 41.67 ns, a 24 MHz timer, so "≤ 1 ns repeatability" is quantisation. Not measured: ingest / parse cost, RT isolation, and the M7/M33 cores. Worst case (724 µs) is not in headlines; the run script is not committed. Gate dR comes from FMA (confirmed in aarch64 asm). | — |
| **H2 gate frames** | These are the first 2,500 s of each op; the taper is active in only 348 / 10,000 frames. | — |
| **Weihai logging** | Weihai is periodic (about 60 s, staggered, with a 600 s heartbeat), not change-logged as the prereg said. The ZOH age median is 36–45 s. Interpolation instead of ZOH leaves the safe set unchanged on Oct ops. | — |
| **Changan labels** | The label rises +2.34 Ah per e-fold of wake→full segment duration; 6–24 h segments (7.4 % of primary labels) are +3.7 Ah high (`data/changan_labels.py:36`, MAX_SEG_S = 3 days). Fixable at the label stage. | — |
| **Changan OCV table** | `odo.min()` NaN-poisoning drops 8 / 300 vehicles from the OCV table (`changan_labels.py:57`). Negligible: 2.2 % of rests. | — |
| **F classes** | "SOC-like" rests on an ASSUMED BMS-SOC-indexed OCV table with an implausible slope profile, so it is not independent evidence. 22 of 41 "events" are chronic cells crossing a fixed threshold (own shift > −30 mV), not onsets. | — |
| **F, cell 31** | Counting any qualifying event, cell 31 appears in 4 of 20 vehicles; the look-elsewhere-corrected null is P = 0.021. Cell 31 is not a generally weak position. Inferred: 12-cell modules, resistance hotspots every 4th index (busbars). This supports a sense-channel / connector hypothesis. | — |
| **Statistics, Study 2** | The Bonferroni family is per label set (60 tests overall). Harm claims use raw p. "Significantly worse at 40–80 k" holds unguarded only. | — |
| **Pre-registration timing** | A reviewer suggested the F code pre-dated its pre-registration. | **✘ refuted:** the session transcript shows every prereg (F, H, G.2, H2) was written and committed before its analysis file was first created, by 1–2 minutes each |

## 3. Numeric corrections

The audit found **no critical discrepancies**. Every verdict follows from its pre-registered rule and its JSON.

**Major corrections:**

1. **vin272 has 11 qualifying events, not 12, and they are not contiguous** (cells 31–51 with gaps).
   ✔ reproduced from `results/F/events.json`.
2. The dossier's "fade ~1.6–2.3× label noise" uses MAD. Against the SD shown it is **1.4–1.6×**. ✔ recomputed.
3. The dossier claimed BATSS and McMaster were "inspected" with specific numbers that no committed output supported.
   Corrected below, with reviewer probes now archived.

**Minor corrections:**

| Item | Stated | Correct |
|---|---|---|
| H p99 repeat spread | ≤ 1.5 % | 2.0 % at N = 324 |
| H2 p99 repeat spread | ≤ 0.2 % | 0.35 % at N = 396 |
| H2 cost per cell | 14.7 ns | 14.6 ns |
| H R-update branch share at N = 1000 | 6 % | 27 % |
| G.2 rest-fraction AUC 0.60 | "outside [0.35, 0.65]" | inside |
| Dossier, 26 % pack-mean figure | attributed to 30 mV / 10 °C | belongs to 50 mV / 5 °C |
| Dossier, EVBattery units | "94 + 20 units" | 94 + 19 |
| Dossier, persistence vs rolling FT | "matches exactly" | 0.7347 vs 0.7334 |
| Dossier, fleet statistics | tagged MEASURED | should be DERIVED |
| Dossier, ns-per-cell and "% of core" | tagged MEASURED | should be DERIVED from MEASURED |

## 4. Things that are solid (per reviewers)

- **Method discipline.** Pre-registration before code (confirmed), numbered deviations, persistence controls,
  Bonferroni, same-run board gates and licence tracking. The big-picture reviewer called it "better than most
  published battery-ML work".
- **Studies 1–2 hygiene.** Fold hygiene and leakage controls are clean: normalisation is fitted on train units and
  the guard is causal.
- **E arithmetic.** E's MDE and R² arithmetic was verified, and the stop rule was honoured.
- **Board gates.** The C↔Python gate semantics are right, and the MCOS datetime decoder is internally consistent.
- **Reproduction.** H and H2 primary verdicts were reproduced, and G.2's features were reproduced to 1e-12.

## 5. Missed opportunities — ranked (reviewer proposals; none run as a pre-registered test)

1. **Confirm the shrunken per-unit offset.**
   - Pre-register κ and the rule, then run on Changan strict, EVBattery ds2/ds3 (already in `data/processed`), and
     the fixed-label Changan.
   - Cheap (CPU, hours). The first credible "per-unit" positive, and it costs bytes of state, not training.
2. **G.2 done properly.**
   - Pre-register a cohort-indistinguishability gate (processing-path features must be AUC ≈ 0.5 after matching).
   - Use matched or same-path subsets, DTI/GIS as path controls, and the authors' MC-AE per-cell residuals vs a
     min/max version.
   - Ask the authors (Beihang) for fault codes and failure dates. Contact is Kyle's call.
3. **H3: per-cell limiter with per-cell parameters.**
   - Replay on Changan's 2,855 cold (< 10 °C) sessions, with per-cell R and capacity from current steps.
   - ~~Replay on McMaster's module-blocked run (per-cell thermistors, 28 °C intra-pack spread).~~ **Corrected
     2026-10-15:** the 28 °C was two dead thermistors (cells 12 and 35 stuck at 1.0 °C). The real McMaster spread is
     at most 11 °C, with no cold regime. McMaster stays useful for a hot, regen-at-4.2 V per-cell-R arm. See
     `../X/README.md`.
4. **H2 correction.** Add a heartbeat staleness screen (healthy series are never older than 590 s), then re-run the
   margin sweep and rewrite the H2 margin text. CPU, about 1 h.
5. **Per-cell-only detection on Changan.**
   - The reviewer's "drift vs own baseline" (< −30 mV for ≥ 3 days) flags 23 vehicles and 76 cells.
   - 40 cells in 5 vehicles are fully silent to min/max: vin272's 30-cell block, vin23 cells 28/30/31, vin158 cell
     89. Four of those vehicles are absent from F's catalogue.
   - Also: per-cell self-discharge across parking gaps. vin272 cells 31–51 drain at up to −0.81 mV/h relative,
     which is BATSS-ISC scale.
   - This is where per-cell data *does* see what min/max cannot. It deserves a pre-registered test.
6. **BATSS blind prediction.**
   - In the ISC run, cell 8 drifts fastest at rest (−1.00 mV/h) while cell 2 is the min cell at every step.
   - **Which cell carried the resistor is still not in the release**, so this is a *prediction* to confirm with the
     authors (CIDETEC), not ground truth. Contact is Kyle's call.
7. **LFP per-cell SOC / capacity on Weihai.** Knee-crossing order at 3.40–3.45 V gives a per-cell ranking. Weihai is
   CC BY, so the result is commercially clean.
8. **AP-specific value never measured.**
   - Per-cell data reduction / selective upload. Raw 96 cells × 2 B × 8,640 frames is about 1.66 MB per vehicle per
     day (DERIVED).
   - On-pack history storage, with EU Battery Regulation 2023/1542 Art. 14 SoH access as the motivation.
   - An M7/M33 timing of the limiter, including ingest.
   - The reviewer's framing point: every per-cell computation tested is MCU-class. The programme showed these uses
     *don't need* an AP, which is itself a useful result. Note that GB/T 32960 frames already carry full per-cell
     lists (SOURCED in `big_report.md`), so the cloud already has per-cell data.
9. **Bench fault-injection string** (about $1–3k). The only route to confirming F's diagnosis classes, and it would
   produce a CC BY dataset.
10. **Datasets to watch.**
    - arXiv 2608.10825: 99 EVs, 14S, teardown-backed per-cell labels, embargoed.
    - TUM thermal-runaway modules: mediaTUM 1717758; licence to confirm.
    - Schaeffer 28 × 8S LFP home systems: Zenodo 13715694, CC BY-NC.
    - No public cold-climate per-cell charging dataset was found.

## 6. What was changed in the repo as a result

The original write-ups were left intact. Each affected write-up got a dated **post-review addendum** that points
here:

- `results_large.md`
- `E/results_E.md`
- `F/results_F.md`
- `G2/results_G2.md`
- `H/results_H.md`
- `H2/results_H2.md`

`RESEARCH_DOSSIER.md` was corrected in place: numbers, tags, the G.2 / F / H2 / Study 2 status, the synthesis wording
and the dataset descriptions.

No re-analysis was promoted to a result. Items 1–5 in §5 need their own pre-registrations.
