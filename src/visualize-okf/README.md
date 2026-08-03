# visualize-okf

Build one HTML file that shows an OKF v0.2 knowledge bundle as an interactive graph.
You can also export the same graph for Gephi as GEXF or GraphML.

Spec: [Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

The tool still reads OKF v0.1 bundles. When the document has no `generated` field, the tool uses the legacy `timestamp` field for the content time. A body `# Citations` list still renders as markdown.

This package comes from the GoogleCloudPlatform/knowledge-catalog `reference_agent visualize` consumer (Apache-2.0). The package is viewer-only. It does not need BigQuery, ADK, or enrichment agents.

## Features

Graph and links:

- Draws a force-directed graph (Cytoscape.js) for every concept
- Colors each node by `type` (NIAID palette, or a stable hash for unknown types)
- Builds directed edges from internal markdown links (relative and absolute from root, OKF section 6)
- Adds provenance edges when `sources[].resource` points at a concept in the bundle (`kind: source`, dashed line)

Detail panel and search:

- Shows description, resource, tags, status, generated, trust tier, `stale_after`, sources, body text, and "Cited by" backlinks
- Supports search on title, id, tags, and actor
- Supports type filter and layout choice

Output:

- Writes a single HTML file that opens in a modern browser (CDN loads Cytoscape and marked)
- Exports GEXF 1.3 and GraphML for Gephi (directed graph)
- Puts type, status, trust_tier, generated fields, and sources on nodes
- Puts `kind` on edges

## Install

```bash
cd visualize-okf
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Usage

```bash
# HTML (Cytoscape) - default
.venv/bin/python -m visualize_okf \
  --bundle ../../okf/bundles/niaid_blueprint \
  --out /tmp/niaid_blueprint_viz.html \
  --name "NIAID Blueprint"

# Gephi: GEXF (recommended) and/or GraphML
.venv/bin/python -m visualize_okf \
  --bundle ../../okf/bundles/niaid_blueprint \
  --format gexf \
  --out /tmp/niaid_blueprint.gexf \
  --name "NIAID Blueprint"

# All three at once (writes into the bundle root)
.venv/bin/python -m visualize_okf \
  --bundle ../../okf/bundles/niaid_blueprint \
  --format html,gexf,graphml \
  --name "NIAID Blueprint"
```

If you omit `--out`, the tool writes these defaults:

| Format | Default path |
|--------|----------------|
| `html` | `<bundle>/viz.html` |
| `gexf` | `<bundle>/graph.gexf` |
| `graphml` | `<bundle>/graph.graphml` |

### Open in Gephi

1. Generate `graph.gexf` or `graph.graphml` with the commands above.
2. In Gephi, choose **File → Open** and select the file.
3. In **Appearance**, color nodes by `type` or `trust_tier`.
4. Run a layout such as ForceAtlas 2.

## OKF v0.2 fields

| Frontmatter | Viewer and export |
|-------------|-------------------|
| `type` (required) | Node type and color |
| `title`, `description`, `resource`, `tags` | Detail panel and export attributes |
| `status` | Chip and node border for draft or deprecated |
| `generated.by` / `generated.at` | Detail "Generated". When `generated.at` is absent, use legacy `timestamp` |
| `verified` | Trust tier: unverified, machine-confirmed, or human-reviewed |
| `stale_after` | Detail panel |
| `sources[]` | Detail list. Paths to concepts in the bundle become provenance edges |

## Tests

```bash
.venv/bin/pytest
```

## Attribution

Viewer code adapted from:

- https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf/src/reference_agent/viewer

See [NOTICE](NOTICE) and [LICENSE](LICENSE).
