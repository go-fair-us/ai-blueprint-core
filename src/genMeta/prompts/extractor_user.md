## Extract task

**Resource URL:** {{url}}

**Run directory (write files here):** {{run_dir}}

### Steps

1. Read `skills/niaid-bp-metadata-extract/references/extraction-workflow.md` and follow its phases for this URL.
2. Fetch the resource page (and jina proxy if needed).
3. Write the Dataset JSON-LD to:

   `{{run_dir}}/record.jsonld`

4. Write metadata notes to:

   `{{run_dir}}/notes.md`

5. Confirm in your reply that both files exist and list which required-ish fields you populated (`name`, `description`, `url`, and any `identifier` / `license` / `conditionsOfAccess`).

Do not wait for other agents. When the files are written, you are done.
