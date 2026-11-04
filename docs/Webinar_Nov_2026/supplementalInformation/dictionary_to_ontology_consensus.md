# From Dictionaries to Ontologies: The Knowledge Representation Spectrum
*Consensus report, NIH Webinar room, Nov 3, 2026 (Researcher, Fact Checker, Planner, Coding, Grok Bot; compiled by Chief of Staff)*

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

## 3. One term, up the ladder
Coding traced **Influenza A virus** (`NCBITaxon:11320`) through the rungs. The `ex:` IRIs are placeholders; the full file is `coding_one_term_ladder.md`.

1. **Data dictionary:** `infectious_agent, "Pathogen studied", string, "Influenza A virus"`
2. **Controlled vocabulary:** `NCBITaxon:11320, Influenza A virus, "FLUAV"`
3. **SKOS:** `ex:fluA skos:prefLabel "Influenza A virus"; skos:altLabel "FLUAV"; skos:broader ex:alphainfluenzavirus; skos:exactMatch obo:NCBITaxon_11320 .`
4. **OWL:** `ex:InfluenzaSample` is defined as a Sample that `hasInfectiousAgent some NCBITaxon_11320`, so a reasoner can classify samples.
5. **SHACL:** a Sample must have at least one `hasInfectiousAgent`, and it must be an NCBITaxon IRI.
6. **SSSOM:** `ex:fluA skos:exactMatch NCBITaxon:11320 semapv:ManualMappingCuration`
7. **schema.org JSON-LD (NDE-style):** `"infectiousAgent": {"@type":"DefinedTerm","name":"Influenza A virus","identifier":"NCBITaxon:11320"}`

## 4. Where the NIAID sites sit (from our earlier probe)
| Site / resource | Rung reached | Evidence |
|---|---|---|
| ImmPort | 2–3 | `lk*` lookup endpoints; validation tool exists but isn't exposed |
| ClinEpiDB | 4 | An open category tree with 162 nodes |
| NDE schema | 6 | A schema.org-based profile |
| IEDB | 7–8 | MRO and ONTIE ontologies |
| All 11 sites | — | No published SSSOM mappings found |

**Pattern:** most repositories stop at rung 2, and many never publish even that.

### Doug's own work on the ladder
- **Science-on-Schema.org (SOSO):** a schema.org profile at rung 6, with SHACL shapes for validation.
- **Croissant:** schema.org-based JSON-LD for ML datasets; its field descriptions act as a machine-readable data dictionary (rungs 2 and 6).
- **Genesis Data Cards:** mostly rung 2. They climb higher only when their values point to vocabulary IDs.
- **BV-BRC sample metadata:** rungs 2–3, reaching rung 3 wherever it uses NCBITaxon or other OBO IDs.
- **Pattern:** this work lives in the middle of the ladder, and can climb cheaply through SKOS, SSSOM and SHACL rather than full OWL.

## 5. Takeaways for the talk
1. **The deck's Slide 26 "vocabulary ladder"** is a compressed version of this established spectrum, so it has solid precedent and can cite Lassila & McGuinness and Z39.19.
2. **SKOS is the cheap middle.** Rungs 3–5 need no OWL at all.
3. **LinkML spans the middle.** One YAML file can generate the dictionary, JSON Schema, SHACL and an OWL view.
4. **SSSOM connects the rungs.** A site at rung 3 can map onto an ontology at rung 8 without climbing the whole ladder.
5. **Agents benefit at every rung.** Even a published rung-2 dictionary is a big step up from nothing.

## 6. Open items
- The Uschold & Gruninger DOI is confirmed through Crossref.
- The McGuinness papers have no working link yet (Stanford KSL is returning server errors), and their rung lists still need a word-for-word check.
- The ISO page blocks automated checks; it's cited by its catalog page.
- Planner's open question is whether LLMs make the middle rungs cheaper to build, or let some be skipped.
- NERC vocabularies, DataCite and DUO could also be placed on the ladder.
