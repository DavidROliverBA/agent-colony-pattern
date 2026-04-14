"""Managed Agents substrate adapter — scaffolding for Teaching Colony v1.6.0.

This is Phase 2 scaffolding from Sub-agent C (Batch 1). The working live
path is scheduled for Sub-agent D (Batch 2). Research findings that
drive the scaffolding live in ``api-research.md`` — read it first.

Design in one paragraph
-----------------------
We use the Anthropic **Claude Managed Agents** API (public beta,
2026-04-08), via the standard ``anthropic`` Python SDK under
``client.beta.*``. Each colony role is one ``agent`` resource with a
stable ID. All substrate operations except ``dispatch_agent`` run as
**client-executed custom tools**: Claude calls them by name, the API
surfaces an ``agent.tool_use`` event, our adapter runs arbitrary local
Python (reading/writing files under ``<root>/state/`` and
``<root>/colony/mirrors/``), and we post the result back as
``user.custom_tool_result``. This keeps the on-disk state shape identical
to Sub-agent B's Claude Code substrate so both adapters produce portable
event logs.

``dispatch_agent`` has two paths. The default **fallback** path opens a
fresh session against the target agent and streams it to idle — works
for every account. The optional **native** path uses ``callable_agents``
plus the ``agent_toolset_20260401`` delegation tool; it requires
research-preview allowlist access. Sub-agent D implements the fallback
first.

See ``api-research.md`` for the full contract-to-mechanism mapping.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # preferred: fully-qualified import (pytest from repo root)
    from examples.teaching_colony.contract import (
        AuditEntry,
        Classification,
        Document,
        Event,
        Mirror,
        Signature,
        SubstrateContract,
    )
except Exception:
    try:  # sibling-relative (run.py from inside examples/teaching_colony/)
        from contract import (  # type: ignore
            AuditEntry,
            Classification,
            Document,
            Event,
            Mirror,
            Signature,
            SubstrateContract,
        )
    except Exception:  # pragma: no cover
        # Fallback lightweight stand-ins — only when BOTH imports above failed.
        from dataclasses import dataclass, field

        class SubstrateContract:  # type: ignore[no-redef]
            pass

        @dataclass
        class Mirror:  # type: ignore[no-redef]
            agent_id: str
            data: dict

        @dataclass
        class Event:  # type: ignore[no-redef]
            type: str
            actor: str
            payload: dict
            timestamp: str = ""
            substrate: str = ""

        @dataclass
        class Document:  # type: ignore[no-redef]
            path: str
            topic: str
            content: str
            provenance: str = ""
            cross_references: list = field(default_factory=list)

        @dataclass
        class AuditEntry:  # type: ignore[no-redef]
            action: str
            actor: str
            co_signer: str
            pre_state_hash: str
            post_state_hash: str
            timestamp: str
            rollback_window_minutes: int = 60

        @dataclass
        class Signature:  # type: ignore[no-redef]
            action_class: str
            actor: str
            co_signer: str
            granted: bool
            timestamp: str
            reason: str = ""

        @dataclass
        class Classification:  # type: ignore[no-redef]
            blast_radius: str
            review_regime: str
            action_class: str
            actor_trust_tier: str


SUBSTRATE_ID = "managed-agents"
BETA_HEADER = "managed-agents-2026-04-01"


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower())
    return s.strip("-") or "untitled"


class ManagedAgentsAdapter(SubstrateContract):
    """Managed Agents API substrate for the Teaching Colony.

    Parameters
    ----------
    repo_root:
        Path to the **colony root** (same convention as the Claude Code
        substrate). Mirrors live at ``repo_root/colony/mirrors/``, state
        at ``repo_root/state/``, events at ``repo_root/state/events.jsonl``,
        and KB at ``repo_root/state/kb/``.
    mock:
        When ``True``, return deterministic canned responses with no
        network calls. Mock mode is the demo default and MUST match
        the Claude Code substrate mock in shape so portability checks
        succeed offline.
    use_native_dispatch:
        When ``True``, use ``callable_agents`` + ``agent_toolset_20260401``
        for ``dispatch_agent``. Requires research-preview allowlist.
        Default ``False`` — the single-session-per-dispatch fallback is used.
    model:
        Model id for agents created on the managed side. Defaults to the
        same Haiku variant as the Claude Code substrate for parity.
    """

    def __init__(
        self,
        repo_root: Path,
        mock: bool = False,
        use_native_dispatch: bool = False,
        model: str = "claude-haiku-4-5-20251001",
        **kwargs: Any,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.mock = mock
        self.use_native_dispatch = use_native_dispatch
        self.model = model
        self.substrate_name = SUBSTRATE_ID
        self._extra_kwargs = kwargs

        # Layout — MUST match the Claude Code substrate byte-for-byte.
        self.colony_dir = self.repo_root / "colony"
        self.mirrors_dir = self.colony_dir / "mirrors"
        self.state_dir = self.repo_root / "state"
        self.kb_dir = self.state_dir / "kb"
        self.events_path = self.state_dir / "events.jsonl"

        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.kb_dir.mkdir(parents=True, exist_ok=True)

        # Lazily constructed on first non-mock call.
        self._client: Any = None
        self._agent_ids: dict[str, str] = {}  # role_name -> agent_<id>
        self._environment_id: str | None = None

    # ------------------------------------------------------------------
    # Internals — Sub-agent D to complete
    # ------------------------------------------------------------------

    def _get_client(self) -> Any:  # pragma: no cover - live path
        """Return a cached ``anthropic.Anthropic()`` client.

        TODO(sub-agent-D): lazily import ``anthropic``, construct the
        client (auth from ``ANTHROPIC_API_KEY``), and verify the SDK
        supports the ``managed-agents-2026-04-01`` beta header. Do NOT
        import ``claude_agent_sdk`` — that is a different package for
        the local Claude Code harness.
        """
        if self.mock:
            raise RuntimeError("_get_client called in mock mode — bug")
        if self._client is None:
            raise NotImplementedError(
                "Sub-agent D: construct the anthropic.Anthropic() client here"
            )
        return self._client

    def _ensure_agents(self) -> None:  # pragma: no cover - live path
        """Create-or-load the colony agents; cache IDs in ``self._agent_ids``.

        TODO(sub-agent-D): for each role present in the colony mirrors
        directory, create a ``beta.agents`` resource with its system
        prompt from the mirror, the colony_* custom tools registered,
        and ``agent_toolset_20260401`` disabled (we don't use the
        built-in bash/file tools). See api-research.md Recommendation 2.
        """
        raise NotImplementedError(
            "Sub-agent D: implement agent creation + ID caching"
        )

    # ------------------------------------------------------------------
    # Canned mock responses — MUST match the Claude Code substrate
    # ------------------------------------------------------------------

    def _mock_dispatch(self, agent_id: str, input: dict) -> dict:
        task = input.get("task")
        if agent_id == "teacher" and task == "teach":
            topic = input.get("topic", "")
            if topic == "beekeeping":
                return {
                    "answer": (
                        "Beekeeping starts with a hive, a queen, and a "
                        "seasonal rhythm of inspection. Citing the primer: "
                        "manage space, monitor for varroa, and never open "
                        "the colony in the rain."
                    ),
                    "tokens": 0,
                    "mock": True,
                }
            if topic == "agent-colony-pattern":
                return {
                    "answer": (
                        "The Agent Colony pattern is a colony of specialised "
                        "agents with mirrors, event memory, and co-signed "
                        "changes — like a beehive, where every forager has "
                        "a role but the hive decides together."
                    ),
                    "tokens": 0,
                    "mock": True,
                }
        if agent_id == "librarian":
            if task == "curate":
                file_path = input.get("file", "")
                derived = Path(file_path).stem or "untitled"
                return {
                    "topic": derived,
                    "content": f"Summary of {file_path} (mock).",
                    "cross_references": [],
                    "tokens": 0,
                    "mock": True,
                }
            if task == "compute_coverage":
                return {
                    "topics": {
                        "beekeeping": {"docs": 1},
                        "agent-colony-pattern": {
                            "docs": 5,
                            "cross_references": 3,
                        },
                    },
                    "tokens": 0,
                    "mock": True,
                }
            if task == "propose_capability":
                return {
                    "agent_id": "teacher",
                    "capability": "teach_agent_colony_pattern",
                    "justification": (
                        "Librarian detected 5 curated documents on "
                        "agent-colony-pattern with 3 cross-references — "
                        "teacher should graduate this topic to a core "
                        "capability."
                    ),
                    "tokens": 0,
                    "mock": True,
                }
        if agent_id == "sentinel" and task == "cosign":
            return {
                "granted": True,
                "reason": "matches pre-registered policy",
                "tokens": 0,
                "mock": True,
            }
        # Default canned response — keeps the demo moving.
        return {"answer": "[mock]", "tokens": 0, "mock": True}

    # ------------------------------------------------------------------
    # Eight contract operations
    # ------------------------------------------------------------------

    def dispatch_agent(self, agent_id: str, input: dict) -> dict:
        """Dispatch a colony agent and return its structured output.

        Two code paths gated by ``self.use_native_dispatch``:

        * **Fallback (default)** — open a fresh session against the
          target agent via ``client.beta.sessions.create(agent=<id>,
          ...)``, send ``input`` as a user event, stream events to
          ``session.thread_idle``, collect the final ``agent.message``
          text, parse it as JSON if the agent was prompted to emit
          JSON, and return as a dict. Works without research-preview
          access.

        * **Native** — route through a single orchestrator session
          using ``callable_agents`` + ``agent_toolset_20260401``.
          Requires research-preview allowlist. Multi-agent threads
          surface as ``session.thread_created`` / ``session.thread_idle``
          events on the primary stream. See api-research.md Q3.
        """
        if self.mock:
            return self._mock_dispatch(agent_id, input)
        # TODO(sub-agent-D): implement fallback path first, then optional
        # native path under ``if self.use_native_dispatch:``.
        raise NotImplementedError(
            "Sub-agent D: implement dispatch_agent — fallback path first. "
            "See api-research.md Q3 for the two-path design."
        )

    # ---------------------------------------------------------------- mirrors

    def _mirror_path(self, agent_id: str) -> Path:
        return self.mirrors_dir / f"{agent_id}.yaml"

    def read_mirror(self, agent_id: str) -> Mirror:
        """Read an agent mirror from local disk.

        In both mock and live mode the mirror data is ours — reading is
        a local file op. In live mode this method doubles as the handler
        for the ``colony_read_mirror`` custom tool (Claude calls it, we
        run this code, result goes back as ``user.custom_tool_result``).
        """
        path = self._mirror_path(agent_id)
        if not path.exists():
            alt = self.mirrors_dir / f"{agent_id}-agent.yaml"
            if alt.exists():
                path = alt
        data: dict = {}
        if path.exists():
            try:
                import yaml  # optional dep

                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except Exception:
                data = {}
        return Mirror(agent_id=agent_id, data=data)

    def update_mirror(
        self, agent_id: str, changes: dict, co_signer: str
    ) -> AuditEntry:
        """Apply a change to a mirror and emit an audit entry.

        Live path: custom tool ``colony_update_mirror`` calls this. Mock
        path: deterministic audit entry with zeroed hashes. Scaffolding
        for Batch 2 — Sub-agent D implements the deep-merge-and-hash
        live write. Mock behaviour stays the same.
        """
        now = _iso_now()
        if self.mock:
            return AuditEntry(
                action="update_mirror",
                actor="system",
                co_signer=co_signer,
                pre_state_hash="0" * 16,
                post_state_hash="0" * 16,
                timestamp=now,
                rollback_window_minutes=60,
            )
        # TODO(sub-agent-D): read current YAML, deep-merge ``changes``,
        # hash pre/post, write atomically, return the AuditEntry. Also
        # append a ``mirror.updated`` event via record_event so the event
        # log stays in sync. Mirror the Claude Code substrate's logic.
        raise NotImplementedError(
            "Sub-agent D: implement update_mirror live path (match the "
            "Claude Code substrate's deep-merge-and-hash behaviour)"
        )

    # ---------------------------------------------------------------- events

    def record_event(self, event: Event) -> None:
        """Append an event to the colony event log.

        Always stamps ``event.substrate = 'managed-agents'`` so portability
        diffs against the Claude Code substrate show only the substrate
        field difference.
        """
        event.substrate = SUBSTRATE_ID
        if not event.timestamp:
            event.timestamp = _iso_now()
        # Both mock and live write to disk — the event log is ours.
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(
            {
                "type": event.type,
                "actor": event.actor,
                "payload": event.payload,
                "timestamp": event.timestamp,
                "substrate": event.substrate,
            },
            sort_keys=True,
        )
        with self.events_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    # ---------------------------------------------------------------- kb

    def read_kb(self, query: str) -> list:
        """Query the colony KB.

        Live path: custom tool ``colony_read_kb`` — adapter scans
        ``<root>/state/kb/*.md`` for matches. Mock path: empty list.
        Optional upgrade to Managed Agents memory stores
        (``memory_search``) if research-preview access is available.
        """
        if self.mock:
            return []
        # TODO(sub-agent-D): implement local kb scan mirroring the
        # Claude Code substrate's _parse_kb_doc logic. Optional memory
        # store upgrade under the same flag as write_kb.
        return []

    def write_kb(self, topic: str, content: str, provenance: str) -> None:
        """Write a topic entry into the colony KB.

        Live path: custom tool ``colony_write_kb``. Writes
        ``<root>/state/kb/<slug>.md`` with provenance frontmatter.
        """
        if self.mock:
            return
        # TODO(sub-agent-D): implement atomic write with frontmatter
        # matching the Claude Code substrate, append a ``kb.written``
        # event via record_event. Optional memory-store upgrade.
        raise NotImplementedError(
            "Sub-agent D: implement write_kb live path"
        )

    def co_sign(
        self, action_class: str, actor: str, co_signer: str
    ) -> Signature:
        """Obtain a co-signature for a given action class.

        Policy is colony-wide, not substrate-specific. The managed path
        is identical to the mock path except that it logs the decision
        as a session event for audit parity.
        """
        now = _iso_now()
        if self.mock:
            return Signature(
                action_class=action_class,
                actor=actor,
                co_signer=co_signer,
                granted=True,
                timestamp=now,
                reason="matches pre-registered policy",
            )
        # TODO(sub-agent-D): call into colony sentinel policy, log an
        # event, return Signature. Match whatever resolution the Claude
        # Code substrate uses (inline policy vs dispatch to sentinel).
        raise NotImplementedError(
            "Sub-agent D: implement co_sign live path to match the "
            "Claude Code substrate resolution"
        )

    def classify_action(self, action: dict, context: dict) -> Classification:
        """Classify blast radius and review regime.

        Delegates to the non-substrate-specific colony logic module so
        both substrates produce identical classifications.
        """
        from examples.teaching_colony.colony.logic.classifier import (
            classify_action as _classify,
        )

        return _classify(action, context)
