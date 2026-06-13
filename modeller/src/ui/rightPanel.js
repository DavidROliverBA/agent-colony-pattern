// Right panel: context-sensitive properties editor.
//   - nothing selected  → diagram properties
//   - one object        → object editor (+ relationships, diagrams, comments)
//   - one relationship  → relationship editor
//   - multiple          → bulk operations

import { store } from '../store.js';
import { el, debounce } from '../util.js';
import {
  elementDef, relationshipDef, relationshipDefsFor, allElementDefs,
  ARCHIMATE_VIEWPOINTS, ARCHIMATE_LAYERS,
} from '../notation/index.js';
import {
  diagramsContaining, relationshipsOf, DIAGRAM_KINDS,
} from '../model.js';

export class RightPanel {
  constructor(root, app) {
    this.root = root;
    this.app = app;
  }

  render() {
    this.root.textContent = '';
    const sel = store.ui.selection;
    if (!store.diagram) { this.root.appendChild(el('div', { class: 'panel-empty', text: 'Create or open a diagram to begin.' })); return; }
    if (sel.length === 0) this._diagramProps();
    else if (sel.length === 1 && store.model.objects[sel[0]]) this._objectProps(sel[0]);
    else if (sel.length === 1 && store.model.relationships[sel[0]]) this._relationshipProps(sel[0]);
    else this._bulkProps(sel);
  }

  _section(title) {
    const s = el('div', { class: 'prop-section' });
    s.appendChild(el('h3', { class: 'prop-section-title', text: title }));
    this.root.appendChild(s);
    return s;
  }

  _field(parent, label, value, onChange, opts = {}) {
    const wrap = el('label', { class: 'field' });
    wrap.appendChild(el('span', { class: 'field-label', text: label }));
    let input;
    if (opts.textarea) {
      input = el('textarea', { rows: opts.rows || 3, value: value || '' });
    } else if (opts.select) {
      input = el('select');
      for (const o of opts.options) {
        input.appendChild(el('option', { value: o.value, text: o.label, selected: o.value === value }));
      }
    } else {
      input = el('input', { type: opts.type || 'text', value: value ?? '' });
    }
    const handler = debounce((v) => onChange(v), opts.immediate ? 0 : 250);
    input.addEventListener('input', () => handler(input.value));
    input.addEventListener('change', () => onChange(input.value));
    wrap.appendChild(input);
    parent.appendChild(wrap);
    return input;
  }

  // -- diagram --------------------------------------------------------------
  _diagramProps() {
    const d = store.diagram;
    const s = this._section('Diagram');
    this._field(s, 'Name', d.name, (v) => store.updateDiagram(d.id, { name: v }));
    this._field(s, 'Type', d.kind, (v) => {
      const def = DIAGRAM_KINDS[v];
      store.updateDiagram(d.id, { kind: v, notation: def.notation, level: def.level });
    }, { select: true, options: Object.entries(DIAGRAM_KINDS).map(([value, def]) => ({ value, label: def.label })), immediate: true });
    this._field(s, 'Description', d.description, (v) => store.updateDiagram(d.id, { description: v }), { textarea: true });

    if (d.notation === 'archimate') {
      this._field(s, 'Viewpoint', d.viewpoint, (v) => store.updateDiagram(d.id, { viewpoint: v }),
        { select: true, options: ARCHIMATE_VIEWPOINTS.map((v) => ({ value: v.id, label: v.name })), immediate: true });
    }

    const stats = this._section('Contents');
    const objCount = Object.keys(d.nodes).length;
    stats.appendChild(el('div', { class: 'stat-row', text: `${objCount} elements` }));
    stats.appendChild(el('div', { class: 'stat-row', text: `${this.app.canvas ? '' : ''}${Object.keys(store.model.relationships).length} relationships in model` }));

    const actions = this._section('Actions');
    actions.appendChild(el('button', { class: 'btn block', text: 'Fit to view', onclick: () => this.app.canvas.fitToView() }));
    actions.appendChild(el('button', { class: 'btn block', text: 'Auto-layout', onclick: () => this.app.autoLayout() }));
    actions.appendChild(el('button', { class: 'btn block', text: 'Duplicate diagram', onclick: () => this.app.duplicateDiagram(d.id) }));
    actions.appendChild(el('button', { class: 'btn block danger', text: 'Delete diagram', onclick: () => { if (confirm('Delete this diagram? Model elements are kept.')) store.deleteDiagram(d.id); } }));
  }

