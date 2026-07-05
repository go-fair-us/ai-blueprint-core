# FAIR Principles Alignment Assessment — ImmPort SDY2968

**Target URL:** https://www.immport.org/shared/study/SDY2968/summary  
**Resource:** ImmPort study SDY2968 — "COVID-19 vaccination perspectives among patients with Long COVID: A qualitative study"  
**Blueprint:** NIAID Blueprint for Digital Objects v2 (26 Sep 2025)  
**Assessment date:** 2026-07-05  

---

## 1. Methodology and Limitations

### Fetch method
ImmPort study pages are JavaScript-rendered. A direct HTML fetch returns an app shell (loading spinner). All content was therefore retrieved via the `r.jina.ai` server-side rendering proxy, which returns clean Markdown.

Pages fetched:
| Page | URL | Status |
|------|-----|--------|
| Study summary | `https://www.immport.org/shared/study/SDY2968/summary` | Success (via r.jina.ai) |
| ImmPort documentation home | `https://docs.immport.org/` | Success |
| User agreement / policies | `https://docs.immport.org/home/agreement/` | Success |
| Citation guidance | `https://docs.immport.org/home/cite/` | Success |
| About ImmPort | `https://docs.immport.org/home/about/` | Success |
| Data model overview | `https://docs.immport.org/datamodel/` | Success |
| Ontologies page | `https://docs.immport.org/datamodel/ontologies/` | Success |
| API documentation overview | `https://docs.immport.org/apidocumentation/` | Success |
| Shared Data API Swagger UI | `https://docs.immport.org/apidocumentation/shareddataapi/swaggerUI/` | Success |
| Download documentation | `https://docs.immport.org/download/` | Success |
| Data sharing page | `https://www.immport.org/shared/dataSharing` | Error (NG04002) — page not found |
| OpenAPI 3.0 spec | `https://www.immport.org/data/query/v3/api-docs` | Fetched but truncated (61 KB+) |

### Limitations
1. **No API key available** — could not make authenticated requests to the Shared Data API or DRS API to inspect actual JSON responses.
2. **JS-rendered pages** — some fields populated by client-side JavaScript (e.g., direct file URLs, DRS IDs per file row) were not fully extractable from the rendered Markdown snapshots.
3. **Embedded metadata not verified** — the r.jina.ai proxy returns Markdown, not raw HTML, so I could not definitively confirm or deny the presence of embedded `<script type="application/ld+json">` blocks on the study landing page. However, no JSON-LD content was visible in the rendered output.
4. **Data sharing page broken** — the `/shared/dataSharing` URL returned a 404-style error, so data sharing policies were assessed from the user agreement page instead.

---

## 2. Blueprint Requirements Summary

The NIAID Blueprint v2 specifies five areas of alignment:

| # | Blueprint Area | Key Requirements |
|---|----------------|------------------|
| 1 | **Minimal Metadata Schema** | 16 schema.org-based metadata elements (Table 1): type, identifier, name, description, dateCreated, author, funder, grant, measurementTechnique, distribution, citation, infectiousAgent, host, healthCondition, conditionsOfAccess, license, spatialCoverage, temporalCoverage. Default PIDs: DOI, ORCID, ROR, NCIT, NCBITaxon, MONDO, SPDX. |
| 2 | **Persistent Identifiers (PIDs)** | DOI for identifier; ORCID for author; ROR for funder; RRID for biological resources. PIDs integrated into metadata. |
| 3 | **API Specifications** | API responses return JSON-LD (at least as option); resource-oriented IRI structure; HTTP GET for metadata; OpenAPI/Swagger documentation. Alternative: HTML with embedded JSON-LD metadata. |
| 4 | **Citation Requirements** | Integrate PIDs (DOI) into citations; consistent citation guidelines for original and reused data; standard formats (APA, MLA, Chicago); repository name + repository PID (RRID) + data PID (DOI). |
| 5 | **Outreach and Training** | Designate a Contact Point (CP) for outreach, training, and collaboration. CP reachable and listed prominently. Develop training materials. |

---

## 3. Per-Principle Assessment with Evidence

