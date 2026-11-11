# Build Brief — DC2: the ramp-spec audit. What compliance window and excursion allowance do real large-load power specifications use, and is any of them shaped so that seconds of history would pay?

**Licence of this document:** public domain (CC0). **Written:** 2026-11-10. **Origin:** DC1 results §7
([`results/DC1/results_DC1.md`](../../results/DC1/results_DC1.md)) and SYNTHESIS §5 — the one DC1 sensitivity where
history pays (a 5× looser violation budget: SD 1.27×, W* 30 s) "is a reason to ask what violation budget a real ramp
spec allows". Documentary; no compute; needs web access. The last data-centre leg of ANGLES §B.2. Same discipline as
L1: fixed instrument list before reading any limit, closed extraction fields, two blind raters, κ-gated.

> ## ▶ START HERE (first stage: pre-registration and the fixed instrument list only, then STOP)
>
> 1. `git pull` on `main`.
> 2. Read this brief, ANGLES §B.2 and §C.2, `results/DC1/results_DC1.md` §1 and the sensitivities table, and
>    `results/L1/L1_preregistration.md` (the procedure to reuse, §3–§5 and §9 L-2 … L-4).
> 3. **Stage 1.** Write `results/DC2/DC2_preregistration.md` (definitions §2, the search protocol §3, extraction
>    fields and classes §4, readouts and decision §5 with every threshold filled in) and `results/DC2/DC2_instruments.md`
>    (the fixed list, built by the §3 protocol by a fresh-context screener **before any limit, window or allowance is
>    read**, with hit counts, access status and the addition log). Commit with "before reading" in the message; set
>    the Status line in `NEXT_TASK.md` to `AWAITING APPROVAL <hash>`; push; stop.
>
> The reviewer approves by editing this box. Then two blind raters extract on `dc2-rater-a` / `dc2-rater-b`; the
> analysis script is committed before either branch exists.

---

## 0. Why DC2 exists

DC1 showed, on public 5 Hz training traces, that a reactive controller with no history holds an AI load inside an
ASSUMED ramp spec (0.10 P_max/s, 0.1 % of samples allowed to violate) with as little storage as a 30 s forecaster — and
that the result flips when the spec allows 0.5 % of samples to violate (forecasting saves 1.27× on Stable Diffusion,
needs 30 s of history). The whole data-centre anticipation leg therefore turns on one documentary fact: **what window
and allowance do the specifications a rack or facility must actually meet use?** If they average over a minute or more,
or allow no excursions, DC1's primary regime is the real one and the leg is closed. If some binding spec limits
real-power variation over 1–60 s while tolerating ~0.5 % or more excursions, DC1's sensitivity is the real-world case
and a re-run under that spec (DC1b, code) is warranted.

> **The question.** Among public specifications and rules that constrain how a large load's real power may vary in
> time — grid-interconnection rules and utility large-load clauses, power-quality standards, and the rack / facility
> specifications of the operators and vendors themselves — what quantity is limited, over what measurement or
> compliance window, with what excursion allowance, at which measurement point; and does any binding requirement have
> the window-and-allowance shape in which DC1 found history to pay?

## 1. Rules of engagement

1. **Fix the instrument list before reading any limit.** Inclusion is decided from titles and scope statements by the
   §3 protocol, with additions by the citation rule only, logged.
2. **Pre-register the extraction fields, the classes and the decision table** (§4–§5) before reading.
3. **Two raters, blind to each other**, fresh-context sub-agents in sparse main-only clones (L1 §4), on
   `dc2-rater-a` / `dc2-rater-b`; κ ≥ 0.6 on the window class and ≥ 80 % identification agreement, or UNGATED;
   disagreements reported, never reconciled.
4. **Sources are the publishing body's own texts, abstracts, catalogue or guidance pages.** Papers (arXiv 2508.14318,
   arXiv 2605.24461), EPRI reports and trade press may *locate* a requirement; they never source one. A paper's
   statement that "utilities require X" is not a requirement; the utility's or ISO's document is.
5. **No bypassing** (L1 §3b): paywalled IEC / IEEE texts are read through the body's own abstract and preview pages
   only, logged `partial` or `none`; the ACCESS-LIMITED qualifier of L1 L-2 applies.
6. **Every requirement SOURCED** (URL, document, clause, quote ≤ 25 words); every class **DERIVED-judgemental**; both
   raters are language-model sessions and the write-up says so beside κ (FR1 D-3). **No dollar figures.**

## 2. Definitions (closed; fix in the pre-registration)

**Instrument.** A public document that binds, or offers as a planning level, a limit on the behaviour of an electrical
load or of the equipment serving it: a grid code or connection code, an ISO / RTO protocol or planning guide, a
regulator's rule, a utility tariff or interconnection requirement, a power-quality standard or technical report, or an
operator / vendor rack, shelf or facility specification. A document that only *describes* load behaviour (a paper, a
reliability assessment, a white paper without requirements) is not an instrument; it is a locator.

