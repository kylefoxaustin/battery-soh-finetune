# DC2 results: the ramp-spec audit

**Brief:** [`briefs/DC2/README.md`](../../briefs/DC2/README.md).
**Pre-registration:** [`DC2_preregistration.md`](DC2_preregistration.md) (`60f7595`), with deviations DC2-1 and DC2-2
(§10, `1dda7d3`).
**Instruments:** [`DC2_instruments.md`](DC2_instruments.md): 56 instruments (50 seeds, 3 S3 additions, 3 DC2-1
additions).
**Code:** [`analysis/DC2_agreement.py`](../../analysis/DC2_agreement.py), committed (`aad23bd`) before either rater
branch existed and not changed since. **Data:** [`dc2.json`](dc2.json).
**Rater files:** `requirements_<A|B>.csv`, `instruments_<A|B>.csv`, `rater_<A|B>_notes.md` and the launch prompts,
from branches `dc2-rater-a` (`e2d3baf`) and `dc2-rater-b` (`bfb6361`).

**Tags.**
- Every requirement is **SOURCED**: URL, document, clause, and a quote of at most 25 words, in the two CSVs.
- Every class is **DERIVED-judgemental**.
- Both raters are language-model sessions (D-3, beside κ below).
- No dollar figures.

---

## 1. Verdict

> **UNGATED.** Identification agreement is **0.523** (M 127, n_A 204, n_B 166), below the 0.80 gate. κ on the window
> class over the 113 clause-matched pairs is **0.644**, which passes. Under §6, UNGATED is checked first and nothing
> below it is read.
>
> **Consequence for ANGLES §B.2 (pre-registered):** no reading. The anticipation leg stays where DC1 left it.

- **Not access-limited.** No seed instrument was `none` for either rater (threshold ≥ 17 of 50). The 10 seeds that
  both raters read only through abstracts or catalogue pages are Q01–Q06, E05–E07 and U02.
- **The script's `verdict_line` field.** It reads "UNGATED (…) — history-shaped requirement at POI / facility only".
  The script appends the measurement-point clause whenever a history-shaped pair exists, without checking the gate.
  The verdict is the `verdict` field, UNGATED. The script is not changed after reading; this is a display artefact,
  not a deviation.

**What the gate failure is made of.** It is the two raters' **row granularity**, almost entirely on quantities that do
not decide (§3):
- rater A wrote one row per harmonic formula and per ride-through curve point; rater B wrote one row per table;
- the deciding rows agree better, but not well enough (§5, exploratory).

**The one thing the raters agree on that matters for §B.2, read exploratorily only.** Both raters, blind to each other,
recorded the same two clauses as the only binding, deciding, history-shaped requirements in their files: **ERCOT Nodal
Protocols §6.5.7.11(1) and (2)**. Both gave them identical classes: ramp rate; measurement point `facility`; window
`1 – 60 s` (a stated one-minute assessment interval); allowance `very loose` (compliance when ≥ 90 % of eligible
one-minute intervals in a month meet the band, so 10 % may fail); `mandatory`. Had the gate passed, the primary verdict
would have been HISTORY-SHAPED SPEC EXISTS on these two clauses alone. The gate did not pass, so this is not a verdict.
The caveats are in §4.

---

## 2. Gates (§5)

| Gate | Value | Bar | Result |
|---|---|---|---|
| **Identification** M / (n_A + n_B − M) | 127 / (204 + 166 − 127) = **0.523** | ≥ 0.80 | **fails** |
| **κ(window class)** over M₁ = 113 pass-1 pairs | **0.644** (observed agreement 0.708) | ≥ 0.60, M₁ ≥ 10 | passes |

*DERIVED-judgemental. Both raters are language-model sessions; κ measures how reproducibly the classes are read from
the same texts, not independence from a shared model prior (FR1 D-3).*

**Also reported (none gating):**

| Quantity | Value |
|---|---|
| Matching | M 127: 113 by clause and category (pass 1), 14 by quantity and window class (pass 2) |
| κ(window class) over all 127 pairs | 0.681 (pass-2 pairs agree on window by construction) |
| κ(allowance class), M₁ | 0.707 (observed 0.912) |
| κ(computed shape), M₁ | 0.569 (observed 0.708) |
| Binding class, all M | κ 1.000 (observed 1.000) |
| Deciding, all M | κ 0.741 (observed 0.929) |
| Field disagreements over the 127 pairs | window 33, allowance 13, quantity 12, measurement point 5, deciding 9, computed shape 33, binding 0 |
| Rater-written shape differing from computed shape | 0 rows |
| DC2-2 conversions | 0. Neither rater found a clause printing both a recurrence and a duration of a permitted exceedance |

## 3. Where the identification gap is

**Matched and unmatched rows, by instrument:**

