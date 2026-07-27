"""LM factory driven by YAML config (NRP, OpenRouter, xAI, NVIDIA, Ollama, …).

Backends and default models live in ``config/default.yaml``. Secrets come only
from environment variables named by each backend's ``env_key`` (never from YAML
values). Local backends may set ``require_api_key: false`` (e.g. Ollama).

Roles:

* **task** — generates artifacts; temperature / max_tokens from backend
  ``temperature_task`` / ``max_tokens_task``.
* **reflection** — GEPA reflection and (by default) the judge; uses
  ``temperature_reflection`` / ``max_tokens_reflection``.
"""
from __future__ import annotations

import os
from typing import Literal

import dspy

from defs.config import AppConfig, BackendConfig, get_active_config, load_app_config

Role = Literal["task", "reflection"]

# Env vars that override Ollama base URL (checked in this order).
_OLLAMA_BASE_ENV = ("OLLAMA_API_BASE", "OLLAMA_HOST")


def backend_names(cfg: AppConfig | None = None) -> tuple[str, ...]:
    cfg = cfg or get_active_config() or load_app_config()
    return cfg.backend_names()


# Backward-compatible name used by main argparse choices — refreshed when config loads.
BACKENDS: tuple[str, ...] = ("nrp", "openrouter", "xai", "nvidia", "ollama")


def refresh_backends(cfg: AppConfig) -> tuple[str, ...]:
    """Update module-level BACKENDS from config; return the new tuple."""
    global BACKENDS
    BACKENDS = cfg.backend_names()
    return BACKENDS


def _normalize_model(backend: str, model: str) -> str:
    """Backend-specific LiteLLM model string fixes."""
    m = model.strip()
    if backend == "nvidia":
        if m.startswith(("openai/", "nvidia_nim/", "custom_openai/")):
            return m
        # Integrate API is OpenAI-compatible; send full nvidia/… id upstream.
        return f"openai/{m}" if not m.startswith("openai/") else m
    if backend == "ollama":
        # Accept bare names (llama3.2) or already-prefixed ollama/ / ollama_chat/.
        if m.startswith(("ollama/", "ollama_chat/", "openai/")):
            return m
        return f"ollama/{m}"
    return m


def _ensure_http_scheme(url: str) -> str:
    """LiteLLM/httpx require an absolute URL with http(s) scheme.

    ``OLLAMA_HOST`` is often ``host:port`` (no scheme). Bare YAML values
    like ``win.lan:11434`` fail with:
    ``Request URL is missing an 'http://' or 'https://' protocol``.
    """
    u = url.strip().rstrip("/")
    if not u:
        return u
    lower = u.lower()
    if lower.startswith(("http://", "https://")):
        return u
    # host:port or host alone
    return f"http://{u}"


def _resolve_api_base(
    backend: str,
    bcfg: BackendConfig,
    api_base: str | None = None,
) -> str | None:
    """CLI override > env (ollama) > YAML api_base.

    For ollama, the result always has an ``http://`` or ``https://`` scheme.
    """
    raw: str | None = None

    if api_base is not None and str(api_base).strip():
        raw = str(api_base).strip()
    elif backend == "ollama":
        for env_name in _OLLAMA_BASE_ENV:
            val = os.environ.get(env_name)
            if val and val.strip():
                raw = val.strip()
                break

    if raw is None and bcfg.api_base:
        raw = str(bcfg.api_base).strip() or None

    if not raw:
        return None

    if backend == "ollama":
        return _ensure_http_scheme(raw)
    return raw.rstrip("/")


def _resolve_api_key(backend: str, bcfg: BackendConfig) -> str:
    """Return API key string for dspy.LM / LiteLLM.

    Cloud backends require a non-empty env value. Local backends
    (``require_api_key: false``) may use a dummy key when unset.
    """
    key: str | None = None
    if bcfg.env_key:
        key = os.environ.get(bcfg.env_key)
        if key is not None:
            key = key.strip() or None

    if key:
        return key

    if bcfg.require_api_key:
        env_name = bcfg.env_key or "(no env_key)"
        raise SystemExit(
            f"{env_name} is not set (needed for backend {backend!r})"
        )

    # LiteLLM often wants a non-empty string even when the server ignores it.
    return "ollama" if backend == "ollama" else "local"


def make_lm(
    backend: str,
    *,
    role: Role = "task",
    model: str | None = None,
    api_base: str | None = None,
    cfg: AppConfig | None = None,
) -> dspy.LM:
    """Build a ``dspy.LM`` for the given backend and role.

    ``model`` overrides the backend default for that role when set.
    ``api_base`` overrides YAML / env base URL when set.
    """
    cfg = cfg or get_active_config() or load_app_config()
    bcfg: BackendConfig = cfg.get_backend(backend)

    key = _resolve_api_key(backend, bcfg)

    if model:
        model_id = model.strip()
    elif role == "reflection":
        model_id = bcfg.reflection_model
    else:
        model_id = bcfg.task_model
    model_id = _normalize_model(backend, model_id)

    if role == "reflection":
        temperature = bcfg.temperature_reflection
        max_tokens = bcfg.max_tokens_reflection
    else:
        temperature = bcfg.temperature_task
        max_tokens = bcfg.max_tokens_task

    base = _resolve_api_base(backend, bcfg, api_base=api_base)

    kwargs: dict = dict(
        model=model_id,
        api_key=key,
        cache=False,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=bcfg.timeout,
        num_retries=bcfg.num_retries,
    )
    if base:
        kwargs["api_base"] = base

    return dspy.LM(**kwargs)


def get_task_lm(
    backend: str | None = None,
    model: str | None = None,
    api_base: str | None = None,
    cfg: AppConfig | None = None,
) -> dspy.LM:
    """LM that generates artifacts (and is optimized against)."""
    cfg = cfg or get_active_config() or load_app_config()
    return make_lm(
        backend or cfg.models.task_backend,
        role="task",
        model=model,
        api_base=api_base,
        cfg=cfg,
    )


def get_reflection_lm(
    backend: str | None = None,
    model: str | None = None,
    api_base: str | None = None,
    cfg: AppConfig | None = None,
) -> dspy.LM:
    """Strong LM for GEPA reflection and (by default) judging."""
    cfg = cfg or get_active_config() or load_app_config()
    return make_lm(
        backend or cfg.models.reflection_backend,
        role="reflection",
        model=model,
        api_base=api_base,
        cfg=cfg,
    )


def resolved_model_ids(
    *,
    task_backend: str,
    reflection_backend: str,
    task_model: str | None = None,
    reflection_model: str | None = None,
    cfg: AppConfig | None = None,
) -> dict[str, str]:
    """Return the effective LiteLLM model strings (for provenance)."""
    cfg = cfg or get_active_config() or load_app_config()
    tb = cfg.get_backend(task_backend)
    rb = cfg.get_backend(reflection_backend)
    return {
        "task_model": _normalize_model(
            task_backend, task_model or tb.task_model
        ),
        "reflection_model": _normalize_model(
            reflection_backend, reflection_model or rb.reflection_model
        ),
    }
