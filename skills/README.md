# NIAID Blueprint Skill Bundle

## What this directory is

This directory is a **skill bundle**: a set of portable **Agent Skills** that
help people and automated agents apply the
[NIAID Blueprint for Digital Objects](../docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md).

The Blueprint is a FAIR-oriented program for NIAID-funded data repositories. It
covers five practical areas—**metadata schema**, **persistent identifiers**,
**APIs / machine access**, **citation**, and **outreach / training**—so digital
objects can be found, reused, and integrated (including with the NIAID Data
Ecosystem Discovery Portal).

These skills package that domain knowledge as **procedures an agent can follow**,
not as a single compiled application. Each skill is a small directory of
instructions and supporting files. Any agent harness that can load skill
packages (or simply read Markdown and run optional scripts) can use them.

## What is a skill?

A **skill** is a self-contained package of domain expertise for an AI agent. At
minimum it is a directory with a `SKILL.md` file. That file has:

1. **YAML frontmatter** — at least a `name` and a `description` (what the skill
   does and when to use it). Some skills also declare `when_to_use`, license,
   or other metadata.
2. **Markdown body** — the procedure: persona, phases, constraints, output
   shape, and pointers to supporting files.

Optional companions (loaded only when needed):

| Folder / files | Typical contents |
|----------------|------------------|
| `references/` | Interview scripts, element guides, workflows, gap catalogs |
| `assets/` | Templates, blank JSON-LD, SHACL shapes, CSS, report skeletons |
| `scripts/` | Deterministic helpers (save citation, run validation) |
| `tests/` | Checks for bundled scripts |

**Skills vs prompts vs tools**

| Form | Role |
|------|------|
| **Skill** | Full procedure + progressive resources; agent *becomes* the specialist for a multi-step task |
| **Prompt persona** (`prompts/`) | Standalone system text for the same domain logic outside a skill loader |
| **Tool / MCP** | Callable functions (search docs, validate JSON-LD); skills often *use* tools or scripts mid-flow |

The same Blueprint logic often appears in more than one form (for example FAIR
assessment as both a skill and a prompt). When behavior changes, keep parallel
copies aligned where they exist.

## What is a skill bundle?

A **skill bundle** is a coherent collection of skills that share a domain,
naming scheme, and cross-references—so an agent (or a team) can install or
point at **one tree** and cover a whole workflow family.

This bundle (`skills/` in `ai-blueprint-core`) is that collection for NIAID
Blueprint work. Skills hand off to each other where it makes sense (for
example teaching modules that lead into assessment or metadata intake;
validation after extract or intake).

You can:

- Point an agent’s skill search path at this `skills/` directory
- Copy or symlink individual skill folders into a harness-specific skills root
- Load a single `SKILL.md` by hand in any chat that can follow file-based
  instructions

No single vendor runtime is required. What matters is: **discover metadata →
load procedure → read references / run scripts as directed**.

## How agents are expected to use skills

Well-behaved skill loaders use **progressive disclosure** so many skills can
sit on disk without flooding the model context:

```text
1. Advertise   Frontmatter name + description for every skill (~small)
2. Activate    Full SKILL.md body when the task matches
3. Deepen      references/, assets/, scripts/ only when the procedure needs them
```

If your environment does not implement automatic skill discovery, you can still
use a skill manually:

1. Open the skill’s `SKILL.md`.
2. Follow **On Skill Start** (or equivalent) steps—usually “read this reference
   file first.”
3. Carry out the interview, extraction, or validation procedure.
4. Emit the skill’s defined deliverable (report, JSON-LD, citation, etc.).

**Invocation** is harness-specific. Skills are identified by their `name`
(directory name). Many environments map that name to a slash command
(`/niaid-bp-fair-assess`); others use a palette, a tool call, or an explicit
“load skill …” instruction. The catalog below lists the **skill name** and
optional arguments—not a requirement to use any particular UI.

## Naming convention

Every primary skill directory and its frontmatter `name` follows:

```text
niaid-bp-<activity>
```

