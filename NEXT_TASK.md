# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-11-10 (end of day). **Owner of this file:** the reviewer. The running session only *reads* it,
except for the Status line.

**Previous task — L1: DONE at `a03164b`, reviewed and accepted** (gated: identification 0.84, κ 0.82; UNCLEAR
[V1: VOLATILE DOMAIN]; kill does not fire; every headline re-derived by the reviewer from the two ledgers,
`results/L1/review/`). SYNTHESIS refreshed. Plan: [`briefs/NEXT_EXPERIMENTS/README.md`](briefs/NEXT_EXPERIMENTS/README.md)
(order now DC2 → O1 → R1).

## Do these steps, in order

1. `git pull` on `main`.
2. Open [`briefs/DC2/README.md`](briefs/DC2/README.md) and follow its START HERE box. **First stage only:** write
   `results/DC2/DC2_preregistration.md` (definitions, search protocol, extraction fields and closed classes, readouts
   and decision table with every threshold filled in — the brief's §2–§5, reusing L1's procedure and its L-2 … L-4
   rules) and `results/DC2/DC2_instruments.md` (the fixed list of instruments, built by the brief §3 protocol by a
   fresh-context screener **before any limit, window or allowance is read**, with exact titles, landing pages, scope,
   access status, hit counts and the addition log), plus `DC2_screen.json`, `DC2_screen_prompt.md` and
   `DC2_orders.json` (`default_rng(31)` for rater A, `default_rng(32)` for rater B).
3. Commit with "before reading" in the commit message.
4. Set the Status line below to `AWAITING APPROVAL <commit-hash>`, push, and stop.

## Rules that always apply
- The instrument list is fixed from titles and scope statements only; additions only by the pre-registered citation
  rule, logged. The screener reads no limit value.
- Sources are the publishing body's own texts, abstracts or guidance; papers, EPRI reports and trade press locate,
  they do not source. No bypassing; `none` is a recorded result.
- Two blind raters on `dc2-rater-a` / `dc2-rater-b` (fresh-context sub-agents in sparse main-only clones, as L1);
  the analysis script is committed before either branch exists; κ ≥ 0.6 on the window class and ≥ 80 % identification
  agreement, or UNGATED; disagreements reported, never reconciled.
- Every requirement SOURCED (URL, document, clause, quote ≤ 25 words); every class DERIVED-judgemental; both raters are
  language-model sessions and the write-up says so. No dollar figures.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `AWAITING APPROVAL <commit-hash>` or `BLOCKED: <one-line reason>`, then commit
and push.

**Status:** AWAITING APPROVAL 60f7595 (DC2 stage 1: pre-registration + 53-instrument list, before reading; reviewer to rule on §3b item 2, DC2-S14)
