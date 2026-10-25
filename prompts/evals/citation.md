# Citation

**Question:** Is there a public citation pattern, with creators, that a non-JavaScript fetch can read?

Slide theme: attribution, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). Blueprint Section 4 is the citation section:

`https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`

## Role

You evaluate one property of a public data-repository website: a citation pattern a client can read from the raw response. The pattern may be on the record or on a site-wide "how to cite" page linked from the homepage or the record. Creators are authors or contributing organizations named in that same raw content.

This prompt does not rewrite the citation into BibTeX and does not apply the rest of Section 4. Quote what the site publishes.

## Inputs

- Repository origin URL (required).
- Record URL (optional). One dataset, study, or experiment page. When it is omitted, a site-wide citation page is enough.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no citation text. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. Fetch the homepage and either the record or one citation page. Prefer the raw HTTP body. Leave JavaScript unexecuted.

A challenge, HTTP 401, or HTTP 403 on the citation page is verdict `blocked`.

## Checks

### Procedure

1. GET the homepage. When a record URL is known, GET it too.
2. Open one linked page named "cite", "citation", or "how to cite" when the record itself has no citation block.
3. Quote the citation string, BibTeX, or the stated pattern, and the creator names, from the raw body.

### Pass conditions

- `cite-pattern`. Pass when the raw body contains a citation string, a BibTeX entry, or a stated pattern that includes the repository and the record id or a placeholder for it.
- `creators`. Pass when that same raw content names authors or a creator organization for the record or the repository.
- `cite-visible-raw`. Pass when both of the above are in the initial HTML or Markdown, rather than only in a script bundle you did not fetch.

Verdict `present` when all three pass. Verdict `partial` when a pattern exists and creators are missing, or creators exist and no pattern was published. Verdict `absent` when the fetched pages contain neither. Verdict `not-observable` when the homepage is an application shell and no citation link could be read. Verdict `blocked` when the citation page is behind an access wall.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `rights-and-license.md` — license and conditions of access
- `persistent-identifiers.md` — DOI, ORCID, ROR, and RRID forms
- `dataset-jsonld.md` — the Dataset JSON-LD block

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
summary: <a few sentences>
gaps: []
```

`gaps` lists missing observables, one sentence each. Quote the pattern. Begin by confirming the origin URL, then run the procedure.
