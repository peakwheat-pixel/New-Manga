/**
 * DISPLAY-PERF-DECISION-1 / baseline — AC1 cold-start timeline (black box).
 *
 * The pinned release exe exposes NO WebView2 CDP endpoint (wry sets its own
 * additionalBrowserArguments, which makes WebView2 ignore
 * WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS; evidence in REPORT.md). So the cold
 * start is measured entirely from the outside:
 *
 *   OS process StartTime         -> "process start"
 *   child process core_service   -> "Core sidecar spawn"
 *   GetProcess.MainWindowHandle  -> "window visible"
 *   app stderr (epoch-stamped)   -> "[core.derived_gc]" (Core finished its
 *                                   startup GC / answered the ping),
 *                                   "[m2rc2-allowlist]" (setup() reached),
 *                                   "[m2rc1-title]" (setup thread alive)
 *   window pixel signature       -> "first painted content" (25 fps blit probe)
 *
 * Usage: node run-ac1.mjs [runs=3]
 */

import { writeFileSync, readFileSync, readdirSync } from "node:fs";
import path from "node:path";

import { sleep } from "./cdp.mjs";
import {
  CDP_PORT_BASE,
  EVIDENCE_ROOT,
  PINNED_EXE,
  PINNED_EXE_SHA256,
  evidenceFor,
  ensureDir,
  nextRunLabel,
} from "./env.mjs";
import { cleanupTaskProcesses, launchApp, readProbeEvents, writeEvidenceJson } from "./launch.mjs";

const RUNS = Number(process.argv[2] || 3);
const AC1_ROOT = evidenceFor("ac1");

const median = (values) => {
  const clean = values.filter((v) => typeof v === "number" && Number.isFinite(v));
  if (!clean.length) return null;
  const s = [...clean].sort((a, b) => a - b);
  const mid = Math.floor(s.length / 2);
  return s.length % 2 === 0 ? (s[mid - 1] + s[mid]) / 2 : s[mid];
};

const stats = (values) => {
  const clean = values.filter((v) => typeof v === "number" && Number.isFinite(v));
  if (!clean.length) return { n: 0, medianMs: null, minMs: null, maxMs: null, values: [] };
  return {
    n: clean.length,
    medianMs: Math.round(median(clean) * 10) / 10,
    minMs: Math.round(Math.min(...clean) * 10) / 10,
    maxMs: Math.round(Math.max(...clean) * 10) / 10,
    values: clean.map((v) => Math.round(v * 10) / 10),
  };
};

function readJsonl(filePath) {
  try {
    return readFileSync(filePath, "utf8")
      .split(/\r?\n/)
      .filter((l) => l.trim())
      .map((l) => {
        try { return JSON.parse(l); } catch { return { kind: "unparsable", raw: l }; }
      });
  } catch {
    return [];
  }
}

/** Parse the epoch-stamped stderr log into [(epochMs, text)] */
function readStampedLog(filePath) {
  try {
    return readFileSync(filePath, "utf8")
      .split(/\r?\n/)
      .filter((l) => l.includes("\t"))
      .map((line) => {
        const idx = line.indexOf("\t");
        return { epochMs: Number(line.slice(0, idx)), text: line.slice(idx + 1).replace(/\\n$/, "") };
      })
      .filter((e) => Number.isFinite(e.epochMs));
  } catch {
    return [];
  }
}

/**
 * First-painted-content analysis on the blit signature series.
 * Baseline = first 3 frames after the window exists (blank webview area).
 * A frame counts as content when its edge energy exceeds the baseline by a
 * robust margin; two consecutive frames are required (anti-flicker).
 */
