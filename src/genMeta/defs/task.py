"""CLI / env resolution for genMeta runs."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, Mapping, Optional

from defs.config import (
    DEFAULT_MAX_ITERS,
    DEFAULT_MODELS,
    DEFAULT_RUNS_DIR,
    DEFAULT_TIMEOUT_S,
    ROLE_EXTRACTOR,
    ROLE_REPAIRER,
)

_PI_AUTH_PATH = Path.home() / ".pi" / "agent" / "auth.json"


def resolve_models(
    extractor: Optional[str] = None,
    repairer: Optional[str] = None,
) -> Dict[str, str]:
    """Model map for extractor and repairer panes."""
    return {
        ROLE_EXTRACTOR: extractor
        or os.environ.get("GENMETA_MODEL_EXTRACTOR", DEFAULT_MODELS[ROLE_EXTRACTOR]),
        ROLE_REPAIRER: repairer
        or os.environ.get("GENMETA_MODEL_REPAIRER", DEFAULT_MODELS[ROLE_REPAIRER]),
    }


def resolve_runs_dir(cli: Optional[str] = None) -> Path:
    if cli:
        return Path(cli).resolve()
    env = os.environ.get("GENMETA_RUNS_DIR")
    if env:
        return Path(env).resolve()
    return DEFAULT_RUNS_DIR.resolve()


def resolve_max_iters(cli: Optional[int] = None) -> int:
    if cli is not None:
        return max(1, int(cli))
    env = os.environ.get("GENMETA_MAX_ITERS")
    if env:
        return max(1, int(env))
    return DEFAULT_MAX_ITERS


def resolve_timeout(cli: Optional[int] = None) -> int:
    if cli is not None:
        return max(30, int(cli))
    env = os.environ.get("GENMETA_TIMEOUT")
    if env:
        return max(30, int(env))
    return DEFAULT_TIMEOUT_S


def _has_openrouter_auth() -> bool:
    if os.environ.get("OPENROUTER_API_KEY", "").strip():
        return True
    try:
        if not _PI_AUTH_PATH.is_file():
            return False
        data = json.loads(_PI_AUTH_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return False
    if not isinstance(data, dict):
        return False
    entry = data.get("openrouter")
    if entry is None:
        return False
    if isinstance(entry, str):
        return bool(entry.strip())
    if isinstance(entry, dict):
        for key in ("apiKey", "api_key", "key", "access", "token"):
            val = entry.get(key)
            if isinstance(val, str) and val.strip():
                return True
        return bool(entry)
    return bool(entry)


def warn_openrouter_credentials(models: Mapping[str, str]) -> None:
    openrouter_slots = [
        f"{name}={spec}"
        for name, spec in models.items()
        if isinstance(spec, str) and spec.lower().startswith("openrouter/")
    ]
    if not openrouter_slots:
        return
    if _has_openrouter_auth():
        return
    slots = ", ".join(openrouter_slots)
    print(
        "Warning: OpenRouter model(s) selected without detectable credentials:\n"
        f"  {slots}\n"
        "  Set OPENROUTER_API_KEY in the environment that starts Herdr, or run\n"
        "  `pi` interactively and `/login openrouter`.\n"
        "  Pi panes inherit Herdr's environment, not only the orchestrator shell.",
        file=sys.stderr,
    )
