// ArchiMate 3.x notation: layers, elements, relationships and viewpoints.
// Colours follow the standard ArchiMate layer palette. The element set is a
// pragmatic, extensible subset covering every layer; it is designed to grow
// toward full specification compliance without restructuring.

export const ARCHIMATE_LAYERS = [
  { id: 'motivation', label: 'Motivation', fill: '#cc99ff', stroke: '#8e6bb3', text: '#1b1230' },
  { id: 'strategy', label: 'Strategy', fill: '#f5deb3', stroke: '#b9a371', text: '#332a14' },
  { id: 'business', label: 'Business', fill: '#ffffb5', stroke: '#bdbd6e', text: '#33330a' },
  { id: 'application', label: 'Application', fill: '#b5ffff', stroke: '#6ebcbc', text: '#0a3333' },
  { id: 'technology', label: 'Technology', fill: '#c9ffc9', stroke: '#74b074', text: '#0a330a' },
  { id: 'physical', label: 'Physical', fill: '#a6e8a6', stroke: '#5f9c5f', text: '#0a330a' },
  { id: 'implementation', label: 'Implementation & Migration', fill: '#ffe0e0', stroke: '#c79a9a', text: '#330a0a' },
];

export const ARCHIMATE_LAYER_MAP = Object.fromEntries(
  ARCHIMATE_LAYERS.map((l) => [l.id, l])
);

// shape: notation hint used by the renderer. ArchiMate distinguishes active
// structure (rounded box), behaviour (rounded box), passive structure (square)
// and uses corner glyphs; we render a simplified, legible variant.
const E = (type, label, layer, aspect, shape, desc) => ({ type, label, layer, aspect, shape, desc });

export const ARCHIMATE_ELEMENTS = [
  // Motivation
  E('stakeholder', 'Stakeholder', 'motivation', 'motivation', 'rounded', 'Role with an interest in the outcome.'),
  E('driver', 'Driver', 'motivation', 'motivation', 'rounded', 'External or internal condition motivating change.'),
  E('assessment', 'Assessment', 'motivation', 'motivation', 'rounded', 'Result of analysing a driver.'),
  E('goal', 'Goal', 'motivation', 'motivation', 'rounded', 'A high-level statement of intent.'),
  E('outcome', 'Outcome', 'motivation', 'motivation', 'rounded', 'An end result that has been achieved.'),
  E('principle', 'Principle', 'motivation', 'motivation', 'rounded', 'A normative property of all systems.'),
  E('requirement', 'Requirement', 'motivation', 'motivation', 'rounded', 'A statement of need to be realised.'),
  E('constraint', 'Constraint', 'motivation', 'motivation', 'rounded', 'A restriction on the way to realise something.'),

  // Strategy
  E('resource', 'Resource', 'strategy', 'active', 'square', 'An asset owned or controlled by the enterprise.'),
  E('capability', 'Capability', 'strategy', 'behaviour', 'rounded', 'An ability that the enterprise possesses.'),
  E('courseOfAction', 'Course of Action', 'strategy', 'behaviour', 'rounded', 'An approach to achieving goals.'),
  E('valueStream', 'Value Stream', 'strategy', 'behaviour', 'rounded', 'A sequence of value-adding activities.'),

  // Business
  E('businessActor', 'Business Actor', 'business', 'active', 'square', 'An organisational entity performing behaviour.'),
  E('businessRole', 'Business Role', 'business', 'active', 'rounded', 'Responsibility for performing behaviour.'),
  E('businessCollaboration', 'Business Collaboration', 'business', 'active', 'rounded', 'Aggregate of two or more roles.'),
  E('businessProcess', 'Business Process', 'business', 'behaviour', 'rounded', 'A sequence of business behaviours.'),
  E('businessFunction', 'Business Function', 'business', 'behaviour', 'rounded', 'Behaviour grouped by required resources/skills.'),
  E('businessService', 'Business Service', 'business', 'behaviour', 'rounded', 'Explicitly defined exposed business behaviour.'),
  E('businessObject', 'Business Object', 'business', 'passive', 'square', 'A concept used within a business domain.'),
  E('businessEvent', 'Business Event', 'business', 'behaviour', 'rounded', 'A business state change.'),
  E('contract', 'Contract', 'business', 'passive', 'square', 'A formal specification of agreement.'),
  E('product', 'Product', 'business', 'passive', 'square', 'A coherent collection of services and a contract.'),

  // Application
  E('applicationComponent', 'Application Component', 'application', 'active', 'square', 'A modular, deployable part of a software system.'),
  E('applicationCollaboration', 'Application Collaboration', 'application', 'active', 'rounded', 'Aggregate of cooperating components.'),
  E('applicationInterface', 'Application Interface', 'application', 'active', 'rounded', 'A point of access for services.'),
  E('applicationFunction', 'Application Function', 'application', 'behaviour', 'rounded', 'Automated behaviour performed by a component.'),
  E('applicationProcess', 'Application Process', 'application', 'behaviour', 'rounded', 'A sequence of application behaviours.'),
  E('applicationService', 'Application Service', 'application', 'behaviour', 'rounded', 'Exposed automated behaviour.'),
  E('dataObject', 'Data Object', 'application', 'passive', 'square', 'Data structured for automated processing.'),

  // Technology
  E('node', 'Node', 'technology', 'active', 'square', 'Computational or physical resource hosting artifacts.'),
  E('device', 'Device', 'technology', 'active', 'square', 'A physical IT resource.'),
  E('systemSoftware', 'System Software', 'technology', 'active', 'rounded', 'Software environment for artifacts.'),
  E('technologyService', 'Technology Service', 'technology', 'behaviour', 'rounded', 'Exposed technology behaviour.'),
  E('technologyFunction', 'Technology Function', 'technology', 'behaviour', 'rounded', 'Technology behaviour grouped by resources.'),
  E('artifact', 'Artifact', 'technology', 'passive', 'square', 'A piece of data used or produced.'),
  E('communicationNetwork', 'Communication Network', 'technology', 'active', 'rounded', 'A set of structures connecting nodes.'),

  // Physical
  E('equipment', 'Equipment', 'physical', 'active', 'square', 'Machines/tools used to produce physical goods.'),
  E('facility', 'Facility', 'physical', 'active', 'square', 'A physical structure or environment.'),
  E('distributionNetwork', 'Distribution Network', 'physical', 'active', 'rounded', 'Physical network for transporting goods.'),
  E('material', 'Material', 'physical', 'passive', 'square', 'Tangible physical matter.'),

  // Implementation & Migration
  E('workPackage', 'Work Package', 'implementation', 'behaviour', 'rounded', 'A series of actions with defined start/end.'),
  E('deliverable', 'Deliverable', 'implementation', 'passive', 'square', 'A precisely defined result of a work package.'),
  E('implementationEvent', 'Implementation Event', 'implementation', 'behaviour', 'rounded', 'A state change related to implementation.'),
  E('plateau', 'Plateau', 'implementation', 'behaviour', 'rounded', 'A relatively stable state of the architecture.'),
  E('gap', 'Gap', 'implementation', 'passive', 'square', 'A difference between two plateaus.'),
];

