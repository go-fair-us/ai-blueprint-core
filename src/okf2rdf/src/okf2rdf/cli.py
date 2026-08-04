"""CLI for OKF bundle → RDF (schema.org-centered)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from okf2rdf.build import graph_from_bundle
from okf2rdf.serialize import default_out_path, normalize_format, write_graph

DEFAULT_BASE = (
    "https://go-fair-us.github.io/ai-blueprint-core/okf/bundles/niaid_blueprint/"
)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="okf2rdf",
        description=(
            "Convert an Open Knowledge Format (OKF) v0.2 knowledge bundle "
            "to an RDF graph (schema.org, PROV, DCTERMS, RDFS, local okf:)."
        ),
    )
    p.add_argument(
        "--bundle",
        required=True,
        type=Path,
        help="Path to the OKF bundle root directory.",
    )
    p.add_argument(
        "--base",
        default=DEFAULT_BASE,
        help=(
            "IRI base for concept subjects (path concept id is appended). "
            f"Default: {DEFAULT_BASE}"
        ),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output path (default: <bundle>/bundle.ttl or bundle.jsonld).",
    )
    p.add_argument(
        "--format",
        dest="fmt",
        default="turtle",
        help="Output format: turtle (default) or json-ld.",
    )
    p.add_argument(
        "--name",
        default=None,
        help="Bundle display name (default: bundle directory name).",
    )
    p.add_argument(
        "--no-body-links",
        action="store_true",
        help="Do not emit dcterms:references edges from body markdown links.",
    )
    p.add_argument(
        "--no-atomics",
        action="store_true",
        help=(
            "Do not emit okf:AtomicConcept nodes from body "
            "'# Atomic concepts' tables (group concepts only)."
        ),
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        fmt = normalize_format(args.fmt)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    bundle = Path(args.bundle)
    if not bundle.is_dir():
        print(f"Bundle directory not found: {bundle}", file=sys.stderr)
        return 1

    out = args.out or default_out_path(bundle, fmt)
    try:
        graph, concepts = graph_from_bundle(
            bundle,
            base=args.base,
            bundle_name=args.name,
            include_body_links=not args.no_body_links,
            include_atomics=not args.no_atomics,
        )
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    if not concepts:
        print("No typed concepts found in bundle.", file=sys.stderr)
        return 1

    n_atomics = sum(len(c.atomics) for c in concepts)
    stats = write_graph(graph, out, fmt)
    atomic_note = ""
    if not args.no_atomics:
        atomic_note = f", {n_atomics} atomic(s)"
    print(
        f"Wrote {len(concepts)} concept(s){atomic_note}, "
        f"{stats['triples']} triple(s), "
        f"{stats['bytes']} bytes ({stats['format']}) → {out}",
        file=sys.stderr,
    )
    return 0
