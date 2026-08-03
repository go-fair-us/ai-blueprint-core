---
type: NIAID Blueprint Section
title: Persistent Identifiers — Motivation
description: Why PIDs and GUPRIs matter for traceability and reproducibility
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [pids, gupri, doi, fair]
status: stable
generated: { by: niaid-bp-okf-migrate/0.2, at: 2026-08-03T12:00:00Z }
sources:
  - id: blueprint-v2
    resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
    title: 2.1. Motivation (lines 139-147)
    author: process:niaid-blueprint-publisher
source_document: NIAID_Blueprint_v2_26Sep2025_forExternal.md
source_lines: 139-147
section: 2.1. Motivation
normative: false
concept_range: 89-98
---

PIDs populated in metadata support persistence, traceability, and reproducibility. The FAIR Principles call for globally unique, persistently resolvable identifiers. The section distinguishes resolvable DOIs from basic DOI strings and notes that URLs lack DOI-level persistence without organizational commitment.[^blueprint-v2]

See also: [Requirements](/persistent-identifiers/requirements.md).

# Atomic concepts

| # | Concept | Lines |
|---|---------|-------|
| 89 | Metadata populated with PIDs ensures long-term persistence and traceability of digital objects, enabling consistent identification and access across systems, regardless of location or format changes. | 143 |
| 90 | PIDs help address reproducibility challenges, improve research quality, and support verification, transparency, and open science by linking digital objects to their documentation. | 143 |
| 91 | To maximize interoperability, the FAIR Principles call for globally unique and persistent PIDs, meaning they are persistently resolvable identifiers (GUPRIs). | 145 |
| 92 | DOIs, URLs, and IRIs provide several of these capabilities and can all be used to identify a wide range of digital objects. | 145 |
| 93 | All identifier types in Table 2 are based on URLs or IRIs and are understood to be globally unique and resolvable. | 145 |
| 94 | Some identifiers, like DOIs, are not resolvable in their basic format. | 147 |
| 95 | Prefixing a DOI with a DOI resolution path creates a resolvable DOI; e.g., prefixing '10.1000/182' with 'https://doi.org/' creates https://doi.org/10.1000/182. | 147 |
| 96 | The resolvable DOI format (https://doi.org/...) is the recommended format. | 147 |
| 97 | URLs are commonly used, but without organizational commitment they lack the same level of persistence as a resolvable DOI. | 147 |
| 98 | URL persistence limitations undermine the citation stability and reproducibility that are crucial for scientific research. | 147 |

[^blueprint-v2]: 2.1. Motivation (lines 139-147)
