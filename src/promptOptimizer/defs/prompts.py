"""Read the seed and optimized prompt (instructions + demos) out of programs.

DSPy stores the "prompt" as a predictor's signature *instructions* plus its
few-shot *demos*. These helpers pull those out — from a fresh (seed) program or
a saved/compiled one — with no LM calls, so they work offline without any key.
"""
from __future__ import annotations

from defs.program import ArtifactGenerator


def extract(program) -> list[dict]:
    """Return [{name, instructions, demos}] for each predictor in the program."""
    result = []
    for name, predictor in program.named_predictors():
        sig = getattr(predictor, "signature", None)
        result.append(
            {
                "name": name,
                "instructions": getattr(sig, "instructions", "") if sig is not None else "",
                "demos": list(getattr(predictor, "demos", []) or []),
            }
        )
    return result


def seed_prompt(task) -> list[dict]:
    """The hand-written starting prompt (the signature docstring)."""
    return extract(ArtifactGenerator(task))


def optimized_prompt(task, path: str) -> list[dict]:
    """The prompt inside a saved/compiled program at ``path``."""
    program = ArtifactGenerator(task)
    program.load(path)
    return extract(program)
