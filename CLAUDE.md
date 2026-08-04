# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

`ai-blueprint-core` builds AI agent tooling to help NIAID-funded data repositories implement the NIAID Blueprint for Digital Objects — a FAIR data initiative by NIAID/ODSET that specifies minimal metadata schemas, persistent identifiers, API standards, and citation practices.

The repository is **content-first, not code-first**: its primary deliverables are Claude Code *skills* and LLM *prompt personas*, not a Python application. The Python tooling that exists is for document conversion (PDF→Markdown) and for an LLM-driven document-analysis script. There is no `main.py` and nothing to "build" or "run" in the conventional sense.

## How the pieces fit together

The repo offers three ways to apply the Blueprint, layered from most to least integrated with Claude Code:

1. **Claude Code skills** (`skills/`) — the main deliverable. Skill directories use the `niaid-bp-` prefix. See below.
2. **Prompt personas** (`prompts/`) — standalone system prompts for the "flipped interaction" pattern: paste one into any modern LLM and it drives the conversation, interviewing the user and producing an artifact. These are model-agnostic (used outside Claude Code too).
3. **DSPy RLM script** (`secret/rv2.py`) — runnable Python that analyzes a directory of Markdown docs and writes a report. `secret/` is **gitignored** (contains source work-plan PDFs and outputs).

The same domain logic often appears in more than one layer (e.g. FAIR assessment exists as both the `niaid-bp-fair-assess` skill and the `fairAssessmentInterview.md` prompt). When changing assessment/intake behavior, check whether a parallel copy needs the same change.

## Claude Code skills (`skills/`)

Each skill follows the standard layout: a `SKILL.md` (frontmatter + persona + flow) plus `references/` (loaded on demand during the interview) and `assets/` (templates/skeletons). The skills are **interview-driven**: they ask one or two questions at a time and progressively load reference files rather than front-loading everything.

**Naming:** directory name = frontmatter `name` = slash command; pattern `niaid-bp-<activity>`. (`skills/hermes/` is a separate packaging path and is not under this convention.)

