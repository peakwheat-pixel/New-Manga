import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { SettingsClient } from "./client";
import { setNativeInputValue, setNativeSelectValue } from "../testSupport/jsdomEvents";
import { CapabilityBindingPanel } from "./CapabilityBindingPanel";

/**
 * P15 AC2/AC3 — the G21 capability default-binding surface: set/clear are
 * the only write ops, the scope union is preserved on the wire, and an
 * empty book/chapter scope id is caught locally before any wire call.
 */
function makeDom() {
  const dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
  const container = dom.window.document.createElement("div");
  dom.window.document.body.appendChild(container);
  return { dom, container };
}

describe("CapabilityBindingPanel (G21)", () => {
  let dom: JSDOM;
  let container: HTMLDivElement;
  let root: Root;
  let invoke: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    ({ dom, container } = makeDom());
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    vi.stubGlobal("window", dom.window);
    vi.stubGlobal("document", dom.window.document);
    vi.stubGlobal("navigator", dom.window.navigator);
    vi.stubGlobal("HTMLElement", dom.window.HTMLElement);
    invoke = vi.fn(async (command: string) => {
      if (command === "settings_provider_bindings_resolve") {
        return { profile_id: null, source: null };
      }
      return {};
    });
    root = createRoot(container);
    act(() => {
      root.render(<CapabilityBindingPanel client={new SettingsClient(invoke)} />);
    });
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    vi.unstubAllGlobals();
  });

  const q = (selector: string) => container.querySelector(selector) as HTMLElement | null;

  const setInputValue = async (el: HTMLInputElement, value: string) => {
    await act(async () => {
      setNativeInputValue(dom.window, el, value);
    });
  };

  const setSelectValue = async (el: HTMLSelectElement, value: string) => {
    await act(async () => {
      setNativeSelectValue(dom.window, el, value);
    });
  };

  it("sends the exact §3.2 payloads for set and clear on a book scope", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="binding-form-scope-kind"]')).not.toBeNull();
    });
    await setSelectValue(q('[data-testid="binding-form-scope-kind"]') as HTMLSelectElement, "book");
    await setInputValue(q('[data-testid="binding-form-scope-id"]') as HTMLInputElement, "bk-7");
    await setSelectValue(q('[data-testid="binding-form-capability"]') as HTMLSelectElement, "Translation");
    await setInputValue(q('[data-testid="binding-form-profile-id"]') as HTMLInputElement, "prof-a");
    await act(async () => {
      (q('[data-testid="binding-set-btn"]') as HTMLButtonElement).click();
    });
    expect(invoke.mock.calls.find(([command]) => command === "settings_provider_bindings_set")?.[1]).toEqual({
      scope: { kind: "book", book_id: "bk-7" },
      capability: "Translation",
      profile_id: "prof-a",
    });

    await act(async () => {
      (q('[data-testid="binding-clear-btn"]') as HTMLButtonElement).click();
    });
    expect(invoke.mock.calls.find(([command]) => command === "settings_provider_bindings_clear")?.[1]).toEqual({
      scope: { kind: "book", book_id: "bk-7" },
      capability: "Translation",
    });
  });

  it("blocks set/clear while a book/chapter scope id is missing (local guard, no wire call)", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="binding-form-scope-kind"]')).not.toBeNull();
    });
    await setSelectValue(q('[data-testid="binding-form-scope-kind"]') as HTMLSelectElement, "chapter");
    // scope id left empty:
    expect(q('[data-testid="binding-field-error-scope-id"]')).not.toBeNull();
    expect((q('[data-testid="binding-set-btn"]') as HTMLButtonElement).disabled).toBe(true);
    expect((q('[data-testid="binding-clear-btn"]') as HTMLButtonElement).disabled).toBe(true);
    expect(invoke.mock.calls.filter(([command]) => command.startsWith("settings_provider_bindings_")).length).toBe(
      1, // only the initial resolve
    );
  });

  it("shows the resolved current binding and the last action feedback", async () => {
    invoke.mockImplementation(async (command: string) => {
      if (command === "settings_provider_bindings_resolve") {
        return { profile_id: "prof-a", source: { kind: "global" } };
      }
      if (command === "settings_provider_bindings_set") {
        return { binding: { scope: { kind: "global" }, capability: "OCR", profile_id: "prof-a" } };
      }
      return {};
    });
    // The initial resolve already ran with the old mock (unbound); switch
    // the capability so the resolve effect re-runs against the new mock.
    await setSelectValue(q('[data-testid="binding-form-capability"]') as HTMLSelectElement, "Translation");
    await vi.waitFor(() => {
      expect(q('[data-testid="binding-current"]')?.textContent).toContain("prof-a");
    });
    await setInputValue(q('[data-testid="binding-form-profile-id"]') as HTMLInputElement, "prof-a");
    await act(async () => {
      (q('[data-testid="binding-set-btn"]') as HTMLButtonElement).click();
    });
    await vi.waitFor(() => {
      expect(q('[data-testid="binding-last-action"]')?.textContent).toContain("已绑定");
    });
  });
});
