# NIAID Data Repository Competency Questions (test set)

Retrieved 2026-10-30. All answers were verified with live HTTP calls (curl, no credentials). Questions follow `competency-answerability.md`: each has one checkable answer (count, name, ID, or yes/no) that can be answered within 5 requests from public resources. Run up to 3 per origin as that prompt's `questions` input.

Template mapping: every CQ maps to `competency-answerability`. Secondary tags name the readiness feature the path uses (`metadata-api`, `openapi-discovery`, `persistent-identifiers`, `vocabulary`, `api-http-behavior`, `provenance-lineage`, `server-rendered-content`).


## AccessClinicalData@NIAID

### ACD-1 (lookup, stable)
**Q:** What ClinicalTrials.gov NCT number is registered for the AccessClinicalData@NIAID study PALM007 (Tecovirimat for Treatment of Monkeypox Virus)?  
**Expected answer:** NCT05559099  
**Check:** exact  
**Templates:** competency-answerability, metadata-api, persistent-identifiers  
**API calls:**
- `GET https://accessclinicaldata.niaid.nih.gov/api/studies/PALM007` — {"field": "nct_number"}

### ACD-2 (discovery, stable)
**Q:** Which AccessClinicalData@NIAID study identifier (cmc_unique_id) corresponds to ClinicalTrials.gov trial NCT04640168, and what is its title?  
**Expected answer:** NCT04640168 — 'Adaptive COVID-19 Treatment Trial 4 (ACTT-4)'  
**Check:** contains: 'ACTT-4'  
**Templates:** competency-answerability, openapi-discovery, metadata-api  
**API calls:**
- `GET https://accessclinicaldata.niaid.nih.gov/api/openapi.json` — {"purpose": "discover endpoints"}
- `GET https://accessclinicaldata.niaid.nih.gov/api/studies/published` — {"filter": "nct_number == NCT04640168"}

_Note:_ Title carries a release-note prefix '(Released May 2022)'.

### ACD-3 (lookup, stable)
**Q:** What condition does the PALM007 study in AccessClinicalData@NIAID address, and on what date did its study start?  
**Expected answer:** Monkeypox; study_start_date 2022-10-10  
**Check:** contains: 'Monkeypox' AND '2022-10-10'  
**Templates:** competency-answerability, metadata-api  
**API calls:**
- `GET https://accessclinicaldata.niaid.nih.gov/api/studies/PALM007` — {"fields": ["condition", "study_start_date"]}

### ACD-4 (multi-step, stable)
**Q:** AccessClinicalData@NIAID lists the IMPACC COVID-19 cohort study under an ImmPort accession. What's that accession, and what's the actual enrollment that ImmPort reports for it?  
**Expected answer:** SDY1760; actual_enrollment 1185  
**Check:** exact on 'SDY1760'; numeric exact 1185  
**Templates:** competency-answerability, metadata-api, persistent-identifiers  
**API calls:**
- `GET https://accessclinicaldata.niaid.nih.gov/api/studies/published` — {"filter": "title contains 'IMPACC' -> cmc_unique_id"}
- `GET https://www.immport.org/data/query/api/search/study?term=SDY1760&pageSize=1` — {"field": "hits.hits[0]._source.actual_enrollment"}

_Note:_ Cross-repository question. ImmPort returned study_pi values that look like curator names (Bjoern Peters, LJI), so the PI was left out of the question.

### ACD-5 (aggregate, volatile)
**Q:** How many studies does AccessClinicalData@NIAID list as published?  
**Expected answer:** 13  
**Check:** numeric, tolerance: may grow; accept >=13  
**Templates:** competency-answerability, metadata-api  
**API calls:**
- `GET https://accessclinicaldata.niaid.nih.gov/api/studies/published` — {"op": "len(array)"}


## TB Portals

### TB-1 (discovery, semi-stable)
**Q:** What version is the TB DEPOT Analytic Data API, and what authentication scheme does it require?  
**Expected answer:** Version 1.4; Bearer token (obtained from /api/Token)  
**Check:** contains: '1.4' AND 'Bearer'  
**Templates:** competency-answerability, openapi-discovery, api-http-behavior  
**API calls:**
- `GET https://analytic.tbportals.niaid.nih.gov/index.html` — {"purpose": "Swagger UI (linked from datasharing.tbportals.niaid.nih.gov data-api page)"}
- `GET https://analytic.tbportals.niaid.nih.gov/swagger/Version%201.4/swagger.json` — {"fields": ["info.version", "components.securitySchemes"]}

