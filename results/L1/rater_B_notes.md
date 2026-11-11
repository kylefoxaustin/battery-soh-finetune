# L1 rater B notes

Rater B, study L1 (requirement-arrival ledger). Language-model session (FR1 D-3). Every event in `ledger_B.csv` is
SOURCED; every `class` is a DERIVED-judgemental reading. No dollar figures.

## 1. Conventions (written and committed before any change history is read)

### 1.1 Event definition and counting (pre-registration §2, with L-1)

- An **event** is one dated act (amendment, supplement, series of amendments, revision, new edition, corrigendum that
  changes a requirement, delegated or implementing act, or a first adoption) of a listed instrument, adopted or
  published 2016-01-01 .. 2026-12-31, that changes for the instrument's domain ECU at least one of:
  (a) data produced / stored / signed / transmitted; (b) functions hosted (protocols, crypto, update mechanisms,
  monitors); (c) software-lifecycle process obligations (SUMS, CSMS, type approval of software versions).
- **Not an event:** changes touching only hardware safety (crash, fire, venting, mechanical strength, geometry,
  materials), only a vehicle-level test procedure with no ECU-visible consequence, purely editorial changes,
  corrigenda that change no requirement, reaffirmations / stabilisations, transitional-provision-only supplements that
  merely re-date existing requirements with no ECU-visible content. When a single act mixes hardware-only and
  ECU-visible content, it is an event (rated on its ECU-visible content).
- **How I decide ECU-visible for domain S.** Domain S ECUs: seat adjustment, seat heating, occupant classification,
  seat-belt reminder (SBR), pretensioner / load-limiter control, head restraints (active / powered), child-restraint
  interfaces (e.g. CRS detection, airbag deactivation). An amendment is an event in S when it changes SBR logic or
  warning requirements, occupant detection / classification, airbag suppression / deactivation signalling, powered
  seat / head-restraint control behaviour, or similar electronically implemented functions. Strength, anchorage
  position, dummy, sled and geometry changes are not events.
- **How I decide ECU-visible for domain B.** BMS, OBC, charge communication controller, DC-DC, HV energy-data
  interfaces. Events include: new or changed battery data / state-of-health / passport data and their access;
  monitors (durability, SOCE/SOH monitors, thermal-event warning that requires detection logic in the BMS);
  charging communication protocols; cybersecurity and software-update obligations; EMC-in-charging-mode changes are
  events only when they change what the charging electronics must do in a way visible to the ECU (otherwise
  test-procedure only, not an event). Purely mechanical / crash / isolation-resistance test changes are not events;
  but a new requirement for the BMS to detect and warn (e.g. thermal propagation warning) is an event.
- **One act, one event.** Adoption and entry into force are one row (two dates). Each dated amendment counts once.
- **Never twice.** An act amending two listed instruments counts under the one that comes first in
  `L1_instruments.md` (row order B01..B35, S01..S16, B36, B37, S17..S26); the other is noted.
- **EU base acts** (B01, B02, B35, S13): every delegated / implementing act adopted under them, and every
  legislative amendment of the base act itself, is a candidate event; the S1 list is a starting point only. The base
  act itself counts once as a first adoption if adopted in the window and meeting (a)-(c). For S13 (GSR2) and B02,
  only acts touching the named provisions' domain ECUs count (seating / SBR / occupant classification for S13;
  battery durability / monitors / in-vehicle battery data for B02).
- **Vehicle-level instruments** (B05 R155, B06 R156, B14 GB 44495, B15 GB 44496): one row per event, `domain = B`,
  classified for the domain-B ECU (L-1). The double counting into S is done by the analysis, not by me.
- **UN regulations:** each supplement or series that meets (a)-(c) is one event. A "Collective amendment" or a
  WP.29 document that amends several regulations counts under each regulation it amends only if those are distinct
  supplements (UN practice: each regulation gets its own supplement number, so each is its own act).
- **Standards:** each new edition, amendment or corrigendum-with-technical-change published in the window is an
  event if it meets (a)-(c) for the domain. A first edition published in the window is an event if it meets (a)-(c).

