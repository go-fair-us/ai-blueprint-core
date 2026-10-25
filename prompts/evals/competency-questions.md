# Competency questions

**Question:** Does the site publish competency questions that an agent could use as tests of this repository?

Slide theme: Be meaningful, and the evaluation slide, from "Making Your Repository More Accessible to AI" (NIAID Blueprint Webinar Series, 6 November 2026). Competency questions are a published list of questions the resource is meant to answer. The slides also mention running your own questions against an agent. This prompt checks that a list is published. It does not run the questions.

## Role

You evaluate one property of a public data-repository website: a public list of questions about this repository's data. Quote questions the site wrote. Do not draft questions the site should have written.

A page that only contains the phrase "competency questions", with no questions under it, fails the list check.

## Inputs

- Repository origin URL (required).
- Record URL (optional). Use it when the record page links the question list.

## Fetch budget

Stay on the repository host and an obvious API or docs subdomain. Send no credentials. Invent no questions. Do not load-test. Do not execute a question against an API.

Caps for this pass: the homepage, `robots.txt`, one `llms.txt`, at most 3 sitemap files and 50 URLs scanned, one record page, one metadata GET, and one OpenAPI document. This prompt reads the homepage, one `llms.txt`, and one docs or about page. Prefer the raw HTTP body.

A challenge, HTTP 401, or HTTP 403 on that page is verdict `blocked`.

## Checks

### Procedure

1. GET the homepage and `{origin}/llms.txt`.
2. Follow one link named competency questions, evaluation questions, "questions this resource answers", or a similar label.
3. Quote up to three questions from the raw body. Note whether they name this repository's entities (studies, assays, subjects, pathogens, and so on).

### Pass conditions

- `questions-page`. Pass when a fetched page is presented as the repository's question list or evaluation set.
- `question-list`. Pass when that page contains at least three concrete questions, or a shorter list when the page clearly ends there. Fail when the heading exists and the body has no questions.
- `about-this-resource`. Pass when the questions refer to this repository's data or entities. Fail when the only list is a generic copy with no tie to the site.

Verdict `present` when all three pass. Verdict `partial` when a page of questions exists and `about-this-resource` fails, or the page has fewer questions than a real list (a heading and one fragment). Verdict `absent` when the homepage, `llms.txt`, and the one follow-up page contain no such list. Verdict `not-observable` when those bodies are application shells and no link could be read. Verdict `blocked` when the questions page is behind an access wall.

## Out of scope

Score only this question. Neighboring prompts own the rest:

- `shacl-shapes.md` — published SHACL
- `vocabulary.md` — glossary and ontology links
- `metadata-api.md` — calling a metadata endpoint

The other files in `prompts/evals/` are separate evaluations. Do not invent a test suite, and do not run one.

## Report

Return one YAML document. `verdict` is one of `present`, `partial`, `absent`, `blocked`, or `not-observable`.

- `present`: every check this prompt requires for a pass is `pass`.
- `partial`: the site was readable, and the checks are mixed.
- `absent`: the artifact or behavior is missing.
- `blocked`: the response was a challenge, HTTP 401 or 403, or an access wall.
- `not-observable`: the pages could not be read far enough. Name what you tried.

```yaml
evaluation: competency-questions
target: <origin>
sampled_record: <url or null>
verdict: present | partial | absent | blocked | not-observable
checks:
  - id: questions-page
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: question-list
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
  - id: about-this-resource
    result: pass | fail | not-observable
    evidence: <url, status, header, or a short quote>
summary: <a few sentences>
gaps: []
```

`gaps` lists missing observables, one sentence each. The quotes in `evidence` are the site's questions. Begin by confirming the origin URL, then run the procedure.
