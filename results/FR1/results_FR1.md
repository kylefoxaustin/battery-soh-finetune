# FR1 results: how long a pre-event window would field data have needed to find the root cause of public HV power-electronics failures?

**Pre-registration:** [`FR1_preregistration.md`](FR1_preregistration.md) (with D-1 to D-6). **Case list:** [`FR1_cases.md`](FR1_cases.md).
**Ratings:** [`ratings_A.csv`](ratings_A.csv), [`ratings_B.csv`](ratings_B.csv). **Analysis:** [`analysis/FR1_agreement.py`](../../analysis/FR1_agreement.py) → [`fr1.json`](fr1.json).
**Written:** 2026-11-06 by the reviewer session, which ran the pre-registered analysis after merging both rater branches.

**Every rating is DERIVED-judgemental. Source of every rated document: NHTSA Part 573 reports, chronologies and ODI
résumés (US Government works, public domain). Both raters are language-model sessions reading the same documents
(D-3): κ measures the reproducibility of a judgement, not its independence from a shared model prior. The optional
human spot-check (D-4) was drawn but not rated (D-5, reviewer decision).**

---

## Verdict (pre-registered §6): **UNGATED**

The agreement gate failed: **κ = 0.19** on item 3 collapsed to ≤ 1 s / (1, 80] s / > 80 s over the 145 cases both
raters rated with a category (gate: ≥ 0.6). No reading of the gate passes: κ = 0.55 on the 71 PE cases, 0.52 on the 36
PE cases after exclusions, 0.01 on the 74 base-rate cases. The pre-registered fractions are therefore reported
without a verdict.

**Why the gate failed — a scheme defect, not a reading defect.** The two raters agree almost perfectly on *what* the
documents say (cause type κ = 0.87 all cases, 0.90 PE). They disagree on one thing the scheme never defined: what to
write when **no in-vehicle signal would show the cause at any window length** (a wrong part, an under-torqued
fastener, a bracket that fatigues, an inflator). Rater A's conventions (written before rating) mapped that to
**> 700 s** ("cannot be seen within any window"); rater B's conventions mapped it to **≤ 1 s** ("a longer window adds
nothing, so the minimum window is the smallest category"). Both are defensible readings of the pre-registered
question. The cross-tab shows the consequence: 82 of 93 disagreements are exactly A = > 80 s, B = ≤ 1 s, and the
base-rate sample — almost entirely mechanical defects — splits 96 % vs 7 %.

| Collapsed category | B: ≤ 1 s | B: (1, 80] s | B: > 80 s | B: cannot judge |
|---|---|---|---|---|
| **A: ≤ 1 s** | 23 | 1 | 1 | 0 |
| **A: (1, 80] s** | 2 | 12 | 0 | 0 |
| **A: > 80 s** | **82** | 1 | 23 | 0 |
| **A: cannot judge** | 4 | 0 | 0 | 1 |

The exploratory re-coding in §4, which gives "not observable in field data" its own state from each rater's own free
text, recovers **κ = 0.84** on the 47 cases neither rater placed there (0.86 on the 44 PE cases). That number is post
hoc and decides nothing; it says the two raters read the documents the same way wherever the scheme gave them a
category to agree on.

---

## 1. Exclusions and denominator (§4.3, §5)

| | Count |
|---|---|
| PE cases | 75 (D-1) |
| Excluded, both raters flagged: no cause stated | 4 |
| Excluded, both raters flagged: software-only, no electrical event | 17 |
| Excluded, both raters flagged: component out of scope | 23 |
| Excluded (any flag; overlapping) | 41 of 150 (PE 38, BR 3) |
| **PE after exclusions** | **37** |
| PE rated *cannot judge* by either rater (post-exclusion) | 1 |
| **PE denominator, conservative reading** | **36** |
| Single-rater flags (reported, not excluding) | no cause 4, software-only 6, out of scope 3 |

The gate's second condition (≥ 10 PE cases after exclusions) is met.

## 2. Pre-registered readouts (conservative reading = the lower of the two raters' categories)

