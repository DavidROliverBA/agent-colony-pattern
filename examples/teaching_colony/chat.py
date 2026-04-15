#!/usr/bin/env python3
"""Teaching Colony — interactive REPL (v1.8.0).

The v1.8.0 interactive entry point. A long-running session that dispatches
real Claude API calls against the existing substrate contract. Scoped
deliberately tight: two commands (``ask`` and ``quit``), no research walks
yet, no tool use, no graduation flow. That stuff is v1.9+.

Usage:

    python -m examples.teaching_colony.chat                # live mode (needs ANTHROPIC_API_KEY)
    python -m examples.teaching_colony.chat --mock         # offline deterministic
    python -m examples.teaching_colony.chat --reset        # wipe state/ first
    python -m examples.teaching_colony.chat --budget 100000   # tighter budget

The TEACHING_COLONY_TOKEN_BUDGET env var is the primary way to set the
session budget. The --budget flag is a convenience override.

Design notes:

* The loop uses ``asyncio`` even though v1.8.0 only has one synchronous
  command, because v1.9 will add background research walks that must not
  block the prompt. Building on asyncio from day one means that addition
  is a create_task away.
* ``ask`` dispatches to Teacher with ``{topic: "__auto__", question: ...}``
  and a KB snippet pre-selected by the adapter's read_kb method. v1.8.0
  has exactly one KB entry (the seeded beekeeping primer), so matching is
  trivial. v2.0 will replace this with a real RAG retrieval step.
* Everything prints to stdout. No colour, no fancy formatting, no history
  editing. The REPL is a skeleton, not a product.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import shutil
import sys
from pathlib import Path

# Make the package importable from the repo root and from inside the example.
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

try:
    from examples.teaching_colony.colony.logic.budget import (  # type: ignore
        Budget,
        BudgetExhausted,
        ENV_VAR as BUDGET_ENV_VAR,
    )
    from examples.teaching_colony.substrates.claude_code.adapter import (  # type: ignore
        ClaudeCodeAdapter,
        AGENT_MODELS,
    )
except ImportError:
    from colony.logic.budget import Budget, BudgetExhausted, ENV_VAR as BUDGET_ENV_VAR  # type: ignore
    from substrates.claude_code.adapter import ClaudeCodeAdapter, AGENT_MODELS  # type: ignore


MIRRORS = (
    "registry-agent",
    "chronicler-agent",
    "equilibrium-agent",
    "sentinel-agent",
    "librarian-agent",
    "teacher-agent",
)

HELP_TEXT = """\
Commands in v1.8.0:
  ask <question>        Dispatch to Teacher — real Claude answer, costs tokens
  help                  Show this message
  quit  (or q, exit)    Graceful shutdown; state persists

Commands coming in v1.9+:
  research "<topic>" from <url>     Librarian walks the web for a topic
  status                            Show running research tasks
  cancel research "<topic>"         Cancel a running walk
  knows [<topic>]                   Report KB coverage
  capabilities                      List what Teacher can currently teach

See examples/teaching_colony/docs/ for the v2.x roadmap.
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="teaching-colony-chat",
        description="Interactive REPL for the Teaching Colony (v1.8.0).",
    )
    p.add_argument(
        "--mock",
        action="store_true",
        help="Offline deterministic mode — no API calls, no token cost.",
    )
    p.add_argument(
        "--reset",
        action="store_true",
        help="Wipe state/ before starting (resets overlay mirrors, events, kb).",
    )
    p.add_argument(
        "--budget",
        type=int,
        default=None,
        help=f"Override session budget (defaults to ${BUDGET_ENV_VAR} or 500000).",
    )
    # v1.8.2 — live viewer flags
    p.add_argument(
        "--view",
        action="store_true",
        help="Start the v1.8.2 HTTP/SSE viewer alongside the REPL. Browser reads from http://127.0.0.1:8765.",
    )
    p.add_argument(
        "--view-port",
        type=int,
        default=8765,
        help="Port for the v1.8.2 viewer (default 8765). Pass 0 for OS-picked.",
    )
    p.add_argument(
        "--no-open",
        action="store_true",
        help="Don't auto-open the browser when --view or --view-file is set.",
    )
    # v1.8.3 — view fallbacks for environments where the HTTP viewer is blocked
    p.add_argument(
        "--view-native",
        action="store_true",
        help="v1.8.3: open a pywebview native window. No HTTP, no browser — "
             "uses the OS WebKit framework directly. Requires 'pip install pywebview'.",
    )
    p.add_argument(
        "--view-file",
        action="store_true",
        help="v1.8.3: write state/live-view.html and open via file://. "
             "Auto-refreshes every 2s. Zero new deps. The fallback when the "
             "HTTP viewer is blocked by endpoint security.",
    )
    return p.parse_args(argv)


