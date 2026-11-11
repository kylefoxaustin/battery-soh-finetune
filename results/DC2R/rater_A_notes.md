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

## 2. Per-instrument remarks (in rating order, reading date 2026-11-11)

- V03: full; 2 rows (5.6 peak-load envelope other/recommendation; 5.5.1 BBU 5 ms hold-up). EMC standards bare refs.
- E06: pending (Entwurf, consultation closed 10 May 2026); partial (VDE announcement page only).
- E10: full; 10 first-pass rows: RVC 1.1.2, three DC2R-3 step rows (Tab. 1-2, window not stated), flicker planning+emission (allowance 95 % weekly from 1.3.5), harmonics x4. Plus 2 unbalance rows (other) added later (§5). Commutation notches, signal voltages, slow voltage change (generation) excluded.
- Q01: partial (abstract only; preview PDF 403); abstract has no number -> 0 rows.
- Q03: partial; abstract says no tolerance limit values -> no requirement.
- E02: full (14 IGDs); no requirement: restatements by reference of DCC, generator RoCoF recommendations, DR SFC settings.
- Q04: partial (abstract, no numbers) -> 0 rows.
- E05: partial (VDE FNN page + FAQ); 1 low-confidence RVC row from FAQ (Δu_Bezug 0,5 %).
- E01: none - EUR-Lex AWS WAF challenge (HTTP 202, x-amzn-waf-action: challenge) on 5 routes incl. retry; not bypassed.
- X02: full; 16 rows: ramp 5-50 MW/min selectable (medium), 50 MW step, 9 oscillation bands (Taulukko 9.1, STFT windows), fast limitation (other), RoCoF, angle jump, FRT, PFAPR.
- E08: full; Teil A methods; 1 row (6.6 interharmonic/supraharmonic voltage emission limits, 6.9 statistics 3 s 99 % -> 1-60 s loose; non-deciding).
- E07: partial (VDE FNN pages + NRW Info Mar 2026, no numbers) -> 0 rows.
- V05: full; 3 rows (Table 2 transient response other; startup/transition/backup hold-up; 4.3.1 peak envelope other).
- Q02: partial; measurement-method standard -> no requirement.
- E04: full (Rev 47); 6 rows: CC.6.1.3 freq withstand, CC.6.1.7 RVC (planning level; Cat 1 envelope), flicker planning levels (allowance not stated), ECC.6.4.5.1 PF, BC1.A.1.1 PN ramp limits x2 (50/40 MW/min, medium).
- U01: full; no requirement (billing terms; qualitative no-cycling attestation; bare cross-ref).
- E09: full; 9 first-pass rows: RVC, Tab. 1-3 step x3 (DC2R-3), flicker x2, harmonics x3. Tab. 1-1 device screening ratios excluded (judgement). Plus 1 unbalance row (other) added later (§5).
- V08: full; 4 rows (dynamic response other; hold-up 6 ms; pulse envelope other/recommendation; inrush other).
- V06: full; 6 rows (PF, THD, hold-up 20 ms, BBU 45-90 s, Table 5 peak envelope other, dynamic loading other).
- E11: full; 10 first-pass rows (RVC 2 %, Tab. 1-2 step x3, flicker x2, harmonics x4) plus 2 unbalance rows (other) added later (§5).
- G05: full; no requirement (recommends ramp limits without numbers).
- G08: pending (CLO-002-1 Draft 1; Board adoption anticipated Dec 2026).
- V10: full; no requirement (layout/density only in Rev 0.7.0).
- G14: full; no requirement (ramping schedule is data for forecasts).
- U02: partial (order full; GS-5 schedule PDF not on Dominion site); 0 rows (billing terms only).
- V11: full; no requirement (feature description, no setting values).
- V12: full; 2 vendor-capability rows (ramp up/down rate mW/s; TMP floor), no numeric values printed.
- G11: pending (PJM LCL ride-through draft; Oct 6 PC informational, proposed).
- E03: pending (ACER Rec 01/2025 draft regulation).
- G03: full (OG Section 2, Nov 1 2026); 7 rows: LCL freq RT table, freq recovery, voltage RT table, 6 sags/90 s, AS capability x3 (other).
- G01: full; no requirement (Section 9: processes and level caps).
- G07: pending (CLO-001-1 Draft 1).
- Q06: partial (abstract, no numbers) -> 0 rows.
- V02: full; no requirement (ripple steady-state, bare refs).
- V13: full; no requirement (prose only).
- G12: full; no requirement.
- G06: full; no requirement (recommends ramp limits; questionnaire).
- G15: pending (proposed SLLIA, staff recommendation 11/5/2026).
- V09: full; 1 row (Table 1 VRT/PFAPR, mandatory per OCP convention, medium). Ramp/oscillation limits deferred to future spec.
- Q08: partial (abstract, no numbers) -> 0 rows.
- Q07: partial (abstract, no numbers) -> 0 rows.
- G13: full; no requirement (commission may impose ramp limits, no number).
- G02: full; 2 rows: 6.5.7.11 PCLR ramp (down 10-20 %/min, up ≤20 %/min), one-minute intervals, 90 % compliance -> very loose -> history shape; awaiting implementation (DC2R-4), medium.
- Q09: partial (ENA catalogue; free download needs login, not done) -> 0 rows.
- V14: full; no requirement (white paper).
- G16: full; no requirement.
- V04: full; 2 rows (transient response other; startup/backup/transition hold-up).
- G09: pending (CLO-003-1 Draft 1).
- G10: full; no requirement.
- Q05: partial (abstract, no numbers) -> 0 rows.
- X01: full; 10 rows: PF, VRT table, recovery (rec), TOV, FRT, RoCoF, phase jump, V/Hz, ramp 10 MW/min (recommendation: 'may be required'), 50 MW reconnection step (low).
- V01: full; no requirement.
- G04: full; approved 11/05/2026, effective Dec 1 (DC2R-4 in force) but no requirement of its own (modeling/tests; cross-ref to OG 2.15).
- V07: full; 1 row (peak load envelope, other/recommendation).
- U03: full; 1 row (PF ≥90 % lagging for low-PF lighting >250 W); large-load clauses are commercial.
- X03: pending (IESO LCL requirements v1.0, proposed pending stakeholdering).

