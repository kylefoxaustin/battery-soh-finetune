import json, re, sys, csv
S = "<scratch>/l1_screen"
OUT = S + "/out"

UA = "L1-screener research fetch (public regulatory texts)"
EURLEX = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:"
OPENSTD = "https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno="
ECFR = "https://www.ecfr.gov/current/title-49/subtitle-B/chapter-V/part-571/section-571."
UNECE_REG = "https://unece.org/transport/vehicle-regulations-wp29/standards/addenda-1958-agreement-regulations-"

NA_REF = "not accessible"

# ---------------------------------------------------------------- seed instruments (S0 order)
# fields: key, domain, identifier, title, body, jurisdiction, landing, scope, scope_src, ref_src, refs_file, note
seeds = [
 dict(key="EU 2023/1542", dom="B", ident="Regulation (EU) 2023/1542",
  title="Regulation (EU) 2023/1542 of the European Parliament and of the Council concerning batteries and waste batteries, amending Directive 2008/98/EC and Regulation (EU) 2019/1020 and repealing Directive 2006/66/EC",
  body="European Parliament and Council (EU)", jur="EU", landing=EURLEX+"32023R1542",
  scope="\"This Regulation lays down requirements on sustainability, safety, labelling, marking and information to allow the placing on the market or putting into service of batteries within the Union. It also lays down minimum requirements for extended producer responsibility, the collection and treatment of waste batteries and for reporting.\" (Art. 1(1)); \"This Regulation applies to all categories of batteries, namely portable batteries, starting, lighting and ignition batteries (SLI batteries), light means of transport batteries (LMT batteries), electric vehicle batteries and industrial batteries [...]\" (Art. 1(3))",
  ref_src="EUR-Lex OJ text (CELEX 32023R1542, original act, not a consolidated version): Articles (Art. 95 'Repeal and transitional rules' excluded) and Annexes; recitals and footnotes excluded",
  refs="refs_eu_32023R1542.json",
  extra_refs={"ISO/IEC 15459-1":["art_77"],"ISO/IEC 15459-2":["art_77"],"ISO/IEC 15459-3":["art_77"],"ISO/IEC 15459-4":["art_77"],"ISO/IEC 15459-5":["art_77"],"ISO/IEC 15459-6":["art_77"]},
  s1=True),
 dict(key="EU 2024/1257", dom="B", ident="Regulation (EU) 2024/1257 (battery-durability provisions)",
  title="Regulation (EU) 2024/1257 of the European Parliament and of the Council on type-approval of motor vehicles and engines and of systems, components and separate technical units intended for such vehicles, with respect to their emissions and battery durability (Euro 7), amending Regulation (EU) 2018/858 of the European Parliament and of the Council and repealing Regulations (EC) No 715/2007 and (EC) No 595/2009 of the European Parliament and of the Council, Commission Regulation (EU) No 582/2011, Commission Regulation (EU) 2017/1151, Commission Regulation (EU) 2017/2400 and Commission Implementing Regulation (EU) 2022/1362",
  body="European Parliament and Council (EU)", jur="EU", landing=EURLEX+"32024R1257",
  scope="\"This Regulation applies to motor vehicles of categories M1, M2, M3, N1, N2 and N3, as well as trailers of categories O3 and O4 as specified in Article 4 of Regulation (EU) 2018/858, including those designed and constructed in one or more stages, and to systems, components and separate technical units intended for such vehicles, and C1, C2 and C3 class tyres, as specified in UN Regulation No 117, with the exception of ice grip tyres.\" (Art. 2)",
  ref_src="EUR-Lex OJ text (CELEX 32024R1257, original act): all Articles (none headed transitional) and Annexes; recitals and footnotes excluded. References taken from the whole act; test 3 confines additions to domain B",
  refs="refs_eu_32024R1257.json", s1=True),
 dict(key="UN GTR 22", dom="B", ident="UN GTR No. 22",
  title="United Nations Global Technical Regulation No. 22: United Nations Global Technical Regulation on In-vehicle Battery Durability for Electrified Vehicles",
  body="UNECE WP.29 (1998 Agreement)", jur="UN (1998 Agreement; EU, China and US are Contracting Parties)",
  landing="https://unece.org/transport/standards/transport/vehicle-regulations-wp29/global-technical-regulations-gtrs",
  scope="\"This GTR applies to vehicles of categories 1-2 and 2, that have a technically permissible maximum laden mass not exceeding 3,855 kg, and to vehicles of category 1-1, that (a) are PEV or OVC-HEV vehicles, and (b) have an originally installed battery as defined in this GTR.\" (para. 2)",
  ref_src="ECE/TRANS/180/Add.22 via documents.un.org (unece.org returned HTTP 403): Part II 'Text of the GTR' only; Part I (statement of technical rationale) excluded",
  refs="refs_gtr22.json",
  note="unece.org blocked the screener's fetch (HTTP 403, Cloudflare); text read from the UN Official Document System copy of ECE/TRANS/180/Add.22"),
 dict(key="UN R100", dom="B", ident="UN Regulation No. 100",
  title="UN Regulation No 100 - Uniform provisions concerning the approval of vehicles with regard to specific requirements for the electric power train",
  body="UNECE WP.29 (1958 Agreement)", jur="UN-1958 Contracting Parties (incl. EU)", landing=UNECE_REG+"81-100",
  scope="\"Part I: Safety requirements with respect to the electric power train of road vehicles of categories M, N and O, with a maximum design speed exceeding 25 km/h, equipped with electric power train, excluding vehicles permanently connected to the grid.\" (1.1) \"Part II: Safety requirements with respect to the Rechargeable Electrical Energy Storage System (REESS), of road vehicles of categories M, N and O equipped with electric power train, excluding vehicles permanently connected to the grid.\" (1.2)",
  ref_src="EUR-Lex OJ publication of the regulation text (most recent base text found by metadata query, chosen by script): body from para. 1 'Scope' to end incl. annexes; front matter and para. 13 'Transitional provisions' excluded",
  refs="refs_unr100.json", self_ids=["UN R100"]),
 dict(key="UN R155", dom="B", ident="UN Regulation No. 155",
  title="UN Regulation No. 155 - Uniform provisions concerning the approval of vehicles with regards to cyber security and cyber security management system",
  body="UNECE WP.29 (1958 Agreement)", jur="UN-1958 Contracting Parties (incl. EU)", landing=UNECE_REG+"141-160",
  scope="\"This Regulation applies to vehicles, with regard to cyber security, of Categories L, M, N and O, if fitted with at least one electronic control unit.\" (1.1)",
  ref_src="EUR-Lex OJ publication of the regulation text (chosen by script): body from para. 1 'Scope' incl. annexes; front matter excluded (no transitional section found)",
  refs="refs_unr155.json", self_ids=["UN R155"], note="vehicle-level instrument (pre-registration §1, sensitivities V2/V0)"),
 dict(key="UN R156", dom="B", ident="UN Regulation No. 156",
  title="UN Regulation No 156 - Uniform provisions concerning the approval of vehicles with regards to software update and software updates management system",
  body="UNECE WP.29 (1958 Agreement)", jur="UN-1958 Contracting Parties (incl. EU)", landing=UNECE_REG+"141-160",
  scope="\"This Regulation applies to vehicles of Categories M, N, O, R, S and T that permit software updates.\" (1.1)",
  ref_src="EUR-Lex OJ publication of the regulation text (chosen by script): body incl. annexes; front matter excluded (no transitional section found)",
  refs="refs_unr156.json", self_ids=["UN R156"], note="vehicle-level instrument (pre-registration §1, sensitivities V2/V0)"),
 dict(key="UN R10", dom="B", ident="UN Regulation No. 10 (charging-mode provisions)",
  title="UN Regulation No. 10 - Uniform provisions concerning the approval of vehicles with regard to electromagnetic compatibility",
  body="UNECE WP.29 (1958 Agreement)", jur="UN-1958 Contracting Parties (incl. EU)", landing=UNECE_REG+"0-20",
  scope="\"This Regulation applies to: Vehicles of categories L, M, N, O, T, R and S with regard to electromagnetic compatibility; Components and separate technical units intended to be fitted in these vehicles [...]\" (1.1-1.2) \"It covers: [...] (c) Additional requirements for vehicles and ESAs providing coupling systems for charging the REESS regarding the control of emissions and immunity from this connection between vehicle and [the power grid].\" (1.3)",
  ref_src="EUR-Lex OJ publication of the regulation text (chosen by script): body from para. 1 'Scope' incl. annexes; front matter and the 'Transitional provisions' section excluded. References taken from the whole regulation; test 3 confines additions to domain B",
  refs="refs_unr10.json", self_ids=["UN R10"]),
]
gb_B = [
 ("GB/T 32960.1","电动汽车远程服务与管理系统技术规范 第1部分：总则","Technical specifications for remote service and management system for electric vehicles - Part 1: General principle","67BCC8F6A51D4F19845F05BBFB7A63ED","recommended national standard (GB/T)"),
 ("GB/T 32960.2","电动汽车远程服务与管理系统技术规范 第2部分：车载终端","Technical specifications for remote service and management system for electric vehicles - Part 2: On-board terminal","86416884A36BBA4B20BEDBADE99CE4A1","recommended national standard (GB/T)"),
 ("GB/T 32960.3","电动汽车远程服务与管理系统技术规范 第3部分：通信协议及数据格式","Technical specifications for remote service and management system for electric vehicles - Part 3: Communication protocol and data format","868AD22C1502F9494A36019BB7B89737","recommended national standard (GB/T)"),
 ("GB 38031","电动汽车用动力蓄电池安全要求","Electric vehicles traction battery safety requirements","3AB693FAFF5D9716DF61C61D6FD2187A","mandatory national standard (GB)"),
 ("GB/T 18487.1","电动汽车传导充电系统 第1部分：通用要求","Electric vehicle conductive charging system - Part 1: General requirements","AEF144D5381E9FDBD265AFA5A87595A3","recommended national standard (GB/T)"),
 ("GB/T 27930","非车载传导式充电机与电动汽车之间的数字通信协议","Digital communication protocols between off-board conductive charger and electric vehicle","6ECF725CD2BCCA2819082279F6B2E243","recommended national standard (GB/T)"),
 ("GB 44495","汽车整车信息安全技术要求","Technical requirements for vehicle cybersecurity","2DB552CAA58F589705C3DC7AD47AC2AB","mandatory national standard (GB); vehicle-level instrument (pre-registration §1, sensitivities V2/V0)"),
 ("GB 44496","汽车软件升级通用技术要求","General technical requirements for software update of vehicles","8BC0D8B44DD4E71F9557BADE5175565A","mandatory national standard (GB); vehicle-level instrument (pre-registration §1, sensitivities V2/V0)"),
]
GB_SCOPE = "not accessible as text: openstd.samr.gov.cn gives title and metadata only; the full text is an in-browser image viewer behind a verification step, which the screener did not attempt to bypass"
GB_REFSRC = "references not accessible (no free text preview of clause 2; full text image-only behind a verification step)"
for ident, zh, en, hc, kind in gb_B:
    seeds.append(dict(key=ident, dom="B", ident=ident, title=f"{zh} / {en}", body="SAMR / SAC (China)", jur="China",
        landing=OPENSTD+hc, scope=GB_SCOPE, ref_src=GB_REFSRC, refs=None, note=kind))

