# Making Your Repository More Accessible to AI

Supplementary materials for the Phase III NIAID Blueprint webinar (6 November 2026).

> NOTE:  Foundational drafts of many glossary entries, section outlines, and bibliography items were produced with generative AI assistance. These were then read, revised, corrected, and expanded by the author(s). Human judgment determined what was kept, rewritten, or discarded. Sources cited in the bibliography were verified against the original pages (with exceptions noted where access was blocked). The author(s) take full responsibility for the content of these materials.

[Presentation Slides](slideDeckSIReadyRepos.pdf)

These files are handouts and working notes, not a second copy of the slides. Definitions stay in the glossary. Sources stay in the bibliography. A longer note is a separate file, linked from the matching section below.

## Files

| File | Who it is for | What it is |
|---|---|---|
| [Glossary](glossary.md) | Anyone using the deck’s words | Short working definitions, in talk order. Not the full specification of each standard. |
| [Bibliography](bibliography.md) | Anyone following a citation | Each source once, grouped like the glossary. Titles checked against the pages, except where a site blocked the fetch. |
| [Identifying agents](supplementalInformation/agentIdentification.md) | Site owners identifying automated visitors | Compares User-Agent strings, IP ranges, Web Bot Auth, CDN services, and behavioral signals, including their limitations. |
| [Evaluation](supplementalInformation/evaluation.md) | Teams checking documentation for agent use | Distinguishes access and readability checks, answerability tests, and content-accuracy checks. |
| [Evaluation prompts](supplementalInformation/evaluationPrompts.md) | Someone following the talk live | Which prompt to try in each "Be" section, and how to run it in ChatGPT, Claude, Grok, or a harness. |
| [TDM reservations](supplementalInformation/tdm.md) | Site owners considering text and data mining policies | Explains TDM reservations and related signals; draft. |
| [From terms to ontologies](supplementalInformation/termsToOntologies.md) | Technical teams choosing how to represent knowledge | Compares vocabulary structures and formal semantics, with guidance for choosing a proportionate approach. |
| [Vocabulary tools and resources](supplementalInformation/vocabularies.md) | Teams creating or reusing vocabularies | Surveys vocabulary editors, spreadsheet workflows, publishing tools, and reuse resources. |
| [Competency questions](compQuestions/) | Someone running those tests on NIAID sites | Competency questions and separate answer keys. Do not paste a key into the prompt an agent sees. |
| [Assets examples](assets/) | Someone looking for a concrete file | Example `robots.txt`, `sitemap.xml`, `llms.txt`, and `ard.json`. |

## Talk sections

The glossary and the bibliography use the same headings. **Why do this** and **Acknowledgements** are citation groups only. The glossary does not define them.

| Talk section | Definitions | Sources | Longer note |
|---|---|---|---|
| Why do this | — | [Why do this](bibliography.md#why-do-this) | — |
| Systems and roles | [Systems and roles](glossary.md#systems-and-roles) | — | — |
| Who visits | [Who visits](glossary.md#who-visits) | [Who visits](bibliography.md#who-visits) | [Identifying agents](supplementalInformation/agentIdentification.md) |
| Being reachable | [Being reachable](glossary.md#being-reachable) | [Being reachable](bibliography.md#being-reachable) | [Identifying agents](supplementalInformation/agentIdentification.md) |
| Being readable | [Being readable](glossary.md#being-readable) | [Being readable](bibliography.md#being-readable) | [assets/](assets/) |
| Being callable | [Being callable](glossary.md#being-callable) | [Being callable](bibliography.md#being-callable) | — |
| Being meaningful | [Being meaningful](glossary.md#being-meaningful) | [Being meaningful](bibliography.md#being-meaningful) | [From terms to ontologies](supplementalInformation/termsToOntologies.md); [Vocabulary tools and resources](supplementalInformation/vocabularies.md); [Competency questions](compQuestions/competency_questions.md) |
| Rights, credit, and lineage | [Rights, credit, and lineage](glossary.md#rights-credit-and-lineage) | [Rights, credit, and lineage](bibliography.md#rights-credit-and-lineage) | [TDM reservations](supplementalInformation/tdm.md) (draft) |
| Checking the result | [Checking the result](glossary.md#checking-the-result) | [Checking the result](bibliography.md#checking-the-result) | [Evaluation guide](supplementalInformation/evaluation.md); [Prompts to try](supplementalInformation/evaluationPrompts.md); [evaluation prompts](../evalPrompts.md); [answerability runs](compQuestions/answerability_runs.md) |
| Acknowledgements | — | [Acknowledgements](bibliography.md#acknowledgements) | — |

 