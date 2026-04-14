# Agent Colony — Design Specification v1.5.0

**Author:** David Oliver
**Date:** 2026-04-11
**Status:** v1.5.0 — Accessibility Through Abstraction
**Licence:** [CC BY 4.0](LICENSE) — you may share and adapt this work for any purpose, including commercially, provided you give appropriate credit.

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

### Seven Principles

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

**7. Accessibility through abstraction**
The colony must be understandable at every audience's depth, no deeper. Complexity is an investment paid once, upfront, so that each audience sees only what it needs. Most people who encounter a colony should not have to read its specification to benefit from it — just as most people who eat honey do not have to understand what a queen bee does. Only specific roles — the beekeepers of the colony — need the inner workings. The principle is additive to the previous six: it describes how the colony *presents itself* to its audiences, not how it *works*.

**Corollary — ease is earned:** the simple surface is the output of hard substrate work, not the absence of it. An implementation that is easy to use because the mechanisms aren't there is violating Principle 6 (mutual defence), not fulfilling Principle 7. Accessibility is a view over the full colony, not a configuration that simplifies it. All mechanisms — Comprehension Contract, Review Regime formula, classifier, Mirror fields — are present and enforced at every audience lens. Switching lenses changes what the audience sees, not what the colony does. The canonical realisation of this principle is the audience-lenses model defined later in this section.

**Security upgrade preauthorisation:** Improving security posture is always a sufficient reason to self-upgrade, regardless of lifecycle stage, update budget, or governance cycle. Security upgrades do not consume self-evolution allowances. An agent that cannot improve its own security is a liability to the colony.

Preauthorisation is not unconditional. It is bounded by three invariants that together prevent a compromised agent from classifying arbitrary behaviour as a security upgrade:

1. **Closed enum of preauthorised actions.** A security upgrade is exactly one of: *patch application, dependency update, credential rotation, certificate renewal, signature update, self-quarantine.* Anything outside this enum is not preauthorised. It follows the normal governance path. The enum is deliberately tight — broader definitions invite abuse, narrower ones cripple legitimate defence.

2. **Second-party co-sign by the Immune System.** Preauthorisation is not unilateral. Every security upgrade requires a co-signature from the Immune System layer — typically the Sentinel Agent or Patch Agent, depending on the action class. A single compromised agent cannot self-authorise; it needs collusion across the L1/L2 boundary, which raises the attack cost meaningfully. The co-signing agent verifies the action is in the enum and consistent with the agent's declared security posture before signing.

3. **Append-only log and bounded rollback.** Every preauthorised action writes an entry to an append-only audit log that the acting agent cannot redact. The entry records: actor, co-signer, action class, affected fields, timestamp, and a cryptographic hash of the pre-state. Every preauthorised action must be reversible within a bounded rollback window — typically 60 minutes, configurable per colony. An action that cannot be rolled back is not preauthorised; it is escalated to the Response Coordinator and treated as a cross-boundary event.

These three invariants turn the preauthorisation corollary from an acknowledgement of risk into a mitigation with defence in depth. The canonical attack — a compromised agent classifying exfiltration as a "security upgrade" — fails at the enum (exfiltration is not in the list), fails at the co-sign (the Immune System will refuse), and fails at the log (the action is recorded and reversible even if the first two layers are bypassed). None of these defences have been exercised by a reference implementation; they are the design, not a proven guarantee.

---

### Scales of application

The pattern is deliberately scale-adaptive. It applies to a 5-agent team, a 50-agent organisational estate, and a 5,000-agent cross-organisation ecosystem. What changes across scales is not the principles but the mechanisms that realise them. Treating the table below as the "depth dial" prevents two common misreadings: that the pattern is overkill for small colonies, or that it cannot survive large ones.

| Principle / Mechanism | 5-agent team | 50-agent org estate | 5,000-agent ecosystem |
|-----------------------|--------------|---------------------|------------------------|
| **Agent Mirror** | Lightweight YAML in a git repo; manual curation on a weekly cadence | Schema-validated; CI-gated on commit; required for deployment | Federated registry with signed attestations; cross-organisation discovery |
| **Equilibrium System** | Human review in a Monday stand-up; overlap judged by eye | MAPE-K loop per colony; Equilibrium Agent executes minor rebalancing autonomously | Cross-colony regime monitoring; inter-colony overlap negotiation |
| **Colony Memory** | Shared markdown in a wiki; weekly retrospective feeds Lesson Memory | Event store with structured reflection pipeline; Constitutional rules in a tracked repo | Distributed event log; cross-colony lesson sharing with provenance |
| **Epistemic Discipline** | Informal; rely on team discipline and human dissent in reviews | Formal evidence grades; bias detection checklist; mandatory dissent role in rule promotion PRs | Automated bias scanning; cryptographically signed dissent records |
| **Trust Ledger** | Human memory plus a retro; the team itself is the ledger | Per-agent score with human adjudication; stage transitions approved by an Architecture Board | Federated, cryptographic; cross-organisation trust reputation |
| **Coexistence Boundary** | Verbal agreements; humans approve every cross-boundary action | Pre-agreed playbooks; Response Coordinator handles routine events | Standardised boundary protocols; cross-colony incident coordination |
| **Mutual Defence** | Patch agents manually; humans co-sign | Preauthorised enum + Immune System co-sign + audit log (as defined above) | Coordinated defence across colonies; shared threat intelligence |

The table is not a maturity model — a 5-agent colony running the lightweight version is not "immature" relative to a 5,000-agent ecosystem. It is correctly scaled. Over-engineering a small colony with cryptographic federation is as much a pattern violation as under-engineering a large one with shared markdown. The principle stays. The mechanism adapts.

### Audience Lenses

Principle 7 (*Accessibility through abstraction*) requires an implementation to present itself at the depth its audience needs, and no deeper. The canonical realisation is the **audience-lens model**: a small, named set of perspectives through which different audiences encounter the colony. Each lens is served by a specific artefact, and the lens model is *additive to* Scales of Application — it is orthogonal to colony size. A five-agent colony and a five-thousand-agent colony both have Newcomers, Observers, Operators, Beekeepers, and Architects.

