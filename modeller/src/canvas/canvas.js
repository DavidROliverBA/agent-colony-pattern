// SVG canvas: renders the current diagram as a view over the model and
// handles all pointer interaction (pan, zoom, select, drag, connect, marquee).
//
// Rendering is model-driven: it reads store.diagram + store.model on every
// render. Layout (positions) lives on the diagram nodes; identity/labels live
// on the model objects — so a rename anywhere re-renders correctly everywhere.

import { store } from '../store.js';
import { svgEl, clamp, snap, escapeHtml } from '../util.js';
import {
  elementDef, relationshipDef, ARCHIMATE_LAYER_MAP, ARCHIMATE_VIEWPOINTS,
} from '../notation/index.js';
import {
  objectsInDiagram, relationshipsInDiagram, childrenOf,
} from '../model.js';

const NODE_W = 180;
const NODE_H = 110;
const BOUNDARY_W = 320;
const BOUNDARY_H = 240;

export class Canvas {
  constructor(root) {
    this.root = root;
    this.svg = svgEl('svg', { class: 'canvas-svg', tabindex: '0' });
    this.defs = svgEl('defs');
    this.gGrid = svgEl('g', { class: 'layer-grid' });
    this.gWorld = svgEl('g', { class: 'world' });
    this.gEdges = svgEl('g', { class: 'layer-edges' });
    this.gNodes = svgEl('g', { class: 'layer-nodes' });
    this.gOverlay = svgEl('g', { class: 'layer-overlay' });
    this.gWorld.append(this.gEdges, this.gNodes, this.gOverlay);
    this.svg.append(this.defs, this.gGrid, this.gWorld);
    this.root.appendChild(this.svg);

    this.minimap = svgEl('svg', { class: 'minimap' });
    this.root.appendChild(this.minimap);

    this._buildMarkers();
    this._bindEvents();

    this.drag = null;       // active drag state
    this.editing = null;    // inline edit state
    this._raf = null;
    this.onContextMenu = null; // set by UI layer
  }

  // -- viewport -------------------------------------------------------------
  get vp() {
    const d = store.diagram;
    return d ? d.viewport : { x: 0, y: 0, zoom: 1 };
  }
  setVp(vp) {
    const d = store.diagram;
    if (!d) return;
    d.viewport = { ...d.viewport, ...vp };
    store._persist();
    this._applyTransform();
    this._renderGrid();
    this._renderMinimap();
  }

  screenToWorld(sx, sy) {
    const rect = this.svg.getBoundingClientRect();
    const { x, y, zoom } = this.vp;
    return { x: (sx - rect.left - x) / zoom, y: (sy - rect.top - y) / zoom };
  }

  _applyTransform() {
    const { x, y, zoom } = this.vp;
    this.gWorld.setAttribute('transform', `translate(${x} ${y}) scale(${zoom})`);
  }

  zoomBy(factor, cx, cy) {
    const { x, y, zoom } = this.vp;
    const rect = this.svg.getBoundingClientRect();
    const px = cx == null ? rect.width / 2 : cx - rect.left;
    const py = cy == null ? rect.height / 2 : cy - rect.top;
    const newZoom = clamp(zoom * factor, 0.1, 4);
    // keep the point under cursor stable
    const wx = (px - x) / zoom;
    const wy = (py - y) / zoom;
    this.setVp({ zoom: newZoom, x: px - wx * newZoom, y: py - wy * newZoom });
  }

  fitToView(padding = 80) {
    const d = store.diagram;
    if (!d) return;
    const boxes = this._nodeBoxes();
    if (!boxes.length) { this.setVp({ x: 60, y: 60, zoom: 1 }); return; }
    const minX = Math.min(...boxes.map((b) => b.x));
    const minY = Math.min(...boxes.map((b) => b.y));
    const maxX = Math.max(...boxes.map((b) => b.x + b.w));
    const maxY = Math.max(...boxes.map((b) => b.y + b.h));
    const rect = this.svg.getBoundingClientRect();
    const w = maxX - minX, h = maxY - minY;
    const zoom = clamp(Math.min((rect.width - padding * 2) / w, (rect.height - padding * 2) / h), 0.1, 2);
    this.setVp({
      zoom,
      x: padding - minX * zoom + (rect.width - padding * 2 - w * zoom) / 2,
      y: padding - minY * zoom + (rect.height - padding * 2 - h * zoom) / 2,
    });
  }

