import { describe, expect, it, vi } from "vitest";
import { EDITABLE_SETTINGS_SECTIONS, SettingsClient } from "./client";
import type { EditableSettingsSection, InvokeFn } from "./client";

/**
 * P15 AC3 — the new G21/G22/G23 wire surface: command names pinned exactly
 * as frozen by P15-C1 §2, request payloads carrying ONLY the contract
 * fields (Secret / CredentialRef / unknown keys must structurally be absent),
 * and the sfx single-section read keeping JSON null distinguishable.
 */
describe("P15-C1 §2 frozen command names", () => {
  it("pins every new Tauri command name (rename = wire drift)", async () => {
    const { SettingsClient: SC } = await import("./client");
    void SC;
    const clientModule = await import("./client");
    expect(clientModule.SETTINGS_PROVIDER_PROFILES_LIST_COMMAND).toBe("settings_provider_profiles_list");
    expect(clientModule.SETTINGS_PROVIDER_PROFILES_CREATE_COMMAND).toBe("settings_provider_profiles_create");
    expect(clientModule.SETTINGS_PROVIDER_PROFILES_UPDATE_COMMAND).toBe("settings_provider_profiles_update");
    expect(clientModule.SETTINGS_PROVIDER_PROFILES_DELETE_COMMAND).toBe("settings_provider_profiles_delete");
    expect(clientModule.SETTINGS_PROVIDER_BINDINGS_SET_COMMAND).toBe("settings_provider_bindings_set");
    expect(clientModule.SETTINGS_PROVIDER_BINDINGS_CLEAR_COMMAND).toBe("settings_provider_bindings_clear");
    expect(clientModule.SETTINGS_PROVIDER_BINDINGS_RESOLVE_COMMAND).toBe("settings_provider_bindings_resolve");
    expect(clientModule.CREDENTIAL_PUT_COMMAND).toBe("credential_put");
    expect(clientModule.CREDENTIAL_CLEAR_COMMAND).toBe("credential_clear");
    expect(clientModule.SETTINGS_NETWORK_PROFILES_LIST_COMMAND).toBe("settings_network_profiles_list");
    expect(clientModule.SETTINGS_NETWORK_PROFILES_CREATE_COMMAND).toBe("settings_network_profiles_create");
    expect(clientModule.SETTINGS_NETWORK_PROFILES_UPDATE_COMMAND).toBe("settings_network_profiles_update");
    expect(clientModule.SETTINGS_NETWORK_PROFILES_DELETE_COMMAND).toBe("settings_network_profiles_delete");
    expect(clientModule.SETTINGS_NETWORK_PROFILES_TEST_COMMAND).toBe("settings_network_profiles_test");
    expect(clientModule.SETTINGS_NETWORK_PROFILE_DEFAULT_SET_COMMAND).toBe("settings_network_profile_default_set");
    expect(clientModule.SETTINGS_NETWORK_PROFILE_DEFAULT_CLEAR_COMMAND).toBe("settings_network_profile_default_clear");
    expect(clientModule.SETTINGS_NETWORK_PROFILE_RESOLVE_COMMAND).toBe("settings_network_profile_resolve");
  });
});

