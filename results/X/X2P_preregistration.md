# Experiment X2-P: pre-registration for active probing, as a precision and coverage curve for per-cell R

**What X2-P asks.** A BMS that injects brief current steps would manufacture its own R history.

1. **Precision.** How many steps, of what amplitude, does it take to recover each pack's per-cell R pattern?
2. **Coverage.** How many injected steps per charge session would give ≥ 90 % of sessions a usable per-cell R?

**Origin and approval.**

- The v2 brief §8.4 item 3, reframed in an internal response note (not included) §3.
- Kyle said "lets do all the recommendations" (2026-10-16).
- This file is committed **before** any X2-P code exists.

**Why it is reframed.**

- The brief's "S on newly covered sessions" would borrow R from elsewhere, so it is true by construction.
- The question the data can answer is how much probing buys a usable R.
- Natural current steps in the Changan record stand in for injected ones.

**Tags.** All outputs are DERIVED, on Changan (CC BY-NC-SA 4.0, non-commercial). The safety envelope is ASSUMED. No
claim is made about real probing hardware.

## 0. What is known in advance (disclosure)

- **X2 base:** the 30-day window holds a median of 7 steps ≥ 0.3 C; 26.5 % of sessions have ≥ 20.
- **Split-half probe (2026-10-16), all steps ≥ 0.3 C per vehicle, about 2,100 steps:**
  - ρ = 0.98 interleaved and 0.94 early versus late;
  - the worst cell is the same in 69–81 % of vehicles;
  - worst / median R_k is 1.20.
- **Not yet computed:** precision at small n or small amplitude, and any coverage figure.

## 1. Steps and amplitude bins

**Definition of a step.** As X2:

- consecutive full frames ≤ 30 s apart, with |ΔT_mean| ≤ 1 °C;
- r_k = ΔV_k / ΔI, with charge-positive current, in mΩ;
- Q_ref = 120 Ah (X2 OPEN-3).

**Amplitude bins** (|ΔI| / Q_ref):

| Bin | Range |
|---|---|
| a1 | 0.05–0.10 C (6–12 A) |
| a2 | 0.10–0.20 C |
| a3 | 0.20–0.30 C |
| a4 | ≥ 0.30 C |

Cell voltage resolution is 1 mV (`dv_full` int16 mV). In a1, ΔV is about 6–12 mV per cell at about 1 mΩ.

## 2. Precision

**Reference and probe pools.** For each vehicle, steps are split by **index parity**.

- The **reference** R_k^ref is the median over the **even-index steps ≥ 0.3 C**. It needs ≥ 40 such steps, or the
  vehicle is excluded.
- **Probes** are drawn from **odd-index** steps only, so probe and reference never share a step.

**Draws.** For each amplitude bin a and each n in {1, 2, 5, 10, 20, 40, 80}:

- 50 random draws (seed 0) of n odd-index steps in bin a;
- if the bin holds fewer than n steps, that (a, n) cell is NA for that vehicle;
- R_k^probe is the median over the n steps.

**Metrics per draw:**

- **ρ:** Spearman ρ between R^probe and R^ref across 96 cells;
- **hit3:** 1 if the argmax of R^probe is among the top 3 of R^ref;
- **ratio error:** |(max/median of R^probe) / (max/median of R^ref) − 1|.

**Aggregation.** Per vehicle, the median over draws. Then the median over vehicles, with p10 and p90, and the number
of vehicles.

**Pre-registered precision threshold.** n*(a) is the **smallest n** with:

- median-over-vehicles ρ ≥ **0.90**, **and**
- median-over-vehicles hit3 ≥ **0.80**,

with at least 30 vehicles evaluable at that (a, n). If no n qualifies, n*(a) = "> 80".

## 3. Coverage

**Sessions.** As X2: H's charge-session logic, keeping sessions with > 0.5 Ah.

**Injection model.** Each charge session receives **m** injected steps of amplitude a (m ∈ {1, 2, 5, 10}). Injected
steps count toward a session's **trailing window** (7 and 30 days, strictly before the session) together with
natural steps in amplitude ≥ a.

**Coverage(a, m, W)** is the fraction of sessions whose window holds ≥ n*(a) steps. The same is reported for **cold**
sessions (Tmin median < 10 °C), and the m = 0 baseline is natural steps only.

**Pre-registered output.** The smallest m with coverage ≥ **90 %** at W = 7 days, for each a with a finite n*(a).

## 4. Safety envelope (ASSUMED, explicit parameters, reported not optimised)

An injected step is allowed only in a charge frame with:

- Vmax ≤ V_lim − 50 mV;
- every probe between 10 °C and 45 °C;
- amplitude ≤ 0.3 C, duration of one frame pair (≤ 30 s), in the direction that **reduces** charge current.

**Envelope feasibility.** The fraction of charge sessions holding ≥ m frames inside the envelope is reported per m.
Coverage is recomputed counting only sessions that can host their m steps. This is the primary coverage figure;
the unconstrained figure is reported beside it.

## 5. What this will and will not say

**Will:**

- the step count and amplitude needed for a usable per-cell R on this fleet;
- how much injection per charge reaches ≥ 90 % coverage.

**Will not:**

- any charge-time saving;
- whether real injected steps behave like natural ones. Natural steps come mostly from driving transients, so they
  have different polarisation history from steps injected mid-charge. This limitation is stated in the results.

## 6. Deviations

Any change after this commit is a numbered deviation. Thresholds are never moved.

**Licence:** CC BY-NC-SA 4.0, non-commercial.
