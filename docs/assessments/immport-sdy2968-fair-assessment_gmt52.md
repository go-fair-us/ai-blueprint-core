# FAIR Principles Alignment Assessment

**Target URL (authoritative input):** https://r.jina.ai/https://www.immport.org/shared/study/SDY2968/summary

**Blueprint (defaulted):** NIAID Blueprint for Digital Objects v2
https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md

**Assessment date:** 2026-07-05

## Fetch Method Used and Limitations

- ImmPort "Shared Data" study pages are JavaScript-rendered.
- A direct HTML fetch of `https://www.immport.org/shared/study/SDY2968/summary` returned an app shell (loading spinner) rather than the study content.
- Therefore, the assessment used the server-side rendered Markdown provided by `r.jina.ai` for:
  - Study summary: `https://r.jina.ai/https://www.immport.org/shared/study/SDY2968/summary`
  - Study download browser: `https://r.jina.ai/https://www.immport.org/shared/study/SDY2968/download`
  - Portal documentation (docs.immport.org) pages.
- Some download-page fields/links (notably direct file URLs / DRS IDs per file row) appear to be filled by client-side code and were not fully extractable from the rendered Markdown snapshot.

## Overall Alignment Summary (NIAID Blueprint + FAIR)

**Overall:** Moderate alignment (good identifiers + strong portal-level API/docs; gaps in per-dataset machine-readable metadata and explicit licensing).

**Score (0-100):** 65/100

### Strengths (with evidence)

- Persistent identifier present (DOI) on the study page.
- Strong portal-level programmatic access options and documentation (OpenAPI/Swagger, GA4GH DRS, FHIR).
- Uses controlled vocabularies/ontologies in the data model.
- Clear contact point (helpdesk) and citation guidance.

### Key Gaps

- No embedded schema.org / JSON-LD metadata evidenced on the dataset landing page HTML (Blueprint prefers schema.org alignment and JSON-LD exposure).
- License is not expressed as an explicit SPDX identifier (or equivalent) per dataset; terms are described via a general user agreement.
- Creator/author ORCIDs, funder RORs, explicit conditionsOfAccess URL, and distribution direct links are not clearly present on the SDY2968 summary page.

## Evidence Collected (Quotes)

### From SDY2968 study summary (via r.jina.ai)

> "Accession SDY2968"

> "DOI 10.21430/M3J8UMVGT6"

> "Title COVID-19 vaccination perspectives among patients with Long COVID: A qualitative study"

> "Condition Studied COVID-19, Post-Acute Sequelae of COVID-19"

### From ImmPort API documentation

Source: https://docs.immport.org/apidocumentation/

> "Shared Data endpoints are documented with OpenAPI 3.0 and exposed via a Swagger UI for interactive exploration and live requests."

> "ImmPort uses scoped API keys for all API access"

> "Authorization: Bearer <api_key>"

### From ImmPort download documentation

Source: https://docs.immport.org/download/

> "ImmPort provides multiple ways to download data ... Authentication is required to download data from ImmPort."

### From ImmPort data model ontologies page

Source: https://docs.immport.org/datamodel/ontologies/

> "Lookup Tables ... are populated using standarized terms from ontologies."

(The page lists multiple established ontologies, including NCBI Taxonomy and NCIT.)

### From ImmPort citation guidance

Source: https://docs.immport.org/home/cite/

> "When using specific ImmPort data sets for publication, please cite the ImmPort Shared Data web site, Study Accession, and Study Title"

### From ImmPort user agreement (usage/conditions)

Source: https://docs.immport.org/home/agreement/

> "You have the unrestricted right to use and distribute ImmPort data. However, you will ensure that all redistribution occurs under terms commensurate with this agreement."

> "You will not attempt to identify individuals from ImmPort data sets"

## FAIR Breakdown (Meet / Partially Meet / Fail)

### Findable

- F1 (globally unique persistent identifiers): **Meet**
  - Evidence: DOI present on SDY2968 page (`10.21430/M3J8UMVGT6`).

- F2 (rich metadata): **Partially meet**
  - Evidence: Title, description, condition studied, start date are present.
  - Gap vs Blueprint minimal metadata (Blueprint 1.2 Table 1): missing/unclear on the SDY2968 page: `author (ORCID)`, `funder (ROR)`, `license (SPDX)`, `conditionsOfAccess (URL)`, and clear `distribution` direct file URLs.

