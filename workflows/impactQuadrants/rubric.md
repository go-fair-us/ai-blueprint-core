---
rubric: impact-quadrants
version: "1.0"
date: 2026-11-17
---
# Effort / impact rubric for agent-access gaps

You place each gap on two axes that run from -1 to 1, with 0 as the midpoint. A gap is
one webinar check that the facet review marked `absent` for this repository. Place the
fix that would close the gap, not the gap itself. Use the evidence and the operator
notes you are given. Do not assume work exists that the evidence does not show.

## x: effort to implement

| x | Anchor | Typical fixes |
|---|---|---|
| -1.0 to -0.7 | One static file or one server setting; hours; one person | add a `Sitemap:` line, publish `robots.txt` groups, publish `llms.txt` |
| -0.6 to -0.3 | Small change to existing templates or content; days | add a JSON-LD block to an existing page template, generate a sitemap from the catalogue, write an agent-facing docs page |
| -0.2 to 0.2 | Moderate engineering inside one existing system; one to three weeks | server-render record fields, Markdown alternates, fix API status codes and media types, a bulk metadata dump |
| 0.3 to 0.6 | A new component or interface; weeks to a few months | an OpenAPI document for an undocumented API, an open metadata API, minting persistent identifiers |
| 0.7 to 1.0 | New infrastructure or cross-team governance; months or more | an MCP server, curated SHACL shapes with a published profile, curated SSSOM mappings |

## y: impact on agent access

| y | Anchor | Meaning |
|---|---|---|
| 0.7 to 1.0 | Removes a blocker | without this fix an agent cannot reach, find or read the repository's records at all |
| 0.3 to 0.6 | Opens access at scale | records become discoverable, callable or downloadable in bulk by most agents |
| -0.2 to 0.2 | Improves working access | access already works; this makes it cheaper, faster or more reliable |
| -0.6 to -0.3 | Semantic enrichment | helps advanced or semantic-web agents interpret records; few agents use it today |
| -1.0 to -0.7 | Marginal | little or no change in what an agent can do |

## Rules

1. Judge impact in context. If the repository's records cannot be reached or read
   (see the verdicts of the other checks), fixes that only matter after records are
   readable get less impact until the blocker is fixed. Say so in the rationale.
2. Judge effort from what already exists. If the evidence shows the data is already
   in an API or a page template, the fix is cheaper than building it from nothing.
3. Use the whole range. Do not put every point near 0.
4. One placement per gap id you are given. Do not add, merge or drop gaps.
5. `fix_label`: an imperative fix of at most 40 characters, e.g. "Publish OpenAPI for /api".
6. `rationale`: one sentence of at most 200 characters naming the evidence that set x and y.
7. `confidence`: `high` when the evidence names the missing artifact directly, `medium`
   when it is inferred, `low` when the evidence is thin or the block did not parse.

## Quadrants

| Quadrant | Region |
|---|---|
| Quick wins | x < 0 and y >= 0 |
| Big bets | x >= 0 and y >= 0 |
| Easy follow-ons | x < 0 and y < 0 |
| Plan for later | x >= 0 and y < 0 |
