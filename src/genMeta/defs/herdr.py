"""Herdr helpers via herdr-python-client (Unix socket API).

Replaces subprocess CLI wrappers with ``HerdrClient.request`` / helpers.
Domain logic (name reclaim, multi-agent settle) stays here.

Aligned with Herdr **0.7.x**:
  - layout via ``workspace.create`` / ``pane.split``
  - ``agent.start`` with ``name`` + ``kind`` + ``pane_id`` + ``args``
  - submit via ``agent.prompt`` (pane.send_input fallback)
"""

from __future__ import annotations

import json
import os
import select
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from herdr_client import HerdrApiError, HerdrClient, HerdrClientError

# Long enough for events.wait / subscribe during multi-minute agent turns.
_DEFAULT_CLIENT_TIMEOUT_S = float(os.environ.get("HERDR_CLIENT_TIMEOUT", "600"))

_client: HerdrClient | None = None


def get_client(*, timeout: float | None = None) -> HerdrClient:
    """Return a shared HerdrClient (recreated if timeout differs)."""
    global _client
    t = _DEFAULT_CLIENT_TIMEOUT_S if timeout is None else timeout
    if _client is None or _client.timeout != t:
        _client = HerdrClient(timeout=t)
    return _client


def reset_client() -> None:
    """Drop the cached client (tests / socket path change)."""
    global _client
    _client = None


