# ANGLES REPORT — what on-vehicle (and on-shelf) memory buys in the battery and power-conversion domain

**Requested by:** [`briefs/OPEN_PROBLEM/README.md`](../../briefs/OPEN_PROBLEM/README.md) §12. **Written:** 2026-10-30.
**Author:** an external reviewer pass (Claude Fable 5.1), reading the brief, the dossier, `results/X/`, the 2026-10-15
audit and the convsim / lifecost code. **Licence:** public domain (CC0).

**Tags.** MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED as in the brief. Two small **EXPLORATORY** checks were run
(minutes, no data download); code and output are in [`exploratory/`](exploratory/). No pre-registered experiment was
started. Where a SOURCED figure comes from a web page rather than a paper or regulation, the source is named inline.

**Scope note.** The brief's Tier A is "A-core + LPDDR + the same real-time engine". The programme owner's framing of the
customer's words is "NPU/MPU instead of MCU for the 1 µs loop". Nothing in the customer's claims C1–C6 puts the 1 µs
interrupt *on* an NPU, and neither tier does; §A.8 and §D treat "NPU" as a word that needs disambiguating, not as a
hardware proposal.

---

## 0. The answer in one page

1. **The programme's negative results are correct, and they kill one argument the roadmap is still half-leaning on.**
   The "working set" case — that battery analytics need more memory than an MCU can host — is refuted by the
   programme's own MEASURED numbers (220 KB int8 model, 10 B per cell, µs limiters). Stop making it. Per-unit *learning*
   does not help on batteries because late-life knees, not estimation error, set the reserve (X5/X6). A load-indexed
   static table is within 1 % of optimal converter loss (convsim), and an EXPLORATORY 100× stress on the
   hard-switching energy did not change that (§A.5). These are clean, useful nulls.

2. **The question has an unstated conditional that resolves the "proves too much" trap.** Software-domain isolation
   is worth paying for in proportion to *requirement volatility × volume × hardware re-spin cost*. The
   battery/charging/power-conversion box is the single most regulation-exposed ECU in the vehicle (five
   software-visible requirement regimes landed on it in roughly eight years: GB/T 32960 per-cell upload, UN GTR 22 /
   Euro 7 on-board durability monitor, EU 2023/1542 battery passport and Art. 14 SoH access, ISO 15118-20
   bidirectional charging, UN R155/R156 cybersecurity and software-update management). A seat ECU faced none. The
   isolation argument therefore does **not** apply to everyone; it applies to the domains where requirements keep
   arriving after SOP. That is why some designs need Tier A and most do not. (§B.1)

3. **C5 ("an MCU would cost more than an MPU with DDR") is a marginal-cost statement, not a price comparison.** Once
   the box must host a Linux-class stack for the reasons in (2), the A-core and its DRAM are sunk. The question flips:
   why also carry a second die for the real-time engine? Read that way, C5 is simply true, and it says nothing about
   battery AI. (§E)

4. **Where memory is physically necessary — not merely convenient — is the continuous ring buffer.** A rolling
   window of converter telemetry at 3–60 MB/s can only live in DRAM: flash write endurance exhausts in 0.1–7.6 years
   (ASSUMED endurance; §B.3 table), HyperRAM's 128 MB window holds 4–40 s, an MCU with SDRAM holds 8–80 s, 2–8 GB of
   LPDDR holds 10–40 min raw and hours decimated. The value is forensic: the Hyundai/Kia ICCU campaigns (an 800 V
   OBC + DC-DC) were traced to transient over-current / end-of-charge over-voltage events after an NHTSA
   investigation and recurred after the first remedy (SOURCED). Pre-event waveform retention is what that class of
   failure needs. (§B.3)

5. **The data-centre case is where the C2-sized number is public.** Hyperscalers already bank 9–25 % power
   oversubscription (Google, SOURCED) worth "hundreds of millions of dollars", and the rack-level stabilisation
   problem for synchronous AI training (0.2–3 Hz swings, tens to hundreds of MW) is being solved with rack energy
   storage plus **fast telemetry and real-time spectral monitoring of the power waveform** (NVIDIA/Microsoft, SOURCED). Provisioned power
   held back against load uncertainty is the exact analogue of an EV uncertainty reserve, and electrical
   infrastructure is $4.5–5.7 per watt of the $11.3 M/MW build (SOURCED JLL, DERIVED). Ten percent on a 130 kW GPU
   rack is $60–70 k of avoided capex against a controller BoM delta of tens of dollars. The rack storage element is
   an EV-class pack with a far more predictable load. (§B.2)

6. **The null (§E) is the best-supported explanation of C1–C6 as a set**, and it is good news for an "application processor +
   DRAM" roadmap: Tier A wins wherever the box must host Linux-class software anyway, with battery and converter
   intelligence as upside that the already-present memory makes free. Tier M wins everywhere else. The DRAM size is
   set by the software stack, not by battery working set.

