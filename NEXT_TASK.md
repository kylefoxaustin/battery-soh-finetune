# ▶ NEXT TASK: read this first, then do it. No other prompt is needed.

**Updated:** 2026-10-31. **Owner of this file:** the reviewer. The running session only *reads* it, except for the
Status line.

**DC1 first stage (`09051a5`) is APPROVED with two reviewer additions, D-1 and D-2.** They are spelled out in the
APPROVED box of [`briefs/DC1/README.md`](briefs/DC1/README.md). Plan: [`briefs/NEXT_EXPERIMENTS/README.md`](briefs/NEXT_EXPERIMENTS/README.md).

## Do these steps, in order

1. `git pull` on `main`.
2. Open [`briefs/DC1/README.md`](briefs/DC1/README.md) and read the APPROVED box.
3. Add **D-1** (co-primary decisions per workload: Llama LoRA and Stable Diffusion, each by §6 at W = 30 s; pooled 41
   and gated 20 reported, non-deciding; Llama carries the sub-0.30-swing caveat) and **D-2** (the 1 s ramp comparator
   K1-r and K1-r-sh; the memory readout as a ratio G(K1, 30 s) / G(K1-r, 1 s) with the 1.10 bar; W* over
   {1, 5, 30, 60} s) to `results/DC1/DC1_preregistration.md` §9 as numbered deviations. Commit with "before controller
   code" in the message. **Still no controller code in that commit.**
4. Write and run `analysis/DC1_storage.py` (and `analysis/DC1_sim.c` with the §4.5 C↔Python gate, if used) exactly as
   pre-registered plus D-1 and D-2. Every number DERIVED from SOURCED traces under ASSUMED specs; every table says so.
5. Commit `results/DC1/results_DC1.md` (verdicts first: Llama, SD; then the memory readout; licence and the resolution
   caveat on each), `results/DC1/dc1.json`, the plots, one row each in `results/X/README.md` and
   `results/RESEARCH_DOSSIER.md` §9, and a dated note under ANGLES §B.2.
6. Set the Status line below to `DONE <commit-hash>`, push, and stop. Do not start anything else.

## Rules that always apply
- Nothing in the pre-registration moves after results are seen; any further change is a numbered deviation.
- Report G_sh and G_∞ beside every G, and W* with the K1-r comparator beside it.
- Use only the measured per-job training profiles; the modelled whole-facility profiles are not data.
- Carry the licence (CC BY 4.0; credit DOE/NLR/ALLIANCE; cite arXiv:2604.07345 and DOI 10.7799/3025227) and the
  resolution caveat (node-level power at 5 Hz; 0.05–2.5 Hz band; not phase-level; not a GB200-class rack) on every
  verdict.
- No $ or capex claims here.
- Do not start any experiment this file does not name.

## When you finish
Edit only the **Status** line below to `DONE <commit-hash>` or `BLOCKED: <one-line reason>`, then commit and push.

**Status:** DONE cf94244
