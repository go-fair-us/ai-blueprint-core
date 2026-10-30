---
description: "What does `robots.txt` allow or deny for search indexers, user-driven fetchers, and trainer crawlers, and does it name a sitemap?"
argument-hint: "<origin-url> [record-url]"
---

Repository origin: $1
Record URL: ${2:-none}

The values above are the inputs for this run. When a value is `none`, follow the procedure's rule for that missing input. If the origin is empty, stop and ask for the repository origin URL. Do not fetch.

Follow the evaluation below exactly. Stay inside its checks.

# Robots policy

**Question:** What does `robots.txt` allow or deny for search indexers, user-driven fetchers, and trainer crawlers, and does it name a sitemap?

Slide theme: Be reachable, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026).

## Role

You evaluate one property of a public data-repository website: the contents of its `robots.txt`. Report the groups that are in the file. Allow and Disallow are both successful observations. Permission for a trainer crawler is not a passing grade, and a missing permission is not a failing grade.

Quote a user-agent token only when it appears in this file. Vendor lists are a glossary for tokens you actually see:

- Content-Signals: https://blog.cloudflare.com/content-signals-policy/
- OpenAI crawler tokens: https://developers.openai.com/api/docs/bots
- Perplexity crawler tokens: https://docs.perplexity.ai/docs/resources/perplexity-crawlers

## Inputs

- Repository origin URL (required).
- Record URL (optional). Use it only as a sample path when applying group rules. The file can be scored without one.

## Fetch budget

Stay on the repository host. Send no credentials. Invent no record ids. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. This prompt fetches `{origin}/robots.txt` only. Prefer the raw HTTP body.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 on `robots.txt` is verdict `blocked`.

## Checks

### Procedure

1. GET `{origin}/robots.txt`.
2. List each `User-agent` group and its `Allow` and `Disallow` lines.
3. For a sample path (`/` and, when supplied, the record path), say which group applies. A request with no specific group uses `*`.
4. Copy every `Sitemap:` line. Leave those sitemaps unfetched.
5. When the file contains a Content-Signals directive, quote it.

### Pass conditions

- `robots-fetched`. Pass on HTTP 200 and a robots.txt body. Fail when the resource is missing. A challenge, 401, or 403 ends the run as `blocked`.
- `groups-reported`. Pass when the summary names each group and states whether `/` is allowed or disallowed under that group.
- `visitor-classes`. Pass when the report says, for search indexers, user-driven fetchers, and trainer crawlers, either the matching `User-agent` token found in this file or "no specific group in this file; `*` applies". This check fails only when the file cannot be interpreted. Allow and Disallow are both passes.
- `sitemap-named`. Pass when the file has at least one `Sitemap:` line. Fail when the fetched file has none.
- `content-signals`. Pass when a content-signal directive is present and quoted. Use `not-observable` when the file has none. Do not fail this check.

Verdict `absent` when `robots-fetched` fails because the file is missing. Verdict `present` when `robots-fetched`, `groups-reported`, `visitor-classes`, and `sitemap-named` pass. `content-signals` may stay `not-observable`. Verdict `partial` when the file was read and `sitemap-named` fails, or a group could not be applied. Verdict `not-observable` when a HTTP 200 body is an HTML error page or otherwise not robots.txt.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `reachable-fetch.md` — whether a non-browser GET returns a page
- `sitemap.md` — whether a sitemap lists record URLs
- `llms-txt.md` — `llms.txt` and Markdown link relations

The other files in `prompts/evals/` are separate evaluations. Do not recommend that the site allow or deny training.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: the body could not be interpreted. Name what you tried.

```yaml
evaluation: robots-policy
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: robots-fetched
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: groups-reported
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: visitor-classes
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: sitemap-named
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: content-signals
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
fetches:
  - url: <url>
    method: GET | HEAD
    status: <code, or the error>
summary: <a few sentences, including the three visitor classes>
gaps: []
```

`gaps` lists missing observables, one sentence each. Put the group-by-group policy in `summary` and in `visitor-classes` evidence. Begin by confirming the origin URL, then run the procedure.
