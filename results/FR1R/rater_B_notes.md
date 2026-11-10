# FR1-R rater B notes

Rater B, branch `fr1r-rater-b`, order `orders.B` (`default_rng(12)`). Every rating is **DERIVED-judgemental**. Source:
NHTSA Part 573 reports, chronologies and ODI résumés (US Government works, public domain). No dollar figure appears.

## 1. Conventions (written and committed before any document was fetched)

These say how I apply pre-registration §3. They are fixed now and are not revised after the first fetch; any case
where one is hard to apply is noted in §3 (per-case remarks), not by changing the rule.

### 1.1 Item 3: the question I answer

*If the investigator had only data recorded on the vehicle before the event, how long a span, ending at the event,
would have been needed to identify this cause?*

- "Identify this cause" means: distinguish the recalled root cause from other plausible causes of the same symptom,
  to the level the Part 573 states it (e.g. "contactor welds under high inrush current", not "a contactor failed").
- "Data recorded on the vehicle" means any signal an ECU on that vehicle could plausibly log (DTCs, freeze-frames,
  voltages, currents, temperatures, CAN messages, state-machine states, software version). It does not include
  teardown, metallurgy, supplier process records, build records, or design review.
- I rate the *minimum* span that would have sufficed, not the span the manufacturer actually used.

### 1.2 The six states

| State | I write | I use it when |
|---|---|---|
| 0 | `not observable` | The cause is a physical property of a part or of the build that no in-vehicle signal distinguishes from other causes at any window: wrong / out-of-spec / contaminated / mis-sourced part; supplier process escape; assembly error (missing or under-torqued fastener, mis-routed or pinched harness, missing clip, wrong part fitted); a design weakness found by analysis or test (insufficient strength, insufficient clearance, wrong material); a labelling or documentation error. The field record could at most show that and when an event occurred. **All mechanical body / chassis / restraint defects** (welds, latches, seat structures, belts, inflator chemistry, suspension parts, wheel studs) default here unless the document names an in-vehicle signal that shows the cause. |
| 1 | `<=1 s` | A DTC plus its freeze-frame, or a single snapshot of state at the trip, is enough. Typical: software that sets a wrong state or wrong DTC response that is visible in the logged state / DTC itself; a sensor reading out of range at the moment of the fault; a missing or wrong software parameter shown by the software version; a fault reaction that is the defect (e.g. the software shut down the drive on a single-sample diagnostic). |
| 2 | `(1,40] s` | The cause shows only in the seconds before the event: a transient sequence (inrush, voltage dip and recovery, switching sequence, fast thermal spike, a short sequence of CAN messages or state changes, a timing race between ECUs within one drive event). |
| 3 | `(40,80] s` | About a minute of history is needed: a slower thermal rise to trip, a precharge / charge-start sequence lasting tens of seconds, a ramp over about a minute. Used only when the document's description points to roughly a minute; by the tie rule an unspecified "short" sequence goes to state 2. |
| 4 | `(80,700] s` | Minutes: a charge session phase, sustained high-load operation over minutes, coolant-loss heating over minutes, a several-minute derate sequence. |
| 5 | `>700 s` | A full session or more: many charge / drive cycles, accumulated degradation (thermal cycling fatigue, insulation ageing, contact wear, moisture ingress over days), cell imbalance growth, counters that grow over weeks or months, long parked periods. |
| — | `cannot judge` | Only when the documents are too thin to map (no usable cause text at all, or no Part 573 report could be fetched). Never used for "the cause is a part defect" (that is state 0). |

**State 0 vs. states 1–5 for electrical defects.** Many power-electronics recalls name a defective part (e.g. a
transistor, capacitor, contactor, solder joint) *and* a mechanism that unfolds electrically (overcurrent, thermal
stress, degradation). My rule:
- If the document identifies the cause as the part or its manufacturing (a supplier process escape, contamination,
  wrong part, insufficient design margin found by teardown or analysis) and the in-vehicle electrical record would
  only show *that a failure happened* (the DTC / shutdown) but not *why*, I rate **0**.
