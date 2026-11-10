# Results X8: the bottom reserve. Does per-cell R admit more low-SOC discharge current than min/max at equal held-out safety?

Experiment X8, run 2026-11-10.

| | |
|---|---|
| **Pre-registration** | [`../X8_preregistration.md`](../X8_preregistration.md), commit `600b296`, before any limiter code; approved without changes 2026-11-10 |
| **Profile** | [`../X8_profile.md`](../X8_profile.md) |
| **Code** | `analysis/X8_bottom.py` (pre-registered run); `analysis/X8_diag.py` (exploratory, written after the results, decides nothing) |
| **Outputs** | `x8.json`, `x8_margin_table.json`, `x8_diag.json`, `x8_kappa_and_session.png`, `x8_S_distribution.png`, `run.log` |
| **Tags** | Every number is **DERIVED** (replay). V_cut, 1 C and every limit are **ASSUMED**. These are replay admissible currents (estimated headroom), not discharge ratings. No kWh, range, cost or C2 percentage. |

**Changan caveat (on every Changan number):** *Changan, CC BY-NC-SA 4.0, research only; NMC; 10 s telemetry;
warm-climate fleet; the limits are ASSUMED replay quantities.* Beihang DTI and QAS are CC BY 4.0 and citable.

---

## Verdicts (pre-registered §6)

| Arm | Verdict | Why |
|---|---|---|
| **Changan (primary)** | **NOT INTERPRETABLE** | Min/max cannot be calibrated: even at κ = 2.00 it is unsafe on 0.061 % / 0.079 % of calibration frames (bar 0.05 %), flagged in both directions. Per-cell and shuffled pass held-out safety (0.036–0.064 %, bar 0.2 %). |
| **Beihang DTI** (NMC) | **NOT INTERPRETABLE** | All three limiters flagged at κ = 2.00 in both directions; held-out unsafe 0.38–0.67 % (per-cell), 1.97–2.32 % (min/max). |
| **Beihang QAS** (LFP) | **NOT INTERPRETABLE**, effectively underpowered | Min/max flagged in one direction by a **single frame** (1 of 741 = 0.135 %). Only 19 vehicles carry ≥ 20 scored frames once history is counted per session (the profile counted 32 per frame); 1,402 frames in all. |

No dither "rounding" label applies on any arm (below). **X8 does not establish whether per-cell R admits more current
at the bottom than min/max**, because min/max cannot be made safe on the pre-registered grid.

**What it is a ratio of (APPROVED-box note 2).** Every admissible current here is **estimated headroom**, not
current a driver would draw. The median reference admits **317 A ≈ 2.6 C** on Changan (DTI 13 C, with V_cut 2.90 V)
against a fleet p95 demand of 0.65 C. In **96–97 % of Changan sessions** no limiter's admissible current ever fell below
the session's own p95 demand (usable-depth readout). S, if it could be read, would be a ratio of estimated headroom at
the bottom; it is not a discharge-rate or usable-energy gain.

---

## The margins (the reading that mattered in X2-F)

Unsafe frames against the independent per-cell reference, % calibration / held-out, Changan A→B (B→A mirrors it; full
table for every arm and direction in `x8_margin_table.json`):

| Limiter (κ chosen) | κ 1.10 | κ 1.20 | κ 1.30 | κ 1.40 | κ 1.50 | κ 1.75 | κ 2.00 |
|---|---|---|---|---|---|---|---|
| **Per-cell** (1.80; B→A 1.95) | 4.5 / 4.6 | 1.1 / 1.1 | 0.43 / 0.47 | 0.22 / 0.25 | 0.13 / 0.15 | 0.055 / 0.071 | 0.034 / 0.047 |
| **Shuffled** (1.85; B→A 2.00) | 11.0 / 10.7 | 1.9 / 1.9 | 0.59 / 0.63 | 0.27 / 0.31 | 0.16 / 0.18 | 0.063 / 0.078 | 0.037 / 0.050 |
| **Min/max** (2.00, flagged) | 67.9 / 69.1 | 45.4 / 46.7 | 19.9 / 20.7 | 4.7 / 6.0 | 1.5 / 2.1 | 0.27 / 0.19 | **0.061 / 0.079** |