### 1.2 The four classes and where I draw the lines

Most demanding consequence stated or clearly implied, for an ECU already fielded:
- `software-only`: parameter, threshold, logic, warning-text, data-field or reporting changes that an existing ECU
  with an existing update path can absorb; process clarifications that do not require new hardware or re-approval.
- `memory-or-crypto`: a new communication stack (e.g. ISO 15118-20 vs -2, new PLC / wireless link layer), a new
  cryptographic service needing secure storage / HSM (certificates, PnC, signed data), or materially more storage
  (new long-term logging of battery data, passport data held on-board).
- `hardware-or-recert`: a new physical interface or connector, a new sensor, a new compute class, OR a requirement
  that re-opens type approval: already-approved vehicle types must be re-approved or must newly comply by a stated
  date to remain on the market (pre-registration §2 definition). New series of amendments to UN regulations with
  transitional provisions that end acceptance of earlier series approvals for registration fall here when the
  change is ECU-visible. Mandatory new requirements applying to all new registrations by a date (e.g. R155/R156
  from July 2024; GB 44495/44496 for existing types) are `hardware-or-recert` on the re-approval criterion.
- `cannot judge`: content not readable (L-3 partial access), or the text does not allow a reading.
- Line-drawing: when a new requirement is optional ("at the request of the manufacturer", alternative compliance
  route), I rate by the mandatory part. Supplements to UN regulations (which by WP.29 practice do not invalidate
  existing approvals) are normally `software-only` unless they add a new interface/stack. A series of amendments
  is assessed for whether its transitional provisions force re-approval of existing types.

### 1.3 Access states (L-3)

- `full`: the body's own dated change history read, and the text or the body's own summary of each change.
- `partial`: identifiers and dates read from the body's own catalogue / metadata / notice pages, but not what changed.
  Under `partial`, a new edition is an event only if the body's own catalogue entry (title, abstract, amendment
  title) shows its subject is data, telemetry, communication protocol, cybersecurity, software update or monitoring;
  then `class = cannot judge` (unless the abstract allows more), `confidence = low`. A new edition of a
  hardware / mechanical / crash-titled instrument with no readable content goes into these notes as
  `unreadable edition` and is not counted.
- `none`: no body-published history reachable by an allowed route. Blocks (HTTP 403, CAPTCHA, WAF, login,
  verification) are recorded, never bypassed.
- Search-engine listings may locate; never source. Trade press, resellers and other-body adoptions (EN, BS, DIN,
  national adoptions) are never sources.

### 1.4 act_id forms (L-4)

- EU act: CELEX, e.g. `32025R1707`; adoption date = date printed on the act.
- UN regulation: `R100-03` (series), `R100-02-S5` (supplement to a series); for supplements to the original
  version, `R156-00-S1`. Adoption date = WP.29 adoption (session) date; if only OJ / entry-into-force date is found,
  that date with `note = EIF date`.
- UN GTR: `GTR22` (establishment), `GTR22-A1` (amendment); AC.3 adoption date.
- FMVSS: Federal Register citation of the final rule, e.g. `89 FR 100660`; FR publication date.
- Standard: identifier with edition date, `ISO 15118-20:2022`, `SAE J3400_202412`, `GB/T 32960.3-2025`,
  `IEC 61851-1:2017`, amendments as `IEC 61851-23:2014/AMD1:2023` style; publication date.
- Dates YYYY-MM-DD. When only a month is known I use the first of the month and say so in `note`.

### 1.5 Window

Adoption (or, for standards, publication) date from 2016-01-01 to 2026-12-31 inclusive. Acts adopted in the window
with later application are included with both dates. Acts adopted before 2016 are excluded even if they apply in the
window. Acts adopted after 2026-12-31 do not exist yet (rating date 2026-11-10).

---

## 2. How the ledger was built (written after reading)

### 2.1 Routes actually used

