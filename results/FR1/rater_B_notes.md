# FR1 rater B: conventions (written before any rating document was opened)

**Rater:** B. **Written:** 2026-11-05, on branch `fr1-rater-b` cut from `main` at `51d2a78`, **before** any Part 573
report, chronology or ODI résumé was fetched or opened. Every rating that follows is **DERIVED-judgemental**.
Source of all rated records: NHTSA (US Government work, public domain).

## Disclosure (pre-registration §8, D-2 and D-3)

- Rater B is a language-model session. It was run as a **fresh-context sub-agent launched from the rater A session**,
  working in a **separate clone that contains only `main`** (no `fr1-rater-a` ref was ever fetched into it), with no
  access to rater A's branch, ratings, notes or document cache. It did not read any file named `rater_A*` or
  `ratings_A*`, nor any part of `briefs/FR1/README.md` beyond the APPROVED box and the brief body.
- Rater A and rater B are the same underlying model family reading the same documents. Agreement between them measures
  the reproducibility of the judgement, not its independence from a shared model prior (D-3).
- Being launched from the rater A session is itself a disclosed departure from the "started by the reviewer" wording
  in pre-registration §4.2 / D-2; the blindness was enforced by a separate clone and a separate context, not by a
  separate human operator.

## Order

The 150 cases are listed as PE001–PE005, PE007–PE076 (75, D-1) followed by BR001–BR075, and rated in the order
`numpy.random.default_rng(2).permutation(150)` over that list (`analysis/FR1_rater_B_fetch.py` records it). `order`
in `ratings_B.csv` is the 1-based position in that permutation.

## Documents (pre-registration §4.1)

- For every case: the latest Part 573 Safety Recall Report published by NHTSA for the campaign (the amended report
  when there is one; earlier versions are also read when the latest omits the chronology), which on current NHTSA
  reports includes the chronology section. A separate chronology attachment is used when NHTSA publishes one.
- The ODI opening and closing résumés **only** when the campaign is "Initiated by: ODI" or its Part 573 cites an
  investigation number.
- Nothing else: no TSBs, owner or dealer letters, press, papers or recollection of a case. The campaign summary text
  that the NHTSA API returns with the document listing is not used as a rating source when it differs from the Part
  573 itself.
- If no Part 573 can be fetched or opened, item 3 is *cannot judge* and the note says why.

## Item 1, cause type (one value)

- **transient electrical:** the stated mechanism is an over-current, over-voltage, short circuit, arc or inrush event
  (including one triggered by a component weakness, if the document puts the electrical event at the centre of the
  failure mechanism).
- **thermal cycling or thermal overload:** the stated mechanism is heat: overheating under load, insufficient cooling,
  fatigue from thermal cycling, thermal runaway initiated by heat.
- **manufacturing or component defect:** a part is out of specification, mis-assembled, contaminated, damaged in
  production, under-designed or wrongly specified, and the document stops at that (no electrical or thermal mechanism
  stated as the cause). Design defects of a part go here unless they are software.
- **software or calibration:** the defect is in code, parameters or calibration data, and the remedy is a software
  change.
- **unknown / mixed:** the document states two or more of the above as joint causes with no primary one, or says the
  root cause is not determined.

## Item 2, evidence (one value: the evidence the documents present as having identified the cause)

- **DTC freeze-frame:** the cause was identified from diagnostic trouble codes or stored fault data from the vehicle.
- **bench reproduction:** the cause was confirmed by reproducing the failure on a bench, rig, test vehicle or in a
  simulation / software test.
- **fleet statistics:** the cause was identified from warranty, field-report or telematics trends across vehicles.
- **waveform or high-rate capture:** the cause was identified from recorded high-rate electrical signals.
- **teardown only:** the cause was identified from inspection or analysis of returned or production parts, with no
  reproduction stated.
- **not stated:** the documents give no basis.
When several are named, the one the chronology presents as decisive (usually the last step before the root-cause
statement) is chosen, and the others are mentioned in the note.

