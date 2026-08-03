# Open Knowledge Format (OKF) — NIAID Blueprint

This directory holds OKF-aligned knowledge bundles and extraction recipes for
NIAID Blueprint source documents.

## Layout

| Path | Purpose |
|------|---------|
| [`samples/`](samples/) | Recipes — how to run concept extraction (`extract.md`, `sources.txt`, `README.md`) |
| [`bundles/`](bundles/) | Produced OKF knowledge bundles |
| [`prompt_examples/`](prompt_examples/) | Filled copies of Prompt Library templates (`{{placeholders}}` grounded in NIAID domain resources) |

## Specification

Bundles follow [OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
from [GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog).

v0.2 makes provenance (`sources`), trust (`generated` / `verified`), and lifecycle
(`status` / `stale_after`) first-class in frontmatter. Body `# Citations` lists
and the legacy `timestamp` field are superseded (see SPEC §13).

## Current bundles

- [`bundles/niaid_blueprint/`](bundles/niaid_blueprint/) — 239 atomic concepts from
  `docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md` (27 concept files),
  `okf_version: "0.2"`

## Run extraction

See [`samples/niaid_blueprint/README.md`](samples/niaid_blueprint/README.md).