  // -- render ---------------------------------------------------------------
  render() {
    if (this._raf) return;
    this._raf = requestAnimationFrame(() => { this._raf = null; this._renderNow(); });
  }

  _renderNow() {
    this._applyTransform();
    this._renderGrid();
    this._renderEdges();
    this._renderNodes();
    this._renderOverlay();
    this._renderMinimap();
  }

  _nodeSize(obj, node) {
    const def = elementDef(obj.type);
    if (def.shape === 'boundary') return { w: node.w || BOUNDARY_W, h: node.h || BOUNDARY_H };
    return { w: node.w || NODE_W, h: node.h || NODE_H };
  }

  _nodeBoxes() {
    const d = store.diagram;
    if (!d) return [];
    return objectsInDiagram(store.model, d).map((o) => {
      const n = d.nodes[o.id];
      const { w, h } = this._nodeSize(o, n);
      return { id: o.id, x: n.x, y: n.y, w, h };
    });
  }

  // Computes which objects/edges should be dimmed by active filter/overlay/flow.
  _emphasis() {
    const d = store.diagram;
    const m = store.model;
    const result = { dimNode: new Set(), dimEdge: new Set(), highlightEdge: new Set(), highlightNode: new Set() };
    if (!d) return result;
    const objs = objectsInDiagram(m, d);

    // Tag/layer filters: dim nodes not matching.
    const tagFilter = d.filters?.tags || [];
    const layerFilter = d.filters?.layers || [];
    if (tagFilter.length || layerFilter.length) {
      for (const o of objs) {
        const def = elementDef(o.type);
        const tagOk = !tagFilter.length || o.tags.some((t) => tagFilter.includes(t));
        const layerOk = !layerFilter.length || (def.notation === 'archimate' && layerFilter.includes(def.layer));
        if (!(tagOk && layerOk)) result.dimNode.add(o.id);
      }
    }

    // Viewpoint (ArchiMate): dim elements outside the viewpoint layers.
    if (d.notation === 'archimate' && d.viewpoint && d.viewpoint !== 'all') {
      const vp = ARCHIMATE_VIEWPOINTS.find((v) => v.id === d.viewpoint);
      if (vp) {
        for (const o of objs) {
          const def = elementDef(o.type);
          if (def.notation === 'archimate' && !vp.layers.includes(def.layer)) result.dimNode.add(o.id);
        }
      }
    }

    // Active flow: highlight current step's relationship + endpoints, dim rest.
    if (store.ui.activeFlow) {
      const flow = m.flows[store.ui.activeFlow];
      if (flow && store.ui.flowStep >= 0) {
        const step = flow.steps[store.ui.flowStep];
        const rel = step && m.relationships[step.relationshipId];
        if (rel) {
          result.highlightEdge.add(rel.id);
          result.highlightNode.add(rel.source);
          result.highlightNode.add(rel.target);
          for (const o of objs) if (!result.highlightNode.has(o.id)) result.dimNode.add(o.id);
        }
      }
    }
    return result;
  }

  _renderNodes() {
    const d = store.diagram;
    this.gNodes.textContent = '';
    if (!d) return;
    const m = store.model;
    const emph = this._emphasis();
    const selection = new Set(store.ui.selection);
    // Boundaries first (behind), then others.
    const objs = objectsInDiagram(m, d).sort((a, b) => {
      const sa = elementDef(a.type).shape === 'boundary' ? 0 : 1;
      const sb = elementDef(b.type).shape === 'boundary' ? 0 : 1;
      return sa - sb;
    });
    for (const o of objs) {
      this.gNodes.appendChild(this._nodeEl(o, d.nodes[o.id], {
        selected: selection.has(o.id),
        dim: emph.dimNode.has(o.id),
        highlight: emph.highlightNode.has(o.id),
      }));
    }
  }

