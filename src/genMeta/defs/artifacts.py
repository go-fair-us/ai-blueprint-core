"""Run directory layout and JSON-LD recovery helpers."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

RECORD_NAME = "record.jsonld"
NOTES_NAME = "notes.md"


def new_run_dir(runs_root: Path, label: Optional[str] = None) -> Path:
    runs_root.mkdir(parents=True, exist_ok=True)
    if label is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        label = f"genmeta-{stamp}"
    path = runs_root / label
    path.mkdir(parents=True, exist_ok=False)
    (path / "validation").mkdir(exist_ok=True)
    return path


def record_path(run_dir: Path) -> Path:
    return run_dir / RECORD_NAME


def notes_path(run_dir: Path) -> Path:
    return run_dir / NOTES_NAME


def validation_iter_dir(run_dir: Path, iteration: int) -> Path:
    d = run_dir / "validation" / f"iter-{iteration:02d}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_task_snapshot(
    run_dir: Path,
    *,
    url: str,
    models: dict[str, str],
    max_iters: int,
    repo_root: Path,
) -> Path:
    path = run_dir / "00-task.txt"
    lines = [
        f"url={url}",
        f"max_iters={max_iters}",
        f"repo_root={repo_root}",
        f"models={json.dumps(models)}",
        f"generated={datetime.now(timezone.utc).isoformat()}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


_FENCED_JSON = re.compile(
    r"```(?:json|jsonld)?\s*\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)


def extract_jsonld_from_text(text: str) -> Optional[dict[str, Any]]:
    """Best-effort: last fenced JSON block that looks like a Dataset record."""
    candidates: list[str] = []
    for match in _FENCED_JSON.finditer(text):
        candidates.append(match.group(1).strip())
    # Also try whole-text JSON
    stripped = text.strip()
    if stripped.startswith("{"):
        candidates.append(stripped)

    for blob in reversed(candidates):
        try:
            data = json.loads(blob)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        # Heuristic: Dataset-like
        type_val = data.get("@type") or data.get("type")
        if type_val == "Dataset" or (
            isinstance(type_val, list) and "Dataset" in type_val
        ):
            return data
        if "@context" in data and ("name" in data or "description" in data):
            return data
    return None


def ensure_record_jsonld(
    run_dir: Path,
    *,
    transcript: str = "",
) -> Path:
    """Ensure ``record.jsonld`` exists; recover from transcript if needed.

    Raises FileNotFoundError if neither a file nor recoverable JSON exists.
    """
    path = record_path(run_dir)
    if path.is_file() and path.stat().st_size > 2:
        # Validate it parses
        try:
            json.loads(path.read_text(encoding="utf-8"))
            return path
        except json.JSONDecodeError:
            pass

    recovered = extract_jsonld_from_text(transcript) if transcript else None
    if recovered is None:
        raise FileNotFoundError(
            f"No valid {RECORD_NAME} in {run_dir} and could not recover "
            "JSON-LD from the agent transcript."
        )
    path.write_text(json.dumps(recovered, indent=2) + "\n", encoding="utf-8")
    print(f"  recovered {RECORD_NAME} from transcript → {path}")
    return path


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))
