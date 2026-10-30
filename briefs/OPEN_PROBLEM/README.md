# Open problem brief: what does on-vehicle memory buy in the battery and power-conversion domain?

**Everything learned so far, what we are still trying to prove, and where we think we might be blind.**

**Licence:** public domain (CC0). **Date:** 2026-10-30.
**Companion repository:** <https://github.com/kylefoxaustin/battery-soh-finetune> (code, data pipelines,
pre-registrations, results and an independent review for every experiment named below).

---

> ## ▶ START HERE: instructions for the reader
>
> You are being asked for a **fresh angle**, not a re-run. A long, careful programme has tested the obvious
> hypotheses and most of them failed. We think we may be asking the wrong question, or measuring the wrong
> quantity. Your job is to find out.
>
> 1. Read this document end to end. It is self-contained.
> 2. Clone the repository. Skim `results/RESEARCH_DOSSIER.md` and `results/X/README.md` for anything you want to
>    verify. Every number here has a source file there, except where marked otherwise.
> 3. **Produce one file, `ANGLES_REPORT.md`,** with the five sections in §12 below.
> 4. You **may** run small exploratory checks (minutes of compute, public data) to support or kill an idea. Label them
>    EXPLORATORY. **Do not** run a full pre-registered experiment until the reviewer approves one.
> 5. Follow the rules in §11. The most important one: a pleasing number is a suspected defect until gated.
> 6. Stop after the report.

---

## How to read this document

| § | Contents |
|---|---|
| 0 | The question in one page |
| 1 | The claims we are trying to explain |
| 2 | The hardware under study (described generically) |
| 3 | What is established |
| 4 | What is ruled out, and why |
| 5 | The full experiment ledger |
| 6 | Mistakes we made and caught, so you do not repeat them |
| 7 | The independent analysis of GaN in AI servers, and what transfers |
| 8 | The hypothesis map: what is tested, what is not |
| 9 | Angles we have **not** tested (seeds, not conclusions) |
| 10 | Data, tools and constraints |
| 11 | Rules of engagement |
| 12 | What we want back from you |

---

## 0. The question in one page

There are two hardware tiers for an electric vehicle's battery and power-conversion domain. **Both contain the same
real-time control engine**, so the fast control loop is identical on both:

| | **Tier M** (microcontroller) | **Tier A** (applications processor) |
|---|---|---|
| Fast control loop | ~1 µs control interrupts on several small cores, high-resolution PWM, fast ADCs | **the same engine** |
| On-chip working memory | ~3 MB SRAM (plus 33–41 MB non-volatile code memory) | on-chip SRAM, plus… |
| External memory | optional octal xSPI HyperRAM: 200 MHz, ≤ 128 MB window, ~0.4 GB/s peak | **LPDDR5, 32-bit, 4,266 MT/s: 12.0 GB/s read, 4.3 GB/s write (measured, 4 cores)** |
| General-purpose cores | real-time cores | adds several Cortex-A55-class cores |
| OS model | RTOS, one certified image | MMU, several isolated software domains, A/B images |

**An EV manufacturer has chosen Tier A for battery, charging and power conversion** and claims specific, economically
large benefits (§1). It will not say what function delivers them, on what timescale, or with what data.

**We have been trying to find a data-backed mechanism, reproducible on public data, that explains why the DRAM-based
tier beats the microcontroller tier in this domain.**

**The skeptic's objection we must answer:**
> "In our market, regulation already requires battery telemetry to be uploaded every 30 seconds, and the cloud runs
> all fleet analytics. So what does an application processor with DRAM do that a microcontroller cannot?"

A related trap: any answer that would make *every* microcontroller in every vehicle obsolete proves too much. If it
were true, the market would already have moved. **The answer has to explain why some designs need Tier A and most do
not.**

**Where we are after ~25 pre-registered experiments:**

- The **architectural** case holds: bandwidth (~30× read), history retention (minutes to hours versus seconds), and
  isolated, separately updated software domains.
- Per-cell knowledge earns **two modest, real effects**: a much smaller and more predictable charge-limit safety
  margin, and an early warning of which cell is about to hit its capacity knee.
- **Every route to a large, battery-specific economic number has failed or come out far too small**:
  accuracy, efficiency, capacity bounds, fault detection, reserve release.
- The manufacturer's largest claim (§1, C2) is **unexplained** by anything public data can show.

**We suspect we are measuring the wrong quantity, or looking in the wrong place.** That is what we want you to find.

---

## 1. The claims we are trying to explain

Statements made by an EV manufacturer, verbally, without supporting data. We treat them as **hypotheses about what
it sees**, not as facts.

