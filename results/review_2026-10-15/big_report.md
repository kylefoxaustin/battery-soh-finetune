# Big-picture review — per-unit learning and per-cell data on an i.MX 95-class processor

Reviewer brief: frank research-director review of the 9-experiment programme in `batt_finetune` (Studies 1–2,
E, F, G.1/G.1b, G.2, H, H2) as narrated in `results/RESEARCH_DOSSIER.md` (commit 731c2b7, 2026-10-15).
Read-only; nothing in the repo was modified. Scratch work (BATSS/McMaster probes) is in
`scratchpad/review/big/`.

Tags used below for any number *I* introduce: **SOURCED** (with URL) or **DERIVED** (computed here, read-only,
CPU, `python -I`). Numbers quoted from the repo's own write-ups carry their original tag.

---

## 0. Executive summary (the frank version)

1. **The method is the strongest asset in the repo and is better than most published battery-ML work**:
   committed pre-registrations, same-run gates, persistence controls, Bonferroni, numbered deviations,
   licence tracking. Keep every bit of it.
2. **The framing drifted away from the question the programme set out to answer [wording edited for the public mirror].** "Per-cell vs min/max" is a clean
   scientific control, but it measures *information content*, not *what an application processor adds*. Every
   per-cell computation tested (OLS slopes, robust z, a LUT limiter) is a microcontroller workload; H-b/H2-b
   prove it (14.7 ns/cell). The programme has therefore shown — correctly, and usefully — that the tested uses
   **do not need an AP**. It has not yet tested the uses that might (learned per-cell models, long per-cell
   history/storage, data reduction, passport/warranty records, LFP per-cell SOC).
3. **The one-line story in §9 over-generalises.** Four of the seven rows in the synthesis table are
   "unresolvable" or "untestable" outcomes dressed as nulls in the prose; the H/H2 null is partly built into
   the limit map by construction (the pre-registration says so); F's 98 % overlap is close to tautological; and
   the G.2 positive is one cohort-confounded AUC 0.59 whose CI lower bound is 0.51. Reword (proposed text in §2).
4. **The premise that telemetry carries only min/max is wrong for the main dataset.** GB/T 32960.3 frames carry
   the full per-cell voltage list and per-probe temperature list (`CellsVoltage`, `ProbesTemp`) — that is where
   Changan's `batteryvoltage` column comes from (SOURCED, §1.1). The real-world baseline for "does the AP need
   per-cell data" is therefore not "the BMS only sends min/max" but "the cloud already receives per-cell at 10 s;
   what is worth computing on the pack instead?"
5. **Two downloaded datasets answer two open questions and were left on the shelf.** BATSS ISC: the rest drift
   separates cell 8 (−1.0 mV/h) from the min cell (cell 2) — a ground-truth-by-construction instance of the
   exact "drifting while not the weakest" mechanism G.2 hinted at (DERIVED, §4.1). McMaster: 72 cells with *per-cell*
   temperature and a 28 °C intra-pack gradient in the module-blocked run — the temperature-gradient regime H and
   H2 declared untested/unanswerable (DERIVED, §4.2).
6. **Best next moves** (§4): a zero-cost blind prediction on BATSS; H-a replayed on McMaster/BATSS gradient
   runs; per-cell SOC/capacity on the Weihai LFP racks (commercially clean licence); a learned per-cell model vs
   G.2's hand feature (first real NPU/AP-class test); a $1–3k bench fault-injection string (the only route to
   confirming F); and a data-reduction experiment, which is the one AP-specific lever never quantified.

---

## 1. Framing critique

### 1.1 Is "per-cell vs min/max" the right comparison for an *application-processor* value case?

It is the right **control**, and it was executed well. It is the wrong **thesis**, for four reasons.

