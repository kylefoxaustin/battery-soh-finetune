# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-10-31. **Owner of this file:** the reviewer. The running session only *reads* it, except for the
Status line.

**Previous task — DC1: DONE at `cf94244`, reviewed and accepted** (REACTIVE SUFFICES on both workloads; NO HISTORY
NEEDED; [`results/DC1/results_DC1.md`](results/DC1/results_DC1.md)). Plan and reading:
[`briefs/NEXT_EXPERIMENTS/README.md`](briefs/NEXT_EXPERIMENTS/README.md) (order now FR1 → X8 → O1 → R1; X8 has a full
Build Brief at [`briefs/X8/README.md`](briefs/X8/README.md) and is next after this task).

## Do these steps, in order

1. `git pull` on `main`.
2. Open [`briefs/FR1/README.md`](briefs/FR1/README.md) and follow its START HERE box. **First stage only:** fix the
   search terms, inclusion criteria and the rating scheme (brief §3), run the search, and write
   `results/FR1/FR1_cases.md` (the case list with sources and **no** root-cause or remedy text) and
   `results/FR1/FR1_preregistration.md`. Then STOP.
3. Commit both with "before rating" in the commit message. **Do not read or record any remedy or root-cause text in this
   stage.** Inclusion is decided from component and symptom fields only.
4. Set the Status line below to `AWAITING APPROVAL <commit-hash>` (and mirror it in the FR1 brief's own Status line),
   push, and stop. The reviewer approves by editing the brief's START HERE box to "APPROVED, rate now".

## Rules that always apply
- The case list is fixed blind, before any root-cause text is read. That rule is what makes the ratings mean anything.
- Pre-register the rating categories and the window thresholds (≤ 1 s · 1–40 s · 40–80 s · 80–700 s · > 700 s) before
  rating; the tier line is 80 s and B1's measured window is 671 s.
- Two raters, blind to each other; κ ≥ 0.6 or the study is UNGATED. Disagreements are reported, never reconciled.
- Every rating is DERIVED-judgemental and says so. Carry the source (NHTSA public domain; check Safety Gate terms).
- No dollar figures.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `AWAITING APPROVAL <commit-hash>` or `BLOCKED: <one-line reason>`, then commit
and push.

**Status:** AWAITING APPROVAL 765d1f1
