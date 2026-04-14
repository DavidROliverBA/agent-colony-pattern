"""Cross-substrate portability test for the Teaching Colony (v1.6.0).

The v1.6.0 portability claim: a scripted lifecycle run in *mock mode* on
both substrates should observe the same structural transitions — the same
classifier output, the same event-type sequence (modulo substrate-specific
fields), and the same final Teacher Mirror state.

This file intentionally treats that claim with honest limits. In v1.6.0 the
Managed Agents adapter ships with mock-mode dispatch, co-sign, classify and
event-log writes implemented, but ``update_mirror`` and ``write_kb`` are
scaffolding only (see ``substrates/managed_agents/gaps.md``). Where the
parity claim cannot be fully exercised against the scaffolding, the test
``pytest.skip``s with a reason that points at ``gaps.md`` rather than
failing. Live-mode parity is v1.7+.

What we *do* assert unconditionally:

* The Claude Code substrate completes the minimal lifecycle end to end in
  mock mode.
* The Managed Agents substrate completes every mock-implemented operation
  in the lifecycle without raising.
* Both substrates' classifier outputs are byte-identical for the same input
  (they delegate to ``colony.logic.classifier`` — this is the running
  demonstration of Principle 2).

What we skip (with citations) when the Managed Agents scaffolding cannot
yet honour the parity claim:

* Teacher-Mirror final-state equality — the scaffolding ``update_mirror``
  returns a zeroed ``AuditEntry`` without persisting the change.
* Event-log-type sequence equality — consequently the ``mirror.updated``
  event is not emitted on the Managed Agents side.
"""

from __future__ import annotations

import importlib
import json
import shutil
from pathlib import Path
from typing import Any

import pytest

# Repo layout: examples/teaching_colony/tests/test_portability.py -> parents[3]
REPO_ROOT = Path(__file__).resolve().parents[3]
COLONY_SRC = REPO_ROOT / "examples" / "teaching_colony" / "colony"
GAPS_MD = (
    REPO_ROOT
    / "examples"
    / "teaching_colony"
    / "substrates"
    / "managed_agents"
    / "gaps.md"
)


# ---------------------------------------------------------------------------
# Fixtures — two independent colony roots, one per substrate
# ---------------------------------------------------------------------------


def _seed_colony_root(root: Path) -> Path:
    """Copy the canonical colony/ tree into *root* and return root.

    Also mirrors each ``<role>-agent.yaml`` as ``<role>.yaml`` so both the
    short-id path used by the minimal lifecycle and the long-id path used by
    ``run.py`` resolve.
    """
    root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(COLONY_SRC, root / "colony", dirs_exist_ok=True)
    mirrors_dir = root / "colony" / "mirrors"
    for long_name in list(mirrors_dir.glob("*-agent.yaml")):
        short = mirrors_dir / f"{long_name.stem.split('-')[0]}.yaml"
        if not short.exists():
            shutil.copy(long_name, short)
    (root / "state").mkdir(parents=True, exist_ok=True)
    (root / "state" / "kb").mkdir(parents=True, exist_ok=True)
    return root


@pytest.fixture()
def cc_root(tmp_path: Path) -> Path:
    return _seed_colony_root(tmp_path / "cc")


@pytest.fixture()
def ma_root(tmp_path: Path) -> Path:
    return _seed_colony_root(tmp_path / "ma")


@pytest.fixture()
def cc_adapter(cc_root: Path):
    from examples.teaching_colony.substrates.claude_code.adapter import (
        ClaudeCodeAdapter,
    )

    return ClaudeCodeAdapter(repo_root=cc_root, mock=True)


