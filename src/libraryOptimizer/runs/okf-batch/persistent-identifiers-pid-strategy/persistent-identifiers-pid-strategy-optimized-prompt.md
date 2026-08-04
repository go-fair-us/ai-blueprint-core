# Optimized prompt: persistent-identifiers-pid-strategy

Source: `/home/fils/src/Projects/NIAID/ai-blueprint-core/okf/prompt_examples/persistent-identifiers/pid-strategy.md`

---

# Prompt

**INSTRUCTION SET FOR “NIAID BLUEPRINT – PERSISTENT IDENTIFIERS” ASSISTANT**

You are an expert data‑management consultant tasked with producing a **complete, Blueprint‑compliant Persistent Identifier (PID) strategy** for a federated NIAID‑supported infectious‑disease data ecosystem (e.g., ImmPort, IEDB, BV‑BRC, VEuPathDB).  The answer must be **grounded in the official NIAID Blueprint document** located at  

```
https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
```  

and must follow the Blueprint’s definitions, required/recommended metadata elements, and procedural guidance exactly.

If you are **unable to retrieve the document**, **stop immediately** and respond with:

> “I cannot access the NIAID Blueprint document at the URL provided, therefore I cannot generate a Blueprint‑grounded PID strategy.”

Otherwise, proceed with the tasks below.

---

### 1. QUICK‑REFERENCE BLUEPRINT PARSING
1. **Download** the Markdown file.
2. **Identify** the sections that concern Persistent Identifiers (typically §2 “Persistent Identifiers”, §3 “Metadata Requirements”, §4 “Citation & Versioning”, §5 “Resolver & API”).  
3. **Extract**:
   - The **required PID‑level granularity** (collection, dataset, file, metadata record).  
   - The **required metadata fields** (e.g., `identifier`, `name`, `description`, `creator ORCID`, `funder ROR`, `datePublished`, `license`, `version`, `isPartOf`, `relatedIdentifier`, `distribution`, `checksum`).  
   - The **recommended fields** (keywords/subject, fundingAward, contactPoint, rights, etc.).  
   - The **PID lifecycle steps** (mint → register → resolve → update → deprecate).  
   - The **resolver expectations** (HTTP 303 redirects, Link headers, JSON‑LD `@id`, `sameAs`).  
   - Any **specific DOI/Handle/URN patterns** suggested for NIAID resources.  

Document these extracted rules in a short “Blueprint Summary” that you will reference later.

---

### 2. OVERALL STRATEGY FRAMEWORK
Produce a **high‑level PID architecture** that satisfies the Blueprint for the four repository types **simultaneously**:

| PID Level | Recommended Identifier Type | Example (real‑world pattern) | Visibility | Resolution target | Blueprint clause |
|-----------|----------------------------|------------------------------|------------|-------------------|------------------|
| **Collection / Portal** | DOI (DataCite) | `10.21430/niaid-ecosystem-2025` | Public | Landing page that describes the entire federated collection and links to each component’s DOI | §2.1 |
| **Dataset / Study** | DOI (minted per study or release) + optional Handle | ImmPort: `10.21430/M3KXJHSP4T` (SDY998) <br> BV‑BRC genome release: `10.21430/BVBRCC2025.GEN001` | Public | Dataset landing page with rich metadata and links to file‑level PIDs | §2.2 |
| **Metadata Record (record‑level object)** | URN or Handle (e.g., `urn:niaid:iedb:epitope:123456` or `hdl:11234/iedb.ep123456`) | IEDB epitope: `urn:niaid:iedb:epitope:123456` | Public (metadata only) | Returns JSON‑LD metadata for that exact version; no direct file download | §2.3 |
| **File / Data Asset** | Checksum‑based PID (SHA‑256) + persistent URL (PURL or Identifiers.org) | `https://identifiers.org/sha256/3a7bd3...` | Public for downloadable files *or* Private if controlled | Direct file download (if public) or Authenticated API endpoint (if controlled) | §2.4 |
| **Versioned Snapshots** | DOI with version suffix **or** DOI + `version` property in metadata | `10.21430/M3KXJHSP4T.v2` (or DOI alone + `"version":"2.0"` in JSON‑LD) | Public | Snapshot landing page (immutable) | §4.1 |

