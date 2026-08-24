# Blueprint MCP Server

This package is a small **knowledge server** for the NIAID Blueprint for Digital
Objects. It does not assess a repository or mint metadata by itself. Instead it
makes the material already in this repository—**Blueprint Markdown under
`docs/`**, **OKF knowledge bundles under `okf/`**, and **prompt personas under
`prompts/`**—available to any AI client that speaks the **Model Context
Protocol (MCP)** over HTTP.

In plain terms: when an agent or chat tool is connected to this server, it can
**look up** the Blueprint, **navigate the OKF concept graph** (atomic claims
with line citations), **search** related docs, **navigate** by section or FAIR
pillar, and **start structured interviews** (FAIR assessment, crawl-style web
assessment, work-plan intake) whose wording lives in the prompt files. The
server is the bridge between “files in a git repo” and “tools an agent can call
mid-conversation.”

It also lists the `niaid-bp-*` Agent Skills and can run the bundled SHACL
validator. Interview skills stay procedures (`read_skill` + follow `SKILL.md`);
they are not one MCP tool per question.

It exposes four MCP surface areas:

1. **Resources** — read-only documents, OKF concepts, and prompt text by URI.
2. **Tools** — model-invoked functions to list and read docs, hybrid-search the
   corpus (including `collection="okf"`), pull a Blueprint or OKF requirements
   pillar, fetch atomic claims, list prompts / prompt examples, and (with
   `TAVILY_API_KEY`) inspect a live URL or search the public web.
3. **Prompts** — user-invoked personas (interview or web assessor flows) with
   optional arguments such as a target URL; arguments are prepended as a short
   instruction block so they override example values in the files.
4. **Skills** — catalog and progressive file reads for `niaid-blueprint/skills`,
   plus `validate_dataset` for host-side SHACL.

Everything is **read-only** with respect to the corpus: the server serves and
searches content; it does not write back into `docs/`, `okf/`, or `prompts/`.
Content roots default to the sibling directories in this repository and can be
overridden with environment variables (see Configuration below).

### When to use docs vs OKF

| Need | Prefer |
|------|--------|
| Full narrative Blueprint text / section wording | `get_blueprint_section`, `docs://…` |
| Claim-level obligations with source line numbers | `get_okf_atomic`, `list_okf_atomics`, `search_docs(collection="okf")` |
| Pillar requirements as a structured checklist | `get_okf_requirements` (atomics) vs `get_blueprint_requirements` (prose) |
| Filled domain few-shot prompts (ImmPort, etc.) | `list_okf_prompt_examples` |
| Interactive FAIR / work-plan interviews | MCP prompts (`fair_assessment_interview`, …) |

## What it exposes

### Resources (read-only context)

| URI | Description |
|-----|-------------|
| `docs://list` | JSON listing of all Markdown files under `../docs` |
| `docs://{path}` | Raw Markdown of a doc by relative path |
| `blueprint://spec` | The canonical Blueprint specification |
| `prompts://list` | JSON listing of registered prompt personas |
| `prompts://{name}` | Raw text of a prompt persona (by name or filename) |
| `okf://bundles` | JSON listing of OKF knowledge bundles |
| `okf://bundles/{name}/list` | Concept catalog for a bundle |
| `okf://bundles/{name}/index` | Root `index.md` (progressive disclosure) |
| `okf://bundles/{name}/concept/{id}` | Raw concept Markdown |
| `okf://bundles/{name}/atomic/{n}` | Single atomic claim (JSON) |
| `okf://prompt_examples/list` | Filled prompt examples catalog |
| `okf://prompt_examples/{path}` | One filled prompt example |

Resources are also available as tools via the `list_resources` / `read_resource`
tools generated automatically by the `ResourcesAsTools` transform, so clients
that don't support the MCP resources protocol (e.g. Claude Code) can still
access all content.

### Tools (model-invoked)

All tools carry `readOnlyHint` and `idempotentHint` annotations, enabling safe
client-side caching and retry.

#### Discovery

| Tool | Parameters | Purpose |
|------|-----------|---------|
| `list_docs()` | — | Enumerate available Markdown docs (path, title, bytes) |
| `read_doc(path)` | `path: str` | Read a doc's full Markdown content |
| `kb_stats()` | — | Corpus statistics: doc counts, total size, section count, OKF, skills, semantic search status |
| `list_resources()` | — | Auto-generated: list all MCP resources as tools |
| `read_resource(uri)` | `uri: str` | Auto-generated: read a resource by URI |

