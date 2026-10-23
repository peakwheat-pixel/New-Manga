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
 * The closed set of sections addressable through the generic section
 * read/write pair: the four batch-A sections frozen by
 * doc/design/SETTINGS_SECTION_SCHEMAS.md §3, the pre-existing `sfx` section,
 * and — SETTINGS-OPEN-B-1 — the two batch-B-1 sections frozen by §4.1/§4.2
 * (`model_gpu`, `tasks`). Sections outside this union are a COMPILE-TIME
 * error; the Core stays fail-closed for unknown sections, but the UI must not
 * even be able to express one.
 */
export type EditableSettingsSection =
  | "ocr"
  | "translate"
  | "inpaint"
  | "typeset"
  | "sfx"
  | "model_gpu"
  | "tasks";

/** Runtime mirror of {@link EditableSettingsSection} — a drift alarm pinned
 * in the structural guard test; never iterated to build requests. */
export const EDITABLE_SETTINGS_SECTIONS: readonly EditableSettingsSection[] = [
  "ocr",
  "translate",
  "inpaint",
  "typeset",
  "sfx",
  "model_gpu",
  "tasks",
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

/* SETTINGS-OPEN-B-2 §4.3 — the frozen payload-free cleanup command names
 * (`cleanup_preview` / `cleanup_run` / `cleanup_retry_pending`). Same
 * pinned-constant discipline as the settings pair above: renaming any of them
 * is a wire drift, and none of them takes an argument object. */
export const CLEANUP_PREVIEW_COMMAND = "cleanup_preview";
export const CLEANUP_RUN_COMMAND = "cleanup_run";
export const CLEANUP_RETRY_PENDING_COMMAND = "cleanup_retry_pending";

/* SETTINGS-OPEN-C-2-BACKUP §3.4 — the frozen `.nmbak` package command names.
 * `backup_create` takes no target directory (the Core owns the backup root),
 * `backup_restore` carries the id + the explicit `confirm_restore`, and every
 * name is a pinned constant: renaming one is wire drift. */
export const BACKUP_CREATE_COMMAND = "backup_create";
export const BACKUP_LIST_COMMAND = "backup_list";
export const BACKUP_RESTORE_COMMAND = "backup_restore";
export const BACKUP_DELETE_COMMAND = "backup_delete";

/* PLUGIN-RUNTIME-1 (design §4.1–§4.4): the local plugin runtime face. The
 * four channel commands are pinned constants; `plugins_open_directory` is a
 * Rust-local command (the opener plugin) and never travels over the Core
 * channel. */
export const PLUGINS_LIST_COMMAND = "plugins_list";
export const PLUGINS_SET_ENABLED_COMMAND = "plugins_set_enabled";
export const PLUGINS_SET_PLUGIN_ENABLED_COMMAND = "plugins_set_plugin_enabled";
export const PLUGINS_AUDIT_LIST_COMMAND = "plugins_audit_list";
export const PLUGINS_OPEN_DIRECTORY_COMMAND = "plugins_open_directory";

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

/* ---------------- SETTINGS-OPEN-B-2 §4.3: cache / revision cleanup ---------------- */

/** One cleanable cache file, addressed RELATIVE to the managed root. The
 * WebView never receives or renders an absolute path for a cleanup target. */
export interface CleanupTarget {
  relative_path: string;
  size_bytes: number;
}

/**
 * `cleanup_preview` projection: what a run would remove, the byte total, and
 * how many paths sit in the persisted `pending_cleanups` retry ledger.
 */
export interface CleanupPreview {
  targets: CleanupTarget[];
  total_bytes: number;
  pending_cleanups: number;
}

/** The only three per-target statuses `CleanupOutcome` produces (cleanup.py). */
export type CleanupItemStatus = "ok" | "failed" | "skipped";

/** One per-target result of a run / retry. `detail` is the Core-provided
 * failure/skip reason and is rendered as opaque text (never interpreted). */
export interface CleanupItem {
  relative_path: string;
  status: CleanupItemStatus;
  detail?: string;
}

/** `cleanup_run` / `cleanup_retry_pending` projection: per-target results plus
 * the removed / failed / skipped counts. */
export interface CleanupOutcome {
  items: CleanupItem[];
  removed: number;
  failed: number;
  skipped: number;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

/** Non-negative integer from a JSON number (or a numeric string, tolerated
 * because the Python projection may serialize counts as strings). Anything
 * else is "unknown" — never NaN, never a negative count. */
function asCount(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value) && value >= 0) {
    return Math.floor(value);
  }
  if (typeof value === "string" && /^[0-9]+$/.test(value.trim())) {
    return Number(value.trim());
  }
  return null;
}

