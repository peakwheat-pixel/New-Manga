/**
 * DISPLAY-PERF-DECISION-1 / baseline — AC2 + AC3 measurement driver.
 *
 * Runs against the live measurement session (session.mjs) over its loopback
 * control surface. Every number is written to
 *   verification/DISPLAY-PERF-DECISION-1/baseline/{ac2,ac3}/...
 * as raw JSON so it can be re-derived.
 *
 * Nothing here monkey-patches product code; it observes the real DOM/IPC/custom
 * protocol path and, for page turns, invokes the product's own handler through
 * the real button element.
 */

import { writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";

import { EVIDENCE_ROOT } from "./env.mjs";

const CTL = process.env.DP1_CTL || "http://127.0.0.1:9362";
const AC3_DIR = path.join(EVIDENCE_ROOT, "ac3");
const AC2_DIR = path.join(EVIDENCE_ROOT, "ac2");
mkdirSync(AC3_DIR, { recursive: true });
mkdirSync(AC2_DIR, { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function post(route, payload) {
  const res = await fetch(`${CTL}${route}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload ?? {}),
  });
  const text = await res.text();
  let parsed;
  try { parsed = JSON.parse(text); } catch { parsed = { raw: text }; }
  return parsed;
}

async function ev(expr) {
  const r = await post("/eval", { expr });
  if (!r.ok) throw new Error(`eval failed: ${JSON.stringify(r).slice(0, 600)}`);
  return r.value;
}

const median = (xs) => {
  const a = xs.filter((v) => typeof v === "number" && Number.isFinite(v)).sort((x, y) => x - y);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
};
const pct = (xs, p) => {
  const a = xs.filter((v) => typeof v === "number" && Number.isFinite(v)).sort((x, y) => x - y);
  if (!a.length) return null;
  return a[Math.max(0, Math.ceil((p / 100) * a.length) - 1)];
};
const r3 = (v) => (typeof v === "number" ? Math.round(v * 1000) / 1000 : v);
const stats = (xs) => ({
  n: xs.filter((v) => typeof v === "number" && Number.isFinite(v)).length,
  median: r3(median(xs)), min: r3(Math.min(...xs.filter(Number.isFinite))), max: r3(Math.max(...xs.filter(Number.isFinite))),
  p95: r3(pct(xs, 95)),
});

/* ------------------------------------------------------------------ AC3 */

const METRICS_JS = `(() => {
  const img = document.querySelector('[data-testid="reader-page-image"]');
  const area = img ? img.parentElement : null;
  const r = img ? img.getBoundingClientRect() : null;
  const ar = area ? area.getBoundingClientRect() : null;
  const cs = img ? getComputedStyle(img) : null;
  const controls = Array.from(document.querySelectorAll('button, [role="button"], input, select'))
    .map((b) => ({ t: b.getAttribute('data-testid') || '', a: b.getAttribute('aria-label') || '', txt: (b.textContent || '').trim().slice(0, 20) }))
    .filter((b) => /zoom|缩放|放大|缩小|fit|适应|width|宽度|scale/i.test(b.t + ' ' + b.a + ' ' + b.txt));
  return {
    dpr: window.devicePixelRatio,
    innerWidth: window.innerWidth, innerHeight: window.innerHeight,
    screen: { w: window.screen.width, h: window.screen.height, availW: window.screen.availWidth, availH: window.screen.availHeight },
    pager: document.querySelector('[data-testid="reader-pager"]')?.textContent ?? null,
    layout: document.querySelector('[data-testid="reader-layout"]')?.textContent ?? null,
    img: img ? {
      naturalW: img.naturalWidth, naturalH: img.naturalHeight,
      renderedW: +r.width.toFixed(2), renderedH: +r.height.toFixed(2),
      cssMaxW: cs.maxWidth, cssMaxH: cs.maxHeight, objectFit: cs.objectFit, srcScheme: (img.getAttribute('src') || '').split(':')[0],
    } : null,
    area: ar ? { w: +ar.width.toFixed(2), h: +ar.height.toFixed(2) } : null,
    renderScaleCss: img && img.naturalWidth ? +(r.width / img.naturalWidth).toFixed(4) : null,
    renderScalePhysical: img && img.naturalWidth ? +((r.width * window.devicePixelRatio) / img.naturalWidth).toFixed(4) : null,
    zoomControls: controls,
    scrollables: Array.from(document.querySelectorAll('*')).filter((el) => el.scrollHeight > el.clientHeight + 4 && getComputedStyle(el).overflowY !== 'visible').slice(0, 6)
      .map((el) => ({ tag: el.tagName, cls: String(el.className).slice(0, 40), sh: el.scrollHeight, ch: el.clientHeight })),
    docScroll: { sh: document.documentElement.scrollHeight, ch: document.documentElement.clientHeight, sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth },
  };
})()`;

const TURN_JS = (direction) => `(async () => {
  const sel = '[data-testid="reader-page-image"]';
  const before = document.querySelector(sel)?.getAttribute('src') || null;
  const btn = document.querySelector(${JSON.stringify(direction > 0 ? "[data-testid='reader-next']" : "[data-testid='reader-prev']")});
  if (!btn) return { blocked: true, reason: 'no button' };
  if (btn.disabled) return { blocked: true, reason: 'disabled' };
  const marks = {};
  const t0 = performance.now();
  let resolveChange;
  const changeP = new Promise((res) => { resolveChange = res; });
  const obs = new MutationObserver(() => {
    const img = document.querySelector(sel);
    const src = img ? img.getAttribute('src') : null;
    if (src && src !== before) {
      if (marks.srcChanged == null) marks.srcChanged = performance.now();
      resolveChange(src);
    }
  });
  obs.observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['src'] });
  const timer = setTimeout(() => resolveChange(null), 20000);
  btn.click();
  const newSrc = await changeP;
  clearTimeout(timer);
  marks.changeAt = performance.now();
  let decodeInfo = null;
  if (newSrc) {
    for (let i = 0; i < 400; i++) {
      const img = document.querySelector(sel);
      if (img && img.getAttribute('src') === newSrc) {
        try { await img.decode(); } catch (e) { decodeInfo = String(e && e.message ? e.message : e); }
        marks.decodeDone = performance.now();
        decodeInfo = decodeInfo || { w: img.naturalWidth, h: img.naturalHeight };
        break;
      }
      await new Promise((r) => setTimeout(r, 5));
    }
  }
  marks.painted = await new Promise((res) => requestAnimationFrame(() => requestAnimationFrame(() => res(performance.now()))));
  obs.disconnect();
  const out = { t0, marks: {}, newSrcScheme: (newSrc || '').split(':')[0], decodeInfo };
  for (const k of Object.keys(marks)) out.marks[k] = +marks[k].toFixed(3);
  out.deltas = {};
  for (const k of Object.keys(marks)) out.deltas[k] = +(marks[k] - t0).toFixed(2);
  const img = document.querySelector(sel);
  out.after = img ? { naturalW: img.naturalWidth, naturalH: img.naturalHeight, renderedW: +img.getBoundingClientRect().width.toFixed(2), renderedH: +img.getBoundingClientRect().height.toFixed(2) } : null;
  out.pagerAfter = document.querySelector('[data-testid="reader-pager"]')?.textContent ?? null;
  return out;
})()`;

const FPS_START = `(() => {
  if (window.__dpFps && window.__dpFps.running) return { already: true };
  const samples = [];
  let last = null;
  const t0 = performance.now();
  const state = { samples, t0, running: true };
  function onFrame(ts) {
    if (!state.running) return;
    if (last != null) samples.push({ t: +ts.toFixed(3), dt: +(ts - last).toFixed(3), fps: +((1000 / (ts - last))).toFixed(2) });
    last = ts;
    requestAnimationFrame(onFrame);
  }
  state.stop = () => { state.running = false; state.endedAt = performance.now(); return state; };
  window.__dpFps = state;
  requestAnimationFrame(onFrame);
  return { started: true, t0 };
})()`;

const FPS_STOP = `(() => {
  const s = window.__dpFps;
  if (!s) return { error: 'no sampler' };
  s.running = false;
  s.endedAt = performance.now();
  const dts = s.samples.map((x) => x.dt);
  const sorted = [...dts].sort((a, b) => a - b);
  const n = sorted.length;
  const avg = n ? dts.reduce((a, b) => a + b, 0) / n : null;
  const p95 = n ? sorted[Math.max(0, Math.ceil(0.95 * n) - 1)] : null;
  const max = n ? sorted[n - 1] : null;
  return {
    durationMs: +(s.endedAt - s.t0).toFixed(1),
    samples: n,
    avgFrameMs: avg == null ? null : +avg.toFixed(3),
    avgFps: avg ? +(1000 / avg).toFixed(2) : null,
    p95FrameMs: p95 == null ? null : +p95.toFixed(3),
    p95Fps: p95 ? +(1000 / p95).toFixed(2) : null,
    maxFrameMs: max == null ? null : +max.toFixed(3),
    minFps: max ? +(1000 / max).toFixed(2) : null,
    csv: ['seq,frame_ts_ms,frame_time_ms,instant_fps'].concat(s.samples.map((x, i) => [i + 1, x.t, x.dt, x.fps].join(','))).join('\\n'),
    raw: s.samples,
  };
})()`;

/* ------------------------------------------------------------------ AC2 */

const AC2_JS = (pageId, pageIndex) => `(async () => {
  const inv = window.__TAURI__.core.invoke;
  const tryInvoke = async (cmd, args) => {
    try { return await inv(cmd, args); } catch (e) {
      if (String(e).includes('invalid args')) {
        const snake = {};
        for (const k of Object.keys(args)) snake[k.replace(/[A-Z]/g, (m) => '_' + m.toLowerCase())] = args[k];
        return await inv(cmd, snake);
      }
      throw e;
    }
  };
  const out = { pageId: ${JSON.stringify(pageId)}, pageIndex: ${Number(pageIndex)} };
  let t = performance.now();
  const resolved = await tryInvoke('resolve_page_resource', { pageId: ${JSON.stringify(pageId)} });
  out.resolveMs = +(performance.now() - t).toFixed(3);
  out.resolveShape = { hasResourceId: !!resolved?.resource_id, hasRevision: !!resolved?.revision };

  t = performance.now();
  const issued = await tryInvoke('issue_resource_url', { resourceId: resolved.resource_id, revision: resolved.revision });
  out.issueMs = +(performance.now() - t).toFixed(3);
  out.size = issued?.size ?? null;
  out.urlHost = (issued?.url || '').split('/')[2] || null;

  // valid chunk: host does Core resolve + full-file streaming SHA-256 + serve
  t = performance.now();
  const resp = await fetch(issued.url + '?chunk=0');
  const buf = await resp.arrayBuffer();
  out.chunkMs = +(performance.now() - t).toFixed(3);
  out.chunkStatus = resp.status;
  out.chunkBytes = buf.byteLength;

  // resolve-only control: chunk index 1 on a 1-chunk file is rejected BEFORE
  // verify_and_serve (resource_protocol.rs: chunk_offset validated, then digest)
  t = performance.now();
  const bad = await fetch(issued.url + '?chunk=1');
  await bad.arrayBuffer();
  out.rejectedChunkMs = +(performance.now() - t).toFixed(3);
  out.rejectedChunkStatus = bad.status;

  // Blob assembly (client.ts fetchAll -> new Blob(parts))
  t = performance.now();
  const blob = new Blob([buf], { type: 'application/octet-stream' });
  const url = URL.createObjectURL(blob);
  out.blobMs = +(performance.now() - t).toFixed(3);

  // decode first frame from the blob URL
  t = performance.now();
  const img = new Image();
  img.src = url;
  let decodeError = null;
  try { await img.decode(); } catch (e) { decodeError = String(e); }
  out.decodeMs = +(performance.now() - t).toFixed(3);
  out.decodeError = decodeError;
  out.natural = { w: img.naturalWidth, h: img.naturalHeight };
  URL.revokeObjectURL(url);

  // WebCrypto SHA-256 over the same bytes: an independent reference for the
  // per-request hashing cost the host pays (hardware SHA-NI in both cases).
  t = performance.now();
  const digest = await crypto.subtle.digest('SHA-256', buf);
  out.webCryptoShaMs = +(performance.now() - t).toFixed(3);
  out.sha256HexPrefix = [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join('').toUpperCase().slice(0, 16);

  out.hostHashMsEstimate = +(out.chunkMs - out.rejectedChunkMs).toFixed(3);
  out.pipelineNoDecodeMs = +(out.resolveMs + out.issueMs + out.chunkMs + out.blobMs).toFixed(3);
  return out;
})()`;

async function shot(name) {
  const r = await post("/shot", { name });
  return r.file;
}

async function runAc3() {
  const result = { capturedAt: new Date().toISOString(), steps: [] };

  // --- A3-1 real window (DPR as configured by the OS) ---
  const metricsDpr1 = await ev(METRICS_JS);
  result.steps.push({ step: "metrics-native-window", value: metricsDpr1 });
  result.shotDpr1 = await shot("ac3-reader-native-window");

  // --- A3-2 DPR2 emulation (1180x860 CSS px @ deviceScaleFactor 2) ---
  const dpr = await post("/dpr", { dpr: 2, width: 1180, height: 860 });
  result.dprOverride = dpr.page;
  await sleep(500);
  const metricsDpr2 = await ev(METRICS_JS);
  result.steps.push({ step: "metrics-dpr2", value: metricsDpr2 });
  result.shotDpr2 = await shot("ac3-reader-dpr2");

  // --- A3-3 page turns at DPR2 ---
  const turns = [];
  for (let i = 0; i < 10; i += 1) {
    const turn = await ev(TURN_JS(-1));
    turns.push(turn);
    if (turn.blocked) break;
    await sleep(180);
  }
  result.steps.push({ step: "page-turns", value: turns });
  const deltas = turns.filter((t) => t.deltas).map((t) => t.deltas);
  result.turnSummary = {
    turns: deltas.length,
    srcChangeMs: stats(deltas.map((d) => d.srcChanged)),
    decodeDoneMs: stats(deltas.map((d) => d.decodeDone)),
    paintedMs: stats(deltas.map((d) => d.painted)),
    raw: deltas,
  };

  // --- A3-4 rAF FPS sampling: page-turn stream (10 s) ---
  await post("/dpr-off", {});
  await sleep(300);
  const fpsTurn = await (async () => {
    await ev(FPS_START);
    const started = Date.now();
    let n = 0;
    while (Date.now() - started < 10000) {
      await ev(TURN_JS(-1));
      n += 1;
      if (n > 200) break;
    }
    return { turnsDuringSample: n, ...(await ev(FPS_STOP)) };
  })();
  result.steps.push({ step: "fps-page-turn-stream", value: { ...fpsTurn, raw: undefined } });
  result.fpsTurn = fpsTurn;

  // --- A3-5 rAF FPS sampling: wheel/scroll attempt on the reader page area (5 s) ---
  const fpsScroll = await (async () => {
    await ev(FPS_START);
    const started = Date.now();
    while (Date.now() - started < 5000) {
      await ev(`(() => {
        const img = document.querySelector('[data-testid="reader-page-image"]');
        const target = img ? img.parentElement : document.scrollingElement;
        if (target) {
          target.dispatchEvent(new WheelEvent('wheel', { deltaY: 600, bubbles: true, cancelable: true }));
          try { target.scrollTop = Math.min(target.scrollHeight, target.scrollTop + 600); } catch {}
        }
        window.scrollBy(0, 200);
        return target ? { sh: target.scrollHeight, ch: target.clientHeight, st: target.scrollTop } : null;
      })()`);
      await sleep(120);
    }
    return await ev(FPS_STOP);
  })();
  result.steps.push({ step: "fps-scroll-attempt", value: { ...fpsScroll, raw: undefined } });
  result.fpsScroll = fpsScroll;

  // --- A3-6 idle FPS (3 s) ---
  const fpsIdle = await (async () => {
    await ev(FPS_START);
    await sleep(3000);
    return await ev(FPS_STOP);
  })();
  result.steps.push({ step: "fps-idle", value: { ...fpsIdle, raw: undefined } });
  result.fpsIdle = fpsIdle;

  // --- A3-7 scrollability facts ---
  result.scrollFacts = await ev(`(() => {
    const img = document.querySelector('[data-testid="reader-page-image"]');
    const area = img ? img.parentElement : null;
    return {
      docScrollHeight: document.documentElement.scrollHeight,
      docClientHeight: document.documentElement.clientHeight,
      docCanScroll: document.documentElement.scrollHeight > document.documentElement.clientHeight + 4,
      imgParentScrollHeight: area ? area.scrollHeight : null,
      imgParentClientHeight: area ? area.clientHeight : null,
      imgParentOverflowY: area ? getComputedStyle(area).overflowY : null,
      imgMaxHeight: img ? getComputedStyle(img).maxHeight : null,
    };
  })()`);

  const file = path.join(AC3_DIR, "ac3-measurements.json");
  writeFileSync(file, JSON.stringify(result, null, 2), "utf8");
  writeFileSync(path.join(AC3_DIR, "fps-page-turns.csv"), result.fpsTurn?.csv || "", "utf8");
  writeFileSync(path.join(AC3_DIR, "fps-scroll-attempt.csv"), result.fpsScroll?.csv || "", "utf8");
  writeFileSync(path.join(AC3_DIR, "fps-idle.csv"), result.fpsIdle?.csv || "", "utf8");
  return { file, result };
}

async function runAc2() {
  const pages = await ev(`(async () => {
    try {
      const r = await window.__TAURI__.core.invoke('list_chapter_pages', { chapterId: ${JSON.stringify(process.env.DP1_CHAPTER || "699cc91849414874a6e54f0dac6d7770")} });
      return (r?.pages || []).map((p) => ({ page_id: p.page_id, order: p.sort_order, name: p.source_filename }));
    } catch (e) { return { error: String(e) }; }
  })()`);
  if (!Array.isArray(pages) || pages.length === 0) {
    const out = { capturedAt: new Date().toISOString(), blocked: true, pages };
    const file = path.join(AC2_DIR, "ac2-stages.json");
    writeFileSync(file, JSON.stringify(out, null, 2), "utf8");
    return { file, result: out };
  }

  // three pages of different byte sizes to expose the per-request cost slope
  const samples = [];
  const targets = [pages[0], pages[Math.floor(pages.length / 2)], pages[pages.length - 1]];
  for (const page of targets) {
    for (let i = 0; i < 4; i += 1) {
      const r = await ev(AC2_JS(page.page_id, page.order));
      samples.push({ ...r, pageName: page.name, iteration: i });
      await sleep(60);
    }
  }

  const byPage = {};
  for (const s of samples) {
    const key = s.pageId;
    byPage[key] = byPage[key] || { pageId: key, pageName: s.pageName, size: s.size, natural: s.natural, runs: [] };
    byPage[key].runs.push(s);
  }
  const perPage = Object.values(byPage).map((p) => ({
    pageId: p.pageId,
    pageName: p.pageName,
    sizeBytes: p.size,
    natural: p.natural,
    resolveMs: stats(p.runs.map((r) => r.resolveMs)),
    issueMs: stats(p.runs.map((r) => r.issueMs)),
    chunkMs: stats(p.runs.map((r) => r.chunkMs)),
    rejectedChunkMs: stats(p.runs.map((r) => r.rejectedChunkMs)),
    hostHashMsEstimate: stats(p.runs.map((r) => r.hostHashMsEstimate)),
    blobMs: stats(p.runs.map((r) => r.blobMs)),
    decodeMs: stats(p.runs.map((r) => r.decodeMs)),
    webCryptoShaMs: stats(p.runs.map((r) => r.webCryptoShaMs)),
    pipelineNoDecodeMs: stats(p.runs.map((r) => r.pipelineNoDecodeMs)),
    shaPrefixes: p.runs.map((r) => r.sha256HexPrefix),
    rejectedStatuses: p.runs.map((r) => r.rejectedChunkStatus),
    chunkStatuses: p.runs.map((r) => r.chunkStatus),
  }));

  // byte-size slope: chunk cost per byte across the three page sizes
  const slope = perPage.length >= 2
    ? (() => {
        const pts = perPage.map((p) => ({ x: p.sizeBytes, y: p.chunkMs.median })).filter((p) => p.x && p.y);
        const n = pts.length;
        const sx = pts.reduce((a, p) => a + p.x, 0);
        const sy = pts.reduce((a, p) => a + p.y, 0);
        const sxx = pts.reduce((a, p) => a + p.x * p.x, 0);
        const sxy = pts.reduce((a, p) => a + p.x * p.y, 0);
        const denom = n * sxx - sx * sx;
        const b = denom === 0 ? null : (n * sxy - sx * sy) / denom; // ms per byte
        const a = b == null ? null : (sy - b * sx) / n;
        return { points: pts, slopeMsPerMb: b == null ? null : r3(b * 1024 * 1024), interceptMs: r3(a), impliedHostScanMbPerSec: b ? r3(1000 / (b * 1024 * 1024)) : null };
      })()
    : null;

  const result = { capturedAt: new Date().toISOString(), samples: samples.length, perPage, slope };
  const file = path.join(AC2_DIR, "ac2-stages.json");
  writeFileSync(file, JSON.stringify(result, null, 2), "utf8");
  return { file, result };
}

const which = process.argv[2] || "all";
const out = {};
if (which === "ac3" || which === "all") out.ac3 = await runAc3();
if (which === "ac2" || which === "all") out.ac2 = await runAc2();
process.stdout.write(`${JSON.stringify({ ac3: out.ac3?.file, ac3Turn: out.ac3?.result?.turnSummary, fps: { turn: out.ac3?.result?.fpsTurn && { avg: out.ac3.result.fpsTurn.avgFps, p95: out.ac3.result.fpsTurn.p95Fps, samples: out.ac3.result.fpsTurn.samples }, scroll: out.ac3?.result?.fpsScroll && { avg: out.ac3.result.fpsScroll.avgFps, p95: out.ac3.result.fpsScroll.p95Fps }, idle: out.ac3?.result?.fpsIdle && { avg: out.ac3.result.fpsIdle.avgFps, p95: out.ac3.result.fpsIdle.p95Fps } }, metrics: out.ac3?.result?.steps?.slice(0, 2), ac2: out.ac2?.result?.perPage, slope: out.ac2?.result?.slope }, null, 2)}\n`);