  // -- object ---------------------------------------------------------------
  _objectProps(id) {
    const o = store.model.objects[id];
    const def = elementDef(o.type);
    const s = this._section('Element');
    s.appendChild(el('div', { class: 'type-chip', dataset: { notation: def.notation }, text: `${def.label} · ${def.notation.toUpperCase()}` }));
    this._field(s, 'Name', o.name, (v) => store.updateObject(id, { name: v }));
    this._field(s, 'Type', o.type, (v) => store.updateObject(id, { type: v }),
      { select: true, immediate: true, options: groupedElementOptions() });
    this._field(s, 'Short description', o.shortDescription, (v) => store.updateObject(id, { shortDescription: v }));
    this._field(s, 'Detailed description', o.description, (v) => store.updateObject(id, { description: v }), { textarea: true, rows: 4 });
    this._field(s, 'Technology', o.technology, (v) => store.updateObject(id, { technology: v }));
    this._field(s, 'Lifecycle', o.lifecycle, (v) => store.updateObject(id, { lifecycle: v }),
      { select: true, immediate: true, options: ['current', 'future', 'proposed', 'removed'].map((x) => ({ value: x, label: x })) });

    this._tagsEditor(this._section('Tags'), o, (tags) => store.updateObject(id, { tags }));
    this._linksEditor(this._section('Links'), o, (links) => store.updateObject(id, { links }));
    this._metadataEditor(this._section('Custom metadata'), o, (metadata) => store.updateObject(id, { metadata }));

    // Relationships
    const rs = this._section('Relationships');
    const rels = relationshipsOf(store.model, id);
    if (!rels.length) rs.appendChild(el('div', { class: 'muted', text: 'No relationships.' }));
    for (const r of rels) {
      const other = r.source === id ? store.model.objects[r.target] : store.model.objects[r.source];
      const dir = r.source === id ? '→' : '←';
      rs.appendChild(el('button', {
        class: 'list-row', text: `${dir} ${other?.name || '?'} (${relationshipDef(r.type).label})`,
        onclick: () => store.setUi({ selection: [r.id], selectionKind: 'relationship' }),
      }));
    }

    // Diagrams containing this object
    const ds = this._section('Appears in diagrams');
    for (const d of diagramsContaining(store.model, id)) {
      ds.appendChild(el('button', {
        class: 'list-row', text: d.name,
        onclick: () => store.setUi({ diagramId: d.id, selection: [id] }),
      }));
    }

    this._commentsEditor(this._section('Comments'), id);

    const actions = this._section('Actions');
    if (store.diagram?.nodes[id]) actions.appendChild(el('button', { class: 'btn block', text: 'Remove from this view', onclick: () => store.removeFromDiagram(id) }));
    actions.appendChild(el('button', { class: 'btn block danger', text: 'Delete from model', onclick: () => { if (confirm('Delete from the entire model? Removes it from all diagrams.')) store.deleteObject(id); } }));
  }

