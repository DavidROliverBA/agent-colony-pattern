"""Unit tests for viewer.py — the v1.8.2 SSE server.

These tests run the asyncio server on port 0 (OS-picked) against a
throwaway state directory, exercise each endpoint via asyncio.to_thread
(so urllib's blocking fetch doesn't stall the event loop), and verify
the event stream shape.

No pytest-asyncio dependency — every test is a plain synchronous
function that calls asyncio.run() internally.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import sys
import threading
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from examples.teaching_colony import viewer  # noqa: E402


@pytest.fixture
def colony_workspace(tmp_path: Path) -> Path:
    """Copy the example into tmp_path so the server has a real colony to read."""
    src = REPO_ROOT / "examples" / "teaching_colony"
    dst = tmp_path / "teaching_colony"
    shutil.copytree(
        src, dst, symlinks=False,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "state"),
    )
    (dst / "state").mkdir(exist_ok=True)
    (dst / "state" / "kb").mkdir(exist_ok=True)
    baseline = src / "state" / "kb" / "beekeeping.md"
    if baseline.exists():
        shutil.copy(baseline, dst / "state" / "kb" / "beekeeping.md")
    return dst


def _fetch(url: str, timeout: float = 3.0) -> tuple[int, bytes]:
    """Blocking HTTP GET, for use inside asyncio.to_thread."""
    import urllib.request
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=timeout)
    return resp.status, resp.read()


def _fetch_sse_lines(url: str, max_lines: int, timeout: float = 3.0) -> list[str]:
    """Blocking SSE read via raw socket.

    urllib's resp.read() buffers in ways that hang on SSE streams
    (the response body has no Content-Length, so read() waits for the
    server to close or the buffer to fill). Using a raw socket with
    an explicit settimeout() avoids this.
    """
    import socket
    from urllib.parse import urlparse

    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 80
    path = parsed.path or "/"

    sock = socket.create_connection((host, port), timeout=timeout)
    sock.settimeout(timeout)
    try:
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Accept: text/event-stream\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        sock.sendall(req.encode("latin-1"))

        buf = b""
        lines: list[str] = []
        deadline = __import__("time").time() + timeout
        # Drain headers
        while b"\r\n\r\n" not in buf:
            if __import__("time").time() > deadline:
                return lines
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                return lines
            if not chunk:
                return lines
            buf += chunk
        _, buf = buf.split(b"\r\n\r\n", 1)

        # Read body until max_lines reached or timeout
        while len(lines) < max_lines and __import__("time").time() < deadline:
            while b"\n\n" in buf and len(lines) < max_lines:
                event, buf = buf.split(b"\n\n", 1)
                for line in event.decode("utf-8", errors="replace").splitlines():
                    if line.startswith("data: "):
                        lines.append(line[6:])
                        if len(lines) >= max_lines:
                            break
            if len(lines) >= max_lines:
                break
            try:
                chunk = sock.recv(4096)
            except socket.timeout:
                break
            if not chunk:
                break
            buf += chunk
        return lines
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        sock.close()


async def _run_with_server(
    workspace: Path,
    coro_factory,
    *,
    port: int = 0,
    host: str = "127.0.0.1",
    budget: object = None,
):
    """Spin up a viewer, await coro_factory(port), then shut down cleanly."""
    actual_port, handle = await viewer.start(
        repo_root=workspace, budget=budget, host=host, port=port,
    )
    try:
        return await coro_factory(actual_port)
    finally:
        await handle.shutdown()


# ---------------------------------------------------------------------------
# Endpoint tests
# ---------------------------------------------------------------------------


def test_health_endpoint(colony_workspace: Path) -> None:
    async def run(port: int):
        status, body = await asyncio.to_thread(
            _fetch, f"http://127.0.0.1:{port}/health"
        )
        return status, body

    status, body = asyncio.run(_run_with_server(colony_workspace, run))
    assert status == 200
    assert body == b"ok"


def test_index_serves_viewer_html(colony_workspace: Path) -> None:
    async def run(port: int):
        return await asyncio.to_thread(_fetch, f"http://127.0.0.1:{port}/")

    status, body = asyncio.run(_run_with_server(colony_workspace, run))
    assert status == 200
    body_str = body.decode("utf-8")
    assert "<svg" in body_str
    assert "Teaching Colony" in body_str
    # Required SVG ids the JS references
    assert 'id="user-node"' in body_str
    assert 'id="svg-stage"' in body_str
    assert 'id="kb-cells"' in body_str
    assert 'id="event-log"' in body_str
    assert 'id="answer-panel"' in body_str
    assert 'id="budget-bar-fill"' in body_str


def test_unknown_path_returns_404(colony_workspace: Path) -> None:
    import urllib.error

    async def run(port: int):
        def do_fetch():
            try:
                return _fetch(f"http://127.0.0.1:{port}/nonexistent")
            except urllib.error.HTTPError as exc:
                return exc.code, b""
        return await asyncio.to_thread(do_fetch)

    status, _ = asyncio.run(_run_with_server(colony_workspace, run))
    assert status == 404


def test_events_sends_initial_state(colony_workspace: Path) -> None:
    async def run(port: int):
        return await asyncio.to_thread(
            _fetch_sse_lines, f"http://127.0.0.1:{port}/events", 1
        )

    lines = asyncio.run(_run_with_server(colony_workspace, run))
    assert lines, "expected at least one SSE data line"
    first = json.loads(lines[0])
    assert first["type"] == "viewer.initial_state"
    assert "agents" in first
    assert "kb_topics" in first
    assert "budget" in first
    # The fixture copies the real colony — should have 6 agents
    assert len(first["agents"]) == 6
    assert "teacher-agent" in first["agents"]
    assert "beekeeping" in first["kb_topics"]


def test_events_replays_existing_log(colony_workspace: Path) -> None:
    """If events.jsonl already has entries, they're replayed on connect."""
    events_path = colony_workspace / "state" / "events.jsonl"
    events_path.write_text(
        json.dumps({"type": "agent_boot", "actor": "registry-agent",
                    "payload": {}, "timestamp": "2026-04-14T00:00:00"}) + "\n"
        + json.dumps({"type": "agent_boot", "actor": "teacher-agent",
                      "payload": {}, "timestamp": "2026-04-14T00:00:01"}) + "\n",
        encoding="utf-8",
    )

    async def run(port: int):
        return await asyncio.to_thread(
            _fetch_sse_lines, f"http://127.0.0.1:{port}/events", 3
        )

    lines = asyncio.run(_run_with_server(colony_workspace, run))
    # Expect: initial_state, then two agent_boot events
    assert len(lines) >= 3
    assert json.loads(lines[0])["type"] == "viewer.initial_state"
    assert json.loads(lines[1])["type"] == "agent_boot"
    assert json.loads(lines[2])["type"] == "agent_boot"


