from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import pytest

from index_builder import DEFAULT_BUNDLE, build_payload
from serve import OkfHandler

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "mini_bundle"


@pytest.fixture
def http_server():
    payload = build_payload(FIXTURE)
    index_bytes = json.dumps(payload).encode("utf-8")
    tree_bytes = json.dumps(payload["tree"]).encode("utf-8")

    def handler(*args, **kwargs):
        return OkfHandler(
            *args,
            payload=payload,
            bundle_root=FIXTURE,
            index_bytes=index_bytes,
            tree_bytes=tree_bytes,
            **kwargs,
        )

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address
    yield f"http://{host}:{port}"
    httpd.shutdown()
    thread.join(timeout=2)


def _request(base: str, path: str) -> tuple[int, dict[str, str], bytes]:
    parsed = urlparse(base)
    conn = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=5)
    try:
        conn.request("GET", path)
        resp = conn.getresponse()
        body = resp.read()
        headers = {k.lower(): v for k, v in resp.getheaders()}
        return resp.status, headers, body
    finally:
        conn.close()


def test_index_and_bundle_routes(http_server: str):
    status, headers, body = _request(http_server, "/data/index.json")
    assert status == 200
    assert headers.get("origin-agent-cluster") == "?1"
    assert "tools=(self)" in headers.get("permissions-policy", "")
    payload = json.loads(body)
    assert payload["stats"]["concepts"] == 2
    status, _, raw = _request(http_server, "/bundle/concepts/alpha.md")
    assert status == 200
    assert b"Resolvable DOI" in raw
    status, _, tree_body = _request(http_server, "/data/tree.json")
    assert status == 200
    tree = json.loads(tree_body)
    assert tree["kind"] == "dir"


def test_bundle_escape_is_404(http_server: str):
    status, _, _ = _request(http_server, "/bundle/../index.md")
    assert status == 404


def test_home_page(http_server: str):
    status, _, html_b = _request(http_server, "/")
    assert status == 200
    html = html_b.decode("utf-8")
    assert "NIAID Blueprint OKF" in html
    assert "/js/bundle.js" in html


def test_real_bundle_payload_optional():
    if not DEFAULT_BUNDLE.is_dir():
        pytest.skip("niaid_blueprint missing")
    payload = build_payload(DEFAULT_BUNDLE)
    assert payload["stats"]["atomics"] == 239
