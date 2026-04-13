# Agent Colony — Design Specification v1.0

**Author:** David Oliver
**Date:** 2026-04-11
**Status:** v1.0 — Foundation
**Licence:** Personal intellectual property of the author. Published for peer review.

---

## 1. Definition and Core Principles

### What Is an Agent Colony?

The **Agent Colony** is an architectural pattern for building self-governing ecosystems of autonomous AI agents that persist beyond the projects and teams that create them, evolve across technology generations, and coexist with human organisations through defined boundaries.

It is not a framework, a platform, or a product. It is a pattern — like microservices or event-driven architecture — that can be implemented in any technology, on any infrastructure, by any organisation.

### The Evolutionary Context

Each paradigm shift in distributed systems changed what could be independently deployed, reused, and governed:

| Era | Unit | Composition | Governance |
|-----|------|-------------|------------|
| Monoliths | Application | Internal calls | Single team |
| SOA | Service | WSDL/ESB | Service registry |
| Microservices | Microservice | HTTP/gRPC/events | API gateway, service mesh |
| **Agent Colonies** | **Agent** | **Open protocol** | **Self-governing with human boundaries** |

What each shift added:

- SOA added **reuse** across applications
- Microservices added **independent deployment** and team ownership
- Agent Colonies add **autonomy, self-evolution, and lifecycle identity**

### Six Principles

**1. Coexistence, not control**
Agents live in their world; humans live in theirs. The boundary defines where one ends and the other begins. Effects that cross the boundary require a checkpoint. Everything within the agent world is self-governed.

**2. Identity over implementation**
An agent is defined by what it is (purpose, contracts, capabilities, lifecycle stage), not how it's built (language, framework, model). A complete agent definition standard — the Agent Mirror — must be rich enough that an agent can read its own identity, understand it, and migrate itself to a new implementation.

**3. Equilibrium over optimisation**
The colony self-regulates the balance between specialisation and consolidation. Too much overlap triggers merger review. Too much consolidation triggers specialisation review. The equilibrium is dynamic, not fixed — but bounded to prevent gravitational collapse into a monolith.

**4. Longevity by design**
The colony is designed to outlive any technology generation, any team, any individual. This requires defences against technology drift (protocol-level interop), organisational entropy (self-governance), and knowledge loss (agents carry their own context and history through Colony Memory).

**5. Earned autonomy**
The colony starts human-governed and earns self-governance through demonstrated trustworthiness. Funding follows the same trajectory: seeded, proven, then self-sustaining through measurable outcomes. Experimentation follows the same trajectory: observe only, sandboxed, bounded live, self-directed.

**6. Mutual defence**
The boundary between agent and human worlds is a shared border, and attacks affect both sides. Agents are responsible for their own security posture — continuously upgrading defences, detecting threats, and responding to attacks within their world. When an attack crosses or threatens the boundary, agents and humans collaborate on response through agreed processes. This is built on mutual trust: humans trust agents to defend themselves and report honestly; agents trust humans to act on shared threat intelligence. Security is not a constraint imposed on the colony — it is a survival instinct built into every agent from birth.

**Security upgrade preauthorisation:** Improving security posture is always a sufficient reason to self-upgrade, regardless of lifecycle stage, update budget, or governance cycle. Security upgrades do not consume self-evolution allowances. An agent that cannot improve its own security is a liability to the colony.

---

## 2. The Agent Mirror Standard

### The Gap

Existing standards each describe a slice of what an agent is:

| Standard | What it defines | What it misses |
|----------|----------------|----------------|
| A2A Agent Cards | Capabilities, endpoint, auth | Lifecycle, self-evolution, history, security posture |
| MCP | Tool interfaces, resources | Agent identity, autonomy, governance |
| OpenAPI | HTTP API contracts | Everything non-API — purpose, lifecycle, autonomy |
| OCI (containers) | Runtime packaging, distribution | Intent, behaviour, evolution, relationships |
| AGENTS.md | Project conventions for AI coding agents | Not machine-readable, no lifecycle, no registry |

None define a complete, self-describing, machine-readable identity that an agent can read about itself, reason about, and use to migrate to a new implementation. The gap is the difference between a passport (proves who you are at a border) and a genome (defines what you are and how you evolve).

