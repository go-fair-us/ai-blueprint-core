# libraryOptimizer

Optimize **OKF library prompt examples** with **DSPy GEPA** so their instructions produce outputs aligned with the **NIAID Blueprint** and **Work Plans** guidance.

Simpler sibling of [`../promptOptimizer`](../promptOptimizer): one prompt in, GEPA only, judge-only metric, artifacts out (no multi-optimizer bake-off, no deterministic JSON-LD/OpenAPI checks).

## Mental model

1. Load an example from `okf/prompt_examples/` (YAML front matter stripped; body under `# Prompt` only).
2. That body becomes the DSPy Signature **seed instructions**.
3. LLM-generated **scenarios** drive train/val/test examples.
4. An LLM **judge** scores free-text artifacts against sliced local:
   - `docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`
   - `docs/WorkPlans/20260515_Work-Plans_Supplementary_DSJ.md`
5. **GEPA** rewrites the instructions; results land under `artifacts/` (or `--workdir`).

## Setup

From the repository root:

```bash
uv sync
```

| Env var | Used for |
|---|---|
| `NRP_API_KEY` | Default **task** and **reflection / judge** backend (`nrp`) |
| `OPENROUTER_API_KEY` | Optional `--backend openrouter` |
| `XAI_API_KEY` | Optional `--backend xai` |
| `OLLAMA_API_BASE` / `OLLAMA_HOST` | Optional local Ollama URL |

## Quickstart (NRP defaults)

Config defaults (both on NRP):

| Role | Backend | Model (LiteLLM id) |
|---|---|---|
| Task (artifact generation) | `nrp` | `custom_openai/glm-5` |
| Reflection + judge (GEPA) | `nrp` | `custom_openai/gpt-oss` |

Only `NRP_API_KEY` is required for the default path.

```bash
cd /path/to/ai-blueprint-core   # repo root
uv sync

export NRP_API_KEY=…            # task (glm-5) + reflection/judge (gpt-oss)

PROMPT=okf/prompt_examples/metadata-schema/core-elements/name-description.md
FLAGS="--prompt $PROMPT --num-threads 4 --seed 0"

# 1) See available OKF examples
uv run python src/libraryOptimizer/main.py list-prompts

# 2) Optional: inspect the seed (body only, no YAML front matter)
uv run python src/libraryOptimizer/main.py show-prompt $FLAGS

# 3) Optional: curate scenarios first (otherwise optimize auto-generates)
uv run python src/libraryOptimizer/main.py gen-scenarios $FLAGS --n 12

# 4) Score the unoptimized seed once (reference “before” number)
uv run python src/libraryOptimizer/main.py baseline $FLAGS

# 5) GEPA with a small rollout budget (demo-friendly)
uv run python src/libraryOptimizer/main.py optimize $FLAGS --gepa-budget 40

# 6) Print optimized instructions
uv run python src/libraryOptimizer/main.py show-prompt $FLAGS \
  --program src/libraryOptimizer/artifacts/metadata-schema-core-elements-name-description-gepa.json
```

Omit `--backend` / `--reflection-backend` to use the YAML defaults. Explicit form of the same thing:

```bash
uv run python src/libraryOptimizer/main.py optimize $FLAGS \
  --backend nrp --reflection-backend nrp \
  --task-model custom_openai/glm-5 \
  --reflection-model custom_openai/gpt-oss \
  --gepa-budget 40 --judge reflection
```

### Alternate recipes

```bash
# All OpenRouter (needs OPENROUTER_API_KEY)
uv run python src/libraryOptimizer/main.py optimize $FLAGS \
  --backend openrouter --reflection-backend openrouter --gepa-budget 40

# Override NRP model ids only
uv run python src/libraryOptimizer/main.py optimize $FLAGS \
  --backend nrp --reflection-backend nrp \
  --task-model custom_openai/glm-5 \
  --reflection-model custom_openai/gpt-oss \
  --gepa-budget 40

# Isolated workdir for a trial
uv run python src/libraryOptimizer/main.py optimize $FLAGS \
  --gepa-budget 40 --workdir src/libraryOptimizer/runs/name-desc-1
```

