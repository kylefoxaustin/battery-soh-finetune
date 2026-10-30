# X5 dataset audit and profile (brief §2–§3)

Run 2026-10-29 by `analysis/X5_profile.py`. Outputs: `X5/profile.json` and `X5/split.json`.

**No estimator (P0–P4), reserve or gain has been computed.** Every number is DERIVED unless tagged SOURCED.

**Brief.** `briefs/X5/README.md`, from the public repo's `x5-brief` branch (commit `8eb30b4`). The three result packs
are copied to `results/X/{lifecost,convsim,x4}/`.

## Verdict of the audit

| Candidate | Passes? | Why |
|---|---|---|
| **A1. UMich 3P modules** | **No** | Parallel modules, so the module has no weakest-cell limit. Each module is tested once. The files carry no cell IDs, so no per-cell history exists. |
| **A2. BatICM cell-to-pack** (found in the search) | **Not as A** | These are real lab packs aged as packs, and the pack capacity is measured very cleanly. But **no cell inside a pack has a measured capacity**. The proposal is to treat it as a separate, descriptive question (§4). |
| **B. Yuasa second-life** | **No** | The per-cell Q values are **model estimates** from the same telemetry, not measurements. Against the reference they agree to 1.7 %, which fails the 1 % gate. There is only one snapshot. |
| **C. ISU-ILCC** (fallback) | **Yes** | Each cell is measured at C/5 every week. Label noise is **0.24 %** (median). There are 61 four-cell groups and **374 evaluation targets**. Caveat: the cells were never in a pack together. |

**Recommendation (§2.4):**

- Every Candidate A option fails the brief's own definition: no public set re-measures each cell's capacity inside a
  string that aged together. That makes **Candidate C (ISU-ILCC) the primary**, with its coupling caveat.
- BatICM lab packs: a possible descriptive secondary, at the reviewer's choice (§4).
- Yuasa: not run.

## 1. Audit table (brief §2)

| | UMich 3P | BatICM cell-to-pack | Yuasa | ISU-ILCC |
|---|---|---|---|---|
| **Source** | Mendeley `10.17632/ssrgfmb8vw.2`; arXiv 2604.16769 | Zenodo `10.5281/zenodo.20132842` (2026-05) | Zenodo `22281620` → code archive with `yuasa/data/`; arXiv 2609.04487 | figshare `10.25380/iastate.22582234`; arXiv 2307.08382 |
| **Licence** | CC BY 4.0 | **CC BY 4.0** (record metadata) | MIT | CC BY 4.0 |
| **Cells** | 70 Sony VTC6 (NCA/Gr-Si, 3 Ah), reused across 78 modules | 34 single lab cells; 6 lab packs (16s, 15s, 16s, 52s LFP; 2 × 15s NMC); 16 field packs (416s) | 324 logical cells (2P), 27 modules of 12s | 251 Li-polymer NMC/graphite, 250 mAh |
| **Tested as** | Cells **separately**, then 3P modules | Packs **as packs**; same-batch cells separately | One field system (MMC converter) | Cells **separately**, 4 per condition, 63 conditions |
| **Capacity method** | 1C CC discharge, 25 °C, Maccor | Pack: current integration per cycle, about 0.5C (LFP) or 1.5C (NMC). Cells: per cycle. | GP-ECM model fit to 12.5 h of field data. Reference: one C/25 cycle on the onboard sensors (96 cells). | RPT C/5 CC discharge after CC-CV, 30 °C chamber, Neware |
| **How often** | Cells re-characterised about every 1 % SOH. Each module is tested once. | Every cycle (433–1,176 records per pack) | Once | Weekly, plus 0.5 week for groups 20–64 |
| **Stated label uncertainty** | No number given; the authors say labels "may contain errors" between re-characterisations (SOURCED) | None stated | Model vs reference: RMSE **1.25 Ah** absolute, 0.55 Ah within-module (SOURCED, paper Fig. 6) | None stated |
| **Per-cell measured capacity over life?** | No (no cell IDs; ageing cycles not published) | **No** (only cell voltages inside the pack) | No | **Yes** |

**Also searched**, not candidates:

- Imperial parallel packs under thermal gradients (Zenodo 10207731, CC BY 4.0): parallel strings.
- arXiv 2507.14020 (retired modules, capacity by cell position): a snapshot, with unclear data availability.
- Zenodo 15755725 and 7250553, and Severson et al.: single cells.

The search used two broad web searches, two follow-ups and direct metadata pulls. It is not exhaustive.

**Two corrections to the brief:**

- **Yuasa.** The brief calls Q and Q_sigma "measured". The paper says they are reconstructed from field data, and that
  "a conclusive assessment would require characterizing cells individually in the laboratory" (SOURCED).
- **BatICM licence.** The older BatICM EV-fault set used in X3 is MIT. This cell-to-pack record is a different
  dataset, licensed CC BY 4.0.

## 2. Profile of the primary, ISU-ILCC (brief §3)

| Item (§3) | Value | Gate |
|---|---|---|
| **1. Label noise** | Median **0.24 %**, p90 0.75 % of capacity. 93 % of cells are at or below 1 %. 16 cells exceed 1 %, up to 8.8 %, from abrupt drops. | **≤ 1 %: PASS** |
| **2. Units** | **61** groups (62 with 4 cells, 1 with 3). Groups 11 and 14 are excluded, with < 6 common checks. Common checks per group: median 15 (6–37). | |
| **3. Spread** (max − min)/mean within group | First check: median **1.3 %** (p10 0.6, p90 2.1). Last check: median 40 % (p10 24, p90 64). | Spread exceeds noise about 5× at the start. **Per-cell information exists.** |
| **4. Weakest-cell persistence** | **89 %** of consecutive checks (pooled) | |
| **5. Power** | Evaluation half (31 groups): **374 targets** at W = 4 (W3 378, W6 349). Calibration half: 340. | **≥ 40: PASS.** 0.1 % α is an extrapolation (< 1,000). |
| Fade of the weakest cell over the record | Median 51 % (30–75 %). Cells run well past 80 %. | |

