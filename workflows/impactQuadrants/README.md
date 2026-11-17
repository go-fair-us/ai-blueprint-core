# impactQuadrants

Where should each repository start? This program takes the output of a `repo_herd` run
(the 19-check facet review), treats every check that came back **absent** as a gap,
asks a model to place the fix for each gap on **effort to implement** (x) and **impact
on agent access** (y), and builds a PDF:

- **Page 1:** summary cards, a combined quadrant chart (one dot per check across all
  repositories) and a ranked table of the most common gaps.
- **One page per repository:** its quadrant chart and a table of each gap's fix,
  category, effort, impact, quadrant and rationale. The counts of non-gap verdicts are
  listed under the chart.
- **Appendix:** the method, the rubric, the model and backend, the run stamp, and all
  verdicts by check.

It is a separate report from the agent-access review (`report-template`). It shares only
that report's look: US Letter landscape, a `#F7F7F5` page, Helvetica/Nimbus Sans, and
the same ink, muted and hairline colours.

`quadrant_plot.py` is the original standalone plotter. The report imports it as a
library, and the per-repository placement files are in its format, so you can still
plot one by hand.

## Run

    pip install -r requirements.txt
    RUN=../repo_herd/runs/20261117T020206Z

    python3 impact.py all --run $RUN --backend stub      # every step; placeholder placements
    python3 impact.py all --run $RUN                     # every step with the default backend (pi)

Or step by step:

    python3 impact.py extract --run $RUN                 # work/<stamp>/gaps/<slug>.json  (no model)
    python3 impact.py assess  --run $RUN --samples 3     # work/<stamp>/assess/<slug>.json
    python3 impact.py review  --run $RUN                 # work/<stamp>/placements/<slug>.yaml
    python3 impact.py report  --run $RUN -o out/impact-<stamp>.pdf [--html out/x.html]

Intermediate files go to `--work` (default `work/<stamp>/`). Nothing in the run folder
is changed.

## Steps

