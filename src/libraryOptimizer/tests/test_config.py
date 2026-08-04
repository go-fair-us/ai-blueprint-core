"""Config load smoke tests."""
from __future__ import annotations

from defs.config import load_app_config


def test_load_default_config():
    app = load_app_config()
    assert "nrp" in app.backend_names() or "openrouter" in app.backend_names()
    assert app.guidance.blueprint.name.endswith(".md")
    assert app.guidance.workplans.name.endswith(".md")
    assert app.data.n_scenarios >= 1
    assert app.prompts.examples_root.name == "prompt_examples"
    # In this monorepo the docs and examples should resolve on disk.
    assert app.guidance.blueprint.is_file()
    assert app.prompts.examples_root.is_dir()
