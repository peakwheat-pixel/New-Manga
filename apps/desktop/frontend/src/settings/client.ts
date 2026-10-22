/**
 * SettingsClient — the React-side consumer of the settings read/write
 * channel (M2-SETTINGS-UI-SFX-POLICY UI + M2-SETTINGS-IPC-CHANNEL channel).
 *
 * CHANNEL LANDED (was BLOCKED_ON_CONTRACT): the production Tauri surface now
 * registers the pinned commands — settings_get / settings_update_section
 * (contract M2-C1 rev 1.3 §5.3, user ruling ① 2026-10-02) — riding the same
 * production stdio bridge as core_ping/library_list_books down to the Python
 * Core. This client's invoke wiring is the REAL channel (an invoke fn can
 * still be injected for tests); the command names below are the RULED wire
 * names, previously pinned here as the drift alarm.
 *
 * Core-side authority (zero UI-side interpretation):
 *   read  → PipelineDefaultsService.read().settings["sfx"]["policy"]
 *   write → PipelineDefaultsService.save_settings_section("sfx", {"policy": ...})
 * (src/application/settings/pipeline_defaults.py:59/105; write-side
 * validation is typed fail-closed BEFORE persistence — the sfx.policy
 * three-value gate — per the M2-SFX-ENTRY r1 R4 lesson; key semantics from
 * M2-SFX-TRANSLATE-ENTRY).
 */

import {
  DEFAULT_SFX_POLICY,
  isSfxPolicy,
  type Capability,
  type CapabilityBinding,
  type BindingScope,
  type CredentialIntent,
  type CredentialTarget,
  type NetworkProfile,
  type NetworkProfileInput,
  type NetworkProfileUpdateInput,
  type NetworkTestResult,
  type ProviderProfile,
  type ProviderProfileInput,
  type ProviderProfileUpdateInput,
  type ResolvedNetworkProfile,
  type SfxPolicy,
} from "./types";

export type InvokeFn = (command: string, args?: Record<string, unknown>) => Promise<unknown>;

function getTauriInvoke(): InvokeFn {
  const globalWindow = typeof window !== "undefined"
    ? (window as unknown as { __TAURI__?: { core?: { invoke: InvokeFn } } })
    : undefined;
  const invoke = globalWindow?.__TAURI__?.core?.invoke;
  if (!invoke) {
    throw new Error("TAURI_BRIDGE_MISSING");
  }
  return invoke;
}

/** RULED wire name (contract M2-C1 rev 1.3 §5.3; was the pinned proposal). */
export const SETTINGS_GET_COMMAND = "settings_get";

/** RULED wire name (contract M2-C1 rev 1.3 §5.3; was the pinned proposal). */
export const SETTINGS_UPDATE_SECTION_COMMAND = "settings_update_section";

/** The settings section this Task touches (Python: settings["sfx"]). */
export const SFX_SECTION = "sfx";

/**
 * SETTINGS-OPEN-A-1 m2（review r1）— the closed set of sections addressable
 * through the generic section read/write pair: the four batch-A sections
 * frozen by doc/design/SETTINGS_SECTION_SCHEMAS.md §3 plus the pre-existing
 * `sfx` section. Sections outside this union are a COMPILE-TIME error; the
 * Core stays fail-closed for unknown sections, but the UI must not even be
 * able to express one.
 */
export type EditableSettingsSection = "ocr" | "translate" | "inpaint" | "typeset" | "sfx";

/** Runtime mirror of {@link EditableSettingsSection} — a drift alarm pinned
 * in the structural guard test; never iterated to build requests. */
export const EDITABLE_SETTINGS_SECTIONS: readonly EditableSettingsSection[] = [
  "ocr",
  "translate",
  "inpaint",
  "typeset",
  "sfx",
] as const;

/* P15-C1 §2 — the frozen production-only Tauri command names for the new
 * settings surface. Pinned as constants exactly like the settings_get pair
 * above: renaming any of them is a wire drift. The runtime host registers
 * them when it pairs with Core protocol 2.6; until then invoking them fails
 * and the UI shows the closed §9 projection. */
