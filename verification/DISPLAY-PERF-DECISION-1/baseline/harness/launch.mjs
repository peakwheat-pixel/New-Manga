/**
 * DISPLAY-PERF-DECISION-1 / baseline — launch + observe the REAL packaged app.
 *
 * Everything here is measurement-only: the app is spawned with the isolated
 * environment from env.mjs, its stdout/stderr are captured with epoch stamps,
 * a native (Win32) probe times the pre-WebView part of the cold start, and the
 * WebView2 page is attached over CDP as early as the endpoint allows.
 */

import { spawn } from "node:child_process";
import { createWriteStream, writeFileSync, mkdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { Cdp, attachPage, sleep } from "./cdp.mjs";
import {
  PINNED_EXE,
  assertLaunchTargetsClean,
  assertTaskEnvironment,
  buildLaunchEnv,
  ensureDir,
  envManifest,
  launchDirs,
  runRootFor,
} from "./env.mjs";

const HARNESS_DIR = path.dirname(fileURLToPath(import.meta.url));
const NATIVE_PROBE = path.join(HARNESS_DIR, "native-probe.ps1");
const PAINT_PROBE = path.join(HARNESS_DIR, "paint-probe.ps1");

/**
 * In-page recorder installed as soon as CDP attaches. It only OBSERVES: it
 * records page-relative performance.now() marks for the paint/navigation
 * timeline and for the first appearance of the shell/shelf milestones, so the
 * cold-start timeline can be reconstructed without having perturbed boot.
 *
 * epochOf(perfNow) = performance.timeOrigin + perfNow   (both in ms)
 */
export const RECORDER_SOURCE = String.raw`
(() => {
  if (window.__dp1) return window.__dp1;
  const M = {};
  const seen = {};
  function mark(name) {
    if (M[name] == null) M[name] = performance.now();
  }
  function q(sel) { try { return document.querySelector(sel); } catch { return null; } }

  const state = {
    installedAtPerfNow: performance.now(),
    installedAtEpochMs: Date.now(),
    timeOrigin: performance.timeOrigin,
    marks: M,
    seen: seen,
    page: null,
  };
  window.__dp1 = state;

  // One sticky poll: first time each milestone becomes true (checks the DOM
  // directly, no framework hooks, no monkey-patching of product code).
  const timer = setInterval(() => {
    try {
      if (document.readyState !== "loading") mark("dom_ready_" + document.readyState);
      if (q('[data-testid="app-root"]') || q('[data-testid="app-shell"]')) mark("app_root");
      if (q('[data-testid="page-shelf"]')) mark("shelf_page");
      const skeleton = q('[data-testid="bookshelf-loading-skeleton"]');
      if (skeleton) { seen.skeleton = true; } else if (seen.skeleton) { mark("skeleton_gone"); }
      if (q('[data-testid="bookshelf-main-content"]') || q('.nm-shelf')) mark("shelf_content");
      if (q('[data-testid="book-card"]') || q('[data-testid^="book-"]')) mark("first_book_card");
      if (q('[data-testid="reader-page-image"]')) mark("reader_page_image");
      if (q('[data-testid="page-reader"]')) mark("reader_page");
      if (q('[data-testid="nav-shelf"]') || q('[data-testid="tab-shelf"]')) mark("nav_ready");
    } catch {}
  }, 8);

  try {
    state.paint = performance.getEntriesByType("paint").map((e) => ({ name: e.name, startTime: e.startTime }));
    const nav = performance.getEntriesByType("navigation")[0];
    state.navigation = nav
      ? { startTime: nav.startTime, responseEnd: nav.responseEnd, domInteractive: nav.domInteractive,
          domContentLoadedEventEnd: nav.domContentLoadedEventEnd, loadEventEnd: nav.loadEventEnd,
          type: nav.type, transferSize: nav.transferSize, decodedBodySize: nav.decodedBodySize }
      : null;
  } catch {}

  state.snapshot = () => {
    const out = {
      nowPerfNow: performance.now(),
      nowEpochMs: Date.now(),
      timeOrigin: performance.timeOrigin,
      marks: {}, paint: [], navigation: null,
      readyState: document.readyState,
      devicePixelRatio: window.devicePixelRatio,
      innerWidth: window.innerWidth, innerHeight: window.innerHeight,
    };
    for (const [k, v] of Object.entries(M)) out.marks[k] = v;
    try { out.paint = performance.getEntriesByType("paint").map((e) => ({ name: e.name, startTime: e.startTime })); } catch {}
    try {
      const nav = performance.getEntriesByType("navigation")[0];
      out.navigation = nav ? { startTime: nav.startTime, responseEnd: nav.responseEnd,
        domInteractive: nav.domInteractive, domContentLoadedEventEnd: nav.domContentLoadedEventEnd,
        loadEventEnd: nav.loadEventEnd } : null;
    } catch {}
    return out;
  };
  // Keep the milestone poller alive (8ms) for the cold-start window, then stop.
  setTimeout(() => clearInterval(timer), 180000);
  return state.snapshot();
})()
`;

/** Wait until a JSONL file contains a line with the given "kind". */
export async function waitForJsonlKind(filePath, kind, timeoutMs = 20000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const text = readFileSync(filePath, "utf8");
      if (text.includes(`"kind":"${kind}"`)) return true;
    } catch {}
    await sleep(10);
  }
  return false;
}

