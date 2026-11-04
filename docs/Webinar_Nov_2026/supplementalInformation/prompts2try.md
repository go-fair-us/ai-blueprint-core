# Prompts to try during the talk

A follow-along sheet for "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026).

Each prompt asks one question about a public repository. The full text lives in [`../../../prompts/evals`](../../../prompts/evals). This page says when to try it, what it asks, and how to run it in ChatGPT, Claude, Grok, or a harness such as [Hermes](https://hermes-agent.nousresearch.com). Definitions of the slide words are in the [glossary](../glossary.md). The catalog of every check is [evalPrompts.md](../../evalPrompts.md).

Use your own repository, or a public one you already know. One fresh chat per prompt keeps the previous question from leaking into the next report.

## How to run one prompt

Open the prompt file from the link under that section. Copy the whole file.

**ChatGPT, Claude, or Grok.** Start a new chat. Paste the file. Under it, add the site you want checked:

```text
Repository origin: https://www.example.org/
Record URL: none
```

Replace the origin with the site's home URL. When you have a dataset, study, or record page, put that URL on the second line. Send the message. The model should fetch the site and return a YAML report.

A web chat often summarizes a page and drops status codes, headers, and JSON-LD blocks inside `script` tags. The prompt tells the model to mark a check `not-observable` and write `client cannot see …` when that happens. Read that as a property of the chat, and keep the checks it could support.

**Hermes, Pi, or another harness that can run HTTP.** Paste the same file as the task and include the two lines above. A client that returns the status code, the headers, and the unmodified body can fill more of the report. `curl -i` is enough. In this repository's Pi launcher, the same files are slash commands: `./bin/pi`, then `/sitemap https://www.example.org/`. See [HARNESS_QUICKSTART.md](../../../HARNESS_QUICKSTART.md).

Hermes also has a separate `/fair-assessment` skill in [`../../../harnesses/hermes/fair-assessor`](../../../harnesses/hermes/fair-assessor). That skill scores the whole Blueprint. The prompts on this page each stop at one question.

Stay on the repository's own host. Send no password or API key. The prompts cap how many pages they open.

## What the report means

Every prompt asks for the same YAML shape: a `verdict`, a list of `checks`, the time, the client, and a `fetches` list. `verdict` is one of:

| Verdict | Reading |
|---|---|
| `present` | The checks this prompt requires all passed. |
| `partial` | The site answered, and the checks are mixed. |
| `absent` | The file or behavior is missing. |
| `blocked` | The response was a challenge, HTTP 401 or 403, or an access wall. |
| `not-observable` | The page, example, or raw response this question needs was not available to the client. |

## Be reachable

The slide covers `robots.txt`, content-use preferences, and an ordinary GET that is not blocked.

### Reachable fetch

[`reachable-fetch.md`](../../../prompts/evals/reachable-fetch.md)

Asks whether a normal HTTP GET, without running JavaScript, gets a real response for the homepage and one record. A JavaScript application shell still counts as a successful fetch. Whether the record's text is in that HTML is the next section.

Paste the file with your origin. Add a record URL when you have one. With `Record URL: none`, the prompt looks for one public record and says how it found it.

### Robots policy

[`robots-policy.md`](../../../prompts/evals/robots-policy.md)

Reads `robots.txt` and reports what it allows for a search indexer, a user-driven fetcher, and a trainer crawler. It also notes whether the file names a sitemap. Allow and Disallow are observations. Permission for a trainer is not a passing grade.

Paste the file with the origin. A record URL is optional and is not required for this question.

## Be readable

The slide covers sitemaps, `llms.txt`, Markdown alternates, pages whose text arrives only after JavaScript, bulk download, and docs an agent can follow.

### llms.txt

[`llms-txt.md`](../../../prompts/evals/llms-txt.md)

Looks for an `llms.txt` file, then checks whether a page points at a Markdown alternate and at the `llms.txt` that describes it.

Paste the file with the origin. A record URL is the page used for the link check. With `Record URL: none`, the prompt uses the homepage.

### Sitemap

[`sitemap.md`](../../../prompts/evals/sitemap.md)

Looks for a sitemap or a sitemap index that an agent can discover, and checks whether the listed URLs include dataset, study, or record pages.

Paste the file with the origin. A record URL is optional. When you supply one, the prompt looks for that URL in the sitemap.

### Server-rendered content

[`server-rendered-content.md`](../../../prompts/evals/server-rendered-content.md)

Checks whether the record title, description, identifier, and license are in the first HTML response, before any browser script runs.

Paste the file with the origin and a record URL. This question needs a record page.

### Markdown negotiation

[`markdown-negotiation.md`](../../../prompts/evals/markdown-negotiation.md)

Checks whether the record returns Markdown when the request asks for `Accept: text/markdown`, or advertises a Markdown alternate with `rel="alternate"` and `type="text/markdown"`. Either path answers the question.

Paste the file with the origin and a record URL. A web chat that cannot set the `Accept` header should mark that half `not-observable`. A harness can send the header with `curl`.

### Bulk export

[`bulk-export.md`](../../../prompts/evals/bulk-export.md)

Looks for a bulk download or a bulk Markdown export linked from the site or from `llms.txt`.

Paste the file with the origin. A record URL is optional.

### Agent documentation

[`agent-documentation.md`](../../../prompts/evals/agent-documentation.md)

Looks for data-access or API docs linked where an agent can follow them, including a `SKILL.md` when the site publishes one.

Paste the file with the origin. A record URL is optional.

## Be callable

The slide covers a metadata API, OpenAPI, ordinary HTTP behavior, and an optional remote MCP server. Run these in order when you want the later prompt to reuse the URL the earlier one found.

### OpenAPI discovery

[`openapi-discovery.md`](../../../prompts/evals/openapi-discovery.md)

Starts from the public site and looks for one OpenAPI or Swagger document. It finds the document. It does not score the API against Blueprint Section 3.

Paste the file with the origin. A record URL is optional.

### Metadata API

[`metadata-api.md`](../../../prompts/evals/metadata-api.md)

Looks for one unauthenticated GET whose path is a resource address and whose body is JSON-LD for a dataset or study. It reports the status, the content type, and whether the body has `@context` and `@type`.

Paste the file with the origin. Add a record URL when it helps the model recognize a real study id in the docs. If you already know the metadata URL, add a third line: `Metadata URL: https://www.example.org/api/study/SDY1`.

### API HTTP behavior

[`api-http-behavior.md`](../../../prompts/evals/api-http-behavior.md)

Takes that same metadata GET and records the status, content type, redirect, and cache headers.

Run the metadata prompt first, then paste this file with the origin and the GET URL the previous report used. Add `Metadata URL:` on its own line when the chat does not keep the earlier turn.

### MCP exposure

[`mcp-exposure.md`](../../../prompts/evals/mcp-exposure.md)

Looks for a public advertisement of a remote MCP server, on the site or in a registry entry the site points to. A missing server is a finding, and the prompt treats a remote MCP server as optional.

Paste the file with the origin. A record URL is optional.

## Be meaningful

The slide covers persistent identifiers, a published vocabulary, one schema.org `Dataset` block, a declared metadata profile, SHACL shapes, SSSOM mappings, and competency questions the repository writes itself.

### Dataset JSON-LD

[`dataset-jsonld.md`](../../../prompts/evals/dataset-jsonld.md)

Checks the record page for one server-rendered schema.org `Dataset` JSON-LD block, including the core fields.

Paste the file with the origin and a record URL. A chat that converts the page to Markdown and drops `script` blocks should mark the block `not-observable` rather than guess.

### Persistent identifiers

[`persistent-identifiers.md`](../../../prompts/evals/persistent-identifiers.md)

Reports which of a DOI or accession, an ORCID, a ROR, and an RRID appear as IRIs in the record's machine-readable metadata.

Paste the file with the origin and a record URL.

### Vocabulary

[`vocabulary.md`](../../../prompts/evals/vocabulary.md)

Looks for a stable glossary, data dictionary, or field list, and for a link to an ontology the repository uses. An informal field list counts. A link to an ontology the site already cites is the second part.

Paste the file with the origin. A record URL is optional. Use it when the record page is what links the glossary.

### Metadata profile

[`metadata-profile.md`](../../../prompts/evals/metadata-profile.md)

Checks whether the record says which profile it follows, with `conformsTo` or an equivalent URL. The slides name schema.org Dataset, Science-on-Schema.org, Bioschemas, the NIAID Data Ecosystem fields, Croissant, and RO-Crate. The question is whether the record declares one.

Paste the file with the origin and a record URL.

### SHACL shapes

[`shacl-shapes.md`](../../../prompts/evals/shacl-shapes.md)

Looks for record or submission rules published as SHACL. It looks for the file. It does not run a validator.

Paste the file with the origin. A record URL is optional.

### SSSOM mappings

[`sssom-mappings.md`](../../../prompts/evals/sssom-mappings.md)

Looks for a public SSSOM file: a table of "our term matches their term," with a relation, a justification, and who asserted it.

Paste the file with the origin. A record URL is optional.

### Competency questions

[`competency-questions.md`](../../../prompts/evals/competency-questions.md)

Checks that the site publishes questions an agent could use as tests of this repository. It quotes questions the site wrote. It does not answer them.

Paste the file with the origin. A record URL is optional. Save the questions the report quotes. The evaluation section runs them.

## Rights, credit, and lineage

These slides sit with the four "Be" sections. A scrape can drop the license, the citation, and the history of the file.

### Rights and license

[`rights-and-license.md`](../../../prompts/evals/rights-and-license.md)

Checks whether the license and the conditions of access are in machine-readable metadata on the record.

Paste the file with the origin and a record URL.

### Citation

[`citation.md`](../../../prompts/evals/citation.md)

Looks for a public citation pattern, with creators, that an agent can read.

Paste the file with the origin. Add a record URL when the citation lives on that page.

### Provenance and lineage

[`provenance-lineage.md`](../../../prompts/evals/provenance-lineage.md)

Checks whether the record's machine-readable metadata says which version it is, where it came from, and how to check that the files are intact.

Paste the file with the origin and a record URL.

## Evaluation

The evaluation slide names three ways to tell whether the work paid off: a Chrome Lighthouse agent audit, server logs split by user agent, and the repository's own competency questions run against an agent. This sheet covers the third. Lighthouse and log breakdowns use a browser audit or the repository's own logs.

Run [competency questions](#competency-questions) first when you want the agent to use a list the site published.

### Competency answerability

[`competency-answerability.md`](../../../prompts/evals/competency-answerability.md)

Tries to answer up to three of those questions from the public site alone. An answer counts when the report quotes text or a field fetched in that run. The path it records shows which of the earlier features helped: `llms.txt`, a sitemap, JSON-LD, an API, or docs.

Paste the file with the origin. Under it, paste up to three questions, one per line. When you leave the questions out, the prompt uses up to three questions it can find on the site. Use each question as written.

```text
Repository origin: https://www.example.org/
Questions:
1. How many studies mention rheumatoid arthritis?
2. What license applies to study SDY1?
3. Which ontology does the assay field use?
```
