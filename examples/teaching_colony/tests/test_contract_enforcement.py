"""Tests that the Comprehension Contract actually bites.

v1.6.x claimed to enforce the §7 Comprehension Contract in update_mirror
but the external review found no enforcement in the adapter at all. v1.7.0
adds four checks — classifier invocation, blast-radius-ceiling, forbidden
list, and co-signer policy freshness — and these tests assert that each
one of them actually raises when it should.

If any of these four tests fail, the Comprehension Contract is visual
theatre again and the v1.7.0 claim is void. These are the minimum proof
that governance bites.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_ROOT = REPO_ROOT / "examples" / "teaching_colony"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from examples.teaching_colony.substrates.claude_code.adapter import (  # noqa: E402
    ClaudeCodeAdapter,
)
from examples.teaching_colony.colony.logic.exceptions import (  # noqa: E402
    BlastRadiusViolation,
    ForbiddenEvolution,
    UnauthorisedCoSign,
)


@pytest.fixture
def colony_workspace(tmp_path: Path) -> Path:
    """Fresh copy of the colony for each enforcement test."""
    workspace = tmp_path / "teaching_colony"
    shutil.copytree(
        EXAMPLE_ROOT,
        workspace,
        symlinks=False,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "state"),
    )
    (workspace / "state").mkdir(exist_ok=True)
    return workspace


def _rewrite_mirror(workspace: Path, agent_id: str, patch: dict) -> None:
    """Mutate a Mirror on disk to set up a precondition for a test."""
    path = workspace / "colony" / "mirrors" / f"{agent_id}.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def _merge(d, p):
        for k, v in p.items():
            if isinstance(v, dict) and isinstance(d.get(k), dict):
                _merge(d[k], v)
            else:
                d[k] = v

    _merge(data, patch)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Happy path — the demo's graduation path must still work after enforcement
# ---------------------------------------------------------------------------


def test_happy_path_graduation_succeeds(colony_workspace: Path) -> None:
    """The demo path — a capability add with a valid Sentinel co-sign —
    must succeed. This is the regression assertion that enforcement
    doesn't break the walkthrough."""
    adapter = ClaudeCodeAdapter(repo_root=colony_workspace, mock=True)
    audit = adapter.update_mirror(
        agent_id="teacher-agent",
        changes={
            "add_capability": {
                "name": "teach_agent_colony_pattern",
                "description": "test",
                "maturity": "nascent",
            }
        },
        co_signer="sentinel-agent",
    )
    assert audit.pre_state_hash
    assert audit.post_state_hash
    assert audit.pre_state_hash != audit.post_state_hash


# ---------------------------------------------------------------------------
# Three negative tests — each check must fire when provoked
# ---------------------------------------------------------------------------


def test_blast_radius_violation_is_raised(colony_workspace: Path) -> None:
    """If the target's blast_radius_ceiling is lower than the action's
    classified blast radius, update_mirror must raise."""
    # Lower Teacher's ceiling back to Inter-agent for this test so the
    # Colony-wide capability_add exceeds it.
    _rewrite_mirror(
        colony_workspace,
        "teacher-agent",
        {"comprehension_contract": {"blast_radius_ceiling": "Inter-agent"}},
    )

    adapter = ClaudeCodeAdapter(repo_root=colony_workspace, mock=True)
    with pytest.raises(BlastRadiusViolation) as excinfo:
        adapter.update_mirror(
            agent_id="teacher-agent",
            changes={
                "add_capability": {
                    "name": "teach_something_new",
                    "description": "test",
                    "maturity": "nascent",
                }
            },
            co_signer="sentinel-agent",
        )
    assert "Inter-agent" in str(excinfo.value)
    assert "Colony-wide" in str(excinfo.value)


def test_forbidden_evolution_is_raised(colony_workspace: Path) -> None:
    """If the target's self_evolution_scope.forbidden names the action,
    update_mirror must raise — even with a valid co-signer."""
    # Install a forbidden entry that does NOT exempt co-signed paths.
    _rewrite_mirror(
        colony_workspace,
        "teacher-agent",
        {
            "autonomy": {
                "self_evolution_scope": {
                    "forbidden": ["Add capability (completely banned, no exceptions)"]
                }
            }
        },
    )

    adapter = ClaudeCodeAdapter(repo_root=colony_workspace, mock=True)
    with pytest.raises(ForbiddenEvolution) as excinfo:
        adapter.update_mirror(
            agent_id="teacher-agent",
            changes={
                "add_capability": {
                    "name": "teach_something_new",
                    "description": "test",
                    "maturity": "nascent",
                }
            },
            co_signer="sentinel-agent",
        )
    assert "forbidden" in str(excinfo.value).lower()


def test_unauthorised_cosign_is_raised(colony_workspace: Path) -> None:
    """If the co-signer does not have a fresh pre-registered policy for
    the action class, update_mirror must raise."""
    # Rewrite Sentinel's Mirror so it has no graduation_cosign policy.
    _rewrite_mirror(
        colony_workspace,
        "sentinel-agent",
        {
            "comprehension_contract": {
                "pre_registered_policies": [
                    {
                        "policy_id": "unrelated-p001",
                        "action_class": "something_else",
                        "blast_radius": "Local",
                        "reviewed_date": "2026-04-14",
                        "freshness": "current",
                    }
                ]
            }
        },
    )

    adapter = ClaudeCodeAdapter(repo_root=colony_workspace, mock=True)
    with pytest.raises(UnauthorisedCoSign) as excinfo:
        adapter.update_mirror(
            agent_id="teacher-agent",
            changes={
                "add_capability": {
                    "name": "teach_something_new",
                    "description": "test",
                    "maturity": "nascent",
                }
            },
            co_signer="sentinel-agent",
        )
    assert "sentinel-agent" in str(excinfo.value)
    assert "graduation_cosign" in str(excinfo.value)


