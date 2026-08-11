"""Defaults, agent names, and role system prompts for genMeta."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

# Package and repo roots
GENMETA_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = GENMETA_DIR.parent.parent

# Agent plugin skills (formerly repo-root skills/, then gfubp-plugin/skills/)
SKILLS_ROOT = REPO_ROOT / "niaid-blueprint" / "skills"
EXTRACT_SKILL = SKILLS_ROOT / "niaid-bp-metadata-extract"
VALIDATE_SKILL = SKILLS_ROOT / "niaid-bp-validation"
EXTRACTION_WORKFLOW = EXTRACT_SKILL / "references" / "extraction-workflow.md"
VALIDATION_WORKFLOW = VALIDATE_SKILL / "references" / "validation-workflow.md"
VALIDATE_SCRIPT = VALIDATE_SKILL / "scripts" / "validate.py"
DEFAULT_SHAPE = VALIDATE_SKILL / "assets" / "blueprint-required.ttl"

# Repo-relative paths for agent prompts (cwd is REPO_ROOT).
SKILLS_REL = "niaid-blueprint/skills"
EXTRACT_SKILL_REL = f"{SKILLS_REL}/niaid-bp-metadata-extract"
VALIDATE_SKILL_REL = f"{SKILLS_REL}/niaid-bp-validation"

BLUEPRINT_RAW_URL = (
    "https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/"
    "refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md"
)
EXAMPLE_JSON_RAW_URL = (
    "https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/"
    "refs/heads/master/docs/example.json"
)

# Prefixed aliases so we do not collide with coffeenotes lead/researcher/reviewer.
ROLE_EXTRACTOR = "genmeta-extractor"
ROLE_REPAIRER = "genmeta-repairer"
AGENTS = [ROLE_EXTRACTOR, ROLE_REPAIRER]

DEFAULT_MODELS: Dict[str, str] = {
    ROLE_EXTRACTOR: "xai-auth/grok-4.5",
    ROLE_REPAIRER: "xai-auth/grok-4.5",
}

DEFAULT_MAX_ITERS = 3
DEFAULT_TIMEOUT_S = 600
DEFAULT_RUNS_DIR = GENMETA_DIR / "runs"

PROMPTS_DIR = GENMETA_DIR / "prompts"


def load_prompt(name: str) -> str:
    """Load a prompt file from ``prompts/`` by basename."""
    path = PROMPTS_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def render_prompt(name: str, **kwargs: str) -> str:
    """Load a prompt and replace ``{{key}}`` placeholders."""
    text = load_prompt(name)
    for key, value in kwargs.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def assert_skill_paths() -> None:
    """Raise FileNotFoundError if extract/validate skill assets are missing.

    Catches silent path drift after skill package moves (e.g. repo-root
    ``skills/`` → ``niaid-blueprint/skills/``).
    """
    required = (
        EXTRACT_SKILL / "SKILL.md",
        EXTRACTION_WORKFLOW,
        VALIDATE_SCRIPT,
        DEFAULT_SHAPE,
        VALIDATION_WORKFLOW,
    )
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise FileNotFoundError(
            "genMeta skill assets missing (expected under "
            f"{SKILLS_ROOT}):\n  - "
            + "\n  - ".join(missing)
        )
