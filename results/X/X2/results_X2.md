# Results X2 (H3): per-cell limiting with per-cell parameters learned from history

Experiment X2, run 2026-10-15 (Changan arm finished 23:56 CDT).

- **Pre-registration:** [`../X2_preregistration.md`](../X2_preregistration.md), commit `0c4580a`. It was committed
  before any X2 code existed.
- **Code:** `analysis/X2_replay.py`, which reuses `H_replay` for C_T, the OCV table and the M1/M2 probe maps.
- **Outputs:** `x2_changan.json`, `x2_changan_sessions.npz`, `x2_mcmaster.json`,
  `x2_mcmaster_posthoc_qscale10.json` (POST-HOC), `x2_batss.json`, and `run_*.log`.
- **Tags:** every number below is **DERIVED** (a replay on MEASURED released telemetry). Every limit (C_T map,
  V_lim = 4.20 V, Q_ref, OCV table, probe mapping) is **ASSUMED**. This makes no claim about real charge rates.

## Verdict (pre-registered primary, §5)

**NO BENEFIT from per-cell history in the cold arm.**

| | X2-C cold (primary) |
|---|---|
| Sessions / vehicles | 2,855 / 130 |
| Sessions with ≥ 20 R-steps of history | **562**, which is ≥ 200, so **not** underpowered |
| Median S, M1 | **0.0 %** (vehicle bootstrap CI 0.0–0.0 %) |
| Median S, M2 (median over 100 maps) | **0.0 %** (5–95 % over maps: 0.0–0.0 %) |
| Mean S / p90 S | 0.16 % / 0.0 % |
| Cold sessions with history only: median / p90 | 0.0 % / 3.1 % |

The secondary pre-registered arm, **X2-C-all** (286,832 sessions, 300 vehicles), is also **NO BENEFIT**: median
S 0.0 %, p90 8.4 %, mean 1.9 %. The median is zero because 74 % of sessions have no history (see below).

## What the data does show (POST-HOC readings of pre-registered outputs)

**1. Where per-cell history exists and it is not cold, there is a consistent gain.**

| Subset (POST-HOC) | Sessions | Vehicles | Median S | Vehicle-bootstrap CI | p90 |
|---|---|---|---|---|---|
| All sessions with history | 75,905 | 290 | **+5.5 %** | 4.7–6.4 % | 17.7 % |
| Cold sessions with history | 562 | 34 | 0.0 % | 0.0–0.0 % | 3.1 % |

- Among sessions with history, the median of the per-vehicle medians is +6.8 %. **88 %** of vehicles have a
  per-vehicle median above 1 %.
- 72 % of these sessions gain something. 0.27 % lose, the worst by −21 %.
- The gain survives every pre-registered sensitivity (history-session median, each variant at its own κ):

| Variant | κ_mm | Sessions with history | Median S |
|---|---|---|---|
| W_R 7 days | 1.55 | 38,300 | +3.8 % |
| W_R 90 days | 1.70 | 156,931 | +6.9 % |
| Step 0.2 C | 1.70 | 129,681 | +7.4 % |
| Step 0.5 C | 1.70 | 53,319 | +5.7 % |
| C_T −5 °C | 1.70 | 75,905 | +6.1 % |
| C_T +5 °C | 1.65 | 75,905 | +4.8 % |

  Every one leaves the cold and all-session medians at 0.0 %, as do the κ tolerances of 0.01 % (κ capped at 2.00)
  and 1 % (κ 1.35).

**2. Why cold gives nothing: the cold sessions do not reach top of charge (probe, 2026-10-16; corrected).**

The first version of this section said the temperature cap binds in the cold. A follow-up probe shows the cause is
**charge depth**, not temperature. The probe is `analysis/X2_probe_depth.py`, base variant, M1, sessions with history only;
it is DERIVED.

| Sessions with history | n | Frames where some cell's headroom binds (median / mean) | Median of session-max Vmax |
|---|---|---|---|
| Cold (Tmin median < 10 °C) | 562 | **0 % / 17 %** | **3,951 mV** |
| Warm | 75,343 | 58 % / 44 % | 4,204 mV |

- Per-cell R can only change the limit where the **voltage-headroom** term binds, which is near the top of charge.
  (Correction: "binds in 67 % of all charge frames" counts frames where headroom binds for *some* cell, at any Vmax.
  It is not a Vmax ≥ 4.2 V figure.)
- The typical cold session with history is a **partial top-up** that stops about 250 mV below V_lim, so headroom
  never binds.
- So this data **does not show that history is useless in the cold**. It shows that this fleet's cold sessions rarely
  reach the regime where history acts. Cold is confounded with charge depth, and the cold question is still open.

**2b. Is the per-cell R structure real or estimation noise? (`analysis/X2_probe_splithalf.py`, 2026-10-16, DERIVED)**

