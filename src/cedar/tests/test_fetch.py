from __future__ import annotations

from pathlib import Path

import pytest

from defs.fetch import (
    FetchSession,
    Link,
    ObscuraClient,
    is_fetchable,
    rank_links,
    resolve_obscura_bin,
)


class FakeClient:
    def __init__(self) -> None:
        self.markdown_calls: list[str] = []
        self.eval_calls: list[str] = []

    def dump_markdown(self, url: str) -> str:
        self.markdown_calls.append(url)
        return f"# body for {url}\nSee the DOI."

    def eval_page_graph(self, url: str) -> tuple[list[Link], list[str]]:
        self.eval_calls.append(url)
        return (
            [
                Link(href="https://doi.org/10.1/abc", text="article DOI"),
                Link(href="mailto:x@y.com", text="email"),
                Link(href="https://example.org/login", text="sign in"),
                Link(href="https://example.org/about", text="About us"),
            ],
            ['{"@type":"Dataset","name":"Demo"}'],
        )


def test_is_fetchable_rejects_non_http_and_login():
    assert is_fetchable("https://example.org/study/1")
    assert not is_fetchable("mailto:x@y.com")
    assert not is_fetchable("javascript:void(0)")
    assert not is_fetchable("#section")
    assert not is_fetchable("https://example.org/login")
    assert not is_fetchable("ftp://files.example.org/a")


def test_rank_links_prefers_doi_and_drops_mailto():
    ranked = rank_links(
        [
            Link(href="https://example.org/about", text="About"),
            Link(href="https://doi.org/10.1/abc", text="paper"),
            Link(href="mailto:x@y.com", text="mail"),
        ]
    )
    hrefs = [item.href for item in ranked]
    assert "mailto:x@y.com" not in hrefs
    assert hrefs[0] == "https://doi.org/10.1/abc"


def test_session_depth_and_budget(tmp_path: Path):
    client = FakeClient()
    session = FetchSession(client, max_depth=2, max_pages=1)  # type: ignore[arg-type]
    first = session.fetch("https://example.org/study", depth=0)
    assert first.ok
    assert client.markdown_calls == ["https://example.org/study"]
    second = session.fetch("https://doi.org/10.1/abc", depth=1)
    assert second.error and "budget" in second.error
    assert len(client.markdown_calls) == 1
    deep = session.fetch("https://example.org/other", depth=3)
    assert deep.error and "depth" in deep.error


def test_list_links_does_not_use_dump_links():
    client = FakeClient()
    session = FetchSession(client, max_depth=2, max_pages=5)  # type: ignore[arg-type]
    session.fetch("https://example.org/study", depth=0)
    links = session.list_links("https://example.org/study")
    hrefs = [item.href for item in links]
    assert "https://doi.org/10.1/abc" in hrefs
    assert "mailto:x@y.com" not in hrefs
    assert "https://example.org/login" not in hrefs


def test_local_file_not_counted_in_web_budget(tmp_path: Path):
    doc = tmp_path / "notes.md"
    doc.write_text("Grant UM1AI148684 funded this work.", encoding="utf-8")
    client = FakeClient()
    session = FetchSession(client, max_depth=2, max_pages=1)  # type: ignore[arg-type]
    session.add_local_file(doc)
    assert session.web_page_count() == 0
    page = session.fetch("https://example.org/study", depth=0)
    assert page.ok
    assert "UM1AI148684" in session.evidence_blob()
    assert '{"@type":"Dataset"' in session.evidence_blob()


def test_missing_binary_raises():
    with pytest.raises(FileNotFoundError, match="Obscura binary not found"):
        ObscuraClient(bin_path="/no/such/obscura-binary")


def test_resolve_bin_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    fake = tmp_path / "obscura"
    monkeypatch.setenv("OBSCURA_BIN", str(fake))
    assert resolve_obscura_bin() == fake