  _nodeEl(obj, node, state) {
    const def = elementDef(obj.type);
    const style = node.styleOverride || {};
    const fill = style.fill || def.fill;
    const stroke = style.stroke || def.stroke;
    const text = style.text || def.text;
    const { w, h } = this._nodeSize(obj, node);
    const g = svgEl('g', {
      class: 'node' + (state.selected ? ' selected' : '') + (state.dim ? ' dim' : '') +
             (state.highlight ? ' highlight' : '') + (def.shape === 'boundary' ? ' boundary' : ''),
      transform: `translate(${node.x} ${node.y})`,
      dataset: { id: obj.id, kind: 'object' },
    });

    g.appendChild(this._shape(def.shape, w, h, fill, stroke, obj.lifecycle));

    if (def.shape === 'boundary') {
      g.appendChild(svgEl('text', { class: 'node-boundary-label', x: 12, y: 22, fill: stroke, text: obj.name }));
    } else {
      g.appendChild(this._nodeText(obj, def, w, h, text));
      // External marker / notation badge
      const badge = def.external ? '⟂ external' : (def.notation === 'archimate' ? ARCHIMATE_LAYER_MAP[def.layer]?.label : def.label);
      g.appendChild(svgEl('text', { class: 'node-type', x: w / 2, y: h - 12, 'text-anchor': 'middle', fill: text, opacity: 0.75, text: badge || def.label }));
      // Drill-down affordance
      if (this._canDrill(obj)) {
        const dd = svgEl('g', { class: 'drill-badge', dataset: { id: obj.id, action: 'drill' }, transform: `translate(${w - 26} 8)` });
        dd.appendChild(svgEl('rect', { x: 0, y: 0, width: 18, height: 18, rx: 4 }));
        dd.appendChild(svgEl('text', { x: 9, y: 13, 'text-anchor': 'middle', text: '⤢' }));
        const childCount = childrenOf(store.model, obj.id).length;
        dd.appendChild(svgEl('title', { text: childCount ? `Drill down (${childCount} children)` : 'Drill down' }));
        g.appendChild(dd);
      }
    }
    return g;
  }

  _canDrill(obj) {
    return ['softwareSystem', 'container', 'component'].includes(obj.type);
  }

  _shape(shape, w, h, fill, stroke, lifecycle) {
    const dashForLifecycle = lifecycle === 'future' || lifecycle === 'proposed';
    const common = {
      fill, stroke, 'stroke-width': 2,
      'stroke-dasharray': dashForLifecycle ? '6 4' : null,
      opacity: lifecycle === 'removed' ? 0.45 : 1,
    };
    switch (shape) {
      case 'person': {
        const g = svgEl('g');
        g.appendChild(svgEl('circle', { cx: w / 2, cy: 22, r: 16, ...common }));
        g.appendChild(svgEl('rect', { x: 8, y: 40, width: w - 16, height: h - 48, rx: 10, ...common }));
        return g;
      }
      case 'cylinder': {
        const g = svgEl('g');
        const ry = 14;
        g.appendChild(svgEl('path', { d: `M0 ${ry} a${w / 2} ${ry} 0 0 1 ${w} 0 v${h - 2 * ry} a${w / 2} ${ry} 0 0 1 ${-w} 0 Z`, ...common }));
        g.appendChild(svgEl('ellipse', { cx: w / 2, cy: ry, rx: w / 2, ry, fill, stroke, 'stroke-width': 2 }));
        return g;
      }
      case 'boundary':
        return svgEl('rect', { x: 0, y: 0, width: w, height: h, rx: 12, fill: 'transparent', stroke, 'stroke-width': 2, 'stroke-dasharray': '8 6' });
      case 'square':
        return svgEl('rect', { x: 0, y: 0, width: w, height: h, rx: 2, ...common });
      case 'rounded':
        return svgEl('rect', { x: 0, y: 0, width: w, height: h, rx: 14, ...common });
      case 'box':
      default:
        return svgEl('rect', { x: 0, y: 0, width: w, height: h, rx: 6, ...common });
    }
  }