| # | Claim | Our current reading |
|---|---|---|
| **C1** | "A 1 °C reduction in battery charging temperature is worth about **$100 per vehicle**." | Plausible at the optimistic end (§3.7: model median $58 per kelvin). |
| **C2** | "We can take the reserve that must be held back (about **20 %**) down to about **5 %** and deliver the same customer benefit." | **The big one** (§3.7: ~$1,700 per vehicle if it is an uncertainty reserve). Unexplained (§4). |
| **C3** | "Putting both the charging curve and the discharge curve on one processor removes **two ECUs**." | ~$148 per vehicle in a cost model (§3.7). Needs no battery theory. |
| **C4** | "A **very small neural network running alongside the µs power-conversion interrupt** gives a better result than static tables." The real-time cores in both tiers have a **128-bit vector datapath** suited to this. | Untested in its dynamic form (§8, §9). |
| **C5** | "We could use a microcontroller, but it would be **more costly than an MPU with DDR**." | Consistent with memory economics (§3.2). |
| C6 | "Cooler charging, the efficient interrupt and other things together get us there." | Not quantified. |

### 1.1 Which reserve does C2 mean?

There are at least three reserves in a battery, and they behave very differently:

| Reserve | What it protects | Who decides it | Can on-vehicle analysis shrink it? |
|---|---|---|---|
| **Durability reserve** | Energy hidden from the driver and released over life so reported energy stays above a regulatory floor. *(From memory, verify: UN GTR 22 / Euro 7 require ~80 % certified energy at 5 years / 100,000 km, and an in-service-checked on-board energy monitor.)* | The regulator, in effect | Only by slowing real degradation. Our model says cooling cannot do it (§3.7). |
| **Uncertainty reserve** | Energy held back because the weakest cell's true remaining energy is not known precisely | **The manufacturer's own engineering judgement** | Yes, in principle, through better estimation. **Our working hypothesis for C2.** |
| **Low-state-of-charge (bottom) reserve** | Headroom below "0 %" so the weakest cell does not hit its cut-off voltage under load (voltage sag), especially cold | The manufacturer | Possibly through better **resistance and power-capability** knowledge. **Never tested** (§9, seed S1). |

**Our reasoning for the uncertainty reading:** a manufacturer cannot tell a regulator "trust us, the durability
reserve is now 5 %"; the regulator checks reported energy in service. An uncertainty reserve, though, is the
manufacturer's own call. **We have not ruled out the third reading, and we now think we should have tested it first.**

---

## 2. The hardware under study (generic)

### 2.1 The shared real-time control engine

- Several small vector cores, each running a power-conversion control interrupt at about **1 µs** (earlier designs managed roughly 5–7 µs).
- High-resolution PWM (~100 ps edge placement) and fast ADCs.
- About **4 million control interrupts per second** in total.
- The engine can **"farm"** its own telemetry: copy a fraction of each interrupt's data out by DMA without disturbing
  the loop. Moving ~3.2 MB/s this way is confirmed easy. The ADC hardware caps raw converter telemetry at very roughly
  **60 MB/s**.

### 2.2 Farmed telemetry rates (DERIVED, arithmetic)

| Case | Rate | 10 s resident |
|---|---|---|
| 10 % of interrupts × 8 bytes | 3.2 MB/s | 32 MB |
| 100 % of interrupts × 8 bytes | 32 MB/s | 320 MB |
| 800 V on-board charger + interleaved DC-DC, all phases at 1 MS/s | 18–42 MB/s | 180–420 MB |
| ADC hardware ceiling | ~60 MB/s | ~600 MB |
| 96-cell pack, every cell at 1 kHz | 0.26 MB/s | 2.6 MB |
| 96-cell pack at 10 Hz (typical BMS) | 0.003 MB/s | — |

**Converter telemetry is two orders of magnitude larger than cell telemetry.** At 3.2 MB/s continuous that is about
276 GB per day, against a commonly cited connected-car data budget of ~17 MB per day (ASSUMED). It cannot go to the
cloud at any price.

### 2.3 What Tier A adds

- **Memory** (§3.2): bandwidth and capacity for history.
- **An MMU and several cores:** separately certified software domains (real-time control; connectivity and security
  with TLS/PKI and secure over-the-air updates with rollback; regulated reporting; analytics) that can each be updated
  without re-opening the others' safety case.
- **A/B images** for secure updates with rollback (pure memory, no compute).

### 2.4 The customer-side picture we inferred for C4 (unverified)

A tiny network (hundreds to tens of thousands of multiply-accumulates) either:

1. **runs in a background loop (~1 kHz)** and writes per-unit compensation coefficients into a small table that the
   µs loop reads (the µs path is untouched); or
