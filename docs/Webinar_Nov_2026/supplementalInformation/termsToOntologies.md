# From Terms to Ontologies: A Practical Guide to Knowledge Representation

Knowledge representation is not a choice between a spreadsheet and a complex ontology. There are useful steps between them, and different systems can combine those steps in different ways. The key question is: **what should people and software be able to understand or do with your data?**

This guide brings together two related but different ways of describing the field: the knowledge-representation spectrum associated with Lassila and McGuinness, and library-science categories such as controlled vocabularies, taxonomies, and thesauri. They are complementary views, not one universally agreed ladder.

## A practical progression of meaning

The table below is a guide to increasing semantic structure, not a checklist or a claim that every system must pass through each row. A project can begin at any point, and many useful resources combine capabilities.

| Capability | What it records | Example of what it enables |
|---|---|---|
| **Terms and definitions** | Names, definitions, units, and allowed values in a glossary or data dictionary | A person can interpret a field such as `assay_type`. |
| **Controlled terms** | A preferred label, often a stable identifier, and sometimes alternative labels for lookup | Different spellings or names can be associated with the same intended concept. |
| **Vocabulary relationships** | Broader/narrower, hierarchical, or related-concept links, as in taxonomies and thesauri | Users can browse a hierarchy or discover related terms. |
| **Conceptual model** | Classes or record types, properties, and expected value types; sometimes structural constraints | A dataset can use a shared model for entities such as studies, samples, and people. |
| **Formal axioms** | Explicit logical statements, such as subclass, disjointness, or property restrictions | A reasoner can derive consequences of the axioms or detect logical inconsistency. |

The differences are about **what is explicitly represented**. A hierarchy adds a kind of relationship; an ontology can define relationships with formal logic. More detail is not automatically more useful: every added commitment costs time to model, govern, explain, and maintain.

### Why the two original spectra differ

Lassila and McGuinness discuss representations in terms of increasing semantic expressiveness and the commitments a system makes—from simpler vocabularies and taxonomies toward frames, restrictions, and logical constraints. Library-science standards such as ANSI/NISO Z39.19 and ISO 25964 instead describe kinds of knowledge-organization systems and the relationships used for indexing and retrieval, including term lists, taxonomies, and thesauri.

Those purposes explain the apparent disagreement. One view emphasizes how much formal meaning a representation can carry; the other distinguishes practical vocabulary structures. Their ordering and category boundaries do not match exactly. For example, taxonomies may include preferred terms and synonyms, while thesauri add structured associative relationships as well as hierarchy. These are useful categories, but they are not mutually exclusive maturity stages.

Neither view is the single correct spectrum for every purpose. Use Lassila and McGuinness when discussing increasing formal semantics; use NISO/ISO when deciding what vocabulary relationships a terminology service needs. A blended list is a helpful inventory, but it overstates consensus if it puts metadata schemas, linked-data publication, and knowledge graphs in the same sequence as semantic categories. Those are different design choices.

## Keep these design choices separate

Several capabilities often appear together, but none is simply a higher rung on the progression above:

- **A data dictionary or metadata schema** describes fields and expected values. It can be informal or formally specified, and can be used with or without an ontology. A schema can support structural validation without supporting logical inference.
- **A format or language** is how information is encoded. CSV and JSON commonly encode records; RDF and JSON-LD can represent linked graph data when terms are tied to shared vocabularies. Using a machine-readable format alone does not establish that the terms have shared meanings.
- **Identifiers and publication** make it possible to refer to concepts consistently across records and systems. A URI can identify a concept, but an identifier by itself does not define the concept or make a vocabulary FAIR.
- **A knowledge graph** is a graph-shaped collection of entities and relationships. It may use RDF, a property-graph model, or another technology. A graph can be queried without a domain ontology; adding an ontology can supply more explicit meaning and support additional inference.
- **Mappings** connect concepts or terms across vocabularies. A mapping can document a useful correspondence without making the two concepts logically identical. SSSOM is a standard way to represent such mappings and their provenance; common exchange is a TSV table, and author or confidence fields are optional.
- **Validation** checks whether data meets stated requirements. SHACL shapes, for example, can validate RDF data graphs. SHACL validation is a different task from OWL reasoning: a project can use SHACL without an OWL ontology, and an OWL ontology does not automatically validate every application-specific record requirement.

One important distinction: SKOS `broader` and `narrower` describe knowledge-organization relationships. They should not automatically be read as OWL `subClassOf` statements. A broader term can be useful for browsing and retrieval without asserting that every instance of the narrower concept is formally an instance of the broader class.

## FAIR does not require the top of a ladder

