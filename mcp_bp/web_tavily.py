"""Tavily-backed live web inspect/search for the Blueprint MCP server.

The corpus tools stay read-only over git files. These helpers call Tavily's
HTTP APIs so a client can pull a small evidence pack from a URL (or a search)
and then look up Blueprint requirements. They do not crawl unbounded and they
do not attach Tavily's hosted MCP.
"""

from __future__ import annotations

import ipaddress
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from . import config

_PLACEHOLDER_KEYS = frozenset({"", "replace-me", "changeme", "your_api_key"})
_BLOCKED_HOSTS = frozenset(
    {
        "localhost",
        "localhost.localdomain",
        "metadata.google.internal",
    }
)
_BLOCKED_SUFFIXES = (".local", ".internal", ".localhost")


class TavilyError(ValueError):
    """User-facing Tavily or URL-validation failure."""


def tavily_api_key() -> str:
    key = os.environ.get("TAVILY_API_KEY", "").strip()
    if key.lower() in _PLACEHOLDER_KEYS:
        return ""
    return key


def tavily_configured() -> bool:
    return bool(tavily_api_key())


def require_tavily() -> str:
    key = tavily_api_key()
    if not key:
        raise TavilyError(
            "TAVILY_API_KEY is not set. Add it to the environment (or "
            "deployment/librechat/.env) to use inspect_url and web_search."
        )
    return key


def public_http_url(url: str) -> str:
    """Normalize an http(s) URL and reject loopback / private targets."""
    raw = (url or "").strip()
    if not raw:
        raise TavilyError("url is required")
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme not in {"http", "https"}:
        raise TavilyError("url must be http or https")
    if parsed.username or parsed.password:
        raise TavilyError("url must not include userinfo")
    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if not host:
        raise TavilyError("url is missing a hostname")
    if host in _BLOCKED_HOSTS or any(host.endswith(suf) for suf in _BLOCKED_SUFFIXES):
        raise TavilyError("url host is not allowed")
    _reject_private_ip(host)
    # Drop fragment; keep query. Rebuild so we do not send userinfo.
    rebuilt = urllib.parse.urlunparse(
        (
            parsed.scheme,
            parsed.netloc.split("@")[-1],
            parsed.path or "/",
            parsed.params,
            parsed.query,
            "",
        )
    )
    return rebuilt


def hostname_of(url: str) -> str:
    host = urllib.parse.urlparse(url).hostname
    if not host:
        raise TavilyError("url is missing a hostname")
    return host.lower().rstrip(".")


def same_host(url: str, host: str) -> bool:
    try:
        other = hostname_of(url)
    except TavilyError:
        return False
    host = host.lower().rstrip(".")
    return other == host or other == f"www.{host}" or host == f"www.{other}"


def _reject_private_ip(host: str) -> None:
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        raise TavilyError("url host is not allowed")


def _clip(text: str, cap: int) -> tuple[str, bool]:
    text = (text or "").strip()
    if len(text) <= cap:
        return text, False
    if cap <= 1:
        return "…", True
    return text[: cap - 1] + "…", True


