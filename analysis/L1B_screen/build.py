# Builds out/L1B_screen.json and out/L1B_instruments_L.md from the screen's intermediate files.
# usage: python3 -I build.py <screen_dir>
import sys, json, re, os, csv
D = sys.argv[1]; W = D + "/web"; O = D + "/out"
J = lambda p: json.load(open(p))
UA = "L1B-screener research fetch (public regulatory texts)"
EURLEX = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:"

def strip_date(t):
    return re.sub(r"[\s\u00a0]+of[\s\u00a0]+\d{1,2}[\s\u00a0]+[A-Z][a-z]+[\s\u00a0]+\d{4}", "", t).replace("\n", " ").strip()

# ---------------- seeds ----------------
un_seed = J(W + "/unr_seeds4.json"); un_seed.update(J(W + "/unr_seeds3.json"))
L = {}
def scope_of(f):
    return " ".join(J(f)["scope_sentences"][:3])
unr_order = ["48", "148", "149", "150", "123", "45", "37", "99", "128"]
for i, n in enumerate(unr_order, 1):
    lid = "L%02d" % i
    v = un_seed[n]
    L[lid] = dict(instrument_id=lid, domain="L", identifier="UN Regulation No %s" % n,
                  title=v["title"], body="UNECE WP.29 (1958 Agreement)", jurisdiction="UN-1958 Agreement parties (incl. EU)",
                  landing=EURLEX + v["celex"], landing_note="EUR-Lex OJ publication of the UN Regulation (unece.org returned HTTP 403)",
                  scope=scope_of(O + "/_%s_refs.json" % lid), origin="seed", celex=v["celex"],
                  oj_fulltext_hits=v.get("hits_full"), refs_file=O + "/_%s_refs.json" % lid)
t2144 = "Regulation (EU) 2019/2144 of the European Parliament and of the Council on type-approval requirements for motor vehicles and their trailers, and systems, components and separate technical units intended for such vehicles, as regards their general safety and the protection of vehicle occupants and vulnerable road users, amending Regulation (EU) 2018/858 of the European Parliament and of the Council and repealing Regulations (EC) No 78/2009, (EC) No 79/2009 and (EC) No 661/2009 of the European Parliament and of the Council and Commission Regulations (EC) No 631/2009, (EU) No 406/2010, (EU) No 672/2010, (EU) No 1003/2010, (EU) No 1005/2010, (EU) No 1008/2010, (EU) No 1009/2010, (EU) No 19/2011, (EU) No 109/2011, (EU) No 458/2011, (EU) No 65/2012, (EU) No 130/2012, (EU) No 347/2012, (EU) No 351/2012, (EU) No 1230/2012 and (EU) 2015/166"
t661 = "Regulation (EC) No 661/2009 of the European Parliament and of the Council concerning type-approval requirements for the general safety of motor vehicles, their trailers and systems, components and separate technical units intended therefor"
_tt = {x["celex"]["value"]: strip_date(x["title"]["value"]) for f in ("s1t_2144.json","s1t_661.json") for x in J(W + "/" + f)["results"]["bindings"]}
t2144 = _tt["32019R2144"]; t661 = _tt["32009R0661"]
L["L10"] = dict(instrument_id="L10", domain="L", identifier="Regulation (EU) 2019/2144 (provisions naming lighting, lamps, headlamps, ADB or light-signalling)", title=t2144,
                body="European Parliament and Council", jurisdiction="EU", landing=EURLEX + "32019R2144", landing_note="EUR-Lex, OJ text as adopted",
                scope=scope_of(O + "/_L10_refs.json"), origin="seed", refs_file=O + "/_L10_refs.json")
L["L11"] = dict(instrument_id="L11", domain="L", identifier="Regulation (EC) No 661/2009 (same provisions; 2016-2022 part of the window)", title=t661,
                body="European Parliament and Council", jurisdiction="EU", landing=EURLEX + "32009R0661", landing_note="EUR-Lex, OJ text as adopted",
                scope=scope_of(O + "/_L11_refs.json"), origin="seed", refs_file=O + "/_L11_refs.json")
L["L12"] = dict(instrument_id="L12", domain="L", identifier="FMVSS 108 (49 CFR 571.108)", title="Standard No. 108; Lamps, reflective devices, and associated equipment.",
                body="NHTSA (US DOT)", jurisdiction="US", landing="https://www.ecfr.gov/current/title-49/subtitle-B/chapter-V/part-571/subpart-B/section-571.108",
                landing_note="eCFR (text retrieved via eCFR versioner API, current date)",
                scope="This standard specifies requirements for original and replacement lamps, reflective devices, and associated equipment. (S1; S3 applies it to passenger cars, multipurpose passenger vehicles, trucks, buses, trailers (except pole trailers and trailer converter dollies), and motorcycles, to retroreflective sheeting and reflex reflectors, and to replacement equipment.)",
                origin="seed")
