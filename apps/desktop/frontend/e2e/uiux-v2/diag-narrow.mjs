/**
 * UIUX-V2-RUNTIME-NARROW-1 — pre/post-fix width diagnostic.
 *
 * For each viewport (900x700 DPR2, 1280x800 DPR2) x each of the four primary
 * pages, measure the REAL packaged app:
 *   - documentElement.scrollWidth vs clientWidth (the defect signal)
 *   - .nm-app box + computed min-width (the suspected root cause)
 *   - titlebar 3-track rects (brand / tabs / actions)
 *   - shelf library/grid/detail rects + the library's own scroll range
 *   - every element whose bounding rect sticks out of the viewport
 *
 * Run against the acceptance build:
 *   UIUX_E2E_EXE=<...>/target/release/new-manga.exe node e2e/uiux-v2/diag-narrow.mjs
 * Output: task-env run dir `narrow-diag.json` + one screenshot per page x viewport.
 */

import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";

import { launchApp } from "./lib/app.mjs";
import { evaluate, sleep } from "../p02-new-time/lib/cdp.mjs";
import { launchDirs, resolveRunName, runRootFor } from "./lib/env.mjs";

const RUN_ROOT = runRootFor(resolveRunName());

const VIEWPORTS = [
  { name: "900x700-dpr2", width: 900, height: 700, dpr: 2 },
  { name: "1280x800-dpr2", width: 1280, height: 800, dpr: 2 },
];

const PAGES = [
  { key: "shelf", tab: "tab-shelf", page: "page-shelf" },
  { key: "workbench", tab: "tab-workbench", page: "page-workbench" },
  { key: "reader", tab: "tab-reader", page: "page-reader" },
  { key: "settings", tab: "tab-settings", page: "page-settings" },
];

async function realClick(cdp, x, y) {
  await cdp.send("Input.dispatchMouseEvent", { type: "mouseMoved", x, y, button: "none", buttons: 0 });
  await cdp.send("Input.dispatchMouseEvent", {
    type: "mousePressed",
    x,
    y,
    button: "left",
    buttons: 1,
    clickCount: 1,
  });
  await sleep(30);
  await cdp.send("Input.dispatchMouseEvent", {
    type: "mouseReleased",
    x,
    y,
    button: "left",
    buttons: 0,
    clickCount: 1,
  });
  await sleep(160);
}

async function clickTab(cdp, tabTestId) {
  const rect = await evaluate(
    cdp,
    `(() => { const el = document.querySelector('[data-testid="${tabTestId}"]'); if (!el) return null; const r = el.getBoundingClientRect(); return { cx: r.x + r.width / 2, cy: r.y + r.height / 2, w: r.width, h: r.height }; })()`,
  );
  if (!rect || !rect.w || !rect.h) throw new Error(`tab not visible: ${tabTestId}`);
  await realClick(cdp, rect.cx, rect.cy);
}

