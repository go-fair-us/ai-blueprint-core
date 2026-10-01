"""Pydantic record for Blueprint/CEDAR dataset payload fields."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Term(BaseModel):
    """Controlled term: ontology/ROR/ORCID IRI plus display label."""

    iri: str | None = None
    label: str | None = None


class LicenseRecord(BaseModel):
    identifier: str | None = None
    description: str | None = None
    iri: str | None = None


class SpatialCoverage(BaseModel):
    country_code: str | None = None
    geonames_id: str | None = None
    geo_coordinates: str | None = None
    geo_shape: str | None = None


class TemporalCoverage(BaseModel):
    start: str | None = None
    end: str | None = None


class FieldNote(BaseModel):
    field: str
    status: Literal["found", "missing"]
    source_url: str | None = None
    quote: str | None = None


class DatasetRecord(BaseModel):
    type: Term | None = None
    identifier: str | None = None
    name: str | None = None
    description: str | None = None
    date_created: str | None = None
    author_persons: list[Term] = Field(default_factory=list)
    author_organizations: list[Term] = Field(default_factory=list)
    funder: list[Term] = Field(default_factory=list)
    grant: list[str] = Field(default_factory=list)
    measurement_technique: list[Term] = Field(default_factory=list)
    distribution: list[str] = Field(default_factory=list)
    citation: list[str] = Field(default_factory=list)
    infectious_agent: list[Term] = Field(default_factory=list)
    host: list[Term] = Field(default_factory=list)
    health_condition: list[Term] = Field(default_factory=list)
    conditions_of_access: list[str] = Field(default_factory=list)
    license: LicenseRecord | None = None
    spatial_coverage: SpatialCoverage | None = None
    temporal_coverage: list[TemporalCoverage] = Field(default_factory=list)


class Link(BaseModel):
    href: str
    text: str = ""


class FetchedPage(BaseModel):
    url: str
    depth: int = 0
    markdown: str = ""
    jsonld_blocks: list[str] = Field(default_factory=list)
    links: list[Link] = Field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return not self.error and bool(self.markdown.strip() or self.jsonld_blocks)


class DroppedValue(BaseModel):
    field: str
    value: str
    reason: str = "not present in fetched text"