**Requirement.** One clause of a listed instrument that states a limit on a quantity of the **load's real power or its
rate of change in time**, or on a voltage-quality quantity that such variation drives, with the window over which it is
assessed. One clause, one row; a table of limits by category is one row per category.

**Deciding set.** Requirements whose quantity is **real-power time variation**: ramp rate (MW/s, %/s, %/min), step
change, swing or oscillation amplitude, power-smoothing or power-capping response time, or a limit on load change per
interval. **Also reported, not deciding:** flicker (Pst / Plt), rapid voltage change, harmonics, power factor, ride-through,
hold-up — the quantities the converter's own control loop meets without anticipation.

**Binding class** (closed): `mandatory` (a code, protocol, rule or tariff condition); `planning level` (a limit the
network operator applies in assessment, as IEC 61000-3-7 planning levels); `recommendation`; `vendor capability` (a
configurable feature, e.g. a GPU or rack power-smoothing ramp setting — not a requirement on anyone).

**Window class** (closed, the measurement or assessment interval): `≤ 100 ms`; `100 ms – 1 s`; `1 – 60 s`;
`1 – 15 min`; `> 15 min`; `not stated`.

**Allowance class** (closed): `hard` (no excursion permitted); `tight` (≤ 0.1 % of intervals or of time may exceed,
e.g. a 99.9th percentile); `loose` (more than 0.1 % up to 5 %: 95th–99.5th percentiles); `very loose` (> 5 %);
`event count` (a number of events per hour / day); `not stated`.

**History-shaped** (the DC1 sensitivity's shape, fixed here): window class `1 – 60 s` **and** allowance class `loose`
or `very loose`. **Reactive-shaped:** window class `1 – 15 min` or `> 15 min`, or allowance `hard` / `tight` at any
window ≥ 1 s (DC1's primary regime). **Electronics-shaped:** window class `≤ 100 ms` or `100 ms – 1 s` (no history can
help; it is the converter's bandwidth and the storage element's power).

## 3. Search protocol (fix before searching; record every hit count)

**S0. Seed instruments to screen** (named by body and subject; the screener records the exact current title, landing
page and scope, and logs access):

| Group | Seeds |
|---|---|
| **US grid / ISO / regulator** | ERCOT: Planning Guide and Nodal Protocol / Operating Guide sections on large-load interconnection and on Controllable Load Resource ramp-rate registration, and any 2025–2026 large-load protocol revision; NERC: the Large Loads task-force reports and guideline(s), the 2025 large-load alert, and any large-load standards project; PJM: large-load additions documents (2025–2026); the Texas PUCT rule(s) implementing SB 6 (2025) for large loads; FERC order(s) on large-load co-location (2025) |
| **US utility large-load clauses** | AEP Ohio data-centre tariff (2025); Dominion Energy Virginia large-load rate schedule (2025); Georgia Power large-load rules (2025); any other investor-owned-utility large-load tariff the screener finds by title that names ramp, step or fluctuation |
| **EU / UK / DE** | Regulation (EU) 2016/1388 (Demand Connection Code) and ENTSO-E's implementation guidance on it; the GB Grid Code Connection Conditions (demand step-change and fluctuation clauses); VDE-AR-N 4120 and 4130 (TAR Hochspannung / Höchstspannung) for Bezugsanlagen; the D-A-CH-CZ Technical Rules for the Assessment of Network Disturbances |
| **Power quality** | IEC TR 61000-3-7; IEC 61000-4-30; IEC 61000-4-15; IEEE 519; IEEE 1453; EN 50160 |
| **Operator / vendor rack and facility** | OCP: Open Rack V3 base and power-shelf / BBU specifications, the 800 VDC ("Mt Diablo") specifications, and any OCP power-stabilisation specification or requirements document (2025–2026); NVIDIA: the GB200 / GB300 NVL72 power-smoothing and power-capping documentation and the 800 VDC architecture white paper; any Microsoft, Google or Meta published facility power-behaviour requirement found by title |

**S1. Locators (read for citations only, never as sources):** arXiv 2508.14318 (Choukse et al.), arXiv 2605.24461, EPRI
DCFlex publications, NERC and ISO presentations. Every instrument they cite as *the* source of a ramp, step, swing or
flicker limit is a candidate addition.

**S2. Title and scope** for each instrument: landing page, exact title, scope (≤ 3 sentences quoted), access status
(`full` / `partial` / `none`, L1 L-3). **The screener does not read any limit value, window or allowance.**

**S3. Additions, one level:** a document cited by a listed instrument or by an S1 locator as the normative basis of a
limit on load real-power variation, flicker or rapid voltage change, that is an instrument under §2, is added once and
logged with the citing document and clause. References of added instruments are not screened.

**S4. Rater routes:** the body's own site (ercot.com, nerc.com, pjm.com, puc.texas.gov, ferc.gov, eur-lex.europa.eu,
entsoe.eu, neso.energy, vde.com, iec.ch, ieee.org / standards.ieee.org, cencenelec.eu, opencompute.org,
docs.nvidia.com / developer.nvidia.com, the utility's tariff pages and the state commission's docket). Resellers and
secondary summaries are not sources.