function asRelativePath(value: unknown): string | null {
  return typeof value === "string" && value.trim() !== "" ? value : null;
}

function normalizeCleanupStatus(value: unknown): CleanupItemStatus {
  const text = typeof value === "string" ? value.trim() : "";
  if (text === "ok" || text === "skipped") {
    return text;
  }
  // Unknown/missing statuses are fail-closed to "failed": the UI must never
  // claim a removal the Core did not actually confirm.
  return "failed";
}

/**
 * Defensive parse of the `cleanup_preview` result. The frozen projection is
 * `{targets:[{relative_path,size_bytes}], total_bytes, pending_cleanups}`;
 * a nested `{preview: ...}` envelope, a pending list instead of a count, and
 * a missing `total_bytes` are all tolerated so the panel degrades to "no
 * cleanable files" instead of crashing on a projection drift.
 */
function normalizeCleanupPreview(raw: unknown): CleanupPreview {
  const root = asRecord(raw) ?? {};
  const nested = asRecord(root.preview);
  const record = nested && root.targets === undefined ? nested : root;

  const targets: CleanupTarget[] = [];
  if (Array.isArray(record.targets)) {
    for (const entry of record.targets) {
      const row = asRecord(entry);
      if (!row) continue;
      const relativePath = asRelativePath(row.relative_path);
      if (!relativePath) continue;
      targets.push({
        relative_path: relativePath,
        size_bytes: asCount(row.size_bytes) ?? 0,
      });
    }
  }

  const totalBytes =
    asCount(record.total_bytes) ?? targets.reduce((sum, target) => sum + target.size_bytes, 0);

  const pendingRaw = record.pending_cleanups ?? root.pending_cleanups;
  const pendingCleanups = Array.isArray(pendingRaw)
    ? pendingRaw.length
    : (asCount(pendingRaw) ?? asCount(asRecord(pendingRaw)?.count) ?? 0);

  return { targets, total_bytes: totalBytes, pending_cleanups: pendingCleanups };
}

function cleanupItemFrom(relativePath: string, raw: unknown): CleanupItem | null {
  const row = asRecord(raw);
  if (!row) return null;
  const detailRaw = row.detail ?? row.reason;
  const detail = typeof detailRaw === "string" && detailRaw !== "" ? detailRaw : undefined;
  return {
    relative_path: relativePath,
    status: normalizeCleanupStatus(row.status),
    ...(detail !== undefined ? { detail } : {}),
  };
}

/**
 * Defensive parse of a cleanup outcome. Accepts BOTH shapes that exist on the
 * wire boundary:
 *
 *   1. the ruled B-2 projection (task-7) — `{items: {relative_path: {status,
 *      reason}}, removed, failed, skipped}`: `items` is a mapping, NOT an
 *      array, and the counts are top-level integers;
 *   2. the legacy `CleanupOutcome.to_dict()` mapping — `{path: {status,
 *      reason}}` (cleanup.py:92) — with the counts derived from the statuses;
 *   3. an items ARRAY form, tolerated for forward compatibility.
 *
 * Counts prefer the server-provided integers; a missing count is derived from
 * the parsed items. Unknown statuses are fail-closed to "failed".
 */
function normalizeCleanupOutcome(raw: unknown): CleanupOutcome {
  const root = asRecord(raw) ?? {};
  const nested = asRecord(root.outcome);
  const record = nested && root.items === undefined && root.removed === undefined ? nested : root;

  const items: CleanupItem[] = [];
  const pushItem = (relativePath: string, value: unknown) => {
    const item = cleanupItemFrom(relativePath, value);
    if (item) items.push(item);
  };

  const itemsRaw = record.items;
  const itemsRecord = asRecord(itemsRaw);
  if (Array.isArray(itemsRaw)) {
    for (const entry of itemsRaw) {
      const row = asRecord(entry);
      if (!row) continue;
      const relativePath = asRelativePath(row.relative_path) ?? asRelativePath(row.path);
      if (!relativePath) continue;
      pushItem(relativePath, row);
    }
  } else if (itemsRecord) {
    // Ruled task-7 shape: items is a path → {status, reason} mapping.
    for (const [relativePath, value] of Object.entries(itemsRecord)) {
      pushItem(relativePath, value);
    }
  } else {
    // Legacy task-7 pre-ruling shape: top-level mapping, no counts.
    for (const [relativePath, value] of Object.entries(record)) {
      if (
        relativePath === "items" ||
        relativePath === "outcome" ||
        relativePath === "removed" ||
        relativePath === "failed" ||
        relativePath === "skipped"
      ) {
        continue;
      }
      pushItem(relativePath, value);
    }
  }

  return {
    items,
    removed: asCount(record.removed) ?? items.filter((item) => item.status === "ok").length,
    failed: asCount(record.failed) ?? items.filter((item) => item.status === "failed").length,
    skipped: asCount(record.skipped) ?? items.filter((item) => item.status === "skipped").length,
  };
}

