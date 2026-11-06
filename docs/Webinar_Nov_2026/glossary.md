# Glossary

Terms from the NIAID Blueprint webinar deck **Making Your Repository More Accessible to SI** (*Phase III NIAID Slides 11/6*, 6 November 2026). The live Google Slides deck and the PDF handout use **SI** in the talk title and pillar language; earlier handout drafts said **AI**. These definitions follow the live deck. **SI** is left as the slides write it (not expanded here).

Definitions follow the way the slides and speaker notes use each word. They are short working definitions for this talk. Where a term is a published standard, the line says what the deck is pointing at, not the full specification.

The talk’s scope is what a repository can hand to an SI workflow: data, services, context, and skills and tools. Building agents, building a harness, choosing a model, and running the compute are outside that scope.

## Systems and roles

**Artificial intelligence (AI).** Software that uses a trained model to interpret, search, summarize, or act on repository content. In this deck that includes training crawlers, cataloging crawlers, and agents that visit because a person asked. The live title and many slides prefer **SI** for the same space of workflows.

**SI.** The live deck’s preferred label in the talk title and “Be …” pillars (Reachable, Readable, Callable, Meaningful). Used the way the slides use it for agent- and model-mediated workflows over repository content. Not expanded in these handouts.

**Model.** The trained system that produces the output. The deck treats the model as one of three parts of an SI flow, alongside the compute environment and the application.

**Weights.** The learned parameters inside a model. “Stale weights” means an older training run that still answers questions about a repository after the live site has changed, moved, or closed.

**Compute environment.** The machines and services where a model runs. Out of scope for this talk.

**Application.** The workflow a person uses. The repository’s contribution is what that application can read and call.

**SI workflow.** A task that uses a model together with repository content: find a study, read a record, call an API, draft a citation. The deck’s subject is how to make that workflow possible from the repository side. (Earlier handout text had a malformed “AI[SI]workflow” label for the same idea.)

**Harness.** The software wrapped around a model that runs the loop: which tools it may call, what it is allowed to remember, and when it must stop. The talk does not ask repositories to build or operate one. It asks them to supply the files, APIs, and context a harness can use.

**Agent.** Software that takes a goal and carries out steps for someone: open a page, follow a link, call an API, read a file. The notes warn that these systems are easy to treat as if they had intentions. They are a mix of fixed instructions and model output, acting for a user community or for whoever directed them.

**Agency.** The capacity to decide and to bear responsibility. The deck says agents do not have agency. They act on behalf of a person or organization, and the open question is how to frame that responsibility.

**Human in the loop.** A person stays in the path before an agent’s action counts. The closing slides place this with liability questions that other sectors, including banks, are still working out.

**Virtual browser.** An agent driving a normal web page the way a person would: clicking, scrolling, and waiting for the screen to update. The deck says this pattern is spreading quickly, and that it is a poor substitute for pages and APIs that can be read directly.

## Who visits

**Crawler.** An automated client that walks a site on its own schedule. The deck splits crawlers by purpose, because a single block often stops the useful visits along with the unwanted ones.

**Trainer crawler.** A crawler collecting text for model training. The slide names GPTBot, ClaudeBot, CCBot, and Google-Extended as examples. Google-Extended is a product token that covers Gemini training and grounding; blocking it does not by itself remove the site from Google Search. The cited study says these crawlers often judge a host from a few sample pages, so the landing page and the record page decide how much of the site gets fetched.

**Index builder.** A crawler looking for citable resources to put in a catalog or a search index. The deck treats this as a visit that can add discovery value. Examples on the slide include OAI-SearchBot, PerplexityBot, and Googlebot for AI Overviews.

**Fetcher.** A client that retrieves a specific page because a user, or that user’s agent, asked for it. The notes say to separate fetchers from training crawlers before writing a block rule. A content-delivery network or firewall may be blocking both. User-triggered agents (for example ChatGPT-User, Perplexity-User) often do not honor `robots.txt` because the fetch is human-directed.

**Organic fetch.** A visit that starts from a person’s query. The person may browse the site, or an agent may visit for them.

**Bot.** Any non-human client. The reachable-site slides use it as the broad class that site rules, CDNs, and `robots.txt` already try to classify.

## Being reachable

