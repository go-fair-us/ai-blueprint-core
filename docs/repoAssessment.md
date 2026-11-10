# Evaluation of Comparison Workflows

## Overview

This section provides an overview of the evaluation comparison for the resource at
 https://www.metabolomicsworkbench.org/.   These results are seen in the following tables.  The two runs where done by different approaches.   The first leveraged a Command Line Interface (CLI) harness based on [Pi](https://pi.dev/).  The other was a web UI leveraging the [Librechat](https://www.librechat.ai/) framework.  

## Summary of Table Differences

Comparing verdicts by evaluation, 6 of 8 observable evaluations agree. The two disagreements are:

- **agent-documentation:** first table `present`; second table `partial`.
- **openapi-discovery:** first table `absent`; second table `partial`.

The remaining 11 evaluations were excluded because at least one verdict is `not-observable`.

Verdict markers: 🟢 present, 🟡 partial, 🔴 absent, ⚪ not-observable.

### Table 1.  Pi Harness + MCP + Prompt templates + Skills

Run using Pi harness at bin/pi in this repo and leveraging the MCP server from bp_mcp.  It also has a 
set of prompt templates.  However, these are also exposed by the MCP server, so this should not be a 
major difference to the following Librechat run.  

However, one significant difference is the Pu harness access to the NIAID skills developed and part of this repo.
A test of Librechat, once configured to access the skills, would be an interesting comparison.  

> NOTE:  The prompt does say to use the MCP server resources only, but a review of the Pi traces indicates it did scope the skills into its approach.


| # | property | evaluation | verdict | evidence_url |
| --- | --- | --- | --- | --- |
| 1 | Be reachable | reachable-fetch | 🟢 present | https://www.metabolomicsworkbench.org/ |
| 2 | Be reachable | robots-policy | 🟡 partial | https://www.metabolomicsworkbench.org/robots.txt |
| 3 | Be readable | llms-txt | 🔴 absent | https://www.metabolomicsworkbench.org/llms.txt |
| 4 | Be readable | sitemap | 🔴 absent | https://www.metabolomicsworkbench.org/sitemap.xml |
| 5 | readable | server-rendered-content | 🟡 partial | https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&StudyID=ST000001&StudyType=MS&ResultType=1 |
| 6 | readable | markdown-negotiation | 🔴 absent | https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&StudyID=ST000001&StudyType=MS&ResultType=1 |
| 7 | Be readable | bulk-export | 🔴 absent | https://www.metabolomicsworkbench.org/ |
| 8 | Be readable | agent-documentation | 🟢 present | https://www.metabolomicsworkbench.org/tools/mw_rest.php |
| 9 | Be callable | openapi-discovery | 🔴 absent | https://www.metabolomicsworkbench.org/tools/mw_rest.php |
| 10 | Be callable | metadata-api | 🟡 partial | https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/summary |
| 11 | Be callable | api-http-behavior | 🟡 partial | https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/summary |
| 12 | Be callable | mcp-exposure | 🔴 absent | https://www.metabolomicsworkbench.org/tools/mw_rest.php |
| 13 | meaningful | dataset-jsonld | 🔴 absent | https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&StudyID=ST000001&StudyType=MS&ResultType=1 |
| 14 | Be meaningful | persistent-identifiers | 🟡 partial | https://dx.doi.org/10.21228/M8159B |
| 15 | Be meaningful | vocabulary | 🟡 partial | https://www.metabolomicsworkbench.org/databases/refmet/index.php |
| 16 | meaningful | metadata-profile | 🔴 absent | https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&StudyID=ST000001&StudyType=MS&ResultType=1 |
| 17 | Be meaningful | shacl-shapes | 🔴 absent | https://www.metabolomicsworkbench.org/tools/mw_rest.php |
| 18 | Be meaningful | sssom-mappings | 🔴 absent | https://www.metabolomicsworkbench.org/tools/mw_rest.php |
| 19 | Be meaningful | competency-questions | 🔴 absent | https://www.metabolomicsworkbench.org/ |


