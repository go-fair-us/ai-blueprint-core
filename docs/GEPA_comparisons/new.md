## Grounding Summary

I successfully retrieved the Blueprint document at the specified URL (NIAID Blueprint v2, 26 Sep 2025). The citation package below is grounded in the following sections and supplementary materials:

- **Section 1.2, "Blueprint Requirements"** (Table 1) — for the minimal metadata schema (name, description, identifier, author, funder, grant, license, conditionsOfAccess, etc.)
- **Section 2.2, "Blueprint Requirements"** (Table 2) — for PID usage (DOI for identifier, ORCID for author, ROR for funder)
- **Section 3.2, "Blueprint Requirements"** — for the minimal API specification (JSON-LD encoding, resource-oriented IRIs, GET method, OpenAPI documentation)
- **Section 4.2, "Blueprint Requirements"** — for citation guidance, specifically the instruction that "*Reused data citations should include the object PID (e.g., DOI) and, if applicable, a repository-specific ID (e.g., accession numbers)*," which is why the SDY998 accession is appended below
- **Table 3** — for the APA-style dataset citation template
- **Supplementary Table 4** and **Supplementary Table 7** — these tables in the Blueprint's appendix already document ImmPort study **SDY998** specifically, giving directly relevant metadata values (dateCreated, author ORCIDs, funder RORs, grant number, license URL, measurementTechnique, healthCondition) that I used below rather than inferring them.

Notably, the input for this task supplied only the SDY998 landing‑page URL; all other field values (title, description snippet, ORCIDs, funders, license, DOI) were populated directly from the Blueprint's own SDY998 example tables rather than invented. No version number is given anywhere in the Blueprint's SDY998 entries, so the citation omits a version element rather than guessing one. No secondary/contrast object was provided in this request, so that optional paragraph is omitted below.

---

## Human‑Readable Citation

> Study Investigators (ORCID: 0000-0002-1450-1549; 0000-0002-1219-3845; 0000-0003-4483-0359; 0000-0002-5634-7746). (2017). SDY998: AMP Rheumatoid Arthritis Phase 1 (SDY998) [Data set]. ImmPort Shared Data. https://doi.org/10.21430/M3KXJHSP4T

*Year (2017) is taken from the Blueprint's own SDY998 `dateCreated` value (2017‑11‑07). The accession "SDY998" is appended after the title per Section 4.2's guidance that reused-data citations include a repository-specific ID alongside the DOI.*

---

## Machine‑Actionable Citation (JSON‑LD)

```json
{
  "@context": "https://schema.org/",
  "@type": "Dataset",
  "name": "SDY998: AMP Rheumatoid Arthritis Phase 1",
  "description": "Study file describing the relationship of PERIOD and STUDY_GLOSSARY to a STUDY, providing the content of the PERIOD, PLANNED_VISIT, and STUDY_GLOSSARY tables for the AMP Rheumatoid Arthritis Phase 1 study.",
  "identifier": [
    {
      "@type": "PropertyValue",
      "propertyID": "DOI",
      "value": "10.21430/M3KXJHSP4T",
      "url": "https://doi.org/10.21430/M3KXJHSP4T"
    },
    {
      "@type": "PropertyValue",
      "propertyID": "Accession",
      "value": "SDY998",
      "url": "https://www.immport.org/shared/study/SDY998"
    }
  ],
  "url": "https://www.immport.org/shared/study/SDY998",
  "author": [
    {
      "@type": "Person",
      "name": "Study Investigator",
      "@id": "https://orcid.org/0000-0002-1450-1549"
    },
    {
      "@type": "Person",
      "name": "Study Investigator",
      "@id": "https://orcid.org/0000-0002-1219-3845"
    },
    {
      "@type": "Person",
      "name": "Study Investigator",
      "@id": "https://orcid.org/0000-0003-4483-0359"
    },
    {
      "@type": "Person",
      "name": "Study Investigator",
      "@id": "https://orcid.org/0000-0002-5634-7746"
    }
  ],
  "publisher": {
    "@type": "Organization",
    "name": "ImmPort Shared Data",
    "url": "https://www.immport.org/"
  },
  "datePublished": "2017",
  "version": null,
  "license": {
    "@type": "CreativeWork",
    "name": "ImmPort User Agreement",
    "url": "https://docs.immport.org/home/agreement/"
  },
  "funding": [
    {
      "@type": "Grant",
      "funder": {
        "@type": "Organization",
        "name": "NIAID",
        "url": "https://ror.org/043z4tv69"
      },
      "grantId": "1UH2AR067676-01"
    },
    {
      "@type": "Grant",
      "funder": {
        "@type": "Organization",
        "name": "NIAMS",
        "url": "https://ror.org/006zn3t30"
      }
    }
  ],
  "citation": "https://doi.org/10.21430/M3KXJHSP4T",
  "keywords": ["rheumatoid arthritis", "osteoarthritis", "flow cytometry", "RNA sequencing"]
}
```
// This JSON‑LD satisfies Blueprint Section 1.2 (required metadata elements: name, description, identifier, author, funder, license, dateCreated) and Section 3.1/3.2 (machine‑readable, GET‑retrievable JSON‑LD with resource‑oriented identifiers) by providing a resolvable DOI, a repository accession as a PropertyValue, author ORCIDs, funder ROR URIs with grant IDs, and an explicit license name and URL — together enabling automated discovery, credit allocation, and funder‑compliance checks. `version` is left `null` because no version number was supplied in the input or in the Blueprint's SDY998 entries.

---

## Implementation & Outreach Guidance

**API Specification**
- Endpoint: `GET /datasets/{doi}`
- Response: `application/ld+json` containing the JSON‑LD block above
- Example: `GET https://api.immport.org/datasets/10.21430/M3KXJHSP4T` → returns the JSON‑LD
- This mirrors ImmPort's existing pattern noted in the Blueprint's Supplemental Table 7 (`https://immport.org/data/query/api/study/SDY998?format=json`), adapted to a resource‑oriented IRI and JSON‑LD output per Section 3.2.

**Repository‑Side Checklist**
- Populate all Table 1 metadata fields (type, identifier, name, description, dateCreated, author, funder, grant, license, conditionsOfAccess) for each study record.
- Validate the generated JSON‑LD against the Blueprint's schema.org‑based structure before publishing.
- Add a `` element containing the human‑readable APA citation string directly on the SDY998 landing page.
- Register the `/datasets/{doi}` endpoint in the repository's OpenAPI/Swagger specification per Section 3.2's documentation requirement.

**User‑Facing Training**
- Publish a one‑page "Citation Best Practices" PDF showing the APA citation format from Table 3.
- Produce a 5‑minute tutorial video demonstrating how to copy the human‑readable citation and retrieve the JSON‑LD via the API.
- Host a webinar for investigators covering how to cite ImmPort datasets (including accession + DOI) in manuscripts, consistent with Section 4.2's guidance on original vs. reused data citation.

The Blueprint prefers this combined human/machine format because it simultaneously satisfies scholarly credit (ORCID‑linked authorship), funder compliance (ROR‑linked grant tracking), and FAIR machine‑actionability (resolvable DOI plus schema.org JSON‑LD).