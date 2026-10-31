# FR1 pre-registration: how long a pre-event window would field data have needed to find the root cause of public HV power-electronics failures?

**Brief:** [`briefs/FR1/README.md`](../../briefs/FR1/README.md).
**Case list:** [`FR1_cases.md`](FR1_cases.md), with a machine-readable copy in [`FR1_screen.json`](FR1_screen.json).
**Screen:** [`analysis/FR1_screen.py`](../../analysis/FR1_screen.py).

**Ordering.** This file and the case list are committed **before rating**.

- To build them, no defect summary, consequence, corrective-action or notes text was read, printed or written.
- The screen touched those fields only to count campaigns whose defect summary is non-empty (§2, step S4).
- No ratings exist.

**Tags.** Every rating will be **DERIVED-judgemental**, and every table will say so. No rating is MEASURED.

**Windows used as thresholds.**

| Window | Tag | Source |
|---|---|---|
| 671 s (2 GB at 3.2 MB/s) | MEASURED | B1, [`results/B1/results_B1.md`](../B1/results_B1.md) |
| ~1 s (MCU freeze-frame) | DERIVED | ANGLES §B.3 |
| 40 s (HyperRAM) | DERIVED | ANGLES §B.3 |
| 80 s (MCU SDRAM) | DERIVED | ANGLES §B.3 |

They are category edges only. No rating is compared numerically against them.

**Licence.**

- NHTSA recall records and Part 573 reports are US Government works, in the public domain. The source is carried on
  every table.
- EU Safety Gate is not used (§1, FR1-P2).

## 0. Departures from the brief's text (fixed now)

| # | Brief | FR1 | Why |
|---|---|---|---|
| **FR1-P1** | §3.1: include a case "if … the public record contains a stated cause". Exclude software-only and no-cause cases. Rule 1: "inclusion is decided from the component and symptom fields only". | **The list stage applies only the component, plug-in and summary-present rules (§2).** The two cause-based exclusions are applied **at rating**: a case is excluded only if **both** raters flag it (§4.3). The excluded count is reported. | Whether a cause is stated, or whether it is software-only, can only be judged by reading the cause text. Rule 1 forbids that before the list is fixed. The mechanical proxy for "a cause is stated" is a non-empty Part 573 defect summary: all 75 cases have one. |
| **FR1-P2** | §2: EU Safety Gate (RAPEX) entries | **Not used.** | Safety Gate has no public bulk or structured API: a JSON probe on 2026-10-31 returned 405. Its records have no separate component field, so a screen would have to read the risk description, which states the cause. That would break rule 1. Its reuse terms are also not settled here. |
| **FR1-P3** | §2: published failure analyses of OBC / DC-DC / inverter field returns | **Not in the case list.** | A paper's title and abstract state the cause, so it cannot be screened blind. Its unit is also a failure mode, not a field campaign. Raters may not use papers to rate a campaign (§4.1). |
| **FR1-P4** | §2: NHTSA ODI investigations (PE/EA) and TSBs as cases | **The unit is the recall campaign.** An ODI résumé may be used as a rating document only when the campaign is linked to it (§4.1). | Investigations without a recall have no Part 573 and no common document format. The seed investigation PE23011 enters through its recalls 24V-204 and 24V-868 (cases PE034 and PE050). |
| **FR1-P5** | §3.4 primary: "the fraction rated > 80 s and > 1 s" | **The fraction > 40 s is also a primary readout.** | The brief's own CONVENIENCE row (§3.5) is defined on > 40 s. |

## 1. Sources and search window

- **Source.** NHTSA ODI recall flat file `FLAT_RCL_POST_2010.zip`.
  - Downloaded 2026-10-31 from `static.nhtsa.gov/odi/ffdd/rcl/`.
  - 14,990,524 B, SHA-256 `5d8cc101ff4c191d87234bbac807c73b92348a3a48fca9a2281436d704c99c56`.
  - It contains `FLAT_RCL_POST_2010.txt`, dated 2026-10-30 in the archive: 247,021 records, 15,368 campaigns.
  - The field layout is NHTSA's `RCL.txt`, last updated May 2025.
- **Window.** Part 573 received date (RCDATE) from 2018-01-01 to 2026-10-31. Vehicle campaigns only (RCLTYPECD = V).
- **Coverage caveat.** The manufacturer-supplied component fields (MFR_COMP_NAME and MFR_COMP_DESC, added in 2020) are
  empty for every 2018 record and for 98 % of 2019 records. Campaigns from those years are screened on NHTSA's
  component code alone. The seed case shows why that matters: 24V-204 is coded "ELECTRICAL SYSTEM: 12V/24V/48V
  BATTERY" and only its manufacturer field says "ICCU". **The earliest included case is from 2019-11.** The list is
  therefore effectively a 2019–2026 list.

## 2. Screen (component, model and date fields only)

