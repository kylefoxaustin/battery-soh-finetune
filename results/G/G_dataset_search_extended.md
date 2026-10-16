# Experiment G.1b — extended dataset search (niche sources)

Search run 2026-10-14. It follows [`G_dataset_search.md`](G_dataset_search.md) and was prompted by Kyle asking for "another
dataset somewhere out there no matter how niche".

**Method.** Three research sub-agents searched in parallel, each with extended web search:

1. **Data repositories.** Zenodo, figshare, Dryad, Dataverse, Borealis, OSF, IEEE DataPort, Kaggle and Hugging Face;
   US-lab and EU portals; Chinese, Korean and Japanese repositories, searched in English, Chinese and Korean.
2. **Papers, competitions and code.** Paper data-availability statements, PHM / NEV / Tianchi / DataFountain
   competitions, GitHub, theses, and NASA / ESA telemetry.
3. **Field and community sources.** EV owner forums, UPS / telecom battery-string monitoring, grid BESS incident
   investigations, DIY BMS logs, Formula Student teams, and satellites.

No sign-ups, no emails and no large downloads. One small public repository (BatICM, MIT licence) was cloned and
inspected; see below.

## Decision: G stays **NO-GO for confirming F's 4-class diagnosis**, but there are now partial routes

Still no public dataset has *deliberately injected* electrical faults that are located to a cell, on a series string
of 4 or more cells. These faults would be sensor offset or drift, sense-lead resistance, or connection resistance.
Every bench paper that injected them says the data is "confidential" or "on request", or gives no availability
statement. Ma / Mi, Applied Energy 2022, for example, physically loosened a cell 3–4 lead, and its data is
confidential.

This search did find **real-world packs with cell-located fault outcomes**. Those outcomes partly fill the gap left
by the n = 2 Yuasa case.

## New candidates, ranked

The **Verified** column gives the strongest check made on each source:

- **INSPECTED:** we opened the data ourselves.
- **READ:** read on the source page or in the PDF.
- **INFERRED:** inferred, not verified.

| # | Dataset | Per-cell telemetry | Fault labels | Independent + located? | Access | Verified |
|---|---|---|---|---|---|---|
| 1 | **BatICM / Nie, Deng et al., *Energy* 323 (2025) 135754.** github.com/BatICM/unsupervised-battery-faults | 4 EVs from China's national NEV monitoring platform. car1: 96 V + 24 T, 1 s, 1.6 days (2021). car2: 88 V, 30 s, Apr–Aug 2019. car3: 87 V, 10 s, ~4 weeks. car4: 87 V + 45 T, 30 s, ~3 months. Includes the BMS warning-level column. | Per the paper: car2 internal short circuit (ISC) in cell #83, ending in thermal runaway; car3 self-discharge in #3 and #82, ending in thermal runaway; car4 rising resistance in #64; car1 healthy | **Located: yes.** The thermal-runaway *outcome* is independent. The cause and cell are "confirmed through expert analysis", which is partly circular. | **Public, MIT** (4 small zips) | **INSPECTED** (see note below) |
| 2 | **Cao et al. (Beihang), *Nat Commun* 2025**, doi 10.1038/s41467-025-56832-8; zenodo 10656500 | 515 EVs, 3 makers, 30 s, 18.2 M rows. Some per-vehicle tensors are 90–91 columns wide, which is probably per-cell voltage (INFERRED). | Thermal runaway, electrolyte leakage, ISC, excessive ageing. "Determined by product engineers after **disassembling** the battery pack." | **Independent: yes.** Located: probably vehicle-level only (unverified). | **Public, CC-BY 4.0**, about 37 GB | READ paper; column meaning INFERRED |
| 3 | **Li, Che, Onori, W. Li, X. Hu**, arXiv 2608.10825 (Chongqing / RWTH) | 99 EVs, 14S NCM, 14 V + 4 T, 0.1 Hz, 16.4 M records | 47,968 samples in 4 cell-level classes (inconsistency, self-discharge, capacity fade, ISC), from recall logs, accident reports and teardown of *some* packs | **Located: yes.** Partly independent: the labelling rules are voltage patterns. | **Not yet public**: "upon final publication" | READ (PDF, Suppl. Note S1) |
| 4 | **BATSS 10s2p Northvolt pack (CIDETEC)**, zenodo 20490514 | 10 cell voltages (1 mV), 55 thermocouples, coolant data | **Injected ISC:** a balancing resistor held permanently on one cell, 3 runs | **Independent: yes, by construction.** Which cell is not in the metadata; it is in a 45 MB xlsx. | **Public, CC-BY 4.0** | READ (metadata) |
| 5 | **McMaster "Battery Pack with Introduced Faults" (SB Limotive)**, Borealis doi:10.5683/SP3/THZTJC | 72S PHEV pack via an Orion BMS; cell voltages + cell temperatures; 14 cases; 15 / 25 °C | **Physically introduced *thermal* faults:** fan off or over-speed, flow blockage, temperature-sensor failures | **Independent: yes.** Located to a submodule or sensor. No electrical faults. | **Public, CC-BY 4.0**, 92 MB | READ (README) |
| 6 | Tencent data-centre UPS strings (Tang / Du / Lin / Jia, IFAC 2020, doi 10.1016/j.ifacol.2020.12.854) | About 300 batteries (one voltage per battery) over 2 years, about 210 M records | Battery **replacement records** | Independent + located (INFERRED) | **On request** (repository lists no files) | READ (secondary sources) |
| 7 | Korea ESS fire investigations (MOTIE 2019 / KESCO 2020) | Investigators held BMS cell V / T logs from about 5 sites | Teardown, CT and ignition-point findings | Independent + located | **Not released** (narrative only) | READ (briefings) |

