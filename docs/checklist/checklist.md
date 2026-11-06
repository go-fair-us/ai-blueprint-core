# Repository checklist: making your repository more accessible to SI

Companion to the 6 November 2026 NIAID Blueprint webinar
[*Making Your Repository More Accessible to SI*](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf)
and its [supplementary materials](../Webinar_Nov_2026/README.md).

This file is the **only content authority** for the checklist. Generated HTML and PDF views are renderings of this document. Edit here, then rebuild.

This companion is a practical list of actions. It is **not** a certification, audit rubric, maturity model, or compliance score. Finishing more items, or items at a higher level number, does not make a repository more trustworthy, more FAIR, or more “SI-ready.” Levels describe the kind of access and maintenance an action typically needs, not quality.

The webinar focuses on assets a repository exposes to agents and workflows—configuration, files and metadata, APIs and MCP services, and semantic-layer components. It does not assess whether particular datasets are suitable for model training or inference.

Informational only; not legal advice.

## How the levels work

Levels record **capability and access**, not a ranking of repositories.

| Level | What it usually takes | Typical access | Typical maintenance |
| --- | --- | --- | --- |
| **1 — Publish or update served files** | Add or edit files the site already knows how to serve (`robots.txt`, `sitemap.xml`, a data dictionary, a mapping table). | Permission to write at a well-known path, or an administrator who can place the file. A CDN or hosted platform can override what you upload. | Keep the file current when paths, policy, or inventory change. |
| **2 — Configure the publishing platform** | Change HTTP headers, HTML templates, landing-page markup, content negotiation, CDN or firewall rules, or repository-platform settings. | Platform, web, or network administrator access; sometimes a developer. | Recheck after platform, theme, or CDN changes. |
| **3 — Write or run software** | Implement or operate an API or MCP server, or run specialized tooling such as a validator. | Developer time and, if you host a service, operational support. | Code, dependencies, and (only if you host it) the running service. |

A Level 1 file can still require administrator access to publish. A Level 3 check such as SHACL validation can run **locally** or in a batch pipeline; it does not require a public validation service unless you choose to offer one.

Optional and emerging items are labeled. Skipping them is not a failure.

## Three different kinds of statement

Do not collapse these into one “AI policy” switch.

1. **Crawl preferences** — `robots.txt` (RFC 9309) tells cooperating clients what they may fetch. Compliance is voluntary. A preference is not a license.
2. **Access enforcement** — HTTP 401/403, CDN or WAF rules, rate limits (`429` + `Retry-After`), and authentication actually allow or deny a request.
3. **Rights and usage signals** — licenses, TDM reservation declarations, and draft usage vocabularies state permissions or preferences about *use*. They do not, by themselves, block a fetch.

US and EU practice around text-and-data-mining reservations is not the same. Read [TDM reservations](../Webinar_Nov_2026/supplementalInformation/tdm.md) before treating any signal as a legal conclusion.

## How to use this checklist

- Work through the four webinar facets: **Reachable**, **Readable**, **Callable**, and **Meaningful**. Evaluation sits beside them; it is not a fifth grade.
- Each item names the action, who can typically do it, how to verify it, and where the webinar or a handout discusses it.
- Print the PDF and mark the empty boxes, or copy this Markdown file and track status in your own notes. The generated PDF is printable; it is not an interactive fill-in form.
- Generate a Level 1 view or a Levels 1–2 view from this same file if you want a shorter handout (see [README](README.md)).
- MCP is **not** required in order to act on the webinar. Reachable and Readable work plus a well documented API already go a long way.

## Reachable

Network-accessible on terms you have thought through: signal what you expect, enforce the constraints that matter, and look at logs. See webinar PDF pp. 10–13 and the glossary section [Being reachable](../Webinar_Nov_2026/glossary.md).

### RCH-01. Review how your host treats automated traffic

- **Level:** 2
- **Pillar:** Reachable
- **Optional:** no
- **Kind:** access-enforcement
- **Maturity:** established
- **Access needed:** Network, CDN, or platform administrator who can see bot-management, WAF, and reverse-proxy rules.
- **Maintenance:** Recheck after provider or rule changes; vendor bot IP lists change.
- **Sources:** [Webinar PDF p. 10](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=10); [Glossary — CDN, rate limiting](../Webinar_Nov_2026/glossary.md); [Identifying agents](../Webinar_Nov_2026/supplementalInformation/agentIdentification.md)

**Do this.**

