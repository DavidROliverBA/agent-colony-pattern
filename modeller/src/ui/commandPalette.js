// Command palette / quick action launcher (Ctrl/Cmd+K).
// Aggregates app commands, diagrams, and model objects into one fuzzy list.

import { store } from '../store.js';
import { el } from '../util.js';
import { elementDef } from '../notation/index.js';

export class CommandPalette {
  constructor(app) {
    this.app = app;
    this.overlay = el('div', { class: 'cmd-overlay', hidden: true });
    this.box = el('div', { class: 'cmd-box' });
    this.input = el('input', { class: 'cmd-input', type: 'text', placeholder: 'Type a command, diagram or element…' });
    this.list = el('div', { class: 'cmd-list' });
    this.box.append(this.input, this.list);
    this.overlay.appendChild(this.box);
    document.body.appendChild(this.overlay);
    this.active = 0;
    this.items = [];

    this.overlay.addEventListener('click', (e) => { if (e.target === this.overlay) this.close(); });
    this.input.addEventListener('input', () => this._refresh());
    this.input.addEventListener('keydown', (e) => this._onKey(e));
  }

  commands() {
    const a = this.app;
    return [
      { label: 'New diagram…', run: () => a.newDiagramDialog() },
      { label: 'Fit to view', run: () => a.canvas.fitToView() },
      { label: 'Auto-layout diagram', run: () => a.autoLayout() },
      { label: 'Connect tool', run: () => store.setUi({ tool: 'connect' }) },
      { label: 'Select tool', run: () => store.setUi({ tool: 'select' }) },
      { label: 'Undo', run: () => store.undo() },
      { label: 'Redo', run: () => store.redo() },
      { label: 'Export PNG', run: () => import('../io/exporters.js').then((m) => m.exportPng()) },
      { label: 'Export SVG', run: () => import('../io/exporters.js').then((m) => m.exportSvg()) },
      { label: 'Export JSON model', run: () => import('../io/exporters.js').then((m) => m.exportJson()) },
      { label: 'Snapshot version', run: () => a.snapshotVersion() },
      { label: 'Toggle full-screen canvas', run: () => a.toggleFullscreen() },
      { label: 'Toggle grid snap', run: () => store.commit('Toggle snap', (m) => { m.settings.snapToGrid = !m.settings.snapToGrid; }) },
    ];
  }

  open() {
    this.overlay.hidden = false;
    this.input.value = '';
    this._refresh();
    setTimeout(() => this.input.focus(), 0);
  }
  close() { this.overlay.hidden = true; }
  get isOpen() { return !this.overlay.hidden; }

  _refresh() {
    const q = this.input.value.trim().toLowerCase();
    const cmds = this.commands().map((c) => ({ ...c, kind: 'Command' }));
    const diagrams = store.model.diagramOrder.map((id) => store.model.diagrams[id]).filter(Boolean).map((d) => ({
      label: d.name, kind: 'Diagram', run: () => store.setUi({ diagramId: d.id, selection: [] }),
    }));
    const objects = Object.values(store.model.objects).map((o) => ({
      label: o.name, kind: elementDef(o.type).label, run: () => this.app.jumpToObject(o.id),
    }));
    let all = [...cmds, ...diagrams, ...objects];
    if (q) all = all.filter((i) => i.label.toLowerCase().includes(q) || i.kind.toLowerCase().includes(q));
    this.items = all.slice(0, 40);
    this.active = 0;
    this._renderList();
  }

  _renderList() {
    this.list.textContent = '';
    this.items.forEach((item, i) => {
      const row = el('button', { class: 'cmd-row' + (i === this.active ? ' active' : '') });
      row.appendChild(el('span', { class: 'cmd-label', text: item.label }));
      row.appendChild(el('span', { class: 'cmd-kind', text: item.kind }));
      row.addEventListener('click', () => this._runIndex(i));
      row.addEventListener('mousemove', () => { this.active = i; this._renderList(); });
      this.list.appendChild(row);
    });
  }

  _onKey(e) {
    if (e.key === 'Escape') { this.close(); }
    else if (e.key === 'ArrowDown') { e.preventDefault(); this.active = Math.min(this.items.length - 1, this.active + 1); this._renderList(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); this.active = Math.max(0, this.active - 1); this._renderList(); }
    else if (e.key === 'Enter') { e.preventDefault(); this._runIndex(this.active); }
  }

  _runIndex(i) {
    const item = this.items[i];
    if (!item) return;
    this.close();
    item.run();
  }
}
