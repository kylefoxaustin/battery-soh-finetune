# Build Brief — Experiment X8: the bottom reserve. Does per-cell resistance admit more discharge current at low SOC than min/max, at equal held-out safety?

**Licence of this document:** public domain (CC0). **Written:** 2026-10-31. **Origin:** open-problem brief seed S1
([`briefs/OPEN_PROBLEM/README.md`](../OPEN_PROBLEM/README.md) §9) and ANGLES §1.1 / §B; item 4 in
[`briefs/NEXT_EXPERIMENTS/README.md`](../NEXT_EXPERIMENTS/README.md). The mirror image of X2-F.

> ## ▶ START HERE (first stage: profile and pre-registration only, then STOP)
>
> 1. `git pull` on `main`.
> 2. Read this brief end to end, then `results/X/X2F_preregistration.md` and `results/X/X2F/results_X2F.md` (the design
>    being mirrored), `analysis/X2F_replay.py` (the per-cell R identification, the odd/even step split, the κ
>    calibration and the held-out safety scoring: **reuse them**), and `results/X/README.md`.
> 3. Write `results/X/X8_profile.md` (§3) and `results/X/X8_preregistration.md` (§4 with every threshold filled in).
> 4. Commit both with "before limiter code" in the commit message. **Write no limiter or scoring code.** A loader and
>    the profile statistics are allowed.
> 5. Set the Status line in `NEXT_TASK.md` to `AWAITING APPROVAL <commit-hash>`, push, and stop.
>
> The reviewer will then edit this box to "APPROVED, run it now" or send changes.

---

## 0. Why X8 exists

The programme's one robust positive is X2-F: **per-cell resistance is a stable, identifiable property**, and a limiter
that knows it needs a margin of κ ≈ 1.10 against an independent reference where min/max needs κ ≈ 1.35–1.45 and does
not transfer to unseen vehicles. That was cashed out only at the **top** of charge, as admitted charge current, and the
gain at equal held-out safety was about +2.5 %.

The customer's C2 ("20 % reserve → 5 %") has a reading the programme never tested: a **bottom (low-SOC) reserve** set by
**power capability**, not energy. The pack is declared empty when the weakest cell would hit its cut-off voltage under
load; the reserve is the headroom a min/max BMS must keep because it sees only the present minimum voltage and cannot
predict how far each cell will sag under the *next* load step. A limiter that knows each cell's resistance can.

X8 asks X2-F's question at the other end of the curve:

> **On low-SOC discharge frames, how much more discharge current does a per-cell-R limiter admit than a min/max limiter
> at equal held-out safety against an independent per-cell reference, and does the gain survive a shuffle of cell
> identity?**

**Expectation, stated before the data is profiled.** On NMC the OCV curve is steep near empty, so the present minimum
voltage already identifies the weakest cell most of the time (X2-F found the binding cell was the max-voltage cell 89 %
of the time at the top of an NMC fleet). Any gain here comes from *predicting sag* at a current other than the present
one, i.e. power capability, not from identifying the cell. That gain may be small. A clean NO BENEFIT is a result.

**Licence, stated before the data is profiled.** Changan is **CC BY-NC-SA 4.0**: research only. Whatever X8 finds
cannot go on a customer slide; it can only direct where a licensed test should look. Beihang (CC BY 4.0) is used only
if the profile shows it carries what X8 needs (§2).

---

## 1. Rules of engagement (unchanged from X2-F / X7)

1. A pleasing number is a suspected defect until gated.
2. Tag every figure MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED. Everything here is DERIVED from field telemetry
   under ASSUMED limits; limits are replay quantities, not charge or discharge rates.
3. Pre-register before limiter code. Never move a threshold after seeing results. Number every deviation.
4. Every limiter carries **its own margin κ**, calibrated the same way (X2-F mistake 1: circular, margin-free references).
5. Safety is judged against an **independent per-cell reference** built from current steps **no limiter sees**
   (odd-index steps), on **held-out vehicles**.
6. Every per-cell claim gets a **shuffle control** that permutes R across cells **at every time step**, with its own κ.
7. Score the quantity a controller acts on: **admitted discharge current**, never a margin alone (X7-P1).
8. Put the data's **resolution** in the profile gate, not only its spread (X7's lesson): the sag being resolved must be
   many voltage LSBs.
9. Carry the licence and caveats onto every verdict: *Changan, CC BY-NC-SA, research only; NMC; 10 s telemetry;
   warm-climate fleet; the limits are ASSUMED replay quantities.*

