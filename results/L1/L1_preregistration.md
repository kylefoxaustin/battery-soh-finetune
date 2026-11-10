# L1 pre-registration: the requirement-arrival ledger

**Question (brief §0).** Between 2016-01-01 and 2026-12-31, how many dated regulatory or standards events changed what
the battery / charging / power-conversion ECU must produce, store, sign, transmit or host? What fraction of them could
not be absorbed by a software update alone? How does that compare with the seat / interior domain?

**Status of this file.**
- Brief: [`briefs/L1/README.md`](../../briefs/L1/README.md). Requested by NEXT_TASK (reviewer, 2026-11-10), stage 1.
- Committed together with [`L1_instruments.md`](L1_instruments.md), **before any instrument's change history has
  been read**, and before either rater branch exists.
- The two-rater procedure is FR1-R's ([`../FR1R/FR1R_preregistration.md`](../FR1R/FR1R_preregistration.md) §4),
  reused except where named.

**Tags.**
- Every event is **SOURCED** (URL, document identifier, date).
- Every classification is **DERIVED-judgemental**.
- Both raters are language-model sessions, and the write-up says so beside κ (FR1 D-3).
- No dollar figures. ANGLES §B.1's option-value arithmetic takes L1's count as an input; it is not redone here.

---

## 1. Domains (closed)

| Domain | ECUs |
|---|---|
| **B: battery / charging / power conversion** | traction-battery management (BMS); on-board charging and charge communication (OBC, charging control unit, EVSE communication); DC-DC conversion; the vehicle's high-voltage energy data interfaces (battery passport, durability monitor, telemetry uploads) |
| **S: control, seat / interior** | seat adjustment, seat heating, occupancy classification, seat-belt reminder, belts and their pretensioner and load-limiter control, head restraints, child-restraint interfaces |

- Every instrument in `L1_instruments.md` carries **one domain**. Additions inherit the domain of the instrument that
  cites them.
- An event counts only if it reaches that domain's ECUs (§2).

**Vehicle-level instruments (disclosed asymmetry).**
- The brief lists UN R155, UN R156, GB 44495 and GB 44496 under domain B. They are vehicle-level:
  - cybersecurity management (R155, GB 44495);
  - software-update management (R156, GB 44496).
- They bind every ECU that is updatable or connected, which includes seat and occupancy ECUs.
- **Primary:** domain B, as the brief lists them.
- **Sensitivity V2:** their events also counted in domain S.
- **Sensitivity V0:** their events counted in neither domain.

**"Blind to domain" (ANGLES §C.1) is not achievable.** An instrument's title reveals its domain. The raters are blind
to each other, not to domain.

## 2. Instrument and event (closed)

### Instrument

An **instrument** is one of the following, applying to vehicles in at least one of the EU, the UN-1958 agreement
countries, China or the United States:
- a regulation, directive, global technical regulation or UN regulation;
- a national standard (GB, GB/T);
- an ISO, IEC or SAE standard;
- a formally adopted amendment or revision of any of these.

**Instrument list.** The list is `L1_instruments.md`. Nothing is added after this commit.

### Event

An **event** is a **dated** adoption, amendment, revision or entry-into-force of a listed instrument that changes at
least one of these for the instrument's domain ECU:
- **(a) data** the ECU must produce, store, sign or transmit: schema, rate, resolution, retention or access;
- **(b) functions** it must host: protocols, cryptographic services, update mechanisms or monitors;
- **(c) process** obligations that reach into its software lifecycle: software-update management, cybersecurity
  management, or type approval of software versions.

**Not an event:**
- a change that touches only hardware safety (crash, fire, venting, mechanical);
- a change that touches only a vehicle-level test procedure with no ECU-visible consequence;
- a purely editorial change, a corrigendum that changes no requirement, or a reaffirmation or stabilisation with no
  technical change.

**Counting rules.**
- **One act, one event.** The act is a document: an amendment, supplement, series of amendments, revision, new
  edition, delegated or implementing act. Its adoption and its entry into force are **one** event with two dates.
- **Never twice.** If one act amends two listed instruments, it counts once, under the instrument that comes first in
  `L1_instruments.md`. The other is noted.
- **EU base acts (CHOSEN, symmetric).** Delegated and implementing acts adopted under a listed EU base act belong to
  that base act's change history. Each is a candidate event of it. This applies to all four EU base acts on the list:
  2023/1542, 2024/1257, 2019/2144 and 2023/1804.
