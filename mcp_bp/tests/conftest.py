"""Shared pytest fixtures: a temporary docs/prompts/OKF content tree.

These fixtures monkeypatch the module-level roots in ``mcp_bp.config`` so the
content/search/sections helpers operate on a controlled fixture tree.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mcp_bp import config, content, hybrid_search, okf_content, search, skills_content


BLUEPRINT_FIXTURE = """\
# A Blueprint for Including Digital Objects

Intro text.

## 1. NIAID Minimal Metadata Schema

Metadata is essential. Required fields include identifier and license.

## 2. Persistent Identifiers (PIDs)

PIDs make objects resolvable. DOIs, ORCIDs and RORs are preferred.

### 2.1. Motivation

Long-term persistence and traceability.

## 3. Minimal API Specifications

APIs should return JSON-LD. Endpoints should be resource-oriented IRIs.
"""

PROMPT_FIXTURE = """\
You are a FAIR assessor.

Starting top-level page: https://example.org/old
Begin the interview now.
"""

OKF_REQUIREMENTS_FIXTURE = """\
---
type: NIAID Blueprint Requirements
title: Minimal Metadata Schema — Requirements
description: Table 1 metadata elements for fixture tests
tags: [table-1, schema.org, doi]
status: stable
normative: true
section: 1.2. Blueprint Requirements
concept_range: 56-58
---

Table 1 defines the minimum metadata standard.

See also: [Motivation](/metadata-schema/motivation.md).

# Atomic concepts

| # | Concept | Lines |
|---|---------|-------|
| 56 | Table 1 presents the metadata elements reflecting a minimum standard. | 99 |
| 57 | Metadata element identifier is a globally unique DOI. | 113 |
| 58 | Metadata element name is free text. | 114 |
"""

OKF_MOTIVATION_FIXTURE = """\
---
type: NIAID Blueprint Section
title: Minimal Metadata Schema — Motivation
description: Why a minimal metadata schema is needed
tags: [motivation]
status: stable
normative: false
---

Repositories need interoperable metadata for the Discovery Portal.

See also: [Requirements](/metadata-schema/requirements.md).

# Atomic concepts

| # | Concept | Lines |
|---|---------|-------|
| 40 | A minimal metadata schema improves findability. | 80 |
"""

OKF_INDEX_FIXTURE = """\
---
okf_version: "0.2"
---

# Subdirectories

* [metadata-schema](metadata-schema/index.md) - Minimal metadata schema
"""

OKF_PROMPT_EXAMPLE = """\
---
type: PromptExample
title: Recommend appropriate persistent identifiers
description: Filled example for ImmPort SDY2968
tags: [identifier, immport]
---

# Prompt

Recommend a DOI for ImmPort SDY2968.
"""

SKILL_ASSESS_FIXTURE = """\
---
name: niaid-bp-fair-assess
description: >
  Conducts a structured NIAID Blueprint FAIR assessment interview.
when_to_use: assess a repository against the Blueprint
license: Apache-2.0
---

# FAIR Assessment Interview Skill

Read `references/interview-phases.md` first.
"""

SKILL_VALIDATE_FIXTURE = """\
---
name: niaid-bp-validation
description: Validate a schema.org Dataset graph with pySHACL.
license: Apache-2.0
---

# niaid-bp-validation

Run scripts/validate.py.
"""


@pytest.fixture
def content_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    docs = tmp_path / "docs"
    prompts = tmp_path / "prompts"
    bundles = tmp_path / "okf" / "bundles"
    bundle = bundles / "niaid_blueprint"
    examples = tmp_path / "okf" / "prompt_examples"
    (docs / "sub").mkdir(parents=True)
    prompts.mkdir(parents=True)
    meta = bundle / "metadata-schema"
    meta.mkdir(parents=True)
    examples.mkdir(parents=True)

    spec = docs / config.BLUEPRINT_SPEC_RELPATH
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text(BLUEPRINT_FIXTURE, encoding="utf-8")
    (docs / "sub" / "extra.md").write_text(
        "# Extra Doc\n\nSome citation guidance here.\n", encoding="utf-8"
    )
    # A non-markdown sibling that must be ignored.
    (docs / "ignore.pdf").write_bytes(b"%PDF-1.4 binary")

    (prompts / "fairAssessorAgentOpenCode.md").write_text(
        PROMPT_FIXTURE, encoding="utf-8"
    )
    (prompts / "fairAssessorCrawl.md").write_text(
        PROMPT_FIXTURE, encoding="utf-8"
    )

    (bundle / "index.md").write_text(OKF_INDEX_FIXTURE, encoding="utf-8")
    (meta / "requirements.md").write_text(OKF_REQUIREMENTS_FIXTURE, encoding="utf-8")
    (meta / "motivation.md").write_text(OKF_MOTIVATION_FIXTURE, encoding="utf-8")
    (examples / "identifier.md").write_text(OKF_PROMPT_EXAMPLE, encoding="utf-8")

    skills = tmp_path / "skills"
    assess = skills / "niaid-bp-fair-assess"
    (assess / "references").mkdir(parents=True)
    (assess / "SKILL.md").write_text(SKILL_ASSESS_FIXTURE, encoding="utf-8")
    (assess / "references" / "interview-phases.md").write_text(
        "# Phases\n\nPhase 1 is resource overview.\n", encoding="utf-8"
    )
    validate = skills / "niaid-bp-validation"
    (validate / "scripts").mkdir(parents=True)
    (validate / "SKILL.md").write_text(SKILL_VALIDATE_FIXTURE, encoding="utf-8")
    (validate / "scripts" / "validate.py").write_text(
        "# stub — real runner lives in the repo skill\n", encoding="utf-8"
    )
    (validate / "secret.bin").write_bytes(b"\x00\x01do-not-serve")

    # Point all modules at the fixture tree.
    for module in (config, content, search, hybrid_search, okf_content, skills_content):
        monkeypatch.setattr(module, "DOCS_DIR", docs, raising=False)
        monkeypatch.setattr(module, "PROMPTS_DIR", prompts, raising=False)
        monkeypatch.setattr(module, "OKF_BUNDLES_DIR", bundles, raising=False)
        monkeypatch.setattr(module, "OKF_DEFAULT_BUNDLE", "niaid_blueprint", raising=False)
        monkeypatch.setattr(module, "OKF_PROMPT_EXAMPLES_DIR", examples, raising=False)
        monkeypatch.setattr(module, "OKF_ENABLED", True, raising=False)
        monkeypatch.setattr(module, "SKILLS_DIR", skills, raising=False)

    # Clear caches so each test builds fresh from the fixture.
    monkeypatch.setattr(hybrid_search, "_INDEX", None)
    okf_content.invalidate_cache()

    return {
        "docs": docs,
        "prompts": prompts,
        "spec": spec,
        "bundles": bundles,
        "bundle": bundle,
        "examples": examples,
        "skills": skills,
    }