---

## A. Red team (one page)

| # | Item in the brief | Problem | Consequence |
|---|---|---|---|
| A.1 | §0 lists **bandwidth (~30× read)** as part of the established architectural case. | No named algorithm in the programme consumes it. Everything run (OLS slopes, robust z, LUT limiters, medians) is single-pass. A re-read factor of 10 at 32 MB/s is 320 MB/s: 80 % of HyperRAM, but only **40 % of a 32-bit SDRAM-200 bus on an MCU**, and 2.7 % of LPDDR5 (DERIVED, `exploratory/arith.out`). | Name the multi-pass algorithm (iterative nonlinear fit over a long window, exact quantiles, long-window spectra, matrix factorisation) or drop the 30×. As stated, the bandwidth leg is unsupported. |
| A.2 | §3.2 calls **Tier M + HyperRAM (≤ 128 MB, ~0.4 GB/s)** the fair comparator. | Rule 4 says use Tier M's best option. Automotive-qualified crossover MCUs with a 32-bit SDRAM controller at up to 200 MHz exist in current vendor catalogues (SDRAM 8/16/32-bit, SDRAM-200; SOURCED vendor part pages). That is ~0.8 GB/s theoretical and hundreds of MB, without an MMU or Linux. | **The dividing line is not "has DRAM" but "has an MMU and an A-class software stack with GB-class memory".** Reword the thesis from "DRAM tier" to "Linux-class tier"; otherwise the MCU-E counterpart can answer "we add SDRAM". |
| A.3 | §3.2 "**Re-reading is the bottleneck**". | Assumes a non-streaming analysis without naming one (see A.1). | Same fix as A.1. |
| A.4 | §2.2 row "**96-cell pack, every cell at 1 kHz**". | Daisy-chained cell-monitor AFEs deliver a full pack scan at ms-class intervals; practical per-cell rates are 1–100 Hz. kHz per-cell voltage is a hypothetical the hardware does not provide. | Any mechanism that needs kHz per-cell data (EIS, relaxation at kHz) is bounded by the AFE, not by the compute tier. Say so in §2. The converter side (1 MS/s per channel) is the only true high-rate stream. |
| A.5 | §4 "**Quasi-static converter efficiency from history: not needed**", from a 48 → 12 V buck with E_oss 0.75 µJ. | My suspicion: an 800 V isolated stage has 10–100× the hard-switching energy per transition, so the verdict might be a plant artefact. **EXPLORATORY check** (own re-implementation of the convsim loss model and WLTC load, `exploratory/explore_eoss.py`): at E_oss × 10, × 30, × 100 and per-unit inductance ± 15 %, the load-indexed static table stays within **0.2–2.2 % excess loss (≤ 0.08 efficiency points)** of the oracle. | **The red-team item did not land.** The verdict is robust to the switching-loss share within this model family. The unmodelled objection (DAB/LLC soft-switching range vs phase shift and voltage gain) remains open but my prior that it changes the answer is weaker. Record as a clean negative. |
| A.6 | §1.1 lists **three** readings of C2's "20 % reserve". | There is a fourth that fits "20 % → 5 %" numerically: the **top-of-charge (anode-potential / plating) margin**, i.e. the "charge to 80 % daily" guidance and the taper above ~70–80 % SOC. 80 → 95 % usable daily window is "same customer benefit from a smaller pack" without touching pack sizing or the durability floor. It cashes out as daily usable energy, not cells avoided. | Add it to §1.1 beside S1 and S3. It is the only reading in which the customer's "cooler charging" (C1) and "reserve" (C2) are the *same* mechanism: the plating boundary is set by anode temperature and current. |
| A.7 | §3.3 sizes the per-cell margin result as "**+2.5 % admitted current, small**". | The economic quantity for a BMS is not the median charge rate; it is that min/max's margin **does not transfer** to unseen vehicles (0.05 % → 0.23 %) while per-cell's does. A fleet margin is set for the worst vehicle; the price of a non-transferring margin is the tail over-current rate × warranty cost, which the programme never computed. | The claim is mis-sized, in the programme's own disfavour. Price the tail, not the median, before putting the number on a slide. |
| A.8 | §2.4 "**An external NPU's offload latency would break a 1 µs deadline.**" | True for an AXI-attached NPU behind a Linux driver (tens to hundreds of µs). Not true of an ISA-coupled vector/matrix extension on the real-time core, which is what §2.4 itself attributes C4 to. The customer's word "NPU" is ambiguous between (i) that vector unit, (ii) the AP-side NPU, (iii) loosely, "the MPU part". | The brief assumes (i) without checking. §D makes the disambiguation part of the one question. |
| A.9 | §3.6 "**applies to everyone, so proves too much**". | It applies in proportion to requirement volatility (summary point 2). The brief's own §7 "cannot be re-binned" argument is the same point stated for data instead of software. | Condition the isolation argument on volatility and it no longer proves too much. This is §B.1. |
| A.10 | §2.2 "**~17 MB/day connected-car budget**" as the uplink comparator. | The real architectures are (a) regulatorily mandated 10 s per-cell upload (GB/T 32960 carries the full cell list — the audit's point) and (b) *trigger-based* bulk upload. 1.66 MB/day of raw per-cell already reaches the national platform. | "Cannot go to the cloud" is true of converter telemetry only, and for that stream the design question is trigger-based upload from a local ring buffer (§B.3), not a daily budget. |
| A.11 | Tag hygiene. | §3.1 header says MEASURED for "~1 % of one core at 100 Hz for 3,564 cells" (DERIVED from MEASURED); §2.1 "confirmed easy" carries no tag; §7's EE Times figures (5 kW per GPU, 10,000 A) are SOURCED from a trade article I could not re-verify. | The audit already flagged this pattern once. |

Nothing in §3 is wrong as a number. The over-statements are A.1/A.3 (bandwidth) and A.9 (the trap applied
asymmetrically); the under-statement is A.7.

---

## B. What you are missing — ranked

Ranking weighs plausibility × size × how specifically the mechanism needs Tier A (memory capacity, bandwidth, isolation,
training) rather than Tier M with SDRAM/HyperRAM and factory calibration. Each entry ends with what kills it.
Mechanisms that are valuable but **tier-neutral** are listed separately in §B.7, because the brief's question is about
the tier, and pretending otherwise would repeat mistake 11.

### B.1 Requirement volatility: the fair form of the isolation argument, and it is priceable

**Mechanism.** The battery/charging/power-conversion box receives new software-visible requirements *after* SOP at a
rate no other ECU domain does: per-cell telemetry schemas (GB/T 32960 editions), an on-board durability monitor read in
service (UN GTR 22: 80 % SOCE at 5 years / 100,000 km and 70 % at 8 years / 160,000 km; Euro 7 adopts 80 % / 72 %;
SOURCED UNECE, EU 2024/1257), battery-passport and Art. 14 SoH read-out (EU 2023/1542), ISO 15118-20 bidirectional
charging with TLS 1.3 / PKI, and UN R155/R156 cybersecurity and software-update management. On Tier A each arrives as a
software domain with its own update cadence; on Tier M each re-opens the one certified image, and some re-open the
hardware.

**Why Tier A specifically.** MMU-isolated domains, A/B images with rollback, a TLS/PKI stack and GB-class memory are
what let a new requirement ship without re-certifying the control loop or re-spinning the board. SDRAM on an MCU does
not supply isolation; HyperRAM does not supply a rollback-capable second image of a Linux-class stack.

**Why the programme could not see it.** Every experiment valued battery physics on battery data. The value here is in
the *arrival process of requirements*, which no battery dataset shows. The evidence is regulatory history.

**Size (order of magnitude).** Option value ≈ Σ P(requirement needs hardware or re-certification) × cost / volume.
With a re-spin plus re-qualification at $10–30 M (ASSUMED), platform volume 200 k–1 M (ASSUMED), and 1–3 events over
a 7-year platform (SOURCED history above: five in eight years, not all hardware-impacting), the per-vehicle value is
**$10–150** (DERIVED, `arith.out`), comparable to C3 and an order below C2 — plus an unpriced tail: market access lost
while a non-compliant fleet waits for hardware. This is the first mechanism in the programme that explains **why some
designs need Tier A and most do not**: body, seat and HVAC ECUs have no such arrival process.

**What kills it.** Evidence that fielded Tier M battery/charging controllers absorbed those five regimes by software
alone, with the safety case intact and no hardware change — e.g. an OEM shipping passport read-out and 15118-20 onto an
in-service RTOS image. If that is common, the option is worth ~$0 and §E stands alone.

### B.2 The data-centre analogue of C2: provisioned-power margin and rack stabilisation, where the money is public

**Mechanism.** A data centre's breakers, transformers and UPS are provisioned for a peak that the load rarely reaches;
the margin is held against load uncertainty, exactly as an EV reserve is held against energy uncertainty. Operators
recover it by oversubscribing and capping. Google reports 25 % or higher oversubscription in production "saving
hundreds of millions of dollars" (SOURCED, ASPLOS 2020) and 9–25 % from its Thunderbolt capping system (SOURCED, OSDI
2020); a distributed per-server UPS design shaved 19.4 % of peak and fitted 24 % more servers in the same budget
(SOURCED, Google). Synchronous AI training adds a second margin: swings of tens to hundreds of MW at 0.2–3 Hz that
must be smoothed at the rack with energy storage; the authors find that 100 ms power counters are too slow for the
~20 Hz component of the swings and call for faster telemetry with real-time spectral monitoring of the power waveform
as a backstop (SOURCED, Choukse et al., arXiv 2508.14318, NVIDIA/Microsoft; paraphrased). NVIDIA's 800 VDC architecture bundles
multi-timescale storage with the bus for the same reason (SOURCED, developer.nvidia.com).

