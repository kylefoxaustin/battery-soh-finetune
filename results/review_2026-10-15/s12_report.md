# Independent review — Study 1 & Study 2 (on-device SoH fine-tuning; per-unit adaptation at scale)

Reviewer lens: battery ML + statistics, adversarial. Repo `<repo>` at `731c2b7`.
Nothing in the repo was modified. All recomputation on CPU (`CUDA_VISIBLE_DEVICES=""`, `nice -n 10`, 8 threads), scripts
and logs in `<scratch>/review/s12/` (`a_ocv_nan.py`, `b_noise.py`, `c_stats.py`, `d_closed_form.py`, `d2_shrink_eb.py`,
`e_segbias.py`, `d_closed_form.log`, `d_closed_form.json`).

Provenance key for every number below: **[read]** = read from a repo file; **[recomputed]** = I recomputed it (script named).

---

## Critical — could change a verdict (or its wording)

### C1. "PER-UNIT ADAPTATION DOES NOT HELP" is too broad: a 1-parameter shrunken per-unit offset passes the repo's own pre-declared robustness rule

`results_large.md` §Decision and `RESEARCH_DOSSIER.md` §2.2/§9 generalise from *gradient fine-tuning of the head* (bias /
last-layer / whole-head, 300 Adam steps) to *per-unit adaptation*. The only closed-form per-unit method the repo tried is
`bias` (fleet + unshrunk window-mean residual, `analysis/rolling.py:136`). The natural estimator for a noisy per-unit
offset — a random-effects / empirical-Bayes shrinkage of that offset toward 0 — was not run, although the repo computed
exactly the two variance components it needs in `results/E/E_power_analysis.md` §2 (between-unit residual SD 2.18 Ah,
within-unit 4.11 Ah, primary [read]).

I re-ran the rolling protocol (same origins, 30 k km window, bands, (origin,label) pairs, `MIN_PAIRS`, same fold models,
frozen predictions recomputed from `runs/chf_*_k*/fleet.pt`; my frozen/bias/persist medians reproduce the repo's
`rolling_*_k*.json` to 3 decimals, e.g. primary 0–5 k: 4.098/3.906/4.844/4.936 [recomputed, `d_closed_form.py`]) with
closed-form methods only, no training:

**Changan primary, 0–5 k km, n = 89 units** [recomputed, `d2_shrink_eb.py`, κ fixed a priori = 4.11²/2.18² = 3.55 from E]:

| Method | median RMSE | vs frozen | beats frozen | sign p | Wilcoxon p | beats persist_recent | sign p |
|---|---|---|---|---|---|---|---|
| frozen | 4.098 | — | — | — | — | — | — |
| bias (repo) | 3.906 | −3.0 % | 55/89 | 0.033 | 0.018 | 69/89 | 1.8e-7 |
| **shrink_eb** (fleet + window-mean residual · n/(n+3.55)) | 3.915 | −4.1 % | 59/89 | **0.0028** | 1.6e-4 | 70/89 | 5e-8 |
| **shrink_eb_ewma10** (same, EWMA residual over all past, τ = 10 k km) | 3.851 | −5.4 % | **67/89** | **1.9e-6** | 3.7e-6 | 70/89 | 5e-8 |
| oracle_bias (true full-history offset; upper bound, not a method) | 3.685 | −6.2 % | 71/89 | 1.3e-8 | — | 71/89 | — |

`shrink_eb_ewma10` satisfies every clause of the pre-declared rule (`analysis/aggregate.py:91-94`: median < frozen,
majority, sign p < 0.0025 vs frozen **and** vs `persist_recent`) at 0–5 k km on primary. `shrink_eb` misses the sign-test
clause by a hair (0.0028 vs 0.0025) while its Wilcoxon p is 1.6e-4. At 5–10 k km both are 53–54/81, sign p 0.004–0.007
(Wilcoxon 2–5e-4) — directionally the same, not clearing Bonferroni. Strict (n = 37) agrees in direction at 0–5 k
(shrink_eb 24/37, −5.4 %, Wilcoxon 0.013) but is underpowered. Beyond 10 k km the gain fades to ~0–1 %, never hurts.

