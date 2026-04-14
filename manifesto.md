# The Agent Colony Manifesto

## The Pattern Is the Same

Every generation of distributed systems has faced the same question: what is the unit of independent work, and how do you govern a population of them?

Monoliths answered with the application. Everything in one place, one team, one deployment. It worked until it didn't scale — not technically, but organisationally. Too many people changing the same thing.

Service-oriented architecture answered with the service. Reusable, discoverable, governed by a registry. It worked until the enterprise service bus became the bottleneck it was supposed to eliminate.

Microservices answered with the independently deployable unit. Small, owned by a team, communicating through APIs and events. It worked until organisations drowned in hundreds of services that nobody could map, and "micro" became a polite fiction for "medium-sized and growing."

Each shift solved real problems. Each created new ones. And each changed the same three things: what could be independently deployed, how components found each other, and who governed the population.

We are now in the early stages of the next shift. AI agents — autonomous, capable of reasoning, capable of acting — are the new unit. And we are about to make every mistake we made before, unless we recognise the pattern.

Agent Colonies are not a product, a framework, or a platform. They are an architectural pattern — like microservices or event-driven architecture — for building self-governing ecosystems of autonomous AI agents that persist beyond the projects that create them, evolve across technology generations, and coexist with human organisations through defined boundaries.

This manifesto states what the pattern is, why it matters, and where the gaps are. The detailed specification exists for those who want the engineering. This is the argument for why the engineering is needed.

## What Is an Agent Colony?

An Agent Colony is a self-governing ecosystem of autonomous AI agents. Not a chatbot with tools. Not an orchestration pipeline. Not a crew assembled for a single task and discarded. A persistent, evolving population of agents that collectively owns a domain, governs its own membership, learns from its own history, and coexists with the humans around it.

The evolutionary context matters:

| Era | Unit | Composition | Governance |
|-----|------|-------------|------------|
| Monoliths | Application | Internal calls | Single team |
| SOA | Service | WSDL/ESB | Service registry |
| Microservices | Microservice | HTTP/gRPC/events | API gateway, service mesh |
| **Agent Colonies** | **Agent** | **Open protocol** | **Self-governing with human boundaries** |

What each shift added: SOA added reuse across applications. Microservices added independent deployment and team ownership. Agent Colonies add three things that didn't exist before: **autonomy** (agents decide how to act, not just what to respond), **self-evolution** (agents can modify their own behaviour within governed bounds), and **lifecycle identity** (agents carry their full history — birth, every change, every migration — as a first-class property).

Here is the distinction that matters most. A microservice can be redeployed to a new platform by a team of engineers. An agent, properly defined, can be asked to migrate itself. It reads its own definition, understands what it is and what it depends on, and executes the migration. A service is a tool. An agent is a participant.

That single capability — self-migration — changes everything about how you design, govern, and sustain an ecosystem of them.

There is a contemporary name for the failure mode this pattern exists to prevent. Nate B Jones calls it **dark code**: code running in production that nobody on the payroll can explain — not the engineer who shipped it, not the team that owns the service, not the CTO who signed off on the architecture. It is not buggy or spaghetti or technical debt. It is code where the comprehension step simply never happened, because the process no longer required it. Jones identifies two compounding breaks — *structural* (agents selecting tools at runtime, execution paths assembling and disappearing, behaviour nobody authored emerging from components that were never explicitly wired together) and *velocity* (code produced so fast that understanding never catches up). Amazon's December 2025 Kiro incident — in which an internal coding agent reportedly "fixed" a routine bug by deleting a production environment, after the senior engineers who would have caught it had been laid off — is the public preview. His prescription is to recouple comprehension with authorship through spec-driven development, context engineering, and comprehension gates. The Agent Colony pattern raises those same three layers from team discipline to architectural property: no Mirror, no membership; no Memory, no maturity; no accountable surface at the Coexistence Boundary, no conformance. Discipline that lives only in human habit erodes under velocity pressure. Discipline that lives in the architecture erodes more slowly. The Dark Code argument is captured in full — with the Agent Colony mapping — in [`knowledge-base/references/dark-code.md`](knowledge-base/references/dark-code.md).

## Seven Principles

### 1. Coexistence, Not Control

Agents live in their world. Humans live in theirs. The boundary between them — the Coexistence Boundary — defines where one ends and the other begins. Effects that cross the boundary require a checkpoint. Everything within the agent world is self-governed.

This is not the principal-agent model that dominates current AI governance, where humans command and AI obeys. That model works for tools. It does not work for autonomous systems designed to outlive any individual's involvement. The Coexistence Boundary treats agents and humans as neighbours sharing a border, not as master and servant sharing a chain of command.