function analyzeFrames(frames, appStartEpoch) {
  const usable = frames.filter((f) => f.kind === "paint_frame");
  if (usable.length === 0) return { missing: true, frames: 0 };
  const base = usable.slice(0, Math.min(3, usable.length));
  const baseEdge = median(base.map((f) => f.edge)) ?? 0;
  const baseMean = median(base.map((f) => f.meanL)) ?? 0;
  const threshold = Math.max(1.5, baseEdge * 3 + 0.5);
  let firstContent = null;
  for (let i = 0; i < usable.length - 1; i += 1) {
    if (usable[i].edge > threshold && usable[i + 1].edge > threshold) {
      firstContent = usable[i];
      break;
    }
  }
  const occludedFrames = usable.filter((f) => f.occluded).length;
  // last frame whose signature differs from the previous frame (visual settle)
  let lastChange = usable[0];
  for (let i = 1; i < usable.length; i += 1) {
    if (usable[i].hash !== usable[i - 1].hash) lastChange = usable[i];
  }
  return {
    frames: usable.length,
    sampleFromEpochMs: usable[0].epochMs,
    sampleToEpochMs: usable[usable.length - 1].epochMs,
    baseline: { edge: baseEdge, meanL: baseMean, threshold },
    firstContentEpochMs: firstContent ? firstContent.epochMs : null,
    firstContentRelMs: firstContent ? Math.round((firstContent.epochMs - appStartEpoch) * 10) / 10 : null,
    firstContentSignature: firstContent ? { meanL: firstContent.meanL, edge: firstContent.edge, darkFrac: firstContent.darkFrac } : null,
    lastChangeEpochMs: lastChange.epochMs,
    lastChangeRelMs: Math.round((lastChange.epochMs - appStartEpoch) * 10) / 10,
    occludedFrames,
    sampleIntervalMsApprox:
      usable.length > 1
        ? Math.round(((usable[usable.length - 1].epochMs - usable[0].epochMs) / (usable.length - 1)) * 10) / 10
        : null,
    series: usable.map((f) => ({ t: f.epochMs - appStartEpoch, meanL: f.meanL, edge: f.edge, darkFrac: f.darkFrac, occluded: f.occluded })),
  };
}