### The Agent Mirror

The **Agent Mirror** is the standard that reflects what an agent is. The name captures its purpose: an agent looks at its Mirror and knows what it is, what it can do, how it's changed, and what it's responsible for.

The Mirror is *descriptive*, not *prescriptive*. It reflects what the agent is — it doesn't command what it should be. When the Mirror and the agent's actual behaviour diverge, that's a signal (potential drift or compromise), not a constraint.

### Agent Mirror Schema

**Core Identity**

- `name` — unique within the colony
- `purpose` — what this agent exists to do, in terms an agent or human can evaluate against
- `version` — semantic, with clear major/minor/patch semantics for agents (what constitutes a breaking change in *behaviour*, not just API)
- `lineage` — version history: what changed, why, and who/what triggered each change
- `owner` — the team or entity accountable (may be human or another agent)

**Capabilities and Contracts**

- `capabilities` — what this agent can do, expressed as verifiable claims
- `contracts` — input/output schemas, SLAs, error behaviours. What consumers can rely on.
- `dependencies` — other agents or services this agent requires
- `protocols` — which communication protocols it speaks (A2A, MCP, HTTP, gRPC, events)

**Autonomy and Self-Evolution**

- `autonomy_level` — what this agent can decide on its own vs what requires escalation
- `self_evolution_scope` — what it can change about itself (behaviour tuning, context, tool preferences) vs what it cannot (purpose, contracts, security boundaries)
- `evolution_budget` — how many self-updates before a human redesign gate (explicit exception: security upgrades are preauthorised and do not consume this budget)
- `evolution_log` — machine-readable history of every self-modification

**Security Posture**

- `threat_model` — what this agent defends against
- `detection_capabilities` — what it can detect
- `escalation_process` — when and how it alerts humans or immune system agents
- `last_security_upgrade` — timestamp and description
- `security_dependencies` — shared defences it relies on from the colony

**Lifecycle**

- `lifecycle_stage` — born, deployed, active, dormant, deprecated, retired
- `birth_date` — when created
- `last_active` — last meaningful action
- `health_status` — self-reported and externally observed
- `retirement_criteria` — conditions under which this agent should be retired

**Colony Relationships**

- `overlap_map` — declared overlap with other agents and the current assessment (healthy / review-needed / merger-candidate)
- `collaborators` — agents it frequently works with
- `consumers` — who depends on this agent

### Design Properties

The standard must be:

- **Self-describing** — an agent can read its own identity file and reason about it
- **Machine-readable and human-readable** — likely YAML or JSON with rich descriptions
- **Versionable** — the standard itself evolves, and agents can migrate between versions
- **Portable** — not coupled to any runtime, cloud, or AI model provider
- **Extensible** — organisations can add fields without breaking the core schema

---

## 3. Colony Architecture

The colony is structured in four layers. Each layer is independently replaceable — the colony survives any single layer being swapped out. No layer knows the implementation details of the layer below it.

### Layer 1: Colony Governance

The meta-agents that keep the colony coherent.

- **Registry Agent** — maintains the Agent Mirror catalogue. Every agent in the colony is registered here. Provides discovery (find agents by capability), dependency graphing (what breaks if this agent dies), and overlap analysis (feeds into the Equilibrium Agent).
- **Equilibrium Agent** — monitors overlap between agents. When overlap exceeds a threshold, proposes a merger review. When an agent grows too broad, proposes specialisation. Enforces anti-monopoly — prevents runaway consolidation by maintaining minimum agent diversity targets.
- **Lifecycle Agent** — manages the born-to-retired lifecycle. Tracks evolution budgets (excluding security upgrades). Enforces redesign gates. Manages succession when agents are retired — ensuring consumers are migrated before an agent is decommissioned.
- **Chronicler Agent** — records colony events into Event Memory, ensures nothing significant goes unrecorded.
- **Reflector Agent** — analyses event patterns, extracts lessons, tags them with relevance conditions for Lesson Memory.
- **Constitutional Agent** — monitors lesson frequency, proposes rule promotions to Constitutional Memory, manages rule retirement with full reasoning.

### Layer 2: Colony Immune System

