"""Unit tests for static_view.py — the v1.8.3 file-mode viewer writer.

Checks that `build_snapshot` produces HTML with the right mode switch,
embedded events, and meta-refresh tag; and that `write_snapshot` lands
a real file on disk with the same content.

Zero dependencies beyond stdlib. Pure synchronous tests — no asyncio.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from examples.teaching_colony import static_view  # noqa: E402


def _sample_events() -> list[dict]:
    return [
        {
            "type": "agent_boot",
            "actor": "registry-agent",
            "payload": {},
            "timestamp": "2026-04-15T08:00:00",
        },
        {
            "type": "dispatch.complete",
            "actor": "teacher-agent",
            "payload": {
                "answer": "Worker bees forage for nectar...",
                "topic": "beekeeping",
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cache_read_input_tokens": 20,
                },
            },
            "timestamp": "2026-04-15T08:00:02",
        },
    ]


def _sample_initial_state() -> dict:
    return {
        "type": "viewer.initial_state",
        "agents": ["registry-agent", "teacher-agent"],
        "kb_topics": ["beekeeping"],
        "budget": {
            "limit": 500_000,
            "used": 170,
            "fraction": 0.00034,
        },
    }


# ---------------------------------------------------------------------------
# build_snapshot — pure string generation
# ---------------------------------------------------------------------------


def test_build_snapshot_switches_view_mode_to_static() -> None:
    html = static_view.build_snapshot(_sample_events(), _sample_initial_state())
    assert 'data-view-mode="static"' in html
    assert 'data-view-mode="sse"' not in html


def test_build_snapshot_embeds_events_as_js_constant() -> None:
    events = _sample_events()
    html = static_view.build_snapshot(events, _sample_initial_state())
    assert "window.EMBEDDED_EVENTS" in html
    assert "window.EMBEDDED_INITIAL_STATE" in html
    # Spot-check: the actor name should appear in the JS constant
    assert "teacher-agent" in html
    assert "beekeeping" in html


def test_build_snapshot_injects_meta_refresh() -> None:
    html = static_view.build_snapshot(_sample_events(), _sample_initial_state(), interval_seconds=2)
    assert '<meta http-equiv="refresh" content="2">' in html


def test_build_snapshot_respects_custom_interval() -> None:
    html = static_view.build_snapshot(
        _sample_events(), _sample_initial_state(), interval_seconds=5
    )
    assert 'content="5"' in html


def test_build_snapshot_preserves_svg_layout() -> None:
    html = static_view.build_snapshot(_sample_events(), _sample_initial_state())
    # The SVG wireframe from viewer.html must still be present
    assert "<svg" in html
    assert 'id="user-node"' in html
    assert 'id="agent-teacher-agent"' in html
    assert 'id="event-log"' in html


# ---------------------------------------------------------------------------
# write_snapshot — file I/O
# ---------------------------------------------------------------------------


def test_write_snapshot_creates_file(tmp_path: Path) -> None:
    out = tmp_path / "live-view.html"
    written = static_view.write_snapshot(
        _sample_events(), _sample_initial_state(), out
    )
    assert written == out
    assert out.exists()
    assert out.stat().st_size > 1000  # must contain the whole template


def test_write_snapshot_creates_parent_dirs(tmp_path: Path) -> None:
    out = tmp_path / "nested" / "dir" / "live-view.html"
    static_view.write_snapshot(
        _sample_events(), _sample_initial_state(), out
    )
    assert out.exists()


def test_write_snapshot_content_matches_build_snapshot(tmp_path: Path) -> None:
    out = tmp_path / "live-view.html"
    static_view.write_snapshot(
        _sample_events(), _sample_initial_state(), out, interval_seconds=3
    )
    body = out.read_text(encoding="utf-8")
    # Same assertions as the build_snapshot tests
    assert 'data-view-mode="static"' in body
    assert "window.EMBEDDED_EVENTS" in body
    assert 'content="3"' in body


# ---------------------------------------------------------------------------
# Event reading helpers
# ---------------------------------------------------------------------------


def test_read_events_empty_when_missing(tmp_path: Path) -> None:
    assert static_view._read_events(tmp_path / "nope.jsonl") == []


def test_read_events_parses_jsonl(tmp_path: Path) -> None:
    events_path = tmp_path / "events.jsonl"
    events_path.write_text(
        json.dumps({"type": "a", "actor": "x", "payload": {}, "timestamp": "t"}) + "\n"
        + json.dumps({"type": "b", "actor": "y", "payload": {}, "timestamp": "t"}) + "\n",
        encoding="utf-8",
    )
    events = static_view._read_events(events_path)
    assert len(events) == 2
    assert events[0]["type"] == "a"
    assert events[1]["type"] == "b"


def test_read_events_skips_malformed_lines(tmp_path: Path) -> None:
    events_path = tmp_path / "events.jsonl"
    events_path.write_text(
        json.dumps({"type": "ok", "actor": "x", "payload": {}, "timestamp": "t"}) + "\n"
        + "garbled-not-json\n"
        + json.dumps({"type": "also_ok", "actor": "y", "payload": {}, "timestamp": "t"}) + "\n",
        encoding="utf-8",
    )
    events = static_view._read_events(events_path)
    assert len(events) == 2
    assert events[0]["type"] == "ok"
    assert events[1]["type"] == "also_ok"


def test_read_events_limit(tmp_path: Path) -> None:
    events_path = tmp_path / "events.jsonl"
    lines = [
        json.dumps({"type": f"t{i}", "actor": "x", "payload": {}, "timestamp": "t"})
        for i in range(10)
    ]
    events_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    events = static_view._read_events(events_path, limit=3)
    assert len(events) == 3
    # Limit takes the last N
    assert events[-1]["type"] == "t9"
