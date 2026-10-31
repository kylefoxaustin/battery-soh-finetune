# Build Brief — FR1: how long a pre-event window would field data have needed to find the root cause of public HV power-electronics failures?

**Licence of this document:** public domain (CC0). **Written:** 2026-10-31. **Origin:** ANGLES report §B.3 / §C.3
([`results/OPEN_PROBLEM/ANGLES_REPORT.md`](../../results/OPEN_PROBLEM/ANGLES_REPORT.md)); promoted after B1 measured
the window the application-processor tier can hold.

> ## ▶ APPROVED 2026-10-31 — rate now, as two blind raters on two branches (D-1 to D-3 in the pre-registration §8)
>
> The first stage (`765d1f1`: 75 power-electronics cases from NHTSA component fields, 75 base-rate cases, the rating
> scheme) is accepted. FR1-P1 to P5 are accepted as written. The reviewer made three pre-rating changes, recorded in
> `results/FR1/FR1_preregistration.md` §8 and `results/FR1/FR1_cases.md`:
> **D-1** — PE006 excluded (non-plug-in by model name); 25V-811 Bentayga Hybrid added as PE076; 75 cases remain.
> **D-2** — blindness by branches: rater A on `fr1-rater-a`, rater B on `fr1-rater-b`; nothing merges to `main` until
> both exist. **D-3** — disclose that both raters are language-model sessions; κ is reproducibility, not independence;
> an optional 15-case human spot-check is defined.
>
> **Rater A (this session):** `git pull`; create branch `fr1-rater-a` from `main`; rate every PE and BR case from its
> Part 573 report (and the ODI résumé only where §4.1 allows) in the `default_rng(1)` order; write
> `results/FR1/ratings_A.csv`; commit and push the branch; set the Status lines in `NEXT_TASK.md` (on `main`) and here
> to `RATER A DONE <hash>`; stop. **Do not run the agreement analysis.**
>
> **Rater B (a fresh session, started by the reviewer afterwards):** `git pull` on `main` only; **do not fetch or open
> `fr1-rater-a`**; create `fr1-rater-b`; rate in the `default_rng(2)` order; write `results/FR1/ratings_B.csv`; commit
> and push the branch; set the Status lines to `RATER B DONE <hash>`; stop.
>
> **Analysis (either session, after both branches exist):** merge both branches into `main`; write
> `analysis/FR1_agreement.py`; produce `results/FR1/results_FR1.md` (verdict first; κ with the D-3 disclosure beside
> it; every disagreement listed, never reconciled), the index rows and the ANGLES §B.3 note; set Status to
> `DONE <hash>`; push; stop.
>
> ## ▶ START HERE (superseded: first stage done at `765d1f1`; see the APPROVED box above)
>
> FR1 is a documentary study with no compute. **As of 2026-10-31 it is the task named in `NEXT_TASK.md`**, so its state
> goes in `NEXT_TASK.md`'s Status line as usual (mirror it in the Status line at the bottom of this file). If it is
> instead run in a parallel session while another task holds `NEXT_TASK.md`, use only this file's Status line.
>
> 1. `git pull` on `main`.
> 2. Read this brief, ANGLES §B.3 and `results/B1/results_B1.md` §1 (the measured windows).
> 3. **Stage 1.** Fix the search terms, inclusion criteria and the rating scheme (§3), run the search, and commit
>    `results/FR1/FR1_cases.md` (the case list with sources and *no* root-cause text yet) and
>    `results/FR1/FR1_preregistration.md`, with "before rating" in the commit message.
> 4. Set the Status line below to `AWAITING APPROVAL <commit-hash>`, push, and stop.
>
> The reviewer approves by editing this box to "APPROVED, rate now".

---

## 0. Why FR1 exists

ANGLES §B.3 argues that a continuous MB/s ring buffer is the one place DRAM is a physical necessity, and that its value
is forensic: finding the root cause of rare, transient field failures of power electronics and packs. B1 then measured
the capability side on the board: 2 GB of LPDDR holds **671 s at 3.2 MB/s, 67 s at 32 MB/s, 36 s at 60 MB/s**, with
every dump that fitted the ring verified and the real-time loops undisturbed (MEASURED). The arithmetic for the other
media stands beside it: an MCU freeze-frame holds about **1 s**; HyperRAM's 128 MB window holds **40 s** at 3.2 MB/s;
an MCU with 256 MB of SDRAM holds **80 s** (DERIVED).

So the capability is measured. **Its value depends on one number nobody has produced: how long a pre-event window
the root cause of a real field failure needs.** If most causes are found from a 1 s freeze-frame plus statistics, the
ring buffer is a convenience and §B.3 drops to tier-neutral. If most need tens of seconds to minutes of waveform, the
80 s MCU-SDRAM figure is the line that separates the tiers, and B1's 671 s is the number that clears it.

The Hyundai/Kia ICCU campaigns are the motivating case: an 800 V OBC + low-voltage DC-DC, traced by NHTSA investigation
PE23011 to "overcurrent, overvoltage induced at the end of charging, and certain thermal loading", recalled twice
(24V-204, 24V-868), with failures recurring after the first remedy, and now under a warranty extension (SOURCED,
NHTSA documents).

