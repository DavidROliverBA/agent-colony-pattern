"""REPL smoke tests for v1.8.0.

These tests run the REPL as a subprocess in mock mode (no API calls) and
verify that the basic flows — banner, ask command, quit — all work
end-to-end. They are the load-bearing test that chat.py is actually a
working program, not just a file that happens to import.

The tests do NOT exercise live mode. Live-mode tests are in
test_live_dispatch.py and are gated by ANTHROPIC_API_KEY + pytest -m live.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CHAT_MODULE = "examples.teaching_colony.chat"


def _run_repl(stdin_text: str, extra_args: list[str] | None = None,
              env_extra: dict[str, str] | None = None,
              timeout: int = 15) -> subprocess.CompletedProcess:
    """Run chat.py as a subprocess with piped stdin."""
    import os
    cmd = [sys.executable, "-m", CHAT_MODULE, "--mock"]
    if extra_args:
        cmd.extend(extra_args)
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        cmd,
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO_ROOT),
        env=env,
    )


def test_repl_starts_and_prints_banner():
    """The REPL launches, prints the banner, and quits cleanly on 'quit'."""
    result = _run_repl("quit\n")
    assert result.returncode == 0, (
        f"REPL exited with code {result.returncode}. "
        f"stdout={result.stdout[:500]!r} stderr={result.stderr[:500]!r}"
    )
    out = result.stdout
    assert "Teaching Colony" in out
    assert "claude-code (mock" in out
    assert "Budget:" in out
    assert "Goodbye" in out


def test_repl_help_lists_current_commands():
    result = _run_repl("help\nquit\n")
    assert result.returncode == 0
    out = result.stdout
    assert "ask <question>" in out
    assert "quit" in out
    # v1.9+ preview must be mentioned so readers know what's coming
    assert "v1.9" in out
    assert "research" in out


def test_repl_ask_beekeeping_fires_canned_answer():
    """In mock mode, ask about beekeeping should return the canned answer
    containing 'worker' — proving the dispatch path is wired correctly."""
    result = _run_repl("ask what do you know about beekeeping\nquit\n")
    assert result.returncode == 0
    out = result.stdout.lower()
    assert "worker" in out, (
        f"Beekeeping answer should contain 'worker' (from the canned mock "
        f"response). Got: {result.stdout[-1000:]}"
    )


def test_repl_unknown_command_routes_helpfully():
    """A v1.9+ command should produce a helpful message, not a traceback."""
    result = _run_repl("research something\nquit\n")
    assert result.returncode == 0
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    assert ("v1.9" in result.stdout) or ("coming" in result.stdout.lower())


def test_repl_completely_unknown_command_also_routes_helpfully():
    """A word that isn't a command at all should also not traceback."""
    result = _run_repl("flabbergast\nquit\n")
    assert result.returncode == 0
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    assert "unknown" in result.stdout.lower() or "help" in result.stdout.lower()


def test_repl_empty_line_is_ignored():
    """Empty input should not crash or advance the budget."""
    result = _run_repl("\n\n\nquit\n")
    assert result.returncode == 0
    assert "Traceback" not in result.stdout


def test_repl_budget_override_flag():
    """--budget sets the limit visibly in the banner."""
    result = _run_repl("quit\n", extra_args=["--budget", "42000"])
    assert result.returncode == 0
    assert "42,000" in result.stdout


def test_repl_budget_env_var():
    """Env var is picked up by from_env."""
    result = _run_repl(
        "quit\n",
        env_extra={"TEACHING_COLONY_TOKEN_BUDGET": "123456"},
    )
    assert result.returncode == 0
    assert "123,456" in result.stdout


def test_repl_ask_followed_by_quit():
    """A full ask + quit cycle produces a final budget line."""
    result = _run_repl(
        "ask what are worker bees\nquit\n"
    )
    assert result.returncode == 0
    assert "Final budget" in result.stdout
    assert "Goodbye" in result.stdout
