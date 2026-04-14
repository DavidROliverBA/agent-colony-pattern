"""Pytest fixtures for the Claude Code substrate tests.

Copies (or synthesises) a minimal Teaching Colony layout into a temporary
directory so tests exercise the adapter without mutating the repository.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[5]
COLONY_SRC = REPO_ROOT / "examples" / "teaching_colony" / "colony"


def _write_minimal_colony(root: Path) -> None:
    """Synthesise a minimal colony layout when sub-agent A's files aren't present."""
    mirrors_dir = root / "colony" / "mirrors"
    mirrors_dir.mkdir(parents=True, exist_ok=True)

    teacher = {
        "identity": {"name": "Teacher", "role": "teacher"},
        "purpose": "Answer questions drawing on the curated knowledge base.",
        "capabilities": ["teach_beekeeping"],
        "autonomy": {"trust_tier": "apprentice", "evolution_log": []},
    }
    librarian = {
        "identity": {"name": "Librarian", "role": "librarian"},
        "purpose": "Curate knowledge base documents and propose capability graduations.",
        "capabilities": ["curate", "compute_coverage", "propose_capability"],
        "autonomy": {"trust_tier": "journeyman", "evolution_log": []},
    }
    sentinel = {
        "identity": {"name": "Sentinel", "role": "sentinel"},
        "purpose": "Co-sign privileged actions against pre-registered policy.",
        "capabilities": ["cosign"],
        "autonomy": {"trust_tier": "steward", "evolution_log": []},
    }
    for agent_id, data in (
        ("teacher-agent", teacher),
        ("librarian-agent", librarian),
        ("sentinel-agent", sentinel),
        # Short-alias copies so either naming convention resolves
        ("teacher", teacher),
        ("librarian", librarian),
        ("sentinel", sentinel),
    ):
        (mirrors_dir / f"{agent_id}.yaml").write_text(
            yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
        )


@pytest.fixture()
def colony_root(tmp_path: Path) -> Path:
    """Return a fresh temporary colony root with mirrors seeded."""
    root = tmp_path / "teaching-colony"
    root.mkdir(parents=True, exist_ok=True)

    if COLONY_SRC.exists():
        shutil.copytree(COLONY_SRC, root / "colony", dirs_exist_ok=True)
        # Ensure minimal teacher mirror state so tests have a baseline even if
        # sub-agent A's seed differs. If short aliases are missing, mirror
        # the `<agent>-agent.yaml` files under the short id.
        mirrors_dir = root / "colony" / "mirrors"
        mirrors_dir.mkdir(parents=True, exist_ok=True)
        for long_id in ("teacher-agent", "librarian-agent", "sentinel-agent"):
            src = mirrors_dir / f"{long_id}.yaml"
            short = mirrors_dir / f"{long_id.split('-')[0]}.yaml"
            if src.exists() and not short.exists():
                shutil.copy(src, short)
    else:
        _write_minimal_colony(root)

    (root / "state").mkdir(parents=True, exist_ok=True)
    (root / "state" / "kb").mkdir(parents=True, exist_ok=True)
    return root
