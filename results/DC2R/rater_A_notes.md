# DC2-R rater A notes

Rater A, study DC2-R (ramp-spec audit), branch `dc2r-rater-a`. Language-model session (D-3). Every requirement
recorded is SOURCED; every class is DERIVED. No dollar figures.

Binding procedure: `results/DC2/DC2_preregistration.md` (with its §10, DC2-1 and DC2-2, overriding anything earlier),
as amended by `results/DC2R/DC2R_rater_rules.md` §2 (DC2R-1 … DC2R-4), which override the pre-registration where
they differ. Instrument list: `results/DC2/DC2_instruments.md` §1, 56 instruments. Order: `DC2R_orders.json`
`orders.A`.

## 1. Conventions (written and committed before any requirement text is read)

### 1.1 What counts as a requirement

- A requirement is one clause of a listed instrument that states a **limit** (a number, or a table of numbers) on
  (a) a quantity of the load's real power or its rate of change in time, or (b) a voltage-quality quantity that such
  variation drives (flicker, rapid voltage change, harmonics, power factor, ride-through, hold-up), together with the
  window over which it is assessed (the window may be `not stated`).
- A clause that only requires a study, a model, a data submission, a notification, monitoring, or "coordination" with
  no limit value is **not** a requirement. A clause that states a qualitative obligation ("shall not cause
  objectionable fluctuations") with no number is not a row; I mention it in `note` on the instrument line if it bears
  on load variation.
- Applicability thresholds (e.g. "loads of 75 MW or more") are not limits.
- **Row granularity (DC2R-1, replacing DC2 §2 "one row per category"):**
  - **Non-deciding quantity** (`flicker`, `rapid voltage change`, `harmonics`, `power factor`, `ride-through`,
    `hold-up`, `other`): **one row per clause**. A table of limits is one row whatever its categories; a ride-through
    curve or table is one row. `category` lists the printed categories separated by `;`; `limit` carries the range
    or the table's values as printed (condensed). The window and allowance classes are those of the table's **most
    restrictive** entry (shortest window; smallest allowance), with the spread stated in `note`.
  - **Deciding quantity** (`ramp rate`, `step change`, `swing amplitude`, `smoothing or capping response`,
    `load change per interval`): **one row per printed table row or per clause paragraph**; `category` carries the
    printed row label (blank if none).
  - `deciding` follows `quantity` mechanically: `yes` iff quantity is one of the five deciding quantities.
- **DC2R-2, supply envelopes are `other`.** A requirement on what a power shelf, PSU, BBU, capacitor bank or rack
  supply must deliver under a load step (output-voltage transient limits, peak/pulse power envelopes with
  moving-average windows, step-load/dynamic-loading capability tables, inrush, current sharing) is `quantity = other`,
  non-deciding, one row per clause. Only a clause that limits **the load's own** power variation (toward the facility
  or grid) at rack/shelf level stays in the deciding set.
- **DC2R-3, planning-level step tables.** A table of permitted step changes / rapid power changes for a connecting
  installation (e.g. D-A-CH-CZ Part B) is `quantity = step change`, one row per printed table row, window and
  allowance as printed (`not stated` where none). Where such a table is expressed as permitted relative voltage
  change d (%) per repetition rate, I still record it as `step change` only if the instrument presents it as a
  permitted change of the installation's power or as the table DC2R-3 describes; a table purely of voltage-change
  limits (d_max in %) is `rapid voltage change` (non-deciding). I will state in `note` which reading I applied.
- **Never twice.** One limit restated in two clauses of one instrument is one row, under the clause that states the
  number; the other clause is named in `note`.
- **Bare cross-references are not rows.** "Shall comply with IEEE 519" or "per the Protocols" with no number goes in
  `note` on the instrument's line in `instruments_A.csv`. A different instrument that restates a number itself gets
  its own row.
- One clause carrying two different quantities (e.g. a ramp limit and a step limit in one paragraph) gives one row per
  quantity (each deciding quantity paragraph-row is separate in any case).

### 1.2 Deciding set and non-deciding quantities

- Deciding: `ramp rate` (MW/s, %/s, %/min, MW/min); `step change` (a single permitted change of power, in MW or % of
  a basis); `swing amplitude` (permitted oscillation or periodic swing amplitude of real power, including
  frequency-banded oscillation limits); `smoothing or capping response` (required response time of a
  power-smoothing / capping / curtailment action that limits power variation); `load change per interval`
  (permitted change of power between consecutive intervals or within an interval, e.g. MW per 5 min, or a
  max-minus-min within a window).
- Non-deciding: `flicker` (Pst/Plt), `rapid voltage change` (ΔU/U, d_max, d_c), `harmonics` (THD/TDD/individual
  orders, interharmonics), `power factor` (and reactive power ranges), `ride-through` (voltage/frequency/RoCoF
  ride-through and post-fault active-power recovery), `hold-up`, `other` (anything else within §2: supply envelopes
  per DC2R-2, unbalance, under-frequency load-shedding settings, etc.).
