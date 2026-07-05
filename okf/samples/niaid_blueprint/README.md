# NIAID Blueprint — OKF concept extraction sample

Extracts grouped atomic concepts from the NIAID Blueprint for Digital Objects
into an [Open Knowledge Format (OKF) v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle.

## Prerequisites

- Source document listed in `sources.txt` (default: `docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`)
- An agent or LLM session with read/write access to this repository

## Run (print mode — review in chat)

```
Use @okf/samples/niaid_blueprint/extract.md on sources in
@okf/samples/niaid_blueprint/sources.txt.
Output mode: print. Show results; do not save files.
```

## Run (files mode — write OKF bundle)

```
Use @okf/samples/niaid_blueprint/extract.md on sources in
@okf/samples/niaid_blueprint/sources.txt.
Output mode: files. Save OKF bundle to okf/bundles/niaid_blueprint/.
```

## What you get

An OKF bundle under `okf/bundles/niaid_blueprint/`:

- Semantic subdirectories (`overview/`, `metadata-schema/`, `appendix/`, …)
- One concept file per thematic group with YAML frontmatter
- `index.md` at bundle root and in each subdirectory (progressive disclosure)
- `log.md` recording bundle creation/updates
- 239 globally numbered atomic concepts with line citations (from Blueprint v2)

## Bundle layout

See `extract.md` for the full directory schema. Concept IDs are paths without
`.md`, e.g. `metadata-schema/requirements`.

## Reference

- OKF specification: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- Produced bundle: [`../../bundles/niaid_blueprint/`](../../bundles/niaid_blueprint/)