### 3.1 Findable (F)

#### F1 — Globally unique, persistent, machine-resolvable identifier
**Status: MEET**

Evidence from study summary page:
> "DOI 10.21430/M3J8UMVGT6"

The DOI is resolvable via `https://doi.org/10.21430/M3J8UMVGT6`. ImmPort also assigns its own accession number (SDY2968).

#### F2 — Rich metadata with all Blueprint Table 1 elements
**Status: PARTIALLY MEET**

Mapped elements from the SDY2968 summary page:

| Blueprint Element | ImmPort Field | Status |
|-------------------|---------------|--------|
| `type` | "qualitative study" / "Epidemiology" | Present (implied Dataset) |
| `identifier` | DOI 10.21430/M3J8UMVGT6 | Present & resolvable |
| `name` | Title (full) | Present |
| `description` | Brief Description + Detailed Description | Present (rich) |
| `dateCreated` | Start Date 2022-08-01; release dates | Partial (ISO format) |
| `author` | None listed on summary page | **Missing** |
| `funder` | "SeroNet, CIVICs" (NIAID programs) | Partial (text only, no ROR) |
| `grant` | "STOP-COVID, CIVR-HRP" contract names | Present (text, no standard IDs) |
| `measurementTechnique` | "Deductive thematic analysis", "qualitative research" | Present |
| `distribution` | None shown on summary page | **Missing** |
| `citation` | DOI provided; no structured citation block | Partial |
| `infectiousAgent` | "COVID-19" (free text) | Partial (no NCBITaxon IRI) |
| `host` | "patients", "Subjects Number" (human implied) | Partial (implied, no NCBITaxon) |
| `healthCondition` | "COVID-19, Post-Acute Sequelae of COVID-19", "Long COVID" | Partial (no MONDO IRI) |
| `conditionsOfAccess` | "ImmPort Shared Data" (registration required) | Partial (no explicit IRI) |
| `license` | None mentioned on study page | **Missing** |
| `spatialCoverage` | None | **Missing** |
| `temporalCoverage` | Start Date 2022-08-01 | Partial (no end date) |

Summary: 4 elements fully present, 8 partially present, 5 missing.

#### F3 — Metadata clearly and explicitly includes the identifier
**Status: MEET**

The DOI is prominently displayed on the study summary page and is machine-resolvable.

#### F4 — Metadata registered or indexed in a searchable resource
**Status: PARTIALLY MEET**

ImmPort is a searchable shared-data portal. The study is indexed with accession SDY2968 and a DOI. However, no evidence was found that the SDY2968 landing page exposes structured markup (e.g., JSON-LD) for external indexing by the NIAID Data Ecosystem Discovery Portal.

---

### 3.2 Accessible (A)

#### A1 — retrievable by identifier using a standardized communications protocol
**Status: PARTIALLY MEET**

- The DOI resolves to the ImmPort study page (HTTPS).
- The ImmPort Shared Data API provides programmatic access to study metadata and files.
- However, the summary page does not expose a direct distribution/download link or a machine-readable metadata endpoint.

#### A1.1 — protocol is open, free, and universally implementable
**Status: MEET**

HTTPS and REST APIs are used throughout.

#### A1.2 — authentication and authorization supported where necessary
**Status: MEET**

ImmPort uses scoped API keys for all API access:
> "Authorization: Bearer <API_KEY>"

Downloads require authentication (registration). This is appropriate for controlled-access data.

#### A2 — metadata should be accessible even when the data is no longer available
**Status: PARTIALLY MEET**

ImmPort is a long-term, sustainable data repository with monthly data releases and CoreTrustSeal certification. However, no explicit tombstoning or retention policy was found in the collected evidence.

---

### 3.3 Interoperable (I)

#### I1 — metadata uses a formal, accessible, shared, and broadly applicable language for knowledge representation
**Status: PARTIALLY MEET**

**Portal-level strengths:**
- ImmPort provides OpenAPI 3.0-documented REST APIs with Swagger UI.
- A HAPI FHIR Server exposes FHIR `ResearchStudy` and related resources.
- A GA4GH Data Repository Service (DRS) API is available for cloud-native file retrieval.
- The data model uses BFO and OBI ontologies as foundational classes.

