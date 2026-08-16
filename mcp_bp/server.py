"""FastMCP server exposing NIAID Blueprint docs, OKF knowledge, and prompts.

Run as a module (the package uses relative imports, so launch it with
``-m`` rather than by file path)::

    uv run --extra mcp python -m mcp_bp.server

The server registers:
  * Resources: docs://…, blueprint://spec, prompts://…, okf://…
  * Tools: list/read docs, hybrid search, Blueprint navigation, OKF concept
    and atomic tools, prompt listing
  * Prompts: the personas defined in prompts_registry.PROMPT_SPECS
  * Transform: ResourcesAsTools (resources accessible as tools for clients
    that don't support the MCP resources protocol)
"""

from __future__ import annotations

import json

from fastmcp import FastMCP
from fastmcp.server.transforms import ResourcesAsTools
from mcp.types import ToolAnnotations

from . import (
    config,
    content,
    hybrid_search,
    okf_content,
    prompts_registry,
    search,
    sections,
    skills_content,
)
from .okf_content import OkfError
from .skills_content import SkillsError

mcp: FastMCP = FastMCP(
    name="ai-blueprint",
    instructions=(
        "Serves the NIAID Blueprint for Digital Objects v2, the OKF knowledge "
        "bundle (atomic concepts with line citations), and FAIR assessment "
        "prompt personas.\n\n"
        "When to use which surface:\n"
        "- Blueprint docs tools (get_blueprint_section, get_blueprint_requirements, "
        "search_docs on docs): full narrative text and official section wording.\n"
        "- OKF tools (list_okf_concepts, read_okf_concept, get_okf_atomic, "
        "search_docs with collection='okf', get_okf_requirements): structured "
        "concept graph and claim-level requirements with source line numbers.\n"
        "- Prompts: interactive FAIR assessment / work-plan interviews.\n"
        "- OKF prompt examples: filled domain few-shots (ImmPort, etc.), not "
        "interview personas.\n"
        "- Skills tools (list_skills, read_skill, read_skill_file): Agent Skill "
        "catalog and progressive file reads. Use validate_dataset to run the "
        "bundled SHACL shape on schema:Dataset JSON-LD or Turtle."
    ),
)

# Expose resources as tools so clients without resource-protocol support
# (e.g. Claude Code) can still access docs and Blueprint content via tools.
mcp.add_transform(ResourcesAsTools(mcp))


# --------------------------------------------------------------------------
# Resources
# --------------------------------------------------------------------------


@mcp.resource("docs://list", mime_type="application/json")
def docs_list() -> str:
    """A JSON listing of all Markdown documents under ./docs."""
    return json.dumps([entry.as_dict() for entry in content.list_docs()], indent=2)


@mcp.resource("docs://{path*}", mime_type="text/markdown")
def docs_get(path: str) -> str:
    """The raw Markdown of a document under ./docs by relative path."""
    return content.read_doc(path)


@mcp.resource("blueprint://spec", mime_type="text/markdown")
def blueprint_spec() -> str:
    """The canonical NIAID Blueprint specification Markdown."""
    return content.read_doc(config.BLUEPRINT_SPEC_RELPATH)


@mcp.resource("prompts://list", mime_type="application/json")
def prompts_list() -> str:
    """A JSON listing of the registered prompt personas."""
    return json.dumps(prompts_registry.list_prompt_specs(), indent=2)


@mcp.resource("prompts://{name}", mime_type="text/markdown")
def prompts_get(name: str) -> str:
    """The raw text of a registered prompt persona (for reading, not invoking).

    ``name`` may be a registered prompt name or a prompt filename.
    """
    spec = prompts_registry.PROMPT_SPECS_BY_NAME.get(name)
    filename = spec.filename if spec else name
    return content.read_prompt_file(filename)


@mcp.resource("okf://bundles", mime_type="application/json")
def okf_bundles_list() -> str:
    """JSON listing of available OKF knowledge bundles."""
    return json.dumps(okf_content.list_bundles(), indent=2)


@mcp.resource("okf://bundles/{name}/list", mime_type="application/json")
def okf_bundle_concepts(name: str) -> str:
    """JSON concept catalog for an OKF bundle (id, type, title, tags, …)."""
    return json.dumps(okf_content.list_concepts(name), indent=2)


@mcp.resource("okf://bundles/{name}/index", mime_type="text/markdown")
def okf_bundle_index(name: str) -> str:
    """Root index.md for progressive disclosure of an OKF bundle."""
    return okf_content.read_bundle_index(name)


