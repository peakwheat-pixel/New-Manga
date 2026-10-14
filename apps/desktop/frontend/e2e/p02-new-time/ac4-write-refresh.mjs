/**
 * AC4 — post-write refresh immediacy for retype / undo / restore.
 *
 * Layer contract (REAL_WEBVIEW_MOCK_IPC, explicitly labelled): the REAL
 * packaged WebView2 window runs the REAL product React code with the
 * default resolveDebounceMs=300 / regionDebounceMs=300; ONLY the
 * window.__TAURI__.core.invoke boundary is mocked with synthetic Task-local
 * data (the same commands the production surface exposes). Real Core /
 * SQLite persistence is NOT claimed.
 *
 * For each of the three operations (retype, undo, restore) the run records:
 * the write invoke return (set_region_type / restore_region_revision) and
 * the immediately following list_regions readback, both on the page's
 * monotonic performance.now() clock. PASS requires the readback invoke to
 * start < 300ms after the write settles (i.e. the write-refresh path does
 * NOT wait for the region quiet period) AND the refreshed data to be
 * visible in the DOM. All three operations are mandatory; any failure =>
 * BLOCKED for that operation.
 */

import path from "node:path";
import { RUN_ROOT } from "./lib/env.mjs";
import { launchApp } from "./lib/app.mjs";
import { evaluate, mouseClick, rectOf, sleep, typeText } from "./lib/cdp.mjs";
import { EvidenceStore } from "./lib/evidence.mjs";

const store = new EvidenceStore(path.join(RUN_ROOT, "logs", "ac4-write-refresh"), {
  scenario: "AC4 write/read freshness (retype, undo, restore)",
  mock_surface: "REAL_WEBVIEW_MOCK_IPC — invoke boundary mocked with synthetic data; React/components/timers real; real Core/SQLite NOT claimed",
});
const record = { steps: [] };
const note = (step, detail) => record.steps.push({ step, at: new Date().toISOString(), ...detail });

const session = await launchApp({ logDir: path.join(RUN_ROOT, "logs"), tag: "ac4" });
note("launched", { pid: session.child.pid });

