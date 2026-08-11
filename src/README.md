# `src/` — Python tooling

Standalone libraries and CLIs that support the NIAID Blueprint agent stack: metadata extract/repair, OKF knowledge tooling, and DSPy prompt optimization. Each package has its own README for setup, flags, and design notes.

| Package | Role |
|---------|------|
| [genMeta](genMeta/) | URL → Dataset JSON-LD extract, SHACL validate, agent repair |
| [libraryOptimizer](libraryOptimizer/) | GEPA optimize one OKF prompt example |
| [promptOptimizer](promptOptimizer/) | Multi-optimizer bake-off (baseline / bootstrap / MIPRO / GEPA) |
| [promptLibrary](promptLibrary/) | Static browser UI for Blueprint prompts |
| [okf_core](okf_core/) | Shared OKF v0.2 parse and walk library |
| [okf2rdf](okf2rdf/) | OKF bundle → schema.org-centered RDF |
| [okf_quality](okf_quality/) | Lint, SHACL, SPARQL, and rule catalogs for OKF artifacts |
| [visualize-okf](visualize-okf/) | Interactive HTML / Gephi graph of an OKF bundle |

---

## genMeta

Orchestrates **URL → schema.org Dataset JSON-LD**: a Pi agent extracts metadata (via Herdr), the host runs **pySHACL** against Blueprint shapes, and a repairer agent patches failures until the record conforms or the retry budget ends. Keeps LLMs on drafting and host code on conformance checks.

```bash
uv sync --extra genmeta   # needs a running Herdr server
uv run python src/genMeta/main.py \
  --url https://immport.org/shared/study/SDY998 \
  --max-iters 3
```

---

## libraryOptimizer

DSPy **GEPA** harness for a single filled prompt under `okf/prompt_examples/`. Loads the `# Prompt` body as seed instructions, generates scenarios, and scores free-text outputs with an LLM judge against local Blueprint and Work Plans text. Simpler sibling of `promptOptimizer` (GEPA only, no multi-optimizer compare).

```bash
uv run python src/libraryOptimizer/main.py list-prompts
uv run python src/libraryOptimizer/main.py optimize \
  --prompt okf/prompt_examples/metadata-schema/core-elements/name-description.md \
  --gepa-budget 40
```

---

## promptOptimizer

Config-driven DSPy harness that compares **baseline, BootstrapFewShot, MIPROv2, and GEPA** on one Blueprint goal per run (e.g. API examples or Dataset JSON-LD). Active goal comes from `config/profile.yaml` or `--profile`; scoring blends deterministic checks with an optional LLM judge.

```bash
cd src/promptOptimizer
uv run main.py baseline
uv run main.py gen-scenarios --n 40
uv run main.py compare
```

(`gepaQuick.sh` in this directory is a short OpenRouter recipe for a light bake-off.)

---

## promptLibrary

Static web app to browse, search, and copy Blueprint-related prompts. Content is generated from a local OKF-style bundle into `data.json`; no backend required beyond any static file server.

```bash
cd src/promptLibrary
python3 -m http.server 8000   # open http://localhost:8000
# optional: regenerate data from okf-bundle/
python3 build_data.py
```

---

## okf_core

Shared **OKF v0.2** library: walk a bundle, parse concept frontmatter and body links, and extract atomic-concept table rows. Used by `visualize-okf` and `okf2rdf` so walk/parse logic lives in one place.

```python
from pathlib import Path
from okf_core import walk_bundle, count_atomics

concepts = walk_bundle(Path("okf/bundles/niaid_blueprint"))
print(len(concepts), "concepts,", count_atomics(concepts), "atomics")
```

```bash
pip install -e src/okf_core
# or: export PYTHONPATH=src/okf_core/src
```

---

## okf2rdf

Exports an OKF bundle to an RDF graph centered on **schema.org**, with PROV/DCTERMS/SKOS and a small `okf:` vocabulary. Concepts become graph nodes; atomic table rows become `okf:AtomicConcept` parts (optional). Output Turtle or JSON-LD.

```bash
export PYTHONPATH=src/okf_core/src:src/okf2rdf/src
python -m okf2rdf \
  --bundle okf/bundles/niaid_blueprint \
  --out /tmp/niaid_blueprint.ttl \
  --format turtle
```

---

## okf_quality

Quality gates for Blueprint knowledge artifacts: structural **lint** on OKF bundles, **SHACL** shapes for OKF RDF and Dataset/Table 1 graphs, **SPARQL** integrity packs, and human-readable normative/style rule catalogs (P0–P3). Organizes checks for CI and agents; does not replace the dataset validation skill or `okf2rdf` export.

```bash
export PYTHONPATH=src:src/okf_core/src:src/okf2rdf/src
python -m okf_quality.scripts.okf_lint --bundle okf/bundles/niaid_blueprint

uv run python -m okf_quality.scripts.shacl_validate \
  --data /tmp/niaid.ttl \
  --shapes src/okf_quality/shapes/okf-graph/okf-bundle.ttl \
  --out-dir src/okf_quality/reports/shacl-okf-graph
```

---

## visualize-okf

Builds a single interactive **HTML** force graph of an OKF bundle (Cytoscape.js), or exports **GEXF/GraphML** for Gephi. Viewer-only; parses via `okf_core` patterns and surfaces type, links, provenance, and search.

```bash
cd src/visualize-okf && pip install -e ".[dev]"
python -m visualize_okf \
  --bundle ../../okf/bundles/niaid_blueprint \
  --out /tmp/niaid_blueprint_viz.html \
  --name "NIAID Blueprint"
```

---

## How they relate

```text
okf/bundles/... ──► okf_core ──┬──► visualize-okf (HTML / Gephi)
                               └──► okf2rdf ──► okf_quality (SHACL / SPARQL)

okf/prompt_examples/ ──► libraryOptimizer (GEPA)
prompts / profiles   ──► promptOptimizer (multi-optimizer)
                         promptLibrary (static browse/copy)

URL + skills ──► genMeta (extract → SHACL → repair)
```

For broader project context, see the root [AGENTS.md](../AGENTS.md) and [okf/README.md](../okf/README.md).