/* ---------------- SETTINGS-OPEN-C-2-BACKUP §3.4: .nmbak packages ---------------- */

/** One package found in the Core's fixed backup root. */
export interface BackupEntry {
  backup_id: string;
  backup_type: string;
  created_at: string;
  size_bytes: number;
  schema_version: number;
  verified: boolean;
}

/** `backup_create` projection: the verified package the Core just wrote. */
export interface BackupCreateResult {
  backup_id: string;
  path: string;
  size_bytes: number;
  created_at: string;
  verified: boolean;
}

/** One DB revision whose managed file was missing after a restore. The Core
 * reports the pair (`{revision_id, managed_path}`), so the projection keeps
 * both fields instead of collapsing them to opaque strings. */
export interface BackupMissingRef {
  revision_id: string;
  managed_path: string;
}

/** `backup_restore` report: overwrite source, rollback package and the
 * post-restore DB/managed consistency summary. */
export interface BackupRestoreReport {
  restored_from: string;
  pre_restore_backup_id: string;
  schema_versions: { backup: number | null; restored: number | null };
  managed_consistency: { checked: number | null; missing: BackupMissingRef[] };
}

/** `backup_delete` projection. */
export interface BackupDeleteResult {
  removed: boolean;
}

function normalizeBackupEntry(raw: unknown): BackupEntry | null {
  const row = asRecord(raw);
  if (!row) return null;
  const backupId = typeof row.backup_id === "string" ? row.backup_id.trim() : "";
  if (!/^[0-9a-f]{32}$/.test(backupId)) return null;
  return {
    backup_id: backupId,
    backup_type: typeof row.backup_type === "string" ? row.backup_type : "unknown",
    created_at: typeof row.created_at === "string" ? row.created_at : "",
    size_bytes: asCount(row.size_bytes) ?? 0,
    schema_version: asCount(row.schema_version) ?? 0,
    verified: row.verified === true,
  };
}

function normalizeBackupList(raw: unknown): BackupEntry[] {
  if (!Array.isArray(raw)) {
    throw new SettingsClientError("BACKUP_MALFORMED", "backup_list returned a non-array");
  }
  const entries: BackupEntry[] = [];
  for (const item of raw) {
    const entry = normalizeBackupEntry(item);
    if (entry) entries.push(entry);
  }
  return entries.sort((a, b) => (a.created_at < b.created_at ? 1 : a.created_at > b.created_at ? -1 : 0));
}

function normalizeBackupCreate(raw: unknown): BackupCreateResult {
  const row = asRecord(raw) ?? {};
  const backupId = typeof row.backup_id === "string" ? row.backup_id.trim() : "";
  if (!/^[0-9a-f]{32}$/.test(backupId)) {
    throw new SettingsClientError("BACKUP_MALFORMED", "backup_create returned no backup_id");
  }
  return {
    backup_id: backupId,
    path: typeof row.path === "string" ? row.path : "",
    size_bytes: asCount(row.size_bytes) ?? 0,
    created_at: typeof row.created_at === "string" ? row.created_at : "",
    verified: row.verified === true,
  };
}

function normalizeBackupRestore(raw: unknown): BackupRestoreReport {
  const row = asRecord(raw) ?? {};
  const versions = asRecord(row.schema_versions) ?? {};
  const consistency = asRecord(row.managed_consistency) ?? {};
  return {
    restored_from: typeof row.restored_from === "string" ? row.restored_from : "",
    pre_restore_backup_id:
      typeof row.pre_restore_backup_id === "string" ? row.pre_restore_backup_id : "",
    schema_versions: {
      backup: asCount(versions.backup),
      restored: asCount(versions.restored),
    },
    managed_consistency: {
      checked: asCount(consistency.checked),
      missing: Array.isArray(consistency.missing)
        ? consistency.missing
            .map((item) => asRecord(item))
            .filter((item): item is Record<string, unknown> => item !== null)
            .map((item) => ({
              revision_id: typeof item.revision_id === "string" ? item.revision_id : "",
              managed_path: typeof item.managed_path === "string" ? item.managed_path : "",
            }))
            .filter((item) => item.managed_path !== "")
        : [],
    },
  };
}

