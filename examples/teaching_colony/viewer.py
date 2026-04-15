"""Teaching Colony live viewer — v1.8.2.

A tiny asyncio HTTP server with Server-Sent Events that tails
``state/events.jsonl`` and streams new lines to any browser connected
to ``/events``. Serves a single-file ``viewer.html`` page at ``/``.

Design notes:

* **Pure stdlib.** No ``aiohttp``, no ``websockets``, no ``flask``. The
  HTTP parser is ~30 lines and only handles the two GET endpoints we
  care about. POST is deliberately not supported in v1.8.2 — the viewer
  is read-only. Bidirectional browser → REPL control is v1.8.3 or v2.0.
* **127.0.0.1 only.** Never ``0.0.0.0``. The viewer is a local demo, not
  a service. Binding to loopback makes it unreachable from other machines.
* **File tailing via polling.** A background asyncio task wakes every
  100ms and checks ``events.jsonl`` for growth. New lines are fanned out
  to all subscribers via their per-connection ``asyncio.Queue``. If the
  file shrinks (``--reset``) the offset resets to zero.
* **Initial state replay.** When a browser connects mid-session, it
  receives a ``viewer.initial_state`` event (current budget, agent
  roster, KB topics) followed by every existing event in the log in
  order. The browser then sees new events as they're written. This
  means a viewer opened at any time shows the full session context, not
  just future events.
* **XSS hygiene.** The server never interprets event payloads; it just
  forwards the raw JSON lines. All rendering is the browser's job, and
  ``viewer.html`` uses ``textContent`` throughout.

Usage from chat.py:

    from examples.teaching_colony import viewer

    server_task = asyncio.create_task(
        viewer.start(
            repo_root=HERE,
            budget=budget,
            host="127.0.0.1",
            port=8765,
        )
    )
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path


VIEWER_HTML_PATH = Path(__file__).parent / "viewer.html"
POLL_INTERVAL_SECONDS = 0.1
INITIAL_EVENT_REPLAY_LIMIT = 500  # cap replay at startup for large logs


@dataclass
class ViewerState:
    """Mutable state shared between the tail task and the per-connection handlers."""

    events_path: Path
    mirrors_dir: Path
    kb_dir: Path
    budget: object  # Budget instance or None; duck-typed to avoid import cycles
    subscribers: set  # set[asyncio.Queue]
    offset: int = 0

    def current_state_payload(self) -> dict:
        """Snapshot current session state for a newly-connected viewer."""
        # Agent roster from mirrors (read every connect — cheap on 6 files)
        agents = []
        if self.mirrors_dir.exists():
            for md in sorted(self.mirrors_dir.glob("*-agent.yaml")):
                agents.append(md.stem)
        # KB topic list
        kb_topics = []
        if self.kb_dir.exists():
            for md in sorted(self.kb_dir.glob("*.md")):
                kb_topics.append(md.stem)
        # Budget snapshot
        budget_payload = {"limit": 500_000, "used": 0, "fraction": 0.0}
        if self.budget is not None:
            try:
                budget_payload = {
                    "limit": self.budget.limit,
                    "used": self.budget.usage.total,
                    "input_tokens": self.budget.usage.input_tokens,
                    "output_tokens": self.budget.usage.output_tokens,
                    "cache_read_input_tokens": self.budget.usage.cache_read_input_tokens,
                    "cache_creation_input_tokens": self.budget.usage.cache_creation_input_tokens,
                    "fraction": self.budget.fraction_used(),
                }
            except Exception:
                pass
        return {
            "type": "viewer.initial_state",
            "agents": agents,
            "kb_topics": kb_topics,
            "budget": budget_payload,
        }


async def _tail_events(state: ViewerState) -> None:
    """Background task: poll events.jsonl for growth, fan new lines out.

    Cancelled by the caller on shutdown.
    """
    try:
        while True:
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            if not state.events_path.exists():
                # File may not exist yet; offset stays at 0
                state.offset = 0
                continue
            try:
                size = state.events_path.stat().st_size
            except FileNotFoundError:
                state.offset = 0
                continue
            if size < state.offset:
                # Truncated (e.g. --reset); start over
                state.offset = 0
            if size == state.offset:
                continue
            # New data available
            try:
                with state.events_path.open("r", encoding="utf-8") as f:
                    f.seek(state.offset)
                    chunk = f.read(size - state.offset)
                    state.offset = size
            except Exception as exc:
                print(f"viewer: tail read error: {exc}", file=sys.stderr)
                continue
            for raw_line in chunk.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                # Fan out to all subscribers; subscribers handle the JSON
                for queue in list(state.subscribers):
                    try:
                        queue.put_nowait(line)
                    except asyncio.QueueFull:
                        pass  # slow client; drop rather than block
    except asyncio.CancelledError:
        raise
    except Exception as exc:  # pragma: no cover
        print(f"viewer: tail task crashed: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# HTTP protocol — minimal manual handler
# ---------------------------------------------------------------------------


async def _read_request_line_and_headers(
    reader: asyncio.StreamReader,
) -> tuple[str, str] | None:
    """Parse the request line and drain headers. Returns (method, path) or None."""
    try:
        request_line = await asyncio.wait_for(reader.readline(), timeout=5.0)
    except (asyncio.TimeoutError, Exception):
        return None
    if not request_line:
        return None
    try:
        parts = request_line.decode("latin-1").strip().split()
    except Exception:
        return None
    if len(parts) < 2:
        return None
    method, path = parts[0], parts[1]
    # Drain headers until blank line
    while True:
        try:
            header = await asyncio.wait_for(reader.readline(), timeout=5.0)
        except asyncio.TimeoutError:
            break
        if not header or header == b"\r\n" or header == b"\n":
            break
    return method, path


async def _write_response(
    writer: asyncio.StreamWriter,
    status: int,
    content_type: str,
    body: bytes,
    *,
    extra_headers: dict[str, str] | None = None,
) -> None:
    status_text = {200: "OK", 404: "Not Found", 405: "Method Not Allowed"}.get(
        status, "OK"
    )
    headers = [
        f"HTTP/1.1 {status} {status_text}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Cache-Control: no-cache",
        "Connection: close",
    ]
    if extra_headers:
        for k, v in extra_headers.items():
            headers.append(f"{k}: {v}")
    header_bytes = ("\r\n".join(headers) + "\r\n\r\n").encode("latin-1")
    writer.write(header_bytes)
    writer.write(body)
    with contextlib.suppress(Exception):
        await writer.drain()


async def _handle_index(writer: asyncio.StreamWriter) -> None:
    try:
        html_bytes = VIEWER_HTML_PATH.read_bytes()
    except FileNotFoundError:
        await _write_response(
            writer,
            404,
            "text/plain; charset=utf-8",
            b"viewer.html not found",
        )
        return
    await _write_response(
        writer,
        200,
        "text/html; charset=utf-8",
        html_bytes,
    )


async def _handle_health(writer: asyncio.StreamWriter) -> None:
    await _write_response(writer, 200, "text/plain", b"ok")


async def _handle_events(
    writer: asyncio.StreamWriter,
    state: ViewerState,
) -> None:
    """SSE endpoint: push events to this client until it disconnects."""
    sse_headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/event-stream\r\n"
        "Cache-Control: no-cache\r\n"
        "Connection: keep-alive\r\n"
        "X-Accel-Buffering: no\r\n"
        "\r\n"
    ).encode("latin-1")
    writer.write(sse_headers)
    try:
        await writer.drain()
    except Exception:
        return

    def _send(line: str) -> bool:
        """Write one SSE frame. Returns False if the connection is dead."""
        try:
            writer.write(f"data: {line}\n\n".encode("utf-8"))
            return True
        except Exception:
            return False

    # 1. Initial state
    initial = json.dumps(state.current_state_payload())
    if not _send(initial):
        return
    try:
        await writer.drain()
    except Exception:
        return

    # 2. Replay existing events (capped)
    if state.events_path.exists():
        try:
            with state.events_path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
            for raw in lines[-INITIAL_EVENT_REPLAY_LIMIT:]:
                line = raw.strip()
                if line and not _send(line):
                    return
            try:
                await writer.drain()
            except Exception:
                return
        except Exception as exc:  # pragma: no cover
            print(f"viewer: replay error: {exc}", file=sys.stderr)

    # 3. Subscribe for new events
    queue: asyncio.Queue = asyncio.Queue(maxsize=1024)
    state.subscribers.add(queue)
    try:
        # Heartbeat every 15s so proxies don't time out the connection.
        # A None queue item is a shutdown sentinel — exit immediately.
        while True:
            try:
                line = await asyncio.wait_for(queue.get(), timeout=15.0)
            except asyncio.TimeoutError:
                if not _send(": heartbeat"):
                    break
                try:
                    await writer.drain()
                except Exception:
                    break
                continue
            if line is None:  # shutdown sentinel
                break
            if not _send(line):
                break
            try:
                await writer.drain()
            except Exception:
                break
    finally:
        state.subscribers.discard(queue)


async def _client_handler(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    state: ViewerState,
) -> None:
    try:
        parsed = await _read_request_line_and_headers(reader)
        if parsed is None:
            return
        method, path = parsed
        if method != "GET":
            await _write_response(writer, 405, "text/plain", b"only GET supported")
            return
        if path == "/" or path == "/index.html":
            await _handle_index(writer)
        elif path == "/health":
            await _handle_health(writer)
        elif path == "/events":
            await _handle_events(writer, state)
        else:
            await _write_response(writer, 404, "text/plain", b"not found")
    except Exception as exc:  # pragma: no cover
        print(f"viewer: client handler error: {exc}", file=sys.stderr)
    finally:
        with contextlib.suppress(Exception):
            writer.close()
        with contextlib.suppress(Exception):
            await writer.wait_closed()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def start(
    repo_root: Path,
    budget: object = None,
    host: str = "127.0.0.1",
    port: int = 8765,
) -> tuple[int, object]:
    """Start the viewer server. Returns (actual_port, server_handle).

    The server_handle is an asyncio.Server; call its ``close()`` and
    ``wait_closed()`` to shut down. Also returns a tail task that must
    be cancelled on shutdown.

    Args:
        repo_root: The teaching_colony directory. events.jsonl lives at
                   repo_root/state/events.jsonl; mirrors at
                   repo_root/colony/mirrors/.
        budget: Optional Budget instance for the initial_state snapshot.
        host: Bind host. MUST be 127.0.0.1 for v1.8.2.
        port: Bind port. Pass 0 to let the OS pick a free port.

    Raises:
        OSError: if the port is in use and no fallback is configured.
    """
    if host not in ("127.0.0.1", "localhost"):
        raise ValueError(
            f"viewer must bind to 127.0.0.1 only in v1.8.2, got {host!r}"
        )

    repo_root = Path(repo_root)
    state = ViewerState(
        events_path=repo_root / "state" / "events.jsonl",
        mirrors_dir=repo_root / "colony" / "mirrors",
        kb_dir=repo_root / "state" / "kb",
        budget=budget,
        subscribers=set(),
        offset=0,
    )

    async def _handler(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        await _client_handler(reader, writer, state)

    server = await asyncio.start_server(_handler, host, port)
    actual_port = server.sockets[0].getsockname()[1]

    tail_task = asyncio.create_task(_tail_events(state))

    # Return a small namespace that the caller can use to shut down.
    class Handle:
        def __init__(self):
            self.port = actual_port
            self.server = server
            self.tail_task = tail_task
            self.state = state

        async def shutdown(self) -> None:
            # v1.8.2: notify every SSE subscriber with a sentinel so their
            # handler loops exit immediately. Without this, a subscribe
            # loop sitting in queue.get() with a 15s heartbeat timeout
            # holds the connection open and blocks server.wait_closed().
            for queue in list(self.state.subscribers):
                try:
                    queue.put_nowait(None)  # sentinel
                except asyncio.QueueFull:
                    pass
            self.state.subscribers.clear()
            self.tail_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.tail_task
            self.server.close()
            try:
                await asyncio.wait_for(self.server.wait_closed(), timeout=1.0)
            except (asyncio.TimeoutError, Exception):
                pass

    return actual_port, Handle()


async def serve_forever(handle: object) -> None:
    """Convenience: block until the server is cancelled."""
    try:
        await handle.server.serve_forever()
    except asyncio.CancelledError:
        pass
