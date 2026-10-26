/**
 * UIUX-V2-RUNTIME-REALCORE-1 — scripted end-to-end acceptance against the REAL
 * packaged Tauri app + REAL Python Core sidecar.
 *
 * Why this exists (and why the previous approach was wrong):
 *   Driving the desktop by "screenshot -> recognise -> click coordinates" is a
 *   last resort: WebView2 drops PostMessage input, the desktop driver cannot
 *   expose stable element handles for WebView content, and every assertion has
 *   to be made by a human looking at a PNG. WebView2 officially supports a CDP
 *   endpoint (WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port),
 *   so the same acceptance can be a reproducible script:
 *     - DOM assertions            -> Runtime.evaluate
 *     - real mouse / keyboard     -> Input.dispatchMouseEvent / dispatchKeyEvent
 *     - screenshots for the human -> Page.captureScreenshot (no recognition)
 *
 * The harness core (CDP client, isolated launch env) is reused unchanged from
 * e2e/p02-new-time/lib — this Task only adds its own env pinning and scenarios.
 *
 * Usage:  node e2e/uiux-v2/run.mjs
 * Exit:   0 only when every scenario check passed.
 */

import { cpSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import path from "node:path";

import { launchApp } from "./lib/app.mjs";
import {
  evaluate,
  pressKey,
  sleep,
} from "../p02-new-time/lib/cdp.mjs";
import {
  CDP_PORT,
  PINNED_EXE,
  canonicalFor,
  envEvidenceManifest,
  launchDirs,
  resolveRunName,
  runRootFor,
} from "./lib/env.mjs";

const TASK_ID = "UIUX-V2-RUNTIME-REALCORE-1";
/** Never overwrite a previous run: a fresh run-iN slot is allocated up front. */
const RUN_NAME = resolveRunName();
const RUN_ROOT = runRootFor(RUN_NAME);
const CANONICAL_RUN_DIR = canonicalFor(RUN_NAME);
const RUN_ID = `uiux-v2-realcore-20261026-${RUN_NAME}`;
const startedAt = new Date().toISOString();
const scenarios = [];

/* ------------------------------------------------------------------ helpers */

function record(scenarioId, title, checks) {
  const ok = checks.every((c) => c.ok);
  scenarios.push({ scenarioId, title, ok, checks });
  const mark = ok ? "PASS" : "FAIL";
  console.log(`\n[${mark}] ${scenarioId} — ${title}`);
  for (const c of checks) {
    console.log(`   ${c.ok ? "ok  " : "FAIL"} ${c.name}${c.detail ? ` :: ${c.detail}` : ""}`);
  }
  return ok;
}

function check(name, ok, detail = undefined) {
  return { name, ok: Boolean(ok), detail: detail === undefined ? undefined : String(detail).slice(0, 400) };
}

async function waitFor(cdp, expression, { timeoutMs = 20000, intervalMs = 150, label } = {}) {
  const deadline = Date.now() + timeoutMs;
  let last = "never evaluated";
  while (Date.now() < deadline) {
    try {
      const value = await evaluate(cdp, expression);
      if (value) return value;
      last = JSON.stringify(value);
    } catch (error) {
      last = String(error.message || error);
    }
    await sleep(intervalMs);
  }
  throw new Error(`waitFor timeout: ${label || expression} (last=${String(last).slice(0, 200)})`);
}

/**
 * Real mouse click with the FULL event sequence (move -> press(buttons=1) ->
 * release). Chromium ignores a `mousePressed` without `buttons`, so the
 * two-event helper in the shared lib behaves like a hover for WebView2 content.
 */
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
  await sleep(140);
}

/** Ctrl+<key> through real key events (modifiers=2 is Ctrl). */
async function ctrlKey(cdp, key, code, vk) {
  const base = { modifiers: 2, key, code, windowsVirtualKeyCode: vk, nativeVirtualKeyCode: vk };
  await cdp.send("Input.dispatchKeyEvent", { type: "keyDown", ...base });
  await sleep(40);
  await cdp.send("Input.dispatchKeyEvent", { type: "keyUp", ...base });
  await sleep(160);
}

