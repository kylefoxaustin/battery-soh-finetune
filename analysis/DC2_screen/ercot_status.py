"""print Title, Status, Effective dates from an ERCOT issue page text (labels only)."""
import sys
L=[l.strip() for l in open(sys.argv[1],errors='replace') if l.strip()]
out=[]
for lab in ("Title","Status","Effective Dates"):
    for i,l in enumerate(L):
        if l==lab and i+1<len(L):
            out.append(f"{lab}: {L[i+1][:150]}"); break
print(" || ".join(out))
