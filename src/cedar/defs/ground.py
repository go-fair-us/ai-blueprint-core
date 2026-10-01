"""Drop identifiers that never appeared in fetched evidence."""
from __future__ import annotations

from defs.models import DatasetRecord, DroppedValue, LicenseRecord, Term
from defs.text import clean_iri, clean_literal, url_path


def corpus_blob(texts: list[str]) -> str:
    return "\n".join(t for t in texts if t)


def _variants(value: str) -> list[str]:
    v = value.strip()
    if not v:
        return []
    out = {v, v.lower()}
    lower = v.lower()
    for prefix in ("https://", "http://"):
        if lower.startswith(prefix):
            rest = v[len(prefix) :]
            out.add(rest)
            out.add(rest.lower())
            if rest.lower().startswith("www."):
                out.add(rest[4:])
    if lower.startswith("https://doi.org/"):
        out.add(v[len("https://doi.org/") :])
    elif lower.startswith("http://doi.org/"):
        out.add(v[len("http://doi.org/") :])
    elif lower.startswith("doi:"):
        tail = v[4:].strip()
        out.add(tail)
        out.add("https://doi.org/" + tail)
    elif v.startswith("10.") and "/" in v:
        out.add("https://doi.org/" + v)
        out.add("http://doi.org/" + v)
        out.add("doi:" + v)
    if "orcid.org/" in lower:
        orcid = v[lower.index("orcid.org/") + len("orcid.org/") :].strip("/")
        out.add(orcid)
        out.add("https://orcid.org/" + orcid)
    if "ror.org/" in lower:
        ror = v[lower.index("ror.org/") + len("ror.org/") :].strip("/")
        out.add(ror)
        out.add("https://ror.org/" + ror)
    return [item for item in out if item]


def appears(value: str | None, blob: str) -> bool:
    text = clean_literal(value)
    if not text:
        return False
    hay_lower = blob.lower()
    hay_raw = blob
    for cand in _variants(text):
        if cand.lower() in hay_lower or cand in hay_raw:
            return True
    path = url_path(text)
    if path and (path in hay_raw or path.lower() in hay_lower):
        return True
    return False


def _ground_term(term: Term, field: str, blob: str, dropped: list[DroppedValue]) -> Term:
    iri = clean_iri(term.iri)
    if iri and not appears(iri, blob):
        dropped.append(DroppedValue(field=f"{field}.iri", value=iri))
        iri = None
    label = clean_literal(term.label)
    if label and iri is None and not appears(label, blob):
        dropped.append(DroppedValue(field=f"{field}.label", value=label))
        label = None
    return Term(iri=iri, label=label)


def _ground_terms(terms: list[Term], field: str, blob: str, dropped: list[DroppedValue]) -> list[Term]:
    out: list[Term] = []
    for term in terms:
        grounded = _ground_term(term, field, blob, dropped)
        if grounded.iri or grounded.label:
            out.append(grounded)
    return out


def _ground_strings(values: list[str], field: str, blob: str, dropped: list[DroppedValue]) -> list[str]:
    out: list[str] = []
    for value in values:
        text = clean_literal(value)
        if not text:
            continue
        if appears(text, blob):
            out.append(text)
        else:
            dropped.append(DroppedValue(field=field, value=text))
    return out


def ground_record(record: DatasetRecord, blob: str) -> tuple[DatasetRecord, list[DroppedValue]]:
    """Return a copy of *record* with ungrounded PIDs/strings removed.

    ``name`` and ``description`` are not deleted (paraphrase is allowed).
    """
    dropped: list[DroppedValue] = []
    data = record.model_copy(deep=True)

    dcmi_dataset = "http://purl.org/dc/dcmitype/Dataset"
    if data.type and (data.type.iri or "").rstrip("/") != dcmi_dataset:
        data.type = _ground_term(data.type, "type", blob, dropped)
        if not data.type.iri and not data.type.label:
            data.type = None

    ident = clean_literal(data.identifier)
    data.identifier = ident
    if ident and not appears(ident, blob):
        dropped.append(DroppedValue(field="identifier", value=ident))
        data.identifier = None

    data.author_persons = _ground_terms(data.author_persons, "author_persons", blob, dropped)
    data.author_organizations = _ground_terms(
        data.author_organizations, "author_organizations", blob, dropped
    )
    data.funder = _ground_terms(data.funder, "funder", blob, dropped)
    data.grant = _ground_strings(data.grant, "grant", blob, dropped)
    data.measurement_technique = _ground_terms(
        data.measurement_technique, "measurement_technique", blob, dropped
    )
    data.distribution = _ground_strings(data.distribution, "distribution", blob, dropped)
    data.citation = _ground_strings(data.citation, "citation", blob, dropped)
    data.infectious_agent = _ground_terms(data.infectious_agent, "infectious_agent", blob, dropped)
    data.host = _ground_terms(data.host, "host", blob, dropped)
    data.health_condition = _ground_terms(data.health_condition, "health_condition", blob, dropped)
    data.conditions_of_access = _ground_strings(
        data.conditions_of_access, "conditions_of_access", blob, dropped
    )

    if data.license:
        ident = clean_literal(data.license.identifier)
        iri = clean_iri(data.license.iri)
        desc = clean_literal(data.license.description)
        if ident and not appears(ident, blob):
            dropped.append(DroppedValue(field="license.identifier", value=ident))
            ident = None
        if iri and not appears(iri, blob):
            dropped.append(DroppedValue(field="license.iri", value=iri))
            iri = None
        if desc and not appears(desc, blob):
            # License prose may be paraphrased; keep short descriptions, drop long ungrounded ones.
            if len(desc) > 80:
                dropped.append(DroppedValue(field="license.description", value=desc))
                desc = None
        if ident or iri or desc:
            data.license = LicenseRecord(identifier=ident, description=desc, iri=iri)
        else:
            data.license = None

    created = clean_literal(data.date_created)
    data.date_created = created
    if created and not appears(created, blob):
        ymd = created[:10]
        if not appears(ymd, blob) and not appears(created[:7], blob):
            dropped.append(DroppedValue(field="date_created", value=created))
            data.date_created = None

    return data, dropped