2. **runs inside the interrupt** and decides which cycles are worth keeping, a learned reduction of the telemetry
   stream ("better than static tables" = learned rather than hand-designed reduction); or
3. both: it adapts local control parameters **and** sends reduced findings to fleet servers, which return improved
   priors.

On the vector cores, a ~500-MAC detector fits in ~0.4 µs and a ~4,300-MAC model in ~0.7 µs at 800 MHz. An external
NPU's offload latency would break a 1 µs deadline. These are engineering estimates, not measurements.

---

## 3. What is established

Tags: **MEASURED** = ran it, gated in the same run; **DERIVED** = arithmetic or replay on stated inputs;
**ASSUMED** = stated stand-in; **SOURCED** = from a document.

### 3.1 Compute is not the constraint (MEASURED, 6-core A55 board)

| Workload | Cost |
|---|---|
| 214 k-parameter LSTM state-of-health model, int8 | 220 KB; **22.8 ms** per inference on one core |
| Per-cell charge-limit evaluation | **1.50 µs** at 96 cells · 5.83 µs at 396 · 14.75 µs at 1,000 · **52.1 µs at 3,564**; 10 bytes of state per cell; ~1 % of one core at 100 Hz for 3,564 cells |
| On-device training: optimizer state | last layer 520 B · head 66,568 B · full 1,713,160 B (Adam) |
| On-device training: peak memory increase | **27–30 MB** last-layer · **59 MB** full retrain |

**Implication:** arguing from compute (MIPS) loses. Inference and limit enforcement fit any tier. Only **training,
history and multi-domain software** need DRAM-class memory.

### 3.2 Memory: the fair comparison (MEASURED / SOURCED)

The fair comparison is **not** DRAM versus on-chip SRAM ("nobody builds a 124 MB SRAM microcontroller" is true but a
strawman). It is DRAM versus a microcontroller **with external HyperRAM**.

| | Tier M on-chip | Tier M + HyperRAM | Tier A LPDDR5 |
|---|---|---|---|
| Capacity | 3 MB | 8 MB on the evaluation board; 128 MB maximum window | GB-class |
| Read bandwidth | — | ~0.4 GB/s peak (theoretical) | **12.0 GB/s** measured, 4 cores (5.21 GB/s one core) |
| Write bandwidth | — | ~0.4 GB/s peak | **4.3 GB/s** measured, 4 cores (1.60 GB/s one core) |
| History at 3.2 MB/s farmed | ~1 s | ~2.5 s (8 MB), ~40 s (128 MB) | ~5 min per GB raw; hours if decimated |
| History at 32 MB/s | — | ~4 s at 128 MB | ~30 s per GB |

- **Ingest is not the bottleneck for an EV.** ~32 MB/s fits in HyperRAM (8 % of its bandwidth).
- **Re-reading is.** Analysing a window ten times means ~320 MB/s: **80 % of HyperRAM, 3 % of LPDDR read bandwidth.**
- SRAM density has stopped scaling at recent process nodes; commodity DRAM is roughly two orders of magnitude cheaper
  per bit (SOURCED, general industry knowledge).

### 3.3 Per-cell resistance buys a smaller, more predictable charge-limit margin (DERIVED, replay)

Experiments X2-F and X2-S. The design that finally worked: every limiter carries its own safety margin κ, calibrated on
half the vehicles; safety is judged against an **independent per-cell reference** built from current steps no limiter
sees; scored on held-out vehicles.

| Limiter | Margin needed to stay safe | Margin on unseen vehicles |
|---|---|---|
| **Per-cell resistance, correct cells** | **κ ≈ 1.10 (~10 %)** | **holds** (unsafe frames 0.08 % → 0.03 %) |
| Per-cell resistance, cells shuffled | κ ≈ 1.20 (~20 %) | holds |
| Min/max pack scalars | **κ ≈ 1.35–1.45 (35–45 %)** | **does not hold** (0.05 % → 0.23 %) |

- **Admitted charge current at equal held-out safety: about +2.5 %** (fine 0.01 κ grid, exploratory, CI 2.1–2.8 %).
  Correct cells beat shuffled cells by **~+6 percentage points**.
- **Replicated in direction** on a second LFP dataset (28 systems): correct beat shuffled in **8 of 8** systems
  (+5.2 pp). Not formally interpretable: min/max could not be made safe there at any κ ≤ 2.
- **Chemistry-dependent.** On an NMC-like fleet the binding cell is already the max-voltage cell 89 % of the time, and
  the gain vanishes. Flat LFP voltage curves make voltage a poor guide to the worst cell; per-cell resistance a good
  one.