ISO_NOTE = "iso.org returned HTTP 403 (Cloudflare challenge) to the screener's fetch and to WebFetch; not bypassed"
seeds += [
 dict(key="ISO 15118-2", dom="B", ident="ISO 15118-2", title="Road vehicles — Vehicle-to-Grid Communication Interface — Part 2: Network and application protocol requirements",
  body="ISO (TC 22/SC 31)", jur="International (ISO)", landing="https://www.iso.org/standard/55366.html", scope="not accessible ("+ISO_NOTE+")",
  ref_src="references not accessible ("+ISO_NOTE+"; no free preview reachable)", refs=None, note="title from iso.org page title as returned in a web-search result listing"),
 dict(key="ISO 15118-20", dom="B", ident="ISO 15118-20", title="Road vehicles — Vehicle to grid communication interface — Part 20: 2nd generation network layer and application layer requirements",
  body="ISO (TC 22/SC 31)", jur="International (ISO)", landing="https://www.iso.org/standard/77845.html", scope="not accessible ("+ISO_NOTE+")",
  ref_src="references not accessible ("+ISO_NOTE+")", refs=None, note="title from iso.org page title as returned in a web-search result listing"),
 dict(key="ISO 15118-8", dom="B", ident="ISO 15118-8", title="Road vehicles — Vehicle to grid communication interface — Part 8: Physical layer and data link layer requirements for wireless communication",
  body="ISO (TC 22/SC 31)", jur="International (ISO)", landing="https://www.iso.org/standard/80525.html", scope="not accessible ("+ISO_NOTE+")",
  ref_src="references not accessible ("+ISO_NOTE+")", refs=None, note="title from iso.org page title as returned in a web-search result listing"),
 dict(key="ISO 17409", dom="B", ident="ISO 17409", title="Electrically propelled road vehicles — Conductive power transfer — Safety requirements",
  body="ISO (TC 22/SC 37)", jur="International (ISO)", landing="https://www.iso.org/search.html?q=ISO%2017409", scope="not accessible ("+ISO_NOTE+")",
  ref_src="references not accessible ("+ISO_NOTE+")", refs=None, note="TITLE NOT VERIFIED at the publisher: title given from the screener's prior knowledge; landing is the ISO search URL because the standard page could not be fetched"),
 dict(key="IEC 61851-1", dom="B", ident="IEC 61851-1", title="Electric vehicle conductive charging system - Part 1: General requirements",
  body="IEC (TC 69)", jur="International (IEC)", landing="https://webstore.iec.ch/en/publication/33644",
  scope="\"[IEC 61851-1] applies to EV supply equipment for charging electric road vehicles, with a rated supply voltage up to 1 000 V AC or up to 1 500 V DC and a rated output voltage up to 1 000 V AC or up to 1 500 V DC. Electric road vehicles (EV) cover all road vehicles, including plug-in hybrid road vehicles (PHEV), that derive all or part of their energy from on-board rechargeable energy storage systems (RESS). The aspects covered in this standard include: the characteristics and operating conditions of the EV supply equipment; the specification of the connection between the EV supply equipment and the EV; the requirements for electrical safety for the EV supply equipment.\" (IEC webstore abstract)",
  ref_src="references not accessible (IEC preview PDF blocked to the screener's fetch: HTTP 403 from the preview endpoint; not bypassed)", refs=None),
 dict(key="IEC 61851-23", dom="B", ident="IEC 61851-23", title="Electric vehicle conductive charging system - Part 23: DC electric vehicle charging station",
  body="IEC (TC 69)", jur="International (IEC)", landing="https://webstore.iec.ch/en/publication/6032",
  scope="\"[IEC 61851-23] gives the requirements for d.c. electric vehicle (EV) charging stations, herein also referred to as 'DC charger', for conductive connection to the vehicle, with an a.c. or d.c. input voltage up to 1 000 V a.c. and up to 1 500 V d.c. according to IEC 60038. It provides the general requirements for the control communication between a d.c. EV charging station and an EV.\" (IEC webstore abstract of the publication page used as landing)",
  ref_src="references not accessible (IEC preview blocked; not bypassed)", refs=None,
  note="the landing page is an IEC webstore publication page located by id; the current-publication page could not be located because IEC catalogue search is script-rendered; title from the screener's knowledge of the series title pattern, NOT VERIFIED"),
 dict(key="IEC 61851-24", dom="B", ident="IEC 61851-24", title="Electric vehicle conductive charging system - Part 24: Digital communication between a d.c. EV charging station and an electric vehicle for control of d.c. charging",
  body="IEC (TC 69)", jur="International (IEC)", landing="https://webstore.iec.ch/en/publication/6033",
  scope="\"[IEC 61851-24], together with IEC 61851-23, applies to digital communication between a d.c. EV charging station and an electric road vehicle (EV) for control of d.c. charging, with an a.c. or d.c. input voltage up to 1 000 V a.c. and up to 1 500 V d.c. for the conductive charging procedure.\" (IEC webstore abstract)",
  ref_src="references not accessible (IEC preview blocked; not bypassed)", refs=None,
  note="as IEC 61851-23: landing located by id; title from the screener's knowledge, NOT VERIFIED"),
]
SAE_NOTE = "sae.org served an AWS-WAF challenge / script-only page to the screener's fetch and to WebFetch; not bypassed"
def sae(key, title, note, landing=None):
    return dict(key=key, dom="B", ident="SAE "+key.split(" ",1)[1] if key.startswith("SAE") else key, title=title, body="SAE International", jur="International (SAE; primarily US/North America)",
        landing=landing or "https://www.sae.org/standards/content/"+key.split(" ")[1].lower()+"/", scope="not accessible ("+SAE_NOTE+")",
        ref_src="references not accessible ("+SAE_NOTE+")", refs=None, note=note)
seeds += [
 sae("SAE J1772", "SAE Electric Vehicle and Plug in Hybrid Electric Vehicle Conductive Charge Coupler", "TITLE NOT VERIFIED at the publisher (screener's prior knowledge)"),
 sae("SAE J3400", "North American Charging System (NACS) for Electric Vehicles", "TITLE NOT VERIFIED at the publisher (screener's prior knowledge)"),
 sae("SAE J2847/1", "Communication for Smart Charging of Plug-in Electric Vehicles Using Smart Energy Profile 2.0", "S0 series expansion: kept (title names communication with the grid side for smart charging); title from an SAE web-search result listing"),
 sae("SAE J2847/2", "Communication Between Plug-in Vehicles and Off-Board DC Chargers", "S0 series expansion: kept (title names communication between vehicle and charger); title from an SAE web-search result listing"),
 sae("SAE J2847/3", "Communication for Plug-in Vehicles as a Distributed Energy Source", "S0 series expansion: kept (title names the vehicle as a grid-side energy source, i.e. bidirectional / vehicle-to-grid); title from an SAE web-search result listing"),
 sae("SAE J2847/6", "Communication for Wireless Power Transfer Between Light-Duty Plug-in Electric Vehicles and Wireless EV Charging Stations", "S0 series expansion: kept (title names communication between vehicle and charging station); title from an SAE web-search result listing"),
 sae("SAE J2931/1", "Digital Communications for Plug-in Electric Vehicles", "S0 series expansion: kept as JUDGEMENT (title names digital communications of plug-in EVs, read as the charging-interface side; the title does not literally name the charger or grid); title from an SAE web-search result listing"),
 sae("SAE J2931/4", "Broadband PLC Communication for Plug-in Electric Vehicles", "S0 series expansion: kept as JUDGEMENT (power-line communication of plug-in EVs, read as charging-interface communication); title from an SAE web-search result listing"),
 sae("SAE J2931/6", "Signaling Communication for Wirelessly Charged Electric Vehicles", "S0 series expansion: kept as JUDGEMENT (signalling communication for wireless charging, read as vehicle-to-charger communication); title from an SAE web-search result listing"),
 sae("SAE J2931/7", "Security for Plug-In Electric Vehicle Communications", "S0 series expansion: kept as JUDGEMENT (security of plug-in EV communications, read as charging/grid-side communication); title from an SAE web-search result listing"),
]
seeds += [
 dict(key="FMVSS 305", dom="B", ident="FMVSS No. 305 (49 CFR 571.305)", title="Standard No. 305; electric-powered vehicles: electrolyte spillage and electrical shock protection [applicability clause of the section heading omitted]",
  body="NHTSA (US DOT)", jur="United States", landing=ECFR+"305",
  scope="\"This standard specifies requirements for limitation of electrolyte spillage and retention of electric energy storage/conversion devices during and after a crash, and protection from harmful electric shock during and after a crash and during normal vehicle operation.\" (S1)",
  ref_src="eCFR section text (versioner API); source/amendment citations stripped by script; phase-in paragraphs excluded where headed as such", refs="refs_fmvss_305.json", self_ids=["FMVSS 305"]),
 dict(key="FMVSS 305a", dom="B", ident="FMVSS No. 305a (49 CFR 571.305a)", title="Standard No. 305a; electric-powered vehicles: Electric powertrain integrity [applicability clause of the section heading omitted]",
  body="NHTSA (US DOT)", jur="United States", landing=ECFR+"305a",
  scope="\"This standard specifies requirements for protection from harmful electric shock, fire, explosion, and gas venting during normal vehicle operation and during and after a crash.\" (S1)",
  ref_src="eCFR section text; source/amendment citations stripped by script", refs="refs_fmvss_305a.json", self_ids=["FMVSS 305a"],
  note="the seed names 'FMVSS 305 / 305a'; listed as two instruments because they are separate CFR sections"),
 dict(key="EU 2023/1804", dom="B", ident="Regulation (EU) 2023/1804 (vehicle-side obligations)",
  title="Regulation (EU) 2023/1804 of the European Parliament and of the Council on the deployment of alternative fuels infrastructure, and repealing Directive 2014/94/EU",
  body="European Parliament and Council (EU)", jur="EU", landing=EURLEX+"32023R1804",
  scope="\"This Regulation establishes mandatory national targets leading to the deployment of sufficient alternative fuels infrastructure in the Union for road vehicles, trains, vessels and stationary aircraft. It lays down common technical specifications and requirements on user information, data provision and payment requirements for alternative fuels infrastructure.\" (Art. 1(1))",
  ref_src="EUR-Lex OJ text (CELEX 32023R1804, original act): all Articles (none headed transitional) and Annexes; recitals and footnotes excluded",
  refs="refs_eu_32023R1804.json", s1=True),
]
# domain S
def unS(n, celex, title, scope, refs, rng, note=None, trans=True):
    return dict(key=f"UN R{n}", dom="S", ident=f"UN Regulation No. {n}", title=title, body="UNECE WP.29 (1958 Agreement)", jur="UN-1958 Contracting Parties (incl. EU)",
        landing=UNECE_REG+rng, scope=scope,
        ref_src="EUR-Lex OJ publication of the regulation text (chosen by script): body from para. 1 'Scope' incl. annexes; front matter"+(" and the 'Transitional provisions' section" if trans else "")+" excluded",
        refs=refs, self_ids=[f"UN R{n}"], note=note)
