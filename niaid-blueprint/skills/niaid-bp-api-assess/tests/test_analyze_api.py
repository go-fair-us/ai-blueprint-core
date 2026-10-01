"""Tests for niaid-bp-api-assess scripts/analyze_api.py."""

from __future__ import annotations

import json
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_DIR / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(SCRIPTS))

yaml = pytest.importorskip("yaml")

from analyze_api import (  # noqa: E402
    FetchResult,
    analyze,
    main,
    select_sample_urls,
)

ALIGNED = FIXTURES / "openapi3-aligned.yaml"
RPC = FIXTURES / "swagger2-rpc.json"
DOCS_LINK = FIXTURES / "docs-with-spec-link.html"
DOCS_PROSE = FIXTURES / "docs-prose-only.html"


def _check(findings: dict, check_id: str) -> dict:
    matches = [row for row in findings["checks"] if row["id"] == check_id]
    assert len(matches) == 1, check_id
    return matches[0]


def _statuses(findings: dict, axis: str) -> dict[str, str]:
    return {row["id"]: row["status"] for row in findings["checks"] if row["axis"] == axis}


def test_aligned_openapi_passes_blueprint_and_practice() -> None:
    findings = analyze(str(ALIGNED), no_sample=True)

    assert findings["confidence"] == "high"
    assert findings["spec"]["format"] == "openapi-3.0.3"
    assert findings["input"]["kind"] == "openapi"
    assert findings["samples"] == []
    assert _statuses(findings, "blueprint") == {
        "bp_openapi_doc": "pass",
        "bp_jsonld_declared": "pass",
        "bp_jsonld_observed": "not_stated",
        "bp_resource_iris": "pass",
        "bp_get_retrieval": "pass",
        "bp_version_in_path": "pass",
    }
    assert _statuses(findings, "practice") == {
        "prac_info_contact": "pass",
        "prac_info_license": "pass",
        "prac_operation_summaries": "pass",
        "prac_operation_ids": "pass",
        "prac_response_examples": "pass",
        "prac_error_responses": "pass",
        "prac_pagination": "pass",
        "prac_local_refs": "pass",
    }
    assert "name" in findings["observed_property_names"]
    assert "license" not in findings["observed_property_names"]
    assert [item["url"] for item in findings["sample_plan"]] == [
        "https://example.org/datasets",
        "https://example.org/datasets/SDY998",
    ]


def test_swagger_rpc_fails_iri_method_and_jsonld() -> None:
    findings = analyze(str(RPC), no_sample=True)

    assert findings["spec"]["format"] == "swagger-2.0"
    assert _check(findings, "bp_openapi_doc")["status"] == "pass"
    assert _check(findings, "bp_jsonld_declared")["status"] == "fail"
    assert _check(findings, "bp_jsonld_declared")["priority"] == "High"
    iris = _check(findings, "bp_resource_iris")
    assert iris["status"] == "fail"
    assert iris["priority"] == "Medium"
    assert {item["path"] for item in iris["evidence"]} >= {"/getDataset", "/search"}
    retrieval = _check(findings, "bp_get_retrieval")
    assert retrieval["status"] == "fail"
    assert retrieval["evidence"][0]["path"] == "/search"
    assert findings["samples"] == []
    assert findings["confidence"] == "high"


def test_docs_page_follows_one_spec_link() -> None:
    findings = analyze(str(DOCS_LINK), no_sample=True)

    hop = findings["input"]["hop"]
    assert hop is not None
    assert hop["to"].endswith("openapi3-aligned.yaml")
    assert "error" not in hop
    assert findings["input"]["kind"] == "openapi"
    assert _check(findings, "bp_openapi_doc")["status"] == "pass"
    assert _check(findings, "bp_jsonld_declared")["status"] == "pass"
    assert findings["confidence"] == "high"


def test_spec_link_wins_over_an_earlier_swagger_ui_link() -> None:
    page = FIXTURES / "docs-ui-before-spec.html"
    findings = analyze(str(page), no_sample=True)

    hop = findings["input"]["hop"]
    assert hop["to"].endswith("openapi3-aligned.yaml")
    assert "error" not in hop
    assert all("swaggerUI" not in step for step in hop["via"])
    assert _check(findings, "bp_openapi_doc")["status"] == "pass"


def test_swagger_ui_chain_reaches_extensionless_spec() -> None:
    page = FIXTURES / "ui-chain" / "docs.html"

    def fetcher(url: str) -> FetchResult:
        raise AssertionError(f"discovery followed {url}")

    findings = analyze(str(page), no_sample=True, fetcher=fetcher)

    hop = findings["input"]["hop"]
    assert hop["to"].endswith(f"{Path('ui-chain') / 'api-docs'}")
    assert "error" not in hop
    joined = " ".join(hop["via"])
    assert "swagger-initializer.js" in joined
    assert "swagger-config.json" in joined
    assert "petstore.swagger.io" not in joined
    assert findings["spec"]["format"] == "openapi-3.0.1"
    assert findings["spec"]["title"] == "Shared Data API"


