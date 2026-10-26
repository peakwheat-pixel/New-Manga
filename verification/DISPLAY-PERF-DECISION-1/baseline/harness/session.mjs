/**
 * DISPLAY-PERF-DECISION-1 / baseline — interactive measurement session.
 *
 * Launches the CDP-enabled acceptance build (identical product code + the
 * window's additionalBrowserArgs from the repo's own tauri.acceptance.conf,
 * only the debug port moved to 9361 so it satisfies the >=9360 rule), attaches
 * over CDP, and exposes a tiny HTTP control surface on loopback so measurement
 * steps can be driven across separate tool calls (the native import dialog has
 * to be worked from outside the WebView).
 *
 * Control surface (all under http://127.0.0.1:<port>):
 *   GET  /status                 -> timeline + page environment snapshot
 *   POST /eval    {expr}         -> Runtime.evaluate, returns JSON value
 *   POST /click   {selector,index}
 *   POST /shot    {name}         -> Page.captureScreenshot -> evidence PNG
 *   POST /dpr     {dpr,width,height} -> Emulation.setDeviceMetricsOverride
 *   POST /dpr-off                -> Emulation.clearDeviceMetricsOverride
 *   POST /quit
 */

import { writeFileSync, mkdirSync } from "node:fs";
import http from "node:http";
import path from "node:path";

import { sleep } from "./cdp.mjs";
import { CDP_PORT_BASE, evidenceFor, ensureDir } from "./env.mjs";
import { launchApp, cleanupTaskProcesses, writeEvidenceJson } from "./launch.mjs";

const LABEL = process.argv[2] || "session";
const HTTP_PORT = Number(process.argv[3] || 9362);
const CDP_PORT = Number(process.argv[4] || 9361);
const EVIDENCE = evidenceFor("session", LABEL);

ensureDir(EVIDENCE);
const shotsDir = ensureDir(path.join(EVIDENCE, "shots"));

const app = await launchApp({ label: `session-${LABEL}`, cdpPort: CDP_PORT, evidenceDir: EVIDENCE, attach: true });
if (!app.cdp) {
  console.error("CDP unavailable:", app.timeline.cdpUnavailable);
  await app.teardown();
  process.exit(1);
}
const cdp = app.cdp;

const state = { label: LABEL, startedAt: new Date().toISOString(), cdpPort: CDP_PORT, ops: [] };

async function pageSnapshot() {
  return cdp.eval(`(() => ({
    url: location.href,
    title: document.title,
    readyState: document.readyState,
    dpr: window.devicePixelRatio,
    innerWidth: window.innerWidth, innerHeight: window.innerHeight,
    screenW: window.screen.width, screenH: window.screen.height,
    outerW: window.outerWidth, outerH: window.outerHeight,
    page: document.querySelector('[data-testid="page-shelf"]') ? 'shelf'
        : document.querySelector('[data-testid="page-reader"]') ? 'reader'
        : document.querySelector('[data-testid="page-workbench"]') ? 'workbench'
        : document.querySelector('[data-testid="page-settings"]') ? 'settings' : 'unknown',
    bookCards: document.querySelectorAll('[data-testid^="book-"]').length,
    layout: document.querySelector('[data-testid="reader-layout"]')?.textContent ?? null,
    pager: document.querySelector('[data-testid="reader-pager"]')?.textContent ?? null,
    imgSrc: document.querySelector('[data-testid="reader-page-image"]')?.getAttribute('src')?.slice(0, 40) ?? null,
    fpsPanel: !!document.querySelector('[data-testid="fps-recorder-panel"]'),
  }))()`);
}

