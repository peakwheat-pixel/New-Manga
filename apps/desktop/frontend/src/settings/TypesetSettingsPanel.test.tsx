import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { setNativeInputValue, setNativeSelectValue } from "../testSupport/jsdomEvents";
import { SettingsClient } from "./client";
import { TypesetSettingsPanel } from "./TypesetSettingsPanel";

/**
 * SETTINGS-OPEN-A-1 §3.4 / AC3+AC4 — the typeset default-style section:
 * eleven editable keys (font_family intentionally absent), #RRGGBB colors
 * with a text echo, numeric ranges, exact payload, post-save re-read and the
 * closed §9 error projection.
 */
describe("TypesetSettingsPanel (SETTINGS-OPEN-A-1 §3.4)", () => {
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
    q('[data-testid="typeset-settings-panel-save-btn"]') as HTMLButtonElement;

  const FULL_SECTION = {
    text_color: "#101010",
    fill_color: "#fafafa",
    stroke_enabled: false,
    stroke_color: "#202020",
    stroke_width: 2.5,
    line_spacing: 1.4,
    text_align: "right",
    text_direction: "horizontal",
    auto_font_size: false,
    font_size_offset: -1,
    manual_font_size: 22,
  };

  it("shows the loading skeleton while settings_get(section) is pending", () => {
    const invoke = vi.fn(() => new Promise(() => {}));
    act(() => {
      root.render(<TypesetSettingsPanel client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="typeset-settings-panel-loading"]')).not.toBeNull();
    expect(input("typeset-text-color")).toBeNull();
  });

  it("reads the typeset section, renders every persisted value and the effect note", async () => {
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      expect(command).toBe("settings_get");
      expect(args).toEqual({ section: "typeset" });
      return { settings: { typeset: FULL_SECTION } };
    });
    await act(async () => {
      root.render(<TypesetSettingsPanel client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="typeset-settings-panel-unset"]')).toBeNull();
    expect(input("typeset-text-color").value).toBe("#101010");
    expect(q('[data-testid="typeset-text-color-value"]')?.textContent).toBe("#101010");
    expect(input("typeset-fill-color").value).toBe("#fafafa");
    expect(input("typeset-stroke-enabled").checked).toBe(false);
    expect(input("typeset-stroke-color").value).toBe("#202020");
    expect(input("typeset-stroke-width").value).toBe("2.5");
    expect(input("typeset-line-spacing").value).toBe("1.4");
    expect(select("typeset-text-align").value).toBe("right");
    expect(select("typeset-text-direction").value).toBe("horizontal");
    expect(input("typeset-auto-font-size").checked).toBe(false);
    expect(input("typeset-font-size-offset").value).toBe("-1");
    expect(input("typeset-manual-font-size").value).toBe("22");
    // font_family is NOT part of the batch A surface
    expect(q('[data-testid="typeset-font-family"]')).toBeNull();
    expect(q('[data-testid="typeset-settings-panel-effect-note"]')?.textContent).toContain(
      "对之后启动的任务生效",
    );
    expect(saveButton().disabled).toBe(true);
  });

  it("renders 未设置 with the Core default style when the section is JSON null", async () => {
    const invoke = vi.fn(async () => ({ settings: { typeset: null } }));
    await act(async () => {
      root.render(<TypesetSettingsPanel client={new SettingsClient(invoke)} />);
    });
    const unset = q('[data-testid="typeset-settings-panel-unset"]');
    expect(unset).not.toBeNull();
    expect(unset?.textContent).toContain("未设置");
    expect(unset?.textContent).toContain("#000000");
    expect(input("typeset-text-color").value).toBe("#000000");
    expect(input("typeset-fill-color").value).toBe("#ffffff");
    expect(input("typeset-stroke-enabled").checked).toBe(true);
    expect(input("typeset-stroke-width").value).toBe("3");
    expect(input("typeset-line-spacing").value).toBe("1");
    expect(select("typeset-text-align").value).toBe("left");
    expect(select("typeset-text-direction").value).toBe("auto");
    expect(input("typeset-auto-font-size").checked).toBe(true);
    expect(input("typeset-font-size-offset").value).toBe("0");
    expect(input("typeset-manual-font-size").value).toBe("");
  });

  it("saves the exact whole-section payload with typed values and re-reads it", async () => {
    let stored: Record<string, unknown> = { ...FULL_SECTION };
    let getCalls = 0;
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      if (command === "settings_update_section") {
        expect(args).toEqual({
          section: "typeset",
          values: {
            text_color: "#112233",
            fill_color: "#fafafa",
            stroke_enabled: false,
            stroke_color: "#202020",
            stroke_width: 4.5,
            line_spacing: 1.5,
            text_align: "center",
            text_direction: "vertical",
            auto_font_size: false,
            font_size_offset: -2,
            manual_font_size: 24,
          },
        });
        stored = args?.values as Record<string, unknown>;
        return {};
      }
      getCalls += 1;
      return { settings: { typeset: stored } };
    });
    await act(async () => {
      root.render(<TypesetSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("typeset-text-color"), "#112233");
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("typeset-stroke-width"), "4.5");
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("typeset-line-spacing"), "1.5");
    });
    await act(async () => {
      setNativeSelectValue(dom.window, select("typeset-text-align"), "center");
    });
    await act(async () => {
      setNativeSelectValue(dom.window, select("typeset-text-direction"), "vertical");
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("typeset-font-size-offset"), "-2");
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("typeset-manual-font-size"), "24");
    });
    expect(saveButton().disabled).toBe(false);
    await act(async () => {
      saveButton().click();
    });
    expect(getCalls).toBe(2);
    expect(input("typeset-text-color").value).toBe("#112233");
    expect(q('[data-testid="typeset-text-color-value"]')?.textContent).toBe("#112233");
    expect(input("typeset-stroke-width").value).toBe("4.5");
    expect(select("typeset-text-align").value).toBe("center");
    expect(q('[data-testid="typeset-settings-panel-save-error"]')).toBeNull();
  });

  it("sends manual_font_size=null when the optional field is blank", async () => {
    let stored: Record<string, unknown> = { ...FULL_SECTION };
    const saveCalls: Array<Record<string, unknown>> = [];
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      if (command === "settings_update_section") {
        saveCalls.push(args?.values as Record<string, unknown>);
        stored = args?.values as Record<string, unknown>;
        return {};
      }
      return { settings: { typeset: stored } };
    });
    await act(async () => {
      root.render(<TypesetSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("typeset-manual-font-size"), "");
    });
    await act(async () => {
      saveButton().click();
    });
    expect(saveCalls).toHaveLength(1);
    expect(saveCalls[0].manual_font_size).toBeNull();
    // the rest of the section is always written as a whole-section upsert
    expect(Object.keys(saveCalls[0]).sort()).toEqual(
      [
        "auto_font_size",
        "fill_color",
        "font_size_offset",
        "line_spacing",
        "manual_font_size",
        "stroke_color",
        "stroke_enabled",
        "stroke_width",
        "text_align",
        "text_color",
        "text_direction",
      ].sort(),
    );
  });

  it("blocks the save and explains both numeric range violations", async () => {
    const invoke = vi.fn(async () => ({ settings: { typeset: null } }));
    await act(async () => {
      root.render(<TypesetSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("typeset-stroke-width"), "25");
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("typeset-line-spacing"), "3.5");
    });
    expect(q('[data-testid="typeset-stroke-width-error"]')?.textContent).toContain("0–20");
    expect(q('[data-testid="typeset-line-spacing-error"]')?.textContent).toContain("1.0–3.0");
    expect(input("typeset-stroke-width").getAttribute("aria-invalid")).toBe("true");
    expect(saveButton().disabled).toBe(true);
    expect(invoke).not.toHaveBeenCalledWith("settings_update_section", expect.anything());
  });

  it("validates font_size_offset and manual_font_size ranges", async () => {
    const invoke = vi.fn(async () => ({ settings: { typeset: null } }));
    await act(async () => {
      root.render(<TypesetSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("typeset-font-size-offset"), "6");
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("typeset-manual-font-size"), "600");
    });
    expect(q('[data-testid="typeset-font-size-offset-error"]')?.textContent).toContain("-5 到 +5");
    expect(q('[data-testid="typeset-manual-font-size-error"]')?.textContent).toContain("1–500");
    expect(saveButton().disabled).toBe(true);
  });

  it("load failure shows the closed §9 projection with retry, never the raw payload", async () => {
    const invoke = vi.fn(async () => {
      throw "CORE_UNAVAILABLE";
    });
    await act(async () => {
      root.render(<TypesetSettingsPanel client={new SettingsClient(invoke)} />);
    });
    const bar = q('[data-testid="typeset-settings-panel-load-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-message-key")).toBe("SETTINGS_UNAVAILABLE");
    expect(container.textContent).not.toContain("CORE_UNAVAILABLE");
    expect(q('[data-testid="typeset-settings-panel-load-error-retry"]')).not.toBeNull();
  });

  it("a failed save keeps the user's draft and shows the localized error", async () => {
    const invoke = vi.fn(async (command: string) => {
      if (command === "settings_update_section") {
        throw { code: "INVALID_REQUEST" };
      }
      return { settings: { typeset: FULL_SECTION } };
    });
    await act(async () => {
      root.render(<TypesetSettingsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeSelectValue(dom.window, select("typeset-text-align"), "center");
    });
    await act(async () => {
      saveButton().click();
    });
    const bar = q('[data-testid="typeset-settings-panel-save-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-error-category")).toBe("validation");
    expect(select("typeset-text-align").value).toBe("center");
    expect(q('[data-testid="typeset-settings-panel-effective"]')?.textContent).toContain("右对齐");
  });
});
