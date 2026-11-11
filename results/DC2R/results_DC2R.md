# DC2-R results: the ramp-spec audit re-rated with row granularity fixed in advance

**Verdict (pre-registered): UNGATED** — identification 0.716 < 0.80 (M 83 of n_A 99 / n_B 100). κ(window, M₁) 1.00
over 45 pass-1 pairs passes. Not access-limited (1 of 50 seeds unread by both raters).

**Consequence (pre-registered, DC2 §6 and DC2-R §4): no reading. DC1b is not run, and the data-centre anticipation leg
closes on DC2-R.**

**The gate failed for a different reason than DC2's.** The granularity fix worked where it was aimed. On the rows
that decide, identification is 26 / 32 = 0.81, and the raters agree on every class of all 23 binding deciding pairs.
What failed is coverage. Each rater rated clauses or topics the other did not, and on four clauses the raters named
the quantity differently (§3).

**Exploratory, not a verdict.** As in DC2, the one binding deciding clause with a history shape is ERCOT Protocols
§6.5.7.11 (G02, PCLR down- and up-ramp rates). Both raters recorded it with identical classes: facility, 1–60 s,
very loose, mandatory, *awaiting implementation* (DC2R-4), confidence medium. Every other binding deciding pair is
`hard`.

**Tags.** Every requirement is **SOURCED** (the raters' URLs and quotes are in their files). Every class is
**DERIVED-judgemental**. Both raters are language-model sessions, so κ measures how reproducible the reading is, not
whether it is independent of a shared model prior (D-3). No number here is MEASURED. No dollar figures.

Pre-registration: [`DC2R_preregistration.md`](DC2R_preregistration.md) (`47ae9f6`; DC2R-1 … DC2R-4; DC2R-D1 at
`64dbfe8`). It carries [`../DC2/DC2_preregistration.md`](../DC2/DC2_preregistration.md) (`60f7595`; DC2-1, DC2-2) by
reference. Analysis: [`../../analysis/DC2R_agreement.py`](../../analysis/DC2R_agreement.py) (`9d4a08d`), output
[`dc2r.json`](dc2r.json).

---

## 1. Gates

| Gate | Value | Pass |
|---|---|---|
| Identification M / (n_A + n_B − M) | 83 / (99 + 100 − 83) = **0.716** | **no** (≥ 0.80) |
| κ(window class) over M₁ | **1.000** (45 pairs, observed 1.000) | yes (≥ 0.60) |
| M₁ ≥ 10 | 45 | yes |

M = 83 = 45 (pass 1) + 38 (pass 2). Unmatched: A 16, B 17.

**Also reported:**

| Measure | Value |
|---|---|
| κ(window), all M | 1.000 (83; pass-2 pairs agree by construction) |
| κ(allowance), M₁ | **0.000**, observed agreement 0.867 (45). This is a degenerate κ: rater B wrote `hard` on all 45 pairs, so expected agreement equals observed. The 6 disagreements are D-A-CH-CZ flicker rows (E09, E10, E11 × 2), where A wrote `loose` and B `hard`. |
| κ(computed shape), M₁ | 1.000 (45) |
| κ(binding class), all M | 0.957 (observed 0.976). Disagreements: E04 RVC planning table (A planning level, B mandatory); X01 7.2 ramp (A recommendation, B mandatory). |
| κ(deciding), all M | 1.000 |
| Field disagreements over M | window 0, allowance 6, binding 2, quantity 0, measurement point 2 (V06 Table 5, V04), deciding 0, computed shape 0 |
| Rater-written vs computed shape | 0 mismatches |

**Rules file check.** `DC2R_rater_rules.md` is byte-identical (`cmp`) to the text of §1–§2 of the pre-registration,
on `main` and on both rater branches. Each rater's launch prompt equals `DC2R_rater_prompt.md` with `{R}` and `{r}`
filled in.

## 2. Pre-registered readouts (primary: binding by both, deciding by both, conservative shape)

**23 binding deciding pairs from 6 instruments.** The raters agree on window and allowance class for all 23.

| Instrument | Pairs | Quantity | Point | Window | Allowance | Conservative shape |
|---|---|---|---|---|---|---|
| X02 Fingrid large demand facilities, 9.1.13 Taulukko 9.1 | 9 | swing amplitude, one row per frequency band | POI | 1–15 min (3 bands, 0.01–0.1 Hz); 1–60 s (5 bands, 0.1–18 Hz); 100 ms–1 s (18–45 Hz) | hard | reactive 8, electronics 1 |
| X02 9.1.7 | 2 | step change (single step); ramp rate (third-party controls) | POI | not stated; 1–60 s | hard | cannot judge; reactive |
| E09, E10, E11 D-A-CH-CZ step tables (DC2R-3) | 9 (3 each) | step change, one row per printed row | POI | not stated | hard | cannot judge |
| X01 AESO data-centre guide 7.4 | 1 | step change | POI | not stated | hard | cannot judge |
| **G02 ERCOT Protocols §6.5.7.11(1), (2)** | **2** | ramp rate (down, up) | facility | **1–60 s** | **very loose** | **history** |

Totals by conservative shape: reactive 9, electronics 1, cannot judge 11, history 2.

**History-shaped pairs:**
- A079 / B060: §6.5.7.11(1), down ramp rate.
- A080 / B061: §6.5.7.11(2), up ramp rate.

Both raters printed the same window and allowance: eligible one-minute intervals (average ramp rate, telemetered),
with the requirement met when at least 90 % of a calendar month's eligible intervals comply. Both pairs matched in
pass 2 because B cited "(1), (4)" where A cited "(1)". They are the only binding deciding rows with a history shape in
either file (4 rows, 2 per rater). Measurement point: facility, so a POI or facility-level match only, which is weaker
against DC1's node and rack model.

**Fastest binding window per body** (binding deciding pairs, window stated):
- Fingrid: 100 ms – 1 s (both raters);
- ERCOT: 1 – 60 s (both raters);
- D-A-CH-CZ and AESO state no window.

**Sensitivities** (all UNGATED under the same gate):

| Variant | Binding deciding pairs | Shapes |
|---|---|---|
| STATED (rate-unit rule off) | 23 from 6 | one X02 9.1.7 ramp row turns to cannot judge |
| ANY (either rater binding or deciding) | 24 from 6 | adds X01 7.2 ramp (A recommendation, B mandatory) |
| SEED (no S3 or DC2-1 additions) | 11 from 4 | history 2, cannot judge 9 |

**Vendor-capability rows:** V12 (NVIDIA power smoothing), a ramp rate and a swing-amplitude setting, rated by both
raters as `vendor capability`, so not a requirement on anyone.

**DC2R-2 in effect.** The OCP supply envelopes (V04–V08) are `other` or `hold-up` in both files: non-deciding, and no
pair disagrees on `deciding`. In DC2, 9 such pairs had split the raters.

**DC2R-4 rows:** 4, all G02 §6.5.7.11, all confidence medium (0 above medium).

**DC2-2:**
- the only conversion is B040, the E04 RVC table, whose Cat 2/3 recurrence becomes `tight`; the row's class comes from
  its Cat 1 entry, `hard`;
- the script's text match on "DC2-2" lists 21 rows, but the others are notes that say DC2-2 does *not* apply.

**Rate-unit rule:** A 5 rows, B 3. **Response-time rule:** A 1, B 2 (the raters' notes).

## 3. Why identification failed: the 33 unmatched rows

Every unmatched row falls into one of three classes:

| Class | A | B | Rows |
|---|---|---|---|
| **Coverage:** a clause or topic rated by one rater only | 11 | 10 | **A:** voltage unbalance in D-A-CH-CZ E09–E11 (5: A095–A099; B's notes exclude unbalance); ERCOT Operating Guide ancillary-service CLR obligations (3: G03 2.3.x); GB Balancing Code BC1.A.1.1 ramp rows (2: E04, found outside CC / ECC); VDE FNN FAQ RVC row (1: E05). **B:** ERCOT Operating Guide ride-through clauses (4: G03 2.15(3), 2.6.4); GB DRSC demand-response clauses (2: E04); Fingrid 9.1.9 under-voltage fast limiting (1: X02); AESO 5.1 step requirement (1: X01); ERCOT Planning Guide 9.2.5(3) step (1: G01); D-A-CH-CZ supraharmonics table (1: E09) |
| **Quantity named differently on the same clause** (so neither pass can pair them) | 2 | 2 | OCP V03 5.5.1 (A `hold-up`, B `other`); Fingrid X02 9.1.8 fast active-power limiting (A `other`, B `smoothing or capping response`, which is deciding) |
| **A table holding two quantities** (DC2R-1 does not say whether a mixed table is one row or one per quantity) | 3 | 5 | OCP V04 5.1 and V05 4.3 Table 2 / 4.3.1 / 4.5: A wrote one `hold-up` or `other` row per clause; B split by quantity (transient load response `other`; battery backup time `hold-up`) |

**Exploratory, not pre-registered:**
- identification on deciding rows only is 26 / (26 + 2 + 4) = **0.81**;
- on non-deciding rows it is 57 / (57 + 14 + 13) = **0.68**.

In DC2 these were 0.61 and 0.50. The granularity fix lifted both. What remains is mostly which clauses of the large
documents a rater searched (ERCOT Operating Guide, GB Grid Code) and which non-deciding topics a rater chose to rate
(unbalance).

## 4. Access and status

| | full / full | partial / full | partial / partial | none / none |
|---|---|---|---|---|
| 50 seeds | 39 | 1 (U02) | 9 | 1 (E01) |

- **E01** (EU Regulation 2016/1388, the Demand Connection Code): every EUR-Lex route returned an AWS WAF bot challenge
  to both raters, who recorded `none` without circumventing it. 1 of 50 is below the threshold of 17, so the study is
  not access-limited.
- **Partial:** the Q group (IEC / IEEE / EN power-quality standards: abstracts and previews only), E05–E07 (VDE, paywalled).
- **Status:** in force 29, no requirement 19, pending 8 for each rater. The pending lists are identical: G07, G08, G09
  (NERC CLO drafts), G11 (PJM draft), G15 (PUCT proposed SLLIA), E03 (ACER DCC draft), E06 (VDE-AR-N 4120/A1 draft),
  X03 (IESO, printed as proposed).
- **Status disagreements:**
  - U02: A `in force`, B `no requirement`;
  - G01: A `no requirement`, B `in force` (B rated 9.2.5(3)).

## 5. Process

- **Order on `main`:**
  - pre-registration `47ae9f6`;
  - reviewer approval and DC2R-D1 `64dbfe8`;
  - analysis script, self-tests (s1–s5 unchanged, s6 for DC2R-D1) and rules file `9d4a08d`;
  - launch prompt, and its diff against DC2's prompt, `7b47601`;
  - then rater A's branch.

  Both rater branches descend from `7b47601`.
- **Rater A** (`dc2r-rater-a`, tip `06aaa90`):
  - clone from the public mirror with four files, all at `7b47601`;
  - conventions `ac9af82` (09:04) committed alone before any requirement text was read;
  - extraction 09:04–09:36.
- **Rater B** (`dc2r-rater-b`, tip `c4dc1e3`):
  - cloned from GitHub at 09:57, after `dc2r-rater-a` was pushed, as a single-branch clone of `main` with no
    `dc2r-rater-a` ref;
  - conventions `7fc0d0c` (09:58);
  - extraction 09:58–10:31.
- Neither rater used a web-search tool. Both used only the publishing bodies' own sites. Neither bypassed a bot check.
- **The raters' own disclosures** (their notes; recorded, not reconciled):
  - **A:**
    - added its five unbalance rows at the end (its conventions class unbalance as `other`);
    - three order slips (E01 recorded after X02 after being blocked in turn; V12 before G11 / E03; Q07 before G13);
    - settled five exclusion rules during extraction rather than in its conventions (power-level caps,
      settlement-charge tolerances, compatibility levels, D-A-CH-CZ Part B I Tab. 1-1 not a DC2R-3 table,
      commutation notches and signal voltages);
    - X01 "will be required" read as mandatory and "should" / "may be required" as recommendation;
    - V09 rated mandatory under the OCP base-spec rule.
  - **B:**
    - E01 recorded after V07 (positions 45 / 46 swapped);
    - in G01, G02, G03 and E04 read the screener's starting sections plus the large-load clauses it could find, and
      did not search the ERCOT Protocols exhaustively;
    - X01 "must" / "will be required" read as mandatory;
    - chose not to rate unbalance, notches, ripple control, steady-state regulation, or the U01 / U02 contract ramp
      schedules.
- **Launching session's exposure (pre-registration §7, repeated).** This session launched and analysed DC2 and has read
  DC2's rating files. It reached the raters only through the launch prompt, which is DC2's with mechanical
  substitutions (diff committed: [`DC2R_rater_prompt.diff`](DC2R_rater_prompt.diff)), and through the four-file
  clone. Neither names an instrument's content, a clause or an expected result. The rules file carries the brief's
  DC2R-1 … DC2R-3 wording, which names the Fingrid oscillation bands and the D-A-CH-CZ Part B tables as examples of
  row granularity (reviewer-approved, §9).
- **Display artefact (as DC2).** The `verdict_line` field in `dc2r.json` appends "history-shaped requirement at POI /
  facility only" whenever a history pair exists, even under UNGATED. The `verdict` field is UNGATED. The script was
  not changed after the rater files existed.

## 6. Deviations

None after any rater read requirement text (no DC2R-D2). The §6 items of the pre-registration did not move.

## 7. What this means

- **Pre-registered:** UNGATED, so no reading. Under the DC1b declaration (§4), DC1b is not run, and the leg closes
  on DC2-R.
- **Documentary, beside the gate failure.** Two fresh raters, under rules fixed in advance, again found the same
  picture as DC2's raters:
  - every binding limit on a large load's real-power variation is `hard` (Fingrid oscillation bands and steps at the
    POI; D-A-CH-CZ step tables; AESO steps), or states no window;
  - the single exception is ERCOT §6.5.7.11, a PCLR one-minute-average ramp band with 10 % of intervals allowed to
    fail, adopted but awaiting implementation.

  The reviewer's reading of that clause in DC2 (`../DC2/review/README.md`) applies unchanged: it is a performance test
  on telemetered one-minute averages for loads that opt into curtailment, and it does not see 0.2–3 Hz swings.
- **For a future audit of this kind** (lesson, not a deviation), fix two more things in advance:
  - *coverage*: which parts of a very large document are searched, for example a named section list per instrument;
  - *mixed tables*: whether a table that holds two quantities is one row or one row per quantity.

  With granularity and these two fixed, the remaining disagreement would be the reading itself.

## Reviewer acceptance (2026-11-11)

Accepted at `5883669` as **UNGATED**; DC1b is not run and the anticipation leg closes on DC2-R (pre-registration §4).
Every number in §1–§4 was re-derived by the reviewer from the four rater files with independent code
([`review/reviewer_check.py`](review/reviewer_check.py), output [`review/reviewer_check.out`](review/reviewer_check.out));
agreement is exact. Process checks, the reading of the coverage failure and the documentary conclusion are in
[`review/README.md`](review/README.md).

---

## Appendix. Every requirement, both raters

Classes as written by the raters; a cell shows "A / B" where they differ. Full fields (limits, quotes, URLs, notes) are
in `requirements_A.csv`, `requirements_B.csv` and `dc2r.json`.

### Matched pairs (83)

| pass | A | B | instrument | clause (A) | category (A) | quantity (A / B) | window (A / B) | allowance (A / B) | binding (A / B) | disagree on |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A001 | B007 | V03 | 5.6 | ≤140% ≤50ms moving average; ≤160% ≤4 | other | ≤ 100 ms | hard | recommendation | — |
| 1 | A003 | B033 | E10 | 1.1.2 | r ≥ 0,01 min-1; r < 0,01 min-1 | rapid voltage change | not stated | hard | planning level | — |
| 1 | A007 | B034 | E10 | 1.2.1 | LPst MS; LPlt MS; LPst HS; LPlt HS | flicker | 1 – 15 min | loose / hard | planning level | allowance_class |
| 1 | A008 | B035 | E10 | 1.2.2 | Pst MS V; Plt MS V | flicker | 1 – 15 min | loose / hard | planning level | allowance_class |
| 1 | A009 | B036 | E10 | 3.1.1 Tab. 3-1 | odd non-triplen; odd triplen; even o | harmonics | not stated | hard | planning level | — |
| 1 | A015 | B067 | X02 | 9.1.7 | single step from internal process | step change | not stated | hard | mandatory | — |
| 1 | A016 | B070 | X02 | 9.1.13 Taulukko 9.1 | 0,01–0,025 Hz | swing amplitude | 1 – 15 min | hard | mandatory | — |
| 1 | A017 | B071 | X02 | 9.1.13 Taulukko 9.1 | 0,025–0,05 Hz | swing amplitude | 1 – 15 min | hard | mandatory | — |
| 1 | A018 | B072 | X02 | 9.1.13 Taulukko 9.1 | 0,05–0,1 Hz | swing amplitude | 1 – 15 min | hard | mandatory | — |
| 1 | A019 | B073 | X02 | 9.1.13 Taulukko 9.1 | 0,1–0,2 Hz | swing amplitude | 1 – 60 s | hard | mandatory | — |
| 1 | A020 | B074 | X02 | 9.1.13 Taulukko 9.1 | 0,2–0,5 Hz | swing amplitude | 1 – 60 s | hard | mandatory | — |
| 1 | A021 | B075 | X02 | 9.1.13 Taulukko 9.1 | 0,5–2,0 Hz | swing amplitude | 1 – 60 s | hard | mandatory | — |
| 1 | A022 | B076 | X02 | 9.1.13 Taulukko 9.1 | 2,0–6,0 Hz | swing amplitude | 1 – 60 s | hard | mandatory | — |
| 1 | A023 | B077 | X02 | 9.1.13 Taulukko 9.1 | 6,0–18,0 Hz | swing amplitude | 1 – 60 s | hard | mandatory | — |
| 1 | A024 | B078 | X02 | 9.1.13 Taulukko 9.1 | 18,0–45,0 Hz | swing amplitude | 100 ms – 1 s | hard | mandatory | — |
| 1 | A026 | B079 | X02 | 9.1.1 |  | ride-through | 1 – 60 s | hard | mandatory | — |
| 1 | A027 | B080 | X02 | 9.1.3 |  | ride-through | 1 – 60 s | hard | mandatory | — |
| 1 | A028 | B081 | X02 | 9.1.10 Kuva 9.2; Kuva 9.3 | undervoltage curve; overvoltage curv | ride-through | ≤ 100 ms | hard | mandatory | — |
| 1 | A029 | B082 | X02 | 9.1.11 |  | ride-through | 1 – 60 s | hard | mandatory | — |
| 1 | A034 | B042 | E04 | CC.6.1.3 | 51.5-52 Hz; 51-51.5 Hz; 49.0-51 Hz;  | ride-through | 1 – 60 s | hard | mandatory | — |
| 1 | A035 | B040 | E04 | CC.6.1.7 Table CC.6.1.7(a) | Category 1 frequent events; Category | rapid voltage change | ≤ 100 ms | hard | planning level / mandatory | binding_class |
| 1 | A037 | B043 | E04 | ECC.6.4.5.1 | Non-Embedded Customers (EU Code User | power factor | not stated | hard | mandatory | — |
| 1 | A040 | B094 | E09 | 1.1.2 | r ≥ 0,01 min-1; r < 0,01 min-1 | rapid voltage change | not stated | hard | planning level | — |
| 1 | A044 | B095 | E09 | 1.2.1 | CPst NS; CPlt NS; LPst MS; LPlt MS;  | flicker | 1 – 15 min | loose / hard | planning level | allowance_class |
| 1 | A045 | B096 | E09 | 1.2.2 | Pst NS V; Plt NS V | flicker | 1 – 15 min | loose / hard | planning level | allowance_class |
| 1 | A049 | B003 | V08 | 3.13 Table 3 | 50% step load; 90% step load; 140% s | other | ≤ 100 ms | hard | mandatory | — |
| 1 | A050 | B004 | V08 | 3.15 |  | hold-up | ≤ 100 ms | hard | mandatory | — |
| 1 | A051 | B005 | V08 | 3.17 | ≤140% ≤50ms MA; ≤160% 400us MA; ≤100 | other | ≤ 100 ms | hard | recommendation | — |
| 1 | A052 | B002 | V08 | 3.7 | DC inrush; re-rush | other | ≤ 100 ms | hard | mandatory | — |
| 1 | A055 | B026 | V06 | 7.1.3.1 |  | hold-up | ≤ 100 ms | hard | mandatory | — |
| 1 | A056 | B027 | V06 | 7.2.1.1 |  | hold-up | 1 – 60 s | hard | mandatory | — |
| 1 | A057 | B028 | V06 | 7.3.2 Table 5 | Rack average power; <2 msec load ste | other | ≤ 100 ms | hard | mandatory | measurement_point |
| 1 | A058 | B029 | V06 | 7.3.3 Table 6 | 50% step load; 90% step load; 140% s | other | ≤ 100 ms | hard | mandatory | — |
| 1 | A059 | B049 | E11 | 1.1.2 |  | rapid voltage change | not stated | hard | planning level | — |
| 1 | A063 | B050 | E11 | 1.2.1 | LPst HS; LPlt HS; LPst HöS; LPlt HöS | flicker | 1 – 15 min | loose / hard | planning level | allowance_class |
| 1 | A064 | B051 | E11 | 1.2.2 | Pst HS V; Plt HS V | flicker | 1 – 15 min | loose / hard | planning level | allowance_class |
| 1 | A065 | B052 | E11 | 3.1.1 Tab. 3-1 | odd non-triplen; odd triplen; even o | harmonics | not stated | hard | planning level | — |
| 1 | A071 | B083 | G03 | 2.6.4(3) Table A | f > 63.0; 61.2 < f ≤ 63.0; 58.8 ≤ f  | ride-through | 1 – 15 min | hard | mandatory | — |
| 1 | A074 | B090 | G03 | 2.15(7) |  | ride-through | 1 – 15 min | hard | mandatory | — |
| 1 | A078 | B056 | V09 | 4.4.3 Table 1 | V > 1.20; 1.10 < V ≤ 1.20; 0.90 ≤ V  | ride-through | 100 ms – 1 s | hard | mandatory | — |
| 1 | A083 | B011 | X01 | 5.3 Requirements 1 |  | power factor | not stated | hard | mandatory | — |
| 1 | A085 | B013 | X01 | 6.1 Requirements 18-19 |  | ride-through | 1 – 60 s | hard | recommendation | — |
| 1 | A088 | B016 | X01 | 6.1 Requirements 25-26 |  | ride-through | 100 ms – 1 s | hard | mandatory | — |
| 1 | A092 | B010 | X01 | 7.4 Requirements 1 |  | step change | not stated | hard | mandatory | — |
| 1 | A093 | B059 | V07 | 4.5 | ≤140% ≤50ms moving average | other | ≤ 100 ms | hard | recommendation | — |
| 2 | A004 | B030 | E10 | Tab. 1-2 | r > 500 | step change | not stated | hard | planning level | — |
| 2 | A005 | B031 | E10 | Tab. 1-2 | 10 ≤ r ≤ 500 | step change | not stated | hard | planning level | — |
| 2 | A006 | B032 | E10 | Tab. 1-2 | r < 10 | step change | not stated | hard | planning level | — |
| 2 | A010 | B037 | E10 | 3.1.2 Tab. 3-2 | ν = 2 … 40 | harmonics | not stated | hard | planning level | — |
| 2 | A011 | B038 | E10 | 3.2.2 Tab. 3-3 | µ 1..2; 3..30; 31..39; near ripple-c | harmonics | not stated | hard | planning level | — |
| 2 | A012 | B039 | E10 | 3.3.2 | 200-Hz bands 2–9 kHz | harmonics | not stated | hard | planning level | — |
| 2 | A014 | B066 | X02 | 9.1.7 | third-party controls (markets etc.) | ramp rate | 1 – 60 s | hard | mandatory | — |
| 2 | A030 | B001 | E08 | 6.6 Tab. 6-6; (6-14); (6-15) | interharmonic µ 1,2; µ 3…30; µ 31…39 | harmonics | 1 – 60 s | loose | planning level | — |
| 2 | A031 | B064 | V05 | 4.3 Table 2 | Transient load response | other | not stated | hard | mandatory | — |
| 2 | A036 | B041 | E04 | CC.6.1.7(j) Table CC.6.7.1(b) | 3.3-33 kV; 66-400 kV | flicker | 1 – 15 min | not stated | planning level | — |
| 2 | A041 | B091 | E09 | Tab. 1-3 | r > 500 | step change | not stated | hard | planning level | — |
| 2 | A042 | B092 | E09 | Tab. 1-3 | 10 ≤ r ≤ 500 | step change | not stated | hard | planning level | — |
| 2 | A043 | B093 | E09 | Tab. 1-3 | r < 10 | step change | not stated | hard | planning level | — |
| 2 | A046 | B097 | E09 | 3.1.2 Tab. 3-2 | ν = 2 … 40 | harmonics | not stated | hard | planning level | — |
| 2 | A047 | B098 | E09 | 3.2.2 Tab. 3-4 | interharmonic orders µ | harmonics | not stated | hard | planning level | — |
| 2 | A048 | B099 | E09 | 3.3.2 Tab. 3-6 | 200-Hz bands 2–9 kHz; Sk V < 2 MVA;  | harmonics | not stated | hard | planning level | — |
| 2 | A053 | B024 | V06 | 7.1.2 Table 3 | PF load <20%; PF load ≥20% | power factor | not stated | hard | mandatory | — |
| 2 | A054 | B025 | V06 | 7.1.2 Table 3 | THD 5%< load <15%; 15% ≤ load <30%;  | harmonics | not stated | hard | mandatory | — |
| 2 | A060 | B046 | E11 | Tab. 1-2 | r > 500 | step change | not stated | hard | planning level | — |
| 2 | A061 | B047 | E11 | Tab. 1-2 | 10 ≤ r ≤ 500 | step change | not stated | hard | planning level | — |
| 2 | A062 | B048 | E11 | Tab. 1-2 | r < 10 | step change | not stated | hard | planning level | — |
| 2 | A066 | B053 | E11 | 3.1.2 Tab. 3-2 | ν = 2 … 40 | harmonics | not stated | hard | planning level | — |
| 2 | A067 | B054 | E11 | 3.2.2 Tab. 3-3 | µ 1..2; 3..30; 31..39; near ripple-c | harmonics | not stated | hard | planning level | — |
| 2 | A068 | B055 | E11 | 3.3.2 | 200-Hz bands 2–9 kHz | harmonics | not stated | hard | planning level | — |
| 2 | A069 | B022 | V12 | GPU ATTRIBUTES: Power Smoothing - Ra | current preset profile; admin overri | ramp rate | 1 – 60 s | hard | vendor capability | — |
| 2 | A070 | B023 | V12 | GPU ATTRIBUTES: Power Smoothing - %  | current preset profile; admin overri | swing amplitude | not stated | hard | vendor capability | — |
| 2 | A072 | B085 | G03 | 2.6.4(5)-(6) |  | ride-through | 1 – 60 s | hard | mandatory | — |
| 2 | A073 | B086 | G03 | 2.15(3) Table A; (a)-(f) | V > 1.20; 1.10 < V ≤ 1.20; 0.90-1.10 | ride-through | 100 ms – 1 s | hard | mandatory | — |
| 2 | A079 | B060 | G02 | 6.5.7.11(1) | down ramp rate | ramp rate | 1 – 60 s | very loose | mandatory | — |
| 2 | A080 | B061 | G02 | 6.5.7.11(2) | up ramp rate | ramp rate | 1 – 60 s | very loose | mandatory | — |
| 2 | A081 | B021 | V04 | 5.1 table | Transient load response | other | not stated | hard | mandatory | measurement_point |
| 2 | A084 | B012 | X01 | 6.1 Table 6-1 | V > 1.25; 1.15 < V ≤ 1.25; 1.10 < V  | ride-through | 100 ms – 1 s | hard | mandatory | — |
| 2 | A086 | B014 | X01 | 6.1 Table 6-2 | V > 1.8; V > 1.7; V > 1.6; V > 1.4;  | ride-through | ≤ 100 ms | hard | mandatory | — |
| 2 | A087 | B015 | X01 | 6.1 Table 6-3 | F > 61.8; 61.2 < F ≤ 61.8; 58.8 ≤ F  | ride-through | 1 – 15 min | hard | mandatory | — |
| 2 | A089 | B017 | X01 | 6.1 Requirement 28 |  | ride-through | ≤ 100 ms | hard | mandatory | — |
| 2 | A090 | B018 | X01 | 6.1 Requirement 31 |  | ride-through | 1 – 60 s | hard | mandatory | — |
| 2 | A091 | B008 | X01 | 7.2 Requirements 2 | ramp-up and ramp-down, normal operat | ramp rate | 1 – 60 s | hard | recommendation / mandatory | binding_class |
| 2 | A094 | B057 | U03 | A. General Rules 16 | neon, fluorescent or similar low pow | power factor | not stated | hard | mandatory | — |

### Unmatched rows, rater A (16)

| req | instrument | clause | category | quantity | window | allowance | binding |
|---|---|---|---|---|---|---|---|
| A002 | V03 | 5.5.1 |  | hold-up | ≤ 100 ms | hard | mandatory |
| A013 | E05 | 5.4.2 / 5.5 (VDE FNN FAQ) | Wirkleistungsbezug | rapid voltage change | not stated | hard | mandatory |
| A025 | X02 | 9.1.8 |  | other | 1 – 60 s | hard | mandatory |
| A032 | V05 | 4.3 Table 2; 4.5 | Startup time; Battery backup time; PSU-B | hold-up | ≤ 100 ms | hard | mandatory |
| A033 | V05 | 4.3.1 | Repetitive peak load; single non-repetit | other | not stated | hard | mandatory |
| A038 | E04 | BC1.A.1.1 | change greater than 300MW and less than  | ramp rate | 1 – 60 s | hard | mandatory |
| A039 | E04 | BC1.A.1.1 | change of 1000MW or more | ramp rate | 1 – 60 s | hard | mandatory |
| A075 | G03 | 2.3.1.2(10)(c) | FFR deployment on under-frequency (Load  | other | 100 ms – 1 s | hard | mandatory |
| A076 | G03 | 2.3.2.1(2) | Non-Spin CLR providers | other | > 15 min | hard | mandatory |
| A077 | G03 | 2.3.3.1(2) | CLR providing ECRS | other | 1 – 15 min | hard | mandatory |
| A082 | V04 | 5.1 table; 5.3 | Startup time; Battery backup time; Power | hold-up | ≤ 100 ms | hard | mandatory |
| A095 | E09 | 2.2 Tab. 2-1 |  | other | not stated | hard | planning level |
| A096 | E10 | 2.1 |  | other | not stated | hard | planning level |
| A097 | E10 | 2.2 Tab. 2-1 |  | other | not stated | hard | planning level |
| A098 | E11 | 2.1 |  | other | not stated | hard | planning level |
| A099 | E11 | 2.2 |  | other | not stated | hard | planning level |

### Unmatched rows, rater B (17)

| req | instrument | clause | category | quantity | window | allowance | binding |
|---|---|---|---|---|---|---|---|
| B006 | V03 | 5.5.1 |  | other | ≤ 100 ms | hard | mandatory |
| B009 | X01 | 5.1 Requirements 2, 4 |  | step change | not stated | hard | mandatory |
| B019 | V04 | 5.1 (table: Transient load response; Sta | Transient load response; Startup time | other | ≤ 100 ms | hard | mandatory |
| B020 | V04 | 5.1 (table: Battery backup time) | Battery backup time | hold-up | 1 – 15 min | hard | mandatory |
| B044 | E04 | DRSC.5.1(i) | Demand Response Providers | ride-through | 100 ms – 1 s | hard | mandatory |
| B045 | E04 | DRSC.7.1(c) | Demand Response Very Fast Active Power C | other | 1 – 60 s | hard | mandatory |
| B058 | G01 | 9.2.5(3) |  | step change | not stated | hard | mandatory |
| B062 | V05 | 4.3, Table 2 (Transient load response; S | Transient load response; Startup time | other | ≤ 100 ms | hard | mandatory |
| B063 | V05 | 4.3, Table 2 (Battery backup time) | Battery backup time | hold-up | 1 – 15 min | hard | mandatory |
| B065 | V05 | 4.5 |  | other | ≤ 100 ms | hard | mandatory |
| B068 | X02 | 9.1.8 | fast active power limiting function | smoothing or capping response | 1 – 60 s | hard | mandatory |
| B069 | X02 | 9.1.9 | undervoltage-triggered fast active power | smoothing or capping response | not stated | hard | mandatory |
| B084 | G03 | 2.6.4(5) |  | ride-through | not stated | hard | recommendation |
| B087 | G03 | 2.15(3)(b), (c) |  | ride-through | 1 – 60 s | hard | mandatory |
| B088 | G03 | 2.15(3)(d) |  | ride-through | 100 ms – 1 s | hard | mandatory |
| B089 | G03 | 2.15(3)(e) |  | ride-through | 100 ms – 1 s | hard | mandatory |
| B100 | E09 | 3.3.1, Tab. 3-5; 3.3.2, eq. (3-9), Tab.  | 2-3 kHz; 3-9 kHz | harmonics | not stated | hard | planning level |