const server = http.createServer(async (req, res) => {
  const send = (code, obj) => {
    res.writeHead(code, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify(obj, null, 2));
  };
  let body = "";
  req.on("data", (chunk) => { body += chunk; });
  req.on("end", async () => {
    let payload = {};
    try { payload = body ? JSON.parse(body) : {}; } catch {}
    const url = new URL(req.url, "http://127.0.0.1");
    const route = url.pathname;
    try {
      if (route === "/status") {
        return send(200, { state, page: await pageSnapshot(), timeline: app.timeline, env: app.env });
      }
      if (route === "/eval") {
        const value = await cdp.eval(payload.expr, { awaitPromise: payload.awaitPromise !== false });
        state.ops.push({ op: "eval", at: Date.now(), expr: payload.expr.slice(0, 120) });
        return send(200, { ok: true, value });
      }
      if (route === "/click") {
        const rect = await cdp.eval(
          `(() => {
             const nodes = Array.from(document.querySelectorAll(${JSON.stringify(payload.selector)}));
             const el = nodes[${Number(payload.index || 0)}];
             if (!el) return null;
             el.scrollIntoView({ block: 'center' });
             const r = el.getBoundingClientRect();
             return { x: r.x + r.width / 2, y: r.y + r.height / 2, w: r.width, h: r.height, text: (el.textContent || '').slice(0, 40) };
           })()`,
          { awaitPromise: false },
        );
        if (!rect) return send(404, { ok: false, error: "selector not found", selector: payload.selector });
        await sleep(60);
        const live = await cdp.eval(
          `(() => { const el = Array.from(document.querySelectorAll(${JSON.stringify(payload.selector)}))[${Number(payload.index || 0)}]; if(!el) return null; const r = el.getBoundingClientRect(); return { x: r.x + r.width/2, y: r.y + r.height/2 }; })()`,
          { awaitPromise: false },
        );
        const pt = live || rect;
        for (const type of ["mouseMoved", "mousePressed", "mouseReleased"]) {
          await cdp.send("Input.dispatchMouseEvent", { type, x: pt.x, y: pt.y, button: "left", clickCount: 1 });
        }
        state.ops.push({ op: "click", at: Date.now(), selector: payload.selector });
        return send(200, { ok: true, clicked: rect });
      }
      if (route === "/shot") {
        const b64 = await cdp.screenshotBase64();
        const name = String(payload.name || `shot-${Date.now()}`).replace(/[^\w.-]/g, "_");
        const file = path.join(shotsDir, name.endsWith(".png") ? name : `${name}.png`);
        writeFileSync(file, Buffer.from(b64, "base64"));
        state.ops.push({ op: "shot", at: Date.now(), file });
        return send(200, { ok: true, file });
      }
      if (route === "/dpr") {
        await cdp.send("Emulation.setDeviceMetricsOverride", {
          width: Number(payload.width),
          height: Number(payload.height),
          deviceScaleFactor: Number(payload.dpr),
          mobile: false,
        });
        await sleep(300);
        return send(200, { ok: true, page: await pageSnapshot() });
      }
      if (route === "/dpr-off") {
        await cdp.send("Emulation.clearDeviceMetricsOverride");
        await sleep(200);
        return send(200, { ok: true, page: await pageSnapshot() });
      }
      if (route === "/quit") {
        send(200, { ok: true, quitting: true });
        setTimeout(async () => {
          writeEvidenceJson(path.join(EVIDENCE, "session.json"), { state, timeline: app.timeline, logs: app.logs });
          await app.teardown();
          await sleep(500);
          const killed = await cleanupTaskProcesses({ appPid: app.timeline.childPid, sinceEpochMs: app.timeline.t0EpochMs });
          writeEvidenceJson(path.join(EVIDENCE, "session-teardown.json"), { exitInfo: app.exitInfo, killed });
          process.exit(0);
        }, 150);
        return;
      }
      return send(404, { ok: false, error: "unknown route" });
    } catch (error) {
      return send(500, { ok: false, error: String(error?.message || error) });
    }
  });
});

server.listen(HTTP_PORT, "127.0.0.1", async () => {
  const page = await pageSnapshot().catch(() => null);
  console.error(`[session] control on http://127.0.0.1:${HTTP_PORT} cdp=${CDP_PORT} label=${LABEL}`);
  console.error(`[session] page: ${JSON.stringify(page)}`);
  writeEvidenceJson(path.join(EVIDENCE, "session-start.json"), {
    label: LABEL,
    httpPort: HTTP_PORT,
    cdpPort: CDP_PORT,
    exe: app.env.__pinnedExe,
    exeSha256: app.env.__pinnedExeSha256,
    timeline: app.timeline,
    env: app.env,
    logs: app.logs,
    pageAtAttach: page,
  });
});
