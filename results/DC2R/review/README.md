# DC2-R — reviewer acceptance (2026-11-11)

**Accepted at `5883669` as UNGATED; the data-centre anticipation leg closes on DC2-R, and DC1b is not run** (the
pre-registration §4 declaration, made before rating). Every number in `results_DC2R.md` §1–§4 was re-derived from
`requirements_A.csv`, `requirements_B.csv`, `instruments_A.csv` and `instruments_B.csv` with the reviewer's own code
(`reviewer_check.py`, the DC2 checker with the DC2R-D1 matching rule; output `reviewer_check.out`). Exact agreement
on: n_A 99, n_B 100, M 83 = 45 (pass 1) + 38 (pass 2), identification 0.716, κ(window, M₁ 45) 1.000, κ(allowance)
0.000 with observed agreement 0.867 (degenerate: B wrote `hard` on every pass-1 pair), κ(shape) 1.000, κ(binding)
0.957, κ(deciding) 1.000, the field disagreements (allowance 6, binding 2, measurement point 2, all others 0), the
unmatched rows (A 16, B 17, of which 4 deciding), the access table (39 full / full, 1 partial / full, 9 partial /
partial, 1 none / none: E01 behind a bot challenge both raters declined to bypass), the status counts (29 / 19 / 8,
identical lists), the 23 binding-deciding pairs from 6 instruments (reactive 9, electronics 1, cannot judge 11,
history 2), STATED / ANY / SEED (23 from 6; 24 from 6; 11 from 4), the two history pairs (A079 / B060, A080 / B061,
both ERCOT §6.5.7.11), each rater's own binding-deciding rows (A 25 from 7; B 28 from 7), and the exploratory
deciding-row identification 26 / 32 = 0.81. Every rater-written shape equals the computed one, and every rater-written
`deciding` flag follows the quantity list (DC2R-1), in both files.

**Process checks.** Script, self-tests (s1–s6) and rules file committed (`9d4a08d`) before the launch prompt
(`7b47601`) and before either rater branch; neither touched afterwards; the four rater files untouched after the
merges. The rules file is byte-identical to pre-registration §1–§2 (reviewer's own `diff`, and the session's `cmp`);
the launch-prompt diff against DC2's is mechanical plus the which-rules-win paragraph, naming no instrument content,
clause or expected result. Rater A's conventions commit (`ac9af82`, 09:04) precedes its first extraction commit; rater
B cloned `main` single-branch at 09:57, after A's branch was pushed, and its notes record no fetch of `dc2r-rater-a`
and no web-search tool. Both raters recorded E01 as `none` rather than bypass the challenge. The raters' own slips
(order, late conventions) are disclosed in their notes and in results §5.

**Reading of the failure.** The granularity fix did what it was for: identification on deciding rows rose from 0.61
to 0.81, κ(window) from 0.64 to 1.00, and the DC2 `deciding` disagreement on OCP envelopes vanished (DC2R-2). The
remaining gap is **coverage** — which sections of a 500-page protocol a rater searched, and which non-deciding topics
(voltage unbalance, supraharmonics) a rater chose to rate — plus four quantity-naming splits and one unspecified case
(a table holding two quantities). None of it touches the deciding set. The two further lessons in results §7 (a named
section list per instrument; the mixed-table rule) are recorded in `briefs/NEXT_EXPERIMENTS/README.md`; a DC2-R2 is
not scheduled, because the deciding picture has now been reproduced by four raters in two independent pairs and would
not change.

**What stands, documentary, with both gate failures beside it.** Four language-model raters, in two blind pairs under
two scheme versions, found the same thing in 56 instruments: every binding limit on a large load's real-power
variation is a **hard** limit — Fingrid's oscillation-amplitude bands by frequency (0.01–45 Hz) and ramp / step
limits at the POI, AESO's step limits, the D-A-CH-CZ step tables, the GB Balancing Code's 40–50 MW/min demand-change
limits (rater A only, outside the Connection Conditions), OCP's sub-100 ms supply envelopes — or states no window;
and the one statistical clause, ERCOT §6.5.7.11, is a Provisional Controllable Load Resource curtailment-performance
rule on telemetered one-minute averages, adopted but awaiting implementation, which does not see the 0.2–3 Hz swings
DC1 modelled. **No public specification was found with the window-and-allowance shape in which DC1 found seconds of
history to pay.** With DC1 (REACTIVE SUFFICES, NO HISTORY NEEDED on public traces) this closes the anticipation leg of
ANGLES §B.2 on public evidence. What is left for the shelf controller's Tier-A case is the software it must host and
the customer's own ramp contract, which is the first thing to ask the data-centre customer for.