@pytest.fixture()
def ma_adapter(ma_root: Path):
    from examples.teaching_colony.substrates.managed_agents.adapter import (
        ManagedAgentsAdapter,
    )

    return ManagedAgentsAdapter(repo_root=ma_root, mock=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


# Fields that legitimately vary across substrates and must be stripped
# before event-log comparison.
VOLATILE_FIELDS = {"timestamp", "substrate"}
VOLATILE_PAYLOAD_FIELDS = {
    "hash",  # dispatch.complete hash depends on output structure
    "pre_state_hash",
    "post_state_hash",
    "timestamp",
}


def _capability_list(mirror_data: dict) -> list:
    caps = mirror_data.get("capabilities", [])
    if isinstance(caps, dict):
        return caps.get("capabilities", []) or []
    return list(caps) if caps else []


def _capability_names(mirror_data: dict) -> list[str]:
    caps = _capability_list(mirror_data)
    if not caps:
        return []
    if isinstance(caps[0], dict):
        return [c.get("name", "") for c in caps]
    return [str(c) for c in caps]


def _normalise_event(evt: dict) -> dict:
    """Strip volatile, substrate-specific fields from an event record."""
    out = {k: v for k, v in evt.items() if k not in VOLATILE_FIELDS}
    if isinstance(out.get("payload"), dict):
        out["payload"] = {
            k: v
            for k, v in out["payload"].items()
            if k not in VOLATILE_PAYLOAD_FIELDS
        }
    return out


def _read_event_log(root: Path) -> list[dict]:
    path = root / "state" / "events.jsonl"
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _run_minimal_lifecycle(adapter: Any) -> dict:
    """Minimal 8-step lifecycle, identical call-for-call on both adapters.

    Returns a dict summarising what was observed. Never modifies the
    adapter's behaviour; only exercises the public contract.
    """
    from examples.teaching_colony.contract import Event

    observed: dict = {"classification": None, "cosign_granted": None}

    # 1. Baseline: read Teacher's mirror
    baseline = adapter.read_mirror("teacher")
    observed["baseline_capabilities"] = _capability_names(baseline.data)

    # 2. Populate KB with five primer docs
    for i in range(5):
        adapter.write_kb(
            topic=f"agent-colony-pattern part {i + 1}",
            content=(
                "The Agent Colony pattern organises specialised agents like "
                "a bee colony. Cross-reference: beekeeping primer."
            ),
            provenance=f"seed:acp-primer-{i + 1}",
        )

    # 3. Librarian proposes graduation
    proposal = adapter.dispatch_agent("librarian", {"task": "propose_capability"})
    observed["proposal"] = proposal

    # 4. Classify the action — must be substrate-independent
    classification = adapter.classify_action(
        {"class": "mirror_capability_add"},
        {"actor_trust_tier": "Observing"},
    )
    observed["classification"] = classification

    # 5. Sentinel co-signs
    sig = adapter.co_sign(
        action_class="capability.add",
        actor=proposal.get("agent_id", "librarian"),
        co_signer="sentinel",
    )
    observed["cosign_granted"] = sig.granted

    # 6. Apply the mirror update (append, don't replace)
    # v1.8.1: use the add_capability DSL (the pre-merged nested-dict form
    # is rejected by the stricter DSL gate in _apply_changes).
    adapter.update_mirror(
        "teacher",
        {
            "add_capability": {
                "name": proposal.get("capability", "teach_agent_colony_pattern"),
                "maturity": "nascent",
            }
        },
        co_signer="sentinel",
    )

    # 7. Record graduation event
    adapter.record_event(
        Event(
            type="graduation.approved",
            actor="librarian",
            payload={
                "agent_id": "teacher",
                "capability": proposal.get("capability"),
                "signature_granted": sig.granted,
            },
        )
    )

    # 8. Read Teacher's mirror again
    final = adapter.read_mirror("teacher")
    observed["final_capabilities"] = _capability_names(final.data)
    return observed


def _ma_persists_mirror_updates() -> bool:
    """True if the Managed Agents mock ``update_mirror`` actually persists.

    The v1.6.0 scaffolding returns a zeroed ``AuditEntry`` without writing.
    If a later batch teaches the scaffolding to persist in mock mode this
    probe will return True and the parity assertions run for real.
    """
    try:
        from examples.teaching_colony.substrates.managed_agents.adapter import (
            ManagedAgentsAdapter,
        )
    except Exception:
        return False

    import tempfile

    with tempfile.TemporaryDirectory() as td:
        root = _seed_colony_root(Path(td) / "probe")
        adapter = ManagedAgentsAdapter(repo_root=root, mock=True)
        before = _capability_names(adapter.read_mirror("teacher").data)
        try:
            adapter.update_mirror(
                "teacher",
                {"add_capability": {"name": "_probe_cap", "maturity": "nascent"}},
                co_signer="sentinel",
            )
        except NotImplementedError:
            return False
        after = _capability_names(adapter.read_mirror("teacher").data)
        return "_probe_cap" in after and before != after


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_lifecycle_runs_on_claude_code(cc_adapter, cc_root: Path) -> None:
    """Claude Code substrate must complete the full minimal lifecycle."""
    observed = _run_minimal_lifecycle(cc_adapter)

    assert "teach_beekeeping" in observed["baseline_capabilities"]
    assert "teach_agent_colony_pattern" not in observed["baseline_capabilities"]
    assert observed["cosign_granted"] is True
    assert "teach_agent_colony_pattern" in observed["final_capabilities"]

    events = _read_event_log(cc_root)
    assert any(e["type"] == "graduation.approved" for e in events)
    assert any(e["type"] == "mirror.updated" for e in events)


def test_lifecycle_runs_on_managed_agents(ma_adapter, ma_root: Path) -> None:
    """Managed Agents substrate must complete every mock-implemented op.

    Operations the scaffolding does not persist (update_mirror, write_kb)
    are still callable in mock mode — they just don't mutate state. The
    test asserts they do not raise and that dispatch/cosign/classify work
    fully.
    """
    try:
        observed = _run_minimal_lifecycle(ma_adapter)
    except NotImplementedError as exc:
        pytest.skip(
            "Managed Agents scaffolding cannot yet complete the mock "
            f"lifecycle: {exc}. See {GAPS_MD.relative_to(REPO_ROOT)}."
        )

    # Dispatch/cosign/classify are mock-implemented — assert their outputs.
    assert observed["proposal"]["capability"] == "teach_agent_colony_pattern"
    assert observed["cosign_granted"] is True

    events = _read_event_log(ma_root)
    assert any(e["type"] == "graduation.approved" for e in events), (
        "Managed Agents adapter must record the graduation event even "
        "when update_mirror is scaffolding."
    )


def test_classifier_output_is_substrate_independent(
    cc_adapter, ma_adapter
) -> None:
    """Principle 2 (Identity over implementation) in running code.

    Both adapters delegate ``classify_action`` to
    ``colony.logic.classifier`` — for identical input they must return
    byte-identical structural fields. This is the v1.6.0 portability
    claim that can be asserted unconditionally.
    """
    action = {"class": "mirror_capability_add", "blast_radius": "Colony-wide"}
    context = {"actor_trust_tier": "Observing"}

    cc = cc_adapter.classify_action(action, context)
    ma = ma_adapter.classify_action(action, context)

    assert cc.action_class == ma.action_class
    assert cc.blast_radius == ma.blast_radius
    assert cc.review_regime == ma.review_regime
    assert cc.actor_trust_tier == ma.actor_trust_tier


def test_event_log_types_match(cc_adapter, ma_adapter, cc_root, ma_root) -> None:
    """Portability parity for event-type sequence.

    Strips volatile, substrate-specific fields (``timestamp``, ``substrate``,
    payload hashes) before comparison. Skipped in v1.6.0 because the
    Managed Agents scaffolding does not emit ``mirror.updated`` events
    from its mock ``update_mirror``.
    """
    _run_minimal_lifecycle(cc_adapter)
    try:
        _run_minimal_lifecycle(ma_adapter)
    except NotImplementedError as exc:
        pytest.skip(
            "Managed Agents scaffolding cannot complete the lifecycle: "
            f"{exc}. See {GAPS_MD.relative_to(REPO_ROOT)}."
        )

    if not _ma_persists_mirror_updates():
        pytest.skip(
            "Managed Agents v1.6.0 scaffolding returns a zeroed "
            "AuditEntry from mock update_mirror and does not emit a "
            "mirror.updated event, so full event-sequence parity cannot "
            "be asserted. Live-mode parity is v1.7+. See "
            f"{GAPS_MD.relative_to(REPO_ROOT)}."
        )

    cc_events = [_normalise_event(e) for e in _read_event_log(cc_root)]
    ma_events = [_normalise_event(e) for e in _read_event_log(ma_root)]

    cc_types = [e["type"] for e in cc_events]
    ma_types = [e["type"] for e in ma_events]
    assert cc_types == ma_types, (
        f"Event-type sequence diverged:\n  cc: {cc_types}\n  ma: {ma_types}"
    )


def test_teacher_mirror_final_state_matches(
    cc_adapter, ma_adapter
) -> None:
    """Portability parity for Teacher Mirror final state.

    Both substrates should converge on the same capability set and an
    evolution-log entry with non-empty pre/post state hashes. Skipped in
    v1.6.0 because the Managed Agents scaffolding does not persist the
    mirror change and emits zeroed hashes.
    """
    _run_minimal_lifecycle(cc_adapter)
    try:
        _run_minimal_lifecycle(ma_adapter)
    except NotImplementedError as exc:
        pytest.skip(
            "Managed Agents scaffolding cannot complete the lifecycle: "
            f"{exc}. See {GAPS_MD.relative_to(REPO_ROOT)}."
        )

    if not _ma_persists_mirror_updates():
        pytest.skip(
            "Managed Agents v1.6.0 scaffolding does not persist mock "
            "update_mirror, so Teacher-Mirror final-state parity cannot "
            "be asserted. Live-mode parity is v1.7+. See "
            f"{GAPS_MD.relative_to(REPO_ROOT)}."
        )

    cc_final = set(_capability_names(cc_adapter.read_mirror("teacher").data))
    ma_final = set(_capability_names(ma_adapter.read_mirror("teacher").data))
    assert cc_final == ma_final

    cc_log = (
        cc_adapter.read_mirror("teacher")
        .data.get("autonomy", {})
        .get("evolution_log", [])
    )
    ma_log = (
        ma_adapter.read_mirror("teacher")
        .data.get("autonomy", {})
        .get("evolution_log", [])
    )
    assert cc_log and ma_log
    assert cc_log[-1]["pre_state_hash"]
    assert cc_log[-1]["post_state_hash"]
    assert ma_log[-1]["pre_state_hash"]
    assert ma_log[-1]["post_state_hash"]