async function runOnce(index) {
  const label = nextRunLabel("ac1");
  const cdpPort = CDP_PORT_BASE + index;
  const runEvidenceDir = path.join(AC1_ROOT, label);
  ensureDir(runEvidenceDir);
  process.stderr.write(`\n=== AC1 ${label} (cdp ${cdpPort}, attach=false) t0=${Date.now()} ===\n`);

  const app = await launchApp({ label, cdpPort, evidenceDir: runEvidenceDir, attach: false });

  // Let the window finish its first screen, then stop.
  await sleep(7000);
  await app.teardown();
  await sleep(500);
  const killed = await cleanupTaskProcesses({ appPid: app.timeline.childPid, sinceEpochMs: app.timeline.t0EpochMs });
  await sleep(500);

  const probeEvents = readProbeEvents(app.logs.probeOut);
  const paintEvents = readJsonl(app.logs.paintOut);
  const stderrLines = readStampedLog(app.logs.stderrTsPath);
  const stdoutLines = readStampedLog(app.logs.stdoutTsPath);

  const findProbe = (kind) => probeEvents.find((e) => e.kind === kind) || null;
  const appStarted = findProbe("app_started");
  const coreFirst = findProbe("core_service_first_seen");
  const windowVisible = findProbe("window_visible");
  const webviewFirst = findProbe("webview2_first_seen");
  const catalogFirst = findProbe("catalog_db_first_seen");
  const paintWindow = paintEvents.find((e) => e.kind === "paint_window_found") || null;
  const paintRect = paintEvents.find((e) => e.kind === "paint_client_rect") || null;

  const appStartEpoch = appStarted?.exeStartEpochMs ?? app.timeline.childSpawnedEpochMs;
  const rel = (epoch) => (epoch == null ? null : Math.round((epoch - appStartEpoch) * 10) / 10);

  const stampFind = (needle) => {
    const hit = stderrLines.find((l) => l.text.includes(needle));
    return hit ? { epochMs: hit.epochMs, relMs: rel(hit.epochMs), text: hit.text.slice(0, 200) } : { missing: true };
  };

  const frameAnalysis = analyzeFrames(paintEvents, appStartEpoch);

  const allStderrText = stderrLines.map((l) => l.text).join("\n");
  const supervisorRestarts = (allStderrText.match(/\[supervisor\]/g) || []).length;
  const coreCrashes = (allStderrText.match(/unhandled exception|Failed to execute script/g) || []).length;

  const timeline = {
    appStartEpochMs: appStartEpoch,
    appStartRelMs: 0,
    coreSpawn: coreFirst ? { epochMs: coreFirst.epochMs, relMs: rel(coreFirst.epochMs), corePid: coreFirst.corePid, isOwnChild: coreFirst.isOwnChild } : { missing: true },
    windowVisible: windowVisible ? { epochMs: windowVisible.epochMs, relMs: rel(windowVisible.epochMs), title: windowVisible.title, hwnd: windowVisible.hwnd } : { missing: true },
    webviewFirstSeen: webviewFirst ? { epochMs: webviewFirst.epochMs, relMs: rel(webviewFirst.epochMs), webviewPid: webviewFirst.webviewPid } : { missing: true },
    catalogFirstSeen: catalogFirst ? { epochMs: catalogFirst.epochMs, relMs: rel(catalogFirst.epochMs) } : { missing: true },
    coreDerivedGcLog: stampFind("[core.derived_gc]"),
    coreReadyPingLog: stampFind("[m2rc2-allowlist]"),
    firstTitleLog: stampFind("[m2rc1-title]"),
    firstContentPainted: frameAnalysis.firstContentRelMs == null
      ? { missing: true }
      : { epochMs: frameAnalysis.firstContentEpochMs, relMs: frameAnalysis.firstContentRelMs },
    visualSettled: { epochMs: frameAnalysis.lastChangeEpochMs, relMs: frameAnalysis.lastChangeRelMs },
    cdp: app.timeline.cdpUnavailable ? { unavailable: app.timeline.cdpUnavailable } : { missing: true },
    health: { supervisorRestarts, coreCrashes },
    paint: {
      frames: frameAnalysis.frames,
      sampleIntervalMsApprox: frameAnalysis.sampleIntervalMsApprox,
      baseline: frameAnalysis.baseline,
      occludedFrames: frameAnalysis.occludedFrames,
      clientRect: paintRect ? { w: paintRect.w, h: paintRect.h } : null,
      series: frameAnalysis.series,
    },
  };

  const record = {
    label,
    cdpPort,
    scenarioRoot: app.scenarioRoot,
    pinnedExe: PINNED_EXE,
    pinnedExeSha256: PINNED_EXE_SHA256,
    env: app.env,
    cleanState: app.cleanState,
    launchTimeline: app.timeline,
    timeline,
    method: {
      processStart: "OS Process.StartTime of new-manga.exe (not the launcher clock)",
      coreSpawn: "first core_service.exe whose ParentProcessId == new-manga pid",
      windowVisible: "GetProcess.MainWindowHandle != 0",
      coreReady: "[core.derived_gc] on the Core sidecar's inherited stderr (printed after the Core's startup GC window, i.e. after the startup ping is answerable)",
      setupReached: "[m2rc2-allowlist] printed in Rust setup()",
      firstPaint: "first window blit frame whose pixel edge-energy exceeds 3x the blank baseline (2 consecutive frames), ~25 fps probe",
      clock: "all values Unix ms; relMs = epoch - appStartEpochMs",
    },
    exitInfo: app.exitInfo,
    killedOrphans: killed,
    logs: app.logs,
    rawProbeEvents: probeEvents,
    rawStderr: stderrLines.map((l) => ({ relMs: rel(l.epochMs), text: l.text })),
    rawStdout: stdoutLines.map((l) => ({ relMs: rel(l.epochMs), text: l.text })),
  };
  writeEvidenceJson(path.join(runEvidenceDir, "ac1-run.json"), record);
  try { writeFileSync(path.join(runEvidenceDir, "native-probe.jsonl"), readFileSync(app.logs.probeOut)); } catch {}
  try { writeFileSync(path.join(runEvidenceDir, "paint-frames.jsonl"), readFileSync(app.logs.paintOut)); } catch {}
  try {
    const shots = readdirSafe(app.dirs.shots);
    for (const name of shots) {
      writeFileSync(path.join(runEvidenceDir, name), readFileSync(path.join(app.dirs.shots, name)));
    }
  } catch {}
  return record;
}