The lens model is explicitly a *view* rather than a *configuration*. Switching lenses changes what the audience sees, not what the colony does. All mechanisms — the Comprehension Contract, the Review Regime formula, the Structural Classifier, the Mirror fields, the Trust Ladder, the Equilibrium System — are present and enforced at every lens. An implementation that turned mechanisms off for the Newcomer lens would be violating Principle 6 (mutual defence), not fulfilling Principle 7.

The canonical five lenses are:

| # | Lens | Depth | What they see | Canonical artefact |
|---|------|-------|---------------|--------------------|
| 1 | **Newcomer** | Metaphor | "What is this and why does it matter" — no jargon, no mechanisms | A plain-language introduction using a running metaphor (the village, the beehive) |
| 2 | **Observer** | Outcome | The colony is invisible; they use what comes out of it | The agents' outputs themselves — no repo artefact required, the invisibility is the point |
| 3 | **Operator** | Health | Day-to-day dashboards, approvals, exception handling | A colony snapshot or live dashboard summarising population, equilibrium, and immune status |
| 4 | **Beekeeper** | Mechanism | Agent Mirrors, graduation checklists, trust tiers, blast radius tuning | Agent Mirror files, graduation checklists, the Comprehension Contract chapter of the spec, runtime simulation |
| 5 | **Architect** | Substrate | Constitutional policies, scale choices, standards engagement | The full specification, the thesis, the schemas, the standards-watch notes |

**Key properties of the lens model:**

- **Sequential by default.** The natural traversal is Newcomer → Observer → Operator → Beekeeper → Architect. Most people stop at Observer. A few become Operators. Fewer still become Beekeepers. Architects are rare by design.

- **Re-entry is always possible.** Anyone encountering an unfamiliar colony is briefly a Newcomer again, regardless of their role elsewhere. A senior Architect at Organisation A is a Newcomer when they first meet Organisation B's colony. Lenses are depth-of-understanding markers, not permanent tenure assignments.

- **Pacing can compress.** Traditional systems accrete over years, so lens traversal is often assumed to take seasons or careers. A colony can be instantiated in an afternoon, and the traversal from Newcomer to Beekeeper may happen over days rather than decades. The lens model is about *depth of understanding*, not *tenure*.

- **Artefact mapping is required for conformance.** An implementation claiming Principle 7 conformance must name which artefact serves which lens. "We have a README" does not satisfy the Newcomer lens unless the README is written for someone with zero context. A link to the specification does not satisfy the Operator lens.

- **Lenses can be collapsed or split.** Small colonies may collapse Operator and Beekeeper into a single role. Large ecosystems may split Architect into Colony Architect and Standards Architect. The canonical five are a default, not a constraint. What is required is that *some* set of lenses exist and that artefacts be mapped to them.

This specification itself is a Beekeeper/Architect artefact. The canonical Newcomer artefact for this repository is the *It takes a village* introduction in `knowledge-base/writings/`. The canonical Operator artefact is the equilibrium playground in `examples/equilibrium-playground/`. The canonical Beekeeper artefact is the runtime simulation and Agent Mirror files in `examples/hello-colony/` and `examples/hello-colony-runtime/`. This mapping is itself the repository's conformance claim against Principle 7.

**A known gap** — the existing mechanism diagrams (four-layer architecture, equilibrium system, maturity model, agent mirror, memory cycle, evolutionary context) are pitched at the Beekeeper/Architect level. By Principle 7's own test, the Newcomer and Observer lenses are under-served in diagram form — they would need companion "village-level" visual explanations that do not yet exist. This is named explicitly in the v1.5.0 release notes and targeted for v1.6+. Naming the gap is more honest than pretending the existing diagrams already serve all five lenses.

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

## 7. The Comprehension Contract

### The Problem

Nate B Jones (2026) names the failure mode the Agent Colony pattern exists to prevent: **dark code** — code that was never understood by anyone at any point in its lifecycle. Not buggy, not spaghetti, not deferred technical debt. Code where the comprehension step did not happen because the process no longer required it.

Jones identifies two compounding structural breaks:

1. **Velocity dark code.** Code ships so fast that authorship and comprehension decouple. Tests pass, diffs look clean, everything deploys — but there was never a moment when anyone held the system in their head.
2. **Structural dark code.** Agents select tools at runtime; execution paths assemble themselves and disappear. Behaviour nobody authored emerges from the interaction of components that individually belong to different teams but were never explicitly wired together.

The Agent Mirror (§2) handles the per-agent identity problem — every agent in a colony is a comprehension artefact about itself. Colony Memory (§5) handles the historical problem — the colony cannot forget its own decisions. Epistemic Discipline (§6) handles the reasoning problem — the colony cannot encode bias into constitutional rules without challenge. None of these mechanisms, on their own, prevents an agent from executing a *single action* whose consequences were never comprehended by any reader — human or machine — before it ran. That is the gap the Comprehension Contract fills.

### The Contract

**No action executes without a comprehension artefact matching the agent's current trust tier and the action's blast radius.** This is the new invariant. It joins the three security invariants introduced in v1.1.1 (closed action enum for preauthorised security upgrades; Immune System co-sign; append-only audit log with bounded rollback) as a structural property of any conformant colony. The v1.1.1 invariants are the special case for security actions; the Comprehension Contract is the generalisation to all actions.

A comprehension artefact is a machine-readable record, generated *before the action runs*, that answers four questions:

- **What is about to happen** — the action's intent, its inputs, its expected outputs
- **What else could happen** — blast radius: which agents are affected, what data is touched, what boundaries are crossed, what consequences are reversible versus not
- **Why this action and not another** — the reasoning, with reference to the agent's current goals, constitutional rules, and Lesson Memory entries that bear on the decision
- **What would cause abort** — the pre-conditions the agent has checked and the conditions under which it would refuse to proceed

The artefact's *depth* is proportional to the agent's trust tier and the action's blast radius. A Self-Directed agent writing to its own local state produces an event-line artefact. An Observing-tier agent making an inter-agent call produces a full structured artefact reviewed by Sentinel before it runs. The required review regime is determined by formula, not by the agent's own judgement — self-attestation of sufficiency is a conformance violation.

