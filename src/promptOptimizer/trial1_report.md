# Trial 1 — Blueprint API prompt optimization (demo run)

**Date:** 2026-07-10 (prep and failed long runs 2026-07-09)  
**Task:** `api` — NIAID Blueprint-aligned API examples (schema.org JSON-LD + OpenAPI + PIDs)  
**Location:** `src/promptOptimizer`  
**Status:** Successful **short** OpenRouter trial after abandoning an overnight NRP run  

This note captures the commands that worked for a **presentable, finite-time** experiment and the observations made along the way. It is a run log / lessons doc, not a substitute for a full multi-seed bake-off.

---

## 1. Context and goals

### What we were optimizing
DSPy optimizes a **program** (seed instructions ± few-shot demos) against a **metric** on scenarios. Branches compared conceptually:

| Branch | Mechanism |
|--------|-----------|
| **baseline** | Seed signature only (no demos, no instruction rewrite) |
| **bootstrap** | BootstrapFewShot — teacher demos filtered by metric |
| **gepa** | GEPA — reflective instruction search with a rollout budget |

MIPROv2 was **skipped** for this trial (too expensive for a demo window).

### What “good” meant for Trial 1
- Finish in **hours, not overnight**
- Use a **stable** provider (OpenRouter), not flaky NRP overnight
- Show **metric headroom** (baseline not stuck at ~0.98)
- Show that optimizers **change something visible** (demos and/or rewritten instructions)
- Prefer **interpretable** artifacts (`show-prompt`, saved JSON) over a single leaderboard number

---

## 2. Setup that made the trial viable

### Metric and seed (from prior work in this repo)
Earlier runs hit a **score ceiling (~0.96+)** when the seed listed every Table 1 field and checks were too soft. Before Trial 1, the codebase was adjusted so that:

- Seed instructions are **short and generic** (~524 characters) — goals only, not a full checklist  
- Scoring is **strict**: Table 1 keys + formats (DOI/ORCID/ROR/NCIT/…), graded JSON-LD/OpenAPI, scenario-relevant paths, filler penalties, reflection judge by default  
- Data split is **train / val / test** (GEPA/MIPRO get an explicit val set; final scores use held-out test)  
- Task LM **temperature 0.0**, higher `max_tokens` (16k) to reduce truncation  

**Implication for demos:** a baseline in the **~0.4** range is a feature (room to improve), not a failure.

### Providers
| Role | Trial 1 choice | Why |
|------|----------------|-----|
| Task (generation) | OpenRouter | NRP timed out overnight; OpenRouter finished runs in tens of minutes per branch |
| Judge / GEPA reflection | OpenRouter (`--judge reflection`) | Stronger, less self-grading than task-only judge |
| Avoided for Trial 1 | NRP as long-running backend | ~16h run aborted after service timeouts; risk of incomplete optimizer state |

Env for this recipe:

```bash
export OPENROUTER_API_KEY=...
cd src/promptOptimizer
```

---

## 3. Data

| Item | Trial 1 |
|------|---------|
| Scenario file | `artifacts/scenarios-api.json` |
| Count | **~27–28** curated scenarios (expanded from a 12-scenario smoke set; full earlier sets were ~40) |
| Split (approx., seed 0) | ~50% train / 25% val / 25% test → on the order of **~14 train / ~7 val / ~7 test** |
| GEPA Pareto / val size | Log reported **7 examples** for Pareto tracking |

Smaller than a production study, large enough that val/test are not 2–3 noisy points only.

---

## 4. Commands run (Trial 1 recipe)

Shared flags used for the successful series:

```bash
FLAGS="--backend openrouter --reflection-backend openrouter --judge reflection --auto light --num-threads 4 --seed 0"
```

### 4.1 Baseline

```bash
uv run main.py baseline $FLAGS
```

**Artifact:** `artifacts/api-baseline.json` (mtime ~2026-07-10 08:13)  
**Expected shape:** seed instructions unchanged, **0 demos**.

### 4.2 Bootstrap

```bash
uv run main.py bootstrap $FLAGS
```

**Artifact:** `artifacts/api-bootstrap.json` (mtime ~2026-07-10 08:41)  
**Expected shape:** seed instructions **unchanged**, few-shot **demos** attached if the metric threshold is met.