- **Ordering per-cell < shuffled < min/max at every κ, both halves, both directions** — the same ordering X2-F found
  at the top of charge. At κ 1.50 min/max is unsafe about 10× as often as per-cell.
- **Every limiter needs a far larger margin at the bottom than at the top.** X2-F's per-cell limiter needed κ ≈ 1.10;
  here it needs 1.80–1.95. Min/max needed 1.35–1.45 at the top; here it does not get under the bar by 2.00.
- **Where min/max can be calibrated** (sensitivities V_cut − 50 mV and the 0.1 % bar), it needs κ **1.86–1.92**,
  per-cell **1.50–1.63**, shuffled 1.54–1.66. Min/max's margin transferred to the held-out half in both of those
  (0.032–0.119 % held-out). Per-cell's advantage is the R **spread** (taking the worst cell's own R), not the cell
  identity: the shuffle needs only 0.03–0.04 more κ.
- **The binding cell.** The per-cell limiter's binding cell is not the present minimum-voltage cell on **73 %** of
  Changan scored frames (DTI 76 %, QAS 72 %), matching the profile (the min-V cell is the highest-R cell in a median
  2 % of frames).

## If the Changan numbers were read anyway (not a verdict)

| Changan, both directions averaged | Median | Vehicle-bootstrap 95 % CI |
|---|---|---|
| S (per-cell vs min/max) | −8.4 % | −10.1 to −5.9 % |
| S_sh (shuffled vs min/max) | −8.5 % | |
| **D = S − S_sh**, paired | **+1.13 pp** | +0.93 to +1.30 pp |
| S_ref (margin-free per-cell reference, ceiling) | +71.6 % | |

S is negative because min/max, still unsafe at κ 2.00, is being given credit for admitting more than its safe share;
the comparison is not at equal safety, which is why the pre-registration makes it NOT INTERPRETABLE. D is the only
like-for-like quantity and it is small (≈ 1 pp) and positive.

Subsets, same κ (non-deciding): SOC < 10 % (295 vehicles) S −5.4 % [−7.6, −2.6], D +1.0 pp [0.7, 1.3]; cold
(204 vehicles) S −5.8 % [−8.6, −2.6], D +0.3 pp [−0.04, 0.74].

## The three APPROVED-box expectations, answered

1. **Zero-reference frames.** On Changan, frames where I_ref = 0 while a limiter issues > 0 are **0.012–0.013 %** of
   scored frames, **below** the 0.05 % calibration bar, so they alone did **not** drive NOT INTERPRETABLE. They are 16–19 %
   of min/max's residual unsafe frames at κ 2.00 (24–28 % of per-cell's); the rest sit at a median reference of ≈ 99 A (≈ 0.8 C), i.e. ordinary
   headroom (exploratory, `x8_diag.json`). On **DTI** they are **0.062 %**, above the bar: there, zero-reference
   frames alone make the 0.05 % calibration unreachable for every limiter — X8's version of X7's resolution ceiling,
   on that arm. On QAS there are none.
2. **Headroom, not realised current.** Stated in the verdict paragraph: median reference 2.6 C on Changan against a
   p95 demand of 0.65 C; 96–97 % of sessions never bind on demand.
3. **The dither check (binding).** Changan S moved by **−0.44 pp** under ±0.5 LSB dither against a CI width of
   **4.2 pp**; DTI −0.28 against 6.7; QAS −0.14 against 3.9. **No "rounding" label.** But the mechanism quantity is
   rounding-sensitive: Changan **D fell from +1.13 pp [0.93, 1.30] to +0.69 pp [0.50, 0.85]**, non-overlapping CIs.
   About 40 % of the per-cell-over-shuffled advantage is at the level of the 1 mV quantisation.

