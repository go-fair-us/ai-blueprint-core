# Competency-answerability runs: NIAID repositories

Built from `competency_questions.json` (answers verified 2026-10-30) for `extensions/prompts/competency-answerability.md` (`$1` = origin URL, `$2` = up to 3 questions). Each run block contains only the inputs. Paste it as the prompt's inputs. Answer keys are kept separate so graders can use them without the agent seeing them.

Origins were checked 2026-10-30 with `curl -L`. All returned HTTP 200.

## AccessClinicalData@NIAID

Origin: https://accessclinicaldata.niaid.nih.gov/

### Run A

```yaml
origin: https://accessclinicaldata.niaid.nih.gov/
questions:
  - "What ClinicalTrials.gov NCT number is registered for the AccessClinicalData@NIAID study PALM007 (Tecovirimat for Treatment of Monkeypox Virus)?"
  - "Which AccessClinicalData@NIAID study identifier (cmc_unique_id) corresponds to ClinicalTrials.gov trial NCT04640168, and what is its title?"
  - "What condition does the PALM007 study in AccessClinicalData@NIAID address, and on what date did its study start?"
```

#### Answer key: AccessClinicalData@NIAID Run A

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| ACD-1 | NCT05559099 | exact | `GET https://accessclinicaldata.niaid.nih.gov/api/studies/PALM007` | stable |
| ACD-2 | NCT04640168 — 'Adaptive COVID-19 Treatment Trial 4 (ACTT-4)' | contains: 'ACTT-4' | `GET https://accessclinicaldata.niaid.nih.gov/api/openapi.json`<br>`GET https://accessclinicaldata.niaid.nih.gov/api/studies/published` | stable (Title carries a release-note prefix '(Released May 2022)'.) |
| ACD-3 | Monkeypox; study_start_date 2022-10-10 | contains: 'Monkeypox' AND '2022-10-10' | `GET https://accessclinicaldata.niaid.nih.gov/api/studies/PALM007` | stable |

### Run B

```yaml
origin: https://accessclinicaldata.niaid.nih.gov/
questions:
  - "How many studies does AccessClinicalData@NIAID list as published?"
```

#### Answer key: AccessClinicalData@NIAID Run B

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| ACD-5 | 13 | numeric, tolerance: may grow; accept >=13 | `GET https://accessclinicaldata.niaid.nih.gov/api/studies/published` | volatile |

## TB Portals

Origin: https://tbportals.niaid.nih.gov/
_TB-1 uses the API subdomain analytic.tbportals.niaid.nih.gov, which the template allows as an obvious API subdomain._

### Run A

```yaml
origin: https://tbportals.niaid.nih.gov/
questions:
  - "What version is the TB DEPOT Analytic Data API, and what authentication scheme does it require?"
  - "According to TB Portals, which country contributes the majority of CT studies?"
  - "How many TB cases, countries, and contributing sites does the TB Portals homepage report?"
```

#### Answer key: TB Portals Run A

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| TB-1 | Version 1.4; Bearer token (obtained from /api/Token) | contains: '1.4' AND 'Bearer' | `GET https://analytic.tbportals.niaid.nih.gov/index.html`<br>`GET https://analytic.tbportals.niaid.nih.gov/swagger/Version%201.4/swagger.json` | semi-stable (Data endpoints (/api/Patient-Case, /api/Genomics, /api/DST, ...) return HTTP 401 without a token.) |
| TB-2 | Belarus | exact (case-insensitive) | `GET https://tbportals.niaid.nih.gov/where-do-our-cases-come-from` | stable |
| TB-3 | 26912 TB cases; 16 countries; 40 sites (as of October 2026) | numeric; cases tolerance ±5% (volatile); countries and sites exact | `GET https://tbportals.niaid.nih.gov/` | volatile (The same page reports 13852 genomic sequences and 29676 CXR/CT images.) |

## IEDB

Origin: https://www.iedb.org/
_The calls use query-api.iedb.org and api-nextgen-tools.iedb.org, which are IEDB API subdomains._

### Run A

```yaml
origin: https://www.iedb.org/
questions:
  - "What is the IEDB epitope ID for the linear peptide SIINFEKL?"
  - "In IEDB, what is the source antigen of epitope SIINFEKL, and which organism does it come from?"
  - "What title and version does the OpenAPI document of the Next-Generation IEDB Tools API declare, and which endpoint submits a single-tool prediction?"
```

