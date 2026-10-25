# MCP exposure

**Question:** Does the site advertise a remote MCP server?

Slide theme: Be callable, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). A remote MCP server is optional. Calls still go through the repository's API, login, and limits. The public registry is https://registry.modelcontextprotocol.io/.

## Role

You evaluate one property of a public data-repository website: whether a remote MCP endpoint is advertised. Fetch only URLs the site links, plus one registry URL when the site links an entry. Do not search the registry by name. Do not invent a `/.well-known/` path.

A CLI named in the docs is worth a sentence in `summary`. It does not make this check pass.

## Inputs

- Repository origin URL (required).
- Record URL (optional). Use it when that page is what links to MCP.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. A registry host is allowed only for a URL the site itself links. Send no credentials. Invent no record ids. Do not call MCP tools. Do not load-test.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. This prompt reads the homepage, one `llms.txt`, and one docs page. Prefer the raw HTTP body.

A challenge, HTTP 401, or HTTP 403 on the docs page is verdict `blocked`.

## Checks

### Procedure

1. GET the homepage and `{origin}/llms.txt`. Follow one docs link when those pages mention MCP, tools, or a model context server.
2. Quote any remote MCP URL (scheme, host, and path).
3. When the site links a registry entry, GET that one entry and quote the name shown there.
4. When the site says the server is local only, quote that sentence and leave the remote URL empty.

### Pass conditions

- `mcp-documented`. Pass when a fetched page names MCP or a Model Context Protocol server for this repository.
- `remote-endpoint`. Pass when that material includes an http(s) URL for a remote server. Fail when the only instruction is to run a server on localhost. Use `not-observable` when MCP is not mentioned.
- `registry-entry`. Pass when a site-linked registry URL was fetched and names this repository. Use `not-observable` when the site links no registry entry. Do not fail the evaluation for that absence.

Verdict `present` when `mcp-documented` and `remote-endpoint` pass. `registry-entry` may be `not-observable`. Verdict `partial` when MCP is documented as local-only, or documented without a URL. Verdict `absent` when the homepage, `llms.txt`, and the one docs page were read and do not mention MCP. Verdict `not-observable` when those pages could not be read (application shell or failed fetch) and no MCP link was visible. Verdict `blocked` when the only docs URL is behind an access wall.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `agent-documentation.md` — API docs and `SKILL.md`
- `openapi-discovery.md` — an OpenAPI document
- `metadata-api.md` — one JSON-LD GET

The other files in `prompts/evals/` are separate evaluations. Do not start a session or call a tool.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: the pages could not be read far enough. Name what you tried.

```yaml
evaluation: mcp-exposure
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
checks:
  - id: mcp-documented
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: remote-endpoint
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: registry-entry
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
summary: <a few sentences>
gaps: []
```

`gaps` lists missing observables, one sentence each. Begin by confirming the origin URL, then run the procedure.
