"""Deprecated: API goal is a profile recipe, not a separate product.

Use ``get_task()`` (active profile) or ``get_task("api")`` / ``--profile api``.
"""
from tasks import get_task

TASK = get_task("api")
