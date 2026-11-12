# L1b results: a second comparison domain (exterior lighting), and the stack class

**Pre-registration:** [`L1B_preregistration.md`](L1B_preregistration.md) (`7c3896c`, approved with L1B-D1 at
`b56f1b4`). **Analysis:** [`analysis/L1B_agreement.py`](../../analysis/L1B_agreement.py) with synthetic self-test
[`analysis/L1B_selftest/`](../../analysis/L1B_selftest/) (t1–t6 pass), committed at `857134e` before either rater
branch existed. **Prompt:** [`L1B_rater_prompt.md`](L1B_rater_prompt.md) with its diff against L1's
([`L1B_rater_prompt.diff`](L1B_rater_prompt.diff)), same commit. **Raters:** `l1b-rater-a` (`4afe7a7`) and
`l1b-rater-b` (`b8ad69d`), merged at `7a7130d` / `e894922`. **Output:** [`l1b.json`](l1b.json).

**Tags.**
- Every event is **SOURCED**.
- Every class and every `stack` value is **DERIVED-judgemental**.
- **Both raters are language-model sessions** (fresh-context sub-agents of the launching session, same model). Their
  agreement measures the reproducibility of the procedure, not the independence of two judges (D-3).
- No dollar figures.

---

## 1. Verdicts

| Readout | Verdict | Why |
|---|---|---|
| **Count** (R_BL, V2) | **UNGATED** | identification 0.60 < 0.80 and κ on the four classes 0.38 < 0.60 |
| **Kind** (stack, specific events) | **UNGATED** | the same two gates; κ on `stack` passes (1.00) but every gate must pass |
| Calibration (seat domain re-rated) | **CALIBRATED** | N_S,specific 6 vs N_S1 8 (difference 2 ≤ 3); 6 of E_S1's 8 acts found (≥ 5) |
| Access | not limited | L: 0 of 22 seeds `none` for both raters (threshold 8); S: 0 of 16 (threshold 6) |

**Consequences, as pre-registered (§5):** an UNGATED verdict gives no reading. ANGLES §B.1 and POSITION §1 stand as
they were after L1. Nothing is withdrawn and nothing is confirmed. POSITION's first sentence is not rewritten.

Every number below is **UNGATED**: reported for the record and for the reviewer, deciding nothing.

## 2. Gates (§5)

| Gate | Over | Value | Bar | Pass |
|---|---|---|---|---|
| Identification M / (n_A + n_B − M) | S and L seed events in the window | **0.597** (M 46; n_A 71, n_B 52) | ≥ 0.80 | **no** |
| κ, four classes | 46 matched S and L pairs | **0.378** (observed agreement 0.72) | ≥ 0.60 | **no** |
| κ, `stack` | 46 matched S and L pairs + 51 `stack_B` rows (n 97) | **1.00** | ≥ 0.60 | yes |

