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

## 2. Per-instrument remarks (in order B; reading dates 2026-11-10/11)

Full per-instrument notes (edition, routes, why no rows) are in `instruments_B.csv`. Highlights:

- **G13** §25.205: commission "may impose" ramp limits; no value. no requirement.
- **G06** NERC Level 2 alert: recommendations to establish ramp limits; questionnaire asks MW/min values; no value. no requirement.
- **G07, G08, G09** NERC CLO-001/002/003-1 Draft 1: pending.
- **E07** VDE-AR-N 4130 (+A1): text sold by VDE Verlag; only blank Annex E forms free. partial, no rows.
- **V06** Diablo 400 v0.7.0: PF/THD table, hold-up, BBU backup time, load-step capability table (read as the
  load-step envelope the supply must carry; supplier capability floor), DC transient deviation. Ride-through via ITIC /
  IEC 61000-4-34 is a cross-reference.
- **G12** §25.194: process/disclosure rule. no requirement.
- **Q04** IEEE 519-2022: abstract only, no value. partial, no rows.
- **V09** OCP disturbance interface spec: Table 1 LVRT/HVRT/PFAPR (5 rows). Ramp / intra-minute / forced-oscillation
  limits are announced as future work (no values).
- **G03** ERCOT NOG §2.6.4 and §2.15 (LCL ride-through): 14 ride-through/other rows. CLR ancillary-service ramp
  qualifications are not load-variation limits.
- **V05** ORv3 48V BBU: transient response, 240 s backup, repetitive peak-load chart (150 %, pulse width vs step),
  average ≤100 %, PSU→BBU transfer <2 ms.
- **G04** PGRR144: adopted (PUCT 11/05/2026, effective 12/01/2026); model-quality tests only. no requirement.
- **E01** DCC 2016/1388: Annex I/II withstand tables (one row per synchronous area), Art 15 reactive range, Art 19 LFDD
  operating time, Art 30 very-fast active power control response ≤2 s (deciding; response-time rule). Art 20 PQ has no
  value.
- **G11** PJM draft ride-through: pending.
- **U01** AEP Ohio Schedule DCT: "Load Ramp Period" is multi-year contract build-up. no requirement.
- **V01** ORv3 base: mechanical; no requirement.
- **E11 / E10 / E09** D-A-CH-CZ Teil B HV/MV/LV: RVC limits, flicker planning levels / allocations / emission limits with
  95 %-week assessment (allowance `loose`), single-value 1,3·Pst cap, Sk/ΔS admission ratios by repetition rate (recorded
  as `step change`, window not stated), harmonics (E10/E11 only, one row per table).
- **V10** OCP Open Data Center 0.7.0: density/cooling targets only. no requirement.
- **V11** NVIDIA GB300 blog: Table 1 configuration parameters (image) as `vendor capability` (ramp 20 W/s up/down,
  5-s-average idle floor, 60 ms idle-to-burn, 10 s before ramp-down).
- **U02** Dominion GS-5: schedule text not on the utility site; order only. partial, no rows.
- **G16** FERC co-location order: no requirement.
- **V03, V07, V08** ORv3 power shelves / PSU: "should be capable" repetitive peak-load envelopes (`recommendation`),
  DC transient deviation, hold-up, BBU transfer time.
- **G15** PUCT Project 59999 SLLIA: pending.
- **G01** ERCOT Planning Guide: no requirement (studies, energization, PCLR LPC cap).
- **V13, V12** NVIDIA tuning guide / nvidia-smi: parameters named, no values. no requirement.
- **E02** ENTSO-E IGDs: numeric content is for generators/HVDC or DR SFC frequency settings. no requirement.
- **Q08, Q07, Q01, Q05, Q06** abstracts only, no values. partial, no rows. **Q02** (measurement methods) and **Q03**
  (flickermeter; abstract says it gives no limit values): partial, no requirement.
- **V02** ORv3 power shelf rev 1.0: no requirement.
- **E08** D-A-CH-CZ Teil A: methods and definitions only. no requirement.
- **Q09** EREC P28: catalogue scope only (document via order flow, not used). partial, no rows; its P28-derived values
  appear in E04.
