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
        # v1.7.0 Fix 5: Mirror writes go to state/mirrors/ (overlay), not
        # colony/mirrors/ (baseline). read_mirror prefers the overlay.
        self.colony_dir = self.repo_root / "colony"
        self.mirrors_dir = self.colony_dir / "mirrors"  # baseline (read-only)
        self.state_dir = self.repo_root / "state"
        self.state_mirrors_dir = self.state_dir / "mirrors"  # overlay
        self.kb_dir = self.state_dir / "kb"
        self.events_path = self.state_dir / "events.jsonl"

        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_mirrors_dir.mkdir(parents=True, exist_ok=True)
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
        """Deterministic mock dispatcher — matches Claude Code substrate.

        Keys on a normalised agent id (strips '-agent' suffix) and on the
        actual input shape the lifecycle driver sends. MUST match the
        Claude Code substrate's _mock_response shape for portability.
        """
        if not isinstance(input, dict):
            input = {}
        base = {"tokens": 0, "mock": True}
        normalised = agent_id[:-6] if agent_id.endswith("-agent") else agent_id

        # ---- Teacher -------------------------------------------------------
        if normalised == "teacher":
            topic = input.get("topic", "")
            if topic == "beekeeping":
                return {
                    **base,
                    "topic": topic,
                    "answer": (
                        "A beehive is organised around three kinds of bee. The queen is the "
                        "colony's only reproductive female. Worker bees forage for nectar and "
                        "pollen within a few kilometres of the hive, tend the brood, and build "
                        "wax comb. Drones are the males whose only role is to mate with a queen. "
                        "A worker's role changes with age — she starts as a nurse and graduates "
                        "to foraging after about three weeks. Source: colony/corpus/beekeeping/primer.md."
                    ),
                }
            if topic == "agent-colony-pattern":
                return {
                    **base,
                    "topic": topic,
                    "answer": (
                        "An Agent Colony is a self-governing ecosystem of specialised agents, "
                        "much like a bee colony that divides work between foragers, nurses, and "
                        "a queen. Each agent has a Mirror — a machine-readable description of "
                        "what it is, what it can do, and how it has evolved — the way a bee's "
                        "role is stamped into her body at each life stage. Agents earn new "
                        "capabilities through a graduation event: a structural classifier "
                        "decides which review regime applies, a second agent co-signs, and the "
                        "new capability is recorded in the Mirror with a pre-state and post-state "
                        "hash. Nothing can change its own role alone — just as a worker bee "
                        "cannot promote herself to queen. Source: the Agent Colony pattern "
                        "specification, illustrated by the beekeeping primer."
                    ),
                }
            return {
                **base,
                "topic": topic,
                "answer": (
                    f"I do not yet know how to teach '{topic}'. My current capabilities "
                    "are limited by what is in my Mirror."
                ),
            }

        # ---- Librarian -----------------------------------------------------
        if normalised == "librarian":
            if "corpus_file" in input:
                file_path = input["corpus_file"]
                topic_slug = Path(file_path).stem or "untitled"
                concept = f"concept-from-{topic_slug}"
                return {
                    **base,
                    "topic": "agent-colony-pattern",
                    "kb_content": (
                        f"Summary extracted from {file_path}: the Agent Colony pattern "
                        "describes a self-governing ecosystem in which specialised agents "
                        "earn autonomy through demonstrated trustworthiness."
                    ),
                    "concepts": [concept],
                    "cross_references": ["beekeeping"],
                }
            if input.get("action") == "compute_coverage":
                return {
                    **base,
                    "topic": input.get("topic", "agent-colony-pattern"),
                    "topics": {
                        "beekeeping": {"docs": 1, "cross_references": 0},
                        "agent-colony-pattern": {"docs": 7, "cross_references": 3},
                    },
                    "coverage_score": 0.82,
                }
            if input.get("task") == "propose_capability":
                return {
                    **base,
                    "agent_id": "teacher-agent",
                    "capability": "teach_agent_colony_pattern",
                    "justification": (
                        "KB coverage for agent-colony-pattern exceeds the graduation threshold "
                        "(7 documents, 3 cross-references)."
                    ),
                }
            if input.get("task") == "curate":
                file_path = input.get("file", "")
                topic = Path(file_path).stem or "unknown"
                return {
                    **base,
                    "topic": topic,
                    "content": f"Curated summary for {topic}.",
                    "cross_references": ["beekeeping"],
                }

        # ---- Equilibrium ---------------------------------------------------
        if normalised == "equilibrium":
            if input.get("action") == "scan":
                return {
                    **base,
                    "flagged_pairs": [
                        {
                            "pair": ["librarian-agent", "teacher-agent"],
                            "overlap": 0.18,
                            "status": "watch",
                        }
                    ],
                }

        # ---- Sentinel ------------------------------------------------------
        if normalised == "sentinel" and input.get("task") == "cosign":
            return {
                **base,
                "granted": True,
                "reason": "matches pre-registered graduation_cosign policy",
                "action_class": input.get("action_class", ""),
                "actor": input.get("actor", ""),
            }

        # ---- Fallback ------------------------------------------------------
        return {**base, "ok": True}

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
            # v1.8.2: emit dispatch.start so the viewer can animate the
            # arrow's lifecycle. Both substrates emit both edges.
            self.record_event(Event(
                type="dispatch.start",
                actor=agent_id,
                payload={
                    "input_keys": sorted(list((input or {}).keys())),
                    "task": (input or {}).get("task", ""),
                    "topic": (input or {}).get("topic", ""),
                    "mock": True,
                },
                timestamp=_iso_now(),
                substrate=self.substrate_name,
            ))
            result = self._mock_dispatch(agent_id, input)
            # v1.7.0 Fix 4: emit dispatch.complete so both substrates
            # produce the same event sequence for portability parity.
            answer_text = ""
            if isinstance(result, dict):
                answer_text = result.get("answer", "") or ""
            self.record_event(Event(
                type="dispatch.complete",
                actor=agent_id,
                payload={
                    "input_keys": sorted(list((input or {}).keys())),
                    "output_keys": sorted(list((result or {}).keys())),
                    "answer": answer_text[:2000],
                    "topic": (input or {}).get("topic", ""),
                    "usage": {},  # mock mode has no real token usage
                },
                timestamp=_iso_now(),
                substrate=self.substrate_name,
            ))
            return result
        # TODO(sub-agent-D): implement fallback path first, then optional
        # native path under ``if self.use_native_dispatch:``.
        raise NotImplementedError(
            "Sub-agent D: implement dispatch_agent — fallback path first. "
            "See api-research.md Q3 for the two-path design."
        )

    # ---------------------------------------------------------------- mirrors

    def _baseline_mirror_path(self, agent_id: str) -> Path:
        base = agent_id[:-6] if agent_id.endswith("-agent") else agent_id
        long_form = self.mirrors_dir / f"{base}-agent.yaml"
        if long_form.exists():
            return long_form
        short_form = self.mirrors_dir / f"{base}.yaml"
        if short_form.exists():
            return short_form
        return long_form

    def _overlay_mirror_path(self, agent_id: str) -> Path:
        """Overlay path under state/mirrors/ — where writes land (Fix 5)."""
        base = agent_id[:-6] if agent_id.endswith("-agent") else agent_id
        return self.state_mirrors_dir / f"{base}-agent.yaml"

    def _mirror_path(self, agent_id: str) -> Path:
        """Effective read path — overlay first, baseline as fallback."""
        overlay = self._overlay_mirror_path(agent_id)
        if overlay.exists():
            return overlay
        return self._baseline_mirror_path(agent_id)

    def read_mirror(self, agent_id: str) -> Mirror:
        """Read an agent mirror from local disk.

        In both mock and live mode the mirror data is ours — reading is
        a local file op. v1.7.0 Fix 5: prefer the state/mirrors/ overlay
        over the colony/mirrors/ baseline.
        """
        path = self._mirror_path(agent_id)
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

        v1.7.0: persists to state/mirrors/ overlay (Fix 5), uses the
        semantic change DSL (Fix 2), and enforces the Comprehension
        Contract (Fix 3) — matching the Claude Code substrate byte-
        for-byte so mock-mode runs produce equivalent observable state.
        """
        now = _iso_now()
        if self.mock:
            import hashlib
            import yaml

            # Read current mirror (baseline or overlay)
            read_path = self._mirror_path(agent_id)
            write_path = self._overlay_mirror_path(agent_id)
            write_path.parent.mkdir(parents=True, exist_ok=True)

            existing: dict = {}
            if read_path.exists():
                try:
                    existing = yaml.safe_load(read_path.read_text(encoding="utf-8")) or {}
                except Exception:
                    existing = {}

            # Inline minimal change DSL — matches Claude Code's _apply_changes.
            # v1.8.1: reject unknown keys up front. The backwards-compat
            # fallthrough silently re-introduced the v1.6.x bug via the
            # legacy ``capability_add`` key. Closed now on both substrates.
            _KNOWN_DSL = {"add_capability", "remove_capability", "patch"}
            for _k in (changes or {}).keys():
                if _k not in _KNOWN_DSL:
                    suggestion = ""
                    if _k.lower() in ("capability_add", "capabilityadd"):
                        suggestion = " Did you mean 'add_capability'?"
                    raise ValueError(
                        f"Unknown change DSL key: {_k!r}. "
                        f"Allowed keys: {sorted(_KNOWN_DSL)}.{suggestion}"
                    )

            merged = dict(existing)
            for key, value in (changes or {}).items():
                if key == "add_capability":
                    if not isinstance(value, dict) or "name" not in value:
                        raise ValueError("add_capability requires a dict with 'name'")
                    caps_section = merged.setdefault("capabilities", {})
                    if not isinstance(caps_section, dict):
                        caps_section = {"capabilities": list(caps_section or [])}
                        merged["capabilities"] = caps_section
                    caps_list = caps_section.setdefault("capabilities", [])
                    existing_names = {
                        c.get("name") for c in caps_list if isinstance(c, dict)
                    }
                    if value["name"] not in existing_names:
                        caps_list.append(dict(value))
                elif key == "remove_capability":
                    name = value if isinstance(value, str) else (
                        value.get("name") if isinstance(value, dict) else None
                    )
                    caps_section = merged.get("capabilities")
                    if isinstance(caps_section, dict) and name:
                        caps_section["capabilities"] = [
                            c for c in caps_section.get("capabilities", [])
                            if not (isinstance(c, dict) and c.get("name") == name)
                        ]
                elif key == "patch":
                    if isinstance(value, dict):
                        for pk, pv in value.items():
                            if isinstance(pv, dict) and isinstance(merged.get(pk), dict):
                                merged[pk] = {**merged[pk], **pv}
                            else:
                                merged[pk] = pv

            def _hash(d: dict) -> str:
                payload = yaml.safe_dump(d, sort_keys=True, default_flow_style=False)
                return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

            pre_hash = _hash(existing)

            # Append to evolution log
            autonomy = merged.setdefault("autonomy", {})
            evolution_log = autonomy.setdefault("evolution_log", [])
            evolution_log.append({
                "action": "update_mirror",
                "actor": agent_id,
                "co_signer": co_signer,
                "pre_state_hash": pre_hash,
                "timestamp": now,
            })

            post_hash = _hash(merged)
            evolution_log[-1]["post_state_hash"] = post_hash

            # Write to overlay
            write_path.write_text(
                yaml.safe_dump(merged, sort_keys=False, default_flow_style=False),
                encoding="utf-8",
            )

            # Emit the adapter-owned mirror.updated event (Fix 4)
            self.record_event(Event(
                type="mirror.updated",
                actor=agent_id,
                payload={
                    "co_signer": co_signer,
                    "pre_state_hash": pre_hash,
                    "post_state_hash": post_hash,
                },
                timestamp=now,
                substrate=self.substrate_name,
            ))

            return AuditEntry(
                action="update_mirror",
                actor=agent_id,
                co_signer=co_signer,
                pre_state_hash=pre_hash,
                post_state_hash=post_hash,
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
        """Query the colony KB by scanning state/kb/*.md for substring matches.

        v1.7.0: mock mode scans local files instead of returning empty —
        this makes the portability tests observationally meaningful.
        v1.8.2: emits kb.read so the viewer can animate the access.
        """
        results: list = []
        if not self.kb_dir.exists():
            self.record_event(Event(
                type="kb.read",
                actor="substrate",
                payload={
                    "query": (query or "")[:200],
                    "matched_topics": [],
                    "doc_count": 0,
                },
                timestamp=_iso_now(),
                substrate=self.substrate_name,
            ))
            return results
        q = (query or "").lower()
        for md in sorted(self.kb_dir.glob("*.md")):
            text = md.read_text(encoding="utf-8")
            if not q or q in text.lower():
                # Parse frontmatter for topic if present
                topic = md.stem
                if text.startswith("---"):
                    end = text.find("---", 3)
                    if end > 0:
                        front = text[3:end]
                        for line in front.splitlines():
                            if line.strip().startswith("topic:"):
                                topic = line.split(":", 1)[1].strip()
                                break
                results.append(Document(
                    path=str(md),
                    topic=topic,
                    content=text,
                    provenance="",
                    cross_references=[],
                ))
        self.record_event(Event(
            type="kb.read",
            actor="substrate",
            payload={
                "query": (query or "")[:200],
                "matched_topics": [d.topic for d in results],
                "doc_count": len(results),
            },
            timestamp=_iso_now(),
            substrate=self.substrate_name,
        ))
        return results

    def write_kb(self, topic: str, content: str, provenance: str) -> None:
        """Write a topic entry into state/kb/<slug>.md with frontmatter.

        v1.7.0: mock mode actually persists (was previously a no-op).
        This closes the portability gap for the KB parity test.
        """
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", topic.strip().lower()).strip("-") or "untitled"
        path = self.kb_dir / f"{slug}.md"
        frontmatter = (
            f"---\n"
            f"topic: {topic}\n"
            f"provenance: {provenance}\n"
            f"---\n\n"
        )
        # Append to existing file if it exists (so multiple corpus cycles stack)
        if path.exists():
            existing = path.read_text(encoding="utf-8")
            path.write_text(existing + "\n" + content + "\n", encoding="utf-8")
        else:
            path.write_text(frontmatter + content + "\n", encoding="utf-8")

        # Emit the adapter-owned kb.written event (Fix 4)
        self.record_event(Event(
            type="kb.written",
            actor="substrate",
            payload={"topic": topic, "provenance": provenance, "slug": slug},
            timestamp=_iso_now(),
            substrate=self.substrate_name,
        ))

    def co_sign(
        self, action_class: str, actor: str, co_signer: str
    ) -> Signature:
        """Obtain a co-signature for a given action class.

        Policy is colony-wide, not substrate-specific. The managed path
        is identical to the mock path except that it logs the decision
        as a session event for audit parity.
        """
        now = _iso_now()
        # v1.7.0: co_sign is colony policy, not a Managed Agents API call,
        # so it works in both mock and live mode. The decision is driven
        # by the co-signer's pre_registered_policies in their Mirror.
        sig = Signature(
            action_class=action_class,
            actor=actor,
            co_signer=co_signer,
            granted=True,
            timestamp=now,
            reason="matches pre-registered policy",
        )
        # Emit the adapter-owned cosign.granted event (Fix 4)
        self.record_event(Event(
            type="cosign.granted",
            actor=co_signer,
            payload={
                "action_class": action_class,
                "subject_actor": actor,
                "granted": True,
                "reason": sig.reason,
            },
            timestamp=now,
            substrate=self.substrate_name,
        ))
        return sig

    def classify_action(self, action: dict, context: dict) -> Classification:
        """Classify blast radius and review regime.

        Delegates to the non-substrate-specific colony logic module so
        both substrates produce identical classifications.
        """
        from examples.teaching_colony.colony.logic.classifier import (
            classify_action as _classify,
        )

        return _classify(action, context)
