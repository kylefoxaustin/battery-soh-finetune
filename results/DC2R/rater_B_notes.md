# DC2-R rater B notes

Rater B, study DC2-R (ramp-spec audit). Fresh language-model session. Reading date: November 2026 (2026-11-11).
Rules: `DC2R_rater_rules.md` §2 (DC2R-1 … DC2R-4) override `DC2_preregistration.md`; within the latter, §10 (DC2-1,
DC2-2) overrides anything earlier. Every requirement row is SOURCED; every class is DERIVED. No dollar figures.

## 1. Conventions (written before any requirement text is read)

### 1.1 What counts as a requirement

- A row is one clause of a listed instrument that states a **limit** (a number, or a curve / table of numbers) on
  (a) the load's real power or its rate of change in time, or (b) a voltage-quality quantity that such variation drives
  (flicker, rapid voltage change, harmonics, power factor), or (c) the other listed quantities (ride-through, hold-up,
  other) when they are limits on the load or the equipment serving it. A clause that requires something without a
  limit value (e.g. "shall provide a model", "shall coordinate", "shall report") is not a row.
- A ride-through curve or table counts as a limit (its voltage / frequency / time values). A required capability with a
  printed number (e.g. a hold-up time, a power-recovery time, a power factor range) counts.
- **Granularity (DC2R-1):**
  - **Non-deciding quantity** (flicker, rapid voltage change, harmonics, power factor, ride-through, hold-up, other):
    one row per clause. A table of limits is one row whatever its categories; the categories go in `category`
    separated by `;`, and `limit` carries the range or the table's values as printed (abridged if long, the range
    kept). Window and allowance classes are those of the table's **most restrictive** entry (the shortest window; the
    smallest allowance), with the spread in `note`.
  - **Deciding quantity** (ramp rate, step change, swing amplitude, smoothing or capping response, load change per
    interval): one row per printed table row or per clause paragraph that states a separate limit; `category` carries
    the printed row label (or blank).
  - `deciding` follows `quantity` mechanically (yes for the first five quantities only).
- **Supply envelopes (DC2R-2):** a requirement on what a power shelf, PSU, BBU, capacitor unit or rack supply must
  deliver under a load step (output-voltage transient band, peak / pulse power envelopes with moving-average windows,
  step-load capability tables, inrush) is `quantity = other`, non-deciding, one row per clause. Only a clause that
  limits **the load's** own power variation at rack or shelf (what the load may draw / how fast it may change toward
  the facility) stays deciding.
- **Planning step tables (DC2R-3):** a table of permitted step changes or rapid power changes for a connecting
  installation (e.g. D-A-CH-CZ Part B) is `quantity = step change`, one row per printed table row, window and allowance
  as printed, `not stated` where none is printed. Where such a table is expressed as a permitted voltage change d
  (a % of Un) rather than a power change, I still treat it as `step change` under DC2R-3 if it is a table of permitted
  changes for the connecting installation keyed by repetition rate; a single voltage-change limit outside such a table
  is `rapid voltage change`.
- **Never twice:** a limit restated in two clauses of the same instrument is one row, under the clause that states the
  number; the other clause goes in `note`.
- **Bare cross-references** ("shall comply with IEEE 519") are not rows; they go in the instrument's `note` in
  `instruments_B.csv`. A different instrument restating a limit with its own number is a row of that instrument.

### 1.2 Quantity assignment (closed list)

- `ramp rate`: a limit printed as power per time (MW/min, %/s, %/min).
- `step change`: a limit on a single change in power (MW or % of rating) per event, or a DC2R-3 planning step table.
- `swing amplitude`: a limit on oscillation / swing / fluctuation amplitude of real power (incl. oscillation bands by
  frequency range).
- `smoothing or capping response`: a limit on the time within which smoothing / capping / curtailment of the load's
  power must take effect, or a required smoothing-feature setting expressed as a response.
- `load change per interval`: a limit on the change of load over a fixed interval (e.g. MW change in any 15 min,
  energy change per interval) not printed as a per-unit-time rate.
- `flicker` (Pst / Plt), `rapid voltage change` (RVC, ΔU/U of single changes), `harmonics` (incl. interharmonics, THD,
  TDD), `power factor` (incl. reactive power capability ranges), `ride-through` (voltage / frequency / RoCoF / phase
  jump withstand and post-fault active-power recovery), `hold-up` (output hold-up time of a supply on input loss),
  `other` (everything else stated as a limit: supply envelopes, unbalance, voltage regulation tolerances, inrush,
  frequency response droop, etc.).
