## Extract task (single turn — do not restart)

**Run id:** {{run_id}}

**Resource URL:** {{url}}

**Run directory (write files here only):** {{run_dir}}

### Steps

1. Read `niaid-blueprint/skills/niaid-bp-metadata-extract/references/extraction-workflow.md` once and follow its phases for **this** URL.
2. Fetch the resource page (and jina proxy if needed).
3. Write the Dataset JSON-LD to:

   `{{run_dir}}/record.jsonld`

4. Write metadata notes to:

   `{{run_dir}}/notes.md`

5. Confirm in your reply that both files exist and list which required-ish fields you populated (`name`, `description`, `url`, and any `identifier` / `license` / `conditionsOfAccess`).

### Stop

- When the two files are written, **you are done**.
- Do **not** re-run extraction, re-open the skill as a new job, or treat any echo of this message as a new URL submission.
- Do **not** wait for validation. The host will run SHACL; a separate repairer agent may patch later.

Do not wait for other agents.