- Over 289 vehicles with ≥ 80 qualifying steps (median 2,104 steps), per-cell median R_k was split two ways:

| Split | Spearman ρ across cells, median (p10) | Same worst cell in both halves |
|---|---|---|
| Interleaved | 0.98 (0.91) | 81 % |
| Early vs late half of the record | 0.94 (0.78) | 69 %; in the other half's top 5: 93 % |

- Worst cell / median cell R_k: median 1.20 (p90 1.46).
- So the cross-cell R pattern is **stable**, not noise.
- **Caveat:** ΔV/ΔI at the cell tap includes interconnect and busbar resistance. A stable "high-R cell" may be a
  wiring position, as with F's vin116 sense-tap. Its voltage error is real at the tap either way. Whether it is cell
  resistance is not known.

**3. Why the all-session median is zero: history is scarce.**

- A 30-day window holds a median of only 7 qualifying current steps (p10 0, p90 261).
- Only 26.5 % of sessions reach the pre-registered minimum of 20.
- The 90-day window doubles coverage to 156,931 sessions but still leaves the median at 0.

**4. What the gain is.**

- κ_mm = **1.65** was calibrated so that min/max is unsafe in at most 0.1 % of frames (0.099 %).
- The min/max limiter has to carry about 65 % R margin because it cannot know which cell is worst. The per-cell
  limiter does not need that margin, so the gain is the **price of not knowing**, measured at top of charge.
- **κ curve** (unsafe fraction against κ): 8.3 % at 1.00, 1.5 % at 1.30, 0.26 % at 1.50, 0.099 % at 1.65, 0.029 % at
  2.00.
- Control: the binding cell under per-cell is neither the max-V cell nor on an extreme probe in **3.0 %** of frames.
  In those frames, min/max structurally lacks the information.

**By temperature-spread band** (all sessions; the pre-registered bands):

| Band | Sessions | Median S | History-session median |
|---|---|---|---|
| 0–5 °C | 263,800 | 0.0 % | +5.7 % |
| 5–10 °C | 22,991 | 0.0 % | +3.1 % |
| 10–20 °C | 26 | 0.0 % | n = 1 |
| > 20 °C | 15 | 0.0 % | none |

The large-gradient regime is effectively absent from Changan, as found when drafting.

## Secondary: per-cell capacity Q_k (Changan)

- 41,029 sessions had ≥ 3 rest pairs. Median S is **−0.4 %**, with p90 12.9 %; cold median S is −0.5 % (n = 298).
- κ_mm hit the top of the grid (2.00) with **3.7 % unsafe frames**, so min/max could not be made equally safe.
  **Not calibrated, so not interpretable.**
- Per-cell Q_k barely varies: the median p95/p5 ratio within a pack is 1.025. That is close to the OCV-table
  resolution, so this arm says nothing either way.

## X2-M: McMaster 72S (CC BY 4.0)

- **As pre-registered:** G = 0 in all 14 runs, and κ_mm = 1.00 because no frame is unsafe at any κ. The verdict is
  "descriptive (CI spans 0)".
  - This is **structural**. H's C_T map at Q_ref = 5.2 Ah caps charge current at about 7.8 A. Regen pulses reach
    about 150 A, so the temperature cap always binds and headroom almost never does: 0–16 % of frames, and 0 % in
    10 of the 14 runs.
  - The pre-registered map is an energy-cell map. These are power cells.
- **POST-HOC, not a result** (`--mcm-qscale 10`, map ×10, chosen after seeing the above):
  - κ_mm = 1.40.
  - G median **+1.0 %**, run bootstrap CI 0.3–3.0 %, all 14 runs ≥ 0, and up to +5.0 % (HWCUST 15 °C).
  - This is directionally consistent with Changan's warm history sessions. It needs its own pre-registration before
    it can be cited.

## X2-B: BATSS fast charge (report-only, CC BY 4.0)

- S = 0 in all four runs (16–19).
- **Structurally uninformative.** Each fast-charge file begins with the charge itself, so there are no current steps
  beforehand. History never exists, and under DEV-3 both limiters are then the same.
- The runs do reach the regime the brief wanted: Tmax 39–79 °C, median spread 13–41 °C. But the
  thermocouple-to-cell mapping is ASSUMED.

## Deviations (after `0c4580a`)

1. **DEV-1: κ is applied in its conservative direction per frame.**
   - The pre-registration wrote R_mm·κ, assuming a larger R is always safer.
   - But `I_adm = I + (V_lim − Vmax)/R` *increases* with R when Vmax > V_lim, and 27 % of Changan charge frames have
     measured Vmax > 4.20 V.
   - So R·κ is used below the limit and R/κ above it.
2. **DEV-2: both limiters are floored at 0.05 C·Q_ref, H's taper floor.**
   - Without it, any frame whose open-circuit estimate is at or above V_lim gives L = 0, and t = Σ dAh/L is dominated
     by those frames.
   - Applied identically to both limiters.