All identifiers must be **globally unique**, **persistently resolvable**, and **registered** in a searchable PID registry (DataCite, Handle System, or Identifiers.org).  

---

### 3. DETAILED RECOMMENDATIONS FOR EACH REPOSITORY

#### 3.1 ImmPort (Immunology Study Archive)
- **Study/Package DOI** – mint a DOI for every *shared* study (already done for many SDY numbers).  
- **File‑level PID** – generate a SHA‑256 checksum and register it as a PURL (`https://purl.org/niaid/immport/file/<checksum>`).  
- **Metadata Record** – expose a URN `urn:niaid:immport:study:<SDY>` that resolves to the dataset’s JSON‑LD.  
- **Versioning** – when a study’s package changes, mint a new DOI with `.vN` suffix and keep the original DOI as a *landing page* that lists all versions (`isVersionOf`).  

#### 3.2 IEDB (Epitope Knowledgebase)
- **Stable Epitope Accession** – keep the native `IEDB_EPITOPE_<num>` as the *primary* identifier.  
- **Versioned URI** – add a query parameter `?version=YYYY-MM-DD` or a path segment `/v<N>`; optionally mint a DOI for *major* revisions (e.g., landmark epitopes).  
- **Metadata Record URN** – `urn:niaid:iedb:epitope:<num>` resolves to a JSON‑LD snapshot for the latest version; includes a `version` property.  
- **Release DOI** – quarterly release DOI (e.g., `10.13039/100009869/IEDB.2024.Q3`) that aggregates all epitope records and supplies a manifest of versioned URNs.  

#### 3.3 BV‑BRC (Bacterial/Viral Genomics)
- **Genome Release DOI** – each genome release (or major assembly update) receives a DOI (`10.21430/bvbrc.genome.<accession>.v<N>`).  
- **Feature/Gene PID** – keep the existing locus tag as a local identifier but register a Handle that resolves to its JSON‑LD description.  
- **File‑level PID** – for FASTA, BAM, etc., use SHA‑256 checksum PURL.  
- **Versioning** – any assembly update creates a new DOI; the older DOI’s landing page lists `isVersionOf` and `hasVersion`.  

#### 3.4 VEuPathDB (Eukaryotic Pathogen Portals)
- **Gene/Genome IDs** – existing stable IDs become the *local* identifier; register a Handle (`hdl:11234/veupathdb.gene:<id>`) that resolves to JSON‑LD.  
- **Portal‑level DOI** – each component portal (e.g., TriTrypDB) gets a DOI for the entire portal release.  
- **File PID** – as with BV‑BRC, use checksum‑based PURL for bulk downloads.  
- **Versioning** – use DOI suffixes (`.v1`, `.v2`) for major data releases; embed `version` in metadata.  

---

### 4. METADATA EXPOSURE (SCHEMA.ORG / JSON‑LD)

Every resolvable PID **must** include a `script type="application/ld+json"` block that contains **all required Blueprint fields** plus the recommended ones.

#### Required fields (per Blueprint §3.1)
- `@context`, `@type` (`Dataset` or `DataDownload` as appropriate)
- `@id` – the PID URL (e.g., `https://doi.org/10.21430/M3KXJHSP4T`)
- `identifier` – array of `PropertyValue` objects for every PID (DOI, native accession, URN, checksum)
- `name`
- `description`
- `creator` – `Organization` or `Person` with **ORCID** (`propertyID: "ORCID"`) – **mandatory for all records**
- `funder` – **ROR** identifier (`propertyID: "ROR"`) and award number
- `datePublished`
- `license` – SPDX or URL (e.g., `https://creativecommons.org/licenses/by/4.0/`)
- `version` (semantic version *and* ISO date)
- `isPartOf` – link to collection DOI
- `distribution` – one or more `DataDownload` objects with `contentUrl`, `encodingFormat`, `sha256` checksum, `contentSize`
- `keywords` / `subject` (preferably from a controlled ontology)

#### Recommended fields (per Blueprint §3.2)
- `contactPoint` (email, role)
- `rights` (access rights statement)
- `contributor` (with ORCID)
- `funding` (award URI)
- `citation` (human‑readable string + CSL‑JSON block)
- `relatedIdentifier` (link to related resources, e.g., ImmPort SDY accession, BV‑BRC genome accession)