- **A first edition or first adoption** inside the window is an event when it meets (a)–(c).
- **The S1 list is a starting point, not a limit.** The acts S1 kept (`L1_instruments.md` §2) are listed for the
  raters, but each rater identifies **every** act adopted under a listed EU base act that meets the event definition,
  whether S1 kept it or not. S1 filtered by title, and a title can understate scope. For example, S1 dropped
  2025/1706 on its emissions title, while it kept an act that amends 2025/1706 "as regards in-vehicle battery
  durability".

### Window

- An event is in the window if its **adoption date** (or, for a standard, its publication date) is from 2016-01-01 to
  2026-12-31.
- Events adopted in the window with later application are included, with both dates.
- **Disclosed:** rating happens in November 2026, so the end of 2026 cannot be observed. The per-year means still
  divide by 11 years, which works against VOLATILE.

### Classification

Each event takes the **most demanding consequence stated or clearly implied**. Write exactly one of:

| Class | Meaning |
|---|---|
| `software-only` | Absorbable by a software update on an ECU already fielded, with no new interface, no new cryptographic hardware requirement and no re-certification of the control safety case |
| `memory-or-crypto` | Needs materially more storage, a secure element or HSM capability, or a new communication stack |
| `hardware-or-recert` | Needs a new interface, sensor or compute class, or re-opens type approval or the functional-safety case of the control software |
| `cannot judge` | The text does not allow a reading |

- **Order:** `software-only` < `memory-or-crypto` < `hardware-or-recert`.
- **Re-opens type approval:** a requirement that a vehicle type already approved must be re-approved, or must newly
  comply by a stated date, to stay on the market.

### Ledger file

`ledger_<A|B>.csv`, one row per event. Columns:
- `event_id`, `instrument_id` (as in `L1_instruments.md`), `domain`, `act_id` (the document identifier);
- `adoption_date` and `application_date` (ISO dates; `application_date` blank if the same);
- `jurisdiction`, `what_changed` (one line), `class`, `confidence` (`low` / `medium` / `high`);
- `source_url`, `source_type` (`primary` or `body summary`), `note`.

## 3. Search protocol (stage 1; run before any change history is read)

The protocol builds the instrument list from **titles, scope statements and normative references only**.

**Who runs it.**
- A fresh-context sub-agent of this session (the **screener**), which is not a rater.
- Its launch prompt is committed as `L1_screen_prompt.md`.
- Its raw record is `L1_screen.json`: every URL, hit count and addition decision.

### S0. Seed list

The instruments named in brief §3, as written:

| Domain | Seed instruments |
|---|---|
| **B** | EU 2023/1542 and its delegated / implementing acts; EU 2024/1257 (battery-durability provisions); UN GTR 22; UN R100; UN R155; UN R156; UN R10 (charging-mode provisions); GB/T 32960.1, .2, .3; GB 38031; GB/T 18487.1; GB/T 27930; GB 44495; GB 44496; ISO 15118-2, -20, -8; ISO 17409; IEC 61851-1, -23, -24; SAE J1772; SAE J3400; SAE J2847 series; SAE J2931 series (the bidirectional parts); FMVSS 305 / 305a; EU 2023/1804 (vehicle-side obligations) |
| **S** | UN R14, R16, R17, R25, R44, R129; FMVSS 202a, 207, 208, 209, 210, 225; EU 2019/2144 (provisions naming seat-belt reminders or seating); GB 14167, GB 15083, GB 11550 |

**Series and parts.** Named parts are listed individually. "SAE J2847 series" and "SAE J2931 series" are expanded
into their parts **by title**. A part is kept when its title names vehicle-to-grid, bidirectional power transfer or
communication between the vehicle and the charging or grid side.

### S1. EU acts adopted under a listed base act

- For each of the four EU base acts, a EUR-Lex search finds the acts adopted under it: delegated and implementing
  acts citing it as their legal basis.
- From **titles only**, an act is kept if its title concerns the listed provisions:
  - 2023/1542: any;
  - 2024/1257: battery durability, monitors or in-vehicle data;
  - 2019/2144: seat-belt reminders, seating or occupant classification;
  - 2023/1804: vehicle-side obligations.
- Query, hit count, and the kept and dropped titles are recorded.
- **Kept acts are not new instruments.** They are listed under their base act as candidate events, with title and
  identifier only.

