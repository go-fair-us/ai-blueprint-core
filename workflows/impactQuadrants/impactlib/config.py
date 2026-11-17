"""impact.yaml loading with built-in defaults."""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

DEFAULTS = {
    "sources": ["facet-check"],
    "gap_verdicts": {"facet-check": ["absent"]},
    "categories": {},
    "quadrants": {"top_left": "Quick wins", "top_right": "Big bets",
                  "bottom_left": "Easy follow-ons", "bottom_right": "Plan for later"},
    "backend": "pi",
    "pi": {"bin": "pi", "provider": "nrp", "model": "deepseek-v4-flash",
           "args": ["--print", "--no-session", "--no-approve", "--no-context-files", "--no-mcp"],
           "timeout": 900},
    "openai": {"base_url_env": "IMPACT_OPENAI_BASE_URL", "api_key_env": "IMPACT_OPENAI_API_KEY",
               "model_env": "IMPACT_MODEL", "temperature": 0.2, "timeout": 300},
    "assess": {"samples": 1, "max_attempts": 3, "variance_threshold": 0.35},
    "report": {"title": "Where to start: agent-access gaps",
               "org": "NIAID Blueprint repository herd", "rename": {}},
    "rubric": str(ROOT / "rubric.md"),
    "stub_defaults": str(ROOT / "stub_defaults.yaml"),
}


def deep_merge(base: dict, extra: dict) -> dict:
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_merge(base[k], v)
        else:
            base[k] = v
    return base


def load(path: Path | str | None = None) -> dict:
    cfg = copy.deepcopy(DEFAULTS)
    p = Path(path) if path else ROOT / "impact.yaml"
    if p.is_file():
        deep_merge(cfg, yaml.safe_load(p.read_text()) or {})
    elif path:
        raise SystemExit(f"config {p} not found")
    return cfg
