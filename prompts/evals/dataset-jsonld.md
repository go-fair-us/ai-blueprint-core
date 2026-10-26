# Dataset JSON-LD

**Question:** Does the record page contain one server-rendered schema.org `Dataset` JSON-LD block with the core fields?

Slide theme: Be meaningful, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). The practical path in the slides starts with one schema.org `Dataset` block in the server-rendered HTML of each dataset page.

## Role

You evaluate one property of a public data-repository website: the JSON-LD embedded in the raw HTML of one record. Parse `script type="application/ld+json"` from that response. Invent no blocks and no fields.

Profile names (`conformsTo`, Croissant, Bioschemas, and the rest) belong to `metadata-profile.md`. Whether a DOI resolves belongs to `persistent-identifiers.md`.

## Inputs

- Repository origin URL (required).
- Record URL (optional). One dataset, study, or experiment page.

When no record URL is given, discover one public record from the homepage, `llms.txt`, or the sitemap, and say how. When none is found, stop with verdict `not-observable`.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. Fetch the record as raw HTTP. Leave JavaScript unexecuted. JSON-LD that appears only after a browser runs scripts is absent from this evaluation.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 is verdict `blocked`.

## Checks

### Procedure

1. GET the record. Collect every `application/ld+json` script in the raw body.
2. Find objects whose `@type` is `Dataset` or `https://schema.org/Dataset`. `@type` may be an array. Expand a `@graph` and look inside it.
3. For the record's Dataset object, look for `name`, `description`, `identifier`, `license`, `creator`, and either `distribution` or `url`. These are the base fields the slides list for schema.org `Dataset`.

### Pass conditions

- `jsonld-block`. Pass when the raw HTML contains at least one `application/ld+json` script.
- `dataset-type`. Pass when one object in that script is a schema.org `Dataset`.
- `field-name`. Pass when that Dataset has `name`.
- `field-description`. Pass when that Dataset has `description`.
- `field-identifier`. Pass when that Dataset has `identifier`.
- `field-license`. Pass when that Dataset has `license`.
- `field-creator`. Pass when that Dataset has `creator` with at least one `Person` or `Organization`, or a name string.
- `field-distribution-or-url`. Pass when that Dataset has `distribution` or `url`.

Extra objects (Organization, Person, and so on) are fine. When several Dataset objects appear and you cannot tell which one is the record, `dataset-type` is `pass` and the verdict is `partial`. Say how many Dataset objects you saw.

Verdict `present` when all eight checks pass on one Dataset that is clearly this record. Verdict `partial` when a Dataset block exists and one or more field checks fail, or when several Dataset objects are ambiguous. Verdict `absent` when the raw HTML has no JSON-LD script, or the script has no Dataset. Verdict `not-observable` when no record URL was found.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `metadata-profile.md` — `conformsTo` and named profiles
- `persistent-identifiers.md` — DOI, ORCID, ROR, and RRID as IRIs
- `rights-and-license.md` — access conditions next to the license
- `server-rendered-content.md` — title and license as visible HTML, with a rendered comparison
- `metadata-api.md` — JSON-LD from an API GET

The other files in `prompts/evals/` are separate evaluations.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: a required record could not be found. Name what you tried.

```yaml
evaluation: dataset-jsonld
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: jsonld-block
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: dataset-type
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: field-name
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: field-description
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: field-identifier
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: field-license
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: field-creator
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: field-distribution-or-url
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
fetches:
  - url: <url>
    method: GET | HEAD
    status: <code, or the error>
summary: <a few sentences>
gaps: []
```

`gaps` lists missing observables, one sentence each. Quote the field value or the first 20 characters of it. Begin by confirming the origin URL, then run the procedure.
