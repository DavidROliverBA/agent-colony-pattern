# Round 4 — Full diagram critique — 2026-04-13

**Reviewer:** anonymous peer review
**Round:** 4
**Scope:** All six diagrams at v1.1.5 — rendered each SVG and inspected visually
**Version reviewed:** v1.1.5

## Summary

The reviewer rendered all six diagrams and returned a per-diagram critique. The cross-cutting conclusion: five of the six diagrams pass the "screenshot test" (each conveys its core claim without needing surrounding prose), but there are set-level weaknesses around missing arrows, inconsistent colour semantics across diagrams, and no "you are here — v1.1.x, design, not validated" marker.

## Per-diagram critique

### 1. Evolutionary context — strong
- The parallel meta-field structure (Unit / Composition / Governance) is the diagram's best feature.
- The dashed purple border on the Agent Colonies box signals "proposed" without a legend.
- **Nits:** The "+Autonomy / +Self-evolution / +Lifecycle identity" stack over the last arrow is visually heavier than the single-word callouts over the earlier arrows, slightly overselling the final transition. "Unit: Microservice" in the third box is singular where others should be plural.
- **Verdict:** keeps its promise.

### 2. Four-layer architecture — load-bearing, mostly works
- The Coexistence Boundary as a dashed line is exactly right — it is not "a layer", it is a membrane.
- The varying bubble sizes in L3 wordlessly show unbounded cardinality.
- **Weaknesses:**
  - **Directionality is missing.** There are no arrows. Is governance top-down? Do L2 agents reach into L1 or vice versa? Does Reflector observe L3? The reader has to guess.
  - L4 Substrate is a flat strip with no detail. The "commoditised" message needs a muted visual treatment.
  - The Coexistence Boundary has no indication of what crosses it.
- **Verdict:** the scaffolding diagram. Highest-value single fix in the set: add inter-layer arrows.

### 3. Agent Mirror — most self-explanatory of the six
- *"The best diagram in the set."* The reader-side annotations (Self, Other Agents, Immune System, Governance) make the role-differentiated access surface legible in two seconds.
- Numbering gives the diagram a natural reading order.
- The *"Descriptive, not prescriptive — divergence between Mirror and behaviour is a signal, not a constraint"* tagline is the most important sentence in the whole project, and it lives in the diagram rather than buried in prose.
- **Nits:**
  - "Security upgrades exempt" is shown in Section 3 but the v1.1.1 enum / co-sign / rollback mitigation is not reflected.
  - The Governance arrow lists only "Registry and Equilibrium agents read these" but per the spec, Constitutional, Lifecycle, and Reflector also touch the Mirror.
- **Verdict:** *"This diagram alone justifies the six-diagram set. It teaches."*

### 4. Equilibrium — clever concept, rough execution
- The two-sided pressure framing is correct and important. Most pattern documents show only one failure mode.
- Threshold numbers embedded in the image (<15% / 15–40% / >40%) mean a reader who screenshots only this diagram still carries the operational rule.
- **Weaknesses:**
  - The red zone (consolidation) has more visual weight than the blue (fragmentation), implying consolidation is the likelier failure — which the spec does not claim.
  - "Self-evolution pressure" as a purple box at the bottom is visually disconnected from the main spectrum.
  - **No mapping from indices to failure modes.** Which index detects which failure? The mapping exists in the spec but is absent from the diagram.
  - No time axis — equilibrium is a dynamic concept but the diagram is static.
- **Verdict:** the idea is right; the execution undersells it. Add the index-to-failure mapping and it becomes a reference diagram.

### 5. Memory cycle — conceptually correct, graphically confused
- Genuine cycle, not a pipeline — closes the loop.
- Each node names its owning agent.
- *"Promotion / Recurring lessons graduate"* captures the differentiator from Anthropic-style constitutional AI.
- **Weaknesses:**
  - Colour semantics inconsistent — why is Constitutional the only green?
  - **No decay arrow.** The side annotation mentions "retired" but the diagram shows no reverse flow.
  - The tagging callout is orphaned, floating next to Lesson Memory with no anchor.
  - The closing-loop arrow is thin and easy to miss — it should be the heaviest line in the diagram.
- **Verdict:** needs a colour discipline pass and a visible decay path.

