"""Robots checks with a fake HTTP client. No live network."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_robots.py"
spec = importlib.util.spec_from_file_location("check_robots", SCRIPT)
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


def robots(body: str, headers: dict[str, str] | None = None) -> mod.Response:
    return mod.Response(
        status=200,
        url="https://repo.example/robots.txt",
        headers=headers or {"Content-Type": "text/plain"},
        body=body.encode(),
    )


def home(status: int = 200, headers: dict[str, str] | None = None) -> mod.Response:
    return mod.Response(status=status, url="https://repo.example/", headers=headers or {})


WEBINAR = """
# Retry-After: 30 is an HTTP header, not a rule in this file.
User-agent: OAI-SearchBot
User-agent: PerplexityBot
User-agent: Claude-SearchBot
Allow: /
Disallow: /admin/
Content-Signal: search=yes, ai-input=yes, ai-train=no
Content-Usage: search=y, train-ai=n

User-agent: ChatGPT-User
User-agent: Perplexity-User
User-agent: Claude-User
Allow: /
Disallow: /admin/
Content-Signal: search=yes, ai-input=yes, ai-train=no
Content-Usage: search=y, train-ai=n

User-agent: GPTBot
User-agent: ClaudeBot
Disallow: /

User-agent: *
Allow: /
Disallow: /admin/
Content-Signal: search=yes, ai-input=yes, ai-train=no
Content-Usage: search=y, train-ai=n

Sitemap: https://repo.example/sitemap.xml
"""


def group(report: dict, token: str) -> dict:
    found = [row for row in report["groups"] if token in row["user_agents"]]
    assert len(found) == 1
    return found[0]


def test_webinar_file_reports_preferences_and_does_not_see_429():
    routes = {
        ("GET", "https://repo.example/robots.txt"): robots(WEBINAR),
        ("GET", "https://repo.example/"): home(200),
    }
    report = mod.check("https://repo.example/", fetch_from(routes))
    assert report["found"] is True
    assert report["well_formed"] is True
    assert report["sitemaps"] == ["https://repo.example/sitemap.xml"]
    search = group(report, "OAI-SearchBot")
    assert search["class"] == ["index builder"]
    assert search["crawl"] == "allow"
    assert search["train_ai"] == "n"
    assert search["content_signal"]["ai-train"] == "no"
    trainers = group(report, "GPTBot")
    assert trainers["class"] == ["trainer"]
    assert trainers["crawl"] == "disallow"
    assert trainers["train_ai"] == "not-applicable"
    assert report["http"]["rate_limit_observed"] is False
    assert report["http"]["retry_after"] is None
    assert any("not HTTP 429" in note for note in report["warnings"])
    assert any("ignore robots.txt" in note for note in report["warnings"])
    assert any("honors robots.txt" in note for note in report["warnings"])
    assert not any("does not apply to" in note for note in report["warnings"])


def test_star_preference_does_not_apply_to_a_named_group():
    body = """
User-agent: *
Allow: /
Content-Usage: train-ai=n

User-agent: GPTBot
Allow: /
"""
    routes = {
        ("GET", "https://repo.example/robots.txt"): robots(body),
        ("GET", "https://repo.example/"): home(200),
    }
    report = mod.check("https://repo.example/robots.txt", fetch_from(routes))
    assert group(report, "*")["train_ai"] == "n"
    assert group(report, "GPTBot")["train_ai"] == "unknown"
    assert any("does not apply to GPTBot" in note for note in report["warnings"])


def test_homepage_429_with_retry_after_is_observed():
    body = """
User-agent: *
Allow: /
Content-Usage: train-ai=n
Sitemap: https://repo.example/sitemap.xml
"""
    routes = {
        ("GET", "https://repo.example/robots.txt"): robots(body),
        ("GET", "https://repo.example/"): home(
            429,
            {"Retry-After": "30", "Content-Usage": "train-ai=n"},
        ),
    }
    report = mod.check("https://repo.example/", fetch_from(routes))
    assert report["http"]["status"] == 429
    assert report["http"]["retry_after"] == "30"
    assert report["http"]["content_usage"] == "train-ai=n"
    assert report["http"]["rate_limit_observed"] is True
    assert not any("not HTTP 429" in note for note in report["warnings"])
    assert not any("no Content-Usage header" in note for note in report["warnings"])


def test_yes_on_content_usage_is_unknown():
    body = """
