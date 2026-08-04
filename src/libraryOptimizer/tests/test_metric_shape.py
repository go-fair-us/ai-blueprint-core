"""Metric adapters return GEPA-friendly shapes without a live LM."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import dspy

from defs.metric import ScoreResult, make_metrics, score_artifact
from defs.task import Task, task_from_prompt
from defs.load_prompt import LibraryPrompt
from defs.signature import make_generate_signature


def test_score_artifact_uses_judge(monkeypatch):
    with patch("defs.metric.judge_alignment", return_value=(0.8, "looks good")):
        result = score_artifact("scenario A", "artifact text", rubric="be good")
    assert isinstance(result, ScoreResult)
    assert result.score == 0.8
    assert "looks good" in result.feedback
    assert result.subscores["judge"] == 0.8


def test_feedback_metric_prediction():
    sig = make_generate_signature(name="t", instructions="Do the thing.")
    task = Task(
        name="t",
        description="t",
        generate_signature=sig,
        rubric="rubric",
    )

    def fake_score(example, pred):
        return ScoreResult(score=0.42, feedback="fb")

    task.score = fake_score  # type: ignore[method-assign]
    scalar, feedback = make_metrics(task)
    ex = dspy.Example(scenario="s").with_inputs("scenario")
    pred = SimpleNamespace(artifact="a")
    assert scalar(ex, pred) == 0.42
    out = feedback(ex, pred)
    assert isinstance(out, dspy.Prediction)
    assert out.score == 0.42
    assert out.feedback == "fb"


def test_task_from_prompt_rubric_hint():
    lp = LibraryPrompt(
        path=__import__("pathlib").Path("citation-guidance.md"),
        slug="citation-outreach-citation-guidance",
        body="Cite the dataset.",
        title="Citation",
        tags=["citation"],
    )
    task = task_from_prompt(lp)
    assert "citation" in task.rubric.lower()
    assert task.input_field == "scenario"
    assert task.output_field == "artifact"
