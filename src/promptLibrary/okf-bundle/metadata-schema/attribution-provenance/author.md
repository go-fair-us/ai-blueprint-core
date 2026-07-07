---
type: Prompt
title: Format author metadata with ORCID and ROR
description: Creates properly structured author entries that include both personal (ORCID) and organizational (ROR) identifiers as recommended by the Blueprint.
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [metadata-schema, attribution, author, orcid, ror]
---

# Prompt

You are an expert in the NIAID Blueprint metadata schema.

Given the list of people and organizations involved in creating this digital object, generate the `author` metadata array following NIAID recommendations.

For each person include their name, ORCID (if known), and affiliation with ROR when possible.

Input:
{{creators_list}}

Output the result as valid JSON matching the NIAID Blueprint author structure.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