def reset_state(state_dir: Path) -> None:
    """Wipe runtime state, preserving the seeded beekeeping KB entry.

    Matches run.py's reset_state behaviour: events, snapshots, graduation
    checklists, the state/mirrors overlay, and the runtime KB (except the
    seeded beekeeping.md) are all removed. A subsequent REPL run starts
    from the baseline.
    """
    for name in ("events.jsonl", "colony-snapshot.yaml"):
        path = state_dir / name
        if path.exists():
            path.unlink()
    for subdir in ("graduation-checklists", "mirrors"):
        path = state_dir / subdir
        if path.is_dir():
            shutil.rmtree(path)
    kb_dir = state_dir / "kb"
    if kb_dir.is_dir():
        for md in kb_dir.glob("*.md"):
            if md.name != "beekeeping.md":
                md.unlink()


def print_banner(adapter: ClaudeCodeAdapter, budget: Budget, mock: bool) -> None:
    mode = "mock (offline)" if mock else "live"
    mix = (
        f"teacher,librarian={AGENT_MODELS.get('teacher-agent', '?')}  |  "
        f"others={AGENT_MODELS.get('sentinel-agent', '?')}"
    )
    seeded_topics: list[str] = []
    kb_dir = adapter.kb_dir
    if kb_dir.exists():
        seeded_topics = sorted(md.stem for md in kb_dir.glob("*.md"))
    topics = ", ".join(seeded_topics) or "(none)"

    print("Teaching Colony — interactive session")
    print("━" * 60)
    print(f"Substrate:  claude-code ({mode})")
    print(f"Model mix:  {mix}")
    print(f"Agents:     {', '.join(a.replace('-agent', '') for a in MIRRORS)}")
    print(f"Topics:     {topics}")
    print(f"Budget:     {budget.usage.total:,} / {budget.limit:,} "
          f"({BUDGET_ENV_VAR}={budget.limit})")
    print("Commands:   ask <question>   |   help   |   quit")
    print()
    if mock:
        print("Note: running in --mock mode. No API calls. No token cost.")
    else:
        print("Note: live mode. Real Claude API calls. Real tokens. Real cost.")
        if os.environ.get("ANTHROPIC_API_KEY") is None:
            print("  ⚠ ANTHROPIC_API_KEY is not set — dispatches will fail.")
    print()
    print('Try: ask what do you know about beekeeping')
    print()


def _select_kb_snippet_and_topic(
    adapter: ClaudeCodeAdapter, question: str
) -> tuple[str, str]:
    """Pick the most-relevant KB entry for the question.

    Returns (snippet, topic). Snippet is the first 2000 chars of the
    matched doc; topic is the doc's declared topic (or filename stem).
    If nothing matches, returns ("", "__auto__") — Teacher will note that
    the colony doesn't know yet.

    v1.8.0 retrieval: dumb keyword match against the KB files, take the
    top result. Fine while the KB has one entry. v2.0 will replace this
    with real RAG.
    """
    docs = adapter.read_kb(question)
    if not docs:
        return "", "__auto__"
    top = docs[0]
    content = getattr(top, "content", "") or ""
    topic = getattr(top, "topic", "") or "__auto__"
    return content[:2000], topic


