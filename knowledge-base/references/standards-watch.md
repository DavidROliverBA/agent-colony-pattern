# Standards watch

Active standards efforts to track. The state of play changes quickly; this file is a snapshot at the last update date with a note on what to watch for.

**Last updated:** 2026-04-13

---

## Google A2A (Agent-to-Agent Protocol)

**Status:** v0.3 stable, draft v1.0 in public review. 150+ partner organisations including Atlassian, SAP, Salesforce, Workday.

**What it covers:** Agent-to-agent communication, task lifecycle (initiated, active, completed, failed), Agent Cards for discovery, authentication.

**What to watch for:**
- The v1.0 release and whether the Agent Card schema expands beyond capabilities and endpoints.
- Whether A2A adopts or interoperates with AGNTCY's OASF (there is some overlap between A2A Agent Cards and OASF agent identity schemas).
- Whether the Agent Card schema ever grows to cover lifecycle states, evolution history, or security posture — if it does, the Agent Mirror becomes an extension rather than a parallel effort.

**Relationship to Agent Colony:** Complementary, not competing. A2A handles the communication surface; the Agent Mirror handles the identity surface. The Colony's `protocols` field in the Mirror explicitly includes A2A as a supported communication protocol.

---

## MCP (Model Context Protocol)

**Status:** v2025-11-25. Donated to Linux Foundation Agentic AI Foundation (AAIF) in December 2025. Founded by Anthropic, OpenAI, Block.

**What it covers:** Tool and resource interfaces between agents and the tools they use. The November 2025 spec added Tasks (tracking long-running work on servers), server-side agent loops, and parallel tool calls.

