# Agent-access review: report template

This kit rebuilds the look of *Repository agent-access review* (`reference/original.pdf`)
from a data file. You fill in YAML, run one command, and get the same three-part PDF:
summary and verdict mix, check-by-repository grid, and competency questions. It works for
any number of repositories, checks, categories and questions.

```
report-template/
├── build.py                  # data file -> PDF (and optional HTML)
├── data/
│   ├── example.yaml          # the original report, value for value
│   ├── test-variable.yaml    # synthetic: 5 repos, 3 categories, 5-12 checks each, 0-9 questions
│   ├── test-small.yaml       # synthetic: 2 repos, 2 categories, 5 checks, 1 question
│   ├── test-stress.yaml      # synthetic: 30 repos, 38 checks, 6 categories, up to 12 questions
│   └── 20261117T020206Z.yaml # generated from the real run by tools/from_repo_herd.py
├── templates/
│   ├── report.html.j2        # page structure (Jinja2)
│   └── report.css            # layout, type, colours (points, letter landscape)
├── theme/
│   ├── report.mplstyle       # matplotlib style matching the report
│   └── theme.py              # palette + stacked_hbar() chart + text measuring
├── schema/report.schema.json # JSON Schema for the data file
├── tools/
│   ├── compare_bbox.py       # word-position diff between two PDFs
│   ├── side_by_side.py       # page renders side by side + pixel-diff score
│   └── make_stress.py        # regenerates data/test-stress.yaml
├── reference/original.pdf    # the report this was modelled on
├── out/                      # built PDFs and comparison PNGs
├── STYLE.md                  # measured style spec (fonts, colours, geometry)
└── requirements.txt
```

## Build

```bash
pip install -r requirements.txt      # WeasyPrint also needs Pango (apt install libpango-1.0-0)
python3 build.py data/example.yaml -o out/example.pdf
python3 build.py my-run.yaml -o out/my-run.pdf --html out/my-run.html   # HTML for debugging
```

For the closest match, install a Helvetica-metric font. On Linux that is
`fonts-urw-base35` (Nimbus Sans); Liberation Sans or Arial also work. Build errors name the
bad field, for example `S/a: unknown verdict 'Z'`.

## Filling in the data file

Copy `data/example.yaml` and edit it. Its blocks:

| Block | What it holds |
|---|---|
| `report` | `title`, `subtitle`, `footer` (`org · stamp · model`), `pdf_title`, `author` |
| `summary_cards` | any number of `{value, label}` cards. Three fit the original 230 pt width; four or five shrink to fit one row; six or more wrap |
| `verdicts` | the verdict vocabulary in bar-stacking order: `id`, `symbol`, `label`, `color`, `text` |
| `categories` | column groups in order: `id`, `label`, optional `tint` (a palette is cycled otherwise) |
| `checks` | every check any repository ran: `id`, `label`, `category`. Columns are grouped by category in category order |
| `question_grades` | grade vocabulary for the competency tiles (`match`, `ungraded`, `no-answer`, ... add more freely) |
| `sections` | headings, captions, footnotes and notes for the three sections |
| `repositories` | one entry per repository, in display order |

A repository looks like this:

```yaml
- name: ACDN
  url: https://accessclinicaldata.niaid.nih.gov/   # optional
  minutes: 23                                       # optional, shown right of the bar
  # Either: one symbol per check, in the order of `checks` (every check ran)
  verdicts: "P o A A A ? A ~ A o ~ A A ~ ~ o A ~ A"
  # Or: only the checks that ran, by check id, as a verdict id or symbol
  # verdicts: {reachable: present, robots: "o", openapi: A}
  questions:                                        # optional; omit for facet-only repos
    - {id: ACD-1, grade: ungraded}
    - {id: ACD-2, grade: match}
```

Quote `"~"` and `"?"` in YAML, because a bare `~` means null.

### Counts are computed, not typed

Bar segments, legend totals, "checks scored present", the grade counts and the list of
repositories without questions all come from the verdicts and questions. You only type
numbers the data can't supply, such as "22 of 23 Pi jobs exited 0" or the run minutes.

Text fields are Jinja templates, so prose stays correct when counts change:

```yaml
subtitle: "{{ n_repos|words|capitalize }} NIAID repository sites · {{ n_checks }} webinar checks · 17 November 2026, 02:02 UTC"
caption: "{{ q.match|words|capitalize }} rows matched, {{ q.ungraded|words }} are ungraded ..."
notes:
  - "{{ no_question_repos|join_and }} have a facet review only."
  - "{% if totals.blocked %}{{ totals.blocked }} checks were blocked.{% endif %}"   # blank notes are dropped
```

### Template variables

| Variable | Meaning |
|---|---|
| `n_repos`, `n_checks`, `n_categories` | counts (only checks or categories some repository used) |
| `checks_min`, `checks_max`, `checks_total` | checks run per repository (min/max) and overall |
| `uniform_checks` | true when every repository ran every check |
| `totals.<verdict id>` | e.g. `totals.present`, `totals['not-observable']` |
| `q.<grade id>` | e.g. `q.match`, `q['no-answer']` |
| `n_questions` | total competency questions |
| `question_repos`, `no_question_repos` | repository names with and without questions |
| `repositories[i]` | each has `.name .total .counts .category_counts .n_categories .questions .results` |
| filters | `words` (0-20 as words), `join_and` ("A, B, and C"), `plural(n, 'check')`, `sep` |

