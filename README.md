# ai-blueprint-core

This project provides AI agent tools that help NIAID-funded data repositories apply the [NIAID Blueprint for Digital Objects](https://datascience.niaid.nih.gov/resources).

The Blueprint is a FAIR data program from NIAID/ODSET. It defines minimal metadata schemas, persistent identifiers (PIDs), API standards, and citation practices for research data repositories.

The agents are LLM-driven and guided by structured prompt personas. They help repository owners and staff assess and apply Blueprint requirements in five areas:

1. **Metadata schema**: schema.org-based metadata elements for digital objects
2. **Persistent identifiers**: DOIs, ORCIDs, RORs, RRIDs, and ontology terms
3. **APIs and machine access**: JSON-LD endpoints, OpenAPI documentation, structured data
4. **Citation guidance**: PID-based citation examples in standard formats
5. **Outreach and training**: Contact Points, training materials, Portal onboarding

## What is in this repository

The main deliverables are written content: agent skills, prompts, and a knowledge bundle. Python tooling supports them. There is no single application. Each part has its own entry point.

| Part | Path | What it is |
|------|------|------------|
| Agent plugin and skills | `niaid-blueprint/` | 12 `niaid-bp-*` Agent Skills (FAIR assessment, dataset metadata intake, metadata extraction, citation, SHACL validation, API and website checks, and others), packaged as an agent plugin. Catalog: [`niaid-blueprint/skills/README.md`](niaid-blueprint/skills/README.md) |
| MCP knowledge server | `mcp_bp/` | Read-only Model Context Protocol server. Any MCP client can use it to search the Blueprint, OKF concepts, prompts, and skills, and to validate a `Dataset` graph. See [`mcp_bp/README.md`](mcp_bp/README.md) |
| Prompts | `prompts/` | Standalone prompts you can paste into any LLM chat (see below) |
| Evaluation procedures | `prompts/evals/` | 23 single-question checks of a repository website, such as sitemap, `robots.txt`, `llms.txt`, Dataset JSON-LD, and OpenAPI discovery |
| OKF knowledge bundle | `okf/` | Blueprint requirements as linked [OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) Markdown concepts, with atomic claims that cite source line numbers |
| Python tooling | `src/` | Metadata extraction and repair pipelines (genMeta, CEDAR), OKF parsing, RDF export and quality checks, and DSPy prompt optimizers |
| Reference documents | `docs/` | The Blueprint and Work Plans converted to Markdown, plus example assessments |

[`AGENTS.md`](AGENTS.md) describes each part in more detail, with commands and test instructions.

## Getting started

Choose the route that fits how you work.

1. **Paste a prompt.** No installation is needed. Copy a file from `prompts/` into a chat with any capable model. The next section explains how.
2. **Run the skills in Pi.** `./bin/pi` loads the skill bundle into the [Pi](https://pi.dev) agent harness. [`HARNESS_QUICKSTART.md`](HARNESS_QUICKSTART.md) covers installation and model credentials.
3. **Connect an MCP client.** Start the knowledge server with `uv sync --extra mcp` and then `./bin/run_mcp.sh`. It listens at `http://127.0.0.1:8000/mcp`.

## Flipped Interaction Pattern

The flipped interaction pattern is a prompt, not an agent. It reverses the usual chat roles: the model asks the questions, and the user answers them.

| Prompt | Purpose |
|--------|---------|
| `fairAssessmentInterview.md` | Runs a six-phase interview to assess a repository's Blueprint alignment, then produces a gap report with ranked recommendations |
| `fairAssessorCrawl.md` | Crawls a repository's top page and key links, then scores it against the Blueprint with cited evidence |
| `workPlanInterview.md` | Interviews repository staff to draft a work plan; `workPlanSpec.md` defines the plan's structure |
| `contextPrompt.md`, `contextPromptShort.md` | Give a model Blueprint background before you ask it questions; these do not run an interview |

`fairAssessmentInterview.md` is long and verbose, and a shorter version would be easier to use.

Paste the document into your chat. Current models start the interview on their own and finish with a summary of your answers. The exchange can run long. To end it early, tell the model: "stop the interview and give me the summary now".

## Evaluation procedures

Each file in `prompts/evals/` asks one question about a public repository website and tells the model to report only what it opened. Paste a file into a chat along with the repository URL. In Pi, each procedure is also a slash command named after its file, for example `/robots-policy https://example.org/`.

## Requirements

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/) for environment and dependency management

Some parts need more. The Pi route needs Pi and a model provider credential. The `niaid-bp-shaclrules` skill needs Deno 2+. The extraction and optimizer pipelines need an LLM API key (see `AGENTS.md`).

## Setup

```bash
# Clone and install
git clone <repo-url>
cd ai-blueprint-core
uv sync
```

Optional extras add the dependencies for specific parts:

```bash
uv sync --extra mcp          # MCP knowledge server
uv sync --extra validation   # SHACL validation skill
uv sync --extra genmeta      # genMeta extraction pipeline
```

## Reference

The authoritative Blueprint specification is `docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`. It was converted from the PDF with `docling` and `marker-pdf`.

To give it to a model, use the GitHub raw link: https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md

## Dependencies

- [`docling`](https://github.com/docling-project/docling): structured document parsing and extraction
- [`marker-pdf`](https://github.com/VikParuchuri/marker): PDF-to-Markdown conversion

Both are ML-based libraries. Expect a large `.venv` and model downloads on the first run. The full dependency list, including `dspy`, `pyshacl`, and `fastmcp`, is in `AGENTS.md`.