Artifacts land under `src/libraryOptimizer/artifacts/` (or `--workdir`). See [Artifacts](#artifacts) below.

## Quickstart (batch: all OKF prompts)

Use [`run_all_okf.sh`](run_all_okf.sh) to run **baseline + GEPA** over every filled example under `okf/prompt_examples/` (skips `README.md`). Runs are **sequential**, one workdir per prompt.

Defaults match `config/default.yaml`: **both backends = NRP** (task `glm-5`, reflection/judge `gpt-oss`).

```bash
cd /path/to/ai-blueprint-core   # repo root
uv sync

export NRP_API_KEY=…            # task + reflection / judge on NRP

# 1) Preview commands only (no API calls) — should list all 10 examples
DRY_RUN=1 ./src/libraryOptimizer/run_all_okf.sh

# 2) Pilot on one path substring before the full bundle
GEPA_BUDGET=20 N_SCENARIOS=8 ONLY=name-description ./src/libraryOptimizer/run_all_okf.sh

# 3) Full batch (baseline then optimize for each prompt)
./src/libraryOptimizer/run_all_okf.sh
```

### What the script does per prompt

1. Derive a slug from the path (e.g. `metadata-schema-core-elements-name-description`).
2. Use workdir `src/libraryOptimizer/runs/okf-batch/<slug>/`.
3. Optionally `gen-scenarios` if `GEN_SCENARIOS=1` (otherwise `optimize` auto-generates when missing).
4. Run `baseline` (unless `BASELINE=0`).
5. Run `optimize` with `--gepa-budget` / `--n` from env.
6. Append OK/FAIL to `batch-summary.txt`; full console capture in `batch.log`.

### Outputs

| Path | Content |
|---|---|
| `src/libraryOptimizer/runs/okf-batch/<slug>/` | Per-prompt scenarios, programs, optimized prompt, report |
| `…/batch.log` | Combined run log |
| `…/batch-summary.txt` | One line per prompt (`OK` / `FAIL`) |

Inspect one optimized prompt after a pilot:

```bash
uv run python src/libraryOptimizer/main.py show-prompt \
  --prompt okf/prompt_examples/metadata-schema/core-elements/name-description.md \
  --program src/libraryOptimizer/runs/okf-batch/metadata-schema-core-elements-name-description/metadata-schema-core-elements-name-description-gepa.json
```

### Env overrides

| Variable | Default | Meaning |
|---|---|---|
| `BACKEND` | `nrp` | Task LM (`glm-5` via config) |
| `REFLECTION_BACKEND` | `nrp` | GEPA reflection (+ judge); model `gpt-oss` via config |
| `JUDGE` | `reflection` | `reflection` or `task` |
| `GEPA_BUDGET` | `40` | Cap GEPA metric evaluations |
| `N_SCENARIOS` | `12` | Scenario count for gen / auto-gen |
| `NUM_THREADS` | `4` | Parallel eval threads |
| `SEED` | `0` | Data shuffle seed |
| `BASELINE` | `1` | `0` to skip baseline |
| `GEN_SCENARIOS` | `0` | `1` to call `gen-scenarios` before optimize |
| `DRY_RUN` | `0` | `1` print commands only |
| `ONLY` | *(empty)* | Path substring filter (e.g. `citation`) |
| `CONTINUE_ON_ERROR` | `1` | `0` abort on first failure |
| `RUNS_ROOT` | `src/libraryOptimizer/runs/okf-batch` | Batch output root |
| `EXAMPLES_ROOT` | `okf/prompt_examples` | Prompt tree |

Examples:

```bash
# All OpenRouter (no NRP)
BACKEND=openrouter REFLECTION_BACKEND=openrouter ./src/libraryOptimizer/run_all_okf.sh

# Faster / cheaper demo
BASELINE=0 GEPA_BUDGET=20 N_SCENARIOS=8 ./src/libraryOptimizer/run_all_okf.sh

# Pre-generate scenarios, then optimize
GEN_SCENARIOS=1 ./src/libraryOptimizer/run_all_okf.sh
```

Expect a full 10-prompt run with GEPA to take a long time and use many API calls; start with `DRY_RUN=1` and `ONLY=…` pilots.

## CLI reference

```bash
# From repo root
uv run python src/libraryOptimizer/main.py list-prompts

uv run python src/libraryOptimizer/main.py gen-scenarios \
  --prompt okf/prompt_examples/metadata-schema/core-elements/name-description.md \
  --n 20

uv run python src/libraryOptimizer/main.py baseline \
  --prompt okf/prompt_examples/metadata-schema/core-elements/name-description.md

uv run python src/libraryOptimizer/main.py optimize \
  --prompt okf/prompt_examples/metadata-schema/core-elements/name-description.md \
  --gepa-budget 40

uv run python src/libraryOptimizer/main.py show-prompt \
  --prompt okf/prompt_examples/metadata-schema/core-elements/name-description.md

uv run python src/libraryOptimizer/main.py show-prompt \
  --prompt okf/prompt_examples/metadata-schema/core-elements/name-description.md \
  --program src/libraryOptimizer/artifacts/<slug>-gepa.json
```

`optimize` **auto-generates scenarios** if none exist for that slug.

### Useful flags

| Flag | Meaning |
|---|---|
| `--prompt PATH` | OKF example markdown |
| `--gepa-budget N` | Cap GEPA metric evaluations (rollouts) |
| `--workdir DIR` | Isolate inputs/outputs |
| `--blueprint-path` / `--workplans-path` | Override guidance docs |
| `--refresh-guidance` | Rebuild `guidance.md` cache |
| `--backend` / `--reflection-backend` | LM providers from `config/default.yaml` |

## Artifacts

Under `artifacts/` (or workdir):

| File | Content |
|---|---|
| `scenarios-<slug>.json` | Scenario pack |
| `guidance.md` | Sliced Blueprint + Work Plans for the judge |
| `<slug>-baseline.json` | Seed program (optional baseline command) |
| `<slug>-gepa.json` | GEPA-compiled program |
| `<slug>-optimized-prompt.md` | Human-readable optimized instructions |
| `report-<slug>.md` | Short score / path report |

## Tests

```bash
uv run pytest src/libraryOptimizer/tests -q
```

No API keys required for unit tests.

## Contrast with promptOptimizer

| | libraryOptimizer | promptOptimizer |
|---|---|---|
| Input | One OKF library prompt example | Profile seed + rubric recipes |
| Optimizers | GEPA (+ optional baseline score) | baseline, bootstrap, MIPRO, GEPA, compare |
| Metric | LLM judge only | Weighted checks + judge |
| Guidance | Blueprint **and** Work Plans (local, sliced) | Blueprint only |
| Output | Optimized prompt markdown + program JSON | Comparison table + multi-branch artifacts |

## Layout

```
main.py
config/default.yaml
defs/          # load_prompt, guidance, lm, metric, dataset, …
optimize/      # gepa, baseline
tests/
artifacts/
```