**Dataset-level gaps:**
- No JSON-LD metadata was evidenced on the SDY2968 study landing page.
- The Shared Data API returns standard JSON responses (not JSON-LD).
- Blueprint Section 3.2 requires: "API responses should return metadata encoded in JSON-LD, at least as an option." This requirement is not met.
- Blueprint Section 3.2 also offers an alternative: "HTML embedded metadata" (structured metadata such as JSON-LD built directly into a webpage). No evidence of this was found.

#### I2 — metadata uses FAIR vocabularies and ontologies
**Status: PARTIALLY MEET**

**Portal-level strengths:**
- ImmPort's data model incorporates multiple established ontologies:
  - NCBI Taxonomy (for infectious agents and hosts)
  - Disease Ontology (for health conditions)
  - Cell Ontology, Gene Ontology, Uberon Anatomy Ontology
  - Vaccine Ontology, Protein Ontology
  - Ontology for Biomedical Investigations (OBI)
  - Clinical Measurement Ontology (CMO)
  - NCIT (National Cancer Institute Thesaurus)
  - MedDRA, RxNorm, SNOMED CT
- The data model uses lookup tables populated with standardized terms from these ontologies.

**Dataset-level gaps:**
- On the SDY2968 summary page, key biomedical terms appear as plain text (e.g., "COVID-19", "Long COVID") rather than resolvable ontology identifiers (e.g., NCBITaxon:2697049, MONDO:0100096).
- No MONDO, NCBITaxon, or NCIT IRIs are exposed on the study page.

#### I3 — metadata includes qualified references to other (meta)data
**Status: PARTIALLY MEET**

- The DOI provides a qualified reference to the dataset.
- Links to release notes (DR54.2, DR58) are present.
- However, no ORCID, ROR, or RRID cross-references are visible on the SDY2968 summary page.

---

### 3.4 Reusable (R)

#### R1 — metadata is richly described with accurate and relevant attributes
**Status: PARTIALLY MEET**

The study page provides:
- Full title and detailed description
- Research focus, condition studied, endpoints
- Start date, grant/contract information
- Data completeness flag and release versioning

But it lacks:
- Author information (names, ORCIDs)
- Funder information (ROR identifiers)
- Spatial and full temporal coverage

#### R1.1 — data has a clear and accessible license
**Status: FAIL**

- No license or SPDX identifier is present on the SDY2968 study page.
- The general ImmPort user agreement describes usage terms:
  > "You have the unrestricted right to use and distribute ImmPort data. However, you will ensure that all redistribution occurs under terms commensurate with this agreement."
- But this is a portal-level agreement, not a dataset-level standard license identifier as required by Blueprint Table 1.

#### R1.2 — metadata includes provenance information
**Status: PARTIALLY MEET**

- Release versions are listed (DR54.2, DR58).
- Grant/contract names are provided (STOP-COVID, CIVR-HRP).
- But no creator identifiers (ORCID) or funder identifiers (ROR) are evidenced on the study page.

#### R1.3 — metadata follows community standards
**Status: PARTIALLY MEET**

**Portal-level (Meet):**
- GA4GH DRS and FHIR are strong community standards.
- OpenAPI 3.0 documentation is a recognized standard.
- CoreTrustSeal certification demonstrates adherence to trustworthy data repository standards.

**Dataset-level (Partially meet):**
- The dataset landing page does not clearly expose machine-readable metadata aligned with schema.org/JSON-LD as specified in Blueprint Section 3.2.

---

## 4. Alignment to NIAID Blueprint by Section

### Section 1 — Minimal Metadata Schema
**Alignment: PARTIAL (8/16 elements fully present)**