_Note:_ Data endpoints (/api/Patient-Case, /api/Genomics, /api/DST, ...) return HTTP 401 without a token.

### TB-2 (lookup, stable)
**Q:** According to TB Portals, which country contributes the majority of CT studies?  
**Expected answer:** Belarus  
**Check:** exact (case-insensitive)  
**Templates:** competency-answerability, server-rendered-content  
**API calls:**
- `GET https://tbportals.niaid.nih.gov/where-do-our-cases-come-from` — {"quote": "The majority of CT studies come from TB patients in Belarus"}

### TB-3 (aggregate, volatile)
**Q:** How many TB cases, countries, and contributing sites does the TB Portals homepage report?  
**Expected answer:** 26912 TB cases; 16 countries; 40 sites (as of October 2026)  
**Check:** numeric; cases tolerance ±5% (volatile); countries and sites exact  
**Templates:** competency-answerability, server-rendered-content  
**API calls:**
- `GET https://tbportals.niaid.nih.gov/` — {"parse": "stats block"}

_Note:_ The same page reports 13852 genomic sequences and 29676 CXR/CT images.

### TB-4 (multi-step, stable)
**Q:** TB Portals clinical data requests now go through AccessClinicalData@NIAID. What start date does that site give for the TB Portals Natural History Study, and what is the study's completion status?  
**Expected answer:** 2013-01-01; ongoing  
**Check:** contains: '2013-01-01' AND 'ongoing'  
**Templates:** competency-answerability, metadata-api  
**API calls:**
- `GET https://tbportals.niaid.nih.gov/` — {"purpose": "banner: 'Clinical data requests have moved to accessclinicaldata@NIAID'"}
- `GET https://accessclinicaldata.niaid.nih.gov/api/studies/tb-portals-natural-history-study` — {"fields": ["study_start_date", "study_completion_status"]}


## IEDB

### IEDB-1 (lookup, stable)
**Q:** What is the IEDB epitope ID for the linear peptide SIINFEKL?  
**Expected answer:** 58560 (IEDB_EPITOPE:58560)  
**Check:** exact on 58560  
**Templates:** competency-answerability, persistent-identifiers, metadata-api  
**API calls:**
- `GET https://query-api.iedb.org/epitope_search?linear_sequence=eq.SIINFEKL&select=structure_id,structure_iri`

### IEDB-2 (lookup, stable)
**Q:** In IEDB, what is the source antigen of epitope SIINFEKL, and which organism does it come from?  
**Expected answer:** ovalbumin (e.g., UNIPROT:P01012.2, positions 258-265); Gallus gallus (chicken), NCBITaxon:9031  
**Check:** contains: 'ovalbumin' AND 'Gallus gallus'  
**Templates:** competency-answerability, vocabulary  
**API calls:**
- `GET https://query-api.iedb.org/epitope_search?linear_sequence=eq.SIINFEKL&select=curated_source_antigens`

### IEDB-3 (discovery, semi-stable)
**Q:** What title and version does the OpenAPI document of the Next-Generation IEDB Tools API declare, and which endpoint submits a single-tool prediction?  
**Expected answer:** 'Next-Generation IEDB Tools API', v3.0; POST /api/v1/predict  
**Check:** contains: 'v3.0' AND '/api/v1/predict'  
**Templates:** competency-answerability, openapi-discovery  
**API calls:**
- `GET https://api-nextgen-tools.iedb.org/apidocs?format=openapi` — {"note": "Swagger 2.0 (drf-yasg). /apidocs/?format=openapi with a trailing slash returns 404"}

### IEDB-4 (lookup, volatile)
**Q:** Which software release does the IEDB NG Tools API currently report?  
**Expected answer:** v5.0.4 (commit 653ded8, 2026-10-29)  
**Check:** exact on branch_or_tag  
**Templates:** competency-answerability, provenance-lineage  
**API calls:**
- `GET https://api-nextgen-tools.iedb.org/api/v1/version_info` — {"field": "version.branch_or_tag"}


## ImmPort

### IMMPORT-1 (lookup, stable)
**Q:** What is the actual enrollment of ImmPort study SDY1, and what is its ClinicalTrials.gov ID?  
**Expected answer:** 159; NCT00078195  
**Check:** numeric exact 159; contains 'NCT00078195'  
**Templates:** competency-answerability, metadata-api  
**API calls:**
- `GET https://www.immport.org/data/query/api/search/study?term=SDY1&pageSize=1` — {"fields": ["actual_enrollment", "clinicaltrials_link"]}

