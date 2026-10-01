"""CedarExtract: Obscura gather + four extractors + host grounding."""
from __future__ import annotations

import json
import logging
from typing import Any

import dspy

from defs.fetch import FetchSession
from defs.ground import ground_record
from defs.models import DatasetRecord, FieldNote, LicenseRecord, TemporalCoverage, Term
from defs.progress import say
from defs.text import clean_iri, clean_literal, normalize_temporal
from defs.signatures import (
    ExtractAccessCoverage,
    ExtractAttribution,
    ExtractDomain,
    ExtractIdentity,
    GatherEvidence,
)

log = logging.getLogger(__name__)

_DCMI_DATASET = Term(iri="http://purl.org/dc/dcmitype/Dataset", label="Dataset")
_PER_PAGE_CHARS = 20_000
_NON_DATASET_TYPE_LABELS = frozenset(
    {
        "patient-level data",
        "data available",
        "individual participant data",
    }
)


def _as_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _clean_term(value: Any) -> Term | None:
    if value is None:
        return None
    if isinstance(value, Term):
        term = value
    elif isinstance(value, dict):
        try:
            term = Term.model_validate(value)
        except Exception:
            return None
    elif isinstance(value, str):
        label = clean_literal(value)
        return Term(label=label) if label else None
    else:
        return None
    iri = clean_iri(term.iri)
    label = clean_literal(term.label)
    if not iri and not label:
        return None
    return Term(iri=iri, label=label)


def _clean_terms(values: Any) -> list[Term]:
    out: list[Term] = []
    for item in _as_list(values):
        term = _clean_term(item)
        if term:
            out.append(term)
    return out


def _clean_strings(values: Any) -> list[str]:
    out: list[str] = []
    for item in _as_list(values):
        text = clean_literal(item)
        if text:
            out.append(text)
    return out


def _normalize_type(term: Term | None, *, has_name: bool) -> Term | None:
    if term is not None:
        iri = term.iri or ""
        if "dcmitype/Dataset" in iri or iri.rstrip("/").endswith("/Dataset"):
            return Term(iri=_DCMI_DATASET.iri, label=term.label or "Dataset")
        label = (term.label or "").strip().lower()
        if label in _NON_DATASET_TYPE_LABELS:
            return _DCMI_DATASET if has_name else None
    if has_name:
        return _DCMI_DATASET
    return term


def _clean_license(value: Any) -> LicenseRecord | None:
    if value is None:
        return None
    if not isinstance(value, LicenseRecord):
        try:
            value = LicenseRecord.model_validate(value)
        except Exception:
            return None
    ident = clean_literal(value.identifier)
    desc = clean_literal(value.description)
    iri = clean_iri(value.iri)
    if not ident and not desc and not iri:
        return None
    return LicenseRecord(identifier=ident, description=desc, iri=iri)


def _clean_temporal(values: Any) -> list[TemporalCoverage]:
    out: list[TemporalCoverage] = []
    for item in _as_list(values):
        if not isinstance(item, TemporalCoverage):
            try:
                item = TemporalCoverage.model_validate(item)
            except Exception:
                continue
        start = normalize_temporal(item.start)
        end = normalize_temporal(item.end)
        if start or end:
            out.append(TemporalCoverage(start=start, end=end))
    return out


def sanitize_record(record: DatasetRecord) -> DatasetRecord:
    name = clean_literal(record.name)
    return record.model_copy(
        update={
            "type": _normalize_type(_clean_term(record.type), has_name=bool(name)),
            "identifier": clean_literal(record.identifier),
            "name": name,
            "description": clean_literal(record.description),
            "date_created": clean_literal(record.date_created),
            "author_persons": _clean_terms(record.author_persons),
            "author_organizations": _clean_terms(record.author_organizations),
            "funder": _clean_terms(record.funder),
            "grant": _clean_strings(record.grant),
            "measurement_technique": _clean_terms(record.measurement_technique),
            "distribution": _clean_strings(record.distribution),
            "citation": _clean_strings(record.citation),
            "infectious_agent": _clean_terms(record.infectious_agent),
            "host": _clean_terms(record.host),
            "health_condition": _clean_terms(record.health_condition),
            "conditions_of_access": _clean_strings(record.conditions_of_access),
            "license": _clean_license(record.license),
            "temporal_coverage": _clean_temporal(record.temporal_coverage),
        }
    )


def _notes_of(pred: Any) -> list[FieldNote]:
    raw = getattr(pred, "notes", None) if pred is not None else None
    out: list[FieldNote] = []
    for item in _as_list(raw):
        if isinstance(item, FieldNote):
            out.append(item)
        elif isinstance(item, dict):
            try:
                out.append(FieldNote.model_validate(item))
            except Exception:
                continue
    return out


def _evidence_for_lm(session: FetchSession) -> str:
    parts: list[str] = []
    for page in session.pages:
        parts.append(f"### SOURCE {page.url}")
        if page.error:
            parts.append(f"[unreadable] {page.error}")
        md = page.markdown or ""
        if len(md) > _PER_PAGE_CHARS:
            md = md[:_PER_PAGE_CHARS] + "\n[truncated]"
        if md:
            parts.append(md)
        for block in page.jsonld_blocks:
            parts.append(f"### EMBEDDED JSON-LD {page.url}")
            parts.append(block[:_PER_PAGE_CHARS])
    return "\n\n".join(parts)


