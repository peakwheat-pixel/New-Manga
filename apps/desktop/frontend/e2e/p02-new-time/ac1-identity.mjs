/**
 * AC1 — real WebView2 harness identity.
 *
 * Launches the pinned packaged EXE under the isolated run-r1 env, proves:
 *  - process identity (m2rc1-desktop.exe + sidecars + msedgewebview2.exe),
 *  - window/page identity (tauri page target, document.title chrome),
 *  - WebView2 runtime identity (CDP Browser/version UA, target process),
 *  - OS identity (CDP SystemInfo),
 *  - production command surface announcement from host stderr,
 *  - pinned binary/source hashes,
 *  - a real screenshot from the real window,
 *  - the mock surface of this session: NONE (full real IPC).
 */

import { readFileSync } from "node:fs";
import path from "node:path";
import { CDP_PORT, PINNED_EXE, launchDirs, RUN_ROOT } from "./lib/env.mjs";
import { launchApp } from "./lib/app.mjs";
import { evaluate, listProcesses, sleep } from "./lib/cdp.mjs";
import { EvidenceStore, sha256File, describeTree } from "./lib/evidence.mjs";

const dirs = launchDirs();
const store = new EvidenceStore(path.join(RUN_ROOT, "logs", "ac1-identity"), {
  scenario: "AC1 runtime identity",
  cdp_port: CDP_PORT,
});

const record = { steps: [], errors: [] };
const note = (step, detail) => {
  record.steps.push({ step, at: new Date().toISOString(), ...detail });
};

// --- pre-launch pins -------------------------------------------------------
const exeHash = sha256File(PINNED_EXE);
note("pinned-binary-hash", { path: PINNED_EXE, sha256: exeHash });

const session = await launchApp({ logDir: path.join(RUN_ROOT, "logs"), tag: "ac1" });
note("launched", {
  pid: session.child.pid,
  spawn_command: PINNED_EXE,
  cwd: path.dirname(PINNED_EXE),
  clean_state: session.cleanStateObserved,
});

try {
  // --- WebView2 / browser identity via CDP (no registry access) -----------
  const browserVersion = session.cdpVersion;
  note("cdp-browser-version", browserVersion);

  const systemInfo = await session.cdp.send("SystemInfo.getInfo");
  note("system-info", {
    osName: systemInfo.osName,
    osVersion: systemInfo.osVersion,
    platform: systemInfo.platformName || null,
    cpuModel: systemInfo.modelName || null,
  });

  const targetInfo = await session.cdp.send("Target.getTargetInfo", {
    targetId: session.pageTarget.id,
  });
  note("page-target-info", {
    targetId: targetInfo.targetInfo.targetId,
    type: targetInfo.targetInfo.type,
    url: targetInfo.targetInfo.url,
    title: targetInfo.targetInfo.title,
    attached: targetInfo.targetInfo.attached,
    browserContextId: targetInfo.targetInfo.browserContextId || null,
  });

  // wait for the page to finish booting (production interactive mode shows nav)
  const bootDeadline = Date.now() + 30000;
  let pageBoot = null;
  while (Date.now() < bootDeadline) {
    pageBoot = await evaluate(
      session.cdp,
      `(() => ({
        readyState: document.readyState,
        title: document.title,
        hasTauriBridge: !!(window.__TAURI__ && window.__TAURI__.core && typeof window.__TAURI__.core.invoke === "function"),
        navPresent: !!document.querySelector('[data-testid="app-nav"]'),
        navConsolePresent: !!document.querySelector('[data-testid="nav-console"]'),
        navWorkbenchPresent: !!document.querySelector('[data-testid="nav-workbench"]'),
        bodyText: (document.body.innerText || "").slice(0, 400),
        ua: navigator.userAgent,
        perfNow: performance.now(),
      }))()`,
      false,
    );
    if (pageBoot.readyState === "complete" && pageBoot.navPresent) break;
    await sleep(500);
  }
  note("page-boot", pageBoot);

  // --- process census (tasklist; project-precedent read-only view) --------
  const census = await listProcesses([
    "m2rc1-desktop.exe",
    "core_service.exe",
    "host_bridge.exe",
    "catalog_loader.exe",
    "acceptance_bridge.exe",
    "msedgewebview2.exe",
  ]);
  note("process-census", {
    exit: census.exit,
    matched: census.matched,
    webview2Count: census.rows.filter((r) => r.name.toLowerCase() === "msedgewebview2.exe").length,
  });

  // --- real screenshot from the real window -------------------------------
  const shot = await session.cdp.send("Page.captureScreenshot", { format: "png" });
  const shotInfo = store.writeBinary("ac1-window-boot.png", Buffer.from(shot.data, "base64"));
  note("screenshot", shotInfo);

  // --- host stderr: production allowlist announcement ----------------------
  // (GUI-subsystem build writes stderr to our redirected pipe)
  await sleep(1500);
  let stderrText = "";
  try {
    stderrText = readFileSync(session.logPaths.stderrPath, "utf8");
  } catch {
    stderrText = "";
  }
  note("host-stderr-announcement", {
    has_production_allowlist: /\[m2rc2-allowlist\] production:/.test(stderrText),
    excerpt: stderrText.slice(0, 1200),
  });

  // --- isolated data roots created by the app (proof of Task-local data) ---
  note("run-r1-tree-after-launch", describeTree(RUN_ROOT).slice(0, 120));

  const verdict = {
    ac: "AC1",
    window_and_webview2_real: Boolean(
      pageBoot?.navPresent && census.matched.some((r) => r.name.toLowerCase() === "m2rc1-desktop.exe"),
    ),
    webview2_runtime_identified: Boolean(browserVersion && /Edg\//.test(browserVersion["User-Agent"] || "")),
    process_identity_captured: census.matched.length > 0,
    pinned_binary_hash_matches: exeHash === store.meta.pinned_exe_sha256.toUpperCase(),
    mock_surface: "NONE — full real Tauri IPC + packaged sidecar Core",
  };
  record.verdict = verdict;
} catch (error) {
  record.errors.push(String(error && error.stack ? error.stack : error));
  record.verdict = { ac: "AC1", status: "ERROR", error: String(error) };
} finally {
  const exit = await session.teardown();
  note("teardown", exit);
  store.writeJson("ac1-identity.json", record);
  console.log(JSON.stringify(record.verdict, null, 2));
  if (record.errors.length) {
    console.error(record.errors.join("\n"));
    process.exitCode = 1;
  }
}
