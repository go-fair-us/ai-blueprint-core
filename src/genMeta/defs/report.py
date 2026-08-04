"""Assemble final-report.md for a genMeta run."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def write_final_report(
    report_path: Path,
    *,
    url: str,
    label: str,
    ws_id: str,
    models: Dict[str, str],
    run_dir: Path,
    iterations: List[Dict[str, Any]],
    final_conforms: bool,
    record_path: Optional[Path],
) -> None:
    """Write a human-readable summary of the extract/validate/repair loop."""
    lines = [
        "# genMeta run report",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Generated | {datetime.now(timezone.utc).isoformat(timespec='seconds')} |",
        f"| Resource URL | `{url}` |",
        f"| Run | `{label}` |",
        f"| Workspace | `{ws_id}` |",
        f"| Models | {', '.join(f'{k}={v}' for k, v in models.items())} |",
        f"| Final conforms | **{final_conforms}** |",
        f"| Iterations | {len(iterations)} |",
        "",
        "## Validation history",
        "",
    ]
    for row in iterations:
        n = row.get("iteration")
        conf = row.get("conforms")
        nv = row.get("n_violations")
        lines.append(
            f"- **iter {n:02d}**: conforms={conf}, violations={nv} "
            f"(`{row.get('out_dir', '')}`)"
        )
        findings = row.get("sample_findings") or []
        for f in findings[:8]:
            lines.append(f"  - `{f.get('result_path')}`: {f.get('message')}")

    lines.extend(["", "## Record", ""])
    if record_path and record_path.is_file():
        lines.append(f"Path: `{record_path}`")
        lines.append("")
        lines.append("```json")
        try:
            data = json.loads(record_path.read_text(encoding="utf-8"))
            lines.append(json.dumps(data, indent=2)[:8000])
        except json.JSONDecodeError:
            lines.append(record_path.read_text(encoding="utf-8")[:8000])
        lines.append("```")
    else:
        lines.append("_No record.jsonld written._")

    notes = run_dir / "notes.md"
    if notes.is_file():
        lines.extend(["", "## Extract notes", "", notes.read_text(encoding="utf-8")[:4000]])

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  report → {report_path}")
