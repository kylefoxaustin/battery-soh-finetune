# Experiments X1–X3: does *history* change a decision?

**Origin.** A research brief (not included),
written 2026-10-15 after the independent review ([`../review_2026-10-15/REVIEW.md`](../review_2026-10-15/REVIEW.md)).

**Thesis.** E–H2 measured *information content*; the value question is about *decisions*. History buys efficiency
where it changes a loop-rate action (the converter), and buys expected value where it changes a rare decision (the
pack).

## Files

| File | What | Status |
|---|---|---|
| [`X2_preregistration.md`](X2_preregistration.md) | H3: a per-cell limiter whose per-cell parameters come from history | Frozen at 0c4580a; **run 2026-10-15** (Kyle approved). Results in [`X2/results_X2.md`](X2/results_X2.md): **NO BENEFIT** in the cold primary arm (median S 0.0 %, 562 cold sessions with history); POST-HOC, warm sessions with history gain a median +5.5 %. |
| [`X3_preregistration.md`](X3_preregistration.md) | G.3: BATSS + BatICM lead-time case study | Frozen at 0c4580a; **run 2026-10-15**. Results in [`X3/results_X3.md`](X3/results_X3.md): **not supported** by the pre-registered identification rule. |
| [`X2M2_preregistration.md`](X2M2_preregistration.md) | McMaster with a SOURCED power-cell map (CC BY) | Frozen at ea9f714; **run 2026-10-16**. [`X2M2/results_X2M2.md`](X2M2/results_X2M2.md): **descriptive, 0.00 %** at the dataset's 6 C; +3.0 % only under a 125 A sensitivity map. |
| [`X2P_preregistration.md`](X2P_preregistration.md) | Active probing as an R precision and coverage curve | Frozen at ea9f714; **run 2026-10-16**. [`X2P/results_X2P.md`](X2P/results_X2P.md): a usable R needs about 80 steps ≥ 0.3 C; no injection rate up to 10 per charge reaches 90 % coverage in 7 days (30 days: 5 per charge). |
| [`X3b_preregistration.md`](X3b_preregistration.md) | Neighbour-referenced drift and a healthy-fleet false-alarm rate | Frozen at ea9f714; **run 2026-10-16**. [`X3b/results_X3b.md`](X3b/results_X3b.md): **NO REDUCTION**; A_nb doubles false alarms (43.5 against 21.8 per 100 vehicle-days), and X3's rule itself fails a usability bar by about 20×. |
| [`X2C_preregistration.md`](X2C_preregistration.md) and [`X2C_profile.md`](X2C_profile.md) | Build Brief rev 6: confirmation of X2's +5.5 % on new data (Beihang QAS), κ calibrated on held-out vehicles | Frozen at d27093f; **run 2026-10-28**. [`X2C/results_X2C.md`](X2C/results_X2C.md): **NOT INTERPRETABLE** (realised held-out unsafe 0.24 % > 0.2 %). The shuffle control beats the real limiter in every variant (11.7 % against 10.8 %), so the gain is margin asymmetry, not per-cell knowledge. **X2's +5.5 % is not confirmed.** |
| [`X2F_preregistration.md`](X2F_preregistration.md) | Fair comparison: each limiter has its own margin; safety judged against a per-cell reference from disjoint (odd-index) steps; shuffle with its own margin. Pre-registered **re-analysis** of X2-C's data | Frozen at 6cbfeb8; **run 2026-10-28**. [`X2F/results_X2F.md`](X2F/results_X2F.md): **NOT INTERPRETABLE** (min/max held-out unsafe 0.23 % > 0.2 %). The mechanism now shows: shuffled per-cell loses to min/max (−1.1 %), real per-cell gains +4.2 %, paired gap +5.5 pp, positive in every variant. The size of the gain is grid-sensitive (+0.6 % to +4.8 %), and the only fully interpretable variant reads NO BENEFIT (+0.6 %). Per-cell needs a κ of about 1.10 against the reference, min/max 1.35–1.45. |
| [`X2S_preregistration.md`](X2S_preregistration.md) | Replication of X2-F on a second LFP dataset (Schaeffer et al., 28 returned systems, CC BY-NC): two-fold cross-fitting, system-weighted, 0.01 κ grid | Frozen at dcd07e8; **run 2026-10-29**. [`XS/results_X2S.md`](XS/results_X2S.md): **NOT INTERPRETABLE** (min/max cannot be made safe even at κ 2.00). Direction repeats: S_sys +4.2 % (CI 1.9–6.5), shuffled −0.75 %, D +5.2 pp, positive in 8 of 8 systems. DEV-1: up/down step R differ 2–3× on this data, so a direction-balanced split was added. |
| [`X5_preregistration.md`](X5_preregistration.md), [`X5_profile.md`](X5_profile.md) | Can per-cell history shrink an uncertainty reserve? Clean-label test on ISU-ILCC (CC BY 4.0, lab RPT capacity, label noise 0.24 %); synthetic 4-cell packs, no coupling | Audit/prereg 059b818, reviewer-approved with D-1/D-2 (624e4ee); **run 2026-10-30**. [`X5/results_X5.md`](X5/results_X5.md): **UNCLEAR** (P3 and P4, full life and first life). P3 vs pack scalar 1.50× at α 1 %, but the shuffled control gains 1.55× and the weakest-cell series alone matches P3; 4× not reached (best P4 1.82×). Packs `lifecost/`, `convsim/`, `x4/` (X4 re-scored on the over-statement tail, NO GAIN unchanged). |
| X1 (bench), and an unsent email draft to the BATSS authors | | Not included in the public mirror. |

