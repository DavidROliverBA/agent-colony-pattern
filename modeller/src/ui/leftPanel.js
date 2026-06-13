// Left panel with tabs: Palette, Tree, Search, Tags/Overlays, Flows, Templates.

import { store } from '../store.js';
import { el } from '../util.js';
import {
  elementDef, paletteGroups, ARCHIMATE_LAYERS,
} from '../notation/index.js';
import { childrenOf, makeFlow } from '../model.js';
import { TEMPLATES } from '../templates.js';

const TABS = [
  { id: 'palette', label: 'Palette', icon: '◧' },
  { id: 'tree', label: 'Model', icon: '☰' },
  { id: 'search', label: 'Search', icon: '⌕' },
  { id: 'overlays', label: 'Tags', icon: '◑' },
  { id: 'flows', label: 'Flows', icon: '➤' },
  { id: 'templates', label: 'Start', icon: '✦' },
];

export class LeftPanel {
  constructor(root, app) {
    this.root = root;
    this.app = app;
    this.searchQuery = '';
    this.recent = [];
  }

  render() {
    this.root.textContent = '';
    const tabs = el('div', { class: 'tab-bar' });
    for (const t of TABS) {
      tabs.appendChild(el('button', {
        class: 'tab' + (store.ui.leftTab === t.id ? ' active' : ''),
        title: t.label,
        onclick: () => store.setUi({ leftTab: t.id }),
        html: `<span class="tab-icon">${t.icon}</span><span class="tab-text">${t.label}</span>`,
      }));
    }
    this.root.appendChild(tabs);
    const body = el('div', { class: 'tab-body' });
    this.root.appendChild(body);

    switch (store.ui.leftTab) {
      case 'palette': this._palette(body); break;
      case 'tree': this._tree(body); break;
      case 'search': this._search(body); break;
      case 'overlays': this._overlays(body); break;
      case 'flows': this._flows(body); break;
      case 'templates': this._templates(body); break;
    }
  }

  // -- palette --------------------------------------------------------------
  _palette(body) {
    const notation = store.diagram?.notation || 'c4';
    const filter = el('input', { class: 'panel-search', type: 'search', placeholder: 'Filter elements…' });
    body.appendChild(filter);

    const switcher = el('div', { class: 'seg' });
    for (const n of ['c4', 'archimate']) {
      switcher.appendChild(el('button', {
        class: 'seg-btn' + ((notation === n || (notation === 'mixed' && n === 'c4')) ? ' active' : ''),
        text: n === 'c4' ? 'C4' : 'ArchiMate',
        onclick: () => { this._paletteNotation = n; this._renderPaletteGroups(groupsHost, n, filter.value); },
      }));
    }
    body.appendChild(switcher);

    if (this.recent.length) {
      const rec = el('div', { class: 'palette-group' });
      rec.appendChild(el('div', { class: 'palette-group-title', text: 'Recently used' }));
      const grid = el('div', { class: 'palette-grid' });
      for (const type of this.recent.slice(0, 6)) grid.appendChild(this._paletteItem(type));
      rec.appendChild(grid);
      body.appendChild(rec);
    }

    const groupsHost = el('div');
    body.appendChild(groupsHost);
    const activeNotation = this._paletteNotation || (notation === 'mixed' ? 'c4' : notation);
    this._renderPaletteGroups(groupsHost, activeNotation, '');
    filter.addEventListener('input', () => this._renderPaletteGroups(groupsHost, this._paletteNotation || activeNotation, filter.value));
  }

  _renderPaletteGroups(host, notation, query) {
    host.textContent = '';
    const q = query.toLowerCase();
    for (const group of paletteGroups(notation)) {
      const items = group.items.filter((type) => !q || elementDef(type).label.toLowerCase().includes(q) || type.toLowerCase().includes(q));
      if (!items.length) continue;
      const g = el('div', { class: 'palette-group' });
      const title = el('div', { class: 'palette-group-title' });
      if (group.color) title.appendChild(el('span', { class: 'group-swatch', style: { background: group.color } }));
      title.appendChild(el('span', { text: group.label }));
      g.appendChild(title);
      const grid = el('div', { class: 'palette-grid' });
      for (const type of items) grid.appendChild(this._paletteItem(type));
      g.appendChild(grid);
      host.appendChild(g);
    }
  }

