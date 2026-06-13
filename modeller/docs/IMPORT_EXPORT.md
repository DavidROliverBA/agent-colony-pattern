# Import & export

Everything runs in-browser — no server is involved, so all of this works from a
GitHub Pages deployment.

## Export

| Format | Scope | Notes |
|---|---|---|
| **PNG** | Current diagram | Rendered at 2× for crisp output, white background |
| **SVG** | Current diagram | Self-contained: styles are inlined, UI-only layers stripped |
| **PDF** | Current diagram | Opens the browser print dialog with the SVG (choose "Save as PDF") |
| **JSON** | Whole model | Complete, loss-less round-trip — the canonical save format |
| **CSV** | Whole model | Two files: `objects.csv` and `relationships.csv` |
| **C4 DSL** | C4 elements/views | Structurizr-style `.dsl` (best-effort) |
| **ArchiMate XML** | ArchiMate elements | Simplified Open Exchange format |

### JSON model shape (abridged)

```jsonc
{
  "schemaVersion": 1,
  "name": "My workspace",
  "objects":       { "obj_x": { "id": "obj_x", "type": "softwareSystem", "name": "...", "tags": [], "links": [], "metadata": {}, "parentId": null, "lifecycle": "current" } },
  "relationships": { "rel_y": { "id": "rel_y", "source": "obj_x", "target": "obj_z", "type": "uses", "label": "...", "direction": "forward" } },
  "diagrams":      { "dgm_z": { "id": "dgm_z", "name": "...", "kind": "c4-context", "notation": "c4", "nodes": { "obj_x": { "x": 10, "y": 20 } } } },
  "flows": {}, "tags": {}, "versions": {}, "diagramOrder": ["dgm_z"]
}
```

## Import

| Format | Behaviour |
|---|---|
| **JSON (replace)** | Replaces the whole workspace with the file's model |
| **JSON (merge)** | Adds the file's objects/relationships/diagrams to the current model |
| **CSV** | Creates elements from rows and drops them on a new diagram |
| **Structurizr DSL** | Parses `person`/`softwareSystem`/`container`/`component` and `a -> b "label" "tech"`; nested `{ }` blocks set parent/child for drill-down |

### CSV import columns

A `name` column is required. Recognised columns (case-insensitive): `id`, `type`,
`name`, `technology`, `tags` (pipe-`|`-separated), `lifecycle`, `parentId`,
`shortDescription`, `description`. **Any other column becomes custom metadata.**

```csv
name,type,technology,tags,owner
Web App,container,React,edge|public,Team A
Orders DB,database,PostgreSQL,core,Team B
```

Here `owner` is not a built-in field, so it is stored as metadata on each element.

## Safety

All imports are validated and sanitised before use:

- unknown/invalid types fall back to sensible defaults;
- relationships pointing at missing elements are dropped (with a console warning);
- nested metadata objects are flattened to strings;
- link URLs are filtered — only `http(s):`, `mailto:` and relative links are
  kept; `javascript:` / `data:` URLs are removed.

## Round-tripping

`JSON export → JSON import (replace)` is loss-less, including positions,
viewpoints, filters, flows, tags and version snapshots. Use it as your project
file format; use the other formats for interchange and presentation.