### IMMPORT-2 (lookup, stable)
**Q:** Who is the principal investigator of ImmPort study SDY1, and what research focus does the study have?  
**Expected answer:** Thomas Casale (Creighton University School of Medicine); Atopy/Allergy  
**Check:** contains: 'Casale' AND 'Atopy/Allergy'  
**Templates:** competency-answerability, metadata-api  
**API calls:**
- `GET https://www.immport.org/data/query/api/search/study?term=SDY1&pageSize=1` — {"fields": ["study_pi", "research_focus"]}

### IMMPORT-3 (lookup, stable)
**Q:** What ontology term does ImmPort's controlled vocabulary link to the sex value 'Female'?  
**Expected answer:** http://purl.bioontology.org/ontology/SNOMEDCT/248152002 (SNOMED CT 248152002)  
**Check:** contains: '248152002'  
**Templates:** competency-answerability, vocabulary, sssom-mappings  
**API calls:**
- `GET https://www.immport.org/data/query/api/lookup/lkSex`

### IMMPORT-4 (discovery, stable)
**Q:** Can the ImmPort Shared Data API study-summary endpoint be used without authentication? Which controllers are public?  
**Expected answer:** No (HTTP 401). Only Study Search and Lookup/Controlled Vocabulary are public.  
**Check:** contains: '401' or 'no' AND 'Study Search' AND 'Lookup'  
**Templates:** competency-answerability, openapi-discovery, api-http-behavior  
**API calls:**
- `GET https://www.immport.org/data/query/v3/api-docs` — {"field": "info.description"}
- `GET https://www.immport.org/data/query/api/study/summary/SDY1` — {"expected_status": 401}


## BV-BRC

### BVBRC-1 (lookup, stable)
**Q:** What are the genome length and GC content of BV-BRC genome 511145.12 (E. coli K-12 MG1655)?  
**Expected answer:** 4639675 bp; GC 50.8%  
**Check:** numeric exact length; GC ±0.1  
**Templates:** competency-answerability, metadata-api  
**API calls:**
- `GET https://www.bv-brc.org/api/genome/?eq(genome_id,511145.12)&select(genome_id,genome_name,genome_length,gc_content)` — {"headers": {"Accept": "application/json"}}

### BVBRC-2 (lookup, stable)
**Q:** What is the assembly accession of the Mycobacterium tuberculosis H37Rv reference genome (83332.12) in BV-BRC, and how many PATRIC CDS does it have?  
**Expected answer:** GCA_000195955.2; 4367 CDS  
**Check:** exact accession; numeric exact CDS (may change on reannotation)  
**Templates:** competency-answerability, persistent-identifiers  
**API calls:**
- `GET https://www.bv-brc.org/api/genome/?eq(genome_id,83332.12)&select(assembly_accession,patric_cds,genome_status)` — {"headers": {"Accept": "application/json"}}

### BVBRC-3 (multi-step, stable)
**Q:** In BV-BRC's PATRIC annotation of M. tuberculosis H37Rv, what is the RefSeq locus tag of the katG gene, and how long is its protein?  
**Expected answer:** Rv1908c; 740 aa (minus strand, 2153889-2156111)  
**Check:** exact 'Rv1908c'; numeric 740  
**Templates:** competency-answerability, metadata-api  
**API calls:**
- `GET https://www.bv-brc.org/api/genome/?and(eq(taxon_id,83332),eq(reference_genome,Reference))&select(genome_id,genome_name)` — {"purpose": "resolve reference genome_id -> 83332.12", "headers": {"Accept": "application/json"}}
- `GET https://www.bv-brc.org/api/genome_feature/?and(eq(genome_id,83332.12),eq(gene,katG),eq(annotation,PATRIC))&select(patric_id,refseq_locus_tag,aa_length,start,end,strand)` — {"headers": {"Accept": "application/json"}}

_Note:_ A plain genome_name match is ambiguous (it returns H37Rv variants under taxon 1773). Use the reference_genome filter.

### BVBRC-4 (lookup, stable)
**Q:** According to the BV-BRC taxonomy, which genus does SARS-CoV-2 (taxon 2697049) belong to?  
**Expected answer:** Betacoronavirus (subgenus Sarbecovirus, family Coronaviridae)  
**Check:** contains: 'Betacoronavirus'  
**Templates:** competency-answerability, vocabulary  
**API calls:**
- `GET https://www.bv-brc.org/api/taxonomy/?eq(taxon_id,2697049)&select(lineage_names)` — {"headers": {"Accept": "application/json"}}


## VEuPathDB

