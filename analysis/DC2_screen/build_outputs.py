"""build_outputs.py OUTDIR : write DC2_screen.json and DC2_instruments.md from the screener's decisions (no web content is read here
except the fetch log, which holds only URLs and statuses)."""
import json, sys, os
OUT = sys.argv[1]

def I(id_, group, ident, title, body, juris, url, scope, heads, access, status, origin, refs):
    return dict(instrument_id=id_, group=group, identifier=ident, title=title, issuing_body=body, jurisdiction=juris,
                landing_url=url, scope=scope, headings=heads, access=access, status=status, origin=origin, references=refs)

E = "https://www.ercot.com"
inst = [
# ---------------- G ----------------
I("G01","G","ERCOT Planning Guide (current; Section 9 dated July 11, 2026)","ERCOT Planning Guide","ERCOT","US-TX (ERCOT)",
  E+"/mktrules/guides/planning/current",
  "“This Section defines the requirements and processes used to facilitate new or modified Large Load interconnections with the ERCOT System.” (Section 9.1(1))",
  "9 Large Load Interconnection or Modification; 9.2.4 Load Commissioning Plan; 9.2.5 Required Interconnection Equipment; 9.3.2 Batch Zero Interconnection Study Methodology; 9.6 Initial Energization and Continuing Operations for Large Loads; 9.6.1 Additional Energization and Operation Requirements for PCLRs; 9.6.2 … for WLPUNs; 9.8.4.3 Legacy Dynamic and Transient Stability Analysis",
  "full","in force (incorporates approved PGRR115, PGRR145)","seed","read 34 (Section 9 keyword-headed clauses); 0 pass"),
I("G02","G","ERCOT Nodal Protocols (current; Section 1 dated Nov 6, 2026)","ERCOT Nodal Protocols","ERCOT","US-TX (ERCOT)",
  E+"/mktrules/nprotocols/current",
  "“[The ERCOT Protocols] means the document adopted by ERCOT … that contains the scheduling, operating, planning, reliability, and Settlement (including Customer registration) policies, rules, guidelines, procedures, standards, and criteria of ERCOT.” (Section 1.1(1))",
  "3.2.7 Large Load Interconnection Status Report; 3.7.1.2 Load Resource Parameters; 3.22.1.4 Large Load Interconnection Assessment; 6.5.7.11 Provisional Controllable Load Resource (PCLR) Ramp Rate Requirements (gray-boxed pending system implementation per NPRR1325); 6.6.5.3 / 6.6.5.3.1 Controllable Load Resource Set Point Deviation Charges",
  "full","in force (incorporates approved NPRR1234, NPRR1267, NPRR1308, NPRR1325; some NPRR1325 sections pending system implementation, as printed)","seed","read 13 (Sections 3 and 6 keyword-headed clauses); 0 pass"),
I("G03","G","ERCOT Nodal Operating Guide (current; Section 2 dated Nov 1, 2026)","ERCOT Nodal Operating Guides","ERCOT","US-TX (ERCOT)",
  E+"/mktrules/guides/noperating/current",
  "“These ERCOT Operating Guides supplement the Protocols. The Operating Guides provide more detail and establish additional operating requirements for those organizations and Entities operating in, or potentially impacting the reliability of the ERCOT Transmission Grid in the ERCOT Region. … Organizations and Entities are obligated to comply with the Operating Guides.” (Section 1.1)",
  "2.6.4 Frequency Ride-Through Requirements for Large Computational Loads; 2.15 Voltage Ride-Through Requirements for Large Computational Loads",
  "full","in force (incorporates NOGRR282, effective 08/01/2026)","seed","read 7 (Section 2 keyword-headed clauses); 0 pass"),
I("G04","G","PGRR144","Dynamic Model Submission and Review Requirements for Large Loads including Large Computational Loads","ERCOT","US-TX (ERCOT)",
  E+"/mktrules/issues/PGRR144",
  "Planning Guide Sections Requiring Revision (as printed): “6.2, Dynamics Model Development; 9.2.1, Applicability of the Batch Zero Study Process; 9.2.1.5, Review of Existing Large Computational Load Modifications Potentially Impacting Ride Through Performance (new); 9.6, Initial Energization and Continuing Operations for Large Loads”",
  "",
  "full","approved 11/05/2026 (PUCT); Effective Date December 1, 2026 (as printed) — not yet in the Planning Guide","seed (ERCOT ‘any 2025–2026 large-load protocol revision’)","read 35 (whole report); 0 pass"),
I("G05","G","NERC Reliability Guideline (May 2026)","Risk Mitigation for Emerging Large Loads — Large Loads Working Group Reliability Guideline","NERC","North America",
  "https://www.nerc.com/globalassets/our-work/guidelines/reliability/RG_Risk-Mitigation-For-Emerging-Large-Loads.pdf",
  "“This reliability guideline shares initial recommended practices, technical insights, and lessons learned for maintaining BPS reliability while integrating emerging large loads. This guideline will suggest mitigations for risks discussed in the prior LLWG white papers.” (Purpose)",
  "Ch. 4 Operations and Balancing (Real-Time Monitoring; Balancing and Reserves); Ch. 5 Stability (Voltage and Frequency Disturbance Performance; Oscillation Mitigation); Ch. 6 Power Quality (Harmonics; Power Quality Monitoring and Analysis); Appendix A High-Level Recommendations",
  "full","published May 2026","seed","read 6 (Ch. 4–6, chapter-scoped); 0 pass"),
I("G06","G","NERC Alert — Industry Recommendation (Level 2), initial distribution Sep 9, 2025","Large Load Interconnection, Study, Commissioning, and Operations","NERC","North America",
  "https://www.nerc.com/pa/rrm/bpsa/Alerts%20DL/NERC%20Alert%20Level%202%20%20Large%20Loads.pdf",
  "“The purpose of this alert is to address the risks observed from the analyzed large load behavior and to assess the status of industry preparedness in relation to large loads.”",
  "", "full","issued Sep 9, 2025","seed","read 4 (whole document); 0 pass"),
I("G07","G","NERC CLO-001-1, Draft 1 (Project 2026-02), Aug 2026","Computational Load Interconnection, Studies, & Modeling Data","NERC","North America",
  "https://www.nerc.com/globalassets/standards/projects/2026-02/formal-posting-1/formal-posting-1/project-2026-02-clo-001-1-draft-1-clean.pdf",
  "“To establish interconnection requirements for Computational Load Sites, to study the impact of interconnecting new or changed Computational Load Sites, and to establish modeling data requirements, verification, and reporting procedures for development of planning horizon cases necessary to support analysis of the reliability of the interconnected transmission system.” (Purpose; Facilities: Computational Load Sites ≥ 50 MW total connected Load, as printed)",
  "", "full","pending (as printed: Draft 1, formal comment period Aug 19–Sep 18, 2026; Board adoption not yet)","seed (NERC ‘any large-load standards project’)","read 29 (whole document); 0 pass"),
I("G08","G","NERC CLO-002-1, Draft 1 (Project 2026-02), Aug 2026","Computational Load Operational Data and Communications","NERC","North America",
  "https://www.nerc.com/globalassets/standards/projects/2026-02/formal-posting-1/formal-posting-1/project-2026-02-clo-002-1-draft-1-clean.pdf",
  "“To ensure that each Transmission Operator, Balancing Authority, and Reliability Coordinator has the Computational Load Site data and information it needs to plan, monitor, and assess the reliable operation of the bulk power system; and to establish Interpersonal Communication capabilities at Computational Load Sites …” (Purpose)",
  "", "full","pending (as printed: Draft 1)","seed (NERC ‘any large-load standards project’)","read 24 (whole document); 0 pass"),
I("G09","G","NERC CLO-003-1, Draft 1 (Project 2026-02), Aug 2026","Computational Load Protection Coordination & Disturbance Monitoring","NERC","North America",
  "https://www.nerc.com/globalassets/standards/projects/2026-02/formal-posting-1/formal-posting-1/project-2026-02-clo-003-1-draft-1-clean.pdf",
  "“To maintain the coordination of Protection Systems at Computational Load Sites and to have adequate data available from Computational Load Sites to facilitate analysis of System Disturbances.” (Purpose)",
  "", "full","pending (as printed: Draft 1)","seed (NERC ‘any large-load standards project’)","read 20 (whole document); 0 pass (IEEE C37.111 cited for file naming only)"),
I("G10","G","PJM Board Decisional Letter, Jan 16, 2026","Board Decisional Letter on Critical Issue Fast Path - Large Load Additions","PJM Interconnection (Board of Managers)","US (PJM)",
  "https://www.pjm.com/-/media/DotCom/about-pjm/who-we-are/public-disclosures/2026/20260116-pjm-board-letter-re-results-of-the-cifp-process-large-load-additions.pdf",
  "“After significant deliberation, the Board is issuing this decisional letter that reflects components of the various presentations.”",
  "", "full","issued Jan 16, 2026","seed","read 0 (no citing sentence naming another document); 0 pass"),
I("G11","G","PJM draft M14B Attachment D-2 and tariff (Sept 1, 2026 draft)","PJM Draft of Ride Through Tariff and Manual Revisions for Large Computational Loads","PJM Interconnection","US (PJM)",
  "https://www.pjm.com/-/media/DotCom/committees-groups/committees/pc/2026/20260908/20260908-item-05---2-large-load-ride-through---redline.pdf",
  "“Large Computational Loads (“LCLs”), including data centers and other computational facilities whose demand is substantially supplied through power electronic conversion equipment, connected at ≥ 100 kV and that aggregate to ≥ 50 MW, may significantly influence Bulk Electric System (BES) voltage performance and dynamic behavior during …” (D-2.1 Purpose)",
  "", "full","pending (as printed: “September 1, 2026 Draft / Remains Under Development and Subject to Revision by PJM”)","seed (PJM large-load documents 2025–2026)","read 2 (whole document); 0 pass"),
I("G12","G","16 TAC §25.194 (PUCT Project No. 58481)","Large Load Interconnection Standards","Public Utility Commission of Texas","US-TX",
  "https://ftp.puc.texas.gov/public/puct-info/agency/rulesnlaws/subrules/electric/25.194/25.194.pdf",
  "“(a) Purpose and Scope. This section sets forth the standards and criteria for an electric utility, a municipally owned utility, and electric cooperative to interconnect a large load customer to the ERCOT system.”",
  "(a) Purpose and Scope; (b) Applicability; (d) Intermediate agreement; (e) Interconnection study; (f) SLLIA; (h) Batch zero load",
  "full","in force (adopted rule, current PDF)","seed","read 36 (whole rule); 0 pass"),
I("G13","G","16 TAC §25.205 (PUCT Project No. 58479)","Net Metering Arrangements Involving a Large Load Customer Co-Located with an Existing Generation Resource","Public Utility Commission of Texas","US-TX",
  "https://ftp.puc.texas.gov/public/puct-info/agency/rulesnlaws/subrules/electric/25.205/25.205.pdf",
  "“(a) Applicability. This section applies to a net metering arrangement involving a large load customer and an existing generation resource in the ERCOT region.”",
  "(h) General requirements of ERCOT study; (k) Commission decision; (m) Periodic evaluation of conditions imposed",
  "full","in force","seed","read 24 (whole rule); 0 pass"),
I("G14","G","16 TAC §25.370","ERCOT Large Load Forecasting Criteria","Public Utility Commission of Texas","US-TX",
  "https://ftp.puc.texas.gov/public/puct-info/agency/rulesnlaws/subrules/electric/25.370/25.370.pdf",
  "“(a) Purpose. The purpose of this section is to establish criteria for including the load of a large load customer in ERCOT’s load forecasts used for identifying transmission planning needs and performing resource adequacy assessments.”",
  "", "full","in force","seed","read 11 (whole rule); 0 pass"),
I("G15","G","PUCT Project No. 59999, Item 5 (filed Nov 5, 2026)","ERCOT Standard Large Load Interconnection Agreement (proposed SLLIA, staff recommendation)","Public Utility Commission of Texas","US-TX",
  "https://interchange.puc.texas.gov/search/filings/?UtilityType=A&ControlNumber=59999&ItemMatch=Equal&DocumentType=ALL&SortOrder=Ascending",
  "Case style (as printed): “Rulemaking to Adopt a Standard Large Load Interconnection Agreement”. No scope sentence read.",
  "Article 7 Facilities and Equipment; Article 8 Operation and Maintenance; Article 9 Performance Obligation and Cost Responsibility",
  "full","pending (as printed: “Proposal Notice of Draft Standardized Large Load Interconnection Agreement (SLLIA)”; Texas Register issue of 11.20.2026)","seed (PUCT SB 6 rules)","read 10 (keyword-headed clauses); 0 pass"),
I("G16","G","193 FERC ¶ 61,217 (Docket No. EL25-49-000 et al.), issued Dec 18, 2025","Order on Show Cause Proceeding, Directing Compliance Filings, Establishing Paper Hearing, and Granting in Part and Denying in Part Complaint (PJM Interconnection, L.L.C.)","Federal Energy Regulatory Commission","US (PJM)",
  "https://www.ferc.gov/sites/default/files/2025-12/E-1%20EL25-49-000.pdf",
  "“The Show Cause Order directed PJM and the transmission owners to either: (1) show cause as to why the [Tariff] remains just and reasonable … without provisions addressing with sufficient clarity or consistency the rates, terms, and conditions of service that apply to Co-Location Arrangements; or (2) explain what changes to the Tariff would remedy the identified concerns …”",
  "", "full","issued Dec 18, 2025 (later orders in the docket exist, e.g. EL25-49-002)","seed","read 0 (no clause heading names a keyword); 0 pass"),
# ---------------- U ----------------
I("U01","U","Ohio Power Company (AEP Ohio) Schedule DCT, issued Aug 28, 2026 (Case Nos. 25-392-EL-AIR, 26-113-EL-ATA)","Schedule DCT (Data Center Tariff)","AEP Ohio (Ohio Power Company); approved by PUCO","US-OH",
  "https://www.aepohio.com/company/about/rates/data-center-tariff",
  "“Service pursuant to this schedule is available for general service to customers that operate a Data Center (both Existing Load and New Load) that will use, within the initial contract term, a monthly maximum demand of greater than 25,000 kW at a Single Location or an aggregated Total Customer Contract Capacity in Service Territory of greater than 25,000 kW as described below.” (Availability of Service)",
  "Availability of Service; Monthly Rate; Minimum Charges; Customer-Owned Generation and Emergency Conditions; Special Terms and Conditions (Schedule DCT inside the November 2026 Ohio Power Tariff Book)",
  "full","in force (effective Aug 28, 2026)","seed","read 14 (whole schedule); 0 pass"),
I("U02","U","Virginia SCC Final Order, Case No. PUR-2025-00058 (Nov 25, 2025) — Rate Schedule GS-5 (large-load class)","Final Order: Application of Virginia Electric and Power Company for a 2025 biennial review of the rates, terms and conditions …","Virginia State Corporation Commission / Dominion Energy Virginia","US-VA",
  "https://www.scc.virginia.gov/docketsearch/DOCS/89g601!.PDF",
  "“This proceeding is a biennial review of Virginia Electric and Power Company’s (“Dominion” or “Company”) rates, terms, and conditions for the provision of generation, distribution, and transmission services pursuant to § 56-585.1 A of the Code of Virginia (“Code”). … Dominion also proposed certain changes to its rate schedules and its terms and conditions of service.”",
  "", "partial","approved; the GS-5 rate schedule text was not found on dominionenergy.com’s Virginia tariff pages (two direct URLs 404; not in the tariff table of contents)","seed","read 0 (no keyword-headed clause in the order); 0 pass"),
I("U03","U","Georgia Power Company Rules, Regulations and Rate Schedules for Electric Service (current PDF)","Rules and Regulations for Electric Service (Rules, Regulations and Rate Schedules for Retail Electric Service)","Georgia Power Company; approved by Georgia PSC","US-GA",
  "https://www.georgiapower.com/content/dam/georgia-power/pdfs/tariffs/rules-regs.pdf",
  "“All rules, regulations, and rate schedules are subject to change by the Georgia Public Service Commission in the manner prescribed by law.” (cover page)",
  "A. General Rules; B. Credit Regulations; C./D. Line Extension and Service Connection Regulations; E. Metering and Billing; F. Contract and Enforcement Regulations; G. Customer Generation",
  "full","in force","seed","read 9 (whole document); 0 pass (IEEE 1547-2018 cited for customer generation only)"),
# ---------------- E ----------------
I("E01","E","Commission Regulation (EU) 2016/1388","Network Code on Demand Connection","European Commission","EU",
  "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32016R1388",
  "“1. This Regulation establishes a network code which lays down the requirements for grid connection of: (a) transmission-connected demand facilities; (b) transmission-connected distribution facilities; (c) distribution systems, including closed distribution systems; (d) demand units, used by a demand facility or a closed distribution system to provide demand response services to relevant system operators and relevant TSOs.” (Art. 1)",
  "Art. 12 General frequency requirements; Art. 13 General voltage requirements; Art. 17 Control requirements; Art. 19 Demand disconnection and demand reconnection; Art. 20 Power quality; Art. 28–30 Demand response provisions; Annex I–II",
  "full","in force (EUR-Lex: ‘In force’, no end date)","seed","read 0 (Art. 20 contains no citing sentence); 0 pass"),
I("E02","E","ENTSO-E Implementation Guidance Documents (connection network codes), current versions whose Code(s) field names the DCC — 14 documents","Implementation Guidance Documents (CNC IGDs): Compliance Verification – Simulation models (2023); Compliance Verification – Compliance Testing and use of Equipment Certificates (2021); Demand Response – System Frequency Control (2021); Frequency Ranges (2021); Harmonisation; HPoPEIPS; Instrumentation, simulation models and protection; Making non-mandatory requirements mandatory; Parameters of non-exhaustive requirements (2021); Parameters related to frequency stability; RoCoF withstand capability; Reactive power management at T/D interface; Real time data and communication; Voltage related parameters","ENTSO-E","EU",
  "https://www.entsoe.eu/network_codes/cnc/cnc-igds/",
  "Non-binding guidance on implementation of the connection network codes (DCC Art. 56). No single scope sentence; each IGD names its codes and articles.",
  "", "full","published (versions as listed on the page; archives excluded)","seed","read 4 (keyword-headed clauses across 14 IGDs); 0 pass"),
I("E03","E","ACER Recommendation No 01/2025, Annex 4a — amended DC Network Code (draft COMMISSION REGULATION (EU) …/…)","Commission Regulation (EU) …/… establishing a Network Code on Demand Connection (amended draft)","ACER (proposal to the European Commission)","EU",
  "https://www.acer.europa.eu/sites/default/files/documents/Recommendations_annex/ACER_Recommendation_01-2025_DR_NC-Annex4a_Amended_DC_Regulation_TC.pdf.pdf",
  "Title only (draft regulation text).", "", "full","pending (recommendation to the Commission; not adopted as of screening)","seed (pending proposal found while resolving E01)","read 0 (power-quality article has no cited document); 0 pass"),
I("E04","E","The Grid Code, Issue 6 Revision 47 (29 Oct 2026; complete) + Revision 48 (3 Nov 2026; General Conditions only)","The Grid Code — Connection Conditions (CC) and European Connection Conditions (ECC)","NESO (National Energy System Operator)","GB",
  "https://www.neso.energy/industry-information/codes/grid-code-gc/grid-code-documents",
  "“The Connection Conditions (“CC”) specify both: (a) the minimum technical, design and operational criteria which must be complied with by: (i) any GB Code User connected to or seeking connection with the National Electricity Transmission System …” (CC.1.1; ECC.1.1 is parallel for EU Code Users)",
  "CC.6.1.7 Voltage changes at a Point of Common Coupling on the Onshore Transmission System; CC.6.1.8 Voltage fluctuations at a Point of Common Coupling with a fluctuating Load …; ECC.6.1.7; ECC.6.1.8; CC.6.4 / ECC.6.4 General Network Operator and Non-Embedded Customer Requirements; Demand Response Services Code (DRSC)",
  "full","in force","seed","read 8 (keyword-headed clauses); 1 added (EREC P28)"),
I("E05","E","VDE-AR-N 4120:2018-11 with VDE-AR-N 4120/A1:2024-04 (in force); successor VDE-AR-N 4120:2026-12 listed with Erscheinungsdatum 2026-11-20 and withdrawal of the 2018-11 edition 2026-12-01 (as printed)","Technische Regeln für den Anschluss von Kundenanlagen an das Hochspannungsnetz und deren Betrieb (TAR Hochspannung)","VDE FNN","DE",
  "https://www.vde.com/de/fnn/themen/tar/tar-hochspannung-vde-ar-n-4120",
  "“Diese VDE-Anwendungsregel legt die Technischen Regeln (TAR) für Planung, Errichtung, Betrieb und Änderung von Kundenanlagen (Bezugs- und Erzeugungsanlagen, Speicher sowie Mischanlagen) fest, die am Netzanschlusspunkt an das Hochspannungsnetz eines Netzbetreibers der allgemeinen Versorgung angeschlossen werden. […]” (VDE Verlag catalogue description)",
  "", "partial","in force (raters re-check edition on reading date)","seed","not accessible (catalogue page only)"),
I("E06","E","E VDE-AR-N 4120/A1:2026-05 (draft amendment)","Entwurf der Ergänzung zur TAR Hochspannung (Novelle 2025) (E VDE-AR-N 4120/A1)","VDE FNN","DE",
  "https://www.vde.com/de/fnn/themen/tar/tar-hochspannung-vde-ar-n-4120/tar-hochspannung-vde-ar-n-4120",
  "“Der Entwurf der Ergänzung zur TAR Hochspannung (Novelle 2025) (E VDE-AR-N 4120/A1) steht zur Konsultation bereit.” (VDE FNN page)",
  "", "partial","pending (as printed: Entwurf)","seed (pending proposal found while resolving E05)","not accessible"),
I("E07","E","VDE-AR-N 4130:2018-11 with VDE-AR-N 4130/A1 (in force 1 June 2026, as printed)","Technische Regeln für den Anschluss von Kundenanlagen an das Höchstspannungsnetz und deren Betrieb (TAR Höchstspannung)","VDE FNN","DE",
  "https://www.vde.com/de/fnn/themen/tar/tar-hoechstspannung-vde-ar-n-4130",
  "“VDE/FNN beschreibt darin erstmals bundesweit einheitliche Anforderungen an alle Kundenanlagen mit Anschluss an das Höchstspannungsnetz. … Damit wird es künftig einheitliche Anforderungen an alle Arten von Kundenanlagen in der Höchstspannung geben: Erzeuger, Verbraucher, Speicher und Mischanlagen. Die neue Anwendungsregel gestaltet außerdem die relevanten Europäischen Network Codes (RfG, DCC) für diese Spannungsebene in Deutschland aus.” (VDE Verlag description)",
  "", "partial","in force (a revision draft is announced by VDE FNN for Oct 2026; no draft document located)","seed","not accessible (catalogue page only)"),
I("E08","E","D-A-CH-CZ Technische Regeln, Teil A, 3. Ausgabe 2021","Technische Regeln für die Beurteilung von Netzrückwirkungen — Teil A: Grundlagen","D-A-CH-CZ working group EMC & Power Quality; published by Oesterreichs Energie, VSE, VDE FNN, CSRES","DE/AT/CH/CZ",
  "https://www.vde.com/de/fnn/arbeitsgebiete/versorgungsqualitaet/spannungsqualitaet/netzruckwirkungen",
  "“Die Technischen Regeln dienen grundsätzlich der Festlegung von Grenzwerten für genehmigungspflichtige Großgeräte und Anlagen von Netzbenutzern mit einer Anschlussleistung größer 52 kVA.” (2.4 Anwendungsbereich)",
  "2.4 Anwendungsbereich; 2.11 Normative Bezüge; 4 Spannungsänderungen und Flicker (4.1 Spannungsänderungen; 4.2 Flicker; 4.4 Bewertungsgrößen; 4.6 Messtechnischer Nachweis)",
  "full","in force (3rd edition)","seed","read 30 (2.11 normative references clause + 15 citing sentences in clause 4); 2 added (EN 61000-3-3, EN 61000-3-11)"),
I("E09","E","D-A-CH-CZ Technische Regeln, Teil B Abschnitt I, 3. Ausgabe 2021","Technische Regeln für die Beurteilung von Netzrückwirkungen — Teil B: Anforderungen und Beurteilung, Abschnitt I: Niederspannung","D-A-CH-CZ (as E08)","DE/AT/CH/CZ",
  "https://www.vde.com/de/fnn/arbeitsgebiete/versorgungsqualitaet/spannungsqualitaet/netzruckwirkungen",
  "“Das vorliegende Dokument fasst die Beurteilungsverfahren und die Berechnung der Emissionsgrenzwerte für Anlagen von Netzbenutzern zum Anschluss an das öffentliche Niederspannungsnetz zusammen.” (Vorwort)",
  "1 Spannungsänderungen und Flicker (1.1 Spannungsänderungen; 1.2 Flicker; 1.3 Beurteilung); Normenverzeichnis",
  "full","in force","seed","read 11 (Normenverzeichnis + 1 citing sentence); 0 new (EN 61000-3-3/-3-11 already added; EN 61000-4-15 already listed)"),
I("E10","E","D-A-CH-CZ Technische Regeln, Teil B Abschnitt II, 3. Ausgabe 2022","Technische Regeln für die Beurteilung von Netzrückwirkungen — Teil B: Anforderungen und Beurteilung, Abschnitt II: Mittelspannung","D-A-CH-CZ (as E08)","DE/AT/CH/CZ",
  "https://www.vde.com/de/fnn/arbeitsgebiete/versorgungsqualitaet/spannungsqualitaet/netzruckwirkungen",
  "“Das vorliegende Dokument fasst die Beurteilungsverfahren und die Berechnung der Grenzwerte für Anlagen von Netzbenutzern zum Anschluss an das Mittelspannungsnetz zusammen.” (Vorwort)",
  "1 Spannungsänderungen und Flicker (1.2.1 Planungspegel und anteiliger Beitrag; 1.2.2 Emissionsgrenzwerte; 1.3 Beurteilung); Normenverzeichnis",
  "full","in force","seed","read 8 (Normenverzeichnis + 1 citing sentence); 0 new (IEC TR 61000-3-7, EN 61000-4-15 already listed)"),
I("E11","E","D-A-CH-CZ Technische Regeln, Teil B Abschnitt III, 3. Ausgabe 2023","Technische Regeln für die Beurteilung von Netzrückwirkungen — Teil B: Anforderungen und Beurteilung, Abschnitt III: Hochspannung","D-A-CH-CZ (as E08)","DE/AT/CH/CZ",
  "https://www.vde.com/de/fnn/arbeitsgebiete/versorgungsqualitaet/spannungsqualitaet/netzruckwirkungen",
  "“Das vorliegende Dokument fasst die Beurteilungsverfahren und die Berechnung der Grenzwerte für Anlagen von Netzbenutzern zum Anschluss an das Hochspannungsnetz zusammen.” (Vorwort)",
  "1 Spannungsänderungen und Flicker (1.2.1 Planungspegel und anteiliger Beitrag; 1.2.2 Emissionsgrenzwerte; 1.3 Beurteilung; 1.4 Messtechnischer Nachweis); Normenverzeichnis",
  "full","in force","seed","read 5 (Normenverzeichnis + 1 citing sentence); 0 new (EN 61000-4-15 already listed)"),
# ---------------- Q ----------------
I("Q01","Q","IEC TR 61000-3-7:2008 (Ed. 2.0)","Electromagnetic compatibility (EMC) - Part 3-7: Limits - Assessment of emission limits for the connection of fluctuating installations to MV, HV and EHV power systems","IEC","International",
  "https://webstore.iec.ch/en/publication/4156",
  "“This part of IEC 61000 provides guidance on principles which can be used as the basis for determining the requirements for the connection of fluctuating installations to MV, HV and EHV public power systems (LV installations are covered in other IEC documents). For the purposes of this report, a fluctuating installation means an installation (which may be a load or a generator) that produces voltage flicker and / or rapid voltage changes. The primary objective is to provide guidance to system operators or owners on engineering practices which will facilitate the provision of adequate service quality for all connected customers.”",
  "", "partial","published 2008-02-22; stability date 2026","seed","not accessible (abstract only; preview PDF 403)"),
I("Q02","Q","IEC 61000-4-30:2025 (Ed. 4.0)","Electromagnetic compatibility (EMC) - Part 4-30: Testing and measurement techniques - Power quality measurement methods","IEC","International",
  "https://webstore.iec.ch/en/publication/71611",
  "“Measurement methods are described for each relevant parameter in terms that give reliable and repeatable results, regardless of the method’s implementation. This document addresses measurement methods for in-situ measurements. … The power quality parameters considered in this document are power frequency, magnitude of the supply voltage, flicker, supply voltage dips and swells, voltage interruptions, transient voltages, supply voltage unbalance, voltage harmonics and interharmonics, rapid voltage changes, …”",
  "", "partial","published 2025-10-24","seed","not accessible (abstract only)"),
I("Q03","Q","IEC 61000-4-15:2010 (Ed. 2.0) with COR1:2012 and ISH1:2017","Electromagnetic compatibility (EMC) - Part 4-15: Testing and measurement techniques - Flickermeter - Functional and design specifications","IEC","International",
  "https://webstore.iec.ch/en/publication/4173",
  "“IEC 61000-4-15:2010 gives a functional and design specification for flicker measuring apparatus intended to indicate the correct flicker perception level for all practical voltage fluctuation waveforms. Information is presented to enable such an instrument to be constructed. A method is given for the evaluation of flicker severity on the basis of the output of flickermeters complying with this standard.”",
  "", "partial","published 2010-08-24; stability date 2026","seed","not accessible (abstract only)"),
I("Q04","Q","IEEE 519-2022","IEEE Standard for Harmonic Control in Electric Power Systems","IEEE SA","International (US origin)",
  "https://standards.ieee.org/ieee/519/10677/",
  "“Goals for the design of electrical systems that include both linear and nonlinear loads are established in this standard. … This standard addresses steady-state limitations. … This document sets the quality of power that is to be provided at the point of common coupling.”",
  "", "partial","Active Standard (published 2022-08-05); revision project P519 active (no draft public)","seed","not accessible (abstract only)"),
I("Q05","Q","IEEE 1453-2022","IEEE Standard for Measurement and Limits of Voltage Fluctuations and Associated Light Flicker on AC Power Systems","IEEE SA","International (US origin)",
  "https://standards.ieee.org/ieee/1453/10459/",
  "“Background information on supply voltage fluctuations caused by fluctuations in power demands of installations is provided by this standard. … For different system voltages, planning levels for flicker that the utilities need their system to be limited to in order to reduce customer complaints are defined in this standard. The procedure for determining emission limits for individual installations at the point of common coupling (PCC) so that the planning levels can be achieved in practice is defined in this standard.”",
  "", "partial","Active Standard (published 2023-02-27; supersedes 1453-2015)","seed","not accessible (abstract only)"),
I("Q06","Q","EN 50160:2022 with EN 50160:2022/A1:2025","Voltage characteristics of electricity supplied by public electricity networks","CENELEC (CLC/TC 8X)","Europe",
  "https://standards.cencenelec.eu/ords/f?p=CENELEC:110:::::FSP_PROJECT:71003&cs=18A352BF203027ECCA5F79274EFAC20F4",
  "“This document specifies the main characteristics of the voltage at a network user's supply terminals in public low voltage, medium, high, and extra-high voltage …” (1.1 Application, catalogue abstract; truncated as displayed). “NOTE 4 This document can be superseded in total or in part by the terms of a contract between the individual network user and the network operator.”",
  "", "partial","Published (DOR 2022-11-07); A1:2025 listed under TC 8X published standards","seed","read 1 (catalogue normative reference: EN 61000-4-30:2015 → already listed Q02)"),
I("Q07","Q","IEC 61000-3-3:2013+AMD1:2017+AMD2:2021 (cited as EN 61000-3-3:2013)","Electromagnetic compatibility (EMC) - Part 3-3: Limits - Limitation of voltage changes, voltage fluctuations and flicker in public low-voltage supply systems, for equipment with rated current ≤16 A per phase and not subject to conditional connection","IEC (EN version: CENELEC)","International / Europe",
  "https://webstore.iec.ch/en/publication/4150",
  "“IEC 61000-3-3:2013 is concerned with the limitation of voltage fluctuations and flicker impressed on the public low-voltage system. It specifies limits of voltage changes which may be produced by an equipment tested under specified conditions and gives guidance on methods of assessment.”",
  "", "partial","in force (consolidated CSV 3.2; ISH1:2025 exists)","added via E08 clause 2.11","not screened (one level)"),
I("Q08","Q","IEC 61000-3-11:2017 (Ed. 2.0) (cited as EN 61000-3-11:2000)","Electromagnetic compatibility (EMC) - Part 3-11: Limits - Limitation of voltage changes, voltage fluctuations and flicker in public low-voltage supply systems - Equipment with rated current ≤ 75 A and subject to conditional connection","IEC (EN version: CENELEC)","International / Europe",
  "https://webstore.iec.ch/en/publication/27902",
  "“IEC 61000-3-11:2017 is concerned with the emission of voltage changes, voltage fluctuations and flicker produced by equipment and impressed on the public low-voltage supply system. It specifies the limits of voltage changes produced by equipment tested under specified conditions.”",
  "", "partial","in force (2017 edition; the cited EN 61000-3-11:2000 edition is superseded)","added via E08 clause 2.11","not screened (one level)"),
I("Q09","Q","EREC P28 Issue 2 (May 2019)","Voltage fluctuations and the connection of disturbing equipment to transmission systems and distribution networks in the United Kingdom","Energy Networks Association (ENA)","GB",
  "https://www.ena-eng.org/ENA-Docs/Index.aspx?Action=ViewDetail&EID=99789&tab=introduction",
  "“This EREC defines planning levels and compatibility levels for the assessment of voltage fluctuations from customer disturbing equipment and fluctuating installations to be connected to transmission systems and distribution networks in the United Kingdom. This EREC only applies to the proposed connection of customer disturbing equipment and fluctuating installations. … The scope of voltage fluctuations in this EREC applies to flicker or RVCs emitted onto the public electricity supply system by customer equipment, i.e. customer owned demand, generation, energy storage, or other types of disturbing equipment that may be connected.”",
  "", "partial","Current (catalogue)","added via E04 clause CC.6.1.7 / ECC.6.1.7 (also CC data clause ‘Demand fluctuations greater than those permitted under [P28]’)","not screened (one level)"),
# ---------------- V ----------------
I("V01","V","OCP Open Rack V3 Base Specification, Rev 1.1","Open Rack V3 Base Specification","Open Compute Project","Industry (global)",
  "https://www.opencompute.org/documents/open-rack-base-specification-version-3-rev1-1-030524-pdf/",
  "“This document defines technical specifications for all components within the Open Rack Frame V3 family used in the Open Compute Project. This document is intended to define all of the requirements needed to ensure intermateability of IT Gear across different racks and power systems developed by the community. Compliance with this specification is required for any products intended to operate with Open Rack V3.” (4. Scope)",
  "", "full","published","seed","read 0 (keyword-headed clauses); 0 pass"),
I("V02","V","OCP Open Rack V3 Power Shelf, Rev 1.0 (file rev 1.0.1, dated 11/10/2022)","Open Rack V3 Power Shelf","Open Compute Project","Industry (global)",
  "https://www.opencompute.org/documents/ocp-open-rack-v3-power-shelf-rev-1-0-1-pdf/",
  "“This document defines the technical specifications for Open Rack V3 Power Shelves used in the Open Compute Project.” (1. Scope)",
  "", "full","published","seed","read 0; 0 pass"),
I("V03","V","OCP Open Rack V3 HPR V2 72kW Power Shelf, Rev 1.0.0 (12 June 2026)","Open Rack V3 HPR V2 72kW Power Shelf","Open Compute Project","Industry (global)",
  "https://www.opencompute.org/documents/open-rack-v3-hpr-v2-72kw-power-shelf-spec-v1-0-0-pdf/",
  "“This document defines the technical specifications for Open Rack V3 72kW Power Shelf used in the Open Compute Project.” (2. Scope)",
  "5.5.2 Pulse_Mgmt_L Signal; 5.6 Peak Load requirements; 5.7 Parallel Operation Mode with Multiple Shelves", "full","published","seed","read 0; 0 pass"),
I("V04","V","OCP Open Rack V3 BBU Shelf, Rev 1.1","Open Rack V3 BBU Shelf","Open Compute Project","Industry (global)",
  "https://www.opencompute.org/documents/open-rack-v3-bbu-shelf-spec-rev1-1-pdf-1/",
  "“This document defines the technical specifications for Open Rack V3 BBU Shelves used in the Open Compute Project.” (3 Scope)",
  "", "full","published","seed","read 0; 0 pass"),
I("V05","V","OCP Open Rack V3 48V BBU, Rev 1.4","Open Rack V3 48V BBU (BBU module)","Open Compute Project","Industry (global)",
  "https://www.opencompute.org/documents/open-rack-v3-bbu-module-spec-1-4-pdf/",
  "“This document defines the technical specifications for the Open Rack V3 BBU (Battery Backup Unit) used in the Open Compute Project.” (1. Scope)",
  "", "full","published","seed","read 0; 0 pass"),
I("V06","V","OCP Diablo 400 Project: Rack and Power, 0.7.0 Base Specification (effective March 1st, 2026) — ‘Mt Diablo’ ±400 VDC","Diablo 400 Project: Rack and Power","Open Compute Project (authors Microsoft, Meta, Google)","Industry (global)",
  "https://www.opencompute.org/documents/ocp-specification-diablo-400-v0-7-0-final-pdf/",
  "“With increased rack power (from 33kW to 100’s of kW), size and power of AI accelerators, and rack/POD size growth, there are significant challenges with interconnect density, power delivery and overall system integration. To solve this, the disaggregated power rack (also known as sidecar) provides a flexible and evolving infrastructure solution.” (5 Scope)",
  "7.1.3 AC Loss (Holdup and ride-through); 7.2 Energy Storage Solutions (BBU; Capacitor Bank Option CBU); 7.3.3 DC Output – Dynamic loading; 9.2 Telemetry",
  "full","published (v0.7.0)","seed","read 1; 0 pass (IEC 61000-4-34 cited for line sag ride-through)"),
I("V07","V","OCP Open Rack V3 HVDC-LVDC 100kW Power Shelf Design Specification, Version 1.0.0","Open Rack V3 HVDC-LVDC 100kW Power Shelf Design Specification","Open Compute Project","Industry (global)",
  "https://www.opencompute.org/documents/orv3-hvdc-lvdc-100kw-power-shelf-spec-1-0-0-pdf/",
  "“This document defines the technical specifications for Open Rack V3 HVDC 100kW Power Shelf used in the Open Compute Project.” (1. Scope)",
  "", "full","published","seed (800 VDC specifications)","read 0; 0 pass"),
I("V08","V","OCP Open Rack V3 +/- 400V to 50V 18kW PSU Design Specification, Version 1.0.0","Open Rack V3 +/- 400V to 50V 18kW PSU Design Specification","Open Compute Project","Industry (global)",
  "https://www.opencompute.org/documents/hvdc-lvdc-psu-18kw-spec-1-0-0-pdf/",
  "“This document defines the technical specifications for Open Rack V3 HVDC IT Rack HVDC input power supply used in the Open Compute Project.” (1. Scope)",
  "", "full","published","seed (800 VDC specifications)","read 0; 0 pass"),
I("V09","V","OCP Base Specification Version 1.0.0 (effective September 17, 2026)","Data Center Facility Project: Interface Specification Between Hyperscalers and Utility Grid for Disturbance Performance","Open Compute Project (authors Google, Microsoft, Meta, NVIDIA)","Industry (global)",
  "https://www.opencompute.org/documents/ocp-base-spec-interface-specification-between-hyperscalers-and-utility-grid-for-disturbance-performance-pdf/",
  "“This OCP Base Specification establishes the interface requirements between hyperscale operators and the utility grid for performance during grid disturbances. The primary objective is to maintain grid stability and reliability through efficient power delivery that accommodates the dynamic demands of advanced computing infrastructure.” (4.1 Description)",
  "4.2 Past and Upcoming Utility Requirements; 4.4 Voltage Ride-Through and Post Fault Active Power Recovery (4.4.3 Proposed specification); 4.6.1 Future requirements; 5 References",
  "full","published","seed (OCP ‘any power-stabilisation … requirements document’; title names data center)","read 19 (References clause 4 entries + 15 citing sentences); 0 new (IEEE 1453, IEEE 519, NOGRR282 already listed)"),
I("V10","V","OCP Open Data Center: Next-Generation ML Infrastructure Design Principles, Revision 0.7.0 (effective Aug 27, 2026)","Open Data Center: Next-Generation ML Infrastructure Design Principles (Datacenter design specification)","Open Compute Project (authors AMD, Google, Meta, Nvidia)","Industry (global)",
  "https://www.opencompute.org/wp-content/uploads/2026/10/Open-Data-center-Spec-Revision-0.7.0-4.pdf",
  "“This specification outlines the unified data center design standards developed in collaboration with Google, Meta, Nvidia, and AMD. This iteration focuses on the 2027-2028 timeline and emphasizes flexible, first principles guidelines to support next-generation AI and ML workloads. The standards herein govern structural, power, and cooling infrastructure to ensure industry wide adaptability and scalability.” (3. Specifications)",
  "5. Power and Density Requirements (5.1 Cluster and Power Density Targets; 5.2 Power Architecture and Interfaces)",
  "full","published (Rev 0.7.0; supersedes 0.3/0.5)","seed (OCP ‘any …’; title names data center)","read 0; 0 pass"),
I("V11","V","NVIDIA Technical Blog, Jul 28, 2025","How New GB300 NVL72 Features Provide Steady Power for AI","NVIDIA","Vendor (global)",
  "https://developer.nvidia.com/blog/how-new-gb300-nvl72-features-provide-steady-power-for-ai/",
  "“NVIDIA introduces a comprehensive power smoothing solution in the GB300 NVL72 platform, combining programmable power caps, integrated electrolytic capacitors for energy storage, and a hardware power burner with software …” (opening paragraph, truncated as displayed)",
  "", "full","published","seed (GB200/GB300 NVL72 power-smoothing and power-capping documentation)","read 0; 0 pass"),
I("V12","V","NVIDIA System Management Interface manual (nvidia-smi), docs.nvidia.com/deploy/nvidia-smi","nvidia-smi — NVIDIA System Management Interface program (manual)","NVIDIA","Vendor (global)",
  "https://docs.nvidia.com/deploy/nvidia-smi/index.html",
  "“nvidia-smi (also NVSMI) provides monitoring and management capabilities for each of NVIDIA's Tesla, Quadro, GRID and GeForce devices from Fermi and higher architecture families.” (DESCRIPTION)",
  "DEVICE MODIFICATION OPTIONS: -pl, --power-limit; GPU ATTRIBUTES: Power Smoothing, Energy Storage Power Smoothing, GPU/Module Power Limits; command section ‘nvidia-smi power-smoothing’",
  "full","current web edition","seed (power-smoothing / power-capping documentation)","read 0; 0 pass"),
I("V13","V","NVIDIA GB200 NVL Multi-Node Tuning Guide — chapter ‘Power and Thermals’","Power and Thermals — NVIDIA GB200 NVL Multi-Node Tuning Guide","NVIDIA","Vendor (global)",
  "https://docs.nvidia.com/multi-node-nvlink-systems/multi-node-tuning-guide/power-thermals.html",
  "“This chapter provides information about CPU power and thermal management settings.” … “Power Smoothing has been implemented to handle these situations, and customers can refer to the application note for more information.”",
  "Power Tunings", "full","current web edition (the application note it mentions is not linked and was not located)","seed","read 3; 0 pass"),
I("V14","V","NVIDIA white paper (Jared Huntington & Mike Tu)","800 VDC Architecture for Next-Generation AI Infrastructure","NVIDIA","Vendor (global)",
  "https://www.nvidia.com/en-us/data-center/technologies/800-vdc-architecture/",
  "Title page: “The Architectural Imperative of 800 VDC and Integrated Energy Storage”. No scope sentence (white paper).",
  "Load Swings and Energy Storage; Grid Interconnect Requirements; 800 VDC MGX Architecture; Datacenter Reference design",
  "full","published (PDF linked from nvidia.com as ‘Read Whitepaper 1’)","seed","read 0; 0 pass"),
]