| Instrument | Matched | Unmatched A | Unmatched B | What differs |
|---|---|---|---|---|
| E01 Demand Connection Code | 2 | 23 | 16 | ride-through rows split differently (A 23, B 14 unmatched); B's Art. 30(2)(c) response row and one `other` row have no A counterpart |
| E10 D-A-CH-CZ Part B-II | 11 | 20 | 4 | harmonics: A one row per formula, B one row per table (A's unmatched rows on E09–E11: harmonics 36, other 7); B's three step-change planning levels (Tab. 1-2) unmatched |
| E11 D-A-CH-CZ Part B-III | 11 | 18 | 4 | as E10 |
| E09 D-A-CH-CZ Part B-I | 8 | 5 | 4 | as E10 (Tab. 1-3) |
| E08 D-A-CH-CZ Part A | 0 | 5 | 0 | A: in force, 5 rows; B: `no requirement` |
| V11 NVIDIA GB300 power-smoothing blog | 0 | 0 | 5 | B: 5 `vendor capability` rows; A: `no requirement` ("the pages name the configurable parameters but print no value or range") |
| X01, X02, V04, V05, V08, E04 | 50 | 6 | 5 | single rows |
| G02, G03, U03, V03, V06, V07, V09 | 41 | 0 | 0 | none |

**Unmatched rows by quantity.**
- **A (77):** harmonics 41, ride-through 26, other 9, hold-up 1. None is deciding.
- **B (39):** ride-through 17, step change 10, smoothing or capping response 3, flicker 3, other 2, ramp rate 2, swing
  amplitude 1, power factor 1. **16 are deciding:**
  - 9 D-A-CH-CZ step-change planning levels (E09–E11), window `not stated`;
  - 5 NVIDIA vendor-capability rows (V11);
  - E01 Art. 30(2)(c);
  - V04 §5.1.

  None of the 16 is history-shaped.

**Quantity disagreements on matched rows.** Nine OCP rack, shelf, PSU and BBU supply-envelope pairs (V03, V05, V06, V07,
V08) are `other` for A and `step change` for B. That is the whole of the `deciding` disagreement. A made this a
reading-time judgement (notes §7 item 8: supply envelopes "rate what the supply must deliver"). B recorded it as a
reading choice in its notes §6.

## 4. ERCOT §6.5.7.11: the clause both raters read as history-shaped (exploratory)

| | Rater A (A109, A110) | Rater B (B104, B105) |
|---|---|---|
| Quantity, point | ramp rate, `facility` | ramp rate, `facility` |
| Limit (as printed) | down: at least 10 % and no greater than 20 % per minute; up: ≤ 20 % per minute | the same, "of the difference between its MPC and its LPC" |
| Window | `1 – 60 s`: "eligible one-minute intervals (6.5.7.11(4))" | `1 – 60 s`: "one-minute intervals, average ramp rate (paragraph (4))" |
| Allowance | `very loose`: ≥ 90 % of eligible one-minute intervals in the month | the same |
| Binding | `mandatory` (confidence medium) | `mandatory` |

*SOURCED (ERCOT Nodal Protocols §6.5.7.11, as quoted in both CSVs); classes DERIVED-judgemental.*

**Caveats, all from the raters' own notes, none weighed in any verdict:**
1. **Not yet implemented.** The section was approved through NPRR1325 but is printed gray-boxed, to take effect "upon
   system implementation of PGRR145". Both raters read §1's test, adoption by the body, as met. Rater B notes that
   B104 / B105 drop out if not-yet-implemented text is read as pending.
2. **Scope.** The clause binds a Provisional Controllable Load Resource (PCLR), a registration category, not every
   large load. Neither rater assessed whether a data centre must register as one.
3. **The window sits at the class edge.** One minute is exactly 60 s, the inclusive upper bound of `1 – 60 s` (§2).
   One second more and the clause would be `1 – 15 min`, `reactive`. DC1's sensitivity used a per-sample (5 Hz) ramp
   test with a 0.5 % budget. A one-minute average ramp rate with 10 % of minutes allowed to fail is a much slacker
   constraint, so the "history" shape here is a match by class, not by mechanism.
4. **The metric.** Compliance counts intervals in which the PCLR's *telemetered* average ramp rate met the band
   (rater A, notes item 10).

## 5. Pre-registered readouts (reported although UNGATED)

**Binding deciding matched pairs (both raters binding and deciding):** 16, from 3 instruments.

| Instrument | Pairs | Quantity | Window (both raters) | Allowance | Computed shape |
|---|---|---|---|---|---|
| X02 Fingrid, large demand facilities, §9.1.13 Table 9.1 (power-oscillation bands) | 9 | swing amplitude, POI | 3 × `1 – 15 min`, 5 × `1 – 60 s`, 1 × `100 ms – 1 s` | `hard` | 8 reactive, 1 electronics |
| X02 §9.1.7, §9.1.8 d) | 3 | ramp rate; step change; smoothing response | `1 – 60 s`; `not stated`; `1 – 15 min` | `hard` | reactive; cannot judge; reactive |
| G02 ERCOT Protocols §6.5.7.11(1), (2) | 2 | ramp rate, facility | `1 – 60 s` | `very loose` | **history** |
| X01 AESO data-centre connection guide §7.2, §7.4 | 2 | ramp rate; step change, POI | `1 – 60 s`; `not stated` | `hard` | reactive; cannot judge |

- The two raters agree on window and allowance class for all 16 pairs.
- 14 of the 16 come from the DC2-1 additions (X01, X02). **SEED** (seeds only) keeps 2 pairs, both ERCOT §6.5.7.11.
- Either-rater history rows, matched or unmatched: 4, all of them the ERCOT clause (A109, A110, B104, B105).

**Fastest binding deciding window per body:** Fingrid `100 ms – 1 s`; ERCOT `1 – 60 s`; AESO `1 – 60 s` (both raters
alike). Under ANY, the OCP rack specifications add `≤ 100 ms`.

**Sensitivities.** Each is UNGATED, because the gate is computed once.

| Run | Binding deciding pairs | Instruments | Conservative shapes |
|---|---|---|---|
| primary | 16 | 3 | reactive 11, history 2, cannot judge 2, electronics 1 |
| STATED (`unit:` windows → `not stated`) | 16 | 3 | reactive 9, cannot judge 4, history 2, electronics 1 |
| ANY (binding / deciding by either rater) | 20 | 5 | reactive 11, electronics 4, cannot judge 3, history 2 |
| SEED (additions out) | 2 | 1 | history 2 |

**Each rater's own binding deciding rows.**

| | Rows | Binding deciding | From instruments | Computed shapes |
|---|---|---|---|---|
| A | 204 | 16 | 3 | reactive 11, history 2, cannot judge 2, electronics 1 |
| B | 166 | 31 | 10 | reactive 12, cannot judge 12, electronics 5, history 2 |

**Vendor-capability rows.** Rater B wrote 5 rows from the NVIDIA GB300 power-smoothing page (V11): 2 ramp rate and 1
swing amplitude at `1 – 60 s`, and 2 smoothing response (`≤ 100 ms`, `1 – 60 s`), all at `device`. Rater A recorded
the NVIDIA documents (V11–V13) as naming configurable parameters without printing values, so it wrote no rows. Not
binding on anyone, by definition.

**Non-deciding (power-quality) pairs:** 102.
- **By quantity:** ride-through 38, flicker 26, other 12, rapid voltage change 8, hold-up 7, harmonics 6, power
  factor 5.
