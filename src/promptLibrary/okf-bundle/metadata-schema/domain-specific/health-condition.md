---
type: Prompt
title: Map health conditions to MONDO terms
description: Finds appropriate MONDO identifiers for health conditions mentioned in a study and formats them for Blueprint metadata.
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [metadata-schema, domain-specific, healthcondition, mondo]
---

# Prompt

Map the following health conditions or diseases to MONDO ontology terms for use in NIAID Blueprint metadata.

Health conditions mentioned: {{conditions}}

For each condition return the preferred MONDO label and identifier. Format the output for the `healthCondition` metadata field.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