### 4.3 GEPA (capped budget)

```bash
uv run main.py gepa $FLAGS --gepa-budget 60
```

**Artifact:** `artifacts/api-gepa.json` (mtime ~2026-07-10 10:09)  
**Budget:** ~**60 metric calls** (not unbounded `--auto light` alone, which can still be large).  
**Log (start):** ~2.86 full evals over train+val; Pareto on **7** val examples.

### 4.4 Inspect prompts (no API keys)

```bash
uv run main.py show-prompt --task api --program artifacts/api-baseline.json
uv run main.py show-prompt --task api --program artifacts/api-bootstrap.json
uv run main.py show-prompt --task api --program artifacts/api-gepa.json
```

### 4.5 Generated report helper

```bash
uv run main.py report --task api
```

Writes `artifacts/report-api.md` from comparison JSON + saved programs.  
**Caution:** if `artifacts/comparison-api.json` is from an **older** run (different metric/seed), the **score table** in that markdown can be stale even when the **prompt sections** reflect current programs. Prefer the scores printed by each `uv run main.py …` invocation for Trial 1.

---

## 5. What each branch produced (artifacts)

Verified from saved programs after Trial 1:

| Branch | Instruction vs seed | Few-shot demos | Notes |
|--------|---------------------|----------------|-------|
| **baseline** | Same (~524 chars) | 0 | Pure seed reference |
| **bootstrap** | Same | **4** | Added scenario demos only; does not rewrite the signature docstring |
| **gepa** | **Rewritten** (~4.7k chars) | 0 | Instruction now enumerates Table 1 fields, PID/ontology formats, OpenAPI constraints, anti-placeholder rules |

### Bootstrap demos (inputs only; abbreviated)
- Malaria vector surveillance — structured metadata API for collection sites  
- Allergen epitopes — content negotiation (e.g. RDF/XML)  
- Sepsis clinical store — resolvable PIDs under storage change  
- Immunogenetics / HLA — pagination for large allele-frequency queries  

### GEPA instruction (qualitative)
GEPA recovered much of the **checklist** that had been removed from the seed on purpose: explicit Table 1 properties, DOI/ORCID/ROR/NCIT/NCBITaxon/MONDO/SPDX-style formats, array-shaped fields, scenario-specific server URLs, ban on `example.org`-style hosts, and a tight output shape (JSON-LD + OpenAPI fences). That is exactly the kind of **instruction search** outcome GEPA is for—especially when the seed is intentionally thin.

---

## 6. Observations from the run logs

### 6.1 Baseline band (hard metric + OpenRouter)
An earlier OpenRouter baseline under the hardened metric landed around **~0.44** mean on the held-out test set (e.g. `4.39 / 10` → **0.439** on a 10-example test when scenarios were larger).  

GEPA’s **Iteration 0** full-val score on **7** examples was about **0.408** — consistent with “seed is mediocre, headroom exists.”

### 6.2 GEPA search dynamics (during the budgeted run)
From console logs mid-run:

| Signal | Observation |
|--------|-------------|
| Budget | `Running GEPA for approx 60 metric calls` — flag honored |
| Val size | `Using 7 examples for tracking Pareto scores` |
| Base | Iteration 0 ~**0.408** mean on full val |
| Subsample vs val | Minibatch **`/ 3`** scores are **sums** on 3 examples used to accept/reject mutations; **program scores** like `0.93` are means on the **full 7-val** set for Pareto selection |
| Skip example | `New subsample score 2.615 is not better than old score 2.619, skipping` — child lost a photo-finish on 3 points; normal |
| Progress | Later iterations selected **program 1** with a much higher val mean (~**0.93** in log) and **proposed new text** for `generate.predict` |
| Warning | `pred_name` score mismatch — expected with holistic LLM-judge metrics; GEPA uses module-level score |

**Pareto (in this context):** keep multiple non-dominated programs across **per-example val scores**, not only the single best average—so search does not discard specialists too early.