class CedarExtract(dspy.Module):
    def __init__(self, session: FetchSession, *, max_iters: int = 6) -> None:
        super().__init__()
        self.session = session
        self.gather = dspy.ReAct(
            GatherEvidence,
            tools=[self.fetch_url, self.list_links],
            max_iters=max_iters,
        )
        self.identity = dspy.Predict(ExtractIdentity)
        self.attribution = dspy.Predict(ExtractAttribution)
        self.domain = dspy.Predict(ExtractDomain)
        self.access = dspy.Predict(ExtractAccessCoverage)

    def fetch_url(self, url: str) -> str:
        """Fetch one page about the same digital object (DOI, license, citation, access policy). Returns markdown or a rejection reason. Do not fetch login or navigation pages."""
        page = self.session.fetch(url)
        if page.error:
            return f"ERROR {page.url}: {page.error}"
        body = page.markdown[:8000]
        extra = f"\nJSON-LD blocks: {len(page.jsonld_blocks)}"
        return body + extra

    def list_links(self, url: str) -> str:
        """List candidate same-object links from a fetched page. Returns JSON [{href, text}]."""
        links = self.session.list_links(url)
        payload = [item.model_dump() for item in links[:40]]
        return json.dumps(payload, ensure_ascii=False)

    def forward(
        self,
        start_url: str | None = None,
        *,
        skip_gather: bool = False,
    ) -> dspy.Prediction:
        if start_url:
            say(f"landing fetch: {start_url}")
            landing = self.session.fetch(start_url, depth=0)
            if landing is not None:
                say(
                    f"landing done: ok={landing.ok} "
                    f"md={len(landing.markdown)} jsonld={len(landing.jsonld_blocks)} "
                    f"links={len(landing.links)}"
                    + (f" error={landing.error}" if landing.error else "")
                )
        else:
            landing = self.session.pages[0] if self.session.pages else None

        summary = "depth-0 only"
        if (
            not skip_gather
            and landing is not None
            and landing.ok
            and start_url
        ):
            say("gather: ReAct (may call the LM several times)")
            try:
                gathered = self.gather(
                    start_url=start_url,
                    landing_text=_evidence_for_lm(self.session)[:12000],
                )
                summary = getattr(gathered, "evidence_summary", None) or summary
                say(f"gather done: {summary[:200]}")
            except Exception as exc:
                log.warning("gather failed: %s", exc)
                summary = f"gather failed: {exc}"
                say(summary)
        elif skip_gather:
            say("gather skipped")

        evidence = _evidence_for_lm(self.session)
        say(f"extract identity ({len(evidence)} chars of evidence)")
        ident = self._call(self.identity, evidence=evidence)
        say("extract attribution")
        attrib = self._call(self.attribution, evidence=evidence)
        say("extract domain")
        domain = self._call(self.domain, evidence=evidence)
        say("extract access/coverage")
        access = self._call(self.access, evidence=evidence)

        try:
            record = DatasetRecord.model_validate(
                {
                    "type": getattr(ident, "type", None),
                    "identifier": getattr(ident, "identifier", None) or None,
                    "name": getattr(ident, "name", None) or None,
                    "description": getattr(ident, "description", None) or None,
                    "date_created": getattr(ident, "date_created", None) or None,
                    "author_persons": _as_list(getattr(attrib, "author_persons", None)),
                    "author_organizations": _as_list(
                        getattr(attrib, "author_organizations", None)
                    ),
                    "funder": _as_list(getattr(attrib, "funder", None)),
                    "grant": [
                        g
                        for g in _as_list(getattr(attrib, "grant", None))
                        if isinstance(g, str) and g.strip()
                    ],
                    "measurement_technique": _as_list(
                        getattr(domain, "measurement_technique", None)
                    ),
                    "infectious_agent": _as_list(getattr(domain, "infectious_agent", None)),
                    "host": _as_list(getattr(domain, "host", None)),
                    "health_condition": _as_list(getattr(domain, "health_condition", None)),
                    "distribution": [
                        u
                        for u in _as_list(getattr(access, "distribution", None))
                        if isinstance(u, str) and u.strip()
                    ],
                    "citation": [
                        u
                        for u in _as_list(getattr(access, "citation", None))
                        if isinstance(u, str) and u.strip()
                    ],
                    "conditions_of_access": [
                        u
                        for u in _as_list(getattr(access, "conditions_of_access", None))
                        if isinstance(u, str) and u.strip()
                    ],
                    "license": getattr(access, "license", None),
                    "spatial_coverage": getattr(access, "spatial_coverage", None),
                    "temporal_coverage": _as_list(getattr(access, "temporal_coverage", None)),
                }
            )
        except Exception as exc:
            log.warning("merge failed: %s", exc)
            record = DatasetRecord()
        record = sanitize_record(record)

        blob = self.session.evidence_blob()
        say("grounding identifiers against fetched text")
        grounded, dropped = ground_record(record, blob)
        say(f"grounding done: dropped {len(dropped)} ungrounded value(s)")
        notes = (
            _notes_of(ident)
            + _notes_of(attrib)
            + _notes_of(domain)
            + _notes_of(access)
        )
        return dspy.Prediction(
            record=grounded,
            notes=notes,
            dropped=dropped,
            evidence_summary=summary,
            pages=self.session.pages,
        )

    def _call(self, predictor, **kwargs):
        name = type(predictor).__name__
        try:
            result = predictor(**kwargs)
            say(f"{name} ok")
            return result
        except Exception as exc:
            log.warning("%s failed: %s", name, exc)
            say(f"{name} failed: {exc}")
            return None
