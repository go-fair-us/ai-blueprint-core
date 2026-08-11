"""Run directory layout and JSON-LD recovery helpers."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Sequence

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


def mtime(path: Path) -> float:
    """Return file mtime, or 0.0 if missing."""
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def is_parseable_jsonld(path: Path) -> bool:
    """True if path exists and parses as a JSON object (Dataset-like preferred)."""
    if not path.is_file() or path.stat().st_size < 3:
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return False
    return isinstance(data, dict) and bool(data)


def artifact_ready(path: Path, *, not_before: float, min_size: int = 1) -> bool:
    """True if path exists, non-trivial, and mtime is at/after ``not_before``."""
    try:
        st = path.stat()
    except OSError:
        return False
    if st.st_size < min_size:
        return False
    # Allow small clock skew between host and writer.
    return st.st_mtime >= (not_before - 2.0)


def mtimes_stable(paths: Sequence[Path], *, stable_s: float, poll_s: float = 0.5) -> bool:
    """True if every path keeps the same mtime for ``stable_s`` seconds."""
    if stable_s <= 0:
        return True
    first = {p: mtime(p) for p in paths}
    if any(v <= 0 for v in first.values()):
        return False
    deadline = time.time() + stable_s
    while time.time() < deadline:
        time.sleep(min(poll_s, max(0.1, deadline - time.time())))
        for p, prev in first.items():
            if mtime(p) != prev:
                return False
    return True


def wait_for_extract_artifacts(
    run_dir: Path,
    *,
    not_before: float,
    timeout_s: float,
    require_notes: bool = True,
    poll_s: float = 2.0,
    stable_s: float = 3.0,
) -> Path:
    """Block until extract deliverables exist and are stable.

    Returns the path to ``record.jsonld``. Raises TimeoutError on deadline.
    """
    record = record_path(run_dir)
    notes = notes_path(run_dir)
    deadline = time.time() + max(1.0, timeout_s)
    last_log = 0.0

    while time.time() < deadline:
        rec_ok = artifact_ready(record, not_before=not_before, min_size=3) and is_parseable_jsonld(
            record
        )
        notes_ok = (not require_notes) or artifact_ready(notes, not_before=not_before, min_size=1)
        if rec_ok and notes_ok:
            paths = [record] + ([notes] if require_notes else [])
            if mtimes_stable(paths, stable_s=stable_s):
                # Re-check parse after stability window (avoid mid-write).
                if is_parseable_jsonld(record):
                    print(f"  extract artifacts ready → {record}")
                    return record
        now = time.time()
        if now - last_log >= 30.0:
            print(
                f"  waiting for extract artifacts "
                f"(record={rec_ok} notes={notes_ok}; "
                f"{int(deadline - now)}s left)…"
            )
            last_log = now
        time.sleep(poll_s)

    raise TimeoutError(
        f"Timed out after {timeout_s}s waiting for {RECORD_NAME}"
        + (f" and {NOTES_NAME}" if require_notes else "")
        + f" under {run_dir}"
    )


def wait_for_record_update(
    run_dir: Path,
    *,
    previous_mtime: float,
    not_before: float,
    timeout_s: float,
    poll_s: float = 2.0,
    stable_s: float = 3.0,
) -> Path:
    """Block until ``record.jsonld`` is rewritten after a repair turn.

    Accepts a file whose mtime is greater than ``previous_mtime`` (and
    ``not_before``), parses as JSON, and stays stable briefly.
    """
    record = record_path(run_dir)
    deadline = time.time() + max(1.0, timeout_s)
    last_log = 0.0
    floor = max(previous_mtime, not_before - 2.0)

    while time.time() < deadline:
        ready = (
            artifact_ready(record, not_before=not_before, min_size=3)
            and mtime(record) > floor
            and is_parseable_jsonld(record)
        )
        if ready and mtimes_stable([record], stable_s=stable_s):
            if is_parseable_jsonld(record) and mtime(record) > floor:
                print(f"  repaired record ready → {record}")
                return record
        now = time.time()
        if now - last_log >= 30.0:
            print(
                f"  waiting for repaired {RECORD_NAME} "
                f"(mtime_floor={floor:.0f}; {int(deadline - now)}s left)…"
            )
            last_log = now
        time.sleep(poll_s)

    raise TimeoutError(
        f"Timed out after {timeout_s}s waiting for updated {RECORD_NAME} under {run_dir}"
    )
