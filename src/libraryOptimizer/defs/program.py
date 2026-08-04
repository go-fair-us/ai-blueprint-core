"""Program under optimization: generate an artifact for a library-prompt task."""
from __future__ import annotations

import dspy


class ArtifactGenerator(dspy.Module):
    def __init__(self, task):
        super().__init__()
        self._input_field = getattr(task, "input_field", "scenario")
        self.generate = dspy.ChainOfThought(task.generate_signature)

    def forward(self, **kwargs):
        if self._input_field in kwargs:
            return self.generate(**{self._input_field: kwargs[self._input_field]})
        if "scenario" in kwargs:
            return self.generate(scenario=kwargs["scenario"])
        raise TypeError(
            f"ArtifactGenerator expects keyword {self._input_field!r} "
            f"(got {sorted(kwargs)})"
        )
