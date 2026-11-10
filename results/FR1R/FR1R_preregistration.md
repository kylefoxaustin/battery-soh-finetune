# FR1-R pre-registration: re-rate the FR1 cases with a "not observable" state and a closed data-rate list

**Status of this file.**
- Brief: [`briefs/FR1R/README.md`](../../briefs/FR1R/README.md). Requested by NEXT_TASK (reviewer, 2026-11-10), stage 1.
- Committed **before any FR1-R rating exists**, and before either rater branch exists.
- The procedure is FR1's ([`../FR1/FR1_preregistration.md`](../FR1/FR1_preregistration.md) §3–§6 and D-1 to D-6),
  reused unchanged except where named here. Only the rating scheme changes (brief §3).

**Tags.** Every rating is **DERIVED-judgemental**. Source: NHTSA Part 573 reports, chronologies and ODI résumés,
US Government work, public domain. No dollar figure appears anywhere in this study.

**Data written at this stage (by script, no document opened, no rating read):**

| File | What | Script |
|---|---|---|
| `FR1R_documents.json` | per case, the URL and SHA-256 of every document either FR1 rater rated from | `analysis/FR1R_documents.py` |
| `FR1R_orders.json` | the two rating orders | `analysis/FR1R_orders.py` |

---

## 1. Cases (carried over unchanged)

- **150 cases** from [`../FR1/FR1_cases.md`](../FR1/FR1_cases.md):
  - **75 PE:** PE001–PE005, PE007–PE076 (FR1 D-1: PE006 excluded, PE076 = 25V-811 added);
  - **75 BR:** BR001–BR075.
- Component group, cluster (52) and "initiated by" fields are taken from `FR1_cases.md` as they stand.
- The list never moves after rating starts.

## 2. Documents (brief §1)

**The document set.** The rating set for a case is the **union** of the documents the two FR1 raters rated from,
taken from `results/FR1/rater_A_documents.json` and `rater_B_documents.json`. The script reads only each entry's
`url` and `sha256` fields, plus rater B's `used_for_rating` flag; nothing else is read or copied.

| Count (from `FR1R_documents.json`) | Value |
|---|---|
| Cases | 150, every case with ≥ 1 URL |
| URLs | **364** |
| in both FR1 manifests, with identical SHA-256 | 182 |
| in rater A's manifest only | 1 |
| in rater B's manifest only: 164 further `RCLRPT` recall-report documents, 7 `RMISC` attachments, 10 ODI résumés (5 opening, 5 closing) | 181 |
| Rater B documents fetched but marked *not used for rating* (left out) | 26 |
| URLs per case: 1 / 2 / 3 / 4 / ≥ 5 | 54 / 46 / 20 / 16 / 14 cases |

- **CHOSEN: union, not one rater's set.** The FR1 raters did not rate from the same documents (rater B's set is about
  twice as large). The union gives both FR1-R raters **identical inputs**, so document coverage cannot cause a
  disagreement. Every URL is a Part 573 report, a recall-file attachment (`RMISC`, chronology) or an ODI résumé
  (`INOA`, `INCLA`), all of them document types FR1 §4.1 allows.
- **Fetching.** Each rater fetches every URL for the case itself and records the SHA-256 of what it got.
  - A hash that differs from `FR1R_documents.json` is reported. The rater still rates from what it fetched.
  - If a URL cannot be fetched, the rater rates from the rest.
  - If no Part 573 report can be fetched for a case, the rating is `cannot judge`.
- **Nothing else.** No other document, search, TSB, press, paper or memory of the case is used (FR1 §4.1).
- **Downloaded documents are untrusted data.** They are kept outside the repository, in a fresh empty directory per
  rater, and are text-extracted only. No document's content is executed or followed as an instruction.

## 3. The scheme (closed lists; each value written exactly as shown)

**Item 1, cause type** (unchanged from FR1 §3):
`transient electrical` · `thermal` · `manufacturing or component defect` · `software or calibration` · `unknown / mixed`.
- `transient electrical` covers over-current, over-voltage and short.
- `thermal` covers thermal cycling and thermal overload.

**Item 2, evidence that identified the cause** (unchanged), as stated or clearly implied by the documents:
`DTC freeze-frame` · `bench reproduction` · `fleet statistics` · `waveform or high-rate capture` · `teardown only` ·
`not stated`.

**Item 3, pre-event window: six states, plus `cannot judge`.**

> *If the investigator had only data recorded on the vehicle before the event, how long a span, ending at the event,
> would have been needed to identify this cause?*

