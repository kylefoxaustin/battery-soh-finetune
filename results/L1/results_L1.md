# Results L1: the requirement-arrival ledger

**How often do software-visible requirements land on the battery / charging / power-conversion ECU domain, compared
with the seat / interior domain?** Study L1, run 2026-11-10.

| | |
|---|---|
| **Pre-registration** | [`L1_preregistration.md`](L1_preregistration.md), `af2d5cb`, with reviewer deviations L-1 … L-5 (§9, `e98f8b3`), all before any change history was read |
| **Instrument list** | [`L1_instruments.md`](L1_instruments.md): 63 instruments fixed blind; 51 seeds are the primary (L-5) |
| **Ledgers** | `ledger_A.csv` and `instruments_A.csv` (branch `l1-rater-a`, `acd5f1d`); `ledger_B.csv` and `instruments_B.csv` (branch `l1-rater-b`, `ddc2070`). Notes and launch prompts beside them. |
| **Code** | `analysis/L1_agreement.py`, committed on `main` (`b5a0d40`) before either rater branch existed and tested on synthetic ledgers (`analysis/L1_selftest/`) |
| **Output** | `l1.json`: every number below, every unmatched event, every disagreement |
| **Tags** | Every event is **SOURCED** (URL, `act_id`, date). Every classification is **DERIVED-judgemental**. Counts and fractions are **DERIVED** from the two ledgers. No dollar figures. |

---

## Verdict (pre-registered §6 with L-1 and L-2)

> **UNCLEAR** [V1: VOLATILE DOMAIN]. Not access-limited.
> **Kill for ANGLES §B.1: does not fire** under the primary, V1 or FULL.

**Domain B passes two of the three VOLATILE conditions and fails the third:**

| Condition | Result | Pass? |
|---|---|---|
| Events | **35** matched events, 3.2 a year (≥ 11 needed) | yes |
| MC (`memory-or-crypto` or above) | **38 %** [22, 57] (≥ 25 % needed, lower bound > 10 %) | yes |
| R = N_B / N_S | **2.2** | **no** (needs ≥ 3) |

**Why R falls short: L-1.** It counts the four vehicle-level instruments (UN R155, R156, GB 44495, GB 44496) on both
sides. Their 8 matched events make up half of domain S's 16.

| Reading | R | Verdict |
|---|---|---|
| Brief's listing (V1): vehicle-level events in domain B only | 35 / 8 = 4.4 | VOLATILE DOMAIN |
| Vehicle-level events removed from both (V0) | 27 / 8 = 3.4 | VOLATILE DOMAIN |

**Kill.** STABLE did not fire, and R ≥ 1.5 in every variant except CN0 (R = 1.9).

**Reading in one line.** The battery / charging domain received **3.2 software-visible requirement events a year** in
2016–2026 against **0.7 a year** specific to seats and interiors. **38 %** of the battery-domain events need more
memory, crypto, new hardware, or re-approval. Counting cybersecurity and software-update management on both sides
puts the domain-specific excess at about 2×, short of the pre-registered 3×.

## Gates

| Gate | Value | Bar | Pass |
|---|---|---|---|
| **Identification**, M / (n_A + n_B − M) | **0.843** (M = 43; n_A = 45, n_B = 49) | ≥ 0.80 | yes |
| **Classification κ**, four classes, unweighted | **0.820** (n = 43; observed agreement 88.4 %) | ≥ 0.60 | yes |

**How the 43 pairs matched:** 40 by identical `act_id` (L-4 pass 1) and 3 by the ± 90-day rule.

> **κ is reproducibility, not independence (D-3).** Both raters are language-model sessions (fresh-context sub-agents
> of the same model) working from the same instrument list and the same allowed routes. κ and the identification
> agreement measure how reproducible the ledger is, not its independence from a shared model prior. Neither rater saw
> the other's branch: each worked in a sparse clone of `main` with four files, and rater B never fetched
> `l1-rater-a`.

