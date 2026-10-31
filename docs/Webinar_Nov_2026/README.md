# Making Your Repository More Accessible to AI

Supplementary materials for the Phase III NIAID Blueprint webinar (6 November 2026).

[Deck (Google Slides)](https://docs.google.com/presentation/d/1_LlLl9GZ2Vy_t4URCCFUWx8CVfqN6jcOj_J7pnD5qYg/edit) · local copy: [slideDeckSIReadyRepos.pdf](slideDeckSIReadyRepos.pdf)

These files are handouts and working notes, not a second copy of the slides. Definitions stay in the glossary. Sources stay in the bibliography. A longer note is a separate file, linked from the matching section below.

## What each file is for

| File | Who it is for | What it is |
|---|---|---|
| [glossary.md](glossary.md) | Anyone using the deck’s words | Short working definitions, in talk order. Not the full specification of each standard. |
| [bibliography.md](bibliography.md) | Anyone following a citation | Each source once, grouped like the glossary. Titles checked against the pages, except where a site blocked the fetch. |
| [supplementalInformation/](supplementalInformation/) | Someone who needs more than a glossary line | Briefings and drafts. Finished pieces can be handed out. Drafts are still speaker prep. |
| [evalPrompts.md](evalPrompts.md) | Someone testing a repository | Catalog of the single-question prompts in `prompts/evals`. This file does not contain the prompts. |
| [compQuestions/](compQuestions/) | Someone running those tests on NIAID sites | Competency questions and separate answer keys. Do not paste a key into the prompt an agent sees. |
| [assets/](assets/) | Someone looking for a concrete file | Example `robots.txt`, `sitemap.xml`, `llms.txt`, and `ard.json`. |

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
| Being meaningful | [Being meaningful](glossary.md#being-meaningful) | [Being meaningful](bibliography.md#being-meaningful) | [Competency questions](compQuestions/competency_questions.md) |
| Rights, credit, and lineage | [Rights, credit, and lineage](glossary.md#rights-credit-and-lineage) | [Rights, credit, and lineage](bibliography.md#rights-credit-and-lineage) | [TDM reservations](supplementalInformation/tdm.md) (draft); [authority and authorization](supplementalInformation/authorityAuthorization.md) (speaker notes) |
| Checking the result | [Checking the result](glossary.md#checking-the-result) | [Checking the result](bibliography.md#checking-the-result) | [Evaluation prompts](evalPrompts.md); [answerability runs](compQuestions/answerability_runs.md) |
| Acknowledgements | — | [Acknowledgements](bibliography.md#acknowledgements) | — |

## Adding more

Add a new file under `supplementalInformation/` when a glossary entry is no longer enough, and add one row or one cell in the table above. Put any new canonical source in [bibliography.md](bibliography.md), once. Do not paste the essay into the glossary, and do not fold answer keys into a public handout.