@mcp.resource("okf://bundles/{name}/concept/{id*}", mime_type="text/markdown")
def okf_concept_md(name: str, id: str) -> str:
    """Raw Markdown of one OKF concept (frontmatter + body)."""
    return okf_content.read_concept_markdown(id, bundle=name)


@mcp.resource("okf://bundles/{name}/atomic/{number}", mime_type="application/json")
def okf_atomic_resource(name: str, number: str) -> str:
    """Single atomic concept claim as JSON."""
    return json.dumps(okf_content.get_atomic(int(number), bundle=name), indent=2)


@mcp.resource("okf://prompt_examples/list", mime_type="application/json")
def okf_prompt_examples_list() -> str:
    """JSON listing of filled OKF prompt examples."""
    return json.dumps(okf_content.list_prompt_examples(), indent=2)


@mcp.resource("okf://prompt_examples/{path*}", mime_type="text/markdown")
def okf_prompt_example_get(path: str) -> str:
    """Raw Markdown of a filled prompt example."""
    return okf_content.read_prompt_example(path)


# --------------------------------------------------------------------------
# Discovery & retrieval tools
# --------------------------------------------------------------------------

_READ_ONLY = ToolAnnotations(readOnlyHint=True, idempotentHint=True)
_READ_ONLY_NON_IDEMPOTENT = ToolAnnotations(readOnlyHint=True)


@mcp.tool(annotations=_READ_ONLY)
def list_docs() -> list[dict[str, object]]:
    """List all Markdown documents available in the NIAID Blueprint corpus.

    Returns path, title, and size for each document. Use the ``path`` values
    with ``read_doc`` to fetch full content, or pass a title keyword to
    ``search_docs`` to find relevant passages.
    """
    return [entry.as_dict() for entry in content.list_docs()]


@mcp.tool(annotations=_READ_ONLY)
def read_doc(path: str) -> str:
    """Read the full Markdown content of a Blueprint corpus document.

    ``path`` is a relative path returned by ``list_docs`` (e.g.
    ``"BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md"``).  For large documents,
    prefer ``get_blueprint_section`` to fetch just the relevant section.
    """
    return content.read_doc(path)


@mcp.tool(annotations=_READ_ONLY)
def kb_stats() -> dict[str, object]:
    """Return corpus statistics: document counts, total sizes, section count.

    Also reports OKF bundle/atomic counts and whether semantic search is enabled.
    Useful for understanding the available corpus before issuing queries.
    """
    docs = content.list_docs()
    prompts = content.list_prompt_files()
    section_count = len(sections.list_blueprint_sections())
    return {
        "docs": {"count": len(docs), "total_bytes": sum(d.bytes for d in docs)},
        "prompts": {
            "count": len(prompts),
            "total_bytes": sum(p.bytes for p in prompts),
        },
        "blueprint_sections": section_count,
        "okf": okf_content.okf_stats(),
        "skills": skills_content.skills_stats(),
        "semantic_search_enabled": config.SEMANTIC_ENABLED,
    }


# --------------------------------------------------------------------------
# Search tools
# --------------------------------------------------------------------------


@mcp.tool(annotations=_READ_ONLY)
def search_docs(
    query: str,
    collection: str | None = None,
    max_results: int = config.DEFAULT_SEARCH_RESULTS,
) -> list[dict[str, object]]:
    """Hybrid BM25 + semantic search across the NIAID Blueprint corpus.

    Searches the Blueprint v2 specification, supporting documents, and prompt
    personas using BM25 keyword ranking fused with optional dense embeddings
    (enabled via the ``BLUEPRINT_SEMANTIC_ENABLED`` env var) via Reciprocal
    Rank Fusion (RRF).

    ``collection`` filters to:
    - ``"docs"`` — specification + supporting docs
    - ``"prompts"`` — interview personas
    - ``"okf"`` — OKF concept graph + atomic claims (preferred for
      claim-level requirements)
    Omit to search docs + prompts only (OKF is opt-in so existing clients keep
    stable rankings). Use ``collection="okf"`` for structured knowledge hits.

    Each result includes:
    - ``chunk_id``: stable ID (OKF atomics use ``okf::atomic/{n}``)
    - ``source`` / ``path``: where the chunk comes from
    - ``section_number`` / ``section_title``: heading or atomic context
    - ``excerpt``: up to 400 chars of the matching passage
    - ``rrf_score``: fusion score (higher = more relevant)
    - ``bm25_rank`` / ``semantic_rank``: per-signal ranks for transparency
    """
    results = hybrid_search.hybrid_search_as_dicts(
        query, collection=collection, max_results=max_results
    )
    if results:
        return results
    # Graceful fallback when BM25 index unavailable (e.g. missing rank-bm25).
    # Fuzzy search does not cover OKF yet.
    if collection == "okf":
        return []
    fuzzy = search.search_as_dicts(query, max_results=max_results)
    if collection:
        fuzzy = [r for r in fuzzy if r.get("source") == collection]
    return fuzzy


