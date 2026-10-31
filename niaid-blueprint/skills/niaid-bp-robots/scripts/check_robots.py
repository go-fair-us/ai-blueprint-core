#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""Read one robots.txt and one homepage response.

Reports RFC 9309 groups, IETF Content-Usage, Cloudflare Content-Signal,
and Crawl-delay. HTTP 429 and Retry-After are read from the homepage
response. They are not robots.txt directives.

Usage::

    uv run --no-project scripts/check_robots.py https://example.org/
    uv run --no-project scripts/check_robots.py https://example.org/robots.txt
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from urllib.parse import urlsplit, urlunsplit

MAX_BYTES = 500 * 1024
TIMEOUT_SECONDS = 15.0
USER_AGENT = "niaid-bp-robots/0.1 (+https://github.com/go-fair-us/ai-blueprint-core)"
PATH = "/"

# Product tokens already used in the webinar robots.txt, plus two published
# training opt-outs. Matching is case-insensitive. Other tokens stay "other".
TOKEN_CLASS = {
    "oai-searchbot": "index builder",
    "perplexitybot": "index builder",
    "claude-searchbot": "index builder",
    "chatgpt-user": "fetcher",
    "perplexity-user": "fetcher",
    "claude-user": "fetcher",
    "gptbot": "trainer",
    "claudebot": "trainer",
    "google-extended": "trainer",
    "ccbot": "trainer",
    "oai-adsbot": "ads",
}

USAGE_LABELS = {"train-ai", "search"}
SIGNAL_LABELS = {"search", "ai-input", "ai-train"}
IGNORES_ROBOTS = {"ChatGPT-User", "Perplexity-User"}


@dataclass
class Response:
    status: int
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    error: str | None = None
    truncated: bool = False


Fetch = Callable[..., Response]


def header(headers: dict[str, str], name: str) -> str:
    folded = {key.lower(): value for key, value in headers.items()}
    return folded.get(name.lower(), "")


def origin_of(url: str) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError("pass an http(s) origin or a robots.txt URL")
    return urlunsplit((parts.scheme, parts.netloc, "", "", ""))


def is_robots_url(url: str) -> bool:
    path = urlsplit(url).path.lower().rstrip("/")
    return path.endswith("/robots.txt") or path == "robots.txt"


def strip_comment(line: str) -> str:
    return line.split("#", 1)[0]


def token_class(token: str) -> str:
    if token == "*":
        return "default"
    return TOKEN_CLASS.get(token.lower(), "other")


def classes_for(tokens: list[str]) -> list[str]:
    found: list[str] = []
    for token in tokens:
        label = token_class(token)
        if label not in found:
            found.append(label)
    return found


def match_length(pattern: str, path: str) -> int | None:
    """Octets of a matching Allow or Disallow pattern, ignoring * and a final $."""
    if pattern == "":
        return None
    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern
    regex = "^" + "".join(".*" if char == "*" else re.escape(char) for char in body)
    if anchored:
        regex += "$"
    if re.match(regex, path) is None:
        return None
    return len(body.replace("*", ""))


def crawl_allowed(allows: list[str], disallows: list[str], path: str = PATH) -> bool:
    """Longest matching path wins. An equal-length Allow wins over Disallow."""
    best = -1
    allowed = True
    for kind, patterns in (("disallow", disallows), ("allow", allows)):
        for pattern in patterns:
            length = match_length(pattern, path)
            if length is None:
                continue
            if length > best or (length == best and kind == "allow"):
                best = length
                allowed = kind == "allow"
    return allowed


def parse_usage(value: str) -> tuple[str, dict[str, str], list[str]]:
    """Return path, known y/n labels, and warnings.

    An absent path is "". A path is present only when the value starts with /.
    Labels are case-sensitive. Values must be the tokens y and n.
    """
    warnings: list[str] = []
    text = value.strip()
    path = ""
    statement = text
    if text.startswith("/"):
        split_at = len(text)
        for index, char in enumerate(text):
            if char in {" ", "\t"}:
                split_at = index
                break
        path = text[:split_at]
        statement = text[split_at:].strip()
    prefs: dict[str, str] = {}
    if not statement:
        warnings.append(f"Content-Usage has no preference: {value}")
        return path, prefs, warnings
    for part in statement.split(","):
        item = part.strip()
        if not item:
            continue
        if "=" not in item:
            warnings.append(f"Content-Usage item is not label=value: {item}")
            continue
        label, raw = item.split("=", 1)
        label = label.split(";", 1)[0].strip()
        token = raw.split(";", 1)[0].strip()
        if label not in USAGE_LABELS:
            continue
        if token not in {"y", "n"}:
            warnings.append(f"Content-Usage value is not y or n: {label}={token}")
            continue
        prefs[label] = token
    return path, prefs, warnings


