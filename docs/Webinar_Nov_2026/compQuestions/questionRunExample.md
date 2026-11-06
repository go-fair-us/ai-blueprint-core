# Question run example: AccessClinicalData@NIAID

Worked output of [`competency-answerability.md`](../../../prompts/evals/competency-answerability.md) on AccessClinicalData Run A from [`answerability_runs.md`](answerability_runs.md).

Run date: 2026-11-06. No credentials. The agent stayed on `accessclinicaldata.niaid.nih.gov`. It did not use the answer key while answering.

## Inputs

```yaml
origin: https://accessclinicaldata.niaid.nih.gov/
questions:
  - "What ClinicalTrials.gov NCT number is registered for the AccessClinicalData@NIAID study PALM007 (Tecovirimat for Treatment of Monkeypox Virus)?"
  - "Which AccessClinicalData@NIAID study identifier (cmc_unique_id) corresponds to ClinicalTrials.gov trial NCT04640168, and what is its title?"
  - "What condition does the PALM007 study in AccessClinicalData@NIAID address, and on what date did its study start?"
```

`questions_source` is `user`.

## Client

Raw requests used `curl` with User-Agent `competency-answerability/1.0`. That client returns the status code, response headers, and the unmodified body.

Every HTML route returned the same 498-byte application shell (`<div id="root"></div>`). Those shells were rendered once each with `chromium --headless --dump-dom`. A rendered hop records the DOM, not response headers. Script bundles were not fetched as separate agent requests.

Budget used: 11 requests (cap 15). Question paths used 4, 6, and 4 requests (cap 5). The sixth request on question 2 was the study-page render, past that question's cap. It still did not contain `cmc_unique_id`.

## Report

```yaml
evaluation: competency-answerability
target: https://accessclinicaldata.niaid.nih.gov/
sampled_record: https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials
verdict: partial
evaluated_at: 2026-11-06T14:59:10Z
client: curl (User-Agent competency-answerability/1.0; status, headers, and unmodified body) and chromium --headless --dump-dom for one render of a shell URL (rendered DOM only; response headers not recorded)
questions_source: user
checks:
  - id: q1
    question: "What ClinicalTrials.gov NCT number is registered for the AccessClinicalData@NIAID study PALM007 (Tecovirimat for Treatment of Monkeypox Virus)?"
    result: pass
    answer: NCT05559099
    path:
      - https://accessclinicaldata.niaid.nih.gov/
      - rendered:https://accessclinicaldata.niaid.nih.gov/
      - https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials
      - rendered:https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials
    evidence: "Rendered study list card class listing-PALM007, title Tecovirimat for Treatment of Monkeypox Virus, links to /study-viewer/clinical_trials/PALM007. Quote: NCT Number NCT05559099. URL: https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials"
  - id: q2
    question: "Which AccessClinicalData@NIAID study identifier (cmc_unique_id) corresponds to ClinicalTrials.gov trial NCT04640168, and what is its title?"
    result: fail
    answer: null
    path:
      - https://accessclinicaldata.niaid.nih.gov/
      - rendered:https://accessclinicaldata.niaid.nih.gov/
      - https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials
      - rendered:https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials
      - https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials/NCT04640168
      - rendered:https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials/NCT04640168
    evidence: "Title is on the list and the study page: (Released May 2022) Adaptive COVID-19 Treatment Trial 4 (ACTT-4), with NCT Number NCT04640168. The string cmc_unique_id is not in either rendered view. The public slug is NCT04640168, which is not labeled as cmc_unique_id, so that half of the question is unsupported. The study-page render was the 6th request on this path, past the 5-request cap; it still did not show the field."
  - id: q3
    question: "What condition does the PALM007 study in AccessClinicalData@NIAID address, and on what date did its study start?"
    result: pass
    answer: "Condition Monkeypox; study start October, 2022"
    path:
      - https://accessclinicaldata.niaid.nih.gov/
      - rendered:https://accessclinicaldata.niaid.nih.gov/
      - https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials
      - rendered:https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials
    evidence: "Same listing-PALM007 card. Quotes: Condition Monkeypox; Study Start Date October, 2022. The site gives month and year, not a calendar day. URL: https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials"
fetches:
  - url: https://accessclinicaldata.niaid.nih.gov/
    method: GET
    status: 200
  - url: https://accessclinicaldata.niaid.nih.gov/llms.txt
    method: GET
    status: 200
  - url: https://accessclinicaldata.niaid.nih.gov/robots.txt
    method: GET
    status: 200
  - url: https://accessclinicaldata.niaid.nih.gov/sitemap.xml
    method: GET
    status: 200
  - url: https://accessclinicaldata.niaid.nih.gov/sitemap_index.xml
    method: GET
    status: 200
  - url: https://accessclinicaldata.niaid.nih.gov/env-config.js
    method: GET
    status: 200
  - url: rendered:https://accessclinicaldata.niaid.nih.gov/
    method: GET
    status: 200
  - url: https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials
    method: GET
    status: 200
  - url: rendered:https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials
    method: GET
    status: 200
  - url: https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials/NCT04640168
    method: GET
    status: 200
  - url: rendered:https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials/NCT04640168
    method: GET
    status: 200
summary: "Two of three questions were answered from the rendered clinical-trials list. The homepage linked to /study-viewer/clinical_trials; raw HTML for every route was the same 498-byte application shell. Rendering that list exposed the PALM007 card (NCT05559099, Monkeypox, October 2022) and the NCT04640168 card (ACTT-4). No llms.txt, sitemap, JSON-LD, or documented metadata API was available. The requested cmc_unique_id was not in the public rendered text."
gaps:
  - "No llms.txt: /llms.txt returned the SPA shell, so it did not guide the path."
  - "No sitemap: /sitemap.xml and /sitemap_index.xml returned the SPA shell, so record URLs were found only after rendering the homepage."
  - "No robots.txt: /robots.txt returned the SPA shell."
  - "Record and list pages are client-rendered; a raw GET cannot see titles, NCT numbers, conditions, or dates."
  - "cmc_unique_id is not published on the public study list or the NCT04640168 study page."
  - "No JSON-LD and no documented public metadata API were linked from the pages fetched."
```

## What the path used

The homepage render linked to `/study-viewer/clinical_trials`. That list, after one render, held the PALM007 card (`listing-PALM007`) and the NCT04640168 card. `env-config.js` named a Power Apps portal URL and `VITE_ENVIRONMENT: prod`. It did not name a metadata API.

`/llms.txt`, `/robots.txt`, `/sitemap.xml`, and `/sitemap_index.xml` each returned the shell (HTTP 200, `content-type: text/html`, 498 bytes). They did not help.

## Against the answer key

The key in [`answerability_runs.md`](answerability_runs.md) was not shown to the agent. It expects `GET /api/studies/PALM007` and `GET /api/studies/published`. This run never discovered those URLs from a link, a sitemap, or `llms.txt`, so it did not call them.

| ID | Key | This run | Match |
|---|---|---|---|
| ACD-1 | NCT05559099 | NCT05559099 | exact |
| ACD-2 | identifier NCT04640168; title contains ACTT-4 | title found; `cmc_unique_id` not in the rendered text | fail |
| ACD-3 | Monkeypox; `2022-10-10` | Monkeypox; October, 2022 | condition only; the day is not on the rendered card |
