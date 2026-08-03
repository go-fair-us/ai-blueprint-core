---
type: NIAID Blueprint Requirements
title: Persistent Identifiers — Requirements
description: Table 2 PID mappings and ontology population guidance
resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
tags: [doi, orcid, ror, rrid, isni, table-2]
status: stable
generated: { by: niaid-bp-okf-migrate/0.2, at: 2026-08-03T12:00:00Z }
sources:
  - id: blueprint-v2
    resource: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
    title: 2.2. Blueprint Requirements (lines 149-170)
    author: process:niaid-blueprint-publisher
source_document: NIAID_Blueprint_v2_26Sep2025_forExternal.md
source_lines: 149-170
section: 2.2. Blueprint Requirements
normative: true
concept_range: 99-116
---

The Blueprint maps Table 1 metadata elements to default PIDs in Table 2, with DOI as the default object identifier and ORCID, ROR, and IRI for other fields. Researchers may register DOIs through agencies when repositories lack registration services. Ontologies complement PID usage for several elements.[^blueprint-v2]

See also: [Requirements](/metadata-schema/requirements.md), [Ontology Mappings](/appendix/ontology-mappings.md).

# Atomic concepts

| # | Concept | Lines |
|---|---------|-------|
| 99 | The NIAID Blueprint specifies certain PIDs to represent metadata (Table 1). | 151 |
| 100 | Metadata elements from Table 1 are mapped to default PIDs, emphasizing how default requirements improve alignment between repositories. | 151 |
| 101 | Each digital object should be assigned a DOI (default option), populated in the metadata element labeled 'identifier.' | 151 |
| 102 | Additional metadata fields such as 'author,' 'funder,' and 'citation' should be populated with an ORCID, ROR, or IRI, respectively. | 151 |
| 103 | Using alternative PIDs may be appropriate in certain circumstances. | 151 |
| 104 | Many repositories will include an option to generate a DOI or another PID when depositing data or other digital objects. | 153 |
| 105 | If sharing to a repository without PID registration service, researchers can register their digital objects with a DOI registration agency such as Crossref or DataCite. | 153 |
| 106 | Several metadata elements can be populated with ontologies, or standard vocabularies. | 155 |
| 107 | Examples of ontologies in Table 1 include MONDO Disease Ontology for healthCondition and NCBITaxon for infectiousAgent and host. | 155 |
| 108 | Additional descriptions and examples of default and alternative ontologies are found in Supplemental Table 5. | 155 |
| 109 | Table 2 identifier—Digital Object Identifier (DOI): a unique and persistent alphanumeric string assigned to a digital object to provide a permanent link to its location on the internet. | 161 |
| 110 | Table 2 identifier—Research Resource Identification (RRID): a persistent identification number assigned to key biological resources to help cite resources used in biomedical research. | 162 |
| 111 | Table 2 identifier—Uniform Resource Locator (URL) is listed as an alternative identifier type. | 163 |
| 112 | Table 2 identifier—Internationalized Resource Identifier (IRI): a flexible identifier supporting a wider range of characters, including non-ASCII characters. | 164 |
| 113 | Table 2 funder—Research Organization Registry (ROR): identifiers for research institutions including universities, research centers, and scholarly organizations. | 166 |
| 114 | Table 2 author—Open Researcher and Contributor Identifier (ORCID): identifier for researchers and academics. | 168 |
| 115 | Table 2 author—International Standard Name Identifier (ISNI): a unique identifier for public contributors to creative works. | 169 |
| 116 | Table 2 author—Research Organization Registry (ROR) is also listed as an author identifier type. | 170 |

[^blueprint-v2]: 2.2. Blueprint Requirements (lines 149-170)
