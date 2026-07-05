# Prompt: Extract grouped atomic concepts from a document

You are analyzing a source document. Your task is to extract **atomic concepts**—self-contained facts or hypotheses explicitly stated in the document—and organize them into **upper-level thematic groups**. Do not invent, infer beyond the text, or paraphrase into new claims. If the document does not support a concept, omit it.

## Input

- **Source document:** `@<path-to-document>`
- **Line-numbered text:** Use the document's line numbers as printed in the file (1-indexed from the first line).

## Output structure

For each **upper-level group**, produce exactly this block:

---

```yaml
---
type: <Type name>                  # REQUIRED
title: <Optional display name>
description: <Optional one-line summary>
resource: <Optional canonical URI for the underlying asset>
tags: [<tag>, <tag>, …]            # Optional
timestamp: <ISO 8601 datetime>     # Optional last-modified time
# … other producer-defined key/value pairs
---
```

### [Group title]

**Group narrative:**  
A narrative describing the *general focus* of this group—what theme ties these facts together and why it matters in the document. The narrative should synthesize the group's atomic facts without introducing new claims. Write in plain, readable prose. The narrative should try to be brief and focused but take the amount of text needed to present the concept well without repeating.

**Atomic concepts:**

| # | Concept | Lines |
|---|---------|-------|
| 1 | [Self-contained fact or hypothesis, stated so it stands alone without the surrounding document] | [line numbers] |
| 2 | … | … |

---

Repeat for all groups until the document is covered.

## Rules for upper-level groups

1. **Derive groups from the document's own structure and themes**, not from an arbitrary count. Prefer the document's major sections, subsections, and appendix themes (e.g., Background, Audience, Implementation, each Blueprint pillar, Impact subsections, supplemental tables).
2. **One group = one coherent theme.** Do not mix unrelated topics in a single group.
3. **Split large sections** when they contain distinct sub-themes (e.g., "Motivation," "Requirements," "Impact," or a table whose rows deserve their own atomic facts).
4. **Merge only when** several short paragraphs share a single focus and would be awkward as separate groups.
5. **Exclude** pure navigation (table of contents), boilerplate disclaimers, and funding acknowledgments unless they contain substantive domain claims.
6. **Include appendix and supplemental material** as their own groups when they add distinct concepts (schemas, ontologies, API references, worked examples).

## Rules for group YAML frontmatter

Each group block must begin with a YAML frontmatter fence (`---` delimiters) **before** the group heading. Populate fields from the source document and the group's role; do not invent metadata.

1. **`type` (REQUIRED).** A short, stable machine-readable label for the group's thematic role. Use lowercase kebab-case. Derive from document structure and content, e.g.:
   - `document-status`, `background`, `definition`, `audience`, `implementation`
   - `motivation`, `requirements`, `impact`
   - `metadata-schema`, `persistent-identifiers`, `api-specification`, `citation`, `outreach-training`
   - `appendix`, `worked-example`, `reference-table`
   Reuse the same `type` when multiple groups share the same role (e.g., separate Motivation and Requirements groups under one pillar may both use pillar-specific types like `metadata-schema-motivation` and `metadata-schema-requirements`, or a shared parent type plus distinguishing `title`).

2. **`title` (optional).** Human-readable display name for the group. Defaults to the group heading text if omitted. Use when the heading alone is too generic (e.g., title: `Metadata Schema — Table 1 Elements` for a `### Metadata schema — requirements` group).

3. **`description` (optional).** One-line summary of the group's focus, distilled from the group narrative. Must be supportable by the group's atomic concepts. Max ~200 characters; no trailing period required.

4. **`resource` (optional).** Canonical URI for the underlying asset this group describes. Use, in order of preference:
   - A URL explicitly stated in the source document for the document itself, a specification, portal, or referenced resource.
   - An in-document anchor if no external URI exists (e.g., `#metadata-schema`, `#table-1`).
   - A `source:` URI with file path and line range for the group's primary source span (e.g., `source:NIAID_Blueprint_v2_26Sep2025_forExternal.md#L89-L133`).
   Do not fabricate `https://` URLs.

