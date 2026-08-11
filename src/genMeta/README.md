# genMeta — extract, validate, repair

## What this is

**genMeta** is a small orchestrator that turns a **public resource URL** into a
**Blueprint-oriented schema.org Dataset JSON-LD** record, then **checks** that
record with **SHACL** and, if needed, asks an agent to **fix** it until the
check passes (or a retry budget runs out).

It answers a practical need: the extract skill
(`niaid-blueprint/skills/niaid-bp-metadata-extract/`) can draft rich metadata from a page, but
drafts are uneven—missing `url`, a too-short `description`, broken structure.
genMeta keeps the LLM where it helps (reading the web, drafting and patching
JSON-LD) and keeps **conformance** where it is reliable: a **deterministic
host-side validator**, not another model claiming “this looks fine.”

This is **not Hermes**. Transport is **Herdr** (Unix socket client) with **Pi**
agents in panes. Pattern adapted from coffeenotes `python_herdr` (Herdr 0.7.x +
Pi).

For the broader “why URL extraction” story, see
[`docs/metadataGeneration.md`](../../docs/metadataGeneration.md).

## The idea in one picture

```text
                    ┌─────────────────────────────────────┐
  resource URL ──►  │  Pi: genmeta-extractor (once only)  │
                    │  (follow niaid-bp-metadata-extract) │
                    └─────────────────┬───────────────────┘
                                      │ writes (barrier)
                                      ▼
                              record.jsonld + notes.md
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  Host Python (no LLM)               │
                    │  pySHACL + blueprint-required.ttl   │
                    │  → validation/iter-NN/…             │
                    └─────────────────┬───────────────────┘
                                      │
                    conforms? ──yes──► final-report.md (done)
                         │
                         no (and iters left)
                         ▼
                    ┌─────────────────────────────────────┐
                    │  Pi: genmeta-repairer               │
                    │  patches record from SHACL results  │
                    │  (does not re-extract)              │
                    └─────────────────┬───────────────────┘
                                      │ record mtime advances
                                      └──► host validate again
```

**Handoff rules**

1. Extract is a **single** prompt. The orchestrator waits for `record.jsonld` +
   `notes.md` on disk (not a flaky Herdr idle alone), then never re-submits the URL.
2. **SHACL always runs on the host** (deterministic). The second agent is a
   **repairer**, not a second extractor and not the SHACL engine.
3. Repair waits for `record.jsonld` to be rewritten, then host validates again.

| Who | Role |
|-----|------|
| **You / CLI** | Supply `--url`; receive a run directory and exit code |
| **Herdr** | Workspace, panes, agent aliases (`genmeta-extractor`, `genmeta-repairer`) |
| **Pi extractor** | Fetch page (jina fallback if needed); write `record.jsonld` + `notes.md` |
| **Host `validate_host`** | Import `niaid-blueprint/skills/niaid-bp-validation/scripts/validate.py`; run **pySHACL** |
| **Pi repairer** | Read SHACL `results.json`; evidence-safe edits only; overwrite `record.jsonld` |

Orchestration lives in `main.py`. Agents never run SHACL themselves; the host
always re-validates after extract and after each repair.

## How SHACL is used

**Yes — SHACL is central to the loop**, but only as a **host-side quality gate**,
not as something the LLM “implements.”

### What runs

1. After extraction (and after each repair), `defs/validate_host.py` calls
   `run_validation()` from
   `niaid-blueprint/skills/niaid-bp-validation/scripts/validate.py`.
2. That loads the data graph from `record.jsonld` and the shapes graph from
   `niaid-blueprint/skills/niaid-bp-validation/assets/blueprint-required.ttl`.
