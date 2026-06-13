// Built-in templates and sample models. Each builder returns a fresh model
// object ready to hand to store.replaceModel(). They double as starter content
// and as a demonstration of the model-first / drill-down structure.

import { createModel, makeObject, makeRelationship, makeDiagram, makeTag } from './model.js';

function build(name, fn) {
  const m = createModel(name);
  const ctx = {
    m,
    obj(type, props) { const o = makeObject(type, props); m.objects[o.id] = o; return o; },
    rel(s, t, type, props) { const r = makeRelationship(s.id, t.id, type, props); m.relationships[r.id] = r; return r; },
    tag(name, color, group) { const t = makeTag({ name, color, group }); m.tags[t.id] = t; return t; },
    diagram(props, layout) {
      const d = makeDiagram(props);
      m.diagrams[d.id] = d; m.diagramOrder.push(d.id);
      for (const [id, pos] of Object.entries(layout || {})) d.nodes[id] = pos;
      return d;
    },
  };
  fn(ctx);
  return m;
}

// Blank starters -----------------------------------------------------------
export function blankC4Context() {
  return build('C4 System Context', ({ diagram }) => {
    diagram({ name: 'System Context', kind: 'c4-context', notation: 'c4', level: 'context' });
  });
}
export function blankC4Container() {
  return build('C4 Container', ({ diagram }) => {
    diagram({ name: 'Containers', kind: 'c4-container', notation: 'c4', level: 'container' });
  });
}
export function blankArchimateApplication() {
  return build('ArchiMate Application', ({ diagram }) => {
    diagram({ name: 'Application Cooperation', kind: 'archimate-layer', notation: 'archimate', viewpoint: 'applicationCooperation' });
  });
}
export function blankArchimateLayered() {
  return build('ArchiMate Layered', ({ diagram }) => {
    diagram({ name: 'Layered View', kind: 'archimate-crosslayer', notation: 'archimate', viewpoint: 'layered' });
  });
}

// Sample: enterprise architecture (ArchiMate layered) ----------------------
export function sampleEnterprise() {
  return build('Sample — Enterprise Architecture', (c) => {
    const goal = c.obj('goal', { name: 'Grow online revenue', shortDescription: 'Strategic goal' });
    const cap = c.obj('capability', { name: 'Order Management', shortDescription: 'Strategic capability' });
    const proc = c.obj('businessProcess', { name: 'Handle Customer Order' });
    const svc = c.obj('businessService', { name: 'Order Service' });
    const app = c.obj('applicationComponent', { name: 'Order Management System', technology: 'Java' });
    const appSvc = c.obj('applicationService', { name: 'Order API' });
    const data = c.obj('dataObject', { name: 'Order' });
    const node = c.obj('node', { name: 'Kubernetes Cluster', technology: 'AWS EKS' });
    const db = c.obj('systemSoftware', { name: 'PostgreSQL', technology: 'RDS' });

    c.rel(cap, goal, 'realization', { label: 'realises' });
    c.rel(proc, svc, 'realization');
    c.rel(appSvc, proc, 'serving', { label: 'supports' });
    c.rel(app, appSvc, 'realization');
    c.rel(app, data, 'access', { label: 'reads/writes' });
    c.rel(node, app, 'assignment', { label: 'hosts' });
    c.rel(db, app, 'serving', { label: 'persistence' });

    c.diagram({ name: 'Layered View', kind: 'archimate-crosslayer', notation: 'archimate', viewpoint: 'layered' }, {
      [goal.id]: { x: 360, y: 40 },
      [cap.id]: { x: 360, y: 180 },
      [proc.id]: { x: 80, y: 320 },
      [svc.id]: { x: 360, y: 320 },
      [appSvc.id]: { x: 360, y: 460 },
      [app.id]: { x: 80, y: 600 },
      [data.id]: { x: 360, y: 600 },
      [node.id]: { x: 80, y: 760 },
      [db.id]: { x: 360, y: 760 },
    });
  });
}

