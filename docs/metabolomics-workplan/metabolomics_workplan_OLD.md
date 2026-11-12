# Example work plan: Metabolomics Workbench

This is an **example** of how a repository team could turn the November 2026 webinar [checklist](https://github.com/go-fair-us/ai-blueprint-core/blob/116743c1caaaa92d6574643251240598f04d771e/docs/checklist/checklist.md) (merged in [PR #4](https://github.com/go-fair-us/ai-blueprint-core/pull/4), commit `116743c`) into a short work plan. It is not a commitment by Metabolomics Workbench, not a certification, and not a filled Blueprint interview from [`workPlanSpec.md`](https://github.com/go-fair-us/ai-blueprint-core/blob/116743c1caaaa92d6574643251240598f04d771e/prompts/workPlanSpec.md)—that still needs an operator.

**Target:** [https://www.metabolomicsworkbench.org/](https://www.metabolomicsworkbench.org/)  
**Sample record:** study [ST000001](https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&StudyID=ST000001&StudyType=MS&ResultType=1)  
**Baseline evidence:** the [repo assessment](https://github.com/go-fair-us/ai-blueprint-core/blob/116743c1caaaa92d6574643251240598f04d771e/docs/repoAssessment.md) tables, using the Pi run for fetches it actually made, plus Fact Checker confirmation of the ST000001 HTML, REST JSON, `robots.txt` body, and summary GET. LibreChat `not-observable` cells are client limits, not site findings.

Checklist IDs and levels below come from the merged checklist on `116743c`. Levels describe access and maintenance, not quality.

## What to keep

These already work and should not be replaced:

| Finding | Why it matters |
| --- | --- |
| Homepage GET succeeded | The site is reachable for a normal fetch. |
| A `robots.txt` already exists at the site root | RCH-02 is not “publish a new file.” The work is to review the policy in that file. |
| Followable REST documentation at [`mw_rest.php`](https://www.metabolomicsworkbench.org/tools/mw_rest.php) (HTML and PDF) | Agents already have API docs. Those pages can stay. No OpenAPI or Swagger document was found to quote. |
| `GET /rest/study/study_id/ST000001/summary` returns useful plain JSON | There is already a public metadata API. |
| Title, description, and ST000001’s identifier are in the first HTML | Do not treat those fields as open work. |
| The study page already has schema.org `Dataset` **microdata** | The markup gap is the JSON-LD format, not a missing Dataset description. |
| License `CC BY-NC-ND` is in the REST JSON | The license is known; it is missing from the study HTML and from JSON-LD. |
| [RefMet](https://www.metabolomicsworkbench.org/databases/refmet/index.php) exists at a stable URL | Vocabulary work starts from this, rather than from a blank slate. |
| DOI `10.21228/M8159B` is the **project** DOI for PR000001 | Keep it, and do not describe it as a study-level DOI for ST000001. |

## Do first — confirmed gaps

### 1. Review the crawl policy — RCH-03 (review RCH-02) (Level 1)

**Evidence:** a `robots.txt` already exists. The body is `User-agent: *` / `Disallow: /`. A `Sitemap:` line is not the fix and would only change the robots-policy verdict.

**Action:** A person who can set crawl policy should decide whether that site-wide ban is intentional. If it is not, write `Allow`/`Disallow` prefixes for the visitor classes they actually want (RCH-03). An agent should not choose that policy. Treat the file as a preference for cooperating clients, not as access control.

**Owner:** a person who can set crawl policy  
**Verify:** `GET https://www.metabolomicsworkbench.org/robots.txt` and rerun `evals/robots-policy.md`, pinned to `116743c`.

### 2. Put the license in the first HTML — RD-02, and the landing-page half of MEA-04 (Level 2)

**Evidence:** title, description, and identifier are already in the first HTML. The license `CC BY-NC-ND` is in the REST JSON, not in that HTML. Server-rendered study content was `partial` for that reason.

**Action:** Add the license to the server-rendered study template. Do not make in-browser rendering the only copy of it.

**Owner:** web / templates, with a metadata steward confirming the license text  
**Verify:** `curl` the ST000001 page with no JavaScript and rerun `evals/server-rendered-content.md`.

### 3. Return HTTP 200 for a successful summary GET — CAL-02 (Level 3)

**Evidence:** the existing summary GET returns useful plain JSON with HTTP 406, not JSON-LD.

**Action:** Keep the public metadata URL and the useful JSON. Return HTTP 200 for that successful retrieval, with a `Content-Type` that matches the body.

**Owner:** API team  
**Verify:** rerun `evals/metadata-api.md` and `evals/api-http-behavior.md` on the same ST000001 summary GET.

### 4. Add a Dataset JSON-LD block, including the license — CAL-03, MEA-04 (Level 2)

**Evidence:** the page already has schema.org Dataset microdata, but not a JSON-LD script. CAL-03 asks for a JSON-LD block that includes identifier, name, and license (or a clear access condition).

**Action:** Embed a server-rendered `schema.org` `Dataset` JSON-LD block on the study page. Include the existing identifier and name, plus the license (preferably an SPDX identifier and HTTPS license URL). Keep it aligned with the visible HTML and the existing microdata. If the API is the machine interface, also offer `application/ld+json`.

**Owner:** web / templates; API team if offering JSON-LD from the API  
**Verify:** view source and rerun `evals/dataset-jsonld.md`. Confirm the JSON-LD includes identifier, name, and the license. `validate_dataset` is only a starter shape (name, description, and URL); a pass there does not by itself complete CAL-03.

### 5. Publish an OpenAPI description of the existing API — CAL-01 (Level 1 if documenting an API you already run)

**Evidence:** no OpenAPI or Swagger document was found to quote. The HTML/PDF docs at `mw_rest.php` can stay.

**Action:** Publish an OpenAPI 3.x (or Swagger 2.0) document at a stable URL that describes the metadata operations you already offer, including the study summary GET, with summaries, parameters, and examples. Link it from `mw_rest.php`.

**Owner:** API team  
**Verify:** fetch the document and confirm it parses as OpenAPI or Swagger; rerun `evals/openapi-discovery.md`, then the `niaid-bp-api-assess` checklist.

### 6. Publish a sitemap of public record URLs — RD-01 (Level 1)

**Evidence:** no sitemap was found at the usual URL in the Pi run.

**Action:** Publish a sitemap (or sitemap index) of public study and record URLs, and advertise it with an absolute, file-wide `Sitemap:` line in `robots.txt`. Do this separately from the RCH-03 policy review. If `Disallow: /` remains the policy, do not list those URLs in the sitemap; the checklist says to omit URLs that `robots.txt` disallows. The webinar assets include an [example sitemap](https://github.com/go-fair-us/ai-blueprint-core/blob/116743c1caaaa92d6574643251240598f04d771e/docs/Webinar_Nov_2026/assets/sitemap.xml).

**Owner:** site / operations  
**Verify:** rerun `evals/sitemap.md` (or the `niaid-bp-sitemap` script). Confirm listed URLs respond and that disallowed paths are omitted.

## Tighten what is already partial

| ID | Action | Notes |
| --- | --- | --- |
| MEA-01 | Keep the project DOI; consider a study-level PID | Keep `10.21228/M8159B` as the project DOI for PR000001. Consider a study-level persistent identifier as a resolver IRI for ST000001, and ORCID/ROR IRIs for the people and organizations already named on the record. |
| MEA-02 | Add clearer links to RefMet and related terms | RefMet is already at a stable URL. Link it more clearly from the record or API docs, and from any ontology terms you already use. |
| MEA-04 | Landing-page half is covered by Wave 1 | Adding the license to the HTML and JSON-LD covers the landing-page side of this item. The license is already in the API JSON. This pass did not review citation (MEA-05) or lineage (MEA-06). |

## Leave for later

Skipping these is not a failure, and some were simply not observed:

- RD-03 Markdown alternates; RD-05 `llms.txt`; RD-06 a `SKILL.md`
- CAL-04 remote MCP (a missing MCP server is a finding, not a failure)
- MEA-03 (`conformsTo` profile), MEA-08 SHACL, MEA-10 SSSOM
- Published competency questions
- RCH-01, RCH-04, and RCH-05 (host/WAF treatment, HTTP 429/`Retry-After`, and logs) were not observed in the recorded tables, so they are not assigned here

A later answerability test can use a few operator-supplied questions even if the site does not yet publish a question list. Keep any answer key out of the agent prompt. Score whether a fetched passage supports the reply. That is separate from the published-list check and from scientific accuracy.

## How to track progress (EVL-01, EVL-02)

1. Track status in the full merged [checklist](https://github.com/go-fair-us/ai-blueprint-core/blob/116743c1caaaa92d6574643251240598f04d771e/docs/checklist/checklist.md). Do not use only the [Level 1](https://github.com/go-fair-us/ai-blueprint-core/blob/116743c1caaaa92d6574643251240598f04d771e/docs/checklist/dist/checklist-level-1.pdf) or [Levels 1–2](https://github.com/go-fair-us/ai-blueprint-core/blob/116743c1caaaa92d6574643251240598f04d771e/docs/checklist/dist/checklist-through-level-2.pdf) handouts: CAL-01 and CAL-02 are catalogued as Level 3, so they drop out of those views even though they are in the first wave.
2. After a few of the first items, rerun the same eval prompts against the same sample record, with a client that returns status, headers, and the raw body. Pin the recheck to `116743c`. Attach the per-check YAML (and script output for robots, sitemap, and `llms.txt` if used).
3. Keep access and readability checks, answerability tests, and accuracy reviews in separate columns. Do not collapse them into one score.
4. If using the [AI review companion](https://github.com/go-fair-us/ai-blueprint-core/blob/116743c1caaaa92d6574643251240598f04d771e/docs/checklist/ai-review.md), start with one ID in an ordinary chat (the companion’s default is RD-01), then open a new chat for the next ID.

A LibreChat rerun with skills and a raw HTTP client is a method improvement for the audit, not work the repository has to do before the first items can start.
