# Blueprint Metadata Extractor

## Why this exists

The [NIAID Blueprint for Digital Objects](BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md) asks repositories and data generators to describe digital objects with a **minimal set of metadata** (Table 1). Those elements—name, description, DOI, authors, funders, license, access conditions, and a handful of infectious-disease-relevant fields—should be expressed as **schema.org** records, ideally as **JSON-LD**, so machines (including the NIAID Data Ecosystem Discovery Portal) can find and reuse them.

In practice, most of that information already lives on a **public landing page**: a study summary in ImmPort, a DOI page, a repository record. What is missing is not always the facts, but the **structured, PID-normalized form**. Filling a long form by hand is slow. Interviewing a person is right when only they know the answers. When a good web page is already online, a language model with web access can **read the page, map what it finds to Blueprint Table 1, and draft the JSON-LD** for you.

That is what this document describes: **URL-driven metadata extraction**—no questionnaire, no FAIR gap report—just the best evidence-based `Dataset` (or related) record the page supports, plus honest notes about what was found, inferred, or missing.

## What you get, in plain terms

You point the agent at a single resource URL (for example a study page). It:

1. Loads the **Blueprint** and a worked **example JSON-LD** record (from GitHub raw URLs, so structure and field conventions stay aligned with this repo).
2. Fetches the **target page** (and, if needed, a JavaScript-rendered fallback).
3. Walks a fixed **five-phase extraction workflow**: understand the resource → map Table 1 elements → normalize PIDs and ontology terms → assemble JSON-LD → self-check.
4. Returns three things you can use immediately:
   - a short **resource summary**
   - a fenced **JSON-LD** document
   - **metadata notes** (found / inferred / missing / unresolved PIDs / confidence)

The draft is meant to be **reviewed and improved**, not treated as perfect. The agent is instructed never to invent DOIs, ORCIDs, grants, or ontology IDs; when a PID is not on the page, it keeps the human-readable value and flags the gap.

## Two paths to the same kind of record

This repository offers two complementary ways to produce Blueprint-aligned JSON-LD. Both aim at schema.org `Dataset` metadata; they differ in **who supplies the evidence**.

| Path | Skill / mechanism | Evidence source | Best when… |
|------|-------------------|-----------------|------------|
| **Extract (this doc)** | `niaid-bp-metadata-extract` + `references/extraction-workflow.md` | Public web page (optional related links) | You have a landing-page URL and want a fast draft |
| **Intake** | `niaid-bp-dataset-intake` | You, in a short conversational interview | Facts are not on the web, or you need authors/ORCIDs the page never lists |

**Extract** does not ask clarifying questions except when the URL is missing or unreachable. **Intake** walks five groups (identity, provenance, content, access, context) and can help look up ORCIDs, RORs, and ontology terms. Many teams use extract first, then intake (or hand edits) to fill the blanks the page could not supply.

Downstream you can **validate** a draft with `niaid-bp-validation` (SHACL / pySHACL), or run the automated **extract → validate → repair** loop in `src/genMeta/` when Herdr and Pi are available.

## How the extract path works

The “prompt” for extraction is not a free-form chat persona alone. It is a **procedure** living in:

`skills/niaid-bp-metadata-extract/references/extraction-workflow.md`

The Claude Code skill `niaid-bp-metadata-extract` loads that workflow, substitutes the target URL, fetches references, and enforces the output shape. Outside Claude Code, the same Markdown file is a **standalone system procedure**: paste it into any web-capable model, set the resource URL, and fetch the same two GitHub raw documents.

Rough flow:

```text
Resource URL
    │
    ├─► Fetch Blueprint (Table 1 + PID conventions)
    ├─► Fetch example.json (structural patterns)
    └─► Fetch landing page (r.jina.ai if the page is a JS shell)
              │
              ▼
    Five-phase workflow (understand → map → normalize → assemble → check)
              │
              ▼
    Resource summary + JSON-LD + Metadata notes
```

Phases in a little more detail:

1. **Understand** — What digital object is this? Dataset by default for research data. Landing URL vs identifier. Open / registered / controlled access.
2. **Map Table 1** — Pull every element with on-page evidence; omit empty fields rather than inventing them.
3. **Normalize** — DOIs as `https://doi.org/…`, ORCIDs, RORs, NCBITaxon / MONDO / NCIT IRIs, SPDX licenses when clear.
4. **Assemble** — One JSON-LD document following the example’s patterns (`@context`, `PropertyValue` for DOIs, arrays for multi-valued fields).
5. **Self-check** — Valid JSON, no fabricated IDs, values traceable to the page.

This is **not** a FAIR assessment. Assessors (`fair_web_assessor`, `fair_crawl_assessor`, the interview prompts) *score* alignment. Extraction *builds a candidate record*. Use assessment when you want gaps and priorities; use extraction when you want machine-readable metadata.

---

## Claude Code skill (recommended)

Use the **`niaid-bp-metadata-extract`** skill in `skills/niaid-bp-metadata-extract/`. It loads the extraction workflow from `references/extraction-workflow.md`, fetches authoritative references from GitHub raw URLs, retrieves the target page, and produces a JSON-LD record plus metadata notes.

**Invoke:**

```
/niaid-bp-metadata-extract https://immport.org/shared/study/SDY998
```

Or paste a URL in natural language: "extract Blueprint metadata from https://…"

The skill requires a **resource URL** (skill argument or user message). If none is provided, it asks once and waits.

If the target page is JavaScript-heavy, blocked, or returns poor text, the skill retries via `https://r.jina.ai/<URL>` (same fallback pattern used by the FAIR crawl assessors).

## Standalone system prompt

For a web-retrieval-capable LLM outside Claude Code, use the extraction workflow in:

`skills/niaid-bp-metadata-extract/references/extraction-workflow.md`

Before running, substitute `{{RESOURCE_URL}}` with the target URL. Fetch these authoritative references from GitHub (do not rely on local copies):

1. **Blueprint specification**  
   https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md

2. **Example metadata record**  
   https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/example.json

**Minimal user message:**

```text
Extract Blueprint-compliant metadata for:
https://immport.org/shared/study/SDY998
```

Or, using an explicit session-parameter block (same pattern as MCP prompt args for assessors such as `fair_web_assessor` — those tools *score* FAIR alignment; they do not extract JSON-LD):

```markdown
> **Session parameters for this run:**
> - Resource Url: https://immport.org/shared/study/SDY998
> Use the parameters above as the authoritative inputs for this session.

Extract metadata for the resource URL above.
```

There is currently **no dedicated MCP prompt** for metadata extraction; use the skill or the standalone workflow above. MCP does expose Blueprint docs tools and FAIR assessor prompts under `mcp_bp/`.

## Output

Three sections (defined in the extraction workflow):

1. **Resource summary** — what the resource is and any retrieval limitations
2. **Extracted metadata record** — fenced `json` code block with JSON-LD only
3. **Metadata notes** — Found / Inferred / Missing / Unresolved PIDs / Confidence

## Related artifacts

- Blueprint spec (raw): https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md
- Example record (local): `docs/example.json`  
  (raw): https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/example.json
- Interview-based alternative: `skills/niaid-bp-dataset-intake/` (user provides values, no web fetch)
- Validate extracted JSON-LD: `skills/niaid-bp-validation/` (`uv sync --extra validation`)
- Automated extract → SHACL → repair loop: `src/genMeta/` (Herdr + Pi; see `src/genMeta/README.md`)
- Skill index: `skills/README.md`