**robots.txt.** A file at the root of the site that states rules for automated clients: what they may fetch, and, with newer policies, how the content may be used. Path patterns in Allow/Disallow begin with `/` (for example `Disallow: /*.gif$`, not a bare `*.gif$`).

**User agent.** The name a client sends with a request. The evaluation slide says to break server logs down by this name so trainer crawlers, indexers, and user-driven fetchers can be told apart.

**CDN**  A content delivery network (CDN) is a network of servers that delivers web content from locations closer to users, improving speed and reducing load on the original server.

**Content Signals.** Cloudflare’s policy labels for whether content may be used in search, as input to an AI answer, or for training. The notes treat this as a vendor policy and pair it with the IETF vocabulary below. It is not the same thing as Cloudflare’s default AI-bot blocking controls.

**AI Preferences (AIPREF).** The IETF “AI Preferences” work. The vocabulary draft verified for these handouts is `draft-ietf-aipref-vocab-08` (14 September 2026). It gives short labels for uses such as `train-ai`. The attachment draft (`draft-ietf-aipref-attach-05`, 19 August 2026) adds a `Content-Usage` rule to `robots.txt` and a `Content-Usage` HTTP header, for example `Content-Usage: train-ai=n`. Label `Content-Usage` as an IETF Internet-Draft mechanism, not a finished RFC. Live speaker notes still cite vocab **-07**; these handouts use **-08**.

**Really Simple Licensing (RSL).** An XML licensing vocabulary discoverable from `robots.txt` (among other places). When a `License:` line appears in `robots.txt`, the value must be an **absolute URL** to a separate RSL XML document (for example `License: https://example.org/rsl.xml`), not a site-relative path alone. Early / emerging relative to TDMRep in many STM settings; watch the US–EU framing on the rights slides.

**Rate limiting.** A server limit on how fast a client may call. The deck asks repositories to answer excess traffic with HTTP 429 and a `Retry-After` header that says when to try again, even though some agents will ignore it.

**Load balancing and caching.** Ordinary web operations the deck lists under “be reachable”: spread traffic, and reuse responses so agent traffic does not have to rebuild the same page on every visit.

## Being readable

**Sitemap (`sitemap.xml`).** An XML list of the site’s URLs, defined at sitemaps.org. A `Sitemap:` line in `robots.txt` advertises that list. Sitemap lines are **not** scoped to a particular `User-agent` group the way Allow/Disallow rules are; they apply file-wide. The deck says sitemaps are still in use, and that many crawlers walk the site anyway because sitemaps often go stale.

**llms.txt.** A curated text file, usually at the site root, that lists the pages and documents an SI workflow should read. Version 2, dated August 2026 in the deck, also lets each page point at a Markdown alternate (`rel="alternate"`, type `text/markdown`) and at the `llms.txt` that covers it (`rel="describedby"`). A file in a subfolder can cover the pages under that folder. Chrome Lighthouse checks this arrangement. Speaker notes attribute roughly 10% domain penetration to SE Ranking’s analysis of nearly 300,000 domains (about 10.13% in that study).

**Markdown alternate.** A Markdown rendering of an HTML page, advertised from the page or from an HTTP `Link` header. The deck also notes that some hosts already return Markdown when the request asks for `Accept: text/markdown`.

**JavaScript rendering.** Pages that fill in their text only after a browser runs JavaScript. Many agent fetches never run that script, so the text is missing. The deck says an agent can be given a browser tool, and that this is slower and cannot be assumed.

**Agent skill (`SKILL.md`).** A folder of instructions an agent can load for a specific job. The deck points at agentskills.io and suggests writing API usage up as a skill, on top of documentation that is already good for people.

**Agentic Resource Discovery (ARD) / `ard.json`.** A bleeding-edge discovery envelope for agentic resources (MCP servers, skills, plugins, and related artifacts). The well-known file is hosted at `https://yourdomain/.well-known/ard.json`. On the ragged-edge readable slide.

**Agent Plugins.** A bleeding-edge, vendor-neutral packaging format for reusable skills and MCP services (`plugin.json`, `skills/`, `mcp.json`). Distinct from, and easy to confuse with, a single `SKILL.md` or the MCP Skills extension.

**Bulk download.** A package, or a direct list of files, so an agent can take a resource in one transfer instead of clicking through the interface. The deck says a sitemap can point at these, and so can a Markdown list.

