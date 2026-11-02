import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { setNativeInputValue, setNativeSelectValue } from "../testSupport/jsdomEvents";
import { SettingsClient } from "./client";
import { InpaintSettingsPanel } from "./InpaintSettingsPanel";

/**
 * SETTINGS-OPEN-A-1 §3.3 / AC3+AC4 — inpaint.preferred_quality /
 * background_complexity / dilate_radius / erode_radius: enum selects, numeric
 * range validation, exact payload and post-save re-read.
 */
describe("InpaintSettingsPanel (SETTINGS-OPEN-A-1 §3.3)", () => {
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
  const input = (id: string) => q(`[data-testid="${id}"]`) as HTMLInputElement;
  const select = (id: string) => q(`[data-testid="${id}"]`) as HTMLSelectElement;
  const saveButton = () =>
    q('[data-testid="inpaint-settings-panel-save-btn"]') as HTMLButtonElement;

  it("shows the loading skeleton while settings_get(section) is pending", () => {
    const invoke = vi.fn(() => new Promise(() => {}));
    act(() => {
      root.render(<InpaintSettingsPanel client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="inpaint-settings-panel-loading"]')).not.toBeNull();
    expect(select("inpaint-preferred-quality")).toBeNull();
  });

  it("reads the inpaint section, renders the persisted values and the effect note", async () => {
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      expect(command).toBe("settings_get");
      expect(args).toEqual({ section: "inpaint" });
      return {
        settings: {
          inpaint: {
            preferred_quality: "quality",
            background_complexity: "high",
            dilate_radius: 4,
            erode_radius: 1,
          },
        },
      };
    });
    await act(async () => {
      root.render(<InpaintSettingsPanel client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="inpaint-settings-panel-unset"]')).toBeNull();
    expect(select("inpaint-preferred-quality").value).toBe("quality");
    expect(select("inpaint-background-complexity").value).toBe("high");
    expect(input("inpaint-dilate-radius").value).toBe("4");
    expect(input("inpaint-erode-radius").value).toBe("1");
    expect(q('[data-testid="inpaint-settings-panel-effective"]')?.textContent).toContain(
      "高质量",
    );
    expect(q('[data-testid="inpaint-settings-panel-effect-note"]')?.textContent).toContain(
      "对之后启动的任务生效",
    );
    expect(saveButton().disabled).toBe(true);
  });

  it("renders 未设置 with the Core defaults when the section is JSON null", async () => {
    const invoke = vi.fn(async () => ({ settings: { inpaint: null } }));
    await act(async () => {
      root.render(<InpaintSettingsPanel client={new SettingsClient(invoke)} />);
    });
    const unset = q('[data-testid="inpaint-settings-panel-unset"]');
    expect(unset).not.toBeNull();
    expect(unset?.textContent).toContain("preferred_quality=balanced");
    expect(unset?.textContent).toContain("background_complexity=low");
    expect(unset?.textContent).toContain("dilate_radius=2");
    expect(unset?.textContent).toContain("erode_radius=0");
    expect(select("inpaint-preferred-quality").value).toBe("balanced");
    expect(input("inpaint-dilate-radius").value).toBe("2");
  });

  it("saves the exact whole-section payload and re-reads the persisted value", async () => {
    let stored: Record<string, unknown> = {
      preferred_quality: "balanced",
      background_complexity: "low",
      dilate_radius: 2,
      erode_radius: 0,
    };
    let getCalls = 0;
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      if (command === "settings_update_section") {
        expect(args).toEqual({
          section: "inpaint",
          values: {
            preferred_quality: "quality",
            background_complexity: "high",
            dilate_radius: 5,
            erode_radius: 2,
          },
        });
        stored = args?.values as Record<string, unknown>;
        return {};
      }
      getCalls += 1;
      return { settings: { inpaint: stored } };
    });
    await act(async () => {
      root.render(<InpaintSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeSelectValue(dom.window, select("inpaint-preferred-quality"), "quality");
    });
    await act(async () => {
      setNativeSelectValue(dom.window, select("inpaint-background-complexity"), "high");
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("inpaint-dilate-radius"), "5");
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("inpaint-erode-radius"), "2");
    });
    expect(saveButton().disabled).toBe(false);
    await act(async () => {
      saveButton().click();
    });
    expect(getCalls).toBe(2);
    expect(select("inpaint-preferred-quality").value).toBe("quality");
    expect(select("inpaint-background-complexity").value).toBe("high");
    expect(input("inpaint-dilate-radius").value).toBe("5");
    expect(q('[data-testid="inpaint-settings-panel-save-error"]')).toBeNull();
  });

  it("blocks the save and explains the range when dilate_radius is outside 0–10", async () => {
    const invoke = vi.fn(async () => ({ settings: { inpaint: null } }));
    await act(async () => {
      root.render(<InpaintSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("inpaint-dilate-radius"), "11");
    });
    const error = q('[data-testid="inpaint-dilate-radius-error"]');
    expect(error).not.toBeNull();
    expect(error?.textContent).toContain("0–10");
    expect(saveButton().disabled).toBe(true);
    expect(invoke).not.toHaveBeenCalledWith("settings_update_section", expect.anything());
  });

  it("load failure shows the closed §9 projection with retry, never the raw payload", async () => {
    const invoke = vi.fn(async () => {
      throw "CORE_UNAVAILABLE";
    });
    await act(async () => {
      root.render(<InpaintSettingsPanel client={new SettingsClient(invoke)} />);
    });
    const bar = q('[data-testid="inpaint-settings-panel-load-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-message-key")).toBe("SETTINGS_UNAVAILABLE");
    expect(container.textContent).not.toContain("CORE_UNAVAILABLE");
    expect(q('[data-testid="inpaint-settings-panel-load-error-retry"]')).not.toBeNull();
  });

  it("a failed save keeps the user's draft and shows the localized error", async () => {
    const invoke = vi.fn(async (command: string) => {
      if (command === "settings_update_section") {
        throw { code: "INVALID_REQUEST" };
      }
      return { settings: { inpaint: null } };
    });
    await act(async () => {
      root.render(<InpaintSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeSelectValue(dom.window, select("inpaint-preferred-quality"), "fast");
    });
    await act(async () => {
      saveButton().click();
    });
    const bar = q('[data-testid="inpaint-settings-panel-save-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-error-category")).toBe("validation");
    expect(select("inpaint-preferred-quality").value).toBe("fast");
    expect(q('[data-testid="inpaint-settings-panel-effective"]')?.textContent).toContain(
      "未设置",
    );
  });
});
