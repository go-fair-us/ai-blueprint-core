"""P0 structural OKF lint CLI.

Usage (from repo root)::

    PYTHONPATH=src/okf_core/src:src/okf_quality \\
      python -m okf_quality.scripts.okf_lint --bundle okf/bundles/niaid_blueprint
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from okf_core.walk import walk_bundle
except ImportError as e:  # pragma: no cover
    print(
        "okf_core is required. Set PYTHONPATH=src/okf_core/src:src/okf_quality",
        file=sys.stderr,
    )
    raise SystemExit(2) from e


@dataclass
class Finding:
    rule_id: str
    severity: str
    message: str
    path: str = ""
    detail: dict[str, Any] | None = None


def _parse_range(concept_range: str) -> tuple[int, int] | None:
    m = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", concept_range or "")
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    return (a, b) if a <= b else (b, a)


def lint_bundle(bundle: Path) -> list[Finding]:
    findings: list[Finding] = []
    concepts = walk_bundle(bundle)
    ids = {c.id for c in concepts}
    all_numbers: list[tuple[int, str]] = []

    for c in concepts:
        if not c.type or not str(c.type).strip():
            findings.append(
                Finding(
                    "concept-has-type",
                    "error",
                    "Missing non-empty type",
                    path=c.id,
                )
            )
        if not c.title:
            findings.append(
                Finding(
                    "title-recommended",
                    "warning",
                    "Missing title (OKF recommended)",
                    path=c.id,
                )
            )

        for src in c.sources:
            if not (src.get("resource") or "").strip():
                findings.append(
                    Finding(
                        "sources-resource-required",
                        "error",
                        "sources entry missing resource",
                        path=c.id,
                        detail=src,
                    )
                )

        for target in c.links_to:
            if target not in ids:
                findings.append(
                    Finding(
                        "broken-body-link",
                        "error",
                        f"Body link target not found: {target}",
                        path=c.id,
                    )
                )

        if not c.atomics:
            findings.append(
                Finding(
                    "atomic-table-present",
                    "warning",
                    "No atomic concepts parsed from body table",
                    path=c.id,
                )
            )
        else:
            for a in c.atomics:
                all_numbers.append((a.number, c.id))

            rng = _parse_range(c.concept_range)
            if rng:
                nums = [a.number for a in c.atomics]
                if min(nums) != rng[0] or max(nums) != rng[1]:
                    findings.append(
                        Finding(
                            "concept-range-matches-atomics",
                            "warning",
                            (
                                f"concept_range {c.concept_range} does not match "
                                f"atomic min/max {min(nums)}-{max(nums)}"
                            ),
                            path=c.id,
                        )
                    )

    counts = Counter(n for n, _ in all_numbers)
    for num, cnt in sorted(counts.items()):
        if cnt > 1:
            parents = [p for n, p in all_numbers if n == num]
            findings.append(
                Finding(
                    "atomic-numbers-unique",
                    "error",
                    f"Duplicate atomic number {num} in {parents}",
                    path=parents[0] if parents else "",
                )
            )

    return findings


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="P0 OKF structural lint")
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--out", type=Path, default=None, help="Write JSON report")
    args = p.parse_args(argv)

    if not args.bundle.is_dir():
        print(f"Bundle not found: {args.bundle}", file=sys.stderr)
        return 2

    findings = lint_bundle(args.bundle)
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    report = {
        "bundle": str(args.bundle),
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "findings": len(findings),
        },
        "findings": [asdict(f) for f in findings],
    }

    text = json.dumps(report, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)

    print(
        f"okf_lint: {len(errors)} error(s), {len(warnings)} warning(s)",
        file=sys.stderr,
    )
    for f in findings:
        if f.severity == "error":
            print(f"  [{f.severity}] {f.rule_id}: {f.path}: {f.message}", file=sys.stderr)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
