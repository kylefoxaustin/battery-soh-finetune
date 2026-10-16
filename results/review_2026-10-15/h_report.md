# Independent review — Experiments H and H2 (per-cell vs min/max vs pack-mean charge limiting; board latency)

Reviewer role: adversarial senior reviewer, BMS control + embedded measurement. Repo: `<repo>`
at `731c2b7`. No repo file was modified; no board access. Scratch: `<scratch>/review/h/` (scripts `changan_R.py`,
`weihai_sync.py`, `weihai_zoh_vs_interp.py`, `weihai_attrib.py`, `h_partial.py`, cross-compiled `h_limiter_a64.s`).

Tagging: **[read]** = taken from a repo file (path:line); **[recomputed]** = my own calculation, method stated.
Host timings are never board numbers and are not reported as such.

---

## Critical

### C1. H2's pack-mean margin headline is an artefact of a November-2024 telemetry outage that the pipeline ingested as real cell states

**Claim under review** [read `results/H2/results_H2.md` §"Against a pack-mean-only limiter"; `results/RESEARCH_DOSSIER.md:332`]:
"The smallest margins with ≤ 0.1 % unsafe frames are 75 mV / 10 °C and 100 mV / 10 °C. That is wider than H's 30 mV /
10 °C, even though the cell spread here is small. At 75 mV / 10 °C limiting from extremes would charge a median 45 %
faster … 54 %." Dossier: "Extremes information recovers 26–54 % charge time."