def parse_signal(value: str) -> tuple[dict[str, str], list[str]]:
    warnings: list[str] = []
    found: dict[str, str] = {}
    for part in value.split(","):
        item = part.strip()
        if not item:
            continue
        if "=" not in item:
            warnings.append(f"Content-Signal item is not key=value: {item}")
            continue
        key, raw = item.split("=", 1)
        key = key.strip()
        raw = raw.strip()
        if key not in SIGNAL_LABELS or raw not in {"yes", "no"}:
            warnings.append(f"Content-Signal {key}={raw} is not a yes/no signal")
            continue
        found[key] = raw
    return found, warnings


def blank_group() -> dict[str, object]:
    return {
        "user_agents": [],
        "allows": [],
        "disallows": [],
        "usage": [],
        "signal": {},
        "crawl_delay": None,
        "rules_started": False,
        "warnings": [],
    }


def parse_robots(text: str) -> tuple[list[dict[str, object]], list[str], list[dict[str, str]], list[str]]:
    groups: list[dict[str, object]] = []
    sitemaps: list[str] = []
    ungrouped: list[dict[str, str]] = []
    warnings: list[str] = []
    current: dict[str, object] | None = None

    for raw in text.splitlines():
        line = strip_comment(raw).strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        field_name = key.strip().lower()
        field_value = value.strip()
        if field_name == "sitemap":
            if field_value:
                sitemaps.append(field_value)
            continue
        if field_name == "user-agent":
            if not field_value:
                warnings.append("a User-agent line has an empty token")
                continue
            if current is None or current["rules_started"]:
                current = blank_group()
                groups.append(current)
            agents = current["user_agents"]
            assert isinstance(agents, list)
            agents.append(field_value)
            continue
        if current is None:
            ungrouped.append({"field": field_name, "value": field_value})
            continue
        current["rules_started"] = True
        group_warnings = current["warnings"]
        assert isinstance(group_warnings, list)
        if field_name == "allow":
            allows = current["allows"]
            assert isinstance(allows, list)
            allows.append(field_value)
        elif field_name == "disallow":
            disallows = current["disallows"]
            assert isinstance(disallows, list)
            disallows.append(field_value)
        elif field_name == "content-usage":
            path, prefs, usage_warnings = parse_usage(field_value)
            group_warnings.extend(usage_warnings)
            if prefs:
                usage = current["usage"]
                assert isinstance(usage, list)
                usage.append({"path": path, **prefs})
        elif field_name == "content-signal":
            found, signal_warnings = parse_signal(field_value)
            group_warnings.extend(signal_warnings)
            signal = current["signal"]
            assert isinstance(signal, dict)
            signal.update(found)
        elif field_name == "crawl-delay":
            try:
                delay = float(field_value)
            except ValueError:
                group_warnings.append(f"Crawl-delay is not a number: {field_value}")
                continue
            if delay < 0:
                group_warnings.append(f"Crawl-delay is negative: {field_value}")
                continue
            current["crawl_delay"] = delay
    if ungrouped:
        warnings.append("rules before the first User-agent are not part of a group")
    return groups, sitemaps, ungrouped, warnings


def usage_for(rules: list[dict[str, str]], path: str = PATH) -> dict[str, str]:
    """Longest Content-Usage path wins. On one path, n wins over y."""
    best = -1
    chosen: list[dict[str, str]] = []
    for rule in rules:
        rule_path = rule.get("path", "")
        if rule_path == "":
            length = 0
        else:
            length_found = match_length(rule_path, path)
            if length_found is None:
                continue
            length = length_found
        if length > best:
            best = length
            chosen = [rule]
        elif length == best:
            chosen.append(rule)
    result = {"train-ai": "unknown", "search": "unknown"}
    for label in USAGE_LABELS:
        values = [rule[label] for rule in chosen if label in rule]
        if "n" in values:
            result[label] = "n"
        elif "y" in values:
            result[label] = "y"
    return result


