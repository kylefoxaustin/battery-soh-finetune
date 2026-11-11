# L1 — reviewer acceptance (2026-11-10)

**Accepted at `a03164b`.** Every headline number in `results_L1.md` was re-derived from `ledger_A.csv`, `ledger_B.csv`,
`instruments_A.csv` and `instruments_B.csv` with the reviewer's own code (`reviewer_check.py`, output
`reviewer_check.out`), which reads no file the session's script wrote. Agreement is exact on: n_A 45, n_B 49, M 43
(40 by `act_id`, 3 by the ± 90-day rule), identification 0.843, κ 0.820 (observed 0.884), N_B 35, N_S 16 (8 of them
vehicle-level), R 2.19, judged 26, MC 10/26 = 38.5 % [22.4, 57.5], H 9/26 = 34.6 % [19.4, 53.8], both per-year tables,
V1 4.38 / V0 3.38 (both VOLATILE), CN0 1.86, FULL and ACC unchanged, the access table (13 / 8 / 4 / 10 and 13 / 3 / 0
/ 0), each rater's own counts, the union (39 / 20), 22 events in 2023–2025, 9 China-only, the eight unmatched events and
the five class disagreements. Verdict **UNCLEAR [V1: VOLATILE DOMAIN]**, not access-limited, kill does not fire —
confirmed.

**Process checks.** `analysis/L1_agreement.py` was committed (`b5a0d40`) before the launch prompt and before either
rater branch, and never touched again; the rater files were not touched after the merges. Each rater committed its
conventions before any change history was read (`a587531`, `a3f884a`). Rater B's ledger commits are batched at the end
of its run, which is a commit habit, not a blindness issue: B never fetched `l1-rater-a`. The launch prompt names no
hypothesis, tier or expected direction. Both raters applied the L-3 partial-access rule the same way (GB 38031-2020 /
-2025 and GB/T 18487.1-2023 logged as unreadable editions, GB/T 32960 and GB/T 27930 editions counted as `cannot
judge`), and both read the eleven UN R10 charging-mode acts as EMC test set-up rather than ECU-visible change. Rater A
built the UN histories by parsing every WP.29 agenda 2016–2026 and reading each proposal; rater B from the AC.1 vote
tables of every session report. Rater B's ISO events come from ISO's own open-data catalogue, an allowed route that A did
not find; they are unmatched and correctly left out of N_B.

## Exploratory readings (reviewer; not pre-registered; none deciding)

1. **R is fragile at this sample size.** With 51 matched seed events split 35 / 16, a binomial reading puts R in
   **[1.2, 3.9]** at 95 %. The pre-registered 3× bar sits inside that interval, as does the 1.5× kill. UNCLEAR is the
   right reading of the primary, and so is "the kill does not fire". The brief set the 3× bar without an uncertainty
   treatment; a future comparison domain with more than eight specific events would be needed to settle the ratio.
2. **Which events carry the Tier-A argument.** The pre-registered class order puts `hardware-or-recert` above
   `memory-or-crypto`, and §2's definition includes "must newly comply by a stated date". So MC (38 %) mixes two things:
   events that put a bigger stack on the ECU, and events that re-open approval or add a BMS warning. Splitting the ten
   above-software events by what the raters' own `what_changed` / `note` lines name (rule in `reviewer_check.py`,
   written after reading those lines, so exploratory):
   - **stack** (cryptographic, key-storage, update-authenticity, data-access, data-retention, telemetry or OTA
     requirement): **R155-00, R156-00, 2023/1542, 2024/1257, 2025/1707** — 5 of 26 judged, **19 % [9, 38]**;
   - **recert-or-function** (re-approval / phase-out dates, warning or monitoring functions, scope extensions,
     verification or documentation): 89 FR 104318, R100-03, R100-05, R155-00-S3, R156-01 — 5.

   The five `stack` events are exactly the cyber-security, software-update and EU energy-data acts: the
   regulation-driven stack of SYNTHESIS §0's positive null. They arrive as a handful of large acts (2020, 2023, 2024,
   2025), not as the 3-a-year drizzle; the drizzle is supplements, monitors and re-approvals that an in-service design
   absorbs in software. Under this narrow reading the MC condition would not be met; it is not the pre-registered
   reading and does not change the verdict.
3. **Counting-rule sensitivities, all unchanged in verdict.** Parallel supplements adopted as two documents for two
   series in force (R100 03/04 twice, R16 07/08 once) are counted twice under "one act, one event"; counted once, N_B
   33, N_S 15, R 2.20. Scope-extension events that do not touch an in-service M1 design (trailers, category L,
   driverless: 5 of 35) removed: N_B 30, N_S 15, R 2.00, MC 9/21.
4. **The floor.** The ten unread SAE instruments include J3400 (a new connector, 2024) and the J2847 / J2931 revisions;
   rater B's four catalogue-only ISO 15118 events are a second sign that N_B is a floor. None of this can raise N_S, so
   R is a floor too.

## What it changes

ANGLES §B.1's "no such arrival process" for body ECUs is withdrawn: the seat domain receives 0.7 specific events a year
and the vehicle-wide cyber / update floor on top. The battery / charging domain's 3.2 a year is real, sourced and
reproducible; its excess is 4.4× on specific events and 2.2× with the floor counted on both sides. The positive null in
SYNTHESIS §0 is strengthened in one respect: the events that force the stack are the cyber, update and energy-data
acts, and they are what size the software, not the drizzle.
