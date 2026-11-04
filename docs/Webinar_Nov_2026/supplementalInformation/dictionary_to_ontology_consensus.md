# From Dictionaries to Ontologies: The Knowledge Representation Spectrum


## 1. Yes, this spectrum is established
The idea is usually called the **ontology spectrum** or **semantic spectrum**. It arranges knowledge representations from weak semantics (lists of words) to strong semantics (machine-reasonable logic).

- **Lassila & McGuinness (2001)**, *The Role of Frame-Based Representation on the Semantic Web* (Stanford KSL-01-02), and **McGuinness (2003)**, "Ontologies Come of Age," in Fensel, Hendler, Lieberman & Wahlster (eds.), *Spinning the Semantic Web*, MIT Press. The rungs run catalog/ID list, glossary, thesaurus, informal is-a, formal is-a, frames with properties, value restrictions, and general logical constraints. *(The Stanford KSL pages currently return HTTP 500 errors, so these are cited without links.)*
- **Obrst's semantic spectrum**, in Daconta, Obrst & Smith, *The Semantic Web* (Wiley, 2003). It runs taxonomy, thesaurus, conceptual model, and logical theory.
- **Uschold & Gruninger (2004)**, [Ontologies and semantics for seamless connectivity, SIGMOD Record](https://doi.org/10.1145/1041410.1041420), which frames the spectrum by what each rung buys for interoperability.
- **Library science (KOS, knowledge organization systems):** [Hodge (2000), CLIR report](https://www.clir.org/pubs/reports/pub91/) and [Zeng, KOS entry in the ISKO Encyclopedia](https://www.isko.org/cyclo/kos).
- **Standards for the middle rungs:** [ANSI/NISO Z39.19](https://www.niso.org/publications/ansiniso-z3919-2005-r2010) (term list, synonym ring, taxonomy, thesaurus) and [ISO 25964-1](https://www.iso.org/standard/53657.html) (thesauri and vocabulary mapping).

## 2. The consensus ladder
| # | Rung | What it adds | Typical standard / format |
|---|---|---|---|
| 1 | Term list / catalog | Names and IDs | CSV, [CSVW](https://www.w3.org/TR/tabular-data-primer/) |
| 2 | Glossary / data dictionary | Definitions, units, allowed values | [Frictionless Table Schema](https://specs.frictionlessdata.io/table-schema/), JSON Schema, LinkML enums |
| 3 | Controlled vocabulary | One preferred term per concept, stable IDs, synonyms | [SKOS](https://www.w3.org/TR/skos-reference/) `prefLabel` / `altLabel`, CURIEs |
| 4 | Taxonomy | Broader and narrower hierarchy | SKOS `broader` / `narrower` |
| 5 | Thesaurus | Related terms and richer synonymy | ISO 25964, SKOS `related` |
| 6 | Schema / conceptual model | Classes, properties, types, cardinality | RDFS, schema.org profiles, [LinkML](https://linkml.io/) |
| 7 | Lightweight ontology | Formal is-a, domains, ranges | RDFS / OBO-style ontologies |
| 8 | Axiomatic ontology | Restrictions and inference | [OWL 2](https://www.w3.org/TR/owl2-overview/), often aligned to BFO |
| Alongside | Validation and rules | What a valid record looks like, derived facts | [SHACL](https://www.w3.org/TR/shacl/), SPARQL / SWRL rules |
| Alongside | Mappings | Crosswalks between rungs and vocabularies, with provenance | [SSSOM](https://mapping-commons.github.io/sssom/) |

**Note:** the order of the rungs varies by source. For example, McGuinness puts thesaurus before informal is-a, while Z39.19 puts taxonomy before thesaurus. This table is a synthesis, not a single canonical order.

**What each step adds:** first agreed meaning, then hierarchy, then relations, then constraints, then inference. **Each rung adds commitments, not just detail.**

SHACL and SSSOM are not "higher than OWL." They do different jobs: SHACL validates records and SSSOM links vocabularies. Most NIAID portals need validation more than they need OWL reasoning.


**Pattern:** most repositories stop at rung 2, and many never publish even that.

### Where do items in the presentation sit on the ladder?

- **Science-on-Schema.org (SOSO):** a schema.org profile at rung 6, with SHACL shapes for validation.
- **Croissant:** schema.org-based JSON-LD for ML datasets; its field descriptions act as a machine-readable data dictionary (rungs 2 and 6).
- **Genesis Data Cards:** mostly rung 2. They climb higher only when their values point to vocabulary IDs.
- **BV-BRC sample metadata:** rungs 2–3, reaching rung 3 wherever it uses NCBITaxon or other OBO IDs.
- **Pattern:** this work lives in the middle of the ladder, and can climb cheaply through SKOS, SSSOM and SHACL rather than full OWL.
 