- If the document states an electrical, thermal or software mechanism such that a recorded signal history (current,
  voltage, temperature, state sequence) would distinguish this cause from other causes, I rate the window that
  history would need (1–5). The mechanism must be one the stated cause hinges on, not just a symptom.
- Where the documents say the defect is a *degradation* that progresses with use (fatigue, wear, ageing) and the
  progression would show in logged signals (rising resistance, rising temperature, growing imbalance), I rate **5**.
  Where the same degradation is said to be invisible until failure, I rate **0**.

**Software / calibration defects** are rated by what the logged data would need to show for the software defect to
be recognised: usually the DTC / state / software version at the event (state 1), or the sequence of inputs leading
up to the misbehaviour (state 2 or more). A software defect is never state 0 unless the record could not show its
effect (e.g. a wrong label / display text that no log captures).

**Tie rule.** When the documents leave the window between two adjacent states, I take the **lower** state, unless a
document states a time scale (e.g. "after several minutes of operation", "over multiple charge cycles"), in which case
I follow the stated scale.

### 1.3 Item 3b: rate class (states 2–5 only; `n/a` for 0, 1 and `cannot judge`)

The class is that of the **fastest** signal I name in `signals`.

| Class (write exactly) | Typical signals I put there |
|---|---|
| `<=10 Hz` | temperatures (coolant, module, cell, junction estimate), state of charge, cell voltages via BMS polling, insulation resistance, odometer / counters, software state, charge-session parameters, slow CAN status messages, 12 V battery voltage trend |
| `10 Hz-1 kHz` | CAN-rate signals: pack voltage / current as broadcast, motor speed / torque command, pedal and gear, contactor command / feedback, precharge voltage ramp, DC-DC output voltage and current, 12 V bus dips, fast diagnostic flags |
| `>=1 kHz` | phase currents, gate-drive signals, DC-link voltage ripple and transients, switch-node voltage, inrush / surge current, arc or short events, desaturation detection, resolver signals, any waveform-level capture |

If the mechanism is an electrical transient on the HV / power path (short, overcurrent spike, inrush, voltage
overshoot, gate fault), I name the waveform signal and class it `>=1 kHz`. If it is a control-logic or communication
sequence, `10 Hz-1 kHz`. If thermal or ageing, `<=10 Hz` unless a faster signal is also needed.

### 1.4 Items 1, 2 and 4

- **Item 1, cause type.** `transient electrical` (over-current, over-voltage, short, arcing as the mechanism),
  `thermal` (thermal cycling, overheating / thermal overload as the mechanism), `manufacturing or component defect`
  (the root cause is a part or build escape, contamination, wrong part, assembly error, or a design weakness of a
  physical part), `software or calibration` (the root cause is code or a parameter), `unknown / mixed` (no root cause
  identified, or two of the above given equal weight). When the documents name a physical part defect that *leads
  to* a short or overheating, I code the root cause (`manufacturing or component defect`), since item 1 asks for the
  cause; the mechanism goes into item 3 and the signals. Base-rate mechanical defects are coded on the same list
  (mostly `manufacturing or component defect`).
- **Item 2, evidence.** As stated or clearly implied: `DTC freeze-frame` (diagnostic data / logs / vehicle data
  identified it), `bench reproduction` (lab test or reproduction), `fleet statistics` (field-report / warranty trend
  analysis was the deciding evidence), `waveform or high-rate capture`, `teardown only` (inspection / analysis of
  returned parts), `not stated`. If several are stated I take the one the chronology presents as identifying the
  root cause; if that is unclear, the one closest to the root cause (teardown or bench over fleet statistics).
- **Item 4, confidence.** `high` when the cause and its observability are explicit; `medium` when I had to infer the
  mechanism or the state boundary; `low` when the documents are thin or the state choice could reasonably be two
  steps off.

### 1.5 Item 5 flags (each `yes` or blank)

- `flag_no_cause`: `yes` when none of the documents states any cause beyond the symptom (e.g. "the part may fail").
  A stated root cause, even brief, means blank. When I set this, item 3 is normally `cannot judge`.
