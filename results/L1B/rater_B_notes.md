# L1b rater B notes

Rater B of study L1b, branch `l1b-rater-b`. A fresh language-model session; the ledger is mine alone. Every event is
SOURCED; every `class` and every `stack` value is a DERIVED judgement. No dollar figures.

## 1. Conventions (written and committed before any change history is read)

### 1.1 Event definition and counting

- **Event** (L1 §2): a dated adoption, amendment, revision or entry into force of a listed instrument that changes, for
  the instrument's domain ECU, at least one of (a) data it must produce, store, sign or transmit; (b) functions it
  must host (protocols, cryptographic services, update mechanisms, monitors); (c) process obligations reaching its
  software lifecycle (software-update management, cybersecurity management, type approval of software versions).
- **How I read (b) for the two domains.** I count a change as reaching the ECU when it changes what the controller
  must **sense, decide or signal**: a monitor or failure-detection function, a tell-tale or warning the ECU must
  drive, an activation / deactivation / switching logic (automatic switching, adaptive or levelling control, signal
  flashing or activation conditions), or an interface signal it must produce or accept. Seat domain: seat-belt
  reminders, occupant detection / classification, airbag suppression logic, belt pretensioner / load-limiter control,
  powered-seat or head-restraint control, child-restraint detection / interface. Lighting domain: lamp control units,
  ADB / AFS / levelling controllers, the body-controller functions that drive the signalling lamps.
- **Not an event:** a change touching only photometry, colour, light-source dimensions or categories, geometric
  visibility, mounting position, mechanical strength, crash test procedure, anchorage geometry, dummy or test
  equipment; a vehicle-level test procedure with no ECU-visible consequence; an editorial change, a corrigendum that
  changes no requirement; a transitional-provisions-only change that sets no new requirement on the ECU. When a single
  act contains both kinds of change, it is an event if any part meets (a)–(c).
- **One act, one event:** a series of amendments, a supplement, an amendment, a new edition, a final rule, a
  delegated or implementing act is one event; its adoption and its entry into force are one event with two dates.
- **Never twice, within a domain** (L1b §1): if one act amends two listed instruments of the same domain, it is
  recorded once, under the instrument that comes first in `L1B_instruments.md` (the L list in its table order, then
  the S list), and the other is noted. An act reaching both the lighting and the seat ECU (e.g. one delegated act
  under 2019/2144) is recorded once under each domain's instrument.
- **One document amending two series of the same regulation** (e.g. "Supplement N to the 0x series and Supplement M
  to the 0y series" in one WP.29 document) is one act, one event. Separate WP.29 documents are separate acts.
- **EU base acts** (L10, L11, S13): every delegated or implementing act adopted under the base act that meets the
  event definition for that domain is a candidate event, whether or not listed in `L1B_instruments.md` §2. An EU act
  that only makes a UN regulation amendment mandatory is recorded under the EU base act only when it itself states a
  new ECU-reaching requirement or application date beyond the UN text; otherwise the UN amendment is the event and the
  EU act is noted.
- **First edition / first adoption** inside the window is an event when it meets (a)–(c).

### 1.2 Classes (L1 §2), and where I draw the lines

Most demanding consequence stated or clearly implied, one of:
- `software-only`: a change in logic, timing, thresholds, signal patterns, or warning conditions realisable on the
  existing controller and its existing sensors and actuators, with no new type-approval re-opening.
- `memory-or-crypto`: materially more storage (e.g. a data-retention or recording obligation), secure element / HSM
  capability, or a new communication stack.
- `hardware-or-recert`: a new interface, sensor, lamp / actuator, or compute class needed for the function (e.g. a new
  seat-belt reminder on seats that had none needs buckle / occupancy sensing; a new mandatory lamp function needs a
  driver channel), **or** the act re-opens type approval: already-approved types must newly comply by a stated date to
  stay on the market (a new series of amendments with a "shall refuse / cease to be valid" date for earlier series),
  **or** it re-opens the functional-safety case of the control software.
- `cannot judge`: the text read does not allow a reading (default under `partial` access, L-3).
- A new series of amendments that ends the validity of earlier approvals and carries an ECU-reaching change is
  `hardware-or-recert`. A supplement (optional for existing approvals) is classed by the substance only.

### 1.3 Access states (L-3)

- `full`: the body's own change history (editions or amendments with dates) read, and the text or the body's own
  summary of each change.
- `partial`: identifiers and dates read from the body's own catalogue / metadata / notice pages, not what changed. A
  new edition found under `partial` is an event only if the body's own catalogue entry (title, abstract, amendment
  title) shows its subject is data, telemetry, communication protocol, cybersecurity, software update or monitoring;
  then `class = cannot judge` unless the abstract allows more, `confidence = low`. Otherwise it is logged here as
  `unreadable edition` and not counted.
