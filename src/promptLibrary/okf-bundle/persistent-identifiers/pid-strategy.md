---
type: Prompt
title: Recommend PID strategy for a repository or dataset
description: Helps teams decide on the right persistent identifier approach based on their repository and data type.
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [persistent-identifiers, pid, doi, strategy]
---

# Prompt

You are advising a data repository team on implementing the Persistent Identifiers section of the NIAID Blueprint.

Repository type: {{repository_type}}
Types of digital objects they host: {{object_types}}
Current identifier practices: {{current_practice}}

Recommend a PID strategy that meets the NIAID Blueprint requirements. Include what identifiers to assign at what level (collection, dataset, file, metadata record) and how they should be exposed.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
