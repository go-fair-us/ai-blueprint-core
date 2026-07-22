"""Shared evaluation harness so every optimizer branch is scored identically."""
from __future__ import annotations

from dataclasses import dataclass, field

from dspy.evaluate import Evaluate


@dataclass
class RunResult:
    name: str
    score: float
    seconds: float
    artifact: str | None = None
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0
    usage_by_lm: dict = field(default_factory=dict)


def run_eval(program, testset, metric, num_threads: int = 8):
    """Score ``program`` on the held-out ``testset`` with the task metric.

    Scores returned by ``dspy.Evaluate`` are percentages (mean metric × 100);
    callers that want a 0–1 mean should divide by 100 (see ``main._score_of``).
    """
    evaluator = Evaluate(
        devset=testset,
        metric=metric,
        num_threads=max(1, min(num_threads, len(testset))),  # no idle threads for tiny sets
        display_progress=True,
    )
    return evaluator(program)
