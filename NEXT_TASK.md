# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-11-11 (evening, later). **Owner of this file:** the reviewer. The running session only *reads* it,
except for the Status line.

**Kyle chose option 2: a second comparison domain for L1.** Brief: [`briefs/L1B/README.md`](briefs/L1B/README.md) —
exterior lighting as domain L, the seat domain re-rated as a calibration, the battery ledger carried over from L1, and
the stack-forcing class pre-registered and rated blind on all three domains. Plan:
[`briefs/NEXT_EXPERIMENTS/README.md`](briefs/NEXT_EXPERIMENTS/README.md).

## Do these steps, in order (L1b stage 1: pre-registration and the fixed lists, then STOP)

1. `git pull` on `main`.
2. Open [`briefs/L1B/README.md`](briefs/L1B/README.md) and follow its START HERE box. **Do not open**
   `results/L1/ledger_A.csv`, `ledger_B.csv`, `rater_A_notes.md`, `rater_B_notes.md` or `l1.json` by eye in the
   session that will launch the raters; `analysis/L1B_b_events.py` reads `l1.json` by script and writes
   `results/L1B/B_events.csv` with the identity and `what_changed` columns only (brief §4).
3. Write `results/L1B/L1B_preregistration.md`: L1's procedure by reference (§1–§9, L-1 … L-5), the three domains and
   their treatment (brief §2), the `stack` class (brief §3), the files and clone contents (brief §4), every readout and
   both decision tables with thresholds (brief §5), the calibration rule, the orders (`default_rng(51)` / `(52)` over
   the sorted S and L instrument IDs), branches `l1b-rater-a` / `l1b-rater-b`, and a disclosure of what the launching
   session has read.
4. Write `results/L1B/L1B_instruments.md`: the lighting list built by a fresh-context screener under the L1 §3
   protocol (titles and scope only; additions by the normative-reference rule; access logged; nothing about any
   instrument's change history read), seeded from brief §6; plus S01–S26 carried over verbatim from
   `results/L1/L1_instruments.md`. Commit the screen record and prompt beside it.
5. Commit with "before reading" in the commit message.
6. Set the Status line below to `AWAITING APPROVAL <commit-hash>`, push, and stop.

## Rules that always apply
- The instrument list is fixed from titles and scope only; additions only by the pre-registered rule, logged.
- Sources are the publishing body's own texts or summaries; trade press and search listings locate, never source.
  No bypassing; `none` is a recorded result.
- Two blind raters, fresh contexts, sparse clones with the five files named in the brief §4 and nothing else; the
  analysis script is committed before either branch exists; gates as the brief §5, or UNGATED; disagreements
  reported, never reconciled.
- Every event SOURCED; every class DERIVED-judgemental; both raters are language-model sessions and the write-up
  says so. No dollar figures.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `AWAITING APPROVAL <commit-hash>` or `BLOCKED: <one-line reason>`, then commit
and push.

**Status:** OPEN (L1b stage 1: pre-registration + fixed lighting list + B_events.csv, before reading)