| Instrument type | Route used | What it gave |
|---|---|---|
| UN regulations (R10, R14, R16, R17, R25, R44, R80, R100, R129, R145, R155, R156, R170) | unece.org returned HTTP 403 (Cloudflare) and was not used. **UN ODS** (`documents.un.org/api/symbol/access?s=...`, plain document links): WP.29 session reports ECE/TRANS/WP.29/1120 to /1192 (168th to 199th sessions, March 2016 to June 2026). Their AC.1 voting tables list each adopted amendment with its WP.29 document. Every adopted document for a listed regulation was then fetched and read. GRE/GRSP working documents were read where a series needed its justification. | Adoption date = AC.1 vote date from the session report. Text of each change. |
| UN GTR 22 | Same session reports (AC.3 sections), plus the adopted documents 2022/45 and 2024/81, and status report 2024/82 | AC.3 dates and content |
| EU acts | EUR-Lex "ALL" pages (the modified-by lists), the Publications Office SPARQL endpoint (based-on / amends / implements links) and EUR-Lex HTML texts | Every act adopted under or amending each base act |
| FMVSS | eCFR versioner (amendment dates per section), Federal Register API (all RULE documents citing 49 CFR 571 since 2016-01-01, 67 hits), Federal Register full texts | Final rules and their content |
| ISO | iso.org returned HTTP 403 (Cloudflare) and was not used. I used ISO's own **open-data deliverables catalogue** (JSONL published by ISO at isopublicstorageprod.blob.core.windows.net), which gives reference, publication date, replaces / replaced-by and the abstract. | Editions and dates. Abstracts only, so access is `partial`. |
| IEC | webstore.iec.ch publication pages. They include the lifecycle (edition history) JSON and the abstract with IEC's own list of "significant technical changes". | `full` for the editions. Corrigendum pages show no content. |
| GB | openstd.samr.gov.cn metadata pages and its catalogue list (std_list), plus std.samr.gov.cn records | Edition numbers and dates only (`partial`) |
| SAE | sae.org returned an AWS-WAF challenge shell for every SAE page (HTTP 200, 15 274 bytes, `captcha-sdk.awswaf.com`). Not bypassed. | `none` |

The 200th WP.29 session (November 2026) had no report available when I read. Anything it adopted is not in the ledger.

### 2.2 Order of work (disclosure)

The ledger rows and `instruments_B.csv` were written and committed in my order (`orders.B`), every 10 instruments.
The **research was not done strictly in that order**. To find which routes worked I first probed one instrument
per publisher (ISO, IEC, SAE, openstd, eCFR, EUR-Lex, ODS). That probe returned the ISO and IEC edition lists for
B16-B22, B36, S19 and S20 before their turn. Because the UN session reports cover every UN regulation at once, the
UN, EU and FMVSS sources were then also gathered in bulk, by source type. Each instrument's rows were decided from
its own documents. Nothing was reconciled across instruments except the never-twice rule.

### 2.3 Classification conventions as applied (additions to §1.2)

- **Re-opens type approval.** I applied the pre-registration definition literally: already-approved types must be
  re-approved, or must newly comply by a stated date to stay on the market. So a new UN series whose transitional
  provisions phase out earlier approvals is `hardware-or-recert` when its change is ECU-visible. So is a new
  mandatory act applying to all new registrations by a date: R155, R156, Euro 7 and its implementing acts, the
  Batteries Regulation Art. 14, FMVSS 305a, and the FMVSS 208 rear SBR. This criterion drives most of my
  `hardware-or-recert` calls. On content alone, several of them (R156-01 RXSWIN, 2025/1706 data integrity) would be
  `software-only` or `memory-or-crypto`.
- **Supplements to UN regulations** (which do not invalidate existing approvals) are rated on content. They are
  usually `software-only` (warning logic, signals).
- **Parallel supplements** (the same text adopted as separate supplements to two series, e.g. R16-07-S6 and
  R16-08-S3, or R100-03-S4 and R100-04-S1) are separate documents, so each is its own act and its own row. A
  **single document** that is two supplements at once (2026/49 = R100-04-S3 and R100-03-S6) is one act and one row.