**What κ on `stack` rests on.** All 46 matched S and L pairs are `no` / `no`. κ on those pairs alone is undefined (one
category), so the variance in the gate comes entirely from the 51 `stack_B` rows, on which the two raters agree row
for row (31 `yes`, 20 `no` each). Both raters judged the `stack_B` rows from the same one-line `what_changed` text
(L1 rater A's wording, carried in `B_events.csv`). Rater B states that no B source was re-read; rater A's notes do not
report re-reading any. The 1.00 is agreement on reading the same sentence, not on reading the acts.

**Why identification fails.** All 46 matches are by `act_id` (pass 1); none needed the date rule. The 31 unmatched
seed events (25 A only, 6 B only) are listed in §8. They fall into:
- **R48 / R148 / R149 supplements A counted and B did not** (A 18 on L01–L03 and L05). Most are failure tell-tale,
  bend-lighting and direction-indicator activation changes, carried in parallel across the R48 05 / 06 / 07 / 08
  series. Rater B's notes (§5 item 5) say it read the base document's justification where restated text might not be
  new, and did not count corrections or clarifications. Rater A counted them.
- **EU acts A recorded and B did not** (L10 ×2, L11 ×1, S13 ×1).
- **Seat events one rater only** (S02 ×3, S08 ×1, S09 ×1). These include 87 FR 18560 (B only, under S08; rater A did
  not record it under any instrument).
- **L20 SAE J3069:** two catalogue editions B counted under `partial` access as `cannot judge`. A recorded SAE as
  `none` (captcha).
- **Single events:** R48-06-S13, a permissive automatic-switching supplement (B only; A's convention excludes "may"
  changes), and the R149 01 series (B only).

**Why κ on classes fails.** All 13 class disagreements run the same way: A `software-only`, B `hardware-or-recert`.
Eleven of them are on R48 (L01). They are the optional projection functions:
- Driver Assistance Projection (2022);
- reversing projection (2025);
- direction-indicator projection and ADS lamp activation (2026);

plus R149-01-S3 (the scope extension to L3) and FMVSS 108's ADB rule (87 FR 9916). The two conventions, both committed
before reading:
- rater A: an optional supplement does not re-open approval; logic on the existing controller is `software-only`;
- rater B: a new lamp function needs a driver channel; with its mid-rating rule for optional new functions (B §5 item
  6), that is `hardware-or-recert`.

The split is at the class boundary L1 §2 leaves open for optional new functions.

## 3. Calibration (seat domain re-rated)

| | Value |
|---|---|
| N_S1 (L1 primary, specific seat events; computed from L1's committed ledgers by L1's functions) | 8 |
| N_S,specific (L1b, matched S seed pairs) | 6 (S02 ×4, S09 ×2) |
| \|difference\| | 2 (bar ≤ 3) |
| E_S1 acts found among the new matched S pairs | 6 of 8 (bar ≥ 5) |
| E_S1 acts not found | R16-07-S3 (S02), 91 FR 17144 (S09). Rater A recorded both; rater B did not. |
| **Status** | **CALIBRATED** |

The seat domain reproduced L1's count within the pre-registered tolerance under fresh raters.

## 4. Count readouts (V2 primary; UNGATED)

| Readout | Value |
|---|---|
| N_B | 35 (27 specific + 8 vehicle-level) |
| N_L | **48** = 40 matched L seed events + 8 |
| N_S | 14 = 6 + 8 |
| **R_BL** | **0.73** [0.47, 1.12] |
| R_BS | 2.50 [1.36, 4.60] (L1: 2.2) |
| Specific L events by instrument | L01 R48 **33**, L03 R149 3, L02 R148 1, L06 R45 1, L10 2019/2144 1, L12 FMVSS 108 1 |
| Union (either rater) | L 73, S 20 |

Read as a count, lighting received **more** events than the battery / charging domain in 2016–2026. Under the
pre-registered table, R_BL 0.73 would read NOT SPECIFIC BY COUNT if gated. The lighting count is dominated by R48:
- 33 of 40 specific events;
- supplements adopted in parallel across up to four series at one WP.29 session, each counted as its own act;
- both raters chose that convention before reading.

L1's B count used the same convention: R100 03-S4 and 04-S1 are separate rows on one date.

**Exploratory (not pre-registered), one change per instrument per adoption date:**
- specific lighting events collapse from 40 to 19, specific B events from 27 to 22;
- R_BL ≈ (22 + 8) / (19 + 8) = 1.1.

The ratio stays far from 3 either way.

**Per year, adoption date (earlier of the pair):**

| Year | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B (35) | 3 | 2 | 0 | 0 | 3 | 0 | 2 | 5 | 8 | 9 | 3 |
| L specific (40) | 0 | 2 | 1 | 3 | 1 | 1 | 9 | 3 | 2 | 9 | 9 |
| S specific (6) | 1 | 0 | 0 | 0 | 2 | 0 | 0 | 1 | 1 | 1 | 0 |

L by application year (where given; UN events carry none and fall back to adoption): 2017 2, 2018 1, 2019 2, 2020 1,
2021 1, 2022 10, 2023 3, 2024 2, 2025 9, 2026 9.

**Classes (conservative: the lower class of the pair):**
- **L:** 36 `software-only`, 4 `hardware-or-recert`. MC_L = H_L = 10 % [4, 23] of 40.
- **S:** 3 / 3. MC_S = H_S = 50 % [19, 81] of 6.

**Sensitivities (all UNGATED):**

| Variant | Identification | κ class | N_B | N_L | N_S | R_BL [95 %] |
|---|---|---|---|---|---|---|
| **V2 (primary)** | 0.597 | 0.378 | 35 | 48 | 14 | 0.73 [0.47, 1.12] |
| V1 (vehicle-level in B only) | 0.597 | 0.378 | 35 | 40 | 6 | 0.88 [0.56, 1.37] |
| V0 (vehicle-level nowhere) | 0.597 | 0.378 | 27 | 40 | 6 | 0.68 [0.42, 1.09] |
| CN0 (China-only instruments out) | 0.597 | 0.378 | 26 | 46 | 12 | 0.57 [0.35, 0.91] |
| FULL (additions in) | 0.681 | 0.332 | 35 | 79 | 14 | 0.44 [0.30, 0.66] |
| ACC (both raters `full` / `partial`) | 0.613 | 0.378 | 35 | 48 | 14 | 0.73 [0.47, 1.12] |

FULL adds 31 lighting events, 19 of them on R53 (L38), the motorcycle installation regulation cited by R148. No GB
lighting seed has a matched event: both raters had catalogue access only (`partial`) and logged the in-window GB
editions as `unreadable edition` (L-3), not counted.

**Each rater's own counts (seed instruments, window):**

| | A | B |
|---|---|---|
| L | 61 (54 `software-only`, 7 `hardware-or-recert`) | 44 (24 / 18, 2 `cannot judge`) |
| S | 10 (6 / 4) | 8 (4 / 4) |

## 5. Stack readouts (UNGATED)

**Specific events, conservative `yes` (both raters):**

| Domain | k / n judged | Share [Wilson 95 %] |
|---|---|---|
| **B** (27 non-vehicle-level) | **16 / 27** | **59 %** [41, 75] |
| **L** (40 matched seed pairs) | **0 / 40** | **0 %** [0, 9] |
| S (6 matched seed pairs) | 0 / 6 | 0 % [0, 39] |

- **Fisher's exact test, one-sided, B > L:** p = 1.2 × 10⁻⁸ (reported, not deciding).
- **B `yes` (both raters, identical):**
  - Batteries Regulation 2023/1542;
  - Euro 7 2024/1257 and implementing acts 2025/1706 and 2025/1707;
  - GTR 22 and its amendment 1;
  - GB/T 32960.1 / .2 / .3, 2016 and 2025 editions (six);
  - GB/T 27930-2023;
  - IEC 61851-1:2017, -23:2023 and -24:2023.
- **B `no`:** the eight R100 events, the two FMVSS 305 / 305a rules, and 2026/1764.
- **No rater rated any lighting or seat event `yes`:** A's 104 events and B's 86, additions included. The L share is 0
  on every subset: matched, A only, B only, FULL (0 / 71).

**Vehicle-level events, rated per domain (`stack_B` rows with domain S and L; reported separately):**

| Domain | k / 8 | Which |
|---|---|---|
| B | 5 | R155-00, R156-00, R156-01, GB 44495, GB 44496 (R155 supplements 1–3 `no`) |
| S | 5 | the same five |
| L | 5 | the same five |

Both raters rated the vehicle-level acts identically in all three domains: an act that imposes cyber-security or
update management reaches every updatable ECU.

**The kind table, applied without the gates (not a verdict):**
- k_B = 16 ≥ 3, k_L = 0 ≤ 1 and k_S = 0 ≤ 1 meet the STACK-SPECIFIC row;
- k_L < 2, and the L1B-D1 share clause (n_L = 40 ≥ 10) does not fire (0 < 0.59);
- the overlap of §5 does not occur.

The two gates that fail are about identifying and classing events, not about `stack`. The reviewer may want to say
whether this is a reading.

## 6. Access

| Seed access (A / B) | L (22) | S (16) |
|---|---|---|
| full / full | 12 | 13 |
| partial / partial | 7 | 3 |
| none / partial | 3 (L20–L22, SAE: A captcha `none`; B SAE's own Mobilus catalogue `partial`) | 0 |
| none / none | **0** (threshold 8) | **0** (threshold 6) |

Additions: S19, S20 and S23 are `none` for A and `partial` for B; S25 (SAE J800) is `none` for both.

**Blocked routes, none bypassed:**
- unece.org returned 403 to both raters, so both rebuilt the UN histories from the UN Official Document System (WP.29
  agendas, reports and AC.1 vote tables). UN events therefore carry no entry-into-force date.
- iso.org served a Cloudflare challenge (B used ISO's open-data catalogue).
- sae.org served a captcha.
- GB full texts sit behind a verification step.
- WP.29 session 200 (November 2026) had not reported, so its agenda items are not counted.

## 7. Departures reported by the raters (from their notes; none changes a §9 item)

**Rater A:**
1. Commit cadence: the first commit came after 14 instruments, one later commit after 43.
2. The UN document index was built before rating; documents were then rated in order A.
3. UN `application_date` is blank.
4. The original adoption of UN R145 was not located.
5. Three conventions were refined while rating, applied to both domains:
   - permissive "may" changes are not counted;
   - requirements on child restraints, light sources and passive reflectors are not ECU obligations;
   - each parallel-series supplement is its own act.

**Rater B:**
1. Session 200 is not recorded.
2. Agenda-parse gaps were closed by hand.
3. AC.1 supplement-number conflicts were resolved as listed.
4. Parallel documents count separately (chosen before reading).
5. R149-01-S6 was withdrawn before its first commit (renumbering only).
6. After instrument 37, R50-00-S18 was re-classed `hardware-or-recert` under a new optional-function rule (an
   addition; outside the primary).
7. `stack_B` was rated from `what_changed` only.
8. 87 FR 18560 was placed under S08, the first listed instrument it amends.

No deviation L1B-D2 was needed: the launching session changed nothing after a change history was read.

## 8. Every disagreement (never reconciled)

**Unmatched, rater A only (25):**

| Instrument | act_id | Adopted | Class |
|---|---|---|---|
| L01 | R48-04-S17, R48-05-S10, R48-06-S8 | 2016-11-16 | software-only |
| L01 | R48-06-S10 | 2017-11-15 | hardware-or-recert |
| L01 | R48-05-S12 | 2018-11-14 | software-only |
| L01 | R48-06-S18, R48-07-S5, R48-08-S3 | 2023-03-08 | software-only |
| L01 | R48-06-S20, R48-07-S7, R48-08-S5 | 2024-03-06 | software-only |
| L02 | R148-00-S2 | 2020-03-11 | software-only |
| L02 | R148-00-S3 | 2021-03-10 | software-only |
| L02 | R148-00-S4 | 2022-03-09 | software-only |
| L02 | R148-01 | 2022-06-22 | hardware-or-recert |
| L03 | R149-00-S3 | 2021-03-10 | software-only |
| L03 | R149-01-S6 | 2025-11-12 | software-only |
| L05 | R123-01-S8 | 2017-03-15 | software-only |
| L10 | 32022R1398 | 2022-06-08 | hardware-or-recert |
| L10 | 32022R1426 | 2022-08-05 | software-only |
| L11 | 32019R0543 | 2019-04-03 | software-only |
| S02 | R16-07-S1 | 2017-06-21 | software-only |
| S02 | R16-07-S3 | 2018-06-20 | software-only |
| S09 | 91 FR 17144 | 2026-04-06 | software-only |
| S13 | 32019R2144 | 2019-11-27 | hardware-or-recert |

**Unmatched, rater B only (6):**

| Instrument | act_id | Adopted | Class |
|---|---|---|---|
| L01 | R48-06-S13 | 2019-11-13 | software-only |
| L03 | R149-01 | 2022-06-22 | hardware-or-recert |
| L20 | SAE J3069_201606 | 2016-06-30 | cannot judge |
| L20 | SAE J3069_202103 | 2021-03-25 | cannot judge |
| S02 | R16-10-S3 | 2026-06-24 | software-only |
| S08 | 87 FR 18560 | 2022-03-30 | hardware-or-recert |

**Class disagreements (13; A `software-only`, B `hardware-or-recert` in every one):**

| Instrument | act_id | Adopted | Subject |
|---|---|---|---|
| L01 | R48-06-S16, R48-07-S3, R48-08-S1 | 2022-06-22 | Driver Assistance Projection |
| L01 | R48-06-S22, R48-07-S9, R48-08-S7, R48-09-S2 | 2025-11-12 | reversing projection (optional) |
| L01 | R48-06-S24, R48-07-S11 | 2026-06-24 | direction-indicator projection (optional) |
| L01 | R48-08-S9, R48-09-S4 | 2026-06-24 | lamp activation by an ADS; direction-indicator projection |
| L03 | R149-01-S3 | 2024-03-06 | scope extended to AFS / ADB for L3 vehicles |
| L12 | 87 FR 9916 | 2022-02-22 | FMVSS 108 permits adaptive driving beam |

**Stack disagreements:** none, on the 46 matched S and L pairs or on the 51 `stack_B` rows.

**Window-straddling pairs:** none.

Full rows, with `what_changed` and sources: `l1b.json` (`primary_V2.unmatched_A`, `unmatched_B`,
`class_disagreements`).

## 9. Exposure disclosure (§8, repeated)

The launching session ran L1 stage 2:
- it wrote L1's analysis script;
- it merged and read both L1 ledgers and notes;
- it wrote `results_L1.md`;
- it has read the L1 review, including the reviewer's exploratory five-act stack split.

It reached the raters only through the five-file clone and the launch prompt. That prompt is L1's with mechanical
substitutions, plus the `stack` instructions and one blindness line ("do not read this project's repository on the
web"), and its diff is committed. The B events' `what_changed` text was written by L1's rater A, and the session did
not edit it. Both L1b raters judged `stack_B` from that text. The session did not read either L1b ledger until both
branches were merged, and changed nothing in the procedure after that.
