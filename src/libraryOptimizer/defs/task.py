"""Runtime task built from one OKF library prompt example."""
from __future__ import annotations

from dataclasses import dataclass, field

from defs.load_prompt import LibraryPrompt
from defs.metric import ScoreResult, score_artifact
from defs.signature import make_generate_signature

# Fallback scenarios if gen-scenarios is unavailable and no JSON on disk.
_SEED_SCENARIOS = [
    "An immunology study repository preparing schema.org Dataset JSON-LD for a multi-site cohort study of influenza vaccine responses.",
    "A pathogen genomics portal exposing study-level metadata for Mycobacterium tuberculosis isolates with linked imaging.",
    "A clinical trial data archive aligning persistent identifiers (DOI, ORCID, ROR) for an ACTT-style COVID-19 trial package.",
    "A eukaryotic pathogen knowledgebase designing machine-readable landing pages for gene and genome digital objects.",
    "A network data coordinating center drafting citation guidance and outreach materials for first-time depositors.",
]

DEFAULT_RUBRIC = """\
Score how well the artifact fulfills the library prompt's task while aligning
with the NIAID Blueprint for Digital Objects and Work Plans guidance provided.

Reward:
- Faithful coverage of Blueprint-required and recommended elements relevant to
  the prompt (metadata schema.org fields, PIDs, APIs/JSON-LD, citation, FAIR
  repository practices, outreach/training as applicable)
- Concrete, scenario-specific detail (real formats: DOI, ORCID, ROR, ontology
  terms, actionable endpoints or steps — not placeholders like example.org)
- Clear structure matching what the prompt asked for (JSON, strategy, design, etc.)
- Actionable guidance a repository team could implement

Penalize:
- Generic filler, templates, or invented hosts/IDs without scenario grounding
- Missing required Blueprint elements for the implied task
- Ignoring the scenario or contradicting Blueprint guidance
- Long essays that omit the requested deliverable format
"""


def rubric_for_prompt(prompt: LibraryPrompt) -> str:
    """Generic rubric plus light path/tag hints."""
    hints: list[str] = []
    hay = " ".join([prompt.slug, prompt.title, " ".join(prompt.tags)]).lower()
    if any(k in hay for k in ("citation", "cite")):
        hints.append("Emphasize Blueprint citation practices and reusable citation text.")
    if any(k in hay for k in ("api", "openapi", "endpoint")):
        hints.append("Emphasize machine access, JSON-LD responses, and OpenAPI-style clarity.")
    if any(k in hay for k in ("pid", "identifier", "doi", "orcid")):
        hints.append("Emphasize persistent identifiers at the right object levels and exposure.")
    if any(k in hay for k in ("outreach", "training")):
        hints.append("Emphasize training/outreach practicality for repository staff and users.")
    if any(k in hay for k in ("metadata", "name", "description", "author", "funder", "health", "infectious")):
        hints.append("Emphasize Table 1 / schema.org Dataset element quality and formats.")
    if any(k in hay for k in ("work", "fair", "plan")):
        hints.append("Emphasize Work Plans / FAIRification interview practicality.")
    extra = ("\n\nCategory focus:\n- " + "\n- ".join(hints)) if hints else ""
    return DEFAULT_RUBRIC + extra


def domain_context_for_prompt(prompt: LibraryPrompt) -> str:
    preview = prompt.body[:500].replace("\n", " ")
    tags = ", ".join(prompt.tags) if prompt.tags else prompt.slug
    return (
        f"NIAID Blueprint digital-object / FAIR repository practices. "
        f"Prompt title: {prompt.title}. Tags: {tags}. "
        f"The optimized prompt will be applied to varied but related scenarios "
        f"(not only one fixed repository). Seed prompt preview: {preview}"
    )


@dataclass
class Task:
    name: str
    description: str
    generate_signature: type
    output_field: str = "artifact"
    input_field: str = "scenario"
    rubric: str = DEFAULT_RUBRIC
    domain_context: str = ""
    seed_scenarios: list[str] = field(default_factory=lambda: list(_SEED_SCENARIOS))
    source_path: str = ""
    tags: list[str] = field(default_factory=list)

    def score(self, example, pred) -> ScoreResult:
        text = getattr(pred, self.output_field, "") or ""
        scenario = (
            getattr(example, self.input_field, "")
            or getattr(example, "scenario", "")
            or ""
        )
        return score_artifact(scenario, text, rubric=self.rubric)


def task_from_prompt(prompt: LibraryPrompt) -> Task:
    sig = make_generate_signature(
        name=prompt.slug,
        instructions=prompt.body,
    )
    return Task(
        name=prompt.slug,
        description=prompt.title,
        generate_signature=sig,
        rubric=rubric_for_prompt(prompt),
        domain_context=domain_context_for_prompt(prompt),
        source_path=str(prompt.path),
        tags=list(prompt.tags),
    )