def request(method: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Socket request with fallback for methods herdr-python-client has not allowlisted yet.

    herdr-python-client 0.4.x rejects unknown methods (e.g. ``agent.prompt``,
    ``agent.wait``) before talking to the server. Herdr 0.7.x still serves them,
    so fall through to the raw envelope sender when the client allowlist is stale.
    """
    client = get_client()
    try:
        return client.request(method, params)
    except HerdrClientError as exc:
        if "unsupported herdr socket method" not in str(exc):
            raise
        with client._connect() as sock:
            return client._send_envelope(sock, method, params or {})


def ensure_reachable() -> None:
    """Ping the herdr server or raise FileNotFoundError / HerdrClientError."""
    get_client().ping()


def create_workspace(
    *,
    cwd: Path | str,
    label: str,
    focus: bool = False,
) -> Dict[str, Any]:
    """Create a workspace; returns the raw workspace.create result.

    Result includes ``workspace``, ``tab``, and ``root_pane`` (Herdr 0.7.x).
    """
    return request(
        "workspace.create",
        {
            "cwd": str(cwd),
            "label": label,
            "focus": focus,
        },
    )


def close_workspace(workspace_id: str, *, check: bool = True) -> None:
    try:
        request("workspace.close", {"workspace_id": workspace_id})
    except (HerdrApiError, HerdrClientError):
        if check:
            raise


def split_pane(
    from_pane_id: str,
    direction: str,
    *,
    cwd: Path | str,
    focus: bool = False,
) -> str:
    """Split an existing shell pane; return the new pane id.

    Layout is separate from agent launch in Herdr 0.7.x — create empty shell
    panes first, then ``agent.start`` into them.
    """
    if direction not in ("right", "down"):
        raise ValueError(f"split direction must be 'right' or 'down', got {direction!r}")
    result = request(
        "pane.split",
        {
            "target_pane_id": from_pane_id,
            "direction": direction,
            "cwd": str(cwd),
            "focus": focus,
        },
    )
    pane = result.get("pane") or {}
    pane_id = pane.get("pane_id")
    if not pane_id:
        raise RuntimeError(f"pane.split returned no pane_id: {result!r}")
    return str(pane_id)


def list_agents() -> List[Dict[str, Any]]:
    try:
        data = request("agent.list")
        return list(data.get("agents", []) or [])
    except (HerdrApiError, HerdrClientError):
        return []


def agent_info(target: str) -> Dict[str, Any]:
    """Resolve agent by live name or pane id (Herdr 0.7.x target rules)."""
    return request("agent.get", {"target": target})["agent"]


def agent_status(target: str) -> str:
    try:
        return str(agent_info(target).get("agent_status", "unknown"))
    except (HerdrApiError, HerdrClientError, KeyError):
        return "unknown"


def agent_pane_id(target: str) -> str:
    return str(agent_info(target)["pane_id"])


def agent_revision(target: str) -> int:
    try:
        return int(agent_info(target).get("revision", 0))
    except (HerdrApiError, HerdrClientError, KeyError, TypeError, ValueError):
        return 0


def ensure_agent_name(pane_id: str, name: str) -> Dict[str, Any]:
    """Ensure Herdr's live agent alias is bound to ``pane_id``.

    Important distinction in ``agent list``:
      - ``agent``  → kind/executable label (always ``pi`` for Pi)
      - ``name``   → optional unique alias (``researcher-2``, ``lead``, …)

    Herdr clears ``name`` when the occupant exits, is released, or is replaced
    (e.g. model/provider errors that restart the process). Pi's terminal title
    may still show ``--name`` even when the Herdr alias is gone. Re-bind by
    pane id so orchestrator lookups keep working.
    """
    info = agent_info(pane_id)
    current = info.get("name")
    if current == name:
        return info

    # If another live agent holds the alias, clear it first.
    if current and current != name:
        try:
            request("agent.rename", {"target": pane_id, "name": None})
        except HerdrApiError:
            pass
    try:
        holders = [a for a in list_agents() if a.get("name") == name]
        for h in holders:
            if h.get("pane_id") != pane_id:
                request(
                    "agent.rename",
                    {"target": str(h["pane_id"]), "name": None},
                )
    except HerdrApiError:
        pass

    result = request("agent.rename", {"target": pane_id, "name": name})
    agent = result.get("agent") or agent_info(pane_id)
    bound = agent.get("name")
    if bound != name:
        raise RuntimeError(
            f"failed to bind agent name {name!r} to pane {pane_id} "
            f"(got name={bound!r}, kind={agent.get('agent')!r})"
        )
    print(f"  bound alias {name!r} → {pane_id} (kind={agent.get('agent')})")
    return agent


def free_agent_names(names: Sequence[str]) -> None:
    """Free global Herdr agent names so a new run can claim them.

    Clears short names by default (panes stay open). Set
    GENMETA_CLOSE_STALE=1 (or HERDR_DEMO_CLOSE_STALE=1) to close holding
    workspaces instead.
    """
    wanted = set(names)
    agents = list_agents()
    close_stale = (
        os.environ.get("GENMETA_CLOSE_STALE", "").lower()
        in ("1", "true", "yes")
        or os.environ.get("HERDR_DEMO_CLOSE_STALE", "").lower()
        in ("1", "true", "yes")
    )
    workspaces_to_close: set[str] = set()

    for agent in agents:
        name = agent.get("name")
        if not name or name not in wanted:
            continue
        pane = agent.get("pane_id", "?")
        ws = agent.get("workspace_id", "?")
        if close_stale and ws and ws != "?":
            print(f"  name '{name}' held by {pane} in {ws}; will close workspace")
            workspaces_to_close.add(str(ws))
        else:
            print(f"  name '{name}' held by {pane} in {ws}; clearing name")
            try:
                request("agent.rename", {"target": name, "name": None})
            except HerdrApiError:
                pass

    for ws in sorted(workspaces_to_close):
        print(f"  closing stale workspace {ws}…")
        close_workspace(ws, check=False)

    remaining = {a.get("name") for a in list_agents() if a.get("name") in wanted}
    if remaining:
        raise RuntimeError(
            "Could not free agent names: "
            + ", ".join(sorted(n for n in remaining if n))
            + ". Close the holding workspace(s) with: herdr workspace close <id>"
            + " (see herdr agent list)"
        )


def start_agent(
    name: str,
    role: str,
    *,
    pane_id: str,
    model: Optional[str] = None,
    kind: str = "pi",
    timeout_ms: int = 90_000,
) -> "AgentSession":
    """Start a named agent in an existing shell pane (Herdr 0.7.x).

    Layout must already exist: create a workspace (or split panes), then pass
    the empty shell ``pane_id``. ``agent.start`` no longer accepts workspace /
    tab / cwd / split — only ``name``, ``kind``, ``pane_id``, optional
    ``timeout_ms``, and agent ``args`` after the kind selects the executable.
    """
    args: List[str] = []
    if model:
        args += ["--model", model]
    args += ["--name", name, "--append-system-prompt", role]

    params: Dict[str, Any] = {
        "name": name,
        "kind": kind,
        "pane_id": pane_id,
        "args": args,
        "timeout_ms": timeout_ms,
    }

    print(f"  starting {name} on {pane_id}" + (f" (model={model})" if model else ""))
    # Newly created/split panes need a moment for the interactive shell to own
    # the PTY; agent.start returns agent_pane_busy until then.
    deadline = time.time() + max(5.0, min(30.0, timeout_ms / 1000.0))
    result: Dict[str, Any] | None = None
    last_exc: Exception | None = None
    while time.time() < deadline:
        try:
            result = request("agent.start", params)
            last_exc = None
            break
        except HerdrApiError as exc:
            last_exc = exc
            if exc.code == "agent_name_taken":
                holders = [a for a in list_agents() if a.get("name") == name]
                if holders:
                    h = holders[0]
                    raise RuntimeError(
                        f"agent name '{name}' is already used "
                        f"(pane={h.get('pane_id')} workspace={h.get('workspace_id')}). "
                        f"Free it with: herdr agent rename {name} --clear "
                        f"or: herdr workspace close {h.get('workspace_id')}"
                    ) from exc
                raise
            if exc.code in ("agent_pane_busy", "pane_busy", "not_ready"):
                time.sleep(0.4)
                continue
            raise
    if result is None:
        assert last_exc is not None
        raise last_exc

    agent = result.get("agent") or {}
    ready_pane = str(agent.get("pane_id") or pane_id)
    # agent.start should set the alias; re-assert so list shows name≠null
    # even if detection briefly replaces the occupant.
    try:
        agent = ensure_agent_name(ready_pane, name)
    except (HerdrApiError, HerdrClientError, RuntimeError) as exc:
        print(f"  warning: could not verify alias for {name} on {ready_pane}: {exc}")

    bound = agent.get("name")
    kind = agent.get("agent")
    print(
        f"  {name} ready pane={ready_pane} "
        f"alias={bound!r} kind={kind!r} "
        f"(kind is always 'pi' for Pi; alias is the orchestrator name)"
    )
    if bound != name:
        raise RuntimeError(
            f"agent.start for {name!r} left Herdr alias unbound "
            f"(pane={ready_pane}, name={bound!r}, kind={kind!r}). "
            f"Fix with: herdr agent rename {ready_pane} {name}"
        )

    return AgentSession(
        name=name,
        pane_id=ready_pane,
        workspace_id=agent.get("workspace_id"),
        terminal_id=agent.get("terminal_id"),
        revision=int(agent.get("revision") or 0),
    )


# ---------------------------------------------------------------------------
# AgentSession — name + pane binding with submit / wait / read
# ---------------------------------------------------------------------------

# Process-local map: logical name → last known AgentSession (pane_id).
# Herdr may clear live aliases while idle agents wait; orchestrator look-ups
# by name must fall back to these pane bindings.
_SESSION_BY_NAME: Dict[str, "AgentSession"] = {}


def register_session(session: "AgentSession") -> "AgentSession":
    """Remember a pane-bound session for name-based recovery."""
    _SESSION_BY_NAME[session.name] = session
    return session


def clear_session_registry() -> None:
    """Drop cached sessions (tests / new orchestration run)."""
    _SESSION_BY_NAME.clear()


@dataclass
class AgentSession:
    """Bound agent name + pane_id for cheaper follow-up calls."""

    name: str
    pane_id: str
    workspace_id: Optional[str] = None
    terminal_id: Optional[str] = None
    revision: int = 0
    _last_status: str = field(default="unknown", repr=False)

    def __post_init__(self) -> None:
        register_session(self)

    @classmethod
    def from_name(cls, name: str) -> "AgentSession":
        """Resolve by live Herdr alias, else by cached pane_id from this run.

        Herdr clears ``name`` when an occupant exits, is released, or is
        replaced. The lead agent sits idle through research + review, so its
        alias is the most likely to drop. Prefer pane_id once known.
        """
        info: Dict[str, Any] | None = None
        try:
            info = agent_info(name)
        except HerdrApiError as alias_exc:
            cached = _SESSION_BY_NAME.get(name)
            if cached is None:
                raise RuntimeError(
                    f"agent {name!r} not found: no live Herdr alias and no "
                    f"cached pane from this run. Known sessions: "
                    f"{sorted(_SESSION_BY_NAME) or 'none'}"
                ) from alias_exc
            try:
                info = agent_info(cached.pane_id)
            except HerdrApiError as pane_exc:
                raise RuntimeError(
                    f"agent {name!r} not found: alias cleared and pane "
                    f"{cached.pane_id!r} is also gone"
                ) from pane_exc
            print(
                f"  recovered {name!r} via cached pane {cached.pane_id} "
                f"(Herdr alias was missing)"
            )

        session = cls(
            name=name,
            pane_id=str(info["pane_id"]),
            workspace_id=info.get("workspace_id"),
            terminal_id=info.get("terminal_id"),
            revision=int(info.get("revision") or 0),
            _last_status=str(info.get("agent_status") or "unknown"),
        )
        # Re-bind if Herdr dropped the alias but the pane is still known.
        if info.get("name") != name:
            try:
                ensure_agent_name(session.pane_id, name)
            except (HerdrApiError, HerdrClientError, RuntimeError) as exc:
                print(f"  warning: could not re-bind alias {name!r}: {exc}")
        return session

    def refresh(self) -> Dict[str, Any]:
        # Prefer pane_id: stable even when the live alias was cleared.
        try:
            info = agent_info(self.pane_id)
        except HerdrApiError:
            try:
                info = agent_info(self.name)
            except HerdrApiError as exc:
                raise RuntimeError(
                    f"agent {self.name!r} unreachable "
                    f"(pane={self.pane_id!r} and alias both missing)"
                ) from exc
        self.pane_id = str(info["pane_id"])
        self.workspace_id = info.get("workspace_id")
        self.terminal_id = info.get("terminal_id")
        self.revision = int(info.get("revision") or 0)
        self._last_status = str(info.get("agent_status") or "unknown")
        register_session(self)
        if info.get("name") != self.name:
            try:
                info = ensure_agent_name(self.pane_id, self.name)
                self._last_status = str(info.get("agent_status") or self._last_status)
            except (HerdrApiError, HerdrClientError, RuntimeError):
                pass
        return info

    @property
    def status(self) -> str:
        try:
            self.refresh()
        except (HerdrApiError, HerdrClientError):
            return "unknown"
        return self._last_status

    def submit(self, message: str) -> None:
        """Submit prompt text + Enter to this agent.

        Prefer ``agent.prompt`` (Herdr 0.7.x). Fall back to ``pane.send_input``
        if the server rejects prompt (older builds). Target by pane id so a
        dropped alias cannot break the hand-off mid-run.
        """
        self.refresh()
        print(f"  submitting to {self.name} ({self.pane_id})")
        try:
            request(
                "agent.prompt",
                {
                    "target": self.pane_id,
                    "text": message,
                },
            )
        except HerdrApiError:
            # Older servers or transient resolution failures: raw pane path.
            get_client().pane_send_input(self.pane_id, text=message, keys=["enter"])

    def read_transcript(self, lines: int = 120) -> str:
        # Socket API uses underscore source names (recent_unwrapped).
        # Prefer pane id so reads work even if the Herdr alias was cleared.
        self.refresh()
        result = request(
            "agent.read",
            {
                "target": self.pane_id,
                "source": "recent_unwrapped",
                "lines": lines,
                "format": "text",
            },
        )
        read = result.get("read") or {}
        return str(read.get("text") or "")

    def save_notes(self, path: Path) -> None:
        text = self.read_transcript()
        path.write_text(text, encoding="utf-8")
        print(f"  saved {self.name} → {path} ({path.stat().st_size} bytes)")

    def wait_until_idle(self, timeout_s: int = 90) -> None:
        """Wait until this agent reports idle or done (startup)."""
        print(f"  waiting for {self.name} to become idle…")
        deadline = time.time() + timeout_s
        # Fast path: already ready
        status = self.status
        if status in ("idle", "done"):
            print(f"  {self.name} ready ({status})")
            return

        # Prefer one-shot event wait for idle; also accept done via poll.
        # Prefer server-owned agent.wait (idle/done), then event wait, then poll.
        remaining_ms = max(1, int((deadline - time.time()) * 1000))
        try:
            request(
                "agent.wait",
                {
                    "target": self.pane_id,
                    "until": ["idle", "done"],
                    "timeout_ms": remaining_ms,
                },
            )
            print(f"  {self.name} ready (agent.wait)")
            return
        except (HerdrApiError, HerdrClientError):
            pass

        remaining_ms = max(1, int((deadline - time.time()) * 1000))
        try:
            request(
                "events.wait",
                {
                    "match_event": {
                        "type": "pane.agent_status_changed",
                        "pane_id": self.pane_id,
                        "agent_status": "idle",
                    },
                    "timeout_ms": remaining_ms,
                },
            )
            print(f"  {self.name} ready (idle)")
            return
        except HerdrApiError as exc:
            # Timeout or mismatch — fall through to poll (also catches done).
            if exc.code not in ("timeout", "wait_timeout", "not_found"):
                # Still poll; some servers use different timeout codes.
                pass

        while time.time() < deadline:
            status = self.status
            if status in ("idle", "done"):
                print(f"  {self.name} ready ({status})")
                return
            time.sleep(1.0)
        raise TimeoutError(f"{self.name} never became idle")

    def wait_settled(
        self,
        timeout_s: int = 300,
        allow_initial_idle: bool = False,
        base_revision: Optional[int] = None,
    ) -> bool:
        """Wait for a post-submit turn to finish (activity then idle/done).

        Must see the agent leave idle (working/blocked) before treating a later
        idle as "turn complete". A bare idle+revision bump is not enough —
        ``agent.prompt`` can advance revision while status is still idle, which
        previously let the orchestrator start the lead while the reviewer was
        still about to run.
        """
        return wait_all_settled(
            [self],
            timeout_s=timeout_s,
            base_revs={
                self.name: base_revision if base_revision is not None else self.revision
            },
            allow_initial_idle=allow_initial_idle,
        )


# ---------------------------------------------------------------------------
# Module-level convenience (orchestrator uses names as ids)
# ---------------------------------------------------------------------------


def _resolve(name_or_session: str | AgentSession) -> AgentSession:
    if isinstance(name_or_session, AgentSession):
        return name_or_session
    return AgentSession.from_name(name_or_session)


def submit(name: str, message: str) -> None:
    AgentSession.from_name(name).submit(message)


def read_transcript(name: str, lines: int = 120) -> str:
    return AgentSession.from_name(name).read_transcript(lines=lines)


def save_notes(name: str, path: Path) -> None:
    AgentSession.from_name(name).save_notes(path)


def wait_until_idle(name: str, timeout_s: int = 90) -> None:
    AgentSession.from_name(name).wait_until_idle(timeout_s=timeout_s)


def wait_settled(
    name: str,
    timeout_s: int = 300,
    allow_initial_idle: bool = False,
) -> bool:
    session = AgentSession.from_name(name)
    print(f"  waiting for {name} to settle…")
    ok = session.wait_settled(
        timeout_s=timeout_s,
        allow_initial_idle=allow_initial_idle,
        base_revision=session.revision,
    )
    if not ok:
        try:
            last = session.status
        except (HerdrApiError, HerdrClientError, RuntimeError):
            last = "unknown"
        print(f"  warning: {name} did not settle in time (last={last})")
    return ok


# How many consecutive idle/done polls with rev>base are required before we
# accept a turn as finished when we never observed working/blocked (fast model
# finished between polls). Keep this high enough that a post-prompt idle
# revision bump cannot look like completion.
_STABLE_IDLE_POLLS = 3


def _apply_status(
    name: str,
    status: str,
    rev: int,
    *,
    base: Dict[str, int],
    activity: Dict[str, bool],
    settled: Dict[str, bool],
    idle_stable: Dict[str, int],
    allow_initial_idle: bool,
    require_activity: bool = True,
) -> None:
    """Update activity/settled state for one agent status sample.

    Default ``require_activity=True``: idle alone does not settle until we have
    seen working/blocked for this turn. That enforces sequential phases
    (researchers → reviewer → lead).
    """
    if settled.get(name):
        return
    if status in ("working", "blocked"):
        if not activity[name]:
            print(f"  {name} is {status} (turn started)")
        activity[name] = True
        idle_stable[name] = 0
        return

    if status == "done":
        # Terminal: accept even if we missed the working window.
        print(f"  {name} is done")
        settled[name] = True
        idle_stable[name] = 0
        return

    if status != "idle":
        idle_stable[name] = 0
        return

    # --- idle ---
    if allow_initial_idle and not activity[name] and rev <= base.get(name, 0):
        # Startup path only: already idle with no turn expected.
        print(f"  {name} is idle (allow_initial_idle)")
        settled[name] = True
        return

    if activity[name]:
        print(f"  {name} is idle (turn finished after activity)")
        settled[name] = True
        idle_stable[name] = 0
        return

    if not require_activity and rev > base.get(name, 0):
        # Legacy loose mode (tests / callers that opt out).
        print(f"  {name} is idle (rev advanced, require_activity=False)")
        settled[name] = True
        return

    # Never observed working/blocked. Revision often advances when the prompt
    # is accepted, while status is still idle — do NOT treat that as complete.
    # Only after several consecutive idle samples with rev>base (and after the
    # activity-wait window in wait_all_settled) accept a missed-activity finish.
    if rev > base.get(name, 0):
        idle_stable[name] = idle_stable.get(name, 0) + 1
        if idle_stable[name] >= _STABLE_IDLE_POLLS:
            print(
                f"  {name} is idle (rev advanced, stable for "
                f"{idle_stable[name]} polls; missed working window)"
            )
            settled[name] = True
        return

    idle_stable[name] = 0


def _parse_status_event(event: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    """Return (pane_id, agent_status) from a subscribe push payload."""
    # Common shapes: top-level data, nested event/data, or flat.
    data = event.get("data") if isinstance(event.get("data"), dict) else event
    if isinstance(event.get("event"), dict):
        data = event["event"].get("data") or event["event"]
    if not isinstance(data, dict):
        return None, None
    pane_id = data.get("pane_id")
    status = data.get("agent_status")
    if pane_id is None and "data" in event and isinstance(event["data"], dict):
        pane_id = event["data"].get("pane_id")
        status = event["data"].get("agent_status")
    return (
        str(pane_id) if pane_id else None,
        str(status) if status else None,
    )


def wait_all_settled(
    names: Sequence[str | AgentSession],
    timeout_s: int = 300,
    base_revs: Optional[Dict[str, int]] = None,
    allow_initial_idle: bool = False,
    require_activity: bool = True,
    activity_grace_s: float = 45.0,
) -> bool:
    """Wait for multiple agents using event subscribe + revision poll fallback.

    Each entry may be a logical name or an ``AgentSession``. Prefer sessions
    (or names already registered via ``start_agent``) so idle aliases that
    Herdr cleared mid-run do not raise not_found.

    Turn barrier (default ``require_activity=True``):
      1. Wait until each agent is seen as working/blocked (turn started), or
      2. After ``activity_grace_s``, accept stable idle + advanced revision
         (fast model finished between polls), then
      3. Wait until idle/done after activity (turn finished).

    This prevents the lead from starting while the reviewer is still running
    because a post-prompt idle+rev bump looked like completion.
    """
    print(f"  waiting for {len(names)} agents (events + poll)…")
    if not names:
        return True

    sessions: Dict[str, AgentSession] = {}
    for item in names:
        session = _resolve(item)
        sessions[session.name] = session
    name_list = list(sessions.keys())
    base = base_revs or {n: sessions[n].revision for n in name_list}
    activity = {n: False for n in name_list}
    settled = {n: False for n in name_list}
    idle_stable = {n: 0 for n in name_list}
    pane_to_name = {s.pane_id: n for n, s in sessions.items()}
    started_at = time.time()
    # Until grace expires, do not count "stable idle + rev" as finished —
    # forces a real wait for working/ on slow starts.
    allow_missed_activity_after = started_at + max(0.0, activity_grace_s)

    deadline = time.time() + timeout_s
    client = HerdrClient(timeout=max(10.0, float(timeout_s) + 15.0))
    subs = [
        {"type": "pane.agent_status_changed", "pane_id": s.pane_id}
        for s in sessions.values()
    ]

    def _sample(n: str, status: str, rev: int) -> None:
        # Gate the missed-activity fallback until grace has elapsed.
        effective_require = require_activity
        if (
            require_activity
            and not activity[n]
            and not allow_initial_idle
            and time.time() < allow_missed_activity_after
        ):
            # Still in grace: only activity→idle or done can settle.
            # Suppress stable-idle-without-activity by keeping require_activity
            # and resetting idle_stable unless we saw activity.
            if status == "idle" and not activity[n]:
                idle_stable[n] = 0
                if rev > base.get(n, 0):
                    # Prompt accepted but turn not visibly started yet.
                    return
        _apply_status(
            n,
            status,
            rev,
            base=base,
            activity=activity,
            settled=settled,
            idle_stable=idle_stable,
            allow_initial_idle=allow_initial_idle,
            require_activity=effective_require,
        )

    def _poll_once() -> None:
        for n, session in sessions.items():
            if settled[n]:
                continue
            try:
                info = session.refresh()
            except (HerdrApiError, HerdrClientError, RuntimeError):
                continue
            _sample(
                n,
                str(info.get("agent_status") or "unknown"),
                int(info.get("revision") or 0),
            )

    # Snapshot before subscribe.
    _poll_once()
    if all(settled[n] for n in name_list):
        print("  all agents settled")
        return True

    try:
        with client.subscribe(subs) as sub:
            # Keep the subscribe socket blocking; use select so idle periods
            # do not poison the makefile with socket timeouts.
            sub._socket.settimeout(None)
            while time.time() < deadline and not all(settled[n] for n in name_list):
                remaining = deadline - time.time()
                ready, _, _ = select.select(
                    [sub._socket], [], [], min(1.0, max(0.2, remaining))
                )
                if not ready:
                    _poll_once()
                    continue

                line = sub._file.readline()
                if line == "":
                    # Stream closed — finish with poll.
                    break

                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                pane_id, status = _parse_status_event(event)
                if not pane_id or not status:
                    continue
                name = pane_to_name.get(pane_id)
                if not name or settled[name]:
                    continue
                try:
                    rev = int(sessions[name].refresh().get("revision") or 0)
                except (HerdrApiError, HerdrClientError, RuntimeError):
                    rev = sessions[name].revision
                # Keep activity map in sync with event status immediately.
                if status in ("working", "blocked") and not activity[name]:
                    print(f"  {name} is {status} (event)")
                    activity[name] = True
                    idle_stable[name] = 0
                _sample(name, status, rev)
    except (HerdrApiError, HerdrClientError, OSError) as exc:
        print(f"  warning: event subscribe failed ({exc}); falling back to poll")
        return _wait_all_settled_poll(
            sessions,
            timeout_s=max(1, int(deadline - time.time())),
            base_revs=base,
            allow_initial_idle=allow_initial_idle,
            activity=activity,
            settled=settled,
            idle_stable=idle_stable,
            require_activity=require_activity,
            activity_grace_s=max(0.0, allow_missed_activity_after - time.time()),
        )

    if all(settled[n] for n in name_list):
        print("  all agents settled")
        return True

    # Stream ended or deadline hit with unfinished agents — poll remaining time.
    remaining_s = max(1, int(deadline - time.time()))
    if remaining_s > 0 and time.time() < deadline:
        return _wait_all_settled_poll(
            sessions,
            timeout_s=remaining_s,
            base_revs=base,
            allow_initial_idle=allow_initial_idle,
            activity=activity,
            settled=settled,
            idle_stable=idle_stable,
            require_activity=require_activity,
            activity_grace_s=max(0.0, allow_missed_activity_after - time.time()),
        )

    for name in name_list:
        if not settled[name]:
            print(
                f"  warning: {name} did not settle "
                f"(activity={activity[name]}, last={sessions[name].status})"
            )
    return False


def _wait_all_settled_poll(
    sessions: Dict[str, AgentSession] | Sequence[str | AgentSession],
    timeout_s: int,
    base_revs: Dict[str, int],
    allow_initial_idle: bool,
    activity: Optional[Dict[str, bool]] = None,
    settled: Optional[Dict[str, bool]] = None,
    idle_stable: Optional[Dict[str, int]] = None,
    require_activity: bool = True,
    activity_grace_s: float = 0.0,
) -> bool:
    """Classic poll loop (fallback if subscribe is unavailable)."""
    if isinstance(sessions, dict):
        session_map = sessions
    else:
        session_map = {}
        for item in sessions:
            s = _resolve(item)
            session_map[s.name] = s
    name_list = list(session_map.keys())
    deadline = time.time() + timeout_s
    activity = activity or {n: False for n in name_list}
    settled = settled or {n: False for n in name_list}
    idle_stable = idle_stable or {n: 0 for n in name_list}
    base = base_revs
    grace_until = time.time() + max(0.0, activity_grace_s)

    while time.time() < deadline:
        pending = []
        for name in name_list:
            if settled[name]:
                continue
            session = session_map[name]
            try:
                info = session.refresh()
                status = str(info.get("agent_status") or "unknown")
                rev = int(info.get("revision") or 0)
            except (HerdrApiError, HerdrClientError, RuntimeError):
                status = "unknown"
                rev = session.revision

            if (
                require_activity
                and not activity[name]
                and not allow_initial_idle
                and time.time() < grace_until
                and status == "idle"
                and rev > base.get(name, 0)
            ):
                # Still waiting for working/ after prompt accept.
                idle_stable[name] = 0
                pending.append(name)
                continue

            _apply_status(
                name,
                status,
                rev,
                base=base,
                activity=activity,
                settled=settled,
                idle_stable=idle_stable,
                allow_initial_idle=allow_initial_idle,
                require_activity=require_activity,
            )
            if not settled[name]:
                pending.append(name)
        if not pending:
            print("  all agents settled")
            return True
        time.sleep(1.0)

    for name in name_list:
        if not settled[name]:
            print(f"  warning: {name} did not settle")
    return False
