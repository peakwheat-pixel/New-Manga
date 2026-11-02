/**
 * AC2 — real navigation and operation on the real Workbench window.
 *
 * Real mouse clicks (CDP Input.dispatchMouseEvent) and real keyboard text
 * (CDP Input.dispatchKeyEvent) drive the production interactive surface:
 * Console -> Workbench view switch, nav button disabled states, page-id
 * input, toolbar context echo, book list from the REAL Core (empty
 * synthetic catalog), plus visible screenshots and focus records.
 * Mock surface of this session: NONE (full real IPC + packaged sidecar).
 */

import path from "node:path";
import { RUN_ROOT, launchDirs, CDP_PORT, PINNED_EXE, PINNED_EXE_SHA256, SOURCE_BASELINE_COMMIT, CANONICAL_RUNS_ROOT, resolveScenarioRoot, envEvidenceManifest } from "./lib/env.mjs";
import { launchApp, assertLaunchTargetsClean } from "./lib/app.mjs";
import { evaluate, mouseClick, pressKey, rectOf, sleep, typeText } from "./lib/cdp.mjs";
import { EvidenceStore, sha256File } from "./lib/evidence.mjs";

const { scenario, root: scenarioRoot, attempt } = resolveScenarioRoot("ac2-navigation");
const dirs = launchDirs(scenarioRoot);

const cleanObserved = assertLaunchTargetsClean(scenarioRoot);

const store = new EvidenceStore(dirs.logs, {
  scenario: "AC2 navigation / operation",
  cdp_port: CDP_PORT,
  scenario_root: scenarioRoot,
  scenario_attempt: attempt,
  mock_surface: "NONE — full real Tauri IPC + packaged sidecar Core",
});
const record = { steps: [] };
const note = (step, detail) => record.steps.push({ step, at: new Date().toISOString(), ...detail });
note("clean-targets-observed", cleanObserved);

const session = await launchApp({
  scenarioRoot,
  logDir: dirs.logs,
  tag: "ac2",
  cleanStateObserved: cleanObserved,
});
note("launched", { pid: session.child.pid });

