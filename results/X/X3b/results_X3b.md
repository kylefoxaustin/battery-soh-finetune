# Results X3-b: neighbour-referenced per-cell drift, and a false-alarm rate on a healthy fleet

Experiment X3-b, run 2026-10-16.

- **Pre-registration:** [`../X3b_preregistration.md`](../X3b_preregistration.md), commit `ea9f714`. It was committed
  before any X3-b code existed.
- **Code:** `analysis/X3b_neighbour.py`, which imports X3's z, slope and flag rules. Outputs: `x3b.json` and
  `x3b_changan_per_vehicle.json`.
- **Tags:** all results are **DERIVED**. Licences: Changan CC BY-NC-SA 4.0 (non-commercial), BatICM MIT. No p-values.
- **Consistency check:** for A, the code reproduces X3 exactly. On car2: first correct flag at day 9.3, 78 false
  flags, +15.4 days of lead.

## Verdict (pre-registered primary, §4)

**NO REDUCTION. Neighbour referencing doubles the false-alarm rate.** The bigger finding is that **X3's flag rule
itself is not usable as a monitor.**

Healthy control: 250 Changan vehicles with zero F event days, 191,396 valid vehicle-days.

| Feature | False-alarm episodes per 100 vehicle-days | Vehicles with ≥ 1 |
|---|---|---|
| A (X3, pack-wide slope z) | **21.8** | 100 % |
| A_lvl (X3, level) | 13.4 | 100 % |
| **A_nb (neighbour-referenced slope, primary)** | **43.5** | 100 % |
| A_nb_lvl | 25.7 | 100 % |
| A_mod (regular block geometry, non-causal) | 36.7 | 100 % |

- The A_nb / A ratio is **2.00**, vehicle-bootstrap interval 1.91–2.10. "Reduces" needed ≤ 0.5 with the interval
  below 1.
- The usability bar (≤ 1 per 100 vehicle-days, ASSUMED) **fails for every feature**, by a factor of 13 to 44.
- 21.8 per 100 vehicle-days is about **80 false episodes per vehicle-year** for X3's own rule.
- Context, not positives: F's 50 event vehicles show A at 31.1 and A_nb at 52.6.

## Why (descriptive)

**1. Changan's false alarms are mostly single cells, not module blocks.**

- For A, the episode-size histogram is 11,172 singles, then 3,098 pairs, then 1,293 triples, falling away from there.
- So the car2 module-block pattern that motivated the fix is **not** what drives false alarms in a healthy fleet.

**2. Neighbour referencing removes shared variation, so the robust spread (MAD) shrinks.**

- Each cell's own noise then stands out more, and a fixed z of −3.5 is crossed more often.
- A fixed robust-z threshold over 96 cells, evaluated daily, has no false-alarm control. Its alarm rate depends on the
  tail shape of the cross-cell distribution, which this fix makes heavier.

## BatICM cars 2–4 (POST-HOC, descriptive; the fix was designed on car2)

| Case | Feature | First correct | First flag correct? | False flags before / total | Lead vs level 3 |
|---|---|---|---|---|---|
| car2 (#83) | A | day 9.3 | No (cell 87) | 1 / 78 | +15.4 d |
| | **A_nb** | **day 7.3** | No (cell 87) | 1 / **16** | +17.4 d |
| | A_nb_lvl | day 3.3 | **Yes, untied** | 0 / 28 | +21.4 d |
| car3 (#3, #82) | A | day 13.2 | Yes (tied) | 0 / 3 | −8.3 d |
| | **A_nb** | **day 5.2** | Yes (tied, with cell 49) | 0 / 3 | −0.3 d |
| car4 (#64) | A | never | — | 0 / 0 | — |
| | A_nb | never | — | 9 / 9 | — |
| | A_lvl | day 34.6 | No | 1 / 1 | +49.9 d |

- Detection is **retained** in the pre-registered sense: A_nb flags the faulty cell in 2 of 3 cars, as A does.
- On the case that inspired it, A_nb **looked like a clear improvement**: 5× fewer false flags in car2, and 2 and 8
  days earlier in car2 and car3. **The independent healthy-fleet control reverses that.**
- This is why the pre-registration put the decision on the control and kept BatICM descriptive.

## What this does and does not show

**Does:**

- On a 250-vehicle healthy fleet, **pack-wide robust-z drift flags raise about one false episode every 5 days per
  vehicle**.
- Neighbour or module referencing makes that worse, not better.
- X3's "weeks of lead over min/max" therefore came with a false-alarm rate that makes the comparison unfair to
  min/max, which almost never fires.

**Does not:**

- Rule out per-cell drift as a signal. It rules out this **threshold rule**.
- A usable monitor needs a false-alarm budget calibrated on healthy vehicles. One option is a per-vehicle threshold
  set from the vehicle's own history at a target rate of, for example, 1 per 100 vehicle-days. That would then be
  tested for lead time on located faults.
- The fleet data says the rate must fall about 20-fold for the X3 lead times to mean anything.
- That calibration is a new pre-registration, not done here.

## Deviations

None after `ea9f714`.

**Implementation choices:**

- BatICM block geometry uses daily rest deviations with ≥ 20 rest frames per day (F's MIN_REST), and needs ≥ 5 such
  days.
- Changan geometry needs ≥ 30 days.
- Evaluations are daily, ending at 24 h multiples of record time. Changan timestamps are re-based per vehicle (F
  gotcha).
