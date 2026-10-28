# X2-C dataset profile and power check (Build Brief rev 6 §3)

Produced 2026-10-28 by `analysis/X2C_profile.py`, **before any X2-C limiter code exists**. It is committed together
with [`X2C_preregistration.md`](X2C_preregistration.md).

- **What was computed:** frame, step and session counts, charge depth, V_lim and Q_ref.
- **What was not:** no per-cell R, limiter value, κ or S.
- **Machine-readable outputs:** `X2C/profile.json`, `X2C/split.json` (vehicle IDs per half) and `X2C/frozen.json`
  (V_lim and Q_ref).
- **Tags:** every number is **DERIVED** from Beihang (Cao et al. 2025, Zenodo 10656500, **CC BY 4.0**). V_lim and
  Q_ref are **ASSUMED**, and frozen here.

## 0. Order of operations

1. **The vehicle split came first.** The normal vehicles were split 50/50 with `numpy.random.default_rng(0)`, before
   anything else was loaded.

   | Fleet | Normal vehicles | Calibration | Evaluation | Faulty, excluded |
   |---|---|---|---|---|
   | QAS | 335 | 167 | 168 | 58 |
   | DTI | 77 | 38 | 39 | 3 |

2. **Labels were used only to exclude faulty vehicles.** They were taken from G.2's `features.csv`, which holds
   Labels.xls as G.2 read it. `xlrd` is no longer installed.
3. **V_lim and Q_ref** were computed from the **calibration half only**, then frozen.
4. **Session and step counts** were computed for both halves.

## 1. Frames, current sign, chemistry

| | QAS | DTI |
|---|---|---|
| Vehicles (normal) | 335 | 77 |
| Rows | 11,872,516 | 3,257,610 |
| Valid frames | 10,188,117 | 3,257,610 |
| Charge-direction frames (charge current > 1 A) | 5,781,366 | 1,189,277 |
| Rows per vehicle, p10 / median / p90 | 27,639 / 32,760 / 43,193 | 4,769 / 48,179 / 62,724 |
| Median corr(ΔSOC, charge-positive I) | +0.16 | +0.46 |

- **Valid frame:** |I| < 900 A (drops the −1000 sentinel), every cell in [2.0, 4.5] V, and finite temperature.
- **Current sign:** the file stores **discharge as positive**. It is negated to charge-positive. This was checked
  with corr(ΔSOC, I) < 0 on raw rows.
- **Chemistry:** QAS cells sit at about 3.2–3.3 V with a top near 3.5–3.6 V. This is consistent with **LFP**. It is
  inferred from the voltages, not stated by the source. DTI is NMC-like (top 4.16 V).

## 2. Frozen limits (calibration half only, ASSUMED)

| | QAS | DTI |
|---|---|---|
| **V_lim**: p99.5 of per-frame max cell V over charge-direction frames, rounded down to 10 mV | **3.51 V** | **4.16 V** |
| **Q_ref**: median ΔAh/ΔSOC over charge segments with ΔSOC ≥ 20 % | **84.4 Ah** (p10–p90 79.4–89.6; 3,229 segments) | **140.6 Ah** (125.9–150.4; 1,537 segments) |

**Assumptions in these figures:**

- ΔAh assumes exactly 30 s between rows, inside a charge segment of consecutive valid charge rows. There are no
  timestamps, so a hidden gap inside a segment would bias Q_ref.
- 1 C is therefore 84.4 A (QAS) and 140.6 A (DTI).

## 3. Current steps (|ΔI| between consecutive valid rows, |ΔT| ≤ 1 °C)

Per-vehicle counts, p10 / median / p90:

| Threshold | QAS | DTI |
|---|---|---|
| ≥ 0.2 C | 2,150 / 3,295 / 5,092 | 379 / 9,855 / 12,240 |
| **≥ 0.3 C** | **1,163 / 2,103 / 3,647** | 248 / 6,040 / 7,982 |
| ≥ 0.5 C | 355 / 901 / 1,897 | 83 / 1,778 / 3,363 |

Steps are plentiful, unlike Changan, where a median of 7 fell in a 30-day window.

## 4. Charge depth and the primary population

**Sessions** are consecutive valid rows with charge current > 1 A. A session ends after ≥ 2 non-charge or invalid
rows, and must deliver ≥ 0.5 Ah.

The **gap** is V_lim − session-max Vmax, in mV. A negative gap means the session exceeded V_lim. The brief's "within
50 mV" counts gap ≤ 50, which **includes sessions above V_lim**.

| | QAS cal | QAS **eval** | DTI cal | DTI eval |
|---|---|---|---|---|
| Sessions ≥ 0.5 Ah | 13,097 | 11,694 | 11,538 | 12,461 |
| Gap p10 / median / p90 (mV) | −114 / 136 / 182 | −127 / 136 / 181 | 30 / 373 / 569 | 30 / 366 / 563 |
| Within 25 / 50 / 100 mV | 1,656 / 1,685 / 2,178 | 1,614 / 1,636 / 2,154 | 1,137 / 1,205 / 1,604 | 1,235 / 1,312 / 1,720 |
| Sessions with ≥ 20 R-steps (30-day window) | 13,002 | 11,599 | 11,498 | 12,414 |
| **Primary population** (30-day window, 50 mV) | 1,671 (93 vehicles) | **1,621 (106 vehicles)** | 1,188 (34) | 1,291 (35) |
| Primary at 25 / 100 mV | 1,642 / 2,155 | 1,599 / 2,136 | 1,120 / 1,582 | 1,214 / 1,694 |

**Power check: PASSED.** The QAS evaluation half has **1,621 primary sessions**, against a floor of 200.

**Reading the profile:**

1. **History is almost never the constraint on Beihang.** About 99 % of sessions have ≥ 20 steps in the window.
   - Records are only about 33 k rows, roughly 11 days at 30 s if gapless, so the 7-, 30- and 90-day frame windows
     give **identical** counts here.
   - The window sensitivity (§6 of the pre-registration) is therefore expected to be uninformative. This is stated
     in advance.
2. **QAS charge depth is bimodal.** About 14 % of sessions reach or exceed V_lim (gap ≤ 25 mV); the rest stop
   130–180 mV short. The primary population is mostly sessions that **reach** the LFP end-of-charge knee.
3. **Charging is gentle.** In the two vehicles inspected (0 and 5), charge current reaches about 32 to 18 A at p1, or about 0.2–0.4 C. So ≥ 0.3 C steps mostly come from
   driving transients, as on Changan.
