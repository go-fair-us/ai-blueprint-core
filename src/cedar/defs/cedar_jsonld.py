"""Map DatasetRecord onto a CEDAR template instance (example.json shape)."""
from __future__ import annotations

import json
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from defs.models import DatasetRecord, LicenseRecord, SpatialCoverage, TemporalCoverage, Term
from defs.paths import EXAMPLE_PATH, TOOL_IRI
from defs.text import clean_iri, clean_literal, normalize_temporal


@lru_cache(maxsize=1)
def load_template() -> dict[str, Any]:
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def _element_id() -> str:
    return f"urn:uuid:{uuid.uuid4()}"


def _nested_context(template: dict[str, Any], key: str) -> dict[str, Any]:
    node = template.get(key)
    if isinstance(node, list) and node:
        node = node[0]
    if isinstance(node, dict):
        ctx = node.get("@context")
        if isinstance(ctx, dict):
            return deepcopy(ctx)
    return {}


def _term_object(term: Term | None) -> dict[str, Any]:
    if term is None:
        return {}
    out: dict[str, Any] = {}
    iri = clean_iri(term.iri)
    label = clean_literal(term.label)
    if iri:
        out["@id"] = iri
    if label:
        out["rdfs:label"] = label
    return out


def _term_array(terms: list[Term]) -> list[dict[str, Any]]:
    items = [_term_object(t) for t in terms if t.iri or t.label]
    return items if items else [{}]


def _id_array(iris: list[str]) -> list[dict[str, Any]]:
    items = [{"@id": iri} for iri in iris if iri]
    return items if items else []


def _value_array(values: list[str]) -> list[dict[str, Any]]:
    items = [{"@value": v} for v in values if v]
    return items if items else []


def _literal(value: str | None) -> dict[str, Any]:
    return {"@value": value}


def _datetime_literal(value: str | None) -> dict[str, Any]:
    text = normalize_temporal(value)
    if not text:
        return {"@value": None, "@type": "xsd:dateTime"}
    return {"@value": text, "@type": "xsd:dateTime"}


def _date_literal(value: str | None) -> dict[str, Any]:
    text = clean_literal(value)
    if not text:
        return {"@value": None, "@type": "xsd:date"}
    if len(text) == 7 and text[4] == "-":
        text = f"{text}-01"
    return {"@value": text, "@type": "xsd:date"}


def _author_block(
    template: dict[str, Any],
    persons: list[Term],
    orgs: list[Term],
) -> dict[str, Any]:
    person_items = [_term_object(t) for t in persons if t.iri or t.label]
    org_items = [_term_object(t) for t in orgs if t.iri or t.label]
    return {
        "@context": _nested_context(template, "Author"),
        "author-person": person_items if person_items else [{}],
        "author-organization": org_items if org_items else [{}],
        "@id": _element_id(),
    }


def _license_block(template: dict[str, Any], license: LicenseRecord | None) -> dict[str, Any]:
    ident = license.identifier if license else None
    desc = license.description if license else None
    iri = license.iri if license else None
    return {
        "@context": _nested_context(template, "LIcense(s)"),
        "licenseIdentifier": [{"@value": ident}] if ident else [{}],
        "licenseDescription": [{"@value": desc}],
        "licenseIRI": [{"@value": iri}] if iri else [{"@value": None}],
        "@id": _element_id(),
    }


def _spatial_block(template: dict[str, Any], spatial: SpatialCoverage | None) -> dict[str, Any]:
    cc = spatial.country_code if spatial else None
    geo = spatial.geonames_id if spatial else None
    coords = spatial.geo_coordinates if spatial else None
    shape = spatial.geo_shape if spatial else None
    return {
        "@context": _nested_context(template, "Spatial Coverage"),
        "countryCode": [{"@value": cc}] if cc else [{}],
        "geoNamesID": [{"@value": geo}] if geo else [{}],
        "geoCoordinates": [{"@value": coords}],
        "geoShape": [{"@value": shape}],
        "@id": _element_id(),
    }


def _temporal_block(template: dict[str, Any], items: list[TemporalCoverage]) -> list[dict[str, Any]]:
    ctx = _nested_context(template, "Temporal Coverage")
    if not items:
        return [
            {
                "@context": ctx,
                "startTime": _datetime_literal(None),
                "endTime": _datetime_literal(None),
                "@id": _element_id(),
            }
        ]
    out = []
    for item in items:
        out.append(
            {
                "@context": ctx,
                "startTime": _datetime_literal(item.start),
                "endTime": _datetime_literal(item.end),
                "@id": _element_id(),
            }
        )
    return out


