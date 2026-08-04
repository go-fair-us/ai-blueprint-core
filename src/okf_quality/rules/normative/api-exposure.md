# Normative rules — API / machine access (P3)

**Source:** NIAID Blueprint §3 Minimal API Specifications  
**Status:** Design catalog — live checkers not implemented yet

## Intent

Repositories expose Table 1 metadata for human and machine access with flexible implementation paths.

## Checkable obligations (live / endpoint)

| ID | Obligation | Check idea |
|----|------------|------------|
| API-01 | Metadata available to machines | HTTP GET returns JSON-LD or documented machine format |
| API-02 | Table 1 elements exposed | JSON-LD properties cover required Table 1 set |
| API-03 | Resource-oriented IRIs | Stable HTTP(S) identifiers for digital objects |
| API-04 | Documentation | OpenAPI/Swagger or equivalent published |
| API-05 | Fallback if no API | HTML embedded metadata or downloadable index |

## Relationship to OKF knowledge graph

OKF/okf2rdf capture **what the Blueprint says**.  
Live checks capture **what a repository does**.  
Do not collapse these into one shapes graph.

## Future scripts

`scripts/check_api_exposure.py` (not yet) — inputs: base URL, optional OpenAPI URL, sample object IRIs.
