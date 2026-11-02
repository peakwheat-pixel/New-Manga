import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { CacheRevisionPanel } from "./CacheRevisionPanel";
import { SettingsClient, type InvokeFn } from "./client";

/**
 * SETTINGS-OPEN-B-2 §4.3 / AC3+AC4 — cache / Revision cleanup panel:
 * auto-preview on mount ("可清理 N 个文件 / X MB" + pending count), empty
 * cache → "无可清理文件", manual cleanup and pending retry (disabled while a
 * request is in flight and double-submit guarded), removed/failed/skipped
 * counts with failure detail, and the closed §9 error projection for both
 * load and action failures.
 *
 * The outcome tests pin BOTH wire shapes: the frozen B-2 items/counts
 * projection and the Python `CleanupOutcome.to_dict()` mapping form
 * (cleanup.py:92) — the client normalizes either one.
 */

const EMPTY_PREVIEW = { targets: [], total_bytes: 0, pending_cleanups: 0 };
const TWO_FILE_PREVIEW = {
  targets: [
    { relative_path: "cache/webtoon-tiles/a.png", size_bytes: 1048576 },
    { relative_path: "cache/webtoon-tiles/b.png", size_bytes: 524288 },
  ],
  total_bytes: 1572864,
  pending_cleanups: 2,
};

