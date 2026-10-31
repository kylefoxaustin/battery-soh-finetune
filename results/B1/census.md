# B1 Stage 1: board census (brief §3)

Run 2026-10-30, 11:29–11:31 board time, by `board/b1_census.sh` from a staged tree in `/tmp/b1` (tmpfs). Raw output:
`raw/census/`. **No ring, producer, dumper or eMMC write code exists.** Every value is **MEASURED** on the board
named below unless tagged otherwise.

- **Board:** FRDM-IMX95-PRO (`imx95-frdm`), held under a **hard** fleet lease for the whole census.
- **Process census:** CPU delta over 10 s, binaries resolved by `/proc/PID/exe`. It was taken before and after the
  baselines; both found **no process above 0.5 % of a core**, among 201 processes.
- **Leftovers from another session, disclosed:** `/tmp` holds JSON files and a `hog.pid` dated 2026-10-29 from another
  session. The PID in `hog.pid` (2017) does not exist, so nothing from it is running. The files were left untouched.

## Verdict of the census: **BLOCKED on the storage gate**

> **Addendum, 2026-10-30, after the census.** Kyle approved option (a) below.
>
> - `mmcblk0p3` was created in the eMMC's unallocated space: 18.8 GB ext4, label `b1dump`, mounted only for B1 at
>   `/mnt/b1`. p1 and p2 were not touched.
> - Re-measured: **18 GB free on the eMMC** (`df`, 18,203,032 kB), so **the storage gate PASSES**. Every other gate
>   above was already PASS.
> - Stage 2 then ran: [`results_B1.md`](results_B1.md).
> - After the run the partition is empty (only `lost+found`), unmounted and not in fstab. It is left in place pending
>   Kyle's decision.

| §3.5 gate | Value | Bar | Result |
|---|---|---|---|
| Available RAM | **15.3 GB** (`MemAvailable` 15,318,620 kB) | ≥ 3 GB | **PASS.** No D-1 is needed: the 2 GB and 512 MB rings fit. |
| Writable eMMC partition, free space | **555 MB** free on `mmcblk0p2` (eMMC, 10.6 GB ext4, 95 % used) | ≥ 12 GB | **FAIL** |
| Named substitute | SD card `mmcblk1p2` (the root fs): **7.9 GB** free | ≥ 12 GB | **FAIL**, and it is an SD card, not eMMC (§6) |
| e1 baseline, int8, core 1 | **p50 22.852 ms**; bit-identity gate PASS (0 LSB, 256 snippets) | within 10 % of 22.84 ms | **PASS** (+0.05 %) |
| H-b baseline, 96 cells, core 2 | **p50 1.500 µs**, p99 3.21 µs; C↔Python gate PASS (10,000 frames) | within 10 % of 1.50 µs | **PASS** (0.0 %) |
| H2-b baseline, 3,564 cells, core 2 | **p50 52.13 µs**, p99 107.3 µs; gate PASS (10,000 frames) | within 10 % of 52.1 µs | **PASS** (+0.05 %) |

**Why the storage gate matters.** A 300 s dump at 32 MB/s is 9.6 GB (DERIVED). Neither medium can take it. The eMMC
partition cannot even take a 60 s dump at 32 MB/s (1.9 GB, DERIVED).

**What would unblock it.** These are not done, because they change a shared board.

- **(a) Use the eMMC's unallocated space.** `parted` shows **20.2 GB unallocated** after partition 2 (11.7–31.8 GB).
  - A new partition there (ext4, mounted only for B1) would pass the gate on the real eMMC.
  - It touches neither existing partition, but it changes the partition table of a board other sessions use.
- **(b) The reviewer amends §3.5** to fit 7.9 GB on the SD card, named as SD, as a numbered deviation. That would mean
  dropping or shortening the N = 300 dump at 32 MB/s.
  - This measures an SD card, not eMMC. The eMMC endurance row would then rest on SD write rates.
