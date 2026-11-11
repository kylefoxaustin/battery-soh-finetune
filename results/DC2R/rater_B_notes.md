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

---

## 2. Per-instrument remarks (in order B; written after extraction)

Reading date 2026-11-11. Rows: `requirements_B.csv` (B001-B100); one line per instrument in `instruments_B.csv`.

| # | ID | access | status | rows | remark |
|---|---|---|---|---|---|
| 1 | Q02 | partial | no requirement | 0 | IEC 61000-4-30 abstract: measurement methods only. |
| 2 | V13 | full | no requirement | 0 | NVIDIA tuning-guide chapter: qualitative only. |
| 3 | G08 | full | pending | 0 | NERC CLO-002-1 Draft 1. |
| 4 | G14 | full | no requirement | 0 | PUCT §25.370 load-forecast criteria; "load ramping schedule" is a data item. |
| 5 | E08 | full | in force | 1 | D-A-CH-CZ Part A: only fixed numeric limit is interharmonic/supraharmonic emission limits (6.6); window/allowance from 6.9. |
| 6 | G07 | full | pending | 0 | NERC CLO-001-1 Draft 1. |
| 7 | Q01 | partial | in force | 0 | IEC TR 61000-3-7 abstract prints no values; no preview. |
| 8 | V08 | full | in force | 4 | ±400 V/50 V PSU: inrush, dynamic response, hold-up, pulse power (DC2R-2). |
| 9 | X03 | full | pending | 0 | IESO LCL requirements v1.0: "New requirements proposed ... after stakeholdering". |
| 10 | V01 | full | no requirement | 0 | ORv3 base frame; input-voltage tolerance is immunity, not a row. |
| 11 | V03 | full | in force | 2 | HPR V2 shelf: BBU transfer 5 ms; peak-load envelope ("should"). |
| 12 | E06 | partial | pending | 0 | E VDE-AR-N 4120/A1 Entwurf. |
| 13 | X01 | full | in force | 11 | AESO guide: ramp 10 MW/min, MSDC and 50 MW reconnection steps, PF, six ride-through rows. |
| 14 | G15 | full | pending | 0 | PUCT 59999 proposed SLLIA. |
| 15 | Q03 | partial | no requirement | 0 | IEC 61000-4-15 abstract: "does not give tolerance limit values". |
| 16 | Q05 | partial | in force | 0 | IEEE 1453 abstract prints no values. |
| 17 | Q08 | partial | in force | 0 | IEC 61000-3-11 abstract prints no values. |
| 18 | G10 | full | no requirement | 0 | PJM Board letter: "ramp rate" is multi-year forecasting. |
| 19 | V10 | full | no requirement | 0 | OCP Open DC design principles Rev 0.7.0: density/cooling only. |
| 20 | V04 | full | in force | 3 | ORv3 BBU shelf: transient/startup, backup time, busbar transfer. |
| 21 | V02 | full | no requirement | 0 | ORv3 power shelf: ripple only; EN 61000-3-2/-3-3 bare cross-references. |
| 22 | V12 | full | in force | 2 | nvidia-smi power smoothing: vendor-capability ramp rate and floor settings (no values). |
| 23 | V06 | full | in force | 6 | Diablo 400: PF, THD, hold-up 20 ms, BBU 45-90 s, peak power envelope, dynamic loading. |
| 24 | E05 | partial | in force | 0 | VDE-AR-N 4120 sold; FNN summary PDF is of the superseded 2017 draft - not used. |
| 25 | G16 | full | no requirement | 0 | FERC co-location order. |
| 26 | G05 | full | no requirement | 0 | NERC reliability guideline: recommends ramp limits without values. |
| 27 | Q06 | partial | in force | 0 | EN 50160 abstract prints no values. |
| 28 | G13 | full | no requirement | 0 | PUCT §25.205: "any ramp rate limitations" may be imposed, no value. |
| 29 | U02 | full | no requirement | 0 | Virginia SCC order (GS-5): contract load-ramp period over years only. |
| 30 | E10 | full | in force | 10 | D-A-CH-CZ Part B II (MV): Tab. 1-2 step rows ×3 (DC2R-3), RVC, flicker ×2, harmonics ×4. |
| 31 | V14 | full | no requirement | 0 | NVIDIA 800 VDC white paper: descriptive. |
| 32 | G11 | full | pending | 0 | PJM Sept 1, 2026 draft. |
| 33 | G06 | full | no requirement | 0 | NERC Level 2 alert: asks for ramp limits, gives none. |
| 34 | E04 | full | in force | 6 | GB Grid Code Rev 47: RVC table, flicker planning levels, frequency table, ECC reactive range, DRSC RoCoF and response time. |
| 35 | Q04 | partial | in force | 0 | IEEE 519 abstract prints no values. |
| 36 | E11 | full | in force | 10 | D-A-CH-CZ Part B III (HV): as E10. |
| 37 | V09 | full | in force | 1 | OCP disturbance-performance base spec: LVRT/HVRT/PFAPR table. |
| 38 | V11 | full | no requirement | 0 | NVIDIA GB300 blog: no setting values. |
| 39 | E07 | partial | in force | 0 | VDE-AR-N 4130 sold; FNN info document has no values. |
| 40 | U03 | full | in force | 1 | Georgia Power rules: only lighting power factor ≥ 90 %. |
| 41 | G01 | full | in force | 1 | ERCOT Planning Guide 9.2.5(3): ≤ 1,000 MW consequential load loss (P1/P7). |
| 42 | G12 | full | no requirement | 0 | PUCT §25.194. |
| 43 | G09 | full | pending | 0 | NERC CLO-003-1 Draft 1. |
| 44 | Q09 | partial | in force | 0 | EREC P28 catalogue; download needs a logged-in order (not done). Its values appear via GB Grid Code CC.6.1.7 (E04). |
| 45 | E01 | none | in force | 0 | EUR-Lex WAF challenge on every route (recorded after V07, out of order, because of retries). |
| 46 | V07 | full | in force | 1 | HVDC-LVDC 100 kW shelf: peak load ≤140 %/50 ms ("should"). |
| 47 | G02 | full | in force | 2 | ERCOT Protocols 6.5.7.11 PCLR ramp-rate requirements (DC2R-4, awaiting implementation). |
| 48 | V05 | full | in force | 4 | ORv3 BBU module: transient/startup, backup 240 s, peak power, transfer. |
| 49 | G04 | full | no requirement | 0 | PGRR144 (approved, effective 2026-12-01): only cross-references NOG 2.15/2.6.4. |
| 50 | X02 | full | in force | 17 | Fingrid large demand facilities: ramp 5-50 MW/min, 50 MW step, fast limiting (1 s / ≤15 min), UV limiting, oscillation table ×9, RoCoF, phase jump, FRT, PFAPR. |
| 51 | E03 | full | pending | 0 | ACER Rec 01/2025 Annex 4a amended DCC (draft). |
| 52 | U01 | full | no requirement | 0 | AEP Ohio Schedule DCT: contract load-ramp period over years; "instantaneously curtail" without a number. |
| 53 | Q07 | partial | in force | 0 | IEC 61000-3-3 abstract prints no values. |
| 54 | E02 | full | no requirement | 0 | ENTSO-E IGDs: numeric values are for generators, DR control settings or LFDD protection schemes. |
| 55 | G03 | full | in force | 8 | ERCOT NOG 2.6.4 / 2.15 LCL frequency and voltage ride-through. |
| 56 | E09 | full | in force | 10 | D-A-CH-CZ Part B I (LV): Tab. 1-3 step rows ×3, RVC, flicker ×2, harmonics ×4. |