def group_report(group: dict[str, object]) -> dict[str, object]:
    agents = list(group["user_agents"])
    allows = list(group["allows"])
    disallows = list(group["disallows"])
    usage = list(group["usage"])
    allowed = crawl_allowed(allows, disallows, PATH)
    prefs = usage_for(usage, PATH)
    train_ai = prefs["train-ai"] if allowed else "not-applicable"
    search_pref = prefs["search"] if allowed else "not-applicable"
    signal = dict(group["signal"]) or None
    return {
        "user_agents": agents,
        "class": classes_for(agents),
        "path": PATH,
        "crawl": "allow" if allowed else "disallow",
        "train_ai": train_ai,
        "search_pref": search_pref,
        "content_signal": signal,
        "crawl_delay": group["crawl_delay"],
        "content_usage": usage,
    }


def looks_like_html(body: str) -> bool:
    start = body.lstrip().lower()
    return start.startswith("<!doctype") or start.startswith("<html")


def add_group_warnings(
    warnings: list[str],
    reports: list[dict[str, object]],
    parsed_warnings: list[str],
) -> None:
    warnings.extend(parsed_warnings)
    star = next((row for row in reports if "*" in row["user_agents"]), None)
    star_states_usage = bool(star and star["content_usage"])
    any_delay = False
    for row in reports:
        agents = ", ".join(row["user_agents"])
        if row["crawl_delay"] is not None:
            any_delay = True
        if row["crawl"] == "disallow" and row["content_usage"]:
            warnings.append(
                f"Content-Usage on {agents} does not attach because / is disallowed"
            )
        if row["crawl"] == "allow" and row["train_ai"] != "n":
            warnings.append(f"train-ai=n is not stated for {agents} on /, which is crawlable")
        signal = row["content_signal"] or {}
        ai_train = signal.get("ai-train")
        if row["train_ai"] == "y" and ai_train == "no":
            warnings.append(f"Content-Signal ai-train=no and Content-Usage train-ai=y disagree for {agents}")
        if row["train_ai"] == "n" and ai_train == "yes":
            warnings.append(f"Content-Signal ai-train=yes and Content-Usage train-ai=n disagree for {agents}")
        named = [token for token in row["user_agents"] if token != "*"]
        if (
            named
            and row["crawl"] == "allow"
            and row["train_ai"] == "unknown"
            and star_states_usage
            and star is not row
        ):
            warnings.append(
                "Content-Usage on User-agent: * does not apply to "
                + ", ".join(named)
                + " because that token has its own group"
            )
        if row["crawl"] != "allow":
            continue
        ignores = [token for token in row["user_agents"] if token in IGNORES_ROBOTS]
        if ignores:
            joined = " and ".join(ignores)
            verb = "are" if len(ignores) > 1 else "is"
            note = f"{joined} {verb} allowed for /. Those products generally ignore robots.txt."
            if "Claude-User" in row["user_agents"]:
                note += " Claude-User is allowed for / and honors robots.txt."
            warnings.append(note)
    if any_delay:
        warnings.append("Crawl-delay is not defined by RFC 9309. It is not HTTP 429.")
    else:
        warnings.append(
            "Crawl-delay is absent. A rate limit is HTTP 429 with Retry-After, "
            "which is not a robots.txt directive."
        )


def result_shell(target: str) -> dict[str, object]:
    return {
        "target": target,
        "found": False,
        "robots_url": None,
        "final_url": None,
        "status": None,
        "content_type": None,
        "well_formed": False,
        "over_500kib": False,
        "groups": [],
        "sitemaps": [],
        "ungrouped": [],
        "http": {
            "url": None,
            "status": None,
            "retry_after": None,
            "content_usage": None,
            "rate_limit_observed": False,
        },
        "robots_response_headers": {"retry_after": None, "content_usage": None},
        "warnings": [],
    }


