# Next experiments — ranked plan after the open-problem pass

**Written:** 2026-10-30, as the follow-on to [`results/OPEN_PROBLEM/ANGLES_REPORT.md`](../../results/OPEN_PROBLEM/ANGLES_REPORT.md).
**Licence of this document:** public domain (CC0). **Owner:** the reviewer (Kyle). The running session reads it.

Every item below follows the programme's rules: profile first, pre-register before analysis code, numbered deviations,
every number tagged, no threshold moved after results, licence carried onto every verdict, a clean null is a result.
**Nothing here starts until the reviewer names it in `NEXT_TASK.md`.**

---

## 0. The ranking, and why it is in this order

The ANGLES report concluded that the best-supported explanation of the customer's claims is the null (§E): Tier A is
chosen where the box must host a Linux-class software stack anyway, and the battery/converter mechanisms are upside.
The experiments below are ordered to (a) produce **slide-grade numbers with clean licences** first, (b) measure the one
Tier A capability that is a physical necessity rather than a convenience, and (c) take the best remaining shot at the
customer's C2 last, because its data is non-commercial.

| # | ID | Question | Data (licence) | Cost | Bears on | Can run in parallel with |
|---|---|---|---|---|---|---|
| 1 | **X7** | Does a per-cell electro-thermal observer remove hottest-cell temperature **margin** that probe interpolation must carry, and does a coupled (higher-order) model beat a lumped one? | McMaster 72-cell (CC BY 4.0), in hand | CPU, hours | B.5; the only mechanism test runnable today with a tier readout | FR1, DC1, L1 |
| 2 | **B1** | Can the board sustain a 3.2–60 MB/s ring buffer in LPDDR for minutes, freeze it on a trigger and dump it, while inference and the limiter keep their latencies? What does eMMC sustain, and what is its implied wear-out? | FRDM-IMX95-PRO, synthetic stream | Board, one day | B.3; first **MEASURED** Tier A capability number an MCU cannot match | nothing on the board |
| 3 | **DC1** | With seconds of history at 5–10 Hz, how much rack-side storage energy does forecasting save over a reactive controller when holding synchronous-AI power swings inside a ramp-rate spec? Does any gain need more than 1 s of history? | NLR/OpenEI GenAI workload power profiles (5/10 Hz; US-government data, licence to confirm); MIT Supercloud (100 ms; licence to confirm) | Download + CPU, hours | B.2; the data-centre case | X7, FR1 |
| 4 | **X8** | Mirror of X2-F at the **bottom** of charge: admissible discharge current at low SOC, per-cell R vs min/max, at equal held-out safety (brief seed S1) | Changan (CC BY-NC-SA: research only); Beihang (CC BY) if its frames carry current at low SOC | CPU, hours (replay pipeline exists) | C2 as a power-capability reserve | after O1's label fix if possible |
| 5 | **FR1** | For public HV power-electronics field failures with a known root cause, how long a pre-event window would field data have needed? | NHTSA ODI investigations and Part 573 reports (public domain) | Reading, hours; no compute | B.3's *value* side | X7, DC1 |
| 6 | **O1** | Confirm the shrunken per-unit offset (audit §5 item 1) and fix the Changan label segment-duration bias | Changan strict, EVBattery ds2/ds3 (in hand) | CPU, hours | Closes two audit items; tier-neutral; improves every later Changan result | — |
| 7 | **R1** | Information retained under a fixed uplink budget: learned/adaptive selection vs fixed decimation to min/max + statistics, scored by downstream detectors (brief seed S7) | Beihang (CC BY), BATSS (CC BY), Changan (NC-SA) | CPU, hours | C4's "farming network"; the "cannot re-bin" claim | after X7 |
| — | **L1** | Requirement-arrival ledger (ANGLES §C.1) | EUR-Lex, UNECE, GB/T editions | Reading; a research session, not a code session | B.1 | anything |

**What changes the roadmap most per hour:** B1 (a MEASURED capability number) and X7 (a CC BY mechanism number). **What
bears most on C2:** X8. **What bears most on the data-centre vertical:** DC1.

