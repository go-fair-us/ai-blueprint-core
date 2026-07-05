---
type: NIAID Blueprint Requirements
title: NIAID Minimal Metadata Schema — Requirements
description: Table 1 metadata elements, formats, and schema.org basis
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [table-1, schema.org, doi, orcid, ror, ncbitaxon, mondo]
source_document: NIAID_Blueprint_v2_26Sep2025_forExternal.md
source_lines: 97-133
section: 1.2. Blueprint Requirements
normative: true
concept_range: 56-83
---

Table 1 defines the minimum metadata standard with schema.org as the preferred basis and default value formats for each element. Repositories choose their own storage format. The table spans core descriptive fields through IID-specific elements, with default PIDs and ontologies noted and alternatives permitted in certain circumstances.

See also: [Metadata Schema — Motivation](/metadata-schema/motivation.md), [Persistent Identifiers — Requirements](/persistent-identifiers/requirements.md), [Metadata Schemas](/appendix/metadata-schemas.md).

# Atomic concepts

| # | Concept | Lines |
|---|---------|-------|
| 56 | Table 1 presents the metadata elements, along with default value formats, reflecting a minimum standard for understanding and using digital objects. | 99 |
| 57 | The Blueprint does not specify a metadata storage format (e.g., JSON, YML, XML); repositories should select one that best fits their implementation needs. | 99 |
| 58 | The metadata elements in Table 1 are based on schema.org, a widely adopted framework that defines the relationship between data elements within a domain. | 101 |
| 59 | Other schemas may be appropriate if they are interoperable with schema.org, widely used, openly available, and maintained by a community (Supplemental Table 2). | 101 |
| 60 | The preferred default representation in Table 1 supports alignment across the NIAID ecosystem. | 101 |
| 61 | These defaults reflect common NIH/NIAID practices and will continue to evolve with community input. | 101 |
| 62 | Metadata element 'type' identifies the type of digital object; default format is IRI to type (e.g., 'dataset', 'software application', 'image'). | 107-111 |
| 63 | Metadata element 'identifier' is a globally unique, persistent, machine-resolvable identifier (GUPRI); default format is Resolvable DOI. | 113 |
| 64 | Metadata element 'name' is the descriptive title or name of the digital object; default format is free text. | 114 |
| 65 | Metadata element 'description' is a description of the digital object; default format is free text. | 115 |
| 66 | Metadata element 'dateCreated' is the date the digital object was created or added to a repository; default format is Date (ISO 8601). | 116 |
| 67 | Metadata element 'author' is the person or organization responsible for creation; default format is ORCID. | 117 |
| 68 | Metadata element 'funder' is the organization(s) that provided funding; default format is ROR. | 118 |
| 69 | Metadata element 'grant' is grant or contract number(s); default format is alphanumeric string. | 119 |
| 70 | Metadata element 'measurementTechnique' is technique(s) or technologies used in measurement, if applicable; default format is NCIT. | 120 |
| 71 | Metadata element 'distribution' provides link(s) to the downloadable distribution (direct link to bit stream or file); default format is IRI (URL). | 121 |
| 72 | Metadata element 'citation' is a citation or reference to another creative work related to the digital object; default format is IRI (URL). | 122 |
| 73 | Metadata element 'infectiousAgent' describes infectious agent(s) involved; default format is NCBITaxon. | 123 |
| 74 | Metadata element 'host' describes host organism(s); default format is NCBITaxon. | 124 |
| 75 | Metadata element 'healthCondition' describes the health condition; default format is MONDO. | 125 |
| 76 | Metadata element 'conditionsOfAccess' describes conditions under which the object can be accessed; default format is IRI (URL) to resources describing access levels such as 'open,' 'registered,' or 'controlled.' | 126 |
| 77 | Metadata element 'license' describes license(s) under which the object is distributed; default format is SPDX License Identifier or IRI to a license document if not listed in SPDX. | 127 |
| 78 | Metadata element 'spatialCoverage' is the geographic area covered; default format is Country Code (ISO 3166). | 129 |
| 79 | Metadata element 'temporalCoverage' is the time period covered; default format is date range (ISO 8601 for start/end). | 131 |
| 80 | Fields marked with ** in Table 1 may accept multiple entries (e.g., multiple authors via multiple fields and/or values). | 133 |
| 81 | Best practices for completing metadata fields will differ by repository. | 133 |
| 82 | Default PIDs and ontologies in the 'Required Element Representation' column may have acceptable alternatives in certain circumstances. | 133 |
| 83 | Refer to Table 2 for PIDs and Supplementary Table 5 for ontologies. | 133 |

# Citations

[1] [1.2. Blueprint Requirements](https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md) (lines 97–133)
