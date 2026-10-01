# CEDAR extract

Turn a landing-page URL (and optional local documents) into a **CEDAR template instance** that matches `example.json`.

The language model fills a typed `DatasetRecord`. Host Python fetches pages with a **local Obscura** binary, caps the crawl, drops identifiers that never appeared in the fetched text, and writes JSON-LD. Missing evidence stays missing.

This is not genMeta (Herdr + schema.org + SHACL repair) and not a CEDAR upload client.

## Honesty rule

Empty is success. An invented ORCID, ROR, DOI, grant number, or ontology IRI is a failure. After extraction, the host deletes any identifier that does not appear in the fetched markdown or embedded JSON-LD.

## Requirements

- Python env from the repo root (`uv sync`; `dspy` is already a dependency).
- [Obscura](https://github.com/h4ckf0r0day/obscura) CLI on disk. Default path:

  `/home/fils/src/git/obscura/target/release/obscura`

  Override with `OBSCURA_BIN` or `--obscura-bin`. There is no jina.ai / third-party render fallback.
- An LM API key for `--backend nrp|openrouter|xai`, or a local Ollama daemon.

## Run

```bash
uv run python src/cedar/main.py extract \
  --url https://accessclinicaldata.niaid.nih.gov/study-viewer/clinical_trials/NCT04640168 \
  --out /tmp/cedar-run \
  --backend nrp \
  --max-depth 2 \
  --max-pages 5 \
  --debug
```

`--debug` prints timestamped progress (Obscura fetch, gather, each extract, write). With `--max-depth 0` or `--max-pages 1` the ReAct gatherer is skipped.

`--compare example.json` prints a payload field table (gold vs this run) after extract and writes `compare.md` in `--out`.

Writes:

- `record.jsonld` — CEDAR instance (`@context` copied from `example.json`)
- `notes.md` — found / missing / ungrounded / unreadable pages

Fetch only (no LM):

```bash
uv run python src/cedar/main.py extract \
  --url https://example.com \
  --out /tmp/cedar-dry \
  --dry-run
```

Local documents (do not count against the web page budget):

```bash
uv run python src/cedar/main.py extract \
  --file ./study-notes.md \
  --out /tmp/cedar-files \
  --backend ollama
```

## What it does

1. Obscura `fetch --dump markdown` plus a page-graph `--eval` (links + `application/ld+json`).
2. A DSPy ReAct gatherer may follow at most `--max-depth` (default 2) and `--max-pages` (default 5) same-object links (DOI, license, citation, access). Login and `mailto:` URLs are rejected.
3. Four extractors fill identity, attribution, domain terms, and access/coverage.
4. Host grounding strips ungrounded IRIs.
5. Serializer emits CEDAR wrapping (`@value` / `@id` / `rdfs:label`) and empty template slots.

## Tests

```bash
uv run --with pytest pytest src/cedar/tests
```

Live extract against ACDN is a manual smoke test, not CI.
