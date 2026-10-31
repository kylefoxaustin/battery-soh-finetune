# B1 results: an LPDDR ring buffer on FRDM-IMX95-PRO (capability measurement, no verdict)

Brief: [`briefs/B1/README.md`](../../briefs/B1/README.md). Census: [`census.md`](census.md). Machine-readable:
[`b1.json`](b1.json), built by `board/b1_report.py` from the logs in [`raw/`](raw/). Run 2026-10-30, 11:48–18:55 board
time, under a hard fleet lease, by `board/run_b1.sh out /mnt/b1 1 2 3`.

**Tags.** Every number is **MEASURED** on the FRDM-IMX95-PRO (six Cortex-A55 at 1.8 GHz, governor `performance`,
kernel 6.18.20) unless tagged otherwise. Spreads are min–max over the repeats (3 per 30-minute cell, 2 for P5 and P6,
as tabled in brief §4.5).

> **The producer is a CPU thread, not DMA. Every CPU-cost number below is an upper bound on a DMA path.**

## Summary

- **Ingest.** At 3.2, 32 and 60 MB/s a single pinned producer thread hit the target rate in all 14 cells
  (achieved/target 1.000001–1.000002), with **0 drop events**. The worst scheduling lag was 6.0 ms; no burst started
  more than 10 ms late. Producer thread CPU was **0.54–0.56 % / 1.84–1.91 % / 3.08–3.10 % of one core** (upper bound on
  a DMA path).
- **Depth.** Measured by sequence span: 512 MB holds **167.8 s at 3.2 MB/s** and **16.8 s at 32 MB/s**. 2 GB holds
  **671.1 s, 67.1 s and 35.8 s** at 3.2, 32 and 60 MB/s. These are identical across repeats.
- **Dump.** All 26 dumps whose window fit inside the ring verified (contiguous, exact count, 0 mismatches). The
  producer dropped nothing during any dump. The 16 dumps whose window was longer than the ring held FAIL the gate as
  written (§4.3), and are reported as results, not tuned away.
- **Real-time work.** **RT DISTURBED was not raised in any phase of any round.** The largest median p99 ratio against
  the same session's baseline was 1.063 (limiter, 3,564 cells, at 60 MB/s). The worst single 60 s block was 1.149
  (limiter, 96 cells, at 60 MB/s). The flag bar is 1.20. The inference p99 never moved more than 0.7 % in any block.
- **SUSTAINED** (≥ 99 % of target, 0 drops, all three dump gates pass) holds only for **3.2 MB/s into 2 GB (P3), 3 of
  3**. The other cells meet the rate and drop parts, and fail it only because the N = 60 or N = 300 window is longer
  than the ring.
- **eMMC.** Sustained `O_DIRECT` sequential writes ran at **164 MB/s** (per-file 159.5–165.8). As a ring medium, the
  29.6 GiB eMMC would wear out in **0.95 / 0.095 / 0.050 years** at 3.2 / 32 / 60 MB/s (DERIVED, endurance ASSUMED
  P/E 3,000; see the table for P/E 500).

## 1. Capability table (brief §4.6)

| Cell | Rate × ring | Achieved / target | Drop events | Max sched. lag (ms) | Producer CPU, % of one core **(upper bound on a DMA path)** | Depth, MEASURED (s, by sequence span) | Depth, DERIVED (ring / rate) | Dump gates N10 / N60 / N300 | Flag |
|---|---|---|---|---|---|---|---|---|---|
| P1 | 3.2 MB/s × 512 MB | 1.000001 (×3) | 0, 0, 0 | 5.46–5.98 | 0.54–0.56 | 167.8 | 167.8 | PASS / PASS / FAIL‡ (×3) | — |
| P2 | 32 MB/s × 512 MB | 1.000001 (×3) | 0, 0, 0 | 5.00–5.96 | 1.89–1.91 | 16.8 | 16.8 | PASS / FAIL‡ / FAIL‡ (×3) | — |
| P3 | 3.2 MB/s × 2 GB | 1.000001 (×3) | 0, 0, 0 | 5.11–5.70 | 0.55–0.56 | 671.1 | 671.1 | PASS / PASS / PASS (×3) | **SUSTAINED** (3 of 3) |
| P4 | 32 MB/s × 2 GB | 1.000001 (×3) | 0, 0, 0 | 5.40–5.86 | 1.84 | 67.1 | 67.1 | PASS / PASS / FAIL‡ (×3) | — |
| P5 | 60 MB/s × 2 GB (10 min) | 1.000002 (×2) | 0, 0 | 5.10–5.83 | 3.08–3.10 | 35.8 | 35.8 | PASS / FAIL‡ / FAIL‡ (×2) | — |