**Why Tier A specifically.** The 2000 V → 48 V (and 800 V → 48 V) shelf controller sits at the one point that sees
every phase: 12 MB/s per GPU and ~100 MB/s per 8-GPU board of phase telemetry (brief §7, DERIVED). A 10 s forecasting
and spectral-monitoring window at 100 MB/s is 1 GB — LPDDR class; HyperRAM holds 1.3 s, an MCU SDRAM 0.6–2.6 s
(`arith.out`). It also needs a TLS path to the operator's DCIM and vendor/operator firmware isolation. And the storage
element on the 800 VDC bus is an EV-class pack cycled 10⁵–10⁶ shallow cycles a year — a BMS problem with a load that
*is* predictable, the one regime where anticipation (brief §7) and per-cell SoH could both pay.

**Why the programme could not see it.** §7 valued only AC-to-core efficiency ("order of a point"). Provisioning and
stabilisation were never on the table, and no EV dataset contains them.

**Size.** Electrical infrastructure is 40–50 % of the $11.3 M/MW shell-and-core build (SOURCED, JLL 2026 via trade
press), i.e. **$4.5–5.7 per watt**. Ten percent oversubscription on a 130 kW rack ≈ **$60–73 k** avoided capex; on a
100 MW site **$45–56 M** (DERIVED, `arith.out`). Against a controller BoM delta of tens of dollars per shelf, the
ratio is 10³–10⁴. This is the C2-sized number — and unlike C2 it is published.

