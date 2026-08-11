# Optimized prompt: md1.1

Source: `/home/fils/src/Projects/NIAID/ai-blueprint-core/src/libraryOptimizer/input/md1.1.md`

---

# Prompt

# 📋 NEW INSTRUCTION FOR THE ASSISTANT
**Goal:** For any repository‑specific scenario you are given (e.g., ImmPort clinical trial, ICPSR social‑science study, Dryad epidemiology dataset, etc.), automatically produce three artefacts that satisfy the **NIAID Minimal Metadata Blueprint** and the **FAIR‑API Work Plan**:

1. **A complete JSON‑LD metadata record** (Schema.org `Dataset`) that contains every mandatory Blueprint field, any domain‑specific extensions, and the extra “best‑practice” properties highlighted by the reviewers.
2. **A concise REST‑ful API specification** (Blueprint §3.2) that returns that JSON‑LD for a given PID, with pagination, filtering, versioning, and explicit access‑control notes.
3. **A citation template** (single‑line) together with a concrete example and a matching BibTeX entry (Blueprint §4.2).

The assistant should **always** follow the step‑by‑step strategy below, inserting the scenario‑specific values that appear in the user prompt.

---

## 🔧 STEP‑BY‑STEP STRATEGY (to be coded into the assistant)

### 1️⃣ Parse the scenario
- Detect the **repository type** (ImmPort, ICPSR, Dryad, or “other”).
- Extract any **required domain‑specific metadata elements** mentioned (e.g., `confidentiality agreements`, `variable coding schemes`, `embargo`, `assay type`, `instrument model`, …).

### 2️⃣ Build the **JSON‑LD** skeleton
Start with this **mandatory block** (order does not matter, but keep the same sequence for readability):

```json
{
  "@context": "https://schema.org/",
  "@type": "Dataset",
  "@id": "<PID‑URL>",                 // https://doi.org/… or repository landing‑page URL
  "identifier": "<PID‑plain>",       // DOI or native ID (e.g., SDY2847, ICPSR38291)
  "name": "<Study / Dataset title>",
  "description": "<Short free‑text description>",
  "creator": [                       // one object per author
    {
      "@type": "Person",
      "name": "<Last, First>",
      "orcid": "https://orcid.org/<ORCID>"
    }
    /* …repeat for all creators… */
  ],
  "datePublished": "<YYYY‑MM‑DD>",
  "dateCreated": "<YYYY‑MM‑DD>",
  "dateModified": "<ISO‑8601 timestamp>",   // e.g. 2025-07-01T12:00:00Z
  "license": "<URL to license>",              // e.g. CC‑BY‑4.0, CC0, or restricted‑use page
  "keywords": [ "<kw1>", "<kw2>", … ],
  "funding": {
    "@type": "Grant",
    "name": "<grant number or name>",
    "funder": {
      "@type": "Organization",
      "name": "<Funding org>",
      "url": "https://ror.org/<ROR‑ID>"
    }
  },
  "temporalCoverage": "<YYYY‑MM‑DD>/<YYYY‑MM‑DD>",
  "spatialCoverage": {
    "@type": "Place",
    "name": "<Region / Country>",
    "geo": {
      "@type": "GeoCoordinates",
      "latitude": <lat>,
      "longitude": <lon>
    }
  },
  "subjectSpecies": "https://identifiers.org/taxonomy/<NCBI‑taxID>",
  "dataUseLimitation": [ "<code1>", "<code2>", … ],   // use controlled codes (e.g., "GRU", "Restricted")
  "conformsTo": "https://doi.org/10.1101/2023.01.01/NIAID-metadata-v1",
```

#### 2.1 Add **repository‑wide mandatory extensions**
| Repository | Required extra properties (add after the block above) |
|-----------|--------------------------------------------------------|
| **ImmPort (clinical trial)** | `additionalType`: "https://schema.org/MedicalTrial", `clinicalTrialPhase`, `trialRegistration`, `interventionType`, `assayType`, `instrumentModel`, `libraryLayout`, `readLength`, `insertSize`, `sequencingCenter`, `dataCollectionMethod` |
| **ICPSR (social‑science)** | `measurementMethod` (use an ontology IRI, e.g., `http://purl.obolibrary.org/obo/OBI_0000270` for “questionnaire”), `variableMeasured` (array of `PropertyValue` objects with `name`, `propertyID`, `description`, optional `valueReference` → URL of codebook), `accessRights` (URL to the data‑use agreement), `isAccessibleForFree`: false, `publisher` (ICPSR organization object) |
| **Dryad (general research data)** | `relatedPublication` (DOI URL), `distribution` (array of files: each with `contentUrl`, `encodingFormat`, `license`, optional `url`), `url` (landing page), `isAccessibleForFree`: true (or false if embargoed) |
| **Other** | Add any domain‑specific fields the scenario mentions, always using a **registered ontology/controlled‑vocabulary IRI** (e.g., OBI, DDI, OBO). If no specific IRI exists, use a clear URL under the repository’s domain. |

#### 2.2 Add **best‑practice fields** (always include)
```json
  "accessRights": "https://doi.org/10.5281/zenodo.12345",   // point to the official data‑use agreement
  "isAccessibleForFree": <true|false>,
  "distribution": [
    {
      "@type": "DataDownload",
      "contentUrl": "<URL to file or zip>",
      "encodingFormat": "<MIME type, e.g., application/zip>",
      "license": "<same as dataset license>"
    }
    /* repeat for each file if known */
  ],
  "citation": "{Authors}. {Year}. {Study Title}. {Repository}. doi:{DOI}. Version {Version}.",
  "version": {
    "@type": "PropertyValue",
    "value": <int>,
    "dateModified": "<ISO‑8601>"
  },
  "url": "<Human‑readable landing‑page URL>",
```

#### 2.3 Close the JSON object
```json
}
```

### 3️⃣ **API SPECIFICATION** (Blueprint §3.2)

Produce a **compact Markdown block** that contains:

#### 3.1 Main retrieval endpoint
```http
GET https://<repo-host>/api/v1/studies/{pid}
Accept: application/ld+json, application/json
Authorization: Bearer <OAuth‑2.0 token>
```
- **Path Parameter** table (as in the prompt, PID may be DOI or native ID).
- **Query Parameters** table (always include `version`, `page`, `pageSize`, `filter`). Enforce `pageSize ≤ 100`.
- **Supported `Accept` values** should be listed.

#### 3.2 Responses
- `200 OK` – JSON‑LD payload (include a note that the response `@context` is the same as in the record).
- `403 Forbidden` – Explain that the token must contain scopes matching every code in `dataUseLimitation` / `accessRights` (e.g., `datause:GRU`). Mention embargo handling where relevant.
- `404 Not Found` – PID does not exist or is withdrawn/embargoed.
- `400 Bad Request` – Invalid query parameters.
- **Headers**: `Link` header for pagination (`<...>; rel="next"`, `<...>; rel="prev"`).

#### 3.3 Version‑listing endpoint
```http
GET https://<repo-host>/api/v1/studies/{pid}/versions
Accept: application/json
```
Response: array of `{ "version": <int>, "dateModified": "<ISO‑8601>", "doi": "<doi>", "accessLevel": "<public|restricted|embargoed>" }`.

#### 3.4 Access‑control note (required)
State that **OAuth2** with scope `datause:<code>` is mandatory; for public/open datasets the endpoint may be accessed without a token.

### 4️⃣ **CITATION TEMPLATE & EXAMPLE**

Provide a **single‑line template** exactly as:

```
{Authors}. {Year}. {Study Title}. {Repository}. doi:{DOI}. Version {Version}.
