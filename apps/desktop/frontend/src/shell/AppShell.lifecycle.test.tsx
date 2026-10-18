import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AppShell } from "./AppShell";
import type { LifecycleStatusPayload } from "../events";

describe("AppShell - P20-ISOLATION-1 sidecar fault indicator and state preservation", () => {
  let dom: JSDOM;
  let container: HTMLDivElement;
  let root: ReturnType<typeof createRoot>;
  let lifecycleHandler: ((event: { payload: LifecycleStatusPayload }) => void) | undefined;

  beforeEach(() => {
    dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
    vi.stubGlobal("window", dom.window);
    vi.stubGlobal("document", dom.window.document);
    vi.stubGlobal("navigator", dom.window.navigator);
    vi.stubGlobal("HTMLElement", dom.window.HTMLElement);

    lifecycleHandler = undefined;
    (dom.window as unknown as { __TAURI__?: unknown }).__TAURI__ = {
      event: {
        listen: vi.fn(async (event: string, handler: (e: { payload: LifecycleStatusPayload }) => void) => {
          if (event === "core:lifecycle_status") {
            lifecycleHandler = handler;
          }
          return () => {};
        }),
      },
    };

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

  it("AC1: displays user-visible error banner with expected keywords when restarting", async () => {
    const mockInvoke = vi.fn().mockImplementation(async (cmd: string) => {
      if (cmd === "library_list_books") return [];
      return null;
    });

    await act(async () => {
      root.render(<AppShell invoke={mockInvoke} />);
    });

    // Initially healthy - no banner
    expect(container.querySelector('[data-testid="core-status-banner"]')).toBeNull();

    // Sidecar crash -> "restarting" event emitted by Tauri host
    await act(async () => {
      lifecycleHandler?.({
        payload: {
          status: "restarting",
          message: "后端服务异常，正在尝试热重启...",
        },
      });
    });

    const banner = container.querySelector('[data-testid="core-status-banner"]');
    expect(banner).not.toBeNull();
    const bannerText = banner?.textContent || "";

    // Check UIA keywords from AC1: 异常|错误|失败|重启|后端|Core
    expect(bannerText).toMatch(/后端/);
    expect(bannerText).toMatch(/异常/);
    expect(bannerText).toMatch(/重启/);
    expect(bannerText).toContain("后端服务异常，正在尝试热重启...");
  });

  it("AC2: displays recovery notification on recovered, and fatal degraded message on permanent failure", async () => {
    const mockInvoke = vi.fn().mockResolvedValue([]);

    await act(async () => {
      root.render(<AppShell invoke={mockInvoke} />);
    });

    // 1. Crash
    await act(async () => {
      lifecycleHandler?.({
        payload: {
          status: "restarting",
          message: "后端服务异常，正在尝试热重启...",
        },
      });
    });
    expect(container.querySelector('[data-testid="core-status-banner"]')).not.toBeNull();

    // 2. Recovered
    await act(async () => {
      lifecycleHandler?.({
        payload: {
          status: "recovered",
          message: "后端服务已恢复正常",
        },
      });
    });
    const recoveredBanner = container.querySelector('[data-testid="core-status-banner"]');
    expect(recoveredBanner).not.toBeNull();
    expect(recoveredBanner?.textContent).toContain("后端服务已恢复正常");

    // 3. Permanent failure (max retries reached)
    await act(async () => {
      lifecycleHandler?.({
        payload: {
          status: "fatal",
          message: "后端服务异常，自动重启失败，请检查服务日志",
        },
      });
    });
    const fatalBanner = container.querySelector('[data-testid="core-status-banner"]');
    expect(fatalBanner).not.toBeNull();
    expect(fatalBanner?.textContent).toContain("后端服务异常，自动重启失败");
    // R-006: In fatal state, automatic retry budget is exhausted.
    // Misleading manual retry button is removed so user is directed to check logs.
    const retryBtn = fatalBanner?.querySelector("button");
    expect(retryBtn).toBeNull();
  });

  it("AC3: preserves draft inputs across sidecar crash and recovery", async () => {
    const createdBooks: unknown[] = [];
    const mockInvoke = vi.fn().mockImplementation(async (cmd: string, args?: Record<string, unknown>) => {
      if (cmd === "library_list_books") return createdBooks;
      if (cmd === "library_create_book") {
        const title = (args?.title as string) || "Untitled";
        const newBook = {
          book_id: `b-${Date.now()}`,
          title,
          original_title: "",
          is_favorite: false,
          is_archived: false,
          page_count: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        createdBooks.push(newBook);
        return newBook;
      }
      return null;
    });

    await act(async () => {
      root.render(<AppShell invoke={mockInvoke} />);
    });

    // Open create title dialog
    const createBtn = container.querySelector('[data-testid="toolbar-new-book-btn"]') as HTMLButtonElement | null;
    expect(createBtn).not.toBeNull();
    await act(async () => {
      createBtn?.click();
    });

    // Type a draft book title into input
    const input = container.querySelector('[data-testid="create-title-input"]') as HTMLInputElement | null;
    expect(input).not.toBeNull();
    await act(async () => {
      if (input) {
        input.value = "Draft Comic Title Unsaved";
        input.dispatchEvent(new dom.window.Event("input", { bubbles: true }));
      }
    });
    expect(input?.value).toBe("Draft Comic Title Unsaved");

    // INJECT FAULT: Sidecar crashes while draft is uncommitted
    await act(async () => {
      lifecycleHandler?.({
        payload: {
          status: "restarting",
          message: "后端服务异常，正在尝试热重启...",
        },
      });
    });

    // Verification 1: Banner appears
    expect(container.querySelector('[data-testid="core-status-banner"]')).not.toBeNull();

    // Verification 2: Dialog is STILL open and draft text is NOT LOST
    const inputDuringCrash = container.querySelector('[data-testid="create-title-input"]') as HTMLInputElement | null;
    expect(inputDuringCrash).not.toBeNull();
    expect(inputDuringCrash?.value).toBe("Draft Comic Title Unsaved");

    // INJECT RECOVERY: Sidecar successfully restarts
    await act(async () => {
      lifecycleHandler?.({
        payload: {
          status: "recovered",
          message: "后端服务已恢复正常",
        },
      });
    });

    // Verification 3: Draft is STILL intact after recovery
    const inputAfterRecovery = container.querySelector('[data-testid="create-title-input"]') as HTMLInputElement | null;
    expect(inputAfterRecovery).not.toBeNull();
    expect(inputAfterRecovery?.value).toBe("Draft Comic Title Unsaved");

    // Verification 4: User submits draft successfully
    const submitBtn = container.querySelector('[data-testid="create-title-submit-btn"]') as HTMLButtonElement | null;
    expect(submitBtn).not.toBeNull();
    await act(async () => {
      submitBtn?.click();
    });

    // Book created with the exact draft title
    expect(mockInvoke).toHaveBeenCalledWith("library_create_book", expect.objectContaining({
      payload: expect.objectContaining({
        title: "Draft Comic Title Unsaved",
      }),
    }));
  });
});
