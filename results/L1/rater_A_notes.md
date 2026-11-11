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

## 2. Ledger summary (rater A)

- 45 events: domain B 35 (all on seed instruments), domain S 10 (all on seed instruments). No events on the 12 S3 additions.
- Domain-B classes: hardware-or-recert 10, memory-or-crypto 1, software-only 15, cannot judge 9 (all 9 are `partial`-access GB/GB/T editions under L-3).
- Domain-S classes: hardware-or-recert 4, software-only 6.
- Access (seed / addition): B seeds full 13, partial 8, none 14; B additions none 2; S seeds full 13, partial 3; S additions full 6, none 4.
- Every classification is DERIVED-judgemental. Both raters are language-model sessions (D-3).

## 3. Per-instrument remarks (in order A)

- **B22 IEC 61851-24** (full): ed.1 2014 (pre-window), ed.2 2023-12-13 (event). Class line used: a revision of an existing protocol's message set = software-only; a new protocol generation / new physical link = memory-or-crypto.
- **B37 SAE J2929** (none): sae.org is a script-only app with an AWS WAF captcha; not bypassed.
- **B34 FMVSS 305a** (full): its establishing rule 89 FR 104318 also amends FMVSS 305 (B33), so it is recorded once under B33 (the instrument listed first), and noted here. Delay rule 90 FR 9609 and the 2026 cross-reference cleanup 91 FR 33111 are not events.
- **B17 ISO 15118-20** (none): iso.org HTTP 403 Cloudflare to curl and WebFetch.
- **B01 EU 2023/1542** (full): one event, the base act itself (Art. 14 BMS SoH data/read access; Art. 77 passport). Every other act under or amending it in the window (recycling methodology, due-diligence postponement, waste reporting, ESPR registry upload, ELV substance table, portable-battery derogations, corrigenda) changes nothing the domain-B ECU must produce, store or transmit.
- **B27 SAE J2847/3** (none): sae.org WAF.
- **B19 ISO 17409** (none): iso.org HTTP 403.
- **S08 FMVSS 207** (full): no events. The ADS terminology rule 87 FR 18560 (2022) touches 207 and 208 among others; I read it as terminology that keeps existing requirements (its abstract: "maintains the existing regulatory text whenever possible"), so not an event under either instrument. The 2026 obsolete-text removal is editorial.
- **B07 UN R10** (full): unece.org blocked; ODS route used. Method for all UN regulations: every WP.29 provisional agenda 2016-2026 (ECE/TRANS/WP.29/1116-1193) parsed for "Proposal for ... to UN Regulation No. N" with its ECE/TRANS/WP.29/YYYY/NN symbol, each proposal text then read from ODS. Session reports checked for adoption. 11 R10 acts in window, all EMC test set-up, limits and immunity criteria in charging mode: I read them as hardware / test procedure, so no events (judgement; R10 contributes nothing).
- **S13 EU 2019/2144** (full): no events. The base act's seat-belt / belt-reminder / CRS rows are all "A" (requirements already in force), and the two UN-reference updates touching seating (2022/1398: R14, R17, R44, R80; 2025/1122: R25) are mechanical.
- **S15 GB 15083** (partial): `unreadable edition` GB 15083-2019 (2019-10-14), strength title.
- **S10 FMVSS 209** (full): no amendment in the window.
- **B11 GB 38031** (partial): `unreadable edition` GB 38031-2020 (2020-05-12) and `unreadable edition` GB 38031-2025 (2025-03-28). Its title is battery safety only; std.samr.gov.cn shows drafters and the replacement chain but no abstract.
- **S17 UN R80** (full): 4 acts, all mechanical / editorial.
- **S05 UN R44** (full): Supplements 11-19 to the 04 series, all about the CRS product; no ECU-visible change.
- **B25 SAE J2847/1, B23 SAE J1772, B30 SAE J2931/4** (none): sae.org WAF.
- **S03 UN R17** (full): 13 acts (5 new series), all seat-strength / head-restraint geometry / test procedure.
- **B21 IEC 61851-23** (full): ed.2 2023 counted (BPT control and communication-process annexes). It is a supply-equipment standard, so I classed it software-only (low) for the vehicle side, the same as B22.
- **B14 GB 44495** (partial): GB 44495-2024 counted as cannot judge (L-3).
- **B10 GB/T 32960.3** (partial): 2016 and 2025 editions counted, cannot judge.
- **B29 SAE J2931/1** (none).
- **B08 GB/T 32960.1** (partial): 2016 and 2025 editions counted, cannot judge (the title names the remote-service / telemetry system).
- **B20 IEC 61851-1** (full): ed.3 2017 counted, software-only (low); a supply-equipment standard.
- **S04 UN R25** (full): one editorial supplement.
- **S11 FMVSS 210** (full): test-procedure, removal and correction rules only.
- **S20 ISO 13216-1** (none).
- **S02 UN R16** (full): 7 events. The 10 series (2024) splits R16 and moves the belt-reminder provisions into two new UN Regulations, which are not on the list. Moving text is not counted as a change to R16's ECU obligations, and the new regulations are not instruments here (no additions after the list was fixed). Communication-form and information-document entries are not counted.
- **S07 FMVSS 202a** (full): the 2017 eCFR version differs from the previous one in punctuation only.
- **B05 UN R155** (full): 4 events (original, S1, S2, S3). The interpretation-document amendments are not regulation amendments.
- **B26 SAE J2847/2** (none).
- **B35 EU 2023/1804 AFIR** (full): no vehicle-side obligation in the base act or its acts, so no events.
- **S18 UN R145** (full): no events.
- **B13 GB/T 27930** (partial): 2023 edition counted (cannot judge). The 2015 edition was published 2015-12-28, before the window. GB/T 27930.2-2024 is a new, separately numbered part (ChaoJi protocol); I treat it as a different document, not counted (judgement).
- **S12 FMVSS 225** (full): no events.
- **B18 ISO 15118-8** (none).
- **S06 UN R129** (full): 52 documents, all about the CRS product; no events.
- **S16 GB 11550** (partial): no edition in the window.
- **B12 GB/T 18487.1** (partial): `unreadable edition` GB/T 18487.1-2023 (2023-09-07), because its title is general charging-system requirements and no abstract is shown.
- **B28 SAE J2847/6, B24 SAE J3400, B32 SAE J2931/7** (none); **S19 ISO 17373** (none).
- **S01 UN R14** (full), **S21 UN R170** (full), **S26 FMVSS 213b** (full): no events. 213b and R170 regulate the CRS product, not a vehicle ECU.
- **B33 FMVSS 305** (full): 2 events (2017 GTR 13 electrical-safety rule; 2024 305a rule, recorded here). The 2019 connector clarification is hardware.
- **B04 UN R100** (full): 9 events. Combined documents (one proposal amending two series, e.g. 2026/49) are recorded once. Parallel supplements adopted as separate documents for two series (03-S4/04-S1, 03-S5/04-S2) count as separate acts under "one act, one event". This inflates the count where WP.29 keeps two series in force, and I applied it the same way in R16 (07-S6/08-S2). The 04 series (2024) is a new series that only adds heavy-vehicle labels: not an event.
- **B15 GB 44496** (partial): GB 44496-2024 counted, cannot judge.
- **B16 ISO 15118-2** (none); **B36 ISO 6469-1** (none); **S23 SAE J826, S25 SAE J800, B31 SAE J2931/6** (none).
- **B09 GB/T 32960.2** (partial): 2016 and 2025 editions counted, cannot judge.
- **B06 UN R156** (full): 2 events. The 2026 supplement only replaces certificate models.
- **B02 EU 2024/1257** (full): 4 events (base act; 2025/1706, kept although S1 dropped it on its title, because its text regulates battery durability and battery-data manipulation; 2025/1707 OBM/EVP data with OTA upload; 2026/1764).
- **S24 FMVSS 213, S22 FMVSS 202** (full): no events.
- **S09 FMVSS 208** (full): 3 events (CRS list for suppression testing 2024; rear-seat belt warning 2025; interim final rule 2026, counted for its warning-logic clarifications).
- **B03 UN GTR 22** (full): 2 events.
- **S14 GB 14167** (partial): `unreadable edition` GB 14167-2024 (2024-09-29).