def test_prose_only_docs_stay_not_stated() -> None:
    findings = analyze(str(DOCS_PROSE), no_sample=True)

    assert findings["input"]["kind"] == "docs"
    assert findings["input"]["hop"] is None
    assert findings["confidence"] == "low"
    assert findings["operations"] == []
    assert _check(findings, "bp_openapi_doc")["status"] == "fail"
    assert _check(findings, "bp_openapi_doc")["priority"] == "Medium"
    assert _check(findings, "bp_jsonld_declared")["status"] == "not_stated"
    assert _check(findings, "bp_resource_iris")["status"] == "not_stated"
    assert _check(findings, "bp_get_retrieval")["status"] == "not_stated"
    assert all(row["status"] == "not_stated" for row in findings["checks"] if row["axis"] == "practice")


def test_select_sample_urls_skips_secured_and_unfilled_params() -> None:
    operations = [
        {
            "method": "GET",
            "path": "/private",
            "secured": True,
            "sample_url": "https://example.org/private",
            "operation_id": "private",
        },
        {
            "method": "GET",
            "path": "/datasets/{dataset_id}",
            "secured": False,
            "sample_url": None,
            "operation_id": "missingExample",
        },
        {
            "method": "POST",
            "path": "/datasets",
            "secured": False,
            "sample_url": "https://example.org/datasets",
            "operation_id": "create",
        },
        {
            "method": "GET",
            "path": "/datasets/{dataset_id}",
            "secured": False,
            "sample_url": "https://example.org/datasets/SDY998",
            "operation_id": "getDataset",
        },
        {
            "method": "GET",
            "path": "/studies/{study_id}",
            "secured": False,
            "sample_url": "https://example.org/studies/1",
            "operation_id": "getStudy",
        },
    ]

    chosen = select_sample_urls(operations, limit=1)

    assert [item["url"] for item in chosen] == ["https://example.org/datasets/SDY998"]


def test_no_sample_opens_no_sockets(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError(f"unexpected outbound connection: {args!r} {kwargs!r}")

    monkeypatch.setattr(socket, "create_connection", refuse)
    findings = analyze(str(ALIGNED), no_sample=True)
    assert findings["samples"] == []
    assert findings["sample_plan"]


def test_refuses_non_http_scheme() -> None:
    with pytest.raises(ValueError, match="non-http"):
        analyze("file:///etc/passwd")


def test_url_input_uses_fetcher_once_when_sampling_is_off() -> None:
    calls: list[str] = []

    def fetcher(url: str) -> FetchResult:
        calls.append(url)
        return FetchResult(200, "application/yaml", ALIGNED.read_bytes(), url)

    findings = analyze("https://example.org/openapi.yaml", no_sample=True, fetcher=fetcher)

    assert calls == ["https://example.org/openapi.yaml"]
    assert findings["spec"]["format"] == "openapi-3.0.3"
    assert _check(findings, "bp_jsonld_declared")["status"] == "pass"


def test_remote_ref_is_not_fetched(tmp_path: Path) -> None:
    calls: list[str] = []

    def fetcher(url: str) -> FetchResult:
        calls.append(url)
        return FetchResult(200, "application/json", b'{"name":"x"}', url)

    spec = {
        "openapi": "3.0.3",
        "info": {"title": "Remote", "version": "1"},
        "servers": [{"url": "https://example.org"}],
        "paths": {
            "/datasets/{dataset_id}": {
                "get": {
                    "operationId": "getDataset",
                    "summary": "Fetch one dataset",
                    "parameters": [
                        {
                            "name": "dataset_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string", "example": "SDY998"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "one",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "https://example.org/schemas/dataset.json"}
                                }
                            },
                        }
                    },
                }
            }
        },
    }
    path = tmp_path / "remote.yaml"
    path.write_text(yaml.safe_dump(spec), encoding="utf-8")
    findings = analyze(str(path), sample=3, fetcher=fetcher)

    assert calls == ["https://example.org/datasets/SDY998"]
    assert findings["unresolved_refs"] == ["https://example.org/schemas/dataset.json"]
    assert _check(findings, "prac_local_refs")["status"] == "fail"


def test_empty_response_schemas_are_medium_confidence(tmp_path: Path) -> None:
    spec = """
openapi: 3.0.3
info:
  title: Empty schemas
  version: "1"
servers:
  - url: https://example.org
paths:
  /datasets/{dataset_id}:
    get:
      operationId: getDataset
      summary: Fetch one dataset
      responses:
        "200":
          description: ok
"""
    path = tmp_path / "empty.yaml"
    path.write_text(spec, encoding="utf-8")
    findings = analyze(str(path), no_sample=True)
    assert findings["confidence"] == "medium"
    assert _check(findings, "bp_jsonld_declared")["status"] == "not_stated"


