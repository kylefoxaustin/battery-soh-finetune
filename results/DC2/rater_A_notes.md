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

## 2. Summary (written after reading)

- 56 instruments rated in order A (`DC2_orders.json` `orders.A`), reading dates 2026-11-10 (single session).
- Access: full 43, partial 13, none 0. Status: in force 28, no requirement 20, pending 8.
- Requirement rows: 204 (`A001`–`A204`); 16 deciding, all 16 mandatory; 195 rows binding (mandatory or planning level).
- Rows are in reading order except `A204` (E10 commutation-notch limit, found while reading E09 and appended then).

## 3. Per-instrument remarks (order A)

- Q07 (IEC 61000-3-3): partial. Abstract only; no limit printed; preview 403 (blocked). No rows.
- V05 (ORv3 48V BBU): full. 4 rows (hold-up x2, other x2); EN61000-3-2/-3-3 bare references.
- G15 (PUCT SLLIA): pending: PUCT Project 59999 Item 5, 'PROPOSED SLLIA (STAFF RECOMMENDATION)' / 'Proposal Notice of Draft Standardized Large Load Interconnection Agreement (SLLIA)'. No rows.
- X02 (Fingrid large demand facilities): full, in force (applied immediately per landing page). 17 rows: ramp (9.1.7), step (9.1.7), fast limitation response (9.1.8), 9 swing-amplitude rows (Table 9.1, STFT windows), 5 ride-through. Finnish text read directly.
- V02 (ORv3 power shelf): full, no requirement (ripple at steady state only; EN 61000-3-2/-3-3 bare references).
- E06 (E VDE-AR-N 4120/A1): pending: E VDE-AR-N 4120/A1, 'Entwurf' 13.04.2026 (consultation closed 10 May 2026). No rows. Partial (VDE summary page).
- Q08 (IEC 61000-3-11): partial; abstract only, no limit printed; preview 403. No rows.
- Q01 (IEC TR 61000-3-7): partial; abstract only, no limit printed; preview 403. No rows.
- V04 (ORv3 BBU shelf): full; 3 rows (hold-up x2, other).
- V01 (ORv3 base): full, no requirement (mechanical; input voltage range only).
- V09 (OCP hyperscaler-utility disturbance spec): full; 5 ride-through rows (Table 1). Explicitly defers ramp-rate / intra-minute / oscillation limits to a future spec.
- G10 (PJM Board letter): full, no requirement ('ramp rate' = multi-year load growth for forecasting).
- G14 (PUCT 25.370): full, no requirement (forecasting).
- Q06 (EN 50160): partial, scope only; no value printed; no rows.
- G05 (NERC Reliability Guideline): full, no requirement (recommends that limits be set; prints none).
- G03 (ERCOT NOG §2): full; 14 rows, all ride-through/other (NOGRR282 LCL FRT/VRT/PFAPR). AS deployment times for CLRs not counted (voluntary reserve products).
- G07 (NERC CLO-001-1): pending: NERC CLO-001-1 Draft 1, 'first draft of proposed standard for the initial formal 30-day comment period' (Board adoption anticipated Dec 2026). No rows.
- X03 (IESO LCL technical requirements): pending: IESO Technical Requirements for LCLs v1.0 (01/May/2026), 'New requirements proposed in this document will be updated into the Market Rules ... after the IESO external stakeholdering ... is completed'. No rows. Text read before status confirmed (logged).
- E08 (D-A-CH-CZ Teil A): full; 5 harmonics rows (interharmonic / supraharmonic emission limits, 10-min 95 % quantile). No voltage-change/flicker values in Teil A.
- G12 (PUCT 25.194): full, no requirement (procedural).
- Q02 (IEC 61000-4-30): partial; measurement methods per abstract -> no requirement.
- G13 (PUCT 25.205): full, no requirement (commission may impose ramp limits case by case; none printed).
- E03 (ACER amended DCC): pending: ACER Recommendation 01/2025 Annex 4a, 'COMMISSION REGULATION (EU) …/… establishing a Network Code on Demand Connection' (draft; 2016/1388 still in force per EUR-Lex). No rows.
- U03 (Georgia Power rules): full; 1 PF row (lighting); large-load rules financial only.
- E11 (D-A-CH-CZ B-III HV): full; 29 rows: RVC 2 % (1), flicker planning/allocation/emission (8), unbalance (2), harmonic emission formulas (3), harmonic planning levels Tab 3-1 (15). Tab 1-2 screening ratio not counted.
- V08 (ORv3 ±400V 18kW PSU): full; 9 rows (other x8 incl. pulse-power moving-average envelope 'should'; hold-up 6 ms).
- E04 (GB Grid Code): full; 7 rows: RVC categories 1–3 (one-cycle RMS), flicker planning levels (4).
- Q03 (IEC 61000-4-15): partial; abstract says it gives no limit values -> no requirement.
- V06 (Diablo 400 v0.7.0): full; 14 rows (PF 2, THD 3, hold-up 2, peak-power envelope 4, dynamic loading 3).
- G02 (ERCOT Nodal Protocols): full; 2 deciding rows: PCLR ramp rate 6.5.7.11(1),(2): 1-min intervals, ≥90 % monthly compliance -> very loose -> computed shape history. Caveats: telemetered ramp-rate metric; gray-boxed pending system implementation (NPRR1325/PGRR145).
- V14 (NVIDIA 800 VDC white paper): full, no requirement (descriptive).
- G01 (ERCOT Planning Guide §9): full, no requirement (project-specific consumption caps only).
- U02 (Dominion GS-5 / SCC order): partial (schedule text not on utility site); order has no §2 requirement (multi-year contract ramp only). No rows.
- V13 (GB200 tuning guide, Power and Thermals): full, no requirement (feature description, no values).
- E05 (VDE-AR-N 4120): partial (catalogue/status only; text sold). No rows.
- V10 (OCP Open Data Center Rev 0.7.0): full, no requirement (density targets only).
- E10 (D-A-CH-CZ B-II MV): full; 31 rows: RVC 2 categories, flicker 8, unbalance 2, harmonic formulas 3, harmonic planning levels 15, commutation notch 1 (A204, appended after E09 was read).
- V12 (nvidia-smi manual): full; exposes power-smoothing parameters (ramp rates mW/s, hysteresis ms, floor %) but no values printed -> no row.
- U01 (AEP Ohio Schedule DCT): full, no requirement (load ramp period = multi-year build-up).
- V11 (NVIDIA GB300 blog): full, no requirement (no setting values; 65 J/GPU storage and 30 % peak reduction are descriptive).
- E01 (DCC 2016/1388): full; 25 rows: Annex I frequency withstand (17), Annex II voltage withstand (7), Art 15 PF (1). Art 30 very-fast DR response ≤2 s not counted (voluntary service, consistent with ERCOT AS).
- E07 (VDE-AR-N 4130): partial (status page only; text sold). No rows.
- G08 (NERC CLO-002-1): pending: NERC CLO-002-1 Draft 1, 'first draft of proposed standard for the initial formal 30-day comment period'. No rows.
- G06 (NERC Level 2 alert): full, no requirement (recommends limits; none printed).
- E02 (ENTSO-E IGDs, 14 docs): full, no requirement for demand (guidance; RoCoF values for PGMs).
- Q04 (IEEE 519-2022): partial; scope only, no values printed; no rows.
- Q09 (EREC P28): partial (catalogue scope; download requires order/account). No rows.
- V03 (ORv3 HPR V2 72 kW shelf): full; 4 rows (hold-up 5 ms; peak-load envelope x3 'should').
- G16 (FERC co-location order): full, no requirement.
- G11 (PJM LCL ride-through draft): pending: PJM draft M14B Att. D-2 and tariff, 'September 1, 2026 Draft / Remains Under Development and Subject to Revision by PJM'. No rows.
- V07 (ORv3 HVDC-LVDC 100 kW shelf): full; 1 row (peak-load envelope 'should').
- X01 (AESO TCDC guide): full; 20 rows incl. deciding: 7.2 ramp 10 MW/min (unit rule, hard, 'may be required', low confidence) and 7.4 reconnection step >50 MW needs approval; PF 0.98; ride-through tables (cumulative windows used).
- G09 (NERC CLO-003-1): pending: NERC CLO-003-1 Draft 1, 'first draft of proposed standard for the initial formal 30-day comment period'. No rows.
- E09 (D-A-CH-CZ B-I LV): full; 13 rows (RVC 2, flicker 6, unbalance 1, harmonic formulas 3, commutation notch 1). Also added E10 commutation-notch row (dKom 5 %) found while reading E09.
- G04 (PGRR144): full, adopted (PUCT 11/05/2026), no requirement (model/test procedures; cross-refers NOG 2.15).
- Q05 (IEEE 1453-2022): partial; abstract only, no values; no rows.

