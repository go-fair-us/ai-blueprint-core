"""P1 check: atomic source_lines exist in the Blueprint markdown file.

Does not judge semantic faithfulness (that is P3 LLM judge). Only verifies
that cited line spans fall within the document and are non-empty.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from okf_core.walk import walk_bundle
except ImportError as e:  # pragma: no cover
    print("okf_core required on PYTHONPATH", file=sys.stderr)
    raise SystemExit(2) from e


def _parse_lines_field(field: str) -> list[int]:
    """Parse '180' or '107-111' into a list of line numbers."""
    field = (field or "").strip()
    if not field:
        return []
    out: list[int] = []
    for part in field.split(","):
        part = part.strip()
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a > b:
                a, b = b, a
            out.extend(range(a, b + 1))
        elif re.fullmatch(r"\d+", part):
            out.append(int(part))
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Check atomic line citations vs Blueprint")
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--blueprint", type=Path, required=True)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args(argv)

    if not args.bundle.is_dir() or not args.blueprint.is_file():
        print("bundle dir and blueprint file required", file=sys.stderr)
        return 2

    lines = args.blueprint.read_text(encoding="utf-8").splitlines()
    n_lines = len(lines)
    concepts = walk_bundle(args.bundle)

    findings = []
    checked = 0
    for c in concepts:
        for a in c.atomics:
            checked += 1
            nums = _parse_lines_field(a.source_lines)
            if not nums:
                findings.append(
                    {
                        "severity": "error",
                        "atomic": a.number,
                        "parent": c.id,
                        "message": "empty or unparseable source_lines",
                        "source_lines": a.source_lines,
                    }
                )
                continue
            bad = [n for n in nums if n < 1 or n > n_lines]
            if bad:
                findings.append(
                    {
                        "severity": "error",
                        "atomic": a.number,
                        "parent": c.id,
                        "message": f"line(s) out of range 1..{n_lines}",
                        "bad_lines": bad,
                        "source_lines": a.source_lines,
                    }
                )
            # Soft: cited line should not be blank
            blank = [n for n in nums if n <= n_lines and not lines[n - 1].strip()]
            if blank:
                findings.append(
                    {
                        "severity": "warning",
                        "atomic": a.number,
                        "parent": c.id,
                        "message": "cited line(s) are blank in blueprint",
                        "blank_lines": blank,
                    }
                )

    report = {
        "bundle": str(args.bundle),
        "blueprint": str(args.blueprint),
        "blueprint_line_count": n_lines,
        "atomics_checked": checked,
        "findings": findings,
        "summary": {
            "errors": sum(1 for f in findings if f["severity"] == "error"),
            "warnings": sum(1 for f in findings if f["severity"] == "warning"),
        },
    }
    text = json.dumps(report, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)
    print(
        f"atomic_lines: checked={checked} "
        f"errors={report['summary']['errors']} "
        f"warnings={report['summary']['warnings']}",
        file=sys.stderr,
    )
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
