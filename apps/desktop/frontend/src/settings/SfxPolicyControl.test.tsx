import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { setNativeSelectValue } from "../testSupport/jsdomEvents";
import { SettingsClient } from "./client";
import { SfxPolicyControl } from "./SfxPolicyControl";

/**
 * P15 AC3/AC4 — the sfx.policy surface: the five state-matrix states, the
 * null-vs-empty-object distinction (frozen-None), and "a failed save keeps
 * the user's input".
 */

function makeDom() {
  const dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
  const container = dom.window.document.createElement("div");
  dom.window.document.body.appendChild(container);
  return { dom, container };
}

describe("SfxPolicyControl state matrix (AC4)", () => {
  let dom: JSDOM;
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    ({ dom, container } = makeDom());
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    vi.stubGlobal("window", dom.window);
    vi.stubGlobal("document", dom.window.document);
    vi.stubGlobal("navigator", dom.window.navigator);
    vi.stubGlobal("HTMLElement", dom.window.HTMLElement);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    vi.unstubAllGlobals();
  });

  const q = (selector: string) => container.querySelector(selector) as HTMLElement | null;

  it("shows the loading skeleton while settings_get(section) is pending", () => {
    const invoke = vi.fn(() => new Promise(() => {}));
    act(() => {
      root.render(<SfxPolicyControl client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="sfx-policy-loading"]')).not.toBeNull();
    expect(q('[data-testid="sfx-policy-select"]')).toBeNull();
  });

  it("renders the 未设置 placeholder when the section is JSON null, with the default-fill action (AC3 frozen-None)", async () => {
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      expect(command).toBe("settings_get");
      expect(args).toEqual({ section: "sfx" });
      return { settings: { sfx: null } };
    });
    await act(async () => {
      root.render(<SfxPolicyControl client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="sfx-policy-unset"]')).not.toBeNull();
    expect(q('[data-testid="sfx-policy-unset"]')?.textContent).toContain("未设置");
    expect(q('[data-testid="sfx-policy-fill-default-btn"]')).not.toBeNull();
    expect(q('[data-testid="sfx-policy-effective"]')?.textContent).toContain("未设置");
  });

  it("distinguishes a SET empty section from null: {sfx:{}} still reads as no usable policy, the placeholder explains the default", async () => {
    const invoke = vi.fn(async () => ({ settings: { sfx: {} } }));
    await act(async () => {
      root.render(<SfxPolicyControl client={new SettingsClient(invoke)} />);
    });
    // An empty object is not a null section, but it carries no policy — the
    // control shows the unset affordance rather than inventing a value.
    expect(q('[data-testid="sfx-policy-unset"]')).not.toBeNull();
  });

  it("renders the selector with the stored value when the section is set", async () => {
    const invoke = vi.fn(async () => ({ settings: { sfx: { policy: "translate" } } }));
    await act(async () => {
      root.render(<SfxPolicyControl client={new SettingsClient(invoke)} />);
    });
    expect(q('[data-testid="sfx-policy-unset"]')).toBeNull();
    const select = q('[data-testid="sfx-policy-select"]') as HTMLSelectElement;
    expect(select.value).toBe("translate");
    expect(q('[data-testid="sfx-policy-effective"]')?.textContent).toContain("翻译");
  });

  it("load failure shows the closed §9 error bar with retry, not the raw payload", async () => {
    const invoke = vi.fn(async () => {
      throw "CORE_UNAVAILABLE";
    });
    await act(async () => {
      root.render(<SfxPolicyControl client={new SettingsClient(invoke)} />);
    });
    const bar = q('[data-testid="sfx-policy-load-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-error-category")).toBe("unavailable");
    expect(bar?.getAttribute("data-message-key")).toBe("SETTINGS_UNAVAILABLE");
    expect(bar?.textContent).not.toContain("CORE_UNAVAILABLE");
    expect(q('[data-testid="sfx-policy-load-error-retry"]')).not.toBeNull();
  });

  it("saving shows a busy state and submits exactly the whole-section upsert {sfx, {policy}}", async () => {
    let resolveSave: (() => void) | null = null;
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      if (command === "settings_update_section") {
        expect(args).toEqual({ section: "sfx", values: { policy: "manual" } });
        await new Promise<void>((resolve) => {
          resolveSave = resolve;
        });
      }
      return { settings: { sfx: { policy: "skip" } } };
    });
    await act(async () => {
      root.render(<SfxPolicyControl client={new SettingsClient(invoke)} />);
    });
    const select = q('[data-testid="sfx-policy-select"]') as HTMLSelectElement;
    await act(async () => {
      setNativeSelectValue(dom.window, select, "manual");
    });
    await act(async () => {
      (q('[data-testid="sfx-policy-save-btn"]') as HTMLButtonElement).click();
    });
    // progress: the busy state is visible while the round trip is pending
    expect(q('[data-testid="sfx-policy-save-btn"]')?.textContent).toContain("保存中");
    expect((q('[data-testid="sfx-policy-save-btn"]') as HTMLButtonElement).disabled).toBe(true);
    await act(async () => {
      resolveSave?.();
    });
    expect(q('[data-testid="sfx-policy-effective"]')?.textContent).toContain("手动处理");
    expect(q('[data-testid="sfx-policy-save-error"]')).toBeNull();
  });

  it("a failed save keeps the user's chosen draft (AC4) and shows the localized error", async () => {
    const invoke = vi.fn(async (command: string) => {
      if (command === "settings_update_section") {
        throw { code: "INVALID_REQUEST" };
      }
      return { settings: { sfx: { policy: "skip" } } };
    });
    await act(async () => {
      root.render(<SfxPolicyControl client={new SettingsClient(invoke)} />);
    });
    const select = q('[data-testid="sfx-policy-select"]') as HTMLSelectElement;
    expect(select.value).toBe("skip");
    await act(async () => {
      setNativeSelectValue(dom.window, select, "manual");
    });
    await act(async () => {
      (q('[data-testid="sfx-policy-save-btn"]') as HTMLButtonElement).click();
    });
    const bar = q('[data-testid="sfx-policy-save-error"]');
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("data-error-category")).toBe("validation");
    expect(bar?.getAttribute("data-message-key")).toBe("SETTINGS_INVALID_INPUT");
    // The user's input survived the failed save:
    expect((q('[data-testid="sfx-policy-select"]') as HTMLSelectElement).value).toBe("manual");
    // The effective value is unchanged until a save succeeds:
    expect(q('[data-testid="sfx-policy-effective"]')?.textContent).toContain("跳过翻译");
  });

  it("the unset placeholder's fill action saves the default (skip) through the same channel", async () => {
    const calls: Array<{ command: string; args?: Record<string, unknown> }> = [];
    const invoke = vi.fn(async (command: string, args?: Record<string, unknown>) => {
      calls.push({ command, args });
      if (command === "settings_get") return { settings: { sfx: null } };
      return { settings: { sfx: { policy: "skip" } } };
    });
    await act(async () => {
      root.render(<SfxPolicyControl client={new SettingsClient(invoke)} />);
    });
    await act(async () => {
      (q('[data-testid="sfx-policy-fill-default-btn"]') as HTMLButtonElement).click();
    });
    const save = calls.find((c) => c.command === "settings_update_section");
    expect(save?.args).toEqual({ section: "sfx", values: { policy: "skip" } });
  });
});