function normalizeBackupDelete(raw: unknown): BackupDeleteResult {
  const row = asRecord(raw) ?? {};
  return { removed: row.removed === true };
}

/* ---------------- PLUGIN-RUNTIME-1 §4.1–§4.4: local plugins ---------------- */

export type PluginStatus = "enabled" | "disabled" | "rejected";

/** One discovered plugin directory, as the Core projects it. */
export interface PluginEntry {
  plugin_id: string;
  status: PluginStatus;
  enabled: boolean;
  name: string;
  version: string;
  description: string;
  hooks: string[];
  reason: string | null;
}

/** `plugins_list` projection: the global kill switch + every discovered dir. */
export interface PluginsSnapshot {
  global_enabled: boolean;
  plugin_root: string;
  plugins: PluginEntry[];
}

/** One `plugin_events` row (append-only audit ledger). */
export interface PluginAuditEvent {
  event_id: string;
  plugin_id: string;
  event_type: string;
  hook_name: string | null;
  detail: Record<string, unknown>;
  occurred_at: string;
}

function normalizePluginStatus(value: unknown): PluginStatus {
  if (value === "enabled" || value === "disabled" || value === "rejected") return value;
  return "rejected";
}

function normalizePluginEntry(raw: unknown): PluginEntry | null {
  const row = asRecord(raw);
  if (!row) return null;
  const pluginId = typeof row.plugin_id === "string" ? row.plugin_id.trim() : "";
  if (!pluginId) return null;
  return {
    plugin_id: pluginId,
    status: normalizePluginStatus(row.status),
    enabled: row.enabled === true,
    name: typeof row.name === "string" ? row.name : "",
    version: typeof row.version === "string" ? row.version : "",
    description: typeof row.description === "string" ? row.description : "",
    hooks: Array.isArray(row.hooks)
      ? row.hooks.filter((item): item is string => typeof item === "string")
      : [],
    reason: typeof row.reason === "string" && row.reason ? row.reason : null,
  };
}

function normalizePluginsSnapshot(raw: unknown): PluginsSnapshot {
  const row = asRecord(raw) ?? {};
  const plugins: PluginEntry[] = [];
  if (Array.isArray(row.plugins)) {
    for (const item of row.plugins) {
      const entry = normalizePluginEntry(item);
      if (entry) plugins.push(entry);
    }
  }
  return {
    global_enabled: row.global_enabled === true,
    plugin_root: typeof row.plugin_root === "string" ? row.plugin_root : "",
    plugins,
  };
}

