# FR1 independent re-derivation

**Written:** 2026-11-06 by the running session (rater A's session), per NEXT_TASK step 1.
**Code:** [`rederive_FR1.py`](rederive_FR1.py), written from pre-registration §4.3, §5 and §6 only. It does not import,
read or modify `analysis/FR1_agreement.py`. Run: `python3 -I results/FR1/review/rederive_FR1.py results/FR1`.
**Inputs:** [`ratings_A.csv`](../ratings_A.csv), [`ratings_B.csv`](../ratings_B.csv) at public `40e8a12`.

Every rating is DERIVED-judgemental (source: NHTSA, public domain). The counts and κ below are DERIVED from those
ratings. The verdict stays UNGATED (κ < 0.6), so no fraction below is gated.

## Result: every checked number matches

| Item | Published (`results_FR1.md`) | Re-derived | Match |
|---|---|---|---|
| Both-rater exclusions: no cause stated | 4 | 4 (PE 1, BR 3) | yes |
| Both-rater exclusions: software-only | 17 | 17 (all PE) | yes |
| Both-rater exclusions: out of scope | 23 | 23 (all PE) | yes |
| Excluded, any flag (overlapping) | 41 (PE 38, BR 3) | 41 (PE 38, BR 3) | yes |
| PE after exclusions | 37 | 37 | yes |
| PE *cannot judge* by either rater | 1 | 1 | yes |
| **PE denominator** | **36** | **36** | yes |
| **κ, item 3 collapsed, all rated cases** | **0.19** (n = 145) | **0.192** (n = 145) | yes |
| **κ, PE** | **0.55** (n = 71) | **0.554** (n = 71) | yes |
| κ, PE post-exclusion | 0.52 (n = 36) | 0.518 (n = 36) | yes |
| κ, BR | 0.01 (n = 74) | 0.006 (n = 74) | yes |
| **PE conservative > 80 s** | **28 % [16, 44]** | **10/36 = 28 % [16, 44]** | yes |
| PE conservative > 40 s | 28 % [16, 44] | 10/36 = 28 % [16, 44] | yes |
| PE conservative > 1 s | 42 % [27, 58] | 15/36 = 42 % [27, 58] | yes |
| PE conservative distribution | ≤ 1 s 21 · (1, 40] 5 · (40, 80] 0 · (80, 700] 2 · > 700 8 | 21 · 5 · 0 · 2 · 8 | yes |
| PE rater A alone > 80 s | 50 % [34, 66] (n = 36) | 18/36 = 50 % [34, 66] | yes |
| PE rater B alone > 80 s | 30 % [17, 46] (n = 37) | 11/37 = 30 % [17, 46] | yes |
| **BR rater A alone > 80 s** | **96 % [88, 99]** (n = 72) | **69/72 = 96 % [88, 99]** | yes |
| **BR rater B alone > 80 s** | **7 % [3, 15]** (n = 72) | **5/72 = 7 % [3, 15]** | yes |
| BR conservative > 80 s | 7 % [3, 15] (n = 72) | 5/72 = 7 % [3, 15] | yes |

## Definitions as implemented

- **Exclusion (§4.3):** a case is excluded if both raters set the same flag to yes. The PE-only flags are n/a or NA on
  BR rows, which never count as yes.
- **Denominator (§5):** not excluded, and neither rater rated *cannot judge*. A single rater's fraction uses that
  rater's own non-*cannot judge* cases after exclusions. That is why rater B's PE n is 37: rater A alone marked the
  remaining PE case *cannot judge*.
- **Conservative reading:** the lower of the two raters' six-way window categories. "> 80 s" means (80, 700] or > 700 s.
- **κ:** Cohen's κ on item 3 collapsed to ≤ 1 / (1, 80] / > 80 s, over cases that both raters rated with a category.
- **Wilson:** 95 % score interval, z = 1.96.

No item differs, so there is no BLOCKED status.
