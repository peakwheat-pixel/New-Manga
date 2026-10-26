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

function submitNativePickerPath(processId, filePath) {
  const script = [
    "$ErrorActionPreference = 'Stop'",
    "Add-Type -AssemblyName UIAutomationClient",
    "Add-Type -AssemblyName UIAutomationTypes",
    "Add-Type -TypeDefinition 'using System; using System.Text; using System.Runtime.InteropServices; public static class NativePickerFocus { [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; } [DllImport(\"user32.dll\", SetLastError=true)] public static extern IntPtr GetForegroundWindow(); [DllImport(\"user32.dll\", SetLastError=true)] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId); [DllImport(\"user32.dll\", SetLastError=true)] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool attach); [DllImport(\"user32.dll\", SetLastError=true)] public static extern bool SetForegroundWindow(IntPtr hWnd); [DllImport(\"user32.dll\", SetLastError=true)] public static extern bool BringWindowToTop(IntPtr hWnd); [DllImport(\"user32.dll\", SetLastError=true)] public static extern bool IsWindow(IntPtr hWnd); [DllImport(\"user32.dll\", SetLastError=true)] public static extern bool IsWindowEnabled(IntPtr hWnd); [DllImport(\"user32.dll\", SetLastError=true)] public static extern IntPtr GetDlgItem(IntPtr hWndParent, int nIDDlgItem); [DllImport(\"user32.dll\", SetLastError=true)] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect); [DllImport(\"user32.dll\", SetLastError=true)] public static extern bool SetCursorPos(int x, int y); [DllImport(\"user32.dll\", SetLastError=true)] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extraInfo); [DllImport(\"user32.dll\", CharSet=CharSet.Unicode, SetLastError=true)] public static extern IntPtr FindWindowEx(IntPtr hWndParent, IntPtr hWndChildAfter, string lpszClass, string lpszWindow); [DllImport(\"user32.dll\", CharSet=CharSet.Unicode, SetLastError=true)] public static extern bool SetWindowText(IntPtr hWnd, string lpString); [DllImport(\"user32.dll\", CharSet=CharSet.Unicode, SetLastError=true)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count); [DllImport(\"user32.dll\", SetLastError=true)] public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam); }'",
    `$processId = ${Number(processId)}`,
    "$root = [System.Windows.Automation.AutomationElement]::RootElement",
    "$deadline = [DateTime]::UtcNow.AddSeconds(10)",
    "$dialog = $null",
    "do { $windows = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition); $dialog = @($windows | Where-Object { $_.Current.ProcessId -eq $processId -and ($_.Current.ClassName -eq '#32770' -or $_.Current.Name -match 'Open|打开|Select|选择') } | Select-Object -First 1)[0]; if (-not $dialog) { Start-Sleep -Milliseconds 200 } } while (-not $dialog -and [DateTime]::UtcNow -lt $deadline)",
    "if (-not $dialog) { throw 'Native picker window not found for Tauri PID' }",
    "$allControls = $dialog.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)",
    "$inputCandidates = @($allControls | Where-Object { $_.Current.AutomationId -match 'FileName|1148|1001' -or $_.Current.Name -match 'File name|文件名' -or $_.Current.ControlType.ProgrammaticName -match 'Edit|ComboBox|Custom' } | ForEach-Object { $_.Current.ControlType.ProgrammaticName + '|' + $_.Current.AutomationId + '|' + $_.Current.Name + '|' + $_.Current.ClassName })",
    "$dialogHandle = [IntPtr]$dialog.Current.NativeWindowHandle",
    "if ($dialogHandle -eq [IntPtr]::Zero) { throw 'Native picker has no HWND' }",
    "$comboHandle = [NativePickerFocus]::GetDlgItem($dialogHandle, 1148)",
    "if ($comboHandle -eq [IntPtr]::Zero) { throw 'Native picker filename control ID 1148 not found' }",
    "$innerCombo = [NativePickerFocus]::FindWindowEx($comboHandle, [IntPtr]::Zero, 'ComboBox', $null)",
    "$editHandle = if ($innerCombo -ne [IntPtr]::Zero) { [NativePickerFocus]::FindWindowEx($innerCombo, [IntPtr]::Zero, 'Edit', $null) } else { [IntPtr]::Zero }",
    "if ($editHandle -eq [IntPtr]::Zero) { $editHandle = [NativePickerFocus]::FindWindowEx($comboHandle, [IntPtr]::Zero, 'Edit', $null) }",
    "if ($editHandle -eq [IntPtr]::Zero) { $editHandle = $comboHandle }",
    `$sourcePath = '${filePath.replaceAll("'", "''")}'`,
    "if (-not [NativePickerFocus]::SetWindowText($editHandle, $sourcePath)) { throw ('Setting filename failed: ' + [Runtime.InteropServices.Marshal]::GetLastWin32Error()) }",
    "$filenameText = New-Object System.Text.StringBuilder 2048",
    "[NativePickerFocus]::GetWindowText($editHandle, $filenameText, $filenameText.Capacity) | Out-Null",
    "if ($filenameText.ToString() -ne $sourcePath) { throw ('Filename edit mismatch: ' + $filenameText.ToString()) }",
    "$editChange = [IntPtr]::new((5 -shl 16) -bor 1148)",
    "[NativePickerFocus]::SendMessage($dialogHandle, 0x0111, $editChange, $comboHandle) | Out-Null",
    "$openButton = [NativePickerFocus]::GetDlgItem($dialogHandle, 1)",
    "$openEnabled = [NativePickerFocus]::IsWindowEnabled($openButton)",
    "$buttonRect = New-Object NativePickerFocus+RECT",
    "[NativePickerFocus]::GetWindowRect($openButton, [ref]$buttonRect) | Out-Null",
    "$shell = New-Object -ComObject WScript.Shell",
    "$activated = $shell.AppActivate($processId)",
    "$foregroundWindow = [NativePickerFocus]::GetForegroundWindow()",
    "$foregroundPid = [uint32]0",
    "$dialogPid = [uint32]0",
    "$foregroundThread = [NativePickerFocus]::GetWindowThreadProcessId($foregroundWindow, [ref]$foregroundPid)",
    "$dialogThread = [NativePickerFocus]::GetWindowThreadProcessId($dialogHandle, [ref]$dialogPid)",
    "$attached = [NativePickerFocus]::AttachThreadInput($foregroundThread, $dialogThread, $true)",
    "$foreground = [NativePickerFocus]::SetForegroundWindow($dialogHandle)",
    "[NativePickerFocus]::BringWindowToTop($dialogHandle) | Out-Null",
    "if ($attached) { [NativePickerFocus]::AttachThreadInput($foregroundThread, $dialogThread, $false) | Out-Null }",
    "Start-Sleep -Milliseconds 200",
    "$openElements = @($allControls | Where-Object { $_.Current.AutomationId -eq '1' -and $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button })",
    "$invokeResult = $false",
    "if ($openElements.Count -gt 0) { try { $openElements[0].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); $invokeResult = $true } catch {} }",
    "Start-Sleep -Milliseconds 500",
    "if ([NativePickerFocus]::IsWindow($dialogHandle)) { [NativePickerFocus]::SendMessage($dialogHandle, 0x0111, [IntPtr]::new(1), [IntPtr]::Zero) | Out-Null }",
    "Start-Sleep -Milliseconds 500",
    "if ([NativePickerFocus]::IsWindow($dialogHandle)) {",
    "$mouseX = [int](($buttonRect.Left + $buttonRect.Right) / 2)",
    "$mouseY = [int](($buttonRect.Top + $buttonRect.Bottom) / 2)",
    "[NativePickerFocus]::SetCursorPos($mouseX, $mouseY) | Out-Null",
    "Start-Sleep -Milliseconds 100",
    "[NativePickerFocus]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)",
    "Start-Sleep -Milliseconds 60",
    "[NativePickerFocus]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)",
    "Start-Sleep -Milliseconds 500",
    "}",
    "$windowsAfter = @($root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition) | Where-Object { $_.Current.ProcessId -eq $processId } | ForEach-Object { $_.Current.ClassName + '|' + $_.Current.NativeWindowHandle + '|' + $_.Current.Name })",
    "$stillOpen = [NativePickerFocus]::IsWindow($dialogHandle)",
    "@{ submitted=(-not $stillOpen); dialog=$dialog.Current.Name; class=$dialog.Current.ClassName; hwnd=$dialogHandle.ToInt64(); filenameControl=$comboHandle.ToInt64(); filenameEdit=$editHandle.ToInt64(); filenameText=$filenameText.ToString(); openEnabled=$openEnabled; buttonRect=@($buttonRect.Left,$buttonRect.Top,$buttonRect.Right,$buttonRect.Bottom); mouse=@($mouseX,$mouseY); activated=$activated; foreground=$foreground; foregroundWindow=$foregroundWindow.ToInt64(); foregroundThread=$foregroundThread; dialogThread=$dialogThread; attached=$attached; stillOpen=$stillOpen; invokeResult=$invokeResult; windowsAfter=$windowsAfter; inputCandidates=$inputCandidates; sourcePath=$sourcePath; action='Set Task-local path in filename control; invoke Open via UIA, WM_COMMAND and click fallback' } | ConvertTo-Json -Compress",
  ].join("; ");
  const result = spawnSync("powershell.exe", ["-NoProfile", "-NonInteractive", "-Command", script], {
    encoding: "utf8",
    timeout: 15000,
    windowsHide: true,
  });
  if (result.error || result.status !== 0) {
    throw new Error(`native picker automation failed: ${result.error || result.stderr || result.status}`);
  }
  return JSON.parse((result.stdout || "").trim());
}

