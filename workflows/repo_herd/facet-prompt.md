You are evaluating one public data repository for agent access, using the
procedures in the connected NIAID Blueprint knowledge server. Do not invent
pages, headers, status codes, or JSON-LD.

Target
- Repository name: {{NAME}}
- Repository origin: {{ORIGIN}}
{{HINT_BLOCK}}
- If no hint page is a dataset, study, or experiment record that returns HTTP 2xx, discover one public record from the homepage, robots.txt, llms.txt, or the sitemap. Say how you found it. Do not invent record ids.
- One metadata GET is allowed after you have read evals/metadata-api.md. Choose it from the API documentation the site publishes. Do not invent a path.

Question
Apply the November 2026 webinar properties Be reachable, Be readable, Be callable, and Be meaningful. The working definitions and the exact checks are in the knowledge server. Load them before you fetch the site.

Use the Blueprint MCP server only as the source of procedures
Call these tools, in this order, before the first request to the target:
1. kb_stats, so you know this server is the Blueprint corpus.
2. read_doc path "evalPrompts.md". That catalog is the index. Obey its verdict labels, client check, and the rule that each file scores only its own question.
3. read_doc path "Webinar_Nov_2026/glossary.md" only if a term in a check is unclear. Use the Being reachable, Being readable, Being callable, and Being meaningful sections.
4. For each check below, read_prompt_file on that eval path immediately before you score it. Follow that file's pass conditions. Keep its check ids.
5. {{STEP_PRIOR_NOTES}}
6. When you score the API, read_skill "niaid-bp-api-assess" and read_skill_file "niaid-bp-api-assess" "references/api-checklist.md". Also get_blueprint_section "3" and get_okf_requirements pillar "api".
7. If you can run a local command, also read_skill and run the script for niaid-bp-robots, niaid-bp-sitemap, and niaid-bp-llms against the origin. Attach their JSON. If you cannot run the script, follow the matching eval file with your HTTP client and say the script did not run.
8. If a server-rendered schema.org Dataset JSON-LD block is in the record HTML, pass that graph text to validate_dataset. If there is no such block, skip the tool.

Leave the registered prompts fair_crawl_assessor, fair_web_assessor, fair_assessment_interview, and fair_self_assessment unused. Leave niaid-bp-fair-assess, niaid-bp-dataset-intake, niaid-bp-citation, niaid-bp-teach, and niaid-bp-model-influence unloaded. Those are interviews or a whole-Blueprint score.

Checks, in order
Be reachable: evals/reachable-fetch.md, evals/robots-policy.md
Be readable: evals/llms-txt.md, evals/sitemap.md, evals/server-rendered-content.md, evals/markdown-negotiation.md, evals/bulk-export.md, evals/agent-documentation.md
Be callable: evals/openapi-discovery.md, then evals/metadata-api.md, then evals/api-http-behavior.md on the same GET, then evals/mcp-exposure.md
Be meaningful: evals/dataset-jsonld.md, evals/persistent-identifiers.md, evals/vocabulary.md, evals/metadata-profile.md, evals/shacl-shapes.md, evals/sssom-mappings.md, evals/competency-questions.md

For Be callable, openapi-discovery only locates a spec. If you find an OpenAPI or Swagger document, score it with the api-assess checklist. If the page has no spec, say so, set confidence to low, and keep undeclared facts as not stated. A remote MCP server on this host is optional. Missing one is a finding. Do not call any MCP tool on {{HOST}}. The Blueprint server you already used is not that advertisement.

HTTP rules
Name your client before the first fetch. Say whether it returns the status code, the response headers, and the unmodified body. A tool that summarizes HTML or returns extracted text cannot support script, meta, link, or header checks. Mark those checks not-observable and write "client cannot see ..." in evidence. inspect_url on the Blueprint server is an extract. It is not a raw HTTP client. Prefer a client that can send curl -i style requests. Send Accept: text/markdown only for the markdown-negotiation check.

Fetch each URL once and reuse that body across checks. Stay on {{HOST}} and an obvious API or docs host the site itself uses. Send no credentials and no cookies. Do not load-test. On HTTP 429, copy Retry-After into the evidence and stop. Combined cap: homepage, robots.txt, one llms.txt, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, one API docs or OpenAPI document, and one Markdown probe of the record. One render of a URL is allowed only when the eval file you just read allows it. Count it in fetches.

Report
Return one Markdown report. Do not collapse the checks into a single score. For each of the four properties, give one short paragraph of what a repository operator should do next, then the YAML from each eval you ran. Each YAML keeps evaluation, target, verdict, evaluated_at, client, checks, and fetches. verdict is one of present, partial, absent, blocked, or not-observable, as that file defines it. Quote the URL, status, header, or a short passage for every evidence line. End with a table: property, evaluation name, verdict, one evidence URL. List the Blueprint MCP tools you called.
