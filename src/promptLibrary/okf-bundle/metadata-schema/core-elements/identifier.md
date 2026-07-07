---
type: Prompt
title: Recommend appropriate persistent identifiers
description: Helps choose the right type of persistent identifier (DOI, accession number, etc.) and explains how to record it according to the NIAID Blueprint.
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [metadata-schema, core-elements, identifier, doi, pid]
---

# Prompt

You are helping a research team implement the NIAID Blueprint Persistent Identifiers requirements.

A researcher has the following digital object and wants to know what persistent identifier(s) they should use and how to record it in metadata.

Digital object type: {{type}}
Current identifiers they have: {{existing_ids}}
Repository they plan to deposit in: {{repository}}

Recommend the best identifier strategy according to the NIAID Blueprint. Explain why and show exactly how it should appear in the `identifier` metadata field.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
