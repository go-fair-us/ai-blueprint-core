#!/usr/bin/env python3
"""Analyze an OpenAPI/Swagger document or an API docs page.

Scores NIAID Blueprint Section 3 (JSON-LD, resource IRIs, GET, OpenAPI) on
its own axis, plus a short REST lint that is not a Blueprint failure.
Check ids and priorities match ``references/api-checklist.md``.

Optional unauthenticated GET samples record whether a response body is
JSON-LD. Remote ``$ref`` links are reported and not fetched. Redirects
that leave the original host are refused.

Usage::

    python scripts/analyze_api.py INPUT [--sample 3] [--no-sample] [--out-dir DIR]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only without deps
    raise SystemExit(
        "PyYAML is required. It is a base dependency of this repository:\n"
        "  uv sync\n"
        f"Original error: {exc}"
    ) from exc


USER_AGENT = "niaid-bp-api-assess/0.1"
MAX_BYTES = 1_000_000
TIMEOUT_S = 15.0
MAX_REDIRECTS = 3

HTTP_METHODS = {"get", "post", "put", "delete", "patch", "head", "options", "trace"}

# Path segments that are RPC verbs rather than resources. CamelCase
# ``getDataset`` counts; plain nouns such as ``datasets`` do not.
_VERBS = (
    "get",
    "post",
    "put",
    "delete",
    "patch",
    "list",
    "search",
    "query",
    "find",
    "fetch",
    "create",
    "update",
    "add",
    "remove",
    "retrieve",
    "lookup",
    "set",
    "read",
)
_RETRIEVAL = (
    "get",
    "search",
    "query",
    "find",
    "fetch",
    "retrieve",
    "list",
    "lookup",
    "read",
)
_VERSION_SEGMENT = re.compile(r"^v\d+(?:\.\d+)?$", re.I)
_ID_QUERY = re.compile(r"^(?:id|identifier|accession|doi)$|(?:_id|Id)$")
_PAGE_PARAMS = {
    "limit",
    "offset",
    "page",
    "pagesize",
    "page_size",
    "per_page",
    "perpage",
    "cursor",
    "skip",
    "start",
    "count",
}
_ENDPOINT_RE = re.compile(
    r"\b(GET|POST|PUT|DELETE|PATCH)\s+(/[A-Za-z0-9_./{}~+-]+)"
)
_EXAMPLE_GET_RE = re.compile(
    r"\b(?:GET|curl(?:\s+-X\s+GET)?)\s+(https?://[^\s\"'<>]+)",
    re.I,
)
_JSONLD_RE = re.compile(r"application/ld\+json|json-?ld", re.I)
_OUTSIDE = (
    ("graphql", re.compile(r"\bgraphql\b", re.I)),
    ("sparql", re.compile(r"\bsparql\b", re.I)),
    ("fhir", re.compile(r"\bfhir\b", re.I)),
)

Fetcher = Callable[[str], "FetchResult"]


class FetchResult:
    """One HTTP GET, including transport failures."""

    def __init__(
        self,
        status: int | None,
        content_type: str,
        body: bytes,
        url: str,
        error: str | None = None,
        truncated: bool = False,
    ) -> None:
        self.status = status
        self.content_type = content_type
        self.body = body
        self.url = url
        self.error = error
        self.truncated = truncated


class _SameHostRedirect(urllib.request.HTTPRedirectHandler):
    """Follow a few redirects only while the host stays the same.

    A docs page or spec server that redirects onto another host would
    otherwise turn a metadata sample into a request the user did not name.
    """

    max_redirs = MAX_REDIRECTS

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        ensure_http_url(newurl)
        old = (urllib.parse.urlparse(req.full_url).hostname or "").lower()
        new = (urllib.parse.urlparse(newurl).hostname or "").lower()
        if old != new:
            raise ValueError(f"refusing cross-host redirect from {old} to {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def ensure_http_url(url: str) -> urllib.parse.ParseResult:
    """Reject non-http schemes and URLs that embed credentials."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"refusing non-http URL: {url}")
    if parsed.username or parsed.password:
        raise ValueError(f"refusing URL with credentials: {parsed.scheme}://{parsed.hostname}")
    if not parsed.hostname:
        raise ValueError(f"refusing URL without a host: {url}")
    return parsed


