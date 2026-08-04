I was able to retrieve and ground this in the official NIAID Blueprint (v2, 26 Sep 2025), specifically **Section 4 (Minimal Citation Requirements)**, **Table 3** (citation style examples), and **Supplementary Table 4 / Supplemental Table 7** (which use this exact SDY998 study as the worked example).

## Human-readable citation

Per Blueprint Table 3's APA-style dataset pattern (`Author(s). (Year). Title of dataset (Version) [Data set]. Repository. DOI`), combined with ImmPort's own citation policy (cite the ImmPort Shared Data website, Study Accession, and Study Title, using the DOI when available):

> **Investigators registered to ImmPort Study SDY998** [ORCID: 0000-0002-1450-1549; 0000-0002-1219-3845; 0000-0003-4483-0359; 0000-0002-5634-7746]. (2017). *SDY998: AMP Rheumatoid Arthritis Phase 1* [Data set]. ImmPort Shared Data. Study Accession: SDY998. https://doi.org/10.21430/M3KXJHSP4T

Notes on construction:
- **Year (2017)** comes from the `dateCreated` element in Supplementary Table 4 (2017‑11‑07), the Blueprint's default date field for datasets.
- **Author identifiers** are given only as ORCIDs in the source metadata (no names were supplied), so they're cited as resolvable ORCID PIDs rather than invented names — consistent with the Blueprint's emphasis on PIDs over free-text names when names aren't authoritatively available. If you have access to ImmPort's contributor records, resolving these ORCIDs to display names (via the ORCID API) is the correct next step and can replace the bracketed ORCID list with `Lastname, F. et al.`
- **DOI** is placed last per Table 3's format, since it is the "identifier" element and Blueprint Section 2 stresses always using the *resolvable* form (`https://doi.org/...`, not the bare `10.21430/...` string).
- **Study Accession (SDY998)** is included explicitly because the Blueprint requires reused-data citations to include the repository-specific ID *alongside* the object PID.

Funder/grant information (NIAID, ROR: https://ror.org/043z4tv69; NIAMS, ROR: https://ror.org/006zn3t30; grant 1UH2AR067676-01) is metadata for discovery/attribution tracking, not part of the citation string itself — Blueprint Table 1 treats `funder`/`grant` as separate elements from `citation`. If your target venue wants an acknowledgment line, that would read something like: *"Data were generated with support from NIAID and NIAMS (grant 1UH2AR067676‑01) as part of the Accelerating Medicines Partnership RA/SLE program."*

If your publication is also drawing on the associated methods paper, the Blueprint's `citation` metadata element (Supplemental Table 7) links it separately:
> Methods for high-dimensional analysis of cell populations in rheumatoid arthritis (2018). https://doi.org/10.1186/s13075-018-1631-y (PMID: 29996944)

## Machine-actionable format (JSON-LD, schema.org)

This follows the exact structure the Blueprint uses in **Supplemental Table 7** for this same study:

```json-ld
{
  "@context": "https://schema.org/",
  "@id": "https://doi.org/10.21430/M3KXJHSP4T",
  "@type": "Dataset",
  "identifier": {
    "@id": "https://doi.org/10.21430/M3KXJHSP4T",
    "@type": "PropertyValue",
    "propertyID": "https://registry.identifiers.org/registry/doi",
    "value": "doi:10.21430/M3KXJHSP4T",
    "url": "https://doi.org/10.21430/M3KXJHSP4T"
  },
  "name": "SDY998: AMP Rheumatoid Arthritis Phase 1",
  "url": "https://www.immport.org/shared/study/SDY998",
  "dateCreated": "2017-11-07",
  "author": [
    { "@type": "Person", "identifier": "https://orcid.org/0000-0002-1450-1549" },
    { "@type": "Person", "identifier": "https://orcid.org/0000-0002-1219-3845" },
    { "@type": "Person", "identifier": "https://orcid.org/0000-0003-4483-0359" },
    { "@type": "Person", "identifier": "https://orcid.org/0000-0002-5634-7746" }
  ],
  "funder": [
    { "@type": "Organization", "identifier": "https://ror.org/043z4tv69", "name": "NIAID" },
    { "@type": "Organization", "identifier": "https://ror.org/006zn3t30", "name": "NIAMS" }
  ],
  "grant": "1UH2AR067676-01",
  "citation": [
    {
      "@type": "ScholarlyArticle",
      "name": "Methods for high-dimensional analysis of cell populations in rheumatoid arthritis",
      "url": "https://pubmed.ncbi.nlm.nih.gov/29996944",
      "identifier": {
        "@id": "https://doi.org/10.1186/s13075-018-1631-y",
        "@type": "PropertyValue",
        "propertyID": "https://registry.identifiers.org/registry/doi",
        "value": "doi:10.1186/s13075-018-1631-y",
        "url": "https://doi.org/10.1186/s13075-018-1631-y"
      }
    }
  ],
  "conditionsOfAccess": "https://www.immport.org/agreement",
  "license": "https://www.immport.org/agreement"
}
```

## Why this format is preferred (per the Blueprint)

1. **Resolvable DOI as the primary identifier.** Section 2 explicitly requires the *resolvable* form (`https://doi.org/10.21430/M3KXJHSP4T`) rather than the bare DOI string, because unresolved DOIs "lack the same level of persistence" needed for citation stability and reproducibility.
2. **Both accession and DOI included.** Section 4.2 distinguishes "original" vs. "reused" data citation, and for reused data specifically requires "the object PID (e.g., DOI) and, if applicable, a repository‑specific ID (e.g., accession numbers)" — which is why SDY998 appears alongside the DOI even though the DOI alone is technically sufficient to resolve the object.
3. **ORCID PIDs for authorship rather than plain-text names.** Table 2 designates ORCID as the default PID for the `author` element specifically because it supports long-term traceability and usage tracking that free-text names cannot — this matters more, not less, when display names aren't yet available in the source metadata.
4. **Alignment with the repository's own stated policy.** Section 4.2 tells repository owners to "provide clear, consistent instructions for citing... data," and ImmPort's own citation guidance (repository + accession + title + DOI) is exactly what's reflected here — the Blueprint's role is to standardize *how* that repository-level guidance gets rendered (PID-first, machine-actionable-ready), not override it.
5. **JSON-LD machine-actionable version** mirrors Supplemental Table 7's worked example for this exact study, satisfying Section 3's requirement that metadata (including citation-relevant fields like `identifier`, `author`, `funder`, and `citation`) be exposable as schema.org-typed JSON-LD so catalogs and the NIAID Data Ecosystem Discovery Portal can harvest it programmatically.

**Contrast note (not merged):** the ACTT-4 package under AccessClinicalData@NIAID would follow the *same* Table 3 pattern (DOI-first, PID-based authorship) but its `conditionsOfAccess` and `license` fields would point to a Data Access Request/DUA document rather than an open user agreement — per Supplementary Table 3, that repository cites a `Controlled-Data` SPDX-style designation instead of ImmPort's open agreement URL, and any citation should flag the controlled-access status so downstream users know a DAR is required before the object (not just its metadata) can be obtained.