# DC2 rater B notes

Rater B, study DC2 (ramp-spec audit). Branch `dc2-rater-b`. Reading date: 2026-11-10 (and following, as logged).
Binding procedure: `DC2_preregistration.md` with §10 (DC2-1, DC2-2) overriding earlier text. Order: `orders.B`.

## 1. Conventions (written before any requirement text is read)

### 1.1 What is a requirement, and how rows are counted (§2)

- A row is **one clause of a listed instrument** that states a **limit** (a number, or a bound with a unit) on:
  - the load's real power or its rate of change in time (ramp, step, swing / oscillation amplitude, smoothing /
    capping response, load change per interval); or
  - a voltage-quality quantity that such variation drives (flicker, rapid voltage change, voltage change), or one of
    the other reported quantities (harmonics, power factor, ride-through, hold-up, other),
  together with whatever window / allowance the clause states. A clause that only asks for a study, a plan, data, a
  model, telemetry or "coordination" without a limit value is not a row. A clause that says "the TSO/ISO may specify
  a limit" without a value is not a row (noted in the instrument note).
- **One clause, one row.** If one clause states several limits on *different quantities* (e.g. a ramp limit and a step
  limit), each quantity is its own row under the same clause, distinguished by `category` (the printed label if any,
  otherwise left blank and the difference stated in `note`). If one clause states the same quantity at several
  categories (e.g. a table by voltage level, by size band), it is **one row per printed category**, with the
  category label as printed in `category`.
- **Tables.** One row per printed category (table row). If a table gives several columns for one category (e.g. Pst
  and Plt), Pst and Plt are different limited indices; I record them as separate rows only if they are separate
  printed categories; otherwise one row per table row with both values in `limit`. Rule I will apply: **one row per
  table row** (the category), values of all columns in `limit`. If a table's rows are voltage levels and columns are
  indices, the category is the row label.
- **Never twice.** A limit restated in two clauses of one instrument is one row under the clause that states the
  number; the other clause goes in `note`.
- **Bare cross-references** ("shall comply with IEEE 519", "as per the Grid Code") are not rows; they go in the
  instrument's `note` in `instruments_B.csv`. A cross-reference that also prints the number is a row of the citing
  instrument.
- Ride-through: a ride-through table is one row per printed table row (the §2 counting rule); a ride-through
  requirement stated as one curve or one sentence is one row.
- Post-fault active-power recovery (a rate or time to restore real power after a disturbance) is a limit on real
  power in time. I classify it as `ride-through` (non-deciding) because it is part of disturbance performance, not
  normal-operation variation, and note "post-fault recovery" in `note`. (The screener's DC2-S14 reading was upheld by
  the reviewer as a citation judgement; I follow it for quantity.)

### 1.2 Deciding set and non-deciding quantities

- `deciding = yes` exactly when `quantity` ∈ {`ramp rate`, `step change`, `swing amplitude`,
  `smoothing or capping response`, `load change per interval`}; otherwise `no`.
- `ramp rate`: a limit stated as power per time (MW/s, MW/min, %/s, %/min) on normal-operation load change.
- `step change`: a limit on an instantaneous or near-instantaneous change in load power (MW or % of rating) with no
  rate unit.
- `swing amplitude`: a limit on the peak-to-peak or amplitude of repeated / oscillatory real-power variation
  (including forced-oscillation amplitude limits in MW or % at a frequency band).
