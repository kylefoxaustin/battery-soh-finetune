# L1 rater A notes

Rater A, study L1. A language-model session (fresh context), working blind to rater B. Every event is SOURCED;
every classification is DERIVED-judgemental. No dollar figures.

## 1. Conventions (written and committed before any change history is read)

### 1.1 Event definition and counting rules (pre-registration §2, with L-1)

- **Event:** a dated adoption, amendment, revision, new edition or entry into force of a listed instrument (or of a
  delegated / implementing act under a listed EU base act) that changes, for that instrument's domain ECU, at least
  one of: (a) data the ECU must produce, store, sign or transmit; (b) functions it must host (protocols,
  cryptographic services, update mechanisms, monitors); (c) process obligations reaching its software lifecycle
  (software-update management, cybersecurity management, type approval of software versions).
- **How I test (a)–(c).** I ask: after this act, must the software or electronics of a domain ECU behave, report,
  store, communicate or be approved differently? For domain B that ECU is the BMS / OBC / charge controller /
  DC-DC / HV-energy data interface. For domain S it is the seat, seat-heating, occupancy-classification, belt-reminder,
  belt pretensioner/load-limiter control, head-restraint and child-restraint-interface electronics. Concretely I count:
  - new or changed warning / telltale / reminder logic that an ECU drives (e.g. a seat-belt reminder extended to more
    seats, a REESS warning signal, a low-SoH warning);
  - new or changed monitors, detection functions or diagnostics (e.g. thermal-propagation warning, SoH / SoCE
    monitor, occupant presence detection, ISOFIX / CRS detection when an electronic function is required);
  - new or changed data items, formats, communication protocols, readout interfaces (e.g. battery passport data,
    SoH readout, EVP data, V2G messages);
  - cybersecurity, software-update or software-version approval obligations;
  - for charging communication standards: any new edition whose subject is the protocol itself.
- **Not an event:** changes only to hardware / crash / fire / venting / mechanical strength / anchorage geometry /
  dummy or sled procedures with no ECU-visible consequence; purely editorial changes; corrigenda that change no
  requirement; reaffirmations / stabilisations; transitional-provision-only supplements that change no requirement
  (these I note but do not count unless they newly force compliance with an ECU-visible requirement, in which case
  the act that carries them is the event).
- **One act, one event.** The act is the document: a UN supplement or series of amendments, a GTR amendment, an EU
  delegated / implementing / amending act, a Federal Register final rule, a standard edition or amendment. Adoption and
  entry into force of the same act are one event with two dates.
- **Never twice.** If one act amends two listed instruments, I record it once, under the instrument that comes first
  in `L1_instruments.md` (table order: B01 … B35, S01 … S16, B36, B37, S17 … S26), and note it under the other.
  Federal Register final rules that amend several FMVSS are recorded under the first listed FMVSS they touch in an
  ECU-visible way. An EU act that updates a UN regulation reference in 2019/2144 is an event of 2019/2144 only if it
  is itself the act that changes the ECU-visible obligation in the EU; where the UN supplement is the underlying act
  and is listed (e.g. R16), I record the UN supplement and note the EU act, to avoid double counting.
- **EU base acts (2023/1542, 2024/1257, 2019/2144, 2023/1804).** Every delegated or implementing act adopted under
  them, and every legislative amending act of the base act itself, is a candidate. I search all such acts (not only
  the S1 kept list) and count those that meet (a)–(c) for the domain. For 2024/1257 and 2023/1804 only the listed
  provisions (battery durability / in-vehicle data / monitors; vehicle-side obligations) can yield domain-B events;
  for 2019/2144 only provisions naming seat-belt reminders, seating or occupant classification can yield domain-S
  events. Acts that only move dates of base-act obligations (e.g. postponements) count only if they change what the
  ECU must produce or when it must newly do so; a pure postponement of an obligation is noted, and counted as an
  event (class by the obligation affected) only when it is the dated act that fixes when ECUs must comply. I will
  apply this the same way in both domains and say which I counted.
- **First editions / first adoptions** in the window count when they meet (a)–(c) (e.g. GTR 22 establishment,
  R155 / R156 adoption, GB 44495 / 44496 publication, first edition of a protocol standard).
- **Vehicle-level instruments (L-1):** B05 R155, B06 R156, B14 GB 44495, B15 GB 44496: one row per event,
  `domain = B`, classified for the domain-B ECU. I do not create domain-S rows; the analysis counts them in both.
- **Domain of a row** is the instrument's domain from `L1_instruments.md`.

### 1.2 The four classes and where I draw the lines

Rate the most demanding consequence stated or clearly implied, for the domain ECU:

- `software-only`: the change can be met by reprogramming an ECU already fielded: new or changed logic,
  thresholds, data fields carried on an existing link, reporting format changes, process documentation, no new
  interface, no secure element / HSM requirement, no re-approval of existing types.