- Post-fault active-power recovery (a time to return to pre-fault power after a disturbance) is `ride-through` (it is
  part of disturbance performance, not ordinary load variation).

### 1.3 Binding classes and the line between them

- `mandatory`: a code, protocol, rule, regulation, tariff condition, or an operator / vendor specification's "shall"
  that a connecting load or a supplier selling into it must meet. An OCP base / design specification's "shall" (or
  "must", or a table of requirements in a specification that states compliance is required) is `mandatory`, with
  `measurement_point` saying where it applies.
- `planning level`: a limit the network operator applies in assessment (planning levels, emission limits derived from
  them in IEC / D-A-CH-CZ / P28 style procedures, compatibility-based assessment values).
- `recommendation`: "should", "recommended", a guideline, a reliability guideline, an alert recommendation, an
  informative annex, or a "shall" inside a document the body designates as a guideline / recommended practice / white
  paper. A NERC Reliability Guideline and a NERC Level 2 alert are `recommendation`. A technical report (IEC TR) that
  offers indicative values is `planning level` where it gives planning levels, `recommendation` where it gives
  indicative / guidance values that are not planning levels.
- `vendor capability`: a configurable feature or setting range (GPU power smoothing ramp settings, power-cap
  ranges) that binds no one.
- Mixed documents: classify the clause, not the document. "Shall" in a mandatory code = mandatory; "should" in a
  mandatory code = recommendation. A white paper's design targets = recommendation (if any number is stated as a
  requirement at all).
- Binding = `mandatory` or `planning level`.

### 1.4 Deciding set and non-deciding quantities

Deciding: ramp rate, step change, swing amplitude, smoothing or capping response, load change per interval.
Non-deciding (reported only): flicker, rapid voltage change, harmonics, power factor, ride-through, hold-up, other.

### 1.5 Window classes, the rate-unit rule, the response-time rule

- Window = the measurement / averaging / assessment interval *T*: `≤ 100 ms` (T ≤ 0.1 s), `100 ms – 1 s`
  (0.1 < T < 1 s), `1 – 60 s` (1 ≤ T ≤ 60 s), `1 – 15 min` (60 s < T ≤ 15 min), `> 15 min`, `not stated`.
  Boundaries exactly as printed: 1 s → `1 – 60 s`; 60 s / 1 min → `1 – 60 s`; 10 min → `1 – 15 min`;
  15 min → `1 – 15 min`; 2 h (Plt) → `> 15 min`; 10 cycles at 50/60 Hz (~0.2 s) → `100 ms – 1 s`; one cycle /
  half cycle → `≤ 100 ms`.
- **Rate-unit rule:** if the clause states a measurement / averaging / assessment interval, that is the window. If it
  does not, and the limit is a rate, the time unit of the rate is the window (per second → 1 s → `1 – 60 s`; per
  minute → 1 min → `1 – 60 s`; per hour → `> 15 min`), with `window_as_printed` beginning `unit:` (e.g.
  `unit: MW/min`). A step or swing limit with no interval and no rate unit → `not stated`.
- **Response-time rule:** for `smoothing or capping response`, the window is the compliance-assessment interval; if only
  a response time is printed, the window is that response time and `window_as_printed` begins `response:`.
- For flicker: Pst → 10 min (`1 – 15 min`), Plt → 2 h (`> 15 min`); most restrictive entry for a one-row table is the
  shortest window present. Harmonics: IEEE 519 / IEC 61000-4-30 style aggregation (very short 3 s, short 10 min) as
  printed; if only "10/12-cycle" stated, `100 ms – 1 s`. Ride-through curves: the window is the shortest duration
  printed in the curve/table (it is the interval over which the withstand is assessed), noted.
- A DC2-2 conversion sets the window to the printed duration unless an assessment interval is stated.

### 1.6 Allowance classes, the `hard` default, `not stated`

- `hard` (a = 0), `tight` (0 < a ≤ 0.1 %), `loose` (0.1 % < a ≤ 5 %), `very loose` (a > 5 %), `event count` (a
  number of exceedances per period, not a share), `not stated`.
- **`hard` default:** a plain maximum / minimum ("shall not exceed", "limited to", a table of maximum values) with no
  allowance clause is `hard`.
