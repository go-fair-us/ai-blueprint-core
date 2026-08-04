# Normative rules — Metadata schema (Table 1)

**Source:** NIAID Blueprint §1 / Table 1  
**Machine checks:** `shapes/dataset-table1/`, skill `niaid-bp-validation`

## Required (target state for deposits)

| Element | Default representation | Machine rule direction |
|---------|------------------------|-------------------------|
| type | IRI to type (dataset, …) | `schema:Dataset` or type IRI present |
| identifier | Resolvable DOI | `schema:identifier` present; DOI-shaped URI preferred |
| name | free text | non-empty `schema:name` |
| description | free text | non-empty `schema:description` |
| dateCreated | ISO 8601 | `schema:dateCreated` |
| author | ORCID | `schema:author` with ORCID URI when person |
| funder | ROR | `schema:funder` |
| grant | string | `schema:funding` / grant property |
| distribution | URL | `schema:distribution` or download URL |
| conditionsOfAccess | URL | `schema:conditionsOfAccess` |
| license | SPDX or URL | `schema:license` |

## IID-oriented (when applicable)

| Element | Default | Machine rule direction |
|---------|---------|-------------------------|
| infectiousAgent | NCBITaxon | ontology URI |
| host | NCBITaxon | ontology URI |
| healthCondition | MONDO | ontology URI |
| measurementTechnique | NCIT | ontology URI |

## Progressive enforcement

1. **Now:** required-core (name, description, url) as Violation  
2. **Next:** identifier, license, conditionsOfAccess as Warning  
3. **Later:** Violation for identifier + license on Portal-bound deposits  