### VEU-1 (lookup, stable)
**Q:** In PlasmoDB, what product and gene name are given for gene PF3D7_1133400?  
**Expected answer:** apical membrane antigen 1; AMA1 (protein coding gene, Plasmodium falciparum 3D7)  
**Check:** contains: 'apical membrane antigen 1'  
**Templates:** competency-answerability, metadata-api  
**API calls:**
- `POST https://plasmodb.org/site-search` — {"body": {"searchText": "PF3D7_1133400", "pagination": {"offset": 0, "numRecords": 1}, "restrictToProject": "PlasmoDB", "documentTypeFilter": {"documentType": "gene"}}}

_Note:_ The WDK record endpoints (POST /plasmo/service/record-types/gene/records and search reports) now return 'Valid API Key required'. Public site-search still works.

### VEU-2 (discovery, volatile)
**Q:** Which build number and release date does the PlasmoDB web service report?  
**Expected answer:** Build 71; 20 August 2026  
**Check:** exact on build; contains date  
**Templates:** competency-answerability, provenance-lineage, api-http-behavior  
**API calls:**
- `GET https://plasmodb.org/plasmo/service` — {"fields": ["buildNumber", "releaseDate"]}

_Note:_ Changes with each VEuPathDB release, roughly every 2-3 months.

### VEU-3 (discovery, semi-stable)
**Q:** Can an anonymous agent fetch a gene record from the PlasmoDB WDK service (POST /plasmo/service/record-types/gene/records)? What does the service return?  
**Expected answer:** No. The service returns 'Valid API Key required for this endpoint.' and points to the user profile serviceAccess page.  
**Check:** contains: 'API Key required'  
**Templates:** competency-answerability, api-http-behavior, rights-and-license  
**API calls:**
- `POST https://plasmodb.org/plasmo/service/record-types/gene/records` — {"body": {"primaryKey": [{"name": "source_id", "value": "PF3D7_1133400"}, {"name": "project_id", "value": "PlasmoDB"}], "attributes": ["product"], "tables": []}}

### VEU-4 (multi-step, stable)
**Q:** Start from the PlasmoDB service root. Is 'gene' a record type, and what is the URL segment of the gene search that finds all genes from one or more species?  
**Expected answer:** Yes; GenesByTaxonGene  
**Check:** exact 'GenesByTaxonGene'  
**Templates:** competency-answerability, openapi-discovery  
**API calls:**
- `GET https://plasmodb.org/plasmo/service/record-types`
- `GET https://plasmodb.org/plasmo/service/record-types/gene` — {"field": "searches[].urlSegment where summary='Find all genes from one or more species/organism.'"}

## Endpoints that failed or required auth

- **AccessClinicalData@NIAID**: `/mds/metadata, /index/index, /guppy, /user/_status (legacy Gen3)`: Returns the SPA HTML shell (200 text/html). There is no Gen3 API now. The public API is /api (OpenAPI at /api/openapi.json).
- **TB Portals**: `https://analytic.tbportals.niaid.nih.gov/api/{Patient-Case,Genomics,DST,...}`: HTTP 401. Bearer token required. datasharing.tbportals.niaid.nih.gov is an Angular SPA.
- **TB Portals**: `https://tbportals.niaid.nih.gov/download-data`: Redirects to / ('Found. Redirecting to /').
- **IEDB**: `https://api-nextgen-tools.iedb.org/api/openapi.json, /api/v1/openapi.json`: 200 with error JSON 'Invalid URL'. The real spec is at /apidocs?format=openapi.
- **ImmPort**: `/data/query/api/study/summary/SDY1 (and the other Study Data/Result/Manifest/DRS endpoints)`: HTTP 401. API key required.
- **VEuPathDB**: `plasmodb.org/plasmo/service/record-types/gene/records, searches/*/reports/standard`: 'Valid API Key required for this endpoint.'
- **VEuPathDB**: `plasmodb.org/common/downloads/(Current_Release|release-71)/...`: HTTP 404 (download tree not at this path). The webServices.html page is a SPA shell with requireLogin=true.

## Example competency-answerability input (YAML)

```yaml
target: https://www.bv-brc.org/
questions:
  - "What are the genome length and GC content of BV-BRC genome 511145.12 (E. coli K-12 MG1655)?"
  - "What is the assembly accession of the Mycobacterium tuberculosis H37Rv reference genome (83332.12) in BV-BRC, and how many PATRIC CDS does it have?"
  - "In BV-BRC's PATRIC annotation of M. tuberculosis H37Rv, what is the RefSeq locus tag of the katG gene, and how long is its protein?"
```
