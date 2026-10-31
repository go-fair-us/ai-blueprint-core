# Evaluation Prompt Templates

Single-question prompts for a public data-repository website. The questions come from the Phase III webinar "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026), in `docs/Phase III NIAID Slides 11_6.pdf`.

The talk describes what a repository can expose to an agent. The four themes are reachable, readable, callable, and meaningful. Three further concerns are rights, attribution, and lineage, because a scrape can drop all three. The talk's evaluation slide adds one more step: run your own competency questions against an agent. Each file in this folder answers one of those questions.

Paste one file and give the model a repository origin URL. Add a dataset, study, or record URL when you have one. The prompt stops at its own question.

## How this folder fits

`prompts/fairAssessorCrawl.md` crawls a site and scores the whole NIAID Blueprint. These prompts do not.

`niaid-bp-api-assess` scores an OpenAPI or Swagger document against Blueprint Section 3. `openapi-discovery.md` only finds that document. Hand the URL it returns to the skill for the Section 3 rubric.

These files are ordinary Markdown under `prompts/`. The MCP server lists them with `list_prompt_files`, reads them with `read_prompt_file`, and searches them with `search_docs` (`collection="prompts"`). They are not entries in `mcp_bp/prompts_registry.py`.

## Shared report

Every prompt asks for the same YAML shape. Besides `verdict` and `checks`, each report records `evaluated_at`, the `client` and User-Agent used, and a `fetches` list of every request with its status. Sites change, so a dated report with its request log is what makes two runs comparable. `verdict` is one of:

| Verdict | When to use it |
|---|---|
| `present` | Every check this prompt requires for a pass is `pass`. |
| `partial` | The site was readable, and the checks are mixed. |
| `absent` | The artifact or behavior is missing. |
| `blocked` | The response was a challenge, HTTP 401 or 403, or an access wall. A block stays a block. |
| `not-observable` | A record, example, or document this question needs was not found. The report says what was tried. |

`robots-policy.md` reports Allow and Disallow as observations. Permission for a trainer crawler is not a passing grade.

Fetch budget, repeated in each file: stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Do not load-test or retry in a loop. Caps: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. Prefer the raw HTTP body. `competency-answerability.md` has its own cap of 5 requests per question and 15 in total.

JavaScript. These prompts do not require JavaScript. A rendered view is a second look at a URL already fetched, and only where that prompt says so. When a prompt allows a render and the client cannot render, that check is `not-observable`.

The raw response is the score for `reachable-fetch.md`, `robots-policy.md`, `sitemap.md`, `metadata-api.md`, `api-http-behavior.md`, `dataset-jsonld.md`, `rights-and-license.md`, `provenance-lineage.md`, and `metadata-profile.md`. `server-rendered-content.md` also scores the initial HTML. Its rendered fetch is a comparison and does not change the verdict.

`llms-txt.md` and `markdown-negotiation.md` read a file or response headers. They have no JavaScript rule.

These prompts fetch the raw body first, then render that same URL once when the body is an application shell or lacks the artifact: `agent-documentation.md`, `openapi-discovery.md`, `citation.md`, `persistent-identifiers.md`, `vocabulary.md`, `competency-questions.md`, `competency-answerability.md`, `bulk-export.md`, `mcp-exposure.md`, `sssom-mappings.md`, and `shacl-shapes.md`. Evidence names the view, `raw` or `rendered`. The rendered request counts in `fetches`.

Client check, also repeated in each file: many agent fetch tools convert HTML to Markdown or summarize it. That drops JSON-LD `script` blocks, `link` relations, and response headers, which many checks depend on. Each prompt asks the model to say what its client can see, and to mark a check `not-observable` rather than guess when the client cannot see the evidence. Use a client that returns raw bodies and headers (`curl -i`, or an HTTP library) for the most complete results.

## Suggested order

Run these by hand in this order when you want a full pass:

1. `reachable-fetch.md`, `robots-policy.md`
2. `llms-txt.md`, `sitemap.md`, `server-rendered-content.md`
3. `dataset-jsonld.md`, `persistent-identifiers.md`, `rights-and-license.md`, `citation.md`, `provenance-lineage.md`
4. `openapi-discovery.md`, `metadata-api.md`, `api-http-behavior.md`, `mcp-exposure.md`
5. `vocabulary.md`, `metadata-profile.md`, `shacl-shapes.md`, `sssom-mappings.md`, `competency-questions.md`
6. `competency-answerability.md`, last, because it uses the questions step 5 found and shows which of the features above an agent actually used

`bulk-export.md`, `markdown-negotiation.md`, and `agent-documentation.md` sit with the readable group whenever you need them.

## Catalog

| File | Question | Record |
|---|---|---|
| `reachable-fetch.md` | Can a non-browser GET read the homepage and one record? | Used for the second GET |
| `robots-policy.md` | What does `robots.txt` allow for search, user-driven fetch, and trainer crawlers, and does it name a sitemap? | No |
| `llms-txt.md` | Is there an `llms.txt`, and do pages point at a Markdown alternate and at that file? | Used for the link check |
| `sitemap.md` | Is there a sitemap or sitemap index that lists record URLs? | No |
| `bulk-export.md` | Is a bulk download or bulk Markdown export linked from the site? | No |
| `server-rendered-content.md` | Are title, description, identifier, and license in the initial HTML? | Yes |
| `markdown-negotiation.md` | Does the record honor `Accept: text/markdown`, or advertise a Markdown alternate? | Yes |
| `agent-documentation.md` | Are data-access or API docs linked where an agent can read them, including a `SKILL.md` when the site publishes one? | No |
| `openapi-discovery.md` | Can you find one OpenAPI or Swagger document from the public site? | No |
| `metadata-api.md` | Is there one unauthenticated resource GET that returns JSON-LD for a dataset or study? | Helps find the example |
| `api-http-behavior.md` | For that metadata GET, which status, content type, redirect, and cache headers are present? | No |
| `mcp-exposure.md` | Does the site advertise a remote MCP server? | No |
| `dataset-jsonld.md` | Does the record HTML contain one server-rendered schema.org `Dataset` JSON-LD block? | Yes |
| `metadata-profile.md` | Does the record declare a metadata profile? | Yes |
| `persistent-identifiers.md` | Which of DOI or accession, ORCID, ROR, and RRID appear as IRIs? | Yes |
| `vocabulary.md` | Is there a stable glossary or data dictionary, and a link to an ontology the repository uses? | Optional |
| `rights-and-license.md` | Are license and access conditions in machine-readable metadata? | Yes |
| `citation.md` | Is there a public citation pattern, with creators, that an agent can read? | Optional |
| `provenance-lineage.md` | Does the record state its version, its derivation, and file checksums? | Yes |
| `shacl-shapes.md` | Are record or submission rules published as SHACL? | No |
| `sssom-mappings.md` | Is a public SSSOM mapping set linked? | No |
| `competency-questions.md` | Does the site publish competency questions about its own data? | No |
| `competency-answerability.md` | Can an agent answer up to three of those questions from the site alone? | No |

## Deferred

This pass does not score FAIR Signposting, WebMCP, generative UI, a Chrome Lighthouse agent audit, or CDN logs by user agent. Of the slides' three evaluation methods, only competency questions are covered here (`competency-answerability.md`). The slides mark signposting, WebMCP, and generative UI as later topics. Lighthouse and log breakdowns need a browser audit or operator logs.

Blueprint text, when a prompt needs it:

`https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`
