"""LM factory driven by YAML config (NRP, OpenRouter, xAI, Ollama, …)."""
from __future__ import annotations

import os
from typing import Literal

import dspy

from defs.config import AppConfig, BackendConfig, get_active_config, load_app_config

Role = Literal["task", "reflection"]

_OLLAMA_BASE_ENV = ("OLLAMA_API_BASE", "OLLAMA_HOST")

BACKENDS: tuple[str, ...] = ("nrp", "openrouter", "xai", "ollama")


def refresh_backends(cfg: AppConfig) -> tuple[str, ...]:
    global BACKENDS
    BACKENDS = cfg.backend_names()
    return BACKENDS


def _normalize_model(backend: str, model: str) -> str:
    m = model.strip()
    if backend == "ollama":
        if m.startswith(("ollama/", "ollama_chat/", "openai/")):
            return m
        return f"ollama/{m}"
    return m


def _ensure_http_scheme(url: str) -> str:
    u = url.strip().rstrip("/")
    if not u:
        return u
    lower = u.lower()
    if lower.startswith(("http://", "https://")):
        return u
    return f"http://{u}"


def _resolve_api_base(
    backend: str,
    bcfg: BackendConfig,
    api_base: str | None = None,
) -> str | None:
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
    return "ollama" if backend == "ollama" else "local"


def make_lm(
    backend: str,
    *,
    role: Role = "task",
    model: str | None = None,
    api_base: str | None = None,
    cfg: AppConfig | None = None,
) -> dspy.LM:
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
    cfg = cfg or get_active_config() or load_app_config()
    return make_lm(
        backend or cfg.models.reflection_backend,
        role="reflection",
        model=model,
        api_base=api_base,
        cfg=cfg,
    )