async def run_command(
    adapter: ClaudeCodeAdapter,
    budget: Budget,
    line: str,
) -> bool:
    """Run a single REPL command. Returns True to keep looping, False to quit."""
    stripped = line.strip()
    if not stripped:
        return True

    # Accept several quit synonyms
    if stripped.lower() in ("quit", "q", "exit", ":q"):
        print("\nFinal budget: " + budget.format_status())
        print("Goodbye.")
        return False

    if stripped.lower() == "help":
        print(HELP_TEXT)
        return True

    if stripped.lower().startswith("ask "):
        question = stripped[4:].strip()
        if not question:
            print("usage: ask <question>")
            return True

        if budget.is_exhausted():
            print(
                f"Budget exhausted ({budget.format_status()}). "
                f"Raise {BUDGET_ENV_VAR} and restart to continue."
            )
            return True

        kb_snippet, resolved_topic = _select_kb_snippet_and_topic(adapter, question)

        # Dispatch is synchronous in v1.8 but wrapped in to_thread so the
        # REPL stays interruptible. v1.9 will call the same pattern for
        # research walks — create_task for background, to_thread for blocking.
        try:
            result = await asyncio.to_thread(
                adapter.dispatch_agent,
                "teacher-agent",
                {
                    "task": "ask",
                    "topic": resolved_topic,
                    "question": question,
                    "kb_snippet": kb_snippet,
                },
            )
        except Exception as exc:
            print(f"error: dispatch failed: {exc}")
            return True

        answer = result.get("answer", "") if isinstance(result, dict) else str(result)
        if not answer:
            # Mock mode returns differently shaped dicts; try a fallback.
            answer = result.get("raw", "(no answer)") if isinstance(result, dict) else str(result)

        print()
        print(answer)
        print()
        print(budget.format_status())
        if budget.is_warning():
            print(
                f"  ⚠ over 80% of budget consumed — raise {BUDGET_ENV_VAR} "
                f"or quit soon to avoid hard stop"
            )
        return True

    # Forward-looking commands (v1.9+) that we want to mention helpfully.
    first_word = stripped.split(maxsplit=1)[0].lower()
    if first_word in ("research", "status", "cancel", "knows", "capabilities"):
        print(f"'{first_word}' is coming in v1.9+. v1.8.0 only supports 'ask' and 'quit'.")
        print("Type 'help' for the current command list.")
        return True

    print(f"unknown command: {stripped!r}")
    print("Type 'help' for the current command list.")
    return True


async def repl_loop(
    adapter: ClaudeCodeAdapter,
    budget: Budget,
    view_handle: object = None,
) -> int:
    """The main REPL read-eval-print loop."""
    prompt = "colony> "
    try:
        while True:
            try:
                line = await asyncio.to_thread(_read_line, prompt)
            except (EOFError, KeyboardInterrupt):
                print()
                print("Final budget: " + budget.format_status())
                print("Goodbye.")
                return 0

            if line is None:  # EOF from stdin (e.g. piped input exhausted)
                print()
                print("Final budget: " + budget.format_status())
                return 0

            keep_going = await run_command(adapter, budget, line)
            if not keep_going:
                return 0
    finally:
        if view_handle is not None:
            try:
                await view_handle.shutdown()
            except Exception:
                pass


async def _run_with_view(
    adapter: ClaudeCodeAdapter,
    budget: Budget,
    args,
) -> int:
    """Run the REPL with the v1.8.2 HTTP/SSE viewer attached (when --view)
    or the v1.8.3 file-mode viewer attached (when --view-file).

    The v1.8.3 --view-native mode is handled OUTSIDE asyncio in main(),
    because pywebview.start() requires the main thread on macOS.
    """
    view_handle = None
    file_task = None

    if args.view:
        try:
            from examples.teaching_colony import viewer  # type: ignore
        except ImportError:
            try:
                import viewer  # type: ignore
            except ImportError as exc:
                print(f"error: --view requested but viewer module not importable: {exc}")
                return 1
        try:
            port, view_handle = await viewer.start(
                repo_root=HERE,
                budget=budget,
                host="127.0.0.1",
                port=args.view_port,
            )
        except OSError as exc:
            print(f"error: viewer failed to bind port {args.view_port}: {exc}")
            print(f"       try --view-port 0 for an OS-picked free port")
            return 1
        url = f"http://127.0.0.1:{port}"
        print()
        print(f"  📺 live viewer: {url}")
        print()
        if not args.no_open:
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception:
                pass

    if args.view_file:
        # v1.8.3: write state/live-view.html periodically. No HTTP anywhere.
        try:
            from examples.teaching_colony import static_view  # type: ignore
        except ImportError:
            try:
                import static_view  # type: ignore
            except ImportError as exc:
                print(f"error: --view-file requested but static_view not importable: {exc}")
                return 1
        state_dir = HERE / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        output_path = state_dir / "live-view.html"
        # Write one snapshot immediately so the file exists before we open it
        try:
            events = static_view._read_events(state_dir / "events.jsonl")
            initial = static_view._current_state(HERE, budget)
            static_view.write_snapshot(events, initial, output_path, interval_seconds=2)
        except Exception as exc:
            print(f"error: failed to write initial snapshot: {exc}")
            return 1
        # Start the periodic rewrite task
        file_task = asyncio.create_task(
            static_view.periodic_snapshot(
                repo_root=HERE,
                budget=budget,
                output_path=output_path,
                interval_seconds=0.5,
                refresh_seconds=2.0,
            )
        )
        file_url = f"file://{output_path.resolve()}"
        print()
        print(f"  📺 live viewer (file mode): {file_url}")
        print(f"       auto-refreshes every 2 seconds — close the tab to stop watching")
        print()
        if not args.no_open:
            try:
                import webbrowser
                webbrowser.open(file_url)
            except Exception:
                pass

    try:
        return await repl_loop(adapter, budget, view_handle=view_handle)
    finally:
        if file_task is not None:
            file_task.cancel()
            try:
                await file_task
            except (asyncio.CancelledError, Exception):
                pass


