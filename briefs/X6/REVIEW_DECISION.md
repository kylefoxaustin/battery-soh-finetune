> ## ▶ START HERE (updated 2026-10-30): X6 is APPROVED, run it now
>
> 1. `git pull` on `main`.
> 2. Read [`briefs/X6/REVIEW_DECISION.md`](REVIEW_DECISION.md). X6 is approved as pre-registered (`2188950`), with
>    the reported additions R-1 and R-2.
> 3. Commit R-1 and R-2 as deviations **D-1 and D-2** in `results/X/X6_preregistration.md`. The commit message must
>    contain "before forecasting code".
> 4. Write and run `analysis/X6_forecast.py` exactly as pre-registered, plus R-1 and R-2.
> 5. Commit `results/X/X6/results_X6.md` (verdict first, with the coupling caveat and licence), `x6.json`, the plots,
>    and the `results/X/README.md` and `results/RESEARCH_DOSSIER.md` updates.
> 6. Set the Status line in [`NEXT_TASK.md`](../../NEXT_TASK.md) to `DONE <commit-hash>`, then **stop and push**.
>    Do not start any other experiment.

---

# X6 reviewer decision: APPROVED (2026-10-30)

Approves `2188950`: the knee definition (H = 2, T = 5 %, 2× rate rule), the profile, the pre-registration and
departure X6-P1. **Two reported additions, R-1 and R-2.** Neither changes the decision table.

## 1. Accepted
- **Knee definition** (chosen without any forecast), and the H1/T3 and H3/T8 sensitivity pair.
- **Power:** 66 evaluation events (full life), so the gate passes. First life has 6 events and is descriptive only.
- **X6-P1** (the shuffle permutes capacity and Q(V) jointly). A Q(V)-only shuffle would keep real per-cell capacity
  trends and would not test cell identity.
- **K1 gives non-weakest cells a constant score.** That is an accurate model of a min/max view. The profile shows
  ~4 in 5 knees start in a cell that is not the weakest, so K1's blindness to them is a property of a min/max BMS.

## 2. R-1: report the two contrasts that separate "per-cell" from "history"
Report both in the verdict section, each with a unit-bootstrap 95 % CI. **Neither decides.**

| Contrast | What it isolates |
|---|---|
| **AUC(K3) − AUC(K3-sh)** | The value of **cell identity**, tested directly against the shuffle rather than via K1 |
| **AUC(K3) − AUC(K2)** | The value of **rich curve history** (Q(V) features) over a 4-point per-cell capacity trend |

**Why:** K2 needs ~4 numbers per cell. K3 needs W Q(V) curves of 1,000 points per cell. Separate the two, so the
result says whether knee warning needs a few numbers per cell or a deep per-cell history.

## 3. R-2: show K1's structural ceiling beside its AUC
Put K1 non-weakest cells in a tied block, rank weakest-cell positives top and weakest-cell negatives bottom, and
report that best-case AUC beside K1's actual AUC. Reviewer estimate from the profile counts: about **0.69–0.73** at
L = 1. This lets a reader see how much of K3 − K1 is structural.

## 4. Unchanged
Thresholds, H, T, W, L, λ, the model family, the features, the split, the decision table and the controls.