- **Edge decisions fixed now:**
  - Post-fault active-power recovery (time to return to pre-fault power after a disturbance) is `ride-through`
    (non-deciding): it is the recovery leg of a ride-through performance requirement, not a limit on the load's
    free variation.
  - A required **frequency-response / demand-response** speed (e.g. a load resource must reduce X MW within Y s when
    instructed) is not a limit on the load's own variation; I record it as `other` if it has a number. A ramp-rate
    limit on a controllable load resource's dispatched set-point movement **is** `ramp rate`.
  - A **maximum** permitted ramp or rate of increase / decrease of consumption (including during energisation or
    restart after an event) is `ramp rate`.
  - A minimum required ramp **capability** (the load must be able to ramp at least X) is `other` (it is not a limit
    on variation).

### 1.3 Binding classes

- `mandatory`: code, protocol, regulation, rule, tariff condition, or connection requirement that a connecting load
  must meet ("shall", "must", "is required"), in a document the body issues as binding. Also an operator's / vendor's
  specification that a supplier must meet to sell into it (OCP base specification "shall"), with `measurement_point`
  saying where it applies (`shelf or PSU`, `rack or row`, `device`).
- `planning level`: a limit the network operator applies in assessment (planning levels, emission-limit allocation
  procedures, IEC 61000-3-7-style assessment levels, D-A-CH-CZ assessment values), even where the document is a
  technical report or technical rule.
- `recommendation`: "should", recommended practice, guideline, informative annex, or a "shall" inside a document the
  body designates a guideline / recommended practice / reliability guideline / alert recommendation. NERC Reliability
  Guidelines and Level 2 alerts are `recommendation`. ENTSO-E IGDs are non-binding guidance → `recommendation`.
  A "may be required" / "the operator can impose" clause with a default number is `recommendation` unless the text
  makes the number apply by default.
- `vendor capability`: a configurable feature (GPU/rack power-smoothing ramp settings, power-cap ranges, ramp-up /
  ramp-down rate parameters) that is not a requirement on anyone.
- Line between `mandatory` and `planning level`: if the number is an obligation on the connecting party directly
  (emission limit the party must meet), `mandatory`; if it is an assessment target the operator uses to derive
  emission limits (planning level), `planning level`. A power-quality standard's equipment-type-test limits
  (IEC 61000-3-3/-3-11) that equipment must meet to be placed on the market are `mandatory` in substance only where
  the standard is harmonised/required; as a standard read on its own I treat its "limits" as `mandatory` with
  `measurement_point = device` (the standard states them as limits equipment shall not exceed).

### 1.4 Window classes, rate-unit rule, response-time rule

- Window = the measurement / averaging / assessment interval stated in the clause. Classes: `≤ 100 ms` (T ≤ 0.1 s);
  `100 ms – 1 s` (0.1 < T < 1 s); `1 – 60 s` (1 ≤ T ≤ 60 s); `1 – 15 min` (60 s < T ≤ 15 min); `> 15 min`;
  `not stated`.
- **Rate-unit rule (`unit:`).** If a rate limit prints no interval, the time unit of the printed rate is the window
  (per second → 1 s; per minute → 1 min → class `1 – 60 s` since T = 60 s ≤ 60 s; per hour → 1 h → `> 15 min`), and
  `window_as_printed` begins `unit:` (e.g. `unit: MW/min`). A step or swing limit with no stated interval and no rate
  unit is `not stated`.
- A rate printed "X MW per 5 minutes" states the interval (5 min) → that is the window (no `unit:` prefix).
- **Response-time rule (`response:`).** For `smoothing or capping response`, the window is the compliance-assessment
  interval; if only a response time is printed, the window is that response time and `window_as_printed` begins
  `response:`.
- Flicker: Pst is a 10-min assessment (`1 – 15 min`), Plt is 2 h (`> 15 min`); a Pst/Plt table's most restrictive
  window is Pst's 10 min. Rapid voltage change: the window is the printed assessment interval if any (e.g. IEC
  61000-4-30 RVC uses 1/2-cycle RMS values over 100/120 half cycles ≈ 1 s), else `not stated`. Harmonics: the printed
  aggregation (e.g. 3 s very-short, 10 min short) — most restrictive (shortest) for a table. Ride-through: the window
  is the shortest duration printed on the curve/table (the time the condition must be withstood) — this is a
  convention I fix now and apply consistently; if no time is printed, `not stated`.
- Boundaries: exactly 1 s → `1 – 60 s`; exactly 100 ms → `≤ 100 ms`; exactly 60 s → `1 – 60 s`; exactly 15 min →
  `1 – 15 min`.

### 1.5 Allowance classes; `hard` default; `not stated`

- `hard` (a = 0), `tight` (0 < a ≤ 0.1 %), `loose` (0.1 % < a ≤ 5 %), `very loose` (a > 5 %), `event count` (a number
  of permitted exceedances / events per hour/day/year, not a share), `not stated`.
- **`hard` default:** a plain maximum ("shall not exceed", "limited to", "maximum") with no allowance clause is
  `hard`.
