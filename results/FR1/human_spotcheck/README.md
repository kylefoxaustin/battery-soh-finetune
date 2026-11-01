# FR1 human spot-check — Rater H (the reviewer)

**Pre-registration D-3 / D-4.** Fifteen power-electronics cases, five from each of the three κ strata of rater A's
window ratings (≤ 1 s / 1–80 s / > 80 s), drawn with `numpy.random.default_rng(3)` and **shuffled, so the strata are
not recoverable from the order**. The stratum key is held by the drawing session only and is published with the
agreement analysis, not before. Non-deciding: κ(A, H) and κ(B, H) on these 15 are reported as a calibration of the two
machine raters. Source of every document: NHTSA, public domain. Every rating is DERIVED-judgemental.

## Rules for Rater H

1. Rate **from the linked documents only**: the Part 573 Safety Recall Report (and the chronology attachment where one
   is linked; the ODI résumé only where linked). No TSBs, press, forums, papers or memory of the case.
2. **Do not** open the `fr1-rater-a` or `fr1-rater-b` branches, any `ratings_*.csv`, or any `rater_*` file until your
   15 rows are committed.
3. Fill one row per case in `ratings_H_template.csv` (rename it `ratings_H.csv`). Use the closed lists below verbatim.
4. If a linked document will not open, write `cannot judge` for item 3 and say so in the note.
5. When done, commit `results/FR1/ratings_H.csv` on branch `fr1-rater-h` (or send the file back and the reviewer
   session will commit it).

## The question (item 3)

> **What is the shortest span of recorded vehicle data, ending at the failure, at a sampling rate you name, from which
> field data alone would have shown the cause?**

