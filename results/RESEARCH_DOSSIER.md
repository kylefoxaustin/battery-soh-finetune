# Research dossier — per-unit and per-cell battery intelligence on an i.MX 95-class processor

Covers every study and experiment to 2026-10-15 (local `master`, commit `b9b4e66`). This is a single narrative over
the per-experiment write-ups, which remain authoritative for exact numbers. Where this file and a write-up
disagree, the write-up wins and this file has a bug.

> **Revised 2026-10-15 after an independent six-reviewer audit**
> ([`review_2026-10-15/REVIEW.md`](review_2026-10-15/REVIEW.md)).
> - G.2's positive result is substantially weakened.
> - F's 98 % overlap is near-tautological.
> - Study 2's negative is narrowed to on-device *training*.
> - H2's pack-mean margin result is withdrawn as a stale-data artefact.
> - Numbers and tags are corrected throughout.

**Tags.**

| Tag | Meaning |
|---|---|
| **MEASURED** | Ran it on the NXP FRDM-IMX95-PRO, output gated in the same run. |
| **DERIVED** | Computed from data or measurements. |
| **ASSUMED** | A stand-in we chose. |
| **SOURCED** | From a paper or datasheet. |
| **UNGATED** | Not quotable. |

A DERIVED or SOURCED number is never compared against a MEASURED one as the same tier.

---

## 0. The research question, and how it evolved

The original question (Build Brief, Oct 2026) was whether an i.MX 95-class application processor should do
**on-device learning** for battery state-of-health (SoH). Specifically: is last-layer fine-tuning of an SoH network
feasible on the A55 cores, and is it worth it?

**How the question evolved:**

- **Study 1** answered "feasible, not worth it".
- **Study 2** confirmed "not worth it" at scale.
- The question then shifted from *per-unit learning* to *per-cell data*: the full cell-voltage vector, as opposed to
  the min/max/mean scalars a typical BMS or GB/T-32960 telemetry frame carries. If per-cell data has value, an
  application processor has a reason to ingest and process it locally.

Experiments E–H2 each test one possible value of per-cell data:

| Experiment | Possible value of per-cell data |
|---|---|
| E | Tighter capacity bounds |
| F | Earlier fault warning |
| G | Validated fault diagnosis |
| G.2 | Flagging packs that later fail |
| H / H2 | Faster charging under per-cell limits |

Each also asks what the processing costs on the board.

**Method discipline**, from Experiment E onward:

- A brief, then a pre-registration committed to git *before* any analysis code, fixing hypotheses, thresholds and the
  decision table.
- Deviations are numbered in the results file. Thresholds are never moved after results are seen.
- Board work uses:
  - a hard reservation and a process census before and after;
  - a pinned core with the `performance` governor (restored to `ondemand`);
  - a same-run correctness gate against a Python reference.

---

## 1. Data used

