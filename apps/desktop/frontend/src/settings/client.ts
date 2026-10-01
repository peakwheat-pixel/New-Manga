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

export class SettingsClientError extends Error {
  code: string;

  constructor(code: string, message?: string) {
    super(message || code);
    this.name = "SettingsClientError";
    this.code = code;
  }
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
      const code = typeof error === "string" ? error : (error as Error)?.message || "SETTINGS_UNAVAILABLE";
      throw new SettingsClientError(code, `settings_get failed: ${code}`);
    }
  }

  /** Persist one SFX policy value via the section-update channel. */
  async saveSfxPolicy(policy: SfxPolicy): Promise<void> {
    try {
      await this.invoke(SETTINGS_UPDATE_SECTION_COMMAND, buildSfxPolicySection(policy));
    } catch (error) {
      const code = typeof error === "string" ? error : (error as Error)?.message || "SETTINGS_SAVE_FAILED";
      throw new SettingsClientError(code, `settings_update_section failed: ${code}`);
    }
  }
}
