import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { SettingsClient } from "./client";
import { setNativeInputValue } from "../testSupport/jsdomEvents";
import { ProviderProfilePanel } from "./ProviderProfilePanel";
import type { ProviderProfile } from "./types";

/**
 * P15 AC2/AC3/AC4 — G21 Provider Profile panel: the editable key set, the
 * Secret-free credential affordance (no inputs at all), field-level
 * INVALID_REQUEST highlighting, and the failed-save-preserves-draft rule.
 */

const PROFILE_A: ProviderProfile = {
  profile_id: "prof-a",
  provider_id: "openai",
  display_name: "OpenAI 主力",
  capabilities: ["OCR", "Translation"],
  endpoint: "https://api.example.com/v1",
  model: "gpt-x",
  network_profile_id: null,
  enabled: true,
  credential_state: "configured",
  credential_hint: "sk-****abcd",
};

const PROFILE_B: ProviderProfile = {
  profile_id: "prof-b",
  provider_id: "openai",
  display_name: "OpenAI 备用",
  capabilities: ["Rendering"],
  endpoint: "https://backup.example.com/v1",
  model: "gpt-y",
  network_profile_id: null,
  enabled: false,
  credential_state: "missing",
};

function makeDom() {
  const dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
  const container = dom.window.document.createElement("div");
  dom.window.document.body.appendChild(container);
  return { dom, container };
}

