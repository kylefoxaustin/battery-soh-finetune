# battery-soh-finetune

**Is on-device fine-tuning of a battery state-of-health (SoH) model feasible on an i.MX 95-class
application processor — and is it worth doing?** Two studies, on real EV field data, with every number tagged
by how it was obtained.

| | Question | Answer (short) | Write-up |
|---|---|---|---|
| **Study 1** | Is last-layer fine-tuning of a ~214 k-parameter LSTM SoH model feasible on an NXP **FRDM-IMX95-PRO** (Cortex-A55 + DDR), and does fine-tuning on a vehicle's own early data beat the fleet model? | **Feasible** (220 KB int8 model, 22.8 ms/inference on one A55 core; last-layer Adam state 520 B; full retrain tens of MB). **Not worth it**: fine-tuning on early data *hurt* 14 of 20 held-out cars. | [`results/results.md`](results/results.md) |
| **Study 2** | Does that negative hold **at scale**, and does a fairer **rolling** re-fine-tune help at short horizons? | **Per-unit adaptation does not help** on the Changan 300-EV fleet (94 units, 4-fold): no variant beats the frozen fleet model robustly at any horizon. The one near-term gain (EVBattery, 0–5 k km) is matched exactly by a no-model "average of recent labels". | [`results/results_large.md`](results/results_large.md), [`results/dataset_profile.md`](results/dataset_profile.md) |

Every figure carries a tag: **MEASURED** (ran it; output verified in the same run), **DERIVED** (arithmetic on
stated inputs), **ASSUMED** (a stated stand-in), **UNGATED** (no same-run correctness check — not quotable).
Code comments mark every input as **CHOSEN** or **IMPOSED**. Section references such as "brief §E2" point to
the two study specifications these experiments were written against (not included); the write-ups are
self-contained.

## Data — not included; how to get it

### EVBattery (Study 1, and Study 2's second dataset) — CC BY 4.0

He et al., *EVBattery: A Large-Scale Electric Vehicle Dataset for Battery Health and Capacity Estimation*,
[figshare 23301881](https://figshare.com/articles/dataset/23301881). ~1.4 GB, no registration.

```bash
mkdir -p data/raw/evbattery && cd data/raw/evbattery
for id in 41076449:battery_dataset1 41076506:battery_dataset2 41076458:battery_dataset3; do
  curl -L -o ${id#*:}.tar.gz https://ndownloader.figshare.com/files/${id%%:*}; done
cd - && python data/prepare_evbattery.py        # streams the tarballs -> data/processed/evbattery_ds{1,2,3}.npz
```

### Changan 300-EV field data (Study 2) — CC BY-NC-SA 4.0, academic / non-commercial use

Liu, H., Li, C., Hu, X. *et al.* Multi-modal framework for battery state of health evaluation using open-source
electric vehicle data. *Nat. Commun.* **16**, 1137 (2025). <https://doi.org/10.1038/s41467-025-56485-7>

Request it from the State Key Laboratory of Intelligent Vehicle Safety Technology:
<https://ivstskl.changan.com.cn/?p=2697> → "Full Dataset of 300 Vehicles" (registration form; read and accept
their terms of use). The download is a **two-volume split zip** — you need **both** `RAW_DATA.z01` (≈ 51.5 GB)
and `RAW_DATA.zip` (≈ 22.8 GB) in the repo root. ~581 GB of CSV inside; nothing here ever writes the CSV to disk.

The release has **no capacity label** — Study 2 derives one (see `results/dataset_profile.md` before using any
Changan number). Requires `libarchive` (for RAR5) and `pip install libarchive-c`.

## Reproduce

Host: Python 3.10+, `torch`, `numpy`, `pandas`, `matplotlib`; for the TFLite export `tensorflow` 2.19 +
`tf_keras`. A GPU helps for EVBattery fleet training (~1 min on an RTX 5090); everything else is CPU.

### Study 1 — on-device feasibility (EVBattery + FRDM-IMX95-PRO)

```bash
# fleet model (prints the two baselines it must beat)
cd model && python train_fleet.py --ds 1 --device cuda --out ../runs/ds1 && cd ..
# int8 + fp32 TFLite, gated (Keras twin == torch; fp32 tflite == torch)
python model/export_tflite.py --run runs/ds1
# stage code + artifacts to the board (tar over ssh into /tmp/batt_ft; host alias `imx95`)
python model/stage_board.py --run runs/ds1 --host imx95
```

