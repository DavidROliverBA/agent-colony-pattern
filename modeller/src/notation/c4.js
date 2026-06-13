// C4 model notation: element and relationship definitions.
// Each element type carries the metadata the palette, canvas renderer and
// drill-down logic need. Colours follow the conventional C4 palette
// (Simon Brown's notation) but are overridable per-diagram.

export const C4_LEVELS = ['landscape', 'context', 'container', 'component', 'code'];

export const C4_LEVEL_LABELS = {
  landscape: 'System Landscape',
  context: 'System Context',
  container: 'Container',
  component: 'Component',
  code: 'Code',
};

// Which child level a given element type drills down into.
export const C4_DRILL = {
  softwareSystem: 'container',
  container: 'component',
  component: 'code',
};

export const C4_ELEMENTS = [
  {
    type: 'person',
    label: 'Person',
    category: 'People',
    fill: '#08427b',
    stroke: '#063865',
    text: '#ffffff',
    shape: 'person',
    external: false,
    desc: 'A human user or role interacting with the system.',
  },
  {
    type: 'externalPerson',
    label: 'External Person',
    category: 'People',
    fill: '#686868',
    stroke: '#4d4d4d',
    text: '#ffffff',
    shape: 'person',
    external: true,
    desc: 'A user outside the boundary of the system being described.',
  },
  {
    type: 'softwareSystem',
    label: 'Software System',
    category: 'Systems',
    fill: '#1168bd',
    stroke: '#0b4884',
    text: '#ffffff',
    shape: 'box',
    external: false,
    desc: 'A system that delivers value. The highest level of abstraction.',
  },
  {
    type: 'externalSystem',
    label: 'External System',
    category: 'Systems',
    fill: '#999999',
    stroke: '#6b6b6b',
    text: '#ffffff',
    shape: 'box',
    external: true,
    desc: 'A system owned by another team or third party.',
  },
  {
    type: 'container',
    label: 'Container',
    category: 'Containers',
    fill: '#438dd5',
    stroke: '#2e6295',
    text: '#ffffff',
    shape: 'box',
    external: false,
    desc: 'An application or data store — something that is separately deployable.',
  },
  {
    type: 'database',
    label: 'Database',
    category: 'Containers',
    fill: '#438dd5',
    stroke: '#2e6295',
    text: '#ffffff',
    shape: 'cylinder',
    external: false,
    desc: 'A data store container (relational, document, cache, queue …).',
  },
  {
    type: 'component',
    label: 'Component',
    category: 'Components',
    fill: '#85bbf0',
    stroke: '#5d82a8',
    text: '#000000',
    shape: 'box',
    external: false,
    desc: 'A grouping of related functionality behind a clear interface.',
  },
  {
    type: 'code',
    label: 'Code Element',
    category: 'Code',
    fill: '#cfe2f7',
    stroke: '#9bb6d4',
    text: '#000000',
    shape: 'box',
    external: false,
    desc: 'A class, interface or function at the most detailed level.',
  },
  {
    type: 'boundary',
    label: 'Boundary',
    category: 'Grouping',
    fill: 'transparent',
    stroke: '#777777',
    text: '#777777',
    shape: 'boundary',
    external: false,
    desc: 'A dashed grouping (enterprise, system or container boundary).',
  },
];

export const C4_RELATIONSHIPS = [
  { type: 'uses', label: 'Uses', dashed: false },
  { type: 'delivers', label: 'Delivers to', dashed: false },
  { type: 'reads', label: 'Reads from', dashed: false },
  { type: 'writes', label: 'Writes to', dashed: false },
  { type: 'async', label: 'Async / event', dashed: true },
];

export const C4_VIEWS = [
  { id: 'landscape', name: 'System Landscape', level: 'landscape' },
  { id: 'context', name: 'System Context', level: 'context' },
  { id: 'container', name: 'Container', level: 'container' },
  { id: 'component', name: 'Component', level: 'component' },
];