‡ `window exceeds the ring's live span`: the requested window holds more data than the ring at that rate. The dumper
copied the whole ring, and the gate fails on count, as §4.3 requires.

- **Depth columns.** The two depth columns are listed side by side because the brief asks for both. No claim is drawn
  from the comparison (Law 1).
- **Pacing.** Bursts more than 1 ms late numbered 161–622 per 30-minute cell (of 1.8 M bursts) and 103–116 per
  10-minute P5 cell. None were more than 10 ms late.
- **Dumper CPU.** The dumper runs on core 4. Its busiest 10 s window was 19.5–20.2 % of the core (cpumon) during the
  2 GB copies. Like the producer figure, this is CPU copy cost, an upper bound on a DMA path.

## 2. Freeze-and-dump (brief §4.3), N = 10 / 60 / 300 s, producer running

| Cell | N | Window | Gate | Dump time incl. `fsync` (s) | Copy+write MB/s | Mismatched frames | Producer drops during dump |
|---|---|---|---|---|---|---|---|
| P1 3.2 × 512 | 10 | 32 MB | PASS ×3 | 0.223–0.232 | 137.7–143.6 | 0 | 0 |
| | 60 | 192 MB | PASS ×3 | 1.258–1.279 | 150.1–152.7 | 0 | 0 |
| | 300 | 960 MB wanted, 537 MB held | FAIL‡ ×3 | 3.495–3.537 | 151.8–153.6 | 0 | 0 |
| P2 32 × 512 | 10 | 320 MB | PASS ×3 | 2.083–2.116 | 151.2–153.6 | 0 | 0 |
| | 60 | 1.92 GB wanted, 537 MB held | FAIL‡ ×3 | 3.494–3.510 | 152.9–153.7 | 0 | 0 |
| | 300 | 9.6 GB wanted, 537 MB held | FAIL‡ ×3 | 3.513–3.567 | 150.5–152.8 | 0 | 0 |
| P3 3.2 × 2 GB | 10 | 32 MB | PASS ×3 | 0.216–0.225 | 142.4–148.0 | 0 | 0 |
| | 60 | 192 MB | PASS ×3 | 1.255–1.292 | 148.6–153.0 | 0 | 0 |
| | 300 | 960 MB | PASS ×3 | 6.238–6.297 | 152.5–153.9 | 0 | 0 |
| P4 32 × 2 GB | 10 | 320 MB | PASS ×3 | 2.093–2.121 | 150.9–152.9 | 0 | 0 |
| | 60 | 1.92 GB | PASS ×3 | 11.797–11.877 | 161.7–162.8 | 0 | 0 |
| | 300 | 9.6 GB wanted, 2.15 GB held | FAIL‡ ×3 | 13.059–13.108 | 163.8–164.5 | 0 | 0 |
| P5 60 × 2 GB | 10 | 600 MB | PASS ×2 | 3.897–3.905 | 153.6–154.0 | 0 | 0 |
| | 60 | 3.6 GB wanted, 2.15 GB held | FAIL‡ ×2 | 13.043–13.078 | 164.2–164.6 | 0 / **3,750** | 0 |
| | 300 | 18 GB wanted, 2.15 GB held | FAIL‡ ×2 | 13.063–13.117 | 163.7–164.4 | **3,750** / 0 | 0 |