// Sample: microservices (C4 with drill-down) -------------------------------
export function sampleMicroservices() {
  return build('Sample — Microservices', (c) => {
    const customer = c.obj('person', { name: 'Customer', shortDescription: 'A shopper using the store' });
    const shop = c.obj('softwareSystem', { name: 'E-Commerce Platform', shortDescription: 'Online retail system' });
    const payment = c.obj('externalSystem', { name: 'Payment Gateway', shortDescription: 'Third-party payments' });
    const email = c.obj('externalSystem', { name: 'Email Provider' });

    c.rel(customer, shop, 'uses', { label: 'Browses & orders', technology: 'HTTPS' });
    c.rel(shop, payment, 'uses', { label: 'Takes payment', technology: 'REST' });
    c.rel(shop, email, 'uses', { label: 'Sends mail', technology: 'SMTP' });

    // Containers (children of shop)
    const web = c.obj('container', { name: 'Web App', technology: 'React', parentId: shop.id });
    const api = c.obj('container', { name: 'API Gateway', technology: 'Node.js', parentId: shop.id });
    const orders = c.obj('container', { name: 'Orders Service', technology: 'Go', parentId: shop.id });
    const catalog = c.obj('container', { name: 'Catalog Service', technology: 'Java', parentId: shop.id });
    const db = c.obj('database', { name: 'Orders DB', technology: 'PostgreSQL', parentId: shop.id });

    c.rel(customer, web, 'uses', { label: 'Uses', technology: 'HTTPS' });
    c.rel(web, api, 'uses', { label: 'Calls', technology: 'JSON/HTTPS' });
    c.rel(api, orders, 'uses', { label: 'Routes', technology: 'gRPC' });
    c.rel(api, catalog, 'uses', { label: 'Routes', technology: 'gRPC' });
    c.rel(orders, db, 'writes', { label: 'Reads/writes', technology: 'SQL' });
    c.rel(orders, payment, 'uses', { label: 'Charges', technology: 'REST' });

    const tagCore = c.tag('core', '#2563eb', 'domain');
    const tagEdge = c.tag('edge', '#16a34a', 'domain');
    web.tags = ['edge']; api.tags = ['edge']; orders.tags = ['core']; catalog.tags = ['core'];

    const ctx = c.diagram({ name: 'System Context', kind: 'c4-context', notation: 'c4', level: 'context' }, {
      [customer.id]: { x: 360, y: 60 },
      [shop.id]: { x: 360, y: 280 },
      [payment.id]: { x: 80, y: 500 },
      [email.id]: { x: 640, y: 500 },
    });
    // Container view scoped to shop — drill target
    c.diagram({ name: 'E-Commerce Platform — container', kind: 'c4-container', notation: 'c4', level: 'container', scopeId: shop.id }, {
      [customer.id]: { x: 60, y: 40 },
      [web.id]: { x: 60, y: 220 },
      [api.id]: { x: 360, y: 220 },
      [orders.id]: { x: 300, y: 420 },
      [catalog.id]: { x: 560, y: 420 },
      [db.id]: { x: 300, y: 620 },
      [payment.id]: { x: 60, y: 620 },
    });
  });
}

// Sample: cloud-native technology view -------------------------------------
export function sampleCloudNative() {
  return build('Sample — Cloud Native', (c) => {
    const user = c.obj('person', { name: 'End User' });
    const cdn = c.obj('node', { name: 'CDN / Edge', technology: 'CloudFront' });
    const lb = c.obj('node', { name: 'Load Balancer', technology: 'ALB' });
    const k8s = c.obj('node', { name: 'Kubernetes', technology: 'EKS' });
    const svcA = c.obj('applicationComponent', { name: 'Frontend', technology: 'Next.js' });
    const svcB = c.obj('applicationComponent', { name: 'Backend API', technology: 'FastAPI' });
    const queue = c.obj('systemSoftware', { name: 'Event Bus', technology: 'Kafka' });
    const store = c.obj('artifact', { name: 'Object Store', technology: 'S3' });

    c.rel(user, cdn, 'serving', { technology: 'HTTPS' });
    c.rel(cdn, lb, 'serving');
    c.rel(lb, k8s, 'serving');
    c.rel(k8s, svcA, 'assignment', { label: 'hosts' });
    c.rel(k8s, svcB, 'assignment', { label: 'hosts' });
    c.rel(svcA, svcB, 'serving', { technology: 'REST' });
    c.rel(svcB, queue, 'flow', { label: 'publishes' });
    c.rel(svcB, store, 'access', { label: 'stores' });

    c.diagram({ name: 'Technology / Infrastructure', kind: 'archimate-layer', notation: 'archimate', viewpoint: 'infrastructure' }, {
      [user.id]: { x: 360, y: 40 },
      [cdn.id]: { x: 360, y: 200 },
      [lb.id]: { x: 360, y: 340 },
      [k8s.id]: { x: 360, y: 480 },
      [svcA.id]: { x: 120, y: 660 },
      [svcB.id]: { x: 420, y: 660 },
      [queue.id]: { x: 700, y: 660 },
      [store.id]: { x: 700, y: 480 },
    });
  });
}