## Sensitivities (κ recalibrated each time; none deciding)

| Changan variant | Same-rules reading | S | S_sh | D |
|---|---|---|---|---|
| Base | NOT INTERPRETABLE | −8.4 % | −8.5 % | +1.1 pp |
| V_cut 3,300 mV | **PER-CELL HELPS AT THE BOTTOM** | **+3.6 % [1.8, 6.5]** | +3.4 % | **+1.2 pp [1.0, 1.3]** |
| V_cut 3,400 mV | NOT INTERPRETABLE (all flagged) | −12.2 % | −9.5 % | −1.5 pp |
| Horizon 20 s | NOT INTERPRETABLE (all flagged) | −14.2 % | −12.0 % | −1.2 pp |
| R held from the first 20 + 20 steps | NOT INTERPRETABLE | −14.7 % | −14.2 % | +0.1 pp |
| Calibration bar 0.1 % | NO BENEFIT (S_sh ≥ S) | +1.4 % [−0.6, 4.3] | +1.7 % | +0.8 pp |
| Calibration bar 0.5 % | NOT INTERPRETABLE (held-out 0.29–0.69 %) | +8.8 % | +8.6 % | +1.4 pp |
| Dither ±0.5 LSB | NOT INTERPRETABLE | −8.8 % | −8.4 % | +0.7 pp |

The one variant that reads PER-CELL HELPS (V_cut − 50 mV) is the one that moves V_cut away from the tail of observed
minima, where min/max becomes calibratable. A moving cut-off flips the reading; the pre-registered V_cut does not
move (§9), and the result is reported as fragile, not positive.

**DTI** reads NOT INTERPRETABLE in every variant (S −7.6 to −13.8 %, D −0.6 to +1.1 pp). **QAS** reads NOT INTERPRETABLE
or NO BENEFIT in every variant; its shuffled limiter beats the real one in every variant but the 0.5 % bar (D −1.7 to −3.2 pp, base
−2.8 pp [−3.6, −2.3]; +1.4 pp at the 0.5 % bar) on 1,402 frames of LFP, where V + I·R is a poor OCV estimator on a flat curve.

## Counts

| | Changan | DTI | QAS |
|---|---|---|---|
| Vehicles scored | 300 | 49 (45 with ≥ 20 frames) | 30 (19 with ≥ 20 frames) |
| History sessions / scored frames | 502,096 / 5,449,916 | 1,728 / 16,009 | 145 / 1,402 |
| Sessions excluded, no history | 2,005 | 245 | 171 |
| Frames with I_ref = 0 (horizon) | 0.24 % | 0.16 % | 0 |
| V_cut (ASSUMED) | 3,350 mV | 2,900 mV | 2,840 mV |

## What this says

- **At the bottom, every limiter needs a large margin** against an independent per-cell reference (κ 1.5–2.0 against
  X2-F's 1.10–1.45 at the top). Near V_cut the headroom is small and a small R error is a large relative error.
- **Min/max is the worst of the three at every margin**, and on the pre-registered settings it cannot be made safe by
  κ 2.00. Per-cell knowledge cuts the margin needed by about 0.3 κ where min/max can be calibrated at all.
- **Most of that comes from the R spread, not the cell identity**: a shuffled per-cell limiter is almost as good
  (D ≈ +1 pp on Changan, of which ≈ 40 % is quantisation; negative on DTI and QAS).
- **The bottom reserve is not demand-limited in this fleet**: the estimated headroom exceeds the fleet's p95 demand in
  96–97 % of sessions, so a larger admissible current at low SOC would rarely be used.

---

*Changan CC BY-NC-SA 4.0, research only; NMC; 10 s telemetry; warm-climate fleet; limits ASSUMED. Beihang CC BY 4.0.*