**AI-ready documentation.** Docs written so an agent can follow them: stable pages, explicit endpoints, examples, and a skill file that points at the same material. The slide calls this the highway from the repository to the agent.

**FAIR Signposting.** Typed HTTP `Link` headers (and/or HTML `<link>` / linksets) that point from a landing page to cite-as, describedby, item, license, author, and related targets, so a client can navigate to PIDs, metadata, content, and licenses without brittle scraping. The live readable slide calls this **mature and low-cost**, and notes platform adoption (Dataverse since ~5.14, DSpace, InvenioRDM/Zenodo, and others). Earlier handout wording that called Signposting merely bespoke / ragged-edge is outdated relative to that slide.

## Being callable

**API.** A programmatic interface for metadata and data. For this talk the minimum is the NIAID Blueprint pattern: JSON-LD for the minimal metadata, resource-shaped URLs, HTTP GET, an OpenAPI description, and the same resource available as HTML for a person. The March 2026 API webinar is the longer treatment. The callable slide also points at the Blueprint DOI.

**OpenAPI.** A machine-readable description of an HTTP API. Coding agents and generated clients use it to discover operations and parameters.

**JSON-LD.** JSON annotated as linked data, so a response can name a dataset, its license, its identifier, and its distributions in a form search engines and agents already expect. The deck wants it both from the API and as one block in the server-rendered HTML of each dataset page.

**Cool URI.** A stable, readable, dereferenceable address. The API slides say to keep dates, software names, and long query strings out of the path.

**Content negotiation.** Serving HTML, JSON-LD, JSON, CSV, or XML for the same resource, chosen from the request. The deck pairs this with ordinary status codes: 2xx success, 3xx redirect (including 303), 4xx client error, 5xx server error.

**CLI.** A command-line client for the same API. The deck lists it as a lighter option when a full MCP server is more than the repository wants to run.

**Model Context Protocol (MCP).** A shared convention for how an agent talks to a server: tools it can call, resources it can read, and prompts it can use. The deck says agents struggle with undocumented or inconsistent APIs, and that MCP is that convention. The Linux Foundation’s Agentic AI Foundation governs it. A call still passes through the repository’s own API, login, and rate limits. MCP is helpful but not required for “SI-ready”; Reachable + Readable + a well documented API already go a long way.

**MCP registry.** The public list of MCP servers at `registry.modelcontextprotocol.io`.

**Local MCP server.** A server running on the user’s machine. It still calls the repository API under that user’s login and limits.

**Remote MCP server.** A server the repository hosts. The repository chooses which tools and descriptions are offered, and it can log use at the MCP layer as well as at the API.

**Tool.** In MCP, a named operation with a description and, in current versions, a structured result. The June 2025 and November 2025 notes in the deck are about making those descriptions and permission steps predictable.

**Resource.** In MCP, something the server lets the agent read: a record, a file, a document.

**Prompt.** In MCP, a prepared prompt the server offers so the agent starts from the repository’s wording.

**Stateless MCP.** The July 2026 change described on the slide: the server does not have to remember earlier turns. Background work moves into optional extensions.

**Skills extension.** The MCP extension the slide says was finalized and shipped in standard kits in September–October 2026, for packaging richer plugins. Distinct from, and easy to confuse with, an `SKILL.md` agent skill or an Agent Plugin package.

**OAuth.** For protected HTTP MCP, the 2026-07-28 MCP authorization model treats the MCP server as an OAuth 2.1 resource server (Protected Resource Metadata, authorization-code + PKCE, audience-bound tokens, illustrative scopes such as `mcp:resources:read`). Prefer scoped, short-lived tokens over long-lived API keys. Open metadata can still be published, with the access condition written on the record.

**WebMCP.** A browser-side companion to this idea: the page itself exposes tools to an agent. Listed on the ragged-edge slide, with the W3C Web Machine Learning draft.

## Being meaningful

**Semantic layer.** The machine-readable meaning around the bytes: identifiers, vocabularies, profiles, shapes, and mappings. The scope slide lists this next to repository configuration, link files, and APIs.

**Context.** The material that tells a model what a field, a record, and a dataset are. The deck’s claim is that published context prevents the model from inventing that structure at answer time.

