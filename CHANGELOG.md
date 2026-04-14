# Changelog

All notable changes to the Agent Colony Pattern are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Version numbers follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.1] — 2026-04-14

### Added
- **`examples/teaching_colony/docs/design-spec.md`** — copy of the working design spec from the author's vault, now committed in the public repo so readers have the Architect-lens view of the example. Includes provenance header.
- **`examples/teaching_colony/docs/implementation-plan.md`** — copy of the implementation plan that produced v1.6.0, including the five-sub-agent parallel execution strategy, write-scope boundaries, and coordination rules.
- **`examples/teaching_colony/README.md`** — a complete "How to use this example" walkthrough with three progressive run scenarios: (1) first run on Claude Code to see the full lifecycle; (2) reset and re-run to verify determinism; (3) run on Managed Agents to see the portability claim concretely. Each scenario states what to run, what to expect, where to look, and how to verify. The walkthrough is honest about the event-count difference between substrates (Claude Code ~42, Managed Agents ~22) and points at `gaps.md` for the known reason.

### Changed
- `examples/teaching_colony/README.md` — replaced the thin "How to run" section with the three-scenario walkthrough, replaced the broken vault-path links to spec/plan with links to the newly-committed copies under `docs/`, and fixed the `substrates/claude-code/` → `substrates/claude_code/` link (and similarly for managed_agents).
- `examples/teaching_colony/substrates/claude_code/README.md` — added a "Design context" line pointing at the design spec and implementation plan under `../../docs/`.
- `examples/teaching_colony/substrates/managed_agents/README.md` — same.
- `README.md` at repo root — version badge v1.6.0 → v1.6.1.
- `CITATION.cff` — version v1.6.1.

### Why

Two things were missing from v1.6.0 that a first-time reader would immediately notice. First, the Architect-lens artefacts — the design spec and the implementation plan — lived only in the author's private vault. The example claimed to serve all five lenses but the Architect lens was a broken link. Copying both documents into `examples/teaching_colony/docs/` closes that gap. Second, the top-level README had the commands but not a walkthrough — a reader had no guided way to actually *use* the example, see what it produces, and check that the graduation actually happened. The three-scenario walkthrough gives a clean path: first run to see the lifecycle, second run to verify determinism, third run to see portability concretely. This is a docs-only patch; no code changes.

### No code changes

- Adapters unchanged
- Colony definition unchanged
- Tests unchanged (26 passed, 2 skipped, 4 xfailed — identical to v1.6.0)
- No version bump to any dependency

---

## [1.6.0] — 2026-04-14

### Added
- **`examples/teaching_colony/`** — a six-agent substrate-portable Agent Colony that teaches the Agent Colony pattern, using beekeeping as the running pedagogical example. Six agents (Registry, Chronicler, Equilibrium, Sentinel, Librarian, Teacher), a colony knowledge base, a structural classifier, a graduation checklist generator, and a CLI lifecycle driver (`run.py`).
- **`examples/teaching_colony/contract.py`** — `SubstrateContract` ABC defining the eight operations L4 owes L1–L3: `dispatch_agent`, `read_mirror`, `update_mirror`, `record_event`, `read_kb`, `write_kb`, `co_sign`, `classify_action`. This is the first time the substrate contract is formalised in code.
- **`examples/teaching_colony/substrates/claude_code/`** — Claude Code substrate adapter, working in mock mode. Implements all eight contract operations with deep-merge-and-hash mirror updates, JSONL event logging, and a deterministic mock dispatcher. Unit tests plus a full lifecycle test.
- **`examples/teaching_colony/substrates/managed_agents/`** — Managed Agents API substrate adapter scaffolding. Mock-mode dispatch, co-sign, classify and event-log writes are working; live-mode operations are gated behind `NotImplementedError` pending v1.7+. Includes `api-research.md` — the first honest adequacy report of a real substrate against the Agent Colony contract.
- **First running exercise of the Comprehension Contract (§7)** — Librarian detects KB coverage crossing a threshold, proposes Teacher acquire a new capability, the structural classifier fires with the trust-tier × blast-radius review regime, Sentinel co-signs, Teacher's Mirror is updated with an append-only audit trail including pre/post state hashes. Until v1.6.0 §7 had only ever been described on paper.
- **`examples/teaching_colony/tests/test_portability.py`** — cross-substrate portability test. Asserts (unconditionally) that classifier output is substrate-independent; that Claude Code completes the minimal lifecycle end to end in mock mode; and that Managed Agents completes every mock-implemented operation. Full event-sequence and Teacher-Mirror parity tests are skipped in v1.6.0 with a reason pointing at `gaps.md` — live-mode parity is v1.7+.
- **Lens-mapped READMEs** at `examples/teaching_colony/`, each substrate subdirectory, and the repository-level `examples/README.md` — every level names its audience lens (Beekeeper) and the Principle 7 framing.

