import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { setNativeInputValue } from "../testSupport/jsdomEvents";
import { SettingsClient } from "./client";
import { TranslationParamsPanel } from "./TranslationParamsPanel";

/**
 * SETTINGS-OPEN-A-1 §3.2 / AC3+AC4 — translate.context_pages (1–5) and
 * translate.context_token_budget (200–8000): front-end range validation
 * blocks the write, the payload uses numbers (not the draft strings), and the
 * saved value is re-read from the Core projection.
 */
describe("TranslationParamsPanel (SETTINGS-OPEN-A-1 §3.2)", () => {
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
  const saveButton = () =>
    q('[data-testid="translation-params-panel-save-btn"]') as HTMLButtonElement;

  it("shows the loading skeleton while settings_get(section) is pending", () => {
    const invoke = vi.fn(() => new Promise(() => {}));
    act(() => {
      root.render(<TranslationParamsPanel client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="translation-params-panel-loading"]')).not.toBeNull();
    expect(input("translate-context-pages")).toBeNull();
  });

  it("reads the translate section, renders the persisted values and the effect note", async () => {
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      expect(command).toBe("settings_get");
      expect(args).toEqual({ section: "translate" });
      return { settings: { translate: { context_pages: 3, context_token_budget: 4000 } } };
    });
    await act(async () => {
      root.render(<TranslationParamsPanel client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="translation-params-panel-unset"]')).toBeNull();
    expect(input("translate-context-pages").value).toBe("3");
    expect(input("translate-context-token-budget").value).toBe("4000");
    expect(q('[data-testid="translation-params-panel-effective"]')?.textContent).toContain(
      "上下文页数 3",
    );
    expect(q('[data-testid="translation-params-panel-effect-note"]')?.textContent).toContain(
      "对之后启动的任务生效",
    );
    expect(saveButton().disabled).toBe(true);
  });

  it("renders 未设置 with the Core defaults when the section is JSON null", async () => {
    const invoke = vi.fn(async () => ({ settings: { translate: null } }));
    await act(async () => {
      root.render(<TranslationParamsPanel client={new SettingsClient(invoke)} />);
    });
    const unset = q('[data-testid="translation-params-panel-unset"]');
    expect(unset).not.toBeNull();
    expect(unset?.textContent).toContain("未设置");
    expect(unset?.textContent).toContain("context_pages=1");
    expect(unset?.textContent).toContain("context_token_budget=2000");
    expect(input("translate-context-pages").value).toBe("1");
    expect(input("translate-context-token-budget").value).toBe("2000");
  });

  it("saves the numeric whole-section payload with a busy state and re-reads the value", async () => {
    let stored: Record<string, unknown> = { context_pages: 1, context_token_budget: 2000 };
    let getCalls = 0;
    let resolveSave: (() => void) | null = null;
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      if (command === "settings_update_section") {
        expect(args).toEqual({
          section: "translate",
          values: { context_pages: 3, context_token_budget: 4000 },
        });
        await new Promise<void>((resolve) => {
          resolveSave = resolve;
        });
        stored = { context_pages: 3, context_token_budget: 4000 };
        return {};
      }
      getCalls += 1;
      return { settings: { translate: stored } };
    });
    await act(async () => {
      root.render(<TranslationParamsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("translate-context-pages"), "3");
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("translate-context-token-budget"), "4000");
    });
    expect(saveButton().disabled).toBe(false);
    await act(async () => {
      saveButton().click();
    });
    // busy state while the round trip is pending
    expect(saveButton().textContent).toContain("保存中");
    expect(saveButton().disabled).toBe(true);
    await act(async () => {
      resolveSave?.();
    });
    expect(getCalls).toBe(2); // initial read + post-save re-read
    expect(input("translate-context-pages").value).toBe("3");
    expect(input("translate-context-token-budget").value).toBe("4000");
    expect(q('[data-testid="translation-params-panel-save-error"]')).toBeNull();
  });

  it("blocks the save and explains the range when context_pages is out of 1–5", async () => {
    const invoke = vi.fn(async () => ({ settings: { translate: null } }));
    await act(async () => {
      root.render(<TranslationParamsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("translate-context-pages"), "9");
    });
    const error = q('[data-testid="translate-context-pages-error"]');
    expect(error).not.toBeNull();
    expect(error?.textContent).toContain("1–5");
    expect(input("translate-context-pages").getAttribute("aria-invalid")).toBe("true");
    expect(saveButton().disabled).toBe(true);
    // no write reached the channel
    expect(invoke).not.toHaveBeenCalledWith("settings_update_section", expect.anything());
  });

  it("blocks the save when context_token_budget is out of 200–8000", async () => {
    const invoke = vi.fn(async () => ({ settings: { translate: null } }));
    await act(async () => {
      root.render(<TranslationParamsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("translate-context-token-budget"), "9000");
    });
    const error = q('[data-testid="translate-context-token-budget-error"]');
    expect(error?.textContent).toContain("200–8000");
    expect(saveButton().disabled).toBe(true);
  });

  it("load failure shows the closed §9 projection with retry, never the raw payload", async () => {
    const invoke = vi.fn(async () => {
      throw "CORE_UNAVAILABLE";
    });
    await act(async () => {
      root.render(<TranslationParamsPanel client={new SettingsClient(invoke)} />);
    });
    const bar = q('[data-testid="translation-params-panel-load-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-message-key")).toBe("SETTINGS_UNAVAILABLE");
    expect(container.textContent).not.toContain("CORE_UNAVAILABLE");
    expect(q('[data-testid="translation-params-panel-load-error-retry"]')).not.toBeNull();
  });

  it("a failed save keeps the user's draft and shows the localized error", async () => {
    const invoke = vi.fn(async (command: string) => {
      if (command === "settings_update_section") {
        throw { code: "INVALID_REQUEST" };
      }
      return { settings: { translate: { context_pages: 1, context_token_budget: 2000 } } };
    });
    await act(async () => {
      root.render(<TranslationParamsPanel client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      setNativeInputValue(dom.window, input("translate-context-pages"), "2");
    });
    await act(async () => {
      saveButton().click();
    });
    const bar = q('[data-testid="translation-params-panel-save-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-error-category")).toBe("validation");
    expect(input("translate-context-pages").value).toBe("2");
    expect(q('[data-testid="translation-params-panel-effective"]')?.textContent).toContain(
      "上下文页数 1",
    );
  });
});
