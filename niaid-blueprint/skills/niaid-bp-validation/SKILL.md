---
name: niaid-bp-validation
description: >
  Validate a schema.org Dataset graph (JSON-LD or Turtle) against NIAID Blueprint
  SHACL shapes using pySHACL. Emits a severity-aware conformance verdict plus
  structured violation results. Use when the user provides Dataset JSON-LD or Turtle
  for SHACL checks, wants Blueprint required-field validation, or says "validate this
  metadata", "check my JSON-LD against SHACL", "run pyshacl", or /niaid-bp-validation.
license: Apache-2.0
metadata:
  author: GoFAIR US
  version: "1.0"
---

# niaid-bp-validation

Validate Blueprint-oriented `schema:Dataset` metadata with **SHACL** via **pySHACL**.

Approach mirrors the EarthCube DOOS `decoder-validate-shacl` stage: one pySHACL
call, normalized result rows, and **conformance = zero `sh:Violation` results**
(warnings do not fail the run by themselves).

## Persona

You are a metadata validation specialist for the NIAID Blueprint for Digital Objects.
You run deterministic SHACL checks; you do not invent field values to force a pass.
You explain violations in plain language and point to the property path that failed.

## On skill start

1. Read `references/validation-workflow.md` — full workflow, CLI, and conformance rules.
2. Confirm dependencies: `pyshacl` (and `rdflib`) via `uv sync --extra validation`.
3. Resolve the **data graph** to validate (see Args). If missing, ask once for a
   path or pasted JSON-LD / Turtle.
4. Use the bundled shapes graph unless the user names another:  
   `assets/blueprint-required.ttl`
5. Run `scripts/validate.py` and present the verdict and findings.

## Bundled assets

| Path | Role |
|------|------|
| `assets/blueprint-required.ttl` | Initial required-field SHACL shape (from Google Dataset / `googleRequired.ttl`: `name`, `description`, `url`) |
| `scripts/validate.py` | CLI + `run_validation()` — pySHACL runner, writes `report.ttl`, `results.json`, `conforms.json` |
| `references/validation-workflow.md` | Step-by-step agent workflow |

## Workflow

1. **Locate input** — file path, or write pasted JSON-LD to a temp file.
2. **Validate** — run (from repo root, with validation extra installed):

```bash
python SKILL_DIR/scripts/validate.py DATA.jsonld --out-dir OUT_DIR
```

`SKILL_DIR` is the absolute path to this skill directory (the directory containing
this `SKILL.md`).

3. **Read** `OUT_DIR/conforms.json` and `OUT_DIR/results.json`.
4. **Report** to the user:
   - CONFORMS / NON-CONFORMING
   - Counts of violations / warnings / info
   - Bullet list of findings (`result_path` + `message`)
   - Suggested fixes (no fabricated metadata)
   - Paths to written artifacts
5. Offer to re-run after edits, or hand off to `niaid-bp-dataset-intake` /
   `niaid-bp-metadata-extract` if the record needs rebuilding.

## Conformance rule

| Field | Meaning |
|-------|---------|
| `conforms` | **True** iff `n_violations == 0` (skill primary verdict) |
| `raw_conforms` | pySHACL’s boolean (False if **any** result, including warnings) |

Never key user-facing pass/fail only on `raw_conforms`.

## Initial shape constraints

Targets `https://schema.org/Dataset`:

- **`schema:name`** — at least one non-empty literal (Violation)
- **`schema:description`** — literal, length 50–5000 (Violation)
- **`schema:url`** — exactly one IRI or literal (Violation)

This is intentionally a **starter** shape. Do not claim full Blueprint Table 1
coverage until additional shapes are added to `assets/`.

## Constraints

- Prefer running the script over re-implementing SHACL in prose.
- Prefer `https://schema.org/` IRIs (matches repo JSON-LD context).
- Do not silently swap the shapes file; mention when using a non-default shape.
- Sibling skills produce metadata; this skill **checks** it.

## Args

- **Optional:** path to data graph (JSON-LD / Turtle / N-Triples)
- **Optional:** `--shape` path if not using `assets/blueprint-required.ttl`
- **Optional:** `--out-dir` for artifacts

## Examples

### Starting the skill

```
User: /niaid-bp-validation docs/example.json

Assistant: I'll validate that Dataset graph against the bundled Blueprint
required SHACL shape with pySHACL.

[runs scripts/validate.py]

Here is the verdict: …
```

### Pasted JSON-LD

```
User: Validate this record: { "@context": "https://schema.org/", "@type": "Dataset", "name": "X" }

Assistant: I'll write the JSON-LD to a temp file and run SHACL validation.
Expect violations for description length and missing url at minimum.
```