| Dataset | What it is | Licence | Used in | Key limitation |
|---|---|---|---|---|
| **EVBattery** (He et al., figshare 23301881) | Charge snippets from ~100 EVs of one manufacturer (sub-dataset 1), with supplied capacity labels | CC BY 4.0 | Study 1, Study 2-C | Labels are supplied but their derivation is opaque; 20 held-out cars |
| **Changan 300-EV** (Liu et al., *Nat Commun* 2025) | 300 NMC EVs, 96s / 32 probes, 10 s telemetry, 130–220 k km each, ~821 M frames, per-cell voltage lists | **CC BY-NC-SA 4.0, academic only** | Study 2, E, F, H | **No capacity label** (we derive one, see §2.2). No fault or service records. 5.6 % malformed per-cell frames, 1.2 % desynced from the scalars. |
| **Yuasa second-life** (arXiv 2609.04487) | 324 LMO cells in 27 modules, a 12.5 h field window | MIT | E (descriptive) | Per-cell Q are the paper's model estimates; one snapshot |
| **Beihang** (Cao et al., *Nat Commun* 2025; Zenodo 10656500) | 515 EVs across 3 manufacturers (QAS 393 at 110 cells, DTI 80 at 85, GIS unlabelled); per-cell V snapshots (the `z` columns are model-derived, not temperatures) | CC BY 4.0 | G.2 | Labels are vehicle-level binary from **teardown**; no failure dates; faulty IDs contiguous (cohort) |
| **Weihai BESS** (Qu et al.; Zenodo 20094787) | LFP grid battery, 9 racks × 396 cells, 216 probes per rack, change-logged, Oct 2024 – May 2025 | CC BY 4.0 | H2 | The container is HVAC-controlled (probes 20–31 °C); MATLAB datetime objects needed our own decoder |
| **BATSS** | Bench tests including an internal-short-circuit (ISC) test | CC BY | Downloaded; metadata read in G.1b; probed post-hoc in the review | The release doesn't say which cell had the resistor. A review probe (`review_2026-10-15/scripts/big/`) found cell 8 drifts fastest at rest (−1.00 mV/h) while cell 2 is the min cell. That is a prediction, not ground truth. |
| **McMaster** | 72 cells, per-cell V and per-cell thermistors at 1 Hz, 14 cases | CC BY | Downloaded; README read in G.1b; probed post-hoc in the review | Thermal faults only. 1 Hz drive cycles, charge-sustaining at about 0.9 SOC, with no charge sessions. The review's "28 °C spread" is **two dead thermistors** (cells 12 and 35 stuck at 1.0 °C). The real spread is at most 11 °C, and the minimum is 10 °C or above. See `X/README.md`. |
| **BatICM** | 4 EVs | MIT | Inspected (G.1b) | Too few units |

---

## 2. Study 1 — on-device last-layer fine-tuning (EVBattery + board), 2026-10-08

**Model.**

- 2 × LSTM-128 → Linear 64 → ReLU → Linear 1, 214,145 parameters, with the last layer at 65.
- Inputs: 128-sample snippets at 10 s, 7 raw channels plus rolling statistics plus odometer.
- Trained on 68 cars and validated on 12. The fleet model beats mileage-linear (1.196 vs 1.290 Ah val RMSE).

**Feasibility (MEASURED on the board, gated):**

| Quantity | Value |
|---|---|
| int8 TFLite model | 220 KB |
| int8 inference latency | **22.84 ms p50**, one A55 core; bit-identical to the host on 256 snippets |
| fp32 inference latency | 37.45 ms |
| Last-layer Adam state | 520 B |
| Full-retrain Adam state | 1.63 MB |
| Training step (bs 32, seq 128, 2 threads) | 0.44 s last-layer, 1.19 s full |

**Memory added by training** (corrected reference point, see the erratum in `results.md`): ≈ 25–30 MB last-layer and
≈ 59–60 MB full. Back-propagation-through-time activations dominate, not optimizer state.

**Worth it (MEASURED vs supplied labels, 20 held-out cars)?** No.

- The split per car is the first 30 % to fine-tune, a 20 % gap, and the last 50 % to test.
- Last-layer fine-tuning *worsened* median RMSE: 0.860 → 1.085 Ah, better on only 6 of 20 cars.
- The frozen model already sits near the label-noise floor (≈ 0.65 Ah).
- Early data cannot teach later degradation.

**Design choices that matter.**

- The 30 / 20 / 50 split.
- 300 Adam steps at 1e-3.
- The odometer input. Removing it weakens the fleet model, and fine-tuning hurts *more*.

## 2.2 Study 2 — per-unit adaptation at scale (Changan), 2026-10-08

**The capacity label is DERIVED: the crux.**

- The Changan release has no capacity label, and the BMS SOC is stale at full charge.
- We built an OCV–SOC table from early-life rests: 62,877 rests in 77 bins, ASSUMED.
- The label is Ah-integration from a post-rest OCV SOC to max-cell ≥ 4.20 V, at a fast-charge end current of
  48–51 A, within a 95–145 Ah plausibility band. Slow-charge labels show no age trend and are excluded.

