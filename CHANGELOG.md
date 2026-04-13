# Changelog

All notable changes to the Agent Colony Pattern are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Version numbers follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