**What kills it.** (a) GPU-side smoothing (programmable ramp rates and power floors on GB200/GB300) plus BMC telemetry
already deliver the headroom, leaving the shelf controller as a follower; (b) the 100 MW provisioning study recovered
its headroom (960 → 1,020 W per GPU, 2–3 % performance) from **3-second** sampling (SOURCED, arXiv 2605.24461), so the
oversubscription half may not need fast local telemetry at all — the stabilisation half is where ms data is called
for; (c) the operator wants the data in its own domain and will not pay the shelf vendor for it.

### B.3 Event-triggered retention: the one place DRAM is physically necessary

**Mechanism.** Keep a rolling window of raw or lightly decimated converter and pack telemetry resident; on a trigger
(protection trip, anomaly score from the C4 network, warranty event, fleet-issued capture request) freeze it and upload
it. The value is root cause for rare field failures of power electronics and packs. The Hyundai/Kia ICCU campaigns —
an 800 V OBC + low-voltage DC-DC — were traced by NHTSA investigation PE23011 to "overcurrent, overvoltage induced at
the end of charging, and certain thermal loading", recalled twice (24V-204, 24V-868, ~145–147 k vehicles) with failures
recurring after the first remedy, and are now under a warranty extension (SOURCED, NHTSA documents). Those are
transient events: a freeze-frame of DTCs at trip time is what the MCU keeps today; the switching-cycle waveform of the
last minutes is what finds the cause.

**Why Tier A specifically.** This is arithmetic, not preference (DERIVED, `arith.out`; endurance ASSUMED):

| Rolling medium | 3.2 MB/s (10 % farmed) | 32 MB/s (100 %) | 60 MB/s (ADC ceiling) |
|---|---|---|---|
| MCU SRAM 3 MB | 0.9 s | 0.1 s | 0.1 s |
| HyperRAM 128 MB (max window) | 40 s | 4 s | 2 s |
| MCU + SDRAM 64 / 256 MB | 20 / 80 s | 2 / 8 s | 1 / 4 s |
| LPDDR 2 / 8 GB | 10 / 42 min | 1 / 4 min | 33 s / 2.2 min |
| eMMC 64 GB, 3 k P/E as ring buffer | **worn out in 1.9 years** | 0.2 years | 0.1 years |
| eMMC 256 GB, 3 k P/E | 7.6 years | 0.8 years | 0.4 years |

A 15-year vehicle life at 3.2 MB/s is 1.5 PB written; no automotive flash carries that. DRAM is the only medium that
absorbs continuous MB/s writes for the life of the vehicle; capacity sets the window; a 10:1 decimation buys an hour in
2 GB. HyperRAM and MCU SDRAM give seconds.

**Why the programme could not see it.** Every experiment valued steady-state estimation. No public dataset contains
pre-failure high-rate telemetry (G.1), so forensics could not be scored.

**Size.** Expected value is modest: with HV power-electronics field failure at 1–3 % over warranty and $1–2 k per
replacement (ASSUMED), exposure is **$10–60 per vehicle**, of which root-cause-driven fixes recover a fraction. The
tail is not modest: one recall campaign of the ICCU class costs 10⁷–10⁸. Order **$10¹–10² per vehicle expected, fat
tail**. The same arithmetic applies to the data-centre shelf, where a fleet-wide converter defect is a site outage.

