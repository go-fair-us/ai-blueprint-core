"""Metric adapters bound to a Task's scoring function.

``make_metrics(task)`` returns two views over the same ``task.score`` — there is
no duplicated evaluation logic:
  * scalar   -> float, for BootstrapFewShot / MIPROv2 / Evaluate.
  * feedback -> dspy.Prediction(score, feedback), for GEPA (5-arg signature).
"""
import dspy


def make_metrics(task):
    def scalar_metric(example, pred, trace=None):
        return task.score(example, pred).score

    def feedback_metric(example, pred, trace=None, pred_name=None, pred_trace=None):
        result = task.score(example, pred)
        return dspy.Prediction(score=result.score, feedback=result.feedback)

    return scalar_metric, feedback_metric