- **Most common window / allowance (rater A's classes):**

  | Window / allowance | Pairs |
  |---|---|
  | `1 – 60 s` / `hard` | 24 |
  | `not stated` / `hard` | 17 |
  | `≤ 100 ms` / `hard` | 12 |
  | `100 ms – 1 s` / `hard` | 9 |
  | `1 – 15 min` / `hard` | 8 |
  | `1 – 15 min` / `not stated` | 7 |
  | `> 15 min` / `not stated` | 7 |
  | `1 – 15 min` / `loose` | 6 |

  The 6 `loose` pairs are the D-A-CH-CZ flicker limits (Pst and Plt, E09–E11), assessed as 95 % values over a week.

**Access and status.**

| | Both raters |
|---|---|
| Access, seeds | full / full 40; partial / partial 10; none 0 |
| Access, by group | G 16 full; U 2 full, 1 partial (U02); E 8 full, 3 partial (E05–E07); Q 9 partial (Q01–Q09); V 14 full; X 3 full |
| Status | in force 28, no requirement 20, pending 8, identical counts for both raters |
| Status differences | E08 (A in force, B no requirement); V11 (B in force, A no requirement) |
| Pending (both) | G07–G09 (NERC CLO drafts), G11 (PJM draft), G15 (PUCT proposed rule), E03 (ACER draft), E06 (VDE draft), X03 (IESO, "proposed") |

## 6. Exploratory readings (not pre-registered; none deciding)

1. **Agreement on deciding rows only.** Restricted to rows that either rater marked deciding, identification is
   25 / (25 + 0 + 16) = **0.61**; on non-deciding rows it is 102 / (102 + 77 + 23) = 0.50. The deciding set fails the
   0.80 bar too. Most of its gap is two reading choices, both recorded in the raters' notes but made while reading,
   not in the conventions committed beforehand:
   - B recorded the D-A-CH-CZ step-change planning levels and the OCP envelopes as step changes;
   - A recorded the envelopes as `other` and wrote no rows for the D-A-CH-CZ step tables.
2. **No candidate other than ERCOT.** Of either rater's 204 + 166 rows, no binding deciding row other than ERCOT
   §6.5.7.11 has computed shape `history`. Under ANY, the 4 extra pairs are OCP envelopes: 3 rows of V06 Table 5 at
   `≤ 100 ms` (electronics), and V05 §4.3.1.1 (A `not stated`, B `≤ 100 ms`; cannot judge). B's 12 `cannot judge`
   rows all have window `not stated`.
3. **What a pass would have needed.** A one-row-per-table convention fixed in the pre-registration, for harmonics,
   ride-through curves and planning-level tables, would have removed most of the 116 unmatched rows. That is a lesson
   for the next documentary audit, not a re-analysis of this one.

## 7. Deviations

None after reading (no DC2-3). Disclosed above:
- the `verdict_line` display artefact (§1);
- the raters' reading-time judgement calls, recorded in their notes (A §7, B §6), each applied consistently after it
  was made.

## 8. What this does and does not say

- It does **not** say that no binding spec is history-shaped. The gate failed, so the pre-registered reading is no
  reading.
- It does **not** say that a history-shaped spec exists. The only candidate is one ERCOT clause, read identically by
  both raters. It is gray-boxed, applies to a registration category, sits on the window-class boundary, and is a much
  slacker constraint than DC1's sensitivity.
- It does say that, in 56 instruments read twice, the binding limits on a large load's real-power variation that
  either rater found are, apart from that clause, `hard` limits:
  - at the POI or facility: on ramp rate, oscillation amplitude and step size (Fingrid, AESO, ERCOT);
  - at the rack, shelf or PSU: on supply envelopes (OCP). Only rater B counted these as deciding.
- Everything above rests on documents read by language-model raters (D-3). No number here is MEASURED.

---

## Appendix. Every requirement, both raters

*SOURCED rows; classes DERIVED-judgemental; generated from `dc2.json`.*

### A.1 Matched pairs (127)

Where the raters differ, a cell reads `A / B`. Shape is computed from the window and allowance classes (§2). Limits as printed are in `dc2.json` and the two CSVs.

| pass | A | B | instrument | clause | category | quantity | point | window | allowance | binding | deciding | shape |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A001 | B035 | V05 | 4.3 Table 2 | Battery backup time | hold-up | shelf or PSU | 1–15min / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A002 | B034 | V05 | 4.3 Table 2 | Transient load response | other | shelf or PSU | n/s | hard | mandatory | no | cannot judge |
| 1 | A003 | B036 | V05 | 4.3.1.1 | Repetitive Peak Load | other / step change | shelf or PSU | n/s / ≤100ms | hard | mandatory | no / yes | cannot judge / electronics |
| 1 | A004 | B038 | V05 | 4.5 |  | hold-up | shelf or PSU | ≤100ms / n/s | hard | mandatory | no | electronics / cannot judge |
| 1 | A005 | B152 | X02 | 9.1.1 |  | ride-through / other | POI | 1–60s | hard | mandatory | no | reactive |
| 1 | A006 | B153 | X02 | 9.1.3 |  | ride-through | POI | 1–60s / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A011 | B156 | X02 | 9.1.10 | peräkkäiset jännitehäiriöt | ride-through | POI | 1–15min / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A012 | B157 | X02 | 9.1.11 |  | ride-through | POI | 1–60s / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A013 | B140 | X02 | 9.1.13 Taulukko 9.1 | 0,01–0,025 Hz | swing amplitude | POI | 1–15min | hard | mandatory | yes | reactive |
| 1 | A014 | B141 | X02 | 9.1.13 Taulukko 9.1 | 0,025–0,05 Hz | swing amplitude | POI | 1–15min | hard | mandatory | yes | reactive |
| 1 | A015 | B142 | X02 | 9.1.13 Taulukko 9.1 | 0,05–0,1 Hz | swing amplitude | POI | 1–15min | hard | mandatory | yes | reactive |
| 1 | A016 | B143 | X02 | 9.1.13 Taulukko 9.1 | 0,1–0,2 Hz | swing amplitude | POI | 1–60s | hard | mandatory | yes | reactive |
| 1 | A017 | B144 | X02 | 9.1.13 Taulukko 9.1 | 0,2–0,5 Hz | swing amplitude | POI | 1–60s | hard | mandatory | yes | reactive |
| 1 | A018 | B145 | X02 | 9.1.13 Taulukko 9.1 | 0,5–2,0 Hz | swing amplitude | POI | 1–60s | hard | mandatory | yes | reactive |
| 1 | A019 | B146 | X02 | 9.1.13 Taulukko 9.1 | 2,0–6,0 Hz | swing amplitude | POI | 1–60s | hard | mandatory | yes | reactive |
| 1 | A020 | B147 | X02 | 9.1.13 Taulukko 9.1 | 6,0–18,0 Hz | swing amplitude | POI | 1–60s | hard | mandatory | yes | reactive |
| 1 | A021 | B148 | X02 | 9.1.13 Taulukko 9.1 | 18,0–45,0 Hz | swing amplitude | POI | 0.1–1s | hard | mandatory | yes | electronics |
| 1 | A022 | B108 | V04 | 5.1 | Battery backup time | hold-up | shelf or PSU | 1–15min / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A023 | B106 | V04 | 5.1 | Transient load response | other | shelf or PSU | n/s | hard | mandatory | no | cannot judge |
| 1 | A025 | B015 | V09 | 4.4.3 Table 1 | 1.10 < V ≤ 1.20 | ride-through | POI | 1–60s / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A026 | B016 | V09 | 4.4.3 Table 1 | 0.80 ≤ V < 0.90 | ride-through | POI | 1–60s / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A027 | B017 | V09 | 4.4.3 Table 1 | 0.50 ≤ V < 0.80 | ride-through | POI | 0.1–1s / n/s | hard | mandatory | no | electronics / cannot judge |
| 1 | A028 | B018 | V09 | 4.4.3 Table 1 | 0.35 ≤ V < 0.50 | ride-through | POI | 0.1–1s / n/s | hard | mandatory | no | electronics / cannot judge |
| 1 | A029 | B019 | V09 | 4.4.3 Table 1 | V < 0.35 | ride-through | POI | 0.1–1s / n/s | hard | mandatory | no | electronics / cannot judge |
| 1 | A030 | B020 | G03 | 2.6.4(3) Table A | 61.2 < f ≤ 63.0 | ride-through | POI | 1–15min / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A031 | B021 | G03 | 2.6.4(3) Table A | 57.5 ≤ f < 58.8 | ride-through | POI | 1–15min / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A032 | B022 | G03 | 2.6.4(5) |  | ride-through | POI | n/s | hard | recommendation | no | cannot judge |
| 1 | A033 | B023 | G03 | 2.6.4(6) |  | ride-through | POI | 1–60s / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A034 | B024 | G03 | 2.15(3) Table A | 1.10 < V ≤ 1.20 | ride-through | POI | 1–60s / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A035 | B025 | G03 | 2.15(3) Table A | 0.80 ≤ V < 0.90 | ride-through | POI | 1–60s / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A036 | B026 | G03 | 2.15(3) Table A | 0.50 ≤ V < 0.80 | ride-through | POI | 0.1–1s / n/s | hard | mandatory | no | electronics / cannot judge |
| 1 | A037 | B027 | G03 | 2.15(3) Table A | 0.35 ≤ V < 0.50 | ride-through | POI | 0.1–1s / n/s | hard | mandatory | no | electronics / cannot judge |
| 1 | A038 | B028 | G03 | 2.15(3) Table A | V < 0.35 | ride-through | POI | 0.1–1s / n/s | hard | mandatory | no | electronics / cannot judge |
| 1 | A039 | B029 | G03 | 2.15(3)(b) |  | ride-through | POI | 1–60s / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A040 | B030 | G03 | 2.15(3)(c) |  | ride-through | POI | 1–60s / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A041 | B031 | G03 | 2.15(3)(d) |  | other | POI | 0.1–1s / n/s | hard | mandatory | no | electronics / cannot judge |
| 1 | A042 | B032 | G03 | 2.15(3)(e) |  | ride-through | POI | 0.1–1s / n/s | hard | mandatory | no | electronics / cannot judge |
| 1 | A043 | B033 | G03 | 2.15(7) |  | ride-through | POI | 1–15min / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A050 | B057 | E11 | 1.1.2 |  | rapid voltage change | POI | n/s | hard | planning level | no | cannot judge |
| 1 | A051 | B058 | E11 | 1.2.1 | LPst HS | flicker | POI | 1–15min | not stated / hard | planning level | no | reactive |
| 1 | A052 | B059 | E11 | 1.2.1 | LPlt HS | flicker | POI | >15min | not stated / hard | planning level | no | reactive |
| 1 | A053 | B060 | E11 | 1.2.1 | LPst HöS | flicker | POI | 1–15min | not stated / hard | planning level | no | reactive |
| 1 | A054 | B061 | E11 | 1.2.1 | LPlt HöS | flicker | POI | >15min | not stated / hard | planning level | no | reactive |
| 1 | A055 | B062 | E11 | 1.2.1 | Pst HS ges | flicker | POI | 1–15min | loose | planning level | no | reactive |
| 1 | A056 | B063 | E11 | 1.2.1 | Plt HS ges | flicker | POI | >15min | loose | planning level | no | reactive |
| 1 | A081 | B097 | V08 | 3.13 Table 3 | 50% step load (10% min. load) | other | shelf or PSU | ≤100ms | hard | mandatory | no | electronics |
| 1 | A082 | B098 | V08 | 3.13 Table 3 | 90% step load (10% min. load) | other | shelf or PSU | ≤100ms | hard | mandatory | no | electronics |
| 1 | A083 | B099 | V08 | 3.13 Table 3 | 140% step load (10% min. load) | other | shelf or PSU | ≤100ms | hard | mandatory | no | electronics |
| 1 | A084 | B100 | V08 | 3.15 |  | hold-up | shelf or PSU | ≤100ms / n/s | hard | mandatory | no | electronics / cannot judge |
| 1 | A085 | B101 | V08 | 3.17 | ≤140%, ≤50ms moving average | other / step change | shelf or PSU | ≤100ms | hard | recommendation | no / yes | electronics |
| 1 | A086 | B102 | V08 | 3.17 | ≤160%, 400us moving average | other / step change | shelf or PSU | ≤100ms | hard | recommendation | no / yes | electronics |
| 1 | A087 | B103 | V08 | 3.17 | ≤100%, ≥1s moving average | other | shelf or PSU | 1–60s | hard | recommendation | no | reactive |
| 1 | A088 | B158 | E04 | CC.6.1.7 Table CC.6.1.7(a) | 1 Frequent events | rapid voltage change | POI | ≤100ms | hard | mandatory | no | electronics |
| 1 | A089 | B159 | E04 | CC.6.1.7 Table CC.6.1.7(a) | 2 Infrequent events | rapid voltage change | POI | ≤100ms | event count | mandatory | no | electronics |
| 1 | A090 | B160 | E04 | CC.6.1.7 Table CC.6.1.7(a) | 3 Very infrequent events | rapid voltage change | POI | ≤100ms | event count | mandatory | no | electronics |
| 1 | A091 | B161 | E04 | CC.6.1.7(j) Table CC.6.1.7(b) | 3.3 kV, 6.6 kV, 11 kV, 20 kV, 33 kV / Ps | flicker | POI | 1–15min | not stated | planning level | no | reactive |
| 1 | A092 | B162 | E04 | CC.6.1.7(j) Table CC.6.1.7(b) | 3.3 kV, 6.6 kV, 11 kV, 20 kV, 33 kV / Pl | flicker | POI | >15min | not stated | planning level | no | reactive |
| 1 | A093 | B163 | E04 | CC.6.1.7(j) Table CC.6.1.7(b) | 66 kV, 110 kV, 132 kV, 150 kV, 200 kV, 2 | flicker | POI | 1–15min | not stated | planning level | no | reactive |
| 1 | A094 | B164 | E04 | CC.6.1.7(j) Table CC.6.1.7(b) | 66 kV, 110 kV, 132 kV, 150 kV, 200 kV, 2 | flicker | POI | >15min | not stated | planning level | no | reactive |
| 1 | A095 | B001 | V06 | 7.1.2 Table 3 | PF load <20% | power factor | shelf or PSU | n/s | hard | mandatory | no | cannot judge |
| 1 | A096 | B002 | V06 | 7.1.2 Table 3 | PF load ≥20% | power factor | shelf or PSU | n/s | hard | mandatory | no | cannot judge |
| 1 | A097 | B003 | V06 | 7.1.2 Table 3 | THD 5%< load <15% | harmonics | shelf or PSU | n/s | hard | mandatory | no | cannot judge |
| 1 | A098 | B004 | V06 | 7.1.2 Table 3 | THD 15% ≤ load <30% | harmonics | shelf or PSU | n/s | hard | mandatory | no | cannot judge |
| 1 | A099 | B005 | V06 | 7.1.2 Table 3 | THD load ≥30% | harmonics | shelf or PSU | n/s | hard | mandatory | no | cannot judge |
| 1 | A100 | B006 | V06 | 7.1.3.1 |  | hold-up | shelf or PSU | ≤100ms / n/s | hard | mandatory | no | electronics / cannot judge |
| 1 | A101 | B007 | V06 | 7.2.1.1 |  | hold-up | shelf or PSU / rack or row | 1–60s / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A102 | B008 | V06 | 7.3.2 Table 5 | <2 msec load step | other / step change | shelf or PSU / rack or row | ≤100ms | hard | mandatory | no / yes | electronics |
| 1 | A103 | B009 | V06 | 7.3.2 Table 5 | <0.5 msec load step | other / step change | shelf or PSU / rack or row | ≤100ms | hard | mandatory | no / yes | electronics |
| 1 | A104 | B010 | V06 | 7.3.2 Table 5 | <50 msec load step | other / step change | shelf or PSU / rack or row | ≤100ms | hard | mandatory | no / yes | electronics |
| 1 | A105 | B011 | V06 | 7.3.2 Table 5 | 1 sec moving average | other | shelf or PSU / rack or row | 1–60s | hard | mandatory | no | reactive |
| 1 | A106 | B012 | V06 | 7.3.3 Table 6 | 50% step load (10% min. load) | other | shelf or PSU | ≤100ms | hard | mandatory | no | electronics |
| 1 | A107 | B013 | V06 | 7.3.3 Table 6 | 90% step load (10% min. load) | other | shelf or PSU | ≤100ms | hard | mandatory | no | electronics |
| 1 | A108 | B014 | V06 | 7.3.3 Table 6 | 140% step load (10% min. load) | other | shelf or PSU | ≤100ms | hard | mandatory | no | electronics |
| 1 | A109 | B104 | G02 | 6.5.7.11(1) | down ramp rate | ramp rate | facility | 1–60s | very loose | mandatory | yes | history |
| 1 | A110 | B105 | G02 | 6.5.7.11(2) | up ramp rate | ramp rate | facility | 1–60s | very loose | mandatory | yes | history |
| 1 | A111 | B072 | E10 | 1.1.2 | häufige Ereignisse (r ≥ 0,01 min-1) | rapid voltage change | POI | n/s | hard | planning level | no | cannot judge |
| 1 | A112 | B073 | E10 | 1.1.2 | seltene Spannungsänderungen (r < 0,01 mi | rapid voltage change | POI | n/s | hard | planning level | no | cannot judge |
| 1 | A113 | B074 | E10 | 1.2.1 | LPst MS | flicker | POI | 1–15min | not stated / hard | planning level | no | reactive |
| 1 | A114 | B075 | E10 | 1.2.1 | LPlt MS | flicker | POI | >15min | not stated / hard | planning level | no | reactive |
| 1 | A115 | B076 | E10 | 1.2.1 | LPst HS | flicker | POI | 1–15min | not stated / hard | planning level | no | reactive |
| 1 | A116 | B077 | E10 | 1.2.1 | LPlt HS | flicker | POI | >15min | not stated / hard | planning level | no | reactive |
| 1 | A117 | B078 | E10 | 1.2.1 | Pst MS ges | flicker | POI | 1–15min | loose | planning level | no | reactive |
| 1 | A118 | B079 | E10 | 1.2.1 | Plt MS ges | flicker | POI | >15min | loose | planning level | no | reactive |
| 1 | A165 | B054 | E01 | Art. 15(1)(a) |  | power factor | POI | n/s | hard | mandatory | no | cannot judge |
| 1 | A166 | B095 | V03 | 5.5.1 |  | hold-up | shelf or PSU | ≤100ms / n/s | hard | mandatory | no | electronics / cannot judge |
| 1 | A167 | B092 | V03 | 5.6 | ≤140%, ≤50ms moving average | other / step change | shelf or PSU | ≤100ms | hard | recommendation | no / yes | electronics |
| 1 | A168 | B093 | V03 | 5.6 | ≤160%, ≤400us moving average | other / step change | shelf or PSU | ≤100ms | hard | recommendation | no / yes | electronics |
| 1 | A169 | B094 | V03 | 5.6 | ≤100%, ≥1s moving average | other | shelf or PSU | 1–60s | hard | recommendation | no | reactive |
| 1 | A170 | B096 | V07 | 4.5 | ≤140%, ≤50ms moving average | other / step change | shelf or PSU | ≤100ms | hard | recommendation | no / yes | electronics |
| 1 | A171 | B121 | X01 | 7.2 Requirements 2 |  | ramp rate | POI | 1–60s | hard | mandatory | yes | reactive |
| 1 | A172 | B122 | X01 | 7.4 Requirements 1 |  | step change | POI | n/s | hard | mandatory | yes | cannot judge |
| 1 | A173 | B123 | X01 | 5.3 Requirements 1 |  | power factor | POI | n/s | hard | mandatory | no | cannot judge |
| 1 | A174 | B124 | X01 | 6.1 Table 6-1 | 1.15 < V ≤ 1.25 | ride-through | POI | 1–60s | hard | mandatory | no | reactive |
| 1 | A175 | B125 | X01 | 6.1 Table 6-1 | 1.10 < V ≤ 1.15 | ride-through | POI | >15min | hard | mandatory | no | reactive |
| 1 | A176 | B126 | X01 | 6.1 Table 6-1 | 0.75 ≤ V < 0.9 | ride-through | POI | 1–60s | hard | mandatory | no | reactive |
| 1 | A177 | B127 | X01 | 6.1 Table 6-1 | 0.65 ≤ V < 0.75 | ride-through | POI | 1–60s | hard | mandatory | no | reactive |
| 1 | A178 | B128 | X01 | 6.1 Table 6-1 | 0.45 ≤ V < 0.65 | ride-through | POI | 1–60s | hard | mandatory | no | reactive |
| 1 | A179 | B129 | X01 | 6.1 Table 6-1 | V < 0.45 | ride-through | POI | 1–60s | hard | mandatory | no | reactive |
| 1 | A180 | B139 | X01 | 6.1 Requirements 18–19 |  | ride-through | POI | 1–60s / n/s | hard | recommendation | no | reactive / cannot judge |
| 1 | A181 | B130 | X01 | 6.1 Table 6-2 | V >1.7 | ride-through | POI | 1–60s | hard | mandatory | no | reactive |
| 1 | A182 | B131 | X01 | 6.1 Table 6-2 | V >1.6 | ride-through | POI | 1–60s | hard | mandatory | no | reactive |
| 1 | A183 | B132 | X01 | 6.1 Table 6-2 | V >1.4 | ride-through | POI | 1–60s | hard | mandatory | no | reactive |
| 1 | A184 | B133 | X01 | 6.1 Table 6-2 | V >1.25 | ride-through | POI | 1–60s | hard | mandatory | no | reactive |
| 1 | A185 | B134 | X01 | 6.1 Table 6-3 | 61.2 < F ≤ 61.8 | ride-through | POI | 1–15min / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A186 | B135 | X01 | 6.1 Table 6-3 | 57 ≤ F < 58.8 | ride-through | POI | 1–15min / n/s | hard | mandatory | no | reactive / cannot judge |
| 1 | A187 | B136 | X01 | 6.1 Requirements 25–26 |  | ride-through / other | POI | 0.1–1s | hard | mandatory | no | electronics |
| 1 | A188 | B137 | X01 | 6.1 Requirements 28 |  | ride-through / other | POI | ≤100ms / n/s | hard | mandatory | no | electronics / cannot judge |
| 1 | A191 | B109 | E09 | 1.1.2 | häufige Ereignisse (r ≥ 0,01 min-1) | rapid voltage change | POI | n/s | hard | planning level | no | cannot judge |
| 1 | A192 | B110 | E09 | 1.1.2 | seltene Spannungsänderungen (r < 0,01 mi | rapid voltage change | POI | n/s | hard | planning level | no | cannot judge |
| 1 | A193 | B111 | E09 | 1.2.1 | LPst MS | flicker | POI | 1–15min | not stated / hard | planning level | no | reactive |
| 1 | A194 | B112 | E09 | 1.2.1 | LPlt MS | flicker | POI | >15min | not stated / hard | planning level | no | reactive |
| 1 | A195 | B113 | E09 | 1.2.1 | Pst NS ges | flicker | POI | 1–15min | loose | planning level | no | reactive |
| 1 | A196 | B114 | E09 | 1.2.1 | Plt NS ges | flicker | POI | >15min | loose | planning level | no | reactive |
| 2 | A007 | B149 | X02 | 9.1.7 | pätötehon suurin muutosnopeus | ramp rate | POI | 1–60s | hard | mandatory | yes | reactive |
| 2 | A008 | B150 | X02 | 9.1.7 | yksittäinen askelmainen tehonmuutos | step change | POI | n/s | hard | mandatory | yes | cannot judge |
| 2 | A009 | B151 | X02 | 9.1.8 d) |  | smoothing or capping response | POI | 1–15min | hard | mandatory | yes | reactive |
| 2 | A049 | B166 | U03 | A. General Rules, rule 16 |  | power factor | device | n/s | hard | mandatory | no | cannot judge |
| 2 | A057 | B064 | E11 | 1.2.2 (1-4) | Pst HS V | flicker | POI | 1–15min | loose | planning level | no | reactive |
| 2 | A058 | B065 | E11 | 1.2.2 (1-5) | Plt HS V | flicker | POI | >15min | loose | planning level | no | reactive |
| 2 | A064 | B070 | E11 | 3.1.1 Tab. 3-1 | ν = 5 | harmonics | POI | n/s | not stated / hard | planning level | no | cannot judge |
| 2 | A065 | B071 | E11 | 3.1.1 Tab. 3-1 | ν = 7 | harmonics | POI | n/s | not stated / hard | planning level | no | cannot judge |
| 2 | A119 | B080 | E10 | 1.2.2 (1-9) | Pst MS V | flicker | POI | 1–15min | loose | planning level | no | reactive |
| 2 | A120 | B081 | E10 | 1.2.2 (1-10) | Plt MS V | flicker | POI | >15min | loose | planning level | no | reactive |
| 2 | A126 | B086 | E10 | 3.1.1 Tab. 3-1 | ν = 5 | harmonics | POI | n/s | not stated / hard | planning level | no | cannot judge |
| 2 | A162 | B039 | E01 | Art. 13(1) Annex II | 300–400 kV / Nordic / 1,05 pu-1,10 pu | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| 2 | A197 | B115 | E09 | 1.2.2 (1-5) | Pst NS V | flicker | POI | 1–15min | loose | planning level | no | reactive |
| 2 | A198 | B116 | E09 | 1.2.2 (1-6) | Plt NS V | flicker | POI | >15min | loose | planning level | no | reactive |

### A.2 Unmatched rows, rater A (77)

| req | instrument | clause | category | quantity | point | window | allowance | binding | deciding | shape |
|---|---|---|---|---|---|---|---|---|---|---|
| A010 | X02 | 9.1.10 | Kuva 9.2 / 9.3 | ride-through | POI | 1–60s | hard | mandatory | no | reactive |
| A024 | V04 | 5.1 | Startup time | hold-up | shelf or PSU | ≤100ms | hard | mandatory | no | electronics |
| A044 | E08 | 6.6 Tab. 6-6 | μ = 1, 2 | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A045 | E08 | 6.6 Tab. 6-6 | μ = 3 ...30 | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A046 | E08 | 6.6 Tab. 6-6 | μ = 31 ...39 | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A047 | E08 | 6.6 (6-14)/(6-15) | NS | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A048 | E08 | 6.6 (6-14)/(6-15) | MS, HS | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A059 | E11 | 2.1 |  | other | POI | n/s | not stated | planning level | no | cannot judge |
| A060 | E11 | 2.2 (2-1)/(2-3) |  | other | POI | 1–15min | loose | planning level | no | reactive |
| A061 | E11 | 3.1.2 (3-1) |  | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A062 | E11 | 3.2.2 (3-4) |  | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A063 | E11 | 3.3.2 (3-5) |  | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A066 | E11 | 3.1.1 Tab. 3-1 | ν = 11 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A067 | E11 | 3.1.1 Tab. 3-1 | ν = 13 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A068 | E11 | 3.1.1 Tab. 3-1 | 17 ≤ ν ≤ 37 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A069 | E11 | 3.1.1 Tab. 3-1 | ν = 3 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A070 | E11 | 3.1.1 Tab. 3-1 | ν = 9 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A071 | E11 | 3.1.1 Tab. 3-1 | ν = 15 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A072 | E11 | 3.1.1 Tab. 3-1 | ν = 21 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A073 | E11 | 3.1.1 Tab. 3-1 | 27 ≤ ν ≤ 39 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A074 | E11 | 3.1.1 Tab. 3-1 | ν = 2 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A075 | E11 | 3.1.1 Tab. 3-1 | ν = 4 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A076 | E11 | 3.1.1 Tab. 3-1 | ν = 6 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A077 | E11 | 3.1.1 Tab. 3-1 | ν = 8 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A078 | E11 | 3.1.1 Tab. 3-1 | 10 ≤ ν ≤ 40 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A079 | V08 | 3.7 1) | DC Inrush Current | other | shelf or PSU | n/s | hard | mandatory | no | cannot judge |
| A080 | V08 | 3.7 2) | Re-rush Current | other | shelf or PSU | ≤100ms | hard | mandatory | no | electronics |
| A121 | E10 | 2.1 |  | other | POI | n/s | not stated | planning level | no | cannot judge |
| A122 | E10 | 2.2 (2-1)/(2-2) |  | other | POI | 1–15min | loose | planning level | no | reactive |
| A123 | E10 | 3.1.2 (3-1) |  | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A124 | E10 | 3.2.2 (3-8) |  | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A125 | E10 | 3.3.2 (3-9) |  | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A127 | E10 | 3.1.1 Tab. 3-1 | ν = 7 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A128 | E10 | 3.1.1 Tab. 3-1 | ν = 11 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A129 | E10 | 3.1.1 Tab. 3-1 | ν = 13 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A130 | E10 | 3.1.1 Tab. 3-1 | 17 ≤ ν ≤ 37 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A131 | E10 | 3.1.1 Tab. 3-1 | ν = 3 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A132 | E10 | 3.1.1 Tab. 3-1 | ν = 9 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A133 | E10 | 3.1.1 Tab. 3-1 | ν = 15 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A134 | E10 | 3.1.1 Tab. 3-1 | ν = 21 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A135 | E10 | 3.1.1 Tab. 3-1 | 27 ≤ ν ≤ 39 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A136 | E10 | 3.1.1 Tab. 3-1 | ν = 2 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A137 | E10 | 3.1.1 Tab. 3-1 | ν = 4 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A138 | E10 | 3.1.1 Tab. 3-1 | ν = 6 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A139 | E10 | 3.1.1 Tab. 3-1 | ν = 8 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A140 | E10 | 3.1.1 Tab. 3-1 | 10 ≤ ν ≤ 40 | harmonics | POI | n/s | not stated | planning level | no | cannot judge |
| A141 | E01 | Art. 12(1) Annex I | Continental Europe / 47,5 Hz-48,5 Hz | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A142 | E01 | Art. 12(1) Annex I | Continental Europe / 48,5 Hz-49,0 Hz | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A143 | E01 | Art. 12(1) Annex I | Continental Europe / 51,0 Hz-51,5 Hz | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A144 | E01 | Art. 12(1) Annex I | Nordic / 47,5 Hz-48,5 Hz | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A145 | E01 | Art. 12(1) Annex I | Nordic / 48,5 Hz-49,0 Hz | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A146 | E01 | Art. 12(1) Annex I | Nordic / 51,0 Hz-51,5 Hz | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A147 | E01 | Art. 12(1) Annex I | Great Britain / 47,0 Hz-47,5 Hz | ride-through | POI | 1–60s | hard | mandatory | no | reactive |
| A148 | E01 | Art. 12(1) Annex I | Great Britain / 47,5 Hz-48,5 Hz | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A149 | E01 | Art. 12(1) Annex I | Great Britain / 48,5 Hz-49,0 Hz | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A150 | E01 | Art. 12(1) Annex I | Great Britain / 51,0 Hz-51,5 Hz | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A151 | E01 | Art. 12(1) Annex I | Great Britain / 51,5 Hz-52,0 Hz | ride-through | POI | 1–15min | hard | mandatory | no | reactive |
| A152 | E01 | Art. 12(1) Annex I | Ireland and Northern Ireland / 47,5 Hz-4 | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A153 | E01 | Art. 12(1) Annex I | Ireland and Northern Ireland / 48,5 Hz-4 | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A154 | E01 | Art. 12(1) Annex I | Ireland and Northern Ireland / 51,0 Hz-5 | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A155 | E01 | Art. 12(1) Annex I | Baltic / 47,5 Hz-48,5 Hz | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A156 | E01 | Art. 12(1) Annex I | Baltic / 48,5 Hz-49,0 Hz | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A157 | E01 | Art. 12(1) Annex I | Baltic / 51,0 Hz-51,5 Hz | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A158 | E01 | Art. 13(1) Annex II | 110–300 kV / Continental Europe / 1,118  | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A159 | E01 | Art. 13(1) Annex II | 110–300 kV / Nordic / 1,05 pu-1,10 pu | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A160 | E01 | Art. 13(1) Annex II | 110–300 kV / Baltic / 1,118 pu-1,15 pu | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A161 | E01 | Art. 13(1) Annex II | 300–400 kV / Continental Europe / 1,05 p | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A163 | E01 | Art. 13(1) Annex II | 300–400 kV / Great Britain / 1,05 pu-1,1 | ride-through | POI | 1–15min | hard | mandatory | no | reactive |
| A164 | E01 | Art. 13(1) Annex II | 300–400 kV / Baltic / 1,097 pu-1,15 pu | ride-through | POI | >15min | hard | mandatory | no | reactive |
| A189 | X01 | 6.1 Requirements 31 | 1.1 per unit | ride-through | POI | 1–60s | hard | mandatory | no | reactive |
| A190 | X01 | 6.1 Requirements 31 | 1.18 per unit | ride-through | POI | 1–60s | hard | mandatory | no | reactive |
| A199 | E09 | 2.2 (2-1) |  | other | POI | 1–15min | loose | planning level | no | reactive |
| A200 | E09 | 3.1.2 (3-1) |  | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A201 | E09 | 3.2.2 (3-7) |  | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A202 | E09 | 3.3.2 (3-9) |  | harmonics | POI | 1–15min | loose | planning level | no | reactive |
| A203 | E09 | 4.2 |  | other | POI | n/s | hard | planning level | no | cannot judge |
| A204 | E10 | 4.2 |  | other | POI | n/s | hard | planning level | no | cannot judge |