  _nodeText(obj, def, w, h, color) {
    const g = svgEl('g', { class: 'node-label' });
    const name = svgEl('text', { class: 'node-name', x: w / 2, y: def.shape === 'person' ? 60 : h / 2 - 6, 'text-anchor': 'middle', fill: color });
    wrapText(name, obj.name, w - 24, 2);
    g.appendChild(name);
    if (obj.technology) {
      g.appendChild(svgEl('text', { class: 'node-tech', x: w / 2, y: (def.shape === 'person' ? 60 : h / 2 - 6) + 30, 'text-anchor': 'middle', fill: color, opacity: 0.8, text: `[${obj.technology}]` }));
    }
    // tag dots
    const tagDefs = obj.tags.map((t) => Object.values(store.model.tags).find((x) => x.name === t)).filter(Boolean);
    tagDefs.slice(0, 6).forEach((t, i) => {
      g.appendChild(svgEl('circle', { cx: 12 + i * 12, cy: 12, r: 4, fill: t.color, stroke: '#0003' }));
    });
    return g;
  }

  _renderEdges() {
    const d = store.diagram;
    this.gEdges.textContent = '';
    if (!d) return;
    const m = store.model;
    const emph = this._emphasis();
    const sel = new Set(store.ui.selection);
    for (const rel of relationshipsInDiagram(m, d)) {
      this.gEdges.appendChild(this._edgeEl(rel, {
        selected: sel.has(rel.id),
        dim: (emph.dimNode.has(rel.source) || emph.dimNode.has(rel.target)) && !emph.highlightEdge.has(rel.id),
        highlight: emph.highlightEdge.has(rel.id),
      }));
    }
  }

  _edgeEl(rel, state) {
    const d = store.diagram;
    const a = d.nodes[rel.source], b = d.nodes[rel.target];
    const sa = this._nodeSize(store.model.objects[rel.source], a);
    const sb = this._nodeSize(store.model.objects[rel.target], b);
    const ca = { x: a.x + sa.w / 2, y: a.y + sa.h / 2 };
    const cb = { x: b.x + sb.w / 2, y: b.y + sb.h / 2 };
    const p1 = edgePoint(ca, cb, sa);
    const p2 = edgePoint(cb, ca, sb);
    const def = relationshipDef(rel.type);
    const g = svgEl('g', {
      class: 'edge' + (state.selected ? ' selected' : '') + (state.dim ? ' dim' : '') + (state.highlight ? ' highlight' : ''),
      dataset: { id: rel.id, kind: 'relationship' },
    });
    const dash = def.dashed || rel.lifecycle === 'future' || rel.lifecycle === 'proposed';
    const markerEnd = rel.direction !== 'none' ? `url(#${edgeMarker(def)})` : null;
    const markerStart = rel.direction === 'bidirectional' ? `url(#${edgeMarker(def)}-start)` : null;
    // wide invisible hit line
    g.appendChild(svgEl('line', { class: 'edge-hit', x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y }));
    g.appendChild(svgEl('line', {
      class: 'edge-line', x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y,
      'stroke-dasharray': dash ? '7 5' : null,
      'marker-end': markerEnd, 'marker-start': markerStart,
    }));
    const label = rel.label || (def.notation === 'c4' ? '' : def.label);
    if (label) {
      const mx = (p1.x + p2.x) / 2, my = (p1.y + p2.y) / 2;
      const t = svgEl('text', { class: 'edge-label', x: mx, y: my - 4, 'text-anchor': 'middle' });
      const tech = rel.technology ? ` [${rel.technology}]` : '';
      t.appendChild(svgEl('tspan', { text: label }));
      if (tech) t.appendChild(svgEl('tspan', { dx: 2, class: 'edge-tech', text: tech }));
      // backing rect for legibility
      g.appendChild(svgEl('rect', { class: 'edge-label-bg', x: mx - (label.length + tech.length) * 3.2, y: my - 16, width: (label.length + tech.length) * 6.4, height: 16, rx: 3 }));
      g.appendChild(t);
    }
    return g;
  }

