# DC2-R agreement self-test

Synthetic files only (every limit, URL and quote is invented). `make.py` writes `list.md` (identical to DC2's: 50 seeds,
Q07, X01) and scenarios `s1` … `s6`; its docstring states what each must read. `s1` … `s5` are DC2's scenarios with
byte-identical inputs; `s6` is new. Check with:

    python3 -I analysis/DC2R_selftest/make.py
    for s in s1 s2 s3 s4 s5 s6; do
      python3 -I analysis/DC2R_agreement.py --dir analysis/DC2R_selftest/$s --list analysis/DC2R_selftest/list.md | diff - analysis/DC2R_selftest/$s/expected.out
    done

| Scenario | Exercises | Reads |
|---|---|---|
| s1 | pass 1 and pass 2, a history pair at the POI on an addition, a DC2-2 conversion by one rater, a vendor-capability row, a written-vs-computed shape mismatch | HISTORY-SHAPED SPEC EXISTS (POI / facility only); SEED UNCLEAR |
| s2 | 12 binding deciding pairs from 5 instruments; one `unit:` window (STATED) | NO HISTORY-SHAPED SPEC |
| s3 | s2 with 17 of 50 seeds `none` for both raters | UNCLEAR (ACCESS-LIMITED) |
| s4 | M1 = 6 | UNGATED (M1 < 10) |
| s5 | binding by one rater only | UNCLEAR; ANY: HISTORY-SHAPED SPEC EXISTS |
| s6 | DC2R-D1: a one-row harmonics table with categories in different words, and a ride-through curve with different category labels and windows, both pass-1 match on clause + quantity; a deciding / non-deciding pair on the same clause does not pair; deciding rows still need clause + category in pass 1; DC2R-1's most-restrictive-entry row (computed shape electronics); DC2R-4 records | NO HISTORY-SHAPED SPEC (M 16 = 15 + 1, identification 16/18, κ(window, M1) 0.916 over 15) |

**s1–s5 under the new matching.** Every line of each `expected.out` equals DC2's `analysis/DC2_selftest/sN/expected.out`
except one added final line (the DC2R-4 and deciding-vs-quantity counts): DC2's scenarios have no non-deciding row that
DC2R-D1 pairs differently.

**s6 under DC2's script, for contrast** (`analysis/DC2_agreement.py`, same inputs): UNGATED, identification 15/19 =
0.789 (M 15 = 13 + 2; the harmonics table falls to pass 2 and the ride-through curve is unmatched on both sides). This
is the failure DC2R-D1 removes.
