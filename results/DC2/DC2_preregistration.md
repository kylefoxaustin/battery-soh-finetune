# DC2 pre-registration: the ramp-spec audit

**Question (brief §0).** Among public specifications and rules that constrain how a large load's real power may vary in
time, what quantity is limited, over what measurement or compliance window, with what excursion allowance, at which
measurement point? Does any binding requirement have the window-and-allowance shape in which DC1 found history to pay
(a 1–60 s window with ~0.5 % or more of intervals allowed to exceed)?

**Status of this file.**
- Brief: [`briefs/DC2/README.md`](../../briefs/DC2/README.md). Requested by NEXT_TASK (reviewer, 2026-11-10), stage 1.
- Committed together with [`DC2_instruments.md`](DC2_instruments.md), **before any limit, window or allowance of any
  instrument has been read** by this session, by the screener, or by a rater, and before either rater branch exists.
- The two-rater procedure is L1's ([`../L1/L1_preregistration.md`](../L1/L1_preregistration.md) §4, with §9 L-2 …
  L-4), reused except where named.

**Tags.**
- Every requirement is **SOURCED** (URL, document, clause, quote of at most 25 words).
- Every class is **DERIVED-judgemental**.
- Both raters are language-model sessions, and the write-up says so beside κ (FR1 D-3).
- No dollar figures, rack counts or capex. DC1's numbers are not re-derived here; a DC1b re-run is a separate study.

---

## 1. Scope of an instrument in time

- The instrument is the document **as in force or as last published on the rater's reading date** (November 2026).
  There is no history window: DC2 asks what the specifications say now.
- An instrument with several editions is read in its current edition. A superseded edition is not rated.
- **A pending proposal is not a requirement.** A revision request, notice of proposed rulemaking, draft standard or
  tariff filing not yet approved by the body or commission that adopts it on the reading date yields no rows. The rater
  logs it in `rater_<A|B>_notes.md` as `pending: <identifier>, <status as printed>` and counts nothing from it.
- A listed instrument that the rater finds to contain no requirement under §2 (for example, a report that only
  describes load behaviour) yields no rows. The rater records `no requirement` in `instruments_<A|B>.csv`.

## 2. Definitions (closed; the brief's §2, filled in)

### Instrument

A public document that binds, or offers as a planning level, a limit on the behaviour of an electrical load or of the
equipment serving it. Instruments include:
- a grid code or connection code;
- an ISO / RTO protocol or planning guide;
- a regulator's rule;
- a utility tariff or interconnection requirement;
- a power-quality standard or technical report;
- an operator or vendor rack, shelf or facility specification.

A document that only *describes* load behaviour (a paper, a reliability assessment, a white paper without
requirements) is not an instrument; it is a **locator**.

**Instrument list.** The list is `DC2_instruments.md`. Nothing is added after this commit.

### Requirement

One clause of a listed instrument that states a limit on one of these, together with the window over which it is
assessed:
- a quantity of the **load's real power or its rate of change in time**;
- a voltage-quality quantity that such variation drives.

**Counting rules.**
- **One clause, one row.** A table of limits by category is one row per category. The category, as printed, goes in
  `category` (§4), which is blank when there is none.
- **Never twice.** One limit restated in two clauses of the same instrument (for example, a body clause and an annex
  table) is one row, under the clause that states the number. The other clause is named in `note`.
- **A different instrument repeating a limit** (for example, a tariff that adopts an ISO limit by reference) is a
  separate row of that instrument only if it states the limit itself. A bare cross-reference ("shall comply with X")
  is not a row. It goes in `note` on the instrument's line in `instruments_<A|B>.csv`.

### Deciding set

Requirements whose quantity is **real-power time variation**:
- `ramp rate` (MW/s, %/s, %/min);
- `step change`;
- `swing amplitude` (swing or oscillation amplitude);
- `smoothing or capping response` (power-smoothing or power-capping response time);
- `load change per interval`.

**Reported, not deciding:**
- `flicker` (Pst / Plt);
- `rapid voltage change`;
- `harmonics`;
- `power factor`;
- `ride-through`;
- `hold-up`;
- `other`.

These are the quantities the converter's own control loop meets without anticipation.

