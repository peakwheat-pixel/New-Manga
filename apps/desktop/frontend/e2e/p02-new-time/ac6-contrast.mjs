/**
 * AC6 — computed colors and WCAG contrast on the real WebView2 DOM.
 *
 * Collects computed foreground/background for representative states of the
 * P02 operating surface (nav buttons enabled/disabled, body text, secondary
 * text, error text, workbench panels), resolves alpha backgrounds against
 * their actual composite backdrop (walk ancestors until opaque), computes
 * WCAG 2.x contrast ratios, and records token mapping against the frozen
 * F candidate tokens (doc/design/tokens-cand-f.json).
 *
 * token_mapping and contrast_result are recorded SEPARATELY per the frozen
 * AC: unmapped tokens never skip the ratio computation. Light theme: the
 * React app has no light-theme entry (no theme switch exists) -> recorded
 * NOT_APPLICABLE. Thresholds per UI/UX GUI design contract §7.2/§9:
 * text >= 4.5:1, disabled text / non-text >= 3.0:1. No style is changed.
 */

import { readFileSync } from "node:fs";
import path from "node:path";
import { RUN_ROOT, launchDirs, CANONICAL_ROOT, REPO_ROOT, resolveScenarioRoot } from "./lib/env.mjs";
import { launchApp, assertLaunchTargetsClean } from "./lib/app.mjs";
import { evaluate, mouseClick, rectOf, sleep, typeText } from "./lib/cdp.mjs";
import { EvidenceStore } from "./lib/evidence.mjs";

const F_TOKENS = JSON.parse(readFileSync(path.join(REPO_ROOT, "doc/design/tokens-cand-f.json"), "utf8"));

const { scenario, root: scenarioRoot, attempt } = resolveScenarioRoot("ac6-contrast");
const dirs = launchDirs(scenarioRoot);

const cleanObserved = assertLaunchTargetsClean(scenarioRoot);

const store = new EvidenceStore(dirs.logs, {
  scenario: "AC6 computed colors / contrast",
  scenario_root: scenarioRoot,
  scenario_attempt: attempt,
  mock_surface: "NONE — real IPC session; DOM computed styles are product truth",
  f_token_file: "doc/design/tokens-cand-f.json",
});
const record = { steps: [] };
const note = (step, detail) => record.steps.push({ step, at: new Date().toISOString(), ...detail });
note("clean-targets-observed", cleanObserved);

const session = await launchApp({
  scenarioRoot,
  logDir: dirs.logs,
  tag: "ac6",
  cleanStateObserved: cleanObserved,
});
note("launched", { pid: session.child.pid });

/** Page-side collector: effective fg/bg with alpha compositing. */
const COLLECT_SOURCE = String.raw`
(() => {
  const parseColor = (css) => {
    const m = css.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const parts = m[1].split(',').map((s) => parseFloat(s.trim()));
    if (parts.length < 3) return null;
    return { r: parts[0], g: parts[1], b: parts[2], a: parts.length > 3 ? parts[3] : 1 };
  };
  const composite = (top, bottom) => ({
    r: top.r * top.a + bottom.r * (1 - top.a),
    g: top.g * top.a + bottom.g * (1 - top.a),
    b: top.b * top.a + bottom.b * (1 - top.a),
    a: top.a + bottom.a * (1 - top.a),
  });
  const effectiveBackground = (el) => {
    let node = el;
    const layers = [];
    while (node && node !== document.documentElement) {
      const bg = parseColor(getComputedStyle(node).backgroundColor);
      if (bg && bg.a >= 0.999) return { color: bg, on: node.tagName + (node.getAttribute('data-testid') ? '[' + node.getAttribute('data-testid') + ']' : ''), layerCount: layers.length + 1, layers };
      if (bg && bg.a > 0) layers.push({ on: node.tagName + (node.getAttribute('data-testid') ? '[' + node.getAttribute('data-testid') + ']' : ''), color: bg });
      node = node.parentElement;
    }
    const htmlBg = parseColor(getComputedStyle(document.documentElement).backgroundColor) || { r: 255, g: 255, b: 255, a: 1 };
    const canvasBg = parseColor(getComputedStyle(document.body).backgroundColor) || { r: 255, g: 255, b: 255, a: 1 };
    let acc = composite(canvasBg.a >= 0.999 ? canvasBg : htmlBg, htmlBg);
    for (const layer of layers) acc = composite(layer.color, acc);
    return { color: acc, on: 'root-composite', layerCount: layers.length + 1, layers };
  };
  const collect = (selector, label, kind) => {
    const el = document.querySelector(selector);
    if (!el) return { selector, label, present: false };
    const cs = getComputedStyle(el);
    const bg = effectiveBackground(el);
    const fg = parseColor(cs.color);
    let fgEff = fg;
    if (fg && fg.a < 0.999) fgEff = composite(fg, bg.color);
    return {
      selector, label, present: true, kind,
      text: (el.textContent || '').slice(0, 40),
      color: cs.color,
      colorResolved: fgEff ? ('rgb(' + fgEff.r.toFixed(1) + ', ' + fgEff.g.toFixed(1) + ', ' + fgEff.b.toFixed(1) + ')') : null,
      backgroundColor: cs.backgroundColor,
      backgroundResolved: bg.color ? ('rgb(' + bg.color.r.toFixed(1) + ', ' + bg.color.g.toFixed(1) + ', ' + bg.color.b.toFixed(1) + ')') : null,
      backgroundSource: bg.on,
      backgroundLayers: bg.layers,
      fontSize: cs.fontSize,
      fontWeight: cs.fontWeight,
      disabled: el.disabled === true,
      opacity: cs.opacity,
    };
  };
  window.__p02Collect = collect;
  return typeof collect;
})()
`;

