# Changelog

All notable changes to the Agent Colony Pattern are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Version numbers follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