describe("G21 provider profile payloads (exact contract shape)", () => {
  it("create sends exactly the §3.2 CreateProviderProfile fields — a Secret cannot ride along", async () => {
    const invoke = vi.fn(async () => ({ profile: {} })) as unknown as InvokeFn & ReturnType<typeof vi.fn>;
    const client = new SettingsClient(invoke);
    await client.createProviderProfile({
      provider_id: "openai",
      display_name: "OpenAI 主力",
      capabilities: ["OCR", "Translation"],
      endpoint: "https://api.example.com/v1",
      model: "gpt-x",
      network_profile_id: null,
      enabled: true,
    });
    expect(invoke).toHaveBeenCalledWith("settings_provider_profiles_create", {
      provider_id: "openai",
      display_name: "OpenAI 主力",
      capabilities: ["OCR", "Translation"],
      endpoint: "https://api.example.com/v1",
      model: "gpt-x",
      network_profile_id: null,
      enabled: true,
    });
    const payload = invoke.mock.calls[0][1] as Record<string, unknown>;
    expect(Object.keys(payload).sort()).toEqual(
      ["capabilities", "display_name", "enabled", "endpoint", "model", "network_profile_id", "provider_id"].sort(),
    );
  });

  it("update sends profile_id + editable fields and never provider_id (not editable)", async () => {
    const invoke = vi.fn(async () => ({ profile: {} })) as unknown as InvokeFn & ReturnType<typeof vi.fn>;
    const client = new SettingsClient(invoke);
    await client.updateProviderProfile({
      profile_id: "prof-1",
      display_name: "改名",
      capabilities: ["Rendering"],
      endpoint: "https://api2.example.com",
      model: "m2",
      network_profile_id: "np-1",
      enabled: false,
    });
    const payload = invoke.mock.calls[0][1] as Record<string, unknown>;
    expect(payload.profile_id).toBe("prof-1");
    expect(payload).not.toHaveProperty("provider_id");
    expect(payload).not.toHaveProperty("credential_state");
    expect(payload).not.toHaveProperty("credential_hint");
  });

  it("setCapabilityBinding sends {scope, capability, profile_id} with the §3.2 scope union", async () => {
    const invoke = vi.fn(async () => ({ binding: {} })) as unknown as InvokeFn & ReturnType<typeof vi.fn>;
    const client = new SettingsClient(invoke);
    await client.setCapabilityBinding({ kind: "book", book_id: "bk-9" }, "OCR", "prof-1");
    expect(invoke).toHaveBeenCalledWith("settings_provider_bindings_set", {
      scope: { kind: "book", book_id: "bk-9" },
      capability: "OCR",
      profile_id: "prof-1",
    });
    await client.clearCapabilityBinding({ kind: "global" }, "Translation");
    expect(invoke).toHaveBeenLastCalledWith("settings_provider_bindings_clear", {
      scope: { kind: "global" },
      capability: "Translation",
    });
  });

  it("resolveCapabilityBinding sends only {capability} — no invented scope field (§3.2 shape)", async () => {
    const invoke = vi.fn(async () => ({ profile_id: null, source: null })) as unknown as InvokeFn & ReturnType<typeof vi.fn>;
    const client = new SettingsClient(invoke);
    await client.resolveCapabilityBinding("Inpaint");
    expect(invoke).toHaveBeenCalledWith("settings_provider_bindings_resolve", { capability: "Inpaint" });
  });
});

describe("G22 credential payloads (Secret-free by construction)", () => {
  it("putCredential sends exactly {target, intent} — no secret/api_key/password field exists", async () => {
    const invoke = vi.fn(async () => ({ state: "configured" })) as unknown as InvokeFn & ReturnType<typeof vi.fn>;
    const client = new SettingsClient(invoke);
    await client.putCredential({ kind: "provider_api", profile_id: "prof-1" }, "replace");
    expect(invoke).toHaveBeenCalledWith("credential_put", {
      target: { kind: "provider_api", profile_id: "prof-1" },
      intent: "replace",
    });
    const payload = invoke.mock.calls[0][1] as Record<string, unknown>;
    expect(Object.keys(payload).sort()).toEqual(["intent", "target"]);
    const forbidden = ["secret", "api_key", "password", "token", "credential_ref", "credentialRef"];
    for (const key of forbidden) {
      expect(payload).not.toHaveProperty(key);
      expect(JSON.stringify(payload).toLowerCase()).not.toContain(`${key}":`);
    }
  });

  it("clearCredential sends exactly {target}", async () => {
    const invoke = vi.fn(async () => ({ state: "missing" })) as unknown as InvokeFn & ReturnType<typeof vi.fn>;
    const client = new SettingsClient(invoke);
    await client.clearCredential({ kind: "proxy_auth", network_profile_id: "np-1" });
    expect(invoke).toHaveBeenCalledWith("credential_clear", {
      target: { kind: "proxy_auth", network_profile_id: "np-1" },
    });
  });
});

