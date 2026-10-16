# Experiment H2 — pre-registration: H re-run on a 3,564-cell LFP grid battery (Weihai BESS)

**What H2 is.** H2 re-runs Experiment H-a (counterfactual per-cell vs min/max vs pack-mean charge limiting; the
original was pre-registered in `43485e8`) on a different system:

- a **different chemistry (LFP)**;
- a **4× larger string (396 cells per rack)**;
- a **winter-inclusive climate**.

There is also an optional board part, H2-b. Kyle approved the run on 2026-10-15 ("Yeah lets rerun H").

This file is committed **before** `analysis/H2_replay.py` exists, and before any limiter quantity, charge-session
temperature distribution or per-cell spread has been computed for this dataset.

**Tags:** MEASURED / DERIVED / ASSUMED / SOURCED, as in H. Every H2-a number is **DERIVED** and every limit is
**ASSUMED**. No regulatory, economic or real charge-rate claim will be made.

## 0. Data, and what has already been seen (disclosure)

**Dataset.** Qu et al. (SJTU), *A Multi-Agent AI Framework for Explainable Battery System Maintenance*, Zenodo
20094787, **CC BY 4.0**. It contains 8 monthly MATLAB v7.3 files (Oct 2024 – May 2025), all md5-verified.

**Structure, decoded.**

- **Operations.** Each operation is one charge or discharge of the whole cluster, with fields `Type`, `StartTime`,
  `EndTime` and `CurrentMean`.
- **Racks.** Each of the 9 racks has 396 `Voltage<k>` and 216 `Temperature<k>` series.
- **Sensor series.** Each series is `{t, value}`, change-logged with its own timestamps.
  - Voltages are in V at 1 mV resolution.
  - Temperatures are integer °C.
- **Rack signals.** Each rack also has `Current`, `Voltage`, `SOC` and `Power` series with their own timestamps.
  Current is about 1.3 s apart; charge is negative.
- **Timestamps.** These are MATLAB datetime objects, decoded with our own MCOS reader (`mcos_dt`): each is an object
  id that maps to a FileWrapper cell holding ms since 1970.
  - Validation: for every series checked, the decoded timestamp count equals the value count, and the times are
    monotone.
  - A third-party reader (mat-io 0.4.2, patched) gave up after 25 minutes; it was not used.

**Seen before this commit:**

- the operation census: **217 Charge** (median 2.28 h, median CurrentMean −104.6 A) and **227 Discharge**
  operations; all have 9 racks with 396 V and 216 T series;
- the raw first values of a few series in Operation 1 of October 2024: rack 1 temperatures were 19–27 °C, cell
  voltages 3.17–3.23 V at the start.

## 1. H2-a — counterfactual replay (every number DERIVED; every limit ASSUMED)

### Sessions and frames

**Session.** One rack during one `Charge` operation. That gives up to 217 × 9 = 1,953 sessions. Each rack is
controlled as its own string; the racks sit in parallel.

**Frame grid.** Every **10 s** from StartTime to EndTime.

- At each grid time, every cell voltage and probe temperature is its **most recent logged value** (zero-order
  hold). This is ASSUMED to match change-logging with a deadband.
- A grid frame is used only after every one of the 396 + 216 series has logged at least once in the operation.
- A session is used if it has ≥ 30 frames.

**Charge per frame.** `dAh` is the integral of rack charging current (−I, clipped at ≥ 0) over the 10 s interval,
using trapezoids on the rack-current samples. Any gap > 60 s between current samples contributes 0.

### Limit map (ASSUMED; generic LFP shape, not the operator's real map)

`C(V, T) = C_T(T) · taper(V)`.

- **`C_T`** is the **same points as H**: (−20, 0.05), (0, 0.2), (10, 0.6), (25, 1.5), (40, 1.5), (50, 0.8), (60, 0.0),
  linearly interpolated and clamped. Keeping H's map keeps the two runs comparable.
  - It is an ASSUMED placeholder for LFP too.
  - Because only *ratios* of charge time are reported, the absolute C scale does not matter. Only the shape does.
- **`taper(V)`** is LFP-specific, and is a function of **cell voltage**, not SOC. LFP's flat plateau makes
  voltage→SOC ill-posed, and real LFP charge tapers are voltage-driven.
  - 1.0 for V ≤ **3.40 V**;
  - then linear down to 0.05 at **3.60 V**;
  - and 0 at ≥ 3.65 V (the cell limit).

