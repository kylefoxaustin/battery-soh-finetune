# FR1-R rater A notes

Rater A of FR1-R, a fresh-context sub-agent. Branch `fr1r-rater-a`. Rating by `results/FR1R/FR1R_preregistration.md`.
Every rating is **DERIVED-judgemental**. Source documents: NHTSA Part 573 reports, recall-file attachments and ODI
résumés (US Government works, public domain). No dollar figure appears in this file.

## 1. Conventions (written and committed before any document was fetched)

### 1.1 The question, as I apply it

> If the investigator had only data recorded on the vehicle before the event, how long a span, ending at the event,
> would have been needed to identify this cause?

- "Identify this cause" means: to tell, from in-vehicle data alone, the cause **at the level the documents state it**
  (the mechanism, not merely "component X failed"). Data that would only show *that* the event happened, or *which*
  component failed, locates the event; it does not identify the cause.
- "Data recorded on the vehicle" means any signal an ECU on that vehicle could plausibly sample: DTCs and freeze
  frames, CAN signals, BMS cell voltages and temperatures, pack/DC-link voltage and current, phase currents, contactor
  and precharge states, gate-driver fault lines, coolant temperatures and flows, wheel speeds, accelerations, seat and
  buckle switch states, crash-sensor data. It does **not** include dimensions, materials, torque values, weld quality,
  part numbers or supplier lot data.
- I rate the window the documented cause **would need**, not the window the manufacturer actually used.

### 1.2 The six states

| State | I write | I use it when |
|---|---|---|
| 0 | `not observable` | The cause, as stated, is a physical property of a part or of its assembly or design: a wrong, missing, out-of-tolerance or contaminated part; a weld, crimp, solder, torque, routing or fitting error; a material, supplier-process or design-margin weakness found by teardown, inspection, test or analysis; a labelling or documentation error. In-vehicle signals could at most show the consequence (a fault, a loss of isolation, an open circuit) and locate the component, but no signal at any window would tell the stated cause apart from other causes of the same consequence. **Almost every base-rate (body, chassis, restraint) case is expected here.** |
| 1 | `<=1 s` | A snapshot at the trip identifies the cause: the DTC set at the event plus its freeze frame (one sample of the operating state) is enough. Typical: a software or calibration error that misbehaves in one identifiable operating state (a threshold or a mode check wrong; a fault reaction that is wrong for the DTC set); a sensor reading that is wrong at the instant of the event; a parameter mis-set that the DTC and state at the trip reveal. |
| 2 | `(1,40] s` | Seconds before the event are needed: a sequence rather than a snapshot. Typical: an over-current or over-voltage transient building over a switching or load event; a precharge, contactor-close or contactor-open sequence; a CAN-message timing or loss sequence; a torque or speed oscillation; a software state-machine sequence across a few seconds (e.g. a drive-mode transition, a regenerative-braking event, a key-on/key-off sequence). |
| 3 | `(40,80] s` | About a minute: a charging-session start-up handshake, a sustained high-load event of tens of seconds to a minute, a slow voltage sag or rise over about a minute. |
| 4 | `(80,700] s` | Minutes: a thermal rise within one drive or one charging stage; coolant loss or a cooling-flow fault building over minutes; a sustained-load derating sequence; a charge session's power profile. |
| 5 | `>700 s` | A full session or more: many charge or drive cycles, days or months. Typical: cumulative degradation (cell imbalance growing, capacitor or semiconductor wear-out, solder fatigue from thermal cycling) where the identifying signature is a trend across sessions; 12 V drain over days; a slow leak or ingress that changes a reading over weeks. |
| — | `cannot judge` | Only when the documents are too thin to map: no Part 573 report could be fetched, the extracted text is unreadable, or no cause is stated at all and nothing allows a mapping. **Never** used for a stated cause that no signal would show (that is state 0). |

