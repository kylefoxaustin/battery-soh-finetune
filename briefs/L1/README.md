# Build Brief — L1: the requirement-arrival ledger. How often do software-visible requirements land on the battery / charging / power-conversion ECU domain, compared with a low-volatility domain?

**Licence of this document:** public domain (CC0). **Written:** 2026-11-10. **Origin:** ANGLES §B.1 / §C.1 and SYNTHESIS §2
item 5 — the one Tier-A-specific leg still standing after X7, B1, DC1, FR1, FR1-R and X8, and the only one that has
never been tested. Documentary; no compute; needs web access.

> ## ▶ DONE 2026-11-10 — `a03164b`: gated (identification 0.84, κ 0.82); UNCLEAR [V1: VOLATILE DOMAIN]; kill does not fire (reviewer accepted)
>
> Results: [`results/L1/results_L1.md`](../../results/L1/results_L1.md). The reviewer re-derived every number from the
> two ledgers with its own code (`results/L1/review/`): M 43, N_B 35, N_S 16 (8 vehicle-level), R 2.19, MC 10/26 =
> 38.5 % [22.4, 57.5], H 9/26, V1 4.38 / V0 3.38 (VOLATILE), CN0 1.86, not access-limited (10 of 35 B seeds unread).
> All match. Exploratory (reviewer): R ∈ [1.2, 3.9]; the five events that force a stack are R155, R156, 2023/1542,
> 2024/1257 and 2025/1707 (19 % [9, 38] of judged). The approval text is kept below for the record.
>
> ## ▶ APPROVED (reviewer, 2026-11-10, `af2d5cb`); stage 2 was the rating (superseded: done)
>
> **Approved with deviations L-1 … L-5**, written into
> [`results/L1/L1_preregistration.md` §9](../../results/L1/L1_preregistration.md) before any change history is read:
>
> - **L-1** the four vehicle-level instruments (R155, R156, GB 44495, GB 44496) count in **both** domains for N_S and
>   R (V2 is primary; the brief's B-only listing is sensitivity V1). Works against VOLATILE; decided blind.
> - **L-2** ACCESS-LIMITED is a qualifier with bound logic: a limited domain's N is a lower bound, so with B limited
>   VOLATILE stays reachable and STABLE / the R < 1.5 kill do not fire; with S limited the reverse.
> - **L-3** `full` / `partial` / `none` defined; under `partial` access an edition is an event only when the body's own
>   catalogue entry shows its subject is data, protocol, cybersecurity, software update or monitoring (then
>   `cannot judge`, low confidence); search listings locate, never source.
> - **L-4** canonical `act_id` forms (CELEX; `R100-03`, `R100-02-S5`; `GTR22-A1`; `89 FR 100660`; `ISO 15118-20:2022`)
>   and matching by `act_id` first, then the ± 90-day rule.
> - **L-5** seed list primary confirmed; the verdict line carries FULL and V1 when they differ.
>
> **Stage 2, in this order:** (1) write and commit `analysis/L1_agreement.py` on `main` **before** any rater branch
> is fetched; (2) commit the rater launch prompt `results/L1/L1_rater_prompt.md` on `main`; (3) rater A on
> `l1-rater-a`, push; (4) rater B on `l1-rater-b`, never fetching A; (5) merge both branches, run the script, write
> `results/L1/results_L1.md` (verdict first), `l1.json`, index rows, dated notes under ANGLES §B.1 and SYNTHESIS §2;
> (6) `NEXT_TASK.md` Status → `AWAITING APPROVAL <hash>`. Details in `NEXT_TASK.md`.

---

## 0. Why L1 exists

The open-problem pass has now tested every battery and converter mechanism it could reach on public data, and the
evidence supports the null in its positive form (SYNTHESIS §0): the application-processor tier is chosen where the box
must host a Linux-class software stack anyway, with isolated, updatable domains. ANGLES §B.1 says *why some designs
need that and most do not*: the battery / charging / power-conversion box receives new software-visible requirements
after start of production at a rate no other ECU domain does. That claim was written from memory of five regimes in
about eight years. It has never been counted, and it is the leg a skeptical customer or the MCU-tier counterpart will
ask about first.

L1 counts it, against a control domain, with the same discipline as FR1-R: fixed lists before reading, two blind raters,
κ-gated classification, every disagreement listed.

> **The question.** Between 2016-01-01 and 2026-12-31, how many dated regulatory or standards events changed what the
> battery / charging / power-conversion ECU must produce, store, sign, transmit or host, what fraction of them could not
> be absorbed by a software update alone, and how does that compare with the seat / interior domain?

## 1. Rules of engagement

1. **Fix the instrument list before reading any change history.** Inclusion is decided from an instrument's title and
   scope statement, by the §3 protocol, not from what its amendments turned out to contain.
2. **Pre-register the event definition and the classification lists** (§2) before reading.
3. **Two raters, blind to each other**, each building the ledger independently from the same instrument list, on
   branches `l1-rater-a` / `l1-rater-b` (fresh-context sub-agents in sparse main-only clones, as FR1-R §4). κ on the
   classification ≥ 0.6 or the study is UNGATED. Disagreements reported, never reconciled.
4. **Sources are primary texts** (the regulation, standard or GTR as published, its amendment or revision notice, the
   official journal or working-party document) or the publishing body's own summary. Trade press may locate an
   instrument; it does not count as the source for an event.
5. Every event is **SOURCED** (URL, document identifier, date). Every classification is **DERIVED-judgemental** and says
   so. Both raters are language-model sessions; the write-up says so beside κ (FR1 D-3).
6. No dollar figures. The option-value arithmetic stays in ANGLES §B.1 and takes L1's count as an input only.

## 2. Definitions (closed; fix in the pre-registration)

**Domains.**
- **Domain B (battery / charging / power conversion):** the ECUs that manage the traction battery (BMS), on-board
  charging and charge communication (OBC, charging control unit, EVSE communication), DC-DC conversion, and the
  vehicle's high-voltage energy data interfaces (passport, durability monitor, telemetry uploads).
- **Domain S (control: seat / interior):** the ECUs that control seats, seat belts and interior fittings (seat
  adjustment, heating, occupancy classification, belt reminder, head restraints). Chosen for low expected
  software volatility and clear regulatory coverage.

**Instrument.** A regulation, directive, global technical regulation, UN regulation, national standard (GB, GB/T), ISO /
IEC / SAE standard, or a formally adopted amendment or revision of one, that applies to vehicles in at least one of the
EU, UN-1958 agreement countries, China or the United States.

**Event.** A **dated** adoption, amendment, revision or entry-into-force of an instrument that changes at least one of:
(a) the **data** the domain's ECU must produce, store, sign or transmit (schema, rate, resolution, retention, access);
(b) the **functions** it must host (protocols, cryptographic services, update mechanisms, monitors);
(c) the **process** obligations that reach into its software lifecycle (software-update management, cybersecurity
management, type-approval of software versions).
A change that touches only hardware safety (crash, fire, venting, mechanical) or only the vehicle-level test procedure
with no ECU-visible consequence is **not** an event. One instrument can yield several events (each dated amendment
counts once).

**Classification of each event (closed list; rate the most demanding consequence stated or clearly implied):**
- `software-only` — absorbable by a software update on an ECU already fielded, with no new interface, no new
  cryptographic hardware requirement and no re-certification of the control safety case;
- `memory-or-crypto` — needs materially more storage, a secure element / HSM capability, or a new communication stack;
- `hardware-or-recert` — needs a new interface, sensor or compute class, or re-opens type approval / the functional
  safety case of the control software;
- `cannot judge` — the text does not allow a reading.

Plus: **date** (adoption and, where distinct, first application), **jurisdiction**, **what changed** (one line),
**source**.

## 3. Search protocol (fix before searching; record every hit count)

- **Domain B instruments to screen:** EU battery regulation 2023/1542 and its delegated / implementing acts (passport,
  SoH, carbon footprint); Euro 7 (2024/1257) battery-durability provisions; UN GTR 22 and amendments; UN R100 series
  (02, 03) and R155, R156; UN R10 (EMC in charging mode) revisions; China GB/T 32960 parts 1–3 and their revisions,
  GB 38031, GB/T 18487.1, GB/T 27930, GB 44495, GB 44496; ISO 15118-2 / -20 / -8, ISO 17409, IEC 61851-1 / -23 /
  -24, SAE J1772, J3400, J2847 / J2931 bidirectional series; US FMVSS 305 / 305a; EU AFIR (2023/1804) insofar as it
  imposes vehicle-side obligations. **The screen may add instruments by the stated rule only:** an instrument is added
  when it is cited as a normative reference by one already listed and meets the §2 instrument definition.
- **Domain S instruments to screen:** UN R14, R16, R17, R25, R44 / R129 (child restraint interfaces), FMVSS 202a, 207,
  208 (occupant classification), 209, 210, 225; EU GSR2 (2019/2144) provisions that name seat-belt reminders or
  seating; China GB 14167, GB 15083, GB 11550. Same addition rule.
- For each instrument: locate the authoritative change history (EUR-Lex "all consolidated versions", UNECE regulation
  page with supplements, SAC / standards.gov.cn record, ISO OBP revision list, SAE revision list, NHTSA rulemaking
  docket). Record the URL used.
- **Window:** events dated 2016-01-01 to 2026-12-31; adopted-but-future-application events are included with both
  dates.

## 4. Readouts and decision (pre-register the numbers)

- **Primary:** events per domain per year (table 2016–2026), and the **fraction of domain-B events classified
  `hardware-or-recert`** (conservative reading: the lower of the two raters' classes in the order software-only <
  memory-or-crypto < hardware-or-recert), with Wilson CI.
- **Secondary:** the fraction `memory-or-crypto` or above; events by jurisdiction; events by instrument; the same
  readouts for domain S; the ratio of domain-B to domain-S event counts (descriptive, no test); every disagreement.
- **Gate:** κ on the four-class classification over all events both raters recorded ≥ 0.6; and both raters' ledgers
  must agree on ≥ 80 % of events (same instrument, same date ± 90 days) — a ledger that the two raters build from the
  same list but populate differently is UNGATED on *identification*, reported separately from κ on *classification*.
- **Decision** (on the conservative reading of domain B):
  - **VOLATILE DOMAIN** if domain B shows ≥ 1 event per year on average over 2016–2026 **and** ≥ 25 % of its events are
    `memory-or-crypto` or above (CI lower bound > 10 %), **and** domain B's event count is ≥ 3× domain S's;
  - **STABLE DOMAIN** if domain B shows < 0.5 events per year, **or** < 10 % of its events are above `software-only`;
  - **UNCLEAR** otherwise; **UNGATED** if a gate fails.
- **Kill for ANGLES §B.1:** STABLE DOMAIN, or a domain-B/domain-S ratio < 1.5.

## 5. Deliverables

Stage 1: `results/L1/L1_preregistration.md`, `results/L1/L1_instruments.md` (with hit counts and the addition log).
Stage 2: `ledger_A.csv` + `rater_A_notes.md` on `l1-rater-a`; the same for B; then `analysis/L1_agreement.py`,
`results/L1/results_L1.md` (verdict first; the per-year table; κ with the D-3 disclosure), `l1.json`, index rows, and
dated notes under ANGLES §B.1 and SYNTHESIS §2.

## 6. What not to do

- Do not add an instrument because its amendments look interesting; only by the §3 rule, and log the addition.
- Do not count the same amendment twice under two instruments.
- Do not read trade-press summaries as sources for an event.
- Do not convert the count into dollars here.

---

*Fix the instrument list blind. Define the event before reading. Build the ledger twice. Compare with the seat
domain. Report the disagreements.*