Why this is real and not a noise artefact: the oracle (fleet + the unit's true lifetime mean residual) improves frozen
RMSE by 4–9 % at *every* horizon on both label sets (71/89, 65/81, 73/85, 66/86, 70/88 units on primary [recomputed]).
A persistent per-unit offset the fleet model misses exists (E's own 22 % between-unit share). The repo's `bias` method
estimated it from ~9 window labels with SE ≈ 4.76/√9 ≈ 1.6 Ah against a true offset SD of 2.2 Ah, so the un-shrunk
estimate adds about as much variance as it removes; the optimal shrinkage factor σ_b²/(σ_b²+σ²/n) ≈ 0.6 is what κ ≈ 3.5
implements.

**Caveats I apply to myself.** (i) The *method family* is mine, chosen after seeing the repo's results — but κ was fixed
from the repo's own pre-existing numbers, not tuned (a κ ∈ {2, 5} bracket gives 58/89 p=0.0055 and 61/89 p=0.0006 in
`d_closed_form.log`). (ii) The effect is small in absolute terms: ≈ 0.2–0.25 Ah of a 4.1 Ah RMSE (≈ 0.2 % of pack
capacity), well inside label noise, and only at ≤ 10 k km. (iii) It is not confirmed on an independent dataset.

**What changes.** The *finding* "gradient fine-tuning of the head does not help" stands. The *decision line* should read:
"on-device **training** does not help; a shrunken running-offset (a few bytes of state, no backprop) gives a small, robust
short-horizon gain on Changan". That also changes the EVBattery reading (see C2). It strengthens, not weakens, the
engineering conclusion for the i.MX 95 (even less compute needed), but the write-up's claim is currently wrong in scope.

### C2. "Persistence matches the only gain" conflates two different mechanisms and is dataset-specific

On EVBattery 0–5 k, `persist_recent` (0.733) ≈ last-layer FT (0.735) [read]. The dossier generalises this to "a unit's own
recent capacity measurements can carry near-term information … and capturing it needs a running average, not on-device
training". My recomputation shows the two datasets have *opposite* structure [recomputed, `d_closed_form.log`]:

| 0–5 k km | EVBattery (n=19) | Changan primary (n=89) |
|---|---|---|
| oracle persistent offset | 0.762 (−9 %) | **3.685 (−6 %, best)** |
| EWMA/recent-label persistence (`persist5`) | **0.733 (−23 %, best)** | 4.936 (+31 %, worst model-free) |
| residual EWMA τ=5k | 0.719 | 3.874 |

EVBattery's gain is a *slowly varying* label deviation (autocorrelated over < 10 k km; persistence beats even the oracle
constant offset) — plausibly a property of how He et al. built their labels, which are "opaque" [read, dossier §1].
Changan's gain is a *persistent* offset that noisy recent labels cannot estimate. "Persistence matches" is true only on
EVBattery; on Changan every residual-tracking method beats persistence by 65–80 of 89 units at every horizon. The
robustness rule's single control (`persist_recent`) is therefore the *weaker* control on Changan (`persist` at 30 k is
better there: 4.84 vs 4.94 [read]) and the stronger one on EVBattery; the rule should use the better of the two (or a
tuned label-EWMA; I ran `ewma_label10`: 4.707 on Changan 0–5 k, still far behind any residual method).

### C3. The "label-noise floor … that is the ceiling" argument is not supported; the floor estimate is an *upper* bound on irreducible noise

`results_large.md` Decision: "The fleet model sits at the label-noise floor (rolling frozen medians 3.73–4.54 Ah vs
≈ 3.9–4.8 Ah noise …). That is the ceiling." The "noise" is the SD of a unit's labels about its own linear fit vs
odometer (`results/make_report.py:33-45`; same for Changan [read]). I reproduce it exactly: 4.761 / MAD 3.909 Ah on the 94
primary units [recomputed, `b_noise.py`]. But:

