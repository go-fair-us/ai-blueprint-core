# Open Knowledge Format (OKF) — NIAID Blueprint

## What OKF is

The **Open Knowledge Format (OKF)** is an open, human- and agent-friendly way
to store **knowledge**—not raw data files themselves, but the **metadata,
context, and curated insight** that sit around data and systems: what a
requirement means, how an API should behave, which identifier scheme to use,
how a metric is defined, and so on.

Physically, an OKF **knowledge bundle** is simple: a **directory of Markdown
files** with **YAML frontmatter**. There is no central schema registry and no
required proprietary runtime. If you can open a file in an editor or clone a
git repo, you can read and ship OKF.

That design formalizes the “LLM wiki” idea—many small, linkable notes agents
can write and maintain—into a **portable convention** so different producers
and consumers share the same layout without translating between custom formats.

Upstream materials:

- [OKF v0.2 specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
  ([GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog))
- [Introduction: how OKF can improve data sharing](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
- [OKF v0.2 trust signals](https://cloud.google.com/blog/products/data-analytics/okf-v0-2-adds-trust-signals)

## Goals OKF is trying to achieve

From the specification’s motivation, knowledge for AI agents should stay in
formats that are:

| Goal | Meaning in practice |
|------|---------------------|
| **Readable** | People can review concepts without a special client. |
| **Parseable** | Agents can load frontmatter + body without a bespoke SDK. |
| **Diffable** | Changes show up cleanly in version control. |
| **Portable** | Bundles move across tools, orgs, and time (git, zip, or a folder in a larger repo). |

As corpora become **agent-written**, plain markdown alone is not enough.
Consumers also need first-class answers to:

1. **Provenance** — What was this created from? (`sources`)
2. **Trust** — Who wrote it, and who confirmed it? (`generated` / `verified`)
3. **Freshness / lifecycle** — Is it still current? (`status`, `stale_after`)
4. **Attestation** (when needed) — Was a computed value produced the sanctioned way? (`type: Attested Computation`)

**OKF v0.2** makes those signals first-class in frontmatter while remaining
minimally opinionated. Body `# Citations` lists and the legacy `timestamp`
field from v0.1 are superseded (see SPEC §13).

**Explicit non-goals** of OKF include fixing a global taxonomy of concept
types, mandating a search or serving stack, or replacing domain schemas
(OpenAPI, schema.org JSON-LD, and so on). OKF *references* those; it does not
replace them.

## How a bundle is structured (in brief)

| Term | Meaning |
|------|---------|
| **Bundle** | Self-contained tree of Markdown documents (the unit of distribution). |
| **Concept** | One knowledge unit = one `.md` file with frontmatter + body. |
| **Concept ID** | Path of the file without `.md` (e.g. `metadata-schema/requirements`). |
| **`index.md`** | Directory listing for progressive disclosure (root may declare `okf_version`). |
| **`log.md`** | Chronological history of bundle updates. |

Every concept requires at least a `type` in frontmatter. Recommended fields
include `title`, `description`, `resource`, and `tags`. Cross-links between
concepts use ordinary Markdown links (prefer bundle-absolute paths like
`/metadata-schema/requirements.md`).

## What this repository uses OKF for

This `okf/` tree is **not** the OKF specification itself. It is an
**application of OKF** to the NIAID Blueprint program:

- Take the long, linear Blueprint Markdown document.
- **Extract atomic concepts** (single, source-backed claims).
- Group them into thematic concept files under a semantic directory tree.
- Ship that tree as a **conformant OKF v0.2 bundle** agents and tools can
  traverse, search, lint, visualize, or export (see `src/okf_core/`,
  `src/okf_quality/`, `src/okf2rdf/`, `src/visualize-okf/` elsewhere in this
  repo).

That gives AI agents a **structured knowledge layer** for FAIR / Blueprint
work—parallel to skills and prompts, but organized as a navigable concept
graph rather than one monolithic PDF or Markdown file.

## What was done in the example bundle

### Source

The primary source is the published Blueprint text:

`docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`

(listed in [`samples/niaid_blueprint/sources.txt`](samples/niaid_blueprint/sources.txt)).

### Extraction recipe

[`samples/niaid_blueprint/`](samples/niaid_blueprint/) holds a reusable recipe:

| File | Role |
|------|------|
| `extract.md` | Prompt: extract atomic concepts, group them, emit OKF v0.2 |
| `sources.txt` | Which documents to read |
| `README.md` | How to run in print mode vs write-to-disk mode |

The recipe forbids inventing claims: only statements supported by the source
text, with **line citations**. Output can be reviewed in chat (`print`) or
written under `bundles/` (`files`).

### Produced bundle: `bundles/niaid_blueprint/`

| Aspect | Detail |
|--------|--------|
| **OKF version** | `okf_version: "0.2"` on the root `index.md` |
| **Scale** | **239** globally numbered **atomic concepts** packed into **27** concept files (plus `index.md` / `log.md` at each level) |
| **Organization** | Semantic subdirectories aligned with Blueprint structure, not a flat dump |
| **Provenance** | Frontmatter `sources` + footnote attribution keyed to `sources[].id` |
| **Trust / lifecycle** | `generated` actors, `status: stable` (v0.2 migration recorded in `log.md`) |
| **History** | Created 2026-07-05 (v0.1); migrated to v0.2 on 2026-08-03 |

**Directory map** (from the root index):

| Subdirectory | Content focus |
|--------------|---------------|
| `overview/` | Background, scope, document status |
| `audience/` | Data generators and repository owners |
| `implementation/` | Collaborative development and Discovery Portal integration |
| `metadata-schema/` | Motivation, Table 1 requirements, impact |
| `persistent-identifiers/` | Motivation, PID requirements, impact |
| `api-specification/` | Motivation, API requirements, impact |
| `citation/` | Motivation, citation requirements, impact |
| `outreach-training/` | Motivation, outreach/training requirements, impact |
| `appendix/` | Supplemental tables, JSON-LD examples, ontology mappings, evaluated repositories |

Each thematic group file (for example
`metadata-schema/requirements.md`) typically holds:

- YAML frontmatter (`type`, `title`, `description`, `resource`, `tags`,
  `sources`, `generated`, `status`, plus producer fields such as
  `concept_range` / `source_lines`)
- A short prose summary with footnote links to the Blueprint source
- An **Atomic concepts** table (`#`, claim text, source line numbers)

So a consumer can open `index.md`, walk to `metadata-schema/`, open
`requirements.md`, and retrieve individual Table 1 claims with line-level
traceability—without re-parsing the entire Blueprint every time.

### Prompt examples (related, separate from the bundle)

[`prompt_examples/`](prompt_examples/) stores **filled** copies of Prompt
Library templates (placeholders replaced with NIAID-domain sample values such
as ImmPort studies). Those are ready-to-run prompt instances, not the OKF
concept extraction output; they sit next to the bundle as companion material
for library-optimizer and training workflows.

## Layout of this directory

| Path | Purpose |
|------|---------|
| [`samples/`](samples/) | Recipes — how to run concept extraction (`extract.md`, `sources.txt`, `README.md`) |
| [`bundles/`](bundles/) | Produced OKF knowledge bundles |
| [`prompt_examples/`](prompt_examples/) | Filled copies of Prompt Library templates (`{{placeholders}}` grounded in NIAID domain resources) |

## Specification pointers

Bundles follow [OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
from [GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog).

v0.2 makes provenance (`sources`), trust (`generated` / `verified`), and lifecycle
(`status` / `stale_after`) first-class in frontmatter. Body `# Citations` lists
and the legacy `timestamp` field are superseded (see SPEC §13).

## Current bundles

- [`bundles/niaid_blueprint/`](bundles/niaid_blueprint/) — 239 atomic concepts from
  `docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md` (27 concept files),
  `okf_version: "0.2"`

## Run extraction

See [`samples/niaid_blueprint/README.md`](samples/niaid_blueprint/README.md).

## Related tooling in this repository

| Path | Role |
|------|------|
| `src/okf_core/` | Parse and walk OKF v0.2 bundles |
| `src/okf_quality/` | Lint, shapes, SPARQL packs, rule catalogs |
| `src/okf2rdf/` | Export a bundle toward schema.org-centered RDF |
| `src/visualize-okf/` | HTML / graph views of a bundle |
| `src/libraryOptimizer/` | GEPA optimization over filled prompt examples |