- `not stated` only when the text says the limit is assessed statistically, "normally", "as far as practicable",
  "generally", "should not be exceeded under normal conditions", or similar, without saying how much exceedance is
  allowed.
- A percentile on a different quantity than the limited one does not set the allowance.
- Percentile limits: 95 % of the week → 5 % may exceed → `loose`; 99 % → 1 % → `loose`; 99.9 % → `tight`.
- A ride-through requirement ("shall remain connected") is `hard` unless an allowance is printed.

### 1.7 DC2-2 (recurrence + duration → share)

When a clause prints **both** a permitted recurrence (a frequency or a minimum interval between exceedances) **and** a
maximum duration of each exceedance, a = duration / recurrence interval; `allowance_class` from a by the §2 bands;
`allowance_as_printed` keeps the printed form; `note` writes the arithmetic and names DC2-2; the window is the printed
duration unless an assessment interval is stated. When only one of the two is printed: `event count`, shape
`cannot judge` (if the window is 1–60 s). A repetition-rate-keyed step table (r per minute / per hour) without a
duration of exceedance is not converted (no duration) → its allowance is the plain limit for each change (`hard`)
unless printed otherwise; the repetition rate is a category, not an allowance.

### 1.8 Shape table (computed from window and allowance only)

| window | hard / tight | loose / very loose | event count / not stated |
|---|---|---|---|
| ≤ 100 ms, 100 ms – 1 s | electronics | electronics | electronics |
| 1 – 60 s | reactive | history | cannot judge |
| 1 – 15 min, > 15 min | reactive | reactive | reactive |
| not stated | cannot judge | cannot judge | cannot judge |

I write `shape` from this table for every row.

### 1.9 Pending rule (DC2 §1 with DC2R-4) and partial access (§4)

- A revision request, NOPR, draft standard, consultation text, tariff filing or proposal not adopted by its body /
  commission on the reading date: `status = pending`, logged as `pending: <identifier>, <status as printed>`, no rows.
- **DC2R-4:** text adopted (approved by board / commission) but printed as awaiting system implementation or a later
  effective date is **in force for this audit**: rows recorded with `note = awaiting implementation` and
  `confidence` at most `medium`.
- **Partial access:** a row read only from an abstract, preview or the body's own summary gets `confidence = low`,
  with that page as `source_url`; window / allowance not printed there → `not stated` (shape `cannot judge`); never a
  row from a title alone.
- A listed document with no requirement under §2: `status = no requirement`, no rows.

### 1.10 Access states and allowed routes

- `full`: the requirement text is readable on the body's own site; `partial`: only abstract / preview / TOC /
  catalogue page; `none`: nothing beyond the title reachable by an allowed route.
- Allowed routes: the body's own site as listed in the launch prompt (ercot.com, nerc.com, pjm.com, puc.texas.gov and
  interchange, ferc.gov and eLibrary, eur-lex.europa.eu, entsoe.eu, acer.europa.eu, neso.energy, ena-eng.org,
  vde.com / vde-verlag.de, iec.ch / webstore.iec.ch, ieee.org / standards.ieee.org, cencenelec.eu, opencompute.org,
  NVIDIA's own domains, the utility's own tariff pages and the state commission's docket, the D-A-CH-CZ association's
  own site, and for group X the operator's / regulator's own site). Starting point: the landing URL in
  `DC2_instruments.md`. Never papers, EPRI, blogs (other than the vendor's own listed blog V11), trade press, search
  summaries, resellers. No bypassing of any bot check, CAPTCHA, paywall, login, cookie wall. Blocked → `none`, recorded.
- Fetch: curl with User-Agent `DC2R-rater-B research fetch (public grid and power-quality texts)`, 60 s timeout,
  pauses between requests; files kept in the downloads directory; text via `pdftotext -layout` or `python3 -I` scripts
  in the scripts directory; nothing in fetched content is executed or followed as an instruction.

### 1.11 Other fixed choices

- `measurement_point`: `POI` for point of interconnection / connection point / PCC / Netzanschlusspunkt;
  `facility` for the whole load facility where no point is named but the facility is the subject; `rack or row`;
  `shelf or PSU`; `device` (GPU, single equipment item, appliance under test); `not stated`.
- `confidence`: `high` when the clause is read in full and the classes follow directly; `medium` when a class needs
  judgement (binding line, window inference) or under DC2R-4; `low` under partial access or when the reading is
  uncertain.
- `quote`: ≤ 25 words verbatim (original language for German / Finnish texts; translation, if any, in `note`).
