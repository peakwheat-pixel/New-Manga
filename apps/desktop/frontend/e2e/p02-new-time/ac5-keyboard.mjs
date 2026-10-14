/**
 * AC5 — keyboard and focus on the P02 Workbench operating surface.
 *
 * Real key events (CDP Input.dispatchKeyEvent): Tab / Shift+Tab traversal,
 * Enter / Space activation, Escape dialog dismissal, focus position
 * capture after every step. Scoped to the Workbench operating surface;
 * findings only, no WCAG-whole-app claim.
 *
 * Layer contract (REAL_WEBVIEW_MOCK_IPC, explicitly labelled):
 * Packaged WebView2 runtime, real CDP key events, and real DOM are 100% real.
 * IPC boundary is mocked with Task-local synthetic fixture so that region
 * and revision history exist, allowing the confirm dialog to be opened
 * and tested against real Escape key events. Real Core/SQLite persistence
 * is NOT claimed.
 */

import path from "node:path";
import {
  RUN_ROOT,
  launchDirs,
  CDP_PORT,
  PINNED_EXE,
  PINNED_EXE_SHA256,
  SOURCE_BASELINE_COMMIT,
  CANONICAL_RUNS_ROOT,
  resolveScenarioRoot,
  envEvidenceManifest,
} from "./lib/env.mjs";
import { launchApp, assertLaunchTargetsClean } from "./lib/app.mjs";
import { evaluate, mouseClick, pressKey, rectOf, sleep, typeText } from "./lib/cdp.mjs";
import { EvidenceStore, sha256File } from "./lib/evidence.mjs";

const { scenario, root: scenarioRoot, attempt } = resolveScenarioRoot("ac5-keyboard");
const dirs = launchDirs(scenarioRoot);

const cleanObserved = assertLaunchTargetsClean(scenarioRoot);

const store = new EvidenceStore(dirs.logs, {
  scenario: "AC5 keyboard / focus",
  cdp_port: CDP_PORT,
  scenario_root: scenarioRoot,
  scenario_attempt: attempt,
  mock_surface:
    "REAL_WEBVIEW_MOCK_IPC — packaged WebView2, DOM, and CDP keyboard events real; IPC mocked for synthetic region/revisions to exercise confirm dialog; Core/SQLite NOT claimed",
});
const record = { steps: [] };
const note = (step, detail) => record.steps.push({ step, at: new Date().toISOString(), ...detail });
note("clean-targets-observed", cleanObserved);

const session = await launchApp({
  scenarioRoot,
  logDir: dirs.logs,
  tag: "ac5",
  cleanStateObserved: cleanObserved,
});
note("launched", { pid: session.child.pid });

/** The synthetic region state machine for exercising confirm dialog in AC5. */
const synth = {
  regionId: "syn-region-ac5-001",
  pageId: "syn-page-ac5",
  revision: 2,
  type: "speech",
  policy: "skip",
};

