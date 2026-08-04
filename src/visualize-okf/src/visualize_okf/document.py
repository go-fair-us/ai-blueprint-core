"""Re-export OKF document helpers from okf_core (backward compatible)."""

from okf_core.document import (  # noqa: F401
    REQUIRED_FRONTMATTER_KEYS,
    OKFDocument,
    OKFDocumentError,
    _as_iso_str,
    content_timestamp,
    generated_by,
    lifecycle_status,
    normalize_sources,
    trust_tier,
)

__all__ = [
    "REQUIRED_FRONTMATTER_KEYS",
    "OKFDocument",
    "OKFDocumentError",
    "_as_iso_str",
    "content_timestamp",
    "generated_by",
    "lifecycle_status",
    "normalize_sources",
    "trust_tier",
]