// Sample: transformation roadmap (current → future) ------------------------
export function sampleRoadmap() {
  return build('Sample — Transformation Roadmap', (c) => {
    const now = c.obj('plateau', { name: 'Current State', lifecycle: 'current' });
    const mid = c.obj('plateau', { name: 'Transition State', lifecycle: 'future' });
    const future = c.obj('plateau', { name: 'Target State', lifecycle: 'future' });
    const gap = c.obj('gap', { name: 'Capability Gap' });
    const wp1 = c.obj('workPackage', { name: 'Migrate to Cloud', lifecycle: 'future' });
    const wp2 = c.obj('workPackage', { name: 'Decommission Legacy', lifecycle: 'future' });
    const legacy = c.obj('applicationComponent', { name: 'Legacy Monolith', lifecycle: 'removed' });
    const cloud = c.obj('applicationComponent', { name: 'Cloud Platform', lifecycle: 'future' });

    c.rel(now, mid, 'triggering', { label: 'phase 1' });
    c.rel(mid, future, 'triggering', { label: 'phase 2' });
    c.rel(gap, future, 'association', { label: 'closes' });
    c.rel(wp1, mid, 'realization');
    c.rel(wp2, future, 'realization');
    c.rel(wp2, legacy, 'association', { label: 'removes' });
    c.rel(wp1, cloud, 'association', { label: 'delivers' });

    c.tag('phase-1', '#f59e0b', 'lifecycle');
    c.tag('phase-2', '#10b981', 'lifecycle');

    c.diagram({ name: 'Roadmap', kind: 'archimate-layer', notation: 'archimate', viewpoint: 'implementation' }, {
      [now.id]: { x: 60, y: 80 },
      [mid.id]: { x: 360, y: 80 },
      [future.id]: { x: 660, y: 80 },
      [wp1.id]: { x: 360, y: 280 },
      [wp2.id]: { x: 660, y: 280 },
      [gap.id]: { x: 660, y: 440 },
      [legacy.id]: { x: 360, y: 460 },
      [cloud.id]: { x: 60, y: 280 },
    });
  });
}

export const TEMPLATES = [
  { id: 'blank-c4-context', name: 'Blank — C4 Context', group: 'Blank', build: blankC4Context },
  { id: 'blank-c4-container', name: 'Blank — C4 Container', group: 'Blank', build: blankC4Container },
  { id: 'blank-archimate-app', name: 'Blank — ArchiMate Application', group: 'Blank', build: blankArchimateApplication },
  { id: 'blank-archimate-layered', name: 'Blank — ArchiMate Layered', group: 'Blank', build: blankArchimateLayered },
  { id: 'sample-enterprise', name: 'Sample — Enterprise Architecture', group: 'Samples', build: sampleEnterprise },
  { id: 'sample-microservices', name: 'Sample — Microservices (C4)', group: 'Samples', build: sampleMicroservices },
  { id: 'sample-cloud', name: 'Sample — Cloud Native', group: 'Samples', build: sampleCloudNative },
  { id: 'sample-roadmap', name: 'Sample — Transformation Roadmap', group: 'Samples', build: sampleRoadmap },
];