#### Search

| Tool | Parameters | Purpose |
|------|-----------|---------|
| `search_docs(query, collection, max_results)` | `query: str`, `collection: "docs"\|"prompts"\|"okf"\|None`, `max_results: int=10` | Hybrid BM25 + semantic search. Omit `collection` for docs+prompts; use `"okf"` for concept/atomic claims. |
| `get_context_window(source, path, line, radius)` | `source: str`, `path: str`, `line: int`, `radius: int=10` | Expand line-level context around a fuzzy-search hit |

#### Live web (Tavily)

Requires `TAVILY_API_KEY`. These call Tavily’s HTTP APIs from this server. They
are **not** LibreChat native Web Search and **not** Tavily’s hosted MCP.

| Tool | Parameters | Purpose |
|------|-----------|---------|
| `inspect_url(url, question, max_pages)` | `url: str`, `question: str`, `max_pages: int=3` (1–3) | Extract the URL (chunks ranked by `question`), same-host search, extract up to two extra pages. Returns a truncated evidence pack. Call once, then Blueprint tools. |
| `web_search(query, max_results)` | `query: str`, `max_results: int=5` (1–5) | Titles, URLs, snippets. Use when the user did not give a URL, then `inspect_url` on the best hit. |

#### Blueprint navigation

| Tool | Parameters | Purpose |
|------|-----------|---------|
| `list_blueprint_sections()` | — | List all Blueprint headings (level, number, title) |
| `get_blueprint_section(section)` | `section: str` | Extract one section by number (`"3"`, `"2.1"`) or heading keyword |
| `get_blueprint_requirements(pillar)` | `pillar: str\|None` | Return requirement sections for a FAIR pillar: `"metadata"`, `"identifiers"`, `"api"`, `"citation"`, `"outreach"`. Omit for a summary index of all pillars. |
| `blueprint_citation(section)` | `section: str\|None` | Canonical raw GitHub citation URL (+ optional section title/number) |

#### OKF (Open Knowledge Format)

| Tool | Parameters | Purpose |
|------|-----------|---------|
| `list_okf_bundles()` | — | Enumerate bundles under `okf/bundles` |
| `list_okf_concepts(...)` | `bundle`, `type`, `prefix`, `tag`, `normative` | Catalog concepts (no body) |
| `read_okf_concept(concept_id, …)` | `concept_id`, `bundle`, `include_body` | Structured concept + atomics |
| `get_okf_atomic(number)` | `number: int` | One atomic claim + source lines |
| `list_okf_atomics(...)` | `parent_id`, `query`, `max_results` | Filter atomic claims |
| `get_okf_requirements(pillar)` | same pillars as Blueprint tools | Requirements concepts + atomics |
| `get_okf_related(concept_id)` | — | Outbound / inbound concept links |
| `okf_stats()` | `bundle` optional | Concept/atomic counts and types |
| `list_okf_prompt_examples()` | — | Filled few-shot prompt files |
| `read_okf_prompt_example(path)` | relative path | Read one filled example |

#### Agent Skills

| Tool | Parameters | Purpose |
|------|-----------|---------|
| `list_skills()` | — | Catalog `SKILL.md` bundles (name, description, `when_to_use`, scripts/references/assets flags) |
| `read_skill(name)` | `name: str` | Full `SKILL.md` procedure |
| `read_skill_file(name, path)` | skill name + relative path | Progressive read of `references/`, `assets/`, or scripts (path-safe) |
| `validate_dataset(graph, data_format)` | JSON-LD or Turtle **text** | Run `niaid-bp-validation` SHACL on a `schema:Dataset` graph |

These tools do **not** re-encode interview skills as one function per question. Load the skill, then follow it. `validate_dataset` is the exception: the SHACL runner is a host script a browser UI cannot execute.

OKF parsing reuses `src/okf_core` (`walk_bundle`, atomic tables). Default bundle:
`niaid_blueprint` (239 atomics in the live repo tree).

#### Prompts

| Tool | Purpose |
|------|---------|
| `list_prompts()` | List registered prompt personas and their arguments |

### Prompts (user-invoked)

