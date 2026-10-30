# Converter-side efficiency replay — results (public domain, CC0)

Run 2026-10-29. Code: `convsim.py`, `run_replay.py`, `run_sens.py`, `run_stress.py`.
Outputs: `results_base.json`, `results_sens.json`, `results_stress.json`, `replay_plot.png`.

**Every component value is ASSUMED** (datasheet-class 100 V GaN, multiphase buck). The drive cycle is real
(WLTC class 3b, 1 Hz, from the JRC `wltp` repository, EUPL). The vehicle-to-12 V-load mapping is ASSUMED. This is a
loss-model replay, not a measurement.

## Plant
48 V → 12 V interleaved buck, 1–6 GaN phases. Each controller picks phase count, switching frequency and dead-time
from the same grid. The plant is credible: 97–98 % efficiency, and the optimum genuinely moves — 1 phase at
150 W, 6 phases at 1.2 kW; a setting tuned for one load costs 3–4 points at another.

## Result (excess converter loss versus the instantaneous optimum)

| Case | Tier A (1 s) | Tier B (frozen 30 s, 30 s stale) | Static table, by load | One fixed setting |
|---|---|---|---|---|
| Base: half life, 45 °C | +0.00 % | **+9.5 %** | **+0.02 %** | +6.0 % |
| End of life, 45 °C | +0.00 % | +10.0 % | +0.09 % | |
| Cold −10 °C, new | +0.00 % | +9.6 % | +0.93 % | |
| Hot 70 °C ambient, EOL | +0.00 % | +11.1 % | +0.29 % | |
| Aggressive ageing (Rds +80 %), EOL | +0.00 % | +13.0 % | +0.99 % | |

Tier A at 1 s is identical to the oracle by construction. At 5 s and 10 s refresh it loses 4.0 % and 6.0 %.

## What it means
1. **The value is in tracking load, not in remembering history.** A load-indexed factory table that never learns
   temperature or ageing stays within 0–1 % of optimal loss in every case, including end of life and −10 °C.
   Temperature and ageing move the optimum only weakly in this model.
2. **Freezing parameters for 30 s is expensive (~+10 % loss), but that is not a realistic design.** Any controller
   that indexes a table by measured load at loop rate avoids it. That is an MCU-class job.
3. **In absolute terms it is small.** Converter loss is ~2 % of throughput. Even the frozen-30 s case costs about
   0.2 efficiency points: 0.6 Wh on a 23 km cycle, ~0.003 kWh/100 km.

## What the model cannot see
- **Anticipation.** The replay is quasi-static at 1 Hz. It has no load-step dynamics, so it cannot test pre-enabling
  phases ahead of a known transient — the one mechanism where history-based forecasting plausibly helps.
- **Unit-specific degradation with a strong effect on the optimum** (e.g. GaN dynamic Rds(on), magnetics drift).
  In this model ageing barely moves the optimum; real parts may differ.
- **Traction-scale converters, multiple converters coordinating, fault diagnosis.**