5. **`tags` (optional).** Array of lowercase terms drawn from the document's domain vocabulary (acronyms, element names, pillar names, standards). Include 2–6 tags when they aid discovery; omit the field entirely if none apply.

6. **`timestamp` (optional).** ISO 8601 datetime (`YYYY-MM-DD` or full `YYYY-MM-DDTHH:MM:SSZ`) for last-modified time **only if** the source document states an explicit date or version date for that content. Omit if not stated; do not use the extraction run date.

7. **Additional producer-defined fields (optional).** Add only when clearly useful and grounded in the source, e.g.:
   - `source_document: <path>` — path to the analyzed file
   - `source_lines: <start>-<end>` — primary line span for the group
   - `section: <document heading>` — verbatim section title from the source
   - `normative: true|false` — whether the group is primarily requirements/guidance vs. descriptive context
   Keep keys lowercase kebab-case; values must be strings, booleans, numbers, or arrays—not nested objects unless necessary.

**Frontmatter formatting rules:**
- Output valid YAML inside the fence; use `key: value` syntax.
- Omit optional keys entirely rather than setting them to empty strings or `null`.
- Use YAML array syntax for `tags`: `tags: [faire, metadata, doi]`
- Do not include inline comments in the emitted frontmatter (comments in this prompt are illustrative only).
- The frontmatter block is metadata *about the group*, not a substitute for atomic concepts.

## Rules for atomic concepts

1. **One concept = one idea.** Each row should express a single fact, requirement, definition, or stated expectation/hypothesis.
2. **Self-contained.** A reader should understand the concept without reading adjacent rows or the source document.
3. **Faithful to source.** Use the document's terminology (acronyms, element names, PID types). Do not upgrade "encouraged" to "required" unless the text does.
4. **Line citations required.** Every concept must cite the line number(s) it was drawn from. Use a comma-separated range for concepts spanning consecutive lines (e.g., `55, 59–63`).
5. **Tables:** Extract each meaningful row, field definition, or requirement as its own atomic concept when it carries distinct information; cite the table's line range.
6. **Do not duplicate** the same fact across groups unless the document states it in meaningfully different contexts; if duplicated, note the distinct framing in the concept text.
7. **Number concepts globally** across the full output (1, 2, 3, …), not restarted per group.

## Rules for group narratives

1. **Synthesize, don't list.** The narrative is not a bullet summary of the table; it explains the group's *purpose and scope* in the document.
2. **Grounded in the group's facts.** Every sentence in the narrative should be supportable by concepts in that group's table.
3. **No new facts.** Do not add context, implications, or recommendations not present in the document.
4. **Proportional length.** Scale length to the group's density: a single-table or single-paragraph group may need only a sentence or two; multi-table requirement sections may need a short paragraph. Never pad; never repeat atomic facts verbatim.

## Quality checks (perform before finishing)

- [ ] Every group begins with YAML frontmatter containing a required `type` field.
- [ ] Frontmatter optional fields are omitted—not empty—when unsupported by the source.
- [ ] No fabricated `resource` URLs or `timestamp` values.
- [ ] Every atomic concept has at least one line citation.
- [ ] No concept relies on information not in the document.
- [ ] Each group has frontmatter, a narrative, and a concept table.
- [ ] Group titles reflect document themes, not generic labels like "Section 3."
- [ ] Requirements vs. encouragement vs. impact are distinguished accurately in concept wording.
- [ ] End with a one-line count: **Total: N atomic concepts across M groups.**

## Constraints

- **Do not create, edit, or save any files.** Print the output only.
- **Do not summarize the whole document** in place of grouped extraction.
- **Do not produce a flat unordered list** without group narratives.

## Optional refinements (include only if requested)

- Tag each concept as: `definition` | `requirement` | `recommendation` | `impact claim` | `example`
- Add a final index mapping document section headings → group titles
- Separate **normative** (shall/must/should) concepts from **descriptive** context within each group