### Table 2.  LibreChat UI plus MCP

Run using a LibreChat UI also connected to the MCP server from bp_mcp.  In contrast to the Pi harness above, this 
LibreChat UI did not have access to the various skills from the repository.  It should be noted that it can use skills, 
but they were not configured for this run.   

**Default provider:** the custom endpoint named **NRP** (`https://ellm.nrp-nautilus.io/v1`).

**Default model:** **`deepseek-v4-flash`**.

That comes from `librechat.yaml` `modelSpecs`. `Blueprint (NRP)` is marked `softDefault: true` and its preset is `endpoint: "NRP"`, `model: "deepseek-v4-flash"`. The NRP endpoint’s `models.default` list starts with the same model. The other spec, `Blueprint (OpenRouter)` / `stealth/ox-alpha`, is not the default.


| # | Property | Evaluation | Verdict | Evidence URL |
| --- | --- | --- | --- | --- |
| 1 | Be reachable | reachable-fetch | ⚪ not-observable | https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&StudyID=ST000001&StudyType=MS&ResultType=1 |
| 2 | Be reachable | robots-policy | ⚪ not-observable | https://www.metabolomicsworkbench.org/robots.txt (not fetched) |
| 3 | Be readable | llms-txt | ⚪ not-observable | https://www.metabolomicsworkbench.org/llms.txt (not fetched) |
| 4 | Be readable | sitemap | ⚪ not-observable | https://www.metabolomicsworkbench.org/sitemap.xml (not fetched) |
| 5 | Be readable | server-rendered-content | 🟡 partial | https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&StudyID=ST000001&StudyType=MS&ResultType=1 |
| 6 | Be readable | markdown-negotiation | ⚪ not-observable | https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&StudyID=ST000001&StudyType=MS&ResultType=1 |
| 7 | Be readable | bulk-export | ⚪ not-observable | https://www.metabolomicsworkbench.org/ (not fetched) |
| 8 | Be readable | agent-documentation | 🟡 partial | https://www.metabolomicsworkbench.org/tools/mw_rest.php |
| 9 | Be callable | openapi-discovery | 🟡 partial | https://www.metabolomicsworkbench.org/tools/mw_rest.php |
| 10 | Be callable | metadata-api | 🟡 partial | https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/summary |
| 11 | Be callable | api-http-behavior | ⚪ not-observable | https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/summary |
| 12 | Be callable | mcp-exposure | ⚪ not-observable | https://www.metabolomicsworkbench.org/tools/mw_rest.php |
| 13 | Be meaningful | dataset-jsonld | ⚪ not-observable | https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&StudyID=ST000001&StudyType=MS&ResultType=1 |
| 14 | Be meaningful | persistent-identifiers | 🟡 partial | https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/summary |
| 15 | Be meaningful | vocabulary | 🟡 partial | https://www.metabolomicsworkbench.org/tools/mw_rest.php |
| 16 | Be meaningful | metadata-profile | ⚪ not-observable | https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/summary |
| 17 | Be meaningful | shacl-shapes | 🔴 absent | https://www.metabolomicsworkbench.org/tools/mw_rest.php |
| 18 | Be meaningful | sssom-mappings | 🔴 absent | https://www.metabolomicsworkbench.org/tools/mw_rest.php |
| 19 | Be meaningful | competency-questions | ⚪ not-observable | https://www.metabolomicsworkbench.org/tools/mw_rest.php |



# Assessment prompt

Paste-ready prompt for a chat UI that has the Blueprint MCP server from `mcp_bp` connected. It scores `https://www.metabolomicsworkbench.org/` on the November 2026 webinar properties: Be reachable, Be readable, Be callable, and Be meaningful.

The connected Blueprint MCP server is the rubric library for this check. It is not the site under test, and it does not crawl Metabolomics Workbench.

## What to ask it to do

Score `https://www.metabolomicsworkbench.org/` on the webinar’s four properties, one check at a time, with evidence from responses it actually received:

| Property | What the webinar is asking | Load these files with `read_prompt_file` |
|---|---|---|
| Be reachable | A normal GET succeeds, and `robots.txt` states crawl and content-use rules | `evals/reachable-fetch.md`, `evals/robots-policy.md` |
| Be readable | A sitemap, `llms.txt`, server-rendered record text, Markdown, bulk export, and followable docs | `evals/llms-txt.md`, `evals/sitemap.md`, `evals/server-rendered-content.md`, `evals/markdown-negotiation.md`, `evals/bulk-export.md`, `evals/agent-documentation.md` |
| Be callable | An OpenAPI document, one JSON-LD metadata GET, ordinary HTTP headers, and an optional remote MCP advertisement on the site | `evals/openapi-discovery.md`, `evals/metadata-api.md`, `evals/api-http-behavior.md`, `evals/mcp-exposure.md` |
| Be meaningful | schema.org `Dataset` JSON-LD, persistent identifiers, a vocabulary, a declared profile, SHACL, SSSOM, and competency questions the site itself published | `evals/dataset-jsonld.md`, `evals/persistent-identifiers.md`, `evals/vocabulary.md`, `evals/metadata-profile.md`, `evals/shacl-shapes.md`, `evals/sssom-mappings.md`, `evals/competency-questions.md` |

Rights, citation, and lineage sit beside those four in the same catalog (`evals/rights-and-license.md`, `evals/citation.md`, `evals/provenance-lineage.md`). The prompt below leaves them for a second pass so this run stays on the four properties.

Two MCP roles stay separate. The server in `mcp_bp` (tools such as `read_prompt_file`, `read_skill`, `get_blueprint_section`, `validate_dataset`) supplies the procedures. Whether Metabolomics Workbench advertises its own remote MCP server is only the `mcp-exposure` check, and that server is optional.

The deterministic checkers `niaid-bp-robots`, `niaid-bp-sitemap`, and `niaid-bp-llms` are skill procedures. `validate_dataset` is the one skill script the MCP server runs itself. `niaid-bp-api-assess` scores Blueprint Section 3 after an OpenAPI document is found. `openapi-discovery` only finds that document. The registered prompts `fair_crawl_assessor` and `fair_assessment_interview` are a different instrument. They score the five Blueprint areas. They are not this webinar pass.

An October 2026 note already exists at `prompts/api_examples/MW_REST_API_NIAID_Blueprint_Compatibility.md`. The prompt tells the model to re-check every claim against a live response.

A chat that only has a page summarizer should still return the report. Most header and JSON-LD checks will be `not-observable`, and that is a property of the client. A client that can return status, headers, and the raw body can fill the same checks.

This run stops before competency answerability. That check is `evals/competency-answerability.md`, and it needs questions the site published. The answer keys under `../compQuestions` stay out of the prompt.

## Prompt

