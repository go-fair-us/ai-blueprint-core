"""DSPy signatures: bounded gather, then four extract groups."""
from __future__ import annotations

import dspy

from defs.models import FieldNote, LicenseRecord, SpatialCoverage, TemporalCoverage, Term


class GatherEvidence(dspy.Signature):
    """Decide whether more pages are needed to fill Blueprint dataset metadata.

    Fetch only pages that likely contain missing identifiers, license, citation,
    access terms, or ontology labels for the same digital object. Stop when the
    remaining fields are simply not on the site. Do not wander into login,
    navigation, or unrelated pages.
    """

    start_url: str = dspy.InputField()
    landing_text: str = dspy.InputField(desc="Markdown and JSON-LD from the start URL")
    evidence_summary: str = dspy.OutputField(
        desc="Which extra pages were fetched and why; which fields still look absent"
    )


class ExtractIdentity(dspy.Signature):
    """Extract dataset identity. Copy only what the evidence supports; do not invent identifiers.

    Copy only facts supported by the SOURCE text. If a field is not in the sources, leave it null or empty. Never invent DOIs, ORCIDs, RORs, grant numbers, NCT ids, or ontology IRIs. An IRI is allowed only if that IRI (or an obvious expansion such as doi.org) appears in the source text.
    """

    evidence: str = dspy.InputField(desc="Concatenated SOURCE pages")
    type: Term | None = dspy.OutputField(
        desc="Use dcmitype Dataset for a research dataset/study record. Do not use UI badges such as Patient-Level Data."
    )
    identifier: str | None = dspy.OutputField(desc="DOI or other PID if present")
    name: str | None = dspy.OutputField(
        desc="Study or dataset title exactly as shown, including a leading (Released …) prefix when present"
    )
    description: str | None = dspy.OutputField(desc="Abstract or summary from the page")
    date_created: str | None = dspy.OutputField(desc="ISO date YYYY-MM-DD if present")
    notes: list[FieldNote] = dspy.OutputField()


class ExtractAttribution(dspy.Signature):
    """Extract authors, funders, and grants. Copy only what the evidence supports; do not invent ORCIDs, RORs, or grant numbers.

    Copy only facts supported by the SOURCE text. If a field is not in the sources, leave it null or empty. Never invent DOIs, ORCIDs, RORs, grant numbers, NCT ids, or ontology IRIs. An IRI is allowed only if that IRI (or an obvious expansion such as doi.org) appears in the source text.
    """

    evidence: str = dspy.InputField()
    author_persons: list[Term] = dspy.OutputField(desc="People with ORCID IRI only if on the page")
    author_organizations: list[Term] = dspy.OutputField()
    funder: list[Term] = dspy.OutputField(desc="Organizations; ROR IRI only if on the page")
    grant: list[str] = dspy.OutputField(desc="Grant numbers exactly as written")
    notes: list[FieldNote] = dspy.OutputField()


class ExtractDomain(dspy.Signature):
    """Extract measurement technique, infectious agent, host, and health condition. Ontology IRIs only if they appear in the sources.

    Copy only facts supported by the SOURCE text. If a field is not in the sources, leave it null or empty. Never invent DOIs, ORCIDs, RORs, grant numbers, NCT ids, or ontology IRIs. An IRI is allowed only if that IRI (or an obvious expansion such as doi.org) appears in the source text.
    """

    evidence: str = dspy.InputField()
    measurement_technique: list[Term] = dspy.OutputField()
    infectious_agent: list[Term] = dspy.OutputField()
    host: list[Term] = dspy.OutputField()
    health_condition: list[Term] = dspy.OutputField()
    notes: list[FieldNote] = dspy.OutputField()


class ExtractAccessCoverage(dspy.Signature):
    """Extract access, license, distribution, citation, spatial and temporal coverage. URLs and license IRIs only if present in the sources.

    Copy only facts supported by the SOURCE text. If a field is not in the sources, leave it null or empty. Never invent DOIs, ORCIDs, RORs, grant numbers, NCT ids, or ontology IRIs. An IRI is allowed only if that IRI (or an obvious expansion such as doi.org) appears in the source text.
    """

    evidence: str = dspy.InputField()
    distribution: list[str] = dspy.OutputField(desc="Data download or study-viewer URLs")
    citation: list[str] = dspy.OutputField(desc="Publication URLs or DOIs")
    conditions_of_access: list[str] = dspy.OutputField(
        desc="Data-use or access policy URL (DUA, DAR, Data Use Limitations PDF). Not a Log in button label."
    )
    license: LicenseRecord | None = dspy.OutputField(
        desc="License or DUA PDF URL from study documents when present"
    )
    spatial_coverage: SpatialCoverage | None = dspy.OutputField()
    temporal_coverage: list[TemporalCoverage] = dspy.OutputField()
    notes: list[FieldNote] = dspy.OutputField()



