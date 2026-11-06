# Making Your Repository More Accessible to AI

**Supplementary materials for the Phase III NIAID Blueprint webinar (6 November 2026).**

> NOTE:  Foundational drafts of many glossary entries, section outlines, and bibliography items were produced with generative AI assistance. These were then read, revised, corrected, and expanded by the author(s). Human judgment determined what was kept, rewritten, or discarded. Sources cited in the bibliography were verified against the original pages (with exceptions noted where access was blocked). The author(s) take full responsibility for the content of these materials.


## Files

 [**Presentation Slides**](slideDeckSIReadyRepos.pdf)

These files are handouts, not a second copy of the slides. Definitions stay in the glossary. Sources stay in the bibliography. A longer note is a separate file, linked from the matching section below.


| File | Who it is for | What it is |
|---|---|---|
| [Glossary](glossary.md) | Anyone using the deck’s words | Short working definitions, in talk order. Not the full specification of each standard. |
| [Bibliography](bibliography.md) | Anyone following a citation | Each source once, grouped like the glossary. Titles checked against the pages, except where a site blocked the fetch. |
| [Identifying agents](supplementalInformation/agentIdentification.md) | Site owners identifying automated visitors | Compares User-Agent strings, IP ranges, Web Bot Auth, CDN services, and behavioral signals, including their limitations. |
| [Evaluation](supplementalInformation/evaluation.md) | Teams checking documentation for agent use | Distinguishes access and readability checks, answerability tests, and content-accuracy checks. |
| [Evaluation prompts](supplementalInformation/evaluationPrompts.md) | Someone following the talk live | Which prompt to try in each "Be" section, and how to run it in ChatGPT, Claude, Grok, or a harness. |
| [TDM reservations](supplementalInformation/tdm.md) | Site owners considering text and data mining policies | Explains TDM reservations and related signals (TDMRep, and how they differ from robots.txt, AIPREF, and RSL). |
| [From terms to ontologies](supplementalInformation/termsToOntologies.md) | Technical teams choosing how to represent knowledge | Compares vocabulary structures and formal semantics, with guidance for choosing a proportionate approach. |
| [Vocabulary tools and resources](supplementalInformation/vocabularies.md) | Teams creating or reusing vocabularies | Surveys vocabulary editors, spreadsheet workflows, publishing tools, and reuse resources. |
| [Competency questions](compQuestions/) | Someone running those tests on NIAID sites | Competency questions and separate answer keys. Do not paste a key into the prompt an agent sees. |
| [Assets examples](assets/) | Someone looking for a concrete file | Example `robots.txt`, `sitemap.xml`, `llms.txt`, and `ard.json`. |



## Adventures

These are some of the harnesses, skills, prompts and other artifacts and approaches I tried during the creation of this presentation.  They are rough, but shared in case anyone finds them interesting. 

### Eval prompts

A collection of evaluation prompts for exploring some of
the concepts presented in the webinar has been made. 
You can explore these more in the docs the 
[evalPrompts.md document.](../evalPrompts.md)

 
### Competency Questions

A collection of competency questions.  They are all auto-generated, so buyer beware.   These are being used more
to explore the concept of competency questions and how they could be used in evaluation of SI enhancements to a repo. .  They are far from production, but they are a start.  See [these notes.](compQuestions/README.md)


### Harness
A harness built around Pi (https://pi.dev) exposes a collection of skills and prompts.  There are [instructions for starting](https://github.com/go-fair-us/ai-blueprint-core/blob/master/HARNESS_QUICKSTART.md) but it is very developmental.  If you try it, I'd love to hear from you.  Tag me in the issues.  

### Glossary to SKOS
This is a test of a partial conversion of the glossary to SKOS via an LLM.  It is just a test to see how good a model can be at making a SKOS vocabulary.   In this end, making this a skill with validation and better context would be a big improvement.  However, this simple single shot test was impressive enough out of the gate, that is people wanted this, it should be doable. I is a start.  See [these notes.](assets/glossary2SKOS/README.md)