describe("G23 network profile payloads", () => {
  it("create omits optional keys when unset and includes the TLS confirmation when disabling", async () => {
    const invoke = vi.fn(async () => ({ profile: {} })) as unknown as InvokeFn & ReturnType<typeof vi.fn>;
    const client = new SettingsClient(invoke);
    await client.createNetworkProfile({
      display_name: "公司代理",
      mode: "HTTP",
      proxy_endpoint: "http://proxy.internal:8080",
    });
    expect(invoke).toHaveBeenLastCalledWith("settings_network_profiles_create", {
      display_name: "公司代理",
      mode: "HTTP",
      proxy_endpoint: "http://proxy.internal:8080",
    });

    await client.createNetworkProfile({
      display_name: "危险配置",
      mode: "SOCKS5",
      proxy_endpoint: "socks5://proxy.internal:1080",
      verify_tls: false,
      confirm_disable_tls_verification: true,
      allow_proxy_failure_direct_fallback: true,
    });
    expect(invoke).toHaveBeenLastCalledWith("settings_network_profiles_create", {
      display_name: "危险配置",
      mode: "SOCKS5",
      proxy_endpoint: "socks5://proxy.internal:1080",
      verify_tls: false,
      confirm_disable_tls_verification: true,
      allow_proxy_failure_direct_fallback: true,
    });
  });

  it("test sends {network_profile_id} alone or with provider_profile_id", async () => {
    const invoke = vi.fn(async () => ({ status: "passed", failed_stage: null, direct_fallback_used: false, stages: [] })) as unknown as InvokeFn & ReturnType<typeof vi.fn>;
    const client = new SettingsClient(invoke);
    await client.testNetworkProfile("np-1");
    expect(invoke).toHaveBeenLastCalledWith("settings_network_profiles_test", { network_profile_id: "np-1" });
    await client.testNetworkProfile("np-1", "prof-1");
    expect(invoke).toHaveBeenLastCalledWith("settings_network_profiles_test", {
      network_profile_id: "np-1",
      provider_profile_id: "prof-1",
    });
  });
});

describe("sfx single-section read keeps null distinguishable (AC3)", () => {
  it("returns null for a JSON null section and the policy for a set one", async () => {
    const invoke = vi.fn(async (_command: string, args?: Record<string, unknown>) => {
      expect(args).toEqual({ section: "sfx" });
      return { settings: { sfx: null } };
    }) as unknown as InvokeFn;
    const client = new SettingsClient(invoke);
    expect(await client.getSfxSection()).toBeNull();
  });

  it("returns the stored policy when the section is a set object", async () => {
    const invoke = vi.fn(async () => ({ settings: { sfx: { policy: "manual" } } })) as unknown as InvokeFn;
    const client = new SettingsClient(invoke);
    expect(await client.getSfxSection()).toBe("manual");
  });

  it("collapses an empty object (no policy key) to null-as-unset — {} is NOT null, policy absent falls back", async () => {
    const invoke = vi.fn(async () => ({ settings: { sfx: {} } })) as unknown as InvokeFn;
    const client = new SettingsClient(invoke);
    // The section exists but carries no policy: the effective policy is the
    // Core default; the UI treats "no usable value" the same as unset for
    // the draft, while the wire shape itself stays distinguishable above.
    expect(await client.getSfxSection()).toBeNull();
  });
});

describe("no untyped settings_update_section passthrough beyond the frozen section API", () => {
  it("the client exposes only the pinned sfx builder plus the frozen section pair", () => {
    const client = new SettingsClient(async () => ({}));
    const clientAny = client as unknown as Record<string, unknown>;
    // No unspecified-name arbitrary update method exists: the only generic
    // write surface is the named `saveSection(section, values)` added by
    // SETTINGS-OPEN-A-1, whose key-level whitelist/range validation lives in
    // the Core (settings.update_section) — never in an untyped passthrough.
    expect(typeof clientAny.updateSection).toBe("undefined");
    expect(typeof clientAny.saveSection).toBe("function");
    expect(typeof clientAny.saveSfxPolicy).toBe("function");
    // m2（review r1）: the section argument is the frozen compile-time union —
    // the runtime mirror must stay exactly the batch-A + sfx whitelist.
    expect(EDITABLE_SETTINGS_SECTIONS).toEqual(["ocr", "translate", "inpaint", "typeset", "sfx"]);
    // The sfx channel still writes exactly "sfx" with {policy} — pinned by the
    // pre-existing client.test.ts.
  });

  it("arbitrary section names are a COMPILE-TIME error, not a runtime convention (m2 guard)", () => {
    const client = new SettingsClient(async () => ({}));
    // These lines are checked by `tsc --noEmit`, not by the vitest runtime:
    // if the section parameter widened back to `string`, the @ts-expect-error
    // directives would become unused and tsc would fail. The closures are
    // never invoked, so no wire call happens.
    // @ts-expect-error — "bogus_section" is outside EditableSettingsSection
    void (() => client.saveSection("bogus_section", {}));
    // @ts-expect-error — same closed union for reads
    void (() => client.getSection("bogus_section"));
    // Positive control: every frozen member stays assignable.
    const accepted: EditableSettingsSection[] = [...EDITABLE_SETTINGS_SECTIONS];
    expect(accepted).toHaveLength(5);
  });
});