- Per-cell resistance is a **stable, real property**: split-half rank correlation across cells 0.94–0.99, worst cell
  ~1.2× the median.

**This is the single most robust positive in the programme. It is small as a charge-rate number, but large as a
margin number.** We have only ever cashed it out at the **top** of charge.

### 3.4 Per-cell identity gives an early warning of capacity knees (DERIVED, lab data)

Experiment X6, on 251 lab cells with weekly capacity checks (label noise 0.24 %):

- **About 4 in 5 capacity knees start in a cell that is not the weakest** one check earlier. A min/max view, which
  watches only the weakest cell, is structurally blind to them.
- Warning AUC one check ahead: min/max view **0.44** (its structural ceiling 0.70), per-cell trend 0.61, per-cell trend
  plus voltage-curve features **0.70**, the same with cell identities shuffled **0.52**.
- **Cell identity adds +0.18 AUC** (CI 0.06–0.28). The first positive identity effect in the programme.
- **It is cheap:** voltage-curve history adds nothing clearly beyond a four-point capacity trend per cell.
- **It is weak:** at a 10 % false-alarm rate it catches 25 % of knees, with 11 % precision.

### 3.5 Telemetry cannot leave the vehicle (DERIVED)

Converter telemetry at 3–60 MB/s is four to six orders of magnitude above any plausible uplink budget. Any analysis of
it happens on the vehicle or not at all. The 30-second regulatory upload is cell-level and pack-level data, a different
stream.

### 3.6 The architectural case (structural, not quantified)

Four software domains with different certification levels and update cadences are converging in the battery box:
real-time control (high integrity, rarely updated), connectivity and security (security cadence), regulated reporting
(regulatory cadence) and analytics (changes most often). On one microcontroller image, patching analytics re-opens the
safety case for control. An MMU plus isolation decouples them, and needs DRAM to exist. **This argument is sound but
applies to everyone, so on its own it proves too much (§0).**

### 3.7 A lifetime cost model makes the claims mutually consistent (DERIVED, Monte Carlo, all inputs ASSUMED)

200,000 draws; 75 kWh usable pack; $90–140 per kWh.

| Claim | Value (p10 / p50 / p90) | Reading |
|---|---|---|
| C1: 1 K cooler charging | **$26 / $58 / $124 per K** | $100 sits near the 75th percentile. Arrhenius fade (Ea 30–65 kJ/mol) on the charge-heat share of fade (15–60 %). Pays in full only if durability, not range, sizes the pack. |
| C2 as an **uncertainty** reserve, 20 % → 5 % | **14.8 kWh of cells avoided: $1,400 / $1,700 / $2,000** | Needs a usable-energy estimate ~**4× more precise**. 20 % → 10 % is worth ~$1,200. |
| C2 as a **durability** reserve | — | **Not reachable by cooling.** 15 K cooler cuts lifetime fade only ~21 % (median); 25 K, ~29 %. Cooling only shrinks the heat-driven share. |
| C3: two ECUs removed | **$132 / $148 / $165** | Silicon, PCB, housing, assembly, harness, amortised engineering; mass effect only ~$4. |

**C2 dominates by an order of magnitude.** That is why most of the late programme went after it.

---

## 4. What is ruled out, and why

| Route | Result | Why it failed |
|---|---|---|
| **Per-vehicle model fine-tuning for accuracy** | Hurt 14 of 20 cars; no robust benefit at 94 units with a rolling protocol | Fleet model already near the label-noise floor; a no-model "average of recent labels" matched the one near-term gain. *(Independent review later found a bytes-of-state shrunken running offset passes at 0–5 k km; post-hoc, never confirmed.)* |
| **Per-cell data tightening a capacity bound** | INCONCLUSIVE; even an oracle recovers only −0.6 to +1.5 % of capacity | Field labels are derived, with 3–4 % noise; the test was nearly unpassable by construction. |
| **Per-cell data detecting faults min/max misses** | Untested in practice | The "98 % overlap" result was a near-tautology of the metric definition. |
| **Per-cell flagging of teardown-confirmed faulty packs** | Weakened to a hypothesis | Faulty and normal records were produced differently (sentinel frames 335/335 vs 17/58; peak temperature 41 vs 31 °C). |
| **Per-cell charge limiting with one shared limit map** | No benefit (0.00–0.01 %) | A design flaw: one shared map makes per-cell ≥ min/max by construction and removes the mechanism per-cell limiting exists for. |
| **"+5.5 % faster charging" from per-cell history** | **Withdrawn** | A shuffle control we ran: wrong-cell resistances gained just as much (+6.0 % vs +5.5 %). The design rewarded any margin-free limiter. |
| **Quasi-static converter efficiency from history** | Not needed | Replay of a GaN multiphase converter over a real drive cycle: a **load-indexed factory table** stays within **0.02–0.99 %** of optimal loss in every case (end of life, −10 °C, 70 °C ambient, aggressive ageing). In absolute terms ~0.003 kWh per 100 km. |
| **Releasing an uncertainty reserve through per-cell history** | **Not supported on public data** | On lab-measured cells: per-cell history reaches **1.50×** precision over a pack-mean estimator, **1.82×** with voltage-curve features. **A min/max view gets the same 1.5×, and so does a shuffled control.** 4× is never close. The reserve is set by unpredictable late-life knee **size**. |
| **Knee warnings shrinking the reserve** | No (G = 1.02) | Both views flag the worst targets; a typical post-onset drop correction (2.8 %) cannot close ~16 % tail errors. |
| **Cooling releasing a durability reserve** | Not reachable (§3.7) | Physics of Arrhenius on the heat-driven share. |
| **Lead time over the vehicle's own BMS warnings** | Not supported | Pre-registered identification rule failed; neighbour-referenced drift doubled false alarms. |
| **Per-cell temperature limiting in the cold** | Unanswerable | No public dataset charges genuinely cold to full; cold sessions in the field are partial top-ups that stop ~250 mV short of the limit. |

