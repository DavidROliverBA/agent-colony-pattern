# Teaching Colony — Substrate-Portable Example

> **This is the design spec for the Teaching Colony example.** It was written as a working document in the author's private vault and copied into the public repository at v1.6.1 so that readers who want the full Architect-lens view of why this example exists, and how it was scoped, have access to it. The Architect lens of Principle 7 (*Accessibility through abstraction*) is served by this document.
>
> Companion: [implementation-plan.md](implementation-plan.md) — the plan that executed this spec.

**Date:** 2026-04-14
**Status:** Implemented in v1.6.0; exposed in public repo at v1.6.1
**Release:** v1.6.0 of `agent-colony-pattern`
**Repository location:** `examples/teaching_colony/`

---

## Summary

A six-agent Agent Colony whose purpose is to **teach the Agent Colony pattern**, using **beekeeping as its running pedagogical example**. The same colony runs on two substrates — Anthropic's Claude Code (local sub-agent orchestration) and the Anthropic Managed Agents API (hosted agent execution) — to demonstrate Principle 2 (Identity over implementation) and Principle 4 (Longevity by design) in running code for the first time in this repository.

The demonstration is the portability. The colony definition — Mirrors, event memory, knowledge base, graduation checklists — is substrate-independent and written once. The substrates are choices for L4 (Substrate) in the four-layer architecture; they provide agent execution, state, and tool access, but nothing else. The colony runs one complete lifecycle that exercises the Comprehension Contract (§7) for the first time in running code: Librarian detects KB coverage crossing a threshold, proposes that Teacher acquire a new capability, the Structural Classifier fires, Review Regime is selected, a graduation checklist is produced, Sentinel co-signs, and Teacher's Mirror is updated with an append-only audit entry.

## Motivation

At v1.5.0 the pattern has seven principles, a full specification, a manifesto, a thesis, a knowledge base, a schema, a worked hello-colony example with YAML Mirrors, a deterministic Python runtime simulation, and an HTML equilibrium playground. What it does *not* have is any artefact that demonstrates the pattern actually running on real agent infrastructure. The hello-colony-runtime is a deterministic simulation — no LLM calls, no substrate. The pattern has been careful to say "design, not validated" on every diagram and in every release note.

Two gaps follow from this:

1. **Substrate-portability is a paper claim.** Principles 2 and 4 both rest on the assumption that what an agent *is* can be separated from how it *runs*. The pattern has argued this is true but has never shown it. A colony that runs identically on two substrates is the minimum evidence.
2. **The Comprehension Contract (§7) has never done real work.** The Contract was formalised in v1.4.0 with 14 sub-sections, a review regime formula, Mirror field extensions, and a Graduation Checklist. No agent has ever actually proposed a capability change and run that proposal through the Contract. The first time it does so will reveal things the design cannot predict.

The Teaching Colony addresses both gaps in a single artefact. It is not a production system and is not proposed as one. It is a demonstration that the pattern's claims about substrate-independence and earned capability growth are falsifiable — and that the answer to the falsification test is "yes, this works".

The colony's purpose was chosen deliberately. A colony that *teaches* is a colony that serves Principle 7 (Accessibility through abstraction) as its core function: it exists to help audiences understand something, pitched to their depth. That the thing it teaches is the Agent Colony pattern itself closes the recursive loop — the pattern's accessibility claim is realised by a colony implementing the pattern.

The beekeeping metaphor was chosen for three reasons: it has been the running metaphor of the v1.5.0 principle corollary ("the beekeepers of the colony"); it is concrete and universal in a way that helps a Newcomer reader; and it provides a small, static corpus that the Teacher can use as a pedagogical example when explaining the more abstract pattern concepts ("the Registry agent is like the beekeeper's hive log; the Sentinel agent is like the queen's alarm pheromone").

## Design

### Agent composition

Six agents, parallel to hello-colony's structure:

| Agent | Layer | Trust tier (initial) | Role |
|-------|-------|----------------------|------|
| **Registry** | L1 Governance | Bounded | Catalogue of all agents in the colony; depended on by almost everyone |
| **Chronicler** | L1 Governance | Bounded | Appends events to Event Memory; terminal node in the dependency graph |
| **Equilibrium** | L1 Governance | Bounded | Detects role overlap; proposes rebalancing; watches for capability drift |
| **Sentinel** | L2 Immune System | Bounded | Co-signs capability graduation and security upgrades |
| **Librarian** | L3 Domain | Observing | Curates the KB, extracts concepts from corpus, detects coverage thresholds, proposes capability growth |
| **Teacher** | L3 Domain | Observing | Answers questions using the KB; pitches responses to the audience; is the agent whose Mirror is updated when a new capability is graduated |

Five out of six are drawn from hello-colony's roster (Registry, Chronicler, Equilibrium, Sentinel are structurally identical; Librarian replaces domain-agent-finance's pre-v1.1 self-monitoring role in a tidier way; Teacher is new). A reader who has already read hello-colony will recognise the first four immediately and can diff the Mirrors to see what's new.

### Substrate contract

The substrate contract defines what L4 owes L1–L3. It is an abstract interface that both Claude Code and Managed Agents substrates must implement. Eight operations:

```python
class SubstrateContract(ABC):
    @abstractmethod
    def dispatch_agent(self, agent_id: str, input: dict) -> dict:
        """Run a named agent with structured input, return structured output."""

    @abstractmethod
    def read_mirror(self, agent_id: str) -> Mirror:
        """Load an agent's Mirror from canonical YAML on disk."""

    @abstractmethod
    def update_mirror(self, agent_id: str, changes: dict, co_signer: str) -> AuditEntry:
        """Mutate a Mirror with an append-only audit trail.
        Enforces §7 Comprehension Contract: classifier must fire,
        co-sign must be verified, append-only log must record pre-state hash."""

    @abstractmethod
    def record_event(self, event: Event) -> None:
        """Append to events.jsonl with timestamp and substrate identifier."""

    @abstractmethod
    def read_kb(self, query: str) -> list[Document]:
        """Retrieve relevant documents from state/kb/ for a query."""

    @abstractmethod
    def write_kb(self, topic: str, content: str, provenance: str) -> None:
        """Add content to state/kb/<topic>.md with provenance header."""

    @abstractmethod
    def co_sign(self, action_class: str, actor: str, co_signer: str) -> Signature:
        """Immune System co-sign for preauthorised or graduation actions.
        Verifies actor ≠ co_signer and action_class is in pre-registered enum."""

    @abstractmethod
    def classify_action(self, action: dict, context: dict) -> Classification:
        """Structural Classifier invocation.
        Returns blast_radius (Local|Inter-agent|Colony-wide|Boundary-crossing)
        and review_regime per §7.4 formula."""
```

The colony itself is written once against this interface. Both substrate adapters subclass `SubstrateContract` and implement the eight operations in their native idiom.

### State layout (substrate-independent)

