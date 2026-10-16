# Results X2-P: active probing as a precision and coverage curve for per-cell R

Experiment X2-P, run 2026-10-16.

- **Pre-registration:** [`../X2P_preregistration.md`](../X2P_preregistration.md), commit `ea9f714`. It was committed
  before any X2-P code existed.
- **Code:** `analysis/X2P_probing.py`. Output: `x2p.json`.
- **Data:** 288 Changan vehicles with ≥ 40 reference steps; 286,832 charge sessions, 2,855 of them cold.
- **Tags:** all results are **DERIVED**. Natural current steps stand in for injected ones, and the envelope is
  ASSUMED.
- **Licence:** CC BY-NC-SA 4.0, non-commercial.

## Verdict (pre-registered thresholds)

**Precision.** n*(a) is the smallest step count giving a usable per-cell R: ρ ≥ 0.90 against a disjoint reference,
and the worst cell in the reference top 3 for the median vehicle.

| Step amplitude | n* | ρ at n = 20 | ρ at n = 80 |
|---|---|---|---|
| a1, 0.05–0.10 C (6–12 A) | **> 80** | 0.40 | 0.59 |
| a2, 0.10–0.20 C | **> 80** | 0.58 | 0.75 |
| a3, 0.20–0.30 C | **> 80** | 0.75 | 0.88 |
| a4, ≥ 0.30 C (≥ 36 A) | **80** | 0.85 | **0.93** |

**Coverage.** Sessions whose trailing window holds ≥ 80 steps ≥ 0.3 C, with m injected steps per prior session,
inside the envelope.

| m per session | 7 days: all | 7 days: cold | 30 days: all | 30 days: cold |
|---|---|---|---|---|
| 0 (natural only) | 7.1 % | 12.2 % | 16.2 % | 15.9 % |
| 1 | 7.8 % | 12.5 % | 26.6 % | 17.4 % |
| 2 | 8.7 % | 12.7 % | 66.8 % | 29.7 % |
| 5 | 24.6 % | 16.5 % | **90.0 %** | 63.0 % |
| 10 | 74.3 % | 35.0 % | 95.0 % | 76.4 % |

- The pre-registered output, the smallest m reaching 90 % at W = 7 days, is **none up to 10**.
- At W = 30 days the answer would be m = 5. That is reported, not substituted.
- **Envelope feasibility:** 96–98 % of sessions can host 1–10 steps inside the ASSUMED envelope, so the envelope is
  not the constraint.
- Cold coverage lags because cold-season vehicles charge less often.

## Reading

**1. Small steps carry little per-cell information.** At 6–24 A, even 80 steps recover the cross-cell R pattern only
weakly (ρ 0.59–0.75).

- With 1 mV resolution, a 6 A step moves a 1 mΩ cell by about 6 mV, so quantisation and timing noise dominate.
- **A probing scheme needs ≥ 0.3 C (about 36 A at 120 Ah) steps.** That is not a gentle perturbation.

**2. X2's 20-step history threshold gave a noisier R than it seemed.**

- At n = 20 and ≥ 0.3 C, ρ against an independent reference is 0.85, and the worst cell is in the top 3 for 74 % of
  draws.
- The full-record split-half (ρ 0.98) used about 1,000 steps per half.
- So X2's per-cell limiter partly acted on noise. Part of the +5.5 % margin saving may reflect R noise spread rather
  than true cell spread, although the κ calibration charges min/max for the same noise. This is an open caveat on
  X2's post-hoc figure.

**3. Reaching ≥ 90 % coverage needs either a longer window or heavy probing.**

| Window | What it takes |
|---|---|
| 7 days | > 10 large steps per charge, and still only 35 % in cold sessions |
| 30 days | 5 per charge |

R drifts slowly (split-half early versus late ρ 0.94), so a 30-day window is defensible. That would be a design
choice for a new pre-registration.

**What this means for the tier question.** The state is small: 80 steps × 96 cells × 2 B is about 15 KB, or a
running median per cell in bytes. Probing is a **firmware feature** (an MCU-class decision), not a reason for local
DDR history.

## Limitations

- **Natural steps are not injected steps.** Natural steps are mostly driving transients with different polarisation
  history. Mid-charge injected steps may behave better or worse.
- **"Usable" means agreement with this vehicle's own large-step reference.** That reference includes interconnect
  resistance (see X2 §2b), so it is not a true cell R.
- **The +5.5 % has not been re-run** with an 80-step or 30-day R. Doing so would re-use seen data, so it is not done
  here.

## Deviations

None after `ea9f714`.

- **Seeding:** the random draws are seeded per vehicle (`default_rng(car)`) rather than one global seed 0, so each
  vehicle is reproducible independently of pool order.
- **Ratio error:** this secondary metric is NaN at n ≤ 1 for some vehicles, when the median R is 0 at 1 mV
  resolution. It is not used in any decision.
