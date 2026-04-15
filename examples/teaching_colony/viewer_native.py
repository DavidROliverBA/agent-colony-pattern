"""Native-window viewer — v1.8.3.

Opens a ``pywebview`` native macOS WebKit window (or the equivalent on
Windows / Linux) and pushes colony events into it via ``evaluate_js``.
No HTTP server. No browser. No corporate Chrome policy to worry about.

Why this exists
---------------

v1.8.2 shipped ``--view``, an asyncio HTTP + SSE server that the browser
connects to. On some corporate machines, endpoint security (Zscaler,
EDR, managed Chrome) actively refuses browser connections to
``127.0.0.1:8765`` even when the server is listening. The screenshot
the author received shows ``ERR_CONNECTION_REFUSED``, which is the
browser (or its proxy layer) refusing the connection — not the server
failing.

This module is the belt-and-braces fallback. ``pywebview`` wraps a
native OS webview. On macOS that's the ``WebKit.framework`` system
component, reached via ``pyobjc-framework-WebKit``. Corporate browser
policies target the browser apps (Chrome, Edge, Firefox) — they do not
govern native apps that embed WebKit. The Python process is, from
endpoint security's perspective, just another Python program drawing
a window.

Usage
-----

``pywebview`` is an **optional** runtime dependency. It is not in
``requirements.txt``. ``chat.py`` imports this module lazily only when
``--view-native`` is set, and if the import fails it prints a one-line
install instruction and exits.

``webview.start()`` must run on the main thread on macOS (Cocoa
requires it). The colony REPL therefore runs in a background thread
when this viewer is active. When the window closes, a shutdown event
is signalled so the REPL thread exits cleanly.

Constraints
-----------

- macOS: needs ``pyobjc-core``, ``pyobjc-framework-WebKit``,
  ``pyobjc-framework-security``. These come preinstalled with the
  system Python but must be installed for stand-alone Pythons.
- Windows: needs ``pythonnet`` and the WebView2 Runtime.
- Linux: needs GTK or QT bindings.

``pywebview`` handles all three — we just import it and let it pick
the backend.
"""

from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable


VIEWER_HTML_PATH = Path(__file__).parent / "viewer.html"
DEFAULT_WIDTH = 1100
DEFAULT_HEIGHT = 760
TAIL_POLL_SECONDS = 0.1


class NativeViewerError(Exception):
    """Raised when the native viewer cannot start — e.g. pywebview missing."""


def _load_pywebview():
    """Lazy import with a helpful error if the package is missing."""
    try:
        import webview  # type: ignore
    except ImportError as exc:
        raise NativeViewerError(
            "--view-native requires the 'pywebview' package.\n\n"
            "Install it with:\n"
            "    pip install pywebview\n\n"
            "On macOS, pywebview uses the system WebKit framework via "
            "pyobjc — no browser, no HTTP, no corporate proxy.\n\n"
            f"(Import error: {exc})"
        )
    return webview


def _prepare_html() -> str:
    """Read viewer.html from disk and switch it into native mode."""
    if not VIEWER_HTML_PATH.exists():
        raise NativeViewerError(
            f"viewer.html not found at {VIEWER_HTML_PATH}. "
            "Did the v1.8.2 ship include it?"
        )
    html = VIEWER_HTML_PATH.read_text(encoding="utf-8")
    html = html.replace(
        '<body data-view-mode="sse">',
        '<body data-view-mode="native">',
        1,
    )
    return html


