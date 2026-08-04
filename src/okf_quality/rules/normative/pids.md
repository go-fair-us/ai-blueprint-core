# Normative rules — Persistent identifiers

**Source:** NIAID Blueprint §2 / Table 2  
**Machine checks:** extend Dataset SHACL; link resolvers (P3)

| Entity | Preferred PID | Check idea |
|--------|---------------|------------|
| Digital object | DOI (resolvable) | `schema:identifier` matches DOI pattern; HTTP resolve optional |
| Person | ORCID | author `@id` or `sameAs` ORCID |
| Organization | ROR | funder / affiliation ROR URI |
| Taxon | NCBITaxon | infectiousAgent / host ontology URI |
| Disease | MONDO | healthCondition |
| License | SPDX | license identifier in SPDX set or URL |

Soft validation can warn on free-text where a PID is preferred.