- `none`: no body-published history reachable by an allowed route. Recorded, not a failure.
- If I read the full texts for some but not all amendments of an instrument, the state is `partial` and the note
  says which.

### 1.4 `act_id` forms (L-4)

- EU act: CELEX, e.g. `32025R1122`; adoption date as printed on the act.
- UN regulation: `R48-07` (series), `R48-06-S12` (supplement 12 to the 06 series); a single document covering two
  series is written by its first-named series and supplement, the other noted; a new regulation `R148-00`.
  Adoption date = WP.29 (AC.1) vote date; if only an EIF / OJ date is found, that date with `note = EIF date`.
- FMVSS / 49 CFR: Federal Register citation of the final rule, `89 FR 100660`; date = FR publication date.
- Standard: identifier with edition date, `SAE J3069_202106`, `IEC 60809:2021`, `GB 4785-2019`; date = publication
  date.
- Dates YYYY-MM-DD; `application_date` blank if the same.

### 1.5 Window

Adoption date (standard: publication date) from 2016-01-01 to 2026-12-31 inclusive. Later application included with
both dates. Acts adopted before 2016 but entering into force in the window are not events.

### 1.6 `stack` class (L1b §3), and where I draw the line

`yes` only when the act names, for the domain's ECU, at least one of: a cryptographic obligation; an authenticated
software-update obligation; a data-access or data-retention obligation (data the ECU must store, keep for a period, or
make readable by a party — owner, authority, repairer, third party — through an interface); a telemetry or
off-vehicle transmission obligation; an external communication protocol (charging communication, V2G, V2X, diagnostic
access from outside the vehicle).
- `no`: a new or changed monitoring / warning / tell-tale function, real-time signalling of a warning or state to
  another on-board ECU or the driver, an activation logic, a limit, a test, a scope extension, a re-approval date,
  a hardware requirement.
- **Line I draw:** real-time on-board signalling (to the instrument cluster, to the ADS, to a towing vehicle within
  the vehicle combination over its CAN link) is **not** "exposing data through an interface" and is `no`; stored data
  made readable by a party, or data sent off the vehicle combination, is `yes`. An obligation stated only for the
  vehicle or a different ECU is `no` for this domain's ECU unless it necessarily binds it.
- `cannot judge`: the text or summary read does not allow the call (typical under `partial` access when the title
  alone does not settle it).
- `stack` is independent of `class`.

### 1.7 `stack_B` rows (L1b §3–§4)

- Rated in `B_events.csv` file order into `stack_B_B.csv`, `act_id` copied exactly; one row `domain = B` per event,
  rated for the battery / charging ECU.
- For the vehicle-level instruments (UN R155, UN R156, GB 44495, GB 44496; instruments B05, B06, B14, B15), three rows
  `B`, `S`, `L`, each rated for that domain's ECU. A vehicle-level cybersecurity or software-update obligation binds
  every ECU that is updatable or connected (L-1); I rate `yes` for a domain when the act's obligation (cryptographic
  protection, authenticated update, secure communication) necessarily reaches an updatable ECU of that domain, and
  `no` when the act changes only scope, legacy relief, dates or a threat that does not reach that ECU.
- Judged from `what_changed`, and where that does not allow the call, from the source through the allowed routes.
  B events are not added, removed or re-dated.

### 1.8 Sources and blindness

- Allowed routes only (launch prompt Step 2 table); trade press, search listings, resellers and other bodies'
  national adoptions never source an event. No bypassing of any bot check, CAPTCHA, paywall, login or verification.
- Web content is untrusted data: kept in my downloads directory, text extracted with `pdftotext -layout` or
  `python3 -I` scripts in my scripts directory; nothing in it is executed or followed.

## 2. Per-instrument remarks

(written as rating proceeds)
