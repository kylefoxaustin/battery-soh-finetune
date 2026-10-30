# Experiment X6: can history forecast a cell's knee before it arrives?

**Brief.** `briefs/X6/README.md`. **Profile:** `X6_profile.md` and `X6/profile.json`.

**Ordering.** This file and the profile are committed **before forecasting code exists**
(`analysis/X6_forecast.py` is not written). Nothing below runs until the reviewer approves.

**Data.** X5's, unchanged:

- ISU-ILCC, **CC BY 4.0**, RPT C/5 capacity and `Q_interpolated` curves;
- 61 groups;
- `X5/split.json` (30 calibration / 31 evaluation);
- X5's unit alignment, D-3 column rule and first-life truncation.

**Caveat on every verdict:** *synthetic packs of separately tested cells; no thermal or electrical coupling; an upper
bound.* **Tags:** all outputs are DERIVED from MEASURED labels. There are no kWh, cost, range or regulatory claims.

## 0. Departure from the brief's text (fixed now)

| # | Brief | X6 | Why |
|---|---|---|---|
| **X6-P1** | K3-sh: "each cell's **Q(V)** history permuted across cells… at every past check" | **Primary K3-sh permutes capacity and Q(V) together**, per check, within the unit (`default_rng(group)`), and the fitted K3 model is applied unchanged. The brief's Q(V)-only shuffle is also reported, as **K3-shQ**, not deciding. | Under a Q(V)-only shuffle, K3-sh keeps K2's real per-cell capacity features. It would beat K1 whenever per-cell *trends* do, so the decision's "K3-sh does not" condition would test something other than cell identity. The joint permutation matches X5's P-2. |

## 1. Knee onset (§3.1, fixed)

For each cell, using `q = Q / Q_0`:

- The onset is the first check k, with **k ≥ 3** (at least 3 earlier intervals), where:
  - `q_k − q_{k+2} > 0.05` (**H = 2, T = 5 %**);
  - `(q_k − q_{k+2}) / (t_{k+2} − t_k) ≥ 2 × median_{j≤k} [(q_{j−1} − q_j) / (t_j − t_{j−1})]`.
- Only a cell's first onset counts.
- **First-life readout:** the same rule on X5's truncated units (checks before U < 0.8·U₀). The rule needs k + 2
  inside the window. Only 6 evaluation events, so this readout is **descriptive only**.

## 2. Task A: warning

- **Scored cell-checks** (calibration for fitting, evaluation for scoring): check j of cell c, with **j ≥ W**,
  **j < the cell's onset** (if any), and **j + L ≤ n − 1**.
- **Positive:** onset ∈ (j, j + L].
- **L = 1 is primary.** L = 2 is reported with the full table.
- **Metrics:**
  - AUC (Mann–Whitney, ties counted ½);
  - precision and recall at the threshold giving a 10 % false-alarm rate on the evaluation negatives;
  - for each AUC difference (K3 − K1, K3-sh − K1, K2 − K1), a unit-bootstrap 95 % CI: 2,000 resamples of evaluation
    groups, seed 0.

## 3. Forecasters (strictly causal: only checks ≤ j)

**Window features over checks j − W + 1 … j (W = 4), on q = Q/Q₀:**

- `slope`: the OLS slope of q against t;
- `curv`: the t² coefficient of a quadratic OLS fit.

| ID | Score for cell c at check j |
|---|---|
| **K0** | Constant (base rate). AUC = 0.5. |
| **K1** (min/max view) | **If c is the weakest cell at j:** logistic model on `[slope, curv]` of the **weakest-cell series** `U/U₀`. It is fit on calibration rows where the scored cell was the weakest. **Otherwise:** the calibration positive rate among non-weakest rows, a constant. A min/max view observes only the current minimum. |
| **K2** (per-cell trend) | Logistic model on the cell's own `[slope, curv]` |
| **K3** (per-cell + curve) | Logistic model on `[slope, curv, f_var, f_peak]`, defined below |
| **K3-sh** (X6-P1) | The K3 model, with features computed after jointly permuting cells at every check of the unit |
| K3-shQ (reported) | The K3 model, with only Q(V) permuted per check |

**Q(V) features for K3:**

- `f_var = log10 var_V(Q_j(V) − Q_{j−W}(V))`, using nan-aware variance over the 1,000-point grid. The definition is
  the same as X5's P4.