seeds += [
 unS(14,"42019X2141","UN Regulation No 14 - Uniform provisions concerning the approval of vehicles with regard to safety-belt anchorages",
   "\"This Regulation applies to: Vehicles of categories M and N with regard to their anchorages for safety-belts intended for adult occupants of forward-facing or rearward-facing or side-facing seats.\" (1)","refs_unr14.json","0-20"),
 unS(16,"42018X0629","Regulation No 16 of the Economic Commission for Europe of the United Nations (UNECE) - Uniform provisions concerning the approval of: I. Safety-belts, restraint systems, child restraint systems and ISOFIX child restraint systems for occupants of power-driven vehicles; II. Vehicles equipped with safety-belts, safety-belt reminders, restraint systems, child restraint systems, ISOFIX child restraint systems and i-Size child restraint systems",
   "\"This Regulation applies to: Vehicles of category M, N, O, L2, L4, L5, L6, L7 and T, with regard to the installation of safety-belts and restraint systems which are intended for separate use, i.e. as individual fittings, by persons of adult build occupying forward-facing, rearward-facing or side-facing seats\" (1.1); \"Safety-belts and restraint systems which are intended for separate use [...] by persons of adult build [...] and are designed for installation in vehicles of category M, N, O, L2 [...]\" (1.2)","refs_unr16.json","0-20",
   note="full title from EUR-Lex metadata (the screener's first print truncated it)"),
 unS(17,"42023X0406","UN Regulation No 17 - Uniform provisions concerning the approval of vehicles with regard to the seats, their anchorages and any head restraints",
   "\"This Regulation applies to: (a) Vehicles of categories M1 and N with regard to the strength of seats and their anchorages and with regard to their head restraints; (b) Vehicles of categories M2 and M3 with regard to seats not covered by Regulation No 80, in respect of the strength of seats and their anchorages, and in respect of their head restraints; (c) Vehicles of category M1 with regard to the design of the rear parts of seat backs and the design of devices intended to protect the occupants from the danger resulting from the displacement of luggage in a frontal impact.\" (1)","refs_unr17.json","0-20"),
 unS(25,"42020X1169","UN Regulation No 25 - Uniform provisions concerning the approval of head restraints (headrests), whether or not incorporated in vehicle seats",
   "\"This Regulation applies to head-restraint devices conforming to one of the types defined in paragraph 2.2 below.\" (1.1) \"It does not apply to head-restraint devices which may be fitted to folding seats or seats facing towards the side or towards the rear.\" (1.1.1) \"It applies to seat backs themselves, when they are so designed as to serve also as head restraints as defined in paragraph 2.2 below.\" (1.1.2)","refs_unr25.json","21-40"),
 unS(44,"42020X1223","UN Regulation No 44 - Uniform provisions concerning the approval of restraining devices for child occupants of power-driven vehicles ('Child Restraint Systems')",
   "\"This Regulation applies to child restraint systems which are suitable for installation in power-driven vehicles having three or more wheels, and which are not intended for use with folding (tip-up) or with side-facing seats.\" (1.1)","refs_unr44.json","41-60"),
 unS(129,"42026X1534","UN Regulation No. 129 - Uniform provisions concerning the approval of Enhanced Child Restraint Systems used on board of motor vehicles",
   "\"This Regulation applies to the following child restraint systems for child occupants of power driven vehicles: (a) Integral Universal ISOFIX Enhanced Child Restraint Systems (i-Size); (b) Integral Specific vehicle ISOFIX Enhanced Child Restraint Systems; (c) Non-integral Universal Enhanced Child Restraint Systems (i-Size booster seat); [...]\" (1)","refs_unr129.json","121-140"),
]
def fm(n, title, scope, refs, note=None):
    return dict(key=f"FMVSS {n}", dom="S", ident=f"FMVSS No. {n} (49 CFR 571.{n})", title=title, body="NHTSA (US DOT)", jur="United States",
        landing=ECFR+n, scope=scope, ref_src="eCFR section text (versioner API); source/amendment citations stripped by script; phase-in paragraphs excluded where headed as such; incorporations by reference named in the text taken as cited (49 CFR 571.5 itself not separately read)",
        refs=refs, self_ids=[f"FMVSS {n}"], note=note)
seeds += [
 fm("202a","Standard No. 202a; Head restraints [applicability clause of the section heading omitted]","\"This standard specifies requirements for head restraints to reduce the frequency and severity of neck injury in rear-end and other collisions.\" (S1)","refs_fmvss_202a.json"),
 fm("207","Standard No. 207; Seating systems","\"This standard establishes requirements for seats, their attachment assemblies, and their installation to minimize the possibility of their failure by forces acting on them as a result of vehicle impact.\" (S1)","refs_fmvss_207.json"),
 fm("208","Standard No. 208; Occupant crash protection","\"This standard specifies performance requirements for the protection of vehicle occupants in crashes.\" (S1) \"The purpose of this standard is to reduce the number of deaths of vehicle occupants, and the severity of injuries, by specifying vehicle crashworthiness requirements in terms of forces and accelerations measured on anthropomorphic dummies in test crashes, and by specifying equipment requirements for active and passive restraint systems.\" (S2)","refs_fmvss_208.json",
   note="seed names FMVSS 208 for occupant classification; references taken from the whole standard"),
 fm("209","Standard No. 209; Seat belt assemblies","\"This standard specifies requirements for seat belt assemblies.\" (S1) \"This standard applies to seat belt assemblies for use in passenger cars, multipurpose passenger vehicles, trucks, and buses.\" (S2)","refs_fmvss_209.json"),
 fm("210","Standard No. 210; Seat belt assembly anchorages","\"This standard establishes requirements for seat belt assembly anchorages to insure their proper location for effective occupant restraint and to reduce the likelihood of their failure.\" (S1)","refs_fmvss_210.json"),
 fm("225","Standard No. 225; Child restraint anchorage systems","\"This standard establishes requirements for child restraint anchorage systems to ensure their proper location and strength for the effective securing of child restraints, to reduce the likelihood of the anchorage systems' failure, and to increase the likelihood that child restraints are properly secured and thus more fully achieve their potential effectiveness in motor vehicles.\" (S1)","refs_fmvss_225.json"),
 dict(key="EU 2019/2144", dom="S", ident="Regulation (EU) 2019/2144 (provisions naming seat-belt reminders or seating)",
  title="Regulation (EU) 2019/2144 of the European Parliament and of the Council on type-approval requirements for motor vehicles and their trailers, and systems, components and separate technical units intended for such vehicles, as regards their general safety and the protection of vehicle occupants and vulnerable road users, amending Regulation (EU) 2018/858 of the European Parliament and of the Council and repealing Regulations (EC) No 78/2009, (EC) No 79/2009 and (EC) No 661/2009 of the European Parliament and of the Council and Commission Regulations (EC) No 631/2009, (EU) No 406/2010, (EU) No 672/2010, (EU) No 1003/2010, (EU) No 1005/2010, (EU) No 1008/2010, (EU) No 1009/2010, (EU) No 19/2011, (EU) No 109/2011, (EU) No 458/2011, (EU) No 65/2012, (EU) No 130/2012, (EU) No 347/2012, (EU) No 351/2012, (EU) No 1230/2012 and (EU) 2015/166",
  body="European Parliament and Council (EU)", jur="EU", landing=EURLEX+"32019R2144",
  scope="\"This Regulation applies to vehicles of categories M, N and O, as defined in Article 4 of Regulation (EU) 2018/858, and to systems, components and separate technical units designed and constructed for such vehicles.\" (Art. 2)",
  ref_src="EUR-Lex OJ text (CELEX 32019R2144, original act): Articles (Art. 15 'Transitional provisions' excluded) and Annexes; recitals and footnotes excluded. References taken from the whole act; test 3 confines additions to domain S",
  refs="refs_eu_32019R2144.json", s1=True,
  note="full title from EUR-Lex metadata"),
]
gb_S = [
 ("GB 14167","机动车乘员用安全带和约束系统安装固定点","Safety-belt anchorages and restraint systems anchorages for occupants of power-driven vehicles","21DD8BFD6059935369C02BB322D0C21D"),
 ("GB 15083","汽车座椅、座椅固定装置及头枕强度要求和试验方法","Strength requirement and test method of automobile seats, their anchorages and any head restraints","1CF9B46ABDA760CCC9FCD47B0C1AAD3F"),
 ("GB 11550","汽车座椅头枕强度要求和试验方法","Strength requirement and test of automobile seats head restraints","85EA6B0D7F181888D5781568DDDCFBFA"),
]
for ident, zh, en, hc in gb_S:
    seeds.append(dict(key=ident, dom="S", ident=ident, title=f"{zh} / {en}", body="SAMR / SAC (China)", jur="China",
        landing=OPENSTD+hc, scope=GB_SCOPE, ref_src=GB_REFSRC, refs=None, note="mandatory national standard (GB)"))

# ---------------------------------------------------------------- canonicalisation of cited identifiers
def canon(raw):
    r = re.sub(r'\s+', ' ', raw).strip()
    m = re.match(r'^(?:UN )?Regulations? Nos?\.? ?(\d+)(?:, ?\d{2})?((?: ?(?:,|and) ?\d+)*)$', r) or re.match(r'^UN(?:/ECE)? Regulation (?:No\.? ?)?(\d+)(?:, ?\d{2})?()$', r)
    if m:
        nums = [m.group(1)] + re.findall(r'\d+', m.group(2) or '')
        return ['UN R%s' % n for n in nums]
    m = re.match(r'^UN GTR No\.? ?(\d+)$', r)
    if m: return ['UN GTR %s' % m.group(1)]
    if r.startswith('ECE/TRANS/WP.29/78'): return ['ECE/TRANS/WP.29/78 (R.E.3)']
    m = re.match(r'^(?:§ ?571\.|Standard No\. ?|FMVSS No\. ?)(\d+[a-z]?)$', r)
    if m:
        n = m.group(1)
        if n == '5': return ['49 CFR 571.5']
        if n == '3': return ['49 CFR 571.3']
        return ['FMVSS %s' % n]
    m = re.match(r'^(?:49 CFR )?[Pp]art (\d+)$', r) or re.match(r'^§ ?(5\d\d)\.\d+$', r)
    if m: return ['49 CFR Part %s' % m.group(1)]
    m = re.match(r'^SAE (?:Standard |Recommended Practice |Information Report )?(J ?\d+(?:/\d+)?)$', r)
    if m: return ['SAE %s' % m.group(1).replace(' ', '')]
    m = re.match(r'^(ISO(?:/IEC|/TS|/TR|/PAS)?) (\d+(?:-\d+)*)(?:-(?:19|20)\d\d)?$', r)
    if m:
        ident = '%s %s' % (m.group(1), m.group(2))
        if ident == 'ISO 17': return ['ISO 17373']   # text 'ISO 17 373' split by the parser (verified)
        if ident == 'ISO 26262-2018': return ['ISO 26262']
        return [ident]
    if r == 'Council Directive 2009/71': return ['Directive 2009/71/Euratom']
    return [r]

