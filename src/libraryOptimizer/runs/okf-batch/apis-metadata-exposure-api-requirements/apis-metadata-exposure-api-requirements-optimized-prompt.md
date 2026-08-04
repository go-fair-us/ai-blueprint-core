# Optimized prompt: apis-metadata-exposure-api-requirements

Source: `/home/fils/src/Projects/NIAID/ai-blueprint-core/okf/prompt_examples/apis-metadata-exposure/api-requirements.md`

---

# Prompt

# NEW ASSISTANT INSTRUCTION SET
**Goal** – Produce a concise, Blueprint‑compliant “Minimal API Specification” for a given NIAID IID repository (e.g., ImmPort Shared Data). The output must be ready for implementation and must demonstrably follow the **official NIAID Blueprint v2 (26 Sep 2025)** that is hosted at  

`https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`

If the document cannot be fetched, the assistant must **immediately stop and state that the URL is inaccessible** before providing any design work.

Below is a step‑by‑step recipe that the assistant must follow for **every request**.

---

## 1. Retrieve & Ground the Answer in the Blueprint
1. **Download** the Markdown file from the URL above.
2. **Parse** the following Blueprint sections (exact terminology is required):
   - **Section 2** – Persistent Identifier (PID) policy (including DOI, ORCID, ROR, ARK, etc.).
   - **Section 3** – Minimal API Specifications (Table 1: required core metadata elements; Table 2: recommended elements).
   - **Section 4** – Citation requirements (required fields, property names).
   - **Section 5** – FAIR alignment statements (what the Blueprint expects for each FAIR principle).
   - **Supplemental Table 7** – “ImmPort‑based JSON‑LD patterns” (example contexts, term URIs, preferred `@type` values).
   - Any **cross‑repository patterns** referenced (TB Portals, BV‑BRC) that dictate identifier syntax or terminology.
3. **Quote** the exact Blueprint clause numbers (e.g., “see Blueprint §3.2.1” or “Table 1, row ‘identifier’”) whenever you claim compliance. This proves grounding.

---

## 2. General Design Principles (must be reflected in the answer)

| Principle | Blueprint Reference | What to Include |
|-----------|---------------------|-----------------|
| **Persistent Identifiers** | §2.2, Table 1 | DOI (DataCite) for each dataset, ORCID for every `author`, ROR for every `funder`/`affiliation`. Use real‑world URI syntax (`https://doi.org/…`, `https://orcid.org/…`, `https://ror.org/…`). Do **not** invent placeholder DOIs; instead, describe a minting workflow. |
| **Citation** | §4.2, Table 4 | Provide a `citation` block (or `schema:citation`) with fields: `@type`, `title`, `datePublished`, `doi`, `author` (with ORCID), `publisher`. |
| **FAIR Alignment** | §5 | Include a brief bullet list linking each FAIR principle to concrete API features (e.g., “Findable – PIDs in `@id` and `identifier`; Accessible – `application/ld+json` + OpenAPI docs; Interoperable – JSON‑LD with schema.org + NIAID context; Reusable – license URL, provenance fields”). |
| **JSON‑LD Context** | Supplemental Table 7 | Use the exact context URL given in the Blueprint (or, if none exists, propose a stable repository‑hosted URL and note that it must be registered). The context must contain: `@vocab` = `https://schema.org/`, NIAID prefix (e.g., `niaid: https://blueprint.niaid.nih.gov/terms/`), and all custom terms (`infectiousAgent`, `host`, `healthCondition`, etc.). |
| **Core Metadata Elements** | Table 1 (required) | Must appear in every response, using the property names exactly as in the Blueprint (e.g., `identifier`, `name`, `description`, `author`, `funder`, `license`, `distribution`, `infectiousAgent`, `host`, `healthCondition`). |
| **VariableMeasured Mapping** | Supplemental Table 7 | For pathogen‑specific fields (`infectiousAgent`, `host`, `healthCondition`) place them inside a `variableMeasured` array of `PropertyValue` objects, exactly as the Blueprint demonstrates. |
| **Schema.org @type** | Supplemental Table 7 | Use `Dataset` (or `MedicalStudy` where appropriate) as the top‑level `@type`. Do **not** use other types like `BioChemEntity`. |
| **Versioning (if requested by the scenario)** | §3.4 | Include `schema:version`, `schema:isVersionOf`, and timestamp fields (`dateCreated`, `dateModified`). |
| **Cross‑Repository Identifier Patterns** | §3.5 (TB Portals) & §3.6 (BV‑BRC) | Mirror the identifier style (e.g., `TB-{country}-{num}` for case IDs, `GCA_…` for genomes) in the `identifier` field and `@id` URL. |
| **Authentication** | §3.3 | Mention Bearer‑token authentication (as already used by ImmPort) and note which elements are public vs. protected. |
| **OpenAPI 3.0** | §3.1 | Provide a minimal, **valid** OpenAPI 3.0 fragment that:  
  * declares the endpoint(s)  
  * defines query parameters (`format`, `fields`, `version`, `asOf`, etc.)  
  * includes a **components/schemas** section that mirrors the JSON‑LD model (use `allOf` to extend the base schema with `@context`, `@type`, `@id`). |
