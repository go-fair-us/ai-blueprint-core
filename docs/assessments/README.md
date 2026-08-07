# FAIR assessment prompts and example reports

This directory holds **example assessment reports** produced by LLM agents that
follow the prompt personas in [`prompts/`](../../prompts/). The prompts encode
how an assessor should behave; the files here show what a finished report can
look like for a real public resource (ImmPort study SDY2968).

The authoritative requirements come from the
[NIAID Blueprint for Digital Objects](../BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md)
(five areas: metadata schema, persistent identifiers, APIs, citation, and
outreach/training). The same domain logic also exists as the Claude Code skill
[`niaid-bp-fair-assess`](../../skills/niaid-bp-fair-assess/) and as MCP prompt
tools under [`mcp_bp`](../../mcp_bp/).

---

## Using prompts this way

Most chat usage is **user-led**: you ask a question, the model answers. The
prompts in this project reverse that pattern. You paste (or load) a long system
persona, and the model takes the lead. That pattern is sometimes called
**flipped interaction**: the prompt defines role, procedure, success criteria,
and output shape; the human supplies facts (or a URL) and the model drives the
session until it can emit a structured artifact.

Why encode assessment as a prompt rather than only as code?

1. **Domain logic is procedural prose.** FAIR/Blueprint checks need judgment
   (what counts as “partial,” which evidence quote matters, what to recommend
   next). A prompt can state that judgment explicitly without hard-coding every
   edge case.
2. **Model-agnostic packaging.** The same Markdown file works in Claude Code,
   OpenCode, ChatGPT, local tools, or an MCP `prompts://` endpoint. You do not
   need a compiled agent binary to run an assessment.
3. **Two complementary evidence sources.** Some assessments interview a human
   who knows the repository; others crawl a public landing page. Both can map
   findings to the same Blueprint sections and produce a gap report.
4. **Reproducible procedure, variable score.** The steps and report sections
   stay stable across runs. Scores and depth still vary with model, tool access
   (JS rendering, multi-page crawl), and how much portal-level documentation
   the agent reads. The examples below illustrate that variance on one target.

**How to run a prompt**

| Mode | What you do |
|------|-------------|
| Chat / LLM UI | Paste the full contents of a `prompts/*.md` file as the system (or first) message, then provide a URL or answer interview questions. |
| Agent host (e.g. OpenCode) | Point the agent at the persona file or use the short invocation block in `fairAssessorAgentOpenCode.md`. |
| MCP (`mcp_bp`) | Invoke registered prompts such as `fair_assessment_interview` or `fair_crawl_assessor` with a URL argument. |
| Claude Code skill | Use `/niaid-bp-fair-assess` for the interview path with progressive loading of `references/`. |

If an interview runs too long, tell the model: *stop the interview and give me
the summary now*. For crawl runs, always require evidence quotes and a clear
statement of fetch method (direct HTML vs. JS-rendered proxy such as
`https://r.jina.ai/<URL>`).

---

## The three FAIR assessor prompts

These files live under [`prompts/`](../../prompts/). They are related but not
interchangeable.

### 1. `fairAssessmentInterview.md` — human interview → gap report

| | |
|--|--|
| **Interaction** | Conversational. The model asks one or two questions at a time. |
| **Evidence** | Answers from a repository manager, data steward, or PI (not web scrape). |
| **Structure** | Six phases: resource overview → metadata → PIDs → APIs → citation → outreach. |
| **Output** | *NIAID Blueprint Assessment Report*: resource summary; per-area current state, gaps, High/Medium/Low priority, one recommended next step; overall readiness (2–3 sentences). |
| **Parallel form** | Skill `niaid-bp-fair-assess`; MCP prompt `fair_assessment_interview`. |

**When to use:** You have a person who can speak for the repository, including
internal practices (submission workflows, planned APIs, unpublished policies)
that a public page may not show.

**When not to use:** You only have a URL and no stakeholder available. Prefer a
crawl prompt instead.

