# X7 profile: hottest-cell spread, probe layout, folds and power (brief §3)

Run 2026-10-30 by `analysis/X7_profile.py`. Output: `X7/profile.json`.

**No observer, thermal model, margin κ_T or score has been computed.** All values are DERIVED from MEASURED surface
thermistors and pack current. Run conditions are SOURCED from the file names and the dataset README.

- **Licence:** McMaster 72S, **CC BY 4.0** (Naguib et al., Borealis doi:10.5683/SP3/UYPYDJ).
- **Caveat:** *surface thermistors on a 72S PHEV pack under drive cycles at ~0.9 SOC; spatial margin, not core margin.*
- **Reused:** `X2_replay.py`'s McMaster path and dead-channel rule. R is not identified here; only the step count is.

## Summary

| §3 item | Value | Gate / reading |
|---|---|---|
| **Power gate (§3.5):** runs with T_hot − T_median ≥ 3 K for ≥ 10 % of frames | **3 of 14 runs** (HWCUST_15C 22 %, US06_15C 14 %, HWFET_15C_ModuleBlocked_Long 66 %) | Needs ≥ 4 per fold, i.e. ≥ 8. **FAILS under any fold assignment: UNDERPOWERED.** |
| **Thermistor resolution** | **1 K steps.** 99.7 % of live readings are whole °C; the rest sit on 0.5 K. | This is the noise floor that matters (§5). |
| **Probe view vs the hottest cell (1 per 3 cells, layout fixed in §3)** | The probe maximum is **never more than 1.0 K below T_hot**, in any frame of any run. It is exactly T_hot in 84 % of frames and 1.0 K low in 16 % (0.5 K low in 0.01 %). | **The most margin any observer can recover is 1.0 K, which is the brief's bar.** |
| Hottest-cell value seen by a probe (§3.6) | 84 % of frames pooled (44–93 % by run). The argmax cell itself is a probe 42–74 %. | Not ≥ 90 %, so the §3.6 kill does not fire by itself. |
| Spread T_hot − T_median | p50 1–3 K, p95 1–5 K, max 2–6 K by run | Smaller than the brief expected |

**Headline of the profile:** on McMaster, a one-probe-in-three Tier M view already reads the hottest cell to within
one thermistor step in every frame.

- The question X7 asks needs a pack where unobserved cells run several kelvin hotter than any probe. This pack does not
  have one at the sensors' resolution.
- Under the brief's own §3.5 rule the verdict is **UNDERPOWERED**, and no observer should be fitted.
- Even ignoring the gate, a SPATIAL MARGIN RECOVERABLE verdict is structurally out of reach (§5).

## 1. Per run (§3.1)

