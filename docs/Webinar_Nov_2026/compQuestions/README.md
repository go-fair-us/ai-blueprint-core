# Competency questions for NIAID repositories

Worked examples for the evaluation prompts. Answers were checked with public HTTP calls on 2026-10-30. No credentials were used.

Six repositories, 25 questions. Each question has one checkable answer (a count, a name, an identifier, or yes or no).

The procedure lives in the eval prompts:

- [`competency-questions.md`](../../../prompts/evals/competency-questions.md) checks that a site publishes its own question list. It quotes questions the site wrote.
- [`competency-answerability.md`](../../../prompts/evals/competency-answerability.md) answers up to three questions from the public site and returns one YAML report. An answer counts when the report quotes text or a field fetched in that run.

The webinar handout for both prompts is [Evaluation prompts](../supplementalInformation/evaluationPrompts.md#evaluation). In the Pi harness the same files are `/competency-questions` and `/competency-answerability`. Run these examples with those prompts. There is no separate skill.

## The two files

| File | What it is |
|---|---|
| [`competency_questions.md`](competency_questions.md) | The full test set. Each question has an expected answer, a check rule, the public calls that supported it, and template tags. |
| [`answerability_runs.md`](answerability_runs.md) | The same questions grouped into runs of at most three. Each run is a YAML block to paste. The answer-key table sits under the block. |

Keep the answer key with the grader. Paste only the fenced YAML into the chat the agent sees.

Every question is tagged `competency-answerability`. Later tags name the readiness feature that path used (`metadata-api`, `openapi-discovery`, `persistent-identifiers`, `vocabulary`, `api-http-behavior`, `provenance-lineage`, `server-rendered-content`, `sssom-mappings`, `rights-and-license`). To score that feature on its own, run the matching file in [`prompts/evals/`](../../../prompts/evals/).

## How to run one test

1. Open a fresh chat, or start Pi from the repo root with `./bin/pi`.
2. Paste [`competency-answerability.md`](../../../prompts/evals/competency-answerability.md).
3. Under it, paste one fenced YAML block from [`answerability_runs.md`](answerability_runs.md). Leave the answer-key table out.
4. When the report comes back, compare `checks[].answer` with the key. Use the Check column (exact, contains, or a numeric tolerance).

The prompt stays on the repository host and an obvious API or docs subdomain. It allows at most 5 requests per question and 15 in total. Send no credentials.

In Pi, `/competency-answerability` takes the origin as the first argument and the questions as the second. When the questions span more than one line, paste the YAML block.

## When the site publishes its own list

Use [`competency-questions.md`](../../../prompts/evals/competency-questions.md) to see whether the site published a list, and save the questions the report quotes. Feed up to three of those quotes into the answerability prompt.

The files in this directory are an external test set for these NIAID sites. They stand in when you want a known test, including on a site that has not published a list.

## Which run to pick

| Repository | Origin | Run A | Run B |
|---|---|---|---|
| AccessClinicalData@NIAID | https://accessclinicaldata.niaid.nih.gov/ | ACD-1, ACD-2, ACD-3 | ACD-5 |
| TB Portals | https://tbportals.niaid.nih.gov/ | TB-1, TB-2, TB-3 | |
| IEDB | https://www.iedb.org/ | IEDB-1, IEDB-2, IEDB-3 | IEDB-4 |
| ImmPort | https://www.immport.org/ | IMMPORT-1, IMMPORT-2, IMMPORT-3 | IMMPORT-4 |
| BV-BRC | https://www.bv-brc.org/ | BVBRC-1, BVBRC-2, BVBRC-4 | BVBRC-3 |
| VEuPathDB (PlasmoDB) | https://plasmodb.org/ | VEU-1, VEU-3, VEU-4 | VEU-2 |

Run B holds the question that did not fit in the three-question cap, or a count or version that changes. Question ids match the headings in [`competency_questions.md`](competency_questions.md).

Two questions need a second repository host: ACD-4 (AccessClinicalData@NIAID and ImmPort) and TB-4 (TB Portals and AccessClinicalData@NIAID). They are at the bottom of [`answerability_runs.md`](answerability_runs.md). A strict answerability run stays on one host, so those two fail by design. Use them only for an extended multi-host test.

## Volatile rows and dead ends

Re-check these before you grade. The recorded values are from 2026-10-30 and will drift:

- ACD-5, published-study count
- TB-3, homepage case, country, and site counts
- IEDB-4, NG Tools software release
- VEU-2, PlasmoDB build number and release date

[Endpoints that failed or required auth](competency_questions.md#endpoints-that-failed-or-required-auth) records paths that returned an application shell, HTTP 401, or HTTP 404 on that day.
