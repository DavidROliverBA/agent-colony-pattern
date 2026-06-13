# ArchModeller — User Guide

A walkthrough of the modelling workflow. The guiding idea: **you build one
model; diagrams are views into it.**

## 1. Core concepts

- **Element (object):** a thing in your architecture — a person, software
  system, container, ArchiMate application component, node, etc. It has a stable
  identity and can appear on many diagrams.
- **Relationship:** a typed, directional connection between two elements. Also
  shared across diagrams.
- **Diagram:** a *view*. It chooses which elements/relationships to show and
  where to place them. Renaming an element updates every diagram at once.
- **Flow / overlay / tag:** ways to annotate and present the model without
  duplicating diagrams.

## 2. Creating elements

- **Drag** from the left **Palette** onto the canvas, or **double-click** a
  palette item to drop it at the centre.
- Switch the palette between **C4** and **ArchiMate** with the toggle. ArchiMate
  elements are grouped by layer with the standard colours.
- Double-click an element on the canvas to **rename inline**. Use the right
  panel for full editing (descriptions, technology, tags, links, metadata).

## 3. Connecting elements

- Press **C** (or the connect tool ⤳ in the toolbar), then drag from one element
  to another. C4 diagrams default to a *uses* relationship; ArchiMate diagrams
  default to *serving*. Change the type in the right panel.
- Double-click a relationship to edit its label inline.

## 4. Drill-down (C4)

C4's power is moving from broad context to detail:

1. On a **System Context** diagram, a software system shows a **⤢ drill badge**.
2. Click it (or select the system and press **D**) to open/create its
   **Container** view, scoped to that system.
3. Containers drill the same way into **Component** views.
4. The **breadcrumb** in the top bar tracks where you are; click any crumb to
   navigate back up.

Add child elements via right-click → *Add child element*; children are linked to
their parent and appear automatically in the drill-down view.

## 5. ArchiMate layers & viewpoints

- Choose a diagram type of **ArchiMate Layer View** or **Cross-Layer View**.
- In the right panel pick a **Viewpoint** (e.g. *Application Cooperation*,
  *Layered*, *Technology/Infrastructure*). Elements outside the viewpoint's
  layers are dimmed so the view stays focused.
- Relationship types follow ArchiMate notation (composition, realization,
  serving, triggering, flow, …) with the correct arrow/marker styling.

## 6. Tags, perspectives & overlays

- Add **tags** to elements in the right panel. Tags belong to **groups**
  (ownership, risk, lifecycle, domain, …) so you can build perspectives.
- In the **Tags** tab, tick tags or ArchiMate layers to **filter** the current
  diagram — non-matching elements dim out. This gives you ownership/risk/domain
  views without duplicating the diagram.

## 7. Flows

Tell a story over an existing diagram:

1. Open the **Flows** tab → **+ New flow**.
2. Select a relationship on the canvas, then **+ step** (or right-click a
   relationship → *Add as flow step*).
3. Use **▶ / ◀** to step through. The active relationship and its endpoints are
   highlighted; everything else dims.

## 8. Versioning & future state

- **Versions menu → Snapshot current state** captures the whole model.
- **Compare with…** shows added / removed / changed elements and relationships.
- Mark elements/relationships with a **lifecycle** (current / future / proposed /
  removed). Future and proposed render dashed; removed renders faded — so a
  single diagram can communicate a transition.
- **Duplicate diagram** (right panel) to draft an alternative without touching
  the original.

## 9. Search & navigation

- The **Search** tab matches names, descriptions, tags, technology, types and
  metadata. Click a result to jump to it (it's added to the current view if not
  already present) and the canvas centres on it.
- The **Model** tab browses everything by hierarchy, type, or ArchiMate layer,
  and lets you add existing elements to the current diagram with **+**.
- **Ctrl/Cmd+K** opens the command palette to jump to any command, diagram, or
  element.

## 10. Saving & sharing

- Work is saved to your browser automatically (localStorage).
- **File → Save (download JSON)** for a portable project file; re-import via
  **File → Import JSON**.
- Export presentation output via the **Export** menu (PNG/SVG/PDF) or share the
  model as JSON/CSV/C4-DSL/ArchiMate-XML.

See `SHORTCUTS.md` and `IMPORT_EXPORT.md` for details.
