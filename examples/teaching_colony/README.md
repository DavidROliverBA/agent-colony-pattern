# Teaching Colony — a substrate-portable example

> **Audience lens: Beekeeper.** This example demonstrates the Agent Colony
> pattern running on two different substrates with a single shared colony
> definition. If you're a Newcomer, start with
> [*It takes a village*](../../knowledge-base/writings/2026-04-12-it-takes-a-village.md).
> If you're an Architect, read [`substrate-contract.md`](substrate-contract.md).

## What this is

A six-agent colony that teaches the Agent Colony pattern using beekeeping
as its running metaphor. The colony boots with a single teaching topic
(beekeeping), learns the Agent Colony pattern from a supplied corpus,
proposes a new capability for its Teacher agent, drives that capability
through the Comprehension Contract (graduation checklist, classification,
co-signature), and finally answers a question it could not have answered
at boot time.

The same colony definition runs on two substrates:

- **Claude Code** — local-file substrate, agents are subprocess calls,
  events are JSONL lines, KB is a directory of markdown files.
- **Managed Agents API** — remote substrate, agents are Anthropic Managed
  Agents, events are thread messages, KB is uploaded files.

## Why this exists

The Agent Colony pattern claims to be substrate-portable. This example is
the smallest convincing proof of that claim: the `colony/` directory, the
six Agent Mirrors, the Structural Classifier, the Graduation logic, and the
lifecycle driver have **no substrate-specific imports**. Both adapters live
under `substrates/` and satisfy the same eight-operation
[Substrate Contract](substrate-contract.md).

Portability is not the only claim. The example also demonstrates that a
domain agent cannot grow a new capability without the Comprehension
Contract's review regime firing — graduation checklist, structural
classification, Sentinel co-signature, audit entry.

## The six agents

| Agent | Layer | Trust tier | Purpose |
|-------|-------|-----------|---------|
| registry-agent | L2 | Bounded | Catalogue of all agents in the colony |
| chronicler-agent | L2 | Bounded | Append-only Event Memory |
| equilibrium-agent | L2 | Bounded | Detects role overlap, proposes rebalancing |
| sentinel-agent | L2 | Bounded | Co-signs graduation events and security upgrades |
| librarian-agent | L3 | Observing | Reads the corpus, writes KB entries, proposes capability growth |
| teacher-agent | L3 | Observing | Teaches from the KB (beekeeping at boot; Agent Colony pattern after graduation) |

## How to use this example

Two ways in, depending on whether you want to see the mechanism or talk to it.

**The scripted walkthrough (v1.7.0)** is three runs of `run.py` that execute a fixed 9-step lifecycle in mock mode. It exists to demonstrate the substrate contract, the Comprehension Contract enforcement, and the portability claim. It does not involve real Claude calls — it's a verifiable smoke test of the mechanism.

**The interactive REPL (v1.8.0, new)** is `chat.py` — a long-running session that dispatches real Claude API calls through the same substrate. Type `ask <question>`, get a real answer grounded in the colony's knowledge base, watch the token budget count down. No research walks yet (that's v1.9), just the "one agent answers questions" slice.

Which one to start with depends on what you want to learn. The scripted walkthrough is cheaper (no tokens), takes 30 seconds, and answers "does this pattern actually work as described". The REPL is slower, costs real money, and answers "what does this actually feel like as a user." Both are worth running.

### Prerequisites

