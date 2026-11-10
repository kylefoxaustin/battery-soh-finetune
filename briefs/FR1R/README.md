# Build Brief — FR1-R: re-rate the FR1 cases with a scheme that has a "not observable" state and a closed data-rate list

**Licence of this document:** public domain (CC0). **Written:** 2026-11-10. **Origin:** FR1 results §7
([`results/FR1/results_FR1.md`](../../results/FR1/results_FR1.md)); SYNTHESIS §5. Same 150 cases, same documents, same
two-rater two-branch procedure as [`briefs/FR1/README.md`](../FR1/README.md); only the rating scheme changes.

> ## ▶ APPROVED 2026-11-10 — rate now (`2541d02`), both raters as fresh sub-agents in sparse main-only clones
>
> The pre-registration is accepted **without changes**. Two of its choices improve on FR1 and are endorsed: the
> **union document set** (identical inputs for both raters, so coverage cannot cause a disagreement) and the
> **sparse checkout** that excludes every FR1 rating, notes, results, review and manifest file, so blindness holds by
> construction. The launching session's disclosure that it was FR1 rater A and has read the FR1 ratings is noted; it
> is therefore neither rater, and that is the right call (it may still run the agreement analysis afterwards).
>
> **Run order.** Rater A: conventions commit first (before any fetch), then fetch, rate, commit `rater_A_notes.md`,
> `ratings_A.csv` and the launch prompt on `fr1r-rater-a`; push. Then rater B the same on `fr1r-rater-b`, launched
> only after A's branch is pushed and never fetching it. Then merge both, write `analysis/FR1R_agreement.py`, produce
> `results/FR1R/results_FR1R.md` (verdict and shape first, κ with the D-3 disclosure beside it, every disagreement
> listed), `fr1r.json`, the index rows and the dated notes under ANGLES §B.3 and SYNTHESIS §1; set `NEXT_TASK.md`
> Status to `DONE <hash>`; push; stop. The reviewer re-derives from the two CSVs afterwards.
>
> ## ▶ START HERE (first stage: pre-registration only, then STOP) (superseded: done at `2541d02`)
>
> 1. `git pull` on `main`.
> 2. Read this brief, `results/FR1/FR1_preregistration.md` §3–§6 (the procedure being reused) and §8 (D-1 to D-6).
>    **Do not open** `results/FR1/ratings_A.csv`, `ratings_B.csv`, `rater_A_notes.md`, `rater_B_notes.md`,
>    `results_FR1.md`, `fr1.json` or `review/` before your ratings are committed: a rater primed by the FR1 ratings is
>    not blind.
> 3. **Stage 1.** Write `results/FR1R/FR1R_preregistration.md`: the scheme in §3 below with every threshold filled in,
>    the case list carried over unchanged from `results/FR1/FR1_cases.md` (75 PE after D-1, 75 BR), the rating orders
>    (`default_rng(11)` for rater A, `default_rng(12)` for rater B), and the branch names `fr1r-rater-a` /
>    `fr1r-rater-b`. Commit with "before rating" in the message; set the Status line in `NEXT_TASK.md` to
>    `AWAITING APPROVAL <hash>`; push; stop.
>
> The reviewer approves by editing this box. Then rater A rates on its branch; rater B is a fresh-context session or
> sub-agent in a main-only clone (FR1 D-6 is accepted practice); the analysis runs only after both branches exist.

---

## 0. Why

FR1 failed its agreement gate (κ 0.19) for one reason: the scheme had no answer for a defect that no in-vehicle signal
would show at any window, and the two raters' pre-written conventions mapped it to opposite ends of the scale. On the
cases where neither rater invoked that rule, they agreed at κ 0.84 (exploratory). The cause-type agreement was 0.87–0.90.
FR1-R adds the missing state, turns the data-rate free text into a closed list, keeps everything else, and would gate.

The retention leg of ANGLES §B.3 is the only place this matters: B1 measured what the DRAM tier holds (671 s at
3.2 MB/s), and the roadmap needs to know whether root causes in the public record need **seconds-to-minutes at ≥ kHz**
(the ring buffer) or **hours-to-months at ≤ 10 Hz** (flash or cloud).

## 1. Rules (as FR1 §1, plus)

- Rate from the same document set, by URL, as the FR1 manifests (`rater_A_documents.json`, `rater_B_documents.json`
  may be opened **only** for their URL and hash fields, by a script, not read as text).
- The FR1 ratings are not consulted. Both raters write their own conventions file before opening a document.
- κ gate **≥ 0.6** on item 3 collapsed to four states (§3.3). Disagreements reported, never reconciled.

