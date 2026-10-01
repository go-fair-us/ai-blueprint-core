#!/usr/bin/env python3
"""Serve the OKF WebMCP browser with headers Chrome's WebMCP API requires."""

from __future__ import annotations

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from index_builder import (
    BundlePathError,
    DEFAULT_BUNDLE,
    WEB_ROOT,
    build_payload,
    resolve_bundle_file,
)

ROOT = WEB_ROOT


class OkfHandler(SimpleHTTPRequestHandler):
    def __init__(
        self,
        *args,
        payload: dict,
        bundle_root: Path,
        index_bytes: bytes,
        tree_bytes: bytes,
        **kwargs,
    ):
        self._payload = payload
        self._bundle_root = bundle_root
        self._index_bytes = index_bytes
        self._tree_bytes = tree_bytes
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path in ("/data/index.json", "/data/index"):
            self._send_bytes(self._index_bytes, "application/json; charset=utf-8")
            return
        if path in ("/data/tree.json", "/data/tree"):
            self._send_bytes(self._tree_bytes, "application/json; charset=utf-8")
            return
        if path.startswith("/bundle/"):
            rel = unquote(path[len("/bundle/") :])
            try:
                file_path = resolve_bundle_file(self._bundle_root, rel)
            except BundlePathError:
                self.send_error(404, "Bundle file not found")
                return
            data = file_path.read_bytes()
            self._send_bytes(data, "text/markdown; charset=utf-8")
            return
        super().do_GET()

    def _send_bytes(self, data: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def end_headers(self) -> None:
        self.send_header("Origin-Agent-Cluster", "?1")
        self.send_header("Permissions-Policy", "tools=(self)")
        super().end_headers()

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        super().log_message(format, *args)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8089, help="Port (default 8089)")
    parser.add_argument(
        "--bundle",
        default=str(DEFAULT_BUNDLE),
        help="OKF bundle directory (default niaid_blueprint)",
    )
    args = parser.parse_args()

    bundle_root = Path(args.bundle).resolve()
    payload = build_payload(bundle_root)
    stats = payload["stats"]
    index_bytes = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
    tree_bytes = json.dumps(payload["tree"], indent=2, ensure_ascii=False).encode("utf-8")

    def handler(*h_args, **h_kwargs):
        return OkfHandler(
            *h_args,
            payload=payload,
            bundle_root=bundle_root,
            index_bytes=index_bytes,
            tree_bytes=tree_bytes,
            **h_kwargs,
        )

    httpd = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Serving {ROOT} at http://{args.host}:{args.port}/")
    print(f"Bundle: {bundle_root} ({stats['concepts']} concepts, {stats['atomics']} atomics)")
    print("Origin-Agent-Cluster: ?1")
    print("Permissions-Policy: tools=(self)")
    print("Chrome: enable chrome://flags/#enable-webmcp-testing and load 127.0.0.1, not a LAN IP.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
