# Results FR1-R: how long a pre-event window do public HV power-electronics root causes need, when "not observable" is allowed?

Study FR1-R, run 2026-11-10.

| | |
|---|---|
| **Pre-registration** | [`FR1R_preregistration.md`](FR1R_preregistration.md), commit `2541d02`, before any rating; approved without changes |
| **Ratings** | `ratings_A.csv` (branch `fr1r-rater-a`, `c93dffc`); `ratings_B.csv` (branch `fr1r-rater-b`, `f29c987`). Notes, fetch records and launch prompts beside them. |
| **Code** | `analysis/FR1R_agreement.py`, written before either ratings file existed and tested on synthetic ratings only; `analysis/FR1R_documents.py`, `analysis/FR1R_orders.py` (stage 1) |
| **Output** | `fr1r.json` (every readout, every disagreement, every signal named) |
| **Tags** | Every rating is **DERIVED-judgemental**. Source: NHTSA Part 573 reports, chronologies and ODI résumés, public domain. No dollar figure. |

---

## Verdict (pre-registered §7)

| | Result |
|---|---|
| **Gate** | **Passes.** κ = **0.90** (four-class item 3, n = 147, PE and BR); 35 PE cases in the denominator (≥ 10) |
| **Retention** | **UNCLEAR.** P80 = **31 %** [19, 48] (11 of 35): below 50 %, and P40 = 31 % is not below 20 % |
| **Shape** | **MIXED.** RB = **17 %** [8, 33] (6 of 35): below 25 %; P80 is below 50 %, so not FLASH/CLOUD SHAPED either |

> **κ is reproducibility, not independence (D-3).** Both raters are language-model sessions (fresh-context sub-agents
> of the same model) rating from the same documents, so κ measures how reproducible the judgement is, not its
> independence from a shared model prior. Both also read the brief, whose §0 states FR1's κ and why FR1 failed its
> gate. Neither saw any FR1 rating: each worked in a sparse clone of `main` without the FR1 rating, notes, results or
> review files, and rater B never fetched rater A's branch.

**The reading in one line.** Of the in-scope power-electronics root causes that field data could show at all, about a
third need a pre-event window of seconds (state 2), a third need only the trip snapshot (≤ 1 s), and a third need
more than 80 s, mostly more than 700 s. One in six is ring-buffer shaped: seconds to minutes at ≥ 1 kHz.

## Readouts on the PE denominator (conservative reading)

**How 75 PE cases became 35:**

| Step | Cases |
|---|---|
| PE cases | 75 |
| Excluded (both raters set the same flag) | 22: out of scope 17, software-only 4, no cause stated 1 |
| `cannot judge` by either rater (after exclusion) | 0 |
| `not observable` by both | **17** |
| `not observable` by one rater | 1 (PE026) |
| **Denominator** | **35** |

Of the 53 PE cases left after the exclusions, **17 (32 %) are not observable by both raters.** Both raters judged
that no in-vehicle record, at any window, would have identified these causes: teardown-found part, weld, assembly or
design defects.

| Readout | Fraction | Wilson 95 % CI |
|---|---|---|
| **P80** (> 80 s; deciding) | **11 / 35 = 31.4 %** | 18.6–48.0 % |
| **P40** (> 40 s) | 11 / 35 = 31.4 % | 18.6–48.0 % |
| **RB** (seconds to minutes **and** ≥ 1 kHz; deciding) | **6 / 35 = 17.1 %** | 8.1–32.7 % |
| P1 (> 1 s) | 24 / 35 = 68.6 % | 52.0–81.4 % |

**Conservative state distribution:**

| State | Cases |
|---|---|
| `<=1 s` | 11 |
| `(1,40] s` | 13 |
| `(40,80] s` | 0 |
| `(80,700] s` | 4 |
| `>700 s` | 7 |

**Conservative rate class, states 2–5:**

| Rate class | Cases |
|---|---|
| `<=10 Hz` | 0 |
| `10 Hz-1 kHz` | 14 |
| `>=1 kHz` | 10 |

The distribution is **bimodal**: a trip snapshot or seconds (24) on one side, more than 80 s (11) on the other, and
nothing at about a minute.

**The six ring-buffer-shaped cases** (conservative state 2–4 at ≥ 1 kHz; signals as both raters named them):

