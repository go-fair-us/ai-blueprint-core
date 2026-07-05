---
type: NIAID Blueprint Requirements
title: Minimal API Specifications — Requirements
description: Flexible exposure options and minimum API objectives for JSON-LD metadata
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [api, json-ld, openapi, object-server]
source_document: NIAID_Blueprint_v2_26Sep2025_forExternal.md
source_lines: 182-199
section: 3.2. Blueprint Requirements
normative: true
concept_range: 121-137
---

API recommendations are customizable per repository, with alternatives ranging from HTML-embedded metadata to advanced knowledge graphs. Minimum objectives require exposing Table 1 elements via JSON-LD, resource-oriented IRIs, HTTP GET retrieval, and OpenAPI/Swagger documentation.

See also: [Requirements](/metadata-schema/requirements.md), [JSON Ld Examples](/appendix/json-ld-examples.md).

# Atomic concepts

| # | Concept | Lines |
|---|---------|-------|
| 121 | API recommendations are designed to be customized during the implementation phase to address the needs of each repository in exposing metadata for human or machine access. | 184 |
| 122 | If a repository or data generator is not able to develop an API, they can add HTML with embedded metadata or a downloadable index of the metadata in a computer-accessible format. | 184 |
| 123 | Repositories with advanced API infrastructure could develop complementary services, such as a queryable metadata knowledge graph. | 184 |
| 124 | Any of these options would allow a data provider to share resources in a way that facilitates metadata collection and aggregation. | 186 |
| 125 | In Figure 2, 'Example Resource' could be a webpage with HTML embedded metadata, an object server delivering a direct byte stream, or a database. | 186 |
| 126 | The term 'Object Server' refers to the endpoint that delivers the bytes of a digital object or its metadata, rather than the repository where they are stored. | 186 |
| 127 | The 'HTML embedded metadata' approach means structured metadata (such as JSON-LD) is built directly into a webpage describing the resource. | 186 |
| 128 | The 'Object Server' approach delivers the JSON-LD or other metadata as a byte stream directly. | 186 |
| 129 | HTML embedded metadata and Object Server approaches are alternative access methods to the Example Resource, not simultaneous connections. | 186 |
| 130 | In practice, an API may return anywhere from one to many resources, each containing both a data byte stream and its associated metadata byte stream. | 186 |
| 131 | For standardized machine access to metadata, APIs should expose metadata elements described in Table 1. | 192 |
| 132 | Metadata Encoding objective: API responses should return metadata encoded in JSON-LD, at least as an option, following the minimal metadata specification types and properties. | 194-195 |
| 133 | IRI (URL) Structure objective: API endpoints should be designed as resource-oriented IRIs (e.g., /datasets/{dataset_id}), avoiding verbs and complex query parameters in the IRI structure. | 196 |
| 134 | Resource-oriented IRIs can function as persistent identifiers within the JSON-LD @id field, enabling seamless integration into knowledge graphs. | 196 |
| 135 | HTTP Method objective: metadata retrieval should be performed using HTTP GET; POST may be used when parameters must be sent in the message body for large or complex queries or security requirements. | 197 |
| 136 | Documentation objective: API documentation should adhere to OpenAPI/Swagger specifications for machine-readability and ease of use. | 198 |
| 137 | An example of API-exposed metadata formatted to meet these objectives is given in Supplemental Table 7. | 199 |

# Citations

[1] [3.2. Blueprint Requirements](https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md) (lines 182–199)
