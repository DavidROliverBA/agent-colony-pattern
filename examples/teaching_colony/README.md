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

## How to run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run against the Claude Code substrate (offline mock mode):

```bash
python run.py --substrate=claude-code --mock
```

Run against the Managed Agents substrate:

```bash
python run.py --substrate=managed-agents
```

Reset runtime state (wipes events, snapshots, graduation checklists):

```bash
python run.py --substrate=claude-code --reset --mock
```

## Substrates

- [Claude Code](substrates/claude-code/README.md)
- [Managed Agents API](substrates/managed-agents/README.md)

## Known limitations

- v1.6.0 defers capability *removal* — the graduation flow only demonstrates
  capability addition. Equilibrium can propose removal but the lifecycle
  driver does not execute it.
- The Managed Agents adapter may be partial in v1.6.0 depending on API
  availability at release time.
- The Structural Classifier is a pure function over a static table. A
  production colony would version this table and treat changes as
  Colony-wide events themselves.

## Spec and plan

- [Design spec](../../../BA-DavidOliver-ObsidianVault/docs/superpowers/specs/2026-04-14-teaching-colony-design.md)
- [Implementation plan](../../../BA-DavidOliver-ObsidianVault/docs/superpowers/plans/2026-04-14-teaching-colony-implementation.md)

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