| Case | Vehicle, group | Window | What would show it |
|---|---|---|---|
| PE008 | Arcimoto, contactor | (80, 700] s | contactor economizer-coil PWM current waveform |
| PE034 | Hyundai/Genesis E-GMP, ICCU | (80, 700] s | LDC current and DC-link voltage overshoot at end of charge |
| PE050 | Hyundai/Genesis E-GMP, ICCU | (80, 700] s | LDC output-voltage overshoot at start and end of HV charging |
| PE013 | Hyundai Ioniq Electric, OBC | (1, 40] s | ground offset and electrical noise on CAN at fail-safe entry |
| PE042 | Nissan Ariya, inverter | (1, 40] s | junction-box current-sensor ripple at high motor speed |
| PE052 | Polestar 3, DC-DC | (1, 40] s | 12 V rail transients during a software update |

**The > 700 s cases (7)** are different in kind. Most are a **per-event signature repeated over many cycles**, not a
continuous record:
- a contactor closing-current dip at each start (PE022);
- ICCU voltage peaks and temperature over many charge cycles (PE033, PE049, the Kia EV6 ICCU pair);
- pack current during fast charges and wide-open-pedal events, building contactor or fuse stress (PE027, PE045,
  PE060);
- intermittent gate-driver interruptions (PE073).

Four of the seven (PE022, PE033, PE049, PE073) need ≥ 1 kHz *within* each event.

## Agreement

