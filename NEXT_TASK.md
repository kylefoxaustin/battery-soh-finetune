# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-11-11 (late). **Owner of this file:** the reviewer. The running session only *reads* it, except for
the Status line.

**Previous task — L1b stage 1: APPROVED at `7c3896c`** with deviation L1B-D1, written into
[`results/L1B/L1B_preregistration.md` §10](results/L1B/L1B_preregistration.md). Read §10 first.

## Do these steps, in order (L1b stage 2, straight through)

1. `git pull` on `main`. Read `results/L1B/L1B_preregistration.md` in full, §10 included.
2. **Analysis first.** Write `analysis/L1B_agreement.py` and commit it on `main` **before any rater branch exists**:
   L1's script extended — domains S and L; matching (L-4) within `instrument_id`; the three gates (identification over
   S + L seeds; κ on the four classes over matched S + L pairs; κ on `stack` over matched S + L pairs plus the 51
   `stack_B` rows joined on `act_id` + `domain`); the calibration readout against L1's committed files (N_S1 and E_S1
   computed by L1's functions, never typed in); N_L, N_S, R_BL, R_BS with intervals; V1, V0, FULL, CN0, ACC; per-year
   tables; classes with CIs; the stack readouts (specific events, conservative `yes`, judged denominators, shares with
   Wilson CIs, vehicle-level stack counts per domain, one-sided Fisher B vs L); both decision tables **with L1B-D1**
   (share clause only when n_L ≥ 10) and the access qualifier (L: ≥ 8 of 22 seeds `none`); every unmatched event, class
   disagreement and stack disagreement listed; `results/L1B/l1b.json`. Run it on small synthetic ledgers you write
   yourself (commit them under `analysis/L1B_selftest/`) that exercise calibration pass / fail, both verdict tables,
   L1B-D1 and the access branch; then commit.
3. **Launch prompt.** `results/L1B/L1B_rater_prompt.md` = `results/L1/L1_rater_prompt.md` with mechanical
   substitutions plus the `stack` and `stack_B` instructions of the pre-registration §3–§4; commit it **with its diff
   against L1's prompt** (`L1B_rater_prompt.diff`) on `main`. It names the five clone files and nothing about any
   instrument's content, event, count or expected direction.
4. **Rater A** on `l1b-rater-a`: a new fresh-context sub-agent in a sparse clone of `main` containing exactly
   `results/L1/L1_preregistration.md`, `results/L1B/L1B_preregistration.md`, `results/L1B/L1B_instruments.md`,
   `results/L1B/L1B_orders.json`, `results/L1B/B_events.csv`; conventions committed before any change history is read;
   order A for S and L, then the `stack_B` rows in `B_events.csv` order. Outputs `ledger_A.csv`, `stack_B_A.csv`,
   `instruments_A.csv`, `rater_A_notes.md`; push. Do not read them.
5. **Rater B** the same on `l1b-rater-b` with order B, launched after A's branch is pushed, never fetching it; push.
6. **Merge** both branches, run the script, write `results/L1B/results_L1B.md`: both verdict lines first (count and
   kind) with the calibration result and the consequences stated beside them; the gates with the D-3 disclosure; the
   per-year tables; the stack table per domain; the sensitivities; the access table; every disagreement; the §8
   exposure disclosure repeated. Then `l1b.json`, the index rows (`results/X/README.md`, `results/RESEARCH_DOSSIER.md`),
   and dated notes under ANGLES §B.1, SYNTHESIS §1 / §3 and POSITION §1 (numbers from `l1b.json`; POSITION's first
   sentence is rewritten only if the kind verdict says so, and then by the reviewer).
7. Any departure after a rater has read a change history is a numbered deviation L1B-D2, … in `results_L1B.md`; none
   of the §9 items may move.
8. Set the Status line below to `AWAITING APPROVAL <commit-hash>`, push, and stop.

## Rules that always apply
- No bypassing; `none` is a recorded result. Sources are the publishing body's own texts or summaries.
- Two blind raters, fresh contexts, sparse clones with the five files only; the analysis script is committed before
  either branch exists; the three gates, or UNGATED; disagreements reported, never reconciled.
- Every event SOURCED; every class and every `stack` value DERIVED-judgemental; both raters are language-model
  sessions and the write-up says so. No dollar figures.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `AWAITING APPROVAL <commit-hash>` or `BLOCKED: <one-line reason>`, then commit
and push.

**Status:** AWAITING APPROVAL b0226dd (L1b done: UNGATED on count and kind — identification 0.60, κ classes 0.38, κ stack 1.00; calibrated; not access-limited; ungated R_BL 0.73, stack B 16/27 vs L 0/40; script 857134e before either branch; raters l1b-rater-a 4afe7a7, l1b-rater-b b8ad69d; no L1B-D2)
