# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Purpose

`ai-blueprint-core` builds AI agent tooling to help NIAID-funded data repositories implement the **NIAID Blueprint for Digital Objects** — a FAIR data initiative by NIAID/ODSET that specifies minimal metadata schemas, persistent identifiers, API standards, and citation practices.

The repository is still **content-first**: primary deliverables are agent *skills*, *prompt personas*, and an *OKF knowledge bundle*. It also ships substantial Python tooling: an MCP knowledge server, extract/validate pipelines, OKF parse/export/quality tools, and DSPy prompt optimizers. There is no single app entrypoint; each subsystem has its own CLI or server.

## How the pieces fit together

Layers from most integrated with agent harnesses to standalone scripts:

1. **Agent plugin + skills** (`niaid-blueprint/`) — installable skill bundle (`niaid-bp-*`) plus MCP client pointer. Main interactive deliverable.
2. **MCP knowledge server** (`mcp_bp/`) — serves Blueprint docs, OKF concepts/atomics, and prompt personas over HTTP so any MCP client can look up, search, and start interviews.
3. **Prompt personas** (`prompts/`) — standalone system prompts for the “flipped interaction” pattern (paste into any LLM). Model-agnostic; used outside skill loaders too.
4. **OKF knowledge layer** (`okf/`) — Blueprint requirements as an OKF v0.2 Markdown concept bundle (atomics with source line citations) plus filled prompt examples.
5. **Python pipelines & libraries** (`src/`, `mcp_bp/`) — genMeta extract/repair, OKF tools, GEPA/prompt optimizers, static prompt library UI.
6. **DSPy RLM script** (`secret/rv2.py`) — analyzes a directory of Markdown docs and writes a report. `secret/` holds source work-plan PDFs and local outputs (often gitignored material).

The same domain logic often appears in more than one layer (e.g. FAIR assessment as skill, prompt, and MCP prompt). When changing assessment/intake behavior, check parallel copies.

## Agent plugin (`niaid-blueprint/`)

Agent Plugins packaging for the NIAID Blueprint:

| File | Role |
|------|------|
| `plugin.json` | Plugin metadata (`name`: `niaid-blueprint`) |
| `mcp.json` | Points clients at the local Blueprint MCP server (`http://localhost:8000/mcp`) |
| `skills/` | The skill bundle (see below) |

### Skills (`niaid-blueprint/skills/`)

Each skill follows the standard layout: a `SKILL.md` (frontmatter + persona + flow) plus `references/` (loaded on demand) and optional `assets/` / `scripts/` / `tests/`. Skills are **interview-driven** or procedure-driven: they ask a few questions at a time (or fetch a URL) and progressively load references rather than front-loading everything.

**Naming:** directory name = frontmatter `name` = slash command; pattern `niaid-bp-<activity>`.

| Skill | What it does |
|-------|----------------|
| **`niaid-bp-fair-assess`** | Six-phase Blueprint FAIR assessment interview → prioritized gap report. Phases in `references/interview-phases.md`; template `assets/report-template.md`. |
| **`niaid-bp-dataset-intake`** | Conversational metadata interview (identity, provenance, content, access, context) → schema.org `Dataset` JSON-LD. Guides in `references/`; skeleton in `assets/blank-dataset.jsonld`. |
| **`niaid-bp-metadata-extract`** | URL-driven extraction of Table 1 elements → JSON-LD + metadata notes. Workflow in `references/extraction-workflow.md`. See `docs/metadataGeneration.md`. |
| **`niaid-bp-citation`** | Interview for Blueprint Section 4 citation text and BibTeX. Guidelines in `references/citation-guidelines.md`; optional `scripts/save_citation.py`. |
| **`niaid-bp-model-influence`** | Model Influence Statement interview (ML disclosure). Bundles template + example; `scripts/save_statement.py` (stdlib, tested). |
| **`niaid-bp-teach`** | Multi-session teaching workspace (MISSION, HTML lessons, learning records, glossary). Hands-on steps hand off to sibling skills. |
| **`niaid-bp-validation`** | SHACL validation of `schema:Dataset` graphs via pySHACL. Shape: `assets/blueprint-required.ttl`; runner: `scripts/validate.py`. Extra: `uv sync --extra validation`. |

When editing a skill, keep frontmatter (`name`, `description`, `when_to_use`) accurate — that text drives discovery — and treat mid-interview reference structure as load-bearing.