**Unlabelled but useful per-cell data:** these sets could rerun the H-a min/max-vs-per-cell replay at a much larger
cell count and in a different chemistry.

- **Weihai / SJTU BESS** (zenodo 20094787): 9 racks × 396 LFP cells, with 216 temperature probes per rack, over 8
  months; CC-BY 4.0, about 10 GB.
- Zenodo 20132842: lab packs of 15–52 cells plus field packs of 416 cells.
- Zenodo 18471156: a thin, low-trust upload.

**Low value or circular:**

- Korea AI-Hub OBD set: labels are thresholds on the same telemetry, and access is restricted to Korean nationals.
- A Formula Student 95s1p repo (MrAndy5): has a real dead sensor channel, but its cause was inferred from the
  telemetry.
- A quadruped-robot 7S set (CXL-edu): labels come from the voltages.
- The vLoong / DataFountain contest and arXiv 2201.12358: min/max cell voltage only.
- IEEE DataPort "Short Circuit 666 Wh": simulated.

**Dry:**

- PHM Society challenges: none on battery packs.
- ESA-ADB: its channels are anonymised.
- NASA: single-cell data only.
- Kaggle: synthetic data only.
- figshare, Dryad, Dataverse, OSF, Hugging Face and Science Data Bank: nothing relevant.
- Prius / Leaf / Bolt / Tesla owner forums: real located repairs, but as anecdotes and screenshots only, with no
  compiled logs.
- DIY BMS forums: same as the owner forums.
- ARENA, UKPN Smarter Network Storage, the Victorian Big Battery and APS McMicken reports: report-level only, no raw
  data.

## BatICM inspection (INSPECTED, 2026-10-14)

The four CSVs match the paper's description. The cell column with the largest mean |deviation from the pack median|
over each file's last 10% was:

| Car | Top deviant column(s) | Paper's faulty cell(s) |
|---|---|---|
| car2 | **V_82** | #83 |
| car3 | **V_81** and **V_2** (the top two) | #82 and #3 |
| car4 | V_32 / V_42 / V_40 | #64 is not in the top 4 on this crude metric |

**Indexing.** In car2 and car3 the paper's cell numbering looks 1-based against columns named `V_k`, giving a
consistent off-by-one. The paper uses `#n` while the columns run from V_1; the mapping needs checking before use.

**Reading this check.** It is a sanity check, not a result. It also illustrates the circularity: the "faulty" cells
are the ones that already stand out in the voltages.

## What this changes

- **For F's diagnosis claim:** still unconfirmed. None of the new sets labels F's sensor, tap or offset classes. The
  BatICM and Beihang labels are all *real-cell* faults (ISC, self-discharge, ageing). They could test the **real-cell /
  SOC-like** class, and whether per-cell beats min/max for **early warning**, which is F's under-powered primary
  question.
  - The BatICM paper claims a lead of more than 10 days over the BMS. Its own BMS warning column lets that claim be
    checked independently.
  - A min/max-only control could be run on the same frames.
- **Possible G.2 / F-replication (not pre-registered):** run F's forecast test on BatICM. Treat it as a case study
  with no p-value, since n = 3 faulty vehicles.
  - Then scale to the Beihang set if its 90-column tensors prove to be per-cell voltages, and if its labels can be
    tied to vehicles. That is a 37 GB download, so ask first.
- **Electrical sensor and tap faults** still need a bench injection or data from the authors (U-Mich / LG ES,
  Pecht 2022, Ma / Mi 2022).

**Licences.** BatICM is MIT. Beihang, BATSS, McMaster and Weihai are CC-BY 4.0. These permit commercial use, unlike
Changan's CC BY-NC-SA.
