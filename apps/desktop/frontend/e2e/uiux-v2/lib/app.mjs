/**
 * UIUX-V2-RUNTIME-REALCORE-1 — launch/attach/teardown for the REAL packaged
 * app, reusing the proven zero-dependency CDP client from
 * `e2e/p02-new-time/lib/cdp.mjs` (never modified, only imported).
 *
 * What this gives us, compared with driving the desktop by screenshots:
 *   -真实 DOM 断言（evaluate）而不是看图
 *   -真实鼠标/键盘（CDP Input.dispatch*）而不是坐标猜测
 *   -截图由 CDP Page.captureScreenshot 产生，不需要识图
 */

import { spawn } from "node:child_process";
import { createWriteStream, mkdirSync } from "node:fs";
import path from "node:path";

import { CdpConnection, sleep } from "../../p02-new-time/lib/cdp.mjs";
import {
  assertLaunchTargetsClean,
  buildLaunchEnv,
  CDP_PORT,
  launchDirs,
  PINNED_EXE,
} from "./env.mjs";

export async function launchApp({ scenarioRoot, tag = "app" } = {}) {
  if (!scenarioRoot) throw new Error("launchApp requires scenarioRoot (never a shared path)");
  const clean = assertLaunchTargetsClean(scenarioRoot);
  const env = buildLaunchEnv(scenarioRoot);
  const dirs = launchDirs(scenarioRoot);
  mkdirSync(dirs.logs, { recursive: true });
  mkdirSync(dirs.shots, { recursive: true });

  const stderrPath = path.join(dirs.logs, `${tag}.stderr.log`);
  const stdoutPath = path.join(dirs.logs, `${tag}.stdout.log`);
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

  const cdpVersion = await CdpConnection.waitForEndpoint(CDP_PORT, 60000);

  let pageTarget = null;
  const deadline = Date.now() + 40000;
  while (Date.now() < deadline) {
    const targets = await CdpConnection.fetchTargets(CDP_PORT);
    pageTarget =
      targets.find((t) => t.type === "page" && /tauri/i.test(t.url || "")) ||
      targets.find((t) => t.type === "page");
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
    env,
    cleanStateObserved: clean,
    cdpVersion,
    pageTarget,
    dirs,
    logPaths: { stderrPath, stdoutPath },
    async teardown() {
      try {
        await cdp.send("Page.close").catch(() => {});
      } catch {}
      await cdp.close();
      await sleep(700);
      if (!exitInfo.exited) child.kill();
      await sleep(500);
      if (!exitInfo.exited) child.kill("SIGKILL");
      stderrSink.end();
      stdoutSink.end();
      await sleep(250);
      return { ...exitInfo };
    },
  };
}
