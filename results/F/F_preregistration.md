# Experiment F — pre-registration: does per-cell data catch a failing cell early, beyond min/max?

Committed **before** `analysis/F_faults.py` exists and before any event catalogue, classification, label join or
first-half/second-half split has been computed. The single exception is disclosed in §0.

Data: Changan 300-EV fleet per-cell extraction (`data/changan/cells/vinN.npz`, built for Experiment E), the scalar
slim files (`data/changan/slim`), and the DERIVED capacity labels (`data/changan/labels_full`). **CC BY-NC-SA 4.0 —
every result here is non-commercial only.** Tags as in Experiment E: MEASURED / DERIVED / ASSUMED / UNGATED / SOURCED.
No regulatory or economic claim will be made.

## 0. What has already been seen (disclosure)

During Experiment E, an **exploratory** scan (`scratchpad/scan.py`, not committed, not a test) computed per-vehicle
summaries of the daily rest per-cell mean deviation:

- 50 vehicles have ≥ 1 day where the weakest cell is below −60 mV; 21 below −100 mV; 11 have ≥ 10 such days.
- The worst cell's early→late drift has a median of −10 mV and a minimum of −30 mV.
- I looked at vin120 by hand: cell index 47 sat about −430 mV for 51 days (27.8–38.4 k km), then went back to
  about −3 mV. I also looked at that vehicle's pack voltage against the sum of its cells.
- Fleet-wide: `totalvoltage` equals the 96-cell sum truncated to 0.1 V in 99.6 % of frames, so it is **not** an
  independent check on the cell voltages.

The −60 mV threshold below was chosen *after* seeing those counts. Its rationale: the fleet's median weakest cell sits
at −19 mV, the cross-cell SD is 4 mV (Experiment E), and −60 mV is about 10 SD beyond the typical weakest cell. No
neighbour-cell, SOC-dependence, current-dependence, label, or first-half/second-half quantity has been looked at for
any vehicle.

## 1. The core limitation, stated up front

The release has **no fault codes, service records or teardown results**, and pack voltage is the cell sum. **No
result here can confirm that any event is a real cell fault.** F therefore measures three things:

- **(a)** what the per-cell anomalies are, and how often they occur;
- **(b)** whether each anomaly's *own physics* looks like a real cell or like a voltage-sensing fault;
- **(c)** whether per-cell data **forecasts** those anomalies better than a scalar min/max-only monitor does.

"Fault detection rate" and "false-alarm rate" in the ground-truth sense are **not measurable** and will not be reported.

## 2. Definitions (fixed)

- **Rest full vector:** a per-cell vector (`dv_full`, mV deviation from the pack mean) whose timestamp matches a
  summary frame with |I| < 1 A.
- **Valid day:** a calendar day (UTC, `t // 86400`) with ≥ 20 rest full vectors. The daily per-cell value is the
  mean of `dv_full` over that day's rest vectors.
- **Event-day (cell k):** a valid day on which cell k's daily value is < −60 mV.
- **Event:** a maximal run of event-days for the *same* cell, where consecutive event-days are ≤ 14 calendar days
  apart.
  - **Qualifying event:** an event with ≥ 3 event-days.
  - **Onset:** the first event-day. **End:** the last event-day. **Depth:** the minimum daily value.
  - Onset and end odometer are also recorded.
- **Recovered:** after the end, the same cell has ≥ 7 valid days with a daily value > −30 mV before the data ends.
  - **Abrupt recovery:** recovered, *and* the first valid day after the end is already > −30 mV, *and* it is
    ≤ 3 calendar days after the end.
  - Rationale: closing a gap of more than 60 mV takes tens of Ah. Passive balancing at around 0.1 A cannot do that
    in 3 days. An abrupt recovery therefore points to an intervention — a repair, a replacement, or a sensor fix —
    rather than to balancing.

## 3. Step 1 — event catalogue (descriptive, MEASURED)

For every vehicle and every qualifying event, record: vehicle, cell index, onset/end date and km, number of
event-days, duration, depth, whether it recovered, and whether the recovery was abrupt. Also report fleet counts.

Rest frames are synced frames only (forced by the 1.2 % desync found in Experiment E). Malformed frames are already
excluded by the extraction.

## 4. Step 2 — physics classification of each qualifying event (DERIVED; evidence, not ground truth)

Each test below is computed per qualifying event.

**2a. Shared-tap signature.** Adjacent cells share a voltage-sense tap. A tap fault (resistance or offset) pulls
cell k low *and* pushes a neighbour high by about the same amount, and the sum is preserved. A real low cell moves
only itself; the neighbours rise by about 1/96 of its drop, through the pack mean.

- **Baseline:** the 30 valid days before onset. If fewer than 10 are available, use the 30 valid days after the end.
  If there are still fewer than 10, the event is **"no baseline"**.
- `shift_j` = median daily value of cell j over the event-days − median over the baseline days, for j ∈ {k−1, k, k+1}
  (indices in the list order, 0..95).
- `comp = max(shift_{k−1}, shift_{k+1}) / (−shift_k)`.
- **Tap-fault-like** if `comp ≥ 0.5`.
- ASSUMED: list order equals the physical series order. If it does not, this test returns ≈ 0 everywhere and
  cannot flag anything. That outcome will be reported as "uninformative", not as "no tap faults".

**2b. SOC dependence.** A real cell at a different state of charge deviates by `OCV(s − δ) − OCV(s)`. That amount
varies with pack SOC s, because the OCV slope varies. A sensor offset is constant.

- **OCV curve:** the ASSUMED `ocv_full.json` table (cell voltage vs BMS SOC at wake). It is made monotone with a
  running maximum and linearly extrapolated beyond its ends using the slope of its last 5 points at each end.
