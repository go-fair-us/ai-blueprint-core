---
type: PromptExample
title: Write a high-quality name + description for a digital object
description: Filled example for name/description generation, grounded in TB Portals multi-domain TB case data and AccessClinicalData@NIAID clinical-trial packaging.
source_template: src/promptLibrary/okf-bundle/metadata-schema/core-elements/name-description.md
domain_sources:
  - https://tbportals.niaid.nih.gov/
  - https://accessclinicaldata.niaid.nih.gov/
placeholders:
  digital_object_info: TB Portals multi-domain natural-history style case collection (clinical + imaging + M. tuberculosis genomics), with clinical packaging referenced via AccessClinicalData@NIAID
tags: [metadata-schema, core-elements, name, description, tb-portals, acdn]
---

# Prompt

You are an expert data steward helping researchers comply with the NIAID Blueprint for Including Digital Objects in the NIAID Data Ecosystem.

Given the following information about a digital object, write:
1. A clear, concise, and descriptive `name` (title)
2. A rich `description` (3-6 sentences) that explains what the object is, why it was created, what it contains, and how it can be used.

Make the description suitable for both human readers and machine discovery. Emphasize any infectious agents, hosts, health conditions, or measurement techniques when relevant.

Digital object information:
- Resource family: NIAID TB Portals (https://tbportals.niaid.nih.gov/) multi-domain tuberculosis research platform, with clinical data access routed through AccessClinicalData@NIAID (https://accessclinicaldata.niaid.nih.gov/) for the TB Portals natural history study packaging.
- Content (approximate scale as published on TB Portals): tens of thousands of TB case records spanning ~16 countries and ~40 contributing sites; linked clinical case metadata; chest X-ray and CT imaging studies; Mycobacterium tuberculosis genomic sequences.
- Purpose: advance TB research and public health impact through open-access, multi-domain global TB data and analysis tools (case exploration, virtual cohorts, genomics/drug-resistance analysis, radiomics).
- Host: Homo sapiens (patient cases). Infectious agent: Mycobacterium tuberculosis complex.
- Data domains: clinical / epidemiologic case descriptors; imaging (radiology); pathogen genomics.
- Intended users: TB clinical researchers, computational biologists, imaging AI developers, public-health analysts seeking multi-domain linked case cohorts.
- Access note: pathogen genomic and imaging data requests remain on TB Portals; clinical data requests are handled via AccessClinicalData@NIAID study viewer for the TB Portals natural history study.

Return the result as clean JSON with keys: name, description.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
