// Export: PNG, SVG, JSON model, CSV, and a C4-style DSL text export.
// All run fully in-browser — no server needed (GitHub Pages requirement 14).

import { store } from '../store.js';
import { downloadFile, toCsv } from '../util.js';
import { elementDef, relationshipDef } from '../notation/index.js';
import { objectsInDiagram, relationshipsInDiagram } from '../model.js';

const STYLE_HREF = 'styles/main.css';

/** Serialise the current diagram's SVG into a standalone, styled SVG string. */
export function currentDiagramSvg() {
  const svg = document.querySelector('.canvas-svg');
  if (!svg) return null;
  const clone = svg.cloneNode(true);
  // Strip transient overlay (marquee/preview) and UI-only layers.
  clone.querySelectorAll('.layer-overlay, .layer-grid, .edge-hit').forEach((n) => n.remove());

  const boxes = nodeBounds();
  const pad = 40;
  const minX = Math.min(...boxes.map((b) => b.x)) - pad;
  const minY = Math.min(...boxes.map((b) => b.y)) - pad;
  const w = Math.max(...boxes.map((b) => b.x + b.w)) + pad - minX;
  const h = Math.max(...boxes.map((b) => b.y + b.h)) + pad - minY;

  const world = clone.querySelector('.world');
  if (world) world.setAttribute('transform', `translate(${-minX} ${-minY}) scale(1)`);
  clone.setAttribute('viewBox', `0 0 ${w} ${h}`);
  clone.setAttribute('width', w);
  clone.setAttribute('height', h);
  clone.removeAttribute('tabindex');

  const css = embeddedCss();
  const styleEl = document.createElementNS('http://www.w3.org/2000/svg', 'style');
  styleEl.textContent = css;
  clone.insertBefore(styleEl, clone.firstChild);
  // white background for export
  const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  bg.setAttribute('x', 0); bg.setAttribute('y', 0); bg.setAttribute('width', w); bg.setAttribute('height', h);
  bg.setAttribute('fill', '#ffffff');
  clone.insertBefore(bg, styleEl.nextSibling);

  return { svg: '<?xml version="1.0" encoding="UTF-8"?>\n' + new XMLSerializer().serializeToString(clone), width: w, height: h };
}

function nodeBounds() {
  const nodes = [...document.querySelectorAll('.canvas-svg .node')];
  if (!nodes.length) return [{ x: 0, y: 0, w: 400, h: 300 }];
  return nodes.map((n) => {
    const t = n.getAttribute('transform') || '';
    const m = /translate\(([-\d.]+)\s+([-\d.]+)\)/.exec(t);
    const bb = n.getBBox();
    return { x: Number(m?.[1] || 0), y: Number(m?.[2] || 0), w: bb.width, h: bb.height };
  });
}

// Pull the relevant canvas CSS rules so the exported SVG is self-contained.
function embeddedCss() {
  let out = '';
  for (const sheet of document.styleSheets) {
    let rules;
    try { rules = sheet.cssRules; } catch { continue; }
    if (!rules) continue;
    for (const rule of rules) {
      if (rule.selectorText && /\.node|\.edge|\.canvas|\.grid|tspan|text/.test(rule.selectorText)) {
        out += rule.cssText + '\n';
      }
    }
  }
  return out;
}

export function exportSvg() {
  const result = currentDiagramSvg();
  if (!result) return;
  const name = (store.diagram?.name || 'diagram').replace(/\s+/g, '-');
  downloadFile(`${name}.svg`, result.svg, 'image/svg+xml');
}