### Binding class (closed)

| Class | Meaning |
|---|---|
| `mandatory` | a code, protocol, rule or tariff condition that a connecting load must meet |
| `planning level` | a limit the network operator applies in assessment (as IEC 61000-3-7 planning levels) |
| `recommendation` | "should", a recommended practice, a guideline, an informative annex |
| `vendor capability` | a configurable feature (for example, a GPU or rack power-smoothing ramp setting): not a requirement on anyone |

**Binding** means `mandatory` or `planning level`.
- A clause written with "shall" inside a document the body itself designates as a guideline or recommended practice
  is `recommendation`.
- An operator's or vendor's specification that a supplier must meet to sell into it (for example, an OCP base
  specification's "shall") is `mandatory`, with `measurement_point` saying where it applies.

### Window class (closed)

The window is the measurement or assessment interval.

| Class | Interval *T* |
|---|---|
| `≤ 100 ms` | *T* ≤ 0.1 s |
| `100 ms – 1 s` | 0.1 s < *T* < 1 s |
| `1 – 60 s` | 1 s ≤ *T* ≤ 60 s |
| `1 – 15 min` | 60 s < *T* ≤ 15 min |
| `> 15 min` | *T* > 15 min |
| `not stated` | no interval stated, and no rate unit to infer one from (rule below) |

**Rate-unit rule (CHOSEN; DC2-specific).** Many ramp limits print a rate ("x %/min") and no measurement interval.
- When the clause states a measurement, averaging or assessment interval, that interval is the window.
- When it does not, the time unit of the printed rate is taken as the window (per second → 1 s; per minute → 1 min).
  `window_as_printed` then begins with `unit:`, for example `unit: MW/min`.
- A step or swing limit with no stated interval and no rate unit is `not stated`.
- **Sensitivity STATED:** every `unit:` window is set to `not stated`.

**A response time is not a window.** For `smoothing or capping response`, the window is the interval over which
compliance is assessed. When only a response time is printed, the window is that response time, with
`window_as_printed` beginning `response:`.

### Allowance class (closed)

The allowance is the share of intervals, samples or time that may exceed the limit.

| Class | Share *a* that may exceed |
|---|---|
| `hard` | none permitted (*a* = 0) |
| `tight` | 0 < *a* ≤ 0.1 % (e.g. a 99.9th percentile) |
| `loose` | 0.1 % < *a* ≤ 5 % (95th–99.5th percentiles) |
| `very loose` | *a* > 5 % |
| `event count` | a number of exceedances or events per hour / day / year, not a share |
| `not stated` | a limit with no statement of how often it may be exceeded |

- A limit stated as a plain maximum ("shall not exceed") with no allowance clause is `hard`, because the text permits
  no excursion.
- `not stated` is reserved for clauses whose text says the limit is assessed statistically, or "normally", or "as far
  as practicable", without saying how much exceedance is permitted.
- A percentile stated on another quantity than the limited one (for example, a 95th-percentile voltage limit inside a
  ramp clause) does not set the ramp clause's allowance.

### Shape (closed; the brief's rule, completed)

Shape is a function of window class and allowance class only:

| Window class | `hard` / `tight` | `loose` / `very loose` | `event count` / `not stated` |
|---|---|---|---|
| `≤ 100 ms` or `100 ms – 1 s` | electronics | electronics | electronics |
| `1 – 60 s` | reactive | **history** | cannot judge |
| `1 – 15 min` or `> 15 min` | reactive | reactive | reactive |
| `not stated` | cannot judge | cannot judge | cannot judge |

- The two cells the brief left open are filled here: `1 – 60 s` with `event count` / `not stated` allowance is
  `cannot judge`; any row with window `not stated` is `cannot judge`.
- Raters write `shape` as well. **The analysis uses the shape computed from the table**, from each rater's own window
  and allowance classes. Every row where the rater's written shape differs from the computed one is listed. Shape is
  not a separate judgement: a disagreement on shape is a disagreement on window or allowance.

## 3. Search protocol (stage 1; run before any limit is read)

The protocol builds the instrument list from **titles, scope statements and citations only**.

**Who runs it.**
- A fresh-context sub-agent of this session (the **screener**), which is not a rater.
- Its launch prompt is committed as `DC2_screen_prompt.md`.
- Its raw record is `DC2_screen.json`: every query, URL, hit count and addition decision.

### S0. Seeds (the brief's table, as written)

| Group | Seeds |
|---|---|
| **G: US grid / ISO / regulator** | ERCOT: Planning Guide and Nodal Protocol / Operating Guide sections on large-load interconnection and on Controllable Load Resource ramp-rate registration, and any 2025–2026 large-load protocol revision; NERC: the Large Loads task-force reports and guideline(s), the 2025 large-load alert, and any large-load standards project; PJM: large-load additions documents (2025–2026); the Texas PUCT rule(s) implementing SB 6 (2025) for large loads; FERC order(s) on large-load co-location (2025) |
| **U: US utility large-load clauses** | AEP Ohio data-centre tariff (2025); Dominion Energy Virginia large-load rate schedule (2025); Georgia Power large-load rules (2025); any other investor-owned-utility large-load tariff the screener finds by title that names ramp, step or fluctuation |
| **E: EU / UK / DE** | Regulation (EU) 2016/1388 (Demand Connection Code) and ENTSO-E's implementation guidance on it; the GB Grid Code Connection Conditions (demand step-change and fluctuation clauses); VDE-AR-N 4120 and 4130 (TAR Hochspannung / Höchstspannung) for Bezugsanlagen; the D-A-CH-CZ Technical Rules for the Assessment of Network Disturbances |
| **Q: power quality** | IEC TR 61000-3-7; IEC 61000-4-30; IEC 61000-4-15; IEEE 519; IEEE 1453; EN 50160 |
| **V: operator / vendor rack and facility** | OCP: Open Rack V3 base and power-shelf / BBU specifications, the 800 VDC ("Mt Diablo") specifications, and any OCP power-stabilisation specification or requirements document (2025–2026); NVIDIA: the GB200 / GB300 NVL72 power-smoothing and power-capping documentation and the 800 VDC architecture white paper; any Microsoft, Google or Meta published facility power-behaviour requirement found by title |

**Resolving a seed.** Each seed names a body and a subject, not always a document. The screener resolves it to
documents on the body's own site:
- **Named document.** It is listed.
- **"Sections on" a subject inside a large document** (the ERCOT Protocols, Planning Guide and Operating Guides; the GB
  Grid Code). The instrument is the document. The sections the screener locates **by heading** are recorded in the
  scope column, as the raters' starting points, not their limit.
- **"Any …" seeds** (a 2025–2026 large-load protocol revision; another utility tariff; an OCP power-stabilisation
  document; an operator's published requirement). The screener searches the body's own site, and the web for the
  body's own pages. It keeps a document whose **title** names large loads, data centres, ramp, step, fluctuation,
  oscillation, power stabilisation or power smoothing. Each query is recorded with its hit count and the kept and
  dropped titles.
- **Pending proposals** found while resolving a seed are listed with status `pending (as printed)`. Raters re-check
  the status under §1.
- **Locators.** A seed whose title and scope show that it only describes load behaviour (§2) is recorded as a
  **locator (seed)**. It is read for citations under S1 and is not rated.

### S1. Locators (read for citations only, never as sources)

Locators: arXiv 2508.14318 (Choukse et al.), arXiv 2605.24461, the EPRI DCFlex publications, the NERC and ISO
presentations found while resolving seeds, and the S0 locators.

**What the screener reads in a locator.** A script extracts:
- every sentence that cites a document;
- the reference list.

Before printing, it replaces every digit, every `%`, and every time-unit token (`s`, `ms`, `sec`, `second(s)`, `min`,
`minute(s)`, `h`, `hour(s)`, `cycle(s)`, `Hz`) with `#`. **The screener reads no limit value, window or allowance, even
masked in a locator.**

**Candidates.** A document a locator cites as the source of a ramp, step, swing, oscillation, flicker or rapid
voltage change limit is a candidate addition. It is judged under S3.

### S2. Landing page, title and scope (each instrument)

For each instrument, the screener records:
- its landing page on the body's own site (§3 S4 below);
- its exact title;
- its scope, quoted in no more than three sentences;
- access status, `full` / `partial` / `none`, as L1 L-3 reads for a text rather than a history:

| State | Meaning |
|---|---|
| `full` | the requirement text is readable from the body's own site |
| `partial` | only an abstract, preview, table of contents or catalogue page is readable |
| `none` | nothing beyond the title is reachable by an allowed route |

**What the screener prints.** A script prints only the title, the scope or applicability clause, and, for large
documents, the section headings. If a scope sentence states a limit value, window or allowance, the script replaces
it with `[…]`. Applicability thresholds (for example, "loads of 75 MW or more") are not limits on power variation and
may stay.

### S3. Additions, one level

A document is added once, and logged with the citing document and clause, when it passes three tests:
1. it is an instrument under §2, judged from its own title and scope;
2. it is cited by a listed instrument, or by an S1 locator, **as the normative basis of** a limit on load real-power
   variation, flicker or rapid voltage change ("shall comply with", "as defined in", "the limits of …"), judged from
   the citing sentence with numbers masked as in S1;
3. it is public: it has a landing page on its body's site.

**Where citations are taken from in listed instruments.**
- With a normative-references clause: that clause, plus the masked citing sentences found by script.
- Without one (codes, protocols, tariffs, rules): the masked sentences of clauses whose heading names ramp, step,
  fluctuation, oscillation, flicker, rapid voltage change, power quality, disturbance or large load.
- Text not readable as text: from a free preview that shows the references when there is one. Otherwise the
  instrument is logged `references not accessible` and adds nothing.

**Bounds.**
- **One level only.** The references of an added instrument are not screened.
- A citation of an instrument already listed adds nothing; it is counted.

**Hit counts, per instrument and per locator:** citations read; passing tests 1, 2 and 3; added; already listed.

**Not a reason to add.** An instrument is never added because it is known to contain a fast limit (brief §7).

### S4. Allowed routes (screener and raters)

Each instrument is read on its body's own site:
- the grid bodies: ercot.com, nerc.com, pjm.com, puc.texas.gov (and its docket interchange), ferc.gov (and eLibrary);
- the EU and European bodies: eur-lex.europa.eu, entsoe.eu, acer.europa.eu, neso.energy (the GB Grid Code),
  ena-eng.org (ENA engineering recommendations);
- the standards bodies: vde.com (VDE FNN) and vde-verlag.de (its publisher), iec.ch / webstore.iec.ch, ieee.org /
  standards.ieee.org, cencenelec.eu;
- the operators and vendors: opencompute.org, docs.nvidia.com, developer.nvidia.com, nvidia.com;
- the utility's own tariff pages and the state commission's docket;
- the publishing association's own site for the D-A-CH-CZ rules.

Resellers and secondary summaries are not sources. No bot check, paywall, login or verification step is circumvented
(L1 §3b rule 1). `none` is a recorded result.

## 4. Extraction (stage 2; one row per requirement)

### `requirements_<A|B>.csv`

| Column | Content |
|---|---|
| `req_id` | `A001` … / `B001` … |
| `instrument_id` | as in `DC2_instruments.md` |
| `clause` | section / table / paragraph identifier as printed |
| `category` | the table row or category label as printed; blank if none (added to the brief's list; it disambiguates rows of one table, §5) |
| `measurement_point` | `POI` / `facility` / `rack or row` / `shelf or PSU` / `device` / `not stated` |
| `quantity` | `ramp rate`, `step change`, `swing amplitude`, `smoothing or capping response`, `load change per interval`, `flicker`, `rapid voltage change`, `harmonics`, `power factor`, `ride-through`, `hold-up`, `other` |
| `limit` | value and unit as printed |
| `basis` | what a percentage refers to (rated power, contracted capacity, P_max, …), if any |
| `window_class`, `window_as_printed` | §2 |
| `allowance_class`, `allowance_as_printed` | §2 |
| `binding_class` | §2 |
| `deciding` | `yes` if `quantity` is in the deciding set, else `no` |
| `shape` | `history` / `reactive` / `electronics` / `cannot judge`, by the §2 table |
| `source_url`, `quote` | the page read; at most 25 words of the clause, verbatim |
| `confidence` | `low` / `medium` / `high` |
| `note` | free text |

### `instruments_<A|B>.csv`

One row per listed instrument, with these columns:
- `instrument_id`;
- `access`: `full` / `partial` / `none`, per §3 S2, as the rater found it;
- `edition_read`: the identifier and date of the edition read;
- `status`: `in force` / `pending` / `no requirement`;
- `sources_tried`;
- `note`.

### Partial access

The L1 L-3 rule, adapted:
- A requirement read from an abstract, preview or the body's own summary is a row, with `confidence = low` and its
  page named in `source_url`. It is classified from what the page prints.
- A window or allowance the page does not print is `not stated`, and the shape is then `cannot judge`.
- A row is never inferred from a title alone.

## 5. Readouts

### Matching the two files

Within each `instrument_id`, in two passes, one-to-one:
1. **Pass 1.** Identical normalised `clause` and identical normalised `category`.
   - Normalisation: lower case; remove whitespace, punctuation and the words `section`, `clause`, `paragraph`,
     `table`, `annex`, `article`, `art`, `§`.
   - Several candidates: rows are taken in each rater's file order.
2. **Pass 2.** For rows still unmatched: the same `quantity` and the same `window_class`, in file order (the brief's
   rule).

Counts:
- **M**, the matched pairs, split M₁ (pass 1) and M₂ (pass 2);
- **n_A** and **n_B**, the file sizes.

### Gates (both must pass)

| Gate | Definition | Pass |
|---|---|---|
| **Identification** | M / (n_A + n_B − M) | **≥ 0.80** |
| **Window class** | unweighted Cohen's κ on the six window classes, over the **M₁ pass-1 pairs** | **≥ 0.60** |

- **Why pass 1 only (CHOSEN).** Pass-2 pairs agree on window class by construction, so including them would inflate
  κ. κ over all M pairs is reported beside the gate.
- If M₁ < 10, κ(window) cannot be estimated and the study reads **UNGATED**.
- **Also reported:** κ on `allowance_class` (over M₁), κ on computed shape (over M₁), and agreement on
  `binding_class` and `deciding`.
- Identification is computed over instruments that at least one rater could read (`access` ≠ `none` for A or B). An
  instrument with `none` from both raters contributes nothing (L1 L-2).

### Conservative reading of a matched pair

| Field | Conservative reading |
|---|---|
| binding | the pair is binding only if **both** raters wrote `mandatory` or `planning level` |
| deciding | the pair is deciding only if **both** wrote `deciding = yes` |
| shape | `history` only if both computed shapes are `history`; `cannot judge` if either is `cannot judge`; otherwise `reactive` if either is `reactive`, else `electronics` |

### Primary readouts (binding, deciding, matched pairs)

- the number of requirements per window class and per allowance class;
- the number whose conservative shape is `history`, with their instrument, clause, window, allowance and measurement
  point;
- **the fastest binding window per body:** the smallest window class among the body's binding deciding pairs;
- the table of every requirement, deciding or not, with both raters' classes.

### Also reported (none deciding)

- **Each rater's own counts**, including its unmatched rows.
- **Vendor-capability rows:** what ramp settings the GPU and rack smoothing features expose.
- **Non-deciding power-quality rows,** with their window and allowance, so the reader sees the shapes the converter
  must meet.
- **Sensitivities:**
  - STATED (§2 rate-unit rule off);
  - **ANY:** binding or deciding by either rater instead of both;
  - **SEED:** S3 additions excluded.
- **Access table:** `access` per instrument and rater; counts by group.
- **Records:**
  - every unmatched row;
  - every class disagreement;
  - every rater-written shape that differs from the computed one.

  They are listed and never reconciled.

## 6. Decision (binding deciding requirements, conservative shape; checked in this order)

| Verdict | Condition |
|---|---|
| **UNGATED** | identification < 0.80, **or** κ(window, M₁) < 0.60, **or** M₁ < 10 |
| **HISTORY-SHAPED SPEC EXISTS** | ≥ 1 binding deciding matched pair with conservative shape `history` |
| **NO HISTORY-SHAPED SPEC** | ≥ **8** binding deciding matched pairs from ≥ **4** distinct instruments, **and** no binding deciding row with computed shape `history` in **either** rater's file, matched or unmatched |
| **UNCLEAR** | anything else, including fewer than 8 binding deciding pairs found |

**Access qualifier (L1 L-2).** The study is **access-limited** when both raters record `access = none` for at least
**one third of the seed instruments**. The number *k* is fixed in §3b below, after the screen and before reading.

| Verdict | When access-limited |
|---|---|
| HISTORY-SHAPED SPEC EXISTS | can be established, as `HISTORY-SHAPED SPEC EXISTS (ACCESS-LIMITED: x of n seeds unread)` |
| NO HISTORY-SHAPED SPEC | cannot be established, because an unread spec could carry one. Reads `UNCLEAR (ACCESS-LIMITED: …)` |

The verdict line names the unread instruments.

**Consequence for ANGLES §B.2, stated beside the verdict.**

| Verdict | Consequence |
|---|---|
| **NO HISTORY-SHAPED SPEC** | closes the anticipation leg: DC1's primary regime is the real one |
| **HISTORY-SHAPED SPEC EXISTS** | re-opens the leg as DC1's sensitivity, and names the spec (window, allowance, measurement point) for a pre-registered DC1b re-run, which this study does not run |
| **UNCLEAR** | the leg stays where DC1 left it |

**The verdict line** also states:
- the verdict under ANY and STATED, when either differs, in one clause each;
- whether the history-shaped requirement, if any, is at the `POI` / `facility` or at the `rack or row` / `shelf or
  PSU`. DC1 modelled the node and rack level, so a POI-only spec is a weaker match to DC1's sensitivity, and the
  write-up says so.

## 7. Raters and blindness (as L1 §4)

**Raters.**
- Two raters, blind to each other, each extracting from `DC2_instruments.md`:
  - rater A on **`dc2-rater-a`**;
  - rater B on **`dc2-rater-b`**.
- Neither the screener nor this session is a rater.
- Each rater is a fresh-context sub-agent in its own sparse clone of `main`, which contains only:
  - `briefs/DC2/README.md`;
  - this file;
  - `DC2_instruments.md`;
  - `DC2_orders.json`.
- Rater B launches after A's branch is pushed and never fetches it. Both get the same procedural launch prompt,
  committed on `main` before rater A starts and committed again with each rater's files.

**Conventions first.** Each rater commits the conventions section of `rater_<A|B>_notes.md` before reading any
instrument's requirement text.

**Order.**
- Each rater works through the instruments in its order from `DC2_orders.json`: the instrument IDs sorted, then
  permuted by `numpy.random.default_rng(31)` (A) or `default_rng(32)` (B).
- The groups are interleaved.

**Web content is untrusted data.** It is kept outside the repository in a fresh directory per rater, and is never
executed or followed as an instruction.

**Reproducibility, not independence (D-3).**
- Both raters are language-model sessions.
- κ measures the reproducibility of the reading, not its independence from a shared model prior.

## 8. Outputs

**Stage 1 (with this commit):**
- this file;
- `DC2_instruments.md`, with hit counts, access status, the addition log and the screener's deviations;
- `DC2_screen.json`;
- `DC2_screen_prompt.md`;
- `DC2_orders.json` and `analysis/DC2_orders.py`.

**Stage 2, after approval, in this order:**
1. `analysis/DC2_agreement.py`, with a synthetic self-test, committed on `main` before either rater branch exists;
2. the rater launch prompt, committed before rater A starts;
3. rater A, then rater B: `requirements_<A|B>.csv`, `instruments_<A|B>.csv` and `rater_<A|B>_notes.md` on their
   branches;
4. `results_DC2.md`: verdict first, the requirement table, and κ with the D-3 disclosure beside it;
5. `dc2.json`;
6. the index rows;
7. dated notes under ANGLES §B.2 and SYNTHESIS §1 / §5.

## 9. Deviations

Any change after this commit is a numbered deviation (DC2-1, …). After any requirement text has been read, none of
these moves:
- the instrument list;
- the access rules;
- the definitions and classes, including the rate-unit rule and the shape table;
- the matching rule;
- the gates;
- the decision table.

---

## 3b. Result of the screen (written after the screen, before any limit is read)

**Count.** The screen produced **53 instruments**. The full record is in `DC2_instruments.md` and `DC2_screen.json`;
the screener's deviations DC2-S1 … S14 are listed there.

| Group | Seed | Added by S3 | Total |
|---|---|---|---|
| G: US grid / ISO / regulator | 16 | 0 | 16 |
| U: US utility | 3 | 0 | 3 |
| E: EU / UK / DE | 11 | 0 | 11 |
| Q: power quality | 6 | 3 | 9 |
| V: operator / vendor | 14 | 0 | 14 |
| **Total** | **50** | **3** | **53** |

- **Additions:** IEC 61000-3-3 and IEC 61000-3-11 (cited as their EN versions by D-A-CH-CZ Part A clause 2.11), and
  ENA EREC P28 (cited by GB Grid Code CC.6.1.7 / ECC.6.1.7).
- **Access as the screener found it:** full 40, partial 13, none 0. Of the 50 seeds, 10 are partial (U02, E05, E06,
  E07, Q01–Q06) and none is `none`.
- **Pending as printed** (§1: rows only if adopted by the reading date): G07, G08, G09 (NERC Project 2026-02 drafts),
  G11 (PJM draft), G15 (PUCT proposed rule), E03 (ACER amended-DCC draft), E06 (VDE-AR-N E 4120/A1 draft).

**Access threshold, fixed now (§6).** The study is access-limited when both raters record `access = none` for
**≥ 17 of the 50 seed instruments**. A pending instrument counts by its access, not its status.

**Disclosed for the reviewer, before any reading.**
1. **The screener saw limit-type content by accident** (DC2-S2): the web-search tool attaches a model-written summary
   to results, and on seven queries it carried limit-type content, touching G11, Q04, V10 and V11–V13 among listed
   instruments. The screener reports that none drove an inclusion or exclusion, and the output files carry no limit,
   window or allowance (checked by regex scan by the screener and again by this session). The screener is not a rater;
   the raters' clones contain only the files named in §7.
2. **DC2-S14, a test-2 judgement that excluded eight documents.** The OCP LVDC white paper (a locator) cites grid
   documents of AESO, EirGrid / SONI, Energinet, RTE, Fingrid, SPP, IESO and ATC for ride-through, post-fault active
   power recovery and RoCoF rows. The screener read these as `ride-through`, not real-power variation, so S3 test 2
   failed and none was added. One search summary (item 1) paraphrased an AESO data-centre ramp limit; under brief §7
   ("do not add an instrument because it is known to contain a fast limit") this session does not add it. **For the
   reviewer to confirm or overturn before rating.** Post-fault active-power recovery is a rate of change of real
   power, so a reading under which test 2 passes is arguable.
3. **Grouping choices:** approved ERCOT revision requests already incorporated are read inside G01–G03 (DC2-S8;
   PGRR144, approved but not yet effective, is G04); the 14 DCC-relevant ENTSO-E implementation guidance documents are
   one instrument (E02, DC2-S9); the EN and IEC texts of Q07 / Q08 are one instrument (DC2-S7).
4. **Off-list hosts** (DC2-S6) were used for locators, landing pages and pending items: nysrc.org (a copy of the NERC
   gap white paper), acer.europa.eu, ena-eng.org, vde-verlag.de, NVIDIA's asset CDN, and the utilities' and
   commissions' own sites. Raters source requirements only from the body's own site (§3 S4); ENA, ACER, VDE Verlag and
   the commission dockets are the publishing bodies of the documents concerned.

---

## 10. Reviewer approval and deviations DC2-1, DC2-2 (2026-11-10, stage 1 → stage 2; before any limit is read)

Stage 1 (`60f7595`) is **approved**. The reviewer checked: the 53 instruments carry no limit value, window or allowance
(regex scan of `DC2_instruments.md` and `DC2_screen.json` for rate units, percentiles, Pst / Plt values and
percent-of-rating phrases: none); the only figures in the table are applicability thresholds, titles and scope
descriptions, which §3 S2 allows; the two rating orders reproduce from `default_rng(31)` / `default_rng(32)` over the
53 sorted IDs; the screener's accidental exposures DC2-S2 (a)–(g) are disclosed, drove no inclusion, and the screener
is not a rater; the three S3 additions each carry the citing clause and the three tests. The pending rule (§1), the
rate-unit rule, the `hard` default and the shape table are accepted as written. **DC2-S14 is upheld as a citation
judgement and corrected as a listing omission (DC2-1).** These deviations bind the screener's stage 1b and both raters.

### DC2-1. Cited grid-operator documents are listed by title (stage 1b, before any limit is read)

The brief's seed table is US- and EU-centric; that was the reviewer's omission, not a design choice. The S1 locators
cite connection requirements of other grid operators for data-centre and large-load sites, and the screener excluded
them because the *citing sentences* concerned ride-through, post-fault active-power recovery and RoCoF — a correct
reading of §2 (`ride-through` is a non-deciding quantity) but the wrong test for whether the *document* is an
instrument this audit should read. A document's title is content-independent, so:

- **Rule.** A document of a grid operator, TSO, ISO / RTO or energy regulator that is cited by a listed instrument or
  by an S1 locator — whatever it was cited for — is listed when its **title** names data centres, large loads, large
  demand facilities, (large) computational loads or high-impact loads **together with** connection, interconnection,
  technical or performance requirements. The test is on the title alone; a document that fails it is not listed
  however relevant its content is said to be (brief §7 stands).
- **Who and how.** A fresh-context screener (the stage-1 prompt plus this section) applies the rule to every citation
  already recorded in `DC2_screen.json` — at least the OCP DCF LVDC white paper's AESO, EirGrid / SONI, Energinet, RTE,
  Fingrid, SPP, IESO and ATC entries — and runs §3 S2 on each candidate (landing page on the body's own site, exact
  title, scope ≤ 3 sentences, access, status). It reads no limit, window or allowance. Each candidate's pass / fail on
  the title test is logged in `DC2_instruments.md` §5.
- **Listing.** Added instruments form group **X: other grid operators** (`X01` …), `origin = DC2-1`. They are
  additions, not seeds: the **SEED** sensitivity excludes them with the S3 additions, and the access threshold stays
  **≥ 17 of the 50 seed instruments**. `DC2_orders.json` is regenerated with the same seeds over the extended sorted
  ID list. The stage-1b commit carries "before reading" in its message.
- **Disclosure.** The screener saw, in one web-search summary, a third-party paraphrase of one AESO limit (DC2-S2 (f)).
  This rule is written so that the AESO guide is listed on its title alone; it would be listed had nothing been seen.
  The stage-1b screener is a fresh context.

### DC2-2. Event-count allowances with a stated duration are converted to a share

The shape table reads `1 – 60 s` with an `event count` allowance as `cannot judge`, because DC1's budget is a share of
samples. When a clause prints **both** a permitted recurrence (a frequency, or a minimum interval between exceedances)
**and** a maximum duration of each exceedance, the share is defined: *a* = duration / recurrence interval. Then:

- `allowance_class` is set from *a* by the §2 bands (`tight` / `loose` / `very loose`); `allowance_as_printed` keeps
  the printed form; `note` records the arithmetic;
- the window is the printed duration unless the clause states an assessment interval;
- when only one of the two is printed, `event count` stays and the shape is `cannot judge`.

Both raters apply this rule; a disagreement on the conversion is a disagreement on allowance class and is listed.

### Stage 1b and stage 2 order (binding)

1. **Stage 1b (screener, fresh context):** DC2-1; commit `DC2_instruments.md`, `DC2_screen.json`, `DC2_orders.json`
   with "before reading"; no approval round-trip is needed — the reviewer checks the additions with the results.
2. `analysis/DC2_agreement.py` with a synthetic self-test, committed on `main` before either rater branch exists
   (§8); it implements §5–§6 with DC2-2 and the group-X additions in FULL / SEED.
3. The rater launch prompt, committed before rater A starts.
4. Rater A (`dc2-rater-a`), then rater B (`dc2-rater-b`), as §7; conventions committed before reading.
5. The rest as §8.
