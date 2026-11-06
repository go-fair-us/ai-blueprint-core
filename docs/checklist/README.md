# Repository checklist

Companion to the 6 November 2026 NIAID Blueprint webinar
[*Making Your Repository More Accessible to SI*](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf)
and the other files in [`docs/Webinar_Nov_2026/`](../Webinar_Nov_2026/).

This folder is a **practical action list** for repository teams who heard
the webinar (or are reading the deck and handouts). It is **not** a
certification, audit rubric, maturity model, or compliance score.
Completing more items, or items with a higher level number, does not make
a repository more trustworthy, more FAIR, or more “SI-ready.”

The webinar is about assets a repository exposes to agents and workflows.
It does not judge whether any particular dataset should be used for
training or inference. Informational only; not legal advice.

## Files

| Path | Role |
| --- | --- |
| [`checklist.md`](checklist.md) | **Only content authority.** Edit this file. |
| [`build.py`](build.py) | Parses the Markdown and writes filtered HTML and PDF views. Includes PEP 723 pins for `uv run`. |
| [`style.css`](style.css) | Shared print and screen stylesheet. |
| [`requirements.txt`](requirements.txt) | Same renderer pins as the PEP 723 block (`markdown==3.11`, `weasyprint==70.0`), for a pip/venv install. |
| [`tests/test_checklist.py`](tests/test_checklist.py) | Structure, wording, link, and renderer checks. |
| [`dist/checklist.pdf`](dist/checklist.pdf) / [`.html`](dist/checklist.html) | Complete printable and browser views. |
| [`dist/checklist-level-1.pdf`](dist/checklist-level-1.pdf) / [`.html`](dist/checklist-level-1.html) | Level 1 items only. |
| [`dist/checklist-through-level-2.pdf`](dist/checklist-through-level-2.pdf) / [`.html`](dist/checklist-through-level-2.html) | Levels 1 and 2. |

Do not hand-edit files under `dist/`. Three generated views share the same source.

The complete PDF is a letter-size printout of the full source (about 18
pages in the current render). The Level 1 view is shorter if you only
need file-shaped actions on paper.

## Capability levels

Levels describe **what kind of access and maintenance an action
typically needs**. They are not a ranking of repositories and not a
maturity ladder.

1. **Publish or update served files** — for example `robots.txt`,
   `sitemap.xml`, `llms.txt`, a data dictionary, or a mapping table.
   You may still need an administrator, and a CDN or hosted platform
   can override the file you upload.
2. **Configure the publishing platform** — headers, HTML templates,
   landing-page markup, content negotiation, CDN or firewall rules,
   repository-platform settings.
3. **Write or run software** — implement or operate an API or MCP
   server, or run specialized tooling. SHACL validation can run
   **locally** or in CI; it does not require a public validation
   service unless you choose to offer one.

Optional items (including `llms.txt`, IETF AIPREF drafts, RSL, TDMRep,
ARD, Agent Plugins, MCP, SHACL validation, SPARQL RL, and SSSOM
mappings) are labeled in the source. Skipping them is not a failure.
SHACL is a W3C Recommendation; it is optional here because the webinar
treats deeper validation as caution / bleeding-edge work, not because
the language is experimental. MCP is not required in order to act on
the talk. Reachable and Readable work, plus a documented API if you
have one, already go a long way.

## Sources

The webinar itself is the **primary scope** of this checklist: the
6 November 2026 talk and the materials in
[`docs/Webinar_Nov_2026/`](../Webinar_Nov_2026/), especially
[`slideDeckSIReadyRepos.pdf`](../Webinar_Nov_2026/slideDeckSIReadyRepos.pdf).

Where that PDF face is known to be stale, the checklist follows the
corrected webinar handouts — the
[glossary](../Webinar_Nov_2026/glossary.md),
[bibliography](../Webinar_Nov_2026/bibliography.md), and
[`tdm.md`](../Webinar_Nov_2026/supplementalInformation/tdm.md) —
rather than copying the error. Those known mismatches are listed below.
The handouts are not a second, broader syllabus.

Page numbers refer to the 42-page PDF export currently on `master`
(`f0a7198`, “deck update”). In that file, PDF page *n* is slide *n*.

