# Experiment X2-M2: pre-registration for McMaster with a SOURCED power-cell current map

**What X2-M2 asks.** Under a charge-current cap taken from **sources** rather than tuned, does a per-cell limiter with
history-derived R admit more regen current than an equally safe min/max limiter on the McMaster 72S pack?

**Why it matters.** McMaster is CC BY 4.0, so this is the only arm of the X2 programme that can be cited
commercially.

**Origin and approval.**

- Recommended in an internal response note (not included) §3; Kyle said "lets do all the recommendations"
  (2026-10-16).
- This file is committed **before** any X2-M2 code exists.
- The code is a parameter change to `analysis/X2_replay.py` `mcmaster(qscale)`, which already exists.

## 0. What is known in advance (disclosure)

- **Pre-registered X2-M, map ×1:** G = 0 in all 14 runs. This is structural: the cap was 1.5 C = 7.8 A, against
  about 150 A of regen.
- **POST-HOC map ×10:** κ_mm = 1.40, median G **+1.0 %** (CI 0.3–3.0 %), all runs ≥ 0.
- **The ×4 and ×16 maps below have never been run.** Their κ and G are unknown.

## 1. The map (SOURCED, not tuned)

**Cell.** SB LiMotive 5.2 Ah PHEV cell, 72 in series. SOURCED: dataset README, Naguib et al., Borealis
doi:10.5683/SP3/UYPYDJ.

**Primary cap: 6 C = 31.2 A at the map's plateau.**

- The dataset authors ran **"6C charge cycles"** on this pack in the thermal chamber at 15 °C and 25 °C (SOURCED:
  README §1).
- 6 C is therefore a charge rate the pack's owners applied, not a value fitted to our result.
- Implementation: H's C_T shape (plateau 1.5 C between 25 and 40 °C) is scaled by **qscale = 4.0**.

**Sensitivity cap: 125 A peak, qscale = 16.0.**

- 125 A is the "charge peak current" on an SB LiMotive automotive-cell slide (Kim, *SB LiMotive Automotive Battery
  Technology*), SOURCED.
- The slide does not tie that figure unambiguously to the 5.2 Ah cell, so it is a **sensitivity**, not the primary.

**Unchanged:**

- V_lim = 4.20 V. SOURCED from the same slide (4.2 V upper), and the same value as X2-M.
- Q_ref = 5.2 Ah.
- Everything else as in X2-M: sign I > 0 = charge, R steps |ΔI| ≥ 0.3 C, R re-estimated every 60 s, ≥ 20 steps for
  history, groups pooled by chamber temperature in file order, dead-thermistor rule, DEV-1 to DEV-3, κ grid
  1.00–2.00, unsafe ≤ 0.1 %.

## 2. Outcome and decision (as X2-M, pre-registered §4–§5)

**Outcome.** Per run, G = mean(L_cell,hist) / mean(L_mm,hist) − 1 over charge-direction frames, at the calibrated
κ_mm. The decision uses the median over the 14 runs with a run-level bootstrap (1,000 resamples, seed 0).

**Decision on the primary map (qscale 4.0):**

| Verdict | Condition |
|---|---|
| **RECOVERS X** | Median G ≥ 1 % **and** CI lower bound > 0 |
| **NO BENEFIT** | Median G < 1 % and the CI excludes 0 |
| **Descriptive** | The CI spans 0 |

**Reported alongside:**

- κ_mm and the κ curve;
- the fraction of frames where headroom binds;
- G per run and by chamber group;
- qscale 16.0 (sensitivity), and ×10 again for continuity, labelled POST-HOC.

**Figure (first-class output).** G and the unsafe fraction against κ, on twin axes, for each map.

## 3. Deviations

Any change after this commit is a numbered deviation. Thresholds are never moved.

**Licence:** CC BY 4.0.
