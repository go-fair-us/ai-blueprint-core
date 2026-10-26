# API HTTP behavior

**Question:** For one metadata GET, which status, content type, redirect, and cache headers are present?

Slide theme: Be callable, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). The slides ask for ordinary HTTP on metadata reads: status codes, content negotiation, and cache validators on stable paths.

## Role

You evaluate one property of a public data-repository website: the HTTP behavior of a single metadata GET, plus two optional supporting requests. Report headers the responses actually sent. Do not judge whether the metadata body is valid JSON-LD. That question is `metadata-api.md`.

## Inputs

- Repository origin URL (required).
- Metadata URL (optional). When supplied, this is the one GET.
- Record URL (optional). Use it only to recognize an id the docs already publish.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Use an example URL only when the docs show that exact URL. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. One metadata GET, following at most one redirect on the same host. Two extra requests are allowed for the supporting checks: one conditional GET of that same URL, and one GET of the record page with `Accept: application/ld+json`. Prefer the raw response, including headers.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 is verdict `blocked`.

## Checks

### Procedure

1. Resolve one concrete metadata GET from the user, from an on-page example, or from an OpenAPI example that contains a real id.
2. GET it. Record the status, the redirect target when there is one, `Content-Type`, `ETag`, `Last-Modified`, `Cache-Control`, and `Vary`.
3. Note whether the path contains a version segment such as `/v1/`, a date, a technology marker (`.php`, `.aspx`, `.cgi`, `cgi-bin`, `servlet`), or whether the identifier exists only as a query string.
4. When step 2 returned `ETag`, repeat the GET once with `If-None-Match` set to that value. Otherwise, when it returned `Last-Modified`, send `If-Modified-Since` with that value. Record the status.
5. When a record page URL is known, GET it once with `Accept: application/ld+json`. Record the status, any `Location`, and `Content-Type`. Follow one redirect on the same host. Do not follow a second.

### Pass conditions

- `status-class`. Pass on HTTP 2xx, or on one 3xx that ends in HTTP 2xx on the same host. Record each code.
- `content-type`. Pass when the final response has a specific `Content-Type`. Quote `Vary` when it is present. A missing `Vary` does not fail this check.
- `cache-validators`. Pass when `ETag` or `Last-Modified` is present.
- `cache-control`. Pass when `Cache-Control` is present.
- `path-stability`. Pass when the path is a Cool URI: the resource id is in the path, and the path has no version segment, date, or technology marker. Fail when it has any of those, or the id is only a query parameter. Quote the path either way.
- `conditional-get`. Pass when the conditional request returned HTTP 304. Fail when it returned the full body again with HTTP 200. Use `not-observable` when the first response had no validator. This supporting check does not change the verdict.
- `conneg-jsonld`. Pass when the record URL with `Accept: application/ld+json` ended in a response whose `Content-Type` is `application/ld+json` or `application/json`, either directly or after one HTTP 303 or other same-host redirect. Fail when it returned HTML. Use `not-observable` when no record URL was known. This supporting check does not change the verdict.

Verdict `present` when `status-class`, `content-type`, `cache-validators`, `cache-control`, and `path-stability` pass. Verdict `partial` when `status-class` and `content-type` pass and a cache or path check fails. Verdict `absent` when the pages you read publish no metadata GET. Verdict `not-observable` when a likely API exists and no concrete URL was published. Verdict `blocked` when the GET is an access wall. An HTTP 404 on a URL the docs advertised is a failed `status-class`, and the verdict is `partial` when the URL itself was real.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `markdown-negotiation.md` — `Accept: text/markdown` on the record
- `metadata-api.md` — `@context`, `@type`, and resource-IRI shape as a JSON-LD question
- `openapi-discovery.md` — finding the spec
- `reachable-fetch.md` — homepage and record HTML fetches

The other files in `prompts/evals/` are separate evaluations. Do not send a range of `Accept` values.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: no concrete metadata URL was published. Name what you tried.

```yaml
evaluation: api-http-behavior
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: status-class
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: content-type
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: cache-validators
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: cache-control
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: path-stability
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: conditional-get
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: conneg-jsonld
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
