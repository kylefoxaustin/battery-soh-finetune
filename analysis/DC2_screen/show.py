"""show.py MODE FILE [args]  -- the ONLY way the screener prints document text.

Modes
  html2txt FILE OUT          convert HTML to plain text (no printing of content)
  links FILE [REGEX]         print anchor text + href (titles); limit-like strings masked
  head FILE N                first N non-empty lines, limit-safe filter (title page)
  headings FILE [REGEX]      heading-like lines, limit-safe filter; optional regex filter
  section FILE START END [MAXLINES]   lines from first START match to next END match, limit-safe filter
                                      (scope clause, normative-references clause)
  cite FILE REGEX [MAX]      sentences matching REGEX, FULLY MASKED (digits, %, time units -> #);
                             recognised document identifiers replaced by tokens [Rk], key printed separately
  count FILE REGEX           number of matching sentences (no text printed)

Limit-safe filter: a sentence containing a number followed by a %/time/rate/Pst unit is replaced by [...].
"""
import sys, re, html.parser

TIME_UNITS = r"(?:ms|s|sec|secs|second|seconds|min|mins|minute|minutes|h|hr|hrs|hour|hours|cycle|cycles|Hz)"
LIMITLIKE = re.compile(
    r"\d[\d.,]*\s*(?:%|percent|per\s*cent|" + TIME_UNITS + r"\b|MW\s*/|kW\s*/|MW\s+per|/\s*(?:s|min|h)\b|p\.?u\.?\b)"
    r"|\b(?:Pst|Plt|THD|TDD)\s*[=<>≤≥:]?\s*\d", re.I)

IDREGEX = re.compile(
    r"(IEC\s*(?:/\s*TR|\s+TR|\s+TS)?\s*\d{4,5}(?:-\d+){0,3}(?::\d{4})?"
    r"|IEEE\s*(?:Std\.?\s*)?\d{3,5}(?:\.\d+)?(?:-\d{4})?"
    r"|(?:BS\s+)?EN\s*\d{4,5}(?:-\d+){0,3}(?::\d{4})?"
    r"|VDE[- ]AR[- ]N\s*\d{4}(?::\d{4}-\d{2})?"
    r"|DIN\s+(?:EN\s+)?\d{4,5}(?:-\d+){0,3}"
    r"|(?:Regulation|Directive)\s*\((?:EU|EC)\)\s*(?:No\s*)?\d{2,4}/\d{2,4}"
    r"|(?:Engineering\s+Recommendation|EREC|ER)\s+[PG]\s*\d{1,3}(?:/\d)?"
    r"|(?:PGRR|NPRR|NOGRR|OBDRR|RRGRR|SCR|PUCT\s+Project\s+No\.?|Docket\s+No\.?|Project\s+No\.?)\s*\d{3,6}"
    r"|(?:EOP|TPL|FAC|PRC|MOD|BAL|VAR|TOP|IRO)-\d{3}-\d+"
    r"|\d{2}\s*TAC\s*§?\s*\d+\.\d+"
    r"|RM\d{2}-\d+|EL\d{2}-\d+|ER\d{2}-\d+|AD\d{2}-\d+"
    r"|arXiv[: ]\s*\d{4}\.\d{4,5}"
    r"|OCP\s+[A-Za-z0-9 ]{0,40}?v\d+(?:\.\d+)*)", re.I)

MASK_TIME = re.compile(r"\b" + TIME_UNITS + r"\b")

def full_mask(s):
    s = re.sub(r"\d", "#", s)
    s = s.replace("%", "#")
    s = MASK_TIME.sub("#", s)
    return s

def sentences(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"-\n(?=[a-z])", "", text)
    flat = re.sub(r"\s*\n\s*", " ", text)
    return re.split(r"(?<=[.;:!?])\s+(?=[A-Z(\[\"'“•])", flat)

def safe(line):
    """limit-safe filter at sentence granularity."""
    out = []
    for sen in re.split(r"(?<=[.;!?])\s+", line):
        out.append("[…]" if LIMITLIKE.search(sen) else sen)
    return " ".join(out)

class H(html.parser.HTMLParser):
    def __init__(s):
        super().__init__(); s.parts=[]; s.skip=0; s.links=[]; s.cur=None
    def handle_starttag(s, t, a):
        if t in ("script","style","noscript"): s.skip+=1
        if t in ("p","div","br","li","tr","h1","h2","h3","h4","h5","h6","title","td","th","section","article"): s.parts.append("\n")
        if t=="a":
            s.cur=[dict(a).get("href",""), ""]
    def handle_endtag(s, t):
        if t in ("script","style","noscript") and s.skip: s.skip-=1
        if t=="a" and s.cur is not None:
            s.links.append(tuple(s.cur)); s.cur=None
        if t in ("p","div","li","tr","h1","h2","h3","h4","h5","h6","title"): s.parts.append("\n")
    def handle_data(s, d):
        if s.skip: return
        s.parts.append(d)
        if s.cur is not None: s.cur[1]+=d

