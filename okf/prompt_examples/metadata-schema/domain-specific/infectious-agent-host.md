---
type: PromptExample
title: Add infectiousAgent and host metadata using NCBITaxon
description: Filled example for infectiousAgent/host annotation spanning ACDN ACTT-4 (SARS-CoV-2), TB Portals (M. tuberculosis), CEIRR (influenza), and BV-BRC pathogen scope.
source_template: src/promptLibrary/okf-bundle/metadata-schema/domain-specific/infectious-agent-host.md
domain_sources:
  - https://accessclinicaldata.niaid.nih.gov/
  - https://tbportals.niaid.nih.gov/
  - https://www.ceirr-network.org/
  - https://www.bv-brc.org/
placeholders:
  study_description: composite description covering ACTT-4 COVID treatment data, TB Portals multi-domain TB cases, and CEIRR influenza surveillance research
tags: [metadata-schema, domain-specific, infectiousagent, host, ncbitaxon, acdn, tb-portals, ceirr, bv-brc]
---

# Prompt

You are helping annotate a dataset according to the NIAID Blueprint.

Study description:
This composite NIAID-supported research portfolio spans three complementary digital-object contexts that all need Blueprint-style infectiousAgent and host annotation:

1) AccessClinicalData@NIAID controlled-access clinical trial package for Adaptive COVID-19 Treatment Trial 4 (ACTT-4) (https://accessclinicaldata.niaid.nih.gov/): patient-level trial data from an international multi-site study of baricitinib + remdesivir versus dexamethasone + remdesivir in hospitalized COVID-19, with human participants infected with SARS-CoV-2. Blueprint Supplementary Table 3 already flags infectiousAgent = SARS-CoV-2 (NCBITaxon) and host = Homo sapiens, healthCondition = COVID-19 (MONDO).

2) NIAID TB Portals multi-domain natural-history style case collection (https://tbportals.niaid.nih.gov/): clinical case records, chest X-ray/CT imaging, and Mycobacterium tuberculosis genomic sequences from patient cases across multiple countries and contributing clinical sites. Host is human; the pathogen of interest is Mycobacterium tuberculosis (complex). Clinical packaging for some TB Portals natural-history clinical data is also referenced via AccessClinicalData@NIAID.

3) CEIRR Network influenza research and response activities (https://www.ceirr-network.org/): NIAID-funded Centers of Excellence studying natural history, transmission, and pathogenesis of influenza viruses (primarily Influenza A and related orthomyxoviruses), with additional work on SARS-CoV-2 and other emerging viruses of pandemic potential. Hosts include humans and animal reservoirs relevant to zoonotic influenza; pathogen surveillance and genomic resources in this space also intersect BV-BRC (https://www.bv-brc.org/) bacterial/viral genome holdings (e.g., Influenza A virus, SARS-CoV-2, Mycobacterium).

Identify the infectious agents and host organisms involved. For each one provide:
- The scientific name
- The NCBITaxon identifier (CURIE or URI)
- Whether it is the infectiousAgent or host

Return the result formatted for the `infectiousAgent` and `host` metadata fields.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
