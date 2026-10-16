# Experiment H — pre-registration: per-cell limit enforcement vs pack-scalar and min/max limiting

Brief: [`Experiment G and H Brief.md`](../../Experiment%20G%20and%20H%20Brief.md), Experiment H.

This file is committed **before** `analysis/H_replay.py` or `board/h_limiter.c` exists, and before any charge-session
current or temperature distribution has been looked at for H.

Data and licence:

- **H-a** runs on the Changan per-cell extraction (`data/changan/cells`). **CC BY-NC-SA 4.0 — non-commercial only.**
- **H-b** runs on the board. Its latency and memory figures are MEASURED and do not depend on Changan. However, its
  correctness gate replays Changan frames, so the gate inherits that licence.

No regulatory, economic or real charge-rate claim will be made. The brief's own warning applies to every H-a number:
H-a measures what a *limiter would have allowed* on recorded cell states. It does not measure what a pack could
safely take.

## 0. Corrections to the brief, and what is known in advance

**1. Which cell constrains charging.** The brief's control asks whether the constraining cell is "not the
min-voltage cell". During **charging** it is the **max**-voltage cell that reaches the upper voltage / SOC limit
first. The control is therefore: is the per-cell limiter's constraining cell **not** identified by the scalar
extremes (max-voltage cell, or the coldest or hottest probe)? The min-voltage comparison will still be reported, as
the brief asked.

**2. Per-cell gains over min/max can only come from temperature.** If every per-cell limit is a monotone function of
that cell's voltage alone, the per-cell limiter and a min/max limiter that reads `vmax` give the **same** current,
by construction. That follows from the algebra; no data is needed to see it. Any per-cell gain over min/max must come
from the coupling between a cell's state of charge and **its own** temperature.

**3. That coupling depends on an unknown.** Changan logs 96 cells and 32 probes but does not say which probe sits
next to which cell. The cell-to-probe mapping is therefore ASSUMED, and H-a's answer is reported under more than one
mapping.

## 1. H-a — counterfactual replay (every number DERIVED; every limit ASSUMED)

### Frames and sessions

- **Frames used:** per-cell full vectors (`dv_full`, `dt_full`) whose timestamps match a summary frame with
  `status == 1` (charging) and `sync == True`.
- **Sessions:** maximal runs of charging summary frames, split at gaps of more than 300 s. A session is used if it has
  ≥ 10 such full vectors. All 300 vehicles are included.
- **Cell voltage:** `V_k = vmean_mv + dv_k` (mV).
- **Probe temperature:** `T_p = tmean + dt_p` (°C, ±0.5 °C rounding).

### Limit map (ASSUMED; generic NMC shape, not Changan's real map)

The allowed C-rate is `C(SOC, T) = C_T(T) · taper(SOC)`:

- `C_T`: linear interpolation through the points (T °C → C) (−20, 0.05), (0, 0.2), (10, 0.6), (25, 1.5), (40, 1.5),
  (50, 0.8), (60, 0.0), clamped at the ends. It falls off on the cold side (lithium plating) and the hot side (thermal
  derating).
- `taper`: 1.0 for SOC ≤ 60 %, then linear down to 0.05 at SOC = 100 %.
- **SOC** is read from voltage through `data/changan/ocv_full.json`, made monotone and clipped to its ends. Terminal
  voltage is used without IR correction (ASSUMED).

### The three limiters, evaluated on each frame

| Limiter | Formula | What it reads |
|---|---|---|
| **L_cell** (per-cell) | `min_k C_T(T_{p(k)}) · taper(SOC(V_k))` | each cell's voltage and its mapped probe |
| **L_mm** (min/max scalar) | `min(C_T(tmin), C_T(tmax)) · taper(SOC(vmax))` | the GB/T scalar extremes; this is the conservative scalar combination |
| **L_pack(m, mT)** (pack-scalar with margins) | `min(C_T(tmean − mT), C_T(tmean + mT)) · taper(SOC(V̄ + m))` | pack mean only; `V̄ = vmean`, `m` is a voltage margin in mV, `mT` a temperature margin in °C |

L_cell ≥ L_mm holds on every frame by construction. L_pack may sit above L_cell; that is the **unsafe** case.

### Cell-to-probe mappings (ASSUMED)

| Mapping | Definition | Role |
|---|---|---|
| **M1 (primary)** | contiguous: `p(k) = ⌊k · 32 / 96⌋`, three neighbouring cells per probe | |
| **M2** | 100 random permutations of M1 (seeds 0–99) | report the median and the 5–95 % range |
| **M0** | every cell gets the worst probe | equals L_mm; included as a check |

### Charge-time proxy (DERIVED; ASSUMED state trajectory)

- For each full vector i, ΔAh_i = charge delivered since the previous full vector of the session. It is integrated
  from the summary frames' current; gaps longer than 60 s contribute 0.
- `t_L = Σ_i ΔAh_i / (L_i · C_nom)`, with C_nom = 120 Ah (ASSUMED; it cancels in every ratio reported).
- **ASSUMED:** the recorded state trajectory is what the cells would follow at the limiter's current. This is
  first-order only, because higher current would change the IR rise and heating.
- The charger's real current is ignored. This asks what the limiter would permit, not what the charger delivered.

### Reported (all DERIVED)

**Per session:**