## Events per year (matched pairs; adoption year; the earlier of the two raters' dates)

| Year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | Total | Per year |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Domain B** | 3 | 2 | 0 | 0 | 3 | 0 | 2 | 5 | 8 | 9 | 3 | **35** | 3.2 |
| **Domain S (V2, incl. vehicle-level)** | 1 | 0 | 1 | 0 | 4 | 0 | 1 | 2 | 4 | 2 | 1 | **16** | 1.5 |
| of which vehicle-level | | | | | | | | | | | | 8 | 0.7 |
| **Domain S, seat-specific** | | | | | | | | | | | | **8** | 0.7 |

- **Domain B is accelerating:** 22 of its 35 events fall in 2023–2025.
- **By application year,** domain B has 3 / 2 / 3 / 2 / 3 / 7 / 8 / 6 events in 2016 / 2017 / 2020 / 2022 / 2023 /
  2024 / 2025 / 2026, and 1 in 2027.
- **2026 is incomplete:** the November 2026 WP.29 session had not been reported.

**Domain-B events by instrument** (matched):

| Instrument | Events |
|---|---|
| UN R100 | 8 |
| Euro 7 (2024/1257 and its implementing acts) | 4 |
| UN R155 | 4 |
| UN GTR 22 | 2 |
| UN R156 | 2 |
| GB/T 32960.1 | 2 |
| GB/T 32960.2 | 2 |
| GB/T 32960.3 | 2 |
| FMVSS 305 / 305a | 2 |
| Batteries Regulation 2023/1542 | 1 |
| GB/T 27930 | 1 |
| GB 44495 | 1 |
| GB 44496 | 1 |
| IEC 61851-1 | 1 |
| IEC 61851-23 | 1 |
| IEC 61851-24 | 1 |

**Domain-S events by instrument** (matched, seat-specific):

| Instrument | Events |
|---|---|
| UN R16 (seat-belt reminder) | 5 |
| FMVSS 208 | 3 |

By jurisdiction, 9 of the 43 matched events are China-only.

## The class fractions

**Domain B** (35 events, conservative class). 9 events are `cannot judge`, all of them GB editions read from the
catalogue only (L-3), which leaves 26 judged:

| Fraction | Value | Wilson 95 % CI |
|---|---|---|
| **MC** (`memory-or-crypto` or above) | **10 / 26 = 38.5 %** | 22.4–57.5 % |
| **H** (`hardware-or-recert`) | **9 / 26 = 34.6 %** | 19.4–53.8 % |
| `software-only` | 16 / 26 | |
| `memory-or-crypto` | 1 / 26 | |

**Basis.** MC and H rest on 26 judged events from **16 of the 35** domain-B seed instruments.
- **Unread by both raters:** the 10 SAE seeds (J1772, J3400, J2847/1, /2, /3, /6, J2931/1, /4, /6, /7). sae.org
  served a bot challenge on every page, and nothing was bypassed.
- **Read but yielding no matched event:**
  - UN R10, where both raters judged its charging-mode changes to be EMC hardware and test set-up;
  - AFIR, where neither rater recorded an event (rater B: its obligations fall on charging points);
  - GB 38031 and GB/T 18487.1, whose editions were unreadable;
  - ISO 15118-2, -20, -8 and ISO 17409 (below);
  - FMVSS 305a, counted under FMVSS 305 by the never-twice rule.

**Domain S** (non-deciding):

| | Events | Judged | MC | H |
|---|---|---|---|---|
| Seat-specific | 8 | 8 | 3 / 8 = 37.5 % [13.7, 69.4] | 3 / 8 = 37.5 % [13.7, 69.4] |
| With the vehicle-level events carrying their domain-B class (L-1) | 16 | 14 | 7 / 14 = 50.0 % [26.8, 73.2] | 7 / 14 = 50.0 % [26.8, 73.2] |

