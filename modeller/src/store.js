// Central application store.
//
// Holds the model plus transient UI state (current diagram, selection).
// All model mutations go through `commit()`, which snapshots for undo/redo
// and persists to localStorage. UI subscribes via `subscribe()`.

import { clone, debounce } from './util.js';
import {
  createModel, sanitiseModel, makeObject, makeRelationship, makeDiagram,
} from './model.js';

const STORAGE_KEY = 'archmodeller.workspace.v1';
const MAX_HISTORY = 80;

class Store {
  constructor() {
    this.model = createModel();
    this.ui = {
      diagramId: null,
      selection: [],          // ids of selected objects/relationships in current diagram
      selectionKind: null,    // 'object' | 'relationship' | 'multi' | null
      tool: 'select',         // select | connect
      connectFrom: null,
      activeFlow: null,
      flowStep: -1,
      leftTab: 'palette',
      leftCollapsed: false,
      rightCollapsed: false,
      fullscreen: false,
    };
    this.history = [];
    this.future = [];
    this.listeners = new Set();
    this._persist = debounce(() => this._save(), 400);
  }

  // -- subscription ---------------------------------------------------------
  subscribe(fn) { this.listeners.add(fn); return () => this.listeners.delete(fn); }
  emit(reason = 'change') { for (const fn of this.listeners) fn(reason); }

  // -- mutation -------------------------------------------------------------
  /** Run a mutation function against the model, with undo capture. */
  commit(label, mutator) {
    this.history.push({ label, model: clone(this.model) });
    if (this.history.length > MAX_HISTORY) this.history.shift();
    this.future = [];
    mutator(this.model);
    this._persist();
    this.emit('commit');
  }

  /** Mutate transient UI state without touching undo history. */
  setUi(patch, reason = 'ui') {
    Object.assign(this.ui, patch);
    this.emit(reason);
  }

  undo() {
    if (!this.history.length) return;
    this.future.push({ label: 'redo', model: clone(this.model) });
    const prev = this.history.pop();
    this.model = prev.model;
    this._reconcileUi();
    this._persist();
    this.emit('undo');
  }

  redo() {
    if (!this.future.length) return;
    this.history.push({ label: 'undo', model: clone(this.model) });
    const next = this.future.pop();
    this.model = next.model;
    this._reconcileUi();
    this._persist();
    this.emit('redo');
  }

  canUndo() { return this.history.length > 0; }
  canRedo() { return this.future.length > 0; }

  _reconcileUi() {
    if (!this.model.diagrams[this.ui.diagramId]) {
      this.ui.diagramId = this.model.diagramOrder[0] || null;
    }
    this.ui.selection = this.ui.selection.filter(
      (id) => this.model.objects[id] || this.model.relationships[id]
    );
  }

  // -- convenience accessors ------------------------------------------------
  get diagram() { return this.model.diagrams[this.ui.diagramId] || null; }

  // -- high-level operations ------------------------------------------------
  addObjectToDiagram(type, x, y, props = {}) {
    let createdId = null;
    this.commit('Add element', (m) => {
      const o = makeObject(type, props);
      m.objects[o.id] = o;
      const d = m.diagrams[this.ui.diagramId];
      if (d) d.nodes[o.id] = { x, y };
      createdId = o.id;
    });
    return createdId;
  }

  placeExistingObject(objectId, x, y) {
    this.commit('Add to diagram', (m) => {
      const d = m.diagrams[this.ui.diagramId];
      if (d && !d.nodes[objectId]) d.nodes[objectId] = { x, y };
    });
  }

  removeFromDiagram(objectId) {
    this.commit('Remove from view', (m) => {
      const d = m.diagrams[this.ui.diagramId];
      if (d) delete d.nodes[objectId];
    });
  }

  deleteObject(objectId) {
    this.commit('Delete element', (m) => {
      delete m.objects[objectId];
      for (const [rid, r] of Object.entries(m.relationships)) {
        if (r.source === objectId || r.target === objectId) delete m.relationships[rid];
      }
      for (const d of Object.values(m.diagrams)) delete d.nodes[objectId];
      // Orphan any children in the hierarchy.
      for (const o of Object.values(m.objects)) if (o.parentId === objectId) o.parentId = null;
    });
  }