describe("CacheRevisionPanel (SETTINGS-OPEN-B-2 §4.3)", () => {
  let dom: JSDOM;
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    vi.stubGlobal("window", dom.window);
    vi.stubGlobal("document", dom.window.document);
    vi.stubGlobal("navigator", dom.window.navigator);
    vi.stubGlobal("HTMLElement", dom.window.HTMLElement);
    container = dom.window.document.createElement("div");
    dom.window.document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    vi.unstubAllGlobals();
  });

  const q = (selector: string) => container.querySelector(selector) as HTMLElement | null;
  const cleanupButton = () =>
    q('[data-testid="cache-revision-panel-cleanup-btn"]') as HTMLButtonElement;
  const retryButton = () =>
    q('[data-testid="cache-revision-panel-retry-btn"]') as HTMLButtonElement;

  const render = async (invoke: InvokeFn) => {
    await act(async () => {
      root.render(<CacheRevisionPanel client={new SettingsClient(invoke)} />);
    });
  };

  it("shows the loading skeleton while the initial preview is pending", () => {
    const invoke = vi.fn(() => new Promise(() => {}));
    act(() => {
      root.render(<CacheRevisionPanel client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="cache-revision-panel-loading"]')).not.toBeNull();
    expect(cleanupButton()).toBeNull();
    expect(retryButton()).toBeNull();
  });

  it("auto-previews via cleanup_preview (no payload) and renders count / MB / pending", async () => {
    const invoke = vi.fn(async (command: string) => {
      expect(command).toBe("cleanup_preview");
      return TWO_FILE_PREVIEW;
    });
    await render(invoke);

    expect(invoke).toHaveBeenCalledWith("cleanup_preview");
    expect(q('[data-testid="cache-revision-panel-summary"]')?.textContent).toContain(
      "可清理 2 个文件 / 1.5 MB",
    );
    expect(q('[data-testid="cache-revision-panel-pending"]')?.textContent).toContain("挂起项：2 个");
    expect(q('[data-testid="cache-revision-panel-empty"]')).toBeNull();
    // A non-empty preview with pending entries enables both operations.
    expect(cleanupButton().disabled).toBe(false);
    expect(cleanupButton().getAttribute("aria-disabled")).toBe("false");
    expect(retryButton().disabled).toBe(false);
    // Read-only note: retention / automatic cleanup stay closed (§4.3).
    expect(q('[data-testid="cache-revision-panel-policy-note"]')?.textContent).toContain(
      "Revision 保留策略与自动清理未开放",
    );
  });

  it("renders 无可清理文件 and disables both operations for an empty cache", async () => {
    const invoke = vi.fn(async () => EMPTY_PREVIEW);
    await render(invoke);

    expect(q('[data-testid="cache-revision-panel-empty"]')?.textContent).toContain("无可清理文件");
    expect(q('[data-testid="cache-revision-panel-summary"]')?.textContent).toContain(
      "可清理 0 个文件 / 0 B",
    );
    expect(q('[data-testid="cache-revision-panel-pending"]')?.textContent).toContain("挂起项：0 个");
    expect(cleanupButton().disabled).toBe(true);
    expect(retryButton().disabled).toBe(true);
    expect(invoke).not.toHaveBeenCalledWith("cleanup_run");
    expect(invoke).not.toHaveBeenCalledWith("cleanup_retry_pending");
  });

  it("runs cleanup, shows removed/failed/skipped counts, and re-reads the preview", async () => {
    let previewCalls = 0;
    let runCalls = 0;
    const invoke = vi.fn(async (command: string) => {
      if (command === "cleanup_preview") {
        previewCalls += 1;
        return TWO_FILE_PREVIEW;
      }
      if (command === "cleanup_run") {
        runCalls += 1;
        expect(command).toBe("cleanup_run");
        return {
          items: [
            { relative_path: "cache/webtoon-tiles/a.png", status: "ok" },
            { relative_path: "cache/webtoon-tiles/b.png", status: "ok" },
          ],
          removed: 2,
          failed: 0,
          skipped: 0,
        };
      }
      throw new Error(`unexpected command ${command}`);
    });
    await render(invoke);

    await act(async () => {
      cleanupButton().click();
    });

    expect(runCalls).toBe(1);
    expect(invoke).toHaveBeenCalledWith("cleanup_run");
    expect(q('[data-testid="cache-revision-panel-result"]')?.getAttribute("data-operation")).toBe(
      "cleanup",
    );
    expect(q('[data-testid="cache-revision-panel-removed"]')?.textContent).toBe("2");
    expect(q('[data-testid="cache-revision-panel-failed"]')?.textContent).toBe("0");
    expect(q('[data-testid="cache-revision-panel-skipped"]')?.textContent).toBe("0");
    expect(q('[data-testid="cache-revision-panel-result-counts"]')?.textContent).toContain(
      "清理结果：成功 2 个 · 失败 0 个 · 跳过 0 个",
    );
    expect(q('[data-testid="cache-revision-panel-failures"]')).toBeNull();
    // The preview is re-read after a successful run (mount + post-run).
    expect(previewCalls).toBe(2);
  });

  it("renders the failure detail for the ruled wire shape (items as a mapping)", async () => {
    const invoke = vi.fn(async (command: string) => {
      if (command === "cleanup_preview") return TWO_FILE_PREVIEW;
      // task-7 final projection: items is a path → {status, reason} object.
      return {
        items: {
          "cache/webtoon-tiles/a.png": { status: "failed", reason: "文件被占用" },
          "cache/other.png": { status: "skipped", reason: "outside safe cache prefixes" },
          "cache/webtoon-tiles/b.png": { status: "ok", reason: "" },
        },
        removed: 1,
        failed: 1,
        skipped: 1,
      };
    });
    await render(invoke);

    await act(async () => {
      cleanupButton().click();
    });

    expect(q('[data-testid="cache-revision-panel-removed"]')?.textContent).toBe("1");
    expect(q('[data-testid="cache-revision-panel-failed"]')?.textContent).toBe("1");
    expect(q('[data-testid="cache-revision-panel-skipped"]')?.textContent).toBe("1");
    const failures = container.querySelectorAll('[data-testid="cache-revision-panel-failure"]');
    expect(failures).toHaveLength(1);
    expect(q('[data-testid="cache-revision-panel-failure-path"]')?.textContent).toContain(
      "cache/webtoon-tiles/a.png",
    );
    expect(q('[data-testid="cache-revision-panel-failure-detail"]')?.textContent).toContain(
      "文件被占用",
    );
  });

  it("also accepts an items ARRAY projection (forward-compatible) and derives the counts", async () => {
    const invoke = vi.fn(async (command: string) => {
      if (command === "cleanup_preview") return TWO_FILE_PREVIEW;
      return {
        items: [
          { relative_path: "cache/webtoon-tiles/a.png", status: "ok" },
          { relative_path: "cache/webtoon-tiles/b.png", status: "failed", detail: "EBUSY" },
        ],
        removed: 1,
        failed: 1,
        skipped: 0,
      };
    });
    await render(invoke);

    await act(async () => {
      cleanupButton().click();
    });

    expect(q('[data-testid="cache-revision-panel-removed"]')?.textContent).toBe("1");
    expect(q('[data-testid="cache-revision-panel-failed"]')?.textContent).toBe("1");
    expect(q('[data-testid="cache-revision-panel-failure-detail"]')?.textContent).toContain("EBUSY");
  });

  it("accepts the Python CleanupOutcome.to_dict() mapping form and derives the counts", async () => {
    const invoke = vi.fn(async (command: string) => {
      if (command === "cleanup_preview") return TWO_FILE_PREVIEW;
      // cleanup.py:92 — {relative_path: {"status", "reason"}}.
      return {
        "cache/webtoon-tiles/a.png": { status: "ok", reason: "" },
        "cache/webtoon-tiles/b.png": { status: "failed", reason: "EBUSY" },
        "cache/other.png": { status: "skipped", reason: "outside safe cache prefixes" },
      };
    });
    await render(invoke);

    await act(async () => {
      cleanupButton().click();
    });

    expect(q('[data-testid="cache-revision-panel-removed"]')?.textContent).toBe("1");
    expect(q('[data-testid="cache-revision-panel-failed"]')?.textContent).toBe("1");
    expect(q('[data-testid="cache-revision-panel-skipped"]')?.textContent).toBe("1");
    expect(q('[data-testid="cache-revision-panel-failure-detail"]')?.textContent).toContain("EBUSY");
  });

  it("retries the persisted pending ledger via cleanup_retry_pending", async () => {
    const invoke = vi.fn(async (command: string) => {
      if (command === "cleanup_preview") {
        return { targets: [], total_bytes: 0, pending_cleanups: 1 };
      }
      if (command === "cleanup_retry_pending") {
        return {
          items: [{ relative_path: "cache/webtoon-tiles/a.png", status: "ok" }],
          removed: 1,
          failed: 0,
          skipped: 0,
        };
      }
      throw new Error(`unexpected command ${command}`);
    });
    await render(invoke);

    // Nothing cleanable, but one pending entry: only retry is available.
    expect(cleanupButton().disabled).toBe(true);
    expect(retryButton().disabled).toBe(false);
    await act(async () => {
      retryButton().click();
    });

    expect(invoke).toHaveBeenCalledWith("cleanup_retry_pending");
    expect(q('[data-testid="cache-revision-panel-result"]')?.getAttribute("data-operation")).toBe(
      "retry",
    );
    expect(q('[data-testid="cache-revision-panel-result-counts"]')?.textContent).toContain(
      "重试结果：成功 1 个 · 失败 0 个 · 跳过 0 个",
    );
  });

  it("disables both buttons while an operation is in flight and ignores a second click", async () => {
    let resolveRun: ((value: unknown) => void) | undefined;
    let runCalls = 0;
    const invoke = vi.fn((command: string) => {
      if (command === "cleanup_preview") return Promise.resolve(TWO_FILE_PREVIEW);
      if (command === "cleanup_run") {
        runCalls += 1;
        return new Promise((resolve) => {
          resolveRun = resolve;
        });
      }
      return Promise.resolve({});
    });
    await render(invoke);

    await act(async () => {
      cleanupButton().click();
    });
    expect(runCalls).toBe(1);
    expect(cleanupButton().disabled).toBe(true);
    expect(cleanupButton().textContent).toContain("清理中…");
    expect(retryButton().disabled).toBe(true);
    expect(q('[data-testid="cache-revision-panel-busy-state"]')?.textContent).toContain(
      "正在清理缓存",
    );

    // Second click while the request is still in flight is a no-op.
    await act(async () => {
      cleanupButton().click();
    });
    expect(runCalls).toBe(1);

    await act(async () => {
      resolveRun?.({
        items: [{ relative_path: "cache/webtoon-tiles/a.png", status: "ok" }],
        removed: 1,
        failed: 0,
        skipped: 0,
      });
      await Promise.resolve();
    });
    expect(cleanupButton().disabled).toBe(false);
    expect(q('[data-testid="cache-revision-panel-result"]')).not.toBeNull();
  });

  it("a failed operation shows the closed §9 projection and allows a real retry", async () => {
    let runCalls = 0;
    const invoke = vi.fn(async (command: string) => {
      if (command === "cleanup_preview") return TWO_FILE_PREVIEW;
      if (command === "cleanup_run") {
        runCalls += 1;
        if (runCalls === 1) {
          throw { code: "CORE_UNAVAILABLE" };
        }
        return {
          items: [{ relative_path: "cache/webtoon-tiles/a.png", status: "ok" }],
          removed: 1,
          failed: 0,
          skipped: 0,
        };
      }
      throw new Error(`unexpected command ${command}`);
    });
    await render(invoke);

    await act(async () => {
      cleanupButton().click();
    });

    const bar = q('[data-testid="cache-revision-panel-action-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-message-key")).toBe("SETTINGS_UNAVAILABLE");
    expect(container.textContent).not.toContain("CORE_UNAVAILABLE");
    // The buttons come back; the error bar offers the retry action.
    expect(cleanupButton().disabled).toBe(false);
    await act(async () => {
      (q('[data-testid="cache-revision-panel-action-error-retry"]') as HTMLButtonElement).click();
    });
    expect(runCalls).toBe(2);
    expect(q('[data-testid="cache-revision-panel-action-error"]')).toBeNull();
    expect(q('[data-testid="cache-revision-panel-result"]')).not.toBeNull();
  });

  it("a failed preview shows the safe error and retry re-reads the preview", async () => {
    let previewCalls = 0;
    const invoke = vi.fn(async (command: string) => {
      if (command === "cleanup_preview") {
        previewCalls += 1;
        if (previewCalls === 1) {
          throw "CORE_UNAVAILABLE";
        }
        return TWO_FILE_PREVIEW;
      }
      throw new Error(`unexpected command ${command}`);
    });
    await render(invoke);

    const bar = q('[data-testid="cache-revision-panel-load-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-message-key")).toBe("SETTINGS_UNAVAILABLE");
    expect(container.textContent).not.toContain("CORE_UNAVAILABLE");
    expect(cleanupButton()).toBeNull();
    expect(q('[data-testid="cache-revision-panel-load-error-retry"]')).not.toBeNull();

    await act(async () => {
      (q('[data-testid="cache-revision-panel-load-error-retry"]') as HTMLButtonElement).click();
    });
    expect(previewCalls).toBe(2);
    expect(q('[data-testid="cache-revision-panel-summary"]')?.textContent).toContain(
      "可清理 2 个文件 / 1.5 MB",
    );
  });
});
