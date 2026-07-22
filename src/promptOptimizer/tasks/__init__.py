"""Active optimization goal as a runtime ``Task``.

The goal comes from YAML (``config/profile.yaml`` or ``--profile``), not from
hard-coded api/metadata product modes. Separate goals = separate runs.
"""
from __future__ import annotations

from defs.config import (
    ProfileConfig,
    get_active_config,
    get_active_profile_config,
    load_app_config,
    load_profile_config,
    set_active_profile_config,
)
from tasks.base import Task, task_from_config

_CACHED_TASK: Task | None = None
_CACHED_KEY: str | None = None


def _cache_key(profile: ProfileConfig) -> str:
    src = str(profile.source_path) if profile.source_path else profile.name
    return f"{src}::{profile.name}"


def set_active_profile(profile: ProfileConfig | None) -> Task | None:
    """Install the active profile and return the runtime Task (or clear)."""
    global _CACHED_TASK, _CACHED_KEY
    set_active_profile_config(profile)
    if profile is None:
        _CACHED_TASK = None
        _CACHED_KEY = None
        return None
    task = task_from_config(profile)
    _CACHED_TASK = task
    _CACHED_KEY = _cache_key(profile)
    return task


def get_task(profile: str | None = None) -> Task:
    """Return the runtime Task for the active (or named) profile.

    * ``profile is None`` — use already-activated profile, or load
      ``config/profile.yaml``.
    * ``profile`` short name or path — load that profile (and activate it).
    """
    global _CACHED_TASK, _CACHED_KEY

    if profile is None:
        active = get_active_profile_config()
        if active is not None and _CACHED_TASK is not None:
            if _CACHED_KEY == _cache_key(active):
                return _CACHED_TASK
        # Load default active profile
        app = get_active_config() or load_app_config()
        pc = load_profile_config(None, app)
        return set_active_profile(pc)  # type: ignore[return-value]

    app = get_active_config() or load_app_config()
    pc = load_profile_config(profile, app)
    return set_active_profile(pc)  # type: ignore[return-value]


def clear_task_cache() -> None:
    """Drop cached task/profile (e.g. after switching --config / --profile)."""
    global _CACHED_TASK, _CACHED_KEY
    _CACHED_TASK = None
    _CACHED_KEY = None
    set_active_profile_config(None)


def list_profiles() -> list[str]:
    """Recipe names under config/profiles/."""
    app = get_active_config() or load_app_config()
    return app.list_profile_names()


# Deprecated aliases for older call sites / tests
def list_tasks() -> list[str]:
    return list_profiles()


def clear_profile_cache() -> None:
    clear_task_cache()