---

## 1. Rules of engagement

1. **Fix the case list before reading any remedy or root-cause text.** Inclusion is decided from the component and
   symptom fields only.
2. **Pre-register the rating scheme** (§3.3) with its categories and the exact window thresholds before rating.
3. **Two raters, blind to each other:** two independent sessions, or the reviewer plus one session. Neither sees the
   other's ratings until both are committed.
4. Inter-rater agreement (Cohen's κ) is the gate: **κ ≥ 0.6** or the study is **UNGATED** and reported as such.
5. Every rating is DERIVED-judgemental and says so. No rating is MEASURED.
6. Carry the source (public domain for NHTSA; check EU Safety Gate's terms) onto every table.
7. A clean "most causes need ≤ 1 s" is a result.

---

## 2. Data (public)

- **NHTSA ODI** (public domain): Part 573 recall reports, investigation opening and closing résumés (PE / EA), and
  Technical Service Bulletins at `static.nhtsa.gov/odi/...`; the recall API at `api.nhtsa.gov`. Seed cases: PE23011,
  24V-204, 24V-868, TSB 26-EV-004H (ICCU).
- **EU Safety Gate (RAPEX)** entries for EV charging and power-electronics components (check reuse terms).
- **Published failure analyses** of OBC / DC-DC / inverter field returns (peer-reviewed or conference; cite each).

Search window: campaigns and investigations opened **2018-01-01 to 2026-10-31**.

---

## 3. Stage 1 — case list and rating scheme (`results/FR1/FR1_cases.md`, `results/FR1/FR1_preregistration.md`)

### 3.1 Inclusion (fix before searching)

A case is included if the affected component is an **on-board charger, DC-DC converter, traction inverter, charging
control unit or HV battery-management/contactor unit** in a plug-in vehicle, and the public record contains a stated
cause. Record the search terms used (component names and synonyms, in English and the source's language) and the hit
counts at each filter step. Exclude cases whose only stated cause is a software defect with no electrical event, and
cases with no cause stated.

### 3.2 Base-rate sample

A matched sample of **the same number of non-power-electronics recalls** (body, chassis, restraint) from the same period,
drawn by a fixed rule (every k-th hit of a generic query), rated with the same scheme. This is the control.

### 3.3 Rating scheme (fix before rating; each item is a closed list)

For each case, each rater records:

1. **Cause type:** transient electrical (over-current / over-voltage / short) · thermal cycling or thermal overload ·
   manufacturing or component defect · software or calibration · unknown/mixed.
2. **Evidence that identified it, as stated or implied by the record:** DTC freeze-frame · bench reproduction ·
   fleet statistics · waveform or high-rate capture · teardown only · not stated.
3. **Judged minimum pre-event window, at a stated data rate, for field data alone to have identified the cause:**
   **≤ 1 s** (an MCU freeze-frame) · **1–40 s** (within a HyperRAM window at 3.2 MB/s) · **40–80 s** (within an
   MCU-SDRAM window) · **80–700 s** (within B1's measured 2 GB window) · **> 700 s** · *cannot judge*. The rater also
   names the signals needed (e.g. switch-node voltage, DC-link current, cell voltages) and the rate.
4. **Confidence:** low / medium / high.

### 3.4 Pre-registered readouts

- Primary: the fraction of power-electronics cases rated **> 80 s** (the tier line), and the fraction rated **> 1 s**,
  with Wilson CIs; the same for the base-rate sample.
- Gate: κ on item 3 (collapsed to ≤ 1 s / 1–80 s / > 80 s) ≥ 0.6; otherwise UNGATED.
- Disagreements are **not** reconciled; both ratings are reported, and the primary uses the *lower* window of the two
  (the conservative reading against §B.3).

### 3.5 Decision

| Verdict | Condition |
|---|---|
| UNGATED | κ < 0.6, or fewer than **10** included power-electronics cases |
| **RETENTION IS A NECESSITY** | ≥ 50 % of cases rated > 80 s (conservative reading), CI lower bound > 20 % |
| **RETENTION IS A CONVENIENCE** | < 20 % of cases rated > 40 s |
| **UNCLEAR** | anything else |

---

## 4. Stage 2 — rating (after approval)

Each rater rates every case and the base-rate sample independently and commits `results/FR1/ratings_<rater>.csv` before
seeing the other's. Then `analysis/FR1_agreement.py` computes κ, the fractions and CIs, and `results/FR1/results_FR1.md`
reports verdict first, with the licence and the "judgemental" caveat, and one row each in `results/X/README.md`,
`results/RESEARCH_DOSSIER.md` §9 and a dated note under ANGLES §B.3.

## 5. What not to do

- Do not read remedies or root-cause text before the case list is committed.
- Do not reconcile disagreements; report both.
- Do not include cases without a stated cause to inflate n.
- Do not rate from memory of a case; rate from the cited document.
- Do not convert the result into a dollar figure here.

---

*Fix the list blind. Pre-register the thresholds against the measured windows. Rate twice. Report the disagreement.*

**Status:** APPROVED 2026-10-31 — rating in progress (rater A first)