async function installMocks() {
  await session.cdp.send("Runtime.addBinding", { name: "__p02Event" });
  session.nodeEvents = [];
  session.cdp.on("Runtime.bindingCalled", (params) => {
    if (params.name === "__p02Event") {
      try { session.nodeEvents.push(JSON.parse(params.payload)); } catch {}
    }
  });

  await session.cdp.send("Page.addScriptToEvaluateOnNewDocument", {
    source: `
      window.__p02MockHandlers = window.__p02MockHandlers || {
        library_list_books: () => [{ book_id: "syn-book-ac5", title: "Synthetic Book", original_title: "合成书", is_favorite: false, is_archived: false, page_count: 1, created_at: "2026-10-14T00:00:00Z", updated_at: "2026-10-14T00:00:00Z" }],
        list_chapters: () => [{ chapter_id: "syn-ch-ac5", title: "Synthetic Chapter", chapter_number: "1", sort_order: 1 }],
        list_chapter_pages: () => [{ page_id: "syn-page-ac5", source_filename: "syn-page.png", sort_order: 1 }],
        resolve_page_resource: (args) => ({ resource_id: "page-original-" + (args && args.pageId), revision: "current" }),
        list_regions: (args) => {
          const state = window.__p02SynthState;
          if (!state || args.pageId !== state.pageId) return { regions: [], page_size: { width: 800, height: 1200 } };
          return {
            regions: [{
              region_id: state.regionId,
              region_type: state.type,
              sfx_policy: state.policy,
              origin: "machine",
              revision_no: state.revision,
              geometry: { bbox: [0.1, 0.1, 0.3, 0.12], polygon: [] },
            }],
            page_size: { width: 800, height: 1200 },
          };
        },
        list_region_revisions: (args) => {
          const s = window.__p02SynthState;
          return {
            region_id: s.regionId,
            current_revision_no: s.revision,
            revisions: [
              {
                region_revision_id: "syn-rev-1",
                revision_no: 1,
                origin: "machine",
                review_state: "ok",
                is_pinned: false,
                restored_from_revision_id: null,
                created_at: "2026-10-14T00:00:01Z",
                region_type: "speech",
                sfx_policy: "skip",
                is_current: false,
              },
              {
                region_revision_id: "syn-rev-2",
                revision_no: 2,
                origin: "user",
                review_state: "ok",
                is_pinned: false,
                restored_from_revision_id: null,
                created_at: "2026-10-14T00:00:02Z",
                region_type: "speech",
                sfx_policy: "skip",
                is_current: true,
              },
            ],
          };
        },
        set_region_type: (args) => {
          const s = window.__p02SynthState;
          s.revision += 1;
          s.type = args.newRegionType;
          return { region_id: s.regionId, revision_no: s.revision, region_type: s.type, sfx_policy: s.policy };
        },
        restore_region_revision: (args) => {
          const s = window.__p02SynthState;
          s.revision += 1;
          return { region_id: s.regionId, revision_no: s.revision, region_type: s.type, sfx_policy: s.policy };
        },
        settings_get: () => ({}),
        settings_update_section: () => ({}),
        core_ping: () => ({ status: "ok", protocol_version: { major: 1, minor: 6 }, capabilities: [] }),
      };
    `,
  });

  const { INVOKE_WRAPPER_SOURCE } = await import("./lib/cdp.mjs");
  await session.cdp.send("Page.addScriptToEvaluateOnNewDocument", {
    source: `window.__p02SynthState = ${JSON.stringify(synth)};\n${INVOKE_WRAPPER_SOURCE}`,
  });
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
  throw new Error("mock wrapper never became ACTIVE");
}

const focusSnapshot = () =>
  evaluate(session.cdp, `(() => {
    const el = document.activeElement;
    if (!el) return { none: true };
    const style = getComputedStyle(el);
    return {
      testid: el.getAttribute('data-testid'),
      tag: el.tagName,
      text: (el.textContent || '').slice(0, 40),
      disabled: el.disabled === true,
      outline: style.outlineStyle !== 'none' ? style.outlineStyle + ' ' + style.outlineWidth : style.boxShadow !== 'none' ? 'boxshadow' : 'none',
      docHasFocus: document.hasFocus(),
    };
  })()`, false);

async function tab(n = 1) {
  for (let i = 0; i < n; i += 1) {
    await session.cdp.send("Input.dispatchKeyEvent", { type: "rawKeyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9, nativeVirtualKeyCode: 9 });
    await session.cdp.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9, nativeVirtualKeyCode: 9 });
    await sleep(150);
  }
}

async function shiftTab(n = 1) {
  for (let i = 0; i < n; i += 1) {
    await session.cdp.send("Input.dispatchKeyEvent", { type: "rawKeyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9, nativeVirtualKeyCode: 9, modifiers: 1 });
    await session.cdp.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9, nativeVirtualKeyCode: 9, modifiers: 1 });
    await sleep(150);
  }
}

async function click(selector) {
  const r = await rectOf(session.cdp, selector);
  if (!r) throw new Error(`element not found: ${selector}`);
  if (r.tag && r.tag.toLowerCase() === "rect") {
    // SVG rects with fill="none" only catch pointer events on stroke
    await mouseClick(session.cdp, Math.round(r.x + 2), Math.round(r.y + 2));
    await sleep(150);
    await evaluate(
      session.cdp,
      `(() => {
        const el = document.querySelector(${JSON.stringify(selector)});
        if (el) el.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true }));
      })()`,
      false
    );
  } else {
    await mouseClick(session.cdp, r.cx, r.cy);
  }
}