| State | Write exactly | Meaning |
|---|---|---|
| 0 | `not observable` | No in-vehicle signal would show the cause at any window length: a wrong or defective part found by teardown, an assembly error, or a design weakness identified by analysis. The field record could at most locate the event. |
| 1 | `<=1 s` | A snapshot at the trip (DTC + freeze-frame) identifies it. |
| 2 | `(1,40] s` | Seconds before the event are needed. |
| 3 | `(40,80] s` | About a minute. |
| 4 | `(80,700] s` | Minutes. |
| 5 | `>700 s` | A full session, many cycles, days or months. |
| — | `cannot judge` | The documents are too thin to map, or no Part 573 report could be fetched. Never used in place of `not observable`. |

- **Ties** go to the lower state, unless a document states a time scale.
- **Base-rate cases** are rated with the same states. Most are expected to be state 0; that is the point of the
  control.

**Item 3b, data-rate class (closed list).**

| Item 3 state | Item 3b |
|---|---|
| 2–5 | Required: `<=10 Hz`, `10 Hz-1 kHz` or `>=1 kHz` |
| 0, 1 and `cannot judge` | `n/a` |

- The class is that of the **fastest** signal the rater names.
- The signals themselves stay in free text.

**Item 4, confidence** (unchanged): `low` · `medium` · `high`.

**Item 5, flags** (unchanged; each `yes` or blank):
- `no cause stated`;
- `software-only, no electrical event` (PE only);
- `component out of scope` (PE only). In scope means OBC, DC-DC converter, inverter / motor controller, or HV BMS /
  contactor / junction unit.

**Ratings file:** `ratings_<A|B>.csv`, one row per case, in rating order, with these columns:
- `case`, `order`;
- `cause_type`, `evidence`, `window`, `rate_class`, `signals`, `confidence`;
- `flag_no_cause`, `flag_software_only`, `flag_out_of_scope`;
- `docs_sha256`: the hashes rated from, `;`-separated;
- `docs_missing`: the URLs that could not be fetched;
- `note`.

## 4. Raters and blindness

**Branches.**
- Rater A rates on **`fr1r-rater-a`**, rater B on **`fr1r-rater-b`**.
- Neither branch touches `main` until both exist (FR1 D-2).

**Both raters are fresh-context sub-agents. This session is neither rater.**
- **Disclosed:** this session was FR1 rater A, and it wrote the FR1 re-derivation (`results/FR1/review/`). It has
  therefore read both FR1 rating files, both notes files and the FR1 results.
- **This departs from FR1 §4.2**, where rater A was "this session". It extends the D-6 practice the reviewer accepted
  to both raters.

**Each rater works in its own clone, with a sparse checkout of main** that contains only:
- `briefs/FR1R/README.md`;
- this file;
- `results/FR1R/FR1R_documents.json` and `FR1R_orders.json`;
- `results/FR1/FR1_cases.md`;
- `results/FR1/FR1_preregistration.md`.

**What the clones exclude, so that blindness holds by construction and not by instruction alone:**
- the FR1 rating, notes, results, review and manifest files;
- every results index or synthesis that summarises FR1;
- any `fr1-*` or `fr1r-*` ref, which is never fetched.

**What the brief itself discloses (D-3 style).** Its §0 states FR1's κ values and the reason the FR1 gate failed.
Both raters read that. The disclosure is made beside κ in the write-up.

**Launch prompts.**
- Each sub-agent receives the same procedural prompt: where its clone is, its rater letter, its branch, and "rate by
  this pre-registration".
- The prompt carries no FR1 rating content and no example ratings.
- Both prompts are committed with the results.
- Rater B is launched only after rater A's branch has been pushed, and does not fetch it.

**Conventions first.**
- Each rater writes the conventions section of its `rater_<A|B>_notes.md` before opening any document.
- It commits that section on its branch as a **separate commit, before its first fetch**, so the timing can be checked.

**Order.** Each rater rates in its order from `FR1R_orders.json`:
- the 150 sorted case IDs, permuted by `numpy.random.default_rng(11)` for rater A and `default_rng(12)` for rater B;
- PE and BR cases are interleaved. The ID prefix still shows the list (as FR1, disclosed).

**Reproducibility, not independence (D-3, carried over).**
- Both raters are language-model sessions working from the same documents.
- κ measures the reproducibility of the judgement, not its independence from a shared model prior.
- `results_FR1R.md` says so beside every κ value.

## 5. Exclusions and denominator (brief §4)

