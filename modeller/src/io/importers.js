// Import: JSON model, CSV objects/relationships, and a lightweight
// Structurizr DSL parser. All imports flow through model.sanitiseModel()
// in the store, so untrusted content is validated before use.

import { store } from '../store.js';
import { parseCsv, pickFile, readFileAsText, uid } from '../util.js';
import { createModel, makeObject, makeRelationship, makeDiagram } from '../model.js';

export async function importJson(merge = false) {
  const file = await pickFile('.json,application/json');
  if (!file) return;
  const text = await readFileAsText(file);
  let parsed;
  try { parsed = JSON.parse(text); } catch { alert('Invalid JSON file.'); return; }
  const warnings = store.replaceModel(parsed, { merge });
  if (warnings.length) console.warn('Import warnings:', warnings);
  return warnings;
}

/**
 * Import objects from a CSV with headers including at least: name.
 * Recognised columns: id, type, name, technology, tags, lifecycle, parentId,
 * shortDescription, description. Unknown columns become metadata.
 */
export async function importCsv() {
  const file = await pickFile('.csv,text/csv');
  if (!file) return;
  const text = await readFileAsText(file);
  const rows = parseCsv(text);
  if (rows.length < 2) { alert('CSV needs a header row and at least one data row.'); return; }
  const header = rows[0].map((h) => h.trim());
  const idx = (name) => header.findIndex((h) => h.toLowerCase() === name);
  const nameCol = idx('name');
  if (nameCol < 0) { alert('CSV must have a "name" column.'); return; }

  store.commit('Import CSV', (m) => {
    const known = ['id', 'type', 'name', 'technology', 'tags', 'lifecycle', 'parentid', 'shortdescription', 'description', 'notation'];
    const created = [];
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      const get = (n) => { const c = idx(n); return c >= 0 ? (row[c] || '').trim() : ''; };
      const o = makeObject(get('type') || 'softwareSystem', {
        name: get('name') || 'Unnamed',
        technology: get('technology'),
        shortDescription: get('shortdescription'),
        description: get('description'),
        tags: get('tags') ? get('tags').split('|').map((t) => t.trim()).filter(Boolean) : [],
        lifecycle: get('lifecycle') || 'current',
        parentId: get('parentid') || null,
      });
      if (get('id')) o.id = get('id');
      // unknown columns → metadata
      header.forEach((h, c) => {
        if (!known.includes(h.toLowerCase()) && row[c]) o.metadata[h] = row[c];
      });
      m.objects[o.id] = o;
      created.push(o.id);
    }
    // Drop everything onto a fresh imported diagram so it's visible.
    const d = makeDiagram({ name: `Imported (${file.name})`, kind: 'freeform', notation: 'mixed' });
    created.forEach((id, i) => { d.nodes[id] = { x: 60 + (i % 5) * 220, y: 60 + Math.floor(i / 5) * 160 }; });
    m.diagrams[d.id] = d;
    m.diagramOrder.push(d.id);
    store.ui.diagramId = d.id;
  });
}

/**
 * Minimal Structurizr DSL importer. Parses person/softwareSystem/container/
 * component declarations and `a -> b "label" "tech"` relationships.
 * Nested blocks set parentId for drill-down.
 */
export async function importStructurizr() {
  const file = await pickFile('.dsl,.txt,text/plain');
  if (!file) return;
  const text = await readFileAsText(file);
  const model = createModel(file.name.replace(/\.[^.]+$/, ''));
  const byIdent = {};
  const stack = [];
  const elementRe = /^([A-Za-z_][\w]*)\s*=\s*(person|softwareSystem|container|component|database)\s+"([^"]*)"(?:\s+"([^"]*)")?(?:\s+"([^"]*)")?\s*\{?/;
  const relRe = /^([A-Za-z_][\w]*)\s*->\s*([A-Za-z_][\w]*)\s*(?:"([^"]*)")?\s*(?:"([^"]*)")?/;
  const pending = [];

  for (let raw of text.split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#') || line.startsWith('//')) continue;
    const em = elementRe.exec(line);
    if (em) {
      const [, ident, kw, name, desc, tech] = em;
      const typeMap = { person: 'person', softwareSystem: 'softwareSystem', container: 'container', component: 'component', database: 'database' };
      const o = makeObject(typeMap[kw], { name, shortDescription: desc || '', technology: tech || '', parentId: stack[stack.length - 1] || null });
      model.objects[o.id] = o;
      byIdent[ident] = o.id;
      if (line.includes('{')) stack.push(o.id);
      continue;
    }
    const rm = relRe.exec(line);
    if (rm && !line.includes('=')) {
      pending.push({ s: rm[1], t: rm[2], label: rm[3] || '', tech: rm[4] || '' });
      continue;
    }
    if (line === '}' && stack.length) stack.pop();
  }
  for (const p of pending) {
    const s = byIdent[p.s], t = byIdent[p.t];
    if (s && t) {
      const r = makeRelationship(s, t, 'uses', { label: p.label, technology: p.tech });
      model.relationships[r.id] = r;
    }
  }
  // Build a context diagram with the systems/people.
  const top = Object.values(model.objects).filter((o) => !o.parentId);
  const d = makeDiagram({ name: 'Imported Context', kind: 'c4-context', notation: 'c4', level: 'context' });
  top.forEach((o, i) => { d.nodes[o.id] = { x: 80 + (i % 4) * 220, y: 80 + Math.floor(i / 4) * 200 }; });
  model.diagrams[d.id] = d;
  model.diagramOrder.push(d.id);

  const warnings = store.replaceModel(model);
  if (!top.length) alert('No top-level elements parsed — check the DSL syntax.');
  return warnings;
}