**Schema hallucination.** A model inventing fields, types, or relations that the repository does not use. The meaningful-section title slide says structured knowledge is the reliable way to reduce this.

**Persistent identifier (PID).** One stable name for one thing, which an agent can cite and follow. The deck’s set is a DOI or an accession for data, ORCID for a person, ROR for an organization, RRID for a resource such as a database or a reagent, and **RAiD** for a project.

**DOI.** A persistent identifier for a digital object, used here for data or for a citation target.

**ORCID.** A persistent identifier for a researcher.

**ROR.** A persistent identifier for a research organization.

**RRID.** A persistent identifier for a research resource. The example on the slide is IEDB’s `SCR_006604`, carried in that site’s homepage JSON-LD.

**RAiD.** Research Activity Identifier — a persistent identifier for a research project or activity, listed with the other PIDs on the meaningful slide.

**Accession.** A repository-issued identifier for a study, sample, or record, used in the same role as a DOI when a DOI is not the local practice.

**Vocabulary.** The controlled words a repository uses. The deck’s ladder runs from a term list, to a taxonomy with broader and narrower terms, to an ontology with definitions and relations. Publishing even an informal data dictionary is the step the notes say most sites skip.

**Data dictionary.** A list of fields with definitions, stable at a URL. First item on the notes’ easiest-first list of context a repository can expose.

**Ontology.** A vocabulary with definitions and relations. The examples are IEDB’s ONTIE and MRO, and Gene Ontology references in BV-BRC’s API docs.

**Profile.** An agreed subset of a shared vocabulary, so every repository describes a dataset with the same fields. The live profile table highlights DataCite Metadata Schema 4.6, Bioschemas Dataset, CODATA CDIF, the NIAID Data Ecosystem schema, Croissant 1.1 (+ RAI and Geo), and RO-Crate 1.2, with Science-on-Schema.org called out among others of potential interest. Declare which profile a record follows with `conformsTo`.

**DataCite Metadata Schema 4.6.** Custom schema (with mappings) for DOI-backed citation: creators, funders, related identifiers, rights. Aimed at generalist repositories (Zenodo, Figshare, Dryad, Dataverse) following NIH GREI recommendations. Unlike most of the other profiles on the slide, it is not built primarily on schema.org Dataset.

**CODATA CDIF.** Cross Domain Interoperability Framework — a set of profiles for core cross-domain FAIR metadata functions.

**schema.org Dataset.** The base type for a dataset: name, description, license, creator, identifier, distribution. Still the practical HTML path when a repository publishes one Dataset block in server-rendered HTML.

**Science-on-Schema.org.** Conventions for using schema.org the same way across science repositories, including identifiers, variables, funding, provenance, and SHACL checks. On the live slide it appears under “others of potential interest.”

**Bioschemas.** A life-science profile over schema.org, with minimum, recommended, and optional fields and ontology-backed keywords.

**NIAID Data Ecosystem schema.** The extra fields the Discovery Portal harvests: infectious agent, health condition, species, and funding. The slide calls these IID fields and notes they are based on Bioschemas.

**Croissant.** A schema.org-based description of dataset files, typed fields, machine-learning splits, provenance, and usage policy. Version 1.1 adds responsible-AI fields (and the deck also mentions Geo). The deck wants a Croissant file when the data are tabular or meant for machine learning, and notes that the core fields are shared with schema.org Dataset.

**`conformsTo`.** A property that names which profile a record follows, so an agent or a validator knows which rules apply.

**RO-Crate.** A package that binds data, code, and workflow runs to their provenance. The slide points it at reproducibility and at workflow hubs such as Galaxy and WorkflowHub.

**SHACL.** Shapes Constraint Language, a W3C Recommendation (`https://www.w3.org/TR/shacl/`). A shape is a machine-readable rule for a valid record, such as “every sample has a collection date and a host taxon.” The same shapes can validate a submission and tell an agent what to expect. ImmPort’s existing validator is the example to recast as public shapes.

**SPARQL RL (SPARQL-RL).** A W3C Working Draft rules language for deriving new RDF facts from existing data (for example a parent category or a computed value), so curation knowledge is declared rather than buried in code. Verified publication date for these handouts: **31 October 2026** at `https://www.w3.org/TR/sparql-rl/`. The live slide still prints “Oct 21 2026” and a `sparql12-rl` path; prefer the verified date and TR URL. This is the deck’s primary “rules” example on the deeper-context slide.