> **Status 2026-10-30.** **X7 is closed: UNDERPOWERED at the profile stage** (`8a468ad`; no observer fitted; see
> `results/X/X7_profile.md`). The order is now **B1 → DC1 → X8 → FR1 → O1 → R1**, with FR1 and DC1 runnable in parallel
> sessions. B1 has a full Build Brief at [`briefs/B1/README.md`](../B1/README.md). Two lessons from X7 apply to every
> later brief: put the data's *resolution* (sensor quantisation, label noise, probe-max gap) in the profile gate, not
> only its *spread*; and score the quantity a controller would act on (the issued bound, the admitted current), never a
> margin alone.

> **Status 2026-10-31.** **B1 is DONE** (`0c4b61e`; [`results/B1/results_B1.md`](../../results/B1/results_B1.md)):
> all 14 cells hit 3.2 / 32 / 60 MB/s with 0 drops; a 2 GB LPDDR ring holds **671 / 67 / 36 s** by sequence span;
> every dump that fitted the ring verified (26 of 26); the real-time loops stayed within 6.3 % (median p99) of
> baseline; the CPU producer cost ≤ 3.1 % of one core (upper bound on a DMA path); eMMC sustains 164 MB/s but would
> wear out as a ring medium in 0.05–0.95 years (DERIVED, endurance ASSUMED). Reviewer re-derived the rates, depths,
> gates and RT ratios from `results/B1/raw/` and they match. **The capability is measured; its value now hinges on FR1**
> (how long a pre-event window real root causes need), so FR1 moves up. The order is now **DC1 → FR1 (parallel) → X8 →
> O1 → R1**. Full Build Briefs: [`briefs/DC1/README.md`](../DC1/README.md), [`briefs/FR1/README.md`](../FR1/README.md).
> The tier line for FR1 is **80 s** (an MCU with 256 MB SDRAM at 3.2 MB/s, DERIVED); B1's 671 s is the number that
> clears it. Design rule from B1: a whole-ring freeze with a running producer needs at least one burst of headroom over
> the window (two 60 MB/s dumps lost exactly one 1 ms burst at the oldest edge).

> **Status 2026-10-31 (later). DC1 is DONE and accepted** (`cf94244`;
> [`results/DC1/results_DC1.md`](../../results/DC1/results_DC1.md)): **REACTIVE SUFFICES on both workloads**
> (Llama LoRA G 1.022 [1.003, 1.048]; SD 1.001 [0.997, 1.054] at W = 30 s) and **NO HISTORY NEEDED** (a 1 s ramp
> extrapolator matches 30 s of history). The reviewer re-derived G, G_sh, G_∞ and the memory ratio from the per-job E*
> values in `dc1.json` for the primary and three sensitivities; they match, including the fold structure (fold A's
> calibration chose g = 0, so fold-B jobs have G = 1 exactly). **Reading for the roadmap:** the anticipation leg of
> ANGLES §B.2 is not supported on public node-level data — a tuned reactive controller or a 1 s ramp detector, both
> MCU-class, do as well — while the perfect-foresight ceiling (~1.38×) shows the pre-positioning *room* exists and the
> causal predictor is what fails to reach it. The one pre-registered sensitivity where history pays is a 5× looser
> violation budget (SD 1.27×, W* 30 s). What remains Tier-A-specific in §B.2 is the telemetry volume for the spectral
> backstop and the storage-element BMS, neither of which public data can test. Two design notes kept: (i) the
> time-shuffle control collapsed the forecaster to persistence, so it tested "forecast vs none" rather than "ordered vs
> disordered history" — a time-*shifted* window (right values, wrong phase) is the better control next time; (ii) the
> violation budget decides this class of result, so **DC2 (documentary seed, not scheduled):** what compliance window and
> excursion allowance real large-load ramp specs actually use (ERCOT large-load interconnection rules, IEC 61000-3-3,
> utility ramp-rate clauses) — if they average over seconds or tolerate ~0.5 % excursions, DC1's sensitivity is the
> real-world case. **Order now: FR1 → X8 → O1 → R1.** X8 has a full Build Brief at [`briefs/X8/README.md`](../X8/README.md);
> it needs no label fix (it is a voltage/current replay) and can run before O1.

---

## 1. How the reviewer starts one

Paste this into `NEXT_TASK.md`, replacing `<ID>` and the brief path, and set Status to OPEN:

```
1. `git pull` on `main`.
2. Open `briefs/<ID>/README.md` and follow its START HERE box. First stage only: profile + pre-registration, then STOP.
3. Commit the profile and pre-registration with "before analysis code" in the commit message. Do not write analysis code.
4. Set Status to `AWAITING APPROVAL <commit-hash>` and push.
```

After approval the reviewer edits the brief's START HERE box to "APPROVED, run it now" (as was done for X6), and the
session runs exactly what was pre-registered, commits results, README and dossier updates, sets `DONE <hash>`, and stops.

**X7** ([`briefs/X7/README.md`](../X7/README.md), closed), **B1** ([`briefs/B1/README.md`](../B1/README.md), done),
**DC1** ([`briefs/DC1/README.md`](../DC1/README.md), done), **FR1** ([`briefs/FR1/README.md`](../FR1/README.md)) and
**X8** ([`briefs/X8/README.md`](../X8/README.md)) have full Build Briefs. FR1 is documentary and may run in a parallel session; it records its state in its own brief's Status line
and never touches `NEXT_TASK.md`. The others below are skeletons at the level of X6's §3–§4; promote one to a Build
Brief before naming it in `NEXT_TASK.md`. B1 is a capability measurement: its brief fixes the protocol in advance and lets the session continue
from the census to the measurement without a stop when every census gate passes.

---

## 2. Skeletons

### B1 — ring-buffer feasibility on the board (MEASURED)

- **Why.** ANGLES §B.3 argues from arithmetic that a continuous MB/s rolling window can only live in DRAM. The
  roadmap needs the arithmetic turned into a MEASURED number on application-processor silicon: *sustained ingest rate, window length,
  CPU cost, interference with the real-time work, and the eMMC alternative's throughput and implied wear.*