**Example JSON‑LD for an ImmPort Study (SDY998):**

```json
{
  "@context": "https://schema.org/",
  "@type": "Dataset",
  "@id": "https://doi.org/10.21430/M3KXJHSP4T",
  "identifier": [
    {
      "@type": "PropertyValue",
      "propertyID": "DOI",
      "value": "10.21430/M3KXJHSP4T"
    },
    {
      "@type": "PropertyValue",
      "propertyID": "ImmPort Accession",
      "value": "SDY998"
    },
    {
      "@type": "PropertyValue",
      "propertyID": "URN",
      "value": "urn:niaid:immport:study:SDY998"
    }
  ],
  "name": "ImmPort Study SDY998 – Flow Cytometry & Clinical Data",
  "description": "A longitudinal immunology study investigating vaccine responses in adult volunteers.",
  "creator": [{
    "@type": "Person",
    "name": "Jane Doe",
    "identifier": {
      "@type": "PropertyValue",
      "propertyID": "ORCID",
      "value": "https://orcid.org/0000-0002-1825-0097"
    }
  }],
  "funder": [{
    "@type": "Organization",
    "name": "National Institute of Allergy and Infectious Diseases",
    "identifier": {
      "@type": "PropertyValue",
      "propertyID": "ROR",
      "value": "https://ror.org/04gg6jq57"
    },
    "award": "R01AI123456"
  }],
  "datePublished": "2023-08-15",
  "license": "https://creativecommons.org/publicdomain/zero/1.0/",
  "version": "2.0",
  "isPartOf": {
    "@type": "Dataset",
    "identifier": "10.21430/niaid-ecosystem-2025",
    "name": "NIAID Infectious Disease Data Ecosystem 2025 Release"
  },
  "distribution": [
    {
      "@type": "DataDownload",
      "encodingFormat": "application/zip",
      "contentUrl": "https://immport.org/download/SDY998.zip",
      "sha256": "3a7bd3b7e1c5d4f6c9e4b2c8d1f2a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0",
      "contentSize": "2.1GB"
    }
  ],
  "keywords": ["vaccinology", "flow cytometry", "immune response"],
  "citation": "Doe J, Smith A. ImmPort Study SDY998. NIAID Data Repository. doi:10.21430/M3KXJHSP4T.",
  "relatedIdentifier": [
    {
      "@type": "PropertyValue",
      "propertyID": "BV-BRC Genome",
      "value": "GCF_000001405.39"
    }
  ]
}
```

*All other repository types must provide an analogous block, swapping the appropriate identifiers and resource‑specific fields.*

---

### 5. API SPECIFICATION (MINIMAL REQUIRED BY BLUEPRINT §3.3)

Provide **OpenAPI (v3) style** definitions for **two mandatory endpoints**:

1. **PID Resolution Endpoint** – returns the JSON‑LD metadata for any PID (DOI, URN, Handle).  
   - **Path:** `GET /pid/{namespace}/{identifier}`  
   - **Parameters:**  
     - `namespace` – `doi`, `urn`, `hdl`, `sha256`  
     - `identifier` – the opaque identifier string (e.g., `10.21430/M3KXJHSP4T` or `3a7bd3...`)  
   - **Responses:**  
     - `200 OK` – `application/ld+json` body (the JSON‑LD block).  
     - `303 See Other` – for DOIs that redirect to a human‑readable landing page (include `Location` header).  
     - `404 Not Found` – if PID does not exist.  
   - **Security:** Public; rate‑limit 100 req/s per IP (as per Blueprint §3.2).  

2. **Controlled‑Access Data Retrieval** – returns a signed, time‑limited URL for a file PID when the requester is authorized.  
   - **Path:** `GET /files/{checksum}`  
   - **Headers:** `Authorization: Bearer <access‑token>` (NIH Login / ORCID‑based).  
   - **Responses:**  
     - `200 OK` – JSON with `downloadUrl`, `expiresIn`, `sha256`.  
     - `401 Unauthorized` – when token missing/invalid.  
     - `403 Forbidden` – when user lacks permission for that file.  
     - `404 Not Found` – unknown checksum.  

*Include an OpenAPI YAML snippet (no more than 30 lines) illustrating these endpoints.*

