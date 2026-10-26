# Provenance and lineage

**Question:** Does the record's machine-readable metadata say which version it is, where it came from, and how to check that the files are intact?

Slide theme: lineage and IP protection, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). The slides list lineage next to rights and attribution as something a blind scrape loses. Lineage tracks where the data came from and how it changed. Integrity shows that it has not been altered.

## Role

You evaluate one property of a public data-repository website: version, derivation, and integrity statements in the machine-readable metadata of one record. Machine-readable means JSON-LD, or `meta` / `link` tags, in the raw HTML, plus one linked Croissant or RO-Crate file when the record points at one. Report the values. Do not judge whether the provenance is complete.

Look for:

- Version or date: schema.org `version`, `dateModified`, `datePublished`, or `dateCreated`.
- Derivation: schema.org `isBasedOn`, `prov:wasDerivedFrom`, `prov:wasGeneratedBy`, `subjectOf` pointing at a protocol, or an RO-Crate `CreateAction`.
- Integrity: a checksum on a file. Examples are `spdx:checksum` (Science-on-Schema.org), Croissant `sha256` or `md5` on a `FileObject`, or a checksum value in a `DataDownload`.

## Inputs

- Repository origin URL (required).
- Record URL (optional). One dataset, study, or experiment page.

When no record URL is given, discover one public record from the homepage, `llms.txt`, or the sitemap, and say how. When none is found, stop with verdict `not-observable`.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. This prompt reads the record and, when the record links one, the first 64 KB of one Croissant or RO-Crate metadata file. Do not download data files. Prefer the raw HTTP body. Leave JavaScript unexecuted.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 is verdict `blocked`.

## Checks

### Procedure

1. GET the record. Read JSON-LD and `meta` / `link` tags in the raw body.
2. Quote any version or date value for this record.
3. Quote any derivation statement and the IRI or name it points at.
4. Look for a checksum on a `distribution` entry. When the record links a Croissant or RO-Crate file, GET its first 64 KB and look there.

### Pass conditions

- `version-or-date`. Pass when the record's metadata has `version` or `dateModified`. Fail when it has only `datePublished` or `dateCreated`, because those do not show change. Fail when it has no date at all.
- `derivation`. Pass when a derivation property names a source, protocol, or generating activity. Use `not-observable` when the record describes primary data and names no source. Fail when visible text names a source dataset and the metadata omits it.
- `checksum`. Pass when at least one file in the metadata carries a checksum with its algorithm. Use `not-observable` when the metadata lists no files. Fail when files are listed and none has a checksum.

Verdict `present` when `version-or-date` passes and `derivation` or `checksum` passes. Verdict `partial` when one or two checks pass and the verdict is not `present`. Verdict `absent` when the record has machine-readable metadata and all three checks fail or are `not-observable`. Verdict `not-observable` when the record has no machine-readable metadata, or no record URL was found. Point at `dataset-jsonld.md` in `summary` when the gap is a missing JSON-LD block.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `dataset-jsonld.md` — the base Dataset fields
- `metadata-profile.md` — whether Croissant or RO-Crate is declared
- `rights-and-license.md` — license and access conditions
- `citation.md` — how to cite the record

The other files in `prompts/evals/` are separate evaluations. Do not verify a checksum against a downloaded file.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: a required record could not be found. Name what you tried.

```yaml
evaluation: provenance-lineage
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: version-or-date
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: derivation
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: checksum
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
fetches:
  - url: <url>
    method: GET | HEAD
    status: <code, or the error>
summary: <a few sentences>
gaps: []
```

`gaps` lists missing observables, one sentence each. Quote the property name and its value. Begin by confirming the origin URL, then run the procedure.
