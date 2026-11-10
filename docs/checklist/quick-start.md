# Ways to make your repository easier for AI to use

These four sections follow the webinar: Be Reachable, Be Readable, Be Callable, and Be Meaningful. They can make a public repository easier for AI to use. They are not a guarantee of better answers, and you do not have to launch new services. A crawl preference is not the same as granting or denying permission to train a model.

## Be Reachable

Decide what should be easy to fetch and what must stay behind the protections you already use. Restricted data should stay protected, while public descriptive records can remain open without a special login. Confirm that a restricted data download still requires the intended authorization.

Possible approaches: Review how your content delivery network (CDN), web application firewall, or host treats automated traffic, including access rules and rate limits. Publish a robots.txt file to state crawl preferences for cooperating visitors. A preference does not enforce itself; authentication, access controls, and rate limits are what actually allow or deny a request. Optional usage-preference signals, some still drafts, do not by themselves block a fetch or settle training rights.

## Be Readable

Say what a collection covers, who it is for, and what it cannot tell someone. Put the important wording in the first HTML page a visitor receives, so people and software do not have to run extra programs just to read it.

Possible approaches: Server-rendered HTML for the meaningful text; a sitemap that lists public record addresses; FAIR Signposting links that point to related files and metadata. Offering Markdown as another representation, or publishing an llms.txt file, is optional. The llms.txt idea is still a proposal, and skipping either convenience is not a failure.

## Be Callable

Write down how people already search, request access, and download, so people and software can follow those paths. If you already offer a way for software to retrieve data, document it too. You do not need a new API.

Possible approaches: Existing HTTP APIs, described with an OpenAPI document when you have one; JSON-LD on landing pages or through that API so records carry structured meaning. The Model Context Protocol (MCP) is an optional enhancement, not a requirement. If you protect an HTTP service, use authentication and appropriately scoped authorization rather than leaving a restricted download unprotected.

## Be Meaningful

Make it easy to tell what a record is, who created it, how to credit them, and whether others may reuse the work. Keep those facts in a predictable place. A formal ontology is not required.

Possible approaches: Persistent identifiers for works and people, such as DataCite DOIs and ORCID iDs; shared vocabularies or profiles such as schema.org, DCAT, or Bioschemas; a license or rights statement; a citation; and provenance. Optional SHACL shapes can help check records against a published profile, and optional SSSOM tables can record term mappings. Neither is required, and publishing shapes is not certification.

[Full checklist](checklist.md) · [Webinar](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf)
