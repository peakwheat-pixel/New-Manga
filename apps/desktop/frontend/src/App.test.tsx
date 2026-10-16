import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

describe("App Mode Dispatching - Production AppShell vs Probe/AC1 Frozen Chrome", () => {
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

  it("mounts production AppShell in user-facing production mode", async () => {
    await act(async () => {
      root.render(<App />);
    });

    // Production mode mounts AppShell
    const appShell = container.querySelector('[data-testid="app-shell"]');
    expect(appShell).not.toBeNull();
    expect(container.querySelector('[data-testid="app-nav-rail"]')).not.toBeNull();
  });

  it("renders frozen probe/console chrome when ?view=console is specified", async () => {
    const consoleDom = new JSDOM("<!doctype html><html><body></body></html>", {
      url: "http://localhost/?view=console",
    });
    vi.stubGlobal("window", consoleDom.window);
    vi.stubGlobal("document", consoleDom.window.document);
    vi.stubGlobal("navigator", consoleDom.window.navigator);
    vi.stubGlobal("HTMLElement", consoleDom.window.HTMLElement);

    const consoleContainer = consoleDom.window.document.createElement("div");
    consoleDom.window.document.body.appendChild(consoleContainer);
    const consoleRoot = createRoot(consoleContainer);

    await act(async () => {
      consoleRoot.render(<App />);
    });

    // Probe chrome DOM shape preserved word-for-word
    expect(consoleContainer.textContent).toContain("M2-RC2 resource channel runtime");
    expect(consoleContainer.querySelector('[data-testid="app-shell"]')).toBeNull();

    act(() => {
      consoleRoot.unmount();
    });
  });

  it("renders frozen probe chrome when probe_config resolves (probe mode)", async () => {
    // Mock TAURI bridge where probe_config succeeds
    const mockInvoke = vi.fn(async (cmd: string) => {
      if (cmd === "probe_config") {
        return { probe_auto: true, fixture_shas: null, chunk_size: 1024 };
      }
      if (cmd === "probe_write_results") {
        return null;
      }
      if (cmd === "probe_exit") {
        return null;
      }
      return null;
    });

    dom.window.__TAURI__ = {
      core: {
        invoke: mockInvoke,
      },
    } as any;

    await act(async () => {
      root.render(<App />);
      // wait for effect resolution
      for (let i = 0; i < 10; i++) {
        await Promise.resolve();
      }
    });

    // Must preserve probe runtime shell
    expect(container.textContent).toContain("M2-RC2 resource channel runtime");
    expect(container.querySelector('[data-testid="app-shell"]')).toBeNull();
  });
});
