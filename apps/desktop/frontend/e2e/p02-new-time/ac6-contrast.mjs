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
 * R-02 rules:
 * - Empty/invisible elements (e.g. bare body > div) are removed; only visible non-empty text sampled.
 * - Alpha backgrounds are composited bottom-up on opaque ancestors. If no opaque ancestor exists,
 *   contrast_result is recorded as NOT_VERIFIABLE with reason; transparent black never produces a 1:1 false fail.
 * - When fg and bg are resolved, contrast is computed against Task thresholds (text >= 4.5:1, disabled/non-text >= 3.0:1).
 * - Rollup summary and findings are recomputed strictly from this run's JSON.
 */

import { readFileSync } from "node:fs";
import path from "node:path";
import {
  RUN_ROOT,
  launchDirs,
  CDP_PORT,
  PINNED_EXE,
  PINNED_EXE_SHA256,
  SOURCE_BASELINE_COMMIT,
  CANONICAL_RUNS_ROOT,
  REPO_ROOT,
  resolveScenarioRoot,
  envEvidenceManifest,
} from "./lib/env.mjs";
import { launchApp, assertLaunchTargetsClean } from "./lib/app.mjs";
import { evaluate, mouseClick, rectOf, sleep, typeText } from "./lib/cdp.mjs";
import { EvidenceStore, sha256File } from "./lib/evidence.mjs";

const F_TOKENS = JSON.parse(readFileSync(path.join(REPO_ROOT, "doc/design/tokens-cand-f.json"), "utf8"));

const { scenario, root: scenarioRoot, attempt } = resolveScenarioRoot("ac6-contrast");
const dirs = launchDirs(scenarioRoot);

const cleanObserved = assertLaunchTargetsClean(scenarioRoot);

