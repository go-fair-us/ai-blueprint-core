# NIAID Blueprint Claude Skills

Claude Code skills for working with the [NIAID Blueprint for Digital Objects](../docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md). Skills live under `skills/` in this repository.

**Naming convention:** every skill directory and frontmatter `name` starts with `niaid-bp-`, followed by an activity segment. Directory name = skill `name` = slash command.

---

## `/niaid-bp-fair-assess` — Blueprint FAIR Assessment

Conducts a structured interview across the Blueprint's five areas (metadata schema, persistent identifiers, APIs, citation, outreach) and produces a prioritized gap report with recommended next steps.

**Use when:** A repository owner, data steward, or PI wants to know how well their resource aligns with the Blueprint, or is preparing to integrate with the NIAID Data Ecosystem Discovery Portal.

**How to invoke:**
```
/niaid-bp-fair-assess
/niaid-bp-fair-assess MyRepositoryName
```

**Output:** A Markdown assessment report — one section per Blueprint area, each with current state, gaps, priority (High/Medium/Low), and one concrete recommended action. Ends with a 2–3 sentence overall readiness summary.

---

## `/niaid-bp-dataset-intake` — Dataset Metadata Intake

Conducts a conversational interview to collect metadata for a dataset and produces a valid JSON-LD document (`@type: Dataset`) aligned with the Blueprint's schema.org-based metadata schema.

**Use when:** A researcher or repository manager needs to generate structured metadata for a dataset — whether depositing to a repository, preparing for Portal indexing, or creating a citable metadata record.

**How to invoke:**
```
/niaid-bp-dataset-intake
/niaid-bp-dataset-intake "My Dataset Name"
```

**Output:** A JSON-LD document covering up to 16 Blueprint metadata elements (name, description, DOI, author/ORCID, funder/ROR, grant, measurementTechnique, infectiousAgent, host, healthCondition, conditionsOfAccess, license, distribution, temporalCoverage, spatialCoverage, citation). Missing required fields are flagged in a Metadata Notes section.

The interview can be stopped early with "make the record with what you have" — the skill generates valid JSON-LD from whatever has been collected.

---

## `/niaid-bp-metadata-extract` — URL Metadata Extraction

Fetches a web resource URL and extracts Blueprint-aligned schema.org JSON-LD metadata by analyzing the page. No interview — the agent retrieves evidence from the web.

**Use when:** You have a dataset or resource landing-page URL and want a draft JSON-LD record without manually answering intake questions.

**How to invoke:**
```
/niaid-bp-metadata-extract https://immport.org/shared/study/SDY998
```

**Output:** Resource summary, a JSON-LD code block, and metadata notes (found / inferred / missing fields, unresolved PIDs, confidence). Authoritative references are fetched from GitHub raw URLs at run time.

See also: `docs/metadataGeneration.md`

---

## `/niaid-bp-citation` — Citation Guidance

Interview for citation text and BibTeX aligned with Blueprint Section 4 (original deposits, reused data, repository-level citations, "How to Cite" drafts).

**How to invoke:**
```
/niaid-bp-citation
```

---

## `/niaid-bp-model-influence` — Model Influence Statement

Conversational interview for a Model Influence Statement (voluntary disclosure of ML model use in a research work), plus a one-paragraph acknowledgment summary.

**How to invoke:**
```
/niaid-bp-model-influence
```

See also: `skills/niaid-bp-model-influence/README.md`

---

## `/niaid-bp-teach` — Blueprint Teaching Workspace

Multi-session teaching of the Blueprint: mission, HTML lessons, learning records, glossary, and reference sheets. Hands-on modules hand off to sibling skills.

**How to invoke:**
```
/niaid-bp-teach
```

---

## Skill files

Skills live in `skills/` and follow the standard Claude Code skill layout (`SKILL.md` + optional `references/`, `assets/`, `scripts/`). The `hermes/` directory is a separate packaging path and is not part of the `niaid-bp-*` naming set.

```
skills/
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
└── hermes/                    # excluded from niaid-bp naming
    └── fair-assessor/
```