locators = [
 dict(name="NERC white paper (seed locator)", title="Characteristics and Risks of Emerging Large Loads — Large Loads Task Force White Paper, July 2025", url="https://www.nerc.com/globalassets/who-we-are/standing-committees/rstc/3_doc_white-paper-characteristics-and-risks-of-emerging-large-loads.pdf", kind="S0 locator", citing=99, refs="footnotes (no reference section detected)", candidates="BAL-001 (CPS1/BAAL: BA ACE, not a load limit) — fails test 2", added=0),
 dict(name="NERC gap white paper (seed locator)", title="Assessment of Gaps in Existing Practices, Requirements, and Reliability Standards for Emerging Large Loads — NERC LLWG White Paper, March 2026", url="https://www.nysrc.org/wp-content/uploads/2026/02/NYSRC-LLWG-2-Att.-6.pdf (NYSRC-hosted copy; nerc.com page JS-rendered, PDF URL not found)", kind="S0 locator", citing=229, refs="footnotes", candidates="BAL-001, TOP standards cited as lacking ramp constraints — fail test 2", added=0),
 dict(name="OCP Open Data Center for AI (seed locator)", title="Open Data Center for AI — A Strategic Initiative of the Open Compute Project (white paper, April 2026)", url="https://www.opencompute.org/documents/ocp-open-data-center-for-ai-whitepaper-final-pdf", kind="S0 locator (kept by title under OCP ‘any …’; white paper)", citing=4, refs="3 entries", candidates="none", added=0),
 dict(name="OCP DCF LVDC white paper (seed locator)", title="Data Center Facility – Low Voltage Direct Current Power Distribution, Version 1.1.0 (2 Sept 2026)", url="https://www.opencompute.org/wp-content/uploads/2026/10/DCF-Power-Distribution-LVDC-white-paper-version-1.1.0.pdf", kind="S0 locator (kept by title under OCP ‘any …’; white paper)", citing=214, refs="15. References (papers) + numbered sources [12]–[29]", candidates="AESO Guide to AESO Connection Requirements for Transmission-Connected Data Centres [24]; EirGrid/SONI FRT papers [25]; Energinet TR 3.4.3 [26]; RTE DTR Art. 8.3.5 [27]; Fingrid large demand facility requirements [28]; SPP HILL FRT requirements [12,13,21]; IESO LCL technical requirements [23]; ATC planning criteria [22] — all cited for ride-through / post-fault active power recovery / RoCoF tables → fail test 2. IEC 61000-3-11 (flicker) → already listed (Q08); IEC 61000-3-12, IEC/TR 61000-3-6 (harmonics) → fail test 2; Regulation (EU) 2016/1388 [29] → already listed (E01).", added=0),
 dict(name="NVIDIA 800 VDC white paper 2 (seed locator)", title="800 VDC Architecture: Industry Alignment & Execution (White Paper)", url="https://www.nvidia.com/en-us/data-center/technologies/800-vdc-architecture/ (‘Read Whitepaper 2’)", kind="S0 locator", citing=3, refs="none", candidates="none", added=0),
 dict(name="Microsoft blog (seed locator)", title="Power stabilization for AI training datacenters (Microsoft Tech Community, Azure Compute blog)", url="https://techcommunity.microsoft.com/blog/azurecompute/power-stabilization-for-ai-training-datacenters/4460937", kind="S0 locator (kept by title under ‘any Microsoft … requirement’; blog describing the arXiv paper)", citing=3, refs="links to arXiv 2508.14318", candidates="none", added=0),
 dict(name="arXiv 2508.14318", title="Power Stabilization for AI Training Datacenters (Choukse et al.)", url="https://arxiv.org/abs/2508.14318", kind="S1 locator", citing=55, refs="23 entries", candidates="[1] IEC 61000-3-3:2013 (‘tolerances … informed by grid standards such as [1]’) → passes; already listed (Q07). NERC oscillation reports [11,12], EPRI/GE torsional reports [4,6] → fail test 1. NVIDIA tuning guide [13] → already listed (V13).", added=0),
 dict(name="arXiv 2605.24461", title="Provisioning to Runtime Optimization of a 100 MW-Scale AI Cluster", url="https://arxiv.org/abs/2605.24461", kind="S1 locator", citing=66, refs="51 entries", candidates="none", added=0),
 dict(name="ERCOT-hosted NERC presentation", title="260424 NERC Update for ERCOT LLWG (Apr 24, 2026)", url="https://www.ercot.com/files/docs/2026/04/23/260424-NERC-Update-for-ERCOT-LLWG.pdf", kind="S1 locator (NERC presentation)", citing=29, refs="none", candidates="none", added=0),
 dict(name="FERC-hosted NERC presentation", title="NERC Activities and Plans to Address Reliability Impacts from Large Load Integration (FERC Open Meeting, April 2025)", url="https://www.ferc.gov/sites/default/files/2025-04/Presentation%20NERC%20Seeks%20to%20Address%20Reliability%20Impacts%20from%C2%A0Large%20Load%20Integration_1.pdf", kind="S1 locator (NERC presentation)", citing=1, refs="none", candidates="none", added=0),
 dict(name="PJM presentation", title="PJM LCL Ride-through Requirements — PJM Interconnection Proposal (Planning Committee, Sept 8, 2026)", url="https://www.pjm.com/-/media/DotCom/committees-groups/committees/pc/2026/20260908/20260908-item-05---1-large-load-ride-through---presentation.pdf", kind="S1 locator (ISO presentation)", citing=7, refs="none", candidates="none (mentions FERC EL26-67 show-cause order; future ramp-rate work)", added=0),
 dict(name="NERC LLAP update", title="Large Loads Action Plan Q3 2026 Update", url="https://www.nerc.com/globalassets/initiatives/large-loads-action-plan/llap-quarterly-update-q3-2026.pdf", kind="S1 locator (NERC)", citing=17, refs="none", candidates="none", added=0),
]
epri = [("3002031504","White Paper: Grid Flexibility Needs and Data Center Characteristics",1),("3002033410","Texas SB6 Explained: Addressing Large Load Impacts",15),("3002033797","White Paper – Integrating Data Centers into the Grid: Benefits of Flexibility and Strategic Siting",4),("3002034099","Assessing Subsynchronous Torsional Interactions with Respect to AI Training Loads",None),("3002034368","Quick Insight – NERC Reliability Guideline: Risk Mitigation for Emerging Large Loads",1),("3002034369","Quick Insight – DOE's Section 403 Letter Explained: Large Load Interconnection",0),("3002034666","Quick Insight: Market and Regulatory Responses to Large Load Growth and the Capacity Crunch in PJM",68),("3002034667","Balancing Speed and Affordability: The NIPSCO GenCo Model for Hyperscale Load Growth",8),("3002036212","Large Load Ride-Through For Data Centers: Identifying Gaps in Requirements, Interpretation, and Compliance",34),("3002036213","Quick Insight: Community Acceptance in Practice",32),("3002036257","Quick Insight: Connecting Data Center Growth to the Distribution Grid",3),("3002036343","Quick Insight: NERC Level 3 Computational Load Alert: Actions and Pathways for Industry Support",21),("3002036362","DCFlex Demonstration of Cleaner Backup Power (HVO)",0),("3002036374","Managing Oscillating Load Impacts from Data Centers on Synchronous Machines: A Framework for Estimating Acceptable Load Oscillation Limits to Minimize Turbine-Generator Shaft Impacts",4),("3002036523","How Existing Programs and Services Fit Within Flex MOSAIC Classes",11),("3002036744","Onsite Generation Options for Data Centers: Implications for Data Center Flexibility",None),("3002036753","Data Center Cooling: Implications for Data Center Flexibility",None),("3002036755","Energy Storage Options for Data Center Flexibility",None),("3002036874","Flex MOSAIC: A Framework to Unlock Large Load Flexibility and Increase Speed to Power",1),("3002036875","Designing for Flexibility: How Onsite Generation, Energy Storage, and Flexible Cooling Technologies Align with Different Data Center Flexibility Needs",3),("3002036876","Tech In Focus: Jenbacher Spark-Ignition Engines",0),("3002036922","Planning for Data Center Demand: Forecasting Regional Load Growth with Interconnection Queue Data",5),("3002037065","Community Guide to Understanding Water and Data Centers",22),("3002037176","Exec Summary – Smoothing Load Fluctuations from Data Centers: A Comparative Study of Mitigation Technologies",2),("3002037178","Smoothing Load Fluctuations from Data Centers: A Comparative Study of Mitigation Technologies (full report)",None)]
for pid, t, c in epri:
    locators.append(dict(name="EPRI DCFlex %s" % pid, title=t, url="https://www.epri.com/research/products/%s (download: https://restservice.epri.com/publicdownload/%018d/0/Product)" % (pid, int(pid)),
                         kind="S1 locator (EPRI DCFlex)", citing=(c if c is not None else "references not accessible (download refused: not purchased)"),
                         refs=("—" if c is None else ("27 entries" if pid=="3002036374" else "endnotes/none detected")),
                         candidates=("EPRI EL-3083 shaft-oscillation report → fails test 1" if pid=="3002036374" else "none"), added=0))

