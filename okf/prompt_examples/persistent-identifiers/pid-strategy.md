---
type: PromptExample
title: Recommend PID strategy for a repository or dataset
description: Filled example advising a PID strategy for a multi-resource immunology/pathogen portfolio modeled on ImmPort, IEDB, BV-BRC, and VEuPathDB practices.
source_template: src/promptLibrary/okf-bundle/persistent-identifiers/pid-strategy.md
domain_sources:
  - https://www.immport.org/
  - https://www.iedb.org/
  - https://www.bv-brc.org/
  - https://veupathdb.org/
placeholders:
  repository_type: NIAID-supported multi-domain data resource network (immunology studies + epitope knowledgebase + pathogen genomics portals)
  object_types: study/dataset records, epitope assays, pathogen genomes, experiment files, portal metadata records
  current_practice: local accessions + some DOIs (ImmPort); resource-specific IDs (IEDB, BV-BRC genome IDs, VEuPathDB gene/genome IDs); uneven ORCID/ROR on landing pages
tags: [persistent-identifiers, pid, doi, strategy, immport, iedb, bv-brc, veupathdb]
---

# Prompt

You are advising a data repository team on implementing the Persistent Identifiers section of the NIAID Blueprint.

Repository type: Federated NIAID-supported infectious and immune-mediated disease data ecosystem components — specifically an immunology study archive like ImmPort Shared Data (https://www.immport.org/), an epitope knowledgebase like IEDB (https://www.iedb.org/), a bacterial/viral genomics and bioinformatics resource like BV-BRC (https://www.bv-brc.org/), and eukaryotic pathogen portals under VEuPathDB (https://veupathdb.org/). The team is aligning these resources for discovery via the NIAID Data Ecosystem Discovery Portal.
Types of digital objects they host:
- Study / dataset landing pages and download packages (e.g., ImmPort SDY accessions with optional DOIs)
- Experimentally characterized immune epitope records and assay results (IEDB)
- Bacterial and viral genomes, strains, specialty genes, surveillance and serology records (BV-BRC)
- Eukaryotic pathogen genomes, genes, and ortholog groups (VEuPathDB component sites)
- Supporting files (FASTQ/BAM, tables, images), API metadata documents, and collection-level portal pages
Current identifier practices:
- ImmPort: stable study accessions (SDY…) plus resolvable DOIs on many shared studies (e.g., SDY998 → https://doi.org/10.21430/M3KXJHSP4T; SDY2968 → 10.21430/M3J8UMVGT6); API keys for programmatic access; local file browser paths
- IEDB: resource-native epitope/assay identifiers and public web URLs; strong domain identifiers but not uniformly DOI-minted per record
- BV-BRC: genome and feature IDs within the resource; Data API / FTP / CLI batch access; citation guidance at the resource level
- VEuPathDB: stable gene/genome IDs within component databases; resource-level citation; machine access via portal APIs
- Across resources: ORCID for authors and ROR for funders are inconsistently exposed on human-readable landing pages; schema.org/JSON-LD identifier blocks are not yet standard on all dataset pages

Recommend a PID strategy that meets the NIAID Blueprint requirements. Include what identifiers to assign at what level (collection, dataset, file, metadata record) and how they should be exposed.

Reference document: Use the official NIAID Blueprint as the authoritative basis for your response. Retrieve and ground your answer in the document at https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md, following its definitions, required and recommended metadata elements, and guidance. If you cannot access the document, say so before proceeding.