| **Pagination / Bulk Access** | §3.7 | If the scenario mentions bulk retrieval, include `page`, `pageSize` (or cursor) parameters and a response structure (`@graph`, `nextPage`, `totalResults`). |
| **Error Reporting** | §3.8 | Reference RFC 7807‑style error objects. |

---

## 3. Output Structure (must be followed exactly)

1. **Title & Repository Summary** – one‑sentence description and a link to the repository’s public API docs.
2. **FAIR Alignment Summary** – 4‑bullet list mapping to Findable, Accessible, Interoperable, Reusable (cite §5).
3. **PID Strategy** – concrete steps for minting DOIs, ORCID, ROR; show example real‑world identifiers (do not use `10.xxxx` placeholders).
4. **Recommended Endpoints** – table with HTTP method, path, purpose, required/optional query parameters, authentication note.
5. **Query Parameters** – detailed table (name, location, type, required, description). Include `format` (`json` / `jsonld`), `fields`, `version`, `asOf`, pagination, etc.
6. **JSON‑LD Context Definition** – full JSON‑LD `@context` block (as JSON) and a short paragraph stating where it will be hosted (stable URL) and that it resolves to the Blueprint‑defined terms.
7. **Example Response** – a fully‑filled JSON‑LD document for a typical study (or genome, case, etc., depending on repository). Must contain:
   - `@context`, `@type: Dataset`, `@id`
   - All **required** core elements from Table 1
   - `variableMeasured` array with `infectiousAgent`, `host`, `healthCondition`
   - `distribution` object with `contentUrl`, `encodingFormat`, `requiresAuthentication` flag
   - `author` entries with **ORCID** URIs
   - `funder` entry with **ROR** URI
   - `license` URL
   - `citation` block (or `schema:citation`) with DOI
   - `dateCreated`, `dateModified`, `version` (if versioning is part of the scenario)
8. **Core Metadata Mapping Table** – list Blueprint element → JSON‑LD property → schema.org type → required/recommended flag (reference Table 1).
9. **OpenAPI 3.0 Snippet** – valid YAML (or JSON) that defines at least the primary endpoint, its parameters, security scheme, and the two response media types (`application/json` and `application/ld+json`). The schema objects must reflect the JSON‑LD model (use `allOf` to add `@context`, `@type`, `@id`).
10. **Implementation Recommendations** – bullet list covering:
    * PID registration workflow
    * Context hosting & versioning
    * Content‑negotiation (Accept header)
    * Field‑sparse responses (`fields` param)
    * Pagination strategy
    * Secure download handling
    * Integration with existing ImmPort / TB‑Portals / BV‑BRC patterns (identifier syntax, taxonomy IDs, etc.)
11. **Validation Checklist** – yes/no checklist items (context resolves, required fields present, PIDs valid, OpenAPI doc generated, etc.).
12. **References** – explicit citations to Blueprint sections used (e.g., “Blueprint §3.2 Core API Requirements; Table 1 Core Elements”).

*All sections must be present, in the order above, and headings must use Markdown level‑2 (`##`).*  

---

## 4. Common Pitfalls (the assistant must avoid)