There is **no interview transcript example** in this directory yet. The skill’s
report template is in
[`skills/niaid-bp-fair-assess/assets/report-template.md`](../../skills/niaid-bp-fair-assess/assets/report-template.md).

---

### 2. `fairAssessorCrawl.md` — web crawl → evidence-based FAIR/Blueprint report

| | |
|--|--|
| **Interaction** | Non-conversational agent task: fetch pages, extract text, score. |
| **Evidence** | Starting URL + selective first-level links (docs, access, metadata, APIs, license). |
| **Blueprint default** | NIAID Blueprint raw GitHub URL if none is supplied. |
| **JS handling** | Prefer a JS-capable fetch; otherwise use `https://r.jina.ai/<URL>`. Report the method and any content that could not be retrieved. |
| **Output** | Overall alignment summary; per-principle meet / partially meet / fail with quotes; gaps and recommendations; overall score (numeric or qualitative); next steps. |

**When to use:** Public dataset or repository pages where you want an external,
reproducible snapshot of what is *visible* on the web.

**Limitations the prompt itself calls out:** login walls, scrape blocks, huge
sites (be selective), and empty SPA shells if JS is not rendered.

The example files in this directory are all **crawl-style** assessments of the
same ImmPort study landing page.

---

### 3. `fairAssessorAgentOpenCode.md` — packaged crawl invocation (OpenCode / agents)

This file is a **thin wrapper** around the crawl assessor pattern, not a third
independent methodology.

| Section | Role |
|---------|------|
| Top block | Short agent invocation (`@fair-assessor`) with a concrete starting URL and Blueprint URL, plus a hard rule for failed JS fetches. |
| “Full version for direct prompt use” | Standalone persona + the same ImmPort SDY2968 URL pre-filled. |

**Default target in the file:**  
`https://www.immport.org/shared/study/SDY2968/summary`

**Extra operational rule (stricter than the base crawl prompt):** if a fetch
returns only a header, navigation, or fewer than ~500 characters of body text,
treat it as a **failed** fetch and **immediately** re-fetch via
`https://r.jina.ai/<full-URL>` before drawing conclusions. Only report “unable
to retrieve content” if the jina fetch also fails.

**When to use:** Agent hosts that support named agents or `@` mentions, or when
you want a ready-to-paste one-shot with URL + Blueprint already filled. For a
generic crawl of another resource, prefer `fairAssessorCrawl.md` and substitute
the URL (or use MCP `fair_crawl_assessor` / `fair_web_assessor`).

`CLAUDE.md` notes a related OpenCode agent path
(`.opencode/agent/fair-resource-assessor.md`); that path may or may not be
present in a given checkout. The Markdown in `prompts/` remains the portable
source of truth.

---

## Prompt comparison at a glance

| | Interview | Crawl (`fairAssessorCrawl`) | Agent OpenCode wrapper |
|--|-----------|-----------------------------|-------------------------|
| Primary input | Human answers | Starting URL (+ Blueprint) | URL pre-filled (example: ImmPort SDY2968) |
| Blueprint framing | Five Blueprint areas (phases 2–6) | FAIR principles + Blueprint criteria | Same as crawl |
| Machine access needed | Chat only | Web fetch / JS render | Same + jina mandatory retry |
| Typical product | Prioritized gap report by Blueprint area | Scored FAIR + recommendations with evidence quotes | Same as crawl |
| Example outputs here | — | Yes (all three files below) | Same family as crawl examples |

---

## Example outputs (ImmPort SDY2968)

All three files assess the **same public study**:

- **Landing page:** https://www.immport.org/shared/study/SDY2968/summary  
- **Title:** *COVID-19 vaccination perspectives among patients with Long COVID: A qualitative study*  
- **DOI:** `10.21430/M3J8UMVGT6`  
- **Blueprint:** NIAID Blueprint v2 (26 Sep 2025)

They illustrate crawl-based assessment under different depth, model, and crawl
breadth. Scores are **not** ground truth; they are point-in-time model judgments
from fetched text.

