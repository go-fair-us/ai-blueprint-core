---
type: PromptExample
title: Generate citation text and guidance for a digital object
description: Filled example producing citation text for ImmPort SDY998 (AMP RA) and noting ImmPort portal citation policy; secondary nod to ACDN ACTT-4 controlled-access packaging.
source_template: src/promptLibrary/okf-bundle/citation-outreach/citation-guidance.md
domain_sources:
  - https://www.immport.org/
  - https://docs.immport.org/home/cite/
  - https://accessclinicaldata.niaid.nih.gov/
placeholders:
  object_details: ImmPort SDY998 AMP Rheumatoid Arthritis Phase 1 with DOI, authors, funders, and ImmPort citation policy
tags: [citation, outreach, doi, immport, sdy998, acdn]
---

# Prompt

Generate a recommended citation for the following digital object following NIAID Blueprint citation guidance. Also provide a short explanation of why this citation format is preferred.

Digital object details:
- Title: SDY998: AMP Rheumatoid Arthritis Phase 1
- Repository: ImmPort Shared Data (https://www.immport.org/)
- Study landing page: https://www.immport.org/shared/study/SDY998
- Persistent identifier (DOI): https://doi.org/10.21430/M3KXJHSP4T
- Accession: SDY998
- Description (short): Open-access ImmPort study from the Accelerating Medicines Partnership RA/SLE program, including multi-modal immune profiling (flow cytometry, CyTOF, RNA sequencing, microscopy) of rheumatoid arthritis and related arthroplasty samples; used as Blueprint Supplementary Table 4 / Supplemental Table 7 worked example.
- Creators (ORCIDs from Blueprint Supplementary Table 4): 0000-0002-1450-1549; 0000-0002-1219-3845; 0000-0003-4483-0359; 0000-0002-5634-7746
- Funders: NIAID (https://ror.org/043z4tv69); NIAMS (https://ror.org/006zn3t30); grant 1UH2AR067676-01
- Related publication example: "Methods for high-dimensional analysis of …" — PubMed https://pubmed.ncbi.nlm.nih.gov/29996944 ; DOI https://doi.org/10.1186/s13075-018-1631-y
- License / use: ImmPort user agreement (https://www.immport.org/agreement) — redistribution allowed under commensurate terms; no re-identification
- ImmPort citation policy note (https://docs.immport.org/home/cite/): when using specific ImmPort datasets in publications, cite the ImmPort Shared Data website, Study Accession, and Study Title (and use the study DOI when available)
- Optional secondary object for contrast (do not merge into one citation): AccessClinicalData@NIAID controlled-access package "(Released May 2022) Adaptive COVID-19 Treatment Trial 4 (ACTT-4)" — controlled conditionsOfAccess clinical trial data at https://accessclinicaldata.niaid.nih.gov/

Include both a human-readable citation and, if appropriate, a machine-actionable format.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