@mcp.tool(annotations=_READ_ONLY)
def get_context_window(
    source: str,
    path: str,
    line: int,
    radius: int = 10,
) -> dict[str, object]:
    """Expand context around a line returned by a fuzzy search result.

    Use ``source``, ``path``, and ``line`` from a ``search_docs`` fallback
    result (when results contain ``"line"`` keys).  ``radius`` controls how
    many lines above and below to include (default 10).

    Returns ``start_line``, ``end_line``, and the joined ``text`` of the window.
    """
    root = config.DOCS_DIR if source == "docs" else config.PROMPTS_DIR
    return content.read_lines_around(root, path, line, radius)


# --------------------------------------------------------------------------
# Blueprint navigation tools
# --------------------------------------------------------------------------


@mcp.tool(annotations=_READ_ONLY)
def list_blueprint_sections() -> list[dict[str, object]]:
    """List the Blueprint's headings (level, number, title) for navigation.

    Use heading numbers or title keywords with ``get_blueprint_section`` to
    retrieve the content of a specific section without loading the full spec.
    """
    return sections.list_blueprint_sections()


@mcp.tool(annotations=_READ_ONLY)
def get_blueprint_section(section: str) -> str:
    """Return a single Blueprint section by number (e.g. '3', '2.1') or heading keyword.

    Extracts just the requested section from the NIAID Blueprint v2 spec,
    keeping responses token-efficient.  Use ``list_blueprint_sections`` to
    browse available headings.
    """
    return sections.get_blueprint_section(section)


@mcp.tool(annotations=_READ_ONLY)
def get_blueprint_requirements(pillar: str | None = None) -> dict[str, object]:
    """Return Blueprint requirement sections for a given FAIR pillar.

    Valid pillar names: ``"metadata"``, ``"identifiers"``, ``"api"``,
    ``"citation"``, ``"outreach"``.  Pass ``None`` (or omit) to get a summary
    index of all pillars and which Blueprint headings map to each.

    Returns ``{"pillar": ..., "sections": [{"title", "number", "content"}, ...]}``
    for a specific pillar, or ``{"pillars": {...}, "available_pillars": [...]}``
    for the overview.
    """
    return sections.get_blueprint_requirements(pillar)


@mcp.tool(annotations=_READ_ONLY)
def blueprint_citation(section: str | None = None) -> dict[str, str]:
    """Return the canonical raw GitHub URL for citing the NIAID Blueprint.

    If ``section`` is provided (number or heading keyword), the resolved
    heading title and number are included alongside the URL.
    """
    result: dict[str, str] = {"url": config.BLUEPRINT_RAW_URL}
    if section:
        match = sections.find_section(
            content.read_doc(config.BLUEPRINT_SPEC_RELPATH), section
        )
        if match is not None:
            result["section_title"] = match.title
            if match.number:
                result["section_number"] = match.number
    return result


# --------------------------------------------------------------------------
# Prompt listing tool
# --------------------------------------------------------------------------


@mcp.tool(annotations=_READ_ONLY)
def list_prompts() -> list[dict[str, object]]:
    """List the registered FAIR assessment and work-plan prompt personas.

    Returns name, title, description, and argument specs for each prompt.
    Invoke a prompt by name via the MCP prompts protocol (not this tool).
    """
    return prompts_registry.list_prompt_specs()


# --------------------------------------------------------------------------
# OKF (Open Knowledge Format) tools
# --------------------------------------------------------------------------


@mcp.tool(annotations=_READ_ONLY)
def list_okf_bundles() -> list[dict[str, object]]:
    """List available OKF knowledge bundles under okf/bundles.

    Returns name, path, whether index.md is present, and which bundle is default.
    """
    return okf_content.list_bundles()


