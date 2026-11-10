# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-11-10. **Owner of this file:** the reviewer. The running session only *reads* it, except for the
Status line.

**Previous task — X8: DONE at `f5296cb`, reviewed and accepted** (NOT INTERPRETABLE on all three arms; every headline
re-derived from the JSON by the reviewer). Where the programme stands after X7, B1, DC1, FR1 and X8 is written up in
[`results/OPEN_PROBLEM/SYNTHESIS.md`](results/OPEN_PROBLEM/SYNTHESIS.md). Plan:
[`briefs/NEXT_EXPERIMENTS/README.md`](briefs/NEXT_EXPERIMENTS/README.md) (order now FR1-R → L1 → DC2 → O1 → R1).

## Do these steps, in order

1. `git pull` on `main`.
2. Open [`briefs/FR1R/README.md`](briefs/FR1R/README.md) and follow its START HERE box. **First stage only:** write
   `results/FR1R/FR1R_preregistration.md` (the six-state scheme and closed rate list of brief §3, every threshold of §4
   filled in, the case list carried over unchanged, the rating orders, the branch names). **Do not open any FR1 rating,
   notes, results or review file** (`results/FR1/ratings_*.csv`, `rater_*_notes.md`, `results_FR1.md`, `fr1.json`,
   `review/`); the FR1 manifests may be read only by a script, for URLs and hashes.
3. Commit with "before rating" in the commit message.
4. Set the Status line below to `AWAITING APPROVAL <commit-hash>`, push, and stop.

## Rules that always apply
- The case list, the six states, the rate classes and the decision thresholds never move after rating starts.
- Two raters, blind to each other and to FR1's ratings, on branches `fr1r-rater-a` and `fr1r-rater-b`; κ ≥ 0.6 or
  UNGATED; disagreements reported, never reconciled; both raters are language-model sessions and the write-up says so.
- Every rating is DERIVED-judgemental; source NHTSA, public domain. No dollar figures.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `AWAITING APPROVAL <commit-hash>` or `BLOCKED: <one-line reason>`, then commit
and push.

**Status:** AWAITING APPROVAL 2541d02 (FR1-R pre-registration; both raters proposed as fresh sub-agents in sparse clones, §4)
