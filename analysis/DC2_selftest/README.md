# DC2 agreement self-test

Synthetic files only (every limit, URL and quote is invented). `make.py` writes `list.md` (50 seeds, Q07, X01) and
scenarios `s1` … `s5`; its docstring states what each must read. Check with:

    python3 -I analysis/DC2_selftest/make.py
    for s in s1 s2 s3 s4 s5; do
      python3 -I analysis/DC2_agreement.py --dir analysis/DC2_selftest/$s --list analysis/DC2_selftest/list.md | diff - analysis/DC2_selftest/$s/expected.out
    done

| Scenario | Exercises | Reads |
|---|---|---|
| s1 | pass 1 and pass 2, a history pair at the POI on an addition, a DC2-2 conversion by one rater, a vendor-capability row, a written-vs-computed shape mismatch | HISTORY-SHAPED SPEC EXISTS (POI / facility only); SEED UNCLEAR |
| s2 | 12 binding deciding pairs from 5 instruments; one `unit:` window (STATED) | NO HISTORY-SHAPED SPEC |
| s3 | s2 with 17 of 50 seeds `none` for both raters | UNCLEAR (ACCESS-LIMITED) |
| s4 | M1 = 6 | UNGATED (M1 < 10) |
| s5 | binding by one rater only | UNCLEAR; ANY: HISTORY-SHAPED SPEC EXISTS |