- One-shot frozen RMSE is **below** the unit's own "noise floor" in **54/94** units (median ratio 0.965) [recomputed].
  A floor that a model beats half the time is not a floor.
- An **out-of-unit** fleet covariate correction (fit on the other 93 units' linear residuals; covariates = charge
  temperature, start SOC, end current, log segment duration, season) reduces the median within-unit SD from 4.76 to
  **4.49 Ah**, improving 81/94 units [recomputed]. In-unit 9-parameter OLS gives 3.70 (overfit; dof-corrected 4.17).
- The label covariates the model *can* see (temperature, current, SOC trajectory in the last 128 charging frames) are
  exactly those; so part of the "noise" is predictable, which is why frozen beats it.

The repo's own E power analysis makes the same point implicitly (within-unit residual SD 4.11 < "noise" 4.76). The
dossier should drop "ceiling" and say "frozen RMSE is comparable to a crude noise estimate that is itself an upper bound".
This does **not** rescue fine-tuning (oracle offset gain is only 4–9 %), but it changes the stated reason for the
negative.

---

## Major

### M1. Label-construction defect: segment-duration bias of ≈ +2.3 Ah per e-fold, +3.7 Ah for 6–24 h segments

`data/changan_labels.py:36` allows a wake→full segment up to `MAX_SEG_S = 3 days`; the label is the Ah integral over
that segment divided by (1 − SOC_s). Within-unit (unit-demeaned) OLS on the 6,638 primary labels of the target units
[recomputed, `e_segbias.py`]: label = **+2.34 Ah per e-fold of segment duration** (+0.31 Ah/°C temperature,
+0.31 Ah per A of end current). By duration bin: 0–2 h −0.54 Ah, 2–6 h +0.44, **6–24 h +3.72 Ah** (n = 420 = 7.4 % of
primary labels), 24–72 h +10.9 (n = 2). A current-sensor offset of ~0.15 A integrated over 24 h gives ~3.6 Ah — the
right order. The strict filter (< 6 h) removes it, which is one reason strict noise is 3.84 vs 4.76. The fleet model
cannot see segment duration (its input is the last 128 charging frames), so this is pure label noise to every method,
and it is **removable at the label stage** (regress out log seg_s fleet-wide, or cap at 6 h in primary). Expected payoff:
primary noise SD falls toward ~4.4–4.5 Ah with no loss of units.

### M2. (downgraded to minor after measurement — kept here for traceability) NaN odometer silently drops vehicles from the OCV table

`data/changan_labels.py:57`: `early = d["odo"][w] <= d["odo"].min() + EARLY_KM`. Eight slim files contain NaN odometer
frames; `odo.min()` is then NaN and `early` is all-False, so those vehicles contribute **zero** rests to the pooled OCV
table. Replicating the selection logic exactly reproduces `ocv_full.json` (292 of 300 vehicles, 62,877 rests); with
`np.nanmin` it is 300 vehicles, 64,260 rests [recomputed, `a_ocv_nan.py`]. Impact: 2.2 % of rests from 8 vehicles, so the
table is essentially unchanged — a silent bug, not a result-changer. Fix with `np.nanmin`. The same run confirms the OCV
premise: odometer at record start is 2–10 km for 95 % of vehicles (median 8 km; only 4 vehicles start > 20 k km), so
"new-pack BMS SOC is accurate" is a reasonable ASSUMED anchor.

### M3. Bonferroni family is per-label-set; harm claims use raw p; the positive bar is asymmetric

- `aggregate.py:71-72`: family = 5 bands × 4 FT methods = 20 **per label set**. The decision is taken over primary +
  strict + EVBattery (60 tests) plus the one-shot family (≈ 12). Nothing passed, so no harm — but the dossier's "Strong
  … Bonferroni" strength tag should say the family definition.
