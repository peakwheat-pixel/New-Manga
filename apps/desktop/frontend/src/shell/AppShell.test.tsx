import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { renderToString } from "react-dom/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AppShell } from "./AppShell";

describe("AppShell - Four-Page Rail, Keep-Alive, Shortcuts & GAP-G15 Compliance", () => {
  let dom: JSDOM;
  let container: HTMLDivElement;
  let root: ReturnType<typeof createRoot>;

  beforeEach(() => {
    dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
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

  it("renders 64px left Rail with fixed 4-page sequence: Bookshelf -> Workbench -> Reader -> Settings", () => {
    const html = renderToString(<AppShell invoke={vi.fn().mockResolvedValue([])} />);

    // 1. Minimum window bounds (1024x680)
    expect(html).toContain('data-testid="app-shell"');
    expect(html).toMatch(/min-width:\s*1024px/);
    expect(html).toMatch(/min-height:\s*680px/);

    // 2. Rail 64px
    expect(html).toContain('data-testid="app-nav-rail"');
    expect(html).toMatch(/width:\s*64px/);

    // 3. Nav buttons in sequence
    const bookshelfIdx = html.indexOf('data-testid="nav-bookshelf"');
    const workbenchIdx = html.indexOf('data-testid="nav-workbench"');
    const readerIdx = html.indexOf('data-testid="nav-reader"');
    const settingsIdx = html.indexOf('data-testid="nav-settings"');

    expect(bookshelfIdx).toBeGreaterThan(0);
    expect(workbenchIdx).toBeGreaterThan(bookshelfIdx);
    expect(readerIdx).toBeGreaterThan(workbenchIdx);
    expect(settingsIdx).toBeGreaterThan(readerIdx);

    // 4. Default active page is Bookshelf
    expect(html).toContain('data-testid="nav-bookshelf" title="书架 (Ctrl+1)" data-active="true"');
    expect(html).toContain('data-testid="nav-workbench" title="工作台 (Ctrl+2)" data-active="false"');

    // 5. G15 Compliance: NavBadge on Workbench is hidden (no badge element fabricated)
    expect(html).not.toContain("nav-badge");
    expect(html).not.toContain("badge-count");
  });

  it("keeps all four page containers mounted simultaneously (keep-alive, no unmounting)", async () => {
    const mockInvoke = vi.fn().mockResolvedValue([]);
    await act(async () => {
      root.render(<AppShell invoke={mockInvoke} />);
    });

    const bookshelfContainer = container.querySelector('[data-testid="page-container-bookshelf"]') as HTMLElement;
    const workbenchContainer = container.querySelector('[data-testid="page-container-workbench"]') as HTMLElement;
    const readerContainer = container.querySelector('[data-testid="page-container-reader"]') as HTMLElement;
    const settingsContainer = container.querySelector('[data-testid="page-container-settings"]') as HTMLElement;

    // All 4 containers MUST exist in DOM concurrently
    expect(bookshelfContainer).not.toBeNull();
    expect(workbenchContainer).not.toBeNull();
    expect(readerContainer).not.toBeNull();
    expect(settingsContainer).not.toBeNull();

    // Default: Bookshelf visible, others display: none
    expect(bookshelfContainer.style.display).toBe("flex");
    expect(workbenchContainer.style.display).toBe("none");
    expect(readerContainer.style.display).toBe("none");
    expect(settingsContainer.style.display).toBe("none");

    // Switch to Workbench
    const navWorkbench = container.querySelector('[data-testid="nav-workbench"]') as HTMLButtonElement;
    await act(async () => {
      navWorkbench.click();
    });

    // Bookshelf stays mounted in DOM, but hidden; Workbench becomes visible
    expect(bookshelfContainer.parentElement).toBe(workbenchContainer.parentElement);
    expect(bookshelfContainer.style.display).toBe("none");
    expect(workbenchContainer.style.display).toBe("flex");
    expect(navWorkbench.getAttribute("data-active")).toBe("true");

    // Switch to Reader
    const navReader = container.querySelector('[data-testid="nav-reader"]') as HTMLButtonElement;
    await act(async () => {
      navReader.click();
    });
    expect(readerContainer.style.display).toBe("flex");
    expect(workbenchContainer.style.display).toBe("none");

    // Switch to Settings
    const navSettings = container.querySelector('[data-testid="nav-settings"]') as HTMLButtonElement;
    await act(async () => {
      navSettings.click();
    });
    expect(settingsContainer.style.display).toBe("flex");
    expect(readerContainer.style.display).toBe("none");
  });

  it("handles Ctrl+1..4 keyboard shortcuts to switch pages", async () => {
    const mockInvoke = vi.fn().mockResolvedValue([]);
    await act(async () => {
      root.render(<AppShell invoke={mockInvoke} />);
    });

    const bookshelfContainer = container.querySelector('[data-testid="page-container-bookshelf"]') as HTMLElement;
    const workbenchContainer = container.querySelector('[data-testid="page-container-workbench"]') as HTMLElement;
    const readerContainer = container.querySelector('[data-testid="page-container-reader"]') as HTMLElement;
    const settingsContainer = container.querySelector('[data-testid="page-container-settings"]') as HTMLElement;

    // Press Ctrl+2 -> Workbench
    await act(async () => {
      dom.window.dispatchEvent(
        new dom.window.KeyboardEvent("keydown", { key: "2", ctrlKey: true, bubbles: true })
      );
    });
    expect(workbenchContainer.style.display).toBe("flex");
    expect(bookshelfContainer.style.display).toBe("none");

    // Press Ctrl+3 -> Reader
    await act(async () => {
      dom.window.dispatchEvent(
        new dom.window.KeyboardEvent("keydown", { key: "3", ctrlKey: true, bubbles: true })
      );
    });
    expect(readerContainer.style.display).toBe("flex");
    expect(workbenchContainer.style.display).toBe("none");

    // Press Ctrl+4 -> Settings
    await act(async () => {
      dom.window.dispatchEvent(
        new dom.window.KeyboardEvent("keydown", { key: "4", ctrlKey: true, bubbles: true })
      );
    });
    expect(settingsContainer.style.display).toBe("flex");
    expect(readerContainer.style.display).toBe("none");

    // Press Ctrl+1 -> Bookshelf
    await act(async () => {
      dom.window.dispatchEvent(
        new dom.window.KeyboardEvent("keydown", { key: "1", ctrlKey: true, bubbles: true })
      );
    });
    expect(bookshelfContainer.style.display).toBe("flex");
    expect(settingsContainer.style.display).toBe("none");
  });
});
