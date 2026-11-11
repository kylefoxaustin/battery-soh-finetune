# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-11-11 (afternoon, later). **Owner of this file:** the reviewer. The running session only *reads* it,
except for the Status line.

**Previous task — DC2-R stage 1: APPROVED at `47ae9f6`** with deviation DC2R-D1 and the clone-contents decision,
written into [`results/DC2R/DC2R_preregistration.md` §9](results/DC2R/DC2R_preregistration.md). Read §9 first.

## Do these steps, in order (DC2-R stage 2, straight through)

1. `git pull` on `main`. Read `results/DC2R/DC2R_preregistration.md` in full, §9 included.
2. **Rules file.** Write `results/DC2R/DC2R_rater_rules.md` = the pre-registration's §1 and §2 verbatim (nothing
   else; no mention of DC2's rows, results or any clause). Commit on `main`.
3. **Analysis first.** Write `analysis/DC2R_agreement.py` (DC2's script with DC2R-1 … DC2R-4 and **DC2R-D1**: pass 1
   on clause + quantity for non-deciding rows, clause + category for deciding rows; pass 2 unchanged) and commit it on
   `main` **before any rater branch exists**. Re-run the DC2 self-tests s1–s5 under the new matching and add one
   (s6) that exercises DC2R-D1 (two raters listing the same non-deciding table with categories in different words,
   which must pass-1 match) and DC2R-1's most-restrictive-entry shape. Commit `analysis/DC2R_selftest/`.
4. **Launch prompt.** `results/DC2R/DC2R_rater_prompt.md` = `results/DC2/DC2_rater_prompt.md` with mechanical
   substitutions only (paths, branch and file names; the clone's four files; one paragraph pointing to DC2R-1 … DC2R-4
   in the rules file). Commit it **with its diff against DC2's prompt** (`DC2R_rater_prompt.diff`) on `main`.
5. **Rater A** on `dc2r-rater-a`: a new fresh-context sub-agent in a sparse clone of `main` containing exactly
   `results/DC2/DC2_preregistration.md`, `results/DC2/DC2_instruments.md`, `results/DC2R/DC2R_orders.json`,
   `results/DC2R/DC2R_rater_rules.md`; conventions committed before any requirement text is read; order A. Outputs
   `results/DC2R/requirements_A.csv`, `instruments_A.csv`, `rater_A_notes.md`; push. Do not read them.
6. **Rater B** the same on `dc2r-rater-b` with order B, launched after A's branch is pushed, never fetching it; push.
7. **Merge** both branches, run the script, write `results/DC2R/results_DC2R.md`: verdict line first with the
   consequence line and **whether DC1b follows** (pre-registration §4); the gates with the D-3 disclosure; the
   `cmp` of the rules file against §1–§2; the binding-deciding table; the per-body fastest window; the vendor and
   power-quality rows; sensitivities; access table; every disagreement; the §7 exposure disclosure repeated. Then
   `dc2r.json`, the index rows (`results/X/README.md`, `results/RESEARCH_DOSSIER.md`), dated notes under ANGLES §B.2
   and SYNTHESIS §1 / §5.
8. Any departure after a rater has read requirement text is a numbered deviation DC2R-D2, … in `results_DC2R.md`;
   none of the §6 items may move.
9. Set the Status line below to `AWAITING APPROVAL <commit-hash>`, push, and stop. **Do not start DC1b.**

## Rules that always apply
- No bypassing; `none` is a recorded result. Sources are the publishing body's own pages.
- Two blind raters, fresh contexts, sparse clones with the four files only; κ ≥ 0.6 on the window class (over M₁)
  and ≥ 80 % identification agreement, or UNGATED; disagreements reported, never reconciled.
- Every requirement SOURCED; every class DERIVED-judgemental; both raters are language-model sessions and the
  write-up says so. No dollar figures.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `AWAITING APPROVAL <commit-hash>` or `BLOCKED: <one-line reason>`, then commit
and push.

**Status:** AWAITING APPROVAL 5883669 (DC2-R: UNGATED, identification 0.72 < 0.80 on coverage and quantity naming; kappa(window) 1.00; deciding rows 0.81, every class agreed; DC1b not run, leg closes on DC2-R; exploratory: ERCOT §6.5.7.11 again the only history-shaped binding clause)