  _renderGrid() {
    const d = store.diagram;
    this.gGrid.textContent = '';
    if (!d || !store.model.settings.snapToGrid) { this.gGrid.style.opacity = 0; return; }
    this.gGrid.style.opacity = 1;
    const rect = this.svg.getBoundingClientRect();
    const { x, y, zoom } = this.vp;
    const size = store.model.settings.gridSize * 4 * zoom;
    if (size < 6) { this.gGrid.style.opacity = 0; return; }
    const ox = ((x % size) + size) % size;
    const oy = ((y % size) + size) % size;
    const pattern = [];
    for (let gx = ox; gx < rect.width; gx += size) pattern.push(svgEl('line', { x1: gx, y1: 0, x2: gx, y2: rect.height, class: 'grid-line' }));
    for (let gy = oy; gy < rect.height; gy += size) pattern.push(svgEl('line', { x1: 0, y1: gy, x2: rect.width, y2: gy, class: 'grid-line' }));
    pattern.forEach((p) => this.gGrid.appendChild(p));
  }

  _renderOverlay() {
    this.gOverlay.textContent = '';
    if (this.drag?.type === 'marquee') {
      const { x0, y0, x1, y1 } = this.drag;
      this.gOverlay.appendChild(svgEl('rect', {
        class: 'marquee', x: Math.min(x0, x1), y: Math.min(y0, y1),
        width: Math.abs(x1 - x0), height: Math.abs(y1 - y0),
      }));
    }
    if (this.drag?.type === 'connect' && this.drag.current) {
      const { from, current } = this.drag;
      this.gOverlay.appendChild(svgEl('line', { class: 'connect-preview', x1: from.x, y1: from.y, x2: current.x, y2: current.y }));
    }
  }

  _renderMinimap() {
    const boxes = this._nodeBoxes();
    this.minimap.textContent = '';
    if (!boxes.length) { this.minimap.style.display = 'none'; return; }
    this.minimap.style.display = 'block';
    const pad = 20;
    const minX = Math.min(...boxes.map((b) => b.x)) - pad;
    const minY = Math.min(...boxes.map((b) => b.y)) - pad;
    const maxX = Math.max(...boxes.map((b) => b.x + b.w)) + pad;
    const maxY = Math.max(...boxes.map((b) => b.y + b.h)) + pad;
    const w = maxX - minX, h = maxY - minY;
    this.minimap.setAttribute('viewBox', `${minX} ${minY} ${w} ${h}`);
    for (const b of boxes) {
      const o = store.model.objects[b.id];
      this.minimap.appendChild(svgEl('rect', { x: b.x, y: b.y, width: b.w, height: b.h, fill: elementDef(o.type).fill, opacity: 0.8 }));
    }
    // viewport rectangle
    const rect = this.svg.getBoundingClientRect();
    const { x, y, zoom } = this.vp;
    this.minimap.appendChild(svgEl('rect', {
      class: 'minimap-vp', x: -x / zoom, y: -y / zoom,
      width: rect.width / zoom, height: rect.height / zoom,
    }));
  }

  _buildMarkers() {
    const mk = (id, builder, color = '#64748b') => {
      const m = svgEl('marker', { id, markerWidth: 14, markerHeight: 14, refX: 11, refY: 6, orient: 'auto', markerUnits: 'userSpaceOnUse' });
      builder(m, color);
      this.defs.appendChild(m);
    };
    mk('arrow-filled', (m) => m.appendChild(svgEl('path', { d: 'M0 0 L12 6 L0 12 z', fill: '#475569' })));
    mk('arrow-open', (m) => m.appendChild(svgEl('path', { d: 'M0 0 L12 6 L0 12', fill: 'none', stroke: '#475569', 'stroke-width': 1.6 })));
    mk('triangle-open', (m) => m.appendChild(svgEl('path', { d: 'M0 0 L12 6 L0 12 z', fill: '#fff', stroke: '#475569', 'stroke-width': 1.4 })));
    mk('diamond-filled', (m) => { m.setAttribute('refX', '13'); m.appendChild(svgEl('path', { d: 'M0 6 L7 0 L14 6 L7 12 z', fill: '#475569' })); });
    mk('diamond-open', (m) => { m.setAttribute('refX', '13'); m.appendChild(svgEl('path', { d: 'M0 6 L7 0 L14 6 L7 12 z', fill: '#fff', stroke: '#475569', 'stroke-width': 1.4 })); });
    mk('ball', (m) => m.appendChild(svgEl('circle', { cx: 6, cy: 6, r: 4, fill: '#475569' })));
    // start variants (reversed) for bidirectional
    ['arrow-filled', 'arrow-open'].forEach((base) => {
      const m = svgEl('marker', { id: `${base}-start`, markerWidth: 14, markerHeight: 14, refX: 1, refY: 6, orient: 'auto', markerUnits: 'userSpaceOnUse' });
      const open = base === 'arrow-open';
      m.appendChild(svgEl('path', { d: 'M12 0 L0 6 L12 12' + (open ? '' : ' z'), fill: open ? 'none' : '#475569', stroke: '#475569', 'stroke-width': open ? 1.6 : 0 }));
      this.defs.appendChild(m);
    });
  }

