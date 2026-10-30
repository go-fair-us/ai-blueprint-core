---
description: "Is there a sitemap or sitemap index, discoverable from the site, that lists record URLs?"
argument-hint: "<origin-url> [record-url]"
---

Repository origin: $1
Record URL: ${2:-none}

The values above are the inputs for this run. When a value is `none`, follow the procedure's rule for that missing input. If the origin is empty, stop and ask for the repository origin URL. Do not fetch.

Follow the evaluation below exactly. Stay inside its checks.

# Sitemap

**Question:** Is there a sitemap or sitemap index, discoverable from the site, that lists record URLs?

Slide theme: Be readable, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026).

## Role

You evaluate one property of a public data-repository website: whether a sitemap an agent can discover lists dataset, study, or record URLs. Report only files you opened.

Protocol reference: https://sitemaps.org/protocol.html. A sitemap index groups several sitemap files. Some `robots.txt` files name more than one sitemap. Record those names. Open at most three of them.

## Inputs

- Repository origin URL (required).
- Record URL (optional). When it is supplied, look for that URL in the URLs you scan.

A record URL is not required. The sitemap's own `loc` entries are the evidence.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. Prefer the raw HTTP body.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 on the sitemap is verdict `blocked`.

## Checks

### Procedure

1. GET `{origin}/robots.txt` and copy each `Sitemap:` value.
2. When no `Sitemap:` line exists, GET `{origin}/sitemap.xml`.
3. Open at most 3 sitemap documents, counting the index. Scan at most 50 `loc` values in total.
4. Classify a `loc` as a record URL when it is the supplied record URL, or when the path looks like a dataset, study, experiment, or accession page. Quote the matching `loc` values, up to five.
5. Note whether the scanned entries carry `lastmod`. Crawlers and agents use it to decide what to fetch again.

### Pass conditions

- `sitemap-discovered`. Pass when a sitemap URL came from `robots.txt` or from `{origin}/sitemap.xml` with HTTP 200.
- `sitemap-parsed`. Pass when the body is a `urlset` or a `sitemapindex`. Fail when the body is HTML or empty.
- `record-urls`. Pass when at least one scanned `loc` is a record URL. Use `not-observable` when the cap was reached before any record URL appeared. Fail when the scanned URLs are only the homepage, docs, or other non-record pages.
- `lastmod`. Pass when most scanned `url` entries have a `lastmod` date. Fail when none do. Quote one value. This supporting check does not change the verdict.

Verdict `present` when all three pass. Verdict `partial` when a sitemap parses and `record-urls` fails or is `not-observable`. Verdict `absent` when no sitemap URL returns a document. Verdict `blocked` when the discovered sitemap response is a challenge, 401, or 403.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `robots-policy.md` — Allow and Disallow groups
- `llms-txt.md` — `llms.txt`
- `bulk-export.md` — bulk download links
- `reachable-fetch.md` — fetching a record page

The other files in `prompts/evals/` are separate evaluations. Leave child sitemaps beyond the cap unopened.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: the cap hid the answer. Name what you tried.

```yaml
evaluation: sitemap
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: sitemap-discovered
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: sitemap-parsed
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: record-urls
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: lastmod
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
fetches:
  - url: <url>
    method: GET | HEAD
    status: <code, or the error>
summary: <a few sentences>
gaps: []
```

`gaps` lists missing observables, one sentence each. Include the sitemap URL and the count of `loc` values you scanned. Begin by confirming the origin URL, then run the procedure.