| κ (unweighted Cohen's) | Value | n | Observed agreement |
|---|---|---|---|
| **Item 3, four classes (gate)** | **0.897** | 147 | 94.6 % |
| Item 3, seven-way (`cannot judge` its own class) | 0.867 | 150 | 92.7 % |
| Item 1, cause type | 0.856 | 150 | 93.3 % |
| Item 3b, rate class (both rated states 2–5) | 1.000 | 34 | 100 % |
| *Exploratory, not pre-registered:* item 3 four-class, PE only | 0.849 | 73 | 89.0 % |
| *Exploratory:* item 3 four-class, PE after exclusions | 0.898 | 53 | 92.5 % |

The PE-only κ is reported because 71 of the 75 base-rate cases are `not observable` by both raters, which could
inflate a pooled κ. It does not: on PE alone κ is 0.85.

**Against FR1** (both DERIVED-judgemental, same cases):

| | FR1 | FR1-R |
|---|---|---|
| κ, four-class item 3 | 0.19 | 0.90 |
| Pre-registered PE fraction > 80 s | 28 % [16, 44] of 36 | 31 % [19, 48] of 35 |

- **The missing state was the problem.** Adding `not observable` is what moved κ.
- **The headline fraction barely moved.**
- **Caution:** FR1-R also changed the document set to the union of both FR1 raters' documents, so not all of the κ gain
  can be attributed to the state.

## Secondaries (none deciding)

| Readout | Denominator | P80 | RB | P1 |
|---|---|---|---|---|
| **Primary** | 35 | 31.4 % [18.6, 48.0] | 17.1 % [8.1, 32.7] | 68.6 % |
| Sensitivity A: a one-rater `not observable` takes the other's state | 36 | 30.6 % [18.0, 46.9] | 16.7 % [7.9, 31.9] | 66.7 % |
| Sensitivity B: `cannot judge` counted as `<=1 s` | 35 | 31.4 % | 17.1 % | 68.6 % |
| One case per cluster (earliest campaign; 52 clusters) | 22 | 27.3 % [13.2, 48.2] | 13.6 % [4.7, 33.3] | 59.1 % |
| Rater A alone (its states 1–5) | 47 | 44.7 % [31.4, 58.8] | 12.8 % [6.0, 25.2] | |
| Rater B alone (its states 1–5) | 49 | 42.9 % [30.0, 56.7] | 10.2 % [4.4, 21.8] | |
| **Base rate (BR)** | 3 (71 of 75 `not observable` by both, 1 excluded) | 0 / 3 | 0 / 3 | 0 / 3 |

- **Each rater alone reads about 44 % > 80 s.** The conservative and exclusion rules bring that to 31 %. The gap is
  mostly the excluded cases: cell defects, an off-board charging cable and vehicle-level software, which both raters
  flagged but often rated `>700 s` (e.g. a self-discharge or SOC trend). A rater's own fraction does not apply the
  both-rater exclusion.

**By component group** (a case counts in each group it hits):

| Group | PE cases | Denominator | P80 | RB |
|---|---|---|---|---|
| OBC / charging control (incl. ICCU) | 13 | 8 | 4 / 8 | 3 / 8 |
| HV BMS / contactor unit | 34 | 15 | 6 / 15 | 1 / 15 |
| Traction inverter / motor controller | 31 | 13 | 1 / 13 | 1 / 13 |
| DC-DC converter | 4 | 1 | 0 / 1 | 1 / 1 |

- **The charging path (OBC / ICCU) is where both long windows and ring-buffer-shaped needs concentrate.**
- **Inverter causes are mostly software or calibration, seen in ≤ 40 s at 10 Hz – 1 kHz on CAN:** torque request
  against delivered torque, inter-inverter frames, current against broadcast limits.

**Cause type** (PE, A / B):

| Cause type | A | B |
|---|---|---|
| Manufacturing or component defect | 34 | 34 |
| Software or calibration | 26 | 27 |
| Unknown / mixed | 7 | 5 |
| Thermal | 6 | 4 |
| Transient electrical | 2 | 5 |

**Evidence that identified it** (PE, A / B):

| Evidence | A | B |
|---|---|---|
| Teardown only | 27 | 26 |
| Not stated | 21 | 20 |
| Bench reproduction | 10 | 14 |
| Fleet statistics | 9 | 8 |
| DTC freeze-frame | 5 | 6 |
| Waveform or high-rate capture | 3 | 1 |

## Documents

- **Both raters fetched all 364 URLs.** Every SHA-256 matched `FR1R_documents.json`, and no URL failed.
- **Two chronology attachments are image-only PDFs**, so they gave no text: `RMISC-23V657-1502` (PE026) and
  `RMISC-24V560-1690` (PE042). Both raters rated those cases from their Part 573 reports.
- **Both raters used the same reading aid**, disclosed in their notes: a display script that hides lines repeated
  across a case's amended reports, and, for long reports, vehicle-list lines. The defect, cause, chronology and remedy
  text was read in full.

## Every disagreement (listed, never reconciled; full detail in `fr1r.json`)

72 cases differ on at least one field:

| Field | Cases |
|---|---|
| Confidence | 35 |
| Evidence | 28 |
| Software-only flag | 13 |
| Window | 11 |
| Cause type | 10 |
| Out-of-scope flag | 7 |
| Rate class | 6 |
| No-cause flag | 3 |

On every single-rater flag, the flag is rater A's.

**Window disagreements (11):**

| Case | Rater A | Rater B | In the denominator? |
|---|---|---|---|
| BR057 | `not observable` | `cannot judge` | BR |
| PE015 | `(80,700] s` | `>700 s` | yes (conservative 4) |
| PE023 | `cannot judge` | `<=1 s` | excluded (both software-only) |
| PE026 | `not observable` | `<=1 s` | no (one rater not observable) |
| PE052 | `(1,40] s` | `>700 s` | yes (conservative 2) |
| PE053 | `>700 s`, `>=1 kHz` | `not observable` | excluded (both out of scope) |
| PE055 | `(80,700] s`, `10 Hz-1 kHz` | `<=1 s` | yes (conservative 1) |
| PE061 | `<=1 s` | `(1,40] s`, `<=10 Hz` | yes (conservative 1) |
| PE062 | `not observable` | `>700 s`, `<=10 Hz` | excluded (both out of scope) |
| PE063 | `not observable` | `>700 s`, `<=10 Hz` | excluded (both out of scope) |
| PE069 | `>700 s`, `>=1 kHz` | `not observable` | excluded (both out of scope) |

- Among non-excluded PE cases, only **one** of the 11 is the FR1 failure mode, `not observable` against a timed state
  (PE026, which therefore leaves the denominator).
- Four more are that mode on excluded, out-of-scope cases (PE053, PE062, PE063, PE069).

## What this says (for ANGLES §B.3)

1. **Retention necessity is not established.** P80 is 31 %, and the CI reaches 48 %. Under the pre-registered rule
   this is UNCLEAR, not NECESSITY.
2. **Retention is not merely a convenience either.** About a third of field-observable causes need more than 80 s, and
   a third need seconds.
3. **A ring buffer is the right shape for about one cause in six** (17 %, CI 8–33 %). These causes are concentrated
   in the charging path (the E-GMP ICCU end-of-charge overshoot, an OBC CAN-noise case) and in a few
   contactor-coil, current-sensor and 12 V transient cases.
4. **Most long windows are many short events over months, not one long record.** This is the flash/cloud leg, with a
   triggered high-rate capture *per event* in three cases.
5. **Not observable at any window: a third of in-scope causes** (17 of 53). Teardown is how these were found, and no
   pre-event record would have changed that.

The FR1 exploratory reading ("supported as event-triggered capture in the charging path, not as a recurring need")
now stands on a gated rating.

---

*Source NHTSA, public domain. Every rating DERIVED-judgemental, by two language-model raters (D-3). No dollar figures.*