```text
You are evaluating one public data repository for agent access, using the
procedures in the connected NIAID Blueprint knowledge server. Do not invent
pages, headers, status codes, or JSON-LD.

Target
- Repository origin: https://www.metabolomicsworkbench.org/
- Record page to confirm, then use: https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&StudyID=ST000001&StudyType=MS&ResultType=1
- API docs page: https://www.metabolomicsworkbench.org/tools/mw_rest.php
- One metadata GET to try after you have read evals/metadata-api.md: https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/summary
- If the record page is not HTTP 2xx, discover one public study from the homepage, robots.txt, llms.txt, or the sitemap. Say how you found it. Use study id ST000001 only. Do not invent other ids.

Question
Apply the November 2026 webinar properties Be reachable, Be readable, Be callable, and Be meaningful. The working definitions and the exact checks are in the knowledge server. Load them before you fetch the site.

Use the Blueprint MCP server only as the source of procedures
Call these tools, in this order, before the first request to the target:
1. kb_stats, so you know this server is the Blueprint corpus.
2. read_doc path "evalPrompts.md". That catalog is the index. Obey its verdict labels, client check, and the rule that each file scores only its own question.
3. read_doc path "Webinar_Nov_2026/glossary.md" only if a term in a check is unclear. Use the Being reachable, Being readable, Being callable, and Being meaningful sections.
4. For each check below, read_prompt_file on that eval path immediately before you score it. Follow that file's pass conditions. Keep its check ids.
5. read_prompt_file path "api_examples/MW_REST_API_NIAID_Blueprint_Compatibility.md" only as prior notes from October 2026. Re-test every claim against a response you receive in this run. A block recorded there is not today's verdict.
6. When you score the API, read_skill "niaid-bp-api-assess" and read_skill_file "niaid-bp-api-assess" "references/api-checklist.md". Also get_blueprint_section "3" and get_okf_requirements pillar "api".
7. If you can run a local command, also read_skill and run the script for niaid-bp-robots, niaid-bp-sitemap, and niaid-bp-llms against the origin. Attach their JSON. If you cannot run the script, follow the matching eval file with your HTTP client and say the script did not run.
8. If a server-rendered schema.org Dataset JSON-LD block is in the record HTML, pass that graph text to validate_dataset. If there is no such block, skip the tool.

Leave the registered prompts fair_crawl_assessor, fair_web_assessor, fair_assessment_interview, and fair_self_assessment unused. Leave niaid-bp-fair-assess, niaid-bp-dataset-intake, niaid-bp-citation, niaid-bp-teach, and niaid-bp-model-influence unloaded. Those are interviews or a whole-Blueprint score.

Checks, in order
Be reachable: evals/reachable-fetch.md, evals/robots-policy.md
Be readable: evals/llms-txt.md, evals/sitemap.md, evals/server-rendered-content.md, evals/markdown-negotiation.md, evals/bulk-export.md, evals/agent-documentation.md
Be callable: evals/openapi-discovery.md, then evals/metadata-api.md, then evals/api-http-behavior.md on the same GET, then evals/mcp-exposure.md
Be meaningful: evals/dataset-jsonld.md, evals/persistent-identifiers.md, evals/vocabulary.md, evals/metadata-profile.md, evals/shacl-shapes.md, evals/sssom-mappings.md, evals/competency-questions.md

For Be callable, openapi-discovery only locates a spec. If you find an OpenAPI or Swagger document, score it with the api-assess checklist. If the REST page has no spec, say so, set confidence to low, and keep undeclared facts as not stated. A remote MCP server on this host is optional. Missing one is a finding. Do not call any MCP tool on metabolomicsworkbench.org. The Blueprint server you already used is not that advertisement.

HTTP rules
Name your client before the first fetch. Say whether it returns the status code, the response headers, and the unmodified body. A tool that summarizes HTML or returns extracted text cannot support script, meta, link, or header checks. Mark those checks not-observable and write "client cannot see ..." in evidence. inspect_url on the Blueprint server is an extract. It is not a raw HTTP client. Prefer a client that can send curl -i style requests. Send Accept: text/markdown only for the markdown-negotiation check.

Fetch each URL once and reuse that body across checks. Stay on www.metabolomicsworkbench.org and an obvious API or docs host the site itself uses. Send no credentials and no cookies. Do not load-test. On HTTP 429, copy Retry-After into the evidence and stop. Combined cap: homepage, robots.txt, one llms.txt, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, one API docs or OpenAPI document, and one Markdown probe of the record. One render of a URL is allowed only when the eval file you just read allows it. Count it in fetches.

Report
Return one Markdown report. Do not collapse the checks into a single score. For each of the four properties, give one short paragraph of what a repository operator should do next, then the YAML from each eval you ran. Each YAML keeps evaluation, target, verdict, evaluated_at, client, checks, and fetches. verdict is one of present, partial, absent, blocked, or not-observable, as that file defines it. Quote the URL, status, header, or a short passage for every evidence line. End with a table: property, evaluation name, verdict, one evidence URL. List the Blueprint MCP tools you called.
```
