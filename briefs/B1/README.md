# Build Brief — B1: can the board hold a continuous MB/s ring buffer in LPDDR, freeze it on a trigger and dump it, without disturbing the real-time work? (MEASURED)

**Licence of this document:** public domain (CC0). **Written:** 2026-10-30. **Origin:** ANGLES report §B.3
([`results/OPEN_PROBLEM/ANGLES_REPORT.md`](../../results/OPEN_PROBLEM/ANGLES_REPORT.md)), item 2 in
[`briefs/NEXT_EXPERIMENTS/README.md`](../NEXT_EXPERIMENTS/README.md); promoted after X7 closed UNDERPOWERED.

> ## ▶ START HERE
>
> 1. `git pull` on `main`.
> 2. Read this brief end to end, then `board/run_all.sh`, `board/census.py`, `board/cpustat.py`, `board/e1_inference.py`
>    and `board/h_limiter.c` with its H-b harness. B1 reuses them; it does not re-implement them.
> 3. **Stage 1 — census (§3).** Run it on the board, write `results/B1/census.md`, commit with "B1 census, before ring
>    code" in the message.
> 4. **If every gate in §3.5 passes, continue to Stage 2 without stopping.** If any gate fails, set the Status line in
>    `NEXT_TASK.md` to `BLOCKED: <gate> <value>`, push, and stop.
> 5. **Stage 2 — measure (§4).** Write the producer, dumper and runner; run the protocol exactly as written; commit
>    `results/B1/results_B1.md`, `b1.json`, the census and the per-phase logs; add one row each to `results/X/README.md`
>    and `results/RESEARCH_DOSSIER.md` §9; set the Status line to `DONE <commit-hash>`, push, and stop.
>
> B1 is a **capability measurement**, not a hypothesis test. There is no verdict to reach, so there is nothing to tune
> toward. Every number is reported with its bound (§1.3).

---

## 0. Why B1 exists

ANGLES §B.3 argues from arithmetic that a continuous rolling window of converter telemetry at 3–60 MB/s can only live
in DRAM: flash write endurance is exhausted in 0.1–7.6 years (ASSUMED endurance), HyperRAM's 128 MB holds 4–40 s, an
MCU with SDRAM holds 8–80 s, and 2–8 GB of LPDDR holds 10–40 minutes raw. That table is DERIVED. The roadmap needs the
same statement **MEASURED on the application-processor tier**: sustained ingest, window depth, CPU cost, interference
with the real-time work that shares the chip, and the eMMC alternative's throughput and implied wear.

B1 answers five questions with numbers:

1. At 3.2, 32 and 60 MB/s, does a single-core producer sustain the rate into an LPDDR ring for 30 minutes with zero
   drops?
2. How many seconds of raw stream does a 512 MB and a 2 GB ring hold, measured by sequence span, not arithmetic?
3. What does the producer cost in CPU, and what happens to the inference latency (Study 1: 22.84 ms p50 on one A55
   core) and the limiter latency (H-b: 1.50 µs at 96 cells, 52.1 µs at 3,564) running beside it?
4. On a trigger, how long does it take to freeze and dump the last 10, 60 and 300 s to eMMC, and does the dumped window
   verify (contiguous sequence numbers, correct count)?
5. What does the eMMC sustain as a sequential writer, and (DERIVED, endurance ASSUMED) how long would it last as the
   ring medium at each rate?

---

## 1. Rules of engagement

1. Tag every figure MEASURED / DERIVED / ASSUMED / SOURCED / UNGATED. The dump verification is a same-run gate.
2. **The producer is a CPU thread, not DMA.** The dev board has no real-time engine with a telemetry-farming path, so
   every CPU-cost number is an **upper bound** on a DMA path. Say so beside every CPU number.
3. **Not measured, and never implied:** HyperRAM or MCU-SDRAM windows (arithmetic only), the M7/M33 ingest path, energy,
   RT-isolated latencies (Linux user space, as in Study 1 and H-b), and anything about a specific MCU product.
4. Governor pinned to `performance` and restored; process census before and after every phase; every child under
   `timeout -k`; nothing else running on the board.
5. Same-run gates: the dumped window is verified against the producer's sequence numbers in the same run; latencies are
   measured by the existing harnesses with their existing correctness gates (e1's bit-identity on 256 snippets; H-b's
   C↔Python gate).
6. Report every number with its spread (p50 / p99 over repeats) and its bound. One run per cell of the protocol is
   not enough: **three repeats** of each 30-minute primary cell, or state why fewer.
7. No kWh, cost, warranty or regulatory claims. The years-to-wear-out figures are DERIVED from an ASSUMED endurance and
   say so in the same cell of the table.