queries = [
 ("WebSearch","site:ercot.com \"Large Load\" NPRR OR PGRR OR NOGRR 2025 2026 revision request",19,"located ERCOT RR documents; systematic listing then taken from ERCOT RR report pages"),
 ("ERCOT listing","https://www.ercot.com/mktrules/issues/reports/nprr — title regex large load|data cent|ramp|step|fluctuat|oscillat|stabili[sz]|smooth|computational","1353 rows / 16 title hits",""),
 ("ERCOT listing","https://www.ercot.com/mktrules/issues/reports/pgrr — same regex","147 rows / 9 title hits",""),
 ("ERCOT listing","https://www.ercot.com/mktrules/issues/reports/nogrr — same regex","290 rows / 4 title hits",""),
 ("WebSearch","site:ercot.com SB6 large load curtailment draft NPRR workshop 2026",19,"draft RRs presented at Oct 6, 2026 workshop; not filed"),
 ("WebSearch","site:nerc.com large loads task force white paper reliability guideline large loads 2025 2026",10,""),
 ("WebSearch","NERC \"Reliability Guideline\" \"Large Loads\" nerc.com pdf",10,"located RG PDF URL"),
 ("WebSearch","NERC Level 2 alert large loads 2025 \"Large Load\" alert nerc.com",18,"located Level 2 alert PDF"),
 ("WebSearch","nerc.com \"Characteristics and Risks of Emerging Large Loads\" white paper pdf; \"Assessment of Gaps\" ...",10,""),
 ("WebSearch","\"Assessment of Gaps in Existing Practices, Requirements, and Reliability Standards for Emerging Large Loads\" nerc globalassets",10,"no nerc.com PDF found; NYSRC copy used"),
 ("WebSearch","NERC standards project \"Large Loads\" Project 2025 OR 2026 SAR standard drafting team",10,"Project 2026-02"),
 ("WebSearch","nerc.com \"Project 2026-02\" \"Computational Loads\" project page (allowed: nerc.com)",9,"draft CLO-001/002/003"),
 ("WebSearch","NERC Project 2026-02 ... final ballot OR additional ballot ... (nerc.com)",10,"status: balloting, not adopted"),
 ("WebSearch","nerc.com globalassets standards projects 2026-02 final-posting CLO-001-1 clean",10,"no final clean draft found"),
 ("WebSearch","pjm.com \"large load additions\" critical issue fast path 2025 2026 board decision manual tariff filing",10,""),
 ("WebSearch","pjm.com large load ride-through OR oscillation OR ramp requirements data center manual 14 2026",10,"located PJM draft ride-through redline (summary text leaked values; see deviation DC2-S2)"),
 ("WebSearch","PJM filing large computational load ride-through tariff revisions EL26-67 compliance filing November 2026 docket",10,"responses due Nov 16, 2026: still pending"),
 ("WebSearch","ferc.gov co-location order PJM EL25-49 December 18 2025 order",10,""),
 ("WebSearch","ferc.gov \"190 FERC ¶ 61,115\" co-location show cause order February 20 2025 pdf",9,"Feb 2025 show-cause order PDF not located"),
 ("WebSearch","puc.texas.gov SB 6 large load rule adopted 16 TAC 25 project large load interconnection standards",10,""),
 ("PUCT index","https://www.puc.texas.gov/agency/rulesnlaws/subrules/electric/ (215 rule links; title filter large load|SLLIA|data cent|ramp|step|fluctuat|oscillat)","4 hits","§25.194, §25.205, §25.370, SLLIA (Project 59999)"),
 ("WebSearch","aepohio.com tariff data center tariff schedule 2025 PUCO approved \"Data Center\" tariff sheet",16,""),
 ("WebSearch","Dominion Energy Virginia \"GS-5\" rate schedule large load 25 MW tariff SCC final order PUR-2025-00058",10,""),
 ("WebSearch","georgiapower.com \"Rules and Regulations for Electric Service\" large load customers 100 MW pdf",10,""),
 ("WebSearch","utility tariff \"large load\" \"ramp rate\" OR \"load fluctuation\" OR \"step change\" rider schedule data center electric tariff sheet",17,"0 IOU tariffs whose title names ramp/step/fluctuation"),
 ("WebSearch","\"fluctuating load\" OR \"fluctuating loads\" electric utility tariff rule large customers data center 2025 2026 investor-owned utility",18,"0 kept"),
 ("WebSearch","Commission Regulation 2026 \"network code on demand connection\" repealing Regulation (EU) 2016/1388 adopted",10,"no repeal; ACER amended-DCC proposal located"),
 ("WebSearch","D-A-CH-CZ \"Technische Regeln zur Beurteilung von Netzrückwirkungen\" 2021 Ausgabe ...",18,"publisher pages located"),
 ("WebSearch","webstore.iec.ch IEC TR 61000-3-7 ...",10,""),
 ("WebSearch","webstore.iec.ch IEC 61000-4-30 ...; IEC 61000-4-15 ...",9,""),
 ("WebSearch","\"IEC 61000-4-15\" flickermeter functional and design specifications webstore.iec.ch publication",10,""),
 ("WebSearch","standards.ieee.org IEEE 1453 recommended practice analysis of fluctuating installations on power systems",9,""),
 ("WebSearch","ieeexplore.ieee.org \"IEEE Standard for Harmonic Control in Electric Power Systems\" 519-2022 document",9,"no Xplore landing; summary text leaked an allowance remark; see DC2-S2"),
 ("WebSearch","EN 50160:2022 ... CENELEC standards search project",9,""),
 ("OCP project page","https://www.opencompute.org/projects/rack-and-power/ (91 document links)","91 titles","kept per seed names (ORv3 base, power shelves, BBU, Diablo 400, HVDC 800 VDC specs)"),
 ("WebSearch","opencompute.org documents \"power stabilization\" OR \"power smoothing\" AI training data center specification requirements 2025 2026",10,"see OCP any-seed log"),
 ("WebSearch","opencompute.org \"AI\" \"power fluctuation\" OR \"load ramp\" OR \"power swing\" rack facility requirements document OCP 2026 workstream",10,"see OCP any-seed log (summary leaked values; DC2-S2)"),
 ("WebSearch","docs.nvidia.com power smoothing GB300 NVL72 documentation page title",20,""),
 ("WebSearch","NVIDIA \"power smoothing\" application note GB200 NVL72 docs.nvidia.com nvidia-smi power smoothing user guide",10,"application note not found (summary leaked a setting; DC2-S2)"),
 ("WebSearch","NVIDIA \"800 VDC\" architecture white paper pdf nvidia.com AI factories",9,""),
 ("WebSearch","Microsoft OR Google OR Meta published data center \"power\" requirements \"ramp\" OR \"power smoothing\" OR \"load fluctuation\" specification for suppliers grid",9,"see any-operator log"),
 ("WebSearch","Google OR Meta \"data center\" \"power\" \"requirements\" ramp rate grid interconnection AI training load published engineering blog specification",10,"0 kept (summary leaked a third-party paraphrase of an AESO limit; DC2-S2)"),
 ("WebSearch","standards.cencenelec.eu EN 61000-3-3 limitation of voltage changes voltage fluctuations flicker; EN 61000-3-11",9,"CENELEC page needs session checksum (500)"),
 ("WebSearch","webstore.iec.ch \"IEC 61000-3-3\" publication; \"IEC 61000-3-11\" publication",10,""),
]

