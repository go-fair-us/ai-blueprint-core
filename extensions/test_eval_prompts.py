"""Committed Pi templates match the wrapper built from prompts/evals."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from eval_prompt_templates import drift


def test_eval_prompt_templates_match_procedures():
    problems = drift()
    assert problems == [], "\n".join(problems)