describe("ProviderProfilePanel (G21)", () => {
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
      if (command === "settings_provider_profiles_list") {
        return { profiles: [PROFILE_A, PROFILE_B] };
      }
      if (command === "settings_network_profiles_list") {
        return { profiles: [] };
      }
      return {};
    });
    root = createRoot(container);
    act(() => {
      root.render(<ProviderProfilePanel client={new SettingsClient(invoke)} />);
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

  it("lists profiles with the read-only credential projection (multiple profiles per provider)", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="provider-row-prof-a"]')).not.toBeNull();
    });
    expect(q('[data-testid="provider-row-prof-b"]')).not.toBeNull();
    expect(q('[data-testid="provider-row-prof-a-credential"]')?.getAttribute("data-credential-state")).toBe("configured");
    expect(q('[data-testid="provider-row-prof-a-credential"]')?.textContent).toContain("sk-****abcd");
    expect(q('[data-testid="provider-row-prof-b-credential"]')?.getAttribute("data-credential-state")).toBe("missing");
  });

  it("renders NO input elements inside any CredentialField — a Secret can never be typed here (AC3)", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="provider-row-prof-a-credential"]')).not.toBeNull();
    });
    for (const credential of container.querySelectorAll('[data-testid$="-credential"]')) {
      expect(credential.querySelectorAll("input, textarea, select").length).toBe(0);
    }
  });

  it("credential_put carries only {target, intent} — no secret field (AC3 wire-level)", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="provider-row-prof-b-credential-put-btn"]')).not.toBeNull();
    });
    await act(async () => {
      (q('[data-testid="provider-row-prof-b-credential-put-btn"]') as HTMLButtonElement).click();
    });
    const call = invoke.mock.calls.find(([command]) => command === "credential_put");
    expect(call).toBeDefined();
    expect(call?.[1]).toEqual({
      target: { kind: "provider_api", profile_id: "prof-b" },
      intent: "create",
    });
  });

  it("highlights invalid fields locally (INVALID_REQUEST affordance) and does not call the wire", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="provider-new-btn"]')).not.toBeNull();
    });
    await act(async () => {
      (q('[data-testid="provider-new-btn"]') as HTMLButtonElement).click();
    });
    expect(q('[data-testid="provider-form"]')).not.toBeNull();
    await act(async () => {
      (q('[data-testid="provider-form-save-btn"]') as HTMLButtonElement).click();
    });
    expect(q('[data-testid="provider-field-error-provider-id"]')).not.toBeNull();
    expect(q('[data-testid="provider-field-error-display-name"]')).not.toBeNull();
    expect(q('[data-testid="provider-field-error-capabilities"]')).not.toBeNull();
    expect(q('[data-testid="provider-field-error-endpoint"]')).not.toBeNull();
    expect(q('[data-testid="provider-field-error-model"]')).not.toBeNull();
    expect(invoke.mock.calls.some(([command]) => command === "settings_provider_profiles_create")).toBe(false);

    // Fill valid values → the errors clear and the payload carries ONLY the
    // G25 whitelist keys.
    await setInputValue(q('[data-testid="provider-form-provider-id"]') as HTMLInputElement, "openai");
    await setInputValue(q('[data-testid="provider-form-display-name"]') as HTMLInputElement, "第三套");
    await act(async () => {
      (q('[data-testid="provider-form-capability-OCR"]') as HTMLInputElement).click();
    });
    await setInputValue(q('[data-testid="provider-form-endpoint"]') as HTMLInputElement, "https://api.third.com/v1?x=1");
    await setInputValue(q('[data-testid="provider-form-model"]') as HTMLInputElement, "gpt-z");
    // endpoint with query is still invalid → stays highlighted
    expect(q('[data-testid="provider-field-error-endpoint"]')).not.toBeNull();
    await setInputValue(q('[data-testid="provider-form-endpoint"]') as HTMLInputElement, "https://api.third.com/v1");
    await act(async () => {
      (q('[data-testid="provider-form-save-btn"]') as HTMLButtonElement).click();
    });
    const call = invoke.mock.calls.find(([command]) => command === "settings_provider_profiles_create");
    expect(call?.[1]).toEqual({
      provider_id: "openai",
      display_name: "第三套",
      capabilities: ["OCR"],
      endpoint: "https://api.third.com/v1",
      model: "gpt-z",
      network_profile_id: null,
      enabled: true,
    });
  });

  it("a failed save keeps the draft and shows the closed conflict projection (AC4)", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="provider-new-btn"]')).not.toBeNull();
    });
    invoke.mockImplementation(async (command: string) => {
      if (command === "settings_provider_profiles_create") {
        throw "CONFLICT";
      }
      if (command === "settings_provider_profiles_list") return { profiles: [] };
      return {};
    });
    await act(async () => {
      (q('[data-testid="provider-new-btn"]') as HTMLButtonElement).click();
    });
    await setInputValue(q('[data-testid="provider-form-provider-id"]') as HTMLInputElement, "p");
    await setInputValue(q('[data-testid="provider-form-display-name"]') as HTMLInputElement, "名字保留");
    await act(async () => {
      (q('[data-testid="provider-form-capability-OCR"]') as HTMLInputElement).click();
    });
    await setInputValue(q('[data-testid="provider-form-endpoint"]') as HTMLInputElement, "https://a.b/c");
    await setInputValue(q('[data-testid="provider-form-model"]') as HTMLInputElement, "m");
    await act(async () => {
      (q('[data-testid="provider-form-save-btn"]') as HTMLButtonElement).click();
    });
    expect(q('[data-testid="provider-form-save-error"]')).not.toBeNull();
    expect(q('[data-testid="provider-form-save-error"]')?.getAttribute("data-error-category")).toBe("conflict");
    // Form still open, values intact:
    expect(q('[data-testid="provider-form"]')).not.toBeNull();
    expect((q('[data-testid="provider-form-display-name"]') as HTMLInputElement).value).toBe("名字保留");
  });

  it("delete is a two-step explicit confirmation; a still-referenced profile surfaces the conflict projection", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="provider-row-prof-a-delete-btn"]')).not.toBeNull();
    });
    await act(async () => {
      (q('[data-testid="provider-row-prof-a-delete-btn"]') as HTMLButtonElement).click();
    });
    expect(invoke.mock.calls.some(([command]) => command === "settings_provider_profiles_delete")).toBe(false);
    invoke.mockImplementation(async (command: string) => {
      if (command === "settings_provider_profiles_delete") throw "CONFLICT";
      if (command === "settings_provider_profiles_list") return { profiles: [PROFILE_A] };
      return {};
    });
    await act(async () => {
      (q('[data-testid="provider-row-prof-a-delete-confirm-btn"]') as HTMLButtonElement).click();
    });
    await vi.waitFor(() => {
      expect(q('[data-testid="provider-panel-delete-error"]')).not.toBeNull();
    });
    expect(q('[data-testid="provider-panel-delete-error"]')?.getAttribute("data-message-key")).toBe("SETTINGS_CONFLICT");
  });
});
