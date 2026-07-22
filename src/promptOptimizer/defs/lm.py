"""LM factory driven by YAML config (NRP, OpenRouter, xAI, NVIDIA, …).

Backends and default models live in ``config/default.yaml``. Secrets come only
from environment variables named by each backend's ``env_key`` (never from YAML
values).

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


def backend_names(cfg: AppConfig | None = None) -> tuple[str, ...]:
    cfg = cfg or get_active_config() or load_app_config()
    return cfg.backend_names()


# Backward-compatible name used by main argparse choices — refreshed when config loads.
BACKENDS: tuple[str, ...] = ("nrp", "openrouter", "xai", "nvidia")


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
    return m


def make_lm(
    backend: str,
    *,
    role: Role = "task",
    model: str | None = None,
    cfg: AppConfig | None = None,
) -> dspy.LM:
    """Build a ``dspy.LM`` for the given backend and role.

    ``model`` overrides the backend default for that role when set.
    """
    cfg = cfg or get_active_config() or load_app_config()
    bcfg: BackendConfig = cfg.get_backend(backend)

    key = os.environ.get(bcfg.env_key)
    if not key:
        raise SystemExit(
            f"{bcfg.env_key} is not set (needed for backend {backend!r}, role {role})"
        )

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

    kwargs: dict = dict(
        model=model_id,
        api_key=key,
        cache=False,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=bcfg.timeout,
        num_retries=bcfg.num_retries,
    )
    if bcfg.api_base:
        kwargs["api_base"] = bcfg.api_base

    return dspy.LM(**kwargs)


def get_task_lm(
    backend: str | None = None,
    model: str | None = None,
    cfg: AppConfig | None = None,
) -> dspy.LM:
    """LM that generates artifacts (and is optimized against)."""
    cfg = cfg or get_active_config() or load_app_config()
    return make_lm(
        backend or cfg.models.task_backend,
        role="task",
        model=model,
        cfg=cfg,
    )


def get_reflection_lm(
    backend: str | None = None,
    model: str | None = None,
    cfg: AppConfig | None = None,
) -> dspy.LM:
    """Strong LM for GEPA reflection and (by default) judging."""
    cfg = cfg or get_active_config() or load_app_config()
    return make_lm(
        backend or cfg.models.reflection_backend,
        role="reflection",
        model=model,
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