Directory name = skill `name` = common invocation identifier.

The `hermes/` tree is a **separate packaging path** (platform-oriented
layout for one agent ecosystem). It is **not** under the `niaid-bp-*` naming
set; treat it as optional packaging, not part of the core bundle contract.

## Skills in this bundle

### `niaid-bp-fair-assess` — Blueprint FAIR assessment

Conducts a structured interview across the Blueprint’s five areas (metadata
schema, persistent identifiers, APIs, citation, outreach) and produces a
prioritized gap report with recommended next steps.

**Use when:** A repository owner, data steward, or PI wants to know how well
their resource aligns with the Blueprint, or is preparing to integrate with the
NIAID Data Ecosystem Discovery Portal.

**Args (optional):** repository name (pre-seeds overview).

**Output:** A Markdown assessment report—one section per Blueprint area, each
with current state, gaps, priority (High / Medium / Low), and one concrete
recommended action. Ends with a short overall readiness summary.

---

### `niaid-bp-dataset-intake` — Dataset metadata intake

Conducts a conversational interview to collect metadata for a dataset and
produces a valid JSON-LD document (`@type: Dataset`) aligned with the
Blueprint’s schema.org-based metadata schema.

**Use when:** A researcher or repository manager needs structured metadata for
deposit, Portal indexing, or a citable record.

**Args (optional):** dataset name or DOI.

**Output:** JSON-LD covering up to 16 Blueprint metadata elements (name,
description, DOI, author/ORCID, funder/ROR, grant, measurementTechnique,
infectiousAgent, host, healthCondition, conditionsOfAccess, license,
distribution, temporalCoverage, spatialCoverage, citation). Missing required
fields are flagged in Metadata Notes.

The interview can be stopped early with “make the record with what you have”—the
skill generates valid JSON-LD from whatever has been collected.

---

### `niaid-bp-metadata-extract` — URL metadata extraction

Fetches a web resource URL and extracts Blueprint-aligned schema.org JSON-LD by
analyzing the page. No interview—the agent retrieves evidence from the web.

**Use when:** You have a dataset or resource landing-page URL and want a draft
JSON-LD record without answering intake questions by hand.

**Args (required):** resource URL.

**Output:** Resource summary, a JSON-LD code block, and metadata notes (found /
inferred / missing fields, unresolved PIDs, confidence). Authoritative Blueprint
and example records are fetched from published raw URLs at run time.

See also: [`docs/metadataGeneration.md`](../docs/metadataGeneration.md).

---

### `niaid-bp-citation` — Citation guidance

Interview for citation text and BibTeX aligned with Blueprint Section 4
(original deposits, reused data, repository-level citations, “How to Cite”
drafts). Optional helper script can save artifacts.

**Args:** none required (conversation-driven).

---

### `niaid-bp-model-influence` — Model influence statement

Conversational interview for a Model Influence Statement (voluntary disclosure
of ML model use in a research work), plus a one-paragraph acknowledgment
summary. Bundles a statement template and example; optional save script.

**Args:** none required.

See also: [`niaid-bp-model-influence/README.md`](niaid-bp-model-influence/README.md).

---

### `niaid-bp-teach` — Blueprint teaching workspace

Multi-session teaching of the Blueprint: mission, HTML lessons, learning
records, glossary, and reference sheets. Hands-on modules hand off to sibling
skills in this bundle.

**Args:** none required (stateful workspace across sessions).

---

### `niaid-bp-validation` — SHACL dataset validation

Validates a `schema:Dataset` graph (JSON-LD or Turtle) against a bundled SHACL
shapes graph. Emits a severity-aware conformance verdict plus structured results
(`report.ttl`, `results.json`, `conforms.json`).

**Use when:** You have Dataset JSON-LD (for example from dataset intake or
metadata extract) and want machine-checkable required-field validation.

**Args:** path to a JSON-LD or Turtle file.

**Dependency:** install validation extras for this repository
(`uv sync --extra validation`, which provides the SHACL engine used by
`scripts/validate.py`).