# ---------------------------------------------------------------- judgements
# value: (title or subject, title_basis, t1, t2, t3B, t3S, reason)
J = {}
def j(ids, title, basis, t1, t2, t3B=False, t3S=False, why=''):
    for i in ([ids] if isinstance(ids, str) else ids):
        J[i] = dict(title=title, title_basis=basis, t1=t1, t2=t2, t3B=t3B, t3S=t3S, why=why)
CIT = 'title as given in the citing text'
EUT = 'title from the citing act (EUR-Lex)'
KNOW = "screener's knowledge of the title (publisher page not fetched)"
# not instruments under §2 (test 1 fails)
j('ECE/TRANS/WP.29/78 (R.E.3)', 'Consolidated Resolution on the Construction of Vehicles (R.E.3)', CIT, False, None, why='a WP.29 resolution, not a regulation or standard')
j('ECE/TRANS/WP.29/1101', 'WP.29 document ECE/TRANS/WP.29/1101', CIT, False, None, why='a WP.29 working document, not a regulation or standard')
for e in ['EN 62196-2','EN 62196-3','EN 61851-23-1','EN 50696','EN 17127','EN 17124','EN 15869-2','EN 16840','EN 16942','EN 17186','EN 50436','EN 71-2','EN 71-3','EN 17025']:
    j(e, 'European standard '+e, CIT, False, None, why='EN (CEN/CENELEC) standards are not in the closed §2 list (regulation, directive, GTR, UN regulation, GB/GB/T, ISO, IEC, SAE); no substitution of an IEC/ISO parent was made')
for e in ['ASTM E274','ASTM B456','ASTM E4','ASTM G23','ASTM B117','ASTM D756']:
    j(e, 'ASTM standard '+e, CIT, False, None, why='ASTM standards are not in the closed §2 list')
j(['Decision 97/836/EC','Decision No 1247/2002/EC'], 'Council/EP decision', EUT, False, None, why='a decision, not a regulation or directive')
j('49 CFR 571.5', 'Matter incorporated by reference (list)', CIT, False, None, why='the incorporation-by-reference list itself; the incorporated documents it names in the citing text are recorded separately')
# EU acts: t1 pass; t2 by scope
eu_nonveh = {
 'Directive 2009/71/Euratom':'nuclear safety of nuclear installations','Directive 2012/19/EU':'waste electrical and electronic equipment','Directive 2008/98/EC':'waste',
 'Regulation (EU) No 1025/2012':'European standardisation','Regulation (EC) No 765/2008':'accreditation and market surveillance','Directive 2004/109/EC':'transparency requirements for issuers of securities',
 'Regulation (EU) 2017/821':'supply chain due diligence for tin, tantalum, tungsten and gold','Directive 2011/83/EU':'consumer rights','Regulation (EC) No 1272/2008':'classification, labelling and packaging of substances',
 'Regulation (EU) 2022/2065':'single market for digital services','Regulation (EU) 2019/943':'internal market for electricity','Regulation (EU) 2019/1020':'market surveillance and compliance of products',
 'Directive (EU) 2019/944':'common rules for the internal market for electricity','Regulation (EC) No 1907/2006':'REACH (chemicals)','Regulation (EU) 2017/745':'medical devices','Regulation (EU) 2017/746':'in vitro diagnostic medical devices',
 'Directive 2008/68/EC':'inland transport of dangerous goods','Directive 2010/75/EU':'industrial emissions','Directive 2014/24/EU':'public procurement','Directive 2014/25/EU':'procurement by utilities',
 'Regulation (EU) No 182/2011':'comitology (implementing powers)','Directive 2006/66/EC':'batteries and accumulators (repealed by the citing act)','Directive 2014/53/EU':'radio equipment','Regulation (EC) No 1013/2006':'shipments of waste',
 'Directive (EU) 2018/2001':'renewable energy','Regulation (EU) No 1315/2013':'TEN-T guidelines','Regulation (EU) 2018/1139':'civil aviation','Regulation (EU) 2015/757':'maritime CO2 monitoring',
 'Directive (EU) 2015/2366':'payment services','Regulation (EU) 2022/1012':'safe and secure truck parking areas (delegated act)','Regulation (EU) 2023/1805':'renewable and low-carbon fuels in maritime transport',
 'Directive (EU) 2019/882':'accessibility requirements for products and services','Regulation (EU) 2017/352':'port services','Regulation (EU) 2022/670':'EU-wide real-time traffic information services (delegated act)',
 'Directive 2014/94/EU':'alternative fuels infrastructure (repealed by the citing act)','Regulation (EU) 2018/732':'alternative fuels unit price comparison methodology',
 'Directive 2008/50/EC':'ambient air quality','Regulation (EU) 2023/2854':'harmonised rules on fair access to and use of data (Data Act)','Regulation (EU) 2017/2394':'consumer protection cooperation',
 'Directive (EU) 2020/1828':'representative actions for consumers','Regulation (EU) 2016/679':'protection of personal data (GDPR)','Directive 95/46/EC':'protection of personal data (repealed)','Regulation (EU) 2018/1725':'personal data processing by Union institutions','Regulation (EC) No 45/2001':'personal data processing by Union institutions (repealed)',
}
for k,v in eu_nonveh.items(): j(k, v, EUT+' (subject)', True, False, why='scope does not name road vehicles, EVs or the charging interface')
eu_veh = {
 'Regulation (EU) No 168/2013':'approval and market surveillance of two- or three-wheel vehicles and quadricycles','Regulation (EU) 2018/858':'approval and market surveillance of motor vehicles and their trailers (framework)',
 'Directive 2000/53/EC':'end-of-life vehicles','Directive 2010/40/EU':'framework for the deployment of Intelligent Transport Systems in road transport',
 'Directive 2014/45/EU':'periodic roadworthiness tests for motor vehicles','Directive 2014/47/EU':'technical roadside inspection of commercial vehicles','Regulation (EU) 2019/1242':'CO2 emission performance standards for new heavy-duty vehicles',
 'Regulation (EC) No 595/2009':'type-approval with respect to emissions from heavy-duty vehicles (Euro VI)','Regulation (EU) 2017/1151':'type-approval with respect to emissions from light passenger and commercial vehicles (implementing)',
 'Regulation (EC) No 715/2007':'type approval with respect to emissions from light passenger and commercial vehicles (Euro 5 and Euro 6)','Regulation (EU) 2022/1362':'heavy-duty vehicles: performance of trailers with regard to CO2 and fuel consumption (implementing)',
 'Regulation (EU) 2023/851':'CO2 emission performance standards for cars and vans (amending act)','Regulation (EU) 2019/631':'CO2 emission performance standards for new passenger cars and light commercial vehicles',
 'Council Directive 96/53/EC':'maximum dimensions and weights of road vehicles','Directive 2007/46/EC':'framework for the approval of motor vehicles (repealed)','Regulation (EU) No 582/2011':'heavy-duty vehicle emissions (implementing)',
 'Regulation (EC) No 692/2008':'light-duty vehicle emissions (implementing)','Regulation (EU) No 1230/2012':'type-approval requirements for masses and dimensions of motor vehicles','Regulation (EU) 2017/2400':'determination of CO2 emissions and fuel consumption of heavy-duty vehicles',
 'Regulation (EU) 2020/683':'administrative requirements for approval and market surveillance of motor vehicles (implementing)','Directive 2009/40/EC':'roadworthiness tests (repealed)','Directive 2000/30/EC':'technical roadside inspection of commercial vehicles (repealed)',
 'Regulation (EC) No 661/2009':'type-approval requirements for the general safety of motor vehicles (repealed by the citing act)','Regulation (EC) No 79/2009':'type-approval of hydrogen-powered motor vehicles (repealed by the citing act)',
 'Regulation (EC) No 78/2009':'type-approval of motor vehicles with regard to the protection of pedestrians (repealed by the citing act)',
}
for k,v in eu_veh.items(): j(k, v, EUT+' (subject)', True, True, why='vehicle instrument whose title/scope does not concern the citing domain\'s subsystems (§1)')
# listed EU acts cited by others
j('Regulation (EU) 2019/2144', 'general safety type-approval (listed as EU 2019/2144)', EUT, True, True, False, True)
j('Regulation (EU) 2023/1542', 'batteries and waste batteries (listed)', EUT, True, True, True, False)
# ISO/IEC/CISPR general (not vehicles)
gen = {'ISO 14040':'Environmental management - Life cycle assessment','IEC 62619':'Secondary lithium cells and batteries for use in industrial applications',
 'ISO/IEC 15459-1':'Unique identification (parts 1-6)','ISO/IEC 15459-2':'Unique identification','ISO/IEC 15459-3':'Unique identification','ISO/IEC 15459-4':'Unique identification','ISO/IEC 15459-5':'Unique identification','ISO/IEC 15459-6':'Unique identification',
 'ISO/IEC 18004':'QR Code bar code symbology','IEC 60884-1':'Plugs and socket-outlets for household purposes','IEC 62613-1':'Plugs, socket-outlets and ship couplers for high-voltage shore connection systems',
 'ISO 16923':'Natural gas fuelling stations - CNG stations for fuelling vehicles','ISO 16924':'Natural gas fuelling stations - LNG stations for fuelling vehicles','ISO 20519':'Ships and marine technology - Specification for bunkering of LNG fuelled vessels',
 'IEC 61508':'Functional safety of electrical/electronic/programmable electronic safety-related systems',
 'CISPR 16':'Specification for radio disturbance and immunity measuring apparatus and methods','CISPR 22':'Information technology equipment - Radio disturbance characteristics','CISPR 32':'Electromagnetic compatibility of multimedia equipment - Emission requirements',
 'IEC 61000-3-2':'EMC - Limits for harmonic current emissions (equipment input current <= 16 A per phase)','IEC 61000-3-12':'EMC - Limits for harmonic currents (equipment input current > 16 A and <= 75 A per phase)',
 'IEC 61000-3-3':'EMC - Limitation of voltage changes, fluctuations and flicker (<= 16 A)','IEC 61000-3-11':'EMC - Limitation of voltage changes, fluctuations and flicker (<= 75 A, conditional connection)',
 'IEC 61000-6-3':'EMC - Generic standards - Emission standard for residential environments','IEC 61000-4-4':'EMC - Electrical fast transient/burst immunity test','IEC 61000-4-5':'EMC - Surge immunity test',
 'ISO 17025':'General requirements for the competence of testing and calibration laboratories (ISO/IEC 17025)',
 'ISO 105':'Textiles - Tests for colour fastness','ISO 139':'Textiles - Standard atmospheres for conditioning and testing','ISO 5725':'Accuracy (trueness and precision) of measurement methods and results',
 'ISO 485':'Plastics / rubber material test (as cited)','ISO 2439':'Flexible cellular polymeric materials - Determination of hardness','ISO 3386':'Polymeric materials, cellular flexible - Determination of stress-strain characteristics in compression',
 'ISO 1798':'Flexible cellular polymeric materials - Determination of tensile strength and elongation at break','ISO 1856':'Flexible cellular polymeric materials - Determination of compression set','ISO 845':'Cellular plastics and rubbers - Determination of apparent density',
 'ISO 4287':'Geometrical product specifications - Surface texture: profile method','ISO 9002':'Quality systems (model for quality assurance)','ISO 7380-2':'Hexagon socket button head screws',
}
for k,v in gen.items(): j(k, v, KNOW+'; subject only', True, False, why='scope does not name road vehicles, EVs or the charging interface')
# vehicle ISO/SAE/CISPR - fail test 3
veh = {'ISO 11992-2':'Road vehicles - Interchange of digital information on electrical connections between towing and towed vehicles - Part 2: Application layer for brakes and running gear',
 'ISO 17840-4':'Road vehicles - Information for first and second responders - Part 4: Propulsion energy identification','ISO 26262':'Road vehicles - Functional safety','ISO/PAS 21448':'Road vehicles - Safety of the intended functionality',
 'CISPR 12':'Vehicles, boats and internal combustion engines - Radio disturbance characteristics - Limits and methods of measurement for the protection of off-board receivers',
 'CISPR 25':'Vehicles, boats and internal combustion engines - Radio disturbance characteristics - Limits and methods of measurement for the protection of on-board receivers',
 'ISO 7637-2':'Road vehicles - Electrical disturbances from conduction and coupling - Part 2: Electrical transient conduction along supply lines only',
 'ISO 11451':'Road vehicles - Vehicle test methods for electrical disturbances from narrowband radiated electromagnetic energy (series)','ISO 11451-1':'Road vehicles - Vehicle test methods for electrical disturbances ... - Part 1: General principles and terminology',
 'ISO 11451-2':'Road vehicles - Vehicle test methods for electrical disturbances ... - Part 2: Off-vehicle radiation sources','ISO 11451-4':'Road vehicles - Vehicle test methods for electrical disturbances ... - Part 4: Bulk current injection (BCI)',
 'ISO 11452':'Road vehicles - Component test methods for electrical disturbances from narrowband radiated electromagnetic energy (series)','ISO 11452-1':'Road vehicles - Component test methods ... - Part 1: General principles and terminology',
 'ISO 11452-2':'Road vehicles - Component test methods ... - Part 2: Absorber-lined shielded enclosure','ISO 11452-3':'Road vehicles - Component test methods ... - Part 3: Transverse electromagnetic (TEM) cell',
 'ISO 11452-4':'Road vehicles - Component test methods ... - Part 4: Harness excitation methods','ISO 11452-5':'Road vehicles - Component test methods ... - Part 5: Stripline',
 'ISO 17268':'Gaseous hydrogen land vehicle refuelling connection devices','ISO 14469':'Road vehicles - Compressed natural gas (CNG) refuelling connector','ISO 12617':'Road vehicles - Liquefied natural gas (LNG) refuelling connector',
 'ISO 23273':'Fuel cell road vehicles - Safety specifications - Protection against hydrogen hazards','SAE J2578':'General Fuel Cell Vehicle Safety',
 'ISO 3560':'Road vehicles - Frontal fixed barrier or pole impact test procedure','ISO 6487':'Road vehicles - Measurement techniques in impact tests - Instrumentation','ISO 2575':'Road vehicles - Symbols for controls, indicators and tell-tales',
 'ISO/TS 13499':'Road vehicles - Multimedia data exchange format for impact tests','SAE J211':'Instrumentation for Impact Test','SAE J211/1':'Instrumentation for Impact Test - Part 1: Electronic Instrumentation',
 'SAE J726':'Air Cleaner Test Code','SAE J1100':'Motor Vehicle Dimensions',
 '49 CFR 571.3':'FMVSS definitions','49 CFR Part 572':'Anthropomorphic test devices','49 CFR Part 585':'Safety equipment phase-in reporting requirements','49 CFR Part 567':'Certification',
 '49 CFR Part 595':'Make inoperative exemptions','49 CFR Part 512':'Confidential business information','49 CFR Part 587':'Deformable barriers','49 CFR Part 552':'Petitions for rulemaking, defect, and noncompliance orders','49 CFR Part 555':'Temporary exemption from motor vehicle safety and bumper standards',
 'FMVSS 101':'Controls and displays','FMVSS 201':'Occupant protection in interior impact','FMVSS 214':'Side impact protection','FMVSS 301':'Fuel system integrity',
}
for k,v in veh.items(): j(k, v, KNOW+' (or as cited)', True, True, why="vehicle instrument whose title/scope does not concern the citing domain's subsystems (§1)")
unr = {1:'headlamps (asymmetrical passing beam, filament lamps R2/HS1)',3:'retro-reflecting devices',4:'rear registration plate lamps',6:'direction indicators',7:'position, stop and end-outline lamps',
 11:'door latches and door retention components',12:'protection of the driver against the steering mechanism in the event of impact',13:'braking (categories M, N, O)',18:'protection against unauthorized use',19:'front fog lamps',
 21:'interior fittings',23:'reversing and manoeuvring lamps',24:'visible pollutants of compression-ignition engines',26:'external projections',28:'audible warning devices',29:'protection of occupants of the cab of a commercial vehicle',
 30:'pneumatic tyres for motor vehicles and trailers',31:'sealed-beam headlamps',33:'behaviour of the structure of the impacted vehicle in a head-on collision',34:'prevention of fire risks',37:'filament light sources',38:'rear fog lamps',39:'speedometer and odometer',
 42:'front and rear protective devices (bumpers)',43:'safety glazing',45:'headlamp cleaners',46:'devices for indirect vision',48:'installation of lighting and light-signalling devices',49:'emissions of compression-ignition and positive-ignition engines (heavy duty)',
 52:'construction of small-capacity M2 and M3 vehicles',54:'pneumatic tyres for commercial vehicles',55:'mechanical coupling components',58:'rear underrun protective devices',61:'external projections forward of the cab rear panel of commercial vehicles',
 64:'temporary-use spare unit, run-flat tyres and tyre pressure monitoring',66:'strength of the superstructure of large passenger vehicles',67:'LPG equipment',73:'lateral protection of goods vehicles',77:'parking lamps',79:'steering equipment',
 83:'emissions of pollutants (light duty)',87:'daytime running lamps',89:'speed limitation devices',90:'replacement brake lining assemblies',91:'side-marker lamps',93:'front underrun protective devices',94:'protection of occupants in the event of a frontal collision',
 95:'protection of occupants in the event of a lateral collision',97:'vehicle alarm systems',98:'headlamps with gas-discharge light sources',99:'gas-discharge light sources',102:'close-coupling devices',104:'retro-reflective markings',105:'vehicles intended for the carriage of dangerous goods',
 107:'general construction of M2 and M3 vehicles',108:'retreaded tyres (passenger cars)',109:'retreaded tyres (commercial vehicles)',110:'CNG and LNG components',112:'headlamps emitting an asymmetrical passing beam',114:'airbag modules for replacement airbag systems',
 116:'protection of motor vehicles against unauthorized use',117:'tyres - rolling sound emissions, adhesion on wet surfaces, rolling resistance',118:'burning behaviour of materials used in the interior construction of certain categories of motor vehicles',119:'cornering lamps',
 121:'location and identification of hand controls, tell-tales and indicators',122:'heating systems of vehicles',123:'adaptive front-lighting systems',124:'wheels for passenger cars and their trailers',125:'forward field of vision of the motor vehicle driver',
 126:'partitioning systems protecting passengers against displaced luggage',127:'pedestrian safety performance',128:'light emitting diode (LED) light sources',130:'lane departure warning system',131:'advanced emergency braking systems',
 134:'safety-related performance of hydrogen-fuelled vehicles',135:'pole side impact performance',137:'frontal impact with focus on restraint system',139:'brake assist systems',140:'electronic stability control',141:'tyre pressure monitoring systems',142:'installation of tyres',
 154:'Worldwide harmonized Light vehicles Test Procedure (WLTP)',168:'real driving emissions (light duty)'}
