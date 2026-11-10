# Synthesis — the open-problem pass after five experiments

**Written:** 2026-11-10, after X8. **Scope:** what [`ANGLES_REPORT.md`](ANGLES_REPORT.md) (2026-10-30) proposed, what
the five experiments that followed established, and where the question now stands. **Licence:** public domain (CC0);
the licence of each cited result is carried with it. Every number here is quoted from a write-up that states its tags;
nothing new is computed.

## 0. The question, and the answer so far

The customer's claim set (C1–C6) says an application-processor part with DRAM beats an MCU for battery charging and
800 V → 48 V power conversion. The open-problem pass asked what, specifically, the DRAM tier does that an MCU with
SDRAM or HyperRAM and factory calibration cannot.

**After five experiments the answer the evidence supports is the null stated in ANGLES §E, in its positive form:**

> The battery and converter computations the programme can test are MCU-class, and per-vehicle learning does not beat a
> fleet model on them. The DRAM tier's physically necessary capability — a continuous MB/s ring buffer — is now
> MEASURED on the board, but the public record shows its forensic value as a rare, event-triggered need rather than a
> recurring one. What remains Tier-A-specific is **software**: the regulation-driven stack the battery/charging box must
> host anyway, and the option value of hosting it in isolated, updatable domains. The DRAM is sized by that stack. The
> battery and converter intelligence is upside that an already-present A-core makes free.

That is a stronger roadmap position than the one the programme started with, because every leg of it is either
measured or explicitly documentary, and the counter-evidence is on the table.

## 1. Scoreboard

| ID | Question | Verdict | Slide-usable? | What it changed |
|---|---|---|---|---|
| **X7** | Does a per-cell thermal observer remove hottest-cell margin that probe interpolation carries? | **UNDERPOWERED** at profile (1 K thermistors; probe-max never > 1 K below T_hot) | n/a (McMaster CC BY, but no result) | Mechanism untestable on public data; lesson: resolution belongs in the gate |
| **B1** | Can the board hold a 3–60 MB/s ring in LPDDR, freeze and dump it, without disturbing real-time work? | **MEASURED**: 0 drops at 3.2/32/60 MB/s; 2 GB holds 671/67/36 s; 26/26 dumps verified; RT loops within 6.3 %; eMMC as ring medium wears out in 0.05–0.95 y (endurance ASSUMED) | **Yes** (own board; CPU producer = upper bound on DMA) | The one Tier-A capability number an MCU cannot match |
| **DC1** | Does forecasting with seconds of history cut rack-side storage for synchronous-AI swings? | **REACTIVE SUFFICES** both workloads (G 1.02, 1.00); **NO HISTORY NEEDED** (1 s ramp detector matches 30 s); ceiling 1.38× exists | **Yes** (NLR CC BY 4.0; node-level 5 Hz caveat) | Anticipation leg of §B.2 not supported; the violation budget decides this class of result |
| **FR1** | How long a pre-event window do public HV power-electronics root causes need? | **UNGATED** (κ 0.19; scheme lacked a "not observable" state). Exploratory: of causes field data could show, ½ need > 80 s, ¾ > 1 s, but the windows are mostly 1–10 Hz over sessions/cycles/days; ≥ kHz in 4–6 of 36 | Partly (NHTSA public domain; UNGATED, so direction only) | DRAM retention: supported as event-triggered capture (ICCU class), not as a recurring need |
| **X8** | Does per-cell R admit more low-SOC discharge current than min/max at equal safety? | **NOT INTERPRETABLE** ×3 (min/max cannot be made safe at κ 2.00). Readings: per-cell < shuffled < min/max at every κ; the per-cell edge over shuffled is ≈ 1 pp and 40 % quantisation; bottom reserve not demand-limited (96–97 % of sessions never bind) | Changan **no** (NC-SA); Beihang DTI/QAS **yes** (CC BY), both NOT INTERPRETABLE | C2-as-power-reserve not supported in these fleets; the gain is R *spread*, which an MCU can carry as a max-R table |

Earlier, from the programme proper: **X2-F** (per-cell R is stable and removes margin at the top of charge: κ 1.10 vs
1.35–1.45, min/max's margin does not transfer) and **X5/X6** (per-vehicle history does not beat a frozen fleet model on
usable energy; knees set the reserve) stand unchanged.

## 2. What stands (usable, with its licence)

1. **The ring buffer is real and measured** (B1, own board). Window by medium at 3.2 MB/s: MCU freeze-frame ~1 s;
   HyperRAM 40 s and MCU + 256 MB SDRAM 80 s (DERIVED); 2 GB LPDDR **671 s measured**. Flash cannot be the rolling
   medium at any of these rates for a vehicle life.
2. **Per-cell resistance is a stable, identifiable property at both ends of the SOC range** (X2-F at the top; X8
   profile at the bottom, split-half ρ 0.995), and **a limiter that knows the R spread needs a smaller margin than
   min/max with a pack-level R** (X2-F; X8 margin table, every κ, every arm).
