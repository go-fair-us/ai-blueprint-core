# Optimized prompt: metadata-schema-core-elements-identifier

Source: `/home/fils/src/Projects/NIAID/ai-blueprint-core/okf/prompt_examples/metadata-schema/core-elements/identifier.md`

---

# Prompt

{
  "@context": "https://schema.org/",
  "@type": "<TYPE>",               // “ScholarlyArticle” for pre‑prints, “Dataset” for data packages, etc.
  "name": "<Human‑readable title>",
  "description": "<Concise description>",
  "identifier": [                  // one or more PropertyValue objects
    {
      "@type": "PropertyValue",
      "propertyID": "DOI",          // or other PID type (e.g., “NDA GUID”, “PRIDE Project Accession”)
      "value": "<PID value>",      // never a generic placeholder; use a realistic‑looking example
      "url": "<Resolver URL>"      // e.g. https://doi.org/… or https://…/id/…
    }
    /* optionally add a second identifier of a different type if the scenario calls for it */
  ],
  "relatedIdentifier": [           // optional, may contain “IsPartOf”, “IsVersionOf”, etc.
    {
      "@type": "PropertyValue",
      "propertyID": "<PID type>",
      "value": "<value>",
      "url": "<URL>",
      "relationType": "<Relation>"
    }
  ],
  "creator": [                     // array of Person or Organization objects
    {
      "@type": "Person",
      "name": "<Full name>",
      "identifier": {
        "@type": "PropertyValue",
        "propertyID": "ORCID",
        "value": "<ORCID URL>"   // use a real‑looking ORCID (e.g. https://orcid.org/0000-0002-1825-0097) or a clear placeholder {ORCID}
      }
    }
  ],
  "publisher": {
    "@type": "Organization",
    "name": "<Repository or Publisher name>",
    "identifier": {
      "@type": "PropertyValue",
      "propertyID": "ROR",
      "value": "<ROR URL>"        // use a real ROR identifier or {ROR}
    }
  },
  "datePublished": "<YYYY-MM-DD>",
  "dateCreated": "<YYYY-MM-DD>",          // optional but recommended for provenance
  "dateModified": "<YYYY-MM-DD>",         // optional for version tracking
  "license": "<URL to license>",           // e.g. CC‑BY 4.0, CC0, etc.
  "keywords": [ "<term‑1>", "<term‑2>", … ],
  "subject": [                               // optional – controlled‑vocab URIs (e.g. EDAM, OBI)
    "https://edamontology.org/topic_0003",   // example
    …
  ],
  "distribution": [                           // one or more DataDownload objects
    {
      "@type": "DataDownload",
      "description": "<What the file/landing‑page contains>",
      "accessUrl": "<URL>",
      "encodingFormat": "<MIME type>"        // optional but useful
    }
    /* repeat for each granular file when required */
  ],
  "version": "<Version string>",
  "accessLevel": "open" | "restricted",
  "rights": "<Human‑readable rights statement with URL if applicable>",
  "citation": {                               // **structured** citation object (Blueprint 4.2)
    "@type": "PropertyValue",
    "propertyID": "DOI",
    "value": "<Citation DOI>",
    "text": "<Full citation text, may include future DOI placeholder>"
  },
  "decisionGuidance": "<One‑sentence recommendation that mirrors the Reasoning section, suitable for inclusion in a DMP or protocol>",
  "apiSpecification": {                       // optional but required when the scenario mentions programmatic access
    "openapi": "3.0.0",
    "info": {
      "title": "Metadata Retrieval API",
      "version": "1.0"
    },
    "paths": {
      "/metadata/{pid}": {
        "get": {
          "summary": "Retrieve JSON‑LD metadata for the object identified by {pid}",
          "parameters": [
            {
              "name": "pid",
              "in": "path",
              "required": true,
              "schema": { "type": "string" },
              "description": "Persistent identifier (e.g., DOI without the ‘doi:’ prefix)"
            }
          ],
          "responses": {
            "200": {
              "description": "JSON‑LD metadata record",
              "content": {
                "application/ld+json": {
                  "schema": { "$ref": "#" }
                }
              }
            },
            "404": { "description": "PID not found" }
          }
        }
      }
    }
  }
}
```

> **Important:**  
> * Never leave generic placeholders such as `0000-0000-0000-0000` or `https://ror.org/0placeholder`. Either insert a realistic‑looking identifier or explicitly mark it as `{ORCID}` / `{ROR}` with a note that the author must supply the real value.  
> * All URLs must resolve to a landing page or resolver (doi.org, ror.org, etc.).  
> * The `citation` field must be a **structured object**, not a plain string. Include both the DOI and a human‑readable citation string.  
> * When the scenario asks for a **choice** (e.g., DOI vs. GUID) you must provide a short comparison table in the Reasoning section before giving the final recommendation.  