---

## 2. Data

**Primary: Changan 300-EV** (CC BY-NC-SA 4.0): 300 NMC EVs, 96 cell voltages and 32 probe temperatures at 10 s, BMS
current and SOC, 130–220 k km each. The slim telemetry pipeline (`data/changan_slim.py`) and the X2/X2-F loaders exist.
Driving frames (discharge) are in the record; the programme has only ever used the charging frames.

**Secondary, conditional: Beihang QAS** (CC BY 4.0). Use **only if** the profile shows frames with a current signal and
per-cell voltages at low SOC during discharge (X2-C used it for charging; the record carries no timestamps). If it
qualifies, it becomes a replication arm with the same pre-registration; if not, say so and the verdict carries the
NC-SA caveat alone.

**Not usable here:** Weihai (HVAC-controlled BESS, no low-SOC discharge), McMaster (charge-sustaining at ~0.9 SOC),
ISU-ILCC (single cells).

---

## 3. Mandatory first step — profile (`results/X/X8_profile.md`, commit before limiter code)

1. **Low-SOC discharge segments.** Per vehicle: number of contiguous driving segments (I < 0 for ≥ 6 frames) that reach
   SOC < 20 % and < 10 %; their frame counts; current p5 / p50 / p95 in C (1 C from the cell's nominal capacity,
   SOURCED from `dataset_profile.md`); minimum cell voltage reached; coldest-probe temperature (so a cold subset can be
   defined).