**What drives `hardware-or-recert`.** Both raters applied §2's "re-opens type approval": a requirement that approved
types must newly meet by a stated date. That is why R155, R156, Euro 7's battery-durability acts and the FMVSS final
rules land there. Rater B applied it more literally to the three Euro 7 acts, which are 3 of the 5 class disagreements. The two FMVSS
disagreements go the other way.

## Access (L-3)

| Seed instruments, rater A / rater B | full / full | partial / partial | none / partial | none / none |
|---|---|---|---|---|
| **Domain B (35)** | 13 | 8 | 4 | **10** |
| **Domain S (16)** | 13 | 3 | 0 | 0 |

- **Not access-limited.** Both raters marked 10 of the 35 B seeds `none`, below the 12 of L-2. Domain S has none.
- **The 4 `none / partial` seeds are ISO 15118-2, -20, -8 and ISO 17409.**
  - iso.org returned HTTP 403 to both raters.
  - Rater B found ISO's own open-data catalogue file and read edition identifiers and dates from it, so it is the
    body's own catalogue (§3b rule 2). Rater A did not find it.
  - B's 4 ISO events (ISO 15118-20:2022, its Amd 1:2026, ISO 15118-8:2018 and :2020) are therefore unmatched. They do
    not enter N_B.
  - Excluding them would raise identification to 43 / 45 = 0.96 and change nothing else.
- **GB instruments are `partial` for both raters.** The catalogue gives editions and dates; the texts sit behind a
  verification step.

## Sensitivities (none deciding)