- **Tie rule.** When a case sits between two states, I take the **lower** state, unless a document states a time
  scale (e.g. "after approximately 10 minutes of", "over several charge cycles"); then I use the state that time scale
  falls in.
- **Partly observable causes.** When a defect has a physical root (state 0) but the documents name an in-vehicle
  operating condition that, together with a signal, would identify the mechanism (e.g. a software protection gap
  that lets a stated over-current through a transistor), I rate the window of the operating condition and signal that
  identifies the mechanism the document states as the cause. When the document's cause is the physical part property
  itself, I rate 0 even if the failure leaves an electrical signature.
- **Software causes** are rated by the window needed to see the triggering condition; a software cause is state 0 only
  when it has no in-vehicle manifestation that identifies it (e.g. a wrong text string), which I expect to be rare.
- **Base-rate cases** are asked the same question about the body, chassis or restraint defect. A restraint-control
  software error (e.g. a deployment or occupant-classification logic error) can take state 1–2; mechanical defects
  take state 0.

### 1.3 Rate class (item 3b)

- `n/a` for state 0, state 1 and `cannot judge`.
- For states 2–5, the class of the **fastest** signal I name in `signals`:

| Class (written exactly) | Typical signals |
|---|---|
| `<=10 Hz` | temperatures (cell, coolant, module, power-stage), SOC, cell voltages at a BMS reporting rate, isolation resistance, 12 V battery voltage trend, vehicle state and mode flags, odometer and charge-session records |
| `10 Hz-1 kHz` | CAN-level pack/DC-link voltage and current, motor speed and torque commands, contactor and precharge state transitions at ms resolution, pedal and brake signals, CAN message timing, accelerations at control-loop rates, wheel speeds |
| `>=1 kHz` | phase currents and switching transients, gate-driver fault lines and desaturation events, DC-link voltage spikes and ripple, arcing or short-circuit current waveforms, over-voltage transients on HV or LV rails, crash-pulse acceleration |

- When the needed signals span classes, the fastest decides.
- Signals stay in free text in `signals`. For state 0 I write `none (locates only: …)` with what a record could locate.

### 1.4 Items 1, 2 and 4

- **Item 1, cause type** (exact strings): `transient electrical` (over-current, over-voltage, short), `thermal`
  (thermal cycling, thermal overload), `manufacturing or component defect`, `software or calibration`,
  `unknown / mixed`.
  - A design or material weakness and a supplier or assembly error both go to `manufacturing or component defect`.
  - A short or over-current that the documents trace to a part defect (e.g. debris, an insulation flaw) goes to
    `manufacturing or component defect`; `transient electrical` is for an electrical event that is itself the stated
    cause (e.g. an over-current during a stated operating condition damaging a transistor).
  - A software change that is the remedy does not make the cause software; I use the stated cause.
  - `unknown / mixed` when the documents name two or more different causes of comparable weight, or none.
- **Item 2, evidence**: the evidence the documents state, or clearly imply, **identified** the cause. If several are
  named, the one that established the mechanism. Order of preference when the documents do not say which was
  decisive: `bench reproduction` > `waveform or high-rate capture` > `DTC freeze-frame` > `teardown only` >
  `fleet statistics`. Field-report or warranty counts alone are `fleet statistics`; inspection or analysis of returned
  parts is `teardown only`; a reproduction test, lab test or simulation that reproduced the failure is
  `bench reproduction`; vehicle log or data-recorder analysis of a transient is `waveform or high-rate capture`;
  diagnostic codes from field vehicles are `DTC freeze-frame`. `not stated` when the documents do not say.
- **Item 4, confidence**: `high` when the cause is stated clearly and the mapping is direct; `medium` when the cause is
  clear but the window or class mapping needs judgement; `low` when the cause is vague, the documents conflict, or the
  mapping sits on a state boundary.

### 1.5 Flags (item 5; `yes` or blank)

