## Repair task (validation iteration {{iteration}})

**Run id:** {{run_id}}

**Resource URL (context only — do not re-extract from scratch):** {{url}}

**Run directory:** {{run_dir}}

**Current record:** `{{run_dir}}/record.jsonld`

**SHACL results (this iteration — host already ran pySHACL):** `{{results_json}}`

**Conforms summary:** `{{conforms_json}}`

### Steps

1. Read `record.jsonld` and `results.json`.
2. For each **violation**, apply an evidence-safe fix (resource URL, page text, existing notes).
3. Write the updated JSON-LD back to `{{run_dir}}/record.jsonld` (must change the file).
4. Confirm what you changed.

### Stop

When the file is updated, **stop**. Do not start a new extraction. Do not re-run SHACL. Wait for a later host message if another repair iteration is needed.
