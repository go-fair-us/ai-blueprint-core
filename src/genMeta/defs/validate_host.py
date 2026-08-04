"""Host-side SHACL validation via niaid-bp-validation skill."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from defs.config import DEFAULT_SHAPE, VALIDATE_SCRIPT


def _import_run_validation():
    scripts_dir = VALIDATE_SCRIPT.parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from validate import run_validation  # type: ignore  # noqa: E402

    return run_validation


def run_host_validation(
    data_path: Path,
    out_dir: Path,
    *,
    shape_path: Path | None = None,
) -> dict[str, Any]:
    """Validate ``data_path``; write artifacts under ``out_dir``; return summary."""
    run_validation = _import_run_validation()
    shape = shape_path or DEFAULT_SHAPE
    summary = run_validation(
        data_path,
        shape_path=shape,
        out_dir=out_dir,
    )
    status = "CONFORMS" if summary.get("conforms") else "NON-CONFORMING"
    print(
        f"  [{status}] violations={summary.get('n_violations')} "
        f"warnings={summary.get('n_warnings')} "
        f"→ {out_dir}"
    )
    return summary