export const SETTINGS_PROVIDER_PROFILES_LIST_COMMAND = "settings_provider_profiles_list";
export const SETTINGS_PROVIDER_PROFILES_CREATE_COMMAND = "settings_provider_profiles_create";
export const SETTINGS_PROVIDER_PROFILES_UPDATE_COMMAND = "settings_provider_profiles_update";
export const SETTINGS_PROVIDER_PROFILES_DELETE_COMMAND = "settings_provider_profiles_delete";
export const SETTINGS_PROVIDER_BINDINGS_SET_COMMAND = "settings_provider_bindings_set";
export const SETTINGS_PROVIDER_BINDINGS_CLEAR_COMMAND = "settings_provider_bindings_clear";
export const SETTINGS_PROVIDER_BINDINGS_RESOLVE_COMMAND = "settings_provider_bindings_resolve";
export const CREDENTIAL_PUT_COMMAND = "credential_put";
export const CREDENTIAL_CLEAR_COMMAND = "credential_clear";
export const SETTINGS_NETWORK_PROFILES_LIST_COMMAND = "settings_network_profiles_list";
export const SETTINGS_NETWORK_PROFILES_CREATE_COMMAND = "settings_network_profiles_create";
export const SETTINGS_NETWORK_PROFILES_UPDATE_COMMAND = "settings_network_profiles_update";
export const SETTINGS_NETWORK_PROFILES_DELETE_COMMAND = "settings_network_profiles_delete";
export const SETTINGS_NETWORK_PROFILES_TEST_COMMAND = "settings_network_profiles_test";
export const SETTINGS_NETWORK_PROFILE_DEFAULT_SET_COMMAND = "settings_network_profile_default_set";
export const SETTINGS_NETWORK_PROFILE_DEFAULT_CLEAR_COMMAND = "settings_network_profile_default_clear";
export const SETTINGS_NETWORK_PROFILE_RESOLVE_COMMAND = "settings_network_profile_resolve";

export class SettingsClientError extends Error {
  code: string;

  constructor(code: string, message?: string) {
    super(message || code);
    this.name = "SettingsClientError";
    this.code = code;
  }
}

/**
 * Extract a stable error code from a rejected invoke: the channel may throw
 * a plain string, an {code} envelope (M2-C1 §8), or an Error. The message
 * text is only a fallback code source — callers render the closed §9
 * projection, never this raw value.
 */
function extractErrorCode(error: unknown, fallback: string): string {
  if (typeof error === "string") return error;
  if (error && typeof error === "object") {
    const obj = error as { code?: unknown; message?: unknown };
    if (typeof obj.code === "string" && obj.code !== "") return obj.code;
    if (typeof obj.message === "string" && obj.message !== "") return obj.message;
  }
  return fallback;
}

/**
 * The wire shape of `settings_get`'s result (contract M2-C1 rev 1.3 §5.3):
 * the PipelineDefaults.settings projection as JSON (e.g.
 * `{"settings": {"sfx": {"policy": "skip"}, "ocr": {"script": "..."}}}`).
 * Only the `sfx.policy` leaf is consumed here.
 */
export interface SettingsProjection {
  settings?: Record<string, Record<string, unknown>>;
}

/** Extract the effective SFX policy from a settings projection.
 * Unset or illegal values collapse to the Core default (skip) — the Core
 * remains the fail-fast authority for illegal values it is actually given. */
export function sfxPolicyFromProjection(
  projection: SettingsProjection | null | undefined,
): SfxPolicy {
  const policy = projection?.settings?.sfx?.policy;
  return isSfxPolicy(policy) ? policy : DEFAULT_SFX_POLICY;
}

/** The exact update payload for one SFX policy save, so the wire shape is
 * unit-pinned in one place (mirrors save_settings_section("sfx", {...})). */
export function buildSfxPolicySection(policy: SfxPolicy): {
  section: string;
  values: Record<string, unknown>;
} {
  return { section: SFX_SECTION, values: { policy } };
}

export class SettingsClient {
  private invoke: InvokeFn;

  constructor(invoke?: InvokeFn) {
    this.invoke = invoke || getTauriInvoke();
  }

  /** Read the effective SFX policy (missing/illegal → Core default). */
  async getSfxPolicy(): Promise<SfxPolicy> {
    try {
      const res = (await this.invoke(SETTINGS_GET_COMMAND)) as SettingsProjection;
      return sfxPolicyFromProjection(res);
    } catch (error) {
      const code = extractErrorCode(error, "SETTINGS_UNAVAILABLE");
      throw new SettingsClientError(code, `settings_get failed: ${code}`);
    }
  }

