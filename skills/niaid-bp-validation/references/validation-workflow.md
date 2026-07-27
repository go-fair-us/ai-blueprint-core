# Validation workflow — niaid-bp-validation

Load this file when running SHACL validation for a Blueprint `schema:Dataset` record.

## Goal

Check whether a Dataset graph satisfies the **required** constraints in
`assets/blueprint-required.ttl` using **pySHACL**. This is semantic validation
(cardinality, node kinds, string lengths) — not merely “is it valid JSON-LD syntax?”

## Prerequisites

```bash
# From the ai-blueprint-core repo root
uv sync --extra validation
```

## Inputs

| Input | Notes |
|-------|--------|
| **Data graph** | JSON-LD (preferred for this repo) or Turtle/N-Triples. Must type the focus node as `schema:Dataset` (`@type: Dataset` with `@context: https://schema.org/`). |
| **Shapes graph** | Default: `assets/blueprint-required.ttl`. Override with `--shape` only when the user supplies another shape. |

Resolve the data path from:

1. Skill invocation argument
2. A path or JSON-LD block in the user’s message
3. A file just produced by `niaid-bp-dataset-intake` or `niaid-bp-metadata-extract`
4. Ask once if none of the above is available

If the user pastes JSON-LD in chat, write it to a temp file (e.g.
`/tmp/dataset-to-validate.jsonld`) before calling the script.

## Command

`SKILL_DIR` is the absolute path to this skill directory (the folder containing
`SKILL.md`):

```bash
python SKILL_DIR/scripts/validate.py DATA.jsonld [--shape SHAPE.ttl] [--out-dir DIR]
```

Examples:

```bash
# Bundled shape, timestamped output dir in cwd
python skills/niaid-bp-validation/scripts/validate.py docs/example.json --out-dir /tmp/bp-val

# Explicit shape
python skills/niaid-bp-validation/scripts/validate.py record.jsonld \
  --shape skills/niaid-bp-validation/assets/blueprint-required.ttl \
  --out-dir ./validation_out
```

Exit code: `0` if zero **Violation** results, `1` otherwise.

## Outputs

| File | Content |
|------|---------|
| `report.ttl` | Full `sh:ValidationReport` graph (provenance / debugging) |
| `results.json` | One object per `sh:ValidationResult` (`severity`, `focus_node`, `result_path`, `message`, `source_constraint`, `value`, …) |
| `conforms.json` | `{ conforms, raw_conforms, n_violations, n_warnings, n_info, data_path, shape_path }` |

## schema.org HTTP vs HTTPS

JSON-LD parsers often expand `"@context": "https://schema.org/"` terms to
`http://schema.org/…` IRIs, while the bundled shape uses `https://schema.org/…`.
`scripts/validate.py` rewrites `http://schema.org/` → `https://schema.org/` on
the data graph before pySHACL runs so `sh:targetClass` and property paths match.
Without that rewrite, validation can silently report **false CONFORMS**.

## Conformance rule (important)

pySHACL’s raw `conforms` boolean is **False whenever any result exists**, including
`sh:Warning`. The skill’s summary field **`conforms` means: zero `sh:Violation`
results** (warnings do not fail the run). Always report both:

- **conforms** (blocking severity only) — primary verdict for the user
- **raw_conforms** (pySHACL boolean) — only if useful for debugging

## Shape coverage (initial)

`blueprint-required.ttl` is an **initial** shape based on Google Dataset required
fields (EarthCube `googleRequired.ttl`):

| Property | Constraint (summary) |
|----------|----------------------|
| `schema:name` | ≥1 non-empty literal |
| `schema:description` | ≥1 literal, length 50–5000 |
| `schema:url` | exactly 1 IRI or literal |

Future shape revisions may add Blueprint Table 1 elements (`identifier`,
`license`, `conditionsOfAccess`, author ORCID, …) as Violation or Warning shapes.

## How to present results to the user

1. State the verdict: **CONFORMS** or **NON-CONFORMING**.
2. Give counts: violations / warnings / info.
3. List each violation as a bullet: property path + message + focus node when useful.
4. Suggest concrete fixes (add missing `url`, lengthen `description`, …).
5. Offer re-validation after the user edits the record.
6. Point to artifact paths if files were written.

Do **not** invent metadata values to “make it pass.” Fix suggestions only.

## Sibling skills

| Skill | Relationship |
|-------|----------------|
| `niaid-bp-dataset-intake` | Interview → JSON-LD; validate the output |
| `niaid-bp-metadata-extract` | URL → JSON-LD; validate the draft record |
| `niaid-bp-fair-assess` | Broader repository gap interview; not a substitute for SHACL |
