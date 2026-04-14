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


#: The only keys _apply_changes accepts at the top level. Anything else
#: raises — v1.8.1 closure of the DSL dual-key bypass flagged in review.
#: Prior v1.7/v1.8 code accepted unknown keys and fell through to a
#: backwards-compat deep-merge, which silently turned the legacy
#: ``capability_add`` key (the exact v1.6.x bug the DSL was meant to kill)
#: into a literal YAML write that bypassed §7 enforcement. Closed now.
KNOWN_DSL_KEYS: set[str] = {"add_capability", "remove_capability", "patch"}


def _apply_changes(mirror_data: dict, changes: dict) -> dict:
    """Apply a semantic change DSL to a Mirror dict.

    The DSL keys are interpreted as instructions, NOT as literal YAML keys:

    - ``add_capability``: {"name": str, ...}  appends to
      ``capabilities.capabilities[]`` (skipping if a capability with the
      same name already exists).
    - ``remove_capability``: "<name>"  removes a capability by name from
      ``capabilities.capabilities[]``.
    - ``patch``: {arbitrary subset}  deep-merges the patch onto the mirror
      (the old v1.6.x behaviour, kept only under this explicit key).

    **Any other top-level key raises ValueError.** v1.7/v1.8 accepted
    unknown keys and silently deep-merged them for "backwards
    compatibility", which re-introduced the v1.6.x bug: a caller passing
    ``capability_add`` (legacy name) bypassed the DSL entirely and the
    new key ended up as a literal top-level YAML field in the Mirror. The
    Comprehension Contract enforcement ran successfully against a
    ``mirror_patch`` classification instead of ``mirror_capability_add``,
    the forbidden-list keyword match missed, and the demo reverted to
    its v1.6.x failure mode. v1.8.1 closes this by rejecting unknown
    DSL keys at the gate. Callers must migrate to the correct key names.

    Returns a new dict — mirror_data is not mutated in place.
    """
    out = dict(mirror_data)  # shallow; _deep_merge will do the deep work

    # v1.8.1: reject unknown DSL keys up front. No backwards-compat
    # fallthrough. See KNOWN_DSL_KEYS for the allowed set.
    for key in (changes or {}).keys():
        if key not in KNOWN_DSL_KEYS:
            suggestion = ""
            if key.lower() in ("capability_add", "capabilityadd", "capabilities_add"):
                suggestion = " Did you mean 'add_capability'?"
            elif key.lower() in ("capability_remove", "capabilityremove", "capabilities_remove"):
                suggestion = " Did you mean 'remove_capability'?"
            raise ValueError(
                f"Unknown change DSL key: {key!r}. "
                f"Allowed keys: {sorted(KNOWN_DSL_KEYS)}.{suggestion}"
            )

    for key, value in (changes or {}).items():
        if key == "add_capability":
            if not isinstance(value, dict) or "name" not in value:
                raise ValueError(
                    "add_capability requires a dict with at least a 'name' field"
                )
            caps_section = out.setdefault("capabilities", {})
            if not isinstance(caps_section, dict):
                # Mirror's capabilities field was a flat list; coerce to dict form.
                caps_section = {"capabilities": list(caps_section or [])}
                out["capabilities"] = caps_section
            caps_list = caps_section.setdefault("capabilities", [])
            # Skip if a capability with the same name already exists
            existing_names = {
                c.get("name") for c in caps_list if isinstance(c, dict)
            }
            if value["name"] not in existing_names:
                caps_list.append(dict(value))

        elif key == "remove_capability":
            name = value if isinstance(value, str) else value.get("name") if isinstance(value, dict) else None
            if not name:
                raise ValueError(
                    "remove_capability requires a capability name string"
                )
            caps_section = out.get("capabilities")
            if isinstance(caps_section, dict):
                caps_list = caps_section.get("capabilities", [])
                caps_section["capabilities"] = [
                    c for c in caps_list
                    if not (isinstance(c, dict) and c.get("name") == name)
                ]

        elif key == "patch":
            if not isinstance(value, dict):
                raise ValueError("patch requires a dict value")
            out = _deep_merge(out, value)

    return out


