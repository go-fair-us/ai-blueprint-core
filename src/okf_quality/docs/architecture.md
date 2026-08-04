# Architecture — okf_quality

## Purpose

Provide a single place to grow **lint**, **validation**, **rules**, and **query** assets for Blueprint-related knowledge work without burying them inside skills or export CLIs.

## Pipelines

### A. Knowledge-of-the-spec (OKF → RDF)

```text
docs/BluePrint/*.md
        │
        │  (existing extraction / manual OKF authoring)
        ▼
okf/bundles/niaid_blueprint/
        │
        ├─► okf_lint (P0) ──► reports/structure.json
        │
        └─► okf2rdf ──► data.ttl
                │
                ├─► SHACL okf-graph (P1) ──► reports/shacl-okf-*.ttl
                │
                ├─► SPARQL packs (P2) ──► reports/queries-*.json
                │
                └─► atomic↔Blueprint check (P1) ──► reports/atomic-align-*.json
```

### B. Instance metadata (deposits / APIs)

```text
JSON-LD Dataset (intake, genMeta, repository API)
        │
        └─► SHACL dataset-table1 (P0/P1) ──► reports/shacl-dataset-*.ttl
                │
                └─► optional live OpenAPI / IRI resolve (P3)
```

### C. Prose quality

```text
OKF bodies / README / docs prose
        │
        └─► style rules + ste-lint (P2) ──► reports/style-*.json
```

## Components

| Component | Responsibility | Inputs | Outputs |
|-----------|----------------|--------|---------|
| `lint/` | Deterministic structure + FM contracts | OKF bundle path | JSON report, exit code |
| `shapes/` | SHACL shapes graphs | RDF data | Validation report graph |
| `queries/` | SPARQL integrity/inventory | RDF data | Row sets / violation lists |
| `rules/` | Human policy catalogs (source of requirements) | — | Docs for implementers & agents |
| `checks/` | Cross-artifact scripts | Bundle + Blueprint md | JSON report |
| `scripts/` | CLI entrypoints | CLI args | reports/ |
| `reports/` | Ephemeral CI/local outputs | — | gitignored |

## Namespaces (RDF)

| Prefix | IRI |
|--------|-----|
| `okf:` | `https://go-fair-us.github.io/ai-blueprint-core/ns/okf#` |
| `schema:` | `https://schema.org/` |
| `sh:` | `http://www.w3.org/ns/shacl#` |
| `ex:` / shapes | `https://niaid.nih.gov/blueprint/shapes#` (dataset shapes; align with skill) |
| `oq:` | `https://go-fair-us.github.io/ai-blueprint-core/ns/okf-quality#` (quality report metadata, optional) |

## Relationship to skills

- **Skills** remain interview-driven UX (`niaid-bp-validation`, fair-assess).
- **okf_quality** is the **batch / CI / library** home for the same domain rules.
- When a skill shape is authoritative (e.g. `blueprint-required.ttl`), either symlink, copy with NOTICE, or document “source of truth” in `shapes/dataset-table1/README.md`.

## Non-goals

- Replacing pySHACL or rdflib
- Publishing a triple store
- Auto-repair of Blueprint prose (genMeta-style loops stay separate)
