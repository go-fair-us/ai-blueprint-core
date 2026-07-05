---
type: Worked Example
title: Worked Example — Portal Metadata Entries
description: Supplementary Tables 3 and 4 completed metadata for ACDN and ImmPort datasets
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [acdn, immport, supplementary-table-3, supplementary-table-4]
source_document: NIAID_Blueprint_v2_26Sep2025_forExternal.md
source_lines: 304-366
section: Examples of Metadata Elements and Entries for NIAID-funded Datasets Indexed in the NIAID Data Ecosystem Discovery Portal
normative: false
concept_range: 203-213
---

Supplementary Tables 3 and 4 demonstrate completed Blueprint metadata for controlled access ACDN and open access ImmPort datasets indexed in the Discovery Portal, with ODSET-supplemented example entries where submitter metadata was incomplete.

See also: [Requirements](/metadata-schema/requirements.md).

# Atomic concepts

| # | Concept | Lines |
|---|---------|-------|
| 203 | Supplementary Tables 3 and 4 provide examples of controlled and registered datasets indexed in the NIAID Data Ecosystem Discovery Portal, with metadata fields populated from the portal. | 306-308 |
| 204 | Where metadata elements were missing, ODSET has provided example entries that would fulfill the metadata requirements of the Blueprint. | 306 |
| 205 | Supplementary Table 3 documents a controlled access dataset from AccessClinicalData@NIAID indexed in the NIAID Ecosystem Portal. | 308 |
| 206 | The ACDN example includes type=dataset, a resolvable DOI identifier, and name '(Released May 2022) Adaptive COVID-19 Treatment Trial 4 (ACTT-4).' | 312-314 |
| 207 | The ACDN example populates author (ORCID), funder (ROR for NIAID), grant numbers, measurementTechnique (NCIT), infectiousAgent (SARS-CoV-2 NCBITaxon), host (Homo sapiens), healthCondition (MONDO COVID-19), controlled conditionsOfAccess, and temporal coverage 2020-11-24/2021-06-30. | 317-332 |
| 208 | The original ACDN submission included a description of the overarching study instead of the dataset; example text was provided to describe the dataset. | 336 |
| 209 | The ACDN dataset is from an international, multi-site study; specific countries were not provided, so spatialCoverage uses ZZ (unknown). | 338 |
| 210 | Supplementary Table 4 documents an open access dataset from ImmPort (SDY998: AMP Rheumatoid Arthritis Phase 1) indexed in the NIAID Ecosystem Portal. | 340-346 |
| 211 | The ImmPort example uses resolvable DOI https://doi.org/10.21430/M3KXJHSP4T and describes a rheumatoid arthritis study. | 345-346 |
| 212 | The ImmPort example includes multiple author ORCIDs, funders (NIAID and NIAMS ROR), grant 1UH2AR067676-01, and measurementTechnique values for flow cytometry (C16585) and RNA sequence (C89252). | 349-352 |
| 213 | The ImmPort example temporal coverage spans 2016-03-15/2024-07-25. | 366 |

# Citations

[1] [Examples of Metadata Elements and Entries for NIAID-funded Datasets Indexed in the NIAID Data Ecosystem Discovery Portal](https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md) (lines 304–366)