function normalizePluginAudit(raw: unknown): PluginAuditEvent[] {
  if (!Array.isArray(raw)) {
    throw new SettingsClientError("PLUGIN_MALFORMED", "plugins_audit_list returned a non-array");
  }
  const events: PluginAuditEvent[] = [];
  for (const item of raw) {
    const row = asRecord(item);
    if (!row) continue;
    events.push({
      event_id: typeof row.event_id === "string" ? row.event_id : "",
      plugin_id: typeof row.plugin_id === "string" ? row.plugin_id : "",
      event_type: typeof row.event_type === "string" ? row.event_type : "unknown",
      hook_name: typeof row.hook_name === "string" ? row.hook_name : null,
      detail: asRecord(row.detail) ?? {},
      occurred_at: typeof row.occurred_at === "string" ? row.occurred_at : "",
    });
  }
  return events;
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
   * UI cannot express a section outside the batch-A + batch-B-1 + sfx
   * whitelist.
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

  /* ---------------- SETTINGS-OPEN-B-2 §4.3: cache / revision cleanup ---------------- */

  /**
   * Read the cleanable-cache preview (`cleanup_preview`, no payload). The
   * request is deliberately empty: the Core owns the managed root and the
   * safe-prefix policy, so the UI cannot widen the cleanup scope.
   */
  async getCleanupPreview(): Promise<CleanupPreview> {
    try {
      return normalizeCleanupPreview(await this.invoke(CLEANUP_PREVIEW_COMMAND));
    } catch (error) {
      throw toClientError(error, CLEANUP_PREVIEW_COMMAND);
    }
  }

  /** Execute the controlled cache cleanup (`cleanup_run`, no payload). */
  async runCleanup(): Promise<CleanupOutcome> {
    try {
      return normalizeCleanupOutcome(await this.invoke(CLEANUP_RUN_COMMAND));
    } catch (error) {
      throw toClientError(error, CLEANUP_RUN_COMMAND);
    }
  }

  /**
   * Retry the persisted `pending_cleanups` ledger (`cleanup_retry_pending`,
   * no payload). Same safe-prefix predicate as a full run — retry is not a
   * bypass.
   */
  async retryPendingCleanups(): Promise<CleanupOutcome> {
    try {
      return normalizeCleanupOutcome(await this.invoke(CLEANUP_RETRY_PENDING_COMMAND));
    } catch (error) {
      throw toClientError(error, CLEANUP_RETRY_PENDING_COMMAND);
    }
  }


  /* ---------------- PLUGIN-RUNTIME-1 §4.1–§4.4: local plugins ---------------- */

  /** The discovered-plugin snapshot (global switch + per-plugin state). */
  async listPlugins(): Promise<PluginsSnapshot> {
    try {
      return normalizePluginsSnapshot(await this.invoke(PLUGINS_LIST_COMMAND));
    } catch (error) {
      throw toClientError(error, PLUGINS_LIST_COMMAND);
    }
  }

  /** The global `plugins.enabled` kill switch (default off). */
  async setPluginsEnabled(enabled: boolean): Promise<{ global_enabled: boolean }> {
    try {
      const row = asRecord(await this.invoke(PLUGINS_SET_ENABLED_COMMAND, { enabled })) ?? {};
      return { global_enabled: row.global_enabled === true };
    } catch (error) {
      throw toClientError(error, PLUGINS_SET_ENABLED_COMMAND);
    }
  }

  /** Per-plugin enable; the Core re-validates the manifest on every call. */
  async setPluginEnabled(pluginId: string, enabled: boolean): Promise<{ plugin_id: string; enabled: boolean }> {
    try {
      const row =
        asRecord(await this.invoke(PLUGINS_SET_PLUGIN_ENABLED_COMMAND, { pluginId, enabled })) ?? {};
      return {
        plugin_id: typeof row.plugin_id === "string" ? row.plugin_id : pluginId,
        enabled: row.enabled === true,
      };
    } catch (error) {
      throw toClientError(error, PLUGINS_SET_PLUGIN_ENABLED_COMMAND);
    }
  }

  /** The newest `plugin_events` rows (append-only audit ledger). */
  async listPluginAudit(limit = 20): Promise<PluginAuditEvent[]> {
    try {
      return normalizePluginAudit(await this.invoke(PLUGINS_AUDIT_LIST_COMMAND, { limit }));
    } catch (error) {
      throw toClientError(error, PLUGINS_AUDIT_LIST_COMMAND);
    }
  }

  /** Open `<app_data>/plugins` so the user can drop a plugin directory. */
  async openPluginDirectory(): Promise<void> {
    try {
      await this.invoke(PLUGINS_OPEN_DIRECTORY_COMMAND);
    } catch (error) {
      throw toClientError(error, PLUGINS_OPEN_DIRECTORY_COMMAND);
    }
  }

  /* ---------------- SETTINGS-OPEN-C-2-BACKUP §3.4: .nmbak packages ---------------- */

  /** Create one `manual` package (`backup_type` is the only payload field;
   * there is no target directory — the Core owns the backup root). */
  async createBackup(): Promise<BackupCreateResult> {
    try {
      return normalizeBackupCreate(
        await this.invoke(BACKUP_CREATE_COMMAND, { backupType: "manual" }),
      );
    } catch (error) {
      throw toClientError(error, BACKUP_CREATE_COMMAND);
    }
  }

  /** List the packages in the Core's backup root, newest first. */
  async listBackups(): Promise<BackupEntry[]> {
    try {
      return normalizeBackupList(await this.invoke(BACKUP_LIST_COMMAND));
    } catch (error) {
      throw toClientError(error, BACKUP_LIST_COMMAND);
    }
  }

  /** Overwrite-restore from one verified package. `confirm_restore` is always
   * true here: the panel's own dialog is the human confirmation. */
  async restoreBackup(backupId: string): Promise<BackupRestoreReport> {
    try {
      return normalizeBackupRestore(
        await this.invoke(BACKUP_RESTORE_COMMAND, {
          backupId,
          confirmRestore: true,
        }),
      );
    } catch (error) {
      throw toClientError(error, BACKUP_RESTORE_COMMAND);
    }
  }

  /** Delete one package (idempotent from the UI's point of view: a second
   * delete answers BACKUP_NOT_FOUND). */
  async deleteBackup(backupId: string): Promise<BackupDeleteResult> {
    try {
      return normalizeBackupDelete(
        await this.invoke(BACKUP_DELETE_COMMAND, { backupId }),
      );
    } catch (error) {
      throw toClientError(error, BACKUP_DELETE_COMMAND);
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