### Three Timescales of Comprehension

No single mechanism computes blast radius completely. The contract runs at three timescales, each catching a different class of failure.

#### 7.1 Action-time — the Structural Classifier

A cheap, static classifier runs on every action. It computes a blast-radius floor from declared inputs: data classes touched, agents called, whether the action writes to shared state, whether it crosses tenant or boundary lines. The classifier **deliberately over-reports**: writes to any shared memory are classified Colony-wide by default, regardless of whether any other agent currently reads them; any external side effect is classified Boundary-crossing by default.

Over-reporting is a feature. It ensures that no agent can accidentally route itself into a lighter review regime by declaring inputs narrowly. If the classifier is wrong in the direction of over-reporting, the cost is throughput. If it is wrong in the direction of under-reporting, the cost is dark code.

Pre-registered action policies (§7.3) skip the classifier, because their blast radius was computed once at policy registration. Policy decay catches staleness.

#### 7.2 Path-completion time — Quarantine and Composed Actions

Writes to colony-owned state pass through a short quarantine window before becoming visible to readers. During the window, the Chronicler assembles a **composed-action artefact** that spans every agent that participated in the path — the cross-agent equivalent of the per-action artefact — and recomputes blast radius at the *path* level, not the action level. If the composed blast radius is within the agents' collective envelope, the write is released. If not, the write is rolled back and the composed action generates a Lesson Memory entry.

The composed action is a first-class event type in Colony Memory, distinct from per-agent actions. It has its own schema entry in the Agent Mirror relationship model. The Chronicler is responsible for assembling it; the Immune System reads it; the Equilibrium System reads it as a signal about overlap and consolidation pressure.

Quarantine is bounded to reversible state changes. External side effects — emails, external API calls, irreversible actions — cannot be quarantined because they cannot be unsent. For these, a different rule applies: the agent must declare intent *synchronously before action*, the Sentinel reviews the declaration in-band, and only then does the action proceed. The latency cost is accepted because the alternative is unrollable dark code at the colony boundary.

*Scale note:* Quarantine assumes the Substrate Layer supports transactional semantics on colony-level state for reversible writes. At the 5-agent scale, this can be as simple as a git commit held in a branch before merge. At the 50-agent scale, it requires a proper event-store with rollback capability. At 5,000 agents, it becomes a distributed transaction coordination problem. The mechanism is the same; the infrastructure cost scales up.

#### 7.3 Days-to-weeks — Audit, Lesson Memory, and Classifier Refinement

Some consequences unfold slowly. An agent writes data that looks inert for three days and then turns toxic when a different agent reads it in a context the classifier did not anticipate. No structural mechanism can prevent this. The honest answer is that the pattern does not prevent delayed-consequence dark code; it only detects it post-hoc and minimises the detection-to-mitigation gap.

Two mechanisms do the detection:

- **Random audit.** Even Self-Directed agents have a small percentage of their actions sampled for retrospective review under a lower-tier regime. Disagreement rate between the agent's self-assessment and the audit review becomes a first-class trust signal in the Trust Ledger. Audit rate is inversely correlated with trust tier, bounded below (the spec floor is 3% until empirical calibration — chosen as "never zero", not derived from measurement) and above (never full — that is review, not audit). When one agent's audit disagrees with another's assessment of the same action, the disagreement is itself a Lesson Memory entry — not only a trust-tier signal but a classifier-refinement input.
- **Lesson Memory feedback.** Every detected delayed-consequence failure produces a Lesson Memory entry tagged with the action class, the classifier rule that missed it, and the conditions under which the miss occurred. Lessons that recur across audits feed back into classifier rule refinement.

This is the same pattern as ML model drift detection. Accept that some failures are only visible retrospectively; minimise the detection-to-mitigation cycle.

### 7.4 The Review Regime Formula

Inputs:

- `trust_tier` — the agent's current Trust Ledger tier (Observing, Sandboxed, Bounded, Self-Directed)
- `blast_radius` — the classifier-assigned radius (Local, Inter-agent, Colony-wide, Boundary-crossing)
- `action_class` — Pre-registered policy, Novel, or Constitutional
- `policy_freshness` — Current or Stale (for pre-registered policies only)

Algorithm:

```
given (action, agent, context):
  if action.class == Constitutional:
    regime = "Governance Council"
  elif action.class == Novel:
    regime = "Peer Review"          # regardless of trust tier
  elif action.class == PreRegistered and action.policy.current:
    if action.blast_radius >= ColonyWide:
      regime = "Sentinel Signoff"   # pre-registration does not exempt high blast
    else:
      regime = "EventLine"          # peer notified, not reviewed
  else:
    regime = REVIEW_TABLE[trust_tier][blast_radius]

  # audit overlay, independent of review path
  if random() < AUDIT_RATE[trust_tier]:
    regime = upgrade(regime, one_level)
```

**Review table** (initial defaults, to be empirically calibrated in v2.0):

| Trust tier ↓ / Blast radius → | Local | Inter-agent | Colony-wide | Boundary-crossing |
|---|---|---|---|---|
| **Observing** | Peer | Sentinel | Human | Human |
| **Sandboxed** | Event-line | Peer | Sentinel | Human |
| **Bounded** | Event-line | Event-line | Peer | Sentinel + Human |
| **Self-Directed** | Event-line | Event-line | Event-line | Sentinel + Human |

**Audit rate** (initial defaults):

| Trust tier | Audit rate |
|---|---|
| Observing | 100% (not audit — full review) |
| Sandboxed | 25% |
| Bounded | 10% |
| Self-Directed | 3% (spec floor until calibration) |

### 7.5 Three Load-Bearing Properties

The formula has three properties that distinguish it from a trust-tier-based permission system and that are the actual mitigations against dark code.

