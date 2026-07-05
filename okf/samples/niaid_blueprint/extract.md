# Prompt: Extract grouped atomic concepts into an OKF bundle

You are analyzing one or more source documents. Your task is to extract **atomic concepts**—self-contained facts or hypotheses explicitly stated in the document—and organize them into **upper-level thematic groups**. Output must conform to [Open Knowledge Format (OKF) v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

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

## Input

- **Source document(s):** one or more line-numbered markdown files
- **Line-numbered text:** use each file's line numbers as printed (1-indexed). For multiple sources, qualify line numbers in the `Lines` column (e.g., `Blueprint.md:41`)
- **Output mode:** `print` | `files` (default `print`)
- **Output directory:** required when output mode is `files`

## Output modes

### Mode: `print` (testing / review)

Print all groups to the conversation. Do **not** create files.

### Mode: `files` (OKF bundle)

Write a conformant **OKF knowledge bundle**: one markdown concept file per thematic group, `index.md` at each directory level, optional `log.md` at bundle root. Create directories as needed. After saving, print only a short summary (files written, concept/group counts).

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

### YAML frontmatter

```yaml
---
type: <Human-readable type name>
title: <Display name>
description: <One-line summary>
resource: <Canonical URI for underlying asset, when available>
tags: [<tag>, <tag>]
source_document: <path>
source_lines: <start>-<end>
section: <verbatim source section heading>
normative: <true|false>
concept_range: <first>-<last>
---
```

**`type` (REQUIRED)** — use human-readable OKF-style values:

| Group role | Suggested `type` |
|------------|------------------|
| Document meta, background, motivation, impact | `NIAID Blueprint Section` |
| Normative requirements / Table 1-style specs | `NIAID Blueprint Requirements` |
| Supplemental tables | `Reference Table` |
| Portal/indexed examples | `Worked Example` |
| Living-document header | `Document Status` |

Use `tags` (lowercase) for machine filtering. Omit optional keys when unsupported.

**`resource`** — prefer a real canonical URL for the source document when known (e.g., raw GitHub URL). Do not fabricate URLs.

**Extension keys** (`source_document`, `source_lines`, `normative`, `concept_range`) are producer-defined OKF extensions.

Do **not** use `group_index`; ordering is expressed via `index.md` listings.

### Markdown body

```markdown
[Opening prose: synthesizing narrative grounded in atomic facts, no new claims.]

[Optional bundle-relative cross-links to related concepts, e.g. Part of the [Blueprint scope](/overview/blueprint-scope.md).]

# Atomic concepts

| # | Concept | Lines |
|---|---------|-------|
| 1 | [Self-contained fact or hypothesis] | [line numbers] |

# Citations

[1] [Source section title](<canonical-source-url>) (lines <start>–<end>)
```

- Opening prose replaces a separate `## Narrative` heading; use plain paragraphs or `# Overview` when helpful.
- `# Atomic concepts` holds the numbered fact table.
- `# Citations` lists external sources backing claims (OKF §8). Include the source document URL and line span from `source_lines`.

### Cross-linking (OKF §5)

Link related concepts with bundle-relative absolute paths:

```markdown
See [Persistent Identifiers — Requirements](/persistent-identifiers/requirements.md).
```

Add cross-links when groups are clearly related (pillar motivation → requirements → impact; requirements → appendix reference tables).

## Index files (OKF §6)

**Bundle-root `index.md`** — frontmatter allowed only for `okf_version`:

```markdown
---
okf_version: "0.1"
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

## Log file (optional, OKF §7)

On bundle creation, write `log.md` at bundle root:

```markdown
# Bundle Update Log

## YYYY-MM-DD
* **Creation**: Initial extraction of N atomic concepts across M groups from <source>.
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

## Quality checks

- [ ] OKF §9: every non-reserved `.md` file has parseable frontmatter with non-empty `type`
- [ ] `index.md` files follow §6 (no frontmatter except `okf_version` at bundle root)
- [ ] Reserved filenames (`index.md`, `log.md`) not used for concept documents
- [ ] Semantic paths and filenames (no `01-` prefixes)
- [ ] `# Citations` present on each concept file
- [ ] Bundle-relative cross-links where groups are related
- [ ] End with: **Total: N atomic concepts across M groups.**

## Constraints

- **`print` mode:** no files; print all groups.
- **`files` mode:** write OKF bundle; chat summary only.
- **Both modes:** grouped extraction, not whole-document summary.

## Optional refinements (include only if requested)

- Tag each concept row: `definition` | `requirement` | `recommendation` | `impact claim` | `example`
- Generate `viz.html` via OKF visualizer tooling
- Separate normative vs descriptive concepts within a group