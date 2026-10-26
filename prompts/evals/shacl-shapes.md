# SHACL shapes

**Question:** Are record or submission rules published as SHACL?

Slide theme: Be meaningful, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). A SHACL shape is a published rule for what a valid record contains. The same file can carry SHACL-AF rules that derive new facts. This prompt looks for the file. It does not run a validator.

## Role

You evaluate one property of a public data-repository website: a public SHACL document linked from the site. Recognize Turtle or RDF that uses SHACL terms (`sh:NodeShape`, `sh:property`, `sh:datatype`, `sh:class`, and the same terms written out as IRIs). When the file also contains rule terms (`sh:rule`, `sh:SPARQLRule`, `sh:TripleRule`), quote one of them under `shacl-af-noted`.

A validator buried in a submission UI, with no shapes file linked, does not pass.

## Inputs

- Repository origin URL (required).
- Record URL (optional). Use it when the record page links a shapes file.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no shapes URL. Do not load-test. Do not run pySHACL or any other validator.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. This prompt reads the homepage, one `llms.txt`, one docs page, and one shapes file. Prefer the raw HTTP body. When the docs page is an application shell, or its raw body has no link to a shapes file, render that same docs URL once and read links from the rendered view. The shapes file stays a raw GET. Name the view in evidence: `raw` or `rendered`. Count the rendered request in `fetches`. Do not render a second URL, and do not download script bundles. When the docs body is a shell and you cannot render, set `shapes-linked` to `not-observable` and write `client cannot render` in evidence.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 on the shapes file is verdict `blocked`.

## Checks

### Procedure

1. GET the homepage and `{origin}/llms.txt`. Follow one docs link that mentions validation, shapes, or submission rules. When that docs page is an application shell, or its raw body has no link to a shapes file, render it once before you decide it has no shapes link.
2. Choose one linked `.ttl`, `.rdf`, or shapes URL, or a link the page labels as SHACL.
3. GET that file. Quote one shape term. When an HTML page only describes a validator, record that and leave the shape term empty.

### Pass conditions

- `shapes-linked`. Pass when a shapes URL is linked from the homepage, `llms.txt`, the record, or the one docs page.
- `shapes-are-shacl`. Pass when the fetched file contains SHACL shape terms. Fail when the link returns a page that only describes a form or a validator.
- `shacl-af-noted`. Pass when the file contains SHACL-AF rule terms and you quoted one. Use `not-observable` when the shapes file has no rule terms. Do not fail the evaluation for that absence.

Verdict `present` when `shapes-linked` and `shapes-are-shacl` pass. `shacl-af-noted` may be `not-observable`. Verdict `partial` when a shapes link exists and the body has no SHACL terms, or the link fails. Verdict `absent` when the fetched pages link no shapes file. Verdict `blocked` when the file is behind an access wall.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `sssom-mappings.md` — SSSOM tables
- `vocabulary.md` — glossary and ontology links
- `competency-questions.md` — published questions
- `dataset-jsonld.md` — JSON-LD on the record

The other files in `prompts/evals/` are separate evaluations. Do not validate a record against the shapes.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: the docs could not be read far enough to look for a link. Name what you tried.

```yaml
evaluation: shacl-shapes
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: shapes-linked
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: shapes-are-shacl
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: shacl-af-noted
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