for n,v in unr.items(): j('UN R%d'%n, v, KNOW+'; subject only', True, True, why="vehicle instrument whose title/scope does not concern the citing domain's subsystems (§1)")
j('UN GTR 15', 'Worldwide harmonized Light vehicles Test Procedure (WLTP)', KNOW+'; subject only', True, True, why="vehicle test procedure; does not concern domain-B subsystems")
# listed / added instruments (t3 passes in their own domain)
for n,v in {10:'electromagnetic compatibility',100:'electric power train',155:'cyber security',156:'software update'}.items(): j('UN R%d'%n, v, 'listed instrument', True, True, True, False)
for n,v in {14:'safety-belt anchorages',16:'safety-belts and restraint systems',17:'seats, their anchorages and head restraints',25:'head restraints',44:'child restraint systems',129:'enhanced child restraint systems'}.items(): j('UN R%d'%n, v, 'listed instrument', True, True, False, True)
for n,v in {'207':'Seating systems','208':'Occupant crash protection','209':'Seat belt assemblies','210':'Seat belt assembly anchorages','225':'Child restraint anchorage systems','202a':'Head restraints'}.items(): j('FMVSS '+n, v, 'listed instrument', True, True, False, True)
j('FMVSS 305','electric-powered vehicles: electrolyte spillage and electrical shock protection','listed instrument',True,True,True,False)
j('IEC 61851-1','Electric vehicle conductive charging system - Part 1: General requirements','listed instrument',True,True,True,False)
# additions
j('ISO 6469-1','Electrically propelled road vehicles - Safety specifications - Part 1: Rechargeable energy storage system (RESS)', KNOW+'; iso.org HTTP 403', True, True, True, False, why='scope names electrically propelled road vehicles; concerns the traction battery (RESS), a domain-B subsystem')
j('SAE J2929','Safety Standard for Electric and Hybrid Vehicle Propulsion Battery Systems Utilizing Lithium-based Rechargeable Cells', KNOW+'; sae.org challenge', True, True, True, False, why='scope names electric and hybrid vehicles; concerns the propulsion battery system, a domain-B subsystem')
j('UN R80','Uniform provisions concerning the approval of seats of large passenger vehicles and of these vehicles with regard to the strength of the seats and their anchorages', 'EUR-Lex OJ publication title (script)', True, True, False, True, why='scope names M2/M3 vehicles; concerns seats and their anchorages')
j('UN R145','Uniform provisions concerning the approval of vehicles with regard to ISOFIX anchorage systems, ISOFIX top tether anchorages and i-Size seating positions', 'EUR-Lex OJ publication title (script)', True, True, False, True, why='scope names vehicles; concerns child-restraint interfaces (ISOFIX) and seating positions')
j('UN R170','Uniform provisions concerning the approval of Child Restraint Systems for safer transport of children in buses and coaches', 'EUR-Lex OJ publication title (script)', True, True, False, True, why='scope names M2/M3 vehicles; concerns built-in child restraint systems in vehicle seats')
j('ISO 13216-1','Road vehicles - Anchorages in vehicles and attachments to anchorages for child restraint systems - Part 1: Seat bight anchorages and attachments', KNOW+'; iso.org HTTP 403', True, True, False, True, why='scope names road vehicles; concerns child-restraint interfaces')
j('ISO 17373','Road vehicles - Sled test procedure for evaluating occupant head and neck interactions with seat/head restraint designs in low-speed rear-end impact', KNOW+'; iso.org HTTP 403', True, True, False, True, why='scope names road vehicles; concerns seat and head-restraint designs')
j('FMVSS 202','Standard No. 202; Head restraints', 'eCFR section heading (applicability clause omitted)', True, True, False, True, why='applies to passenger cars and light vehicles; concerns head restraints')
j('FMVSS 213','Child restraint systems', 'eCFR section heading (applicability clause omitted)', True, True, False, True, why='applies to motor vehicles and child restraint systems for use in them; concerns child restraint systems')
j('FMVSS 213b','Standard No. 213b; Child restraint systems', 'eCFR section heading (applicability clause omitted)', True, True, False, True, why='as FMVSS 213')
j('SAE J826','Devices for Use in Defining and Measuring Vehicle Seating Accommodation', KNOW+'; sae.org challenge', True, True, False, True, why='scope names motor vehicles; concerns vehicle seating (H-point device for seats)')
j('SAE J800','Motor Vehicle Seat Belt Installation', KNOW+'; sae.org challenge', True, True, False, True, why='scope names motor vehicles; concerns seat-belt installation')