---

## 5. The full experiment ledger

All pre-registered unless marked. Code, pre-registrations and results are in the repository.

| ID | Question | Data | Verdict | Key number |
|---|---|---|---|---|
| Study 1 | Can a state-of-health model run and be fine-tuned on-device; does a car's own early data help? | EVBattery, 20 held-out cars | Feasible; **no gain** | 220 KB / 22.8 ms; fine-tuning hurt 14/20 |
| Study 2 | Per-unit adaptation at scale, incl. rolling re-tuning | Changan 300-EV fleet, 94 units, 4-fold | **No** | No variant robustly beats the frozen fleet model; persistence matched the one gain |
| D | Training footprint on the board | — | MEASURED | 520 B last-layer state; 27–59 MB peak increase |
| E | Can per-cell data tighten a worst-case capacity bound? | Changan; 27-module BESS | INCONCLUSIVE | Oracle ≤ ~1.5 %; resolution ~0.9 % |
| F | Does per-cell data catch a failing cell early? | Changan per-cell | Forecast underpowered (3 positives) | Diagnosis signatures seen (sense-tap, sensor offset, module shift); unconfirmed |
| G.1 | Is there public per-cell data with located fault labels? | Literature search | NO-GO | No public set injects cell-located electrical faults on a ≥ 4-cell string |
| G.2 | Per-cell drift vs min/max on teardown-confirmed faulty packs | Beihang, 58 faulty / 335 normal | Weakened | AUC 0.59 vs 0.52 early; cohort confound |
| H / H2 | Per-cell vs min/max charge limiting | Changan (NMC); 3,564-cell LFP grid battery | No benefit (by construction) | 0.00–0.01 %; board 1.5–52 µs |
| X2 | Per-cell limiting with history-learned resistance | Changan | Withdrawn (+5.5 % was margin asymmetry) | shuffle 6.0 % vs real 5.5 % |
| X2-C | Confirmation on new data | Beihang QAS | NOT INTERPRETABLE; shuffle failed | real 10.8 %, shuffled 11.7 % |
| **X2-F** | **Fair comparison: own margins, independent reference** | Beihang QAS | NOT INTERPRETABLE (narrowly); **mechanism shown** | margin ~10 % vs 35–45 %; +2.5 % at equal safety (fine grid) |
| X2-S | Replication | 28 LFP systems (returned units) | NOT INTERPRETABLE; direction 8/8 | D +5.2 pp |
| X2-M2, X2-P | Power-cell map; active probing for resistance | McMaster 72S | 0.00 % at the dataset's 6C; usable R needs ~80 steps ≥ 0.3C | — |
| X3, X3b | Lead time over the BMS; neighbour-referenced drift | BATSS, BatICM, healthy fleet | Not supported; no reduction | false alarms 43.5 vs 21.8 per 100 vehicle-days |
| convsim | Converter efficiency vs adaptation speed | Real WLTC 3b cycle, assumed GaN converter | **Load-indexed table suffices** | within 0–1 % of optimal loss |
| lifecost | Are C1–C3 mutually consistent? | Monte Carlo | Consistent; C2 dominates | $58/K; $1,700; $148 |
| X4 | Usable-energy precision from per-cell field data | One Changan vehicle, 96 cells, 66,000 km | NO GAIN; labels too noisy | ~6 % label noise; labels rise with mileage |
| **X5** | **Usable-energy precision on lab-measured cells** | ISU-ILCC, 251 cells, 61 synthetic 4-cell packs | UNCLEAR | **1.50× (= min/max = shuffled); best 1.82×** |
| **X6** | **Can history forecast a capacity knee?** | ISU-ILCC | UNCLEAR | identity +0.18 AUC; reserve gain 1.02 |

