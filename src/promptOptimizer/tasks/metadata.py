"""Deprecated: metadata goal is a profile recipe, not a separate product.

Use ``get_task("metadata")`` / ``--profile metadata`` for a metadata-focused run.
"""
from tasks import get_task

TASK = get_task("metadata")
