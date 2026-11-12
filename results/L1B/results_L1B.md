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

---

## 10. Reviewer acceptance (2026-11-12)

**Accepted at `b0226dd` (Status `359df6a`): count UNGATED, kind UNGATED, seat domain CALIBRATED, lighting not
access-limited — confirmed.** Every number above was re-derived from `ledger_A.csv`, `ledger_B.csv`,
`instruments_A.csv`, `instruments_B.csv`, `stack_B_A.csv`, `stack_B_B.csv`, `B_events.csv` and L1's two ledgers with the
reviewer's own code ([`review/reviewer_check.py`](review/reviewer_check.py), output
[`review/reviewer_check.out`](review/reviewer_check.out)), which reads nothing `L1B_agreement.py` wrote. Agreement is
exact on: n_A 71, n_B 52, M 46 (all by `act_id`, none by the date rule), identification 0.597, κ(classes) 0.378
(observed 0.717), κ(`stack`) 1.000 over 97 rows (46 pairs all `no`/`no`; 51 `stack_B` rows 31 `yes` / 20 `no` for each
rater); N_S1 8 and E_S1 recomputed from L1's ledgers, N_S,specific 6 (S02 ×4, S09 ×2), difference 2, 6 of 8 acts found
(R16-07-S3 and 91 FR 17144 not); N_L 48 (40 + 8), N_S 14, R_BL 0.73 [0.47, 1.12], R_BS 2.50 [1.36, 4.60]; V1 0.88, V0
0.68, CN0 26 / 46 / 12 → 0.57, FULL 35 / 79 → 0.44 (identification 0.681, κ 0.332; 31 added events, 19 on R53), ACC
unchanged (identification 0.613); L01 33 of 40; classes L 36 / 4 (MC_L 10 % [4, 23]), S 3 / 3; all three per-year tables
and the application-year row; each rater's own counts; the access table (12 / 7 / 3 / 0 and 13 / 3 / 0 / 0; S19, S20,
S23 `none`/`partial`, S25 `none`/`none`); no matched event on a GB seed; the 25 + 6 unmatched events and the 13 class
disagreements, row for row; no stack disagreement; no window-straddling pair; stack B 16 / 27 = 59 % [41, 75], L 0 / 40
[0, 9], S 0 / 6 [0, 39]; Fisher one-sided p = 1.16 × 10⁻⁸; vehicle-level `yes` 5 of 8 in each of B, S and L (the same
five); the kind table's STACK-SPECIFIC row met with no overlap; the exploratory collapse 40 → 19 and 27 → 22, R_BL ≈ 1.1.
`l1b.json` carries the same values.

**Process checks.** `analysis/L1B_agreement.py`, its self-test and the launch prompt were committed at `857134e`
before either branch existed, and never touched again. Both branches fork from `857134e`. Rater A's conventions were
committed at `267949f` (22:20 UTC, 11 Nov) before its first ledger commit (23:04); rater A finished at `4afe7a7` (23:19).
Rater B's conventions were committed at `9091fe4` (00:52 UTC, 12 Nov), after A had finished; B's branch contains no A
file and `4afe7a7` is not an ancestor of `b8ad69d`: B never fetched A. The merges (`7a7130d`, `e894922`) are clean, and
no rater file changed after them; the session's two later commits add only `results_L1B.md`, `l1b.json`, the index rows
and dated notes. Each launch prompt differs from the committed `L1B_rater_prompt.md` only in the `{R}` / `{r}`
substitutions and the clone and scratch paths. No source was bypassed: unece.org (403), iso.org (challenge), sae.org
(captcha) and the GB full-text viewer are recorded as blocked by both raters, and the UN histories were rebuilt from the
UN Official Document System. POSITION §1 sentence 1 was not rewritten by the session, as instructed.

### Is the kind readout a reading? No — and what the data does settle anyway

The pre-registration (§5) makes the three gates joint for both verdicts, and two fail. The reviewer does not reopen
that: UNGATED gives no reading, and the kind row is reported as what the table *would* say. Three reasons, beyond the
rule itself:

1. **κ(`stack`) = 1.00 carries no information about the seat and lighting events.** All 46 matched pairs are `no` /
   `no`; κ on them alone is undefined. The gate passes on the 51 battery rows, which both raters judged from the same
   one-line `what_changed` text (item R-3 below). It measures how reproducibly two readers classify one sentence, not
   how reproducibly two readers classify the acts.
2. **The identification gate is the only instrument that bounds recall, and it failed.** No matching choice can put a
   lighting event into the `yes` column — every one of the 190 S and L rows either rater wrote, additions included, is
   `no` — so the 0 / 40 is robust to how the ledgers are reconciled. It is not robust to an act both raters missed, and
   with 25 events found by A only and 6 by B only, the procedure's recall is exactly what the gate was there to vouch
   for.
3. **The class gate failed on a definitional boundary** (optional new functions, item R-1), which `stack` does not
   share. That is why the kind readout looks clean while the class readout does not; it is not a reason to gate one
   field of a ledger whose rows the two raters did not agree on.

What the two ledgers do settle, ungated and in the reviewer's reading:

- **By count, lighting is not the quiet comparison domain the brief took it for; it is the busier one.** Under every
  counting the reviewer can construct from these ledgers — matched events (R_BL 0.73), rater A alone (0.51), rater B
  alone (0.67), the union (0.48), FULL (0.44), one event per instrument per adoption date with the battery count as it
  stands (1.30) or collapsed the same way (1.11) — R_BL lies between 0.44 and 1.3. The 3× row of the count table is out
  of reach of this data; what fails is the count form of ANGLES §B.1, in the direction L1 already pointed. The lighting
  count is also a floor: all seven GB seeds and the three SAE seeds were unreadable in the window.
- **By kind, the separation is total in both raters' hands:** 16 of 27 specific battery events and 0 of 46 seat and
  lighting events name an obligation of one of the five kinds; the five vehicle-level cyber-security and update acts
  were rated `yes` for all three domains alike. This is the second exploratory observation in that direction (L1's
  reviewer split was the first, on a narrower definition); it is still exploratory.

### Reviewer items (numbered; none is a deviation of the pre-registration, which has only L1B-D1)

- **R-1. Rater B's class rule for optional new functions was adopted at position 37 of order B — which is L01, UN R48
  itself** — and applied retroactively to one addition row (R50-00-S18, L41). Eleven of the thirteen class disagreements
  are R48 projection and ADS-activation supplements rated under that rule. The rule was formed after R48's history had
  been read; rater B disclosed it (notes §5 item 6). Rater A's committed convention reads the other way ("a supplement
  that is optional does not re-open type approval"; logic on the existing controller is `software-only`). L1 §2 does not
  settle optional new functions. Both conventions are on the record; the classes are used conservatively (the lower of
  the pair), so MC_L = 10 % is a floor (rater B's own classes give 18 of 42 judged). A rerun pre-registers the rule.
- **R-2. Rater A refined three conventions while rating** (notes §6 item 5: permissive "may" changes not counted;
  obligations on child restraints, light sources and passive reflectors not ECU obligations; each parallel-series
  supplement its own act). Disclosed. The third coincides with rater B's committed convention 1.1 (4); the first two
  reduce A's count, and A still recorded 25 seed events B did not.
- **R-3. Both raters rated `stack_B` from the `what_changed` line alone**, which §3 permits ("may read its source").
  Seven of the sixteen `yes` events are the GB/T 32960 (×6) and GB/T 27930-2023 catalogue entries, whose class in L1 was
  `cannot judge` for both raters: their `yes` rests on a title that names a remote service and management system, an
  on-board terminal, or a charger–vehicle communication protocol, with confidence from `low` to `high`. Without them
  k_B / n_B is 9 / 20 = 45 % [26, 66] (Fisher p 1.1 × 10⁻⁵); also without the three IEC 61851 charging-communication
  editions, 6 / 17 = 35 % [17, 59] (p 3.4 × 10⁻⁴). The STACK-SPECIFIC row (k_B ≥ 3) is met in each.
- **R-4. The `stack` class is broader than the Linux-class-forcing set POSITION §1 names, and the two must not be
  conflated.** Of the sixteen specific `yes` events, three are POSITION's acts (2023/1542, 2024/1257, 2025/1707; R155-00
  and R156-00 are vehicle-level). The other thirteen name telemetry (GB/T 32960), charging communication (IEC 61851-1 /
  -23 / -24, GB/T 27930) or data read-out and update disclosure (GTR 22, GTR 22-A1, 2025/1706). Several of those are
  MCU-class obligations — a PWM control pilot, a CAN protocol. "16 of 27 force the stack" means "16 of 27 name an
  external-communication, data, update or cryptographic obligation"; it does not mean sixteen acts force Tier A. The
  finding is that the comparison domains carry **none of any kind**, under either rater — a statement about what kind
  of system a battery / charging ECU is made to be by regulation (communicating, data-holding, updatable), not a count
  of acts that size a DRAM. POSITION §1's "five acts" and "thirty smaller events are software" are class statements and
  stand; L1b's `stack` is a separate field.
