# llms.txt

**Question:** Is there an `llms.txt` for the site or a section of it, and do pages point at a Markdown alternate and at the `llms.txt` that describes them?

Slide theme: Be readable, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026).

## Role

You evaluate one property of a public data-repository website: `llms.txt` and the two link relations that point at Markdown and at that file. Report only URLs and headers you fetched.

Specification and audit notes, for the relation names: https://llmstxt.org/ and https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt. A file under a subfolder covers the pages under that folder. Relations may be HTML `link` tags or HTTP `Link` headers: `rel="alternate"` with `type="text/markdown"`, and `rel="describedby"` pointing at the `llms.txt`.

## Inputs

- Repository origin URL (required).
- Record URL (optional). One dataset, study, or experiment page.

When no record URL is given, discover one public record from the homepage, `llms.txt`, or the sitemap, and say how. The file can still be reported when no record exists. Link-relation checks are then `not-observable`.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. Prefer the raw HTTP body.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 is verdict `blocked` for that URL.

## Checks

### Procedure

1. GET `{origin}/llms.txt`.
2. When that response is a miss, GET the homepage and follow the first href whose path ends in `llms.txt`. Count that as the one `llms.txt` fetch.
3. GET one record page. Read its HTML `link` tags and its `Link` response header.
4. Quote the `rel` and `type` values you found. A subfolder `llms.txt` linked from the page counts.

### Pass conditions

- `llms-found`. Pass when a fetched body is an `llms.txt` document.
- `llms-has-links`. Pass when that file lists at least one http(s) or root-relative URL.
- `llms-structure`. Pass when the file opens with a Markdown H1 naming the site, and its links sit in Markdown lists under H2 sections, as llmstxt.org describes. Quote the H1 and the H2 names. Fail when the body is a bare URL list or HTML. This supporting check does not change the verdict.
- `alternate-markdown`. Pass when the record response has `rel="alternate"` and `type="text/markdown"` in a `link` tag or a `Link` header.
- `describedby`. Pass when the record response has `rel="describedby"` pointing at an `llms.txt`.

Verdict `present` when all four pass. Verdict `partial` when `llms-found` passes and a link relation fails, or when the link relations pass and no `llms.txt` was found. Verdict `absent` when no `llms.txt` was found and both link relations fail. Verdict `not-observable` for a link relation when no record page was available. Verdict `blocked` when the `llms.txt` and the record are both behind an access wall.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `sitemap.md` — XML sitemaps
- `markdown-negotiation.md` — whether `Accept: text/markdown` returns Markdown
- `agent-documentation.md` — API docs and `SKILL.md`
- `bulk-export.md` — bulk dumps

The other files in `prompts/evals/` are separate evaluations.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: a required record or document could not be found. Name what you tried.

```yaml
evaluation: llms-txt
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: llms-found
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: llms-has-links
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: llms-structure
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: alternate-markdown
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: describedby
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