- `smoothing or capping response`: a required response time of a power-smoothing / capping / curtailment function.
- `load change per interval`: a limit on how much load may change over a fixed interval (e.g. "no more than X MW in
  any 10-minute period").
- Voltage-change limits caused by load switching (ΔU/U, d_max, d_c) are `rapid voltage change` (not deciding),
  flicker (Pst/Plt) is `flicker`; harmonics, power factor / reactive power, ride-through, hold-up as named;
  anything else limited (frequency, RoCoF withstand, unbalance, DC output transient voltage deviation) is `other`.

### 1.3 Binding classes and the lines between them

- `mandatory`: a code, protocol, rule, regulation, tariff condition, or connection requirement the connecting load must
  meet ("shall", "must", "is required") in a document the body designates as binding (grid code, protocol, operating
  guide, regulation, tariff, technical requirement document of a TSO/ISO that it applies). An operator's or vendor's
  **specification** that a supplier must meet to sell into it (OCP base spec "shall", OCP power shelf spec) is
  `mandatory`, with `measurement_point` saying where (shelf or PSU / rack or row / device).
- `planning level`: a limit the network operator applies in assessment (planning levels, emission limits derived
  for assessment in IEC TR 61000-3-7, IEEE 1453, EREC P28, D-A-CH-CZ). Where a document says the emission limit
  allocated to the customer is what the customer installation must meet, but the document is an assessment rule of
  network operators, I use `planning level`. Where a grid code itself imposes the planning-level-derived limit as a
  connection condition (e.g. GB Grid Code CC.6.1.7 "shall not exceed"), it is `mandatory`.
- `recommendation`: "should", recommended practice, guideline, informative annex, guide, white paper text with
  "recommended". **"Shall" inside a document the body itself designates as a guideline / reliability guideline /
  recommended practice / implementation guidance is `recommendation`.** An "Industry Recommendation" alert is
  `recommendation`.
- `vendor capability`: a configurable feature or a description of what a product does (GPU power-smoothing ramp
  settings, power-cap ranges, a white paper describing what a rack can do). Not a requirement on anyone.
- A voltage-characteristics standard (EN 50160) describes the supply voltage the network delivers, not a limit on a
  load. If a clause prints a value on a load-driven voltage quantity (flicker Plt, RVC), I record it with
  `binding_class = planning level` only if the text says it is used for planning or assessment; otherwise
  `recommendation`, explained in `note`.
- Default when a binding status is ambiguous: the body's own designation of the document governs (code / rule /
  tariff / connection requirement → `mandatory`; guideline / guide / recommended practice → `recommendation`).

### 1.4 Window classes, the rate-unit rule and the response-time rule

- Window = the measurement / averaging / assessment interval *T*. Classes by §2: `≤ 100 ms` (T ≤ 0.1 s);
  `100 ms – 1 s` (0.1 < T < 1 s); `1 – 60 s` (1 ≤ T ≤ 60 s); `1 – 15 min` (60 s < T ≤ 15 min); `> 15 min`;
  `not stated`. Boundaries: exactly 1 s → `1 – 60 s`; exactly 60 s / 1 min → `1 – 60 s`; exactly 15 min →
  `1 – 15 min`; exactly 100 ms → `≤ 100 ms`.
- Flicker: Pst is assessed over 10 min → `1 – 15 min`; Plt over 2 h → `> 15 min` (when the clause or the referenced
  definition in the same instrument prints those intervals; if the instrument does not print the interval but uses
  Pst/Plt by name, I take the standard definition of Pst = 10 min and Plt = 2 h as the printed meaning of the index and
  write `window_as_printed` as `Pst (10 min)` and note it).
- RVC / voltage change: when the clause states the measurement basis (e.g. half-cycle RMS, 1-cycle RMS, steady state
  after the change), that is the window; otherwise `not stated`.
- **Rate-unit rule (`unit:`).** When a ramp limit prints a rate and no measurement / averaging / assessment interval,
  the time unit of the rate is the window: per second → 1 s (`1 – 60 s`); per minute → 1 min (`1 – 60 s`, since
  exactly 60 s is in that class); per hour → `> 15 min`. `window_as_printed` begins `unit:` (e.g. `unit: MW/min`).
  A step or swing limit with no interval and no rate unit is `not stated`. Every use is logged in §5.
- **Response-time rule (`response:`).** For `smoothing or capping response`, the window is the compliance-assessment
  interval; when only a response time is printed, the window is that response time and `window_as_printed` begins
  `response:`. Every use logged.
- A "load change per interval" limit uses that interval as window.
- Oscillation limits by frequency band: the window is the assessment interval printed; if none, `not stated`.

### 1.5 Allowance classes, the `hard` default, `not stated`

- `hard`: no excursion permitted; **a plain maximum ("shall not exceed", "limited to", "maximum") with no allowance
  clause is `hard`.**
