# API alignment report

Fill this from `findings.json`. Check ids, statuses, and priorities are defined in `references/api-checklist.md`. Copy evidence from the findings. Do not add endpoints, media types, or sample results that are not in the file.

---

## Input

- **Source:**
- **Kind:** openapi / docs / unreachable
- **Spec format:**
- **Hop:** none, or the docs page and the spec it linked
- **Confidence:** high / medium / low
- **Outside this rubric:** none, or GraphQL / SPARQL / FHIR as named in `outside_rubric`

---

## Blueprint alignment

One subsection per blueprint check whose status is `fail`. Then one line listing checks that passed, and one line listing checks that are `not_stated`.

### [check id] — [priority]

- **Evidence:** method, path, media type, or sample URL from the finding
- **Recommended next step:** one concrete change

---

## Common practice

These are not Blueprint failures.

### [check id]

- **Evidence:**
- **Recommended next step:**

Passed practice checks, in one line:

---

## Samples

| URL | Status | Content type | JSON-LD `@context` |
|-----|--------|--------------|--------------------|
| | | | |

State when `sample_plan` was not called (`--no-sample`) or was empty.

---

## Not checked

- HTML pages with embedded JSON-LD, and a downloadable metadata index. Both are Blueprint fallbacks. This run did not crawl the site for them.
- Authenticated operations. No API key was sent.
- Table 1 fields that are absent from `observed_property_names`. Fields that did appear:

---

## Overall

Two or three sentences: Blueprint alignment, the single highest-priority gap, and whether the practice lint changes what to do first.
