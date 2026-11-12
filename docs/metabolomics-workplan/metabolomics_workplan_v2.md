# Metabolomics Workbench work plan

Changes that would move the 9 November 2026 scores for <https://www.metabolomicsworkbench.org/>. This is an example a repository team could adopt. Metabolomics Workbench has not signed off on it, and it is not a certification.

Evidence is the Pi run summarized in [docs/repoAssessment.md](../docs/repoAssessment.md) (Table 1) and written out as per-check YAML in the [9 November session](../logs/traces/pi-session-2026-11-09T20-13-18-921Z_01a1c1f1-9ac9-70e4-ae1e-5f6bafdd6810.html). Question examples come from the external set in [metabolomics-workbench-competency-questions-final.md](../compQuestions/metabolomics/metabolomics-workbench-competency-questions-final.md). The shape of each action follows the 6 November 2026 deck [slideDeckSIReadyRepos.pdf](../docs/Webinar_Nov_2026/slideDeckSIReadyRepos.pdf): be reachable, be readable, be callable, be meaningful, then evaluate.

LibreChat cells marked `not-observable` are limits of that client. They are not site findings. On the eight checks both runs could score, they agree except `agent-documentation` (Pi `present`, LibreChat `partial`) and `openapi-discovery` (Pi `absent`, LibreChat `partial`). This plan follows the Pi evidence, which recorded status, headers, and the raw body.

Sample record: study [ST000001](https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&StudyID=ST000001&StudyType=MS&ResultType=1).

## Leave in place

