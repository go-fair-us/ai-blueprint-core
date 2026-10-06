# Making the Metabolomics Workbench REST API Compatible with the NIAID Blueprint (Section 3)

## Report Information

| | |
|---|---|
| **Model used** | Claude Opus 5.5 (Anthropic) |
| **Date** | October 6, 2026 |
| **Input** | User question: *"What should I do to make the Metabolomics Workbench API (https://www.metabolomicsworkbench.org/tools/mw_rest.php) work in a way compatible with the NIAID Blueprint? The Blueprint is attached and the API section is section 3."* Attached file: `NIAID_Blueprint_v2_26Sep2025_forExternal.md` |
| **Tools used** | File reading in a sandboxed Linux environment (`grep`, `sed`) to extract Blueprint sections; web fetch (MW REST service page); web search (MW REST API documentation and examples). An attempted fetch of a live study summary endpoint (`/rest/study/study_id/ST000001/summary`) was blocked by the site's robots.txt, so live JSON responses were not inspected. |
| **Resources consulted** | NIAID Blueprint v2 (26 Sep 2025): Sections 1 (Minimal Metadata Schema, Table 1), 2 (PIDs, Table 2), 3 (Minimal API Specifications), Supplemental Tables 6–7. Metabolomics Workbench REST service page (MW REST API v1.1, 11/27/2023). MW REST API specification PDF (MWRestAPIv1.0.pdf). MW REST tutorial slides (MW_REST.pdf). metabolomicsWorkbenchR Bioconductor vignette. MW binder Jupyter notebook (MWRestAPIStudyDataExample.ipynb). |

---

## Summary

The Metabolomics Workbench (MW) REST API already meets one of the four Section 3.2 objectives (HTTP GET). It partly meets the IRI-structure objective and misses the other two: it has no JSON-LD output and no OpenAPI description. The least disruptive fix is to add a small, resource-oriented, JSON-LD-returning layer for *studies* next to the existing API, and leave the current API as it is. Existing clients such as the Bioconductor and Python tools depend on it.

## How the current API compares to Section 3.2

**1. HTTP GET: already compliant.** Every request is a plain GET on a URL.

**2. Resource-oriented IRIs: partly compliant.** The URL is built from a context (study, compound, refmet, metstat, gene, protein, moverz), then an input item and value, then an output item and an optional format, e.g. `/rest/study/study_id/ST000001/summary`. It is path-based and has no verbs, which is good. But it works as a query language, not as one stable address per resource:

- The same input slot does exact lookups and searches: `/study/study_title/diabetes/` is a search.
- Partial IDs match many studies. `ST0004/summary` and `ST/summary` (which returns all studies) are examples.
- Each study's metadata is split across several URLs: `summary`, `factors`, `analysis`, `metabolites` and `data`.
- The metstat context uses 8 semicolon-delimited slots, which is the kind of complex parameter string the Blueprint advises against.

As a result, no single current URL can serve as the JSON-LD `@id` for a study.

**3. JSON-LD encoding: missing.** The default output is plain JSON, with text as an option. There is no `@context` or `@type` and no schema.org property names.

**4. OpenAPI/Swagger documentation: missing.** The documentation is a web page, an interactive URL builder, and a PDF. None of these is machine-readable in the OpenAPI sense.

## Recommendations

### Step 1: Scope it to studies

Under the Blueprint, the "digital objects" are the deposited studies and analyses (schema.org `Dataset`). The compound, RefMet, gene, protein, and moverz contexts are reference and lookup services, so they can stay as they are. You could later describe compounds with Bioschemas `MolecularEntity`, but that is optional.

### Step 2: Add canonical resource endpoints

Put these beside the v1 API, for example:

- `GET /rest/v2/studies/ST000001` returns the study record
- `GET /rest/v2/studies/ST000001/analyses/AN000001` returns one analysis
- `GET /rest/v2/studies?page=…` returns a paged list for harvesters

These endpoints should only do exact-ID lookups, never partial matches. They should return JSON-LD through `Accept: application/ld+json` or `?format=json-ld`, which follows the pattern in Supplemental Table 7. Each document's `@id` should be its own URL, so that dereferencing the `@id` returns the document, as the Blueprint asks. The DOI goes in `identifier`, not in `@id`. The existing `/rest/study/study_id/...` paths can stay unchanged, or redirect where they map one-to-one.