2. **The cut-off (ASSUMED, fix now).** The minimum cell voltage observed fleet-wide and its 0.1 percentile. Fix
   **V_cut** as the 0.1 percentile rounded down to 10 mV (expected near the BMS's own floor); sensitivity at ± 50 mV.
3. **Per-cell R at low SOC.** Using X2's identification (steps |ΔI| ≥ 0.3 C between consecutive frames, pack-mean
   temperature change ≤ 1 K, finite voltages; per-cell R = ΔV_c / ΔI as the median over the block's steps), report on
   low-SOC frames: steps per vehicle, R_c median and the R_max / R_median ratio across cells, split-half rank
   correlation of R across cells (is it a stable property at the bottom as X2-F found at the top?), and how often the
   **minimum-voltage cell is also the highest-R cell** (if ≈ always, min/max sees the binding cell for free).
4. **Resolution gate (X7's lesson).** Cell voltage LSB (expected 1 mV from GB/T 32960 frames; confirm from the data) and
   current LSB. Report the median sag `|I_t · R_c|` on low-SOC frames at the observed currents and at the admitted
   currents the limiters will issue (approximate with the fleet-median R and the p95 current). **Gate:** median sag
   ≥ **10 LSB** (10 mV); below that the limiters would be comparing rounding, and the verdict is UNDERPOWERED by
   resolution.
5. **Power gate.** ≥ **30 vehicles** with ≥ **20 low-SOC (< 20 %) discharge frames** each that carry a per-cell R
   history (≥ 20 identification steps before the frame). Fewer is UNDERPOWERED: report and stop. Report the < 10 %
   and cold (coldest probe < 10 °C) subset counts separately; under 10 vehicles they are descriptive only.
6. **Folds (CHOSEN, fix now).** Vehicles split in two halves balanced by low-SOC frame count; κ is calibrated on one
   half and scored on the other, both directions (as X2-F).
7. **Beihang eligibility** (§2): does it carry current and per-cell voltage at low SOC during discharge? Yes/no, with
   counts.

---

## 4. Method (to be pre-registered after §3; mirrors X2-F)

### 4.1 Quantity scored

At each scored frame t (discharge, SOC < 20 %), each limiter issues an **admissible discharge current** `I_adm(t)`: the
largest current it would allow such that no cell falls below V_cut at the 10 s horizon. Currents are magnitudes; the
limiter uses the present measured current `I_t`, the present cell voltages `V_c(t)` and its resistance knowledge.

### 4.2 Reference (independent, as X2-F)

Per-cell resistance `R_c^ref` from the **odd-index** identification steps of the vehicle's history before t. The
reference's admissible current is `I_ref(t) = min_c (V_c(t) + I_t · R_c^ref − V_cut) / R_c^ref` (the cell's estimated
open-circuit voltage minus the cut-off, divided by its resistance). A limiter is **unsafe** at t if `I_adm(t) > I_ref(t)`.
The reference carries no margin; it is the yardstick, not a limiter.

### 4.3 Limiters (each with its own κ, calibrated on the calibration half)

| Limiter | Knowledge | Admissible current |
|---|---|---|
| **Per-cell** | `R_c` from **even-index** steps, every cell's `V_c(t)`, `I_t` | `min_c (V_c + I_t R_c − V_cut) / (κ_c R_c)` |
| **Min/max (Tier M comparator)** | the present minimum voltage `V_min(t)`, `I_t`, and a **pack-level** resistance `R_pack` (pack ΔV/ΔI from the same even steps, divided by cell count) | `(V_min + I_t R_pack − V_cut) / (κ_mm R_pack)` |
| **Shuffled per-cell** | as per-cell, with `R_c` **permuted across cells at every frame** (fresh permutation per frame; RNG seeded by vehicle and frame) | as per-cell, with κ_s |

κ is chosen per limiter on the calibration half as the smallest value on a **0.01 grid in 1.00–2.00** at which unsafe
frames ≤ **0.05 %**; the realised unsafe fraction on the evaluation half is the **held-out safety**, bar **0.2 %** (as
X2-F). Both are reported for every κ on the grid (the margin table X2-F found most informative).

### 4.4 Outcomes

- **S** = median over scored sessions of `I_adm,cell / I_adm,mm − 1` (the per-cell limiter's extra admissible discharge
  current at equal held-out safety).
- **S_sh** = the same for the shuffled limiter; **D = S − S_sh**, paired per session.
- Vehicle-bootstrap CIs (1,000 resamples, seed 0), both fold directions averaged.
- Secondary (reported, non-deciding): the same on SOC < 10 % frames; on the cold subset; the fraction of frames where
  the binding cell is not the minimum-voltage cell; **usable-depth** read as the SOC at which each limiter's admissible
  current first falls below the session's p95 demand (DERIVED, not kWh).

### 4.5 Decision (fill the numbers in the pre-registration; defaults below)

| Verdict | Condition |
|---|---|
| UNDERPOWERED | §3.4 resolution gate or §3.5 power gate fails |
| NOT INTERPRETABLE | any limiter's held-out unsafe fraction > **0.2 %** at its calibrated κ (report the margin table anyway, as X2-F did) |
| **PER-CELL HELPS AT THE BOTTOM** | S ≥ **1 %**, CI lower bound > 0, **and** D ≥ **1 pp** with CI > 0 |
| **NO BENEFIT** | S < 1 % with CI upper bound < 1 %, or S_sh ≥ S |
| **UNCLEAR** | anything else |

Report separately the κ each limiter needed (the margin reading) and whether min/max's margin transferred to the
held-out half, as X2-F did; those are the numbers that mattered last time.

### 4.6 Controls and sensitivity

1. Shuffle (§4.3) with its own κ.
2. Held-out vehicles, both fold directions.
3. Best Tier M option: min/max with a pack-level R and a fitted margin, not a fixed margin.
4. Sensitivity: V_cut ± 50 mV; horizon 20 s (two frames); R re-estimated per block vs held from the first 20 steps;
   0.1 % and 0.5 % safety bars; the < 10 % and cold subsets.
5. Resolution check: repeat the primary with cell voltages dithered by ± 0.5 LSB; if S moves by more than its CI width,
   the result is rounding.

---

## 5. Deliverables

1. `results/X/X8_profile.md` and `results/X/X8_preregistration.md`, committed before limiter code (first stage).
2. After approval: `analysis/X8_bottom.py`; `results/X/X8/results_X8.md` (verdict first, with the NC-SA caveat and
   chemistry), `x8.json`, the margin table, plots (κ vs unsafe fraction per limiter; S distribution; one session's
   admissible currents), one row each in `results/X/README.md` and `results/RESEARCH_DOSSIER.md` §9, a dated note under
   ANGLES §1.1 / §B.

## 6. What not to do

- Do not let any limiter be its own safety reference, and do not give the reference a margin.
- Do not use a shared limit map (H's mistake): every cell's admissible current comes from its own R and V.
- Do not tune V_cut, κ grids or the horizon after results.
- Do not report S without S_sh, D and the margin table beside it.
- Do not convert to kWh, range, cost or a C2 percentage; the result is a replay current ratio on non-commercial data.

---

*Profile the bottom first: how many frames, how much sag against the LSB, and whether the min cell is already the
high-R cell. Fix V_cut and the folds. Mirror X2-F exactly. Report the margins.*