3. **[pySHACL](https://github.com/RDFLib/pySHACL)** evaluates the shapes and
   writes three artifacts under `validation/iter-NN/`:
   - `report.ttl` — full SHACL validation report
   - `results.json` — normalized findings for the repairer
   - `conforms.json` — summary including the boolean the loop uses

### What “conforms” means

The starter shape uses **`sh:Violation`** severity for required constraints.
**Conforms** means **zero Violation results** (warnings alone would not block,
but the current starter shape is almost all violations).

The process exit code is **0** if the final iteration conforms, **1** otherwise
(still writes `final-report.md`).

### What the starter shape actually checks

`blueprint-required.ttl` is an **initial** Dataset shape (inspired by Google
Dataset / EarthCube “required” constraints), **not** full Blueprint Table 1:

| Constraint | Rule (simplified) |
|------------|-------------------|
| `schema:name` | Required, non-empty literal |
| `schema:description` | Required literal, length **50–5000** |
| `schema:url` | Required landing-page IRI or literal (exactly one) |

Passing SHACL here means: “this JSON-LD is a minimally usable Dataset shell for
downstream tooling.” It does **not** mean every Blueprint element (DOI, ORCID,
license, infectiousAgent, …) is present or correct. The extractor still tries
to populate Table 1 from the page; SHACL only **forces** the three required
fields above (and structural alignment with `schema:Dataset`).

The shape file itself notes that later revisions can add more Table 1
properties as Violations or Warnings. genMeta will pick those up automatically
when the shape file grows—no orchestrator change required beyond re-running.

### How SHACL drives repair

When validation **fails**:

1. The host does **not** invent fixes.
2. The **repairer** agent receives paths to `results.json` and `conforms.json`.
3. It patches `record.jsonld` using **on-page evidence** (or the known resource
   URL for `url`)—same “never invent PIDs” rules as extract.
4. The host runs pySHACL again.

Typical first failures: missing `url`, description shorter than 50 characters.
The extractor prompt already steers toward those requirements so fewer repair
rounds are needed.

### What SHACL is *not* doing in genMeta

- Not run inside the Pi agent REPL as a tool call (host only).
- Not a FAIR assessment or a full Blueprint interview.
- Not a guarantee of Portal-ready completeness.
- Not Hermes or a multi-optimizer GEPA loop (see `src/libraryOptimizer/` for
  that family of work).

## Prerequisites

1. **Herdr** running (`herdr` or `herdr server &`)
2. **Pi** available to Herdr (`kind=pi`)
3. Python deps (includes validation stack used by the host):

```bash
# from ai-blueprint-core repo root
uv sync --extra genmeta
```

(`genmeta` depends on the same pySHACL path as `uv sync --extra validation`.)

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

## Pipeline (code map)

```text
URL → [Pi extractor] → record.jsonld
    → [host pySHACL] → validation/iter-NN/
    → if fail: [Pi repairer] patches record.jsonld → re-validate
    → final-report.md
```

| Step | Code | Prompts / assets |
|------|------|------------------|
| Extract | `main.py` phase 1 | `prompts/extractor_*.md` → skill `niaid-bp-metadata-extract` |
| Validate | `defs/validate_host.py` | `validate.py` + `blueprint-required.ttl` |
| Repair | `main.py` phase 3 | `prompts/repairer_*.md` + SHACL `results.json` |
| Report | `defs/report.py` | `final-report.md` |

Default models (overridable): both agents `xai-auth/grok-4.5`. Default max
validate/repair iterations: **3**.

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
  tests/          # unit tests (e.g. artifact helpers)
```

## Troubleshooting

| Symptom | What to try |
|---------|-------------|
| Herdr not reachable | `herdr` or `herdr server &` |
| `invalid_agent_argument` / “cannot be encoded safely” | System prompt must be a **file path** to `--append-system-prompt` (genMeta does this). Multi-line text args are rejected by Herdr. |
| `agent_name_taken` | `GENMETA_CLOSE_STALE=1` or `herdr agent rename genmeta-extractor --clear` |
| OpenRouter fails in pane | Export key **before** starting Herdr; restart Herdr |
| No `record.jsonld` | Check `01-extractor.txt`; orchestrator tries to recover fenced JSON |
| Extract “starts over” / never validates | Fixed by artifact barriers: completion = files on disk, extract not re-submitted. Ensure prompts are current. |
| Iterations = 0 in report but files exist | Orchestrator exited before host SHACL (old settle bug). Re-run with current main. |
| Always NON-CONFORMING | Inspect `validation/iter-*/results.json`; often short description or missing url |
| `pyshacl` import errors | `uv sync --extra genmeta` (or `--extra validation`) from repo root |

## Skills used as instructions

Skills live under the agent plugin package (not repo-root `skills/`):

- `niaid-blueprint/skills/niaid-bp-metadata-extract/` — what to extract and how (Table 1 mapping, PID rules)
- `niaid-blueprint/skills/niaid-bp-validation/` — host SHACL runner and starter shape

Related docs:

- `docs/metadataGeneration.md` — human-oriented URL extraction overview
- `niaid-blueprint/skills/niaid-bp-validation/references/validation-workflow.md` — SHACL workflow detail
