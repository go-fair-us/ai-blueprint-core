# Citation

**Question:** Is there a public citation pattern, with creators, that an agent can read?

Slide theme: attribution, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). Blueprint Section 4 is the citation section:

`https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`

## Role

You evaluate one property of a public data-repository website: a citation pattern a client can read from the page. The pattern may be on the record or on a site-wide "how to cite" page linked from the homepage or the record. Read the raw response first. When that body has no citation block, render that same URL once. Creators are authors or contributing organizations named in that same content.

This prompt does not rewrite the citation into BibTeX and does not apply the rest of Section 4. Quote what the site publishes.

## Inputs

- Repository origin URL (required).
- Record URL (optional). One dataset, study, or experiment page. When it is omitted, a site-wide citation page is enough.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no citation text. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. Fetch the homepage and either the record or one citation page. Prefer the raw HTTP body. When that body is an application shell, or it has no citation block, render that same URL once. A pass from either view counts. Name the view in evidence: `raw` or `rendered`. Count the rendered request in `fetches`. Do not render a second URL, and do not download script bundles. When the raw body is a shell and you cannot render, set the citation checks to `not-observable` and write `client cannot render` in evidence.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 on the citation page is verdict `blocked`.

## Checks

### Procedure

1. GET the homepage. When a record URL is known, GET it too.
2. Open one linked page named "cite", "citation", or "how to cite" when the record itself has no citation block. When the raw body has no citation block and no cite link, render that same URL once.
3. Quote the citation string, BibTeX, or the stated pattern, and the creator names, from the view that contains them. Name the view in evidence.

### Pass conditions

- `cite-pattern`. Pass when the raw body or the one rendered view contains a citation string, a BibTeX entry, or a stated pattern that includes the repository and the record id or a placeholder for it.
- `creators`. Pass when that same content names authors or a creator organization for the record or the repository.
- `cite-visible-raw`. Pass when `cite-pattern` and `creators` are both in the initial HTML or Markdown. Fail when they were found only in the rendered view. This check does not change the verdict.

Verdict `present` when `cite-pattern` and `creators` pass. `cite-visible-raw` may fail. Verdict `partial` when a pattern exists and creators are missing, or creators exist and no pattern was published. Verdict `absent` when the fetched pages contain neither. Verdict `not-observable` when the raw homepage and one rendered view of it are application shells and no citation link could be read. Verdict `blocked` when the citation page is behind an access wall.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `rights-and-license.md` — license and conditions of access
- `persistent-identifiers.md` — DOI, ORCID, ROR, and RRID forms
- `dataset-jsonld.md` — the Dataset JSON-LD block
- `provenance-lineage.md` — version, derivation, and checksums

The other files in `prompts/evals/` are separate evaluations. Leave Section 4's full citation rules for a reader who opens the Blueprint. Do not generate a citation the site did not publish.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: no citation page could be found to read. Name what you tried.

```yaml
evaluation: citation
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: cite-pattern
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: creators
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: cite-visible-raw
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
fetches:
  - url: <url>
    method: GET | HEAD
    status: <code, or the error>
summary: <a few sentences>
gaps: []
```

`gaps` lists missing observables, one sentence each. Quote the pattern. Begin by confirming the origin URL, then run the procedure.
