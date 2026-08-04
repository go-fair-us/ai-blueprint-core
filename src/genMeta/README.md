# genMeta — Herdr + Pi metadata extract / SHACL loop

First-try orchestrator: **extract** Dataset JSON-LD from a resource URL (Pi agent),
**validate** with host pySHACL (`niaid-bp-validation`), **repair** (Pi agent) until
conformance or max iterations.

**Not Hermes.** Pattern adapted from coffeenotes `python_herdr` (Herdr 0.7.x + Pi).

## Prerequisites

1. **Herdr** running (`herdr` or `herdr server &`)
2. **Pi** available to Herdr (`kind=pi`)
3. Python deps:

```bash
# from ai-blueprint-core repo root
uv sync --extra genmeta
```

4. Model credentials in the environment that **starts Herdr** (panes inherit that env), e.g.:

- `OPENROUTER_API_KEY` for `openrouter/…` models
- xAI / NRP keys for `xai-auth/…` or `ellm-nautilus/…`
- or `pi` → `/login …` so `~/.pi/agent/auth.json` is populated

## Run

```bash
cd /path/to/ai-blueprint-core

uv run python src/genMeta/main.py \
  --url https://immport.org/shared/study/SDY998 \
  --max-iters 3 \
  --timeout 600
```

Useful flags:

| Flag | Meaning |
|------|---------|
| `--cleanup` | Close the Herdr workspace when finished |
| `--model-extractor ID` | Pi model for extract pane |
| `--model-repairer ID` | Pi model for repair pane |
| `--runs-dir PATH` | Where to write run artifacts (default `src/genMeta/runs`) |
| `--cwd PATH` | Pane working directory (default: repo root) |

Env overrides: `GENMETA_MAX_ITERS`, `GENMETA_TIMEOUT`, `GENMETA_MODEL_EXTRACTOR`,
`GENMETA_MODEL_REPAIRER`, `GENMETA_CLEANUP=1`, `GENMETA_CLOSE_STALE=1`,
`HERDR_CLIENT_TIMEOUT`.

## Pipeline

```text
URL → [Pi extractor] → record.jsonld
    → [host pySHACL] → validation/iter-NN/
    → if fail: [Pi repairer] patches record.jsonld → re-validate
    → final-report.md
```

Host validation uses:

- `skills/niaid-bp-validation/scripts/validate.py`
- `skills/niaid-bp-validation/assets/blueprint-required.ttl`

Starter shape requires `schema:name`, `schema:description` (50–5000 chars), and
`schema:url`. Passing SHACL is **not** full Blueprint Table 1 compliance.

## Agents

| Herdr alias | Role |
|-------------|------|
| `genmeta-extractor` | Fetch page; write `record.jsonld` + `notes.md` |
| `genmeta-repairer` | Evidence-safe patches from SHACL `results.json` |

Names are prefixed so they do not collide with other herds (`lead`, `researcher-*`).

## Run artifacts

```text
src/genMeta/runs/genmeta-<timestamp>/
  00-task.txt
  workspace_id
  01-extractor.txt
  record.jsonld
  notes.md
  validation/iter-01/{report.ttl,results.json,conforms.json}
  02-repair-iter-01.txt
  final-report.md
```

## Layout

```text
src/genMeta/
  main.py
  README.md
  defs/           # herdr client helpers, config, host validate, report
  prompts/        # system + user prompts for extractor/repairer
  runs/           # generated (gitignored contents)
```

## Troubleshooting

| Symptom | What to try |
|---------|-------------|
| Herdr not reachable | `herdr` or `herdr server &` |
| `agent_name_taken` | `GENMETA_CLOSE_STALE=1` or `herdr agent rename genmeta-extractor --clear` |
| OpenRouter fails in pane | Export key **before** starting Herdr; restart Herdr |
| No `record.jsonld` | Check `01-extractor.txt`; orchestrator tries to recover fenced JSON |
| Always NON-CONFORMING | Inspect `validation/iter-*/results.json`; often short description or missing url |

## Skills used as instructions

- `skills/niaid-bp-metadata-extract/`
- `skills/niaid-bp-validation/`