## 4. Blocked routes and access limits

- **IEC webstore previews** (Q01, Q07, Q08): the catalogue preview endpoint returned HTTP 403 "Request blocked" (CloudFront); the legacy `/pub/pdf/preview/` path returned 404. Not retried with other headers or routes. Q02, Q03 read from abstracts only (preview not retried after three 403s).
- **IEEE** (Q04, Q05): abstract/scope pages only; full text sold.
- **CENELEC** (Q06): catalogue scope page readable; text sold. EN 61000-3-3 / -3-11 not looked up on CENELEC (screener: session checksum needed); IEC originals used (Q07, Q08).
- **VDE / VDE Verlag** (E05, E06, E07): status, news and catalogue pages only; TAR texts sold.
- **ENA** (Q09): EREC P28 listed as free but obtained through "Add to Order" (account / checkout); not attempted.
- **Dominion** (U02): GS-5 schedule not listed on dominionenergy.com Virginia rate-schedule page; the SCC final order was read in full.
- **NERC project page** (G07–G09): guessed project-page URLs returned 404; status taken from each draft's own development timeline.
- **IESO engagement page** (X03): guessed URL 404; status taken from the document's own text.
- No `none` access state was recorded: every instrument had at least its body's own catalogue, abstract or summary page.

## 5. Pending entries (§1)