Catalog and cross-skill map: `niaid-blueprint/skills/README.md`.

> **Path note:** Skills previously lived at repo-root `skills/` (and briefly under other plugin dir names). They now live only under `niaid-blueprint/skills/`. Pipelines such as `src/genMeta/` must use that root for extract/validate skill files.

## MCP knowledge server (`mcp_bp/`)

Read-only **Model Context Protocol** server over HTTP. Bridges files in this repo to tools an agent can call mid-conversation. It does **not** assess repositories or mint metadata by itself.

**Surfaces:** resources (docs / OKF / prompts by URI), tools (list/read/search/navigate/OKF atomics), and user-invoked prompts (FAIR interview, web assessor, crawl assessor, work-plan intake).

```bash
uv sync --extra mcp
uv run --extra mcp python -m mcp_bp.server   # http://127.0.0.1:8000/mcp
uv run --extra mcp --with pytest pytest mcp_bp/tests
```

Hybrid search: BM25 + optional semantic embeddings (`BLUEPRINT_SEMANTIC_ENABLED=1`). Content roots overrideable via env (`BLUEPRINT_DOCS_DIR`, `BLUEPRINT_PROMPTS_DIR`, `BLUEPRINT_OKF_*`). Full tool table: `mcp_bp/README.md`.

## Prompt personas (`prompts/`)

| File | Purpose |
|------|---------|
| `fairAssessmentInterview.md` | Structured 6-phase FAIR/Blueprint interview → gap report |
| `fairAssessorCrawl.md` | Crawl top page + key links; score against Blueprint with evidence |
| `contextPrompt.md` / `contextPromptShort.md` | Blueprint context primers for grounding a model |
| `workPlanInterview.md` / `workPlanSpec.md` | Interview + spec for repository work plans |
| `fairAssessorAgentOpenCode.md` | Pointer/config for the OpenCode agent variant |

## OKF knowledge layer (`okf/`)

Application of [OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md): Markdown concept files with YAML frontmatter, atomic claims, and progressive `index.md` disclosure.

| Path | Contents |
|------|----------|
| `okf/bundles/niaid_blueprint/` | Blueprint requirements as linked concepts + atomic claims |
| `okf/prompt_examples/` | Filled few-shot domain prompts (ImmPort-style scenarios, etc.) |
| `okf/samples/` | Sample extract notes / sources |
| `okf/README.md` | What OKF is and how this repo uses it |