ADD_META = {
 'ISO 6469-1': dict(ident='ISO 6469-1', body='ISO (TC 22/SC 37)', jur='International (ISO)', landing='https://www.iso.org/search.html?q=ISO%206469-1', scope='not accessible ('+ISO_NOTE+')'),
 'SAE J2929': dict(ident='SAE J2929', body='SAE International', jur='International (SAE; primarily US/North America)', landing='https://www.sae.org/standards/content/j2929/', scope='not accessible ('+SAE_NOTE+')'),
 'UN R80': dict(ident='UN Regulation No. 80', body='UNECE WP.29 (1958 Agreement)', jur='UN-1958 Contracting Parties (incl. EU)', landing=UNECE_REG+'61-80',
   scope='"This Regulation applies to: (a) Passenger seats for forward-facing installation in vehicles of categories M2 and M3, of Classes II, III and B; (b) Vehicles of categories M2 and M3 of Classes II, III and B in respect of their passenger seat anchorages and seat installation. (c) It does not apply to rearward-facing seats or to any head restraint fitted to these seats." (1.1)'),
 'UN R145': dict(ident='UN Regulation No. 145', body='UNECE WP.29 (1958 Agreement)', jur='UN-1958 Contracting Parties (incl. EU)', landing=UNECE_REG+'141-160',
   scope='"This Regulation applies to: (a) Vehicles of category M1 with regard to their ISOFIX anchorage systems, their ISOFIX top tether anchorages and lower tether anchorages intended for child restraint systems. Other categories of vehicles fitted with ISOFIX anchorages and/or lower tether anchorages have also to comply with the provisions of this Regulation; (b) Vehicles of any category with regard to their i-Size seating positions, if any are defined by the vehicle manufacturer." (1)'),
 'UN R170': dict(ident='UN Regulation No. 170', body='UNECE WP.29 (1958 Agreement)', jur='UN-1958 Contracting Parties (incl. EU)', landing=UNECE_REG+'161-180',
   scope='"This Regulation applies to Built-in Child Restraint Systems installed in vehicles of categories M2 and M3 class B and class III with regards to the securing of children from 40 - 150 cm in forward facing and rearward facing vehicle seats. At the request of the manufacturer, this Regulation may also apply to any Built-in Child Restraint Systems installed in vehicles of categories M2 or M3 of classes I, II and A." (2)'),
 'ISO 13216-1': dict(ident='ISO 13216-1', body='ISO (TC 22/SC 36)', jur='International (ISO)', landing='https://www.iso.org/search.html?q=ISO%2013216-1', scope='not accessible ('+ISO_NOTE+')'),
 'ISO 17373': dict(ident='ISO 17373', body='ISO (TC 22/SC 36)', jur='International (ISO)', landing='https://www.iso.org/search.html?q=ISO%2017373', scope='not accessible ('+ISO_NOTE+')'),
 'FMVSS 202': dict(ident='FMVSS No. 202 (49 CFR 571.202)', body='NHTSA (US DOT)', jur='United States', landing=ECFR+'202', scope='"This standard specifies requirements for head restraints to reduce the frequency and severity of neck injury in rear-end and other collisions." (S1)'),
 'FMVSS 213': dict(ident='FMVSS No. 213 (49 CFR 571.213)', body='NHTSA (US DOT)', jur='United States', landing=ECFR+'213', scope='"This standard specifies requirements for child restraint systems used in motor vehicles and aircraft." (S1)'),
 'FMVSS 213b': dict(ident='FMVSS No. 213b (49 CFR 571.213b)', body='NHTSA (US DOT)', jur='United States', landing=ECFR+'213b', scope='"This standard specifies requirements for child restraint systems used in motor vehicles and aircraft." (S1)'),
 'SAE J826': dict(ident='SAE J826', body='SAE International', jur='International (SAE; primarily US/North America)', landing='https://www.sae.org/standards/content/j826/', scope='not accessible ('+SAE_NOTE+')'),
 'SAE J800': dict(ident='SAE J800', body='SAE International', jur='International (SAE; primarily US/North America)', landing='https://www.sae.org/standards/content/j800/', scope='not accessible ('+SAE_NOTE+')'),
}

# ---------------------------------------------------------------- S3 run
listed = [s['key'] for s in seeds]
# canonical aliases of listed seeds
ALIAS = {'Regulation (EU) 2023/1542':'EU 2023/1542','Regulation (EU) 2024/1257':'EU 2024/1257','Regulation (EU) 2019/2144':'EU 2019/2144','Regulation (EU) 2023/1804':'EU 2023/1804'}
def as_listed(c):
    c2 = ALIAS.get(c, c)
    return c2 if c2 in listed else None
additions = []; s3 = []
for sd in seeds:
    rec = dict(instrument=sd['key'], domain=sd['dom'], reference_source=sd['ref_src'], references=[])
    if not sd.get('refs'):
        rec['status'] = 'references not accessible'
        s3.append(rec); continue
    raw = json.load(open(OUT+'/'+sd['refs']))
    for k,v in sd.get('extra_refs',{}).items(): raw[k] = {'cited_in': {x:1 for x in v}}
    agg = {}
    for k,v in raw.items():
        locs = list(v['cited_in'].keys()) if isinstance(v,dict) else v
        ctx = v.get('title_ctx','') if isinstance(v,dict) else ''
        for c in canon(k):
            a = agg.setdefault(c, dict(as_cited=[], clauses=[], ctx=''))
            if k not in a['as_cited']: a['as_cited'].append(k)
            for l in locs:
                l = re.sub(r'\s+',' ',str(l)).strip() or 'annex (clause not resolved)'
                if l not in a['clauses']: a['clauses'].append(l)
            if ctx and not a['ctx']: a['ctx'] = re.sub(r' of \d{1,2} \w+ \d{4}','',ctx)[:200]
    for c,a in agg.items():
        if c in sd.get('self_ids',[]) or ALIAS.get(c)==sd['key']:
            rec['references'].append(dict(id=c, as_cited=a['as_cited'], clauses=a['clauses'][:8], outcome='self-citation (not counted)')); continue
        jj = J.get(c)
        if jj is None:
            print('NO JUDGEMENT', sd['key'], c, a['as_cited']); continue
        t3 = jj['t3B'] if sd['dom']=='B' else jj['t3S']
        t1 = jj['t1']; t2 = jj['t2'] if t1 else None; t3v = (t3 if t2 else None)
        lst = as_listed(c)
        if lst: outcome = 'already listed (%s)' % lst
        elif t1 and t2 and t3:
            outcome = 'ADDED'
            listed.append(c); additions.append(dict(key=c, dom=sd['dom'], via=sd['key'], clause=a['clauses'][0], tests=(t1,t2,t3), title=jj['title'], title_basis=jj['title_basis'], why=jj['why']))
        else: outcome = 'not added'
        rec['references'].append(dict(id=c, as_cited=a['as_cited'], clauses=a['clauses'][:8], title_or_subject=jj['title'], title_basis=jj['title_basis'],
            test1_instrument=t1, test2_vehicle_scope=t2, test3_domain=t3v, reason=jj['why'], outcome=outcome))
    refs = [r for r in rec['references'] if not r['outcome'].startswith('self')]
    rec['hit_counts'] = dict(references_read=len(refs), pass_test1=sum(1 for r in refs if r['test1_instrument']),
        pass_test1_2=sum(1 for r in refs if r['test1_instrument'] and r['test2_vehicle_scope']),
        pass_test1_2_3=sum(1 for r in refs if r['test1_instrument'] and r['test2_vehicle_scope'] and r['test3_domain']),
        added=sum(1 for r in refs if r['outcome']=='ADDED'), already_listed=sum(1 for r in refs if r['outcome'].startswith('already')),
        self_citations=len(rec['references'])-len(refs))
    rec['status'] = 'read'
    s3.append(rec)
print('additions:', [(a['key'],a['via']) for a in additions])

# ---------------------------------------------------------------- S1
def load_hits(fn):
    d = json.load(open(S+'/web/'+fn))['results']['bindings']; out = {}
    for b in d:
        c = b['celex']['value']; t = b.get('title',{}).get('value','')
        t = re.sub(r'\s+',' ',t.replace(' ',' '))
        t = re.sub(r' of \d{1,2} \w+ \d{4}','',t)            # adoption dates removed (rule 1)
        t = re.sub(r' \(OJ L[^)]*\)','',t); t = re.sub(r' \(Official Journal[^)]*\)','',t)
        out.setdefault(c, t)
    return out
