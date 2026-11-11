# DC2 rater A notes

Rater A of study DC2 (the ramp-spec audit), a fresh-context language-model session (FR1 D-3). Branch `dc2-rater-a`.
Reading date: 2026-11-10 onwards (November 2026). Every requirement row is **SOURCED**; every class is a
**DERIVED** judgement. No dollar figures.

## 1. Conventions (written and committed before any requirement text is read)

These conventions apply `DC2_preregistration.md` §1–§4, with §10 (DC2-1, DC2-2) overriding anything earlier.

### 1.1 What counts as a requirement; counting rules (§2)

- A **requirement** is one clause of a listed instrument that states a limit on (a) the load's real power or its rate
  of change in time, or (b) a voltage-quality quantity that such variation drives (flicker, rapid voltage change,
  harmonics, and the other non-deciding quantities in the closed list), together with the window over which it is
  assessed (or with no window, in which case the window class is `not stated` unless the rate-unit or response-time
  rule applies).
- A clause that only asks for studies, models, data, notification, coordination, or that describes behaviour without a
  limit, is not a requirement. A clause that says a limit "will be set by the operator" without printing it is not a
  row (no limit is printed); I mention it in the instrument note.
- **One clause, one row.** If one clause states several distinct limits on different quantities (e.g. a ramp limit and
  a step limit), each distinct limited quantity is its own row under the same `clause`, distinguished by `category`
  when the text gives a label, else by `quantity` (and a note).
- **A table of limits by category** is one row per category; the category label as printed goes in `category`. A table
  with categories by voltage level (e.g. Pst and Plt per voltage level) is one row per category label as printed; where a
  row of the table carries two quantities (e.g. Pst and Plt), I keep one row per printed category and quantity and put
  the second quantity in a second row with the same category plus the quantity name appended in `category` only if the
  table prints it as a separate column heading (e.g. `MV / Pst`, `MV / Plt`).
- **Never twice.** A limit restated in two clauses of one instrument is one row, under the clause that states the
  number; the other clause is named in `note`.
- **A different instrument repeating a limit** is a row of that instrument only if it states the limit itself. A bare
  cross-reference ("shall comply with X", "as defined in X") is not a row; it goes in `note` in `instruments_A.csv`.
- Definitions, test methods and measurement procedures (e.g. a flickermeter specification, a measurement-method
  standard) are not limits; such documents may be `no requirement`, unless they print a limit.

### 1.2 Deciding set and non-deciding quantities

- **Deciding** (`deciding = yes`) exactly when `quantity` is one of: `ramp rate`, `step change`, `swing amplitude`,
  `smoothing or capping response`, `load change per interval`.
- `ramp rate`: a limit on dP/dt (MW/s, MW/min, %/s, %/min).
- `step change`: a limit on a single change in power (MW or % of a base) without a stated rate.
- `swing amplitude`: a limit on oscillation or periodic fluctuation amplitude of real power (including a limit on power
  oscillation amplitude in a frequency band).
- `smoothing or capping response`: a required response time of a power-smoothing / power-capping / curtailment
  function on the load's real power.