**What kills it.** A review of the last N root-cause reports showing the needed pre-event window is ≤ 1 s (today's
UDS snapshot plus statistics). Design in §C.3.

**Note, 2026-10-30: B1 measured the application-processor half of this table** ([`results/B1/results_B1.md`](../B1/results_B1.md)).

- **Ring buffer (MEASURED, FRDM-IMX95-PRO).** The ring sustained 3.2, 32 and 60 MB/s with 0 drops. Measured depth
  is 512 MB = 168 / 17 s and 2 GB = 671 / 67 / 36 s. Every dump that fitted the ring verified. The real-time loops
  were not disturbed beyond the 20 % flag.
- **eMMC (MEASURED).** The board's 29.6 GiB eMMC sustains 164 MB/s.
- **eMMC wear-out (DERIVED, endurance ASSUMED).** 0.95 / 0.095 / 0.050 years at P/E 3,000.
- **What B1 does not measure.** The HyperRAM, MCU-SDRAM and SRAM rows above remain DERIVED arithmetic.

### B.4 Per-unit learning pays on the converter, not the battery — the variance structure is inverted

**Mechanism.** Studies 1–2 and X5/X6 failed because battery ageing is dominated by **unpredictable late-life knees**;
there is little stable per-unit structure to learn (only 22–25 % of residual variance is a persistent offset, E).
A converter is the opposite: unit-to-unit variance is **large and static** (magnetics ± 10–20 %, Coss, sensor gains,
layout parasitics), and the protection and derating margins (OCP / desaturation thresholds, thermal derating,
soft-switching boundary) are set for the worst unit in the population. A per-unit learned envelope lets each unit run
closer to its own limit: the converter's "uncertainty reserve".

**Why Tier A specifically — weakly.** Rule 4 applies: factory end-of-line calibration captures *static* variance, and
Tier M holds a per-unit table. Tier A is required only if (i) the envelope must be re-learned in the field because
drift is material, or (ii) the model is trained on-vehicle from retained waveform history (Study 1 measured the
training footprint class at 27–59 MB). On (i), GaN dynamic R_ds(on) within rated conditions is projected at < 10 %
shift over 25 years (SOURCED, EPC), so the switch itself is not the drifter; magnetics and capacitor ageing remain
candidates.

**Why the programme could not see it.** convsim modelled per-unit variance as ageing only and cashed it out as
efficiency, where the loss surface is flat (A.5), not as derating, where it is not.

**Size.** Recovering 10–20 % of derating on ~$300–600 of HV power electronics per vehicle (ASSUMED) is **$30–120**, or
the equivalent in power density; on a data-centre shelf, density per U is worth more than that.

**What kills it.** A measured field-drift distribution of the envelope parameters that a fixed factory margin covers.
Needs fleet data from the customer; no public set.

### B.5 Core-temperature observer: the temperature analogue of X2-F

**Mechanism.** C1's "1 °C" is cashed as **margin**, not cooling. A probe-based limit charges to T_probe + margin (Changan:
32 probes for 96 cells). A per-cell electro-thermal observer — fed by per-cell I²R, which requires the per-cell
resistance X2-F showed is a stable, identifiable property — estimates core temperature and removes the margin, in the
same way X2-F's per-cell R removed the κ margin at the top of charge.

**Why Tier A specifically — unknown.** A lumped two-node-per-cell model is MCU-class. Tier A is needed only if a
higher-order spatial model (10³–10⁴ states coupled to the coolant path) beats lumped by more than the probe margin. That
is the test (§C.4), and it is runnable on data in hand.

**Why the programme could not see it.** lifecost valued 1 K; nothing asked how it is achieved; H/H2 used probe
temperature directly.

**Size.** C1's $58/K (p50, all inputs ASSUMED) × a probe-to-core margin of 2–5 K (ASSUMED) = **$120–290 per vehicle**
(DERIVED), if the OEM cashes it as cooler charging at equal time.

**What kills it.** McMaster's 72 per-cell thermistors predicted within ~1 K by a lumped model, or by probe interpolation
with a fixed margin. Then the mechanism is real but Tier M.

> **Update 2026-10-30 (X7 profile, `8a468ad`).** Run as §C.4 to the profile stage and **closed UNDERPOWERED** without a
> model: 3 of 14 McMaster runs reach a 3 K hot spot for ≥ 10 % of frames (gate 8); the thermistors read in 1 K steps;
> a one-probe-per-three-cells view is never more than 1.0 K below the hottest cell; the hot spots sit at fixed, probed
> positions. The mechanism is neither confirmed nor killed — it is **untestable on public data at this sensor
> resolution**. Two corrections to this section's test design were made by the session and are kept: sensor resolution
> and the raw probe-max gap belong in the profile gate, and the scored quantity must be the issued bound
> `mean(T̂_hot + κ_T − T_hot)`, not κ_T alone, which a biased-high estimator earns for free.
> See `results/X/X7_profile.md` and `results/X/X7_preregistration.md`.

