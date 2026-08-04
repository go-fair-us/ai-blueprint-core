"""Serialize rdflib Graph to Turtle or JSON-LD."""

from __future__ import annotations

import json
from pathlib import Path

from rdflib import Graph

from okf2rdf.mapping import DCTERMS, OKF_NS, PROV, RDFS, SCHEMA

_FORMATS = {
    "turtle": "turtle",
    "ttl": "turtle",
    "json-ld": "json-ld",
    "jsonld": "json-ld",
}

_JSONLD_CONTEXT = {
    "@vocab": SCHEMA,
    "schema": SCHEMA,
    "prov": PROV,
    "dcterms": "http://purl.org/dc/terms/",
    "rdfs": RDFS,
    "okf": OKF_NS,
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "name": "schema:name",
    "description": "schema:description",
    "url": {"@id": "schema:url", "@type": "@id"},
    "keywords": "schema:keywords",
    "creativeWorkStatus": "schema:creativeWorkStatus",
    "hasPart": {"@id": "schema:hasPart", "@type": "@id"},
    "isPartOf": {"@id": "dcterms:isPartOf", "@type": "@id"},
    "references": {"@id": "dcterms:references", "@type": "@id"},
    "wasDerivedFrom": {"@id": "prov:wasDerivedFrom", "@type": "@id"},
    "wasAttributedTo": {"@id": "prov:wasAttributedTo", "@type": "@id"},
    "generatedAtTime": {
        "@id": "prov:generatedAtTime",
        "@type": "xsd:dateTime",
    },
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "text": "schema:text",
    "atomicNumber": {"@id": "okf:atomicNumber", "@type": "xsd:integer"},
    "sourceLines": "okf:sourceLines",
    "AtomicConcept": "okf:AtomicConcept",
    "notation": "skos:notation",
}


def normalize_format(fmt: str) -> str:
    key = fmt.lower().strip()
    if key not in _FORMATS:
        raise ValueError(
            f"Unknown format {fmt!r}; choose turtle or json-ld"
        )
    return _FORMATS[key]


def default_out_path(bundle_root: Path, fmt: str) -> Path:
    fmt_n = normalize_format(fmt)
    if fmt_n == "json-ld":
        return Path(bundle_root) / "bundle.jsonld"
    return Path(bundle_root) / "bundle.ttl"


def write_graph(graph: Graph, out_path: Path, fmt: str) -> dict[str, int]:
    """Write graph to path; returns stats."""
    fmt_n = normalize_format(fmt)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt_n == "json-ld":
        # rdflib json-ld serialization
        data = graph.serialize(format="json-ld", context=_JSONLD_CONTEXT, indent=2)
        if isinstance(data, bytes):
            text = data.decode("utf-8")
        else:
            text = data
        # Ensure context is visible at top when possible
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                wrapper = {"@context": _JSONLD_CONTEXT, "@graph": parsed}
                text = json.dumps(wrapper, indent=2, ensure_ascii=False)
            elif isinstance(parsed, dict) and "@context" not in parsed:
                parsed = {"@context": _JSONLD_CONTEXT, **parsed}
                text = json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            pass
        out_path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    else:
        data = graph.serialize(format="turtle")
        text = data.decode("utf-8") if isinstance(data, bytes) else data
        out_path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")

    return {
        "triples": len(graph),
        "bytes": out_path.stat().st_size,
        "format": fmt_n,
    }


def load_shipped_context() -> dict:
    """Return the JSON-LD context (also written under context/)."""
    return dict(_JSONLD_CONTEXT)
