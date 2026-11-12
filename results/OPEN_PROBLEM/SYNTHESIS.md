# Synthesis — the open-problem pass after ten experiments (close-out)

**Written:** 2026-11-10, after X8; refreshed after FR1-R and L1; **close-out 2026-11-11** after DC2 and DC2-R, the last legs;
L1b (2026-11-12, UNGATED) added after the close-out and moves nothing.
**Scope:** what [`ANGLES_REPORT.md`](ANGLES_REPORT.md) (2026-10-30) proposed, what the ten experiments that followed
established, and where the question now stands. **Licence:** public domain (CC0); the licence of each cited result is
carried with it. Every number here is quoted from a write-up that states its tags; nothing new is computed.

## 0. The question, and the answer so far

The customer's claim set (C1–C6) says an application-processor part with DRAM beats an MCU for battery charging and
800 V → 48 V power conversion. The open-problem pass asked what, specifically, the DRAM tier does that an MCU with
SDRAM or HyperRAM and factory calibration cannot.

**After ten experiments the answer the evidence supports is the null stated in ANGLES §E, in its positive form:**

> The battery and converter computations the programme can test are MCU-class, and per-vehicle learning does not beat a
> fleet model on them. The DRAM tier's physically necessary capability — a continuous MB/s ring buffer — is MEASURED on
> the board, and the public record (now gated) shows its forensic value as an event-triggered need in the charging path,
> about one public root cause in six, not a recurring one. What remains Tier-A-specific is **software**: the
> regulation-driven stack the battery/charging box must host anyway, and the option value of hosting it in isolated,
> updatable domains. L1 has now counted that regulation: 35 sourced events in eleven years, 3.2 a year and accelerating,
> of which the ones that force the stack are the cyber-security, software-update and EU energy-data acts — a handful of
> large acts, not the drizzle. The DRAM is sized by that stack. The battery and converter intelligence is upside that an
> already-present A-core makes free. On the data-centre side, DC1 and DC2 together leave the anticipation leg without
> support: a reactive controller holds public training swings inside a ramp spec as well as one with seconds of
> history, and no public specification was found with the slack, sub-minute shape in which history would have paid.

That is a stronger roadmap position than the one the programme started with, because every leg of it is either
measured, gated, or explicitly documentary, and the counter-evidence is on the table.

## 1. Scoreboard

