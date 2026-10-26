# SSSOM mappings

**Question:** Is a public SSSOM mapping set linked from the site?

Slide theme: Be meaningful, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). SSSOM is a table that says a term in this repository matches a term elsewhere, with a relation, a justification, and who asserted it. The slides use an ImmPort-to-CDISC set as an example of a set nobody had published. That pair is an illustration, not a required mapping.

## Role

You evaluate one property of a public data-repository website: a linked SSSOM file or a page that publishes an SSSOM table. A generic crosswalk that never says SSSOM is a partial finding. Quote the header you fetched. Do not download more than the header and one data row.

Usual SSSOM columns include `subject_id`, `predicate_id`, `object_id`, and `mapping_justification`.

## Inputs

- Repository origin URL (required).
- Record URL (optional). Use it when the record page links a mapping set.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. One mapping file on another host is allowed when the site links it. Send no credentials. Invent no mappings. Do not load-test.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. This prompt reads the homepage, one `llms.txt`, one docs page, and the header of one mapping file. Prefer the raw HTTP body. When the docs page is an application shell, or its raw body has no mapping link, render that same docs URL once and read links from the rendered view. The mapping file stays a raw GET of its header. Name the view in evidence: `raw` or `rendered`. Count the rendered request in `fetches`. Do not render a second URL, and do not download script bundles. When the docs body is a shell and you cannot render, set `sssom-linked` to `not-observable` and write `client cannot render` in evidence.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 on the mapping file is verdict `blocked`.

## Checks

### Procedure

1. GET the homepage and `{origin}/llms.txt`. Follow one docs link that mentions mappings, crosswalks, or SSSOM. When that docs page is an application shell, or its raw body has no mapping link, render it once before you decide it has no mapping link.
2. GET the linked file, or the first kilobyte of it. Read the header row.
3. Quote one data row when it is in that first kilobyte.

### Pass conditions

- `sssom-linked`. Pass when the site links a file or page it calls SSSOM, or a `.sssom.tsv` (or similar) path.
- `sssom-header`. Pass when the fetched bytes include `subject_id`, `predicate_id`, and `object_id`.
- `mapping-table`. Pass when a crosswalk table is present and the page does not call it SSSOM. Use `not-observable` when the file is SSSOM, and when no crosswalk was found. This check records the partial case. It is not required for `present`.

Verdict `present` when `sssom-linked` and `sssom-header` pass. Verdict `partial` when `mapping-table` passes and the SSSOM checks fail. Verdict `absent` when the fetched pages mention no mapping set. Verdict `blocked` when the linked file is behind an access wall. Verdict `not-observable` when the raw docs body and one rendered view of it are application shells and no mapping link could be read.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `vocabulary.md` — the site's own glossary and ontology links
- `shacl-shapes.md` — SHACL shapes
- `metadata-profile.md` — a declared dataset profile

The other files in `prompts/evals/` are separate evaluations. Do not look for a specific source-target pair.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: the docs could not be read far enough. Name what you tried.

```yaml
evaluation: sssom-mappings
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: sssom-linked
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: sssom-header
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: mapping-table
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
