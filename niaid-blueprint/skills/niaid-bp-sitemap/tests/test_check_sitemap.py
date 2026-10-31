"""Sitemap checks with a fake HTTP client. No live network."""

from __future__ import annotations

import gzip
import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_sitemap.py"
spec = importlib.util.spec_from_file_location("check_sitemap", SCRIPT)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def fetch_from(routes: dict[tuple[str, str], mod.Response]):
    def fetch(method: str, url: str, *, read: bool = False) -> mod.Response:
        key = (method, url)
        if key not in routes:
            return mod.Response(status=404, url=url, body=b"")
        found = routes[key]
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


def xml(body: str) -> bytes:
    return body.encode()


def test_robots_index_opens_one_child_and_samples():
    index = f"""<?xml version="1.0" encoding="UTF-8"?>
    <sitemapindex xmlns="{NS}">
      <sitemap><loc>https://repo.example/sitemaps/studies.xml</loc></sitemap>
      <sitemap><loc>https://repo.example/sitemaps/files.xml</loc></sitemap>
    </sitemapindex>
    """
    urlset = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="{NS}">
      <url><loc>https://repo.example/studies/1</loc><lastmod>2026-01-02</lastmod></url>
      <url><loc>https://repo.example/studies/2</loc><lastmod>not-a-date</lastmod></url>
      <url><loc>https://repo.example/studies/1</loc></url>
    </urlset>
    """
    routes = {
        ("GET", "https://repo.example/robots.txt"): mod.Response(
            status=200,
            url="https://repo.example/robots.txt",
            body=b"Sitemap: https://repo.example/sitemap.xml\nSitemap: https://repo.example/extra.xml\n",
        ),
        ("GET", "https://repo.example/sitemap.xml"): mod.Response(
            status=200,
            url="https://repo.example/sitemap.xml",
            headers={"Content-Type": "application/xml"},
            body=xml(index),
        ),
        ("GET", "https://repo.example/sitemaps/studies.xml"): mod.Response(
            status=200,
            url="https://repo.example/sitemaps/studies.xml",
            body=xml(urlset),
        ),
        ("HEAD", "https://repo.example/studies/1"): mod.Response(
            status=200, url="https://repo.example/studies/1"
        ),
        ("HEAD", "https://repo.example/studies/2"): mod.Response(
            status=404, url="https://repo.example/studies/2"
        ),
    }
    report = mod.check("https://repo.example/", fetch_from(routes), sample_size=10, seed=0)
    assert report["found"] is True
    assert report["source"] == "robots"
    assert report["well_formed"] is True
    assert report["kind"] == "sitemapindex"
    assert report["index_child_count"] == 2
    assert report["child_sitemap_url"] == "https://repo.example/sitemaps/studies.xml"
    assert report["loc_count"] == 3
    assert "https://repo.example/sitemaps/files.xml" in report["not_opened"]
    assert "https://repo.example/extra.xml" in report["not_opened"]
    assert "https://repo.example/sitemap_index.xml" not in report["not_opened"]
    statuses = {row["url"]: row["status"] for row in report["samples"]}
    assert statuses["https://repo.example/studies/2"] == 404
    assert any("duplicate loc" in note for note in report["warnings"])
    assert any("not a W3C date" in note for note in report["warnings"])


def test_sitemap_xml_fallback_when_robots_has_no_directive():
    urlset = f"""<urlset xmlns="{NS}"><url><loc>https://repo.example/a</loc></url></urlset>"""
    routes = {
        ("GET", "https://repo.example/robots.txt"): mod.Response(
            status=200, url="https://repo.example/robots.txt", body=b"User-agent: *\nDisallow:\n"
        ),
        ("GET", "https://repo.example/sitemap.xml"): mod.Response(
            status=200,
            url="https://repo.example/sitemap.xml",
            headers={"Content-Type": "application/xml"},
            body=xml(urlset),
        ),
        ("HEAD", "https://repo.example/a"): mod.Response(status=200, url="https://repo.example/a"),
    }
    report = mod.check("https://repo.example", fetch_from(routes))
    assert report["source"] == "well-known"
    assert report["sitemap_url"] == "https://repo.example/sitemap.xml"
    assert report["kind"] == "urlset"
    assert report["samples"][0]["status"] == 200
    assert "https://repo.example/sitemap_index.xml" in report["not_opened"]


def test_malformed_xml_stops_the_sample():
    routes = {
        ("GET", "https://repo.example/sitemap.xml"): mod.Response(
            status=200,
            url="https://repo.example/sitemap.xml",
            body=b"<urlset><url></urlset>",
        ),
    }
    report = mod.check("https://repo.example/sitemap.xml", fetch_from(routes))
    assert report["found"] is True
    assert report["source"] == "given"
    assert report["well_formed"] is False
    assert report["samples"] == []


