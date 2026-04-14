"""Live-mode dispatch tests — gated by ANTHROPIC_API_KEY and pytest -m live.

These tests actually call the Anthropic API. Each test costs real tokens
(each run of the whole file costs ~5-10k tokens, which is fractions of a
penny at Haiku pricing but isn't zero). They exist to prove that the v1.8.0
live-mode path works end-to-end against a real model, and specifically that
prompt caching fires on repeat dispatches.

Running:
    pytest -m live examples/teaching_colony/tests/test_live_dispatch.py -v

Without -m live, these tests are collected but skipped. In CI they should
NEVER run — gate the marker at the CI config level.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from examples.teaching_colony.substrates.claude_code.adapter import (  # noqa: E402
    ClaudeCodeAdapter,
)


pytestmark = pytest.mark.live


@pytest.fixture
def live_adapter(tmp_path: Path) -> ClaudeCodeAdapter:
    """A live adapter pointing at a throwaway copy of the example root.

    The real colony/ is copied into tmp_path so the live dispatch writes
    (events, any mirror updates) don't touch the repo.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY not set — skipping live tests")

    import shutil
    src = REPO_ROOT / "examples" / "teaching_colony"
    dst = tmp_path / "teaching_colony"
    shutil.copytree(
        src, dst, symlinks=False,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "state"),
    )
    (dst / "state").mkdir(exist_ok=True)
    (dst / "state" / "kb").mkdir(exist_ok=True)
    # Seed the beekeeping KB entry from baseline into the overlay-reachable state
    baseline_kb = src / "state" / "kb" / "beekeeping.md"
    if baseline_kb.exists():
        shutil.copy(baseline_kb, dst / "state" / "kb" / "beekeeping.md")

    return ClaudeCodeAdapter(repo_root=dst, mock=False)


def test_live_dispatch_teacher_beekeeping(live_adapter):
    """Dispatch Teacher with a real beekeeping question. Assert the answer
    is non-empty and plausibly about bees."""
    result = live_adapter.dispatch_agent(
        "teacher-agent",
        {
            "task": "ask",
            "topic": "beekeeping",
            "question": "What are worker bees?",
            "kb_snippet": "Worker bees forage for nectar and pollen. They "
                          "build wax comb and tend the brood. The queen is "
                          "the colony's only reproductive female.",
        },
    )
    assert isinstance(result, dict)
    answer = result.get("answer", "")
    assert answer, f"empty answer: {result!r}"
    # Loose assertion — real Claude will phrase things differently per call,
    # but the answer should mention at least one bee-related word.
    lowered = answer.lower()
    assert any(w in lowered for w in ("worker", "bee", "hive", "queen", "forage")), (
        f"answer doesn't mention any bee-related word: {answer!r}"
    )


def test_live_dispatch_prompt_cache_hit(live_adapter):
    """Two consecutive dispatches to the SAME agent should trigger Anthropic
    prompt caching on the second call. The usage block should report a
    non-zero cache_read_input_tokens on the second dispatch.

    This is the one test that directly proves prompt caching is working.
    If this fails but the others pass, the cache_control marker is probably
    being ignored or the model isn't eligible for caching.
    """
    # First dispatch — cache miss, cache creation
    live_adapter.dispatch_agent(
        "teacher-agent",
        {
            "task": "ask",
            "topic": "beekeeping",
            "question": "What is a queen bee?",
            "kb_snippet": "The queen is the only reproductive female in a colony.",
        },
    )
    first_usage = live_adapter.last_response_usage
    assert first_usage is not None
    # First call should show cache_creation_input_tokens > 0 (we just wrote the cache)
    # OR cache_read_input_tokens == 0 (cache was cold).

    # Second dispatch — same agent, same Mirror system prompt → should hit cache
    live_adapter.dispatch_agent(
        "teacher-agent",
        {
            "task": "ask",
            "topic": "beekeeping",
            "question": "What is a drone bee?",  # different question, same system prompt
            "kb_snippet": "Drones are the males in a honeybee colony.",
        },
    )
    second_usage = live_adapter.last_response_usage
    assert second_usage is not None
    cache_hit = second_usage.get("cache_read_input_tokens", 0)
    assert cache_hit > 0, (
        f"Second dispatch to same agent did NOT hit the prompt cache. "
        f"usage={second_usage}. Check that cache_control is being set "
        f"on the system block."
    )


def test_live_dispatch_sentinel_returns_json(live_adapter):
    """Supervisory agents use JSON-strict prompts. A Sentinel co-sign
    dispatch must return a parseable dict with a 'granted' field."""
    result = live_adapter.dispatch_agent(
        "sentinel-agent",
        {
            "task": "cosign",
            "action_class": "graduation_cosign",
            "actor": "librarian-agent",
            "subject": "teacher-agent",
            "reason": "test dispatch for v1.8 live smoke",
        },
    )
    assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"
    # The JSON-strict prompt should produce a response with 'granted' or at
    # least an 'error' field. Both count as the JSON path working — the
    # failure mode we're testing for is a prose response that doesn't parse.
    assert "granted" in result or "error" in result, (
        f"Sentinel response did not match expected schema. Got: {result!r}"
    )
