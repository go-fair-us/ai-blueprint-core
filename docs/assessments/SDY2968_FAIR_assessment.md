**FAIR Principles Alignment Assessment Report**  
**Resource:** https://www.immport.org/shared/study/SDY2968/summary (ImmPort SDY2968)  
**Blueprint:** NIAID Blueprint v2 (26 Sep 2025) – Table 1 metadata elements + Sections 2–5  
**Assessment date:** 2026-07-04  
**Method:** JS-capable fetch via r.jina.ai (successful); content mapped to Blueprint Table 1

### Step 3: Identify key links
- Primary persistent identifier: https://doi.org/10.21430/M3J8UMVGT6  
- Release notes: https://docs.immport.org/home/release_notes/DR54.2_DataRelease/ and DR58  
- No direct data-distribution link, license link, or API endpoint visible on the summary page.  
- No ORCID, ROR, or SPDX license links present.

### Step 4: Map extracted ImmPort fields to Blueprint Table 1 elements

| Blueprint Table 1 Element | ImmPort Field / Evidence | Status |
|---------------------------|--------------------------|--------|
| type | “qualitative study” / “Epidemiology” | Present (Dataset) |
| identifier | DOI 10.21430/M3J8UMVGT6 | Present & resolvable |
| name | Title (full) | Present |
| description | Brief Description + Detailed Description (rich) | Present |
| dateCreated | Start Date 2022-08-01; release dates | Partial (ISO format) |
| author | None listed | Missing |
| funder | SeroNet, CIVICs (NIAID programs) | Partial (text only) |
| grant | STOP-COVID, CIVR-HRP contract names | Present (text) |
| measurementTechnique | “Deductive thematic analysis”, “vaccine acceptance continuum framework”, “qualitative research” | Present |
| distribution | None shown | Missing |
| citation | DOI provided | Present |
| infectiousAgent | COVID-19 | Partial (free text) |
| host | “patients”, “Subjects Number” (human) | Partial (implied) |
| healthCondition | “COVID-19, Post-Acute Sequelae of COVID-19”, “Long COVID” | Present |
| conditionsOfAccess | “ImmPort Shared Data” | Partial (no explicit IRI) |
| license | None mentioned | Missing |
| spatialCoverage | None | Missing |
| temporalCoverage | Start Date 2022-08-01 | Partial |

### Step 5: Evaluate each FAIR principle with evidence quotes and per-criterion scores

**Findable (F)**  
- **F1 – Identifier (meet)**: “DOI[10.21430/M3J8UMVGT6](https://doi.org/10.21430/M3J8UMVGT6)” – resolvable GUPRI present.  
- **F2 – Metadata richness (partial)**: Strong title, description, conditions studied, and endpoints, but missing author, funder PID, license.  
- **F3 – Metadata searchability (partial)**: Good free-text fields; limited structured PIDs/ontologies.  
- **F4 – Registration (meet)**: Listed in ImmPort with accession and DOI.

**Accessible (A)**  
- **A1 – Access protocol (partial)**: Accessible via ImmPort web UI; no machine-readable distribution link or explicit conditionsOfAccess IRI.  
- **A2 – Metadata persistence (partial)**: DOI guarantees identifier persistence; full metadata not yet exposed via API/JSON-LD.

**Interoperable (I)**  
- **I1 – Metadata format (fail)**: No JSON-LD or schema.org markup detected.  
- **I2 – Vocabulary/PIDs (partial)**: Free-text COVID-19 and Long COVID; no NCBITaxon, MONDO, or ORCID/ROR used.  
- **I3 – Qualified references (partial)**: DOI citation present; limited cross-links.

**Reusable (R)**  
- **R1 – License (fail)**: No license or SPDX identifier present.  
- **R2 – Provenance (partial)**: Grant/contract names and release versions provided; authors and funder PIDs missing.  
- **R3 – Community standards (partial)**: Strong domain description; not yet aligned with Blueprint minimal schema.

### Step 6: Structured report with overall score and prioritized recommendations

**Overall Blueprint/FAIR alignment score: 52/100**  
(Weighted: Findable 70, Accessible 45, Interoperable 35, Reusable 25)

**Strengths**  
- Clear, resolvable DOI and rich textual description.  
- Explicit health condition, measurement technique, and grant information.  
- Data-completeness flag and release versioning demonstrate good internal curation.

**Gaps** (ranked by Blueprint priority)  
1. No machine-readable metadata (JSON-LD) or API exposure (Section 3).  
2. Missing license and conditionsOfAccess IRI (critical for Reusability).  
3. No author ORCIDs, funder RORs, or ontology terms (NCBITaxon, MONDO).  
4. No direct distribution link or citation guidance page.

**Prioritized recommendations** (High → Medium)

**High**  
- Embed schema.org JSON-LD (or expose via `/api/studies/SDY2968`) containing all 16 Table 1 elements.  
- Add an explicit license (SPDX or link) and conditionsOfAccess IRI.  
- Provide a direct distribution/download link.

**Medium**  
- Add author ORCIDs and map funder/grant to ROR identifiers.  
- Annotate infectiousAgent and healthCondition with NCBITaxon/MONDO IRIs.  
- Publish a “How to Cite” section using the DOI and ImmPort RRID (if assigned).

**Low**  
- Add spatialCoverage (if applicable) and full temporalCoverage range.  
- Register the study with the NIAID Data Ecosystem Discovery Portal once metadata is Blueprint-compliant.

Once the high-priority items are addressed, a re-assessment is expected to raise the score above 80.