**(a) The information is already on the wire.** The dossier (§0) describes min/max/mean as "the scalars a
typical BMS or GB/T-32960 telemetry frame carries". A GB/T 32960 real-time frame contains the information type
可充电储能装置电压数据 with a `CellsVoltage` array (all cells, chunked across frames via `FrameCellsIndex` /
`FrameCellsCount`) and 可充电储能装置温度数据 with a `ProbesTemp` array (SOURCED: EMQX GB/T 32960 protocol
documentation, https://docs.emqx.com/zh/enterprise/v4.2/modules/gbt32960_protocol.html). Changan's
`batteryvoltage` (96 values) and `probetemperatures` (32 values) columns *are* those fields. So on the Chinese
national platform — the source of Changan, Beihang and BatICM — the cloud already has per-cell data at 10–30 s.
The honest commercial question is then: **which computations on the per-cell stream are worth doing on the pack
rather than in the cloud, and which of those are too big for the BMS MCU?** None of E–H2 asked that.

**(b) Every tested per-cell computation is MCU-class.** The G.2 feature A is 110 OLS slopes and a robust z; the
F classifier is a handful of medians and two curve fits per event; the H limiter is two LUTs and an argmin,
measured at 52 µs for 3,564 cells on an A55 (MEASURED, H2-b). The i.MX 95 itself carries a Cortex-M7 and a
Cortex-M33 alongside the six A55s (SOURCED: https://www.ezurio.com/support/faqs/what-is-the-npu-performance-on-the-nitrogen95-and-how-does-it-support-edge-ai-inference-workloads ;
https://docs.peridio.com/hardware/under-evaluation/frdm-imx-95). A 100 Hz limiter with 724 µs Linux
preemption spikes (self-identified weakness 5) belongs on the M7 or on the BMS MCU, not on an A55 under Linux.
H-b's headline — "a small fraction of one A55 core" — is true and *argues against* the AP: anything that cheap
runs anywhere. The AP earns its place only with workloads an MCU cannot host: models >1 MB, long per-cell
history (GB), a filesystem, OTA, TLS/passport signing, connectivity, and software flexibility. Only Study 1's
H1–H3 feasibility numbers touch that, and they concern a 220 KB model that also fits an MCU with external flash.

**(c) The per-cell hypotheses were tested with hand-built scalar features, never with a learned per-cell
model.** The programme's one learned model (2×LSTM-128) consumes 7 pack-level channels. Nothing ever ingested
the 96- or 110-vector into a model, so "does an AP/NPU-class model extract more from per-cell data than a
10-line feature?" — the only version of the question where the AP's compute matters — is untested. The eIQ
Neutron NPU (2 TOPS, SOURCED: ezurio page above; an 8 "eTOPS" marketing figure also circulates and should not
be used) was never exercised.

**(d) The "fleet model on-device" result is being under-sold.** Studies 1–2 show the *frozen fleet model* beats
mileage-linear and persistence on Changan at every horizon (results_large.md §C: persistence 4.94–6.95 Ah vs
frozen 4.10–4.54 Ah). That *is* a value case for on-device inference of a fleet-learned model (the AP as
inference host, with fleet learning in the cloud) — it just is not a case for on-device *training*. The dossier
frames both studies purely as negatives.

### 1.2 Value propositions never tested, ranked by plausibility × value

| Rank | Proposition | Why it matters commercially / technically | Plausibility of a measurable effect on data in hand | Programme status |
|---|---|---|---|---|
| 1 | **Per-cell SOC / capacity tracking on LFP** (flat plateau; BESS and LFP EVs) | LFP BESS operators cannot read SOC from voltage; per-cell ΔSOC/capacity is what decides balancing, usable energy and replacement. Weihai = 3,564 LFP cells, 8 months, 217 full-cluster charges. | High: knee-crossing order at 3.40–3.45 V is a per-cell signal; min/max gives one number per rack | Untested (H2 used Weihai only as a limiter replay) |
| 2 | **ISC / self-discharge early warning** (the safety case) | Recalls, fires, BESS insurance. The literature's standard detector is rest-period drift relative to siblings — exactly G.2's A. | High: BATSS ISC (resistor by construction) and BatICM (3 located ISC/self-discharge cars) are already downloaded | Touched only via G.2's binary label |
| 3 | **Sensor / harness fault detection as a product** (F's "diagnosis") | Warranty cost: a false "weak cell" is a module swap; a tap fault is a connector. Only per-cell + neighbour data can tell them apart. | Medium: no public ground truth (G.1), but a bench string gives it by construction for ~$1–3k | Blocked on data; bench route recommended in G.1 but not costed |
| 4 | **Edge data reduction / selective upload** (the AP's natural job) | 300 vehicles × 96 cells × 10 s ≈ 1.66 MB/vehicle/day raw at 2 B/cell (DERIVED: 96 × 2 B × 8,640 frames); fleets of 10⁵ vehicles pay for that. Weihai's own change-logged format shows operators already do deadband compression. | High: measurable on data in hand with zero loss on the F/G.2 features as the criterion | Untested; E5 sized 7-channel buffers only |
| 5 | **Warranty / passport analytics** (per-cell history retention) | EU Regulation 2023/1542 Art. 14 obliges makers to give read-only access to state-of-health / expected-lifetime data held in the BMS. One manufacturer's Art. 10/14 disclosure (SOURCED: https://www.livewire.com/en-gb/documents/battery-regulation) exposes SoH as a single % over UDS (service $22, DID 0x020E) for models placed on the market after 18 Aug 2024, with Art. 10 figures of capacity fade < 15 %, power fade < 24 %, resistance rise < 32 % over 5 years. Primary text CELEX 32023R1542 (eur-lex fetch failed in this session; Annex VII parameter list from memory, not re-verified). A per-cell drift history is how those pack-level parameters would be computed defensibly on the pack. | Medium: storage sizing is a pure DERIVED/MEASURED exercise | Untested |
| 6 | **Second-life grading from in-service history** | Yuasa shows heterogeneity costs ~1 % in healthy modules and 24–44 % at a failed cell; a per-cell drift log at end-of-first-life replaces part of the teardown grading. | Medium: Yuasa n=2 faults; Beihang teardown labels are vehicle-level | Only descriptive in E |
| 7 | **Learned anomaly detection on the NPU** (autoencoder over the cell vector) | The only AP/NPU-specific compute story; but the workload is tiny (110 inputs), so the NPU is irrelevant for sizing. Value is software flexibility, not TOPS. | Medium on Beihang (393 labelled vehicles) | Untested |
| 8 | **Balancing optimisation** | Active balancing using per-cell capacity estimates; E/Yuasa bound the gain at ~1 % in healthy modules | Low–medium | E bounded the ceiling |
| 9 | **Thermal-runaway early warning** | Highest consequence, but voltage-only per-cell data warns late; needs gas/pressure. | Low on in-hand data | Not applicable to the data held |
| 10 | **Fleet learning + on-device inference only** | Already demonstrated implicitly (frozen fleet model beats all per-unit variants). Should be stated as a positive. | Done | Mis-framed as a negative |

### 1.3 What was missed structurally

- **No "where should it run" axis.** Every board number was on an A55 under Linux. Adding one column — "fits
  BMS MCU / needs M7 / needs A55" — to each experiment would have turned the cost measurements into the
  placement argument the original brief asked for [wording edited for the public mirror].
- **No learned per-cell model** (see 1.1c).
- **No per-cell ageing in the limiter maps** (self-identified weakness 2). With identical maps and a
  voltage-only taper, per-cell ≡ min/max algebraically (H pre-registration §0.2). The experiment could only
  ever find a temperature-coupling effect, then ran on two datasets with 3–4 °C probe spreads. That is a
  designed-in null, not a discovered one.
- **Storage/history was never measured for per-cell data** — the one resource that *does* scale with cell
  count × time on an AP.

---

## 2. Logic of the synthesis (dossier §9)

### 2.1 Does the one-line story follow from the evidence?

Current text: *"On every public dataset we could find, an application processor gains little from per-unit
learning or per-cell limiting. The one place per-cell data shows an edge over min/max scalars is flagging packs
headed for teardown-confirmed failure, where it sees a cell drifting relative to its siblings before it becomes
the weakest. The compute cost of per-cell processing is negligible on an A55."*

Row by row against the write-ups:

| Claim | What the evidence supports | Problem |
|---|---|---|
| "an application processor gains little" | The *tested computations* do not need an AP; the *information* mostly does not beat min/max | Subject slip: experiments measured information and features, never AP-vs-alternative placement |
| "from per-unit learning" (Studies 1–2) | Study 1 (supplied labels, n=20) is a clean negative. Study 2 is "no effect detectable below ≈ 3 Ah" with label noise 45–75 % of lifetime fade (results_large.md Scope paragraph) | Study 2 should be worded as a resolution limit, which its own text does; the dossier flattens it to "Strong" |
| Tighter bound (E) | INCONCLUSIVE; oracle ceiling ~1 %, MDE 0.8–0.9 % | Fine as written ("informative bound") |
| Detecting anomalies (F): "min/max sees 98 %" | Event-days are defined by one cell < −60 mV; on such a day that cell is (almost always) the pack minimum, so `vmin − V/96` crosses the same threshold by construction | Near-tautological; it shows the *definition* is min-detectable, not that min/max suffices for detection in general. The non-tautological question (drift while not minimal) was feature A — underpowered |
| Early warning (F) | 3 positives | Correct ("untestable") |
| G.2 "Per-cell > min/max … survives adjustment" | AUC 0.59 (0.51–0.67) early; faulty cohort is contiguous IDs 335–392 with temperature AUC 0.74; adjustment uses 5 measured controls | A 5-covariate logistic adjustment cannot remove unmeasured batch effects (firmware, sampling path, season). Lower CI bound 0.51 ≈ p 0.03 for one pre-registered test. It is "one modest, confounded, unreplicated positive", not "the one place per-cell shows an edge" |
| H/H2 "No … Strong within the assumed maps" | Median saving 0.008 % / 0.00 %; 79 % of Changan sessions in the flat band; Weihai HVAC 20–31 °C; identical maps per cell | "Strong" is wrong in kind: under the chosen maps the null is the algebraic default, and per-cell ageing (the real lever) was excluded by design. "Not tested in any regime where theory predicts a difference" is the accurate verdict |
| "compute cost negligible on an A55" | MEASURED, true | Cuts against the AP: negligible on an A55 ⇒ trivially hosted on an MCU |

**Over-generalisation from structurally unable datasets** — yes, in three places: (i) Study 2's label noise
makes it unable to see per-unit gains < ~3 Ah; (ii) H's climate and H2's HVAC make them unable to see
temperature coupling; (iii) F's n=3 makes early warning untestable. The synthesis *table* mostly says this; the
*prose* and the title phrase "on every public dataset we could find" do not. "Every public dataset we could
find" is also literally untrue: BATSS, McMaster and BatICM were found and downloaded but not used.

### 2.2 Proposed rewording of the one-line story

> "On the public field data we could use — one warm-climate NMC EV fleet with capacity labels we derived
> ourselves, one HVAC-controlled LFP container, and one teardown-labelled fleet without failure dates — per-unit
> fine-tuning did not beat a frozen fleet model (clean negative at n = 20 with supplied labels; unresolvable
> below ≈ 3 Ah at n = 94), and hand-built per-cell features did not beat min/max scalars for capacity bounds,
> anomaly detection or charge limiting under uniform per-cell limit maps — null where the data could resolve an
> effect, unresolvable where it could not. One teardown-labelled fleet gives a modest, cohort-confounded signal
> (AUC 0.59 vs 0.52) that a cell drifting relative to its siblings predicts failure before it becomes the
> weakest cell. Every per-cell computation we tested runs in microseconds on one A55 core; none of them needs
> an application processor."

Smaller wording fixes:

- §0: replace "the min/max/mean scalars a typical BMS or GB/T-32960 telemetry frame carries" with "the
  min/max/mean scalars most BMS CAN summaries carry (GB/T 32960.3 frames also carry the full cell list, which
  is where Changan's per-cell columns come from)".
- §4/§9: say explicitly that F's 98 % overlap is expected from the event definition.
- §7/§9: replace "Strong within the assumed maps" with "Null by construction for voltage-limited frames; the
  temperature-coupling regime was not present in either dataset; per-cell ageing not modelled".
- §6/§9: add "unreplicated; requires an independent cohort" to G.2.
- §9 table: add a column "Could this dataset have shown the effect if it existed?" (Y/N/partly). It will read
  N, N, partly, N, N, Y, N — which is the real finding of the programme and a good figure.
- §10: add weakness 9 — "No experiment tested a learned per-cell model or any AP-specific resource (storage,
  model size, connectivity); the placement question (MCU vs M7 vs A55) was not asked."

---

## 3. Missed datasets and sources

*(G.1/G.1b lists checked first; items below are additions or status updates. Two parallel read-only web
searches were run; their results are integrated here. Items marked INFERRED were not verified on the source page.)*

### 3.1 Status checks requested in the brief

| Item | Status (2026-10-15) | Source |
|---|---|---|
| **arXiv 2608.10825** (Li, Che, Onori, W. Li, X. Hu; 99 EVs, 14S ternary, 14 V + 4 T + 1 I, 16.4 M records; dynamic per-cell labels EI/ASD/ACD/ISC from accident reports, recall logs and disassembly) | **Not released.** v1 only (11 Aug 2026); data statement: "will be made publicly available upon final publication". No Zenodo/GitHub/figshare record. Region/climate withheld under NDA. | https://arxiv.org/abs/2608.10825 (PDF, Suppl. Note 1) |
| **ZJU-o BESS** (zenodo 18158360; 28 modules × 16S LFP, 1 min, Dec 2023–May 2024) | **No change — restricted.** Zenodo API `access_right: restricted`, file list empty (login-gated sample), nominal CC BY 4.0, record last modified 2026-04-22 (rev. 24), text still "will be released publicly soon". | https://zenodo.org/records/18158360 |
| Weihai 20094787, U-Mich/LG ES 2606.26347, Schaeffer 13715694, Zhang 23659323 | No change | re-checked |

### 3.2 Cold-climate / field / service-record sources — new candidates checked (none fully fits)

| Dataset | URL | Per-cell? | Units & span | Cold / fault / label content | Licence | Verified |
|---|---|---|---|---|---|---|
| Field EV Fleet BMS Telemetry (Kookmin U / Hansnetwork, Korea) | https://ieee-dataport.org/documents/field-ev-fleet-bms-telemetry-dataset (10.21227/0v0g-gz47) | **No** — pack V/I/T/SOC/SOH at 1 s; ~800 k stop–launch resistance events | 21 E-GMP taxis (77.4 kWh NMC), Aug 2024–Jan 2026 | Battery T **−5.7 to 40.3 °C** (real winter); no faults | IEEE DataPort subscription | page read |
| CH-BatteryGen "Battery Fault" (ICLR 2026) | https://openreview.net/forum?id=jSM71b1JsV | Not stated (INFERRED cell-level) | "1000 EVs", NCM + LFP; **real + mechanism-constrained generative** data, share unknown | 4 fault classes × 3 severities; label origin not stated | claimed "open-sourced", **no repo URL found** | pages read |
| Shenzhen Autosun charging dataset (PolyU) | https://data.mendeley.com/datasets/c7gg94tmvz/3 | **No** — charger-side V/I/P, gun temps, 1 min | 10,154 EVs, 21,175 sessions, 2020–2023 | Binary faulty flag "reported by engineering personnel" (TR, imbalance, SC) — independent-ish, vehicle-level; Shenzhen (warm) | CC BY 4.0 | page read |
| Chengdu e-bus "Real EV dataset" (Z. Fei) | https://data.mendeley.com/datasets/j9ky68gnd3 | Claims > 180S packs at 10 s, but files are 4 CSVs of 1.6–7.7 kB | 5 buses | none | CC BY 4.0 | file list read — effectively empty |
| TUM 101 e-bus operating data | https://mediatum.ub.tum.de/1717359 | INFERRED unknown (server errors) | 101 buses | unknown | unknown | not verified |
| TUM/Steinstraeter BMW i3 heating data | https://ieee-dataport.org/open-access/battery-and-heating-data-real-driving-cycles | **No** — pack level, 0.1 s | 1 car, 72 Munich trips | heating/ambient logged | open (IEEE login) | page read |
| RWTH GO ELK! fleet | https://publications.rwth-aachen.de/record/979878 | INFERRED unknown (page empty) | 9 BEVs, Aachen 2014–16 | 3.1–13 % fade over 3 y | open zip | snippet only |
| NDANEV 10-EV set (VBFDD-Agent) | https://github.com/sjtu-chan-joey/VBFDD-Agent-Vehicle-Battery-Fault-Detection-and-Diagnosis-Agent | **No** — min/max only; raw not released | 10 EVs, ~6 mo | 19 alarm codes (0.18 % abnormal) | n/a | read |
| RVD 300-EV (IEEE DataPort 10.21227/jyrv-2179) | https://ieee-dataport.org/documents/real-world-battery-dataset-comprising-operational-data-battery-packs-300-mass-produced | **No** — pack per cycle | 300 EVs, 104,621 cycles | SOH only | subscription | page read |
| UPC pack test bench (CORA 10.34810/data2395) | https://batterymaster.upc.edu/datasets | Yes, 36 cells (3P) | lab, WLTP | none | CC BY 4.0 | search only |
| ULPGC OPzS bank (zenodo 17252822) | https://doi.org/10.5281/zenodo.17252822 | Yes, 6 cells, 1 min | lab, lead-acid | none | CC BY 4.0 | search only |

Dead ends (searched; nothing public with per-cell): INL cold-climate EV programmes (reports only); ACEP Alaska;
Yukon/NWT portals; Norwegian/Finnish/Swedish fleet programmes; Cornell/TCAT cold e-bus (paper only); northern-China
实车 低温 单体电压 on ScienceDB/figshare/Zenodo; NDANEV open samples (annual reports); Faraday / OEDI / Battery
Passport pilots (metadata only); EVERLASTING; Kaggle/HF (synthetic or lab cells); e-moto swap, forklift/AGV,
telecom, Arctic/Antarctic, CubeSat (< 4S) — none.

**Reading.** As of today there is **no public cold-climate per-cell charging dataset** and the only
teardown-labelled per-cell EV set (2608.10825) is embargoed. The programme's reliance on Weihai and Beihang was
justified. Two consequences: (i) H's cold question can only be approached with *lab gradient* data — which is
exactly what McMaster and the BATSS Ta10/Tl10 files provide (§3.x below); (ii) set a watch on 2608.10825 and on
the ZJU-o record; and consider asking the CH-BatteryGen authors for the repo via the OpenReview thread (no
contact was made in this review).

### 3.3 Fault-injection / ISC / module datasets — new candidates checked

| Dataset | URL | Per-cell? | Fault type and how located | Units/runs | Licence | Verified |
|---|---|---|---|---|---|---|
| **TUM Schöberl et al. thermal-runaway propagation set — NMC-811 (Mini Cooper SE) and LFP (Tesla Model 3 SR+) modules** | https://mediatum.ub.tum.de/1717758 (DOI 10.14459/2023mp1717758) | Yes: cell voltages + module/vent/surface temperatures via CAN log (.mat/.txt); rate not stated (INFERRED 1–10 Hz) | Heater-triggered TR propagation; trigger-cell location in the linked *eTransportation* 19:100305 (2024) | 2 modules, 1 test each | Not confirmed (page timed out) | metadata via snippets/FIS portal; details INFERRED |
| Schaeffer / Braatz / Findeisen 28 × 8S LFP home systems | https://zenodo.org/records/13715694 (paper 10.1016/j.xcrp.2024.102258) | Yes: 8 cell V, 4 shared T, current; 133 M rows, 1.7 GB | Warranty returns ("unsatisfactory behaviour"); no teardown-located cell | 28 systems, 224 cells, 1–5 yr | CC BY-NC 4.0 | page read (in G.1 as NOT SUITABLE; still usable for an 8S per-cell-vs-min/max replay with weak labels) |
| Hangzhou Dianzi / Tsinghua pack multi-fault (JEIT 2026, 10.11999/JEIT251156) | https://www.jeit.ac.cn/en/article/doi/10.11999/JEIT251156 | pack under FUDS/UDDS/US06; cell count not in abstract | ISC, sensor noise, sensor drift, SOC inconsistency ("constructed dataset") | n/a | No link found (INFERRED not public) | abstract read |
| Dong et al. (Brunel/HDU) ISC pack, 3 conditions × 3 severities (IEEE TTE 11(1):3655, 2025) | https://bura.brunel.ac.uk/handle/2438/29858 | not stated | ISC injection | n/a | no data release found | record read |
| Yang/Xu/Peng, *Electronics* 2022 11(9):1494 — physically injected ESC/ISC/thermal/loose connection in a series pack | https://www.mdpi.com/2079-9292/11/9/1494 | series pack (page 403) | ESC, ISC, thermal damage, loose connection | n/a | INFERRED not public (reviewer asked for release) | abstract + review report |
| UPV semi-solid-state 3-cell mini-module overcharge TR | https://zenodo.org/records/22273467 | 3 cells (< 4S) | overcharge TR | 3 tests | CC BY 4.0 | page read — below threshold |
| UTFPR/PUCPR 4-cell second-life pack | https://ieee-dataport.org/documents/dataset-constant-load-discharge-characterization-pack-composed-four-second-life-batteries | Yes: v1–v4, t1–t4, I at 10 s | per-cell SOH labels 63/87/55/92 % (category c, tiny) | 31 discharges | IEEE DataPort subscription | page read |
| Fan, "model-enabled asymmetric autoencoder" supplement (IEEE DataPort 10.21227/wyab-x647) | https://ieee-dataport.org/documents/supplementary-materials-model-enabled-asymmetric-autoencoder-fault-detection-li-ion | .fig plots only | field packs, early faults | 8 packs | subscription | not a dataset |
| Daffodil Univ "Industrial LiFePO4 BMS dataset" 8S | https://data.mendeley.com/datasets/k675pxrd83/1 | 8 cell V per cycle record | none; the *Data in Brief* article says cell voltages are **simulated** | 3,000 cycles | CC BY 4.0 | SYNTHETIC — avoid |
| Mendeley "EV Li-ion Battery Fault Diagnosis Dataset" t42ynjk936; Kaggle "Battery Failure Surfaces" | https://data.mendeley.com/datasets/t42ynjk936/1 ; https://www.kaggle.com/datasets/niladriroy0/battery-failure-surfaces | model output | over-discharge / short-circuit labels | — | — | SYNTHETIC, not validated pack models |
| *Scientific Data* 2026 "Multi-modal thermal runaway dataset of fresh and aged cells and modules" (s41597-026-07857-1) | not retrievable in this sweep | unknown | TR, modules | unknown | unknown | INFERRED — worth a direct check |

Leads verified as **not public**: Xia/Sun/Chen (BIT) sensor-fault packs; Bing Xia (SDSU) 8-cell sensor/connection
experiments; Stefanopoulou/UMich Deep Blue (cell-level only); RWTH ISEA (cell-level and pack-level home storage,
no module fault set); Aalborg/Stroe; Warwick WMG (parallel modules, DiB 2024, CC BY — wrong topology); Sandia
module propagation (slides only); NREL ISCD (papers only); INL, PNNL, UL RI, CATARC/CAERI, Battery Archive
(cell-level), ScienceDB, AI-Hub (KR); EVERLASTING 4TU collection (cell-level); 4TU "forced temperature gradient"
set (figure data only); UPC 36-cell pack cycling (per-cell V/I/T, no faults); Düzgün et al. three-module TR
(row voltages only).

**Gap statement for the dossier (update to G.1b).** As of 2026-10-15 there is still no public bench dataset with
injected ISC / sensor / connection faults on a ≥ 4S string with per-cell voltage released, other than BATSS (ISC)
and McMaster (thermal/sensor). Reusable ground truth remains field + post-mortem (Beihang now; the 99-EV 14S set
when published) and TR-trigger modules (TUM mediaTUM 1717758 — new, licence and rate to confirm). The bench
string in §4.5 therefore remains the only way to get sensor/tap-fault ground truth, and would itself be a
publishable dataset.

### 3.x In-hand but unused data that already fills two gaps (DERIVED, read-only probes)

**BATSS ISC file** (`data/raw/batss/BATSS_20-21-22_ISC_results.xlsx`, CC BY 4.0, Zenodo 20490514 — record
text on the ISC test is only "one of the balancing resistance connected all the time", SOURCED:
https://zenodo.org/records/20490514). Parsed with stdlib (`scratchpad/review/big/batss_isc_probe.py`):

- 62,817 rows at 1 Hz, 17.5 h, one continuous run (no time resets): REST → three CC discharge / CC-CV charge
  cycles (−67 A, −33 A, −67 A discharges; 32, 56, 84 A charges; 52–59 Ah each) → one 10.0 h rest. 10 cell
  voltages, 55 thermocouples (24.7–59.5 °C), coolant in/out T, pressures, flow.
- **Rest drift, hours 2–10 of the final rest (relative to pack mean):** cell 8 **−1.00 mV/h**, cell 2
  **−0.73 mV/h**, all other cells +0.16 to +0.27 mV/h. Cell 8's deviation moved monotonically from −12 → −21 mV
  across the rest; cell 2 from −19 → −25 mV.
- **Across the three cycles, cell 8 swings from +33 mV (end of discharge 1) to −29 mV to −54 mV (end of
  discharges 2–3)** — a cell losing SOC relative to its siblings cycle after cycle. Cell 2 is low from the first
  minutes (−1.5 mV at t=0, −19 mV after discharge 1, −107/−121 mV at the end of discharges 2–3) and recovers to
  −16…−27 mV after each CV charge: the signature of a lower-capacity / higher-resistance cell, not of a drain.
- **The min-voltage cell at the end of every step is cell 2** (once cell 7). A min/max monitor points at cell 2.
  A per-cell *drift-rate* feature (G.2's A) points at cell 8.
- Implied drain for cell 8, if the 2P logical cell is of order 40–50 Ah and dOCV/dSOC ≈ 8–10 mV per % SOC near
  4.1 V (both ASSUMED): 1 mV/h ≈ 0.1–0.12 % SOC/h ≈ 40–60 mA, i.e. a resistor of order 70–100 Ω at 4.1 V —
  a plausible passive-balancing resistor (DERIVED; order-of-magnitude only).

So the dossier's "which cell had the resistor is ambiguous (cells 2 and 8 both self-discharge 0.8–1.1 mV/h)" is
resolvable: the two cells have different *kinds* of deviation. This makes BATSS a one-shot, ground-truth-by-
construction test of the exact mechanism G.2 proposes (§4, proposal 1). Caveat: I have now seen the data, so
the pre-registration must disclose that the prediction "cell 8" was formed after inspection; the blind element
is the author confirmation.

The other BATSS files are also relevant to H: `BATSS_8_SteadyState_Ta10_Tl25`, `BATSS_28_Capacitance_Ta10_Tl25`
(10 °C ambient, 25 °C coolant) and `BATSS_6/10_*_Tl10` (10 °C coolant) impose controlled intra-module
temperature gradients with 55 thermocouples on 10 cells (file names SOURCED from the Zenodo listing; contents
not opened here).

**McMaster pack** (`data/raw/mcmaster/x/Drive Cycle Data/*.mat`, CC BY 4.0, Borealis
https://doi.org/10.5683/SP3/UYPYDJ per the README). Read with a minimal MAT-5 reader
(`scratchpad/review/big/mat5_probe.py`), 13 of 14 files:

- Each file: `Voltages_R2` (n × 72, V, 2.87–4.23 V), `CellTemp_R` (n × 72, °C, **one temperature per cell**),
  `SOC_R2` (n × 72), `Current_R2` (−191 to +150 A), `Temptime` at **1 Hz**; runs of 0.2–3.1 h (≈ 11 h total).
- Median cell spread 31–138 mV; a persistent weak cell at index 13 in 9 of 13 runs (−6 to −12 mV).
- **Intra-pack temperature gradients that H and H2 never saw:** `HWFET_15C_ModuleBlocked_Long` has cell
  temperatures 1–37 °C, **median spread 28 °C**; `Fanoffon_15C_Long` reaches 46 °C with a 3 °C median spread but
  large transients; `HWCUST_15C` 5 °C spread. Changan's charging probe spread was 3 °C median; Weihai's 4 °C.
- Current sign convention and the 6C charge segments mentioned in the README need checking before replay
  (charge appears as positive ≈ +50 A plateaus in several runs; not verified here).

This is the regime in which the H pre-registration says per-cell can differ from min/max (temperature
coupling), with the cell-to-probe mapping *known* (per-cell thermistors) instead of ASSUMED. See §4, proposal 2.

---

## 4. Best next experiments

Each entry: hypothesis · data · pre-registered decision rule (sketch) · cost · expected value. Ordered by
value per unit cost.

### 4.1 G.3 — BATSS ISC blind-confirmation case study (zero cost, in hand, CC BY)

- **Hypothesis.** A per-cell rest-drift feature identifies the cell carrying the permanently connected
  balancing resistor; the min-voltage heuristic identifies a different cell. (From the probe above: drift → cell
  8; min → cell 2.)
- **Data.** `BATSS_20-21-22_ISC_results.xlsx` plus the healthy-pack files (tests 7–19) as the null distribution
  for drift rates. BatICM (MIT, already cloned per G.1b) car2/car3/car4 as three more located cases (ISC #83,
  self-discharge #82/#3, resistance rise #64) with the BMS warning column as a timing reference.
- **Decision rule.** Pre-register: (i) feature A' = per-cell OLS slope of rest deviation over the final rest,
  robust-z across the 10 cells; prediction = argmin z (disclosed as formed after inspection: cell 8); (ii) the
  min/max control = modal min cell (cell 2); (iii) outcome table: author confirms 8 → "drift identifies ISC
  where min/max misidentifies"; confirms 2 → "min/max suffices, drift mis-fires"; other → both fail; no reply →
  report as a prediction on record. On BatICM: does A' rank the paper's cell top-1 in each car, and how many
  days before the first BMS warning does z cross the healthy-pack 99th percentile? n = 4 total; **no p-values**,
  case-study rules per the G brief.
- **Cost.** One day CPU. One email from Kyle to the CIDETEC contact (Arrinda) asking only "which cell position
  carried the resistor in tests 20–22" — the review did not send it.
- **Value.** First ground-truth-by-construction evidence for or against G.2's mechanism; permissive licence;
  also yields an ISC-resistance estimate method (drift → drain current) that is an MCU-class feature.

### 4.2 H3 — per-cell limiting where temperature gradients actually exist (McMaster + BATSS, CC BY)

- **Hypothesis.** When intra-pack temperature spread exceeds ~10 °C, a per-cell limiter (own V, own T) differs
  from the min/max limiter on a material fraction of frames and the counterfactual charge-time saving exceeds
  H's pre-registered 1 % at the median of gradient sessions.
- **Data.** McMaster 72S runs (per-cell thermistors — mapping known), stratified by run type (nominal / fan off /
  module blocked / high fan; 15 °C and 25 °C chamber); BATSS Ta10/Tl25 and Tl10 runs (10 cells, 55
  thermocouples). Use charge segments only (verify current sign first); replay H's exact `C_T` and taper, same
  code path (`analysis/H_replay.py` generalised), same M1-vs-known-mapping comparison — this also measures how
  wrong the ASSUMED M1 mapping was.
- **Decision rule.** H's rule unchanged (median S_mm ≥ 1 % ⇒ "per-cell recovers X"), but applied *per thermal
  regime* pre-declared by the max intra-pack spread in the session (< 5, 5–10, 10–20, > 20 °C). Secondary: the
  fraction of frames where the constraining cell is not on the coldest/hottest sensor. Also report the gap
  between the known-mapping result and M1/M2 on the same frames.
- **Cost.** 1–2 days CPU; optional board re-gate using McMaster frames (half a day with a hard reservation).
- **Value.** Converts H/H2's "cold/gradient regime untested" into a measured curve; small n (≈ 20 runs) but the
  only per-cell-temperature pack data in hand. Honest limit: drive-cycle pack, not a fleet.

### 4.3 E-LFP — per-cell SOC/capacity ranking on an LFP BESS (Weihai, CC BY)

- **Hypothesis.** For LFP, per-cell knee-crossing order (first frame each cell exceeds 3.40 / 3.45 V during a
  full charge, converted to Ah-delivered-at-crossing) gives a per-cell SOC-offset/capacity ranking that is
  stable across months and predicts the rack's top cell and end-of-charge spread; min/max gives none of this.
- **Data.** Weihai, 217 cluster charge operations × 9 racks; the H2 10 s grid, zero-order hold and `mcos_dt`
  decoder already exist. H2 found the median top cell at 3.377 V, so only the subset of operations that reach
  ≥ 3.45 V on ≥ 10 % of cells qualifies — count that first and pre-register a minimum (e.g. ≥ 30 operations
  spread over ≥ 4 months).
- **Decision rule.** (i) Month-to-month Spearman of the per-cell crossing-Ah ranking within a rack ≥ 0.7
  (pre-set) on ≥ 7 of 9 racks ⇒ "stable per-cell state exists"; (ii) early-month per-cell ranking predicts the
  identity of the top-3 cells in the final month with precision ≥ 0.5 vs a min/max control that can only name
  the current max cell; (iii) report the per-cell ΔSOC spread in Ah and as % of rack capacity (DERIVED).
- **Cost.** 2–3 days CPU; no board. **Value.** This is the question LFP BESS operators actually pay for
  (balancing/replacement scheduling under a flat plateau), on a commercially clean licence, on 3,564 cells.

### 4.4 G.4 — learned per-cell model vs the hand feature (Beihang, CC BY) — first AP/NPU-class test

- **Hypothesis.** A small model that ingests the full per-cell deviation vector (e.g. a per-vehicle
  autoencoder trained on *normal* vehicles' early windows, scored by reconstruction-error drift; or a 1-D CNN
  over cells × blocks) separates faulty from normal better than feature A (0.59 early) — or it does not, in which
  case the AP/NPU adds nothing over a 10-line MCU feature.
- **Data.** Beihang QAS (393 vehicles); same early/late windows, same bootstrap, same 5 negative controls and
  the pre-registered adjusted logistic model. Add the de-confounding checks the first run lacked: (a) restrict
  normals to the ID range adjacent to the faulty block (if batch structure is by ID), (b) temperature-matched
  AUC as a *pre-registered* secondary, (c) nested CV by vehicle with the model fitted on normals only.
- **Decision rule.** Three-way: learned ≥ A + 0.05 AUC with difference-CI > 0 ⇒ "learned per-cell model adds
  value"; |Δ| < 0.05 ⇒ "feature A suffices (MCU)"; learned < A ⇒ "no". Keep the 0.70 SUPPORTED bar.
- **Cost.** 1–2 days CPU; board: export to TFLite int8 and run on the A55 *and* the NPU (eIQ) with the Study-1
  gate — MEASURED latency/energy per 110-cell vector. **Value.** The first experiment whose answer actually
  depends on having AP-class compute; also the replication G.2 needs.

### 4.5 G.5 — bench fault-injection string (the G.1 recommendation, costed)

- **Hypothesis.** F's four-class classifier (with the minimum-shift floor fix) assigns the injected class with
  ≥ 80 % accuracy across ≥ 5 repeats per class, and a min/max-only classifier cannot exceed chance on the tap
  and offset classes.
- **Data.** Own: a 12–16S string of cheap cells on an off-the-shelf AFE evaluation board logging every cell at
  ≥ 1 Hz; injections one at a time: series resistor in one sense lead, resistor in a *shared* tap, fixed tap
  offset, one cell pre-discharged by 5–10 % SOC, ISC resistor across one cell, module-wide bias. Blind labels
  held by a second person. Release under CC BY — this is also how the programme escapes the Changan NC-SA
  dependency for the diagnosis claim.
- **Decision rule.** Pre-registered confusion matrix with class accuracy thresholds; min/max classifier as the
  comparator; n per class fixed in advance.
- **Cost.** US$1–3k of hardware, 2–4 weeks part-time. **Value.** The *only* route to confirming F; produces a
  dataset the G.1 search shows does not exist publicly — itself publishable.

### 4.6 R1 — per-cell data reduction and history retention (Changan NC-SA + Weihai CC BY)

- **Hypothesis.** A pack-side encoder (deviation-from-mean at 1 mV with deadband change-logging plus
  event-triggered full frames) preserves the F and G.2 features *exactly* at < 10 % of the raw per-cell byte rate,
  and a year of per-cell history for 96–3,564 cells fits in tens to hundreds of MB.
- **Data.** Changan per-cell vectors (148 M synced frames exist as `.npz`) and Weihai (already change-logged —
  measure its native compression ratio vs the 10 s grid).
- **Decision rule.** Bytes/cell/day under three schemes vs raw (DERIVED); features A/B/event catalogue
  bit-identical ⇒ "lossless for the tested uses"; MEASURED on the board: encode/decode cost and sustained write
  rate to eMMC/SD for 3,564 cells at 10 s. Pre-register the "lossless" criterion as feature identity, not RMSE.
- **Cost.** 1 day CPU + half a day board. **Value.** This is the one AP-specific resource (storage, IO,
  connectivity) the programme never quantified; the Changan half is non-commercial, the Weihai half is clean.

*(Not proposed: moving the limiter to the i.MX 95 M7 — correct engineering, but it would only confirm what
H-b already implies.)*

---

## 5. Presentation — making the body of work credible and useful

1. **One public summary**, not nine write-ups. The dossier is the right document; make it the README of the
   public repo with the §9 table rewritten (see §2.2) and add the proposed "could this data have shown the
   effect?" column. Readers should see within one screen which results are nulls, which are resolution limits,
   and which are positives.
2. **A negative-results / methods paper.** Working title: *"Pre-registered tests of per-cell battery telemetry
   against scalar BMS summaries on public field data: what can and cannot be resolved."* The committed
   pre-registrations with git hashes are the unusual asset; the resolvability analysis (E's oracle ceiling vs
   MDE, Study 2's noise-vs-fade ratio) is the intellectual contribution; the G.1/G.1b search ("no public
   per-cell + located-fault dataset exists") is a citable gap statement. Venues that take negative/methods
   work in this area: *Journal of Energy Storage*, *eTransportation*, *Batteries*, or an arXiv + Zenodo
   release. Changan-derived numbers can appear in a paper under CC BY-NC-SA with attribution; the
   commercial-safe headline must rest on Beihang/Weihai/BATSS/McMaster (all CC BY) — the write-ups already
   track this; the paper must too.
3. **Figures that carry the argument** (the repo has 10 PNGs, none summarising):
   - resolvability plot: per-dataset label noise / effect size vs the MDE line (Study 2, E);
   - a "where the per-cell gain could live" plot for H/H2: saving vs intra-pack temperature spread, with the
     Changan and Weihai spread distributions overlaid (and, after §4.2, McMaster);
   - G.2 ROC with the temperature-stratified curve beside it (exists in parts);
   - a programme matrix: experiment × {dataset, licence, label type, n positives, resolvable?, verdict}.
4. **Repo hygiene for the public mirror** (github.com/kylefoxaustin/battery-soh-finetune currently has
   Studies 1–2 only): push E–H2 analysis/board code (MIT) and all pre-registrations; put Changan-derived result
   tables/JSON in `results/changan_nc_sa/` with a `LICENSE-DATA.md` (CC BY-NC-SA, attribution to Liu et al.);
   keep Beihang/Weihai/BATSS/McMaster-derived results under CC BY; add `CITATION.cff`, a `DATA.md` with every
   dataset's DOI/licence/row-count, and the raw JSON per experiment (already present locally). State the
   commit hash of each pre-registration in the README table.
5. **Terminology and small corrections** an outside reader will catch: the GB/T 32960 statement (§1.1a); H-b's
   comparison to a 22.8 ms LSTM inference should say the limiter is an MCU-class task; the dossier's data table
   lists BATSS/McMaster as "CC BY" — give the 4.0 and the DOIs; results_E references UMich/NREL as "not
   examined" — say why (not needed after NO-GO).
6. **Independent replication of G.2.** It is the only positive and it is confounded. Before it becomes a slide
   claim, have someone outside the loop re-run `G2_beihang.py` from the pre-registration alone, and run §4.4.
7. **Say the positive thing the data supports.** "A cloud-trained fleet model running on the pack beats every
   per-unit alternative we tried, including a running average, at every horizon on Changan" is a true,
   useful statement for an inference-on-device product story; it is currently buried as the null hypothesis.

---

## Appendix A — numbers introduced in this review

| Number | Tag | Source / derivation |
|---|---|---|
| GB/T 32960 frames carry `CellsVoltage` (all cells) and `ProbesTemp` arrays | SOURCED | https://docs.emqx.com/zh/enterprise/v4.2/modules/gbt32960_protocol.html |
| i.MX 95: 6× Cortex-A55 up to 2.0 GHz, Cortex-M7 + Cortex-M33, eIQ Neutron NPU 2.0 TOPS | SOURCED (secondary) | https://www.ezurio.com/support/faqs/what-is-the-npu-performance-on-the-nitrogen95-and-how-does-it-support-edge-ai-inference-workloads ; https://docs.peridio.com/hardware/under-evaluation/frdm-imx-95 |
| EU 2023/1542 Art. 10/14 SoH information duties; applicability to models after 18 Aug 2024 | SOURCED (manufacturer disclosure) | https://www.livewire.com/en-gb/documents/battery-regulation ; primary: CELEX 32023R1542 (eur-lex fetch failed in this session) |
| BATSS ISC: 62,817 rows, 1 Hz, 17.5 h, 3 cycles + 10 h rest; cell 8 −1.00 mV/h, cell 2 −0.73 mV/h, others +0.16…+0.27 mV/h; min cell = 2 | DERIVED | `scratchpad/review/big/batss_isc_probe.py` on the downloaded xlsx |
| BATSS ISC implied drain 40–60 mA, ~70–100 Ω | DERIVED (ASSUMED capacity and dOCV/dSOC) | order-of-magnitude arithmetic above |
| McMaster: 72 cells, per-cell T, 1 Hz, 13 runs 0.2–3.1 h; module-blocked run T 1–37 °C, median spread 28 °C | DERIVED | `scratchpad/review/big/mat5_probe.py` on the downloaded .mat files |
| Changan raw per-cell byte rate ≈ 1.66 MB/vehicle/day | DERIVED | 96 cells × 2 B × 8,640 frames/day |