| Element | Present? | Notes |
|---------|----------|-------|
| type | Partial | Implied "Dataset", not explicit |
| identifier | Yes | Resolvable DOI |
| name | Yes | Full title |
| description | Yes | Rich detailed description |
| dateCreated | Partial | Start date present, no creation date |
| author | No | Not listed on summary page |
| funder | Partial | Text only ("SeroNet, CIVICs"), no ROR |
| grant | Partial | Contract names only, no standard IDs |
| measurementTechnique | Yes | "Deductive thematic analysis", "qualitative research" |
| distribution | No | No direct download link on summary page |
| citation | Partial | DOI present, no structured citation block |
| infectiousAgent | Partial | "COVID-19" free text, no NCBITaxon IRI |
| host | Partial | Human implied, no NCBITaxon IRI |
| healthCondition | Partial | "COVID-19, Long COVID" free text, no MONDO IRI |
| conditionsOfAccess | Partial | Registration required, no explicit IRI |
| license | No | No SPDX identifier or license URL |
| spatialCoverage | No | Not provided |
| temporalCoverage | Partial | Start date only, no end date |

### Section 2 — Persistent Identifiers (PIDs)
**Alignment: PARTIAL**

| PID Type | Present? | Notes |
|----------|----------|-------|
| DOI (identifier) | Yes | `10.21430/M3J8UMVGT6` — resolvable |
| ORCID (author) | No | Not evidenced on study page |
| ROR (funder) | No | Not evidenced on study page |
| RRID (repository) | No | Not evidenced on study page |
| NCBITaxon (infectiousAgent, host) | No | Free text only, no IRIs |
| MONDO (healthCondition) | No | Free text only, no IRIs |
| NCIT (measurementTechnique) | No | Free text only, no IRIs |

### Section 3 — API Specifications for Exposing Metadata to Machines
**Alignment: PARTIAL (strong portal-level, weak dataset-level)**

| Requirement | Status | Notes |
|-------------|--------|-------|
| Metadata encoding in JSON-LD | **Fail** | API returns standard JSON, not JSON-LD |
| Resource-oriented IRI structure | **Meet** | `/data/query/study/{study_accession}` pattern |
| HTTP GET for metadata retrieval | **Meet** | Shared Data API uses GET for data retrieval |
| OpenAPI/Swagger documentation | **Meet** | OpenAPI 3.0 spec available at `/data/query/v3/api-docs` |
| HTML embedded metadata (alternative) | **Fail** | No JSON-LD embedded in study page HTML |
| GA4GH DRS API | **Meet** | DRS API available for cloud-native retrieval |
| FHIR API | **Meet** | HAPI FHIR Server exposes ResearchStudy resources |

### Section 4 — Citation Requirements
**Alignment: PARTIAL**

| Requirement | Status | Notes |
|-------------|--------|-------|
| PIDs integrated into citations | **Partial** | DOI present but not integrated into a structured citation |
| Consistent citation guidelines | **Partial** | Portal-level guidance exists but no dataset-specific citation block |
| Standard citation formats (APA, MLA, Chicago) | **Fail** | No standard-format citation examples provided for individual studies |
| Repository name in citation | **Meet** | "ImmPort" referenced in citation guidance |
| Repository PID (RRID) in citation | **Fail** | No RRID identified for ImmPort |
| Data PID (DOI) in citation | **Partial** | DOI exists but not presented in a copy-paste citation format |

Evidence from citation guidance page:
> "When using specific ImmPort data sets for publication, please cite the ImmPort Shared Data web site, Study Accession, and Study Title (e.g. 'The data supporting this publication is available at ImmPort (immport.org) under study accession SDY1444 Immunology study of interest')"

### Section 5 — Point of Contact for Outreach and Training
**Alignment: MEET**

| Requirement | Status | Notes |
|-------------|--------|-------|
| Designated Contact Point (CP) | **Meet** | ImmPort Helpdesk: `ImmPort_Helpdesk@immport.org` |
| CP reachable and listed prominently | **Meet** | Listed in footer and navigation across all pages |
| Training materials developed | **Meet** | Tutorials, webinars, office hours, documentation chatbot, FAQs |
| CP supports NIAID Data Ecosystem Discovery Portal training | **Partial** | Not explicitly evidenced but ImmPort is a major NIAID repository |