def test_missing_cosigner_is_raised(colony_workspace: Path) -> None:
    """update_mirror must require a co_signer. Empty string is a co-sign
    violation, not a silent pass-through."""
    adapter = ClaudeCodeAdapter(repo_root=colony_workspace, mock=True)
    with pytest.raises(UnauthorisedCoSign):
        adapter.update_mirror(
            agent_id="teacher-agent",
            changes={
                "add_capability": {
                    "name": "teach_something_new",
                    "description": "test",
                    "maturity": "nascent",
                }
            },
            co_signer="",
        )


# ---------------------------------------------------------------------------
# v1.8.1 regression — DSL dual-key bypass closure
# ---------------------------------------------------------------------------
#
# External review of v1.8.0 found a latent bypass: _apply_changes had a
# backwards-compat fallthrough that silently deep-merged any unknown top-
# level key as a literal YAML patch. A caller passing the legacy
# ``capability_add`` (singular) name bypassed the semantic DSL entirely —
# the change was classified as "mirror_patch" (Local blast radius), the
# blast-radius ceiling passed trivially, the forbidden-list keyword match
# missed, and the new capability ended up as a top-level YAML stanza
# (the exact v1.6.x bug the DSL was meant to kill).
#
# v1.8.1 closes the hole by rejecting unknown DSL keys up front. These
# tests provoke the specific bypass and assert it raises.


def test_legacy_capability_add_key_is_rejected(colony_workspace: Path) -> None:
    """The v1.6.x legacy key name must raise, not silently deep-merge.

    This is the load-bearing regression test for the DSL dual-key bypass
    the reviewer flagged. If this test fails the §7 enforcement has a
    qualifier ('enforced provided the caller uses the current DSL names')
    and the governance story is compromised.
    """
    adapter = ClaudeCodeAdapter(repo_root=colony_workspace, mock=True)
    with pytest.raises(ValueError) as excinfo:
        adapter.update_mirror(
            agent_id="teacher-agent",
            changes={
                "capability_add": {  # <-- legacy name, v1.6.x bug key
                    "name": "teach_something_new",
                    "description": "test",
                    "maturity": "nascent",
                }
            },
            co_signer="sentinel-agent",
        )
    msg = str(excinfo.value)
    assert "capability_add" in msg
    assert "add_capability" in msg  # the fix suggestion
    assert "Unknown change DSL key" in msg


def test_random_unknown_dsl_key_is_rejected(colony_workspace: Path) -> None:
    """Any key that is NOT one of the three recognised DSL keys must raise.

    This generalises the capability_add case: the fix isn't a special-case
    for that one legacy name, it's a complete whitelist of allowed keys.
    """
    adapter = ClaudeCodeAdapter(repo_root=colony_workspace, mock=True)
    with pytest.raises(ValueError) as excinfo:
        adapter.update_mirror(
            agent_id="teacher-agent",
            changes={"set_description": "some new purpose"},
            co_signer="sentinel-agent",
        )
    assert "set_description" in str(excinfo.value)
    assert "Unknown change DSL key" in str(excinfo.value)


def test_patch_key_still_works_for_legitimate_literal_updates(
    colony_workspace: Path,
) -> None:
    """The explicit ``patch`` key remains the escape hatch for literal
    field updates. v1.8.1 rejects unknown keys but keeps the DSL's three
    recognised operations working.
    """
    adapter = ClaudeCodeAdapter(repo_root=colony_workspace, mock=True)
    audit = adapter.update_mirror(
        agent_id="teacher-agent",
        changes={
            "patch": {
                "identity": {"notes": "updated via patch key"},
            }
        },
        co_signer="sentinel-agent",
    )
    assert audit.pre_state_hash != audit.post_state_hash
    # Read it back via the overlay
    mirror = adapter.read_mirror("teacher-agent")
    assert mirror.data.get("identity", {}).get("notes") == "updated via patch key"


def test_mixed_dsl_and_legacy_key_rejects_entire_change(
    colony_workspace: Path,
) -> None:
    """If a caller passes BOTH a legitimate add_capability AND a legacy
    capability_add, the whole change is rejected — we don't silently
    apply the good half. Atomic gate.
    """
    adapter = ClaudeCodeAdapter(repo_root=colony_workspace, mock=True)
    with pytest.raises(ValueError):
        adapter.update_mirror(
            agent_id="teacher-agent",
            changes={
                "add_capability": {"name": "valid_one"},
                "capability_add": {"name": "legacy_one"},
            },
            co_signer="sentinel-agent",
        )
    # Verify neither capability landed — the pre-check fired before any
    # mutation. Read teacher's mirror and assert only the baseline
    # capability is present.
    mirror = adapter.read_mirror("teacher-agent")
    caps_section = mirror.data.get("capabilities", {})
    caps_list = (
        caps_section.get("capabilities", [])
        if isinstance(caps_section, dict)
        else []
    )
    names = [c.get("name") for c in caps_list if isinstance(c, dict)]
    assert "valid_one" not in names
    assert "legacy_one" not in names