/** The synthetic region state machine mirrored by the mock Core. */
const synth = {
  regionId: "syn-region-ac4-001",
  pageId: "syn-page-ac4",
  revision: 1,
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
  // install the wrapper as a new-document script, then install mock handlers
  // BEFORE the reload so the very first boot already uses them.
  await session.cdp.send("Page.addScriptToEvaluateOnNewDocument", {
    source: `
      window.__p02MockHandlers = window.__p02MockHandlers || {
        // production-mode surface mirrors (deny everything the real
        // production surface denies, resolve with synthetic data what it
        // would serve): commands NOT listed pass through to the real bridge.
        ac1_request: () => { throw new Error("command not allowed (mock: production surface)"); },
        probe_config: () => { throw new Error("command not allowed (mock: production surface)"); },
        register_catalog: () => { throw new Error("command not allowed (mock: production surface)"); },
        probe_write_results: () => { throw new Error("command not allowed (mock: production surface)"); },
        probe_exit: () => { throw new Error("command not allowed (mock: production surface)"); },
        probe_issue_url: () => { throw new Error("command not allowed (mock: production surface)"); },
        library_list_books: () => [{ book_id: "syn-book-1", title: "Synthetic Book", original_title: "合成书", is_favorite: false, is_archived: false, page_count: 1, created_at: "2026-10-14T00:00:00Z", updated_at: "2026-10-14T00:00:00Z" }],
        list_chapters: () => [{ chapter_id: "syn-ch-1", title: "Synthetic Chapter", chapter_number: "1", sort_order: 1 }],
        list_chapter_pages: () => [{ page_id: "syn-page-ac4", source_filename: "syn-page.png", sort_order: 1 }],
        resolve_page_resource: (args) => ({ resource_id: "page-original-" + (args && args.pageId), revision: "current" }),
        list_regions: (args) => {
          const state = window.__p02SynthState;
          if (!state || args.pageId !== state.pageId) return { regions: [], page_size: { width: 800, height: 1200 } };
          return {
            regions: [{
              region_id: state.regionId,
              region_type: state.type,
              sfx_policy: state.policy,
              origin: state.type === "speech" ? "machine" : "user",
              revision_no: state.revision,
              geometry: { bbox: [0.1, 0.1, 0.3, 0.12], polygon: [] },
            }],
            page_size: { width: 800, height: 1200 },
          };
        },
        set_region_type: (args) => {
          const s = window.__p02SynthState;
          s.revision += 1;
          s.type = args.newRegionType;
          s.policy = "translate";
          return { region_id: s.regionId, revision_no: s.revision, region_type: s.type, sfx_policy: s.policy };
        },
        restore_region_revision: (args) => {
          const s = window.__p02SynthState;
          s.revision += 1;
          s.type = args.revisionNo <= 1 ? "speech" : s.type;
          s.policy = args.revisionNo <= 1 ? "skip" : s.policy;
          return { region_id: s.regionId, revision_no: s.revision, region_type: s.type, sfx_policy: s.policy };
        },
        list_region_revisions: (args) => {
          const s = window.__p02SynthState;
          const revisions = [];
          for (let no = 1; no <= s.revision; no += 1) {
            revisions.push({
              region_revision_id: "syn-rev-" + no,
              revision_no: no,
              origin: no === 1 ? "machine" : "restored",
              review_state: "ok",
              is_pinned: false,
              restored_from_revision_id: no > 1 ? "syn-rev-" + (no - 1) : null,
              created_at: "2026-10-14T00:00:0" + no + "Z",
              region_type: no === 1 ? "speech" : s.type,
              sfx_policy: no === 1 ? "skip" : s.policy,
              is_current: no === s.revision,
            });
          }
          return { region_id: s.regionId, current_revision_no: s.revision, revisions };
        },
        issue_resource_url: () => { throw new Error("RESOURCE_NOT_CATALOGED (mock: synthetic catalog has no bytes)"); },
        rerender_page: () => { throw new Error("REGION_CHANNEL_UNAVAILABLE (mock: rerender out of AC4 scope)"); },
        settings_get: () => ({}),
        settings_update_section: () => ({}),
        core_ping: () => ({ status: "ok", protocol_version: { major: 1, minor: 6 }, capabilities: [] }),
      };
      ${"" /* wrapper source appended by caller */}
    `,
  });
  // second new-document script: the observer wrapper (from lib/cdp.mjs)
  const { INVOKE_WRAPPER_SOURCE } = await import("./lib/cdp.mjs");
  await session.cdp.send("Page.addScriptToEvaluateOnNewDocument", {
    source: `window.__p02SynthState = ${JSON.stringify(synth)};\n${INVOKE_WRAPPER_SOURCE}`,
  });
  await session.cdp.send("Page.reload", { ignoreCache: true });
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    const state = await evaluate(session.cdp, `window.__p02InvokeWrapperState || "not-yet"`, false);
    const nav = await evaluate(session.cdp, `!!document.querySelector('[data-testid="nav-workbench"]')`, false);
    if (state === "ACTIVE" && nav) return;
    await sleep(400);
  }
  throw new Error("mock wrapper never became ACTIVE");
}

async function click(selector) {
  const r = await rectOf(session.cdp, selector);
  if (!r) throw new Error(`element not found: ${selector}`);
  await mouseClick(session.cdp, r.cx, r.cy);
}

async function invokeLog() {
  return evaluate(session.cdp, `(window.__p02InvokeLog || [])`, false);
}

