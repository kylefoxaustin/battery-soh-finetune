# L1b screener scripts

The stage-1 screener's scripts for domain L, as run, with local paths written `<scratch>` or `<home>`. `build.py`
regenerates the screener's `L1B_instruments_L.md` and `L1B_screen.json` from its intermediate files. Those files are not
committed, because they are fetched web content. The launching session then assembled `results/L1B/L1B_instruments.md`
from the screener's file, with the seat list S01–S26 carried over from L1 and the GB edition years removed from the
identifiers (pre-registration §3b).
