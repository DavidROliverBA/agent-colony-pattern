# The Agent Colony

> A pattern language for self-governing AI agent ecosystems

The Agent Colony is an architectural pattern for building self-governing ecosystems of autonomous AI agents that persist beyond the projects that create them, evolve across technology generations, and coexist with human organisations through defined boundaries. It is not a framework, a platform, or a product — it is a pattern, like microservices or event-driven architecture, that can be implemented in any technology, on any infrastructure, by any organisation.

> 📖 **New here? Start with the lay-audience article:** [*It takes a village — the Agent Colony definition*](https://medium.com/@davidroliver/it-takes-a-village-the-agent-colony-definition-32b9bd714bb8) on Medium (16 min read). It explains the pattern using the metaphor of a village, with no jargon. The text is also preserved in [`knowledge-base/writings/`](knowledge-base/writings/2026-04-12-it-takes-a-village.md).

Current version: **v1.8.0** · [What's new](CHANGELOG.md) · [Latest release](https://github.com/DavidROliverBA/agent-colony-pattern/releases/latest)

## What's in this repository

| Document | Purpose |
|----------|---------|
| **[Manifesto](manifesto.md)** | Short, opinionated, shareable. The core argument in 15 minutes. |
| **[Thesis Paper](thesis.md)** | The full academic-lite treatment with literature review against 12 existing standards, formal gap analysis, six diagrams, and scales of application. Cite this for peer review. |
| **[Specification](specification.md)** | The detailed technical reference. Four-layer architecture, Agent Mirror schema, colony dynamics, maturity model, conformance section with anti-patterns and failure modes. |
| **[Schema](schemas/)** | `agent-mirror-v0.2.0.json` — JSON Schema (draft 2020-12) formalising the Agent Mirror identity standard. v0.2.0 adds Comprehension Contract, NFRs, Valuation, and critical path fields. `agent-mirror-v0.1.json` kept for reference. |
| **[Examples](examples/)** | `hello-colony` — a worked 5-agent example with pre/post-evolution pair. `hello-colony-runtime` — deterministic Python simulation of four colony events (no LLM calls). `equilibrium-playground` — browser visualisation of the Equilibrium System (no build step). [`teaching-colony`](examples/teaching_colony/) — a six-agent substrate-portable colony that teaches the pattern, with Claude Code and Managed Agents substrates (v1.6.0). Plus [`demonstration-options.md`](examples/demonstration-options.md) — a design memo of ten options for building a visual demonstration of the pattern. |
| **[Diagrams](diagrams/)** | Six SVG diagrams (render inline on GitHub) plus the Excalidraw source files. See [`diagrams/README.md`](diagrams/README.md) for the shared colour palette and style conventions. |
| **[Knowledge Base](knowledge-base/)** | Feedback received (good and bad), lessons extracted, prior art, standards watch. The pattern's own evolution, captured as it happens. |

## Scope and audiences

This repository has four distinct audiences. Read the document that fits your need:

- **If you are not a technical reader** — read [*It takes a village — the Agent Colony definition*](https://medium.com/@davidroliver/it-takes-a-village-the-agent-colony-definition-32b9bd714bb8) on Medium. 16 minutes. No jargon, uses a village as the running metaphor, written for someone wise about life but not about brackets and code.
- **If you want the argument** — read [`manifesto.md`](manifesto.md). 15 minutes. Opinionated, shareable, practitioner voice.
- **If you want the evidence** — read [`thesis.md`](thesis.md). Literature review, gap analysis, diagrams. This is the version to cite.
- **If you want to build it** — read [`specification.md`](specification.md), then [`schemas/agent-mirror-v0.2.0.json`](schemas/agent-mirror-v0.2.0.json), then [`examples/hello-colony/`](examples/hello-colony/). In that order. Run `python examples/hello-colony-runtime/runtime.py` to see the pattern execute as code.

If you only have ten minutes: open `examples/hello-colony/colony-snapshot.yaml` and skim `registry-agent.v1.1.yaml`. The example was made to answer "what does this actually look like on disk?" in one pass.

## The argument in one paragraph

Every paradigm shift in distributed systems has changed the unit of independent work and the way populations of those units are governed. Monoliths, SOA, microservices — each answered the question differently. AI agents are the next answer, but agents add three things that did not exist before: autonomy, self-evolution, and lifecycle identity. Building agent ecosystems with the patterns we used for services will repeat every mistake we made before, plus new ones we have not seen yet. The Agent Colony is a pattern language for doing it differently.

## The seven principles

1. **Coexistence, not control** — agents and humans share a border, not a chain of command
2. **Identity over implementation** — what an agent *is* matters more than how it is built
3. **Equilibrium over optimisation** — the colony self-regulates between consolidation and fragmentation
4. **Longevity by design** — the colony outlives any technology generation
5. **Earned autonomy** — self-governance is earned through demonstrated trustworthiness
6. **Mutual defence** — security is collaborative, not imposed
7. **Accessibility through abstraction** — the colony is understandable at every audience's depth, no deeper

Principle 6 has a corollary: **security upgrades are preauthorised** — an agent improving its own security does not wait for a governance cycle. v1.1.1 strengthened this with three invariants (closed action enum, Immune System co-sign, append-only audit log with bounded rollback). See the specification for the full contract and `registry-agent.v1.1.yaml` for a worked example showing the fields on disk.

Principle 7 has a corollary: **ease is earned** — the simple surface is the output of hard substrate work, not the absence of it. v1.5.0 introduced the audience-lens model as the canonical realisation: five sequential lenses (Newcomer → Observer → Operator → Beekeeper → Architect), each served by a specific artefact, over the same full colony. Lenses are a view, not a configuration. All mechanisms are present and enforced at every lens.

## Scales of application

The pattern is scale-adaptive. A 5-agent team, a 50-agent organisational estate, and a 5,000-agent cross-organisation ecosystem all apply the same principles but realise them with different mechanisms. A small colony running YAML Mirrors in git with weekly human-led equilibrium reviews is not immature relative to a large colony running federated cryptographic attestations — it is **correctly scaled**. Over-engineering a small colony is as much a pattern violation as under-engineering a large one. One exception: security mechanisms do not dial down with scale. The preauthorisation contract is the same at every size.

See the Scales of Application table in [`specification.md`](specification.md) (Section 1) for the full tier comparison.

## The six gaps

Six problems must be solved for Agent Colonies to work. None are addressed by existing standards:

1. **Agent Identity Standard** — no standard defines the complete, self-describing identity of an autonomous agent (the [Agent Mirror schema](schemas/agent-mirror-v0.2.0.json) is this repo's proposal)
2. **Agent Lifecycle Management** — no standard addresses the born-to-retired lifecycle of an autonomous agent
3. **Collective Memory and Institutional Learning** — no framework addresses colony-level memory that persists across agent generations
4. **Equilibrium and Population Governance** — no engineering standard addresses the consolidation/fragmentation problem
5. **Epistemic Framework for Autonomous Systems** — no standard addresses how autonomous systems should validate their own knowledge
6. **Coexistence Boundary Protocols** — no standard defines the human-agent interface as a mutual boundary rather than a permission system

Two candidate gaps (agent registry interoperability and agent authentication/authorisation) are discussed in the thesis paper.

See the [thesis paper](thesis.md) for the full analysis and the literature review backing each claim.

## Status

**v1.8.0** — First release where the Teaching Colony runs on real Claude. Adds an interactive REPL ([`examples/teaching_colony/chat.py`](examples/teaching_colony/chat.py)) with an `ask` command that dispatches the Teacher agent to a real Claude Sonnet call and returns a live answer grounded in the seeded beekeeping primer. Fills in the Claude Code substrate's live-mode `dispatch_agent` path with Anthropic prompt caching (repeat dispatches of the same agent pay ~10% of the system-prompt cost), model tiering (Sonnet for Teacher/Librarian, Haiku for the four supervisory agents), and prose-vs-JSON prompt discipline. Introduces a session token budget (`TEACHING_COLONY_TOKEN_BUDGET`, default 500,000) with an 80% warning and a 100% hard stop. **This is the first release of the pattern that costs money to use** — roughly $2-5 for a full default-budget session with the recommended model mix. Research walks and capability graduation are deferred to v1.9+. v1.7.0's scripted mock-mode walkthrough remains as the free mechanism-demo smoke test. 72 mock-mode tests passing, 3 live-mode tests gated behind `pytest -m live` + `ANTHROPIC_API_KEY`, 2 xfails unchanged from v1.7 (live-mode Managed Agents). The pattern is still **practically untested at production scale** — v1.8 is the foundation for v2.0 but not the reference implementation itself.

**Roadmap:**

| Version | Status | Focus |
|---------|--------|-------|
| v1.0.0 | ✅ released 2026-04-11 | Manifesto, thesis, specification, 6 Excalidraw diagrams |
| v1.1.0 | ✅ released 2026-04-13 | SVG diagrams, JSON Schema, hello-colony example, conformance section, repo hygiene |
| v1.1.1 | ✅ released 2026-04-13 | Scales of Application table, strengthened security preauthorisation with three invariants |
| v1.1.2 | ✅ released 2026-04-13 | Hello-colony reflects the v1.1.1 preauthorisation contract; Trust Ledger framing fixed |
| v1.2.0 | ✅ released 2026-04-13 | Knowledge base — feedback, lessons, prior art, standards watch |
| v1.2.1 | ✅ released 2026-04-13 | First published article; writings subfolder in knowledge base |
| v1.2.2 | ✅ released 2026-04-13 | Dark code reference (Jones 2026); IndyDevDan six ideas + §7.14 False Comprehension Artefacts |
| v1.3.0 | ✅ released 2026-04-13 | Comprehension Contract Mirror fields; schema v0.2.0; graduation checklist; live runtime; equilibrium playground |
| v1.4.0 | ✅ released 2026-04-13 | Comprehension Contract formalised as §7 of specification; review regime formula; 14 sub-sections; two new conformance anti-patterns |
| v1.5.0 | ✅ released 2026-04-14 | Principle 7 Accessibility Through Abstraction; audience-lens model; lens-traversal diagram; lens-inversion anti-pattern |
| v1.6.0 | ✅ released 2026-04-14 | Teaching Colony — first substrate-portable example; first exercise of Comprehension Contract in running code; Claude Code + Managed Agents substrates |
| v1.6.1 | ✅ released 2026-04-14 | Teaching Colony docs — design spec + implementation plan exposed in public repo; three-scenario walkthrough in the README |
| v1.7.0 | ✅ released 2026-04-14 | Honest Teaching Colony — six fixes from external review (mock dispatch, change DSL, §7 enforcement, event ownership, Mirror overlay, classifier gate); new end-to-end walkthrough test |
| v1.8.0 | ✅ released 2026-04-14 | Teaching Colony runs on real Claude — interactive REPL, live-mode dispatch, prompt caching, model tiering, session budget; first release that costs money to use |
| v1.9.0 | planned | Research walks — `fetch_url` tool with hop budget, `research` command, background concurrent walks, G3 graduation |
| v2.0.0 | planned | Full interactive Teaching Colony — remaining commands, session persistence, cost enforcement, v2 reference implementation |
| v2.1+ | planned | Live-mode Managed Agents substrate completion; Newcomer/Observer companion diagrams; peer feedback incorporation |
| v3.0 | planned | Standards engagement — A2A, AAIF, NIST, AGNTCY |

## Contributing

Contributions, challenges, and reference implementations are welcome. This is published *for* the community, not just *by* an author. The worst outcome is not that the pattern is wrong — it is that the gaps go unnamed and the same mistakes get made again, one more time, with agents.

Three ways in:

- **Challenge the argument** — open an [issue](https://github.com/DavidROliverBA/agent-colony-pattern/issues/new/choose) using the Challenge template. Cite the section, state your claim, give your evidence (with grade: empirical, corroborated, theoretical, inherited, anecdotal).
- **Propose refinements** — open a pull request or a Refinement issue. Say what you would change, why, and what other sections it affects.
- **Build a reference implementation** — link your work and it will be added to the roadmap.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide, including how the paper's own epistemic principles (evidence grades, mandatory dissent, honest limitations) apply to its development.

## Citation

If you reference this work, please cite:

> Oliver, D. (2026). *The Agent Colony: A Pattern Language for Self-Governing AI Agent Ecosystems* (v1.8.0). https://github.com/DavidROliverBA/agent-colony-pattern

Machine-readable citation metadata is in [`CITATION.cff`](CITATION.cff).

## License

[CC BY 4.0](LICENSE) — you may share and adapt this work for any purpose, including commercially, provided you give appropriate credit.

---

*The Agent Colony — David Oliver, 2026*