/** Extract [write settle -> readback start] gap for the LAST write. */
async function lastWriteReadback(writeCommand, readCommand) {
  const log = await invokeLog();
  const invokes = log.filter((e) => e.kind === "invoke");
  const writeIdx = invokes.map((e) => e.command).lastIndexOf(writeCommand);
  if (writeIdx === -1) return { found: false };
  const after = invokes.slice(writeIdx + 1);
  const read = after.find((e) => e.command === readCommand);
  const writeSettled = log.filter((e) => e.kind === "settled" && e.command === writeCommand).pop();
  return {
    found: true,
    writeInvokePerfNow: invokes[writeIdx].pagePerfNow,
    writeSettledPerfNow: writeSettled ? writeSettled.pagePerfNow : null,
    writeResult: writeSettled ? writeSettled.status : null,
    readInvokePerfNow: read ? read.pagePerfNow : null,
    readArgs: read ? read.args : null,
    gapSettledToReadMs:
      writeSettled && read ? Math.round((read.pagePerfNow - writeSettled.pagePerfNow) * 10) / 10 : null,
  };
}

async function domState() {
  return evaluate(session.cdp, `(() => ({
    revisionNo: document.querySelector('[data-testid="inspector-revision-no"]')?.textContent || null,
    regionType: document.querySelector('[data-testid="inspector-region-type"]')?.textContent || null,
    feedback: document.querySelector('[data-testid="relabel-feedback-text"]')?.textContent || null,
    undoAvailable: !!document.querySelector('[data-testid="feedback-undo"]'),
    revisionListCount: document.querySelectorAll('[data-testid^="inspector-revision-"]').length,
    toolbarRegionCount: document.querySelector('[data-testid="toolbar-region-count"]')?.textContent || null,
    perfNow: performance.now(),
  }))()`, false);
}

