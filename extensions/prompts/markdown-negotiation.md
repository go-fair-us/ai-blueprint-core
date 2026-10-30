---
description: "Does the record honor `Accept: text/markdown`, or advertise a Markdown alternate?"
argument-hint: "<origin-url> [record-url]"
---

Repository origin: $1
Record URL: ${2:-none}

The values above are the inputs for this run. When a value is `none`, follow the procedure's rule for that missing input. If the origin is empty, stop and ask for the repository origin URL. Do not fetch.

Follow the evaluation below exactly. Stay inside its checks.

# Markdown negotiation

**Question:** Does the record honor `Accept: text/markdown`, or advertise a Markdown alternate?

Slide theme: Be readable, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). Some sites answer `Accept: text/markdown` with Markdown. Others advertise `rel="alternate"` `type="text/markdown"`. Either path answers this question.

## Role

You evaluate one property of a public data-repository website: a Markdown representation of one record. Report the status, `Content-Type`, and a short quote from each response. Invent no alternate URLs.

## Inputs

- Repository origin URL (required).
- Record URL (optional). One dataset, study, or experiment page.

When no record URL is given, discover one public record from the homepage, `llms.txt`, or the sitemap, and say how. When none is found, stop with verdict `not-observable`.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. This prompt may GET the record twice: once with `Accept: text/markdown`, and once for the advertised alternate when that URL is present. Prefer the raw HTTP body.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 is verdict `blocked`.

## Checks

### Procedure

1. GET the record with `Accept: text/markdown`. Record status and `Content-Type`.
2. Read `link` tags and the `Link` header for `rel="alternate"` and `type="text/markdown"`.
3. When an alternate URL is present, GET it and quote the first lines.

### Pass conditions

- `accept-markdown`. Pass when the `Accept: text/markdown` response is Markdown: `Content-Type` includes `text/markdown`, or the body is Markdown and is a different document from an HTML shell.
- `alternate-advertised`. Pass when a `link` tag or `Link` header advertises `rel="alternate"` with `type="text/markdown"`.
- `alternate-body`. Pass when that alternate URL returns non-empty Markdown. Use `not-observable` when no alternate URL was advertised.

Verdict `present` when `accept-markdown` passes, or when both `alternate-advertised` and `alternate-body` pass. Verdict `partial` when an alternate is advertised and the alternate body fails, or when `Content-Type` says Markdown and the body is still an HTML shell. Verdict `absent` when `accept-markdown` fails and no alternate is advertised. Verdict `not-observable` when no record URL was found.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `llms-txt.md` — whether an `llms.txt` exists and `rel="describedby"` is set
- `server-rendered-content.md` — title, description, identifier, and license in HTML
- `bulk-export.md` — a repository-wide Markdown dump

The other files in `prompts/evals/` are separate evaluations.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: a required record could not be found. Name what you tried.

```yaml
evaluation: markdown-negotiation
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
checks:
  - id: accept-markdown
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: alternate-advertised
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: alternate-body
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
