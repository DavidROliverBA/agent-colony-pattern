# Managed Agents API Research — 2026-04-14

## Summary

Anthropic launched **Claude Managed Agents** in public beta on 2026-04-08, six days before this research. It is a cloud-hosted agent harness accessed through the existing `anthropic` Python SDK under `client.beta.*`, gated by the `managed-agents-2026-04-01` beta header. It provides first-class primitives for named agents, persistent sessions with filesystem-backed containers, cross-session memory stores, and — critically — **client-executed custom tools** that let our adapter handle mirror/KB/event operations locally while Claude runs in the managed container. Multi-agent coordination (`callable_agents` + `agent_toolset_20260401`) is available but is currently a **research preview** feature requiring allowlist access, as are memory stores and outcomes. We can therefore build a working adapter for the full 8-operation substrate contract in v1.6.0 with **high confidence for the non-dispatch operations** and a **dependency/gate risk on `dispatch_agent`** — which we will work around with a single-session-per-dispatch fallback when research-preview access is not granted.

## Confidence

**High** — primary sources are the live Anthropic platform docs dated for the 2026-04-01 beta surface, fetched 2026-04-14, plus the PyPI listing for `claude-agent-sdk` 0.1.59 (released 2026-04-13). All design claims below are grounded in code examples quoted directly from the docs, not inferred.

## Primary sources used

- `https://platform.claude.com/docs/en/managed-agents/overview` — confirms the product exists, beta header, core concepts (Agent/Environment/Session/Events), supported built-in tools, rate limits (60 create/min, 600 read/min per org), and which features are research-preview-gated (outcomes, multi-agent, memory).
- `https://platform.claude.com/docs/en/managed-agents/multi-agent` — defines `callable_agents`, `agent_toolset_20260401`, session threads, one-level delegation, and the `session_thread_id` routing protocol for custom tool calls originating in subagent threads. **Research preview — allowlist required.**
- `https://platform.claude.com/docs/en/managed-agents/memory` — memory stores (`memstore_...`), `resources=[{type: memory_store, ...}]` on session create, `memory_list/search/read/write/edit/delete` tools auto-attached, immutable versioning, 100 KB per memory, max 8 stores per session. **Research preview — allowlist required.**
- `https://platform.claude.com/docs/en/managed-agents/tools` — confirms `type: custom` tools defined on the agent, executed by the client application (analogous to Messages API client-executed tools), with results posted back as `user.custom_tool_result` events. This is the mechanism that lets our substrate operations run locally.
- `https://pypi.org/project/claude-agent-sdk/` — separate package, version 0.1.59, 2026-04-13. This is the **local Claude Code harness SDK**, not the Managed Agents client; it is relevant to Sub-agent B, not to us.
- `https://github.com/anthropics/claude-agent-sdk-python` — confirms the two-surface model: `claude-agent-sdk` for local execution, `anthropic` SDK `beta.*` namespace for Managed Agents.

## Questions and answers

### Q1. Does Anthropic offer a Managed Agents API?

**Yes.** It is named **Claude Managed Agents**, launched in public beta on 2026-04-08. Access is enabled by default for all API accounts. All requests require the `anthropic-beta: managed-agents-2026-04-01` header; the SDK sets it automatically. Endpoints live under `https://api.anthropic.com/v1/` (`/agents`, `/environments`, `/sessions`, `/memory_stores`, etc.).

Not to be confused with the separately-packaged `claude-agent-sdk` (PyPI 0.1.59), which is the local Claude Code harness — that is Sub-agent B's substrate, not ours.

### Q2. Multiple named agents?

**Yes.** Agents are first-class persistent resources created via `client.beta.agents.create(name, model, system, tools, callable_agents, ...)` and returned with an `id` (`agent_...`) and `version`. They are referenced by ID when creating sessions: `client.beta.sessions.create(agent=agent.id, environment_id=...)`. Agent identity is stable across sessions.