### A.3 Unmatched rows, rater B (39)

| req | instrument | clause | category | quantity | point | window | allowance | binding | deciding | shape |
|---|---|---|---|---|---|---|---|---|---|---|
| B037 | V05 | 4.3.1.1 Note 2 |  | other | shelf or PSU | n/s | hard | mandatory | no | cannot judge |
| B040 | E01 | Annex I (Art. 12(1)) | Nordic | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B041 | E01 | Annex I (Art. 12(1)) | Great Britain | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B042 | E01 | Annex I (Art. 12(1)) | Ireland and Northern Ireland | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B043 | E01 | Annex I (Art. 12(1)) | Baltic | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B044 | E01 | Annex II table 1 (110 kV to <300 kV) | Continental Europe | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B045 | E01 | Annex II table 1 (110 kV to <300 kV) | Nordic | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B046 | E01 | Annex II table 1 (110 kV to <300 kV) | Great Britain | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B047 | E01 | Annex II table 1 (110 kV to <300 kV) | Ireland and Northern Ireland | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B048 | E01 | Annex II table 1 (110 kV to <300 kV) | Baltic | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B049 | E01 | Annex II table 2 (300-400 kV) | Continental Europe | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B050 | E01 | Annex II table 2 (300-400 kV) | Nordic | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B051 | E01 | Annex II table 2 (300-400 kV) | Great Britain | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B052 | E01 | Annex II table 2 (300-400 kV) | Ireland and Northern Ireland | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B053 | E01 | Annex II table 2 (300-400 kV) | Baltic | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B055 | E01 | Art. 19(1)(c)(ii) |  | other | POI | n/s | hard | mandatory | no | cannot judge |
| B056 | E01 | Art. 30(2)(c) |  | smoothing or capping response | not stated | 1–60s | hard | mandatory | yes | reactive |
| B066 | E11 | 1.4 | Einzelwert Pst | flicker | POI | 1–15min | hard | planning level | no | reactive |
| B067 | E11 | 1.3 Tab. 1-2 | r > 500 | step change | POI | n/s | hard | planning level | yes | cannot judge |
| B068 | E11 | 1.3 Tab. 1-2 | 10 ≤ r ≤ 500 | step change | POI | n/s | hard | planning level | yes | cannot judge |
| B069 | E11 | 1.3 Tab. 1-2 | r < 10 | step change | POI | n/s | hard | planning level | yes | cannot judge |
| B082 | E10 | 1.3.5 | Einzelwert Pst | flicker | POI | 1–15min | hard | planning level | no | reactive |
| B083 | E10 | 1.3.2 Tab. 1-2 | r > 500 | step change | POI | n/s | hard | planning level | yes | cannot judge |
| B084 | E10 | 1.3.2 Tab. 1-2 | 10 ≤ r ≤ 500 | step change | POI | n/s | hard | planning level | yes | cannot judge |
| B085 | E10 | 1.3.2 Tab. 1-2 | r < 10 | step change | POI | n/s | hard | planning level | yes | cannot judge |
| B087 | V11 | Table 1 | Ramp-up rate | ramp rate | device | 1–60s | hard | vendor capability | yes | reactive |
| B088 | V11 | Table 1 | Ramp-down rate | ramp rate | device | 1–60s | hard | vendor capability | yes | reactive |
| B089 | V11 | Table 1 | GPU-Idle floor power | swing amplitude | device | 1–60s | hard | vendor capability | yes | reactive |
| B090 | V11 | Table 1 | GPU-Idle-to-burn time | smoothing or capping response | device | ≤100ms | hard | vendor capability | yes | electronics |
| B091 | V11 | Table 1 | Idle time before ramp-down | smoothing or capping response | device | 1–60s | hard | vendor capability | yes | reactive |
| B107 | V04 | 5.1 | Output power | step change | shelf or PSU | n/s | hard | mandatory | yes | cannot judge |
| B117 | E09 | 1.3.6 | Einzelwert Pst | flicker | POI | 1–15min | hard | planning level | no | reactive |
| B118 | E09 | 1.3.2 Tab. 1-3 | r > 500 | step change | POI | n/s | hard | planning level | yes | cannot judge |
| B119 | E09 | 1.3.2 Tab. 1-3 | 10 ≤ r ≤ 500 | step change | POI | n/s | hard | planning level | yes | cannot judge |
| B120 | E09 | 1.3.2 Tab. 1-3 | r < 10 | step change | POI | n/s | hard | planning level | yes | cannot judge |
| B138 | X01 | 6.1 Requirements 31 |  | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B154 | X02 | 9.1.10 Kuva 9.2 |  | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B155 | X02 | 9.1.10 Kuva 9.3 |  | ride-through | POI | n/s | hard | mandatory | no | cannot judge |
| B165 | E04 | ECC.6.4.5.1 |  | power factor | POI | n/s | hard | mandatory | no | cannot judge |
