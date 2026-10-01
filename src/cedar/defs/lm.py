"""Small LM factory (NRP / OpenRouter / xAI / Ollama). Secrets from env only."""
from __future__ import annotations

import os
from dataclasses import dataclass

import dspy

BACKENDS = ("nrp", "openrouter", "xai", "ollama")


@dataclass(frozen=True)
class Backend:
    env_key: str | None
    task_model: str
    api_base: str | None = None
    require_api_key: bool = True
    temperature: float = 0.0
    max_tokens: int = 16000
    timeout: int = 180


_BACKENDS: dict[str, Backend] = {
    "nrp": Backend(
        env_key="NRP_API_KEY",
        task_model="custom_openai/qwen3",
        api_base="https://ellm.nrp-nautilus.io/v1",
    ),
    "openrouter": Backend(
        env_key="OPENROUTER_API_KEY",
        task_model="openrouter/tencent/hy3:free",
        api_base="https://openrouter.ai/api/v1",
    ),
    "xai": Backend(
        env_key="XAI_API_KEY",
        task_model="xai/grok-4.5",
    ),
    "ollama": Backend(
        env_key="OLLAMA_API_KEY",
        task_model="ollama/qwen3:8b",
        api_base="http://localhost:11434",
        require_api_key=False,
        timeout=300,
    ),
}


def _normalize_model(backend: str, model: str) -> str:
    m = model.strip()
    if backend == "ollama" and not m.startswith(("ollama/", "ollama_chat/", "openai/")):
        return f"ollama/{m}"
    return m


def make_task_lm(
    backend: str,
    *,
    model: str | None = None,
    api_base: str | None = None,
) -> dspy.LM:
    if backend not in _BACKENDS:
        raise SystemExit(f"unknown backend {backend!r}; choose from {BACKENDS}")
    cfg = _BACKENDS[backend]
    key = None
    if cfg.env_key:
        key = (os.environ.get(cfg.env_key) or "").strip() or None
    if cfg.require_api_key and not key:
        raise SystemExit(f"{cfg.env_key} is not set (needed for backend {backend!r})")
    if not key:
        key = "ollama" if backend == "ollama" else "local"
    model_id = _normalize_model(backend, model or cfg.task_model)
    base = (api_base or os.environ.get("OLLAMA_API_BASE") or os.environ.get("OLLAMA_HOST") or cfg.api_base)
    if backend == "ollama" and base:
        base = base if base.startswith(("http://", "https://")) else f"http://{base}"
        base = base.rstrip("/")
    kwargs: dict = dict(
        model=model_id,
        api_key=key,
        cache=False,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
        timeout=cfg.timeout,
        num_retries=1,
    )
    if base:
        kwargs["api_base"] = base
    return dspy.LM(**kwargs)


def configure_lm(backend: str, *, model: str | None = None, api_base: str | None = None) -> dspy.LM:
    lm = make_task_lm(backend, model=model, api_base=api_base)
    dspy.configure(lm=lm, track_usage=True)
    return lm