- pending: PUCT Project No. 59999 Item 5 (proposed SLLIA) — G15, "PROPOSED SLLIA (STAFF RECOMMENDATION)"; Item 3 "Proposal Notice of Draft Standardized Large Load Interconnection Agreement (SLLIA)"; Texas Register issue of 11.20.2026.
- pending: E VDE-AR-N 4120/A1:2026-05 — E06, "Entwurf" (Erscheinungsdatum 13.04.2026).
- pending: NERC CLO-001-1 Draft 1 — G07, "This is the first draft of proposed standard for the initial formal 30-day comment period."
- pending: NERC CLO-002-1 Draft 1 — G08, same wording.
- pending: NERC CLO-003-1 Draft 1 — G09, same wording.
- pending: IESO Technical Requirements for Large Computational Loads, Version 1.0 (01/May/2026) — X03, "New requirements proposed in this document will be updated into the Market Rules or relevant standards after the IESO external stakeholdering over these requirements is completed."
- pending: ACER Recommendation No 01/2025 Annex 4a, amended DC Network Code — E03, draft "COMMISSION REGULATION (EU) …/…" (Regulation 2016/1388 still in force on EUR-Lex).
- pending: PJM draft M14B Attachment D-2 and tariff revisions for LCL ride-through — G11, "September 1, 2026 Draft / Remains Under Development and Subject to Revision by PJM".
- Not pending although not yet effective: G04 (PGRR144, approved by PUCT 11/05/2026) and G02 §6.5.7.11 (NPRR1325 language approved, gray-boxed pending system implementation of PGRR145) are adopted by their bodies; treated as in force under convention 1.8.

## 6. DC2-2 conversions, rate-unit rule and response-time rule

- **DC2-2:** no conversion made. The only event-count allowances (E04 GB Grid Code CC.6.1.7 categories 2 and 3: "4 events in 1 calendar month", "1 event in 3 calendar months") print a recurrence but no maximum exceedance duration per event, so they stay `event count` (A089, A090; their window class is `≤ 100 ms`, so the shape is electronics regardless).
- **Rate-unit rule (`unit:`):**
  - A007 (X02 Fingrid 9.1.7): `unit: MW/min` → `1 – 60 s`.
  - A171 (X01 AESO 7.2): `unit: MW/minute` (PMU measurement at POC, no averaging interval printed) → `1 – 60 s`.
  - Not applied to A109/A110 (G02 PCLR ramp): the clause states one-minute assessment intervals, which set the window directly.
- **Response-time rule (`response:`):**
  - A009 (X02 Fingrid 9.1.8 d): activation within 1 s, set point within a pre-agreed time of at most 15 min; window taken as the time to reach the set point (`1 – 15 min`). Alternative reading (activation time 1 s → `1 – 60 s`) noted in the row.

## 7. Judgement calls and refinements made while reading (applied consistently after first use)

