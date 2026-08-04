## Repair task (validation iteration {{iteration}})

**Resource URL:** {{url}}

**Run directory:** {{run_dir}}

**Current record:** `{{run_dir}}/record.jsonld`

**SHACL results (this iteration):** `{{results_json}}`

**Conforms summary:** `{{conforms_json}}`

### Steps

1. Read `record.jsonld` and `results.json`.
2. For each **violation**, apply an evidence-safe fix (resource URL, page text, existing notes).
3. Write the updated JSON-LD back to `{{run_dir}}/record.jsonld`.
4. Confirm what you changed.

When the file is updated, stop. Do not start a new extraction from scratch unless the record is unusable.