/**
 * Launch the pinned release exe with the isolated environment.
 *
 * @param {object} opts
 * @param {string} opts.label        evidence/run label (unique)
 * @param {number} opts.cdpPort      CDP port (>= 9360, unique per launch)
 * @param {string} opts.evidenceDir  repo evidence dir for this launch
 * @param {boolean} [opts.attach]    attach CDP + install recorder (default true)
 */
export async function launchApp({ label, cdpPort, evidenceDir, attach = true, cdpTimeoutMs = 90000 }) {
  const scenarioRoot = runRootFor(label);
  const cleanState = assertLaunchTargetsClean(scenarioRoot);
  const dirs = launchDirs(scenarioRoot);
  const env = buildLaunchEnv(scenarioRoot, { cdpPort });
  assertTaskEnvironment(env);

  ensureDir(dirs.logs);
  ensureDir(dirs.shots);
  ensureDir(dirs.probe);
  ensureDir(evidenceDir);

  const clockPath = path.join(dirs.probe, "clock.json");
  const pidPath = path.join(dirs.probe, "app-pid.json");
  const probeOut = path.join(dirs.probe, "native-probe.jsonl");
  const t0EpochMs = Date.now();
  writeFileSync(clockPath, JSON.stringify({ t0EpochMs, cdpPort, catalogDb: dirs.catalogDb }), "utf8");

  // Native probe FIRST (it waits for the pid file), so the pre-WebView part of
  // the cold start is observed even though pwsh itself needs ~400 ms to start.
  const probeErr = createWriteStream(path.join(dirs.logs, "native-probe.stderr.log"), { flags: "a" });
  const probe = spawn(
    process.env.DSH_PWSH || "pwsh",
    ["-NoProfile", "-NoLogo", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", NATIVE_PROBE,
      "-PidFile", pidPath, "-ClockFile", clockPath, "-OutFile", probeOut, "-TimeoutMs", "120000"],
    { stdio: ["ignore", "pipe", "pipe"], windowsHide: true },
  );
  probe.stdout.on("data", () => {});
  probe.stderr.pipe(probeErr);

  // First-paint pixel probe: the window is sampled from the outside because the
  // release exe exposes no CDP endpoint.
  const paintOut = path.join(dirs.probe, "paint-frames.jsonl");
  const paintErr = createWriteStream(path.join(dirs.logs, "paint-probe.stderr.log"), { flags: "a" });
  const paint = spawn(
    process.env.DSH_PWSH || "pwsh",
    ["-NoProfile", "-NoLogo", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", PAINT_PROBE,
      "-PidFile", pidPath, "-OutFile", paintOut, "-ShotDir", dirs.shots, "-SampleMs", "6500", "-TimeoutMs", "30000"],
    { stdio: ["ignore", "pipe", "pipe"], windowsHide: true },
  );
  paint.stdout.on("data", () => {});
  paint.stderr.pipe(paintErr);

  // Wait for both probes to announce readiness BEFORE starting the app, so their
  // polling loops are already running at t0 (without this the two earliest
  // events would be latched in the first poll, losing sub-400 ms resolution).
  await waitForJsonlKind(probeOut, "probe_ready", 25000);
  await waitForJsonlKind(paintOut, "paint_probe_ready", 25000);

  const spawnRequestedEpochMs = Date.now();
  const stdoutPath = path.join(dirs.logs, "app.stdout.log");
  const stderrPath = path.join(dirs.logs, "app.stderr.log");
  const stdoutTsPath = path.join(dirs.logs, "app.stdout.ts.log");
  const stderrTsPath = path.join(dirs.logs, "app.stderr.ts.log");
  const stdoutSink = createWriteStream(stdoutPath, { flags: "a" });
  const stderrSink = createWriteStream(stderrPath, { flags: "a" });
  const stdoutTs = createWriteStream(stdoutTsPath, { flags: "a" });
  const stderrTs = createWriteStream(stderrTsPath, { flags: "a" });

  const child = spawn(PINNED_EXE, [], {
    cwd: path.dirname(PINNED_EXE),
    env,
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: false,
  });

  const exitInfo = { exited: false, code: null, signal: null, epochMs: null };
  child.on("exit", (code, signal) => {
    exitInfo.exited = true;
    exitInfo.code = code;
    exitInfo.signal = signal;
    exitInfo.epochMs = Date.now();
  });

  child.stdout.on("data", (chunk) => {
    stdoutSink.write(chunk);
    stdoutTs.write(`${Date.now()}\t${String(chunk).replace(/\n/g, "\\n")}\n`);
  });
  child.stderr.on("data", (chunk) => {
    stderrSink.write(chunk);
    stderrTs.write(`${Date.now()}\t${String(chunk).replace(/\n/g, "\\n")}\n`);
  });
  const childSpawnedEpochMs = Date.now();
  writeFileSync(pidPath, JSON.stringify({ appPid: child.pid, t0EpochMs }), "utf8");

  const result = {
    label,
    cdpPort,
    scenarioRoot,
    evidenceDir,
    dirs,
    cleanState,
    env: envManifest(env, cdpPort),
    timeline: {
      t0EpochMs,
      spawnRequestedEpochMs,
      childSpawnedEpochMs,
      childPid: child.pid,
    },
    logs: { stdoutPath, stderrPath, stdoutTsPath, stderrTsPath, probeOut, probeErrPath: path.join(dirs.logs, "native-probe.stderr.log"), paintOut, paintErrPath: path.join(dirs.logs, "paint-probe.stderr.log") },
    child,
    exitInfo,
    probe,
    paint,
    async teardown() {
      try { await cdp?.close(); } catch {}
      await sleep(400);
      if (!exitInfo.exited) child.kill();
      await sleep(600);
      if (!exitInfo.exited) child.kill("SIGKILL");
      stdoutSink.end(); stderrSink.end(); stdoutTs.end(); stderrTs.end();
      try { probe.kill(); } catch {}
      try { paint.kill(); } catch {}
      await sleep(200);
      return { ...exitInfo };
    },
  };

  let cdp = null;

  if (attach) {
    try {
      const endpoint = await Cdp.waitForEndpoint(cdpPort, cdpTimeoutMs, 40);
      result.timeline.cdpEndpointEpochMs = endpoint.epochMs;
      result.timeline.cdpVersion = endpoint.version;
      const attached = await attachPage(cdpPort, { timeoutMs: 45000 });
      cdp = attached.cdp;
      result.timeline.cdpAttachedEpochMs = Date.now();
      result.timeline.pageTarget = { id: attached.page.id, url: attached.page.url, type: attached.page.type };
      result.cdp = cdp;
      // record the milestone snapshot the moment we attach (cold start evidence)
      try {
        result.timeline.attachSnapshot = await cdp.eval(RECORDER_SOURCE, { awaitPromise: false });
      } catch (error) {
        result.timeline.attachSnapshotError = String(error?.message || error);
      }
    } catch (error) {
      // The frozen release exe has no CDP endpoint (wry overrides the WebView2
      // additional-args env var); record it as a fact instead of failing the
      // launch measurement, which is entirely native-side.
      result.timeline.cdpUnavailable = String(error?.message || error);
    }
  }

  return result;
}

