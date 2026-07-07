---
type: Prompt
title: Generate funder and grant metadata
description: Produces correctly formatted `funder` and `grant` metadata elements according to the NIAID Blueprint.
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [metadata-schema, attribution, funder, grant, ror]
---

# Prompt

Help a researcher create compliant `funder` and `grant` metadata for the NIAID Blueprint.

Project title: {{project_title}}
Funding organizations: {{funders}}
Grant or contract numbers: {{grant_numbers}}

Generate the metadata as JSON with `funder` (using ROR where possible) and `grant` fields.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