On the board (Yocto, Python 3.14, torch 2.9 CPU, tflite_runtime 2.19 — make sure nothing else is running on it):

```bash
cd /tmp/batt_ft && sh board/run_all.sh runs/ds1 results/raw
```

`run_all.sh` pins the CPU governor to `performance` (restores it on exit), pins inference to one A55 core and
training to two, records a census of other processes (CPU delta over 5 s, binaries via `/proc/PID/exe`) before
each experiment, and wraps every child in `timeout -k`. Then on the host:

```bash
scp -r imx95:/tmp/batt_ft/results/raw results/
python board/e5_buffers.py --e4 results/raw/e4.json --out results/raw/e5.json
python results/make_report.py            # -> results/summary.json, results/plots/
```

### Study 2 — per-unit adaptation at scale (Changan)

```bash
sh analysis/run_full.sh      # extract both volumes -> slim telemetry -> OCV table -> labels -> 4-fold
                             # fleet models -> one-shot (A/B) + rolling (C) experiments -> aggregate + plots
```

Stages, each runnable alone (see the docstrings): `data/changan_extract.py` (reads the split zip, CRC-checked,
works with either volume alone for the members it holds) → `data/changan_slim.py` (RAR5 stream → scalar
columns) → `data/changan_labels.py` (`ocv`, then `label`) → `data/changan_consolidate.py` (`--filter
primary|strict`) → `model/train_fleet.py --data … --nfolds 4 --fold k` → `board/e4_pervehicle.py` and
`analysis/rolling.py` → `analysis/aggregate.py`. CPU only, ~1–2 h on 32 cores.

The board re-confirmation (Study 2 §D): `python model/stage_board.py --run runs/chf_primary_k0`, then on the
board `sh board/run_expD.sh runs/chf_primary_k0 results/expD`.

## Layout

```
data/      prepare_evbattery.py · changan_extract.py · changan_slim.py · changan_labels.py · changan_consolidate.py
model/     common.py (features, SoHNet, freeze scopes) · train_fleet.py · export_tflite.py · arena_bound.py · stage_board.py
board/     cpustat.py · census.py · e1_inference.py · train_mem.py · e2_fullretrain.py · e3_lastlayer.py ·
           e4_pervehicle.py · e5_buffers.py · run_all.sh · run_expD.sh · probe_fixed_cost.sh
analysis/  rolling.py (Exp C) · aggregate.py (sign tests, Bonferroni, plots) · run_full.sh
results/   results.md · dataset_profile.md · results_large.md · raw/ · large/ · plots/   (aggregate results only — no data)
```

## Traps found on the way (worth knowing if you do anything similar)

1. **A TFLite LSTM converted from Keras is stateful across `invoke()`.** `UNIDIRECTIONAL_SEQUENCE_LSTM` keeps h/c
   as variable tensors; without `interpreter.reset_all_variables()` before each inference, every sample starts
   from the previous one's state. Median error looked fine (3e-5 Ah); the max was 0.52 Ah.
2. **One heavy-tailed feature wrecks per-tensor int8 input quantization** (rolling-variance z-scores up to 180 →
   an int8 model worse than predicting the mean). Fixed with rolling std + clipping z to ±6.
3. **A weak fleet model flatters every fine-tune.** Without odometer as an input, the LSTM lost to a one-line
   mileage fit; any per-vehicle "gain" against it would have been an artifact.
4. **BMS SOC is stale at full charge** in the Changan data (cells at 4.2 V while the BMS reports ~97 %), and
   **derived capacity depends on the charger** (IR drop at 49 A vs 15 A): slow-charge labels show no ageing
   trend at all.
5. **"Memory added by training" depends on the reference point.** VmHWM-before vs RSS-before differ by the batch
   forward working set (~14 MB here) — and which one you get silently depends on fine-tune set size.

## Licence

Code: MIT (see `LICENSE`). Data: not included; each dataset remains under its own licence (EVBattery CC BY 4.0;
Changan CC BY-NC-SA 4.0 with the provider's terms of use). Results derived from the Changan data are
published here for non-commercial research with attribution to Liu et al. (2025) and the State Key Laboratory of
Intelligent Vehicle Safety Technology.
