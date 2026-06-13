// Application entry point. Builds the shell, wires the store to the UI, sets up
// hash routing, keyboard shortcuts, and the high-level operations the panels call.

import { store } from './store.js';
import { el, clone, snap } from './util.js';
import { Canvas } from './canvas/canvas.js';
import { TopBar, DiagramTabs } from './ui/topbar.js';
import { LeftPanel } from './ui/leftPanel.js';
import { RightPanel } from './ui/rightPanel.js';
import { CommandPalette } from './ui/commandPalette.js';
import { DIAGRAM_KINDS } from './model.js';
import { sampleMicroservices } from './templates.js';

class App {
  constructor() {
    this.buildShell();
    this.canvas = new Canvas(this.canvasHost);
    this.topbar = new TopBar(this.topbarHost, this);
    this.tabs = new DiagramTabs(this.tabsHost, this);
    this.left = new LeftPanel(this.leftHost, this);
    this.right = new RightPanel(this.rightHost, this);
    this.commandPalette = new CommandPalette(this);
    this.canvas.onContextMenu = (e, target) => this.showContextMenu(e, target);

    this.bootstrap();
    store.subscribe((reason) => this.onStoreChange(reason));
    this.bindGlobalKeys();
    window.addEventListener('hashchange', () => this.applyRoute());
    window.addEventListener('resize', () => this.canvas.render());
    this.renderAll();
  }

  buildShell() {
    const app = el('div', { class: 'app' });
    this.topbarHost = el('header', { class: 'topbar' });
    this.tabsHost = el('div', { class: 'diagram-tabs' });
    const main = el('div', { class: 'main' });
    this.leftHost = el('aside', { class: 'left-panel' });
    this.canvasHost = el('div', { class: 'canvas-host' });
    this.rightHost = el('aside', { class: 'right-panel' });

    // Collapse handles
    this.leftToggle = el('button', { class: 'panel-toggle left', title: 'Toggle left panel (Ctrl+\\)', text: '‹', onclick: () => store.setUi({ leftCollapsed: !store.ui.leftCollapsed }) });
    this.rightToggle = el('button', { class: 'panel-toggle right', title: 'Toggle right panel', text: '›', onclick: () => store.setUi({ rightCollapsed: !store.ui.rightCollapsed }) });

    main.append(this.leftHost, this.leftToggle, this.canvasHost, this.rightToggle, this.rightHost);
    app.append(this.topbarHost, this.tabsHost, main);
    document.getElementById('root').appendChild(app);
    this.appEl = app;
  }

  bootstrap() {
    const loaded = store.load();
    if (!loaded || !store.model.diagramOrder.length) {
      // First run: seed with the microservices sample so the canvas isn't empty.
      const warnings = store.replaceModel(sampleMicroservices());
      void warnings;
    }
    if (!store.ui.diagramId) store.ui.diagramId = store.model.diagramOrder[0] || null;
    this.applyRoute(true);
    setTimeout(() => this.canvas.fitToView(), 50);
  }

