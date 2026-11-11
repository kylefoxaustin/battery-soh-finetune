# Build Brief — L1b: a second comparison domain for the requirement-arrival ledger (exterior lighting), with the stack-forcing class pre-registered

**Licence of this document:** public domain (CC0). **Written:** 2026-11-11. **Origin:** L1 results and the reviewer's
acceptance ([`results/L1/review/README.md`](../../results/L1/review/README.md)); SYNTHESIS §5 ("a second quiet
comparison domain … the seat domain gave eight specific events, too few to pin R"). Same event definition, classes,
two-rater two-branch procedure and gates as [`briefs/L1/README.md`](../L1/README.md) and
`results/L1/L1_preregistration.md` (with its §9 deviations L-1 … L-5). Kyle chose this leg on 2026-11-11.

> ## ▶ APPROVED (reviewer, 2026-11-11, `7c3896c`) — stage 2 runs straight through to results
>
> Approved with one deviation, **L1B-D1** (pre-registration §10): the share clause of NOT STACK-SPECIFIC fires only
> when n_L ≥ 10; the k_L ≥ 2 clause is unchanged. The session's five choices are accepted: B events rebuilt by script
> from the L1 ledgers (35, identity + `what_changed` only); three `stack_B` rows per vehicle-level event (rated for the
> B, S and L ECU); "never twice" within a domain; calibration numbers masked from the rater-visible file; table order.
> Lighting list 22 seeds + 25 additions, fixed blind; S list carried over; orders reproduce. Order: `analysis/
> L1B_agreement.py` with self-test on `main` before any branch → prompt (L1's + stack instructions, diff committed) →
> rater A → rater B → merge, run, `results/L1B/results_L1B.md` (both verdicts first, calibration, consequences),
> `l1b.json`, index rows, dated notes under ANGLES §B.1, SYNTHESIS and POSITION → `NEXT_TASK.md` Status
> `AWAITING APPROVAL <hash>`.
>
> ## ▶ START HERE (first stage: pre-registration and the fixed instrument list, then STOP) (superseded: done at `7c3896c`)
>
> 1. `git pull` on `main`.
> 2. Read this brief, `results/L1/L1_preregistration.md` (§1–§9: the procedure reused), `results/L1/L1_instruments.md`
>    (the seat list S01–S26 is reused unchanged) and `results/L1/review/README.md` (the exploratory stack split that
>    §3 below turns into a pre-registered class). **Do not open** `results/L1/ledger_A.csv`, `ledger_B.csv`,
>    `rater_A_notes.md`, `rater_B_notes.md` or `l1.json` in the session that launches the raters; the raters re-rate the
>    seat domain as a calibration and must not be primed by L1's seat events. (The reviewer has read them; the reviewer
>    is not a rater.)
> 3. **Stage 1.** Write `results/L1B/L1B_preregistration.md` (§2–§5 below with every threshold filled in; L1's
>    procedure by reference) and `results/L1B/L1B_instruments.md`: the **lighting list**, built by the L1 §3 protocol
>    by a fresh-context screener from titles and scope only, **before any change history is read**, with the addition
>    log; plus the seat list carried over from L1 unchanged. Build `results/L1B/B_events.csv` (§4) by script from
>    `results/L1/l1.json` **without reading the ledgers by eye** (the script copies the matched domain-B events'
>    identity and `what_changed` fields only). Commit with "before reading" in the message; set the Status line in
>    `NEXT_TASK.md` to `AWAITING APPROVAL <hash>`; push; stop.
>
> The reviewer approves by editing this box. Then two fresh blind raters build the lighting and seat ledgers and flag
> the stack class on all three domains; the analysis runs after both branches exist.

---

## 0. Why

L1 counted 35 dated events on the battery / charging ECU domain in 2016–2026 and 8 specific events on the seat domain;
with the four vehicle-level cyber / update instruments on both sides the ratio was 2.2 [1.2, 3.9], neither above the
pre-registered 3× nor below the 1.5× kill. Two things were left open:

1. **Is the battery box's arrival rate unusual for an ECU domain with real function obligations?** Seats are a quiet
   domain by construction (mostly crash-safety hardware). Exterior lighting is the opposite: a body-ECU domain that
   regulation has reshaped in the window (the UN lighting simplification of 2019, adaptive driving beam, automatic
   levelling, emergency stop signal, FMVSS 108's ADB rule, new GB editions). It is the strongest public falsification
   target for the "no other ECU domain" reading of ANGLES §B.1.
2. **Which events force a stack.** The reviewer's exploratory split of L1's above-software events found that the ones
   naming cryptographic, update, data-access, retention or telemetry obligations are five acts, all cyber / update / EU
   energy-data, and that the rest is software. That split was coded after reading. L1b pre-registers it as a class,
   rated blind by two raters on all three domains, so that POSITION.md's first sentence rests on a gated number.

> **The question.** Against exterior lighting, counted the same way, is the battery / charging domain's requirement
> arrival specific in **count**, and specific in **kind** — the share of events that force a cryptographic, update,
> data-access, retention or external-communication stack onto the ECU?

## 1. Rules of engagement

L1 §1 and `results/L1/L1_preregistration.md` §1–§9 apply unchanged: the event definition (a dated change to data,
function or process obligations that reaches the domain's ECUs), the classes, the window 2016–2026, the access rules
and states (L-2, L-3), the canonical `act_id` forms and two-pass matching (L-4), the gates (identification ≥ 0.80 on the
union, κ ≥ 0.60 on classification), sources (the body's own texts or summaries; trade press locates), no bypassing,
fresh-context raters in sparse clones, conventions committed before reading, D-3 disclosure, no dollar figures.

## 2. Domains

| Domain | Status in L1b | Instruments |
|---|---|---|
| **B** battery / charging / power conversion | **Carried over**: the 35 matched events of L1 are the B ledger. Not re-identified. The raters rate only the new `stack` flag on them (§3), from `B_events.csv`. | L1's B01–B37 (for reference) |
| **S** seat / interior | **Re-rated as calibration**: both raters identify events again from L1's seat instrument list S01–S26 (S01–S16 primary), blind to L1's seat ledger. | `results/L1/L1_instruments.md` S01–S26, unchanged |
| **L** exterior lighting and light-signalling | **New**: lamp controllers, adaptive-driving-beam and levelling controllers, light-signalling functions (stop, emergency stop signal, DRL, direction indicators, cornering). The domain's ECUs are the lamp / lighting control units and the body controller functions that drive them. | §6 seed list, screened by the L1 §3 protocol |

**Vehicle-level instruments** (UN R155, UN R156, GB 44495, GB 44496) count in every domain for N and R (L1 L-1, V2
primary); their events are carried over from the B ledger and are not re-identified.

## 3. The stack class (new, pre-registered)

Each event carries one more closed field, `stack`:

| Value | Meaning |
|---|---|
| `yes` | the act names, for the domain's ECU, a **cryptographic** obligation (keys, certificates, signatures, secure boot, secure communication), an **authenticated software-update** obligation, a **data-access or data-retention** obligation (data the ECU must store, keep for a period, or expose through an interface), a **telemetry or transmission** obligation (data the ECU must send off-vehicle or to a server), or an **external communication protocol** the ECU must implement (charging communication, vehicle-to-grid, diagnostic access from outside the vehicle) |
| `no` | none of the above: a new or changed monitoring or warning function, a limit, a test, a scope extension, a re-approval date, a hardware requirement |
| `cannot judge` | the text or summary read does not allow the call |

The rule is written before rating and applied by both raters to every event they record in S and L, and to each of the
35 carried-over B events (identity and `what_changed` text supplied; the raters may read the source). **A vehicle-level
act is rated for the domain it is being counted in** (R155 for a lighting ECU, say), since the obligation differs by
ECU.

## 4. Files

- `results/L1B/B_events.csv`: one row per L1 matched domain-B event — `instrument_id`, `act_id`, `adoption_date`,
  `jurisdiction`, `what_changed` (rater A's text from L1), `source_url`. **No class, confidence or note columns.**
  Written by `analysis/L1B_b_events.py` from `l1.json`; the session does not read the ledgers by eye.
- Raters: `results/L1B/ledger_<A|B>.csv` (L1 columns + `stack`, domains S and L), `stack_B_<A|B>.csv` (`act_id`,
  `stack`, `confidence`, `note` for the 35 B events), `instruments_<A|B>.csv`, `rater_<A|B>_notes.md`, on
  `l1b-rater-a` / `l1b-rater-b`.
- Rater clone contents, exactly: `results/L1/L1_preregistration.md`, `results/L1B/L1B_preregistration.md`,
  `results/L1B/L1B_instruments.md`, `results/L1B/L1B_orders.json`, `results/L1B/B_events.csv`. **Not** any L1 ledger,
  notes, results, review or `l1.json`, and not this brief (it names the expected direction).

## 5. Readouts and decision (pre-register the numbers)

**Gates** (L1 §5, computed over domains S and L together): identification ≥ 0.80; κ ≥ 0.60 on the four-class
classification over matched pairs; **and** κ ≥ 0.60 on `stack` over all events both raters rated (S and L matched
pairs plus the 35 B events). Any gate failing → UNGATED.

**Calibration (S re-rated).** N_S,specific from the new pair against L1's 8 (V2: 16). **Calibrated** if the new
count is within ± 3 of L1's specific count and the new pair's matched S events include at least 5 of L1's 8 by
`act_id`; otherwise **MISCALIBRATED**, and every ratio below is reported with the qualifier.

**Count readouts** (V2 primary, as L1 L-1): N_L (specific + vehicle-level), N_S (new), R_BL = 35 / N_L and
R_BS = 35 / N_S, each with the binomial interval L1's review used; per-year tables; classes (MC, H) for L with Wilson
CIs; V1 and V0 as sensitivities.

**Stack readouts.** For each domain, the number of **specific** events (vehicle-level excluded) with conservative
`stack = yes` (both raters `yes`; `cannot judge` from either → not counted, listed), the share of judged events, and
the vehicle-level stack count separately. Fisher's exact test (one-sided, B vs L, stack vs not) is reported.

**Decision — count:**

| Verdict | Condition (V2) |
|---|---|
| **SPECIFIC BY COUNT** | R_BL ≥ 3 and the interval's lower bound > 1.5 |
| **NOT SPECIFIC BY COUNT** | R_BL < 1.5 |
| **UNCLEAR BY COUNT** | otherwise |

**Decision — kind (the deciding readout for POSITION §1):**

| Verdict | Condition (specific events, conservative `stack`) |
|---|---|
| **STACK-SPECIFIC** | B has ≥ 3 stack events, and L and S each have ≤ 1 |
| **NOT STACK-SPECIFIC** | L has ≥ 2 stack events, or L's stack share ≥ B's |
| **UNCLEAR IN KIND** | otherwise |

**Consequences, stated beside the verdicts.** NOT SPECIFIC BY COUNT withdraws the count form of ANGLES §B.1 for good
(SYNTHESIS §3 row rewritten: "the battery box is one of the volatile ECU domains, with lighting"). NOT STACK-SPECIFIC
kills POSITION §1 sentence 1 as written: the stack is then not what distinguishes the battery box, and the C5 argument
must be made on cost alone. STACK-SPECIFIC with any count verdict is the position as written, now gated. The access
qualifier of L1 L-2 applies to domain L (≥ 1/3 of its seeds `none` for both raters → N_L a lower bound → NOT SPECIFIC
BY COUNT can be established, SPECIFIC cannot).

## 6. Seed list for domain L (titles only; the screener resolves, logs access, adds by the L1 normative-reference rule)

- **UN:** R48 (installation of lighting and light-signalling devices); R148 (light-signalling devices); R149 (road
  illumination devices); R150 (retro-reflective devices); R123 (adaptive front-lighting systems); R45 (headlamp
  cleaners); R37, R99, R128 (filament, gas-discharge and LED light sources).
- **EU:** Regulation (EU) 2019/2144 (provisions naming lighting, lamps, headlamps, adaptive driving beam or
  light-signalling, and the delegated / implementing acts under it whose titles do, found by the L1 S1 SPARQL screen);
  Regulation (EC) No 661/2009 for the 2016–2022 part of the window, the same way.
- **US:** FMVSS 108 (lamps, reflective devices and associated equipment); the NHTSA ADB rulemaking docket is part of
  108's history, not a separate instrument.
- **China:** GB 4785 (installation of lighting and light-signalling devices); GB 4599 (headlamps); GB 25991 (LED
  headlamps); GB 23255 (daytime running lamps); GB 17509 (direction indicators); GB 5920 (position, stop and
  end-outline marker lamps); any GB standard the screener finds by title for adaptive front lighting or ADB.
- **SAE:** J3069 (adaptive driving beam); J578 (color specification); J1383 (performance requirements for motor vehicle
  headlamps) — expected `none`, listed for symmetry with B's SAE seeds.
- **ISO:** none seeded (lighting has no ISO communication standard of the ISO 15118 kind); additions by reference only.

## 7. Deliverables

Stage 1: `results/L1B/L1B_preregistration.md`, `L1B_instruments.md` (+ screen record and prompt), `L1B_orders.json`
(`default_rng(51)` / `(52)` over the sorted S and L IDs), `analysis/L1B_b_events.py` and `results/L1B/B_events.csv`.
Stage 2: `analysis/L1B_agreement.py` (L1's script extended: calibration, stack readouts, Fisher; synthetic self-test;
committed before either branch), the rater prompt, the rater files on the two branches, `results/L1B/results_L1B.md`
(both verdicts first, with calibration and consequences), `l1b.json`, index rows, dated notes under ANGLES §B.1,
SYNTHESIS §1 / §3 and POSITION §1.

## 8. What not to do

- Do not re-identify domain B's events; do not show the raters L1's seat ledger or any L1 class.
- Do not add a lighting instrument because it is known to have changed; only by title and by the reference rule.
- Do not move a threshold after reading; a change after the stage-1 commit is a numbered deviation L1B-D1, ….
- Do not convert anything into dollars.

---

*Same ledger rules, a louder comparison domain, and the one class that decides whether the stack argument is the
battery box's own. Fix the list blind. Rate it twice. Let the table decide.*
