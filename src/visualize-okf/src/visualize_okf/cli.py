"""CLI for generating OKF bundle visualizations and Gephi exports."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from visualize_okf.viewer.export import default_out_path, export_graph

_FORMATS = ("html", "gexf", "graphml")


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="visualize-okf",
        description=(
            "Generate an OKF knowledge-bundle graph as self-contained HTML "
            "(Cytoscape.js) or Gephi-friendly GEXF / GraphML. "
            "Adapted from GoogleCloudPlatform/knowledge-catalog reference_agent viewer."
        ),
    )
    p.add_argument(
        "--bundle",
        required=True,
        type=Path,
        help="Path to the OKF bundle root directory.",
    )
    p.add_argument(
        "--format",
        dest="formats",
        default="html",
        help=(
            "Output format: html (default), gexf, graphml, or a comma-separated "
            "list (e.g. html,gexf,graphml)."
        ),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help=(
            "Output path. For a single format: a file path "
            "(defaults: <bundle>/viz.html, graph.gexf, or graph.graphml). "
            "For multiple formats: a directory (defaults to the bundle root)."
        ),
    )
    p.add_argument(
        "--name",
        default=None,
        help="Display / graph name (default: bundle directory name).",
    )
    return p


def _parse_formats(raw: str) -> list[str]:
    parts = [p.strip().lower() for p in raw.split(",") if p.strip()]
    if not parts:
        raise SystemExit("--format must list at least one of: html, gexf, graphml")
    bad = [p for p in parts if p not in _FORMATS]
    if bad:
        raise SystemExit(
            f"Unknown format(s) {bad}; choose from {', '.join(_FORMATS)}"
        )
    # preserve order, drop dups
    seen: set[str] = set()
    out: list[str] = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    formats = _parse_formats(args.formats)

    try:
        if len(formats) == 1:
            fmt = formats[0]
            out = args.out or default_out_path(args.bundle, fmt)
            stats = export_graph(
                args.bundle, out, fmt, bundle_name=args.name
            )
            print(
                f"Wrote {stats['concepts']} concept(s), "
                f"{stats['edges']} edge(s), "
                f"{stats['bytes']} bytes ({fmt}) → {out}",
                file=sys.stderr,
            )
            return 0

        # Multiple formats: --out is a directory (or default to bundle root)
        out_dir = args.out or args.bundle
        if out_dir.suffix.lower() in {".html", ".gexf", ".graphml"}:
            raise SystemExit(
                "When exporting multiple formats, --out must be a directory "
                "(or omit it to write into the bundle root)."
            )
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for fmt in formats:
            out = out_dir / default_out_path(args.bundle, fmt).name
            stats = export_graph(
                args.bundle, out, fmt, bundle_name=args.name
            )
            print(
                f"Wrote {stats['concepts']} concept(s), "
                f"{stats['edges']} edge(s), "
                f"{stats['bytes']} bytes ({fmt}) → {out}",
                file=sys.stderr,
            )
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0