Chamber and cooling are SOURCED from the file names. Current is MEASURED; I > 0 is charge (regen); 1 C = 5.2 A. Steps
are |ΔI| ≥ 0.3 C between consecutive frames (X2's R-identification events). Spread is T_hot − T_median over live
cells.

| Run | Frames (s) | Chamber | Cooling | I p5 / p50 / p95 (C) | Steps ≥ 0.3 C | Spread p50 / p95 / max (K) | ≥ 2 K | ≥ 3 K | ≥ 4 K | T range (°C) |
|---|---|---|---|---|---|---|---|---|---|---|
| Fanoffon_15C_Long | 11,188 | 15 °C | fan off, then on | −9.2 / 0.1 / 7.7 | 3,565 | 2 / 2 / 3 | 50 % | 2 % | 0 % | 14–46 |
| HWCUST_15C | 758 | 15 °C | normal | −15.1 / 1.1 / 9.5 | 246 | 2 / 3 / 3 | 85 % | **22 %** | 0 % | 14–31 |
| HWCUST_25C | 838 | 25 °C | normal | −14.1 / 0.0 / 9.6 | 289 | 2 / 2 / 3 | 50 % | 2 % | 0 % | 24–39 |
| HWFET_15C_ModuleBlocked_Long | 4,233 | 15 °C | module blocked | −7.4 / −1.7 / 9.6 | 1,661 | 3 / 5 / 6 | 83 % | **66 %** | 45 % | 14–37 |
| HWFET_15C | 1,273 | 15 °C | normal | −7.4 / −1.9 / 9.5 | 480 | 1 / 2 / 3 | 29 % | 4 % | 0 % | 14–28 |
| HWFET_25C | 1,493 | 25 °C | normal | −7.2 / −1.5 / 9.6 | 627 | 1 / 2 / 3 | 18 % | 2 % | 0 % | 25–37 |
| LA92_15C | 2,257 | 15 °C | normal | −9.6 / −0.0 / 7.8 | 1,030 | 1 / 2 / 3 | 43 % | 4 % | 0 % | 10–30 |
| LA92_25C | 2,314 | 25 °C | normal | −10.1 / −0.1 / 7.8 | 1,061 | 1 / 2 / 3 | 18 % | 2 % | 0 % | 25–37 |
| LA92_HighFan_15C | 2,012 | 15 °C | high fan | −9.7 / −0.0 / 7.8 | 847 | 1 / 1 / 2 | 5 % | 0 % | 0 % | 14–26 |
| UDDS_15C | 3,151 | 15 °C | normal | −6.4 / −0.1 / 4.0 | 1,482 | 1 / 1.5 / 2 | 5 % | 0 % | 0 % | 14–24 |
| UDDS_25C | 3,888 | 25 °C | normal | −6.2 / −0.1 / 4.0 | 1,682 | 1 / 1 / 2 | 2 % | 0 % | 0 % | 26–32 |
| UDDS_Blocked_25C | 3,201 | 25 °C | blocked | −6.7 / −0.1 / 5.8 | 1,307 | 1 / 1 / 2 | 3 % | 0 % | 0 % | 25–37 |
| US06_15C | 1,073 | 15 °C | normal | −17.0 / 3.8 / 5.9 | 282 | 2 / 3 / 3 | 78 % | **14 %** | 0 % | 14–30 |
| US06_25C | 1,264 | 25 °C | normal | −17.3 / 0.3 / 6.0 | 462 | 2 / 2 / 3 | 54 % | 1 % | 0 % | 26–39 |

**Channels:**

- **Dead:** cells **12 and 35** in HWFET_15C_ModuleBlocked_Long only (constant 1.0 °C; X2's rule). They are excluded
  from truth and from every probe set in that run.
- **Stuck:** no other channel was stuck at one value for more than half of any run while the pack moved.
- **Non-finite frames:** none in the thermistor and current channels.
- **Time base:** 1 s steps throughout, with no gaps.

**Not used, disclosed.** Every file also carries `Temp_Est` (the dataset authors' ECM temperature estimate) and
`Temp_Smooth`. Truth is `CellTemp_R` only. Neither authors' channel is a model input or comparator.

## 2. Spread available to recover (§3.2)

- The time fractions with spread ≥ 2 K and ≥ 4 K are in the table above.
- **Only one run (module blocked) ever reaches 4 K.** Twelve of 14 runs never exceed a 3 K spread.
- The large hot-minus-coldest spreads in `results/X/README.md` (up to 11 K, fan off/on) are mostly **cold** outliers.
  The hottest cell sits at most 3 K above the median in that run.

## 3. Probe emulation layout (§3.3, CHOSEN and fixed)

**Primary layout:**

- one thermistor per three cells: cells **1, 4, 7, …, 70** (24 probes);
- a dead probe cell moves to the next live cell up. No primary probe is dead in any run, so none moved.
- **Mean distance** from an unobserved cell to its nearest probe: **1.02 cells** (1.0 in the offset layout).

**Sensitivity layouts (brief §4.5):**

| Layout | Probes | Hottest value seen by a probe (pooled) | Frames where the probe max is 1 K below T_hot |
|---|---|---|---|
| **1 per 3, cells 1, 4, 7, … (primary)** | 24 | 84 % | **16.2 %** |
| 1 per 3, offset, cells 2, 5, 8, … | 24 (cell 35 → 36 in the blocked run) | 98 % | 1.7 % |
| 1 per 2 | 36 | 99 % | 1.3 % |
| Every cell (ceiling) | 70–72 | 100 % | 0 % |

**The gap never exceeds 1.0 K in any layout, run or frame** (max over 38,943 frames).

**Index adjacency is physical enough to interpolate along.**

- Neighbouring cell indices differ in their run-mean temperature by a median 0.10–0.52 K.
- Random pairs differ by 0.25–0.94 K: two to four times more.
- So M0's interpolation along the index and M2's nearest-neighbour coupling are reasonable layouts.
- The physical pack geometry is not in the README, so this is ASSUMED from the data, not SOURCED.

**The hottest cells are fixed places.** The most frequent hottest cell is 1, 28 or 29 in 13 of 14 runs (24 in the
fan-off run).

- Cells 1 and 28 are primary probes.
- With an offset layout, cells 29 and 2 are probes.
- Either way, the layout catches a hot spot that stays in one place.

## 4. Folds (§3.4, CHOSEN and fixed)

Each drive cycle's 15 °C and 25 °C runs go to opposite folds. The four abnormal-cooling runs are split so each fold has
one fan fault and one blockage.

| Fold | Runs | Chambers | Cooling | Frames | Runs passing §3.5 |
|---|---|---|---|---|---|
| **A** | HWCUST_15C, HWFET_25C, LA92_15C, UDDS_25C, US06_15C, Fanoffon_15C_Long, UDDS_Blocked_25C | 4 × 15 °C, 3 × 25 °C | fan off/on, blocked, 5 normal | 23,858 (fan-off run 47 %) | 2 (HWCUST_15C, US06_15C) |
| **B** | HWCUST_25C, HWFET_15C, LA92_25C, UDDS_15C, US06_25C, HWFET_15C_ModuleBlocked_Long, LA92_HighFan_15C | 4 × 15 °C, 3 × 25 °C | module blocked, high fan, 5 normal | 15,085 | 1 (module blocked) |

The brief asks that each fold contain at least one high-spread run. **That holds.**

## 5. Power gate (§3.5) and what the data can support

**Gate: FAILS.**

- Needed: ≥ 4 runs per fold with spread ≥ 3 K for ≥ 10 % of frames.
- Fold A has 2 such runs and fold B has 1.
- Only 3 of the 14 runs qualify, so **no assignment of the runs to two folds can pass.**
- **Brief §3.5: "Fewer is UNDERPOWERED: report and stop."**

**Independently of the gate, the margin ceiling is 1.0 K.** This is DERIVED from the raw probe-max gap; nothing was
fitted.

- M0's interpolated estimate can never exceed its highest probe. Linear interpolation stays between its endpoints.
- So its fitted margin κ_T(M0) must cover the gap T_hot − max(probes).
- That gap is 1.0 K in 16.2 % of frames and never more. **κ_T(M0) at the 0.2 % bar is therefore 1.0 K** in each fold.
  The offset layout's gap fraction is 1.7 %, so the same holds there.
- Δκ(M0 − M1) ≥ 1.0 K would need **κ_T(M1) = 0.0 K**. That means an observer that is never below the hottest cell's
  whole-degree reading in more than 0.2 % of frames, with no margin at all.
- **And the recovered 1.0 K is one thermistor step.** No Δκ below twice the floor may be claimed (§4.5.4).
  - With a 1 K quantum, the measured rest noise is about 0 K: channel SD at rest is 0.0 K in 26 of 28 windows, and a
    channel changes in 0–3 % of frames.
  - The meaningful floor is the quantisation itself, about 0.29 K RMS for a 1 K step (DERIVED, q/√12), or the 1 K step
    for a worst-case reading.

**Reading.** On this pack, at this sensor resolution, the spatial margin that probe interpolation carries is at most
one thermistor step. The experiment cannot distinguish "an observer recovers it" from "the sensor rounds it away".

## 6. Is the hottest cell already a probe cell? (§3.6)

| | Pooled | Range by run |
|---|---|---|
| The hottest **value** is read by some probe (ties count) | **84 %** | 44 % (HWCUST_15C) to 93 % |
| The first hottest **cell** is itself a probe | 52 % | 42 % to 74 % |

Neither reaches the brief's 90 % kill. With whole-degree sensors, though, the hottest reading is usually shared by
several cells, and a probe holds one of them.

## Notes for the reviewer

1. **By the brief's rule this is UNDERPOWERED.** I have still filed the pre-registration complete, with every
   threshold set, as the task asked. Its §0 says it should **not** run unless you change the gate by a numbered
   deviation.
2. **I would not relax the gate on this dataset.** A 2 K gate would pass 10 runs (5 per fold), but the 1.0 K ceiling (§5)
   makes SPATIAL MARGIN RECOVERABLE unreachable at any gate. The likely outcome is a NO MARGIN TO RECOVER that the
   sensors decide, not the models.
3. **A design point for any re-use of this brief (X7-P1 in the pre-registration).** Δκ compares margins, not
   estimates. A model biased upward by one degree gets κ_T = 0 for free. The pre-registration therefore scores the
   **mean issued bound** (T̂_hot + κ_T − T_hot, averaged over frames) as primary, with Δκ reported beside it.
4. **What would make X7 testable** is a multi-cell pack with sub-kelvin thermistors on every cell and an unobserved
   hot spot of several kelvin. No such public dataset is known to this session. Searching for one is a new-dataset
   question, so I have not started.