---

## 6. Mistakes we made and caught (please do not repeat them)

Each of these produced a pleasing number that did not survive.

1. **Circular safety references.** If a limiter is its own safety reference and carries no margin, any margin-free
   limiter looks better, right or wrong. Fix: independent reference built from data no limiter sees.
2. **Designs that guarantee the answer.** A single shared limit map made per-cell ≥ min/max by construction.
3. **Tautological metrics.** "Per-cell and min/max detect 98 % of the same anomaly-days" followed from the definition.
4. **Cohort confounds.** Faulty and normal records collected differently (sentinel values, temperature, record
   structure) produce strong AUCs on the artefact alone.
5. **Shuffle controls that cannot fail.** Permuting whole per-cell series leaves "minimum over cells" unchanged.
   Permute cells independently at every time step.
6. **The wrong tail.** A reserve protects against **over**-statement of usable energy: use `q(1−α)(U_pred − U_true)`.
   We first scored the other tail.
7. **Derived field labels.** Capacity labels derived from field telemetry carried ~6 % noise and rose with mileage.
   Lab reference tests (≤ 1 % noise) are required for precision questions.
8. **Labels that are model outputs.** One "measured per-cell capacity" dataset turned out to be model estimates from
   the same telemetry.
9. **Untypical samples.** A single vehicle's dramatic weak-cell drift was not typical of the fleet.
10. **Unsourced sizing.** An early "hundreds of MB" working-set estimate rested on 225 MB of neural-network weights
    (falsified by ~144×: a real battery model is ~270 KB) and an uncited "1 MB per cell" (measured per-cell estimator
    state is ~10 bytes).
11. **Strawmen against the other tier.** Comparing DRAM with on-chip SRAM instead of HyperRAM; comparing on-board
    adaptation against "parameters frozen for 30 s" when any microcontroller indexes a table by load every cycle;
    applying a server-scale data rate (1.2 GB/s) to an EV converter (~32 MB/s).
12. **Tooling traps.** The public Changan samples are RAR5; `7z` reports "unsupported method", which looks like
    corruption. Use `unrar` or Python `libarchive-c`.

---

## 7. The independent analysis of GaN in AI servers

Starting point: *EE Times*, "AI Power Demands Push GaN into Data Center Design" (Sept 2026), reporting EPC's view.

| Number | Meaning |
|---|---|
| 5 kW | per GPU within two years, at under 1 V |
| 10,000 A | of core current |
| 800 V | DC into the rack; 1,200–2,000 V and multilevel next |
| 3 → 10 MHz | GaN switching today → roadmap |
| 5 % | AC-to-core efficiency gain claimed for GaN; the number the business case rests on |

A separate analysis of that article reached **the same two-tier split** we reached for EVs:

- **Data:** 100 phases × 6 channels × 10 kS/s × 16 bit ≈ 12 MB/s per GPU, ~100 MB/s per 8-GPU board, ~1.2 TB/s per
  100,000-GPU site. "No data-centre management system ingests that."
- **A microcontroller's "40 MB" is 2–3 MB of data** after OS A/B images and buffers: statistics, not history.
- **"Streaming statistics cannot be re-binned: a question nobody asked at firmware-build time is unanswerable
  later."** Retention is about not pre-committing to which questions you can ask.
- **The mechanism with a clear efficiency payoff there is anticipatory phase shedding.** A GPU at 20 % load runs most
  efficiently on ~25 phases, but a step to full load arrives in ~100 µs and re-enabling phases takes 10–50 µs each. A
  controller without a forecast must keep extra phases alive. With seconds of history plus a scheduler hint, it can
  pre-enable phases 200 µs–1 ms ahead and shed further at light load. Estimated "order of a point" of AC-to-core,
  uncharacterised.
- **Architecture:** learn locally, aggregate globally. Fast loop on the controllers; seconds-to-months of history and
  forecasting on a board-level processor with DRAM; cross-board learning in the fleet.
- **Its own risks:** the server management controller may grow into the job; voltage-regulator ASICs may absorb the
  middle tier; locally adapting controllers are harder to trust; the gains may be smaller than the story.

**What transfers to EVs:** the split, the retention argument, the "cannot be re-binned" argument. **What may not:**
EV load steps are less predictable than GPU kernel dispatch, so the anticipation payoff is unproven for EVs.

---