def read(f):
    return open(f, encoding="utf-8", errors="replace").read()

mode, f = sys.argv[1], sys.argv[2]
if mode == "html2txt":
    h = H(); h.feed(read(f))
    txt = re.sub(r"\n\s*\n+", "\n", "".join(h.parts))
    open(sys.argv[3], "w").write(txt)
    print("wrote", sys.argv[3], len(txt), "chars;", len(h.links), "links")
elif mode == "links":
    rx = re.compile(sys.argv[3], re.I) if len(sys.argv) > 3 else None
    h = H(); h.feed(read(f))
    seen=set()
    for href, t in h.links:
        t = " ".join(t.split())
        if rx and not (rx.search(t) or rx.search(href)): continue
        if (href,t) in seen: continue
        seen.add((href,t))
        print(safe(t)[:200], "|", href[:300])
elif mode == "head":
    n = int(sys.argv[3]); k = 0
    for line in read(f).splitlines():
        if line.strip():
            print(safe(" ".join(line.split()))[:220]); k += 1
            if k >= n: break
elif mode == "headings":
    rx = re.compile(sys.argv[3], re.I) if len(sys.argv) > 3 else None
    pat = re.compile(r"^\s*((?:\d{1,2}(?:\.\d{1,2}){0,4}\.?|[A-H]\.\d+(?:\.\d+)*|Annex [A-Z]|ANNEX [A-Z]|Article \d+|Section \d+(?:\.\d+)*|CC\.\d+(?:\.\d+)*|[A-Z]{2,4}\.\d+(?:\.\d+)*))\s*([A-Z][^\.]{2,110})$")
    for line in read(f).splitlines():
        m = pat.match(line)
        if m:
            body = re.sub(r"\.{3,}.*$", "", m.group(2)).strip()
            body = re.sub(r"\s{2,}\d+\s*$", "", body)
            if rx and not rx.search(body): continue
            print(m.group(1), full_mask(body) if LIMITLIKE.search(body) else body)
elif mode == "subsec":
    for line in read(f).splitlines():
        m = re.match(r"^\s*\(([a-z]{1,2})\)\s+([A-Z][A-Za-z ,'’/&-]{2,90}?)\.(\s|$)", line)
        if m: print("(%s) %s" % (m.group(1), m.group(2)))
elif mode == "lines":
    rx = re.compile(sys.argv[3]); mx = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    seen = []
    for i, line in enumerate(read(f).splitlines()):
        l = " ".join(line.split())
        if rx.search(l) and l not in seen:
            seen.append(l); print("%6d: %s" % (i + 1, full_mask(l)[:160] if LIMITLIKE.search(l) else l[:160]))
            if len(seen) >= mx: break
elif mode == "toc":
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 120; k=0
    for line in read(f).splitlines():
        if re.search(r"(\.\s?){4,}\s*[ivxlc\d]+\s*$", line):
            body = re.sub(r"(\.\s?){4,}\s*[ivxlc\d]+\s*$", "", line).strip()
            body = " ".join(body.split())
            print(full_mask(body) if LIMITLIKE.search(body) else body); k+=1
            if k>=mx: break
elif mode == "section":
    start, end = re.compile(sys.argv[3], re.I), re.compile(sys.argv[4], re.I)
    maxl = int(sys.argv[5]) if len(sys.argv) > 5 else 40
    on = False; k = 0
    for line in read(f).splitlines():
        if not on and start.search(line):
            on = True; print(safe(" ".join(line.split()))); continue
        if on:
            if end.search(line): break
            if line.strip():
                print(safe(" ".join(line.split()))[:900]); k += 1
                if k >= maxl: print("...[truncated]"); break
elif mode in ("cite", "count"):
    rx = re.compile(sys.argv[3], re.I)
    mx = int(sys.argv[4]) if len(sys.argv) > 4 else 200
    hits = [s for s in sentences(read(f)) if rx.search(s)]
    if mode == "count":
        print(len(hits)); sys.exit()
    key = {}
    for i, s in enumerate(hits[:mx]):
        def rep(m):
            idt = " ".join(m.group(0).split())
            if idt not in key: key[idt] = "R%d" % (len(key) + 1)
            return "[%s]" % key[idt]
        s2 = IDREGEX.sub(rep, s[:600])
        print("%3d: %s" % (i + 1, full_mask(s2)))
    print("-- %d sentences (showing %d)" % (len(hits), min(len(hits), mx)))
    print("-- reference key (document identifiers only):")
    for k, v in key.items(): print("  [%s] = %s" % (v, k))
