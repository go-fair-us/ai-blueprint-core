# Vendored JSON-LD contexts

`scripts/validate.py` never lets the RDF parser fetch a `@context` over the
network. Untrusted graph text reaches it through the MCP `validate_dataset`
tool, and rdflib dereferences remote context IRIs at parse time — including
`file://` ones — so a crafted document could otherwise drive arbitrary
outbound requests from the validating process.

Contexts are resolved from this directory instead. Anything not on the
allowlist in `validate.py` (`_ALLOWED_CONTEXT_IRIS`) is refused with a
`RemoteContextError` rather than fetched.

## schemaorg-jsonldcontext.jsonld

| | |
|---|---|
| Source | <https://schema.org/docs/jsonldcontext.json> |
| Retrieved | 2026-08-15 |
| Size | 211,606 bytes — 3,080 terms |
| sha256 | `58f70940892ef4ed…` (first 16 hex chars) |

Verbatim upstream file, including its top-level `@context` wrapper. Serves
every spelling of the schema.org context IRI on the allowlist.

Note that upstream sets `"@vocab": "http://schema.org/"` (http). That is why
`normalize_schema_org_iris()` exists: Blueprint shapes use the canonical
`https://schema.org/`, so expanded IRIs are rewritten after parsing.

## Refreshing

```bash
curl -sSL -o schemaorg-jsonldcontext.jsonld https://schema.org/docs/jsonldcontext.json
```

Then re-run the skill tests. Update the table above with the new date, size,
and digest. Review the diff before committing — this file is executed as
vocabulary against every dataset the validator sees.