3. **DEV-3: without history, the per-cell limiter gets min/max's uniform R and κ.**
   - Without per-cell history there is no per-cell R. Giving the per-cell limiter the bare pack R without margin would
     hand it a free advantage.
   - Its only possible edge is then the temperature mapping, as in H.

**Clarification (not a deviation).** r = ΔV/ΔI with charge-positive current. The pre-registration's "−ΔV/ΔI" was
written for discharge-positive current, before sign normalisation.

## Implementation choices the pre-registration left open

| | Choice |
|---|---|
| OPEN-1 | A step means consecutive full frames ≤ 30 s apart |
| OPEN-2 | R = 0.5 mΩ placeholder when a window has zero steps. Those sessions are "no history" and fall under DEV-3. |
| OPEN-3 | Q_ref = 120 Ah for Changan (fleet fast-charge label median about 120–126 Ah) |
| OPEN-4 | A rest is \|I\| < 1 A continuously for > 1 h, with gaps ≤ 60 s. Rest-pair ΔSOC ≥ 20 %. |
| OPEN-5 | McMaster R re-estimated every 60 s from steps strictly before |

All were fixed in the code before any result was read.

## What this does and does not show

**Does:**

- In the pre-registered cold arm, **per-cell history does not change the charge limit**. That is because the cold
  sessions are partial top-ups that never reach the headroom regime (§2, corrected), not because of temperature.
- Where history exists and the pack is warm, a history-derived per-cell R would let a limiter run a median **+5.5 %**
  faster (POST-HOC) than an equally safe min/max. This holds across vehicles and all sensitivities.

**Does not:**

- No fleet-level claim. History at the pre-registered threshold exists for only 26 % of sessions.
- No real charge-time claim. Every limit is ASSUMED, and +5.5 % is relative to a replay limiter, not a production BMS.
- Nothing about large gradients. No dataset in hand has them with known mapping.
- Nothing about cold charging to full. Too few cold sessions reach top of charge.
- No independent confirmation is possible with the data in hand.
  - Every Changan session has been seen.
  - Weihai (CC BY) charge sessions contain essentially no current steps: 10 steps ≥ 0.3 C in 85,270 sampled frames
    (probe, 2026-10-16). Per-cell R cannot be learned from them.

**If pursued.**

- Stratify by **charge depth** (session-max Vmax), not by temperature.
- A confirmatory test needs **new data**. A re-run on Changan would be a re-specification, not a confirmation.
- Pre-register a datasheet-based power-cell map for McMaster.

**Board.** None. The primary verdict is NO BENEFIT, so §7 is not triggered.

**Licences:** X2-C (Changan) is **CC BY-NC-SA 4.0, non-commercial**. X2-M and X2-B are CC BY 4.0.

## Addendum (2026-10-28): X2-C does not confirm the +5.5 %

See [`../X2C/results_X2C.md`](../X2C/results_X2C.md). The pre-registered confirmation ran on new data: Beihang QAS,
CC BY 4.0, with κ calibrated on held-out vehicles.

- **Verdict: NOT INTERPRETABLE.** Held-out unsafe frames were 0.24 %, against a bar of 0.2 %.
- **The shuffle control failed.** Assigning each cell another cell's R gave a **larger** S than the true assignment:
  11.7 % against 10.8 %.
- **So the comparison in this file rewards the per-cell limiter's lack of margin, not knowledge of which cell is
  worst.** The +5.5 % above should be read as margin asymmetry. X2 itself ran no shuffle control.

### Shuffle diagnostic on Changan (2026-10-28, POST-HOC, seen data)

Run at Kyle's request after X2-C. Code: `analysis/X2_shuffle_diag.py`. Output: `x2_shuffle_diag.json`. It re-scores
the subset above (all sessions with history) at X2's κ_mm 1.65, M1 mapping, with each vehicle's R_k vector permuted
once (`default_rng(car)`), exactly as X2-C did. All numbers are **DERIVED**; limits are **ASSUMED**. It is a
diagnostic on data already seen, not a test.

| All sessions with history (75,905 sessions, 290 vehicles) | Median S | Vehicle-bootstrap CI |
|---|---|---|
| Real per-cell R (reproduces the +5.5 % above exactly) | **+5.5 %** | 4.7–6.4 % |
| **R_k shuffled across cells** | **+6.0 %** | 5.2–6.7 % |
| Paired, real minus shuffled | **0.0 pp** | 0.0–0.0 |

- The shuffled limiter exceeds the true per-cell limiter in **30 %** of frames, yet gains as much or more.
- Warm sessions: 5.6 % real against 6.1 % shuffled. Cold sessions: 0 % for both.
- **The +5.5 % is margin asymmetry, as X2-C indicated.** Knowing which cell has which R contributes nothing measurable
  in this comparison.