**What that label set gives:**

| | Primary | Strict |
|---|---|---|
| Labels | 6,638 | 3,285 |
| Qualifying units (≥ 20 labels over ≥ 50 k km) | 94 | 45 |
| Within-unit noise SD | 4.76 Ah | 3.84 Ah |
| Per-unit lifetime fade | 6.5 Ah | 6.3 Ah |

So fade is only about 1.4–1.6× the label-noise SD (1.7–2.3× the MAD).

**Protocol.**

- 4-fold by unit.
- A method "helps" only if it beats frozen at the median, on a majority of units, *and* passes a sign test at
  Bonferroni 0.05/20.
- It must also beat a no-model persistence control (the mean of the unit's last 5 k km of labels).

**Results.**

- **One-shot fine-tuning reproduces the negative.** Last-layer fine-tuning is +1.9 % worse on primary and +10.4 % on
  strict; whole-head fine-tuning is significantly worse on both.
- **The rolling protocol** (re-fine-tune every 10 k km on the last 30 k km) finds no robust benefit at any horizon.
  It is significantly worse at 40–80 k km.
- **EVBattery, 0–5 k km**: rolling fine-tuning does beat frozen (0.73 vs 0.84 Ah, 17 of 19, p = 0.0007), but
  **persistence matches it** (0.7334 vs 0.7347 Ah).

**Decision: PER-UNIT ADAPTATION DOES NOT HELP** at this label quality.

**Post-review (2026-10-15): narrowed to on-device *training*.** A closed-form *shrunken* per-unit offset (bytes of
state) passes every clause of the robustness rule at 0–5 k km on primary labels:

- median 3.85 vs 4.10 Ah;
- beats frozen on 67 of 89 units, p = 1.9e-6;
- beats persistence on 70 of 89 units.

This was reproduced, but it is post hoc and passes in one band only. On Changan, recent-label persistence is the
weakest control, so "persistence matches the only gain" is EVBattery-specific.

**Disclosed:**

- The persistence control and the Bonferroni rule were added after preliminary results; both make a positive claim
  harder.
- N = 94 is 6 short of the brief's 100.

---

## 3. Experiment E — can per-cell data tighten a worst-case capacity bound? (2026-10-13)

**Question.** Can per-unit and per-cell information produce a capacity lower bound that is tighter than a fleet prior
at matched, verified risk α?

**Power analysis first** (`E_power_analysis.md`, committed fc9c79c before any per-cell/label join):

- Even an **oracle** that knows each unit's true offset and spread recovers −0.6 % to +1.5 % of capacity at
  verifiable α (0.10–0.01).
- The minimum detectable change is about 0.8–0.9 %.
- Only 22–25 % of fleet-model residual variance is a persistent per-unit offset.
- α = 0.001 is unverifiable at this data size.

**Pre-registered per-cell pre-check.**

- Do 6 causal per-cell features (5 k km window before each label) explain the within-unit residual?
- Out-of-fold R² was −0.020 (primary) and −0.176 (strict), against thresholds of 0.26 and 0.39. **FAIL.**
- Min/max-only features: −0.010 and −0.129.

**Verdict: INCONCLUSIVE, with an informative upper bound of about 1 % recoverable capacity.** The estimators, coverage
gate and board footprint (E6) were not built, per the stop rule.

**Side findings (DERIVED from telemetry, fleet-wide):**

| Finding | Value |
|---|---|
| Malformed per-cell frames | 5.62 % (the brief said 0.4 %) |
| Per-cell list out of sync with scalar min/max | 1.22 % (the brief said essentially never) |
| Median weakest-cell deviation | −18.8 mV in the first third of life, −19.4 mV in the last; no growth with age |
| Same weakest cell in both thirds | 55 of 94 vehicles |

**Yuasa comparison** (DERIVED from SOURCED, UNGATED):

- In a healthy module, capacity heterogeneity costs about 1 % (module-mean vs weakest-cell Q, median 0.85 %).
- It costs 24–44 % only in the 2 modules with a physically failed cell.
- So per-cell value here looks like **fault detection, not buffer sizing**.

## 4. Experiment F — does per-cell data catch a failing cell early, beyond min/max? (2026-10-13)

**Events.**

- An event-day is one cell's daily rest-mean deviation below −60 mV. The threshold was chosen after seeing fleet
  counts, which is disclosed.
- A qualifying event is ≥ 3 consecutive event-days.
- 20 of 300 vehicles have a qualifying event, giving 41 events. vin272 alone accounts for 11, on cells 31–51 with
  gaps, which looks module-wide.

**Detection overlap:** min/max (`vmin − V/96`) flags **97.9 %** of the per-cell event-days.

*Post-review:* this is close to an identity. On identical frames a per-cell event-day is always a min-only day
(730 of 730), so detection was not actually tested. A per-cell-only detector, drift against each cell's own
baseline, finds 40 cells in 5 vehicles that min/max cannot see (post-hoc).

**Primary forecast** (first-half features predict a second-half first anomaly): **UNDERPOWERED**.

- There were 3 positives, against a pre-registered floor of 8.
- AUC was 0.31 for per-cell and 0.35 for min/max, both meaningless at n = 3.

**Diagnosis** (DERIVED physics classes, no ground truth):

| Class | Events |
|---|---|
| SOC-like | 23 |
| Offset-like | 2, both on cell 31 in different vehicles, with onsets around day 356–362 |
| Tap-fault-like | 4, of which 1 is convincing: vin116 cell 21, −195 mV with neighbours at +116 and +57 mV |
| Unresolved | 12 |

**Post-hoc surprise:** capacity labels *rise* after event onset, by +4.4 Ah median excess over an age-matched
placebo. That is 6 vehicles, Wilcoxon p = 0.031, which is the minimum attainable p at that n.

**Withdrawn post-review:** the analysis mixed slow-charge labels. On the 48–51 A band it is n = 5, p = 0.062.

**Verdict.**

- **Detection:** not tested, because the overlap metric was an identity. A per-cell-only detector looks promising
  (post-hoc).
- **Early warning:** untestable.
- **Diagnosis:** per-cell adds it, unconfirmed. Cell 31 recurs in 4 of 20 vehicles (corrected P ≈ 0.02), which
  points to a sense-channel or connector cause.

## 5. Experiment G.1 / G.1b — is there public ground truth to validate F's diagnosis? (2026-10-14)

**G.1.** No public dataset pairs per-cell telemetry with independent, located fault labels. The best was Yuasa: 2
cells, one fault type, and the cells were chosen for inspection *because* the telemetry looked odd. **NO-GO.**

**G.1b** (extended niche search, three parallel agents, multilingual):

- Still no public dataset with deliberately injected, cell-located electrical faults on a ≥ 4-cell string.
  Bench papers that did inject such faults call their data confidential.
- **Partial routes, downloaded:**
  - Beihang (teardown labels) → became G.2.
  - Weihai → became H2.
  - BATSS ISC test.
  - McMaster thermal faults.
- **Pending:** arXiv 2608.10825.
- **Not pursued:** a ZJU dataset available by email. Kyle said not to send it.

## 6. Experiment G.2 — per-cell vs min/max flagging of teardown-confirmed faulty packs (Beihang), 2026-10-15

**Data.** Beihang QAS: 58 faulty vs 335 normal EVs, 110 cells each. Faulty is a binary label from teardown by product
engineers.

**Features.**

- **A (per-cell drift):** for each cell, the OLS slope of its rest deviation from its siblings across blocks of the
  window. Each slope gets a robust z across the pack; A = −min z, the cell drifting down fastest relative to its
  siblings.
- **B (min/max drift):** minus the OLS slope of the block-median pack-minimum deviation. A scalar monitor could
  compute this.
- Each is computed in an early and a late window of each vehicle's record.
- The pre-registration has the exact block construction.

**Results (DERIVED):**

| | AUC (95 % CI) |
|---|---|
| A early | **0.59 (0.51–0.67)** |
| B early | 0.52 (0.44–0.60) |
| A − B early | **+0.07 (+0.01, +0.14)** |
| A late | 0.73 |
| B late | 0.57 |
| A − B late | +0.16 |

**Classification.** This falls in a gap in the pre-registered decision table: the edge is resolvable, but A is below
the 0.70 "SUPPORTED" bar. This is disclosed as deviation 1. Verdict: *per-cell beats min/max, modestly; not
deployable.*

**Confound.**

- Median temperature has AUC 0.74 (faulty 20 °C vs normal 17 °C), and faulty IDs are contiguous (335–392).
- So the result is flagged "cohort-distinguishable".
- A survives the adjusted logistic model: +0.30 (+0.04, +0.51). B does not.

**Mechanism hint.** The A-flagged cell is the modal min cell in only 28 % of faulty vehicles. So per-cell data sees
a cell drifting relative to its siblings *while not being the weakest*.

**DTI** (3 faulty out of 72 eligible vehicles): too few to read.

**Post-review (2026-10-15): substantially weakened.**

- **The cohorts were processed differently.** All 335 normal records carry current-sentinel frames, but only 17 of
  58 faulty ones do. Median maximum temperature is 41 vs 31 °C. Both were reproduced.
- **Stratified on these, the A − B edge is not significant** (p = 0.07–0.11).
- **The late gain is not drift:** shuffling the block order keeps it.
- **Early A − B is fragile to reasonable definition changes.**

What remains is a weak early per-cell signal (AUC ≈ 0.6) as a **hypothesis** for a matched, date-bearing follow-up.
The "drifting before weakest" mechanism claim is withdrawn.

## 7. Experiment H — per-cell charge-limit enforcement (Changan replay + board), 2026-10-14

**H-a (DERIVED; limits ASSUMED).**

- **Replay.** 286,832 charging sessions and 40.1 M frames.
- **Limit map.** `C = C_T(T) · taper(SOC)`. `C_T` is flat at 1.5 C between 25 and 40 °C. The taper runs from 1 at
  60 % SOC down to 0.05 at 100 %.
- **The three limiters compared:**
  - **per-cell:** the min over cells of each cell's own limit;
  - **min/max:** `min(C_T(Tmin), C_T(Tmax)) · taper(at Vmax)`;
  - **pack-mean:** with margins.

**H-a results.**

- **Verdict: NO BENEFIT over min/max.** Median saving 0.008 % (CI 0.004–0.011 %); M2 permutations agree.
- Per-cell ≠ min/max on 13.3 % of frames.
- Post-hoc, the cold or hot bands show a 0.7–3.3 % median saving, but **79 % of sessions sit in the 25–40 °C flat
  band**.
- **Against pack-mean:** pack-mean needs 30 mV / 10 °C margins for ≤ 0.1 % unsafe frames. At those margins, limiting
  from the extremes gives a median 34 % shorter charge time. At 50 mV / 5 °C the figure is 26 %.
- Min/max already carries the extremes. Pack-mean is a weak baseline: GB/T frames carry min/max *and* their
  indices.
- *Post-review:* `L_cell ≥ L_mm` by construction, and one shared map excludes per-cell R and capacity differences.
  A post-hoc per-cell-R limiter gains median +2.0 % admissible current at vmax ≥ 4.0 V.

**H-b (MEASURED, gated 20/20).** C limiter on A55 core 3 at 1.8 GHz.

| Cells | p50 |
|---|---|
| 96 | 1.50 µs |
| 1,000 | 14.75 µs |

- Linear at about 14.7 ns per cell (DERIVED from MEASURED).
- State is 10 B per cell plus 13.6 KB of lookup tables.
- At 100 Hz, 1,000 cells use about 0.3 % of one core (DERIVED).
- Timing resolution is 41.67 ns, a 24 MHz counter. Ingest cost, RT isolation and the M7/M33 cores were not
  measured.

## 8. Experiment H2 — H re-run on an LFP grid BESS (Weihai), 2026-10-15

**Why.** A different chemistry (LFP), 4× longer strings (396 cells), and a winter-inclusive record. That last one
was the hope for H's open cold-weather question.

**H2-a (DERIVED).**

- **Scope.** 1,929 rack charge sessions and 1.59 M 10 s frames.
- **Limit map.** H's `C_T`, times an LFP *voltage* taper: 1 at ≤ 3.40 V, 0.05 at 3.60 V, 0 at 3.65 V.
- **Verdict: NO BENEFIT**, median 0.00 %.
- **Why there is no benefit:**
  - The **container is climate-controlled.** The coldest probe sits at 20–28 °C (p5–p95), and no session has a
    median coldest probe below 10 °C. The cold question is **unanswerable**, not negative.
  - The median top cell is 3.377 V, below the taper knee.
  - The cell spread is 12 mV.
  - Per-cell ≠ min/max on only 1.95 % of frames.
- ~~Against pack-mean: needs 75 mV / 10 °C margins; extremes give 45–54 % shorter charge time.~~
  **Withdrawn post-review.** The result was driven by stale cell series in November 2024 (44,905 frames with any
  cell > 100 mV off the median, against ≤ 515 in every other month). Excluding those frames gives 30 mV / 10 °C
  and 33 %, the same as H. The primary verdict is unaffected.

**H2-b (MEASURED, gated 10/10)**, at real geometry: probe index ⌊k·P/N⌋ and `VLIM` = 3650.

| Cells | p50 |
|---|---|
| 396 | **5.83 µs** |
| 3,564 | **52.1 µs** |

- About 14.6 ns per cell (DERIVED), the same as H.
- At 100 Hz, the full cluster uses about 1.1 % of one core (DERIVED).

**Deviations.**

- 24 rack-sessions were empty.
- `VLIM` became a compile-time define, which was not pre-registered.
- Current came from the grid dAh.
- The timestamp decoder is our own.

---

## 9. Synthesis (revised after the review)

| Possible value of per-cell / per-unit data | Answer on public data | Could this data have shown it? | Strength |
|---|---|---|---|
| On-device *training* beats the fleet model (Study 1–2) | **No** | Yes on EVBattery; only above ≈ 3 Ah on Changan (derived labels) | Strong |
| Cheap per-unit *offset* (shrunken, bytes of state) | **Possibly yes**, at 0–5 k km (post-hoc, one band) | Partly | Candidate; needs pre-registered confirmation |
| Tighter capacity bound (E) | Unresolvable; ceiling about 1 % | No (label noise; white residual) | Informative bound |
| Detecting anomalies (F) | **Not tested.** The 98 % overlap was an identity; a per-cell-only detector finds cells min/max misses (post-hoc). | Partly | Open |
| Early warning of anomalies (F) | Untestable (3 positives) | No | — |
| Diagnosing fault type (F/G) | Plausible classes, no public ground truth | No | Weak; blocked |
| Flagging packs that fail at teardown (G.2) | Weak early per-cell signal (AUC ≈ 0.6); A > B does **not** survive cohort stratification | Partly (cohorts processed differently, no dates) | Hypothesis only |
| Shorter charging under per-cell limits (H, H2) | **No**, under uniform assumed maps | No: `L_cell ≥ L_mm` by construction; no cold or gradient regime | Strong only within the assumed maps |
| Shorter charging with per-cell R **learned from history** (X2, 2026-10-15) | **Cold: no**, because cold sessions are partial top-ups (median peak 3.95 V). **Top of charge with history: +5.5 %** median against an equally safe min/max (POST-HOC; CI 4.7–6.4 %). | Cold: no (sessions never reach headroom). Warm: yes, but already seen, so it needs new data to confirm. | Candidate, NC-SA only. The CC BY arm (X2-M2, McMaster at the SOURCED 6 C) gives **0.00 %**; the gain tracks how often headroom binds. |
| Locating a faulty cell before min/max and the BMS (X3, 2026-10-15) | Pre-registered rule **not supported** (2 of 3). Weeks to months ahead of min/max; mixed against BMS level 3 (+15 d / −8 d / never). | Partly (n = 3, labels not independent). **X3-b healthy control:** the rule raises 21.8 false episodes per 100 vehicle-days (Changan); the neighbour fix doubles it. | **Weak.** The lead is uninterpretable without a calibrated false-alarm budget. BatICM MIT, BATSS CC BY. |
| Board cost of per-cell processing | Trivial: 1.50 µs at 96 cells; 52.1 µs at 3,564 cells (MEASURED p50) | Yes | MEASURED (A55 user-space; MCU cores not measured) |

**The one-line story (revised).** These were the public field datasets we could use:

- a warm-climate NMC EV fleet with labels we derived ourselves;
- an HVAC-controlled LFP container;
- a teardown-labelled fleet whose cohorts were processed differently and carry no dates.

On these:

- **On-device training does not beat a frozen fleet model.** A bytes-of-state shrunken offset may.
- **Hand-built per-cell features did not beat min/max** for capacity bounds or charge limiting under uniform limit
  maps. The designs mostly could not have shown an effect.
- **Two per-cell signals remain open hypotheses:** drift against a cell's own baseline (Changan), and a weak
  teardown-failure signal (Beihang).
- **Cost:** every per-cell computation tested runs in microseconds on one A55 core and looks MCU-class. The
  application-processor case therefore has to rest on something these experiments did not test: data reduction,
  history storage, learned models, or fleet-model inference.

## 10. Known weaknesses

The review (`review_2026-10-15/REVIEW.md`) has the full list.

1. **Changan labels are ours.** About 3–4 % per-unit noise, built on an ASSUMED OCV table. The review found a
   segment-duration bias, with 6–24 h segments reading about +3.7 Ah high.
2. **The limit maps in H and H2 are generic and ASSUMED, and shared by every cell.** That makes `L_cell ≥ L_mm` by
   construction. The trajectory is held fixed, with no closed loop.
3. **G.2's cohorts were processed differently.** The 5 pre-registered controls missed sentinel frames, run counts and
   temperature range. There are no failure dates.
4. **F has three weaknesses:**
   - the −60 mV threshold was chosen after seeing counts;
   - the overlap metric was an identity;
   - "SOC-like" depends on an ASSUMED table.
5. **Board measurements:**
   - user-space Linux, not RT-isolated (spikes 57–724 µs);
   - 41.67 ns timer resolution;
   - no ingest cost, no MCU cores, no energy measurement.
6. **H2 needs a staleness screen.** The extractor's "has logged" guard admits series that went stale for hours.
7. **Cold and gradient regimes are untested** for H/H2. Neither McMaster nor BATSS has one; the review's McMaster
   "28 °C gradient" was two dead sensors. Only Changan has cold charging, in 2,855 sessions.
8. **No closed-loop or hardware-in-the-loop test** of any limiter or monitor.

## 11. Where things are

| What | Where |
|---|---|
| Independent review | `results/review_2026-10-15/` (REVIEW.md + six reviewer reports + scripts) |
| Write-ups | `results/results.md`, `results/results_large.md`, `results/dataset_profile.md`, `results/{E,F,G,G2,H,H2}/` |
| Pre-registrations | `results/*/*_preregistration.md`; E's is `E_power_analysis.md` |
| Briefs | `Experiment E Brief.md`, `Experiment G and H Brief.md` (repo root) |
| Analysis code | `analysis/`, e.g. `E_precheck.py`, `F_faults.py`, `G2_beihang.py`, `H_replay.py`, `H2_replay.py`, `mcos_dt.py` |
| Board code | `board/`: `h_limiter.c`, `h_ref.py`, `h2_ref.py`, `census.py`, plus Study-1 scripts |
| Model code | `model/` |
| Raw data | `data/raw/` and `data/changan`, `data/weihai` (gitignored, not public) |