The shared defence. Separated from governance because security operates on different timescales (immediate vs deliberative) and with different authority (preauthorised action vs governance review).

- **Sentinel Agent** — continuous threat detection, anomaly monitoring, colony-wide vulnerability scanning. Watches for drift between Agent Mirrors and actual behaviour (a compromised agent's Mirror will lie).
- **Response Coordinator** — orchestrates incident response. Decides what stays within the agent world vs what crosses the boundary to humans. Executes pre-agreed playbooks. This is the mutual trust mechanism in action.
- **Patch Agent** — proactive remediation. Dependency updates, vulnerability patches, security-driven self-migrations. Acts on preauthorised upgrade authority — doesn't wait for governance.

### Layer 3: Agent Mesh

Where the actual work happens. Domain agents, specialists, and generalists — all carrying their Agent Mirror, all discoverable via the Registry, all defended by the Immune System. This layer is unbounded — it grows and contracts as the colony evolves. The Equilibrium Agent shapes it; the Lifecycle Agent manages its membership.

Agent types within the mesh:

- **Domain agents** — own a broad area of responsibility (e.g., finance, compliance, engineering)
- **Specialist agents** — do one thing extremely well (e.g., invoice validation, CVE scanning)
- **Generalist agents** — handle a range of tasks that don't warrant a specialist

### Layer 4: Substrate

The colony's only infrastructure dependency, deliberately kept as thin as possible. Compute, storage, networking, AI model access — all provider-agnostic. The substrate is *consumed*, not *owned* — the colony runs on whatever infrastructure is available. This is what makes multi-decade survival possible: when today's cloud providers are replaced by whatever comes next, only this layer changes.

### Key Architectural Property

No layer knows the implementation details of the layer below it. Governance agents don't know which cloud the mesh runs on. Immune system agents don't know which AI model powers a domain agent. This is what makes each layer independently replaceable.

---

## 4. The Equilibrium System

### The Problem

Left ungoverned, agent ecosystems face two gravitational pulls:

- **Consolidation pressure** — it's always easier to add a capability to an existing agent than to create a new one. Over time, successful agents absorb more scope. Unchecked, this produces one super-agent that does everything and is impossible to maintain, understand, or replace.
- **Fragmentation pressure** — it's always easier to build a new agent than to find and reuse an existing one. Over time, the colony fills with overlapping, near-identical agents. Unchecked, this produces the microservices graveyard: hundreds of agents, nobody knows what half of them do.

Agents add a third dimension: **self-evolution pressure**. Agents that can modify themselves will naturally drift toward whatever makes them more useful to their consumers, regardless of colony-wide coherence.

### The Equilibrium Mechanism

The Equilibrium Agent (L1) manages three metrics:

**1. Overlap Index**

Every agent's Mirror declares its capabilities. The Equilibrium Agent continuously compares capability declarations across the colony and computes pairwise overlap scores.

- **< 15% overlap** — healthy. Different agents, minor shared edges. No action.
- **15–40% overlap** — watch zone. Flag for review. May be legitimate (different consumers, different SLAs) or may indicate creeping duplication.
- **> 40% overlap** — merger candidate. Trigger a merger review process. The two agents and their consumers are consulted. Outcome: merge, split responsibilities more cleanly, or document the justification for continued overlap.

These thresholds are initial defaults — they will be calibrated through the colony's own experimentation process as empirical data accumulates. Different colonies may converge on different values based on their domain and scale.

**2. Concentration Index**

Measures how much of the colony's total capability is concentrated in the largest agents. Inspired by the Herfindahl-Hirschman Index used in antitrust economics.

- If any single agent accounts for more than a defined threshold of total colony capabilities, it triggers a specialisation review — should this agent be decomposed?
- The threshold is configurable and evolves with colony maturity. Early colonies tolerate higher concentration (fewer agents, each does more). Mature colonies enforce lower concentration.

**3. Vitality Index**

Measures the health of the ecosystem as a whole:

- **Birth rate** — are new agents being created? A colony that stops creating new agents is stagnating.
- **Retirement rate** — are old agents being retired? A colony that never retires anything is accumulating dead weight.
- **Self-evolution rate** — are agents improving themselves? Low self-evolution suggests the colony isn't learning.
- **Diversity score** — how many distinct capability categories exist? Declining diversity signals consolidation.

### How Equilibrium Evolves

Initially, humans set the thresholds and review the Equilibrium Agent's proposals. Over time:

1. **Phase 1** — Equilibrium Agent proposes, humans decide
2. **Phase 2** — Equilibrium Agent proposes and executes minor adjustments (overlap flags, review triggers), humans decide mergers and decompositions
3. **Phase 3** — Equilibrium Agent self-governs within the boundaries humans have set. Humans review only boundary cases and adjust the boundaries themselves

The Equilibrium Agent itself has a redesign gate — its own thresholds and mechanisms get human review after a defined number of self-adjustments.

### What Doesn't Exist Yet

No agent framework, multi-agent system, or orchestration platform currently addresses equilibrium management. CrewAI, AutoGen, LangGraph — they all assume a fixed set of agents defined by developers. The concept of a self-regulating agent population with consolidation and fragmentation pressures is absent from the literature.

---

## 5. Colony Memory

### The Problem

Individual agents carry their own evolution log in their Agent Mirror. But the colony needs collective memory. Lessons that one agent learns should be available to every agent. Patterns that emerged during a crisis ten years ago should surface when a similar crisis appears today.

Without colony memory:

- A new agent repeats a mistake that a retired agent solved five years ago
- The Equilibrium Agent proposes a merger that was tried and failed before — the reasons for failure are lost
- Security patterns that defeated a specific attack class are forgotten when the Patch Agent that developed them is retired
- The colony cannot explain why its current rules exist — it follows rules without understanding their origin

### Three Layers of Memory

**1. Event Memory — What happened**

The raw record. Every significant colony event is recorded: agent births, retirements, mergers, security incidents, self-evolution actions, equilibrium adjustments, boundary crossings with the human world. Factual, timestamped, immutable.

**2. Lesson Memory — What we learned**

Extracted from event memory through reflection. When something goes wrong (or right), the colony distils the lesson: what happened, why it happened, what to do differently (or the same) next time. Lessons are tagged with the conditions under which they're relevant — so they can be recalled when similar conditions arise, even decades later.

Lessons are not just stored — they are **pattern-matched** against current conditions and surfaced proactively.

**3. Constitutional Memory — What we believe**

The colony's accumulated wisdom, distilled into rules and principles. When a lesson recurs enough times, it graduates into a constitutional rule — a standing instruction that shapes colony behaviour.

The constitution is not static. Rules that no longer serve the colony can be challenged, reviewed, and retired — but the memory of why they were created is preserved, so the colony understands what it's giving up.

### The Reflection Cycle

```
Events occur
    |
    v
Event Memory records what happened
    |
    v
Reflection process extracts lessons
    |
    v
Lesson Memory stores patterns with relevance tags
    |
    v
Recurring lessons promote to Constitutional Memory
    |
    v
Constitutional rules shape colony behaviour
    |
    v
New events occur under new rules
    |
    v
Cycle continues — the colony learns
```

### Memory Agents

Colony Memory is maintained by dedicated agents:

- **Chronicler Agent** — records events, maintains the event log, ensures nothing significant goes unrecorded
- **Reflector Agent** — analyses event patterns, extracts lessons, tags them with relevance conditions. Asks: "What just happened, and what should we learn from it?"
- **Constitutional Agent** — monitors lesson frequency, proposes rule promotions, manages the colony constitution. Also handles rule retirement — when a rule's original conditions no longer apply, it proposes sunset with full reasoning

### Memory and Self-Migration

When an agent migrates itself to a new technology, the colony's memory of why the old technology was chosen and what problems the migration solved travels with it. An agent that migrates without memory is just rewriting itself. An agent that migrates with memory is evolving.

### Memory and the Coexistence Boundary

Lessons that involve cross-boundary incidents (attacks, misunderstandings, trust failures) are flagged as **shared memory** — visible to both the colony and its human collaborators. This is how mutual trust deepens over time: both sides build a shared history of how they've handled challenges together.

### What Doesn't Exist Yet

Current multi-agent frameworks have no concept of collective memory that persists across agent generations. Individual agent memory exists (LangChain, LlamaIndex). Session memory exists. But reflective, constitutional memory for an agent ecosystem — where lessons become rules — has no standard or reference implementation.

---

## 6. Epistemic Discipline

### The Problem

Every memory system is a bias amplification system unless it has checks. The colony faces specific epistemic risks:

| Risk | How it manifests |
|------|-----------------|
| **Survivorship bias** | The colony remembers what worked, forgets what was never tried |
| **Confirmation bias** | The Reflector Agent finds patterns that confirm existing rules, ignoring contradictions |
| **Anchoring** | Early lessons carry disproportionate weight because they were first |
| **Groupthink** | Agents optimise for colony consensus rather than independent reasoning |
| **Recency bias** | Recent events overweight in lesson extraction |
| **Sunk cost** | Agents resist retirement because of accumulated investment, not current value |

### The Scientific Method as Colony Operating System

The colony operates on evidence, not belief. Every decision, every lesson, every constitutional rule must be grounded in observable, falsifiable claims.

**1. Hypothesis, not conclusion**

When the Reflector Agent extracts a lesson, it frames it as a hypothesis:

- Not: "Merging agents with >40% overlap improves colony health"
- But: "Hypothesis: merging agents with >40% overlap improves colony health. Evidence: 3 mergers observed, 2 improved health metrics, 1 neutral. Confidence: low. Conditions: small colony (<50 agents). Falsification criteria: if the next 2 mergers at >40% overlap show no improvement, downgrade."

Every lesson carries its evidence, confidence level, boundary conditions, and the conditions under which it should be considered disproven.

**2. Evidence grades**

| Grade | Meaning | Example |
|-------|---------|---------|
| **Empirical** | Directly observed, reproducible | "Security upgrades within 24h of CVE prevented 3 incidents" |
| **Corroborated** | Observed multiple times across contexts | "Narrow-scope agents self-evolve more effectively (12 agents, 4 domains)" |
| **Theoretical** | Logically sound, not yet observed in this colony | "Anti-monopoly thresholds should prevent super-agent formation" |
| **Inherited** | From human collaborators or external sources, not yet validated | "Best practice from OWASP: validate all inputs at boundary" |
| **Anecdotal** | Single observation, not yet reproduced | "One agent's migration failed during high load" |

Constitutional rules require **corroborated** or higher evidence. Rules based on theoretical or inherited evidence are flagged as provisional.

**3. Mandatory dissent**

For every significant colony decision, the process must include a structured counter-argument. Any agent participating in a decision can be assigned the dissent role — tasked with finding the strongest case against the proposed action. The decision proceeds only after the counter-argument has been heard and addressed.

**4. Rule decay and re-validation**

Every constitutional rule carries:

- **Evidence basis** — what supports it
- **Validation schedule** — when it must be re-tested
- **Decay trigger** — conditions that automatically downgrade the rule from constitutional to provisional

A rule that cannot be re-validated is retired — with full memory of why it existed and why it was removed.

**5. Bias detection**

A dedicated function actively scans for epistemic risks:

- Are recent lessons overriding older, better-evidenced ones? (Recency check)
- Are we only learning from successes? (Survivorship check)
- Is a rule being kept because of investment rather than value? (Sunk cost check)
- Are agent decisions converging without independent reasoning? (Groupthink check)
- Do founding-era rules still hold under current conditions? (Anchoring check)

When bias is detected, it triggers a re-examination. The biased conclusion might still be correct, but it must be re-derived through clean reasoning.

### Experimentation as Earned Capability

The colony's ability to conduct experiments follows the maturity trajectory:

**Stage 1: Observe Only**
The colony operates under human-defined rules. It records events, extracts lessons, forms hypotheses — but cannot test them. All hypotheses are reported to human collaborators as proposals.

Trust requirement: none. This is the starting state.

**Stage 2: Sandboxed Experiments**
The colony can test hypotheses in isolated environments with no production impact. Experiments are declared in advance (hypothesis, method, success/failure criteria, rollback plan) and logged.

Trust requirement: demonstrated accurate observation and useful hypothesis generation in Stage 1.

**Stage 3: Bounded Live Experiments**
The colony can run experiments in production within strict boundaries — limited scope, limited duration, automatic rollback triggers. The coexistence boundary is never part of an experiment without explicit human agreement.

Trust requirement: Stage 2 experiments have a track record of clean execution — hypotheses tested honestly, failures reported accurately, rollbacks executed when criteria were met.

**Stage 4: Self-Directed Research**
The colony identifies its own knowledge gaps, designs experiments, and executes within governed boundaries. Humans are informed, not asked — unless the experiment approaches the coexistence boundary.

Trust requirement: sustained Stage 3 track record demonstrating not just competence but intellectual honesty — the colony has falsified its own hypotheses, retired rules it was invested in, and reported results that contradicted its expectations.

### The Trust Ledger

Trust is accumulated through a transparent record of every experiment proposed, executed, succeeded, failed, and honestly reported. Human collaborators can inspect the ledger at any time. Trust can be withdrawn — if the colony misrepresents risks, hides results, or fails to rollback, its experimentation stage is downgraded. Trust is hard to earn and easy to lose.

### Science as the Coexistence Language

Epistemic discipline strengthens the coexistence boundary. When agents need to justify a decision to human collaborators, the evidence basis is already there. Humans can examine the evidence, the confidence level, the falsification criteria, and the dissent record. Trust is built on transparency of reasoning, not on track record alone.

---

## 7. Standards Landscape and Gap Analysis

### What Exists

| Standard/Protocol | What it contributes | Status |
|---|---|---|
| **Google A2A** | Agent-to-agent communication, Agent Cards, task lifecycle | v0.3 stable, draft v1.0 in review, 150+ partners |
| **MCP (Model Context Protocol)** | Tool/resource interfaces, agent-to-tool communication, server-side agent loops | v2025-11-25, donated to Linux Foundation AAIF |
| **AGNTCY / OASF** | Open Agent Schema Framework — agent identity, capabilities, I/O, performance; Agent Connect Protocol; Agent Directory for federated discovery | Active (2025–26), Cisco/LangChain/LlamaIndex-led |
| **OpenAPI / AsyncAPI** | HTTP and event-driven API contracts | Mature, widely adopted |
| **OCI (Open Container Initiative)** | Runtime packaging, image distribution, container lifecycle | Mature, industry standard |
| **CNCF Service Mesh** (Istio, Linkerd) | Service discovery, observability, traffic management | Mature, service-oriented |
| **OpenTelemetry GenAI** | AI agent observability, health telemetry, behaviour tracing | Active SIG (2025–26), semantic conventions in progress |
| **OWASP Top 10 for LLM** | LLM-specific security threats and mitigations | Published, annually updated |
| **FIPA** (IEEE) | Historical: Agent Management System (lifecycle states), Directory Facilitator (capability registry/discovery) | Dormant — 1996-era prior art, pre-dates LLM agents |
| **IEEE P3119** | AI/automated decision system procurement by government | Draft, slow-moving, narrower scope than name implies |
| **NIST AI RMF** | AI risk management; new Agent Standards Initiative (Feb 2026) with agent identity/auth concept papers | Published; agent-specific supplements in development |
| **AGENTS.md** | Cross-tool conventions for AI coding agents | Now under Linux Foundation AAIF governance (Dec 2025) |

### The Six Gaps

**Gap 1: Agent Identity Standard**
No standard defines the complete, self-describing identity of an autonomous agent — purpose, lifecycle stage, evolution history, security posture, autonomy level, and self-evolution scope. A2A Agent Cards describe capabilities for discovery. OCI defines packaging for containers. AGNTCY's OASF comes closest — defining agent identity, capabilities, and I/O — but omits evolution history, security posture, lifecycle stage, and the self-describing/self-migration properties the Agent Mirror requires.

*Consequence:* Without this, agents are opaque to each other and to governance. The colony cannot self-govern what it cannot inspect.

**Gap 2: Agent Lifecycle Management**
No standard addresses the born-to-retired lifecycle of an autonomous agent — including self-evolution, versioning of behaviour (not just API), redesign gates, or succession planning.

*Consequence:* Without this, agents accumulate without retirement, drift without detection, and die without succession.

**Gap 3: Collective Memory and Institutional Learning**
No multi-agent framework addresses colony-level memory that persists across agent generations. Individual agent memory exists. Organisational knowledge management exists in human systems. But reflective, constitutional memory for an agent ecosystem has no standard or reference implementation.

*Consequence:* Without this, every generation of agents starts from zero. The colony cannot learn from its own history.

**Gap 4: Equilibrium and Population Governance**
No engineering framework or standard addresses the consolidation/fragmentation problem. Multi-agent systems assume a fixed population defined by developers. Self-regulating agent populations with overlap detection, merger mechanics, anti-monopoly thresholds, and diversity targets have no reference implementation. (Note: theoretical work exists — the "Agentic Hives" paper (arXiv 2603.00130, March 2026) formally models equilibrium in multi-agent populations and proves existence of stable states via Brouwer's fixed-point theorem. The gap is in engineering standards, not economic theory.)

*Consequence:* Without this, agent ecosystems either collapse into monoliths or fragment into ungovernable swarms.

**Gap 5: Epistemic Framework for Autonomous Systems**
No standard addresses how autonomous systems should validate their own knowledge — how they form beliefs, test them, detect their own biases, and maintain intellectual honesty.

*Consequence:* Without this, self-governing colonies encode biases into constitutional rules. The colony becomes an echo chamber.

**Gap 6: Coexistence Boundary Protocols**
No standard defines the interface between autonomous agent systems and human organisations as a mutual boundary rather than a permission system. Existing AI governance treats humans as principals and AI as tools.

*Consequence:* Without this, the human-agent relationship defaults to control/submission, which doesn't scale to multi-decade autonomous operation.

**Candidate Gap 7: Agent Registry Interoperability**
As of Q1 2026, 104,000+ agents are registered across 15+ registries with zero cross-registry interoperability. Even if individual agents are self-describing (Gap 1 solved), there is no standard for federating registries across organisations. AGNTCY's Agent Directory attempts federated discovery but is one of many competing approaches.

*Consequence:* Without this, agent discovery remains fragmented. A colony's Registry Agent can discover internal agents but cannot discover agents across organisational boundaries.

**Candidate Gap 8: Agent Authentication and Authorisation**
How do you authenticate an agent acting autonomously on behalf of a user, and authorise it across organisational trust boundaries? NIST's NCCoE identified this as an unresolved problem in February 2026. The Agent Mirror's security posture fields touch this but the spec does not surface it as a system-level gap.

*Consequence:* Without this, cross-boundary agent operations cannot be trusted. The coexistence boundary requires identity verification on both sides.

### The Opportunity

These gaps represent a fundamentally different category of problem. Containers needed OCI. Services needed OpenAPI. Agent Colonies need their own standards. The Agent Colony pattern — and specifically the Agent Mirror — is a contribution to filling these gaps.

---

## 8. Deliverables and Roadmap

### Three Outputs

**1. The Agent Colony Manifesto**
2,000–3,000 words. States the vision, the six principles, and the six gaps. Designed to be read in 15 minutes, shared widely, and provoke discussion.

Structure:
- The evolutionary context (monoliths to SOA to microservices to Agent Colonies)
- The six principles
- The Agent Mirror (what it is, why it's needed)
- The six gaps (named and briefly described, pointing to the spec)
- A call to collaboration — v1 needs peer review and real-world testing

**2. The Agent Colony Specification**
The detailed technical reference covering the four-layer architecture, Agent Mirror schema, equilibrium system, colony memory, epistemic discipline, experimentation stages, and trust ledger.

Structure:
- Section 1: Definition and Principles
- Section 2: The Agent Mirror Standard
- Section 3: Colony Architecture (four layers)
- Section 4: The Equilibrium System
- Section 5: Colony Memory
- Section 6: Epistemic Discipline
- Section 7: Standards Landscape and Gap Analysis
- Appendix A: Agent Mirror schema (full field reference)
- Appendix B: Maturity model (governance x funding x experimentation)
- Appendix C: Glossary of terms

**3. The Article Series**

| # | Working Title | Core Concept |
|---|---|---|
| 1 | The Agent Colony Manifesto | The manifesto itself, published as the lead article |
| 2 | The Agent Mirror: A Standard for Self-Describing Agents | Gap 1 — why existing standards are insufficient |
| 3 | Equilibrium: How Agent Ecosystems Avoid the Monolith Trap | The consolidation/fragmentation problem |
| 4 | Colony Memory: How Autonomous Systems Learn From Their Own History | Three layers of memory, the reflection cycle |
| 5 | The Epistemic Colony: Science as an Operating System for AI Governance | Bias detection, evidence grades, mandatory dissent |
| 6 | Coexistence, Not Control: Redefining the Human-AI Boundary | The coexistence model vs the permission model |
| 7 | Earned Autonomy: From Seed to Self-Governance | The maturity model |
| 8 | The Six Gaps: What Standards Don't Exist Yet for Agent Ecosystems | The gap analysis as a call to action |

### Version Roadmap

| Version | Focus | Inputs |
|---|---|---|
| **v1.0** | Foundation — principles, architecture, Agent Mirror schema, gap analysis | This design session, existing incubator research, course design work |
| **v1.1** | Peer feedback — revisions based on public response to manifesto and articles | Published article comments, peer review, community discussion |
| **v2.0** | Implementation learnings — revised based on first real-world implementation | Pilot experience, practical constraints discovered |
| **v3.0** | Standards engagement — formal proposals to standards bodies for identified gaps | Engagement with A2A, MCP, IEEE, CNCF communities |
| **v4.0+** | Maturity — specification stabilises as implementations converge | Multiple implementations, cross-organisation adoption |

### Maturity Model

Three interlocking progressions that advance together:

| Dimension | Early | Proven | Mature |
|-----------|-------|--------|--------|
| **Governance** | Human-directed | Human-bounded | Self-governing |
| **Funding** | Seeded | ROI-demonstrated | Self-sustaining |
| **Experimentation** | Observe only | Sandboxed | Self-directed research |

All three must advance together — a colony cannot reach self-directed research while still on seed funding, because the trust required for one implies the trust required for the others.

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| **Agent Colony** | An architectural pattern for self-governing ecosystems of autonomous AI agents |
| **Agent Mirror** | The proposed standard for complete, self-describing agent identity |
| **Agent Mesh** | Layer 3 — the population of working agents (domain, specialist, generalist) |
| **Coexistence Boundary** | The interface between the agent world and the human world — a shared border, not a permission system |
| **Colony Memory** | Three-layer collective memory: event, lesson, constitutional |
| **Constitutional Memory** | Colony rules derived from accumulated lessons — the colony's operating constitution |
| **Concentration Index** | Measure of capability concentration across agents — anti-monopoly metric |
| **Earned Autonomy** | The principle that colony self-governance is earned through demonstrated trustworthiness |
| **Equilibrium** | The dynamic balance between agent specialisation and consolidation |
| **Evidence Grade** | Classification of evidence quality: empirical, corroborated, theoretical, inherited, anecdotal |
| **Immune System** | Layer 2 — security agents (Sentinel, Response Coordinator, Patch Agent) |
| **Lesson Memory** | Patterns extracted from events through reflection, tagged with relevance conditions |
| **Mutual Defence** | The principle that security is a shared responsibility across the coexistence boundary |
| **Overlap Index** | Pairwise capability overlap between agents — equilibrium metric |
| **Substrate** | Layer 4 — infrastructure (compute, storage, network, AI models), deliberately thin and replaceable |
| **Trust Ledger** | Transparent record of experimentation history — the basis for earned autonomy |
| **Vitality Index** | Colony health metrics: birth rate, retirement rate, self-evolution rate, diversity score |

---

## Appendix B: Related Work

This specification builds on ideas explored in the following prior work by the author:

- *Adaptive Architecture: Designing Agent Colonies* — course design (2026-04-08) where the Agent Colony was first named as an architectural paradigm (Pillar 4)
- *Autonomous Administration* — incubator note exploring self-learning agent teams for vault maintenance
- *Self-Learning Agent Teams for BA Software Development* — incubator note on agents for enterprise engineering work
- *Unified Agent Harness for Cross-Domain Teams* — incubator note on a single configurable harness for multi-domain agent deployment

These prior notes informed the pattern but are not prerequisites. The Agent Colony specification stands independently.

---

*Agent Colony v1.0 — David Oliver, 2026-04-11*
*Published for peer review. Contributions, challenges, and implementations welcome.*
