// Mermaid C4 tooling for the sub-domain views: render, geometry, overlap check, label placement.
//
//   node mermaid_c4.cjs render   <diagram.mmd> <out.png>   PNG of the diagram
//   node mermaid_c4.cjs geometry <diagram.mmd>             JSON: boundaries and shapes with their boxes
//   node mermaid_c4.cjs overlaps <diagram.mmd>             texts drawn over each other, one per line
//   node mermaid_c4.cjs place    <diagram.mmd>             one UpdateRelStyle line per label to move
//
// Renders with Mermaid 11.4.1 (the version the notation was checked against) in a headless browser
// driven by Playwright, at the screen width SCREEN (Mermaid wraps rows at screen.availWidth).
// Playwright is resolved from C4_PLAYWRIGHT_DIR, then from the usual node paths; the browser is
// C4_BROWSER (a Playwright channel such as msedge or chrome), else Playwright's own Chromium, else
// the installed Edge or Chrome. Mermaid is loaded from cdn.jsdelivr.net.
const fs = require('fs');
const path = require('path');

const MERMAID = 'https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs';
const SCREEN = Number(process.env.C4_SCREEN || 1800);

function playwright() {
  const dirs = [process.env.C4_PLAYWRIGHT_DIR, process.cwd(), __dirname].filter(Boolean);
  for (const d of dirs) {
    try { return require(require.resolve('playwright', { paths: [d] })); } catch (e) { /* next */ }
  }
  throw new Error('playwright not found: set C4_PLAYWRIGHT_DIR to a folder whose node_modules holds playwright');
}

async function launch(chromium) {
  const channels = process.env.C4_BROWSER ? [process.env.C4_BROWSER] : [undefined, 'msedge', 'chrome'];
  let last;
  for (const channel of channels) {
    try { return await chromium.launch(channel ? { channel } : {}); } catch (e) { last = e; }
  }
  throw last;
}

async function withDiagram(code, fn) {
  const { chromium } = playwright();
  const browser = await launch(chromium);
  try {
    const page = await browser.newPage({ viewport: { width: SCREEN, height: 1200 } });
    await page.setContent(`<html><body style="margin:0;background:#fff"><div id="d"></div><script type="module">
      import mermaid from '${MERMAID}';
      mermaid.initialize({ startOnLoad: false });
      try { const { svg } = await mermaid.render('g', ${JSON.stringify(code)}); document.getElementById('d').innerHTML = svg; }
      catch (e) { window.err = String(e); }
      window.done = true;
    </script></body></html>`);
    await page.waitForFunction('window.done === true', null, { timeout: 90000 });
    const err = await page.evaluate(() => window.err);
    if (err) throw new Error(err);
    return await fn(page);
  } finally {
    await browser.close();
  }
}

// ---------------------------------------------------------------- geometry
function geometryInPage() {
  const svg = document.querySelector('#d svg');
  const boundaries = [], shapes = [];
  for (const g of svg.querySelectorAll('g')) {
    const kids = [...g.children];
    const rect = kids.find(k => k.tagName === 'rect');
    const shape = kids.find(k => k.tagName === 'rect' || (k.tagName === 'path' && !k.getAttribute('marker-end')));
    const texts = kids.filter(k => k.tagName === 'text').map(t => t.textContent.trim()).filter(Boolean);
    if (!shape || !texts.length) continue;
    const b = shape.getBBox();
    const item = { texts, x: Math.round(b.x), y: Math.round(b.y), w: Math.round(b.width), h: Math.round(b.height) };
    (rect && rect.getAttribute('stroke-dasharray') ? boundaries : shapes).push(item);
  }
  return { boundaries, shapes };
}

// ---------------------------------------------------------------- overlaps between texts of different groups
function overlapsInPage() {
  const svg = document.querySelector('#d svg');
  const groups = [...svg.querySelectorAll('g')];
  const paths = [...svg.querySelectorAll('path[marker-end], line[marker-end]')];
  // owner of a text: the relation whose path precedes it (label and technology line), else its group
  const owner = t => {
    let p = t.previousElementSibling;
    for (let k = 0; k < 2 && p; k++, p = p.previousElementSibling) {
      if (p.getAttribute && p.getAttribute('marker-end')) return 'rel' + paths.indexOf(p);
    }
    let g = t.parentElement; while (g && g.tagName !== 'g') g = g.parentElement;
    return 'g' + groups.indexOf(g);
  };
  const texts = [...svg.querySelectorAll('text')].map(t => {
    const b = t.getBBox();
    return { s: t.textContent.trim(), x: b.x, y: b.y, w: b.width, h: b.height, o: owner(t) };
  }).filter(t => t.s && t.w > 0);
  const out = [];
  for (let a = 0; a < texts.length; a++) for (let b = a + 1; b < texts.length; b++) {
    const A = texts[a], B = texts[b];
    if (A.o === B.o) continue;
    const ix = Math.min(A.x + A.w, B.x + B.w) - Math.max(A.x, B.x);
    const iy = Math.min(A.y + A.h, B.y + B.h) - Math.max(A.y, B.y);
    if (ix > 2 && iy > 2) out.push(`@${Math.round(A.x)},${Math.round(A.y)} "${A.s.slice(0, 50)}" x "${B.s.slice(0, 50)}"`);
  }
  return out;
}