**How the label noise is estimated.**

- Each check is compared with the linear interpolation of its two neighbours, using a robust MAD scaled for white
  noise.
- Curvature and genuine recovery also enter this estimate, so it is an **upper bound** on measurement noise.
- The median change between consecutive checks is 2.4 %. That is real weekly fade, not noise. It is the same statistic
  that read 5.9 % on X4's field labels.

**Unit definition.**

- A "pack" is the 3–4 cells of one test condition, aligned on the RPT schedule (matched within 0.5 time units).
- The unit's life ends at the **first check any cell is missing**: the first cell to stop ends the pack.

**Split** (`X5/split.json`, brief §4.3; seed-0 permutation of the 61 usable groups):

- calibration: 30 groups;
- evaluation: 31 groups.

## 3. Other candidates, profiled

**UMich.**

- 78 modules, 3 cells each, one test per module.
- Within-module capacity spread: median 10.7 % (max 24 %).
- Module capacity is **0.987 × the sum of its cells** (p05–p95: 0.982–0.990). In parallel, the module sees the sum,
  not the weakest cell.
- No cell IDs in `Summary.csv` or the raw headers (Table 5 of the descriptor), so **0 history targets**.

**BatICM lab packs** (pack labels are MEASURED, by current integration):

| Pack | Chem, cells | Records (cycles) | SOH first → last | Label noise | End-of-charge cell spread (median) | Charge ends on | Top-cell persistence |
|---|---|---|---|---|---|---|---|
| 1 (ESSL1) | LFP 102 Ah, 16s | 433 (2–534) | 0.98 → 0.76 | 0.10 % | 147 mV | Pack voltage (Vpack p05–p95 56.26–56.31 V) | 82 % |
| 2 (ESSL2) | LFP 105 Ah, 15s | 1,176 (4–1,281) | 0.99 → 0.81 | 0.17 % | 200 mV | Mixed | 59 % |
| 5 (ESSH1) | LFP 302 Ah, 16s | 503 | 1.02 → 0.98 | 0.02 % | 130 mV | **Top cell at 3.65 V** | 91 % |
| 6 (ESSH1) | LFP 302 Ah, 52s | 519 | 1.00 → 0.96 | 0.01 % | 165 mV | **Top cell at 3.65 V** | 100 % |
| 3 (PBSL1) | NMC 4 Ah, 15s | 449 | 0.99 → 0.78 | 0.14 % | 21 mV | Pack voltage | 94 % |
| 4 (PBSL1) | NMC 4 Ah, 15s | 381 | 0.98 → 0.78 | 0.13 % | 12 mV | Pack voltage | 85 % |

Readings:

- Label noise passes easily, and targets are plentiful (1,478 in a 3-pack evaluation half).
- But the **effective sample is 6 packs, 3 scored**.
- Only packs 5 and 6 end charge on a cell limit, which is where the weakest cell sets usable charge. Two packs of the
  ESSH1 pair fade only 4 %.
- The 34 single lab cells have per-cycle measured capacity with label noise median 0.014 %.

**Yuasa** (SOURCED from the paper; not downloaded beyond the archive listing):

- Labels: model vs reference RMSE 1.25 Ah on cells of about 75 Ah, which is **≈ 1.7 % and fails the gate**.
- Within-module agreement: 0.55 Ah (≈ 0.7 %).
- Both labels come from the same onboard sensors.
- Snapshot only, so the history question is untestable. The snapshot question would score telemetry-derived estimates
  against labels derived from the same telemetry, which is circular.

## 4. Decision needed from the reviewer

1. **Accept ISU-ILCC (Candidate C) as primary?** It is the only candidate with measured per-cell capacity over life.
   Every verdict will carry: *"synthetic packs of separately tested cells; no thermal or electrical coupling; an upper
   bound on what per-cell history can do."*
2. **BatICM lab packs as a descriptive secondary?** Here the question becomes: *does per-cell telemetry (end-of-charge
   cell voltages) predict a pack's **measured** usable charge better than the pack's own capacity trend?* There would
   be no verdict, since there are only 3 scored packs. It is not pre-registered yet. I'd draft it only on a yes.
3. The pre-registration (`X5_preregistration.md`) records **five departures from the brief's text**, each with its
   reason (§0 there). The two that matter most:
   - **The reserve sign.** The brief's `q(1−α)(−e)` with `e = U_pred − U_true` measures **under**-prediction. The
     reserve guards against **over**-statement, so X5 uses `q(1−α)(e)` and reports the brief's form beside it. X4
     (`x4.py` lines 104–106) used `q(−e)`, so **X4's reserve column measured the other tail.**
   - **P3 with last-value trend is identical to P0.** The minimum of last values is the last minimum, so that
     sensitivity is degenerate.

**Licences:** ISU-ILCC CC BY 4.0; BatICM cell-to-pack CC BY 4.0; UMich CC BY 4.0; Yuasa MIT. **Data:** in
`data/raw/{isu_ilcc,baticm_c2p,umich_ppm}` (gitignored). The BatICM pickles were opened only through an allowlisted
unpickler, after a static scan of every file's imports.
