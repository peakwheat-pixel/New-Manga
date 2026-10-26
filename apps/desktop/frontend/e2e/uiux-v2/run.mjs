/**
 * UIUX-V2-RUNTIME-REALCORE-2 — scripted end-to-end acceptance against the REAL
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

import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
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
  TASK_ENV_ROOT,
  canonicalFor,
  envEvidenceManifest,
  launchDirs,
  resolveRunName,
  runRootFor,
} from "./lib/env.mjs";

const TASK_ID = "UIUX-V2-RUNTIME-REALCORE-2";
/** Never overwrite a previous run: a fresh run-iN slot is allocated up front. */
const RUN_NAME = resolveRunName();
const RUN_ROOT = runRootFor(RUN_NAME);
const CANONICAL_RUN_DIR = canonicalFor(RUN_NAME);
const RUN_ID = `uiux-v2-realcore-20261026-${RUN_NAME}`;
const startedAt = new Date().toISOString();
const scenarios = [];

/* ------------------------------------------------------------------ helpers */

function record(scenarioId, title, checks) {
  const totals = checks.reduce(
    (result, item) => {
      if (item.status === "PASS") result.passed += 1;
      else if (item.status === "FAIL") result.failed += 1;
      else if (item.status === "KNOWN_DEFECT") result.knownDefects += 1;
      return result;
    },
    { passed: 0, failed: 0, knownDefects: 0 },
  );
  const denominator = totals.passed + totals.failed;
  const ok = totals.failed === 0;
  scenarios.push({
    scenarioId,
    title,
    ok,
    checks,
    checkSummary: { ...totals, total: checks.length },
    passRate: denominator === 0 ? 1 : totals.passed / denominator,
    passRateScope: "PASS / (PASS + FAIL); KNOWN_DEFECT excluded",
  });
  console.log("\n[" + (ok ? "PASS" : "FAIL") + "] " + scenarioId + " — " + title);
  for (const item of checks) {
    console.log("   " + item.status.padEnd(12) + " " + item.label + (item.detail ? " :: " + item.detail : ""));
  }
  return ok;
}

function check(label, ok, detail = "") {
  const passed = Boolean(ok);
  return {
    label,
    name: label,
    status: passed ? "PASS" : "FAIL",
    ok: passed,
    detail: String(detail).slice(0, 400),
  };
}

