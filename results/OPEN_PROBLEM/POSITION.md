# Position paper — why an application-processor tier with DRAM sits in the battery-charging and power-conversion box, and what it is not for

**Licence of this document:** public domain (CC0). **Written:** 2026-11-11, at the close of the open-problem pass.
**Audience:** whoever has to answer an EV manufacturer or a data-centre operator who says "the MPU with DDR beats an
MCU for the charging and 800 V → 48 V box". **Vocabulary:** *Tier A* is an application-processor part with DRAM and a
Linux-class software stack; *Tier M* is an MCU with on-chip SRAM, HyperRAM or a small SDRAM and a factory calibration.
Every number below is quoted from a result file in this repository with its tag (MEASURED, DERIVED, SOURCED, documentary)
and its licence; nothing here is computed on a dataset that forbids commercial use. The evidence trail is
[`SYNTHESIS.md`](SYNTHESIS.md); the red-team is [`ANGLES_REPORT.md`](ANGLES_REPORT.md).

---

## 1. The position in five sentences

1. **The Tier-A part is in the box because regulation put a Linux-class stack there**, not because the battery or the
   converter needs the compute: UN R155 (cyber-security management), UN R156 (authenticated software updates), the EU
   Batteries Regulation (SoH data retention and read-only access), and Euro 7 with its on-board-monitoring / OTA
   implementing act. Those five acts, in six years, are the ones that force cryptography, update images, data access
   and telemetry onto the battery / charging ECU; the thirty smaller regulatory events around them are software (L1).
2. **Once the core and its DRAM are there, the battery and converter intelligence is free upside** — and on every
   public dataset we could reach, that intelligence is MCU-class anyway: a 220 KB model, ten bytes per cell, limiter
   loops of 1.5–52 µs; per-vehicle learning does not beat a fleet model on usable energy; a load-indexed table holds
   converter loss within 1 % of optimal under 100× switching stress.
3. **The one capability no Tier-M memory can match is measured:** a continuous 3.2 MB/s telemetry ring of **671 s in
   2 GB of LPDDR with zero drops** and real-time loops undisturbed (B1); HyperRAM holds 40 s, an MCU with 256 MB SDRAM
   80 s, and flash wears out in under a year as a ring medium. The public failure record values that ring as an
   event-triggered capture for about **one root cause in six**, concentrated in the on-board-charger / charging path
   (FR1-R) — real, not recurring.
4. **The marginal-cost claim ("an MCU would cost more") is true in exactly this form:** the second die is cheaper than
   a second board once the A-core is required for the stack. Lead with that. Do not lead with cooler charging, the
   released reserve, or the µs-loop neural network: the first is plausible but untestable on public data, the second
   is not supported in any public fleet, the third is a table.
5. **For the data-centre box, do not lead with anticipation.** On public training traces a reactive controller holds
   the load inside a ramp spec with as little storage as one with seconds of history (DC1), and no public grid,
   utility, power-quality or rack specification has the slack, sub-minute shape in which history would have paid
   (DC2 / DC2-R, four raters). What is Tier-A-specific there is, again, the software: operator telemetry, TLS to the
   DCIM, firmware isolation, the storage element's BMS — plus whatever the operator's own ramp contract says.

> **Note, 2026-11-11 (L1b, [`../L1B/results_L1B.md`](../L1B/results_L1B.md)).** The test of sentence 1 against a
> second comparison domain is **UNGATED** (identification 0.60, class κ 0.38), so sentence 1 stands as written and is
> not rewritten. Ungated, for the record:
> - exterior lighting receives as many dated requirement events as the battery / charging domain, or more (R_BL
>   0.73);
> - but none of its 40 events, nor the 6 seat events, force the stack. 16 of 27 specific battery events do, under
>   both raters.
>
> Sentence 1's 'five acts' was counted on L1's narrower split. Under L1b's `stack` definition both raters also put
> GTR 22, GB/T 32960 (2016 and 2025), GB/T 27930-2023 and IEC 61851 in the stack set. That is ungated, and a
> rewording is the reviewer's.
>
> *Reviewer, 2026-11-12 (L1b accepted as UNGATED; [`../L1B/results_L1B.md` §10](../L1B/results_L1B.md)):* no
> rewording. Sentence 1 is a class statement and stands: the five acts are the ones that put cryptography, update
> images, data retention with access and OTA on the ECU, and the thirty smaller events are software-only in class.
> L1b's `stack` is a broader field — it also counts telemetry (GB/T 32960), charging communication (IEC 61851,
> GB/T 27930) and data read-out (GTR 22), several of them MCU-class obligations — and "16 of 27" is a count of
> those five kinds, not of acts that force Tier A. Its usable content for this paper, still ungated: by arrival
> *rate* the battery box is not special (a lamp regulation moves as often or more), and no lighting or seat act of
> any kind reaches the stack, under either rater. Say the five acts; do not say "sixteen".

## 2. The customer's claims, one by one