export const ARCHIMATE_RELATIONSHIPS = [
  { type: 'composition', label: 'Composition', dashed: false, marker: 'diamondFilled' },
  { type: 'aggregation', label: 'Aggregation', dashed: false, marker: 'diamondOpen' },
  { type: 'assignment', label: 'Assignment', dashed: false, marker: 'ball' },
  { type: 'realization', label: 'Realization', dashed: true, marker: 'triangleOpen' },
  { type: 'serving', label: 'Serving', dashed: false, marker: 'arrowOpen' },
  { type: 'access', label: 'Access', dashed: true, marker: 'arrowOpen' },
  { type: 'influence', label: 'Influence', dashed: true, marker: 'arrowOpen' },
  { type: 'triggering', label: 'Triggering', dashed: false, marker: 'arrowFilled' },
  { type: 'flow', label: 'Flow', dashed: true, marker: 'arrowFilled' },
  { type: 'specialization', label: 'Specialization', dashed: false, marker: 'triangleOpen' },
  { type: 'association', label: 'Association', dashed: false, marker: 'none' },
];

// Viewpoint presets: each restricts the palette/model to relevant layers.
export const ARCHIMATE_VIEWPOINTS = [
  { id: 'all', name: 'All layers', layers: ARCHIMATE_LAYERS.map((l) => l.id) },
  { id: 'motivation', name: 'Motivation', layers: ['motivation'] },
  { id: 'strategy', name: 'Strategy', layers: ['strategy', 'motivation'] },
  { id: 'businessProcess', name: 'Business Process Cooperation', layers: ['business'] },
  { id: 'serviceRealization', name: 'Service Realization', layers: ['business', 'application'] },
  { id: 'applicationCooperation', name: 'Application Cooperation', layers: ['application'] },
  { id: 'applicationUsage', name: 'Application Usage', layers: ['business', 'application'] },
  { id: 'technologyUsage', name: 'Technology Usage', layers: ['application', 'technology'] },
  { id: 'infrastructure', name: 'Technology / Infrastructure', layers: ['technology', 'physical'] },
  { id: 'layered', name: 'Layered', layers: ARCHIMATE_LAYERS.map((l) => l.id) },
  { id: 'implementation', name: 'Implementation & Migration', layers: ['implementation', 'business', 'application', 'technology'] },
];

export const ARCHIMATE_ELEMENT_MAP = Object.fromEntries(
  ARCHIMATE_ELEMENTS.map((e) => [e.type, e])
);