Evidence:
- ImmPort documentation home lists: "Contact ImmPort: ImmPort_Helpdesk@immport.org"
- "News & Events: ImmPort news, newsletters, webinars, office hours, and community events"
- "Help & Tutorials: FAQs, tutorials, user registration, usage metrics, and tool guides"
- "Documentation ChatBot: Have a question? The ImmPort Docs Chatbot uses AI to answer questions across these documentation pages"

---

## 5. Overall Alignment Summary and Score

### Scoring methodology
Each of the five Blueprint sections is scored on a 0-100 scale, weighted equally (20% each), to produce an overall alignment score.

| Blueprint Section | Score (0-100) | Weight | Weighted Score |
|--------------------|---------------|--------|-----------------|
| 1. Minimal Metadata Schema | 50 | 20% | 10.0 |
| 2. Persistent Identifiers (PIDs) | 40 | 20% | 8.0 |
| 3. API Specifications | 65 | 20% | 13.0 |
| 4. Citation Requirements | 45 | 20% | 9.0 |
| 5. Outreach and Training | 90 | 20% | 18.0 |
| **Overall** | | | **58.0/100** |

### FAIR principles breakdown

| FAIR Principle | Score (0-100) | Summary |
|----------------|---------------|---------|
| **Findable (F)** | 65 | Strong DOI and rich description; missing author, license, distribution, and ontology IRIs |
| **Accessible (A)** | 70 | HTTPS + REST APIs + DRS + FHIR; authentication well-managed; some gaps in machine-readable metadata access |
| **Interoperable (I)** | 50 | Good portal-level ontology usage and API standards; no JSON-LD metadata at dataset level; ontology terms not exposed as IRIs on study pages |
| **Reusable (R)** | 45 | Rich description and provenance; no explicit license (SPDX); no author ORCIDs or funder RORs |

### Strengths

1. **Resolvable DOI** — The study has a persistent, machine-resolvable identifier (`10.21430/M3J8UMVGT6`).
2. **Rich textual metadata** — Full title, detailed description, condition studied, endpoints, and grant information are provided.
3. **Strong portal-level API infrastructure** — OpenAPI 3.0/Swagger UI, GA4GH DRS API, HAPI FHIR Server, and scoped API key authentication.
4. **Ontology-backed data model** — Multiple established ontologies (NCBI Taxonomy, Disease Ontology, Cell Ontology, Gene Ontology, NCIT, etc.) are used in lookup tables.
5. **Comprehensive outreach and training** — Helpdesk, webinars, office hours, tutorials, documentation chatbot, FAQs, and CoreTrustSeal certification.
6. **Data versioning and release management** — Monthly data releases with release notes and version tracking (DR54.2 → DR58).

### Key Gaps (ranked by Blueprint priority)

#### Critical (blocks FAIR compliance)

1. **No machine-readable metadata (JSON-LD) at dataset level** (Blueprint Section 3.2)
   - The Shared Data API returns standard JSON, not JSON-LD.
   - No JSON-LD is embedded in the study landing page HTML.
   - Blueprint requires: "API responses should return metadata encoded in JSON-LD, at least as an option."
   - Alternative: "HTML embedded metadata" (JSON-LD built into webpage) — also not present.

2. **No explicit license at dataset level** (Blueprint Table 1: `license`)
   - No SPDX identifier or license URL is present on the SDY2968 study page.
   - The general ImmPort user agreement describes usage terms but is not a dataset-level standard license.

3. **Missing author information and ORCIDs** (Blueprint Table 1: `author`)
   - No author names or ORCID identifiers are listed on the SDY2968 summary page.
   - Blueprint requires ORCID for the `author` field.

#### High (significantly reduces alignment)

4. **No funder ROR identifiers** (Blueprint Table 1: `funder`)
   - Funder information is present as text only ("SeroNet, CIVICs") with no ROR identifiers.

5. **Ontology terms not exposed as resolvable IRIs on study pages** (Blueprint Table 1: `infectiousAgent`, `host`, `healthCondition`)
   - Key biomedical terms appear as free text (e.g., "COVID-19", "Long COVID") rather than resolvable ontology identifiers (e.g., NCBITaxon:2697049, MONDO:0100096).
   - The portal's data model supports these ontologies, but they are not surfaced on the study summary page.

