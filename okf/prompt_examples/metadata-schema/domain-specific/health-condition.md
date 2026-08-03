---
type: PromptExample
title: Map health conditions to MONDO terms
description: Filled example mapping health conditions drawn from ImmPort Long COVID, ImmPort RA, TB Portals, MWCCS/HIV, ClinEpiDB-style epidemiology, and ITN immune-tolerance contexts.
source_template: src/promptLibrary/okf-bundle/metadata-schema/domain-specific/health-condition.md
domain_sources:
  - https://www.immport.org/
  - https://tbportals.niaid.nih.gov/
  - https://statepi.jhsph.edu/mwccs/
  - https://clinepidb.org/
  - https://www.itntrialshare.org/
placeholders:
  conditions: multi-domain NIAID portfolio conditions (COVID-19/PASC, RA, TB, HIV, malaria, type 1 diabetes / immune tolerance)
tags: [metadata-schema, domain-specific, healthcondition, mondo, immport, tb-portals, mwccs, clinepidb, itn]
---

# Prompt

Map the following health conditions or diseases to MONDO ontology terms for use in NIAID Blueprint metadata.

Health conditions mentioned:
- COVID-19 and post-acute sequelae of COVID-19 / Long COVID (as studied in ImmPort SDY2968 qualitative vaccination-perspectives work; also relevant to AccessClinicalData@NIAID ACTT-series COVID treatment trials)
- Rheumatoid arthritis (ImmPort SDY998 AMP Rheumatoid Arthritis Phase 1)
- Tuberculosis / pulmonary TB (NIAID TB Portals multi-domain case collection)
- HIV infection and HIV-associated comorbidities (MACS/WIHS Combined Cohort Study — MWCCS; https://statepi.jhsph.edu/mwccs/)
- Malaria and other infectious-disease epidemiology endpoints typical of ClinEpiDB-hosted observational studies (https://clinepidb.org/)
- Type 1 diabetes mellitus and immune-tolerance clinical contexts associated with ITN TrialShare-style interventional immunology trials (https://www.itntrialshare.org/)

For each condition return the preferred MONDO label and identifier. Format the output for the `healthCondition` metadata field.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
