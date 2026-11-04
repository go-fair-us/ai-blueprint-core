# Vocabulary Tools and Resources  

The following is a collection of resources from the net related to authoring vocabularies.

--- 
## Quick recommendation

| Need | Start with |
|------|------------|
| Absolute simplest / domain experts | [SKOS Play](https://skos-play.sparna.fr/play/) or [voc4cat-tool](https://github.com/nfdi4cat/voc4cat-tool) with Excel and GitHub |
| Easy web thesaurus editor | [TemaTres](https://vocabularyserver.com/tematres/) |
| Collaborative / production / multi-user | [VocBench](https://vocbench.uniroma2.it/) |
| Pure browser, no install | [Intentional Arrangement SKOS](https://jesstalisman-ia.github.io/intentional-arrangement-skos/) |

For non-SKOS vocabularies (plain lists, OWL ontologies, etc.), spreadsheet tools or [Protégé](https://protege.stanford.edu/) may be a better fit. Import and export options vary by tool and template, so check that the data you need is preserved before moving between systems; do not assume conversions are lossless.

If you describe the scale (small list vs. large hierarchical thesaurus), whether it needs collaboration/multilingual support, or your preferred interface (Excel, web form, desktop), I can narrow it further or point to specific templates/setup notes.


## Simplest options (especially good for non-RDF experts) 

- **[SKOS Play!](https://skos-play.sparna.fr/play/)** ([source code](https://github.com/sparna-git/skos-play))  
  A web tool for converting spreadsheet templates into SKOS RDF, visualizing vocabularies, and publishing HTML or PDF views. Its converter is [xls2rdf](https://github.com/sparna-git/xls2rdf), which is also available as a separate project. Start with one of the examples, fill in concepts, labels, and relationships, then inspect the generated RDF and validation results.

- **Excel + conversion tools**  
  - **[voc4cat-tool](https://github.com/nfdi4cat/voc4cat-tool)** and its [repository template](https://github.com/nfdi4cat/voc4cat-template): an Excel-and-GitHub workflow for maintaining SKOS vocabularies, with conversion and quality checks.  
  - **[VocExcel](https://github.com/RDFLib/VocExcel)**: a separate project for converting templated Excel workbooks to SKOS RDF.  
  - **[xls2rdf](https://github.com/sparna-git/xls2rdf)**: another Excel-to-RDF converter, used by SKOS Play; it supports more than SKOS, including RDF graph data and SHACL constraints.  
  Spreadsheet workflows let domain experts edit familiar tables while producing RDF, but the templates and supported features differ across projects.

- **Browser-only editors**  
  - **[Intentional Arrangement SKOS](https://jesstalisman-ia.github.io/intentional-arrangement-skos/)** is a static browser app for creating, validating, and exporting SKOS without an account or server; see its [source repository](https://github.com/jesstalisman-ia/intentional-arrangement-skos) and [license notice](https://github.com/jesstalisman-ia/intentional-arrangement-skos/blob/main/LICENSE). The code is source-available under a size-based dual license, not an unrestricted open-source license: the notice says legal entities with 75 or more total employees, including related entities, need separate written terms. Check the current terms before adopting it.
  - **[Vocabseditor](https://github.com/acdh-oeaw/vocabseditor)** is a web-based tool for collaborative controlled-vocabulary development.

## Full-featured open-source management systems

These provide proper editing UIs, hierarchy management, multilingual support, import/export, and often publishing features:

- **[TemaTres](https://vocabularyserver.com/tematres/)** — A web application for managing controlled vocabularies, thesauri, taxonomies, and glossaries; it can publish vocabularies in SKOS.  
- **[VocBench](https://vocbench.uniroma2.it/)** — A collaborative web platform for editing SKOS/SKOS-XL, OWL, OntoLex, and other RDF resources. It offers multilingual and workflow features, with more deployment and administration overhead than a spreadsheet workflow.  
- **[iQvoc](https://github.com/innoq/iqvoc)** — A SKOS(-XL) vocabulary management system for editing and publishing vocabularies.  
- **[OpenTheso](https://github.com/MOM-CNRS/Opentheso)** — An open-source thesaurus management application with SKOS support.

## Find and reuse existing vocabularies

Before building a new vocabulary, search for one that already covers the subject. [BioPortal](https://bioportal.bioontology.org/) catalogs biomedical ontologies and vocabularies; its [MHC Restriction Ontology (MHCRO) entry](https://bioportal.bioontology.org/ontologies/MHCRO) is an example of a reusable domain resource, not an authoring tool. The [OBO Foundry resources page](https://obofoundry.org/resources) points to tools and services for finding, developing, and using ontologies in the life sciences. Reuse can improve consistency, but check a resource’s scope, version, license, and maintenance status before depending on it.

For a case study of why explicit vocabulary and ontology development can matter in biology, see [Ontology Development for the Immune Epitope Database](https://pmc.ncbi.nlm.nih.gov/articles/PMC7121563/). The paper describes how domain experts and ontology specialists worked together to represent immune-epitope data consistently; it is a development example, not a software recommendation.

## Other useful tools

- **[Protégé](https://protege.stanford.edu/)** and [WebProtégé](https://webprotege.stanford.edu/) — Free ontology editors for desktop and web. They support OWL and RDF-based modeling, including SKOS vocabularies; they are most useful when you need ontology editing rather than just a spreadsheet workflow.  
- **Publishing/browsing**: Once you have SKOS, [Skosmos](https://skosmos.org/) can provide a public interface for search, hierarchy browsing, and multilingual labels.  
- **Validation**: [qSKOS](https://github.com/cmader/qSKOS) checks SKOS vocabularies for common quality issues; SKOS Play and voc4cat-tool also provide quality checks within their workflows.  
- **Wiki-style alternatives**: [Semantic MediaWiki](https://www.semantic-mediawiki.org/wiki/Semantic_MediaWiki) and [Wikibase](https://wikiba.se/) may suit teams that prefer collaborative, wiki-style editing.