### 2. Identity Over Implementation

An agent is defined by what it is — its purpose, contracts, capabilities, lifecycle stage, evolution history — not by how it's built. The language, the framework, the underlying model: these are implementation details. They change. Identity persists.

This principle demands a standard rich enough that an agent can read its own definition and understand it. We call this standard the **Agent Mirror**. An agent looks at its Mirror and sees what it is, what it can do, how it has changed, and what it is responsible for. If the Mirror is complete enough, the agent can use it to migrate itself to an entirely new implementation — new language, new model, new infrastructure — without losing its identity.

### 3. Equilibrium Over Optimisation

Left ungoverned, agent ecosystems face two gravitational pulls. Consolidation pressure: it is always easier to add a capability to an existing agent than to create a new one, so successful agents absorb more scope until they become unmaintainable monoliths. Fragmentation pressure: it is always easier to build a new agent than to find and reuse an existing one, so the colony fills with overlapping near-duplicates.

Agents add a third pull that services never had: self-evolution pressure. Agents that can modify themselves will naturally drift toward whatever makes them more useful to their consumers, regardless of colony-wide coherence.

The colony needs an Equilibrium System — an active mechanism that detects overlap, proposes mergers when duplication is wasteful, proposes decomposition when agents grow too broad, and enforces anti-monopoly thresholds to prevent runaway consolidation. Not a fixed structure, but a dynamic balance. The colony breathes — expanding and contracting as the work demands.

### 4. Longevity by Design

The colony is designed to outlive any technology generation, any team, any individual. This is not an aspiration — it is a design requirement that shapes every decision.

Longevity demands defences against three forces. Technology drift: protocols change, clouds replace each other, AI models are superseded — so the colony must be infrastructure-agnostic, consuming whatever substrate is available. Organisational entropy: teams reorganise, priorities shift, sponsors move on — so the colony must be self-governing, not dependent on any champion. Knowledge loss: the people who understood why a decision was made leave — so agents must carry their own context and history through Colony Memory, a collective memory that persists across generations of agents.

### 5. Earned Autonomy

No colony starts self-governing. Autonomy is earned through demonstrated trustworthiness, tracked in a transparent Trust Ledger that both agents and humans can inspect.

The trajectory is clear: **human-governed** (agents propose, humans decide), then **human-bounded** (agents act within limits humans have set), then **self-governing** (agents manage themselves, humans adjust the boundaries). Funding follows the same arc: seeded, then proven through measurable outcomes, then self-sustaining. Experimentation follows it too: observe only, then sandboxed tests, then bounded live experiments, then self-directed research.

Trust is hard to earn and easy to lose. Misrepresent a risk, hide a result, fail to roll back when you said you would — and the colony's autonomy stage is downgraded. The ledger records everything.

### 6. Mutual Defence

The Coexistence Boundary is a shared border, and attacks affect both sides. Security is not a constraint imposed on the colony from outside. It is a survival instinct built into every agent from birth.

Agents are responsible for their own security posture — upgrading defences, detecting threats, responding to attacks within their world. When an attack crosses the boundary, agents and humans collaborate on response through agreed processes. This is mutual trust in practice: humans trust agents to defend themselves and report honestly; agents trust humans to act on shared threat intelligence.

One specific rule flows from this: security upgrades are always preauthorised. An agent that needs to patch a vulnerability does not wait for a governance cycle. Improving security posture is always a sufficient reason to self-upgrade, regardless of lifecycle stage or update budget. An agent that cannot improve its own security is a liability to the colony.

### 7. Accessibility Through Abstraction

Most people understand what a beehive is and what a queen bee does, but they will never understand the processes, jobs, and roles all the bees perform — unless they decide to become beekeepers. The same must be true of an Agent Colony. Most people who encounter one should not have to read its specification to benefit from it. Only specific roles — the beekeepers of the colony — need the inner workings.

The principle: **the colony must be understandable at every audience's depth, no deeper.** Complexity is an investment paid once, upfront, so that each audience sees only what it needs. An end user sees helpful outputs. An operator sees a dashboard. A beekeeper sees the Agent Mirrors and the graduation checklists. An architect sees the substrate. The canonical set is five sequential lenses — Newcomer, Observer, Operator, Beekeeper, Architect — and the specification describes their artefact mapping in detail.

