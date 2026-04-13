# Changelog

All notable changes to the Agent Colony Pattern are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Version numbers follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