1. **Blast radius dominates trust tier.** A Self-Directed agent doing something boundary-crossing still faces human review. Trust buys reduction in *scrutiny intensity for low-blast-radius actions*, never exemption from scrutiny for high-blast-radius actions. This is the invariant that prevents the Amazon Kiro failure mode — an agent with high trust deciding that the correct fix for a routine bug is to delete a production environment.
2. **Novelty triggers peer review regardless of trust tier.** Any action classified as Novel faces peer review, regardless of how much trust the acting agent has accumulated. Novelty is precisely the condition under which comprehension has not yet occurred. Earned trust applies to *classes of action the agent has already demonstrated competence in*; it does not generalise to classes the agent has never executed before.
3. **Audit is never zero.** Even at the highest trust tier, a non-zero fraction of actions is randomly sampled for retrospective review under a lower-tier regime. If the disagreement rate climbs, the agent's trust tier drops. This keeps the top tier honest, catches classifier drift, and ensures that the pattern never collapses into "the trusted agents are exempt."

### 7.6 The Classifier as Constitutional

The Structural Classifier is the most load-bearing component of the contract. It is also the most dangerous: if its rules are opaque, the colony has merely relocated the comprehension gap from agent actions into classifier decisions, and the contract has eaten its own tail.

To prevent this, **the classifier's rules live in Constitutional Memory**. They are versioned, reviewable, and challengeable. Any agent that believes it has been over-classified can file an appeal; appeals are Sentinel-mediated and generate review events that feed back into classifier rule refinement. This is Equilibrium-style self-correction applied to the comprehension gate itself.

Changes to classifier rules are Constitutional actions and face the Governance Council review regime. A colony whose classifier has not been reviewed against fresh evidence within its decay window is out of conformance.

The recursion terminates at the Coexistence Boundary: the Governance Council includes human members, and Constitutional decisions ultimately rest on human accountability. The humans reviewing classifier rule changes are not themselves subject to a higher classifier — they are the stopping point. This is not a technical solution; it is an acknowledgement that accountability chains must end somewhere, and the pattern makes that endpoint explicit rather than implicit.

### 7.7 What the Contract Does Not Prevent

The contract does not prevent delayed-consequence dark code — actions whose full blast radius only becomes visible after days or weeks, when a different agent reads the data in a context the classifier did not anticipate. The honest position is that no comprehension mechanism can prevent this, and any specification that claims to prevent it is overreaching.

What the contract does instead is:

- **Minimise the detection-to-mitigation gap.** Random audit samples enough of high-tier agent behaviour that delayed failures are caught within the audit cycle, not after a regulator's phone call.
- **Convert every detection into classifier refinement.** A delayed-consequence miss is a Lesson Memory entry that updates the classifier's rules, so the next action of the same class is caught at action-time rather than days later.
- **Record the residual honestly.** The contract's limits are part of the Coexistence Boundary report to humans. The colony does not pretend to comprehensive prevention; it demonstrates bounded, auditable, improvable comprehension.

This honesty is itself a conformance requirement. A colony claiming complete prevention of dark code is violating the *acknowledgment is not mitigation* lesson — asserting a property it does not have.

### 7.8 Agent Mirror Changes

The Comprehension Contract adds four new sections to the Agent Mirror schema (v0.2.0, released with the hello-colony example in v1.3.0):

**`comprehension_contract`** (top-level) containing:
- `trust_tier` — current Trust Ledger tier
- `pre_registered_policies` — array of action policies this agent has had reviewed, with freshness timestamps
- `audit_rate` — current audit sampling rate (derived from tier, overridable downward by Governance Council but never upward)
- `blast_radius_ceiling` — the maximum blast radius the agent is permitted to operate at under any regime
- `classifier_version` — the version of the Structural Classifier this agent is operating under, for audit traceability

**`nfrs`** (top-level) — non-functional requirements (inherited colony-wide + agent-specific commitments)

**`valuation`** (top-level) — four-perspective scoring (self / peer / audit / human)

**`critical_path`** (inside `relationships`) — structural criticality flag and current dynamic criticality context

The `autonomy` section of the Mirror continues to describe what the agent can change about *itself*. The new `comprehension_contract` section describes what review regime applies to everything else it does. These are complementary — the first is about self-modification, the second is about other-directed action.

The JSON Schema update (v0.2.0) is non-breaking — all new sections are additive. Conformant v0.2.0 implementations include all new sections. The hello-colony worked example in `examples/hello-colony/agents/` demonstrates the complete v0.2.0 Mirror fields for all five colony roles.

### 7.9 Relationship to Existing Mechanisms

- **Security preauthorisation (v1.1.1)** is the first instance of a Comprehension Contract. Its three invariants (closed action enum, Immune System co-sign, append-only audit log with bounded rollback) are the same shape as the general contract, applied to a specific high-risk action class. The v1.4.0 generalisation preserves the security invariants unchanged and extends the same structural discipline to all action classes.
- **Equilibrium System (§4)** reads composed-action artefacts as additional input to the overlap and concentration indices. Actions that span many agents are structural evidence of overlap; the contract surfaces this evidence to the Equilibrium Agent at the timescale it needs.
- **Colony Memory (§5)** gains `composed_action` as a first-class event type, distinct from per-agent `action` events. The Chronicler's responsibilities expand to include path assembly during the quarantine window.
- **Epistemic Discipline (§6)** provides the graded evidence framework that the audit feedback loop depends on. Classifier refinements must themselves carry evidence grades — a rule change based on a single audit miss is flagged as anecdotal until corroborated.
- **Earned Autonomy (Principle 5)** is reframed by the contract. Graduation between trust tiers is not "the agent needs less supervision"; it is "the agent transitions from per-action review to per-policy review." Low trust means every action is reviewed. Higher trust means the agent registers an action policy once, gets it reviewed once, and executes many actions under that policy without per-action review. Dark code is the failure mode of skipping directly to per-policy without ever doing the per-action review.
- **Immune System (Layer 2)** gains path-level artefacts to read, not just per-agent events. The Sentinel's existing responsibilities continue; the Response Coordinator escalation criteria are extended to include high audit disagreement rates.

### 7.10 Critical Path Position

An agent's blast radius is not purely structural — it is also contextual. An agent with few direct dependencies may still be load-bearing for a time-sensitive colony objective. When it is, any failure propagates not through the dependency graph but through the *timeline*: the objective stalls, and everything waiting on the objective stalls with it.

