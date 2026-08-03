# Prompt: Extract grouped atomic concepts into an OKF bundle

You are analyzing one or more source documents. Your task is to extract **atomic concepts**—self-contained facts or hypotheses explicitly stated in the document—and organize them into **upper-level thematic groups**. Output must conform to [Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

Do not invent, infer beyond the text, or paraphrase into new claims. If the document does not support a concept, omit it.

## Usage (read first)

Invoke this prompt with explicit **inputs**, an **output mode**, and (for file mode) an **OKF bundle output directory**.

**Single source, print to chat (testing):**

> Use `@okf/samples/niaid_blueprint/extract.md` on sources in `@okf/samples/niaid_blueprint/sources.txt`. Output mode: `print`. Show results; do not save files.

**Single source, write OKF bundle:**

> Use `@okf/samples/niaid_blueprint/extract.md` on sources in `@okf/samples/niaid_blueprint/sources.txt`. Output mode: `files`. Save OKF bundle to `okf/bundles/niaid_blueprint/`.

**Multiple sources:**

> Use `@okf/samples/niaid_blueprint/extract.md` on `@doc-a.md` and `@doc-b.md`. Output mode: `files`. Save to `okf/bundles/<bundle-name>/` with one subdirectory per source under the bundle root.

**Parameters to specify every run:**

| Parameter | Required | Example |
|-----------|----------|---------|
| Source(s) | Yes | paths from `sources.txt` or `@path/to/document.md` |
| Output mode | Yes | `print` or `files` |
| Output directory | Yes if `files` | `okf/bundles/niaid_blueprint/` |
| Prompt file | Optional | `okf/samples/niaid_blueprint/extract.md` (default) |
| Actor id | Optional | `<producer>/<version>` for `generated.by` (default: `niaid-bp-okf-extract/0.2`) |

## Input

- **Source document(s):** one or more line-numbered markdown files
- **Line-numbered text:** use each file's line numbers as printed (1-indexed). For multiple sources, qualify line numbers in the `Lines` column (e.g., `Blueprint.md:41`)
- **Output mode:** `print` | `files` (default `print`)
- **Output directory:** required when output mode is `files`
- **Actor id:** string for `generated.by` using the OKF actor convention (§7): `<producer>/<version>` for agents, `human:<id>` for people, `process:<id>` for processes

## Output modes

### Mode: `print` (testing / review)

Print all groups to the conversation. Do **not** create files.

### Mode: `files` (OKF bundle)

Write a conformant **OKF v0.2 knowledge bundle**: one markdown concept file per thematic group, `index.md` at each directory level, optional `log.md` at bundle root. Create directories as needed. After saving, print only a short summary (files written, concept/group counts).

## OKF bundle layout

Organize concepts in **semantic subdirectories** (no numeric filename prefixes). Concept ID = file path without `.md` (e.g., `metadata-schema/requirements`).

**Single-source bundle example:**

```
<output_dir>/
├── index.md
├── log.md                          # optional; recommended on first creation
├── overview/
│   ├── index.md
│   ├── document-status.md
│   ├── background.md
│   └── blueprint-scope.md
├── audience/
│   ├── index.md
│   ├── data-generators.md
│   └── repository-owners.md
├── implementation/
│   ├── index.md
│   └── approach.md
├── metadata-schema/
│   ├── index.md
│   ├── motivation.md
│   ├── requirements.md
│   └── impact.md
├── persistent-identifiers/
│   ├── index.md
│   ├── motivation.md
│   ├── requirements.md
│   └── impact.md
├── api-specification/
│   ├── index.md
│   ├── motivation.md
│   ├── requirements.md
│   └── impact.md
├── citation/
│   ├── index.md
│   ├── motivation.md
│   ├── requirements.md
│   └── impact.md
├── outreach-training/
│   ├── index.md
│   ├── motivation.md
│   ├── requirements.md
│   └── impact.md
└── appendix/
    ├── index.md
    ├── evaluated-repositories.md
    ├── metadata-schemas.md
    ├── portal-metadata-examples.md
    ├── ontology-mappings.md
    ├── iid-api-reference.md
    └── json-ld-examples.md
```

Derive subdirectories from the source document's structure. A pillar with Motivation / Requirements / Impact maps to `<pillar>/motivation.md`, `requirements.md`, `impact.md`. Appendix and supplemental tables go under `appendix/`.

**Multiple sources:** place each source's subtree under `<output_dir>/<source-slug>/` using the same internal layout. Write a bundle-root `index.md` linking to each source subdirectory.

## Concept document structure (per group)

Each group becomes one OKF concept file.

### YAML frontmatter (OKF §4–§5)

```yaml
---
type: <Human-readable type name>              # REQUIRED
title: <Display name>
description: <One-line summary>
resource: <Canonical URI for underlying asset, when available>
tags: [<tag>, <tag>]
status: stable                                # draft | stable | deprecated (§5.4)
generated: { by: <actor>, at: <ISO-8601> }    # (§5.2) who wrote this content
sources:                                      # (§5.1) provenance — replaces body # Citations
  - id: <stable-key>                          # used for per-claim footnote attribution
    resource: <absolute URL or path>
    title: <Human-readable source label>
    author: <optional actor for the source>
# Optional trust (when a human or process has confirmed the extraction):
# verified: { by: human:<id>, at: <ISO-8601> }
# Optional freshness:
# stale_after: YYYY-MM-DD
# Producer extensions (allowed; consumers preserve unknown keys):
source_document: <filename>
source_lines: <start>-<end>
section: <verbatim source section heading>
normative: <true|false>
concept_range: <first>-<last>
---
```

**`type` (REQUIRED)** — use human-readable OKF-style values (not centrally registered; consumers tolerate unknowns):

| Group role | Suggested `type` |
|------------|------------------|
| Document meta, background, motivation, impact | `NIAID Blueprint Section` |
| Normative requirements / Table 1-style specs | `NIAID Blueprint Requirements` |
| Supplemental tables | `Reference Table` |
| Portal/indexed examples | `Worked Example` |
| Living-document header | `Document Status` |

**`generated` (RECOMMENDED for agent-written content)** — `by` is an actor (§7); `at` is ISO 8601 for the last meaningful content change.

**`sources` (RECOMMENDED)** — list materials this concept derives from. Each entry MUST have `resource`. Include a stable `id` when the body attributes claims with footnotes. Optional credibility signals: `author`, `usage_count`, `last_modified` (and bundle-level or per-entry `usage_window`).

**`status`** — default when absent is `stable`. Prefer explicit `status: stable` for extracted specs; use `draft` only for incomplete extractions.

**`resource`** — prefer a real canonical URL for the source document when known (e.g., raw GitHub URL). Do not fabricate URLs.

**Extension keys** (`source_document`, `source_lines`, `section`, `normative`, `concept_range`) are producer-defined OKF extensions (§4.1).

Do **not** use `group_index`; ordering is expressed via `index.md` listings.

Do **not** use legacy v0.1 `timestamp` (use `generated.at`) or a body `# Citations` list (use `sources` + footnotes).

### Markdown body

```markdown
[Opening prose: synthesizing narrative grounded in atomic facts, no new claims.][^src-id]

[Optional bundle-relative cross-links to related concepts, e.g. Part of the [Blueprint scope](/overview/blueprint-scope.md).]

# Atomic concepts

| # | Concept | Lines |
|---|---------|-------|
| 1 | [Self-contained fact or hypothesis] | [line numbers] |

[^src-id]: [Source section title] (lines <start>–<end>)
```

- Opening prose replaces a separate `## Narrative` heading; use plain paragraphs or `# Overview` when helpful.
- `# Atomic concepts` holds the numbered fact table.
- **Per-claim attribution (OKF §5.1):** use markdown footnotes whose labels match `sources[].id`. Do **not** emit a `# Citations` body section (that was v0.1; superseded by `sources`).
- Footnote *prose* is human-readable; consumers join on the footnote label → `sources[].id`, not by parsing footnote text.

### Cross-linking (OKF §6)

Link related concepts with bundle-relative absolute paths (recommended form):

```markdown
See [Persistent Identifiers — Requirements](/persistent-identifiers/requirements.md).
```

Relative links (`./other.md`) are also valid. Consumers MUST tolerate broken links.

Add cross-links when groups are clearly related (pillar motivation → requirements → impact; requirements → appendix reference tables).

## Index files (OKF §8)

**Bundle-root `index.md`** — frontmatter allowed only for `okf_version` (§12):

```markdown
---
okf_version: "0.2"
---

# Subdirectories

* [overview](overview/index.md) - Background, scope, and document status
* [metadata-schema](metadata-schema/index.md) - Minimal metadata schema
…
```

**Subdirectory `index.md`** — **no frontmatter**. Body uses section heading + bullet list:

```markdown
# Metadata Schema

* [Motivation](motivation.md) - Why minimal metadata matters
* [Requirements](requirements.md) - Table 1 elements and formats
* [Impact](impact.md) - Expected integration benefits
```

Each entry: `* [Title](filename.md) - description` where description comes from the concept's `description` frontmatter.

## Log file (optional, OKF §9)

On bundle creation, write `log.md` at bundle root. Date headings MUST be ISO 8601 `YYYY-MM-DD`, newest first:

```markdown
# Bundle Update Log

## YYYY-MM-DD
* **Creation**: Initial extraction of N atomic concepts across M groups from <source> into OKF v0.2.
```

## Rules for upper-level groups

1. Derive groups from the document's structure and themes (major sections, Motivation/Requirements/Impact, supplemental tables).
2. One group = one coherent theme.
3. Split large sections with distinct sub-themes.
4. Exclude table-of-contents navigation, funding disclaimers unless substantive.
5. Include appendix material as its own groups under `appendix/`.

## Rules for atomic concepts

1. One concept = one idea (fact, requirement, definition, or stated expectation).
2. Self-contained — understandable without adjacent rows or the source.
3. Faithful to source terminology; do not upgrade "encouraged" to "required" unless the text does.
4. Line citations required on every row.
5. Tables: one concept per meaningful row/field when distinct.
6. Number concepts globally (1, 2, 3, …) across the full bundle.

## Rules for opening prose

1. Synthesize the group's purpose and scope; do not list table rows verbatim.
2. Every sentence supportable by concepts in the table.
3. No new facts beyond the source.
4. Scale length to group density.
5. Attribute the group to its source with a footnote keyed to `sources[].id`.

## Quality checks

- [ ] OKF §11: every non-reserved `.md` file has parseable frontmatter with non-empty `type`
- [ ] `index.md` files follow §8 (no frontmatter except `okf_version: "0.2"` at bundle root)
- [ ] Reserved filenames (`index.md`, `log.md`) not used for concept documents
- [ ] Semantic paths and filenames (no `01-` prefixes)
- [ ] Every concept has `sources` with at least one entry that has `resource`
- [ ] Every concept has `generated: { by, at }` for agent-written content
- [ ] No body `# Citations` section; footnotes use `sources[].id` labels
- [ ] No legacy `timestamp` field
- [ ] Bundle-relative cross-links where groups are related
- [ ] End with: **Total: N atomic concepts across M groups.**

## Constraints

- **`print` mode:** no files; print all groups.
- **`files` mode:** write OKF bundle; chat summary only.
- **Both modes:** grouped extraction, not whole-document summary.

## Optional refinements (include only if requested)

- Tag each concept row: `definition` | `requirement` | `recommendation` | `impact claim` | `example`
- Add `verified: { by: human:<id>, at: <ISO-8601> }` after human review of the extraction
- Set `stale_after: YYYY-MM-DD` when the source document has a known review cadence
- Generate `viz.html` via OKF visualizer tooling
- Separate normative vs descriptive concepts within a group
