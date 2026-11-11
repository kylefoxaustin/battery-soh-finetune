"""locator2.py TXT : compact S1 read. Counts citing sentences; prints MASKED citing sentences that mention a
ramp/step/swing/oscillation/flicker/RVC/fluctuation limit subject; prints reference-list entries that name an
instrument-type document (limit-safe filtered); reports total reference entries."""
import sys, re
t = re.sub(r"[​‬‭]", "", open(sys.argv[1], errors="replace").read())
TIME = r"(?:ms|s|sec|secs|second|seconds|min|mins|minute|minutes|h|hr|hrs|hour|hours|cycle|cycles|Hz)"
def mask(s): return re.sub(r"\b" + TIME + r"\b", "#", re.sub(r"\d", "#", s).replace("%", "#"))
LIM = re.compile(r"\d[\d.,]*\s*(?:%|percent|(?:ms|s|sec|second|seconds|min|minutes?|h|hr|hours?|Hz|cycles?)\b|MW\s*/|p\.?u\.?\s*/)", re.I)
def safe(s): return " ".join("[…]" if LIM.search(x) else x for x in re.split(r"(?<=[.;])\s+", s))
m = list(re.finditer(r"\n\s*(?:[IVX]+\.\s*|\d+\.?\s+)?(References|REFERENCES|R EFERENCES|Bibliography|Endnotes|Sources|Works Cited|Citations)\s*\n", t))
body, refs = (t[:m[-1].start()], t[m[-1].start():]) if m else (t, "")
flat = re.sub(r"-\n(?=[a-z])", "", body); flat = re.sub(r"\s*\n\s*", " ", flat)
sents = re.split(r"(?<=[.;!?])\s+(?=[A-Z(\[“\"•])", flat)
CITE = re.compile(r"\[\d+(?:\s*[,–-]\s*\d+)*\]|\(\w[\w&.\s]+,?\s+(?:19|20)\d\d[a-z]?\)|\b(?:IEC|IEEE|NERC|ERCOT|FERC|PJM|AESO|EirGrid|NESO|ENTSO|EN\s\d|Grid Code|Protocols?|Planning Guide|Operating Guide|[Tt]ariff|Standard|Recommendation|Regulation|Guideline|Alert|NOGRR|NPRR|PGRR)\b|\b[Ss]ee\b|\b(?:19|20)\d\d\b\)|\d\s*$")
SUBJ = re.compile(r"ramp|step change|swing|oscillat|flicker|rapid voltage|fluctuat", re.I)
LIMW = re.compile(r"limit|requirement|require|specif|standard|allow|permit|must|shall|criteri|threshold|tolerance", re.I)
cit = [s for s in sents if CITE.search(s)]
show = [s for s in cit if SUBJ.search(s) and LIMW.search(s)]
print("== citing sentences: %d ; shown (limit-subject filter): %d" % (len(cit), len(show)))
for i, s in enumerate(show[:25]): print("%3d: %s" % (i + 1, mask(s[:420])))
entries = [" ".join(e.split()) for e in re.split(r"\n(?=\s*\[?\d{1,3}[\].]\s)", refs) if e.strip()]
INST = re.compile(r"IEC|IEEE|\bEN\b|Grid Code|Protocol|Guide\b|Guideline|Standard|[Tt]ariff|Rule|Regulation|Code\b|Requirement|Specification|NERC|ERCOT|PJM|AESO|ENTSO|EirGrid|NESO|VDE|FERC|PUCT|Alert|Engineering Recommendation|EREC|Manual|Order")
print("== reference entries: %d ; instrument-type shown:" % len(entries))
for e in entries:
    if INST.search(e): print("  " + safe(e)[:260])
