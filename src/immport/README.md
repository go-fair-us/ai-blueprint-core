# ImmPort RA + ELISA search

This script finds ImmPort studies and subjects that match a filter set. The default filter is rheumatoid arthritis, female, ELISA, Homo sapiens.

It needs only Python 3. You do not install extra packages.

Search is public. Study summaries and ELISA result rows need an ImmPort API key.

## What you get

A default run prints matching studies and subjects.

Each study line shows accession, title, PI, assays, and DOI. Each subject line shows accession, study, age, race, and ethnicity.

With a key, the script also prints the study summary. With `--elisa`, it also pulls ELISA result rows and keeps the female rows.

The last check of the default filter found one study: `SDY473` (Lovastatin in RA). That search returned 60 female subjects. The ELISA pull returned 3302 female rows.

## Get an API key

You need a key only for summaries and ELISA rows.

1. Open https://www.immport.org/auth/api/keys
2. Sign in and download the JSON key file
3. Copy the `api_key` string from that file. Do not paste the whole JSON object if you can avoid it. The script can unwrap a full JSON blob if you do.

## Set the key

Pick one method.

**Environment variable (best):**

```bash
export IMMPORT_API_KEY='paste-the-api_key-string-here'
```

**Path to the downloaded JSON file:**

```bash
export IMMPORT_API_KEY=/path/to/immport-key.json
```

**Command line:**

```bash
python3 src/immport/search_ra_elisa.py --api-key 'paste-the-api_key-string-here'
```

**`.env` file** in the repo root or in `src/immport/`:

```
IMMPORT_API_KEY=paste-the-api_key-string-here
```

The repo already ignores `.env`. Do not commit the key.

## Run the script

From the repo root:

```bash
# public search only
python3 src/immport/search_ra_elisa.py

# search plus study summary plus ELISA rows
python3 src/immport/search_ra_elisa.py --elisa

# write the full payload to a file
python3 src/immport/search_ra_elisa.py --elisa --json /tmp/ra-elisa.json
```

If `python3` is not on your PATH, use the Python 3 binary you have.

## Change the filter

The defaults match the RA + female + ELISA search. You can replace any of them:

```bash
python3 src/immport/search_ra_elisa.py \
  --condition "systemic lupus erythematosus" \
  --sex Female \
  --assay ELISA \
  --species "Homo sapiens"
```

| Flag | Default | Role |
|---|---|---|
| `--condition` | `rheumatoid arthritis` | ImmPort disease name |
| `--sex` | `Female` | ImmPort sex value |
| `--assay` | `ELISA` | ImmPort assay method |
| `--species` | `Homo sapiens` | ImmPort species |
| `--page-size` | `100` | Max search hits to return |
| `--elisa` | off | Pull ELISA rows (needs a key) |
| `--json PATH` | off | Write the full result as JSON |
| `--api-key` | `$IMMPORT_API_KEY` | Key string or path to the JSON file |

Use the exact ImmPort vocabulary values. A wrong disease or assay name returns zero hits with no extra error.

## Notes

- The ImmPort ELISA endpoint fails if you send `sex=` on the URL. The script downloads the study ELISA table and then keeps the female rows.
- Search can return more subjects than `--page-size`. Raise `--page-size` (max 1000) or write `--json` and count the `subject_total` field.
- A study that lists ELISA can still have sparse parsed rows. Zero ELISA rows means ImmPort has not loaded that table, not that the study has no ELISA files.