def fill_http(report: dict[str, object], home_url: str, home: Response, warnings: list[str]) -> None:
    retry_after = header(home.headers, "retry-after") or None
    content_usage = header(home.headers, "content-usage") or None
    observed = home.status == 429 and bool(retry_after)
    report["http"] = {
        "url": home.url or home_url,
        "status": home.status,
        "retry_after": retry_after,
        "content_usage": content_usage,
        "rate_limit_observed": observed,
    }
    if home.error:
        warnings.append(home.error)
    if home.status == 429 and not retry_after:
        warnings.append("homepage status is 429 and Retry-After is absent")
    elif home.status != 429:
        warnings.append(
            "the homepage request was not HTTP 429. "
            "One request cannot show that a 429 policy exists"
        )
    if not content_usage:
        warnings.append("the homepage response has no Content-Usage header")


def check(target: str, fetch: Fetch) -> dict[str, object]:
    origin = origin_of(target)
    report = result_shell(target)
    warnings: list[str] = []
    robots_url = target if is_robots_url(target) else origin + "/robots.txt"
    home_url = origin + "/"
    robots = fetch("GET", robots_url, read=True)
    home = fetch("GET", home_url, read=False)
    fill_http(report, home_url, home, warnings)

    report["robots_url"] = robots_url
    report["final_url"] = robots.url or robots_url
    report["status"] = robots.status
    report["content_type"] = header(robots.headers, "content-type") or None
    report["robots_response_headers"] = {
        "retry_after": header(robots.headers, "retry-after") or None,
        "content_usage": header(robots.headers, "content-usage") or None,
    }
    if robots.error:
        warnings.append(robots.error)
        report["warnings"] = warnings
        return report
    if robots.truncated:
        report["found"] = True
        report["over_500kib"] = True
        warnings.append("robots.txt exceeds 500 KiB and was not parsed")
        report["warnings"] = warnings
        return report
    if robots.status != 200:
        report["warnings"] = warnings
        return report

    report["found"] = True
    text = robots.body.decode("utf-8", errors="replace").lstrip("\ufeff")
    if looks_like_html(text):
        warnings.append("body is HTML, not a robots.txt file")
        report["warnings"] = warnings
        return report

    groups, sitemaps, ungrouped, parse_warnings = parse_robots(text)
    reports = [group_report(group) for group in groups]
    for group in groups:
        parse_warnings.extend(group["warnings"])
    add_group_warnings(warnings, reports, parse_warnings)
    if not sitemaps:
        warnings.append("robots.txt names no sitemap")
    report["well_formed"] = True
    report["groups"] = reports
    report["sitemaps"] = sitemaps
    report["ungrouped"] = ungrouped
    report["warnings"] = warnings
    return report


def live_fetch(timeout: float) -> Fetch:
    import httpx

    client = httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
        max_redirects=5,
    )

    def fetch(method: str, url: str, *, read: bool = False) -> Response:
        try:
            with client.stream(method, url) as response:
                length = response.headers.get("content-length")
                headers = {key: value for key, value in response.headers.items()}
                if read and length and length.isdigit() and int(length) > MAX_BYTES:
                    return Response(
                        status=response.status_code,
                        url=str(response.url),
                        headers=headers,
                        truncated=True,
                    )
                body = b""
                truncated = False
                if read:
                    chunks: list[bytes] = []
                    total = 0
                    for chunk in response.iter_bytes():
                        total += len(chunk)
                        if total > MAX_BYTES:
                            truncated = True
                            break
                        chunks.append(chunk)
                    body = b"".join(chunks)
                return Response(
                    status=response.status_code,
                    url=str(response.url),
                    headers=headers,
                    body=body,
                    truncated=truncated,
                )
        except httpx.HTTPError as exc:
            return Response(status=0, url=url, error=str(exc))

    fetch.client = client  # type: ignore[attr-defined]
    return fetch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check robots.txt AI preferences and one homepage response.")
    parser.add_argument("target", help="Site origin or a robots.txt URL")
    args = parser.parse_args(argv)
    try:
        origin_of(args.target)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    fetch = live_fetch(TIMEOUT_SECONDS)
    try:
        report = check(args.target, fetch)
    finally:
        client = getattr(fetch, "client", None)
        if client is not None:
            client.close()

    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if not report["found"] or not report["well_formed"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
