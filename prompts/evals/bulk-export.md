# Bulk export

**Question:** Is a bulk download or bulk Markdown export linked from the site or from `llms.txt`?

Slide theme: Be readable, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026).

## Role

You evaluate one property of a public data-repository website: whether an agent can find a bulk transfer of records or Markdown, rather than one page at a time. Report only links you found in the pages you fetched. A per-record download button is not a bulk export.

## Inputs

- Repository origin URL (required).
- Record URL (optional). Use it only when the record page itself links to a repository-wide dump. A single-file download for that one record does not pass.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. This prompt reads the homepage, one `llms.txt`, and one linked docs or download page. Prefer the raw HTTP body. When the homepage is an application shell and `llms.txt` has no bulk link, render the homepage once and look for the link. The dump stays a HEAD or a short GET. Name the view in evidence: `raw` or `rendered`. Count the rendered request in `fetches`. Do not render a second URL, and do not download script bundles. When the homepage is a shell and you cannot render, set `bulk-link` to `not-observable` and write `client cannot render` in evidence.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

Do not download a multi-gigabyte object. HEAD it, or GET the first kilobyte, and record status and `Content-Type`. A landing page that names the dump URL and the format is enough when the file itself is large.

A challenge, HTTP 401, or HTTP 403 on the export page is verdict `blocked`.

## Checks

### Procedure

1. GET the homepage and `{origin}/llms.txt`.
2. From those two bodies, choose one link whose text or path names a bulk download, data dump, full export, or bulk Markdown. When the raw homepage is a shell and `llms.txt` has no such link, render the homepage once and choose the link from that view. GET that page.
3. Record the artifact URL, the format the page states, and the HEAD or short GET of one artifact.

### Pass conditions

- `bulk-link`. Pass when the homepage, `llms.txt`, or that one follow-up page links to a repository-wide dump or bulk Markdown set.
- `link-resolves`. Pass when that link returns HTTP 2xx, or when the landing page names a concrete file URL and format. Fail when the link 404s.
- `format-stated`. Pass when the page names the format (Markdown, CSV, JSON, tar, and so on) or the unit of the dump (all studies, all records).

Verdict `present` when all three pass. Verdict `partial` when a bulk link exists and `link-resolves` or `format-stated` fails. Verdict `absent` when the fetched pages contain no bulk link. Verdict `not-observable` when the raw homepage and one rendered view are shells with no links and `llms.txt` is missing, so the pass could not see a download page. Verdict `blocked` when the candidate export URL is behind an access wall.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `sitemap.md` — sitemap `loc` entries
- `llms-txt.md` — the `llms.txt` format and link relations
- `agent-documentation.md` — API documentation
- `metadata-api.md` — one metadata GET

The other files in `prompts/evals/` are separate evaluations.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: the pages you were allowed to read did not expose enough to decide. Name what you tried.

```yaml
evaluation: bulk-export
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: bulk-link
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: link-resolves
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: format-stated
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