gb = [("L13", "4785"), ("L14", "4599"), ("L15", "25991"), ("L16", "23255"), ("L17", "17509"), ("L18", "5920"), ("L19", "30036")]
gbinfo = {}
for lid, n in gb:
    t = open(W + "/osd_%s.txt" % n).read()
    g = lambda lab: (re.search(lab + r"：\s*([^\n]+)", t).group(1).strip())
    q = J(W + ("/gb_%s.json" % n if n != "30036" else "/gbt_自适应前照明.json"))
    cur = q["current"][0]
    gbinfo[n] = q
    L[lid] = dict(instrument_id=lid, domain="L", identifier=g("标准号"), title="%s (%s)" % (g("英文标准名称"), g("中文标准名称")),
                  body="SAMR / SAC (competent dept.: MIIT)", jurisdiction="China",
                  landing="https://std.samr.gov.cn/gb/search/gbDetailed?id=" + cur["id"],
                  landing_note="std.samr.gov.cn / openstd.samr.gov.cn landing page (title only; scope not on landing page; full text behind online viewer with interactive verification)",
                  scope="not accessible", origin="seed" if n != "30036" else "seed (GB title search: 自适应前照明 / AFS)",
                  std_state_on_landing=cur["state"])
sae = [("L20", "SAE J3069", "Adaptive Driving Beam", "https://www.sae.org/standards/content/j3069/"),
       ("L21", "SAE J578", "Color Specification", "https://www.sae.org/standards/content/j578/"),
       ("L22", "SAE J1383", "Performance Requirements for Motor Vehicle Headlamps", "https://www.sae.org/standards/content/j1383_201805/")]
for lid, ident, title, url in sae:
    L[lid] = dict(instrument_id=lid, domain="L", identifier=ident, title=title + " (title not read from landing page; see deviation L1B-S4)", body="SAE International",
                  jurisdiction="US (voluntary; referenced by regulation)", landing=url,
                  landing_note="sae.org page is client-side rendered and loads an AWS WAF captcha SDK; no title/scope in static HTML; not bypassed",
                  scope="not accessible", origin="seed")

# ---------------- reference tests ----------------
LIGHT = re.compile(r"(?i)lamp|headlamp|light|lighting|retro-?reflect|direction indicator|illumination|signalling|fog")
known_titles = {  # titles of cited UN Regulations not in the seed or addition texts: from 2019/2144 Annex I subject column where available
}
s2144 = J(O + "/_L10_refs.json")["table_subjects"]
adds_meta = J(W + "/unr_adds_final.json")
not_accessible_un = {"70": "Rear marking plates for heavy and long vehicles (title per screener; not read from source)",
                     "88": "Retroreflective tyres for two-wheeled vehicles (title per screener; not read from source)"}
other_un_titles = {"24": "Visible pollutants / power of compression-ignition engines (title per screener; not in 2019/2144 Annex I table)",
                   "33": "Behaviour of the structure of the impacted vehicle in a head-on collision (title per screener; not in 2019/2144 Annex I table)",
                   "53": "Installation of lighting and light-signalling devices on category L3 vehicles",
                   "74": "Installation of lighting and light-signalling devices on category L1 vehicles",
                   "86": "Installation of lighting and light-signalling devices on agricultural or forestry tractors",
                   "50": "Front position lamps, rear position lamps, stop lamps, direction indicators and rear-registration-plate illuminating devices for vehicles of category L",
                   "113": "Headlamps emitting a symmetrical passing beam or a driving beam or both"}
def un_title(n):
    if n in adds_meta and adds_meta[n].get("title"): return adds_meta[n]["title"]
    if n in un_seed and un_seed[n].get("title"): return un_seed[n]["title"]
    if ("UN R" + n) in s2144: return s2144["UN R" + n]
    return other_un_titles.get(n) or not_accessible_un.get(n, "")