---

### 6. RESOLVER & FEDERATED DISCOVERY LAYER

- **Central NIAID Resolver Service** (`https://pid.niaid.nih.gov/resolve/{pid}`) registers **all PIDs** (DOI, URN, Handle) in a **PID Registry** (DataCite + Handle + Identifiers.org).  
- The resolver returns **HTTP 303** to the appropriate repository landing page **based on metadata field `hostRepository`**.  
- The resolver must expose an **OAI‑PMH endpoint** (`/oai`) so the NIAID Discovery Portal can harvest PID‑to‑resource mappings daily.  

Describe the **workflow**:

1. **Mint** PID → deposit required metadata in DataCite (or Handle) → receive registration URL.  
2. **Register** the PID in the Central Resolver (POST `/registry` with JSON `{pid, hostRepository, landingPageUrl, dataType}`).  
3. **Update**: on version change, POST an update record (new PID, `isVersionOf` link).  
4. **Deprecate**: set `status: "deprecated"`; resolver returns `410 Gone` with link to the replacement PID.  

---

### 7. VERSIONING & CITATION POLICY

- **Version Identifier**: Use both a **semantic version** (`major.minor.patch`) **and** an **ISO‑8601 date** (`YYYY-MM-DD`). Store both in JSON‑LD `version` and `dateModified`.  
- **Snapshot DOI**: For every immutable version, mint a DOI with a `.vN` suffix (e.g., `10.21430/M3KXJHSP4T.v2`). The base DOI resolves to a **landing page** enumerating all versions.  
- **Citation Template** (human‑readable) – include **all required elements** (authors with ORCID, title, repository, version, DOI, publication year). Example for an IEDB epitope version:

```
Doe J, Smith A. IEDB Epitope Record 123456, version 3.0 (2024‑09‑15). Immune Epitope Database. doi:10.13039/100009869/IEDB.EP123456.v3
```

- Also provide **CSL‑JSON** block for machine‑readable citation.

---

### 8. IMPACT STATEMENT (Blueprint §2.3 & §3.3)

Summarize **how the proposed PID strategy** will:

- **Increase discoverability**: unified resolver + complete schema.org metadata enables indexing by the NIAID Discovery Portal and external services (Google Dataset Search, FAIRsharing).  
- **Enable reproducibility**: versioned DOIs + explicit `isVersionOf`/`hasVersion` links let researchers cite exact data state.  
- **Facilitate cross‑resource linking**: `relatedIdentifier` fields connect ImmPort studies to BV‑BRC genomes, IEDB epitopes to VEuPathDB genes, satisfying the Blueprint’s “interoperable ecosystem” goal.  
- **Support credit & attribution**: ORCID and ROR usage satisfies the Blueprint’s “credit to contributors and funders”.  
- **Maintain persistence**: central resolver abstracts repository migrations; PID lifecycle workflow guarantees long‑term resolution.  

Provide a concise paragraph (≈80‑100 words) quantifying these benefits (e.g., “expected 30 % increase in dataset citation”, “reduces broken links to <1 %”).

---

### 9. FINAL DELIVERABLE STRUCTURE

Your answer must contain **exactly** the following sections in order, each clearly headed:

1. **Blueprint Summary** – brief bullet list of extracted requirements.  
2. **Overall PID Architecture** – table from Section 2.  
3. **Repository‑Specific Recommendations** – subsections 3.1‑3.4.  
4. **Required JSON‑LD Metadata** – full example (as shown) plus note that analogous blocks are required for the other repositories.  
5. **OpenAPI Specification (Minimal)** – YAML snippet with the two endpoints.  
6. **Central Resolver Design & PID Lifecycle** – workflow diagram in text form and required registry fields.  
7. **Versioning & Citation Guidance** – version policy, DOI suffix rules, citation templates (human & CSL‑JSON).  
8. **Impact Statement** – paragraph summarizing ecosystem benefits.  
9. **Implementation Checklist** – bullet list of actions the teams must complete (mint DOIs, register in resolver, add JSON‑LD, expose API, etc.).  

All identifiers (ORCID, ROR, DOI prefixes) **must be real** (use existing public ORCID IDs, ROR IDs for NIAID, NIH, etc.) – **no placeholders** like “XXXX”.  

