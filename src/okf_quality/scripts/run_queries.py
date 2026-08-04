"""Run SPARQL query packs against an RDF file (P2).

Queries that bind ?violation (or return rows) are treated as findings.
Empty result → pass for that query.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run SPARQL .rq files against RDF data")
    p.add_argument("--data", type=Path, required=True)
    p.add_argument(
        "--query-dir",
        type=Path,
        required=True,
        help="Directory of .rq files",
    )
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args(argv)

    try:
        from rdflib import Graph
    except ImportError:
        print("rdflib required (uv sync --extra validation)", file=sys.stderr)
        return 2

    if not args.data.is_file():
        print(f"Data not found: {args.data}", file=sys.stderr)
        return 2
    if not args.query_dir.is_dir():
        print(f"Query dir not found: {args.query_dir}", file=sys.stderr)
        return 2

    g = Graph()
    g.parse(args.data)

    results: list[dict] = []
    failed = 0
    for qpath in sorted(args.query_dir.glob("*.rq")):
        qtext = qpath.read_text(encoding="utf-8")
        # Strip leading comment block for execution
        rows = []
        try:
            qres = g.query(qtext)
            for row in qres:
                rows.append({str(k): str(v) if v is not None else None for k, v in row.asdict().items()})
        except Exception as e:
            results.append(
                {
                    "query": qpath.name,
                    "error": str(e),
                    "row_count": -1,
                }
            )
            failed += 1
            continue
        results.append(
            {
                "query": qpath.name,
                "row_count": len(rows),
                "rows": rows[:50],  # cap for report size
                "truncated": len(rows) > 50,
            }
        )
        # Integrity queries: any row is a finding
        if rows and "integrity" in str(args.query_dir):
            failed += 1

    report = {
        "data": str(args.data),
        "query_dir": str(args.query_dir),
        "results": results,
        "failed_queries": failed,
    }
    text = json.dumps(report, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        print(text)

    print(
        f"run_queries: {len(results)} query file(s), {failed} with findings/errors",
        file=sys.stderr,
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