nonun = {  # identifier: (title judged on, t1, t2, t3, note)
 "IEC 60809": ("Lamps and light sources for road vehicles - Dimensional, electrical and luminous requirements", "yes", "yes", "yes", "title and abstract from webstore.iec.ch/en/publication/65713"),
 "IEC 60061": ("Lamp caps and holders together with gauges for the control of interchangeability and safety", "yes", "no", "-", "title per screener; scope (lamp caps and holders in general use) names no road vehicles"),
 "IEC 60410": ("Sampling plans and procedures for inspection by attributes", "yes", "no", "-", "title per screener"),
 "ISO 105": ("Textiles - Tests for colour fastness", "yes", "no", "-", "title per screener; iso.org returned HTTP 403 (bot challenge)"),
 "ISO 2859-1": ("Sampling procedures for inspection by attributes - Part 1", "yes", "no", "-", "title per screener; iso.org 403"),
 "ISO 3768": ("Metallic coatings - Neutral salt spray test (NSS test)", "yes", "no", "-", "title per screener; iso.org 403"),
 "ISO 4892-2": ("Plastics - Methods of exposure to laboratory light sources - Part 2: Xenon-arc lamps", "yes", "no", "-", "title per screener; iso.org 403"),
 "ISO 11341": ("Paints and varnishes - Artificial weathering and exposure to artificial radiation - Exposure to filtered xenon-arc radiation", "yes", "no", "-", "title per screener; iso.org 403"),
 "ISO 11664-2": ("Colorimetry - Part 2: CIE standard illuminants", "yes", "no", "-", "title per screener; iso.org 403"),
 "ISO 23603": ("Standard method of assessing the spectral quality of daylight simulators for visual appraisal and measurement of colour", "yes", "no", "-", "title per screener; iso.org 403"),
 "ISO 23273": ("Fuel cell road vehicles - Safety specifications - Protection against hydrogen hazards", "yes", "yes", "no", "title per screener"),
 "ISO 28580": ("Passenger car, truck and bus tyres - Methods of measuring rolling resistance", "yes", "yes", "no", "title per screener"),
 "EN 13422": ("CEN standard (vehicle warning devices)", "no", "-", "-", "EN (CEN) is not an instrument type under L1 §2"),
 "EN 50436": ("CENELEC standard (alcohol interlocks)", "no", "-", "-", "EN (CENELEC) is not an instrument type under L1 §2"),
 "SAE J2578": ("Recommended Practice for General Fuel Cell Vehicle Safety", "yes", "yes", "no", "title per screener; sae.org not readable"),
 "CIE 15": ("CIE colorimetry publication", "no", "-", "-", "CIE is not an instrument type under L1 §2"),
 "CIE 45": ("CIE publication", "no", "-", "-", "CIE"),
 "CIE 85": ("CIE publication", "no", "-", "-", "CIE"),
 "CIE S (standard, number not parsed)": ("CIE standard", "no", "-", "-", "CIE"),
 "Resolution R.E.3": ("Consolidated Resolution on the Construction of Vehicles (R.E.3)", "no", "-", "-", "UN WP.29 resolution, not a regulation/GTR/standard"),
 "Resolution R.E.5": ("Consolidated Resolution on the common specification of light source categories (R.E.5)", "no", "-", "-", "UN WP.29 resolution, not a regulation/GTR/standard"),
 "Directive 95/46/EC": ("Data protection directive", "yes", "no", "-", ""),
 "Directive 2007/46/EC": ("Framework for the approval of motor vehicles and their trailers", "yes", "yes", "no", ""),
 "Directive 92/23/EEC": ("Tyres for motor vehicles and their trailers and their fitting", "yes", "yes", "no", ""),
 "Regulation (EU) 2016/679": ("General Data Protection Regulation", "yes", "no", "-", ""),
 "Regulation (EU) No 182/2011": ("Comitology (control of implementing powers)", "yes", "no", "-", ""),
 "Regulation (EU) 2018/858": ("Approval and market surveillance of motor vehicles and their trailers", "yes", "yes", "no", ""),
 "Regulation (EC) No 715/2007": ("Type approval of motor vehicles with respect to emissions from light passenger and commercial vehicles", "yes", "yes", "no", ""),
 "Regulation (EC) No 661/2009": ("listed as L11", "yes", "yes", "yes", "already listed"),
 "Regulation (EU) 2019/2144": ("listed as L10", "yes", "yes", "yes", "already listed (self-citation in Annex III; counted)"),
 # FMVSS 108 references
 "ASTM Motor Fuels section (Annual Book of ASTM Standards, Vol. 05.04)": ("ASTM", "no", "-", "-", "ASTM is not an instrument type under L1 §2"),
 "ASTM B117": ("Standard Method of Salt Spray (Fog) Testing", "no", "-", "-", "ASTM"),
 "ASTM C150": ("Standard Specification for Portland Cement", "no", "-", "-", "ASTM"),
 "ASTM D362": ("Standard Specification for Industrial Grade Toluene", "no", "-", "-", "ASTM"),
 "ASTM D1003": ("Standard Test Method for Haze and Luminous Transmittance of Transparent Plastics", "no", "-", "-", "ASTM"),
 "ASTM D4956": ("Standard Specification for Retroreflective Sheeting for Traffic Control", "no", "-", "-", "ASTM"),
 "ASTM E308": ("Standard Practice for Spectrophotometry and Description of Color in CIE 1931 System", "no", "-", "-", "ASTM"),
 "GSA Federal Specification L-S-300": ("Sheeting and Tape, Reflective; Nonexposed Lens, Adhesive Backing", "no", "-", "-", "federal procurement specification"),
 "IES LM 45": ("IES Approved Method for Electrical and Photometric Measurements of General Service Incandescent Filament Lamps", "no", "-", "-", "IES"),
 "CIE 1931": ("CIE 1931 Chromaticity Diagram", "no", "-", "-", "CIE"),
 "SAE J567": ("Bulb Sockets", "yes", "not established", "-", "title from 49 CFR 571.5; scope not accessible (sae.org); title names no vehicle"),
 "SAE J573": ("Lamp Bulbs and Sealed Units", "yes", "not established", "-", "title from 49 CFR 571.5; scope not accessible; title names no vehicle"),
 "SAE J602": ("Headlamp Aiming Device for Mechanically Aimable Sealed Beam Headlamp Units", "yes", "not established", "-", "title from 49 CFR 571.5; scope not accessible; title names no vehicle (see L1B-S5)"),
 "SAE J941": ("Motor Vehicle Driver's Eye Range", "yes", "yes", "no", "title from 49 CFR 571.5"),
 "SAE J2009": ("Discharge Forward Lighting Systems", "yes", "not established", "-", "title from 49 CFR 571.5; scope not accessible; title names no vehicle (see L1B-S5)"),
 "49 CFR Part 564": ("Replaceable light source and sealed beam headlamp information", "yes", "yes", "yes", "scope §564.1 read on eCFR"),
}
EU_MV = re.compile(r"Regulation \((EU|EC)\) No (19/2011|65/2012|78/2009|79/2009|109/2011|130/2012|347/2012|351/2012|406/2010|458/2011|631/2009|672/2010|1003/2010|1005/2010|1008/2010|1009/2010|1230/2012)|Regulation \(EU\) 2015/(758|166)")

