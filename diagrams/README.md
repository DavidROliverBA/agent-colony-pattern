# Diagrams

Seven SVG diagrams rendered from the Excalidraw source files in this directory. They illustrate the Agent Colony pattern and are referenced inline from `thesis.md` and `manifesto.md`.

## The set

| File | What it shows |
|------|----------------|
| [`agent-colony-evolutionary-context.svg`](agent-colony-evolutionary-context.svg) | The paradigm progression: monoliths → SOA → microservices → Agent Colonies, and what each shift added |
| [`agent-colony-four-layer-architecture.svg`](agent-colony-four-layer-architecture.svg) | The four-layer colony architecture with the Coexistence Boundary and inter-layer dynamics |
| [`agent-colony-agent-mirror.svg`](agent-colony-agent-mirror.svg) | The Agent Mirror — six-section identity schema with role-differentiated readers |
| [`agent-colony-equilibrium.svg`](agent-colony-equilibrium.svg) | The Equilibrium System — consolidation vs fragmentation pressure with three detection indices |
| [`agent-colony-memory-cycle.svg`](agent-colony-memory-cycle.svg) | The Colony Memory reflection cycle — six nodes on a circle showing how events become constitutional rules |
| [`agent-colony-maturity-model.svg`](agent-colony-maturity-model.svg) | The Earned Autonomy maturity model — three independent progressions with trust gates |
| [`agent-colony-lens-traversal.svg`](agent-colony-lens-traversal.svg) | The audience-lens model — five sequential lenses (Newcomer → Observer → Operator → Beekeeper → Architect) with canonical artefacts and the re-entry curve. Added v1.5.0 alongside Principle 7 (Accessibility through abstraction). |

**Note on v1.5.0:** The existing six mechanism diagrams are pitched at the Beekeeper/Architect depth (Principle 7 terminology). Newcomer/Observer companion diagrams — "village-level" visual explanations of the same mechanisms — are a known gap deferred to v1.6+.

## Shared colour palette

Colours carry meaning across the diagrams. A single legend for the whole set:

| Colour | Semantic meaning | Used in |
|--------|-----------------|---------|
| **Blue family** (#3b82f6, #60a5fa, #93c5fd) | Governance, authority, structured knowledge. Darker = more authoritative or later in a progression. | Layer 1 governance band, Agent Mirror identity sections, memory progression (event → lesson → constitutional) |
| **Green** (#a7f3d0, #047857) | Health, stability, equilibrium, end-state success | Layer 3 agent mesh, equilibrium zone, maturity "proven" stage, colony relationships |
| **Purple/lavender** (#ddd6fe, #6d28d9) | AI, autonomy, self-evolution, reflection | Agent Colonies box, autonomy section in the Mirror, memory transitions (Events, Reflection, Promotion), maturity "experimentation" track |
| **Red/pink** (#fee2e2, #fecaca, #dc2626, #b91c1c) | Security, danger, pressure, warning. Solid = immediate, dashed = boundary or proposed | Layer 2 immune system, coexistence boundary, consolidation pressure, security posture |
| **Orange/peach** (#fed7aa, #c2410c) | Lifecycle stages, transitions, events occurring | Lifecycle section in the Mirror, Events node in the memory cycle, Trust Ledger strip |
| **Yellow** (#fef3c7, #b45309) | Decisions, gates, checkpoints | Trust gates in the maturity model, decision points |
| **Grey** (#64748b, #94a3b8) | Metadata, captions, annotations, version footers | Subtitles, descriptions, figure captions, version stamps |

## Style conventions

- **Hand-drawn Excalidraw aesthetic** (roughness: 0 for crisp edges). This signals "conceptual, not UML" — the lines are arguments, not implementation blueprints.
- **Solid borders for stable structures; dashed borders for boundaries or proposed/not-yet-established elements** (e.g., the Coexistence Boundary, the Agent Colony box in the evolutionary progression).
- **Arrows are single-segment lines.** No waypoints or bends unless the bend itself carries meaning. Horizontal arrows are perfectly horizontal; vertical arrows are perfectly vertical.
- **Peer elements share size and shape.** Three memory stores in the memory cycle are identical rectangles; three transitions are identical ellipses.
- **Centre-line alignment.** Elements in the same conceptual column share an exact `x`-centre; elements in the same row share an exact `y`-centre.

## Version status

Every diagram carries a footer stamp — currently `Agent Colony v1.5.0 — design, not validated` on new diagrams and `v1.1.x` on the original six. This is deliberate. The pattern is v1 conceptual work, not backed by a reference implementation. The footer exists to prevent the common misreading that these diagrams describe a real running system.

## Editing the sources

The `.excalidraw` source files are JSON. They can be:

- Opened in [Excalidraw](https://excalidraw.com) (file → open)
- Opened in [Obsidian](https://obsidian.md) with the Excalidraw plugin
- Edited directly as JSON (surgical changes)

After editing, re-generate the SVGs with:

```bash
python3 scripts/export-svg.py
```

The exporter is in `scripts/export-svg.py`. It handles rectangles, ellipses, diamonds, lines, arrows, and text — the six primitives used across the set. It does **not** replicate Excalidraw's full hand-drawn rendering; the output is clean geometric SVG optimised for GitHub rendering.

## Rendering to PNG (optional)

For local previews or external use:

```bash
for svg in diagrams/agent-colony-*.svg; do
  name=$(basename "$svg" .svg)
  rsvg-convert -w 1400 "$svg" -o "/tmp/${name}.png"
done
```

Requires `librsvg` (`brew install librsvg` on macOS, `apt install librsvg2-bin` on Linux).
