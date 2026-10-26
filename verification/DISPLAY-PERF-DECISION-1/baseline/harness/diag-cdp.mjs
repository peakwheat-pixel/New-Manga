/**
 * Diagnostic only: why does the WebView2 CDP endpoint not answer?
 * Launches the pinned exe with an isolated env (same as the real harness),
 * then inspects the WebView2 browser process command lines and the port.
 */
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";

import { PINNED_EXE, TASK_ENV_ROOT, buildLaunchEnv, launchDirs } from "./env.mjs";
import { sleep } from "./cdp.mjs";
import { cleanupTaskProcesses } from "./launch.mjs";

const label = process.argv[2] || "diag-cdp-02";
const cdpPort = Number(process.argv[3] || 9377);
const scenarioRoot = path.join(TASK_ENV_ROOT, "diag", label);
const d = launchDirs(scenarioRoot);
// NOTE: d.catalogDb is a FILE path — never mkdir it.
for (const [name, dir] of Object.entries(d)) {
  if (name === "catalogDb") { mkdirSync(path.dirname(dir), { recursive: true }); continue; }
  mkdirSync(dir, { recursive: true });
}

const env = buildLaunchEnv(scenarioRoot, { cdpPort });
const child = spawn(PINNED_EXE, [], { cwd: path.dirname(PINNED_EXE), env, stdio: ["ignore", "pipe", "pipe"], windowsHide: false });
let stderr = "";
child.stderr.on("data", (d) => { stderr += String(d); });
const t0 = Date.now();

await sleep(6000);

function pwsh(command) {
  return new Promise((resolve) => {
    const p = spawn(process.env.DSH_PWSH || "pwsh", ["-NoProfile", "-NonInteractive", "-Command", command], { stdio: ["ignore", "pipe", "pipe"], windowsHide: true });
    let out = "";
    p.stdout.on("data", (d) => { out += String(d); });
    p.on("close", () => resolve(out));
  });
}

const udd = launchDirs(scenarioRoot).webview2Udd.replace(/'/g, "''");
const cmd = `
Write-Output "--- our webview2 command lines ---"
Get-CimInstance Win32_Process -Filter "Name='msedgewebview2.exe'" | Where-Object { $_.CommandLine -like '*${udd}*' } | ForEach-Object { "PID $($_.ProcessId) :: $($_.CommandLine)" }
Write-Output "--- any webview2 started after t0 ---"
Get-CimInstance Win32_Process -Filter "Name='msedgewebview2.exe'" | Where-Object { $_.CreationDate -ge (Get-Date) } | Measure-Object | Select-Object -ExpandProperty Count
Write-Output "--- listening ports 9360-9400 ---"
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -ge 9360 -and $_.LocalPort -le 9400 } | ForEach-Object { "port=$($_.LocalPort) pid=$($_.OwningProcess)" }
Write-Output "--- new-manga procs ---"
Get-CimInstance Win32_Process -Filter "Name='new-manga.exe'" | ForEach-Object { "pid=$($_.ProcessId) ppid=$($_.ParentProcessId)" }
`;
const out = await pwsh(cmd);

let cdpResult = "n/a";
for (const candidate of [cdpPort, 9345, 9222]) {
  try {
    const r = await fetch(`http://127.0.0.1:${candidate}/json/version`, { signal: AbortSignal.timeout(3000) });
    cdpResult = `${candidate}: HTTP ${r.status} ${(await r.text()).slice(0, 200)}`;
    break;
  } catch (error) {
    cdpResult = `${candidate}: ${error.message}`;
  }
}

const report = { label, cdpPort, t0, env: { WEBVIEW2_USER_DATA_FOLDER: env.WEBVIEW2_USER_DATA_FOLDER, WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS: env.WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS }, cdpResult, pwshOut: out, stderrTail: stderr.slice(-2000), exited: child.exitCode };
writeFileSync(path.join(scenarioRoot, "diag-report.json"), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));

try { child.kill(); } catch {}
await sleep(600);
try { child.kill("SIGKILL"); } catch {}
const killed = await cleanupTaskProcesses({ appPid: child.pid, sinceEpochMs: t0 });
console.log("killed:", killed);