const MEASURE = `(() => {
  const vw = innerWidth;
  const round = (n) => Math.round(n * 10) / 10;
  const rect = (el) => { if (!el) return null; const r = el.getBoundingClientRect(); return { left: round(r.left), right: round(r.right), top: round(r.top), bottom: round(r.bottom), width: round(r.width), height: round(r.height) }; };
  const app = document.querySelector('.nm-app');
  const appStyle = app ? getComputedStyle(app) : null;
  const titlebar = document.querySelector('.nm-titlebar');
  const offenders = [];
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    if (r.right > vw + 0.5 || r.left < -0.5) {
      offenders.push({
        tag: el.tagName.toLowerCase(),
        cls: String(el.className || '').slice(0, 120),
        testid: el.getAttribute('data-testid'),
        rect: { left: round(r.left), right: round(r.right), width: round(r.width) },
        minWidth: getComputedStyle(el).minWidth,
      });
      if (offenders.length >= 25) break;
    }
  }
  const library = document.querySelector('.nm-shelf__library');
  const grid = document.querySelector('.nm-book-grid');
  const detail = document.querySelector('.nm-detail');
  return {
    view: { width: vw, height: innerHeight, dpr: devicePixelRatio },
    doc: { scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth, bodyScrollWidth: document.body.scrollWidth },
    app: app ? { rect: rect(app), minWidth: appStyle.minWidth, minHeight: appStyle.minHeight, overflowX: appStyle.overflowX } : null,
    titlebar: titlebar ? {
      grid: getComputedStyle(titlebar).gridTemplateColumns,
      brand: rect(titlebar.querySelector('.nm-titlebar__brand')),
      tabs: rect(titlebar.querySelector('.nm-tabs')),
      actions: rect(titlebar.querySelector('.nm-titlebar__actions')),
    } : null,
    shelf: document.querySelector('[data-testid="page-shelf"]') ? {
      library: rect(library),
      libraryScroll: library ? { scrollWidth: library.scrollWidth, clientWidth: library.clientWidth } : null,
      grid: rect(grid),
      gridColumns: grid ? getComputedStyle(grid).gridTemplateColumns : null,
      detail: rect(detail),
    } : null,
    offenders,
  };
})()`;

async function shot(cdp, name) {
  const dirs = launchDirs(RUN_ROOT);
  mkdirSync(dirs.shots, { recursive: true });
  const file = path.join(dirs.shots, `${name}.png`);
  const { data } = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  writeFileSync(file, Buffer.from(data, "base64"));
  return file;
}

const report = { startedAt: new Date().toISOString(), viewports: [] };

const app = await launchApp({ scenarioRoot: RUN_ROOT, tag: "narrow-diag" });
try {
  const { cdp } = app;
  const deadline = Date.now() + 45000;
  while (Date.now() < deadline) {
    if (await evaluate(cdp, `document.querySelector('[data-testid="app-root"]') !== null`)) break;
    await sleep(250);
  }

  const { windowId, bounds: oldBounds } = await cdp.send("Browser.getWindowForTarget");
  try {
    for (const vp of VIEWPORTS) {
      await cdp.send("Browser.setWindowBounds", { windowId, bounds: { width: vp.width, height: vp.height, windowState: "normal" } });
      await cdp.send("Emulation.setDeviceMetricsOverride", {
        width: vp.width,
        height: vp.height,
        deviceScaleFactor: vp.dpr,
        mobile: false,
        screenWidth: vp.width,
        screenHeight: vp.height,
      });
      await sleep(450);
      const vpReport = { viewport: vp, pages: [] };
      for (const page of PAGES) {
        await clickTab(cdp, page.tab);
        const deadline2 = Date.now() + 15000;
        while (Date.now() < deadline2) {
          if (await evaluate(cdp, `document.querySelector('[data-testid="${page.page}"]') !== null`)) break;
          await sleep(150);
        }
        await sleep(350);
        const measured = await evaluate(cdp, MEASURE);
        const shotPath = await shot(cdp, `diag-${vp.name}-${page.key}`);
        vpReport.pages.push({ page: page.key, ...measured, shot: path.basename(shotPath) });
        console.log(
          `[${vp.name}] ${page.key.padEnd(10)} doc=${measured.doc.scrollWidth}/${measured.doc.clientWidth}` +
            ` app=${measured.app ? measured.app.rect.width + ' min:' + measured.app.minWidth : 'n/a'}` +
            ` offenders=${measured.offenders.length}`,
        );
      }
      report.viewports.push(vpReport);
    }
  } finally {
    await cdp.send("Emulation.clearDeviceMetricsOverride").catch(() => {});
    if (oldBounds) await cdp.send("Browser.setWindowBounds", { windowId, bounds: oldBounds }).catch(() => {});
  }
} finally {
  await app.teardown();
}

report.finishedAt = new Date().toISOString();
const outFile = path.join(RUN_ROOT, "narrow-diag.json");
writeFileSync(outFile, JSON.stringify(report, null, 2));
console.log(`\nreport: ${outFile}`);