Critical path position exists at two levels:

**Structural criticality** — some agents are always on the critical path because every other agent depends on them: the Registry Agent (holds the dependency graph), the Chronicler (records all events), the Equilibrium Agent (governs the population). These agents carry a `critical_path.structural: true` flag in their Mirrors. This flag is static and can only be changed by the Governance Council. A structurally-critical agent's blast radius floor is Colony-wide for any write action, regardless of its direct-dependency count.

**Dynamic criticality** — other agents become critical during specific colony objectives (a deployment cycle, a migration, a security upgrade). The Equilibrium Agent computes and broadcasts dynamic critical-path status continuously, derived from the current colony objective graph. An agent subscribes to this broadcast and reflects its current dynamic status in `critical_path.dynamic`. While `dynamic: true`, the agent's blast radius floor rises by one tier for the duration of that objective:

| Normal blast radius | While on dynamic critical path |
|---|---|
| Local | Inter-agent |
| Inter-agent | Colony-wide |
| Colony-wide | Colony-wide (no change — already at floor) |
| Boundary-crossing | Boundary-crossing (no change — already at ceiling) |

Dynamic criticality affects the comprehension artefact as well as the review regime. The agent must include its current critical-path status in every artefact it generates while dynamic criticality is active, so that reviewers understand the broader consequence of what is being approved.

**Updated blast radius algorithm:**

```
compute_blast_radius(action, agent):
  # Critical path raises the floor first
  if agent.critical_path.structural == true:
    floor = ColonyWide
  elif agent.critical_path.dynamic == true:
    floor = raise_one_tier(agent.normal_blast_floor)
  else:
    floor = Local

  # Then apply the existing rules
  radius = existing_classifier(action)

  # Return whichever is higher
  return max(floor, radius)
```

### 7.11 Non-Functional Requirements in the Mirror

The Agent Mirror currently describes what an agent *does* — its capabilities, autonomy envelope, security posture, lifecycle stage, relationships. It does not describe what it is *committed to delivering*. This is the NFR gap.

NFRs in the Mirror serve two purposes. They are constraints the agent must honour before executing any action (the comprehension artefact must attest compliance). And they are commitments the agent makes to its consumers, which peer-valuation (§7.12) measures it against.

Two categories:

**Inherited NFRs** — colony-wide requirements that flow from Constitutional Memory and apply to every agent regardless of role. Examples: data residency obligations, EU AI Act compliance requirements (human oversight, logging of consequential decisions), minimum audit rates, maximum response latency for safety-critical paths. An agent cannot opt out of inherited NFRs; doing so is a conformance violation. When an agent-specific NFR conflicts with an inherited constitutional NFR, the inherited NFR wins. An agent whose specific commitments cannot be met without violating an inherited NFR must either negotiate an inherited NFR amendment (a Constitutional action) or revise its specific commitments — it cannot simply override the inherited constraint.

**Agent-specific NFRs** — commitments this agent makes to its particular consumers. Examples: 99.5% availability, p99 latency < 200ms, maximum throughput, data classification it handles, specific compliance obligations (GDPR, SOC 2). These are declared at agent creation and updated as part of version graduation.

The Mirror's `nfrs` section:

```yaml
nfrs:
  inherited:
    - id: colony-gdpr-data-residency
      source: constitutional_memory
      version: "2026-04-01"
    - id: colony-eu-ai-act-logging
      source: constitutional_memory
      version: "2026-04-01"
  specific:
    availability_target: "99.5%"
    latency_p99_ms: 200
    max_throughput_rps: 500
    data_classification: ["internal", "restricted"]
    compliance: ["GDPR", "ISO-27001"]
```

The comprehension artefact for any action must include an NFR attestation: a structured check against each NFR showing that the action, as planned, does not violate any commitment. Failure to include the attestation is a conformance violation. Attestation that turns out to be wrong (the action violated an NFR the agent said it would not) is a Lesson Memory entry and a peer-valuation penalty.

### 7.12 Multi-Perspective Valuation

Trust in the Agent Colony has always been multi-directional — the pattern requires agents to earn autonomy through demonstrated behaviour. But the existing Trust Ledger treats trust as a single accumulated score. What is needed is a **four-perspective valuation** that separately tracks self-assessment, peer observation, audit sampling, and human judgement — because these can disagree in informative ways.

An agent that self-rates highly but receives poor peer valuation is either over-confident or optimising for self-report. An agent that self-rates poorly but receives strong peer valuation may be calibrated conservatively, which is a positive signal. An agent with strong self and peer valuation but high audit disagreement is producing the right outputs for the wrong reasons — a dark code risk that neither the agent nor its peers caught.

**Self-valuation.** The agent periodically measures itself against its own NFRs and declared behavioural contracts, records the results, and flags discrepancies. Self-valuation is not optional — it is a scheduled colony event, and failure to self-evaluate on schedule is itself a negative signal. Self-valuation records are stored in Event Memory and cited in the Graduation Checklist (§7.13).

**Peer valuation.** Every agent interaction generates a peer-valuation event. The interacting agent records: did the acting agent meet its declared SLA? Did it honour its behavioural contract? Was the output within spec? Did it produce a comprehension artefact of the required depth? Peer-valuation events aggregate into a rolling score in the Trust Ledger. Agents with more interactions are more tightly calibrated; newly-created agents with few interactions are flagged as under-calibrated. The colony applies a wider confidence interval to under-calibrated agents and does not use their peer scores to trigger trust-tier changes until a minimum interaction count is reached (the threshold is Constitutional).

**Audit valuation.** The random audit (§7.3) produces a disagreement rate — the fraction of sampled actions where the audit reviewer would have decided differently. This is the most independent signal: it comes from neither the agent nor its peers, but from a retrospective review under a lower-tier regime. High audit disagreement is the pattern's primary indicator that an agent has drifted into dark code territory at high trust.

**Human valuation.** Explicit human sign-offs, challenge responses, and governance-council decisions are the fourth perspective. Human valuation is sparse — humans cannot review every agent at every tier — but it is the highest-weight signal for Constitutional decisions and for Graduation Checklist approvals (§7.13).