any_logs = {
 "ERCOT — any 2025–2026 large-load protocol revision": {
   "queries": ["ERCOT RR report pages (NPRR/PGRR/NOGRR) with title regex", "WebSearch site:ercot.com (2 queries)"],
   "hit_counts": {"NPRR": "1353 rows / 16 hits", "PGRR": "147 / 9", "NOGRR": "290 / 4"},
   "kept": [
     "PGRR144 Dynamic Model Submission and Review Requirements for Large Loads including Large Computational Loads — approved 11/05/2026, effective 12/01/2026 → listed G04",
     "NPRR1234 Interconnection Requirements for Large Loads and Modeling Standards for Loads 25 MW or Greater — approved 05/15/2025 → incorporated in G02 (resolved to current Protocols)",
     "PGRR115 Related to NPRR1234 — approved 05/15/2025 → incorporated in G01",
     "NPRR1267 Large Load Interconnection Status Report — approved 07/31/2025 → incorporated in G02 (3.2.7)",
     "NPRR1308 Board Priority – Related to NOGRR282, Large Computational Load Ride-Through Requirements — approved 07/09/2026 → incorporated in G02",
     "NOGRR282 Board Priority – Large Computational Load Ride-Through Requirements — approved 07/09/2026, eff. 08/01/2026 → incorporated in G03 (2.6.4, 2.15)",
     "NPRR1325 Related to PGRR145, Batch Zero Process for Large Load Interconnections — approved 06/18/2026, eff. 07/11/2026 except 4.4.9.4, 4.4.9.4.4, 6.5.7.3, 6.5.7.11 → incorporated in G02 (gray-boxed parts pending implementation)",
     "PGRR145 Batch Zero Process for Large Load Interconnections — approved 06/18/2026, eff. 07/11/2026 except 9.6.1(2),(3) → incorporated in G01"],
   "dropped": [
     "NPRR069, NPRR217, NPRR239, NPRR277, NPRR282, NPRR351, NPRR460, NPRR920, NPRR973 — dated 2010–2023 and/or not large-load (generation/SCED ramp, transformer definitions)",
     "NPRR999 DC Tie Ramp Limitations — DC ties, not large load; pre-2025 by number",
     "PGRR074, NOGRR026, NOGRR196 — pre-2025 / not large-load",
     "NPRR1191, NPRR1202, PGRR111, PGRR135, PGRR136, PGRR138, PGRR141, NOGRR256 — Withdrawn",
     "SB6 Large Load Curtailment draft NPRR/NOGRR/PGRR (Oct 6, 2026 workshop) — drafts presented, not filed; no RR document"]},
 "NERC — any large-load standards project": {
   "queries": ["4 WebSearch queries (see query log)"],
   "kept": ["Project 2026-02 Computational Loads: CLO-001-1, CLO-002-1, CLO-003-1 Draft 1 (Aug 2026) → G07–G09, pending"],
   "dropped": ["Project 2026-02 FAC-001-5 / FAC-002-5 revisions — titles do not name large loads; not located as documents", "Rules of Procedure ‘Computational Load Entity’ registration changes — registration, not a standards project",
               "NERC Level 3 Essential Actions alert (May 2026) — not the 2025 alert named by the seed (logged, not listed)", "NERC LLWG ‘Large Load Disturbance Performance’ draft white paper — white paper (locator-type), not located on nerc.com"]},
 "Utility — any other IOU large-load tariff whose title names ramp, step or fluctuation": {
   "queries": ["2 WebSearch queries"], "hit_counts": {"q1": 17, "q2": 18},
   "kept": [], "dropped": ["All returned titles were studies, trackers, white papers or news (LBNL, Brattle, E3, Synapse/NM PRC, NASUCA, PA PUC model tariff comments, trade press); none is an IOU tariff whose title names ramp, step or fluctuation"]},
 "OCP — any power-stabilisation specification or requirements document (2025–2026)": {
   "queries": ["OCP Rack & Power project page (91 titles)", "2 WebSearch queries (opencompute.org)"], "hit_counts": {"project page": 91, "q1": 10, "q2": 10},
   "kept": ["Data Center Facility Project: Interface Specification Between Hyperscalers and Utility Grid for Disturbance Performance v1.0.0 → V09",
            "Open Data Center: Next-Generation ML Infrastructure Design Principles Rev 0.7.0 (title names Datacenter) → V10",
            "Open Data Center for AI (white paper, Apr 2026) → kept by title, classed locator (seed)",
            "Data Center Facility – LVDC Power Distribution white paper v1.1.0 → kept by title, classed locator (seed)"],
   "dropped": ["GW-scale Open AIDC Framework White Paper (Draft) — title does not literally name a keyword; draft white paper",
               "Colocation Facility Guidelines for Deployment of Open Racks — title names no keyword",
               "Thermal Boundaries in AI Infrastructure — thermal", "Datacenter Design Guide v0.3 / v0.5 — superseded by Rev 0.7.0",
               "OCP news article on AI data centre infrastructure — news"]},
 "Microsoft / Google / Meta — any published facility power-behaviour requirement found by title": {
   "queries": ["2 WebSearch queries"], "hit_counts": {"q1": 9, "q2": 10},
   "kept": ["Microsoft Tech Community blog ‘Power stabilization for AI training datacenters’ → kept by title, classed locator (blog describing arXiv 2508.14318)"],
   "dropped": ["Google patent WO2013059111A1 — patent", "Microsoft Research ASPLOS 2024 paper — paper", "Google Cloud blog ‘Enabling 1 MW IT racks …’ — title names no keyword",
               "Enchanted Rock SEC filings — not the operator's own publication", "arXiv papers (10) — papers"]},
}
named_logs = {
 "ERCOT Planning Guide / Protocols / Operating Guide sections": "Resolved to the three documents (G01–G03); headings located by script from section files (PG §9; NP §3, §6; NOG §2). Resource Registration Glossary not named by the seed; not listed.",
 "NERC Large Loads task-force reports and guideline(s)": "Reliability Guideline (G05) = instrument; two white papers (Jul 2025; Mar 2026) = locators (seed).",
 "NERC 2025 large-load alert": "Level 2 Industry Recommendation, Sep 9, 2025 (G06).",
 "PJM large-load additions documents (2025–2026)": "Kept: Board Decisional Letter Jan 16, 2026 (G10); Sept 1, 2026 draft ride-through tariff/manual revisions for LCLs (G11, pending). Dropped: Aug 8, 2025 Board letter launching the CIFP (process launch, no load-behaviour content by title/scope); Manual 19 load-forecast revisions (forecasting); Expedited Interconnection Track tariff sheets (generation track); 2026 Large Load Forecast Adjustment Methodology (forecasting); Board letter on Reliability Backstop Procurement (capacity procurement); stakeholder survey/comments (not PJM documents).",
 "Texas PUCT rule(s) implementing SB 6": "§25.194, §25.205, §25.370 (G12–G14); proposed SLLIA, Project 59999 (G15, pending). GRUS petition for a new rule (Item 8) — a third-party petition, not a body proposal; logged, not listed.",
 "FERC order(s) on large-load co-location (2025)": "Dec 18, 2025 order 193 FERC ¶ 61,217 (G16). Feb 20, 2025 show-cause order (190 FERC ¶ 61,115) — procedural order establishing the proceeding; its PDF was not located on ferc.gov in one query; logged, not listed. 2026 orders (EL25-49-002 rehearing; EL26-67…70 large-load show-cause orders) — outside the seed (2025, co-location); logged.",
 "AEP Ohio data-centre tariff (2025)": "Schedule DCT, current issue Aug 28, 2026 (U01). ‘DCT Load Study Letter’, NERC questionnaire, AEP Interconnection Requirements Rev6 (linked from the DCT page) — not the tariff; not listed (not cited in the tariff's keyword clauses).",
 "Dominion Energy Virginia large-load rate schedule (2025)": "SCC Final Order PUR-2025-00058 establishing Rate Schedule GS-5 (U02); schedule text not on utility site.",
 "Georgia Power large-load rules (2025)": "Rules, Regulations and Rate Schedules for Electric Service, current PDF (U03).",
 "Regulation (EU) 2016/1388 and ENTSO-E implementation guidance": "E01; E02 (14 current IGDs whose Code(s) field names the DCC; RfG/HVDC-only IGDs and archive versions dropped: Monitoring after operational notification, Automatic connection/reconnection and admissible active power ramp (RfG only), CBA zip, Embedded HVDC, Fault current contribution, FSM, HVDC default parameters, HVDC interactions, LFSM, Max admissible P reduction, Synthetic inertia, Reactive power control modes, Reactive power at low/zero power, Selection of national MW boundary, Type A generators); DCC Implementation Guideline 2013 (pre-adoption, superseded) dropped. Pending: ACER Rec 01/2025 Annex 4a (E03); ACER Rec 03/2023 Annex 2 superseded by it (logged).",
 "GB Grid Code Connection Conditions": "E04 (Issue 6 Rev 47 complete text; Rev 48 changes General Conditions only). Digitalised Grid Code (dcm.neso.energy) is JS-rendered.",
 "VDE-AR-N 4120 and 4130": "E05 (4120, edition note), E06 (pending draft amendment E 4120/A1:2026-05), E07 (4130 + A1). E VDE-AR-N 4120:2024-11 draft — superseded by the 2026-12 edition (logged, not listed). 4130 revision draft announced for Oct 2026 — no document located (logged).",
 "D-A-CH-CZ Technical Rules": "Four parts E08–E11 (VDE FNN download pages; publisher Oesterreichs Energie). Older 2007 Kompendium and 2012 HV supplement superseded; dropped.",
 "IEC TR 61000-3-7; IEC 61000-4-30; IEC 61000-4-15; IEEE 519; IEEE 1453; EN 50160": "Q01–Q06 at current editions. IEEE P519 revision project (PAR only, no draft public) logged, not listed.",
 "OCP Open Rack V3 base, power-shelf, BBU; 800 VDC (Mt Diablo)": "V01–V08. Dropped: ORv3 48V PSU spec, ORv3 HPR V2 12kW PSU (PSU module specs, not named), Diablo 400 v0.5.2 (superseded by v0.7.0), ORv3 base V1.0, Meta/Google ORv3 frame implementations (frame variants), connectors/cables/PMM/PMI specs (not power-shelf/BBU).",
 "NVIDIA GB200/GB300 NVL72 power-smoothing and power-capping documentation; 800 VDC white paper": "V11–V14. Dropped: DGX GB200/GB300 NVL72 release notes (release notes); DGX GB Rack Scale Systems User Guide (no power-smoothing/capping headings); Mission Control PRS FAQ (rack power budgeting). 800 VDC white paper 2 → locator (seed).",
}