LEGIS = 'legislative act of the European Parliament and Council: not adopted under the base act (base act\'s own history, left to the raters); title withheld from this record under rule 1'
S1DEC = {
 '32023R1542': {
   '32025R0606':('keep','delegated act supplementing the base act (2023/1542: any)'),
   '32025R2289':('keep','implementing act for the application of the base act (2023/1542: any)'),
   '32026R1770':('keep','delegated act supplementing the base act (2023/1542: any)'),
   '52025XC00214':('drop','Commission notice (guidelines), not a delegated or implementing act'),
   '52026DC0470':('drop','Commission report, not a delegated or implementing act'),
   '52026XC05531':('drop','Commission notice (guidelines), not a delegated or implementing act'),
   '32023R1542':('drop','the base act itself'),
   '32023R1542R(05)':('drop','corrigendum to the base act, not an act adopted under it'),'32023R1542R(11)':('drop','corrigendum to the base act, not an act adopted under it'),'32023R1542R(13)':('drop','corrigendum to the base act, not an act adopted under it'),
   '32024R1781':('drop',LEGIS),'32024R1781R(01)':('drop','corrigendum of a legislative act; '+LEGIS),'32024R1781R(02)':('drop','corrigendum of a legislative act; '+LEGIS),
   '32025R1561':('drop',LEGIS),'32026R1738':('drop',LEGIS),
   '32026D2048':('drop','implementing decision whose legal basis (first citation) is Regulation (EU) No 1025/2012 on standardisation, not the base act'),
 },
 '32024R1257': {
   '32025R1706':('drop','title concerns exhaust and evaporative emission type-approval, not battery durability, monitors or in-vehicle data'),
   '32025R1706R(01)':('drop','corrigendum'),
   '32025R1707':('keep','title names OBFCM devices, OBM systems (monitors) and EVP data and its communication (in-vehicle data)'),
   '32025R1707R(01)':('drop','corrigendum of a kept act (not a separate act)'),
   '32026R1214':('drop','title concerns brake particle emission testing'),
   '32026R1216':('drop','title concerns durability multipliers for gaseous pollutants of heavy-duty vehicles, not battery durability'),
   '32026R1762':('drop','title concerns brake particle emissions'),
   '32026R1764':('keep','title names in-vehicle battery durability; legal basis per metadata query is the base act'),
   '32024R1257':('drop','the base act itself'),
 },
 '32019R2144': {
   '32021R0535':('drop','title (general construction characteristics and safety) does not name seat-belt reminders, seating or occupant classification'),
   '32021R0646':('drop','title concerns emergency lane-keeping'),'32021R0646R(01)':('drop','corrigendum'),
   '32021R1243':('drop','title concerns alcohol interlock installation facilitation'),'32021R1341':('drop','title concerns driver drowsiness and attention warning'),
   '32021R1958':('drop','title concerns intelligent speed assistance'),'32022R0545':('drop','title concerns event data recorder'),
   '32022R1398':('drop','title does not name seat-belt reminders, seating or occupant classification (generic UN-regulation update)'),
   '32022R1426':('drop','title concerns automated driving systems'),'32023R1675':('drop','title concerns language corrections of an intelligent speed assistance act'),
   '32023R2590':('drop','title concerns advanced driver distraction warning'),'32024R0883':('drop','title concerns registration plate space and mass of energy storage systems'),
   '32024R1721':('drop','title concerns approval templates for ISA, DDAW, EDR, alcohol interlock and ADDW'),'32024R2220':('drop','title concerns heavy-duty event data recorder'),
   '32025R1122':('keep','JUDGEMENT: title names UN Regulation No 25 (head restraints, part of seating) among the UN Regulations it concerns'),
   '32026R0481':('drop','title concerns automated driving systems'),
   '52021IP0010':('drop','EP resolution, not a delegated or implementing act'),'52021IP0122':('drop','EP resolution'),'52021IP0407':('drop','EP resolution'),
   '52024DC0582':('drop','Commission report, not a delegated or implementing act'),
   '32019R2144':('drop','the base act itself'),'32019R2144R(03)':('drop','corrigendum to the base act'),
   '32024R1689':('drop',LEGIS),
 },
 '32023R1804': {
   '32025R0645':('drop','title concerns a common application programme interface (infrastructure side)'),
   '32025R0655':('drop','title concerns data on alternative fuels infrastructure'),
   '32025R0656':('keep','JUDGEMENT: title names vehicle-to-grid communication and supply for road transport vehicles (vehicle-side interface)'),
   '32025R0671':('drop','title concerns additional data types on alternative fuels infrastructure'),
   '52023IP0484':('drop','EP resolution'),'52024IP0025':('drop','EP resolution'),'52025DC0260':('drop','Commission communication'),'52025IP0344':('drop','EP resolution'),
   '32023R1804':('drop','the base act itself'),
 },
}
s1 = []
base_key = {'32023R1542':('EU 2023/1542','s1_1542.json','s1t_1542.json','2023/1542','any'),
            '32024R1257':('EU 2024/1257','s1_32024R1257.json','s1t_2024_1257.json','2024/1257','battery durability, monitors or in-vehicle data'),
            '32019R2144':('EU 2019/2144','s1_32019R2144.json','s1t_2019_2144.json','2019/2144','seat-belt reminders, seating or occupant classification'),
            '32023R1804':('EU 2023/1804','s1_32023R1804.json','s1t_2023_1804.json','2023/1804','vehicle-side obligations')}
for celex,(key,f1,f2,num,crit) in base_key.items():
    h1 = load_hits(f1); h2 = load_hits(f2); union = dict(h1); union.update({k:v for k,v in h2.items() if k not in union})
    acts = []
    for c in sorted(union):
        dec, why = S1DEC[celex][c]
        title = union[c] if 'title withheld' not in why else '[withheld under rule 1]'
        acts.append(dict(celex=c, in_query=('Q1' if c in h1 else '')+('+' if c in h1 and c in h2 else '')+('Q2' if c in h2 else ''), title=title, decision=dec, reason=why))
    s1.append(dict(base_act=key, base_celex=celex, keep_criterion=crit,
        queries=[dict(id='Q1', endpoint='https://publications.europa.eu/webapi/rdf/sparql', description='works whose cdm:resource_legal_based_on_resource_legal is the base act (EUR-Lex legal-basis metadata)', hits=len(h1)),
                 dict(id='Q2', endpoint='https://publications.europa.eu/webapi/rdf/sparql', description='sector-3 works (CELEX 3201*/3202*) whose English expression title contains "%s"' % num, hits=len(h2))],
        union_hits=len(union), kept=sum(1 for a in acts if a['decision']=='keep'), dropped=sum(1 for a in acts if a['decision']=='drop'), acts=acts))
for x in s1: print(x['base_act'], [q['hits'] for q in x['queries']], x['union_hits'], x['kept'], x['dropped'])

# ---------------------------------------------------------------- assemble instrument list
rows = []; cnt = {'B':0,'S':0}; idmap = {}
s3map = {r['instrument']: r for r in s3}
for sd in seeds:
    cnt[sd['dom']] += 1; iid = '%s%02d' % (sd['dom'], cnt[sd['dom']]); idmap[sd['key']] = iid
    r = s3map[sd['key']]
    rows.append(dict(instrument_id=iid, key=sd['key'], domain=sd['dom'], identifier=sd['ident'], title=sd['title'], issuing_body=sd['body'], jurisdiction=sd['jur'],
        landing_url=sd['landing'], scope=sd['scope'], origin='seed', references_status=('read %d' % r['hit_counts']['references_read']) if r['status']=='read' else 'not accessible',
        reference_source=sd['ref_src'], note=sd.get('note') or ''))
for a in additions:
    cnt[a['dom']] += 1; iid = '%s%02d' % (a['dom'], cnt[a['dom']]); idmap[a['key']] = iid
    m = ADD_META[a['key']]
    rows.append(dict(instrument_id=iid, key=a['key'], domain=a['dom'], identifier=m['ident'], title=a['title'], issuing_body=m['body'], jurisdiction=m['jur'],
        landing_url=m['landing'], scope=m['scope'], origin='added via %s clause %s' % (idmap[a['via']], a['clause']), references_status='not screened (S3 is one level only)',
        reference_source='', note='title basis: '+a['title_basis']))
for a in additions: a['via_id'] = idmap[a['via']]; a['id'] = idmap[a['key']]

fetchlog = []
with open(OUT+'/fetchlog.tsv') as f:
    for line in f:
        p = line.rstrip('\n').split('\t')
        if len(p) >= 4:
            if p[2].startswith('SPARQL'): fetchlog.append(dict(time=p[0], saved_as=p[1], request=p[2], bytes=p[3]))
            else: fetchlog.append(dict(time=p[0], saved_as=p[1], url=p[2], http_status=p[3], bytes=p[4] if len(p)>4 else ''))
webtools = [
 dict(tool='WebFetch', url='https://www.iso.org/standard/77845.html', result='HTTP 403; nothing read'),
 dict(tool='WebFetch', url='https://www.sae.org/standards/content/j1772/', result='challenge page; nothing read'),
 dict(tool='WebFetch', url='https://standardsworks.sae.org/standards-committees/hybrid-ev-committee', result='not loaded; nothing read'),
 dict(tool='WebSearch', query='ISO 15118-20 Road vehicles Vehicle to grid communication interface network and application protocol requirements (allowed_domains iso.org)', result='10 result links; used for ISO 15118-2/-20/-8 titles and landing URLs. CONTAMINATION: the result list and the tool\'s summary included titles of amendment/related documents; not used for any decision'),
 dict(tool='WebSearch', query='SAE J2847 communication plug-in vehicles part titles J2847/1 J2847/2 J2847/3 J2847/5 J2847/6 (allowed_domains sae.org)', result='9 result links + tool summary; used for J2847 part titles. CONTAMINATION: the tool summary listed revision identifiers/dates; not used for any decision and not carried into outputs'),
 dict(tool='WebSearch', query='SAE J2931/1 J2931/4 J2931/6 J2931/7 plug-in electric vehicle communications titles (allowed_domains sae.org)', result='9 result links + summary; used for J2931 part titles. CONTAMINATION: summary listed revision identifiers/dates; not carried into outputs'),
 dict(tool='WebSearch', query='"J2931/2" OR "J2931/3" OR "J2931/5" SAE plug-in electric vehicles (allowed_domains sae.org)', result='no publisher listing found for /2, /3, /5 (summary described /2 and /3 only as proposed parts); those parts not listed'),
]

s0 = dict(seed_rows=[s['key'] for s in seeds if not s['key'].startswith('SAE J2847') and not s['key'].startswith('SAE J2931')],
  series_expansion=[
   dict(series='SAE J2847', part='J2847/1', title='Communication for Smart Charging of Plug-in Electric Vehicles Using Smart Energy Profile 2.0', decision='keep', reason='communication with the grid side (smart charging)'),
   dict(series='SAE J2847', part='J2847/2', title='Communication Between Plug-in Vehicles and Off-Board DC Chargers', decision='keep', reason='communication between vehicle and charger'),
   dict(series='SAE J2847', part='J2847/3', title='Communication for Plug-in Vehicles as a Distributed Energy Source', decision='keep', reason='vehicle as a grid-side energy source (bidirectional)'),
   dict(series='SAE J2847', part='J2847/5', title='Communication Between Plug-In Vehicles and Customers', decision='drop', reason='names customers, not the charging or grid side'),
   dict(series='SAE J2847', part='J2847/6', title='Communication for Wireless Power Transfer Between Light-Duty Plug-in Electric Vehicles and Wireless EV Charging Stations', decision='keep', reason='communication between vehicle and charging station'),
   dict(series='SAE J2931', part='J2931/1', title='Digital Communications for Plug-in Electric Vehicles', decision='keep (judgement)', reason='plug-in EV communications read as charging-interface communication'),
   dict(series='SAE J2931', part='J2931/4', title='Broadband PLC Communication for Plug-in Electric Vehicles', decision='keep (judgement)', reason='power-line communication of plug-in EVs read as charging-interface communication'),
   dict(series='SAE J2931', part='J2931/6', title='Signaling Communication for Wirelessly Charged Electric Vehicles', decision='keep (judgement)', reason='signalling for wireless charging read as vehicle-to-charger communication'),
   dict(series='SAE J2931', part='J2931/7', title='Security for Plug-In Electric Vehicle Communications', decision='keep (judgement)', reason='security of plug-in EV communications read as charging/grid-side communication'),
   dict(series='SAE J2931', part='J2931/2, /3, /5', title='(not found as published documents in any listing the screener could reach)', decision='not listed', reason='no publisher title could be verified; recorded as a deviation'),
  ],
  enumeration_source='SAE web-search result listings (sae.org / saemobilus.sae.org titles); sae.org itself could not be fetched')