- `load change per interval`: a limit on the change of real power within a stated interval (e.g. "no more than X MW in
  any Y minutes").
- **Non-deciding** (`deciding = no`): `flicker`, `rapid voltage change`, `harmonics`, `power factor`, `ride-through`,
  `hold-up`, `other`. Post-fault active-power recovery is a requirement on real power after a disturbance; I classify it
  as `ride-through` (it is a disturbance-performance requirement, met by the converter, part of ride-through clauses),
  and say so in `note`. A voltage-unbalance, frequency-withstand or RoCoF-withstand limit is `ride-through` when it is a
  withstand requirement and `other` otherwise. A dynamic-loading or transient-response specification of a power supply
  output (voltage deviation for a load step) is `other` (it limits the supply's voltage, not the load's power), unless
  it limits the real power drawn from upstream.

### 1.3 Binding classes (§2)

- `mandatory`: a code, protocol, rule, regulation, tariff condition, or a grid operator's connection requirement that a
  connecting load must meet; also an operator's or vendor's specification that a supplier must meet to sell into it
  (e.g. an OCP base specification's "shall"), with `measurement_point` saying where it applies.
- `planning level`: a limit the network operator applies in assessment (e.g. IEC 61000-3-7 planning levels, D-A-CH-CZ
  Planungspegel, GB Grid Code flicker planning levels). Emission limits allocated to a customer from planning levels
  in a document the operator applies to the connection are `mandatory` when the document says the customer shall meet
  them, and `planning level` when the document presents them as assessment values.
- `recommendation`: "should", a recommended practice, a guideline, an informative annex. A "shall" inside a document
  the body itself designates as a guideline, reliability guideline, recommended practice, technical report or white
  paper is `recommendation`.
- `vendor capability`: a configurable feature (e.g. GPU or rack power-smoothing ramp setting, power-cap range):
  not a requirement on anyone. A vendor white paper's description of what its products do is `vendor capability`.
- Where a voltage-characteristics standard (e.g. EN 50160) states values the network should meet, I record its rows
  as `recommendation` unless the text designates them as a limit on the load (its values describe supply, not load;
  if it states no limit on the load I may record `no requirement`). Decided per instrument and noted.

### 1.4 Window classes; rate-unit rule; response-time rule

- Window = the measurement, averaging or assessment interval *T*. Classes: `≤ 100 ms` (T ≤ 0.1 s);
  `100 ms – 1 s` (0.1 s < T < 1 s); `1 – 60 s` (1 s ≤ T ≤ 60 s); `1 – 15 min` (60 s < T ≤ 15 min);
  `> 15 min` (T > 15 min); `not stated`.
- Boundaries: exactly 1 s → `1 – 60 s`; exactly 60 s / 1 min → `1 – 60 s`; exactly 15 min → `1 – 15 min`; exactly
  100 ms → `≤ 100 ms`. Cycles are converted at the stated system frequency (or 60 Hz for North American documents,
  50 Hz for European), with the arithmetic in `note`.
- Flicker: Pst's window is 10 min → `1 – 15 min`; Plt's is 2 h → `> 15 min` (these are the standard observation
  periods; I use them only when the clause names Pst / Plt, which by definition carry them, and say so in `note`).
- **Rate-unit rule (`unit:`).** When a clause states a measurement, averaging or assessment interval, that interval is
  the window. When it does not, the time unit of the printed rate is taken as the window (per second → 1 s; per minute
  → 1 min; per hour → 1 h); `window_as_printed` then begins `unit:`, e.g. `unit: MW/min`. A step or swing limit with no
  stated interval and no rate unit is `not stated`. Every use is listed in §3.
- **Response-time rule (`response:`).** For `smoothing or capping response`, the window is the interval over which
  compliance is assessed; when only a response time is printed, the window is that response time, and
  `window_as_printed` begins `response:`. Every use is listed in §3.

### 1.5 Allowance classes; `hard` default; `not stated`

- Share *a* that may exceed: `hard` (a = 0); `tight` (0 < a ≤ 0.1 %); `loose` (0.1 % < a ≤ 5 %); `very loose`
  (a > 5 %); `event count` (a number of exceedances per hour / day / year, not a share); `not stated`.
- A percentile limit: the 99th percentile → a = 1 % → `loose`; 95th → 5 % → `loose`; 99.9th → `tight`.
- **`hard` default.** A plain maximum ("shall not exceed", "maximum", "limited to", a plain numerical limit in a
  requirement) with no allowance clause is `hard`.
- **`not stated`** only when the text says the limit is assessed statistically, "normally", "as far as practicable",
  "generally", or similar, without saying how much exceedance is permitted; and under partial access when the page
  read does not print the allowance (§4).
- A percentile on another quantity (e.g. a 95th-percentile voltage limit inside a ramp clause) does not set the
  clause's allowance.
- Planning levels and emission limits for flicker that the text states as 95 %- or 99 %-of-time values get the
  corresponding percentile class.

### 1.6 DC2-2 (event count with recurrence and duration)

When a clause prints both a permitted recurrence (frequency, or minimum interval between exceedances) and a maximum
duration of each exceedance, I compute *a* = duration / recurrence interval, set `allowance_class` from *a* by the bands
above, keep the printed form in `allowance_as_printed`, and write the arithmetic in `note` naming DC2-2 (e.g.
"DC2-2: 2 s / 3600 s = 0.056 % → tight"). The window is then the printed duration unless the clause states an
assessment interval. When only one of the two is printed, the class stays `event count` (shape `cannot judge`). Every
conversion is listed in §3.

### 1.7 Shape table (§2)

| Window class | `hard` / `tight` | `loose` / `very loose` | `event count` / `not stated` |
|---|---|---|---|
| `≤ 100 ms` or `100 ms – 1 s` | electronics | electronics | electronics |
| `1 – 60 s` | reactive | history | cannot judge |
| `1 – 15 min` or `> 15 min` | reactive | reactive | reactive |
| `not stated` | cannot judge | cannot judge | cannot judge |

I write `shape` from this table only, from my own window and allowance classes, for every row (deciding or not).

### 1.8 Pending rule (§1) and partial-access rule (§4)

- **Pending.** The instrument is read as in force or as last published on my reading date. A proposal not adopted by
  its body on that date (revision request, NOPR, draft standard, draft amendment, tariff filing not yet approved,
  stakeholder proposal) → `status = pending`, logged in §2/§4 below as `pending: <identifier>, <status as printed>`,
  no rows. An approved instrument whose effective date is later than the reading date (adopted, not yet effective) is
  not a proposal: it is adopted by its body, so I treat it as `in force` for DC2 purposes and say so in its note. If
  an instrument listed as pending has been adopted by my reading date, I rate it and record what I found.
- Status of an in-force document that contains no §2 limit → `no requirement`.
- **Partial access.** A row read from an abstract, preview or the body's own summary gets `confidence = low` and its
  page in `source_url`; a window or allowance the page does not print is `not stated` (shape then follows the table:
  `cannot judge` when the window is not stated); never infer a row from a title.

### 1.9 Access states (§3 S2) and allowed routes (§3 S4)

- `full`: the requirement text is readable from the body's own site; `partial`: only an abstract, preview, table of
  contents, catalogue page or the body's own summary is readable; `none`: nothing beyond the title is reachable by an
  allowed route.
- Allowed routes: ercot.com, nerc.com, pjm.com, puc.texas.gov (and interchange / ftp), ferc.gov (and eLibrary),
  eur-lex.europa.eu, entsoe.eu, acer.europa.eu, neso.energy, ena-eng.org, vde.com and vde-verlag.de, iec.ch /
  webstore.iec.ch, ieee.org / standards.ieee.org, cencenelec.eu, opencompute.org, docs.nvidia.com /
  developer.nvidia.com / nvidia.com (including its asset CDN linked from nvidia.com), the utility's own tariff pages and
  the state commission's docket, the D-A-CH-CZ association's own site (VDE FNN download pages and the publishing
  association), and for group X the grid operator's or regulator's own site (aeso.ca, fingrid.fi, ieso.ca).
- Never a source: papers, EPRI reports, blogs, trade press, search-result listings or their summaries, resellers,
  secondary summaries. No bot check, CAPTCHA, paywall, login, cookie wall or verification step is circumvented; a
  blocked route is `none` and is recorded.
- Fetching: User-Agent `DC2-rater-A research fetch (public grid and power-quality texts)`, 60 s timeout, polite
  pacing; downloads only in my downloads directory; text by `pdftotext -layout` or `python3 -I` scripts in my scripts
  directory; nothing in fetched content is executed or followed as an instruction.