  // -- interaction ----------------------------------------------------------
  _bindEvents() {
    this.svg.addEventListener('wheel', (e) => {
      e.preventDefault();
      this.zoomBy(e.deltaY < 0 ? 1.12 : 0.89, e.clientX, e.clientY);
    }, { passive: false });

    this.svg.addEventListener('pointerdown', (e) => this._onPointerDown(e));
    window.addEventListener('pointermove', (e) => this._onPointerMove(e));
    window.addEventListener('pointerup', (e) => this._onPointerUp(e));
    this.svg.addEventListener('dblclick', (e) => this._onDblClick(e));
    this.svg.addEventListener('contextmenu', (e) => {
      const target = this._hit(e);
      if (this.onContextMenu) { e.preventDefault(); this.onContextMenu(e, target); }
    });

    // palette drag-drop
    this.svg.addEventListener('dragover', (e) => { e.preventDefault(); e.dataTransfer.dropEffect = 'copy'; });
    this.svg.addEventListener('drop', (e) => {
      e.preventDefault();
      const type = e.dataTransfer.getData('application/x-element-type');
      const existingId = e.dataTransfer.getData('application/x-object-id');
      const p = this.screenToWorld(e.clientX, e.clientY);
      const gs = store.model.settings.gridSize;
      const x = store.model.settings.snapToGrid ? snap(p.x - NODE_W / 2, gs) : p.x - NODE_W / 2;
      const y = store.model.settings.snapToGrid ? snap(p.y - NODE_H / 2, gs) : p.y - NODE_H / 2;
      if (existingId) {
        store.placeExistingObject(existingId, x, y);
      } else if (type) {
        const id = store.addObjectToDiagram(type, x, y);
        store.setUi({ selection: [id], selectionKind: 'object' });
      }
    });
  }

  _hit(e) {
    const node = e.target.closest('.node');
    const edge = e.target.closest('.edge');
    const drill = e.target.closest('.drill-badge');
    if (drill) return { kind: 'drill', id: drill.dataset.id };
    if (node) return { kind: 'object', id: node.dataset.id };
    if (edge) return { kind: 'relationship', id: edge.dataset.id };
    return { kind: 'canvas' };
  }

  _onPointerDown(e) {
    if (e.button === 1 || (e.button === 0 && e.altKey)) {
      // middle / alt: pan
      this.drag = { type: 'pan', sx: e.clientX, sy: e.clientY, vp: { ...this.vp } };
      this.svg.setPointerCapture?.(e.pointerId);
      return;
    }
    if (e.button !== 0) return;
    const hit = this._hit(e);
    const world = this.screenToWorld(e.clientX, e.clientY);

    if (hit.kind === 'drill') { this._drill(hit.id); return; }

    if (store.ui.tool === 'connect') {
      if (hit.kind === 'object') {
        const n = store.diagram.nodes[hit.id];
        const s = this._nodeSize(store.model.objects[hit.id], n);
        this.drag = { type: 'connect', fromId: hit.id, from: { x: n.x + s.w / 2, y: n.y + s.h / 2 }, current: world };
      }
      return;
    }

    if (hit.kind === 'object') {
      const already = store.ui.selection.includes(hit.id);
      let selection;
      if (e.shiftKey) {
        selection = already ? store.ui.selection.filter((x) => x !== hit.id) : [...store.ui.selection, hit.id];
      } else {
        selection = already ? store.ui.selection : [hit.id];
      }
      store.setUi({ selection, selectionKind: selection.length > 1 ? 'multi' : 'object' });
      // begin node drag for all selected objects present in diagram
      const objs = selection.filter((id) => store.diagram.nodes[id]);
      this.drag = {
        type: 'node', objs, started: false,
        start: world,
        origin: Object.fromEntries(objs.map((id) => [id, { x: store.diagram.nodes[id].x, y: store.diagram.nodes[id].y }])),
      };
    } else if (hit.kind === 'relationship') {
      store.setUi({ selection: [hit.id], selectionKind: 'relationship' });
    } else {
      // background: marquee or pan depending on space
      if (this._spaceDown) {
        this.drag = { type: 'pan', sx: e.clientX, sy: e.clientY, vp: { ...this.vp } };
      } else {
        store.setUi({ selection: [], selectionKind: null });
        this.drag = { type: 'marquee', x0: world.x, y0: world.y, x1: world.x, y1: world.y };
      }
    }
  }

