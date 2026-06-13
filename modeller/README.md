# ArchModeller

A **model-first, browser-based architecture modelling tool** for **C4** and
**ArchiMate**, inspired by IcePanel's model-driven C4 experience and extended to
cover the full ArchiMate layer stack. It runs entirely as a **static front-end**
and is designed to be published to **GitHub Pages** with no back end.

> Diagrams are *views* over a single shared model. Create an element once, reuse
> it across many diagrams, drill down from landscape to component, and rename it
> in one place to update it everywhere.

---

## Why it works on GitHub Pages

- **No build step.** Plain ES modules + CSS. Open `index.html` and it runs.
- **No server.** All state lives in the browser (localStorage) and in files you
  import/export. Nothing is sent anywhere.
- **Relative asset paths** and **hash-based routing** (`#/diagram/<id>`), so it
  works at any base path Pages assigns.
- Optional collaboration/sync features are designed as **decoupled enhancements**
  and are *not* required for the baseline app.

## Technology choices (and why)

The build prompt deliberately left the stack open. The choices here optimise for
the one hard constraint — *must run on GitHub Pages without a server*:

| Concern | Choice | Reason |
|---|---|---|
| Framework | **None** (vanilla ES modules) | Zero build/deploy friction; nothing to break a Pages base path |
| Rendering | **SVG** | Crisp at any zoom, presentation-quality, exports natively to SVG/PNG |
| State | Custom store with undo/redo + pub/sub | Small, transparent, decoupled from rendering |
| Persistence | localStorage + JSON/CSV files | Baseline works offline; no secrets, no back end |
| Routing | Hash routing | Pages-safe, no 404 rewrites needed |

The model layer (`src/model.js`) is fully decoupled from rendering — diagrams
store only ids + layout, so the same object renders consistently in every view.

---

## Quick start (local)

Because browsers restrict ES modules over `file://`, serve the folder over HTTP:

```bash
cd modeller
python3 -m http.server 8080
# open http://localhost:8080
```

Any static server works (`npx serve`, `php -S`, etc.). On first run the app seeds
a sample microservices model so the canvas isn't empty.

## Deploy to GitHub Pages

Two supported paths:

**A. GitHub Actions (recommended).** This repo includes
`.github/workflows/pages.yml`, which uploads `modeller/` as the Pages artifact.
In your repository: **Settings → Pages → Build and deployment → Source = GitHub
Actions**. Push to `main` (or run the workflow manually via *Actions →
Deploy ArchModeller → Run workflow*). The app is served at the root of your
Pages site.

**B. Serve from a folder.** Copy the contents of `modeller/` to the root of a
`gh-pages` branch (or set Pages to serve from `/docs` and place the files there).
No build is required.

---

## Feature matrix — baseline vs. optional

| Capability | Pure GitHub Pages (baseline) | Optional enhancement |
|---|---|---|
| C4 + ArchiMate modelling | ✅ | — |
| Shared model, reuse across diagrams | ✅ | — |
| Drill-down (landscape→context→container→component) | ✅ | — |
| Canvas: pan/zoom/grid/minimap/multi-select/connect/undo | ✅ | — |
| Tags, perspectives, overlays, flows | ✅ | — |
| Versioning / future-state snapshots & compare | ✅ (in-browser) | Git-backed history |
| Import: JSON, CSV, Structurizr DSL | ✅ | ArchiMate Exchange import* |
| Export: PNG, SVG, PDF, JSON, CSV, C4 DSL, ArchiMate XML | ✅ | — |
| Persistence | ✅ localStorage + files | Remote sync / shared workspace |
| Collaboration (live edit, presence, comments) | Local comments only | Real-time backend (out of scope for static core) |

\* The exporter writes a simplified ArchiMate Open Exchange XML; full-fidelity
import is a documented extension point, not yet implemented.

---

## Project structure

```
modeller/
  index.html              Entry point (loads src/main.js as a module)
  styles/main.css         Theme + all component styling (light/dark)
  src/
    main.js               App shell, routing, keyboard, high-level operations
    store.js              State, undo/redo, persistence, pub/sub
    model.js              Schema, factories, queries, import sanitisation
    util.js               DOM/SVG helpers, file I/O, CSV
    templates.js          Blank starters + worked sample models
    notation/
      c4.js               C4 element/relationship/level definitions
      archimate.js        ArchiMate layers, elements, relationships, viewpoints
      index.js            Unified notation registry + palette grouping
    canvas/canvas.js      SVG renderer + all pointer interaction
    ui/
      topbar.js           Nav, breadcrumb, menus, tools, diagram tabs
      leftPanel.js        Palette / tree / search / overlays / flows / templates
      rightPanel.js       Context-sensitive properties editor
      commandPalette.js   Ctrl/Cmd+K quick launcher
    io/
      exporters.js        PNG/SVG/PDF/JSON/CSV/C4-DSL/ArchiMate-XML
      importers.js        JSON/CSV/Structurizr-DSL
  docs/
    USER_GUIDE.md         Modelling workflow walkthrough
    SHORTCUTS.md          Keyboard shortcuts
    IMPORT_EXPORT.md      Formats and round-trip behaviour
```

## Security & privacy

- All imported models pass through `sanitiseModel()`: types are validated,
  dangling relationships dropped, nested metadata flattened, and link URLs
  filtered (only `http(s)`, `mailto`, and relative links survive — `javascript:`
  and `data:` are stripped).
- User content is rendered as **text/data only**; the canvas never injects raw
  HTML from model fields.
- No secrets or credentials are required. Nothing leaves your browser.

## Accessibility

Keyboard navigation throughout, visible focus rings, semantic controls outside
the canvas, non-colour state indicators (dashes for future-state, glyphs for
external/drill), `prefers-reduced-motion` support, and zoom tolerance.

See `docs/` for the full user guide, shortcuts, and import/export reference.