| ID | Question | Verdict | Slide-usable? | What it changed |
|---|---|---|---|---|
| **X7** | Does a per-cell thermal observer remove hottest-cell margin that probe interpolation carries? | **UNDERPOWERED** at profile (1 K thermistors; probe-max never > 1 K below T_hot) | n/a (McMaster CC BY, but no result) | Mechanism untestable on public data; lesson: resolution belongs in the gate |
| **B1** | Can the board hold a 3–60 MB/s ring in LPDDR, freeze and dump it, without disturbing real-time work? | **MEASURED**: 0 drops at 3.2/32/60 MB/s; 2 GB holds 671/67/36 s; 26/26 dumps verified; RT loops within 6.3 %; eMMC as ring medium wears out in 0.05–0.95 y (endurance ASSUMED) | **Yes** (own board; CPU producer = upper bound on DMA) | The one Tier-A capability number an MCU cannot match |
| **DC1** | Does forecasting with seconds of history cut rack-side storage for synchronous-AI swings? | **REACTIVE SUFFICES** both workloads (G 1.02, 1.00); **NO HISTORY NEEDED** (1 s ramp detector matches 30 s); ceiling 1.38× exists | **Yes** (NLR CC BY 4.0; node-level 5 Hz caveat) | Anticipation leg of §B.2 not supported; the violation budget decides this class of result |
| **FR1** | How long a pre-event window do public HV power-electronics root causes need? | **UNGATED** (κ 0.19; scheme lacked a "not observable" state). Exploratory: of causes field data could show, ½ need > 80 s, ¾ > 1 s, but the windows are mostly 1–10 Hz over sessions/cycles/days; ≥ kHz in 4–6 of 36 | Partly (NHTSA public domain; UNGATED, so direction only) | Exposed the scheme defect; superseded by FR1-R |
| **X8** | Does per-cell R admit more low-SOC discharge current than min/max at equal safety? | **NOT INTERPRETABLE** ×3 (min/max cannot be made safe at κ 2.00). Readings: per-cell < shuffled < min/max at every κ; the per-cell edge over shuffled is ≈ 1 pp and 40 % quantisation; bottom reserve not demand-limited (96–97 % of sessions never bind) | Changan **no** (NC-SA); Beihang DTI/QAS **yes** (CC BY), both NOT INTERPRETABLE | C2-as-power-reserve not supported in these fleets; the gain is R *spread*, which an MCU can carry as a max-R table |
| **FR1-R** | FR1 re-rated with a `not observable` state and a closed data-rate list | **Gated (κ 0.90), retention UNCLEAR, shape MIXED.** P80 31 % [19, 48] and ring-buffer-shaped 17 % [8, 33] of 35 field-observable in-scope causes; 17 of 53 in-scope causes not observable at any window; long windows are mostly per-event signatures over many cycles; ring-buffer needs concentrate in the charging path (the ICCU pair) | **Yes** (NHTSA public domain; DERIVED-judgemental, two language-model raters) | DRAM retention stands as an event-triggered capture for about one public cause in six, not a necessity |
| **L1** | How often do software-visible requirements land on the battery / charging ECU domain, against seats? | **UNCLEAR [V1: VOLATILE]** (gated: identification 0.84, κ 0.82; kill does not fire). 35 matched events 2016–2026, 3.2 / yr, 22 in 2023–25; MC 38 % [22, 57] of 26 judged; battery / seat ratio 2.2 with R155 / R156 / GB 44495 / GB 44496 on both sides (L-1), 4.4 / 3.4 without; N_B a floor (10 SAE instruments unreadable) | **Yes** (public regulatory record; DERIVED-judgemental, two language-model raters) | §B.1's arrival process is counted and real; its excess over a quiet domain is 2–4×, not "no such process elsewhere"; the stack-forcing events are five large acts |
| **DC2** | What window and excursion allowance do real large-load power specs use; is any shaped so that seconds of history would pay? | **UNGATED** (identification 0.52 < 0.80; κ(window) 0.64). Exploratory: binding real-power-variation limits found are `hard`, except ERCOT §6.5.7.11 (PCLR ramp, one-minute intervals, 10 % may fail), read identically by both raters; gray-boxed, registration-scoped, at the 60 s class edge | No (UNGATED; public documents, DERIVED-judgemental) | The last data-centre leg gets no reading; no spec found that makes DC1's 0.5 % sensitivity the real case |
| **DC2-R** | DC2 re-rated by two fresh raters with row granularity fixed in advance | **UNGATED** (identification 0.72 < 0.80, now on coverage of very large documents; κ(window) 1.00; deciding-row identification 0.81; every class of all 23 binding-deciding pairs agreed). Same picture: every binding real-power-variation limit `hard` or no window stated, except ERCOT §6.5.7.11 (PCLR, one-minute averages, 10 % may fail) | No (UNGATED; documentary) | Four raters in two blind pairs reproduce the reading; DC1b not run (pre-declared); the anticipation leg closes on public evidence |
| **L1b** | Against exterior lighting, is the battery domain's requirement arrival specific in count, and in kind (acts forcing the crypto / update / data / telemetry stack)? | **UNGATED** both (identification 0.60, κ classes 0.38; κ `stack` 1.00). Calibrated. Ungated: R_BL 0.73 [0.47, 1.12]; stack B 16 / 27 vs L 0 / 40, S 0 / 6 | No (UNGATED; public regulatory record, DERIVED-judgemental) | No reading. Ungated, the count form of §B.1 looks weaker than L1 and the kind form stronger; see the note under §3 |

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
   a kHz capture at end of charge plus a long low-rate history** — the one public case shaped like a flight recorder;
   FR1-R puts that shape at 17 % [8, 33] of field-observable in-scope causes.
