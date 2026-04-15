"""End-to-end subprocess test for chat.py --view-file.

Runs chat.py in a subprocess with --view-file --no-open, pipes `quit`
into stdin, and verifies that the expected state/live-view.html file
exists afterwards with the right shape.

Also verifies the v1.8.3 mutex — --view and --view-file together must
return exit code 2 with a clear error.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_ROOT = REPO_ROOT / "examples" / "teaching_colony"


def _run_chat(args: list[str], stdin_text: str = "", timeout: int = 15) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", "examples.teaching_colony.chat", *args]
    return subprocess.run(
        cmd,
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO_ROOT),
        env=os.environ.copy(),
    )


def test_view_file_writes_live_view_html() -> None:
    """--view-file must write state/live-view.html that contains the
    embedded events and the static-mode marker."""
    # Clean up any previous file
    live_view = EXAMPLE_ROOT / "state" / "live-view.html"
    if live_view.exists():
        live_view.unlink()

    try:
        result = _run_chat(
            ["--mock", "--view-file", "--no-open"],
            stdin_text="ask what do you know about beekeeping\nquit\n",
        )
        assert result.returncode == 0, (
            f"chat.py exited with code {result.returncode}. "
            f"stdout={result.stdout[:500]!r} stderr={result.stderr[:500]!r}"
        )
        assert live_view.exists(), (
            f"live-view.html not written. stdout={result.stdout[-500:]!r}"
        )
        body = live_view.read_text(encoding="utf-8")
        assert 'data-view-mode="static"' in body
        assert "window.EMBEDDED_EVENTS" in body
        assert '<meta http-equiv="refresh"' in body
        assert "<svg" in body
        # The beekeeping answer should have made it into the embedded events
        assert "beekeeping" in body
        # The stdout should have printed the file:// URL
        assert "file://" in result.stdout
    finally:
        if live_view.exists():
            live_view.unlink()


def test_view_mutex_rejects_combination() -> None:
    """v1.8.3: --view and --view-file together must error out."""
    result = _run_chat(
        ["--mock", "--view", "--view-file", "--no-open"],
        stdin_text="",
        timeout=5,
    )
    assert result.returncode == 2
    combined = (result.stdout + result.stderr).lower()
    assert "mutually exclusive" in combined
    assert "--view" in combined
    assert "--view-file" in combined


def test_view_native_without_pywebview_fails_cleanly() -> None:
    """On a machine without pywebview installed, --view-native must fail
    with a helpful install message and exit code 1."""
    # Skip this test if pywebview IS installed (would actually open a window)
    try:
        import webview  # noqa: F401
        pytest.skip("pywebview is installed — skipping missing-dep test")
    except ImportError:
        pass

    result = _run_chat(
        ["--mock", "--view-native"],
        stdin_text="",
        timeout=5,
    )
    assert result.returncode == 1
    combined = (result.stdout + result.stderr).lower()
    assert "pywebview" in combined
    assert "pip install pywebview" in combined
    # Must NOT have printed the REPL banner — we fail before that in v1.8.3
    assert "Teaching Colony — interactive session" not in (result.stdout + result.stderr)