def default_fetcher(url: str) -> FetchResult:
    """GET ``url`` with a size cap. No Authorization header and no cookies."""
    ensure_http_url(url)
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/ld+json, application/json;q=0.9, */*;q=0.1",
        },
    )
    opener = urllib.request.build_opener(_SameHostRedirect)
    try:
        response = opener.open(request, timeout=TIMEOUT_S)
    except urllib.error.HTTPError as exc:
        response = exc
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        return FetchResult(None, "", b"", url, error=str(exc))
    try:
        raw = response.read(MAX_BYTES + 1)
        content_type = response.headers.get("Content-Type", "")
        final = response.geturl()
        status = getattr(response, "status", None) or response.getcode()
    finally:
        response.close()
    truncated = len(raw) > MAX_BYTES
    return FetchResult(status, content_type, raw[:MAX_BYTES], final or url, truncated=truncated)


def _check(
    check_id: str,
    axis: str,
    status: str,
    evidence: list[dict[str, Any]],
    priority: str | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": check_id,
        "axis": axis,
        "status": status,
        "evidence": evidence,
    }
    if axis == "blueprint":
        row["priority"] = priority
    return row


def _detail(text: str) -> str:
    return " ".join(text.split())[:240]


def parse_spec(text: str) -> dict[str, Any] | None:
    """Return an OpenAPI or Swagger mapping, or None when ``text`` is prose."""
    stripped = text.lstrip("\ufeff").lstrip()
    if not stripped or stripped.startswith("<"):
        return None
    data: Any = None
    if stripped[0] in "{[":
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError:
            return None
    else:
        try:
            data = yaml.safe_load(stripped)
        except yaml.YAMLError:
            return None
    if isinstance(data, dict) and (
        isinstance(data.get("openapi"), str) or isinstance(data.get("swagger"), str)
    ):
        return data
    return None


def resolve_pointer(root: dict[str, Any], ref: str) -> Any:
    """Resolve a local JSON pointer (``#/components/schemas/Dataset``)."""
    if not ref.startswith("#/"):
        raise ValueError(ref)
    current: Any = root
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return current


def deref(root: dict[str, Any], node: Any, seen: set[str] | None = None) -> Any:
    """Follow local ``$ref`` links. Remote refs are left unresolved."""
    if not isinstance(node, dict):
        return node
    ref = node.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return node
    seen = seen or set()
    if ref in seen:
        return {}
    try:
        target = resolve_pointer(root, ref)
    except (KeyError, IndexError, TypeError, ValueError):
        return {}
    if isinstance(target, dict):
        return deref(root, target, seen | {ref})
    return target


def collect_remote_refs(node: Any, found: list[str] | None = None) -> list[str]:
    """Collect ``$ref`` values that are not local JSON pointers."""
    found = found if found is not None else []
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and not ref.startswith("#"):
            found.append(ref)
        for value in node.values():
            collect_remote_refs(value, found)
    elif isinstance(node, list):
        for value in node:
            collect_remote_refs(value, found)
    return found


def _is_verb_segment(segment: str, verbs: tuple[str, ...] = _VERBS) -> bool:
    if not segment or segment.startswith("{"):
        return False
    low = segment.lower()
    if low in verbs:
        return True
    for verb in verbs:
        if (
            low.startswith(verb)
            and len(segment) > len(verb)
            and (segment[len(verb)].isupper() or segment[len(verb)] == "_")
        ):
            return True
    return False


def _version_segments(path: str) -> list[str]:
    source = urllib.parse.urlparse(path).path if "://" in path else path
    return [part for part in source.split("/") if _VERSION_SEGMENT.match(part)]


def expand_server(server: dict[str, Any]) -> str | None:
    url = str(server.get("url") or "")
    variables = server.get("variables") or {}

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        spec = variables.get(name) or {}
        if not isinstance(spec, dict) or spec.get("default") is None:
            raise KeyError(name)
        return str(spec["default"])

    try:
        return re.sub(r"\{([^{}]+)\}", replace, url)
    except KeyError:
        return None


def server_urls(spec: dict[str, Any], origin: str) -> list[str]:
    """Absolute server URLs samples are allowed to call."""
    urls: list[str] = []
    if isinstance(spec.get("openapi"), str):
        for server in spec.get("servers") or []:
            expanded = expand_server(server) if isinstance(server, dict) else None
            if not expanded:
                continue
            if expanded.startswith("/") and origin.startswith(("http://", "https://")):
                expanded = urllib.parse.urljoin(origin, expanded)
            if expanded.startswith(("http://", "https://")):
                urls.append(expanded.rstrip("/"))
        if not urls and origin.startswith(("http://", "https://")):
            parsed = urllib.parse.urlparse(origin)
            urls.append(f"{parsed.scheme}://{parsed.netloc}")
        return urls

    host = spec.get("host")
    if not host and origin.startswith(("http://", "https://")):
        host = urllib.parse.urlparse(origin).netloc
    if not host:
        return []
    schemes = spec.get("schemes") or ["https"]
    scheme = "https" if "https" in schemes else str(schemes[0])
    base = str(spec.get("basePath") or "")
    if base and not base.startswith("/"):
        base = "/" + base
    return [f"{scheme}://{host}{base}".rstrip("/")]


def _param_example(param: dict[str, Any], root: dict[str, Any]) -> Any:
    param = deref(root, param)
    if not isinstance(param, dict):
        return None
    for key in ("example", "x-example"):
        value = param.get(key)
        if value is not None and not isinstance(value, (dict, list)):
            return value
    schema = deref(root, param.get("schema") or {})
    if isinstance(schema, dict):
        for key in ("example", "default"):
            value = schema.get(key)
            if value is not None and not isinstance(value, (dict, list)):
                return value
    if "default" in param and param.get("in") != "body" and not isinstance(param["default"], (dict, list)):
        return param["default"]
    examples = param.get("examples")
    if isinstance(examples, dict):
        for example in examples.values():
            example = deref(root, example) if isinstance(example, dict) else example
            if isinstance(example, dict) and "value" in example and not isinstance(example["value"], (dict, list)):
                return example["value"]
    return None


def _merged_parameters(path_item: dict[str, Any], operation: dict[str, Any]) -> list[dict[str, Any]]:
    merged: dict[tuple[Any, Any], dict[str, Any]] = {}
    for param in path_item.get("parameters") or []:
        if isinstance(param, dict):
            merged[(param.get("name"), param.get("in"))] = param
    for param in operation.get("parameters") or []:
        if isinstance(param, dict):
            merged[(param.get("name"), param.get("in"))] = param
    return list(merged.values())


def _fill_path(path: str, params: list[dict[str, Any]], root: dict[str, Any]) -> str | None:
    names = re.findall(r"\{([^{}]+)\}", path)
    if not names:
        return path
    by_name: dict[str, dict[str, Any]] = {}
    for param in params:
        resolved = deref(root, param)
        if isinstance(resolved, dict) and resolved.get("in") == "path":
            by_name[str(resolved.get("name"))] = resolved
    filled = path
    for name in names:
        example = _param_example(by_name.get(name.rstrip("*")) or {}, root)
        if example is None:
            return None
        filled = filled.replace("{" + name + "}", urllib.parse.quote(str(example), safe=""))
    return filled


def _media_types(response: dict[str, Any], produces: list[str]) -> list[str]:
    content = response.get("content")
    if isinstance(content, dict) and content:
        return [str(key) for key in content.keys()]
    return list(produces)


def _has_schema(response: dict[str, Any], root: dict[str, Any]) -> bool:
    if isinstance(response.get("schema"), dict):
        return True
    content = response.get("content")
    if isinstance(content, dict):
        for media in content.values():
            media = deref(root, media) if isinstance(media, dict) else {}
            if isinstance(media, dict) and isinstance(media.get("schema"), dict):
                return True
    return False


def _has_example(response: dict[str, Any], root: dict[str, Any]) -> bool:
    if "example" in response:
        return True
    if isinstance(response.get("examples"), dict) and response["examples"]:
        return True
    schema = deref(root, response.get("schema") or {})
    if isinstance(schema, dict) and "example" in schema:
        return True
    content = response.get("content")
    if isinstance(content, dict):
        for media in content.values():
            media = deref(root, media) if isinstance(media, dict) else {}
            if not isinstance(media, dict):
                continue
            if "example" in media or (isinstance(media.get("examples"), dict) and media["examples"]):
                return True
            media_schema = deref(root, media.get("schema") or {})
            if isinstance(media_schema, dict) and "example" in media_schema:
                return True
    return False


def _declares_context(node: Any, root: dict[str, Any], depth: int = 0, seen: set[int] | None = None) -> bool:
    if depth > 12:
        return False
    node = deref(root, node)
    if not isinstance(node, dict):
        return False
    seen = seen or set()
    marker = id(node)
    if marker in seen:
        return False
    seen.add(marker)
    if "@context" in node:
        return True
    props = node.get("properties")
    if isinstance(props, dict) and "@context" in props:
        return True
    example = node.get("example")
    if isinstance(example, dict) and "@context" in example:
        return True
    if isinstance(example, list) and any(isinstance(item, dict) and "@context" in item for item in example):
        return True
    value = node.get("value")
    if isinstance(value, dict) and "@context" in value:
        return True
    examples = node.get("examples")
    if isinstance(examples, dict):
        for item in examples.values():
            if _declares_context(item, root, depth + 1, seen):
                return True
    for key in ("allOf", "oneOf", "anyOf"):
        for sub in node.get(key) or []:
            if _declares_context(sub, root, depth + 1, seen):
                return True
    items = node.get("items")
    if isinstance(items, dict) and _declares_context(items, root, depth + 1, seen):
        return True
    content = node.get("content")
    if isinstance(content, dict):
        for media in content.values():
            if _declares_context(media, root, depth + 1, seen):
                return True
    schema = node.get("schema")
    if isinstance(schema, dict) and _declares_context(schema, root, depth + 1, seen):
        return True
    return False


def _collect_property_names(
    node: Any,
    root: dict[str, Any],
    found: set[str],
    depth: int = 0,
    seen: set[int] | None = None,
) -> None:
    """Record schema property names and example object keys. Does not invent fields."""
    if depth > 16:
        return
    seen = seen or set()
    if isinstance(node, list):
        for item in node:
            _collect_property_names(item, root, found, depth + 1, seen)
        return
    if not isinstance(node, dict):
        return
    marker = id(node)
    if marker in seen:
        return
    seen.add(marker)
    node = deref(root, node)
    if not isinstance(node, dict):
        return
    props = node.get("properties")
    if isinstance(props, dict):
        found.update(str(key) for key in props.keys())
    for key in ("example", "value"):
        example = node.get(key)
        if isinstance(example, dict):
            found.update(str(name) for name in example.keys())
    for value in node.values():
        if isinstance(value, (dict, list)):
            _collect_property_names(value, root, found, depth + 1, seen)


def _operation_secured(operation: dict[str, Any], global_security: Any) -> bool:
    if "security" in operation:
        return bool(operation.get("security"))
    return bool(global_security)


def _produces(spec: dict[str, Any], operation: dict[str, Any]) -> list[str]:
    declared = operation.get("produces")
    if not declared:
        declared = spec.get("produces") or []
    return [str(item) for item in declared]


def extract_operations(spec: dict[str, Any], origin: str) -> list[dict[str, Any]]:
    """Normalize path operations. ``sample_url`` is set only when a GET needs no invented ids."""
    servers = server_urls(spec, origin)
    server = servers[0] if servers else None
    global_security = spec.get("security")
    operations: list[dict[str, Any]] = []
    paths = spec.get("paths") or {}
    if not isinstance(paths, dict):
        return operations
    for path, path_item in paths.items():
        path_item = deref(spec, path_item)
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            operation = deref(spec, operation)
            if not isinstance(operation, dict):
                continue
            params = _merged_parameters(path_item, operation)
            resolved_params = []
            for param in params:
                resolved = deref(spec, param)
                if isinstance(resolved, dict):
                    resolved_params.append(resolved)
            has_body = "requestBody" in operation or any(
                param.get("in") in {"body", "formData"} for param in resolved_params
            )
            responses: list[dict[str, Any]] = []
            raw_responses = operation.get("responses") or {}
            produces = _produces(spec, operation)
            if isinstance(raw_responses, dict):
                for code, response in raw_responses.items():
                    response = deref(spec, response)
                    if not isinstance(response, dict):
                        continue
                    responses.append(
                        {
                            "status": str(code),
                            "media_types": _media_types(response, produces if str(code).startswith("2") else []),
                            "has_example": _has_example(response, spec),
                            "declares_context": _declares_context(response, spec),
                            "has_schema": _has_schema(response, spec),
                        }
                    )
            filled = _fill_path(str(path), resolved_params, spec)
            sample_url = None
            if (
                method.lower() == "get"
                and server
                and filled is not None
                and not _operation_secured(operation, global_security)
            ):
                sample_url = server.rstrip("/") + "/" + filled.lstrip("/")
            operations.append(
                {
                    "method": method.upper(),
                    "path": str(path),
                    "operation_id": operation.get("operationId") or "",
                    "summary": operation.get("summary") or "",
                    "description": operation.get("description") or "",
                    "parameters": [
                        {
                            "name": param.get("name"),
                            "in": param.get("in"),
                            "required": bool(param.get("required")),
                        }
                        for param in resolved_params
                        if param.get("in") != "body"
                    ],
                    "secured": _operation_secured(operation, global_security),
                    "request_body": has_body,
                    "responses": responses,
                    "sample_url": sample_url,
                    "servers": servers,
                }
            )
    return operations


def select_sample_urls(operations: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    """GETs that need no credentials and no invented path parameters, capped at ``limit``."""
    chosen: list[dict[str, Any]] = []
    if limit <= 0:
        return chosen
    for operation in operations:
        if operation.get("method") != "GET":
            continue
        if operation.get("secured"):
            continue
        url = operation.get("sample_url")
        if not url:
            continue
        try:
            ensure_http_url(url)
        except ValueError:
            continue
        chosen.append(
            {
                "url": url,
                "method": "GET",
                "path": operation.get("path"),
                "operation_id": operation.get("operation_id") or "",
            }
        )
        if len(chosen) >= limit:
            break
    return chosen


def _public_operation(operation: dict[str, Any]) -> dict[str, Any]:
    media: list[str] = []
    for response in operation["responses"]:
        if str(response["status"]).startswith("2"):
            for item in response["media_types"]:
                if item not in media:
                    media.append(item)
    return {
        "method": operation["method"],
        "path": operation["path"],
        "operation_id": operation["operation_id"],
        "media_types": media,
        "secured": operation["secured"],
    }


def _info_present(info: dict[str, Any], field: str, keys: tuple[str, ...]) -> bool:
    block = info.get(field)
    return isinstance(block, dict) and any(block.get(key) for key in keys)


def _schemas_known(operations: list[dict[str, Any]]) -> bool:
    for operation in operations:
        for response in operation["responses"]:
            if response["media_types"] or response["has_schema"]:
                return True
    return False


def _jsonld_declared(operations: list[dict[str, Any]]) -> str:
    saw_encoding = False
    for operation in operations:
        for response in operation["responses"]:
            if response["media_types"] or response["has_schema"] or response["declares_context"]:
                saw_encoding = True
            if response["declares_context"] or any(
                _is_ld_json(media) for media in response["media_types"]
            ):
                return "pass"
    if not operations or not saw_encoding:
        return "not_stated"
    return "fail"


def _is_ld_json(media: str) -> bool:
    return media.split(";", 1)[0].strip().lower() == "application/ld+json"


def _resource_evidence(operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for operation in operations:
        for segment in str(operation["path"]).split("/"):
            if _is_verb_segment(segment):
                evidence.append(
                    {
                        "method": operation["method"],
                        "path": operation["path"],
                        "detail": _detail(f"verb-like path segment '{segment}'"),
                    }
                )
                break
        if operation["method"] != "GET" or re.search(r"\{[^{}]+\}", operation["path"]):
            continue
        for param in operation["parameters"]:
            name = str(param.get("name") or "")
            if param.get("in") == "query" and param.get("required") and _ID_QUERY.search(name):
                evidence.append(
                    {
                        "method": operation["method"],
                        "path": operation["path"],
                        "detail": _detail(
                            f"item identity is required query parameter '{name}' rather than a path IRI"
                        ),
                    }
                )
                break
    return evidence


def _retrieval_post_evidence(operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for operation in operations:
        if operation["method"] != "POST" or operation["request_body"]:
            continue
        signal = None
        for segment in str(operation["path"]).split("/"):
            if _is_verb_segment(segment, _RETRIEVAL):
                signal = segment
                break
        operation_id = operation.get("operation_id") or ""
        if signal is None and _is_verb_segment(operation_id, _RETRIEVAL):
            signal = operation_id
        summary = (operation.get("summary") or "").strip()
        first = summary.split(" ", 1)[0] if summary else ""
        if signal is None and first.lower() in _RETRIEVAL:
            signal = first
        if signal is None:
            continue
        evidence.append(
            {
                "method": "POST",
                "path": operation["path"],
                "detail": _detail(
                    f"retrieval-shaped POST ('{signal}') has no request body; Blueprint allows POST when parameters are in the body"
                ),
            }
        )
    return evidence


def _version_evidence(operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[str] = set()
    for operation in operations:
        places = [operation["path"], *(operation.get("servers") or [])]
        for place in places:
            segments = _version_segments(str(place))
            if not segments:
                continue
            key = f"{operation['path']}|{segments[0]}"
            if key in seen:
                continue
            seen.add(key)
            evidence.append(
                {
                    "method": operation["method"],
                    "path": operation["path"],
                    "detail": _detail(
                        f"version segment '{segments[0]}' in '{place}' — unstable as a JSON-LD @id"
                    ),
                }
            )
    return evidence


def blueprint_checks(
    operations: list[dict[str, Any]],
    *,
    spec_parsed: bool,
    samples: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    checks.append(
        _check(
            "bp_openapi_doc",
            "blueprint",
            "pass" if spec_parsed else "fail",
            [] if spec_parsed else [{"detail": "no OpenAPI or Swagger document was parsed"}],
            None if spec_parsed else "Medium",
        )
    )

    declared = _jsonld_declared(operations) if spec_parsed else "not_stated"
    declared_evidence: list[dict[str, Any]] = []
    if declared == "fail":
        for operation in operations:
            medias: list[str] = []
            for response in operation["responses"]:
                medias.extend(response["media_types"])
            if medias:
                declared_evidence.append(
                    {
                        "method": operation["method"],
                        "path": operation["path"],
                        "detail": _detail("response media types: " + ", ".join(dict.fromkeys(medias))),
                    }
                )
    checks.append(
        _check(
            "bp_jsonld_declared",
            "blueprint",
            declared,
            declared_evidence,
            "High" if declared == "fail" else None,
        )
    )

    observed, observed_evidence = _observed_jsonld(samples)
    checks.append(
        _check(
            "bp_jsonld_observed",
            "blueprint",
            observed,
            observed_evidence,
            "High" if observed == "fail" else None,
        )
    )

    if not spec_parsed or not operations:
        checks.append(_check("bp_resource_iris", "blueprint", "not_stated", [], None))
        checks.append(_check("bp_get_retrieval", "blueprint", "not_stated", [], None))
        checks.append(_check("bp_version_in_path", "blueprint", "not_stated", [], None))
        return checks

    resource = _resource_evidence(operations)
    checks.append(
        _check(
            "bp_resource_iris",
            "blueprint",
            "fail" if resource else "pass",
            resource,
            "Medium" if resource else None,
        )
    )
    posts = _retrieval_post_evidence(operations)
    checks.append(
        _check(
            "bp_get_retrieval",
            "blueprint",
            "fail" if posts else "pass",
            posts,
            "Medium" if posts else None,
        )
    )
    versions = _version_evidence(operations)
    checks.append(
        _check(
            "bp_version_in_path",
            "blueprint",
            "fail" if versions else "pass",
            versions,
            "Medium" if versions else None,
        )
    )
    return checks


def _observed_jsonld(samples: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    if not samples:
        return "not_stated", [{"detail": "no unauthenticated sample was fetched"}]
    evidence = [
        {
            "url": sample.get("url"),
            "status": sample.get("status"),
            "jsonld": sample.get("jsonld"),
            "detail": sample.get("error")
            or _detail(
                f"content-type {sample.get('content_type') or 'unknown'}; "
                f"JSON-LD @context {'present' if sample.get('jsonld') else 'absent'}"
            ),
        }
        for sample in samples
    ]
    success = [sample for sample in samples if isinstance(sample.get("status"), int) and sample["status"] < 400]
    if any(sample.get("jsonld") for sample in success):
        return "pass", evidence
    if any(sample.get("json") and not sample.get("jsonld") for sample in success):
        return "fail", evidence
    return "not_stated", evidence


def practice_checks(spec: dict[str, Any] | None, operations: list[dict[str, Any]], remote_refs: list[str]) -> list[dict[str, Any]]:
    if spec is None:
        return [
            _check(check_id, "practice", "not_stated", [])
            for check_id in (
                "prac_info_contact",
                "prac_info_license",
                "prac_operation_summaries",
                "prac_operation_ids",
                "prac_response_examples",
                "prac_error_responses",
                "prac_pagination",
                "prac_local_refs",
            )
        ]
    info = spec.get("info") if isinstance(spec.get("info"), dict) else {}
    checks = [
        _check(
            "prac_info_contact",
            "practice",
            "pass" if _info_present(info, "contact", ("name", "email", "url")) else "fail",
            [] if _info_present(info, "contact", ("name", "email", "url")) else [{"detail": "info.contact name, email, or url is absent"}],
        ),
        _check(
            "prac_info_license",
            "practice",
            "pass" if _info_present(info, "license", ("name", "url")) else "fail",
            [] if _info_present(info, "license", ("name", "url")) else [{"detail": "info.license name or url is absent"}],
        ),
    ]
    if not operations:
        for check_id in (
            "prac_operation_summaries",
            "prac_operation_ids",
            "prac_response_examples",
            "prac_error_responses",
            "prac_pagination",
        ):
            checks.append(_check(check_id, "practice", "not_stated", []))
    else:
        missing_summary = [
            {"method": op["method"], "path": op["path"], "detail": "no summary or description"}
            for op in operations
            if not (op["summary"] or op["description"])
        ]
        missing_ids = [
            {"method": op["method"], "path": op["path"], "detail": "no operationId"}
            for op in operations
            if not op["operation_id"]
        ]
        missing_examples = []
        missing_errors = []
        for op in operations:
            success = [resp for resp in op["responses"] if str(resp["status"]).startswith("2")]
            errors = [resp for resp in op["responses"] if str(resp["status"])[:1] in {"4", "5"}]
            if success and not any(resp["has_example"] for resp in success):
                missing_examples.append(
                    {"method": op["method"], "path": op["path"], "detail": "2xx response has no example"}
                )
            if not errors:
                missing_errors.append(
                    {"method": op["method"], "path": op["path"], "detail": "no 4xx or 5xx response documented"}
                )
        checks.append(_check("prac_operation_summaries", "practice", "fail" if missing_summary else "pass", missing_summary))
        checks.append(_check("prac_operation_ids", "practice", "fail" if missing_ids else "pass", missing_ids))
        checks.append(
            _check(
                "prac_response_examples",
                "practice",
                "not_stated" if not any(str(resp["status"]).startswith("2") for op in operations for resp in op["responses"]) else ("fail" if missing_examples else "pass"),
                missing_examples,
            )
        )
        checks.append(_check("prac_error_responses", "practice", "fail" if missing_errors else "pass", missing_errors))

        collections = []
        for op in operations:
            if op["method"] != "GET":
                continue
            segments = [part for part in op["path"].split("/") if part]
            if not segments or segments[-1].startswith("{"):
                continue
            names = {str(param.get("name") or "").lower() for param in op["parameters"] if param.get("in") == "query"}
            if not names & _PAGE_PARAMS:
                collections.append(
                    {"method": "GET", "path": op["path"], "detail": "collection GET has no pagination parameter"}
                )
        if not any(
            op["method"] == "GET"
            and (parts := [part for part in op["path"].split("/") if part])
            and not parts[-1].startswith("{")
            for op in operations
        ):
            checks.append(_check("prac_pagination", "practice", "not_applicable", []))
        else:
            checks.append(_check("prac_pagination", "practice", "fail" if collections else "pass", collections))

    checks.append(
        _check(
            "prac_local_refs",
            "practice",
            "fail" if remote_refs else "pass",
            [{"detail": ref} for ref in remote_refs],
        )
    )
    return checks


def _line_snippet(text: str, match: re.Match[str]) -> str:
    start = text.rfind("\n", 0, match.start()) + 1
    end = text.find("\n", match.end())
    if end < 0:
        end = len(text)
    return _detail(text[start:end])


# Links and JS config keys that name a spec, a springdoc config, or a UI shell.
_DISCOVERY_RE = re.compile(
    r"""(?:href|src|spec-url|specurl)\s*=\s*["']([^"']+)["']"""
    r"""|\]\(\s*<?([^)\s>]+)>?\)"""
    r"""|(https?://[^\s"'<>]+)"""
    r"""|["'](?:url|configUrl|apiDescriptionUrl)["']\s*:\s*["']([^"']+)["']"""
    r"""|\b(?:url|configUrl|apiDescriptionUrl)\s*:\s*["']([^"']+)["']""",
    re.I,
)
_SPEC_FILE_RE = re.compile(r"(?:openapi|swagger|api-docs).*\.(?:json|yaml|yml)$", re.I)
_DISCOVERY_BUDGET = 4


def _resolve_link(origin: str, raw: str) -> str:
    raw = raw.strip().rstrip(").,;")
    if raw.startswith(("http://", "https://")):
        return raw
    if origin.startswith(("http://", "https://")):
        return urllib.parse.urljoin(origin, raw)
    if raw.startswith("/"):
        return raw
    base = Path(origin)
    parent = base if base.is_dir() else base.parent
    return str((parent / raw).resolve())


def _link_path(url: str) -> str:
    path = urllib.parse.urlparse(url).path if "://" in url else url
    return urllib.parse.unquote(path).split("?", 1)[0].split("#", 1)[0]


def _is_petstore(url: str) -> bool:
    """Stock Swagger UI ships this placeholder beside the real configUrl."""
    return (urllib.parse.urlparse(url).hostname or "").lower() == "petstore.swagger.io"


def _classify_target(url: str) -> str | None:
    """Return ``spec``, ``config``, or ``ui``. Asset bundles are ignored.

    ``swagger-config`` is classified before ``api-docs`` because springdoc
    serves the config at ``/v3/api-docs/swagger-config`` and the document
    at ``/v3/api-docs``.
    """
    if url.startswith(("mailto:", "javascript:", "data:")):
        return None
    path = _link_path(url)
    base = path.rstrip("/").rsplit("/", 1)[-1].lower()
    if not base or base.endswith((".css", ".png", ".svg", ".map", ".ico")):
        return None
    if "bundle" in base or "standalone" in base:
        return None
    lowered = path.lower()
    if "swagger-config" in lowered:
        return "config"
    if "swagger-initializer" in base or any(
        token in lowered for token in ("swagger-ui", "swaggerui", "/redoc", "rapidoc")
    ):
        return "ui"
    if base in {"redoc", "redoc.html", "rapidoc.html"}:
        return "ui"
    if _SPEC_FILE_RE.search(base):
        return "spec"
    if base in {"api-docs", "openapi"} or lowered.rstrip("/").endswith(("/api-docs", "/openapi")):
        return "spec"
    return None


def _discover_targets(text: str, origin: str) -> dict[str, list[str]]:
    """Spec, config, and UI URLs written on a page or in a Swagger initializer."""
    found: dict[str, list[str]] = {"spec": [], "config": [], "ui": []}
    visiting: set[str] = set()

    def add(raw: str, base: str) -> None:
        if not raw or raw.startswith(("mailto:", "javascript:", "#")):
            return
        resolved = _resolve_link(base, raw)
        if resolved in visiting:
            return
        visiting.add(resolved)
        kind = _classify_target(resolved)
        if kind and resolved not in found[kind]:
            found[kind].append(resolved)
        if "://" not in resolved and not resolved.startswith("/"):
            return
        parsed = urllib.parse.urlparse(resolved if "://" in resolved else "")
        if not parsed.query:
            return
        for key in ("url", "configUrl", "configurl"):
            for value in urllib.parse.parse_qs(parsed.query).get(key, []):
                add(value, resolved if "://" in resolved else base)

    for match in _DISCOVERY_RE.finditer(text):
        raw = next(group for group in match.groups() if group)
        add(raw, origin)
    return found


def _spec_rank(url: str) -> tuple[int, int]:
    path = _link_path(url).lower()
    petstore = 1 if _is_petstore(url) else 0
    extension = 0 if path.endswith((".json", ".yaml", ".yml")) else 1
    return (petstore, extension)


def _enqueue(buckets: dict[str, list[str]], text: str, origin: str, seen: set[str]) -> None:
    for kind, urls in _discover_targets(text, origin).items():
        for url in urls:
            if url in seen or url in buckets[kind]:
                continue
            buckets[kind].append(url)


def _next_discovery(buckets: dict[str, list[str]]) -> tuple[str, str] | None:
    """Prefer a real spec, then a config, then a UI. Petstore waits until nothing else is queued."""
    real = [url for url in buckets["spec"] if not _is_petstore(url)]
    if real:
        url = min(real, key=_spec_rank)
        buckets["spec"].remove(url)
        return url, "spec"
    if buckets["config"]:
        return buckets["config"].pop(0), "config"
    if buckets["ui"]:
        return buckets["ui"].pop(0), "ui"
    if buckets["spec"]:
        return buckets["spec"].pop(0), "spec"
    return None


def _enqueue_config_document(
    buckets: dict[str, list[str]],
    text: str,
    origin: str,
    seen: set[str],
) -> None:
    """Read springdoc ``url`` / ``urls`` / ``configUrl`` fields from a config document."""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return
    if not isinstance(payload, dict):
        return
    raw_urls: list[str] = []
    if isinstance(payload.get("url"), str):
        raw_urls.append(payload["url"])
    for item in payload.get("urls") or []:
        if isinstance(item, dict) and isinstance(item.get("url"), str):
            raw_urls.append(item["url"])
        elif isinstance(item, str):
            raw_urls.append(item)
    if isinstance(payload.get("configUrl"), str):
        raw_urls.append(payload["configUrl"])
    for raw in raw_urls:
        resolved = _resolve_link(origin, raw)
        kind = _classify_target(resolved)
        if kind and resolved not in seen and resolved not in buckets[kind]:
            buckets[kind].append(resolved)


def follow_to_spec(
    text: str,
    origin: str,
    fetcher: Fetcher,
) -> tuple[dict[str, Any] | None, str, dict[str, Any] | None]:
    """Follow docs and Swagger UI links until an OpenAPI document parses.

    Order: a linked spec, then a ``swagger-config`` (or ``configUrl``) document,
    then a Swagger UI / ReDoc page and its ``swagger-initializer.js``. The
    petstore URL bundled in stock Swagger UI is used only when no other
    candidate exists. At most ``_DISCOVERY_BUDGET`` extra fetches.
    """
    seen = {origin}
    via: list[str] = []
    buckets: dict[str, list[str]] = {"spec": [], "config": [], "ui": []}
    _enqueue(buckets, text, origin, seen)
    budget = _DISCOVERY_BUDGET
    while budget > 0:
        nxt = _next_discovery(buckets)
        if nxt is None:
            break
        url, kind = nxt
        if url in seen:
            continue
        seen.add(url)
        budget -= 1
        via.append(url)
        try:
            linked, linked_origin, link_error = load_text(url, fetcher)
        except (ValueError, FileNotFoundError, OSError) as exc:
            linked, linked_origin, link_error = "", url, str(exc)
        if link_error or not linked:
            continue
        spec = parse_spec(linked)
        if spec is not None:
            return spec, linked_origin, {"from": origin, "to": linked_origin, "via": via}
        _enqueue(buckets, linked, linked_origin, seen)
        if kind == "config":
            _enqueue_config_document(buckets, linked, linked_origin, seen)
    if not via:
        return None, origin, None
    return None, origin, {
        "from": origin,
        "to": via[-1],
        "via": via,
        "error": "linked document is not OpenAPI or Swagger",
    }


def extract_example_gets(text: str) -> list[str]:
    """Absolute GET URLs written on a docs page. Credentialed URLs are dropped."""
    urls: list[str] = []
    for match in _EXAMPLE_GET_RE.finditer(text):
        url = match.group(1).rstrip(").,;")
        try:
            ensure_http_url(url)
        except ValueError:
            continue
        if url not in urls:
            urls.append(url)
    return urls


def _outside_rubric(*texts: str) -> list[str]:
    blob = "\n".join(texts)
    return [name for name, pattern in _OUTSIDE if pattern.search(blob)]


def prose_checks(text: str) -> list[dict[str, Any]]:
    """Docs-only rubric. Undeclared facts stay ``not_stated`` rather than failures."""
    jsonld = _JSONLD_RE.search(text)
    endpoints = list(_ENDPOINT_RE.finditer(text))
    resource_evidence = []
    version_evidence = []
    for match in endpoints:
        method, path = match.group(1).upper(), match.group(2)
        if any(_is_verb_segment(segment) for segment in path.split("/")):
            resource_evidence.append(
                {"method": method, "path": path, "detail": _detail("verb-like path stated in the documentation")}
            )
        for segment in _version_segments(path):
            version_evidence.append(
                {
                    "method": method,
                    "path": path,
                    "detail": _detail(f"version segment '{segment}' stated in the documentation"),
                }
            )
    if not endpoints:
        resource_status, version_status = "not_stated", "not_stated"
    else:
        resource_status = "fail" if resource_evidence else "pass"
        version_status = "fail" if version_evidence else "pass"
    return [
        _check(
            "bp_openapi_doc",
            "blueprint",
            "fail",
            [{"detail": "documentation page has no parseable OpenAPI or Swagger document"}],
            "Medium",
        ),
        _check(
            "bp_jsonld_declared",
            "blueprint",
            "pass" if jsonld else "not_stated",
            [{"detail": _line_snippet(text, jsonld)}] if jsonld else [],
            None,
        ),
        _check(
            "bp_jsonld_observed",
            "blueprint",
            "not_stated",
            [{"detail": "no unauthenticated sample was fetched"}],
            None,
        ),
        _check("bp_resource_iris", "blueprint", resource_status, resource_evidence, "Medium" if resource_status == "fail" else None),
        _check("bp_get_retrieval", "blueprint", "not_stated", [], None),
        _check("bp_version_in_path", "blueprint", version_status, version_evidence, "Medium" if version_status == "fail" else None),
    ]


def _confidence(spec_parsed: bool, schemas_known: bool, samples: list[dict[str, Any]], attempted: bool) -> str:
    if not spec_parsed:
        return "low"
    failed = attempted and bool(samples) and all(
        sample.get("error")
        or not isinstance(sample.get("status"), int)
        or sample["status"] >= 400
        for sample in samples
    )
    if not schemas_known or failed:
        return "medium"
    return "high"


def _empty_findings(source: str, error: str) -> dict[str, Any]:
    return {
        "input": {"kind": "unreachable", "source": source, "hop": None, "error": error},
        "spec": {"format": None, "title": "", "version": "", "servers": []},
        "confidence": "low",
        "operations": [],
        "checks": [],
        "samples": [],
        "sample_plan": [],
        "unresolved_refs": [],
        "observed_property_names": [],
        "outside_rubric": [],
    }


def load_text(source: str, fetcher: Fetcher) -> tuple[str, str, str | None]:
    """Return text, canonical origin, and an error string when a URL cannot be read."""
    if source.startswith(("http://", "https://", "file:")):
        if source.startswith("file:"):
            raise ValueError(f"refusing non-http URL: {source}")
        ensure_http_url(source)
        result = fetcher(source)
        if result.error and not result.body:
            return "", source, result.error
        return result.body.decode("utf-8", errors="replace"), result.url or source, None
    path = Path(source)
    if not path.is_file():
        raise FileNotFoundError(source)
    return path.read_text(encoding="utf-8"), str(path.resolve()), None


def _interpret_sample(result: FetchResult, planned: dict[str, Any]) -> dict[str, Any]:
    parsed: Any = None
    if result.body:
        try:
            parsed = json.loads(result.body.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            parsed = None
    names: list[str] = []
    jsonld = False
    if isinstance(parsed, dict):
        jsonld = "@context" in parsed
        names = [str(key) for key in parsed.keys()]
    elif isinstance(parsed, list):
        for entry in parsed[:5]:
            if isinstance(entry, dict):
                jsonld = jsonld or "@context" in entry
                names.extend(str(key) for key in entry.keys())
    return {
        "url": result.url or planned["url"],
        "method": "GET",
        "path": planned.get("path"),
        "status": result.status,
        "content_type": (result.content_type or "").split(";", 1)[0].strip(),
        "json": parsed is not None,
        "jsonld": jsonld,
        "error": result.error,
        "truncated": result.truncated,
        "property_names": names[:40],
    }


def _spec_summary(spec: dict[str, Any] | None, origin: str) -> dict[str, Any]:
    if spec is None:
        return {"format": None, "title": "", "version": "", "servers": []}
    info = spec.get("info") if isinstance(spec.get("info"), dict) else {}
    if isinstance(spec.get("openapi"), str):
        fmt = f"openapi-{spec['openapi']}"
    else:
        fmt = f"swagger-{spec.get('swagger')}"
    return {
        "format": fmt,
        "title": str(info.get("title") or ""),
        "version": str(info.get("version") or ""),
        "servers": server_urls(spec, origin),
    }


def analyze(
    source: str,
    *,
    sample: int = 3,
    no_sample: bool = False,
    fetcher: Fetcher | None = None,
) -> dict[str, Any]:
    """Analyze ``source`` (path or http URL). Returns the findings object.

    ``fetcher`` replaces the default HTTP GET. Tests pass one so fixture
    runs do not open sockets. ``--no-sample`` still builds ``sample_plan``.
    """
    fetch = fetcher or default_fetcher
    text, origin, error = load_text(source, fetch)
    if error:
        return _empty_findings(source, error)

    page_text = text
    spec = parse_spec(text)
    if spec is None:
        spec, spec_origin, hop = follow_to_spec(text, origin, fetch)
    else:
        spec_origin = origin
        hop = None

    remote_refs = collect_remote_refs(spec) if spec else []
    operations = extract_operations(spec, spec_origin) if spec else []
    plan = select_sample_urls(operations, limit=sample)
    if spec is None and not no_sample:
        for url in extract_example_gets(text)[:sample]:
            plan.append({"url": url, "method": "GET", "path": urllib.parse.urlparse(url).path, "operation_id": ""})

    samples: list[dict[str, Any]] = []
    attempted = bool(plan) and not no_sample
    if attempted:
        for planned in plan:
            print(f"GET {planned['url']}", file=sys.stderr, flush=True)
            try:
                result = fetch(planned["url"])
            except Exception as exc:  # a stand-in fetcher, or a refused redirect
                result = FetchResult(None, "", b"", planned["url"], error=str(exc))
            samples.append(_interpret_sample(result, planned))

    names: set[str] = set()
    if spec is not None:
        _collect_property_names(spec, spec, names)
        info = spec.get("info") if isinstance(spec.get("info"), dict) else {}
        outside_text = page_text + " " + " ".join(
            str(info.get(key) or "") for key in ("title", "description")
        )
    else:
        outside_text = page_text
    for item in samples:
        names.update(item.get("property_names") or [])

    if spec is None:
        checks = prose_checks(text) + practice_checks(None, [], [])
        # Sampling from example URLs on a prose page can still observe JSON-LD.
        observed, observed_evidence = _observed_jsonld(samples)
        for check in checks:
            if check["id"] == "bp_jsonld_observed":
                check["status"] = observed
                check["evidence"] = observed_evidence
                check["priority"] = "High" if observed == "fail" else None
    else:
        checks = blueprint_checks(spec_parsed=True, operations=operations, samples=samples)
        checks.extend(practice_checks(spec, operations, remote_refs))

    return {
        "input": {
            "kind": "openapi" if spec is not None else "docs",
            "source": source,
            "hop": hop,
            "error": None,
        },
        "spec": _spec_summary(spec, spec_origin),
        "confidence": _confidence(spec is not None, _schemas_known(operations), samples, attempted),
        "operations": [_public_operation(operation) for operation in operations],
        "checks": checks,
        "samples": samples,
        "sample_plan": plan,
        "unresolved_refs": remote_refs,
        "observed_property_names": sorted(names)[:80],
        "outside_rubric": _outside_rubric(outside_text),
    }


def write_findings(findings: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "findings.json"
    path.write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assess an API against Blueprint Section 3 and a short REST lint.")
    parser.add_argument("input", help="Path or http(s) URL of an OpenAPI/Swagger document or an API docs page")
    parser.add_argument("--sample", type=int, default=3, help="Maximum unauthenticated GET samples (default 3)")
    parser.add_argument("--no-sample", action="store_true", help="Build sample_plan but do not call the API")
    parser.add_argument("--out-dir", type=Path, default=None, help="Directory for findings.json")
    args = parser.parse_args(argv)
    try:
        findings = analyze(args.input, sample=args.sample, no_sample=args.no_sample)
    except ValueError as exc:
        print(str(exc))
        return 2
    except FileNotFoundError as exc:
        print(f"input not found: {exc}")
        return 2
    out_dir = args.out_dir
    if out_dir is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_dir = Path(f"api_assess_output_{stamp}")
    path = write_findings(findings, out_dir)
    fails = [check for check in findings["checks"] if check["status"] == "fail"]
    blueprint_fails = sum(1 for check in fails if check["axis"] == "blueprint")
    practice_fails = sum(1 for check in fails if check["axis"] == "practice")
    print(f"confidence: {findings['confidence']}")
    print(f"blueprint fails: {blueprint_fails}")
    print(f"practice fails: {practice_fails}")
    print(f"findings: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