def test_events_picks_up_new_writes(colony_workspace: Path) -> None:
    """Events appended to events.jsonl after the viewer starts should
    be pushed to subscribed clients."""
    events_path = colony_workspace / "state" / "events.jsonl"
    events_path.write_text("", encoding="utf-8")  # empty

    async def run(port: int):
        received: list[str] = []

        def subscribe():
            # Use the same raw-socket helper as the other tests — urllib's
            # resp.read() buffers in ways that don't work for SSE.
            got = _fetch_sse_lines(f"http://127.0.0.1:{port}/events", 2, timeout=5.0)
            received.extend(got)

        t = threading.Thread(target=subscribe, daemon=True)
        t.start()

        # Give the subscriber time to connect and receive initial_state
        await asyncio.sleep(0.4)

        # Append a new event
        with events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "type": "dispatch.start",
                "actor": "teacher-agent",
                "payload": {"topic": "beekeeping"},
                "timestamp": "2026-04-14T00:00:10",
            }) + "\n")

        # Wait for the tail loop (poll is 100ms) and the subscriber thread
        await asyncio.to_thread(t.join, 4.0)
        return received

    received = asyncio.run(_run_with_server(colony_workspace, run))
    assert len(received) >= 2, f"only received: {received}"
    new_event = json.loads(received[1])
    assert new_event["type"] == "dispatch.start"
    assert new_event["actor"] == "teacher-agent"


def test_viewer_refuses_non_loopback_host(colony_workspace: Path) -> None:
    """v1.8.2 contract: must bind to 127.0.0.1 only."""
    async def run():
        with pytest.raises(ValueError, match="127.0.0.1"):
            await viewer.start(
                repo_root=colony_workspace, budget=None, host="0.0.0.0", port=0
            )
    asyncio.run(run())


def test_viewer_refuses_post(colony_workspace: Path) -> None:
    """No POST support in v1.8.2 — should return 405."""
    import urllib.error
    import urllib.request

    async def run(port: int):
        def do_post():
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/",
                data=b"hello",
                method="POST",
            )
            try:
                resp = urllib.request.urlopen(req, timeout=3)
                return resp.status
            except urllib.error.HTTPError as exc:
                return exc.code

        return await asyncio.to_thread(do_post)

    status = asyncio.run(_run_with_server(colony_workspace, run))
    assert status == 405
