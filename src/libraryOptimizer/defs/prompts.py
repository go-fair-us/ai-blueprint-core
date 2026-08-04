"""Extract seed and optimized instructions from programs."""
from __future__ import annotations

from defs.program import ArtifactGenerator


def extract(program) -> list[dict]:
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
    return extract(ArtifactGenerator(task))


def optimized_prompt(task, path: str) -> list[dict]:
    program = ArtifactGenerator(task)
    program.load(path)
    return extract(program)


def instructions_text(parts: list[dict]) -> str:
    blocks = []
    for p in parts:
        instr = (p.get("instructions") or "").strip()
        if instr:
            blocks.append(instr)
    return "\n\n".join(blocks)