| Population | n | > 80 s | > 40 s | > 1 s | Distribution |
|---|---|---|---|---|---|
| **PE, conservative (deciding if gated)** | 36 | **28 % [16, 44]** | 28 % [16, 44] | 42 % [27, 58] | ≤ 1 s 21 · (1, 40] 5 · (40, 80] 0 · (80, 700] 2 · > 700 8 |
| PE, rater A alone | 36 | 50 % [34, 66] | 50 % [34, 66] | 64 % [48, 78] | |
| PE, rater B alone | 37 | 30 % [17, 46] | 30 % [17, 46] | 46 % [31, 62] | |
| PE, *cannot judge* counted as ≤ 1 s | 37 | 27 % [15, 43] | | | |
| PE, one case per cluster (earliest of 25 clusters) | 25 | 24 % [11, 43] | 24 % [11, 43] | | |
| **BR (base rate), conservative** | 72 | 7 % [3, 15] | 7 % [3, 15] | 7 % [3, 15] | ≤ 1 s 67 · > 700 5 |
| BR, rater A alone | 72 | 96 % [88, 99] | | | |
| BR, rater B alone | 72 | 7 % [3, 15] | | | |

Wilson 95 % intervals. Had the gate passed, the PE conservative row would have read **UNCLEAR** (28 % is neither
≥ 50 % with a lower bound > 20 %, nor < 20 % on > 40 s). The base-rate rows show the scheme defect at its starkest:
the same body/chassis/restraint recalls read as 96 % "> 80 s" to one rater and 7 % to the other.

**By component group (PE, conservative, post-exclusion; non-deciding).** OBC / charging control 83 % > 80 s (n = 6);
HV BMS / contactor 25 % (n = 16); DC-DC 25 % (n = 4); inverter / motor controller 8 % (n = 12).
**By year:** no trend readable at these counts (n = 1–9 per year).

**Evidence that identified the cause (item 2, PE post-exclusion).** Rater A: fleet statistics 12, bench reproduction 8,
not stated 8, teardown 6, DTC freeze-frame 2, **waveform or high-rate capture 1**. Rater B: fleet statistics 13,
teardown 13, bench 4, not stated 4, DTC 2, **waveform 1**. Both raters find that public root causes were identified
from returned parts, bench work and warranty trends; essentially never from high-rate field capture. That is
consistent with such capture not existing in fielded vehicles, so it neither supports nor refutes its value; item 3 is
the counterfactual judgement.

**Cause type (item 1, PE post-exclusion, both raters within one case of each other).** Manufacturing or component
defect 20, software or calibration 6–7, thermal 4–5, unknown / mixed 4, transient electrical 2.

## 3. The cases both raters put beyond 700 s (post-exclusion; 8 of 36)

| Case | Campaign | What both raters say would have had to be retained |
|---|---|---|
| PE033, PE049 | 24V-200, 24V-867 (Kia EV6 ICCU) | ICCU input/output voltage at **≥ kHz near the end of charge**, plus ICCU and coolant temperature at ~1 Hz **over many charge cycles** |
| PE015, PE027, PE060 | 22V-412, 23V-687, 25V-441 (Mach-E contactor / bussed electrical centre) | pack current and contactor temperature or resistance at 1–10 Hz **over full DC fast-charge sessions** |
| PE045 | 24V-601 (LiveWire HV fuse) | pack current at ~100 Hz over many acceleration events (fuse I²t history) |
| PE054 | 25V-125 (VW OCDC) | OCDC humidity / dew point, temperature and LV output at 0.1–1 Hz **over days** |
| PE073 | 26V-309 (Lucid inverter gate driver) | gate-driver interruption events at high rate plus neighbouring temperature **over many cycles** |

Reading the named rates: the long windows the raters agree on are mostly **long and slow** (1–10 Hz over charge
sessions, cycles or days), with the ICCU pair also needing a **short kHz window at end of charge**. Across all
post-exclusion PE cases the rater-named rate for windows longer than 1 s is low-rate (≤ 100 Hz) in 17 of 23 (A) and
11 of 17 (B) rows, high-rate (≥ kHz) in 4 (A) and 6 (B). (Rate classes are a keyword read of the free text;
`analysis/FR1_agreement.py` companion check, non-deciding.)