def norm(k):
    k = k.replace("Consolidated Resolution on the Construction of Vehicles (R.E.3", "Resolution R.E.3")
    if k.startswith("CIE"):
        m = re.search(r"(\d+)", k.replace("015", "15"))
        if k in ("CIE S", "CIE Standard"): return "CIE S (standard, number not parsed)"
        return "CIE %d" % int(m.group(1)) if m else k
    return k

def test_un(n):
    t = un_title(n)
    if n in not_accessible_un:
        return t, "yes", "not established", "-", "no EUR-Lex OJ publication found (SPARQL title search, 0 hits); unece.org HTTP 403; title/scope not accessible"
    t3 = "yes" if LIGHT.search(t or "") else "no"
    return t, "yes", "yes", t3, "title from EUR-Lex OJ publication" if n in adds_meta or n in un_seed else ("title = 2019/2144 Annex I subject column" if ("UN R" + n) in s2144 else "title per screener")

def tests_for(k):
    if k.startswith("UN R"): return test_un(k[4:])
    if k in nonun: return nonun[k]
    if EU_MV.search(k): return ("EU motor-vehicle implementing/component regulation (repealed by 2019/2144)", "yes", "yes", "no", "title concerns a non-lighting system")
    return ("", "?", "?", "?", "unclassified")

# listed set (identifiers -> L ids)
listed = {"UN R%s" % n: "L%02d" % i for i, n in enumerate(unr_order, 1)}
listed.update({"Regulation (EU) 2019/2144": "L10", "Regulation (EC) No 661/2009": "L11"})
next_id = 23
additions = []; hitcounts = {}; refrecords = {}
def process(lid, refs):  # refs: dict identifier -> clauses
    global next_id
    hc = dict(references_read=0, pass_test1=0, pass_test2=0, pass_test3=0, added=0, already_listed=0)
    recs = []
    for k in sorted(refs, key=lambda k: (k.split()[0], int(re.findall(r"\d+", k)[0]) if re.findall(r"\d+", k) else 0, k)):
        t, t1, t2, t3, note = tests_for(k)
        hc["references_read"] += 1
        p1 = t1 == "yes"; p2 = p1 and t2 == "yes"; p3 = p2 and t3 == "yes"
        hc["pass_test1"] += p1; hc["pass_test2"] += p2; hc["pass_test3"] += p3
        outcome = "not added"
        if p3:
            if k in listed:
                hc["already_listed"] += 1; outcome = "already listed (%s)" % listed[k]
            else:
                nid = "L%02d" % next_id; next_id += 1; listed[k] = nid; hc["added"] += 1
                outcome = "added as %s" % nid
                additions.append(dict(id=nid, ident=k, via=lid, clause=sorted(refs[k], key=lambda c: (not c[0].isdigit(), c))[0], title=t, tests=(t1, t2, t3)))
        recs.append(dict(identifier=k, clauses=sorted(refs[k])[:20], title_judged_on=t, test1=t1, test2=t2, test3=t3, note=note, outcome=outcome))
    hitcounts[lid] = hc; refrecords[lid] = recs

for lid in ["L%02d" % i for i in range(1, 12)]:
    raw = J(L[lid]["refs_file"])["refs"]
    refs = {}
    selfid = {"L10": "Regulation (EU) 2019/2144", "L11": "Regulation (EC) No 661/2009"}.get(lid)
    for k, v in raw.items():
        nk = norm(k)
        if lid == "L11" and nk == selfid: continue  # self-reference in own annex
        if nk == "Regulation (EC) No 661/2009" and lid == "L11": continue
        refs.setdefault(nk, set()).update(v)
    if lid == "L10": refs.pop("Regulation (EU) 2019/2144", None)  # self-citation
    process(lid, refs)