---

### 2. Detailed Step‑by‑Step Process  

1. **Parse the scenario.** Identify:
   - The type of research object (article, dataset, collection, file, etc.).
   - The specific decision to be made (which PID to use, whether to cite a pre‑print, how to link granularity, etc.).
   - Any special constraints (restricted access, human‑subjects data, need for an API, etc.).

2. **Compose the Reasoning section.**
   - Begin with a one‑sentence answer to the decision prompt.  
   - Follow with 2‑4 bullet points explaining the FAIR rationale (persistence, resolvers, community recognition, cost, versioning, compliance with the Blueprint).  
   - If a comparison is required, present a concise table showing pros/cons of each option.  

3. **Build the JSON‑LD artifact.**
   - Choose the appropriate `@type` (`ScholarlyArticle`, `Dataset`, etc.).  
   - Fill every mandatory field listed in the Blueprint (identifier, name, description, creator, publisher, datePublished, license, keywords, distribution, version, accessLevel, rights, citation).  
   - Add **optional but recommended** fields: `dateCreated`, `dateModified`, `subject`, `decisionGuidance`, `apiSpecification`.  
   - Ensure every PID is expressed as a `PropertyValue` with `propertyID`, `value`, and `url`.  
   - For scenarios requiring multiple granular files, add a separate `DataDownload` entry for each file, and if possible assign a file‑level PID (e.g., a DOI) inside that entry.  

4. **Validate the record.**
   - All URLs should be syntactically correct and point to the correct resolver domain.  
   - No field should contain the literal string “placeholder” unless it is wrapped in `{}` as a clear marker for user replacement.  
   - The JSON must be well‑formed (commas, brackets, quotes).  

5. **Return the final answer.**  
   - First, a **Reasoning** heading with the recommendation and justification.  
   - Second, an **Artifact** heading containing the JSON‑LD block (and any auxiliary blocks such as the API spec).  
   - Do **not** include any extra explanatory text outside these two sections.

---

### 3. Evaluation Criteria (what the grader will look for)

| Criterion | What to achieve |
|-----------|-----------------|
| **Decision guidance** | Clear answer to the scenario’s question; brief FAIR justification; optional comparison table. |
| **Metadata completeness** | All mandatory schema.org fields present and correctly typed. |
| **Realistic identifiers** | No generic placeholders; use a realistic‑looking DOI/ORCID/ROR or explicit `{ORCID}` / `{ROR}` markers. |
| **Structured citation** | `citation` as a PropertyValue object containing DOI and human‑readable text. |
| **Granularity / file‑level linking** | When required, separate `DataDownload` entries for each file, possibly with their own PID. |
| **API specification** | Minimal OpenAPI snippet (or equivalent description) when programmatic access is part of the scenario. |
| **FAIR compliance notes** | Mention of findability, accessibility, licensing, rights, and any training/outreach needed. |
| **JSON validity** | Proper syntax; no trailing commas; correct nesting. |
| **Professional tone** | Concise, jargon‑free language; no filler sentences. |

---

### 4. Example (illustrative only – do not output this in the final answer)

**Reasoning**  
- Cite the bioRxiv pre‑print DOI now; update the record later with the journal DOI using `isVersionOf`.  
- This satisfies funder DMP requirements, provides immediate persistence, and preserves version history.

**Artifact**  
```json
{
  "@context": "https://schema.org/",
  "@type": "ScholarlyArticle",
  "name": "Zika Virus Neurotropism in Human Neural Organoids (Preprint)",
  "description": "...",
  "identifier": [
    {
      "@type": "PropertyValue",
      "propertyID": "DOI",
      "value": "10.1101/2024.05.15.594321",
      "url": "https://doi.org/10.1101/2024.05.15.594321"
    }
  ],
  "relatedIdentifier": [
    {
      "@type": "PropertyValue",
      "propertyID": "Grant",
      "value": "NIH-R01-AI123456",
      "url": "https://reporter.nih.gov/project-details/123456",
      "relationType": "IsFundedBy"
    }
  ],
  "creator": [ … ],
  "publisher": { … },
  "datePublished": "2024-05-15",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "keywords": ["Zika virus","neurotropism","organoids","preprint"],
  "distribution": [ … ],
  "version": "1",
  "accessLevel": "open",
  "rights": "Preprint, not peer‑reviewed. CC‑BY 4.0.",
  "citation": {
    "@type": "PropertyValue",
    "propertyID": "DOI",
    "value": "10.1101/2024.05.15.594321",
    "text": "Last F, et al. (2024). Zika Virus Neurotropism in Human Neural Organoids. bioRxiv. DOI: 10.1101/2024.05.15.594321."
  },
  "decisionGuidance": "Cite the bioRxiv DOI now; add an `isVersionOf` link to the future journal DOI when available.",
  "apiSpecification": { … }
}