/** Real mouse click on the centre of the index-th match of `selector`. */
async function clickSelector(cdp, selector, index = 0) {
  const rect = await evaluate(
    cdp,
    `(() => {
      const els = Array.from(document.querySelectorAll(${JSON.stringify(selector)}));
      const el = els[${index}];
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { cx: r.x + r.width / 2, cy: r.y + r.height / 2, w: r.width, h: r.height, text: (el.textContent||"").slice(0,80) };
    })()`,
  );
  if (!rect || !rect.w || !rect.h) throw new Error(`click target not visible: ${selector}[${index}]`);
  await realClick(cdp, rect.cx, rect.cy);
  return rect;
}

async function insertText(cdp, text) {
  await cdp.send("Input.insertText", { text });
  await sleep(120);
}

async function shot(cdp, name) {
  const dirs = launchDirs(RUN_ROOT);
  mkdirSync(dirs.shots, { recursive: true });
  const file = path.join(dirs.shots, `${name}.png`);
  const { data } = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  writeFileSync(file, Buffer.from(data, "base64"));
  return file;
}

async function text(cdp, selector) {
  return evaluate(
    cdp,
    `(() => { const el = document.querySelector(${JSON.stringify(selector)}); return el ? (el.textContent || "").trim() : null; })()`,
  );
}

async function count(cdp, selector) {
  return evaluate(cdp, `document.querySelectorAll(${JSON.stringify(selector)}).length`);
}


/* --------------------------------------------------------------------- main */

const report = {
  taskId: TASK_ID,
  runId: RUN_ID,
  startedAt,
  cdpPort: CDP_PORT,
  pinnedExe: PINNED_EXE,
  exeSha256: null,
  envManifest: null,
  scenarios,
  stderrAllowlistLine: null,
  ok: false,
};