- **R-5.** The unions in §4 ("L 73, S 20") include the 8 vehicle-level events; the seed-only unions are 65 and 12.
- **R-6.** Rater A's first ledger commit came after 14 instruments and the next after 43 (prompt: every 10). A commit
  habit, not a blindness issue.
- **R-7. Identification by domain: L 0.615, S 0.500** (L1: S 0.667, B 0.897). Over L1 and L1b the 0.80 gate has been met
  only where the battery domain's CELEX-numbered acts and R100 series dominated the union; both body-ECU domains sit at
  0.5–0.67 under fresh raters. The split is a granularity and inclusion property of the procedure (one WP.29 adoption =
  one act per series in force; corrections and clarifications; "may" clauses), as DC2's was, not a rater failing. A
  rerun fixes it in advance, as DC2-R did for rows.
- **R-8.** N_L is a floor (seven GB and three SAE seeds unreadable); a floor strengthens only the direction already
  found.
- **R-9.** Adoptions in 2025–2026: L 18 of 40 specific events, B 12 of 35, S 1 of 6. The acceleration L1 read on the
  battery domain has a lighting counterpart (ungated).
- **R-10.** Housekeeping in this commit: SYNTHESIS §1 carried two DC2-R rows (one from the session's DC2-R write-up, one
  from the review); merged into one.

### Consequences written in this commit

None of the pre-registered consequences fires. ANGLES §B.1, SYNTHESIS §3 and POSITION §1 stand as they were after L1;
the session's dated notes are correct and are kept, and the reviewer adds one sentence to each (item R-4) so that
"16 of 27" is not read as sixteen Linux-class acts. SYNTHESIS is retitled to ten experiments. `NEXT_TASK.md` → CLOSED.

### What would gate the kind verdict (recorded for Kyle's decision; not scheduled)

An **L1b-R** on the same instruments and the same two fixed ledgers' sources would need: (i) the class rule for optional
new functions, and the counting rule for parallel-series supplements, corrections and "may" clauses, written into the
pre-registration (R-1, R-7); (ii) identification measured on instrument-dates, the DC2-R fix; (iii) `stack_B` rated from
the acts' own texts, `cannot judge` where only a catalogue entry is readable (R-3); and (iv), if POSITION §1 is the
sentence to gate, a second pre-registered tier of `stack` restricted to cryptographic, authenticated-update, data-retention-
with-access and OTA obligations (R-4). With those, the count verdict would read NOT SPECIFIC BY COUNT under any plausible
outcome (R_BL ≤ 1.3 in every counting here), and the kind verdict would be whatever two fresh raters find; on this
evidence, STACK-SPECIFIC. The alternative is to stop here: POSITION already states the thesis at its gated level
(exploratory on kind), and L1b adds a second ungated observation in the same direction, plus the count result that the
battery box is not the busiest ECU domain by arrival rate.