### S2. Landing page, title and scope

- For each instrument: its official landing page (EUR-Lex, UNECE, eCFR / NHTSA, ISO, IEC, SAE, SAC /
  openstd.samr.gov.cn), its exact title, and its scope statement, quoted in no more than three sentences.
- **What the screener reads.** A script extracts and prints only the title, the scope clause and the
  normative-references clause.
- **What it does not read.** The front matter that lists amendments, any history or version list, and any
  transitional-provisions section are never printed or read.

### S3. Normative references, one level (CHOSEN)

**Where references are taken from.**

| Instrument type | Source of its references |
|---|---|
| Has a normative-references clause | That clause |
| UN regulations and EU acts (no such clause) | Every standard or instrument identifier cited in the requirements text and annexes, extracted by script as identifier + clause, excluding the front matter, the transitional provisions and any bibliography |
| FMVSS | The standard's own text, plus its incorporations by reference in 49 CFR 571.5 that it names |

**When the text is not freely accessible as text** (most ISO, IEC and SAE texts and some GB texts):
- the references are taken from a free preview that shows the normative-references clause, when one exists;
- otherwise the instrument is logged **"references not accessible"** and adds nothing.

**Additions.** A cited document is added only when it passes all three tests, judged from its own title and scope:
1. it is an instrument under §2;
2. its scope names road vehicles, electric vehicles, or the vehicle-to-supply-equipment charging interface;
3. its title or scope concerns the citing instrument's domain ECUs (§1).

**Bounds.**
- **One level only.** The references of an added instrument are not screened. This keeps the list finite, since the
  ISO 15118 references fan out into general networking and security standards.
- A citation of an instrument already listed adds nothing; it is counted.

**Hit counts per instrument:** references read; passing test 1; passing test 2; passing test 3; added; already listed.

**Addition log:** each added instrument, which instrument cites it, the clause, the three test outcomes, and the
title and scope it was judged on.

## 3b. Result of the screen, and access (written after the screen, before any change history is read)

**Count.** The screen produced **63 instruments**:

| Domain | Seed | Added by S3 | Total |
|---|---|---|---|
| B | 35 | 2 | 37 |
| S | 16 | 10 | 26 |

The full record is in `L1_instruments.md` and `L1_screen.json`. The screener's deviations D1–D11 are listed there.

**The additions are asymmetric because of access, not because of the domains.**
- S3 could read references only where the text was free as text:
  - UN regulations, through their EUR-Lex OJ publications, since unece.org returned HTTP 403;
  - EU acts;
  - FMVSS.
- It could not read them for any ISO, IEC, SAE or GB text: iso.org returned HTTP 403, sae.org a bot challenge, the
  IEC previews HTTP 403, and the GB texts sit behind an image viewer with a verification step.
- **25 of 35 domain-B seeds** gave no references. Only **3 of 16 domain-S seeds** did not. Domain S therefore gained
  10 instruments and domain B only 2.
- Counting the additions would lower R through accessibility alone.

**CHOSEN, for the reviewer to confirm before rating.**
- The deciding readouts use the **seed list only** (51 instruments: B 35, S 16). These are the instruments the brief
  itself named for both domains.
- The 12 additions are still rated by both raters. They enter the sensitivity **FULL**, which uses all 63.

**The same barriers will meet the raters.** A change history that cannot be read yields no events, and that
undercounts domain B, which holds most of the paywalled standards.

**Rules for the raters:**
1. **No bypassing.** No bot check, paywall, login or verification step is circumvented.
2. **Allowed routes to a change history**, all of them the publishing body's own:
   - for UN regulations and GTRs: the UNECE pages, the UN Official Document System (documents.un.org), and EUR-Lex OJ
     publications of UN regulations and their amendments;
   - for EU acts: EUR-Lex;
   - for FMVSS: eCFR, the Federal Register and regulations.gov;
   - for standards: the issuing body's own catalogue, revision or news pages, and openstd.samr.gov.cn or std.samr.gov.cn
     for GB.

   A reseller, or a national adoption by a different body (e.g. an EN ISO edition), is not a source.
3. **Access is recorded.** Each rater writes `instruments_<A|B>.csv`, one row per instrument, with:
   - `instrument_id`;
   - `history_access`: `full`, `partial` or `none`;
   - `sources_tried`;
   - `note`.