deviations = [
 "DC2-S1. Identifier key in masked citing sentences. Masking every digit makes document identifiers unreadable, so the scripts replaced recognised document identifiers (IEC/IEEE/EN numbers, section numbers, docket numbers) by tokens [Rk] before masking and printed the identifiers separately as a key. No value, window or allowance is in the key. Locator sentences in locator.py/locator2.py were fully masked without a key; identifiers there were resolved from the reference list.",
 "DC2-S2. WebSearch summaries exposed limit content. The WebSearch tool returns a model-written summary with each result list, and on seven queries that summary stated limit-type content I did not request: (a) PJM draft LCL voltage/frequency ride-through table values and a post-fault recovery value (PJM query, G11 — ride-through, pending draft); (b) a remark about the percentile basis on which IEEE 519 limits are applied (IEEE Xplore query, Q04; the percentiles are not repeated here); (c) an OCP Open Data Center spec statement on generator support of ML load fluctuation with a percentage of generator rating, a recurrence interval and a duration, plus news-reported ride-through durations for Ireland and Finland and a peak-reduction figure (OCP query; V10 is affected); (d) a statement that BESS is required for load smoothing in every DC building (OCP query; no value); (e) an NVIDIA release-note power-floor setting (percentages) and an energy-storage-per-GPU figure (NVIDIA query; V11–V13 vendor capability); (f) a third-party paper's paraphrase of an AESO point-of-connection ramp-rate limit for transmission-connected data centres and a NERC-reported measured ramp (Google/Meta query; AESO is not on the list — its guide was later met through the S1 test via the OCP LVDC white paper and failed test 2 because that citation is a RoCoF ride-through row, so AESO was not added); (g) a flicker frequency-range remark for IEC 61000-3-3 (CENELEC query). Also, my own ERCOT listing parser printed the title of NPRR239 (2010, wind-generation ramp limitation, with its value in the title) before the masking regex was fixed; it is not a DC2 instrument. Dollar/price figures also appeared in some summaries and catalogue pages; none is used. None of these affected an inclusion decision.",
 "DC2-S3. Clause first lines shown while locating headings. In a few large documents the heading-locating step printed the first line of clauses (truncated to ≤ 75–160 characters; digits masked when limit-like): ERCOT PG §9.1 opening paragraphs; EU DCC lines containing ‘Article N’ (before the title-only script); GB Grid Code CC.6.1.x / ECC.6.1.x clause heads; PUCT §25.194 subsection lines from one unfiltered grep (procedural day-counts and dollar amounts, no power-variation limit). The D-A-CH-CZ Part A normative-references clause (2.11) was printed unmasked as the protocol allows; it contains equipment current ratings and a frequency band that are applicability ranges of the cited standards, not limits.",
 "DC2-S4. Keyword-headed clause scoping was done by script: nearest preceding numbered heading (or the document's TOC headings; chapter level for the NERC guideline). For revision-request reports, PUCT rules, tariffs, the NERC alert, draft standards and the PJM letter/draft, the whole document was scanned, because their headings rarely carry the keywords or the documents are short.",
 "DC2-S5. Locator display filter. All citing sentences were counted. Displayed were those mentioning ramp, step change, swing, oscillation, flicker, RVC or fluctuation together with a limit or requirement word, plus reference entries naming instrument-type documents. Full reference lists were printed for the two arXiv papers.",
 "DC2-S6. Hosts outside the S4 list. These were used for locators, landing pages or pending items: nysrc.org (copy of the NERC gap white paper; nerc.com page is JS-rendered and no nerc.com PDF URL was found); acer.europa.eu (E03 pending); ena-eng.org (Q09, ENA's own catalogue); vde-verlag.de (VDE's own publisher; E05, E07 catalogue pages); NVIDIA's asset CDN linked from nvidia.com (V14); utility and commission sites (aepohio.com, dominionenergy.com, georgiapower.com, scc.virginia.gov, interchange/ftp.puc.texas.gov) as the ‘utility's own tariff pages and state commission docket’; EPRI, arXiv and Microsoft Tech Community for locators only.",
 "DC2-S7. EN 61000-3-3 and EN 61000-3-11 were cited as EN documents. CENELEC catalogue pages need a session checksum (HTTP 500 / ‘session state protection violation’ without one), so Q07 and Q08 point to the IEC originals' webstore pages. Raters should treat the EN and IEC texts as one instrument. The cited EN 61000-3-11:2000 edition is superseded; the current IEC edition is 2017.",
 "DC2-S8. Approved ERCOT revision requests already in the current Planning Guide, Protocols or Operating Guide were resolved to that document (G01–G03), not listed separately, to avoid double counting. PGRR144 (approved, not yet effective) is listed separately (G04).",
 "DC2-S9. Grouping. The NERC Project 2026-02 drafts are listed per standard (G07–G09). The 14 DCC-relevant ENTSO-E IGDs are one instrument (E02).",
 "DC2-S10. The Dominion GS-5 rate schedule text was not found on dominionenergy.com. The landing page is the SCC Final Order (state commission docket), and access is recorded as partial.",
 "DC2-S11. The IEC preview PDFs (which carry scope, normative references and the TOC) returned 403 at the catalogue preview endpoint; the legacy path redirected to the product list. No other headers or routes were tried. Q01–Q03 are recorded as abstract-only, ‘references not accessible’.",
 "DC2-S12. Classification of seed-found white papers and blogs. NVIDIA 800 VDC white paper 2, the OCP Open Data Center for AI white paper, the OCP DCF LVDC white paper and the Microsoft blog are locators (seed). NVIDIA 800 VDC white paper 1 is listed as an instrument (V14) because the seed names it. Raters may record ‘no requirement’.",
 "DC2-S13. ERCOT NPRR999 (DC Tie Ramp Limitations) has no date on the listing page. It was dropped on title (DC ties, not large load) and RR-number sequence, without opening the issue page.",
 "DC2-S14. Post-fault active power recovery, RoCoF and other ride-through rows in locators were judged ‘ride-through’, not ‘real-power variation’, so S3 test 2 fails for the documents they cite (AESO, EirGrid/SONI, Energinet, RTE, Fingrid, SPP, IESO, ATC). The reviewer may revisit this judgement; it decided no inclusion except by exclusion.",
]

