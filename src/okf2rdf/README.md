# okf2rdf

Convert an [Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) knowledge bundle to an RDF knowledge graph centered on **schema.org**, with **PROV**, **DCTERMS**, **RDFS**, **SKOS**, and a small local **okf:** vocabulary.

Walk and parse code is shared with visualize-okf via **okf-core**.

## Install

```bash
cd src/okf_core && pip install -e .
cd ../okf2rdf && pip install -e ".[dev]"
```

Or with PYTHONPATH (no install):

```bash
export PYTHONPATH=src/okf_core/src:src/okf2rdf/src
```

## Usage

```bash
python -m okf2rdf \
  --bundle ../../okf/bundles/niaid_blueprint \
  --base https://go-fair-us.github.io/ai-blueprint-core/okf/bundles/niaid_blueprint/ \
  --out /tmp/niaid_blueprint.ttl \
  --format turtle \
  --name "NIAID Blueprint"

# JSON-LD
python -m okf2rdf \
  --bundle ../../okf/bundles/niaid_blueprint \
  --format json-ld \
  --out /tmp/niaid_blueprint.jsonld

# Group concepts only (no atomic table rows)
python -m okf2rdf \
  --bundle ../../okf/bundles/niaid_blueprint \
  --no-atomics \
  --out /tmp/niaid_groups_only.ttl
```

| Flag | Meaning |
|------|---------|
| `--bundle` | OKF bundle root (required) |
| `--base` | IRI base for concept subjects (path id appended) |
| `--out` | Output file (default `<bundle>/bundle.ttl` or `bundle.jsonld`) |
| `--format` | `turtle` (default) or `json-ld` |
| `--name` | Bundle display name |
| `--no-body-links` | Skip `dcterms:references` from body markdown links |
| `--no-atomics` | Skip `okf:AtomicConcept` nodes from `# Atomic concepts` tables |

## What is mapped

### Group concepts (one per concept file)

Subject: `{base}{concept-id}` e.g. `…/metadata-schema/requirements`

| OKF | RDF |
|-----|-----|
| `type` | `rdf:type` schema.org class + `okf:Concept` + `okf:okfType` |
| `title` | `schema:name`, `rdfs:label` |
| `description` | `schema:description` |
| `resource` (http URL) | `schema:url` |
| `tags` | `schema:keywords` |
| `status` | `schema:creativeWorkStatus` |
| `generated.at` / `.by` | `prov:generatedAtTime` / `prov:wasAttributedTo` |
| `sources[].resource` | `prov:wasDerivedFrom`, `dcterms:source` |
| body See-also links | `dcterms:references` |
| atomic children | `schema:hasPart` → each atomic |
| bundle | `schema:Collection` / `okf:Bundle` with `schema:hasPart` |

### Atomic concepts (table rows; default on)

Subject: `{base}atomic/{number}` e.g. `…/atomic/118`

Parsed from body heading `# Atomic concepts` and columns `# | Concept | Lines`.

| Field | RDF |
|-------|-----|
| claim text | `schema:text`, `rdfs:comment`, short `rdfs:label` |
| number | `okf:atomicNumber`, `skos:notation` |
| lines | `okf:sourceLines` |
| parent file | `dcterms:isPartOf` group concept |
| parent normative / status | inherited when present |
| Blueprint URL | `prov:wasDerivedFrom` (from parent `resource`) |

For the NIAID Blueprint bundle this yields **27** group concepts and **239** atomics.

Local terms: `https://go-fair-us.github.io/ai-blueprint-core/ns/okf#`

JSON-LD context: `src/okf2rdf/context/okf-schemaorg.jsonld`

### Example SPARQL

```sparql
PREFIX okf: <https://go-fair-us.github.io/ai-blueprint-core/ns/okf#>
PREFIX schema: <https://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?n ?text WHERE {
  ?a a okf:AtomicConcept ;
     okf:atomicNumber ?n ;
     schema:text ?text ;
     dcterms:isPartOf <https://go-fair-us.github.io/ai-blueprint-core/okf/bundles/niaid_blueprint/api-specification/motivation> .
}
ORDER BY ?n
```

## Tests

```bash
cd src/okf2rdf
PYTHONPATH=src:../okf_core/src pytest -q
```
