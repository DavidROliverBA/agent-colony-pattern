# Managed Agents Substrate — Adequacy Report (v1.6.0)

## Scope of this document

This file documents what the Managed Agents substrate adapter supports
in v1.6.0 of the Teaching Colony example. It is the honest answer to
the question: "can the Agent Colony pattern run on the Anthropic
Managed Agents API?" as of 2026-04-14. The research behind this report
is in [api-research.md](api-research.md).

The short answer: **the contract interface is proven implementable on
Managed Agents in principle, and mock-mode runs end-to-end today. Live
mode is deferred to v1.7+.** The v1.6.0 portability claim rests on
mock-mode lifecycle parity between this adapter and the Claude Code
substrate, not on a live Managed Agents run.

## Operation-by-operation status

| Contract operation | v1.6.0 status | Notes |
|---|---|---|
| `dispatch_agent`  | mock only, live deferred | Mock returns canned responses keyed on `(agent_id, task, topic)`. Live path raises `NotImplementedError` — design is fully specified in api-research.md Q3 (single-session-per-dispatch fallback by default; optional `callable_agents` + `agent_toolset_20260401` native path gated on research-preview allowlist). |
| `read_mirror`     | fully supported | Reads local YAML from `<root>/colony/mirrors/<agent_id>.yaml` in both mock and live mode. This operation is intentionally substrate-agnostic — the mirror store is on the client's filesystem so both substrates share byte-for-byte on-disk shape. |
| `update_mirror`   | mock only, live deferred | Mock returns a deterministic `AuditEntry` with zeroed hashes. Live path raises `NotImplementedError` — the deep-merge-and-hash write is scaffolded but not implemented (would also need to emit a `mirror.updated` event via `record_event`). |
| `record_event`    | fully supported | Appends to `<root>/state/events.jsonl` in both mock and live mode with `substrate="managed-agents"`. No managed-side dependency — the event log is local to the adapter process. |
| `read_kb`         | mock only, live deferred | Mock returns `[]`. Live path scan of `<root>/state/kb/*.md` is scaffolded but returns `[]` until Sub-agent D implements the local-disk match logic. An optional upgrade path to Managed Agents memory stores exists but is research-preview-gated. |
| `write_kb`        | mock only, live deferred | Mock is a no-op. Live path raises `NotImplementedError` — atomic write with provenance frontmatter plus a `kb.written` event is scaffolded but not implemented. |
| `co_sign`         | mock only, live deferred | Mock returns a granted `Signature` against pre-registered policy. Live path raises `NotImplementedError` — policy resolution and session-event logging to be implemented in parity with the Claude Code substrate. |
| `classify_action` | fully supported | Pure function — delegates to `examples.teaching_colony.colony.logic.classifier.classify_action`. Identical across substrates; no substrate involvement. |

Summary: **3 of 8** operations are fully supported in v1.6.0 (`read_mirror`, `record_event`, `classify_action`). **5 of 8** work in mock mode only, with the live path scaffolded and research-specified but not yet implemented. **0 of 8** are gapped — nothing on the contract is fundamentally impossible on Managed Agents per Phase 1 research.

## What works today (v1.6.0)

Running `python run.py --substrate=managed-agents --mock` will:

- Instantiate `ManagedAgentsAdapter` against a colony root with the same on-disk layout as the Claude Code substrate (`colony/mirrors/`, `state/`, `state/kb/`, `state/events.jsonl`).
- Produce canned dispatch results for all six colony roles/tasks used by the Teaching Colony cycle (`teacher`/`teach`/`beekeeping`, `teacher`/`teach`/`agent-colony-pattern`, `librarian`/`curate`, `librarian`/`compute_coverage`, `librarian`/`propose_capability`, `sentinel`/`cosign`).
- Read mirror YAML from disk correctly (both in mock and live mode — this is a local file op).
- Append events to `state/events.jsonl` with `substrate="managed-agents"` stamped, so portability diffs against the Claude Code substrate surface only the `substrate` field and timestamps.
- Return a granted mock co-signature for action classes registered by the colony policy.
- Classify actions via the colony logic module — identical output to the Claude Code substrate for the same inputs.
- Pass the full Batch 1 test suite: 14 passing unit tests plus 4 xfails for live-mode gated operations.

## What does not work today

If someone tried to run this adapter against the real Managed Agents API in v1.6.0 (`mock=False`), they would see:

- **`dispatch_agent`** — raises `NotImplementedError` immediately. From api-research.md Q3: *"this feature requires research-preview allowlist access... Our adapter must handle the case where access is not granted. Fallback (no allowlist): for each dispatch, open a fresh session against the target agent's ID, send the input as a user message, stream events until `session.thread_idle`..."* The fallback is specified but not coded.
- **`update_mirror`** — raises `NotImplementedError`. The deep-merge-and-hash live write, atomic file replacement, and sibling `mirror.updated` event emission are scaffolded with TODO comments only.
- **`write_kb`** — raises `NotImplementedError`. The atomic write with frontmatter and the sibling `kb.written` event are scaffolded with TODO comments only.
- **`co_sign`** — raises `NotImplementedError`. Live policy resolution and audit-parity event logging are scaffolded with TODO comments only.
- **`read_kb`** — does not raise, but silently returns `[]` in live mode. This is a soft gap: the operation compiles and runs, but will always appear to find no KB entries until the local-disk scan is implemented.
- **`_get_client`** and **`_ensure_agents`** — the lazy Anthropic SDK client construction and the "create-or-load colony agents, cache IDs" bootstrap both raise `NotImplementedError`. No live call can happen at all until these land.
- **Native multi-agent dispatch** (`use_native_dispatch=True`) — gated on research-preview allowlist access (`callable_agents` + `agent_toolset_20260401` + session threads). Even when live mode ships, this path will only be available to allowlisted accounts. The fallback path is expected to be the default indefinitely.
- **Memory-store-backed KB** — gated on the same research-preview allowlist. The local-disk KB is the v1.6.0 (and v1.7 default) path; memory stores remain an opt-in upgrade.