/** Read the native probe JSONL into an array of events. */
export function readProbeEvents(probeOutPath) {
  try {
    const text = readFileSync(probeOutPath, "utf8");
    return text
      .split(/\r?\n/)
      .filter((line) => line.trim().length > 0)
      .map((line) => {
        try { return JSON.parse(line); } catch { return { kind: "unparsable", raw: line }; }
      });
  } catch {
    return [];
  }
}

/**
 * Kill only the sidecar/WebView2 processes that belong to THIS task-env run.
 * Attribution: parent pid is our app pid, or (for reparented orphans) the
 * recorded start time is after our launch and the name is one of the frozen
 * sidecar names. Never touches anything outside the task environment.
 */
export async function cleanupTaskProcesses({ appPid, sinceEpochMs }) {
  const script = `
$ErrorActionPreference='SilentlyContinue'
$appPid = ${Number(appPid) || 0}
$since = ${Number(sinceEpochMs) || 0}
$names = @('core_service','host_bridge','acceptance_bridge','catalog_loader','sfx_detect_probe','msedgewebview2')
$killed = @()
foreach ($n in $names) {
  foreach ($p in [System.Diagnostics.Process]::GetProcessesByName($n)) {
    $kill = $false
    try {
      $cim = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$($p.Id)" -ErrorAction SilentlyContinue
      if ($cim -and ([int]$cim.ParentProcessId -eq $appPid)) { $kill = $true }
      if (-not $kill -and $since -gt 0) {
        try { if (([DateTimeOffset]$p.StartTime).ToUnixTimeMilliseconds() -ge $since) { $kill = $true } } catch {}
      }
    } catch {}
    if ($kill) { try { Stop-Process -Id $p.Id -Force; $killed += "$n:$($p.Id)" } catch {} }
  }
}
$killed -join ","
`;
  const proc = spawn(process.env.DSH_PWSH || "pwsh", ["-NoProfile", "-NonInteractive", "-Command", script], {
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: true,
  });
  let out = "";
  proc.stdout.on("data", (d) => { out += String(d); });
  await new Promise((resolve) => proc.on("close", resolve));
  return out.trim();
}

/** Write a JSON evidence file (pretty) after ensuring its directory exists. */
export function writeEvidenceJson(filePath, value) {
  mkdirSync(path.dirname(filePath), { recursive: true });
  writeFileSync(filePath, JSON.stringify(value, null, 2), "utf8");
  return filePath;
}

export { sleep };