## 8. The hypothesis map

| Mechanism that could justify Tier A | Status | Best evidence |
|---|---|---|
| Model accuracy from per-vehicle learning | **Ruled out** | Studies 1–2 |
| Quasi-static converter efficiency | **Ruled out** | convsim |
| Capacity-bound tightening | **Ruled out / unresolvable** | E |
| Uncertainty-reserve release via per-cell history | **Not supported on public data** | X5, X6 |
| Durability-reserve release via cooling | **Ruled out by physics** | lifecost |
| Per-cell charge-limit margin | **Supported, small as charge rate** | X2-F, X2-S |
| Knee early warning | **Supported, weak, cheap** | X6 |
| Fault diagnosis (sense-tap, sensor offset, module shift) | Seen, **unconfirmed** | F |
| Bandwidth / retention / domain isolation | **Holds architecturally**; not quantified economically | §3.2, §3.6 |
| ECU consolidation | Modelled ~$148 | lifecost |
| **Dynamic in-loop converter adaptation** (soft-switching tracking, adaptive loop tuning) | **Untested** | — |
| **Anticipatory control** (pre-positioning before load or charge events) | **Untested for EVs** | server analysis |
| **Low-SOC (bottom) reserve via power capability** | **Untested** | — |
| **Cell coupling in real packs** (weak cell runs hotter, degrades faster) | **Untestable on public data** | — |
| **Learned telemetry reduction for fleet learning** | **Untested** | — |

---

## 9. Angles we have NOT tested (seeds, not conclusions)

**Please do not anchor on these.** They are what we would try next. Your value is in what is *not* on this list.
For each, we note why our experiments could not have seen it.

| # | Seed | Why we could have missed it | A possible public-data test |
|---|---|---|---|
| **S1** | **C2 is the bottom (low-SOC) reserve, and it is set by power capability, not energy.** The weakest cell hits its cut-off voltage under load at low SOC, especially cold. Usable depth is limited by `V_cell − I·R_cell` at the bottom, not by capacity. | X5/X6 tested **capacity** estimation. Our only robust positive is **per-cell resistance** (X2-F), which we only ever cashed in at the **top** of charge. | Replay per-cell discharge near low SOC (Changan, Beihang, Schaeffer): how much deeper could a pack discharge at equal safety if each cell's R were known, versus min/max? Same X2-F design, mirrored. |
| **S2** | **"Smaller battery, same benefit" is about charge speed, not reserve.** A smaller pack that charges faster can deliver the same trip time. | We sized everything by energy. | Model trip time for a pack 10–20 % smaller with a charge curve improved by X2-F-style margins. |
| **S3** | **Lithium-plating avoidance during fast charge.** Plating limits are cell-specific and temperature-dependent, and the main constraint on fast-charge current. Detection uses each cell's post-charge voltage relaxation (minutes of high-rate per-cell data), which is history- and memory-heavy. Links to C1 and C6. | No experiment looked at plating or relaxation. | Lab plating datasets with relaxation curves, if any exist publicly. |
| **S4** | **Active balancing plus per-cell capacity knowledge.** Usable energy is set by the weakest cell; with active balancing and known per-cell capacities, usable energy can rise by up to the cell-to-cell spread. | We measured spread (1.3 % early, ~40 % late in lab cells; a few % in field packs) but never valued it. | Value field spread distributions under passive vs active balancing. |
| **S5** | **Predictive thermal management for charging** (pre-conditioning and cooling ahead of a known fast-charge session) as the source of "1 °C". | We valued 1 °C (§3.7) but never asked what achieves it. | Thermal model + fast-charge session data: how much peak cell temperature does forecast-driven pre-cooling remove? |
| **S6** | **Dynamic in-loop adaptation** of an 800 V → 48 V dual-active-bridge or LLC (soft-switching range depends on load and on component values that vary ±10 % per unit and drift with age). | convsim was quasi-static, a 48 V → 12 V buck. | Cycle-level simulation; the deciding comparison is a **factory-calibrated per-unit table** (Tier M can hold it) vs **continuously re-learned** (Tier A). |
| **S7** | **Learned telemetry reduction** ("the farming network") decides what to keep under a fixed uplink budget; the value is fleet-level detection of rare batch defects. | Never tested. | Information retained under fixed budget vs fixed decimation, on public fault datasets. |
| **S8** | **Coupling.** In a real pack the weak cell runs hotter and degrades faster: positive feedback that synthetic packs cannot show. | Every clean-label dataset tested cells separately. | Look for any public pack dataset with per-cell temperature and voltage over ageing. |
| **S9** | **Certified state-of-health as a product** (battery passport, residual value, warranty). Value accrues at resale or second life, not in the first owner's range. | We only valued first-life cells. | Literature on used-EV price sensitivity to certified SoH. |
| **S10** | **The claims are mainly ECU consolidation and software-domain isolation**, and the battery-AI framing is secondary or aspirational. | We took the battery claims at face value. | Cost and weight model for the consolidation alone. |