- **`niaid-bp-fair-assess`** — six-phase Blueprint FAIR assessment interview → prioritized gap report. Phases and question sets live in `references/interview-phases.md`; output uses `assets/report-template.md`. Priority rules (High/Medium/Low) are defined in the SKILL.
- **`niaid-bp-dataset-intake`** — conversational metadata interview across five element groups (identity, provenance, content, access, context) → valid schema.org `Dataset` JSON-LD. Element questions/formats in `references/element-guide.md`; JSON-LD assembly guided by `references/jsonld-structure.md` + `assets/blank-dataset.jsonld`. `references/pid-help.md` walks users through finding PIDs (ORCID, ROR, NCBITaxon, MONDO, SPDX).
- **`niaid-bp-metadata-extract`** — URL-driven metadata extraction: fetches a target resource page (Blueprint spec and example JSON from GitHub raw URLs), extracts Table 1 elements, and produces JSON-LD plus metadata notes. Workflow in `references/extraction-workflow.md`. Documented in `docs/metadataGeneration.md`.
- **`niaid-bp-citation`** — conversational interview for Blueprint Section 4 citation text and BibTeX (original deposits, reused data, repository-level citations, "How to Cite" drafts). Guidelines in `references/citation-guidelines.md`; optional save helper in `scripts/save_citation.py`.
- **`niaid-bp-model-influence`** — conversational interview for producing a Model Influence Statement (voluntary disclosure of ML model use in a research work), branching on whether a model was used → a markdown statement plus a one-paragraph acknowledgment summary. Mirrors the upstream [Model Influence Statement Generator](https://github.com/pengyin-shan/Model-Influence-Statement) by Pengyin Shan; bundles verbatim `statement-template.md` + `example-influence-statement.md`. Output rendering and timestamped file artifacts come from `scripts/save_statement.py` (stdlib only, tested in `tests/`).
- **`niaid-bp-teach`** — multi-session Blueprint teaching workspace (MISSION, HTML lessons, learning records, glossary, resources). Hands-on curriculum steps hand off to sibling skills.
- **`niaid-bp-validation`** — SHACL validation of `schema:Dataset` graphs with pySHACL. Bundled initial shape in `assets/blueprint-required.ttl` (required name/description/url); runner in `scripts/validate.py` (severity-aware `conforms`). Needs optional extra: `uv sync --extra validation`.

### genMeta (Herdr + Pi pipeline)

`src/genMeta/` orchestrates **Pi agents via Herdr** (not Hermes): extract JSON-LD from a URL → host pySHACL → repair until pass. See `src/genMeta/README.md`. Run: `uv sync --extra genmeta` then `uv run python src/genMeta/main.py --url …` with a running Herdr server.

### libraryOptimizer (GEPA on OKF prompt examples)

`src/libraryOptimizer/` optimizes one filled prompt from `okf/prompt_examples/` at a time with **DSPy GEPA** (no multi-optimizer compare). Seed = `# Prompt` body (YAML stripped); metric = LLM judge against local Blueprint + Work Plans (section-sliced). See `src/libraryOptimizer/README.md`. Run: `uv run python src/libraryOptimizer/main.py optimize --prompt okf/prompt_examples/… --gepa-budget 40`.

### OKF tooling (`okf_core`, `visualize-okf`, `okf2rdf`, `okf_quality`)

- **`src/okf_core/`** — shared OKF v0.2 parse/walk library (`walk_bundle`, `OKFDocument`, atomic tables).
- **`src/visualize-okf/`** — HTML / Gephi graph of a bundle (uses `okf_core`).
- **`src/okf2rdf/`** — export a bundle to schema.org-centered RDF (Turtle or JSON-LD; PROV/DCTERMS/okf:; atomics as `okf:AtomicConcept`).  
  Example: `PYTHONPATH=src/okf_core/src:src/okf2rdf/src python -m okf2rdf --bundle okf/bundles/niaid_blueprint --out /tmp/bundle.ttl`.
- **`src/okf_quality/`** — lint, SHACL shapes, SPARQL packs, and rule catalogs (P0–P3). See `src/okf_quality/README.md`.  
  Example: `PYTHONPATH=src:src/okf_core/src python -m okf_quality.scripts.okf_lint --bundle okf/bundles/niaid_blueprint`.

When editing a skill, keep the `SKILL.md` frontmatter (`name`, `description`, `when_to_use`) accurate — that text is what triggers the skill — and remember reference files are read mid-interview, so their structure is load-bearing.

## Prompts (`prompts/`)

- `fairAssessmentInterview.md` — standalone version of the FAIR assessment interview (flipped-interaction prompt).
- `contextPrompt.md` / `contextPromptShort.md` — Blueprint context primers for grounding a model.
- `workPlanInterview.md` / `workPlanSpec.md` — interview + spec for producing repository work plans.
- `fairAssessorAgentOpenCode.md` — pointer/config for the OpenCode agent variant (`.opencode/agent/fair-resource-assessor.md`).

## Development Commands

Uses [`uv`](https://docs.astral.sh/uv/) (Python 3.13).

```bash
uv sync                  # install/sync the environment
uv add <package>         # add a dependency

# Run the DSPy RLM document analyzer (gitignored; needs NRP_API_KEY or OPENROUTER_API_KEY)
uv run secret/rv2.py --prompt-file prompts/contextPrompt.md
uv run secret/rv2.py --prompt-file prompt.md --backend openrouter

# Serve the proof-of-concept interactive lesson
cd lesson && python -m http.server 8000   # then open http://localhost:8000
```

`rv2.py` does **not** read files from the sandbox filesystem — it injects host-side helpers (`list_markdown_files`, `read_markdown`, `grep_markdown`, `save_report`, `SUBMIT`) into the RLM's REPL globals. See `secret/USE.md`.

## Key Dependencies

- **`dspy`** — used by `secret/rv2.py` for the RLM (Recursive Language Model) document-analysis loop.
- **`docling`** / **`marker-pdf`** — PDF→Markdown conversion used to produce `docs/*.md` from Blueprint PDFs. Heavy ML libraries: expect a large `.venv` and model downloads on first run.

## Domain Context

The authoritative spec is `docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md` (converted from the PDF). Raw link for passing to a model: `https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`

The Blueprint's five areas drive nearly every skill/prompt: **metadata schema** (schema.org elements), **persistent identifiers** (DOI, ORCID, ROR, RRID, ontology terms), **APIs/machine access** (JSON-LD, OpenAPI), **citation**, and **outreach/training**. Repositories ultimately feed the **NIAID Data Ecosystem Discovery Portal**.