For the Teaching Colony, each colony role (teacher, librarian, sentinel, and any others the colony adds) maps onto one Managed Agents `agent` resource.

### Q3. Inter-agent dispatch?

**Natively supported in research preview only.** The mechanism is:

1. Create each subordinate agent first and capture its `{id, version}`.
2. Create the coordinator agent with `tools=[{"type": "agent_toolset_20260401"}]` and `callable_agents=[{"type": "agent", "id": ..., "version": ...}, ...]`.
3. Start a single session referencing the coordinator. When the coordinator decides to delegate, the platform spawns a new **session thread** for the callee — isolated context, persistent across turns. Activity surfaces as `session.thread_created`, `agent.thread_message_sent`, `agent.thread_message_received`, `session.thread_idle` events on the primary stream.
4. Only **one level** of delegation is supported — callees cannot call further agents.

**Gate:** this feature requires research-preview allowlist access (`https://claude.com/form/claude-managed-agents`). Our adapter must handle the case where access is not granted.

**Fallback (no allowlist):** for each dispatch, open a fresh session against the target agent's ID, send the input as a user message, stream events until `session.thread_idle`, collect the final `agent.message` text, and return it. This simulates dispatch without requiring the research-preview feature, at the cost of parallel isolation — dispatches run sequentially instead of in parallel threads. For a ~6-dispatch demo cycle this is a non-issue.

### Q4. Persistent state?

**Three distinct layers**, of which only the first is unconditionally available:

1. **Session container filesystem** (default) — each session runs in a configured `environment` with a persistent container. Files written during a session survive across turns within that session. Sessions themselves are persistent server-side: you can resume and re-stream their event history. Good for per-session working state.
2. **Memory stores** (research preview, allowlist required) — `memstore_...` resources holding path-addressed text memories, attached to sessions via `resources=[{type: memory_store, memory_store_id, access}]`. The agent automatically gets `memory_read/write/edit/list/search/delete` tools. Memories are versioned (immutable `memver_...`). Max 8 stores per session, 100 KB per memory. Ideal for colony KB persistence if allowlisted.
3. **Externally-managed state** — the substrate contract's `Mirror`, `KB`, and `Event` stores can live in the client's local filesystem (the machine running the adapter) and be reached via client-executed custom tools. This is the fully-portable, non-gated path and is what our scaffolding targets. It also keeps the on-disk shape byte-for-byte identical to Sub-agent B's Claude Code substrate, which is the whole point of the v1.6.0 portability demo.

Our adapter defaults to **option 3 for all mirror/KB/event operations**. Sub-agent D may optionally upgrade KB operations to memory stores if allowlist access is available at implementation time.

### Q5. Tool definition + local file access?

**Fully supported via client-executed custom tools** — and this is the single most important finding for the adapter.

From the tools doc: *"Custom tools are analogous to user-defined client tools in the Messages API. ... Claude decides when and how to call them. The model never executes anything on its own. It emits a structured request, your code runs the operation, and the result flows back into the conversation."*

Tools are defined on the agent at creation time:

```python
{
  "type": "custom",
  "name": "colony_read_mirror",
  "description": "Read a colony agent's mirror (capabilities, boundaries, principles, metadata)...",
  "input_schema": {"type": "object", "properties": {"agent_id": {"type": "string"}}, "required": ["agent_id"]}
}
```

When Claude calls the tool, the API emits an event requiring the client to respond with `user.custom_tool_result`. Our adapter runs **arbitrary Python** in that handler — reading and writing files under the colony root's `state/` and `colony/mirrors/` on the local machine. This gives us byte-for-byte portability with Sub-agent B's Claude Code substrate: both adapters write to the same on-disk shape.

No sandbox restriction applies to the custom tool handler — it runs in *our* process, not in the managed container. The managed container is only used by the built-in `bash/read/write/edit` tools, which we do **not** need to enable for this adapter.