- **SOC of a frame:** pack SOC is read from the summary frame's `vmean_mv` through the inverse table.
- **Binning:** the event-day rest vectors are binned by s into 5 % bins. A bin is kept if it has ≥ 20 vectors; the
  value used is the median of cell k's `dv` in that bin.
- **Two models are fitted to the bin medians:**
  - **M_off:** dv = c (least squares).
  - **M_soc:** dv = OCV(s − δ) − OCV(s), with δ ∈ [−80, 80] % in 0.25 % steps.
- **Classification:**
  - **SOC-like (cell-like)** if SSE_soc ≤ 0.5 · SSE_off.
  - **Offset-like (sensor-like)** if SSE_off ≤ 0.5 · SSE_soc.
  - **Unresolved** otherwise, or if there are < 4 kept bins, or if the bins span < 30 % SOC.
- If 2a says tap-fault-like, the final class is **tap-fault-like** regardless of 2b.

**2c. Current dependence (attribute, not a class).** Over driving full vectors (|I| ≥ 10 A), take the OLS slope of
cell k's dv on I, separately on event-days and on baseline days.

- Report `ΔR = slope_event − slope_baseline` in mΩ.
- A large ΔR fits either a high-resistance cell or a resistive sense connection. **It cannot separate the two**, so
  it is reported only.

## 5. Step 3+4 — PRIMARY test: does per-cell data forecast a later event better than min/max-only?

This is the "catch it early" claim, and it is the experiment's one decision.

**Split.** For each vehicle with ≥ 120 valid days, F = the valid days up to and including the median valid day,
and S = the rest. "Days" means valid days in both definitions, so F and S hold the same number of valid days.

**Groups.**

| Group | Definition |
|---|---|
| **Positive** | ≥ 1 qualifying event with onset in S, **and** no event-day (any cell) in F |
| **Negative** | no event-day (any cell) in F or S |
| **Excluded** | everything else: event-days in F (already flagged by any monitor), or only non-qualifying event-days in S |

**Features** (computed on F only):

- **A (per-cell):** for each cell, the OLS slope of its daily value vs day number over F. Take the robust z of each
  slope against the vehicle's 96 slopes, `z = (slope − median) / (1.4826 · MAD)`. Then **A = −min z**: a cell drifting
  down relative to its siblings scores high, whether or not it is currently the minimum.
- **B (min/max-only):** from the slim files (every frame, no cell list needed), the daily mean over rest frames
  (|I| < 1 A, ≥ 20 per day) of `vmin − V/96`, in mV. Then **B = −(OLS slope over the same F days)**.
  - V is the cell sum truncated to 0.1 V, so V/96 is within 1.04 mV of the cell mean.
  - B is what a scalar BMS monitor could compute.

**Metric.** AUC of A, and AUC of B, for positives vs negatives. Uncertainty comes from a 2,000-resample vehicle
bootstrap, stratified by group, giving 95 % percentile CIs for AUC_A, AUC_B and AUC_A − AUC_B. Seed 0.

**Power gate.** If there are < 8 positives, the test is **UNDERPOWERED**: report the numbers descriptively and draw
no conclusion. With 8 positives, the AUC SE is about 0.09–0.10, so only a large effect could be resolved; this is
stated now.

**Decision (one test, α = 0.05).**

| Outcome | Condition |
|---|---|
| **Per-cell early warning SUPPORTED** | AUC_A ≥ 0.70 **and** AUC_A's CI lower bound > 0.5 **and** (AUC_A − AUC_B)'s CI lower bound > 0 |
| **Early warning exists but per-cell adds nothing resolvable over min/max** | AUC_A's CI lower bound > 0.5 but the difference CI includes 0 |
| **NOT SUPPORTED** | AUC_A's CI includes 0.5 |

**My prior, stated before running:** I expect AUC_A ≈ AUC_B. The drifting cell is usually already the minimum, so
min/max should see most of what per-cell data sees.

## 6. Step 4b — detector agreement (descriptive, MEASURED)

On all vehicles, define a **min-only event-day** as a valid slim day whose daily rest mean of `vmin − V/96` is
< −60 mV. Report:

- the fraction of per-cell event-days that are also min-only event-days;
- the reverse fraction;
- vehicle-level agreement on "has ≥ 1 qualifying event", with the min-only analogue: ≥ 3 min-only event-days with
  gaps ≤ 14 days.

What per-cell data adds that min/max cannot, by construction:

- **cell identity** (min/max gives only an index, and only if one is logged);
- the **tap signature** of §4 2a, which needs the neighbour's value;
- **cells drifting while not the minimum** — feature A.

## 7. Secondary consequence check (descriptive, predicted null)

For each qualifying event with ≥ 2 labels within the 180 days before onset and ≥ 2 within the 180 days after onset:

- Δ = median label after − median label before (Ah).
- **Placebo:** negative vehicles, with pseudo-onset at their median valid day and the same rule.
- Report a Mann–Whitney two-sided p.

Predicted null: the labels are built from charge to *max* cell ≥ 4.2 V (`data/changan_labels.py`), so a cell that is
low at rest barely enters them. A null here does **not** show that the events are harmless.

## 8. What will NOT be done

- No detection-rate or false-alarm-rate claim.
- No claim that any event is a real fault.
- No i.MX95 footprint measurement in this pass (optional step 5; it needs a board reservation).
- No threshold tuning after the run. If a definition turns out unworkable (for example, a crash), the change and its
  reason are logged in the results as a deviation.

## 9. Outputs

| Output | Contents |
|---|---|
| `analysis/F_faults.py` → `results/F/events.json` | catalogue + classes |
| `results/F/forecast.json` | primary test |
| `results/F/agreement.json` | detector agreement |
| `results/F/consequence.json` | secondary consequence check |
| `results/F/results_F.md` | write-up |