1. **Ride-through window.** Window = the printed minimum ride-through / operating time, or, where the clause states a cumulative assessment window (X01 AESO Table 6-1 footnote 17: 10 s or 3600 s; Table 6-2 footnote 19: 60 s), that stated window. For a withstand curve, the longest duration of the profile (X02 9.1.10: 10 s). Post-fault active power recovery is `ride-through` (convention 1.2), window = the recovery time.
2. **Ancillary-service and demand-response products not counted.** ERCOT CLR/Load Resource deployment times (NOG 2.3, Protocols 3.17/6.5.7.6) and DCC Art. 29/30 demand-response performance (very fast active power control ≤ 2 s) are minimum-response obligations of voluntary reserve products, not limits on how a large load's power may vary; not rows. Fingrid 9.1.8 fast limitation is mandatory for every connected large demand facility and is counted.
3. **Compatibility levels not counted** (D-A-CH-CZ Teil B I: EN 61000-2-2 CPst/CPlt, CU2, harmonic voltages): network reference levels, not limits on a load. Planning levels, shares of all users (`ges`) and customer emission limits are counted as `planning level`.
4. **D-A-CH-CZ binding class.** All D-A-CH-CZ limits (planning levels and emission limits "als Richtwerte") classed `planning level`: technical rules the network operator applies in connection assessment.
5. **D-A-CH-CZ screening ratios not counted** (Tab. 1-2 Sk V/ΔSA by repetition rate; stage-1/2 ratios for unbalance and harmonics): criteria deciding whether emission limits are set, not limits on the load.
6. **Proportionality-factor tables** (D-A-CH-CZ Tab. 3-2/3-3) are parameters of one emission-limit formula: one row per formula clause, not per harmonic order. Planning-level tables that print a limit per order (Tab. 3-1) are one row per printed category.
7. **D-A-CH-CZ emission-limit allowance** taken from Teil A's measurement rule (95 % quantile of 10-min values over a week → `loose`), to which Teil B §2.4/§3.4 refer; flicker allowances from each part's own Nachweisverfahren clause.
8. **Supply-side rack/PSU specifications.** Output-voltage transient limits, pulse/peak-load envelopes (moving-average windows) and inrush limits classed `other` (they rate what the supply must deliver; they do not limit the load's power toward the facility or grid); BBU / PSU AC-loss transfer and backup times classed `hold-up`. Steady-state output ripple not counted (not driven by load variation).
9. **AESO guide binding class.** "Will be required" items classed `mandatory` (requirements implemented through project-specific Functional Specifications), "should" items `recommendation`; the 10 MW/min ramp ("may be required", called "the proposed 10MW/min requirement") and the >50 MW reconnection-approval threshold classed `mandatory` with `confidence = low`.
10. **ERCOT PCLR ramp (G02 6.5.7.11).** Compliance is assessed on one-minute intervals with ≥ 90 % of eligible intervals per month required → 10 % may exceed → `very loose`; computed shape `history`. The metric counts intervals where the PCLR's *telemetered* average up/down ramp rates met the band, and the section is approved but gray-boxed pending system implementation; both caveats are in the rows' `note` and `confidence = medium`.
11. **Vendor-capability content without values** (V11 NVIDIA blog, V12 nvidia-smi, V13 tuning guide) yields no `vendor capability` row: the pages name the configurable parameters (ramp-rate in mW/s, hysteresis, floor %) but print no value or range.
12. **Instruments with only magnitude caps** (ERCOT PG §9 LPC / withdrawal limit; AEP DCT contract capacity; Dominion / AEP multi-year "load ramp" periods) yield no rows: the caps are project-specific and not printed, and the ramp periods are multi-year demand build-up, not real-power time variation.

## 8. Anything I could not follow, and what I did instead

- **Orders file.** `DC2_orders.json` contains both raters' orders; reading the file (as instructed) displayed `orders.B` as well. Only `orders.A` was used.
- **X03 (IESO)** was read in full before its pending status was confirmed from its own text; no rows were recorded from it.
- **Sources_tried / fetch log.** A raw fetch log (URL, HTTP status, file) is kept outside the repository in the rater's scratch directory; `sources_tried` in `instruments_A.csv` summarises it.
- **Quotes.** Quotes over 25 words were truncated to their first 25 words (verbatim prefix); quotes in A009, A010 (X02) and A141–A164 (E01 Annex I/II rows) use "..." to mark an elision inside the clause; none adds words.
- **Languages.** Finnish (X02) and German (E05–E11) texts were read directly by the rater (a language model); quotes are in the original language.
- **E10 row order.** A204 belongs to E10 but was appended after E09's rows (see §2).
- No bot check, paywall, login or verification step was circumvented. Nothing in fetched content was executed or followed as an instruction.