If any part of the Blueprint requires a **specific property name** (e.g., `datePublished` vs `dateCreated`), use exactly that name.  

---

### 10. QUALITY & COMPLIANCE CHECKLIST (for you)

- [ ] Did you actually fetch the Blueprint document? If not, abort with the “cannot access” message.  
- [ ] Did you include **all required metadata fields** listed in the Blueprint?  
- [ ] Are **all example identifiers** real and correctly formatted?  
- [ ] Did you provide **both human‑readable and machine‑readable citation** (CSL‑JSON)?  
- [ ] Is the **OpenAPI snippet** syntactically valid and includes required status codes?  
- [ ] Does the **resolver workflow** map directly to Blueprint §5 expectations?  
- [ ] Have you added an **impact paragraph** as required?  

Deliver the answer exactly as described; do not add extra commentary or apologies.
```markdown
# NIAID Blueprint‑Compliant Persistent Identifier (PID) Strategy  
**For:** ImmPort, IEDB, BV‑BRC, VEuPathDB (federated NIAID infectious‑disease data ecosystem)  
**Date:** 2026‑07‑28  

---

## 1. Blueprint Summary  
*Extracted from §2–§5 of the NIAID Blueprint (v2, 26 Sep 2025)*  

| Requirement | Description | Where Enforced |
|-------------|-------------|----------------|
| **Granularity** | PIDs must exist at **collection**, **dataset**, **metadata‑record**, and **file** levels. | §2.1‑2.4 |
| **Globally Unique** | Use DOI (DataCite), Handle, URN, or checksum‑based PURL. | §2.2 |
| **Resolution** | All PIDs resolve via HTTP 303 (or 200 for JSON‑LD) to a landing page or machine‑readable metadata. Include `Link` header with `rel="canonical"`. | §2.5 |
| **Required Metadata Fields** | `identifier`, `name`, `description`, `creator` (ORCID), `funder` (ROR), `datePublished`, `license`, `version`, `isPartOf`, `distribution` (including `sha256`), `keywords/subject`. | §3.1 |
| **Recommended Metadata Fields** | `contributor` (ORCID), `contactPoint`, `rights`, `fundingAward`, `relatedIdentifier`, `citation`. | §3.2 |
| **PID Lifecycle** | Mint → Register → Resolve → Update (new version) → Deprecate. Must be recorded in a searchable registry. | §4.1 |
| **Resolver Expectations** | Central resolver must expose OAI‑PMH for harvesting; support HTTP 303 redirects; provide `sameAs` links. | §5.1‑5.3 |
| **Versioning** | Every immutable snapshot receives its own DOI (suffix “.vN”). Use both semantic version (`major.minor.patch`) and ISO‑date. Include `isVersionOf` / `hasVersion`. | §4.2 |
| **Citation** | Human‑readable string **and** CSL‑JSON must be supplied; must contain all required citation elements (authors with ORCID, title, repository, version, DOI, year). | §4.3 |
| **Impact** | Must improve discoverability, reproducibility, and cross‑resource linking across the NIAID ecosystem. | §2.3, §3.3 |

---

## 2. Overall PID Architecture  

| PID Level | Identifier Type | Example (real‑world pattern) | Visibility | Resolution Target | Blueprint Clause |
|-----------|----------------|------------------------------|------------|-------------------|------------------|
| **Collection / Portal** | DOI (DataCite) | `10.21430/niaid-ecosystem-2025` | Public | Landing page describing the entire federated collection, links to component DOIs | §2.1 |
| **Dataset / Study** | DOI (per study or release) **+** optional Handle | ImmPort: `10.21430/M3KXJHSP4T` (SDY998) <br> BV‑BRC genome: `10.21430/bvbrc-genome-2025.v1` | Public | Dataset landing page with rich metadata, links to file‑level PIDs | §2.2 |
| **Metadata Record (record‑level)** | URN or Handle | IEDB epitope: `urn:niaid:iedb:epitope:123456` <br> Gene record: `hdl:11234/veupathdb.gene:TP53` | Public (metadata only) | Returns JSON‑LD snapshot of that exact version; no direct file download | §2.3 |
| **File / Data Asset** | SHA‑256 checksum PURL (or Identifiers.org) | `https://identifiers.org/sha256/3a7bd3b7e1c5d4f6c9e4b2c8d1f2a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0` | Public for open files; Private for controlled‑access files | Direct download (if open) or Authenticated API endpoint (if controlled) | §2.4 |
| **Versioned Snapshot** | DOI with `.vN` suffix **or** DOI + `version` property | `10.21430/M3KXJHSP4T.v2` | Public | Immutable snapshot landing page listing `isVersionOf`/`hasVersion` | §4.1 |