@mcp.tool(annotations=_READ_ONLY)
def list_okf_concepts(
    bundle: str | None = None,
    type: str | None = None,
    prefix: str | None = None,
    tag: str | None = None,
    normative: bool | None = None,
) -> list[dict[str, object]]:
    """List OKF concepts (structured Blueprint knowledge units).

    Filters (all optional):
    - ``bundle``: bundle name (default niaid_blueprint)
    - ``type``: substring match on concept type (e.g. ``"Requirements"``)
    - ``prefix``: concept id prefix (e.g. ``"metadata-schema"``)
    - ``tag``: exact tag match (case-insensitive)
    - ``normative``: if set, only concepts with that normative flag

    Returns catalog entries (id, type, title, tags, atomic_count, …) without body.
    Use ``read_okf_concept`` or ``get_okf_atomic`` for full content.
    """
    return okf_content.list_concepts(
        bundle, type=type, prefix=prefix, tag=tag, normative=normative
    )


@mcp.tool(annotations=_READ_ONLY)
def read_okf_concept(
    concept_id: str,
    bundle: str | None = None,
    include_body: bool = True,
) -> dict[str, object]:
    """Read one OKF concept as structured JSON (frontmatter fields + atomics).

    ``concept_id`` is the path id without ``.md`` (e.g.
    ``"metadata-schema/requirements"``). Set ``include_body=false`` for a
    lighter payload when you only need metadata and the atomic table.
    """
    try:
        c = okf_content.get_concept(concept_id, bundle=bundle)
    except OkfError as exc:
        raise ValueError(str(exc)) from exc
    return okf_content.concept_as_dict(c, include_body=include_body)


@mcp.tool(annotations=_READ_ONLY)
def get_okf_atomic(
    number: int,
    bundle: str | None = None,
) -> dict[str, object]:
    """Return a single atomic claim by global number (1–239 in niaid_blueprint).

    Each atomic includes claim text, Blueprint source line numbers, and parent
    concept id/title. Prefer this over loading a whole concept when you need
    one obligation or fact.
    """
    try:
        return okf_content.get_atomic(number, bundle=bundle)
    except OkfError as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool(annotations=_READ_ONLY)
def list_okf_atomics(
    bundle: str | None = None,
    parent_id: str | None = None,
    query: str | None = None,
    max_results: int = 50,
) -> list[dict[str, object]]:
    """List atomic claims, optionally filtered by parent concept or text query.

    ``parent_id`` limits to one concept (e.g. ``"persistent-identifiers/requirements"``).
    ``query`` is a case-insensitive substring match on claim text.
    """
    return okf_content.list_atomics(
        bundle, parent_id=parent_id, query=query, max_results=max_results
    )


@mcp.tool(annotations=_READ_ONLY)
def get_okf_requirements(
    pillar: str | None = None,
    bundle: str | None = None,
) -> dict[str, object]:
    """Return OKF requirements concepts for a FAIR pillar.

    Valid pillars: ``"metadata"``, ``"identifiers"``, ``"api"``, ``"citation"``,
    ``"outreach"``. Omit ``pillar`` for an index of all pillars.

    Unlike ``get_blueprint_requirements`` (narrative Blueprint sections), this
    returns structured concepts with atomic claim tables and line citations.
    """
    try:
        return okf_content.get_requirements(pillar, bundle=bundle)
    except OkfError as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool(annotations=_READ_ONLY)
def get_okf_related(
    concept_id: str,
    bundle: str | None = None,
) -> dict[str, object]:
    """Return concepts linked from / linking to an OKF concept id."""
    try:
        return okf_content.get_related(concept_id, bundle=bundle)
    except OkfError as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool(annotations=_READ_ONLY)
def okf_stats(bundle: str | None = None) -> dict[str, object]:
    """OKF corpus statistics: concept counts, atomics, types, prompt examples."""
    return okf_content.okf_stats(bundle)


@mcp.tool(annotations=_READ_ONLY)
def list_okf_prompt_examples() -> list[dict[str, object]]:
    """List filled Prompt Library examples under okf/prompt_examples.

    These are domain-grounded few-shots (ImmPort, ACDN, etc.), not the
    interactive interview personas from ``list_prompts``.
    """
    return okf_content.list_prompt_examples()


@mcp.tool(annotations=_READ_ONLY)
def read_okf_prompt_example(path: str) -> str:
    """Read a filled prompt example by relative path from list_okf_prompt_examples.

    Example path: ``"metadata-schema/core-elements/identifier.md"``.
    """
    try:
        return okf_content.read_prompt_example(path)
    except Exception as exc:
        raise ValueError(str(exc)) from exc