```
examples/teaching-colony/
├── README.md                     # Top-level lens map + quick start
├── substrate-contract.md         # Prose description of the eight operations
├── contract.py                   # The ABC
├── colony/
│   ├── mirrors/
│   │   ├── registry-agent.yaml
│   │   ├── chronicler-agent.yaml
│   │   ├── equilibrium-agent.yaml
│   │   ├── sentinel-agent.yaml
│   │   ├── librarian-agent.yaml
│   │   └── teacher-agent.yaml
│   ├── corpus/
│   │   ├── pattern/              # Symlinks or copies of spec/thesis/manifesto/etc.
│   │   └── beekeeping/
│   │       └── primer.md         # Hand-written 2–3 page primer
│   └── logic/
│       ├── classifier.py         # Structural Classifier (pure function, no LLM)
│       ├── review_regime.py      # §7.4 formula
│       └── graduation.py         # Graduation checklist generation
├── substrates/
│   ├── claude-code/
│   │   ├── adapter.py
│   │   ├── README.md             # How to run on Claude Code
│   │   └── tests/
│   │       └── test_cycle.py
│   └── managed-agents/
│       ├── adapter.py
│       ├── api-research.md       # Sub-agent C's research output
│       ├── gaps.md               # Honest documentation of unsupported ops
│       ├── README.md
│       └── tests/
│           └── test_cycle.py
├── state/                        # Written at runtime; .gitignored except for initial state
│   ├── kb/
│   │   └── beekeeping.md         # Initial seeded KB entry
│   ├── events.jsonl
│   └── graduation-checklists/
├── tests/
│   └── test_portability.py       # Diff event logs + Mirror final states between substrates
└── run.py                        # CLI entry: python run.py --substrate=claude-code
```

### The observable lifecycle

One complete run of the colony, observable identically on both substrates:

1. **Boot.** The CLI instantiates the chosen substrate adapter. Registry reads all six Mirrors from `colony/mirrors/`. Chronicler opens (or creates) `state/events.jsonl` and records a `colony.boot` event. Equilibrium reads the overlap matrix (static for v1, stored in `colony/overlap.yaml`). Sentinel verifies its own Mirror is valid.
2. **Initial serve.** A scripted Newcomer input is fed to Teacher: *"teach me about beekeeping"*. Teacher reads `state/kb/beekeeping.md`, produces an answer, Chronicler records `teacher.serve` with input/output hashes.
3. **Learn (N cycles).** Librarian reads one new file from `corpus/pattern/` per cycle (in deterministic order: spec first, then thesis, then manifesto, then knowledge-base files). For each file, Librarian extracts a structured summary and writes it to `state/kb/<topic>.md` with provenance. Each write emits `librarian.curate` events.
4. **Detect.** After processing enough corpus files, Librarian recomputes KB coverage. When `agent-colony-pattern` coverage reaches the threshold (≥ 5 KB documents + ≥ 3 cross-references, configurable), Librarian emits `librarian.propose_capability` with payload: *Teacher should acquire `teach-agent-colony-pattern`*.
5. **Classify.** The substrate's `classify_action` runs the Structural Classifier over the proposal. Action class = `mirror_capability_add`. Blast radius = `Colony-wide` (any Mirror change is Colony-wide per §7.4 defaults). Trust tier of the proposing agent = `Observing` (Librarian starts Observing). Review regime per §7.4 formula = `Peer Review`. Event `classifier.fired`.
6. **Graduate.** `colony/logic/graduation.py` generates a graduation checklist with three evidence requirements (document count, cross-reference count, classifier pass) and two approval requirements (Sentinel co-sign, human ack — simulated by a second agent dispatch in v1). Checklist written to `state/graduation-checklists/<timestamp>-teacher-teach-pattern.yaml`. Sentinel's `co_sign` fires and returns a signature. Event `graduation.approved`.
7. **Acquire.** `update_mirror(agent_id='teacher', changes={capabilities: +teach-agent-colony-pattern}, co_signer='sentinel')` runs. Pre-state hash written to append-only audit entry in Teacher's Mirror. Rollback window opens. Event `mirror.updated`.
8. **Serve (new capability).** Second scripted Newcomer input: *"teach me about the Agent Colony pattern, using bees as the example"*. Teacher now has the new capability; reads the KB entries for `agent-colony-pattern`; produces an answer that explicitly uses the beekeeping primer's concepts as running examples. Event `teacher.serve` with the new capability recorded.
9. **Snapshot.** Final colony snapshot written to `state/colony-snapshot.yaml`. Colony shuts down cleanly.

