"""YAML configuration for models, run knobs, and guidance paths."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from defs.paths import PACKAGE_ROOT, REPO_ROOT

DEFAULT_CONFIG_DIR = PACKAGE_ROOT / "config"
CONFIG_ENV = "LIBRARY_OPTIMIZER_CONFIG"


@dataclass(frozen=True)
class BackendConfig:
    name: str
    env_key: str | None
    task_model: str
    reflection_model: str
    api_base: str | None = None
    require_api_key: bool = True
    temperature_task: float = 0.0
    temperature_reflection: float = 1.0
    max_tokens_task: int = 16_000
    max_tokens_reflection: int = 12_000
    timeout: int = 180
    num_retries: int = 2


@dataclass(frozen=True)
class ModelsSection:
    task_backend: str
    reflection_backend: str
    judge: str
    backends: dict[str, BackendConfig]


@dataclass(frozen=True)
class RunSection:
    seed: int = 0
    num_threads: int = 8
    auto: str = "light"
    gepa_budget: int | None = None


@dataclass(frozen=True)
class DataSection:
    n_scenarios: int = 20
    train_frac: float = 0.5
    val_frac: float = 0.25
    min_val: int = 3
    min_test: int = 3


@dataclass(frozen=True)
class GuidanceSection:
    blueprint: Path
    workplans: Path
    max_chars: int = 14_000
    keep_keywords: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PromptsSection:
    examples_root: Path


@dataclass
class AppConfig:
    root: Path
    default_path: Path
    models: ModelsSection
    run: RunSection
    data: DataSection
    guidance: GuidanceSection
    prompts: PromptsSection
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    def backend_names(self) -> tuple[str, ...]:
        return tuple(self.models.backends.keys())

    def get_backend(self, name: str) -> BackendConfig:
        if name not in self.models.backends:
            known = ", ".join(self.backend_names()) or "(none)"
            raise SystemExit(
                f"Unknown backend {name!r}. Configured backends: {known}"
            )
        return self.models.backends[name]


_ACTIVE: AppConfig | None = None


def get_active_config() -> AppConfig | None:
    return _ACTIVE


def set_active_config(cfg: AppConfig | None) -> None:
    global _ACTIVE
    _ACTIVE = cfg


def resolve_config_root(path: str | Path | None = None) -> Path:
    if path is not None:
        p = Path(path).expanduser().resolve()
        if p.is_file():
            return p.parent
        if p.is_dir():
            return p
        raise SystemExit(f"Config path does not exist: {p}")

    env = os.environ.get(CONFIG_ENV)
    if env:
        p = Path(env).expanduser().resolve()
        if p.is_file():
            return p.parent
        if p.is_dir():
            return p
        raise SystemExit(
            f"{CONFIG_ENV}={env!r} does not exist (file or directory expected)"
        )

    if DEFAULT_CONFIG_DIR.is_dir() and (DEFAULT_CONFIG_DIR / "default.yaml").is_file():
        return DEFAULT_CONFIG_DIR.resolve()

    raise SystemExit(
        f"No config found. Expected {DEFAULT_CONFIG_DIR / 'default.yaml'} "
        f"or set --config / {CONFIG_ENV}."
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"Config file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise SystemExit(f"Config root must be a mapping: {path}")
    return data


def _resolve_doc_path(value: str) -> Path:
    p = Path(value).expanduser()
    if p.is_absolute():
        return p
    return (REPO_ROOT / p).resolve()


def _parse_backend(name: str, raw: dict[str, Any]) -> BackendConfig:
    if not isinstance(raw, dict):
        raise SystemExit(f"Backend {name!r} must be a mapping")
    for req in ("task_model", "reflection_model"):
        if req not in raw or raw[req] in (None, ""):
            raise SystemExit(f"Backend {name!r}: missing required key {req!r}")

    require_api_key = bool(raw.get("require_api_key", True))
    env_raw = raw.get("env_key")
    if env_raw in (None, ""):
        if require_api_key:
            raise SystemExit(
                f"Backend {name!r}: missing required key 'env_key' "
                f"(or set require_api_key: false for local backends)"
            )
        env_key: str | None = None
    else:
        env_key = str(env_raw)

    return BackendConfig(
        name=name,
        env_key=env_key,
        api_base=(str(raw["api_base"]) if raw.get("api_base") else None),
        require_api_key=require_api_key,
        task_model=str(raw["task_model"]),
        reflection_model=str(raw["reflection_model"]),
        temperature_task=float(raw.get("temperature_task", 0.0)),
        temperature_reflection=float(raw.get("temperature_reflection", 1.0)),
        max_tokens_task=int(raw.get("max_tokens_task", 16_000)),
        max_tokens_reflection=int(raw.get("max_tokens_reflection", 12_000)),
        timeout=int(raw.get("timeout", 180)),
        num_retries=int(raw.get("num_retries", 2)),
    )


def _parse_models(raw: dict[str, Any] | None) -> ModelsSection:
    raw = raw or {}
    backends_raw = raw.get("backends") or {}
    if not isinstance(backends_raw, dict) or not backends_raw:
        raise SystemExit("models.backends must be a non-empty mapping")
    backends = {
        name: _parse_backend(name, entry)
        for name, entry in backends_raw.items()
    }
    task_backend = str(raw.get("task_backend", next(iter(backends))))
    reflection_backend = str(raw.get("reflection_backend", task_backend))
    judge = str(raw.get("judge", "reflection"))
    if judge not in ("task", "reflection"):
        raise SystemExit(f"models.judge must be 'task' or 'reflection', got {judge!r}")
    if task_backend not in backends:
        raise SystemExit(f"models.task_backend {task_backend!r} not in backends")
    if reflection_backend not in backends:
        raise SystemExit(
            f"models.reflection_backend {reflection_backend!r} not in backends"
        )
    return ModelsSection(
        task_backend=task_backend,
        reflection_backend=reflection_backend,
        judge=judge,
        backends=backends,
    )


def _parse_run(raw: dict[str, Any] | None) -> RunSection:
    raw = raw or {}
    budget = raw.get("gepa_budget", None)
    if budget is not None:
        budget = int(budget)
    auto = str(raw.get("auto", "light"))
    if auto not in ("light", "medium", "heavy"):
        raise SystemExit(f"run.auto must be light|medium|heavy, got {auto!r}")
    return RunSection(
        seed=int(raw.get("seed", 0)),
        num_threads=int(raw.get("num_threads", 8)),
        auto=auto,
        gepa_budget=budget,
    )


def _parse_data(raw: dict[str, Any] | None) -> DataSection:
    raw = raw or {}
    return DataSection(
        n_scenarios=int(raw.get("n_scenarios", 20)),
        train_frac=float(raw.get("train_frac", 0.5)),
        val_frac=float(raw.get("val_frac", 0.25)),
        min_val=int(raw.get("min_val", 3)),
        min_test=int(raw.get("min_test", 3)),
    )


def _parse_guidance(raw: dict[str, Any] | None) -> GuidanceSection:
    raw = raw or {}
    bp = raw.get("blueprint") or "docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md"
    wp = raw.get("workplans") or "docs/WorkPlans/20260515_Work-Plans_Supplementary_DSJ.md"
    keys = raw.get("keep_keywords") or []
    if not isinstance(keys, list):
        raise SystemExit("guidance.keep_keywords must be a list")
    return GuidanceSection(
        blueprint=_resolve_doc_path(str(bp)),
        workplans=_resolve_doc_path(str(wp)),
        max_chars=int(raw.get("max_chars", 14_000)),
        keep_keywords=[str(k) for k in keys],
    )


def _parse_prompts(raw: dict[str, Any] | None) -> PromptsSection:
    raw = raw or {}
    root = raw.get("examples_root") or "okf/prompt_examples"
    return PromptsSection(examples_root=_resolve_doc_path(str(root)))


def load_app_config(path: str | Path | None = None) -> AppConfig:
    root = resolve_config_root(path)
    if path is not None:
        p = Path(path).expanduser().resolve()
        default_path = p if p.is_file() else root / "default.yaml"
    else:
        env = os.environ.get(CONFIG_ENV)
        if env:
            ep = Path(env).expanduser().resolve()
            default_path = ep if ep.is_file() else root / "default.yaml"
        else:
            default_path = root / "default.yaml"

    raw = _load_yaml(default_path)
    return AppConfig(
        root=root,
        default_path=default_path,
        models=_parse_models(raw.get("models")),
        run=_parse_run(raw.get("run")),
        data=_parse_data(raw.get("data")),
        guidance=_parse_guidance(raw.get("guidance")),
        prompts=_parse_prompts(raw.get("prompts")),
        raw=raw,
    )


def announce_config(app: AppConfig) -> None:
    print(
        f"[config] root={app.root} default={app.default_path.name} "
        f"backends={','.join(app.backend_names())} "
        f"examples={app.prompts.examples_root}",
        file=sys.stderr,
    )