## 4. Exploratory re-coding (post hoc, UNGATED, non-deciding)

Written after both conventions files were read; regexes disclosed in `fr1.json`. A case is "not observable" for rater
A if rated > 700 s with "not observable / no in-vehicle signal / none" in its free text; for rater B if rated ≤ 1 s with
"static / teardown / snapshot / inspection" in its free text.

| | B observable | B not observable |
|---|---|---|
| **A observable** | 50 | 30 |
| **A not observable** | 51 | 19 |

- κ (3-way) on the 47 cases neither rater marked not-observable: **0.84** (PE only: 0.86, n = 44).
- κ (4-way, "not observable" as its own category from each rater's own marking): 0.20 — the markings themselves do
  not line up, because the regexes are a proxy for a category the scheme never had.
- **PE conservative reading on the 20 post-exclusion cases both raters consider observable in field data:**
  > 80 s **50 % [30, 70]**, > 40 s 50 %, > 1 s **75 % [53, 89]**; distribution ≤ 1 s 5 · (1, 40] 5 · (80, 700] 2 ·
  > 700 8. Rater A on its own 35 observable cases: 49 % > 80 s; rater B on its own 20: 55 %.

This is what the study would have shown with a "not observable in field data" category. It is reported so the scheme
can be fixed; it is not a verdict.

## 5. What this does and does not say for ANGLES §B.3

- **It does not gate.** FR1's pre-registered verdict is UNGATED; the deciding fraction cannot be read.
- **The scheme defect is identified and fixable:** add a sixth item-3 state, *not observable in field data at any
  window*, and re-rate from the same documents under a shared convention (FR1-R, a re-run, not a reanalysis). Both
  raters' conventions files already show how each would apply it.
- **Direction of the evidence, labelled as such.** Among root causes that field data could have shown at all, both
  raters place about half beyond 80 s and three-quarters beyond 1 s (exploratory). But the windows they name are
  mostly **slow and long** — 1–10 Hz over fast-charge sessions, cycles, days — which is the cloud / flash retention leg
  (GB/T-class telemetry already carries per-cell data at 10 s), not the MB/s DRAM ring buffer B1 measured. The
  ring-buffer-shaped need (seconds to minutes at ≥ kHz) appears in a minority of rows (4–6 of 36), with the ICCU pair
  the clearest case: a triggered kHz capture at end of charge **plus** a long low-rate history. For §B.3 that reads:
  **event-triggered high-rate capture is implicated in the single costliest public campaign in the list, but the
  recurring need in the public record is long, low-rate history, which either tier can hold in flash.**
- **The base-rate control did its job**: it exposed the scheme defect that the PE sample alone would have hidden
  behind a plausible κ of 0.55.

## 6. Deviations applied (pre-registration §8)

D-1 list edits · D-2 branch blindness · D-3 disclosure · D-4 human subset drawn · **D-5** human subset not rated
(reviewer decision, 2026-11-06; the packet stays on `fr1-rater-h` for the record) · **D-6** rater B was launched as a
fresh-context sub-agent from the rater A session in a separate main-only clone, rather than "started by the reviewer";
disclosed by rater B before rating; blindness held by construction (no `fr1-rater-a` ref was ever fetched into that
clone). The analysis was written after the ratings existed; it implements §5–§6 as written, with §4 above the only
addition and labelled.

## 7. Recommended follow-up (not scheduled)

**FR1-R:** re-rate the same 150 cases from the same documents with a six-state item 3 (the five windows plus *not
observable in field data*), a stated data-rate class per window (≤ 100 Hz / ≥ kHz) as a closed list rather than free
text, and the same two-rater, two-branch procedure. Cost: the documents are already fetched and hashed on both
branches; one session-day per rater. The decision table can stay; the denominator becomes the observable cases.
