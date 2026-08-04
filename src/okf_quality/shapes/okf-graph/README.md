# SHACL shapes — OKF knowledge graph (okf2rdf output)

**Priority:** P1  
**Data graph:** Turtle/JSON-LD from `python -m okf2rdf`  
**Namespace (data):** `okf:` = `https://go-fair-us.github.io/ai-blueprint-core/ns/okf#`

## Files

| File | Role |
|------|------|
| `okf-bundle.ttl` | Starter shapes for Bundle, Concept, AtomicConcept |

## Run

See [../../docs/howto.md](../../docs/howto.md).

## Design notes

- Shapes are **open** (extra triples allowed).
- Severity: core identity fields → `sh:Violation`; soft provenance → `sh:Warning`.
- Align property paths with `src/okf2rdf` mapping (`schema:name`, `schema:text`, `dcterms:isPartOf`, …).
