"""Judge-only scoring + GEPA feedback adapters."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import dspy

from defs.guidance import get_guidance_context

JUDGE_LM = None


def set_judge_lm(lm) -> None:
    global JUDGE_LM
    JUDGE_LM = lm


class JudgeAlignment(dspy.Signature):
    """Strictly score how well an artifact follows the NIAID Blueprint and Work
    Plans guidance and the given rubric. Reward faithful adherence and
    scenario-specific detail; penalize placeholders, generic templates, missing
    required elements, and wrong or invented identifiers."""

    guidance_context: str = dspy.InputField(
        desc="Sliced excerpts of the NIAID Blueprint and Work Plans guidance."
    )
    rubric: str = dspy.InputField(desc="What a strong artifact looks like for this task.")
    scenario: str = dspy.InputField(desc="The scenario the artifact was written for.")
    artifact: str = dspy.InputField(desc="The generated artifact to grade.")
    alignment_score: float = dspy.OutputField(
        desc="A number from 0.0 (poor) to 1.0 (excellent)."
    )
    critique: str = dspy.OutputField(
        desc="Specific, actionable critique citing Blueprint or Work Plans gaps."
    )


class BrainstormScenarios(dspy.Signature):
    """Generate diverse, realistic scenarios for optimizing a NIAID Blueprint
    library prompt. Vary biomedical domain, data type, repository type, and
    specific FAIR / metadata concern. Each scenario is one self-contained
    paragraph the prompt can be applied to."""

    domain_context: str = dspy.InputField(
        desc="Framing for the library prompt and its Blueprint focus area."
    )
    n: int = dspy.InputField(desc="How many distinct scenarios to produce.")
    scenarios: list[str] = dspy.OutputField(
        desc="One-paragraph, self-contained scenario descriptions."
    )


_judge = None


def _get_judge():
    global _judge
    if _judge is None:
        _judge = dspy.ChainOfThought(JudgeAlignment)
    return _judge


@dataclass
class ScoreResult:
    score: float
    feedback: str
    subscores: dict = field(default_factory=dict)


def judge_alignment(rubric: str, scenario: str, artifact: str) -> tuple[float, str]:
    """Grade an artifact 0..1 with a written critique grounded in guidance docs."""
    try:
        judge = _get_judge()
        kwargs = dict(
            guidance_context=get_guidance_context(),
            rubric=rubric,
            scenario=scenario,
            artifact=artifact,
        )
        if JUDGE_LM is not None:
            with dspy.context(lm=JUDGE_LM):
                out = judge(**kwargs)
        else:
            out = judge(**kwargs)
        m = re.search(r"[0-9]*\.?[0-9]+", str(getattr(out, "alignment_score", "0")))
        val = float(m.group()) if m else 0.0
        if val > 1.0:
            val /= 100.0
        return max(0.0, min(1.0, val)), str(getattr(out, "critique", "")).strip()
    except Exception as e:  # noqa: BLE001 — judge outage must not kill GEPA
        return 0.5, f"(judge unavailable — neutral 0.5, not a real grade: {e})"


def score_artifact(scenario: str, text: str, *, rubric: str) -> ScoreResult:
    """Judge-only score for libraryOptimizer v1."""
    text = text or ""
    judge, critique = judge_alignment(rubric, scenario, text)
    lines = [
        f"Overall score: {judge:.3f}",
        f"- Judge alignment: {judge:.2f}",
    ]
    if critique:
        lines.append(f"  Judge critique: {critique}")
    return ScoreResult(
        score=judge,
        feedback="\n".join(lines),
        subscores={"judge": round(judge, 3)},
    )


def make_metrics(task):
    """Return scalar and GEPA feedback metrics bound to ``task.score``."""

    def scalar_metric(example, pred, trace=None):
        return task.score(example, pred).score

    def feedback_metric(example, pred, trace=None, pred_name=None, pred_trace=None):
        result = task.score(example, pred)
        return dspy.Prediction(score=result.score, feedback=result.feedback)

    return scalar_metric, feedback_metric
