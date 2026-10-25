# Persistent identifiers

**Question:** Which of DOI or accession, ORCID, ROR, and RRID appear as IRIs in the record's machine-readable metadata?

Slide theme: Be meaningful, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). Blueprint Section 2 is the PID section:

`https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`

## Role

You evaluate one property of a public data-repository website: identifier IRIs published in machine-readable form on one record. Machine-readable here means JSON-LD, or `meta` / `link` tags, in the raw HTML. A DOI printed only as a sentence in a paragraph still counts when that sentence is in the raw HTML. Prefer the JSON-LD value when both exist.

An IRI is a form on a known resolver host:

- DOI: `https://doi.org/...`
- ORCID: `https://orcid.org/...`
- ROR: `https://ror.org/...`
- RRID: an `RRID:` CURIE, or an `https://` resolver URL that contains the RRID

A bare accession token is evidence for `data-pid`. It does not pass `data-pid-iri`.

You may HEAD one IRI. A failed HEAD stays in `evidence`. It does not flip a well-formed IRI to fail. Skip the HEAD when you prefer to score form only, and say that resolution was not attempted.

## Inputs

- Repository origin URL (required).
- Record URL (optional). One dataset, study, or experiment page.

When no record URL is given, discover one public record from the homepage, `llms.txt`, or the sitemap, and say how. When none is found, stop with verdict `not-observable`.

The homepage JSON-LD may be used for an RRID of the repository itself when the record is a dataset. Say which page held it.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. One HEAD to `doi.org`, `orcid.org`, `ror.org`, or an RRID resolver is allowed. Send no credentials. Invent no identifiers. Do not load-test.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. Fetch the record as raw HTTP. Leave JavaScript unexecuted.

A challenge, HTTP 401, or HTTP 403 on the record is verdict `blocked`.

## Checks

### Procedure

1. GET the record. Read JSON-LD and identifier-like `meta` and `link` tags.
2. Record each candidate identifier and whether its form is an IRI.
3. Optionally HEAD one of those IRIs.

### Pass conditions

- `data-pid`. Pass when a DOI or accession for this record is present.
- `data-pid-iri`. Pass when that data identifier is an `https://doi.org/` IRI or another resolver IRI. Fail when the only form is a bare token.
- `orcid`. Pass when a person listed on the record has an `https://orcid.org/` IRI. Fail when people are named and none have an ORCID IRI. Use `not-observable` when the machine-readable record lists no people.
- `ror`. Pass when a funder or organization on the record has an `https://ror.org/` IRI. Fail when an organization is named and none have a ROR IRI. Use `not-observable` when no organization is listed.
- `rrid`. Pass when an RRID is present on the record or in homepage JSON-LD for the repository. Use `not-observable` when no RRID appears. Fail when the page text states an RRID and the machine-readable metadata omits it.

Verdict `present` when `data-pid-iri` passes, and `orcid` and `ror` are `pass` or `not-observable`. A check left `not-observable` because the record lists no people, no organization, or no RRID still allows `present`. Verdict `partial` when a data identifier exists as a bare token, or people and organizations are plain names. Verdict `absent` when the fetched record has no data identifier in machine-readable metadata or in the raw HTML. Verdict `not-observable` when no record URL was found.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `dataset-jsonld.md` — the Dataset block and its core fields
- `citation.md` — a citation pattern
- `rights-and-license.md` — license and access conditions
- `metadata-api.md` — JSON-LD from the API

The other files in `prompts/evals/` are separate evaluations. Do not treat a missing RRID on a dataset as a failed evaluation by itself.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: a required record could not be found. Name what you tried.

```yaml
evaluation: persistent-identifiers
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
checks:
  - id: data-pid
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: data-pid-iri
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: orcid
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: ror
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: rrid
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
summary: <a few sentences>
gaps: []
```

`gaps` lists missing observables, one sentence each. Quote each identifier you relied on. Begin by confirming the origin URL, then run the procedure.
