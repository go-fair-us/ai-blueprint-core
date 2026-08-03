---
type: PromptExample
title: Generate funder and grant metadata
description: Filled example for funder/grant metadata using ImmPort AMP RA (SDY998) and ACDN ACTT-4 / NIAID funding patterns from Blueprint worked examples.
source_template: src/promptLibrary/okf-bundle/metadata-schema/attribution-provenance/funder-grant.md
domain_sources:
  - https://www.immport.org/
  - https://accessclinicaldata.niaid.nih.gov/
placeholders:
  project_title: "SDY998: AMP Rheumatoid Arthritis Phase 1 (ImmPort open-access dataset)"
  funders: "NIAID (ROR https://ror.org/043z4tv69); NIAMS (ROR https://ror.org/006zn3t30); Accelerating Medicines Partnership RA/SLE"
  grant_numbers: "1UH2AR067676-01 (NIAID secondary per Blueprint Supplementary Table 4)"
tags: [metadata-schema, attribution, funder, grant, ror, immport, acdn]
---

# Prompt

Help a researcher create compliant `funder` and `grant` metadata for the NIAID Blueprint.

Project title: SDY998: AMP Rheumatoid Arthritis Phase 1 — open-access ImmPort study dataset (https://www.immport.org/shared/study/SDY998; DOI https://doi.org/10.21430/M3KXJHSP4T), generated under the Accelerating Medicines Partnership RA/SLE program and indexed as a worked example in the NIAID Blueprint Supplementary Table 4
Funding organizations: National Institute of Allergy and Infectious Diseases (NIAID), NIH — ROR https://ror.org/043z4tv69; National Institute of Arthritis and Musculoskeletal and Skin Diseases (NIAMS), NIH — ROR https://ror.org/006zn3t30; program vehicle: Accelerating Medicines Partnership RA/SLE (AMP RA/SLE)
Grant or contract numbers: 1UH2AR067676-01 (NIAID is secondary funder per Blueprint Supplementary Table 4)

Generate the metadata as JSON with `funder` (using ROR where possible) and `grant` fields.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
