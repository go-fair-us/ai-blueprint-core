# Repository herd

Run a facet review and the competency-answerability questions for each repository in a CSV. Each job is a fresh Pi process. Herdr holds a fixed set of panes and keeps the runs visible.

The facet review is the November 2026 webinar pass in [`docs/metabolomics-workplan/repoAssessment.md`](../../docs/metabolomics-workplan/repoAssessment.md): Be reachable, Be readable, Be callable, and Be meaningful, nineteen checks, one Pi process per repository. The process loads each procedure from the Blueprint knowledge server before it scores that check.

Competency answerability is the single-host runs in [`compQuestions/answerability_runs.md`](../../compQuestions/answerability_runs.md). One Pi process takes one run of at most three questions. The answer key stays in `key.md` for the grader.

`workflows/shell_herdr_copy/` is a separate demo with a researcher, a reviewer, and a lead. This directory runs one fresh Pi process per job.

## Before a live run

- `herdr`, `pi`, `jq`, and `uv` are on `PATH`. Start Herdr in another terminal with `herdr`.
- Pi can call the NRP provider. The default is `pi --provider nrp --model deepseek-v4-flash`. Check with `pi auth check --provider nrp --model deepseek-v4-flash`.
- For facet jobs, start the knowledge server and leave it up:

```bash
uv sync --extra mcp
./bin/run_mcp.sh
```

That serves `http://127.0.0.1:8000/mcp`. The script checks the port. Start the server yourself before a facet run. `--only answerability` skips the check. Answerability jobs pass `--no-mcp` either way.

- `bwrap` hides `compQuestions/` and the stamp directory from the agent's bash. The report is redirected to the stamp directory by the outer shell, so it stays on disk. `--no-sandbox` leaves the answer key readable.

## Commands

From the repository root:

```bash
workflows/repo_herd/run-repo-herd.sh --dry-run
workflows/repo_herd/run-repo-herd.sh --repos immport,iedb --concurrency 2
workflows/repo_herd/run-repo-herd.sh --only facet
workflows/repo_herd/run-repo-herd.sh --only answerability --no-sandbox
workflows/repo_herd/run-repo-herd.sh -- --provider openai --model gpt-4o-mini
```

Every job runs `pi --provider nrp --model deepseek-v4-flash` unless flags after `--` include `--provider`, `--model`, or `--models`. Those flags replace the default pair. Other Pi flags after `--` are added and the default model stays.

`--repos` is a comma-separated list. A row is included when its Name contains a token, case-insensitive. `--concurrency` is the number of Herdr panes (default 3). One host has at most one job running, so a facet review and an answerability run for the same site take turns. Different hosts fill the free panes.

`--facet-timeout` defaults to 2700 seconds. `--answerability-timeout` defaults to 1200 seconds. `--cleanup` closes the Herdr workspace when the script exits. The default leaves it open. The script prints `herdr workspace focus <id>`.

`--dry-run` writes the stamp directory and stops before Herdr and Pi. Pi options go after `--` and override the default NRP model when they name a provider or model.

The default CSV is [`docs/NIAID_RepostoryList.csv`](../../docs/NIAID_RepostoryList.csv). `--csv` selects another file with the same columns.

## What each row becomes

The origin is the CSV URL reduced to scheme and host. A path on that URL, and every URL in Additional Reference URL, is a hint page. `repo.json` keeps the Notes column. The prompt omits it. The agent confirms hint pages with a live response and discovers one public record when none of the hints is a record.

Six repositories have single-host question runs: AccessClinicalData@NIAID, TB Portals, IEDB, ImmPort, BV-BRC, and VEuPathDB. VEuPathDB is the alias in `aliases.json`. The facet review uses `https://veupathdb.org/`. The questions use `https://plasmodb.org/`, which is the origin already written in those YAML blocks. The summary states both hosts.

MWCCS, ACTG, ITN Trialshare, immunspace, CEIRR, and ClinEpiDB have no single-host test set. They still get a facet review, including `evals/competency-questions.md`. `skipped-answerability.md` records that no external run was on file. The herd invents no questions.

ACD-4 and TB-4 need two repository hosts, so they are not jobs. Metabolomics Workbench is not a row in the default CSV. Its driver remains `compQuestions/metabolomics/run-metabolomics-answerability.sh`. A row in a CSV is how that site would enter this herd. When the origin host is `www.metabolomicsworkbench.org`, the facet prompt includes the October 2026 compatibility note.

## Output

Runs are written under `workflows/repo_herd/runs/<UTC stamp>/`, which is gitignored.

```text
manifest.json
summary.md
<slug>/repo.json
<slug>/facet/prompt.txt command.txt run.sh report.md stderr.txt meta.txt
<slug>/answerability/run-a/input.yaml prompt.txt key.md report.md stderr.txt meta.txt
<slug>/answerability/score.md
<slug>/skipped-answerability.md
```

`summary.md` has one table per repository: property, evaluation, verdict, evidence URL. A check that is missing from the facet report is `not-observable`, and the table says the report did not include it.

`score.md` lines up `checks[].answer` with the key table in question order. A row is `match` or `miss` only when the whole Check cell is one of these:

- a `contains` list joined by `AND`
- an exact token that also appears in the expected answer
- a numeric floor written as `accept >= N`

Every other Check cell is `ungraded`, with the expected text and the agent's answer side by side. Volatile rows stay marked volatile. A Pi exit of 0 means the process finished. It does not mean the answer matched. The script's own exit code is 1 when a Pi process exits non-zero or a job never writes `meta.txt`.

## Tests

```bash
uv run --with pytest pytest workflows/repo_herd/tests
```

The tests read the real CSV and `compQuestions/answerability_runs.md`. They do not call Herdr or Pi.