| Variant | N_B | N_S | R | MC_B | Verdict |
|---|---|---|---|---|---|
| **Primary (V2)** | 35 | 16 | 2.19 | 38.5 % [22.4, 57.5] | **UNCLEAR** |
| V1: vehicle-level events in B only (the brief's listing) | 35 | 8 | 4.38 | 38.5 % | **VOLATILE DOMAIN** |
| V0: vehicle-level events in neither domain | 27 | 8 | 3.38 | 30.0 % [14.5, 51.9] | **VOLATILE DOMAIN** |
| CN0: China-only instruments excluded | 26 | 14 | 1.86 | 38.5 % | UNCLEAR |
| FULL: all 63 instruments | 35 | 16 | 2.19 | 38.5 % | UNCLEAR (the 12 additions yielded no events) |
| ACC: instruments both raters could read | 35 | 16 | 2.19 | 38.5 % | UNCLEAR (identification 0.91) |

**Each rater's own ledger** (seed instruments):

| Rater | Domain B events | MC_B | Domain S events |
|---|---|---|---|
| A | 35 | 42.3 % | 10 |
| B | 39 | 50.0 % | 10 |

**Union of both ledgers:** domain B 39, domain S (V2) 20.

## Every disagreement (listed, never reconciled)

**Unmatched in rater A (2):**

| `act_id` | Instrument | Date | A's class |
|---|---|---|---|
| R16-07-S1 | UN R16 | 2017-06-21 | software-only |
| R16-10-S3 | UN R16 | 2026-06-24 | software-only |

**Unmatched in rater B (6):**

| `act_id` | Instrument | Date | B's class |
|---|---|---|---|
| ISO 15118-20:2022 | ISO 15118-20 | 2022-04-26 | memory-or-crypto |
| ISO 15118-20:2022/Amd 1:2026 | ISO 15118-20 | 2026-07-13 | cannot judge |
| ISO 15118-8:2018 | ISO 15118-8 | 2018-02-27 | hardware-or-recert |
| ISO 15118-8:2020 | ISO 15118-8 | 2020-09-21 | cannot judge |
| 87 FR 18560 | FMVSS 207 | 2022-03-30 | hardware-or-recert |
| 32019R2144 | GSR2 base act | 2019-11-27 | hardware-or-recert |

Rater A counted the ADS rule (87 FR 18560) under neither FMVSS 207 nor 208, reading it as terminology that keeps the
existing requirements. It judged the GSR2 base act not to be a seat event, because its belt-reminder and seating rows
already applied.

**Class disagreements on matched pairs (5):**

| `act_id` | Instrument | Rater A | Rater B |
|---|---|---|---|
| 32025R1706 | Euro 7 | software-only | hardware-or-recert |
| 32025R1707 | Euro 7 | memory-or-crypto | hardware-or-recert |
| 32026R1764 | Euro 7 | software-only | hardware-or-recert |
| 82 FR 44945 | FMVSS 305 | hardware-or-recert | software-only |
| 89 FR 67869 | FMVSS 208 | hardware-or-recert | software-only |

## Procedure notes and deviations

**No numbered deviation.** Nothing in §8 moved, and no departure from the pre-registration was made after a change
history was read.

**Disclosed:**
- **Blocked routes, nothing bypassed.**
  - unece.org (HTTP 403): both raters built the UN regulation and GTR histories from the UN Official Document System
    (WP.29 agendas and session-report vote tables), an allowed route. UN adoption dates are the vote dates.
  - iso.org (HTTP 403) and sae.org (bot challenge): see Access.
- **Order of work.** Rater A fetched some documents ahead of their turn and filed two sets of rows out of order. Rater
  B committed in its order but researched by source type. Both are disclosed in the notes.
- **Per-year tables.** A matched pair is dated by the earlier of its two adoption dates. That is an implementation
  choice the pre-registration did not specify. No pair straddles the window.
- **Undated acts.** Rater B left out two undated "Amendment No. 1" entries (GB 44495, GB 44496), since the window
  rule needs a date.

## What this says (for ANGLES §B.1)

1. **The arrival process exists and is counted.**
   - 35 dated, sourced events in eleven years on the battery / charging domain, reproducible between two blind raters
     (identification 0.84, κ 0.82).
   - It accelerates: 22 events in 2023–2025, against 5 in 2016–2017.
   - Counted by dated act rather than by regime, the rate is well above the "five regimes in eight years" ANGLES §B.1
     gave from memory.
2. **More than a third of those events are not software-only** (MC 38 % [22, 57]). Nine of the ten are
   `hardware-or-recert`. Under §2 that class includes re-approval by a stated date, and the ledgers do not separate
   re-approval from new hardware.
3. **The 3× specificity is not established.**
   - With cybersecurity and software-update management counted as a floor common to every connected ECU (L-1, decided
     blind), the battery domain receives about 2.2× the seat domain's events.
   - Without that floor it is 3.4–4.4×.
   - The pre-registered verdict is UNCLEAR, and the kill does not fire.
4. **The count is a floor for domain B.**
   - The 10 SAE charging and communication standards, and the content of the ISO 15118 revisions, were unreadable
     without bypassing.
   - Rater B's catalogue-only ISO record adds 4 events that would raise N_B.

---

## Reviewer acceptance (2026-11-10)

Accepted at `a03164b`. Every number above was re-derived by the reviewer from the two ledgers and the two instruments
files with independent code ([`review/reviewer_check.py`](review/reviewer_check.py), output
[`review/reviewer_check.out`](review/reviewer_check.out)); agreement is exact. Process checks (script before raters,
conventions before reading, no post-merge edits, no hypothesis in the launch prompt) and the reviewer's exploratory
readings are in [`review/README.md`](review/README.md): a binomial interval on R of [1.2, 3.9]; a split of the ten
above-software events into **five `stack` events (R155, R156, 2023/1542, 2024/1257, 2025/1707; 19 % [9, 38] of judged)**
and five re-approval / function events; and two counting-rule sensitivities (R 2.0–2.2). None is pre-registered and none
changes the verdict.

---

*Events SOURCED (UNECE / UN ODS, EUR-Lex, eCFR / Federal Register, IEC, SAMR / openstd, ISO open data). Classifications
DERIVED-judgemental, by two language-model raters (D-3). No dollar figures.*