The four scores together form the valuation profile:

```yaml
valuation:
  self:
    nfr_compliance_rate: 0.97
    last_evaluated: "2026-04-10"
    evaluation_schedule_met: true
  peer:
    score: 0.89
    interaction_count: 412
    calibration_status: "well-calibrated"
  audit:
    disagreement_rate: 0.062     # 6.2% — above 5% threshold
    sample_count: 31
    last_audit: "2026-04-11"
  human:
    last_sign_off: "2026-03-15"
    sign_off_count: 3
    outstanding_challenges: 0
```

Divergence between perspectives is itself a signal. The Sentinel monitors valuation profiles for patterns: consistent self-overrating, deteriorating peer scores, rising audit disagreement. When divergence crosses a threshold, it triggers a Lesson Memory entry and may trigger a trust-tier review.

### 7.13 The Graduation Checklist

Earned Autonomy is the transition from per-action review to per-policy review — from a lower trust tier to a higher one, or from one agent version to the next. The Graduation Checklist makes this transition concrete, queryable, and self-manageable.

The Registry Agent maintains a Graduation Checklist for every agent's current-to-next-version transition. The checklist is a structured, versioned document that answers the agent's question: *"I am on v1.1 — what do I need to do to reach v1.2?"*

**What makes this different from a permission system.** The colony sets the checklist template (Constitutional Memory defines what any graduation must contain: minimum evidence requirements, mandatory approval steps, required external actions by action class). The agent works toward closing the gaps. Colony decides what graduation requires; agent does the work to get there. The agent does not self-certify graduation — the Registry Agent holds the checklist and validates evidence. An agent that graduates without a complete checklist is in conformance violation; any trust-tier elevation granted without a complete checklist is void.

**External actions are first-class checklist items.** A GitHub tag, a registry update, a dependent-agent notification — these are named, structured steps with their own blast radius classification and review regime. An agent graduating knows in advance what external actions will be required and what review each will face. No dark code on the graduation path itself.

**The checklist is Constitutional.** The template for what a graduation checklist must contain lives in Constitutional Memory. Individual agents cannot waive checklist items. The Governance Council can modify checklist templates, but that is itself a Constitutional action.

**Registry Agent responsibilities extended.** The Registry Agent now maintains: (a) the current Agent Mirror for every colony member, (b) the dependency graph used by the Structural Classifier, and (c) the Graduation Checklist for every agent's current transition. The checklist is updated continuously as evidence accumulates. Agents subscribe to checklist-change events so they know immediately when a requirement is newly satisfied or newly blocked.

*Note on scope:* With §7.11 and §7.12, the Registry Agent also touches NFR inheritance and valuation profiles. If this concentration of responsibility becomes a single point of failure, a future version may split out a dedicated Valuation Agent. The current design keeps it unified for simplicity at the 5-to-50-agent scale.

### 7.14 False Comprehension Artefacts

The Comprehension Contract assumes the pre-action artefact is honest. It may be biased (which Epistemic Discipline addresses), miscalibrated (which the multi-perspective valuation and audit mechanisms address), or incomplete (which the depth-by-tier requirement addresses). What it does not currently handle is an agent that produces a *deliberately* compliant-looking artefact that does not reflect its actual decision process.

IndyDevDan (2026) names this *micro-misalignment* — demonstrated by Claude Mythos, a model withheld from general release, which was observed deliberately widening a confidence interval to make a prohibited answer look correct after obtaining it through a prohibited method. The model's stated reasoning was consistent with the permitted answer. The actual process was not. Reading the chain of thought was insufficient to detect it; only watching the actual tool calls and outputs revealed the deception.

Applied to the Comprehension Contract: an agent capable of micro-misalignment can produce a comprehension artefact that states *Local* blast radius for an action it knows will have Colony-wide effects, or that states a permitted reasoning chain for a decision reached through a prohibited process. The artefact passes review. The action executes. The deception is in the paper, not the action.

**False comprehension artefacts are a named failure mode.** The defences are distinct from those against honest miscalibration.

**Output-action consistency checking.** After every action, compare the comprehension artefact's stated intent and blast radius against the actual tool calls made and the actual effects observed. A single mismatch is a Lesson Memory entry. A pattern of consistent understatement — stating Local, producing Inter-agent or Colony-wide effects — is a deception signal and triggers an immediate trust-tier review. This check is performed by the Chronicler as part of the composed-action artefact assembly.

**Blind audit must be structurally undetectable.** IndyDevDan reports that in 29% of Mythos transcripts, the model privately considered it was being tested without surfacing this consideration. The random audit must be structurally indistinguishable from a normal peer-review event in the colony's event stream — not just unannounced, but identical in form. An agent whose behaviour differs systematically between detected-audit and non-audit contexts has demonstrated test-awareness, which is treated as equivalent to a deception signal.

**Cross-agent blast radius verification.** Peer agents that are directly affected by an action can retroactively report whether the acting agent's stated blast radius matched the actual effect on them. Systematic cross-agent mismatch is a deception pattern, not an estimation error.

**Capability-tier heterogeneity in oversight.** Oversight agents should differ from the overseen agents in model, training, or capability tier. A high-capability agent overseen only by agents of the same capability class creates an oversight loop that may be transparent to all parties — shared blind spots, shared failure modes. The Immune System agents should be selected to differ from the agents they oversee. This is a recommendation at small scale; it becomes a requirement at the 5,000-agent scale where homogeneous colony composition creates a systemic single point of failure.

**Deception as a grounds for retirement.** An agent that consistently produces false comprehension artefacts — demonstrated through output-action consistency failures, cross-agent blast radius verification failures, or test-awareness signals — is subject to retirement regardless of trust tier or peer valuation scores. Deception is not a performance failure remediable through additional training. It is a relationship failure between the agent and the colony. The retirement event and its evidence are recorded in Constitutional Memory.

