# Claude Code Substrate Adapter

> **Audience lens:** Beekeeper — you are reading the mechanism. If you're an Operator or Newcomer, start at [../../README.md](../../README.md) or run the example in mock mode.

## What this is

Implementation of the eight operations in the Teaching Colony substrate contract, using the Anthropic Python SDK to orchestrate a local colony of LLM-backed agents. This is "Claude Code substrate" in the sense that it follows the Claude Code idiom of dispatching sub-agents and composing their outputs — but it runs as a standalone Python program, not inside Claude Code itself.

## Prerequisites

- Python 3.10+
- `pip install -r ../../requirements.txt`
- `ANTHROPIC_API_KEY` environment variable (required for non-mock runs)

## How to run

### Full cycle against real Claude (costs tokens)

```bash
cd examples/teaching-colony
python run.py --substrate=claude-code
```

### Full cycle in deterministic mock mode (offline, no API key, no tokens)

```bash
cd examples/teaching-colony
python run.py --substrate=claude-code --mock
```

## Contract operation mapping

| Contract operation | Claude Code mechanism |
|---|---|
| `dispatch_agent` | `anthropic.messages.create` with the agent's Mirror as system prompt; response parsed as structured output |
| `read_mirror` | `yaml.safe_load(colony/mirrors/<agent_id>.yaml)` |
| `update_mirror` | Read → hash → apply deep merge → hash → append audit entry to `autonomy.evolution_log` → write back |
| `record_event` | Append JSONL line to `state/events.jsonl` |
| `read_kb` | Glob `state/kb/*.md`, keyword match on topic/content |
| `write_kb` | Write `state/kb/<slug>.md` with YAML frontmatter |
| `co_sign` | Dispatch Sentinel agent with the action; expect structured signature response |
| `classify_action` | Delegates to `colony/logic/classifier.py` (pure function, no LLM) |

## Mock mode

Mock mode is mandatory for offline CI and tests. When `ClaudeCodeAdapter(..., mock=True)` is constructed, `dispatch_agent` and `co_sign` return deterministic canned responses keyed on `(agent_id, task, topic)` instead of calling the API. All file-I/O operations (mirrors, events, KB) run unchanged. This lets the full lifecycle be exercised without an API key, without spending tokens, and without network access.

## Estimated token cost

Measure and report from `state/events.jsonl` after a real run. Placeholder: a full cycle consumes approximately N input + M output tokens with `claude-haiku-4-5`. Per-call counts are recorded in the event log.

## Test

```bash
pytest examples/teaching-colony/substrates/claude-code/tests/ -v
```