## 4. Extraction (one row per requirement; `requirements_<A|B>.csv`)

`req_id`, `instrument_id`, `clause` (section / table / paragraph identifier as printed), `measurement_point` (`POI` /
`facility` / `rack or row` / `shelf or PSU` / `device` / `not stated`), `quantity` (closed list: `ramp rate`, `step
change`, `swing amplitude`, `smoothing or capping response`, `load change per interval`, `flicker`, `rapid voltage
change`, `harmonics`, `power factor`, `ride-through`, `hold-up`, `other`), `limit` (value and unit as printed),
`basis` (what the percentage refers to, if any), `window_class`, `window_as_printed`, `allowance_class`,
`allowance_as_printed`, `binding_class`, `deciding` (`yes` if quantity is in the deciding set), `shape` (`history` /
`reactive` / `electronics` / `cannot judge`, by the §2 rules), `source_url`, `quote` (≤ 25 words), `confidence`,
`note`. Plus `instruments_<A|B>.csv` with `history_access` and `sources_tried` per instrument (L1 L-3).

## 5. Readouts and decision (pre-register the numbers)

- **Matching:** same `instrument_id` and the same normalised `clause`; then, for the rest, same `instrument_id`,
  same `quantity` and same `window_class`. Identification = M / (n_A + n_B − M).
- **Gates:** identification ≥ 0.80; unweighted κ on `window_class` over matched pairs ≥ 0.60. Also reported: κ on
  `allowance_class` and on `shape`.
- **Conservative shape** of a matched pair: `history` only if both raters say `history`; `cannot judge` if either does.
- **Primary readouts:** the number of deciding requirements per window class and per allowance class; the number of
  binding (`mandatory` or `planning level`) deciding requirements whose conservative shape is `history`; the fastest
  binding window per body; the table of every requirement.
- **Decision (deciding set, binding classes only, conservative shape):**

| Verdict | Condition |
|---|---|
| **UNGATED** | identification < 0.80 or κ(window) < 0.60 |
| **HISTORY-SHAPED SPEC EXISTS** | ≥ 1 binding deciding requirement with conservative shape `history` |
| **NO HISTORY-SHAPED SPEC** | ≥ 8 binding deciding requirements from ≥ 4 instruments, and none with shape `history` from **either** rater |
| **UNCLEAR** | anything else (including fewer than 8 binding deciding requirements found) |

  ACCESS-LIMITED qualifier as L1 L-2 (≥ 1/3 of seed instruments `none` for both raters): NO HISTORY-SHAPED SPEC cannot
  be established (an unread spec could carry one); HISTORY-SHAPED SPEC EXISTS can.
- **Consequence for ANGLES §B.2 (stated beside the verdict):** NO HISTORY-SHAPED SPEC closes the anticipation leg —
  DC1's primary regime is the real one. HISTORY-SHAPED SPEC EXISTS re-opens it as DC1's sensitivity and names the
  spec (window, allowance, point) for a pre-registered DC1b re-run. UNCLEAR: the leg stays where DC1 left it.
- **Also reported:** the vendor-capability rows (what ramp settings GPU and rack smoothing features expose), the
  non-deciding power-quality rows with their window and allowance (so the reader sees the shapes the converter must
  meet), and every disagreement.

## 6. Deliverables

Stage 1: `results/DC2/DC2_preregistration.md`, `results/DC2/DC2_instruments.md` (+ `DC2_screen.json`,
`DC2_screen_prompt.md`, `DC2_orders.json`).
Stage 2: `analysis/DC2_agreement.py` (committed before either rater branch, with a synthetic self-test); the rater
prompt; `requirements_<A|B>.csv`, `instruments_<A|B>.csv`, `rater_<A|B>_notes.md` on the two branches; then
`results/DC2/results_DC2.md` (verdict first, the requirement table, κ with the D-3 disclosure), `dc2.json`, index rows,
dated notes under ANGLES §B.2 and SYNTHESIS §1 / §5.

## 7. What not to do

- Do not take a paper's paraphrase of a utility or ISO requirement as the requirement.
- Do not promote a vendor's configurable ramp setting to a requirement.
- Do not add an instrument because it is known to contain a fast limit; only by the §3 rule, logged.
- Do not convert anything into dollars, rack counts or capex here.

---

*Fix the list blind. Extract the window and the allowance as printed. Classify by the pre-registered shape. Build it
twice. Report the disagreements.*
