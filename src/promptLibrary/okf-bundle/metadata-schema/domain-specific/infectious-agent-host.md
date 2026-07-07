---
type: Prompt
title: Add infectiousAgent and host metadata using NCBITaxon
description: Identifies the correct NCBITaxon terms for pathogens and hosts and formats them for the NIAID Blueprint metadata schema.
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [metadata-schema, domain-specific, infectiousagent, host, ncbitaxon]
---

# Prompt

You are helping annotate a dataset according to the NIAID Blueprint.

Study description:
{{study_description}}

Identify the infectious agents and host organisms involved. For each one provide:
- The scientific name
- The NCBITaxon identifier (CURIE or URI)
- Whether it is the infectiousAgent or host

Return the result formatted for the `infectiousAgent` and `host` metadata fields.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