  // -- relationship ---------------------------------------------------------
  _relationshipProps(id) {
    const r = store.model.relationships[id];
    const s = this._section('Relationship');
    const objOptions = Object.values(store.model.objects).map((o) => ({ value: o.id, label: o.name }));
    this._field(s, 'Source', r.source, (v) => store.updateRelationship(id, { source: v }), { select: true, immediate: true, options: objOptions });
    this._field(s, 'Target', r.target, (v) => store.updateRelationship(id, { target: v }), { select: true, immediate: true, options: objOptions });
    const notation = store.diagram?.notation;
    this._field(s, 'Type', r.type, (v) => store.updateRelationship(id, { type: v }),
      { select: true, immediate: true, options: relationshipDefsFor(notation).map((x) => ({ value: x.type, label: x.label })) });
    this._field(s, 'Label', r.label, (v) => store.updateRelationship(id, { label: v }));
    this._field(s, 'Technology / protocol', r.technology, (v) => store.updateRelationship(id, { technology: v }));
    this._field(s, 'Direction', r.direction, (v) => store.updateRelationship(id, { direction: v }),
      { select: true, immediate: true, options: [{ value: 'forward', label: 'Forward →' }, { value: 'bidirectional', label: 'Bidirectional ↔' }, { value: 'none', label: 'None —' }] });
    this._field(s, 'Notes', r.description, (v) => store.updateRelationship(id, { description: v }), { textarea: true });
    this._field(s, 'Lifecycle', r.lifecycle, (v) => store.updateRelationship(id, { lifecycle: v }),
      { select: true, immediate: true, options: ['current', 'future', 'proposed', 'removed'].map((x) => ({ value: x, label: x })) });

    const actions = this._section('Actions');
    actions.appendChild(el('button', { class: 'btn block danger', text: 'Delete relationship', onclick: () => store.deleteRelationship(id) }));
  }

  // -- bulk -----------------------------------------------------------------
  _bulkProps(ids) {
    const objs = ids.filter((id) => store.model.objects[id]);
    const s = this._section(`${ids.length} items selected`);
    s.appendChild(el('div', { class: 'muted', text: `${objs.length} elements selected.` }));

    const tagWrap = this._section('Add tag to all');
    this._tagSelector(tagWrap, (tagName) => {
      store.commit('Bulk tag', (m) => {
        for (const id of objs) {
          const o = m.objects[id];
          if (o && !o.tags.includes(tagName)) o.tags.push(tagName);
        }
      });
    });

    const life = this._section('Set lifecycle for all');
    this._field(life, 'Lifecycle', 'current', (v) => {
      store.commit('Bulk lifecycle', (m) => { for (const id of objs) if (m.objects[id]) m.objects[id].lifecycle = v; });
    }, { select: true, immediate: true, options: ['current', 'future', 'proposed', 'removed'].map((x) => ({ value: x, label: x })) });

    const actions = this._section('Actions');
    actions.appendChild(el('button', { class: 'btn block', text: 'Align left', onclick: () => this.app.align('left') }));
    actions.appendChild(el('button', { class: 'btn block', text: 'Align top', onclick: () => this.app.align('top') }));
    actions.appendChild(el('button', { class: 'btn block', text: 'Distribute horizontally', onclick: () => this.app.distribute('h') }));
    actions.appendChild(el('button', { class: 'btn block', text: 'Remove all from view', onclick: () => { store.commit('Remove from view', (m) => { for (const id of objs) delete m.diagrams[store.ui.diagramId].nodes[id]; }); store.setUi({ selection: [] }); } }));
  }

  // -- reusable editors -----------------------------------------------------
  _tagsEditor(parent, owner, onChange) {
    const list = el('div', { class: 'chip-list' });
    for (const t of owner.tags) {
      const def = Object.values(store.model.tags).find((x) => x.name === t);
      const chip = el('span', { class: 'chip', style: def ? { borderColor: def.color, color: def.color } : {} });
      chip.appendChild(el('span', { text: t }));
      chip.appendChild(el('button', { class: 'chip-x', text: '×', onclick: () => onChange(owner.tags.filter((x) => x !== t)) }));
      list.appendChild(chip);
    }
    parent.appendChild(list);
    this._tagSelector(parent, (name) => { if (!owner.tags.includes(name)) onChange([...owner.tags, name]); });
  }