## How the template adapts to the counts

- **Repositories.** The verdict-mix chart is 24 pt per repository. Page 1 holds 13 bars under one
  row of cards, and each further row of cards removes 3. More repositories continue on
  "Verdict mix (continued)" pages of 17 bars, with the label column and bar scale kept
  constant across pages. The check grid shows 13 rows per page and continues with the header
  repeated. Pages with only a few repositories leave white space, and footnotes stay pinned to
  the bottom as in the original.
- **Checks per repository.** If every repository ran the same checks, bars are full width
  as in the original. Otherwise a bar's length is proportional to the checks it ran, and the right
  column reads "12 checks · 10 min". In the grid, a check a repository did not run is a dashed
  empty cell, and the caption explains this.
- **Categories.** Any number of categories is supported, and bands size to their column count.
  The column pitch is 34 pt as in the original and shrinks to fit, down to 21 pt. Below that,
  columns split at category boundaries into "part 1 of N" pages.
- **Long names.** The chart label column and the grid label column widen to fit (the grid
  caps at 160 pt and truncates beyond that with an ellipsis).
- **Questions.** Tiles wrap seven per row, and repositories without questions are skipped. The
  section flows over as many pages as it needs without splitting a repository's block. With no
  questions at all, it prints a one-line note. Set `sections.competency.enabled: false`
  to drop it.
- **Footnotes.** Long footnotes reserve space by taking rows off the last page of their
  section.

Layout constants (rows per page, column-pitch limits, and so on) are in `LAYOUT` at the top
of `build.py`.

## Reusing the chart style elsewhere

```python
from theme import theme
theme.apply()                     # loads theme/report.mplstyle: fonts, colours, no chartjunk
svg = theme.stacked_hbar(rows, verdicts)   # the verdict-mix chart, sized in points
```

The style file sets the verdict palette as the colour cycle, Helvetica-like fonts, the
`#F7F7F5` background, hairline `#D1D6DB` spines and muted tick labels. New chart types
picked up from it will match.

## Building straight from a repo_herd run

```bash
python3 build.py --run ~/src/Projects/NIAID/ai-blueprint-core/workflows/repo_herd/runs/20261117T020206Z \
                 -o out/20261117T020206Z.pdf
# same thing in two steps:
python3 tools/from_repo_herd.py RUN_DIR -o data/20261117T020206Z.yaml
python3 build.py data/20261117T020206Z.yaml -o out/20261117T020206Z.pdf
```

Run `jobs.py finish --out RUN_DIR` first; `run-repo-herd.sh` does this at the end of a run.
The converter reads only files in the run folder:

| Report element | Source in the run folder |
|---|---|
| repositories, order, URL shown | `manifest.json` `repos[]` (`name`, `origin`). The name in brackets at the end, such as `(ACDN)`, is used as the short name. `--full-names` turns that off, and `--rename VeuPathDB=VEuPathDB` sets a name by hand |
| checks, columns, categories | `summary.md` tables: `Evaluation` is the check, `Property` ("Be callable") is the category |
| verdict letters | `summary.md` `Verdict`. `not-observable (report did not include this evaluation)` becomes `?` (unparsed): the facet report had no parseable YAML block for that check |
| minutes, facet exit | `<slug>/facet/meta.txt` (`seconds`, `exit_code`). The first line of `stderr.txt` is quoted when the exit is non-zero |
| "N of M Pi jobs exited 0" | every `jobs[].dir/meta.txt` listed in `manifest.json` |
| model in the footer | `--provider` and `--model` in `command.txt` |
| stamp and date | the run folder name (`YYYYMMDDTHHMMSSZ`) |
| question tiles and grades | `<slug>/answerability/score.md` (written by `jobs.py finish`), in file order |
| why a row has no answer | whether each `run-*/report.md` has a fenced YAML block and whether it parses |
| facet-only repositories | `<slug>/skipped-answerability.md` |
| question host differs | `manifest.json` `question_origin` (the VeuPathDB to PlasmoDB alias) |

**Missing values are never guessed.** If something is missing, such as meta seconds, a
`summary.md` section, `score.md` or an unknown verdict word, the value is left out and a
warning is printed. The warnings are also written as comments at the top of the YAML.

**Captions and notes are generated from facts in the run.** Hand-written commentary goes in
an overrides file merged on top, for example `--overrides notes/20261117.yaml` containing:

```yaml
sections:
  competency:
    notes:
      - TB Portals still answers the country question with Belarus in the report text.
```

`jobs.py` does not make a PDF. `visual-report.pdf` in the run folder was made separately with
ReportLab, and this template reproduces it.

Tests: `python3 -m pytest tests` (or `python3 tests/test_from_repo_herd.py`). The real-run test
reads `$REPO_HERD_RUN` and is skipped when no run folder is found.

## Checking a build against the original

```bash
python3 tools/side_by_side.py reference/original.pdf out/example.pdf out/compare
python3 tools/compare_bbox.py reference/original.pdf out/example.pdf
```

Current result for `data/example.yaml`:
- **Words:** the same words as the original on all three pages, with every word within about 2 pt
  of its original position.
- **Pixels:** 1.8 to 3.4 % of pixels differ, mostly from anti-aliasing and font hinting.
