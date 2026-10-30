---
description: "Using only what the public site serves, can an agent answer up to three competency questions about this repository's data?"
argument-hint: "<origin-url> [questions]"
---

Repository origin: $1
Questions: ${2:-none}

The values above are the inputs for this run. When a value is `none`, follow the procedure's rule for that missing input. If the origin is empty, stop and ask for the repository origin URL. Do not fetch.

Follow the evaluation below exactly. Stay inside its checks.

# Competency answerability

**Question:** Using only what the public site serves, can an agent answer up to three competency questions about this repository's data?

Slide theme: Evaluation, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). The slides list three ways to tell whether agent-readiness work paid off: a Chrome Lighthouse agent audit, server logs broken down by user agent, and the repository's own competency questions run against an agent. This prompt is the third. `competency-questions.md` checks that a list is published. This prompt runs the questions.

## Role

You act as an ordinary agent visiting the site for a user. Answer each question from pages and responses you fetch in this run. Do not use prior knowledge of the repository, its papers, or its data. An answer counts only when you can quote the fetched text or field that supports it.

Record the path you took for each question. The path shows which readiness features helped: `llms.txt`, a sitemap, JSON-LD, an API, docs, or search. A question that needs a feature the site lacks is useful evidence. Name the missing feature in `gaps`.

## Inputs

- Repository origin URL (required).
- Questions (optional). Up to three questions from the user. When none are given, use up to three questions from the page `competency-questions.md` found. When neither exists, stop with verdict `not-observable`.

Use each question as written. Do not reword a question to make it easier. Each question should have one checkable answer, such as a count, a name, an identifier, or yes or no. When a question has no checkable answer, say so and score it `not-observable`.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no record ids. Do not load-test, and do not retry in a loop.

This prompt has its own caps, because it follows the site the way an agent would: at most 5 requests per question and 15 in total. Count each GET, HEAD, API call, and rendered view. Prefer the raw HTTP body. When a page is an application shell, or the answer is only in the rendered view, render that same URL once and continue the question. Record that hop as `rendered` in evidence. A need for JavaScript does not by itself stop the question. The rendered request counts toward the 5-request cap. Do not render a second URL on the same hop, and do not download script bundles. When you cannot render, record that and continue with the raw body.

Client check. Before the first fetch, name the client you use and say whether it returns the status code, the response headers, and the unmodified body. Many agent fetch tools convert HTML to Markdown or summarize it. That drops `script`, `meta`, and `link` elements and hides headers. When your client cannot show evidence a check needs, set that check to `not-observable` and write `client cannot see <what>` in `evidence`. Do not infer it.

A challenge, HTTP 401, or HTTP 403 on a step is `blocked` for that question.

## Checks

### Procedure

1. List the questions and where they came from.
2. For each question, start at the homepage or `llms.txt`. Choose the next request from links, documented endpoints, or a sitemap. When a page is an application shell, render that same URL once and keep going. Stop when you have a supported answer, when the budget for that question is spent, or when the path dead-ends.
3. For each question, record the answer, the quote that supports it, and the URL of each request in order.

### Pass conditions

Use one check per question, with ids `q1`, `q2`, and `q3`.

- `pass`. A supported answer was found within the budget. `evidence` gives the answer, the quote, and the URL that held it.
- `fail`. The site was readable, the budget ran out or the path dead-ended, and no supported answer was found. `evidence` names the last URL and why it stopped (no link, both views were an application shell, search form only, and so on).
- `not-observable`. The question has no checkable answer, or the client could not see what was needed.

Verdict `present` when every question passes. Verdict `partial` when at least one passes and at least one fails. Verdict `absent` when every scored question fails. Verdict `blocked` when every question stopped at an access wall. Verdict `not-observable` when no questions were supplied or published.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `competency-questions.md` — whether the site publishes a question list
- `llms-txt.md`, `sitemap.md`, `metadata-api.md` — the features a path used, scored on their own

The other files in `prompts/evals/` are separate evaluations. Do not draft new questions, and do not judge whether the site's answer is scientifically correct. Score only whether an agent could find a supported answer.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: no questions were available. Name where you looked.

```yaml
evaluation: competency-answerability
target: <origin>
sampled_record: null
verdict: present | partial | absent | blocked | not-observable
evaluated_at: <ISO 8601 date and time>
client: <tool or library, and the User-Agent sent>
questions_source: user | site:<url>
checks:
  - id: q1
    question: <text as written>
    result: pass | fail | not-observable
    answer: <answer or null>
    path: [<url>, <url>]
    evidence: <supporting quote and the URL that held it, or why it stopped>
fetches:
  - url: <url>
    method: GET | HEAD
    status: <code, or the error>
summary: <a few sentences, naming which readiness features helped or were missing>
gaps: []
```

Repeat the `q1` entry for `q2` and `q3`. `gaps` lists missing features, one sentence each, such as "No sitemap, so record pages were not reachable from the homepage". Begin by confirming the origin URL and the question list, then run the procedure.
