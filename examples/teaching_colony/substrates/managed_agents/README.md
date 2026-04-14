# Managed Agents API Substrate Adapter

> **Audience lens:** Beekeeper — you are reading the mechanism. If you're an Operator or Newcomer, start at [../../README.md](../../README.md) or run the example in mock mode.
>
> **Design context (Architect lens):** see [`../../docs/design-spec.md`](../../docs/design-spec.md) for why this adapter exists and [`../../docs/implementation-plan.md`](../../docs/implementation-plan.md) for how it was scoped, including the research risk that was acknowledged upfront.

> **v1.6.0 status:** mock-mode fully working; live-mode implementation deferred to v1.7+. See [gaps.md](gaps.md) for the honest adequacy report.

## What this is

Implementation of the Teaching Colony substrate contract using the Anthropic **Claude Managed Agents** API (public beta, launched 2026-04-08). Demonstrates Principle 4 (Longevity by design) by running the same colony definition on a second substrate alongside Sub-agent B's Claude Code adapter.

At v1.6.0, mock mode produces deterministic event logs and Mirror final states that match the Claude Code substrate's output — which is the evidence the portability claim relies on. Live-mode operations are scaffolded structurally but gated behind `NotImplementedError` pending further implementation work; the design is fully specified in [api-research.md](api-research.md) and the v1.7+ upgrade path is listed in [gaps.md](gaps.md).

The adapter uses the standard `anthropic` Python SDK under `client.beta.*` with the `managed-agents-2026-04-01` beta header. It does **not** use `claude-agent-sdk` — that is a different package for the local Claude Code harness and belongs to Sub-agent B's substrate.

## Prerequisites

- Python 3.10+
- `pip install -r ../../requirements.txt`
- For mock mode: no API key required, no network access needed
- For live mode (v1.7+): `ANTHROPIC_API_KEY` environment variable, plus optional research-preview allowlist at <https://claude.com/form/claude-managed-agents> for native multi-agent dispatch and memory stores

## How to run (v1.6.0)

### Mock mode — works today

```bash
cd examples/teaching_colony
python run.py --substrate=managed-agents --mock
```

This runs the full Teaching Colony lifecycle using deterministic canned responses. Produces event logs and Mirror state changes that match the Claude Code substrate's output for the same cycle, modulo the `substrate` and `timestamp` fields.

### Live mode — v1.7+ target

Not supported in v1.6.0. The live-mode code paths raise `NotImplementedError`. See [gaps.md](gaps.md) for the exact list of operations that need to land and the order in which they should be implemented.

## Contract operation mapping

| Contract operation | Managed Agents mechanism | v1.6.0 status |
|---|---|---|
| `dispatch_agent`  | **Fallback (default):** one session per dispatch via `client.beta.sessions.create(agent=<id>)`, stream to `session.thread_idle`, return the final agent message. **Native (optional):** `callable_agents` + `agent_toolset_20260401` + session threads (research-preview allowlist required) | mock only, live deferred |
| `read_mirror`     | Local YAML read from `<root>/colony/mirrors/<agent_id>.yaml`. In live mode, this is also the handler for the `colony_read_mirror` client-executed custom tool | fully supported |
| `update_mirror`   | Client-executed custom tool `colony_update_mirror` — adapter deep-merges changes, hashes pre/post state, writes atomically, returns `AuditEntry` | mock only, live deferred |
| `record_event`    | Local JSONL append to `<root>/state/events.jsonl` with `substrate="managed-agents"` | fully supported |
| `read_kb`         | Client-executed custom tool `colony_read_kb` — adapter scans `<root>/state/kb/*.md` | mock only, live deferred |
| `write_kb`        | Client-executed custom tool `colony_write_kb` — adapter writes `<root>/state/kb/<slug>.md` with provenance frontmatter | mock only, live deferred |
| `co_sign`         | Client-executed custom tool `colony_cosign` — policy resolution logged as a session event for audit parity | mock only, live deferred |
| `classify_action` | Delegates to `colony/logic/classifier.py` (pure function, no substrate involvement) | fully supported |

All live-mode operations run as **client-executed custom tools**: Claude runs in the managed container and emits structured tool-use events; our adapter handles them in-process by reading and writing the local colony filesystem. The managed container's built-in `bash/read/write/edit` toolset (`agent_toolset_20260401`) is disabled — we don't need it, and keeping it off preserves byte-for-byte on-disk parity with the Claude Code substrate.

## Mock mode

Mock mode is mandatory for offline CI, tests, and the v1.6.0 portability demo. When `ManagedAgentsAdapter(..., mock=True)` is constructed, `dispatch_agent` returns deterministic canned responses keyed on `(agent_id, task, topic)` — the same response shape as the Claude Code substrate mock — and all file-I/O operations (mirrors, events, KB) run unchanged against the local filesystem. This lets the full lifecycle be exercised without an API key, without spending tokens, and without network access.

## Local state layout

Identical to the Claude Code substrate by design — this is what makes the two substrates portable against the same colony root:

```
<colony root>/
  colony/
    mirrors/<agent_id>.yaml       # read/updated via mirror ops
  state/
    events.jsonl                   # appended via record_event
    kb/<slug>.md                   # read/written via KB ops
```

The Managed Agents adapter never writes to the managed-side container filesystem — all colony state stays on the client.

## Tests

```bash
cd /Users/david.oliver/Documents/GitHub/agent-colony-pattern
python3 -m pytest examples/teaching_colony/substrates/managed_agents/tests/ -v
```

Current test state: **14 passed, 4 xfailed** — the xfails are expected and gate live-mode operations that land in v1.7+ (`dispatch_agent`, `update_mirror`, `write_kb`, `co_sign`).

## Gaps and path forward

See [gaps.md](gaps.md) for the v1.6.0 adequacy report — operation-by-operation status, what works today, what does not, why mock-mode is enough for the v1.6.0 portability claim, and the ordered v1.7+ upgrade path.

## Related documents

- [api-research.md](api-research.md) — full Phase 1 API research (primary sources, 10 questions, contract mapping, SDK recommendations)
- [gaps.md](gaps.md) — v1.6.0 adequacy report
- [../claude_code/README.md](../claude_code/README.md) — the other substrate for comparison
- [../../README.md](../../README.md) — Teaching Colony example top-level readme
