"""Scaffolding tests for the Managed Agents substrate adapter.

Batch 1 (Sub-agent C) — these tests exercise the adapter in ``mock=True``
mode. Mock-mode operations that the scaffolding already implements are
expected to pass. Live-mode operations that still raise
``NotImplementedError`` until Sub-agent D completes Batch 2 are marked
``xfail``. No network calls. No live SDK.

The file must import cleanly and all tests must either pass or xfail —
never hard-error.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from examples.teaching_colony.substrates.managed_agents.adapter import (
    ManagedAgentsAdapter,
    Event,
    SubstrateContract,
)


@pytest.fixture()
def colony_root(tmp_path: Path) -> Path:
    """Temporary colony root. No real mirrors needed — scaffolding tests
    exercise shape, not content."""
    root = tmp_path / "teaching-colony"
    (root / "colony" / "mirrors").mkdir(parents=True, exist_ok=True)
    (root / "state" / "kb").mkdir(parents=True, exist_ok=True)
    return root


@pytest.fixture()
def adapter(colony_root: Path) -> ManagedAgentsAdapter:
    return ManagedAgentsAdapter(repo_root=colony_root, mock=True)


# ----------------------------------------------------------------------
# Contract shape
# ----------------------------------------------------------------------


def test_subclasses_substrate_contract(adapter: ManagedAgentsAdapter) -> None:
    assert isinstance(adapter, SubstrateContract)


def test_substrate_name(adapter: ManagedAgentsAdapter) -> None:
    assert adapter.substrate_name == "managed-agents"


# ----------------------------------------------------------------------
# Mock-mode dispatch (implemented)
# ----------------------------------------------------------------------


def test_dispatch_teacher_beekeeping(adapter: ManagedAgentsAdapter) -> None:
    result = adapter.dispatch_agent(
        "teacher", {"task": "teach", "topic": "beekeeping"}
    )
    assert result["mock"] is True
    assert "answer" in result
    assert result["tokens"] == 0


def test_dispatch_teacher_agent_colony(adapter: ManagedAgentsAdapter) -> None:
    result = adapter.dispatch_agent(
        "teacher", {"topic": "agent-colony-pattern", "question": "what is it?"}
    )
    assert result["mock"] is True
    # v1.7.0: the Agent Colony answer must use the beekeeping metaphor
    # AND reference the Mirror — that's the substance of the graduation claim.
    answer_lower = result["answer"].lower()
    assert "mirror" in answer_lower, (
        "Agent Colony answer must mention Mirror — see §7 graduation"
    )
    assert (
        "bees" in answer_lower
        or "hive" in answer_lower
        or "beehive" in answer_lower
        or "bee colony" in answer_lower
    )


def test_dispatch_librarian_curate(adapter: ManagedAgentsAdapter) -> None:
    result = adapter.dispatch_agent(
        "librarian", {"task": "curate", "file": "corpus/beekeeping-primer.md"}
    )
    assert result["mock"] is True
    assert result["topic"] == "beekeeping-primer"


def test_dispatch_librarian_coverage(adapter: ManagedAgentsAdapter) -> None:
    # v1.7.0: driver uses `action` key, not `task`, for coverage
    result = adapter.dispatch_agent(
        "librarian", {"action": "compute_coverage", "topic": "agent-colony-pattern"}
    )
    assert "agent-colony-pattern" in result["topics"]
    assert result["topics"]["agent-colony-pattern"]["docs"] == 7
    assert result.get("coverage_score", 0) > 0.5


def test_dispatch_librarian_propose_capability(
    adapter: ManagedAgentsAdapter,
) -> None:
    result = adapter.dispatch_agent("librarian", {"task": "propose_capability"})
    # v1.7.0: the canonical agent id is the long form `teacher-agent`
    assert result["agent_id"] == "teacher-agent"
    assert result["capability"] == "teach_agent_colony_pattern"


def test_dispatch_sentinel_cosign(adapter: ManagedAgentsAdapter) -> None:
    result = adapter.dispatch_agent(
        "sentinel",
        {
            "task": "cosign",
            "action_class": "capability_graduation",
            "actor": "librarian",
        },
    )
    assert result["granted"] is True


# ----------------------------------------------------------------------
# Mirror, event, KB, co-sign (mock)
# ----------------------------------------------------------------------


def test_read_mirror_missing_returns_empty(
    adapter: ManagedAgentsAdapter,
) -> None:
    mirror = adapter.read_mirror("teacher")
    assert mirror.agent_id == "teacher"
    assert isinstance(mirror.data, dict)


def test_update_mirror_mock_returns_audit(
    adapter: ManagedAgentsAdapter,
) -> None:
    audit = adapter.update_mirror(
        "teacher",
        {"capabilities": ["teach_agent_colony_pattern"]},
        co_signer="sentinel",
    )
    assert audit.action == "update_mirror"
    assert audit.co_signer == "sentinel"
    assert audit.rollback_window_minutes == 60


def test_record_event_writes_line(
    adapter: ManagedAgentsAdapter, colony_root: Path
) -> None:
    event = Event(type="demo.tick", actor="teacher", payload={"value": 42})
    adapter.record_event(event)
    log = colony_root / "state" / "events.jsonl"
    assert log.exists()
    content = log.read_text(encoding="utf-8")
    assert "managed-agents" in content
    assert "demo.tick" in content


def test_read_kb_mock_returns_empty(adapter: ManagedAgentsAdapter) -> None:
    assert adapter.read_kb("beekeeping") == []


def test_write_kb_mock_is_noop(adapter: ManagedAgentsAdapter) -> None:
    adapter.write_kb(
        topic="beekeeping",
        content="Hives need space.",
        provenance="corpus/beekeeping-primer.md",
    )


def test_co_sign_mock_grants(adapter: ManagedAgentsAdapter) -> None:
    sig = adapter.co_sign(
        action_class="capability_graduation",
        actor="librarian",
        co_signer="sentinel",
    )
    assert sig.granted is True
    assert sig.co_signer == "sentinel"


def test_classify_action_delegates(adapter: ManagedAgentsAdapter) -> None:
    """classify_action is non-substrate work and must be present in any
    working build. If the colony classifier is missing at Batch 1 time
    we xfail rather than hard-error."""
    try:
        cls = adapter.classify_action(
            action={"type": "capability_graduation"},
            context={"actor": "librarian"},
        )
    except Exception as exc:
        pytest.xfail(f"colony classifier not importable: {exc}")
    else:
        assert getattr(cls, "action_class", None) is not None
        assert getattr(cls, "review_regime", None) is not None


# ----------------------------------------------------------------------
# Live-mode xfails — until Sub-agent D ships Batch 2
# ----------------------------------------------------------------------


@pytest.fixture()
def live_adapter(colony_root: Path) -> ManagedAgentsAdapter:
    return ManagedAgentsAdapter(repo_root=colony_root, mock=False)


def test_live_dispatch_xfail(live_adapter: ManagedAgentsAdapter) -> None:
    with pytest.raises(NotImplementedError):
        live_adapter.dispatch_agent(
            "teacher", {"task": "teach", "topic": "beekeeping"}
        )
    pytest.xfail(
        "Gap — dispatch_agent live path pending Sub-agent D "
        "(see api-research.md Q3)"
    )


def test_live_update_mirror_xfail(live_adapter: ManagedAgentsAdapter) -> None:
    with pytest.raises(NotImplementedError):
        live_adapter.update_mirror(
            "teacher", {"x": 1}, co_signer="sentinel"
        )
    pytest.xfail("Gap — update_mirror live path pending Sub-agent D")


def test_live_write_kb_is_local(live_adapter: ManagedAgentsAdapter) -> None:
    """v1.7.0: write_kb is now a local-file op regardless of mode — matches
    the Claude Code substrate. The mock/live distinction only applies to
    dispatch_agent and update_mirror (live), which still require API calls.
    """
    live_adapter.write_kb(topic="beekeeping", content="x", provenance="y")
    slug_path = live_adapter.kb_dir / "beekeeping.md"
    assert slug_path.exists()


def test_live_co_sign_is_local_policy(live_adapter: ManagedAgentsAdapter) -> None:
    """v1.7.0: co_sign is colony policy, not a Managed Agents API call —
    it works in both mock and live mode and emits cosign.granted.
    """
    sig = live_adapter.co_sign(
        "graduation_cosign", "librarian-agent", "sentinel-agent"
    )
    assert sig.granted is True
    assert sig.action_class == "graduation_cosign"