| Category (write exactly) | Meaning |
|---|---|
| `<=1 s` | an MCU freeze-frame around the trip would have shown it |
| `(1,40] s` | needs seconds of history (fits a HyperRAM window at 3.2 MB/s) |
| `(40,80] s` | needs about a minute (fits an MCU-with-SDRAM window) |
| `(80,700] s` | needs minutes (fits B1's measured 2 GB LPDDR window, 671 s) |
| `>700 s` | needs longer than that, or no in-vehicle signal would show it at any length (say which in the note) |
| `cannot judge` | the documents are too thin to say how the defect develops |

Also write the **signals and rate** you would need (e.g. "DC-link voltage and phase currents at 100 kHz",
"cell voltages at 1 Hz over a full charge").

## The other items (closed lists; write exactly)

- **item1_cause_type:** `transient electrical` · `thermal cycling or overload` · `manufacturing or component defect` ·
  `software or calibration` · `unknown / mixed`
- **item2_evidence** (what the documents say identified the cause; pick the most specific):
  `DTC freeze-frame` · `bench reproduction` · `fleet statistics` · `waveform or high-rate capture` · `teardown only` ·
  `not stated`
- **item4_confidence** (how well the documents support *your window*, not the cause): `low` · `medium` · `high`
- **item5 flags** (each `yes` / `no`):
  - `item5_no_cause_stated` — the documents state no cause;
  - `item5_software_only` — a logic or calibration error cured by software, with **no** damaged or faulty hardware
    (a real isolation fault or short that software merely misclassified is **not** software-only);
  - `item5_component_out_of_scope` — the part that actually failed is none of: OBC / charging control unit, DC-DC
    converter, traction inverter / motor controller, HV BMS / contactor / junction unit (e.g. a cable, a 12 V battery,
    a cell, a motor winding, a bracket).

## The 15 cases (rate in this order)

| # | Case | NHTSA campaign | Record page | Rating documents |
|---|---|---|---|---|
| 1 | PE007 | 21V-110 | <https://www.nhtsa.gov/recalls?nhtsaId=21V110> | [Part 573, amendment](https://static.nhtsa.gov/odi/rcl/2021/RCLRPT-21V110-3871.PDF) |
| 2 | PE020 | 23V-041 | <https://www.nhtsa.gov/recalls?nhtsaId=23V041> | [Part 573](https://static.nhtsa.gov/odi/rcl/2023/RCLRPT-23V041-3277.PDF) |
| 3 | PE041 | 24V-547 | <https://www.nhtsa.gov/recalls?nhtsaId=24V547> | [Part 573, amendment 1](https://static.nhtsa.gov/odi/rcl/2024/RCLRPT-24V547-5691.PDF); [chronology](https://static.nhtsa.gov/odi/rcl/2024/RMISC-24V547-0771.pdf) |
| 4 | PE025 | 23V-478 | <https://www.nhtsa.gov/recalls?nhtsaId=23V478> | [Part 573](https://static.nhtsa.gov/odi/rcl/2023/RCLRPT-23V478-2832.PDF) |
| 5 | PE044 | 24V-603 | <https://www.nhtsa.gov/recalls?nhtsaId=24V603> | [Part 573](https://static.nhtsa.gov/odi/rcl/2024/RCLRPT-24V603-2189.PDF) |
| 6 | PE012 | 21V-486 | <https://www.nhtsa.gov/recalls?nhtsaId=21V486> | [Part 573, amendment 1](https://static.nhtsa.gov/odi/rcl/2021/RCLRPT-21V486-9519.PDF); ODI investigation **PE21013** (search that ID on nhtsa.gov; use its opening/closing résumé) |
| 7 | PE017 | 22V-899 | <https://www.nhtsa.gov/recalls?nhtsaId=22V899> | [Part 573](https://static.nhtsa.gov/odi/rcl/2022/RCLRPT-22V899-6222.PDF); [chronology](https://static.nhtsa.gov/odi/rcl/2022/RMISC-22V899-9233.pdf) |
| 8 | PE070 | 26V-030 | <https://www.nhtsa.gov/recalls?nhtsaId=26V030> | [Part 573](https://static.nhtsa.gov/odi/rcl/2026/RCLRPT-26V030-0889.pdf) |
| 9 | PE037 | 24V-404 | <https://www.nhtsa.gov/recalls?nhtsaId=24V404> | [Part 573](https://static.nhtsa.gov/odi/rcl/2024/RCLRPT-24V404-4629.PDF) |
| 10 | PE074 | 26V-311 | <https://www.nhtsa.gov/recalls?nhtsaId=26V311> | [Part 573](https://static.nhtsa.gov/odi/rcl/2026/RCLRPT-26V311-6844.pdf) |
| 11 | PE001 | 19V-833 | <https://www.nhtsa.gov/recalls?nhtsaId=19V833> | [Part 573](https://static.nhtsa.gov/odi/rcl/2019/RCLRPT-19V833-4326.PDF) |
| 12 | PE010 | 21V-244 | <https://www.nhtsa.gov/recalls?nhtsaId=21V244> | [Part 573, amendment 1](https://static.nhtsa.gov/odi/rcl/2021/RCLRPT-21V244-7005.PDF) |
| 13 | PE011 | 21V-311 | <https://www.nhtsa.gov/recalls?nhtsaId=21V311> | [Part 573](https://static.nhtsa.gov/odi/rcl/2021/RCLRPT-21V311-3328.PDF) |
| 14 | PE015 | 22V-412 | <https://www.nhtsa.gov/recalls?nhtsaId=22V412> | [Part 573](https://static.nhtsa.gov/odi/rcl/2022/RCLRPT-22V412-9551.PDF) |
| 15 | PE042 | 24V-560 | <https://www.nhtsa.gov/recalls?nhtsaId=24V560> | [Part 573](https://static.nhtsa.gov/odi/rcl/2024/RCLRPT-24V560-5361.PDF) |

Links are the ones rater A's manifest recorded (SHA-256 on file). If NHTSA has since posted a later amendment, use the
latest Part 573 and say so in the note.

*Rate what the documents support, not what you suspect. "Cannot judge" is a valid answer. The point of this subset is to
see whether two language-model raters and an engineer read the same documents the same way.*