## 2. Data

Unchanged: `results/FR1/FR1_cases.md` (PE001–PE005, PE007–PE076; BR001–BR075); NHTSA Part 573 reports, chronologies,
and ODI résumés where FR1 §4.1 allows. Public domain.

## 3. The scheme (closed lists; write exactly)

### 3.1 Item 1, cause type — unchanged from FR1 §3.3.
### 3.2 Item 2, evidence that identified the cause — unchanged.

### 3.3 Item 3, pre-event window — **six states**

> *If the investigator had only data recorded on the vehicle before the event, how long a span, ending at the event,
> would have been needed to identify this cause?*

| State | Write exactly | Meaning |
|---|---|---|
| 0 | `not observable` | no in-vehicle signal would show the cause at any window length (a wrong or defective part found by teardown; an assembly error; a design weakness identified by analysis). The field record could at most locate the event. |
| 1 | `<=1 s` | a snapshot at the trip (DTC + freeze-frame) identifies it |
| 2 | `(1,40] s` | seconds before the event are needed |
| 3 | `(40,80] s` | about a minute |
| 4 | `(80,700] s` | minutes |
| 5 | `>700 s` | a full session, many cycles, days or months |
| — | `cannot judge` | documents too thin to map (reserved for that; not for "not observable") |

Ties go to the lower state unless the document states a time scale. **Base-rate cases are rated with the same six
states**; most are expected to be state 0 under this scheme — that is the point of the control.

### 3.4 Item 3b, data-rate class — **closed list**, required for states 2–5 (`n/a` for 0, 1 and *cannot judge*)

`<=10 Hz` · `10 Hz–1 kHz` · `>=1 kHz` — the rate of the *fastest* signal the rater names. Signals stay in free text.

### 3.5 Item 4, confidence — unchanged. Item 5 flags — unchanged (no cause stated; software-only; out of scope).

## 4. Readouts and decision (pre-register the numbers)

- **Exclusions** as FR1 §4.3 (both-rater flags). **Denominator** = PE cases, not excluded, rated with a state by both
  raters and **not `not observable` by either** (conservative: a case either rater calls not-observable leaves the
  denominator; the count is reported).
- **Conservative reading** = the lower state of the two, among states 1–5.
- **Primary:** fraction of the denominator at **> 80 s** (states 4–5), with Wilson CI; and the **ring-buffer-shaped
  fraction**: states 2–4 **and** rate class `>=1 kHz` (seconds-to-minutes at high rate), using the lower rate class of
  the two raters.
- **Secondary:** > 1 s; the state distribution; the rate-class distribution for states 2–5; the base-rate sample on the
  same readouts; everything by component group; one case per cluster; every disagreement listed.
- **Gate:** κ on item 3 collapsed to {not observable, ≤ 1 s, (1, 80] s, > 80 s} over cases both raters rated with a
  state (PE and BR together, as FR1), **≥ 0.6**; and ≥ 10 PE cases in the denominator.
- **Decision** (same thresholds as FR1 §3.5 on the > 80 s fraction): RETENTION IS A NECESSITY (≥ 50 %, CI lower bound
  > 20 %) · RETENTION IS A CONVENIENCE (< 20 % at > 40 s) · UNCLEAR · UNGATED. **Plus one new line**, decided on the
  ring-buffer-shaped fraction: **RING BUFFER SHAPED** if ≥ 25 % with CI lower bound > 10 %; **FLASH/CLOUD SHAPED** if
  the > 80 s fraction is ≥ 50 % but the ring-buffer-shaped fraction is < 10 %; otherwise MIXED.

## 5. Deliverables

Stage 1: `results/FR1R/FR1R_preregistration.md`. Stage 2: `results/FR1R/rater_A_notes.md`, `ratings_A.csv` (branch
`fr1r-rater-a`); `rater_B_notes.md`, `ratings_B.csv` (branch `fr1r-rater-b`); then `analysis/FR1R_agreement.py`,
`results/FR1R/results_FR1R.md` (verdict first; κ with the D-3 disclosure beside it), `fr1r.json`, index rows, and a
dated note under ANGLES §B.3 and SYNTHESIS §1.

## 6. What not to do

- Do not read any FR1 rating, note, result or review file before your ratings are committed.
- Do not reconcile disagreements. Do not move a threshold after results.
- Do not put a dollar figure anywhere in this study.

---

*Same cases, same documents, one missing state added, one free-text field closed. Rate twice, blind. Gate.*