**The 3,750-frame mismatches.**

- **What happened.** In 2 of the 4 whole-ring dumps at 60 MB/s (round 1 N300, round 2 N60), exactly **one burst
  (3,750 frames = 1 ms at 60 MB/s)** at the oldest end of the window had been overwritten before the copy reached it.
  The first mismatch is at index 0; the overwrite depth is 0.001 s.
- **Where it did not happen.** None of the 12 whole-ring dumps at 3.2 or 32 MB/s showed it, and none of the 26 dumps
  whose window fitted inside the ring did.
- **Why.** When the window is the whole ring, its oldest slot is the one the producer writes next. The outcome tracks
  where the trigger landed in the burst cycle. In both failing dumps the head at trigger was exactly the scheduled
  count for that time (1.5 × 10⁹ or 2.1 × 10⁹ frames). In both clean ones it was one burst further on.
- **What this says.** A whole-ring freeze with a running producer needs at least one burst of headroom over the window.
  This is the headroom statement §4.3 asks for. These dumps fail the gate on count anyway; no window that fitted was
  affected.

## 3. Real-time work beside the producer (brief §4.2)

Inference: `e1_inference.py`, int8, 1 thread, core 1, continuous, 256-snippet bit-identity gate once per 60 s block.
Limiter: `h_limiter.c` unchanged, core 2, 100 Hz, alternating 96-cell and 3,564-cell 60 s blocks, C↔Python gate per
block. **Every gate passed in every block:** e1 416 of 416 blocks, limiter 415 of 415. Values are the median over the
phase's blocks, one number per round (r1 / r2 / r3).

| Phase | e1 p50 (ms) | e1 p99 (ms) | Limiter 96 p50 / p99 (µs) | Limiter 3,564 p50 / p99 (µs) | Max median p99 ratio vs P0 | Max worst-block p99 ratio vs P0 | RT DISTURBED |
|---|---|---|---|---|---|---|---|
| P0 baseline | 22.848 / 22.872 / 22.851 | 23.038 / 23.067 / 23.024 | 2.50 / 2.38 / 2.42 ; 5.15 / 5.04 / 5.13 | 56.9 / 57.0 / 56.8 ; 119.4 / 124.5 / 127.1 | — | — | — |
| P1 3.2 × 512 | 22.836 / 22.842 / 22.833 | 23.063 / 23.040 / 23.026 | 2.46 / 2.46 / 2.50 ; 5.25 / 5.21 / 5.23 | 57.5 / 57.4 / 56.8 ; 120.7 / 130.1 / 128.1 | e1 1.001, L96 1.033, L3564 1.045 | e1 1.005, L96 1.081, L3564 1.099 | no |
| P2 32 × 512 | 22.875 / 22.827 / 22.822 | 23.037 / 23.063 / 23.046 | 2.50 / 2.40 / 2.48 ; 5.13 / 5.10 / 5.25 | 57.7 / 57.3 / 57.3 ; 120.6 / 129.3 / 131.8 | e1 1.001, L96 1.024, L3564 1.038 | e1 1.005, L96 1.106, L3564 1.111 | no |
| P3 3.2 × 2 GB | 22.826 / 22.839 / 22.833 | 23.023 / 23.051 / 22.993 | 2.56 / 2.42 / 2.46 ; 5.25 / 5.13 / 5.21 | 58.0 / 57.5 / 57.3 ; 121.5 / 129.2 / 129.7 | e1 0.999, L96 1.020, L3564 1.038 | e1 1.002, L96 1.098, L3564 1.104 | no |
| P4 32 × 2 GB | 22.832 / 22.830 / 22.823 | 23.011 / 23.055 / 22.976 | 2.50 / 2.42 / 2.44 ; 5.29 / 5.06 / 5.15 | 57.5 / 57.5 / 57.3 ; 121.5 / 130.5 / 130.5 | e1 0.999, L96 1.028, L3564 1.049 | e1 1.007, L96 1.109, L3564 1.122 | no |
| P5 60 × 2 GB | 22.845 / 22.845 / — | 23.077 / 23.065 / — | 2.58 / 2.58 / — ; 5.29 / 5.29 / — | 57.6 / 58.4 / — ; 120.2 / 132.3 / — | e1 1.002, L96 1.050, L3564 1.063 | e1 1.007, L96 1.149, L3564 1.117 | no |