| Name | Arguments | Purpose |
|------|-----------|---------|
| `fair_assessment_interview` | — | Structured 6-phase interview → prioritized gap report |
| `fair_self_assessment` | — | Verbose pillar-by-pillar Blueprint self-assessment |
| `fair_self_assessment_short` | — | Concise pillar-by-pillar Blueprint self-assessment |
| `fair_web_assessor` | `url` (required), `blueprint_url` (optional) | Fetch a web resource and score it against the Blueprint |
| `fair_crawl_assessor` | `url` (required), `blueprint_url` (optional) | Crawl the top page + key first-level links and score per-principle against the Blueprint (JS pages via a headless tool or the `r.jina.ai` fallback) |
| `work_plan_interview` | `repo_name` (optional) | Intake interview → FAIRification Work Plan |

Prompts with arguments prepend a short **instruction block** to the persona
body so the supplied values override any example values in the file.

## Search architecture

`search_docs` uses a two-signal hybrid approach:

1. **BM25** (`rank-bm25`) — keyword relevance over section-level chunks. Fast,
   no model download required. Handles exact terminology, identifiers, and
   multi-word queries with IDF weighting.

2. **Semantic embeddings** (`fastembed`, optional) — dense vector similarity
   using `BAAI/bge-small-en-v1.5` (33 MB ONNX model, no PyTorch required).
   Handles synonyms, paraphrase, and conceptual queries.

Both signals are fused via **Reciprocal Rank Fusion (RRF)**:
`score = Σ 1/(60 + rank_i)` — documents ranked highly by *either* signal
surface near the top.

The corpus is chunked at **section boundaries** (using the Blueprint's Markdown
headings), so each result maps to a coherent unit of content rather than an
arbitrary line window.

The search index is built lazily on the first query and cached for the process
lifetime.

## Install

```bash
# From the repository root
uv sync --extra mcp
```

## Run (HTTP)

```bash
# Run as a module (the package uses relative imports, so use -m, not a file path)
uv run --extra mcp python -m mcp_bp.server
```

The server listens on `http://127.0.0.1:8000/mcp` by default.

## Configuration

| Env var | Default | Description |
|---------|---------|-------------|
| `MCP_HOST` | `127.0.0.1` | Bind host |
| `MCP_PORT` | `8000` | Bind port |
| `MCP_PATH` | `/mcp` | HTTP endpoint path |
| `BLUEPRINT_DOCS_DIR` | `../docs` | Docs content root |
| `BLUEPRINT_PROMPTS_DIR` | `../prompts` | Prompts content root |
| `BLUEPRINT_OKF_BUNDLES_DIR` | `../okf/bundles` | OKF bundles parent directory |
| `BLUEPRINT_OKF_DEFAULT_BUNDLE` | `niaid_blueprint` | Default bundle name |
| `BLUEPRINT_OKF_PROMPT_EXAMPLES_DIR` | `../okf/prompt_examples` | Filled prompt examples root |
| `BLUEPRINT_OKF_ENABLED` | `1` | Set to `0` to disable OKF tools/index |
| `BLUEPRINT_SKILLS_DIR` | `../niaid-blueprint/skills` | Agent Skill bundle root (`SKILL.md` directories) |
| `BLUEPRINT_SEMANTIC_ENABLED` | *(off)* | Set to `1` to enable embedding-based semantic search (downloads ~33 MB model on first run) |
| `BLUEPRINT_SEMANTIC_MODEL` | `BAAI/bge-small-en-v1.5` | fastembed model name for semantic embeddings |
| `TAVILY_API_KEY` | *(unset)* | Enables `inspect_url` and `web_search`. Placeholder values like `replace-me` count as unset. |
| `TAVILY_API_BASE` | `https://api.tavily.com` | Override only for tests. |
| `TAVILY_TIMEOUT` | `30` | HTTP timeout in seconds |

## Test

```bash
uv run --extra mcp --with pytest pytest mcp_bp/tests
```

## Notes

- Only Markdown (`.md`) files are served; other files (`.pdf`, `.docx`, etc.)
  are ignored.
- BM25 search is always active when `rank-bm25` is installed (included in the
  `mcp` extra). Semantic search is opt-in via `BLUEPRINT_SEMANTIC_ENABLED=1`
  to avoid surprise model downloads.
- The `ResourcesAsTools` transform bridges the MCP resources protocol gap:
  clients that support only tools still get full read access to the corpus.