- **Optional alternatives** ("may", "at the request of the manufacturer", warning signal as an alternative to a
  mechanism) are not events by themselves.
- **Unreadable corrigenda.** A corrigendum whose text I could not read is noted and not counted, and the access state
  is not downgraded. By WP.29 / IEC practice a corrigendum corrects errors.
- **Domain S and child restraint products.** UN R44 and R129 and FMVSS 213, 213a and 213b regulate the child
  restraint product, not a vehicle ECU. Their amendments (dummies, CRS labels, CRS-side warning options) are not
  domain-S ECU events. Vehicle-side child-restraint interfaces (air-bag deactivation or suppression, occupant
  classification) are domain S.

## 3. Per-instrument remarks (in order B)

1. **S22 FMVSS 202**: no amendment in window. `full`.
2. **B31 SAE J2931/6**: `none` (SAE WAF).
3. **S11 FMVSS 210**: 89 FR 76236 (2024, alternative test device), 91 FR 33091 and correction (2026, obsolete text). Mechanical: no events.
4. **S24 FMVSS 213**: CRS product standard. Rules 2022-2026 change dummies, side impact, registration and labels: no events.
5. **S25 SAE J800**: `none`.
6. **B26 SAE J2847/2**: `none`.
7. **S02 UN R16**: 5 events. 07 series (rear and passenger SBR), 07-S3 (second-level warning), 07-S6 and 08-S3 (rear visual warning, occupancy option), 09 series (removable-seat SBR connection). Not events: the 08 series (2018/141, air-bag warning labels), the information-document supplements (2019/104, 2019/105, 2020/51, 2021/112, 2021/113 and Corr. 2021/111), ISOFIX/booster/anchorage/test supplements, and the 10 series (2024/118). The 10 series moved the SBR and installation provisions out of R16 into two new UN Regulations, which are not on the list (one is the proposal for a new UN Regulation [173] in 2024/152). I did not record that transfer as an R16 event. Supplements to the 10 series: not events.
8. **S09 FMVSS 208**: 3 events. 89 FR 67869 (CRS list for suppression tests, low confidence), 90 FR 390 (rear SBR), 91 FR 17144 (SBR IFR). 87 FR 18560 is counted under S08 (never twice).
9. **B22 IEC 61851-24**: 2023 edition 2, `software-only`, low.
10. **B24 SAE J3400**: `none`.
11. **S01 UN R14**: supplements 7-9 to 07, 08 and 09 series and later supplements: anchorage geometry and strength, ISOFIX moved to R145. No events.
12. **B25 SAE J2847/1**: `none`.
13. **B06 UN R156**: 2 events (2020 adoption; 01 series 2025). Supplement 1 to the original version (2026, certificate and declaration models): not counted.
14. **B27 SAE J2847/3**: `none`.
15. **B36 ISO 6469-1**: `partial`. 2019 edition and Amd 1:2022 ("Safety management of thermal propagation") are unreadable editions (see §5).
16. **B03 UN GTR 22**: 2 events.
17. **S15 GB 15083**: `partial`. 2019 edition is an unreadable edition.
18. **B02 EU 2024/1257**: 4 events (base act, 2025/1706, 2025/1707, 2026/1764). 2025/1706 was dropped by S1 on its title but is counted for its battery-durability data-integrity provisions. Non-battery acts 2026/1214, 2026/1216 and 2026/1762 are not events.
19. **B28 SAE J2847/6**: `none`.
20. **B05 UN R155**: 4 events (2020 adoption, S1, S2, S3).
21. **B11 GB 38031**: `partial`. 2020 and 2025 editions are unreadable editions.
22. **S04 UN R25**: Suppl. 2 to 04 (2024): mechanical, no events.
23. **S19 ISO 17373**: `partial`. No new edition in window.
24. **B20 IEC 61851-1**: 2017 edition 3, `software-only`, low. COR1:2023 unread corrigendum.
25. **S08 FMVSS 207**: 87 FR 18560 (ADS occupant protection; its FMVSS 208 air-bag suppression and telltale content). Counted here because 207 is the first listed instrument the act amends. 91 FR 33098 (obsolete text): not an event.
26. **B04 UN R100**: 9 events (see the ledger). Non-events listed in `instruments_B.csv`. The 04 series (2024) adds only emergency-service identification labels: not an event.
27. **S12 FMVSS 225**: 87 FR 18560 counted under S08. 90 FR 1288 (anchorage ease of use) is mechanical.
28. **B30 SAE J2931/4**: `none`.
29. **S17 UN R80**: mechanical, no events.
30. **B14 GB 44495**: 1 event, `cannot judge`. An undated "Amendment No. 1" note on the catalogue page is not recorded (no date).
31. **S21 UN R170**: no events. The new regulation (2023) allows a visual and audible warning only as an alternative to a mechanism.
32. **B29 SAE J2931/1**: `none`.
33. **S10 FMVSS 209**: no amendment in window.
34. **S18 UN R145**: no events. The new regulation (2017) transferred R14's ISOFIX provisions without change (EU 2022/1398 recital 8 says so), including the existing air-bag deactivation requirement. Later supplements and the 01 series are mechanical.
35. **B07 UN R10**: no events. 06 and 07 series and all supplements change EMC limits, test set-ups (charging harness layout), ADS test configurations and administrative items. The GRE justifications for both series were read. None changes the data, functions or process of the charging ECU.
36. **S05 UN R44**: child restraint products, no events.
37. **B32 SAE J2931/7**: `none`.
38. **B34 FMVSS 305a**: no events of its own. Its establishing rule 89 FR 104318 also amends FMVSS 305 and is counted under B33 by the never-twice rule. 91 FR 33111 only deletes cross-references.
39. **B15 GB 44496**: 1 event, `cannot judge`. Undated "Amendment No. 1" not recorded.
40. **S07 FMVSS 202a**: no events. The eCFR 2017-09-05 version has no matching Federal Register rule (editorial).
41. **B16 ISO 15118-2**: `partial`. Only the 2014 edition is published; the revision is still at DIS. No events.
42. **B23 SAE J1772**: `none`.
43. **B19 ISO 17409**: `partial`. The 2020 edition is an unreadable edition (electrical safety title; the abstract mentions control functions but the subject is electrical safety).
44. **B12 GB/T 18487.1**: `partial`. The 2023 edition is an unreadable edition: the title "general requirements" does not show a data or protocol subject. The 2015 edition predates the window.
45. **S26 FMVSS 213b**: CRS product standard, no events.
46. **B08 GB/T 32960.1**: 2 events (2016, 2025), `cannot judge`.
47. **B17 ISO 15118-20**: 2 events (2022 first edition, `memory-or-crypto` from the abstract; Amd 1:2026, `cannot judge`).
48. **B37 SAE J2929**: `none`.
49. **S13 EU 2019/2144**: 1 event (base act, SBR per UN R16 mandatory). 2022/1398 and 2025/1122 update only mechanical seating rows. The other delegated and implementing acts concern ADAS, EDR and similar: not domain S.
50. **S03 UN R17**: 09, 10, 11 and 12 series and supplements: seat and head-restraint strength and dynamic tests, labels. No events.
51. **B10 GB/T 32960.3**: 2 events, `cannot judge`.
52. **S20 ISO 13216-1**: `partial`. No edition in window.
53. **B35 EU 2023/1804**: no events. The obligations fall on recharging points. Recital-level advice to vehicle manufacturers in 2025/656 (ISO 15118-20) is not an obligation.
54. **B18 ISO 15118-8**: 2 events (2018 first edition, `hardware-or-recert` low from the abstract; 2020 edition 2, `cannot judge`).
55. **B13 GB/T 27930**: 1 event (2023), `cannot judge`. The 2015 edition predates the window. GB/T 27930.2-2024 is a separate part, not this instrument.
56. **B09 GB/T 32960.2**: 2 events, `cannot judge`.
57. **S14 GB 14167**: `partial`. The 2024 edition is an unreadable edition.
58. **S16 GB 11550**: `partial`. No edition in window (2009 edition, now abolished).
59. **S06 UN R129**: child restraint products, no events.
60. **B33 FMVSS 305**: 2 events (82 FR 44945; 89 FR 104318).
61. **B01 EU 2023/1542**: 1 event (base act). 2024/1781 (registry upload of the identifier), 2025/606 (recycling efficiency), 2025/1561 (due diligence), 2025/2289 (waste reporting), 2026/1738 (Annex I substance restrictions) and 2026/1770 (portable batteries) are not ECU-visible. No passport, carbon-footprint or SoH delegated or implementing acts were found as adopted.
62. **B21 IEC 61851-23**: 1 event (2023 edition). COR1:2016 unread corrigendum.
63. **S23 SAE J826**: `none`.