- `S_mm = 1 − t_cell / t_mm`: time saved by per-cell enforcement over min/max.
- Per-frame admissible current ratio `L_cell / L_mm`.

**The key control:**

- The fraction of frames where the per-cell constraining cell (argmin) is **not** the max-voltage cell. It is
  reported both over all frames and over frames where `L_cell < L_mm − 1e-9` (frames where per-cell differs at all).
- The same fraction against the min-voltage cell (as the brief asked).
- The same fraction against cells mapped to the tmin or tmax probe.

**Margin sweep:**

- `m` ∈ {0, 5, 10, 20, 30, 50, 75, 100} mV × `mT` ∈ {0, 2, 5, 10} °C.
- For each combination: the median session `S_pack = 1 − t_cell / t_pack`, and the **unsafe-frame fraction** (frames
  where `L_pack > L_cell · 1.001`).
- The smallest `(m, mT)` with unsafe fraction ≤ 0.1 % is reported with its S_pack. That is the margin a pack-scalar
  limiter needs, and what it costs relative to per-cell.

**Sensitivity:**

- The `C_T` breakpoints shifted ±5 °C.
- The taper knee at 50 / 60 / 70 % SOC.

Each sensitivity is run under M1 and reported as a separate row.

**Uncertainty:** a 1,000-resample cluster bootstrap over vehicles (seed 0) for the median `S_mm`.

### Decision rule (fixed now; the threshold is CHOSEN)

| Verdict | Condition |
|---|---|
| **NO BENEFIT over min/max** | median session `S_mm` < 1 % under M1 **and** under the M2 median |
| **PER-CELL RECOVERS X** | median `S_mm` ≥ 1 % under M1 **and** the M2 median, with M1's bootstrap CI lower bound > 0. X is reported as the M1 value with the M2 range, at the stated map and margins. |
| **NOT ANSWERABLE from replay** | the M1 and M2 verdicts disagree (the answer depends on the unknown cell-to-probe mapping) |

**Prior, stated before running:** the probe spread in charging is a few °C at most, and Changan's temperatures sit in
the flat part of `C_T`. I therefore expect NO BENEFIT over min/max, with a non-trivial benefit over pack-scalar at any
margin large enough to be safe.

## 2. H-b — compute footprint at loop rate (MEASURED on the board)

### The evaluator: `board/h_limiter.c`, C, `-O2`, single thread

Per update it:

- reads N cell voltages (int16 mV) and P = ⌈N/3⌉ probe temperatures (int16, 0.1 °C);
- computes per-cell SOC from a voltage LUT, and `C_T` from a temperature LUT;
- updates a per-cell EWMA resistance estimate, `R_k ← R_k + α(ΔV_k/ΔI − R_k)` when |ΔI| > 5 A. This is the brief's
  "optional per-cell resistance estimate", included so the resident state is realistic. It does not enter the limit;
- takes the min and argmin over cells, and emits a setpoint `L · C_nom`.

**Resident state, reported per cell and in total:** last voltage (2 B), resistance estimate (4 B), probe index
(2 B), per-cell voltage limit (2 B), plus the shared LUTs. Totals are given for N = 96, 192, 324 and 1000.

### Frames

- Real Changan charge frames from **held-out vehicles**: vehicle IDs ≡ 0 (mod 10). These vehicles' frames are not
  used in tuning anything.
- N = 96 uses one vehicle frame per update.
- N = 192, 324 and 1000 tile consecutive real frames from several held-out vehicles into one wider pack (real values,
  synthetic geometry; ASSUMED).

### Measurements (each N, 5 repeats, pinned to one A55 core, `performance` governor, the hard reservation held)

- **Per-update latency:** p50 / p99 / max over ≥ 100,000 updates, timed with `CLOCK_MONOTONIC` around each update.
- **Sustained rate:** updates per second over a tight 5 s loop.
- **Memory:** `VmRSS` before the limiter state and LUTs are allocated, and `VmHWM` after the run.
- Frame buffers are pre-loaded and reported separately, because they stand in for the data the BMS would receive.

### Gate, in the same run

- The board output (argmin and setpoint per frame) is compared against a Python reference that implements the same
  algorithm on the same frames.
- **PASS** requires all of: argmin identical on 100 % of frames; setpoint |Δ| ≤ 1e-4 C; resistance state |Δ| ≤ 1e-3.
- **Ties:** where two cells give the same minimum within 1e-9, either index counts as a match.
- **A FAIL withholds the latency numbers.**

### Comparison point

The model already measured in this repo (Experiment E1, MEASURED): 225,544 B, 22.8 ms int8 p50 inference.

### Board protocol

- Hard reservation of `imx95-frdm` through the bus.
- Census before the run; staging in `/tmp/batt_h` (tmpfs).
- At release: reap and print the remaining processes, restore the `ondemand` governor, and delete the staging
  directory.

## 3. Outputs

| Output | File |
|---|---|
| H-a results | `analysis/H_replay.py` → `results/H/replay.json` |
| H-a plots | `results/H/h_constraining.png`, `results/H/h_margin.png` |
| H-b evaluator | `board/h_limiter.c` |
| H-b reference and gate | `board/h_ref.py` |
| H-b results | `results/H/footprint.json` |
| H-b plot | `results/H/h_scaling.png` |
| Write-up | `results/H/results_H.md` |

H-a and H-b will not share a headline.
