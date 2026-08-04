"""Run pySHACL on a data graph against a shapes file (P0/P1).

Usage::

    PYTHONPATH=src/okf_quality python -m okf_quality.scripts.shacl_validate \\
      --data /tmp/niaid.ttl \\
      --shapes src/okf_quality/shapes/okf-graph/okf-bundle.ttl \\
      --out-dir src/okf_quality/reports/shacl-okf-graph
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="SHACL validate RDF with pySHACL")
    p.add_argument("--data", type=Path, required=True, help="Data graph (ttl/jsonld/…)")
    p.add_argument("--shapes", type=Path, required=True, help="Shapes graph TTL")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Write report.ttl + summary.json here",
    )
    p.add_argument(
        "--inference",
        default="rdfs",
        choices=["none", "rdfs", "owlrl", "both"],
    )
    args = p.parse_args(argv)

    try:
        from pyshacl import validate
        from rdflib import Graph
    except ImportError:
        print(
            "pyshacl and rdflib required. Install with: uv sync --extra validation",
            file=sys.stderr,
        )
        return 2

    if not args.data.is_file():
        print(f"Data file not found: {args.data}", file=sys.stderr)
        return 2
    if not args.shapes.is_file():
        print(f"Shapes file not found: {args.shapes}", file=sys.stderr)
        return 2

    data_g = Graph()
    data_g.parse(args.data)
    shapes_g = Graph()
    shapes_g.parse(args.shapes)

    conforms, report_g, report_text = validate(
        data_g,
        shacl_graph=shapes_g,
        inference=args.inference,
        abort_on_first=False,
        meta_shacl=False,
        advanced=True,
        inplace=False,
    )

    out_dir = args.out_dir
    if out_dir is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_dir = Path("src/okf_quality/reports") / f"shacl_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    report_path = out_dir / "report.ttl"
    report_g.serialize(destination=str(report_path), format="turtle")
    (out_dir / "report.txt").write_text(str(report_text), encoding="utf-8")

    summary = {
        "data": str(args.data),
        "shapes": str(args.shapes),
        "conforms": bool(conforms),
        "inference": args.inference,
        "report_ttl": str(report_path),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    print(
        f"SHACL conforms={conforms} → {out_dir}",
        file=sys.stderr,
    )
    return 0 if conforms else 1


if __name__ == "__main__":
    raise SystemExit(main())
