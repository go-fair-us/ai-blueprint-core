"""YAML configuration for models, run knobs, and the active goal profile.

Layout (package default)::

    config/
      default.yaml          # models, run, data, optimizers
      profile.yaml          # active goal (seed, rubric, weights, scenarios)
      profiles/             # optional recipe library (api, metadata, …)
      prompts/*.md

One optimizer, one active profile per process. Different goals = different
runs (``--profile`` and/or ``--workdir``), not a multi-task product enum.

Discovery order for the config root:

1. Explicit path (``--config`` or ``load_app_config(path=...)``)
2. ``PROMPT_OPTIMIZER_CONFIG`` environment variable
3. Package ``config/`` directory next to this package

Secrets are never read from YAML — only env var *names* (``env_key``).
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Allowed scoring components (must match tasks.base.COMPONENTS).
SCORING_COMPONENTS = ("jsonld", "openapi", "table1", "pid", "judge")

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_DIR = PACKAGE_ROOT / "config"
CONFIG_ENV = "PROMPT_OPTIMIZER_CONFIG"
ACTIVE_PROFILE_NAME = "profile.yaml"

_TEXT_SUFFIXES = {".md", ".txt", ".markdown"}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BackendConfig:
    name: str
    env_key: str
    task_model: str
    reflection_model: str
    api_base: str | None = None
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
    train_frac: float = 0.5
    val_frac: float = 0.25
    min_val: int = 3
    min_test: int = 3


@dataclass(frozen=True)
class BootstrapSection:
    metric_threshold: float = 0.7
    max_bootstrapped_demos: int = 4
    max_labeled_demos: int = 4


@dataclass(frozen=True)
class OptimizersSection:
    bootstrap: BootstrapSection = field(default_factory=BootstrapSection)


@dataclass(frozen=True)
class GenerationSection:
    output_field: str
    input_field: str
    input_desc: str
    output_desc: str
    instructions: str


@dataclass(frozen=True)
class ProfileConfig:
    """One optimization goal: seed prompt, rubric, weights, scenarios."""

    name: str
    description: str
    generation: GenerationSection
    rubric: str
    weights: dict[str, float]
    domain_context: str
    seed_scenarios: list[str]
    scenarios_file: str | None = None
    source_path: Path | None = None


# Backward-compatible alias
TaskConfig = ProfileConfig


@dataclass
class AppConfig:
    """Root configuration for a promptOptimizer run (models + knobs)."""

    root: Path
    default_path: Path
    models: ModelsSection
    run: RunSection
    data: DataSection
    optimizers: OptimizersSection
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

    def list_profile_names(self) -> list[str]:
        """Short names available under profiles/ (recipe library)."""
        profiles_dir = self.root / "profiles"
        if not profiles_dir.is_dir():
            return []
        return sorted(p.stem for p in profiles_dir.glob("*.yaml") if p.is_file())


# Process-wide loaded config (set by main after --config resolution).
_ACTIVE: AppConfig | None = None
_ACTIVE_PROFILE: ProfileConfig | None = None


def get_active_config() -> AppConfig | None:
    return _ACTIVE


def set_active_config(cfg: AppConfig | None) -> None:
    global _ACTIVE
    _ACTIVE = cfg


def get_active_profile_config() -> ProfileConfig | None:
    return _ACTIVE_PROFILE


def set_active_profile_config(profile: ProfileConfig | None) -> None:
    global _ACTIVE_PROFILE
    _ACTIVE_PROFILE = profile


# ---------------------------------------------------------------------------
# Path / text helpers
# ---------------------------------------------------------------------------

def resolve_config_root(path: str | Path | None = None) -> Path:
    """Resolve config root directory (containing default.yaml and profile.yaml)."""
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


def resolve_text(value: str | None, config_root: Path, *, field_name: str) -> str:
    """Return literal text, or contents of a sidecar file if value looks like a path."""
    if value is None:
        raise SystemExit(f"Missing required text field: {field_name}")
    text = str(value).strip()
    if not text:
        raise SystemExit(f"Empty text field: {field_name}")

    if "\n" in text:
        return text

    candidate = Path(text)
    if not candidate.is_absolute():
        candidate = (config_root / text).resolve()

    if candidate.is_file() and candidate.suffix.lower() in _TEXT_SUFFIXES:
        return candidate.read_text(encoding="utf-8").strip()

    if text.endswith(tuple(_TEXT_SUFFIXES)):
        raise SystemExit(
            f"{field_name}: referenced file not found: {config_root / text}"
        )
    return text


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _parse_backend(name: str, raw: dict[str, Any]) -> BackendConfig:
    if not isinstance(raw, dict):
        raise SystemExit(f"Backend {name!r} must be a mapping")
    for req in ("env_key", "task_model", "reflection_model"):
        if req not in raw or raw[req] in (None, ""):
            raise SystemExit(f"Backend {name!r}: missing required key {req!r}")
    return BackendConfig(
        name=name,
        env_key=str(raw["env_key"]),
        api_base=(str(raw["api_base"]) if raw.get("api_base") else None),
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
        raise SystemExit(
            f"models.task_backend {task_backend!r} not in backends "
            f"{list(backends)}"
        )
    if reflection_backend not in backends:
        raise SystemExit(
            f"models.reflection_backend {reflection_backend!r} not in backends "
            f"{list(backends)}"
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
        train_frac=float(raw.get("train_frac", 0.5)),
        val_frac=float(raw.get("val_frac", 0.25)),
        min_val=int(raw.get("min_val", 3)),
        min_test=int(raw.get("min_test", 3)),
    )


def _parse_optimizers(raw: dict[str, Any] | None) -> OptimizersSection:
    raw = raw or {}
    boot = raw.get("bootstrap") or {}
    if not isinstance(boot, dict):
        raise SystemExit("optimizers.bootstrap must be a mapping")
    return OptimizersSection(
        bootstrap=BootstrapSection(
            metric_threshold=float(boot.get("metric_threshold", 0.7)),
            max_bootstrapped_demos=int(boot.get("max_bootstrapped_demos", 4)),
            max_labeled_demos=int(boot.get("max_labeled_demos", 4)),
        )
    )


def _validate_weights(weights: dict[str, float], profile_name: str) -> dict[str, float]:
    unknown = set(weights) - set(SCORING_COMPONENTS)
    if unknown:
        raise SystemExit(
            f"Profile {profile_name!r}: unknown weight keys {sorted(unknown)}; "
            f"allowed: {SCORING_COMPONENTS}"
        )
    if not weights:
        raise SystemExit(f"Profile {profile_name!r}: weights must be non-empty")
    total = sum(weights.values())
    if abs(total - 1.0) > 1e-6:
        raise SystemExit(
            f"Profile {profile_name!r}: weights must sum to 1.0, got {total:.4f}"
        )
    return {k: float(v) for k, v in weights.items()}


def parse_profile_config(
    raw: dict[str, Any],
    config_root: Path,
    *,
    source_path: Path | None = None,
) -> ProfileConfig:
    name = str(raw.get("name") or "").strip()
    if not name:
        if source_path is not None:
            name = source_path.stem
        else:
            raise SystemExit("Profile config missing 'name'")
    description = str(raw.get("description") or name)

    gen_raw = raw.get("generation") or {}
    if not isinstance(gen_raw, dict):
        raise SystemExit(f"Profile {name!r}: generation must be a mapping")
    for req in ("output_field", "input_field", "instructions"):
        if req not in gen_raw:
            raise SystemExit(f"Profile {name!r}: generation.{req} is required")

    generation = GenerationSection(
        output_field=str(gen_raw["output_field"]),
        input_field=str(gen_raw["input_field"]),
        input_desc=str(gen_raw.get("input_desc") or gen_raw["input_field"]),
        output_desc=str(gen_raw.get("output_desc") or gen_raw["output_field"]),
        instructions=resolve_text(
            gen_raw.get("instructions"),
            config_root,
            field_name=f"{name}.generation.instructions",
        ),
    )

    scoring = raw.get("scoring") or {}
    if not isinstance(scoring, dict):
        raise SystemExit(f"Profile {name!r}: scoring must be a mapping")
    rubric = resolve_text(
        scoring.get("rubric"), config_root, field_name=f"{name}.scoring.rubric"
    )
    weights_raw = scoring.get("weights") or {}
    if not isinstance(weights_raw, dict):
        raise SystemExit(f"Profile {name!r}: scoring.weights must be a mapping")
    weights = _validate_weights(
        {str(k): float(v) for k, v in weights_raw.items()}, name
    )

    brainstorm = raw.get("brainstorm") or {}
    domain_context = str(
        (brainstorm.get("domain_context") if isinstance(brainstorm, dict) else None)
        or raw.get("domain_context")
        or ""
    ).strip()
    if not domain_context:
        raise SystemExit(f"Profile {name!r}: brainstorm.domain_context is required")

    scenarios = raw.get("scenarios") or {}
    if not isinstance(scenarios, dict):
        raise SystemExit(f"Profile {name!r}: scenarios must be a mapping")
    seeds = scenarios.get("seeds") or []
    if not isinstance(seeds, list) or not seeds:
        raise SystemExit(f"Profile {name!r}: scenarios.seeds must be a non-empty list")
    seed_scenarios = [str(s).strip() for s in seeds if str(s).strip()]
    scenarios_file = scenarios.get("file")
    if scenarios_file is not None:
        scenarios_file = str(scenarios_file)

    return ProfileConfig(
        name=name,
        description=description,
        generation=generation,
        rubric=rubric,
        weights=weights,
        domain_context=domain_context,
        seed_scenarios=seed_scenarios,
        scenarios_file=scenarios_file,
        source_path=source_path,
    )


# Backward-compatible names
parse_task_config = parse_profile_config


# ---------------------------------------------------------------------------
# Public load API
# ---------------------------------------------------------------------------

def load_app_config(path: str | Path | None = None) -> AppConfig:
    """Load root default.yaml and return AppConfig."""
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
        optimizers=_parse_optimizers(raw.get("optimizers")),
        raw=raw,
    )


def resolve_profile_path(
    app: AppConfig,
    profile: str | Path | None = None,
) -> Path:
    """Locate the profile YAML file.

    * ``None`` → ``config/profile.yaml`` (active profile for this config root)
    * path to an existing file → that file
    * short name (e.g. ``metadata``) → ``config/profiles/<name>.yaml``
    """
    if profile is None or str(profile).strip() == "":
        active = app.root / ACTIVE_PROFILE_NAME
        if active.is_file():
            return active.resolve()
        # Legacy: first profiles/*.yaml or tasks/*.yaml
        for sub in ("profiles", "tasks"):
            d = app.root / sub
            if d.is_dir():
                yamls = sorted(d.glob("*.yaml"))
                if yamls:
                    return yamls[0].resolve()
        raise SystemExit(
            f"No active profile at {active}. Create profile.yaml or pass --profile."
        )

    p = Path(str(profile)).expanduser()
    if p.is_file():
        return p.resolve()

    # Short library name
    name = str(profile).strip()
    candidates = [
        app.root / "profiles" / f"{name}.yaml",
        app.root / "profiles" / f"{name}.yml",
        app.root / ACTIVE_PROFILE_NAME if name in ("active", "default", "profile") else None,
        app.root / "tasks" / f"{name}.yaml",  # legacy
    ]
    for c in candidates:
        if c is not None and c.is_file():
            return c.resolve()

    known = app.list_profile_names()
    raise SystemExit(
        f"Profile {name!r} not found (tried path and profiles/{name}.yaml). "
        f"Library: {', '.join(known) or '(none)'}. "
        f"Active file: {app.root / ACTIVE_PROFILE_NAME}"
    )


def load_profile_config(
    profile: str | Path | None = None,
    app: AppConfig | None = None,
) -> ProfileConfig:
    """Load the active or named profile YAML."""
    app = app or get_active_config()
    if app is None:
        app = load_app_config()
    path = resolve_profile_path(app, profile)
    raw = _load_yaml(path)
    raw.setdefault("name", path.stem if path.stem != "profile" else "run")
    return parse_profile_config(raw, app.root, source_path=path)


def load_task_config(name: str, app: AppConfig | None = None) -> ProfileConfig:
    """Deprecated alias: load a library profile by short name."""
    return load_profile_config(name, app)


def announce_config(app: AppConfig, profile: ProfileConfig | None = None) -> None:
    lib = ",".join(app.list_profile_names()) or "(none)"
    if profile is not None:
        src = profile.source_path.name if profile.source_path else "?"
        print(
            f"[config] root={app.root} default={app.default_path.name} "
            f"profile={profile.name!r} ({src}) library=[{lib}] "
            f"backends={','.join(app.backend_names())}",
            file=sys.stderr,
        )
    else:
        print(
            f"[config] root={app.root} default={app.default_path.name} "
            f"library=[{lib}] backends={','.join(app.backend_names())}",
            file=sys.stderr,
        )