function readdirSafe(dir) {
  try {
    return readdirSync(dir);
  } catch {
    return [];
  }
}

const records = [];
for (let i = 0; i < RUNS; i += 1) records.push(await runOnce(i + 1));

const tl = records.map((r) => r.timeline);
const stage = (pick) => stats(tl.map(pick));

const summary = {
  generatedAt: new Date().toISOString(),
  runs: records.length,
  pinnedExe: PINNED_EXE,
  pinnedExeSha256: PINNED_EXE_SHA256,
  units: "ms after new-manga.exe process start (OS Process.StartTime)",
  cdpStatus: records[0]?.timeline?.cdp?.unavailable ? "UNAVAILABLE_ON_FROZEN_RELEASE_EXE" : "unknown",
  stages: {
    coreSidecarSpawned: stage((t) => t.coreSpawn?.relMs),
    coreDerivedGcLog: stage((t) => t.coreDerivedGcLog?.relMs),
    coreReadyPingLog: stage((t) => t.coreReadyPingLog?.relMs),
    windowVisible: stage((t) => t.windowVisible?.relMs),
    webview2FirstSeen: stage((t) => t.webviewFirstSeen?.relMs),
    firstContentPainted: stage((t) => t.firstContentPainted?.relMs),
    visualSettled: stage((t) => t.visualSettled?.relMs),
    firstTitleLog: stage((t) => t.firstTitleLog?.relMs),
  },
  perRun: records.map((r) => ({
    label: r.label,
    appStartEpochMs: r.timeline.appStartEpochMs,
    coreSpawnMs: r.timeline.coreSpawn?.relMs ?? null,
    coreDerivedGcMs: r.timeline.coreDerivedGcLog?.relMs ?? null,
    allowlistSetupMs: r.timeline.coreReadyPingLog?.relMs ?? null,
    windowVisibleMs: r.timeline.windowVisible?.relMs ?? null,
    windowTitle: r.timeline.windowVisible?.title ?? null,
    firstContentMs: r.timeline.firstContentPainted?.relMs ?? null,
    visualSettledMs: r.timeline.visualSettled?.relMs ?? null,
    paintFrames: r.timeline.paint?.frames ?? null,
    paintIntervalMs: r.timeline.paint?.sampleIntervalMsApprox ?? null,
    supervisorRestarts: r.timeline.health?.supervisorRestarts ?? null,
    coreCrashes: r.timeline.health?.coreCrashes ?? null,
    killedOrphans: r.killedOrphans,
  })),
};

writeEvidenceJson(path.join(AC1_ROOT, "ac1-summary.json"), summary);

const lines = ["# AC1 summary (auto-generated)", "", `runs: ${summary.runs}  exe: ${PINNED_EXE_SHA256}`, `cdp: ${summary.cdpStatus}`, "",
  "| stage (ms after process start) | median | min | max | values |", "|---|---|---|---|---|"];
for (const [name, s] of Object.entries(summary.stages)) {
  lines.push(`| ${name} | ${s.medianMs ?? "n/a"} | ${s.minMs ?? "n/a"} | ${s.maxMs ?? "n/a"} | ${JSON.stringify(s.values)} |`);
}
lines.push("", "## per run", "```json", JSON.stringify(summary.perRun, null, 2), "```");
writeFileSync(path.join(AC1_ROOT, "ac1-summary.md"), lines.join("\n"), "utf8");

process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`);
