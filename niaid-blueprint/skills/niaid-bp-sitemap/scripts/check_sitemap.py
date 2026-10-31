#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""Check that a site publishes a sitemap and that a sample of its URLs answer.

Finds the sitemap from the URL you pass, from robots.txt, or from the
well-known paths /sitemap.xml and /sitemap_index.xml. Parses one document.
If that document is an index, opens one child. Samples up to 10 loc URLs.

Does not walk every child of an index and does not decide whether a URL is
a dataset record.

Usage::

    uv run --no-project scripts/check_sitemap.py https://example.org/
    uv run --no-project scripts/check_sitemap.py https://example.org/sitemap.xml
"""

from __future__ import annotations

import argparse
import gzip
import json
import random
import re
import sys
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urljoin, urlsplit, urlunsplit

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
MAX_BYTES = 5_000_000
MAX_LOCS = 50_000
DEFAULT_SAMPLE = 10
TIMEOUT_SECONDS = 15.0
USER_AGENT = "niaid-bp-sitemap/0.1 (+https://github.com/go-fair-us/ai-blueprint-core)"

W3C_LASTMOD = re.compile(
    r"^\d{4}-\d{2}-\d{2}"
    r"(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})?)?$"
)


@dataclass
class Response:
    status: int
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    error: str | None = None
    truncated: bool = False


Fetch = Callable[..., Response]


def local_name(tag: str) -> str:
    if tag.startswith("{"):
        return tag.rsplit("}", 1)[1]
    return tag


def header(headers: dict[str, str], name: str) -> str:
    folded = {key.lower(): value for key, value in headers.items()}
    return folded.get(name.lower(), "")


def is_sitemap_url(url: str) -> bool:
    path = urlsplit(url).path.lower()
    return path.endswith(".xml") or path.endswith(".xml.gz")


def origin_of(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError("pass an http(s) origin or a sitemap URL")
    return urlunsplit((parts.scheme, parts.netloc, "", "", ""))


def hostname_of(url: str) -> str:
    return (urlsplit(url).hostname or "").lower()


def sitemap_directives(robots_body: str) -> list[str]:
    found: list[str] = []
    for raw in robots_body.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip().lower() == "sitemap" and value.strip():
            found.append(value.strip())
    return found


def decode_body(_url: str, body: bytes) -> bytes:
    # Magic bytes, not the URL suffix. httpx already undoes Content-Encoding.
    if body.startswith(b"\x1f\x8b"):
        return gzip.decompress(body)
    return body


def lastmod_ok(value: str) -> bool:
    if not W3C_LASTMOD.match(value):
        return False
    try:
        datetime.strptime(value[:10], "%Y-%m-%d")
    except ValueError:
        return False
    if "T" not in value:
        return True
    clock = value.split("T", 1)[1]
    hour = int(clock[0:2])
    minute = int(clock[3:5])
    return 0 <= hour <= 23 and 0 <= minute <= 59


def parse_document(xml_bytes: bytes) -> tuple[str | None, bool, list[tuple[str, str | None]], list[str]]:
    """Return kind, namespace_ok, entries (loc, lastmod), warnings."""
    warnings: list[str] = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError(f"XML is not well formed: {exc}") from exc

    kind_name = local_name(root.tag)
    if kind_name not in {"urlset", "sitemapindex"}:
        warnings.append(f"root element is {kind_name or 'empty'}, not urlset or sitemapindex")
        return None, root.tag.startswith("{" + SITEMAP_NS + "}"), [], warnings

    namespace_ok = root.tag.startswith("{" + SITEMAP_NS + "}")
    if not namespace_ok:
        warnings.append("sitemap namespace is missing")

    parent = "sitemap" if kind_name == "sitemapindex" else "url"
    entries: list[tuple[str, str | None]] = []
    for node in list(root):
        if local_name(node.tag) != parent:
            continue
        loc = ""
        lastmod: str | None = None
        for child in list(node):
            name = local_name(child.tag)
            text = (child.text or "").strip()
            if name == "loc":
                loc = text
            elif name == "lastmod" and text:
                lastmod = text
        if not loc:
            warnings.append("a loc element is empty")
            continue
        entries.append((loc, lastmod))
    return kind_name, namespace_ok, entries, warnings


def absolute_http(url: str) -> bool:
    parts = urlsplit(url)
    return parts.scheme in {"http", "https"} and bool(parts.netloc)


def inspect_locs(
    entries: list[tuple[str, str | None]],
    sitemap_url: str,
) -> tuple[list[str], dict[str, str | None], list[str]]:
    warnings: list[str] = []
    locs: list[str] = []
    lastmods: dict[str, str | None] = {}
    seen: set[str] = set()
    host = hostname_of(sitemap_url)
    off_host = 0
    not_absolute = 0
    for loc, lastmod in entries:
        if loc in seen:
            warnings.append(f"duplicate loc: {loc}")
        seen.add(loc)
        if not absolute_http(loc):
            not_absolute += 1
        elif hostname_of(loc) != host:
            off_host += 1
        locs.append(loc)
        lastmods.setdefault(loc, lastmod)
    if not locs:
        warnings.append("urlset has no loc")
    if not_absolute:
        warnings.append(f"{not_absolute} loc values are not absolute http(s) URLs")
    if off_host:
        warnings.append(f"{off_host} loc hosts differ from the sitemap host")
    if len(locs) > MAX_LOCS:
        warnings.append(f"urlset has {len(locs)} loc values; the protocol limit is {MAX_LOCS}")
    return locs, lastmods, warnings


def choose_samples(locs: list[str], sample_size: int, seed: int) -> list[str]:
    if len(locs) <= sample_size:
        return list(locs)
    return random.Random(seed).sample(locs, sample_size)


def probe(fetch: Fetch, url: str) -> Response:
    if not absolute_http(url):
        return Response(status=0, url=url, error="not an absolute http(s) URL")
    head = fetch("HEAD", url, read=False)
    if head.error or head.status not in {405, 501}:
        return head
    return fetch("GET", url, read=False)


def sample_report(
    fetch: Fetch,
    locs: list[str],
    lastmods: dict[str, str | None],
    sample_size: int,
    seed: int,
) -> tuple[list[dict[str, object]], list[str]]:
    warnings: list[str] = []
    rows: list[dict[str, object]] = []
    for url in choose_samples(locs, sample_size, seed):
        lastmod = lastmods.get(url)
        response = probe(fetch, url)
        lastmod_valid: bool | None
        if lastmod is None:
            lastmod_valid = None
        else:
            lastmod_valid = lastmod_ok(lastmod)
            if not lastmod_valid:
                warnings.append(f"lastmod is not a W3C date: {lastmod}")
        rows.append(
            {
                "url": url,
                "status": response.status,
                "final_url": response.url,
                "error": response.error,
                "lastmod": lastmod,
                "lastmod_ok": lastmod_valid,
            }
        )
    return rows, warnings


def read_document(fetch: Fetch, url: str) -> tuple[Response, bytes | None, list[str]]:
    warnings: list[str] = []
    response = fetch("GET", url, read=True)
    if response.error:
        return response, None, [response.error]
    if response.truncated:
        warnings.append("body exceeds 5 MB and was not parsed")
        return response, None, warnings
    if response.status != 200 or not response.body:
        return response, None, warnings
    try:
        xml_bytes = decode_body(response.url or url, response.body)
    except (gzip.BadGzipFile, EOFError, OSError) as exc:
        warnings.append(f"gzip body could not be read: {exc}")
        return response, None, warnings
    return response, xml_bytes, warnings


def result_shell(target: str) -> dict[str, object]:
    return {
        "target": target,
        "found": False,
        "source": None,
        "sitemap_url": None,
        "final_url": None,
        "status": None,
        "content_type": None,
        "well_formed": False,
        "kind": None,
        "index_child_count": None,
        "child_sitemap_url": None,
        "not_opened": [],
        "loc_count": 0,
        "warnings": [],
        "samples": [],
    }


def fill_from_urlset(
    report: dict[str, object],
    fetch: Fetch,
    sitemap_url: str,
    xml_bytes: bytes,
    sample_size: int,
    seed: int,
) -> None:
    warnings = list(report["warnings"])
    try:
        kind, _namespace_ok, entries, parse_warnings = parse_document(xml_bytes)
    except ValueError as exc:
        warnings.append(str(exc))
        report["warnings"] = warnings
        report["well_formed"] = False
        return
    warnings.extend(parse_warnings)
    if kind != "urlset":
        if kind is not None:
            warnings.append(f"opened child is a {kind}, not a urlset")
        report["warnings"] = warnings
        return
    locs, lastmods, loc_warnings = inspect_locs(entries, sitemap_url)
    warnings.extend(loc_warnings)
    samples, sample_warnings = sample_report(fetch, locs, lastmods, sample_size, seed)
    warnings.extend(sample_warnings)
    report["loc_count"] = len(locs)
    report["samples"] = samples
    report["warnings"] = warnings


def remember_opened(
    report: dict[str, object],
    source: str,
    url: str,
    response: Response,
    warnings: list[str],
    not_opened: list[str],
) -> None:
    report["found"] = True
    report["source"] = source
    report["sitemap_url"] = url
    report["final_url"] = response.url or url
    report["status"] = response.status
    report["content_type"] = header(response.headers, "content-type") or None
    report["warnings"] = warnings
    report["not_opened"] = not_opened


def check(target: str, fetch: Fetch, sample_size: int = DEFAULT_SAMPLE, seed: int = 0) -> dict[str, object]:
    origin_of(target)
    report = result_shell(target)
    warnings: list[str] = []
    candidates: list[tuple[str, str]] = []

    if is_sitemap_url(target):
        candidates.append(("given", target))
    else:
        origin = origin_of(target)
        robots_url = origin + "/robots.txt"
        robots = fetch("GET", robots_url, read=True)
        directives: list[str] = []
        if robots.truncated:
            warnings.append("robots.txt exceeds 5 MB and was not fully read")
        elif robots.status == 200 and robots.body and not robots.error:
            directives = sitemap_directives(robots.body.decode("utf-8", errors="replace"))
        if directives:
            for directive in directives:
                candidates.append(("robots", urljoin(robots.url or robots_url, directive)))
        else:
            candidates.append(("well-known", origin + "/sitemap.xml"))
            candidates.append(("well-known", origin + "/sitemap_index.xml"))

    opened_url: str | None = None
    response: Response | None = None
    body: bytes | None = None
    not_opened: list[str] = []
    seen_urls: list[str] = []
    for index, (source, url) in enumerate(candidates):
        if url in seen_urls:
            continue
        seen_urls.append(url)
        if opened_url is not None:
            not_opened.append(url)
            continue
        got, got_body, notes = read_document(fetch, url)
        warnings.extend(notes)
        if got.truncated:
            rest = [later for _, later in candidates[index + 1 :] if later not in seen_urls]
            not_opened.extend(rest)
            remember_opened(report, source, url, got, warnings, not_opened)
            report["well_formed"] = False
            return report
        if got_body is None:
            continue
        opened_url = url
        response = got
        body = got_body
        report["source"] = source

    report["warnings"] = warnings
    report["not_opened"] = not_opened
    if opened_url is None or response is None or body is None:
        return report

    remember_opened(report, str(report["source"]), opened_url, response, warnings, not_opened)

    try:
        kind, _namespace_ok, entries, parse_warnings = parse_document(body)
    except ValueError as exc:
        warnings.append(str(exc))
        report["warnings"] = warnings
        report["well_formed"] = False
        return report

    warnings.extend(parse_warnings)
    report["well_formed"] = True
    report["kind"] = kind
    report["warnings"] = warnings

    if kind == "sitemapindex":
        child_urls = [urljoin(response.url or opened_url, loc) for loc, _lastmod in entries]
        report["index_child_count"] = len(child_urls)
        if not child_urls:
            warnings.append("sitemap index has no child loc")
            report["warnings"] = warnings
            return report
        child_url = child_urls[0]
        not_opened.extend(child_urls[1:])
        report["not_opened"] = not_opened
        child_response, child_body, child_notes = read_document(fetch, child_url)
        warnings.extend(child_notes)
        report["warnings"] = warnings
        if child_response.truncated or child_body is None:
            if child_body is None and not child_response.truncated:
                warnings.append("the first child sitemap did not return a document")
            if child_response.truncated:
                report["well_formed"] = False
            report["warnings"] = warnings
            return report
        report["child_sitemap_url"] = child_response.url or child_url
        fill_from_urlset(
            report,
            fetch,
            child_response.url or child_url,
            child_body,
            sample_size,
            seed,
        )
        return report

    if kind == "urlset":
        locs, lastmods, loc_warnings = inspect_locs(entries, response.url or opened_url)
        warnings.extend(loc_warnings)
        samples, sample_warnings = sample_report(fetch, locs, lastmods, sample_size, seed)
        warnings.extend(sample_warnings)
        report["loc_count"] = len(locs)
        report["samples"] = samples
        report["warnings"] = warnings
        return report

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
                if read and length and length.isdigit() and int(length) > MAX_BYTES:
                    return Response(
                        status=response.status_code,
                        url=str(response.url),
                        headers={key: value for key, value in response.headers.items()},
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
                    headers={key: value for key, value in response.headers.items()},
                    body=body,
                    truncated=truncated,
                )
        except httpx.HTTPError as exc:
            return Response(status=0, url=url, error=str(exc))

    fetch.client = client  # type: ignore[attr-defined]
    return fetch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a site sitemap and sample its URLs.")
    parser.add_argument("target", help="Site origin or a sitemap URL")
    parser.add_argument("--sample", type=int, default=DEFAULT_SAMPLE, help="How many loc URLs to request")
    parser.add_argument("--seed", type=int, default=0, help="Sample seed, so a repeat run picks the same URLs")
    args = parser.parse_args(argv)
    if args.sample < 0:
        parser.error("--sample must be zero or greater")
    try:
        origin_of(args.target)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    fetch = live_fetch(TIMEOUT_SECONDS)
    try:
        report = check(args.target, fetch, sample_size=args.sample, seed=args.seed)
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