#: v1.8.0 model tiering map — Sonnet for reasoning agents, Haiku for supervisors.
#: Teacher and Librarian do the work that needs real pedagogical quality; the
#: four L1/L2 agents return small structured JSON decisions and don't need
#: the more expensive model. See the v1.8 spec for the cost rationale.
AGENT_MODELS: dict[str, str] = {
    "teacher-agent":     "claude-sonnet-4-6",
    "librarian-agent":   "claude-sonnet-4-6",
    "registry-agent":    "claude-haiku-4-5-20251001",
    "chronicler-agent":  "claude-haiku-4-5-20251001",
    "equilibrium-agent": "claude-haiku-4-5-20251001",
    "sentinel-agent":    "claude-haiku-4-5-20251001",
}

#: Supervisory agents return strict JSON; Teacher/Librarian return prose.
PROSE_AGENTS: set[str] = {"teacher-agent", "librarian-agent"}


class ClaudeCodeAdapter(SubstrateContract):
    """Claude Code substrate implementation of SubstrateContract."""

    def __init__(
        self,
        repo_root: Path,
        mock: bool = False,
        model: str = "claude-haiku-4-5-20251001",
        budget: object = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.mock = mock
        self.model = model
        self.substrate_name = "claude-code"
        self.budget = budget  # optional Budget — None in mock/offline tests

        self.colony_dir = self.repo_root / "colony"
        self.mirrors_dir = self.colony_dir / "mirrors"  # baseline (read-only)
        self.state_dir = self.repo_root / "state"
        self.state_mirrors_dir = self.state_dir / "mirrors"  # overlay (writes)
        self.kb_dir = self.state_dir / "kb"
        self.events_path = self.state_dir / "events.jsonl"

        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_mirrors_dir.mkdir(parents=True, exist_ok=True)
        self.kb_dir.mkdir(parents=True, exist_ok=True)

        self._client = None  # lazily constructed in non-mock dispatch
        self.last_response_usage: dict | None = None  # exposed for tests

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

    # ---------------------------------------------------------------- system prompts
    #
    # v1.8.0 splits the system prompt style by agent role. Teacher and
    # Librarian get a prose-friendly prompt because their outputs ARE the
    # user-facing product of the colony. Registry, Chronicler, Equilibrium,
    # and Sentinel get JSON-strict prompts because their outputs are
    # structured decisions consumed by other agents or the driver.

    def _build_system_prompt(self, mirror: Mirror) -> str:
        data = mirror.data or {}
        identity = data.get("identity", {}) or {}
        purpose = identity.get("purpose", "") or data.get("purpose", "")
        caps_section = data.get("capabilities", {})
        if isinstance(caps_section, dict):
            caps_list = caps_section.get("capabilities", []) or []
        else:
            caps_list = list(caps_section) if caps_section else []

        def _cap_line(c):
            if isinstance(c, dict):
                return f"  - {c.get('name', '?')}: {c.get('description', '')}"
            return f"  - {c}"

        caps_text = "\n".join(_cap_line(c) for c in caps_list) or "  (none declared)"

        cc = data.get("comprehension_contract", {}) or {}
        trust_tier = cc.get("trust_tier", "Observing")

        # Discover current KB topics so agents know what the colony has.
        kb_topics: list[str] = []
        if self.kb_dir.exists():
            for md in sorted(self.kb_dir.glob("*.md")):
                kb_topics.append(md.stem)
        kb_text = ", ".join(kb_topics) or "(none)"

        header = (
            f"You are {identity.get('name', mirror.agent_id)}, "
            f"a {mirror.agent_id} in an Agent Colony.\n\n"
            f"Your purpose: {purpose}\n\n"
            f"Your capabilities:\n{caps_text}\n\n"
            f"Your trust tier: {trust_tier}\n\n"
            f"The colony knowledge base currently contains entries on: {kb_text}\n\n"
        )

        if mirror.agent_id in PROSE_AGENTS:
            tail = (
                "You will receive a task request as JSON. Respond with a "
                "structured answer in the format requested. If the task asks "
                "you to teach a topic you do not yet have a capability for, "
                "say so explicitly and suggest that the user run "
                "`research \"<topic>\" from <url>` (a feature coming in v1.9)."
            )
        else:
            tail = (
                "You will receive a request as JSON. You MUST respond with "
                "ONLY a valid JSON object matching the schema appropriate to "
                "your role. No prose. No markdown fences. No explanation. If "
                "the request is ambiguous or malformed, return "
                '{"error": "...", "reason": "..."}.'
            )

        return header + tail

    def _real_dispatch(self, mirror: Mirror, input: dict) -> dict:  # pragma: no cover
        """Live-mode dispatch: real Claude API call with prompt caching and
        model tiering.

        This path is exercised by the live-mode test suite and by the REPL.
        It is not executed in the default mock-mode tests (hence the pragma).
        """
        if self._client is None:
            from anthropic import Anthropic  # local import to keep mock offline

            self._client = Anthropic()

        system_prompt = self._build_system_prompt(mirror)
        model = AGENT_MODELS.get(mirror.agent_id, self.model)

        # Anthropic prompt caching: mark the system block as ephemeral so
        # repeat dispatches of the SAME agent pay only ~10% of the
        # system-prompt cost. The cache lives ~5 minutes.
        system_blocks = [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]

        user_message = json.dumps(input, default=str)

        resp = self._client.messages.create(
            model=model,
            max_tokens=2048,
            system=system_blocks,
            messages=[{"role": "user", "content": user_message}],
        )

        # Record the usage block for tests and the REPL budget display.
        usage = getattr(resp, "usage", None)
        if usage is not None:
            self.last_response_usage = {
                "input_tokens": getattr(usage, "input_tokens", 0) or 0,
                "output_tokens": getattr(usage, "output_tokens", 0) or 0,
                "cache_creation_input_tokens": getattr(
                    usage, "cache_creation_input_tokens", 0
                ) or 0,
                "cache_read_input_tokens": getattr(
                    usage, "cache_read_input_tokens", 0
                ) or 0,
                "model": model,
            }
            # Accumulate into the budget if one is attached.
            if self.budget is not None:
                try:
                    self.budget.record(usage)
                except Exception:
                    pass  # budget is best-effort; never break dispatch

        # Extract the text response.
        text = "".join(
            getattr(block, "text", "")
            for block in resp.content
            if getattr(block, "type", "") == "text"
        )

        # For prose agents, return the answer directly inside a small dict.
        # For JSON agents, try to parse; retry once with a reminder if it
        # fails, fall back to a structured error.
        if mirror.agent_id in PROSE_AGENTS:
            return {
                "answer": text.strip(),
                "topic": input.get("topic", ""),
                "tokens": self.last_response_usage.get("input_tokens", 0)
                + self.last_response_usage.get("output_tokens", 0)
                if self.last_response_usage
                else 0,
                "mock": False,
                "model": model,
            }

        # JSON-strict agents: try to parse
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # One retry with an explicit reminder
            retry_msg = (
                "Your previous response was not valid JSON. "
                "Return ONLY a JSON object, no prose, no markdown fences."
            )
            resp2 = self._client.messages.create(
                model=model,
                max_tokens=1024,
                system=system_blocks,
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": text},
                    {"role": "user", "content": retry_msg},
                ],
            )
            usage2 = getattr(resp2, "usage", None)
            if usage2 is not None and self.budget is not None:
                try:
                    self.budget.record(usage2)
                except Exception:
                    pass
            text2 = "".join(
                getattr(block, "text", "")
                for block in resp2.content
                if getattr(block, "type", "") == "text"
            )
            try:
                return json.loads(text2.strip())
            except json.JSONDecodeError:
                return {
                    "error": "malformed_response",
                    "reason": "agent did not return valid JSON after retry",
                    "raw": text2[:500],
                }

    def _mock_response(self, agent_id: str, input: dict) -> dict:
        """Deterministic mock dispatcher.

        Keys on a normalised agent id (the '-agent' suffix is stripped so that
        driver calls like 'teacher-agent' and direct test calls like 'teacher'
        both match) and on the actual input shape the lifecycle driver sends:

        - Teacher:   {topic, question}                 — teach a topic
        - Librarian: {corpus_file: <path>}             — curate a file
        - Librarian: {action: 'compute_coverage', ...} — report coverage
        - Equilibrium: {action: 'scan'}                — overlap scan
        - Sentinel:  {task: 'cosign', action_class, actor} — co-sign decision

        Returns canned responses that contain the observable strings the
        walkthrough README promises ('worker' for beekeeping, 'Mirror' for
        the Agent Colony pattern turn) so end-to-end tests can assert
        against them.
        """
        if not isinstance(input, dict):
            input = {}
        base = {"tokens": 0, "mock": True}

        # Normalise the agent id — strip the '-agent' suffix so 'teacher'
        # and 'teacher-agent' map to the same branch.
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
            # Corpus reading (driver sends {corpus_file: <path>})
            if "corpus_file" in input:
                file_path = input["corpus_file"]
                topic_slug = _slug(Path(file_path).stem) if file_path else "unknown"
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
            # Coverage check (driver sends {action: 'compute_coverage', topic})
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
            # Capability proposal (may be called from tests)
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
            # Legacy curate task (kept so test_portability.py still fires)
            if input.get("task") == "curate":
                file_path = input.get("file", "")
                topic = _slug(Path(file_path).stem) if file_path else "unknown"
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

    # ---------------------------------------------------------------- mirrors

    def _baseline_mirror_path(self, agent_id: str) -> Path:
        """Find the baseline (read-only) Mirror file in colony/mirrors/.

        Accepts either `teacher` or `teacher-agent` — canonicalises to the
        long form. Used as the fallback source when no state/mirrors/ overlay
        exists yet.
        """
        base = agent_id[:-6] if agent_id.endswith("-agent") else agent_id
        long_form = self.mirrors_dir / f"{base}-agent.yaml"
        if long_form.exists():
            return long_form
        short_form = self.mirrors_dir / f"{base}.yaml"
        if short_form.exists():
            return short_form
        return long_form  # doesn't exist — used as write target signal

    def _overlay_mirror_path(self, agent_id: str) -> Path:
        """The state/mirrors/ overlay file for an agent.

        v1.7.0 Fix 5 — all writes go to state/mirrors/, never to
        colony/mirrors/. Reads prefer the overlay if it exists and fall
        back to the baseline.
        """
        base = agent_id[:-6] if agent_id.endswith("-agent") else agent_id
        return self.state_mirrors_dir / f"{base}-agent.yaml"

    def _mirror_path(self, agent_id: str) -> Path:
        """Legacy single-file accessor — kept for adapter-internal callers
        that want the effective read path. Always prefers the overlay.
        """
        overlay = self._overlay_mirror_path(agent_id)
        if overlay.exists():
            return overlay
        return self._baseline_mirror_path(agent_id)

    def read_mirror(self, agent_id: str) -> Mirror:
        path = self._mirror_path(agent_id)
        if not path.exists():
            return Mirror(agent_id=agent_id, data={})
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return Mirror(agent_id=agent_id, data=data)

    _BLAST_RADIUS_ORDER = {
        "Local": 0,
        "Inter-agent": 1,
        "Colony-wide": 2,
        "Boundary-crossing": 3,
    }

    def _change_action_class(self, changes: dict) -> str:
        """Infer the action class from a change dict.

        Semantic DSL keys map directly; legacy literal patches fall back
        to 'mirror_patch' which gets the default blast radius from the
        classifier table.
        """
        if "add_capability" in changes:
            return "mirror_capability_add"
        if "remove_capability" in changes:
            return "mirror_capability_remove"
        if "patch" in changes:
            return "mirror_patch"
        return "mirror_patch"

    def _change_describes(self, changes: dict) -> str:
        """Build a short human-readable description of a change dict.

        Used to match entries in self_evolution_scope.forbidden, which are
        themselves plain English strings.
        """
        if "add_capability" in changes:
            name = changes["add_capability"].get("name", "<unknown>")
            return f"Add new teaching topic {name}"
        if "remove_capability" in changes:
            name = changes["remove_capability"] if isinstance(
                changes["remove_capability"], str
            ) else changes["remove_capability"].get("name", "<unknown>")
            return f"Remove teaching topic {name}"
        return f"Patch mirror with keys: {sorted(changes.keys())}"

    def _enforce_contract(
        self,
        agent_id: str,
        target_mirror: dict,
        changes: dict,
        co_signer: str,
    ) -> None:
        """Enforce §7 Comprehension Contract clauses before any Mirror write.

        Raises ContractViolation subclass if any check fails. All four
        checks must pass before update_mirror proceeds to hash, merge, and
        write. This is the v1.7.0 fix for the external review's Finding 3
        ("the Comprehension Contract is not enforced").
        """
        # Late import so the adapter module stays importable even if
        # colony.logic.exceptions moves.
        try:
            from examples.teaching_colony.colony.logic.exceptions import (  # type: ignore
                BlastRadiusViolation,
                ForbiddenEvolution,
                UnauthorisedCoSign,
            )
        except ImportError:
            from colony.logic.exceptions import (  # type: ignore
                BlastRadiusViolation,
                ForbiddenEvolution,
                UnauthorisedCoSign,
            )

        # Step 0 — co-signer presence check (must be first so that
        # downstream forbidden-list "exempts co-signed paths" logic has
        # something truthy to check against).
        if not co_signer:
            raise UnauthorisedCoSign(
                f"Change to {agent_id} requires a co_signer but none was provided"
            )

        action_class = self._change_action_class(changes)
        description = self._change_describes(changes)

        target_cc = target_mirror.get("comprehension_contract", {}) or {}
        target_tier = target_cc.get("trust_tier", "Observing")
        target_ceiling = target_cc.get("blast_radius_ceiling", "Colony-wide")
        target_autonomy = target_mirror.get("autonomy", {}) or {}
        target_scope = target_autonomy.get("self_evolution_scope", {}) or {}
        forbidden = target_scope.get("forbidden", []) or []

        # Step 1 — classify the action against the target's trust tier
        classification = self.classify_action(
            {"class": action_class},
            {"actor_trust_tier": target_tier},
        )

        # Step 2 — blast radius ceiling check
        classifier_rank = self._BLAST_RADIUS_ORDER.get(classification.blast_radius, 99)
        ceiling_rank = self._BLAST_RADIUS_ORDER.get(target_ceiling, 99)
        if classifier_rank > ceiling_rank:
            raise BlastRadiusViolation(
                f"Proposed change to {agent_id} has blast radius "
                f"'{classification.blast_radius}' but the target's "
                f"blast_radius_ceiling is '{target_ceiling}'. "
                f"Action class: {action_class}."
            )

        # Step 3 — forbidden list check
        # The forbidden list holds plain-English strings. We do a substring
        # match on the description OR on any named capability in the change.
        # If any entry matches AND the entry does NOT explicitly exempt
        # co-signed paths (marker: "without a valid ... co-sign"), raise.
        for entry in forbidden:
            entry_lower = str(entry).lower()
            description_lower = description.lower()
            # If the forbidden entry exempts co-signed paths, and this
            # change IS accompanied by a co-sign, skip.
            exempts_cosigned = (
                "without a valid" in entry_lower
                and "co-sign" in entry_lower
            )
            if exempts_cosigned and co_signer:
                # The entry explicitly permits co-signed paths; the
                # UnauthorisedCoSign check below will catch a bad co-sign.
                continue
            # Simple keyword match: if the entry names the action
            # (e.g. "Add new teaching topics"), it matches.
            key_phrases = [
                "add new teaching",
                "add capability",
                "remove capability",
                "write to the colony knowledge base",
            ]
            for phrase in key_phrases:
                if phrase in entry_lower and phrase[:3] in description_lower:
                    raise ForbiddenEvolution(
                        f"Proposed change to {agent_id} is forbidden by "
                        f"self_evolution_scope.forbidden entry: {entry!r}. "
                        f"Change description: {description!r}."
                    )

        # Step 4 — co-signer policy freshness check
        co_signer_mirror = self.read_mirror(co_signer)
        co_signer_cc = co_signer_mirror.data.get("comprehension_contract", {}) or {}
        policies = co_signer_cc.get("pre_registered_policies", []) or []

        # The action class for graduation co-sign is 'graduation_cosign'
        # (what Sentinel pre-registers), not the underlying
        # 'mirror_capability_add'. We check either.
        valid_policy_classes = {"graduation_cosign", action_class}
        if action_class == "mirror_capability_add":
            valid_policy_classes.add("graduation_cosign")

        matching = [
            p for p in policies
            if p.get("action_class") in valid_policy_classes
            and str(p.get("freshness", "current")).lower() == "current"
        ]
        if not matching:
            raise UnauthorisedCoSign(
                f"Co-signer {co_signer} does not have a fresh "
                f"pre-registered policy for action_class='{action_class}' "
                f"(or for 'graduation_cosign' which covers capability adds). "
                f"Available policies: {[p.get('action_class') for p in policies]}"
            )

    def update_mirror(self, agent_id: str, changes: dict, co_signer: str) -> AuditEntry:
        # v1.7.0 Fix 5 — read from the effective path (overlay or baseline),
        # but ALWAYS write to state/mirrors/ (the overlay). This keeps
        # colony/mirrors/ clean across runs.
        read_path = self._mirror_path(agent_id)
        write_path = self._overlay_mirror_path(agent_id)
        write_path.parent.mkdir(parents=True, exist_ok=True)

        existing = {}
        if read_path.exists() and read_path.stat().st_size > 0:
            with read_path.open("r", encoding="utf-8") as f:
                existing = yaml.safe_load(f) or {}

        # ---- §7 Comprehension Contract enforcement ------------------------
        # See colony/logic/exceptions.py and substrate-contract.md.
        # These four checks are what v1.6.x claimed to do but didn't.
        self._enforce_contract(
            agent_id=agent_id,
            target_mirror=existing,
            changes=changes,
            co_signer=co_signer,
        )

        pre_hash = _hash_state(existing)
        merged = _apply_changes(existing, changes)

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

        with write_path.open("w", encoding="utf-8") as f:
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
                    "granted": sig.granted,
                    "reason": sig.reason,
                },
                timestamp=sig.timestamp,
                substrate=self.substrate_name,
            )
        )
        return sig

    # ---------------------------------------------------------------- classify

    def classify_action(self, action: dict, context: dict) -> Classification:
        # Try both import forms: fully-qualified (pytest from repo root)
        # and sibling-relative (run.py from inside examples/teaching_colony/).
        try:
            from examples.teaching_colony.colony.logic.classifier import (
                classify_action as _classify,
            )
            return _classify(action, context)
        except ImportError:
            pass
        try:
            from colony.logic.classifier import (  # type: ignore
                classify_action as _classify,
            )
            return _classify(action, context)
        except Exception:
            # Final fallback — safe default so the adapter can still run,
            # but this should NEVER fire in practice. If it does, the
            # §7 enforcement will over-report and fail safe.
            return Classification(
                blast_radius=action.get("blast_radius", "Colony-wide"),
                review_regime="Governance Council",
                action_class=action.get("class", "unknown"),
                actor_trust_tier=context.get("actor_trust_tier", "Observing"),
            )