**Initial shape:** `assets/blueprint-required.ttl` — required `name`,
`description` (50–5000 characters), and `url` on `schema:Dataset`. Expandable
toward fuller Blueprint Table 1 coverage later.

The same host validation path is used by automated pipelines such as
[`src/genMeta/`](../src/genMeta/).

---

## How the skills fit together

```text
                    ┌─────────────────────────┐
                    │  niaid-bp-teach         │  learn the Blueprint
                    └───────────┬─────────────┘
                                │ hands-on handoff
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
 niaid-bp-fair-assess   niaid-bp-dataset-intake   niaid-bp-citation
   (gap interview)        (human → JSON-LD)      (how to cite)
                                │
                    niaid-bp-metadata-extract
                      (URL → JSON-LD draft)
                                │
                                ▼
                      niaid-bp-validation
                      (SHACL gate on Dataset)
```

`niaid-bp-model-influence` sits alongside the Blueprint core: research
transparency about model use, not a Table 1 metadata path.

## Skill layout on disk

Skills follow a conventional Agent Skills layout (`SKILL.md` plus optional
`references/`, `assets/`, `scripts/`, `tests/`). Exact discovery rules depend on
your harness; the on-disk contract is the directory + frontmatter.

```text
skills/
├── README.md                 # this file
├── niaid-bp-fair-assess/
│   ├── SKILL.md
│   ├── references/
│   │   ├── interview-phases.md
│   │   ├── blueprint-quick-ref.md
│   │   └── gap-patterns.md
│   └── assets/
│       └── report-template.md
├── niaid-bp-dataset-intake/
│   ├── SKILL.md
│   ├── references/
│   │   ├── element-guide.md
│   │   ├── pid-help.md
│   │   └── jsonld-structure.md
│   └── assets/
│       └── blank-dataset.jsonld
├── niaid-bp-metadata-extract/
│   ├── SKILL.md
│   └── references/
│       └── extraction-workflow.md
├── niaid-bp-citation/
│   ├── SKILL.md
│   ├── references/
│   ├── scripts/
│   └── …
├── niaid-bp-model-influence/
│   ├── SKILL.md
│   ├── scripts/
│   ├── tests/
│   └── …
├── niaid-bp-teach/
│   ├── SKILL.md
│   ├── references/
│   ├── lessons/
│   └── …
├── niaid-bp-validation/
│   ├── SKILL.md
│   ├── assets/
│   │   └── blueprint-required.ttl
│   ├── scripts/
│   │   └── validate.py
│   ├── references/
│   │   └── validation-workflow.md
│   └── tests/
└── hermes/                   # optional alternate packaging; not niaid-bp-*
    └── fair-assessor/
```

## Related material in this repository

| Path | Relation to skills |
|------|--------------------|
| [`prompts/`](../prompts/) | Standalone personas for the same domain without a skill loader |
| [`docs/metadataGeneration.md`](../docs/metadataGeneration.md) | URL extraction overview (pairs with metadata extract) |
| [`docs/assessments/`](../docs/assessments/) | Example FAIR assessment outputs (crawl / interview family) |
| [`mcp_bp/`](../mcp_bp/) | Serves docs and prompt personas over MCP; complementary to skills |
| [`src/genMeta/`](../src/genMeta/) | Automated extract → SHACL validate → repair using extract + validation skills |
| [`okf/`](../okf/) | OKF knowledge bundle of Blueprint concepts (structured knowledge layer) |

## Authoring notes

When you add or edit a skill in this bundle:

1. Keep frontmatter **`name`**, **`description`**, and (if present)
   **`when_to_use`** accurate—those fields drive discovery.
2. Prefer **progressive references**: do not dump every table into
   `SKILL.md`; load `references/` mid-procedure.
3. Preserve the **`niaid-bp-`** prefix for core skills.
4. If parallel prompt personas exist under `prompts/`, update them when the
   skill’s interview or output contract changes.
5. Optional scripts should stay **stdlib-friendly** where possible, or document
   extra install steps clearly (as validation does).