  _paletteItem(type) {
    const def = elementDef(type);
    const item = el('div', {
      class: 'palette-item', draggable: 'true', title: def.desc || def.label,
      dataset: { type },
    });
    item.appendChild(el('span', { class: 'palette-swatch', style: { background: def.fill, borderColor: def.stroke } }));
    item.appendChild(el('span', { class: 'palette-label', text: def.label }));
    item.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('application/x-element-type', type);
      e.dataTransfer.effectAllowed = 'copy';
    });
    item.addEventListener('dblclick', () => {
      // quick-create at viewport centre
      const id = this.app.createAtCentre(type);
      this._noteRecent(type);
      if (id) store.setUi({ selection: [id], selectionKind: 'object' });
    });
    return item;
  }

  _noteRecent(type) {
    this.recent = [type, ...this.recent.filter((t) => t !== type)].slice(0, 8);
  }

  // -- model tree -----------------------------------------------------------
  _tree(body) {
    const groupBy = el('div', { class: 'seg small' });
    for (const g of ['hierarchy', 'type', 'layer']) {
      groupBy.appendChild(el('button', {
        class: 'seg-btn' + ((this._treeGroup || 'hierarchy') === g ? ' active' : ''),
        text: g[0].toUpperCase() + g.slice(1),
        onclick: () => { this._treeGroup = g; this.render(); },
      }));
    }
    body.appendChild(groupBy);

    const tree = el('div', { class: 'tree' });
    const mode = this._treeGroup || 'hierarchy';
    if (mode === 'hierarchy') {
      const roots = Object.values(store.model.objects).filter((o) => !o.parentId);
      for (const o of roots) tree.appendChild(this._treeNode(o, 0));
    } else if (mode === 'type') {
      const byType = {};
      for (const o of Object.values(store.model.objects)) (byType[o.type] ||= []).push(o);
      for (const [type, objs] of Object.entries(byType)) {
        tree.appendChild(el('div', { class: 'tree-group-title', text: `${elementDef(type).label} (${objs.length})` }));
        for (const o of objs) tree.appendChild(this._treeLeaf(o, 1));
      }
    } else {
      for (const layer of ARCHIMATE_LAYERS) {
        const objs = Object.values(store.model.objects).filter((o) => elementDef(o.type).layer === layer.id);
        if (!objs.length) continue;
        tree.appendChild(el('div', { class: 'tree-group-title', html: `<span class="group-swatch" style="background:${layer.fill}"></span>${layer.label} (${objs.length})` }));
        for (const o of objs) tree.appendChild(this._treeLeaf(o, 1));
      }
      const c4 = Object.values(store.model.objects).filter((o) => elementDef(o.type).notation === 'c4');
      if (c4.length) {
        tree.appendChild(el('div', { class: 'tree-group-title', text: `C4 elements (${c4.length})` }));
        for (const o of c4) tree.appendChild(this._treeLeaf(o, 1));
      }
    }
    if (!Object.keys(store.model.objects).length) tree.appendChild(el('div', { class: 'muted pad', text: 'No elements yet. Drag from the palette or pick a template.' }));
    body.appendChild(tree);
  }

  _treeNode(obj, depth) {
    const wrap = el('div');
    wrap.appendChild(this._treeLeaf(obj, depth));
    const kids = childrenOf(store.model, obj.id);
    for (const k of kids) wrap.appendChild(this._treeNode(k, depth + 1));
    return wrap;
  }

  _treeLeaf(obj, depth) {
    const def = elementDef(obj.type);
    const onDiagram = store.diagram?.nodes[obj.id];
    const row = el('div', {
      class: 'tree-leaf' + (store.ui.selection.includes(obj.id) ? ' selected' : ''),
      style: { paddingLeft: `${8 + depth * 14}px` },
      draggable: 'true',
    });
    row.appendChild(el('span', { class: 'tree-dot', style: { background: def.fill, borderColor: def.stroke } }));
    row.appendChild(el('span', { class: 'tree-name', text: obj.name }));
    if (!onDiagram && store.diagram) {
      row.appendChild(el('button', { class: 'tree-add', title: 'Add to current diagram', text: '+', onclick: (e) => { e.stopPropagation(); this.app.addExistingToCentre(obj.id); } }));
    }
    row.addEventListener('click', () => {
      if (onDiagram) store.setUi({ selection: [obj.id], selectionKind: 'object' });
      else store.setUi({ selection: [obj.id], selectionKind: 'object' });
    });
    row.addEventListener('dragstart', (e) => { e.dataTransfer.setData('application/x-object-id', obj.id); e.dataTransfer.effectAllowed = 'copy'; });
    return row;
  }

  // -- search ---------------------------------------------------------------
  _search(body) {
    const input = el('input', { class: 'panel-search', type: 'search', placeholder: 'Search names, descriptions, tags, tech, metadata…', value: this.searchQuery });
    input.addEventListener('input', () => { this.searchQuery = input.value; this._renderResults(results); });
    body.appendChild(input);
    const results = el('div', { class: 'search-results' });
    body.appendChild(results);
    this._renderResults(results);
    setTimeout(() => input.focus(), 0);
  }

  _renderResults(host) {
    host.textContent = '';
    const q = this.searchQuery.trim().toLowerCase();
    if (!q) { host.appendChild(el('div', { class: 'muted pad', text: 'Type to search the model.' })); return; }
    const matchObjs = Object.values(store.model.objects).filter((o) => objectMatches(o, q));
    const matchRels = Object.values(store.model.relationships).filter((r) => relMatches(r, q));
    if (!matchObjs.length && !matchRels.length) { host.appendChild(el('div', { class: 'muted pad', text: 'No matches.' })); return; }
    for (const o of matchObjs) {
      const def = elementDef(o.type);
      const row = el('button', { class: 'search-row' });
      row.appendChild(el('span', { class: 'tree-dot', style: { background: def.fill } }));
      row.appendChild(el('span', { class: 'search-name', text: o.name }));
      row.appendChild(el('span', { class: 'search-sub', text: def.label }));
      row.addEventListener('click', () => this.app.jumpToObject(o.id));
      host.appendChild(row);
    }
    for (const r of matchRels) {
      const s = store.model.objects[r.source]?.name, t = store.model.objects[r.target]?.name;
      const row = el('button', { class: 'search-row', text: `↔ ${s} → ${t} ${r.label ? '· ' + r.label : ''}` });
      row.addEventListener('click', () => {
        const d = Object.values(store.model.diagrams).find((dg) => dg.nodes[r.source] && dg.nodes[r.target]);
        if (d) store.setUi({ diagramId: d.id, selection: [r.id], selectionKind: 'relationship' });
      });
      host.appendChild(row);
    }
  }

  // -- tags & overlays ------------------------------------------------------
  _overlays(body) {
    const d = store.diagram;
    body.appendChild(el('div', { class: 'panel-hint', text: 'Apply perspectives without duplicating diagrams. Filter dims non-matching elements.' }));

    const groups = {};
    for (const t of Object.values(store.model.tags)) (groups[t.group] ||= []).push(t);

    for (const [group, tags] of Object.entries(groups)) {
      const sec = el('div', { class: 'overlay-group' });
      sec.appendChild(el('div', { class: 'overlay-group-title', text: group }));
      for (const t of tags) {
        const active = d?.filters?.tags?.includes(t.name);
        const row = el('label', { class: 'overlay-row' });
        const cb = el('input', { type: 'checkbox', checked: !!active });
        cb.addEventListener('change', () => this.app.toggleTagFilter(t.name));
        row.append(cb, el('span', { class: 'tree-dot', style: { background: t.color } }), el('span', { text: `${t.name} (${countTag(t.name)})` }));
        sec.appendChild(row);
      }
      body.appendChild(sec);
    }
    if (!Object.keys(store.model.tags).length) body.appendChild(el('div', { class: 'muted pad', text: 'No tags yet. Add tags to elements in the right panel.' }));

    // Layer filter for ArchiMate
    if (d?.notation === 'archimate') {
      const sec = el('div', { class: 'overlay-group' });
      sec.appendChild(el('div', { class: 'overlay-group-title', text: 'Layer filter' }));
      for (const layer of ARCHIMATE_LAYERS) {
        const active = d.filters?.layers?.includes(layer.id);
        const row = el('label', { class: 'overlay-row' });
        const cb = el('input', { type: 'checkbox', checked: !!active });
        cb.addEventListener('change', () => this.app.toggleLayerFilter(layer.id));
        row.append(cb, el('span', { class: 'tree-dot', style: { background: layer.fill } }), el('span', { text: layer.label }));
        sec.appendChild(row);
      }
      body.appendChild(sec);
    }

    if (d?.filters?.tags?.length || d?.filters?.layers?.length) {
      body.appendChild(el('button', { class: 'btn block', text: 'Clear filters', onclick: () => store.updateDiagram(d.id, { filters: { tags: [], layers: [] } }) }));
    }
  }

  // -- flows ----------------------------------------------------------------
  _flows(body) {
    const d = store.diagram;
    body.appendChild(el('div', { class: 'panel-hint', text: 'Flows step through relationships as a narrative overlay — no duplicate diagrams.' }));
    const flows = Object.values(store.model.flows).filter((f) => !f.diagramId || f.diagramId === d?.id);
    for (const f of flows) {
      const card = el('div', { class: 'flow-card' + (store.ui.activeFlow === f.id ? ' active' : '') });
      const head = el('div', { class: 'flow-head' });
      head.appendChild(el('span', { class: 'flow-name', text: f.name }));
      head.appendChild(el('button', { class: 'chip-x', text: '×', onclick: () => { if (confirm('Delete flow?')) store.commit('Delete flow', (m) => delete m.flows[f.id]); } }));
      card.appendChild(head);

      const steps = el('ol', { class: 'flow-steps' });
      f.steps.forEach((s, i) => {
        const rel = store.model.relationships[s.relationshipId];
        const label = rel ? `${store.model.objects[rel.source]?.name} → ${store.model.objects[rel.target]?.name}` : '(missing)';
        const li = el('li', { class: 'flow-step' + (store.ui.activeFlow === f.id && store.ui.flowStep === i ? ' active' : '') });
        li.appendChild(el('span', { class: 'flow-step-label', text: s.label || label }));
        li.addEventListener('click', () => store.setUi({ activeFlow: f.id, flowStep: i }));
        steps.appendChild(li);
      });
      card.appendChild(steps);

      const controls = el('div', { class: 'flow-controls' });
      controls.appendChild(el('button', { class: 'btn small', text: '⏮', title: 'First', onclick: () => store.setUi({ activeFlow: f.id, flowStep: 0 }) }));
      controls.appendChild(el('button', { class: 'btn small', text: '◀', title: 'Prev', onclick: () => store.setUi({ activeFlow: f.id, flowStep: Math.max(0, store.ui.flowStep - 1) }) }));
      controls.appendChild(el('button', { class: 'btn small', text: '▶', title: 'Next', onclick: () => store.setUi({ activeFlow: f.id, flowStep: Math.min(f.steps.length - 1, (store.ui.activeFlow === f.id ? store.ui.flowStep : -1) + 1) }) }));
      controls.appendChild(el('button', { class: 'btn small', text: 'Stop', onclick: () => store.setUi({ activeFlow: null, flowStep: -1 }) }));
      controls.appendChild(el('button', { class: 'btn small', text: '+ step', title: 'Add selected relationship as a step', onclick: () => this._addFlowStep(f.id) }));
      card.appendChild(controls);
      body.appendChild(card);
    }

    body.appendChild(el('button', { class: 'btn block', text: '+ New flow', onclick: () => {
      const name = prompt('Flow name:', 'New flow');
      if (name) store.commit('New flow', (m) => { const f = makeFlow({ name, diagramId: d?.id }); m.flows[f.id] = f; store.ui.activeFlow = f.id; store.ui.flowStep = -1; });
    } }));
    body.appendChild(el('div', { class: 'panel-hint', text: 'Tip: select a relationship on the canvas, then "+ step".' }));
  }

  _addFlowStep(flowId) {
    const sel = store.ui.selection[0];
    if (!sel || !store.model.relationships[sel]) { alert('Select a relationship on the canvas first.'); return; }
    store.commit('Add flow step', (m) => {
      m.flows[flowId].steps.push({ relationshipId: sel, label: '', description: '' });
    });
  }

  // -- templates ------------------------------------------------------------
  _templates(body) {
    body.appendChild(el('div', { class: 'panel-hint', text: 'Start from a blank canvas or a worked sample. This replaces the current workspace.' }));
    const groups = {};
    for (const t of TEMPLATES) (groups[t.group] ||= []).push(t);
    for (const [group, items] of Object.entries(groups)) {
      body.appendChild(el('div', { class: 'palette-group-title', text: group }));
      for (const t of items) {
        body.appendChild(el('button', { class: 'template-row', text: t.name, onclick: () => {
          if (Object.keys(store.model.objects).length && !confirm('Replace current workspace with this template?')) return;
          this.app.loadTemplate(t);
        } }));
      }
    }
  }
}

function objectMatches(o, q) {
  return [o.name, o.shortDescription, o.description, o.technology, o.type, ...o.tags, ...Object.values(o.metadata)]
    .some((v) => String(v || '').toLowerCase().includes(q));
}
function relMatches(r, q) {
  return [r.label, r.technology, r.description, r.type].some((v) => String(v || '').toLowerCase().includes(q));
}
function countTag(name) {
  return Object.values(store.model.objects).filter((o) => o.tags.includes(name)).length;
}
