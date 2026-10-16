import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

describe("App Mode Dispatching - Detecting Neutrality, Production AppShell vs Probe/AC1 Frozen Chrome (I1)", () => {
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

  // I1 Assertion (a): When __TAURI__ is missing, stay neutral; no AppShell, no production commands
  it("renders neutral frozen console chrome without app-shell when __TAURI__ is missing", async () => {
    await act(async () => {
      root.render(<App />);
    });

    // Initial render and subsequent missing-bridge state MUST NOT mount AppShell
    expect(container.querySelector('[data-testid="app-shell"]')).toBeNull();
    expect(container.textContent).toContain("M2-RC2 resource channel runtime");
    expect(container.textContent).toContain("TAURI_BRIDGE_MISSING");
  });

  // I1 Assertion (b): Initial frame before probe_config resolves MUST NOT mount AppShell or call production commands
  it("renders neutral frozen console chrome and does NOT call production commands on initial frame before probe_config resolves", async () => {
    let resolveProbeConfig!: (val: unknown) => void;
    const probeConfigPending = new Promise((resolve) => {
      resolveProbeConfig = resolve;
    });

    const invokedCommands: string[] = [];
    const mockInvoke = vi.fn(async (cmd: string) => {
      invokedCommands.push(cmd);
      if (cmd === "ac1_request") {
        throw new Error("COMMAND_DENIED");
      }
      if (cmd === "probe_config") {
        return probeConfigPending;
      }
      return null;
    });

    dom.window.__TAURI__ = {
      core: {
        invoke: mockInvoke,
      },
    } as any;

    // Render initial frame while probe_config is still unresolved
    await act(async () => {
      root.render(<App />);
      // One turn to allow synchronous start and ac1 ping denial
      await Promise.resolve();
    });

    // 1. Initial frame MUST NOT mount AppShell
    expect(container.querySelector('[data-testid="app-shell"]')).toBeNull();
    expect(container.textContent).toContain("M2-RC2 resource channel runtime");

    // 2. Production commands MUST NOT be called in this unresolved detection window
    expect(invokedCommands).not.toContain("library_list_books");
    expect(invokedCommands).not.toContain("settings_get");
    expect(invokedCommands).not.toContain("library_import_file");
    expect(invokedCommands).not.toContain("library_import_folder");

    // Clean up pending promise
    resolveProbeConfig({ probe_auto: false });
  });

  // Probe Mode Confirmed: Renders frozen probe chrome with pre-Task DOM structure preserved
  it("renders frozen probe chrome when probe_config resolves as probe mode", async () => {
    const mockInvoke = vi.fn(async (cmd: string) => {
      if (cmd === "ac1_request") {
        throw new Error("COMMAND_DENIED");
      }
      if (cmd === "probe_config") {
        return { probe_auto: true, fixture_shas: null, chunk_size: 1024 };
      }
      if (cmd === "issue_resource_url") {
        return { url: "http://m2res.localhost/m2id/res-probe", opaque_id: "res-probe" };
      }
      if (cmd === "probe_issue_url" || cmd === "probe_write_results" || cmd === "probe_exit") {
        return null;
      }
      if (cmd === "library_list_books" || cmd === "settings_get") {
        throw new Error("COMMAND_DENIED_IN_PROBE_MODE");
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
      for (let i = 0; i < 15; i++) {
        await Promise.resolve();
      }
    });

    // Probe chrome DOM shape preserved word-for-word
    expect(container.textContent).toContain("M2-RC2 resource channel runtime");
    expect(container.querySelector('[data-testid="app-shell"]')).toBeNull();
  });

  // Production Mode: Explicitly entered only after probe_config is denied and deny matrix completes
  it("mounts production AppShell after probe_config is denied (production mode confirmed)", async () => {
    const invokedCommands: string[] = [];
    const mockInvoke = vi.fn(async (cmd: string) => {
      invokedCommands.push(cmd);
      if (cmd === "ac1_request" || cmd === "probe_config") {
        throw new Error("COMMAND_NOT_FOUND");
      }
      if (
        cmd === "register_catalog" ||
        cmd === "probe_write_results" ||
        cmd === "probe_exit" ||
        cmd === "probe_issue_url"
      ) {
        throw new Error("DENIED_IN_PRODUCTION");
      }
      if (cmd === "issue_resource_url") {
        return {
          url: "http://m2res.localhost/m2id/res-cataloged",
          size: 100,
          opaque_id: "res-cataloged",
        };
      }
      if (cmd === "library_list_books") {
        return [];
      }
      if (cmd === "settings_get") {
        return { settings: {} };
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
      for (let i = 0; i < 20; i++) {
        await Promise.resolve();
      }
    });

    // Now production mode is confirmed and AppShell is mounted
    expect(container.querySelector('[data-testid="app-shell"]')).not.toBeNull();
    expect(container.querySelector('[data-testid="app-nav-rail"]')).not.toBeNull();

    // In production mode, library_list_books is now legitimately called by BookshelfPage
    expect(invokedCommands).toContain("library_list_books");
  });

  // View Escape Hatch: ?view=console always renders frozen console chrome
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
});
