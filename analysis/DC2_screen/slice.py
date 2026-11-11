"""slice.py IN START_RX END_RX OUT : write lines from first START match to the next END match (no printing)."""
import sys, re
L = open(sys.argv[1], errors="replace").read().splitlines()
s, e = re.compile(sys.argv[2]), re.compile(sys.argv[3])
i = next(k for k, l in enumerate(L) if s.search(l))
j = next((k for k in range(i + 1, len(L)) if e.search(L[k])), len(L))
open(sys.argv[4], "w").write("\n".join(L[i:j]))
print("sliced lines", i + 1, "to", j)