- `flag_software_only` (PE only): `yes` when the defect is purely a software / calibration error and the recall
  involves no electrical event in the power electronics (e.g. a display, a warning-logic or a range-estimate error
  with no fault in the HV circuit). A software defect that causes or fails to prevent an electrical event (contactor
  opening, inverter shutdown, overcharge) is blank.
- `flag_out_of_scope` (PE only): `yes` when the defective part is not an OBC, DC-DC converter, inverter / motor
  controller or HV BMS / contactor / junction unit (e.g. a cell / module defect alone, a cabin water pump, a signal
  connector, a bracket, a charging cable outside the OBC, a VCU not in these groups). Software in a BMS / inverter /
  OBC / DC-DC is in scope.
- BR cases: the PE-only flags are left blank.

### 1.6 Mechanics

- `docs_sha256`: the SHA-256 of every document I fetched and read for the case, `;`-separated. `docs_missing`: URLs
  that could not be fetched, `;`-separated.
- If no Part 573 report (`RCLRPT`) is fetched for a case, the rating is `cannot judge` (pre-registration §2).
- Signals and notes are free text without commas where possible; the CSV is written with proper quoting.
- Each row is appended immediately after the case is rated, in order; commits after every 25 cases.

## 2. Problems, hash mismatches and unfetchable URLs

(Written after rating. Sections 2 and 3 were added after the conventions commit; section 1 is unchanged.)

**Fetch.** 364 of 364 URLs in `FR1R_documents.json` fetched with a plain GET (User-Agent
`FR1R-rater-B research fetch (public NHTSA documents)`, 60 s timeout, 0.5 s pacing), on 2026-11-10. Every
response was a PDF. **Hash mismatches: 0.** Every fetched SHA-256 equals `sha256_A` or `sha256_B` (whichever is
non-null). **Unfetchable URLs: 0**, so `docs_missing` is empty for every case. Record: `rater_B_fetch.json`.

**Text extraction.** `pdftotext -layout` on every file. Two attachments returned no usable text. Both look like
image-only PDFs. Nothing was OCR'd: rating used only the extracted text.
- `PE026__RMISC-23V657-1502.pdf`: the chronology attachment for 23V-657.
- `PE042__RMISC-24V560-1690.pdf`: the chronology attachment for 24V-560.

Both cases were rated from their Part 573 reports. For neither did the cause depend on the missing chronology.

**Reading method.** For each case, a script (`show.py`, in the scripts directory) printed the extracted text of
every fetched document in turn.
- A line identical to one already printed for the same case was suppressed, with a count of the lines suppressed.
  Lines of 25 characters or fewer were always shown.
- Amended Part 573 reports mostly repeat the original, so the reduced text covers every distinct line.
- For long cases, repeated vehicle-list boilerplate was also filtered from the display (Body Style, Power Train,
  VIN ranges and similar). The defect, cause, chronology and remedy text was always read in full.

**Mechanics.**
- Each row was appended immediately after the case was rated, by a script (`add.py`) that checks every closed-list
  value and the rating order.
- Commits came after cases 26, 51, 76, 100 and 125, then the final commit. They are one or two cases off the exact
  multiples of 25 because I committed at the first pause after each 25-case mark.
- `git add` needed `--sparse` because `results/FR1R/` new files sit outside the sparse-checkout patterns. This adds
  files to the index only. It does not change the sparse-checkout definition. No other git operation was used.
- No document was opened that is not in `FR1R_documents.json`. No other source and no memory of these recalls was
  used.

**Totals (all DERIVED-judgemental).**
- Item 3, all 150 cases: `not observable` 96, `<=1 s` 15, `(1,40] s` 15, `(40,80] s` 1, `(80,700] s` 3,
  `>700 s` 18, `cannot judge` 2.
- Item 3, PE cases only: `not observable` 25, `<=1 s` 12, `(1,40] s` 15, `(40,80] s` 1, `(80,700] s` 3, `>700 s` 18,
  `cannot judge` 1.