5. **Regulatory arrival on the battery/charging box is counted** (L1, [`../L1/results_L1.md`](../L1/results_L1.md)):
   35 dated, sourced events in 2016–2026 from UN R100 / R155 / R156 / GTR 22, the EU Batteries Regulation and Euro 7,
   GB/T 32960 and GB/T 27930, IEC 61851 and FMVSS 305 / 305a, reproducible between two blind raters. 38 % [22, 57] of
   the judged events are above `software-only` under the pre-registered class order, which puts re-approval-by-date in
   the top class. The reviewer's exploratory split (`../L1/review/README.md`) finds the events that name a
   cryptographic, update, data-access, retention or telemetry requirement to be **five large acts — UN R155 (2020), UN
   R156 (2020), the Batteries Regulation (2023), Euro 7 (2024) and its OBM / OTA implementing act (2025)** — 19 % [9,
   38] of judged events; the rest are supplements, warning functions, scope extensions and re-approvals. **This is the
   mechanism of ANGLES §B.1 with its size now known: the stack is forced by a few acts per decade, and the drizzle
   around them is software.**

## 3. What fell — the counter-evidence, stated plainly

| Claim | Status | Evidence |
|---|---|---|
| Battery analytics need a working set beyond an MCU | **Refuted** | 220 KB model, 10 B per cell, 1.5–52 µs limiters (Study 1, H, H2) |
| Per-vehicle / per-unit learning beats a fleet model | **Refuted (battery)** | Studies 1–2, X5, X6: knees, not estimation error, set the reserve |
| Converter efficiency needs a history-fed model | **Refuted (within the model family)** | convsim: static table within 1 %; holds under 100× hard-switching stress |
| Anticipation at the rack needs seconds of history | **Not supported** | DC1: a 1 s ramp detector matches 30 s of history; reactive suffices at 0.1 % budget |
| A real spec has the slack, sub-minute shape where history would pay | **Not found** (DC2 and DC2-R both UNGATED on identification; documentary reading reproduced by four raters) | 56 instruments read twice: every binding limit on real-power variation either rater found is a hard limit (Fingrid oscillation bands and ramp / step at the POI, AESO ramp / step, OCP sub-100 ms envelopes), except an ERCOT curtailment-dispatch rule on one-minute averages that does not see the swings |
| Per-cell *identity* (not just R spread) carries the limiter gain | **Not supported** | X8: shuffled per-cell is within ≈ 1 pp of per-cell; 40 % of that is 1 mV quantisation. **An MCU min/max limiter with a max-R table captures most of the gain** |
| A bottom power-capability reserve is there to release | **Not supported in these fleets** | X8: estimated headroom exceeds p95 demand in 96–97 % of sessions |
| Thermal margin from a per-cell observer | **Untestable on public data** | X7 |
| DRAM retention is a recurring forensic necessity | **Not supported** (gated) | FR1-R: 31 % of field-observable causes need > 80 s, but the long windows are per-event signatures over many cycles (flash/cloud class); ring-buffer-shaped 17 % |
| The battery box's requirement arrival is unlike any other ECU domain (ANGLES §B.1 as written) | **Overstated** | L1: seats receive 0.7 specific events a year plus the vehicle-wide cyber / update floor; the battery box's excess is 4.4× on specific events, 2.2× with the floor on both sides; the pre-registered 3× bar is not met under the symmetric count (R in [1.2, 3.9]) |
| Most of that arrival forces more silicon | **Not supported** (exploratory) | L1 reviewer split: five `stack` acts in eleven years; the other 30 events are software, re-approval, warnings or scope |

