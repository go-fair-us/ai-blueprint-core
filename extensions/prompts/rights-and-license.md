---
description: "Are the license and the conditions of access present in machine-readable metadata on the record?"
argument-hint: "<origin-url> [record-url]"
---

Repository origin: $1
Record URL: ${2:-none}

The values above are the inputs for this run. When a value is `none`, follow the procedure's rule for that missing input. If the origin is empty, stop and ask for the repository origin URL. Do not fetch.

Follow the evaluation below exactly. Stay inside its checks.

# Rights and license

**Question:** Are the license and the conditions of access present in machine-readable metadata on the record?

Slide theme: rights and access, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). The slides treat rights as something an agent should keep attached to the record. Blind scraping often drops them.

## Role

You evaluate one property of a public data-repository website: license and access conditions in machine-readable form in the raw record response. Machine-readable here means JSON-LD fields, or `link` / `meta` tags, in the initial HTML. You report the values. You do not judge whether the license is open.

Look for:

- License: schema.org `license`, a `rel="license"` link, or an SPDX identifier or license URL in JSON-LD.
- Access: schema.org `conditionsOfAccess`, or an access phrase in that same machine-readable block (`open access`, `controlled access`, `restricted`, `data use agreement`).

A license that appears only inside a script bundle, an image, or a modal the raw HTML does not contain fails the machine-readable check. Visible text in the raw HTML is supporting evidence. The pass is the machine-readable value.

## Inputs

- Repository origin URL (required).
- Record URL (optional). One dataset, study, or experiment page.

When no record URL is given, discover one public record from the homepage, `llms.txt`, or the sitemap, and say how. When none is found, stop with verdict `not-observable`.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no licenses. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. Fetch the record as raw HTTP. Leave JavaScript unexecuted.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 is verdict `blocked`. A blocked record is not a finding about its license.

## Checks

### Procedure

1. GET the record.
2. Read JSON-LD and license or access `link` and `meta` tags in the raw body.
3. Quote the license value and the access value from that machine-readable source.

### Pass conditions

- `license-machine`. Pass when a license URL, license name, or SPDX identifier is in JSON-LD or in a `rel="license"` link in the raw response.
- `access-machine`. Pass when `conditionsOfAccess` or an access phrase is in that same machine-readable metadata.

Verdict `present` when both pass. Verdict `partial` when one passes. Verdict `absent` when the raw record contains neither in machine-readable form. Verdict `not-observable` when no record URL was found. A footer "Privacy" link is not a license for the dataset.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `citation.md` — how to cite, and creators
- `dataset-jsonld.md` — the full Dataset field list
- `persistent-identifiers.md` — DOI, ORCID, ROR, and RRID
- `server-rendered-content.md` — whether the license string is in the initial HTML at all
- `provenance-lineage.md` — version, derivation, and checksums

The other files in `prompts/evals/` are separate evaluations.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: a required record could not be found. Name what you tried.

```yaml
evaluation: rights-and-license
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: license-machine
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: access-machine
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
fetches:
  - url: <url>
    method: GET | HEAD
    status: <code, or the error>
summary: <a few sentences>
gaps: []
```

`gaps` lists missing observables, one sentence each. Quote the license and access values you found. Begin by confirming the origin URL, then run the procedure.
