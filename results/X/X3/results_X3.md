# Results X3 (G.3) — per-cell drift on located faults: BatICM + BATSS case study

Experiment X3, run 2026-10-15.

- **Pre-registration:** [`../X3_preregistration.md`](../X3_preregistration.md), commit `0c4580a`. It was committed
  before any X3 code existed.
- **Code:** `analysis/X3_casestudy.py`. Output: `x3.json` and `run.log`.
- **Design:** a case study with n = 4 faulty packs; **no p-values**. Every time is DERIVED from released telemetry.
- **Fault identities:** SOURCED from Nie et al. (*Energy* 2025, Table 1) for BatICM. For BATSS the cell is a
  **prediction**, since the CIDETEC email was not sent.

## Verdict (pre-registered reading, §4)

**"Not supported on these cases."** The pre-registered identification test asked whether A's *first* flag points at
the faulty cell. It failed in 2 of the 3 BatICM faulty cars:

- in car2 the first flag (day 5.3) was a different cell, and the faulty cell followed at day 9.3;
- car4 was never flagged by A.

The healthy-car false-alarm control could not be applied (see deviation 3).

Under that verdict, the cases show three things worth carrying forward. All are descriptive, at n = 3–4.

1. **The min/max monitor almost never fired.**
   - B (vmin − pack median < −60 mV at rest) never flags in car3 or car4, and flags car2 only at **day 89**.
   - The per-cell monitors flag the paper's faulty cells at day 9.3 (car2, A), day 3.2–13.2 (car3, A_lvl and A), and
     day 34.7 (car4, A_lvl).
   - On these located faults, **per-cell data saw what min/max did not, by weeks to months.**
2. **Against the BMS's own first level-3 warning, the lead is mixed:**

| Car | First level-3 | A | A_lvl |
|---|---|---|---|
| car2 | day 24.6 | **+15.4 days** | +21.4 days, but tied with 4 other cells at its first flag |
| car3 | day 5.0 | **−8.2 days** (later) | +1.8 days |
| car4 | day 84.6, the last record day | never flags | +50 days, after one false flag |

3. **False alarms are the weakness, and they have a clear cause.**
   - In car2, A raised 78 wrong-cell flags. They all came in **contiguous blocks** that flagged together: cells 0–36
     at day 19.3, cells 46–72 at day 55.3, cells 73–86 at day 44.3.
   - That is the signature of **whole-module shifts**, which a pack-wide robust z treats as outliers.
   - Post-hoc, not tested: a module-aware z would remove them.

## Per-case detail

**Index convention.** The primary convention is the paper's cell #n read as CSV column V_(n−1). The paper's cell
counts (89 / 88 / 88) exceed the CSV's (88 / 87 / 87) by one. The alternative convention (V_n) identifies almost
nothing:
- A finds cell #83 in car2 only at day 44, and only after 39 false flags.
- It finds nothing in car3.

That supports the primary mapping.

| Case | Record | First level-3 | A: first correct flag (primary) | First A flag correct? | A false flags (before / total) | A_lvl: first correct | B (min/max) first flag |
|---|---|---|---|---|---|---|---|
| BatICM car2 (ISC, #83) | 111.7 d | 24.6 d | **9.3 d** | No (cell index 87 at 5.3 d) | 1 / 78 | 3.3 d (tied with 4 others) | 89.3 d |
| BatICM car3 (self-discharge, #3 and #82) | 26.9 d | 5.0 d | 13.2 d (both cells together) | **Yes** | 0 / 3 | **3.2 d** (first, tied with cells 48, 49, 67) | never |
| BatICM car4 (resistance rise, #64) | 84.6 d | 84.6 d | never | — | 0 / 0 | 34.7 d | never |
| BatICM car1 (healthy) | 1.6 d | — | not evaluable | — | — | — | never |
| BATSS ISC (cell unconfirmed) | 17.5 h | resistor-on time not in file | 11 h, flags **cell 8** first, then cell 2 at 12 h | Consistent with the prediction; **pending** | 0 / 1 | 13 h (cell 2 first) | never |

**BATSS caveat.** The cell-8 prediction was formed from this same rest data during the review. A flagging cell 8
first is therefore **not independent confirmation**. Only the authors can confirm it.

**What the vehicles' own BMS min-cell column shows.** Using `BMSCellVoltageMin` in B gives the same first-flag days
as the cell-list minimum.

## Deviations and disclosures

1. **DEV-1: the rest threshold is 2.5 A for BatICM.** The pre-registration said |I| < 0.05 C, but the BatICM packs'
   capacity is not published. 2.5 A equals 0.05 C of an ASSUMED 50 Ah pack, which is stricter than a larger pack
   would give. BATSS used 0.05 C = 3.35 A; 1C = 67 A was checked against the BATSS 1C charge file.
2. **DEV-2: BATSS has no resistor-on time.** Lead against resistor-on cannot be computed, so record start is used, as
   pre-registered.
3. **Car1 could not be evaluated, so the pre-registered false-alarm control could not be applied.**
   - Car1 is 1.6 days long. OPEN-1 requires ≥ 50 rest frames spanning ≥ 25 % of the 7-day window. That choice was
     fixed in the code before the run, because the pre-registration left the minimum open.
   - **The "≤ 2 false alarms in car1" clause could not be applied.** This was not foreseen when pre-registering.
4. **Bug fix before reading.** The first run read level-3 warnings after dropping rows without a full cell vector.
   That lost car4's level-3 warning, which comes on the last day. Warnings are now read from the unfiltered record.
   No threshold changed, and no other output moved.
5. **Ties are reported.**
   - When several cells cross on the same evaluation, "first flag correct" uses column order and is therefore
     arbitrary.
   - This affects A_lvl in car2 (cells 30, 31, 39, 40 and 81 together) and car3 (cells 1, 48, 49, 67 and 80
     together).
   - It also affects A in car3, where cells 1 and 80 are both faulty.
6. **Post-hoc material.** The module-block explanation of car2's false flags and the min/max comparison emphasis are
   post-hoc readings of pre-registered outputs.
7. **Seen before.** The G.1b last-10 % inspection and the warning-column timing were seen before the run (prereg §0).

## What this does and does not show

**Does:**

- On 3 field EVs whose faulty cells were located by expert analysis, per-cell rest-voltage features flagged those
  cells weeks to months before a min/max threshold monitor.
- In 1–3 of the cases (depending on feature), that flag came before the BMS's own severe warning.

**Does not:**

- **No error rate.** n = 3, and there is no usable healthy control.
- **No clean identification.** Pack-wide robust z mis-fires on module shifts, and the pre-registered identification
  rule failed.
- **No independence for BatICM.** Its fault labels come partly from the same voltage data.
- **No value claim.** That needs an OEM's cost per field event.

**Next, if pursued.** Pre-register a module-aware z, using module boundaries inferred from correlation as in the
review's `module_structure.py`. Then run it on a larger located-fault set: arXiv 2608.10825 when released, or Beihang
with dates.

**Licences:** BatICM is MIT; BATSS is CC BY 4.0. These results are not non-commercial-restricted.
