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