| Step | Rule | Campaigns |
|---|---|---|
| S1 | Vehicle campaigns in the window | 7,915 |
| S2 | A component term (below) in COMPNAME, MFR_COMP_NAME or MFR_COMP_DESC of any record. Exclusion terms are removed first. Records whose COMPNAME starts with `EQUIPMENT:RECREATIONAL VEHICLE/TRAILER` are skipped (RV house electrical). | 123 (OBC 16, DC-DC 13, inverter 60, BMS/contactor 45; a campaign can hit several groups) |
| S2b | **Propulsion context:** some record's COMPNAME contains `PROPULSION`, or a strict OBC term (`ON-BOARD CHARG`, `OBC`/`OBCM`, `ICCU`, `INTEGRATED CHARGING`) appears in a component field | 99 |
| S3 | **Plug-in.** P1: COMPNAME contains `PROPULSION SYSTEM:CHARGING`, or a strict OBC term appears. P2: the make is in the BEV-maker list, or a model name matches the plug-in model patterns. | **75 included** (P1 14, P2 61). 24 unresolved, listed but not included. |
| S4 | Part 573 defect summary non-empty (the only use of that field: a count) | 75 of 75 |
| S5 | Mechanical clusters: same manufacturer, a shared component group and a shared model name (union-find) | 52 clusters |

- **Exact terms.** The component terms, exclusion terms, BEV-maker list and model patterns are in
  `analysis/FR1_screen.py` (`GROUPS`, `NOT_TERMS`, `OBC_STRICT`, `P2_MAKES`, `P2_MODEL`) and are copied into
  `FR1_screen.json`.
- **The groups are those named in brief §3.1:**
  - OBC / charging control unit;
  - DC-DC converter;
  - traction inverter / motor controller (including PCU);
  - HV BMS / contactor / junction unit.
- **The traction battery itself is not a group.** Cell or module defects are out of scope unless a BMS, contactor or
  junction term also appears.

**Revision 1 (disclosed).** The rules were revised once, before this commit. The revision came after inspecting the
**make, model and component fields** of a first pass's hits, with no cause text.

- **Why.** The first pass:
  - let RV solar charge controllers and house converters through on a bare "CHARGER" term;
  - missed BEVs whose model names my first pattern list did not cover (e.g. "MUSTANG MACH E" without a hyphen; Zero,
    Arcimoto and LiveWire motorcycles and vehicles; battery-electric buses and trucks).
- **What changed:**
  - S2b was added;
  - a bare "CHARGER" no longer stands in for a plug-in or a propulsion context;
  - "SOLAR …" was added to the exclusion terms;
  - the BEV-maker and model lists were extended.
- **The first pass is not kept.** The revision is marked in the code.

**Known screen artefacts, left in by rule and flagged for the reviewer.** Each is component- or model-field
information, not cause text.

- **PE006** (Honda Accord Hybrid, CR-V Hybrid, Insight). These are non-plug-in hybrids by model name. It enters
  through P1 because NHTSA coded a `PROPULSION SYSTEM:CHARGING:MODULE` component.
- **Possibly out of scope.** In these, the named manufacturer component may not be one of the four groups, e.g. a
  signal connector, a cabin water pump or a fuse-box bracket on a campaign that also hit a group term: PE039, PE041,
  PE044, PE056 and PE057. They are handled at rating by the scope check (§4.3).
- **Unresolved, not included (24).** These are mostly non-plug-in hybrids by model name (Prius, Camry, Accord,
  Elantra Hybrid, …) and buses or vans whose names do not say whether they are electric (Nova LFS, Gillig Low Floor,
  Blue Bird, Ram ProMaster). **The reviewer may move any of them in, from model names alone, before rating.** Nothing
  else in this file changes if that happens.

**Base-rate sample (brief §3.2).**

- **Pool.** The 1,867 vehicle campaigns in the window whose **every** record's top-level COMPNAME is:
  - body: STRUCTURE, LATCHES/LOCKS/LINKAGES or SEATS;
  - chassis: SUSPENSION or WHEELS;
  - restraint: AIR BAGS or SEAT BELTS.
- **Draw.** Order the pool by campaign number and take indices 12, 36, 60, … (k = ⌊1,867 / 75⌋ = 24, start k/2). That
  gives **75 base-rate cases**, BR001–BR075, rated with the same scheme.

## 3. Rating scheme (fixed now; every item is a closed list)

For each case, each rater records:

1. **Cause type:**
   - transient electrical (over-current / over-voltage / short);
   - thermal cycling or thermal overload;
   - manufacturing or component defect;
   - software or calibration;
   - unknown / mixed.
2. **Evidence that identified it**, as stated or clearly implied by the rating documents:
   - DTC freeze-frame;
   - bench reproduction;
   - fleet statistics;
   - waveform or high-rate capture;
   - teardown only;
   - not stated.
