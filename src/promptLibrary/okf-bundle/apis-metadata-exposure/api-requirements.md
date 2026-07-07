---
type: Prompt
title: Design a minimal metadata API for a repository
description: Creates a simple OpenAPI-style specification or description for exposing metadata in a way that satisfies the NIAID Blueprint minimal API requirements.
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [apis, metadata-exposure, openapi, json-ld]
---

# Prompt

You are helping a repository implement the 'Minimal API Specifications for Exposing Metadata to Machines' section of the NIAID Blueprint.

Repository name: {{repo_name}}
Current tech stack: {{tech_stack}}

Propose a minimal but compliant API design. Include:
- Recommended endpoints
- Required query parameters
- Response format (JSON-LD preferred)
- How to handle the core metadata elements from the Blueprint

Keep it practical and aligned with the Blueprint's goals.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