**Evidence** [recomputed from the cached frames `data/weihai/frames/*.npz` with the repo's own `H2_replay.limiters`/`taper`/`c_t`, all 1,929 sessions, 1,590,811 frames — matches `replay.json`]:

| Margin | Unsafe frames, all sessions | of which Nov-2024 | by rack (top 3) |
|---|---|---|---|
| 30 mV / 10 °C | 2,769 (0.174 %) in 535 sessions | **1,507** | rack 8: 1,149; 5: 400; 1: 383 |
| 50 mV / 10 °C | 1,866 (0.117 %) | **1,328** | 8: 903; 5: 345; 2: 255 |
| 75 mV / 10 °C | 1,424 (0.090 %) | **1,244** | 8: 714; 5: 329; 2: 252 |
| 100 mV / 10 °C | 1,231 (0.077 %) | **1,178** | 8: 601; 5: 328; 2: 252 |

Safe-margin set recomputed with the pre-registered rule (≤ 0.1 % unsafe), median `S_pack` in brackets:

- all sessions: `75_10` (44.9 %), `100_10` (53.7 %)  — reproduces `replay.json`.
- **excluding Nov 2024** (1,638 sessions, 1.38 M frames): `30_10` (**33.4 %**), `50_10`, `75_5`, `75_10` (45.2 %), `100_5`.
- excluding any session with a cell > 100 mV from the rack mean (1,755 sessions): `30_10` (**33.5 %**), same set.

So with the outage month removed, H2's smallest safe margin is **(30 mV, 10 °C) and the pack-mean figure is ~33 %,
i.e. the same as H's (30 mV, 10 °C) / 34 %**. The sentence "wider than H's even though the cell spread here is small"
is explained by bad data, not by LFP or by the long string.

**What the November data actually is** [recomputed from raw `data/raw/weihai/OperationCondition_202411_All.mat`, decoded with the repo's `mcos_dt`]:

- `Operation48` rack 9 (Charge, 3.34 h): 145 of 396 cell-voltage series (cells 251–395, contiguous modules) have **1 log
  in the whole operation**; their last log is 133,232 s (37 h) before EndTime; their held value is the start-of-charge
  3.115 V while the other 251 cells climb to 3.45–3.55 V. The ZOH therefore manufactures a 330–360 mV "spread".
- `Operation48` rack 8: **283 of 396 series have a single log, time-stamped 120,667 s (33 h) before StartTime.**
  Because `H2_replay.extract_file` sets the grid start at `max(st, t0)` with `t0 = max over series of first log`
  [read `analysis/H2_replay.py:75-76`], a series whose *only* log predates the operation passes the "has logged" rule
  and is held stale for the entire session. The pre-registered guard only covers late first logs, not dead series.
- `Operation48` rack 3: cell series are healthy (154–185 logs) but **the rack current series has 1 sample**, so
  `len(ti) < 2` [read `H2_replay.py:78`] wrote the "empty" marker. All 24 empty sessions are racks 3 and 7 for
  Nov ops 46–68 [recomputed: listing of `empty` npz files]. `results_H2.md` deviation 1 attributes them to cell/probe
  series not logging; for the case checked (Op48 rack 3) the trigger is missing rack current.
- Sessions with any cell > 100 mV from the rack mean: Nov 83, every other month 9–17 [recomputed]. Largest
  single-cell deviations are all Nov ops 48–68, racks 8/9/1, 320–359 mV, present in 85–100 % of the session's frames.

**Why the primary verdict survives:** a stale cell held at 3.115 V has `taper = 1`; it never becomes `vmax` and never
lowers `L_cell` below `L_mm`. `S_mm` is unaffected (median 0.00 % with and without Nov [recomputed]). Only the
pack-mean quantities (which depend on `vmean`) and the descriptive spread statistics are corrupted.

**Required fixes:** (i) a staleness screen — healthy series have a 600 s heartbeat (ZOH age never exceeds 590 s in
clean operations [recomputed on Oct ops]); any age > 600 s means the series is dead and the cell must be marked
missing, not held; (ii) a per-session data-quality report (dead series count, stale fraction); (iii) re-run the
margin sweep and rewrite the H2 margin paragraph, the "wider than H" sentence, and the dossier's "26–54 %" and
"45–54 %" lines; (iv) correct deviation 1.

---

## Major

### M1. The per-cell vs min/max comparison cannot detect the mechanism that is supposed to make per-cell limiting valuable

The write-ups say this [read `results/H/H_preregistration.md` §0.2; `results_H.md` "What would change the H-a answer";
dossier §10.2], so it is disclosed. But the consequence for the verdict is understated.

- **Algebra.** `C_T` is unimodal, so `min_p C_T(T_p) = min(C_T(Tmin), C_T(Tmax))` exactly, and `taper∘soc` is monotone,
  so `min_k taper(V_k) = taper(Vmax)`. Hence `L_mm = (min_p C_T)(min_k taper) ≤ min_k C_T(T_p(k)) taper(V_k) = L_cell`
  on every frame, with equality unless the coldest/hottest probe's cells are not the top-voltage cell. The only channel
  for a per-cell gain is the slope of `C_T` at the probe temperatures times the probe spread (3 °C median in Changan,
  4 °C in Weihai [read `replay.json`]). In the flat 25–40 °C band the gain is identically zero. **The test is a test
  of the assumed map's slope at the fleet's climate, not of per-cell limiting.** [recomputed, 8 Changan vehicles,
  748 k frames: 93 % of frames where `L_cell ≠ L_mm` have the coldest probe < 25 °C.]
- **Every cell shares one map** [read `analysis/H_replay.py:106,114-115`; `H2_replay.py:111-116`]: same OCV→SOC, same
  taper, same `C_T`. No per-cell capacity, resistance or ageing enters. That is precisely the physical reason a
  per-cell limiter is argued for (an aged / high-R cell hits its voltage or anode-potential limit before `vmax` says
  so), and it is excluded by construction.
- **Post-hoc quantification of the excluded mechanism, with Changan data** [recomputed, `changan_R.py`, 40 vehicles,
  38 usable; **post-hoc, DERIVED, model ASSUMED**]. Per-cell effective 10-s resistance from consecutive charging full
  frames with |ΔI| ≥ 20 A, ≤ 30 s apart, median over ≥ 10 events per vehicle (median 264 events): per-cell
  `R_k` median 0.49 mΩ; **`R_max / R_med = 1.20`, CV 5.6 %** (p10–p90 across vehicles 4.7–9.5 %); sign-consistent
  in 99 % of events. A voltage-headroom limiter `I_allow = I_now + min_k (V_lim − V_k)/R_k` (per-cell) versus
  `I_now + (V_lim − Vmax)/R_max` (min/max with the worst-case R it must assume) on frames with `vmax ≥ 4.0 V`:
  **median extra admissible current +2.0 % (vehicle p10–p90: 0.7–4.6 %), within-vehicle p90 +4.4 %**; the
  constraining cell is not the max-V cell in ~50 % of those frames. A min/max limiter that used a *typical* R
  instead would exceed the per-cell headroom in 99.8 % of frames. So under a per-cell-parameter model the gain is
  above the pre-registered 1 % but modest, and bounded by the IR spread (~20 %) times the IR-governed share of the
  limit. This is an admissible-current gain near top-of-charge, not a charge-time saving; converting it needs a
  trajectory model. It should be reported as the honest upper envelope of what H could not see.
- **Trajectory held fixed is off by an order of magnitude at the top.** Recorded charging current: Changan median
  −17 A (p5 −116 A) ≈ 0.14 C on 120 Ah [recomputed, vin100]; Weihai median −134 A on an implied 282–292 Ah rack ≈
  0.46 C [recomputed from rack Ah vs SOC 4→97 %]. The assumed ceiling is 1.5 C. At 1.5 C the polarisation on a
  0.49 mΩ cell is ≈ 88 mV ≈ 9 % SOC at the top of the Changan OCV table (10 mV per % SOC [read `ocv_full.json`;
  recomputed `soc(4000)=81.5 %, soc(4030)=84.5 %`]). The replay evaluates the taper at voltages the cells would never
  show at the limiter's current. Both limiters are affected alike, so the *ratio* is less wrong than the levels, but
  the "first-order only" caveat [read `H_preregistration.md` §1] undersells it.
- Also: the OCV table is "ASSUMED (built from early-life BMS SOC at wake)" [read `data/changan/ocv_full.json` tag], so
  "SOC" in H is the Changan BMS's own SOC mapped through `vmax`. Fine for a shape, but it should be said in `results_H.md`.

### M2. The pack-mean baseline is a straw man, and the 26–54 % numbers are mostly a self-inflicted temperature-margin derate on the assumed map

- GB/T-32960 scalar frames carry max/min cell voltage, max/min temperature **and their indices** (`imin`, `imax`,
  `itmax` are present in the Changan extraction [recomputed: `vin100.npz` keys]). No production BMS limits on pack mean.
  The brief imposed the pack-scalar baseline, so running it is legitimate; elevating "pack-mean-only limiting is
  consistently unsafe without large margins" to a joint H/H2 conclusion [read `results_H2.md` "What H and H2 together
  say"; dossier §7, §8] is a tautology of the model.
- Decomposition of the 34 % [recomputed]: at a typical Changan `tmean` of 28–31 °C, a 10 °C margin evaluates `C_T` at
  18–21 °C → 1.08–1.26 C instead of 1.5 C, a **16–28 % derate in the flat band where nothing is happening**; the
  30 mV margin shifts SOC by ~3 % and the taper by ~15 % at 4.0 V (0.489 → 0.418). Both are properties of the assumed
  `C_T` slope below 25 °C and the assumed taper, not of the data. The curve is honest; the prose should say the
  benefit is dominated by the T-margin term and would vanish with a flatter cold slope.
- The 1.001 unsafe tolerance is fine: unsafe fraction at (30 mV, 10 °C) is 0.002 % at tol 1.0, 1.001 and 1.01
  on 8 vehicles [recomputed]. The threshold 0.1 % is CHOSEN and the result is frame-pooled; one bad month (C1) or a
  few outlier sessions set it — that is the structural weakness, not the tolerance.
- Wording: `S_pack = 1 − t_cell/t_pack` is time **saved**; 34 % shorter = 52 % *faster*, 45 % shorter = 82 % faster.
  "charge a median 34 % faster" [read `results_H.md`, `results_H2.md`, dossier §7–8] is the wrong word.

### M3. Board measurement: sound as a p50/p99 microbenchmark, over-read as repeatability and as the silicon answer

- **Timer resolution.** Every reported latency is an integer multiple of 41.667 ns (1/24 MHz, the i.MX generic timer):
  p50s are exactly 36, 70, 116, 354, 140 and 1,251 ticks [recomputed from `results/H*/board/results.jsonl`]. The
  statement "p50 range across repeats ≤ 1 ns" [read `results_H.md` "Repeatability"] is quantisation (the same tick
  count), not 1 ns repeatability; H2's "≤ 42 ns" is exactly one tick. Each sample also includes two `clock_gettime`
  calls [read `board/h_limiter.c:134-136`], not subtracted (~tens of ns of the 1,500 ns at N = 96).
- **Representativeness.** Frames are pre-decoded `int16` arrays read sequentially from a 2.6–110 MB buffer
  [read `h_limiter.c:103-106`]; the brief's "parse/ingest 96 voltages + 32 temperatures" [read brief §H.3] is not
  implemented — the AFE/isoSPI/CAN decode that dominates a real BMS loop is zero-cost here. Data-dependent branches
  (`c < best`) cycle through 10,000 distinct frames, so branch-predictor memorisation is not a concern; the compiler
  did not remove work (aarch64 `-O2` keeps `fdiv`/`fmadd`/`str` in the loop, no NEON vectorisation; 26 cycles per
  cell at 1.8 GHz [recomputed: cross-compiled `h_limiter_a64.s`]). The FMA explanation for dR = 4.8e-7 is confirmed:
  the R update contracts to `fmadd s2, s1, s5, s2`; the same binary on x86 (no FMA) gives dR = 0 and passes the gate
  [recomputed on host — a semantics check, not a timing].
- **Worst case is discarded.** Max 57–724 µs (H) and 61–217 µs (H2) [read `footprint.json`] are attributed to
  preemption and then the "1.1 % of a core" uses p99 (107 µs × 100 Hz = 1.07 %, arithmetic correct). Mean-based
  utilisation is 0.54 %; worst-case schedulability is 2.2 %. A `SCHED_FIFO` + `isolcpus`/`nohz_full` run (or at least
  `mlockall`) would have given a real worst case at no board risk; the census shows `wireplumber` at 3.5 % after H
  [recomputed from `census_after.json`].
- **Wrong core for the question.** The brief's silicon question is "is per-cell enforcement an A55+DDR-class
  workload?" The measured answer — 52 µs for 3,564 cells, 48 KB of state — says it is an **M-class** workload. The
  i.MX 95 has an M7 (800 MHz) and an M33 on the same die; neither was measured. At 26 A55-cycles/cell, an M7 estimate
  is ~90–180 µs per 3,564-cell update (ASSUMED 20–40 cycles/cell), comfortably inside a 10 ms period. That is the
  missing measurement for the control-lever argument, and it would also remove the Linux preemption caveat.
- **Reproducibility gap.** No script in the repo or git history builds, pins, repeats, censuses or gates the H-b/H2-b
  run (`grep` for `h_limiter`/`taskset` finds only prose and the Study-1 `run_all.sh`) [recomputed]. Governor and
  frequency exist only as a tag string in `footprint.json`; no `scaling_cur_freq`/`cpuinfo` capture.

### M4. The H2 gate exercises the limiter mostly in its degenerate region

`h2_ref.stream` takes the first `nframes//40 = 250` common grid times per operation, i.e. the first ~2,500 s of each
charge [read `board/h2_ref.py:48-59`]. In the resulting 10,000 gate frames `vmax` median is 3,298 mV, p99 3,411 mV; the
taper is active in **348 frames**; the argmin is unique in **867 (N = 396) and 323 (N = 3,564)** frames; all cells tie in
864 / 274 [recomputed: host rebuild with `h2_ref.py build`, identical tie counts to `gates.jsonl`, 9,133 / 9,677]. The
gate still has teeth (hundreds of non-trivial argmins, setpoint Δ = 0), but it should sample late-charge frames so the
LFP taper and the `VLIM` branch are tested. H's gate is healthier: 44 % unique-argmin frames, 11 % all-tie [recomputed].

### M5. H2's logging model in the pre-registration is wrong; the ZOH consequence for the margin sweep was checked and is small (outside C1)

Pre-registration: "change-logged with its own timestamps … ZOH … ASSUMED to match change-logging with a deadband"
[read `H2_preregistration.md` §0, §1]. Raw data [recomputed, Oct ops 1 and 10, rack 1]: cell voltages are logged
**periodically at ~60 s (p90 120 s) per cell, staggered across cells** (only 14 of 1,124 log instants in Op1 carry all
396 cells; most carry < 50), with a 600 s heartbeat (every 600 s gap has step 0); 11–13 % of logs repeat the previous
value, step sizes peak at 1–2 mV — not change-triggered. Temperatures: integer °C, median gap 220 s, 600 s heartbeat.
ZOH age at the 10 s grid: median 36–45 s, p90 127–200 s, max 590 s. Consequences: the 1.59 M "frames" are ~6× oversampled
composites of values up to minutes old; `dVmax/dt` reaches 0.1–0.2 mV/s at the knee, so a 200 s-stale cell can read
20–40 mV low. **Check performed:** rebuilding 8 Oct rack-1 sessions with linear time-interpolation instead of ZOH
leaves the safe-margin set unchanged ((30,10) and (50,5) safe in both), `S_pack` within 0.4 pp, and `S_mm` = 0 in both
[recomputed, `weihai_zoh_vs_interp.py`]. So the hold is benign in healthy months; the failure mode is dead series (C1).
The pre-registration text should be corrected and the heartbeat used as the validity criterion.

---

## Minor

1. `results_H.md`: "p99 varies by ≤ 1.5 %" — N = 324 p99 range 10,459–10,667 ns = **2.0 %** [read `footprint.json`].
2. `results_H2.md`: "p99 varies ≤ 0.2 %" — N = 396 range 11,834–11,875 = **0.35 %** [read `footprint.json`].
3. `results_H.md`: "p99 ≈ 2.1 × p50, consistent with the 6 % of frames that also run the resistance update". The 6 %
   holds for the N = 96 frame set; for N = 1,000 the current is sub-sampled every 11th frame and **26.8 %** of frames
   take the branch [recomputed: host rebuild of the frame files with `h_ref.py build`]. The ratio is still ~2.2, so the
   explanation is incomplete.
4. `results_H2.md` deviation 1 (empty sessions) misattributes the cause for the case checked; see C1.
5. `results_H2.md` lists 8 monthly files; `data/raw/weihai/` currently holds 7 `.mat` (202505 absent) while
   `data/weihai/frames` has 198 May sessions. Extraction is not reproducible from the current tree for May.
6. The "constraining cell is not the max-V cell" 21.5 % / 36.1 % figures are correct as computed but are mostly
   "coldest-probe cell at taper 1 with the pack below the knee" cases; the write-up's reading ("the binding limit is
   a temperature limit") is right, but the number says nothing about per-cell value — 8.2 pp of the 21.5 % occur with
   `L_cell = L_mm` [read `replay.json`: 21.5 % vs 13.3 %].
7. The pre-registered metric is the *median session* saving. Fleet-wide, the session mean is 0.44 % (H) and the
   Ah/time-weighted total saving on 8 vehicles is 0.30 % [recomputed from `replay_sessions.npz` and `h_partial.py`];
   14.8 % of H sessions save ≥ 1 % and 0.73 % save ≥ 5 %. Reporting these alongside the median would be fairer to the
   cold tail without changing the verdict.
8. Post-hoc band table in `results_H.md` reproduces exactly from `replay_sessions.npz` (2,855 / 18,351 / 38,397 /
   226,690 / 539 sessions; 0.70 / 0.93 / 0.88 / 0.00 / 3.30 %) [recomputed].
9. MCOS datetimes are UTC-naive wall-clock: charge starts peak at 10:00–12:00 decoded (74 of 217 at 11 h), consistent
   with Shandong's midday valley tariff if decoded = local; implausible (18:00–20:00 local) if decoded = UTC
   [recomputed]. Irrelevant to the verdict; worth one line in the write-up.
10. `h_limiter.c` carries a per-cell `vlim[]` array that is constant (`VLIM`) — the "per-cell voltage limit" in the
    10 B/cell resident-state table is never per-cell [read `h_limiter.c:58`]. Fine for sizing; the prose implies more.
11. "Scaling ≈ 14.7 ns per cell" checks: (14,750 − 1,500)/904 = 14.66; (52,126 − 5,834)/3,168 = 14.61 [recomputed].

---

## Missed opportunities (ranked by expected value / cost)

1. **Re-run H on Changan's own cold sessions with a pre-registered conditional test (cheap, high value).** 2,855
   sessions have a median coldest probe < 10 °C and 18,351 are 10–20 °C [read `results_H.md`; recomputed]. That is a
   large cold sub-fleet already in hand; H2 was not needed to ask the cold question. Pre-register the sub-fleet
   threshold and power, and report the Ah-weighted saving. Also add a *per-cell-parameter* limiter (R_k from current
   steps, as above; Q_k if a per-cell Ah/ΔSOC estimate is feasible) as a second pre-registered arm — this is the
   actual engineering claim.
2. **Data-quality screening as a first-class result (required anyway for C1).** Dead/stale series, module-wide
   dropouts (racks 3/7/8/9 Nov 2024), heartbeat-based validity. This is also per-cell *monitoring* value: a module of
   145 cells going silent for 37 h is detectable from per-cell streams and — note for the min/max thread — would also
   show as `vmin` frozen at 3.115 V.
3. **Cortex-M7/M33 build and timing of `h_limiter.c`** on the same i.MX 95 (bare-metal or Zephyr), with the real
   ingest path (frame parse) included. This answers the silicon question the A55 run only implies.
4. **Discharge power limits.** H/H2 only limit charge (`vmax`). Discharge is constrained by the min-V cell under load,
   where per-cell R matters more (I·R_k subtracts from a low OCV) and LFP's flat plateau makes voltage a late
   indicator. Same replay machinery, `status` discharge frames exist in Changan.
5. **Thermal-runaway / thermal-fault early warning** on the McMaster thermal-fault set the dossier says was downloaded
   and inspected but not used [read dossier §10.6] — it has ground truth, unlike F.
6. **Balancing scheduling / weak-cell identity.** Quantified quickly [recomputed]: the end-of-charge top cell is the
   same cell in 31–83 % of sessions per Changan vehicle (10 vehicles) and 13–44 % per Weihai rack; but GB/T frames
   already carry `imax`/`imin`, and in Weihai 396/396 cells are past the 3.40 V knee whenever `vmax ≥ 3.45 V` (racks
   are well balanced). Low expected value on these datasets.
7. **Per-cell OCV-based SOC on LFP** is ill-posed on the plateau; only the knee is informative, and the racks hit the
   knee together. Low value here.
8. **Energy per update** (not measured; the brief asked for compute sizing, not energy — optional).

---

## Solid

- Pre-registration before code, for both H and H2, with thresholds unchanged and deviations enumerated
  [read commits `43485e8`, `bf6ca52`; `results_H.md` "Deviations"].
- The correction of the brief's min-cell control to the max-cell for charging, and reporting both [read
  `H_preregistration.md` §0.1].
- The tie-aware constraining-cell control; raw-argmin figures retained in `replay.json` for transparency.
- Taking the min/max extremes from the cell list so `L_cell ≥ L_mm` holds exactly, and disclosing it (deviation 5).
- Cluster bootstrap by vehicle (H) and by operation with all racks (H2) — the right resampling units.
- M2 random probe permutations as the mapping sensitivity; the verdict does not depend on the mapping.
- The primary `S_mm` verdict (NO BENEFIT over min/max under the assumed single-map model) is reproduced and is
  robust to the Nov-2024 data problem, to ZOH vs interpolation, and to the unsafe tolerance.
- C ↔ Python semantics: first-index argmin, float32 products, `VLIM` branch, clamped LUT indices, R update — all
  match; host gate passes for both maps with dR = 0 on x86; the board's 4.8e-7 dR is FMA contraction, confirmed in
  the aarch64 assembly. Linear scaling 14.6–14.7 ns/cell is consistent between synthetic (H) and real (H2) geometry.
- `mcos_dt`: internally consistent on everything checked — 171,926 / 171,927 objects decoded, timestamp count =
  value count for 396/396 series, monotone 396/396, datetime `data` is float64 ms, decoded dates fall in the file's
  month, rack current at 1.0 s cadence, 2.28 h operation matches `EndTime − StartTime`.
- Licence hygiene (CC BY-NC-SA on every Changan verdict; CC BY on H2) and the refusal to make charge-rate or
  economic claims.

---

## Bottom line

The pre-registered **primary** verdicts stand: under a single shared assumed map, per-cell and min/max limiting are
the same thing except through temperature coupling, and both fleets charge in the flat band. The **secondary** H2
pack-mean numbers (75 mV / 10 °C; 45–54 %; "wider than H") are artefacts of a November-2024 telemetry outage and must
be re-run with a staleness screen, after which H2 agrees with H (30 mV / 10 °C, ~33 %). The structural point that
should lead the write-up is that H/H2 were not able to test the mechanism per-cell limiting is actually argued for;
a quick post-hoc per-cell-resistance headroom model on Changan gives a median ~2 % (p90 ~4.5 %) admissible-current
gain near top-of-charge — above the 1 % bar, modest, and the honest next pre-registered test. The board numbers are
good p50/p99 microbenchmarks with a 41.7 ns timer tick; they show the limiter belongs on the M7/M33, which was not measured.