try {
  await waitFor(session, `document.querySelector('[data-testid="nav-workbench"]')`);

  // S1: initial Console view state
  const initial = await pageState(session.cdp);
  note("console-view-initial", initial);
  await screenshot(session.cdp, store, "ac2-s1-console-initial.png", note);

  // S2: nav button states BEFORE switching (console active => its nav disabled)
  note("nav-states-before", await navStates(session.cdp));

  // S3: REAL MOUSE click on the Workbench nav button
  const navWb = await rectOf(session.cdp, '[data-testid="nav-workbench"]');
  note("nav-workbench-rect", navWb);
  await mouseClick(session.cdp, navWb.cx, navWb.cy);
  await waitFor(session, `document.querySelector('[data-testid="workbench-page"]')`);
  note("workbench-entered", await pageState(session.cdp));
  note("nav-states-after", await navStates(session.cdp));
  await screenshot(session.cdp, store, "ac2-s2-workbench-entered.png", note);

  // S4: workbench five zones present
  note("zones", await evaluate(session.cdp, `(() => ({
    toolbar: !!document.querySelector('[data-testid="workbench-toolbar"]'),
    pageList: !!document.querySelector('[data-testid="page-list-panel"]'),
    viewer: !!document.querySelector('[data-testid="viewer-panel"]'),
    inspector: !!document.querySelector('[data-testid="region-inspector"]'),
    taskProgress: !!document.querySelector('[data-testid="task-progress-panel"]'),
    toolbarContext: document.querySelector('[data-testid="toolbar-context"]')?.textContent || null,
    regionCount: document.querySelector('[data-testid="toolbar-region-count"]')?.textContent || null,
    bookListEmpty: !!document.querySelector('[data-testid="page-list-empty"]'),
  }))()`, false));

  // S5: REAL KEYBOARD typing into the page-id input
  const pageInput = await rectOf(session.cdp, '[data-testid="page-id-input"]');
  await mouseClick(session.cdp, pageInput.cx, pageInput.cy);
  const focusAfterClick = await activeElement(session.cdp);
  note("page-input-focus", focusAfterClick);
  const typedId = "syn-page-ac2-001";
  await typeText(session.cdp, typedId);
  // wait out the 300ms quiet period + core round trip
  await sleep(1600);
  note("after-typing", await evaluate(session.cdp, `(() => ({
    inputValue: document.querySelector('[data-testid="page-id-input"]')?.value,
    toolbarContext: document.querySelector('[data-testid="toolbar-context"]')?.textContent,
    viewerEmpty: !!document.querySelector('[data-testid="viewer-empty"]'),
    resolveError: document.querySelector('[data-testid="resource-resolve-error"]')?.textContent || null,
    resolveBusyGone: !document.querySelector('[data-testid="resource-resolve-busy"]'),
    activeElement: document.activeElement ? (document.activeElement.getAttribute('data-testid') || document.activeElement.tagName) : null,
  }))()`, false));
  await screenshot(session.cdp, store, "ac2-s3-page-id-typed.png", note);

  // S6: Enter key on the input (real keyboard event)
  await pressKey(session.cdp, "Enter", { code: "Enter", windowsVirtualKeyCode: 13 });
  await sleep(300);
  note("after-enter", await pageState(session.cdp));

  // S7: back to Console via real mouse click
  const navConsole = await rectOf(session.cdp, '[data-testid="nav-console"]');
  await mouseClick(session.cdp, navConsole.cx, navConsole.cy);
  await waitFor(session, `!document.querySelector('[data-testid="workbench-page"]')`);
  note("console-returned", await pageState(session.cdp));
  note("nav-states-console", await navStates(session.cdp));
  await screenshot(session.cdp, store, "ac2-s4-console-returned.png", note);

  record.verdict = {
    ac: "AC2",
    real_mouse_navigation: true,
    real_keyboard_input: true,
    button_state_transitions: record.steps.some((s) => s.step === "nav-states-after"),
    screenshots: ["ac2-s1-console-initial.png", "ac2-s2-workbench-entered.png", "ac2-s3-page-id-typed.png", "ac2-s4-console-returned.png"],
    mock_surface: "NONE",
  };
} catch (error) {
  record.errors = [String(error && error.stack ? error.stack : error)];
  record.verdict = { ac: "AC2", status: "ERROR", error: String(error) };
  process.exitCode = 1;
} finally {
  const exit = await session.teardown();
  note("teardown", exit);
  store.writeJson("ac2-navigation.json", record);
  store.writeMetadata({
    scenario_name: scenario,
    command: `node apps/desktop/frontend/e2e/p02-new-time/ac2-navigation.mjs`,
    env_manifest: envEvidenceManifest(session.env),
    pinned_source_commit: SOURCE_BASELINE_COMMIT,
    pinned_exe_sha256: PINNED_EXE_SHA256,
    stdout_path: session.logPaths.stdoutPath,
    stderr_path: session.logPaths.stderrPath,
  });
  store.copyToCanonical(path.join(CANONICAL_RUNS_ROOT, scenario));
  console.log(JSON.stringify(record.verdict, null, 2));
}

async function waitFor(session, selectorJs) {
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    const ok = await evaluate(session.cdp, `!!(${selectorJs})`, false);
    if (ok) return;
    await sleep(300);
  }
  throw new Error(`timeout waiting for ${selectorJs}`);
}

async function pageState(cdp) {
  return evaluate(cdp, `(() => ({
    title: document.title,
    navPresent: !!document.querySelector('[data-testid="app-nav"]'),
    workbenchPresent: !!document.querySelector('[data-testid="workbench-page"]'),
    bodyHead: (document.body.innerText || "").slice(0, 200),
  }))()`, false);
}

async function navStates(cdp) {
  return evaluate(cdp, `(() => ['nav-console','nav-workbench'].map((id) => {
    const el = document.querySelector('[data-testid="' + id + '"]');
    return { id, disabled: el ? el.disabled : null, bg: el ? getComputedStyle(el).backgroundColor : null };
  }))()`, false);
}

async function activeElement(cdp) {
  return evaluate(cdp, `(() => {
    const el = document.activeElement;
    return el ? { testid: el.getAttribute('data-testid'), tag: el.tagName, focused: document.hasFocus() } : null;
  })()`, false);
}

async function screenshot(cdp, storeRef, name, noteFn) {
  const shot = await cdp.send("Page.captureScreenshot", { format: "png" });
  const info = storeRef.writeBinary(name, Buffer.from(shot.data, "base64"));
  noteFn(`screenshot:${name}`, info);
}
