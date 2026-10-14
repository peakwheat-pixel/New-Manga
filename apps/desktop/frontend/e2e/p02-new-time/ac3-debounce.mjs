/**
 * AC3 — 300ms quiet-period and stale-response windows on the real page.
 *
 * Phase A (REAL IPC, no mocks): type a page id key-by-key with real key
 * events at ~80ms intervals, then read the page-side invoke log (page
 * performance.now() monotonic clock). Assert: no intermediate prefix fired
 * resolve_page_resource / list_regions; after the 300ms quiet period each
 * fired exactly ONCE for the final page id.
 *
 * Phase B (REAL page + labelled invoke-level mocks): switch page ids
 * inside the quiet period (old timer must be cancelled — only the final id
 * fires) and a delayed resolve for the OLD page must not overwrite the
 * current page's resolved state (late-reply guard). Timing evidence comes
 * from the real page clock; no fake timers are used anywhere.
 *
 * Mock surface: Phase A none (passthrough observer only); Phase B mocks
 * ONLY resolve_page_resource / list_regions at the invoke boundary —
 * clearly labelled MOCK_IPC in every record.
 */

import path from "node:path";
import { RUN_ROOT, launchDirs, CANONICAL_ROOT, resolveScenarioRoot } from "./lib/env.mjs";
import { launchApp, assertLaunchTargetsClean } from "./lib/app.mjs";
import {
  evaluate,
  INVOKE_WRAPPER_SOURCE,
  mouseClick,
  rectOf,
  sleep,
  typeText,
} from "./lib/cdp.mjs";
import { EvidenceStore } from "./lib/evidence.mjs";

const { scenario, root: scenarioRoot, attempt } = resolveScenarioRoot("ac3-debounce");
const dirs = launchDirs(scenarioRoot);

const cleanObserved = assertLaunchTargetsClean(scenarioRoot);

const store = new EvidenceStore(dirs.logs, {
  scenario: "AC3 300ms quiet-period / stale response",
  scenario_root: scenarioRoot,
  scenario_attempt: attempt,
  mock_surface: "Phase A: observer wrapper only (passthrough). Phase B: MOCK_IPC for resolve_page_resource/list_regions at the invoke boundary; product React code and timers fully real.",
});
const record = { steps: [] };
const note = (step, detail) => record.steps.push({ step, at: new Date().toISOString(), ...detail });
note("clean-targets-observed", cleanObserved);

const session = await launchApp({
  scenarioRoot,
  logDir: dirs.logs,
  tag: "ac3",
  cleanStateObserved: cleanObserved,
});
note("launched", { pid: session.child.pid });

async function installObserver() {
  await session.cdp.send("Runtime.addBinding", { name: "__p02Event" });
  session.nodeEvents = [];
  session.cdp.on("Runtime.bindingCalled", (params) => {
    if (params.name === "__p02Event") {
      try { session.nodeEvents.push(JSON.parse(params.payload)); } catch {}
    }
  });
  await session.cdp.send("Page.addScriptToEvaluateOnNewDocument", { source: INVOKE_WRAPPER_SOURCE });
  await session.cdp.send("Page.reload", { ignoreCache: true });
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    const state = await evaluate(session.cdp, `(() => {
      if (typeof window.__p02TryHook === "function") window.__p02TryHook();
      return window.__p02InvokeWrapperState || "not-yet";
    })()`, false);
    const nav = await evaluate(session.cdp, `!!document.querySelector('[data-testid="nav-workbench"]')`, false);
    if (state === "ACTIVE" && nav) return;
    await sleep(400);
  }
  throw new Error("observer wrapper never became ACTIVE");
}

async function gotoWorkbench() {
  const nav = await rectOf(session.cdp, '[data-testid="nav-workbench"]');
  await mouseClick(session.cdp, nav.cx, nav.cy);
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    if (await evaluate(session.cdp, `!!document.querySelector('[data-testid="page-id-input"]')`, false)) return;
    await sleep(300);
  }
  throw new Error("workbench never appeared");
}

async function focusPageInput() {
  const input = await rectOf(session.cdp, '[data-testid="page-id-input"]');
  await mouseClick(session.cdp, input.cx, input.cy);
}

async function clearInput() {
  // select-all + delete via real key events
  await session.cdp.send("Input.dispatchKeyEvent", { type: "rawKeyDown", key: "a", code: "KeyA", windowsVirtualKeyCode: 65, nativeVirtualKeyCode: 65, modifiers: 2 });
  await session.cdp.send("Input.dispatchKeyEvent", { type: "keyUp", key: "a", code: "KeyA", windowsVirtualKeyCode: 65, nativeVirtualKeyCode: 65, modifiers: 2 });
  await session.cdp.send("Input.dispatchKeyEvent", { type: "rawKeyDown", key: "Delete", code: "Delete", windowsVirtualKeyCode: 46, nativeVirtualKeyCode: 46 });
  await session.cdp.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Delete", code: "Delete", windowsVirtualKeyCode: 46, nativeVirtualKeyCode: 46 });
}