def record_to_cedar(
    record: DatasetRecord,
    *,
    now: datetime | None = None,
    instance_id: str | None = None,
) -> dict[str, Any]:
    """Build a CEDAR instance dict. Does not invent payload values."""
    template = load_template()
    stamp = (now or datetime.now(timezone.utc)).isoformat(timespec="seconds")
    type_obj = _term_object(record.type)

    return {
        "@context": deepcopy(template["@context"]),
        "type": type_obj if type_obj else {},
        "identifier": {"@value": clean_literal(record.identifier)}
        if clean_literal(record.identifier)
        else {},
        "name": _literal(clean_literal(record.name)),
        "description": _literal(clean_literal(record.description)),
        "dateCreated": _date_literal(record.date_created) if record.date_created else {},
        "Author": _author_block(template, record.author_persons, record.author_organizations),
        "funder": _term_array(record.funder),
        "grant": _value_array(record.grant),
        "measurementTechnique": _term_array(record.measurement_technique),
        "distribution": _id_array(record.distribution),
        "citation": _id_array(record.citation),
        "infectiousAgent": _term_array(record.infectious_agent),
        "host": _term_array(record.host),
        "healthCondition": _term_array(record.health_condition),
        "conditionsOfAccess": _value_array(record.conditions_of_access),
        "LIcense(s)": _license_block(template, record.license),
        "Spatial Coverage": _spatial_block(template, record.spatial_coverage),
        "Temporal Coverage": _temporal_block(template, record.temporal_coverage),
        "schema:isBasedOn": template["schema:isBasedOn"],
        "schema:name": template["schema:name"],
        "schema:description": template["schema:description"],
        "pav:createdOn": stamp,
        "pav:createdBy": TOOL_IRI,
        "pav:lastUpdatedOn": stamp,
        "oslc:modifiedBy": TOOL_IRI,
        "@id": instance_id or _element_id(),
    }


def _node_literal(node: Any) -> str | None:
    if node is None or node == {}:
        return None
    if isinstance(node, str):
        return clean_literal(node)
    if isinstance(node, dict):
        if "@value" in node:
            return clean_literal(node.get("@value"))
        return clean_literal(node.get("rdfs:label"))
    return None


def _node_term(node: Any) -> Term | None:
    if not isinstance(node, dict) or node == {}:
        return None
    iri = clean_iri(node.get("@id"))
    label = clean_literal(node.get("rdfs:label"))
    if not iri and not label:
        return None
    return Term(iri=iri, label=label)


def _as_list(node: Any) -> list[Any]:
    if node is None:
        return []
    if isinstance(node, list):
        return node
    return [node]


def _term_list(node: Any) -> list[Term]:
    out: list[Term] = []
    for item in _as_list(node):
        term = _node_term(item)
        if term:
            out.append(term)
    return out


def _id_list(node: Any) -> list[str]:
    out: list[str] = []
    for item in _as_list(node):
        if isinstance(item, dict):
            iri = clean_iri(item.get("@id")) or _node_literal(item)
        else:
            iri = clean_iri(item)
        if iri:
            out.append(iri)
    return out


def _value_list(node: Any) -> list[str]:
    out: list[str] = []
    for item in _as_list(node):
        text = _node_literal(item)
        if text:
            out.append(text)
    return out


def _first_nested(node: Any) -> dict[str, Any]:
    if isinstance(node, list) and node and isinstance(node[0], dict):
        return node[0]
    if isinstance(node, dict):
        return node
    return {}


def cedar_to_record(doc: dict[str, Any]) -> DatasetRecord:
    """Payload-only inverse of ``record_to_cedar`` (drops template plumbing)."""
    author = _first_nested(doc.get("Author"))
    license_el = _first_nested(doc.get("LIcense(s)"))
    spatial_el = _first_nested(doc.get("Spatial Coverage"))
    temporal_nodes = _as_list(doc.get("Temporal Coverage"))

    license_ident = _value_list(license_el.get("licenseIdentifier"))
    license_desc = _value_list(license_el.get("licenseDescription"))
    license_iri = _value_list(license_el.get("licenseIRI"))
    license = None
    if license_ident or license_desc or license_iri:
        license = LicenseRecord(
            identifier=license_ident[0] if license_ident else None,
            description=license_desc[0] if license_desc else None,
            iri=license_iri[0] if license_iri else None,
        )

    spatial = None
    cc = _value_list(spatial_el.get("countryCode"))
    geo = _value_list(spatial_el.get("geoNamesID"))
    coords = _value_list(spatial_el.get("geoCoordinates"))
    shape = _value_list(spatial_el.get("geoShape"))
    if cc or geo or coords or shape:
        spatial = SpatialCoverage(
            country_code=cc[0] if cc else None,
            geonames_id=geo[0] if geo else None,
            geo_coordinates=coords[0] if coords else None,
            geo_shape=shape[0] if shape else None,
        )

    temporal: list[TemporalCoverage] = []
    for item in temporal_nodes:
        if not isinstance(item, dict):
            continue
        start = _node_literal(item.get("startTime"))
        end = _node_literal(item.get("endTime"))
        if start or end:
            temporal.append(TemporalCoverage(start=start, end=end))

    date_created = _node_literal(doc.get("dateCreated"))
    return DatasetRecord(
        type=_node_term(doc.get("type")),
        identifier=_node_literal(doc.get("identifier")),
        name=_node_literal(doc.get("name")),
        description=_node_literal(doc.get("description")),
        date_created=date_created,
        author_persons=_term_list(author.get("author-person")),
        author_organizations=_term_list(author.get("author-organization")),
        funder=_term_list(doc.get("funder")),
        grant=_value_list(doc.get("grant")),
        measurement_technique=_term_list(doc.get("measurementTechnique")),
        distribution=_id_list(doc.get("distribution")),
        citation=_id_list(doc.get("citation")),
        infectious_agent=_term_list(doc.get("infectiousAgent")),
        host=_term_list(doc.get("host")),
        health_condition=_term_list(doc.get("healthCondition")),
        conditions_of_access=_value_list(doc.get("conditionsOfAccess")),
        license=license,
        spatial_coverage=spatial,
        temporal_coverage=temporal,
    )