- "Significantly worse" claims (`results_large.md` §A: whole-head p = 0.0095 primary; dossier §2.2 "whole-head
  fine-tuning is significantly worse on both") use raw p while "helps" needs p < 0.0025. Under the same Bonferroni,
  primary whole-head harm (0.0095) is **not** significant; strict (0.00025) is. Report consistently.
- Dossier §2.2 "It is significantly worse at 40–80 k km" — true for *unguarded* last-layer only (23/88, p = 8.5e-6
  [read]); the deployable guarded variant is 35/88, p = 0.086 [read]. Qualify.
- Sign test vs Wilcoxon: with Wilcoxon signed-rank [recomputed, `c_stats.py`], Holm over 20 tests, primary shows two
  significant *harms* (last 40–80 k, head_guard 40–80 k) and no help; EVBattery shows last/last_guard/head_guard
  significantly *better* than frozen at 0–5 k but none vs persistence. Study 1's "last-layer FT hurt" is Wilcoxon
  p = 0.011 (sign p = 0.115) — results.md wisely didn't claim significance. The sign test is a legitimate conservative
  choice, but it is the lower-power choice for a *negative* study, which cuts against the authors' own interest in
  "absence of evidence ≠ evidence of absence". Report both.

### M4. The "majority" clause treats guard ties as losses

`aggregate.py:92`: `beats_frozen > n/2` counts ties (guard chose 0 steps = frozen) as not beating. With 32–39 of 94 ties
in one-shot [read], a guarded method can never pass the clause even if it wins every non-tied unit. Either apply the
clause to non-tied units or state it.

---

## Minor

- **m1. dof.** Noise SD uses `res.std()` (n dof) about a 2-parameter fit; with n−2 it is 4.88 Ah [recomputed]. Negligible,
  and the bias is in the direction that *favours* the "at the floor" claim; mention.
- **m2. EVBattery label duplication.** Labels are constant within a charge segment (within-segment SD ≤ 1e-5 Ah, 13
  snippets/segment median [recomputed]). `results.md` E5 "915 labelled charge snippets" ≈ 70 distinct labels; the FT
  window's information content is overstated by ~13× in that framing. Also 300 Adam steps × bs 32 on ~70 labels is ~140
  epochs of the same labels — the overfit in Study 1 is partly a protocol artefact.
- **m3. Model can read the BMS's own capacity estimate.** During a 49 A CC charge, ΔSOC_BMS/Δt encodes C_BMS. From the
  128-frame snippet: proxy valid for 98 % of labels, median 108 Ah, declining 109.7→95.9 Ah across 0–400 k km, within-unit
  corr with the label 0.33 [recomputed, `e_segbias.py`]. Not leakage of the derived label (which uses OCV SOC_s and Ah
  integration, not BMS SOC), but a strong "feature" worth naming: the fleet LSTM is partly reading a BMS estimate, which
  helps explain why it beats mileage-linear by 1.2 Ah and leaves little for per-unit learning.
- **m4. Label semantics.** The label is "Ah to first-cell 4.20 V at 49 A"; the snippet contains vmax and V/96, so the
  model directly observes the imbalance that triggers cutoff. The label tracks *usable CC charge*, not capacity; the
  dossier says "tracks degradation", fine, but imbalance growth and capacity fade are confounded in it.
- **m5. OCV table is pooled across all 300 units including each fold's targets** (`changan_labels.py:52-70`;
  `run_full.sh` step 3). Not differential leakage (frozen and FT see the same labels), 1/300 per unit; disclose.
- **m6. Three EVBattery cars have unscored bands** (83, 121, 168: spans 25–57 k km) so n = 18–19 not 20 [read,
  `rolling_evb_ds1.json`]. Say so in the table header (it says "19–20").
- **m7. Head-guard is the best model-based method on EVBattery 0–5 k** (0.713 vs last 0.735 [read]) and is not shown in
  the EVBattery table; model-based offset methods beat persistence 15–18/19 at ≥ 5 k km while matching frozen
  [recomputed]. Under-claim, not over-claim.