Prefer **docs/** narrative for full Blueprint wording; prefer **OKF atomics** for claim-level obligations with source line numbers.

## Python tooling (`src/` and related)

### genMeta (Herdr + Pi pipeline)

`src/genMeta/` — extract JSON-LD from a URL via **Pi agents over Herdr** (not Hermes) → host pySHACL → repair until pass (or budget). See `src/genMeta/README.md`.

```bash
uv sync --extra genmeta
uv run python src/genMeta/main.py --url …   # requires a running Herdr server
```

Uses the metadata-extract and validation skills (paths under `niaid-blueprint/skills/`).

### libraryOptimizer (GEPA on OKF prompt examples)

`src/libraryOptimizer/` — optimizes **one** filled prompt from `okf/prompt_examples/` with **DSPy GEPA**. Seed = `# Prompt` body (YAML stripped); metric = LLM judge against local Blueprint + Work Plans (section-sliced). See `src/libraryOptimizer/README.md`.

```bash
uv run python src/libraryOptimizer/main.py optimize --prompt okf/prompt_examples/… --gepa-budget 40
```

### promptOptimizer (multi-optimizer harness)

`src/promptOptimizer/` — DSPy harness comparing BootstrapFewShot / MIPROv2 / GEPA on Blueprint-oriented goals (API example vs Dataset JSON-LD profiles). Config-driven (`config/profile.yaml`, `config/profiles/`). Sibling of libraryOptimizer; more general bake-off. See `src/promptOptimizer/README.md` and `QUICKSTART.md`.

### promptLibrary (static UI)

`src/promptLibrary/` — static web app to browse/copy Blueprint-related prompts (`data.json`). Serve with any static HTTP server from that directory.

### OKF tooling (`okf_core`, `visualize-okf`, `okf2rdf`, `okf_quality`)

| Package | Role |
|---------|------|
| **`src/okf_core/`** | Shared OKF v0.2 parse/walk (`walk_bundle`, `OKFDocument`, atomic tables) |
| **`src/visualize-okf/`** | Interactive HTML / Gephi graph of a bundle |
| **`src/okf2rdf/`** | Export bundle → schema.org-centered RDF (Turtle or JSON-LD; PROV/DCTERMS/okf:; atomics as `okf:AtomicConcept`) |
| **`src/okf_quality/`** | Lint, SHACL shapes, SPARQL packs, rule catalogs (P0–P3). See `src/okf_quality/README.md` |

Examples:

```bash
PYTHONPATH=src/okf_core/src:src/okf2rdf/src python -m okf2rdf \
  --bundle okf/bundles/niaid_blueprint --out /tmp/bundle.ttl

PYTHONPATH=src:src/okf_core/src python -m okf_quality.scripts.okf_lint \
  --bundle okf/bundles/niaid_blueprint
```

Prebuilt RDF snapshots may live under `resources/` (`niaid_blueprint.ttl`, `niaid_with_atomics.ttl`). Oxigraph compose file: `deployment/docker-compose.oxigraph.yaml`.

## Docs and reference material (`docs/`)

| Path | Role |
|------|------|
| `docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md` | Authoritative Blueprint spec (from PDF) |
| `docs/WorkPlans/` | Work Plans supplementary material |
| `docs/metadataGeneration.md` | URL → metadata extraction story |
| `docs/assessments/` | Example FAIR assessment outputs |
| `docs/sources/` | Source PDF/DOCX inputs |
| `lesson/` | Proof-of-concept interactive lesson (static HTML) |

## Development commands

Uses [`uv`](https://docs.astral.sh/uv/) (Python 3.13+).

```bash
uv sync                         # base env
uv sync --extra mcp             # + MCP server deps
uv sync --extra validation      # + SHACL for skill validator
uv sync --extra genmeta         # + Herdr client + SHACL
uv add <package>

# MCP knowledge server
uv run --extra mcp python -m mcp_bp.server

# Tests
uv run --extra mcp --with pytest pytest mcp_bp/tests
uv run --with pytest pytest niaid-blueprint/skills/niaid-bp-validation/tests
uv run --with pytest pytest niaid-blueprint/skills/niaid-bp-model-influence/tests

# DSPy RLM document analyzer (needs NRP_API_KEY or OPENROUTER_API_KEY)
uv run secret/rv2.py --prompt-file prompts/contextPrompt.md
uv run secret/rv2.py --prompt-file prompt.md --backend openrouter

# PoC interactive lesson
cd lesson && python -m http.server 8000   # http://localhost:8000
```

`rv2.py` does **not** read files from the sandbox filesystem — it injects host-side helpers (`list_markdown_files`, `read_markdown`, `grep_markdown`, `save_report`, `SUBMIT`) into the RLM’s REPL globals. See `secret/USE.md`.

Optimizer / genMeta runs typically need `NRP_API_KEY` (default), or `OPENROUTER_API_KEY` / `XAI_API_KEY` / Ollama env vars depending on backend flags.

## Key dependencies

| Package / extra | Used for |
|-----------------|----------|
| **`dspy`** | RLM (`secret/rv2.py`), GEPA optimizers (`libraryOptimizer`, `promptOptimizer`) |
| **`docling`** / **`marker-pdf`** | PDF→Markdown for Blueprint/Work Plan docs |
| **`pyshacl`** / **`rdflib`** | Dataset SHACL validation, OKF RDF, quality shapes |
| **`fastmcp`**, **`rank-bm25`**, **`fastembed`** (extra `mcp`) | MCP server + hybrid search |
| **`herdr-python-client`** (extra `genmeta`) | Herdr transport for genMeta Pi agents |

Heavy ML libraries (docling, marker, optional fastembed) mean a large `.venv` and downloads on first run.

## Domain context

Authoritative spec: `docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`.

Raw GitHub link for models:

`https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`

The Blueprint’s five areas drive nearly every skill, prompt, and OKF concept:

1. **Metadata schema** (schema.org elements)
2. **Persistent identifiers** (DOI, ORCID, ROR, RRID, ontology terms)
3. **APIs / machine access** (JSON-LD, OpenAPI)
4. **Citation**
5. **Outreach / training**

Repositories ultimately feed the **NIAID Data Ecosystem Discovery Portal**.