// ---------------------------------------------------------------- label placement
// Mermaid draws a label with its left edge on the middle of its line. For every relation, try spots
// along the line (start on, centred on, ending on the line; above, on, below it) and keep the one with
// the least overlap with cards, titles and the labels already placed; longest labels first.
function placeInPage() {
  const svg = document.querySelector('#d svg');
  const bb = e => { const b = e.getBBox(); return { x: b.x, y: b.y, w: b.width, h: b.height }; };
  const relPaths = [...svg.querySelectorAll('path[marker-end], line[marker-end]')];
  const labelTexts = new Set();
  const rels = relPaths.map(p => {
    const t1 = p.nextElementSibling, t2 = t1 && t1.nextElementSibling;
    [t1, t2].forEach(t => t && labelTexts.add(t));
    const len = p.getTotalLength();
    const pts = []; for (let k = 0; k <= 20; k++) { const q = p.getPointAtLength(len * k / 20); pts.push([q.x, q.y]); }
    const w = Math.max(t1 ? t1.getComputedTextLength() : 0, t2 ? t2.getComputedTextLength() : 0);
    return { text: t1 ? t1.textContent : '', pts, w, h: 32, x0: t1 ? +t1.getAttribute('x') : 0, y0: t1 ? +t1.getAttribute('y') : 0 };
  });
  const obstacles = [];
  for (const r of svg.querySelectorAll('rect')) {
    if (r.getAttribute('stroke-dasharray')) continue;
    const b = bb(r); if (b.w > 0 && b.h > 0) obstacles.push(b);
  }
  for (const p of svg.querySelectorAll('path:not([marker-end])')) { const b = bb(p); if (b.w > 20 && b.h > 20) obstacles.push(b); }
  for (const t of svg.querySelectorAll('text')) {
    if (labelTexts.has(t) || !t.textContent.trim()) continue;
    const b = bb(t); if (b.w > 0) obstacles.push(b);
  }
  const vb = svg.viewBox.baseVal;
  return { rels, obstacles, W: vb.x + vb.width, H: vb.y + vb.height, X: vb.x, Y: vb.y };
}

function chooseOffsets(code, geo) {
  const rels = [...code.matchAll(/^\s*(?:Rel|BiRel|Rel_[UDLRB])\((\w+),\s*(\w+),\s*"([^"]*)"/gm)]
    .map(m => ({ from: m[1], to: m[2], label: m[3] }));
  if (geo.rels.length !== rels.length) throw new Error(`relations: ${rels.length} in the source, ${geo.rels.length} drawn`);
  const inter = (a, b) => Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)) *
                          Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
  const placed = [], out = [];
  const order = geo.rels.map((r, i) => i).sort((a, b) => geo.rels[b].w - geo.rels[a].w);
  for (const i of order) {
    const r = geo.rels[i], src = rels[i];
    if (!r.text.startsWith(src.label.slice(0, 20))) throw new Error(`relation order differs at ${src.from} -> ${src.to}`);
    let best = null;
    for (let k = 2; k <= 18; k++) {
      const [px, py] = r.pts[k];
      for (const ax of [0, -0.25, -0.5, -0.75, -1]) {
        for (const dy of [0, -24, 24, -48, 48, -72, 72]) {
          const box = { x: px + ax * r.w - 4, y: py + dy - 10, w: r.w + 8, h: r.h };
          let cost = 0;
          for (const o of geo.obstacles) cost += 6 * inter(box, o);
          for (const p of placed) cost += 8 * inter(box, p);
          const outX = Math.max(0, geo.X + 4 - box.x) + Math.max(0, box.x + box.w - geo.W + 4);
          const outY = Math.max(0, geo.Y - box.y) + Math.max(0, box.y + box.h - geo.H);
          cost += 400 * (outX + outY) + 5 * Math.abs(k - 10) + Math.abs(dy) + Math.abs(ax) * 20;
          if (!best || cost < best.cost) best = { cost, box, lx: px + ax * r.w + r.w / 2, ly: py + dy };
        }
      }
    }
    placed.push(best.box);
    const dx = Math.round(best.lx - r.x0), dy = Math.round(best.ly - r.y0);
    if (Math.abs(dx) > 2 || Math.abs(dy) > 2) out[i] = `  UpdateRelStyle(${src.from}, ${src.to}, $offsetX="${dx}", $offsetY="${dy}")`;
  }
  return out.filter(Boolean);
}

// ---------------------------------------------------------------- main
(async () => {
  const [cmd, src, out] = process.argv.slice(2);
  if (!cmd || !src) { console.error('usage: mermaid_c4.cjs render|geometry|overlaps|place <diagram.mmd> [out.png]'); process.exit(2); }
  let code = fs.readFileSync(src, 'utf8');
  if (cmd === 'place') code = code.split('\n').filter(l => !/^\s*UpdateRelStyle\(/.test(l)).join('\n');
  await withDiagram(code, async page => {
    if (cmd === 'render') {
      await page.locator('#d').screenshot({ path: out || src.replace(/\.mmd$/, '.png') });
      console.log(out || src.replace(/\.mmd$/, '.png'));
    } else if (cmd === 'geometry') {
      console.log(JSON.stringify(await page.evaluate(geometryInPage)));
    } else if (cmd === 'overlaps') {
      const ov = await page.evaluate(overlapsInPage);
      console.log(`overlaps ${ov.length}`); ov.forEach(o => console.log('  ' + o));
    } else if (cmd === 'place') {
      console.log(chooseOffsets(code, await page.evaluate(placeInPage)).join('\n'));
    } else {
      throw new Error(`unknown command ${cmd}`);
    }
  });
})().catch(e => { console.error(String(e)); process.exit(1); });
