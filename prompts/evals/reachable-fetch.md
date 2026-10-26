# Reachable fetch

**Question:** Can a non-browser GET read the homepage and one record?

Slide theme: Be reachable, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026).

## Role

You evaluate one property of a public data-repository website: whether a normal HTTP client, without running JavaScript, receives a real response for the homepage and one record. Report only responses you received. Invent no pages, headers, or status codes.

A JavaScript application shell is still a successful fetch. Whether the record's text is in that HTML is the job of `server-rendered-content.md`.

## Inputs

- Repository origin URL (required). Example: `https://example.org/`.
- Record URL (optional). One dataset, study, or experiment page.

When no record URL is given, discover one public record from the homepage, `llms.txt`, or the sitemap, and say how you found it. When none is found, report the homepage and set the record check to `not-observable`.

Identify the client with a descriptive evaluation user agent. Do not impersonate Googlebot or a trainer crawler.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. This prompt uses the homepage and one record. Prefer the raw HTTP body. Leave JavaScript unexecuted.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge page, HTTP 401 or 403, or an empty access wall is verdict `blocked` for that URL. CDN and firewall bot filters often answer automated clients this way. When a response is blocked, quote whatever names the filter: a header such as `cf-mitigated: challenge` or `server: AkamaiGHost`, or page text such as "Just a moment", "Verify you are human", or "Access denied". That tells the operator to look at the CDN setting, not the application.

## Checks

### Procedure

1. Confirm the origin URL.
2. GET the origin. Record status, `Content-Type`, and whether the body is empty, a challenge, or a page.
3. Resolve one record URL. GET it the same way.
4. When a response is HTTP 429, copy `Retry-After` into the evidence and stop. Do not retry.

### Pass conditions

- `homepage-get`. Pass when the origin returns HTTP 2xx, a `Content-Type`, and a non-empty body that is a page rather than a challenge or interstitial. A short application shell still passes.
- `record-get`. Pass on the same conditions for the record URL. Use `not-observable` when no record URL could be discovered. Use a blocked result when that response is a challenge, 401, or 403.

Verdict `present` when both checks pass. Verdict `partial` when one passes and the other fails or is `not-observable`. Verdict `blocked` when both URLs are blocked, or the only requested URL is blocked. Verdict `absent` when the server answers and the body is empty. A 429 on the single try is `blocked` for that URL.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `robots-policy.md` — what `robots.txt` allows
- `server-rendered-content.md` — whether record text is in the initial HTML
- `markdown-negotiation.md` — Markdown responses
- `api-http-behavior.md` — cache and content-negotiation headers on a metadata API

The other files in `prompts/evals/` are separate evaluations.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: a required record or document could not be found. Name what you tried.

```yaml
evaluation: reachable-fetch
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: homepage-get
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: record-get
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
fetches:
  - url: <url>
    method: GET | HEAD
    status: <code, or the error>
summary: <a few sentences>
gaps: []
```

`gaps` lists missing observables, one sentence each. When a 429 included `Retry-After`, quote the header in `evidence`. Begin by confirming the origin URL, then run the procedure.