f108 = {"ASTM Motor Fuels section (Annual Book of ASTM Standards, Vol. 05.04)": {"571.5(d)"}, "ASTM B117": {"S14.5.4.1", "S14.6.3.1"},
        "ASTM C150": {"S14.5.3.2", "S14.6.5.1.2"}, "ASTM D362": {"S14.6.2.1.1"}, "ASTM D1003": {"S14.4.2.2.4.1"}, "ASTM D4956": {"S8.2.1.2"},
        "ASTM E308": {"S14.4.2.2.4.4"}, "GSA Federal Specification L-S-300": {"S8.1"}, "IES LM 45": {"571.5"}, "CIE 1931": {"S4", "S14.2.5.7.3"},
        "SAE J567": {"S14.2.1.6.2"}, "SAE J573": {"S14.2.1.6"}, "SAE J602": {"S6.4.5", "S10.18.7"}, "SAE J941": {"S9.3.5"}, "SAE J2009": {"S11.3", "S14.7.3.1.2"},
        "UN R48": {"571.5 (UNECE Regulation 48 incorporated into 571.108)"}, "49 CFR Part 564": {"S4", "S10.13", "S11"}}
process("L12", f108)
for lid in ["L%02d" % i for i in range(13, 23)]:
    hitcounts[lid] = "references not accessible"

# addition rows
add_scope = {}
for a in additions:
    k = a["ident"]
    if k.startswith("UN R"):
        n = k[4:]
        meta = adds_meta[n]
        txt = W + "/R%s.txt" % n
        sc = os.popen("python3 -I %s/scripts/scope_only.py '%s'" % (D, txt)).read().strip() if os.path.exists(txt) else ""
        if n == "86": sc = "This Regulation applies to vehicles of category T (1), with regard to the installation of lighting and light-signalling devices."
        if n == "98": sc = "This Regulation applies to: (a) Headlamps, and (b) Distributed lighting systems, utilizing gas-discharge light sources, for vehicles of categories, M and N and L3."
        if n == "113": sc = sc.replace("(2) ", "", 1)
        if n == "3": sc = sc.split(" 2. DEFINITIONS")[0]
        L[a["id"]] = dict(instrument_id=a["id"], domain="L", identifier="UN Regulation No %s" % n, title=meta["title"], body="UNECE WP.29 (1958 Agreement)",
                          jurisdiction="UN-1958 Agreement parties (incl. EU)", landing=EURLEX + meta["celex"] + ("" if n != "86" else " (HTML returned 202; PDF route used)"),
                          landing_note="EUR-Lex OJ publication", scope=sc, origin="added via %s clause %s" % (a["via"], a["clause"]), celex=meta["celex"])
    elif k == "IEC 60809":
        L[a["id"]] = dict(instrument_id=a["id"], domain="L", identifier="IEC 60809", title="Lamps and light sources for road vehicles - Dimensional, electrical and luminous requirements",
                          body="IEC (TC 34)", jurisdiction="international", landing="https://webstore.iec.ch/en/publication/65713", landing_note="IEC webstore",
                          scope="IEC 60809 is applicable to electric light sources for use in automotive applications, for example in road illumination devices and/or light signalling devices for road vehicles. (webstore abstract; the edition year in the abstract is omitted here)",
                          origin="added via %s clause %s" % (a["via"], a["clause"]))
    elif k == "49 CFR Part 564":
        L[a["id"]] = dict(instrument_id=a["id"], domain="L", identifier="49 CFR Part 564", title="Part 564—Replaceable light source and sealed beam headlamp information",
                          body="NHTSA (US DOT)", jurisdiction="US", landing="https://www.ecfr.gov/current/title-49/subtitle-B/chapter-V/part-564", landing_note="eCFR",
                          scope="This part requires the submission of dimensional, electrical specification, and marking/designation information as specified in Appendices A and B of this part, for original equipment replaceable light sources used in motor vehicle headlighting systems. This part also serves as a repository for design information as specified in appendix C of this part, for original equipment and replacement standardized sealed beam units used in motor vehicle headlighting systems.",
                          origin="added via %s clause %s" % (a["via"], a["clause"]))
for lid in L:
    if lid in hitcounts and isinstance(hitcounts[lid], dict): L[lid]["references_status"] = "read %d" % hitcounts[lid]["references_read"]
    elif lid in hitcounts: L[lid]["references_status"] = "not accessible"
    else: L[lid]["references_status"] = "not screened (addition; one level only)"