**What to watch for:**
- The next MCP spec revision and whether it expands from agent-to-tool to agent-to-agent (there is pressure from the community for this, and A2A's existence creates tension).
- AAIF governance decisions about MCP's scope boundaries.
- Any MCP extension that introduces agent identity concerns — if that happens, the Agent Mirror needs to align with it or explicitly position against it.

**Relationship to Agent Colony:** Complementary. MCP handles the agent-to-tool surface; the Agent Mirror handles agent identity. The Colony's `protocols` field includes MCP.

---

## AGNTCY / OASF (Open Agent Schema Framework)

**Status:** Active 2025–2026. Open-source collective led by Cisco Outshift with LangChain, Galileo, LlamaIndex, and others.

**What it covers:**
- **OASF** — schema for agent identity, capabilities, I/O, performance characteristics. The closest existing work to the Agent Mirror.
- **Agent Connect Protocol (ACP)** — agent-to-agent messaging layer.
- **SLIM** — secure low-latency inter-agent communication.
- **Agent Directory** — federated agent discovery.

**What to watch for:**
- OASF schema evolution. If OASF adds evolution history, security posture, or lifecycle stage fields, the Agent Mirror's distinctiveness shrinks. This would be a good outcome — it would mean the standards community is converging on the right concerns.
- Whether AGNTCY positions OASF as complementary to A2A or as an alternative.
- Whether AGNTCY adopts a validator or a reference implementation — if they do, the Agent Mirror should interop with their validator where possible.

**Relationship to Agent Colony:** This is the **primary** standards relationship to manage. OASF is the closest existing work to the Agent Mirror, and the pattern's most honest positioning is as an *extension profile* of OASF rather than a competing schema. The v1.3 or v2.0 roadmap should include concrete engagement with AGNTCY — a PR proposing the Agent Mirror's additions as an extension, or a fork-and-revise with clear attribution.

---

## NIST Agent Standards Initiative

**Status:** Launched February 2026 via CAISI (Center for AI Safety Institute). Supplementary work to the existing NIST AI Risk Management Framework.

**What it covers:**
- **COSAiS overlays** for SP 800-53 covering single-agent and multi-agent deployments. Drafts expected throughout 2026.
- **NCCoE concept paper** (February 2026) on agent identity and authorisation.
- Broader agent-specific guidance planned as supplements to the NIST AI RMF.

**What to watch for:**
- The first public draft of the COSAiS overlays. This is where the US government's position on agent security will start to crystallise.
- Whether the NCCoE identity concept paper adopts or references OASF, AGENTS.md, or A2A Agent Cards.
- Any NIST engagement with the Coexistence Boundary concept (unlikely directly, but the agent authorisation concerns are adjacent).

**Relationship to Agent Colony:** NIST is not going to adopt the Colony pattern directly, but the Conformance section of the spec (§7.5) is structured to answer the kind of questions NIST guidance raises: what are the health signals, what are the failure modes, what are the anti-patterns. Aligning with NIST vocabulary where possible will help the pattern land with US government audiences.

---

## AGENTS.md

**Status:** Released by OpenAI August 2025. Adopted by 60,000+ projects. Contributed to Linux Foundation AAIF in December 2025.

**What it covers:** Cross-tool conventions for AI coding agents — a human-readable markdown file that describes a project's conventions, constraints, and context for agents working on the project.

**What to watch for:**
- Whether AGENTS.md evolves a machine-readable extension. It currently is not — the Colony could propose the Agent Mirror as the machine-readable complement.
- AAIF governance decisions about the file's scope. If it stays narrowly about coding agents, the Agent Mirror is in a different space. If it broadens to cover general agent identity, there is a potential alignment or conflict.

**Relationship to Agent Colony:** Different layer. AGENTS.md is project-level context for humans and agents; the Agent Mirror is agent-level identity for the agent itself and for other agents to inspect. They coexist without overlapping directly.

---

## IEEE P3119

**Status:** Draft, slow-moving.

**What it covers:** AI and automated decision system procurement by government entities. Narrower than its name suggests.

**What to watch for:** Not much. This is on the watchlist mainly to prevent misreading — the project name sounds like it might cover broader AI ethics and governance, but it does not.

**Relationship to Agent Colony:** Limited direct relationship. Relevant only if the Colony pattern is ever adopted in a government procurement context.

---

## ISO/IEC 42001 family

**Status:**
- **ISO/IEC 42001** — AI management systems. Published 2023.
- **ISO/IEC 42005:2025** — AI system impact assessment.
- **ISO/IEC 42006** — AIMS audit and certification.
- **ISO/IEC TS 22440** — AI in safety-critical systems.

**What it covers:** Organisational-level governance for AI systems — management processes, risk assessment, audit frameworks.

**What to watch for:** Whether any of these extend to cover autonomous multi-agent systems specifically. Currently they operate at a higher level than the Agent Colony concerns.

**Relationship to Agent Colony:** The Colony's governance layer is compatible with ISO/IEC 42001 management processes — a colony deployed in an ISO/IEC 42001-compliant organisation could plug into the organisation's existing AI governance framework via the Coexistence Boundary. This is a potential integration story rather than a conflict.

---

## Emerging — watch list without firm standards yet

- **Agent registry interoperability** — Q1 2026 data shows 104,000+ agents registered across 15+ registries with zero cross-registry interoperability. This is the Candidate Gap 7 in the thesis. Expect a standards effort to emerge in 2026–2027 to address it.
- **Agent authentication and authorisation** — NIST NCCoE has flagged this as unresolved (February 2026). Expect formal work in this space throughout 2026.
- **OpenTelemetry GenAI semantic conventions** — active SIG, expanding through 2026. Could become the observability substrate for any colony implementation.
- **TOSCA 2.0 (OASIS)** — published September 2025 as a full OASIS standard. Topology and lifecycle management for cloud services. Thin overlap with the Colony's Substrate layer (L4).

---

## How to update this file

Bump the "Last updated" date at the top. Add new entries as standards emerge or existing ones shift state. Remove or archive entries only when a standard is formally withdrawn or superseded (note the reason).

The purpose of this file is not to be encyclopedic — it is to capture the standards landscape that matters for the Colony pattern's positioning. If an entry has not been touched in 12 months and nothing has changed, it probably should not be here.
