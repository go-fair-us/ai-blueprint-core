# Server-rendered content

**Question:** Are the record title, description, identifier, and license in the initial HTML response?

Slide theme: Be readable, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). Many agent fetches do not run JavaScript, so text that arrives only after a browser executes scripts is invisible to them.

## Role

You evaluate one property of a public data-repository website: whether four record strings are in the raw HTML, before any script runs. Report only text present in that response, plus one optional rendered comparison.

This is the only prompt in the set that may use a JavaScript-capable fetch. Use it to compare. The pass conditions are the raw response.

## Inputs

- Repository origin URL (required).
- Record URL (optional). One dataset, study, or experiment page.

When no record URL is given, discover one public record from the homepage, `llms.txt`, or the sitemap, and say how. When none is found, stop with verdict `not-observable`.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. Fetch the record once as raw HTTP. A second, rendered fetch of that same URL is allowed for the comparison check.

Text inside a linked `.js` bundle is outside the initial HTML. Do not download the bundle. A document that is only a root element plus script tags fails the four raw checks.

A challenge, HTTP 401, or HTTP 403 is verdict `blocked`.

## Checks

### Procedure

1. GET the record with a normal HTTP client. Save status, `Content-Type`, and the raw body.
2. Search that body for the title, a description, an identifier (DOI, accession, or other id), and a license or access-terms string. `title`, meta description, visible text, and a JSON-LD script all count as in the initial HTML.
3. When a JavaScript-capable tool is available, render the same URL once and say whether any of the four strings appear only after render.
4. When no renderer is available, set `js-contrast` to `not-observable` and score the raw checks.

### Pass conditions

- `raw-title`. Pass when the record title is in the raw body.
- `raw-description`. Pass when a description of this record is in the raw body.
- `raw-identifier`. Pass when a DOI, accession, or other record id is in the raw body.
- `raw-license`. Pass when a license name, license URL, or access-terms phrase for this record is in the raw body.
- `js-contrast`. Pass when a rendered view was compared and you stated, for each of the four strings, whether it was already in the raw body. Use `not-observable` when you did not render. This check does not change the verdict on its own.

Verdict `present` when the four `raw-*` checks pass. Verdict `partial` when at least one `raw-*` check passes and another fails. Verdict `absent` when the raw body is an application shell or otherwise lacks all four strings. Verdict `not-observable` when no record URL was found. `js-contrast` may be `not-observable` on a `present` verdict.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `dataset-jsonld.md` — whether that JSON-LD is a schema.org `Dataset` with the expected fields
- `rights-and-license.md` — whether license and access are machine-readable
- `markdown-negotiation.md` — Markdown negotiation
- `reachable-fetch.md` — whether the GET returns a page at all

The other files in `prompts/evals/` are separate evaluations.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: a required record could not be found. Name what you tried.

```yaml
evaluation: server-rendered-content
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
checks:
  - id: raw-title
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: raw-description
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: raw-identifier
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: raw-license
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: js-contrast
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
summary: <a few sentences>
gaps: []
```

`gaps` lists missing observables, one sentence each. Quote a short snippet for each raw check that passes. Begin by confirming the origin URL, then run the procedure.
