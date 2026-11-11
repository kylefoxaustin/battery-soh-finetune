# DC2 — reviewer acceptance (2026-11-11)

**Accepted at `af74b0e` as UNGATED.** Every number in `results_DC2.md` §1–§3 and §5 was re-derived from
`requirements_A.csv`, `requirements_B.csv`, `instruments_A.csv` and `instruments_B.csv` with the reviewer's own code
(`reviewer_check.py`, output `reviewer_check.out`), which reads nothing the session's script wrote. Exact agreement on:
n_A 204, n_B 166, M 127 = 113 (clause + category) + 14 (quantity + window), identification 0.523, κ(window, M₁) 0.644
(observed 0.708), κ(window, all M) 0.681, κ(allowance) 0.707, κ(computed shape) 0.569, κ(binding) 1.000, κ(deciding)
0.741, the seven field-disagreement counts, the unmatched rows by quantity (A 77: harmonics 41, ride-through 26, other
9, hold-up 1; B 39, of which 16 deciding), the access table (40 full / full, 10 partial / partial, 0 none; not
access-limited), the status counts (28 / 20 / 8, both raters), the 16 binding-deciding pairs from 3 instruments with
their conservative shapes (reactive 11, history 2, cannot judge 2, electronics 1), STATED / ANY / SEED (16 from 3; 20
from 5; 2 from 1), the two history pairs (A109 / B104, A110 / B105, both ERCOT §6.5.7.11), the four either-rater
history rows, each rater's own binding-deciding rows (A 16 from 3; B 31 from 10), and the exploratory deciding-row
identification 25 / 41 = 0.61. Every rater-written shape equals the shape computed from its own window and allowance
classes (0 mismatches, both files). The only counts that differ are definitional and reconcile exactly: the session's
"non-deciding pairs 102" excludes the 9 OCP-envelope pairs on which the raters disagree about `deciding`; the
reviewer's 111 includes them.

**Process checks.** `analysis/DC2_agreement.py` was committed (`aad23bd`) before the launch prompt and before either
rater branch, and never touched again; the four rater files were not touched after the merges. Each rater committed
its conventions before reading (`2277855`, `8d22807`); rater B started 18 minutes after rater A's final commit and
its notes record no fetch of `dc2-rater-a`. The launch prompt names no hypothesis, tier or expected direction. Both
raters applied the pending rule the same way (8 pending, identical lists), read the same 10 seeds as abstract-only, and
disagree on status for exactly two instruments (E08, V11), both disclosed. The `verdict_line` display artefact (§1 of
the results) is a cosmetic defect of the script, disclosed, and does not touch the `verdict` field.

**Why UNGATED is the right reading, and why a re-run is not scheduled.** The gate failure is row granularity on
quantities that do not decide: 67 of A's 77 unmatched rows are harmonics formulas and ride-through curve points that B
wrote as one row per table. On the rows that decide, the two raters agree on window and allowance class for all 16
matched pairs and on the single history-shaped clause. A DC2-R with a one-row-per-table convention fixed in the
pre-registration (the lesson recorded in §6.3 of the results) would very probably gate and would return
**HISTORY-SHAPED SPEC EXISTS on ERCOT §6.5.7.11 alone** — a formally positive verdict that the pre-registered
consequence line would turn into a DC1b, and that the clause itself does not support:

- it is a Provisional Controllable Load Resource rule: the down-ramp band is a *minimum* curtailment speed (at least
  10 % per minute) with a cap at 20 %, judged on telemetered one-minute averages, ≥ 90 % of a month's eligible
  intervals — a dispatch-following performance test for loads that volunteer to be curtailable, not a limit on
  self-initiated power swings;
- a one-minute average of a 0.2–3 Hz training swing is nearly constant, so the clause does not see the oscillation
  DC1 modelled at all; the ramps it does see are job starts and stops, which are scheduler events, not something 30 s
  of power history foresees;
- it is gray-boxed (approved, awaiting system implementation) and sits on the inclusive 60 s edge of the class.

So the honest state of the data-centre anticipation leg, after DC1 and DC2, is: **no public specification was found
whose window and allowance have the shape in which DC1 found seconds of history to pay at the rack.** The binding
limits on real-power variation that either rater found at any level are hard limits — Fingrid's oscillation-amplitude
bands by frequency (0.01–45 Hz) and ramp / step limits at the POI, AESO's ramp and step limits at the POI, OCP's
sub-100 ms supply envelopes at the shelf — which are DC1's primary regime (reactive) or the converter's own bandwidth
(electronics). This is stated as a documentary reading with the gate failure beside it, not as a verdict. The reviewer
does not schedule DC2-R; Kyle may ask for it if a gated line is wanted for a slide, at the cost of one session run.

**Design lessons recorded** (for `briefs/NEXT_EXPERIMENTS/README.md`): fix row granularity in the pre-registration
(one row per table for tables of limits; one row per curve for ride-through curves); define `deciding` for supply
envelopes (a limit on what the supply must deliver under a load step is not a limit on the load's power); define the
treatment of approved-but-unimplemented text explicitly rather than leaving it to a rater convention.