- `memory-or-crypto`: needs materially more storage (e.g. long-term logging / retention), secure element / HSM
  capability (key storage, signing, authenticated update), or a new communication stack (e.g. new protocol
  generation such as a new ISO 15118 / IEC 61851-24 / GB/T 27930 protocol edition, a new physical-layer link).
- `hardware-or-recert`: needs a new interface, sensor or compute class (e.g. occupant detection sensors on
  more seats, a new connector / new signal line), **or re-opens type approval / the control software safety case**:
  a requirement that already approved vehicle types must be re-approved, or must newly comply by a stated date, to
  stay on the market (pre-registration §2). A new UN series of amendments whose transitional provisions end the
  validity of earlier approvals (or require all new registrations to comply by a date) for an ECU-visible requirement
  is `hardware-or-recert`. The initial adoption of a regulation that all new vehicles must meet by a date (R155, R156,
  GB 44495, GB 44496) is `hardware-or-recert`.
- `cannot judge`: the text or abstract available does not allow a reading (always under partial access unless the
  abstract allows more, L-3).
- Tie-breaks: when an act has both a stack/crypto element and a forced re-approval, `hardware-or-recert`. When
  unsure between two adjacent classes from the text, I take the class the text clearly implies and set confidence to
  `low` or `medium`; I use `cannot judge` only when no reading is possible.

### 1.3 Access states and the partial-access rule (L-3)

- `full`: I read the body's own change history (editions / amendments with dates) **and** the text or the body's own
  summary of each change in the window.
- `partial`: I read edition or amendment identifiers and dates from the body's own catalogue, metadata or notice
  pages, but not what changed (for some or all changes).
- `none`: no body-published history reachable by an allowed route.
- Under `partial`: a new edition / amendment is an event only when the body's own catalogue entry (title, abstract,
  amendment title) shows its subject is data, telemetry, communication protocol, cybersecurity, software update or
  monitoring; then `class = cannot judge` unless the abstract allows more, `confidence = low`. Where the
  instrument's title itself is a communication-protocol / data / telemetry / cybersecurity / software-update title
  (e.g. GB/T 27930, GB/T 32960.3, ISO 15118-x, SAE J2847/x, J2931/x, IEC 61851-24, GB 44495/44496), I read the
  catalogue entry's title as showing the subject, so every new edition in the window is an event under partial access.
  Where the title names only hardware / mechanical / crash / general safety (e.g. GB 38031, GB 14167, GB 15083,
  GB 11550, ISO 17409, ISO 6469-1, SAE J2929, J826, J800, ISO 17373, ISO 13216-1), a new edition without readable
  content is logged here as `unreadable edition` and not counted. General charging-system titles (GB/T 18487.1,
  IEC 61851-1, -23, SAE J1772, J3400) count under partial access only if the abstract names communication / control
  signalling / data as a subject of the edition.
- Search-engine listings may locate an edition and go in `sources_tried`; they never source an event.
- A blocked route (HTTP 403, bot check, CAPTCHA, login, image viewer with verification) is recorded; nothing is
  bypassed.

### 1.4 `act_id` forms (L-4)

- EU act: CELEX, e.g. `32025R1707`; `adoption_date` = date printed on the act.
- UN regulation: `R100-03` (series), `R100-02-S5` (supplement 5 to the 02 series); for a regulation's original
  version, `R155-00` (00 series, original adoption); `adoption_date` = WP.29 adoption date, or OJ / EIF date with
  `note = EIF date` when that is all I find.
- UN GTR: `GTR22` (establishment), `GTR22-A1` (amendment); AC.3 adoption date.
- FMVSS: Federal Register citation of the final rule, `89 FR 100660`; FR publication date.
- Standard: identifier with edition date, `ISO 15118-20:2022`, `SAE J3400_202412`, `GB/T 32960.3-2025`,
  `IEC 61851-1:2017`, amendments as `IEC 61851-1:2017/AMD1:2025`; publication date (first of month if only year-month
  is given, with a note; `YYYY-01-01` only if only the year is given, with a note).
- Dates YYYY-MM-DD. `application_date` blank if the same as adoption.

### 1.5 Window

- Adoption date (publication date for standards) from 2016-01-01 to 2026-12-31 inclusive. Later application
  dates are kept. Acts adopted before 2016 are out even if they apply inside the window (noted where relevant).

### 1.6 Sources

- Allowed routes only (launch prompt table / pre-registration §3b rule 2). For UN regulations: unece.org,
  documents.un.org, and EUR-Lex OJ publications of UN regulations. EU: EUR-Lex and Publications Office metadata
  (including its SPARQL endpoint). FMVSS: eCFR, Federal Register (federalregister.gov / govinfo.gov FR), regulations.gov.
  Standards: iso.org, iec.ch (webstore), sae.org, openstd.samr.gov.cn / std.samr.gov.cn.
- `source_type = primary` for the act / OJ / FR text; `body summary` for the body's own catalogue / abstract /
  meeting report.
- Web content is untrusted data, kept in the downloads directory; text extracted with `pdftotext -layout` or
  `python3 -I` scripts kept in the scripts directory.