  // -- routing (hash-based, GitHub Pages safe) ------------------------------
  applyRoute(initial = false) {
    const hash = location.hash.replace(/^#\/?/, '');
    const [key, id] = hash.split('/');
    if (key === 'diagram' && id && store.model.diagrams[id]) {
      if (store.ui.diagramId !== id) store.setUi({ diagramId: id, selection: [] });
    } else if (initial && store.ui.diagramId) {
      this.syncRoute();
    }
  }
  syncRoute() {
    if (store.ui.diagramId) {
      const want = `#/diagram/${store.ui.diagramId}`;
      if (location.hash !== want) history.replaceState(null, '', want);
    }
  }

  // -- store → UI -----------------------------------------------------------
  onStoreChange(reason) {
    if (reason === 'move') { this.canvas.render(); return; }
    this.syncRoute();
    this.renderAll();
  }

  renderAll() {
    document.documentElement.dataset.theme = store.model.settings.theme;
    this.appEl.classList.toggle('left-collapsed', store.ui.leftCollapsed);
    this.appEl.classList.toggle('right-collapsed', store.ui.rightCollapsed);
    this.appEl.classList.toggle('fullscreen', store.ui.fullscreen);
    this.topbar.render();
    this.tabs.render();
    if (!store.ui.leftCollapsed) this.left.render();
    if (!store.ui.rightCollapsed) this.right.render();
    this.canvas.render();
  }

  // -- operations called by panels -----------------------------------------
  createAtCentre(type) {
    if (!store.diagram) return null;
    const { x, y } = this._centreWorld();
    const id = store.addObjectToDiagram(type, x - 90, y - 55);
    return id;
  }
  addExistingToCentre(objectId) {
    const { x, y } = this._centreWorld();
    store.placeExistingObject(objectId, x - 90, y - 55);
  }
  _centreWorld() {
    const rect = this.canvasHost.getBoundingClientRect();
    const w = this.canvas.screenToWorld(rect.left + rect.width / 2, rect.top + rect.height / 2);
    const gs = store.model.settings.gridSize;
    return store.model.settings.snapToGrid ? { x: snap(w.x, gs), y: snap(w.y, gs) } : w;
  }

  jumpToObject(objectId) {
    // Switch to a diagram containing it (or add to current), select and centre.
    let d = store.diagram;
    if (!d || !d.nodes[objectId]) {
      const containing = Object.values(store.model.diagrams).find((dg) => dg.nodes[objectId]);
      if (containing) { store.setUi({ diagramId: containing.id, selection: [objectId], selectionKind: 'object' }); d = containing; }
      else { this.addExistingToCentre(objectId); store.setUi({ selection: [objectId], selectionKind: 'object' }); return; }
    } else {
      store.setUi({ selection: [objectId], selectionKind: 'object' });
    }
    setTimeout(() => {
      const n = store.diagram.nodes[objectId];
      if (n) {
        const rect = this.canvasHost.getBoundingClientRect();
        const zoom = store.diagram.viewport.zoom;
        this.canvas.setVp({ x: rect.width / 2 - (n.x + 90) * zoom, y: rect.height / 2 - (n.y + 55) * zoom });
      }
    }, 20);
  }

  toggleTagFilter(name) {
    const d = store.diagram; if (!d) return;
    const tags = d.filters.tags.includes(name) ? d.filters.tags.filter((t) => t !== name) : [...d.filters.tags, name];
    store.updateDiagram(d.id, { filters: { ...d.filters, tags } });
  }
  toggleLayerFilter(id) {
    const d = store.diagram; if (!d) return;
    const layers = d.filters.layers.includes(id) ? d.filters.layers.filter((l) => l !== id) : [...d.filters.layers, id];
    store.updateDiagram(d.id, { filters: { ...d.filters, layers } });
  }

  // -- layout helpers -------------------------------------------------------
  autoLayout() {
    const d = store.diagram; if (!d) return;
    const ids = Object.keys(d.nodes);
    if (!ids.length) return;
    store.beginInteraction('Auto-layout');
    // Simple layered layout: rank by relationship depth (sources before targets).
    const indeg = Object.fromEntries(ids.map((id) => [id, 0]));
    const adj = Object.fromEntries(ids.map((id) => [id, []]));
    for (const r of Object.values(store.model.relationships)) {
      if (d.nodes[r.source] && d.nodes[r.target] && r.source !== r.target) {
        adj[r.source].push(r.target); indeg[r.target]++;
      }
    }
    const layers = [];
    let frontier = ids.filter((id) => indeg[id] === 0);
    const placed = new Set();
    const localIndeg = { ...indeg };
    while (frontier.length) {
      layers.push(frontier);
      frontier.forEach((id) => placed.add(id));
      const next = [];
      for (const id of frontier) for (const t of adj[id]) { if (--localIndeg[t] === 0 && !placed.has(t)) next.push(t); }
      frontier = next;
    }
    const leftover = ids.filter((id) => !placed.has(id));
    if (leftover.length) layers.push(leftover);
    const colW = 260, rowH = 170;
    layers.forEach((layer, li) => {
      layer.forEach((id, idx) => {
        d.nodes[id].x = 80 + idx * colW;
        d.nodes[id].y = 60 + li * rowH;
      });
    });
    store._persist();
    store.emit('layout');
    setTimeout(() => this.canvas.fitToView(), 20);
  }

  align(edge) {
    const ids = store.ui.selection.filter((id) => store.diagram?.nodes[id]);
    if (ids.length < 2) return;
    store.beginInteraction('Align');
    const nodes = ids.map((id) => store.diagram.nodes[id]);
    if (edge === 'left') { const x = Math.min(...nodes.map((n) => n.x)); nodes.forEach((n) => n.x = x); }
    if (edge === 'top') { const y = Math.min(...nodes.map((n) => n.y)); nodes.forEach((n) => n.y = y); }
    store._persist(); store.emit('align');
  }
  distribute(axis) {
    const ids = store.ui.selection.filter((id) => store.diagram?.nodes[id]);
    if (ids.length < 3) return;
    store.beginInteraction('Distribute');
    const nodes = ids.map((id) => store.diagram.nodes[id]).sort((a, b) => axis === 'h' ? a.x - b.x : a.y - b.y);
    const min = axis === 'h' ? nodes[0].x : nodes[0].y;
    const max = axis === 'h' ? nodes[nodes.length - 1].x : nodes[nodes.length - 1].y;
    const step = (max - min) / (nodes.length - 1);
    nodes.forEach((n, i) => { if (axis === 'h') n.x = min + i * step; else n.y = min + i * step; });
    store._persist(); store.emit('distribute');
  }

  // -- diagrams -------------------------------------------------------------
  newDiagramDialog() {
    this.showModal('New diagram', (body, close) => {
      const name = el('input', { type: 'text', value: 'New diagram', class: 'modal-input' });
      const kind = el('select', { class: 'modal-input' });
      for (const [value, def] of Object.entries(DIAGRAM_KINDS)) kind.appendChild(el('option', { value, text: def.label }));
      body.append(labelled('Name', name), labelled('Type', kind));
      const create = el('button', { class: 'btn primary', text: 'Create', onclick: () => {
        const def = DIAGRAM_KINDS[kind.value];
        const id = store.addDiagram({ name: name.value || def.label, kind: kind.value, notation: def.notation, level: def.level });
        store.setUi({ diagramId: id, selection: [] });
        close();
      } });
      body.appendChild(el('div', { class: 'modal-actions' }, [create]));
      setTimeout(() => name.select(), 0);
    });
  }

  duplicateDiagram(id) {
    const src = store.model.diagrams[id];
    if (!src) return;
    store.commit('Duplicate diagram', (m) => {
      const copy = clone(src);
      copy.id = 'dgm_' + Math.random().toString(36).slice(2, 8);
      copy.name = src.name + ' (copy)';
      m.diagrams[copy.id] = copy;
      m.diagramOrder.push(copy.id);
      store.ui.diagramId = copy.id;
    });
  }

  loadTemplate(template) {
    const warnings = store.replaceModel(template.build());
    store.setUi({ leftTab: 'palette', selection: [] });
    if (warnings?.length) console.warn(warnings);
    setTimeout(() => this.canvas.fitToView(), 30);
  }

  // -- versioning -----------------------------------------------------------
  snapshotVersion() {
    const name = prompt('Snapshot name:', `Snapshot ${new Date().toLocaleString()}`);
    if (!name) return;
    store.commit('Snapshot version', (m) => {
      const snap = clone(m); delete snap.versions;
      const id = 'ver_' + Math.random().toString(36).slice(2, 8);
      m.versions[id] = { id, name, createdAt: new Date().toISOString(), note: '', snapshot: snap };
    });
    alert(`Snapshot "${name}" saved.`);
  }

  restoreVersion(id) {
    const v = store.model.versions[id];
    if (!v || !confirm(`Restore "${v.name}"? Current versions list is preserved.`)) return;
    const versions = clone(store.model.versions);
    store.replaceModel({ ...clone(v.snapshot), versions: {} });
    store.commit('Keep versions', (m) => { m.versions = versions; });
  }

  compareVersion(id) {
    const v = store.model.versions[id];
    if (!v) return;
    const diff = this._diffModels(v.snapshot, store.model);
    this.showModal(`Compare with "${v.name}"`, (body) => {
      body.appendChild(el('p', { class: 'muted', text: `Snapshot taken ${new Date(v.createdAt).toLocaleString()}.` }));
      const section = (title, items, cls) => {
        body.appendChild(el('h4', { class: 'diff-title ' + cls, text: `${title} (${items.length})` }));
        const ul = el('ul', { class: 'diff-list' });
        for (const it of items.slice(0, 100)) ul.appendChild(el('li', { class: cls, text: it }));
        body.appendChild(ul);
      };
      section('Added', diff.added, 'added');
      section('Removed', diff.removed, 'removed');
      section('Changed', diff.changed, 'changed');
    });
  }

  _diffModels(oldM, newM) {
    const added = [], removed = [], changed = [];
    const name = (o) => o?.name || o?.label || '(unnamed)';
    for (const id of Object.keys(newM.objects)) {
      if (!oldM.objects[id]) added.push(`Element: ${name(newM.objects[id])}`);
      else if (JSON.stringify(oldM.objects[id]) !== JSON.stringify(newM.objects[id])) changed.push(`Element: ${name(newM.objects[id])}`);
    }
    for (const id of Object.keys(oldM.objects)) if (!newM.objects[id]) removed.push(`Element: ${name(oldM.objects[id])}`);
    for (const id of Object.keys(newM.relationships)) {
      if (!oldM.relationships[id]) added.push(`Relationship: ${name(newM.relationships[id]) || id}`);
    }
    for (const id of Object.keys(oldM.relationships)) if (!newM.relationships[id]) removed.push(`Relationship: ${id}`);
    return { added, removed, changed };
  }

  // -- view toggles ---------------------------------------------------------
  toggleFullscreen() { store.setUi({ fullscreen: !store.ui.fullscreen }); setTimeout(() => this.canvas.render(), 50); }

  // -- context menu ---------------------------------------------------------
  showContextMenu(e, target) {
    document.querySelectorAll('.context-menu').forEach((m) => m.remove());
    const items = [];
    if (target.kind === 'object') {
      const obj = store.model.objects[target.id];
      items.push({ label: 'Edit', action: () => store.setUi({ selection: [target.id], selectionKind: 'object' }) });
      if (['softwareSystem', 'container', 'component'].includes(obj.type)) {
        items.push({ label: `Drill into ${obj.name}`, action: () => this.canvas._drill(target.id) });
        items.push({ label: 'Add child element', action: () => this._addChild(target.id) });
      }
      items.push({ label: 'Remove from view', action: () => store.removeFromDiagram(target.id) });
      items.push({ label: 'Delete from model', action: () => { if (confirm('Delete from model?')) store.deleteObject(target.id); } });
    } else if (target.kind === 'relationship') {
      items.push({ label: 'Edit', action: () => store.setUi({ selection: [target.id], selectionKind: 'relationship' }) });
      items.push({ label: 'Add as flow step', action: () => this._quickFlowStep(target.id) });
      items.push({ label: 'Delete', action: () => store.deleteRelationship(target.id) });
    } else {
      items.push({ label: 'Fit to view', action: () => this.canvas.fitToView() });
      items.push({ label: 'Auto-layout', action: () => this.autoLayout() });
      items.push({ label: 'New diagram…', action: () => this.newDiagramDialog() });
    }
    const menu = el('div', { class: 'context-menu', style: { left: `${e.clientX}px`, top: `${e.clientY}px` } });
    for (const it of items) menu.appendChild(el('button', { class: 'context-item', text: it.label, onclick: () => { it.action(); menu.remove(); } }));
    document.body.appendChild(menu);
    const close = () => { menu.remove(); document.removeEventListener('pointerdown', close); };
    setTimeout(() => document.addEventListener('pointerdown', close), 0);
  }

  _addChild(parentId) {
    const parent = store.model.objects[parentId];
    const childType = { softwareSystem: 'container', container: 'component', component: 'component' }[parent.type] || 'component';
    const { x, y } = this._centreWorld();
    const id = store.addObjectToDiagram(childType, x, y, { parentId, name: `New ${childType}` });
    store.setUi({ selection: [id], selectionKind: 'object' });
  }

  _quickFlowStep(relId) {
    const d = store.diagram;
    let flow = Object.values(store.model.flows).find((f) => f.diagramId === d.id);
    store.commit('Flow step', (m) => {
      if (!flow) { const f = makeDiagramFlow(d.id); m.flows[f.id] = f; flow = f; }
      m.flows[flow.id].steps.push({ relationshipId: relId, label: '', description: '' });
      store.ui.activeFlow = flow.id; store.ui.flowStep = m.flows[flow.id].steps.length - 1; store.ui.leftTab = 'flows';
    });
  }

  // -- modal ----------------------------------------------------------------
  showModal(title, builder) {
    const overlay = el('div', { class: 'modal-overlay' });
    const box = el('div', { class: 'modal-box' });
    box.appendChild(el('div', { class: 'modal-head' }, [el('h3', { text: title }), el('button', { class: 'chip-x', text: '×', onclick: () => overlay.remove() })]));
    const body = el('div', { class: 'modal-body' });
    box.appendChild(body);
    overlay.appendChild(box);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
    document.body.appendChild(overlay);
    builder(body, () => overlay.remove());
  }

  // -- keyboard -------------------------------------------------------------
  bindGlobalKeys() {
    window.addEventListener('keydown', (e) => {
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName) || document.activeElement?.isContentEditable;
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); this.commandPalette.open(); return; }
      if (this.commandPalette.isOpen) return;
      if (typing) return;
      const mod = e.ctrlKey || e.metaKey;
      if (mod && e.key.toLowerCase() === 'z' && !e.shiftKey) { e.preventDefault(); store.undo(); }
      else if (mod && (e.key.toLowerCase() === 'y' || (e.key.toLowerCase() === 'z' && e.shiftKey))) { e.preventDefault(); store.redo(); }
      else if (mod && e.key.toLowerCase() === 's') { e.preventDefault(); import('./io/exporters.js').then((m) => m.exportJson()); }
      else if (mod && e.key === '\\') { e.preventDefault(); store.setUi({ leftCollapsed: !store.ui.leftCollapsed }); }
      else if (e.key === 'Delete' || e.key === 'Backspace') { this._deleteSelection(); }
      else if (e.key === 'v' || e.key === 'V') { store.setUi({ tool: 'select' }); }
      else if (e.key === 'c' || e.key === 'C') { store.setUi({ tool: 'connect' }); }
      else if (e.key === 'f') { this.canvas.fitToView(); }
      else if (e.key === 'F') { this.toggleFullscreen(); }
      else if (e.key === 'Escape') { store.setUi({ selection: [], tool: 'select', activeFlow: null, flowStep: -1 }); }
      else if (mod && e.key === 'a') { e.preventDefault(); const ids = Object.keys(store.diagram?.nodes || {}); store.setUi({ selection: ids, selectionKind: ids.length > 1 ? 'multi' : 'object' }); }
      else if (e.key === 'd' && store.ui.selection.length === 1 && store.model.objects[store.ui.selection[0]]) {
        const obj = store.model.objects[store.ui.selection[0]];
        if (['softwareSystem', 'container', 'component'].includes(obj.type)) this.canvas._drill(obj.id);
      }
    });
    // Space-to-pan
    window.addEventListener('keydown', (e) => { if (e.code === 'Space' && !/^(INPUT|TEXTAREA)$/.test(document.activeElement?.tagName)) { this.canvas._spaceDown = true; } });
    window.addEventListener('keyup', (e) => { if (e.code === 'Space') this.canvas._spaceDown = false; });
  }

  _deleteSelection() {
    const sel = store.ui.selection;
    if (!sel.length) return;
    store.commit('Delete selection', (m) => {
      for (const id of sel) {
        if (m.objects[id]) {
          delete m.objects[id];
          for (const [rid, r] of Object.entries(m.relationships)) if (r.source === id || r.target === id) delete m.relationships[rid];
          for (const d of Object.values(m.diagrams)) delete d.nodes[id];
        } else if (m.relationships[id]) {
          delete m.relationships[id];
        }
      }
    });
    store.setUi({ selection: [] });
  }
}

function labelled(label, input) {
  return el('label', { class: 'field' }, [el('span', { class: 'field-label', text: label }), input]);
}

function makeDiagramFlow(diagramId) {
  return { id: 'flow_' + Math.random().toString(36).slice(2, 8), name: 'Flow', description: '', diagramId, steps: [] };
}

// boot
window.addEventListener('DOMContentLoaded', () => { window.__app = new App(); });