async function invokeLog() {
  return evaluate(session.cdp, `(window.__p02InvokeLog || []).map((e) => ({ ...e, args: e.args }))`, false);
}

async function snapshot(label) {
  return evaluate(session.cdp, `(() => ({
    label: ${JSON.stringify(label)},
    pageId: document.querySelector('[data-testid="page-id-input"]')?.value || "",
    resourceId: document.querySelector('[data-testid="resource-id-input"]')?.value || "",
    resolveBusy: !!document.querySelector('[data-testid="resource-resolve-busy"]'),
    resolveError: document.querySelector('[data-testid="resource-resolve-error"]')?.textContent || null,
    toolbarContext: document.querySelector('[data-testid="toolbar-context"]')?.textContent || null,
    perfNow: performance.now(),
  }))()`, false);
}

try {
  await installObserver();
  note("observer-installed", { state: "ACTIVE", mock: "none (passthrough)" });
  await gotoWorkbench();
  await focusPageInput();

  // ---------- Phase A: real IPC quiet period --------------------------------
  session.nodeEvents.length = 0;
  const typingStart = await evaluate(session.cdp, "performance.now()", false);
  await typeText(session.cdp, "syn-page-a", 80); // 10 chars, ~80ms apart => well inside quiet period
  const typingEnd = await evaluate(session.cdp, "performance.now()", false);
  note("phaseA-typing", { text: "syn-page-a", pagePerfStart: typingStart, pagePerfEnd: typingEnd });
  await sleep(1600); // let the quiet period + real core round trip settle

  const logA = await invokeLog();
  const resolveA = logA.filter((e) => e.kind === "invoke" && e.command === "resolve_page_resource" && e.pagePerfNow >= typingStart);
  const regionsA = logA.filter((e) => e.kind === "invoke" && e.command === "list_regions" && e.pagePerfNow >= typingStart);
  note("phaseA-invoke-log", { resolveCalls: resolveA, regionCalls: regionsA, fullLogTail: logA.slice(-12) });

  const firstResolveAfterTyping = resolveA.length ? resolveA[0].pagePerfNow : null;
  const firstRegionsAfterTyping = regionsA.length ? regionsA[0].pagePerfNow : null;
  record.phaseA = {
    layer: "REAL_IPC (observer passthrough)",
    typed_text: "syn-page-a",
    resolve_page_resource_calls: resolveA.length,
    resolve_args: resolveA.map((c) => c.args),
    list_regions_calls: regionsA.length,
    regions_args: regionsA.map((c) => c.args),
    first_resolve_perf_now: firstResolveAfterTyping,
    first_regions_perf_now: firstRegionsAfterTyping,
    typing_end_perf_now: typingEnd,
    quiet_period_observed_ms:
      firstResolveAfterTyping != null && typingEnd != null
        ? Math.round((firstResolveAfterTyping - typingEnd) * 10) / 10
        : null,
  };
  const shot = await session.cdp.send("Page.captureScreenshot", { format: "png" });
  note("phaseA-screenshot", store.writeBinary("ac3-phaseA.png", Buffer.from(shot.data, "base64")));

  // ---------- Phase B: switch inside the quiet period + stale late reply ----
  // Install invoke-level mocks for exactly two commands.
  await evaluate(session.cdp, `(() => {
    window.__p02MockHandlers = {
      resolve_page_resource: (args) => new Promise((resolve, reject) => {
        const pageId = args && args.pageId ? args.pageId : "";
        if (pageId === "syn-stale-old") {
          setTimeout(() => reject("PAGE_RESOURCE_UNAVAILABLE:STALE_OLD_LATE"), 900); // old page replies LATE with an error
        } else if (pageId === "syn-stale-new") {
          setTimeout(() => resolve({ resource_id: "page-original-syn-stale-new", revision: "current" }), 40);
        } else if (pageId === "syn-quiet-final") {
          setTimeout(() => resolve({ resource_id: "page-original-syn-quiet-final", revision: "current" }), 40);
        } else {
          setTimeout(() => reject("PAGE_RESOURCE_UNAVAILABLE"), 40);
        }
      }),
      list_regions: (args) => new Promise((resolve) => {
        setTimeout(() => resolve({ regions: [], page_size: null }), 40);
      }),
    };
    return Object.keys(window.__p02MockHandlers);
  })()`, false);
  note("phaseB-mocks-installed", { commands: ["resolve_page_resource", "list_regions"], layer: "MOCK_IPC at invoke boundary" });

  // B1: type old id, then switch to new id INSIDE the 300ms window
  await clearInput();
  session.nodeEvents.length = 0;
  const b1Start = await evaluate(session.cdp, "performance.now()", false);
  await typeText(session.cdp, "syn-stale-old");
  await sleep(120); // still inside the quiet period
  await clearInput();
  await typeText(session.cdp, "syn-stale-new");
  const b1TypingEnd = await evaluate(session.cdp, "performance.now()", false);
  note("phaseB1-typing", { first: "syn-stale-old", then: "syn-stale-new", pagePerfStart: b1Start, pagePerfEnd: b1TypingEnd });
  await sleep(1800); // old-page late error would land ~900ms after its (never-fired) resolve... only relevant if a stale call slipped through

  const logB1 = await invokeLog();
  const resolveB1 = logB1.filter((e) => e.kind === "invoke" && e.command === "resolve_page_resource" && e.pagePerfNow >= b1Start);
  const stateB1 = await snapshot("B1-after-switch");
  note("phaseB1-result", { resolveCalls: resolveB1, state: stateB1 });
  record.phaseB1 = {
    layer: "MOCK_IPC (resolve/list mocked; React effect chain real)",
    resolve_calls: resolveB1.map((c) => ({ args: c.args, pagePerfNow: c.pagePerfNow })),
    only_final_id_fired: resolveB1.length === 1 && resolveB1[0].args.pageId === "syn-stale-new",
    resolved_resource_state: stateB1.resourceId,
    stale_error_leaked: stateB1.resolveError !== null,
  };

  // B2: let the OLD page actually fire, then switch — its LATE error reply
  // must not overwrite the new page's resolved state.
  await clearInput();
  session.nodeEvents.length = 0;
  const b2Start = await evaluate(session.cdp, "performance.now()", false);
  await typeText(session.cdp, "syn-stale-old");
  await sleep(500); // old id DOES fire (past quiet period), its reply is delayed 900ms
  await clearInput();
  await typeText(session.cdp, "syn-stale-new");
  const b2SwitchAt = await evaluate(session.cdp, "performance.now()", false);
  note("phaseB2-typing", { old: "syn-stale-old", new: "syn-stale-new", switchPerfNow: b2SwitchAt });
  await sleep(700); // new page resolves fast; old late error lands during this window
  const stateMid = await snapshot("B2-mid");
  await sleep(700); // well past the old page's late reply
  const stateEnd = await snapshot("B2-end");
  const logB2 = await invokeLog();
  const resolveB2 = logB2.filter((e) => e.kind === "invoke" && e.command === "resolve_page_resource" && e.pagePerfNow >= b2Start);
  const settledB2 = logB2.filter((e) => e.kind === "settled" && e.command === "resolve_page_resource" && e.pagePerfNow >= b2Start);
  note("phaseB2-result", { resolveCalls: resolveB2, settled: settledB2, mid: stateMid, end: stateEnd });
  record.phaseB2 = {
    layer: "MOCK_IPC (delayed stale reply; guard logic real)",
    resolve_calls: resolveB2.map((c) => ({ args: c.args, pagePerfNow: c.pagePerfNow })),
    settled: settledB2.map((c) => ({ status: c.status, error: c.error, pagePerfNow: c.pagePerfNow })),
    final_resource_state: stateEnd.resourceId,
    final_resolve_error: stateEnd.resolveError,
    stale_reply_overwrote_current: stateEnd.resourceId !== "page-original-syn-stale-new",
  };
  const shotB = await session.cdp.send("Page.captureScreenshot", { format: "png" });
  note("phaseB-screenshot", store.writeBinary("ac3-phaseB.png", Buffer.from(shotB.data, "base64")));

  record.verdict = {
    ac: "AC3",
    quiet_period_final_id_only: record.phaseA.resolve_page_resource_calls === 1 && record.phaseA.list_regions_calls === 1,
    no_intermediate_prefix_reads: record.phaseA.resolve_args.every((a) => a.pageId === "syn-page-a"),
    switch_cancels_old_timer: record.phaseB1.only_final_id_fired === true,
    stale_reply_guarded: record.phaseB2.stale_reply_overwrote_current === false,
    clock: "page performance.now() monotonic; no fake timers",
  };
} catch (error) {
  record.errors = [String(error && error.stack ? error.stack : error)];
  record.verdict = { ac: "AC3", status: "ERROR", error: String(error) };
  process.exitCode = 1;
} finally {
  const exit = await session.teardown();
  note("teardown", exit);
  store.writeJson("ac3-debounce.json", record);
  store.copyToCanonical(path.join(CANONICAL_ROOT, scenario));
  console.log(JSON.stringify(record.verdict, null, 2));
}