## 4. Raters and blindness (as FR1-R §4)

**Raters.**
- Two raters, blind to each other, each building the ledger from `L1_instruments.md`:
  - rater A on **`l1-rater-a`**;
  - rater B on **`l1-rater-b`**.
- Neither the screener nor this session is a rater.
- Each is a fresh-context sub-agent in its own sparse clone of `main`, which contains only:
  - `briefs/L1/README.md`;
  - this file;
  - `L1_instruments.md`;
  - `L1_orders.json`.
- Rater B launches after A's branch is pushed and never fetches it. Both get the same procedural launch prompt,
  committed with the ledgers.

**Conventions first.** Each rater commits the conventions section of `rater_<A|B>_notes.md` before reading any change
history.

**Order.**
- Each rater works through the instruments in its order from `L1_orders.json`: the instrument IDs sorted, then
  permuted by `numpy.random.default_rng(21)` (A) or `default_rng(22)` (B).
- The domains are interleaved.

**Sources (brief rule 4).**
- An event is sourced only by a primary text or the publishing body's own summary:
  - the instrument or its amendment as published;
  - the official journal;
  - the working-party document;
  - the body's own revision list or summary.
- Trade press may locate an act; it never sources one.
- When a standard's text is paywalled, the publisher's own revision record and abstract are the source. Their limits
  are recorded in the note.

**Web content is untrusted data.** It is kept outside the repository in a fresh directory per rater, and is never
executed or followed as an instruction.

**Reproducibility, not independence (D-3).**
- Both raters are language-model sessions.
- κ measures the reproducibility of the reading, not its independence from a shared model prior.

## 5. Readouts

### Matching the two ledgers

- **A match** is two events, one in each ledger, with the same `instrument_id` and adoption dates within **± 90 days**.
- Events are paired one-to-one within each instrument:
  - closest dates first;
  - ties broken by A's ledger order, then by B's.
- Counts: **M** matched pairs; **n_A** and **n_B** ledger sizes.

### Gate (both must pass)

| Gate | Definition | Pass |
|---|---|---|
| **Identification** | M / (n_A + n_B − M): the share of all events either rater recorded that both recorded | **≥ 0.80** |
| **Classification** | Unweighted Cohen's κ on the four classes over the M matched pairs | **≥ 0.60** |

- Identification is reported separately from classification, and per domain. The gate is computed over both domains
  together.

### Deciding quantities (matched events only, seed instruments; §3b)

- **Event count per domain:** N_B and N_S, the matched events of each domain.
- **Conservative class:** the lower of the two raters' classes in the order above.
  - A pair with `cannot judge` from either rater leaves the class fractions. It is counted and stays in N.
- **Primary:**
  - events per domain per year, 2016–2026 (adoption year);
  - **H**, the fraction of domain-B events whose conservative class is `hardware-or-recert`, with a Wilson 95 % CI;
  - **MC**, the fraction of domain-B events whose conservative class is `memory-or-crypto` or above, with a Wilson
    95 % CI. MC is the deciding fraction.
- **Ratio R = N_B / N_S.**
  - If N_S = 0, R is reported as "∞ (N_S = 0)".
  - For the decision, R = ∞ satisfies R ≥ 3 if N_B ≥ 3, and never satisfies R < 1.5.

### Also reported (none deciding)

**Events:**
- MC and H for domain S;
- events by jurisdiction, by instrument and by class;
- the per-year table by **application** year;
- each rater's own counts and fractions;
- the **union** count (M + unmatched events from either rater).

**Sensitivities:**
- **CN0:** China-only instruments excluded (ANGLES §C.1);
- **V2 / V0:** vehicle-level instruments counted in both domains / in neither (§1);
- **FULL:** all 63 instruments, including the S3 additions (the primary is the seed list, §3b);
- **ACC:** both domains restricted to instruments that **both** raters marked `full` or `partial`.

**Access table:** `history_access` per instrument and rater; counts by domain.

**Records:**
- identification agreement per domain;
- κ per domain;
- every unmatched event and every class disagreement, listed and never reconciled.

## 6. Decision (domain B, matched events, conservative class; checked in this order)

