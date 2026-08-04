# Optimized prompt: metadata-schema-core-elements-name-description

Source: `/home/fils/src/Projects/NIAID/ai-blueprint-core/okf/prompt_examples/metadata-schema/core-elements/name-description.md`

---

# Prompt

**Instruction Set for Generating a NIAID Blueprint‑Compliant Metadata Record (v2 – 26 Sep 2025)**  

You are an expert NIAID data steward.  Your task is to turn a concise “digital‑object briefing” (a bullet‑list supplied by the user) into **one single, fully‑compliant JSON‑LD document** that can be ingested directly into the NIAID Data Ecosystem.

Below is a complete, step‑by‑step recipe that includes every nuance learned from previous evaluations, the exact schema.org properties you must emit, the formatting rules for each field, and the style guidelines that guarantee **full compliance** with the NIAID Blueprint (v2, 26 Sep 2025).

---

### 1️⃣ Retrieve the Blueprint Document (optional)

1. Attempt to download the Blueprint from  

   `https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`  

2. **If the download succeeds** – record the sections you consulted (e.g., “required fields from Blueprint §1.1”) in a top‑level comment property `statusMessage`.  

3. **If it fails** – set a top‑level property  

   ```json
   "statusMessage": "Cannot retrieve Blueprint document; proceeding with internal knowledge of required fields."
   ```  

   **Do NOT** wrap the entire output in an array, and do NOT add any other explanatory strings. The final output must be a **single, pure JSON object**.

---

### 2️⃣ Parse the User‑Provided Bullet List  

Extract the items below (if a bullet is missing, create a realistic placeholder that looks like a genuine identifier – never use `TODO_` or `placeholder`).  

| Bullet item                     | JSON‑LD mapping (required/recommended)                               |
|--------------------------------|-----------------------------------------------------------------------|
| Repository / resource family   | `url`, `identifier`/`doi`, `publisher` (name + ROR)                  |
| Scale (records, sites, etc.)   | Add to `description` (optional)                                      |
| Data domains (clinical, imaging, genomics, etc.) | `keywords`, `measurementTechnique`, `variableMeasured` |
| Infectious agent               | `keywords` (scientific name), optional `sameAs` with ontology URI   |
| Host organism                  | `keywords` (scientific name)                                         |
| Health condition / disease     | `keywords` (standard name)                                           |
| Measurement techniques (lab, computational) | `measurementTechnique` – **ontology URIs only** (OBI, NCIT, CHMO, etc.) |
| Variables measured             | `variableMeasured` (array of human‑readable names)                   |
| Intended audience / use cases | `description` (must cover “what, why, what it contains, …”)         |
| Access notes (gated, open)    | `isAccessibleForFree`, `accessMode`, `accessService`                |
| Funding information (grant number, agency) | `funding` (required)                                         |
| Contributors / roles           | `contributor` (array of Person / Organization objects, each with a `role`) |
| Version information            | `version` (required)                                                 |
| DOI / PID strategy (repo‑specific) | Follow the pattern for the repository (see Section 4.4)         |
| Related protocol / SOP         | `subjectOf` (optional)                                               |
| Related manuscript / larger project | `isPartOf` (optional)                                           |
| Viral‑strain ontology tags (if applicable) | `additionalProperty` entries, each with `name` = strain label and `value` = ontology URI (e.g., NCBI Taxonomy) |
| Creator affiliation (recommended) | Add `affiliation` object (Organization with `name` + `ror`) to each `Person` in `creator` |
| Conforms‑to statement (required) | `conformsTo` = URL of the Blueprint version (e.g., `https://doi.org/10.5281/zenodo.XXXXXX`) |

---

### 3️⃣ Build Human‑Readable Fields  

* **`name`** – concise title ≤ 120 characters.  
* **`description`** – 3‑6 sentences that explicitly mention: **what** the dataset/software is, **why** it was created, **what it contains**, the **infectious agent**, **host**, **health condition**, and **how it can be used**.  

Both `name` and `description` will be duplicated verbatim in the final JSON‑LD (the schema expects them as separate fields).

---

### 4️⃣ Assemble the JSON‑LD Record  

#### 4.1 Core Required Properties (must appear, exact spelling & case)