3. **Pre-positioning room exists at the rack** (DC1 ceiling ≈ 1.38× less storage with 5 s of foresight) — the causal
   predictor, not the mechanism, is what fails; the result flips at a 5× looser violation budget.
4. **The costliest public power-electronics campaign in the FR1 list (the ICCU pair) is rated by both raters as needing
   a kHz capture at end of charge plus a long low-rate history** — the one public case shaped like a flight recorder.
5. **Regulatory volatility of the battery/charging box** (five software-visible regimes in ~8 years; ANGLES §B.1) is
   the mechanism that explains *why some designs need Tier A and most do not*. It is documentary and **untested** (L1).

## 3. What fell — the counter-evidence, stated plainly

| Claim | Status | Evidence |
|---|---|---|
| Battery analytics need a working set beyond an MCU | **Refuted** | 220 KB model, 10 B per cell, 1.5–52 µs limiters (Study 1, H, H2) |
| Per-vehicle / per-unit learning beats a fleet model | **Refuted (battery)** | Studies 1–2, X5, X6: knees, not estimation error, set the reserve |
| Converter efficiency needs a history-fed model | **Refuted (within the model family)** | convsim: static table within 1 %; holds under 100× hard-switching stress |
| Anticipation at the rack needs seconds of history | **Not supported** | DC1: a 1 s ramp detector matches 30 s of history; reactive suffices at 0.1 % budget |
| Per-cell *identity* (not just R spread) carries the limiter gain | **Not supported** | X8: shuffled per-cell is within ≈ 1 pp of per-cell; 40 % of that is 1 mV quantisation. **An MCU min/max limiter with a max-R table captures most of the gain** |
| A bottom power-capability reserve is there to release | **Not supported in these fleets** | X8: estimated headroom exceeds p95 demand in 96–97 % of sessions |
| Thermal margin from a per-cell observer | **Untestable on public data** | X7 |
| DRAM retention is a recurring forensic necessity | **Not supported** (UNGATED) | FR1: the long windows named are mostly slow (1–10 Hz); flash/cloud-class |

The second-to-last row is new and matters for the MCU-tier story: the cheapest fix to min/max is not per-cell
telemetry, it is carrying the pack's **worst-cell resistance** in the limiter — bytes, not DRAM.

## 4. The revised position, claim by claim

| Customer claim | What the evidence says | How to say it |
|---|---|---|
| **C1** 1 °C cooler charging ≈ $100 | lifecost: $58/K (p50, ASSUMED inputs); mechanism untested (X7) | Value plausible; mechanism not demonstrated on public data |
| **C2** 20 % reserve → 5 % | Not as estimation precision (X5/X6); not as bottom power capability (X8); top-of-charge plating margin untested (S3) | The reserve is set by knees and by policy; no public evidence that per-vehicle data releases it |
| **C3** ECU consolidation | lifecost $148 (p50, ASSUMED) | Real, and the strongest *measured-cost* leg; tier-defining when the box must host Linux-class software (C5) |
| **C4** small NN beside the µs loop beats static tables | convsim: no, within the model family; R-spread limiter: yes, but MCU-class | Ask which quantity the NN sets (§D's question); most candidates are tables |
| **C5** MCU would cost more than MPU + DDR | True as a *marginal* statement once the A-core is required for software | Lead with this; it is the honest form of the thesis |
| **C6** converter benefit from history | Not supported (convsim; DC1) | Keep as upside with kill criteria; do not lead with it |

## 5. What would still move the position

- **L1 — requirement-arrival ledger** (ANGLES §C.1): documentary, the evidence for §B.1, the only Tier-A-specific leg
  left standing. Runnable in any session with web access.
- **FR1-R — re-rate with a six-state scheme** on the already-fetched documents: converts UNGATED into a gated fraction
  on the retention leg; one session-day per rater.
- **DC2 — spec audit**: what compliance window and excursion allowance real large-load ramp specs use; decides whether
  DC1's sensitivity (history pays at a 0.5 % budget) is the real-world case.
- **Customer data asks** (public data cannot reach these): a phase-level (≥ 1 kHz) rack power trace; per-unit field
  drift of converter envelope parameters over life; the OEM's last twenty root-cause reports with the pre-event window
  each needed.
- **O1 / R1** (code; tier-neutral or secondary): close the audit items; test learned telemetry reduction under a budget.

## 6. Licence map for anything customer-facing

Usable: B1 (own board), DC1 (NLR CC BY 4.0), McMaster-based profiles (CC BY 4.0), Beihang arms (CC BY 4.0), NHTSA
material (public domain, FR1 direction only while UNGATED), convsim and lifecost (own models, ASSUMED inputs stated).
**Not usable:** anything computed on Changan (CC BY-NC-SA 4.0), which includes X8's primary, X2-F's primary and the
Study 2 fleet results — these direct where a licensed test should look; they do not go on a slide.