## 3. Blocked routes, pending entries, DC2-2, rate-unit and response-time uses

### 3.1 Blocked routes (not bypassed)

- **E01** (Regulation (EU) 2016/1388): every EUR-Lex route (TXT/HTML consolidated, TXT/PDF, ALL, TXT, ELI) returned
  HTTP 202 with `x-amzn-waf-action: challenge` and an empty body, also after a pause. This is a bot check; not
  circumvented. Access `none`.
- **IEC previews** (Q01): preview.iec.ch returned 403 (CloudFront); not retried for Q03, Q07, Q08. IEC/IEEE/CENELEC
  texts read from abstracts only (Q01-Q08 partial).
- **Q09** (ENA EREC P28): the catalogue lists the document as free, but ordering/downloading requires a registered
  login; not done (partial).
- **E05/E06/E07** (VDE-AR-N 4120/4130): full texts are sold by VDE Verlag; only VDE FNN pages read (partial).
- **U02**: the GS-5 schedule PDF is not on Dominion's Virginia tariff page (GS-1 to GS-4 only); order read in full.
- NERC Project 2026-02 project page: guessed URLs returned 404; status taken from the drafts' own timelines.
- IESO LCL engagement page: guessed URL returned 404; status taken from the document's own text.

### 3.2 Pending entries (§1 with DC2R-4)

- pending: E VDE-AR-N 4120/A1:2026-05 (E06), "Entwurf" (consultation ended 10 May 2026).
- pending: ACER Recommendation 01/2025 Annex 4a amended DC Network Code (E03), draft "COMMISSION REGULATION (EU) …/…".
- pending: NERC CLO-001-1 Draft 1 (G07), "first draft of proposed standard for the initial formal 30-day comment period".
- pending: NERC CLO-002-1 Draft 1 (G08), same; Board adoption anticipated December 2026.
- pending: NERC CLO-003-1 Draft 1 (G09), same.
- pending: PJM LCL ride-through tariff/manual revisions (G11), "September 1, 2026 Draft / Remains Under Development and
  Subject to Revision by PJM"; 6 Oct 2026 PC item informational ("proposed requirements").
- pending: PUCT Project No. 59999 proposed SLLIA (G15), "PROPOSED SLLIA (STAFF RECOMMENDATION)" / "Proposal Notice of
  Draft Standardized Large Load Interconnection Agreement".
- pending: IESO Technical Requirements for Large Computational Loads v1.0 (X03), "New requirements proposed in this
  document will be updated into the Market Rules ... after the IESO external stakeholdering ... is completed".
- **DC2R-4 applied (in force, awaiting implementation):** G02 Protocols 6.5.7.11 PCLR ramp-rate requirements
  (NPRR1325 gray box, "upon system implementation of PGRR145") - rows A079, A080 with `confidence = medium` and
  "awaiting implementation" in `note`. G04 (PGRR144, approved 11/05/2026, effective 1 Dec 2026) treated as in force but
  contains no requirement of its own (status `no requirement`). G01 9.6.1(2)-(3) (PGRR145 gray box) contain no limit.

### 3.3 DC2-2 conversions

- **None made.** No clause printed both a recurrence and a per-exceedance duration for the limited quantity.
  - E04 CC.6.1.7: Category 2/3 RVC counts (4 per month; 1 per 3 months) are numbers of permitted larger events with an
    envelope, not exceedances of the row's (most restrictive, Category 1) limit; allowance taken from Category 1
    (`hard`).
  - X02 Taulukko 9.1: exceedance allowed only when caused by a grid voltage disturbance, for at most the window length
    per disturbance - a duration without a recurrence; treated as a scope exemption, allowance `hard`.
  - G02 6.5.7.11(4): the allowance is printed directly as a share (90 % of one-minute intervals must comply,
    a = 10 %) -> `very loose`; no conversion needed.