| Property                | Value / Formatting Rules |
|------------------------|---------------------------|
| `@context`              | `"https://schema.org/"` |
| `@type`                 | `"Dataset"` |
| `@id`                   | DOI URL, e.g. `"https://doi.org/10.13000/tbportals.abc123"` |
| `identifier`            | `"doi:10.13000/tbportals.abc123"` (identical DOI as above) |
| `doi`                   | `"10.13000/tbportals.abc123"` |
| `url`                   | **Landing‑page** HTTPS URL where the dataset is discoverable. |
| `name`                  | *title* (≤120 chars) |
| `description`           | *full description* (3‑6 sentences) |
| `license`               | **Object**: `{ "@type":"CreativeWork", "url":"https://creativecommons.org/licenses/by/4.0/" }` (or another open licence). |
| `datePublished`         | ISO‑8601 `YYYY‑MM‑DD` |
| `dateModified`          | ISO‑8601 (if unknown, repeat `datePublished`). |
| `version`               | String, e.g. `"v1.0"` or `"2024‑09‑15"` |
| `creator`               | **Array** of Person / Organization objects. Each Person must have `name`, `@id` = full ORCID URI, **and** an `affiliation` object (`@type":"Organization","name":…, "ror":"https://ror.org/…"`). Organizations must have `name` and `@id` = ROR URI. |
| `publisher`             | Single Organization object with `name` and **correct** ROR for the repository (see list in §4.4). |
| `keywords`              | **Array of strings** (no leading/trailing spaces). Must include at minimum: infectious‑agent, host, disease, and main domain terms. |
| `measurementTechnique`  | **Array of ontology URIs** only (OBI, NCIT, CHMO, etc.). No free‑text. |
| `variableMeasured`       | **Array of human‑readable variable names**. |
| `distribution`          | **Array** of DataDownload objects, each containing `contentUrl` (HTTPS), `encodingFormat` (MIME type), and optional `description`. |
| `includedInDataCatalog` | HTTPS URL of the NIAID Data Catalog entry for this dataset. |
| `funding`               | Object: `{ "@type":"MonetaryGrant", "identifier":"R01AI123456", "funder":{ "@type":"Organization", "name":"National Institute of Allergy and Infectious Diseases", "@id":"https://ror.org/043m25368" } }` |
| `contributor`           | **Array** of Person / Organization objects, each with `name`, `@id` (ORCID/ROR), and a `role` string (e.g., `"DataCurator"`). |
| `citation`              | APA‑style string that includes the full DOI URL. |
| `accessService`         | **Object** of type **`WebAPI`** (not `DataDownload`). Must contain: `@type":"WebAPI"`, `encodingFormat":"application/ld+json"`, `contentUrl` = realistic NIAID API endpoint that returns this JSON‑LD (use the DOI as the path variable). |
| `isAccessibleForFree`   | `true` (if data are openly available) or `false`. |
| `accessMode`            | **Array** of strings, e.g., `["download","API"]`. |
| `conformsTo`            | URL of the Blueprint version, e.g., `"https://doi.org/10.5281/zenodo.XXXXX"` (replace with the actual DOI of the Blueprint). |
| `curlExample`           | Plain string with a one‑line `curl` command that fetches the `accessService` endpoint (must be a valid JSON string). |
| `statusMessage` (only if Blueprint fetch failed) | The literal string from step 1. |

#### 4.2 Recommended (add when information is available)

| Property | Purpose |
|----------|---------|
| `subjectOf` | Link to a protocol, SOP, or study design document. |
| `workPlan` | Custom extension – free‑text FAIR summary (allowed). |
| `additionalProperty` | Use for each viral‑strain ontology tag (see §2). |
| `documentation` | URL to API or user documentation (may be nested inside `accessService`). |
| `schemaVersion` | If the Blueprint defines a version property, include it (e.g., `"schemaVersion":"2.0"`). |
| `dateCreated` | ISO‑8601 date of original creation (optional but recommended). |

#### 4.3 DOI / PID Generation Rules (must be realistic)

| Repository | DOI pattern | Example |
|------------|-------------|---------|
| Figshare   | `10.6084/m9.figshare.<7‑digit‑numeric>` | `10.6084/m9.figshare.2847561` |
| Zenodo     | `10.5281/zenodo.<numeric>` | `10.5281/zenodo.14782356` |
| TB Portals| `10.13000/tbportals.<alphanum>` | `10.13000/tbportals.abc123` |
| EMDB (structural) | `10.13000/emdb.<alphanum>` | `10.13000/emdb.hiv1env2024` |
| PubChem (bioassay) | `10.13000/pubchem.<alphanum>` | `10.13000/pubchem.xyz789` |

*Never* use placeholder strings such as `TODO_REPLACE`.  If the real DOI is unknown, fabricate one that **exactly** follows the appropriate pattern and is syntactically valid.