### File index

| File | Approx. length | Overall score | Character of the report |
|------|----------------|---------------|-------------------------|
| [`SDY2968_FAIR_assessment.md`](./SDY2968_FAIR_assessment.md) | Short (~90 lines) | **52/100** | Landing-page focused; Table 1 element map; compact F/A/I/R scores |
| [`immport-sdy2968-fair-assessment_gmt52.md`](./immport-sdy2968-fair-assessment_gmt52.md) | Medium (~180 lines) | **65/100** | Multi-page crawl (study + docs.immport.org); portal-level API/citation/contact credit |
| [`immport-sdy2968-fair-assessment_full_glm52_nrp.md`](./immport-sdy2968-fair-assessment_full_glm52_nrp.md) | Long (~500+ lines) | **58/100** | Full methodology, per-subcriterion FAIR, five Blueprint sections scored, timed next steps |

Filenames that include model tags (e.g. `gmt52`, `glm52_nrp`) mark different
runs or backends. Use them for comparison, not as an official ranking of
ImmPort.

### Shared findings (stable across runs)

Despite different scores, the three reports **agree on the main picture**:

| Strengths (repeated) | Gaps (repeated) |
|----------------------|-----------------|
| Resolvable DOI / accession on the study page | No schema.org **JSON-LD** (or JSON-LD API option) at dataset level |
| Rich free-text title and description | No dataset-level **license** / SPDX on the summary page |
| Health condition, measurement technique, grant/program text | Missing **author ORCID** and **funder ROR** on the page |
| (Deeper crawls) Strong portal APIs: OpenAPI/Swagger, DRS, FHIR; helpdesk; citation page | Biomedical terms as free text, not **NCBITaxon / MONDO** IRIs on the landing page |
| | Weak or absent **dataset-level** “How to cite” block with standard formats |

That convergence is the practical value of the crawl prompt: independent runs
still surface the same Blueprint blockers (machine-readable metadata, license,
PIDs on the landing page).

### How the reports differ

#### 1. `SDY2968_FAIR_assessment.md` (score 52)

- Maps ImmPort fields to **Blueprint Table 1** in one table (present / partial / missing).
- Scores **FAIR sub-criteria** with short evidence quotes.
- Weighted FAIR totals: Findable 70, Accessible 45, Interoperable 35, Reusable 25.
- Recommendations stay at High / Medium / Low and stay close to the landing page
  (JSON-LD embed, license, distribution link, ORCIDs/RORs, ontology IRIs, cite block).
- **Does not** credit portal-wide API docs, ImmPort helpdesk, or `/home/cite/` as
  strongly as the longer crawls—so Interoperable/Accessible scores are lower.

This shape is closest to a **minimal successful crawl**: one primary page, Table 1
check, FAIR breakdown, prioritized actions.

#### 2. `immport-sdy2968-fair-assessment_gmt52.md` (score 65)

- Documents **fetch method and limitations** first (SPA shell → jina; partial
  download-page extraction).
- Pulls evidence from **study summary + ImmPort documentation** (API, download,
  ontologies, citation, user agreement).
- FAIR criteria marked meet / partially meet / fail, with portal vs. dataset
  distinctions (e.g. I2 “Meet” from ontology lookup tables; R1.1 partial from
  user agreement rather than SPDX on the study).
- Blueprint alignment section rates all five areas; **outreach/contact = Meet**
  via `ImmPort_Helpdesk@immport.org`.
- Ends with five prioritized recommendations (JSON-LD on landing pages, metadata
  endpoint, license/access fields, cite block, ontology IDs).

This shape matches **`fairAssessorCrawl.md` step 3–4** (follow important
first-level links) and the OpenCode jina-retry discipline.

#### 3. `immport-sdy2968-fair-assessment_full_glm52_nrp.md` (score 58)

- Full **methodology table** of pages fetched (including failures and truncated
  OpenAPI specs).
