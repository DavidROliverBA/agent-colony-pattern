"""Structural tests for the v1.8.3 viewer.html mode-switch machinery.

These tests make sure the template has the right hooks so static_view.py
can rewrite it into static mode and viewer_native.py can rewrite it into
native mode. Breaking any of these would break the v1.8.3 fallback paths
silently — the hooks are load-bearing, not cosmetic.
"""

from __future__ import annotations

from pathlib import Path

import pytest


VIEWER_HTML = Path(__file__).resolve().parents[1] / "viewer.html"


@pytest.fixture(scope="module")
def html_body() -> str:
    assert VIEWER_HTML.exists(), f"viewer.html missing at {VIEWER_HTML}"
    return VIEWER_HTML.read_text(encoding="utf-8")


def test_default_view_mode_is_sse(html_body: str) -> None:
    """The template ships in SSE mode for v1.8.2 backward-compatibility."""
    assert '<body data-view-mode="sse">' in html_body


def test_has_meta_refresh_placeholder(html_body: str) -> None:
    """static_view.py depends on the META_REFRESH_PLACEHOLDER comment."""
    assert "META_REFRESH_PLACEHOLDER" in html_body


def test_exposes_push_colony_event_global(html_body: str) -> None:
    """Both pywebview (--view-native) and the SSE handler call
    window.pushColonyEvent. The global must be defined."""
    assert "window.pushColonyEvent" in html_body


def test_has_init_view_mode_dispatcher(html_body: str) -> None:
    """The JS must have an init function that branches on data-view-mode."""
    assert "function initViewMode" in html_body
    assert "initViewMode()" in html_body


def test_init_dispatcher_handles_all_three_modes(html_body: str) -> None:
    for mode in ('"sse"', '"native"', '"static"'):
        assert mode in html_body, f"initViewMode is missing branch for {mode}"


def test_static_mode_reads_embedded_events(html_body: str) -> None:
    """The static-mode branch reads window.EMBEDDED_EVENTS, which
    static_view.py injects as a <script> block."""
    assert "window.EMBEDDED_EVENTS" in html_body
    assert "window.EMBEDDED_INITIAL_STATE" in html_body


def test_native_mode_does_not_connect_sse(html_body: str) -> None:
    """The native-mode branch MUST NOT call connectSSE — pywebview pushes
    events directly via evaluate_js and there is no HTTP endpoint."""
    # Grep for the native branch and ensure it contains a banner message
    # but doesn't call connectSSE inside the branch
    native_idx = html_body.find('if (mode === "native")')
    assert native_idx != -1
    # Find the next `return;` after the native branch start
    next_return = html_body.find("return;", native_idx)
    assert next_return != -1
    branch = html_body[native_idx:next_return]
    assert "connectSSE" not in branch, (
        "native mode must not call connectSSE — it has no HTTP endpoint"
    )
