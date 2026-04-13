# Diagrams must run on rules, not on taste

**Date first learned:** 2026-04-13
**Evidence grade:** corroborated
**Source:** Multiple diagram iterations in v1.1.3 through v1.1.6; [Round 4 diagram critique](../feedback/2026-04-13-diagram-critique.md)
**Status:** graduated to rule (upstream `excalidraw-diagram` skill)

## The lesson

Conceptual diagrams built by hand drift. They drift in arrow length, in element alignment, in colour semantics, in shape sizing, in annotation placement. The drift is invisible to the author while building and obvious to a reader on first viewing. The fix is not more care — the fix is **rules**, applied and verified mechanically after the diagram is built.

## Conditions

Applies to any hand-built conceptual diagram where the geometry carries meaning. It applies especially strongly when the diagram is meant to be a reference artefact that travels without the surrounding prose.

Specifically, the rules that matter most in practice:

1. **Arrows must be straight single segments.** No waypoints, no bends unless the bend is itself the message.
2. **Arrows on the same axis must be the same length.** Equal left and equal right in a bilateral diagram; equal across stages in a progression.
3. **Elements in the same column or row must share an exact centre line.** Not "approximately" — exactly. Even a 10px drift reads as sloppy at normal viewing distance.
4. **Peer elements must be the same size and shape.** Three memory stores in a cycle are identical rectangles. Three transitions are identical ellipses.
5. **Cycle diagrams need geometric circles.** Compute node positions from `(cx + R*cos(θ), cy - R*sin(θ))` with equal angular spacing. Never place cycle nodes by eye.
6. **Annotations must be anchored.** Every text element belongs inside a node, adjacent to one with a clear visual connection, or at a structural caption position. Floating text with no anchor is a defect.
7. **Colour semantics must be shared across a diagram set.** If blue means "governance" in one diagram and "memory" in another, the set reads as six different authors.

## Evidence

- **v1.1.0** — six diagrams shipped. Several had asymmetric arrows, drifted alignments, and inconsistent colour use. None were caught by the author during production.
- **v1.1.3** — user noticed arrows in the Agent Mirror diagram were not straight. Fix applied in the SVG exporter: collapse multi-point arrows to start + end.
- **v1.1.4** — user noticed the "Self" label had two zig-zag arrows reaching multiple sections. Diagram rebuilt with mirror symmetry.
- **v1.1.4 follow-up** — user noticed that even with mirror symmetry, left arrows were 180px and right arrows were 40px stubs. Another rebuild with equal arrow lengths.
- **v1.1.5** — user noticed the Equilibrium gauges were not centre-line-aligned with the pressure boxes above them (drift of 10–100px). Script-fixed to snap to the same x-centres.
- **v1.1.5** — user critiqued the Memory Cycle as having scattered nodes, inconsistent shapes, mismatched colours. Rebuilt from scratch using geometric circle positioning.
- **v1.1.6** — reviewer's diagram critique identified five more issues at the set level.

Six rounds of "the author built something and a reader found the defect" across three days = corroborated.

## Disproven if

- An author consistently builds drift-free diagrams by eye without using the rules. (Not observed — across three days of iteration, every diagram accumulated at least one geometry defect during initial building.)
- The rules themselves introduce a class of defects that would not have existed otherwise. (Not yet observed.)

## Related rules

All seven rules above have been added to the upstream `excalidraw-diagram` skill (private workspace) in three sections:

- **Arrow Straightness** (mandatory)
- **Symmetric Layout for Bilateral Labels** (mandatory)
- **Centre-Line Alignment** (mandatory)
- **Cycle Diagrams** (mandatory)
- **Annotations and Floating Text** (mandatory)

Plus seven new rows in the validation table so the defects are caught automatically in future diagrams: arrow straightness, horizontal arrows horizontal, bilateral symmetry, equal arrow length, centre-line alignment, cycle geometry, peer node uniformity, uniform arrow styling, anchored annotations.

The broader meta-lesson — **rules over taste for geometry-carrying diagrams** — is the lesson worth preserving at the pattern level.
