"""Aggregate token usage + $cost from dspy LM ``.history``.

We read ``.history`` rather than ``dspy.track_usage()`` because the parallelizer
deep-copies the usage tracker into each Evaluate worker thread and never merges
it back — so ``track_usage()`` misses every threaded call (the common case here).
Each LM instead appends every call (threads included) to its own ``.history``,
each entry carrying ``usage`` and ``cost``. We clear the relevant LMs' history
before a run and sum it after.
"""
from __future__ import annotations


def _distinct(lms):
    seen, out = set(), []
    for lm in lms:
        if lm is not None and id(lm) not in seen:
            seen.add(id(lm))
            out.append(lm)
    return out


def reset_history(lms) -> None:
    """Clear history on each distinct LM so the next run measures only itself."""
    for lm in _distinct(lms):
        hist = getattr(lm, "history", None)
        if hist is not None:
            hist.clear()


def collect_usage(lms):
    """Return (totals, cost, by_model) summed over the LMs' current history.

    ``cost`` is a float in USD (0.0 when litellm can't price the endpoint, e.g.
    a self-hosted model). ``by_model`` breaks tokens/cost/calls down per model.
    """
    totals = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    cost = 0.0
    by_model: dict[str, dict] = {}
    for lm in _distinct(lms):
        model = getattr(lm, "model", "?")
        for entry in list(getattr(lm, "history", []) or []):
            usage = entry.get("usage") or {}
            slot = by_model.setdefault(
                model,
                {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "cost": 0.0, "calls": 0},
            )
            slot["calls"] += 1
            for k in ("prompt_tokens", "completion_tokens", "total_tokens"):
                v = usage.get(k)
                if isinstance(v, (int, float)):
                    totals[k] += int(v)
                    slot[k] += int(v)
            c = entry.get("cost")
            if isinstance(c, (int, float)):
                cost += c
                slot["cost"] += c
    return totals, cost, by_model
