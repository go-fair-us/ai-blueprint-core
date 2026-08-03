"""Export OKF concept graphs to Gephi-friendly formats (GEXF, GraphML)."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from xml.dom import minidom

from visualize_okf.viewer.generator import (
    Concept,
    _build_graph,
    _walk_concepts,
    generate_visualization,
)

# Re-export for callers that want a single entry point
__all__ = [
    "export_graph",
    "generate_visualization",
    "write_gexf",
    "write_graphml",
]


def load_concepts(bundle_root: Path) -> list[Concept]:
    bundle_root = Path(bundle_root)
    if not bundle_root.is_dir():
        raise FileNotFoundError(f"Bundle directory not found: {bundle_root}")
    return _walk_concepts(bundle_root)


def _xml_escape_attr(text: str) -> str:
    """ElementTree handles escaping on write; normalize control chars for Gephi."""
    return (text or "").replace("\r\n", "\n").replace("\r", "\n")


def _pretty_xml(elem: ET.Element) -> str:
    rough = ET.tostring(elem, encoding="utf-8")
    parsed = minidom.parseString(rough)
    # minidom adds an XML declaration; keep it
    return parsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")


def _tags_str(tags: Any) -> str:
    if isinstance(tags, list):
        return "; ".join(str(t) for t in tags)
    return str(tags or "")


def _sources_str(sources: Any) -> str:
    """Serialize sources list for a single string attribute."""
    if not sources:
        return ""
    try:
        return json.dumps(sources, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(sources)


def write_gexf(
    concepts: list[Concept],
    out_path: Path,
    *,
    graph_name: str = "OKF Bundle",
) -> dict[str, int]:
    """Write a directed GEXF 1.3 graph Gephi can open via File → Open."""
    graph = _build_graph(concepts)
    nodes = graph["nodes"]
    edges = graph["edges"]

    gexf = ET.Element(
        "gexf",
        {
            "xmlns": "http://gexf.net/1.3",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://gexf.net/1.3 http://gexf.net/1.3/gexf.xsd",
            "version": "1.3",
        },
    )
    meta = ET.SubElement(gexf, "meta")
    ET.SubElement(meta, "creator").text = "visualize-okf"
    ET.SubElement(meta, "description").text = graph_name

    g = ET.SubElement(
        gexf,
        "graph",
        {"mode": "static", "defaultedgetype": "directed"},
    )

    attrs = ET.SubElement(g, "attributes", {"class": "node"})
    attr_defs = [
        ("0", "type", "string"),
        ("1", "description", "string"),
        ("2", "resource", "string"),
        ("3", "tags", "string"),
        ("4", "color", "string"),
        ("5", "size", "integer"),
        ("6", "status", "string"),
        ("7", "generated_by", "string"),
        ("8", "generated_at", "string"),
        ("9", "trust_tier", "string"),
        ("10", "stale_after", "string"),
        ("11", "sources", "string"),
    ]
    for aid, title, atype in attr_defs:
        ET.SubElement(attrs, "attribute", {"id": aid, "title": title, "type": atype})

    edge_attrs = ET.SubElement(g, "attributes", {"class": "edge"})
    ET.SubElement(
        edge_attrs, "attribute", {"id": "e0", "title": "kind", "type": "string"}
    )

    nodes_el = ET.SubElement(g, "nodes")
    for n in nodes:
        d = n["data"]
        node = ET.SubElement(
            nodes_el,
            "node",
            {
                "id": str(d["id"]),
                "label": _xml_escape_attr(str(d.get("label") or d["id"])),
            },
        )
        attvalues = ET.SubElement(node, "attvalues")
        values = [
            ("0", str(d.get("type") or "")),
            ("1", _xml_escape_attr(str(d.get("description") or ""))),
            ("2", str(d.get("resource") or "")),
            ("3", _tags_str(d.get("tags"))),
            ("4", str(d.get("color") or "")),
            ("5", str(int(d.get("size") or 30))),
            ("6", str(d.get("status") or "stable")),
            ("7", str(d.get("generated_by") or "")),
            ("8", str(d.get("generated_at") or "")),
            ("9", str(d.get("trust_tier") or "unverified")),
            ("10", str(d.get("stale_after") or "")),
            ("11", _xml_escape_attr(_sources_str(d.get("sources")))),
        ]
        for aid, val in values:
            ET.SubElement(attvalues, "attvalue", {"for": aid, "value": val})

    edges_el = ET.SubElement(g, "edges")
    for i, e in enumerate(edges):
        d = e["data"]
        edge = ET.SubElement(
            edges_el,
            "edge",
            {
                "id": str(d.get("id") or i),
                "source": str(d["source"]),
                "target": str(d["target"]),
            },
        )
        attvalues = ET.SubElement(edge, "attvalues")
        ET.SubElement(
            attvalues,
            "attvalue",
            {"for": "e0", "value": str(d.get("kind") or "link")},
        )

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = _pretty_xml(gexf)
    out_path.write_text(text, encoding="utf-8")
    return {
        "concepts": len(nodes),
        "edges": len(edges),
        "bytes": len(text.encode("utf-8")),
    }


def write_graphml(
    concepts: list[Concept],
    out_path: Path,
    *,
    graph_name: str = "OKF Bundle",
) -> dict[str, int]:
    """Write GraphML for Gephi (File → Open) or other tools."""
    graph = _build_graph(concepts)
    nodes = graph["nodes"]
    edges = graph["edges"]

    root = ET.Element(
        "graphml",
        {
            "xmlns": "http://graphml.graphdrawing.org/xmlns",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": (
                "http://graphml.graphdrawing.org/xmlns "
                "http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
            ),
        },
    )
    keys = [
        ("label", "node", "label", "string"),
        ("type", "node", "type", "string"),
        ("description", "node", "description", "string"),
        ("resource", "node", "resource", "string"),
        ("tags", "node", "tags", "string"),
        ("color", "node", "color", "string"),
        ("size", "node", "size", "int"),
        ("status", "node", "status", "string"),
        ("generated_by", "node", "generated_by", "string"),
        ("generated_at", "node", "generated_at", "string"),
        ("trust_tier", "node", "trust_tier", "string"),
        ("stale_after", "node", "stale_after", "string"),
        ("sources", "node", "sources", "string"),
        ("kind", "edge", "kind", "string"),
    ]
    for kid, kfor, kname, ktype in keys:
        ET.SubElement(
            root,
            "key",
            {"id": kid, "for": kfor, "attr.name": kname, "attr.type": ktype},
        )

    g = ET.SubElement(
        root,
        "graph",
        {"id": graph_name, "edgedefault": "directed"},
    )

    for n in nodes:
        d = n["data"]
        node = ET.SubElement(g, "node", {"id": str(d["id"])})
        fields = [
            ("label", str(d.get("label") or d["id"])),
            ("type", str(d.get("type") or "")),
            ("description", _xml_escape_attr(str(d.get("description") or ""))),
            ("resource", str(d.get("resource") or "")),
            ("tags", _tags_str(d.get("tags"))),
            ("color", str(d.get("color") or "")),
            ("size", str(int(d.get("size") or 30))),
            ("status", str(d.get("status") or "stable")),
            ("generated_by", str(d.get("generated_by") or "")),
            ("generated_at", str(d.get("generated_at") or "")),
            ("trust_tier", str(d.get("trust_tier") or "unverified")),
            ("stale_after", str(d.get("stale_after") or "")),
            ("sources", _sources_str(d.get("sources"))),
        ]
        for kid, val in fields:
            data_el = ET.SubElement(node, "data", {"key": kid})
            data_el.text = val

    for i, e in enumerate(edges):
        d = e["data"]
        edge = ET.SubElement(
            g,
            "edge",
            {
                "id": str(d.get("id") or i),
                "source": str(d["source"]),
                "target": str(d["target"]),
            },
        )
        kind_el = ET.SubElement(edge, "data", {"key": "kind"})
        kind_el.text = str(d.get("kind") or "link")

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = _pretty_xml(root)
    out_path.write_text(text, encoding="utf-8")
    return {
        "concepts": len(nodes),
        "edges": len(edges),
        "bytes": len(text.encode("utf-8")),
    }


_FORMAT_DEFAULTS = {
    "html": "viz.html",
    "gexf": "graph.gexf",
    "graphml": "graph.graphml",
}


def default_out_path(bundle_root: Path, fmt: str) -> Path:
    return Path(bundle_root) / _FORMAT_DEFAULTS[fmt]


def export_graph(
    bundle_root: Path,
    out_path: Path,
    fmt: str,
    *,
    bundle_name: str | None = None,
) -> dict[str, Any]:
    """Export a bundle graph to html, gexf, or graphml.

    Returns stats dict including concepts, edges, bytes, and format.
    """
    fmt = fmt.lower().strip()
    if fmt not in _FORMAT_DEFAULTS:
        raise ValueError(f"Unknown format {fmt!r}; choose html, gexf, or graphml")

    name = bundle_name or Path(bundle_root).resolve().name
    if fmt == "html":
        stats = generate_visualization(bundle_root, out_path, bundle_name=name)
    else:
        concepts = load_concepts(bundle_root)
        if fmt == "gexf":
            stats = write_gexf(concepts, out_path, graph_name=name)
        else:
            stats = write_graphml(concepts, out_path, graph_name=name)
    stats = dict(stats)
    stats["format"] = fmt
    stats["out"] = str(out_path)
    return stats
