# Quality layers (P0–P3)

## P0 — Structural foundations (CI-blocking candidates)

### P0a. OKF structural lint

**Location:** `lint/`, `checks/structure/`, `scripts/okf_lint.py`

| Check | Severity | Notes |
|-------|----------|--------|
| Every non-reserved `.md` has YAML `type` | error | OKF §11 |
| Reserved `index.md` / `log.md` not treated as concepts | info | walker skips |
| Body links resolve to existing concept paths | error | absolute `/…` and relative |
| `# Atomic concepts` table present when expected | warning/error | NIAID profile: all groups |
| Atomic `#` unique globally | error | NIAID: 1..N unique |
| `concept_range` matches min/max atomic numbers | warning | if both present |
| Frontmatter: `sources[].resource` present when `sources` set | error | OKF §5.1 |

### P0b. Dataset SHACL (instance metadata)

**Location:** `shapes/dataset-table1/`

| Shape set | Severity | Notes |
|-----------|----------|--------|
| Required name / description / url | violation | Mirror skill starter |
| Table 1 recommended fields | warning → violation over time | identifier, license, … |

**Source docs:** `docs/BluePrint/NIAID_Blueprint_v2_…md` Table 1; skill `blueprint-required.ttl`.

---

## P1 — Graph integrity

### P1a. SHACL on okf2rdf graph

**Location:** `shapes/okf-graph/`

| Target | Constraints (starter) |
|--------|------------------------|
| `okf:Concept` | name, description, okfType |
| `okf:AtomicConcept` | text, atomicNumber, isPartOf → Concept |
| `okf:Bundle` | hasPart minCount 1 |
| Provenance | soft: generatedAtTime implies wasAttributedTo |

### P1b. Atomic ↔ Blueprint line alignment

**Location:** `checks/atomic_vs_blueprint/`

| Check | Method |
|-------|--------|
| Line span exists in Blueprint md | deterministic |
| Claim token overlap / containment | heuristic (P1) |
| Semantic faithfulness | LLM judge (P3) |

**Source:** `docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md` + atomic `source_lines`.

---

## P2 — Rules packs & style

### P2a. Style / STE-oriented

**Location:** `rules/style/`, integrate `ste-lint.py` from ste-writing skill

| Check | Target |
|-------|--------|
| Marketing adjectives | atomic `schema:text` / OKF prose |
| Sentence length | optional |
| Normative tone mismatch | Requirements vs Motivation |

### P2b. SPARQL integrity & inventory

**Location:** `queries/integrity/`, `queries/inventory/`

| Query | Intent |
|-------|--------|
| orphan_atomics.rq | Atomic without isPartOf Concept |
| missing_text.rq | Atomic without schema:text |
| inventory_counts.rq | Counts by type |

---

## P3 — Soft / live layers

### P3a. LLM faithfulness judge

**Location:** `rules/normative/llm-judge.md`

Design only: prompt + scoring rubric; never sole CI gate.

### P3b. Live API / repository checks

**Location:** `rules/normative/api-exposure.md`

Blueprint Section 3: JSON-LD exposure, OpenAPI, resolvable IRIs — against real endpoints, not OKF text.

---

## Severity model

| Level | CI default | Meaning |
|-------|------------|---------|
| `error` / `sh:Violation` | fail | Must fix |
| `warning` / `sh:Warning` | pass + report | Should fix |
| `info` | report only | Inventory |

Align SHACL severity with lint JSON `"severity"` fields for unified reporting later.