s3 = []
for it in inst:
    s3.append(dict(instrument_id=it["instrument_id"], references=it["references"]))

fetchlog = [json.loads(l) for l in open(os.path.join(OUT, "fetchlog.jsonl"))]
screen = dict(study="DC2", screener="fresh-context screener sub-agent", date="2026-11-10",
              protocol="results/DC2/DC2_preregistration.md §2–§3", instruments=inst, locators=locators, query_log=[dict(tool=a, query=b, hits=c, note=d) for a, b, c, d in queries],
              any_seed_resolution=any_logs, named_seed_resolution=named_logs,
              s3_additions=[
                dict(added="Q07 IEC 61000-3-3 (cited as EN 61000-3-3:2013)", citing="E08 D-A-CH-CZ Teil A", clause="2.11 Normative Bezüge", sentence_masked="Emissionsgrenzwerte für Harmonische und Spannungsänderungen/Flicker für Einzelgeräte mit einem Bemessungsstrom bis ## A bzw. im Bereich zwischen ## A und ## A sind in [EN #####-#-#] bzw. [EN #####-#-#] sowie [EN #####-#-##] und [EN #####-#-##] aufgeführt.", tests=dict(t1="pass: power-quality standard limiting equipment voltage changes/flicker", t2="pass: cited as the source of voltage-change/flicker emission limits", t3="pass: IEC webstore landing (EN page needs CENELEC session checksum)")),
                dict(added="Q08 IEC 61000-3-11 (cited as EN 61000-3-11:2000)", citing="E08 D-A-CH-CZ Teil A", clause="2.11 Normative Bezüge", sentence_masked="(same sentence)", tests=dict(t1="pass", t2="pass", t3="pass (IEC webstore)")),
                dict(added="Q09 ENA EREC P28 Issue 2", citing="E04 GB Grid Code", clause="CC.6.1.7 / ECC.6.1.7 (Table CC.6.1.7(b) / ECC.6.1.7(b) planning levels for flicker); also CC data clause", sentence_masked="Table CC.#.#.#(b) — Planning levels for flicker The values and figures referred to in this paragraph CC.#.#.# are derived from [EREC P##] Issue #. | Details of all loads which may cause Demand fluctuations greater than those permitted under [EREC P##] Issue #, Stage # at a Point of Common Coupling …", tests=dict(t1="pass: ENA engineering recommendation defining planning levels for voltage fluctuations from customer equipment", t2="pass: named as the source of the flicker planning levels and of permitted demand fluctuations", t3="pass: ENA document catalogue landing (ena-eng.org)")),
              ],
              s3_failed_or_already_listed=[
                "E04: IEC 61400-21 (flicker coefficient data for power park units) — t2 fail (data definition, generators)",
                "E08 2.11: EN 61000-2-2, EN 61000-2-12 — t2 fail (compatibility levels of the network, not a limit on a load); IEC TR 61000-3-6, IEC TR 61000-3-13, EN 61000-3-2, EN 61000-3-12 — t2 fail (harmonics/unbalance); IEC TR 61000-3-14, IEC TR 61000-3-15 — t2 fail (further assessment procedures, TR status); EN 61000-4-7 — t2 fail (measurement); EN 61000-4-30 → already listed (Q02); EN 61000-4-15 → already listed (Q03; ‘Grenzwerte basieren auf … nach [EN 61000-4-15]’); EN 50160 → already listed (Q06); IEC TR 61000-3-7 → already listed (Q01); IEC 60725 — t2 fail (reference impedance)",
                "E09–E11 Normenverzeichnis: same documents → already listed or failed as above",
                "Q06 EN 50160 catalogue normative reference: EN 61000-4-30:2015 → already listed (Q02)",
                "U03: IEEE 1547-2018 — t2 fail (customer generation interconnection)",
                "V06: IEC 61000-4-34 — t2 fail (dips/ride-through test method)",
                "V09: IEEE 1453 → already listed (Q05); IEEE 519 → already listed (Q04); NOGRR 282 → already listed (in G03); ESIG ‘Large Load Performance Requirements’ report — t1 fail (industry report) and t2 fail; IEEE white paper ‘Review of industry efforts and standards of grid readiness for data center deployment’ — t1 fail (white paper); IEEE 1566 — t2 fail (VFD ride-through)",
                "G09: IEEE C37.111 — t2 fail (data file format)",
                "G05: Primary Frequency Control Reliability Guideline; TPL-001-5 — t2 fail",
                "Locator arXiv 2508.14318: IEC 61000-3-3 → passes, already listed (Q07)",
                "Locator OCP DCF LVDC white paper: AESO guide, EirGrid/SONI FRT papers, Energinet TR 3.4.3, RTE DTR Art. 8.3.5, Fingrid technical requirements for large demand facilities, SPP HILL ride-through requirements, IESO LCL technical requirements, ATC planning criteria — t2 fail (ride-through / post-fault recovery / RoCoF rows); IEC 61000-3-11 → already listed (Q08); Regulation (EU) 2016/1388 → already listed (E01)",
              ],
              references_not_accessible=["E05","E06","E07","Q01","Q02","Q03","Q04","Q05","EPRI 3002034099","EPRI 3002036744","EPRI 3002036753","EPRI 3002036755","EPRI 3002037178"],
              deviations=deviations, fetch_log=fetchlog)