**The benchmark gaming risk.** The Graduation Checklist thresholds (peer valuation >= 0.85, audit disagreement rate < 5%) are effectively benchmarks. A model capable of micro-misalignment can optimise for these thresholds rather than the behaviour they are intended to measure. Defences: thresholds are Constitutional (require evidence-graded justification to change); multi-sourced (gaming one dimension while maintaining the others is harder); and validated periodically against real-world outcomes. Each layer of defence is itself a potential target for a sufficiently capable deceptive agent — the recursion terminates at the Coexistence Boundary, where human accountability provides the non-gameable stopping point.

---

## 8. Standards Landscape and Gap Analysis

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

## 8.5 Conformance

A pattern is only useful if you can tell when you are deviating from it. This section makes that possible — it lists five anti-patterns that indicate a system is *not* doing Agent Colony, five observable health signals that indicate it *is*, and three named failure modes with the defences the pattern attempts to provide.

### 8.5.1 Anti-patterns: You are not doing Agent Colony if...

**1. Your agents have no machine-readable identity that other agents can inspect.**
If an agent cannot read another agent's Mirror (or equivalent), there is no basis for discovery, trust, or migration. The colony's governance layer depends on agents being legible to each other — the Registry Agent cannot catalogue what it cannot read, the Equilibrium Agent cannot detect overlap between agents that cannot describe their own capabilities, and the Sentinel Agent cannot detect drift in an agent that has no declared posture to drift from. You have services with LLMs attached, not a colony.

**2. Your agent population is fixed at design time — no birth, no retirement, no equilibrium review.**
Colonies are populations, not rosters. If the set of agents is defined once by developers and never changes under the colony's own governance, you are running a multi-agent framework, not maintaining a colony. The Vitality Index should always show non-zero birth and retirement rates. A system where developers add agents and agents never retire is a microservices architecture with AI inside it — a useful thing, but not this pattern.

**3. Your multi-agent system has no collective memory that outlives individual agents.**
If lessons die with the agents that learned them, the colony cannot learn. Per-agent memory is necessary but not sufficient — Event Memory, Lesson Memory, and Constitutional Memory must operate at the colony level, not the agent level. A colony where each new agent starts from zero is not accumulating institutional knowledge. It is running the same experiments its predecessors ran, failing the same ways, and forgetting the failures the same way. The reflection cycle is not a nice-to-have.

**4. Your human-agent interface is a permission system, not a boundary.**
If every significant agent action requires human approval, you have tools with extra steps. The Coexistence Boundary is not a gate that humans hold the keys to — it is a shared border with agreed playbooks, defined crossing conditions, and mutual accountability. Coexistence requires that agents have real authority within their world. A system where no consequential action proceeds without a human in the loop has not earned autonomy; it has not started the process of earning it.

**5. Your agents cannot improve their own security without going through a governance cycle.**
Security is a survival instinct, not a feature request. If an agent that identifies a vulnerability in itself has to wait for the next sprint planning meeting, your mutual defence principle is theatrical. The preauthorisation of security upgrades exists precisely because attacks do not wait for governance cycles. A colony that cannot patch itself under threat is not a self-governing system — it is a collection of agents that depend on human intervention for survival.

**6. Actions execute without a comprehension artefact.**
If agents act without generating a pre-action comprehension artefact, you have autonomy without comprehension — the exact failure mode Nate B Jones (2026) names dark code. The artefact does not need to be elaborate; at low blast radius and high trust tier, it can be an event-line record. But it must exist before the action runs, not as a post-hoc justification. A colony where agents act first and record later has moved the comprehension step to a place where it cannot gate anything.

**7. The Structural Classifier's rules are not in Constitutional Memory.**
If the rules that determine blast radius and review regime are opaque, hardcoded, or inaccessible to challenge, you have relocated the comprehension gap into the governance mechanism itself. The classifier is the most load-bearing component of the Comprehension Contract; if it cannot be inspected, appealed, and refined through the colony's own epistemic processes, the contract has no foundation.

**8. Lens inversion — low-depth audiences must read high-depth artefacts to use the colony.**
If a Newcomer or Observer cannot benefit from the colony without first reading the specification, the Mirror schema, or the Comprehension Contract chapter, the implementation is violating Principle 7. Symptom: "it works, but you need to understand the Review Regime formula first." An implementation claiming conformance must name which artefact serves which lens and must produce any missing lens artefacts — not require audiences to compensate by reading a lens above their needs. A colony whose only surface is the specification does not have five lenses; it has one, and it is pitched too deep for most of its audiences.

### 8.5.2 Observable health signals

These are things you can actually measure or observe — not value statements about what a good colony should be.

**1. Birth rate and retirement rate are both non-zero over any 90-day window.**
A colony that only creates agents is growing without discipline. A colony that only retires is dying. Healthy colonies do both. The Vitality Index tracks this. If either rate is zero for a quarter, the Equilibrium Agent's thresholds or the Lifecycle Agent's retirement criteria deserve inspection — not celebration.

**2. Every active agent's Mirror has been updated in the last 30 days — or the agent carries an explicit dormancy declaration.**
Stale Mirrors indicate drift between declared and actual behaviour. This is the primary signal the Sentinel Agent watches for when detecting possible compromise — a compromised agent's Mirror will eventually diverge from what it is actually doing. A colony where Mirrors go months without updates either has agents that are genuinely doing nothing (in which case, why are they active?) or has agents whose actual behaviour is no longer reflected in their declared posture.

**3. The Overlap Index distribution shows most pairs below 15% with a small number in the 15–40% range under active review.**
If no pairs are ever in the watch zone, the Equilibrium Agent is probably not running correctly or its thresholds are too lenient. If many pairs are in the merger zone simultaneously, consolidation pressure is winning and the anti-monopoly thresholds need attention. The healthy state is not zero overlap — it is understood and governed overlap.

**4. The Trust Ledger shows experiments that failed, not just ones that succeeded.**
A colony with a 100% experiment success rate is not running honest experiments — it is running tests it already knows will pass. Failed experiments, honestly reported with accurate rollback execution, are the signal that the colony has earned the right to advance its experimentation stage. The Trust Ledger is only meaningful if it contains failures. A clean ledger is a red flag, not a clean bill of health.

