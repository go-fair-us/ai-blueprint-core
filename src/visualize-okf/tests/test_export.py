from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from textwrap import dedent

from visualize_okf.viewer.export import export_graph, write_gexf, write_graphml
from visualize_okf.viewer.generator import _walk_concepts


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(body).lstrip(), encoding="utf-8")


def _mini_bundle(root: Path) -> None:
    _write(
        root / "concepts" / "a.md",
        """
        ---
        type: Concept
        title: Concept A
        description: 'Alpha & beta <test>'
        tags: [alpha, beta]
        status: stable
        generated: { by: test/fixture, at: 2026-05-28T00:00:00Z }
        sources:
          - id: b-src
            resource: /examples/b.md
            title: Example B
        ---
        Links to [B](../examples/b.md).
        """,
    )
    _write(
        root / "examples" / "b.md",
        """
        ---
        type: Skill Bundle Example
        title: Example B
        description: Bravo.
        verified: { by: human:reviewer, at: 2026-06-01T00:00:00Z }
        ---
        Back to [A](../concepts/a.md).
        """,
    )
    _write(root / "index.md", "# Index\n")


def test_write_gexf(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _mini_bundle(bundle)
    concepts = _walk_concepts(bundle)
    out = tmp_path / "graph.gexf"
    stats = write_gexf(concepts, out, graph_name="Test")
    assert stats["concepts"] == 2
    # link edges both ways + one provenance source edge a→b
    assert stats["edges"] == 3
    assert out.exists()

    text = out.read_text(encoding="utf-8")
    assert 'defaultedgetype="directed"' in text
    assert "Concept A" in text
    assert "concepts/a" in text
    assert "examples/b" in text
    assert "Skill Bundle Example" in text
    assert "trust_tier" in text
    assert "generated_by" in text
    assert 'title="kind"' in text

    root = ET.fromstring(text.encode("utf-8"))
    ns = {"g": "http://gexf.net/1.3"}
    nodes = root.findall(".//g:node", ns)
    edges = root.findall(".//g:edge", ns)
    assert len(nodes) == 2
    assert len(edges) == 3
    ids = {n.get("id") for n in nodes}
    assert ids == {"concepts/a", "examples/b"}
    pairs = {(e.get("source"), e.get("target")) for e in edges}
    assert ("concepts/a", "examples/b") in pairs
    assert ("examples/b", "concepts/a") in pairs


def test_write_graphml(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _mini_bundle(bundle)
    concepts = _walk_concepts(bundle)
    out = tmp_path / "graph.graphml"
    stats = write_graphml(concepts, out, graph_name="Test")
    assert stats["concepts"] == 2
    assert stats["edges"] == 3

    text = out.read_text(encoding="utf-8")
    assert 'edgedefault="directed"' in text
    assert 'attr.name="trust_tier"' in text
    assert 'attr.name="kind"' in text
    root = ET.fromstring(text.encode("utf-8"))
    ns = {"g": "http://graphml.graphdrawing.org/xmlns"}
    nodes = root.findall(".//g:node", ns)
    edges = root.findall(".//g:edge", ns)
    assert len(nodes) == 2
    assert len(edges) == 3


def test_export_graph_gexf_cli_path(tmp_path: Path):
    bundle = tmp_path / "bundle"
    _mini_bundle(bundle)
    out = tmp_path / "out.gexf"
    stats = export_graph(bundle, out, "gexf", bundle_name="Mini")
    assert stats["format"] == "gexf"
    assert stats["concepts"] == 2
    assert Path(stats["out"]).exists()


def test_export_special_chars_in_description(tmp_path: Path):
    """Descriptions with & < > must not break XML."""
    bundle = tmp_path / "bundle"
    _mini_bundle(bundle)
    out = tmp_path / "graph.gexf"
    export_graph(bundle, out, "gexf")
    # Round-trip parse
    ET.parse(out)
