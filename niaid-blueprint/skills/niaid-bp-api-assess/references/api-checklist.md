# API checklist

Rubric for `scripts/analyze_api.py` and the gap report. Check ids and priorities below are the ones the script emits. Blueprint priorities match Phase 4 of `niaid-bp-fair-assess/references/gap-patterns.md`.

Authoritative wording is the Blueprint, fetched at skill start. Do not copy it into this skill.

- Blueprint: `https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md` — Section 3 (lines 176–203) and the Supplemental Table 7 note (line 434).
- Claim list: `okf/bundles/niaid_blueprint/api-specification/requirements.md`, atomics 132–136 (JSON-LD, resource IRIs, HTTP GET, OpenAPI/Swagger).

Section 3 is about exposing metadata to machines. It is not a general API style guide. Practice checks are a second axis and are never Blueprint failures.

`not_stated` means the document did not say. Do not report `not_stated` as a failure. A passing sample does not flip a failed `bp_jsonld_declared` into a pass; report both.

## Finding the document

A documentation page is not a dead end when its only obvious link is a Swagger UI. The script searches in this order and stops when a document parses as Swagger 2 or OpenAPI 3:

1. A linked spec (`.json` / `.yaml` / `.yml`, or an extensionless `/api-docs` or `/openapi` path). A Swagger UI link does not count as the spec.
2. A springdoc config (`swagger-config`, or `configUrl`), then its `url` or `urls` field.
3. A Swagger UI, ReDoc, or RapiDoc page, then `swagger-initializer.js` referenced from that page. Read `url`, `urls`, and `configUrl` there.

The petstore URL shipped in stock Swagger UI (`petstore.swagger.io`) is ignored while any other candidate remains. `hop.via` in the findings lists each document that was opened. Do not stop the review at the UI page.

## Blueprint axis

| Id | Pass when | Failure priority |
|----|-----------|------------------|
| `bp_openapi_doc` | A Swagger 2.0 or OpenAPI 3.x document parsed | Medium |
| `bp_jsonld_declared` | A response offers `application/ld+json`, or a schema or example declares `@context` | High |
| `bp_jsonld_observed` | An unauthenticated sample returned JSON with `@context` | High |
| `bp_resource_iris` | Paths are resource IRIs. Verb-like segments (`getDataset`, `search`) and item lookups whose id lives only in a required query parameter fail | Medium |
| `bp_get_retrieval` | Retrieval uses GET. A retrieval-shaped POST fails only when it documents no request body. POST with a body is allowed (atomic 135) | Medium |
| `bp_version_in_path` | No `/v1/`-style segment in the path or server URL. A version segment is unstable as a JSON-LD `@id` | Medium |

When no API document parses, `bp_openapi_doc` fails and the other blueprint checks stay `not_stated` unless the page itself states the fact (a JSON-LD mention, a verb-like path, a version segment).

GraphQL, SPARQL, and FHIR are named in `outside_rubric` when the text says so. They do not receive a score on this rubric. Say that the minimum objectives are resource IRIs, GET, JSON-LD, and OpenAPI.

HTML-embedded JSON-LD and a downloadable metadata index are Blueprint fallbacks (atomic 122). This skill does not crawl a site to prove them. The report lists them under "Not checked." A single landing page can be handed to `niaid-bp-metadata-extract`.

Table 1 coverage is not a check. `observed_property_names` lists names that appeared in schemas, examples, or sample bodies. Mention a Table 1 field only when it is in that list.

## Practice axis

No Blueprint priority. `prac_pagination` is `not_applicable` when the document has no collection GET.

| Id | Pass when |
|----|-----------|
| `prac_info_contact` | `info.contact` has a name, email, or url |
| `prac_info_license` | `info.license` has a name or url |
| `prac_operation_summaries` | Every operation has a summary or description |
| `prac_operation_ids` | Every operation has an `operationId` |
| `prac_response_examples` | Every operation with a 2xx response includes an example |
| `prac_error_responses` | Every operation documents a 4xx or 5xx response |
| `prac_pagination` | Every collection GET documents `limit`, `offset`, `page`, `cursor`, or the same class of parameter. Item GETs are ignored |
| `prac_local_refs` | Every `$ref` is a local JSON pointer. Remote refs are listed in `unresolved_refs` and are not fetched |

## Samples

`sample_plan` lists unauthenticated GETs whose path parameters have an example or default. The script does not invent ids, send credentials, or follow a redirect onto another host. `--no-sample` fills the plan and does not call those URLs.

Docs-only pages are sampled only when the page itself contains an absolute example GET URL with no credentials.

## Confidence

| Value | When |
|-------|------|
| `high` | A spec parsed, response encodings are present, and any samples that were attempted did not all fail |
| `medium` | A spec parsed, but response schemas/media types are absent, or every sample errored or returned HTTP 400+ |
| `low` | No OpenAPI or Swagger document was parsed |