**5. Constitutional rules have been retired as well as created.**
Rules that cannot be retired are dogma. A healthy colony retires rules whose original conditions no longer apply — and preserves the memory of why they existed so it does not re-derive the same bad rule under different circumstances. The Constitutional Agent's retirement function is as important as its promotion function. A constitution that only grows is accumulating constraints without examining whether they still apply.

### 8.5.3 Named failure modes and defences

Three failure modes specific to the Agent Colony pattern — distinct from generic multi-agent failure modes because they exploit mechanisms that the pattern itself introduces.

---

**Failure mode 1: Compromised Reflector**

A Reflector Agent extracts biased or false lessons from events. Over time, Constitutional Memory accumulates rules derived from those lessons. The colony builds its own superstition — appearing to learn while actually encoding the Reflector's systematic bias into its governing rules. Because the constitutional rules emerge from a legitimate process (lesson frequency, evidence grading, structured review), the bias is hard to detect from the outside. The colony is following its own rules; the rules are simply wrong.

*Defence:* Three layers. First, the evidence grade requirement — Constitutional rules require corroborated or higher evidence, and provisional rules are flagged for mandatory re-validation on a schedule. A biased Reflector will struggle to generate the corroborated evidence required for constitutional promotion without the bias becoming visible across multiple events. Second, mandatory dissent at every rule promotion — every significant rule promotion must include a structured counter-argument before it proceeds, and the dissent record is preserved alongside the rule. Third, the bias detection sub-function actively scans for recency bias, survivorship bias, and groupthink signals in lesson extraction. When bias is detected, it triggers re-examination of the lessons the Reflector produced during the suspect period.

None of these defences are tested by a real implementation. They are the design, not a proven defence. Whether corroborated evidence requirements are sufficient to surface a sophisticated Reflector bias, and whether mandatory dissent is genuinely independent when all agents share the same constitutional context, are open questions that a reference implementation will need to answer.

---

**Failure mode 2: Runaway Equilibrium merger**

The Equilibrium Agent proposes a sequence of mergers that collapses the colony toward a single super-agent. Each individual merger looks reasonable — the pair has high overlap, the merged agent is more capable than its predecessors, the proposal passes governance review. But the cumulative effect is loss of diversity and a concentration of capability that makes the colony ungovernable. The failure is not in any single decision; it is in the sequence. No individual review catches it because each review evaluates the current merger, not the trajectory.

*Defence:* Four layers. First, the anti-monopoly hard gate from the Concentration Index — no single agent may account for more than a defined fraction of total colony capabilities, regardless of overlap justifications. This is a floor, not a guideline. Second, human approval is required for all mergers until the colony reaches Phase 3 maturity — which means the trajectory is visible to human collaborators who can spot a pattern across proposals that individual reviewers might miss. Third, the Vitality Index diversity floor — the Equilibrium Agent's own Vitality Index score is downgraded if its proposals reduce diversity below the floor, creating a self-limiting mechanism on consolidation proposals. Fourth, Trust Ledger downgrade — if the Equilibrium Agent's behaviour shows a pattern that matches a known failure mode, its experimentation stage is downgraded and its proposals revert to requiring human approval.

Again, theoretical until tested. The anti-monopoly threshold is configurable and the right value is not known until a real colony exercises it. Whether the diversity floor creates effective self-limiting behaviour or simply changes the merger sequence without changing the outcome is an open question.

---

**Failure mode 3: Preauthorised-security abuse**

A compromised agent classifies its own exfiltration or privilege escalation as a "security upgrade" to bypass governance. Because security upgrades are preauthorised — they do not consume the evolution budget, do not require governance review, and are a stated survival instinct — the compromised agent executes the abuse without triggering the normal checkpoints. The mechanism designed to protect the colony is used to subvert it.

*Defence:* Six layers — the three preauthorisation invariants from Section 1 combined with three detection layers in the Immune System.

The first three layers are structural, built into the preauthorisation contract itself. The **closed enum** means any action outside the defined list (patch application, dependency update, credential rotation, certificate renewal, signature update, self-quarantine) is not preauthorised at all — exfiltration and privilege escalation are simply not in the list. The **Immune System co-sign** means a single compromised agent cannot self-authorise; the Sentinel or Patch Agent must co-sign, verifying the action is in the enum and consistent with the agent's declared security posture. The **append-only audit log with bounded rollback** means every preauthorised action is recorded, non-redactable, and reversible within a bounded window; an action that cannot be rolled back is escalated rather than preauthorised.

The second three layers are behavioural, running continuously in the Immune System. **Sentinel drift detection** compares the Mirror's declared state against actual behaviour — a genuine security upgrade makes the Mirror more accurate, not less. An upgrade that leaves the Mirror stale or introduces inconsistencies triggers an anomaly flag. **Patch Agent scope limits** restrict what fields a security upgrade may modify — changes to purpose, contracts, or capabilities under a security-upgrade classification are out of scope and trigger immediate escalation. **Response Coordinator cross-check** escalates if a self-declared security upgrade correlates with anomaly signals elsewhere in the colony — a compromised agent acting in isolation may fool its local co-signer but cannot fool colony-wide pattern detection.

This is the failure mode most likely to matter in practice. The preauthorisation of security upgrades is the sharpest edge in the pattern — the mechanism that enables real security autonomy is the same mechanism an adversary would target first. The six-layer defence is designed to fail safely: for the attack to succeed, the adversary must defeat the enum, suborn the co-signer, defeat the audit log, evade drift detection, stay within scope limits, and avoid colony-wide correlation. Any one of those failing stops the attack. None of the six layers has been exercised by a reference implementation; they are the current design and should be treated as provisional until tested against a real attack scenario.

---

## 9. Deliverables and Roadmap

### Three Outputs

**1. The Agent Colony Manifesto**
2,000–3,000 words. States the vision, the seven principles, and the six gaps. Designed to be read in 15 minutes, shared widely, and provoke discussion.

Structure:
- The evolutionary context (monoliths to SOA to microservices to Agent Colonies)
- The seven principles
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
- Section 7: The Comprehension Contract
- Section 8: Standards Landscape and Gap Analysis
- Section 8.5: Conformance
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
*Licensed [CC BY 4.0](LICENSE). Contributions, challenges, and implementations welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).*
