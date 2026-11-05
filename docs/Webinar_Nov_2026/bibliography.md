# Bibliography and Further Details

Sources from **Making Your Repository More Accessible to SI** (*Phase III NIAID Slides 11/6*, NIAID Blueprint webinar, 6 November 2026). The live deck and PDF use **SI** in the talk title; earlier handout drafts said **AI**.

[Presentation Slides](slideDeckSIReadyRepos.pdf)

Grouped by the same sections as [glossary.md](glossary.md). **Why do this** and **Acknowledgements** are extra: the deck cites them, and the glossary does not define them. Each source is listed once.

Where these handouts correct a date, draft number, or URL that still appears on the live slides, the discrepancy is noted so the slide deck can be updated separately.

## Agenda & Scope

1. [GoFAIR US webinar supplemental materials](https://github.com/go-fair-us/ai-blueprint-core/tree/master/docs/Webinar_Nov_2026).

As mentioned on this slide, there will be more focus on metadata elements than the
data elements.  If we had addressed data it would have touched on some of the following

* Dataset-level documentation standards (Datasheets for Datasets style or equivalent structured cards)
* Explicit characterization of completeness
* quality metrics
* known biases
* recommended uses
* ML-oriented packaging
  * train/val/test splits
  * columnar formats such as Parquet
  * streaming/range-request patterns
* Governance and responsible-use policies expressed in machine-actionable form such as:
  * ODRL
  * DUO
  * Croissant RAI fields


## Why do this

1. Russo, Marissa. “NIH joins Trump’s $5B AI mission with biomedical research push.” *Fierce Biotech*, 22 July 2026. Cited for the NIH Bio Genesis Mission.
   https://www.fiercebiotech.com/research/hhs-joins-trumps-artificial-intelligence-genesis-mission

2. “NIH Launches Bio Genesis Mission to Accelerate AI-Driven Biomedical Discovery.” *ASCO AI in Oncology*, July 2026. Cited for the NIH Bio Genesis Mission. https://ascoai.org/articles/2026/07/nih-launches-bio-genesis-mission-to-accelerate-ai-driven-biomedical-discovery/

3. “Bridge to Artificial Intelligence (Bridge2AI).” NIH Common Fund. Cited for Bridge2AI Stage 1.
   https://commonfund.nih.gov/bridge2ai

4. “NIH Bridge2AI Stage 2: Inside the $130 Million Push to Make Health Data Actually Work for AI.” *Granted AI*. Cited for Bridge2AI Stage 2, approved early 2026.
   https://grantedai.com/blog/nih-bridge2ai-stage-2-130-million-health-ai-datasets-strategy-2026

5. “NIH Injects $130M to Provide Quality Tools, Data for AI in Medicine.” *Nextgov/FCW*, September 2022. Cited for the original Bridge2AI investment.
  https://www.nextgov.com/artificial-intelligence/2022/09/nih-injects-130m-provide-quality-tools-data-ai-medicine/377095/

6. “AIM-AHEAD.” Data Science at NIH. Cited in the speaker notes for the NIH network on AI/ML research capacity.  https://datascience.nih.gov/super-intelligence/aim-ahead

7. “AIM-AHEAD.” University of Houston Population Health. Second note source for AIM-AHEAD. https://www.uh.edu/population-health/research/aim-ahead.php

8. “DOE, NIH, and Biohub Partner to Build Foundational Data for Predictive Biological Super Intelligence Models.” U.S. Department of Energy, Office of Science. Cited for the predictive-biology partnership announced 7 October 2026 (deck / PDF date).
   https://www.energy.gov/science/articles/doe-nih-and-biohub-partner-build-foundational-data-predictive-biological-super

9. “Fact Sheet: Trump Administration Announces the Most Ambitious Set of Science Initiatives This Century.” The White House, October 2026. Cited in the notes beside the DOE–NIH–Biohub partnership.
   https://www.whitehouse.gov/fact-sheets/2026/10/fact-sheet-trump-administration-announces-the-most-ambitious-set-of-science-initiatives-this-century/

10. “Secretary of Energy Chris Wright Announces First Genesis Mission Projects Selected to Accelerate AI-Driven Scientific Discovery.” U.S. Department of Energy, 22 July 2026. Cited for the first-round project count (278 projects, 342 institutions).
    https://www.energy.gov/articles/secretary-energy-chris-wright-announces-first-genesis-mission-projects-selected-accelerate

11. Cho, Adrian. “Department of Energy expands ‘Genesis Mission’ to boost AI, awarding larger grants.” *Science*, 9 October 2026. Cited for Genesis Mission scale and spending.
    https://www.science.org/content/article/department-energy-expands-genesis-mission-boost-ai-awarding-larger-grants

12. “U.S. Department of Energy Announces More Than $800 Million in Partner Commitments to the Genesis Mission.” U.S. Department of Energy, Office of the Under Secretary for Science, 22 July 2026. Cited for consortium partner commitments.
    https://www.energy.gov/undersecretaryforscience/articles/us-department-energy-announces-more-800-million-partner

13. “Energy Department Announces New Genesis Mission Awards to Advance Super Intelligence for Science.” U.S. Department of Energy, 8 October 2026. Cited in the longer note for the later Phase I/II additions and the $159 million Phase II round.
    https://www.energy.gov/articles/energy-department-announces-new-genesis-mission-awards-advance-super-intelligence-science

14. “Trump Administration Announces More Than $5 Billion for the Genesis Mission, a National Mission on AI for Science.” The White House, 22 July 2026. Cited for the cross-agency funding figure.
    https://www.whitehouse.gov/releases/2026/07/45502/

## Who visits

1. Ostendorff, Malte. “Host-Aware Web Crawling for LLM Pretraining Data.” arXiv:2610.13321, submitted 9 October 2026. Computer Science > Computation and Language. Cited for the claim that trainer crawlers judge a repository by sampling a few pages, so landing-page and record-page quality decide how deep the crawl goes. No DOI is given in the deck or on the arXiv record used here.
    https://arxiv.org/abs/2610.13321

2. AI Ranked Editorial. “AI Crawler Access Study: robots.txt and llms.txt of 261 Major Websites (Oct 2026).” Zenodo, 11 October 2026. Dataset cited on the user-agent slide (S11) for training- vs search-crawler block rates. Preferred cite over the stale Mendeley dataset still named in some speaker notes.
    https://doi.org/10.5281/zenodo.23303786

## Being reachable

1. Markman, Jon. “Cloudflare Says AI Agent Traffic Grew More Than 1,700% in the Past Year.” *Forbes*, 1 October 2026. Printed as the source for “+1,700%” growth in daily AI agent requests and “>50%” non-human traffic on major CDNs. The title is taken from the URL. The page itself blocked a direct fetch.
    https://www.forbes.com/sites/jonmarkman/2026/10/01/cloudflare-says-ai-agent-traffic-grew-more-than-1700-in-the-past-year/


2. [Kong developer documentation](https://developer.konghq.com/). Documentation for Kong’s API gateway and related tools.

3. [Caddy web server](https://caddyserver.com/). Project site and documentation for the Caddy web server.


4. “Giving users choice with Cloudflare’s new Content Signals Policy.” Cloudflare Blog. Vendor policy for separating search, AI-input, and training uses. Distinct from Cloudflare’s default AI-bot block controls and from the IETF AIPREF vocabulary.
    https://blog.cloudflare.com/content-signals-policy/

5. “Overview of OpenAI Crawlers.” OpenAI API docs. An example of a crawler’s published user-agent policy.
    https://developers.openai.com/api/docs/bots

6. “Perplexity Crawlers.” Perplexity docs. A second crawler policy example.
    https://docs.perplexity.ai/docs/resources/perplexity-crawlers

IETF AI Preferences (verified against the Datatracker; live speaker notes still cite vocab **-07**):

- Keller, P., and M. Thomson, ed. “A Vocabulary For Expressing AI Usage Preferences.” IETF Internet-Draft, `draft-ietf-aipref-vocab-08`, 14 September 2026.
  https://datatracker.ietf.org/doc/html/draft-ietf-aipref-vocab-08
- Illyes, G., and M. Thomson, ed. “Associating AI Usage Preferences with Content in HTTP.” IETF Internet-Draft, `draft-ietf-aipref-attach-05`, 19 August 2026. Defines the `Content-Usage` robots.txt rule and HTTP header (for example `Content-Usage: train-ai=n`). Still an Internet-Draft.
  https://datatracker.ietf.org/doc/html/draft-ietf-aipref-attach-05

Really Simple Licensing (RSL), also named on the rights slide:

- “Really Simple Licensing (RSL) 1.0 Specification.” RSL Collective. `License:` in `robots.txt` must be an absolute URL to a separate RSL XML document.
  https://rslstandard.org/rsl

## Being readable

1. “sitemaps.org — Protocol.” The XML schema for `sitemap.xml`. Note: a `Sitemap:` line in `robots.txt` is not User-agent-scoped.
    https://sitemaps.org/protocol.html

2. “The /llms.txt file, v2.” llms.txt. The deck dates version 2 to August 2026.
    https://llmstxt.org/

3. “llms.txt.” Lighthouse, Chrome for Developers. The agentic-browsing audit of `llms.txt`, including `rel="alternate"` Markdown and `rel="describedby"`.
    https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt

4. Deda, Yulia / SE Ranking. “LLMs.txt: Why Brands Rely On It and Why It Doesn’t Work.” SE Ranking Blog. Speaker notes attribute ~10% llms.txt penetration to this analysis of nearly 300,000 domains (reported share 10.13%). The study also reports no clear link between the file and AI citation frequency.
    https://seranking.com/blog/llms-txt/

5. “Agent Skills Overview.” Agent Skills. Cited for exposing API usage as an agent skill (`SKILL.md`).
    https://agentskills.io/

6. “FAIR Signposting.” signposting.org. Live readable slide: mature, low-cost, platform-adopted (Dataverse, DSpace, InvenioRDM/Zenodo, and others). Typed Link headers / link elements for cite-as, describedby, item, license, author, etc.
    https://signposting.org/FAIR/

7. “Agentic Resource Discovery Specification.” agenticresourcediscovery.org. Bleeding-edge `/.well-known/ard.json` discovery envelope (S18).
    https://agenticresourcediscovery.org/spec/

8. “Agent Plugins.” agent-plugins.org. Bleeding-edge packaging format for skills and MCP services (S19).
    https://agent-plugins.org/

## Being callable

1. *API NIAID Webinar Slides*, 31 March 2026. PDF in the go-fair-us/apireference repository. The earlier, longer API talk.
    https://github.com/go-fair-us/apireference/blob/master/docs/Presentation/API_NIAIDWebinarSlides033126.pdf

2. Mayer, Lisa, et al. “A Blueprint for Including Digital Objects in the NIAID Data Ecosystem.” Zenodo. Cited on the callable / Blueprint slide (S20). DOI as printed on the live deck:
    https://doi.org/10.5281/zenodo.17161561

3. Model Context Protocol registry. Where servers are listed. The deck also says the Linux Foundation’s Agentic AI Foundation governs MCP. That organization is not given its own URL.
    https://registry.modelcontextprotocol.io/

4. “MCP updates.” go-fair-us/apireference, `docs/mcp/updates.md`. Speaker note for the March 2025–October 2026 protocol table. The note says this will be linked from the page.
    https://github.com/go-fair-us/apireference/blob/master/docs/mcp/updates.md

5. “WebMCP.” W3C Web Machine Learning Community Group. Named on the ragged-edge portion of the deck. The glossary defines it with the callable terms.
    https://webmachinelearning.github.io/webmcp/

Additional standards and services named in the notes:

- [JSON-LD](https://www.w3.org/TR/json-ld11/) and NIAID’s minimum metadata recommendations in the [Blueprint for Digital Objects](https://www.niaid.nih.gov/research/data-blueprint) (see also the Zenodo DOI above).
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html) (formerly called the Swagger Specification).
- [Cool URIs for the Semantic Web](https://www.w3.org/TR/cooluris/).
- HTTP status classes ([RFC 9110, section 15](https://www.rfc-editor.org/rfc/rfc9110.html#section-15)), [`Cache-Control`](https://www.rfc-editor.org/rfc/rfc9111.html#section-5.2), [`ETag`](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.8.3), and [`Last-Modified`](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.8.2).
- [NIAID Data Ecosystem Discovery Portal](https://data.niaid.nih.gov/).
- Repository examples: [ImmPort](https://www.immport.org/), [IEDB](https://www.iedb.org/), and [TB Portals](https://tbportals.niaid.nih.gov/).
- [MCP specification dated 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28), named as the version that lines up with OAuth / protected-resource authorization for data access.

## Being meaningful

1. “NIAID Data Ecosystem Data Science and Sharing: Blueprint for Digital Objects.” NIAID. The pointer for the Blueprint recommendations.
    https://www.niaid.nih.gov/research/data-blueprint

2. [RRID:SCR_006604](https://scicrunch.org/resolver/RRID:SCR_006604). The identifier in IEDB’s homepage JSON-LD, described as the only identifier found in page JSON-LD across the 11 sites reviewed. An example identifier, not a cited publication.

3. “FAIR Signposting.” Also under **Being readable**, item 6. Rights notes reuse the same Link-header pattern.

Additional terms and resources named in the notes / live profile table:

- A glossary, data dictionary, or field list at a stable URL (a general resource type, not a specific reference).
- IEDB ontologies ONTIE and [MHC Restriction Ontology (MRO; BioPortal ID: MHCRO)](https://bioportal.bioontology.org/ontologies/MHCRO). [Gene Ontology](https://geneontology.org/) references appear in the [BV-BRC API documentation](https://www.bv-brc.org/api/doc/).
- Resolvable identifiers: [DOIs](https://doi.org/), accessions, [RRIDs](https://www.rrids.org/current-project), [RAiD](https://www.raid.org/) (projects), and [CURIEs](https://www.w3.org/TR/2010/NOTE-curie-20101216/). The only specific RRID is **Being meaningful**, item 2.
- [DataCite Metadata Schema 4.6](https://schema.datacite.org/meta/kernel-4.6/) for DOI-backed citation metadata (generalist repos / NIH GREI).
- [schema.org `Dataset`](https://schema.org/Dataset), [Science-on-Schema.org](https://github.com/ESIPFed/science-on-schema.org) (others of potential interest on the live slide), [Bioschemas Dataset](https://bioschemas.org/profiles/Dataset/), and the [NIAID Data Ecosystem schemas](https://github.com/NIAID-Data-Ecosystem/nde-schemas) (IID fields: infectious agent, health condition, species, funding).
- [CODATA Cross Domain Interoperability Framework (CDIF)](https://cdif.org/) and the [CDIF book](https://cross-domain-interoperability-framework.github.io/cdifbook/).
- [Croissant 1.1](https://docs.mlcommons.org/croissant/docs/croissant-spec-1.1.html) and its [RAI specification](https://docs.mlcommons.org/croissant/docs/croissant-rai-spec.html), including the usage policies named in the access-control notes.
- [RO-Crate 1.2](https://www.researchobject.org/ro-crate/specification/1.2/introduction.html). [Galaxy](https://galaxyproject.org/) and [WorkflowHub](https://workflowhub.eu/) are named as users of it. The lineage notes also name RO-Crate.
- [SHACL](https://www.w3.org/TR/shacl/) (W3C Recommendation; prefer this Rec URL). ImmPort’s [Data Package Validator](https://docs.immport.org/datasubmission/datapackagevalidator) is a separate validation example.
- [SPARQL 1.2 RL](https://www.w3.org/TR/sparql-rl/) (W3C Working Draft, **31 October 2026**). Primary “rules” citation for the deeper-context slide. Live slide text still says “Oct 21 2026” / `sparql12-rl`; handouts use the verified date and TR URL. [SHACL-AF](https://www.w3.org/TR/shacl-af/) remains available as a supplemental WG Note, not the slide’s primary rules example.
- [SSSOM](https://mapping-commons.github.io/sssom/) (dev notes: https://mapping-commons.github.io/sssom/dev/). Common exchange is TSV; author and confidence are optional. Notes say no public mapping set was found on the 11 sites reviewed; ImmPort-to-CDISC is a suggested first set.
- Competency questions, as the test suite for the items above (a general testing method, not a specific resource).

## Rights, credit, and lineage

Additional rights, citation, and provenance resources named in the notes:

- W3C [Text and Data Mining Reservation Protocol (TDMRep)](https://www.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240510) (Community Group report; also tracked at https://github.com/w3c-cg/tdm-reservation-protocol). Common in EU / STM reservation practice; US practice differs.
- [Really Simple Licensing (RSL)](https://rslstandard.org/rsl) — see **Being reachable**. Early / emerging; absolute `License:` URL in robots.txt.
- [Data Privacy Vocabulary (DPV) 2.0](https://w3c-cg.github.io/dpv/2.0/), linked from the rights slide.
- [ODRL](https://www.w3.org/TR/odrl-model/) (Open Digital Rights Language), paired with [DUO](https://github.com/EBISPOT/DUO) (Data Use Ontology) codes.
- schema.org [`conditionsOfAccess`](https://schema.org/conditionsOfAccess), for open metadata on gated data.
- [SPDX license identifiers](https://spdx.org/licenses/).
- [CRediT (NISO Contributor Role Taxonomy)](https://credit.niso.org/), used with schema.org `Role` on the attribution slide.
- Croissant’s [`cr:citeAs`](https://docs.mlcommons.org/croissant/docs/croissant-spec-1.1.html) property, a citation to the dataset or a publication about it that ideally uses BibTeX.
- [DOI](https://doi.org/), [ORCID](https://orcid.org/), [ROR](https://ror.org/), [RRID](https://www.rrids.org/current-project), and [RAiD](https://www.raid.org/), named as identifier types.
- W3C [PROV-O](https://www.w3.org/TR/prov-o/).
- DataCite version / related-identifier relations (`IsVersionOf`, `IsNewVersionOf`, `IsDerivedFrom`, and similar) on the lineage slide.

The same notes also name Content Signals and AIPREF (**Being reachable**), FAIR Signposting (**Being readable** / **Being meaningful**), RO-Crate and SHACL / SPARQL RL (under **Being meaningful**), and read-only MCP or OpenAPI envelopes (under **Being callable**).

## Checking the result

1. Evaluation prompts in ai-blueprint-core, `prompts/evals`. Prompts a repository can use to test an agent.
    https://github.com/go-fair-us/ai-blueprint-core/tree/master/prompts/evals

2. “AI-Assisted Search.” NIAID Data Ecosystem Knowledge Center. Compare portal results with AI-assisted search on and off (S35).
    https://data.niaid.nih.gov/knowledge-center/ai-assisted-search

3. CopilotKit, OpenIntelligentUI. Cited for generative and dynamic user interfaces. The deck prints the repository and its default branch. Both addresses are the same project.
    https://github.com/CopilotKit/OpenIntelligentUI
    https://github.com/CopilotKit/OpenIntelligentUI/tree/main

4. Pranavsai, Madala. `genui-package`. Cited as “Opencode genui.”
    https://github.com/madalapranavsai/genui-package

5. Herdr UI. Backup “More From the Edge” slide (S39).
    https://herdr.dev/

Closing NIH policy pointers from speaker notes (S36):

- NIH Office of Science Policy, Artificial Intelligence policies overview:
  https://osp.od.nih.gov/policies/artificial-intelligence/
- NOT-OD-25-118 — Request for Information (RFI); not itself a binding data-use policy:
  https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-118.html
- NOT-OD-25-081 — DUC-related notice:
  https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-081.html

The Lighthouse agent audit in this part of the deck is the `llms.txt` audit; see **Being readable**, item 3. An `ard.json` analyser is also named; see the ARD specification under **Being readable**, item 7.

## Acknowledgements

1. NIAID home page. Printed as an image source.
    https://www.niaid.nih.gov/

Three photographs are credited to the NIH Image Gallery, with no URL. The captions are “Alzheimer's,” “Peekaboo human parotid glands,” and “Cancer nanomedicine.”
