# Repository checklist

An editable companion to the 6 November 2026 NIAID Blueprint webinar
[*Making Your Repository More Accessible to SI*](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf).

Doug (and anyone reviewing feedback) should edit **[checklist.md](checklist.md)** only. That Markdown file is the sole content authority. HTML and PDF files under `dist/` are generated views.

This is a practical checklist, not a certification, maturity ladder, or compliance score. Higher level numbers mean more specialized access or software work, not a more trustworthy repository.

## Contents

| File | Role |
| --- | --- |
| [checklist.md](checklist.md) | Source you edit: items, levels, verification steps, and citations |
| [build.py](build.py) | Renderer and validator |
| [style.css](style.css) | Shared screen and print styles |
| [requirements.txt](requirements.txt) | Python packages for the renderer |
| [tests/test_checklist.py](tests/test_checklist.py) | Parser, filter, link, and wording checks |
| `dist/checklist.pdf` | Printable complete checklist |
| `dist/checklist-level-1.pdf` | Level 1 items only |
| `dist/checklist-through-level-2.pdf` | Levels 1 and 2 |
| `dist/*.html` | Browser-readable copies of the same views |

## Capability levels

Levels describe **how an action is usually carried out**:

1. Publish or update a file the site already serves. Placing that file can still require an administrator, and a CDN can override it.
2. Configure the publishing platform (headers, templates, CDN or WAF rules, landing-page markup).
3. Write or run software (an API or MCP server, or specialized tooling). SHACL validation can be run locally or in CI without hosting a public service.

Optional and emerging items (`llms.txt`, IETF AIPREF drafts, RSL, TDMRep, ARD, Agent Plugins, MCP, SPARQL RL, and similar) are labeled. Skipping them is not a failure. MCP is not required in order to apply the webinar.

## Printable PDF, fillable Markdown, and browser HTML

The same source is rendered three ways on purpose:

- **Markdown (`checklist.md`)** is what you modify in git. Copy it if you want working checkboxes or status notes in your own tracker. Keeping the committed copy unchecked keeps review diffs about content, not personal progress.
- **HTML (`dist/*.html`)** is the version for a browser (the user agent): text reflows, links work, and a screen reader can move through headings and item titles.
- **PDF (`dist/*.pdf`)** is the printable handout. Empty squares are for pen-and-paper marks. These files are **not** interactive AcroForm fill-in PDFs, because a fillable form would be a second document to maintain and is harder to regenerate cleanly from Markdown.

Do not fork Level 1 and Level 2 into separate Markdown files. Ask the renderer for a filtered view instead.

## Why this renderer

Quarto or hand-written LaTeX can produce polished PDFs, but they add a heavy toolchain and make the editable source less obvious. This folder uses **Python-Markdown plus WeasyPrint**:

- The source stays ordinary Markdown with a small, visible metadata list on each item.
- One parser builds every view, so level-specific handouts cannot drift from the full list.
- There is no TeX install. WeasyPrint needs the usual system libraries (cairo and pango) plus the pins in `requirements.txt`.
- HTML and PDF share `style.css`, so print and screen stay aligned.

## Rebuild

From this directory, after the Python packages and WeasyPrint system libraries are available:

```bash
python3 build.py --check
python3 build.py                  # HTML + PDF for all views
python3 build.py --view level-1
python3 build.py --view through-2
python3 build.py --view all --html-only
```

From the repository root:

```bash
python3 docs/checklist/build.py
uv run --no-project --with pytest --with markdown --with weasyprint \
  python -m pytest docs/checklist/tests/test_checklist.py
```

`build.py --check` parses the source, requires each item to have the standard fields plus “Do this” and “How to verify,” and checks that relative links resolve.

## Source hierarchy

When the exported slide PDF disagrees with a handout, the checklist follows the handouts:

1. [Webinar README](../Webinar_Nov_2026/README.md)
2. [Glossary](../Webinar_Nov_2026/glossary.md)
3. [Bibliography](../Webinar_Nov_2026/bibliography.md)
4. [TDM reservations](../Webinar_Nov_2026/supplementalInformation/tdm.md)
5. Other supplemental notes and examples
6. [slideDeckSIReadyRepos.pdf](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf) (42-page export; face text still has a few known errors)

Page numbers below refer to that PDF export on `master` (`f0a7198`, “deck update”).

