"""cites.py TXT [--all] [--max N] [--kw REGEX]
Print citing sentences, FULLY MASKED (digits, %, time-unit tokens -> #), with recognised document identifiers
replaced by tokens [Rk] (key printed at the end; identifiers only).
Default scope (S3 rule for documents without a normative-references clause): sentences inside clauses whose nearest
preceding heading names one of: ramp, step, fluctuation, oscillation, flicker, rapid voltage change, power quality,
disturbance, large load (+ German equivalents). --all: every sentence in the document (locators, normative clauses).
A sentence is 'citing' if it names a document identifier or uses a citation phrase with a document noun.
"""
import sys, re
sys.path.insert(0, __file__.rsplit("/", 1)[0])
args = sys.argv[1:]
f = args[0]
ALL = "--all" in args
EXT = "--ext" in args
EXTNOUN = re.compile(r"\b(IEC|IEEE|EN\s?\d|NERC|ENTSO|Engineering Recommendation|EREC|ANSI|UL\s?\d|CIGRE|CIGRÉ|IEC/TR|standard|Standard|Norm|DIN|VDE|FNN|D-A-CH|IEEE|EPRI|ISO\b|PUCT|FERC|Grid Code|Regulation \(EU\))")
MAX = int(args[args.index("--max") + 1]) if "--max" in args else 400
KW = re.compile(args[args.index("--kw") + 1] if "--kw" in args else
                r"ramp|step|fluctuat|oscillat|flicker|rapid voltage|voltage change|power quality|disturb|large load|"
                r"large computational|Rampe|Laständerung|Spannungsänderung|Netzrückwirkung|Spannungsqualität|Flicker|Schwankung", re.I)
TIME_UNITS = r"(?:ms|s|sec|secs|second|seconds|min|mins|minute|minutes|h|hr|hrs|hour|hours|cycle|cycles|Hz)"
MASK_TIME = re.compile(r"\b" + TIME_UNITS + r"\b")
IDREGEX = re.compile(
    r"(IEC\s*(?:/\s*TR|\s+TR|\s+TS)?\s*\d{4,5}(?:-\d+){0,3}(?::\d{4})?"
    r"|IEEE\s*(?:Std\.?\s*)?\d{3,5}(?:\.\d+)?(?:-\d{4})?"
    r"|(?:BS\s+|DIN\s+|ÖVE\s+|SN\s+)?EN\s*\d{4,5}(?:-\d+){0,3}(?::\d{4})?"
    r"|VDE[- ]AR[- ]N\s*\d{4}(?:/A\d)?(?::\d{4}-\d{2})?"
    r"|(?:Regulation|Directive|Verordnung)\s*\((?:EU|EC|EG)\)\s*(?:No\.?\s*|Nr\.?\s*)?\d{2,4}/\d{2,4}"
    r"|(?:Engineering\s+Recommendation|EREC|ER)\s+[PGM]\s*\d{1,3}(?:/\d)?"
    r"|(?:NPRR|PGRR|NOGRR|OBDRR|RRGRR|SCR)\s*\d{2,6}"
    r"|(?:Project|Docket|Case)\s+No\.?\s*[A-Z]*-?\d[\d-]{2,}"
    r"|(?:EOP|TPL|FAC|PRC|MOD|BAL|VAR|TOP|IRO|CLO)-\d{3}-\d+"
    r"|\d{2}\s*TAC\s*§?\s*\d+\.\d+|§\s*\d{2}\.\d{2,3}"
    r"|(?:RM|EL|ER|AD)\d{2}-\d+(?:-\d{3})?"
    r"|arXiv[: ]\s*\d{4}\.\d{4,5}"
    r"|UL\s*\d{3,5}[A-Z]?|ANSI\s*C\d{2}(?:\.\d+)?|NFPA\s*\d{2,4}"
    r"|(?:Section|Article|Art\.|Clause|Annex|Appendix|Table|Figure|Chapter)\s+[A-Z]?\d+(?:\.\d+)*(?:\(\d+\))?)", re.I)
DOCNOUN = re.compile(r"\b(standard|code|guide|protocol|regulation|recommendation|rule|specification|tariff|order|"
                     r"report|guideline|norm|Anwendungsregel|Richtlinie|Regel|Technische|IEC|IEEE|EN\b|NERC|ERCOT|ENTSO|"
                     r"P28|G5|TR\b)", re.I)
CITEPH = re.compile(r"(in accordance with|as defined in|as specified in|specified in|comply with|compliance with|"
                    r"the limits of|limits (?:in|of|given in|set out in)|pursuant to|according to|as per|per the|"
                    r"set out in|referred to in|described in|defined in|given in|see |\[\d+(?:[,–-]\s*\d+)*\]|"
                    r"gemäß|nach |entsprechend|siehe)", re.I)
HEAD = re.compile(r"^\s*((?:[A-Z]{1,4}\.)?\d{1,2}(?:\.\d{1,3}){0,5}\.?|[A-Z]\.\d+(?:\.\d+)*|Annex [A-Z]|Article \d+|"
                  r"Section \d+(?:\.\d+)*|\([a-z]\)|[IVX]{1,5}\.|[A-H]\.)\s*[A-Z][^\n]{2,110}$")

def full_mask(s):
    s = re.sub(r"\d", "#", s); s = s.replace("%", "#"); return MASK_TIME.sub("#", s)

text = open(f, errors="replace").read()
text = re.sub(r"[​‬‭]", "", text)
lines = text.splitlines()
if "--hfile" in args:
    _hs = [h.strip() for h in open(args[args.index("--hfile") + 1]) if h.strip()]
    HEAD = re.compile(r"^\s*(?:" + "|".join(re.escape(h) for h in _hs) + r")\s*$")
# build (heading, paragraph-text) blocks
blocks, cur_h, buf = [], "", []
for ln in lines:
    if HEAD.match(ln) and len(ln.strip()) < 130:
        if buf: blocks.append((cur_h, " ".join(buf)))
        cur_h, buf = ln.strip(), [ln.strip()]
    else:
        if ln.strip(): buf.append(ln.strip())
if buf: blocks.append((cur_h, " ".join(buf)))
key, out, n_cite = {}, [], 0
for h, body in blocks:
    if not ALL and not KW.search(h):
        continue
    body = re.sub(r"-\s(?=[a-z])", "", body)
    for s in re.split(r"(?<=[.;!?])\s+(?=[A-Z(\[\"“])", body):
        ids = IDREGEX.findall(s)
        ext_ids = [i for i in ids if not re.match(r"(Section|Article|Art\.|Clause|Annex|Appendix|Table|Figure|Chapter)\b", i, re.I)]
        if not (ext_ids or (CITEPH.search(s) and DOCNOUN.search(s))):
            continue
        n_cite += 1
        if EXT and not (ext_ids or EXTNOUN.search(s)):
            continue
        def rep(m):
            idt = " ".join(m.group(0).split())
            if idt not in key: key[idt] = "R%d" % (len(key) + 1)
            return "[%s]" % key[idt]
        hh = full_mask(IDREGEX.sub(rep, h))[:90]
        out.append("{%s} %s" % (hh, full_mask(IDREGEX.sub(rep, s[:500]))))
for i, o in enumerate(out[:MAX]):
    print("%3d: %s" % (i + 1, o))
print("-- citing sentences: %d (shown %d); scope: %s" % (n_cite, min(n_cite, MAX), "all" if ALL else "keyword-headed clauses"))
print("-- reference key (document identifiers only):")
for k, v in key.items():
    print("  [%s] = %s" % (v, k))