3. **Judged minimum pre-event window, at a stated data rate, for field data alone to have identified the cause:**

   | Category | Meaning |
   |---|---|
   | **≤ 1 s** | an MCU freeze-frame |
   | **(1, 40] s** | within a HyperRAM window at 3.2 MB/s |
   | **(40, 80] s** | within an MCU-SDRAM window |
   | **(80, 700] s** | within B1's measured 2 GB window |
   | **> 700 s** | longer than B1's window |
   | *cannot judge* | |

   The rater also names the signals needed (e.g. switch-node voltage, DC-link current, cell voltages) and the sample
   rate, in free text.
4. **Confidence:** low / medium / high.
5. **Flags (for §4.3):**
   - *no cause stated*;
   - *software-only, no electrical event*;
   - *component out of scope* (the defective part is not an OBC, DC-DC converter, inverter / motor controller or
     HV BMS / contactor / junction unit).

**Base-rate cases** use items 1–4. For them, item 3 asks the same question about the body, chassis or restraint
defect.

## 4. Rating procedure

### 4.1 Documents

A rater rates each case **from its cited documents only**:

- **Always:** the campaign's **Part 573 Safety Recall Report**, including the chronology attachment where NHTSA
  publishes one.
- **Only when the campaign is "Initiated by: ODI" or the Part 573 cites an investigation:** the **ODI investigation
  résumé(s)** (opening and closing) for that investigation.

Nothing else is used: no TSBs, no press, no papers, no memory of the case. A rater who cannot open a document records
*cannot judge*.

### 4.2 Raters

- **Two raters, blind to each other:**
  - **Rater A:** this session.
  - **Rater B:** chosen by the reviewer, either the reviewer itself or a fresh session that has not seen rater A's
    file.
- Each rater commits `results/FR1/ratings_<rater>.csv` (one row per PE and BR case, items 1–5 plus free text) before
  seeing the other's.
- The order of rating is randomised per rater: rater A uses `numpy.random.default_rng(1)`, rater B
  `default_rng(2)`. PE and BR cases are interleaved, so the rater rates without regard to which list a case came from.
  The case ID's prefix still shows the list. That is disclosed, not hidden.

### 4.3 Exclusions at rating (FR1-P1)

- A case is **excluded from all fractions** if **both** raters set the same flag. The flags are:
  - no cause stated;
  - software-only, no electrical event (PE only);
  - component out of scope (PE only).
- A single rater's flag does not exclude; it is reported.
- If the exclusions take the PE count below **10**, the verdict is **UNGATED**.

## 5. Readouts (pre-registered)

The analysis code is `analysis/FR1_agreement.py`, written at stage 2.

**Primary, on the PE cases.** The fractions of cases rated **> 80 s**, **> 40 s** and **> 1 s**:

- **Conservative reading (deciding):** for each case, the **lower** of the two raters' window categories. Brief §3.4
  calls this the reading against §B.3.
- **95 % Wilson CIs.**

**Denominator.**

- Cases neither excluded (§4.3) nor rated *cannot judge* by **either** rater.
- The *cannot judge* count is reported.
- Sensitivity: *cannot judge* counted as ≤ 1 s.

**Base rate.** The same fractions for BR cases. These are reported beside the PE fractions as the control. No test
between them decides anything.

**Agreement gate.** Cohen's κ on item 3, collapsed to **≤ 1 s / (1, 80] s / > 80 s**:

- computed over cases both raters rated with a window category;
- pre-registered gate: **κ ≥ 0.6**;
- also reported: κ on the six-way item 3, with *cannot judge* as its own category, and κ on item 1.

**Also reported, none deciding:**

- each rater's own fractions;
- the fractions by component group and by year;
- the one-case-per-cluster sensitivity, taking the earliest campaign of each of the 52 clusters;
- the "evidence" distribution (item 2);
- the signals and rates named;
- every disagreement, listed case by case and never reconciled.

## 6. Decision (brief §3.5, unchanged; on the conservative reading)

| Verdict | Condition |
|---|---|
| **UNGATED** | κ < 0.6, or fewer than **10** PE cases after exclusions |
| **RETENTION IS A NECESSITY** | ≥ **50 %** of PE cases rated > 80 s, **and** the Wilson CI lower bound > **20 %** |
| **RETENTION IS A CONVENIENCE** | < **20 %** of PE cases rated > 40 s |
| **UNCLEAR** | anything else |

A clean "most causes need ≤ 1 s" is a result (brief rule 7). No dollar figure is computed.

## 7. Outputs (stage 2, after approval)

- `results/FR1/ratings_A.csv` and `ratings_B.csv`.
- `analysis/FR1_agreement.py`.
- `results/FR1/results_FR1.md`: verdict first, with the "DERIVED-judgemental" caveat and NHTSA as the source.
- One row each in `results/X/README.md` and `results/RESEARCH_DOSSIER.md` §9, and a dated note under ANGLES §B.3.

## 8. Deviations

Any change after this commit is a numbered deviation (D-1, D-2, …). After any rating has been written, none of the
following moves:

- the case list (apart from a reviewer move of unresolved cases before rating, §2);
- the base-rate draw;
- the categories and thresholds;
- the conservative-reading rule;
- the κ gate;
- the decision table.
