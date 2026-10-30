# X5 reviewer decision — APPROVED (2026-10-30)

> ## ▶ START HERE — instructions for the session running this repo
>
> 1. `git fetch && git checkout x5-review && git pull` — this branch carries this file and the X4 correction.
> 2. Read this file in full, then `results/X/X5_preregistration.md` and `results/X/X5_profile.md` (both at `059b818`).
> 3. **X5 is approved as pre-registered**, with the two additions in §2 below. Do not change anything else.
> 4. Commit §2's two additions as **numbered deviations D-1 and D-2** in `X5_preregistration.md` **before** writing
>    `analysis/X5_estimate.py`. Commit message must say "before estimator code".
> 5. Write and run `analysis/X5_estimate.py` exactly as pre-registered. Then commit
>    `results/X/X5/results_X5.md`, its JSON and plots, and the README/dossier updates. **Stop** and push for review.
> 6. Merge `x5-review` into `main` along with your results (fast-forward or merge commit; do not rebase away the
>    X4 correction commit).
> 7. Do **not** run BatICM, Yuasa or UMich arms. Do **not** start any new experiment.

---

## 1. Review of the audit and pre-registration (`059b818`)

**Accepted:** ISU-ILCC as primary (Candidate C), with the coupling caveat on every verdict, the 30 / 31 split in
`X5/split.json`, and all five departures P-1 to P-5.

**Notes on the departures:**

- **P-1 (Candidate C primary).** Correct. No public set re-measures each cell's capacity inside a string that aged
  together. The Yuasa correction (labels are model estimates, not measurements) is also correct; the brief was wrong.
- **P-2 (shuffle permutes cells at every past check).** Correct. The brief's whole-series permutation leaves
  `min over cells` unchanged and could not have failed. Thank you.
- **P-3 (reserve on the over-statement tail, `q(1−α)(e)`).** Correct, and it applies to X4 too. X4 has been
  re-scored on the correct tail on this branch (`results/X/x4/README.md`, `x4_results_overstatement_tail.json`).
  **X4's verdict does not change: NO GAIN** (gain 0.93 at 99 %, 1.00 at 99.9 %; 1.16–1.17 at W = 4).
- **P-4 (last-value P3 = P0).** Correct. Report as degenerate.
- **P-5 (group size 4 only).** Correct.
- **P1 uses a calibration-half constant ρ.** Correct, and important: a pack-level BMS never observes its own weakest
  cell, so its ratio must come from other packs. Keep P1-h as reported-not-deciding.

## 2. Two additions (commit as deviations D-1 and D-2 before estimator code)

**D-1 — End-of-first-life truncation is a co-primary readout, not only a sensitivity row.**
ISU cells run to a median 51 % fade, far past automotive use. A gain that only appears below 80 % does not answer the
reserve question. So:

- Report the **full verdict table (§5) twice**, side by side: (a) full life, as pre-registered; (b) each unit
  truncated at the first check where `U < 0.8 · U_0`.
- The **headline verdict** is (a). If (a) and (b) disagree, say so in the first paragraph of `results_X5.md`.
- If truncation leaves fewer than 40 evaluation targets, (b) is UNDERPOWERED. Report that; do not relax anything.

**D-2 — Report the spread trajectory beside the result.**
ISU spread runs from ~1.3 % at the first check to ~40 % at the last. Per-cell history should help most where spread
is large. Add one descriptive table: P3 and P1 reserve at α = 1 %, binned by the unit's within-group spread at the
target check (< 2 %, 2–5 %, 5–15 %, > 15 %). Descriptive only, no verdict.

## 3. What not to do

- Do not touch the split, W, warm-up, α, the P4 model family or its features.
- Do not convert any reserve into kWh, dollars, range, or a regulatory statement.
- Do not present a gain without the shuffle control beside it.
- Do not omit the coupling caveat: *"synthetic packs of separately tested cells; no thermal or electrical coupling;
  an upper bound on what per-cell history can do."*

## 4. Why this experiment matters (context, one paragraph)

A lifetime cost model (`results/X/lifecost/`) found that the dominant value in a "20 % → 5 % reserve" claim is an
**uncertainty** reserve: the energy held back because the weakest cell's remaining capacity is not known precisely.
Shrinking it 4× needs a usable-energy estimate about 4× more precise. Field data cannot test that (X4: ~6 % label
noise). ISU-ILCC is the first public set with measured per-cell capacity over life and 0.24 % label noise, and its
cells diverge strongly, which gives per-cell history its best chance. **If per-cell history cannot reach 1.5× here,
the claim has no support in public data. That is a result worth having.**