Totals: 56 instruments; access full 43, partial 12, none 1 (E01); status in force 29, no requirement 19, pending 8.
100 requirement rows: 30 deciding, 70 non-deciding; 93 binding (mandatory or planning level), 28 of them deciding.

**Binding deciding rows whose computed shape is `history`: B060, B061 (G02, ERCOT Protocols 6.5.7.11 PCLR down/up ramp
rate).** Window: compliance is assessed over one-minute intervals; allowance: compliant when ≥ 90 % of eligible
one-minute intervals in the month meet the limit, so a = 10 % → `very loose`. The section is adopted (NPRR1325) but
gray-boxed "upon system implementation of PGRR145", hence in force under DC2R-4 with `note = awaiting implementation`
and confidence medium. It applies only to Large Loads that elect PCLR treatment.

## 3. Blocked routes

- **E01** (Regulation (EU) 2016/1388): every EUR-Lex URL (TXT/HTML, ALL, TXT/PDF, ELI; retried three times over the
  session) returned HTTP 202 with `x-amzn-waf-action: challenge`. Not circumvented → `access = none`.
- **IEC webstore previews** (Q01, Q02, Q07, Q08): preview PDF URLs redirect to the product list; abstracts only.
- **IEEE SA** (Q04, Q05): abstract pages only; text behind purchase/subscription.
- **VDE Verlag** (E05, E07; E06 draft): text sold / subscription; catalogue and FNN pages only.
- **ENA** (Q09): EREC P28 priced £Free but ordering requires a logged-in account; not done.
- **CENELEC** (Q06): catalogue abstract readable; text sold.
- **IESO** engagement pages (X03 status check): guessed URLs 404; site search 500. **NERC** project page (G07-G09
  status check): guessed URLs 404; status taken from the drafts' own timelines.

