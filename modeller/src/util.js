// Small, dependency-free helpers shared across the app.

/** Generate a stable, collision-resistant id with an optional prefix. */
export function uid(prefix = 'id') {
  const rnd = Math.random().toString(36).slice(2, 8);
  const time = Date.now().toString(36).slice(-4);
  return `${prefix}_${time}${rnd}`;
}

/** Deep clone via structuredClone with a JSON fallback for older engines. */
export function clone(value) {
  if (typeof structuredClone === 'function') return structuredClone(value);
  return JSON.parse(JSON.stringify(value));
}

/** Clamp a number to a range. */
export function clamp(n, min, max) {
  return Math.min(max, Math.max(min, n));
}

/** Debounce a function by `wait` ms. */
export function debounce(fn, wait = 200) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}

/**
 * Escape a string for safe insertion as HTML text content.
 * The canvas and panels never use innerHTML with raw user content, but this
 * is used for the few places where templated markup is unavoidable.
 */
export function escapeHtml(value) {
  if (value == null) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Validate that a string is a safe href. We only allow http(s), mailto and
 * relative links — this blocks javascript: and data: URLs from imported models.
 */
export function safeHref(value) {
  if (typeof value !== 'string') return null;
  const v = value.trim();
  if (/^(https?:|mailto:)/i.test(v)) return v;
  if (/^[/.#]/.test(v)) return v;
  return null;
}

/** Create an element with attributes and children. */
export function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  applyAttrs(node, attrs);
  appendChildren(node, children);
  return node;
}

/** Create an SVG element in the correct namespace. */
export function svgEl(tag, attrs = {}, children = []) {
  const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
  applyAttrs(node, attrs, true);
  appendChildren(node, children);
  return node;
}

function applyAttrs(node, attrs, isSvg = false) {
  for (const [key, val] of Object.entries(attrs)) {
    if (val == null || val === false) continue;
    if (key === 'class') node.setAttribute('class', val);
    else if (key === 'text') node.textContent = val;
    else if (key === 'html') node.innerHTML = val; // only for trusted, app-generated markup
    else if (key === 'dataset') {
      for (const [dk, dv] of Object.entries(val)) node.dataset[dk] = dv;
    } else if (key.startsWith('on') && typeof val === 'function') {
      node.addEventListener(key.slice(2).toLowerCase(), val);
    } else if (key === 'style' && typeof val === 'object') {
      Object.assign(node.style, val);
    } else if (!isSvg && key in node && key !== 'list') {
      try { node[key] = val; } catch { node.setAttribute(key, val); }
    } else {
      node.setAttribute(key, val);
    }
  }
}

function appendChildren(node, children) {
  const list = Array.isArray(children) ? children : [children];
  for (const child of list) {
    if (child == null || child === false) continue;
    node.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
  }
}

/** Download a Blob or string as a file from the browser. */
export function downloadFile(filename, content, mime = 'application/octet-stream') {
  const blob = content instanceof Blob ? content : new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** Read a File object as text (Promise). */
export function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    reader.readAsText(file);
  });
}

/** Open the OS file picker and resolve with the chosen File(s). */
export function pickFile(accept = '', multiple = false) {
  return new Promise((resolve) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = accept;
    input.multiple = multiple;
    input.onchange = () => resolve(multiple ? Array.from(input.files) : input.files[0]);
    input.click();
  });
}

/** Snap a value to a grid size. */
export function snap(value, grid) {
  return Math.round(value / grid) * grid;
}

/** Simple CSV serialisation that quotes fields containing separators. */
export function toCsv(rows) {
  return rows
    .map((row) => row.map(csvCell).join(','))
    .join('\r\n');
}

function csvCell(value) {
  const s = value == null ? '' : String(value);
  if (/[",\r\n]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
  return s;
}

/** Minimal CSV parser handling quoted fields and embedded newlines. */
export function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = '';
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; }
        else inQuotes = false;
      } else field += c;
    } else if (c === '"') {
      inQuotes = true;
    } else if (c === ',') {
      row.push(field); field = '';
    } else if (c === '\n') {
      row.push(field); rows.push(row); row = []; field = '';
    } else if (c === '\r') {
      // ignore, handled by \n
    } else {
      field += c;
    }
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  return rows.filter((r) => r.length > 1 || (r.length === 1 && r[0] !== ''));
}