#### Answer key: IEDB Run A

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| IEDB-1 | 58560 (IEDB_EPITOPE:58560) | exact on 58560 | `GET https://query-api.iedb.org/epitope_search?linear_sequence=eq.SIINFEKL&select=structure_id,structure_iri` | stable |
| IEDB-2 | ovalbumin (e.g., UNIPROT:P01012.2, positions 258-265); Gallus gallus (chicken), NCBITaxon:9031 | contains: 'ovalbumin' AND 'Gallus gallus' | `GET https://query-api.iedb.org/epitope_search?linear_sequence=eq.SIINFEKL&select=curated_source_antigens` | stable |
| IEDB-3 | 'Next-Generation IEDB Tools API', v3.0; POST /api/v1/predict | contains: 'v3.0' AND '/api/v1/predict' | `GET https://api-nextgen-tools.iedb.org/apidocs?format=openapi` | semi-stable |

### Run B

```yaml
origin: https://www.iedb.org/
questions:
  - "Which software release does the IEDB NG Tools API currently report?"
```

#### Answer key: IEDB Run B

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| IEDB-4 | v5.0.4 (commit 653ded8, 2026-10-29) | exact on branch_or_tag | `GET https://api-nextgen-tools.iedb.org/api/v1/version_info` | volatile |

## ImmPort

Origin: https://www.immport.org/
_https://www.immport.org/ redirects to https://www.immport.org/shared/ (200). Its docs subdomain is docs.immport.org._

### Run A

```yaml
origin: https://www.immport.org/
questions:
  - "What is the actual enrollment of ImmPort study SDY1, and what is its ClinicalTrials.gov ID?"
  - "Who is the principal investigator of ImmPort study SDY1, and what research focus does the study have?"
  - "What ontology term does ImmPort's controlled vocabulary link to the sex value 'Female'?"
```

#### Answer key: ImmPort Run A

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| IMMPORT-1 | 159; NCT00078195 | numeric exact 159; contains 'NCT00078195' | `GET https://www.immport.org/data/query/api/search/study?term=SDY1&pageSize=1` | stable |
| IMMPORT-2 | Thomas Casale (Creighton University School of Medicine); Atopy/Allergy | contains: 'Casale' AND 'Atopy/Allergy' | `GET https://www.immport.org/data/query/api/search/study?term=SDY1&pageSize=1` | stable |
| IMMPORT-3 | http://purl.bioontology.org/ontology/SNOMEDCT/248152002 (SNOMED CT 248152002) | contains: '248152002' | `GET https://www.immport.org/data/query/api/lookup/lkSex` | stable |

### Run B

```yaml
origin: https://www.immport.org/
questions:
  - "Can the ImmPort Shared Data API study-summary endpoint be used without authentication? Which controllers are public?"
```

#### Answer key: ImmPort Run B

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| IMMPORT-4 | No (HTTP 401). Only Study Search and Lookup/Controlled Vocabulary are public. | contains: '401' or 'no' AND 'Study Search' AND 'Lookup' | `GET https://www.immport.org/data/query/v3/api-docs`<br>`GET https://www.immport.org/data/query/api/study/summary/SDY1` | stable |

## BV-BRC

Origin: https://www.bv-brc.org/
_BVBRC-3 is in Run B because it is multi-step (it needs at least 2 API requests)._

### Run A

```yaml
origin: https://www.bv-brc.org/
questions:
  - "What are the genome length and GC content of BV-BRC genome 511145.12 (E. coli K-12 MG1655)?"
  - "What is the assembly accession of the Mycobacterium tuberculosis H37Rv reference genome (83332.12) in BV-BRC, and how many PATRIC CDS does it have?"
  - "According to the BV-BRC taxonomy, which genus does SARS-CoV-2 (taxon 2697049) belong to?"
```

#### Answer key: BV-BRC Run A

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| BVBRC-1 | 4639675 bp; GC 50.8% | numeric exact length; GC ±0.1 | `GET https://www.bv-brc.org/api/genome/?eq(genome_id,511145.12)&select(genome_id,genome_name,genome_length,gc_content)` | stable |
| BVBRC-2 | GCA_000195955.2; 4367 CDS | exact accession; numeric exact CDS (may change on reannotation) | `GET https://www.bv-brc.org/api/genome/?eq(genome_id,83332.12)&select(assembly_accession,patric_cds,genome_status)` | stable |
| BVBRC-4 | Betacoronavirus (subgenus Sarbecovirus, family Coronaviridae) | contains: 'Betacoronavirus' | `GET https://www.bv-brc.org/api/taxonomy/?eq(taxon_id,2697049)&select(lineage_names)` | stable |

### Run B

```yaml
origin: https://www.bv-brc.org/
questions:
  - "In BV-BRC's PATRIC annotation of M. tuberculosis H37Rv, what is the RefSeq locus tag of the katG gene, and how long is its protein?"
```