# ---------------- S1 ----------------
def s1(f, base):
    d = J(f)["results"]["bindings"]; recs = []
    KEEP = re.compile(r"(?i)lighting|lamp|headlamp|adaptive driving beam|light-signal|light signal")
    for x in sorted(d, key=lambda x: x["celex"]["value"]):
        c = x["celex"]["value"]; t = strip_date(x.get("title", {}).get("value", ""))
        nums = set()
        for m in re.finditer(r"Regulations?\s+Nos?\.?\s*([\d ,andH]+?)\s+(?:of the|adopted)", t): nums |= set(re.findall(r"\d+", m.group(1)))
        for m in re.finditer(r"UN Regulations?\s+Nos?\.?\s*([\d ,and]+)", t): nums |= set(re.findall(r"\d+", m.group(1)))
        title_test = bool(KEEP.search(t)) or bool(nums & set(unr_order))
        is_act = c.startswith("3")
        kept = title_test and is_act
        reason = ("kept" if kept else ("title test passes (names UN Regulation(s) %s) but not an act adopted under the base act (CELEX sector %s: preparatory/EP document); not kept" % (sorted(nums & set(unr_order)), c[0]) if title_test else ("dropped: title does not name the §6 terms" + ("" if is_act else "; also not an act adopted under the base act (CELEX sector %s)" % c[0]))))
        recs.append(dict(celex=c, title=t, title_test=title_test, act_adopted_under_base=is_act, decision=reason))
    return recs
S1 = {"32019R2144": s1(W + "/s1_2144.json", "2019/2144"), "32009R0661": s1(W + "/s1_661.json", "661/2009")}
s1_query = open(D + "/scripts/sparql_s1.py").read().split('q = """')[1].split('"""')[0]
s1_title_query = open(D + "/scripts/sparql_title.py").read().split('q = """')[1].split('"""')[0]

# ---------------- fetch log ----------------
fetches = [dict(zip(["utc", "http", "url", "file"], r.rstrip("\n").split("\t"))) for r in open(W + "/fetchlog.tsv")]
for f in fetches: f["file"] = os.path.basename(f["file"])

deviations = [
 ("L1B-S1", "UN Regulations were read from their EUR-Lex OJ publications (unece.org returned HTTP 403), as in L1. Each was located by a SPARQL title query on the EU Publications Office endpoint; amendment, supplement and corrigendum titles were filtered out by script before printing, and the most recent remaining full-text OJ publication (sector 4) was chosen by document date without displaying the other publications. Hit counts of matching full-text publications are recorded. Two first-pass picks were non-UN EU acts with the same number (Regulation No 1 on languages; Regulation No 31 Staff Regulations) and consolidated-text CELEX numbers (sector 0) for R38/R77/R87/R91; the query was re-run restricted to sector-4 UN publications and those picks replaced. No consolidated text was opened."),
 ("L1B-S2", "Regulation (EC) No 661/2009: references were taken from the OJ text as adopted (CELEX 32009R0661). Its Annex IV (list of UNECE Regulations) is empty in that text, so 661/2009 contributes no UN-Regulation references; a consolidated version was not used, because choosing one would require the version list. The UN Regulations relevant to lighting are reached through 2019/2144 Annex I and the UN seeds."),
 ("L1B-S3", "S1: the legal-basis SPARQL query (cdm:resource_legal_based_on_resource_legal) also returns European Parliament resolutions, a Commission report and Commission proposals (CELEX sectors 5). These are not acts adopted under the base act and are not kept even where the title test passes: 52010PC0310 (proposal for a Council Decision on compulsory application of UN Regulations including Nos 37, 48, 99 and 123) passes the title test but is not kept. A cross-check title query (titles containing the base-act number, sector 3) found no further act adopted under either base act. Adoption dates were stripped from the S1 titles by script."),
 ("L1B-S4", "SAE seeds L20-L22: the sae.org and SAE Mobilus pages are rendered client-side and load an AWS WAF captcha SDK; the static HTML holds no title or scope. Not bypassed. Exact titles: J578 is taken from 49 CFR 571.5 (an official incorporation list); J3069 and J1383 are the titles shown in web-search result titles for the SAE pages. Scope and references: not accessible."),
 ("L1B-S5", "Tests for SAE documents cited by FMVSS 108 (J567, J573, J602, J2009): the cited document's scope was not accessible, and its title (from 49 CFR 571.5) does not name road vehicles, so test 2 is recorded 'not established' and nothing is added. Read on title alone with the SAE ground-vehicle context, J602 (headlamp aiming device) and J2009 (discharge forward lighting systems) would pass all three tests. They are listed here for the reviewer as a sensitivity set and are NOT on the list. The same rule leaves UN R70 and UN R88 (cited by R48; no EUR-Lex OJ publication found; unece.org 403) not added."),
 ("L1B-S6", "Titles of some cited documents that fail test 1 or test 2 (ISO, IEC 60061/60410, ASTM, R24, R33) are recorded from the screener's knowledge, not from a landing page (iso.org returned 403 / bot challenge). None of these could change an addition except if the title were wrong in a way that names road vehicles and lighting; none is a lighting-on-vehicles title."),
 ("L1B-S7", "Disclosure (rule 1): two web searches were used to find landing URLs (IEC 60809 and IEC 60061 on webstore.iec.ch; SAE J3069/J1383/J578 on sae.org). The search tool returned, unrequested, a synthesized summary that mentioned edition and amendment information for IEC 60809, IEC 60061, SAE J1383 and SAE J3069. Nothing from those summaries is used in or recorded in these outputs, and no further web search was made. Separately, the std.samr.gov.cn search JSON rows and the GB detail page include edition-state fields; only the current (or, where none is current, the single most recent) edition's identifier was printed, except that one withdrawn-edition row of GB 4785 was seen in a raw response preview at the start of the GB search. The reviewer should weigh whether this exposure matters for the blind list; the list itself was fixed by the protocol, not by that information."),
 ("L1B-S8", "GB seeds GB 25991, GB 23255 and GB 17509 have no edition marked current on std.samr.gov.cn. The most recent edition's identifier is listed (only that row was printed). The current-state flag is recorded in the JSON for access purposes and carries no description of what changed."),
 ("L1B-S9", "GB title search: std.samr.gov.cn queried for 自适应前照明, 自适应远光, 自适应驾驶光束, 自适应前照灯, 自适应照明, 自适应光束, 前照明系统, 自适应, ADB, AFS (and 前照灯, 远光 as context checks). Only GB/T 30036 (汽车用自适应前照明系统) has a title naming AFS or ADB; it is L19. No GB title naming ADB was found. The openstd.samr.gov.cn search page was not separately queried, because it serves the same SAMR catalogue (its landing pages were used)."),
 ("L1B-S10", "Reference extraction for UN Regulations and EU acts is by script (identifier + clause), starting at the Scope heading (UN) or Article 1 (EU), and excluding sections headed 'Transitional provisions' and any bibliography. Approval-mark examples in annexes (e.g. R48 Annex 2 citing R33) are counted as citations because they are annex text. For 2019/2144 Annex I, a bare number in the 'UN Regulation Number' column was read as a citation of that UN Regulation with its subject; the series-of-amendments and OJ-reference columns were not read or printed."),
]

