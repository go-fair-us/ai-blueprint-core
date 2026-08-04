"""Shared evaluation harness."""
from __future__ import annotations

from dataclasses import dataclass, field

from dspy.evaluate import Evaluate


@dataclass
class RunResult:
    name: str
    score: float
    seconds: float
    artifact: str | None = None
    optimized_prompt: str | None = None
    report: str | None = None


def run_eval(program, testset, metric, num_threads: int = 8):
    """Score program on testset. dspy.Evaluate returns percentage (mean × 100)."""
    evaluator = Evaluate(
        devset=testset,
        metric=metric,
        num_threads=max(1, min(num_threads, len(testset))),
        display_progress=True,
    )
    return evaluator(program)
