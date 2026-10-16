# Experiment X3-b: pre-registration for neighbour-referenced per-cell drift, with a false-alarm rate on a healthy fleet

**What X3-b asks.** X3's pack-wide robust z mis-fired on whole-module shifts. Two questions follow:

1. **False alarms.** Does referencing each cell to its **neighbours** instead of the pack cut that rate on vehicles
   with no known anomaly?
2. **Detection.** Does it still locate the BatICM faulty cells?

**The new output** is a **false-alarm rate per 100 vehicle-days**. X3 had none.

**Origin and approval.**

- The v2 brief §8.4 item 4, revised in an internal response note (not included) §3.
- Kyle said "lets do all the recommendations" (2026-10-16).
- This file is committed **before** any X3-b code exists. The code will extend `analysis/X3_casestudy.py`.

**Tags.** All outputs are DERIVED. Licences:

| Data | Licence |
|---|---|
| Changan | CC BY-NC-SA 4.0, non-commercial |
| BatICM | MIT |

No p-values.

## 0. What is known in advance (disclosure)

- **The fix was designed after seeing X3.** The car2 false flags came in contiguous blocks (cells 0–36, 46–72,
  73–86). **The BatICM evaluation below is therefore POST-HOC by construction** and can only be descriptive.
- **The Changan healthy-fleet evaluation is new.** A, A_lvl and the neighbour-referenced features have never been run
  on Changan rest data. F ran a different feature: a daily −60 mV deviation from the pack mean.
- **Beihang normal vehicles are not used.** REVIEW §G.2 found its cohorts were processed differently.
- **The BMS-warning baseline exists only in BatICM** (n = 3 faulty cars).

## 1. Features (per evaluation; daily, trailing 7-day window, as X3)

**Rest frames and data minimum.**

- Rest is |I| ≤ 0.05 C: 6.0 A for Changan (Q_ref 120 Ah, ASSUMED as in X2), 2.5 A for BatICM (X3 DEV-1).
- The window needs ≥ 50 rest frames spanning ≥ 25 % of it (X3 OPEN-1).

**The features.** D_k is the deviation of cell k from the pack median (mV), and s_k is the OLS slope of D_k against
time over the window.

| Feature | Definition |
|---|---|
| **A** (as X3) | robust z across cells of s_k |
| **A_lvl** (as X3) | robust z of the window median of D_k |
| **A_nb** (new, primary) | robust z across cells of s_k − ref_k |
| **A_nb_lvl** (new) | the same construction on levels |

**How ref_k is chosen for A_nb.**

- L_k is the median of s over cells k−5 … k−1; R_k is the median over cells k+1 … k+5. Each is truncated at the pack
  ends, and a side with fewer than 3 cells is unavailable.
- ref_k is whichever of L_k and R_k is **closer** to s_k.
- **Rationale:** at a module boundary, one side is the cell's own module, so a module-wide shift cancels. A single
  drifting cell differs from both sides.

**Flag rule (unchanged from X3).** z ≤ −3.5 on 2 consecutive valid evaluations, with a gap resetting the count.

**Secondary (reported, no decision):** **A_mod**. The best regular block geometry is chosen per vehicle as in the
review's `module_structure.py`:

- block sizes {6, 8, 12, 16, 24, 32, 48}, all offsets;
- scored by within-block minus between-block correlation of daily rest deviations over the **whole record**;
- s_k is then referenced to its block median.

This uses future data, so it is labelled non-causal. In production the geometry would come from the pack design.

## 2. Healthy control: Changan

**Vehicles.** Those with **zero F event days**: no day on which any cell's daily rest deviation is < −60 mV, using
F's rule (`F_faults.py`: REST_A 1 A, MIN_REST 20). That is expected to be 250 of 300. F's 50 event vehicles are
reported separately as context, not as positives.

**Selection bias, disclosed.** Choosing vehicles with no −60 mV level days favours low false-alarm rates for level
features (A_lvl, A_nb_lvl). The **slope** features (A, A_nb) are the primary comparison for that reason.

**False-alarm rate.**

- An **episode** is a cell's transition from unflagged to flagged.
- FA rate = episodes per 100 valid vehicle-days, per feature.
- Also reported: the fraction of vehicles with ≥ 1 episode, and the size distribution of simultaneous episodes, as a
  module-shift signature.
- **Uncertainty:** vehicle bootstrap, 1,000 resamples, seed 0. This is an interval, not a test.

## 3. Located faults: BatICM cars 2–4 (POST-HOC, descriptive)

As X3, for A_nb and A_nb_lvl:

- first correct flag;
- whether the first flag is correct;
- false flags before the correct one, and in total;
- lead over B (min/max) and over the first **level-3 BMS warning**;
- index convention primary V_(n−1).

BatICM car1 is still not evaluable (1.6 days).

## 4. Pre-registered reading

**Primary: does neighbour referencing cut false alarms?** Compare A_nb with A on the Changan control.

| Reading | Condition |
|---|---|
| **REDUCES FALSE ALARMS** | A_nb FA rate ≤ 0.5 × A's, **and** the bootstrap interval of the ratio lies below 1 |
| **NO REDUCTION** | Ratio ≥ 0.8, or the interval includes 1 |
| **PARTIAL** | Otherwise |

**Absolute usability (reported against a stated bar, not a decision).** An FA rate ≤ 1 episode per 100 vehicle-days
is taken as "usable" (ASSUMED bar). That is about one false episode per vehicle every 3 months.

**Detection retained (descriptive, BatICM, post-hoc).** A_nb is said to *retain detection* if it flags the faulty
cell in at least as many of cars 2–4 as A does (A: 2 of 3).

## 5. Deviations

Any change after this commit is a numbered deviation. Thresholds are never moved.
