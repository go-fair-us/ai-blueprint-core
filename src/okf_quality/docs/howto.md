# How to use okf_quality

## Prerequisites

```bash
# From repo root — `src` makes the okf_quality package importable
export PYTHONPATH=src:src/okf_core/src:src/okf2rdf/src

# For SHACL / rdflib
uv sync --extra validation
```

## 1. Lint an OKF bundle (P0)

```bash
python -m okf_quality.scripts.okf_lint \
  --bundle okf/bundles/niaid_blueprint \
  --out src/okf_quality/reports/okf-lint.json
```

Exit code `1` if any `error` findings.

## 2. Export RDF then SHACL-validate (P1)

```bash
python -m okf2rdf \
  --bundle okf/bundles/niaid_blueprint \
  --out src/okf_quality/reports/niaid_blueprint.ttl \
  --name "NIAID Blueprint"

python -m okf_quality.scripts.shacl_validate \
  --data src/okf_quality/reports/niaid_blueprint.ttl \
  --shapes src/okf_quality/shapes/okf-graph/okf-bundle.ttl \
  --out-dir src/okf_quality/reports/shacl-okf-graph
```

## 3. Run SPARQL packs (P2)

```bash
python -m okf_quality.scripts.run_queries \
  --data src/okf_quality/reports/niaid_blueprint.ttl \
  --query-dir src/okf_quality/queries/integrity \
  --out src/okf_quality/reports/sparql-integrity.json
```

## 4. Atomic vs Blueprint lines (P1 stub)

```bash
python -m okf_quality.scripts.check_atomic_lines \
  --bundle okf/bundles/niaid_blueprint \
  --blueprint docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md \
  --out src/okf_quality/reports/atomic-lines.json
```

## 5. Dataset SHACL (instance)

Prefer the skill for interactive use:

```bash
# skill path
uv run python skills/niaid-bp-validation/scripts/validate.py path/to/dataset.jsonld
```

Shapes under `shapes/dataset-table1/` are the growing Table 1 profile; start with `required-core.ttl` (aligned with the skill).

## Adding a rule

1. Document intent under `rules/` (human).
2. Prefer a **deterministic** check first:
   - structure → `lint/rules/*.yaml` + implement in `okf_lint`
   - graph shape → new `shapes/**/*.ttl`
   - graph pattern → new `queries/**/*.rq`
3. Add a test under `tests/`.
4. Update `docs/layers.md` severity table if CI policy changes.

## Reports

`reports/` holds generated artifacts. Track the directory; ignore contents via `.gitignore` except `.gitkeep`.