## Item 3, window: how a documented cause is mapped onto the five categories

The question is: **if the investigator had only field data recorded on the vehicle before the event, how long a
pre-event span (of the signals named, at the rate named) would have been needed to identify this cause?** The window is
judged by length; the data rate goes in the free text.

- **≤ 1 s:** a snapshot suffices, i.e. a DTC with its freeze-frame (state, temperatures, voltages at the fault), or the
  cause is a static property of the part, the configuration or the code that pre-event field data cannot reveal at any
  window length (teardown, inspection or code review identifies it; the field record only locates the event). A
  longer window adds nothing here, so the minimum window is the smallest category. This is the rule for most pure
  manufacturing / mechanical defects, including most base-rate cases.
- **(1, 40] s:** the mechanism needs the sequence of seconds before the event: a driving or charging transition, a
  contactor/precharge sequence, a regen or torque event, a software state machine running through several steps, or an
  electrical transient whose trigger lies in operating conditions a few seconds earlier.
- **(40, 80] s:** about one minute of history is needed, e.g. a short thermal ramp under sustained high load, or a
  repeated event pattern over tens of seconds.
- **(80, 700] s:** minutes are needed: heating over a sustained drive or charge phase of a few minutes, a slow
  sequence of charging-state changes, or conditions that accumulate over a few-minute episode.
- **> 700 s:** the cause shows only over a charge session, a long drive, many cycles or months (thermal cycling
  fatigue, end-of-charge behaviour after a full session, degradation trends). The free text says when the needed rate
  is low (≤ 10 Hz telemetry) so that the reader can see this is a long, slow window rather than a long MB/s window.
- ***cannot judge*:** only when a rating document cannot be fetched or opened, or when it is opened but gives no
  description of the failure that could be mapped at all.

Ties between two adjacent categories go to the **lower** one unless the document states a time scale that needs the
higher one. Base-rate cases are judged the same way for their body, chassis or restraint defect (item 3 asks the same
question).

Signals and rate (free text): the signals that would have to be retained (e.g. DC-link voltage, phase currents,
contactor command and feedback, cell voltages, coolant temperature, CAN state) and an order-of-magnitude sample rate.

## Item 4, confidence

- **high:** the document states the mechanism and the conditions that trigger it.
- **medium:** the mechanism is stated but the trigger conditions or time scale have to be inferred.
- **low:** the document is thin, ambiguous or self-contradictory, or the mapping rests mostly on judgement.

## Item 5, flags (yes / no; for BR cases only *no cause stated* is set, the other two are `NA`)

- **no cause stated:** the documents describe a symptom or a risk but give no cause (no statement of what is defective
  or why), or say the cause is unknown.
- **software-only, no electrical event:** the stated cause is software or calibration **and** the failure as described
  involves no abnormal electrical event in hardware (no over-current, over-voltage, short, arc or overheating of a
  power part); e.g. software that commands a loss of drive power, displays a wrong value or fails to warn. If the
  software lets a hardware electrical or thermal event happen, the flag is **no**.
- **component out of scope:** the part that is defective, as stated in the documents, is not an on-board charger /
  charging control unit, a DC-DC converter, a traction inverter / motor controller (incl. PCU/EPCU) or an HV
  battery-management / contactor / junction / fuse unit. Cells and modules alone, cables, connectors, pumps, brackets,
  12 V batteries, vehicle control units and other parts are out of scope. Software in an in-scope controller counts as
  in scope (the software-only flag handles it).

## Files

- `results/FR1/rater_B_documents.json`: one entry per document fetched (case, URL, local file name, bytes, SHA-256,
  fetch time). The documents themselves are kept under the gitignored `data/raw/nhtsa/fr1_docs_B/` and are not
  committed.
- `results/FR1/ratings_B.csv`: one row per case, columns as in `NEXT_TASK.md` step 5.
- `analysis/FR1_rater_B_fetch.py`: the order and the fetcher.
