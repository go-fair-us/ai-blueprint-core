# The Spectrum of Knowledge Representation: From Dictionaries to Formal Ontologies

Knowledge representation is not a binary choice between a flat vocabulary and a heavyweight ontology — it is a spectrum that has been recognized, refined, and taught for over two decades, with roots reaching back to Wittgenstein's early work on language and logic. From the first glossaries carved into library catalogs to the description-logic engines powering modern biomedical ontologies, each rung on this ladder adds expressive power at a cost in complexity, tooling, and maintenance — and the climb from one rung to the next is marked by inflection points where genuinely new capabilities emerge.

---

## The Spectrum

What follows is a walk through eight levels of knowledge organization, ordered from the least to the most formally expressive. Each level subsumes the one below it: a taxonomy is a controlled vocabulary with hierarchy, a thesaurus is a taxonomy with equivalence and association, and so on. At every step, the question is not *whether* you are representing knowledge but *how much* of its structure you are committing to make machine-processable.

### Level 1 — Simple Dictionaries and Glossaries

**What it is.** A dictionary or glossary is the simplest form of a knowledge organization system (KOS): an alphabetical list of terms, each paired with a definition (ISKO, 2020, https://www.isko.org/cyclo/kos). The Getty Research Institute places glossaries and dictionaries at the least formal end of the KOS spectrum, noting that they contain "no relationships between terms" beyond the alphabetical ordering itself (Getty, 2004, https://www.getty.edu/research/tools/vocabularies/ward_stanford_kos.pdf).

**What relationships it can express.** None, structurally. The only ordering is alphabetical — a convenience for human lookup, not a semantic relationship.

**What it cannot express.** It cannot express hierarchy, synonymy, associative links, or any formal constraint. Two terms may be definitionally related, but the dictionary does not record that fact.

**Life-science example.** A lab's internal glossary of assay types — "ELISA: enzyme-linked immunosorbent assay" — defined in a spreadsheet for new team members. Each entry stands alone.

**Trade-off.** You gain the lowest possible creation and maintenance cost; every domain expert can write a glossary. You pay with zero machine-actionability: no software can traverse, infer, or query relationships that do not exist.

### Level 2 — Controlled Vocabularies

**What it is.** A controlled vocabulary is an authoritative, curated list of terms in which each term has a single, defined meaning and one preferred label, with variant labels (synonyms) mapped to the preferred form (KU Leuven RDM, 2024, https://www.kuleuven.be/rdm/en/guidance/documentation-metadata/vocabularies). The Library of Congress Name Authority File (LCNAF) is a paradigmatic example — an authoritative list of names used by libraries, where each entity receives a preferred label and known variants (LCNAF, 2024, https://id.loc.gov/download/). The National Library of Medicine describes MeSH as "a controlled and hierarchically-organized vocabulary" for indexing biomedical literature (MeSH, 2026, https://www.nlm.nih.gov/mesh/meshhome.html).

**What relationships it can express.** Equivalence between a preferred label and its variants — "synonym control." Each term points to exactly one meaning, disambiguating homonyms.

**What it cannot express.** Hierarchy, associative relations, or any formal semantic constraint. The vocabulary is a flat (or flat-with-synonyms) list.

**Life-science example.** MeSH's entry terms function as a controlled vocabulary layer: "Neoplasms" is the preferred descriptor, and "Cancer," "Tumour," and "Tumor" are mapped to it as entry terms.

**Trade-off.** You gain disambiguation and synonym control — a search for "Cancer" retrieves records indexed under "Neoplasms." You pay the curation cost of maintaining the preferred-label mappings, but you still cannot traverse from "Neoplasms" to "Melanoma" without hierarchy.

### Level 3 — Taxonomies

**What it is.** A taxonomy is a controlled vocabulary organized hierarchically, with concepts arranged in parent-child (IS-A or broader-narrower) relationships (ISKO, 2020, https://www.isko.org/cyclo/kos; datos.gob.es, 2020, https://datos.gob.es/en/noticias/taxonomies-and-thesauri-knowledge-organization-tools). The NCBI Taxonomy is a curated classification organizing organisms into a phylogenetic hierarchy with standard ranks, stable TaxIDs, and explicit parent-child IS-A links (NCBI, 2024, https://www.ncbi.nlm.nih.gov/books/NBK53758/).

**What relationships it can express.** Hierarchical (broader-narrower, parent-child) relationships: "Mammalia" IS-A "Chordata," "Homo sapiens" IS-A "Mammalia."

**What it cannot express.** Synonyms, associative relations, or formal logical constraints (ISKO, 2020). A taxonomy says that B is narrower than A, but not that B is *equivalent* to C or *associated with* D.

**Life-science example.** NCBI Taxonomy itself: every organism has a stable TaxID, and the hierarchy runs from the root of life down to individual species. A query for "Mammalia" can retrieve all descendants — but you cannot express that two species names are synonyms for the same organism, or that one organism is a *model organism for* another.

**Trade-off.** You gain structure: traversal, roll-up queries, and inheritance of properties from parent to child. You pay the curation cost of deciding *where* each concept belongs in the tree and maintaining a consistent IS-A semantics — a deceptively hard task.

### Level 4 — Thesauri

**What it is.** A thesaurus adds equivalence (synonym) and associative (related-term) relationships to the hierarchical structure of a taxonomy. MeSH is a thesaurus with descriptors organized in 16 hierarchical categories reaching up to 13 levels deep, with entry terms (synonyms), BT/NT (broader/narrower), and RT (related term) relationships (MeSH, 2026). The ERIC Thesaurus contains approximately 12,000 terms — 4,500+ descriptors and 7,000+ synonyms — with hierarchical, equivalence, and associative relationships (ERIC, 2025, https://eric.ed.gov/?faq-thesaurus).

**What relationships it can express.** Three kinds: hierarchical (BT/NT), equivalence (USE/UF — use/use-for), and associative (RT). This is the classic ANSI/NISO Z39.19 thesaurus triad.

**What it cannot express.** Formal logical constraints. As Hipertext.net notes, thesauri "represent conceptual structure through hierarchical, associative, and equivalence relations, but [have] limited semantic expressivity — for humans, not automatic machine reasoning" (Hipertext.net, 2006, https://arxiu-web.upf.edu/hipertextnet/en/numero-3/tesauros.html). You know that two terms are *related*, but not *how* or *why* — the RT relationship is unlabeled.

**Life-science example.** MeSH's RT links: "Neoplasms" has a related-term link to "Neoplastic Syndromes," but the thesaurus does not specify the nature of that relationship — is it *causes*, *is-a-type-of*, *co-occurs-with*? A human reading the MeSH tree files knows they are associated; a machine cannot reason about the association.

**Trade-off.** You gain the richest human-usable KOS: synonyms for retrieval, hierarchy for browsing, related terms for discovery. You pay with an RT relationship that is semantically opaque — the machine sees a link but cannot interpret it, which limits automated reasoning.

### Level 5 — Metadata Schemas and Element Sets

**What it is.** A metadata schema defines a set of properties (elements) for describing resources — a frame with named slots. Dublin Core defines 15 core properties for resource description, standardized as ISO 15836, ANSI/NISO Z39.85, and IETF RFC 5013 (Dublin Core, 2012, https://www.dublincore.org/specifications/dublin-core/dces/; RFC 5013, 2007, https://datatracker.ietf.org/doc/html/rfc5013). The DataCite Metadata Schema provides core metadata properties for resource identification via DOIs, with controlled lists for values but no formal ontological semantics (DataCite, 2024, https://schema.datacite.org/).

**What relationships it can express.** Typed attribute-value pairs: a resource *has a* "dc:title" with a string value, *has a* "dc:creator" with a name. The schema constrains which properties exist and what types their values take, but the properties themselves are not semantically defined beyond their labels.

**What it cannot express.** Formal semantics for the properties or the resources they describe. Dublin Core is, in the words of its own specification, a flat schema with no formal semantic constraints — "dc:creator" means what the community has agreed it means by convention, not by logical axiom.

**Life-science example.** A DataCite record for a dataset: `creator = "Jane Doe"`, `title = "Single-cell RNA-seq of mouse hippocampus"`, `publicationDate = "2024-03-15"`. The schema ensures these fields exist and are the right type, but does not define what "creator" *is* in a formal sense, or how it relates to "contributor."

**Trade-off.** You gain a shared, citable frame for description — every Dublin Core record can be understood by any system that knows the 15 elements. You pay with semantic looseness: two systems may use "dc:creator" to mean subtly different things, and nothing in the schema prevents that.

### Level 6 — Linked Data Vocabularies

**What it is.** A linked data vocabulary publishes KOS content as machine-readable RDF on the Web, with concepts identified by URIs, labels in multiple languages, and links between concepts across schemes. SKOS is the W3C recommendation for "sharing knowledge organization systems via the Web using RDF" — concepts are identified with URIs, labeled in multiple languages, linked into hierarchies and associations, and mapped across schemes (SKOS, 2009, https://www.w3.org/TR/skos-reference/). JSON-LD uses `@context` to map JSON keys to URLs, enabling machine-interpretable data at Web scale (JSON-LD Best Practices, 2024, https://w3c.github.io/json-ld-bp/). schema.org is a collaborative vocabulary from Google, Microsoft, Yahoo, and Yandex with a `Thing` class hierarchy, designed for machine readability via JSON-LD, Microdata, and RDFa (schema.org, 2024, https://schema.org/).

**What relationships it can express.** Everything a thesaurus can, plus global identity: each concept has a URI, so "MeSH:D009369" is addressable on the Web and can be linked to from any other dataset. SKOS supports `skos:exactMatch`, `skos:closeMatch`, `skos:broadMatch`, and `skos:narrowMatch` for cross-vocabulary mapping.

**What it cannot express.** Formal logical axioms or automated inference. SKOS is explicitly designed as a lightweight, semi-formal KOS language — it can say that two concepts are *related* or *matched*, but not that a class is a *subclass* of another with necessary conditions.

**Life-science example.** MeSH published as SKOS/RDF on the web: each MeSH descriptor becomes a URI (`http://id.nlm.nih.gov/mesh/D009369`), other datasets can link to it, and cross-walks to SNOMED CT or ICD can be expressed with `skos:exactMatch`. A SPARQL query can now retrieve all resources annotated with MeSH terms that are exact matches across vocabularies.

**Trade-off.** You gain global addressability and inter-dataset linking — the foundation of the Semantic Web. You pay the infrastructure cost: URIs must resolve, servers must stay up, and the RDF serialization must be maintained. SKOS gives you linked concepts, not reasoned facts.

### Level 7 — Knowledge Graphs

**What it is.** A knowledge graph (KG) is a graph of semantically described entities and their interrelations, typically encoded as RDF triples (subject, predicate, object) or as a property graph with typed nodes and edges. Färber et al. collect multiple definitions, including Paulheim's: "a knowledge graph mainly describes real world entities and their interrelations, organized in a graph" (Färber et al., 2016, https://ceur-ws.org/Vol-1695/paper4.pdf). KGs can be implemented as RDF-based graphs (queried with SPARQL) or as labeled property graphs (LPGs), with RDF offering standardized interoperability and LPGs offering flexible attributes at the cost of less standardization (arXiv, 2023, https://arxiv.org/html/2302.11509).

**What relationships it can express.** Arbitrary typed relationships between entities: `(drug, treats, disease)`, `(gene, encodes, protein)`, `(person, authored, publication)`. The graph can be queried traversally — find all drugs that treat diseases caused by mutations in gene X — because every edge has a label and a direction.

**What it cannot express.** In its base form (without an ontology layer), a knowledge graph cannot guarantee logical consistency or perform automated inference. The graph is a *collection of facts*, not a *theory*: it can tell you what is true but not derive what *must* be true given the axioms.

**Life-science example.** A biomedical KG linking drugs, targets, pathways, and diseases: `(imatinib, targets, ABL1)`, `(ABL1, participates_in, Philadelphia_chromosome_signaling)`, `(Philadelphia_chromosome_signaling, causes, CML)`. A graph query can traverse from drug to disease, but without an ontology layer, it cannot infer that if ABL1 is a tyrosine kinase and imatinib inhibits all tyrosine kinases in a class, then imatinib inhibits ABL1.

**Trade-off.** You gain queryable, traversable structure at scale — the power that drives Google's Knowledge Graph, Wikidata, and enterprise data fabrics. You pay with the complexity of graph modeling and the fact that a KG without an ontology layer is not guaranteed to be logically consistent: contradictions can coexist silently.

### Level 8 — Formal Ontologies

**What it is.** A formal ontology is a computational logic-based theory accounting for the intended meaning of a vocabulary — a set of classes, properties, individuals, and axioms expressed in a description logic. OWL 2 is the W3C recommendation for this, based on the SROIQ description logic, supporting class intersection, union, and complement, cardinality restrictions, property hierarchies, and automated inference (OWL 2 Primer, 2012, https://www.w3.org/TR/owl2-primer/). Guarino's influential definition frames an ontology as "a logical theory accounting for the intended meaning of a formal vocabulary" (Guarino, 1998, http://csis.pace.edu/~marchese/CS835/Lec9/guarino98formal.pdf), and Gruber's earlier and most-cited definition calls it "a specification of a conceptualization" — definitions of classes, relations, functions, and other objects (Gruber, 1993, https://tomgruber.org/writing/ontolingua-kaj-1993/).

**What relationships it can express.** Everything below, plus formal logical axioms: necessary and sufficient conditions for class membership, universal and existential restrictions, disjointness, cardinality, and property chains. An OWL reasoner can infer new facts (if X is a subclass of Y and Y is disjoint with Z, then X is disjoint with Z) and check consistency (if X is asserted to be both a Y and a Z, and Y and Z are disjoint, the ontology is inconsistent).

**What it cannot express.** Description logics deliberately trade expressivity for decidability — OWL 2 (SROIQ) cannot express arbitrary first-order logic, and some constructs (like the full arity of relations or arbitrary quantification) are outside its scope. The open-world assumption means absence of a statement is not a statement of absence.

**Life-science example.** OBI (the Ontology for Biomedical Investigations) is an OWL-DL ontology with 2500+ classes, 40+ relations, built on the BFO upper ontology (OBI, 2026, https://www.ebi.ac.uk/ols4/ontologies/obi). EDAM is a formal ontology of bioinformatics operations, data, identifiers, topics, and formats, with 2200+ concepts across four sub-ontologies, supporting machine-understandable annotation (EDAM, 2013, https://pmc.ncbi.nlm.nih.gov/articles/PMC3654706/). PROV-O is a W3C-recommended OWL2 ontology for provenance — entities, activities, and agents — with machine-processable axioms and class restrictions (PROV-O, 2013, https://www.w3.org/TR/2012/WD-prov-o-20120503/).

**Trade-off.** You gain automated reasoning, consistency checking, and inference — the machine can derive facts you never explicitly stated and flag contradictions you did not notice. You pay the highest cost: ontology engineering requires trained specialists, reasoners are computationally expensive at scale, and the open-world assumption can produce surprising results for implementers expecting closed-world SQL semantics.

---

## Historical Lineage

The idea that knowledge representation is a spectrum, not a dichotomy, did not arrive all at once. It has a lineage that stretches from early-twentieth-century philosophy of language through the knowledge-representation community of the 1980s and 1990s to today's FAIR data movement.

### Wittgenstein: Representation vs. Use

The deepest root is Ludwig Wittgenstein's tension between two views of language. In the *Tractatus Logico-Philosophicus* (1921), language is a logical picture of facts — a formal representation in which well-formed propositions mirror the structure of the world. In the later *Philosophical Investigations* (1953), meaning is instead "use in language games": fluid, contextual, and not reducible to a single formal calculus (SEP, 2026, https://plato.stanford.edu/archives/fall2026/entries/wittgenstein/). This tension — between language as a formal structure and language as a social practice — is the same tension that runs through the entire KOS spectrum, from glossaries (pure practice) to formal ontologies (pure structure).

### Brachman: Layered Classification

Ron Brachman's work on structured knowledge representation in the 1970s and 1980s, particularly the KL-ONE system and the classification of representational levels, introduced the idea that knowledge could be layered from implementational to logical levels. Brachman's levels — implementational, logical, epistemological, conceptual, and linguistic — provided the scaffolding upon which later spectra were built. The key insight was that each layer adds a *commitment* about what the representation means, and that these commitments can be made independently.

### Guarino: The Ontological Level

Nicola Guarino inserted a crucial new layer into Brachman's scheme. In his 1995 paper, Guarino introduced the "ontological level" between Brachman's epistemological and conceptual levels, drawing a distinction between sortal and non-sortal properties — some categories tell you *what kind of thing* an entity is (sortal), while others merely describe it (non-sortal) (Guarino, 1995, https://www.loa.istc.cnr.it/old/Papers/FormOntKR.pdf). In 1998, Guarino gave the field its working definition: "an ontology is a logical theory accounting for the intended meaning of a formal vocabulary," and distinguished top-level, domain, task, and application ontologies by their level of generality (Guarino, 1998). Later, Guarino (2009) described a continuum from informal representations (glossaries, hierarchies, folksonomies, thesauri) to formal ones (first-order logics, description logics), attributing the KR spectrum to the OKBC/Protégé community (Guarino, 2009, https://iaoa.org/isc2012/docs/Guarino2009_What_is_an_Ontology.pdf).

### Gruber: Ontology as Specification

Thomas Gruber's 1993 definition — "an ontology is a specification of a conceptualization" — became the most cited definition in ontology engineering (Gruber, 1993, https://tomgruber.org/writing/ontolingua-kaj-1993/). Its power was in its precision: a conceptualization is an abstract, simplified view of the world; a specification makes it concrete and shareable. Gruber's definition gave the field a common vocabulary for talking about *what* an ontology is, even as it left room for the spectrum of *how formal* that specification might be.

### Lassila & McGuinness: The Ontology Spectrum Figure

The explicit articulation of the spectrum as a graduated series of levels came from Ora Lassila and Deborah McGuinness in 2001. Their figure — published in the context of the Semantic Web — proposed a progression from controlled vocabularies through glossaries, informal taxonomies, formal taxonomies, frames, value restrictions, and general logical constraints. Everything to the right of "strict subclass hierarchy" on their axis qualified as an "ontology" (Lassila & McGuinness, 2001, https://www.ksl.stanford.edu/people/dlm/etai/lassila-mcguinness-fbr-sw.html). This is the figure that the present article traces and extends. The related "semantic staircase" concept — attributed to Olensky (2010) and Blumauer & Pellegrini (2006) — describes the same progression by semantic richness, using Guarino's "ontological precision" to distinguish lightweight from heavyweight ontologies (Ontologies as KOS, 2021, https://storage.imrpress.com/imr/journal/KO/article/504706/1752844994873.pdf).

### Berners-Lee: The Semantic Web and 5-Star Linked Data

Tim Berners-Lee, James Hendler, and Ora Lassila articulated the Semantic Web vision in 2001: web content with formal, machine-understandable meaning, enabled by "a taxonomy and a set of inference rules" (Berners-Lee et al., 2001, https://lassila.org/publications/2001/SciAm.html). The 5-Star Linked Data scheme made the spectrum actionable for data publishers: ★ on the Web, ★★ machine-readable, ★★★ non-proprietary format, ★★★★ W3C open standards, ★★★★★ links to other data (W3C, 2011, https://www.w3.org/2011/gld/wiki/5_Star_Linked_Data). Each star is an inflection point — adding it unlocks a new class of automated processing.

### Wilkinson et al.: The FAIR Principles

In 2016, Wilkinson and colleagues published the FAIR Guiding Principles — Findable, Accessible, Interoperable, Reusable — which mapped the spectrum onto the practical concerns of data repository builders (Wilkinson et al., 2016, https://link.springer.com/article/10.1038/sdata.2016.18). The Interoperability principles are where the KOS spectrum lives:

- **I1:** (Interoperability 1) Use formal, accessible, shared, and broadly applicable languages for knowledge representation.
- **I2:** (Interoperability 2) Use vocabularies that follow FAIR principles.
- **I3:** (Interoperability 3) Include qualified references to other (meta)data.

These three criteria are not binary checkmarks; they map directly onto the spectrum. A glossary satisfies none of them. A SKOS vocabulary satisfies I1 and I2. A formal ontology satisfies all three — and, critically, enables the *qualified* references of I3 because the meaning of each reference is defined by axioms, not just by a label.

---

## Inflection Points

Most of the spectrum is a gradual enrichment — adding synonyms, adding hierarchy, adding types. But four transitions are not gradual. Each is an inflection point where a qualitatively new capability emerges, changing what a downstream system can *do*, not just what it can *store*.

### Inflection 1 — Flat List → Hierarchy (Dictionary to Taxonomy): Structure Emerges

The jump from a flat list of terms to a parent-child hierarchy is the first structural inflection. Before it, terms are atoms with no bonds between them. After it, terms are nodes in a tree, and the tree *is* knowledge — it encodes the claim that "Mammalia is a kind of Chordata," a fact that was not present in the dictionary and could not be inferred from it. This unlocks roll-up queries (retrieve all species under Mammalia), inheritance (if Mammalia has a property, all its children inherit it), and hierarchical browsing. The NCBI Taxonomy exists at this inflection: without its tree, "Homo sapiens" and "Pan troglodytes" are just two names; with it, they are sister taxa under Hominidae.

### Inflection 2 — Hierarchy → Equivalence and Association (Taxonomy to Thesaurus): Related Terms

The second inflection adds the *kinds* of relationships that a pure hierarchy cannot carry. Synonymy (equivalence) means that a search for "cancer" retrieves records indexed under "neoplasms" — a retrieval capability that no taxonomy provides. Association (related terms) means that "neoplasms" and "neoplastic syndromes" are linked, even though neither is a subtype of the other. This inflection matters because it is the first time the KOS acknowledges that two concepts can be *related without being nested* — a primitive of the graph structure that knowledge graphs and ontologies will later exploit fully.

### Inflection 3 — Terms → URIs (Controlled Vocabulary to Linked Data): Global Identity

The third inflection is the jump from local, human-readable labels to global, machine-addressable identifiers. When a concept gets a URI, it ceases to be a string in a single database and becomes a *node in the global graph*. MeSH:D009369 as a string is a label; `http://id.nlm.nih.gov/mesh/D009369` as a resolvable URI is an address that any system, in any dataset, in any country, can point to unambiguously. This is the inflection that Berners-Lee's 5-Star scheme is built on: ★★★★ (W3C open standards) and ★★★★★ (links to other data) are only possible when identifiers are global. It is also the inflection that makes the FAIR I3 criterion — "qualified references" — meaningful: a reference is qualified when it points to a *defined* thing, not just a *labeled* one.

### Inflection 4 — Graphs → Logic (Knowledge Graph to Formal Ontology): Automated Reasoning

The fourth and most powerful inflection is the jump from a collection of asserted facts to a *theory* — a set of axioms that entail new facts. Before this inflection, a knowledge graph can tell you what is *stated*. After it, a reasoner can tell you what is *implied* — and, just as importantly, what is *inconsistent*. If OBI defines "assay" as a subclass of "planned process" and also defines a specific assay as a subclass of "device," the reasoner detects the contradiction because "planned process" and "device" are declared disjoint. No lower level of the spectrum can do this. This is the inflection that makes formal ontologies worth their enormous cost: they are the only level at which a machine can *discover* knowledge you did not explicitly encode.

---

## FAIR Principles Mapping

The three Interoperability criteria from Wilkinson et al. (2016) provide a practical lens for asking, at each level: *what can a machine do with this?*

| Level | I1: Formal, shared KR languages | I2: FAIR vocabularies | I3: Qualified references |
|---|---|---|---|
| 1. Dictionaries/Glossaries | ❌ No formal language | ❌ Not FAIR-structured | ❌ No references |
| 2. Controlled Vocabularies | ❌ (informal list) | ⚠️ Partially (if published as FAIR vocab) | ❌ No links |
| 3. Taxonomies | ⚠️ Partially (structured but not formally defined) | ⚠️ Partially | ❌ Internal-only relations |
| 4. Thesauri | ⚠️ Partially (ANSI/NISO standard, but not KR language) | ⚠️ Partially | ❌ Unlabeled relations |
| 5. Metadata Schemas | ⚠️ Partially (RFC 5013, ISO 15836 — formal *format*) | ✅ Yes (Dublin Core, DataCite are FAIR vocabularies) | ⚠️ Partially (DOI links, but not semantically qualified) |
| 6. Linked Data Vocabularies | ✅ Yes (RDF, SKOS, JSON-LD are W3C formal languages) | ✅ Yes (SKOS vocabularies are FAIR) | ⚠️ Partially (URIs link, but `skos:exactMatch` is not a formal axiom) |
| 7. Knowledge Graphs | ✅ Yes (RDF/SPARQL or property graphs) | ✅ Yes (if vocabularies are FAIR) | ⚠️ Partially (typed edges, but not axiomatically qualified) |
| 8. Formal Ontologies | ✅ Yes (OWL 2, description logic) | ✅ Yes (ontology URIs are FAIR) | ✅ Yes (axioms define *how* references are qualified) |

The pattern is clear: I1 (formal languages) is satisfied only from linked data upward, because below that level the representation is either not formal or not in a shared KR language. I2 (FAIR vocabularies) is satisfiable from metadata schemas upward, because Dublin Core and DataCite are published as FAIR vocabularies even without formal semantics. I3 (qualified references) is *fully* satisfied only at the formal ontology level, because only axioms can state *why* a reference is valid — not just that it exists.

For a NIAID Blueprint data repository aiming to be FAIR-compliant, the practical guidance is: **levels 5–6 are the minimum for interoperability; level 8 is required for full machine-actionability and automated validation.**

---

## The Spectrum Diagram

The following is a textual rendering of the spectrum, arranged on a horizontal axis from **human-readable** (left) to **machine-reasonable** (right). Each level is placed at its approximate position, with the four inflection points marked between the levels they separate.

```
Human-readable ◀──────────────────────────────────────────────▶ Machine-reasonable

  Dictionaries    Controlled     Taxonomies    Thesauri    Metadata     Linked Data    Knowledge     Formal
  /Glossaries     Vocabularies                              Schemas      Vocabularies    Graphs       Ontologies

  ●━━━━━━━━━━━━━━━●━━━━━━━━━━━━━━●━━━━━━━━━━━━━━●━━━━━━━━━━━━●━━━━━━━━━━━━━●━━━━━━━━━━━━━━●━━━━━━━━━━━━━●
  L1               L2              L3              L4            L5             L6              L7             L8

       ▲ Inflection 1     ▲ Inflection 2                    ▲ Inflection 3                    ▲ Inflection 4
       Flat → Hierarchy   Hierarchy →                        Terms → URIs                       Graphs → Logic
       Structure           Equivalence/                        Global identity                   Automated reasoning
       emerges             Association                        Machine-
                           Related terms                      addressability

  MeSH entry         LCNAF          NCBI           MeSH          Dublin Core    SKOS MeSH      Wikidata         OBI
  terms              (preferred     Taxonomy       (full         (15 elements)  (RDF/RDF)       (RDF triples)    EDAM
  (spreadsheet)       labels)        (TaxIDs)       thesaurus)                                                    PROV-O
```

Reading left to right: the first inflection (L1→L3) is where structure appears — the flat list becomes a tree. The second (L3→L4) is where non-hierarchical relationships (synonyms, related terms) appear. The third (L5→L6) is where terms become global URIs and the data becomes addressable on the Web. The fourth (L7→L8) is where facts become a theory and the machine can reason, not just retrieve.

The life-science examples cluster instructively: MeSH appears at *three* levels depending on how it is published — as entry terms (L1–L2), as a full thesaurus (L4), or as SKOS/RDF (L6). NCBI Taxonomy sits at L3 as a pure hierarchy. OBI, EDAM, and PROV-O sit at L8 as formal OWL ontologies. This is not an accident: a single resource can be expressed at multiple levels of the spectrum, and *which level you publish at determines what consumers can do with it*.

---

## Closing: Which Level Do You Need?

For someone building AI-ready data repositories — particularly in the NIAID Blueprint context — the choice of knowledge representation level is not aspirational; it is practical. Each level answers a different question:

- **"Can humans find the right term?"** → You need a **dictionary or controlled vocabulary** (L1–L2). This is the floor: if your data elements are not even disambiguated, nothing downstream works.
- **"Can users browse and roll up?"** → You need a **taxonomy** (L3). NCBI Taxonomy is the model: stable IDs, parent-child links, traversal from root to leaf.
- **"Can users discover related concepts and synonyms?"** → You need a **thesaurus** (L4). MeSH is the model: BT/NT/RT/USE in one structure.
- **"Can machines across the web link to my terms?"** → You need **linked data** (L6). Publish your thesaurus as SKOS with resolvable URIs. This is the minimum for FAIR I1 and I2.
- **"Can machines reason about my data — infer, validate, detect contradictions?"** → You need a **formal ontology** (L8). OBI, EDAM, and PROV-O are the models: OWL axioms, description logic, reasoner-checked consistency.

The most common mistake is to assume that "more formal is always better." It is not. A formal ontology that is never reasoner-checked, never maintained, and never consumed by any inference engine is a thesaurus with expensive overhead. The spectrum is a *menu of capabilities*, and the right level is the one that matches what your downstream systems — human or machine — actually need to do.

The second most common mistake is to assume that a single level suffices for a whole repository. In practice, most mature data ecosystems occupy multiple levels simultaneously: a SKOS thesaurus (L6) for discovery, a metadata schema (L5) for citation, and a formal ontology (L8) for the core domain model that must be logically consistent. The FAIR principles do not require you to pick one; they require you to be *deliberate* about which level you are operating at, and to ensure that each level you use is itself FAIR.

The spectrum has existed for as long as people have organized knowledge. What is new is the clarity with which we can see it — and the precision with which we can choose where on it to stand.