- `tight`: 0 < a ≤ 0.1 % (99.9th percentile or tighter); `loose`: 0.1 % < a ≤ 5 % (95th–99.5th percentile);
  `very loose`: a > 5 %.
- `event count`: a number of exceedances per hour / day / year (e.g. RVC "≤ 1 per hour"), when not convertible
  under DC2-2.
- `not stated`: only when the text says the limit is assessed statistically, "normally", "as far as practicable",
  "typically", or similar, without saying how much exceedance is permitted.
- A percentile stated on another quantity than the limited one does not set the allowance.
- 95 % of week (EN 50160-style) → a = 5 % → `loose`. 99 % → `loose`. 99.9 % → `tight`.

### 1.6 DC2-2 conversion

- When a clause prints **both** a permitted recurrence (frequency, or minimum interval between exceedances) **and** a
  maximum duration of each exceedance: a = duration / recurrence interval; classify by the bands; keep
  `allowance_as_printed`; write the arithmetic in `note` beginning "DC2-2:". Window = printed duration unless an
  assessment interval is stated. If only one of the two is printed, `event count` stays (shape `cannot judge` at
  1–60 s). Every conversion logged in §5.

### 1.7 Shape table (§2) — computed, written in `shape`

| Window | hard / tight | loose / very loose | event count / not stated |
|---|---|---|---|
| ≤ 100 ms, 100 ms – 1 s | electronics | electronics | electronics |
| 1 – 60 s | reactive | history | cannot judge |
| 1 – 15 min, > 15 min | reactive | reactive | reactive |
| not stated | cannot judge | cannot judge | cannot judge |

I write `shape` from this table only, from my own window and allowance classes.

### 1.8 Pending rule (§1) and partial-access rule (§4)

- Pending: a proposal (draft standard, NPRM, revision request not approved, draft tariff, consultation draft,
  recommendation to the Commission not adopted) not adopted by its body on the reading date → `status = pending`,
  no rows, logged `pending: <identifier>, <status as printed>`. Approved-but-not-yet-effective (e.g. approved with a
  future effective date) is **adopted**, so it is rated `in force` and the effective date noted. A document issued by
  a TSO/ISO that says its "new requirements … will be updated into the Market Rules … after stakeholdering" is
  pending as printed.
- Partial access: a row read only from an abstract, preview or the body's own summary page gets `confidence = low`,
  the page in `source_url`; window or allowance not printed there → `not stated` (shape `cannot judge`). Never infer
  a row from a title.

### 1.9 Access states (§3 S2) and allowed routes (§3 S4)

- `full`: requirement text readable from the body's own site; `partial`: only abstract / preview / TOC / catalogue;
  `none`: nothing beyond the title by an allowed route.
- Allowed routes only: ercot.com, nerc.com, pjm.com, puc.texas.gov (+ interchange, ftp), ferc.gov (+ eLibrary),
  eur-lex.europa.eu, entsoe.eu, acer.europa.eu, neso.energy, ena-eng.org, vde.com, vde-verlag.de, iec.ch /
  webstore.iec.ch, ieee.org / standards.ieee.org, cencenelec.eu, opencompute.org, docs/developer.nvidia.com,
  nvidia.com, the utility's own tariff pages and the state commission's docket (aepohio.com, PUCO; dominionenergy.com,
  scc.virginia.gov; georgiapower.com, Georgia PSC), the D-A-CH-CZ association sites, and for group X aeso.ca,
  fingrid.fi, ieso.ca. Never papers, EPRI, blogs, trade press, search result summaries, resellers. No bypassing of
  bot checks, paywalls, logins, cookie walls. Fetch UA `DC2-rater-B research fetch (public grid and power-quality
  texts)`, 60 s timeout, polite pacing. Downloads only in my downloads directory; scripts only in my scripts
  directory; text via `pdftotext -layout` or `python3 -I`.

## 2. Per-instrument remarks

(filled during extraction)

## 3. Blocked routes

(filled during extraction)

## 4. Pending entries

(filled during extraction)

## 5. DC2-2 conversions, rate-unit and response-time rule uses

(filled during extraction)

## 6. Things I could not follow, and what I did instead

(filled during extraction)