Each item cites the relevant slide and, where a definition or
correction lives in a handout, that file too. External specifications
are linked so a reader can verify the current text. Internet-Drafts,
Community Group reports, and Working Drafts are labeled as such.

## Why this renderer

`checklist.md` is meant to stay easy to edit in Git. Generated views
should look finished on paper without turning the source into a
typesetting project.

Other document toolchains can also produce polished PDFs. Quarto, for
example, can render through several engines; it does **not** always
require LaTeX, and [Typst](https://quarto.org/docs/output-formats/typst.html)
is one Quarto path that avoids a TeX install. Hand-written LaTeX is
heavier still.

This folder uses **Python-Markdown plus WeasyPrint** so that:

- The source remains ordinary Markdown.
- Level filters are data, not forked copies of the document.
- There is no TeX or Typst install for the default build.
- WeasyPrint’s system libraries are documented by the upstream
  project (see [Rebuild](#rebuild)).

### Printable PDF, fillable Markdown, browser HTML

The PDF is a **printable** rendering: letter-size pages, checkboxes
drawn as empty boxes, items that can split across a page so large
blank regions are avoided. It is **not** a fillable PDF form and it
is not a PDF/UA (ISO 14289) accessibility-tagged document.

To record answers, print the PDF and mark the boxes, or copy
`checklist.md` and keep status in your own notes. For screen readers
and reflow, prefer the Markdown source or the generated HTML, not the
PDF.

## Rebuild

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if
you do not already have it. From the repository root:

```bash
uv run docs/checklist/build.py --check
uv run docs/checklist/build.py
```

`build.py` declares its own pinned dependencies as
[PEP 723](https://peps.python.org/pep-0723/) inline script metadata
(`markdown==3.11` and `weasyprint==70.0`). `uv run` creates an isolated
environment from that block and does **not** install this repository’s
root `pyproject.toml` dependencies. Python 3.11 or newer is required:
Markdown 3.11 declares `Requires-Python: >=3.11`. WeasyPrint 70.0
allows `>=3.10`; the tighter pin is the one that matters.

WeasyPrint still needs platform libraries (typically Pango, cairo, and
related graphics libraries), whether you use uv or pip. Install those
by following WeasyPrint’s current first-steps page for your operating
system:

<https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation>

Do not guess package names from this README; the upstream page is the
authority and differs by platform.

The renderer does not require LaTeX or Typst. The same two pins are
listed in [`requirements.txt`](requirements.txt) so a pip/venv install
stays aligned with `uv run`. A test checks that those lists are
identical; if you change a pin, update both files.

To run the tests with uv (pytest is a test extra, not a renderer pin):

```bash
uv run --no-project --with pytest --with markdown==3.11 --with weasyprint==70.0 \
  python -m pytest docs/checklist/tests/test_checklist.py
```

### pip and venv alternative

If you prefer not to use uv:

```bash
python3 -m venv docs/checklist/.venv
source docs/checklist/.venv/bin/activate   # Windows: docs\checklist\.venv\Scripts\activate
pip install -r docs/checklist/requirements.txt
python3 docs/checklist/build.py --check
python3 docs/checklist/build.py
```

To run the tests in that environment:

```bash
pip install pytest
python3 -m pytest docs/checklist/tests/test_checklist.py
```

`build.py --check` parses and validates the source without writing
files. By default the script writes every view as HTML and PDF into
`dist/`. Useful flags:

```text
--view all|level-1|through-2|all-views
--html-only
--pdf-only
--date YYYY-MM-DD
```

`--date` sets the **source/review date** printed in the output. If you
omit it, the renderer uses `SOURCE_DATE_EPOCH` when that variable is
set, then an optional `revision_date` YAML front-matter field on
`checklist.md`, then the last git commit date of `checklist.md`
(`git log -1 --format=%cs`). That printed date is not “today’s build
date” and not an evidence date for a cited standard or for the
webinar itself.

The visible footer looks like `Checklist source <git-short-hash>,
dated <YYYY-MM-DD> (git)` — the last commit of `checklist.md`, not a
wall-clock stamp from the machine that ran the renderer.

PDF metadata uses noon UTC (`YYYY-MM-DDT12:00:00Z`) so a date-only
value is not interpreted as midnight UTC (which would display as the
previous calendar evening in America/Chicago). Rebuilds of the same
source with the same revision should produce byte-identical HTML. PDF
bytes are also kept stable across rebuilds on the same WeasyPrint
version by setting a content-derived PDF `/ID`; if a future WeasyPrint
release introduces metadata-only drift, compare extracted text before
assuming the document changed.

`.venv/` is local tooling; do not commit it.

## Item inventory and source map

33 items, grouped by webinar facet. Evaluation sits beside the four
pillars; it is not a fifth grade. Each item records Level, Pillar,
Optional, Kind, Maturity, Access needed, Maintenance, and Sources,
then **Do this**, **How to verify**, and **Watch for** when a slide
face is easy to over-read.

Kind values include `preference-signal` (for example `robots.txt` and
AIPREF), `rights-signal` (for example RSL and TDMRep),
`access-enforcement`, `standard-practice`, `blueprint-aligned`, and
`advice`. Kind is a label, not an enforcement claim. AIPREF is a draft
usage *preference*, not a license or a rights reservation. TDMRep is a
W3C Community Group Final Report commonly discussed in EU and STM
settings; US practice differs.

CAL-01 and CAL-02 apply if you expose a metadata API. Teams that only
publish static landing pages can mark those two items N/A. Landing-page
JSON-LD (CAL-03) remains useful without an API.

| ID | Facet | Level | PDF | Preferred handouts / notes |
| --- | --- | ---: | ---: | --- |
| RCH-01 | Reachable | 2 | 10 | Glossary (CDN, rate limiting); agent-identification handout |
| RCH-02 | Reachable | 1 | 11 | Glossary (`robots.txt`); RFC 9309; example file |
| RCH-03 | Reachable | 1 | 12 | Glossary visitor classes; Google-Extended = Gemini training *and* grounding, Search ranking unaffected; Search / AI Overviews use Googlebot (no separate AI-Overviews robots token) |
| RCH-04 | Reachable | 2 | 10 | Rate limit is HTTP, not a robots.txt rule |
| RCH-05 | Reachable | 2 | 12–13 | Agent-identification limits |
| RCH-06 | Reachable | 1 | 11 | Optional AIPREF (`preference-signal`, Internet-Draft, vocab **-08** / attach **-05**); distinct from Cloudflare Content Signals |
| RCH-07 | Reachable | 1 | 11 | Optional RSL; `License:` value must be an absolute URL |
| RD-01 | Readable | 1 | 14 | Sitemap lines are not User-agent-scoped |
| RD-02 | Readable | 2 | 17 | Server-rendered text |
| RD-03 | Readable | 2 | 17 | Markdown is a convenience, not “the” preferred format (primary cite is p. 17) |
| RD-04 | Readable | 2 | 16 | FAIR Signposting |
| RD-05 | Readable | 1 | 15 | Optional `llms.txt` (v2); not a baseline |
| RD-06 | Readable | 1 | 18 | Optional `SKILL.md` |
| RD-07 | Readable | 1 | 19 | Optional / bleeding-edge `ard.json` |
| RD-08 | Readable | 3 | 20 | Optional / bleeding-edge Agent Plugins |
| CAL-01 | Callable | 3 | 21 | If you expose a metadata API, document it; mark N/A if you only publish static pages |
| CAL-02 | Callable | 3 | 21 | If you expose a metadata API, use ordinary web architecture for **metadata**; mark N/A if you have no API |
| CAL-03 | Callable | 2 | 21 | JSON-LD on landing pages is useful even without an API; also offer it from the API if you have one |
| CAL-04 | Callable | 3 | 22–25 | MCP optional; not an SI-readiness plan by itself |
| CAL-05 | Callable | 3 | 26 | Protected HTTP MCP; authorization optional; scopes illustrative |
| MEA-01 | Meaningful | 2 | 28 | PIDs |
| MEA-02 | Meaningful | 1 | 29 | Data dictionary / vocabulary; not an ontology ladder |
| MEA-03 | Meaningful | 2 | 30 | Profiles + `conformsTo`; DataCite is not primarily schema.org |
| MEA-04 | Meaningful | 2 | 31 | License metadata; not “all NIAID data are public domain” |
| MEA-05 | Meaningful | 2 | 32 | Citation, CRediT, contributor PIDs; live page https://www.gofair.us/resources/citation |
| MEA-06 | Meaningful | 2 | 33 | PROV-O / DataCite version relations |
| MEA-07 | Meaningful | 1 | 31 | Optional TDMRep (CG Final Report; rights signal, not a block; common in EU/STM; US practice differs) |
| MEA-08 | Meaningful | 3 | 34 | Optional SHACL Recommendation (not experimental); local or CI validation is enough |
| MEA-09 | Meaningful | 3 | 34 | Optional SPARQL RL Working Draft; cite https://www.w3.org/TR/sparql-rl/ |
| MEA-10 | Meaningful | 1 | 34 | Optional SSSOM/**TSV** (advice); `author_id` and `confidence` optional |
| EVL-01 | Evaluation | 1 | 36 | Try an agent; `prompts/evals` |
| EVL-02 | Evaluation | 1 | 36 | Access vs answerability vs accuracy; no single score |
| EVL-03 | Evaluation | 1 | 36 | Optional NDE / Lighthouse diagnostics |

## Source map and known PDF-face mismatches

Corrections below follow the webinar handouts, not a wider literature
review. Use them when the PDF face and a handout disagree.

| Topic | PDF face | Checklist follows |
| --- | --- | --- |
| Google-Extended | Broader “AI search visibility” sentence (p. 12) | Glossary and [Google’s crawler documentation](https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers#google-extended): product token covering Gemini training **and** grounding; does not affect Search inclusion or ranking. Search / AI Overviews surfaces use Googlebot; there is no separate AI-Overviews robots token. |
| AIPREF drafts | Sample `robots.txt` in `assets/` still comments `draft-ietf-aipref-vocab-07` | Glossary/bibliography: `draft-ietf-aipref-vocab-08` and `draft-ietf-aipref-attach-05`. Unlabeled `Content-Usage` lines should be labeled as an Internet-Draft. |
| RSL | Example can be read as a relative `License:` path (p. 11) | RSL docs: `License` must be an absolute URL. |
| Sitemap | Easy to read `Sitemap:` as `User-agent`-scoped | sitemaps.org / Google: `Sitemap` lines are not scoped per user agent. |
| SPARQL RL | Older dated `sparql12-rl` path (p. 34) | Current shortname [https://www.w3.org/TR/sparql-rl/](https://www.w3.org/TR/sparql-rl/). Date omitted unless essential. |
| SSSOM | Easy to infer required author and confidence (p. 34) | SSSOM/TSV (not CSV); `author_id` and `confidence` are optional. |
| MCP auth | Closing line can be read as “no login each time” (p. 25) | OAuth is optional and applies only when the HTTP transport is protected. Example scopes are illustrative; consent may still be required. |
| Markdown alternate | Alternate-representation discussion also appears with `llms.txt` (p. 15) | Primary cite is p. 17. |
| Citation guidelines | Slide p. 32 points at `https://www.gofair.us/citation-recommendations` (that path currently 404s) | Live Blueprint page: [https://www.gofair.us/resources/citation](https://www.gofair.us/resources/citation). |

Other points called out in item text rather than copied from the
slide: static-file edits can require an admin; preference is not
enforcement; licenses and reservation signals are not crawl blocks;
NIAID data are not assumed to be public domain; NIH notice
NOT-OD-25-081 is cited for controlled-access human genomic data;
JSON examples on slides are fragments.

## Third-party evaluation tools

EVL-01 mentions trying a public page in an AI-assisted search or chat
interface, and other checks may use hosted auditors. Those tools send
the URLs or text you provide to a vendor. Do not paste non-public or
controlled-access data into them.

## Editing the source

Edit [`checklist.md`](checklist.md), then rebuild and run the tests so
generated views and the Markdown stay aligned. Keep new items on the
`### ID. Title` pattern with the same metadata fields, plus **Do this**
and **How to verify**. Prefer webinar PDF pages and the corrected
handouts above; do not invent citations.

Generated HTML and PDF must not become a parallel source of truth.
