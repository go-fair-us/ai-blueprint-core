---
type: PromptExample
title: Format author metadata with ORCID and ROR
description: Filled example for author metadata, using ImmPort SDY998 (AMP Rheumatoid Arthritis Phase 1) principal-investigator ORCIDs from Blueprint Supplementary Table 4.
source_template: src/promptLibrary/okf-bundle/metadata-schema/attribution-provenance/author.md
domain_sources:
  - https://www.immport.org/
  - https://www.immport.org/shared/study/SDY998
placeholders:
  creators_list: AMP RA Phase 1 PI ORCIDs and institutional affiliations (ImmPort SDY998 / Blueprint Table 4)
tags: [metadata-schema, attribution, author, orcid, ror, immport, sdy998]
---

# Prompt

You are an expert in the NIAID Blueprint metadata schema.

Given the list of people and organizations involved in creating this digital object, generate the `author` metadata array following NIAID recommendations.

For each person include their name, ORCID (if known), and affiliation with ROR when possible.

Input:
Digital object: ImmPort study SDY998 — AMP Rheumatoid Arthritis Phase 1
Landing page: https://www.immport.org/shared/study/SDY998
DOI: https://doi.org/10.21430/M3KXJHSP4T

Principal investigators / creators (ORCIDs as listed in NIAID Blueprint Supplementary Table 4 for this open-access ImmPort dataset):
- ORCID 0000-0002-1450-1549 (principal investigator; affiliation: Accelerating Medicines Partnership RA/SLE research team; use institutional ROR when resolvable)
- ORCID 0000-0002-1219-3845 (principal investigator)
- ORCID 0000-0003-4483-0359 (principal investigator)
- ORCID 0000-0002-5634-7746 (principal investigator)

Organizational contributors / hosting:
- ImmPort Shared Data repository (NIAID/DAIT-supported immunology data archive) — https://www.immport.org/
- National Institute of Allergy and Infectious Diseases (NIAID) — ROR https://ror.org/043z4tv69
- National Institute of Arthritis and Musculoskeletal and Skin Diseases (NIAMS) — ROR https://ror.org/006zn3t30

Notes for formatting:
- Prefer schema.org Person / Organization structures consistent with Blueprint author guidance.
- Include ORCID as a resolvable identifier (https://orcid.org/<id>).
- Include ROR for organizational affiliations where known.
- Where a person's display name is not provided in the source table, leave name as a structured placeholder keyed by ORCID rather than inventing a full legal name.

Output the result as valid JSON matching the NIAID Blueprint author structure.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
