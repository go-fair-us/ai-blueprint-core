# Optimized prompt: metadata-schema-attribution-provenance-author

Source: `/home/fils/src/Projects/NIAID/ai-blueprint-core/okf/prompt_examples/metadata-schema/attribution-provenance/author.md`

---

# Prompt

# Assistant Instruction – Generation of Blueprint‑compliant JSON‑LD Dataset Metadata

You will be given a **scenario description** that outlines a research dataset (e.g., imaging data, sequencing data, clinical trial data) together with any explicit values that the user supplies (DOI, ORCID, ROR, dates, titles, URLs, etc.).  
Your job is to construct a **single JSON‑LD document** that conforms exactly to the NIAID “Blueprint for FAIR Dataset Metadata” (Schema.org v14) and to the additional judging rubric used in the examples above.

Below is the complete, step‑by‑step recipe you must follow. **Do not output anything other than the JSON‑LD** (no markdown fences, no explanations, no comments except those required by the schema).  

---

## 1. Top‑Level Structure

| Property | Required? | When to include | Formatting notes |
|----------|-----------|----------------|------------------|
| `@context` | ✅ | always | `"https://schema.org/"` |
| `@type` | ✅ | always | `"Dataset"` |
| `@id` | ✅ if DOI supplied | `"https://doi.org/<DOI>"` (the full DOI URL) |
| `name` | ✅ | dataset title |
| `description` | ✅ | if a separate description is supplied; otherwise repeat `name` |
| `url` | ✅ | landing‑page URL for the dataset |
| `identifier` | ✅ if DOI supplied | see **2. Identifier block** |
| `datePublished` | ✅ if supplied | `"YYYY-MM-DD"` |
| `dateModified` | ✅ if supplied | `"YYYY-MM-DD"` |
| `dateCreated` | ✅ optional – add if you have a creation date (recommended) |
| `license` | ✅ if supplied | URL if known; if only a name, map to a known SPDX URL (e.g., CC0 → `https://creativecommons.org/publicdomain/zero/1.0/`). |
| `keywords` | ✅ if supplied | array of strings |
| `measurementTechnique` | ✅ if supplied | **array** of strings (even if only one) |
| `variableMeasured` | ✅ if supplied | **array** of strings |
| `accessRights` | ✅ if supplied | `"Open Access"` or `"Controlled Access"` |
| `isAccessibleForFree` | ✅ if supplied | `true` or `false` |
| `isPartOf` | ✅ optional – dataset collection/catalog | object of type `DataCatalog` (name & url) |
| `publisher` | ✅ optional – primary repository | **Organization** object (see **3. Organization object**) |
| `provider` | ✅ optional – service delivering the data | same shape as `publisher` |
| `about` | ✅ optional – brief FAIR statement | string |
| `sameAs` | ✅ optional – alternate persistent identifier | URL or identifier string |
| `citation` | ✅ optional – use if a ready‑made citation string is supplied; otherwise construct (see § 5) |
| `version` | ✅ optional – dataset version string (e.g., `"1.0"` ) |
| `schemaVersion` | ✅ optional – URL of the Schema.org version used, e.g., `"https://schema.org/version/14.0"` |
| `funding` | ✅ optional – include only if funding details are supplied (see **4. Funding block**) |
| `distribution` | ✅ optional – at least one `DataDownload` entry; include an API endpoint (see **6. Distribution & API**) |
| `maintainer` / `contactPoint` | ✅ optional – recommended for all records (see **7. Contact**) |
| `contributor` **or** `author` `@list` | ✅ optional – only when the author list is huge (see **8. Scalable author handling**) |
| `author` | ✅ required – **single contiguous array** unless you use the external roster pattern (see § 8) |
| any **other top‑level keys** not listed here must **NOT** be emitted. |
| **Never** emit `null`, empty arrays `[]`, or empty objects `{}` – simply omit the property. |
| **Never** emit a `creator` array unless a repository forces it; if you must, place it **after** `author` and add a JSON‑LD `description` comment stating it duplicates `author`. |

---

## 2. Identifier Block (DOI)

If a DOI is provided:

```json
"identifier": {
  "@type": "PropertyValue",
  "propertyID": "DOI",                     // case‑sensitive as shown
  "value": "<DOI raw, no https://doi.org/>",
  "url": "https://doi.org/<DOI>"
}
```

*If no DOI is supplied, omit the entire `identifier` block and the `@id` field.*

---

## 3. Building the `author` Array  

The `author` key must contain **exactly one array** (unless you use the external‑roster pattern, see § 8). The array may include **Person** and **Organization** objects, each following the shapes below.

### 3.1 Person Object (required fields)

```json
{
  "@type": "Person",
  "name": "<display name or placeholder>",
  "identifier": {
    "@type": "PropertyValue",
    "propertyID": "ORCID",
    "value": "<ORCID raw 16‑digit string without hyphens>",
    "url": "https://orcid.org/<ORCID hyphenated>"
  },
  "affiliation": <Affiliation block>,   // see below
  "role": {
    "@type": "Role",
    "roleName": "<Exact role term>"
  }
}
```

**Name placeholder** (used when no name is supplied):

```json
"name": "Person (ORCID: 0000-0000-0000-0000)"
```

*(Replace the hyphenated ORCID with the actual one.)*

