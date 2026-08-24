"""Tests for Tavily inspect/search helpers. HTTP is mocked; no live calls."""

from __future__ import annotations

from typing import Any

import pytest

from mcp_bp import web_tavily
from mcp_bp.web_tavily import TavilyError


def test_rejects_private_and_non_http_urls() -> None:
    with pytest.raises(TavilyError, match="http or https"):
        web_tavily.public_http_url("ftp://example.org/x")
    with pytest.raises(TavilyError, match="not allowed"):
        web_tavily.public_http_url("http://localhost/admin")
    with pytest.raises(TavilyError, match="not allowed"):
        web_tavily.public_http_url("http://127.0.0.1/")
    with pytest.raises(TavilyError, match="not allowed"):
        web_tavily.public_http_url("http://192.168.1.9/docs")
    with pytest.raises(TavilyError, match="not allowed"):
        web_tavily.public_http_url("http://10.0.0.2/")
    with pytest.raises(TavilyError, match="not allowed"):
        web_tavily.public_http_url("http://169.254.169.254/latest")
    with pytest.raises(TavilyError, match="userinfo"):
        web_tavily.public_http_url("https://user:pass@example.org/")
    with pytest.raises(TavilyError, match="required"):
        web_tavily.public_http_url("   ")


def test_accepts_public_https_and_strips_fragment() -> None:
    out = web_tavily.public_http_url("https://immunespace.org/about#team")
    assert out == "https://immunespace.org/about"
    assert web_tavily.hostname_of(out) == "immunespace.org"
    assert web_tavily.same_host("https://www.immunespace.org/cite", "immunespace.org")


def test_unconfigured_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    assert web_tavily.tavily_configured() is False
    with pytest.raises(TavilyError, match="TAVILY_API_KEY"):
        web_tavily.require_tavily()
    monkeypatch.setenv("TAVILY_API_KEY", "replace-me")
    assert web_tavily.tavily_configured() is False


def test_web_search_mocked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")

    def fake_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
        assert path == "/search"
        assert payload["query"] == "NIAID How to Cite"
        assert payload["max_results"] == 3
        return {
            "results": [
                {
                    "title": "How to Cite",
                    "url": "https://example.org/cite",
                    "content": "Use a DOI.",
                },
                {"title": "Skip me", "url": "", "content": "no url"},
            ]
        }

    monkeypatch.setattr(web_tavily, "_tavily_post", fake_post)
    out = web_tavily.web_search("NIAID How to Cite", max_results=3)
    assert out["provider"] == "tavily"
    assert len(out["hits"]) == 1
    assert out["hits"][0]["url"] == "https://example.org/cite"
    assert "DOI" in out["hits"][0]["snippet"]


def test_inspect_url_packs_landing_and_same_host(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")
    calls: list[tuple[str, dict[str, Any]]] = []

    def fake_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
        calls.append((path, payload))
        if path == "/search":
            assert payload["include_domains"] == ["immunespace.org"]
            return {
                "results": [
                    {
                        "title": "Home",
                        "url": "https://immunespace.org/",
                        "content": "landing hit",
                    },
                    {
                        "title": "Citation",
                        "url": "https://immunespace.org/cite",
                        "content": "cite page",
                    },
                    {
                        "title": "Other lab",
                        "url": "https://evil.example/cite",
                        "content": "wrong host",
                    },
                    {
                        "title": "Docs",
                        "url": "https://immunespace.org/docs",
                        "content": "docs",
                    },
                ]
            }
        if path == "/extract":
            urls = payload["urls"]
            assert payload.get("query") == "citation guidance"
            assert "https://immunespace.org/" in urls
            assert "https://immunespace.org/cite" in urls
            assert "https://evil.example/cite" not in urls
            return {
                "results": [
                    {
                        "url": "https://immunespace.org/",
                        "raw_content": "ImmuneSpace portal. See How to Cite.",
                    },
                    {
                        "url": "https://immunespace.org/cite",
                        "raw_content": "Cite datasets with a resolvable DOI.",
                    },
                ],
                "failed_results": [
                    {"url": "https://immunespace.org/docs", "error": "timeout"}
                ],
            }
        raise AssertionError(path)

    monkeypatch.setattr(web_tavily, "_tavily_post", fake_post)
    out = web_tavily.inspect_url(
        "https://immunespace.org/#top",
        "citation guidance",
        max_pages=3,
    )
    assert out["host"] == "immunespace.org"
    assert out["url"] == "https://immunespace.org/"
    roles = [p["role"] for p in out["pages"]]
    assert roles[0] == "landing"
    assert "related" in roles
    texts = " ".join(p["content"] for p in out["pages"])
    assert "How to Cite" in texts
    assert "resolvable DOI" in texts
    assert any("docs" in w for w in out["warnings"])
    assert all(p["url"].startswith("https://immunespace.org") for p in out["pages"])


def test_inspect_url_empty_extract_warns(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")

    def fake_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if path == "/search":
            return {"results": []}
        return {"results": [], "failed_results": []}

    monkeypatch.setattr(web_tavily, "_tavily_post", fake_post)
    out = web_tavily.inspect_url("https://immunespace.org/", "citation")
    assert out["pages"] == []
    assert any("no usable text" in w for w in out["warnings"])


def test_inspect_url_requires_question() -> None:
    with pytest.raises(TavilyError, match="question"):
        web_tavily.inspect_url("https://immunespace.org/", "  ")


def test_inspect_url_truncates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")
    monkeypatch.setattr("mcp_bp.config.WEB_PAGE_CHAR_CAP", 40)
    monkeypatch.setattr("mcp_bp.config.WEB_PACK_CHAR_CAP", 40)
    monkeypatch.setattr(web_tavily.config, "WEB_PAGE_CHAR_CAP", 40)
    monkeypatch.setattr(web_tavily.config, "WEB_PACK_CHAR_CAP", 40)

    def fake_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if path == "/search":
            return {"results": []}
        return {
            "results": [
                {
                    "url": "https://immunespace.org/",
                    "raw_content": "x" * 500,
                }
            ]
        }

    monkeypatch.setattr(web_tavily, "_tavily_post", fake_post)
    out = web_tavily.inspect_url("https://immunespace.org/", "citation")
    assert out["truncated"] is True
    assert out["pages"][0]["truncated"] is True
    assert len(out["pages"][0]["content"]) <= 40