### 6. Maturity model — the weakest of the six
- **The diagram the reviewer would redraw.**
- The commit trail shows it was trimmed to remove an unreadable right-side annotation, and *"the cure left a scar"* — empty visual space on the right where context is missing.
- Trust gates have no content. What does the gate check? Who signs off?
- Colour per row is inconsistent with the rest of the set — no shared palette.
- *"Earned Autonomy"* in the title is the thesis' single most important phrase and the diagram carries no caption making the point explicit.
- **Verdict:** structurally right, visually least finished. Highest-leverage single improvement to the whole set.

## Cross-cutting observations

### Set-level strengths
1. All six pass the screenshot test.
2. Provenance is consistent — every named agent in the diagrams appears in the spec under the same name.
3. Honest rendering — the Excalidraw aesthetic signals "conceptual, not UML" and prevents over-reading precision into gestural lines.
4. Zero false decoration.

### Set-level weaknesses
1. **No shared palette or legend.** Blue means "infrastructure" in the architecture diagram, "memory" in the memory cycle, and "governance stage" in the maturity model.
2. **Arrows are inconsistent.** Some diagrams are all arrows (memory cycle, evolutionary context), some have none (four-layer architecture). The architecture diagram is where arrows are most missed.
3. **No v1.1.1 updates.** The security strengthening does not appear in any diagram. The Mirror diagram should carry a "co-signed by Immune System" annotation on Section 4.
4. **The maturity model undermines the others.** On GitHub, viewers pattern-match to the weakest artefact.
5. **No "you are here" marker.** None of the diagrams say "v1.1.x — design, not validated". A footer would match the intellectual honesty of the prose and prevent the "these look like they describe a real system" misreading.

## Priority fixes proposed

1. **Add inter-layer arrows to four-layer-architecture.svg.** The highest-leverage fix.
2. **Redraw maturity-model.svg** to remove the "trimmed scar", label trust gates, add Earned Autonomy tagline.
3. **Map indices → failure modes in equilibrium.svg** with small pointer lines.
4. **Add co-sign annotation to Agent Mirror Section 4** and co-sign icon on the four-layer diagram to reflect v1.1.1.
5. **Ship `diagrams/LEGEND.svg` or `diagrams/README.md`** fixing colour semantics across the set.

## Verdict

> About four hours of work would move the set from "competent conceptual illustrations" to "self-contained reference that travels without the paper". The diagrams are already the second-strongest artefact in the repo (after the thesis); these fixes would make them the strongest.

## What changed in response

All five priority fixes plus the nits implemented in **v1.1.6** (2026-04-13):

- **Four-layer architecture:** six inter-layer arrows added — Sentinel → Mesh (monitors), Patch → Mesh (applies patches), Mesh → Response Coordinator (reports anomalies), Sentinel ↔ Patch (co-signs v1.1.1), Mesh → Chronicler (events recorded, left gutter), Response Coordinator → Coexistence Boundary (escalates, right gutter).
- **Maturity model:** trust gates now labelled with specific criteria ("honest observation", "intellectual honesty"), explicit row-independence annotation, and the Earned Autonomy tagline *"You graduate by proving you can — you do not graduate by waiting."*
- **Equilibrium:** each index now carries an annotation mapping it to the failure mode it detects.
- **Agent Mirror:** Immune System reader description now explicitly mentions co-signing preauthorised security upgrades; Governance reader description now lists all four readers (Registry, Equilibrium, Lifecycle, Constitutional).
- **`diagrams/README.md`** created with the shared colour palette and style conventions.
- **Version footer** *"Agent Colony v1.1.6 — design, not validated"* added to every diagram.
- **Evolutionary context plural fix** — Unit fields now "Services", "Microservices", "Agents".

The upstream `excalidraw-diagram` skill (in the author's private workspace) was also updated with three new rule sections (Centre-Line Alignment, Cycle Diagrams, Annotations and Floating Text) so this class of defect cannot recur in future diagrams.

## What has not changed and why

- **The memory cycle decay arrow** — the reviewer suggested showing rule retirement as a reverse flow. Not yet implemented because the memory cycle was rebuilt from scratch in v1.1.5 to fix a more fundamental structural problem, and the rebuild moved the annotations out of the ring. Adding a decay arrow is a small follow-up for a future version.
- **L4 Substrate "muted visual treatment"** — partial fix only. The L4 band still uses the same visual weight as the other layers. A proper "faded" or "greyed" treatment would require changing the colour palette defined in the new diagrams/README.md, which needs to happen as a deliberate choice rather than a one-off.