def test_failed_samples_lower_confidence(tmp_path: Path) -> None:
    spec = """
openapi: 3.0.3
info:
  title: Sample target
  version: "1"
  contact:
    name: Team
  license:
    name: CC0-1.0
servers:
  - url: https://example.org
paths:
  /datasets:
    get:
      operationId: listDatasets
      summary: List datasets
      responses:
        "200":
          description: list
          content:
            application/json:
              schema:
                type: object
                properties:
                  name:
                    type: string
"""
    path = tmp_path / "sample.yaml"
    path.write_text(spec, encoding="utf-8")

    def fetcher(url: str) -> FetchResult:
        return FetchResult(None, "", b"", url, error="timed out")

    findings = analyze(str(path), sample=1, fetcher=fetcher)
    assert findings["confidence"] == "medium"
    assert _check(findings, "bp_jsonld_observed")["status"] == "not_stated"
    assert findings["samples"][0]["error"] == "timed out"


def test_local_schema_ref_counts_as_jsonld(tmp_path: Path) -> None:
    spec = """
openapi: 3.0.3
info:
  title: Ref
  version: "1"
  contact:
    name: Team
  license:
    name: CC0-1.0
servers:
  - url: https://example.org
paths:
  /datasets/{dataset_id}:
    get:
      operationId: getDataset
      summary: Fetch one dataset
      parameters:
        - name: dataset_id
          in: path
          required: true
          schema:
            type: string
            example: SDY998
      responses:
        "200":
          description: one
          content:
            application/ld+json:
              schema:
                $ref: "#/components/schemas/Dataset"
        "404":
          description: missing
components:
  schemas:
    Dataset:
      type: object
      properties:
        "@context":
          type: string
        name:
          type: string
      example:
        "@context": "https://schema.org/"
        name: Example
"""
    path = tmp_path / "ref.yaml"
    path.write_text(spec, encoding="utf-8")
    findings = analyze(str(path), no_sample=True)
    assert _check(findings, "bp_jsonld_declared")["status"] == "pass"
    assert "name" in findings["observed_property_names"]
    assert _check(findings, "prac_pagination")["status"] == "not_applicable"


class _SampleHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/datasets/ld"):
            body = b'{"@context":"https://schema.org/","name":"linked"}'
            content_type = "application/ld+json"
        else:
            body = b'{"name":"plain"}'
            content_type = "application/json"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        return


def _serve() -> tuple[ThreadingHTTPServer, int]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _SampleHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", port), 0.2):
                break
        except OSError:
            continue
    return server, port


def _spec_for(port: int, paths: dict) -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Local",
            "version": "1",
            "contact": {"name": "Team"},
            "license": {"name": "CC0-1.0"},
        },
        "servers": [{"url": f"http://127.0.0.1:{port}"}],
        "paths": paths,
    }


def test_samples_record_jsonld_and_plain_json(tmp_path: Path) -> None:
    server, port = _serve()
    spec = _spec_for(
        port,
        {
            "/datasets/ld": {
                "get": {
                    "operationId": "linked",
                    "summary": "Linked dataset",
                    "responses": {"200": {"description": "ok"}, "404": {"description": "missing"}},
                }
            },
            "/datasets/plain": {
                "get": {
                    "operationId": "plain",
                    "summary": "Plain dataset",
                    "responses": {"200": {"description": "ok"}, "404": {"description": "missing"}},
                }
            },
        },
    )
    path = tmp_path / "live.yaml"
    path.write_text(yaml.safe_dump(spec), encoding="utf-8")
    try:
        findings = analyze(str(path), sample=3)
    finally:
        server.shutdown()
        server.server_close()

    observed = _check(findings, "bp_jsonld_observed")
    assert observed["status"] == "pass"
    by_url = {sample["url"]: sample for sample in findings["samples"]}
    assert by_url[f"http://127.0.0.1:{port}/datasets/ld"]["jsonld"] is True
    assert by_url[f"http://127.0.0.1:{port}/datasets/plain"]["jsonld"] is False
    assert "name" in findings["observed_property_names"]


def test_plain_json_sample_fails_observed_jsonld(tmp_path: Path) -> None:
    server, port = _serve()
    spec = _spec_for(
        port,
        {
            "/datasets/plain": {
                "get": {
                    "operationId": "plain",
                    "summary": "Plain dataset",
                    "parameters": [{"name": "limit", "in": "query", "schema": {"type": "integer"}}],
                    "responses": {
                        "200": {"description": "ok"},
                        "404": {"description": "missing"},
                    },
                }
            }
        },
    )
    path = tmp_path / "plain.yaml"
    path.write_text(yaml.safe_dump(spec), encoding="utf-8")
    try:
        findings = analyze(str(path), sample=1)
    finally:
        server.shutdown()
        server.server_close()

    assert _check(findings, "bp_jsonld_observed")["status"] == "fail"
    assert _check(findings, "bp_jsonld_observed")["priority"] == "High"
    assert findings["samples"][0]["json"] is True
    assert findings["samples"][0]["jsonld"] is False


def test_main_writes_findings(tmp_path: Path) -> None:
    code = main([str(ALIGNED), "--no-sample", "--out-dir", str(tmp_path)])
    assert code == 0
    written = json.loads((tmp_path / "findings.json").read_text(encoding="utf-8"))
    assert written["confidence"] == "high"
