---
type: PromptExample
title: Design a minimal metadata API for a repository
description: Filled example for minimal Blueprint-aligned metadata API design, grounded in ImmPort OpenAPI/DRS/FHIR stack and TB Portals / BV-BRC programmatic access patterns.
source_template: src/promptLibrary/okf-bundle/apis-metadata-exposure/api-requirements.md
domain_sources:
  - https://www.immport.org/
  - https://docs.immport.org/apidocumentation/
  - hhttps://accessclinicaldata.niaid.nih.gov/
  https://www.bv-brc.org/
  https://www.ceirr-network.org/
  https://clinepidb.org/
  https://www.iedb.org/
  https://www.immport.org/
  https://www.itntrialshare.org/
  https://statepi.jhsph.edu/mwccs/
  https://tbportals.niaid.nih.gov/
  https://veupathdb.org/
  https://immunspace.org/robots.txtttps://tbportals.niaid.nih.gov/
  - https://www.bv-brc.org/
placeholders:
  repo_name: ImmPort Shared Data (with notes from TB Portals API and BV-BRC Data API peers)
  tech_stack: OpenAPI 3 / Swagger UI, scoped API keys, GA4GH DRS, FHIR endpoints; peers use REST Data APIs and FTP/CLI
tags: [apis, metadata-exposure, openapi, json-ld, immport, tb-portals, bv-brc]
---

# Prompt

You are helping a repository implement the 'Minimal API Specifications for Exposing Metadata to Machines' section of the NIAID Blueprint.

Repository name: ImmPort Shared Data (https://www.immport.org/) — primary target. Peer patterns to keep in mind for NIAID IID interoperability: TB Portals programmatic access to clinical/radiological/genomic TB case data (https://tbportals.niaid.nih.gov/), and BV-BRC Data API + FTP + CLI batch access (https://www.bv-brc.org/api/doc/; https://www.bv-brc.org/).
Current tech stack:
- ImmPort Shared Data endpoints documented with OpenAPI 3.0 and exposed via Swagger UI for interactive exploration (https://docs.immport.org/apidocumentation/)
- Scoped API keys / Bearer token authentication for API access
- Study metadata example pattern: https://immport.org/data/query/api/study/SDY998?format=json (landing page counterpart https://immport.org/shared/study/SDY998)
- Additional machine interfaces already in use or documented: GA4GH DRS for data objects; FHIR endpoints for some clinical-style resources
- Download paths require authenticated access under the ImmPort user agreement
- Goal: extend or wrap existing JSON study APIs so responses can be requested as schema.org JSON-LD covering Blueprint Table 1 core elements (identifier, name, description, author, funder, license, distribution, infectiousAgent, host, healthCondition, etc.), following Blueprint Supplemental Table 7 ImmPort-based JSON-LD patterns

Propose a minimal but compliant API design. Include:
- Recommended endpoints
- Required query parameters
- Response format (JSON-LD preferred)
- How to handle the core metadata elements from the Blueprint

Keep it practical and aligned with the Blueprint's goals.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
