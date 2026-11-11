# DC2-R pre-registration: the ramp-spec audit re-rated with row granularity fixed in advance

**Question.** DC2's question, unchanged ([`../DC2/DC2_preregistration.md`](../DC2/DC2_preregistration.md), opening
lines): does any binding public requirement on a large load's real-power variation have the window-and-allowance shape
in which DC1 found history to pay (a 1–60 s window with ~0.5 % or more of intervals allowed to exceed)?

**Status of this file.**
- Brief: [`briefs/DC2R/README.md`](../../briefs/DC2R/README.md). Requested by NEXT_TASK (reviewer, 2026-11-11,
  afternoon), stage 1.
- Committed **before rating**, before `analysis/DC2R_agreement.py` exists, and before either DC2-R rater branch
  exists.
- DC2 failed its identification gate (0.52 < 0.80) on row granularity of non-deciding rows (reviewer acceptance,
  [`../DC2/review/README.md`](../DC2/review/README.md)). DC2-R changes only the counting conventions (§2 below).

**Tags.** As DC2: every requirement **SOURCED**, every class **DERIVED-judgemental**, both raters are language-model
sessions and the write-up says so beside κ (D-3). No dollar figures.

---

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

## 3. Raters, orders, branches

- **Branches:** rater A on **`dc2r-rater-a`**, rater B on **`dc2r-rater-b`**.
- **Fresh raters (brief §1):** neither DC2 rater, nor the DC2 screener, nor any session that has read a DC2 rating
  file is a DC2-R rater. Each rater is a new fresh-context sub-agent.
- **Orders:** [`DC2R_orders.json`](DC2R_orders.json), written by
  [`analysis/DC2R_orders.py`](../../analysis/DC2R_orders.py) (DC2's orders script with the seeds and output path
  changed): the 56 instrument IDs sorted, then permuted by `numpy.random.default_rng(41)` (A) and
  `default_rng(42)` (B). Both orders cover the same 56 IDs as DC2's; neither equals a DC2 order.
- **No DC2 rating file in a rater's clone,** and no rater reads one (`results/DC2/requirements_*.csv`,
  `instruments_*.csv`, `rater_*_notes.md`, `results_DC2.md`, `dc2.json`, `analysis/DC2_selftest/`, `results/DC2/review/`).

## 4. Follow-on declared now: DC1b (the brief §4, copied)

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

## 5. Outputs and order (brief §5)

**Stage 1 (this commit):** this file; `DC2R_orders.json`; `analysis/DC2R_orders.py`.

