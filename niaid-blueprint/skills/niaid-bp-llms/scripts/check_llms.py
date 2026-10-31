#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""Check that a site publishes an llms.txt file and that a sample of its links answer.

The format is The /llms.txt file, v2 (Jeremy Howard, 10 August 2026):
https://llmstxt.org/

Finds /llms.txt, or one llms.txt linked from the homepage. Parses one file.
Samples up to 10 same-host file-list links. Does not open a nested llms.txt
and does not decide whether a link is a dataset record.

Usage::

    uv run --no-project scripts/check_llms.py https://example.org/
    uv run --no-project scripts/check_llms.py https://example.org/llms.txt
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlsplit, urlunsplit

MAX_BYTES = 500 * 1024
CONTEXT_BYTES = 100 * 1024
DEFAULT_SAMPLE = 10
TIMEOUT_SECONDS = 15.0
USER_AGENT = "niaid-bp-llms/0.1 (+https://github.com/go-fair-us/ai-blueprint-core)"

LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")
LIST_ITEM = re.compile(r"^(?:[-*+]|\d+[.)])\s+(.*)$")
TAG = re.compile(r"<(link|a)\b([^>]*)>", re.IGNORECASE)
ATTR = re.compile(
    r"""([A-Za-z_:][-A-Za-z0-9_:.]*)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))"""
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


def header(headers: dict[str, str], name: str) -> str:
    folded = {key.lower(): value for key, value in headers.items()}
    return folded.get(name.lower(), "")


def origin_of(url: str) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError("pass an http(s) origin or an llms.txt URL")
    return urlunsplit((parts.scheme, parts.netloc, "", "", ""))


def is_llms_url(url: str) -> bool:
    path = urlsplit(url).path.lower().rstrip("/")
    return path.endswith("/llms.txt") or path == "llms.txt"


def hostname_of(url: str) -> str:
    return (urlsplit(url).hostname or "").lower()


def absolute_http(url: str) -> bool:
    parts = urlsplit(url)
    return parts.scheme in {"http", "https"} and bool(parts.netloc)


def looks_like_html(body: str) -> bool:
    start = body.lstrip().lower()
    return start.startswith("<!doctype") or start.startswith("<html")


def link_shape(url: str) -> str:
    name = urlsplit(url).path.rstrip("/").split("/")[-1].lower()
    if name in {"index.md", "index.html.md"}:
        return "index-md"
    if name.endswith(".html.md"):
        return "html-md"
    if name.endswith(".md"):
        return "md"
    return "other"


def list_item_body(line: str) -> str | None:
    match = LIST_ITEM.match(line.strip())
    if match is None:
        return None
    return match.group(1).strip()


def parse_link(item: str) -> dict[str, str | None] | None:
    match = LINK.search(item)
    if match is None:
        return None
    notes = None
    rest = item[match.end() :].strip()
    if rest.startswith(":"):
        notes = rest[1:].strip() or None
    return {"name": match.group(1).strip(), "url": match.group(2).strip(), "notes": notes}


def parse_llms(text: str) -> dict[str, object]:
    """Return title, summary, sections, warnings, and whether the section order holds."""
    phase = "start"
    title: str | None = None
    quotes: list[str] = []
    sections: list[dict[str, object]] = []
    warnings: list[str] = []
    well_formed = True
    in_fence = False
    current: dict[str, object] | None = None
    noted_non_list = False

    def fail(note: str) -> None:
        nonlocal well_formed
        well_formed = False
        warnings.append(note)

    for raw in text.lstrip("\ufeff").splitlines():
        stripped = raw.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue
        if stripped.startswith("###"):
            warnings.append(f"heading is deeper than H2: {stripped}")
            if phase == "start":
                fail("content appears before the H1")
            continue
        if stripped.startswith("## "):
            if title is None:
                fail("an H2 appears before the H1")
            name = stripped[3:].strip() or "(untitled)"
            current = {"name": name, "optional": name == "Optional", "links": []}
            sections.append(current)
            phase = "files"
            noted_non_list = False
            continue
        if stripped.startswith("# "):
            if phase != "start":
                fail("an H1 appears after other content")
                continue
            heading = stripped[2:].strip()
            if not heading:
                fail("the H1 is empty")
            else:
                title = heading
                phase = "quote"
            continue
        if stripped.startswith(">"):
            if phase == "start":
                fail("content appears before the H1")
            elif phase == "quote":
                quotes.append(stripped.lstrip(">").strip())
            else:
                warnings.append("a blockquote appears after other content")
            continue
        if phase == "start":
            fail("content appears before the H1")
            continue
        if phase == "quote":
            phase = "prose"
        if phase == "prose":
            continue
        item = list_item_body(stripped)
        if item is None:
            if current is not None and not noted_non_list:
                warnings.append(
                    f"H2 section {current['name']} has text that is not a file-list item"
                )
                noted_non_list = True
            continue
        parsed = parse_link(item)
        if parsed is None:
            warnings.append(f"file-list item is not a Markdown link: {item}")
            continue
        assert current is not None
        links = current["links"]
        assert isinstance(links, list)
        links.append(parsed)

    if in_fence:
        warnings.append("a code fence is not closed")
    if title is None:
        fail("llms.txt has no H1")
    summary = " ".join(part for part in quotes if part) or None
    return {
        "well_formed": well_formed,
        "title": title,
        "summary": summary,
        "sections": sections,
        "warnings": warnings,
    }


def annotate(
    sections: list[dict[str, object]],
    base_url: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[str], int]:
    host = hostname_of(base_url)
    public_sections: list[dict[str, object]] = []
    flat: list[dict[str, object]] = []
    nested: list[str] = []
    off_host = 0
    for section in sections:
        public_links: list[dict[str, object]] = []
        links = section["links"]
        assert isinstance(links, list)
        for link in links:
            resolved = urljoin(base_url, str(link["url"]))
            shape = link_shape(resolved)
            same_host = absolute_http(resolved) and hostname_of(resolved) == host
            is_nested = is_llms_url(resolved)
            if is_nested:
                nested.append(resolved)
            elif absolute_http(resolved) and not same_host:
                off_host += 1
            public = {
                "name": link["name"],
                "url": link["url"],
                "notes": link["notes"],
                "shape": shape,
            }
            public_links.append(public)
            flat.append(
                {
                    **public,
                    "resolved": resolved,
                    "same_host": same_host,
                    "nested": is_nested,
                    "section": section["name"],
                    "optional": section["optional"],
                }
            )
        public_sections.append(
            {
                "name": section["name"],
                "optional": section["optional"],
                "links": public_links,
            }
        )
    return public_sections, flat, nested, off_host


def choose_samples(links: list[dict[str, object]], sample_size: int, seed: int) -> list[dict[str, object]]:
    primary = [link for link in links if not link["optional"] and link["same_host"] and not link["nested"]]
    extra = [link for link in links if link["optional"] and link["same_host"] and not link["nested"]]
    if len(primary) >= sample_size:
        return random.Random(seed).sample(primary, sample_size)
    need = sample_size - len(primary)
    if len(extra) <= need:
        return primary + extra
    return primary + random.Random(seed).sample(extra, need)


def probe(fetch: Fetch, url: str) -> Response:
    if not absolute_http(url):
        return Response(status=0, url=url, error="not an absolute http(s) URL")
    head = fetch("HEAD", url, read=False)
    if head.error or head.status not in {405, 501}:
        return head
    return fetch("GET", url, read=False)


def split_link_header(value: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    quoted = False
    angle = False
    for char in value:
        if char == '"' and not angle:
            quoted = not quoted
        elif char == "<" and not quoted:
            angle = True
        elif char == ">" and not quoted:
            angle = False
        if char == "," and not quoted and not angle:
            parts.append("".join(buf).strip())
            buf = []
            continue
        buf.append(char)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return [part for part in parts if part]


def parse_link_value(part: str) -> tuple[str, set[str], str]:
    url = ""
    if "<" in part and ">" in part:
        url = part.split("<", 1)[1].split(">", 1)[0].strip()
    rels: set[str] = set()
    media_type = ""
    rest = part.split(">", 1)[1] if ">" in part else part
    for piece in rest.split(";"):
        if "=" not in piece:
            continue
        key, raw = piece.split("=", 1)
        key = key.strip().lower()
        raw = raw.strip().strip('"').strip("'")
        if key == "rel":
            rels.update(token.lower() for token in raw.split())
        elif key == "type":
            media_type = raw.lower()
    return url, rels, media_type


def tag_attrs(blob: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for match in ATTR.finditer(blob):
        value = next(group for group in match.groups()[1:] if group is not None)
        attrs[match.group(1).lower()] = value
    return attrs


def relations_from(response: Response, page_url: str) -> tuple[list[str], list[str], list[str]]:
    """Return alternate Markdown URLs, describedby llms.txt URLs, and every href."""
    alternate: list[str] = []
    describedby: list[str] = []
    hrefs: list[str] = []

    def consider(url: str, rels: set[str], media_type: str) -> None:
        if not url:
            return
        resolved = urljoin(page_url, url)
        hrefs.append(resolved)
        if "alternate" in rels and media_type.startswith("text/markdown") and resolved not in alternate:
            alternate.append(resolved)
        if "describedby" in rels and is_llms_url(resolved) and resolved not in describedby:
            describedby.append(resolved)

    for part in split_link_header(header(response.headers, "link")):
        consider(*parse_link_value(part))
    if response.body:
        text = response.body.decode("utf-8", errors="replace")
        for match in TAG.finditer(text):
            attrs = tag_attrs(match.group(2))
            href = attrs.get("href", "")
            if match.group(1).lower() == "a":
                if href:
                    hrefs.append(urljoin(page_url, href))
                continue
            rels = set(attrs.get("rel", "").lower().split())
            consider(href, rels, attrs.get("type", "").lower())
    return alternate, describedby, hrefs


def read_document(fetch: Fetch, url: str) -> Response:
    return fetch("GET", url, read=True)


def document_text(response: Response) -> str | None:
    if response.error or response.truncated or response.status != 200 or not response.body:
        return None
    text = response.body.decode("utf-8", errors="replace")
    if looks_like_html(text):
        return None
    return text


def result_shell(target: str) -> dict[str, object]:
    return {
        "target": target,
        "found": False,
        "source": None,
        "llms_url": None,
        "final_url": None,
        "status": None,
        "content_type": None,
        "well_formed": False,
        "title": None,
        "summary": None,
        "sections": [],
        "link_count": 0,
        "off_host_count": 0,
        "nested": [],
        "samples": [],
        "homepage": {
            "url": None,
            "status": None,
            "alternate_markdown": None,
            "describedby": None,
        },
        "warnings": [],
    }


def fill_homepage(
    report: dict[str, object],
    home_url: str,
    home: Response,
    warnings: list[str],
) -> list[str]:
    alternate, describedby, hrefs = relations_from(home, home.url or home_url)
    report["homepage"] = {
        "url": home.url or home_url,
        "status": home.status,
        "alternate_markdown": alternate or None,
        "describedby": describedby or None,
    }
    if home.error:
        warnings.append(home.error)
    if not alternate:
        warnings.append('homepage has no rel="alternate" type="text/markdown"')
    if not describedby:
        warnings.append('homepage has no rel="describedby" llms.txt')
    return hrefs


def apply_document(
    report: dict[str, object],
    fetch: Fetch,
    source: str,
    url: str,
    response: Response,
    text: str,
    warnings: list[str],
    sample_size: int,
    seed: int,
) -> None:
    report["found"] = True
    report["source"] = source
    report["llms_url"] = url
    report["final_url"] = response.url or url
    report["status"] = response.status
    report["content_type"] = header(response.headers, "content-type") or None
    if len(response.body) > CONTEXT_BYTES:
        warnings.append("llms.txt is over 100 KiB and may be too large for a context window")
    parsed = parse_llms(text)
    warnings.extend(parsed["warnings"])
    sections, flat, nested, off_host = annotate(parsed["sections"], response.url or url)
    if not flat:
        warnings.append("llms.txt has no file-list links")
    other = sum(1 for link in flat if link["shape"] == "other" and not link["nested"])
    if other:
        noun = "link" if other == 1 else "links"
        verb = "does" if other == 1 else "do"
        warnings.append(f"{other} file-list {noun} {verb} not use a Markdown URL shape")
    if nested:
        warnings.append("linked llms.txt files were not opened")
    samples: list[dict[str, object]] = []
    for link in choose_samples(flat, sample_size, seed):
        probed = probe(fetch, str(link["resolved"]))
        samples.append(
            {
                "url": link["resolved"],
                "status": probed.status,
                "final_url": probed.url,
                "error": probed.error,
                "shape": link["shape"],
                "section": link["section"],
            }
        )
    report["well_formed"] = parsed["well_formed"]
    report["title"] = parsed["title"]
    report["summary"] = parsed["summary"]
    report["sections"] = sections
    report["link_count"] = len(flat)
    report["off_host_count"] = off_host
    report["nested"] = nested
    report["samples"] = samples
    report["warnings"] = warnings


def check(
    target: str,
    fetch: Fetch,
    sample_size: int = DEFAULT_SAMPLE,
    seed: int = 0,
) -> dict[str, object]:
    origin = origin_of(target)
    report = result_shell(target)
    warnings: list[str] = []
    home_url = origin + "/"
    home: Response | None = None

    if is_llms_url(target):
        response = read_document(fetch, target)
        text = document_text(response)
        if response.truncated:
            report["found"] = True
            report["source"] = "given"
            report["llms_url"] = target
            report["final_url"] = response.url or target
            report["status"] = response.status
            warnings.append("llms.txt exceeds 500 KiB and was not parsed")
        elif text is None and response.status == 200 and response.body and looks_like_html(
            response.body.decode("utf-8", errors="replace")
        ):
            report["found"] = True
            report["source"] = "given"
            report["llms_url"] = target
            report["final_url"] = response.url or target
            report["status"] = response.status
            report["content_type"] = header(response.headers, "content-type") or None
            warnings.append("body is HTML, not an llms.txt file")
        elif text is not None:
            home = read_document(fetch, home_url)
            fill_homepage(report, home_url, home, warnings)
            apply_document(report, fetch, "given", target, response, text, warnings, sample_size, seed)
            return report
        else:
            if response.error:
                warnings.append(response.error)
            report["llms_url"] = target
            report["status"] = response.status
    else:
        well_known = origin + "/llms.txt"
        response = read_document(fetch, well_known)
        text = document_text(response)
        if response.truncated:
            report["found"] = True
            report["source"] = "well-known"
            report["llms_url"] = well_known
            report["final_url"] = response.url or well_known
            report["status"] = response.status
            warnings.append("llms.txt exceeds 500 KiB and was not parsed")
        elif text is not None:
            home = read_document(fetch, home_url)
            fill_homepage(report, home_url, home, warnings)
            apply_document(
                report, fetch, "well-known", well_known, response, text, warnings, sample_size, seed
            )
            return report
        else:
            if response.status == 200 and response.body and looks_like_html(
                response.body.decode("utf-8", errors="replace")
            ):
                warnings.append(f"{well_known} body is HTML, not an llms.txt file")
            elif response.error:
                warnings.append(response.error)
            home = read_document(fetch, home_url)
            hrefs = fill_homepage(report, home_url, home, warnings)
            seen = {well_known}
            chosen = next((href for href in hrefs if is_llms_url(href) and href not in seen), None)
            if chosen is not None:
                found = read_document(fetch, chosen)
                found_text = document_text(found)
                if found.truncated:
                    report["found"] = True
                    report["source"] = "homepage"
                    report["llms_url"] = chosen
                    report["status"] = found.status
                    warnings.append("llms.txt exceeds 500 KiB and was not parsed")
                elif found_text is not None:
                    apply_document(
                        report, fetch, "homepage", chosen, found, found_text, warnings, sample_size, seed
                    )
                    return report
                elif found.status == 200 and found.body and looks_like_html(
                    found.body.decode("utf-8", errors="replace")
                ):
                    report["found"] = True
                    report["source"] = "homepage"
                    report["llms_url"] = chosen
                    report["final_url"] = found.url or chosen
                    report["status"] = found.status
                    warnings.append("body is HTML, not an llms.txt file")
                elif found.error:
                    warnings.append(found.error)

    if home is None:
        home = read_document(fetch, home_url)
        fill_homepage(report, home_url, home, warnings)
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
    parser = argparse.ArgumentParser(description="Check an llms.txt file and sample its links.")
    parser.add_argument("target", help="Site origin or an llms.txt URL")
    parser.add_argument("--sample", type=int, default=DEFAULT_SAMPLE, help="How many same-host links to request")
    parser.add_argument("--seed", type=int, default=0, help="Sample seed, so a repeat run picks the same links")
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
