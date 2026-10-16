# Experiment G.1 — dataset search: per-cell telemetry paired with independent fault ground truth

Search run 2026-10-14. Brief: [`Experiment G and H Brief.md`](../../Experiment%20G%20and%20H%20Brief.md), Experiment G.

## Decision: **NO-GO — NO GROUND TRUTH AVAILABLE**

No public dataset found pairs per-cell (series-string) voltage time series with **independent, located** fault labels
in a quantity that could test F's four-class diagnosis (SOC-like / offset-like / tap-fault-like / module-wide).

- The best public source is the Yuasa second-life system. It has **2 cells** with a fault confirmed by inspection.
  Both are the same fault type (a busbar contact, which F's scheme would most likely call a real low-capacity cell,
  not a sensor fault). Both were *chosen for inspection because the telemetry looked odd*.
- That is one class at n = 2 with a selection-biased label. It cannot confirm, or refute, a 4-class diagnosis.
  G.2 is therefore **not run**.
- The brief anticipated this outcome: *a clean "no public dataset pairs per-cell telemetry with fault ground truth" is
  a publishable-quality negative finding.*

**Method.** Web search plus source-page reading. No downloads, no sign-ups, no emails sent. The search was delegated
to a research sub-agent. The Yuasa busbar quote was re-checked against the paper text we already hold (arXiv
2609.04487, line 833).

## Candidates

The **Tag** column uses these values:

- **CONFIRMED-SUITABLE:** none found.
- **PARTIAL:** usable at very small n only.
- **LIKELY:** the paper suggests suitability, but the data contents are unverified.
- **NOT AVAILABLE:** the data exists but is not public.
- **NOT SUITABLE:** the data is public but fails a requirement.
- **NOT FOUND:** no public data statement located.

| Dataset | Where | Per-cell telemetry | Units | Fault label | Independent of telemetry? | Licence / access | Tag |
|---|---|---|---|---|---|---|---|
| **Yuasa / STABL second-life BESS** (Cornejo et al.) | zenodo 10.5281/zenodo.22281620; arXiv 2609.04487 | V per logical cell, 10 s; T per module | 27 modules × 12 logical cells (2P LEV50N) | 2 faulty cells (P1M6C1, P3M5C12). *"Inspection after the study traced both faults to the busbar contacts, which were subsequently fixed."* | Partly. The inspection is physical, but the cells were selected from the telemetry. The paper's reference test covers neither cell. | MIT, public | **PARTIAL (n = 2, one fault type)** |
| ZJU-o BESS | zenodo.org/records/18158360; arXiv 2512.16453 | V, T, SOC per cell, ~1 min | 28 modules × 16 LFP | Expert annotation + 3 artificially inserted anomalies; "reports" from a rule-based pipeline run on the same telemetry. No maintenance logs mentioned. | No | CC BY 4.0, files **restricted** ("public release soon") | NOT SUITABLE as ground truth (useful unlabelled) |
| U-Michigan / LG ES grid BESS (Wong et al.) | arXiv 2606.26347 | V per parallel group, 1 Hz, 1 mV; 2 T per module | 25 modules × 14 groups | 25 faulty groups, confirmed by post-mortem | **Yes** | **Not public** (confidentiality) | NOT AVAILABLE — best label quality found; ask the authors |
| Yu, Li, Chen, Pecht, *Frontiers Energy Res.* 2022 | 10.3389/fenrg.2022.891637 | Cell / interleaved V at 10 Hz, 3–5 cells | Bench | Injected connection (200/400 mΩ), frozen/noisy sensor, ISC, ESC | **Yes** (induced) | On request | NOT AVAILABLE — closest to F's sensor and tap classes |
| Kang et al. interleaved multi-fault (2019; attribution not verified) | Mendeley 10.17632/6ng4crgrrz.1 | Interleaved voltage topology, not standard per-cell taps | Small lab pack | Induced ISC / connection / sensor faults | Yes | CC BY-NC 3.0, public; appears to be figure data only | LIKELY but marginal (wrong topology; contents unverified) |
| Feng / Tsinghua ISC; *Patterns* 2023 ISC forecasting | 10.1016/j.apenergy.2019.114143; *Patterns* | Single cells | 70 cells (*Patterns*) | Induced ISC | Yes | No public data statement found | NOT FOUND (single cells, not strings) |
| Kwak et al. thermal runaway | 10.17605/OSF.IO/C2HNQ | **No per-cell voltage** (T, pressure, force) | 6 cell + 2 module tests | Heater-triggered runaway | Yes | CC0, public | NOT SUITABLE |
| NREL/INL high-mileage fleet packs | 10.15483/1876633 | Pack capacity + HPPC; no per-cell series stated | 21 vehicle models | No teardown or failure findings on record | — | Public (OSTI) | NOT SUITABLE |
| Schaeffer et al., 28 LFP home systems | 10.5281/zenodo.13715694 | Per-cell V (8S), 4 shared T | 28 systems, up to 5 years | All returned for "unsatisfactory behaviour"; no reasons | — | CC BY-NC 4.0, public | NOT SUITABLE (no labels) |
| HIT swap-station multi-fault (Xie et al. 2026) | 10.5281/zenodo.18328701 | Raw per-cell V for a subset | > 128 k devices (features) | Clustering + rules; recall lab tests mentioned but not included | No | CC BY 4.0, public | NOT SUITABLE (CSVs not opened) |
| Zhang et al., 347 EVs (*Nat. Commun.* 2023) | figshare 10.6084/m9.figshare.23659323 | min / max / mean cell V only — no per-cell vector | 347 EVs (55 abnormal) | Driver reports confirmed by engineers, vehicle-level | Semi; **no cell location** | Public (licence unverified) | NOT SUITABLE (vehicle-level labels) |
| Second-life grading sets (IEEE DataPort 10.21227/wr14-9q53; Zenodo 20317410; TU Berlin depositonce-11469) | as listed | Small packs / single cells | small | SOH grading only | — | Public | NOT SUITABLE |
| Changan 300-EV (in hand); CH-BatteryGen; 99-EV topology study; synthetic sets | — | — | — | None, generated, or not public | — | — | NOT SUITABLE |

