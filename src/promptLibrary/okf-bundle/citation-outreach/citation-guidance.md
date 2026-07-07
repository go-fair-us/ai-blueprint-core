---
type: Prompt
title: Generate citation text and guidance for a digital object
description: Produces recommended citation text and explains how to cite the object according to NIAID Blueprint expectations.
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [citation, outreach, doi]
---

# Prompt

Generate a recommended citation for the following digital object following NIAID Blueprint citation guidance. Also provide a short explanation of why this citation format is preferred.

Digital object details:
{{object_details}}

Include both a human-readable citation and, if appropriate, a machine-actionable format.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