### Q6. SDK package name and version?

**`anthropic`** (standard Anthropic Python SDK) — access the Managed Agents surface under `client.beta.agents`, `client.beta.sessions`, `client.beta.memory_stores`, `client.beta.sessions.threads`, `client.beta.sessions.events`. Install: `pip install anthropic`. Any recent 2026 release supports the `managed-agents-2026-04-01` beta.

**NOT** `claude-agent-sdk` — that is a different package for the local Claude Code harness (Sub-agent B's territory). Mixing them up is the most likely research error.

### Q7. Auth?

`ANTHROPIC_API_KEY` environment variable, set via the `x-api-key` header (SDK handles automatically). Plus `anthropic-beta: managed-agents-2026-04-01` (SDK handles automatically). Plus a second beta header for any research-preview feature (multi-agent, memory, outcomes) — SDK handles this automatically when the corresponding parameters are used. Access to multi-agent, memory, and outcomes requires filling out `https://claude.com/form/claude-managed-agents` for allowlist.

### Q8. Rate limits and costs?

**Rate limits (per organisation):**

- Create endpoints (agents, sessions, environments, memory stores, events): **60/min**
- Read endpoints (retrieve, list, stream): **600/min**
- Plus organisation-level spend limits and tier-based Messages API rate limits.

**Cost:** session turns are billed at the underlying model's token rate (the doc defaults to `claude-sonnet-4-6`; we can use Haiku if we want to match Sub-agent B's `claude-haiku-4-5-20251001` default). A full Teaching Colony demo cycle is ~15 LLM calls. Well within a single-digit-dollar envelope and nowhere near the rate ceiling. No concerns.

### Q9. Streaming required?

**No.** Streaming is the default event transport (SSE via `client.beta.sessions.threads.stream(...)`), but the event history is **persisted server-side** and can be fetched with `client.beta.sessions.threads.events.list(...)` as a plain paginated list after the fact. The adapter can stream for responsiveness and fall back to pull-mode for tests. In mock mode no network calls happen at all.

### Q10. Useful features?

Several that simplify the implementation:

- **Client-executed custom tools** (Q5) — the core enabler. Maps 6 of the 8 contract operations cleanly.
- **Persistent session event history** — `record_event` can optionally be cross-checked against the session event log; no separate event store is needed if we lean on the managed side, though we still mirror events to local disk for audit parity with the Claude Code substrate.
- **Memory stores** (if allowlisted) — a natural home for `read_kb`/`write_kb`, with automatic versioning and audit.
- **Stable agent IDs across sessions** — `dispatch_agent` resolves a colony role name to a stable `agent_...` ID we can cache at adapter init.
- **Environment templates** — we don't need the managed container's bash/file tools at all; we can create an empty environment with no network access and disable the built-in toolset.
- **MCP server support** — not needed for v1.6.0 but available if the colony wants external tool providers later.

## Mapping to the substrate contract

| Contract operation | Managed Agents mechanism | Status |
|---|---|---|
| dispatch_agent | **Default (fallback):** one session per dispatch against the target agent's ID, stream to `session.thread_idle`, return the final agent message. **Optional native (research preview):** `callable_agents` + `agent_toolset_20260401` + session threads. | **simulated** (fallback always works; native path requires allowlist) |
| read_mirror | Client-executed custom tool `colony_read_mirror` → adapter reads local `<root>/colony/mirrors/<agent_id>.yaml`. Identical to the Claude Code substrate's on-disk shape. | **supported** |
| update_mirror | Client-executed custom tool `colony_update_mirror` → adapter deep-merges changes, hashes pre/post state, writes atomically, returns `AuditEntry`. | **supported** |
| record_event | Client-executed custom tool `colony_record_event` → adapter appends to `<root>/state/events.jsonl` with `substrate="managed-agents"`. | **supported** |
| read_kb | Client-executed custom tool `colony_read_kb` → adapter scans `<root>/state/kb/*.md`. Optional upgrade to memory stores if allowlisted. | **supported** |
| write_kb | Client-executed custom tool `colony_write_kb` → adapter writes `<root>/state/kb/<slug>.md` with provenance frontmatter. | **supported** |
| co_sign | Client-executed custom tool `colony_cosign` → adapter enforces pre-registered action-class policy and returns a `Signature`. Logic is colony-wide, not substrate-specific. | **supported** |
| classify_action | Non-substrate-specific — delegated directly to `examples.teaching_colony.colony.logic.classifier.classify_action`. | **supported** (delegated) |

