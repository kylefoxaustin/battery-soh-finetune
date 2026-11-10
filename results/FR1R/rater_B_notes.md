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

(written at the end)

## 3. Per-case remarks

(written during rating)