### B.6 Anticipation on the 48 V side of the EV, where the load *is* predictable

**Mechanism.** The brief says EV load steps are less predictable than GPU dispatch. True for traction; false for the 48 V
zonal loads (steer-by-wire, brake-by-wire, active suspension, PTC) that are announced on the vehicle network 10–100 ms
ahead and correlate with vehicle dynamics. The 800 → 48 V stage and its buffer are sized for peak (3–5 kW) against an
average under 1 kW (ASSUMED); a predictor shrinks the buffer and the converter headroom.

**Why Tier A specifically — by architecture.** The predictor needs vehicle-wide context and history: the zonal
power-controller role that C3 consolidates. The functional payoff goes beyond C3's BoM saving.

**Why the programme could not see it.** convsim's load was synthetic at 1 Hz with no anticipation; there is no public
48 V net dataset.

**Size.** Shaving 20 % of peak sizing on the 48 V stage plus buffer: **$20–60 per vehicle** (ASSUMED/DERIVED).

**What kills it.** Production designs already feed-forward 48 V load requests over CAN to the DC-DC; then it is
MCU-class feed-forward with no history needed.

### B.7 Tier-neutral mechanisms worth knowing (valuable, but not a Tier A argument)

| Mechanism | Why it matters | Why it is tier-neutral |
|---|---|---|
| **The converter as an impedance analyser.** The OBC / DC-DC can inject programmable small-signal current (0.1 Hz – kHz) during charging; a streaming lock-in over the cell-monitor stream gives per-cell R and impedance on every charge. | Fixes X2-P's kill: a usable per-cell R needed ~80 passive steps ≥ 0.3 C and coverage never reached 90 %. Active excitation gives coverage on every session. | Streaming lock-in is accumulators, not history; the per-cell rate is AFE-bound (A.4). |
| **Forecast → intervention.** X6 priced the knee warning as a forecast correction (G_B 1.02). The value of a weak warning is the action it enables: per-module charge-rate and thermal policy to *delay* the knee. | Invisible on fixed-protocol lab data by construction. | Policy is MCU-class; per-cell history for it is small. |
| **Fleet-tail learning from retained per-cell history.** The reserve is a fleet statistic set for the worst 1 % of packs at year 8; it shrinks when the *fleet* learns knee precursors from every vehicle's history. | X5/X6 valued a vehicle's own history for its own estimate; the value may be in the fleet. | Per-cell at 10 s is 1.66 MB/day (audit); eMMC on either tier holds a year. |

---

## C. Test designs (pre-registration-ready; not run)

Top three by the §B ranking, plus a fourth because it is the only one runnable on data already in hand.

### C.1 Requirement-arrival ledger (for B.1)

- **Question.** How often do software-visible requirements land on the battery/charging domain after SOP, and what
  fraction need hardware or re-certification, compared with a low-volatility ECU domain?
- **Data (public).** EUR-Lex: Regulation (EU) 2023/1542 (batteries), 2024/1257 (Euro 7), 2019/2144 (GSR2);
  UNECE: GTR 22 and amendments, R155, R156; GB/T 32960 editions (2016 and later revisions); ISO 15118-2 → -20
  (standard texts are not free; use published change summaries). Control domain: seat/body/HVAC ECUs under the same
  period's type-approval regulations.
- **Pre-registered definitions.** A "requirement event" is a dated legal or standards change that alters the data the
  ECU must produce, store, sign or transmit. Classify before counting: software-only / needs more memory or crypto /
  needs new hardware. Two raters, blind to domain, adjudicated.
- **Primary metric.** Events per domain per year 2016–2027; fraction non-software-only.
- **Controls.** The control domain; a sensitivity count that excludes China-only regimes.
- **Kill.** ≤ 1 battery-domain event per five years, **or** documented Tier M fielded parts that absorbed every event
  by software update. Then B.1's option value is ~0.

### C.2 Anticipation and stabilisation value at the rack (for B.2)

- **Question.** With seconds of history at ≥ 5 Hz, how much of the rack power swing can a forecasting controller
  pre-position for, compared with a reactive controller and with a GPU-side ramp limit, and what storage energy does
  each need?
- **Data (public).** NLR/OpenEI "Dataset of Generative AI Workload Power Profiles" (5/10 Hz node power on Kestrel,
  training and inference; US-government data, licence to confirm on the submission page); MIT Supercloud (GPU power via
  nvidia-smi at 100 ms; licence to confirm); ClusterWise / OLCF Summit (per-GPU power, CC BY 4.0). None is a GB200
  rack and none is phase-level; the brief's rule 9 applies: phase-level (ms) anticipation is **not testable on public
  data** and must come from a customer trace.
