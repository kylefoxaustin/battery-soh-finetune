# Dataset profile — Changan "Large-Scale Lithium-Ion Battery Dataset for Real-World NEVs" (Analysis Brief §2)

Profiled 2026-10-08. The release is a two-volume split zip (`RAW_DATA.z01` 51.5 GB + `RAW_DATA.zip` 22.8 GB).
The profile was first done on the **85 vehicles** recoverable from the second volume alone, then repeated on
**all 300** once the first volume arrived (`data/changan_extract.py` reads across both volumes; every member
CRC-verified). The **full-set (300) figures are in the section "Full set" below and are the ones used by the
analysis**; the 85-vehicle tables are kept because they are where every labelling decision was made — before
any model was trained, and before the other 215 vehicles were seen.

Tags as in `results.md`: MEASURED / DERIVED / ASSUMED. Nothing here is a model result.

## What it is

| Item | Value | Tag |
|---|---|---|
| Source | State Key Lab of Intelligent Vehicle Safety Technology (Changan), released with Liu et al., *Nat. Commun.* 16:1137 (2025) | — |
| Licence | **CC BY-NC-SA 4.0; site terms: academic research only.** Used here for non-commercial research. If you reuse these results, follow the provider's terms. | — |
| Level | Vehicle / pack (96 series cells, 32 temperature probes); one OEM; ternary (NMC) Li-ion | MEASURED (columns), SOURCED (chemistry) |
| Units | 300 vehicles; all 300 recovered; 295 yield at least one capacity label | MEASURED |
| Sampling | 10 s per frame (`terminaltime` step) | MEASURED |
| Size | 74.3 GB of RAR archives (≈ 581 GB of CSV per the release page); one ~2 GB CSV per vehicle | MEASURED (archives) |
| Rows (85 vehicles) | ≈ 2–4 M frames per vehicle (e.g. vin3: 2,556,550 frames, 809 all-zero placeholders dropped) | MEASURED |
| Span (example) | vin3: 1,328 days, odometer 8 → 188,437 km | MEASURED |
| Field vs lab | **Real field data** — operating fleet vehicles, random partial charging, real climate | SOURCED + consistent with what we see |
| Fields kept | time, SOC (integer %), speed, odometer, charge status (GB/T 32960), pack V, pack I (+ = discharge), min/max cell V, min/max temperature | MEASURED |

## The label — there isn't one; we derive it, and that is the crux

The release ships **no capacity/SOH label**. The paper derived labels with Ah-integration from a post-rest
OCV-calibrated SOC to a full charge, using an **OEM OCV–SOC table that was not released**. We reproduced
that method as closely as the public data allows (`data/changan_labels.py`). Three things we found, each
measured on the 85 vehicles:

1. **BMS SOC is stale at full charge.** In all 85 vehicles the max cell reaches ≈ 4.2 V (true full) while the
   BMS reports a median **97 %** SOC; BMS SOC = 100 % almost never occurs (vin3: 7 frames in 1,328 days). This
   is the paper's own finding ("the BMS cannot timely update battery capacity information"). ⇒ The end anchor
   must be the **cell voltage** (max cell ≥ 4.20 V, CHOSEN), not BMS SOC.
2. **No OEM OCV table ⇒ we built one (ASSUMED).** From 17,346 rests (> 1 h) in each vehicle's first 20,000 km we
   took (max-cell voltage at wake, BMS SOC at wake), assuming a new pack's BMS SOC is still accurate. Result
   is a plausible NMC curve (3.52 V ≈ 6 %, 3.73 V ≈ 52 %, 4.21 V ≈ 100 %). Every label inherits this assumption.
3. **The label depends on the charger.** With the voltage anchor, labels from slow (≤ 15 A) and fast (≈ 49.5 A)
   charge endings differ by ~11 Ah, because IR drop at high current reaches the 4.2 V cutoff before the pack is
   full. Slow-charge labels show **no** trend with mileage and scatter widely; **fast-charge labels decline
   monotonically** (125.8 → 118.3 Ah median, 0 → 600 k km). ⇒ Primary label (CHOSEN): **charge capacity to the
   4.2 V cutoff at a ≈ 49.5 A end current** — consistent across life, biased low vs true capacity by a
   near-constant amount. It tracks degradation; it is **not** absolute capacity. All labels: **DERIVED**.

Reference point (SOURCED): the paper's own published labels (pooled, no vehicle IDs) decline from SOH 0.908 →
0.857 over 0 → 250 k km and scatter 0.040–0.046 SOH (robust–plain SD) about that trend.

