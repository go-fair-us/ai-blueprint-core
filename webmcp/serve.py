#!/usr/bin/env python3
"""Serve the WebMCP handbook with headers Chrome's WebMCP API requires."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
XAI_RESPONSES_URL = "https://api.x.ai/v1/responses"
DEFAULT_MODEL = "grok-4.6"
MAX_BODY_BYTES = 200_000
MAX_QUESTION_CHARS = 4_000
MAX_PASSAGES = 8

SYSTEM_PROMPT = """You are a concise guide to the NIAID Blueprint for Digital Objects.
Answer the user's question using ONLY the retrieved handbook passages.
Write a brief narrative of 2–4 short paragraphs in plain language.
Weave in markdown links to the relevant pages using the provided href paths
(for example [Persistent identifiers](/topics/persistent-identifiers.html)).
Do not mention tools, JSON, retrieval, or that you were given source material.
Do not invent requirements that are not in the passages.
If the passages are only a partial match, say what they do cover and point
to the closest pages."""


def load_dotenv() -> None:
    for path in (ROOT / ".env", ROOT.parent / ".env"):
        if not path.is_file():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if key.startswith("export "):
                key = key[len("export ") :].strip()
            value = value.strip().strip("'").strip('"')
            if key and key not in os.environ:
                os.environ[key] = value


def narrative_configured() -> bool:
    return bool(os.environ.get("XAI_API_KEY"))


def narrative_model() -> str:
    return os.environ.get("BLUEPRINT_CHAT_MODEL", DEFAULT_MODEL)


def extract_output_text(payload: dict) -> str:
    if not isinstance(payload, dict):
        return ""
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    chunks: list[str] = []
    for item in payload.get("output") or []:
        if not isinstance(item, dict):
            continue
        for part in item.get("content") or []:
            if not isinstance(part, dict):
                continue
            if part.get("type") in ("output_text", "text"):
                text = part.get("text")
                if isinstance(text, str) and text.strip():
                    chunks.append(text.strip())
    return "\n".join(chunks).strip()


def _clean_passages(raw) -> list[dict]:
    if not isinstance(raw, list):
        return []
    cleaned = []
    for item in raw[:MAX_PASSAGES]:
        if not isinstance(item, dict):
            continue
        excerpt = str(item.get("excerpt") or "")[:2_000]
        summary = str(item.get("summary") or "")[:800]
        cleaned.append(
            {
                "slug": str(item.get("slug") or "")[:120],
                "title": str(item.get("title") or "")[:200],
                "href": str(item.get("href") or "")[:200],
                "summary": summary,
                "excerpt": excerpt,
            }
        )
    return cleaned


def build_narrative_input(question: str, passages: list[dict]) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Question: {question}\n\n"
                "Retrieved handbook passages:\n"
                f"{json.dumps(passages, indent=2)}"
            ),
        },
    ]


def request_narrative(question: str, passages: list[dict]) -> str:
    key = os.environ.get("XAI_API_KEY")
    if not key:
        raise RuntimeError("XAI_API_KEY is not set")
    body = json.dumps(
        {
            "model": narrative_model(),
            "store": False,
            "input": build_narrative_input(question, passages),
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        XAI_RESPONSES_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"xAI HTTP {err.code}: {detail}") from err
    text = extract_output_text(payload)
    if not text:
        raise RuntimeError("xAI returned an empty narrative")
    return text


class HandbookHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Origin-Agent-Cluster", "?1")
        self.send_header("Permissions-Policy", "tools=(self)")
        super().end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/status":
            self._send_json(
                200,
                {"narrative": narrative_configured(), "model": narrative_model()},
            )
            return
        if path == "/api/narrative":
            self._send_json(405, {"error": "Use POST."})
            return
        super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/narrative":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            self._send_json(400, {"error": "Empty request body."})
            return
        if length > MAX_BODY_BYTES:
            self._send_json(413, {"error": "Request is too large."})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "Body must be JSON."})
            return
        if not isinstance(payload, dict):
            self._send_json(400, {"error": "Body must be a JSON object."})
            return
        question = str(payload.get("question") or "").strip()
        if not question:
            self._send_json(400, {"error": "Provide a question."})
            return
        if len(question) > MAX_QUESTION_CHARS:
            self._send_json(400, {"error": "Question is too long."})
            return
        if not narrative_configured():
            self._send_json(
                503,
                {
                    "error": "Narrative model is not configured. Set XAI_API_KEY.",
                    "configured": False,
                },
            )
            return
        passages = _clean_passages(payload.get("passages"))
        try:
            text = request_narrative(question, passages)
        except Exception as err:  # noqa: BLE001 — surface model errors to the chat
            self._send_json(502, {"error": str(err), "configured": True})
            return
        self._send_json(200, {"text": text, "model": narrative_model()})

    def _send_json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8088, help="Port (default 8088)")
    args = parser.parse_args()

    httpd = ThreadingHTTPServer((args.host, args.port), HandbookHandler)
    print(f"Serving {ROOT} at http://{args.host}:{args.port}/")
    print("Origin-Agent-Cluster: ?1")
    print("Permissions-Policy: tools=(self)")
    print(f"Chat narrative: {'on' if narrative_configured() else 'off (set XAI_API_KEY)'} · {narrative_model()}")
    print("Chrome: enable chrome://flags/#enable-webmcp-testing and load 127.0.0.1, not a LAN IP.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
