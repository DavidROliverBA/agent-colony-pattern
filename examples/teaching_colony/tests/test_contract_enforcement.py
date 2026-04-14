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