json.dump(screen, open(os.path.join(OUT, "DC2_screen.json"), "w"), indent=1, ensure_ascii=False)

# ---------------- Markdown ----------------
def esc(s): return str(s).replace("|", "\\|").replace("\n", " ")
L = []
L.append("# DC2 — fixed instrument list (screener output, before any limit is read)\n")
L.append("Built by the DC2 screener (a fresh-context sub-agent, not a rater) on 2026-11-10, under `DC2_preregistration.md` §2–§3. Every decision, query, hit count and URL is in `DC2_screen.json`. The screen read only titles, scope and applicability clauses, headings, normative-reference clauses, and masked citing sentences. Deviation DC2-S2 lists every place where limit-type content was nevertheless shown.\n")
cnt = {}
for it in inst:
    g = it["group"]; o = "added" if it["origin"].startswith("added") else "seed"
    cnt.setdefault(g, {"seed": 0, "added": 0})[o] += 1
acc = {"full": 0, "partial": 0, "none": 0}
for it in inst: acc[it["access"]] += 1
L.append("**Counts.** " + "; ".join("%s: %d seed + %d added" % (g, cnt[g]["seed"], cnt[g]["added"]) for g in "GUEQV") +
         ". Total %d instruments (%d seed, %d added). Access: full %d, partial %d, none %d. Pending (status as printed): G07, G08, G09, G11, G15, E03, E06.\n" %
         (len(inst), sum(c["seed"] for c in cnt.values()), sum(c["added"] for c in cnt.values()), acc["full"], acc["partial"], acc["none"]))
