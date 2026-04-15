"""Structural sanity tests for viewer.html.

Loads the file and asserts that the required SVG ids (which the server
and its JS depend on) and the required JS function names are present.
This prevents drift between viewer.py (which references the file) and
viewer.html (which the JS drives).
"""

from __future__ import annotations

from pathlib import Path

import pytest


VIEWER_HTML = Path(__file__).resolve().parents[1] / "viewer.html"


@pytest.fixture(scope="module")
def html_body() -> str:
    assert VIEWER_HTML.exists(), f"viewer.html missing at {VIEWER_HTML}"
    return VIEWER_HTML.read_text(encoding="utf-8")


def test_viewer_html_has_required_svg_ids(html_body: str) -> None:
    # Core layout containers
    required_ids = [
        "svg-stage",
        "user-node",
        "kb-cells",
        "event-log",
        "event-log-entries",
        "answer-panel",
        "answer-text",
        "answer-meta",
        "budget-bar-fill",
        "budget-text",
        "budget-cache-text",
        "dispatch-arrows",
        "status-banner",
    ]
    for rid in required_ids:
        assert f'id="{rid}"' in html_body, f"viewer.html missing id={rid!r}"


def test_viewer_html_has_agent_nodes(html_body: str) -> None:
    for agent in (
        "registry-agent",
        "chronicler-agent",
        "equilibrium-agent",
        "sentinel-agent",
        "librarian-agent",
        "teacher-agent",
    ):
        assert f'id="agent-{agent}"' in html_body, (
            f"viewer.html missing agent node id=agent-{agent}"
        )


def test_viewer_html_js_hooks_present(html_body: str) -> None:
    """Function names the JS needs to respond to every event type."""
    required_functions = [
        "connectSSE",
        "handleEvent",
        "applyInitialState",
        "updateBudget",
        "renderKbCells",
        "onDispatchStart",
        "onDispatchComplete",
        "onKbRead",
        "onKbWritten",
        "onCosignGranted",
        "onMirrorUpdated",
        "drawDispatchArrow",
        "appendEventLog",
    ]
    for fn in required_functions:
        assert f"function {fn}" in html_body, (
            f"viewer.html missing JS function {fn!r}"
        )


def test_viewer_html_uses_textcontent_not_innerhtml(html_body: str) -> None:
    """XSS hygiene check. Every data-bearing assignment from the event
    stream must use textContent, not innerHTML, to prevent HTML injection
    from fetched content (which will arrive in v1.9)."""
    # We allow innerHTML = "" style clears, but not innerHTML = variable
    # usage. Rough check: innerHTML should NOT appear at all in v1.8.2
    # since we clear via removeChild in the renderer.
    assert ".innerHTML" not in html_body, (
        "viewer.html should not use innerHTML — use textContent or "
        "createElementNS + appendChild to avoid XSS from event payloads"
    )


def test_viewer_html_connects_to_events_endpoint(html_body: str) -> None:
    assert 'EventSource("/events")' in html_body or "EventSource('/events')" in html_body


def test_viewer_html_references_v1_9_deferrals_honestly(html_body: str) -> None:
    """The Internet placeholder must be explicitly labelled as v1.9."""
    assert "INTERNET (v1.9)" in html_body
    assert "not wired in v1.8.2" in html_body