### 6.3 Runtime
- OpenRouter **baseline / bootstrap**: on the order of **~20–40+ minutes** each in the successful regime (far better than NRP multi-hour hangs).  
- GEPA with **budget 60**: on the order of **~1–2 hours** wall clock in this trial (e.g. ~63% budget at ~42 minutes mid-log; artifact written ~10:09 after ~08:50 start).  
- Failed NRP path: **~16 hours** then stop due to timeouts — **not** used for Trial 1 claims.

### 6.4 Bootstrap “no improvement” on smaller sets
On a **very small** scenario cut (e.g. 12) with free OpenRouter models, Bootstrap often:

- Keeps the **same instruction**, and/or  
- Adds demos that **do not move** a hard structural metric much  

That is expected: Bootstrap does not rewrite instructions. **GEPA** is the branch that demonstrated clear **prompt growth** in Trial 1.

### 6.5 Token / cost metering
Free OpenRouter models reported **$0** cost in earlier comparisons. Prompt-token totals can look low relative to judge context size depending on provider usage reporting—treat cost columns as approximate on free endpoints.

### 6.6 Operational lessons
1. **Do not trust a half-finished overnight NRP optimize** after timeouts—prefer a clean short re-run.  
2. **Cap GEPA** with `--gepa-budget` for demos.  
3. **Match flags** (`--backend`, `--reflection-backend`, `--seed`, `--task`) across branches.  
4. **Inspect programs** (`show-prompt`) as carefully as scores.  
5. **Stale `comparison-api.json`** can make `report` show old ~98% scores from the pre-hardening era—do not mix those numbers with Trial 1.

---

## 7. How to talk about Trial 1 (suggested narrative)

> We optimize Blueprint API prompts with DSPy against a strict, multi-part metric (JSON-LD structure, Table 1 coverage and formats, OpenAPI scenario fit, PIDs, plus an LLM judge). The seed prompt is intentionally short so optimizers have room to work. On OpenRouter, with ~28 scenarios and a 60-rollout GEPA budget, a baseline sits around the low-to-mid **0.4** range on validation during search; Bootstrap mainly adds few-shot demos; GEPA rewrites the instruction into a detailed Blueprint checklist. That is a finite-time demonstration of the pipeline without an overnight multi-optimizer bake-off on NRP.

Emphasize **process + artifacts**, not a claim that one optimizer always wins on all seeds and models.

---

## 8. Reproduce Trial 1

```bash
cd src/promptOptimizer
export OPENROUTER_API_KEY=...

# Ensure scenarios-api.json has ~25–30 scenarios
FLAGS="--backend openrouter --reflection-backend openrouter --judge reflection --auto light --num-threads 4 --seed 0"

uv run main.py baseline  $FLAGS
uv run main.py bootstrap $FLAGS
uv run main.py gepa      $FLAGS --gepa-budget 60

uv run main.py show-prompt --task api --program artifacts/api-baseline.json
uv run main.py show-prompt --task api --program artifacts/api-bootstrap.json
uv run main.py show-prompt --task api --program artifacts/api-gepa.json
```

Optional: record the three printed `score=` lines into a small table by hand, or re-run `compare` later when a long stable window exists (still skip or budget-limit expensive branches as needed).

---

## 9. Artifacts checklist (this trial)

| Path | Role |
|------|------|
| `artifacts/scenarios-api.json` | Scenario corpus (~28) |
| `artifacts/api-baseline.json` | Seed program |
| `artifacts/api-bootstrap.json` | Seed + up to 4 demos |
| `artifacts/api-gepa.json` | GEPA-rewritten instructions |
| `artifacts/report-api.md` | Human-readable dump (verify scores aren’t from an old comparison) |
| `trial1_report.md` | This document |

---

## 10. Follow-ups (not part of Trial 1)

- Re-run with a **fresh** `compare` after deleting or archiving stale `comparison-api.json` so the scoreboard matches the hard metric.  
- Try **`--gepa-budget 80–120`** or a stronger **paid** task model if free models plateau.  
- Add a second seed (`--seed 1`) to see variance on the small test set.  
- Vendor Blueprint load offline (local `docs/BluePrint/…`) so judge context never depends on GitHub mid-run.  
- Only then consider MIPROv2 on a stable backend with a clear time box.

---

*Documented from Trial 1 commands, console observations, and post-run inspection of saved programs in `src/promptOptimizer`.*