### Changed
- **`examples/README.md`** — added teaching-colony to the lens map and the example list; Beekeeper row now points to hello-colony → hello-colony-runtime → teaching-colony.
- **`README.md`** — version v1.5.0 → v1.6.0; Examples row updated to mention teaching-colony; Status section rewritten for v1.6.0; roadmap entry added for v1.6.0; v1.6+ renamed v1.7+; citation line updated.
- **`CITATION.cff`** — version v1.6.0, date 2026-04-14.

### Why

Principle 2 (*Identity over implementation*) and Principle 4 (*Longevity by design*) were paper claims until v1.6.0. The teaching colony demonstrates both in running code for the first time: the *same* colony, with the *same* six Agent Mirrors and the *same* structural classifier, runs behind two substrate contracts that differ in almost every implementation detail. The Comprehension Contract (§7) had been fully specified in v1.4.0 but had never done real work — v1.6.0 shows the classifier firing, the co-sign being issued, and the append-only audit trail being written as a graduation actually happens. The teaching mission is Principle 7 (*Accessibility through abstraction*) in action: the colony's purpose is to help other people learn the pattern, and the beekeeping metaphor serves as the running pedagogical example throughout the lifecycle — a worker Librarian foraging the KB corpus, a Sentinel guarding the hive entrance, a queen-less colony that decides together. Beekeeping is the metaphor the Newcomer can hold; the substrate contract is what the Architect argues about; the same colony serves both lenses.

### Known gap

The Managed Agents substrate adapter ships with mock-mode fully working — dispatch, co-sign, classify, read/write of the local event log — and all live-mode operations gated behind `NotImplementedError`. The mock `update_mirror` returns a zeroed `AuditEntry` without persisting the change, and the mock `write_kb` is a no-op. Consequently the portability parity tests for full event-sequence equality and Teacher-Mirror final-state equality are *skipped* in v1.6.0 with a reason pointing at [`examples/teaching_colony/substrates/managed_agents/gaps.md`](examples/teaching_colony/substrates/managed_agents/gaps.md) — the honest adequacy report documenting which contract operations the Managed Agents API can and cannot support. Live-mode completion is targeted for v1.7+.

---

## [1.5.0] — 2026-04-14

### Added
- **Principle 7 — Accessibility through abstraction** added to the core set in `manifesto.md`, `thesis.md` §3, `specification.md` §1, and `README.md`. The principle states that the colony must be understandable at every audience's depth, no deeper; complexity is an investment paid once upfront so that each audience sees only what it needs. Corollary: *ease is earned* — the simple surface is the output of hard substrate work, not the absence of it.
- **`specification.md` §1 — Audience Lenses** — new subsection of §1 Definition and Core Principles, parallel in shape to Scales of Application. Defines the canonical realisation of Principle 7 as a five-lens model: Newcomer → Observer → Operator → Beekeeper → Architect. Each lens has a canonical artefact in this repository. Lenses are a *view* over the full colony, not a *configuration* that simplifies it — all mechanisms are present and enforced at every lens. Sequential by default with re-entry always possible; pacing can compress; artefact mapping is required for conformance; lenses can be collapsed or split per context.
- **`specification.md` §8.5.1** — one new conformance anti-pattern: **lens inversion** (forcing low-depth audiences to read high-depth artefacts to use the colony at all).
- **`diagrams/lens-traversal.svg`** — new diagram visually representing the five sequential lenses, their canonical artefacts, and the re-entry arrow from any lens back to Newcomer.