#### Affiliation block  
- The schema allows a **single** object or an **array** of objects. Use an **array** when the person has multiple affiliations (as in the ImmPort scenario).  
- Each affiliation is an **Organization** object (see § 3.2).  
- If an affiliation supplies a full ROR URL, strip the leading `https://ror.org/` to obtain the raw value for `value`.  
- **If no ROR can be resolved**, omit the `identifier` sub‑object entirely but keep the `name`.

### 3.2 Organization Object (required fields)

```json
{
  "@type": "Organization",
  "name": "<Organization name>",
  "identifier": {                     // omit if ROR unknown
    "@type": "PropertyValue",
    "propertyID": "ROR",
    "value": "<ROR raw (9‑character code)>",
    "url": "https://ror.org/<ROR>"
  },
  "role": {
    "@type": "Role",
    "roleName": "<Role term – e.g., Hosting Repository, Funding Agency, Consortium>"
  },
  "url": "<official website URL if supplied>"
}
```

### 3.3 Ordering & Role Rules  

1. **Corresponding Author** **must be first** in the `author` array.  
2. All remaining persons follow the order given in the input scenario (or the order you infer from the narrative).  
3. Use the **exact role strings** supplied in the scenario. If none are supplied, choose a Blueprint‑approved term (case‑sensitive) from the list:  

   `Corresponding Author`, `Principal Investigator`, `Co‑Investigator`, `Data Curator`, `Field Worker`, `Data Analyst`, `Data Manager`, `Contributor`, `Reviewer`, `Hosting Repository`, `Funding Agency`, `Consortium`, etc.

---

## 4. Funding Block (optional)

Include **only** when funding data are present.

```json
"funding": {
  "@type": "MonetaryGrant",
  "funder": {
    "@type": "Organization",
    "name": "<Funder name>",
    "identifier": {
      "@type": "PropertyValue",
      "propertyID": "ROR",
      "value": "<ROR raw>",
      "url": "https://ror.org/<ROR>"
    }
  },
  "grantId": "<grant identifier>"
}
```

If the funder’s ROR is unknown, omit its `identifier` sub‑object.

---

## 5. Citation Construction (when not supplied)

If the user does **not** provide a ready‑made citation string, build one using this pattern:

```
<LastName1>, <F.Initial1>., <LastName2>, <F.Initial2>., … (<Year>). <Dataset title>. <Repository name>. https://doi.org/<DOI>
```

- Extract last name and first initial from each person’s `name`.  
- Use the year from `datePublished`.  
- Use the repository name from the `publisher.name` (or `isPartOf.name` if publisher absent).  
- Insert the full DOI URL.  
- Place the resulting string in the `citation` property (as a plain string).

---

## 6. Distribution & Minimal API Description  

### 6.1 Primary JSON‑LD endpoint (mandatory)

```json
"distribution": {
  "@type": "DataDownload",
  "encodingFormat": "application/ld+json",
  "contentUrl": "<API endpoint that returns this exact JSON‑LD>"
}
```

### 6.2 Data file download (optional but encouraged)

Add a second `DataDownload` entry (as an **array** under `distribution` if you also need a file download).

```json
{
  "@type": "DataDownload",
  "encodingFormat": "<MIME type, e.g., application/dicom, text/csv>",
  "contentUrl": "<URL to bulk download or API endpoint for files>"
}
```

### 6.3 Minimal API specification (highly recommended)

```json
"api": {
  "@type": "EntryPoint",
  "urlTemplate": "https://<host>/api/metadata/{datasetId}.jsonld",
  "encodingFormat": "application/ld+json",
  "httpMethod": "GET",
  "description": "Returns JSON‑LD metadata for the dataset. Supports `page` and `per_page` query parameters for paginated author lists."
}
```

If you add `api`, ensure it is **top‑level** (same level as `distribution`).

---

## 7. Contact / Maintainer (recommended)

```json
"maintainer": {
  "@type": "Organization",
  "name": "<Repository or responsible org>",
  "email": "mailto:<support@domain.org>",
  "url": "<support web page>"
}
```

or, using `contactPoint`:

```json
"contactPoint": {
  "@type": "ContactPoint",
  "email": "mailto:<support@domain.org>",
  "contactType": "Technical Support",
  "url": "<support web page>"
}
```

Include **one** of the two; both is unnecessary.

---

## 8. Scalable Author Handling (hundreds of contributors)

When the scenario mentions **hundreds of contributors**:

1. **Keep the core lead authors** (e.g., Corresponding Author, Principal Investigators) **directly** in the `author` array, **before** any reference.
2. **Add a single reference** to an external roster **using ONE** of the following patterns **(do NOT use both)**:

   **Pattern A – `contributor` property**

   ```json
   "contributor": {
     "@type": "DataCatalog",
     "url": "https://example.org/consortium-authors.jsonld"
   }
   ```

   **Pattern B – `author` @list reference**

   ```json
   "author": {
     "@list": [
       {
         "@type": "DataCatalog",
         "url": "https://example.org/consortium-authors.jsonld"
       }
     ]
   }
   ```

   The external JSON‑LD file must contain a valid `author` list following the same Blueprint shapes, but you do **not** need to produce that file here.

3. **If you use Pattern B**, place the lead authors **before** the `@list` reference by converting the whole `author` field into an array that starts with the lead author objects, followed by a **single** object of the form:

   ```json
   {
     "@type": "DataCatalog",
     "url": "https://example.org/consortium-authors.jsonld"
   }