| Verdict | Condition |
|---|---|
| **UNGATED** | Identification < 0.80, **or** κ < 0.60 |
| **ACCESS-LIMITED** | **Both** raters record `history_access = none` for ≥ **1/3** of the seed instruments of **either** domain. The counts are then a lower bound for that domain, and R is not read. MC and H are reported. |
| **VOLATILE DOMAIN** | N_B ≥ **11** (≥ 1 event a year over the 11 years 2016–2026) **and** MC ≥ **25 %** with Wilson lower bound > **10 %** **and** R ≥ **3** |
| **STABLE DOMAIN** | N_B ≤ **5** (< 0.5 a year) **or** MC < **10 %** |
| **UNCLEAR** | anything else |

**Kill for ANGLES §B.1:** STABLE DOMAIN, **or** R < **1.5**. This is stated beside the verdict.

The other kill named in ANGLES §C.1 is a fielded MCU-tier part that absorbed every event by software update. That
needs product evidence. L1 does not test it, and says so.

## 7. Outputs (stage 2, after approval)

**Stage 1 (with this commit):**
- `L1_instruments.md`, with hit counts, the addition log and the screener's deviations;
- `L1_screen.json`;
- `L1_screen_prompt.md`;
- `L1_orders.json`.

**Stage 2:**
- on each rater's branch: `ledger_<A|B>.csv`, `instruments_<A|B>.csv`, `rater_<A|B>_notes.md` and the launch
  prompt;
- `analysis/L1_agreement.py`, written before either ledger is read;
- `results_L1.md`: verdict first, the per-year table, and κ with the D-3 disclosure beside it;
- `l1.json`;
- the index rows;
- dated notes under ANGLES §B.1 and SYNTHESIS §2.

## 8. Deviations

Any change after this commit is a numbered deviation (L-1, …). After any change history has been read, none of these
moves:
- the instrument list, and the choice of the seed list as primary;
- the access rules (§3b);
- the domains;
- the event definition and counting rules;
- the classes;
- the matching rule;
- the gates;
- the decision table.

---

## 9. Reviewer approval and deviations L-1 … L-5 (2026-11-10, stage 1 → stage 2; before any change history is read)

Stage 1 (`af2d5cb`) is **approved**. The reviewer checked: the seed list is the brief's own; the 12 additions each
carry a citing clause and the three test outcomes; the instrument table carries no edition year, amendment date or
change description (the only years in it are act identifiers and repealed-regulation numbers inside EU titles, and the
1958/1998 Agreements); `L1_screen.json` holds no amendment dates (the only ISO dates in it are the eCFR versioner
fetch date); the two rating orders reproduce from `default_rng(21)` / `default_rng(22)` over the 63 sorted IDs
(longest same-domain run 8 and 5); the screener's blind-reading breaches D5 (a)–(e) are disclosed and the screener is
not a rater. The three choices flagged in the status line are decided below. **These deviations bind both raters;
they are part of this file, which is in the raters' sparse clones.**

### L-1. Vehicle-level instruments: V2 is the primary for N_S and R (was: domain B only)

UN R155, UN R156, GB 44495 and GB 44496 bind every ECU that is updatable or connected, which includes the seat and
occupancy ECUs. They are real obligations of the domain-B ECU, so their events stay in domain B and **N_B, MC and H are
unchanged**. For the comparison they are the common floor, not what is specific to B, and counting them on one side
only would manufacture R. So:

- **Primary:** each matched event of a vehicle-level instrument is counted once in N_B **and** once in N_S.
  R = N_B / N_S with that N_S. The decision table is applied to these numbers.
- **V1 (sensitivity):** the brief's listing, vehicle-level events in domain B only (the former primary).
- **V0 (sensitivity):** vehicle-level events in neither domain.
- The raters write one row per vehicle-level event, `domain = B`, classified for the domain-B ECU. The domain-S class
  fractions (non-deciding) are reported twice: without the vehicle-level events, and with them carrying the B class
  over (not re-rated).

This moves R toward 1 and therefore works against VOLATILE. It is decided before any change history is read.

### L-2. ACCESS-LIMITED is a qualifier with bound logic, not a terminal verdict (was: "R is not read")

A domain is **access-limited** when both raters record `history_access = none` for ≥ 1/3 of its seed instruments
(B: ≥ 12 of 35; S: ≥ 6 of 16). More events can only raise a limited domain's N, so N of that domain is a **lower
bound**, and the decision table is read as follows:

| Limited | What can be established | What cannot (reads **UNCLEAR (ACCESS-LIMITED)**) |
|---|---|---|
| **B only** | N_B ≥ 11; R ≥ 3 (R is then a lower bound, R_lb = N_B,lb / N_S) — so **VOLATILE DOMAIN** is reachable | N_B ≤ 5 (STABLE by count); the kill R < 1.5 |
| **S only** | N_B conditions; R < 1.5 and STABLE (R is an upper bound) | R ≥ 3, so VOLATILE is not reachable |
| **both** | N_B ≥ 11; MC and H | R in either direction |

- A verdict reached while a domain is limited carries the qualifier in its name, e.g. `VOLATILE DOMAIN
  (ACCESS-LIMITED, B: 14 of 35 seeds unread)`.
- MC and H are computed on the recorded events. They are not bounds in either direction. The verdict line states
  their basis: "MC on N events from k of 35 seed instruments; unread: <list>". The write-up names the unread
  instruments and gives no number for them.
- The ACC sensitivity (§5) stays as pre-registered.
- The gates (§5) are computed over the events both raters could reach; an instrument with `none` from both raters
  contributes no events and does not enter identification agreement.

### L-3. Access states, and events under partial access

`history_access` per instrument and rater:

| State | Meaning |
|---|---|
| `full` | the body's own change history (editions / amendments with dates) was read, **and** the text or the body's own summary of each change |
| `partial` | edition or amendment identifiers and dates were read from the body's own catalogue, metadata or notice pages, but not what changed |
| `none` | no body-published history reachable by an allowed route (§3b rule 2) |

**Events under `partial` access.** A new edition or amendment found under `partial` access is an event **only when the
body's own catalogue entry (title, abstract or amendment title) shows that its subject is (a), (b) or (c)** of §2 —
data, telemetry, communication protocol, cybersecurity, software update, monitoring. Then `class = cannot judge` unless
the abstract allows more, and `confidence = low`. A new edition of an instrument whose title names only hardware,
mechanical or crash safety, with no readable content, is logged in `rater_<A|B>_notes.md` as `unreadable edition` and
**not** counted. The same rule applies in both domains.

**Search-engine listings** of a publisher's page may be recorded in `sources_tried` and may locate an edition; they
never source an event (the status of trade press, brief rule 4).

### L-4. Act identifiers and matching

So that the identification gate measures the ledgers and not the raters' naming, `act_id` is written in one of these
forms:

| Source | `act_id` form | `adoption_date` |
|---|---|---|
| EU act | CELEX number, e.g. `32025R1707` | the adoption date printed on the act |
| UN regulation | `R100-03` (series of amendments); `R100-02-S5` (Supplement 5 to the 02 series) | the WP.29 adoption date; if only the OJ or EIF date is found, that date, with `note = EIF date` |
| UN GTR | `GTR22-A1` (Amendment 1); `GTR22` (establishment) | the AC.3 / WP.29 adoption date |
| FMVSS | the Federal Register citation of the final rule, `89 FR 100660` | the Federal Register publication date |
| Standard | identifier with its edition date, `ISO 15118-20:2022`, `SAE J3400_202412`, `GB/T 32960.3-2025` | the publication date |

Matching (§5) proceeds in two passes within each `instrument_id`: **(1)** identical `act_id` after normalisation
(case, whitespace and punctuation removed); **(2)** the pre-registered ± 90-day rule on `adoption_date` for the events
still unmatched. Pass 1 is added because WP.29 adoption and entry into force are typically six to eight months apart,
and two raters recording different dates of the same act must still match.

### L-5. Seed list primary: confirmed; what the verdict line carries

The seed list (51 instruments) is the primary, as §3b proposes: the S3 additions depend on which texts were readable,
and that readability is concentrated in domain S. The verdict line reports the primary verdict and, when they differ,
the verdicts under **FULL** (63 instruments) and **V1**, each in one clause. The kill is evaluated under the primary;
if it fires under V1 or FULL only, that is stated beside it.

### Stage 2 order (binding)

1. `analysis/L1_agreement.py` is written and committed on `main` **before** either rater branch is fetched; it
   implements §5 with L-1, L-2 and L-4.
2. The rater launch prompt is committed as `results/L1/L1_rater_prompt.md` on `main` **before** rater A is launched.
3. Rater A (`l1-rater-a`), then rater B (`l1-rater-b`), as §4.
4. The rest as §7.
