# QUICKSTART

Fast track to optimizing a Blueprint prompt for **one goal per run**.

## Mental model

- **One** optimizer harness (baseline / bootstrap / MIPRO / GEPA).
- **One active profile** = seed prompt + rubric + weights + scenarios.
- Change goals by changing the profile or pointing `--profile` / `--workdir` at a separate run — not by switching a multi-task product mode.

```text
config/
  default.yaml       # models + run knobs
  profile.yaml       # active goal (shipped default: API examples)
  profiles/          # optional recipes (api, metadata, …)
  prompts/*.md       # long seed / rubric text
```

## 1. Keys + deps

```bash
export NRP_API_KEY=...          # --backend nrp
export OPENROUTER_API_KEY=...   # openrouter
export XAI_API_KEY=...          # xai
export NVIDIA_API_KEY=...       # nvidia
# Ollama needs no key; optional: export OLLAMA_API_BASE=http://localhost:11434
uv sync                          # from repo root
cd src/promptOptimizer
```

> Only OpenRouter? `--backend openrouter --reflection-backend openrouter`  
> Only xAI? `--backend xai --reflection-backend xai`  
> Local Ollama? `ollama pull llama3.2` then  
> `--backend ollama --reflection-backend ollama`  
> (URL: `--api-base` or `OLLAMA_API_BASE`; model: `--task-model` / YAML)

## 2. Sanity check

```bash
uv run main.py baseline
```

Uses `config/profile.yaml` (API goal by default).

## 3. Scenarios + optimize

```bash
uv run main.py gen-scenarios --n 40
# prune artifacts/scenarios-api.json if needed
uv run main.py compare
```

## 4. A different goal = a different run

```bash
# Metadata-focused run, isolated artifacts
uv run main.py gen-scenarios --profile metadata --n 40 --workdir runs/meta-1
uv run main.py compare --profile metadata --workdir runs/meta-1

# Or promote a recipe to the active profile, then run as usual
cp config/profiles/metadata.yaml config/profile.yaml
uv run main.py compare --workdir runs/meta-2
```

## Edit the goal without code

```bash
$EDITOR config/profile.yaml           # weights, fields, scenario seeds
$EDITOR config/prompts/api.seed.md    # seed system prompt (path from profile)
$EDITOR config/prompts/api.rubric.md  # judge rubric
uv run main.py show-prompt
```

## Useful flags

| Flag | Role |
|---|---|
| `--profile name\|path` | Goal recipe (default: `config/profile.yaml`) |
| `--workdir DIR` | Isolate inputs/outputs for this run |
| `--backend` / `--task-model` | Generation LM |
| `--reflection-backend` / `--reflection-model` | Judge / GEPA reflection LM |
| `--api-base` | Override base URL (e.g. Ollama host) |
| `--gepa-budget N` | Cap GEPA rollouts |
| `--config DIR` | Alternate config root |

See `README.md` for scoring and architecture detail.