- Explicit **Blueprint requirements summary** table before scoring.
- Deep per-subcriterion FAIR writeups, then **Section 1–5 Blueprint tables**.
- Dual scoring: equal weights on five Blueprint sections → **58/100**, plus a
  separate FAIR principle table (F 65, A 70, I 50, R 45).
- Recommendations include sample JSON-LD fragments, example citation text, and a
  **time-phased roadmap** (0–3 months through 12+ months).
- States limitations clearly (no API key, Markdown proxy cannot prove absence of
  HTML `<script type="application/ld+json">`, etc.).

This is the **audit-style** extreme of the crawl prompt: still external and
evidence-based, but long enough to hand to a repository team as a working draft
of a formal assessment.

### Why overall scores differ (52 vs 58 vs 65)

| Factor | Effect on score |
|--------|-----------------|
| **Crawl breadth** | Narrow (landing page only) under-credits portal APIs, citation docs, and helpdesk → lower Accessible / Interoperable / Outreach. |
| **Scoring frame** | Pure F/A/I/R weighting vs. equal Blueprint-section weighting changes the overall number even when narrative gaps match. |
| **Strictness on license** | Landing-page-only “license missing → Fail” vs. partial credit for ImmPort user agreement. |
| **Model / run variance** | Same procedure, different synthesis of partial evidence. |

**Read scores as ordinal signals within one report, not as inter-lab precision
measurements.** Prefer the **shared gap list** when comparing runs.

### Relation to the interview prompt

None of the three example files is an interview product. An interview report
would:

- Attribute claims to a **named respondent role** (e.g. “repository engineer
  reports ORCID required at submission”), not only to page quotes.
- Organize primarily by **five Blueprint areas** with High/Medium/Low, not by
  F1–R1.3.
- Capture **internal or planned** work (roadmap items not yet on the public
  site).

A useful practice for a real repository is to **run both**: crawl first for an
external baseline (like these examples), then interview to fill gaps the web
cannot show and to validate priorities with staff.

---

## Suggested workflow

```text
1. Choose path
   ├─ Stakeholder available  → prompts/fairAssessmentInterview.md
   │                           (or skill niaid-bp-fair-assess)
   └─ Public URL only        → prompts/fairAssessorCrawl.md
                               (or fairAssessorAgentOpenCode.md / MCP crawl tools)

2. Fix inputs: resource URL or name; Blueprint URL if not the default NIAID v2.

3. For crawl: require JS-capable fetch or r.jina.ai; list pages fetched and limits.

4. Produce report; store under docs/assessments/ with a clear name, e.g.
   <resource>-fair-assessment_<model-or-date>.md

5. Optional: re-run after high-priority fixes; compare gap lists, not only scores.
```

---

## Adding new examples

When you add a report to this directory:

1. **Name** it so the resource and run are obvious (`resource-id`, optional model
   or date tag).
2. **State** method (interview vs. crawl), Blueprint version, date, and fetch
   tools.
3. **Quote** evidence; do not invent page content or API behavior.
4. **Separate** portal-level strengths from **dataset landing-page** gaps when
   both appear.
5. **Update** the file index table in this README.

---

## Related paths

| Path | Role |
|------|------|
| [`prompts/fairAssessmentInterview.md`](../../prompts/fairAssessmentInterview.md) | Interview persona |
| [`prompts/fairAssessorCrawl.md`](../../prompts/fairAssessorCrawl.md) | Crawl persona |
| [`prompts/fairAssessorAgentOpenCode.md`](../../prompts/fairAssessorAgentOpenCode.md) | Agent/OpenCode crawl invocation |
| [`skills/niaid-bp-fair-assess/`](../../skills/niaid-bp-fair-assess/) | Claude Code interview skill + report template |
| [`mcp_bp/`](../../mcp_bp/) | MCP tools and registered prompts |
| [`docs/BluePrint/…`](../BluePrint/) | Authoritative Blueprint Markdown |
| Project root [`README.md`](../../README.md) | Flipped-interaction overview for interview prompts |