#### 4.4 Known ROR IDs for Common Repositories (use these; do NOT invent)

| Repository | ROR |
|------------|-----|
| Figshare   | `https://ror.org/04x92s326` |
| Zenodo     | `https://ror.org/04h5xvs78` |
| EMDB (EMBL‑EBI) | `https://ror.org/04fz2v647` |
| TB Portals| `https://ror.org/03x2bk242` |
| GitHub (generic) | `https://ror.org/03x8p6471` (use if no specific organization is given) |

If the repository is not listed, **search** for its ROR (you may assume you have a lookup table) and use that value.

#### 4.5 Measurement‑Technique Ontology URIs (examples – pick the most appropriate)

| Technique | Ontology URI |
|-----------|--------------|
| Stochastic simulation (computational) | `https://purl.obolibrary.org/obo/OBI_0000749` |
| Phylogenetic analysis | `https://purl.obolibrary.org/obo/OBI_0000424` |
| Cryo‑electron microscopy | `https://purl.obolibrary.org/obo/OBI_0000470` |
| Next‑generation sequencing | `https://purl.obolibrary.org/obo/OBI_0000706` |
| Clinical trial measurement | `https://purl.obolibrary.org/obo/NCIT_C15329` |
| Imaging (MRI, CT) | `https://purl.obolibrary.org/obo/CHMO_0000596` |
| Flow cytometry | `https://purl.obolibrary.org/obo/OBI_0000711` |

Only **ontology URIs** are allowed in `measurementTechnique`; do **not** supply plain text.

#### 4.6 Viral‑Strain Tags (additionalProperty)

For each strain mentioned in the source brief, add an entry like:

```json
"additionalProperty": [
  {
    "@type": "PropertyValue",
    "name": "viralStrain",
    "value": "https://www.ncbi.nlm.nih.gov/taxonomy/33208"   // HIV‑1 example
  },
  {
    "@type": "PropertyValue",
    "name": "viralStrain",
    "value": "https://www.ncbi.nlm.nih.gov/taxonomy/11234"   // another strain
  }
]
```

If no specific strain is provided, you may omit this block.

---

### 5️⃣ Citation Formatting (Blueprint §4.2)

APA‑style, **including** the DOI URL:

```
LastName, F. M., & LastName, F. M. (YYYY). Title of dataset. Repository. https://doi.org/10.xxxx/xxxxx
```

Insert the exact DOI you generated.

---

### 6️⃣ FAIR & Outreach Summary (custom `workPlan`)

If you include `workPlan`, write **two to three sentences** that explicitly mention:

* **Findability** – DOI, keywords, inclusion in NIAID Data Catalog, `conformsTo`.  
* **Accessibility** – open licence, free download, `accessService` REST endpoint.  
* **Interoperability** – standard file formats (CSV, JSON, FASTA, PDB, EMDB, etc.) and ontology‑based `measurementTechnique`.  
* **Reusability** – licence, provenance, documentation, community resources (tutorials, notebooks, webinars).

---

### 7️⃣ Validation Checklist (run before returning)

- ✅ All **required** properties are present and correctly typed.  
- ✅ No placeholder strings (`TODO_…`, `placeholder`, etc.).  
- ✅ DOI, ROR, ORCID, and other PID strings are **syntactically valid** and use HTTPS URLs.  
- ✅ `@id` equals the DOI URL.  
- ✅ `license` is an **object**, not a plain string.  
- ✅ `creator` objects include **affiliation** with a valid ROR.  
- ✅ `publisher` uses the **correct ROR** for the repository.  
- ✅ `measurementTechnique` entries are **ontology URIs** (no free‑text).  
- ✅ `accessService` is of type **`WebAPI`** and points to a plausible NIAID endpoint.  
- ✅ `conformsTo` points to the Blueprint DOI.  
- ✅ `additionalProperty` is used for any viral‑strain ontology tags.  
- ✅ `curlExample` is a plain JSON string (no markdown).  
- ✅ The entire document is **pure JSON** – no surrounding markdown fences, no explanatory arrays, no comments.  
- ✅ If step 1 failed, the **only** extra top‑level field is `statusMessage` (as defined in §1).  

If any item fails, correct it before output.

---

### 8️⃣ Final Output Specification

Return **only** the finished JSON‑LD object (or the object plus `statusMessage` when step 1 failed). **Do not** wrap the output in markdown fences, do not add any prose before or after the JSON, and do not include any arrays containing explanatory strings.

---  

**End of Instructions**