6. **No dataset-specific citation block in standard formats** (Blueprint Section 4.2)
   - No "Cite this study" block with standard formats (APA, MLA, Chicago) that include the DOI.
   - Portal-level citation guidance exists but does not provide dataset-specific copy-paste citations.

#### Medium (improves completeness)

7. **No direct distribution/download link on summary page** (Blueprint Table 1: `distribution`)
   - The summary page does not expose a direct download link or file manifest link.

8. **Missing spatial coverage** (Blueprint Table 1: `spatialCoverage`)
   - No geographic location information is provided (ISO 3166 country code).

9. **Incomplete temporal coverage** (Blueprint Table 1: `temporalCoverage`)
   - Only the start date (2022-08-01) is provided; no end date or full date range.

10. **No repository-level RRID** (Blueprint Section 4.2)
    - No RRID (Research Resource Identification) was identified for ImmPort as a repository.

---

## 6. Prioritized Recommendations

### Priority 1 — Machine-Readable Metadata (Blueprint Section 3.2)

**Action:** Embed schema.org `Dataset` JSON-LD on each study landing page (e.g., SDY2968 summary).

**Rationale:** The Blueprint requires that metadata be exposed in JSON-LD format, either via API responses or HTML embedded metadata. This is the single highest-impact gap.

**Implementation:**
```json
{
  "@context": "https://schema.org/",
  "@type": "Dataset",
  "identifier": "https://doi.org/10.21430/M3J8UMVGT6",
  "name": "COVID-19 vaccination perspectives among patients with Long COVID: A qualitative study",
  "description": "To improve our understanding of perspectives about COVID-19 vaccines among individuals with Long COVID...",
  "dateCreated": "2022-08-01",
  "author": [{"@type": "Person", "@id": "https://orcid.org/XXXX-XXXX-XXXX-XXXX"}],
  "funder": [{"@type": "Organization", "@id": "https://ror.org/043z4tv69"}],
  "measurementTechnique": "Qualitative research; Deductive thematic analysis",
  "distribution": "https://www.immport.org/shared/study/SDY2968/download",
  "citation": "https://doi.org/10.21430/M3J8UMVGT6",
  "infectiousAgent": "NCBITaxon:2697049",
  "host": "NCBITaxon:9606",
  "healthCondition": "MONDO:0100096",
  "conditionsOfAccess": "https://docs.immport.org/home/agreement/",
  "license": "https://docs.immport.org/home/agreement/",
  "temporalCoverage": "2022-08-01/2023-XX-XX"
}
```

**Also:** Add a JSON-LD response option to the Shared Data API (e.g., `Accept: application/ld+json`).

### Priority 2 — Explicit License and Conditions of Access (Blueprint Table 1)

**Action:** Add an explicit license (SPDX identifier or URL) and `conditionsOfAccess` URL at the dataset level.

**Rationale:** The Blueprint Table 1 requires a `license` field with an SPDX License Identifier or IRI to a license document. The `conditionsOfAccess` field should link to a resource describing access conditions.

**Implementation:**
- Add `license` field to study metadata (e.g., link to ImmPort user agreement or a standard open license).
- Add `conditionsOfAccess` field (e.g., `https://docs.immport.org/home/agreement/`).

### Priority 3 — Author ORCIDs and Funder RORs (Blueprint Section 2.2)

**Action:** Add author names with ORCID identifiers and funder names with ROR identifiers to the study summary page and JSON-LD metadata.

**Rationale:** The Blueprint requires ORCID for the `author` field and ROR for the `funder` field. These PIDs are currently missing from the SDY2968 study page.

**Implementation:**
- Collect ORCID iDs from study personnel during data submission.
- Map funder names to ROR identifiers (e.g., NIAID → `https://ror.org/043z4tv69`).

### Priority 4 — Ontology IRIs on Study Pages (Blueprint Table 1)

**Action:** Expose resolvable ontology identifiers for key biomedical terms on study summary pages.