> **Note, 2026-11-11 (L1b, [`../L1B/results_L1B.md`](../L1B/results_L1B.md)): UNGATED on count and kind**, so neither
> row above moves. Two fresh raters failed identification (0.60) and class κ (0.38) on the lighting ledger; they
> agreed on every `stack` call (κ 1.00, carried by the 51 battery rows judged from one shared text). Ungated, the
> two readouts point in opposite directions. By count, lighting received **more** events than the battery domain
> (R_BL 0.73 [0.47, 1.12]; 33 of 40 on UN R48 parallel supplements; ≈ 1.1 if each instrument-date counts once). By
> kind, 16 of 27 specific battery events force the stack and **none** of 40 lighting or 6 seat events do, under
> either rater (Fisher p 1e-8). The vehicle-level acts (R155-00, R156-00/01, GB 44495, GB 44496) were rated `yes`
> for the lighting and seat ECUs as well. The seat domain calibrated against L1 (6 vs 8).
>
> *Reviewer, 2026-11-12 (accepted; [`../L1B/results_L1B.md` §10](../L1B/results_L1B.md)):* the `stack` class counts
> obligations of five kinds — telemetry, charging communication and data read-out included, several of them MCU-class —
> so "16 of 27" is not sixteen Linux-class acts: three of the sixteen are the acts named in POSITION §1, and the
> finding is that the comparison domains carry none of any kind. Under every counting of the two ledgers R_BL lies
> between 0.44 and 1.3, so the 3× count row is out of reach of this data. Both rows above stand.

Two rows matter most for the MCU-tier story: the cheapest fix to min/max is not per-cell telemetry, it is carrying the
pack's **worst-cell resistance** in the limiter — bytes, not DRAM; and the regulation that forces a Linux-class stack is
**five acts**, so a design that already carries R155 / R156 / OTA / energy-data obligations has the stack, and one that
does not is not pushed there by the rest of the ledger.

## 4. The revised position, claim by claim

