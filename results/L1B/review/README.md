# L1b — reviewer acceptance (2026-11-12)

**Accepted at `b0226dd` (Status `359df6a`): count UNGATED, kind UNGATED, seat domain CALIBRATED, lighting not
access-limited.** The full acceptance, the answer to the session's "is the kind readout a reading?" question (no), the
reviewer items R-1 … R-10 and the conditions under which a rerun would gate are in
[`../results_L1B.md` §10](../results_L1B.md).

**What this folder holds.**
- `reviewer_check.py` — the reviewer's own re-derivation of every number in `results_L1B.md` from the rater files
  (`ledger_*.csv`, `instruments_*.csv`, `stack_B_*.csv`), `B_events.csv` and L1's two ledgers (for N_S1 / E_S1). It reads
  nothing `analysis/L1B_agreement.py` wrote except, at the end, `l1b.json` for a side-by-side print. Run from the
  repository root: `python3 -I results/L1B/review/reviewer_check.py results/L1B results/L1`.
- `reviewer_check.out` — its output. Agreement with the session's write-up and `l1b.json` is exact on every readout
  (gates, calibration, N_L / N_S / R_BL / R_BS with intervals, the six variants, classes, per-year tables, access,
  unions, own counts, the 25 + 6 unmatched events, the 13 class disagreements, the stack shares, Fisher, the
  vehicle-level stack rows, the kind table and the exploratory collapse).

**Exploratory block at the end of the output (reviewer; not pre-registered; none deciding):**
- R_BL under every counting of the two ledgers: matched 0.73, A alone 0.51, B alone 0.67, union 0.48, FULL 0.44, one
  event per instrument-date 1.11–1.30. The 3× row is out of reach of this data.
- Seven of the sixteen battery `stack = yes` events were judged from a catalogue entry only (GB/T 32960 ×6, GB/T
  27930-2023; class `cannot judge` in L1): without them 9 / 20 = 45 % [26, 66], Fisher p 1.1 × 10⁻⁵; also without the
  three IEC 61851 editions 6 / 17 = 35 % [17, 59], p 3.4 × 10⁻⁴. Lighting stays 0 / 40.
- Of the sixteen, three are the Linux-class acts POSITION §1 names (2023/1542, 2024/1257, 2025/1707); the other thirteen
  name telemetry, charging communication or data read-out — several of them MCU-class obligations. "16 of 27" is a count
  of obligations of five kinds, not of acts that force Tier A.
- 2025–2026 adoptions: L 18 of 40, B 12 of 35, S 1 of 6.

**Process checks passed:** script and prompt at `857134e` before either branch; both branches fork from `857134e`;
conventions committed before any ledger row (`267949f`, `9091fe4`); rater B started after rater A finished and never
fetched A; clean merges; no rater file touched after the merges; launch prompts equal the committed prompt up to the
`{R}` / `{r}` and path substitutions; no source bypassed; POSITION §1 sentence 1 not rewritten by the session.
