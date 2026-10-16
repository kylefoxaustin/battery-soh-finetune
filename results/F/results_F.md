# Results F — does per-cell data catch a failing cell early, beyond min/max?

Experiment F, run 2026-10-13.

- Pre-registration: [`F_preregistration.md`](F_preregistration.md), commit `2b9e629`, committed before any analysis code
  existed.
- Code: `analysis/F_faults.py` (pre-registered analysis) and `analysis/F_diag.py` (**post-hoc** diagnostics).
- Changan 300-EV fleet. **CC BY-NC-SA 4.0 — every result here is non-commercial only.**
- No ground truth exists: the release has no fault codes or service records, and pack voltage is just the cell sum.
  **Nothing here shows that any event is a real cell fault.**

## Verdict

**The primary forecast test is UNDERPOWERED.** Only 3 vehicles develop their first anomaly after a clean first
half, against a pre-registered floor of 8, so the "catch it early" claim cannot be tested on this fleet.

On *detection*, a scalar min/max monitor sees **98 %** of the anomaly-days that full per-cell data sees.

What per-cell data adds here is **diagnosis**, which min/max cannot give:

- which cell is affected;
- whether its neighbour moves (a sense-tap signature);
- whether a whole module shifts;
- whether the deviation behaves like a real state-of-charge offset.

## 1. Event catalogue (MEASURED; `events.json`)

An *event-day* is a day on which one cell's daily mean deviation at rest is below −60 mV. A *qualifying event* is a
run of at least 3 event-days on the same cell.

| | Count |
|---|---|
| Vehicles analysed | 300 |
| Vehicles with ≥ 1 event-day | 50 |
| Vehicles with a qualifying event | **20** |
| Qualifying events | 41 (out of 232 runs of any length) |
| …recovered (pre-registered rule) | 41 / 41 — uninformative; see deviations |
| …abrupt recovery (≤ 3 days back above −30 mV) | **7** (vin93, 114, 116, 120, 139, 161, 169) |

How the 41 qualifying events are spread across vehicles:

- **vin272 accounts for 11 of them** (corrected from 12 on 2026-10-15; `events.json`), on cells 31–51 — a block
  with gaps (31, 32, 34, 37, 39, 40 ×2, 41, 42, 49, 51). A whole-module drift looks more likely
  than 12 independent cell faults.
- In **vin162**, cells 41–43 all fell together (−35 to −52 mV), again a module-level shift.
- The deepest events are vin120 cell 47 (−774 mV on its worst day, −382 mV median shift), vin277 cell 31 (−389 mV),
  vin19 cell 31 (−380 mV), vin50 cell 31 (−263 mV) and vin116 cell 21 (−258 mV).

## 2. Physics classification (DERIVED — evidence, not ground truth)