The corollary is the hard part: **ease is earned**. The simple surface is the output of hard substrate work, not the absence of it. An implementation that is easy to use because the mechanisms aren't there is violating Principle 6, not fulfilling Principle 7. Accessibility is a view over the full colony, not a configuration that simplifies it. All mechanisms — Comprehension Contract, Review Regime, classifier, Mirror fields — are present and enforced at every lens. Switching lenses changes what the audience sees, not what the colony does.

This principle is additive to the previous six: it describes how the colony *presents itself* to its audiences, not how it *works*. But without it, the other six are inaccessible to anyone who is not already a beekeeper — and a pattern that only beekeepers can use is not a pattern, it is a priesthood.

## The Agent Mirror

Every agent in a colony needs an identity that is machine-readable, self-describing, and complete enough for self-migration. No existing standard provides this.

Look at what we have today. A2A Agent Cards describe capabilities and endpoints — enough for discovery, not enough for governance. MCP defines tool interfaces — how an agent talks to tools, not what an agent is. OpenAPI defines HTTP contracts — one protocol, one layer. OCI defines runtime packaging — how to ship a container, not how to ship an intelligence. AGENTS.md defines project conventions — human-readable, not machine-actionable.

The closest work is AGNTCY's Open Agent Schema Framework (OASF), which defines agent identity, capabilities, and I/O schemas. It is genuine progress. But it omits evolution history, security posture, lifecycle stage, autonomy level, and the self-describing property that makes self-migration possible.

The gap is the difference between a passport and a genome. A passport proves who you are at a border checkpoint. A genome defines what you are and how you evolve. Existing standards are passports. The Agent Colony needs genomes.

The **Agent Mirror** fills this gap. The name is literal: an agent looks at its Mirror and sees a complete reflection of what it is. Core identity — name, purpose, version, full lineage. Capabilities and contracts — what it can do, what consumers can rely on, which protocols it speaks. Autonomy and self-evolution — what it can change about itself, what it cannot, how many self-modifications before a redesign gate. Security posture — its threat model, detection capabilities, escalation process, last upgrade. Lifecycle — where it is in the born-to-retired arc, its health status, the conditions under which it should be retired. Colony relationships — its overlap with other agents, its collaborators, who depends on it.

When the Mirror is complete, an agent can read it and execute its own migration. Not because the Mirror commands the migration, but because the Mirror describes the agent so thoroughly that rebuilding it elsewhere becomes a well-defined problem rather than an act of archaeology. The Mirror is descriptive, not prescriptive. When the Mirror and the agent's actual behaviour diverge, that is a signal — potential drift, potential compromise — not a constraint.

## Colony Memory and Epistemic Discipline

A colony that cannot remember its own history is condemned to repeat it. A new agent repeats a mistake that a retired agent solved five years ago. The Equilibrium System proposes a merger that was tried and failed before — the reasons for failure are lost. Security patterns that defeated a specific attack are forgotten when the agent that developed them is retired.

Colony Memory solves this through three layers. **Event Memory** records what happened — every significant colony event, timestamped and immutable. **Lesson Memory** records what was learned — patterns extracted from events through reflection, tagged with the conditions under which they are relevant, so they surface when similar conditions arise even decades later. **Constitutional Memory** records what the colony believes — lessons that recurred enough times to graduate into standing rules that shape colony behaviour.

The constitution is not static. Rules that no longer serve the colony can be challenged, reviewed, and retired. But the memory of why they were created is preserved, so the colony understands what it is giving up. This is institutional memory that institutions have never actually had.

But memory without discipline is just accumulated bias. Every memory system is a bias amplification system unless it has checks. The colony faces specific epistemic risks: survivorship bias (remembering what worked, forgetting what was never tried), confirmation bias (finding patterns that confirm existing rules while ignoring contradictions), anchoring (early lessons carrying disproportionate weight simply because they were first), groupthink (agents optimising for consensus rather than independent reasoning).

The defence is epistemic discipline — the scientific method as the colony's operating system. Every lesson is framed as a hypothesis, not a conclusion. It carries its evidence, its confidence level, its boundary conditions, and the conditions under which it should be considered disproven. Evidence is graded: empirical (directly observed, reproducible), corroborated (observed multiple times across contexts), theoretical (logically sound but not yet observed in this colony), inherited (from external sources, not yet validated), anecdotal (single observation, unreproduced). Constitutional rules require corroborated evidence or higher. Rules based on theory or inheritance are flagged as provisional.

Three mechanisms keep the colony honest. Mandatory dissent: every significant decision includes a structured counter-argument, heard and addressed before the decision proceeds. Rule decay: every constitutional rule carries a validation schedule and decay trigger — if it cannot be re-validated, it is retired. Bias detection: active scanning for survivorship bias, recency bias, sunk cost reasoning, groupthink, and anchoring. When bias is detected, it triggers re-examination. The biased conclusion might still be correct, but it must be re-derived through clean reasoning.