out = dict(screen="L1B domain L", user_agent=UA, timeout_s=60,
           protocol="L1B_preregistration.md §6 (L1 §3 applied to domain L)",
           S0_seed_order=[(k, L[k]["identifier"]) for k in sorted(L) if int(k[1:]) <= 22],
           S1=dict(query_legal_basis=s1_query, query_title_crosscheck=s1_title_query,
                   hits={"32019R2144": len(S1["32019R2144"]), "32009R0661": len(S1["32009R0661"])},
                   kept={k: [r for r in v if r["decision"] == "kept"] for k, v in S1.items()}, records=S1),
           S0_GB_title_search={k: v for k, v in [(f, J(W + "/" + f)) for f in sorted(os.listdir(W)) if f.startswith("gbt_") and f.endswith(".json")]},
           GB_seed_lookup={n: gbinfo[n] for n in gbinfo},
           UN_lookup={"seeds": un_seed, "additions": adds_meta, "R70_R88": "SPARQL title queries for 'Regulation No 70/88' and for 'rear marking plates for heavy', 'etro-reflective tyres', 'etroreflective tyres' (sector 4): 0 hits"},
           instruments=[L[k] for k in sorted(L)], S3_references=refrecords, S3_hit_counts=hitcounts,
           additions=additions, references_not_accessible=[k for k in sorted(L) if L[k]["references_status"] == "not accessible"],
           access_blocks=["unece.org: HTTP 403", "iso.org: HTTP 403 (Cloudflare 'Just a moment' challenge)", "sae.org / saemobilus.sae.org: client-side rendered, AWS WAF captcha SDK; no static content",
                          "openstd.samr.gov.cn online viewer: returns the landing page; full text needs an interactive verification step", "eur-lex.europa.eu: intermittent HTTP 202 with empty body (throttling); retried after pauses; R86 HTML never served, PDF route used",
                          "webstore.iec.ch free preview PDF: preview URL returned HTML, not a PDF (not pursued)"],
           fetches=fetches, deviations=[dict(id=a, text=b) for a, b in deviations])
for k in out["instruments"]: k.pop("refs_file", None)
json.dump(out, open(O + "/L1B_screen.json", "w"), indent=1, ensure_ascii=False, default=list)

# ---------------- markdown ----------------
def esc(s): return str(s).replace("|", "\\|").replace("\n", " ")
md = []
md.append("# L1b instrument list, domain L (exterior lighting and light-signalling)\n")
md.append("Built by the L1b screener (fresh context, not a rater) under `L1B_preregistration.md` §6 (L1 §3, S0–S3), from titles, scope statements and normative references only, before any change history was read. Raw record: `L1B_screen.json`.\n")
ns = sum(1 for k in L if int(k[1:]) <= 22); na = len(L) - ns
md.append("**Count:** %d instruments (seed %d, added by S3 %d).\n" % (len(L), ns, na))
md.append("## 1. Instruments\n")
md.append("| instrument_id | domain | identifier | exact title | issuing body | jurisdiction | landing URL | scope (≤ 3 sentences, quoted) | origin | references status |")
md.append("|---|---|---|---|---|---|---|---|---|---|")
for k in sorted(L):
    r = L[k]
    sc = r["scope"] if r["scope"] == "not accessible" else "“%s”" % r["scope"]
    md.append("| %s |" % " | ".join(esc(x) for x in [k, "L", r["identifier"], r["title"], r["body"], r["jurisdiction"], r["landing"], sc, r["origin"], r["references_status"]]))