- **How RT DISTURBED is computed.** It is fixed in `board/b1_report.py`, which was committed (`78f2ff6` local) before
  any producer-on block was read. The flag is raised when the median of the producer-on block p99s exceeds the median
  of the same round's P0 block p99s by more than 20 %, counting only blocks wholly inside the phase. The worst single
  block is reported beside it as descriptive. On either reading, nothing reaches 1.20.
- **Limiter latency here is not the H-b figure.** The in-session limiter p50 (2.4–2.6 µs at 96 cells) is higher than
  the census H-b baseline (1.50 µs). The census harness runs updates back to back with warm caches. The B1 loop runs
  one update every 10 ms, so each starts cold. Interference is therefore read only against the same session's P0
  blocks, never against H-b. The 3,564-cell figure behaves the same way (about 57 µs vs 52.1 µs).
- **Inference matches Study 1.** e1 p50 inside B1 (22.82–22.88 ms) agrees with Study 1 (22.84 ms) and the census
  (22.852 ms), all MEASURED under the same harness.

## 4. eMMC as a medium (brief §4.4)

- **Medium.** eMMC `mmcblk0` (`0IM20E`), new partition `mmcblk0p3` (18.8 GB ext4, label `b1dump`; see §6). It is
  **not** the SD card.
- **Write mode.** `dd if=<1 GB urandom file in tmpfs> oflag=direct conv=fsync`. `O_DIRECT` was accepted.

| | Round 1 | Round 2 |
|---|---|---|
| Files × 1 GB, duration | 46, 301.5 s | 46, 301.0 s |
| Per-file MB/s, median (min–max) | 163.7 (159.5–165.7) | 164.2 (162.2–165.8) |
| Overall MB/s | 163.8 | 164.1 |
| Return codes | all 0 | all 0 |
| Free space before / after | 18,203,032 kB / 18,203,032 kB | 18,203,032 kB / 18,203,032 kB |

**DERIVED (from the MEASURED 163.9 MB/s mean and the census capacity of 31.83 GB; endurance ASSUMED: P/E 3,000
MLC-class or 500 TLC-class, write amplification 1.0).** These are years to wear-out if this eMMC were the ring medium.

| Rate | Years, P/E 3,000 (ASSUMED) | Years, P/E 500 (ASSUMED) | Can the eMMC absorb the rate? (DERIVED: 163.9 MB/s ≥ rate) | N = 300 dump time, DERIVED from 163.9 MB/s | N = 300 dump time, MEASURED |
|---|---|---|---|---|---|
| 3.2 MB/s | 0.95 (DERIVED / ASSUMED) | 0.16 (DERIVED / ASSUMED) | yes | 5.86 s | 6.24–6.30 s (P3, 960 MB) |
| 32 MB/s | 0.095 (≈ 35 days) (DERIVED / ASSUMED) | 0.016 (≈ 6 days) (DERIVED / ASSUMED) | yes | 58.6 s | not measured: the 2 GB ring cannot hold 300 s (P4 copied the full 2.15 GB in 13.1 s) |
| 60 MB/s | 0.050 (≈ 18 days) (DERIVED / ASSUMED) | 0.0084 (≈ 3 days) (DERIVED / ASSUMED) | yes | 109.8 s | not measured: as above (P5, 13.1 s for 2.15 GB) |

The DERIVED and MEASURED dump times sit in separate columns because the brief asks for both. No claim is drawn from
their difference (Law 1).

## 5. Events, board state and census

