"""Fetch pages with a local Obscura binary (no third-party render proxy)."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from urllib.parse import urljoin, urlparse

from defs.models import FetchedPage, Link
from defs.paths import DEFAULT_OBSCURA_BIN
from defs.progress import say

EVAL_PAGE_GRAPH = """(function(){
  const links = Array.from(document.querySelectorAll('a[href]')).map(a => ({
    href: a.href,
    text: (a.textContent || '').trim().slice(0, 120)
  }));
  const jsonld = Array.from(
    document.querySelectorAll('script[type="application/ld+json"]')
  ).map(s => s.textContent || '');
  return {links: links, jsonld: jsonld};
})()"""

_BLOCKED_SCHEMES = {"mailto", "javascript", "tel", "data", "ftp"}
_LOGIN_PARTS = {"login", "signin", "signup", "logout", "register", "auth"}
_KEEP_HINTS = (
    "doi.org",
    "dx.doi.org",
    "orcid.org",
    "ror.org",
    "license",
    "creativecommons",
    "spdx",
    "pubmed",
    "pmc.ncbi",
    "clinicaltrials",
    "nct",
    "grant",
    "funding",
    "citation",
    "publication",
    "protocol",
    "dataset",
    "data-use",
    "dua",
    "dar.pdf",
    "conditions-of-access",
)


class ObscuraError(RuntimeError):
    """Obscura subprocess failed."""


def resolve_obscura_bin(explicit: str | Path | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    env = os.environ.get("OBSCURA_BIN")
    if env:
        return Path(env).expanduser()
    return DEFAULT_OBSCURA_BIN


def is_fetchable(url: str) -> bool:
    raw = (url or "").strip()
    if not raw or raw.startswith("#"):
        return False
    parsed = urlparse(raw)
    scheme = parsed.scheme.lower()
    if scheme in _BLOCKED_SCHEMES:
        return False
    if scheme not in {"http", "https"}:
        return False
    parts = {p.lower() for p in parsed.path.split("/") if p}
    if parts & _LOGIN_PARTS:
        return False
    return True


def normalize_url(url: str, base: str | None = None) -> str:
    joined = urljoin(base, url) if base else url
    parsed = urlparse(joined)
    return parsed._replace(fragment="").geturl()


def keep_hint_score(link: Link) -> int:
    blob = f"{link.href} {link.text}".lower()
    return sum(1 for hint in _KEEP_HINTS if hint in blob)


def rank_links(links: list[Link], *, limit: int = 40) -> list[Link]:
    seen: set[str] = set()
    scored: list[tuple[int, Link]] = []
    for link in links:
        href = (link.href or "").strip()
        if not is_fetchable(href) or href in seen:
            continue
        seen.add(href)
        scored.append((keep_hint_score(link), Link(href=href, text=link.text)))
    scored.sort(key=lambda item: (-item[0], item[1].href))
    hinted = [link for score, link in scored if score > 0]
    rest = [link for score, link in scored if score == 0]
    return (hinted + rest)[:limit]


class ObscuraClient:
    def __init__(self, bin_path: str | Path | None = None, timeout: int = 30) -> None:
        self.bin_path = resolve_obscura_bin(bin_path)
        self.timeout = timeout
        if not self.bin_path.is_file():
            raise FileNotFoundError(
                f"Obscura binary not found: {self.bin_path}. "
                "Set OBSCURA_BIN or pass --obscura-bin."
            )

    def _run(self, args: list[str]) -> str:
        cmd = [str(self.bin_path), "fetch", *args]
        label = "eval" if "--eval" in args else next(
            (args[i + 1] for i, a in enumerate(args) if a == "--dump"), "fetch"
        )
        url = next((a for a in args if a.startswith("http")), args[0] if args else "")
        say(f"obscura {label}: {url}")
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout + 10,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            say(f"obscura {label} timed out after {self.timeout + 10}s")
            raise ObscuraError(f"Obscura timed out for {args[:1]!r}") from exc
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or f"exit {proc.returncode}").strip()
            say(f"obscura {label} failed: {err[:200]}")
            raise ObscuraError(err)
        say(f"obscura {label} done ({len(proc.stdout)} chars)")
        return proc.stdout

    def dump_markdown(self, url: str) -> str:
        return self._run(
            [url, "--dump", "markdown", "-q", "--timeout", str(self.timeout)]
        )

    def eval_page_graph(self, url: str) -> tuple[list[Link], list[str]]:
        raw = self._run(
            [url, "-q", "--timeout", str(self.timeout), "--eval", EVAL_PAGE_GRAPH]
        )
        data = json.loads(raw)
        links = [
            Link(href=item.get("href", ""), text=item.get("text", "") or "")
            for item in data.get("links", [])
            if isinstance(item, dict)
        ]
        jsonld = [block for block in data.get("jsonld", []) if isinstance(block, str) and block.strip()]
        return links, jsonld


class FetchSession:
    def __init__(
        self,
        client: ObscuraClient,
        *,
        max_depth: int = 2,
        max_pages: int = 5,
    ) -> None:
        self.client = client
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.pages: list[FetchedPage] = []
        self._by_url: dict[str, FetchedPage] = {}
        self._depth: dict[str, int] = {}

    def web_page_count(self) -> int:
        return sum(1 for page in self.pages if page.url.startswith(("http://", "https://")))

    def add_local_file(self, path: Path) -> FetchedPage:
        text = path.read_text(encoding="utf-8", errors="replace")
        page = FetchedPage(
            url=path.resolve().as_uri(),
            depth=0,
            markdown=text,
        )
        self.pages.append(page)
        self._by_url[page.url] = page
        return page

    def fetch(self, url: str, *, depth: int | None = None) -> FetchedPage:
        normalized = normalize_url(url)
        if normalized in self._by_url:
            return self._by_url[normalized]
        if not is_fetchable(normalized):
            return FetchedPage(url=normalized, error="rejected URL", depth=depth or 0)
        if depth is None:
            depth = self._depth.get(normalized, 0 if self.web_page_count() == 0 else 1)
        if depth > self.max_depth:
            say(f"skip {normalized} (depth {depth} > max {self.max_depth})")
            return FetchedPage(
                url=normalized,
                depth=depth,
                error=f"rejected: depth {depth} exceeds max {self.max_depth}",
            )
        if self.web_page_count() >= self.max_pages:
            say(f"skip {normalized} (page budget {self.max_pages} exhausted)")
            return FetchedPage(
                url=normalized,
                depth=depth,
                error=f"rejected: page budget {self.max_pages} exhausted",
            )
        try:
            markdown = self.client.dump_markdown(normalized)
            links, jsonld = self.client.eval_page_graph(normalized)
        except (ObscuraError, json.JSONDecodeError, OSError) as exc:
            page = FetchedPage(url=normalized, depth=depth, error=str(exc))
            self.pages.append(page)
            self._by_url[normalized] = page
            return page
        page = FetchedPage(
            url=normalized,
            depth=depth,
            markdown=markdown or "",
            jsonld_blocks=jsonld,
            links=rank_links(links),
        )
        if not page.ok:
            page.error = "empty page after Obscura fetch"
        self.pages.append(page)
        self._by_url[normalized] = page
        self._depth[normalized] = depth
        for link in page.links:
            child = normalize_url(link.href, normalized)
            self._depth.setdefault(child, depth + 1)
        return page

    def list_links(self, url: str) -> list[Link]:
        page = self._by_url.get(normalize_url(url))
        if page is None:
            page = self.fetch(url)
        return page.links

    def evidence_blob(self) -> str:
        parts: list[str] = []
        for page in self.pages:
            parts.append(f"### SOURCE {page.url}")
            if page.error:
                parts.append(f"[unreadable] {page.error}")
            if page.markdown:
                parts.append(page.markdown)
            for block in page.jsonld_blocks:
                parts.append(f"### EMBEDDED JSON-LD {page.url}")
                parts.append(block)
        return "\n\n".join(parts)
