# L1b pre-registration: a second comparison domain (exterior lighting), and the stack class

**Question (brief §0).** Against exterior lighting, counted the same way, is the battery / charging domain's
requirement arrival specific in **count**, and specific in **kind**? Kind means the share of events that force a
cryptographic, update, data-access, retention or external-communication stack onto the ECU.

**Status of this file.**
- Brief: [`briefs/L1B/README.md`](../../briefs/L1B/README.md). Requested by NEXT_TASK (reviewer, 2026-11-11), stage 1.
- Committed together with [`L1B_instruments.md`](L1B_instruments.md) and [`B_events.csv`](B_events.csv), **before
  any lighting or seat instrument's change history has been read** by this session, by the screener or by a rater,
  and before either rater branch exists.
- L1's procedure ([`../L1/L1_preregistration.md`](../L1/L1_preregistration.md) §1–§9, with deviations L-1 … L-5) is
  reused by reference, except where this file names a change.

**Tags.**
- Every event is **SOURCED**.
- Every classification and every `stack` value is **DERIVED-judgemental**.
- Both raters are language-model sessions, and the write-up says so beside κ (D-3).
- No dollar figures.

---

## 1. Carried over from L1 by reference (unchanged)

| L1 section | Content |
|---|---|
| §2 | instrument; event (a) data, (b) functions, (c) process; what is not an event; counting rules; window 2016-01-01 – 2026-12-31; the four classes and their order; the ledger columns |
| §3 S0–S3 | the search protocol (titles, scope and normative references only; one level of additions by the three tests) |
| §3b rules 1–3 | no bypassing; allowed routes (the body's own pages); access recorded per instrument |
| §4 | raters and blindness: fresh-context sub-agents in sparse clones; conventions committed first; rater B after A's branch is pushed, never fetching it; sources; web content untrusted; D-3 |
| §5 | matching (L-4: pass 1 normalised `act_id`, pass 2 ± 90 days on `adoption_date`, within `instrument_id`); Wilson intervals; per-year tables |
| L-1 | vehicle-level instruments (UN R155, UN R156, GB 44495, GB 44496) count in every domain for N (V2 primary) |
| L-2 | access-limited as a qualifier with bound logic |
| L-3 | access states `full` / `partial` / `none`; events under partial access; unreadable editions |
| L-4 | canonical `act_id` forms |
| L-5 | seed instruments primary; additions in FULL |

**Changes:**
- **Counting rule "never twice" applies within a domain.** An act that reaches the lighting ECU and the seat ECU (for
  example one delegated act under Regulation (EU) 2019/2144) is one event of **each** domain it reaches, recorded once
  under each domain's instrument. Domains are counted separately, as L-1 already does for vehicle-level acts.
- **L1's decision table (§6) is replaced** by §5 below.

## 2. Domains

| Domain | Status in L1b | Instruments | ECUs |
|---|---|---|---|
| **B** battery / charging / power conversion | **Carried over.** L1's matched domain-B events, primary V2, are the B ledger: **35 events**, in [`B_events.csv`](B_events.csv). They are not re-identified. The raters rate only `stack` on them (§3). | L1's B01–B37 | as L1 §1 |
| **S** seat / interior | **Re-rated as calibration.** Both raters identify events again from L1's seat list. | S01–S26, carried over verbatim into `L1B_instruments.md`; S01–S16 are the seeds (primary) | as L1 §1 |
| **L** exterior lighting and light-signalling | **New.** | L01…, built by the screen of §6 | lamp control units; adaptive-driving-beam (ADB), adaptive front-lighting (AFS) and headlamp-levelling controllers; light-signalling functions (stop lamps, emergency stop signal, daytime running lamps, direction indicators, cornering lamps) and the body-controller functions that drive them |

**Vehicle-level instruments.** UN R155, UN R156, GB 44495 and GB 44496 are not re-identified. Their **8 matched
events** in `B_events.csv` (instruments B05, B06, B14, B15) count in N_B, N_S and N_L (L-1, V2 primary). V1 counts
them in B only; V0 counts them in no domain.

## 3. The stack class (new; brief §3)

Each event carries one more closed field, `stack`:

| Value | Meaning |
|---|---|
| `yes` | the act names, for the domain's ECU, any of: a **cryptographic** obligation (keys, certificates, signatures, secure boot, secure communication); an **authenticated software-update** obligation; a **data-access or data-retention** obligation (data the ECU must store, keep for a period, or expose through an interface); a **telemetry or transmission** obligation (data the ECU must send off-vehicle or to a server); an **external communication protocol** the ECU must implement (charging communication, vehicle-to-grid, diagnostic access from outside the vehicle) |
| `no` | none of the above: a new or changed monitoring or warning function, a limit, a test, a scope extension, a re-approval date, a hardware requirement |
| `cannot judge` | the text or summary read does not allow the call |

**Who rates what:**
- every event a rater records in domains S and L: in `ledger_<A|B>.csv`;
- each of the 35 B events, rated for the battery / charging ECU: in `stack_B_<A|B>.csv`. The raters are given each
  event's identity and `what_changed` text, and may read its source.
- **A vehicle-level act is rated for the domain it is counted in (CHOSEN).** Each of the 8 vehicle-level events in
  `B_events.csv` gets **three** rows in `stack_B_<A|B>.csv`: one each with `domain` = `B`, `S` and `L`, rated for that
  domain's ECU.

`stack` is independent of `class`. The four-class classification of L1 §2 is kept unchanged for S and L events.

## 4. Files and clone contents (brief §4)

**This commit:**
- `B_events.csv`: one row per carried-over B event, with columns `instrument_id`, `act_id`, `adoption_date`,
  `jurisdiction`, `what_changed` (rater A's line in L1) and `source_url`. It has no class, confidence or note column.
  It is written by [`analysis/L1B_b_events.py`](../../analysis/L1B_b_events.py), which recomputes L1's primary
  matched pairs with L1's own analysis functions, checks the count against `l1.json` (N_B = 35), and writes rater A's
  identity fields only. `l1.json` does not store the pairs, so it is used only for the check. The session did not read
  a ledger by eye.
- `L1B_instruments.md`, `L1B_screen.json` and `L1B_screen_prompt.md`;
- `L1B_orders.json` and `analysis/L1B_orders.py`.

**Each rater writes, on `l1b-rater-a` / `l1b-rater-b`:**

| File | Contents |
|---|---|
| `ledger_<A\|B>.csv` | L1 §2 columns plus `stack`; domains S and L only |
| `stack_B_<A\|B>.csv` | `act_id`, `domain` (`B`; `S` / `L` also for vehicle-level events), `stack`, `confidence`, `note`. One row per B event, three per vehicle-level event (8 × 3 + 27 = 51 rows) |
| `instruments_<A\|B>.csv` | one row per S and L instrument, with `history_access` (L-3) |
| `rater_<A\|B>_notes.md` | conventions (committed first) and remarks |

**Rater clone contents, exactly these five files:**
- `results/L1/L1_preregistration.md`;
- this file;
- `L1B_instruments.md`;
- `L1B_orders.json`;
- `B_events.csv`.

The clone has no L1 ledger, notes, results, review or `l1.json`, and not the brief.

## 5. Readouts and decision

**Instruments in the deciding readouts:** the seed instruments of S (S01–S16) and of L (§3b), as L-5. The additions
enter FULL.

### Gates (all must pass, else UNGATED)

| Gate | Over | Pass |
|---|---|---|
| Identification M / (n_A + n_B − M) | events in domains S and L together (seed instruments, window, L-2: instruments `none` for both raters excluded) | **≥ 0.80** |
| κ on the four classes | matched S and L pairs | **≥ 0.60** |
| κ on `stack` (three values, unweighted) | every event both raters rated: matched S and L pairs, plus the 51 rows of `stack_B` (joined on `act_id` + `domain`) | **≥ 0.60** |

### Calibration (domain S re-rated)

- **Reference.** L1's specific seat count, **N_S1**, is the number of L1 primary matched domain-S events from
  non-vehicle-level instruments. Its act set **E_S1** is the normalised `act_id`s of those pairs. Both are fixed by
  L1's committed files (`results/L1/ledger_*.csv`, `instruments_*.csv`, `L1_instruments.md`) and are computed by
  `analysis/L1B_agreement.py` with L1's own functions.
- **Masking (CHOSEN).** The numbers are not written in this file, because this file is in the raters' clones and a
  rater told the expected seat count is primed. They are public in `results/L1/results_L1.md`, which the raters do
  not have.
- **Calibrated** when both hold:
  - |N_S,specific − N_S1| ≤ **3**;
  - the new matched S pairs include **at least 5** of E_S1 by normalised `act_id` (either rater's `act_id` of the
    pair).
- Otherwise **MISCALIBRATED**, and every ratio is reported with that qualifier.

### Count readouts (V2 primary)

| Readout | Definition |
|---|---|
| N_L | matched L events from seed instruments, plus the 8 vehicle-level events |
| N_S | matched S events from seed instruments, plus the 8 vehicle-level events |
| N_B | 35 |
| R_BL | 35 / N_L, with a 95 % interval: Wilson interval [lo, hi] on the proportion N_B / (N_B + N_L), mapped to lo / (1 − lo) and hi / (1 − hi) (the L1 review's method). R = ∞ if N_L = 0 |
| R_BS | 35 / N_S, the same way |

**Also reported:**
- per-year tables (adoption and application year);
- classes, with MC and H for L (Wilson CIs);
- V1 and V0;
- FULL;
- CN0 (China-only instruments excluded);
- ACC (instruments both raters read `full` or `partial`);
- each rater's own counts;
- unions;
- every unmatched event, class disagreement and stack disagreement, listed and never reconciled.

### Stack readouts

- **Specific events** exclude vehicle-level instruments: the 27 non-vehicle-level B events, and the matched seed S and
  L pairs.
- **Conservative `stack = yes`:** both raters `yes`. A pair with `cannot judge` from either rater is not counted and
  is listed.
- **Per domain:** k_d stack events among n_d judged specific events (judged = neither rater `cannot judge`), and the
  share k_d / n_d with a Wilson CI.
- **Vehicle-level stack counts:** per domain from the `stack_B` rows with `domain` S and L, reported separately.
- **Fisher's exact test:** one-sided, B vs L, `yes` vs `no` among judged specific events; alternative "B's share >
  L's". Reported, not deciding.

### Decision — count (V2; checked in this order)

| Verdict | Condition |
|---|---|
| **UNGATED** | any gate fails |
| **SPECIFIC BY COUNT** | R_BL ≥ **3** and the interval's lower bound > **1.5** |
| **NOT SPECIFIC BY COUNT** | R_BL < **1.5** |
| **UNCLEAR BY COUNT** | otherwise |

**Access qualifier (L-2 for domain L).**
- Domain L is **access-limited** when both raters record `history_access = none` for at least one third of L's seed
  instruments. The number is fixed in §3b after the screen.
- When limited, N_L is a lower bound and R_BL an upper bound. NOT SPECIFIC BY COUNT can then be established;
  SPECIFIC BY COUNT cannot and reads `UNCLEAR BY COUNT (ACCESS-LIMITED: …)`.
- The S access rule is L1's (≥ 6 of 16), and it bears on R_BS only.

### Decision — kind (specific events, conservative `stack`; checked in this order)

| Verdict | Condition |
|---|---|
| **UNGATED** | any gate fails |
| **STACK-SPECIFIC** | k_B ≥ **3**, and k_L ≤ **1**, and k_S ≤ **1** |
| **NOT STACK-SPECIFIC** | k_L ≥ **2**, or (n_L > 0 and k_L / n_L ≥ k_B / n_B) |
| **UNCLEAR IN KIND** | otherwise |

**Order (CHOSEN; flagged in §8).** The brief's two conditions can both hold, for example with k_L = 1 of n_L = 2 and
k_B = 3 of 27. This file checks the rows in the brief's order, so STACK-SPECIFIC wins such a case, and the overlap is
stated beside the verdict when it occurs.

**Consequences, stated beside the verdicts (brief §5):**
- **NOT SPECIFIC BY COUNT** withdraws the count form of ANGLES §B.1: the battery box is one of the volatile ECU
  domains, with lighting.
- **NOT STACK-SPECIFIC:** the stack is not what distinguishes the battery box. POSITION §1 sentence 1 falls as
  written, and the C5 argument is made on cost alone.
- **STACK-SPECIFIC,** with any count verdict: the position as written, now gated.
- **UNCLEAR in either:** that verdict gives no reading.

## 6. Search protocol for domain L (L1 §3, applied to the brief §6 seeds)

- **Screener.** The screen is run by a fresh-context sub-agent of this session, which is not a rater. Its prompt is
  `L1B_screen_prompt.md` and its raw record `L1B_screen.json`. It reads titles, scope statements and
  normative-reference clauses only, and never a change history.
- **S0 seeds:**

  | Source | Seeds |
  |---|---|
  | UN | R48, R148, R149, R150, R123, R45, R37, R99, R128 |
  | EU | Regulation (EU) 2019/2144 (provisions naming lighting, lamps, headlamps, adaptive driving beam or light-signalling); Regulation (EC) No 661/2009 (the same provisions, for the 2016–2022 part of the window) |
  | US | FMVSS 108. NHTSA's ADB rulemaking is part of 108's history, not a separate instrument |
  | China | GB 4785, GB 4599, GB 25991, GB 23255, GB 17509, GB 5920; any GB standard whose **title** names adaptive front lighting or adaptive driving beam, found by a title search on openstd.samr.gov.cn / std.samr.gov.cn |
  | SAE | J3069, J578, J1383 |
  | ISO | none |

  Seeds are listed as L01… in this order.
- **S1 (EU acts under the two EU base acts).** Kept by **title only** if the title names lighting, lamps, headlamps,
  adaptive driving beam, light-signalling, or a UN Regulation among R48, R148, R149, R150, R123, R45, R37, R99, R128.
  Kept acts are candidate events under their base act, not instruments. The query, hit count, and kept and dropped
  titles are recorded.
- **S2.** Landing page, exact title, and scope in ≤ 3 sentences, printed by script. No history, edition list or
  transitional provisions.
- **S3.** One level of normative-reference additions by L1's three tests. Test 3 reads "concerns the citing
  instrument's domain (§2: domain L)". Additions take the next L IDs after the seeds.
- **The S list is not re-screened.** S01–S26, and the S1 acts L1 listed under S13, are carried over verbatim.

## 7. Raters, orders, branches

- **Branches:** rater A `l1b-rater-a`; rater B `l1b-rater-b`.
- **Orders:** `L1B_orders.json`. The S and L instrument IDs are sorted, then permuted by
  `numpy.random.default_rng(51)` (A) and `default_rng(52)` (B). The `stack_B` rows are rated after the S and L
  instruments, in `B_events.csv` order.
- **Fresh raters:** no L1 rater, L1 screener or L1b screener, and no session that has read an L1 ledger or notes.
- **Stage 2 order (binding):**
  1. `analysis/L1B_agreement.py` (L1's script extended: calibration, stack readouts, Fisher; synthetic self-test),
     committed on `main` before either branch exists;
  2. the launch prompt, committed before rater A;
  3. rater A, then rater B;
  4. merge, run and write the results.

## 8. Disclosure, and points for the reviewer

**What the launching session has read.** This session ran L1 stage 2:
- it wrote `analysis/L1_agreement.py`;
- it merged and read both L1 ledgers and both sets of rater notes;
- it wrote `results_L1.md` and `l1.json`;
- it has read the L1 review, including the reviewer's exploratory stack split.

It cannot un-read them, so the brief's "do not open" cannot be met by this session, and is disclosed instead. It
reaches the raters only through the launch prompt and the five-file clone. Proposed:
- the launch prompt is L1's committed prompt (`results/L1/L1_rater_prompt.md`) with mechanical substitutions only, plus
  the `stack` and `stack_B` instructions copied from §3–§4 here;
- its diff against L1's prompt is committed with it;
- it names no instrument's content, no event, no count and no expected direction.

**Points for the reviewer (CHOSEN here; the reviewer may change them before rating):**
1. **B_events from the ledgers by script.** `l1.json` does not store the matched pairs, so `L1B_b_events.py`
   recomputes them from the L1 ledgers with L1's own functions and checks N_B = 35 against `l1.json` (§4).
2. **Vehicle-level `stack` rows** for S and L (§3): three rows per vehicle-level event.
3. **"Never twice" within a domain only** (§1).
4. **Calibration numbers masked** in this rater-visible file (§5); they are fixed by L1's committed files.
5. **Overlap of the kind conditions** resolved by table order (§5).

## 9. Deviations

Any change after this commit is a numbered deviation L1B-D1, …. After any change history has been read, none of these
moves:
- the instrument lists;
- the domains;
- the event definition and the classes;
- the `stack` definition;
- the matching rule;
- the gates;
- the calibration rule;
- the decision tables.

---

## 3b. Result of the screen (written after the screen, before any change history is read)

**Count.**

| Domain | Seeds | Additions (S3) | Total |
|---|---|---|---|
| L | 22 (L01–L22) | 25 (L23–L47) | 47 |
| S (carried over from L1) | 16 (S01–S16) | 10 (S17–S26) | 26 |

- **Additions:**
  - 14 UN lamp and device regulations cited by R48;
  - IEC 60809, R53, R74 and R86 cited by R148;
  - R50 cited by R149;
  - R113 cited by R37;
  - R1, R8, R20 and R31 cited by the 2019/2144 Annex I;
  - 49 CFR Part 564 cited by FMVSS 108.
- **S1:** 19 acts under 2019/2144 and 25 under 661/2009 were found by legal basis, and none passed the title test.
- **References not accessible:** all 7 GB seeds (full text behind an interactive verification step) and all 3 SAE seeds
  (sae.org loads a captcha).

**Access threshold (fixed now).** Domain L is access-limited when both raters record `history_access = none` for
**≥ 8 of its 22 seeds** (22 / 3 = 7.3). S: ≥ 6 of 16, as L1.

**Disclosed before reading.**
1. **The screener's exposures (L1B-S7, L1B-S8):**
   - two web searches used to find landing URLs returned unrequested summaries that mentioned edition or amendment
     information for IEC 60809, IEC 60061, SAE J1383 and SAE J3069;
   - the GB catalogue search responses kept in `L1B_screen.json` list GB editions with a current or withdrawn state.

   Nothing from either reached an addition decision. `L1B_screen.json` is not in the raters' clones.
2. **Edition years removed (session).** The screener wrote the GB seeds with their latest edition year (for example
   `GB 4599-…`). Under L1's convention ("identifiers carry no edition year"), the launching session removed the years
   from the 14 GB identifiers in `L1B_instruments.md`; the session has therefore seen them. L1B-S8 in the instruments
   file says that three GB seeds have no edition marked current. That is a catalogue state, not a description of change,
   and it is left as written.
3. **Sensitivity set not on the list (L1B-S5):** SAE J602 and J2009, cited by FMVSS 108, would pass the three tests
   on title alone. Their scope could not be read, so they are not added.
4. **Lamp-device regulations.** Most additions are UN device regulations (lamps, light sources, reflex reflectors).
   They are rated under the same event definition and enter FULL only.