- The homepage and the ST000001 page both return HTTP 200 HTML to an ordinary GET (`reachable-fetch`: present).
- REST help at [/tools/mw_rest.php](https://www.metabolomicsworkbench.org/tools/mw_rest.php) is linked from the homepage and states the study-summary URL in the first HTML (`agent-documentation`: present). Keep that HTML page and the PDF.
- `GET /rest/study/study_id/ST000001/summary` already returns the study title, species, and license in JSON. The partial `metadata-api` score is the missing `@context`, not a missing endpoint.
- The study page already puts the title, the description, and accession ST000001 in the first HTML, with schema.org `Dataset` microdata. The partial `server-rendered-content` score is the missing license.
- [RefMet](https://www.metabolomicsworkbench.org/databases/refmet/index.php) is a public nomenclature page linked from the homepage (`vocabulary`: partial).
- Project DOI `10.21228/M8159B` is on the study page as the DOI for project PR000001 (`persistent-identifiers`: partial).

## Do these

### 1. Rewrite robots.txt by visitor class

**Gap.** `robots-policy` is partial. The file is 26 bytes: `User-agent: *` and `Disallow: /`. It names no sitemap and no content-use preference. That one group covers search indexers, user-triggered fetchers, and trainer crawlers together.

**Action.** A person who sets crawl policy decides which of those three classes may read public pages, then writes a named `User-agent` group for each class that should differ. Keep a `User-agent: *` group for everyone else. The deck treats that split as the reachable signal, and a copy-ready pattern is in [assets/robots.txt](../docs/Webinar_Nov_2026/assets/robots.txt). When load requires it, answer with HTTP 429 and `Retry-After`. The 9 November client was not rate-limited, so 429 is a host practice to have ready.

**Recheck.** `evals/robots-policy.md` on the origin.

### 2. Publish a sitemap of public study URLs

**Gap.** `sitemap` is absent. `/sitemap.xml` and `/sitemap_index.xml` returned HTTP 404, and `robots.txt` has no `Sitemap:` line.

**Action.** After the crawl decision, publish a sitemap or a sitemap index of the study URLs that policy allows, with a real `lastmod`. Point at it with an absolute `Sitemap:` line in `robots.txt`. The deck separates the two files: `robots.txt` is the permission, the sitemap is the inventory. Example: [assets/sitemap.xml](../docs/Webinar_Nov_2026/assets/sitemap.xml).

**Recheck.** `evals/sitemap.md`.

### 3. Put the study license in the first HTML

**Gap.** `server-rendered-content` is partial. Title, description, and ST000001 are in the raw HTML. The license string is absent there. The summary JSON already returns `CC BY-NC-ND` and `https://creativecommons.org/licenses/by-nc-nd/4.0/deed.en` (external question MW-2). The page link “Terms of Use” was not scored as this study’s license.

**Action.** Print that same license on the study template, in the HTML the server sends. Add FAIR Signposting `Link` headers for `license` and `cite-as` (the project DOI). The deck’s rights section asks for the license on the record so a fetch keeps it with the text.

**Recheck.** `evals/server-rendered-content.md` on ST000001.

### 4. Add one Dataset JSON-LD block, and name the profile

**Gap.** `dataset-jsonld` and `metadata-profile` are absent. The page has schema.org microdata and no `application/ld+json` script, so `validate_dataset` was skipped. Nothing on the page declares `conformsTo`.

**Action.** Embed one server-rendered JSON-LD `Dataset` on the study page. Use the title, description, accession, project DOI, and the license already in the summary JSON (SPDX `CC-BY-NC-ND-4.0` plus the HTTPS license URL). Set `conformsTo` to the profile the repository actually follows. The deck points at Bioschemas Dataset and the NIAID Data Ecosystem schema for life-science records. Keep the existing microdata in agreement with the JSON-LD.

**Recheck.** `evals/dataset-jsonld.md` and `evals/metadata-profile.md`. Pass the JSON-LD block to `validate_dataset` as a starter check for name, description, and URL.

### 5. Publish an OpenAPI document for the API you already run

**Gap.** `openapi-discovery` is absent. The REST page and `MWRestAPIv1.2.pdf` describe the calls in prose. The check found no OpenAPI or Swagger document to parse, so the Section 3 rubric stayed at low confidence.

**Action.** Publish an OpenAPI 3 document at a stable URL for the metadata reads the help page already documents: study summary, RefMet name and match, compound by regno, and the moverz examples. Link that URL from `/tools/mw_rest.php`. The deck treats a documented API with ordinary HTTP as the callable baseline, and treats a remote MCP server as optional once that document exists.

**Recheck.** `evals/openapi-discovery.md`, then the `niaid-bp-api-assess` checklist on the spec.

### 6. Make successful REST reads ordinary HTTP

**Gap.** `metadata-api` and `api-http-behavior` are partial. In the Pi run the ST000001 summary GET was HTTP 200 `application/json`, with the study id in the path, and the body had no `@context` or `@type`. That response had no `ETag`, `Last-Modified`, or `Cache-Control`. The external question set, checked the same day, records a second behavior on the same family of URLs: HEAD, and a GET that omits `Accept: application/json`, can return HTTP 406 while the body still holds the fields. `moverz` can answer HTTP 302 and then `Content-Type: text/html` for line-oriented or tab-separated text (MW-5, MW-7, MW-8, MW-9). The lipid `/txt` table wrote matched m/z and delta as one field (`513.4495.0005`).

**Action.** Return HTTP 200 for a successful metadata read, with a `Content-Type` that matches the bytes, for GET and for HEAD, including when the client sends no `Accept` header. Add `ETag` or `Last-Modified`, and `Cache-Control`, on the stable summary URL. Serve `@context` and `@type` on that summary, reusing the JSON-LD from action 4, or a `Link: rel="describedby"` to the study page that holds it. Give moverz tables a text content type and a separator between m/z and delta.

**Recheck.** `evals/metadata-api.md` and `evals/api-http-behavior.md` on the summary GET. Grade MW-1, MW-2, and MW-5 from the response body.

### 7. Attach ORCID and ROR to names already on the record

**Gap.** `persistent-identifiers` is partial. ST000001 and DOI `10.21228/M8159B` are on the page, with resolver URL `https://dx.doi.org/10.21228/M8159B`. Tobias Kind and University of California, Davis are named, and the HTML has no `https://orcid.org/` or `https://ror.org/` IRI.

**Action.** Keep `10.21228/M8159B` as the project DOI for PR000001. Add ORCID and ROR IRIs beside the people and organizations the study page already names. The deck uses those IRIs so an agent can cite a person and an organization the same way it cites the DOI. A study-level PID for ST000001 can follow. The accession already identifies the study inside the repository.

**Recheck.** `evals/persistent-identifiers.md` on ST000001.

### 8. Publish the questions this repository answers

**Gap.** `competency-questions` is absent. The homepage and the REST page do not link a question list. Example request labels on the REST page were not scored as questions. The external file is a test set written outside the repository. The site has not published it, so the 9 November run stopped before answerability.

**Action.** Publish a short list the repository stands behind, at a stable URL, and link it from the REST help page. A domain editor should accept or rewrite each line before it goes up. The stable external questions are a draft to start from, because each one already resolves with a public GET: study title and species (MW-1), license (MW-2), RefMet identifiers for a named metabolite (MW-3), synonym match (MW-4), and compound name by regno (MW-11). The deck’s evaluation step is to hand an agent the API docs and see which of those questions it can answer from the live site. After the list is public, run `evals/competency-answerability.md` on up to three of them, and keep the answer key with the grader.

**Recheck.** `evals/competency-questions.md`, then one answerability run.

### 9. Link RefMet to the identifiers it already stores

**Gap.** `vocabulary` is partial. RefMet is readable and describes itself as a reference nomenclature. The study page, the REST page, and the RefMet page do not link an ontology IRI. RefMet records already carry outside identifiers. MW-3 shows that for Cholesterol: PubChem CID 5997, InChIKey `HVYWMOMLDIMFJA-DPAQBDIFSA-N`, RefMet ID RM0135639.

**Action.** From the RefMet page and from a RefMet JSON record, link each stored outside identifier as a URL (PubChem, and any ChEBI or LIPID MAPS id the record holds). A table of “our name, their id, relation” is enough for this pass. An SSSOM file can wrap that table later.

**Recheck.** `evals/vocabulary.md`.

## Later

These checks were absent. The deck marks them optional or later. Leaving them for a second pass leaves actions 1–9 intact.

- `llms.txt` returned HTTP 404, and the study page answered `Accept: text/markdown` with HTML (`llms-txt`, `markdown-negotiation`). A small `llms.txt` plus a Markdown alternate of the study page matches the deck’s readable pattern ([assets/llms.txt](../docs/Webinar_Nov_2026/assets/llms.txt)). The deck also says clean first-HTML covers much of that need, which actions 3 and 4 already do.
- Bulk export is absent. Study pages already offer mwTab text, mwTab JSON, and a named-metabolite download. A repository-wide dump is a separate product choice.
- No remote MCP server is advertised (`mcp-exposure`: absent). The deck says OpenAPI carries the callable work, and that an MCP server is a larger security surface. Add one with a security review, and publish `/.well-known/mcp.json` if you do.
- SHACL shapes and SSSOM mappings are absent. Publish them after the JSON-LD profile and the RefMet crosswalk exist.
- `SKILL.md` and `ard.json` are the deck’s bleeding-edge packaging. The 19 checks did not require them.

## Recheck

Rerun the same 19 checks against this origin and ST000001, with a client that returns the status line, the headers, and the raw body. Keep a verdict on each check. The deck asks for a baseline and a later measurement, kept as separate results.