  /** Persist one SFX policy value via the section-update channel. */
  async saveSfxPolicy(policy: SfxPolicy): Promise<void> {
    try {
      await this.invoke(SETTINGS_UPDATE_SECTION_COMMAND, buildSfxPolicySection(policy));
    } catch (error) {
      const code = extractErrorCode(error, "SETTINGS_SAVE_FAILED");
      throw new SettingsClientError(code, `settings_update_section failed: ${code}`);
    }
  }

  /**
   * P15 AC3 — null vs empty-object must stay distinguishable. Reads the
   * single `sfx` section; a JSON null result means "section not set", an
   * object means "set" (its policy may still fall back to the Core default
   * when absent/illegal).
   */
  async getSfxSection(): Promise<SfxPolicy | null> {
    try {
      const res = (await this.invoke(SETTINGS_GET_COMMAND, { section: SFX_SECTION })) as {
        settings?: { sfx?: unknown };
      };
      const section = res?.settings?.sfx;
      if (section === null || section === undefined) {
        // frozen-None: JSON null = section unset; a missing key is treated
        // the same way (still "not set", never an empty-object stand-in).
        return null;
      }
      const policy = (section as { policy?: unknown }).policy;
      return isSfxPolicy(policy) ? policy : null;
    } catch (error) {
      const code = extractErrorCode(error, "SETTINGS_UNAVAILABLE");
      throw new SettingsClientError(code, `settings_get(section) failed: ${code}`);
    }
  }

  /* ---------------- SETTINGS-OPEN-A-1: generic section read/write ---------------- */

  /**
   * Generic single-section read over the frozen `settings_get` channel
   * (request shape `{section}`; same wire as getSfxSection). A JSON null — or
   * a missing key, which the projection treats the same way — returns null so
   * callers can render the explicit "未设置" affordance instead of inventing
   * values. Non-object payloads fail closed to null: the Core is the authority
   * for each section's shape, the UI never guesses.
   *
   * `section` is the frozen {@link EditableSettingsSection} union (m2): an
   * arbitrary section name is a compile error, not a runtime convention.
   */
  async getSection<T>(section: EditableSettingsSection): Promise<T | null> {
    try {
      const res = (await this.invoke(SETTINGS_GET_COMMAND, { section })) as {
        settings?: Record<string, unknown>;
      };
      const value = res?.settings?.[section];
      if (value === null || value === undefined) {
        return null;
      }
      if (typeof value !== "object" || Array.isArray(value)) {
        return null;
      }
      return value as T;
    } catch (error) {
      const code = extractErrorCode(error, "SETTINGS_UNAVAILABLE");
      throw new SettingsClientError(code, `settings_get(section) failed: ${code}`);
    }
  }

  /**
   * Generic whole-section upsert over the frozen `settings_update_section`
   * channel: exactly `{section, values}` — the mirror of the Core's
   * `save_settings_section(section, values)`. Key-level whitelist/value-domain
   * validation stays in the Core (SettingsRequestError → INVALID_REQUEST);
   * this client only preserves the closed error projection.
   *
   * `section` is the frozen {@link EditableSettingsSection} union (m2): the
   * UI cannot express a section outside the batch-A + sfx whitelist.
   */
  async saveSection(
    section: EditableSettingsSection,
    values: Record<string, unknown>,
  ): Promise<void> {
    try {
      await this.invoke(SETTINGS_UPDATE_SECTION_COMMAND, { section, values });
    } catch (error) {
      const code = extractErrorCode(error, "SETTINGS_SAVE_FAILED");
      throw new SettingsClientError(code, `settings_update_section failed: ${code}`);
    }
  }

  /* ---------------- G21: Provider Profiles + Capability bindings ---------------- */

  async listProviderProfiles(): Promise<ProviderProfile[]> {
    try {
      const res = (await this.invoke(SETTINGS_PROVIDER_PROFILES_LIST_COMMAND)) as { profiles?: unknown };
      return Array.isArray(res?.profiles) ? (res.profiles as ProviderProfile[]) : [];
    } catch (error) {
      throw toClientError(error, SETTINGS_PROVIDER_PROFILES_LIST_COMMAND);
    }
  }

  async createProviderProfile(input: ProviderProfileInput): Promise<ProviderProfile> {
    try {
      const res = (await this.invoke(SETTINGS_PROVIDER_PROFILES_CREATE_COMMAND, {
        provider_id: input.provider_id,
        display_name: input.display_name,
        capabilities: input.capabilities,
        endpoint: input.endpoint,
        model: input.model,
        network_profile_id: input.network_profile_id,
        enabled: input.enabled,
      })) as { profile: ProviderProfile };
      return res.profile;
    } catch (error) {
      throw toClientError(error, SETTINGS_PROVIDER_PROFILES_CREATE_COMMAND);
    }
  }