The FAIR Interoperability principles provide a practical set of goals, not a required progression to OWL:

- **I1:** use a formal, accessible, shared, and broadly applicable language for knowledge representation.
- **I2:** use vocabularies that follow FAIR principles.
- **I3:** include qualified references to other (meta)data.

These are not equivalent to “use an ontology.” A shared representation language, a findable and reusable vocabulary, and meaningful qualified links each need deliberate implementation. An OWL ontology can help with some use cases, but it is not required by I1–I3; nor does using RDF, JSON-LD, a URI, or an OWL file by itself make a resource FAIR. In particular, qualified references need an appropriate relation and context—not necessarily an OWL axiom.

For a data repository, a useful starting package is often a clear data dictionary, stable identifiers for concepts, a shared metadata model, and validation rules for records. Add hierarchy or related-term links when users need them. Add formal ontology axioms when there is a concrete need for reasoning or consistency checks and the project can maintain them. SHACL can provide record validation independently of that decision.

## Life-science examples

- A local spreadsheet defining assay fields is a data dictionary. It helps people understand the fields, but does not by itself encode how assay concepts relate.
- MeSH illustrates a vocabulary with preferred descriptors, entry terms, hierarchical organization, and related terms. It can serve multiple user needs at once; describing it with SKOS/RDF is a publication/representation choice, not a new semantic category.
- NCBI Taxonomy is a useful example of a stable, browsable organism classification. Its identifiers and hierarchy support lookup and roll-up; they do not make every taxonomic relation an OWL axiom.
- A schema.org-based dataset profile can specify fields for a dataset, while SHACL shapes can check that published records meet local requirements. Neither choice implies that the repository needs a full domain ontology.
- OBI and EDAM are examples of domain ontologies for biomedical investigations and bioinformatics. Their formal axioms are useful where explicit class and property meaning, reuse, and reasoning justify the additional governance and tooling.

The same resource can therefore be a controlled vocabulary, a hierarchy, and an RDF publication at the same time. Describe it by the capabilities it actually provides rather than assigning it one permanent “level.”

## Choosing what to build

Start with the task, not the most formal technology:

- Need consistent terms and clearer fields? Maintain a data dictionary and select controlled terms with stable identifiers.
- Need browsing, roll-up, or discovery? Add hierarchical and related-concept relationships; use an established vocabulary where possible.
- Need records to follow a shared structure? Publish a metadata schema and define appropriate validation rules.
- Need systems to refer to concepts across datasets? Publish stable identifiers and document vocabulary mappings and relation types.
- Need software to infer new facts or check logical consistency? Consider a formal ontology, and plan for expert review, maintenance, and a reasoner.

For NIAID Blueprint repositories, interoperability does not mean “use OWL everywhere.” A proportionate combination—shared metadata, well-identified vocabulary terms, useful links, and explicit validation—may meet practical needs. Choose formal reasoning when the use case calls for it, not as a proxy for quality or FAIRness.

## Sources and further reading

- Lassila, O. & McGuinness, D. L. (2001). [*The Role of Frame-Based Representation on the Semantic Web*](https://openalex.org/W1482253003), Stanford Knowledge Systems Laboratory Technical Report KSL-01-02 (bibliographic record); McGuinness, D. L. (2003). “Ontologies Come of Age.” In D. Fensel, J. Hendler, H. Lieberman, & W. Wahlster (eds.), *Spinning the Semantic Web: Bringing the World Wide Web to Its Full Potential*. MIT Press. These are sources for the expressive-spectrum perspective.
- Hodge (2000), [*Systems of Knowledge Organization for Digital Libraries*](https://www.clir.org/pubs/reports/pub91/), and Zeng, [“Knowledge Organization Systems (KOS)”](https://www.isko.org/cyclo/kos), introduce knowledge-organization-system categories.
- [ANSI/NISO Z39.19](https://www.niso.org/publications/ansiniso-z3919-2005-r2010) and [ISO 25964-1](https://www.iso.org/standard/53657.html) describe structured vocabularies and thesauri.
- W3C, [SKOS Reference](https://www.w3.org/TR/skos-reference/), defines a model for sharing knowledge-organization systems on the Web.
- Wilkinson et al. (2016), [The FAIR Guiding Principles](https://doi.org/10.1038/sdata.2016.18), states the FAIR principles, including I1–I3.
- W3C, [SHACL](https://www.w3.org/TR/shacl/), specifies validation of RDF graphs; W3C, [OWL 2 Primer](https://www.w3.org/TR/owl2-primer/), introduces OWL ontologies and reasoning.
- [SSSOM](https://mapping-commons.github.io/sssom/) documents mappings between semantic resources (common exchange: TSV).