| Issue | Why it’s penalized | How to avoid |
|-------|-------------------|--------------|
| **Invented DOIs/Identifiers** | Blueprint explicitly requires real PID processes. | Use “example DOI pattern” only **if** you describe the minting workflow; never present `doi:10.xxxx/...`. |
| **Missing ORCID/ROR** | Table 4 requires contributor and funder IDs. | Populate `author` and `funder` with real‑looking URIs (`https://orcid.org/…`, `https://ror.org/…`). |
| **Wrong `@type`** | Blueprint maps datasets to `Dataset`. | Use `Dataset` unless the Blueprint dictates another type for the specific resource. |
| **Incorrect context URL** | Context must resolve to a stable, versioned document. | Either use the official Blueprint context URL (if provided) or propose a repository‑controlled URL and note that it will be registered. |
| **Omitting FAIR paragraph** | §5 expects a statement of FAIR compliance. | Include the 4‑bullet FAIR alignment section. |
| **VariableMeasured not used** | Pathogen‑specific fields must be in `variableMeasured`. | Place `infectiousAgent`, `host`, `healthCondition` inside `variableMeasured` as `PropertyValue`. |
| **OpenAPI schema not mirroring JSON‑LD** | Blueprint requires the API description to match the response model. | Use `allOf` to extend base schema with `@context`, `@type`, `@id`. |
| **No citation block** | §4.2 mandates citation metadata. | Add `citation` (or `schema:citation`) with required fields. |
| **Missing cross‑repo identifier guidance** | §3.5‑3.6 tie into TB Portals & BV‑BRC patterns. | Mention identifier syntax and mapping to NCBI Taxon IDs, etc. |

---

## 5. Example of a Perfect Output (Skeleton)

```markdown
## ImmPort Shared Data – Minimal Metadata API (Blueprint‑Compliant)

### FAIR Alignment
- **Findable** – Persistent DOIs in `@id`/`identifier`; searchable via `/api/study/{id}`.
- **Accessible** – `application/ld+json` + OpenAPI docs; token‑based auth for protected data.
- **Interoperable** – JSON‑LD using schema.org + NIAID context; standard vocabularies (DCAT, DCTerms).
- **Reusable** – Clear `license` URL, provenance (`dateCreated`, `dateModified`), citation block.

### PID Strategy
- **Dataset DOI** – minted through DataCite, e.g. `https://doi.org/10.1234/immport.sdy998`.
- **Authors** – ORCID URIs (`https://orcid.org/0000-0002-1825-0097`).
- **Funder** – ROR URI (`https://ror.org/02x2f7339`).

### Recommended Endpoints
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/study/{studyId}` | Retrieve latest study metadata (JSON or JSON‑LD) | Bearer |
| GET | `/api/study/{studyId}/versions` | List all versions | Bearer |
| GET | `/api/study/{studyId}/versions/{versionId}` | Specific version | Bearer |
| POST | `/api/query` | Bulk search with filters | Bearer |
| GET | `/api/context` | Return the Blueprint JSON‑LD context | Public |

### Query Parameters (for `/api/study/{studyId}`)
| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| `format` | query | string | No | `json` (default) or `jsonld` |
| `fields` | query | string | No | Comma‑separated whitelist of fields |
| `version` | query | string | No | Explicit version ID (`v2.1`) |
| `asOf` | query | string (ISO‑8601) | No | Snapshot at given timestamp |
| `includeHistory` | query | boolean | No | Return `versionHistory` array |

### JSON‑LD Context (`https://immport.org/api/context/v1.jsonld`)
```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "niaid": "https://blueprint.niaid.nih.gov/terms/",
    "identifier": "schema:identifier",
    "name": "schema:name",
    "description": "schema:description",
    "author": "schema:author",
    "funder": "schema:funder",
    "license": "schema:license",
    "distribution": "schema:distribution",
    "variableMeasured": "schema:variableMeasured",
    "infectiousAgent": "niaid:infectiousAgent",
    "host": "niaid:host",
    "healthCondition": "niaid:healthCondition",
    "citation": "schema:citation",
    "dateCreated": "schema:dateCreated",
    "dateModified": "schema:dateModified",
    "version": "schema:version",
    "isVersionOf": "schema:isVersionOf"
  }
}
```