- **Primary metric.** Storage energy (J) required to hold the rack's upstream power within a fixed ramp-rate and
  dynamic-range spec (take IEC 61000-3-3-style bounds as ASSUMED), for: reactive controller; forecaster with W seconds
  of history; GPU-side ramp limit at equal performance loss. Report the storage reduction from forecasting.
- **Controls.** Time-shuffled history (destroys periodicity; the shuffle control for "history" here); held-out jobs;
  the best Tier M option = a reactive controller with a fixed pre-charge, no forecast.
- **Kill.** Forecasting reduces required storage by < 10 % over reactive at any W, or the shuffled history does as
  well. Separately report whether anything needs > 1 s of history; if not, the memory argument fails even if the
  mechanism holds.

### C.3 Pre-event window audit (for B.3)

- **Question.** For HV power-electronics field failures that reached a public root cause, how long a pre-event window
  at what rate would have been needed to find the cause from field data alone?
- **Data (public).** NHTSA ODI investigations and Part 573 recall reports with root-cause text (e.g. PE23011,
  24V-204, 24V-868 for the ICCU; search the ODI database for OBC / DC-DC / inverter campaigns 2018–2026); EU RAPEX /
  Safety Gate entries; published failure-analysis papers on OBC/DC-DC field returns. All public.
- **Pre-registered definitions.** Classify each case *before* reading the remedy: cause type (transient electrical /
  thermal cycling / manufacturing / software); data that identified it (freeze-frame DTCs / bench reproduction /
  fleet statistics / waveforms); minimum pre-event window a reviewer judges sufficient (≤ 1 s, 1–60 s, > 60 s). Two
  raters, blind to each other.
- **Primary metric.** Fraction of cases where the judged window exceeds what an MCU freeze-frame holds (≤ 1 s) and
  what HyperRAM / MCU SDRAM holds (≤ 40 s at 3.2 MB/s).
- **Controls.** Inter-rater agreement (κ ≥ 0.6 or the study is UNGATED); a sample of non-power-electronics recalls as a
  base rate.
- **Kill.** < 20 % of cases need > 40 s of pre-event data. Then DRAM retention is a convenience and B.3 drops to
  tier-neutral.

### C.4 Probe-vs-core margin on McMaster (for B.5; runnable now)

- **Question.** How much hottest-cell temperature margin does a per-cell electro-thermal observer remove compared with
  probe interpolation, and does a higher-order spatial model beat a lumped one?
- **Data (public).** McMaster 72-cell dataset (CC BY 4.0): per-cell voltage and thermistor at 1 Hz, 14 drive-cycle
  runs including Fan-off (46 °C) and Module-blocked; exclude thermistors 12 and 35 (dead, stuck at 1.0 °C; `X/README.md`).
- **Models.** M0: Tier M comparator — one probe per 3 cells (emulated by masking 2 of 3 thermistors), linear
  interpolation plus a fixed margin fitted on calibration runs. M1: lumped 2-node per cell (core/surface) driven by
  per-cell I²R with per-cell R identified from current steps (X2-F method). M2: M1 plus neighbour and coolant coupling
  (sparse state-space, order 10² –10³). Fit on 7 runs, score on 7 held-out runs; two folds.