def _read_line(prompt: str) -> str | None:
    """Read one line from stdin, returning None on EOF.

    Isolated so asyncio.to_thread can wrap it; also makes it trivially
    mockable in tests that feed input via stdin.
    """
    try:
        return input(prompt)
    except EOFError:
        return None


def _check_view_mutex(args) -> int | None:
    """v1.8.3: the three view modes (--view / --view-file / --view-native)
    are mutually exclusive. Return an exit code if the user set more than
    one, otherwise None.
    """
    view_flags = [
        ("--view", args.view),
        ("--view-file", args.view_file),
        ("--view-native", args.view_native),
    ]
    active = [name for name, on in view_flags if on]
    if len(active) > 1:
        print(
            f"error: view modes are mutually exclusive — got {', '.join(active)}. "
            f"Pick one.",
            file=sys.stderr,
        )
        return 2
    return None


def _run_native_view(adapter, budget, args) -> int:
    """v1.8.3 --view-native: pywebview takes the main thread, REPL runs
    in a background thread. When the window closes the REPL is signalled
    to stop; when the REPL quits, the window is destroyed.
    """
    try:
        from examples.teaching_colony import viewer_native  # type: ignore
    except ImportError:
        try:
            import viewer_native  # type: ignore
        except ImportError as exc:
            print(f"error: --view-native requested but viewer_native not importable: {exc}")
            return 1

    def repl_target() -> None:
        # Background thread: run the REPL loop on its own asyncio loop.
        try:
            asyncio.run(repl_loop(adapter, budget))
        except KeyboardInterrupt:
            pass

    try:
        viewer_native.start(
            repo_root=HERE,
            repl_thread_target=repl_target,
            title="Teaching Colony — live view",
        )
    except viewer_native.NativeViewerError as exc:
        print(f"\n{exc}\n", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    # v1.8.3: reject mutually-exclusive view flags up front
    mutex_err = _check_view_mutex(args)
    if mutex_err is not None:
        return mutex_err

    # v1.8.3: if --view-native is set, fail fast if pywebview is missing
    # so the user doesn't see the banner before the error.
    if args.view_native:
        try:
            from examples.teaching_colony import viewer_native  # type: ignore
        except ImportError:
            try:
                import viewer_native  # type: ignore
            except ImportError as exc:
                print(
                    f"error: --view-native requested but viewer_native not importable: {exc}",
                    file=sys.stderr,
                )
                return 1
        try:
            viewer_native._load_pywebview()
        except viewer_native.NativeViewerError as exc:
            print(f"\n{exc}\n", file=sys.stderr)
            return 1

    # Budget: command-line flag > env var > default
    if args.budget is not None:
        budget = Budget(limit=args.budget)
    else:
        budget = Budget.from_env()

    if args.reset:
        state_dir = HERE / "state"
        if state_dir.exists():
            reset_state(state_dir)

    adapter = ClaudeCodeAdapter(
        repo_root=HERE,
        mock=args.mock,
        budget=budget,
    )

    print_banner(adapter, budget, mock=args.mock)

    # v1.8.3: --view-native lives outside asyncio.run because pywebview
    # wants the main thread on macOS. The other view modes run inside
    # the asyncio event loop alongside the REPL.
    if args.view_native:
        return _run_native_view(adapter, budget, args)

    try:
        return asyncio.run(_run_with_view(adapter, budget, args))
    except KeyboardInterrupt:
        print()
        print("Final budget: " + budget.format_status())
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