md.append("\n## 2. S1 acts kept under each EU base act (candidate events; title and identifier only)\n")
for base, lid in [("32019R2144", "L10"), ("32009R0661", "L11")]:
    kept = [r for r in S1[base] if r["decision"] == "kept"]
    md.append("**%s (%s):** %d acts found, %d kept." % (lid, {"L10": "Regulation (EU) 2019/2144", "L11": "Regulation (EC) No 661/2009"}[lid], len(S1[base]), len(kept)))
    md.append("\n" + ("\n".join("- %s — %s" % (r["celex"], r["title"]) for r in kept) if kept else "- none kept") + "\n")
md.append("## 3. S3 hit counts per instrument\n")
md.append("| instrument_id | references read | pass test 1 | pass test 2 | pass test 3 | added | already listed |")
md.append("|---|---|---|---|---|---|---|")
for k in sorted(L):
    h = hitcounts.get(k)
    if isinstance(h, dict): md.append("| %s | %d | %d | %d | %d | %d | %d |" % (k, h["references_read"], h["pass_test1"], h["pass_test2"], h["pass_test3"], h["added"], h["already_listed"]))
    elif h: md.append("| %s | references not accessible | – | – | – | 0 | – |" % k)
tot = {x: sum(h[x] for h in hitcounts.values() if isinstance(h, dict)) for x in ["references_read", "pass_test1", "pass_test2", "pass_test3", "added", "already_listed"]}
md.append("| **total** | %d | %d | %d | %d | %d | %d |" % tuple(tot.values()))
md.append("\nAdditions (L23 onward) are not screened for references (one level only). References are counted as distinct identifiers per citing instrument; CIE variants are merged by publication number.\n")
md.append("## 4. Addition log\n")
md.append("| added id | identifier | cited by | clause | test 1 | test 2 | test 3 | title and scope judged on |")
md.append("|---|---|---|---|---|---|---|---|")
for a in additions:
    r = L[a["id"]]
    md.append("| %s |" % " | ".join(esc(x) for x in [a["id"], r["identifier"], a["via"], a["clause"], *a["tests"], "%s. Scope: “%s”" % (r["title"], r["scope"])]))
md.append("\nReferences that passed tests 1 and 2 but failed test 3, and other non-additions, are recorded per reference in `L1B_screen.json` → `S3_references`.\n")
md.append("## 5. S1 query log\n")
md.append("- Endpoint: `https://publications.europa.eu/webapi/rdf/sparql` (EU Publications Office CELLAR), JSON results.")
md.append("- Query 1 (legal basis): works whose `cdm:resource_legal_based_on_resource_legal` is the base act (matched by CELEX). Hits: 2019/2144 → %d; 661/2009 → %d." % (len(S1["32019R2144"]), len(S1["32009R0661"])))
md.append("- Query 2 (cross-check): English titles containing `2019/2144` / `661/2009`, CELEX sector 3. Extra items not in query 1: the base acts themselves, their corrigenda, one corrigendum of 2021/646 and Regulation (EU) 2024/1689 (AI Act, amends 2019/2144; not adopted under it; title fails the test). Nothing added.")
md.append("- Title rule (§6): kept if the title names lighting, lamps, headlamps, adaptive driving beam, light-signalling, or UN Regulation No 48, 148, 149, 150, 123, 45, 37, 99 or 128.\n")
for base, lid in [("32019R2144", "L10"), ("32009R0661", "L11")]:
    md.append("**%s — %s** (%d hits)\n" % (lid, base, len(S1[base])))
    md.append("| CELEX | title (adoption date removed) | decision |")
    md.append("|---|---|---|")
    for r in S1[base]: md.append("| %s | %s | %s |" % (r["celex"], esc(r["title"]), esc(r["decision"])))
    md.append("")
md.append("## 6. References not accessible\n")
for k in out["references_not_accessible"]:
    md.append("- **%s** %s — %s" % (k, L[k]["identifier"], L[k]["landing_note"]))
md.append("\nCited documents whose own title/scope could not be read (so not added): UN R70, UN R88 (cited by L01); SAE J567, J573, J602, J2009 (cited by L12; test 2 not established). See L1B-S5.\n")
md.append("## 7. Deviations from the protocol\n")
for a, b in deviations: md.append("- **%s.** %s" % (a, b))
open(O + "/L1B_instruments_L.md", "w").write("\n".join(md) + "\n")
print("instruments", len(L), "seed", ns, "added", na)
print(json.dumps(tot))
for k in sorted(hitcounts): print(k, hitcounts[k])
