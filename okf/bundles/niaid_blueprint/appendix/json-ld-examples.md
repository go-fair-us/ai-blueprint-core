---
type: Worked Example
title: Worked Example — JSON-LD Encodings
description: Supplemental Table 7 ImmPort-based JSON-LD API examples
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [json-ld, schema.org, immport, supplemental-table-7]
source_document: NIAID_Blueprint_v2_26Sep2025_forExternal.md
source_lines: 430-436
section: Supplemental Table 7. Example JSON-LD Encodings
normative: false
concept_range: 235-239
---

Supplemental Table 7 presents truncated ImmPort SDY998 JSON-LD examples illustrating Blueprint-aligned schema.org metadata, recommended API request patterns, and @id resolution expectations.

See also: [Requirements](/api-specification/requirements.md).

# Atomic concepts

| # | Concept | Lines |
|---|---------|-------|
| 235 | Supplemental Table 7 provides two examples of summary metadata (derived from ImmPort study SDY998) expressed as schema.org-based JSON-LD attributes and values. | 432 |
| 236 | The first JSON-LD example shows a small subset of Blueprint attributes; the second shows all attributes from the Blueprint. | 432 |
| 237 | The JSON-LD examples truncate and modify the complete ImmPort summary metadata to focus on Blueprint attributes and will not match actual ImmPort JSON data. | 432 |
| 238 | An IRI request to obtain JSON-LD data can follow a pattern like https://data.<domain.org>/<entity>/<instanceID>?format=json-ld, analogous to the ImmPort API pattern. | 434 |
| 239 | The JSON-LD document's '@id' node (at the top) should resolve to the document when de-referenced; the examples use a demonstration @id based on the example.org domain. | 436 |

# Citations

[1] [Supplemental Table 7. Example JSON-LD Encodings](https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md) (lines 430–436)