**Order of work.** Each pre-registration was committed before any X analysis code existed. X2 and X3 were run on 2026-10-15; X1 is blocked.

## Corrections to the brief, found while drafting (checked 2026-10-15; DERIVED, read-only probes)

These change the design of X2 and X3, so they are recorded here and disclosed in each pre-registration.

1. **McMaster's "28 °C intra-pack spread" is two dead thermistors, not a gradient.**
   - In `HWFET_15C_ModuleBlocked_Long`, cells 12 and 35 read a constant 1.0 °C for the entire run.
   - Excluding them, the real per-cell spread is median 5 °C, p95 8 °C, maximum 9 °C.
   - The claim came from the review's big-picture report and was repeated in the brief. It is withdrawn.
   - **Across all 14 McMaster runs**, the real spread is at most 11 °C (Fan-off/on run: p95 9 °C, max 11 °C), and
     the minimum cell temperature is 10 °C or above. **McMaster has no cold regime and no large gradient.** It does
     have a *hot* regime: the Fan-off run reaches 46 °C.
2. **McMaster has no charge sessions.**
   - The 14 files are 1 Hz drive cycles of 758–11,188 s, run charge-sustaining at about 0.9 SOC.
   - Charge-direction current appears only as regen pulses: positive current is charge (dV/dI < 0 for I > 0).
   - The metric for McMaster is therefore *admissible regen current*, not charge time.
   - Upside: these runs sit near 4.2 V, where a voltage-headroom limit binds often.
3. **BATSS has no real cold regime either.**
   - During charging in the 10 °C ambient run (`8_SteadyState_Ta10_Tl25`) and the 10 °C coolant run
     (`10_SteadyState_Ta25_Tl10`), the coldest thermocouple reads 9.8–10.5 °C at p5.
   - Those runs cycle at partial SOC (cell V ≤ 3.83 V), so a top-of-charge taper rarely binds.
   - The 3C fast charge (`19_FastCharge_3C`) reaches 79 °C.
   - BATSS has 55 thermocouples on a 10-cell string, and **which thermocouple sits on which cell is not documented in
     the files**.
4. **The only cold data in hand is Changan.** It has 2,855 charge sessions with the coldest probe below 10 °C
   (`results/H/replay_sessions.npz`) and is CC BY-NC-SA.
5. **BatICM BMS warnings are non-zero from the first day.**
   - car2 has level 2 on day 1; car3 has level 2 in the first frame; car4 has level 1 in the first frame.
   - Level 3 first appears on these dates:

| Car | First level-3 warning |
|---|---|
| car2 | 2019-05-10 |
| car3 | 2019-04-20 |
| car4 | 2019-07-09, the record's last day |

   - The level semantics are not documented, so "lead over the BMS" is defined against the first **level-3** warning,
     and that choice is disclosed.
6. **The +2.0 % per-cell-R prior** is the review's post-hoc figure (`h_report.md`, 38 Changan vehicles). The main
   session has **not** re-checked it (REVIEW §2, status "—"). X2 uses it only as a stated prior, not as a result.
7. **The brief cites the dossier at commit b9b4e66.** The dossier was created at 731c2b7 and revised at 2013325.
   Request 5 of the brief, the "could this data have shown it?" column, **was already added** to dossier §9 at
   2013325.

## What the corrections mean for X2

**What the data in hand supports:**

- **Changan cold sessions:** cold, real charging, NMC. This is the main arm.
- **McMaster:** hot, with per-cell thermistors and so a known mapping, regen near 4.2 V. This is the per-cell-R
  headroom arm.
- **BATSS fast charge:** hot, but its thermocouple-to-cell mapping is unknown.

**What none of it supports** is the "large gradient" regime the brief hoped for. X2 can still answer whether
history-derived per-cell parameters change the limit. It cannot answer whether they help under a large gradient.
