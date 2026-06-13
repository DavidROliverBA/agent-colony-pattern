// Unified notation registry. Resolves any element/relationship type to its
// visual + semantic definition regardless of whether it is C4 or ArchiMate.

import {
  C4_ELEMENTS, C4_RELATIONSHIPS, C4_LEVELS, C4_LEVEL_LABELS, C4_DRILL,
} from './c4.js';
import {
  ARCHIMATE_ELEMENTS, ARCHIMATE_RELATIONSHIPS, ARCHIMATE_LAYERS,
  ARCHIMATE_LAYER_MAP, ARCHIMATE_VIEWPOINTS,
} from './archimate.js';

// Build element lookup. Each entry is tagged with its notation.
const elementDefs = {};
for (const e of C4_ELEMENTS) elementDefs[e.type] = { ...e, notation: 'c4' };
for (const e of ARCHIMATE_ELEMENTS) {
  const layer = ARCHIMATE_LAYER_MAP[e.layer];
  elementDefs[e.type] = {
    ...e,
    notation: 'archimate',
    fill: layer.fill,
    stroke: layer.stroke,
    text: layer.text,
    category: layer.label,
  };
}

const relDefs = {};
for (const r of C4_RELATIONSHIPS) relDefs[r.type] = { ...r, notation: 'c4' };
for (const r of ARCHIMATE_RELATIONSHIPS) relDefs[r.type] = { ...r, notation: 'archimate' };

export function elementDef(type) {
  return elementDefs[type] || {
    type, label: type, notation: 'c4', fill: '#cccccc', stroke: '#999999',
    text: '#000000', shape: 'box', category: 'Other', desc: '',
  };
}

export function relationshipDef(type) {
  return relDefs[type] || { type, label: type, notation: 'c4', dashed: false };
}

export function allElementDefs() {
  return Object.values(elementDefs);
}

export function relationshipDefsFor(notation) {
  if (notation === 'archimate') return ARCHIMATE_RELATIONSHIPS;
  if (notation === 'c4') return C4_RELATIONSHIPS;
  return [...C4_RELATIONSHIPS, ...ARCHIMATE_RELATIONSHIPS];
}

export {
  C4_ELEMENTS, C4_RELATIONSHIPS, C4_LEVELS, C4_LEVEL_LABELS, C4_DRILL,
  ARCHIMATE_ELEMENTS, ARCHIMATE_RELATIONSHIPS, ARCHIMATE_LAYERS,
  ARCHIMATE_LAYER_MAP, ARCHIMATE_VIEWPOINTS,
};

// Palette grouping for the left panel.
export function paletteGroups(notation) {
  if (notation === 'archimate') {
    return ARCHIMATE_LAYERS.map((layer) => ({
      key: layer.id,
      label: layer.label,
      color: layer.fill,
      items: ARCHIMATE_ELEMENTS.filter((e) => e.layer === layer.id).map((e) => e.type),
    }));
  }
  // C4 grouped by category
  const groups = {};
  for (const e of C4_ELEMENTS) {
    (groups[e.category] ||= []).push(e.type);
  }
  return Object.entries(groups).map(([label, items]) => ({ key: label, label, items }));
}