- **Frequency and thermal.**
  - `cpumon` sampled every 10 s, 2,491 samples. Every core was at 1,800,000 kHz in every sample.
  - Governor `performance` throughout.
  - Peak `a55-thermal` was 60.8 / 61.3 / 62.3 °C in rounds 1 / 2 / 3, and peak `ana-thermal` 60.2 °C.
  - **No throttle or frequency event.** The PMIC zones `pf09`, `pf53_soc` and `pf53_arm` read a constant 105.0 °C,
    the known placeholder on this board, and are not used.
- **Memory.** Lowest `MemAvailable` was 11.95 GB, with both rings mapped and the RT loads running. Peak `Dirty` was
  1.79 GB, during the 2 GB dumps (buffered write before `fsync`).
- **Process census before and after every phase (38 censuses).** Each is a CPU delta over 10 s, with binaries resolved
  by `/proc/PID/exe`. Above 0.5 % of a core they show only the B1 inference loop, the B1 limiter loop and `init`
  (≤ 1.0 %). **Nothing foreign ran.**
- **Repeats.** Every phase completed, with no board reset and no rerun. Watchdog log: [`raw/watchdog.log`](raw/watchdog.log).
- **Cleanup.**
  - Removed: `/tmp/b1`.
  - Leftover scan (`/proc/*/exe` and cmdline): no B1 process left.
  - Board CPU after cleanup: 0.18 % busy over 10 s.
  - Governor: `performance` on all six cores, as found.
  - `/mnt/b1` unmounted and removed; nothing added to `/etc/fstab`.
  - Fleet lease released.

## 6. Deviations and notes

- **D-2 (P5 trigger times).** P5 is a 10-minute cell, so the 10 / 20 / 28-minute trigger times cannot apply. They were
  scaled to **200 / 400 / 560 s** (same order, 10 → 60 → 300), fixed in `board/run_b1.sh` before the run. D-1 was not
  needed (census: 15.3 GB available).
- **No `MAP_HUGETLB`.** `HugePages_Total` is 0. Reserving huge pages changes a system-wide setting, so the rings used
  `MAP_POPULATE` with THP `always`. This was recorded in the census before the run.
- **Storage partition.**
  - The census storage gate failed: 555 MB free on the eMMC root partition.
  - On Kyle's approval (census option (a)), `mmcblk0p3` was created in the eMMC's 20.2 GB of unallocated space as 18.8
    GB ext4, label `b1dump`. p1 and p2 were not touched.
  - It was mounted only for B1. After the run it is **empty (only `lost+found`), unmounted and not in fstab**, so no
    dump file remains on the partition (§6 of the brief).
  - The partition itself is left in place pending Kyle's decision. See the census addendum.
- **Governor (brief §6: do not leave `performance` set).** The census found the governor already at `performance`, set
  by an earlier tenant (the board card says `ondemand` is the boot default). The runner's trap restored *what it found*,
  so the board is at `performance`, as found. Setting it to `ondemand` is a one-line change if the reviewer wants that;
  it was not done on B1's initiative because the state predates B1.
- **The 100 Hz limiter is cache-cold per update** (§3). This is why its in-session p50 differs from H-b. It is a
  property of the 100 Hz loop the brief asks for, not a regression of `h_limiter.c`, which is included unchanged and
  passed its gate in every block.

## 7. Not measured, and not implied

- HyperRAM or MCU-SDRAM windows, the M7/M33 ingest path, or any specific MCU product. The ANGLES §B.3 rows for those
  media remain DERIVED arithmetic with their sources.
- A DMA producer. All CPU figures are upper bounds on one.
- Energy, kWh or cost.
- RT-isolated latency. Everything here is Linux user space with core pinning, as in Study 1 and H-b.
- eMMC endurance. Wear-out is DERIVED from an ASSUMED P/E count; no wear was measured, and the eMMC's own health
  registers were not read.
- Upload of a dump off the board.
- Rings larger than 2 GB, and rates other than 3.2 / 32 / 60 MB/s.