**Predicted consequence (stated before running).** As in H §0.2, when the voltage taper binds, min/max (reading
`vmax`) matches per-cell exactly. **Any per-cell gain over min/max must come from temperature coupling**, meaning a
cell whose own probe is colder or hotter than the pack extremes would suggest at that cell's voltage.

### Cell-to-probe mapping (ASSUMED; not published)

The paper's rack has 9 modules × 44 cells and 216 probes, which is 24 per module.

- **M1 (contiguous):** probe(k) = ⌊k · 216 / 396⌋ for cell k = 0..395, in series-number order.
- **M2:** 100 random permutations of the M1 assignment (seeds 0–99), as in H.

### The three limiters, per frame (per rack)

| Limiter | Definition |
|---|---|
| **L_cell** (per-cell) | min over k of `C_T(T_probe(k)) · taper(V_k)` |
| **L_mm** (min/max) | `min(C_T(Tmin), C_T(Tmax)) · taper(Vmax)`, with the extremes taken from the cell/probe lists |
| **L_pack(m, mT)** (pack-mean with margins) | `min(C_T(Tmean − mT), C_T(Tmean + mT)) · taper(Vmean + m)` |

Margins swept: m ∈ {0, 5, 10, 20, 30, 50, 75, 100} mV and mT ∈ {0, 2, 5, 10} °C.

### Time-to-charge and saving

- The charge time a limiter allows is `t = Σ dAh / max(L, 1e-6)` over the session.
- **Saving of per-cell over min/max:** `S_mm = 1 − t_cell / t_mm`.
- **Saving of per-cell over pack-mean:** `S_pack = 1 − t_cell / t_pack`.
- Sessions delivering < 0.5 Ah are skipped.

### PRIMARY decision (same rule as H)

| Verdict | Condition |
|---|---|
| **NO BENEFIT over min/max** | Median session `S_mm` < 1 % under M1 **and** the median of per-permutation medians < 1 % under M2 |
| **PER-CELL RECOVERS X** | Both ≥ 1 %, **and** the M1 bootstrap CI lower bound > 0 |
| **NOT ANSWERABLE from replay (mapping-dependent)** | Otherwise |

**Uncertainty.** A bootstrap CI (1,000 resamples, seed 0) on the M1 median, resampling **operations** with all of
their racks together, since racks share weather and current.

### Pre-registered secondary analyses

These were post-hoc in H; here they are fixed in advance.

1. **Temperature bands.** Median and p90 `S_mm` by the session's median coldest probe: < 10, 10–20, 20–25, 25–40,
   ≥ 40 °C, with the session count in each. This is H's open question: does the per-cell gain appear in cold
   weather?
2. **Tie-aware constraining-cell controls,** as in H:
   - the fraction of frames where the max-V cell is not among the constraining cells;
   - the same for the min-V cell;
   - the fraction where no cell on an extreme-temperature probe is constraining;
   - the fraction where L_cell ≠ L_mm.
3. **Margin sweep:** the median `S_pack` and the unsafe fraction (L_pack > 1.001 · L_cell) for each (m, mT). Report
   the smallest margins with ≤ 0.1 % unsafe frames.
4. **Sensitivity (M1 median `S_mm`):**
   - temperature breakpoints shifted −5 °C and +5 °C;
   - taper knee at 3.35 V and at 3.45 V.
5. **Temperature description.** The charging distributions of per-rack probe spread, coldest probe and hottest probe.

## 2. H2-b — board footprint at real geometry (MEASURED; optional; only if the board can be hard-reserved)

**What it measures.** Rerun `board/h_limiter.c` at:

- **N = 396 cells / P = 216 probes**, using the real per-rack geometry and real Weihai frames;
- **N = 3,564 / P = 1,944**, the whole cluster as one limiter, from 9 racks' frames concatenated.

**Code change.** The probe index is generalised from `k/3` to `⌊k·P/N⌋`, in both the C code and the Python
reference.

**Procedure.** Hard reservation, census before and after, model check, 5 repeats, gate. This is H's procedure and
H's gate: argmin tie-aware 100 %, setpoint error ≤ 1e-4 C, R error ≤ 1e-3.

**Frames.** The first 10,000 grid frames of charge operations, round-robin across racks and operations.

## 3. Deviations policy

Any change after this commit is listed in the results as a numbered deviation, with the reason. Thresholds will not
change after results are seen.

**Licence.** Weihai is CC BY 4.0, so H2 results are **not** non-commercial-restricted, unlike H.
