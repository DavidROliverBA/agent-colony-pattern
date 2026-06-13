// The shared model: schema, factories, validation and sanitisation.
//
// Design rule (product principle "model first, diagram second"):
//   - `objects` and `relationships` are the single source of truth.
//   - `diagrams` are VIEWS: they reference object/relationship ids and store
//     per-view layout (positions, styling overrides, filters, viewport).
//   - The same object may appear in many diagrams. Renaming it once updates
//     every view, because views hold ids, not copies.

import { uid, clone, safeHref } from './util.js';
import { elementDef } from './notation/index.js';

export const SCHEMA_VERSION = 1;

/** Create an empty, valid model. */
export function createModel(name = 'Untitled workspace') {
  const model = {
    schemaVersion: SCHEMA_VERSION,
    id: uid('model'),
    name,
    description: '',
    createdAt: new Date().toISOString(),
    objects: {},
    relationships: {},
    diagrams: {},
    flows: {},
    tags: {},
    comments: {},
    versions: {},          // { id: {id,name,createdAt,note,snapshot} }
    settings: { snapToGrid: true, gridSize: 10, theme: 'light' },
    diagramOrder: [],
  };
  return model;
}

/** Create a new object (model element). */
export function makeObject(type, props = {}) {
  return {
    id: uid('obj'),
    type,
    name: props.name || elementDef(type).label,
    shortDescription: props.shortDescription || '',
    description: props.description || '',
    technology: props.technology || '',
    tags: props.tags || [],
    links: props.links || [],          // [{label, url}]
    metadata: props.metadata || {},    // arbitrary key/value
    parentId: props.parentId || null,  // for C4 hierarchy (system→container→component)
    lifecycle: props.lifecycle || 'current', // current | future | proposed | removed
    ...props,
  };
}

/** Create a new relationship. */
export function makeRelationship(sourceId, targetId, type, props = {}) {
  return {
    id: uid('rel'),
    source: sourceId,
    target: targetId,
    type,
    label: props.label || '',
    technology: props.technology || '',
    description: props.description || '',
    direction: props.direction || 'forward', // forward | bidirectional | none
    tags: props.tags || [],
    metadata: props.metadata || {},
    lifecycle: props.lifecycle || 'current',
    ...props,
  };
}

/** Create a diagram (a view over the model). */
export function makeDiagram(props = {}) {
  return {
    id: uid('dgm'),
    name: props.name || 'New diagram',
    kind: props.kind || 'c4-context', // see DIAGRAM_KINDS
    notation: props.notation || 'c4', // c4 | archimate | mixed
    level: props.level || null,        // c4 level when applicable
    scopeId: props.scopeId || null,    // object whose internals this view shows (drill-down)
    viewpoint: props.viewpoint || 'all',
    nodes: props.nodes || {},          // { objectId: {x,y,w,h,styleOverride} }
    edges: props.edges || {},          // { relationshipId: {waypoints, styleOverride} }
    filters: props.filters || { tags: [], layers: [] },
    overlay: props.overlay || null,    // active overlay tag-group key
    viewport: props.viewport || { x: 0, y: 0, zoom: 1 },
    description: props.description || '',
    ...props,
  };
}

export function makeFlow(props = {}) {
  return {
    id: uid('flow'),
    name: props.name || 'New flow',
    description: props.description || '',
    diagramId: props.diagramId || null,
    steps: props.steps || [], // [{relationshipId, label, description}]
    ...props,
  };
}

export function makeTag(props = {}) {
  return {
    id: uid('tag'),
    name: props.name || 'tag',
    color: props.color || '#3b82f6',
    group: props.group || 'general', // overlay grouping e.g. ownership, risk
    ...props,
  };
}

export const DIAGRAM_KINDS = {
  'c4-landscape': { label: 'C4 System Landscape', notation: 'c4', level: 'landscape' },
  'c4-context': { label: 'C4 System Context', notation: 'c4', level: 'context' },
  'c4-container': { label: 'C4 Container', notation: 'c4', level: 'container' },
  'c4-component': { label: 'C4 Component', notation: 'c4', level: 'component' },
  'archimate-layer': { label: 'ArchiMate Layer View', notation: 'archimate', level: null },
  'archimate-crosslayer': { label: 'ArchiMate Cross-Layer View', notation: 'archimate', level: null },
  'freeform': { label: 'Free-form Mixed View', notation: 'mixed', level: null },
  'presentation': { label: 'Stakeholder Presentation', notation: 'mixed', level: null },
};

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