def _tavily_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    key = require_tavily()
    base = os.environ.get("TAVILY_API_BASE", "https://api.tavily.com").rstrip("/")
    url = f"{base}{path}"
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    timeout = float(os.environ.get("TAVILY_TIMEOUT", "30"))
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        raise TavilyError(f"Tavily HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise TavilyError(f"Tavily request failed: {exc.reason}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TavilyError("Tavily returned non-JSON") from exc
    if not isinstance(data, dict):
        raise TavilyError("Tavily returned an unexpected payload")
    return data


def tavily_search(
    query: str,
    *,
    max_results: int = 5,
    include_domains: list[str] | None = None,
) -> list[dict[str, str]]:
    q = (query or "").strip()
    if not q:
        raise TavilyError("query is required")
    n = max(1, min(int(max_results), 5))
    payload: dict[str, Any] = {
        "query": q,
        "search_depth": "basic",
        "max_results": n,
        "include_answer": False,
    }
    if include_domains:
        payload["include_domains"] = include_domains
    data = _tavily_post("/search", payload)
    hits: list[dict[str, str]] = []
    for row in data.get("results") or []:
        if not isinstance(row, dict):
            continue
        url = str(row.get("url") or "").strip()
        if not url:
            continue
        snippet, _ = _clip(str(row.get("content") or row.get("snippet") or ""), 400)
        hits.append(
            {
                "title": str(row.get("title") or "").strip(),
                "url": url,
                "snippet": snippet,
            }
        )
    return hits[:n]


def tavily_extract(
    urls: list[str],
    *,
    question: str = "",
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not urls:
        return [], []
    payload: dict[str, Any] = {
        "urls": urls,
        "extract_depth": "basic",
        "format": "markdown",
    }
    q = (question or "").strip()
    if q:
        payload["query"] = q
        payload["chunks_per_source"] = 3
    data = _tavily_post("/extract", payload)
    pages: list[dict[str, str]] = []
    for row in data.get("results") or []:
        if not isinstance(row, dict):
            continue
        url = str(row.get("url") or "").strip()
        content = str(row.get("raw_content") or row.get("content") or "")
        if not url:
            continue
        pages.append({"url": url, "content": content})
    failed: list[dict[str, str]] = []
    for row in data.get("failed_results") or []:
        if not isinstance(row, dict):
            continue
        failed.append(
            {
                "url": str(row.get("url") or ""),
                "error": str(row.get("error") or "extract failed"),
            }
        )
    return pages, failed


def web_search(query: str, max_results: int = 5) -> dict[str, Any]:
    """Search the live web via Tavily. Returns titles, URLs, and snippets."""
    hits = tavily_search(query, max_results=max_results)
    return {"query": query.strip(), "hits": hits, "provider": "tavily"}


def inspect_url(
    url: str,
    question: str,
    max_pages: int = 3,
) -> dict[str, Any]:
    """Fetch a URL (and a few same-host pages) as a small evidence pack.

    Uses Tavily Extract with ``question`` as the chunk-ranking query, then
    Tavily Search restricted to that host for extra pages.
    """
    landing = public_http_url(url)
    host = hostname_of(landing)
    q = (question or "").strip()
    if not q:
        raise TavilyError("question is required")
    pages_cap = max(1, min(int(max_pages), 3))

    warnings: list[str] = []
    hits: list[dict[str, str]] = []
    if pages_cap > 1:
        try:
            hits = tavily_search(q, max_results=5, include_domains=[host])
        except TavilyError as exc:
            warnings.append(f"host search failed: {exc}")

    extract_urls = [landing]
    for hit in hits:
        hit_url = hit.get("url") or ""
        try:
            public_http_url(hit_url)
        except TavilyError:
            continue
        if not same_host(hit_url, host):
            continue
        if any(hit_url.rstrip("/") == u.rstrip("/") for u in extract_urls):
            continue
        extract_urls.append(hit_url)
        if len(extract_urls) >= pages_cap:
            break

    extracted, failed = tavily_extract(extract_urls, question=q)
    by_url = {p["url"].rstrip("/"): p for p in extracted}
    packed_pages: list[dict[str, Any]] = []
    pack_truncated = False
    remaining = config.WEB_PACK_CHAR_CAP

    for i, src in enumerate(extract_urls):
        key = src.rstrip("/")
        page = by_url.get(key)
        if page is None:
            # Tavily may return a slightly different URL spelling.
            page = next(
                (p for p in extracted if p["url"].rstrip("/") == key),
                None,
            )
        if page is None:
            continue
        content, page_trunc = _clip(page["content"], min(config.WEB_PAGE_CHAR_CAP, remaining))
        if not content:
            continue
        packed_pages.append(
            {
                "url": page["url"],
                "content": content,
                "truncated": page_trunc,
                "role": "landing" if i == 0 else "related",
            }
        )
        remaining -= len(content)
        pack_truncated = pack_truncated or page_trunc
        if remaining <= 200:
            pack_truncated = True
            break

    if failed:
        warnings.extend(
            f"extract failed for {row['url']}: {row['error']}" for row in failed if row.get("url")
        )
    if not packed_pages:
        warnings.append(
            "Tavily Extract returned no usable text. The page may be blocked, "
            "empty, or JavaScript-only."
        )

    return {
        "url": landing,
        "question": q,
        "host": host,
        "provider": "tavily",
        "pages": packed_pages,
        "search_hits": hits,
        "truncated": pack_truncated,
        "warnings": warnings,
    }