| Claim as stated | What the evidence says | Say this |
|---|---|---|
| **C1** "1 °C cooler charging is worth about $100 a vehicle" | A life-cost model with stated assumptions puts it at $26 / **$58** / $124 per kelvin (DERIVED, ASSUMED inputs). The mechanism — a per-cell thermal observer removing hottest-cell margin — could not be tested: public packs carry 1 K thermistors and the probe maximum is never more than 1 K below the hottest cell (X7, UNDERPOWERED). | Plausible at the optimistic end; not demonstrated on public data. Ask for the customer's own per-cell thermal traces. |
| **C2** "Take the 20 % reserve to 5 %, same customer benefit" | Not as estimation precision: knees, not estimation error, set the reserve, and per-vehicle history does not beat a frozen fleet model (X5 / X6, lab cells, CC BY). Not as bottom power capability: in two public fleets the estimated headroom exceeds the 95th-percentile demand in 96–97 % of sessions (X8, NOT INTERPRETABLE; Beihang CC BY, Changan research-only). The top-of-charge plating margin is the one reading never tested. | The reserve is set by knees and by policy. No public evidence that per-vehicle data releases it. The $1,700-class number stays hypothetical until the customer shows which reserve they mean and how they would release it. |
| **C3** "One processor for charge and discharge removes two ECUs" | $132 / **$148** / $165 a vehicle in the cost model (DERIVED, ASSUMED). Needs no battery theory. | Real and measurable; tier-defining only because the consolidated box must host the C5 stack. |
| **C4** "A very small neural network beside the µs interrupt beats static tables" | Within the model family tested, a load-indexed table holds converter loss within 0.2–2.2 % of optimal under 10–100× switching stress (convsim, own model). A limiter that knows the pack's resistance *spread* needs a smaller margin than min/max — but a shuffled-identity limiter is within ≈ 1 pp of the true per-cell one, so the gain is a worst-cell table, bytes not DRAM (X2-F, X8). | Ask which quantity the network sets. Most candidates are tables an MCU holds. |
| **C5** "An MCU would cost more than an MPU with DDR" | True as a marginal statement once the A-core is required for the regulation-driven stack. L1 counts that regulation: 35 dated events in 2016–2026 on the battery / charging domain, 3.2 a year and accelerating; the five that force a stack are named above. The DRAM is sized by the stack, not by the battery maths. | **This is the thesis.** State it with the five acts and their dates. |
| **C6** "Cooler charging, the efficient interrupt and other things together get us there" | Converter benefit from history: not supported (convsim; DC1). | Keep as upside with kill criteria. |

## 3. The numbers that may go on a slide, with their sources

| Number | Tag | Source and licence |
|---|---|---|
| 671 s of 3.2 MB/s telemetry in 2 GB LPDDR, 0 drops, 26 / 26 dumps verified, real-time loops within 6.3 % | MEASURED | B1, own board |
| 40 s (HyperRAM 128 MB), 80 s (MCU + 256 MB SDRAM) at the same rate; eMMC as a ring medium wears out in 0.05–0.95 y | DERIVED (endurance ASSUMED) | B1 |
| 35 regulatory events on the battery / charging ECU domain, 2016–2026 (3.2 / yr, 22 in 2023–25); five stack-forcing acts | SOURCED events, DERIVED-judgemental classes | L1, public regulatory record |
| Battery / seat requirement-arrival ratio 2.2× with the vehicle-wide cyber / update floor on both sides, 4.4× without | DERIVED | L1 |
| About one public power-electronics root cause in six is ring-buffer-shaped (17 % [8, 33]); a third need > 80 s of history, mostly as per-event signatures over many cycles | DERIVED-judgemental, gated κ 0.90 | FR1-R, NHTSA public domain |
| Reactive controller matches 30 s of history on AI-training swings (storage ratio 1.02 and 1.00); 1 s ramp detector does as well; perfect-foresight ceiling 1.38× | DERIVED under ASSUMED spec | DC1, NLR traces CC BY 4.0 |
| No public spec with a 1–60 s window and a loose allowance on real-power variation, except an ERCOT curtailment rule on one-minute averages | documentary (UNGATED twice on identification; deciding rows agreed by four raters) | DC2 / DC2-R |
| Load-indexed converter table within 1 % of optimal loss | DERIVED, own model | convsim |
| $58 / K (C1), $148 (C3) | DERIVED, ASSUMED inputs stated | lifecost |

**Not for slides:** anything computed on the Changan fleet data (CC BY-NC-SA 4.0): the X2-F and X8 primaries and the
Study 2 fleet results. They direct where a licensed test should look; they do not go to a customer.

## 4. What to ask the customer

Ask the one question in ANGLES §D:

> *If we gave you the same A-core software stack — Linux, isolated domains, A/B images, TLS — but only 128 MB of RAM
> and no bulk waveform retention, which of C1–C5 would you lose? And when you say "NPU", do you mean the vector unit on
> the real-time core, the accelerator on the application side, or the part as a whole?*

A claim that survives is a software / isolation claim and this paper's thesis. A claim that dies is a data-retention
claim, and its answer sizes the memory. Then ask for the four things public data cannot reach: a phase-level (≥ 1 kHz)
rack power trace; per-unit field drift of converter envelope parameters over life; the last twenty root-cause reports
with the pre-event window each needed; and, for the EV customer, their own list of post-SOP requirement changes on a
fielded battery ECU with what each one cost.

## 5. What would change this position

- A customer-supplied per-cell thermal trace showing probe-maximum error well above 1 K (reopens C1's mechanism).
- A fleet in which bottom power capability binds in more than a few percent of sessions (reopens C2 as power).
- A ramp contract or utility clause on the operator's own connection with a sub-minute window and an excursion
  allowance (reopens the data-centre anticipation leg; DC1's model is ready to run under it).
- A post-SOP change on a fielded battery ECU that needed new silicon rather than a software update or re-approval.