  async updateProviderProfile(input: ProviderProfileUpdateInput): Promise<ProviderProfile> {
    try {
      const res = (await this.invoke(SETTINGS_PROVIDER_PROFILES_UPDATE_COMMAND, {
        profile_id: input.profile_id,
        display_name: input.display_name,
        capabilities: input.capabilities,
        endpoint: input.endpoint,
        model: input.model,
        network_profile_id: input.network_profile_id,
        enabled: input.enabled,
      })) as { profile: ProviderProfile };
      return res.profile;
    } catch (error) {
      throw toClientError(error, SETTINGS_PROVIDER_PROFILES_UPDATE_COMMAND);
    }
  }

  async deleteProviderProfile(profileId: string): Promise<void> {
    try {
      await this.invoke(SETTINGS_PROVIDER_PROFILES_DELETE_COMMAND, { profile_id: profileId });
    } catch (error) {
      throw toClientError(error, SETTINGS_PROVIDER_PROFILES_DELETE_COMMAND);
    }
  }

  async setCapabilityBinding(
    scope: BindingScope,
    capability: Capability,
    profileId: string,
  ): Promise<CapabilityBinding> {
    try {
      const res = (await this.invoke(SETTINGS_PROVIDER_BINDINGS_SET_COMMAND, {
        scope,
        capability,
        profile_id: profileId,
      })) as { binding: CapabilityBinding };
      return res.binding;
    } catch (error) {
      throw toClientError(error, SETTINGS_PROVIDER_BINDINGS_SET_COMMAND);
    }
  }

  async clearCapabilityBinding(scope: BindingScope, capability: Capability): Promise<void> {
    try {
      await this.invoke(SETTINGS_PROVIDER_BINDINGS_CLEAR_COMMAND, { scope, capability });
    } catch (error) {
      throw toClientError(error, SETTINGS_PROVIDER_BINDINGS_CLEAR_COMMAND);
    }
  }

  /**
   * Read the current binding for one capability. Request shape is exactly
   * `ResolveCapabilityBinding { capability }` (contract §3.2): omitting
   * book/chapter/run context resolves against the current persistent
   * settings; unknown fields would be rejected, so none are added.
   */
  async resolveCapabilityBinding(
    capability: Capability,
  ): Promise<{ profile_id: string | null; source: unknown }> {
    try {
      const res = (await this.invoke(SETTINGS_PROVIDER_BINDINGS_RESOLVE_COMMAND, {
        capability,
      })) as { profile_id: string | null; source: unknown };
      return { profile_id: res?.profile_id ?? null, source: res?.source ?? null };
    } catch (error) {
      throw toClientError(error, SETTINGS_PROVIDER_BINDINGS_RESOLVE_COMMAND);
    }
  }

  /* ---------------- G22: one-shot credential operations ---------------- */

  /**
   * Ask the Host to open its secure input for the given target. The WebView
   * payload carries ONLY (target, intent) — never a Secret, password, or
   * CredentialRef (contract §4.1).
   */
  async putCredential(
    target: CredentialTarget,
    intent: CredentialIntent,
  ): Promise<{ state: "configured"; masked_hint?: string }> {
    try {
      return (await this.invoke(CREDENTIAL_PUT_COMMAND, { target, intent })) as {
        state: "configured";
        masked_hint?: string;
      };
    } catch (error) {
      throw toClientError(error, CREDENTIAL_PUT_COMMAND);
    }
  }

  async clearCredential(target: CredentialTarget): Promise<{ state: "missing" }> {
    try {
      return (await this.invoke(CREDENTIAL_CLEAR_COMMAND, { target })) as { state: "missing" };
    } catch (error) {
      throw toClientError(error, CREDENTIAL_CLEAR_COMMAND);
    }
  }

  /* ---------------- G23: Network Profiles ---------------- */

  async listNetworkProfiles(): Promise<NetworkProfile[]> {
    try {
      const res = (await this.invoke(SETTINGS_NETWORK_PROFILES_LIST_COMMAND)) as { profiles?: unknown };
      return Array.isArray(res?.profiles) ? (res.profiles as NetworkProfile[]) : [];
    } catch (error) {
      throw toClientError(error, SETTINGS_NETWORK_PROFILES_LIST_COMMAND);
    }
  }