## 4. Blocked routes (nothing bypassed)

- **unece.org**: HTTP 403 (Cloudflare "Sorry, you have been blocked") on the regulation addenda page. I used the UN Official Document System instead (documents.un.org, `api/symbol/access` PDF by symbol). That route reads: the WP.29 provisional agendas and session reports ECE/TRANS/WP.29/1116-1193 (sessions 166-200), the AC.1/AC.3 vote tables in the reports, and every proposal document ECE/TRANS/WP.29/YYYY/NN for the listed UN regulations and GTR 22.
- **iso.org**: HTTP 403 Cloudflare challenge ("Just a moment...") for standard pages, the search page and the OBP, with both curl and WebFetch. All 7 ISO instruments are `none` (B16, B17, B18, B19, B36, S19, S20).
- **sae.org**: a script-only application shell carrying an AWS WAF captcha script, for every SAE page tried (curl; WebFetch also returned no content for J2929). All 13 SAE instruments are `none` (B23-B32, B37, S23, S25).
- **openstd.samr.gov.cn / std.samr.gov.cn**: catalogue list and detail pages (edition, publication and implementation dates, replaced standard, drafters) are reachable. The full text is an online viewer behind a verification step, which I did not attempt. No abstract or scope is shown. All GB/GB/T instruments are therefore `partial`.
- **webstore.iec.ch**: publication pages, with abstracts that list the significant technical changes, are reachable. The history table is script-rendered and was not read; I took the edition chains from the "cancels and replaces" statements. All IEC instruments are `full`.
- EUR-Lex HTML, the Publications Office SPARQL endpoint, eCFR (versioner API) and the Federal Register (API and full text) were all reachable.