def test_head_method_not_allowed_falls_back_to_get():
    urlset = f"""<urlset xmlns="{NS}"><url><loc>https://repo.example/a</loc></url></urlset>"""
    routes = {
        ("GET", "https://repo.example/sitemap.xml"): mod.Response(
            status=200, url="https://repo.example/sitemap.xml", body=xml(urlset)
        ),
        ("HEAD", "https://repo.example/a"): mod.Response(status=405, url="https://repo.example/a"),
        ("GET", "https://repo.example/a"): mod.Response(status=200, url="https://repo.example/a"),
    }
    calls: list[tuple[str, str]] = []

    def fetch(method: str, url: str, *, read: bool = False) -> mod.Response:
        calls.append((method, url))
        return fetch_from(routes)(method, url, read=read)

    report = mod.check("https://repo.example/sitemap.xml", fetch, sample_size=1)
    assert report["samples"][0]["status"] == 200
    assert ("GET", "https://repo.example/a") in calls


def test_index_does_not_open_a_later_child_when_the_first_fails():
    index = f"""<sitemapindex xmlns="{NS}">
      <sitemap><loc>https://repo.example/sitemaps/missing.xml</loc></sitemap>
      <sitemap><loc>https://repo.example/sitemaps/files.xml</loc></sitemap>
    </sitemapindex>"""
    urlset = f"""<urlset xmlns="{NS}"><url><loc>https://repo.example/a</loc></url></urlset>"""
    routes = {
        ("GET", "https://repo.example/sitemap.xml"): mod.Response(
            status=200, url="https://repo.example/sitemap.xml", body=xml(index)
        ),
        ("GET", "https://repo.example/sitemaps/files.xml"): mod.Response(
            status=200, url="https://repo.example/sitemaps/files.xml", body=xml(urlset)
        ),
        ("HEAD", "https://repo.example/a"): mod.Response(status=200, url="https://repo.example/a"),
    }
    calls: list[tuple[str, str]] = []

    def fetch(method: str, url: str, *, read: bool = False) -> mod.Response:
        calls.append((method, url))
        return fetch_from(routes)(method, url, read=read)

    report = mod.check("https://repo.example/sitemap.xml", fetch)
    assert report["kind"] == "sitemapindex"
    assert report["child_sitemap_url"] is None
    assert report["samples"] == []
    assert "https://repo.example/sitemaps/files.xml" in report["not_opened"]
    assert ("GET", "https://repo.example/sitemaps/files.xml") not in calls


def test_gzip_body_is_parsed():
    urlset = f"""<urlset xmlns="{NS}"><url><loc>https://repo.example/a</loc></url></urlset>"""
    routes = {
        ("GET", "https://repo.example/sitemap.xml.gz"): mod.Response(
            status=200,
            url="https://repo.example/sitemap.xml.gz",
            body=gzip.compress(xml(urlset)),
        ),
        ("HEAD", "https://repo.example/a"): mod.Response(status=200, url="https://repo.example/a"),
    }
    report = mod.check("https://repo.example/sitemap.xml.gz", fetch_from(routes))
    assert report["source"] == "given"
    assert report["well_formed"] is True
    assert report["loc_count"] == 1
    assert report["samples"][0]["status"] == 200


def test_oversized_body_is_not_parsed():
    routes = {
        ("GET", "https://repo.example/sitemap.xml"): mod.Response(
            status=200,
            url="https://repo.example/sitemap.xml",
            body=b"<urlset></urlset>",
            truncated=True,
        ),
    }
    report = mod.check("https://repo.example/sitemap.xml", fetch_from(routes))
    assert report["found"] is True
    assert report["well_formed"] is False
    assert report["samples"] == []
    assert any("5 MB" in note for note in report["warnings"])


def test_missing_namespace_still_reads_loc():
    urlset = "<urlset><url><loc>https://repo.example/a</loc></url></urlset>"
    routes = {
        ("GET", "https://repo.example/sitemap.xml"): mod.Response(
            status=200, url="https://repo.example/sitemap.xml", body=xml(urlset)
        ),
        ("HEAD", "https://repo.example/a"): mod.Response(status=200, url="https://repo.example/a"),
    }
    report = mod.check("https://repo.example/sitemap.xml", fetch_from(routes))
    assert report["well_formed"] is True
    assert report["loc_count"] == 1
    assert any("namespace is missing" in note for note in report["warnings"])


def test_lastmod_accepts_w3c_dates():
    assert mod.lastmod_ok("2026-01-02")
    assert mod.lastmod_ok("2026-01-02T03:04:05Z")
    assert mod.lastmod_ok("2026-01-02T03:04:05.123+00:00")
    assert not mod.lastmod_ok("2026-13-01")
    assert not mod.lastmod_ok("02 Jan 2026")


def test_bad_target_exits_2():
    assert mod.main(["not-a-url"]) == 2
