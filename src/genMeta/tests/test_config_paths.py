"""Skill and prompt path wiring for genMeta (no Herdr required)."""

from __future__ import annotations

import sys
from pathlib import Path

GENMETA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GENMETA))

from defs.config import (  # noqa: E402
    DEFAULT_SHAPE,
    EXTRACT_SKILL,
    EXTRACTION_WORKFLOW,
    PROMPTS_DIR,
    SKILLS_ROOT,
    VALIDATE_SCRIPT,
    VALIDATE_SKILL,
    VALIDATION_WORKFLOW,
    assert_skill_paths,
    render_prompt,
)


def test_skills_live_under_niaid_blueprint() -> None:
    assert SKILLS_ROOT.name == "skills"
    assert SKILLS_ROOT.parent.name == "niaid-blueprint"
    assert EXTRACT_SKILL.parent == SKILLS_ROOT
    assert VALIDATE_SKILL.parent == SKILLS_ROOT


def test_skill_assets_exist() -> None:
    assert_skill_paths()
    assert DEFAULT_SHAPE.is_file()
    assert VALIDATE_SCRIPT.is_file()
    assert EXTRACTION_WORKFLOW.is_file()
    assert VALIDATION_WORKFLOW.is_file()


def test_prompts_reference_niaid_blueprint_skills() -> None:
    extractor = render_prompt("extractor_system.md")
    repairer = render_prompt("repairer_system.md")
    user = render_prompt(
        "extractor_user.md",
        url="https://example.org",
        run_dir="/tmp/r",
        run_id="genmeta-test",
    )
    repair_user = render_prompt(
        "repairer_user.md",
        url="https://example.org",
        run_dir="/tmp/r",
        run_id="genmeta-test",
        iteration="1",
        results_json="/tmp/r/validation/iter-01/results.json",
        conforms_json="/tmp/r/validation/iter-01/conforms.json",
    )
    for text in (extractor, repairer, user, repair_user):
        assert "niaid-blueprint/skills/" in text or "host" in text.lower()
        assert "`skills/niaid-bp-" not in text
        assert "gfubp-plugin/skills" not in text
    assert "single turn" in user.lower() or "do not restart" in user.lower()
    assert "host already ran" in repair_user.lower() or "pySHACL" in repair_user
    assert (PROMPTS_DIR / "extractor_system.md").is_file()