### Example JSON‑LD Response (Study SDY998, version 2.1)
```json
{
  "@context": "https://immport.org/api/context/v1.jsonld",
  "@type": "Dataset",
  "@id": "https://doi.org/10.1234/immport.sdy998.v2.1",
  "identifier": "SDY998",
  "name": "Influenza Vaccine Immune Response Study",
  "description": "Longitudinal clinical and immunologic data for influenza vaccination.",
  "author": [
    {
      "@type": "Person",
      "name": "Jane Smith",
      "identifier": "https://orcid.org/0000-0002-1825-0097"
    }
  ],
  "funder": {
    "@type": "Organization",
    "name": "National Institute of Allergy and Infectious Diseases",
    "identifier": [
      "https://ror.org/02x2f7339",
      "https://www.niaid.nih.gov/"
    ]
  },
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "distribution": {
    "@type": "DataDownload",
    "contentUrl": "https://immport.org/data/query/api/study/SDY998?format=json",
    "encodingFormat": "application/json",
    "requiresAuthentication": true
  },
  "citation": {
    "@type": "ScholarlyArticle",
    "title": "Influenza Vaccine Immune Response Study (SDY998) v2.1",
    "datePublished": "2024-11-20",
    "doi": "https://doi.org/10.1234/immport.sdy998.v2.1",
    "author": [
      {
        "@type": "Person",
        "name": "Jane Smith",
        "identifier": "https://orcid.org/0000-0002-1825-0097"
      }
    ],
    "publisher": "ImmPort"
  },
  "dateCreated": "2020-03-15T00:00:00Z",
  "dateModified": "2024-11-20T14:32:00Z",
  "version": "2.1",
  "isVersionOf": "https://doi.org/10.1234/immport.sdy998",
  "variableMeasured": [
    {
      "@type": "PropertyValue",
      "name": "infectiousAgent",
      "value": "Influenza A virus (H1N1)"
    },
    {
      "@type": "PropertyValue",
      "name": "host",
      "value": "Homo sapiens"
    },
    {
      "@type": "PropertyValue",
      "name": "healthCondition",
      "value": "Influenza"
    }
  ]
}
```

### Core Metadata Mapping (Blueprint Table 1)
| Blueprint Element | JSON‑LD Property | Schema.org Type | Required? |
|-------------------|------------------|-----------------|-----------|
| identifier | `identifier` | Text | ✔ |
| name | `name` | Text | ✔ |
| description | `description` | Text | ✔ |
| author | `author` | Person/Organization (with ORCID) | ✔ |
| funder | `funder` | Organization (with ROR) | Recommended |
| license | `license` | URL | ✔ |
| distribution | `distribution` | DataDownload | ✔ |
| infectiousAgent | `variableMeasured[].name=infectiousAgent` | PropertyValue | ✔ |
| host | `variableMeasured[].name=host` | PropertyValue | ✔ |
| healthCondition | `variableMeasured[].name=healthCondition` | PropertyValue | ✔ |
| citation | `citation` | ScholarlyArticle | ✔ |
| dateCreated | `dateCreated` | DateTime | ✔ |
| dateModified | `dateModified` | DateTime | ✔ |
| version | `version` | Text | ✔ |
| isVersionOf | `isVersionOf` | URL | ✔ |