### Changed
- **`README.md`** — six principles → seven; version badge v1.4.0 → v1.5.0; roadmap entry added for v1.5.0; status section rewritten; citation line updated.
- **`CITATION.cff`** — version v1.5.0, date 2026-04-14.
- **`manifesto.md`** — "Six Principles" heading → "Seven Principles"; new Principle 7 section added with the beekeeper framing and the ease-is-earned corollary.
- **`thesis.md`** — "Six Principles" heading → "Seven Principles"; new Principle 7 subsection added to §3.

### Why

Principle 7 formalises what the pattern had always been doing implicitly. The repository already has artefacts pitched at different depths — the village article on Medium, the equilibrium playground, the hello-colony-runtime, the specification, the thesis — but until v1.5.0 this stratification was ad-hoc. Naming the lenses makes it explicit, testable, and conformance-relevant. The beekeeper analogy captures the correct disposition: most people understand what a beehive is and what the queen bee does, but will never understand the processes, jobs, and roles all the bees perform unless they become beekeepers. Most audiences for an Agent Colony need a metaphor and an outcome, not a mechanism. Forcing them to read the specification to benefit from the pattern was a violation of a principle that had not yet been named.

### Known gap

The existing six mechanism diagrams (four-layer architecture, equilibrium system, maturity model, agent mirror, memory cycle, evolutionary context) are pitched at the Beekeeper/Architect level. By Principle 7's own test, the Newcomer and Observer lenses are under-served in diagram form — they would need companion "village-level" visual explanations that do not yet exist. This is deferred to v1.6+ rather than shipping v1.5.0 pretending the existing diagrams already serve all five lenses.

---

## [1.4.0] — 2026-04-13

### Added
- **`specification.md` §7 — The Comprehension Contract** — new first-class mechanism formalising the requirement that no action executes without a comprehension artefact matching the agent's trust tier and blast radius. Fourteen sub-sections covering: the dark code problem (Jones 2026), the contract invariant, three timescales of comprehension (Structural Classifier, quarantine/composed actions, audit/Lesson Memory feedback), the review regime formula with trust-tier × blast-radius table, three load-bearing properties, the classifier as Constitutional, honest limits (delayed-consequence residual), Agent Mirror changes (v0.2.0 fields), relationship to existing mechanisms, critical path position (§7.10), NFRs in the Mirror (§7.11), multi-perspective valuation (§7.12), the Graduation Checklist (§7.13), and false comprehension artefacts / micro-misalignment (§7.14, IndyDevDan 2026).
- **`specification.md` §8.5.1** — two new conformance anti-patterns: actions without comprehension artefacts; Structural Classifier rules not in Constitutional Memory.

### Changed
- **`specification.md`** — §7 Standards Landscape → §8; §7.5 Conformance → §8.5 (sub-sections renumbered accordingly); §8 Deliverables → §9. Specification status updated to v1.4.0.
- **`thesis.md`** — §3 extended with Comprehension Contract as the fourth mechanism alongside Equilibrium, Memory, and Epistemic Discipline.

### Why

The Comprehension Contract was designed and implemented as a Mirror schema extension (v0.2.0) and hello-colony example in v1.3.0. v1.4.0 makes it a formal specification section — the mechanism is now fully described, its relationship to all existing mechanisms documented, and its conformance implications stated. The dark code response (Jones 2026) is now not just named in the knowledge base but answered in the specification itself.

## [1.3.0] — 2026-04-13

### Added
- **`schemas/agent-mirror-v0.2.0.json`** — updated Agent Mirror schema adding four new optional sections: `comprehension_contract` (trust tier, pre-registered policies, audit rate, blast radius ceiling, classifier version), `nfrs` (inherited colony NFRs plus agent-specific commitments), `valuation` (self / peer / audit / human multi-perspective scoring), and `critical_path` inside the `relationships` object (structural and dynamic critical path flags). Previous `agent-mirror-v0.1.json` kept intact — both versions coexist.
- **`examples/hello-colony/graduation-checklists/finance-agent-v1.0-to-v1.1.yaml`** — the first graduation checklist. Records the finance domain agent's path from v1.0 to v1.1 (suppressing accreted self-monitoring capabilities that caused an overlap score of 0.24 with equilibrium-agent). Three evidence requirements, two approval requirements, three external actions — each pre-classified with blast radius and review regime.
- **`examples/hello-colony/graduation-checklists/README.md`** — explains what graduation checklists are, who maintains them (Registry Agent), and what each field means.
- **`examples/hello-colony-runtime/`** — Level 1 demonstration: a deterministic Python simulation that loads the hello-colony YAML files, validates them against the v0.2.0 schema, and simulates four colony events (bootstrap, equilibrium check, security patch co-sign, graduation query). No LLM calls, no external services. Run with `python runtime.py` after `pip install -r requirements.txt`.
- **`examples/equilibrium-playground/`** — Level 1 demonstration: a self-contained HTML visualisation of the Equilibrium System. D3.js overlap matrix heatmap colour-coded by threshold zones. Threshold sliders, add/remove agent controls, inject-workload button, three live index gauges (Overlap, Concentration, Vitality). No build step — open `index.html` in any browser.

