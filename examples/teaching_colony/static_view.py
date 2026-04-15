"""Static file viewer — v1.8.3.

Writes a self-contained ``live-view.html`` to disk with the event stream
embedded as a JavaScript constant. The browser loads the file via ``file://``
(no HTTP, no proxy, no corporate browser policy in the way) and a
``<meta http-equiv="refresh">`` tag reloads it every N seconds so the
reader sees fresh state without any live connection.

This is the v1.8.3 fallback for environments where localhost HTTP is
blocked (the v1.8.2 ``--view`` server cannot be reached from the browser).
It is deliberately crude: every reload is a full re-render, so animations
between reloads are lost. The trade-off buys us pure ``file://`` loading,
which survives almost any endpoint security policy.

Usage from chat.py:

    from examples.teaching_colony import static_view

    snapshot_task = asyncio.create_task(
        static_view.periodic_snapshot(
            repo_root=HERE,
            budget=budget,
            output_path=HERE / "state" / "live-view.html",
            interval_seconds=0.5,
        )
    )
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path


VIEWER_HTML_PATH = Path(__file__).parent / "viewer.html"

#: String the template's META_REFRESH_PLACEHOLDER comment contains.
#: static_view replaces this with an actual <meta http-equiv="refresh"> tag.
META_REFRESH_COMMENT = "<!-- META_REFRESH_PLACEHOLDER"
META_REFRESH_COMMENT_END = "-->"


def _load_template() -> str:
    """Read viewer.html from disk as the template source."""
    if not VIEWER_HTML_PATH.exists():
        raise FileNotFoundError(
            f"viewer.html not found at {VIEWER_HTML_PATH}"
        )
    return VIEWER_HTML_PATH.read_text(encoding="utf-8")


def _inject_meta_refresh(html: str, interval_seconds: float) -> str:
    """Replace the meta-refresh placeholder with a real refresh tag.

    The template has a comment marker immediately after the viewport meta
    tag. We replace the entire comment block with the real meta tag.
    """
    start = html.find(META_REFRESH_COMMENT)
    if start == -1:
        # No placeholder — fall back to injecting after the charset meta.
        return html.replace(
            '<meta charset="utf-8">',
            f'<meta charset="utf-8">\n<meta http-equiv="refresh" content="{int(interval_seconds)}">',
            1,
        )
    end = html.find(META_REFRESH_COMMENT_END, start)
    if end == -1:
        return html
    end += len(META_REFRESH_COMMENT_END)
    return (
        html[:start]
        + f'<meta http-equiv="refresh" content="{max(1, int(interval_seconds))}">'
        + html[end:]
    )


def _switch_view_mode(html: str) -> str:
    """Rewrite the body tag from data-view-mode="sse" to "static"."""
    return html.replace(
        '<body data-view-mode="sse">',
        '<body data-view-mode="static">',
        1,
    )


def _inject_embedded_data(
    html: str,
    events: list[dict],
    initial_state: dict,
) -> str:
    """Inject a JavaScript constant that carries the embedded events.

    The constant is written just before the closing </head> tag so it's
    defined before the body script runs. `textContent`-safe because we
    use json.dumps with default string escaping.
    """
    payload = (
        "<script>\n"
        f"window.EMBEDDED_INITIAL_STATE = {json.dumps(initial_state)};\n"
        f"window.EMBEDDED_EVENTS = {json.dumps(events)};\n"
        "</script>\n"
    )
    return html.replace("</head>", payload + "</head>", 1)


def build_snapshot(
    events: list[dict],
    initial_state: dict,
    interval_seconds: float = 2.0,
) -> str:
    """Return the full HTML string for a static snapshot.

    Separated from the file-writing path so tests can assert on the
    string without touching disk.
    """
    html = _load_template()
    html = _switch_view_mode(html)
    html = _inject_meta_refresh(html, interval_seconds)
    html = _inject_embedded_data(html, events, initial_state)
    return html


def write_snapshot(
    events: list[dict],
    initial_state: dict,
    output_path: Path,
    interval_seconds: float = 2.0,
) -> Path:
    """Write a static snapshot of the colony to ``output_path``.

    Args:
        events: the list of events from state/events.jsonl to embed
        initial_state: the viewer.initial_state payload (budget, agents, kb_topics)
        output_path: where to write the HTML file
        interval_seconds: how often the meta-refresh should reload the page

    Returns the path that was written.
    """
    html = build_snapshot(events, initial_state, interval_seconds)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def _read_events(events_path: Path, limit: int = 2000) -> list[dict]:
    """Read events.jsonl, parse each line, cap at `limit` most-recent."""
    if not events_path.exists():
        return []
    lines: list[dict] = []
    try:
        with events_path.open("r", encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    lines.append(json.loads(raw))
                except json.JSONDecodeError:
                    continue
    except Exception as exc:  # pragma: no cover
        print(f"static_view: events read error: {exc}", file=sys.stderr)
    return lines[-limit:]


def _current_state(repo_root: Path, budget: object) -> dict:
    """Build the initial_state payload the same way viewer.py does."""
    agents: list[str] = []
    mirrors_dir = repo_root / "colony" / "mirrors"
    if mirrors_dir.exists():
        for md in sorted(mirrors_dir.glob("*-agent.yaml")):
            agents.append(md.stem)
    kb_topics: list[str] = []
    kb_dir = repo_root / "state" / "kb"
    if kb_dir.exists():
        for md in sorted(kb_dir.glob("*.md")):
            kb_topics.append(md.stem)
    budget_payload = {"limit": 500_000, "used": 0, "fraction": 0.0}
    if budget is not None:
        try:
            budget_payload = {
                "limit": budget.limit,
                "used": budget.usage.total,
                "input_tokens": budget.usage.input_tokens,
                "output_tokens": budget.usage.output_tokens,
                "cache_read_input_tokens": budget.usage.cache_read_input_tokens,
                "cache_creation_input_tokens": budget.usage.cache_creation_input_tokens,
                "fraction": budget.fraction_used(),
            }
        except Exception:
            pass
    return {
        "type": "viewer.initial_state",
        "agents": agents,
        "kb_topics": kb_topics,
        "budget": budget_payload,
    }


async def periodic_snapshot(
    repo_root: Path,
    budget: object,
    output_path: Path,
    interval_seconds: float = 0.5,
    refresh_seconds: float = 2.0,
) -> None:
    """Background task: rewrite the snapshot file every ``interval_seconds``.

    The separate ``refresh_seconds`` controls the ``<meta refresh>`` tag
    value — i.e. how often the browser will reload. The file rewrite
    cadence is faster so that when the browser reloads it sees fresh data.

    Cancel the task on shutdown; the file is left in place for later viewing.
    """
    repo_root = Path(repo_root)
    output_path = Path(output_path)
    events_path = repo_root / "state" / "events.jsonl"
    try:
        while True:
            try:
                events = _read_events(events_path)
                state = _current_state(repo_root, budget)
                write_snapshot(events, state, output_path, interval_seconds=refresh_seconds)
            except Exception as exc:  # pragma: no cover
                print(f"static_view: snapshot write error: {exc}", file=sys.stderr)
            await asyncio.sleep(interval_seconds)
    except asyncio.CancelledError:
        raise