## Why mock mode is enough for v1.6.0's portability claim

The v1.6.0 portability claim is that *the Agent Colony pattern's substrate contract is implementable on more than one substrate*, not that both substrates are simultaneously production-ready. Mock-mode lifecycle parity is the evidence. The mock-mode demonstration is meaningful because:

1. **The substrate contract interface is proven implementable twice** — both `ClaudeCodeAdapter` and `ManagedAgentsAdapter` subclass `SubstrateContract` and expose all eight operations with matching signatures. The fact that the Managed Agents adapter instantiates, passes its mock-mode tests, and drives the same lifecycle is the portability property.
2. **The classifier, graduation, and lifecycle logic run identically on both adapters** — `classify_action` delegates to the same colony logic module on both substrates, so any action classified by one is classified identically by the other. Graduation decisions, co-sign policies, and lifecycle transitions are colony-wide, not substrate-specific.
3. **The deterministic event logs can be diffed byte-for-byte (excluding substrate-specific metadata)** — both adapters append to `state/events.jsonl` with the same JSONL schema. A normalised diff (strip `substrate` and `timestamp`) should produce zero delta between a Claude Code mock run and a Managed Agents mock run of the same cycle.
4. **The colony definition (Mirrors, corpus, state layout) is substrate-independent by construction** — `colony/mirrors/*.yaml`, `state/kb/*.md`, and `state/events.jsonl` live in the client filesystem, owned by neither substrate. Swapping adapters does not move or rewrite the colony state.

Live-mode parity would strengthen the claim — it is a v1.7+ goal — but it is not load-bearing for v1.6.0.

## Path to v1.7+

In rough order of dependency:

1. **Implement `_get_client`** — lazy `anthropic.Anthropic()` construction, assert the SDK ships `client.beta.agents` and `client.beta.sessions`, honour the `managed-agents-2026-04-01` beta header (the SDK should set it automatically when `client.beta.*` is used).
2. **Implement `_ensure_agents`** — for each role in `colony/mirrors/`, create or `list` a `beta.agents` resource with the mirror's system prompt and the six `colony_*` custom tools registered. Disable `agent_toolset_20260401` (`default_config.enabled=False`). Cache `{role_name: agent_id}` in `self._agent_ids`. Create a minimal environment with no network access for reuse across sessions.
3. **Implement `dispatch_agent` fallback path** — open a fresh session against the target agent, stream events, dispatch `colony_*` tool calls back into the adapter's operation methods, reply with `user.custom_tool_result` (echoing `session_thread_id` where present), stop at `session.thread_idle`, return the final `agent.message` text parsed as JSON. Verified end-to-end before touching the native path.
4. **Implement `update_mirror` live path** — read current YAML, deep-merge `changes`, hash pre/post state, write atomically, append the `AuditEntry` to `autonomy.evolution_log`, emit a `mirror.updated` event via `record_event`. Must match the Claude Code substrate's logic byte-for-byte.
5. **Implement `write_kb` live path** — atomic write of `state/kb/<slug>.md` with provenance frontmatter, emit a `kb.written` event. Mirror the Claude Code substrate's `_parse_kb_doc` shape.
6. **Implement `read_kb` live scan** — glob `state/kb/*.md`, parse frontmatter, keyword match on topic/content. Same semantics as the Claude Code substrate.
7. **Implement `co_sign` live path** — either dispatch the sentinel agent (for parity with the Claude Code substrate's resolution) or resolve policy inline, then log the decision as a session event for audit parity.
8. **Validate portability** — run `run.py --substrate=managed-agents` (live) and `run.py --substrate=claude-code` (live) against the same colony root, diff the resulting event logs modulo `substrate` and `timestamp` fields, confirm zero semantic delta.
9. **Optional: native multi-agent dispatch** — only after allowlist access is confirmed. Gate behind `use_native_dispatch=True`, build the `callable_agents` orchestrator session, handle session-thread routing for `colony_*` tool calls originating in subagent threads.
10. **Optional: memory-store KB** — only after allowlist access is confirmed. Gate behind a second flag. Upgrade `read_kb`/`write_kb` to use `memory_search`/`memory_write` while keeping the local-disk path as the default.

None of these steps require contract changes. All are internal to `adapter.py`.

## Related documents

- [api-research.md](api-research.md) — full Phase 1 research (primary sources, 10 questions, contract mapping, recommendations for Sub-agent D)
- [../../../CHANGELOG.md](../../../CHANGELOG.md) — release history
- [../claude_code/README.md](../claude_code/README.md) — the other substrate for comparison
- [README.md](README.md) — Managed Agents adapter usage
