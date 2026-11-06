# FR1: rater A's working conventions

*Written 2026-10-31, before rater A opened any rating document. Rater A's own reading of the pre-registration §3; it
does not change the scheme. Rater B does not see this file (D-2). Every rating is **DERIVED-judgemental**. Source of all
rated documents: NHTSA, public domain.*

**Files.**

- `ratings_A.csv`: 150 rows (75 PE, 75 BR), in `default_rng(1)` order.
- `rater_A_documents.json`: the document manifest, with file names, URLs and SHA-256.
- `analysis/FR1_docs.py`: the fetch script.

Every row is tagged DERIVED-judgemental.

## Documents

These are fetched by `analysis/FR1_docs.py` (manifest: `data/raw/nhtsa/fr1_docs/manifest.json`, with SHA-256):

- the latest Part 573 report (the original, or its latest amendment);
- every chronology attachment NHTSA publishes;
- the ODI résumé (the investigation description on the NHTSA record), **only** when the campaign is ODI-initiated or
  the Part 573 or chronology cites that investigation by number.

Nothing else is used. If a case has no Part 573 PDF, every item is rated *cannot judge*.

## Item 3: the window

The window is the shortest pre-event span of recorded vehicle data, at a rate the rater names, from which field data
alone would have shown the cause.

| The documents describe… | Window |
|---|---|
| A fast electrical event (short, over-current, over-voltage spike, a switching or gate-drive failure) whose signature lies in the last moments before the fault | **≤ 1 s** at a high rate (kHz to MHz on phase or DC-link current, switch-node or bus voltage) |
| A software or logic sequence (a state machine, a diagnostic, an interlock or a mode change) that unfolds over a drive or charge transition | **(1, 40] s** at CAN-signal rates (10 to 100 Hz), unless the documents point to a longer sequence |
| A cause that develops over minutes (heating during a charge or a sustained load; a resistance that creeps; a coolant-flow or pump-threshold problem) | **(40, 80] s** or **(80, 700] s**, by the time constant the documents imply |
| A cause that develops over hours, cycles or the vehicle's life (cell manufacturing defects that self-discharge; wear; corrosion; moisture ingress; material ageing; mis-assembly that shows only under long-term vibration) | **> 700 s** (the cause cannot be seen within B1's window) |
| A defect that no in-vehicle signal would show at any length (a wrong label or part, a missing fastener, a mechanical defect that is not instrumented) | **> 700 s**, with the free text saying "not observable in vehicle data at any window" |
| Documents too thin to say how the defect develops | ***cannot judge*** |

Base-rate cases (body, chassis, restraint) use the same table for their defects. Most are mechanical or material, so
most fall in the last two rows.

## Items 1, 2, 4 and 5

- **Item 1 (cause type)** follows the documents' stated cause. Use *unknown / mixed* when the documents name several
  causes and none of them is primary, or when they name none.
- **Item 2 (evidence)** records what the documents say identified the cause. When they describe several kinds, choose
  the most specific kind in the chronology (waveform > bench reproduction > teardown only > DTC freeze-frame > fleet
  statistics). Use *not stated* only when the documents give none.
- **Item 4 (confidence)** is how well the documents support the window, not the cause.
- **Item 5 (flags)** are set for PE cases only, except *no cause stated*, which applies to every case.
  - *Software-only, no electrical event* is set when the cure is software and the defect is a logic or calibration
    error with no hardware damage.
    *Clarified during rating, after case #20 and applied to every case from the start:* an "electrical event" means a
    real hardware fault outside the software, such as an isolation loss, a short, or a damaged part. If a real
    isolation fault is misclassified by software (PE040, PE061), the flag is **not** set. If firmware alone causes the
    excursion and no part is faulty (PE009), the flag **is** set.
  - *Component out of scope* is set when the part that fails is none of: OBC, DC-DC converter, inverter or motor
    controller, HV BMS / contactor / junction unit. For example, a cable, a 12 V battery, a cell or a motor winding.