## Label-noise floor and per-vehicle coverage

Within-vehicle noise = SD of a vehicle's labels about its own linear fit vs odometer (the prior run's method),
for vehicles with ≥ 20 labels spanning ≥ 50 k km. All DERIVED from DERIVED labels.

| Label filter (cumulative) | Vehicles qualifying | Noise SD (median) | Robust noise (MAD) | Fade over vehicle span (median) | Vehicles whose fit says capacity *rises* |
|---|---|---|---|---|---|
| Fast-charge, end current 40–60 A | 33 | 7.80 Ah | 4.74 Ah | 5.7 Ah | 30 % |
| … end current 48–51 A | 30 | 6.96 | 4.18 | 5.9 | 30 % |
| … + OCV start SOC 15–50 % | 20 | 5.02 | 3.66 | 7.1 | 15 % |
| … + wake→full < 6 h | 20 | 4.30 | 3.57 | 6.4 | 15 % |
| … + charge temperature 15–35 °C | 16 | 4.21 | 2.78 | 5.4 | 12 % |

Fleet scale for comparison: median label ≈ 120–126 Ah, so 4 Ah ≈ 3.3 %; between-vehicle SD of median capacity
≈ 5.9 Ah. EVBattery (prior run) had ≈ 1.6 % noise.

**Read-out:** per vehicle, the degradation signal (≈ 5–7 Ah over 130–220 k km) is only ~1.5× the label noise
under the strictest filter, and ~1× under the looser ones. Tightening the filter buys signal-to-noise at the
direct cost of qualifying vehicles.

## Full set (all 300 vehicles) — the numbers the analysis uses

| Item | Value | Tag |
|---|---|---|
| OCV table | 77 bins from 62,877 early-life rests (same method as above) | ASSUMED |
| Vehicles with ≥ 1 label / labels total | 295 / 17,474 (all charge types) | DERIVED |
| Fast-charge (end current 48–51 A) labels by odometer | 126.4 (0–50 k) → 123.6 → 122.7 → 121.1 → 120.2 → 118.6 Ah (300–600 k) | DERIVED |
| Slow-charge (≤ 15 A) labels by odometer | 130.5 → 126.2 → 125.2 → 127.6 → 128.2 → 126.7 Ah — no age trend (excluded) | DERIVED |
| Labels > 145 Ah among fast-charge labels | 3.1 % (removed by the 95–145 Ah plausibility band) | DERIVED |
| **Primary label set** (fast 48–51 A, 95–145 Ah) | **6,638 labels, 246 vehicles**; **94** qualify as targets (≥ 20 labels over ≥ 50 k km) | DERIVED |
| **Strict label set** | 3,285 labels, 224 vehicles; **45** qualify as targets | DERIVED |
| Label noise, primary targets (median within-unit SD / MAD about own linear fit) | **4.76 / 3.91 Ah** | DERIVED |
| Label noise, strict targets | 3.84 / 2.76 Ah | DERIVED |
| Per-unit fade over its span, primary / strict (median) | 6.5 / 6.3 Ah; 16 % / 7 % of units' fits say capacity *rises* | DERIVED |

So the full set reaches **N = 94** held-out units on the primary labels (brief asked for ≥ 100 — 6 short) and
45 on the strict ones. The signal-to-noise problem does **not** improve with more vehicles: per unit, total
fade over the unit's whole life is only ~1.6–2.3× the label noise.

## Representativeness

One OEM, one chemistry, one platform (96s pack, ~120–135 Ah by our label); operating-fleet duty (high mileage:
130–220 k km typical span). Climate/usage spread not characterized beyond charge temperature. **Scope any
result to this fleet.**

## Decision (§2: which subsets can answer §1)

- **Usable:** fast-charge-labelled vehicles under the filter rows above — **16 to 33 vehicles** of the 85,
  depending on the noise/coverage trade-off.
- **Excluded, with reason:** slow-charge labels (no age trend — label artifact); vehicles with < 20 fast labels
  or < 50 k km span (cannot form early-FT / gap / later-test splits); 1 vehicle with no full charges.
- **Consequence for the brief:** Experiment A asks for **N ≥ 100** held-out units. With only the 85-vehicle volume
  the qualifying pool was 16–33. **With all 300 vehicles it is 94 (primary) / 45 (strict)** — measured, and
  within the ~55–115 range scaling had suggested.