  async createNetworkProfile(input: NetworkProfileInput): Promise<NetworkProfile> {
    try {
      const res = (await this.invoke(SETTINGS_NETWORK_PROFILES_CREATE_COMMAND, {
        display_name: input.display_name,
        mode: input.mode,
        proxy_endpoint: input.proxy_endpoint,
        ...(input.verify_tls !== undefined ? { verify_tls: input.verify_tls } : {}),
        ...(input.confirm_disable_tls_verification !== undefined
          ? { confirm_disable_tls_verification: input.confirm_disable_tls_verification }
          : {}),
        ...(input.allow_proxy_failure_direct_fallback !== undefined
          ? { allow_proxy_failure_direct_fallback: input.allow_proxy_failure_direct_fallback }
          : {}),
      })) as { profile: NetworkProfile };
      return res.profile;
    } catch (error) {
      throw toClientError(error, SETTINGS_NETWORK_PROFILES_CREATE_COMMAND);
    }
  }

  async updateNetworkProfile(input: NetworkProfileUpdateInput): Promise<NetworkProfile> {
    try {
      const res = (await this.invoke(SETTINGS_NETWORK_PROFILES_UPDATE_COMMAND, {
        network_profile_id: input.network_profile_id,
        display_name: input.display_name,
        mode: input.mode,
        proxy_endpoint: input.proxy_endpoint,
        verify_tls: input.verify_tls,
        ...(input.confirm_disable_tls_verification !== undefined
          ? { confirm_disable_tls_verification: input.confirm_disable_tls_verification }
          : {}),
        allow_proxy_failure_direct_fallback: input.allow_proxy_failure_direct_fallback,
      })) as { profile: NetworkProfile };
      return res.profile;
    } catch (error) {
      throw toClientError(error, SETTINGS_NETWORK_PROFILES_UPDATE_COMMAND);
    }
  }

  async deleteNetworkProfile(networkProfileId: string): Promise<void> {
    try {
      await this.invoke(SETTINGS_NETWORK_PROFILES_DELETE_COMMAND, {
        network_profile_id: networkProfileId,
      });
    } catch (error) {
      throw toClientError(error, SETTINGS_NETWORK_PROFILES_DELETE_COMMAND);
    }
  }

  async testNetworkProfile(
    networkProfileId: string,
    providerProfileId?: string,
  ): Promise<NetworkTestResult> {
    try {
      const res = (await this.invoke(SETTINGS_NETWORK_PROFILES_TEST_COMMAND, {
        network_profile_id: networkProfileId,
        ...(providerProfileId !== undefined ? { provider_profile_id: providerProfileId } : {}),
      })) as NetworkTestResult;
      return res;
    } catch (error) {
      throw toClientError(error, SETTINGS_NETWORK_PROFILES_TEST_COMMAND);
    }
  }

  async setGlobalNetworkProfile(networkProfileId: string): Promise<string> {
    try {
      const res = (await this.invoke(SETTINGS_NETWORK_PROFILE_DEFAULT_SET_COMMAND, {
        network_profile_id: networkProfileId,
      })) as { network_profile_id: string };
      return res.network_profile_id;
    } catch (error) {
      throw toClientError(error, SETTINGS_NETWORK_PROFILE_DEFAULT_SET_COMMAND);
    }
  }

  async clearGlobalNetworkProfile(): Promise<void> {
    try {
      await this.invoke(SETTINGS_NETWORK_PROFILE_DEFAULT_CLEAR_COMMAND);
    } catch (error) {
      throw toClientError(error, SETTINGS_NETWORK_PROFILE_DEFAULT_CLEAR_COMMAND);
    }
  }

  async resolveNetworkProfile(): Promise<ResolvedNetworkProfile> {
    try {
      return (await this.invoke(SETTINGS_NETWORK_PROFILE_RESOLVE_COMMAND)) as ResolvedNetworkProfile;
    } catch (error) {
      throw toClientError(error, SETTINGS_NETWORK_PROFILE_RESOLVE_COMMAND);
    }
  }
}

function toClientError(error: unknown, command: string): SettingsClientError {
  const code = extractErrorCode(error, "SETTINGS_UNAVAILABLE");
  return new SettingsClientError(code, `${command} failed: ${code}`);
}
