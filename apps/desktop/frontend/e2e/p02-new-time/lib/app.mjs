/**
 * P02-NEW-TIME-X6-AC1-AC7 — packaged app launch/session management.
 *
 * Launches the pinned packaged EXE (read-only) under the isolated Task env,
 * waits for the WebView2 remote-debugging endpoint, attaches CDP to the
 * main window page target, and provides clean teardown (graceful window
 * close then process kill).
 */

import { spawn } from "node:child_process";
import { createWriteStream, mkdirSync } from "node:fs";
import path from "node:path";
import {
  assertLaunchTargetsClean,
  buildLaunchEnv,
  CDP_PORT,
  launchDirs,
  PINNED_EXE,
  RUN_ROOT,
} from "./env.mjs";
import { CdpConnection, sleep } from "./cdp.mjs";

export async function launchApp({ scenarioRoot = RUN_ROOT, logDir, tag = "app", cleanStateObserved } = {}) {
  const clean = cleanStateObserved || assertLaunchTargetsClean(scenarioRoot);
  const env = buildLaunchEnv(scenarioRoot);
  const effectiveLogDir = logDir || launchDirs(scenarioRoot).logs;
  mkdirSync(effectiveLogDir, { recursive: true });
  const stderrPath = path.join(effectiveLogDir, `${tag}.stderr.log`);
  const stdoutPath = path.join(effectiveLogDir, `${tag}.stdout.log`);
  const stderrSink = createWriteStream(stderrPath, { flags: "a" });
  const stdoutSink = createWriteStream(stdoutPath, { flags: "a" });

  const child = spawn(PINNED_EXE, [], {
    cwd: path.dirname(PINNED_EXE),
    env,
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: false,
  });
  child.stdout.pipe(stdoutSink);
  child.stderr.pipe(stderrSink);

  const exitInfo = { exited: false, code: null, signal: null };
  child.on("exit", (code, signal) => {
    exitInfo.exited = true;
    exitInfo.code = code;
    exitInfo.signal = signal;
  });

  const cdpVersion = await CdpConnection.waitForEndpoint(CDP_PORT, 45000);

  // find the app page target (tauri://localhost or http://tauri.localhost)
  let pageTarget = null;
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    const targets = await CdpConnection.fetchTargets(CDP_PORT);
    pageTarget = targets.find(
      (t) => t.type === "page" && /tauri/i.test(t.url),
    ) || targets.find((t) => t.type === "page");
    if (pageTarget) break;
    await sleep(300);
  }
  if (!pageTarget) throw new Error("no page target on CDP endpoint");

  const cdp = await new CdpConnection(pageTarget.webSocketDebuggerUrl).open();
  await cdp.send("Page.enable").catch(() => {});
  await cdp.send("Runtime.enable").catch(() => {});

  return {
    child,
    cdp,
    exitInfo,
    cleanStateObserved: clean,
    env,
    cdpVersion,
    pageTarget,
    logPaths: { stderrPath, stdoutPath },
    async teardown() {
      try {
        await cdp.send("Page.close").catch(() => {});
      } catch {}
      await cdp.close();
      await sleep(600);
      if (!exitInfo.exited) child.kill();
      await sleep(400);
      if (!exitInfo.exited) child.kill("SIGKILL");
      stderrSink.end();
      stdoutSink.end();
      await sleep(200);
      return { ...exitInfo };
    },
  };
}

export { assertLaunchTargetsClean, buildLaunchEnv, launchDirs, CDP_PORT };
