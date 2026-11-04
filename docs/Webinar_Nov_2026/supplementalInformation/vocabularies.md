# Vocabulary Tools and Resources  

The following is a collection of resources from the net related to authoring vocabularies.

--- 
## Quick recommendation

| Need | Start with |
|------|------------|
| Absolute simplest / domain experts | SKOS Play Excel converter or voc4cat-style Excel + GitHub |
| Easy web thesaurus editor | TemaTres |
| Collaborative / production / multi-user | VocBench |
| Pure browser, no install | Intentional Arrangement SKOS or similar |

For non-SKOS vocabularies (plain lists, OWL ontologies, etc.), the same Excel approaches or Protégé cover most cases. Most of these tools support import/export so you can start simple and move to a fuller system later.

If you describe the scale (small list vs. large hierarchical thesaurus), whether it needs collaboration/multilingual support, or your preferred interface (Excel, web form, desktop), I can narrow it further or point to specific templates/setup notes.


## Simplest options (especially good for non-RDF experts) 

- **SKOS Play!** (https://skos-play.sparna.fr/ or the labs version)  
  Online free/open-source tool. Its strongest simple feature is converting Excel (or Google Sheets) spreadsheets into SKOS RDF using straightforward templates. You can also visualize, print to HTML/PDF, and do basic validation. Ideal for getting started quickly—download an example spreadsheet, fill in concepts/labels/relations, and convert. Code is on GitHub (Sparna).

- **Excel + conversion tools**  
  - **voc4cat-tool** (and related templates): Maintains SKOS in Excel, converts to Turtle/RDF, validates (including SHACL), and works well with GitHub for versioning/collaboration.  
  - **VocExcel** / xls2rdf (the engine behind SKOS Play’s converter): Similar spreadsheet-to-SKOS approach with templates.  
  These let domain experts work in spreadsheets while producing valid SKOS.

- **Browser-only editors**  
  Tools like **Intentional Arrangement SKOS** (static web app, no server needed) let you build, validate, and export SKOS taxonomies directly in the browser. Other lightweight web editors (e.g., Vocabseditor) exist for collaborative work.

## Full-featured open-source management systems

These provide proper editing UIs, hierarchy management, multilingual support, import/export, and often publishing features:

- **TemaTres** — Lightweight web application (PHP/MySQL) specifically for controlled vocabularies, thesauri, taxonomies, and glossaries. Term-based interface, exports to SKOS, supports multiple vocabularies, and has demos/Docker options. Very approachable.  
- **VocBench** — The most mature collaborative platform. Web-based, handles SKOS/SKOS-XL, OWL ontologies, OntoLex, and generic RDF. Strong workflow, multilingual support, and used by many institutions (including the EU Publications Office). More setup required (typically with a triplestore) but excellent for serious or multi-user work.  
- **iQvoc** — SKOS(-XL) vocabulary management system with a clean web interface for editing and publishing.  
- **OpenTheso** — Another solid open-source option for thesauri with SKOS support.

## Other useful tools

- **Protégé** (or WebProtégé) — Free desktop/web ontology editor. You can model SKOS vocabularies as RDF or use plugins; best if you already work with OWL or want more expressive modeling.  
- **Publishing/browsing**: Once you have SKOS, tools like **Skosmos** make nice public interfaces (search, hierarchy, multilingual).  
- **Validation**: qSKOS (or features in SKOS Play/voc4cat) for quality checks.  
- Wiki-style alternatives: Semantic MediaWiki or Wikibase if you prefer that workflow.

# Notes to incorporate

https://pmc.ncbi.nlm.nih.gov/articles/PMC7121563/

https://bioportal.bioontology.org/ontologies/MHCRO

https://skos-play.sparna.fr/play/

A recent addition Jessica Talisman's  SKOS tool at: https://github.com/jesstalisman-ia/intentional-arrangement-skos    

https://obofoundry.org/resources   

