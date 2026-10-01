"""Payload-only diff of two DatasetRecords (gold vs extract)."""
from __future__ import annotations

from dataclasses import dataclass

from defs.models import DatasetRecord, LicenseRecord, SpatialCoverage, TemporalCoverage, Term


@dataclass(frozen=True)
class FieldDiff:
    field: str
    gold: str
    pred: str
    status: str  # match | differ | gold_only | pred_only | both_empty


def _fmt(value: object | None) -> str:
    if value is None:
        return ""
    if isinstance(value, Term):
        parts = []
        if value.iri:
            parts.append(value.iri)
        if value.label:
            parts.append(value.label)
        return " | ".join(parts)
    if isinstance(value, LicenseRecord):
        return " ; ".join(
            p
            for p in (value.identifier, value.description, value.iri)
            if p
        )
    if isinstance(value, SpatialCoverage):
        return " ; ".join(
            p
            for p in (
                value.country_code,
                value.geonames_id,
                value.geo_coordinates,
                value.geo_shape,
            )
            if p
        )
    if isinstance(value, TemporalCoverage):
        return f"{value.start or ''} / {value.end or ''}".strip(" /")
    if isinstance(value, list):
        if not value:
            return ""
        return " || ".join(_fmt(item) for item in value if _fmt(item))
    return str(value)


def _status(gold: str, pred: str) -> str:
    if not gold and not pred:
        return "both_empty"
    if gold == pred:
        return "match"
    if gold and not pred:
        return "gold_only"
    if pred and not gold:
        return "pred_only"
    return "differ"


_FIELDS = (
    "type",
    "identifier",
    "name",
    "description",
    "date_created",
    "author_persons",
    "author_organizations",
    "funder",
    "grant",
    "measurement_technique",
    "distribution",
    "citation",
    "infectious_agent",
    "host",
    "health_condition",
    "conditions_of_access",
    "license",
    "spatial_coverage",
    "temporal_coverage",
)


def compare_records(gold: DatasetRecord, pred: DatasetRecord) -> list[FieldDiff]:
    rows: list[FieldDiff] = []
    for name in _FIELDS:
        g = _fmt(getattr(gold, name))
        p = _fmt(getattr(pred, name))
        rows.append(FieldDiff(field=name, gold=g, pred=p, status=_status(g, p)))
    return rows


def format_table(rows: list[FieldDiff]) -> str:
    lines = [
        "| field | status | gold | pred |",
        "|-------|--------|------|------|",
    ]
    for row in rows:
        gold = row.gold.replace("|", "\\|")[:120]
        pred = row.pred.replace("|", "\\|")[:120]
        lines.append(f"| {row.field} | {row.status} | {gold} | {pred} |")
    return "\n".join(lines) + "\n"
