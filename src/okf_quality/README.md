# okf_quality

**Lint · Validate · Rules · Query** for NIAID Blueprint knowledge artifacts.

This directory scopes quality gates around:

| Artifact | Examples |
|----------|----------|
| Source specs | `docs/BluePrint/`, `docs/WorkPlans/` |
| OKF bundles | `okf/bundles/niaid_blueprint/` |
| RDF graphs | output of `src/okf2rdf` |
| Instance metadata | `schema:Dataset` JSON-LD (intake / genMeta / Portal) |

It does **not** replace `skills/niaid-bp-validation` (dataset SHACL skill) or `src/okf2rdf` (export). It **organizes and extends** checks so CI, agents, and humans share one map of rules.

## Priority layers (P0–P3)

| Priority | Layer | Location here | Status |
|----------|--------|---------------|--------|
| **P0** | OKF structural lint | `lint/`, `checks/structure/` | Starter CLI |
| **P0** | Dataset SHACL (Table 1 path) | `shapes/dataset-table1/` | Starter shapes + pointer to skill |
| **P1** | SHACL on OKF RDF graph | `shapes/okf-graph/` | Starter shapes |
| **P1** | Atomic ↔ Blueprint line integrity | `checks/atomic_vs_blueprint/` | Spec + stub |
| **P2** | Style / claim lint (STE-like) | `rules/style/`, `lint/rules/` | Rule catalog |
| **P2** | SPARQL rule packs | `queries/` | Query library |
| **P3** | LLM faithfulness judge | `rules/normative/llm-judge.md` | Design only |
| **P3** | Live repo / API checks | `rules/normative/api-exposure.md` | Design only |

See [docs/layers.md](docs/layers.md) and [docs/architecture.md](docs/architecture.md).

## Layout

```text
okf_quality/
  README.md                 # this file
  docs/                     # architecture, layers, how-to
  lint/                     # structural + FM contract lint
    rules/                  # machine-readable rule defs (YAML)
  shapes/                   # SHACL shapes graphs
    okf-graph/              # shapes for okf2rdf output
    dataset-table1/         # shapes for schema:Dataset / Table 1
    examples/               # tiny data graphs for demos
  queries/                  # SPARQL packs (rdflib / any SPARQL engine)
    integrity/
    inventory/
  rules/                    # human-readable policy catalogs
    normative/              # Blueprint shall/must style obligations
    style/                  # prose / STE-oriented guidance
  checks/                   # cross-artifact check specs + scripts
    structure/
    atomic_vs_blueprint/
  scripts/                  # entrypoints (lint, validate, query)
  reports/                  # generated outputs (gitignored contents)
  tests/
```

## Quick start

Structural OKF lint (P0) — needs `okf_core` on `PYTHONPATH`:

```bash
export PYTHONPATH=src:src/okf_core/src:src/okf2rdf/src
python -m okf_quality.scripts.okf_lint \
  --bundle okf/bundles/niaid_blueprint
```

SHACL on an exported OKF graph (P1) — needs `uv sync --extra validation` (pyshacl):

```bash
# 1) Export RDF
python -m okf2rdf \
  --bundle okf/bundles/niaid_blueprint \
  --out /tmp/niaid.ttl

# 2) Validate
uv run python -m okf_quality.scripts.shacl_validate \
  --data /tmp/niaid.ttl \
  --shapes src/okf_quality/shapes/okf-graph/okf-bundle.ttl \
  --out-dir src/okf_quality/reports/shacl-okf-graph
```

Run SPARQL integrity queries (P2):

```bash
uv run python -m okf_quality.scripts.run_queries \
  --data /tmp/niaid.ttl \
  --query-dir src/okf_quality/queries/integrity
```

## Design principles

1. **Structure before truth** — lint/SHACL gate form; humans (and optional LLM judges) assess scientific accuracy.
2. **Two graphs, two shape libraries** — (A) knowledge about the Blueprint (`okf-graph`), (B) instance Dataset/API metadata (`dataset-table1`).
3. **Reports over silent failure** — write machine-readable summaries under `reports/`.
4. **Agents must not edit the rules** — treat `shapes/`, `lint/rules/`, and `queries/` as protected policy.

## Related code

| Package / skill | Role |
|-----------------|------|
| `src/okf_core` | Parse/walk OKF bundles |
| `src/okf2rdf` | Bundle → Turtle/JSON-LD |
| `src/visualize-okf` | Graph visualization |
| `skills/niaid-bp-validation` | Dataset SHACL skill + pySHACL runner |
| `~/.grok/skills/ste-writing` | Prose STE lint (style layer) |

## License

Same as the parent repository.