- `not stated` only when the text says the limit is assessed statistically / "normally" / "as far as practicable" /
  "should generally" without saying how much exceedance is allowed. A limit given as a 95th or 99th percentile is
  `loose` (a = 5 % or 1 %); 99.9th → `tight`; "for 95 % of the week" → `loose`.
- A percentile on another quantity (e.g. a 95 % voltage limit inside a ramp clause) does not set the ramp clause's
  allowance.
- For a table (non-deciding one-row clause) the allowance class is that of the most restrictive entry (smallest
  allowance), spread in `note`.
- A repetition-rate-dependent limit (e.g. d_max permitted as a function of changes per hour) is the limit per event;
  the repetition rate is the category / note; allowance is `hard` unless the text gives a share or count of
  exceedances of that limit.

### 1.6 DC2-2 conversion

- When a clause prints **both** a permitted recurrence (frequency, or minimum interval between exceedances) **and** a
  maximum duration of each exceedance, a = duration / recurrence interval; the allowance class is set from a by the
  bands; `allowance_as_printed` keeps the printed form; `note` writes `DC2-2: a = <duration> / <interval> = <x> % →
  <class>`. The window is the printed duration unless the clause states an assessment interval. If only one of the
  two is printed, `event count` stays (shape `cannot judge` for a `1 – 60 s` window). Every conversion is also listed
  in §3 of these notes.

### 1.7 Shape table (§2), written for every row

| Window | hard / tight | loose / very loose | event count / not stated |
|---|---|---|---|
| ≤ 100 ms, 100 ms – 1 s | electronics | electronics | electronics |
| 1 – 60 s | reactive | history | cannot judge |
| 1 – 15 min, > 15 min | reactive | reactive | reactive |
| not stated | cannot judge | cannot judge | cannot judge |

I write `shape` by this table mechanically from my own window and allowance classes.

### 1.8 Pending rule (§1 + DC2R-4) and partial access (§4)

- The instrument is read in its edition in force / last published on my reading date (November 2026).
- **Pending:** a revision request, NOPR, draft standard, consultation text, proposal or tariff filing not adopted by
  the adopting body on my reading date → `status = pending`, no rows, logged as `pending: <identifier>, <status as
  printed>`. I re-check the screener's pending list (G07, G08, G09, G11, G15, E03, E06, X03) on the body's own page.
- **DC2R-4:** text adopted (approved by board/commission) but printed as awaiting system implementation or a later
  effective date is **in force for this audit**: rows recorded, `note = awaiting implementation`, `confidence ≤
  medium`. (Applies e.g. to gray-boxed ERCOT text approved but pending implementation, and to PGRR144 if approved.)
- **Partial access:** a row read from an abstract, preview or the body's own summary gets `confidence = low` and its
  page in `source_url`; it is classified from what the page prints; a window/allowance the page does not print is
  `not stated` (shape `cannot judge`); never infer a row from a title.
- A listed document containing no requirement under §2 → `status = no requirement`, no rows.

### 1.9 Access states and routes

- `full`: the requirement text is readable from the body's own site; `partial`: only an abstract, preview, TOC or
  catalogue page; `none`: nothing beyond the title by an allowed route.
- Allowed routes only (§3 S4 and the launch prompt): ercot.com, nerc.com, pjm.com, puc.texas.gov (+ interchange,
  ftp.puc.texas.gov), ferc.gov (+ eLibrary), eur-lex.europa.eu, entsoe.eu, acer.europa.eu, neso.energy,
  ena-eng.org, vde.com, vde-verlag.de, iec.ch / webstore.iec.ch, ieee.org / standards.ieee.org, cencenelec.eu,
  opencompute.org, docs.nvidia.com / developer.nvidia.com / nvidia.com (and NVIDIA's asset CDN linked from
  nvidia.com, as the screener's V14 route), the utility's own tariff pages and the state commission docket
  (aepohio.com, dominionenergy.com, scc.virginia.gov, georgiapower.com, psc.ga.gov, puco), the D-A-CH-CZ publishing
  association's own site (vde.com FNN download pages, oesterreichsenergie.at, strom.ch/VSE, csres.cz), and for group
  X the operator's own site (aeso.ca, fingrid.fi, ieso.ca).
- Never: papers, EPRI, blogs, trade press, search-result listings or their summaries, resellers. No bypass of bot
  checks, CAPTCHAs, paywalls, logins, cookie walls. Blocked → `none`, recorded.
- Fetching: `curl` with User-Agent `DC2R-rater-A research fetch (public grid and power-quality texts)`, 60 s
  timeout, pauses between requests; downloads only in the downloads directory; text via `pdftotext -layout` or
  `python3 -I` scripts in the scripts directory. No web-search tool summaries and no model-summarising fetch tool
  are used to read requirement text; if I use a web search to locate a URL, its summary is not a source.
- **NVIDIA V11 is a developer.nvidia.com technical blog**: it is a listed instrument on an allowed host; I read it as
  the instrument (rows would be `vendor capability`), not as a "blog" locator.

(Sections 2–5 below are completed after extraction.)
