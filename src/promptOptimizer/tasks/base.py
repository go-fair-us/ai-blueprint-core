"""Runtime goal object for one optimization run.

A ``Task`` is built from the active **profile** YAML (seed instructions, rubric,
weights, scenario seeds). The optimizer harness is profile-agnostic: change the
goal by changing ``config/profile.yaml`` or ``--profile``, and isolate runs with
``--workdir``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import dspy

from defs import checks
from defs.blueprint import get_blueprint_context

if TYPE_CHECKING:
    from defs.config import ProfileConfig

# --- Shared LLM judge -------------------------------------------------------
JUDGE_LM = None  # stronger LM for grading; set via set_judge_lm() (default: reflection)


def set_judge_lm(lm) -> None:
    """Point the LLM judge at a specific (usually stronger) LM."""
    global JUDGE_LM
    JUDGE_LM = lm


class JudgeAlignment(dspy.Signature):
    """Strictly score how well an artifact follows the given NIAID Blueprint
    rubric and the Blueprint excerpts provided. Reward faithful adherence and
    scenario-specific detail; penalize placeholders, generic templates, invalid
    structures, missing required elements, and wrong field names
    (creator/datePublished/funding)."""

    blueprint_context: str = dspy.InputField(desc="Relevant excerpts of the NIAID Blueprint.")
    rubric: str = dspy.InputField(desc="What a strong artifact looks like for this task.")
    task_description: str = dspy.InputField(desc="The scenario the artifact was written for.")
    artifact: str = dspy.InputField(desc="The generated artifact to grade.")
    alignment_score: float = dspy.OutputField(desc="A number from 0.0 (poor) to 1.0 (excellent).")
    critique: str = dspy.OutputField(
        desc="Specific, actionable critique citing Blueprint elements that are missing or wrong."
    )


class BrainstormScenarios(dspy.Signature):
    """Generate diverse, realistic scenarios for the described NIAID Blueprint
    task. Vary the biomedical domain, data type, and specific concern."""

    domain_context: str = dspy.InputField(desc="Framing for the task and its Blueprint focus area.")
    n: int = dspy.InputField(desc="How many distinct scenarios to produce.")
    scenarios: list[str] = dspy.OutputField(desc="One-sentence, self-contained scenario prompts.")


_judge = None


def _get_judge():
    global _judge
    if _judge is None:
        _judge = dspy.ChainOfThought(JudgeAlignment)
    return _judge


def judge_alignment(rubric: str, task_description: str, artifact: str) -> tuple[float, str]:
    """Grade an artifact 0..1 with a written critique, grounded in the Blueprint.

    On judge failure (timeout, parse error, etc.) returns a *neutral* 0.5 rather
    than 0.0 so a transient outage does not poison optimizer demos / reflection.
    """
    try:
        judge = _get_judge()
        kwargs = dict(
            blueprint_context=get_blueprint_context(),
            rubric=rubric,
            task_description=task_description,
            artifact=artifact,
        )
        if JUDGE_LM is not None:
            with dspy.context(lm=JUDGE_LM):
                out = judge(**kwargs)
        else:
            out = judge(**kwargs)
        m = re.search(r"[0-9]*\.?[0-9]+", str(getattr(out, "alignment_score", "0")))
        val = float(m.group()) if m else 0.0
        if val > 1.0:  # tolerate a 0-100 style answer
            val /= 100.0
        return max(0.0, min(1.0, val)), str(getattr(out, "critique", "")).strip()
    except Exception as e:
        return 0.5, f"(judge unavailable — neutral 0.5, not a real grade: {e})"


# --- Weighted scoring composition ------------------------------------------
@dataclass
class ScoreResult:
    score: float
    feedback: str
    subscores: dict = field(default_factory=dict)


# Component keys a task may weight. Only weighted components are computed and
# reported; a task's weights should sum to 1.0.
COMPONENTS = ("jsonld", "openapi", "table1", "pid", "judge")

# Filler / template quality is multiplied into the weighted sum so a checklist
# answer that ignores the scenario cannot sit near 1.0.
# final = weighted * (QUALITY_FLOOR + (1 - QUALITY_FLOOR) * content_quality)
_QUALITY_FLOOR = 0.50


def score_artifact(task_description: str, text: str, *, weights: dict, rubric: str) -> ScoreResult:
    """Compose a weighted score from the reusable checks named in ``weights``."""
    text = text or ""
    blocks = checks.code_blocks(text)
    jsonld = checks.find_jsonld(blocks)
    comps: dict[str, float] = {}
    lines = ["Overall score: PLACEHOLDER"]

    if "jsonld" in weights:
        jscore, jnotes = checks.jsonld_score(jsonld)
        comps["jsonld"] = jscore
        if jscore >= 0.99:
            lines.append("- JSON-LD: yes (schema.org Dataset with identity fields)")
        else:
            detail = "; ".join(jnotes) if jnotes else f"partial ({jscore:.2f})"
            lines.append(f"- JSON-LD: {jscore:.2f} — {detail}")

    if "openapi" in weights:
        openapi = checks.find_openapi(blocks)
        oscore, onotes = checks.openapi_score(openapi, task_description=task_description)
        comps["openapi"] = oscore
        if oscore >= 0.99:
            lines.append("- OpenAPI: yes (structure + scenario-relevant paths)")
        else:
            detail = "; ".join(onotes) if onotes else f"partial ({oscore:.2f})"
            lines.append(f"- OpenAPI: {oscore:.2f} — {detail}")

    if "table1" in weights:
        cov, missing = checks.table1_coverage(jsonld)
        comps["table1"] = cov
        # Split missing keys vs format failures for clearer GEPA feedback.
        absent = [m for m in missing if not m.startswith("~format:")]
        bad_fmt = [m[len("~format: "):] for m in missing if m.startswith("~format:")]
        parts = [f"Table 1 score: {cov:.0%}"]
        if absent:
            parts.append(f"missing: {', '.join(absent)}")
        if bad_fmt:
            parts.append(f"wrong format: {'; '.join(bad_fmt)}")
        if not absent and not bad_fmt:
            parts.append("all present with Blueprint-default formats")
        lines.append("- " + " — ".join(parts))

    if "pid" in weights:
        pid, found = checks.pid_score(text, jsonld=jsonld)
        comps["pid"] = pid
        lines.append(
            "- Persistent identifiers: "
            + (", ".join(found) if found else "NONE — put a DOI in identifier, ORCID in author, ROR in funder")
        )

    if "judge" in weights:
        judge, critique = judge_alignment(rubric, task_description, text)
        comps["judge"] = judge
        lines.append(f"- Judge alignment: {judge:.2f}")
        if critique:
            lines.append(f"  Judge critique: {critique}")

    weighted = sum(weights[k] * comps.get(k, 0.0) for k in weights)

    quality, qnotes = checks.content_quality(text, jsonld)
    comps["quality"] = quality
    q_factor = _QUALITY_FLOOR + (1.0 - _QUALITY_FLOOR) * quality
    if quality >= 0.99:
        lines.append("- Content quality: clean (no template filler detected)")
    else:
        lines.append(
            f"- Content quality: {quality:.2f} (×{q_factor:.2f} on weighted score)"
            + (f" — {'; '.join(qnotes)}" if qnotes else "")
        )

    score = weighted * q_factor
    lines[0] = f"Overall score: {score:.3f}"
    return ScoreResult(
        score=score,
        feedback="\n".join(lines),
        subscores={k: round(v, 3) for k, v in comps.items()},
    )


# --- Task definition --------------------------------------------------------
@dataclass
class Task:
    name: str
    description: str
    generate_signature: type | dspy.Signature
    output_field: str          # attribute on the prediction holding the artifact text
    rubric: str                # what "good" looks like, handed to the judge
    weights: dict              # component -> weight (subset of COMPONENTS, sums to 1.0)
    domain_context: str        # framing for scenario brainstorming
    seed_scenarios: list[str]  # built-in fallback scenarios
    scenarios_file: str | None = None  # optional preferred scenarios JSON basename/path
    input_field: str = "task_description"

    def __post_init__(self) -> None:
        unknown = set(self.weights) - set(COMPONENTS)
        if unknown:
            raise ValueError(f"Task {self.name!r}: unknown weight keys {sorted(unknown)}; "
                             f"allowed: {COMPONENTS}")
        total = sum(self.weights.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"Task {self.name!r}: weights must sum to 1.0, got {total:.4f} from {self.weights}"
            )

    def score(self, example, pred) -> ScoreResult:
        text = getattr(pred, self.output_field, "") or ""
        return score_artifact(
            getattr(example, self.input_field, "") or getattr(example, "task_description", ""),
            text,
            weights=self.weights,
            rubric=self.rubric,
        )


def make_generate_signature(
    *,
    name: str,
    instructions: str,
    input_field: str,
    input_desc: str,
    output_field: str,
    output_desc: str,
) -> type:
    """Build a DSPy Signature class from config text (seed prompt + fields)."""
    # Named subclass so saved programs / debugging show a stable label.
    return type(
        f"Generate_{name}",
        (dspy.Signature,),
        {
            "__doc__": instructions,
            "__annotations__": {input_field: str, output_field: str},
            input_field: dspy.InputField(desc=input_desc),
            output_field: dspy.OutputField(desc=output_desc),
        },
    )


def task_from_config(tc: "ProfileConfig") -> Task:
    """Materialize a runtime Task from a loaded ProfileConfig."""
    gen = tc.generation
    signature = make_generate_signature(
        name=tc.name,
        instructions=gen.instructions,
        input_field=gen.input_field,
        input_desc=gen.input_desc,
        output_field=gen.output_field,
        output_desc=gen.output_desc,
    )
    return Task(
        name=tc.name,
        description=tc.description,
        generate_signature=signature,
        output_field=gen.output_field,
        rubric=tc.rubric,
        weights=dict(tc.weights),
        domain_context=tc.domain_context,
        seed_scenarios=list(tc.seed_scenarios),
        scenarios_file=tc.scenarios_file,
        input_field=gen.input_field,
    )
