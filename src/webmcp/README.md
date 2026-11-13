# WebMCP handbook

Static HTML pages about the NIAID Blueprint for Digital Objects, plus Chrome
**WebMCP** tools that search, look up, and navigate those pages.

This is a local test fixture. It is not the OKF bundle and not the MCP knowledge
server in `mcp_bp/`. For a tree/reader over the real
`okf/bundles/niaid_blueprint/` files, use `okf/webmcp/` (port 8089).

## Serve

WebMCP needs a [secure context](https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts)
and an origin-keyed document. Use the small server so the right headers are set:

```bash
python webmcp/serve.py
```

Then open http://127.0.0.1:8088/

`--host` and `--port` override the defaults (`127.0.0.1`, `8088`). Bind to
localhost, not a LAN address: `http://192.168.x.x` is not a secure context.

The handler sends:

- `Origin-Agent-Cluster: ?1`
- `Permissions-Policy: tools=(self)`

`python -m http.server` from this directory will render the pages, but Chrome
may reject `document.modelContext.registerTool()` with `SecurityError` if the
document is not origin-isolated.

## Chrome setup

1. Chrome 149+ (origin trial) or any build with the flag.
2. Open `chrome://flags/#enable-webmcp-testing`, set **Enabled**, relaunch.
3. Load http://127.0.0.1:8088/ — the header badge should read **WebMCP available**.
4. Optional: [Model Context Tool Inspector](https://chromewebstore.google.com/detail/model-context-tool-inspec/gbpdfapgefenggkahomfgkhfehlcenpd)
   to list and call tools the way an in-browser agent would. Gemini in Chrome is
   the production agent path.

The in-page **WebMCP tester** calls `getTools()` and `executeTool()` without
Gemini. Use it to confirm registration and JSON input.

## Pages

| URL | Content |
|-----|---------|
| `/` | Handbook home, three goals, topic cards, tester |
| `/chatbp.html` | Chat over the topic index: search, then a short narrative with links |
| `/topics/overview.html` | What the Blueprint is and the five areas |
| `/topics/metadata.html` | Minimum metadata elements (schema.org-oriented) |
| `/topics/persistent-identifiers.html` | DOI, ORCID, ROR, RRID, ontologies |
| `/topics/apis.html` | JSON-LD, resource IRIs, GET, OpenAPI, fallbacks |
| `/topics/citation.html` | Citation guidance plus a declarative citation form |
| `/topics/outreach.html` | Contact Point and training materials |

Topic prose is paraphrased from themes in `okf/bundles/niaid_blueprint/`.
Shared JSON in `data/` feeds both the HTML tables and the tools, so they cannot
drift. There are no OKF frontmatter files and no atomic claim tables here.

## WebMCP tools

API: `document.modelContext` (fallback `navigator.modelContext` if present).

**On every page**

| Tool | Action |
|------|--------|
| `list_topics` | Catalog of handbook pages |
| `search_topics` | Keyword search over titles, summaries, keywords |
| `get_topic` | One topic by slug, including excerpt |
| `navigate_to_topic` | `location.assign` to that page |

**Page-specific**

| Page | Tools |
|------|--------|
| Metadata | `list_metadata_elements`, `get_metadata_element` |
| Identifiers | `list_pid_schemes`, `lookup_pid_scheme` |
| APIs | `get_api_objectives` |
| Citation | Imperative `format_citation`; declarative form `format_citation_form` |

Try in the tester (home page, WebMCP enabled):

- `search_topics` with `{"query":"DOI"}`
- `get_topic` with `{"slug":"metadata"}`
- `navigate_to_topic` with `{"slug":"citation"}`
- on the citation page, `format_citation` with author, year, title, repository, style

## Chat (`/chatbp.html`)

A chat UI over the same four site tools. It does **not** list tool names or JSON.
Each question:

1. `search_topics` over the handbook catalog in `data/topics.json` (paraphrased from the OKF bundle).
2. `get_topic` for the top hits, so the answer has the page excerpt.
3. A short narrative, plus **Read more** cards that link to the topic pages.

If Chrome WebMCP is available the chat calls `document.modelContext.executeTool`.
Otherwise it uses the same catalog functions the tools wrap.

When `XAI_API_KEY` is set (environment or a gitignored `.env` next to this
directory or the repo root), `serve.py` posts the retrieved passages to
`https://api.x.ai/v1/responses` (`grok-4.6` by default, override with
`BLUEPRINT_CHAT_MODEL`). The key stays on the server. Without a key the chat
still answers from the retrieved excerpts.

```bash
export XAI_API_KEY=…          # optional, for model-written narratives
python webmcp/serve.py
# http://127.0.0.1:8088/chatbp.html
```

## Layout

```
webmcp/
  serve.py              # stdlib HTTP server + WebMCP headers + /api/narrative
  index.html
  chatbp.html           # chat UI over the four site tools
  css/site.css
  css/chatbp.css
  js/                   # catalog, layout, WebMCP helpers, tools, tester, chatbp
  data/                 # topics, metadata elements, PID schemes, API objectives
  topics/               # handbook pages
```

## What this is not

- Not a copy of `okf/` (no YAML atomics, no line citations).
- Not `mcp_bp/` (no Model Context Protocol server, no OKF search).
- Not a public origin-trial deployment (no trial token).
