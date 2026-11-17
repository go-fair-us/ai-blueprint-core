"""Gap-source registry.

An extractor turns one repository of a run into gap items (see gaps.py for the item
schema). Register a new source with the decorator and list it under `sources:` in
impact.yaml (or pass --sources):

    from impactlib.extractors import register, ExtractResult

    @register("competency-question")
    def extract(run, repo, cfg):
        ...
        return ExtractResult(gaps=[...], non_gaps={"match": 9}, notes=[])

Each gap item must carry `source` equal to the registered name and a `key` that is
stable across repositories (the combined chart groups on source + key).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

REGISTRY: dict[str, Callable] = {}


@dataclass
class ExtractResult:
    gaps: list[dict] = field(default_factory=list)
    non_gaps: dict[str, int] = field(default_factory=dict)   # verdict -> count, not plotted
    notes: list[str] = field(default_factory=list)
    context: dict = field(default_factory=dict)   # shown to the model (e.g. all verdicts)
    available: bool = True        # False when the source has no data for this repo


def register(name: str):
    def deco(fn):
        REGISTRY[name] = fn
        return fn
    return deco


def get(name: str) -> Callable:
    load_builtin()
    if name not in REGISTRY:
        raise SystemExit(f"unknown gap source {name!r}; known: {', '.join(sorted(REGISTRY))}")
    return REGISTRY[name]


def load_builtin() -> None:
    from . import facet_check  # noqa: F401  (registers "facet-check")
