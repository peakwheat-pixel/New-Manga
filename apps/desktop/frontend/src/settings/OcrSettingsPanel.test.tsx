import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { setNativeSelectValue } from "../testSupport/jsdomEvents";
import { SettingsClient } from "./client";
import { OcrSettingsPanel } from "./OcrSettingsPanel";

/**
 * SETTINGS-OPEN-A-1 §3.1 / AC3+AC4 — the OCR section surface: initial read
 * (JSON null → explicit 未设置), exact whole-section save payload, post-save
 * re-read echo, closed §9 error projection, and "a failed save keeps the
 * user's draft".
 */
describe("OcrSettingsPanel (SETTINGS-OPEN-A-1 §3.1)", () => {
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
  const select = (id: string) => q(`[data-testid="${id}"]`) as HTMLSelectElement;
  const saveButton = () => q('[data-testid="ocr-settings-panel-save-btn"]') as HTMLButtonElement;

  it("shows the loading skeleton while settings_get(section) is pending", () => {
    const invoke = vi.fn(() => new Promise(() => {}));
    act(() => {
      root.render(<OcrSettingsPanel client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="ocr-settings-panel-loading"]')).not.toBeNull();
    expect(select("ocr-script")).toBeNull();
  });

  it("reads the ocr section, renders the persisted values and the effect note", async () => {
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      expect(command).toBe("settings_get");
      expect(args).toEqual({ section: "ocr" });
      return { settings: { ocr: { script: "korean", direction: "vertical" } } };
    });
    await act(async () => {
      root.render(<OcrSettingsPanel client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="ocr-settings-panel-unset"]')).toBeNull();
    expect(select("ocr-script").value).toBe("korean");
    expect(select("ocr-direction").value).toBe("vertical");
    expect(q('[data-testid="ocr-settings-panel-effective"]')?.textContent).toContain("韩语");
    expect(q('[data-testid="ocr-settings-panel-effect-note"]')?.textContent).toContain(
      "对之后启动的任务生效",
    );
    // Nothing to save until the draft changes.
    expect(saveButton().disabled).toBe(true);
  });

  it("renders 未设置 with the Core default hint when the section is JSON null", async () => {
    const invoke = vi.fn(async () => ({ settings: { ocr: null } }));
    await act(async () => {
      root.render(<OcrSettingsPanel client={new SettingsClient(invoke)} />);
    });
    const unset = q('[data-testid="ocr-settings-panel-unset"]');
    expect(unset).not.toBeNull();
    expect(unset?.textContent).toContain("未设置");
    expect(unset?.textContent).toContain("japanese");
    expect(select("ocr-script").value).toBe("japanese");
    expect(select("ocr-direction").value).toBe("horizontal");
  });

  it("saves the exact whole-section payload, then re-reads the persisted value", async () => {
    let stored: Record<string, unknown> = { script: "japanese", direction: "horizontal" };
    let getCalls = 0;
    const saveCalls: Array<Record<string, unknown>> = [];
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      if (command === "settings_update_section") {
        expect(args).toEqual({
          section: "ocr",
          values: { script: "korean", direction: "vertical" },
        });
        stored = args?.values as Record<string, unknown>;
        saveCalls.push(stored);
        return {};
      }
      getCalls += 1;
      return { settings: { ocr: stored } };
    });
    await act(async () => {
      root.render(<OcrSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeSelectValue(dom.window, select("ocr-script"), "korean");
    });
    await act(async () => {
      setNativeSelectValue(dom.window, select("ocr-direction"), "vertical");
    });
    expect(saveButton().disabled).toBe(false);
    await act(async () => {
      saveButton().click();
    });
    expect(saveCalls).toHaveLength(1);
    // initial read + post-save re-read: the echo comes from the Core projection
    expect(getCalls).toBe(2);
    expect(select("ocr-script").value).toBe("korean");
    expect(select("ocr-direction").value).toBe("vertical");
    expect(q('[data-testid="ocr-settings-panel-effective"]')?.textContent).toContain("韩语");
    expect(q('[data-testid="ocr-settings-panel-save-error"]')).toBeNull();
  });

  it("load failure shows the closed §9 projection with retry, never the raw payload", async () => {
    const invoke = vi.fn(async () => {
      throw "CORE_UNAVAILABLE";
    });
    await act(async () => {
      root.render(<OcrSettingsPanel client={new SettingsClient(invoke)} />);
    });
    const bar = q('[data-testid="ocr-settings-panel-load-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-error-category")).toBe("unavailable");
    expect(bar?.getAttribute("data-message-key")).toBe("SETTINGS_UNAVAILABLE");
    expect(container.textContent).not.toContain("CORE_UNAVAILABLE");
    expect(q('[data-testid="ocr-settings-panel-load-error-retry"]')).not.toBeNull();
  });

  it("a failed save keeps the user's draft and shows the localized error", async () => {
    const invoke = vi.fn(async (command: string) => {
      if (command === "settings_update_section") {
        throw { code: "INVALID_REQUEST" };
      }
      return { settings: { ocr: { script: "japanese", direction: "horizontal" } } };
    });
    await act(async () => {
      root.render(<OcrSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeSelectValue(dom.window, select("ocr-script"), "korean");
    });
    await act(async () => {
      saveButton().click();
    });
    const bar = q('[data-testid="ocr-settings-panel-save-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-error-category")).toBe("validation");
    expect(bar?.getAttribute("data-message-key")).toBe("SETTINGS_INVALID_INPUT");
    // The draft survived the failed write; the effective value did not move.
    expect(select("ocr-script").value).toBe("korean");
    expect(q('[data-testid="ocr-settings-panel-effective"]')?.textContent).toContain("日语");
  });
});