That's one run. It is deterministic — same corpus, same order, same substrate, same output hashes — except for substrate-specific metadata (timestamps, execution IDs). Running the same cycle on the other substrate produces a parallel event log that differs only in substrate-specific fields.

### Capability growth detection — v1 mechanism

Librarian maintains a coverage map: `{topic: {documents: [...], cross_references: N}}`. When Librarian writes to the KB, it updates this map. After each write, it checks:

```python
def is_teachable(coverage_map, topic):
    entry = coverage_map.get(topic, {})
    doc_count = len(entry.get('documents', []))
    xref_count = entry.get('cross_references', 0)
    return doc_count >= MIN_DOCUMENTS and xref_count >= MIN_CROSS_REFERENCES
```

`MIN_DOCUMENTS = 5`, `MIN_CROSS_REFERENCES = 3` for v1. These values are deliberately low enough that a short corpus can exercise the loop. When `is_teachable('agent-colony-pattern')` flips from `False` to `True`, Librarian emits the capability proposal.

v1 does not include the Critic self-test from §7.12 multi-perspective valuation. That is explicitly deferred. v1 coverage detection is "dumb" and we document it as such. The Comprehension Contract fires on the proposal regardless — the classifier doesn't care how the proposal was generated, only that it was proposed.

### Classifier (v1 — pure function, no LLM)

```python
def classify_action(action: dict, context: dict) -> Classification:
    action_class = action.get('class')

    # Blast radius rules
    if action_class in ('mirror_capability_add', 'mirror_capability_remove'):
        blast_radius = 'Colony-wide'
    elif action_class == 'kb_write':
        blast_radius = 'Inter-agent'
    elif action_class == 'teacher_serve':
        blast_radius = 'Local'
    elif action_class == 'security_patch':
        blast_radius = 'Colony-wide'
    else:
        blast_radius = 'Colony-wide'  # Over-report by design (§7.1)

    # Review regime per §7.4 formula
    trust_tier = context.get('actor_trust_tier', 'Observing')

    if action_class == 'security_patch':  # Constitutional → Governance
        review_regime = 'Governance Council'
    elif action_class in ('mirror_capability_add',):  # Novel → Peer Review
        review_regime = 'Peer Review'
    elif blast_radius == 'Local' and trust_tier in ('Bounded', 'Self-Directed'):
        review_regime = 'Event-line'
    else:
        review_regime = REVIEW_TABLE[trust_tier][blast_radius]

    return Classification(blast_radius=blast_radius, review_regime=review_regime)
```

The classifier is a pure function in `colony/logic/classifier.py`. Both substrates call it from their `classify_action` operation. It does not vary by substrate. This is correct — the classifier is a colony-level concern, not a substrate concern.

### Substrate A — Claude Code adapter

Operations map to Claude Code primitives as follows:

| Contract op | Claude Code mechanism |
|-------------|-----------------------|
| `dispatch_agent` | Dispatch a Task sub-agent with the agent's Mirror loaded as system prompt context. Return the sub-agent's final structured output. |
| `read_mirror` | `yaml.safe_load(open('colony/mirrors/' + agent_id + '.yaml'))` |
| `update_mirror` | Read current Mirror → compute pre-state hash → apply changes → append audit entry → write back → emit `mirror.updated` event |
| `record_event` | Append JSONL line to `state/events.jsonl` |
| `read_kb` | Simple glob + keyword match across `state/kb/*.md` (v1); no vector store |
| `write_kb` | Write `state/kb/<slug>.md` with provenance header frontmatter |
| `co_sign` | Dispatch a second Task sub-agent (Sentinel) to verify the action against its pre-registered policies; return a signature dict |
| `classify_action` | Direct call to `colony/logic/classifier.py` |

Running on Claude Code is a matter of `python run.py --substrate=claude-code`. The CLI uses the `anthropic` SDK with `claude-sonnet-4-6` (or `claude-haiku-4-5` for the sub-agent dispatches to keep costs down) and drives the colony through the scripted lifecycle.