- **Setup.** FRDM-IMX95-PRO, governor pinned, process census before and after (as `run_all.sh`). The dev board has no
  real-time engine, so the "farmed" stream is a **CPU producer** writing fixed-size frames (8 B payload + 8 B
  timestamp, ASSUMED) into an LPDDR ring (`mmap`'d hugepages or `/dev/shm`), at 3.2, 32 and 60 MB/s. That makes the
  producer's CPU cost an **upper bound** on a DMA path; say so on every number.
- **Concurrent load.** Study 1's int8 inference (`e1_inference.py`, 22.84 ms p50 baseline) pinned to one core and the
  H limiter (`h_limiter.c`, 1.50 µs at 96 cells) on another, both running throughout.
- **Trigger.** At a scripted time, freeze the ring and dump the last N s (N = 10, 60, 300) to eMMC; gate by same-run
  checksum of the dumped frames against the producer's sequence numbers (missing or duplicated frames fail the gate).
- **Measure (MEASURED).** Sustained producer rate and drop count over ≥ 30 min at each rate; ring depth achievable
  within a stated memory budget (512 MB, 2 GB); producer CPU % per core; inference p50/p99 and limiter p50/p99 with
  and without the producer; eMMC sequential write MB/s sustained over ≥ 5 min and dump time for each N.
- **Derive (DERIVED, endurance ASSUMED and stated).** Window length per medium at each rate; eMMC years-to-wear-out if
  used as the ring medium at each rate (state the P/E assumption); compare with the ANGLES §B.3 table.
- **Not measured, say so.** HyperRAM and MCU-SDRAM windows (no such board in hand; arithmetic only), the M7 ingest
  path, energy. If an SDRAM-capable crossover-MCU EVK is available, a matching SDRAM ring on it would turn A.2's point into a MEASURED
  comparison; ask the reviewer.
- **Kill.** None needed; this is a capability measurement. Report every number with its bound.

### DC1 — rack anticipation value on public GPU power profiles

- **Question.** Holding a rack's upstream power inside a ramp-rate and dynamic-range spec with a storage element, how
  much less storage energy does a forecasting controller need than a reactive one, and how long a history does it use?
- **Data.** NLR/OpenEI "Dataset of Generative AI Workload Power Profiles" (OpenEI submission 8651, issued 2026-03-31;
  5/10 Hz node power on Kestrel, training and inference, LLM and image generation; confirm licence on the submission
  page before download). Second set: MIT Supercloud (GPU power via `nvidia-smi` at 100 ms; confirm licence). Both
  resolve the 0.2–3 Hz band of the swings; **neither is phase-level or ms-resolution**, so phase-level anticipation is
  out of scope and must be said to be.
- **Profile first.** Per trace: sampling rate, duration, swing amplitude (p5–p95 of power), dominant periodicity
  (spectral peak), step rise times. Power gate: at least 10 traces with p95−p5 ≥ 30 % of peak.
- **Spec (ASSUMED, fix in the pre-registration).** Ramp-rate limit as a fraction of peak per second and a dynamic range
  band, in the style of the utility constraints described by Choukse et al. (arXiv 2508.14318). Report sensitivity at
  two more settings.
- **Controllers (all causal except the oracle).** K0 reactive: feedback on measured bus power, fixed pre-charge.
  K1 forecaster: predicts the next ΔT of load from the last W s (W = 1, 5, 30) with a fixed-form seasonal/AR predictor
  specified in the pre-registration, pre-positions storage. K1-sh: K1 with the history window time-shuffled (destroys
  periodicity; the "history" shuffle control). K∞ oracle: knows the future (ceiling).
- **Primary metric.** Minimum storage energy E (J) and power P (W) at which upstream power violates the spec in
  ≤ 0.1 % of frames, per controller, per trace; G = E(K0) / E(K1). Secondary: the smallest W at which G saturates
  (the memory readout: if W = 1 s saturates, the mechanism holds but needs no history).
- **Controls.** K1-sh must not approach K1 (G_sh < 1.1); held-out traces (fit any predictor parameters on half the
  traces, score on the other half); the Tier M comparator is K0.
- **Decision.** FORECASTING SAVES STORAGE if median G ≥ 1.25 with unit-bootstrap CI > 1 and G_sh < 1.1.
  REACTIVE SUFFICES if G < 1.1. UNCLEAR otherwise. Report separately whether W > 1 s is ever needed.
- **Kill.** G < 1.1, or G_sh ≈ G, or every gain saturates at W ≤ 1 s.

### X8 — the bottom reserve: admissible discharge current at low SOC (brief seed S1)

- **Question.** Mirror of X2-F. At low SOC under load, a limiter must keep every cell above its cut-off voltage. A
  per-cell-R limiter predicts each cell's sag; min/max sees only the current minimum. At equal held-out safety, how
  much more discharge current (power) does per-cell admit, and does the gain survive a shuffle?
- **Data.** Changan (CC BY-NC-SA, research only): driving frames at 10 s with current, SOC and 96 cell voltages;
  per-cell R from current steps (the X2 / X2-F identification). Beihang QAS (CC BY): use **only if** the profile shows
  frames with current and per-cell V at SOC < 20 %; otherwise the licence caveat stays on the verdict.
- **Profile first.** Number of discharge segments reaching SOC < 20 % (and < 10 %), their currents in C, cold vs warm;
  how often the min-V cell at low SOC is the highest-R cell (if almost always, min/max sees the binding cell for free
  and the gain can only come from *prediction* of sag before a load step).
- **Reference and margins (as X2-F).** Independent per-cell reference from odd-index current steps; each limiter
  carries its own κ calibrated on half the vehicles to ≤ 0.05 % unsafe calibration frames; scored on the other half;
  the shuffle control permutes per-cell R across cells at every time step and carries its own κ.
- **Primary metric.** S = median per-session gain in admissible discharge current (per-cell vs min/max) on frames with
  SOC < 20 %; S_sh for the shuffled limiter; D = S − S_sh paired. Secondary: the same as energy below the min/max
  cut-off point (a usable-depth number, DERIVED, not kWh).
- **Decision.** PER-CELL HELPS AT THE BOTTOM if S ≥ 1 %, CI > 0, D ≥ 1 pp, all limiters held-out safe at ≤ 0.2 %.
  NOT INTERPRETABLE if any limiter fails held-out safety (report the margins anyway, as X2-F did).
- **Kill.** S < 1 %, or S_sh ≥ S, or cold low-SOC segments too few to read (report n).
- **Expectation to state up front.** On NMC the OCV curve is steep at the bottom, so voltage may already identify the
  weakest cell (X2-F found the binding cell was the max-V cell 89 % of the time on NMC at the top). The gain, if any,
  is in predicting sag before a load step, which is a power-capability number, not an identification number.

### FR1 — pre-event window audit on public failure records

- **Question.** For HV power-electronics field failures with a public root cause, what pre-event window at what data
  rate would have been needed to find the cause from field telemetry alone?
- **Data (public domain).** NHTSA ODI: PE23011 and recalls 24V-204, 24V-868 (ICCU: OBC + LDC DC-DC); search the ODI
  recall and investigation database for OBC, DC-DC, inverter and charger campaigns 2018–2026 (`api.nhtsa.gov`);
  EU Safety Gate entries; published failure-analysis papers on OBC/DC-DC returns.
- **Pre-register before reading remedies.** The classification scheme: cause type (transient electrical / thermal
  cycling / manufacturing / software); evidence type that identified it (DTC freeze-frame / bench reproduction / fleet
  statistics / waveform capture); judged minimum pre-event window (≤ 1 s / 1–40 s / > 40 s) at a stated rate. Two
  raters blind to each other (two independent sessions, or Kyle plus one session). Fix the case list before rating.
- **Primary metric.** Fraction of cases judged to need > 1 s (beyond an MCU freeze-frame) and > 40 s (beyond the
  HyperRAM window at 3.2 MB/s). Inter-rater κ.
- **Gate.** κ ≥ 0.6 or the study is UNGATED. Report the base rate on a matched sample of non-power-electronics recalls.
- **Kill.** < 20 % of cases need > 40 s. Then B.3 is a convenience, not a necessity, and drops to tier-neutral.

### O1 — shrunken per-unit offset, and the Changan label fix

- **Two cheap closures from the audit.** (a) Pre-register κ = 3.55 and the robustness rule, then run the shrunken
  offset on Changan strict, EVBattery ds2/ds3 and the fixed-label Changan (audit §5 item 1). (b) Fix the segment-duration
  bias in `data/changan_labels.py` (6–24 h segments read +3.7 Ah high; audit §2) and re-derive the primary/strict label
  sets, recording the before/after noise SD.
- **Why it is here.** Tier-neutral (bytes of state), but it closes the one open "per-unit positive", and the label fix
  improves X8 and any future Changan replay. Hours of CPU.
- **Decision.** As Study 2's pre-declared rule (median, majority of units, sign test at Bonferroni 0.05/20, beats
  persistence).