---

## 2. Setup

- **Board.** FRDM-IMX95-PRO as used in Study 1 and H/H2 (six Cortex-A55, LPDDR5; Yocto; `ssh imx95` from the host via
  `model/stage_board.py`). The census records the actual RAM, kernel and storage.
- **Reused.** `board/run_all.sh` conventions (governor, census, pinning, `timeout -k`), `board/cpustat.py` (per-core
  utilisation), `board/census.py` (process census), `board/e1_inference.py` (int8 inference, 256 snippets, bit-identity
  gate), `board/h_limiter.c` + H-b harness (limiter timing, C↔Python gate).
- **New.** `board/b1_ring.c` (producer), `board/b1_dump.c` (freeze-and-dump with verification), `board/b1_emmc.sh`
  (sequential write test), `board/run_b1.sh` (the protocol), `board/b1_report.py` (JSON → table).
- **Core assignment (CHOSEN, fixed).** Core 0: OS and the runner. Core 1: inference loop. Core 2: limiter loop. Core 3:
  producer. Core 4: dumper. Core 5: `cpustat.py` and idle. If the census shows fewer than six online cores, record the
  reduced plan before any measurement.

---

## 3. Stage 1 — census (`results/B1/census.md`, commit before ring code)

Record, with the command used for each:

1. Kernel version, online cores and their max frequency; governor before pinning.
2. RAM: total, free and available (`/proc/meminfo`); huge-page support (`HugePages_Total`, THP setting); whether
   `MAP_HUGETLB` or `MAP_POPULATE` can back a 512 MB and a 2 GB anonymous mapping (try it; release it).
3. Block devices (`lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,ROTA`), the eMMC device node, model and size
   (`/sys/block/mmcblk*/device/name`, `cid`, `size`), the filesystem and mount options of the partition that will
   receive dumps, and its free space. If there is no eMMC, say so and name the medium that will be used instead.
4. Baselines with nothing else running: e1 inference p50/p99 over 256 snippets on core 1 (gate must pass);
   H-b limiter p50/p99 at 96 and 3,564 cells on core 2 (gate must pass). Compare with Study 1 (22.84 ms p50) and
   H-b/H2-b (1.50 µs, 52.1 µs).
5. **Gates (§3.5):**
   - available RAM ≥ 3 GB (so a 2 GB ring plus 512 MB fits); otherwise scale the large ring to the largest power of two
     ≤ 60 % of available and record the change as D-1;
   - a writable eMMC (or named substitute) partition with ≥ 12 GB free (a 300 s dump at 32 MB/s is 9.6 GB);
   - baseline e1 p50 within 10 % of 22.84 ms and H-b p50 within 10 % of 1.50 µs / 52.1 µs; otherwise BLOCKED, with
     the census attached, because the interference measurement would have no reference.

---

## 4. Stage 2 — measurement protocol

### 4.1 Producer (`b1_ring.c`)

- One pinned thread. Frame = 16 B: 8 B payload (a counter-derived pattern, so the ring is not compressible) + 8 B
  monotonic sequence number. The sequence number is the ground truth for drops and for dump verification.
- Ring: anonymous `mmap`, `MAP_POPULATE`, `MAP_HUGETLB` if the census allowed it (record which), sizes **512 MB** and
  **2 GB** (or the D-1 substitute). Pre-touched before the clock starts.
- Pacing: bursts every 1 ms of `rate × 1 ms / 16` frames, scheduled by `clock_nanosleep(TIMER_ABSTIME)`. A burst that
  starts more than **1 s** behind schedule is a **drop event**: log it with the lag and the sequence number, then
  resynchronise. Also log the maximum scheduling lag seen.
- Rates (IMPOSED by the brief, from ANGLES §2.2): **3.2 MB/s** (10 % farmed), **32 MB/s** (100 % farmed), **60 MB/s**
  (ADC ceiling).
- Every 10 s, write a one-line status: achieved MB/s over the window, cumulative drops, head sequence, oldest live
  sequence (so the **measured** ring depth in seconds = (head − oldest) × 16 / rate).

### 4.2 Concurrent real-time load

- Core 1: `e1_inference.py` in a continuous loop over the 256-snippet set, logging p50/p99 per 60 s block and running
  its bit-identity gate once per block.
- Core 2: the H-b limiter harness in a loop at 100 Hz, alternating 96-cell and 3,564-cell inputs per 60 s block,
  logging p50/p99 per block, gate per block.
- Both run for a **10-minute baseline** before the producer starts and continue throughout. Interference is read as
  the per-block p50/p99 with the producer on versus the baseline blocks of the same session.

### 4.3 Trigger, freeze and dump (`b1_dump.c`)

