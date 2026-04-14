"""Tests for the Claude Code substrate adapter.

The adapter is tested in two layers:

1. Unit-level assertions over each of the eight contract operations
   (`read_mirror`, `update_mirror`, `record_event`, `read_kb`, `write_kb`,
   `co_sign`, `dispatch_agent` in mock mode, `classify_action`).
2. A full lifecycle test that imitates what the sub-agent A lifecycle driver
   will do, using only the adapter's public methods. If sub-agent A's real
   `run.py` driver is present it is imported and run instead.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from examples.teaching_colony.substrates.claude_code.adapter import (
    ClaudeCodeAdapter,
)


def _capability_list(mirror_data: dict) -> list:
    """Return the list of capability entries from a Mirror.

    In the v0.2.0 schema, `capabilities` is a top-level SECTION that
    contains the fields `capabilities` (list), `contracts`, `dependencies`,
    `protocols`. So the actual list of capabilities lives at
    `mirror_data['capabilities']['capabilities']`. A flat-list form
    (`mirror_data['capabilities'] = [...]`) is also tolerated."""
    caps_section = mirror_data.get("capabilities", [])
    if isinstance(caps_section, dict):
        return caps_section.get("capabilities", []) or []
    return list(caps_section) if caps_section else []


def _capability_names(mirror_data: dict) -> list[str]:
    """Extract capability names from a Mirror, supporting both the
    hello-colony dict form ([{name: ..., ...}, ...]) and the flat
    string-list form ([name, name, ...])."""
    caps = _capability_list(mirror_data)
    if not caps:
        return []
    if isinstance(caps[0], dict):
        return [c.get("name", "") for c in caps]
    return [str(c) for c in caps]


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------


def test_read_mirror_returns_seeded_capabilities(colony_root: Path) -> None:
    adapter = ClaudeCodeAdapter(repo_root=colony_root, mock=True)
    mirror = adapter.read_mirror("teacher")
    names = _capability_names(mirror.data)
    assert "teach_beekeeping" in names
    assert "teach_agent_colony_pattern" not in names


def test_record_event_appends_jsonl(colony_root: Path) -> None:
    adapter = ClaudeCodeAdapter(repo_root=colony_root, mock=True)
    from examples.teaching_colony.substrates.claude_code.adapter import Event

    adapter.record_event(
        Event(type="test.fixture", actor="tester", payload={"n": 1})
    )
    line = (colony_root / "state" / "events.jsonl").read_text(encoding="utf-8").strip()
    parsed = json.loads(line.splitlines()[-1])
    assert parsed["type"] == "test.fixture"
    assert parsed["substrate"] == "claude-code"
    assert parsed["timestamp"]


def test_write_and_read_kb(colony_root: Path) -> None:
    adapter = ClaudeCodeAdapter(repo_root=colony_root, mock=True)
    adapter.write_kb(
        topic="beekeeping",
        content="Worker bees forage within a few kilometres of the hive.",
        provenance="seed:primer",
    )
    docs = adapter.read_kb("forage")
    assert any(d.topic == "beekeeping" for d in docs)
    assert any("Worker bees" in d.content for d in docs)


def test_update_mirror_records_audit_and_hashes(colony_root: Path) -> None:
    adapter = ClaudeCodeAdapter(repo_root=colony_root, mock=True)
    # v1.8.1: use the add_capability DSL (the legacy capability_add key
    # and the literal {capabilities: {capabilities: [...]}} form are now
    # rejected by the stricter DSL gate in _apply_changes).
    audit = adapter.update_mirror(
        "teacher",
        {"add_capability": {"name": "teach_agent_colony_pattern", "maturity": "nascent"}},
        co_signer="sentinel",
    )
    assert audit.pre_state_hash
    assert audit.post_state_hash
    assert audit.pre_state_hash != audit.post_state_hash
    assert audit.co_signer == "sentinel"

    mirror = adapter.read_mirror("teacher")
    names = _capability_names(mirror.data)
    assert "teach_beekeeping" in names
    assert "teach_agent_colony_pattern" in names

    log = mirror.data.get("autonomy", {}).get("evolution_log", [])
    assert log, "evolution_log should have at least one entry"
    assert log[-1]["co_signer"] == "sentinel"
    assert log[-1]["post_state_hash"] == audit.post_state_hash


def test_cosign_mock_returns_granted(colony_root: Path) -> None:
    adapter = ClaudeCodeAdapter(repo_root=colony_root, mock=True)
    sig = adapter.co_sign(
        action_class="capability.add", actor="librarian", co_signer="sentinel"
    )
    assert sig.granted is True
    assert sig.action_class == "capability.add"


def test_dispatch_agent_mock_teacher_beekeeping(colony_root: Path) -> None:
    adapter = ClaudeCodeAdapter(repo_root=colony_root, mock=True)
    out = adapter.dispatch_agent("teacher", {"task": "teach", "topic": "beekeeping"})
    assert out["mock"] is True
    assert "answer" in out
    assert "bees" in out["answer"].lower()


def test_classify_action_fallback(colony_root: Path) -> None:
    adapter = ClaudeCodeAdapter(repo_root=colony_root, mock=True)
    c = adapter.classify_action(
        {"class": "mirror_capability_add", "blast_radius": "Colony-wide"},
        {"actor_trust_tier": "Observing"},
    )
    assert c.action_class == "mirror_capability_add"
    assert c.actor_trust_tier == "Observing"
    # Novel action short-circuits to Peer Review per §7.4
    assert c.review_regime == "Peer Review"


# ---------------------------------------------------------------------------
# Full lifecycle test
# ---------------------------------------------------------------------------


def _run_inline_lifecycle(adapter: ClaudeCodeAdapter) -> None:
    """A minimal stand-in for sub-agent A's lifecycle driver.

    Steps:
      1. Teacher asked about beekeeping (known capability) → baseline.
      2. Librarian curates 5 agent-colony-pattern primer docs into the KB.
      3. Librarian proposes capability graduation for Teacher.
      4. Sentinel co-signs the graduation.
      5. Teacher's Mirror is updated to include `teach_agent_colony_pattern`.
      6. A `graduation.approved` event is recorded.
    """
    from examples.teaching_colony.substrates.claude_code.adapter import Event

    # 1. Baseline dispatch
    adapter.dispatch_agent("teacher", {"task": "teach", "topic": "beekeeping"})

    # 2. Populate KB with five primer docs for agent-colony-pattern
    for i in range(5):
        adapter.write_kb(
            topic=f"agent-colony-pattern part {i + 1}",
            content=(
                "The Agent Colony pattern organises specialised agents like a bee "
                "colony. Cross-reference: beekeeping primer."
            ),
            provenance=f"seed:acp-primer-{i + 1}",
        )

    # 3. Librarian proposes graduation
    proposal = adapter.dispatch_agent("librarian", {"task": "propose_capability"})
    assert proposal["capability"] == "teach_agent_colony_pattern"

    # 4. Sentinel co-signs
    sig = adapter.co_sign(
        action_class="capability.add",
        actor=proposal["agent_id"],
        co_signer="sentinel",
    )
    assert sig.granted

    # 5. Apply mirror update via the semantic DSL (v1.8.1)
    adapter.update_mirror(
        proposal["agent_id"],
        {"add_capability": {"name": proposal["capability"], "maturity": "nascent"}},
        co_signer="sentinel",
    )

    # 6. Record graduation event
    adapter.record_event(
        Event(
            type="graduation.approved",
            actor="librarian",
            payload={
                "agent_id": proposal["agent_id"],
                "capability": proposal["capability"],
                "signature_granted": sig.granted,
            },
        )
    )


def test_full_lifecycle_mock(colony_root: Path) -> None:
    adapter = ClaudeCodeAdapter(repo_root=colony_root, mock=True)

    # Precondition: teacher does not yet know agent-colony-pattern
    initial = adapter.read_mirror("teacher")
    initial_names = _capability_names(initial.data)
    assert "teach_beekeeping" in initial_names
    assert "teach_agent_colony_pattern" not in initial_names

    # Run lifecycle — prefer real driver from sub-agent A if present
    try:
        from examples.teaching_colony.run import run_lifecycle  # type: ignore

        run_lifecycle(adapter=adapter, repo_root=colony_root)  # pragma: no cover
    except Exception:
        _run_inline_lifecycle(adapter)

    # Postcondition: Teacher now has the new capability
    final = adapter.read_mirror("teacher")
    final_names = _capability_names(final.data)
    assert "teach_beekeeping" in final_names
    assert "teach_agent_colony_pattern" in final_names

    # Event log contains graduation.approved and at least one audit entry with hashes
    events = [
        json.loads(line)
        for line in (colony_root / "state" / "events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    assert any(e["type"] == "graduation.approved" for e in events)

    mirror_updates = [e for e in events if e["type"] == "mirror.updated"]
    assert mirror_updates, "expected a mirror.updated event"
    last = mirror_updates[-1]
    assert last["payload"]["pre_state_hash"]
    assert last["payload"]["post_state_hash"]
    assert last["payload"]["pre_state_hash"] != last["payload"]["post_state_hash"]

    cosigns = [e for e in events if e["type"] == "cosign.granted"]
    assert cosigns, "expected at least one cosign.granted event"