- **(c) Free space on `mmcblk0p2`.** Its 9.1 GB of contents belong to the board's eMMC system image, not to this
  project. **Not recommended.**

## 1. Kernel, cores, frequency, governor

| | Value |
|---|---|
| Kernel | Linux 6.18.20-2.0.0-gb096ce610e95, SMP PREEMPT, aarch64 (not RT) |
| Online cores | **6** (0–5), so the brief's core plan (OS 0, inference 1, limiter 2, producer 3, dumper 4, cpustat 5) stands unchanged |
| Max frequency | 1.8 GHz on every core |
| Governor before pinning | **`performance` on every core**, as found; it was left by a previous tenant. It was pinned to `performance` for the baselines and restored to `performance` on exit. |

## 2. RAM and huge pages

| | Value |
|---|---|
| MemTotal / MemFree / MemAvailable | 16,097,084 / ≈14.4 GB / 15,318,620 kB |
| CMA | 5.18 GB total, 5.11 GB free (the NPU device tree's reservation) |
| Explicit huge pages | `HugePages_Total` = **0** (2 MB page size), so **`MAP_HUGETLB` fails** for 512 MB and 2 GB (ENOMEM) |
| Transparent huge pages | `enabled` = **always**, `defrag` = madvise |
| `MAP_POPULATE` anonymous mapping | **512 MB: OK in 0.04 s. 2 GB: OK in 0.18 s.** Both released. |

**Plan for Stage 2 (recorded, not a deviation):** the brief says to use `MAP_HUGETLB` "if the census allowed it". It
did not. The rings would use `MAP_POPULATE` with THP (`always`). Reserving explicit huge pages would change a
system-wide setting, so it is not done.

## 3. Storage

| Device | Type (`/sys/.../type`, `name`) | Size | Partitions | Mounted | Free |
|---|---|---|---|---|---|
| `mmcblk0` | **MMC (eMMC)**, `0IM20E`, CID `13014e30494d3230451035839a019c00` | 29.6 GiB (62,160,896 sectors) | p1 256 MB vfat; p2 10.6 GB ext4; **20.2 GB unallocated** | p2 at `/run/media/root-mmcblk0p2` (rw, relatime) | **555 MB** |
| `mmcblk1` | **SD**, `SD64G`, CID `275048534436344760da30750e018a00` | 58 GiB | p1 256 MB vfat; p2 57.7 GB ext4 | p2 at `/` (rw, relatime); **the board boots from SD** | **7.9 GB** |
| `/tmp` | tmpfs (RAM) | 7.7 GB | | | not a storage medium |

## 4. Baselines (nothing else running; governor `performance`)

| Harness | Core | p50 | p99 | Gate | Reference |
|---|---|---|---|---|---|
| `e1_inference.py`, int8, 1 thread | 1 | **22.852 ms** | (in `e1_baseline.json`) | bit-identity 0 LSB, RMSE equal: PASS | Study 1: 22.84 ms |
| `h_limiter`, 96 cells, 32 probes | 2 | **1.500 µs** | 3.208 µs | `h_ref.py gate`: argmin exact 1.0, Δsetpoint 0, ΔR 2.4e-7: PASS | H-b: 1.50 µs / 3.17 µs |
| `h_limiter` (VLIM 3650), 3,564 cells, 1,944 probes | 2 | **52.126 µs** | 107.293 µs | `h2_ref.py gate`: PASS | H2-b: 52.1 µs / 107.0 µs |

The frame files and references were rebuilt on the host with the unchanged `h_ref.py` and `h2_ref.py build`. Gating
was done on the host against the board's `gate_out_*.bin`.

## Board state at the end of the census

- `/tmp/b1` was removed.
- The governor is `performance`, as found.
- No B1 process was left running. The process census after the baselines shows nothing above 0.5 % of a core.
- The fleet lease was released after cleanup; see the commit for the cleanup evidence.
