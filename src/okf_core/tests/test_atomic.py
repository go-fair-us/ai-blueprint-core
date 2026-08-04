from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from okf_core.atomic import count_atomics, parse_atomic_concepts
from okf_core.walk import walk_bundle


SAMPLE_BODY = dedent(
    """
    Opening prose here.[^src]

    See also: [Requirements](/api-specification/requirements.md).

    # Atomic concepts

    | # | Concept | Lines |
    |---|---------|-------|
    | 118 | The NIAID repository landscape includes a variety of data systems. | 180 |
    | 119 | These systems range from little access to APIs. | 180 |
    | 120 | Aligning repositories maximizes findability. | 180 |

    [^src]: Source label
    """
).lstrip()


def test_parse_atomic_concepts_basic():
    rows = parse_atomic_concepts(SAMPLE_BODY, parent_id="api-specification/motivation")
    assert len(rows) == 3
    assert [r.number for r in rows] == [118, 119, 120]
    assert rows[0].parent_id == "api-specification/motivation"
    assert rows[0].source_lines == "180"
    assert "repository landscape" in rows[0].text
    assert rows[0].concept_id == "atomic/118"


def test_parse_atomic_empty_without_heading():
    assert parse_atomic_concepts("No table here.\n", parent_id="x") == []


def test_parse_atomic_line_range():
    body = dedent(
        """
        # Atomic concepts

        | # | Concept | Lines |
        |---|---------|-------|
        | 62 | Metadata element type. | 107-111 |
        """
    ).lstrip()
    rows = parse_atomic_concepts(body, parent_id="metadata-schema/requirements")
    assert len(rows) == 1
    assert rows[0].source_lines == "107-111"


def test_niaid_bundle_atomics():
    repo_bundle = (
        Path(__file__).resolve().parents[3]
        / "okf"
        / "bundles"
        / "niaid_blueprint"
    )
    if not repo_bundle.is_dir():
        import pytest

        pytest.skip("niaid_blueprint not present")
    concepts = walk_bundle(repo_bundle)
    total = count_atomics(concepts)
    assert total == 239
    numbers = sorted(a.number for c in concepts for a in c.atomics)
    assert numbers == list(range(1, 240))
    # motivation sample
    mot = next(c for c in concepts if c.id == "api-specification/motivation")
    assert [a.number for a in mot.atomics] == [118, 119, 120]
