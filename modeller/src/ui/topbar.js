// Top navigation bar: workspace name, diagram tabs, drill-down breadcrumb,
// tools, undo/redo, zoom, import/export menu, versions, and view toggles.

import { store } from '../store.js';
import { el, downloadFile } from '../util.js';
import { DIAGRAM_KINDS } from '../model.js';
import {
  exportPng, exportSvg, exportPdf, exportJson, exportCsv, exportC4Dsl, exportArchimateExchange,
} from '../io/exporters.js';
import { importJson, importCsv, importStructurizr } from '../io/importers.js';

export class TopBar {
  constructor(root, app) {
    this.root = root;
    this.app = app;
    this.menuOpen = null;
  }

  render() {
    this.root.textContent = '';

    // Brand + workspace name
    const left = el('div', { class: 'tb-group' });
    left.appendChild(el('div', { class: 'brand', text: 'ArchModeller' }));
    const nameInput = el('input', { class: 'workspace-name', value: store.model.name, title: 'Workspace name' });
    nameInput.addEventListener('change', () => store.commit('Rename workspace', (m) => { m.name = nameInput.value; }));
    left.appendChild(nameInput);
    this.root.appendChild(left);

    // Menus
    const menus = el('div', { class: 'tb-group' });
    menus.appendChild(this._menu('File', [
      { label: 'New workspace', action: () => { if (confirm('Start a new empty workspace?')) store.newWorkspace('Untitled workspace'); } },
      { label: 'New diagram…', action: () => this.app.newDiagramDialog() },
      { sep: true },
      { label: 'Import JSON (replace)…', action: () => importJson(false) },
      { label: 'Import JSON (merge)…', action: () => importJson(true) },
      { label: 'Import CSV…', action: () => importCsv() },
      { label: 'Import Structurizr DSL…', action: () => importStructurizr() },
      { sep: true },
      { label: 'Save (download JSON)', action: () => exportJson() },
    ]));
    menus.appendChild(this._menu('Export', [
      { label: 'PNG (current diagram)', action: () => exportPng() },
      { label: 'SVG (current diagram)', action: () => exportSvg() },
      { label: 'PDF (print dialog)', action: () => exportPdf() },
      { sep: true },
      { label: 'JSON model', action: () => exportJson() },
      { label: 'CSV (objects + relationships)', action: () => exportCsv() },
      { label: 'C4 DSL (Structurizr-style)', action: () => exportC4Dsl() },
      { label: 'ArchiMate Exchange XML', action: () => exportArchimateExchange() },
    ]));
    menus.appendChild(this._menu('Versions', this._versionItems()));
    this.root.appendChild(menus);

    // Spacer with breadcrumb
    this.root.appendChild(this._breadcrumb());

    // Right-side tools
    const tools = el('div', { class: 'tb-group right' });
    tools.appendChild(this._toolBtn('↶', 'Undo (Ctrl+Z)', () => store.undo(), !store.canUndo()));
    tools.appendChild(this._toolBtn('↷', 'Redo (Ctrl+Shift+Z)', () => store.redo(), !store.canRedo()));
    tools.appendChild(el('span', { class: 'tb-sep' }));
    tools.appendChild(this._toolBtn('⌖', 'Select / move (V)', () => store.setUi({ tool: 'select' }), false, store.ui.tool === 'select'));
    tools.appendChild(this._toolBtn('⤳', 'Connect (C)', () => store.setUi({ tool: 'connect' }), false, store.ui.tool === 'connect'));
    tools.appendChild(el('span', { class: 'tb-sep' }));
    tools.appendChild(this._toolBtn('−', 'Zoom out', () => this.app.canvas.zoomBy(0.85)));
    tools.appendChild(this._toolBtn('⊡', 'Fit to view (F)', () => this.app.canvas.fitToView()));
    tools.appendChild(this._toolBtn('+', 'Zoom in', () => this.app.canvas.zoomBy(1.18)));
    tools.appendChild(el('span', { class: 'tb-sep' }));
    tools.appendChild(this._toolBtn('⌘', 'Command palette (Ctrl+K)', () => this.app.commandPalette.open()));
    tools.appendChild(this._toolBtn('⛶', 'Full-screen canvas (Shift+F)', () => this.app.toggleFullscreen(), false, store.ui.fullscreen));
    this.root.appendChild(tools);
  }