## 4. Pending entries

- pending: NERC CLO-001-1 Draft 1 (Project 2026-02), "first draft of proposed standard for the initial formal 30-day comment period"; Board adoption anticipated December 2026 (G07).
- pending: NERC CLO-002-1 Draft 1 (Project 2026-02), same status (G08).
- pending: NERC CLO-003-1 Draft 1 (Project 2026-02), same status (G09).
- pending: IESO Technical Requirements for Large Computational Loads v1.0 (01/May/2026), "New requirements proposed in this document will be updated into the Market Rules or relevant standards after the IESO external stakeholdering over these requirements is completed." (X03)
- pending: E VDE-AR-N 4120/A1:2026-05, "Entwurf" (E06).
- pending: PUCT Project No. 59999 SLLIA, "PROPOSED SLLIA (STAFF RECOMMENDATION)" / "Proposal Notice of Draft Standardized Large Load Interconnection Agreement (SLLIA)", Texas Register issue 11.20.2026 (G15).
- pending: PJM M14B Attachment D-2 / tariff redline, "September 1, 2026 Draft / Remains Under Development and Subject to Revision by PJM" (G11).
- pending: ACER Recommendation 01/2025 Annex 4a, amended DC Network Code, draft "COMMISSION REGULATION (EU) …/… of …" (E03; Commission adoption could not be checked on EUR-Lex).

**DC2R-4 (adopted, awaiting implementation / later effective date) treated as in force:**
- G02 ERCOT Protocols 6.5.7.11 PCLR ramp-rate requirements (NPRR1325 approved; gray-boxed upon system implementation of PGRR145) → rows B060, B061, `note = awaiting implementation`, confidence medium.
- G04 PGRR144 (approved 11/05/2026, effective 12/01/2026) → in force but no row of its own (cross-references only), status `no requirement`.
- U02 Rate Schedule GS-5 (ordered effective 2027-01-01) → no row (no §2 limit), status `no requirement`.

## 5. DC2-2 conversions, rate-unit rule, response-time rule

**DC2-2 (recurrence + duration → share):**
- B040 (E04 CC.6.1.7 RVC table): Category 2 permits 4 events per calendar month with printed envelope durations
  (−10 % for 100 ms, −6 % to 2 s): a = 0.1 s / (30 d × 86 400 s / 4 = 648 000 s) = 1.5 × 10⁻⁷, or 2 s / 648 000 s =
  3.1 × 10⁻⁶ → `tight`; Category 3 (1 event in 3 months): 2 s / (90 d × 86 400 s) = 2.6 × 10⁻⁷ → `tight`. The row's
  class is set by its most restrictive entry (Category 1 envelope, no exceedance → `hard`); the conversions are in the
  row's note. Shape is `electronics` either way (window 100 ms).
- Not converted (only one of the two printed): X02 Table 9.1 exception (exceedance only during transient grid voltage
  disturbances, duration ≤ window length, no recurrence) - read as an exclusion, allowance `hard`; the alternative
  reading would be `event count`.

