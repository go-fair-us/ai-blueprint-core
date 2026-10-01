# OKF WebMCP browser

A local **single-page reader** for the `niaid_blueprint` OKF bundle. Humans
browse the real Markdown tree. A search chat and Chrome **WebMCP** tools share
the same open document.

This is a local test fixture. It is **not** the paraphrased handbook in
repo-root `webmcp/` and **not** the MCP knowledge server in `mcp_bp/`.

## Serve

WebMCP needs a [secure context](https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts)
and an origin-keyed document. Use this server so the right headers are set:

```bash
python okf/webmcp/serve.py
```

Then open http://127.0.0.1:8089/

`--host`, `--port`, and `--bundle` override the defaults (`127.0.0.1`, `8089`,
`okf/bundles/niaid_blueprint`). Bind to localhost, not a LAN address:
`http://192.168.x.x` is not a secure context.

The handler sends:

- `Origin-Agent-Cluster: ?1`
- `Permissions-Policy: tools=(self)`

`python -m http.server` from this directory will render the shell, but Chrome
may reject `document.modelContext.registerTool()` with `SecurityError` if the
document is not origin-isolated, and `/data/index.json` / `/bundle/` will be
missing.

Needs **PyYAML** (used by `okf_core` to parse frontmatter). The repo `.venv`
already has it.

## Chrome setup

1. Chrome 149+ (origin trial) or any build with the flag.
2. Open `chrome://flags/#enable-webmcp-testing`, set **Enabled**, relaunch.
3. Load http://127.0.0.1:8089/ — the header badge should read **WebMCP available**.
4. Optional: [Model Context Tool Inspector](https://chromewebstore.google.com/detail/model-context-tool-inspec/gbpdfapgefenggkahomfgkhfehlcenpd)
   to list and call tools the way an in-browser agent would.

The in-page **chat** does not need an LLM or API key. It maps a free-form
sentence to one of the page tools (`search_okf`, `open_concept`, `get_atomic`,
and so on), then runs that tool. If WebMCP is available it uses
`document.modelContext.executeTool`; otherwise it calls the same JavaScript
the tools wrap. Example: “Show me material related to citation” →
`search_okf` with `pillar=citation`, and the reader opens the top hit.

The **WebMCP tester** (collapsed in the search pane) calls `getTools()` and
`executeTool()` when the API is present.

## What you see

| Pane | Role |
|------|------|
| Tree | Bundle directories, concept files, `index.md`, `log.md` |
| Reader | Frontmatter chips, rendered Markdown, atomic claim table, related links |
| Search chat | Free-form sentence → picks a WebMCP tool and shows hits; `#63` opens that atomic |

Hash routes (`#/metadata-schema/requirements`, `#/metadata-schema/requirements/atomic/63`)
are shareable. In-body `.md` links stay in the SPA.

Search facets in the chat (and as tool arguments):

| Token | Meaning |
|-------|---------|
| (free text) | Title, tags, description, atomics, body |
| `tag:doi` | Exact tag |
| `type:Requirements` | Substring on frontmatter type |
| `pillar:metadata` | FAIR pillar (`metadata`, `identifiers`, `api`, `citation`, `outreach`) |
| `kind:atomic` | Concepts, atomics, or index/log files |
| `normative:true` | Requirements flag |
| `#63` / `atomic 63` | Direct atomic lookup |

## WebMCP tools

API: `document.modelContext` (fallback `navigator.modelContext` if present).
All tools stay registered on this one page.

| Tool | Action |
|------|--------|
| `search_okf` | Faceted keyword search |
| `list_concepts` | Catalog with type / prefix / tag / normative filters |
| `open_concept` | Load a document into the reader (shared view) |
| `get_concept` | Structured concept JSON (does not navigate) |
| `get_atomic` | Atomic by number; opens the parent concept |
| `list_atomics` | Filter by parent id or substring |
| `get_related` | Outbound and inbound concept links |
| `get_current_document` | What the human is looking at |
| `list_facets` | Tags, types, pillars, stats |

Try in the tester (WebMCP enabled):

- `search_okf` with `{"query":"DOI"}`
- `open_concept` with `{"id":"metadata-schema/requirements"}`
- `get_atomic` with `{"number":63}`

## Tests

```bash
uv run --with pytest pytest okf/webmcp/tests
```

## Layout

```
okf/webmcp/
  serve.py              # stdlib HTTP server + WebMCP headers + /data + /bundle
  index_builder.py      # okf_core walk → JSON index/tree
  index.html            # SPA shell
  css/app.css
  js/                   # bundle, tree, reader, chat, WebMCP tools, tester
  tests/
```

The index is built in memory at process start from the bundle on disk. It is
not a committed JSON snapshot.

## What this is not

- Not a copy of the paraphrased handbook in `webmcp/` (port 8088).
- Not `mcp_bp/` (no Model Context Protocol server, no BM25/embeddings).
- Not an LLM chat. The search pane routes messages to `search_okf` / `open_concept` / `get_atomic`.
- Not a public origin-trial deployment (no trial token).
