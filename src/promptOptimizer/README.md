# promptOptimizer

Optimize prompts for **NIAID Blueprint** goals with DSPy, and compare optimizers
(BootstrapFewShot, MIPROv2, GEPA) on the same footing (with token cost metered).

> **Just want to run it?** See [QUICKSTART.md](QUICKSTART.md).

## Mental model

**One harness, one active profile per run.** Changing goals is a configuration /
run isolation concern — not a multi-product `--task` switch.

| Piece | What it is |
|---|---|
| **Harness** | Shared program + scoring + optimizers (`defs/`, `optimize/`) |
| **Active profile** | `config/profile.yaml` — seed prompt, rubric, weights, scenarios |
| **Recipe library** | `config/profiles/*.yaml` — optional copies you activate with `--profile` |
| **Separate goals** | Separate runs: `--profile metadata --workdir runs/meta-1` |

Shipped recipes (examples, not hard-wired modes):

| Profile | Goal | Scoring emphasis |
|---|---|---|
| `api` *(default profile.yaml)* | Blueprint-aligned **API example** (JSON-LD + OpenAPI + PIDs) | JSON-LD, **OpenAPI**, Table 1, PIDs, judge |
| `metadata` | schema.org **Dataset** JSON-LD | JSON-LD, **Table 1**, PIDs, judge (no OpenAPI) |

Both follow the [NIAID Blueprint for Digital Objects](https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md).

## Why this shape

DSPy optimizers don't "make a prompt better" in the abstract — they search
against a **metric over an eval set**. So the real work is a program, a
dataset, and a scoring function; the optimizers are interchangeable branches
on top.

- **Steps 1–2 once, shared:** program + scenarios + scoring core + one eval harness.
- **Three optimizer branches, as alternatives (not a pipeline):** each compiles
  from the same un-optimized program and is scored on the same held-out test set.

## Layout

```
main.py                 CLI
config/
  default.yaml          models (nrp, openrouter, xai, nvidia), run/data knobs
  profile.yaml          ACTIVE goal (edit this for the default run)
  profiles/             optional recipes (api.yaml, metadata.yaml, …)
  prompts/*.md          long seed / rubric text
  schemas/              editor JSON schemas
tasks/                  runtime Task from active profile (not product modules)
defs/                   harness: config, lm, checks, dataset, evaluate, …
optimize/               baseline | bootstrap | mipro | gepa
artifacts/              default workdir (prefer --workdir per goal)
```

## Scoring

`score_artifact` blends deterministic checks (`defs/checks.py`) with an LLM
judge, using **weights from the active profile**. Components with weight 0 or
omitted are skipped (e.g. metadata profile has no OpenAPI).

Checks are intentionally **strict** so baseline sits below ceiling. Seed
instructions stay short; the full checklist lives in the rubric + checks so
optimizers can rediscover detail.

### Train / val / test

Scenarios split into **train** / **val** / **test**. Optimizers never see final
test scores as `valset`. Fractions come from `config/default.yaml` `data:`.

### New goal (new profile recipe)

1. Add `config/profiles/<name>.yaml` (copy an existing recipe).
2. Point seed/rubric at `config/prompts/…` sidecars.
3. Run with `--profile <name> --workdir runs/<name>-1`.

Or overwrite `config/profile.yaml` and run without `--profile`.

## Configuration

**Never put API keys in YAML** — only env var *names* (`env_key`).  
Precedence: **CLI > config file > shipped defaults**.

```bash
# Default active profile (config/profile.yaml)
uv run main.py baseline

# Library recipe + isolated run
uv run main.py compare --profile metadata --workdir runs/meta-1

# Alternate config root for a whole trial
uv run main.py compare --config runs/trial2/config --workdir runs/trial2
```

Edit seed without code:

```bash
$EDITOR config/prompts/api.seed.md
uv run main.py show-prompt
```

## Setup

| Var | Used for |
|---|---|
| `NRP_API_KEY` | `--backend` / `--reflection-backend nrp` |
| `OPENROUTER_API_KEY` | OpenRouter (default reflection backend) |
| `XAI_API_KEY` | xAI Grok API key (not OAuth) |
| `NVIDIA_API_KEY` | NVIDIA Integrate API |

```bash
uv sync            # from repo root
cd src/promptOptimizer
```

By default the judge is the reflection LM — align backends or use `--judge task`
if you only have one key.

## Usage

```bash
uv run main.py gen-scenarios --n 40
uv run main.py baseline
uv run main.py bootstrap
uv run main.py mipro
uv run main.py gepa --gepa-budget 60
uv run main.py compare

# Different goal, separate artifacts
uv run main.py compare --profile metadata --workdir runs/meta-1

uv run main.py eval --program artifacts/api-gepa.json
uv run main.py show-prompt --program artifacts/api-gepa.json
uv run main.py report
```

Flags: `--config`, `--profile`, `--backend {nrp,openrouter,xai,nvidia}`,
`--task-model`, `--reflection-backend`, `--reflection-model`, `--auto`,
`--seed`, `--num-threads`, `--judge`, `--gepa-budget`,
`--workdir` / `--inputdir` / `--outputdir`.

```bash
# xAI-only
uv run main.py baseline --backend xai --reflection-backend xai

# Generate on OpenRouter, reflect on xAI
uv run main.py gepa --backend openrouter --reflection-backend xai \
  --reflection-model xai/grok-4 --gepa-budget 60
```

## Cost & comparison

Every run reports score + tokens + wall-clock. `compare` ranks branches and
writes `comparison-<profile>.json` plus `report-<profile>.md` under the
outputdir. Artifacts are named by **profile name** (`api-gepa.json`, …);
prefer a **dedicated `--workdir`** per goal so runs do not mix.

## Practical tips

- Cap GEPA with `--gepa-budget` on first runs.
- Curate scenarios (`gen-scenarios` then prune) before trusting MIPRO/GEPA.
- Match backend/seed/profile across branches when comparing.
- Provenance: `run-meta.json` / `run-log.jsonl` include config path, profile, and resolved model IDs.