  _onPointerMove(e) {
    if (!this.drag) return;
    const world = this.screenToWorld(e.clientX, e.clientY);
    if (this.drag.type === 'pan') {
      this.setVp({ x: this.drag.vp.x + (e.clientX - this.drag.sx), y: this.drag.vp.y + (e.clientY - this.drag.sy) });
    } else if (this.drag.type === 'node') {
      if (!this.drag.started) { store.beginInteraction('Move'); this.drag.started = true; }
      const dx = world.x - this.drag.start.x;
      const dy = world.y - this.drag.start.y;
      const gs = store.model.settings.gridSize;
      for (const id of this.drag.objs) {
        let nx = this.drag.origin[id].x + dx;
        let ny = this.drag.origin[id].y + dy;
        if (store.model.settings.snapToGrid) { nx = snap(nx, gs); ny = snap(ny, gs); }
        store.diagram.nodes[id].x = nx;
        store.diagram.nodes[id].y = ny;
      }
      this.render();
    } else if (this.drag.type === 'marquee') {
      this.drag.x1 = world.x; this.drag.y1 = world.y;
      this._renderOverlay();
    } else if (this.drag.type === 'connect') {
      this.drag.current = world;
      this._renderOverlay();
    }
  }

  _onPointerUp(e) {
    if (!this.drag) return;
    const drag = this.drag;
    this.drag = null;
    if (drag.type === 'marquee') {
      const x = Math.min(drag.x0, drag.x1), y = Math.min(drag.y0, drag.y1);
      const x2 = Math.max(drag.x0, drag.x1), y2 = Math.max(drag.y0, drag.y1);
      if (Math.abs(x2 - x) > 4 || Math.abs(y2 - y) > 4) {
        const sel = this._nodeBoxes().filter((b) => b.x < x2 && b.x + b.w > x && b.y < y2 && b.y + b.h > y).map((b) => b.id);
        store.setUi({ selection: sel, selectionKind: sel.length > 1 ? 'multi' : (sel.length === 1 ? 'object' : null) });
      }
      this._renderOverlay();
    } else if (drag.type === 'connect') {
      const hit = this._hit(e);
      if (hit.kind === 'object' && hit.id !== drag.fromId) {
        const notation = store.diagram.notation === 'archimate' ? 'archimate' : 'uses';
        const type = store.diagram.notation === 'archimate' ? 'serving' : 'uses';
        const id = store.addRelationship(drag.fromId, hit.id, type);
        store.setUi({ selection: [id], selectionKind: 'relationship', tool: 'select' });
      } else {
        store.setUi({ tool: 'select' });
      }
      this._renderOverlay();
    } else if (drag.type === 'node' && drag.started) {
      store._persist();
      store.emit('move-end');
    }
  }

  _onDblClick(e) {
    const hit = this._hit(e);
    if (hit.kind === 'object') this._startInlineEdit(hit.id, 'object');
    else if (hit.kind === 'relationship') this._startInlineEdit(hit.id, 'relationship');
  }

