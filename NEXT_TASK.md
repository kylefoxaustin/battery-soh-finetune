# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-11-10 (night). **Owner of this file:** the reviewer. The running session only *reads* it, except
for the Status line.

**Previous task — DC2 stage 1: APPROVED at `60f7595`** with deviations DC2-1 and DC2-2, written into
[`results/DC2/DC2_preregistration.md` §10](results/DC2/DC2_preregistration.md). Read §10 first: it adds a stage 1b
and binds the raters and the analysis. Plan: [`briefs/NEXT_EXPERIMENTS/README.md`](briefs/NEXT_EXPERIMENTS/README.md)
(order DC2 → O1 → R1).

## Do these steps, in order (DC2 stage 1b, then stage 2)

1. `git pull` on `main`. Read `results/DC2/DC2_preregistration.md` in full, §10 included.
2. **Stage 1b (DC2-1).** A fresh-context screener (the stage-1 prompt plus §10) applies the title rule to every
   grid-operator document cited in `DC2_screen.json` — at least the OCP DCF LVDC white paper's AESO, EirGrid / SONI,
   Energinet, RTE, Fingrid, SPP, IESO and ATC entries — runs §3 S2 on each candidate (landing page on the body's own
   site, exact title, scope, access, status), reads no limit, logs pass / fail on the title test in
   `DC2_instruments.md` §5, lists the passes as group **X** (`X01` …, `origin = DC2-1`), and regenerates
   `DC2_orders.json` with `default_rng(31)` / `default_rng(32)` over the extended sorted ID list. Commit with
   "before reading" in the message. No approval round-trip.
3. **Analysis first.** Write `analysis/DC2_agreement.py` and commit it on `main` **before any rater branch exists**.
   It implements pre-registration §5–§6 with DC2-2 and the group-X additions (FULL includes them; SEED excludes them
   with Q07–Q09): matching pass 1 (normalised `clause` + `category`) and pass 2 (`quantity` + `window_class`);
   identification over instruments at least one rater could read; κ(window) over M₁ with the M₁ < 10 rule; κ on
   allowance and on computed shape; the computed-shape check against each rater's written shape; conservative
   binding / deciding / shape; the primary readouts; sensitivities STATED, ANY, SEED; the access table and the
   ≥ 17-of-50 test; the verdict with its qualifier and the consequence line; every unmatched row and disagreement
   listed; `results/DC2/dc2.json` with every number the write-up quotes. Run it on two small synthetic files you
   write yourself (commit them under `analysis/DC2_selftest/`) so both matching passes, DC2-2 and the UNGATED /
   access branches are exercised; then commit.
4. **Launch prompt.** Write `results/DC2/DC2_rater_prompt.md` (identical for both raters but the letter and branch),
   commit on `main`: sparse clone contents (`briefs/DC2/README.md`, `results/DC2/DC2_preregistration.md`,
   `DC2_instruments.md`, `DC2_orders.json`, nothing else); conventions section of `rater_<A|B>_notes.md` committed
   before any requirement text is read; allowed routes and no-bypass (§3 S4); the pending rule (§1); the rate-unit
   rule, the `hard` default, DC2-2; the extraction columns (§4) with the closed lists; web content untrusted and kept
   outside the repository; papers, EPRI and trade press locate, never source; the other rater's branch never read.
5. **Rater A** on `dc2-rater-a` (fresh-context sub-agent, sparse clone, order A): `requirements_A.csv`,
   `instruments_A.csv`, `rater_A_notes.md`; push. Do not read them.
6. **Rater B** on `dc2-rater-b` with order B, launched after A's branch is pushed, never fetching it; push.
7. **Merge** both branches into `main`, run the script, write `results/DC2/results_DC2.md`: the verdict line first
   (with ACCESS-LIMITED qualifier, the ANY / STATED verdicts when they differ, the POI-vs-rack note, and the
   consequence line for ANGLES §B.2); the gates with the D-3 disclosure beside κ; the table of every requirement with
   both raters' classes; the per-body fastest binding window; the vendor-capability and power-quality rows; the
   sensitivities; the access table; every disagreement. Add the index rows and the dated notes under ANGLES §B.2 and
   SYNTHESIS §1 / §5 (numbers from `dc2.json`).
8. Any departure after a requirement text has been read is a numbered deviation DC2-3, … in `results_DC2.md`; none
   of the §9 items may move.
9. Set the Status line below to `AWAITING APPROVAL <commit-hash>`, push, and stop.

## Rules that always apply
- No bypassing: no bot check, paywall, login or verification step is circumvented; `none` is a recorded result.
- Sources are the publishing body's own texts, abstracts, catalogue or guidance pages; papers, EPRI reports, blogs
  and trade press locate, they do not source.
- Two blind raters; κ ≥ 0.6 on the window class (over M₁) and ≥ 80 % identification agreement, or UNGATED;
  disagreements reported, never reconciled.
- Every requirement SOURCED (URL, document, clause, quote ≤ 25 words); every class DERIVED-judgemental; both raters
  are language-model sessions and the write-up says so. No dollar figures.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `AWAITING APPROVAL <commit-hash>` or `BLOCKED: <one-line reason>`, then commit
and push.

**Status:** AWAITING APPROVAL af74b0e (DC2: UNGATED, identification 0.52 < 0.80 on row granularity; kappa(window) 0.64; exploratory: ERCOT §6.5.7.11 the only history-shaped binding clause, both raters)