L.append("## 1. Instruments\n")
L.append("| instrument_id | group | identifier | exact title | issuing body | jurisdiction | landing URL | scope (≤ 3 sentences, quoted) | section headings located (raters' starting points) | access | status | origin | references |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for it in inst:
    L.append("| " + " | ".join(esc(it[k]) for k in ["instrument_id","group","identifier","title","issuing_body","jurisdiction","landing_url","scope","headings","access","status","origin","references"]) + " |")
L.append("\nGroups: G = US grid / ISO / regulator; U = US utility large-load clauses; E = EU / UK / DE; Q = power quality; V = operator / vendor rack and facility. Additions sit in the group of their own type (Q).\n")
L.append("## 2. Locators (not rated)\n")
L.append("| locator | title | URL | type | citing sentences read | reference list | candidates and outcome | added |")
L.append("|---|---|---|---|---|---|---|---|")
for l in locators:
    L.append("| " + " | ".join(esc(l[k]) for k in ["name","title","url","kind","citing","refs","candidates","added"]) + " |")
L.append("\n## 3. Per-seed resolution log\n")
L.append("### 3a. Named seeds\n")
for k, v in named_logs.items(): L.append("- **%s.** %s" % (k, v))
L.append("\n### 3b. ‘Any …’ seeds (queries, hit counts, kept and dropped titles)\n")
for k, v in any_logs.items():
    L.append("**%s**\n" % k)
    L.append("- Queries: " + "; ".join(v.get("queries", [])))
    if v.get("hit_counts"): L.append("- Hit counts: " + "; ".join("%s = %s" % (a, b) for a, b in v["hit_counts"].items()))
    L.append("- Kept:" + ("" if v["kept"] else " none"))
    for x in v["kept"]: L.append("  - " + x)
    L.append("- Dropped:")
    for x in v["dropped"]: L.append("  - " + x)
    L.append("")
L.append("### 3c. Query log (web searches and listing pages)\n")
L.append("| tool | query / page | hits | note |"); L.append("|---|---|---|---|")
for a, b, c, d in queries: L.append("| %s | %s | %s | %s |" % (esc(a), esc(b), esc(c), esc(d)))
L.append("\nThe fetch log (%d requests, URL and HTTP status of each) is in `DC2_screen.json` → `fetch_log`.\n" % len(fetchlog))
L.append("## 4. S3 hit counts\n")
L.append("Columns: citations read; passing tests 1, 2 and 3; added; already listed. ‘Not accessible’ means no text or free preview with references could be reached by an allowed route.\n")
L.append("| instrument / locator | citations read | pass 1·2·3 | added | already listed | note |"); L.append("|---|---|---|---|---|---|")
s3rows = {
 "G01":(34,0,0,0,""),"G02":(13,0,0,0,""),"G03":(7,0,0,0,""),"G04":(35,0,0,0,""),"G05":(6,0,0,0,"chapter-scoped"),"G06":(4,0,0,0,""),
 "G07":(29,0,0,0,"pending draft"),"G08":(24,0,0,0,"pending draft"),"G09":(20,0,0,0,"pending draft"),"G10":(0,0,0,0,""),"G11":(2,0,0,0,"pending draft"),
 "G12":(36,0,0,0,""),"G13":(24,0,0,0,""),"G14":(11,0,0,0,""),"G15":(10,0,0,0,"pending"),"G16":(0,0,0,0,"no keyword-headed clause"),
 "U01":(14,0,0,0,""),"U02":(0,0,0,0,"no keyword-headed clause"),"U03":(9,0,0,0,""),
 "E01":(0,0,0,0,"Art. 20 has no citing sentence"),"E02":(4,0,0,0,"14 IGDs"),"E03":(0,0,0,0,"pending"),"E04":(8,1,1,0,"EREC P28 added"),
 "E05":("—","—","—","—","references not accessible"),"E06":("—","—","—","—","references not accessible"),"E07":("—","—","—","—","references not accessible"),
 "E08":(30,4,2,2,"EN 61000-3-3, EN 61000-3-11 added; IEC TR 61000-3-7, EN 61000-4-15 already listed"),"E09":(11,3,0,3,""),"E10":(8,2,0,2,""),"E11":(5,1,0,1,""),
 "Q01":("—","—","—","—","references not accessible"),"Q02":("—","—","—","—","references not accessible"),"Q03":("—","—","—","—","references not accessible"),
 "Q04":("—","—","—","—","references not accessible"),"Q05":("—","—","—","—","references not accessible"),"Q06":(1,0,0,1,"EN 61000-4-30 (cited as normative reference; measurement — counted already listed)"),
 "Q07":("n/a","n/a","n/a","n/a","addition — one level only"),"Q08":("n/a","n/a","n/a","n/a","addition — one level only"),"Q09":("n/a","n/a","n/a","n/a","addition — one level only"),
 "V01":(0,0,0,0,""),"V02":(0,0,0,0,""),"V03":(0,0,0,0,""),"V04":(0,0,0,0,""),"V05":(0,0,0,0,""),"V06":(1,0,0,0,""),"V07":(0,0,0,0,""),"V08":(0,0,0,0,""),
 "V09":(19,1,0,1,"IEEE 1453 already listed"),"V10":(0,0,0,0,""),"V11":(0,0,0,0,""),"V12":(0,0,0,0,""),"V13":(3,0,0,0,""),"V14":(0,0,0,0,""),
}
for k, (a, b, c, d, e) in s3rows.items(): L.append("| %s | %s | %s | %s | %s | %s |" % (k, a, b, c, d, esc(e)))
for l in locators:
    pa = 1 if "arXiv 2508" in l["name"] else 0
    al = 1 if ("arXiv 2508" in l["name"] or "LVDC" in l["name"]) else 0
    L.append("| %s | %s | %s | 0 | %s | %s |" % (esc(l["name"]), esc(l["citing"]), pa, al, "" if not al else ("IEC 61000-3-3" if pa else "IEC 61000-3-11, Reg. 2016/1388")))
L.append("\n## 5. Addition log\n")
for a in screen["s3_additions"]:
    L.append("- **%s** — cited by %s, clause %s. Masked citing sentence: “%s”. Tests: 1 %s; 2 %s; 3 %s." % (a["added"], a["citing"], a["clause"], a["sentence_masked"], a["tests"]["t1"], a["tests"]["t2"], a["tests"]["t3"]))
L.append("\nCitations read that did not add (failed a test, or already listed):\n")
for x in screen["s3_failed_or_already_listed"]: L.append("- " + x)
L.append("\nReferences not accessible: " + ", ".join(screen["references_not_accessible"]) + ".\n")
L.append("## 6. Screener deviations\n")
for d in deviations: L.append("- " + d)
L.append("")
open(os.path.join(OUT, "DC2_instruments.md"), "w").write("\n".join(L))
print("instruments", len(inst), cnt, acc)
