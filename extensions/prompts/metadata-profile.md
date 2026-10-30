---
description: "Does the record declare which metadata profile it follows?"
argument-hint: "<origin-url> [record-url]"
---

Repository origin: $1
Record URL: ${2:-none}

The values above are the inputs for this run. When a value is `none`, follow the procedure's rule for that missing input. If the origin is empty, stop and ask for the repository origin URL. Do not fetch.

Follow the evaluation below exactly. Stay inside its checks.

# Metadata profile

**Question:** Does the record declare which metadata profile it follows?

Slide theme: Be meaningful, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). The slides name schema.org Dataset, Science-on-Schema.org, Bioschemas Dataset, the NIAID Data Ecosystem fields, Croissant, and RO-Crate. Declaration is the question. A profile is declared with `conformsTo` or an equivalent URL in the record's machine-readable metadata.

## Role

You evaluate one property of a public data-repository website: whether one record says which profile it follows. Recognize these names when they appear:

- Science-on-Schema.org (`science-on-schema.org`)
- Bioschemas Dataset (`bioschemas.org`)
- NIAID Data Ecosystem schema (a `conformsTo` value that names it)
- Croissant (`mlcommons.org/croissant` or a Croissant file URL)
- RO-Crate (`w3id.org/ro/crate`)

schema.org Dataset alone is the base vocabulary. It is not, by itself, a declared profile. Field presence for that base type is `dataset-jsonld.md`.

## Inputs

- Repository origin URL (required).
- Record URL (optional). One dataset, study, or experiment page.

When no record URL is given, discover one public record from the homepage, `llms.txt`, or the sitemap, and say how. When none is found, stop with verdict `not-observable`.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. Fetch the record as raw HTTP. When the record links a Croissant or RO-Crate document on the same host, you may GET that one file. Leave JavaScript unexecuted.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 is verdict `blocked`.

## Checks

### Procedure

1. GET the record. Read JSON-LD in the raw HTML, plus any `Link` header that carries a profile relation.
2. Quote `conformsTo`, `dct:conformsTo`, or a profile URL when present.
3. When no declaration exists, note profile-shaped fields you can see (`variableMeasured`, Bioschemas markup, `infectiousAgent`, `healthCondition`, a Croissant distribution). Those fields support a `partial` verdict. They do not satisfy `profile-declared`.

### Pass conditions

- `profile-declared`. Pass when the record's JSON-LD or HTTP `Link` header names a profile with `conformsTo` or an equivalent profile URL.
- `profile-named`. Pass when that declaration is one of Science-on-Schema.org, Bioschemas Dataset, the NIAID Data Ecosystem schema, Croissant, or RO-Crate. Fail when `conformsTo` is present and matches none of these. Quote the value either way.
- `profile-document`. Pass when a Croissant or RO-Crate URL from the record returns a document of that kind. Use `not-observable` when the record does not link one. Do not fail the evaluation for that absence.

Verdict `present` when `profile-declared` and `profile-named` pass. `profile-document` may be `not-observable`. Verdict `partial` when a `conformsTo` value names a profile outside the five above, or when profile-shaped fields or a Croissant link exist and `profile-declared` fails. Verdict `absent` when the record was fetched, machine-readable metadata was readable, and it declares no profile and shows no profile-shaped fields. Verdict `not-observable` when the record has no machine-readable metadata to inspect, or no record URL was found. Point at `dataset-jsonld.md` in `summary` when the gap is a missing JSON-LD block.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `dataset-jsonld.md` — Dataset type and core fields
- `vocabulary.md` — glossary and ontology links
- `shacl-shapes.md` — published SHACL
- `persistent-identifiers.md` — identifier IRIs

The other files in `prompts/evals/` are separate evaluations. One declared profile is enough. Do not expect every profile at once.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: there was no machine-readable record to inspect. Name what you tried.

```yaml
evaluation: metadata-profile
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: profile-declared
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: profile-named
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: profile-document
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
