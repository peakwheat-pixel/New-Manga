import { JSDOM } from "jsdom";
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { SettingsClient } from "./client";
import { setNativeInputValue, setNativeSelectValue } from "../testSupport/jsdomEvents";
import { NetworkProfilePanel } from "./NetworkProfilePanel";
import type { NetworkProfile, NetworkTestResult } from "./types";

/**
 * P15 AC2/AC4 — G23 Network Profile panel: the TLS danger confirmation
 * gate (disable is never silent), the default-false direct fallback, the
 * mode/endpoint combination rules, and the closed staged-test projection
 * (all six stages, direct_fallback_used constantly false).
 */

const NP_DIRECT: NetworkProfile = {
  network_profile_id: "np-direct",
  display_name: "直连",
  mode: "Direct",
  proxy_endpoint: null,
  verify_tls: true,
  tls_verification_state: "enabled",
  allow_proxy_failure_direct_fallback: false,
  credential_state: "missing",
};

const NP_SOCKS: NetworkProfile = {
  network_profile_id: "np-socks",
  display_name: "SOCKS 代理",
  mode: "SOCKS5",
  proxy_endpoint: "socks5://proxy.internal:1080",
  verify_tls: false,
  tls_verification_state: "disabled_confirmed",
  allow_proxy_failure_direct_fallback: false,
  credential_state: "missing",
};

const TEST_FAILED_AT_TLS: NetworkTestResult = {
  status: "failed",
  failed_stage: "TLS",
  direct_fallback_used: false,
  stages: [
    { stage: "Proxy", status: "passed", duration_ms: 12 },
    { stage: "DNS", status: "passed", duration_ms: 3 },
    { stage: "TCP", status: "passed", duration_ms: 20 },
    {
      stage: "TLS",
      status: "failed",
      failure: { category: "unavailable", action: "review_tls_setting", message_key: "NETWORK_STAGE_FAILED" },
      duration_ms: 45,
    },
    { stage: "HTTP", status: "not_run", reason: "upstream_stage_failed" },
    { stage: "ProviderAuth", status: "not_run", reason: "upstream_stage_failed" },
  ],
};

function makeDom() {
  const dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
  const container = dom.window.document.createElement("div");
  dom.window.document.body.appendChild(container);
  return { dom, container };
}