let app = null;
try {
  report.exeSha256 = createHash("sha256").update(readFileSync(PINNED_EXE)).digest("hex").toUpperCase();

  app = await launchApp({ scenarioRoot: RUN_ROOT, tag: "uiux-v2" });
  const { cdp } = app;
  report.envManifest = envEvidenceManifest(app.env);

  // The page is ALREADY the real product boot (no reload): reloading a live
  // Tauri page tears down the IPC bridge mid-flight and hangs the acceptance.
  await waitFor(cdp, `document.querySelector('[data-testid="app-root"]') !== null`, {
    label: "app-root mounted",
    timeoutMs: 45000,
  });

  /* ---------------------------------------------------------- S1 identity */
  {
    const checks = [];
    const dataView = await evaluate(cdp, "document.documentElement.dataset.view");
    const dataTheme = await evaluate(cdp, "document.documentElement.dataset.theme");
    const shellCount = await count(cdp, ".app-shell, [data-testid='app-shell']");
    const tabs = await count(cdp, "[role='tab']");
    const title = await evaluate(cdp, "document.title");
    const tauriBridge = await evaluate(cdp, "typeof window.__TAURI__");

    checks.push(check("data-view=app", dataView === "app", `data-view=${dataView}`));
    checks.push(check("data-theme 已设置", dataTheme === "dark" || dataTheme === "light", `data-theme=${dataTheme}`));
    checks.push(check("旧内联壳 AppShell 不在 DOM 中", shellCount === 0, `count=${shellCount}`));
    checks.push(check("一级导航 4 个 tab", tabs === 4, `count=${tabs}`));
    checks.push(check("Tauri IPC 桥存在", tauriBridge === "object", `typeof __TAURI__=${tauriBridge}`));
    checks.push(check("文档标题非空", Boolean(title), `title=${title}`));

    const stderr = readFileSync(app.logPaths.stderrPath, "utf8");
    const allow = stderr.split(/\r?\n/).find((l) => l.includes("[m2rc2-allowlist]")) || "";
    report.stderrAllowlistLine = allow.slice(0, 2000);
    const allowCount = allow ? allow.split("production:")[1]?.split(",").length || 0 : 0;
    checks.push(check("生产 IPC allowlist 已公告", allowCount > 60, `commands=${allowCount}`));

    await shot(cdp, "01-identity-shelf-dark");
    record("S1", "身份与单一 UI（真实 packaged EXE + WebView2）", checks);
  }

  /* ------------------------------------------------------ S2 shelf 空态真实读取 */
  {
    const checks = [];
    await waitFor(cdp, `document.querySelector('[data-testid="page-shelf"]') !== null`, { label: "page-shelf" });
    await waitFor(cdp, `document.querySelector('[data-testid="shelf-empty"]') !== null || document.querySelectorAll('[data-testid^="book-"]').length > 0`, {
      label: "shelf settled (empty or books)",
    });
    const emptyShown = (await count(cdp, "[data-testid='shelf-empty']")) === 1;
    const status = await text(cdp, "[data-testid='shelf-statusbar']");
    const readBadge = await text(cdp, "[data-testid='shelf-grid']");
    const detailEmpty = await text(cdp, "[data-testid='shelf-detail']");

    checks.push(check("书架空态来自真实读取（0 部作品）", emptyShown, `shelf-empty=${emptyShown}`));
    checks.push(check("状态栏显示真实 Core 在线", /Core/i.test(status || ""), `statusbar=${(status || "").slice(0, 120)}`));
    checks.push(check("工具栏声明数据来自 Core 的最新读取", /Core/.test(readBadge || status || ""), `text=${(readBadge || "").slice(0, 80)}`));
    checks.push(check("详情面板为空态（未编造数据）", /未选择作品/.test(detailEmpty || ""), `detail=${(detailEmpty || "").slice(0, 80)}`));

    await shot(cdp, "02-shelf-empty-real-core");
    record("S2", "书架页真实数据（library_list_books + core_ping）", checks);
  }

  /* --------------------------------------------------------- S3 命令面板 */
  {
    const checks = [];
    await ctrlKey(cdp, "k", "KeyK", 75);
    await waitFor(cdp, `document.querySelector('[data-testid="command-palette"]') !== null`, {
      label: "palette open (Ctrl+K)",
    });
    checks.push(check("Ctrl+K 快捷键打开命令面板", true, "keyboard path"));
    const options = await count(cdp, "[data-testid='command-palette'] [role='option']");
    const focused = await evaluate(cdp, "document.activeElement && document.activeElement.getAttribute('data-testid')");
    const activeDesc = await evaluate(
      cdp,
      "(() => { const el = document.querySelector('[role=\"combobox\"]'); return el ? el.getAttribute('aria-activedescendant') : null; })()",
    );
    checks.push(check("Ctrl+K 触发按钮打开面板", options >= 4, `options=${options}`));
    checks.push(check("焦点落在命令输入框", focused === "command-input", `activeElement=${focused}`));
    checks.push(check("aria-activedescendant 指向可选项", Boolean(activeDesc), `aria-activedescendant=${activeDesc}`));

    // Esc closes the palette. Focus returns to whatever opened it: for the
    // keyboard path that is <body> (no opener element), which is correct.
    await pressKey(cdp, "Escape", { code: "Escape", windowsVirtualKeyCode: 27 });
    await waitFor(cdp, `document.querySelector('[data-testid="command-palette"]') === null`, { label: "palette closed" });
    checks.push(check("Esc 关闭面板（键盘路径）", true, "closed"));

    // Mouse path: click the toolbar trigger, then Esc must restore focus to it.
    await clickSelector(cdp, "[data-testid='command-trigger']");
    await waitFor(cdp, `document.querySelector('[data-testid="command-palette"]') !== null`, {
      label: "palette open (click)",
    });
    checks.push(check("真实鼠标点击触发器也能打开", true, "click path"));
    await pressKey(cdp, "Escape", { code: "Escape", windowsVirtualKeyCode: 27 });
    await waitFor(cdp, `document.querySelector('[data-testid="command-palette"]') === null`, {
      label: "palette closed (click)",
    });
    const focusAfter = await evaluate(cdp, "document.activeElement && document.activeElement.getAttribute('data-testid')");
    checks.push(check("焦点还原到唤起按钮", focusAfter === "command-trigger", `activeElement=${focusAfter}`));

    await shot(cdp, "03-command-palette-closed");
    record("S3", "命令面板（焦点圈禁 / Esc / 焦点还原）", checks);
  }

  /* --------------------------------------------------------- S4 四页导航 */
  {
    const checks = [];
    const pages = [
      { index: 1, testid: "page-workbench", label: "工作台" },
      { index: 2, testid: "page-reader", label: "阅读器" },
      { index: 3, testid: "page-settings", label: "设置" },
      { index: 0, testid: "page-shelf", label: "书架" },
    ];
    for (const page of pages) {
      await clickSelector(cdp, "[role='tab']", page.index);
      await waitFor(cdp, `document.querySelector('[data-testid="${page.testid}"]') !== null`, {
        label: page.testid,
      });
      const selected = await evaluate(
        cdp,
        `(() => { const t = document.querySelectorAll("[role='tab']")[${page.index}]; return t ? t.getAttribute('aria-selected') : null; })()`,
      );
      checks.push(check(`切到${page.label}（${page.testid}）`, selected === "true", `aria-selected=${selected}`));
    }
    const shellCount = await count(cdp, ".app-shell, [data-testid='app-shell']");
    checks.push(check("全程只有一套 UI（无 AppShell）", shellCount === 0, `app-shell=${shellCount}`));
    await shot(cdp, "04-navigation-back-to-shelf");
    record("S4", "四页导航（真实点击 + aria-selected）", checks);
  }

  /* ------------------------------------------------------ S5 设置页真实读 */
  {
    const checks = [];
    await clickSelector(cdp, "[role='tab']", 3);
    await waitFor(cdp, `document.querySelector('[data-testid="page-settings"]') !== null`, { label: "page-settings" });
    await waitFor(cdp, `document.querySelector('[data-testid="settings-section-title"]') !== null`, {
      label: "settings loaded",
    });
    const sections = await count(cdp, "[data-testid^='settings-category-']");
    const channel = await text(cdp, "[data-testid='settings-channel-status']");
    const sfx = await text(cdp, "[data-testid='settings-sfx-policy']");
    const titleBefore = await text(cdp, "[data-testid='settings-section-title']");

    checks.push(check("12+ 分节导航", sections >= 12, `sections=${sections}`));
    checks.push(check("settings_get 已同步", /已同步|synced/i.test(channel || ""), `channel=${(channel || "").slice(0, 120)}`));
    checks.push(check("SFX 策略显示真实未设置态", /未设置|Core 默认/.test(sfx || ""), `sfx=${(sfx || "").slice(0, 120)}`));

    await clickSelector(cdp, "[data-testid^='settings-category-']", 3);
    await sleep(400);
    const titleAfter = await text(cdp, "[data-testid='settings-section-title']");
    checks.push(check("切分节改变内容标题", Boolean(titleAfter) && titleAfter !== titleBefore, `${titleBefore} -> ${titleAfter}`));

    await shot(cdp, "05-settings-real-core");
    record("S5", "设置页（真实 settings_get + 分节切换）", checks);
  }

  /* ------------------------------------------- S6 新建作品 = 真实写入 + 刷新 */
  {
    const checks = [];
    await clickSelector(cdp, "[role='tab']", 0);
    await waitFor(cdp, `document.querySelector('[data-testid="page-shelf"]') !== null`, { label: "page-shelf" });
    await clickSelector(cdp, "[data-testid='shelf-create']");
    await waitFor(cdp, `document.querySelector('[data-testid="create-title-dialog"]') !== null`, {
      label: "create dialog",
    });
    await shot(cdp, "06-create-dialog-real");

    await clickSelector(cdp, "[data-testid='create-title-input']");
    const focusedInput = await evaluate(cdp, "document.activeElement && document.activeElement.getAttribute('data-testid')");
    checks.push(check("标题输入框可聚焦", focusedInput === "create-title-input", `activeElement=${focusedInput}`));

    const bookTitle = `端到端验收-${Date.now().toString().slice(-6)}`;
    await insertText(cdp, bookTitle);
    const inputValue = await evaluate(cdp, "document.querySelector('[data-testid=\"create-title-input\"]')?.value ?? null");
    checks.push(check("标题写入受控输入框", inputValue === bookTitle, `value=${inputValue}`));

    await clickSelector(cdp, "[data-testid='create-title-submit-btn']");
    // The create round-trip goes through real IPC to the real Core. Wait for
    // ANY settled outcome (dialog closed = accepted, error text = refused) so a
    // refusal is reported as a finding instead of hanging the whole run.
    const settled = await (async () => {
      const deadline = Date.now() + 30000;
      while (Date.now() < deadline) {
        const closed = await evaluate(
          cdp,
          `document.querySelector('[data-testid="create-title-dialog"]') === null`,
        );
        if (closed) return { closed: true, error: null };
        const err = await text(cdp, "[data-testid='create-title-error']");
        if (err) return { closed: false, error: err };
        await sleep(250);
      }
      return { closed: false, error: null };
    })();
    checks.push(
      check(
        "创建被真实 Core 接受（对话框关闭）",
        settled.closed,
        settled.error ? `error=${settled.error}` : settled.closed ? "accepted" : "timeout",
      ),
    );

    if (settled.closed) {
      await waitFor(cdp, `document.querySelectorAll('[data-testid^="book-"]').length > 0`, {
        label: "book card appears (real Core write + refresh)",
        timeoutMs: 30000,
      });
      const cards = await count(cdp, "[data-testid^='book-']");
      const gridText = await text(cdp, "[data-testid='shelf-grid']");
      const statusNow = await text(cdp, "[data-testid='shelf-statusbar']");
      checks.push(check("真实写入后书架出现书卡", cards >= 1, `cards=${cards}`));
      checks.push(
        check("书卡显示我写入的标题", (gridText || "").includes(bookTitle), `grid=${(gridText || "").slice(0, 160)}`),
      );
      checks.push(check("作品计数从 0 变为 1（真实刷新）", /1 部作品/.test(statusNow || ""), `statusbar=${statusNow}`));

      // Selecting the fresh book must load real chapters through IPC too.
      await clickSelector(cdp, "[data-testid^='book-']", 0);
      await sleep(900);
      const selectedTitle = await text(cdp, "[data-testid='shelf-detail']");
      const chapterState = await count(cdp, "[data-testid='shelf-chapters-empty'], [data-testid='chapter-list']");
      checks.push(
        check(
          "选中作品后详情面板显示该作品",
          (selectedTitle || "").includes(bookTitle),
          `detail=${(selectedTitle || "").slice(0, 120)}`,
        ),
      );
      checks.push(check("章节区为真实空态或真实列表", chapterState >= 1, `chapterStateNodes=${chapterState}`));
    } else {
      await shot(cdp, "07-create-failed");
    }

    await shot(cdp, "07-shelf-with-real-book");
    record("S6", "新建作品（真实 Core 写入 + 书架刷新）", checks);
  }

  /* ------------------------------------------------------------- S7 主题 */
  {
    const checks = [];
    const before = await evaluate(
      cdp,
      `(() => ({ theme: document.documentElement.dataset.theme, bg: getComputedStyle(document.body).backgroundColor }))()`,
    );
    await clickSelector(cdp, "[data-testid='theme-toggle']");
    await sleep(500);
    const after = await evaluate(
      cdp,
      `(() => ({ theme: document.documentElement.dataset.theme, bg: getComputedStyle(document.body).backgroundColor }))()`,
    );
    checks.push(check("主题切换改变 data-theme", before.theme !== after.theme, `${before.theme} -> ${after.theme}`));
    checks.push(check("主题切换改变实际计算背景色", before.bg !== after.bg, `${before.bg} -> ${after.bg}`));
    await shot(cdp, "08-theme-light");

    // restore
    await clickSelector(cdp, "[data-testid='theme-toggle']");
    await sleep(400);
    const restored = await evaluate(cdp, "document.documentElement.dataset.theme");
    checks.push(check("可切回原主题", restored === before.theme, `theme=${restored}`));

    record("S7", "主题切换（真机计算样式，非 jsdom）", checks);
  }

  report.ok = scenarios.every((s) => s.ok);
} catch (error) {
  console.error("\n[FATAL]", error && error.stack ? error.stack : error);
  scenarios.push({
    scenarioId: "FATAL",
    title: "harness failure",
    ok: false,
    checks: [check("harness", false, String(error && error.message ? error.message : error))],
  });
  report.ok = false;
} finally {
  if (app) {
    try {
      const exit = await app.teardown();
      report.appExit = exit;
    } catch (error) {
      report.teardownError = String(error && error.message ? error.message : error);
    }
  }
}

/* ------------------------------------------------------------- evidence out */

report.finishedAt = new Date().toISOString();
mkdirSync(CANONICAL_RUN_DIR, { recursive: true });
const runDir = CANONICAL_RUN_DIR;
writeFileSync(path.join(runDir, "report.json"), JSON.stringify(report, null, 2));

// copy run artifacts (logs + shots) into the canonical evidence dir
const dirs = launchDirs(RUN_ROOT);
try {
  cpSync(dirs.shots, path.join(runDir, "shots"), { recursive: true });
} catch {}
try {
  cpSync(dirs.logs, path.join(runDir, "logs"), { recursive: true });
} catch {}

console.log(`\n=== ${TASK_ID} / ${RUN_ID} ===`);
for (const s of scenarios) console.log(`${s.ok ? "PASS" : "FAIL"}  ${s.scenarioId}  ${s.title}`);
console.log(`\nreport: ${path.join(runDir, "report.json")}`);
console.log(`result: ${report.ok ? "PASS" : "FAIL"}`);
process.exit(report.ok ? 0 : 1);