- **G02** ERCOT Protocols §6.5.7.11 (NPRR1325, approved, gray-boxed pending system implementation of PGRR145): PCLR
  down ramp 10–20 %/min and up ramp ≤20 %/min of (MPC−LPC), compliant when ≥90 % of eligible one-minute intervals in a
  month meet them. Window = the stated one-minute interval (`1 – 60 s`); allowance a = 10 % (`very loose`); shape
  **history** (B104, B105). Measurement point `facility` (PCLR telemetry). Treated as adopted (see §6).
- **V04** ORv3 BBU shelf: transient response, 27 kW peak (low confidence), 240 s backup.
- **G05** NERC Reliability Guideline: no value. no requirement.
- **V14** NVIDIA 800 VDC white paper 1: descriptive. no requirement.
- **G10** PJM Board letter: "ramp rate" = multi-year load build-up. no requirement.
- **E06** E VDE-AR-N 4120/A1: pending. **E05** VDE-AR-N 4120: partial, no rows.
- **X01** AESO TCDC guide: 10 MW/min ramp limit at POC (rate-unit rule, hard), reconnection >50 MW needs approval,
  PF >0.98, ride-through tables, RoCoF 5 Hz/s (0.5 s window), phase jump, V/Hz, recovery (recommendation).
- **X03** IESO LCL requirements v1.0: pending as printed.
- **X02** Fingrid large demand facilities (Finnish): Table 9.1 cyclic power-oscillation limits by frequency band with
  STFT windows 300 s … 0.5 s (9 rows, `swing amplitude`, hard), market/third-party ramp rate selectable within an
  indicative 5–50 MW/min, single step ≤50 MW, fast limitation response, RoCoF, FRT curves, PFAPR.
- **E03** ACER amended DCC draft: pending.
- **E04** GB Grid Code CC.6.1.7: RVC categories 1–3 (half-cycle-refreshed one-cycle RMS: `≤ 100 ms`; categories 2/3
  `event count`), flicker planning levels Table CC.6.1.7(b) (allowance `not stated`, NOTE 2), ECC.6.4.5.1 reactive range.
- **U03** Georgia Power rules: lighting PF ≥90 % only.
- **G14** §25.370: forecasting. no requirement.

## 3. Blocked routes

- IEC webstore preview PDFs (Q01, Q02, Q03, Q07, Q08): `/pub/pdf/preview/…` 404; catalogue preview endpoint redirects to
  the home page. Abstracts only.
- IEEE 519 / 1453 full text paywalled; abstracts only.
- VDE Verlag (E05, E07): purchase required; catalogue descriptions only.
- ENA EREC P28 (Q09): listed "£Free" but obtained through an order/account flow; not used.
- Dominion GS-5 schedule text (U02): not on dominionenergy.com.
- EUR-Lex "ALL" page for 2016/1388 returned HTTP 202 with an empty body (challenge page) on two tries; not pursued.
  The TXT/HTML text was served normally and was used.
- NERC project pages for 2026-02: guessed URLs 404; status taken from the drafts' own timelines.
- opencompute.org V02: HTTP/2 stream errors; completed with HTTP/1.1 and resume (not a block).

## 4. Pending entries

- pending: G07 NERC CLO-001-1 Draft 1, "first draft of proposed standard for the initial formal 30-day comment period";
  Board adoption anticipated December 2026
- pending: G08 NERC CLO-002-1 Draft 1, same timeline
- pending: G09 NERC CLO-003-1 Draft 1, same timeline
- pending: G11 PJM M14B Att. D-2 / tariff, "September 1, 2026 Draft / Remains Under Development and Subject to Revision by PJM"
- pending: G15 PUCT Project 59999, "Proposal Notice of Draft Standardized Large Load Interconnection Agreement (SLLIA)" (11/5/26 OM Item No. 40)
- pending: E03 ACER Recommendation 01/2025 Annex 4a, draft "COMMISSION REGULATION (EU) …/… of …"
- pending: E06 E VDE-AR-N 4120/A1:2026-05, "Entwurf … steht zur Konsultation bereit … Konsultation endet am 10. Mai 2026"
- pending: X03 IESO LCL Technical Requirements v1.0, "New requirements proposed in this document will be updated into the Market Rules … after the IESO external stakeholdering … is completed"