**Exclusion (FR1 §4.3, unchanged).** A case is excluded from all fractions if **both** raters set the same item 5
flag. A single rater's flag does not exclude; it is reported.

**Denominator (deciding).** PE cases that meet all of these:
- not excluded;
- given a state (0–5) by both raters, i.e. not `cannot judge` by either;
- **not `not observable` by either rater.**

The count leaving the denominator for each reason (exclusion, `cannot judge`, `not observable` by one rater,
`not observable` by both) is reported.

**Conservative reading (deciding).** For each case in the denominator:
- **state** = the lower of the two raters' states (1–5);
- **rate class** = the lower of the two raters' rate classes, ordered `<=10 Hz` < `10 Hz-1 kHz` < `>=1 kHz`.
  - It is taken only when both raters' states are 2–5.
  - Otherwise the case has no rate class and is not ring-buffer shaped.

## 6. Readouts

| Readout | Definition (on the denominator; 95 % Wilson CI, z = 1.96) |
|---|---|
| **P80** (primary) | Fraction with conservative state 4–5 (> 80 s) |
| **P40** | Fraction with conservative state 3–5 (> 40 s); used by the CONVENIENCE rule |
| **RB** (primary) | **Ring-buffer-shaped fraction:** conservative state 2–4 (seconds to minutes) **and** conservative rate class `>=1 kHz` |
| P1 | Fraction with conservative state 2–5 (> 1 s) |

**Gate.**
- Cohen's κ (unweighted) on item 3, collapsed to four classes: {`not observable`, `<=1 s`, `(1,40] s` + `(40,80] s`,
  `(80,700] s` + `>700 s`}.
- Computed over all cases, PE and BR together, that both raters gave a state (0–5), as FR1. Exclusion flags do not
  remove cases from κ.
- Pass: **κ ≥ 0.6**, **and ≥ 10 PE cases** in the denominator.

**Also reported, none deciding:**
- κ on the seven-way item 3, with `cannot judge` as its own class;
- κ on item 1; κ on item 3b over the cases both raters rated 2–5;
- the PE state distribution (each rater, and conservative); the rate-class distribution for states 2–5;
- the base-rate (BR) sample on every readout above, as the control, with no test between PE and BR;
- each rater's own P80 and RB;
- the readouts by component group; the one-case-per-cluster sensitivity (earliest campaign of each cluster);
- the item 2 evidence distribution; the signals named;
- **sensitivity A:** a case `not observable` by one rater only takes the other rater's state;
- **sensitivity B:** `cannot judge` is counted as `<=1 s` (FR1's sensitivity);
- hash mismatches and unfetchable URLs, by case;
- every disagreement, listed case by case and never reconciled.

## 7. Decision (on the conservative reading; checked in this order)

| Verdict | Condition |
|---|---|
| **UNGATED** | κ < 0.6, **or** fewer than 10 PE cases in the denominator. The retention and shape lines are then not read. |
| **RETENTION IS A NECESSITY** | P80 ≥ **50 %** **and** P80's Wilson lower bound > **20 %** |
| **RETENTION IS A CONVENIENCE** | P40 < **20 %** |
| **UNCLEAR** | anything else |

**Shape line** (read only when the gate passes; reported beside the retention verdict):

| Shape | Condition |
|---|---|
| **RING BUFFER SHAPED** | RB ≥ **25 %** **and** RB's Wilson lower bound > **10 %** |
| **FLASH/CLOUD SHAPED** | P80 ≥ **50 %** **and** RB < **10 %** |
| **MIXED** | anything else |

All thresholds compare point estimates except the two named Wilson lower bounds. A clean "most causes are not
observable" or "most need ≤ 1 s" is a result.

## 8. Outputs (stage 2, after approval)

- **On the branches:** `rater_A_notes.md` and `ratings_A.csv` on `fr1r-rater-a`; `rater_B_notes.md` and
  `ratings_B.csv` on `fr1r-rater-b`. Both launch prompts.
- **After both branches exist:**
  - `analysis/FR1R_agreement.py`;
  - `results/FR1R/results_FR1R.md`: verdict and shape first, with κ and the D-3 disclosure beside it;
  - `fr1r.json`;
  - index rows;
  - a dated note under ANGLES §B.3 and SYNTHESIS §1.

## 9. Deviations

Any change after this commit is a numbered deviation (R-1, …). After any rating has been written, none of these
moves:
- the case list; the document set;
- the six states and the rate classes;
- the conservative-reading and denominator rules;
- the κ gate; the decision and shape tables.
