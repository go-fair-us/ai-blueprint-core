"""Run provenance: last-state meta + append-only history.

Written under the configured ``outputdir``:

* ``run-meta.json`` — latest overall run plus last record per command name
  (so a trial dir remembers the most recent baseline/bootstrap/gepa/compare/…)
* ``run-log.jsonl`` — one JSON object per line, full chronological history

Neither file is required to re-run optimizers; they exist so scores and flags
are not lost when comparison tables go stale or programs are mixed across trials.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from defs import paths as pathconf

META_NAME = "run-meta.json"
LOG_NAME = "run-log.jsonl"


def meta_path() -> Path:
    pathconf.ensure_output_dir()
    return pathconf.OUTPUTDIR / META_NAME


def log_path() -> Path:
    pathconf.ensure_output_dir()
    return pathconf.OUTPUTDIR / LOG_NAME


def _jsonable(obj: Any) -> Any:
    """Best-effort conversion for argparse Namespace fields / Paths / etc."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(x) for x in obj]
    if hasattr(obj, "items") and callable(obj.items):
        try:
            return {str(k): _jsonable(v) for k, v in obj.items()}
        except Exception:
            pass
    return str(obj)


def flags_from_args(args) -> dict[str, Any]:
    """Extract relevant CLI flags from an argparse Namespace."""
    keys = (
        "command", "profile", "backend", "reflection_backend", "reflection_model",
        "task_model", "judge", "seed", "num_threads", "auto", "gepa_budget",
        "workdir", "inputdir", "outputdir", "config", "n", "program",
    )
    out: dict[str, Any] = {}
    for k in keys:
        if hasattr(args, k):
            v = getattr(args, k)
            if v is not None:
                out[k] = _jsonable(v)
    # Always record resolved command name
    if "command" not in out and hasattr(args, "command"):
        out["command"] = args.command
    return out


def paths_snapshot() -> dict[str, str]:
    snap = {
        "workdir": str(pathconf.WORKDIR),
        "inputdir": str(pathconf.INPUTDIR),
        "outputdir": str(pathconf.OUTPUTDIR),
    }
    try:
        from defs.config import get_active_config
        app = get_active_config()
        if app is not None:
            snap["config_root"] = str(app.root)
            snap["config_default"] = str(app.default_path)
    except Exception:
        pass
    return snap


def data_snapshot(
    task_name: str,
    *,
    n_scenarios: int | None = None,
    n_train: int | None = None,
    n_val: int | None = None,
    n_test: int | None = None,
    scenarios_source: str | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {"task": task_name}
    read = pathconf.scenarios_read_path(task_name)
    if scenarios_source is not None:
        data["scenarios_source"] = scenarios_source
    elif read is not None:
        data["scenarios_file"] = str(read)
        data["scenarios_source"] = "file"
    else:
        data["scenarios_source"] = "seed_scenarios"
    if n_scenarios is not None:
        data["n_scenarios"] = n_scenarios
    split = {}
    if n_train is not None:
        split["train"] = n_train
    if n_val is not None:
        split["val"] = n_val
    if n_test is not None:
        split["test"] = n_test
    if split:
        data["split"] = split
    return data


def build_entry(
    *,
    command: str,
    args=None,
    task_name: str | None = None,
    data: dict | None = None,
    result: dict | None = None,
    extra: dict | None = None,
) -> dict[str, Any]:
    """Assemble one provenance record."""
    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": command,
    }
    if task_name:
        entry["task"] = task_name
    if args is not None:
        entry["flags"] = flags_from_args(args)
        # Resolved model IDs when backends are known
        try:
            from defs.config import get_active_config
            from defs.lm import resolved_model_ids
            app = get_active_config()
            if app is not None and hasattr(args, "backend"):
                entry["models"] = resolved_model_ids(
                    task_backend=args.backend,
                    reflection_backend=getattr(
                        args, "reflection_backend", app.models.reflection_backend
                    ),
                    task_model=getattr(args, "task_model", None),
                    reflection_model=getattr(args, "reflection_model", None),
                    cfg=app,
                )
        except Exception:
            pass
    entry["paths"] = paths_snapshot()
    if data:
        entry["data"] = _jsonable(data)
    if result:
        entry["result"] = _jsonable(result)
    if extra:
        entry["extra"] = _jsonable(extra)
    return entry


def record_run(entry: dict[str, Any]) -> tuple[Path, Path]:
    """Append to ``run-log.jsonl`` and merge into ``run-meta.json``.

    Returns ``(meta_path, log_path)``.
    """
    entry = _jsonable(entry)
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    mpath = meta_path()
    lpath = log_path()

    # Append-only history
    with open(lpath, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Last-state meta: overall last + last per command
    meta: dict[str, Any] = {}
    if mpath.is_file():
        try:
            meta = json.loads(mpath.read_text(encoding="utf-8"))
            if not isinstance(meta, dict):
                meta = {}
        except Exception:
            meta = {}

    commands = meta.get("commands")
    if not isinstance(commands, dict):
        commands = {}
    cmd = str(entry.get("command") or "unknown")
    commands[cmd] = entry

    meta = {
        "updated_at": entry["timestamp"],
        "last": entry,
        "commands": commands,
    }
    mpath.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return mpath, lpath


def record_from_run_result(
    args,
    task_name: str,
    rr,
    *,
    n_train: int,
    n_val: int,
    n_test: int,
    n_scenarios: int | None = None,
    command: str | None = None,
) -> tuple[Path, Path]:
    """Convenience for a single optimizer branch (baseline/bootstrap/mipro/gepa)."""
    cmd = command or getattr(args, "command", None) or getattr(rr, "name", "unknown")
    entry = build_entry(
        command=cmd,
        args=args,
        task_name=task_name,
        data=data_snapshot(
            task_name,
            n_scenarios=n_scenarios,
            n_train=n_train,
            n_val=n_val,
            n_test=n_test,
        ),
        result={
            "name": getattr(rr, "name", cmd),
            "score": getattr(rr, "score", None),
            "seconds": getattr(rr, "seconds", None),
            "total_tokens": getattr(rr, "total_tokens", None),
            "prompt_tokens": getattr(rr, "prompt_tokens", None),
            "completion_tokens": getattr(rr, "completion_tokens", None),
            "cost": getattr(rr, "cost", None),
            "artifact": getattr(rr, "artifact", None),
            "usage_by_lm": getattr(rr, "usage_by_lm", None),
        },
    )
    return record_run(entry)


def announce_provenance(meta_p: Path, log_p: Path) -> None:
    print(f"[provenance] updated {meta_p.name}  appended {log_p.name}", file=sys.stderr)