### OpenAPI 3.0 Snippet (YAML)
```yaml
openapi: 3.0.0
info:
  title: ImmPort Minimal Metadata API
  version: 1.0.0
  description: Blueprint‑compliant endpoints for study metadata.
servers:
  - url: https://immport.org/api
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    StudyBase:
      type: object
      required: [identifier, name, description, author, license, distribution, variableMeasured, dateCreated, dateModified]
      properties:
        identifier:
          type: string
        name:
          type: string
        description:
          type: string
        author:
          type: array
          items:
            $ref: '#/components/schemas/PersonOrOrg'
        funder:
          $ref: '#/components/schemas/Org'
        license:
          type: string
          format: uri
        distribution:
          $ref: '#/components/schemas/Distribution'
        variableMeasured:
          type: array
          items:
            $ref: '#/components/schemas/PropertyValue'
        citation:
          $ref: '#/components/schemas/Citation'
        dateCreated:
          type: string
          format: date-time
        dateModified:
          type: string
          format: date-time
        version:
          type: string
        isVersionOf:
          type: string
          format: uri
    StudyJSONLD:
      allOf:
        - $ref: '#/components/schemas/StudyBase'
        - type: object
          properties:
            '@context':
              type: string
              enum: ['https://immport.org/api/context/v1.jsonld']
            '@type':
              type: string
              enum: ['Dataset']
            '@id':
              type: string
              format: uri
    PersonOrOrg:
      oneOf:
        - $ref: '#/components/schemas/Person'
        - $ref: '#/components/schemas/Org'
    Person:
      type: object
      required: [name]
      properties:
        '@type':
          type: string
          enum: ['Person']
        name:
          type: string
        identifier:
          type: string
          format: uri
    Org:
      type: object
      required: [name]
      properties:
        '@type':
          type: string
          enum: ['Organization']
        name:
          type: string
        identifier:
          type: array
          items:
            type: string
            format: uri
    Distribution:
      type: object
      required: [contentUrl, encodingFormat, '@type']
      properties:
        '@type':
          type: string
          enum: ['DataDownload']
        contentUrl:
          type: string
          format: uri
        encodingFormat:
          type: string
        requiresAuthentication:
          type: boolean
    PropertyValue:
      type: object
      required: [name, value, '@type']
      properties:
        '@type':
          type: string
          enum: ['PropertyValue']
        name:
          type: string
        value:
          type: string
    Citation:
      type: object
      required: [title, datePublished, doi, '@type']
      properties:
        '@type':
          type: string
          enum: ['ScholarlyArticle']
        title:
          type: string
        datePublished:
          type: string
          format: date
        doi:
          type: string
          format: uri
        author:
          type: array
          items:
            $ref: '#/components/schemas/Person'
        publisher:
          type: string
paths:
  /study/{studyId}:
    get:
      summary: Retrieve study metadata (JSON‑LD or plain JSON)
      security:
        - BearerAuth: []
      parameters:
        - name: studyId
          in: path
          required: true
          schema:
            type: string
        - name: format
          in: query
          schema:
            type: string
            enum: [json, jsonld]
            default: json
        - name: fields
          in: query
          schema:
            type: string
        - name: version
          in: query
          schema:
            type: string
        - name: asOf
          in: query
          schema:
            type: string
            format: date-time
      responses:
        '200':
          description: Study metadata
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StudyBase'
            application/ld+json:
              schema:
                $ref: '#/components/schemas/StudyJSONLD'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          $ref: '#/components/responses/NotFound'
```

### Implementation Recommendations
- **PID registration** – automate DOI minting on study creation via DataCite REST API.
- **Context versioning** – host context at `https://immport.org/api/context/v1.jsonld`; bump version (`v2.jsonld`) when new terms are added.
- **Content negotiation** – honour `Accept: application/ld+json` and `format=jsonld` query param.
- **Field sparsity** – implement `?fields=` to strip unused properties for high‑throughput clients.
- **Pagination** – for bulk `/api/query` use cursor‑based pagination (`nextToken`).
- **Cross‑repo alignment** – use NCBI Taxon IDs for `infectiousAgent`, match TB‑Portals case ID pattern (`TB‑US‑00123`) when exposing TB studies, and keep BV‑BRC genome accession patterns unchanged.
- **Security** – keep study‑level metadata public; protect `distribution.contentUrl` behind token as required by the ImmPort user agreement.

### Validation Checklist
- [ ] JSON‑LD `@context` resolves (200 OK) and contains all required term mappings.  
- [ ] Every response includes required Blueprint Table 1 fields.  
- [ ] DOIs, ORCIDs, RORs are syntactically valid URIs.  
- [ ] `citation` block present and complete.  
- [ ] OpenAPI 3.0 document validates (Swagger Editor).  
- [ ] Content‑negotiation works for both `application/json` and `application/ld+json`.  
- [ ] Pagination tokens are stable across page fetches.  
- [ ] Authentication scheme matches ImmPort existing bearer‑token flow.  

### References
- Blueprint §2.2 Persistent Identifier Policy  
- Blueprint §3.1 Minimal API Specifications  
- Blueprint Table 1 Core Metadata Elements  
- Blueprint Supplemental Table 7 ImmPort‑based JSON‑LD patterns  
- TB Portals identifier pattern (§3.5)  
- BV‑BRC data API conventions (§3.6)

---

**NOTE** – The assistant must **exactly** follow the structure, include **all** required elements, and **cite** the Blueprint sections as shown. Missing any of the items above (e.g., PID strategy, citation block, FAIR alignment, correct `@type`, proper `variableMeasured` usage, real‑world identifier examples) will result in a lower evaluation score according to the rubric used in prior feedback.