**SHACL-AF.** SHACL Advanced Features, a W3C Working Group Note. Supplemental advanced features for SHACL; not the primary rules example on the live S33 slide (that role is SPARQL RL).

**SSSOM.** Simple Standard for Sharing Ontological Mappings. Common exchange is a **TSV** table whose rows say “our term X matches term Y,” with the relation (exact, close, broader, related) and justification. Author and confidence fields are **optional**, not mandatory. The notes say no public mapping set was found on the 11 sites reviewed, and they suggest an ImmPort-to-CDISC set as a first one.

**Competency question.** A question the repository publishes as a test of its own context. If the identifiers, profiles, shapes, and mappings are sufficient, an agent should be able to answer it. The notes call these the test suite for the meaningful layer. The evaluation slide says to run the repository’s own questions against an agent.

## Rights, credit, and lineage

**Rights and access.** Who may view or use the data, and on what conditions, for people and for automated clients. The notes name `robots.txt` / Content Signals / AIPREF, the W3C TDM Reservation Protocol, RSL, DPV, SPDX in schema.org `license`, and ODRL combined with DUO codes. US and EU practice diverge; TDMRep is common in European / STM reservation settings, while RSL is earlier-stage.

**Data Privacy Vocabulary (DPV).** A vocabulary for describing privacy and data-handling concepts in machine-readable form. Linked from the rights slide (`https://w3c-cg.github.io/dpv/2.0/`).

**TDMRep.** The W3C Text and Data Mining Reservation Protocol, a way to state a reservation or a permission for mining.

**ODRL.** The W3C Open Digital Rights Language, for permissions, prohibitions, and duties.

**DUO.** The Data Use Ontology. Short codes for secondary-use conditions, often on human data. The notes pair DUO with ODRL.

**`conditionsOfAccess`.** The schema.org property for how a dataset may be obtained. The notes say controlled-access human data should still publish open metadata, with this condition written on the record, and put the bytes behind OAuth.

**Attribution and authority.** Who gets credit, and how a reader checks the source and cites it. The notes name FAIR Signposting, SPDX license identifiers, a cite-as link to BibTeX, CRediT roles, and DOI, ORCID, ROR, RRID, and RAiD.

**CRediT.** NISO Contributor Role Taxonomy — controlled contributor roles (for example Conceptualization) that can be expressed with schema.org `Role` and ORCID. On the attribution slide.

**SPDX.** A standard identifier for a license, so a machine can tell which license applies.

**cite-as.** A link or property (the notes write `cr:citeAs`) that points at the citation text or the BibTeX for a resource.

**Lineage.** The history of a dataset: where it came from and how it changed. The deck treats this as part of protecting the repository’s intellectual property, alongside provenance and read-only API or MCP envelopes. DataCite version / related-identifier relations (`IsVersionOf`, `IsNewVersionOf`, `IsDerivedFrom`, and similar) appear on the lineage slide.

**PROV-O.** The W3C Provenance Ontology. Classes and relations for an entity, the activity that produced it, and the agent that carried the activity out.

**Intellectual property (IP).** In the closing slide, the value the repository adds, and the open question of how to expose that value to agents without giving it away unmarked. Tied on the concerns slide to provenance, packaging, and integrity.

## Checking the result

**Evaluation.** The deck’s word for “how do you know it worked.” Starting points on the slide include trying an agent against your docs, the prompts in `prompts/evals`, NDE AI-assisted search with the feature on and off, Chrome Lighthouse’s agent audits (including `llms.txt`), and an `ard.json` analyser.

**NDE AI-assisted search.** The NIAID Data Ecosystem Discovery Portal’s AI-assisted search mode, cited as a practical comparison when evaluating repository discoverability (`https://data.niaid.nih.gov/knowledge-center/ai-assisted-search`).

**Lighthouse agent audit.** The agentic-browsing audits in Chrome Lighthouse, including the `llms.txt` audit cited earlier in the deck.

**Evaluation prompt.** A fixed prompt, kept in version control, used to test an agent against the repository. The slide points at `prompts/evals` in the ai-blueprint-core repository.