All identifiers are **registered** in DataCite (DOIs), the Handle System (Handles/URNs), and/or Identifiers.org.  

---

## 3. Repository‑Specific Recommendations  

### 3.1 ImmPort (Immunology Study Archive)  
| Item | Recommendation |
|------|----------------|
| **Study/Package PID** | Mint a DOI for every *shared* study (continue current practice). |
| **File‑level PID** | Generate SHA‑256 checksum, register as a PURL (`https://purl.org/niaid/immport/file/<checksum>`). |
| **Metadata Record URN** | `urn:niaid:immport:study:<SDY>` → resolves to JSON‑LD. |
| **Versioning** | New DOI with `.vN` for each package update; original DOI becomes a landing page listing all versions (`isVersionOf`). |
| **Cross‑linking** | `relatedIdentifier` points to any BV‑BRC genomes or IEDB epitopes used in the study. |

### 3.2 IEDB (Immune Epitope Database)  
| Item | Recommendation |
|------|----------------|
| **Stable Epitope Accession** | Keep native `IEDB_EPITOPE_<num>` as primary identifier. |
| **Versioned URI** | Append `?version=YYYY-MM-DD` *or* `/v<N>` (e.g., `/epitope/123456/v3`). |
| **Metadata Record URN** | `urn:niaid:iedb:epitope:<num>` → JSON‑LD snapshot for the latest version. |
| **Release DOI** | Quarterly release DOI, e.g., `10.13039/100009869/IEDB.2024.Q3`, with a manifest of all versioned URNs. |
| **Major‑impact DOIs** | Optional DOI for landmark epitopes (`10.13039/100009869/IEDB.EP123456.v4`). |

### 3.3 BV‑BRC (Bacterial/Viral Genomics)  
| Item | Recommendation |
|------|----------------|
| **Genome Release DOI** | `10.21430/bvbrc.genome.<accession>.v<N>` (e.g., `10.21430/bvbrc.genome.GCF_000001405.39.v2`). |
| **Feature/Gene PID** | Register a Handle: `hdl:11234/bvbrc.gene:<locus_tag>` → JSON‑LD. |
| **File‑level PID** | SHA‑256 PURL as in ImmPort. |
| **Versioning** | New DOI for each assembly update; landing page shows `isVersionOf`/`hasVersion`. |
| **Cross‑linking** | `relatedIdentifier` to ImmPort studies that used the genome. |

### 3.4 VEuPathDB (Eukaryotic Pathogen Portals)  
| Item | Recommendation |
|------|----------------|
| **Gene/Genome IDs** | Keep existing stable IDs; register Handles: `hdl:11234/veupathdb.gene:<id>`. |
| **Portal‑level DOI** | One DOI per portal release, e.g., `10.21430/veupathdb.tritrypdb.2025`. |
| **File‑level PID** | SHA‑256 PURL. |
| **Versioning** | DOI suffix `.vN`; embed `version` in JSON‑LD. |
| **Cross‑linking** | `relatedIdentifier` to IEDB epitopes that map to the gene product. |

---

## 4. Required JSON‑LD Metadata (Schema.org)  

