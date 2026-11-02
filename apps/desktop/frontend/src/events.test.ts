import { describe, it, expect, vi } from "vitest";
import {
  CORE_EVENT_NAMES,
  listenCoreEvent,
  onTaskFailed,
  onRunPaused,
  onRunCompleted,
  onCurrentPageStepChanged,
  onExportProgressChanged,
  onReadingProgressChanged,
  type ListenFn,
  type TaskFailedPayload,
  type RunPausedPayload,
  type RunCompletedPayload,
  type CurrentPageStepChangedPayload,
  type ExportProgressChangedPayload,
  type ReadingProgressChangedPayload,
} from "./events";

describe("events listener surface (M2-C1 rev 2.4 §6.4)", () => {
  it("exposes the exact 6 frozen event constants with core: prefix", () => {
    expect(CORE_EVENT_NAMES).toEqual({
      TaskFailed: "core:TaskFailed",
      RunPaused: "core:RunPaused",
      RunCompleted: "core:RunCompleted",
      CurrentPageStepChanged: "core:CurrentPageStepChanged",
      ExportProgressChanged: "core:ExportProgressChanged",
      ReadingProgressChanged: "core:ReadingProgressChanged",
    });
  });

  it("subscribes and unpacks payload via listenCoreEvent with custom listener", async () => {
    const unlistenMock = vi.fn();
    let registeredHandler: ((event: { payload: RunCompletedPayload }) => void) | undefined;

    const mockListen: ListenFn = vi.fn(async (event, handler) => {
      expect(event).toBe("core:RunCompleted");
      registeredHandler = handler as (event: { payload: RunCompletedPayload }) => void;
      return unlistenMock;
    });

    const received: RunCompletedPayload[] = [];
    const unlisten = await listenCoreEvent(
      "core:RunCompleted",
      (payload) => received.push(payload),
      mockListen
    );

    expect(mockListen).toHaveBeenCalledTimes(1);
    expect(registeredHandler).toBeDefined();

    registeredHandler!({ payload: { run_id: "run-42", status: "completed" } });
    expect(received).toEqual([{ run_id: "run-42", status: "completed" }]);

    unlisten();
    expect(unlistenMock).toHaveBeenCalledTimes(1);
  });

  it("dispatches typed helpers for all 6 frozen events", async () => {
    const listeners = new Map<string, (e: { payload: unknown }) => void>();
    const mockListen: ListenFn = vi.fn(async (event, handler) => {
      listeners.set(event, handler as (e: { payload: unknown }) => void);
      return () => {
        listeners.delete(event);
      };
    });

    // 1. TaskFailed
    const taskFailedCb = vi.fn();
    const unlisten1 = await onTaskFailed(taskFailedCb, mockListen);
    const taskFailedData: TaskFailedPayload = {
      run_id: "r1",
      task_id: "t1",
      page_id: "p1",
      error_code: "OCR_TIMEOUT",
    };
    listeners.get("core:TaskFailed")!({ payload: taskFailedData });
    expect(taskFailedCb).toHaveBeenCalledWith(taskFailedData);

    // 2. RunPaused
    const runPausedCb = vi.fn();
    const unlisten2 = await onRunPaused(runPausedCb, mockListen);
    const runPausedData: RunPausedPayload = { run_id: "r1", status: "paused" };
    listeners.get("core:RunPaused")!({ payload: runPausedData });
    expect(runPausedCb).toHaveBeenCalledWith(runPausedData);

    // 3. RunCompleted
    const runCompletedCb = vi.fn();
    const unlisten3 = await onRunCompleted(runCompletedCb, mockListen);
    const runCompletedData: RunCompletedPayload = { run_id: "r1", status: "completed" };
    listeners.get("core:RunCompleted")!({ payload: runCompletedData });
    expect(runCompletedCb).toHaveBeenCalledWith(runCompletedData);

    // 4. CurrentPageStepChanged
    const stepCb = vi.fn();
    const unlisten4 = await onCurrentPageStepChanged(stepCb, mockListen);
    const stepData: CurrentPageStepChangedPayload = {
      run_id: "r1",
      current_page_id: "p1",
      current_step_type: "translating",
    };
    listeners.get("core:CurrentPageStepChanged")!({ payload: stepData });
    expect(stepCb).toHaveBeenCalledWith(stepData);

    // 5. ExportProgressChanged
    const exportCb = vi.fn();
    const unlisten5 = await onExportProgressChanged(exportCb, mockListen);
    const exportData: ExportProgressChangedPayload = {
      export_id: "exp-1",
      status: "in_progress",
      completed_pages: 5,
      total_pages: 10,
    };
    listeners.get("core:ExportProgressChanged")!({ payload: exportData });
    expect(exportCb).toHaveBeenCalledWith(exportData);

    // 6. ReadingProgressChanged
    const readingCb = vi.fn();
    const unlisten6 = await onReadingProgressChanged(readingCb, mockListen);
    const readingData: ReadingProgressChangedPayload = {
      book_id: "b1",
      chapter_id: "c1",
      mode: "original",
    };
    listeners.get("core:ReadingProgressChanged")!({ payload: readingData });
    expect(readingCb).toHaveBeenCalledWith(readingData);

    // Clean up
    unlisten1();
    unlisten2();
    unlisten3();
    unlisten4();
    unlisten5();
    unlisten6();
    expect(listeners.size).toBe(0);
  });

  it("uses window.__TAURI__.event.listen when available", async () => {
    const unlistenMock = vi.fn();
    const globalListen = vi.fn(async () => unlistenMock);
    const originalWindow = globalThis.window;

    try {
      (globalThis as unknown as { window: unknown }).window = {
        __TAURI__: {
          event: {
            listen: globalListen,
          },
        },
      };

      const cb = vi.fn();
      const unlisten = await onRunCompleted(cb);
      expect(globalListen).toHaveBeenCalledWith("core:RunCompleted", expect.any(Function));
      unlisten();
      expect(unlistenMock).toHaveBeenCalledTimes(1);
    } finally {
      (globalThis as unknown as { window: unknown }).window = originalWindow;
    }
  });
});
