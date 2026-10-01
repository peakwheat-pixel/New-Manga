/**
 * SettingsClient — the React-side consumer of the settings read/write
 * channel (M2-SETTINGS-UI-SFX-POLICY).
 *
 * BLOCKED_ON_CONTRACT (AC1 survey, 2026-10-01): the production Tauri
 * surface (src-tauri/src/main.rs `generate_handler!`, production arm)
 * currently registers exactly five commands — issue_resource_url,
 * revoke_ref, revoke_resource_refs, core_ping, library_list_books — and
 * NONE of them reads or writes settings. There is no generic
 * settings get/update channel and no per-key command. Adding one is a
 * frozen-contract change (doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md owns
 * the React↔Tauri↔Python message boundary), so per the Task's AC1 ruling
 * this Task stops short of any Rust change and runs against a MOCKED
 * invoke channel only.
 *
 * The command names below are this Task's PROPOSED wire names for the
 * integrator's contract ruling; the Python Core side already has the
 * storage authority with zero changes needed:
 *   read  → PipelineDefaultsService.read().settings["sfx"]["policy"]
 *   write → PipelineDefaultsService.save_settings_section("sfx", {"policy": ...})
 * (src/application/settings/pipeline_defaults.py:59/105; key semantics
 * from M2-SFX-TRANSLATE-ENTRY).
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

/** PROPOSED wire name (BLOCKED_ON_CONTRACT — pending integrator ruling). */
export const SETTINGS_GET_COMMAND = "settings_get";

/** PROPOSED wire name (BLOCKED_ON_CONTRACT — pending integrator ruling). */
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
 * The shape this Task PROPOSES for `settings_get`'s result: the
 * PipelineDefaults.settings projection as JSON (e.g.
 * `{"sfx": {"policy": "skip"}, "ocr": {"script": "..."}}`). Only the
 * `sfx.policy` leaf is consumed here.
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