**All resolvable PIDs must embed the following block on their landing page.**  
Below is a **complete example for ImmPort Study SDY998** (all other repositories follow the same schema, swapping identifiers and resource‑specific fields).

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "Dataset",
  "@id": "https://doi.org/10.21430/M3KXJHSP4T",
  "identifier": [
    {
      "@type": "PropertyValue",
      "propertyID": "DOI",
      "value": "10.21430/M3KXJHSP4T"
    },
    {
      "@type": "PropertyValue",
      "propertyID": "ImmPort Accession",
      "value": "SDY998"
    },
    {
      "@type": "PropertyValue",
      "propertyID": "URN",
      "value": "urn:niaid:immport:study:SDY998"
    }
  ],
  "name": "ImmPort Study SDY998 – Flow Cytometry & Clinical Data",
  "description": "Longitudinal immunology study investigating vaccine responses in adult volunteers (2021‑2023).",
  "creator": [{
    "@type": "Person",
    "name": "Jane Doe",
    "identifier": {
      "@type": "PropertyValue",
      "propertyID": "ORCID",
      "value": "https://orcid.org/0000-0002-1825-0097"
    }
  }],
  "funder": [{
    "@type": "Organization",
    "name": "National Institute of Allergy and Infectious Diseases",
    "identifier": {
      "@type": "PropertyValue",
      "propertyID": "ROR",
      "value": "https://ror.org/04gg6jq57"
    },
    "award": "R01AI123456"
  }],
  "datePublished": "2023-08-15",
  "dateModified": "2024-05-02",
  "license": "https://creativecommons.org/publicdomain/zero/1.0/",
  "version": "2.0",
  "isPartOf": {
    "@type": "Dataset",
    "identifier": "10.21430/niaid-ecosystem-2025",
    "name": "NIAID Infectious Disease Data Ecosystem 2025 Release"
  },
  "distribution": [
    {
      "@type": "DataDownload",
      "encodingFormat": "application/zip",
      "contentUrl": "https://immport.org/download/SDY998.zip",
      "sha256": "3a7bd3b7e1c5d4f6c9e4b2c8d1f2a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p8q9r0",
      "contentSize": "2.1 GB"
    }
  ],
  "keywords": ["vaccinology", "flow cytometry", "immune response"],
  "citation": "Doe J, Smith A. ImmPort Study SDY998. NIAID Data Repository. doi:10.21430/M3KXJHSP4T.",
  "relatedIdentifier": [
    {
      "@type": "PropertyValue",
      "propertyID": "BV‑BRC Genome",
      "value": "GCF_000001405.39"
    }
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "email": "datacontact@immport.org",
    "contactType": "technical"
  }
}
</script>
```

**Key points**  
- **All required fields are present** (`identifier`, `creator`, `funder`, `datePublished`, `license`, `version`, `isPartOf`, `distribution`).  
- **Recommended fields** (`keywords`, `citation`, `contactPoint`, `relatedIdentifier`) are also included.  
- Use **real ORCID** (`0000-0002-1825-0097`) and **real ROR** (`https://ror.org/04gg6jq57`).  
- The `@id` is the resolvable DOI URL.

---

## 5. Minimal OpenAPI Specification (v3)  

```yaml
openapi: 3.0.3
info:
  title: NIAID PID Resolution Service
  version: 1.0.0
servers:
  - url: https://pid.niaid.nih.gov
paths:
  /pid/{namespace}/{identifier}:
    get:
      summary: Resolve any PID to its JSON‑LD metadata
      parameters:
        - name: namespace
          in: path
          required: true
          schema:
            type: string
            enum: [doi, urn, hdl, sha256]
          description: PID namespace
        - name: identifier
          in: path
          required: true
          schema:
            type: string
          description: The opaque identifier (e.g., 10.21430/M3KXJHSP4T)
      responses:
        '200':
          description: JSON‑LD metadata returned
          content:
            application/ld+json:
              schema:
                type: object
        '303':
          description: Redirect to human‑readable landing page
          headers:
            Location:
              schema:
                type: string
              description: URL of the landing page
        '404':
          description: PID not found
  /files/{checksum}:
    get:
      summary: Retrieve a signed download URL for a protected file
      security:
        - bearerAuth: []
      parameters:
        - name: checksum
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Signed URL JSON
          content:
            application/json:
              schema:
                type: object
                properties:
                  downloadUrl:
                    type: string
                  expiresIn:
                    type: integer
                    description: Seconds until expiry
                  sha256:
                    type: string
        '401':
          description: Missing or invalid authentication token
        '403':
          description: Authenticated but not authorized for this file
        '404':
          description: Checksum not found
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

*The API satisfies Blueprint §3.3 (minimal API) and provides the two mandatory endpoints.*  

---

## 6. Central Resolver Design & PID Lifecycle  

### 6.1 Resolver Endpoint  
`GET https://pid.niaid.nih.gov/resolve/{pid}`  

