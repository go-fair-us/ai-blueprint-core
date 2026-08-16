#!/usr/bin/env python3
"""Validate a schema:Dataset RDF/JSON-LD graph with pySHACL.

Bundled shape: ``assets/blueprint-required.ttl`` (initial NIAID Blueprint
required-field shape, derived from Google Dataset required constraints).

Inspired by the EarthCube DOOS ``decoder-validate-shacl`` stage: one pySHACL
call, severity-aware conformance (zero ``sh:Violation`` results), and three
artifacts — report Turtle, normalized results JSON, and a conforms summary.

Usage (CLI)::

    python scripts/validate.py DATA.jsonld [--shape SHAPE.ttl] [--out-dir DIR]

Usage (import)::

    from validate import run_validation
    summary = run_validation("record.jsonld", out_dir="validation_output")
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    from pyshacl import validate
    from rdflib import Graph, Namespace, URIRef
    from rdflib.namespace import RDF
except ImportError as exc:  # pragma: no cover - exercised only without deps
    raise SystemExit(
        "pyshacl and rdflib are required. Install with:\n"
        "  uv sync --extra validation\n"
        "or:\n"
        "  uv pip install pyshacl\n"
        f"Original error: {exc}"
    ) from exc

SH = Namespace("http://www.w3.org/ns/shacl#")

# Skill root = parent of scripts/; default shape lives in assets/.
_SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SHAPE = _SKILL_DIR / "assets" / "blueprint-required.ttl"

# Stable blank-node skolemization authority for report graph ids.
_SKOLEM_AUTHORITY = "https://niaid.nih.gov/blueprint/validation"

# JSON-LD remote context for schema.org expands terms to http://schema.org/
# while Blueprint JSON-LD and our shapes use https://schema.org/. Rewrite so
# sh:targetClass and property paths match (avoids silent false "conforms").
_SCHEMA_HTTP = "http://schema.org/"
_SCHEMA_HTTPS = "https://schema.org/"

#################################################################
# JSON-LD context resolution: offline, allowlisted.
#
# rdflib dereferences remote "@context" IRIs over the network while parsing.
# The graph text here is untrusted -- it arrives from the MCP
# ``validate_dataset`` tool, so it is whatever a user pasted or a model was
# talked into passing along. A crafted "@context" therefore turns validation
# into an outbound request of the attacker's choosing (http://, and also
# file://, which rdflib resolves as a local read).
#
# So: never let the parser fetch. Every context is resolved from a vendored
# copy on disk, and any reference not on the allowlist is refused with an
# error instead of a request. This also makes validation work offline.
#################################################################

_CONTEXTS_DIR = _SKILL_DIR / "assets" / "contexts"
_SCHEMA_ORG_CONTEXT_FILE = _CONTEXTS_DIR / "schemaorg-jsonldcontext.jsonld"

# Every spelling of the schema.org context IRI that appears in Blueprint
# examples, all served from the one vendored file above.
_ALLOWED_CONTEXT_IRIS = frozenset(
    {
        "http://schema.org",
        "http://schema.org/",
        "https://schema.org",
        "https://schema.org/",
        "http://www.schema.org",
        "http://www.schema.org/",
        "https://www.schema.org",
        "https://www.schema.org/",
        "http://schema.org/docs/jsonldcontext.json",
        "https://schema.org/docs/jsonldcontext.json",
    }
)


class RemoteContextError(RuntimeError):
    """Raised for a JSON-LD context this validator will not dereference."""


@lru_cache(maxsize=1)
def _schema_org_context() -> Any:
    """Return the vendored schema.org term map (parsed once, then cached)."""
    if not _SCHEMA_ORG_CONTEXT_FILE.is_file():
        raise RemoteContextError(
            "Vendored schema.org context is missing: "
            f"{_SCHEMA_ORG_CONTEXT_FILE}. Restore it from "
            "https://schema.org/docs/jsonldcontext.json"
        )
    doc = json.loads(_SCHEMA_ORG_CONTEXT_FILE.read_text(encoding="utf-8"))
    # Upstream ships the term map wrapped in a top-level "@context".
    if isinstance(doc, dict) and "@context" in doc:
        return doc["@context"]
    return doc


def _localize_context_value(value: Any) -> Any:
    """Resolve one ``@context`` value locally, or refuse it."""
    if value is None or isinstance(value, dict):
        # An inline context object. Term definitions can carry their own
        # scoped @context / @import, so keep walking.
        return _localize_contexts(value) if value is not None else value
    if isinstance(value, str):
        if value in _ALLOWED_CONTEXT_IRIS:
            return _schema_org_context()
        raise RemoteContextError(
            f"Refusing to dereference remote JSON-LD context {value!r}. "
            "Inline the context object instead, or use one of: "
            + ", ".join(sorted(_ALLOWED_CONTEXT_IRIS))
        )
    if isinstance(value, list):
        return [_localize_context_value(item) for item in value]
    raise RemoteContextError(
        f"Unsupported @context value of type {type(value).__name__}."
    )


def _localize_contexts(node: Any) -> Any:
    """Rewrite every ``@context`` in a JSON-LD structure to a local one.

    Recurses the whole document because JSON-LD allows scoped contexts on any
    node and inside any term definition -- checking only the top level would
    leave a nested remote reference to be fetched at parse time.
    """
    if isinstance(node, list):
        return [_localize_contexts(item) for item in node]
    if not isinstance(node, dict):
        return node
    out: dict[str, Any] = {}
    for key, value in node.items():
        if key == "@context":
            out[key] = _localize_context_value(value)
        elif key == "@import":
            # JSON-LD 1.1 context @import is always a remote reference.
            raise RemoteContextError(
                f"Refusing to dereference JSON-LD context @import {value!r}. "
                "Inline the imported terms instead."
            )
        else:
            out[key] = _localize_contexts(value)
    return out

_FORMAT_BY_SUFFIX = {
    ".ttl": "turtle",
    ".turtle": "turtle",
    ".nt": "nt",
    ".n3": "n3",
    ".rdf": "xml",
    ".xml": "xml",
    ".jsonld": "json-ld",
    ".json": "json-ld",
}


def _guess_format(path: Path, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    return _FORMAT_BY_SUFFIX.get(path.suffix.lower(), "turtle")


def normalize_schema_org_iris(graph: Graph) -> Graph:
    """Rewrite ``http://schema.org/`` IRIs to ``https://schema.org/``.

    Walks subjects, predicates, and objects (``Graph.all_nodes()`` omits
    predicates, which would leave property paths unmatched).
    """
    mapping: dict[URIRef, URIRef] = {}
    for s, p, o in graph:
        for term in (s, p, o):
            if isinstance(term, URIRef):
                text = str(term)
                if text.startswith(_SCHEMA_HTTP) and term not in mapping:
                    mapping[term] = URIRef(_SCHEMA_HTTPS + text[len(_SCHEMA_HTTP) :])
    if not mapping:
        return graph
    out = Graph()
    for s, p, o in graph:
        out.add((mapping.get(s, s), mapping.get(p, p), mapping.get(o, o)))
    return out


def _load_graph(path: Path, fmt: str) -> Graph:
    g = Graph()
    if fmt == "json-ld":
        doc = json.loads(path.read_text(encoding="utf-8"))
        # publicID keeps relative-IRI resolution identical to parsing the
        # file by path, which is what rdflib would have used as the base.
        g.parse(
            data=json.dumps(_localize_contexts(doc)),
            format=fmt,
            publicID=path.resolve().as_uri(),
        )
    else:
        # Turtle/N-Triples/RDF-XML have no remote-context mechanism.
        g.parse(path.as_posix(), format=fmt)
    return normalize_schema_org_iris(g)


def _severity_bucket(severity_iri: str | None) -> str:
    """Map a sh:resultSeverity IRI to 'violation' | 'warning' | 'info'."""
    if not severity_iri:
        # SHACL default severity is sh:Violation when none is stated.
        return "violation"
    s = severity_iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1].lower()
    if s.startswith("viol"):
        return "violation"
    if s.startswith("warn"):
        return "warning"
    if s.startswith("info"):
        return "info"
    return "violation"


def _get_obj(graph: Graph, subject: Any, predicate: Any) -> str | None:
    """Return the first object for (s, p, *) as a string, or None."""
    value = graph.value(subject, predicate)
    if value is None:
        return None
    return str(value)


def run_validation(
    data_path: str | Path,
    shape_path: str | Path = DEFAULT_SHAPE,
    out_dir: str | Path | None = None,
    data_format: str | None = None,
    shape_format: str | None = None,
    inference: str = "rdfs",
) -> dict[str, Any]:
    """Validate ``data_path`` against ``shape_path``; write artifacts; return summary.

    Conformance here is **severity-aware**: ``conforms`` is True iff there are
    zero ``sh:Violation`` results. pySHACL's raw boolean is False whenever any
    result exists (including warnings); that raw value is exposed as
    ``raw_conforms`` for debugging only.

    Returns a dict with ``conforms``, ``raw_conforms``, counts, ``results``,
    and paths to written artifacts (when ``out_dir`` is set or defaulted).
    """
    data_path = Path(data_path)
    shape_path = Path(shape_path)
    if not data_path.is_file():
        raise FileNotFoundError(f"Data graph not found: {data_path}")
    if not shape_path.is_file():
        raise FileNotFoundError(f"Shapes graph not found: {shape_path}")

    if out_dir is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_dir = Path(f"validation_output_{stamp}")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data_fmt = _guess_format(data_path, data_format)
    shape_fmt = _guess_format(shape_path, shape_format)

    try:
        data_graph = _load_graph(data_path, data_fmt)
        shape_graph = Graph()
        shape_graph.parse(shape_path.as_posix(), format=shape_fmt)
        raw_conforms, report_graph, _ = validate(
            data_graph,
            shacl_graph=shape_graph,
            inference=inference,
            serialize_report_graph=False,
        )
    except RemoteContextError:
        # Surface the refusal verbatim; it is a rejected input, not a failure.
        raise
    except Exception as e:
        raise RuntimeError(f"SHACL validation failed for {data_path}: {e}") from e

    report_graph = report_graph.skolemize(authority=_SKOLEM_AUTHORITY)

    results: list[dict[str, Any]] = []
    for res in report_graph.subjects(RDF.type, SH.ValidationResult):
        results.append(
            {
                "result_id": str(res),
                "severity": _get_obj(report_graph, res, SH.resultSeverity),
                "focus_node": _get_obj(report_graph, res, SH.focusNode),
                "result_path": _get_obj(report_graph, res, SH.resultPath),
                "message": _get_obj(report_graph, res, SH.resultMessage),
                "source_shape": _get_obj(report_graph, res, SH.sourceShape),
                "source_constraint": _get_obj(
                    report_graph, res, SH.sourceConstraintComponent
                ),
                "value": _get_obj(report_graph, res, SH.value),
            }
        )

    buckets = [_severity_bucket(r["severity"]) for r in results]
    n_violations = buckets.count("violation")
    n_warnings = buckets.count("warning")
    n_info = buckets.count("info")
    conforms = n_violations == 0

    report_ttl = out_dir / "report.ttl"
    results_json = out_dir / "results.json"
    conforms_json = out_dir / "conforms.json"

    report_ttl.write_text(report_graph.serialize(format="turtle"), encoding="utf-8")
    results_json.write_text(json.dumps(results, indent=2), encoding="utf-8")

    summary: dict[str, Any] = {
        "conforms": conforms,
        "raw_conforms": bool(raw_conforms),
        "n_violations": n_violations,
        "n_warnings": n_warnings,
        "n_info": n_info,
        "data_path": str(data_path.resolve()),
        "shape_path": str(shape_path.resolve()),
        "data_format": data_fmt,
    }
    conforms_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    summary["results"] = results
    summary["report_ttl"] = str(report_ttl.resolve())
    summary["results_json"] = str(results_json.resolve())
    summary["conforms_json"] = str(conforms_json.resolve())
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a schema:Dataset graph (JSON-LD or Turtle) against the "
            "NIAID Blueprint required SHACL shape (pySHACL)."
        ),
    )
    parser.add_argument(
        "data",
        help="Data graph path (.jsonld, .json, .ttl, .nt, …)",
    )
    parser.add_argument(
        "--shape",
        default=str(DEFAULT_SHAPE),
        help=f"SHACL shapes file (default: bundled {DEFAULT_SHAPE.name})",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Directory for report.ttl / results.json / conforms.json "
        "(default: validation_output_YYYYMMDD_HHMMSS)",
    )
    parser.add_argument(
        "--data-format",
        default=None,
        help="Override data graph format (json-ld, turtle, nt, …)",
    )
    parser.add_argument(
        "--shape-format",
        default=None,
        help="Override shapes graph format (default: turtle)",
    )
    parser.add_argument(
        "--inference",
        default="rdfs",
        choices=["none", "rdfs", "owlrl", "both"],
        help="pySHACL inference mode (default: rdfs)",
    )
    args = parser.parse_args(argv)

    summary = run_validation(
        args.data,
        shape_path=args.shape,
        out_dir=args.out_dir,
        data_format=args.data_format,
        shape_format=args.shape_format,
        inference=args.inference,
    )

    status = "CONFORMS" if summary["conforms"] else "NON-CONFORMING"
    print(
        f"{status}: {summary['n_violations']} violation(s), "
        f"{summary['n_warnings']} warning(s), {summary['n_info']} info "
        f"(pySHACL raw_conforms={summary['raw_conforms']})"
    )
    print(f"  report:   {summary['report_ttl']}")
    print(f"  results:  {summary['results_json']}")
    print(f"  conforms: {summary['conforms_json']}")

    if not summary["conforms"] and summary["results"]:
        print("  sample findings:")
        for row in summary["results"][:8]:
            path = row.get("result_path") or "(no path)"
            msg = row.get("message") or ""
            print(f"    - [{_severity_bucket(row.get('severity'))}] {path}: {msg}")

    return 0 if summary["conforms"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
