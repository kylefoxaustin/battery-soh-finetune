# Lifetime battery cost model — results (public domain, CC0)

Run 2026-10-29. Code: `lifecost.py`. Output: `results.json`.
200,000-draw Monte Carlo over the assumption ranges, seed 0. **Every input is ASSUMED.** Regulatory figures (UN GTR 22 /
Euro 7: 80 % certified energy at 5 years / 100,000 km) are from memory and must be verified before citing.

Pack: 75 kWh usable in every case, $90–140/kWh. Results are p10 / p50 / p90.

## C1 — "1 °C cooler charging is worth ~$100"

Mechanism: Arrhenius fade (Ea 30–65 kJ/mol) on the share of lifetime fade driven by charging heat (15–60 %), at a
charge temperature of 35–55 °C. One kelvin saves **0.2 / 0.4 / 0.8 % of capacity** over the durability window.

| Channel | $ per kelvin |
|---|---|
| Fewer cells, **if durability (not range) sizes the pack** | 24 / **55** / 118 |
| Lower expected capacity-warranty cost | 1 / 2.5 / 7 |
| **Total** | 26 / **58** / 124 |

**$100 sits at about the 75th percentile.** 59 % of draws fall between $50 and $200. Plausible, at the optimistic end,
and it only pays in full if the durability floor, rather than range, sets the pack size.

## C2 — "20 % reserve down to 5 %", two readings

| Reading | What it requires | Value |
|---|---|---|
| **A. An uncertainty reserve** (energy held back because the weakest cell's remaining energy is not known precisely) | ~4× better state estimation | **14.8 kWh of cells avoided: $1,400 / $1,700 / $2,000**. Halfway (20 → 10 %): ~$1,200 |
| **B. A durability reserve** (hidden energy released over life to stay above the 80 % floor) | Lifetime fade cut ~4× | **Not reachable by temperature.** Even 15 K cooler cuts fade only ~21 % (median); 25 K cooler, ~29 %. Cooling can only shrink the heat-driven share. |

## C3 — "two ECUs removed"

Silicon, PCB, housing, assembly, harness and amortised engineering per ECU, plus the mass effect on pack size:
**$132 / $148 / $165 per vehicle.** Mass is a small part of it (~$4). This number needs no battery theory.

## Do the three claims hang together?

Yes, if C2 means reading A.

- **C2A is the big one: ~$1,700**, an order of magnitude larger than either of the others. It is a **state-estimation**
  problem, not an efficiency problem: knowing each pack's true usable energy, down to the weakest cell, well enough
  to release reserve safely.
- **C1 (~$60, up to ~$120) and C3 (~$150)** are real but small next to it.
- **C2B cannot come from cooling.** If a claimed 20 % → 5 % reduction means the durability reserve, it needs a degradation
  mechanism far stronger than charging temperature.

## What it does not show

- That any controller achieves the 4× precision gain C2A needs. That is the open technical question.
- Real ageing parameters for any specific cell; the ranges are literature-typical.
- Regulatory detail; verify GTR 22 / Euro 7 and any Chinese equivalent before citing.
