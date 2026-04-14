"""Session-level budget tracking for the Teaching Colony REPL.

v1.8.0 introduces real Claude-backed dispatch. A session that doesn't track
its own cost is dangerous: a single runaway loop can burn through thousands
of dollars. The Budget class is the cheap, obvious defence.

Usage:

    budget = Budget.from_env()          # reads TEACHING_COLONY_TOKEN_BUDGET
    budget.record(response.usage)        # after every Anthropic API call
    if budget.is_exhausted():
        raise BudgetExhausted(budget.format_status())
    if budget.is_warning():
        print("WARNING: " + budget.format_status(), file=sys.stderr)

The TEACHING_COLONY_TOKEN_BUDGET environment variable overrides the default
of 500,000. Invalid values fall back to the default with a warning.

The 'warning' threshold is 80%. The 'exhausted' threshold is 100%. In v1.8.0
the only mechanism that spends budget is the REPL's `ask` command, so
exhausted means "no more `ask`". In v1.9+ when research walks exist, the
exhausted threshold blocks new walks but leaves a 10% carve-out for `ask`
calls against the already-collected KB — not implemented in v1.8.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field


DEFAULT_LIMIT = 500_000
ENV_VAR = "TEACHING_COLONY_TOKEN_BUDGET"
WARNING_THRESHOLD = 0.80


class BudgetExhausted(Exception):
    """Raised when the caller attempts a dispatch after the budget is full."""


@dataclass
class Usage:
    """Cumulative spend over a session.

    The four counters correspond directly to the Anthropic API's ``usage``
    fields: ``input_tokens``, ``output_tokens``, ``cache_creation_input_tokens``,
    and ``cache_read_input_tokens``. The ``cache_read`` field is the cheap
    cached portion on repeat hits; the ``cache_creation`` field is the one-
    time cost of establishing a cache entry. Both are counted against the
    budget — they are real — but displayed separately so a reader can see
    prompt caching paying off.
    """

    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0

    @property
    def total(self) -> int:
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_input_tokens
            + self.cache_read_input_tokens
        )


@dataclass
class Budget:
    """A simple cumulative budget against a hard limit."""

    limit: int
    usage: Usage = field(default_factory=Usage)

    @classmethod
    def from_env(cls) -> "Budget":
        """Construct a Budget from the TEACHING_COLONY_TOKEN_BUDGET env var.

        Invalid values fall back to the default and emit a warning to stderr.
        """
        raw = os.environ.get(ENV_VAR)
        if raw is None or raw.strip() == "":
            return cls(limit=DEFAULT_LIMIT)
        try:
            limit = int(raw)
            if limit <= 0:
                raise ValueError(f"non-positive: {limit}")
            return cls(limit=limit)
        except ValueError as exc:
            print(
                f"warning: {ENV_VAR}={raw!r} is not a positive integer "
                f"({exc}); falling back to default {DEFAULT_LIMIT:,}",
                file=sys.stderr,
            )
            return cls(limit=DEFAULT_LIMIT)

    def record(self, response_usage: object) -> None:
        """Parse an Anthropic API response's usage block and accumulate.

        Accepts either an Anthropic SDK ``Usage`` object (has attributes)
        or a plain dict (has keys). Unknown fields are ignored.
        """
        def _get(name: str) -> int:
            if hasattr(response_usage, name):
                value = getattr(response_usage, name)
                return int(value) if value is not None else 0
            if isinstance(response_usage, dict):
                return int(response_usage.get(name, 0) or 0)
            return 0

        self.usage.input_tokens += _get("input_tokens")
        self.usage.output_tokens += _get("output_tokens")
        self.usage.cache_creation_input_tokens += _get("cache_creation_input_tokens")
        self.usage.cache_read_input_tokens += _get("cache_read_input_tokens")

    def fraction_used(self) -> float:
        if self.limit <= 0:
            return 1.0
        return min(1.0, self.usage.total / self.limit)

    def is_warning(self) -> bool:
        return self.fraction_used() >= WARNING_THRESHOLD and not self.is_exhausted()

    def is_exhausted(self) -> bool:
        return self.usage.total >= self.limit

    def remaining(self) -> int:
        return max(0, self.limit - self.usage.total)

    def format_status(self, compact: bool = False) -> str:
        """Return a one-line status string for the REPL display."""
        pct = self.fraction_used() * 100
        used = self.usage.total
        limit = self.limit
        if compact:
            return f"{used:,} / {limit:,} ({pct:.1f}%)"
        cache_share = ""
        if self.usage.cache_read_input_tokens > 0:
            cache_share = (
                f" [{self.usage.cache_read_input_tokens:,} from cache]"
            )
        return f"budget: {used:,} / {limit:,} ({pct:.1f}%){cache_share}"

    def format_banner(self) -> str:
        """Return the REPL-startup banner line."""
        return (
            f"Budget:     {self.usage.total:,} / {self.limit:,}  "
            f"({ENV_VAR}={self.limit})"
        )