### Changed
- **All 6 hello-colony agent YAML files** — extended with `comprehension_contract:`, `nfrs:`, and `valuation:` top-level sections, and `critical_path:` inside `relationships:`. Values reflect each agent's real position in the colony: Sentinel has two pre-registered policies (cosign + threat escalation); finance domain agent is Observing tier with 100% audit rate; v1.1 registry agent shows three peer interactions (calibrating).
- **`examples/hello-colony/colony-snapshot.yaml`** — new `comprehension_contract_overview:` section added at the bottom, capturing trust tier distribution, structural critical path agents, and a pointer to the active finance graduation checklist.
- **`examples/hello-colony/README.md`** — new section "New in v1.3.0: Comprehension Contract fields" added, explaining each new Mirror section.
- **`examples/README.md`** — new file (or updated) listing all three example directories with usage instructions.
- **`schemas/README.md`** — updated to document v0.2.0 alongside v0.1.

### Why

The pattern was previously articulated but not demonstrated. The Comprehension Contract (§7 of the forthcoming v1.3.0 specification) introduces the most significant new mechanism since v1.0: every action produces a pre-action comprehension artefact matched to the agent's trust tier and blast radius. The hello-colony examples now show what an agent's Mirror looks like when it carries this information. The live runtime shows the event logic running — schema validation, equilibrium flagging, security co-sign verification, graduation query — as deterministic code rather than description. The equilibrium playground makes the three indices interactive so the pattern's dynamics are visceral rather than abstract. The pattern now demonstrates what it describes.

## [1.2.2] — 2026-04-13

### Added
- **`knowledge-base/references/dark-code.md`** — captures Nate B Jones's 2026 framing of *dark code* (code that was never understood by anyone at any point in its lifecycle), its two structural breaks (runtime tool selection; velocity outpacing comprehension), the Amazon Kiro / retail outage incident record as public preview, and Jones's three prescribed layers (spec-driven development, context engineering, comprehension gates). The file maps each of Jones's layers onto Agent Colony mechanisms — Agent Mirror, Colony Memory, Equilibrium System, Coexistence Boundary — and records where the pattern extends beyond his framing (lifecycle identity across technology generations, population dynamics, mutual coexistence).

### Changed
- **`manifesto.md`** — new paragraph in "What Is an Agent Colony?" introducing dark code as the contemporary name for the failure mode the pattern exists to prevent, with the Amazon Kiro incident as public preview and the core reframing: *discipline that lives only in human habit erodes under velocity pressure; discipline that lives in the architecture erodes more slowly*. Links to the full reference in the knowledge base.
- **`thesis.md`** — new paragraph in §1 "The Problem" citing Jones (2026) as corroborating practitioner evidence for the comprehension gap claim, with the explicit argument that Jones's three layers are necessary but insufficient at the population level and that the Agent Colony raises each layer from per-module to per-agent-and-per-generation, per-colony-lifetime, and population-dynamics scope respectively.
- **`knowledge-base/references/README.md`** — adds dark-code.md to the structure listing.

### Why

The manifesto and thesis both argue *historically* — every shift in distributed systems has faced the same question. That framing is correct but abstract; a reviewer from an engineering org under AI adoption pressure reads it as a philosophical observation rather than as a description of their present liability. Jones's *Dark Code* gives the same argument a contemporary name, a documented incident catalogue, and a regulatory deadline (the EU AI Act enforcement date in August 2026). Adding it to the knowledge base is not decoration — it changes the answer to *"what happens if we do not build this?"* from a hypothetical to a case study. It also strengthens the lesson *acknowledgment-is-not-mitigation* by showing that Jones independently reached the same conclusion ("observability is retrospective; guardrails are reactive; adding layers makes it worse") from the practitioner side.