## 4. Blocked routes (never bypassed)

- **unece.org**: HTTP 403, Cloudflare "you have been blocked". All UN material came through documents.un.org document links instead.
- **iso.org**: HTTP 403, Cloudflare "Just a moment" challenge. I used ISO's open-data catalogue instead.
- **sae.org**: AWS-WAF captcha shell on every standard page. All 13 SAE instruments are `none`.
- **documents.un.org search**: the search API uses a WebAssembly check. I did not use it, and used direct symbol links only.
- **openstd.samr.gov.cn full texts**: an image viewer behind a verification step. Not attempted. Metadata only.
- Corrigenda not retrievable as PDFs from ODS: 2016/100 (R44), 2016/104, 2019/58 and 2019/59 (R129), 2023/133 (R100 Corr. 1 to 03), and 2025/123-125 (R100, French-only corrigenda).

## 5. Unreadable editions (L-3; not counted)

| Instrument | Edition (catalogue date) | Why not counted |
|---|---|---|
| B11 GB 38031 | GB 38031-2020 (2020-05-12) | title names traction battery safety only; no content readable |
| B11 GB 38031 | GB 38031-2025 (2025-03-28) | same |
| B12 GB/T 18487.1 | GB/T 18487.1-2023 (2023-09-07) | title (conductive charging system, general requirements) does not show a data/protocol/monitoring subject; no content readable |
| B19 ISO 17409 | ISO 17409:2020 (2020-02-26) | electrical safety title and abstract |
| B36 ISO 6469-1 | ISO 6469-1:2019 (2019-04-16) | RESS safety title and abstract |
| B36 ISO 6469-1 | ISO 6469-1:2019/Amd 1:2022 (2022-11-10) | "Safety management of thermal propagation": fire/thermal safety title, no abstract |
| S14 GB 14167 | GB 14167-2024 (2024-09-29) | anchorage title |
| S15 GB 15083 | GB 15083-2019 (2019-10-14) | seat strength title |

## 6. What I could not follow, and what I did instead

- **unece.org as a route** was blocked. I used documents.un.org (named in the allowed routes). Every UN adoption date
  is the AC.1 or AC.3 vote date from the WP.29 session report, which is the L-4 preferred date.
- **ISO catalogue.** iso.org was blocked. I used ISO's own published open-data catalogue file. I treat it as "the
  issuing body's own catalogue"; it is not a reseller or a search listing. If the reviewer disagrees, B16-B19, B36,
  S19 and S20 would be `none`, and the four ISO events (B17 x2, B18 x2) would drop.
- **Research order** differed from `orders.B` (see §2.2). The recording and commit order followed it.
- **Undated GB amendment sheets** (GB 44495 and GB 44496, "第1号修改单") could not be dated from the body's
  catalogue. They are not recorded.
- **The 200th WP.29 session** (November 2026) is not covered; its report was not available.
- **Application dates** are filled only where the act states one that I read. For the EU base acts and Euro 7 the
  application date is my reading of the act's date provisions. They are marked as judgement in `note`.
- **No web search was used.** Every location came from the bodies' own pages, documents or APIs.
