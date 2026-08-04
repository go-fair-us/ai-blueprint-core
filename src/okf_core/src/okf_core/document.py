"""OKF document frontmatter/body parser.

Derived from GoogleCloudPlatform/knowledge-catalog
okf/src/reference_agent/bundle/document.py (Apache-2.0).

Aligned with OKF v0.2 (SPEC §4–§5, §11, §13): only ``type`` is always
required; ``generated.at`` supersedes legacy ``timestamp``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

import yaml

# OKF v0.2 §11: type is the only always-required key.
REQUIRED_FRONTMATTER_KEYS = ("type",)

_FRONTMATTER_DELIM = "---"


class OKFDocumentError(ValueError):
    pass


def _as_iso_str(value: Any) -> str | None:
    """Serialize YAML-loaded datetime/date or plain values to an ISO-ish string."""
    if value is None:
        return None
    if isinstance(value, datetime):
        # Prefer Z for UTC
        if value.tzinfo is not None:
            return value.isoformat().replace("+00:00", "Z")
        return value.isoformat() + "Z"
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    return text or None


def content_timestamp(fm: dict[str, Any]) -> str | None:
    """Prefer ``generated.at``; fall back to legacy ``timestamp`` (SPEC §13.1)."""
    gen = fm.get("generated")
    if isinstance(gen, dict) and gen.get("at") is not None:
        return _as_iso_str(gen["at"])
    ts = fm.get("timestamp")
    if ts is not None:
        return _as_iso_str(ts)
    return None


def generated_by(fm: dict[str, Any]) -> str | None:
    """Return ``generated.by`` actor string when present."""
    gen = fm.get("generated")
    if isinstance(gen, dict) and gen.get("by") is not None:
        return str(gen["by"])
    return None


def trust_tier(fm: dict[str, Any]) -> str:
    """Derive trust tier from ``verified`` (SPEC §5.3).

    Returns one of: ``unverified``, ``machine-confirmed``, ``human-reviewed``.
    A bare ``verified`` mapping is treated as a one-element list (§5.2).
    """
    verified = fm.get("verified")
    if not verified:
        return "unverified"
    if isinstance(verified, dict):
        events = [verified]
    elif isinstance(verified, list):
        events = [e for e in verified if isinstance(e, dict)]
    else:
        return "unverified"
    if not events:
        return "unverified"
    if any(str(e.get("by", "")).startswith("human:") for e in events):
        return "human-reviewed"
    return "machine-confirmed"


def lifecycle_status(fm: dict[str, Any]) -> str:
    """Return lifecycle status; absent ``status`` means ``stable`` (§5.4)."""
    raw = fm.get("status")
    if raw is None or str(raw).strip() == "":
        return "stable"
    return str(raw).strip()


def normalize_sources(fm: dict[str, Any]) -> list[dict[str, str]]:
    """Normalize ``sources`` to a list of JSON-safe dicts with string fields.

    Each entry keeps ``id``, ``resource``, ``title``, and optional ``author``
    when present. Entries without ``resource`` are dropped (SPEC §5.1).
    """
    raw = fm.get("sources")
    if not raw:
        return []
    if not isinstance(raw, list):
        return []
    out: list[dict[str, str]] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        resource = entry.get("resource")
        if resource is None or str(resource).strip() == "":
            continue
        item: dict[str, str] = {"resource": str(resource)}
        if entry.get("id") is not None:
            item["id"] = str(entry["id"])
        if entry.get("title") is not None:
            item["title"] = str(entry["title"])
        if entry.get("author") is not None:
            item["author"] = str(entry["author"])
        out.append(item)
    return out


@dataclass
class OKFDocument:
    frontmatter: dict[str, Any] = field(default_factory=dict)
    body: str = ""

    @classmethod
    def parse(cls, text: str) -> "OKFDocument":
        lines = text.splitlines()
        if not lines or lines[0].strip() != _FRONTMATTER_DELIM:
            return cls(frontmatter={}, body=text)

        end_idx = None
        for i in range(1, len(lines)):
            if lines[i].strip() == _FRONTMATTER_DELIM:
                end_idx = i
                break
        if end_idx is None:
            raise OKFDocumentError("Unterminated YAML frontmatter block")

        fm_text = "\n".join(lines[1:end_idx])
        try:
            fm = yaml.safe_load(fm_text) or {}
        except yaml.YAMLError as e:
            raise OKFDocumentError(f"Invalid YAML in frontmatter: {e}") from e
        if not isinstance(fm, dict):
            raise OKFDocumentError("Frontmatter must be a YAML mapping")

        body = "\n".join(lines[end_idx + 1 :])
        if body.startswith("\n"):
            body = body[1:]
        return cls(frontmatter=fm, body=body)

    def serialize(self) -> str:
        fm_text = yaml.safe_dump(
            self.frontmatter, sort_keys=False, allow_unicode=True
        ).rstrip()
        body = self.body if self.body.endswith("\n") else self.body + "\n"
        return f"{_FRONTMATTER_DELIM}\n{fm_text}\n{_FRONTMATTER_DELIM}\n\n{body}"

    def validate(self) -> None:
        missing = [k for k in REQUIRED_FRONTMATTER_KEYS if not self.frontmatter.get(k)]
        if missing:
            raise OKFDocumentError(
                f"Missing required frontmatter keys: {', '.join(missing)}"
            )