## 5. `unreadable edition` entries (L-3; logged, not counted)

- B11 GB 38031-2020 (2020-05-12): `unreadable edition`
- B11 GB 38031-2025 (2025-03-28): `unreadable edition`
- B12 GB/T 18487.1-2023 (2023-09-07): `unreadable edition` (general charging-system title, no abstract)
- S14 GB 14167-2024 (2024-09-29): `unreadable edition`
- S15 GB 15083-2019 (2019-10-14): `unreadable edition`

The ISO and SAE instruments are `none`, so their editions could not even be identified from a body source.

## 6. What I could not follow exactly, and what I did instead

1. **UN change history route.** unece.org was blocked, so no regulation page with its list of supplements was read. Instead I built the list of amendments from the WP.29 agendas, a script-parsed list of every "Proposal for … to UN Regulation No. N". I then checked each one against the AC.1 vote tables in the session reports, which give the adoption date, and read each proposal text on ODS. Corrigenda were not read (by definition editorial). Possible misses: proposals listed only in agenda addenda (…/Add.1), which I did not fetch, and the new-regulation entries whose titles carry no number (found by a separate title search: R155, R156, R170, GTR 22). The vote tables were used as a cross-check, and they listed no further R10/R14/R16/R17/R25/R44/R80/R100/R129/R145/R155/R156/R170 acts.
2. **`adoption_date` for UN acts** is the AC.1 (or AC.3) vote date printed in the session report. This is the WP.29/AC adoption date, not the entry-into-force date. One label mismatch: ECE/TRANS/WP.29/2020/113 is titled "Supplement 2 to the 08 series" in the document but labelled "Suppl. 3 to 08" in the 2020-11 vote table. I used the document title (R16-08-S2), because the vote table also gives "Suppl. 3 to 08" to 2021/113.
3. **Reading order.** For efficiency, some catalogue pages and documents were downloaded before their instrument came up in order A: the ODS proposal PDFs for all UN regulations were fetched in one batch, and the openstd list for "32960" returned B08, B09 and B10 together. Each instrument was still judged and recorded when reached. Exceptions: the B33 row for the 305a rule (89 FR 104318) was written while rating B34, and the B03 (GTR 22) ledger rows went into the commit for instruments 51-60. No event decision depended on this.
4. **Never-twice applied across instruments:** the FMVSS 305a establishing rule is recorded under B33, not B34. The ADS terminology rule 87 FR 18560 touches 207 and 208 and is counted under neither.
5. **Judgement calls a second rater may make differently:**
   - R10 EMC charging-mode changes are not events (hardware / test procedure).
   - Supply-equipment standards (IEC 61851-1, -23) and the protocol revision IEC 61851-24 are classed software-only for the vehicle side.
   - Parallel supplements to two series of one regulation count as separate acts when they are separate documents (R16 07-S6/08-S2; R100 03-S4/04-S1, 03-S5/04-S2). A single document that amends two series counts once (R100 2026/49).
   - GB/T 27930.2-2024 (a new part) is not counted under GB/T 27930.
   - FMVSS final rules that all new vehicles must meet by a compliance date are classed hardware-or-recert under "must newly comply by a stated date". Effective-date delays are not events.
   - R155 Supplement 2 (V2X spoofing mitigation) is software-only for the domain-B ECU.
   - The EU 2019/2144 base act is not an S event, because its seat-belt / reminder / CRS rows are "A" (already applying).
6. **Window end:** the 200th WP.29 session (November 2026) had not voted when I read the agendas, so its proposals (e.g. R129 2026/198, amendments to GTR 22) are not counted.
7. No web-search listing was used to locate or source anything. All sources are the publishing bodies' own pages and documents.