  deleteRelationship(relId) {
    this.commit('Delete relationship', (m) => {
      delete m.relationships[relId];
      for (const f of Object.values(m.flows)) {
        f.steps = f.steps.filter((s) => s.relationshipId !== relId);
      }
    });
  }

  addRelationship(sourceId, targetId, type, props = {}) {
    let id = null;
    this.commit('Connect', (m) => {
      const r = makeRelationship(sourceId, targetId, type, props);
      m.relationships[r.id] = r;
      id = r.id;
    });
    return id;
  }

  moveNode(objectId, x, y) {
    // Frequent during drag; we still snapshot once per drag via beginDrag.
    const d = this.diagram;
    if (d && d.nodes[objectId]) {
      d.nodes[objectId].x = x;
      d.nodes[objectId].y = y;
      this._persist();
      this.emit('move');
    }
  }

  beginInteraction(label) {
    this.history.push({ label, model: clone(this.model) });
    if (this.history.length > MAX_HISTORY) this.history.shift();
    this.future = [];
  }

  updateObject(objectId, patch) {
    this.commit('Edit element', (m) => Object.assign(m.objects[objectId], patch));
  }

  updateRelationship(relId, patch) {
    this.commit('Edit relationship', (m) => Object.assign(m.relationships[relId], patch));
  }

  updateDiagram(diagramId, patch) {
    this.commit('Edit diagram', (m) => Object.assign(m.diagrams[diagramId], patch));
  }

  addDiagram(props) {
    let id = null;
    this.commit('New diagram', (m) => {
      const d = makeDiagram(props);
      m.diagrams[d.id] = d;
      m.diagramOrder.push(d.id);
      id = d.id;
    });
    return id;
  }

  deleteDiagram(diagramId) {
    this.commit('Delete diagram', (m) => {
      delete m.diagrams[diagramId];
      m.diagramOrder = m.diagramOrder.filter((x) => x !== diagramId);
      for (const [fid, f] of Object.entries(m.flows)) if (f.diagramId === diagramId) delete m.flows[fid];
    });
    if (this.ui.diagramId === diagramId) {
      this.setUi({ diagramId: this.model.diagramOrder[0] || null, selection: [] });
    }
  }

  // -- persistence ----------------------------------------------------------
  _save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ model: this.model, diagramId: this.ui.diagramId }));
    } catch (e) {
      console.warn('Persist failed (storage full or unavailable):', e);
    }
  }

  load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return false;
      const parsed = JSON.parse(raw);
      const { model } = sanitiseModel(parsed.model);
      this.model = model;
      this.ui.diagramId = model.diagrams[parsed.diagramId] ? parsed.diagramId : (model.diagramOrder[0] || null);
      return true;
    } catch (e) {
      console.warn('Load failed:', e);
      return false;
    }
  }

  replaceModel(rawModel, { merge = false } = {}) {
    const { model, warnings } = sanitiseModel(rawModel);
    this.commit('Import model', (m) => {
      if (merge) {
        Object.assign(m.objects, model.objects);
        Object.assign(m.relationships, model.relationships);
        Object.assign(m.diagrams, model.diagrams);
        Object.assign(m.flows, model.flows);
        Object.assign(m.tags, model.tags);
        for (const id of model.diagramOrder) if (!m.diagramOrder.includes(id)) m.diagramOrder.push(id);
      } else {
        // wholesale replace (mutate in place so reference stays valid)
        for (const k of Object.keys(m)) delete m[k];
        Object.assign(m, model);
      }
    });
    this.ui.diagramId = this.model.diagrams[this.ui.diagramId] ? this.ui.diagramId : (this.model.diagramOrder[0] || null);
    this.ui.selection = [];
    this.emit('import');
    return warnings;
  }

  newWorkspace(name) {
    this.commit('New workspace', (m) => {
      const fresh = createModel(name);
      for (const k of Object.keys(m)) delete m[k];
      Object.assign(m, fresh);
    });
    this.ui.diagramId = null;
    this.ui.selection = [];
    this.emit('import');
  }
}

export const store = new Store();