User-agent: *
Allow: /
Content-Usage: train-ai=yes
"""
    routes = {
        ("GET", "https://repo.example/robots.txt"): robots(body),
        ("GET", "https://repo.example/"): home(200),
    }
    report = mod.check("https://repo.example/", fetch_from(routes))
    assert group(report, "*")["train_ai"] == "unknown"
    assert any("not y or n" in note for note in report["warnings"])


def test_html_body_is_not_a_robots_file():
    routes = {
        ("GET", "https://repo.example/robots.txt"): robots("<!DOCTYPE html><html></html>"),
        ("GET", "https://repo.example/"): home(200),
    }
    report = mod.check("https://repo.example/", fetch_from(routes))
    assert report["found"] is True
    assert report["well_formed"] is False
    assert report["groups"] == []


def test_content_usage_on_a_disallowed_group_does_not_attach():
    body = """
User-agent: GPTBot
Disallow: /
Content-Usage: train-ai=n
"""
    routes = {
        ("GET", "https://repo.example/robots.txt"): robots(body),
        ("GET", "https://repo.example/"): home(200),
    }
    report = mod.check("https://repo.example/", fetch_from(routes))
    assert group(report, "GPTBot")["train_ai"] == "not-applicable"
    assert any("does not attach" in note for note in report["warnings"])


def test_crawl_delay_is_reported_as_nonstandard():
    body = """
User-agent: *
Allow: /
Crawl-delay: 10
Content-Usage: train-ai=n
Sitemap: https://repo.example/sitemap.xml
"""
    routes = {
        ("GET", "https://repo.example/robots.txt"): robots(body),
        ("GET", "https://repo.example/"): home(200),
    }
    report = mod.check("https://repo.example/", fetch_from(routes))
    assert group(report, "*")["crawl_delay"] == 10
    assert any("not defined by RFC 9309" in note for note in report["warnings"])
    assert not any("Crawl-delay is absent" in note for note in report["warnings"])


def test_equal_length_allow_wins():
    assert mod.crawl_allowed(["/"], ["/"]) is True
    assert mod.crawl_allowed([], ["/"]) is False


def test_longest_content_usage_path_wins_and_n_wins_a_tie():
    rules = [
        {"path": "", "train-ai": "n"},
        {"path": "/ai-ok/", "train-ai": "y"},
    ]
    assert mod.usage_for(rules, "/")["train-ai"] == "n"
    assert mod.usage_for(rules, "/ai-ok/test")["train-ai"] == "y"
    tie = mod.usage_for(
        [
            {"path": "/", "train-ai": "y"},
            {"path": "/", "train-ai": "n"},
        ]
    )
    assert tie["train-ai"] == "n"


def test_signal_and_usage_disagree():
    body = """
User-agent: *
Allow: /
Content-Usage: train-ai=y
Content-Signal: ai-train=no
"""
    routes = {
        ("GET", "https://repo.example/robots.txt"): robots(body),
        ("GET", "https://repo.example/"): home(200),
    }
    report = mod.check("https://repo.example/", fetch_from(routes))
    assert any("disagree" in note for note in report["warnings"])


def test_oversized_robots_is_not_parsed():
    routes = {
        ("GET", "https://repo.example/robots.txt"): mod.Response(
            status=200,
            url="https://repo.example/robots.txt",
            truncated=True,
            body=b"User-agent: *\n",
        ),
        ("GET", "https://repo.example/"): home(200),
    }
    report = mod.check("https://repo.example/", fetch_from(routes))
    assert report["found"] is True
    assert report["over_500kib"] is True
    assert report["well_formed"] is False
    assert report["groups"] == []


def test_missing_robots_is_not_found():
    routes = {("GET", "https://repo.example/"): home(200)}
    report = mod.check("https://repo.example/", fetch_from(routes))
    assert report["found"] is False
    assert report["well_formed"] is False


def test_bad_target_exits_2():
    assert mod.main(["not-a-url"]) == 2