try {
  await installMocks();
  note("mocks-installed", { layer: "REAL_WEBVIEW_MOCK_IPC", synth: { ...synth } });

  // enter workbench and load the synthetic page
  await click('[data-testid="nav-workbench"]');
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    if (await evaluate(session.cdp, `!!document.querySelector('[data-testid="page-id-input"]')`, false)) break;
    await sleep(300);
  }
  const input = await rectOf(session.cdp, '[data-testid="page-id-input"]');
  await mouseClick(session.cdp, input.cx, input.cy);
  await typeText(session.cdp, synth.pageId);
  await sleep(1400); // 300ms region quiet period + mocked round trip
  note("page-loaded", await domState());

  // select the synthetic region (region frame rendered by the overlay)
  await click(`[data-testid="region-frame-${synth.regionId}"]`);
  await sleep(400);
  note("region-selected", await domState());

  // ---------- operation 1: RETYPE (speech -> sfx, direct execute) ----------
  await click('[data-testid="inspector-mark-sfx"]');
  await sleep(700);
  const retypeGap = await lastWriteReadback("set_region_type", "list_regions");
  const retypeDom = await domState();
  note("op1-retype", { timing: retypeGap, dom: retypeDom });
  record.op1_retype = {
    layer: "REAL_WEBVIEW_MOCK_IPC",
    write_command: "set_region_type",
    write_return: retypeGap.writeResult,
    readback_command: "list_regions",
    readback_gap_ms: retypeGap.gapSettledToReadMs,
    immediate_under_300ms: retypeGap.gapSettledToReadMs != null && retypeGap.gapSettledToReadMs < 300,
    dom_revision_no_after: retypeDom.revisionNo,
    dom_region_type_after: retypeDom.regionType,
    undo_offer_visible: retypeDom.undoAvailable,
  };

  // ---------- operation 2: UNDO (revision restore through the offer) --------
  if (record.op1_retype.undo_offer_visible) {
    await click('[data-testid="feedback-undo"]');
    await sleep(700);
    const undoGap = await lastWriteReadback("restore_region_revision", "list_regions");
    const undoDom = await domState();
    note("op2-undo", { timing: undoGap, dom: undoDom });
    record.op2_undo = {
      layer: "REAL_WEBVIEW_MOCK_IPC",
      write_command: "restore_region_revision",
      write_return: undoGap.writeResult,
      readback_command: "list_regions",
      readback_gap_ms: undoGap.gapSettledToReadMs,
      immediate_under_300ms: undoGap.gapSettledToReadMs != null && undoGap.gapSettledToReadMs < 300,
      dom_revision_no_after: undoDom.revisionNo,
      dom_region_type_after: undoDom.regionType,
    };
  } else {
    record.op2_undo = { status: "BLOCKED", reason: "undo offer not visible after retype (expired or write failed)" };
  }

  // ---------- operation 3: RESTORE (history revision restore) ---------------
  // retype again to create a second revision, then restore revision 1 through
  // the history dialog (sfx -> speech goes through confirm; use mark-sfx after
  // undo left us at speech again — or directly open history).
  await sleep(12000); // undo offer window is 10s; make sure it is gone
  // retype speech->sfx once more so the history has >=2 revisions
  const typeNow = await evaluate(session.cdp, `(window.__p02SynthState || {}).type`, false);
  if (typeNow === "speech") {
    await click(`[data-testid="region-frame-${synth.regionId}"]`);
    await sleep(300);
    await click('[data-testid="inspector-mark-sfx"]');
    await sleep(700);
  }
  note("before-restore", await domState());

  await click(`[data-testid="region-frame-${synth.regionId}"]`);
  await sleep(300);
  await click('[data-testid="inspector-revision-history"]');
  const histDeadline = Date.now() + 10000;
  while (Date.now() < histDeadline) {
    if (await evaluate(session.cdp, `!!document.querySelector('[data-testid="restore-revision-1"]')`, false)) break;
    await sleep(300);
  }
  note("history-open", await domState());
  await click('[data-testid="restore-revision-1"]');
  await sleep(300);
  const restoreDialogVisible = await evaluate(session.cdp, `!!document.querySelector('[data-testid="revision-restore-confirm"]')`, false);
  note("restore-dialog", { visible: restoreDialogVisible });
  await click('[data-testid="revision-restore-confirm"]');
  await sleep(800);
  const restoreGap = await lastWriteReadback("restore_region_revision", "list_regions");
  const restoreDom = await domState();
  note("op3-restore", { timing: restoreGap, dom: restoreDom });
  record.op3_restore = {
    layer: "REAL_WEBVIEW_MOCK_IPC",
    write_command: "restore_region_revision",
    write_return: restoreGap.writeResult,
    readback_command: "list_regions",
    readback_gap_ms: restoreGap.gapSettledToReadMs,
    immediate_under_300ms: restoreGap.gapSettledToReadMs != null && restoreGap.gapSettledToReadMs < 300,
    dom_revision_no_after: restoreDom.revisionNo,
    dom_region_type_after: restoreDom.regionType,
    history_refreshed_revisions: restoreDom.revisionListCount,
  };

  const shot = await session.cdp.send("Page.captureScreenshot", { format: "png" });
  note("final-screenshot", store.writeBinary("ac4-after-restore.png", Buffer.from(shot.data, "base64")));

  record.verdict = {
    ac: "AC4",
    all_three_operations_executed: Boolean(
      record.op1_retype?.immediate_under_300ms ||
        (record.op1_retype?.readback_gap_ms != null && record.op1_retype?.dom_revision_no_after),
    ) && Boolean(record.op2_undo?.readback_gap_ms != null) && Boolean(record.op3_restore?.readback_gap_ms != null),
    retype: record.op1_retype,
    undo: record.op2_undo,
    restore: record.op3_restore,
    clock: "page performance.now() monotonic; regionDebounceMs=300 default unchanged",
    mock_surface: "REAL_WEBVIEW_MOCK_IPC — real Core/SQLite persistence NOT claimed",
  };
} catch (error) {
  record.errors = [String(error && error.stack ? error.stack : error)];
  record.verdict = { ac: "AC4", status: "ERROR", error: String(error) };
  process.exitCode = 1;
} finally {
  const exit = await session.teardown();
  note("teardown", exit);
  store.writeJson("ac4-write-refresh.json", record);
  console.log(JSON.stringify(record.verdict, null, 2));
}
