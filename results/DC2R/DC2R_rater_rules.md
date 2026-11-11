## 1. Carried over from DC2 by reference (unchanged)

Everything in [`DC2_preregistration.md`](../DC2/DC2_preregistration.md) applies unless §2 below names it:

| DC2 section | Content |
|---|---|
| §1 | scope in time (reading date November 2026); the pending rule (clarified, not changed, by DC2R-4) |
| §2 | definitions; deciding set; binding, window and allowance classes; the rate-unit and response-time rules; the `hard` default; the shape table |
| §3 S4 | allowed routes; no bypassing; `none` is a recorded result |
| §4 | the columns of `requirements_<A\|B>.csv` and `instruments_<A\|B>.csv`; the partial-access rule |
| §5 | matching (pass 1 normalised clause + category; pass 2 quantity + window class); gates; conservative reading; readouts; sensitivities STATED / ANY / SEED |
| §6 | decision table; access qualifier; consequence line |
| §7 | raters and blindness (two fresh sub-agents, sparse clones, conventions committed first, B after A and never fetching A) |
| §3b | the access threshold: access-limited when both raters record `none` for **≥ 17 of the 50 seeds** |
| §10 | DC2-1 (group X, excluded from SEED) and DC2-2 (recurrence + duration converted to a share) |

**Thresholds, unchanged.** Identification M / (n_A + n_B − M) ≥ **0.80**; κ(window class) over the M₁ pass-1 pairs
≥ **0.60**; M₁ ≥ **10**, else UNGATED. NO HISTORY-SHAPED SPEC needs ≥ **8** binding deciding matched pairs from
≥ **4** instruments and no binding deciding `history` row in either file.

**Instrument list, unchanged:** [`../DC2/DC2_instruments.md`](../DC2/DC2_instruments.md) §1 as it stands,
**56 instruments** (G01–G16, U01–U03, E01–E11, Q01–Q09, V01–V14, X01–X03).

## 2. What changes: rules DC2R-1 … DC2R-4 (as the brief §3 states them)

- **DC2R-1. Row granularity by deciding status.**
  - For a **non-deciding** quantity (flicker, rapid voltage change, harmonics, power factor, ride-through, hold-up,
    other): **one row per clause**. A table of limits is one row, whatever its categories; a ride-through curve or
    table is one row; the categories are listed in `category` separated by `;`, and `limit` carries the range or the
    table's values as printed. The window and allowance classes are those of the table's **most restrictive** entry
    (the shortest window; the smallest allowance), with the spread noted in `note`.
  - For a **deciding** quantity (ramp rate, step change, swing amplitude, smoothing or capping response, load change
    per interval): **one row per printed table row or clause paragraph**, exactly as DC2's raters both did for the
    Fingrid oscillation bands; `category` carries the printed row label.
  - `deciding` follows `quantity` by the DC2 §2 list; a rater does not decide it independently.
- **DC2R-2. Supply-capability envelopes are `other`.** A requirement on what a power shelf, PSU, BBU or rack supply
  must deliver under a load step — output-voltage transient limits, peak or pulse power envelopes with moving-average
  windows, step-load capability tables, inrush — limits the supply, not the load's power toward the facility or the
  grid. It is `quantity = other`, non-deciding, one row per clause. A requirement that limits **the load's** power
  variation at the rack or shelf (if any instrument states one) stays in the deciding set.
- **DC2R-3. Planning-level step tables are deciding rows.** A table of permitted step changes or rapid power changes
  for a connecting installation (as in the D-A-CH-CZ Part B tables) is `quantity = step change`, one row per printed
  table row, window and allowance as printed (`not stated` where the text states none).
- **DC2R-4. Approved text awaiting implementation.** A clause the body has adopted (approved by its board or
  commission) but printed as awaiting system implementation or a later effective date is **in force for this audit**,
  with `note = awaiting implementation` and `confidence ≤ medium`. A draft, consultation text or unadopted proposal
  stays pending (DC2 §1). This makes explicit the convention both DC2 raters applied.

Nothing else changes. The gates, the shape table, the deciding list, the decision table and the consequence line are
DC2's.