## Overall verdict

- Number of operations fully supported: **7 of 8** (read_mirror, update_mirror, record_event, read_kb, write_kb, co_sign, classify_action)
- Number simulated: **1 of 8** (dispatch_agent — native path is research-preview-gated; adapter ships with the fallback as default)
- Number gapped: **0 of 8**
- Can the Managed Agents adapter run the full portability cycle in v1.6.0?
  - [x] **Yes, fully** — with `dispatch_agent` running in single-session-per-dispatch fallback mode by default, and an optional `use_native_dispatch=True` upgrade path for allowlist holders.
  - [ ] Partial — with specific gaps
  - [ ] No — fundamental blockers

The only real constraint is the fallback's serialisation of dispatches: native multi-agent would run parallel threads, our fallback runs them sequentially. For a demo cycle this is acceptable and should be recorded honestly in `gaps.md`.

## Recommendations for Sub-agent D (Batch 2)

1. **Use the `anthropic` SDK, not `claude-agent-sdk`.** This is the single most likely mistake. `from anthropic import Anthropic; client = Anthropic()` — then everything lives under `client.beta.*`.

2. **Build the adapter around client-executed custom tools, not around the built-in toolset.** Disable `agent_toolset_20260401` entirely (`default_config.enabled=false`) on all colony agents. The colony operations are ours, they don't need bash or a cloud container. Create a minimal environment with no network access.

3. **Register one custom tool per contract operation.** Use namespaced names: `colony_read_mirror`, `colony_update_mirror`, `colony_record_event`, `colony_read_kb`, `colony_write_kb`, `colony_cosign`. Long, detailed descriptions (3–4 sentences each) — the docs emphasise this heavily.

4. **Implement the event loop as:** send user message → stream events → on `agent.tool_use` for a `colony_*` tool, dispatch to the adapter method → reply with `user.custom_tool_result` (echoing `session_thread_id` if present, see Q3) → continue streaming → stop at `session.thread_idle`.

5. **For `dispatch_agent`, default to the fallback path.** Gate the native `callable_agents` path behind the `use_native_dispatch` constructor flag. Verify the fallback end-to-end before attempting the native path.

6. **Cache agent IDs at adapter `__init__` time.** On first use, create or `list` the colony agents and store `{role_name: agent_id}` in `self._agent_ids`.

7. **Local state shape must match the Claude Code substrate byte-for-byte.** Read Sub-agent B's `examples/teaching_colony/substrates/claude_code/adapter.py` for reference — colony_dir at `repo_root/colony`, mirrors at `repo_root/colony/mirrors/<id>.yaml`, state at `repo_root/state/`, events at `repo_root/state/events.jsonl`, kb at `repo_root/state/kb/*.md`. The scaffolding already matches this.

8. **Mock mode is not optional.** The demo must run offline. The scaffolding already wires mock-mode canned responses that match the Claude Code substrate's shape — keep those intact.

9. **Watch the 60/min create ceiling.** Don't create a new session per turn when you can reuse one. Use one session per full dispatch, not per tool call.

10. **Write `gaps.md` after implementation.** Document any operations where the managed API forced you to deviate from the ideal contract semantics (e.g. parallel vs sequential dispatch, event ordering, mirror atomicity). The honest gap report is part of the Principle 4 demonstration.