# --------------------------------------------------------------------------
# Agent Skills (SKILL.md bundles)
# --------------------------------------------------------------------------


@mcp.tool(annotations=_READ_ONLY)
def list_skills() -> list[dict[str, object]]:
    """List Agent Skills under the Blueprint skill bundle.

    Returns name, description, when_to_use, and whether scripts / references /
    assets exist. Use ``read_skill`` for the procedure, then
    ``read_skill_file`` for references or assets. Interview skills are
    procedures — do not skip loading ``SKILL.md``. Run SHACL with
    ``validate_dataset``.
    """
    return skills_content.list_skills()


@mcp.tool(annotations=_READ_ONLY)
def read_skill(name: str) -> str:
    """Read the full ``SKILL.md`` body for a skill listed by ``list_skills``.

    ``name`` is the skill directory / frontmatter name (e.g.
    ``"niaid-bp-fair-assess"``).
    """
    try:
        return skills_content.read_skill(name)
    except SkillsError as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool(annotations=_READ_ONLY)
def read_skill_file(name: str, path: str) -> dict[str, object]:
    """Read one file from a skill directory (references, assets, scripts).

    ``path`` is relative to the skill root (e.g.
    ``"references/interview-phases.md"`` or ``"assets/blank-dataset.jsonld"``).
    Paths that escape the skill directory are rejected.
    """
    try:
        return skills_content.read_skill_file(name, path)
    except SkillsError as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool(annotations=_READ_ONLY)
def validate_dataset(graph: str, data_format: str | None = None) -> dict[str, object]:
    """Validate a schema.org Dataset graph against the Blueprint SHACL shape.

    ``graph`` is the JSON-LD or Turtle text (not a filesystem path).
    ``data_format`` is ``"json-ld"`` (default) or ``"turtle"``.

    Returns severity-aware ``conforms`` (true iff zero ``sh:Violation``
    results), counts, and finding rows. Does not invent field values.
    """
    try:
        return skills_content.validate_dataset(graph, data_format=data_format)
    except SkillsError as exc:
        raise ValueError(str(exc)) from exc


# --------------------------------------------------------------------------
# Prompts
# --------------------------------------------------------------------------


@mcp.prompt(
    name="fair_assessment_interview",
    description=(
        "Structured 6-phase interview assessing Blueprint alignment, ending "
        "in a prioritized gap report."
    ),
)
def fair_assessment_interview() -> str:
    return prompts_registry.render_prompt("fair_assessment_interview")


@mcp.prompt(
    name="fair_self_assessment",
    description="Verbose pillar-by-pillar Blueprint self-assessment consultant.",
)
def fair_self_assessment() -> str:
    return prompts_registry.render_prompt("fair_self_assessment")


@mcp.prompt(
    name="fair_self_assessment_short",
    description="Concise pillar-by-pillar Blueprint self-assessment consultant.",
)
def fair_self_assessment_short() -> str:
    return prompts_registry.render_prompt("fair_self_assessment_short")


@mcp.prompt(
    name="fair_web_assessor",
    description=(
        "Assess a web resource against the Blueprint. Provide a target URL "
        "and optionally an alternate Blueprint URL."
    ),
)
def fair_web_assessor(url: str, blueprint_url: str | None = None) -> str:
    return prompts_registry.render_prompt(
        "fair_web_assessor", url=url, blueprint_url=blueprint_url
    )


@mcp.prompt(
    name="fair_crawl_assessor",
    description=(
        "Crawl a resource's top page and key first-level links, then score it "
        "against the Blueprint. Provide a target URL and optionally an "
        "alternate Blueprint URL."
    ),
)
def fair_crawl_assessor(url: str, blueprint_url: str | None = None) -> str:
    return prompts_registry.render_prompt(
        "fair_crawl_assessor", url=url, blueprint_url=blueprint_url
    )


@mcp.prompt(
    name="work_plan_interview",
    description=(
        "Intake interview that produces a FAIRification Work Plan. Optionally "
        "provide the target repository name."
    ),
)
def work_plan_interview(repo_name: str | None = None) -> str:
    return prompts_registry.render_prompt("work_plan_interview", repo_name=repo_name)


# --------------------------------------------------------------------------
# Entrypoint
# --------------------------------------------------------------------------


def main() -> None:
    """Run the server over HTTP (Streamable HTTP / SSE-compatible)."""
    mcp.run(
        transport="http",
        host=config.HOST,
        port=config.PORT,
        path=config.HTTP_PATH,
    )


if __name__ == "__main__":
    main()
