```json
{
  "input": "NIH NIAID Immport data repository",
  "interpreted_as": "ImmPort (Immunology Database and Analysis Portal), the NIAID/DAIT-funded research data repository. The ROR entity is the National Institute of Allergy and Infectious Diseases (NIAID), not ImmPort itself.",
  "ror_id": "https://ror.org/043z4tv69",
  "ror_name": "National Institute of Allergy and Infectious Diseases",
  "status": "active",
  "successor_ror_id": null,
  "location": {
    "city": "Bethesda",
    "country": "United States"
  },
  "parent_ror_ids": [
    "https://ror.org/01cwqze88"
  ],
  "external_ids": {
    "wikidata": "Q3519875",
    "isni": "0000000121649667",
    "crossref_funder_id": "100000060",
    "grid": "grid.419681.3",
    "viaf": "136483746",
    "loc": "n79084679",
    "openalex": null
  },
  "verification": {
    "ror_to_wikidata": false,
    "wikidata_to_ror": true,
    "other_sources_agreeing": [
      "re3data",
      "SciCrunch",
      "Crossref Funder Registry",
      "Library authority files",
      "OpenAlex"
    ],
    "sources_not_reachable": [
      "ROR API v2 query endpoint",
      "ROR API v2 affiliation endpoint",
      "ROR API v2 record endpoint",
      "OpenAlex Institutions API",
      "Crossref Funder Registry API"
    ]
  },
  "conflicts": [
    "The ROR API v2 endpoints were not reachable in this session, so the required direct ROR API query, affiliation result (including the 'chosen' flag), and record-level ROR-to-Wikidata verification could not be independently inspected.",
    "OpenAlex work records identify National Institute of Allergy and Infectious Diseases as an ROR-linked organization, but the OpenAlex Institutions API was not reachable, so no OpenAlex institution ID is reported.",
    "ImmPort itself is a repository/resource rather than the ROR organization being identified. Its re3data record lists NIAID/DAIT as the general/funding institution, alongside HHS and UCSF; therefore those latter organizations were not selected as the primary match."
  ],
  "alternative_candidates": [
    {
      "ror_id": "https://ror.org/01cwqze88",
      "name": "National Institutes of Health",
      "why_not_chosen": "Parent organization of NIAID; ImmPort is specifically described as developed/funded for NIAID's Division of Allergy, Immunology, and Transplantation (DAIT), so the institute-level entity is the closer match."
    },
    {
      "ror_id": "https://ror.org/033jnv181",
      "name": "United States Department of Health and Human Services",
      "why_not_chosen": "HHS is listed as a funding institution for ImmPort, but it is the broader parent federal department rather than the NIAID entity named in the input."
    },
    {
      "ror_id": "https://ror.org/043mz5j54",
      "name": "University of California, San Francisco",
      "why_not_chosen": "UCSF is listed by re3data as the technical institution for ImmPort, and ImmPort describes a UCSF partnership, but it is not the NIAID organization named in the input."
    }
  ],
  "confidence": "medium"
}

```

```
{
  "input": "NIH NIAID Immport data repository",
  "interpreted_as": "ImmPort (Immunology Database and Analysis Portal), the NIAID/DAIT-funded research data repository. The ROR entity is the National Institute of Allergy and Infectious Diseases (NIAID), not ImmPort itself.",
  "ror_id": "https://ror.org/043z4tv69",
  "ror_name": "National Institute of Allergy and Infectious Diseases",
  "status": "active",
  "successor_ror_id": null,
  "location": {
    "city": "Bethesda",
    "country": "United States"
  },
  "parent_ror_ids": [
    "https://ror.org/01cwqze88"
  ],
  "external_ids": {
    "wikidata": "Q3519875",
    "isni": "0000000121649667",
    "crossref_funder_id": "100000060",
    "grid": "grid.419681.3",
    "viaf": "136483746",
    "loc": "n79084679",
    "openalex": null
  },
  "verification": {
    "ror_to_wikidata": false,
    "wikidata_to_ror": true,
    "other_sources_agreeing": [
      "re3data",
      "SciCrunch",
      "Crossref Funder Registry",
      "Library authority files",
      "OpenAlex"
    ],
    "sources_not_reachable": [
      "ROR API v2 query endpoint",
      "ROR API v2 affiliation endpoint",
      "ROR API v2 record endpoint",
      "OpenAlex Institutions API",
      "Crossref Funder Registry API"
    ]
  },
  "conflicts": [
    "The ROR API v2 endpoints were not reachable in this session, so the required direct ROR API query, affiliation result (including the 'chosen' flag), and record-level ROR-to-Wikidata verification could not be independently inspected.",
    "OpenAlex work records identify National Institute of Allergy and Infectious Diseases as an ROR-linked organization, but the OpenAlex Institutions API was not reachable, so no OpenAlex institution ID is reported.",
    "ImmPort itself is a repository/resource rather than the ROR organization being identified. Its re3data record lists NIAID/DAIT as the general/funding institution, alongside HHS and UCSF; therefore those latter organizations were not selected as the primary match."
  ],
  "alternative_candidates": [
    {
      "ror_id": "https://ror.org/01cwqze88",
      "name": "National Institutes of Health",
      "why_not_chosen": "Parent organization of NIAID; ImmPort is specifically described as developed/funded for NIAID's Division of Allergy, Immunology, and Transplantation (DAIT), so the institute-level entity is the closer match."
    },
    {
      "ror_id": "https://ror.org/033jnv181",
      "name": "United States Department of Health and Human Services",
      "why_not_chosen": "HHS is listed as a funding institution for ImmPort, but it is the broader parent federal department rather than the NIAID entity named in the input."
    },
    {
      "ror_id": "https://ror.org/043mz5j54",
      "name": "University of California, San Francisco",
      "why_not_chosen": "UCSF is listed by re3data as the technical institution for ImmPort, and ImmPort describes a UCSF partnership, but it is not the NIAID organization named in the input."
    }
  ],
  "confidence": "medium"
}
```

 The correct organizational match is **National Institute of Allergy and Infectious Diseases (NIAID), ROR `https://ror.org/043z4tv69`**, rather than ImmPort as a standalone ROR entity. ImmPort's own documentation identifies it as the Immunology Database and Analysis Portal developed for NIH/NIAID's DAIT, while re3data identifies NIAID/DAIT as its general/funding institution.  ImmPort+2  Wikidata independently maps NIAID (Q3519875) to ROR `043z4tv69` and supplies ISNI `0000000121649667`, GRID `grid.419681.3`, Crossref Funder ID `100000060`, VIAF `136483746`, and Library of Congress ID `n79084679`; the parent is NIH.  Wikidata+1  Crossref's funder identifier is independently confirmed as `100000060`, and current scholarly records continue to cite NIAID with ROR `043z4tv69`.  MIT Press Direct+1  Because the required ROR v2 API endpoints themselves were inaccessible in this session, I would classify this **medium confidence and flag it for human review**, rather than claiming the requested high-confidence bidirectional ROR↔Wikidata verification.
