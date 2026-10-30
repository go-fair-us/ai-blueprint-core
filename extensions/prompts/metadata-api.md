---
description: "Is there one unauthenticated GET whose path is a resource IRI and whose body is JSON-LD for a dataset or study?"
argument-hint: "<origin-url> [record-url] [metadata-url]"
---

Repository origin: $1
Record URL: ${2:-none}
Metadata URL: ${3:-none}

The values above are the inputs for this run. When a value is `none`, follow the procedure's rule for that missing input. If the origin is empty, stop and ask for the repository origin URL. Do not fetch.

Follow the evaluation below exactly. Stay inside its checks.

# Metadata API

**Question:** Is there one unauthenticated GET whose path is a resource IRI and whose body is JSON-LD for a dataset or study?

Slide theme: Be callable, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). This is one observation of Blueprint Section 3, not the Section 3 rubric. Section text:

`https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`

Section 3's minimum objectives are JSON-LD, resource IRIs, HTTP GET, and an OpenAPI document. OpenAPI discovery is `openapi-discovery.md`. Hand a spec URL to `niaid-bp-api-assess` for the full rubric.

## Role

You evaluate one property of a public data-repository website: a single metadata response. Perform one unauthenticated GET. Report status, `Content-Type`, the request URL, and whether the body contains `@context` and `@type`. Invent no path ids.

## Inputs

- Repository origin URL (required).
- Record URL (optional). Use it to recognize a study or dataset id that the docs already show.
- Metadata URL (optional). When the user supplies a concrete GET URL, call that URL and skip discovery.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Use an example id only when the docs show that exact URL as a real call. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. One metadata GET means one request. Prefer the raw HTTP body.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 on that GET is verdict `blocked`. A response that asks for a key is `blocked`.

## Checks

### Procedure

1. When a metadata URL was supplied, GET it and go to the checks.
2. Otherwise read the homepage, one API docs page, or one OpenAPI document you can find by a direct link. Choose one GET whose path is a single dataset or study and whose id appears in the docs.
3. GET that URL with no credentials. Quote `@context` and `@type` when they are present.

### Pass conditions

- `endpoint-found`. Pass when the request URL was supplied by the user or copied from the site's docs or spec. Use `not-observable` when every example id is a placeholder (`{id}`, `YOUR_ID`, `12345` marked as fake).
- `get-method`. Pass when the call is HTTP GET.
- `resource-iri`. Pass when the path identifies one dataset or study. A path segment such as `getDataset` or `search`, or an id that lives only in a required query parameter, fails this check.
- `jsonld-body`. Pass when the body is JSON and includes `@context` and `@type`. `Content-Type: application/ld+json` is supporting evidence. A repository study type passes when `@context` and `@type` are both present. Plain JSON fails this check.

Verdict `present` when all four pass. Verdict `partial` when the GET returns metadata and `resource-iri` or `jsonld-body` fails. Verdict `absent` when the docs you read describe no metadata GET for a dataset or study. Verdict `not-observable` when a likely API exists and no concrete example URL was published. Verdict `blocked` when the GET requires credentials.

Do not inventory Table 1 fields. Mention a field only when it appears in this one body and you need it as evidence of `@type`.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `openapi-discovery.md` — finding the spec
- `api-http-behavior.md` — status class, redirects, and cache headers
- `dataset-jsonld.md` — JSON-LD embedded in the record HTML
- `persistent-identifiers.md` — DOI, ORCID, ROR, and RRID

The other files in `prompts/evals/` are separate evaluations.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: no concrete example URL was published. Name what you tried.

```yaml
evaluation: metadata-api
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: endpoint-found
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: get-method
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: resource-iri
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: jsonld-body
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
fetches:
  - url: <url>
    method: GET | HEAD
    status: <code, or the error>
summary: <a few sentences>
gaps: []
```

`gaps` lists missing observables, one sentence each. Begin by confirming the origin URL, then run the procedure.