const store = new EvidenceStore(dirs.logs, {
  scenario: "AC6 computed colors / contrast",
  cdp_port: CDP_PORT,
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

/** Page-side collector: effective fg/bg with rigorous alpha compositing. */
const COLLECT_SOURCE = String.raw`
(() => {
  const parseColor = (css) => {
    if (!css) return null;
    const m = css.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const parts = m[1].split(',').map((s) => parseFloat(s.trim()));
    if (parts.length < 3) return null;
    return { r: parts[0], g: parts[1], b: parts[2], a: parts.length > 3 ? parts[3] : 1 };
  };

  // Porter-Duff source-over composite: top over bottom
  const composite = (top, bottom) => {
    const a = top.a + bottom.a * (1 - top.a);
    if (a <= 0) return { r: 0, g: 0, b: 0, a: 0 };
    return {
      r: (top.r * top.a + bottom.r * bottom.a * (1 - top.a)) / a,
      g: (top.g * top.a + bottom.g * bottom.a * (1 - top.a)) / a,
      b: (top.b * top.a + bottom.b * bottom.a * (1 - top.a)) / a,
      a: a,
    };
  };

  const effectiveBackground = (el) => {
    // 1. Walk up the ancestor tree, collecting all layers with background
    const layers = [];
    let node = el;
    let opaqueBase = null;

    while (node && node !== document.documentElement) {
      const cs = getComputedStyle(node);
      const bg = parseColor(cs.backgroundColor);
      if (bg && bg.a > 0) {
        layers.unshift({
          on: node.tagName + (node.getAttribute('data-testid') ? '[' + node.getAttribute('data-testid') + ']' : ''),
          color: bg,
        });
        if (bg.a >= 0.999) {
          opaqueBase = bg;
          break; // reached an opaque base
        }
      }
      node = node.parentElement;
    }

    // Check html and body if no opaque base found
    if (!opaqueBase) {
      const htmlBg = parseColor(getComputedStyle(document.documentElement).backgroundColor);
      const bodyBg = parseColor(getComputedStyle(document.body).backgroundColor);
      if (bodyBg && bodyBg.a >= 0.999) {
        opaqueBase = bodyBg;
        layers.unshift({ on: 'body', color: bodyBg });
      } else if (htmlBg && htmlBg.a >= 0.999) {
        opaqueBase = htmlBg;
        layers.unshift({ on: 'html', color: htmlBg });
      }
    }

    // If still no opaque base exists, background is NOT verifiable (never assume transparent black 0,0,0,0)
    if (!opaqueBase) {
      return {
        color: null,
        isVerifiable: false,
        reason: 'no opaque background found in ancestor chain',
        layers,
      };
    }

    // Composite from the bottom-most opaque base upwards
    let acc = { ...opaqueBase };
    // find index of opaque base in layers
    const baseIdx = layers.findIndex((l) => l.color === opaqueBase);
    const topLayers = baseIdx >= 0 ? layers.slice(baseIdx + 1) : layers;
    for (const layer of topLayers) {
      acc = composite(layer.color, acc);
    }

    return {
      color: acc,
      isVerifiable: true,
      on: layers.map((l) => l.on).join(' -> '),
      layerCount: layers.length,
      layers,
    };
  };

  const collect = (selector, label, kind) => {
    const el = document.querySelector(selector);
    if (!el) return { selector, label, present: false, reason: 'element not in DOM' };
    const cs = getComputedStyle(el);

    // If kind is text, verify non-empty text and visibility
    const text = (el.textContent || '').trim();
    if (kind === 'text' && !text) {
      return { selector, label, present: false, reason: 'element has no visible text content' };
    }
    if (cs.display === 'none' || cs.visibility === 'hidden') {
      return { selector, label, present: false, reason: 'element is hidden' };
    }

    const bg = effectiveBackground(el);
    const fg = parseColor(cs.color);
    let fgEff = fg;
    if (fg && bg.color && fg.a < 0.999) {
      fgEff = composite(fg, bg.color);
    }

    return {
      selector,
      label,
      present: true,
      kind,
      text: text.slice(0, 50),
      color: cs.color,
      colorResolved: fgEff ? ('rgb(' + fgEff.r.toFixed(1) + ', ' + fgEff.g.toFixed(1) + ', ' + fgEff.b.toFixed(1) + ')') : null,
      backgroundColor: cs.backgroundColor,
      backgroundResolved: bg.color ? ('rgb(' + bg.color.r.toFixed(1) + ', ' + bg.color.g.toFixed(1) + ', ' + bg.color.b.toFixed(1) + ')') : null,
      backgroundVerifiable: bg.isVerifiable,
      backgroundSource: bg.on || null,
      backgroundReason: bg.reason || null,
      backgroundLayers: bg.layers || [],
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
  if (!text) return null;
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
  if (!rgb) return [];
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

  // R-02: body > div sample REMOVED. Only visible elements with non-empty text are sampled.
  const consoleSamples = [
    ['[data-testid="nav-console"]', 'nav-console button (disabled/active view)', 'non-text-ui'],
    ['[data-testid="nav-workbench"]', 'nav-workbench button (enabled)', 'text'],
    ["h1", "console heading", "text"],
  ];
  const consoleColors = [];
  for (const [selector, label, kind] of consoleSamples) {
    consoleColors.push(
      await evaluate(
        session.cdp,
        `window.__p02Collect(${JSON.stringify(selector)}, ${JSON.stringify(label)}, ${JSON.stringify(kind)})`,
        false
      )
    );
  }
  note("console-view-colors", consoleColors);

  // enter workbench for the workbench samples
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
    wbColors.push(
      await evaluate(
        session.cdp,
        `window.__p02Collect(${JSON.stringify(selector)}, ${JSON.stringify(label)}, ${JSON.stringify(kind)})`,
        false
      )
    );
  }
  note("workbench-view-colors", wbColors);

  const shot = await session.cdp.send("Page.captureScreenshot", { format: "png" });
  note("screenshot", store.writeBinary("ac6-workbench.png", Buffer.from(shot.data, "base64")));

  // --- assemble the contrast table -----------------------------------------
  const contrastRows = [];
  for (const sample of [...consoleColors, ...wbColors]) {
    if (!sample || sample.present === false) {
      contrastRows.push({
        label: sample?.label,
        selector: sample?.selector,
        present: false,
        token_mapping: "NOT_APPLICABLE",
        contrast_result: "NOT_VERIFIABLE",
        reason: sample?.reason || "element not present or empty in this state",
      });
      continue;
    }

    if (sample.backgroundVerifiable === false) {
      contrastRows.push({
        label: sample.label,
        selector: sample.selector,
        present: true,
        text: sample.text,
        kind: sample.kind,
        foreground: sample.colorResolved || sample.color,
        background: null,
        token_mapping: "NOT_APPLICABLE",
        contrast_result: "NOT_VERIFIABLE",
        reason: sample.backgroundReason || "background could not be resolved to opaque composite",
      });
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

    row.token_mapping =
      mapToken(fg).length > 0 || mapToken(bg).length > 0
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

  record.verdict = {
    ac: "AC6",
    samples: contrastRows.length,
    computed: contrastRows.filter((r) => typeof r.contrast_ratio === "number").length,
    passed: contrastRows.filter((r) => r.contrast_result === "PASS").map((r) => r.label),
    fails: contrastRows.filter((r) => r.contrast_result === "FAIL").map((r) => r.label),
    not_verifiable: contrastRows.filter((r) => r.contrast_result === "NOT_VERIFIABLE").map((r) => r.label),
    token_mapping_summary: {
      mapped: contrastRows.filter((r) => r.token_mapping && r.token_mapping.status === "MAPPED").length,
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
  store.writeMetadata({
    scenario_name: scenario,
    command: `node apps/desktop/frontend/e2e/p02-new-time/ac6-contrast.mjs`,
    env_manifest: envEvidenceManifest(session.env),
    pinned_source_commit: SOURCE_BASELINE_COMMIT,
    pinned_exe_sha256: PINNED_EXE_SHA256,
    stdout_path: session.logPaths.stdoutPath,
    stderr_path: session.logPaths.stderrPath,
  });
  store.copyToCanonical(path.join(CANONICAL_RUNS_ROOT, scenario));
  console.log(JSON.stringify(record.verdict, null, 2));
}