### Step 3: Map MW study metadata to Table 1

Many fields are already in MW's study metadata. Others need ontology mapping or new collection at submission time.

| Table 1 element | MW source | Work needed |
|---|---|---|
| type | constant | `Dataset` |
| identifier | study DOI (MW mints DataCite DOIs) | Emit as `https://doi.org/…` |
| name / description | study title / study summary | Direct mapping |
| dateCreated | submit date | Convert to ISO 8601 |
| author | PI name and institute | Add ORCID (collect at submission) |
| funder / grant | funding info in study metadata, if present | Add ROR IDs; normalize grant numbers |
| measurementTechnique | analysis type (MS/NMR), chromatography, ionization | Map to NCIT terms |
| host | subject species | Map to NCBITaxon |
| healthCondition | disease association (already used by MetStat) | Map to MONDO |
| infectiousAgent | only for relevant studies | NCBITaxon where applicable |
| distribution | mwTab, results, raw-data download URLs | `DataDownload` entries |
| citation | linked publications | DOI or PubMed IRIs |
| conditionsOfAccess / license | MW's data-use terms | Pick an SPDX ID (e.g. CC-BY-4.0) or a URL to the terms |
| spatial / temporalCoverage | usually not captured | Optional; skip unless available |

Section 1.1 says a subset is acceptable. The best first release is identifier, name, description, dateCreated, author, host, measurementTechnique, distribution, and license; the rest can follow. The ontology mapping for species, disease, and technique is probably the largest single task. MW's existing controlled lists, such as the MetStat menus, give you a head start.

### Step 4: Publish an OpenAPI 3 description

Serve something like `/rest/openapi.json`, plus a Swagger UI page, covering the v2 endpoints and ideally the v1 ones too. The v1 path-parameter style can still be described in OpenAPI. Include response schemas so clients know what fields they will receive.

### Step 5 (optional but cheap): Add the other exposure routes from Figure 2

Embed the same JSON-LD in a `<script type="application/ld+json">` block on each study landing page. NIAID Data Ecosystem (NDE)-style harvesters and Google Dataset Search will pick that up. A downloadable bulk dump of all study JSON-LD records also makes full harvesting simple.

## Sketch of a study response

```json
{
  "@context": "https://schema.org/",
  "@id": "https://www.metabolomicsworkbench.org/rest/v2/studies/ST000001",
  "@type": "Dataset",
  "identifier": {
    "@type": "PropertyValue",
    "propertyID": "https://registry.identifiers.org/registry/doi",
    "value": "doi:10.21228/XXXXXX",
    "url": "https://doi.org/10.21228/XXXXXX"
  },
  "name": "<study_title>",
  "description": "<study_summary>",
  "dateCreated": "2013-01-15",
  "url": "<study landing page>",
  "author": [{ "@type": "Person", "name": "<PI>", "identifier": "https://orcid.org/…",
               "affiliation": { "@type": "Organization", "name": "<institute>", "identifier": "https://ror.org/…" } }],
  "measurementTechnique": [{ "@type": "DefinedTerm", "name": "Mass Spectrometry",
                             "url": "http://purl.obolibrary.org/obo/NCIT_C17156" }],
  "species": { "@type": "DefinedTerm", "name": "Homo sapiens",
               "url": "http://purl.obolibrary.org/obo/NCBITaxon_9606" },
  "healthCondition": { "@type": "DefinedTerm", "name": "<disease>", "url": "http://purl.obolibrary.org/obo/MONDO_…" },
  "distribution": [{ "@type": "DataDownload", "encodingFormat": "application/json",
                     "contentUrl": "https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/mwtab" }],
  "license": "https://spdx.org/licenses/CC-BY-4.0",
  "conditionsOfAccess": "Open"
}
```

The DOI suffix, date, and IDs are placeholders. Host organism is shown with `species` here; check which property name (`host` vs `species`) the NIAID Data Ecosystem schema expects before you finalize.

## Caveats and next steps

- The MW site blocks automated fetching, so a live `summary` response could not be inspected. The MW field names in the mapping table come from the documentation and may differ slightly from the real JSON keys. Check them against an actual response before writing the mapping code.
- Coordinate with the NIAID Data Ecosystem team early, since they are the main consumer and can tell you which subset of fields their harvester uses first.