  _menu(label, items) {
    const wrap = el('div', { class: 'menu' });
    const btn = el('button', { class: 'menu-btn', text: label });
    const list = el('div', { class: 'menu-list' });
    for (const item of items) {
      if (item.sep) { list.appendChild(el('div', { class: 'menu-sep' })); continue; }
      list.appendChild(el('button', { class: 'menu-item', text: item.label, onclick: () => { item.action(); wrap.classList.remove('open'); } }));
    }
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      document.querySelectorAll('.menu.open').forEach((m) => { if (m !== wrap) m.classList.remove('open'); });
      wrap.classList.toggle('open');
    });
    wrap.append(btn, list);
    return wrap;
  }

  _versionItems() {
    const items = [
      { label: 'Snapshot current state…', action: () => this.app.snapshotVersion() },
      { sep: true },
    ];
    const versions = Object.values(store.model.versions);
    if (!versions.length) items.push({ label: '(no snapshots yet)', action: () => {} });
    for (const v of versions) {
      items.push({ label: `Restore: ${v.name}`, action: () => this.app.restoreVersion(v.id) });
      items.push({ label: `Compare with: ${v.name}`, action: () => this.app.compareVersion(v.id) });
    }
    return items;
  }

  _breadcrumb() {
    const bc = el('div', { class: 'breadcrumb' });
    const d = store.diagram;
    if (!d) return bc;
    // Build chain via scopeId parents.
    const chain = [];
    let cur = d;
    const seen = new Set();
    while (cur && !seen.has(cur.id)) {
      seen.add(cur.id);
      chain.unshift(cur);
      if (cur.scopeId) {
        const parentObj = store.model.objects[cur.scopeId];
        const parentDiagram = parentObj && Object.values(store.model.diagrams).find((x) => x.nodes[parentObj.id] && x.id !== cur.id && !x.scopeId);
        cur = parentDiagram || null;
      } else cur = null;
    }
    chain.forEach((node, i) => {
      if (i > 0) bc.appendChild(el('span', { class: 'crumb-sep', text: '›' }));
      bc.appendChild(el('button', {
        class: 'crumb' + (node.id === d.id ? ' current' : ''),
        text: node.name,
        onclick: () => store.setUi({ diagramId: node.id, selection: [] }),
      }));
    });
    return bc;
  }

  _toolBtn(icon, title, action, disabled = false, active = false) {
    return el('button', { class: 'tool-btn' + (active ? ' active' : ''), title, text: icon, disabled, onclick: action });
  }
}

// Diagram tab strip rendered separately under the topbar.
export class DiagramTabs {
  constructor(root, app) { this.root = root; this.app = app; }
  render() {
    this.root.textContent = '';
    for (const id of store.model.diagramOrder) {
      const d = store.model.diagrams[id];
      if (!d) continue;
      const tab = el('div', { class: 'dtab' + (store.ui.diagramId === id ? ' active' : '') });
      tab.appendChild(el('span', { class: 'dtab-kind', title: DIAGRAM_KINDS[d.kind]?.label || d.kind, text: kindGlyph(d) }));
      tab.appendChild(el('span', { class: 'dtab-name', text: d.name, onclick: () => store.setUi({ diagramId: id, selection: [] }) }));
      tab.appendChild(el('button', { class: 'dtab-x', text: '×', title: 'Delete diagram', onclick: (e) => { e.stopPropagation(); if (confirm(`Delete diagram "${d.name}"?`)) store.deleteDiagram(id); } }));
      this.root.appendChild(tab);
    }
    this.root.appendChild(el('button', { class: 'dtab-add', text: '+', title: 'New diagram', onclick: () => this.app.newDiagramDialog() }));
  }
}

function kindGlyph(d) {
  if (d.notation === 'archimate') return '▤';
  return { 'c4-landscape': '🌐', 'c4-context': '◎', 'c4-container': '▣', 'c4-component': '▦' }[d.kind] || '◇';
}