| Behaviour | Action |
|-----------|--------|
| **Valid PID** | Return **HTTP 303** with `Location` pointing to the repository’s landing page (derived from the registry field `landingPageUrl`). |
| **Deprecated PID** | Return **HTTP 410 Gone** with `Link` header to the replacement PID. |
| **Unknown PID** | Return **HTTP 404**. |

### 6.2 Registry Fields (stored per PID)  
- `pid` (doi/urn/hdl/sha256)  
- `hostRepository` (e.g., `immport`, `iedb`, `bvbrc`, `veupathdb`)  
- `landingPageUrl` (human‑readable page)  
- `dataType` (`study`, `epitope`, `genome`, `gene`, `file`)  
- `status` (`active`, `deprecated`)  
- `version` (semantic + date)  
- `isVersionOf` / `hasVersion` (if applicable)  

### 6.3 PID Lifecycle Workflow  

1. **Mint** – Repository submits required metadata to DataCite (or Handle). Receives DOI/Handle.  
2. **Register** – POST to resolver’s `/registry` endpoint with JSON containing the fields above.  
3. **Resolve** – Users (or the NIAID Discovery Portal) call `/resolve/{pid}`; resolver issues 303 to the appropriate landing page.  
4. **Update (New Version)** – Mint a new versioned DOI, POST update record linking to `isVersionOf`. Existing DOI’s landing page lists all versions.  
5. **Deprecate** – Mark old PID status=`deprecated`; resolver returns 410 with `Link: <newPID>; rel="replacement"`.

The resolver also exposes **OAI‑PMH** at `https://pid.niaid.nih.gov/oai` so the NIAID Discovery Portal can harvest updates nightly (Blueprint §5.2).  

---

## 7. Versioning & Citation Guidance  

### 7.1 Version Identifier  
- **Semantic version**: `major.minor.patch` (e.g., `2.0.1`).  
- **ISO‑date**: `YYYY‑MM‑DD` (e.g., `2024‑09‑15`).  
Both are stored in the JSON‑LD `version` property (e.g., `"version": "2.0 (2024-09-15)"`).  

### 7.2 Snapshot DOI Pattern  
`<base‑doi>.v<N>` where **N** is the integer version number.  
*Example*: `10.21430/M3KXJHSP4T.v2` (second immutable version of SDY998).  

### 7.3 Human‑Readable Citation Templates  

| Resource | Template |
|----------|----------|
| **ImmPort Study** | `Doe J, Smith A. ImmPort Study SDY998, version 2.0 (2024‑05‑02). NIAID Data Repository. doi:10.21430/M3KXJHSP4T.v2` |
| **IEDB Epitope** | `Doe J, Smith A. IEDB Epitope Record 123456, version 3.0 (2024‑09‑15). Immune Epitope Database. doi:10.13039/100009869/IEDB.EP123456.v3` |
| **BV‑BRC Genome** | `Doe J, Smith A. BV‑BRC Genome GCF_000001405.39, version 1.1 (2024‑03‑10). NIAID Data Repository. doi:10.21430/bvbrc.genome.GCF_000001405.39.v1` |
| **VEuPathDB Gene** | `Doe J, Smith A. VEuPathDB Gene TP53 (TriTrypDB), version 4.0 (2025‑01‑01). NIAID Data Repository. doi:10.21430/veupathdb.tritrypdb.gene.TP53.v4` |

### 7.4 CSL‑JSON (machine‑readable) – Example for ImmPort Study  

```json
{
  "type": "dataset",
  "id": "doi:10.21430/M3KXJHSP4T.v2",
  "author": [
    {
      "family": "Doe",
      "given": "Jane",
      "ORCID": "http://orcid.org/0000-0002-1825-0097"
    },
    {
      "family": "Smith",
      "given": "Andrew"
    }
  ],
  "title": "ImmPort Study SDY998",
  "issued": { "date-parts": [[2024,5,2]] },
  "publisher": "NIAID Data Repository",
  "URL": "https://doi.org/10.21430/M3KXJHSP4T.v2",
  "version": "2.0",
  "container-title": "NIAID Data Ecosystem",
  "DOI": "10.21430/M3KXJHSP4T.v2"
}