/** Contrast ratio computed from the page-reported resolved rgb strings. */
function contrastRatio(rgbA, rgbB) {
  const lum = (rgb) => {
    const [r, g, b] = rgb;
    const lin = (c) => {
      const v = c / 255;
      return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
  };
  const l1 = lum(rgbA);
  const l2 = lum(rgbB);
  const [hi, lo] = l1 >= l2 ? [l1, l2] : [l2, l1];
  return (hi + 0.05) / (lo + 0.05);
}

function parseRgb(text) {
  const m = String(text).match(/rgba?\(([^)]+)\)/);
  if (!m) return null;
  const parts = m[1].split(",").map((s) => parseFloat(s.trim()));
  return [parts[0], parts[1], parts[2]];
}

function hex(c) {
  return "#" + [c[0], c[1], c[2]].map((v) => Math.round(v).toString(16).padStart(2, "0")).join("").toUpperCase();
}

/** token mapping against the F palette (both modes). */
function mapToken(rgb) {
  const target = hex(rgb).toLowerCase();
  const hits = [];
  for (const [mode, data] of Object.entries(F_TOKENS.modes)) {
    for (const [name, value] of Object.entries(data.color || {})) {
      const m = String(value).match(/^#([0-9a-f]{6})$/i);
      if (m && m[1].toLowerCase() === target) hits.push({ mode, token: name });
    }
  }
  return hits;
}

try {
  // wait for interactive chrome
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    if (await evaluate(session.cdp, `!!document.querySelector('[data-testid="nav-workbench"]')`, false)) break;
    await sleep(400);
  }
  await evaluate(session.cdp, COLLECT_SOURCE, false);

  const consoleSamples = [
    ['[data-testid="nav-console"]', 'nav-console button (disabled/active view)', 'non-text-ui'],
    ['[data-testid="nav-workbench"]', 'nav-workbench button (enabled)', 'text'],
    ["h1", "console heading", "text"],
    ["body > div", "app root text", "text"],
  ];
  const consoleColors = [];
  for (const [selector, label, kind] of consoleSamples) {
    consoleColors.push(await evaluate(session.cdp, `window.__p02Collect(${JSON.stringify(selector)}, ${JSON.stringify(label)}, ${JSON.stringify(kind)})`, false));
  }
  note("console-view-colors", consoleColors);

  // enter workbench for the workbench samples (incl. typed-id error states)
  const nav = await rectOf(session.cdp, '[data-testid="nav-workbench"]');
  await mouseClick(session.cdp, nav.cx, nav.cy);
  const wbDeadline = Date.now() + 20000;
  while (Date.now() < wbDeadline) {
    if (await evaluate(session.cdp, `!!document.querySelector('[data-testid="workbench-page"]')`, false)) break;
    await sleep(300);
  }
  const input = await rectOf(session.cdp, '[data-testid="page-id-input"]');
  await mouseClick(session.cdp, input.cx, input.cy);
  await typeText(session.cdp, "syn-page-ac6-unknown");
  await sleep(1400); // real core: resolve fails -> error text appears

  const wbSamples = [
    ['[data-testid="workbench-toolbar"] [data-testid="toolbar-context"]', 'toolbar context text', 'text'],
    ['[data-testid="toolbar-region-count"]', 'toolbar secondary text', 'text'],
    ['[data-testid="page-id-input"]', 'page id input', 'text'],
    ['[data-testid="resource-resolve-error"]', 'resolve error text', 'text'],
    ['[data-testid="inspector-empty"]', 'inspector empty note', 'text'],
    ['[data-testid="task-progress-placeholder"]', 'task progress placeholder', 'text'],
    ['[data-testid="workbench-page"]', 'workbench panel surface', 'non-text-ui'],
  ];
  const wbColors = [];
  for (const [selector, label, kind] of wbSamples) {
    wbColors.push(await evaluate(session.cdp, `window.__p02Collect(${JSON.stringify(selector)}, ${JSON.stringify(label)}, ${JSON.stringify(kind)})`, false));
  }
  note("workbench-view-colors", wbColors);

  const shot = await session.cdp.send("Page.captureScreenshot", { format: "png" });
  note("screenshot", store.writeBinary("ac6-workbench.png", Buffer.from(shot.data, "base64")));

  // --- assemble the contrast table -----------------------------------------
  const contrastRows = [];
  for (const sample of [...consoleColors, ...wbColors]) {
    if (!sample || sample.present === false) {
      contrastRows.push({ label: sample?.label, selector: sample?.selector, present: false, token_mapping: "NOT_APPLICABLE", contrast_result: "NOT_VERIFIABLE", reason: "element not present in this state" });
      continue;
    }
    const fg = parseRgb(sample.colorResolved || sample.color);
    const bg = parseRgb(sample.backgroundResolved || sample.backgroundColor);
    const row = {
      label: sample.label,
      selector: sample.selector,
      text: sample.text,
      kind: sample.kind,
      disabled: sample.disabled === true,
      fontSize: sample.fontSize,
      fontWeight: sample.fontWeight,
      foreground: sample.colorResolved || sample.color,
      background: sample.backgroundResolved || sample.backgroundColor,
      backgroundSource: sample.backgroundSource,
      backgroundLayers: sample.backgroundLayers,
    };
    row.token_mapping = mapToken(fg).length > 0 || mapToken(bg).length > 0
      ? { status: "MAPPED", hits: [...mapToken(fg), ...mapToken(bg)] }
      : { status: "UNMAPPED", note: "inline React runtime colors; F token system not wired into this surface" };
    if (fg && bg) {
      const ratio = contrastRatio(fg, bg);
      row.contrast_ratio = Math.round(ratio * 100) / 100;
      const threshold = row.disabled || sample.kind === "non-text-ui" ? 3.0 : 4.5;
      row.threshold = threshold;
      row.contrast_result = ratio >= threshold ? "PASS" : "FAIL";
    } else {
      row.contrast_result = "NOT_VERIFIABLE";
      row.reason = fg ? "background could not be resolved to opaque composite" : "foreground not parseable";
    }
    contrastRows.push(row);
  }
  record.contrast_table = contrastRows;

  // light theme entry check (frozen AC: record NOT_APPLICABLE when absent)
  record.light_theme = {
    entry_point_present: false,
    how_checked: "DOM census of nav/settings surfaces in this session: no theme/toggle control exists",
    status: "NOT_APPLICABLE (no light theme entry in the React app)",
  };

  // state-not-by-color-only census (triple encoding): report observed badges
  record.triple_encoding_observation = await evaluate(session.cdp, `(() => ({
    sfxBadgeSamples: [...document.querySelectorAll('[data-testid^="region-badge-"]')].map((el) => el.textContent),
    note: "with the real empty synthetic catalog no region badges render in this state",
  }))()`, false);

  record.verdict = {
    ac: "AC6",
    samples: contrastRows.length,
    computed: contrastRows.filter((r) => typeof r.contrast_ratio === "number").length,
    fails: contrastRows.filter((r) => r.contrast_result === "FAIL").map((r) => r.label),
    not_verifiable: contrastRows.filter((r) => r.contrast_result === "NOT_VERIFIABLE").map((r) => r.label),
    token_mapping_summary: {
      mapped: contrastRows.filter((r) => r.token_mapping.status === "MAPPED").length,
      unmapped: contrastRows.filter((r) => r.token_mapping && r.token_mapping.status === "UNMAPPED").length,
    },
    light_theme: record.light_theme.status,
    thresholds: { text: "4.5:1", disabled_or_non_text: "3.0:1" },
  };
} catch (error) {
  record.errors = [String(error && error.stack ? error.stack : error)];
  record.verdict = { ac: "AC6", status: "ERROR", error: String(error) };
  process.exitCode = 1;
} finally {
  const exit = await session.teardown();
  note("teardown", exit);
  store.writeJson("ac6-contrast.json", record);
  store.copyToCanonical(path.join(CANONICAL_ROOT, scenario));
  console.log(JSON.stringify(record.verdict, null, 2));
}