**extract.** For each repository, every check in `summary.md` whose verdict is in
`gap_verdicts` (default: `absent` only) becomes a gap item. Present, partial, blocked,
not-observable and unparsed checks are only counted (`non_gaps`). The evidence comes from
the check's fenced YAML block in `facet/report.md`: the sub-checks that did not pass, the
summary and the listed gaps. If a block doesn't parse, the raw evidence lines are used and
a note is added. The operator-fix text is the report's prose for the check's property
(the `## Be readable` section, or a `**Be readable.**` paragraph under "What the operator
should do next").

**assess.** One model call per repository. The prompt is built from `rubric.md`, the
repository's verdicts for all checks (context only) and its gap list. It's saved in
`work/<stamp>/prompts/`. The answer must be JSON matching
`schema/placement-response.schema.json`, with exactly one placement per gap id: no added
ids, none missing, x and y in -1..1, a label of 40 characters or fewer, a rationale of
200 characters or fewer, and a confidence of low, medium or high. A label or rationale
that only runs past its cap is shortened on a word boundary and kept. Any other invalid
answer is rejected and retried with the errors, up to `max_attempts` times.

`--samples N` calls N times and uses the median. A point whose spread on either axis
exceeds `variance_threshold` is flagged "high variance" in the table. Answers are cached
in `work/<stamp>/cache/`, keyed by a sha256 of the prompt, the rubric file, the backend,
the model and the sample index, so a re-run costs nothing. If you change the rubric, the
cache key changes too.

**review.** This step writes `placements/<slug>.yaml` in `quadrant_plot.py` format, with
extra keys (`gap_id`, `rationale`, `quadrant` and so on) that the plotter ignores.
Hand edits survive re-runs:

- Put corrections in `work/<stamp>/overrides.yaml` (or `--overrides FILE`):

      repos:
        veupathdb:
          facet-check:openapi-discovery: {x: 0.2, y: 0.8, label: "OpenAPI for /service"}
          facet-check:mcp-exposure: {hide: true}
      combined:
        facet-check:llms-txt: {label_pos: below}

- Or edit `placements/<slug>.yaml` directly. The next `review` compares it with the copy
  it generated last time (`placements/.generated/`) and copies your changes into
  `overrides.yaml` before it regenerates. A deleted point becomes `{hide: true}`.

**report.** The combined chart has one dot per check id across repositories. It sits at
the median x and median y over the repositories where that check is a gap. Its size is
the number of those repositories, its colour is the category, and its label reads like
"OpenAPI discovery (9/12)".

The pages adapt to any number of repositories, checks and categories:
- Long tables continue on extra pages.
- A repository with no gaps, or with no facet results, gets a short page that says so.
- A crowded chart (more than 14 points, or too much label text) switches to numbered
  dots that match a numbered table.

## Model backends

Choose one with `--backend` (the default is set in `impact.yaml`):

| Backend | What it does | Setup |
|---|---|---|
| `pi` | Pi CLI, as the run used it: `--provider nrp --model deepseek-v4-flash`, no tools, no MCP | set `pi.bin` in `impact.yaml` to `ai-blueprint-core/bin/pi`; `--model` and `--provider` override |
| `openai` | any OpenAI-compatible `/chat/completions` endpoint | `IMPACT_OPENAI_BASE_URL`, `IMPACT_OPENAI_API_KEY`, `IMPACT_MODEL` (or `OPENAI_BASE_URL` / `OPENAI_API_KEY` / `--model`) |
| `stub` | **PLACEHOLDER, not a model.** One fixed position per check from `stub_defaults.yaml`, set by hand from the rubric anchors | none |

The stub exists so you can test the pipeline and layout without credentials. Its output
is marked `placeholder: true` in the assess and placement files. Every rationale starts
with "PLACEHOLDER", and the report carries a red banner, a watermark on every chart and
a footer note. The stub does not read the evidence, so every repository gets the same
position for the same check. Stub answers are never cached.

## Adding gap sources (e.g. competency questions)

Gaps are generic items (`schema/gap-file.schema.json`). Each one has a `source` (today
`facet-check`), a `key` that is stable across repositories, a free-text `category` and
the evidence fields. To add a source:

1. Write `impactlib/extractors/<name>.py`:

       from . import ExtractResult, register

       @register("competency-question")
       def extract(run, repo, cfg):
           # read run.dir / repo.slug / "answerability" / "score.md" ...
           return ExtractResult(gaps=[{"id": "competency-question:Q3", "source": "competency-question",
                                       "key": "Q3", "label": "...", "category": "Answerable",
                                       "verdict": "miss", "evidence": [...], ...}],
                                non_gaps={"match": 9}, context={"grades": {...}})

2. Import it in `extractors.load_builtin()`.
3. List it under `sources:` in `impact.yaml`, set its gap verdicts in `gap_verdicts:`, and
   optionally give it a colour under `categories:`.

Nothing else is hard-wired. Categories come from the data (with palette colours if
they're not configured), the combined chart groups on `source:key`, and the prompt sends
each item's evidence fields as they are. The rubric is written for webinar checks, so a
question source probably wants its own rubric section (`--rubric`). The test
`test_custom_extractor_source` registers a fake `competency-question` source.

## Files

    impact.py               command line (extract | assess | review | report | all)
    impact.yaml             settings: sources, gap verdicts, colours, backends, sampling
    rubric.md               versioned effort/impact rubric (the model sees its body)
    stub_defaults.yaml      placeholder positions for --backend stub
    quadrant_plot.py        standalone plotter, also imported as a library
    impactlib/              runfiles, gaps, extractors/, rubric, backends, assess, review,
                            combine, report, style
    templates/              impact.html.j2, impact.css
    schema/                 gap-file and placement-response JSON Schemas
    tests/                  pytest (20261117 run + synthetic runs); stress.py layout check

    python3 -m pytest -q tests
    python3 tests/stress.py /tmp/stress     # 20 repos x 24 checks x 5 categories

## quadrant_plot.py (standalone)

    python3 quadrant_plot.py example.yaml                     # writes example.png
    python3 quadrant_plot.py example.csv --config example.yaml -o out.png

Each point has `label`, `x`, `y` and `category`. The optional fields are `label_pos`
(right, left, above or below), `dx`/`dy` and `color`. Chart settings are title, x_label,
y_label, quadrants, quadrant_colors, categories, width, height, dpi, dot_size, the font
sizes, legend and output.

The additions are backward compatible. Old files render pixel-for-pixel as before, and
every new option is off by default:
- **Point fields:** `size`, which scales the dot area across `size_range`, and
  `marker_text`, which is drawn inside the dot.
- **Chart settings:** `avoid_overlap: true` (it moves labels that have no
  `label_pos`/`dx`/`dy` and draws a leader line when one moves far), `size_legend`,
  `watermark`, `font_family`, `background`, `label_wrap`, `dot_edge_width` and
  `quadrant_text_alpha`.
- **Library use:** `qp.plot(cfg, points, path_or_file)` and `qp.render(cfg, points)`,
  which returns the matplotlib figure.

Note: in `example.csv`, the OpenAPI row and the last row have extra empty columns, and
its Dataset JSON-LD point is at x = 0.24 while `example.yaml` has -0.20. Both files are
unchanged from the originals.
