"""End-to-end smoke test for chat.py --view.

Runs chat.py in a subprocess with --view --no-open --view-port 0, reads
the "live viewer" line from stdout to extract the OS-picked port, hits
the index URL, asserts the viewer HTML is served.

This closes the loop from the user's perspective: the command they
actually type (python -m examples.teaching_colony.chat --view) must
actually start the viewer and the viewer must actually serve the page.
"""

from __future__ import annotations

import os
import re
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_chat_view_serves_the_viewer_page() -> None:
    cmd = [
        sys.executable,
        "-m", "examples.teaching_colony.chat",
        "--mock",
        "--view",
        "--no-open",
        "--view-port", "0",
    ]
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=str(REPO_ROOT),
        env=os.environ.copy(),
    )
    try:
        # Read stdout until we see the viewer URL line or give up
        port: int | None = None
        banner_lines: list[str] = []
        deadline = time.time() + 15
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                break
            banner_lines.append(line)
            m = re.search(r"http://127\.0\.0\.1:(\d+)", line)
            if m:
                port = int(m.group(1))
                break

        assert port is not None, (
            f"did not see a viewer URL in first 15s of stdout. "
            f"output: {''.join(banner_lines)!r}"
        )

        # Hit the viewer
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/", timeout=5
        ) as resp:
            assert resp.status == 200
            body = resp.read().decode("utf-8")
        assert "<svg" in body
        assert "Teaching Colony" in body

        # Tell the REPL to quit cleanly
        try:
            proc.stdin.write("quit\n")
            proc.stdin.flush()
        except Exception:
            pass

        # Wait up to 5 seconds for it to exit
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    finally:
        if proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
                proc.wait()