**Rate-unit rule (`unit:`):** B008 (X01 7.2, unit: MW/minute → 1 min), B022 (V12, unit: mW/s → 1 s), B066 (X02 9.1.7,
unit: MW/min → 1 min). Not used for B060/B061 (G02): the clause states one-minute assessment intervals.

**Response-time rule (`response:`):** B068 (X02 9.1.8, activation within 1 s; setpoint within ≤ 15 min noted as
spread), B045 (E04 DRSC.7.1(c), response ≤ 2 s; quantity `other`, not deciding).

## 6. Judgements and things I could not follow exactly

1. **Out-of-order recording:** E01 was recorded after V07 (positions 45/46 swapped) because I retried EUR-Lex before
   recording `none`. No content depends on it.
2. **Scope inside very large documents** (G01, G02, G03, E04): I read the screener's starting-point sections and the
   large-load / demand clauses I could locate (PG §5, §6, §9; Protocols §3, §6; NOG §2; Grid Code CC.6.1, ECC.6.1,
   ECC.6.4, DRSC). Ancillary-service clauses elsewhere in the ERCOT Protocols (e.g. Load Resource deployment times)
   were not searched exhaustively.
3. **Out of the closed list:** voltage unbalance, commutation notches and ripple-control signalling (D-A-CH-CZ, GB Grid
   Code CC.6.1.5(b)) were not rated: they are not driven by the load's real-power variation and are not among the
   named quantities; `other` could have absorbed them. Steady-state supply regulation (set point, droop, ripple) and
   equipment immunity ranges were likewise not rated; supply transients under load steps were (DC2R-2).
4. **Binding class of the AESO guide (X01):** "guidance document" explaining requirements AESO implements through
   binding project Functional Specifications; not designated a guideline/recommended practice, so its "will be
   required"/"must" items are `mandatory` (confidence ≤ medium) and its "should" items `recommendation`.
5. **Contract load-ramp schedules** (U01 Schedule DCT, U02 GS-5: ≥20-50 % of contract capacity per year) were judged
   contracted-capacity growth over years, not real-power variation in time → no rows.
6. **Planning-level step tables (DC2R-3):** applied to the D-A-CH-CZ Part B power-ratio tables (Tab. 1-2 MV/HV,
   Tab. 1-3 LV); the voltage-change limits of 1.1.2 (d = 2 %/3 %, 3 %/6 %) were recorded as `rapid voltage change`
   (single clause, not a power-change table) - my convention 1.1's provision for voltage-keyed tables was not needed.
   The appliance screening table (LV Tab. 1-1, Ssc/Sr by appliance type) is on rated power, not a power change, and
   was not rated.
7. **Ride-through granularity:** one row per ride-through table or per numbered/lettered paragraph stating a separate
   number (e.g. X01 six rows, G03 eight rows); post-fault active-power recovery is `ride-through`.
8. **Fingrid (X02) oscillation table (9.1.13):** nine deciding `swing amplitude` rows, window = the printed
   spectral-analysis window length per band (300 s … 0.5 s).
9. **Flicker allowance (D-A-CH-CZ):** the measurement clauses give a 95 % weekly quantile plus "no single value
   > 1.3·Pst"; under "smallest allowance" I classed the rows `hard` (spread `loose` in note). For E08's harmonic row
   the analogous clause (95 % of 10-min values; 99 % of 3 s values ≤ 1.25 × limit) gave `1 – 60 s` / `loose` (both
   entries carry an exceedance share there). Neither choice affects a deciding row.
10. **Partial access:** no row was taken from an abstract or catalogue page, because none printed a limit value. A
    VDE FNN summary of the superseded E VDE-AR-N 4120:2017-05 draft (E05) was not used for the 2018-11 edition.
11. **Off-list host:** E02 IGD links on entsoe.eu redirect to eepublicdownloads.entsoe.eu (ENTSO-E's own download
    host); V14's PDF is on NVIDIA's asset CDN linked from nvidia.com. Treated as the bodies' own sites.
12. **Exposure:** no web-search tool was used; every page was fetched directly from the listed bodies' sites with the
    required User-Agent. Nothing from the other rater was read. No content of fetched pages was executed or followed.