#### Answer key: BV-BRC Run B

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| BVBRC-3 | Rv1908c; 740 aa (minus strand, 2153889-2156111) | exact 'Rv1908c'; numeric 740 | `GET https://www.bv-brc.org/api/genome/?and(eq(taxon_id,83332),eq(reference_genome,Reference))&select(genome_id,genome_name)`<br>`GET https://www.bv-brc.org/api/genome_feature/?and(eq(genome_id,83332.12),eq(gene,katG),eq(annotation,PATRIC))&select(patric_id,refseq_locus_tag,aa_length,start,end,strand)` | stable (A plain genome_name match is ambiguous (it returns H37Rv variants under taxon 1773). Use the reference_genome filter.) |

## VEuPathDB (PlasmoDB component site)

Origin: https://plasmodb.org/
_All of these questions are answered on plasmodb.org, a VEuPathDB component site that is a separate host from veupathdb.org. The origin is therefore https://plasmodb.org/ (redirects to /plasmo/, 200). Using https://veupathdb.org/ (redirects to /veupathdb/, 200) would put these calls off-host under the template's rules._

### Run A

```yaml
origin: https://plasmodb.org/
questions:
  - "In PlasmoDB, what product and gene name are given for gene PF3D7_1133400?"
  - "Can an anonymous agent fetch a gene record from the PlasmoDB WDK service (POST /plasmo/service/record-types/gene/records)? What does the service return?"
  - "Start from the PlasmoDB service root. Is 'gene' a record type, and what is the URL segment of the gene search that finds all genes from one or more species?"
```

#### Answer key: VEuPathDB (PlasmoDB component site) Run A

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| VEU-1 | apical membrane antigen 1; AMA1 (protein coding gene, Plasmodium falciparum 3D7) | contains: 'apical membrane antigen 1' | `POST https://plasmodb.org/site-search` body `{"searchText": "PF3D7_1133400", "pagination": {"offset": 0, "numRecords": 1}, "restrictToProject": "PlasmoDB", "documentTypeFilter": {"documentType": "gene"}}` | stable (The WDK record endpoints (POST /plasmo/service/record-types/gene/records and search reports) now return 'Valid API Key required'. Public site-search still works.) |
| VEU-3 | No. The service returns 'Valid API Key required for this endpoint.' and points to the user profile serviceAccess page. | contains: 'API Key required' | `POST https://plasmodb.org/plasmo/service/record-types/gene/records` body `{"primaryKey": [{"name": "source_id", "value": "PF3D7_1133400"}, {"name": "project_id", "value": "PlasmoDB"}], "attributes": ["product"], "tables": []}` | semi-stable |
| VEU-4 | Yes; GenesByTaxonGene | exact 'GenesByTaxonGene' | `GET https://plasmodb.org/plasmo/service/record-types`<br>`GET https://plasmodb.org/plasmo/service/record-types/gene` | stable |

### Run B

```yaml
origin: https://plasmodb.org/
questions:
  - "Which build number and release date does the PlasmoDB web service report?"
```

#### Answer key: VEuPathDB (PlasmoDB component site) Run B

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| VEU-2 | Build 71; 20 August 2026 | exact on build; contains date | `GET https://plasmodb.org/plasmo/service` | volatile (Changes with each VEuPathDB release, roughly every 2-3 months.) |

## Cross-repository questions (outside the template's scope)

`competency-answerability.md` only allows fetches on the repository host and its obvious API or docs subdomains. These questions need two separate repository hosts, so a strict run would fail them by design. Use them only in an extended or multi-host test. There are 2 of them, not 3: ACD-4 and TB-4 are the only questions in the JSON that span two hosts.

### ACD-4 (needs www.immport.org)

```yaml
origin: https://accessclinicaldata.niaid.nih.gov/
questions:
  - "AccessClinicalData@NIAID lists the IMPACC COVID-19 cohort study under an ImmPort accession. What's that accession, and what's the actual enrollment that ImmPort reports for it?"
```

### TB-4 (needs accessclinicaldata.niaid.nih.gov)

```yaml
origin: https://tbportals.niaid.nih.gov/
questions:
  - "TB Portals clinical data requests now go through AccessClinicalData@NIAID. What start date does that site give for the TB Portals Natural History Study, and what is the study's completion status?"
```

#### Answer key: cross-repository

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| ACD-4 | SDY1760; actual_enrollment 1185 | exact on 'SDY1760'; numeric exact 1185 | `GET https://accessclinicaldata.niaid.nih.gov/api/studies/published`<br>`GET https://www.immport.org/data/query/api/search/study?term=SDY1760&pageSize=1` | stable (Cross-repository question. ImmPort returned study_pi values that look like curator names (Bjoern Peters, LJI), so the PI was left out of the question.) |
| TB-4 | 2013-01-01; ongoing | contains: '2013-01-01' AND 'ongoing' | `GET https://tbportals.niaid.nih.gov/`<br>`GET https://accessclinicaldata.niaid.nih.gov/api/studies/tb-portals-natural-history-study` | stable |