  _tagSelector(parent, onPick) {
    const row = el('div', { class: 'inline-row' });
    const input = el('input', { type: 'text', placeholder: 'Add tag…', list: 'tag-suggestions' });
    const dl = el('datalist', { id: 'tag-suggestions' });
    for (const t of Object.values(store.model.tags)) dl.appendChild(el('option', { value: t.name }));
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && input.value.trim()) {
        const name = input.value.trim();
        if (!Object.values(store.model.tags).some((t) => t.name === name)) {
          store.commit('Create tag', (m) => { const t = { id: 'tag_' + Math.random().toString(36).slice(2, 8), name, color: randomColor(name), group: 'general' }; m.tags[t.id] = t; });
        }
        onPick(name); input.value = '';
      }
    });
    row.append(input, dl);
    parent.appendChild(row);
  }

  _linksEditor(parent, owner, onChange) {
    for (const link of owner.links) {
      const row = el('div', { class: 'inline-row' });
      row.appendChild(el('a', { href: link.url, target: '_blank', rel: 'noopener noreferrer', class: 'link-row', text: link.label || link.url }));
      row.appendChild(el('button', { class: 'chip-x', text: '×', onclick: () => onChange(owner.links.filter((l) => l !== link)) }));
      parent.appendChild(row);
    }
    const row = el('div', { class: 'inline-row' });
    const label = el('input', { type: 'text', placeholder: 'Label' });
    const url = el('input', { type: 'text', placeholder: 'https://…' });
    const add = el('button', { class: 'btn small', text: 'Add', onclick: () => {
      if (url.value.trim()) { onChange([...owner.links, { label: label.value.trim(), url: url.value.trim() }]); label.value = ''; url.value = ''; }
    } });
    row.append(label, url, add);
    parent.appendChild(row);
  }

  _metadataEditor(parent, owner, onChange) {
    for (const [k, v] of Object.entries(owner.metadata)) {
      const row = el('div', { class: 'inline-row' });
      row.appendChild(el('span', { class: 'meta-key', text: k }));
      const val = el('input', { type: 'text', value: v });
      val.addEventListener('change', () => onChange({ ...owner.metadata, [k]: val.value }));
      row.appendChild(val);
      row.appendChild(el('button', { class: 'chip-x', text: '×', onclick: () => { const m = { ...owner.metadata }; delete m[k]; onChange(m); } }));
      parent.appendChild(row);
    }
    const row = el('div', { class: 'inline-row' });
    const key = el('input', { type: 'text', placeholder: 'Key' });
    const value = el('input', { type: 'text', placeholder: 'Value' });
    const add = el('button', { class: 'btn small', text: 'Add', onclick: () => {
      if (key.value.trim()) { onChange({ ...owner.metadata, [key.value.trim()]: value.value }); key.value = ''; value.value = ''; }
    } });
    row.append(key, value, add);
    parent.appendChild(row);
  }

  _commentsEditor(parent, objectId) {
    const comments = Object.values(store.model.comments).filter((c) => c.objectId === objectId);
    for (const c of comments) {
      const row = el('div', { class: 'comment' });
      row.appendChild(el('div', { class: 'comment-body', text: c.body }));
      row.appendChild(el('div', { class: 'comment-meta', text: new Date(c.createdAt).toLocaleString() }));
      parent.appendChild(row);
    }
    const ta = el('textarea', { rows: 2, placeholder: 'Add a comment…' });
    parent.appendChild(ta);
    parent.appendChild(el('button', { class: 'btn small', text: 'Comment', onclick: () => {
      if (ta.value.trim()) {
        store.commit('Add comment', (m) => { const id = 'cmt_' + Math.random().toString(36).slice(2, 8); m.comments[id] = { id, objectId, body: ta.value.trim(), createdAt: new Date().toISOString() }; });
        ta.value = '';
      }
    } }));
  }
}

function groupedElementOptions() {
  return allElementDefs().map((d) => ({ value: d.type, label: `${d.label} (${d.notation})` }));
}

function randomColor(seed) {
  let h = 0; for (const ch of seed) h = (h * 31 + ch.charCodeAt(0)) % 360;
  return `hsl(${h} 65% 45%)`;
}
