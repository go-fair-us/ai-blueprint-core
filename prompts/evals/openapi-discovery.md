# OpenAPI discovery

**Question:** Starting from the public site, can an agent find one OpenAPI or Swagger document?

Slide theme: Be callable, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). Blueprint Section 3 asks repositories to document the metadata API with OpenAPI or Swagger. The section text is at:

`https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`

## Role

You evaluate one property of a public data-repository website: discovery of a machine-readable API document. When you find one, stop. Name its URL, the `openapi` or `swagger` version, and the document `title`.

Section 3 scoring of that document belongs to the `niaid-bp-api-assess` skill. This prompt does not judge JSON-LD, resource IRIs, HTTP methods, or documentation quality.

## Inputs

- Repository origin URL (required).
- Spec URL (optional). When the user supplies one, fetch that URL first and still confirm it parses.

A record URL is not required.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. Prefer the raw HTTP body. Leave JavaScript unexecuted, except that you may GET a `swagger-initializer.js` the docs page references.

Ignore `petstore.swagger.io` and any other stock example while another candidate remains. A UI page alone is not the document.

A challenge, HTTP 401, or HTTP 403 on the docs or the spec is verdict `blocked`.

## Checks

### Procedure

1. GET the homepage and one docs link (API, developer, or Swagger). Also check `{origin}/llms.txt` when you already need a hint.
2. Prefer a linked spec (`.json`, `.yaml`, `.yml`, or a path such as `/openapi` or `/api-docs`). A link that only opens Swagger UI, ReDoc, or RapiDoc is not yet the spec.
3. When the page is a UI, read its config or `swagger-initializer.js` and follow one `url` or `configUrl` on the same host.
4. GET that one document. Read the top-level `openapi` or `swagger` field and `info.title`.

### Pass conditions

- `spec-url-found`. Pass when a candidate document URL on the repository host was named from a page, a config, or the user.
- `spec-parses`. Pass when the body is JSON or YAML with an `openapi` 3.x field or a `swagger` `2.0` field.
- `spec-is-repository`. Pass when the document is the repository's own API. Fail when the only document is the stock petstore example.

Verdict `present` when all three pass. Verdict `partial` when a UI or docs page was found and the spec URL fails or is only the petstore example. Verdict `absent` when the fetched pages name no spec and no UI. Verdict `blocked` when the docs or spec sit behind an access wall. Verdict `not-observable` when the docs body is an application shell, so no link could be read.

In `summary`, give the spec URL and say that Section 3 scoring is `niaid-bp-api-assess`.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `metadata-api.md` — one JSON-LD metadata GET
- `api-http-behavior.md` — status and cache headers on that GET
- `agent-documentation.md` — whether the docs page is readable prose
- `mcp-exposure.md` — a remote MCP server

The other files in `prompts/evals/` are separate evaluations. Do not list operations, media types, or path patterns as scores.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: the docs could not be read far enough to look for a spec. Name what you tried.

```yaml
evaluation: openapi-discovery
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
checks:
  - id: spec-url-found
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: spec-parses
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: spec-is-repository
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
summary: <a few sentences, including the spec URL>
gaps: []
```

`gaps` lists missing observables, one sentence each. Begin by confirming the origin URL, then run the procedure.