---

## 10. Data, tools and constraints

### 10.1 Public datasets used (licence matters)

| Dataset | Licence | Contents | Limits |
|---|---|---|---|
| **Changan 300-EV** | CC BY-NC-SA 4.0 (non-commercial) | 300 vehicles, 96 per-cell voltages + 32 probes at 10 s, up to 4 years | Capacity labels must be derived (3–6 % noise); 5.6 % malformed frames; RAR5 samples |
| EVBattery | CC BY 4.0 | min/max/mean only | no per-cell |
| **Beihang QAS / DTI** | CC BY 4.0 | 110 / 85 cell voltages at 30 s; teardown-confirmed fault labels | cohort confound between faulty and normal; no timestamps |
| Weihai grid BESS | CC BY 4.0 | LFP, 9 racks × 396 cells | climate-controlled, so no cold data |
| McMaster 72S | CC BY 4.0 | per-cell voltage and temperature, drive cycles, regen only | two dead thermistors; no charge sessions |
| BATSS | CC BY 4.0 | 10-cell string, 55 thermocouples | thermocouple-to-cell mapping undocumented |
| BatICM EV faults | MIT | 4 EVs, per-cell | small |
| BatICM cell-to-pack | CC BY 4.0 | 6 lab packs aged as packs | pack capacity only, no per-cell capacity |
| Schaeffer LFP | CC BY-NC 4.0 | 28 home-storage systems, 8S | all returned to manufacturer as faulty |
| Yuasa second-life BESS | MIT | 324 cells | per-cell "capacities" are model estimates |
| UMich parallel modules | CC BY 4.0 | 78 3P modules | parallel, so no weakest-cell limit; no cell IDs |
| **ISU-ILCC** | CC BY 4.0 | **251 cells, weekly C/5 reference tests, 0.24 % label noise** | cells tested separately (no coupling) |
| WLTC class 3b | EUPL (JRC `wltp` repository) | real drive cycle, 1 Hz | — |

**Gap we could not fill:** no public dataset has **per-cell capacity re-measured inside a pack whose cells aged
together**, or **per-cell telemetry paired with located, independent fault labels**.

### 10.2 Hardware
A 6-core Cortex-A55 development board with LPDDR, used for all MEASURED timings (governor pinned, process census
before and after each run).

### 10.3 Environment constraints, if you work from a restricted sandbox
Some environments can reach `github.com` and `pypi.org` but not data repositories (Zenodo, figshare, Mendeley).
Plan downloads accordingly.

---

## 11. Rules of engagement

1. A pleasing number is a suspected defect until gated.
2. Tag every figure MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED.
3. Pre-register before analysis code; never move a threshold after seeing results; number every deviation.
4. Every comparison against the microcontroller tier must use **its best option** (HyperRAM, load-indexed tables,
   factory per-unit calibration), not a strawman.
5. Every per-cell claim needs a **shuffle control** that scrambles cell identity at every time step.
6. Every safety claim needs an **independent reference** and **held-out units**.
7. Carry dataset licences and caveats onto every verdict.
8. No kWh, cost, range or regulatory claim from a replay without saying it is modelled.
9. A clean negative is a result. So is "this question cannot be answered on public data".

---

## 12. What we want back from you: `ANGLES_REPORT.md`

**A. Red team (≤ 1 page).** Errors in our reasoning, numbers, or experiment designs. Anything in §3 or §4 you think
is wrong or over-stated, and why.

**B. What we are missing (the main deliverable).** A ranked list of mechanisms or framings we have not considered, or
have dismissed too quickly. For each:
- the mechanism, in two sentences;
- why it needs Tier A specifically (memory, bandwidth, isolation, training) rather than Tier M with HyperRAM and
  factory calibration;
- why our experiments could not have seen it;
- the size of the effect, as an order of magnitude, with your reasoning;
- what would kill it.

**C. Test designs** for your top three: public data that exists today (name it, with licence), primary metric,
controls (shuffle, held-out, best-option comparator), and a kill criterion. Pre-registration-ready, but **do not run
them**.

**D. The one question** to put to the manufacturer that would discriminate most between your top hypotheses.

**E. The null hypothesis, stated fairly.** If you conclude that no battery- or converter-specific mechanism justifies
Tier A, and that the case rests only on consolidation and software isolation, say so and argue it.

Stop after the report.
