"""Unit tests for YAML config + single-profile loading (no live API calls)."""
from __future__ import annotations

import pytest

from defs.config import (
    DEFAULT_CONFIG_DIR,
    load_app_config,
    load_profile_config,
    resolve_text,
    set_active_config,
    set_active_profile_config,
)
from defs.lm import (
    _ensure_http_scheme,
    make_lm,
    refresh_backends,
    resolved_model_ids,
)
from tasks import clear_task_cache, get_task, list_profiles, set_active_profile
from tasks.base import task_from_config


@pytest.fixture
def app():
    clear_task_cache()
    cfg = load_app_config(DEFAULT_CONFIG_DIR)
    set_active_config(cfg)
    refresh_backends(cfg)
    # Activate default profile.yaml
    pc = load_profile_config(None, cfg)
    set_active_profile(pc)
    yield cfg
    set_active_config(None)
    set_active_profile_config(None)
    clear_task_cache()


def test_default_config_has_xai_and_core_backends(app):
    names = app.backend_names()
    assert "nrp" in names
    assert "openrouter" in names
    assert "xai" in names
    assert "ollama" in names
    xai = app.get_backend("xai")
    assert xai.env_key == "XAI_API_KEY"
    assert xai.task_model.startswith("xai/")
    assert xai.require_api_key is True


def test_ollama_backend_config(app):
    ollama = app.get_backend("ollama")
    assert ollama.require_api_key is False
    assert ollama.api_base  # URL configured (host may be customized)
    assert ollama.task_model.startswith("ollama/")
    assert ollama.reflection_model.startswith("ollama/")


def test_active_profile_loads(app):
    pc = load_profile_config(None, app)
    assert pc.name == "api"
    assert abs(sum(pc.weights.values()) - 1.0) < 1e-6
    assert "openapi" in pc.weights
    assert len(pc.seed_scenarios) >= 4
    assert pc.source_path is not None
    assert pc.source_path.name == "profile.yaml"


def test_library_profiles(app):
    assert "api" in list_profiles()
    assert "metadata" in list_profiles()
    meta = load_profile_config("metadata", app)
    assert meta.name == "metadata"
    assert "openapi" not in meta.weights
    assert abs(sum(meta.weights.values()) - 1.0) < 1e-6


def test_resolve_text_sidecar(app):
    text = resolve_text(
        "prompts/api.seed.md", app.root, field_name="test"
    )
    assert "JSON-LD" in text or "Blueprint" in text


def test_resolve_text_inline(app):
    text = resolve_text("just a seed prompt", app.root, field_name="test")
    assert text == "just a seed prompt"


def test_get_task_active_profile(app):
    task = get_task()
    assert task.name == "api"
    assert task.output_field == "api_example"
    from defs.program import ArtifactGenerator
    from defs.prompts import extract

    prog = ArtifactGenerator(task)
    extracted = extract(prog)
    assert extracted
    assert "Blueprint" in extracted[0]["instructions"] or "JSON-LD" in extracted[0]["instructions"]


def test_get_task_named_profile(app):
    task = get_task("metadata")
    assert task.name == "metadata"
    assert task.output_field == "metadata_record"


def test_make_lm_requires_env(app, monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    with pytest.raises(SystemExit, match="XAI_API_KEY"):
        make_lm("xai", role="task", cfg=app)


def test_make_lm_xai_kwargs(app, monkeypatch):
    monkeypatch.setenv("XAI_API_KEY", "test-key-not-real")
    lm = make_lm("xai", role="task", cfg=app)
    assert "xai" in str(lm.model).lower() or "grok" in str(lm.model).lower()


def test_make_lm_openrouter_with_override(app, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-not-real")
    lm = make_lm(
        "openrouter",
        role="reflection",
        model="openrouter/anthropic/claude-sonnet-4",
        cfg=app,
    )
    assert "claude" in str(lm.model).lower() or "anthropic" in str(lm.model).lower()


def test_resolved_model_ids(app):
    ids = resolved_model_ids(
        task_backend="nrp",
        reflection_backend="xai",
        cfg=app,
    )
    assert "qwen" in ids["task_model"] or "custom_openai" in ids["task_model"]
    assert ids["reflection_model"].startswith("xai/")


def test_make_lm_ollama_without_api_key(app, monkeypatch):
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_API_BASE", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    lm = make_lm("ollama", role="task", cfg=app)
    assert str(lm.model).startswith("ollama/")
    base = lm.kwargs.get("api_base") or ""
    assert base.startswith(("http://", "https://"))
    assert lm.kwargs.get("api_key") == "ollama"


def test_make_lm_ollama_model_and_api_base_override(app, monkeypatch):
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_API_BASE", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    lm = make_lm(
        "ollama",
        role="task",
        model="qwen2.5:14b",  # bare name → ollama/ prefix
        api_base="http://192.168.1.10:11434",
        cfg=app,
    )
    assert lm.model == "ollama/qwen2.5:14b"
    assert lm.kwargs.get("api_base") == "http://192.168.1.10:11434"


def test_make_lm_ollama_env_api_base(app, monkeypatch):
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    monkeypatch.setenv("OLLAMA_API_BASE", "http://10.0.0.5:11434/")
    lm = make_lm("ollama", role="reflection", cfg=app)
    # Trailing slash stripped; env wins over YAML default.
    assert lm.kwargs.get("api_base") == "http://10.0.0.5:11434"


def test_ensure_http_scheme():
    assert _ensure_http_scheme("http://localhost:11434") == "http://localhost:11434"
    assert _ensure_http_scheme("https://remote:11434/") == "https://remote:11434"
    assert _ensure_http_scheme("win.lan:11434") == "http://win.lan:11434"
    assert _ensure_http_scheme("127.0.0.1:11434") == "http://127.0.0.1:11434"


def test_make_lm_ollama_bare_host_api_base(app, monkeypatch):
    """Bare host:port (common OLLAMA_HOST form) must get http:// for LiteLLM."""
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_API_BASE", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    lm = make_lm(
        "ollama",
        role="task",
        api_base="win.lan:11434",
        cfg=app,
    )
    assert lm.kwargs.get("api_base") == "http://win.lan:11434"


def test_make_lm_ollama_host_env_without_scheme(app, monkeypatch):
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_API_BASE", raising=False)
    monkeypatch.setenv("OLLAMA_HOST", "0.0.0.0:11434")
    lm = make_lm("ollama", role="task", cfg=app)
    assert lm.kwargs.get("api_base") == "http://0.0.0.0:11434"


def test_resolved_model_ids_ollama_bare_name(app):
    ids = resolved_model_ids(
        task_backend="ollama",
        reflection_backend="ollama",
        task_model="mistral",
        reflection_model="ollama_chat/mistral",
        cfg=app,
    )
    assert ids["task_model"] == "ollama/mistral"
    assert ids["reflection_model"] == "ollama_chat/mistral"


def test_task_from_config_signature(app):
    tc = load_profile_config("metadata", app)
    task = task_from_config(tc)
    assert task.input_field == "task_description"
    assert task.output_field == "metadata_record"
