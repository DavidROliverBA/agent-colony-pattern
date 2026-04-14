"""Unit tests for the session budget tracker.

Part of v1.8.0. The Budget class is the first defence against a runaway
session burning through tokens — if it doesn't work, neither does cost
discipline. These tests deliberately over-test the class relative to its
size because a subtle off-by-one in fraction_used or is_exhausted would
silently allow overspend.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from examples.teaching_colony.colony.logic.budget import (  # noqa: E402
    Budget,
    BudgetExhausted,
    Usage,
    DEFAULT_LIMIT,
    ENV_VAR,
    WARNING_THRESHOLD,
)


# ---------------------------------------------------------------------------
# Usage arithmetic
# ---------------------------------------------------------------------------


def test_usage_starts_at_zero():
    u = Usage()
    assert u.total == 0
    assert u.input_tokens == 0
    assert u.output_tokens == 0


def test_usage_total_sums_all_four_fields():
    u = Usage(
        input_tokens=100,
        output_tokens=50,
        cache_creation_input_tokens=30,
        cache_read_input_tokens=10,
    )
    assert u.total == 190


# ---------------------------------------------------------------------------
# Budget construction
# ---------------------------------------------------------------------------


def test_budget_initialises_with_explicit_limit():
    b = Budget(limit=10_000)
    assert b.limit == 10_000
    assert b.usage.total == 0


def test_from_env_uses_env_var(monkeypatch):
    monkeypatch.setenv(ENV_VAR, "12345")
    b = Budget.from_env()
    assert b.limit == 12345


def test_from_env_falls_back_to_default_when_unset(monkeypatch):
    monkeypatch.delenv(ENV_VAR, raising=False)
    b = Budget.from_env()
    assert b.limit == DEFAULT_LIMIT


def test_from_env_falls_back_on_invalid(monkeypatch, capsys):
    monkeypatch.setenv(ENV_VAR, "not a number")
    b = Budget.from_env()
    assert b.limit == DEFAULT_LIMIT
    captured = capsys.readouterr()
    assert "warning" in captured.err
    assert "not a number" in captured.err


def test_from_env_falls_back_on_negative(monkeypatch, capsys):
    monkeypatch.setenv(ENV_VAR, "-100")
    b = Budget.from_env()
    assert b.limit == DEFAULT_LIMIT
    captured = capsys.readouterr()
    assert "warning" in captured.err


def test_from_env_accepts_empty_string_as_unset(monkeypatch):
    monkeypatch.setenv(ENV_VAR, "")
    b = Budget.from_env()
    assert b.limit == DEFAULT_LIMIT


# ---------------------------------------------------------------------------
# Record usage
# ---------------------------------------------------------------------------


def test_record_from_dict():
    b = Budget(limit=10_000)
    b.record({
        "input_tokens": 100,
        "output_tokens": 50,
        "cache_read_input_tokens": 20,
        "cache_creation_input_tokens": 30,
    })
    assert b.usage.total == 200
    assert b.usage.cache_read_input_tokens == 20


def test_record_accumulates_across_calls():
    b = Budget(limit=10_000)
    b.record({"input_tokens": 100, "output_tokens": 50})
    b.record({"input_tokens": 200, "output_tokens": 75})
    assert b.usage.input_tokens == 300
    assert b.usage.output_tokens == 125
    assert b.usage.total == 425


def test_record_from_object_with_attributes():
    class FakeUsage:
        input_tokens = 100
        output_tokens = 50
        cache_creation_input_tokens = 0
        cache_read_input_tokens = 20

    b = Budget(limit=10_000)
    b.record(FakeUsage())
    assert b.usage.input_tokens == 100
    assert b.usage.cache_read_input_tokens == 20


def test_record_handles_missing_fields():
    b = Budget(limit=10_000)
    b.record({"input_tokens": 100})  # no output_tokens etc
    assert b.usage.input_tokens == 100
    assert b.usage.output_tokens == 0


def test_record_handles_none_values():
    b = Budget(limit=10_000)
    b.record({"input_tokens": 100, "output_tokens": None})
    assert b.usage.input_tokens == 100
    assert b.usage.output_tokens == 0


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------


def test_fraction_used_starts_at_zero():
    b = Budget(limit=10_000)
    assert b.fraction_used() == 0.0


def test_fraction_used_at_half():
    b = Budget(limit=10_000)
    b.record({"input_tokens": 5_000})
    assert b.fraction_used() == 0.5


def test_fraction_used_clamps_at_one():
    b = Budget(limit=10_000)
    b.record({"input_tokens": 50_000})
    assert b.fraction_used() == 1.0  # clamped


def test_is_warning_fires_at_80_percent():
    b = Budget(limit=10_000)
    b.record({"input_tokens": 7_999})
    assert b.is_warning() is False
    b.record({"input_tokens": 1})  # now at exactly 8000
    assert b.is_warning() is True


def test_is_warning_false_when_exhausted():
    # At 100% we're exhausted, not 'warning'
    b = Budget(limit=10_000)
    b.record({"input_tokens": 10_000})
    assert b.is_exhausted() is True
    assert b.is_warning() is False


def test_is_exhausted_at_exactly_limit():
    b = Budget(limit=10_000)
    b.record({"input_tokens": 10_000})
    assert b.is_exhausted() is True


def test_is_exhausted_below_limit():
    b = Budget(limit=10_000)
    b.record({"input_tokens": 9_999})
    assert b.is_exhausted() is False


def test_remaining_drops_as_usage_grows():
    b = Budget(limit=10_000)
    assert b.remaining() == 10_000
    b.record({"input_tokens": 3_000})
    assert b.remaining() == 7_000
    b.record({"input_tokens": 20_000})  # overshoots
    assert b.remaining() == 0


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def test_format_status_shows_percentage():
    b = Budget(limit=10_000)
    b.record({"input_tokens": 2_500})
    status = b.format_status()
    assert "2,500" in status
    assert "10,000" in status
    assert "25.0" in status


def test_format_status_shows_cache_share_when_nonzero():
    b = Budget(limit=10_000)
    b.record({
        "input_tokens": 1_000,
        "cache_read_input_tokens": 500,
    })
    status = b.format_status()
    assert "500" in status
    assert "cache" in status


def test_format_status_omits_cache_share_when_zero():
    b = Budget(limit=10_000)
    b.record({"input_tokens": 1_000})
    status = b.format_status()
    assert "cache" not in status


def test_format_banner_matches_expected_shape():
    b = Budget(limit=500_000)
    banner = b.format_banner()
    assert "500,000" in banner
    assert ENV_VAR in banner


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_default_limit_is_500k():
    assert DEFAULT_LIMIT == 500_000


def test_warning_threshold_is_80_percent():
    assert WARNING_THRESHOLD == 0.80
