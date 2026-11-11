# Build Brief — DC2-R: the ramp-spec audit re-rated with row granularity fixed in advance; DC1b declared as its follow-on

**Licence of this document:** public domain (CC0). **Written:** 2026-11-11. **Origin:** DC2 results §6.3 and the
reviewer's acceptance ([`results/DC2/review/README.md`](../../results/DC2/review/README.md)); SYNTHESIS §5. Same 56
instruments, same two-rater two-branch procedure as [`briefs/DC2/README.md`](../DC2/README.md); only the counting
conventions change, and the follow-on is declared now so that nothing after the verdict is chosen with the verdict in
hand.

> ## ▶ START HERE (first stage: pre-registration only, then STOP)
>
> 1. `git pull` on `main`.
> 2. Read this brief, `results/DC2/DC2_preregistration.md` (§1–§10: everything here is reused unless §3 below names
>    it), and `results/DC2/review/README.md`. **Do not open** `results/DC2/requirements_A.csv`, `requirements_B.csv`,
>    `rater_A_notes.md`, `rater_B_notes.md`, `results_DC2.md`, `dc2.json` or `dc2_selftest/` in the session that will
>    launch the raters, and never in a rater: a rater primed by the DC2 rows is not blind. (The reviewer has read them;
>    the reviewer is not a rater.)
> 3. **Stage 1.** Write `results/DC2R/DC2R_preregistration.md`: the DC2 pre-registration carried over by reference,
>    with §3 below written out as rules DC2R-1 … DC2R-4, every threshold unchanged, the instrument list unchanged
>    (`results/DC2/DC2_instruments.md`, 56 instruments), the rating orders (`default_rng(41)` for rater A,
>    `default_rng(42)` for rater B), the branch names `dc2r-rater-a` / `dc2r-rater-b`, and the §4 follow-on declaration.
>    Commit with "before rating" in the message; set the Status line in `NEXT_TASK.md` to `AWAITING APPROVAL <hash>`;
>    push; stop.
>
> The reviewer approves by editing this box. Then `analysis/DC2R_agreement.py` (DC2's script with DC2R-1 … DC2R-4;
> self-tests re-run) is committed before either rater branch exists; rater A, then rater B, as fresh-context sub-agents
> in sparse clones; the analysis runs only after both branches exist.

---

## 0. Why

DC2 failed its identification gate (0.52 against 0.80) for one reason: the pre-registration said "one clause, one row;
a table of limits by category is one row per category", and the two raters read "category" differently on quantities
that do not decide — rater A wrote one row per harmonic formula and per ride-through curve point, rater B one row per
table. Sixty-seven of A's seventy-seven unmatched rows are those. On the sixteen pairs that decide, the raters agreed on
every class; on the one history-shaped clause they agreed on every field. The scheme, not the reading, failed the gate.
DC2-R fixes the scheme and keeps everything else, so that the data-centre anticipation leg ends on a gated verdict
rather than on a reviewer's reading.

## 1. Rules (DC2 §1, plus)

- Fresh raters: neither DC2 rater, nor the DC2 screener, nor any session that has read a DC2 rating file, is a DC2-R
  rater. The launching session's own exposure is disclosed in the pre-registration.
- Nothing in §3 is chosen with a verdict in hand: the rules below fix granularity and two classifications that DC2's
  raters resolved differently at reading time; they do not touch the shape table, the deciding set, the gates or the
  decision table.

## 2. What is reused unchanged

The DC2 pre-registration §1 (scope in time; pending rule), §2 (definitions, classes, rate-unit rule, `hard` default,
shape table), §3 S4 (routes, no bypassing), §4 (columns), §5 (matching, gates, conservative reading, readouts,
sensitivities), §6 (decision table, access qualifier, consequence line), §7 (raters and blindness), §10 (DC2-1,
DC2-2). The instrument list is `results/DC2/DC2_instruments.md` as it stands (56).

## 3. What changes (write these out as DC2R-1 … DC2R-4)

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

Nothing else changes. The gates, the shape table, the decision table and the consequence line are DC2's.

## 4. Follow-on declared now: DC1b

The DC2 §6 consequence line says that HISTORY-SHAPED SPEC EXISTS "names the spec (window, allowance, measurement point)
for a pre-registered DC1b re-run". So that this is not chosen after the fact:

- **If DC2-R returns HISTORY-SHAPED SPEC EXISTS**, DC1b is run next: DC1's pre-registered machinery
  (`analysis/DC1_storage.py`, `DC1_sim.c`, the NLR traces, the same controllers K0 / K1 / K1-r / K∞, the same folds and
  bootstrap), with the **spec replaced by the named clause** — the ramp limit applied to **one-minute averages** of the
  held power, the band as printed (the up-ramp cap, and the down-ramp band, in % per minute of the trace's
  P_max − P_min as the stand-in for MPC − LPC), the violation budget **10 % of one-minute intervals** — on the **whole
  trace** (DC1's primary used the active segment because job start and end are not forecastable from 30 s of power
  history; a one-minute-average ramp limit is bound by exactly those transitions, so the whole trace is the primary
  here and the active segment the sensitivity). DC1's verdict table and memory readout (D-2) are reused unchanged.
  DC1b gets its own brief and pre-registration after DC2-R's verdict is in; the lines above are its fixed points.
- **If DC2-R returns NO HISTORY-SHAPED SPEC, UNCLEAR or UNGATED**, DC1b is not run and the leg closes on DC2-R.
- A different clause than ERCOT §6.5.7.11 landing as the history-shaped one would be a finding in itself; DC1b then
  takes that clause's window and allowance.

## 5. Deliverables

Stage 1: `results/DC2R/DC2R_preregistration.md` (+ `DC2R_orders.json`).
Stage 2: `analysis/DC2R_agreement.py` (self-tests re-run and committed before either rater branch); the rater prompt;
`requirements_<A|B>.csv`, `instruments_<A|B>.csv`, `rater_<A|B>_notes.md` on `dc2r-rater-a` / `dc2r-rater-b`; then
`results/DC2R/results_DC2R.md` (verdict first, with the consequence line and whether DC1b follows), `dc2r.json`, index
rows, dated notes under ANGLES §B.2 and SYNTHESIS §1 / §5.

## 6. What not to do

- Do not reuse DC2's rows, and do not let a rater see them.
- Do not change the shape table, the deciding list, a threshold or the consequence line.
- Do not add or remove an instrument.
- Do not start DC1b before DC2-R's verdict is accepted by the reviewer.

---

*Fix the granularity. Rate it twice, fresh. Let the table decide. Then run the spec it names through DC1's model.*