## [1.2.1] — 2026-04-13

### Added
- **`knowledge-base/writings/`** — new subfolder for things written *about* the pattern. Articles, blog posts, talks. Each entry is preserved verbatim with a link to the canonical published version.
- **First article: *It takes a village — the Agent Colony definition*** by David R Oliver, published on Medium 2026-04-12. The lay-audience introduction to the pattern, using the metaphor of a village for the six principles, the colony memory layers, and the epistemic discipline. Captured at [`knowledge-base/writings/2026-04-12-it-takes-a-village.md`](knowledge-base/writings/2026-04-12-it-takes-a-village.md). [Read on Medium](https://medium.com/@davidroliver/it-takes-a-village-the-agent-colony-definition-32b9bd714bb8).

### Changed
- **`README.md`** — surfaces the article in two places: a callout near the top ("New here? Start with the lay-audience article"), and as the first entry in the "Scope and audiences" section, recognising that not every reader is a technical practitioner.
- **`knowledge-base/README.md`** — structure listing now includes the `writings/` subfolder with a note on how it complements the other three (incoming feedback, outgoing writings, distilled lessons, inherited references).

### Why

The article is the first time the Agent Colony pattern has been written for a non-technical audience. It belongs in the knowledge base alongside the feedback and lessons because it is part of the pattern's evolution — specifically, the moment the pattern moved from "thing the author thinks about" to "thing the author has explained to someone else's family". Preserving it in-repo (not just linking to Medium) means future contributors can trace what was said to whom and when, even if the live URL changes.

## [1.2.0] — 2026-04-13

### Added
- **`knowledge-base/`** — new top-level folder capturing the pattern's own evolution. Three subfolders:
  - **`feedback/`** — peer review captured as it arrives. Four rounds so far, one file per round, each with: key points raised, verdict, what changed in response, and what has not changed and why. Negative feedback kept alongside positive.
  - **`lessons/`** — insights extracted from feedback and development. Each lesson carries an evidence grade (empirical / corroborated / theoretical / inherited / anecdotal) and a note on whether it has graduated to a specification rule. Four lessons so far: *acknowledgment is not mitigation*, *diagrams must run on rules not taste*, *scale slippage is a feature when stated*, *worked examples must track the spec*.
  - **`references/`** — prior art (MAPE-K, FIPA, KQML, MOISE+ / OperA / Jason, Constitutional AI, stigmergy, holonics, Agentic Hives) and active standards watch (A2A, MCP, AGNTCY / OASF, NIST Agent Standards Initiative, AGENTS.md, IEEE P3119, ISO/IEC 42001 family). Working notes behind the thesis literature review, including concessions and disagreements the formal prose compresses.
- **`examples/demonstration-options.md`** — a design memo of ten options for building a visual demonstration of the pattern, organised against four purposes (demonstrate, educate, evaluate, prove). Includes a purpose-fit matrix, three recommended combinations at different ambition levels, and honest trade-offs. This is the first forward-looking design memo captured in the repo.

### Changed
- **`README.md`** — "What's in this repository" now lists the knowledge base and renames "Example" to "Examples" (to reflect that `examples/` now has more than just hello-colony).

### Why

The manifesto asks for interrogation, not agreement. The repo had no visible mechanism for capturing that interrogation — feedback arrived, was acted on, and disappeared into commit messages. The knowledge base closes that loop. Every substantive critique received in v1.0.0 through v1.1.6 is now a first-class artefact with traceable lineage: feedback → lesson → rule (where the lesson graduated). The pattern's own epistemic principles (evidence grades, mandatory dissent, lessons become rules) are now applied to the pattern's own development. The process the pattern prescribes for colonies is the process that built the pattern itself.

## [1.1.6] — 2026-04-13

### Added
- **`diagrams/README.md`** — shared colour palette and style conventions across all six diagrams. Explains what blue / green / purple / red / orange / yellow mean and where each is used, so the set reads as coherent rather than as six different authors.
- **`Agent Colony v1.1.6 — design, not validated`** footer stamp on every diagram. Prevents the common misreading that the diagrams describe a real running system. Matches the intellectual honesty of the prose.
- **Four-layer architecture: inter-layer arrows.** Previously the diagram was a static stack with no dynamics. Now shows: Sentinel → Mesh (monitors), Patch → Mesh (applies patches), Mesh → Response Coordinator (reports anomalies), Sentinel ↔ Patch (co-signs security upgrades — v1.1.1 reference), Mesh → Chronicler (events recorded, via left gutter), Response Coordinator → Coexistence Boundary (escalates, via right gutter).
- **Equilibrium diagram: index → failure mapping.** Each of the three detection indices now carries a small annotation mapping it to the failure mode it detects — Overlap and Concentration detect consolidation, Vitality detects either extreme.
- **Maturity model: labelled trust gates** — each column's gates now carry a specific criterion ("honest observation", "intellectual honesty") instead of the generic "trust gate". **Row independence annotation** — explicit note that a colony can be Proven in Governance while still Seeded in Funding. **Earned Autonomy tagline** — "You graduate by proving you can — you do not graduate by waiting."
- **Agent Mirror: v1.1.1 co-sign annotation.** The Immune System reader description now explicitly mentions co-signing preauthorised security upgrades. The Governance reader description now lists all the agents that read relationship data (Registry, Equilibrium, Lifecycle, Constitutional) instead of only the first two.

### Fixed
- **Evolutionary context: singular/plural consistency.** Unit fields are now "Services", "Microservices", "Agents" (plural) to match the paradigm-level framing. Only "Application" remains singular because monoliths have exactly one per era.

## [1.1.5] — 2026-04-13

### Fixed

- **Agent Mirror diagram: equal-length arrows on both sides.** Previous v1.1.4 had the left arrows at 180px and the right arrows at 40px stubs. Rebuilt with exactly 120px arrows on every side, labels positioned symmetrically around the card midpoint at x=640, `textAlign: right` on left labels and `textAlign: left` on right labels so the text pushes toward the arrow.
- **Equilibrium diagram: centre-line alignment across all columns.** The three columns (Consolidation / Equilibrium / Fragmentation) now have every element — top label, subtitle, main box, super-agent blob, bottom gauge, gauge heading, gauge description — aligned on the same vertical centre lines at x=240/800/1360. Previously the gauge headings drifted (250/700/1310) and subtitle labels drifted by ±20px.
- **Colony Memory Reflection Cycle: rebuilt from scratch with proper circular geometry.** Previous diagram had scattered node positions, inconsistent shape sizes, mismatched colours, floating annotations, and ambiguous arrow direction. Rebuilt with six nodes sitting on a geometric circle (radius 320, centre 640,500) at exact 60° angular spacing. All three memory stores are identical rectangles (240×120), all three transitions are identical ellipses (200×100). Arrows are uniform in stroke width and colour. Memory colours now form a progression (light blue → medium blue → dark blue) showing the distillation from events to lessons to constitutional rules. Annotations moved out of the ring — the centre is now a short "Colony Memory / The reflection cycle" heading, and the summary caption sits below the diagram as a figure caption.

### Changed

- Upstream excalidraw-diagram skill updated with three new rule sections:
  - **Centre-Line Alignment** — elements in a shared column or row must share cx or cy exactly
  - **Cycle Diagrams** — nodes on a cycle must sit on a geometric circle with equal angular spacing, peer nodes share size and shape, arrow styling is uniform
  - **Annotations and Floating Text** — every text element must have a clear anchor; long explanations belong in figure captions below the diagram
- Five new validation table rows catch these defects automatically in future diagrams.

## [1.1.4] — 2026-04-13

### Fixed
- **Agent Mirror diagram: mirror-symmetric layout and perfectly horizontal arrows.** The diagram previously had the "Self" label with two zig-zag arrows reaching across multiple sections, and the right-side arrows were slightly off-horizontal (10px drift). Rebuilt with strict bilateral symmetry: three labels on the left (Registry Agent → Core Identity, Self → Autonomy, Lifecycle Agent → Lifecycle) and three on the right (Other Agents → Capabilities, Immune System → Security, Governance → Relationships). Every arrow is a single horizontal segment with `y_start == y_end` at the target section's y-centre. Every section now has exactly one external reader.
- The underlying excalidraw-diagram skill has been updated with explicit Arrow Straightness and Symmetric Layout rules so future diagrams follow the same discipline by default.

## [1.1.3] — 2026-04-13

### Fixed
- **Arrows in diagrams are now straight.** The SVG exporter was preserving intermediate waypoints from the Excalidraw source, causing some arrows (most visibly the "Self" arrows in the Agent Mirror diagram) to zig-zag. The exporter now draws arrows as direct lines from the first point to the last point, ignoring intermediate waypoints. Lines (non-arrows) keep their polyline shape because they often draw borders or underlines where the shape matters.

## [1.1.2] — 2026-04-13

### Added
- **Scale calibration in `examples/hello-colony/`** — `colony-snapshot.yaml` now declares `scale: 5-agent-team` with an explanatory `scale_notes` block tying the example to the specification's Scales of Application table. README opens with a Scale Calibration section making the same point.
- **Preauthorised security upgrade fields in `registry-agent.v1.1.yaml`** — the security_patch evolution log entry now shows all three v1.1.1 invariants concretely: `preauthorised_action_class: patch_application` (closed enum), `co_signer: sentinel-agent` + `co_sign_verified: true` (Immune System co-sign), `pre_state_hash`, `rollback_window_minutes`, `rollback_deadline`, `append_only_log_id` (append-only audit log). `last_security_upgrade` in the security section is enriched with the same metadata.
- **Hello-colony README section** walking through the preauthorisation fields and showing how the canonical attack (exfiltration-as-security-upgrade) fails at the enum, the co-sign, and the log.

### Changed
- **Trust Ledger row** in the Scales of Application table: 5-agent cell changed from "Informal; spreadsheet or markdown table" to "Human memory plus a retro; the team itself is the ledger" — honest about what the ledger actually is at that scale. Mirrored in thesis.

## [1.1.1] — 2026-04-13

### Added
- **Scales of application** subsection in `specification.md` §1 — explicit table showing how each principle/mechanism adapts at three scales (5-agent team, 50-agent org estate, 5,000-agent ecosystem). Reframes unit-of-analysis "slippage" as scale-adaptive application.
- **Security upgrade preauthorisation** strengthened with three concrete invariants: closed enum of preauthorised action classes, Immune System co-sign requirement, append-only log with bounded rollback. Turns the corollary from acknowledged risk into a mitigation with defence in depth.
- **Preauthorised-security abuse failure mode** in Conformance section (§7.5) now shows six-layer defence (three structural from the new invariants, three behavioural from Sentinel/Patch/Response).

### Changed
- `thesis.md` — mirrors the scale-adaptive table and strengthened preauthorisation treatment (shorter summaries, pointer to specification for full detail).

## [1.1.0] — 2026-04-13

### Added
- Agent Mirror JSON Schema (`schemas/agent-mirror-v0.1.json`)
- Worked example: `examples/hello-colony/` with 5 agent definitions, a pre/post-evolution pair, and a colony snapshot
- Conformance section in `specification.md` with anti-patterns, health signals, and failure modes
- `CONTRIBUTING.md` — contribution guide applying the paper's own epistemic principles
- `CITATION.cff` — Citation File Format metadata
- Issue templates for challenges and refinements
- SVG exports of all 6 diagrams for native GitHub rendering

### Changed
- README now includes a "Scope and audiences" section routing practitioners, researchers, and implementers to the appropriate documents
- Thesis paper diagrams now reference `.svg` files (rendered inline on GitHub) instead of `.excalidraw` source files

### Fixed
- Diagrams now render on GitHub — previously the `.excalidraw` references showed as broken image links
- License contradiction in `specification.md` — removed any ownership statement that conflicted with the repo-level CC BY 4.0 licence

## [1.0.0] — 2026-04-11

### Added
- The Agent Colony Manifesto
- The thesis paper: "The Agent Colony: A Pattern Language for Self-Governing AI Agent Ecosystems"
- v1.0 Specification with four-layer architecture, Agent Mirror schema, colony dynamics, and maturity model
- 6 Excalidraw source diagrams
- CC BY 4.0 licence
