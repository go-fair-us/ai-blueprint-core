# Vocabulary

**Question:** Is there a stable glossary, data dictionary, or field list, and does the site link to an ontology it uses?

Slide theme: Be meaningful, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). The slides treat a published term list as the step repositories most often skip. An informal field list counts. A link to an ontology the repository already uses is the second part. IEDB's ONTIE and MRO, and a Gene Ontology reference in API docs, are examples from the slides, not requirements.

## Role

You evaluate one property of a public data-repository website: a stable URL for the site's own terms, and a link to an external or local ontology. A search box is not a dictionary. Report only pages you fetched.

## Inputs

- Repository origin URL (required).
- Record URL (optional). Use it when the record page links the dictionary or an ontology term.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. One ontology URL on another host is allowed when the site links it. Send no credentials. Invent no terms. Do not load-test.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. This prompt reads the homepage, one `llms.txt`, and one dictionary or ontology page. Prefer the raw HTTP body. When the glossary URL's raw body has no terms, render that same URL once. A pass from either view counts. Name the view in evidence: `raw` or `rendered`. Count the rendered request in `fetches`. Do not render a second URL, and do not download script bundles. When the raw body is a shell and you cannot render, set `glossary-readable` to `not-observable` and write `client cannot render` in evidence.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 on the dictionary is verdict `blocked`.

## Checks

### Procedure

1. GET the homepage and `{origin}/llms.txt`. Follow one link named glossary, data dictionary, field list, schema, or ontology.
2. GET that page. When the raw body has no terms, render that same URL once. Quote two terms or field names from the view that contains them. Name the view in evidence.
3. Quote one ontology link (OBO, OLS, Ontobee, a local ontology page, or a term IRI) when the record or the docs contain one.

### Pass conditions

- `glossary-url`. Pass when a stable URL for a glossary, data dictionary, or field list was linked from the homepage, `llms.txt`, the record, or the one docs page you opened.
- `glossary-readable`. Pass when the raw body or the one rendered view of that URL contains terms or field names and a short definition or description.
- `ontology-link`. Pass when the record or the docs link to an ontology or a term in an ontology. Fail when a dictionary exists and no ontology link was found in the pages you fetched.

Verdict `present` when all three pass. Verdict `partial` when the glossary checks pass and `ontology-link` fails, or when an ontology is linked and no site dictionary was found. Verdict `absent` when the fetched pages contain neither. Verdict `blocked` when the dictionary URL is behind an access wall.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `metadata-profile.md` — a declared dataset profile
- `shacl-shapes.md` — SHACL shapes
- `sssom-mappings.md` — SSSOM mapping sets
- `dataset-jsonld.md` — the Dataset JSON-LD block

The other files in `prompts/evals/` are separate evaluations. Do not require a particular ontology.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: the pages you could fetch did not expose a link to judge. Name what you tried.

```yaml
evaluation: vocabulary
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: glossary-url
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: glossary-readable
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: ontology-link
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
