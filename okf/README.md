# Open Knowledge Format (OKF) — NIAID Blueprint

This directory holds OKF-aligned knowledge bundles and extraction recipes for
NIAID Blueprint source documents.

## Layout

| Path | Purpose |
|------|---------|
| [`samples/`](samples/) | Recipes — how to run concept extraction (`extract.md`, `sources.txt`, `README.md`) |
| [`bundles/`](bundles/) | Produced OKF knowledge bundles |

## Specification

Bundles follow [OKF v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
from [GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog).

## Current bundles

- [`bundles/niaid_blueprint/`](bundles/niaid_blueprint/) — 239 atomic concepts from
  `docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md` (27 concept files)

## Run extraction

See [`samples/niaid_blueprint/README.md`](samples/niaid_blueprint/README.md).