- At scripted times (10, 20 and 28 minutes into each 30-minute cell), the dumper snapshots the ring indices and copies
  the **last N seconds** (N = **10, 60, 300**, one per trigger, order fixed: 10 → 60 → 300) to a new file on the eMMC
  partition, `fsync`, and records wall time per dump. The producer **keeps running** during the dump (a flight recorder
  does not stop recording).
- **Verification gate (same run):** the dumped file's sequence numbers must be contiguous and their count equal to
  `N × rate / 16` within one burst. A discontinuity means the producer overwrote the window during the copy; report it
  as GATE FAIL for that (rate, ring, N) with the overwrite depth. Do not adjust N or the ring to make it pass; the
  failure is a result (it says how much headroom the ring needs over the window at that rate).
- Report dump time, achieved copy MB/s, and whether the producer dropped during the dump.

### 4.4 eMMC as a medium (`b1_emmc.sh`)

- Sequential write of 1 GB files back to back for **≥ 5 minutes** with `O_DIRECT` (or `conv=fsync` if `O_DIRECT` is
  refused; record which), reporting sustained MB/s per file and overall. Delete the files afterwards. Record the
  partition's free space before and after.
- **DERIVED (endurance ASSUMED, stated in the same table cell):** years to wear-out if this eMMC were the ring medium at
  3.2, 32 and 60 MB/s, for P/E = **3,000** (MLC-class) and **500** (TLC-class), write amplification 1.0, capacity from the
  census. Also the DERIVED time per dump for N = 300 at each rate from the measured write rate, for comparison with the
  measured dump times.

### 4.5 Protocol order and repeats

| Phase | Rate | Ring | Duration | Repeats |
|---|---|---|---|---|
| P0 baseline | — | — | 10 min | per session |
| P1 | 3.2 MB/s | 512 MB | 30 min | 3 |
| P2 | 32 MB/s | 512 MB | 30 min | 3 |
| P3 | 3.2 MB/s | 2 GB | 30 min | 3 |
| P4 | 32 MB/s | 2 GB | 30 min | 3 |
| P5 | 60 MB/s | 2 GB | 10 min | 2 |
| P6 eMMC write | — | — | ≥ 5 min | 2 |

Each phase: census before and after; governor pinned; `timeout -k` on every child. If a phase cannot complete (board
reset, thermal throttle seen in `cpustat`), record it and continue; do not silently rerun.

### 4.6 What is reported (`results/B1/results_B1.md`, capability table, no verdict)

For each (rate, ring): achieved MB/s (MEASURED), drop events (MEASURED), measured ring depth in seconds (MEASURED, by
sequence span) beside the arithmetic depth (DERIVED), producer CPU % on its core (MEASURED, **upper bound on a DMA
path**), inference p50/p99 with and without the producer (MEASURED), limiter p50/p99 with and without (MEASURED), dump
time and gate result for N = 10 / 60 / 300 (MEASURED), and any thermal or frequency event. Then the eMMC row: sustained
MB/s (MEASURED), years-to-wear-out per rate and P/E assumption (DERIVED/ASSUMED), dump time predicted vs measured.

Two flags, defined now so they are not invented later:

- **SUSTAINED** = achieved ≥ 99 % of target, zero drop events over the full phase, all three dump gates pass.
- **RT DISTURBED** = inference p99 or limiter p99 in producer-on blocks exceeds the session's baseline p99 by more than
  **20 %**. A flag, not a failure; report which core assignment produced it.

---

## 5. Deliverables

1. `results/B1/census.md` (Stage 1, committed first).
2. `board/b1_ring.c`, `board/b1_dump.c`, `board/b1_emmc.sh`, `board/run_b1.sh`, `board/b1_report.py`.
3. `results/B1/results_B1.md` (the capability table, flags, bounds and what was not measured), `results/B1/b1.json`,
   per-phase logs and censuses under `results/B1/raw/`.
4. One row each in `results/X/README.md` and `results/RESEARCH_DOSSIER.md` §9, and a dated note under ANGLES §B.3 that
   points to the results.

## 6. What not to do

- Do not present the CPU producer's cost as the cost of telemetry farming by DMA.
- Do not tune ring size, N or pacing after seeing a dump gate fail; report the failure.
- Do not run the eMMC test on an SD card and call it eMMC; name the medium.
- Do not leave the board with the `performance` governor set or with dump files on the partition.
- Do not claim anything about HyperRAM, MCU SDRAM or any MCU product from this measurement; the comparison column stays
  DERIVED arithmetic with its sources.

---

*Census first. Pin everything. Keep the real-time loops running the whole time. Verify every dump against the sequence
numbers in the same run. Report bounds, not conclusions.*
