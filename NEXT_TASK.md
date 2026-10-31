# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-10-31. **Owner of this file:** the reviewer. The running session only *reads* it, except for the
Status line.

**FR1 first stage (`765d1f1`) is APPROVED with reviewer deviations D-1 to D-3** (see
[`briefs/FR1/README.md`](briefs/FR1/README.md) APPROVED box and `results/FR1/FR1_preregistration.md` §8). Plan:
[`briefs/NEXT_EXPERIMENTS/README.md`](briefs/NEXT_EXPERIMENTS/README.md). X8 ([`briefs/X8/README.md`](briefs/X8/README.md))
is next after FR1.

## Do these steps, in order (this session is **Rater A**)

1. `git pull` on `main`. Read the APPROVED box in `briefs/FR1/README.md` and §8 of the pre-registration.
2. Create branch `fr1-rater-a` from `main`. Rate every PE case (PE001–PE005, PE007–PE076) and every BR case from its
   Part 573 Safety Recall Report (plus the ODI résumé only where pre-registration §4.1 allows), in the
   `numpy.random.default_rng(1)` order, using the closed lists in pre-registration §3. Record *cannot judge* where a
   document cannot be opened. No TSBs, press, papers or memory of a case.
3. Write `results/FR1/ratings_A.csv` (one row per case: items 1–5 plus the free-text signals and rate). Commit and push
   **the branch only**. Do not merge to `main`. Do not write or run any agreement analysis.
4. Set the Status line below (on `main`) to `RATER A DONE <branch-hash>`, mirror it in the FR1 brief's Status line,
   push, and stop.

The reviewer will then start a fresh session as **Rater B** (branch `fr1-rater-b`, blind to yours), and after both
branches exist a session merges them and runs the pre-registered agreement analysis.

## Rules that always apply
- Rate from the cited documents only. Every rating is DERIVED-judgemental and says so.
- Nothing in the case list, categories, thresholds or decision table moves. Any change is a numbered deviation (D-4, …).
- The κ gate (≥ 0.6) and the conservative reading decide; disagreements are reported, never reconciled.
- Carry the source (NHTSA, public domain) on every table. No dollar figures.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `RATER A DONE <branch-hash>` or `BLOCKED: <one-line reason>`, then commit and
push `main`.

**Status:** RATER A DONE f736331