**Dependencies:** `anthropic`, `pyyaml`, `jsonschema`.

### Substrate B — Managed Agents API adapter

**This adapter cannot be built without prior research on the current Managed Agents API surface.** Sub-agent C's first task is to document the API as of 2026-04, specifically answering:

1. Can multiple named agents be defined in one session or across sessions?
2. Is inter-agent dispatch natively supported or must it be simulated via an orchestrator agent?
3. How is persistent state handled — per-session, per-agent, shared?
4. How are tools defined? Can a tool wrap arbitrary Python code that reads/writes local files?
5. What are the auth, rate limit, and cost implications for running the demo?
6. Is streaming necessary, or can the demo run with batch responses?

Based on research findings, the adapter implements the eight operations using Managed Agents primitives. Where native support is absent, the adapter documents the gap in `substrates/managed-agents/gaps.md` and simulates the operation honestly — for example, if inter-agent dispatch is not native, a single orchestrator agent with a dispatch tool simulates it. The gap documentation is itself a contribution: it is the first adequacy report of a real substrate against the Agent Colony contract.

**Dependencies:** whatever the current `anthropic` or `anthropic-agents` SDK version exposes; to be determined by sub-agent C.

### Portability test

`tests/test_portability.py` runs the cycle on both substrates from a fresh initial state and compares:

1. **Event log equivalence.** Event types and ordering must match. Substrate-specific fields (timestamps, execution IDs) are excluded from the diff. Payload hashes for deterministic fields (KB document hashes, Mirror pre/post state hashes) must match exactly.
2. **Mirror final state equivalence.** After both runs, all six Mirrors on disk must be byte-identical modulo the `last_modified` timestamp field.
3. **KB final state equivalence.** Files in `state/kb/` must have the same filenames and the same content hashes.
4. **Graduation checklist equivalence.** The single graduation checklist produced by each run must have the same evidence entries and approval signatures (modulo signer-specific metadata).

If any of these diverge, the portability claim is falsified and the gap is documented. The test's job is not to prove the claim universally but to prove it for this specific colony and this specific lifecycle.

## Files created

| Path | Purpose |
|------|---------|
| `examples/teaching-colony/README.md` | Top-level example README with lens map, Beekeeper lens header, Newcomer entry path |
| `examples/teaching-colony/substrate-contract.md` | Prose description of the eight operations |
| `examples/teaching-colony/contract.py` | The SubstrateContract ABC |
| `examples/teaching-colony/colony/mirrors/*.yaml` | Six Agent Mirrors (v0.2.0 schema) |
| `examples/teaching-colony/colony/corpus/pattern/` | Copies (not symlinks — portable across OS) of spec/thesis/manifesto/knowledge-base notes |
| `examples/teaching-colony/colony/corpus/beekeeping/primer.md` | 2–3 page beekeeping primer, hand-written |
| `examples/teaching-colony/colony/overlap.yaml` | Static overlap matrix |
| `examples/teaching-colony/colony/logic/classifier.py` | Pure-function Structural Classifier |
| `examples/teaching-colony/colony/logic/review_regime.py` | §7.4 formula implementation |
| `examples/teaching-colony/colony/logic/graduation.py` | Graduation checklist generator |
| `examples/teaching-colony/state/kb/beekeeping.md` | Initial seeded KB entry |
| `examples/teaching-colony/state/.gitignore` | Ignore runtime state except initial seeds |
| `examples/teaching-colony/substrates/claude-code/adapter.py` | Claude Code adapter |
| `examples/teaching-colony/substrates/claude-code/README.md` | How to run on Claude Code |
| `examples/teaching-colony/substrates/claude-code/tests/test_cycle.py` | Claude Code cycle test |
| `examples/teaching-colony/substrates/managed-agents/api-research.md` | Sub-agent C's API research output |
| `examples/teaching-colony/substrates/managed-agents/gaps.md` | Honest adequacy report |
| `examples/teaching-colony/substrates/managed-agents/adapter.py` | Managed Agents adapter |
| `examples/teaching-colony/substrates/managed-agents/README.md` | How to run on Managed Agents |
| `examples/teaching-colony/substrates/managed-agents/tests/test_cycle.py` | Managed Agents cycle test |
| `examples/teaching-colony/tests/test_portability.py` | Cross-substrate portability test |
| `examples/teaching-colony/run.py` | CLI entry point |
| `examples/teaching-colony/requirements.txt` | Python dependencies |