### R1 — information retained under a fixed uplink budget (brief seed S7)

- **Question.** Given a fixed bytes-per-day budget, does learned or adaptive selection of what to keep from the per-cell
  stream preserve more detector performance than fixed decimation to min/max plus statistics?
- **Data.** Beihang QAS (CC BY; the G.2 feature A and its cohort caveats), BATSS ISC run (CC BY; the rest-drift
  detector), Changan (NC-SA; the review's per-cell-only drift detector).
- **Method.** Budgets at 1/10, 1/100, 1/1000 of raw. Reducers: fixed decimation to min/max/mean + fixed statistics;
  deadband change-logging (Weihai-style); a learned selector (small autoencoder or importance scorer) trained on a
  calibration half. Score each by the AUC of the pre-existing downstream detectors on the reduced stream vs the full
  stream, on held-out units.
- **Controls.** Shuffle control (selector trained on cell-identity-shuffled data); the Tier M comparator is the fixed
  reducer at the same budget.
- **Decision.** LEARNED REDUCTION HELPS if the learned reducer retains ≥ 0.05 more AUC than the fixed reducer at the
  same budget on two datasets with CI > 0. Otherwise fixed decimation suffices and the "cannot re-bin" claim has no
  measured cost at these budgets.

### L1 — requirement-arrival ledger (not a code task)

As ANGLES §C.1. Run in a research session with web access; the code session has nothing to compute.

---

## 3. What not to do

- Do not start X8 on Changan and put the number on a customer slide; the licence is non-commercial.
- Do not report B1's CPU cost as the cost of a DMA path; it is an upper bound from a CPU producer.
- Do not run DC1 against phase-level claims; the public data is node-level at 5–10 Hz.
- Do not run two experiments in one session; one brief, one pre-registration, one stop.