- **m8. Numbers cross-checked and consistent** between dossier / results_large / summary JSONs / split.json: 94/45 units,
  fold partitions clean (no target in own train/val; union 94/45 [recomputed]), 4.76/3.84 noise, 6.5 fade, 62,877 rests /
  77 bins [read `ocv_full.json`], val baselines 4.36–4.59 vs 5.45–5.87 [read split.json], 68/12/20 cars, 1.196/1.290,
  0.65 Ah floor (0.648 [recomputed]), one-shot median capacity drop 2.0 Ah [recomputed from e4.json per_car]. No
  inconsistencies found in the Study 1–2 numbers.
- **m9. Odometer channel.** z at 600 k km is 5.4–5.9 < Z_CLIP 6 across folds [recomputed]; no saturation. Odometer is
  broadcast as a constant channel through an LSTM — a cheap, odd way to inject a scalar; fine.
- **m10.** `MIN_WINDOW_LABELS = 5` plus 300 full-batch Adam steps on 5–9 labels for 65 params is a regime where
  overfitting is guaranteed; the guard's holdout is 1–2 labels. The result "FT hurts at long horizons" is therefore
  largely about this regime, which the dossier should say when it generalises.

---

## Missed opportunities (ranked by expected value)

1. **Shrunken offset / Kalman offset as the deployable "adaptation" (done above; needs confirmation).** Pre-register
   κ = σ_w²/σ_b² from E, confirm on strict and on EVBattery ds2/ds3 (fresh units, supplied labels). Cost: hours, CPU.
   Payoff: converts the headline into a positive, cheap, board-trivial recommendation (bytes of state, no backprop) —
   or kills it cleanly.
2. **Fix the label (M1) and re-derive noise.** Regress out log(seg_s), T, I_end fleet-wide on the OCV-calibrated label;
   or cap segments at 6 h in primary. Expected noise 4.76 → ≈ 4.4; rerun the rolling protocol. Also consider the paper's
   own 4.25 V cutoff and a pack-mean-voltage start anchor to decouple imbalance. Cost: one pipeline rerun (~1–2 h).
3. **EVBattery sub-datasets 2 and 3** (`data/processed/evbattery_ds{2,3}.npz` are already built, 836 MB / 136 MB). Two
   more manufacturers with *supplied* labels at ~1.6 % noise: the cleanest available test of generality for both the
   FT negative and the offset positive. Cost: 2 fleet trainings (~minutes on GPU) + rolling.
4. **Label-noise-aware evaluation.** Report paired ΔMSE with a unit-level bootstrap CI instead of/in addition to RMSE
   sign tests; evaluate against a smoothed label (per-unit LOESS of future labels) to reduce the noise term equally for
   all methods — raises power for small effects like the 4–6 % here.
5. **Hierarchical / mixed-effects fleet model.** Random intercept per unit learned jointly (or a per-unit embedding
   with L2 shrinkage) is the principled version of (1) and would also give calibrated per-unit uncertainty for E's
   bound question.
6. **Fairer FT regime.** Fewer steps (guard shows 25–50 often chosen), weight decay toward fleet weights (L2-SP), or
   fine-tune only the bias with Adam — gradient FT was tested only in a known-overfitting regime.

---

## Things that are solid

- Fold construction and leakage hygiene: per-unit 4-fold, targets never in own train/val (verified), normalisation
  fitted on train units only (`common.py:53-63`, `train_fleet.py:89`), guard uses only pre-origin data
  (`rolling.py:69-98`), identical (origin,label) pairs for every method, bit-identical frozen-weight gates.
- Rolling protocol is causal; I reproduced its frozen/bias/persist medians to 3 decimals from the saved models.
- The disclosed post-hoc additions (persistence control, Bonferroni) do make a positive claim harder, as stated.
- Baselines: every fold's LSTM beats fleet-mean and mileage-linear on its own val units (verified in split.json).
- Board measurements, census, governor pinning, gating — not in my lens, but the Study 1 memory erratum is handled
  honestly.
- Numbers are traceable: every figure I checked in results.md / results_large.md / dossier matched the JSONs.
- Study 1's core finding (one-shot early-data FT hurts; the fleet model with odometer is hard to beat) is correct and
  well-explained; the no-odometer sensitivity is a good control.