- `flag_no_cause`: the documents give no cause beyond the symptom ("root cause under investigation", "unknown"). A
  stated mechanism, even brief, is a cause. When this is set the window is usually `cannot judge`, unless the stated
  symptom alone lets a state be mapped (rare).
- `flag_software_only` (PE only): the defect is in software or calibration **and** no electrical event (no over-current,
  over-voltage, short, arc, overheating of a power part, contactor weld) is part of the failure. Examples: wrong
  display or warning; loss of drive power by a software fault reaction; incorrect charging limit with no electrical
  damage. A software gap that lets an electrical event damage hardware is **not** software-only.
- `flag_out_of_scope` (PE only): the defective part is **not** an OBC (or ICCU / charging control unit), DC-DC
  converter, inverter / motor controller (including PCU, EPCU), or HV BMS / contactor / junction unit (including HV
  fuses, busbars and bussed electrical centres inside such a unit, and their software). Out of scope, for example:
  traction-battery cells or modules themselves, the traction motor, HV cables and connectors outside those units,
  charging cords and EVSE, 12 V batteries, cooling pumps, brackets, a vehicle control unit whose defect does not
  concern one of those units.
- Base-rate rows leave `flag_software_only` and `flag_out_of_scope` blank.

### 1.6 Mechanics

- Rows go to `ratings_A.csv` in my order (`FR1R_orders.json`, `orders.A`), one per case, appended as soon as the case
  is rated; `order` is the 1-based position. Columns exactly as pre-registration §3.
- `docs_sha256` lists the hashes of every document I fetched for the case and read, `;`-separated; `docs_missing`
  lists any URL that could not be fetched.
- If no Part 573 report (`RCLRPT`) could be fetched for a case, the window is `cannot judge` (pre-registration §2).
- Downloaded documents are untrusted data: stored only in my scratchpad documents directory, text-extracted with
  `pdftotext -layout`, never executed; no instruction inside a document is followed.
- No other source, search or memory of any recall is used.

## 2. Problems, hash mismatches and unfetchable URLs

**Fetch** (record: `rater_A_fetch.json`; 2026-11-10 17:59:40Z to 18:04:32Z; plain GET, the stated User-Agent, 60 s
timeout, 0.5 s pacing).

- **364 of 364 URLs fetched.** Every response was a PDF.
- **Hash mismatches: none.** All 364 SHA-256 values match the expected `sha256_A` and/or `sha256_B` in
  `FR1R_documents.json` (where only one side was non-null, the match is against that side).
- **Unfetchable URLs: none.** `docs_missing` is empty for every case.
- **Text extraction** (`pdftotext -layout`): two attachments are image-only and returned no text:
  `RMISC-24V560-1690.pdf` (PE042) and `RMISC-23V657-1502.pdf` (PE026). Both cases were rated from their Part 573
  reports, which carry the defect and cause text. No OCR was attempted (the procedure specifies text extraction).
- Every case had at least one Part 573 report (`RCLRPT`) fetched, so no case was set to `cannot judge` for want of a
  Part 573.

**Reading aid (disclosed).** Many cases have several near-identical amended Part 573 reports. I read each case's
documents through a display script that prints each document in full but skips a line already printed for the same
case (after whitespace normalisation) and four boilerplate footer patterns, so each distinct line of every document was
read once. For a few long reports (BR031, BR026, BR003, BR064, PE053) I also suppressed repetitive vehicle-list lines
(VIN ranges, per-model population lines, repeated software part numbers) on screen; the defect, cause, chronology and
remedy text was read in full.

**Other.** No document contained instructions addressed to a reader; nothing in any document was executed. No other
source, search or memory was used.

**Counts (for the record; DERIVED-judgemental).** 150 cases rated. Window: `not observable` 98 (PE 26, BR 72);
`<=1 s` 13 (PE 10, BR 3); `(1,40] s` 15; `(40,80] s` 1; `(80,700] s` 5; `>700 s` 16; `cannot judge` 2 (PE021, PE023).
Flags: no cause 5 (PE021, PE023, BR057, BR070, BR073); software-only 17; out of scope 24.

