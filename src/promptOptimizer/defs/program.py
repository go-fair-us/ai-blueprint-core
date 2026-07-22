"""The program under optimization: generate an artifact for the selected task.

Task-agnostic — it wraps whatever generation signature the Task provides. The
Blueprint requirements live in that signature's instructions (which optimizers
may rewrite); the only per-example input is the scenario, so bootstrapped
demonstrations stay compact.
"""
import dspy


class ArtifactGenerator(dspy.Module):
    def __init__(self, task):
        super().__init__()
        self._input_field = getattr(task, "input_field", "task_description")
        self.generate = dspy.ChainOfThought(task.generate_signature)

    def forward(self, **kwargs):
        # Accept the configured input field name (default task_description).
        if self._input_field in kwargs:
            return self.generate(**{self._input_field: kwargs[self._input_field]})
        # Backward-compat: callers/examples still using task_description
        if "task_description" in kwargs:
            return self.generate(**{self._input_field: kwargs["task_description"]})
        raise TypeError(
            f"ArtifactGenerator expects keyword {self._input_field!r} "
            f"(got {sorted(kwargs)})"
        )