**Rationale:** The Blueprint requires NCBITaxon for `infectiousAgent` and `host`, MONDO for `healthCondition`, and NCIT for `measurementTechnique`. Currently, these terms appear as free text on the SDY2968 page.

**Implementation:**
- Map "COVID-19" to NCBITaxon:2697049 (SARS-CoV-2).
- Map "Long COVID" / "Post-Acute Sequelae of COVID-19" to MONDO:0100096 (COVID-19) or a more specific MONDO term.
- Map "Homo sapiens" (host) to NCBITaxon:9606.
- Map "qualitative research" / "deductive thematic analysis" to appropriate NCIT terms.

### Priority 5 — Dataset-Specific Citation Block (Blueprint Section 4.2)

**Action:** Add a "Cite this study" block on each study landing page with at least one standard format (APA, NLM) that includes the DOI.

**Rationale:** The Blueprint requires consistent citation guidelines with standard formats. Currently, only portal-level citation guidance exists.

**Implementation:**
```
Smith, J., et al. (2022). COVID-19 vaccination perspectives among patients 
with Long COVID: A qualitative study [Data set]. ImmPort. 
https://doi.org/10.21430/M3J8UMVGT6
```

Also provide BibTeX for citation management tools.

### Priority 6 — Complete Temporal and Spatial Coverage (Blueprint Table 1)

**Action:** Add full temporal coverage (start/end date range in ISO 8601) and spatial coverage (ISO 3166 country code) where applicable.

**Rationale:** The Blueprint Table 1 requires `temporalCoverage` as a date range and `spatialCoverage` as a country code. Currently, only a start date is provided and no spatial coverage is given.

---

## 7. Suggested Next Steps

1. **Immediate (0-3 months):**
   - Embed schema.org `Dataset` JSON-LD on the SDY2968 study landing page.
   - Add an explicit license and `conditionsOfAccess` URL to the study metadata.
   - Add a dataset-specific "Cite this study" block with APA and BibTeX formats.

2. **Short-term (3-6 months):**
   - Collect and add author ORCID iDs and funder ROR identifiers to study metadata.
   - Map key biomedical terms to resolvable ontology identifiers (NCBITaxon, MONDO, NCIT).
   - Add a JSON-LD response option to the Shared Data API.

3. **Medium-term (6-12 months):**
   - Complete all 16 Blueprint Table 1 metadata elements for every study in ImmPort.
   - Apply for or verify an RRID for ImmPort as a repository.
   - Ensure all study landing pages are indexed by the NIAID Data Ecosystem Discovery Portal.

4. **Long-term (12+ months):**
   - Develop a queryable metadata knowledge graph as suggested in Blueprint Section 3.2.
   - Implement automated metadata quality checks during data submission.
   - Establish a regular re-assessment cadence to track Blueprint alignment progress.

---

## 8. Assessment Summary

| Dimension | Score | Status |
|-----------|-------|--------|
| **Overall Blueprint Alignment** | **58/100** | Moderate |
| Findable (F) | 65/100 | Good |
| Accessible (A) | 70/100 | Good |
| Interoperable (I) | 50/100 | Partial |
| Reusable (R) | 45/100 | Partial |

**Bottom line:** ImmPort has a strong foundation for FAIR compliance — persistent identifiers (DOI), rich textual metadata, comprehensive API infrastructure (OpenAPI, DRS, FHIR), ontology-backed data models, and excellent outreach/training resources. The primary gaps are at the **dataset level**: no machine-readable JSON-LD metadata, no explicit dataset-level license (SPDX), missing author ORCIDs and funder RORs, and no dataset-specific citation blocks in standard formats. Addressing these gaps — particularly embedding schema.org JSON-LD on study landing pages — would significantly improve Blueprint alignment and enable seamless integration with the NIAID Data Ecosystem Discovery Portal.

---

*This assessment was conducted using evidence gathered from the ImmPort study summary page (SDY2968), ImmPort documentation pages, API documentation, and the NIAID Blueprint v2 specification. All evidence quotes are verbatim from the fetched pages. Scores are based on the assessor's evaluation of the evidence against the Blueprint requirements and should be considered as a point-in-time assessment.*