| Class (pre-registered rules) | Events |
|---|---|
| SOC-like (fits a constant state-of-charge offset through the OCV curve ≥ 2× better than a constant mV offset) | 23 |
| Offset-like (constant mV fits ≥ 2× better — sensor-like) | 2 (vin19 cell 31, vin50 cell 31) |
| Tap-fault-like (a neighbour rises ≥ 0.5× the cell's drop) | 4 — **only 1 convincing**, see below |
| Unresolved | 12 (including vin120 cell 47) |

**Reading the classes:**

- **Tap signature.** vin116 cell 21 is a clean case: −195 mV, with neighbours at +116 and +57 mV. That is what a
  shared sense-tap fault looks like, and min/max data could not show it. The other 3 tap flags (vin266/76,
  vin272/40, vin272/41) are artefacts. Their own shift against baseline is only 5–11 mV, so the ratio blows up. The
  pre-registered rule had no minimum-shift floor; this is reported as-is and flagged.
- **SOC-like events** mostly fit offsets of δ ≈ 6–12 % SOC. That is consistent with a real cell sitting at a lower
  state of charge, not a sensor offset. **Caveat:** event-days are selected because they cross −60 mV, which
  favours low-SOC rest days, where the OCV curve is steep. That selection pushes toward "SOC-like".
- **Offset-like:** both cases are cell 31, and both onsets fall at about day 356–362 of each vehicle's record. A
  constant offset that doesn't follow SOC is sensor-like. vin277's −389 mV event is also on cell 31 (unresolved).
  Post-hoc, the chance that any single cell index shows up as the deepest cell in ≥ 3 of 20 vehicles is
  **p = 0.10**. That is suggestive, not significant.
- **vin120 cell 47:** neither model wins (unresolved). Its neighbours stayed within 2–4 mV against a 382 mV drop,
  so it is not tap-like. It recovered abruptly, which fits an intervention.
- **Current dependence (2c)** is reported per event in `events.json`. Changes in apparent resistance are
  at most 0.42 mΩ (vin277), with no outlier.

## 3. Detection: per-cell vs min/max-only (MEASURED; `agreement.json`)

| | |
|---|---|
| Per-cell event-days also flagged by min-only (`vmin − V/96`) | **97.9 %** (715 / 730) |
| Min-only event-days also flagged by per-cell | 98.9 % (715 / 723) |
| Vehicles with a qualifying event: per-cell / min-only / both | 20 / 25 / 19 |

Min-only flags 6 extra vehicles. The slim files keep frames that the per-cell extraction dropped as malformed or
desynced, so those 6 may be partly data defects. **For detecting that something is wrong, min/max telemetry is
essentially sufficient.**

## 4. PRIMARY — forecast (DERIVED; `forecast.json`)

The test computes features on the first half of each vehicle's valid days and asks whether they separate vehicles
whose first anomaly comes in the second half from vehicles that never have one.

| | |
|---|---|
| Eligible vehicles (≥ 120 valid days) | 298 |
| Positives / negatives / excluded | **3** / 248 / 47 (the excluded already had event-days in the first half) |
| AUC, per-cell drift feature A | 0.31 [0.03, 0.71] |
| AUC, min-only drift feature B | 0.35 [0.03, 0.78] |
| A − B | −0.04 [−0.19, +0.14] |
| **Decision** | **UNDERPOWERED** (< 8 positives) — descriptive only |

Most anomalous vehicles already show their anomaly early in their records, so almost none are "new" in the second
half. On 3 positives the numbers mean nothing, and no claim is made in either direction.

## 5. Secondary — capacity labels around onset (DERIVED labels; `consequence.json`, `diag.json`)

**Pre-registered prediction: null.** Labels are built from charge up to the *max* cell, so a low cell should barely
affect them.

**Observed: the opposite.** Labels in the 180 days after onset sit higher than in the 180 days before:

| Analysis | Event Δ | Placebo Δ | p |
|---|---|---|---|
| Pre-registered, per event | +3.6 Ah median (18 events) | −1.5 Ah (185 vehicles) | Mann–Whitney 2e-6 |
| Post-hoc, one value per vehicle, age-matched placebo | +4.4 Ah median excess (6 vehicles) | same-age placebo from every negative vehicle | Wilcoxon 0.031 |

- **The pre-registered p-value is not valid.** The 18 events come from only 7 vehicles (vin272 contributes 7 and
  vin93 contributes 5), so they are not independent.
- **The post-hoc analysis holds.** All 6 vehicles are above their same-age placebo median. p = 0.031 is the smallest
  value attainable with n = 6.
- **The mechanism is unknown.** It is not seasonal at any detectable level: event-days are a median 1.7 °C colder
  than other days (13 of 20 vehicles colder).
- **One possibility, untestable here:** vin116, 120 and 169 have the largest rises and abrupt recoveries. A service
  visit that recalibrated the BMS or changed hardware would move the charge-based labels.
- **This is a post-hoc, small-n observation, not a finding.**

## 6. Deviations and disclosures

- **"Recovered" (41 / 41)** is uninformative. The rule counts any 7 later days above −30 mV, including days between
  repeated runs. "Abrupt" is the useful flag.
- **Tap rule:** it has no minimum-shift floor, which produced 3 artefact flags (§2). Not re-tuned.
- **Clocks are per-vehicle.** Timestamps are re-based so each vehicle starts at day 0. "Onset day" is vehicle age,
  not a calendar date, so season and fleet-wide calendar effects cannot be separated. The diagnostic placebo is
  age-matched, not date-matched.
- **Open implementation choices** are marked OPEN-1 to OPEN-4 in `F_faults.py`. They cover the SOC span reading, SOC
  clipping, which days count for agreement, and merging ties in the OCV table.
- **Post-hoc material** in `F_diag.py` changes no pre-registered decision.
- **Seen before pre-registration:** the fleet-level counts and vin120 (pre-registration §0).

## Honest verdict

On this fleet, full per-cell telemetry does **not** detect anomalies that min/max misses: 98 % of anomaly-days
overlap. Whether it gives *earlier warning* cannot be tested: anomalies are rare (20 of 300 vehicles), and most are
already present early in the record, which leaves 3 testable vehicles.

What per-cell data demonstrably adds is **diagnosis**:

- one clean sense-tap signature (vin116 cell 21);
- two sensor-like constant offsets on the same cell index in different vehicles;
- module-wide shifts (vin272, vin162);
- most events behaving like real state-of-charge offsets of about 6–12 %.

Separately, the capacity-label rise after events (post-hoc, 6 vehicles) contradicts my pre-registered prediction
and is unexplained.

Without fault codes or service records, none of these classes can be confirmed. A dataset that pairs per-cell
telemetry with service or teardown records would turn this from suggestive to testable.

**Licence:** non-commercial only (CC BY-NC-SA 4.0). **No regulatory or economic consequence is claimed or implied.**

## Post-review addendum (2026-10-15, independent review)

See [`review_2026-10-15/REVIEW.md`](../review_2026-10-15/REVIEW.md). The original text above is unchanged except where marked.

1. **The 98 % detection overlap is close to an identity, not evidence.** If one cell's daily mean deviation is below
   −60 mV, then the daily mean of (vmin − pack mean) must be too. On identical frames the overlap is 100 % (730 of
   730, reviewer recomputation). The remaining ~2 % came only from differences between the scalar and per-cell
   frame sets. So §3 did not test whether min/max is sufficient for detection.
2. **A per-cell-only detector does find things min/max cannot** (post-hoc, reviewer). It flags drift against each
   cell's own baseline (< −30 mV for ≥ 3 days):
   - 23 vehicles and 76 cells are flagged;
   - 40 cells in 5 vehicles are silent to min/max, including vin272's block, vin23 cells 28/30/31 and vin158 cell
     89.
   This needs a pre-registered test.
3. **The §5 label-rise observation is withdrawn.**
   - It used all labels, including slow-charge labels, which sit about 6.8 Ah above the fast-charge trend.
   - vin116 changed charger current.
   - On the 48–51 A band: n = 5, +2.4 Ah, p = 0.062.
4. **The "SOC-like" class is not independent evidence.** It relies on the ASSUMED BMS-SOC-indexed OCV table.
5. **22 of the 41 events are chronic cells crossing the fixed threshold** (own shift > −30 mV), not onsets.
6. **Cell 31 recurs more than chance allows.** Counting any qualifying event, it appears in 4 of 20 vehicles
   (look-elsewhere-corrected P ≈ 0.021, reviewer). That supports a sense-channel / connector hypothesis.
