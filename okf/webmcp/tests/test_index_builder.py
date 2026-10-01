from __future__ import annotations

from pathlib import Path

import pytest

from index_builder import (
    DEFAULT_BUNDLE,
    BundlePathError,
    build_payload,
    pillar_for_id,
    resolve_bundle_file,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "mini_bundle"


def _ids(payload: dict) -> set[str]:
    return {d["id"] for d in payload["documents"]}


def test_mini_bundle_tree_and_counts():
    payload = build_payload(FIXTURE)
    ids = _ids(payload)
    assert "index" in ids
    assert "log" in ids
    assert "concepts/index" in ids
    assert "concepts/alpha" in ids
    assert "concepts/beta" in ids

    stats = payload["stats"]
    assert stats["concepts"] == 2
    assert stats["atomics"] == 3
    assert stats["documents"] == 5

    alpha = next(d for d in payload["documents"] if d["id"] == "concepts/alpha")
    assert alpha["kind"] == "concept"
    assert alpha["type"] == "NIAID Blueprint Requirements"
    assert alpha["normative"] is True
    assert "doi" in alpha["tags"]
    assert [a["number"] for a in alpha["atomics"]] == [1, 2]
    assert "concepts/beta" in alpha["links_to"]

    tree_ids = []

    def walk(node):
        if node.get("kind") != "dir":
            tree_ids.append(node["id"])
        for child in node.get("children") or []:
            walk(child)

    walk(payload["tree"])
    assert "index" in tree_ids
    assert "log" in tree_ids
    assert "concepts/alpha" in tree_ids


def test_pillar_for_id():
    assert pillar_for_id("metadata-schema/requirements") == "metadata"
    assert pillar_for_id("persistent-identifiers") == "identifiers"
    assert pillar_for_id("overview/background") is None


def test_resolve_bundle_file_ok(tmp_path: Path):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    target = bundle / "a.md"
    target.write_text("# A\n", encoding="utf-8")
    nested = bundle / "sub"
    nested.mkdir()
    (nested / "b.md").write_text("# B\n", encoding="utf-8")

    assert resolve_bundle_file(bundle, "a.md") == target.resolve()
    assert resolve_bundle_file(bundle, "sub/b.md").name == "b.md"


@pytest.mark.parametrize(
    "rel",
    [
        "../a.md",
        "..",
        "/etc/passwd",
        "a.md/../../etc/passwd",
        "",
        "https://example.com/x.md",
        "secret.txt",
    ],
)
def test_resolve_bundle_file_rejects_escape(tmp_path: Path, rel: str):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "a.md").write_text("# A\n", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("nope", encoding="utf-8")
    with pytest.raises(BundlePathError):
        resolve_bundle_file(bundle, rel)


def test_niaid_blueprint_bundle_shape():
    if not DEFAULT_BUNDLE.is_dir():
        pytest.skip("niaid_blueprint bundle missing")
    payload = build_payload(DEFAULT_BUNDLE)
    ids = _ids(payload)
    assert "index" in ids
    assert "log" in ids
    assert "metadata-schema/requirements" in ids
    assert payload["stats"]["concepts"] == 27
    assert payload["stats"]["atomics"] == 239
    req = next(d for d in payload["documents"] if d["id"] == "metadata-schema/requirements")
    assert req["pillar"] == "metadata"
    assert req["normative"] is True
    assert req["type"]
    assert req["tags"]
    numbers = {a["number"] for a in req["atomics"]}
    assert 63 in numbers
