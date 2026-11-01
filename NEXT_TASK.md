# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-11-01. **Owner of this file:** the reviewer. The running session only *reads* it, except for the
Status line.

**FR1 rater A is done** (branch `fr1-rater-a`, `f736331`; reviewed for process only: 150 rows, 75 PE + 75 BR, PE006 out,
PE076 in, documents manifested, conventions written before rating). **This session is Rater B.** It must stay blind to
rater A (pre-registration D-2).

## Blindness rules for this session — read before anything else
- Work from `main` only. Fetch only `main`: `git fetch origin main` (never a bare `git fetch`, never `git pull --all`).
  If `origin/fr1-rater-a` is already present in this clone, do not check it out, `git show` it, diff it or list its
  files.
- Do not open, search for or read any file whose name contains `rater_A` or `ratings_A`, anywhere, in any branch.
- Do not read `briefs/FR1/README.md` beyond its APPROVED box and the brief body; do not read any FR1 chat or notes you
  did not write.

## Do these steps, in order

1. `git fetch origin main && git checkout main && git reset --hard origin/main`. Read the APPROVED box in
   [`briefs/FR1/README.md`](briefs/FR1/README.md), then `results/FR1/FR1_preregistration.md` (all of it, including §8
   D-1 to D-3) and `results/FR1/FR1_cases.md`.
2. Create branch `fr1-rater-b` from `main`.
3. **Before opening any rating document,** write `results/FR1/rater_B_notes.md`: your own reading of pre-registration §3
   (how you will map what a document describes onto the five window categories; how you will set the flags). Commit it
   with "rater B conventions, before any document" in the message.
4. Fetch each case's documents per pre-registration §4.1 (the Part 573 Safety Recall Report and any chronology
   attachment; the ODI résumé only where §4.1 allows). Keep a manifest with URLs and SHA-256 as
   `results/FR1/rater_B_documents.json`. Nothing else is a rating source: no TSBs, press, papers or memory of a case.
5. Rate every PE case (PE001–PE005, PE007–PE076) and every BR case in the `numpy.random.default_rng(2)` order, using the
   closed lists in pre-registration §3; items 1–5 plus the free-text signals and rate; *cannot judge* where a document
   cannot be opened. Write `results/FR1/ratings_B.csv` with the columns
   `order, case, list, nhtsa_id, rating_documents, odi_resume, item1_cause_type, item2_evidence, item3_window,
   item3_signals_and_rate, item4_confidence, item5_no_cause_stated, item5_software_only, item5_component_out_of_scope,
   rater_note, rater, provenance, source` (rater = B; provenance = DERIVED-judgemental; source = NHTSA, public domain).
6. Commit and push **the branch only**. Do not merge to `main`. Do not write or run any agreement analysis.
7. Set the Status line below (on `main`) to `RATER B DONE <branch-hash>`, mirror it in the FR1 brief's Status line, push
   `main`, and stop.

After this, a session (any) merges `fr1-rater-a` and `fr1-rater-b` into `main` and runs the pre-registered agreement
analysis (pre-registration §5–§6). The reviewer may add the optional 15-case human spot-check (D-3) before that.

## Rules that always apply
- Rate from the cited documents only. Every rating is DERIVED-judgemental and says so.
- Nothing in the case list, categories, thresholds or decision table moves. Any change is a numbered deviation (D-4, …).
- Carry the source (NHTSA, public domain) on every table. No dollar figures.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `RATER B DONE <branch-hash>` or `BLOCKED: <one-line reason>`, then commit and
push `main`.

**Status:** OPEN (rater B)