| ID | Facet | Level | PDF | Preferred handouts / notes |
| --- | --- | ---: | ---: | --- |
| RCH-01 | Reachable | 2 | 10 | Glossary (CDN, rate limiting); agent-identification handout |
| RCH-02 | Reachable | 1 | 11 | Glossary (`robots.txt`); RFC 9309; example file |
| RCH-03 | Reachable | 1 | 12 | Glossary visitor classes; Google-Extended = Gemini training *and* grounding, Search ranking unaffected |
| RCH-04 | Reachable | 2 | 10 | Rate limit is HTTP, not a robots.txt rule |
| RCH-05 | Reachable | 2 | 12–13 | Agent-identification limits |
| RCH-06 | Reachable | 1 | 11 | AIPREF labeled Internet-Draft, vocab **-08** / attach **-05**; distinct from Cloudflare Content Signals |
| RCH-07 | Reachable | 1 | 11 | RSL `License:` value must be an absolute URL |
| RD-01 | Readable | 1 | 14 | Sitemap lines are not User-agent-scoped |
| RD-02 | Readable | 2 | 17 | Server-rendered text |
| RD-03 | Readable | 2 | 15, 17 | Markdown is a convenience, not “the” preferred format |
| RD-04 | Readable | 2 | 16 | FAIR Signposting |
| RD-05 | Readable | 1 | 15 | Optional `llms.txt` (v2); not a baseline |
| RD-06 | Readable | 1 | 18 | Optional `SKILL.md` |
| RD-07 | Readable | 1 | 19 | Optional / bleeding-edge `ard.json` |
| RD-08 | Readable | 3 | 20 | Optional / bleeding-edge Agent Plugins |
| CAL-01 | Callable | 3 | 21 | Documented metadata API; Blueprint-aligned |
| CAL-02 | Callable | 3 | 21 | Web architecture for **metadata** |
| CAL-03 | Callable | 2 | 21 | JSON-LD on records |
| CAL-04 | Callable | 3 | 22–25 | MCP optional; not an SI-readiness plan by itself |
| CAL-05 | Callable | 3 | 26 | Protected HTTP MCP; authorization optional; scopes illustrative |
| MEA-01 | Meaningful | 2 | 28 | PIDs |
| MEA-02 | Meaningful | 1 | 29 | Data dictionary / vocabulary; not an ontology ladder |
| MEA-03 | Meaningful | 2 | 30 | Profiles + `conformsTo`; DataCite is not primarily schema.org |
| MEA-04 | Meaningful | 2 | 31 | License metadata; not “all NIAID data are public domain” |
| MEA-05 | Meaningful | 2 | 32 | Citation, CRediT, contributor PIDs |
| MEA-06 | Meaningful | 2 | 33 | PROV-O / DataCite version relations |
| MEA-07 | Meaningful | 1 | 31 | Optional TDMRep (CG report; rights signal, not a block) |
| MEA-08 | Meaningful | 3 | 34 | SHACL Rec; local validation is enough |
| MEA-09 | Meaningful | 3 | 34 | Optional SPARQL RL Working Draft; cite https://www.w3.org/TR/sparql-rl/ |
| MEA-10 | Meaningful | 1 | 34 | Optional SSSOM/**TSV**; `author_id` and `confidence` optional |
| EVL-01 | Evaluation | 1 | 36 | Try an agent; `prompts/evals` |
| EVL-02 | Evaluation | 1 | 36 | Access vs answerability vs accuracy; no single score |
| EVL-03 | Evaluation | 1 | 36 | Optional NDE / Lighthouse diagnostics |

## Known source mismatches (intentionally not copied)

These remain on the PDF face or in an example comment. The checklist uses the corrected handout wording instead:

- `License: /rsl.xml` should be an absolute URL.
- `Sitemap:` lines are not User-agent-specific.
- “Blocking does not affect AI search visibility” is too broad for Google-Extended (Search is unaffected; Gemini grounding is affected).
- `Content-Usage` is an IETF Internet-Draft (`draft-ietf-aipref-vocab-08`).
- SPARQL RL should be cited at https://www.w3.org/TR/sparql-rl/ without copying the slide’s older date.
- SSSOM prose on the slide still implies author and confidence are always present.
- MCP authorization may still involve initial user consent.
- `docs/Webinar_Nov_2026/assets/robots.txt` comments still mention AIPREF vocabulary **-07** in places. The checklist points at **-08**. Updating that example comment is left as a follow-up so this folder can stay reviewable on its own.

## What this folder does not do

- It does not edit the canonical Google Slides deck or the webinar PDF.
- It does not score repositories or claim Blueprint conformance.
- It is not legal advice about licenses, TDM exceptions, or NIH data-use notices.
