# Bio / NIH MCP server catalog

A curated, reviewed list of MCP servers for the biomedical and NIH/NIAID research
community. The YAML file is the source of truth, and `yaml2ard.py` turns it into an
[Agentic Resource Discovery (ARD) v0.91](https://agenticresourcediscovery.org/spec/)
manifest (`ard.json`).

Status: draft 0.1.0, checked 2026-11-13. Nothing here is published.

## Files

| Path | What it is |
| --- | --- |
| `bio-nih-mcp.yaml` | Source of truth: catalog header, 21 entries, and a `reviewedNotListed` section |
| `yaml2ard.py` | YAML to ARD converter and validator |
| `ard.json` | Generated manifest with the curation terms kept |
| `ard.pure.json` | Generated manifest with only ARD core terms (`--strip-curation`) |
| `checks/` | Probe scripts (`probe.py` for remote Streamable HTTP, `probe_stdio.py` for local stdio) and raw results |
| `vendor/ard-spec/` | Copies of the ARD JSON Schema, base context, CDDL, and the official `conformance-test` CLI from [ards-project/ard-spec](https://github.com/ards-project/ard-spec) (Apache-2.0) |

## Catalog at a glance

| Server | Role | Status | Profiles | Transport |
| --- | --- | --- | --- | --- |
| [BRC Analytics MCP](https://brc-analytics.org/learn/mcp) | default | alive | nih-niaid-research | streamable-http (hosted) |
| [BioMCP](https://biomcp.org/) | default | alive | general-bio, nih-niaid-research | stdio, streamable-http (self-hosted, `biomcp serve-http`) |
| [EMBL-EBI Ontology Lookup Service (OLS4) MCP](https://www.ebi.ac.uk/ols4/mcp) | default | alive | general-bio, nih-niaid-research | streamable-http (hosted) |
| [TogoMCP (DBCLS RDF Portal)](https://togomcp.rdfportal.org/) | default | alive | general-bio, nih-niaid-research | streamable-http (hosted), stdio (local) |
| [BioPortal MCP (NCBO)](https://bioportal.bioontology.org/) | optional | alive | general-bio, nih-niaid-research | stdio, streamable-http (hosted on FastMCP Cloud) |
| [BioThings MCP (longevity-genie)](https://github.com/longevity-genie/biothings-mcp) | optional | alive | general-bio | stdio, streamable-http (self-hosted), sse |
| [ClinicalTrials.gov MCP Server (cyanheads)](https://github.com/cyanheads/clinicaltrialsgov-mcp-server) | optional | alive | nih-niaid-research | streamable-http (hosted by author), stdio |
| [EMBL-EBI InterPro MCP](https://www.ebi.ac.uk/interpro/) | optional | alive | general-bio | streamable-http (hosted) |
| [Ensembl MCP Server (cyanheads)](https://github.com/cyanheads/ensembl-mcp-server) | optional | alive | general-bio | streamable-http (hosted by author), stdio |
| [Galaxy MCP](https://github.com/galaxyproject/galaxy-mcp) | optional | alive | nih-niaid-research, general-bio | stdio, streamable-http (self-hosted, OAuth) |
| [Open Targets Platform MCP (official)](https://platform-docs.opentargets.org/data-access/model-context-protocol) | optional | alive | general-bio | streamable-http (hosted), stdio |
| [OpenGenes MCP (longevity-genie)](https://open-genes.com/) | optional | alive | general-bio | stdio, streamable-http (self-hosted), sse |
| [PDBe MCP Servers (EMBL-EBI)](https://github.com/PDBeurope/PDBe-MCP-Servers) | optional | alive | general-bio | streamable-http (hosted beta), stdio |
| [PubMed MCP Server (cyanheads)](https://github.com/cyanheads/pubmed-mcp-server) | optional | alive | general-bio, nih-niaid-research | streamable-http (hosted by author), stdio |
| [ToolUniverse (Harvard Zitnik lab)](https://aiscientist.tools/) | optional | alive | general-bio | stdio, streamable-http (self-hosted) |
| [UniProt MCP Server (cyanheads)](https://github.com/cyanheads/uniprot-mcp-server) | optional | alive | general-bio | streamable-http (hosted by author), stdio |
| [gget MCP (longevity-genie)](https://github.com/pachterlab/gget) | optional | alive | general-bio | stdio, streamable-http (self-hosted, default port 3002), sse |
| [BV-BRC MCP](https://www.bv-brc.org/) | watch | unverified | nih-niaid-research | streamable-http (documented remote dev host, OAuth), stdio/local via cucinellclark/bvbrc-mcp-server |
| [Biomni (Stanford SNAP) -- self-exported MCP](https://biomni.stanford.edu) | watch | alive | general-bio | stdio (only when you write a small Python launcher) |
| [NIH RePORTER (Pipeworx gateway pack)](https://github.com/pipeworx-io/mcp-nih-reporter) | watch | alive | nih-niaid-research | streamable-http (hosted gateway) |
| [SynergyAge MCP (longevity-genie)](https://www.synergyage.info/) | watch | stale | general-bio | stdio, streamable-http (self-hosted), sse |

Reviewed but not listed: Cracking Shells. See `reviewedNotListed` in the YAML.

## How an entry is built

Every entry has two kinds of terms.

1. **ARD terms**, written without a prefix: `identifier`, `displayName`, `type`, `url`,
   `description`, `tags`, `version`, `updatedAt`, `representativeQueries`, and
   `capabilities`. `capabilities` holds the real tool names returned by `tools/list`.
2. **Curation terms** under the `cat:` prefix:

| Term | Meaning |
| --- | --- |
| `cat:profile` | `general-bio` and/or `nih-niaid-research` |
| `cat:role` | `default` (load always), `optional` (load on demand), or `watch` (not ready or not a fit yet) |
| `cat:status` | `alive`, `stale`, or `unverified` |
| `cat:urlKind` | What `url` points at: `mcp-endpoint`, `registry-server-json`, or `repository` |
| `cat:homepage`, `cat:source` | Human-facing page and source repository |
| `cat:transport`, `cat:auth`, `cat:install` | How to connect or run it |
| `cat:license`, `cat:dataSources`, `cat:dataTerms` | The code license, and the upstream data and its terms |
| `cat:lastCommit`, `cat:lastChecked`, `cat:verifiedBy` | Freshness, and how the entry was verified |
| `cat:reviewNotes` | Honest strengths and concerns |
| `cat:foundVia` | Where the entry came from (your list, the prior report, the MCP Registry, or an X post URL) |

The default set is kept small to avoid tool overload: **BioMCP, BRC Analytics, TogoMCP,
and EMBL-EBI OLS4**.

### Identifiers

Identifiers take the form `urn:air:github.com:fils:bio-nih-mcp:<slug>`, which follows the
spec's own solo-developer example (`urn:air:github.com:alice-dev:...`).

Under ARD the URN's domain is the publisher. These URNs therefore mark the entries as
**your catalog's descriptions of third-party servers, not publisher-attested ARD
entries**. No `trustManifest` is included. If a publisher later posts its own
`/.well-known/ard.json`, prefer their identifier and keep yours as a cross-reference.

### The `cat:` namespace (placeholder)

The `cat:` prefix maps to `https://example.org/mcp-catalog/ns#`, which is a **placeholder**.
Replace it with an IRI you control, such as a w3id.org redirect or a GitHub Pages page,
before publishing. `yaml2ard.py` warns while the placeholder is in use.

The converter writes a per-entry `@context` of
`["https://agenticresourcediscovery.org/context/v1", {"cat": "<ns>"}]`. It does this
because ARD reads `@context` on each entry, not on the manifest (spec §4.1). JSON-LD
expansion with pyld confirms that `cat:*` terms resolve to the namespace IRI and core terms
resolve to `https://agenticresourcediscovery.org/ns#`.

### What `url` points at

ARD says `url` should point at the artifact, such as an MCP Server Card. None of these
publishers currently publish a server card, so `url` points at one of these, recorded in
`cat:urlKind`:

- the hosted MCP endpoint, when one exists
- the official MCP Registry `server.json` (the `.../versions/latest` URL), for
  local-only servers listed there
- the source repository, otherwise

## Regenerate and validate

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python yaml2ard.py                                   # -> ard.json
.venv/bin/python yaml2ard.py --strip-curation -o ard.pure.json # ARD core terms only
.venv/bin/python yaml2ard.py --role default -o ard.default.json
.venv/bin/python yaml2ard.py --profile nih-niaid-research -o ard.niaid.json
.venv/bin/python yaml2ard.py --curation-as-metadata            # copy scalar cat: terms into metadata.*
.venv/bin/python vendor/ard-spec/conformance/bin/conformance-test manifest ard.json
```

`yaml2ard.py` checks:

- the required terms
- that each entry has exactly one of `url` or `data`
- the URN, against both the schema pattern and the stricter conformance-CLI form, plus a
  check that the publisher is an FQDN
- media-type syntax
- `updatedAt` as a date-time with a time zone
- that `metadata` values are scalars
- prefixes that are used but not declared
- duplicate identifiers
- a warning when `representativeQueries` falls outside 2–5 items
- the vendored JSON Schema (`ArdManifest`), when `jsonschema` is installed

It exits with status 1 on errors.

To re-verify that servers are alive:

```bash
python3 checks/probe.py https://brc-analytics.org/api/v1/mcp/ ...   # remote: initialize + tools/list, no auth
python3 checks/probe_stdio.py -- uvx biothings-mcp                  # local stdio
```

## Notes from the ARD spec and appendices

- **Required terms:** `identifier`, `displayName`, `type`, and exactly one of `url` or
  `data`. `representativeQueries` is a SHOULD with 2–5 items. A missing or wrong count is
  only a warning, but an entry without it is "not discoverable by search."
  `capabilities` is a MAY.
- **URN grammar (Appendix C):** `urn:air:<fqdn>[:<namespace>...]:<name>`, where the
  namespace can have several segments. The schema regex is
  `^urn:air:[a-zA-Z0-9.-]+(:[a-zA-Z0-9._-]+)+$`. `@id` may mirror the identifier.
- **Manifest (§5.1, D.1):** the only required member is `entries`. Other top-level members
  are "transport-defined" and ignored. Top-level `collections` was removed, and the
  conformance tool warns if it's present. Model hierarchy inside `entries`, or use nested
  `application/ai-catalog+json` entries.
- **`metadata`:** values must be scalars, and ARD doesn't expand this member into JSON-LD.
  It's filterable as `metadata.*` paths, but registry support varies. Namespaced terms
  (our `cat:`) are the intended extension point. `--curation-as-metadata` exists for
  registries that only index `metadata.*`.
- **Media types:** `application/mcp-server-card+json` is the standard type for an MCP
  server, and `application/mcp-server+json` is deprecated (ADR-0008). Types are not yet
  registered with IANA.
- **Trust (§4.5, D.2):** `trustManifest.identity` must align with the URN domain. This is
  the anti-squatting rule, and it's why a curator's catalog can't claim to be the publisher.
- **Spec quirk:** in the published JSON Schema, the property is spelled `TrustManifest`
  (capital T) under `EntryFields`, while the spec text and the base context use
  `trustManifest`. Because `additionalProperties` is true, a lowercase `trustManifest` is
  not schema-checked. Our script checks it.
- **Search API:** filters resolve namespaced keys by IRI, not by prefix string. A registry
  could filter on `cat:role` = `default` across catalogs, as long as they share the same
  namespace IRI, which is another reason to choose a stable IRI.