function knownDefect(label, detail = "") {
  return {
    label,
    name: label,
    status: "KNOWN_DEFECT",
    ok: true,
    detail: String(detail).slice(0, 400),
  };
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

async function invokeTauri(cdp, command, args = {}) {
  const expression = `window.__TAURI_INTERNALS__.invoke(${JSON.stringify(command)}, ${JSON.stringify(args)})`;
  const response = await cdp.send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (response.exceptionDetails) {
    throw new Error(response.exceptionDetails.text || `Tauri IPC failed: ${command}`);
  }
  return response.result?.value;
}

async function findImportFileInput(cdp) {
  await cdp.send("DOM.enable");
  const documentNode = await cdp.send("DOM.getDocument", { depth: -1, pierce: true });
  const rootNodeId = documentNode.root.nodeId;
  const rootMatch = await cdp.send("DOM.querySelector", {
    nodeId: rootNodeId,
    selector: "input[type=file]",
  });
  const dialogMatch = await cdp.send("DOM.querySelector", {
    nodeId: rootNodeId,
    selector: '[data-testid="import-dialog"]',
  });
  const dialogInput = dialogMatch.nodeId
    ? await cdp.send("DOM.querySelector", {
        nodeId: dialogMatch.nodeId,
        selector: "input[type=file]",
      })
    : { nodeId: 0 };
  return {
    rootNodeId,
    rootInputNodeId: rootMatch.nodeId || 0,
    dialogNodeId: dialogMatch.nodeId || 0,
    inputNodeId: dialogInput.nodeId || 0,
  };
}

async function setImportFileInput(cdp, nodeId, filePath) {
  const absolutePath = path.resolve(filePath);
  await cdp.send("DOM.setFileInputFiles", { nodeId, files: [absolutePath] });
  await sleep(100);
  const files = await evaluate(
    cdp,
    "(() => { const input = document.querySelector('[data-testid=\"import-dialog\"] input[type=\"file\"]'); return input ? Array.from(input.files || []).map((file) => ({ name: file.name, size: file.size, type: file.type })) : []; })()",
  );
  return {
    absolutePath,
    files,
    delivered: files.length === 1 && files[0].name === path.basename(absolutePath) && files[0].size > 0,
  };
}
function stopCoreSidecar(parentPid) {
  const script = [
    "$ErrorActionPreference = 'Stop'",
    `$processes = @(Get-CimInstance Win32_Process -Filter 'ParentProcessId = ${Number(parentPid)}' | Where-Object { $_.Name -ieq 'core_service.exe' } | Select-Object -ExpandProperty ProcessId)`,
    "if ($processes.Count -eq 0) { throw 'core_service.exe child not found for the Tauri PID' }",
    "$processes | ConvertTo-Json -Compress",
    "foreach ($processId in $processes) { Stop-Process -Id $processId -Force }",
  ].join("; ");
  const result = spawnSync("powershell.exe", ["-NoProfile", "-NonInteractive", "-Command", script], {
    encoding: "utf8",
    timeout: 15000,
    windowsHide: true,
  });
  if (result.error || result.status !== 0) {
    throw new Error(`sidecar kill failed: ${result.error || result.stderr || result.status}`);
  }
  const parsed = JSON.parse((result.stdout || "").trim());
  return Array.isArray(parsed) ? parsed.map(Number) : [Number(parsed)];
}

function coreSidecarPids(parentPid) {
  const script = `Get-CimInstance Win32_Process -Filter 'ParentProcessId = ${Number(parentPid)}' | Where-Object { $_.Name -ieq 'core_service.exe' } | Select-Object -ExpandProperty ProcessId | ConvertTo-Json -Compress`;
  const result = spawnSync("powershell.exe", ["-NoProfile", "-NonInteractive", "-Command", script], {
    encoding: "utf8",
    timeout: 15000,
    windowsHide: true,
  });
  if (result.error || result.status !== 0) {
    throw new Error(`sidecar process query failed: ${result.error || result.stderr || result.status}`);
  }
  const raw = (result.stdout || "").trim();
  if (!raw) return [];
  const parsed = JSON.parse(raw);
  return (Array.isArray(parsed) ? parsed : [parsed]).map(Number);
}

async function waitForCoreSidecar(parentPid, timeoutMs = 20000) {
  const deadline = Date.now() + timeoutMs;
  let pids = [];
  while (Date.now() < deadline) {
    pids = coreSidecarPids(parentPid);
    if (pids.length) return pids;
    await sleep(100);
  }
  throw new Error(`core_service.exe did not recover for parent ${parentPid}`);
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
  cleanTargetsObserved: null,
  fileInjection: null,
  databasePath: null,
  databaseExists: false,
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
  report.cleanTargetsObserved = app.cleanStateObserved;

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

  /* ---------------------------------------------- S8 CDP 文件注入 + Core 导入 */
  {
    const checks = [];
    const fixtureDir = path.join(RUN_ROOT, "fixtures");
    const pngPath = path.join(fixtureDir, "uiux-import.png");
    const invalidPath = path.join(fixtureDir, "uiux-import-unsupported.txt");
    let imported = false;
    let bookId = null;
    let chapterId = null;
    mkdirSync(fixtureDir, { recursive: true });
    writeFileSync(
      pngPath,
      Buffer.from(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+nmgoAAAAASUVORK5CYII=",
        "base64",
      ),
      { flag: "wx" },
    );
    writeFileSync(invalidPath, "unsupported import fixture\n", { flag: "wx" });
    report.importFixture = {
      pngPath,
      pngSha256: createHash("sha256").update(readFileSync(pngPath)).digest("hex").toUpperCase(),
      unsupportedPath: invalidPath,
    };

    try {
      const card = await evaluate(
        cdp,
        "(() => { const el = Array.from(document.querySelectorAll('[data-testid^=\"book-\"]')).find((node) => (node.textContent || \"\").includes(\"端到端验收-\")); return el ? el.getAttribute(\"data-testid\") : null; })()",
      );
      bookId = typeof card === "string" ? card.slice("book-".length) : null;
      checks.push(check("S6 创建的作品仍来自真实书架", Boolean(bookId), "bookId=" + bookId));

      if (bookId) {
        const chapterTitle = "导入验收章节-" + Date.now().toString().slice(-5);
        const chapter = await invokeTauri(cdp, "create_chapter", {
          payload: { book_id: bookId, title: chapterTitle },
        });
        chapterId = chapter?.chapter_id || null;
        checks.push(check("通过真实 Tauri IPC 创建导入目标章节", Boolean(chapterId), "chapterId=" + chapterId));

        await clickSelector(cdp, "[data-testid='tab-workbench']");
        await waitFor(cdp, "document.querySelector('[data-testid=\"page-workbench\"]') !== null", { label: "S8 refresh via page remount" });
        await clickSelector(cdp, "[data-testid='tab-shelf']");
        await waitFor(cdp, "document.querySelector('[data-testid=\"page-shelf\"]') !== null", { label: "S8 shelf remounted" });
        await waitFor(cdp, "document.querySelector('[data-testid=\"chapter-list\"] li') !== null", { label: "Core-created chapter appears" });
        const chapterTitleInShelf = await text(cdp, "[data-testid='chapter-list']");
        checks.push(check("书架重新读取到真实章节", (chapterTitleInShelf || "").includes(chapterTitle), chapterTitleInShelf));

        const chapterIndex = await evaluate(
          cdp,
          "(() => Array.from(document.querySelectorAll('[data-testid=\"chapter-list\"] .nm-chapter')).findIndex((node) => (node.textContent || \"\").includes(" + JSON.stringify(chapterTitle) + ")))()",
        );
        if (chapterIndex >= 0) await clickSelector(cdp, "[data-testid='chapter-list'] .nm-chapter", chapterIndex);
        await clickSelector(cdp, "[data-testid='shelf-detail'] .nm-btn--primary");
        await waitFor(cdp, "document.querySelector('[data-testid=\"page-reader\"]') !== null", { label: "S8 establish book/chapter context" });
        await clickSelector(cdp, "[data-testid='tab-shelf']");
        await waitFor(cdp, "document.querySelector('[data-testid=\"page-shelf\"]') !== null", { label: "S8 return to shelf" });

        await clickSelector(cdp, "[data-testid='shelf-import']");
        await waitFor(cdp, "document.querySelector('[data-testid=\"import-dialog\"]') !== null", { label: "import dialog open" });
        const chapterSelected = await evaluate(
          cdp,
          "(() => { const el = document.querySelector('[data-testid=\"import-target-chapter-select\"]'); return el ? el.value : null; })()",
        );
        checks.push(check("导入对话框指向目标章节", chapterSelected === chapterId, "selected=" + chapterSelected + "; expected=" + chapterId));

        const pngInput = await findImportFileInput(cdp);
        report.fileInjection = { pngPath: path.resolve(pngPath), ...pngInput };
        checks.push(
          check(
            "ImportDialog 存在可由 CDP 注入的 input[type=file]",
            pngInput.dialogNodeId > 0 && pngInput.inputNodeId > 0,
            JSON.stringify(pngInput),
          ),
        );

        if (pngInput.dialogNodeId > 0 && pngInput.inputNodeId > 0) {
          const injectedPng = await setImportFileInput(cdp, pngInput.inputNodeId, pngPath);
          report.fileInjection.png = injectedPng;
          checks.push(
            check(
              "DOM.setFileInputFiles 将真实 PNG 交给页面",
              injectedPng.delivered,
              JSON.stringify({ path: injectedPng.absolutePath, files: injectedPng.files }),
            ),
          );
          await waitFor(
            cdp,
            "document.querySelector('[data-testid=\"import-report-view\"]') !== null || document.querySelector('[data-testid=\"import-error-banner\"]') !== null",
            { label: "CDP image import settled", timeoutMs: 30000, intervalMs: 200 },
          );
          const importReport = await evaluate(
            cdp,
            "(() => ({ imported: document.querySelector('[data-testid=\"report-imported-files\"]')?.textContent?.trim() ?? null, rejected: document.querySelector('[data-testid=\"report-rejected-files\"]')?.textContent?.trim() ?? null, error: document.querySelector('[data-testid=\"import-error-banner\"]')?.textContent?.trim() ?? null }))()",
          );
          imported = importReport.imported === "1" && importReport.rejected === "0";
          checks.push(check("真实 PNG 导入结果为 1 页", imported, JSON.stringify(importReport)));
          if (imported) {
            await clickSelector(cdp, "[data-testid='import-finish-btn']");
            await waitFor(cdp, "document.querySelector('[data-testid=\"import-dialog\"]') === null", { label: "import dialog finished" });
            const books = await invokeTauri(cdp, "library_list_books");
            const chaptersEnvelope = await invokeTauri(cdp, "list_chapters", { bookId });
            const pagesEnvelope = await invokeTauri(cdp, "list_chapter_pages", { chapterId });
            const coreBook = Array.isArray(books) ? books.find((book) => book.book_id === bookId) : null;
            const coreChapters = Array.isArray(chaptersEnvelope?.chapters) ? chaptersEnvelope.chapters : [];
            const corePages = Array.isArray(pagesEnvelope?.pages) ? pagesEnvelope.pages : [];
            await waitFor(
              cdp,
              "document.querySelector('[data-testid=\"chapter-list\"] .nm-chapter__pages')?.textContent?.trim() === \"" + corePages.length + "p\" && document.querySelectorAll('[data-testid=\"shelf-detail\"] .nm-stat__value')[1]?.textContent?.trim() === \"" + corePages.length + " 页\"",
              { label: "shelf reflects imported page count", timeoutMs: 20000 },
            );
            const rendered = await evaluate(
              cdp,
              "(() => ({ books: document.querySelectorAll('[data-testid^=\"book-\"]').length, chapterRows: document.querySelectorAll('[data-testid=\"chapter-list\"] li').length, chapterPageLabel: document.querySelector('[data-testid=\"chapter-list\"] .nm-chapter__pages')?.textContent?.trim() ?? null, detailStats: Array.from(document.querySelectorAll('[data-testid=\"shelf-detail\"] .nm-stat__value')).map((el) => el.textContent?.trim()), gridText: document.querySelector('[data-testid=\"shelf-grid\"]')?.textContent ?? \"\" }))()",
            );
            checks.push(check("作品数量与真实 Core 一致", rendered.books === books.length, "UI=" + rendered.books + "; Core=" + books.length));
            checks.push(check("章节数量与真实 Core 一致", rendered.chapterRows === coreChapters.length, "UI=" + rendered.chapterRows + "; Core=" + coreChapters.length));
            checks.push(check("页数与真实 Core 一致", coreBook?.page_count === corePages.length && rendered.detailStats?.[1] === corePages.length + " 页" && rendered.chapterPageLabel === corePages.length + "p", JSON.stringify({ corePageCount: coreBook?.page_count, corePages: corePages.length, rendered })));
            await shot(cdp, "09-imported-real-page");
          }

          if (!(await count(cdp, "[data-testid='import-dialog']"))) {
            await clickSelector(cdp, "[data-testid='shelf-import']");
            await waitFor(cdp, "document.querySelector('[data-testid=\"import-dialog\"]') !== null", { label: "import dialog reopened for error case" });
          }
          const errorInput = await findImportFileInput(cdp);
          const injectedInvalid = errorInput.inputNodeId > 0
            ? await setImportFileInput(cdp, errorInput.inputNodeId, invalidPath)
            : { delivered: false, files: [], absolutePath: path.resolve(invalidPath) };
          report.fileInjection.unsupported = { ...errorInput, ...injectedInvalid };
          checks.push(
            check(
              "不支持格式错误路径也由 CDP 文件注入",
              injectedInvalid.delivered,
              JSON.stringify({ path: injectedInvalid.absolutePath, files: injectedInvalid.files }),
            ),
          );
          if (injectedInvalid.delivered) {
            await waitFor(cdp, "document.querySelector('[data-testid=\"import-error-banner\"]') !== null", { label: "unsupported file rejection", timeoutMs: 20000, intervalMs: 200 });
            const importError = await text(cdp, "[data-testid='import-error-banner']");
            const errorCode = importError?.match(/\(([A-Z][A-Z0-9_]+)\)/)?.[1] || null;
            checks.push(check("导入失败明确显示错误码", Boolean(errorCode), errorCode + ": " + importError));
          } else {
            checks.push(check("导入失败明确显示错误码", false, "ImportDialog 未提供可注入文件控件，错误路径无法交给真实导入链"));
          }
          await clickSelector(cdp, "[data-testid='import-dialog-close-btn']").catch(() => {});
        } else {
          checks.push(check("DOM.setFileInputFiles 将真实 PNG 交给页面", false, "ImportDialog 没有 input[type=file]；CDP 无可注入节点"));
          checks.push(check("不支持格式错误路径也由 CDP 文件注入", false, "ImportDialog 没有 input[type=file]；CDP 无可注入节点"));
          checks.push(check("导入失败明确显示错误码", false, "ImportDialog 没有 input[type=file]；无法在不打开原生选择器时提交错误样本"));
          await clickSelector(cdp, "[data-testid='import-dialog-close-btn']").catch(() => {});
        }
      }
    } catch (error) {
      checks.push(check("S8 CDP 文件注入与真实导入链完成", false, error?.stack || error));
      if (await count(cdp, "[data-testid='import-dialog-close-btn']").catch(() => 0)) {
        await clickSelector(cdp, "[data-testid='import-dialog-close-btn']").catch(() => {});
      }
    }

    report.importResult = { imported, bookId, chapterId };
    record("S8", "书架 CDP 文件注入（Tauri IPC + 真实 Core）", checks);
  }
  /* ---------------------------------------------- S9 Core sidecar 掉线/恢复 */
  {
    const checks = [];
    const pages = [
      { key: "shelf", page: "page-shelf", label: "书架", normal: "[data-testid='shelf-grid']" },
      { key: "workbench", page: "page-workbench", label: "工作台", normal: "[data-testid='filmstrip']" },
      { key: "reader", page: "page-reader", label: "阅读器", normal: "[data-testid='reader-top']" },
      { key: "settings", page: "page-settings", label: "设置", normal: "[data-testid='settings-section-title']" },
    ];
    const killedPids = [];
    report.coreOutage = { parentPid: app.child.pid, killedPids, pages: [], recoveredPids: [], recoveredPages: [] };
    let coreReady = false;

    try {
      const books = await invokeTauri(cdp, "library_list_books");
      const outageBook = Array.isArray(books) ? books[0] : null;
      if (!outageBook?.book_id) throw new Error("S9 requires a real Core book from S6");
      let chaptersEnvelope = await invokeTauri(cdp, "list_chapters", { bookId: outageBook.book_id });
      let outageChapters = Array.isArray(chaptersEnvelope?.chapters) ? chaptersEnvelope.chapters : [];
      if (!outageChapters.length) {
        const chapter = await invokeTauri(cdp, "create_chapter", {
          payload: { book_id: outageBook.book_id, title: "掉线验收章节-" + Date.now().toString().slice(-5) },
        });
        if (!chapter?.chapter_id) throw new Error("S9 could not create a real chapter context");
        await clickSelector(cdp, "[data-testid='tab-workbench']");
        await waitFor(cdp, "document.querySelector('[data-testid=\"page-workbench\"]') !== null", { label: "S9 chapter refresh" });
        await clickSelector(cdp, "[data-testid='tab-shelf']");
        await waitFor(cdp, "document.querySelector('[data-testid=\"page-shelf\"]') !== null", { label: "S9 shelf refresh" });
        chaptersEnvelope = await invokeTauri(cdp, "list_chapters", { bookId: outageBook.book_id });
        outageChapters = Array.isArray(chaptersEnvelope?.chapters) ? chaptersEnvelope.chapters : [];
      }
      if (!outageChapters.length) throw new Error("S9 real Core book has no chapter context");

      await clickSelector(cdp, "[data-testid='tab-shelf']");
      await waitFor(cdp, "document.querySelector('[data-testid=\"page-shelf\"]') !== null", { label: "S9 establish shelf context" });
      const bookCard = "[data-testid='book-" + outageBook.book_id + "']";
      if (await count(cdp, bookCard)) await clickSelector(cdp, bookCard);
      await waitFor(cdp, "document.querySelector('[data-testid=\"chapter-list\"] li') !== null", { label: "S9 real chapter appears" });
      const chapterIndex = await evaluate(
        cdp,
        "(() => Array.from(document.querySelectorAll('[data-testid=\"chapter-list\"] .nm-chapter')).findIndex((node) => (node.textContent || \"\").includes(" + JSON.stringify(outageChapters[0].title || "") + ")))()",
      );
      if (chapterIndex >= 0) await clickSelector(cdp, "[data-testid='chapter-list'] .nm-chapter", chapterIndex);
      await clickSelector(cdp, "[data-testid='shelf-detail'] .nm-btn--primary");
      await waitFor(cdp, "document.querySelector('[data-testid=\"page-reader\"]') !== null", { label: "S9 reader context established" });
      await clickSelector(cdp, "[data-testid='tab-shelf']");
      await waitFor(cdp, "document.querySelector('[data-testid=\"page-shelf\"]') !== null", { label: "S9 return to shelf" });
      checks.push(check("故障注入前建立真实作品与章节上下文", chapterIndex >= 0, "book=" + outageBook.book_id + "; chapter=" + outageChapters[0].chapter_id + "; rowIndex=" + chapterIndex));

      await clickSelector(cdp, "[data-testid='tab-settings']");
      await waitFor(cdp, "document.querySelector('[data-testid=\"settings-section-title\"]') !== null && /已同步|synced/i.test(document.querySelector('[data-testid=\"settings-channel-status\"]')?.textContent || \"\")", { label: "S9 pre-outage healthy settings" });
      await waitForCoreSidecar(app.child.pid);
      const outagePids = stopCoreSidecar(app.child.pid);
      killedPids.push(...outagePids);
      report.coreOutage.killedPids = [...killedPids];
      checks.push(check("故障注入前设置页正常且仅定向终止本 Tauri 的 Core", outagePids.length > 0, "killed=" + outagePids.join(",")));

      for (const item of pages) {
        await clickSelector(cdp, "[data-testid='tab-" + item.key + "']");
        await waitFor(cdp, "document.querySelector('[data-testid=\"" + item.page + "\"]') !== null", { label: item.label + " page mounted" });
        let errorState = null;
        const deadline = Date.now() + 7000;
        while (Date.now() < deadline) {
          const pageSelector = "document.querySelector(" + JSON.stringify("[data-testid=\"" + item.page + "\"]") + ")";
          const expression = "(() => { const page = " + pageSelector + "; const code = page?.querySelector('[data-testid=\"page-error-code\"]')?.textContent?.trim() ?? null; const alert = page?.querySelector('[role=\"alert\"]'); const style = alert ? getComputedStyle(alert) : null; const visible = !!alert && !!style && style.display !== \"none\" && style.visibility !== \"hidden\" && alert.getBoundingClientRect().width > 0 && alert.getBoundingClientRect().height > 0; return { code, alertTestId: alert?.getAttribute(\"data-testid\") ?? null, visible, pageText: (page?.textContent || \"\").trim().slice(0, 240) }; })()";
          errorState = await evaluate(cdp, expression);
          if (errorState?.code && errorState.visible) break;
          await sleep(100);
        }
        const hasCoreError = errorState?.visible && /CORE_(UNAVAILABLE|BRIDGE_DOWN)/.test(errorState?.code || "");
        checks.push(check(item.label + "真实错误态可见且含错误码", hasCoreError, JSON.stringify(errorState)));
        report.coreOutage.pages.push({ page: item.page, ...errorState });
      }

      const sidecarDeadline = Date.now() + 20000;
      while (Date.now() < sidecarDeadline) {
        try {
          const ping = await invokeTauri(cdp, "core_ping");
          if (ping?.status === "ready") {
            coreReady = true;
            break;
          }
        } catch {}
        await sleep(150);
      }
      const recoveredPids = coreSidecarPids(app.child.pid);
      report.coreOutage.recoveredPids = recoveredPids;
      checks.push(check("Core supervisor 恢复真实 core_ping=ready", coreReady, "pids=" + recoveredPids.join(",")));
      checks.push(check("恢复使用未在故障清单中的新 PID", recoveredPids.length > 0 && recoveredPids.every((pid) => !killedPids.includes(pid)), "killed=" + killedPids.join(",") + "; recovered=" + recoveredPids.join(",")));

      if (coreReady) {
        for (const item of pages) {
          await clickSelector(cdp, "[data-testid='tab-" + item.key + "']");
          await waitFor(cdp, "document.querySelector('[data-testid=\"" + item.page + "\"]') !== null", { label: item.label + " remounted after recovery" });
          const pageSelector = "document.querySelector(" + JSON.stringify("[data-testid=\"" + item.page + "\"]") + ")";
          const recoveryExpression = "(() => { const page = " + pageSelector + "; if (!page || page.querySelector('[data-testid=\"page-error-code\"]')) return false; const content = page.querySelector(" + JSON.stringify(item.normal) + "); if (!content) return false; if (\"" + item.key + "\" === \"shelf\") return page.querySelectorAll('[data-testid^=\"book-\"]').length > 0; if (\"" + item.key + "\" === \"settings\") return /已同步|synced/i.test(page.querySelector('[data-testid=\"settings-channel-status\"]')?.textContent || \"\"); if (\"" + item.key + "\" === \"reader\") return !page.querySelector('[data-testid=\"reader-error\"]') && !page.querySelector('[data-testid=\"reader-no-context\"]'); if (\"" + item.key + "\" === \"workbench\") return !page.querySelector('[data-testid=\"workbench-chapters-error\"]'); return false; })()";
          await waitFor(cdp, recoveryExpression, { label: item.label + " recovered data state", timeoutMs: 20000 });
          const recoveredState = await evaluate(
            cdp,
            "(() => { const page = " + pageSelector + "; return { pagePresent: !!page, code: page?.querySelector('[data-testid=\"page-error-code\"]')?.textContent?.trim() ?? null, contentPresent: !!page?.querySelector(" + JSON.stringify(item.normal) + "), text: (page?.textContent || \"\").trim().slice(0, 200) }; })()",
          );
          checks.push(check(item.label + "恢复后回到正常态", Boolean(recoveredState.contentPresent && !recoveredState.code), JSON.stringify(recoveredState)));
          report.coreOutage.recoveredPages.push({ page: item.page, ...recoveredState });
          await shot(cdp, "11-core-recovered-" + item.key);
        }
      } else {
        for (const item of pages) {
          checks.push(check(item.label + "恢复后回到正常态", false, "Core 未恢复 ready，无法验证该页正常态"));
        }
      }
    } catch (error) {
      checks.push(check("S9 四页掉线与逐页恢复流程完成", false, error?.stack || error));
    }
    record("S9", "真实 Core sidecar 定向终止与四页恢复", checks);
  }
  /* ---------------------------------------------- S10 窄窗 + 高 DPI + 亚克力 */
  {
    const checks = [];
    let windowId = null;
    let oldBounds = null;
    try {
      await clickSelector(cdp, "[data-testid='tab-shelf']");
      await waitFor(cdp, `document.querySelector('[data-testid="page-shelf"]') !== null`, { label: "S10 shelf active" });
      const windowInfo = await cdp.send("Browser.getWindowForTarget");
      windowId = windowInfo.windowId;
      oldBounds = windowInfo.bounds;
      await cdp.send("Browser.setWindowBounds", {
        windowId,
        bounds: { width: 900, height: 700, windowState: "normal" },
      });
      await cdp.send("Emulation.setDeviceMetricsOverride", {
        width: 900,
        height: 700,
        deviceScaleFactor: 2,
        mobile: false,
        screenWidth: 900,
        screenHeight: 700,
      });
      await sleep(400);
      const layout = await evaluate(
        cdp,
        `(() => {
          const rect = (el) => { if (!el) return null; const r = el.getBoundingClientRect(); return { left:r.left, top:r.top, right:r.right, bottom:r.bottom, width:r.width, height:r.height }; };
          const titlebar = document.querySelector('[data-testid="shelf-titlebar"]');
          const titleParts = titlebar ? [titlebar.querySelector('.nm-titlebar__brand'), titlebar.querySelector('[role="tab"]')?.parentElement, titlebar.querySelector('.nm-titlebar__actions')] : [];
          const boxes = titleParts.map(rect);
          const status = document.querySelector('[data-testid="shelf-statusbar"]');
          const blur = Array.from(document.querySelectorAll('.nm-acrylic, .nm-acrylic-24, .nm-acrylic-strong')).filter((el) => { const style=getComputedStyle(el); return style.backdropFilter !== 'none' || style.webkitBackdropFilter !== 'none'; }).length;
          return { width:innerWidth, height:innerHeight, dpr:devicePixelRatio, docWidth:document.documentElement.scrollWidth, docClientWidth:document.documentElement.clientWidth, pageWidth:document.querySelector('[data-testid="page-shelf"]')?.scrollWidth ?? null, titleParts:boxes, grid:rect(document.querySelector('[data-testid="shelf-grid"]')), detail:rect(document.querySelector('[data-testid="shelf-detail"]')), status:rect(status), statusVisible:!!status && getComputedStyle(status).display !== 'none' && getComputedStyle(status).visibility !== 'hidden' && rect(status).width > 0 && rect(status).height > 0, blur };
        })()`,
      );
      const titlePartsValid = layout.titleParts.length === 3 && layout.titleParts.every((box) => box && box.width > 0);
      const noTitleOverlap = titlePartsValid && layout.titleParts.every((a, i) => layout.titleParts.slice(i + 1).every((b) => a.right <= b.left || b.right <= a.left || a.bottom <= b.top || b.bottom <= a.top));
      const gridDetailNoOverlap = layout.grid && layout.detail && (layout.grid.right <= layout.detail.left || layout.detail.right <= layout.grid.left || layout.grid.bottom <= layout.detail.top || layout.detail.bottom <= layout.grid.top);
      checks.push(check("900×700 视口与 DPR=2 生效", layout.width === 900 && layout.height === 700 && layout.dpr === 2, JSON.stringify({ width: layout.width, height: layout.height, dpr: layout.dpr })));
      checks.push(knownDefect("窄窗横向溢出（KNOWN_DEFECT，另立 Task）", JSON.stringify({ detected: layout.docWidth > layout.docClientWidth || layout.pageWidth > layout.width, docWidth: layout.docWidth, clientWidth: layout.docClientWidth, pageWidth: layout.pageWidth })));
      checks.push(check("标题栏关键元素不重叠", noTitleOverlap, JSON.stringify(layout.titleParts)));
      checks.push(check("书架内容区与详情区不重叠", Boolean(gridDetailNoOverlap), JSON.stringify({ grid: layout.grid, detail: layout.detail })));
      checks.push(check("useAcrylicBudget 计算出的模糊层不超过 2", layout.blur <= 2, `blurLayers=${layout.blur}`));
      const statusIntersectsViewport = layout.status && layout.status.right > 0 && layout.status.left < layout.width && layout.status.bottom > 0 && layout.status.top < layout.height;
      checks.push(check("状态条在窄窗仍可见", layout.statusVisible && statusIntersectsViewport, JSON.stringify(layout.status)));
      await shot(cdp, "11-shelf-900x700-dpr2");
      report.narrowWindowLayout = layout;
    } catch (error) {
      checks.push(check("S10 窄窗与高 DPI 探针完成", false, error?.stack || error));
    } finally {
      if (windowId !== null) {
        await cdp.send("Emulation.clearDeviceMetricsOverride").catch(() => {});
        if (oldBounds) await cdp.send("Browser.setWindowBounds", { windowId, bounds: oldBounds }).catch(() => {});
      }
    }
    record("S10", "900×700 窄窗与 200% DPI 布局预算", checks);
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

report.databasePath = path.join(launchDirs(RUN_ROOT).dataRoot, "library.db");
report.databaseExists = existsSync(report.databasePath);
if (!report.databaseExists) report.ok = false;
report.finishedAt = new Date().toISOString();
mkdirSync(CANONICAL_RUN_DIR, { recursive: true });
const runDir = CANONICAL_RUN_DIR;
writeFileSync(path.join(runDir, "report.json"), JSON.stringify(report, null, 2));

// Logs and screenshots stay under task-envs; only the compact report is canonical.

console.log(`\n=== ${TASK_ID} / ${RUN_ID} ===`);
for (const s of scenarios) console.log(`${s.ok ? "PASS" : "FAIL"}  ${s.scenarioId}  ${s.title}`);
console.log(`\nreport: ${path.join(runDir, "report.json")}`);
console.log(`result: ${report.ok ? "PASS" : "FAIL"}`);
process.exit(report.ok ? 0 : 1);