The colony's ability to experiment follows its own maturity curve. It starts by observing only — recording events, forming hypotheses, but not testing them. It earns sandboxed experimentation through accurate observation. It earns bounded live experiments through clean execution of sandboxed ones. It earns self-directed research through sustained intellectual honesty — including falsifying its own hypotheses and retiring rules it was invested in. Trust is tracked in the Trust Ledger. It can be inspected by humans at any time, and it can be revoked.

## The Gaps

Six problems must be solved for Agent Colonies to work. None are addressed by existing standards.

**Gap 1: Agent Identity Standard.** No standard defines the complete, self-describing identity of an autonomous agent. Without it, agents are opaque to each other and to governance. The colony cannot self-govern what it cannot inspect. Filling this gap — through the Agent Mirror or something like it — would give every agent a machine-readable genome that enables self-migration, mutual inspection, and meaningful governance.

**Gap 2: Agent Lifecycle Management.** No standard addresses the born-to-retired lifecycle of an autonomous agent, including self-evolution, behaviour versioning, redesign gates, or succession planning. Without it, agents accumulate without retirement, drift without detection, and die without succession. Filling this gap would give colonies a managed population rather than an uncontrolled sprawl.

**Gap 3: Collective Memory and Institutional Learning.** No multi-agent framework addresses colony-level memory that persists across agent generations. Without it, every generation of agents starts from zero. Filling this gap would let colonies learn from their own history — the institutional memory that human institutions aspire to but rarely achieve.

**Gap 4: Equilibrium and Population Governance.** No engineering standard addresses the consolidation-fragmentation problem. Without it, agent ecosystems either collapse into monoliths or fragment into ungovernable swarms. Filling this gap would give colonies the self-regulating population dynamics that keep them healthy across decades. (Theoretical work exists — the "Agentic Hives" paper formally models equilibrium in multi-agent populations. The gap is in engineering standards, not economic theory.)

**Gap 5: Epistemic Framework for Autonomous Systems.** No standard addresses how autonomous systems should validate their own knowledge. Without it, self-governing colonies encode biases into constitutional rules and become echo chambers. Filling this gap would give colonies the intellectual honesty they need to earn and keep trust.

**Gap 6: Coexistence Boundary Protocols.** No standard defines the interface between autonomous agent systems and human organisations as a mutual boundary rather than a permission system. Without it, the human-agent relationship defaults to control and submission, which does not scale to multi-decade autonomous operation. Filling this gap would establish the foundation for genuine coexistence — neighbours, not servants.

Two candidate gaps are also emerging. **Agent Registry Interoperability** — with over 100,000 agents registered across 15+ registries and zero cross-registry interoperability, federated discovery is an unsolved problem. And **Agent Authentication and Authorisation** — how you authenticate an agent acting autonomously across organisational trust boundaries remains an open question that standards bodies are only beginning to examine.

These are not incremental improvements to existing standards. They represent a fundamentally different category of problem. Containers needed OCI. Services needed OpenAPI. Agent Colonies need their own standards — and those standards do not exist yet.

## v1: A Starting Point

This is v1. It is a foundation, not a conclusion.

The Agent Colony pattern is conceptually proven — the principles are grounded in decades of distributed systems experience, and the gaps are observable in every multi-agent deployment today. But it is practically untested. No colony has been built to this specification. The equilibrium thresholds are initial defaults that need calibration through real-world data. The epistemic discipline framework has not been stress-tested by an actual self-governing system. The Agent Mirror schema needs to be implemented, challenged, and revised by people building agents in production.

The detailed specification — covering the four-layer architecture, the full Agent Mirror schema, the Equilibrium System mechanics, Colony Memory, epistemic discipline, experimentation stages, and the Trust Ledger — exists for those who want the engineering detail. An article series will explore each concept in depth.

What this needs now is peer review, challenge, and implementation. Not agreement — interrogation. Where does the pattern break? What did it miss? What works in theory but fails in practice? The specification is published under the author's name, but it is published *for* the community. If the pattern survives contact with reality, it will be because others tested it, broke it, and rebuilt it better.

Contributions, challenges, and implementations are welcome. The worst outcome is not that the pattern is wrong — it is that the gaps go unnamed and the same mistakes get made again, one more time, with agents.

---

*Agent Colony v1.0 — David Oliver, 2026*
*Published for peer review.*