Ask whether your CDN, reverse proxy, or hosting provider already detects and filters automated clients. Decide, with that administrator, which classes of visitor you intend to allow (for example index builders and user-triggered fetchers) and which you intend to throttle or block. Ordinary load balancing and caching remain useful under agent traffic. Match vendor documentation for product tokens and, where they publish them, IP ranges (for example [OpenAI GPTBot addresses](https://openai.com/gptbot.json)); do not hard-code addresses in `robots.txt`.

**How to verify.**

From outside the internal network, request a public page as an ordinary client and compare the status code with what your written policy predicts. Confirm in the provider console (or exported rules) that AI-bot or WAF settings match that policy. User-Agent strings can be spoofed; published IP ranges and cryptographic bot authentication are stronger than a name tag alone (see the agent-identification handout).

**Watch for.**

A firewall or CDN rule can block a fetcher that `robots.txt` allows. Identification usually tells you the operator or product, not which model a person selected.

### RCH-02. Publish a robots.txt at the site root

- **Level:** 1
- **Pillar:** Reachable
- **Optional:** no
- **Kind:** preference-signal
- **Maturity:** established
- **Access needed:** Permission to place a file at the origin site root, or an administrator who can. A CDN-managed `robots.txt` can replace the file you uploaded.
- **Maintenance:** Review when paths, collections, or vendor product tokens change.
- **Sources:** [Webinar PDF p. 11](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=11); [Glossary — robots.txt](../Webinar_Nov_2026/glossary.md); [Example robots.txt](../Webinar_Nov_2026/assets/robots.txt); [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html)

**Do this.**

Publish `https://YOUR-HOST/robots.txt`. Use `User-agent` groups with `Allow` and `Disallow` path prefixes that begin with `/` (for example `Disallow: /*.gif$`, not a bare `*.gif$`). Remember that this file states preferences for cooperating clients; it cannot make a client comply, and it does not grant or deny copyright permission.

An annotated example lives with the webinar assets. Treat it as a demonstration (replace hosts and placeholder paths) rather than a drop-in policy.

**How to verify.**

`GET https://YOUR-HOST/robots.txt` and confirm the bytes you expect are served (not a generic platform default). Check that every `Allow`/`Disallow` path starts with `/`.

**Watch for.**

RFC 9309 does not define `Crawl-delay`. Prefer HTTP `429` and `Retry-After` for rate control (see RCH-04). Some clients ignore the file entirely.

### RCH-03. Separate trainer, index, and user-triggered visitors

- **Level:** 1
- **Pillar:** Reachable
- **Optional:** no
- **Kind:** preference-signal
- **Maturity:** established
- **Access needed:** Same as publishing `robots.txt`, plus someone who can reconcile that file with CDN rules.
- **Maintenance:** Recheck vendor bot names and documented behavior; they change.
- **Sources:** [Webinar PDF p. 12](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=12); [Glossary — trainer crawler, index builder, fetcher](../Webinar_Nov_2026/glossary.md); [Identifying agents](../Webinar_Nov_2026/supplementalInformation/agentIdentification.md); [Google-Extended](https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers#google-extended)

**Do this.**

Do not rely on a single `User-agent: *` rule if you want different outcomes for different missions. The webinar groups visitors roughly as:

1. **Trainer crawlers** (examples named on the slide include GPTBot, ClaudeBot, CCBot, and Google-Extended) collecting content for model training or related use.
2. **Search or index crawlers** (examples include OAI-SearchBot, PerplexityBot, and Googlebot for AI Overviews) that can affect discovery and citation.
3. **User-triggered fetchers** (examples include ChatGPT-User and Perplexity-User) retrieving a page because a person asked. Several vendors document that these often do **not** honor `robots.txt`.
4. **Unknown** clients, where a robots line is only a guess and enforcement may belong at the firewall.

Write named groups for the products you actually care about, and keep CDN rules consistent with that intent.

If you mention **Google-Extended**, treat it as a *product token* with no separate HTTP User-Agent. It covers Gemini **training and grounding**. It does **not** affect inclusion or ranking in Google Search. Do not say that blocking it leaves all “AI search visibility” unchanged.

**How to verify.**

Read `robots.txt` and confirm that trainer tokens and search tokens are not forced into one outcome unless that is a deliberate choice. Compare each named token with the vendor’s current crawler documentation. For Google-Extended, use Google’s crawler documentation rather than assuming it behaves like Googlebot.

**Watch for.**

The PDF face still contains the broader sentence “Blocking does not affect AI search visibility.” Prefer the glossary and Google’s documentation, as above.

### RCH-04. Answer overload with HTTP 429 and Retry-After

- **Level:** 2
- **Pillar:** Reachable
- **Optional:** no
- **Kind:** access-enforcement
- **Maturity:** established
- **Access needed:** Someone who can configure the origin, reverse proxy, or CDN rate-limit responses.
- **Maintenance:** Tune thresholds as traffic changes; watch for accidental blocking of ordinary users.
- **Sources:** [Webinar PDF p. 10](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=10); [Glossary — rate limiting](../Webinar_Nov_2026/glossary.md); [Example robots.txt comments](../Webinar_Nov_2026/assets/robots.txt); [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html)

**Do this.**

When a client asks too fast, respond with `429 Too Many Requests` and a `Retry-After` header. That is an HTTP access control, not a `robots.txt` directive. The same pattern is useful for browser-like agent load on JavaScript-heavy pages (see RD-02).

**How to verify.**

Document where the rule is configured. If you can safely exercise it in a staging environment, confirm the response status is 429 and that `Retry-After` is present. Do not run an aggressive test against a production repository you do not operate.

**Watch for.**

Some agents ignore `Retry-After`. RFC 9309 does not define `Crawl-delay`; a few vendors document it, but it is not a substitute for HTTP rate control.

### RCH-05. Log automated traffic and review the patterns

- **Level:** 2
- **Pillar:** Reachable
- **Optional:** no
- **Kind:** advice
- **Maturity:** established
- **Access needed:** Access to request logs or a bot-management dashboard (often a network or platform administrator).
- **Maintenance:** Ongoing review; logs are only useful if someone looks at them.
- **Sources:** [Webinar PDF pp. 12–13](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=12); [Glossary — user agent](../Webinar_Nov_2026/glossary.md); [Identifying agents](../Webinar_Nov_2026/supplementalInformation/agentIdentification.md)

**Do this.**

Keep request logs that include timestamp, path, status, User-Agent, and (where you have it) the provider’s bot classification. Periodically review trainer crawlers, indexers, user-triggered fetchers, and unknowns. Use logs to improve signal and enforcement; they are not a courtroom-grade identification of a model.

**How to verify.**

Produce one recent sample (even a redacted screenshot or query) that breaks traffic down by User-Agent or vendor class, including status codes such as 200, 403, 404, and 429.

**Watch for.**

Behavioral fingerprints suggest automation; they are probabilities, not proof, and they do not identify a model. Do not instruct visiting agents to “report their model” via hidden page text (the agent-identification handout advises against that).

### RCH-06. Optionally declare IETF AI usage preferences

- **Level:** 1
- **Pillar:** Reachable
- **Optional:** yes
- **Kind:** rights-signal
- **Maturity:** draft
- **Access needed:** Same as editing `robots.txt` for a `Content-Usage` line; HTTP header attachment needs platform or CDN configuration (Level 2).
- **Maintenance:** Revisit when the Internet-Drafts are revised or published as RFCs.
- **Sources:** [Webinar PDF p. 11](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=11); [Glossary — AI Preferences (AIPREF)](../Webinar_Nov_2026/glossary.md); [Bibliography — Being reachable](../Webinar_Nov_2026/bibliography.md); [AIPREF vocabulary draft-08](https://datatracker.ietf.org/doc/html/draft-ietf-aipref-vocab-08); [AIPREF attachment draft-05](https://datatracker.ietf.org/doc/html/draft-ietf-aipref-attach-05); [TDM reservations](../Webinar_Nov_2026/supplementalInformation/tdm.md)

**Do this.**

If you want a machine-readable *usage preference* in addition to crawl rules, you may add IETF AI Preferences syntax—for example `Content-Usage: search=y, train-ai=n`—in `robots.txt` and/or as an HTTP `Content-Usage` header. Label this as an **IETF Internet-Draft** mechanism (`draft-ietf-aipref-vocab-08` and `draft-ietf-aipref-attach-05`), not a finished RFC.

Cloudflare Content Signals (`Content-Signal`, with labels such as `search`, `ai-input`, and `ai-train`) are a **different** vocabulary from AIPREF and are also distinct from Cloudflare’s default AI-bot blocking controls. If you use both lines, keep them separate; a parser for one will not read the other.

**How to verify.**

If you adopted the robots-file form, open `/robots.txt` and confirm the `Content-Usage` line matches the drafts you intended. If you adopted the header form, request a sample page and inspect the `Content-Usage` response header. Confirm you did not accidentally treat the line as a fetch block.

**Watch for.**

The webinar PDF shows `Content-Usage` without calling it a draft. The handouts use vocabulary **-08**; the example `assets/robots.txt` comments still mention **-07** in places—follow the glossary and bibliography.

### RCH-07. Optionally point at an RSL license document with an absolute URL

- **Level:** 1
- **Pillar:** Reachable
- **Optional:** yes
- **Kind:** rights-signal
- **Maturity:** emerging
- **Access needed:** Permission to publish an RSL XML document and to edit `robots.txt`.
- **Maintenance:** Keep the XML and the `License:` URL in agreement if licensing changes.
- **Sources:** [Webinar PDF p. 11](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=11); [Glossary — Really Simple Licensing](../Webinar_Nov_2026/glossary.md); [TDM reservations](../Webinar_Nov_2026/supplementalInformation/tdm.md); [RSL specification](https://rslstandard.org/rsl)

**Do this.**

Really Simple Licensing is an emerging XML licensing vocabulary. If you use a `License:` line in `robots.txt`, the value must be an **absolute URL** to that XML document, such as `https://example.org/rsl.xml`, not a host-relative path such as `/rsl.xml`.

**How to verify.**

Confirm the `License:` value starts with `https://` (or another absolute scheme), fetch it, and confirm it returns the RSL document you intended.

**Watch for.**

The PDF face still shows `License: /rsl.xml`. Prefer the glossary, bibliography, and RSL specification. RSL is earlier-stage than several other rights tools discussed in the webinar; skip it unless you have a reason to experiment.

## Readable

Expressive resources: inventories, landing pages, and typed links that an agent can follow without brittle scraping. See webinar PDF pp. 14–20 and [Being readable](../Webinar_Nov_2026/glossary.md).

### RD-01. Publish a sitemap and advertise it with absolute, file-wide Sitemap lines

- **Level:** 1
- **Pillar:** Readable
- **Optional:** no
- **Kind:** standard-practice
- **Maturity:** established
- **Access needed:** Permission to publish XML at a stable URL and to edit `robots.txt`.
- **Maintenance:** Update `lastmod` when pages actually change; stale sitemaps are common, and crawlers may walk the site anyway.
- **Sources:** [Webinar PDF p. 14](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=14); [Glossary — Sitemap](../Webinar_Nov_2026/glossary.md); [Example sitemap.xml](../Webinar_Nov_2026/assets/sitemap.xml); [sitemaps.org protocol](https://sitemaps.org/protocol.html); [Google robots.txt sitemap field](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt#sitemap)

**Do this.**

Publish a sitemap (or several thematic sitemaps, optionally listed from a sitemap index) using the [sitemaps.org](https://sitemaps.org/protocol.html) vocabulary. List each sitemap with an absolute `Sitemap:` URL in `robots.txt`. Those declarations are **not** scoped to `User-agent` groups; they apply file-wide. You can publish separate sitemaps for different parts of the site, but placing a `Sitemap:` line under a particular User-agent block does not make it bot-specific.

Omit URLs that `robots.txt` disallows. If you include `lastmod`, use the date the page changed, not the date the sitemap file was regenerated. A sitemap is an inventory, not crawl permission and not a reading guide (that role is closer to an optional `llms.txt`).

**How to verify.**

Fetch `/robots.txt` and each advertised sitemap URL. Confirm the XML is well formed, each `loc` is on your host, a sample of those URLs respond, and disallowed paths are absent. Confirm `Sitemap:` lines use absolute URLs.

**Watch for.**

The PDF face says you can “express them for specific user agents.” Prefer the glossary, bibliography, and Google’s robots.txt documentation: the sitemap field “isn’t tied to any specific user agent.”

### RD-02. Make the meaningful text available without running JavaScript

- **Level:** 2
- **Pillar:** Readable
- **Optional:** no
- **Kind:** advice
- **Maturity:** established
- **Access needed:** Someone who can change templates or the front-end rendering path so important text is in the server-rendered HTML.
- **Maintenance:** Recheck after theme or single-page-app changes.
- **Sources:** [Webinar PDF p. 17](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=17); [Glossary — JavaScript rendering](../Webinar_Nov_2026/glossary.md)

**Do this.**

Many agent fetches never execute JavaScript. Put titles, descriptions, licenses, identifiers, and other citeable text in clean, semantic, server-rendered HTML (headings, lists, and links that exist in the initial response). In-browser rendering can still be offered to people; do not make it the only copy of the meaning.

If agent traffic on expensive rendered pages becomes a problem, combine this item with HTTP `429` and `Retry-After` (RCH-04).

**How to verify.**

Request a landing page and a record page with a non-browser client (for example `curl`) and confirm that the main descriptive text, license, and identifiers are present without executing script.

### RD-03. Offer Markdown where it helps; keep structured HTML too

- **Level:** 2
- **Pillar:** Readable
- **Optional:** yes
- **Kind:** advice
- **Maturity:** established
- **Access needed:** Developer or platform access to templates, static-site output, or content negotiation.
- **Maintenance:** Keep HTML and Markdown views aligned when pages change.
- **Sources:** [Webinar PDF pp. 15 and 17](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=15); [Glossary — Markdown alternate](../Webinar_Nov_2026/glossary.md)

**Do this.**

Markdown can be convenient for text-oriented agents. You may advertise a Markdown alternate (`rel="alternate"` with `type="text/markdown"`) or honor `Accept: text/markdown`. That is a convenience, not a universal requirement, and it is not a reason to drop clean HTML or structured metadata. Be cautious about asking agents to transcode large PDFs or office documents when a simpler representation exists.

**How to verify.**

If you advertise an alternate, fetch the HTML (or its `Link` header) and then fetch the Markdown URL. If you negotiate, request the page with `Accept: text/markdown` and confirm a Markdown response or a clear fallback.

### RD-04. Add FAIR Signposting links from landing pages

- **Level:** 2
- **Pillar:** Readable
- **Optional:** no
- **Kind:** standard-practice
- **Maturity:** established
- **Access needed:** Ability to set HTTP `Link` headers (often via the repository platform or reverse proxy) and/or to edit HTML `<link>` elements. Headers are lightweight for clients and often harder to implement than HTML tags.
- **Maintenance:** Recheck after platform upgrades; several repository platforms now support Signposting.
- **Sources:** [Webinar PDF p. 16](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=16); [Glossary — FAIR Signposting](../Webinar_Nov_2026/glossary.md); [FAIR Signposting](https://signposting.org/FAIR/)

**Do this.**

Use typed links so a client can walk from a landing page to a PID, metadata, content, and license without scraping. The webinar names `cite-as`, `describedby`, `item`, `license`, and `author` (among others). Implement them as HTTP `Link` headers, HTML `<link>` elements, and/or a linkset. The live deck describes Signposting as mature and low-cost, with platform-level support in systems such as Dataverse, DSpace, and InvenioRDM/Zenodo.

**How to verify.**

Request a landing page and inspect `Link` headers and/or the HTML head for those relations. Follow `cite-as`, `describedby`, `item`, and `license` targets and confirm they resolve.

### RD-05. Optionally publish llms.txt

- **Level:** 1
- **Pillar:** Readable
- **Optional:** yes
- **Kind:** advice
- **Maturity:** emerging
- **Access needed:** Permission to place `llms.txt` at the site root or in a covering subfolder.
- **Maintenance:** Curate the reading list; an outdated guide can be worse than none.
- **Sources:** [Webinar PDF p. 15](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=15); [Glossary — llms.txt](../Webinar_Nov_2026/glossary.md); [Example llms.txt](../Webinar_Nov_2026/assets/llms.txt); [llms.txt](https://llmstxt.org/); [Chrome Lighthouse llms.txt audit](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt)

**Do this.**

`llms.txt` is an optional, curated reading order for agents, not a baseline requirement for following the webinar. Version 2 (dated August 2026 in the deck) also describes pointing from each page to a Markdown alternate (`rel="alternate"` type `text/markdown`) and to the covering `llms.txt` (`rel="describedby"`), as HTML tags or HTTP `Link` headers. A file in a subfolder can cover the pages under it.

Clean semantic HTML, Signposting, and Markdown negotiation can address similar goals without this file.

**How to verify.**

`GET https://YOUR-HOST/llms.txt` (or the subfolder URL) and confirm the links you listed are the ones you intended. If you implemented v2 page pointers, inspect `rel="alternate"` and `rel="describedby"` on a sample page. An optional Chrome Lighthouse agentic-browsing audit exists for this arrangement.

**Watch for.**

Adoption is still limited. Bibliography notes attribute roughly 10% penetration to an SE Ranking analysis of nearly 300,000 domains (about 10.13% in that study)—not “10% of the web.” Do not treat the file as required for SI-oriented access.

### RD-06. Optionally document a workflow as SKILL.md

- **Level:** 1
- **Pillar:** Readable
- **Optional:** yes
- **Kind:** advice
- **Maturity:** emerging
- **Access needed:** Permission to publish a Markdown file or folder; adding executable scripts or service calls raises this to Level 3.
- **Maintenance:** Update the skill when the API or workflow changes.
- **Sources:** [Webinar PDF p. 18](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=18); [Glossary — Agent skill](../Webinar_Nov_2026/glossary.md); [Agent Skills](https://agentskills.io/)

**Do this.**

If you want to tell an agent how to perform a specific job (for example, how to call your records API), you may publish a `SKILL.md` with YAML front matter and imperative instructions. The webinar treats this as documenting a workflow. A Markdown-only skill is a static file. Packaging scripts, tool calls, or live service invocations is optional and needs software maintenance.

**How to verify.**

Fetch the `SKILL.md` URL. Confirm it states when to use the skill, points at the real documentation or OpenAPI file, and does not contradict those sources.

### RD-07. Optionally experiment with ard.json

- **Level:** 1
- **Pillar:** Readable
- **Optional:** yes
- **Kind:** advice
- **Maturity:** bleeding-edge
- **Access needed:** Permission to publish `/.well-known/ard.json`.
- **Maintenance:** High churn; specifications in this area change quickly.
- **Sources:** [Webinar PDF p. 19](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=19); [Glossary — ARD / ard.json](../Webinar_Nov_2026/glossary.md); [Example ard.json](../Webinar_Nov_2026/assets/ard.json); [ARD specification](https://agenticresourcediscovery.org/spec/)

**Do this.**

Only if you are experimenting: publish an Agentic Resource Discovery file at `/.well-known/ard.json`. The webinar marks this as bleeding edge. It is not a substitute for `robots.txt`, a sitemap, Signposting, or a documented API.

**How to verify.**

Fetch `https://YOUR-HOST/.well-known/ard.json` and confirm it parses as JSON and matches the current specification you intended to follow.

### RD-08. Optionally package skills or MCP servers as Agent Plugins

- **Level:** 3
- **Pillar:** Readable
- **Optional:** yes
- **Kind:** advice
- **Maturity:** bleeding-edge
- **Access needed:** Developer time to build and publish a plugin package.
- **Maintenance:** Keep the package aligned with evolving plugin and MCP conventions.
- **Sources:** [Webinar PDF p. 20](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=20); [Glossary — Agent Plugins](../Webinar_Nov_2026/glossary.md); [Agent Plugins](https://agent-plugins.org/)

**Do this.**

Agent Plugins is a bleeding-edge packaging format for reusable skills and MCP services. It is easy to confuse with a single `SKILL.md` or with the MCP Skills extension; they are not the same thing. Skip this unless you have a concrete distribution need.

**How to verify.**

If you publish a plugin, confirm its package files match the current Agent Plugins documentation and that any MCP endpoint it advertises actually exists.

## Callable

Dynamic, service-based reads. The webinar’s callable material is aimed at **metadata** services, not at every domain data payload (those have their own use cases and access-control needs). MCP is optional. See webinar PDF pp. 21–26 and [Being callable](../Webinar_Nov_2026/glossary.md).

A previous NIAID webinar treated APIs in more depth: [API NIAID Webinar Slides (31 March 2026)](https://github.com/go-fair-us/apireference/blob/master/docs/Presentation/API_NIAIDWebinarSlides033126.pdf). The Blueprint DOI cited on the slide is [10.5281/zenodo.17161561](https://doi.org/10.5281/zenodo.17161561).

### CAL-01. Document the metadata API with OpenAPI or Swagger

- **Level:** 3
- **Pillar:** Callable
- **Optional:** no
- **Kind:** blueprint-aligned
- **Maturity:** established
- **Access needed:** If you already run an API, publishing an OpenAPI file can be a static or generated document (closer to Level 1). Designing and operating the API itself is Level 3.
- **Maintenance:** Regenerate or edit the description when operations change.
- **Sources:** [Webinar PDF p. 21](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=21); [Glossary — API, OpenAPI](../Webinar_Nov_2026/glossary.md); [OpenAPI Specification](https://spec.openapis.org/oas/latest.html); [NIAID Blueprint](https://www.niaid.nih.gov/research/data-blueprint)

**Do this.**

Expose metadata through a documented HTTP API. Publish a machine-readable OpenAPI (or Swagger) description at a stable URL, with operation summaries, parameters, and examples. Good documentation is the slide’s first “SI aware” API point. If you do not yet operate an API, treat this as a software project rather than a file drop.

**How to verify.**

Fetch the OpenAPI or Swagger URL and confirm it parses as OpenAPI 3.x or Swagger 2.0. Confirm it describes the metadata operations you actually offer, not only a UI wrapper.

### CAL-02. Use ordinary web architecture for metadata resources

- **Level:** 3
- **Pillar:** Callable
- **Optional:** no
- **Kind:** blueprint-aligned
- **Maturity:** established
- **Access needed:** API developers and operators.
- **Maintenance:** Preserve stable URLs when systems are upgraded.
- **Sources:** [Webinar PDF p. 21](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=21); [Glossary — Cool URI, content negotiation](../Webinar_Nov_2026/glossary.md)

**Do this.**

Give metadata records stable, dereferenceable URLs; use HTTP status codes honestly; and prefer GET for retrieval of metadata. Connect each response to a documented schema or data model. The webinar notes that JSON-LD and “prefer GET” guidance here target **metadata**, not necessarily every data-file download, which may have different security and domain constraints.

**How to verify.**

Pick a public metadata record URL. Confirm GET returns the record, the status code matches the outcome (including 404 for unknown IDs), and the URL remains useful as an identifier (avoid embedding versions or software names that will break).

### CAL-03. Publish profile-shaped JSON-LD for records

- **Level:** 2
- **Pillar:** Callable
- **Optional:** no
- **Kind:** blueprint-aligned
- **Maturity:** established
- **Access needed:** Ability to embed JSON-LD in server-rendered landing pages (Level 2) and/or to offer `application/ld+json` from the API (Level 3).
- **Maintenance:** Keep the JSON-LD aligned with the HTML a person sees.
- **Sources:** [Webinar PDF p. 21](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=21); [Glossary — JSON-LD, schema.org Dataset](../Webinar_Nov_2026/glossary.md); [JSON-LD 1.1](https://www.w3.org/TR/json-ld11/)

**Do this.**

For metadata the webinar cares about, publish a JSON-LD representation—typically a `schema.org` `Dataset` or a profile built from one—on the landing page and, where you have an API, as a content type the API can return. This is also the bridge into the Meaningful items on profiles and `conformsTo`.

**How to verify.**

View page source or request `Accept: application/ld+json`. Confirm a JSON-LD block parses and includes identifier, name, and license (or a clear access condition) when those apply.

**Watch for.**

Do not put controlled payloads in an open JSON-LD block. Open metadata can still describe a restricted dataset (see MEA-04).

### CAL-04. Treat MCP as an optional enhancement, not a plan by itself

- **Level:** 3
- **Pillar:** Callable
- **Optional:** yes
- **Kind:** advice
- **Maturity:** established
- **Access needed:** Developers and operators, plus your security team if you expose tools that can change state or retrieve non-public data.
- **Maintenance:** Ongoing service operation, protocol updates, and access control.
- **Sources:** [Webinar PDF pp. 22–25](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=22); [Glossary — Model Context Protocol](../Webinar_Nov_2026/glossary.md); [MCP specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28); [MCP registry](https://registry.modelcontextprotocol.io/)

**Do this.**

MCP is a shared convention for tools, resources, and prompts. The webinar’s own view is that MCP is **not required** in order to address SI-oriented access, and that MCP alone is not an “SI-readiness plan.” If you do run a server, think beyond wrapping each API call as a tool: offer resources an agent can read and prompts that start from your wording. Involve security reviewers; exposing tools increases the attack surface.

A well documented API, or even a CLI over that API, may be enough.

**How to verify.**

If you do not run MCP, record that agents should use the OpenAPI description (CAL-01) and stop here. If you do, confirm `tools/list`, `resources/list`, and `prompts/list` (as applicable) match what you intended to expose, and that your security review covered those primitives.

### CAL-05. If you protect an HTTP MCP server, use scoped, short-lived tokens

- **Level:** 3
- **Pillar:** Callable
- **Optional:** yes
- **Kind:** access-enforcement
- **Maturity:** established
- **Access needed:** Developers familiar with OAuth and operators who can register clients.
- **Maintenance:** Token lifetimes, redirect configuration, and scope reviews.
- **Sources:** [Webinar PDF p. 26](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=26); [Glossary — OAuth](../Webinar_Nov_2026/glossary.md); [MCP authorization (2026-07-28)](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)

**Do this.**

Authorization is **optional** in MCP. The 2026-07-28 authorization model applies to **protected HTTP** MCP servers (not the stdio transport, which typically uses local environment credentials). When you do protect an HTTP server, follow that specification’s OAuth 2.1 pattern: unauthenticated requests are pointed at how to obtain access; the client obtains a token audience-bound to that server; later requests carry the token.

Prefer scoped, short-lived tokens over long-lived shared API keys. Example scope names such as `mcp:resources:read` are **illustrative server-defined scopes**, not a universal MCP permission registry. Initial browser sign-in or consent may still be required; the goal is to avoid sharing long-lived secrets and repeating manual key entry, not to claim that no person ever signs in.

**How to verify.**

If the server is open, confirm that fact is intentional and documented. If it is protected, attempt a call without a token and confirm you receive an unauthorized response that points to the authorization server, then complete the documented flow once and confirm a scoped token is issued for that MCP server only.

**Watch for.**

The PDF closing line about acting “without … someone logging in by hand each time” should not be read as “no consent ever.”

## Meaningful

Structured context—identifiers, vocabularies, profiles, rights, provenance, and optional shapes or mappings—so a model is less likely to invent your schema. See webinar PDF pp. 27–34 and [Being meaningful](../Webinar_Nov_2026/glossary.md). A data dictionary is already useful; a formal ontology is not automatically better.

### MEA-01. Give people, organizations, projects, and outputs persistent identifiers

- **Level:** 2
- **Pillar:** Meaningful
- **Optional:** no
- **Kind:** blueprint-aligned
- **Maturity:** established
- **Access needed:** Repository-platform settings and metadata-entry permissions; minting DOIs may involve your DOI service.
- **Maintenance:** Keep identifiers resolvable; do not reuse them for a different object.
- **Sources:** [Webinar PDF p. 28](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=28); [Glossary — persistent identifier](../Webinar_Nov_2026/glossary.md)

**Do this.**

Assign and display persistent identifiers an agent can cite and follow. The webinar’s set is a DOI or accession for data, ORCID for people, ROR for organizations, RRID for research resources, and RAiD for projects—use the ones that apply to what you actually describe.

**How to verify.**

On a sample record, follow the data identifier, at least one creator ORCID, and an organization ROR (when present) and confirm each resolves to the intended landing page or registry record.

### MEA-02. Publish a data dictionary or vocabulary at a stable URL

- **Level:** 1
- **Pillar:** Meaningful
- **Optional:** no
- **Kind:** advice
- **Maturity:** established
- **Access needed:** Permission to publish a page or file at a stable URL. Building a formal ontology is a larger modeling effort, not a higher “grade.”
- **Maintenance:** Version the vocabulary when terms change.
- **Sources:** [Webinar PDF p. 29](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=29); [Glossary — vocabulary, data dictionary](../Webinar_Nov_2026/glossary.md); [From terms to ontologies](../Webinar_Nov_2026/supplementalInformation/termsToOntologies.md); [Vocabulary tools](../Webinar_Nov_2026/supplementalInformation/vocabularies.md)

**Do this.**

Publish the words and fields you use: at minimum an informal data dictionary with definitions, units, and allowed values. A term list, a taxonomy, or an ontology adds structure for some use cases; choose a proportionate approach rather than climbing a ladder for its own sake. Reuse an existing vocabulary when one already covers the subject.

**How to verify.**

Fetch the stable URL. Confirm a new staff member (or an agent) can look up a core field such as an assay or study type and find a definition.

### MEA-03. Reuse an existing metadata profile and declare conformsTo

- **Level:** 2
- **Pillar:** Meaningful
- **Optional:** no
- **Kind:** blueprint-aligned
- **Maturity:** established
- **Access needed:** Ability to edit landing-page JSON-LD or the metadata template the repository emits.
- **Maintenance:** Recheck after schema or harvester changes.
- **Sources:** [Webinar PDF p. 30](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=30); [Glossary — Profile, conformsTo](../Webinar_Nov_2026/glossary.md); [DataCite Metadata Schema 4.6](https://schema.datacite.org/meta/kernel-4.6/); [Bioschemas Dataset](https://bioschemas.org/profiles/Dataset/); [NIAID Data Ecosystem schemas](https://github.com/NIAID-Data-Ecosystem/nde-schemas)

**Do this.**

Reuse a profile that already fits your objects instead of inventing a parallel schema. The webinar table highlights DataCite Metadata Schema 4.6 (DOI-backed citation metadata; not built primarily on schema.org), Bioschemas Dataset, CODATA CDIF (a set of profiles for cross-domain FAIR functions), the NIAID Data Ecosystem schema (IID fields based on Bioschemas), Croissant 1.1 (including RAI and Geo extensions named on the slide), and RO-Crate 1.2, with Science-on-Schema.org among others of interest.

Declare which profile a record follows with `conformsTo`, so agents and validators know which rules to apply.

**How to verify.**

On a sample JSON-LD or DataCite record, confirm `conformsTo` (or the platform’s equivalent profile declaration) points at the profile you claim, and that required fields of that profile are populated.

**Watch for.**

Do not describe every listed framework as a schema.org profile. DataCite is the clear exception on the slide; CDIF is a framework of profiles rather than a single schema.org shape.

### MEA-04. State rights and licenses in the metadata, not only in prose

- **Level:** 2
- **Pillar:** Meaningful
- **Optional:** no
- **Kind:** rights-signal
- **Maturity:** established
- **Access needed:** Metadata editors and, for controlled data, access-policy owners.
- **Maintenance:** Update the record if the license or access condition changes.
- **Sources:** [Webinar PDF p. 31](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=31); [Glossary — rights and access, SPDX, conditionsOfAccess](../Webinar_Nov_2026/glossary.md); [SPDX license list](https://spdx.org/licenses/); [TDM reservations](../Webinar_Nov_2026/supplementalInformation/tdm.md); [NOT-OD-25-081](https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-081.html)

**Do this.**

Record the license that actually applies to each object, preferably with an SPDX identifier and a resolvable license URL in schema.org `license` (or the equivalent DataCite rights field). Use HTTPS license URLs in new records (for example `https://spdx.org/licenses/CC0-1.0.html` when CC0 is the real license). If access is restricted, say so in metadata (for example schema.org `conditionsOfAccess`) and keep the bytes behind the appropriate control.

Rights metadata is not a crawl rule. A public landing page does not make the underlying data free for every use.

**How to verify.**

On open and, if you have one, controlled-access examples, confirm the machine-readable license or access condition matches the human-readable policy. Resolve the license URL.

**Watch for.**

License terms vary across NIAID-funded repositories and across datasets. This checklist does **not** assume NIAID or NIH data are public domain or CC0. NIH notice [NOT-OD-25-081](https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-081.html) addresses sharing, retaining, or training generative models on controlled-access human genomic data; read that notice rather than inferring permission from open metadata. The JSON fragment on the slide is illustrative, not a complete record.

### MEA-05. Make citation, contributors, and roles machine-readable

- **Level:** 2
- **Pillar:** Meaningful
- **Optional:** no
- **Kind:** blueprint-aligned
- **Maturity:** established
- **Access needed:** Metadata editors; some platforms already expose cite-as links or CRediT fields.
- **Maintenance:** Update citations when versions change.
- **Sources:** [Webinar PDF p. 32](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=32); [Glossary — attribution and authority, CRediT](../Webinar_Nov_2026/glossary.md); [CRediT](https://credit.niso.org/); [Minimum citation guidelines](https://www.gofair.us/citation-recommendations)

**Do this.**

Provide a citation an agent can find (a `cite-as` link, BibTeX, or the platform’s equivalent) and identify contributors with persistent identifiers. Where roles matter, use a controlled taxonomy such as NISO CRediT with schema.org `Role`. The JSON on the slide is a fragment illustrating a role, not a complete Dataset record.

**How to verify.**

From a landing page, follow Signposting `cite-as` or the visible citation download and confirm it matches the record. Confirm at least one contributor PID resolves.

### MEA-06. Record lineage, versions, and integrity information

- **Level:** 2
- **Pillar:** Meaningful
- **Optional:** no
- **Kind:** standard-practice
- **Maturity:** established
- **Access needed:** Metadata editors and, for package checksums, release engineering or repository administrators.
- **Maintenance:** Add relations when you derive or version a dataset.
- **Sources:** [Webinar PDF p. 33](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=33); [Glossary — lineage, PROV-O](../Webinar_Nov_2026/glossary.md); [PROV-O](https://www.w3.org/TR/prov-o/)

**Do this.**

Show where a dataset came from and how it changed. The webinar points at W3C PROV-O relations (`wasGeneratedBy`, `wasDerivedFrom`, `wasAssociatedWith`, and others), DataCite version and related-identifier relations such as `IsVersionOf`, `IsNewVersionOf`, and `IsDerivedFrom`, links to upstream sources and downstream products, and checksums or digital signatures on packages.

**How to verify.**

On a versioned or derived record, confirm the relation types are present and that related identifiers resolve. If you publish packages, confirm a checksum is advertised and matches the file.

### MEA-07. Optionally publish a TDM reservation signal

- **Level:** 1
- **Pillar:** Meaningful
- **Optional:** yes
- **Kind:** rights-signal
- **Maturity:** emerging
- **Access needed:** Permission to publish `/.well-known/tdmrep.json` and/or to set HTTP headers or HTML metadata (headers are Level 2).
- **Maintenance:** Keep the site-level file and per-resource declarations consistent.
- **Sources:** [Webinar PDF p. 31](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=31); [TDM reservations](../Webinar_Nov_2026/supplementalInformation/tdm.md); [TDMRep CG Final Report](https://www.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240510/); [Bibliography — Rights, credit, and lineage](../Webinar_Nov_2026/bibliography.md)

**Do this.**

TDMRep is a W3C Community Group Final Report (not a W3C Recommendation) for machine-readable text-and-data-mining rights signals, including `/.well-known/tdmrep.json`, HTTP headers, and HTML metadata. A `tdm-reservation` value of `1` reserves TDM rights in that declaration; `0` means they are not reserved by that declaration. An optional `tdm-policy` URL can point to more detail.

This is a **rights signal**, not a crawler block, and not a substitute for reading applicable law or licenses. It is commonly discussed in EU and STM reservation settings; US practice differs. This item is not legal advice.

**How to verify.**

If you publish the well-known file, fetch it and confirm `tdm-reservation` (and `tdm-policy`, if used) match your intended statement. Do not expect the file alone to change whether a client can GET a URL.

### MEA-08. Publish SHACL shapes and validate records against them

- **Level:** 3
- **Pillar:** Meaningful
- **Optional:** no
- **Kind:** standard-practice
- **Maturity:** established
- **Access needed:** Someone comfortable with RDF and SHACL. Running the validator locally or in CI does **not** require operating a public service. Hosting a live validator is an extra choice.
- **Maintenance:** Update shapes when the profile changes; keep example records passing.
- **Sources:** [Webinar PDF p. 34](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=34); [Glossary — SHACL](../Webinar_Nov_2026/glossary.md); [SHACL Recommendation](https://www.w3.org/TR/shacl/)

**Do this.**

Write SHACL shapes that say what a valid record looks like (the slide’s example: every sample has a collection date and a host taxon). Publish the shapes at a stable URL so agents can see your expectations. Validate submissions or published JSON-LD locally, in a batch job, or in CI. The webinar marks deeper context work as caution / bleeding edge in places; SHACL itself is a W3C Recommendation.

**How to verify.**

Run a SHACL validator (for example pySHACL) on one record you believe is valid and on one deliberate invalid record. Confirm the valid record passes and the invalid record fails for the expected constraint. If you publish the shapes, fetch their URL.

### MEA-09. Optionally declare derivation rules with SPARQL RL

- **Level:** 3
- **Pillar:** Meaningful
- **Optional:** yes
- **Kind:** advice
- **Maturity:** draft
- **Access needed:** Developers or ontologists who can maintain RDF rules.
- **Maintenance:** Rules need review when vocabularies change. The language is a W3C Working Draft.
- **Sources:** [Webinar PDF p. 34](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=34); [Glossary — SPARQL RL](../Webinar_Nov_2026/glossary.md); [SPARQL RL](https://www.w3.org/TR/sparql-rl/)

**Do this.**

If curation knowledge is currently hidden in code (for example inferring a parent category), you may declare it with SPARQL RL so the rule is explicit. Treat SPARQL RL as a **W3C Working Draft** and cite the current TR: [https://www.w3.org/TR/sparql-rl/](https://www.w3.org/TR/sparql-rl/). This is optional deeper-context work, not a baseline.

**How to verify.**

If you adopt it, keep a small test graph that shows a rule firing as you intend, and link the draft you implemented.

**Watch for.**

The PDF face still prints an older date and a `sparql12-rl` path. Prefer the current shortname URL above rather than copying a date from the slide.

### MEA-10. Optionally publish mappings as SSSOM/TSV

- **Level:** 1
- **Pillar:** Meaningful
- **Optional:** yes
- **Kind:** standard-practice
- **Maturity:** established
- **Access needed:** Permission to publish a file, plus people who understand both vocabularies well enough to map them. Creating high-quality mappings is skilled work; hosting a mapping *service* would be Level 3.
- **Maintenance:** Update mappings when either vocabulary versions.
- **Sources:** [Webinar PDF p. 34](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=34); [Glossary — SSSOM](../Webinar_Nov_2026/glossary.md); [SSSOM](https://mapping-commons.github.io/sssom/); [SSSOM specification (dev)](https://mapping-commons.github.io/sssom/dev/)

**Do this.**

If you need to say “our term X matches term Y,” publish a mapping set using SSSOM. The common exchange format is **SSSOM/TSV** (not CSV) with mapping-set metadata. Each row records the two terms and a relation such as exact, close, broader, or related, and it can record a justification. Fields such as `author_id` and `confidence` are **optional**; do not imply that every row names an author or carries an independently established confidence value.

**How to verify.**

Fetch the TSV (or the URL you advertised). Confirm it is tab-separated, includes the mapping columns you intended, and that optional provenance columns are present only when you actually have the information.

## Evaluation

Evaluation is a large topic; the webinar treats it as a place to start, not a scoring system. Different checks answer different questions. See webinar PDF p. 36, [Checking the result](../Webinar_Nov_2026/glossary.md), and [Evaluation](../Webinar_Nov_2026/supplementalInformation/evaluation.md).

### EVL-01. Try an agent against your public documentation and record what happens

- **Level:** 1
- **Pillar:** Evaluation
- **Optional:** no
- **Kind:** advice
- **Maturity:** established
- **Access needed:** Anyone who can use a public chat or agent interface and read your public pages.
- **Maintenance:** Repeat after you change robots rules, sitemaps, or landing pages.
- **Sources:** [Webinar PDF p. 36](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=36); [Evaluation prompts (handout)](../Webinar_Nov_2026/supplementalInformation/evaluationPrompts.md); [prompts/evals](../../prompts/evals)

**Do this.**

Give an agent or a simple chat UI links to your site or API documentation and see what it can find. Write down the question, whether the answer was supported by fetched evidence, and what was missing (license, DOI, data dictionary, and so on). Starting prompts live in this repository under `prompts/evals`.

**How to verify.**

Keep a short written record (even a few rows) of questions, dates, tools used, and whether the supporting URL was correct.

### EVL-02. Keep access checks, answerability tests, and accuracy reviews separate

- **Level:** 1
- **Pillar:** Evaluation
- **Optional:** no
- **Kind:** advice
- **Maturity:** established
- **Access needed:** The people who run documentation and metadata review.
- **Maintenance:** Do not replace human review of content with a single vendor “agent score.”
- **Sources:** [Evaluation](../Webinar_Nov_2026/supplementalInformation/evaluation.md); [Webinar PDF p. 36](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=36)

**Do this.**

Ask three different questions and do not merge the answers into one grade:

1. Can an agent *discover and read* the documentation (access and readability)?
2. Can it *answer the questions your users care about*, with evidence?
3. Are the docs and examples *accurate*?

Tools mentioned in the evaluation handout (including early-stage documentation checkers) may help with (1). Competency questions help with (2). Human review, and tools that execute documented examples, help with (3). No single score covers all three, and a passing readability check is not a measure of trustworthiness.

**How to verify.**

In your notes, label each test as access/readability, answerability, or accuracy. If you record a numeric score from a tool, record what that tool actually measured.

### EVL-03. Optionally reuse published audits and portal comparisons

- **Level:** 1
- **Pillar:** Evaluation
- **Optional:** yes
- **Kind:** advice
- **Maturity:** emerging
- **Access needed:** A browser, and (for NDE) a public portal account if the feature requires one.
- **Maintenance:** Repeat when you change `llms.txt` or portal metadata.
- **Sources:** [Webinar PDF p. 36](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=36); [NDE AI-assisted search](https://data.niaid.nih.gov/knowledge-center/ai-assisted-search); [Chrome Lighthouse llms.txt audit](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt)

**Do this.**

If they apply to you: compare NIAID Data Ecosystem search with AI-assisted search on and off; run Chrome Lighthouse’s `llms.txt` audit if you publish that file; try the webinar evaluation prompts. These are diagnostics, not badges.

**How to verify.**

Save the date and the tool output (or a screenshot) next to the checklist item you thought you had completed.

## Closing reminder

Other than APIs and MCP services, almost everything in the webinar is a static text file your server can expose. That does not make the work easy: the files need governance and curation. Prefer durable investments that help human users as well as agents. See webinar PDF p. 37 and the [resource list on p. 38](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf#page=38).
