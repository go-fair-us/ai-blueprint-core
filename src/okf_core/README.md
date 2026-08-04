# okf-core

Shared **Open Knowledge Format (OKF) v0.2** parse and walk library.

Used by:

- [`visualize-okf`](../visualize-okf/) — HTML / Gephi graph viewer
- [`okf2rdf`](../okf2rdf/) — schema.org-centered RDF export

## API

```python
from okf_core import walk_bundle, count_atomics, OKFDocument
from pathlib import Path

concepts = walk_bundle(Path("okf/bundles/niaid_blueprint"))
for c in concepts:
    print(c.id, c.type, len(c.atomics), c.links_to)
print("total atomics", count_atomics(concepts))
```

Body tables under ``# Atomic concepts`` become ``c.atomics`` (``AtomicConcept`` rows).

## Install

```bash
pip install -e src/okf_core
```
