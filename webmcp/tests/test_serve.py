from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse

import pytest

from serve import HandbookHandler


@pytest.fixture
def http_server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), HandbookHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address
    yield f"http://{host}:{port}"
    httpd.shutdown()
    thread.join(timeout=2)


def _request(base: str, path: str, method: str = "GET", body: bytes | None = None, content_type: str | None = None) -> tuple[int, dict[str, str], bytes]:
    parsed = urlparse(base)
    conn = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=5)
    try:
        headers = {}
        if content_type:
            headers["Content-Type"] = content_type
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        data = resp.read()
        headers_out = {k.lower(): v for k, v in resp.getheaders()}
        return resp.status, headers_out, data
    finally:
        conn.close()


def test_home_and_webmcp_headers(http_server: str):
    status, headers, body = _request(http_server, "/")
    assert status == 200
    assert headers.get("origin-agent-cluster") == "?1"
    assert "tools=(self)" in headers.get("permissions-policy", "")
    html = body.decode("utf-8")
    assert "NIAID Blueprint handbook" in html
    assert "/chatbp.html" in html


def test_chat_page_is_not_a_tester(http_server: str):
    status, _, body = _request(http_server, "/chatbp.html")
    assert status == 200
    html = body.decode("utf-8")
    assert 'id="chat-form"' in html
    assert 'id="chat-log"' in html
    assert "webmcp-tester" not in html
    assert "Ask the Blueprint" in html


def test_status_reports_narrative_flag(http_server: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    status, _, body = _request(http_server, "/api/status")
    assert status == 200
    payload = json.loads(body)
    assert payload["narrative"] is False
    assert payload["model"]


def test_narrative_without_key_is_503(http_server: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    status, _, body = _request(
        http_server,
        "/api/narrative",
        method="POST",
        body=json.dumps({"question": "What is a DOI?", "passages": []}).encode(),
        content_type="application/json",
    )
    assert status == 503
    payload = json.loads(body)
    assert payload["configured"] is False


def test_narrative_requires_question(http_server: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    status, _, body = _request(
        http_server,
        "/api/narrative",
        method="POST",
        body=json.dumps({"passages": []}).encode(),
        content_type="application/json",
    )
    assert status == 400
    assert "question" in json.loads(body)["error"].lower()


def test_narrative_proxies_xai(http_server: str, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("XAI_API_KEY", "test-key")

    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(
                {
                    "output": [
                        {
                            "type": "message",
                            "content": [{"type": "output_text", "text": "Use a resolvable DOI."}],
                        }
                    ]
                }
            ).encode()

    def fake_urlopen(req, timeout=0):
        assert "api.x.ai/v1/responses" in req.full_url
        assert req.get_header("Authorization") == "Bearer test-key"
        payload = json.loads(req.data.decode())
        assert payload["store"] is False
        assert payload["model"]
        return FakeResp()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    status, _, body = _request(
        http_server,
        "/api/narrative",
        method="POST",
        body=json.dumps(
            {
                "question": "What identifier should an object have?",
                "passages": [
                    {
                        "slug": "persistent-identifiers",
                        "title": "Persistent identifiers",
                        "href": "/topics/persistent-identifiers.html",
                        "excerpt": "The Blueprint defaults to a resolvable DOI.",
                    }
                ],
            }
        ).encode(),
        content_type="application/json",
    )
    assert status == 200
    payload = json.loads(body)
    assert payload["text"] == "Use a resolvable DOI."