function dismissNativePicker(processId) {
  const script = [
    "$ErrorActionPreference = 'Stop'",
    "Add-Type -AssemblyName UIAutomationClient",
    "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class NativePickerDismiss { [DllImport(\"user32.dll\", SetLastError=true)] public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam); }'",
    "$root = [System.Windows.Automation.AutomationElement]::RootElement",
    "$windows = $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)",
    `$dialog = @($windows | Where-Object { $_.Current.ProcessId -eq ${Number(processId)} -and $_.Current.ClassName -eq '#32770' } | Select-Object -First 1)[0]`,
    "if (-not $dialog) { return }",
    "[NativePickerDismiss]::SendMessage([IntPtr]$dialog.Current.NativeWindowHandle, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null",
    "@{ closed=$true; hwnd=$dialog.Current.NativeWindowHandle } | ConvertTo-Json -Compress",
  ].join("; ");
  const result = spawnSync("powershell.exe", ["-NoProfile", "-NonInteractive", "-Command", script], {
    encoding: "utf8",
    timeout: 10000,
    windowsHide: true,
  });
  if (result.error || result.status !== 0) {
    throw new Error(`native picker close failed: ${result.error || result.stderr || result.status}`);
  }
  return (result.stdout || "").trim();
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
  nativePickerAttempts: [],
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

  /* ---------------------------------------- S8 原生文件选择器 + Core 导入 */
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
    writeFileSync(invalidPath, "not an image; used only to assert the native host rejection code\n", {
      flag: "wx",
    });
    report.importFixture = {
      pngPath,
      pngSha256: createHash("sha256").update(readFileSync(pngPath)).digest("hex").toUpperCase(),
      unsupportedPath: invalidPath,
    };

    try {
      const card = await evaluate(
        cdp,
        `(() => { const el = Array.from(document.querySelectorAll('[data-testid^="book-"]')).find((node) => (node.textContent || "").includes("端到端验收-")); return el ? el.getAttribute("data-testid") : null; })()`,
      );
      bookId = typeof card === "string" ? card.slice("book-".length) : null;
      checks.push(check("S6 创建的作品仍来自真实书架", Boolean(bookId), `bookId=${bookId}`));

      if (bookId) {
        const chapterTitle = `导入验收章节-${Date.now().toString().slice(-5)}`;
        const chapter = await invokeTauri(cdp, "create_chapter", {
          payload: { book_id: bookId, title: chapterTitle },
        });
        chapterId = chapter?.chapter_id || null;
        checks.push(check("通过真实 Tauri IPC 创建导入目标章节", Boolean(chapterId), `chapterId=${chapterId}`));

        await clickSelector(cdp, "[data-testid='tab-workbench']");
        await waitFor(cdp, `document.querySelector('[data-testid="page-workbench"]') !== null`, { label: "S8 refresh via page remount" });
        await clickSelector(cdp, "[data-testid='tab-shelf']");
        await waitFor(cdp, `document.querySelector('[data-testid="page-shelf"]') !== null`, { label: "S8 shelf remounted" });
        await waitFor(cdp, `document.querySelector('[data-testid="chapter-list"] li') !== null`, { label: "Core-created chapter appears" });
        const chapterTitleInShelf = await text(cdp, "[data-testid='chapter-list']");
        checks.push(check("书架重新读取到真实章节", (chapterTitleInShelf || "").includes(chapterTitle), chapterTitleInShelf));

        await clickSelector(cdp, "[data-testid='shelf-import']");
        await waitFor(cdp, `document.querySelector('[data-testid="import-dialog"]') !== null`, { label: "import dialog open" });
        const chapterSelected = await evaluate(
          cdp,
          `(() => { const el = document.querySelector('[data-testid="import-target-chapter-select"]'); return el ? el.value : null; })()`,
        );
        checks.push(check("导入对话框指向目标章节", chapterSelected === chapterId, `selected=${chapterSelected}; expected=${chapterId}`));

        await clickSelector(cdp, "[data-testid='import-file-btn']");
        await waitFor(cdp, `document.querySelector('[data-testid="import-progress-indicator"]') !== null`, { label: "native file picker requested" });
        const nativeImportWindow = submitNativePickerPath(app.child.pid, pngPath);
        report.nativePickerAttempts.push({ file: pngPath, ...nativeImportWindow });
        if (!nativeImportWindow.submitted) throw new Error(`native picker filename control unavailable: ${JSON.stringify(nativeImportWindow)}`);
        await waitFor(
          cdp,
          `document.querySelector('[data-testid="import-report-view"]') !== null || document.querySelector('[data-testid="import-error-banner"]') !== null`,
          { label: "native image import settled", timeoutMs: 30000, intervalMs: 200 },
        );
        const importReport = await evaluate(
          cdp,
          `(() => ({ imported: document.querySelector('[data-testid="report-imported-files"]')?.textContent?.trim() ?? null, rejected: document.querySelector('[data-testid="report-rejected-files"]')?.textContent?.trim() ?? null, error: document.querySelector('[data-testid="import-error-banner"]')?.textContent?.trim() ?? null }))()`,
        );
        imported = importReport.imported === "1" && importReport.rejected === "0";
        checks.push(check("原生选择器导入真实 PNG", imported, JSON.stringify(importReport)));
        if (imported) {
          await clickSelector(cdp, "[data-testid='import-finish-btn']");
          await waitFor(cdp, `document.querySelector('[data-testid="import-dialog"]') === null`, { label: "import dialog finished" });

          const books = await invokeTauri(cdp, "library_list_books");
          const chaptersEnvelope = await invokeTauri(cdp, "list_chapters", { bookId });
          const pagesEnvelope = await invokeTauri(cdp, "list_chapter_pages", { chapterId });
          const coreBook = Array.isArray(books) ? books.find((book) => book.book_id === bookId) : null;
          const coreChapters = Array.isArray(chaptersEnvelope?.chapters) ? chaptersEnvelope.chapters : [];
          const corePages = Array.isArray(pagesEnvelope?.pages) ? pagesEnvelope.pages : [];
          await waitFor(
            cdp,
            `document.querySelector('[data-testid="chapter-list"] .nm-chapter__pages')?.textContent?.trim() === "${corePages.length}p" && document.querySelectorAll('[data-testid="shelf-detail"] .nm-stat__value')[1]?.textContent?.trim() === "${corePages.length} 页"`,
            { label: "shelf reflects imported page count", timeoutMs: 20000 },
          );
          const rendered = await evaluate(
            cdp,
            `(() => ({ books: document.querySelectorAll('[data-testid^="book-"]').length, chapterRows: document.querySelectorAll('[data-testid="chapter-list"] li').length, chapterPageLabel: document.querySelector('[data-testid="chapter-list"] .nm-chapter__pages')?.textContent?.trim() ?? null, detailStats: Array.from(document.querySelectorAll('[data-testid="shelf-detail"] .nm-stat__value')).map((el) => el.textContent?.trim()), gridText: document.querySelector('[data-testid="shelf-grid"]')?.textContent ?? "" }))()`,
          );
          checks.push(check("作品数量与真实 Core 一致", rendered.books === books.length, `UI=${rendered.books}; Core=${books.length}`));
          checks.push(check("章节数量与真实 Core 一致", rendered.chapterRows === coreChapters.length, `UI=${rendered.chapterRows}; Core=${coreChapters.length}`));
          checks.push(check("页数与真实 Core 一致", coreBook?.page_count === corePages.length && rendered.detailStats?.[1] === `${corePages.length} 页` && rendered.chapterPageLabel === `${corePages.length}p`, JSON.stringify({ corePageCount: coreBook?.page_count, corePages: corePages.length, rendered })));
          await shot(cdp, "09-imported-real-page");
        } else {
          await shot(cdp, "09-import-failed");
        }

        // The host must reject unsupported selected files with a visible code;
        // this also covers ImportDialog's real IPC error presentation.
        await clickSelector(cdp, "[data-testid='shelf-import']");
        await waitFor(cdp, `document.querySelector('[data-testid="import-dialog"]') !== null`, { label: "import dialog reopened" });
        await clickSelector(cdp, "[data-testid='import-file-btn']");
        await waitFor(cdp, `document.querySelector('[data-testid="import-progress-indicator"]') !== null`, { label: "second native file picker requested" });
        const nativeErrorWindow = submitNativePickerPath(app.child.pid, invalidPath);
        report.nativePickerAttempts.push({ file: invalidPath, ...nativeErrorWindow });
        if (!nativeErrorWindow.submitted) throw new Error(`native picker filename control unavailable: ${JSON.stringify(nativeErrorWindow)}`);
        await waitFor(cdp, `document.querySelector('[data-testid="import-error-banner"]') !== null`, { label: "unsupported file rejection", timeoutMs: 20000, intervalMs: 200 });
        const importError = await text(cdp, "[data-testid='import-error-banner']");
        const errorCode = importError?.match(/\(([A-Z][A-Z0-9_]+)\)/)?.[1] || null;
        checks.push(check("导入失败明确显示错误码", errorCode === "REF_SCOPE_DENIED", `${errorCode}: ${importError}`));
        await clickSelector(cdp, "[data-testid='import-dialog-close-btn']");

        await clickSelector(cdp, "[data-testid='shelf-detail'] .nm-btn--primary");
        await waitFor(cdp, `document.querySelector('[data-testid="page-reader"]') !== null`, { label: "Reader context established" });
        await clickSelector(cdp, "[data-testid='tab-shelf']");
        await waitFor(cdp, `document.querySelector('[data-testid="page-shelf"]') !== null`, { label: "S8 returns to shelf" });
      }
    } catch (error) {
      checks.push(check("S8 场景执行完成", false, error?.stack || error));
      try { report.nativePickerDismissed = dismissNativePicker(app.child.pid); } catch (dismissError) { report.nativePickerDismissError = String(dismissError); }
      await sleep(250);
      if (await count(cdp, "[data-testid='import-dialog-close-btn']").catch(() => 0)) {
        await clickSelector(cdp, "[data-testid='import-dialog-close-btn']").catch(() => {});
      }
    }
    report.importResult = { imported, bookId, chapterId };
    record("S8", "书架原生导入（Tauri IPC + 真实 Core）", checks);
  }

  /* ---------------------------------------------- S9 Core sidecar 掉线/恢复 */
  {
    const checks = [];
    const pageChecks = [
      { index: 1, page: "page-workbench", label: "工作台" },
      { index: 2, page: "page-reader", label: "阅读器" },
      { index: 3, page: "page-settings", label: "设置" },
      { index: 0, page: "page-shelf", label: "书架" },
    ];
    let killedPids = [];
    try {
      killedPids = stopCoreSidecar(app.child.pid);
      report.coreOutage = { parentPid: app.child.pid, killedPids, pages: [] };
      checks.push(check("仅终止本 Tauri 父进程的 core_service.exe", killedPids.length > 0, `parentPid=${app.child.pid}; killed=${killedPids.join(",")}`));

      for (const item of pageChecks) {
        // shortcut: reserve the final supervisor restart for the recovery read; revisit if its retry budget changes.
        if (item.index !== 1 && item.index !== 0) {
          await waitForCoreSidecar(app.child.pid);
          const pageKilledPids = stopCoreSidecar(app.child.pid);
          killedPids.push(...pageKilledPids);
          report.coreOutage.killedPids = [...killedPids];
          checks.push(check(`${item.label}页前再次定向终止 Core`, pageKilledPids.length > 0, `killed=${pageKilledPids.join(",")}`));
        }
        await clickSelector(cdp, `[data-testid='tab-${item.page.replace("page-", "")}']`);
        await waitFor(cdp, `document.querySelector('[data-testid="${item.page}"]') !== null`, { label: `${item.label} remounted` });
        let errorState = null;
        const deadline = Date.now() + 4500;
        while (Date.now() < deadline) {
          errorState = await evaluate(
            cdp,
            `(() => { const page = document.querySelector('[data-testid="${item.page}"]'); const code = page?.querySelector('[data-testid="page-error-code"]')?.textContent?.trim() ?? null; const alert = page?.querySelector('[role="alert"]')?.getAttribute('data-testid') ?? null; const shelfStatus = document.querySelector('[data-testid="shelf-statusbar"]'); const shelfState = shelfStatus?.querySelector('[data-state]')?.getAttribute('data-state') ?? null; return { code, alert, shelfState, statusText: shelfStatus?.textContent?.trim() ?? null }; })()`,
          );
          if (errorState?.code) break;
          await sleep(100);
        }
        const hasCoreError = /CORE_(UNAVAILABLE|BRIDGE_DOWN)/.test(errorState?.code || "");
        checks.push(check(`${item.label}真实错误态包含错误码`, hasCoreError, JSON.stringify(errorState)));
        report.coreOutage.pages.push({ page: item.page, ...errorState });
        await shot(cdp, `10-core-down-${item.page}`);
      }

      await clickSelector(cdp, "[data-testid='tab-shelf']");
      await waitFor(
        cdp,
        `document.querySelectorAll('[data-testid^="book-"]').length > 0 || document.querySelector('[data-testid="shelf-error"]') !== null`,
        { label: "shelf settled after Core restart", timeoutMs: 20000 },
      );
      let recovered = (await count(cdp, "[data-testid^='book-']")) > 0;
      let coreReady = false;
      if (!recovered) {
        const readyDeadline = Date.now() + 15000;
        while (Date.now() < readyDeadline) {
          try {
            const ping = await invokeTauri(cdp, "core_ping");
            if (ping?.status === "ready") {
              coreReady = true;
              break;
            }
          } catch {}
          await sleep(150);
        }
      }
      if (!recovered && coreReady && (await count(cdp, "[data-testid='page-error-retry']"))) {
        await clickSelector(cdp, "[data-testid='page-error-retry']");
        try {
          await waitFor(cdp, `document.querySelectorAll('[data-testid^="book-"]').length > 0`, { label: "shelf data after retry", timeoutMs: 20000 });
          recovered = true;
        } catch {}
      }
      const recoveredBooks = recovered ? await invokeTauri(cdp, "library_list_books") : [];
      const nextPids = coreSidecarPids(app.child.pid);
      report.coreOutage.recoveredPids = nextPids;
      checks.push(check("Core 重启后真实 core_ping 恢复 ready", coreReady || recovered, `coreReady=${coreReady}; pids=${nextPids.join(",")}`));
      checks.push(check("Core 重启后书架重新拉到真实数据", recovered && Array.isArray(recoveredBooks) && recoveredBooks.length > 0, `books=${recoveredBooks?.length}; pids=${nextPids.join(",")}`));
      checks.push(check("恢复使用新的 core_service.exe PID", nextPids.length > 0 && nextPids.every((pid) => !killedPids.includes(pid)), `killed=${killedPids.join(",")}; recovered=${nextPids.join(",")}`));
    } catch (error) {
      checks.push(check("S9 故障注入与恢复流程完成", false, error?.stack || error));
    }
    record("S9", "真实 Core sidecar 定向终止与自愈", checks);
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
      checks.push(check("无横向滚动溢出", layout.docWidth <= layout.docClientWidth && layout.pageWidth <= layout.width, JSON.stringify({ docWidth: layout.docWidth, clientWidth: layout.docClientWidth, pageWidth: layout.pageWidth })));
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