- Python 3.10 or newer
- About 50 MB of disk (the corpus is a copy of this repository's main pattern documents)
- For the interactive REPL in live mode: `ANTHROPIC_API_KEY` env var set

### Setup (one-off)

From the repository root:

```bash
cd examples/teaching_colony
pip install -r requirements.txt
```

That installs `anthropic`, `pyyaml`, `jsonschema`, and `pytest`. No network or build step for the scripted walkthrough. For the live REPL, set `ANTHROPIC_API_KEY` in your environment too.

## Interactive REPL — v1.8.0 (+ v1.8.2 live viewer)

**This is the first release that costs money to use.** Running `chat.py` in live mode makes real Claude API calls. Each `ask` question costs roughly 1,000–3,000 tokens (~1-3 pennies at Sonnet pricing, less with caching on repeat calls). A full afternoon of exploration against the default 500,000 token budget costs around $5. The scripted walkthrough remains free.

### Start an interactive session

```bash
# Offline, no API calls, no cost. Good for trying the REPL mechanics.
python -m examples.teaching_colony.chat --mock

# Live mode. Requires ANTHROPIC_API_KEY. Costs real tokens.
python -m examples.teaching_colony.chat

# Tighter budget for cost discipline (overrides the default 500,000).
TEACHING_COLONY_TOKEN_BUDGET=50000 python -m examples.teaching_colony.chat

# Reset state and start fresh.
python -m examples.teaching_colony.chat --reset

# v1.8.2: start the live browser viewer alongside the REPL.
# Opens http://127.0.0.1:8765 in your default browser. Watch agent
# dispatches animate, see the KB pulse on reads, watch the budget
# gauge tick up in real time. Zero new dependencies, localhost only.
python -m examples.teaching_colony.chat --view

# --view with all the knobs:
python -m examples.teaching_colony.chat --mock --view --view-port 9000 --no-open
```

### Three ways to view the colony (v1.8.2 + v1.8.3)

v1.8.2 shipped a browser viewer that talks to a local HTTP server. On some machines (locked-down corporate Chrome, managed Zscaler proxies, certain EDR products) that server is unreachable from the browser — you get `ERR_CONNECTION_REFUSED` on `http://127.0.0.1:8765` even though the server is running. v1.8.3 adds two fallback modes so the colony remains visually observable in those environments. Pick whichever works.

| Flag | How it renders | Pros | Cons |
|---|---|---|---|
| `--view` (v1.8.2) | Browser ↔ localhost HTTP/SSE | Richest UX, live animation, cache-hit visible, true streaming | Blocked by some endpoint security |
| `--view-native` (v1.8.3) | Native WebKit window via `pywebview` | No HTTP, no browser, no corporate proxy to worry about; real animations | Requires `pip install pywebview` |
| `--view-file` (v1.8.3) | Static HTML file auto-refreshed every 2s | Zero new deps, works via `file://` everywhere | No animation between reloads |

All three render the same wireframe from the same `viewer.html`. The event stream is the same `state/events.jsonl`. The difference is only the data-path.

### `--view` — HTTP/SSE browser viewer (v1.8.2, first choice)

Adding `--view` starts a tiny asyncio HTTP server on `127.0.0.1:8765` (or `--view-port N`) alongside the REPL loop. A single-file `viewer.html` renders the colony as:

- **User node** on the left — where the question enters
- **L1 Governance band** (Registry, Chronicler, Equilibrium), **L2 Immune band** (Sentinel), **L3 Domain band** (Librarian, Teacher) — agents laid out by architectural layer
- **Knowledge Base cells** at the bottom left — filled cells are real topics, dashed cells are slots that v1.9 research walks will fill
- **Internet node** — a dashed placeholder explicitly labelled "v1.9" so you can see where `fetch_url` will plug in later
- **Event log** on the right — every `state/events.jsonl` entry as it's written
- **Current answer panel** at the bottom — streamed into place when Teacher responds
- **Token budget gauge** at the top — live updates after every dispatch, with cache-hit breakdown

**It's read-only in v1.8.2.** You still type commands in the terminal. The browser is a passive observer. Bidirectional input (typing questions from the browser) is v1.8.3 or v2.0.

**It's localhost only.** The server binds to `127.0.0.1` — unreachable from other machines, even on the same LAN. No XSS risk: the viewer uses `textContent` (never `innerHTML`) for every field from the event stream.

**Shut it down cleanly** by quitting the REPL (`quit`, `q`, `exit`, or Ctrl-C). The viewer server is shut down as part of REPL exit.

### What the REPL can do in v1.8.0

- `ask <question>` — dispatch Teacher with your question + the best-matching KB snippet, get a real Claude answer
- `help` — show the command list
- `quit` (or `q`, `exit`) — graceful shutdown, state persists
- budget display after every dispatch, with warning at 80% and hard stop at 100%
- prompt caching on repeated dispatches (second call shows `[500 from cache]` in the budget line)

### `--view-native` — pywebview native window (v1.8.3)

```bash
pip install pywebview
python -m examples.teaching_colony.chat --view-native
```

Opens a native macOS WebKit window via `pywebview`. No HTTP server. No browser. Python pushes events directly into the window's JavaScript context via `evaluate_js`. Corporate browser policies target specific browser apps (Chrome, Edge, Firefox) — they don't govern the OS-level WebKit framework that `pywebview` embeds, so this works in environments where `--view` is blocked.

Requires `pip install pywebview`. On macOS that pulls in `pyobjc-core`, `pyobjc-framework-WebKit`, and `pyobjc-framework-security` — the PyObjC bindings that come preinstalled with system Python but need an explicit install for stand-alone Python distributions.

If you run `--view-native` without pywebview installed, you get a helpful one-line install instruction and a clean exit — nothing else is printed, nothing else runs. No banner, no REPL, just the install hint.

**Known limit:** `pywebview.start()` takes over the main thread on macOS (Cocoa requirement), so the REPL runs in a background thread when this mode is active. Closing the window gracefully shuts down the REPL. Ctrl-C in the terminal still quits cleanly.

### `--view-file` — static HTML with auto-refresh (v1.8.3)

```bash
python -m examples.teaching_colony.chat --view-file
```

Writes `state/live-view.html` to disk. The file contains the whole event stream embedded as a JavaScript constant, plus a `<meta http-equiv="refresh" content="2">` tag that reloads the page every 2 seconds. Your browser opens it via `file://` — which doesn't go through any proxy because no network request is made — and sees fresh state on every reload. `chat.py` rewrites the file every 500ms in the background, so each refresh catches up to the latest events.

Zero new dependencies. Pure Python stdlib. Works on any machine that can open an HTML file locally.

**Known limit:** it's not truly live. Each page reload is a full re-render. Animations that happen mid-dispatch aren't visible — you see before and after, not the transition. This is the trade-off for `file://` loading; any live-streaming approach needs HTTP which is exactly what we're trying to avoid here.

**Which mode should I pick?**

- Start with `--view` — it gives the best experience when it works.
- If you see `ERR_CONNECTION_REFUSED` on `127.0.0.1:8765`, your endpoint security is blocking localhost HTTP. Try `--view-native` next if you can install `pywebview`.
- If you can't install pywebview (corporate Python lockdown), `--view-file` always works. It's uglier but guaranteed.
- All three modes are mutually exclusive — you can't set more than one. `chat.py` errors out with a clear message if you do.

### What v1.8.0 does NOT support — coming in v1.9+

- `research "<topic>" from <url>` — Librarian walks the web for a new topic
- `status` / `cancel research` — track and control running research walks
- `knows <topic>` — report KB coverage
- `capabilities` — list what Teacher can currently teach
- Background concurrent research tasks
- Capability graduation triggered by research

These are all sketched in the v2.0 design spec. v1.8.0 ships the REPL foundation and the real-Claude dispatch path; v1.9.0 will add the tool system and research walks.

### Token budget — the primary cost control

The session budget defaults to 500,000 tokens. Override it by:

```bash
# Environment variable (preferred)
export TEACHING_COLONY_TOKEN_BUDGET=200000

# Per-invocation
TEACHING_COLONY_TOKEN_BUDGET=100000 python -m examples.teaching_colony.chat

# Command-line flag (overrides env var)
python -m examples.teaching_colony.chat --budget 50000
```

The budget tracks all four Anthropic usage counters (input, output, cache-creation, cache-read) and prints a one-line status after every dispatch. At 80% the REPL warns. At 100% the REPL refuses new `ask` dispatches with a message pointing at the env var.

### Cost in practice

Default model tiering: `claude-sonnet-4-6` for Teacher and Librarian (the agents that need real pedagogical quality), `claude-haiku-4-5-20251001` for the four supervisory agents (Registry, Chronicler, Equilibrium, Sentinel). v1.8.0 only actively dispatches Teacher (via `ask`), so Sonnet is the dominant cost. Prompt caching pays off after the second `ask` — the agent's Mirror stays the same across a session, so the system prompt is cached once and repeat-charged at ~10% of its original cost.

Rough envelope:

| Pattern | Tokens | Approx cost |
|---|---|---|
| Banner + one ask in mock mode | 0 | 0p |
| Banner + one ask in live mode (cold cache) | ~3,500 | ~1p |
| Each additional ask in the same session (warm cache) | ~1,200 | ~0.4p |
| 30-question session | ~40,000 | ~15p |
| Full 500,000 default budget consumed | 500,000 | ~$2-5 depending on model mix |

---

## Scripted walkthrough — v1.7.0

The scripted walkthrough below is the v1.7.0 mechanism demo. It still works and is still worth running to see the pattern execute end-to-end in mock mode without any cost.

### Run 1 — see the whole lifecycle on Claude Code

```bash
python run.py --substrate=claude-code --mock --reset
```

`--reset` wipes `state/` so you always start from a known baseline. `--mock` means no real Claude API calls — the adapter uses canned deterministic responses so you can see the full lifecycle offline.

**What happens:**

1. The six agents are registered from their YAML Mirrors in `colony/mirrors/`
2. Teacher answers a baseline beekeeping question using the seeded KB entry
3. Librarian reads the pattern corpus and curates new KB entries
4. Librarian computes coverage and proposes that Teacher acquire `teach_agent_colony_pattern`
5. The Structural Classifier fires — the review regime formula short-circuits to `Peer Review` because a capability addition is a Novel action class (§7.4)
6. A graduation checklist is generated in `state/graduation-checklists/`
7. Sentinel co-signs the graduation
8. Teacher's Mirror is updated with an append-only audit entry containing pre/post state hashes and a rollback window
9. Teacher answers a new Agent Colony pattern question it could not have answered at boot time
10. A colony snapshot is written

**What to expect on stdout:**

A summary table listing all six agents, their capabilities, and any capability changes that happened during the run. The last line should read:

```
- teacher-agent acquired 'teach_agent_colony_pattern' (co-signed by sentinel-agent)
```

**What to inspect after the run:**

```bash
# The append-only event log — every colony event, in order
cat state/events.jsonl | python3 -m json.tool

# Summary of event types
python3 -c "
import json
from collections import Counter
c = Counter(json.loads(l)['type'] for l in open('state/events.jsonl'))
for t, n in sorted(c.items()): print(f'  {n:3d}  {t}')
print('total:', sum(c.values()))
"

# The updated Teacher Mirror — evolution_log has a new entry
cat colony/mirrors/teacher-agent.yaml

# The graduation checklist that gated the capability addition
ls state/graduation-checklists/
cat state/graduation-checklists/*.yaml

# What the colony now knows about the pattern
ls state/kb/
```

On the Claude Code substrate you should see ~42 events covering 14 unique event types, including `graduation_checklist` (the checklist being generated), `cosign.granted` (Sentinel's co-signature), `mirror.updated` with non-empty `pre_state_hash` and `post_state_hash` fields in its payload, and a new entry in Teacher's `autonomy.evolution_log`. The exact numbers may drift as the adapter evolves; the key thing is that all three — the checklist, the co-signature, and the Mirror update with hashes — appear in order.

> **Known follow-up (v1.7+):** the Claude Code adapter writes Mirror updates back to `colony/mirrors/` which is git-tracked. Running the example locally will therefore leave `teacher-agent.yaml` modified in your working copy. Run `git restore examples/teaching_colony/colony/mirrors/teacher-agent.yaml` to revert before committing anything else. The proper fix — moving Mirror writes to `state/` or making the adapter copy-on-write — is tracked for v1.7+.

### Run 2 — reset and re-run to verify determinism

```bash
python run.py --substrate=claude-code --mock --reset
```

Same command, run again. The whole point of mock mode is determinism: given the same corpus and the same Mirrors, the colony should produce the same observable events (excluding timestamps and hashes derived from timestamps). This run is how you verify that.

**What to check:**

```bash
# Count events — should match Run 1 exactly
wc -l state/events.jsonl
```

You should see the same number of events as Run 1 (currently around 42 on Claude Code — the exact number will drift as the adapter evolves but must stay the same across two runs of the same substrate), the same event types in the same order, and the same Teacher capability change. Timestamps will differ. The determinism is what makes the pattern testable — live runs can be replayed, graduations can be audited after the fact, and regressions are detectable.

### Run 3 — same colony on the Managed Agents substrate

```bash
python run.py --substrate=managed-agents --mock --reset
```

This is the portability claim made concrete. The identical six Agent Mirrors, the identical classifier, the identical graduation logic, the identical corpus — now orchestrated by a completely different substrate adapter.

**What to expect:**

The same summary table, the same capability change on Teacher, the same co-signer. The underlying Python code in `substrates/managed_agents/adapter.py` is structurally different from `substrates/claude_code/adapter.py` — different imports, different class, different mock response plumbing — but the observable *graduation* is identical. That is Principle 2 (*Identity over implementation*) and Principle 4 (*Longevity by design*) in running code for the first time.

**One thing you will notice is different — the raw event count.** Claude Code emits about 42 events; Managed Agents emits about 22. The 20-event difference is not noise. The Claude Code adapter emits additional events from inside its own operations — `dispatch.complete` for every agent dispatch, `mirror.updated` on every mirror write, `kb.written` on every KB entry, `cosign.granted` when Sentinel signs — on top of the 22 events the substrate-independent lifecycle driver emits. The Managed Agents adapter's mock operations are currently no-ops for `update_mirror`, `write_kb`, and `co_sign` (no side effects, no events), and it does not emit a `dispatch.complete` event from `dispatch_agent`. So you see only the 22 driver events.

The driver events on their own are enough to observe the graduation: both substrates emit `classification`, `cosign`, `graduation_checklist`, `mirror_update`, and the capability-change summary. The adapter-internal events are observability richness, not the graduation proof.

**Consequences of the Managed Agents no-op mocks at v1.6.1:**

- Teacher's Mirror on disk is **not** updated on a Managed Agents mock run. The graduation event is recorded in `events.jsonl` but the state change to the YAML file is not persisted. If you `cat colony/mirrors/teacher-agent.yaml` after a Managed Agents run, it looks unchanged.
- The `state/kb/` directory is not populated by Managed Agents mock writes.

This is why the portability parity tests for full event-log sequence and Mirror final-state equality are marked `skip` in v1.6.x with a reason pointing at `gaps.md`. The v1.6.x portability claim rests on the parts that *can* be asserted today: the same six Mirrors load on both substrates, the Structural Classifier is byte-identical across them, both complete their mock lifecycles end-to-end without raising, and both record the same observable graduation in their driver event logs. Full parity — meaning byte-for-byte event sequences and byte-for-byte Mirror final states — is a v1.7+ deliverable.

This is the honest version of the portability claim. If you see it and think "wait, Claude Code has 42 events and Managed Agents has 22, that's not the same colony running" — you are correct to notice, and the example does not hide it.

### What to do next

- Open the [design spec](docs/design-spec.md) to see how this example was scoped
- Open the [implementation plan](docs/implementation-plan.md) to see how five parallel sub-agents built it
- Read the [Claude Code adapter README](substrates/claude_code/README.md) to see the contract-operation mapping
- Read the [Managed Agents adapter README](substrates/managed_agents/README.md) and the [adequacy report](substrates/managed_agents/gaps.md) to see the honest substrate research
- Run `pytest examples/teaching_colony/ -v` from the repository root to see the full test suite (26 passed, 2 skipped, 4 xfailed is expected at v1.6.0)

## Substrates

- [Claude Code](substrates/claude_code/README.md) — local Python, Anthropic SDK, filesystem state
- [Managed Agents API](substrates/managed_agents/README.md) — Anthropic Managed Agents (live mode is v1.7+; mock mode is v1.6.0)

## Known limitations

- v1.6.0 defers capability *removal* — the graduation flow only demonstrates
  capability addition. Equilibrium can propose removal but the lifecycle
  driver does not execute it.
- The Managed Agents adapter may be partial in v1.6.0 depending on API
  availability at release time.
- The Structural Classifier is a pure function over a static table. A
  production colony would version this table and treat changes as
  Colony-wide events themselves.

## Design artefacts

The working documents that produced this example are in [`docs/`](docs/):

- [**Design spec**](docs/design-spec.md) — the scope, motivation, substrate contract, agent composition, lifecycle, and deferrals. Read this first if you want to understand *why* the example looks the way it does.
- [**Implementation plan**](docs/implementation-plan.md) — the five-sub-agent parallel execution strategy that actually built v1.6.0. Includes write-scope boundaries, coordination rules, research risks, and rollback plan. Read this if you want to see how the example was built and what coordination issues were resolved during the merge.

These are the Architect-lens artefacts for the example. The top-level [`specification.md`](../../specification.md) and [`thesis.md`](../../thesis.md) are the Architect-lens artefacts for the pattern as a whole.

## Portability test

The portability claim for v1.6.0 — *the same colony runs on two substrates
and produces equivalent structural observations* — is exercised by
[`tests/test_portability.py`](tests/test_portability.py).

```bash
python -m pytest examples/teaching_colony/tests/test_portability.py -v
```

The test seeds two independent copies of `colony/` into a temporary
directory, instantiates `ClaudeCodeAdapter` and `ManagedAgentsAdapter`
against them in mock mode, and runs an eight-step minimal lifecycle on
each: baseline mirror read, KB populate (five primer documents), Librarian
proposes a capability graduation, structural classifier fires, Sentinel
co-signs, Teacher's Mirror is updated, a `graduation.approved` event is
recorded, and the final mirror is read back. It then asserts:

- **Unconditional.** Claude Code completes the full lifecycle end to end
  and emits both `graduation.approved` and `mirror.updated` events.
- **Unconditional.** Managed Agents completes every mock-implemented
  operation in the lifecycle without raising, and records the
  `graduation.approved` event.
- **Unconditional.** Both adapters return byte-identical classifier output
  for the same input — the running demonstration of Principle 2
  (*Identity over implementation*).
- **Skipped in v1.6.0**, with a citation to
  [`substrates/managed_agents/gaps.md`](substrates/managed_agents/gaps.md):
  full event-type sequence parity and Teacher-Mirror final-state parity.
  The Managed Agents scaffolding does not yet persist mock
  `update_mirror` or emit the `mirror.updated` event, so those parity
  assertions are skipped rather than faked. Live-mode parity is a v1.7+
  deliverable.

This is an honest version of the portability claim. The facts the test
can assert today are asserted; the facts that require the Managed Agents
live path wait for v1.7+.