### 3.4 Rate-unit rule (`unit:`) uses

- A014 (X02 9.1.7, MW/min -> 1 min), A038-A039 (E04 BC1.A.1.1, "MW per minute" -> 1 min), A069 (V12 ramp rates,
  mW/s -> 1 s), A091 (X01 7.2, MW/minute -> 1 min).
- Not used for G02 6.5.7.11: paragraph (4) states one-minute assessment intervals, so the stated interval is the
  window (`window_as_printed` without `unit:`). Under the STATED sensitivity these rows keep their window.

### 3.5 Response-time rule (`response:`) uses

- A025 (X02 9.1.8 fast active-power limitation, "response: 1 s activation"): the row is `quantity = other`
  (instructed curtailment capability, convention 1.2), so the `response:` prefix was used by analogy, not because the
  row is a `smoothing or capping response`. No row was classed `smoothing or capping response`.

## 4. Counts (for the launching session's checks)

- Instruments: 56 rows; access full 42, partial 13, none 1 (E01); status in force 29, no requirement 19, pending 8.
- Requirement rows: 99 (A001-A099); see the CSV for classes.

## 5. What I could not follow exactly, and what I did instead

1. **Unbalance rows added after the first pass.** Convention 1.2 (committed first) lists unbalance as `other`, but
   during the first pass over E09, E10, E11 I wrongly left unbalance out. Before finishing I added the five unbalance
   rows (A095-A099, `other`, non-deciding) and corrected the instrument notes. E08 (Teil A) has no unbalance limit
   value; E04's unbalance clauses state transmission-system performance, not a user limit. Commutation notches
   (E10 4.2) and ripple-control signal levels are not in the convention's list and were not rated.
2. **Level caps not rated (clarification made during extraction).** Caps on a power *level* rather than its variation
   in time (contract capacity, LPC/MPC and MW Withdrawal limits, charger input-power caps, GPU power limit) were not
   rated as requirements, since the deciding question is real-power time variation and none of the non-deciding
   quantities is a level cap. Affects U01, G01, V04/V05 charger caps, V12 `-pl`.
3. **Settlement charges not rated.** Tolerances that only trigger a charge (ERCOT 6.6.5.3 CLR set-point deviation,
   values TAC-set and not printed; AEP excess-reactive-demand charge) are prices, not limits.
4. **Compatibility levels not rated** (EN 61000-2-2 levels quoted in E09) as network levels, not limits on a load;
   planning levels were rated. D-A-CH-CZ Tab. 1-1 (E09, stage-1 screening ratio Sk/Sr by device type) not treated as a
   DC2R-3 step table: it screens device rating rather than stating a permitted power change (judgement).
5. **Ancillary-service capability clauses** (G03 2.3.x for Load Resources/CLRs) rated as `other` per convention 1.2;
   generation-only AS clauses not rated.
6. **AESO guide binding class (X01).** The guide states requirements that AESO implements in Functional
   Specifications; "will be required" items were classed `mandatory` (medium confidence), "should" and "may be
   required" items `recommendation` (incl. the 10 MW/min ramp, A091). This is a judgement on a guide-type document.
7. **OCP V09** classed `mandatory` under the §2 OCP base-spec convention although it is a self-commitment by the
   hyperscalers (medium confidence).
8. **E05 row from an FAQ question.** The only readable value for VDE-AR-N 4120 appears in a user question on VDE FNN's
   own FAQ page (the answer points Bezugsanlagen to 5.5 without restating it); recorded with `confidence = low`.
9. **Scope inside large documents.** For G01-G03 and E04 I read the seed sections plus a keyword search of the
   downloaded section files (G02 Sections 3 and 6; G03 Section 2; G01 Section 9; E04 complete Grid Code text);
   other sections of the ERCOT documents were not downloaded. E04 BC1.A.1.1 (Physical Notification ramp limits that
   also apply to demand BM Units) was found by keyword search outside CC/ECC and rated (medium confidence).
10. **Text extraction.** ERCOT .docx files were converted to text by my own `python3 -I` script (zip/XML) kept in the
    scripts directory; a few D-A-CH-CZ formulas were garbled by `pdftotext` and are flagged in `note`.
11. **Hosts.** V14's PDF is served from NVIDIA's asset CDN (dam-cdn.nvd.orangelogic.com) linked from nvidia.com, as
    in the screener's record; X01-X03 from aeso.ca, fingrid.fi, ieso.ca (group-X operators' own sites). No web search
    was used; no search summaries or model-summarising fetch tools were used to read requirement text. The NVIDIA blog
    page (V11) carries an AI-generated summary box, which was ignored.
12. **Order deviations (minor).** `instruments_A.csv` lists instruments in the order I recorded them, which differs
    from `orders.A` in three places: E01 was attempted in its turn, blocked, retried and recorded after X02;
    V12 was read and recorded before G11 and E03 (positions 25-27 of the order, swapped by mistake); G13 and Q07 were
    fetched together and Q07 recorded first. All 56 instruments have exactly one row. No reading of one instrument
    informed another's classes beyond the never-twice / cross-reference notes.