**Verification level.**

- **Read on source pages:** the Zenodo pages (ZJU, Schaeffer, HIT, the Cornejo software record); the Kwak OSF
  licence and listing; OSTI 1876633; the methods and data statements of Cornejo, ZJU, Wong and Frontiers 2022.
- **Inferred, not verified:** the Kang 2019 attribution and contents, the CH-BatteryGen download, and the
  Zhang/figshare licence.

## What the n = 2 Yuasa case could and could not do

The two cells show about half the capacity and roughly twice the resistance of the median. That pattern fits the
loss of one of the two parallel physical cells behind a failed busbar contact.

- In F's scheme, that would most likely land in **SOC-like / real-cell**. That is the right answer at the electrical
  level, but it is the wrong *root cause*: the fault is a connection, not a weak cell.
- So the case would test one class, on two cells chosen by the telemetry itself. **The brief's G.2 rule says to
  report a case like this as a case study with no p-value.** Run under that rule, it would show only that F's
  classifier does not mislabel two obvious faults. It cannot show that per-cell data diagnoses better than min/max.
- It was therefore **not run**. Running it would invite a "diagnosis confirmed" reading the data cannot support.

## What data would settle G

Any one of these would do:

1. **A controlled bench injection** on our own series string. This is the cheapest route and has ground truth by
   construction. Inject, one at a time:
   - a series resistor in one sense lead (offset- and current-dependent);
   - a fixed offset on one tap (sensor offset);
   - a resistance in a *shared* tap (one cell low, its neighbour high — the tap signature);
   - one cell held at a different SOC (a real cell);
   - a module-wide bias.

   Then run F's classifier and a min/max-only control blind. The Frontiers 2022 and Kang 2019 set-ups show how.
2. **The U-Michigan / LG ES post-mortem data** (25 confirmed faulty groups) under a data agreement. Ask Wong /
   Stefanopoulou.
3. **The Yu / Pecht (Frontiers 2022) injected-fault data**, on request.
4. **ZJU-o BESS plus its operator's maintenance log.** A draft request is below; it has **not been sent** and needs
   Kyle's approval.

## Draft email to the ZJU authors

A draft access request was written but **not sent** (Kyle decided not to pursue it). It is omitted from the public mirror.


## Verdict

**NO GROUND TRUTH AVAILABLE.** On public data, F's diagnosis finding stays *supported but unconfirmed*. Confirming it
needs purpose-collected bench data (fault injection) or proprietary post-mortem / service data.

Licences: every source cited here is listed with its own licence. F's underlying finding rests on Changan data
(CC BY-NC-SA 4.0, non-commercial).