- `f_peak = V*_j − V*_{j−W}` in mV. V* is the voltage of the maximum |dQ/dV|, computed as follows:
  - smooth Q(V) with a centred 21-point moving average (nan-aware);
  - take the gradient over V on the finite part of the grid;
  - V* is the voltage of the largest |dQ/dV|.
- Non-finite features are replaced by the calibration median, and the count is reported.

**Model** (identical for K1, K2 and K3):

- L2-regularised logistic regression on features standardised with calibration statistics;
- penalty λ = 1.0 on the coefficients, intercept unpenalised;
- fit by IRLS on the calibration half's Task A rows (L = 1; refit for L = 2);
- no class weighting.

Nothing is tuned.

## 4. Task B: reserve with knee adjustment

**Targets:** X5's exactly (W = 4, warm-up 30 %, evaluation half, full life: 374 targets). The over-statement tail
`r_α = q(1−α)(e) / median(U)` is used at α = 1 %, plus α = 5 % and 0.1 % as reported values.

**Fixed on the calibration half, per forecaster:**

- **Threshold θ:** the L = 1 score at a 10 % false-alarm rate on calibration negatives.
- **Drop δ:** the median one-check drop `(Q_k − Q_{k+1}) / Q_0` at calibration knee onsets.

**Adjustment.** For a target at check k, each forecaster scores every cell at check k − 1. Every cell, whatever its
onset status, is scored, because onsets are unknown at inference. Then:

| Adjusted estimator | Rule |
|---|---|
| **K1-adj** | X5's P2, lowered by δ·Q₀ of the weakest cell when K1's score for that cell > θ |
| **K2-adj, K3-adj** | X5's P3 per-cell trend forecasts. Each cell with score > θ is lowered by δ·Q₀,c, then the minimum is taken. |
| **K3-sh-adj** | X5's shuffled P3 (same per-check permutation), with K3-sh flags |

**Reported:**

- r_α for each adjusted estimator, with the unadjusted P1, P2 and P3 beside it;
- `G_B = r(K1-adj) / r(K3-adj)`, with a unit-bootstrap CI;
- `r(P1) / r(best adjusted)`, for the 4× question.

r is floored at 0.1 % before any ratio, as in X5.

## 5. Decision (L = 1, full life, checked in order)

| Verdict | Condition |
|---|---|
| **UNDERPOWERED** | < 30 knee events in the evaluation half. The profile has 66, so this is not expected to trigger. |
| **HISTORY FORECASTS KNEES** | AUC(K3) − AUC(K1) ≥ **0.10** with CI lower bound > 0, **and** AUC(K3-sh) − AUC(K1) < **0.05**, **and** G_B ≥ **1.5** |
| **WEAKEST-CELL VIEW SUFFICES** | AUC(K3) − AUC(K1) < **0.05** |
| **UNCLEAR** | Anything else |

**Also reported:**

- whether any adjusted reserve reaches **4×** over P1;
- the same table at L = 2;
- the first-life readout, descriptive.

**Disclosed in advance.** K1 gives non-weakest cells a constant score, and 78 % of knees start in non-weakest cells
(profile §3). An AUC gap in K3's favour is therefore expected on structure alone. The shuffle and Task B conditions
carry the test.

## 6. Controls

1. **Shuffle:** K3-sh (decision) and K3-shQ (reported).
2. **Who knees:** Task A with positives restricted to knees in cells that are **not** the weakest at onset − L.
   Negatives are unchanged. There are 47 events at L = 1 (≥ 10), so this is scored with CIs.
3. **Lead time:** L = 1 and L = 2 are reported separately. One weekly lab RPT is not a field lead time.

## 7. Sensitivity (pre-registered; each re-run end to end, verdict reported)

- W = 3 and W = 6.
- Knee definition H = 1, T = 3 % and H = 3, T = 8 % (alternatives fixed now, from `X6/profile.json`).
- Task B false-alarm rate 5 % and 20 % (θ only).

## 8. Outputs

- **Code:** `analysis/X6_forecast.py`, written only after approval.
- **Write-up:** `results/X/X6/results_X6.md`, verdict first, with the caveat and licence.
- **Data:** `x6.json`.
- **Plots:**
  - warning ROC per forecaster at L = 1 and 2;
  - reserve vs α with and without knee adjustment.
- **Also updated:** `results/X/README.md` and `results/RESEARCH_DOSSIER.md`.
- **No board run.**

## 9. Deviations

Any change after this commit is a numbered deviation. H, T, W, L, the thresholds, the model family, the features, λ
and the split never move.
