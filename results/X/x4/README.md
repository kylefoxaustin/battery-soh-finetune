# X4 results — per-cell vs pack-scalar usable-energy estimation (public domain, CC0)

Run 2026-10-30. Pre-registration: `X4_preregistration.md` (one deviation, recorded before any
estimator code). Code: `x4.py`. Outputs: `x4_results.json`, `x4_labels.csv`.
Data: one Changan EV, 6 public sample files, 1.2 M frames at 10 s, 1,322 days, 0 → 66,297 km, 96 cells.
**CC BY-NC-SA 4.0: non-commercial.** Every number is DERIVED from ASSUMED labels.

## Verdict: NO GAIN — and the labels are too noisy to have shown one

> **Correction (2026-10-30).** The first version of this table scored the reserve on the **under-prediction** tail,
> `q(−e)` with `e = U_pred − U_true`. A reserve protects against **over**-statement, so the correct form is `q(e)`.
> This was caught in the X5 audit (`X5_preregistration.md` P-3). The table below is re-scored on the correct tail with
> the same code and data (`x4_results_overstatement_tail.json`). **The verdict does not change.** The original
> under-prediction figures are kept in `x4_results.json` for the record.

| Estimator (W = 8) | Mean abs error | Reserve at 95 % | at 99 % | at 99.9 % (extrapolated) |
|---|---|---|---|---|
| P0 last value | 7.8 % | 15.9 % | 33.0 % | 36.2 % |
| P1 pack scalar | 7.0 % | 16.7 % | 25.9 % | 29.4 % |
| P2 min/max | 7.7 % | 17.0 % | 28.7 % | 38.8 % |
| **P3 per-cell** | **7.0 %** | **14.5 %** | **27.8 %** | **29.4 %** |

- Precision gain P1/P3: **0.93 at 99 %, 1.00 at 99.9 %** (W = 4: 1.17 / 1.16; W = 16: 1.01 / 0.90). Pre-registered bar
  for "helps": 1.5. **NO GAIN.**
- P3 beats P1 on 51 % of targets (W = 8); 49 % (W = 4); 57 % (W = 16).
- **Shuffle control:** shuffled per-cell gives about the same reserve (29.1 % at 99 %; 32.6 % at 99.9 %). Nothing here
  depends on knowing which cell is which. **Pack-level truth:** P3 does no better than P1.
- **Shuffle caveat:** this control permutes cells independently within each discharge, which does change the
  per-cell trends. (The X5 brief's whole-series version would have been a no-op; see `X5_preregistration.md` P-2.)
- 234 labels (12 outliers > 5 MAD removed), 164 scored after warm-up. Not underpowered by count.

## Why it could not have shown anything (post-hoc, read before using the result)
1. **Label noise is ~6 % per discharge**, against an effect we need to resolve at ~1 % precision. Successive labels
   differ by a median 5.9 % (p95 28 %), yet true capacity cannot change that much between two drives.
2. **The labels rise with mileage** (U: 93 → 113 Ah over the record; BMS-SOC capacity 94 → 128 Ah). Real capacity
   falls with age. Likely causes: the per-file logging changes, SOC calibration drift, or the early-life OCV table
   mapping aged cells wrongly. Either way, the labels are not tracking capacity.
3. The weakest cell is the same cell (#19) in 52 % of discharges, and it is the end-rest min-voltage cell in 53 %.
   A min/max view already sees it about half the time.

So X4 says only this: **on one vehicle's field telemetry, nothing can estimate usable energy to better than about
±7 %, per-cell or not.** It does not test whether per-cell history could reach the ~4× gain the reserve claim needs.
That needs labels with < 1 % noise: a periodic full-discharge capacity check, or lab reference tests.

## Where this leaves the reserve question
- The **value** is not in doubt in the lifecost model (~$1,700 if the reserve is an uncertainty reserve).
- The **precision needed** (~4×) cannot be measured on public field data. Every public field dataset we have shares
  this label-noise problem (Changan ~3–6 %, Beihang no capacity labels).
- The one supporting result remains X2-F: per-cell knowledge shrinks a charge limiter's safety margin from 35–45 % to
  ~10%, and that margin holds on unseen vehicles. That is the same mechanism at a different point of the charge.

## Reproducing
Data: the six `EV_feild_data_sample/data_*.rar` files in the public repository
`github.com/HoraceLiu1010/Multi-modal-SOH-estimation-framework`. They are RAR5; `7z` cannot decode them. Use real
`unrar`, or Python `libarchive-c` with the system libarchive. Concatenate the six CSVs (columns `terminaltime, soc,
totalodometer, chargestatus, totalcurrent, batteryvoltage, mintemperaturevalue, maxtemperaturevalue`) into a pandas
pickle, then run `CHANGAN_PKL=all.pkl python3 x4.py`.