deviations = [
 'D1 (S1 method): EUR-Lex HTML expert search returned no parseable results to a script; S1 used the Publications Office SPARQL endpoint behind EUR-Lex, two queries per base act (Q1 legal-basis metadata; Q2 title contains the base-act number), union taken. Q1 metadata is visibly incomplete (it missed acts found by Q2), so Q2 was added.',
 'D2 (UN regulation texts): unece.org returned HTTP 403 (Cloudflare) for all pages and PDFs. UN regulation texts were taken from their EUR-Lex OJ publications; for each, a script picked the most recent base text from the metadata list and printed only its CELEX and title. The landing URL recorded is the UNECE addenda page (not fetchable by the screener). GTR 22 was read from the UN ODS copy of ECE/TRANS/180/Add.22.',
 'D3 (references not accessible): ISO (iso.org, HTTP 403), SAE (AWS-WAF challenge), IEC previews (HTTP 403 from the preview endpoint) and GB full texts (image viewer behind a verification step) could not be read. No bypass was attempted (one attempt to fetch the openstd download endpoint directly was refused by the session permission system and was not repeated). All those instruments are logged "references not accessible" and add nothing. %d of %d domain-B seeds and %d of %d domain-S seeds are affected, which makes the S3 additions asymmetric toward instruments with free text (UN, EU, FMVSS).' % (sum(1 for r in s3 if r['status']!='read' and r['domain']=='B'), sum(1 for x in seeds if x['dom']=='B'), sum(1 for r in s3 if r['status']!='read' and r['domain']=='S'), sum(1 for x in seeds if x['dom']=='S')),
 'D4 (scope not accessible): no scope statement could be read for the GB, ISO and SAE instruments; S2 is incomplete for them (title only). Titles of ISO 17409, SAE J1772, J3400, IEC 61851-23/-24 and of the added ISO/SAE documents are the screener\'s knowledge, flagged NOT VERIFIED. ISO 15118 and SAE J2847/J2931 titles come from web-search result listings of the publishers\' pages.',
 'D5 (blind-reading breaches, disclosed): (a) the openstd list page for GB 38031 displayed edition rows before the script was narrowed; (b) the IEC 61851-1 abstract printout included the first words of its edition statement before the script was fixed to cut there; (c) three WebSearch summaries named amendment/revision identifiers or dates of ISO 15118-20 and SAE J2847/J2931 parts; (d) the first-page printout for UN R170 included its "Incorporating" line; (e) the S1 titles of amending acts necessarily describe what they amend (protocol S1 requires titles). None of this changed any inclusion decision: additions are decided only by the S3 tests on cited references. Nothing from (a)-(d) is carried into the outputs.',
 'D6 (test 1, EN standards): EN standards cited by AFIR (EN 62196-2/-3, EN 61851-23-1, etc.) and EN 50436 (GSR2) fail test 1 because EN is not in the closed §2 list; no IEC/ISO parent was substituted.',
 'D7 (test 3 reading): test 3 was read as "the title or scope concerns a subsystem or function that §1 lists for the citing domain" (traction battery/RESS, charging and charge communication, DC-DC, HV energy data; seats, belts, head restraints, occupant classification, child-restraint interfaces). This matches how the seed list itself was built (it already contains hardware-safety instruments such as GB 38031, FMVSS 305, UN R14, FMVSS 207). General EMC, functional-safety, crash-test, instrumentation and material standards fail test 3.',
 'D8 (whole-text references for partial seeds): for seeds named for a subset of provisions (Euro 7 battery durability, UN R10 charging mode, AFIR vehicle side, GSR2 seating), references were taken from the whole act; test 3 confines additions to the domain.',
 'D9 (FMVSS 305 / 305a): listed as two instruments (two CFR sections). Section headings of FMVSS 305, 305a, 202a, 202, 213, 213b carry applicability dates; those clauses are omitted from the recorded titles under rule 1.',
 'D10 (J2931 judgement and missing parts): see s0.series_expansion. J2931 part titles do not literally name the charger or grid; they were kept as a judgement. Parts /2, /3, /5 were not listed because no published title could be verified.',
 'D11 (S1 judgements): 32025R1122 (GSR2, names UN R25) and 32025R0656 (AFIR, names vehicle-to-grid communication) were kept as title judgements; 32026D2048 was dropped after reading only its citation line (legal basis Regulation 1025/2012).',
]
record = dict(study='L1', stage='screen (stage 1)', screener='fresh-context sub-agent (not a rater)', user_agent=UA, timeout_s=60,
  protocol='results/L1/L1_preregistration.md §2-§3', instrument_count=dict(B_seed=sum(1 for s in seeds if s['dom']=='B'), S_seed=sum(1 for s in seeds if s['dom']=='S'),
     B_added=sum(1 for a in additions if a['dom']=='B'), S_added=sum(1 for a in additions if a['dom']=='S')),
  S0=s0, S1=s1, S2_S3_instruments=rows, S3=s3,
  addition_log=[dict(added=a['id'], identifier=a['key'], domain=a['dom'], cited_by=a['via_id']+' '+a['via'], clause=a['clause'], test1=a['tests'][0], test2=a['tests'][1], test3=a['tests'][2], title=a['title'], title_basis=a['title_basis'], judged_on=a['why']) for a in additions],
  references_not_accessible=[dict(instrument=idmap[r['instrument']]+' '+r['instrument'], reason=r['reference_source']) for r in s3 if r['status']!='read'],
  fetch_log=fetchlog, web_tools=webtools, deviations=deviations)
json.dump(record, open(OUT+'/L1_screen.json','w'), indent=1, ensure_ascii=False)
print(record['instrument_count'])

# ---------------------------------------------------------------- Markdown
def esc(x): return str(x).replace('|','\\|').replace('\n',' ')
L = []
L.append('# L1 instrument list (fixed before reading any change history)\n')
L.append('Built by the L1 screener (a fresh-context sub-agent, not a rater) under `L1_preregistration.md` §3. Raw record: `L1_screen.json`.\n')
L.append('- Instruments: domain B %d (seed %d, added %d); domain S %d (seed %d, added %d).' % (record['instrument_count']['B_seed']+record['instrument_count']['B_added'], record['instrument_count']['B_seed'], record['instrument_count']['B_added'], record['instrument_count']['S_seed']+record['instrument_count']['S_added'], record['instrument_count']['S_seed'], record['instrument_count']['S_added']))
L.append('- Identifiers carry no edition year: the instrument is the document across its editions, amendments and revisions in the window.')
L.append('- Titles of EU acts omit the adoption date; FMVSS section headings omit their applicability clause. Nothing in this file states an amendment date or what any amendment changed, except where an S1 act title itself says what it amends (protocol S1 requires titles).')
L.append('- "Not accessible" means the screener could not read the text without bypassing a bot check; see Deviations.\n')
L.append('## 1. Instruments\n')
L.append('| instrument_id | domain | identifier | exact title | issuing body | jurisdiction | landing URL | scope (≤ 3 sentences, quoted) | origin | references |')
L.append('|---|---|---|---|---|---|---|---|---|---|')
for r in rows:
    title = r['title'] + (' *(%s)*' % r['note'] if r['note'] else '')
    L.append('| %s |' % ' | '.join(esc(x) for x in [r['instrument_id'], r['domain'], r['identifier'], title, r['issuing_body'], r['jurisdiction'], r['landing_url'], r['scope'], r['origin'], r['references_status']]))
L.append('\n## 2. S1: acts adopted under each EU base act (candidate events, not instruments)\n')
L.append('Kept acts are candidate events of their base act. Title and identifier only (adoption dates removed).\n')
for x in s1:
    L.append('### %s %s (keep if title concerns: %s)\n' % (idmap[x['base_act']], x['base_act'], x['keep_criterion']))
    kept = [a for a in x['acts'] if a['decision']=='keep']
    if kept:
        for a in kept: L.append('- **CELEX %s**: %s *(%s)*' % (a['celex'], a['title'], a['reason']))
    else: L.append('- none kept')
    L.append('')
L.append('## 3. S3 hit counts per instrument\n')
L.append('Counts are sequential: test 2 is applied only to references passing test 1, test 3 only to those passing tests 1 and 2. Self-citations are not counted.\n')
L.append('| instrument_id | identifier | status | references read | pass test 1 | pass tests 1-2 | pass tests 1-3 | added | already listed |')
L.append('|---|---|---|---|---|---|---|---|---|')
for r in s3:
    h = r.get('hit_counts')
    if h: L.append('| %s | %s | read | %d | %d | %d | %d | %d | %d |' % (idmap[r['instrument']], r['instrument'], h['references_read'], h['pass_test1'], h['pass_test1_2'], h['pass_test1_2_3'], h['added'], h['already_listed']))
    else: L.append('| %s | %s | references not accessible | – | – | – | – | – | – |' % (idmap[r['instrument']], r['instrument']))
tot = [sum(r['hit_counts'][k] for r in s3 if r.get('hit_counts')) for k in ['references_read','pass_test1','pass_test1_2','pass_test1_2_3','added','already_listed']]
L.append('| **total** | | | %d | %d | %d | %d | %d | %d |' % tuple(tot))
L.append('\n## 4. Addition log\n')
L.append('| added | identifier | domain | cited by | clause | test 1 (instrument) | test 2 (vehicle scope) | test 3 (domain) | title judged on | title basis | reason |')
L.append('|---|---|---|---|---|---|---|---|---|---|---|')
for a in record['addition_log']:
    L.append('| %s |' % ' | '.join(esc(x) for x in [a['added'], a['identifier'], a['domain'], a['cited_by'], a['clause'], 'pass', 'pass', 'pass', a['title'], a['title_basis'], a['judged_on']]))
L.append('\nReferences of added instruments were not screened (one level only).\n')
L.append('## 5. S1 query log\n')
L.append('Endpoint: `https://publications.europa.eu/webapi/rdf/sparql` (the Publications Office metadata store behind EUR-Lex). Q1: acts whose legal-basis metadata is the base act. Q2: sector-3 acts whose English title contains the base-act number. Union taken.\n')
L.append('| base act | Q1 hits | Q2 hits | union | kept | dropped |')
L.append('|---|---|---|---|---|---|')
for x in s1: L.append('| %s %s | %d | %d | %d | %d | %d |' % (idmap[x['base_act']], x['base_act'], x['queries'][0]['hits'], x['queries'][1]['hits'], x['union_hits'], x['kept'], x['dropped']))
L.append('\nDropped acts (identifier, query, reason; the full titles are in `L1_screen.json`, except legislative amending acts, whose titles are withheld):\n')
for x in s1:
    for a in x['acts']:
        if a['decision']=='drop': L.append('- %s: CELEX %s (%s): %s' % (x['base_act'], a['celex'], a['in_query'], a['reason']))
L.append('\n## 6. S0 series expansion (by title)\n')
for e in s0['series_expansion']: L.append('- %s %s, "%s": **%s** (%s)' % (e['series'], e['part'], e['title'], e['decision'], e['reason']))
L.append('\n## 7. References not accessible\n')
for x in record['references_not_accessible']: L.append('- %s: %s' % (x['instrument'], x['reason']))
L.append('\n## 8. Deviations from the protocol\n')
for d in deviations: L.append('- '+d)
open(OUT+'/L1_instruments.md','w').write('\n'.join(L)+'\n')
print('written', len(L))