## Scope — v1 versus deferred

### v1 includes

- Substrate contract ABC and prose description
- Six Agent Mirrors parallel to hello-colony
- Beekeeping primer (hand-written)
- Corpus copies from this repo
- Structural Classifier as a pure function
- Review Regime formula implementation
- Graduation checklist generator
- Claude Code substrate adapter (fully working)
- Managed Agents API research + substrate adapter (honest, with gaps documented)
- Per-substrate cycle tests
- Cross-substrate portability test
- CLI entry point
- Lens-mapped READMEs
- Integration into `examples/README.md` lens map
- v1.6.0 release with the known gaps stated

### v1 explicitly defers (to v1.7 or v2)

- Critic self-test for capability growth (v1 uses coverage threshold only)
- Real research against web or external corpora
- Multi-capability growth in a single run
- Per-audience teaching style variation (Newcomer vs Beekeeper pitch)
- Beekeeping as an independently-growing domain
- Operator dashboard UI for the colony
- Public deployment of a running Managed Agents colony
- Federated colony-to-colony operation
- LLM-based classifier (v1 is pure rules)

### v1 known risks

1. **Managed Agents API surface is uncertain.** Sub-agent C's research may reveal that key operations are not natively supported. The mitigation is honest gap documentation — we do not hide an unsupported operation behind a fake implementation. If the gaps are severe enough that the portability test cannot pass, we ship v1.6.0 with Claude Code working and Managed Agents documented-only, and target v1.7.0 for the completion.
2. **Token cost of the cycle.** Running the colony on Claude Code with real LLM sub-agents will consume tokens. The cycle is designed to be short (9 steps, small inputs, small outputs) but the cost should be measured and documented in the README.
3. **Determinism.** LLM calls are not fully deterministic even at temperature 0. The portability test must exclude fields that LLMs vary on (exact wording of Teacher's answers) and must compare only structural fields (Mirror state, event types, KB file lists).

## Conformance claim

This example is a **Beekeeper-lens artefact** by default, with a documented path for Newcomers and Operators. The top-level README directs:

- **Newcomers** to the village article and the lens-map in `examples/README.md`
- **Observers** to "you don't need to run this; it runs and does things"
- **Operators** to a scripted run with output they can read
- **Beekeepers** to the Mirror files, the substrate contract, and the adapters
- **Architects** to the specification and this spec document

The example's conformance to Principle 7 is exactly this explicit mapping: no lens is forced to read the adapter code to benefit from the example.

## Testing / verification

1. `python run.py --substrate=claude-code` completes without error and produces the expected final state
2. `python run.py --substrate=managed-agents` completes without error (or documents a specific blocker)
3. `python tests/test_portability.py` passes, demonstrating event-log and Mirror equivalence
4. `examples/teaching-colony/README.md` has a lens map line for each audience
5. Commit message, CHANGELOG entry, and GitHub release text all ship
6. `schemas/agent-mirror-v0.2.0.json` validates all six Mirrors

## Out of scope

- Any claim that this example is a production system
- Comparison against third-party multi-agent frameworks (LangGraph, AutoGen, CrewAI)
- Claims about real-world learning quality of the Teacher
- Security hardening of the example beyond the pattern's baseline mechanisms
- Cost optimisation of the Claude Code adapter beyond model selection