## 5. DC2-2 conversions, rate-unit and response-time rule uses

- **DC2-2 conversions: none.** Considered for E04 CC.6.1.7 categories 2 and 3 (recurrence printed, but no duration of a
  permitted exceedance, the time profile is the limit itself) and X02 Table 9.1 (exceedance permitted only for
  grid-caused disturbances, duration ≤ window; not a load allowance): neither prints a recurrence and duration of a
  permitted load exceedance, so no conversion.
- **Rate-unit rule (`unit:`):** B087, B088 (V11, W/s); B121 (X01, MW/minute); B149 (X02, MW/min). Under STATED these
  become `not stated`.
- **Response-time rule (`response:`):** B056 (E01 Art 30, 2 s); B090 (V11, 60 ms); B091 (V11, 10 s); B151 (X02 9.1.8,
  ≤15 min, activation 1 s).
- Not the rate-unit rule: B104/B105 (G02) state their own one-minute assessment interval in §6.5.7.11(4).

## 6. Things I could not follow exactly, and what I did instead

- **WebSearch summary exposure (disclosure).** One WebSearch (restricted to pjm.com / ferc.gov) to check G11's adoption
  status returned a model-written summary that paraphrased draft ride-through content and FERC EL26-67 statements. G11 is
  pending and yields no rows; nothing from the summary was used as a source. No other web search was made.
- **Gray-boxed ERCOT text (G02).** §6.5.7.11 is approved (NPRR1325) but inserted "upon system implementation of PGRR145".
  I read "adopted by its body" (§1) as satisfied and rated it; if the analysis reads not-yet-implemented text as pending,
  B104/B105 drop out.
- **AESO guide binding class (X01).** My conventions (§1.3) default a "guide" to `recommendation`; the AESO document is a
  guide *to connection requirements* whose "Requirements" items say "will be required" / "may be required", so I classed
  those `mandatory` and its "should" items `recommendation`. Borderline; flagged in each row's note.
- **Ride-through / hold-up windows.** For ride-through and hold-up rows the printed duration is the limit, not an
  assessment interval; I set the window `not stated` unless a cumulative or averaging window is printed (X01 footnotes
  17/19, X02, E01 none). This affects only non-deciding rows.
- **Supply-capability tables (V03–V08).** OCP PSU/BBU peak-load envelopes are requirements on the supplier to carry load
  steps; I recorded them as `step change` (deciding) at `shelf or PSU` / `rack or row`, and the "≥1 s moving average
  ≤100 %" rows as `other`. "should be capable" rows are `recommendation`.
- **D-A-CH-CZ windows.** Teil B clauses do not print the RVC measurement basis; Teil A (E08, a separate instrument)
  defines RVC on half-period RMS values and Pst/Plt over 10 min / 2 h. I used the Pst/Plt intervals (index definitions)
  but left RVC windows `not stated` in E09–E11, per §1.4. Harmonic tables recorded one row per table (E10, E11), not per
  order; unbalance, commutation notches and ripple-control limits not recorded (not driven by real-power variation).
- **Network compatibility levels** (E09 CPst/CPlt from EN 61000-2-2) not recorded as load limits.
- **X03 IESO** restates existing Market Rules requirements alongside pending ones; I took no rows (the Market Rules are
  not a listed instrument).
- **Quotes** are verbatim excerpts ≤25 words; for table rows the quote is the row's printed cells joined by spaces.
  Fingrid (X02) and D-A-CH-CZ quotes are in the original language; limits are paraphrased in English in `limit`.
- The `deciding` and `shape` columns were computed by script from my own quantity, window and allowance classes (§2
  table); no hand-written shape differs from the computed one.
