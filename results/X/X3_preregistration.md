# Experiment X3 (G.3) — pre-registration: lead time of per-cell drift on located faults (BATSS + BatICM)

**What X3 asks.** On packs where the faulty cell is known or claimed, does **drift relative to sibling cells** (G.2's
feature A, computed causally over days of history):

1. single out the faulty cell?
2. do so before a min/max monitor?
3. do so before the BMS's own warning?

**Origin.** Kyle's brief §5 X3 ([`README.md`](README.md)). **Running X3 needs Kyle's go-ahead.** Any contact with
the BATSS authors is Kyle's decision; the draft is in a draft (not sent; not included in the public mirror).

**Design.** This is a **case study**: n = 4 faulty packs plus 1 healthy pack. **No p-values**; the outcome is
descriptive by design. The file is committed before any X3 analysis code exists.

**Tags.** Times and deviations are DERIVED from released telemetry. Fault identities are SOURCED from the papers, or
are a stated prediction for BATSS.

## 0. What has already been seen (disclosure; it biases toward success, so it is listed in full)

**BatICM** (G.1b inspection, 2026-10-14, `results/G/G_dataset_search_extended.md` §"BatICM inspection"):

- The most-deviant column over each file's **last 10 %** was V_82 (car2; the paper says cell #83), and V_81 and V_2
  (car3; the paper says #82 and #3).
- So the faulty cells are visibly deviant late in the record. That is not a lead-time result, but it is seen.

**BatICM warning column** (2026-10-15, while drafting):

- Levels 1–2 appear from the first day in cars 2–4.
- First level-3 dates: car2 2019-05-10; car3 2019-04-20; car4 2019-07-09 (the last record day).

**BATSS ISC run** (review probe, `review_2026-10-15/scripts/big/batss_isc_probe.out`):

- Over the 10 h rest, cells 2 and 8 end −25.2 and −21.2 mV from the pack.
- Cell 8 drifts fastest relative to siblings (−1.00 mV/h, against −0.73 for cell 2). Cell 2 is the min cell at every
  step.
- **Prediction on record, formed after that inspection:** the injected-ISC cell is **cell 8**. If the authors confirm
  cell 2 instead, the prediction is wrong and that will be reported.

**Index convention.** BatICM column V_n against the paper's cell #n differs by one in the G.1b inspection (V_82 vs
#83). The **primary analysis uses the paper's numbering mapped as V_(n−1)**. The alternative (V_n) is reported
alongside. This is fixed now, before any lead-time computation.

## 1. Cases

| Case | Pack | Fault (source) | Faulty cell(s) | Reference event |
|---|---|---|---|---|
| BatICM car2 | 88 cells, 30 s, Apr–Aug 2019 | ISC → thermal runaway (paper) | #83 | First level-3 BMS warning; end of record |
| BatICM car3 | 87 cells, 10 s, ~4 weeks | Self-discharge → thermal runaway (paper) | #3, #82 | Same |
| BatICM car4 | 87 cells, 30 s, ~3 months | Resistance rise (paper) | #64 | Same |
| BatICM car1 | 96 cells, 1 s, 1.6 days | Healthy (paper) | — | False-alarm control only |
| BATSS ISC | 10s2p, 1 Hz, 17.5 h | Injected ISC, a balancing resistor held on (metadata) | Unknown in release; **predicted cell 8** | Start of the resistor-on period if the step log or metadata identifies it; otherwise start of record, disclosed |

**Licences:** BatICM is MIT; BATSS is CC BY 4.0.

## 2. Monitors (definitions fixed here)

All three per-cell features use **rest frames only**, |I| < 0.05 C. Each is evaluated at the end of every calendar
day (BatICM) or every hour (BATSS), using only data up to that point.

**Per-cell drift (A, the G.2 feature):**

- Over the trailing window (BatICM 7 days; BATSS 3 h), take each cell's rest deviation from the pack median.
- Fit an OLS slope per cell, then a robust z of the slopes across the pack.
- **Flag** a cell when z ≤ −3.5 on 2 consecutive evaluations.
- The 3.5 threshold is CHOSEN now; it is the usual robust-z outlier convention.

**Min/max monitor (B):**

- Daily (or hourly) median of (vmin − pack median) at rest.
- **Flag** when it falls below −60 mV (F's threshold, unchanged) on 2 consecutive evaluations.
- Also report the vehicle's own BMS `BMSCellVoltageMin` column where present.

**Per-cell level (A_lvl):**

- Robust z of each cell's median rest deviation over the trailing window.
- Same threshold rule as A.
- Reported secondary.

## 3. Outcomes (descriptive)

For each faulty case:

1. **Identification.** Does A's first flag point at the faulty cell, under the primary or the alternative index
   convention?
2. **Lead time.**
   - A's first correct flag against B's first flag, the first level-3 warning, and end of record, in days (hours for
     BATSS).
   - Negative values mean A was later.
3. **False alarms.** The number of A flags on non-faulty cells:
   - in each faulty car before the first correct flag;
   - over the whole of car1.

**Expected-value framing.** Value = p(event) × value(lead time).

- The **cost per field event must come from an OEM**. None is assumed here.
- X3 reports lead time and false-alarm counts only.
- Any value number added later will be tagged SOURCED, with its source, and kept separate.

## 4. Reading the result (fixed now)

| Pattern | Reading |
|---|---|
| A identifies the faulty cell in ≥ 3 of 4 faulty cases, leads B and level-3 in ≥ 3 of 4, with ≤ 2 false alarms in car1 | **Consistent with a per-cell history lead.** A case study at n = 4: worth a pre-registered test on larger data, nothing more. |
| A identifies but does not lead | **Per-cell localisation without lead time** |
| A fails to identify in ≥ 2 of 4 | **Not supported on these cases** |

BATSS counts as identified only if the authors confirm the cell. Until then it is reported as "prediction pending".

## 5. Deviations policy

Any change after this commit is a numbered deviation in the results, with its reason. No threshold changes after
results are seen.
