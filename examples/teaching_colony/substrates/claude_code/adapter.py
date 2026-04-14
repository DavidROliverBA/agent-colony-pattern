"""Claude Code substrate adapter.

Implements the eight SubstrateContract operations using local file I/O for
state (Mirrors, event log, KB) and the Anthropic Python SDK for agent dispatch.
In mock mode, agent dispatch returns deterministic canned responses so tests
can exercise the full lifecycle offline without an API key.

This adapter is a plain Python program, not something that runs inside a
Claude Code session. It is named "Claude Code substrate" because it follows
the Claude Code idiom of dispatching sub-agents by handing each one a scoped
role (its Mirror) and composing their outputs.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

try:  # preferred: fully-qualified import (pytest from repo root)
    from examples.teaching_colony.contract import (
        SubstrateContract,
        Mirror,
        Event,
        Document,
        AuditEntry,
        Signature,
        Classification,
    )
except Exception:
    try:  # sibling-relative (run.py from inside examples/teaching_colony/)
        from contract import (  # type: ignore
            SubstrateContract,
            Mirror,
            Event,
            Document,
            AuditEntry,
            Signature,
            Classification,
        )
    except Exception:  # pragma: no cover
        # Fallback lightweight stand-ins so this module imports even if
        # contract.py is missing entirely. Only runs when BOTH imports above
        # have failed — if either succeeds the real types are used.
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


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower())
    return s.strip("-") or "untitled"


def _deep_merge(base: dict, changes: dict) -> dict:
    out = dict(base) if base else {}
    for k, v in (changes or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        elif isinstance(v, list) and isinstance(out.get(k), list):
            # Append unique items (preserving order) for list-valued fields
            merged = list(out[k])
            for item in v:
                if item not in merged:
                    merged.append(item)
            out[k] = merged
        else:
            out[k] = v
    return out


def _hash_state(data: Any) -> str:
    payload = yaml.safe_dump(data, sort_keys=True, default_flow_style=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


class ClaudeCodeAdapter(SubstrateContract):
    """Claude Code substrate implementation of SubstrateContract."""

    def __init__(
        self,
        repo_root: Path,
        mock: bool = False,
        model: str = "claude-haiku-4-5-20251001",
    ) -> None:
        self.repo_root = Path(repo_root)
        self.mock = mock
        self.model = model
        self.substrate_name = "claude-code"

        self.colony_dir = self.repo_root / "colony"
        self.mirrors_dir = self.colony_dir / "mirrors"
        self.state_dir = self.repo_root / "state"
        self.kb_dir = self.state_dir / "kb"
        self.events_path = self.state_dir / "events.jsonl"

        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.kb_dir.mkdir(parents=True, exist_ok=True)

        self._client = None  # lazily constructed in non-mock dispatch

    # ---------------------------------------------------------------- dispatch

    def dispatch_agent(self, agent_id: str, input: dict) -> dict:
        mirror = self.read_mirror(agent_id)

        if self.mock:
            output = self._mock_response(agent_id, input)
        else:  # pragma: no cover - network path not exercised in tests
            output = self._real_dispatch(mirror, input)

        payload_hash = hashlib.sha256(
            json.dumps({"in": input, "out": output}, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]
        self.record_event(
            Event(
                type="dispatch.complete",
                actor=agent_id,
                payload={"hash": payload_hash, "mock": self.mock},
                timestamp=_iso_now(),
                substrate=self.substrate_name,
            )
        )
        return output

    def _real_dispatch(self, mirror: Mirror, input: dict) -> dict:  # pragma: no cover
        if self._client is None:
            from anthropic import Anthropic  # local import to keep mock offline

            self._client = Anthropic()

        data = mirror.data or {}
        identity = data.get("identity", {})
        capabilities = data.get("capabilities", [])
        purpose = data.get("purpose", "")
        trust_tier = data.get("autonomy", {}).get("trust_tier", "unknown")

        system = (
            f"You are {identity.get('name', mirror.agent_id)}, "
            f"role={identity.get('role', mirror.agent_id)}, trust_tier={trust_tier}.\n"
            f"Purpose: {purpose}\n"
            f"Capabilities: {', '.join(capabilities) if capabilities else '(none declared)'}\n"
            "Respond with a single JSON object matching the task contract."
        )
        user = json.dumps(input, default=str)

        resp = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(
            getattr(block, "text", "") for block in resp.content if getattr(block, "type", "") == "text"
        )
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}

    def _mock_response(self, agent_id: str, input: dict) -> dict:
        task = (input or {}).get("task", "")
        base = {"tokens": 0, "mock": True}

        if agent_id == "teacher" and task == "teach":
            topic = input.get("topic", "")
            if topic == "beekeeping":
                return {
                    **base,
                    "answer": (
                        "Worker bees forage for nectar and pollen within a few kilometres of the "
                        "hive; the queen is the colony's only reproductive female. "
                        "Source: beekeeping-primer.md."
                    ),
                }
            if topic == "agent-colony-pattern":
                return {
                    **base,
                    "answer": (
                        "An Agent Colony is a self-governing ecosystem of specialised agents, "
                        "much as a bee colony divides work between foragers, nurses, and a queen. "
                        "Each agent has a Mirror (its role), and capabilities evolve through "
                        "co-signed graduation. Source: agent-colony-pattern primer."
                    ),
                }
            return {**base, "answer": f"I do not yet know how to teach '{topic}'."}

        if agent_id == "librarian":
            if task == "curate":
                file_path = input.get("file", "")
                topic = _slug(Path(file_path).stem) if file_path else "unknown"
                return {
                    **base,
                    "topic": topic,
                    "content": f"Curated summary for {topic}.",
                    "cross_references": [],
                }
            if task == "compute_coverage":
                return {
                    **base,
                    "topics": {
                        "beekeeping": {"docs": 1, "cross_references": 0},
                        "agent-colony-pattern": {"docs": 5, "cross_references": 3},
                    },
                }
            if task == "propose_capability":
                return {
                    **base,
                    "agent_id": "teacher",
                    "capability": "teach_agent_colony_pattern",
                    "justification": (
                        "KB coverage for agent-colony-pattern exceeds the graduation threshold "
                        "(5 documents, 3 cross-references)."
                    ),
                }

        if agent_id == "sentinel" and task == "cosign":
            return {
                **base,
                "granted": True,
                "reason": "matches pre-registered policy",
                "action_class": input.get("action_class", ""),
                "actor": input.get("actor", ""),
            }

        return {**base, "ok": True}

    # ---------------------------------------------------------------- mirrors

    def _mirror_path(self, agent_id: str) -> Path:
        return self.mirrors_dir / f"{agent_id}.yaml"

    def read_mirror(self, agent_id: str) -> Mirror:
        path = self._mirror_path(agent_id)
        if not path.exists():
            # Also try "<agent_id>-agent.yaml" for the teaching colony's file naming
            alt = self.mirrors_dir / f"{agent_id}-agent.yaml"
            if alt.exists():
                path = alt
            else:
                return Mirror(agent_id=agent_id, data={})
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return Mirror(agent_id=agent_id, data=data)

    def update_mirror(self, agent_id: str, changes: dict, co_signer: str) -> AuditEntry:
        path = self._mirror_path(agent_id)
        if not path.exists():
            alt = self.mirrors_dir / f"{agent_id}-agent.yaml"
            if alt.exists():
                path = alt
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("", encoding="utf-8")

        existing = {}
        if path.exists() and path.stat().st_size > 0:
            with path.open("r", encoding="utf-8") as f:
                existing = yaml.safe_load(f) or {}

        pre_hash = _hash_state(existing)
        merged = _deep_merge(existing, changes)

        audit = AuditEntry(
            action="update_mirror",
            actor=agent_id,
            co_signer=co_signer,
            pre_state_hash=pre_hash,
            post_state_hash="",  # filled in below once post-state is finalised
            timestamp=_iso_now(),
            rollback_window_minutes=60,
        )

        autonomy = merged.setdefault("autonomy", {})
        evolution_log = autonomy.setdefault("evolution_log", [])
        evolution_log.append(
            {
                "action": audit.action,
                "actor": audit.actor,
                "co_signer": audit.co_signer,
                "pre_state_hash": audit.pre_state_hash,
                "timestamp": audit.timestamp,
            }
        )

        post_hash = _hash_state(merged)
        audit.post_state_hash = post_hash
        evolution_log[-1]["post_state_hash"] = post_hash

        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(merged, f, sort_keys=False, default_flow_style=False)

        self.record_event(
            Event(
                type="mirror.updated",
                actor=agent_id,
                payload={
                    "co_signer": co_signer,
                    "pre_state_hash": pre_hash,
                    "post_state_hash": post_hash,
                },
                timestamp=audit.timestamp,
                substrate=self.substrate_name,
            )
        )
        return audit

    # ---------------------------------------------------------------- events

    def record_event(self, event: Event) -> None:
        if not event.timestamp:
            event.timestamp = _iso_now()
        if not event.substrate:
            event.substrate = self.substrate_name
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        with self.events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), default=str) + "\n")

    # ---------------------------------------------------------------- kb

    def read_kb(self, query: str) -> list:
        results: list = []
        if not self.kb_dir.exists():
            return results
        terms = [t for t in re.split(r"\W+", (query or "").lower()) if t]
        for md in sorted(self.kb_dir.glob("*.md")):
            raw = md.read_text(encoding="utf-8")
            topic, content, provenance, xrefs = self._parse_kb_doc(raw)
            haystack = f"{topic}\n{content}".lower()
            if not terms or any(t in haystack for t in terms):
                results.append(
                    Document(
                        path=str(md),
                        topic=topic or md.stem,
                        content=content,
                        provenance=provenance,
                        cross_references=xrefs,
                    )
                )
        return results

    def write_kb(self, topic: str, content: str, provenance: str) -> None:
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        path = self.kb_dir / f"{_slug(topic)}.md"
        frontmatter = {
            "topic": topic,
            "provenance": provenance,
            "written_at": _iso_now(),
            "substrate": self.substrate_name,
        }
        body = (
            "---\n"
            + yaml.safe_dump(frontmatter, sort_keys=False, default_flow_style=False)
            + "---\n\n"
            + content
            + "\n"
        )
        path.write_text(body, encoding="utf-8")
        self.record_event(
            Event(
                type="kb.written",
                actor="librarian",
                payload={"topic": topic, "path": str(path)},
                timestamp=_iso_now(),
                substrate=self.substrate_name,
            )
        )

    def _parse_kb_doc(self, raw: str) -> tuple[str, str, str, list]:
        topic = ""
        provenance = ""
        xrefs: list = []
        content = raw
        if raw.startswith("---\n"):
            end = raw.find("\n---", 4)
            if end != -1:
                fm_text = raw[4:end]
                content = raw[end + 4 :].lstrip("\n")
                try:
                    fm = yaml.safe_load(fm_text) or {}
                    topic = fm.get("topic", "") or ""
                    provenance = fm.get("provenance", "") or ""
                    xrefs = fm.get("cross_references", []) or []
                except yaml.YAMLError:
                    pass
        return topic, content, provenance, xrefs

    # ---------------------------------------------------------------- co-sign

    def co_sign(self, action_class: str, actor: str, co_signer: str) -> Signature:
        if self.mock:
            sig = Signature(
                action_class=action_class,
                actor=actor,
                co_signer=co_signer,
                granted=True,
                timestamp=_iso_now(),
                reason="mock: matches pre-registered policy",
            )
        else:  # pragma: no cover
            resp = self.dispatch_agent(
                co_signer,
                {"task": "cosign", "action_class": action_class, "actor": actor},
            )
            sig = Signature(
                action_class=action_class,
                actor=actor,
                co_signer=co_signer,
                granted=bool(resp.get("granted")),
                timestamp=_iso_now(),
                reason=str(resp.get("reason", "")),
            )

        self.record_event(
            Event(
                type="cosign.granted" if sig.granted else "cosign.denied",
                actor=co_signer,
                payload={
                    "action_class": action_class,
                    "subject_actor": actor,
                    "reason": sig.reason,
                },
                timestamp=sig.timestamp,
                substrate=self.substrate_name,
            )
        )
        return sig

    # ---------------------------------------------------------------- classify

    def classify_action(self, action: dict, context: dict) -> Classification:
        try:
            from examples.teaching_colony.colony.logic.classifier import (
                classify_action as _classify,
            )

            return _classify(action, context)
        except Exception:
            # Fallback: return a safe default so the adapter can still run.
            return Classification(
                blast_radius=action.get("blast_radius", "unknown"),
                review_regime=action.get("review_regime", "human-in-the-loop"),
                action_class=action.get("action_class", "unknown"),
                actor_trust_tier=context.get("actor_trust_tier", "unknown"),
            )
