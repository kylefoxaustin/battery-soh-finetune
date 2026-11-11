# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-11-11 (afternoon). **Owner of this file:** the reviewer. The running session only *reads* it, except
for the Status line.

**Previous task — DC2: DONE at `af74b0e`, accepted as UNGATED** (row granularity; every number re-derived,
`results/DC2/review/`). Kyle chose to keep going: **DC2-R**, the same audit with granularity fixed in advance, with
**DC1b** declared as its follow-on. Brief: [`briefs/DC2R/README.md`](briefs/DC2R/README.md). Plan:
[`briefs/NEXT_EXPERIMENTS/README.md`](briefs/NEXT_EXPERIMENTS/README.md).

## Do these steps, in order (DC2-R stage 1: pre-registration only, then STOP)

1. `git pull` on `main`.
2. Open [`briefs/DC2R/README.md`](briefs/DC2R/README.md) and follow its START HERE box. **Do not open any DC2 rating
   file** (`results/DC2/requirements_*.csv`, `rater_*_notes.md`, `results_DC2.md`, `dc2.json`, `dc2_selftest/`) in
   the session that will launch the raters. Read `results/DC2/DC2_preregistration.md` and
   `results/DC2/review/README.md`.
3. Write `results/DC2R/DC2R_preregistration.md`: DC2's pre-registration carried over by reference; rules
   DC2R-1 … DC2R-4 written out exactly as the brief §3 states them; thresholds, gates, shape table, decision table and
   consequence line unchanged; the instrument list unchanged (56); orders `default_rng(41)` / `default_rng(42)` in
   `results/DC2R/DC2R_orders.json`; branches `dc2r-rater-a` / `dc2r-rater-b`; the brief §4 DC1b declaration copied in;
   and a disclosure of what the launching session has read.
4. Commit with "before rating" in the commit message; set the Status line below to `AWAITING APPROVAL <commit-hash>`;
   push; stop.

## Rules that always apply
- No bypassing; `none` is a recorded result. Sources are the publishing body's own pages.
- Two blind raters, fresh contexts, sparse clones; the analysis script is committed before either branch exists;
  κ ≥ 0.6 on the window class (over M₁) and ≥ 80 % identification agreement, or UNGATED; disagreements reported,
  never reconciled.
- Every requirement SOURCED; every class DERIVED-judgemental; both raters are language-model sessions and the
  write-up says so. No dollar figures.
- Do not start any experiment this file does not name. DC1b waits for the reviewer's acceptance of DC2-R.

## When you finish
Edit only the **Status** line below to `AWAITING APPROVAL <commit-hash>` or `BLOCKED: <one-line reason>`, then commit
and push.

**Status:** AWAITING APPROVAL 47ae9f6 (DC2-R stage 1: pre-registration before rating; launching-session exposure disclosed §7; two points for the reviewer §8: rater clone contents, pass-1 matching on `;` category lists)
