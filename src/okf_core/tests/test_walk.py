from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from okf_core.walk import walk_bundle


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(body).lstrip(), encoding="utf-8")


def test_walk_bundle(tmp_path: Path):
    root = tmp_path / "bundle"
    _write(
        root / "a.md",
        """
        ---
        type: Concept
        title: A
        ---
        See [B](/b.md).
        """,
    )
    _write(
        root / "b.md",
        """
        ---
        type: Concept
        title: B
        ---
        Hello.
        """,
    )
    _write(root / "index.md", "# Index\n")
    concepts = walk_bundle(root)
    assert {c.id for c in concepts} == {"a", "b"}
    by_id = {c.id: c for c in concepts}
    assert by_id["a"].links_to == ["b"]