export function exportPng(scale = 2) {
  const result = currentDiagramSvg();
  if (!result) return;
  const img = new Image();
  const svgBlob = new Blob([result.svg], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(svgBlob);
  img.onload = () => {
    const canvas = document.createElement('canvas');
    canvas.width = result.width * scale;
    canvas.height = result.height * scale;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.drawImage(img, 0, 0);
    URL.revokeObjectURL(url);
    canvas.toBlob((blob) => {
      const name = (store.diagram?.name || 'diagram').replace(/\s+/g, '-');
      downloadFile(`${name}.png`, blob, 'image/png');
    }, 'image/png');
  };
  img.onerror = () => { URL.revokeObjectURL(url); alert('PNG export failed.'); };
  img.src = url;
}

/** Print-to-PDF: opens a print window with the SVG (browser handles PDF). */
export function exportPdf() {
  const result = currentDiagramSvg();
  if (!result) return;
  const w = window.open('', '_blank');
  if (!w) { alert('Pop-up blocked — allow pop-ups to export PDF.'); return; }
  w.document.write(`<!doctype html><title>${store.diagram?.name || 'diagram'}</title>
    <style>@page{size:landscape;margin:10mm}body{margin:0}svg{width:100%;height:auto}</style>
    ${result.svg}<script>window.onload=()=>{window.print()}<\/script>`);
  w.document.close();
}

export function exportJson() {
  const json = JSON.stringify(store.model, null, 2);
  downloadFile(`${store.model.name.replace(/\s+/g, '-') || 'model'}.json`, json, 'application/json');
}

export function exportCsv() {
  const m = store.model;
  const objRows = [['id', 'type', 'notation', 'name', 'technology', 'tags', 'lifecycle', 'parentId', 'shortDescription']];
  for (const o of Object.values(m.objects)) {
    objRows.push([o.id, o.type, elementDef(o.type).notation, o.name, o.technology, o.tags.join('|'), o.lifecycle, o.parentId || '', o.shortDescription]);
  }
  const relRows = [['id', 'source', 'target', 'type', 'label', 'technology', 'direction', 'lifecycle']];
  for (const r of Object.values(m.relationships)) {
    relRows.push([r.id, r.source, r.target, r.type, r.label, r.technology, r.direction, r.lifecycle]);
  }
  downloadFile('objects.csv', toCsv(objRows), 'text/csv');
  setTimeout(() => downloadFile('relationships.csv', toCsv(relRows), 'text/csv'), 150);
}

/** Structurizr-flavoured C4 DSL text export (best-effort, current diagram scope). */
export function exportC4Dsl() {
  const m = store.model;
  const lines = ['workspace {', '  model {'];
  const c4Objs = Object.values(m.objects).filter((o) => elementDef(o.type).notation === 'c4');
  const idName = {};
  for (const o of c4Objs) {
    const ident = identifier(o.name, o.id, idName);
    const kw = { person: 'person', externalPerson: 'person', softwareSystem: 'softwareSystem', externalSystem: 'softwareSystem', container: 'container', database: 'container', component: 'component' }[o.type] || 'softwareSystem';
    lines.push(`    ${ident} = ${kw} "${esc(o.name)}" "${esc(o.shortDescription)}"${o.technology ? ` "${esc(o.technology)}"` : ''}`);
  }
  for (const r of Object.values(m.relationships)) {
    const s = idName[r.source], t = idName[r.target];
    if (s && t) lines.push(`    ${s} -> ${t} "${esc(r.label)}"${r.technology ? ` "${esc(r.technology)}"` : ''}`);
  }
  lines.push('  }', '  views {');
  for (const d of Object.values(m.diagrams).filter((d) => d.notation === 'c4')) {
    const kind = { 'c4-landscape': 'systemLandscape', 'c4-context': 'systemContext', 'c4-container': 'container', 'c4-component': 'component' }[d.kind];
    if (!kind) continue;
    lines.push(`    ${kind} "${esc(d.name)}" {`, '      include *', '      autolayout lr', '    }');
  }
  lines.push('  }', '}');
  downloadFile(`${m.name.replace(/\s+/g, '-')}.dsl`, lines.join('\n'), 'text/plain');
}

/** ArchiMate Open Exchange (simplified) XML export. */
export function exportArchimateExchange() {
  const m = store.model;
  const archObjs = Object.values(m.objects).filter((o) => elementDef(o.type).notation === 'archimate');
  const esc2 = (s) => esc(s);
  let xml = `<?xml version="1.0" encoding="UTF-8"?>\n<model xmlns="http://www.opengroup.org/xsd/archimate/3.0/" identifier="${m.id}">\n`;
  xml += `  <name xml:lang="en">${esc2(m.name)}</name>\n  <elements>\n`;
  for (const o of archObjs) {
    xml += `    <element identifier="${o.id}" xsi:type="${archimateXsiType(o.type)}">\n      <name xml:lang="en">${esc2(o.name)}</name>\n${o.description ? `      <documentation xml:lang="en">${esc2(o.description)}</documentation>\n` : ''}    </element>\n`;
  }
  xml += '  </elements>\n  <relationships>\n';
  for (const r of Object.values(m.relationships)) {
    if (!m.objects[r.source] || !m.objects[r.target]) continue;
    xml += `    <relationship identifier="${r.id}" source="${r.source}" target="${r.target}" xsi:type="${capitalize(r.type)}">\n${r.label ? `      <name xml:lang="en">${esc2(r.label)}</name>\n` : ''}    </relationship>\n`;
  }
  xml += '  </relationships>\n</model>\n';
  downloadFile(`${m.name.replace(/\s+/g, '-')}.archimate.xml`, xml, 'application/xml');
}

function archimateXsiType(type) {
  return capitalize(type);
}
function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
function esc(s) { return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
function identifier(name, id, map) {
  let base = name.replace(/[^a-zA-Z0-9]/g, '') || 'el';
  if (/^[0-9]/.test(base)) base = 'e' + base;
  let ident = base, n = 1;
  const used = new Set(Object.values(map));
  while (used.has(ident)) ident = base + (++n);
  map[id] = ident;
  return ident;
}