describe("NetworkProfilePanel (G23)", () => {
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
      if (command === "settings_network_profiles_list") {
        return { profiles: [NP_DIRECT, NP_SOCKS] };
      }
      if (command === "settings_provider_profiles_list") {
        return { profiles: [] };
      }
      if (command === "settings_network_profile_resolve") {
        return { network_profile_id: null, mode: "Direct", source: "direct" };
      }
      return {};
    });
    root = createRoot(container);
    act(() => {
      root.render(<NetworkProfilePanel client={new SettingsClient(invoke)} />);
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

  it("lists profiles and makes the TLS state visible (disabled_confirmed is shown, not hidden)", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="network-row-np-socks"]')).not.toBeNull();
    });
    expect(q('[data-testid="network-row-np-direct-tls"]')?.textContent).toContain("开启");
    expect(q('[data-testid="network-row-np-socks-tls"]')?.textContent).toContain("已关闭（经危险确认）");
    expect(q('[data-testid="network-row-np-socks"]')?.textContent).toContain("关闭（默认）");
  });

  it("requires an explicit danger confirmation before TLS verification may be turned off (AC4/boundary 5)", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="network-new-btn"]')).not.toBeNull();
    });
    await act(async () => {
      (q('[data-testid="network-new-btn"]') as HTMLButtonElement).click();
    });
    const tlsCheckbox = q('[data-testid="network-form-verify-tls"]') as HTMLInputElement;
    expect(tlsCheckbox.checked).toBe(true);
    await act(async () => {
      tlsCheckbox.click();
    });
    expect(q('[data-testid="network-form-tls-danger"]')).not.toBeNull();
    // Without confirmation the save stays disabled:
    expect((q('[data-testid="network-form-save-btn"]') as HTMLButtonElement).disabled).toBe(true);
    // With the explicit confirmation it submits confirm_disable_tls_verification:
    await act(async () => {
      (q('[data-testid="network-form-tls-danger-confirm"]') as HTMLInputElement).click();
    });
    expect((q('[data-testid="network-form-save-btn"]') as HTMLButtonElement).disabled).toBe(false);
    await setInputValue(q('[data-testid="network-form-display-name"]') as HTMLInputElement, "危险代理");
    await setSelectValue(q('[data-testid="network-form-mode"]') as HTMLSelectElement, "HTTPS");
    await setInputValue(q('[data-testid="network-form-proxy-endpoint"]') as HTMLInputElement, "https://proxy.internal:8443");
    await act(async () => {
      (q('[data-testid="network-form-save-btn"]') as HTMLButtonElement).click();
    });
    const call = invoke.mock.calls.find(([command]) => command === "settings_network_profiles_create");
    expect(call?.[1]).toEqual({
      display_name: "危险代理",
      mode: "HTTPS",
      proxy_endpoint: "https://proxy.internal:8443",
      verify_tls: false,
      confirm_disable_tls_verification: true,
      allow_proxy_failure_direct_fallback: false,
    });
  });

  it("Direct mode forbids an endpoint (input disabled, payload sends null) and defaults the fallback to false", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="network-new-btn"]')).not.toBeNull();
    });
    await act(async () => {
      (q('[data-testid="network-new-btn"]') as HTMLButtonElement).click();
    });
    expect((q('[data-testid="network-form-proxy-endpoint"]') as HTMLInputElement).disabled).toBe(true);
    expect((q('[data-testid="network-form-fallback"]') as HTMLInputElement).checked).toBe(false);
    await setInputValue(q('[data-testid="network-form-display-name"]') as HTMLInputElement, "直连默认");
    await act(async () => {
      (q('[data-testid="network-form-save-btn"]') as HTMLButtonElement).click();
    });
    const call = invoke.mock.calls.find(([command]) => command === "settings_network_profiles_create");
    expect(call?.[1]).toEqual({
      display_name: "直连默认",
      mode: "Direct",
      proxy_endpoint: null,
      allow_proxy_failure_direct_fallback: false,
    });
  });

  it("rejects a mode-mismatched proxy endpoint with a field-level message before any wire call", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="network-new-btn"]')).not.toBeNull();
    });
    await act(async () => {
      (q('[data-testid="network-new-btn"]') as HTMLButtonElement).click();
    });
    await setInputValue(q('[data-testid="network-form-display-name"]') as HTMLInputElement, "错配");
    await setSelectValue(q('[data-testid="network-form-mode"]') as HTMLSelectElement, "SOCKS5");
    await setInputValue(q('[data-testid="network-form-proxy-endpoint"]') as HTMLInputElement, "http://proxy.internal:1080");
    await act(async () => {
      (q('[data-testid="network-form-save-btn"]') as HTMLButtonElement).click();
    });
    expect(q('[data-testid="network-field-error-proxy-endpoint"]')?.textContent).toContain("scheme 必须与 SOCKS5 模式一致");
    expect(invoke.mock.calls.some(([command]) => command === "settings_network_profiles_create")).toBe(false);
  });

  it("shows the staged test result with all six stages and no silent direct fallback", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="network-row-np-socks-test-btn"]')).not.toBeNull();
    });
    invoke.mockImplementation(async (command: string) => {
      if (command === "settings_network_profiles_test") return TEST_FAILED_AT_TLS;
      if (command === "settings_network_profiles_list") return { profiles: [NP_SOCKS] };
      return {};
    });
    await act(async () => {
      (q('[data-testid="network-row-np-socks-test-btn"]') as HTMLButtonElement).click();
    });
    await vi.waitFor(() => {
      expect(q('[data-testid="network-test-result-np-socks"]')).not.toBeNull();
    });
    const result = q('[data-testid="network-test-result-np-socks"]');
    expect(result?.textContent).toContain("失败");
    expect(result?.textContent).toContain("TLS");
    expect(q('[data-testid="network-test-result-np-socks-fallback"]')?.textContent).toContain("direct_fallback_used=false");
    const stages = q('[data-testid="network-test-result-np-socks-stages"]');
    for (const stage of ["Proxy", "DNS", "TCP", "TLS", "HTTP", "ProviderAuth"]) {
      expect(stages?.textContent).toContain(stage);
    }
    expect(stages?.textContent).toContain("未执行（upstream_stage_failed）");
  });

  it("failed save keeps the draft (AC4) and shows the closed projection", async () => {
    await vi.waitFor(() => {
      expect(q('[data-testid="network-new-btn"]')).not.toBeNull();
    });
    invoke.mockImplementation(async (command: string) => {
      if (command === "settings_network_profiles_create") throw "CONFLICT";
      if (command === "settings_network_profiles_list") return { profiles: [] };
      return {};
    });
    await act(async () => {
      (q('[data-testid="network-new-btn"]') as HTMLButtonElement).click();
    });
    await setInputValue(q('[data-testid="network-form-display-name"]') as HTMLInputElement, "保留草稿");
    await act(async () => {
      (q('[data-testid="network-form-save-btn"]') as HTMLButtonElement).click();
    });
    expect(q('[data-testid="network-form-save-error"]')).not.toBeNull();
    expect(q('[data-testid="network-form-save-error"]')?.getAttribute("data-error-category")).toBe("conflict");
    expect(q('[data-testid="network-form"]')).not.toBeNull();
    expect((q('[data-testid="network-form-display-name"]') as HTMLInputElement).value).toBe("保留草稿");
  });
});
