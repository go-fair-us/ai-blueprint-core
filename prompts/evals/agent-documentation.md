# Agent documentation

**Question:** Are data-access or API docs linked in a form an agent can follow, including a `SKILL.md` when the site publishes one?

Slide theme: Be readable, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). The slides point at agent skills as one way to expose API usage: https://agentskills.io/.

## Role

You evaluate one property of a public data-repository website: whether an agent can open documentation that explains how to get data or call the API, using the raw HTML. A `SKILL.md` and a CLI are reported when the site links them. Their absence is an observation, and it does not by itself fail the docs check.

## Inputs

- Repository origin URL (required).
- Record URL (optional). Use it when the record page is what links to the docs.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Do not load-test, and do not retry in a loop.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. This prompt reads the homepage, one `llms.txt`, and one documentation page. Prefer the raw HTTP body. Leave JavaScript unexecuted.

A challenge, HTTP 401, or HTTP 403 on the docs page is verdict `blocked`.

## Checks

### Procedure

1. GET the homepage and `{origin}/llms.txt`.
2. Follow one link whose text or path names API docs, data access, a developer guide, or a `SKILL.md`.
3. Read that page as raw HTML or Markdown. Quote one concrete instruction (an endpoint, a parameter, or a download step).
4. When the site links a `SKILL.md`, GET it and quote its `name` or first heading. When the docs mention a CLI, quote that sentence.

### Pass conditions

- `docs-linked`. Pass when the homepage, `llms.txt`, or the record links to data-access or API documentation.
- `docs-readable`. Pass when the raw body of that page contains a concrete instruction. Fail when the body is only an application shell.
- `skill-md`. Pass when a fetched `SKILL.md` (or an agentskills.io skill page for this repository) contains a name and steps. Use `not-observable` when the site does not link one. Do not fail the evaluation for that absence.
- `cli-mentioned`. Pass when the fetched docs name a CLI and how to obtain it. Use `not-observable` when they do not. Do not fail the evaluation for that absence.

Verdict `present` when `docs-linked` and `docs-readable` pass. `skill-md` and `cli-mentioned` may be `not-observable`. Verdict `partial` when a docs link exists and the page is a shell or has no concrete instruction. Verdict `absent` when the fetched pages link no such docs. Verdict `blocked` when the docs URL is behind an access wall.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `openapi-discovery.md` — finding an OpenAPI or Swagger document
- `mcp-exposure.md` — a remote MCP server
- `llms-txt.md` — `llms.txt` link relations
- `metadata-api.md` — one JSON-LD metadata GET

The other files in `prompts/evals/` are separate evaluations. Leave the Section 3 API rubric to `niaid-bp-api-assess`.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: the pages you could read did not include a docs link to judge. Name what you tried.

```yaml
evaluation: agent-documentation
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
checks:
  - id: docs-linked
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: docs-readable
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: skill-md
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: cli-mentioned
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
summary: <a few sentences>
gaps: []
```

`gaps` lists missing observables, one sentence each. Begin by confirming the origin URL, then run the procedure.