- **Primary metric.** p95 absolute error of the hottest-cell temperature on held-out runs, per model; the margin a
  limiter would need at ≤ 0.2 % unsafe frames (X2-F's bar), per model.
- **Controls.** Shuffled cell identity at every time step (rule 5); held-out runs (rule 6); M0 is the best Tier M option
  (rule 4).
- **Kill.** M0's margin within 1 K of M2's: no margin to recover. M1 within 0.5 K of M2: the mechanism is real but
  MCU-class, and B.5 moves to §B.7.

---

## D. The one question for the manufacturer

> **"If we gave you the same A-core software stack — Linux, isolated domains, A/B images, TLS — but only 128 MB of RAM
> and no bulk waveform retention, which of C1–C5 would you lose? And when you say 'NPU', do you mean the vector unit on
> the real-time core, the accelerator on the application side, or the MPU part as a whole?"**

The first half partitions the claims without asking the manufacturer to disclose the function: a claim that survives
is a **software/isolation** claim (§B.1, §E); a claim that dies is a **data/retention** claim (§B.2–B.4), and its
answer sizes the memory. The second half resolves A.8: it tells you whether C4 is in-loop inference on the RT engine
(both tiers can do it), AP-side inference on retained data (Tier A), or just a name for the part.

---

## E. The null hypothesis, stated fairly

**Statement.** No battery- or converter-specific mechanism on current public evidence justifies Tier A over Tier M
with SDRAM/HyperRAM and factory calibration. The case for Tier A in the battery/charging/power-conversion box rests on
(i) ECU consolidation (C3, ~$148 per vehicle modelled) and (ii) software-domain isolation for a stack the box must host
anyway. The battery and converter "AI" (C4, C6) is upside that an already-present A-core and DRAM make free; it is not
the foundation.

**The argument for it.**

1. Every estimation and limiting computation measured is MCU-class (§3.1: 220 KB model, 10 B per cell, 1.5–52 µs).
2. Per-unit learning does not help on batteries because knees, not estimation error, set the reserve (X5/X6: best
   1.82× vs the 4× needed; shuffle controls match). Per-unit variance on converters is static and is captured by
   factory calibration (§B.4; GaN R_ds(on) drift < 10 % over 25 years, SOURCED).
3. A load-indexed static table is within 1 % of optimal converter loss, and that holds under a 100× stress on
   hard-switching energy (§A.5, EXPLORATORY).
4. kHz per-cell data does not physically exist (A.4), and 10 s per-cell data already reaches the cloud (GB/T 32960).
5. The one physically necessary use of DRAM — the continuous ring buffer (§B.3) — is a *forensic* function whose
   expected value is $10¹–10² per vehicle, and its need for > 40 s windows is unproven until §C.3 is run.
6. What is left is that the box must run TLS/PKI for ISO 15118-20, a passport and SoH read-out API, OTA with rollback
   under R156, and a cybersecurity management system under R155. These are Linux-class requirements with their own
   update cadences. Once the A-core is in the box for them, C5 is a marginal-cost truth: carrying a second die for the
   real-time engine costs more than integrating it.

**What the null predicts, and so what would refute it.** It predicts that Tier A is chosen by OEMs who own their
battery software stack and sell into regulation-heavy markets, and Tier M by Tier-1 suppliers of fixed-function
converters and by OEMs who outsource the stack. It predicts the manufacturer's answer to §D is "we lose nothing but
C4/C6" to the first half. It is refuted if §C.3 finds most root causes need minutes of waveform, if §C.2 finds
forecasting cuts rack storage by a large factor *and* needs seconds of history, or if §C.4 finds a higher-order thermal
model removes several kelvin of margin that lumped models cannot.

**Why the null is good news for an "application processor + DRAM" roadmap.** It says that class of design is real and the customers for it are
identifiable by their software obligations, not by their battery chemistry; that the DRAM is sized by the software
stack (OS, A/B images, TLS, applications: 1–2 GB) rather than by a battery working set that does not exist; and that
the counter-tier (MCU + MRAM, no MMU) keeps every customer whose box has no post-SOP software obligations. The battery
and converter mechanisms in §B.2–B.6 are the upside list, each with a kill criterion, to be tested in the order §C
gives.

---

## Appendix — sources used beyond the repository

- UN GTR 22 thresholds (80 % / 5 y / 100,000 km; 70 % / 8 y / 160,000 km) and Euro 7 adoption (80 % / 72 %):
  UNECE GTR 22 documents via globalautoregs.com; European Parliament press release 2023-12-18; Regulation (EU) 2024/1257.
- Google power oversubscription: Sakalkar et al., ASPLOS 2020 ("25 % or higher … hundreds of millions of dollars");
  Li et al., Thunderbolt, OSDI 2020 ("9 %–25 %"); Kontorinis et al., distributed UPS ("19.4 % of peak … 24 % more
  servers"), research.google.
- AI training power swings and rack storage: Choukse et al., "Power Stabilization for AI Training Datacenters",
  arXiv 2508.14318 (NVIDIA/Microsoft); "Provisioning to Runtime Optimization of a 100 MW-Scale AI Cluster",
  arXiv 2605.24461 (960 → 1,020 W per GPU from 3 s sampling).
- NVIDIA 800 VDC architecture and multi-timescale energy storage: developer.nvidia.com blog posts (2025).
- Data-centre build cost $11.3 M/MW (JLL 2026) and electrical share 40–50 %: trade-press summaries (datacentres.com,
  ulegroup.com). Treat as SOURCED-secondary.
- ICCU campaigns: NHTSA PE23011 closing resume; recall reports 24V-204 and 24V-868; TSB 26-EV-004H (warranty
  extension Z14), static.nhtsa.gov.
- GaN dynamic R_ds(on) lifetime projection (< 10 % over 25 years under spec): EPC news release on in-situ R_ds(on)
  characterisation; JEDEC JEP180 DHTOL context from TUM / IEEE PELS pages.
- Automotive crossover MCU with 8/16/32-bit SDRAM-200 and HyperRAM: vendor part pages and fact sheet.
- Public GPU power datasets: NLR/OpenEI "Dataset of Generative AI Workload Power Profiles" (5/10 Hz, 2026-03-31);
  MIT Supercloud Dataset (100 ms GPU sampling); ClusterWise (OLCF Summit, CC BY 4.0).

*Stop here, per the brief.*