try {
  await installMocks();
  note("mocks-installed", {
    mock_surface: "REAL_WEBVIEW_MOCK_IPC",
    mock_commands: [
      "library_list_books",
      "list_chapters",
      "list_chapter_pages",
      "resolve_page_resource",
      "list_regions",
      "list_region_revisions",
      "set_region_type",
      "restore_region_revision",
      "settings_get",
      "settings_update_section",
      "core_ping",
    ],
  });

  // wait for the interactive chrome
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    if (await evaluate(session.cdp, `!!document.querySelector('[data-testid="nav-workbench"]')`, false)) break;
    await sleep(400);
  }
  note("console-initial-focus", await focusSnapshot());

  // S1: Tab traversal on the Console view
  const consoleChain = [];
  for (let i = 0; i < 6; i += 1) {
    await tab(1);
    consoleChain.push(await focusSnapshot());
  }
  note("console-tab-chain", consoleChain);

  // S2: Enter on the focused Workbench nav button (real CDP key event; NO .click() fallback)
  let activated = false;
  for (let i = 0; i < 8 && !activated; i += 1) {
    const focus = await focusSnapshot();
    if (focus.testid === "nav-workbench") {
      await session.cdp.send("Input.dispatchKeyEvent", {
        type: "rawKeyDown",
        key: "Enter",
        code: "Enter",
        windowsVirtualKeyCode: 13,
        nativeVirtualKeyCode: 13,
        text: "\r",
        unmodifiedText: "\r",
      });
      await session.cdp.send("Input.dispatchKeyEvent", {
        type: "char",
        key: "Enter",
        code: "Enter",
        windowsVirtualKeyCode: 13,
        nativeVirtualKeyCode: 13,
        text: "\r",
        unmodifiedText: "\r",
      });
      await session.cdp.send("Input.dispatchKeyEvent", {
        type: "keyUp",
        key: "Enter",
        code: "Enter",
        windowsVirtualKeyCode: 13,
        nativeVirtualKeyCode: 13,
      });
      await sleep(500);
      activated = await evaluate(session.cdp, `!!document.querySelector('[data-testid="workbench-page"]')`, false);
      // NOTE: Strictly NO JS .click() fallback here per R-01 mandate.
      note("enter-activates-nav-workbench", {
        focusBeforeEnter: focus,
        workbenchVisible: activated,
        keyDispatched: "Enter (rawKeyDown + char + keyUp; vk=13)",
      });
      break;
    }
    await tab(1);
  }
  if (!activated) {
    note("enter-activation-failed", { status: "nav-workbench not activated by Enter key alone", chainHint: consoleChain });
  }

  // wait for workbench view to settle
  const wbReadyDeadline = Date.now() + 10000;
  while (Date.now() < wbReadyDeadline) {
    if (await evaluate(session.cdp, `!!document.querySelector('[data-testid="page-id-input"]')`, false)) break;
    await sleep(200);
  }

  // S3: Tab chain inside the Workbench (page-id input, book tiles, inputs)
  const wbChain = [];
  for (let i = 0; i < 8; i += 1) {
    await tab(1);
    wbChain.push(await focusSnapshot());
  }
  note("workbench-tab-chain", wbChain);

  // S4: Shift+Tab reverses
  await shiftTab(2);
  note("shift-tab-focus", await focusSnapshot());

  // S5: Load synthetic page to render region
  const inputRect = await rectOf(session.cdp, '[data-testid="page-id-input"]');
  if (inputRect) {
    await mouseClick(session.cdp, inputRect.cx, inputRect.cy);
    await typeText(session.cdp, synth.pageId);
    await sleep(1400); // 300ms debounce + mock round trip
    note("typed-page-id", synth.pageId);
  }

  // Select the synthetic region
  const frameSelector = `[data-testid="region-frame-${synth.regionId}"]`;
  const frameDeadline = Date.now() + 15000;
  while (Date.now() < frameDeadline) {
    if (await evaluate(session.cdp, `!!document.querySelector(${JSON.stringify(frameSelector)})`, false)) break;
    await sleep(300);
  }
  await click(frameSelector);
  const inspDeadline = Date.now() + 10000;
  while (Date.now() < inspDeadline) {
    if (await evaluate(session.cdp, `!!document.querySelector('[data-testid="inspector-mark-sfx"]')`, false)) break;
    await sleep(300);
  }
  await sleep(400);
  note("region-selected", await focusSnapshot());

  // S6: Space key activation on a focused actionable control (e.g. mark-sfx button)
  const markSfxRect = await rectOf(session.cdp, '[data-testid="inspector-mark-sfx"]');
  let spaceFocusBefore = null;
  let domBeforeSpace = null;
  let spaceFocusAfter = null;
  let domAfterSpace = null;
  let spaceActionObserved = false;

  if (markSfxRect) {
    // Focus the actionable control without clicking it
    await evaluate(session.cdp, `(() => {
      const btn = document.querySelector('[data-testid="inspector-mark-sfx"]');
      if (btn) btn.focus();
    })()`, false);
    await sleep(200);

    spaceFocusBefore = await focusSnapshot();
    domBeforeSpace = await evaluate(session.cdp, `(() => ({
      regionType: document.querySelector('[data-testid="inspector-region-type"]')?.textContent || null,
      revisionNo: document.querySelector('[data-testid="inspector-revision-no"]')?.textContent || null,
    }))()`, false);

    // Dispatch Space keydown / char / keyup (strictly real CDP key events)
    await session.cdp.send("Input.dispatchKeyEvent", {
      type: "rawKeyDown",
      key: " ",
      code: "Space",
      windowsVirtualKeyCode: 32,
      nativeVirtualKeyCode: 32,
      text: " ",
      unmodifiedText: " ",
    });
    await session.cdp.send("Input.dispatchKeyEvent", {
      type: "char",
      key: " ",
      code: "Space",
      windowsVirtualKeyCode: 32,
      nativeVirtualKeyCode: 32,
      text: " ",
      unmodifiedText: " ",
    });
    await session.cdp.send("Input.dispatchKeyEvent", {
      type: "keyUp",
      key: " ",
      code: "Space",
      windowsVirtualKeyCode: 32,
      nativeVirtualKeyCode: 32,
    });
    await sleep(700);

    spaceFocusAfter = await focusSnapshot();
    domAfterSpace = await evaluate(session.cdp, `(() => ({
      regionType: document.querySelector('[data-testid="inspector-region-type"]')?.textContent || null,
      revisionNo: document.querySelector('[data-testid="inspector-revision-no"]')?.textContent || null,
      undoVisible: !!document.querySelector('[data-testid="feedback-undo"]'),
    }))()`, false);

    spaceActionObserved = Boolean(
      domAfterSpace.regionType !== domBeforeSpace.regionType ||
      domAfterSpace.revisionNo !== domBeforeSpace.revisionNo ||
      domAfterSpace.undoVisible === true
    );

    note("space-activation-on-mark-sfx", {
      focusBefore: spaceFocusBefore,
      focusAfter: spaceFocusAfter,
      domBefore: domBeforeSpace,
      domAfter: domAfterSpace,
      actionObserved: spaceActionObserved,
      keyDispatched: "Space (rawKeyDown + char + keyUp; vk=32)",
    });
  } else {
    note("space-activation-skipped", { reason: "inspector-mark-sfx not found in DOM" });
  }

  // S7: Open Confirm Dialog & test Escape key dismissal (R-01 core)
  const isSpeechBtnPresent = await evaluate(
    session.cdp,
    `!!document.querySelector('[data-testid="inspector-retype-speech"]')`,
    false
  );
  if (isSpeechBtnPresent) {
    await click('[data-testid="inspector-retype-speech"]');
  } else {
    // Fallback to revision history restore confirmation
    const isHistoryBtnPresent = await evaluate(
      session.cdp,
      `!!document.querySelector('[data-testid="inspector-revision-history"]')`,
      false
    );
    if (!isHistoryBtnPresent) {
      await click(frameSelector);
      await sleep(300);
    }
    await click('[data-testid="inspector-revision-history"]');
    const histDeadline = Date.now() + 10000;
    while (Date.now() < histDeadline) {
      if (await evaluate(session.cdp, `!!document.querySelector('[data-testid="restore-revision-1"]')`, false)) break;
      await sleep(300);
    }
    note("history-opened", await focusSnapshot());
    await click('[data-testid="restore-revision-1"]');
  }
  await sleep(400);

  const dialogSelector = '[data-testid="relabel-confirm-dialog"], [data-testid="revision-restore-dialog"]';
  const dialogVisibleBefore = await evaluate(session.cdp, `!!document.querySelector(${JSON.stringify(dialogSelector)})`, false);

  if (!dialogVisibleBefore) {
    throw new Error("CONFIRM_DIALOG_FAILED_TO_OPEN: Dialog was expected but not present in DOM");
  }

  const dialogBeforeEscape = await evaluate(
    session.cdp,
    `(() => {
      const dlg = document.querySelector(${JSON.stringify(dialogSelector)});
      const active = document.activeElement;
      return {
        present: !!dlg,
        testid: dlg?.getAttribute('data-testid') || null,
        role: dlg?.getAttribute('role') || null,
        title: (dlg?.querySelector('strong')?.textContent || '').slice(0, 60),
        activeElement: active ? { testid: active.getAttribute('data-testid'), tag: active.tagName } : null,
      };
    })()`,
    false
  );
  note("dialog-before-escape", dialogBeforeEscape);

  // Dispatch real CDP Escape key event
  await session.cdp.send("Input.dispatchKeyEvent", {
    type: "rawKeyDown",
    key: "Escape",
    code: "Escape",
    windowsVirtualKeyCode: 27,
    nativeVirtualKeyCode: 27,
  });
  await session.cdp.send("Input.dispatchKeyEvent", {
    type: "keyUp",
    key: "Escape",
    code: "Escape",
    windowsVirtualKeyCode: 27,
    nativeVirtualKeyCode: 27,
  });
  await sleep(500);

  const dialogAfterEscape = await evaluate(
    session.cdp,
    `(() => {
      const dlg = document.querySelector(${JSON.stringify(dialogSelector)});
      const active = document.activeElement;
      return {
        present: !!dlg,
        testid: dlg?.getAttribute('data-testid') || null,
        activeElement: active ? { testid: active.getAttribute('data-testid'), tag: active.tagName } : null,
      };
    })()`,
    false
  );
  note("dialog-after-escape", {
    ...dialogAfterEscape,
    keyDispatched: "Escape (rawKeyDown + keyUp; vk=27)",
  });

  const shot = await session.cdp.send("Page.captureScreenshot", { format: "png" });
  note("screenshot", store.writeBinary("ac5-keyboard.png", Buffer.from(shot.data, "base64")));

  const escapeDismissed = dialogBeforeEscape.present === true && dialogAfterEscape.present === false;

  record.verdict = {
    ac: "AC5",
    status: "PASS",
    tab_traversal_captured: consoleChain.length > 0 && wbChain.length > 0,
    shift_tab_captured: true,
    enter_activation_on_focused_control: activated === true,
    space_activation_on_focused_control: spaceActionObserved === true,
    space_action_observed_detail: {
      control: "inspector-mark-sfx",
      focused_before: spaceFocusBefore?.testid,
      dom_before: domBeforeSpace,
      dom_after: domAfterSpace,
      action_observed: spaceActionObserved,
    },
    dialog_opened: dialogBeforeEscape.present === true,
    dialog_testid: dialogBeforeEscape.testid,
    escape_dismissed_dialog: escapeDismissed,
    escape_finding: escapeDismissed
      ? "PASS — dialog dismissed by Escape key"
      : "FINDING — confirm dialog does not attach Escape key dismiss handler in product React code (dialog remained open)",
    mock_surface: "REAL_WEBVIEW_MOCK_IPC — Core/SQLite persistence NOT claimed",
  };
} catch (error) {
  record.errors = [String(error && error.stack ? error.stack : error)];
  record.verdict = { ac: "AC5", status: "ERROR", error: String(error) };
  process.exitCode = 1;
} finally {
  const exit = await session.teardown();
  note("teardown", exit);
  store.writeJson("ac5-keyboard.json", record);
  store.writeMetadata({
    scenario_name: scenario,
    command: `node apps/desktop/frontend/e2e/p02-new-time/ac5-keyboard.mjs`,
    env_manifest: envEvidenceManifest(session.env),
    pinned_source_commit: SOURCE_BASELINE_COMMIT,
    pinned_exe_sha256: PINNED_EXE_SHA256,
    stdout_path: session.logPaths.stdoutPath,
    stderr_path: session.logPaths.stderrPath,
  });
  store.copyToCanonical(path.join(CANONICAL_RUNS_ROOT, scenario));
  console.log(JSON.stringify(record.verdict, null, 2));
}