  _startInlineEdit(id, kind) {
    const obj = kind === 'object' ? store.model.objects[id] : store.model.relationships[id];
    if (!obj) return;
    const d = store.diagram;
    let cx, cy, width;
    if (kind === 'object') {
      const n = d.nodes[id]; const s = this._nodeSize(obj, n);
      const { x, y, zoom } = this.vp;
      const rect = this.svg.getBoundingClientRect();
      cx = rect.left + x + (n.x + 12) * zoom;
      cy = rect.top + y + (n.y + s.h / 2 - 16) * zoom;
      width = (s.w - 24) * zoom;
    } else {
      const a = d.nodes[obj.source], b = d.nodes[obj.target];
      const { x, y, zoom } = this.vp;
      const rect = this.svg.getBoundingClientRect();
      cx = rect.left + x + ((a.x + b.x) / 2 + 30) * zoom;
      cy = rect.top + y + ((a.y + b.y) / 2 + 30) * zoom;
      width = 140;
    }
    const input = document.createElement('input');
    input.className = 'inline-edit';
    input.value = kind === 'object' ? obj.name : obj.label;
    input.style.left = `${cx}px`;
    input.style.top = `${cy}px`;
    input.style.width = `${Math.max(80, width)}px`;
    document.body.appendChild(input);
    input.focus(); input.select();
    const finish = (save) => {
      if (save) {
        if (kind === 'object') store.updateObject(id, { name: input.value });
        else store.updateRelationship(id, { label: input.value });
      }
      input.remove();
    };
    input.addEventListener('blur', () => finish(true));
    input.addEventListener('keydown', (ev) => {
      if (ev.key === 'Enter') { ev.preventDefault(); finish(true); }
      else if (ev.key === 'Escape') { ev.preventDefault(); finish(false); }
    });
  }

  _drill(objectId) {
    // Navigate to (or create) the child-level diagram scoped to this object.
    const obj = store.model.objects[objectId];
    if (!obj) return;
    const drillKind = { softwareSystem: 'c4-container', container: 'c4-component', component: 'c4-component' }[obj.type];
    const level = { softwareSystem: 'container', container: 'component', component: 'component' }[obj.type];
    // Find existing scoped diagram
    let target = Object.values(store.model.diagrams).find((d) => d.scopeId === objectId && d.kind === drillKind);
    if (!target) {
      const id = store.addDiagram({ name: `${obj.name} — ${level}`, kind: drillKind, notation: 'c4', level, scopeId: objectId });
      target = store.model.diagrams[id];
      // auto-place children
      const kids = childrenOf(store.model, objectId);
      kids.forEach((k, i) => {
        target.nodes[k.id] = { x: 80 + (i % 3) * 240, y: 80 + Math.floor(i / 3) * 180 };
      });
      store._persist();
    }
    store.setUi({ diagramId: target.id, selection: [] });
    setTimeout(() => this.fitToView(), 30);
  }
}

// -- geometry helpers -------------------------------------------------------
function edgePoint(from, to, size) {
  // intersection of line from->to with the box centred at `from`
  const dx = to.x - from.x, dy = to.y - from.y;
  if (dx === 0 && dy === 0) return from;
  const hw = size.w / 2, hh = size.h / 2;
  const scale = 1 / Math.max(Math.abs(dx) / hw, Math.abs(dy) / hh);
  return { x: from.x + dx * scale, y: from.y + dy * scale };
}

function edgeMarker(def) {
  const map = {
    arrowFilled: 'arrow-filled', arrowOpen: 'arrow-open', triangleOpen: 'triangle-open',
    diamondFilled: 'diamond-filled', diamondOpen: 'diamond-open', ball: 'ball',
  };
  return map[def.marker] || 'arrow-filled';
}

function wrapText(textEl, str, maxWidth, maxLines) {
  const words = String(str || '').split(/\s+/);
  const approxChar = 7.4;
  const perLine = Math.max(6, Math.floor(maxWidth / approxChar));
  const lines = [];
  let line = '';
  for (const w of words) {
    if ((line + ' ' + w).trim().length > perLine && line) { lines.push(line); line = w; }
    else line = (line + ' ' + w).trim();
    if (lines.length >= maxLines) break;
  }
  if (line && lines.length < maxLines) lines.push(line);
  if (lines.length === maxLines && words.join(' ').length > lines.join(' ').length) {
    lines[maxLines - 1] = lines[maxLines - 1].replace(/.{1}$/, '…');
  }
  const baseY = Number(textEl.getAttribute('y'));
  lines.forEach((ln, i) => {
    textEl.appendChild(svgEl('tspan', { x: textEl.getAttribute('x'), y: baseY + i * 18, text: ln }));
  });
}