- F3 (metadata includes identifier): **Meet**
  - Evidence: SDY2968 summary includes accession and DOI.

- F4 (registered/indexed): **Partially meet**
  - Evidence: ImmPort is a shared-data portal with discovery/download features in documentation.
  - Gap: no evidence collected that the SDY2968 landing page exposes structured markup (e.g., JSON-LD) for external indexing.

### Accessible

- A1 (retrievable by identifier using standardized protocol): **Partially meet**
  - Evidence: HTTPS pages; APIs documented for programmatic access.
  - Gap: data downloads require authentication (not inherently a failure, but reduces open accessibility).

- A1.1 (protocol open/free/universal): **Meet**
  - Evidence: HTTPS + REST APIs.

- A1.2 (authentication/authorization supported): **Meet**
  - Evidence: scoped API keys; auth required for downloads.

- A2 (metadata accessible if data unavailable): **Unknown / Partially meet**
  - Evidence: not assessed from fetched pages (no explicit tombstoning/retention policy found in collected evidence).

### Interoperable

- I1 (formal/shared language for knowledge representation): **Partially meet**
  - Evidence: JSON/REST APIs; FHIR interface exists.
  - Gap vs Blueprint 3.2: no evidence collected of JSON-LD responses or JSON-LD embedded metadata for SDY2968.

- I2 (uses FAIR vocabularies): **Meet**
  - Evidence: ontology-backed lookup tables; multiple established ontologies listed.

- I3 (qualified references to other metadata): **Partially meet**
  - Evidence: DOI links; links to release notes.
  - Gap: key terms on SDY2968 page appear as plain text rather than resolvable ontology IDs; no clear ORCID/ROR cross-links.

### Reusable

- R1 (richly described with relevant attributes): **Partially meet**
  - Evidence: substantive detailed description.
  - Gap: provenance fields like creators, affiliations, funder IDs, grant IDs not evidenced on SDY2968 summary.

- R1.1 (clear license): **Partially meet**
  - Evidence: user agreement describes allowed use/redistribution.
  - Gap vs Blueprint 1.2: no dataset-level standard license identifier (SPDX) or explicit license field evidenced.

- R1.2 (provenance): **Partially meet**
  - Evidence: release versions listed.
  - Gap: no creator identifiers (ORCID) evidenced on the page.

- R1.3 (community standards): **Meet (portal-level), Partially meet (dataset page)**
  - Evidence: GA4GH DRS + FHIR are strong community standards.
  - Gap: dataset landing page does not clearly expose machine-readable metadata aligned with schema.org/JSON-LD.

## Alignment to NIAID Blueprint (Highest-Impact Gaps)

- Minimal metadata schema (Blueprint 1.2): **Partially meet**
  - Present: `identifier (DOI)`, `name`, `description`.
  - Missing/unclear on SDY2968 page: `author (ORCID)`, `funder (ROR)`, `license (SPDX)`, `conditionsOfAccess (URL)`, `distribution` as direct file URLs or stable download endpoints.

- Persistent identifiers (Blueprint 2.2): **Partially meet**
  - Present: DOI.
  - Missing: ORCID (author), ROR (funder) evidenced on dataset page.

- APIs / machine access (Blueprint 3.2): **Partially meet**
  - Strong: OpenAPI/Swagger documented; DRS; FHIR.
  - Missing evidence: JSON-LD option for metadata responses and/or JSON-LD embedded in dataset HTML.

- Citation (Blueprint 4.2): **Partially meet**
  - Present: portal citation guidance; dataset DOI exists.
  - Missing: dataset-specific copy/paste citations in standard formats that include DOI.

- Outreach/contact (Blueprint 5.2): **Meet**
  - Evidence: helpdesk email prominently listed: `ImmPort_Helpdesk@immport.org`.

## Recommendations (Prioritized)

1. Embed schema.org `Dataset` JSON-LD on each study landing page (e.g., SDY2968 summary).
2. Provide a stable, unauthenticated per-study metadata endpoint that returns JSON-LD (even if file downloads require auth).
3. Make license and access conditions explicit at the dataset level using a standard license identifier (SPDX) or resolvable license URL + `conditionsOfAccess` URL.
4. Add a dataset-level "Cite this study" block with at least one standard format (APA/NLM) that includes the DOI, and optionally BibTeX.
5. Expose resolvable ontology identifiers (or links) for key biomedical terms already supported by the data model.