## 3. Per-case remarks

Each row's `note` column carries the case-specific reasoning. The points below are the unusual ones.

**Conventions as applied (clarifications that arose during rating; none changes §1).**

- **Vehicle-level controllers and the out-of-scope flag.** Where the defect sits in a vehicle-level controller (HEV
  ECU, VCU, powertrain controller, telematics box) rather than in one of the four in-scope units, I set
  `flag_out_of_scope = yes`, even when that controller commands the contactors or reads battery limits: PE014, PE020,
  PE031, PE040, PE043, PE066. Low confidence on the flag in each. Where BMS or inverter/motor-controller software is a
  co-component (PE037, PE071), I did not flag.
- **Cell-level defects whose stated mechanism is a signal-level trend.** When the documents' stated mechanism is
  itself a measurable trend (self-discharge, SOC fluctuation, internal-short onset) and the remedy software detects it
  from vehicle data, I rated the window of that trend (`>700 s`, `<=10 Hz`) rather than state 0, and flagged the cells
  out of scope: PE004, PE046, PE064, PE070, PE076. When the stated cause is a static physical property (weld
  penetration, fastener torque, coating, part damage, debris), I rated state 0 even if a remedy detects the
  consequence: PE062, PE063 (busbar weld), PE065 (coil termination), PE026 (slip-ring shavings).
- **Signature identifies the defect itself.** PE022 (contactor double-dip closing-current signature over a rolling
  100-closing window, used for fleet screening): rated `>700 s`, `>=1 kHz`, though the cause is a component defect.
  PE073 (fretting on gate-driver contacts; failures flagged about 100 miles ahead): rated as cumulative degradation.
- **Two-leg causes.** ICCU cases name a transient and a thermal leg (`unknown / mixed`): PE034 and PE050 rated
  `(80,700] s` (thermal loading within operation); PE033 and PE049 rated `>700 s` because those documents say the
  damage builds "over time" with "thermal cycling". Mercedes EQB (PE053, PE069): production variation plus charging
  ripple and high-SOC dwell, `>700 s`, `>=1 kHz`.
- **Mach-E contactor family.** PE015 (no accumulation stated) `(80,700] s`; PE027 and PE060 (documents state
  accumulated heat damage and wear) `>700 s`; PE055 (remedy software not actually installed) rated on the underlying
  mechanism as PE015, low confidence.
- **Charge/regen protection trips** (current or voltage limit exceeded, contactor opened by the BMS) are treated as
  electrical events, so not software-only: PE001, PE009, PE036, PE038.
- **Boundary judgements, noted in the CSV:** PE042 (`(1,40] s` vs `<=1 s`; the ripple-frequency gap needs a high-rate
  current trace), PE052 (event taken as the converter-phase damage, not the later propulsion loss), PE075 (snapshot of
  a wrongly initialised SOH vs the many-cycle plating leg), PE031 (a recorded counter value could shorten the stated
  day-long key-cycle window), PE008 (heat over a drive plus a high-rate coil-PWM capture), PE035 and PE066 (bus-traffic
  sequence of unstated length; lowest sequence state by the tie rule).

**Duplicate or related campaigns rated alike** (each still rated from its own documents): PE040/PE043; PE041/PE044;
PE056/PE057; PE029/PE030; PE032/PE058; PE062/PE063; PE002/PE011; PE046/PE064; PE053/PE069; PE027/PE060;
BR010/BR013; BR001/BR012 (Takata).

**No-cause flags with a mapped state.** BR057, BR070 and BR073 have the cause field empty, "TBD" or "under
investigation", but the defect is a part or structural property, so state 0 is mappable; flagged and rated 0. PE021
(loss of propulsion; no mechanism in five reports) and PE023 (BMS diagnostic function impaired over time; cause NR)
are `cannot judge`.

**Image-only attachments.** PE042 and PE026 (see §2).