export function objectsInDiagram(model, diagram) {
  return Object.keys(diagram.nodes)
    .map((id) => model.objects[id])
    .filter(Boolean);
}

export function relationshipsInDiagram(model, diagram) {
  const present = new Set(Object.keys(diagram.nodes));
  // An edge is shown if both endpoints are on the diagram.
  return Object.values(model.relationships).filter(
    (r) => present.has(r.source) && present.has(r.target)
  );
}

/** All diagrams that contain a given object. */
export function diagramsContaining(model, objectId) {
  return Object.values(model.diagrams).filter((d) => d.nodes[objectId]);
}

/** Relationships touching an object. */
export function relationshipsOf(model, objectId) {
  return Object.values(model.relationships).filter(
    (r) => r.source === objectId || r.target === objectId
  );
}

/** Children of an object in the C4 hierarchy. */
export function childrenOf(model, parentId) {
  return Object.values(model.objects).filter((o) => o.parentId === parentId);
}

// ---------------------------------------------------------------------------
// Validation & sanitisation (security requirement 21)
// ---------------------------------------------------------------------------

/**
 * Validate and sanitise an imported model. Returns { model, warnings }.
 * Throws if the input is not a plausible model object.
 * All string fields are kept as data only — nothing is ever rendered as HTML.
 * Links are filtered through safeHref to strip javascript:/data: URLs.
 */