class _EventPump(threading.Thread):
    """Background thread that tails events.jsonl and pushes each line into
    the pywebview window via evaluate_js.

    Separate from the REPL thread so one doesn't block the other. The
    window is thread-safe for evaluate_js calls.
    """

    def __init__(
        self,
        window: Any,
        events_path: Path,
        shutdown_event: threading.Event,
        poll_seconds: float = TAIL_POLL_SECONDS,
    ) -> None:
        super().__init__(daemon=True, name="colony-event-pump")
        self.window = window
        self.events_path = events_path
        self.shutdown_event = shutdown_event
        self.poll_seconds = poll_seconds
        self._offset = 0

    def run(self) -> None:
        # Wait a brief moment for the window to be ready before pushing
        time.sleep(0.3)
        try:
            # Initial replay of existing events (so a fresh window sees history)
            self._drain_existing()
            # Then tail for new events
            while not self.shutdown_event.is_set():
                self._poll_once()
                time.sleep(self.poll_seconds)
        except Exception as exc:  # pragma: no cover
            print(f"viewer_native: event pump crashed: {exc}", file=sys.stderr)

    def _drain_existing(self) -> None:
        if not self.events_path.exists():
            self._offset = 0
            return
        try:
            text = self.events_path.read_text(encoding="utf-8")
        except Exception:
            return
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            self._push(line)
        try:
            self._offset = self.events_path.stat().st_size
        except Exception:
            pass

    def _poll_once(self) -> None:
        if not self.events_path.exists():
            self._offset = 0
            return
        try:
            size = self.events_path.stat().st_size
        except Exception:
            return
        if size < self._offset:
            self._offset = 0  # truncated (--reset)
        if size == self._offset:
            return
        try:
            with self.events_path.open("r", encoding="utf-8") as f:
                f.seek(self._offset)
                chunk = f.read(size - self._offset)
                self._offset = size
        except Exception:
            return
        for raw in chunk.splitlines():
            line = raw.strip()
            if line:
                self._push(line)

    def _push(self, line: str) -> None:
        """Parse a JSONL line and inject it into the window's JS context."""
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return
        # evaluate_js must receive a pre-serialised JS expression. We use
        # json.dumps for the object literal so quoting is safe.
        payload = json.dumps(event)
        js = f"window.pushColonyEvent && window.pushColonyEvent({payload});"
        try:
            self.window.evaluate_js(js)
        except Exception as exc:  # pragma: no cover
            # Window probably closed mid-push. Signal shutdown.
            print(f"viewer_native: evaluate_js failed: {exc}", file=sys.stderr)
            self.shutdown_event.set()


def start(
    repo_root: Path,
    repl_thread_target: Callable[[], Any] | None = None,
    title: str = "Teaching Colony — live view",
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    gui: str | None = None,
) -> None:
    """Open the pywebview window and block until it is closed.

    Args:
        repo_root: the teaching_colony directory (events.jsonl at
                   repo_root/state/events.jsonl).
        repl_thread_target: a callable that runs the REPL loop. It
                   will be started on a background thread. When the
                   window closes, the REPL thread is signalled to stop
                   via ``sys.exit()`` in that thread — the thread is
                   expected to honour KeyboardInterrupt-style exits.
        title, width, height: window chrome.
        gui: pywebview backend override ('cocoa', 'qt', 'gtk', None=auto).

    Raises NativeViewerError if pywebview is not installed.
    """
    webview = _load_pywebview()
    repo_root = Path(repo_root)
    events_path = repo_root / "state" / "events.jsonl"
    html = _prepare_html()

    window = webview.create_window(
        title,
        html=html,
        width=width,
        height=height,
        resizable=True,
        confirm_close=False,
    )

    shutdown_event = threading.Event()

    pump = _EventPump(window, events_path, shutdown_event)

    repl_thread: threading.Thread | None = None
    if repl_thread_target is not None:
        def _repl_runner() -> None:
            try:
                repl_thread_target()
            except SystemExit:
                pass
            except Exception as exc:  # pragma: no cover
                print(f"viewer_native: repl thread error: {exc}", file=sys.stderr)
            finally:
                shutdown_event.set()
                # Ask the window to close so webview.start() returns
                try:
                    window.destroy()
                except Exception:
                    pass

        repl_thread = threading.Thread(
            target=_repl_runner, daemon=True, name="colony-repl"
        )

    def _on_start() -> None:
        """Called once the window is open. Kick off the pump and REPL."""
        pump.start()
        if repl_thread is not None:
            repl_thread.start()

    try:
        webview.start(_on_start, gui=gui)
    finally:
        shutdown_event.set()
        try:
            if repl_thread is not None and repl_thread.is_alive():
                repl_thread.join(timeout=2.0)
        except Exception:
            pass