**Stage 2, after approval, in this order:**
1. `analysis/DC2R_agreement.py` (DC2's script with DC2R-1 … DC2R-4; self-tests re-run), committed on `main` before
   either rater branch exists;
2. the rater launch prompt, committed before rater A starts;
3. rater A, then rater B, on their branches;
4. `results_DC2R.md` (verdict first, the consequence line, and whether DC1b follows), `dc2r.json`, index rows, dated
   notes under ANGLES §B.2 and SYNTHESIS §1 / §5.

## 6. Deviations

Any change after this commit is a numbered deviation (DC2R-D1, …). After any requirement text has been read by a
DC2-R rater, none of these moves: the instrument list, the access rules, the definitions and classes (with DC2R-1 …
DC2R-4), the matching rule, the gates, the decision table, the DC1b fixed points of §4.

## 7. Disclosure: what the launching session has read

**This session is the one that launched and analysed DC2.** It wrote `analysis/DC2_agreement.py` and its self-tests,
merged and read both DC2 rater files (`requirements_A.csv`, `requirements_B.csv`, `instruments_*.csv`,
`rater_*_notes.md`), and wrote `results_DC2.md` and `dc2.json`. It cannot un-read them. The brief's "do not open" step
therefore cannot be met by this session; it is disclosed here instead (brief §1: "the launching session's own exposure
is disclosed"). The session knows DC2's per-instrument rows, the 16 binding deciding pairs and the ERCOT §6.5.7.11 pair.

**What that exposure can and cannot reach.**
- It cannot reach the rows: raters are fresh sub-agents that never see a DC2 rating file (§3), read the instruments
  themselves, and write their own files.
- It can reach the raters only through the launch prompt and the clone contents. Proposed mitigation, binding unless
  the reviewer changes it:
  - the DC2-R launch prompt is DC2's committed prompt ([`../DC2/DC2_rater_prompt.md`](../DC2/DC2_rater_prompt.md))
    with mechanical substitutions only (`DC2` → `DC2R` in paths, branch names and file names; the clone's file list)
    plus one paragraph pointing to DC2R-1 … DC2R-4 by name; its diff against DC2's prompt is committed with it, so the
    reviewer can see that nothing about content, instruments or expected results was added;
  - the prompt names no instrument, clause, limit, hypothesis or expected verdict.

## 8. For the reviewer, before stage 2 (no change made here)

1. **Clone contents and §4.** DC2's raters had the brief and the pre-registration in their clones. DC2-R's brief
   (§0, §3, §4) and this file's §4 name ERCOT §6.5.7.11, the expected verdict, and DC2's agreed classes on the deciding
   pairs (Fingrid bands, D-A-CH-CZ step tables, OCP envelopes). A rater who reads them is told where the
   history-shaped clause is and how DC2 read it. **Proposed:** the rater clone contains `DC2_preregistration.md`,
   `DC2_instruments.md`, `DC2R_orders.json` and a rater-rules file `results/DC2R/DC2R_rater_rules.md` that carries §1
   and §2 of this file verbatim and nothing else; it does **not** contain `briefs/DC2R/README.md` or this file. The
   rules file would be committed on `main` with the analysis script, before either branch, and checked identical to
   §1–§2 here by `cmp` of the extracted text. If the reviewer prefers DC2's arrangement (brief + pre-registration in the
   clone), the exposure is disclosed in the results instead.
2. **Matching on `;` category lists.** Under DC2R-1 a non-deciding table is one row with its categories listed in
   `category`. DC2 §5 pass 1 compares normalised clause **and** category, so two raters who list the same categories in
   different words or order will not match in pass 1; they fall to pass 2 (same quantity + window class), which DC2R-1's
   most-restrictive-entry rule makes likely to match. The effect is on M₁ (the κ(window) base), not on identification.
   The matching rule is unchanged here, as the brief requires; the agreement script will apply it as written.

---

## 9. Reviewer approval and deviation DC2R-D1 (2026-11-11, before rating)

Stage 1 (`47ae9f6`) is **approved**. The reviewer checked: §2 carries DC2R-1 … DC2R-4 verbatim from the brief; the
thresholds, shape table, deciding list, decision table and consequence line are DC2's; the instrument list is the 56
of DC2; the orders reproduce from `default_rng(41)` / `default_rng(42)` over the same 56 IDs and equal neither DC2
order; the §4 DC1b fixed points are copied; the launching session's exposure is disclosed (§7). The two points of §8 are
decided as follows.

**§8.1 — clone contents: the session's proposal is adopted, and extended.** The rater clone contains exactly four
files: `results/DC2/DC2_preregistration.md`, `results/DC2/DC2_instruments.md`, `results/DC2R/DC2R_orders.json` and
`results/DC2R/DC2R_rater_rules.md` (this file's §1 and §2 verbatim, nothing else). It contains **no brief** — not
`briefs/DC2R/README.md` and not `briefs/DC2/README.md`, whose DONE box names the DC2 result — and not this file. The
rules file is committed on `main` with the analysis script, before either branch, and the results report the `cmp`
of its text against §1–§2 here. The launch prompt names the four files and nothing about content, instruments or
expected results (the §7 mitigation: DC2's prompt with mechanical substitutions, its diff committed).

**§8.2 — DC2R-D1, matching for one-row-per-clause rows.** DC2R-1 makes `category` descriptive rather than
identifying for non-deciding rows, so pass 1 is restated by deciding status, before any reading:

- **non-deciding rows** (quantity not in the deciding list): pass 1 matches on identical normalised `clause` **and
  identical `quantity`** — `category` is ignored;
- **deciding rows**: pass 1 matches on identical normalised `clause` and `category`, as DC2 §5;
- pass 2 (same `quantity` and `window_class`, in file order) is unchanged for the remainder;
- a pair whose two rows have different `deciding` values (possible only through a quantity disagreement) can form
  only in pass 2.

This changes which pairs count as M₁ (the κ(window) base), not the identification formula, the gates or the
thresholds. It is recorded as DC2R-D1 and implemented in `analysis/DC2R_agreement.py` with a self-test that
exercises it.

**Stage 2 runs straight through** to `AWAITING APPROVAL` on the results; no further approval stop. DC1b, if the
verdict calls for it, waits for the reviewer's acceptance of DC2-R (brief §6).