export function sanitiseModel(input) {
  if (!input || typeof input !== 'object') throw new Error('Not a model object');
  const warnings = [];
  const base = createModel(typeof input.name === 'string' ? input.name : 'Imported model');
  base.description = str(input.description);
  base.schemaVersion = SCHEMA_VERSION;

  const objects = obj(input.objects);
  for (const [id, raw] of Object.entries(objects)) {
    if (!raw || typeof raw !== 'object') continue;
    base.objects[id] = {
      id,
      type: str(raw.type) || 'softwareSystem',
      name: str(raw.name) || 'Unnamed',
      shortDescription: str(raw.shortDescription),
      description: str(raw.description),
      technology: str(raw.technology),
      tags: arr(raw.tags).map(str),
      links: arr(raw.links)
        .map((l) => ({ label: str(l?.label), url: safeHref(l?.url) }))
        .filter((l) => l.url),
      metadata: cleanMeta(raw.metadata, warnings),
      parentId: raw.parentId ? str(raw.parentId) : null,
      lifecycle: lifecycle(raw.lifecycle),
    };
  }

  const rels = obj(input.relationships);
  for (const [id, raw] of Object.entries(rels)) {
    if (!raw || typeof raw !== 'object') continue;
    if (!base.objects[str(raw.source)] || !base.objects[str(raw.target)]) {
      warnings.push(`Relationship ${id} references a missing object — skipped.`);
      continue;
    }
    base.relationships[id] = {
      id,
      source: str(raw.source),
      target: str(raw.target),
      type: str(raw.type) || 'uses',
      label: str(raw.label),
      technology: str(raw.technology),
      description: str(raw.description),
      direction: ['forward', 'bidirectional', 'none'].includes(raw.direction) ? raw.direction : 'forward',
      tags: arr(raw.tags).map(str),
      metadata: cleanMeta(raw.metadata, warnings),
      lifecycle: lifecycle(raw.lifecycle),
    };
  }

  const diagrams = obj(input.diagrams);
  for (const [id, raw] of Object.entries(diagrams)) {
    if (!raw || typeof raw !== 'object') continue;
    const d = makeDiagram({
      name: str(raw.name) || 'Diagram',
      kind: DIAGRAM_KINDS[raw.kind] ? raw.kind : 'freeform',
      notation: ['c4', 'archimate', 'mixed'].includes(raw.notation) ? raw.notation : 'mixed',
      level: raw.level ? str(raw.level) : null,
      scopeId: raw.scopeId ? str(raw.scopeId) : null,
      viewpoint: str(raw.viewpoint) || 'all',
      description: str(raw.description),
    });
    d.id = id;
    for (const [oid, n] of Object.entries(obj(raw.nodes))) {
      if (!base.objects[oid]) continue;
      d.nodes[oid] = {
        x: num(n?.x), y: num(n?.y),
        w: n?.w ? num(n.w) : undefined, h: n?.h ? num(n.h) : undefined,
        styleOverride: cleanStyle(n?.styleOverride),
      };
    }
    for (const [rid, e] of Object.entries(obj(raw.edges))) {
      if (!base.relationships[rid]) continue;
      d.edges[rid] = { waypoints: arr(e?.waypoints), styleOverride: cleanStyle(e?.styleOverride) };
    }
    if (raw.filters) d.filters = { tags: arr(raw.filters.tags).map(str), layers: arr(raw.filters.layers).map(str) };
    if (raw.viewport) d.viewport = { x: num(raw.viewport.x), y: num(raw.viewport.y), zoom: num(raw.viewport.zoom) || 1 };
    base.diagrams[id] = d;
  }

  const flows = obj(input.flows);
  for (const [id, raw] of Object.entries(flows)) {
    if (!raw || typeof raw !== 'object') continue;
    base.flows[id] = {
      id,
      name: str(raw.name) || 'Flow',
      description: str(raw.description),
      diagramId: raw.diagramId ? str(raw.diagramId) : null,
      steps: arr(raw.steps).map((s) => ({
        relationshipId: str(s?.relationshipId),
        label: str(s?.label),
        description: str(s?.description),
      })).filter((s) => base.relationships[s.relationshipId]),
    };
  }

  const tags = obj(input.tags);
  for (const [id, raw] of Object.entries(tags)) {
    if (!raw || typeof raw !== 'object') continue;
    base.tags[id] = {
      id,
      name: str(raw.name) || 'tag',
      color: /^#[0-9a-f]{3,8}$/i.test(raw.color) ? raw.color : '#3b82f6',
      group: str(raw.group) || 'general',
    };
  }

  if (input.settings && typeof input.settings === 'object') {
    base.settings = {
      snapToGrid: input.settings.snapToGrid !== false,
      gridSize: num(input.settings.gridSize) || 10,
      theme: input.settings.theme === 'dark' ? 'dark' : 'light',
    };
  }

  base.diagramOrder = arr(input.diagramOrder).filter((id) => base.diagrams[id]);
  // Append any diagrams missing from the saved order.
  for (const id of Object.keys(base.diagrams)) {
    if (!base.diagramOrder.includes(id)) base.diagramOrder.push(id);
  }

  // Preserve versions (snapshots are themselves models — sanitise recursively,
  // but cap depth by stripping nested versions to avoid unbounded recursion).
  const versions = obj(input.versions);
  for (const [id, raw] of Object.entries(versions)) {
    if (!raw || typeof raw !== 'object' || !raw.snapshot) continue;
    try {
      const snap = clone(raw.snapshot);
      delete snap.versions;
      base.versions[id] = {
        id,
        name: str(raw.name) || 'Version',
        createdAt: str(raw.createdAt) || new Date().toISOString(),
        note: str(raw.note),
        snapshot: sanitiseModel(snap).model,
      };
    } catch {
      warnings.push(`Version ${id} could not be restored.`);
    }
  }

  return { model: base, warnings };
}

function str(v) { return typeof v === 'string' ? v : (v == null ? '' : String(v)); }
function num(v) { const n = Number(v); return Number.isFinite(n) ? n : 0; }
function arr(v) { return Array.isArray(v) ? v : []; }
function obj(v) { return v && typeof v === 'object' && !Array.isArray(v) ? v : {}; }
function lifecycle(v) { return ['current', 'future', 'proposed', 'removed'].includes(v) ? v : 'current'; }

function cleanMeta(meta, warnings) {
  const out = {};
  if (!meta || typeof meta !== 'object') return out;
  for (const [k, v] of Object.entries(meta)) {
    if (typeof v === 'object') { warnings.push(`Metadata "${k}" flattened to text.`); out[str(k)] = JSON.stringify(v); }
    else out[str(k)] = str(v);
  }
  return out;
}

function cleanStyle(s) {
  if (!s || typeof s !== 'object') return undefined;
  const out = {};
  if (/^#[0-9a-f]{3,8}$/i.test(s.fill)) out.fill = s.fill;
  if (/^#[0-9a-f]{3,8}$/i.test(s.stroke)) out.stroke = s.stroke;
  if (/^#[0-9a-f]{3,8}$/i.test(s.text)) out.text = s.text;
  return Object.keys(out).length ? out : undefined;
}