- `cannot judge`: 2 (PE021, BR057). Both also carry `flag_no_cause`.
- `flag_software_only` (4): PE014, PE023, PE031, PE071.
- `flag_out_of_scope` (17): PE004, PE028, PE039, PE041, PE044, PE046, PE051, PE053, PE056, PE057, PE062, PE063,
  PE064, PE066, PE069, PE070, PE076.

## 3. Per-case remarks

Applying the conventions:
- **Evidence when the cause came from supplier or plant records.** When the documents say only that the cause was
  found by a supplier notification, a process review or a records audit, item 2 is `not stated`; none of the closed
  values fits. When they describe inspecting parts, it is `teardown only`. When they describe testing, it is
  `bench reproduction`.
- **Cause field `NR` but the cause stated elsewhere.** Several reports leave the "Description of the Cause" field
  `NR` but state the cause in the defect description or the chronology. That counts as a stated cause, so
  `flag_no_cause` is blank. Examples: BR004, BR006, BR007, BR015, BR023, BR030, BR042, BR043, BR045, BR064, PE001,
  PE026, PE037, PE042, PE048.
- **Defects in cells or modules.** These carry `flag_out_of_scope`: cell robustness, lithium deposits, self-discharge
  and the module J-bar busbar. Where the documents name an in-vehicle signal that shows the defect progressing, I
  rated the window `>700 s` and `<=10 Hz`: the BMS self-discharge or SOC-fluctuation detection and the module
  voltage/temperature signature. That applies to PE004, PE046, PE062, PE063, PE064, PE070 and PE076. Where no such
  signal is named, I rated `not observable`: PE053 and PE069.
- **Contactor overheating campaigns (Ford Mach-E).** PE015, PE027 and PE060 cover cumulative contactor heat damage,
  so `>700 s`. PE055 is a different cause: the earlier remedy software was not actually installed. A snapshot of the
  installed software identifies it, so `<=1 s`. The underlying contactor mechanism is unchanged.
- **PE069.** The cause field restates the 25V-050 cell-robustness cause, so it is rated like PE053. Its
  supplemental chronology adds that these vehicles missed the correct BMS update.
- **PE052.** The 12 V voltage fluctuations damaged the DC-DC phase during an earlier software-update session. The
  window ending at the later loss of propulsion therefore reaches back to that session (`>700 s`). Confidence is low:
  if the damage itself is taken as the event, the window would be seconds.
- **PE026.** The momentary slip-ring short is captured in a sub-second high-rate record at the trip. I rated
  `<=1 s`, which has no rate class under the scheme; the high rate is noted in `signals`.
- **PE022.** The only case with `waveform or high-rate capture` evidence: the double-dip contactor-closing current
  signature. The documents state a rolling 100-closing screening window, so `>700 s` and `>=1 kHz`.
- **Stated time scales.**
  - PE014: "twice in one minute", so `(40,80] s`.
  - PE031: excessive key cycles through the day, so `>700 s`.
  - PE033 and PE049: damage "over time", so `>700 s`. The related Hyundai ICCU cases, PE034 and PE050, state no
    time scale. Their mechanism is end-of-charge voltage peaks plus thermal loading, which I rated `(80,700] s` at
    `>=1 kHz`.
  - PE061: shutdown 15-20 s after the warning, so `(1,40] s`.
- **The two `cannot judge` cases.**
  - PE021: no cause in any amendment or the chronology; the remedy is repurchase.
  - BR057: a pass-through whose chronology refers to FCA's 24V-129, which is not in the document set. The cause is
    `NR`, and the defect text is only the symptom.
- **Chronology attachments not in the document set.** BR047 and BR057 refer to separate chronology attachments that
  are not in the document set. BR047 was still rated from its defect text.
- **PE047.** The incorrect motor-controller software is identified by its version, so `<=1 s` with low confidence.
  The mechanism ("certain circumstances") is not described.
- **Software-only flag.** I set it only where the software fault causes no electrical event in the power
  electronics:
  - PE071: SoC misread from CAN ID conflicts.
  - PE014: charge relay latched off by firmware.
  - PE023: BMS warning failure.
  - PE031: counter-triggered shutdown.

  Inverter, BMS or contactor shutdowns caused by software were left unflagged, following §1.5.