| Customer claim | What the evidence says | How to say it |
|---|---|---|
| **C1** 1 °C cooler charging ≈ $100 | lifecost: $58/K (p50, ASSUMED inputs); mechanism untested (X7) | Value plausible; mechanism not demonstrated on public data |
| **C2** 20 % reserve → 5 % | Not as estimation precision (X5/X6); not as bottom power capability (X8); top-of-charge plating margin untested (S3) | The reserve is set by knees and by policy; no public evidence that per-vehicle data releases it |
| **C3** ECU consolidation | lifecost $148 (p50, ASSUMED) | Real, and the strongest *measured-cost* leg; tier-defining when the box must host Linux-class software (C5) — and L1 names which acts put it there |
| **C4** small NN beside the µs loop beats static tables | convsim: no, within the model family; R-spread limiter: yes, but MCU-class | Ask which quantity the NN sets (§D's question); most candidates are tables |
| **C5** MCU would cost more than MPU + DDR | True as a *marginal* statement once the A-core is required for software | Lead with this; it is the honest form of the thesis. The software is R155 / R156 / OTA / battery-passport / Euro 7 OBM data: five acts, all in force or dated |
| **C6** converter benefit from history | Not supported (convsim; DC1) | Keep as upside with kill criteria; do not lead with it |

## 5. What would still move the position

The programme has run every leg the public record can carry. What is left is either the customer's data or optional
tidying:

- **Customer data asks** (public data cannot reach these): a phase-level (≥ 1 kHz) rack power trace; per-unit field
  drift of converter envelope parameters over life; the OEM's last twenty root-cause reports with the pre-event window
  each needed; the OEM's own list of post-SOP requirement changes on a fielded battery ECU with what each one cost
  (software update, re-approval, or hardware) — the second kill in ANGLES §C.1 that L1 could not test; and the
  violation budget and window of the ramp spec the data-centre customer is actually held to, which DC2 could not find
  in public.
- **DC2-R — run 2026-11-11, UNGATED again** ([`../DC2R/results_DC2R.md`](../DC2R/results_DC2R.md)): the
  granularity fix lifted deciding-row agreement to 0.81 and κ(window) to 1.00, but coverage of the 500-page protocols
  kept identification at 0.72. Four raters in two pairs now agree on the deciding picture; DC1b was pre-declared not
  to run on UNGATED, and the leg closes here. A DC2-R2 with a named section list per instrument would probably gate;
  it is not scheduled because the deciding set would not change.
  **Run 2026-11-11 ([`results/DC2R/results_DC2R.md`](../DC2R/results_DC2R.md)): UNGATED** — identification 0.72;
  the granularity fix worked on the deciding rows (0.81, every class agreed), and the gap moved to coverage of large
  documents and quantity naming. DC1b is not run; the leg closes on DC2-R. ERCOT §6.5.7.11 was again the only
  history-shaped binding clause, recorded identically by both raters.
- **O1 / R1** (code; tier-neutral or secondary): close the audit items; test learned telemetry reduction under a
  budget. Neither moves the thesis.
- **A second quiet comparison domain for L1** (lighting or wipers, say) if the 3× ratio is ever to be settled: the
  seat domain gave eight specific events, too few to pin R.

## 6. Licence map for anything customer-facing

Usable: B1 (own board), DC1 (NLR CC BY 4.0), McMaster-based profiles (CC BY 4.0), Beihang arms (CC BY 4.0), NHTSA
material (public domain; FR1-R gated), L1 (public regulatory record; UN, EU, US and GB sources cited per event), convsim
and lifecost (own models, ASSUMED inputs stated). **Not usable:** anything computed on Changan (CC BY-NC-SA 4.0), which
includes X8's primary, X2-F's primary and the Study 2 fleet results — these direct where a licensed test should look;
they do not go on a slide.

## 7. Close-out: the position to carry

*The customer-facing form of this section, with every slide-usable number and its licence, is
[`POSITION.md`](POSITION.md).*

**For the EV customer (800 V → 48 V, battery charging).** Lead with C5 in its honest form: the A-core and its DRAM are
in the box because UN R155, UN R156, the EU Batteries Regulation and Euro 7 with its OBM / OTA implementing act put a
Linux-class stack there — cyber-security management, authenticated updates, SoH data access, on-board monitoring with
OTA transmission — and that stack is sized by five acts in six years, not by the thirty smaller events around them
(L1). Once the core is there, the battery intelligence is free upside, and the one capability no MCU-class memory can
match is MEASURED: a 671 s ring of 3.2 MB/s telemetry in 2 GB LPDDR with zero drops (B1), whose forensic value the
public record puts at about one root cause in six, concentrated in the charging path (FR1-R). Do not lead with
per-cell analytics, per-vehicle learning or converter history: the programme refutes each on the public data it could
reach, and the cheapest fix to min/max is a worst-cell resistance table in the limiter, bytes not DRAM (X2-F, X8).

**For the data-centre customer (2000 V → 48 V).** Do not lead with anticipation: on public training traces a reactive
controller matches seconds of history at tight budgets (DC1), and no public specification was found with the slack,
sub-minute shape in which history would pay (DC2 and DC2-R, documentary, four raters in two blind pairs). The shelf controller's Tier-A case is the same as the
EV one — the software it must host (operator telemetry, TLS to the DCIM, vendor / operator firmware isolation, the
storage element's BMS) — plus whatever the customer's own ramp contract says, which is the first thing to ask for.

**What the customer's belief most likely rests on.** Not on any computation the programme could find. On the cost of
the stack they already know they must host, on the option value of not re-spinning a board when the next act lands,
and on a ring buffer they have wanted at least once. Each of those is a real reason; none is "the NPU does the 1 µs
loop better". Say that, with the numbers above, and ask the one question in ANGLES §D.

