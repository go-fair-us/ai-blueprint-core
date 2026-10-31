"""llms.txt checks with a fake HTTP client. No live network."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_llms.py"
spec = importlib.util.spec_from_file_location("check_llms", SCRIPT)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def fetch_from(routes: dict[tuple[str, str], mod.Response]):
    def fetch(method: str, url: str, *, read: bool = False) -> mod.Response:
        found = routes.get((method, url))
        if found is None:
            return mod.Response(status=404, url=url, body=b"")
        if not read:
            return mod.Response(
                status=found.status,
                url=found.url,
                headers=found.headers,
                error=found.error,
                truncated=found.truncated,
            )
        return found

    return fetch


def text_response(url: str, body: str, headers: dict[str, str] | None = None) -> mod.Response:
    return mod.Response(
        status=200,
        url=url,
        headers=headers or {"Content-Type": "text/plain"},
        body=body.encode(),
    )


FILE = """# Example Data Repository

> Public studies of human immune response.

Prose before the fence.

```
## Not a section
Link: </studies/SDY1001.md>; rel="alternate"
```

- [Prose link](https://repo.example/not-a-file.md)

## Start here

- [Overview](https://repo.example/index.md): What the repository holds.
- [Citation](https://repo.example/about/citation.html.md): Citation string.

## Studies

- [Study guide](https://repo.example/studies/llms.txt): Nested file.
- [SDY1001](https://repo.example/studies/SDY1001.md): One study.
- just text

## Optional

- [Blueprint](https://example.org/blueprint.md): Off host.
- [Portal](https://example.org/portal): HTML page, not a Markdown URL.
- [Glossary](https://repo.example/docs/glossary.md)
"""

SAME_HOST = [
    "https://repo.example/index.md",
    "https://repo.example/about/citation.html.md",
    "https://repo.example/studies/SDY1001.md",
    "https://repo.example/docs/glossary.md",
]


def routes_for(body: str, home: str = "<html></html>", home_headers: dict[str, str] | None = None):
    found = {
        ("GET", "https://repo.example/llms.txt"): text_response("https://repo.example/llms.txt", body),
        ("GET", "https://repo.example/"): text_response(
            "https://repo.example/", home, home_headers or {"Content-Type": "text/html"}
        ),
    }
    for url in SAME_HOST:
        found[("HEAD", url)] = mod.Response(status=200, url=url)
    return found


def test_webinar_shaped_file_parses_and_skips_off_host_and_nested():
    report = mod.check("https://repo.example/", fetch_from(routes_for(FILE)))
    assert report["found"] is True
    assert report["source"] == "well-known"
    assert report["well_formed"] is True
    assert report["title"] == "Example Data Repository"
    assert report["summary"] == "Public studies of human immune response."
    names = [section["name"] for section in report["sections"]]
    assert names == ["Start here", "Studies", "Optional"]
    assert report["sections"][2]["optional"] is True
    assert report["link_count"] == 7
    assert report["off_host_count"] == 2
    assert report["nested"] == ["https://repo.example/studies/llms.txt"]
    sampled = [row["url"] for row in report["samples"]]
    assert sampled == SAME_HOST
    shapes = {row["url"]: row["shape"] for row in report["samples"]}
    assert shapes["https://repo.example/index.md"] == "index-md"
    assert shapes["https://repo.example/about/citation.html.md"] == "html-md"
    assert "https://example.org/blueprint.md" not in sampled
    assert "https://repo.example/not-a-file.md" not in sampled
    assert any("not a Markdown link" in note for note in report["warnings"])
    assert any("were not opened" in note for note in report["warnings"])
    assert any("not use a Markdown URL shape" in note for note in report["warnings"])
    assert any('rel="alternate"' in note for note in report["warnings"])


def test_html_or_missing_h1_is_not_well_formed():
    html = fetch_from(
        {
            ("GET", "https://repo.example/llms.txt"): text_response(
                "https://repo.example/llms.txt", "<!DOCTYPE html><html></html>"
            ),
            ("GET", "https://repo.example/"): text_response("https://repo.example/", "<html></html>"),
        }
    )
    report = mod.check("https://repo.example/llms.txt", html)
    assert report["found"] is True
    assert report["well_formed"] is False
    assert report["source"] == "given"

    bare = fetch_from(
        routes_for("- https://repo.example/a\n- https://repo.example/b\n")
    )
    report = mod.check("https://repo.example/", bare)
    assert report["found"] is True
    assert report["well_formed"] is False
    assert any("no H1" in note for note in report["warnings"])


def test_homepage_points_at_one_llms_file():
    calls: list[tuple[str, str]] = []
    page = '<a href="/docs/llms.txt">guide</a><a href="/other/llms.txt">second</a>'
    routes = {
        ("GET", "https://repo.example/llms.txt"): mod.Response(
            status=404, url="https://repo.example/llms.txt", body=b""
        ),
        ("GET", "https://repo.example/"): text_response("https://repo.example/", page),
        ("GET", "https://repo.example/docs/llms.txt"): text_response(
            "https://repo.example/docs/llms.txt",
            "# Docs\n\n## Pages\n\n- [Page](https://repo.example/docs/page.md)\n",
        ),
        ("HEAD", "https://repo.example/docs/page.md"): mod.Response(
            status=200, url="https://repo.example/docs/page.md"
        ),
    }

    def fetch(method: str, url: str, *, read: bool = False) -> mod.Response:
        calls.append((method, url))
        return fetch_from(routes)(method, url, read=read)

    report = mod.check("https://repo.example/", fetch)
    assert report["source"] == "homepage"
    assert report["llms_url"] == "https://repo.example/docs/llms.txt"
    assert report["well_formed"] is True
    assert report["samples"][0]["url"] == "https://repo.example/docs/page.md"
    assert ("GET", "https://repo.example/other/llms.txt") not in calls


def test_list_item_without_a_link_is_a_warning():
    body = "# Title\n\n## Docs\n\n- just text\n- [Ok](https://repo.example/ok.md)\n"
    routes = routes_for(body)
    routes[("HEAD", "https://repo.example/ok.md")] = mod.Response(
        status=200, url="https://repo.example/ok.md"
    )
    report = mod.check("https://repo.example/", fetch_from(routes))
    assert report["well_formed"] is True
    assert any("not a Markdown link" in note for note in report["warnings"])
    assert report["samples"][0]["status"] == 200


def test_head_method_not_allowed_falls_back_to_get():
    body = "# Title\n\n## Docs\n\n- [Ok](https://repo.example/ok.md)\n"
    routes = routes_for(body)
    routes[("HEAD", "https://repo.example/ok.md")] = mod.Response(
        status=405, url="https://repo.example/ok.md"
    )
    routes[("GET", "https://repo.example/ok.md")] = mod.Response(
        status=200, url="https://repo.example/ok.md"
    )
    calls: list[tuple[str, str]] = []

    def fetch(method: str, url: str, *, read: bool = False) -> mod.Response:
        calls.append((method, url))
        return fetch_from(routes)(method, url, read=read)

    report = mod.check("https://repo.example/", fetch, sample_size=1)
    assert report["samples"][0]["status"] == 200
    assert ("GET", "https://repo.example/ok.md") in calls


def test_homepage_link_relations_are_reported():
    headers = {
        "Content-Type": "text/html",
        "Link": '</about.md>; rel="alternate"; type="text/markdown", </llms.txt>; rel="describedby"',
    }
    report = mod.check("https://repo.example/", fetch_from(routes_for(FILE, home_headers=headers)))
    home = report["homepage"]
    assert home["alternate_markdown"] == ["https://repo.example/about.md"]
    assert home["describedby"] == ["https://repo.example/llms.txt"]
    assert not any('rel="alternate"' in note for note in report["warnings"])


def test_bad_target_exits_2():
    assert mod.main(["not-a-url"]) == 2
