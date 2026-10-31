# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-10-30. **Owner of this file:** the reviewer. The running session only *reads* it, except for the
Status line.

**Previous task — X7 first stage: done at `8a468ad`; X7 CLOSED as UNDERPOWERED by the reviewer** (power gate failed
under any fold assignment; 1 K thermistor steps and a probe-max gap never above 1.0 K cap the recoverable margin at the
bar). No observer is to be fitted. Write-ups: `results/X/X7_profile.md`, `results/X/X7_preregistration.md`; one row each
added to `results/X/README.md` and `results/RESEARCH_DOSSIER.md` §9. Plan: `briefs/NEXT_EXPERIMENTS/README.md`
(order now B1 → DC1 → X8 → FR1 → O1 → R1).

## Do these steps, in order

1. `git pull` on `main`.
2. Open [`briefs/B1/README.md`](briefs/B1/README.md) and follow its START HERE box.
   **Stage 1:** the board census (`results/B1/census.md`), committed with "B1 census, before ring code" in the message.
3. If every census gate in brief §3.5 passes, **continue to Stage 2 without stopping** and run the protocol in brief §4
   exactly as written (phases P0–P6, repeats as tabled). If any gate fails, set the Status line to
   `BLOCKED: <gate> <value>`, push, and stop.
4. Commit `results/B1/results_B1.md`, `results/B1/b1.json`, `results/B1/raw/`, the new `board/b1_*` files, one row each
   in `results/X/README.md` and `results/RESEARCH_DOSSIER.md` §9, and a dated note under ANGLES §B.3.
5. Set the Status line to `DONE <commit-hash>`, push, and stop. Do not start DC1 or anything else.

## Rules that always apply
- B1 is a capability measurement: no verdict, no tuning toward one. Report every number with its spread and its bound.
- Tag every number MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED. The eMMC wear figures are DERIVED from an ASSUMED
  endurance and say so in the same table cell.
- **The producer is a CPU thread, not DMA: every CPU-cost number is an upper bound on a DMA path.** Say so beside it.
- Never imply a HyperRAM, MCU-SDRAM or MCU-product measurement; those columns stay DERIVED arithmetic with sources.
- Governor pinned and restored; census before and after each phase; `timeout -k` on every child; nothing else on the board.
- Do not tune ring size, dump length or pacing after a dump gate fails; the failure is a result.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `DONE <commit-hash>` or `BLOCKED: <one-line reason>`, then commit and push.

**Status:** DONE 0c4b61e
