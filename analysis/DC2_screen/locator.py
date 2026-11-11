"""locator.py TXT : S1 reading of a locator.
(1) count every citing sentence (bracket/numeric cites, document identifiers, 'see ...');
(2) print, FULLY MASKED, the citing sentences that mention a limit-type subject (ramp, step, swing, oscillation,
    flicker, rapid voltage change, fluctuation, requirement, limit, specification, standard, grid code, tariff);
(3) print the reference list (limit-safe filtered)."""
import sys, re
t = re.sub(r"[​‬‭]", "", open(sys.argv[1], errors="replace").read())
TIME = r"(?:ms|s|sec|secs|second|seconds|min|mins|minute|minutes|h|hr|hrs|hour|hours|cycle|cycles|Hz)"
def mask(s): return re.sub(r"\b" + TIME + r"\b", "#", re.sub(r"\d", "#", s).replace("%", "#"))
LIM = re.compile(r"\d[\d.,]*\s*(?:%|percent|(?:ms|s|sec|second|seconds|min|minutes?|h|hr|hours?|Hz|cycles?)\b|MW\s*/|p\.?u\.?\s*/)", re.I)
def safe(s): return " ".join("[…]" if LIM.search(x) else x for x in re.split(r"(?<=[.;])\s+", s))
m = list(re.finditer(r"\n\s*(?:[IVX]+\.\s*|\d+\s+)?(References|REFERENCES|R EFERENCES|Bibliography|Endnotes|Literaturverzeichnis|Works Cited)\s*\n", t))
body, refs = (t[:m[-1].start()], t[m[-1].start():]) if m else (t, "")
flat = re.sub(r"-\n(?=[a-z])", "", body); flat = re.sub(r"\s*\n\s*", " ", flat)
sents = re.split(r"(?<=[.;!?])\s+(?=[A-Z(\[“\"])", flat)
CITE = re.compile(r"\[\d+(?:\s*[,–-]\s*\d+)*\]|\(\w[\w&.\s]+,?\s+(?:19|20)\d\d[a-z]?\)|\b(?:IEC|IEEE|NERC|ERCOT|FERC|EN\s\d|Grid Code|Protocol|Planning Guide|Operating Guide|tariff|Tariff|Standard|standard|Recommendation|Regulation)\b|\bsee\b|\bper\b", re.I)
SUBJ = re.compile(r"ramp|step|swing|oscillat|flicker|rapid voltage|fluctuat|requirement|limit|specif|standard|grid code|tariff|interconnection|ride", re.I)
cit = [s for s in sents if CITE.search(s)]
show = [s for s in cit if SUBJ.search(s)]
print("== citing sentences: %d ; shown (subject filter): %d" % (len(cit), len(show)))
for i, s in enumerate(show): print("%3d: %s" % (i + 1, mask(s[:450])))
print("== reference list (limit-safe):")
for ln in re.split(r"\n(?=\s*\[\d+\]|\s*\d+\.\s)", refs)[:200]:
    ln = " ".join(ln.split())
    if ln: print("  " + safe(ln)[:300])
