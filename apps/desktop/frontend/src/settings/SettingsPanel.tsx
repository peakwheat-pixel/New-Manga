import { useCallback, useEffect, useState } from "react";
import { SettingsClient, SettingsClientError } from "./client";
import {
  DEFAULT_SFX_POLICY,
  SFX_POLICY_LABELS,
  SFX_POLICY_VALUES,
  type SfxPolicy,
} from "./types";

/**
 * SettingsPanel — the minimal settings surface for M2-SETTINGS-UI-SFX-POLICY.
 *
 * Survey fact (AC1): the product React app has no settings page yet (App.tsx
 * is the M2-RC2 runtime host + LibraryPanel), so this Task lands the minimal
 * Settings SECTION component alongside LibraryPanel, reusing its exact visual
 * language (same section frame, button, and error-block styles). The "翻译与
 * 检测 (Translation & Detection)" group hosts the SFX policy control; a future
 * settings-page Task can adopt this component unchanged (client is injected).
 *
 * The save channel is mocked at the client boundary (BLOCKED_ON_CONTRACT —
 * see client.ts); the component itself is channel-agnostic.
 */

export interface SettingsPanelProps {
  client?: SettingsClient;
  /** Optional initial state for testing or static preview */
  initialState?: {
    loading?: boolean;
    /** null = unset on the Core → the default (skip) is displayed */
    sfxPolicy?: SfxPolicy | null;
    error?: string | null;
  };
}

// Scope note (fact source: M2-SFX-TRANSLATE-ENTRY r1 R1 registration in
// verification/M2-SFX-TRANSLATE-ENTRY/integration.md): the policy is
// re-assembled — it applies to newly-created regions only, existing regions
// are never retro-fitted.
const SFX_SCOPE_NOTE =
  "保存后重新打开应用生效；仅对此后新建检出的 region 生效（既有页面需重新检出）";

export function SettingsPanel({ client, initialState }: SettingsPanelProps) {
  const [loading, setLoading] = useState<boolean>(
    initialState?.loading ?? (initialState ? false : true),
  );
  const [loadError, setLoadError] = useState<string | null>(initialState?.error ?? null);
  // the effective value on the Core (what "当前生效值" means)
  const [policy, setPolicy] = useState<SfxPolicy>(
    initialState?.sfxPolicy ?? DEFAULT_SFX_POLICY,
  );
  // the draft the user is choosing (becomes effective only after a save)
  const [draft, setDraft] = useState<SfxPolicy>(
    initialState?.sfxPolicy ?? DEFAULT_SFX_POLICY,
  );
  const [saving, setSaving] = useState<boolean>(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const loadPolicy = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const activeClient = client || new SettingsClient();
      const effective = await activeClient.getSfxPolicy();
      setPolicy(effective);
      setDraft(effective);
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setLoadError(code);
    } finally {
      setLoading(false);
    }
  }, [client]);

  useEffect(() => {
    // Only auto-fetch if no static initial state was passed
    if (!initialState) {
      void loadPolicy();
    }
  }, [loadPolicy, initialState]);

  const saveDraft = useCallback(async () => {
    setSaving(true);
    setSaveError(null);
    try {
      const activeClient = client || new SettingsClient();
      await activeClient.saveSfxPolicy(draft);
      setPolicy(draft);
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setSaveError(code);
    } finally {
      setSaving(false);
    }
  }, [client, draft]);

  const dirty = draft !== policy;

  return (
    <section
      data-testid="settings-panel"
      style={{
        marginTop: 20,
        padding: 16,
        border: "1px solid #2a3441",
        borderRadius: 6,
        background: "#161b22",
        color: "#e6edf3",
      }}
    >
      <h2 style={{ fontSize: 16, margin: 0, marginBottom: 12, fontWeight: 600 }}>
        设置 (Settings)
      </h2>

      {/* Loading state */}
      {loading && (
        <div data-testid="settings-loading" style={{ color: "#8b949e", padding: "12px 0" }}>
          正在加载设置数据...
        </div>
      )}

      {/* Load error state (explicit UI, no automatic retry) */}
      {!loading && loadError && (
        <div
          data-testid="settings-load-error"
          style={{
            padding: 12,
            background: "#3c1618",
            border: "1px solid #f85149",
            borderRadius: 4,
            color: "#ff7b72",
          }}
        >
          <div style={{ fontWeight: "bold" }}>加载失败: {loadError}</div>
          <div style={{ fontSize: 12, marginTop: 4, color: "#e6edf3" }}>
            无法读取设置数据。请检查后台服务状态后重试（系统不会自动重试）。
          </div>
        </div>
      )}

      {/* Settings content */}
      {!loading && !loadError && (
        <fieldset
          data-testid="settings-group-translation-detection"
          style={{ border: "1px solid #30363d", borderRadius: 4, margin: 0, padding: 12 }}
        >
          <legend style={{ fontSize: 13, color: "#8b949e", padding: "0 6px" }}>
            翻译与检测 (Translation &amp; Detection)
          </legend>

          <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
            <label
              htmlFor="sfx-policy-select"
              style={{ fontSize: 13, minWidth: 140, display: "inline-block" }}
            >
              SFX 翻译策略
            </label>
            <select
              id="sfx-policy-select"
              data-testid="sfx-policy-select"
              value={draft}
              disabled={saving}
              onChange={(event) => {
                const next = event.target.value as SfxPolicy;
                if (SFX_POLICY_VALUES.includes(next)) {
                  setDraft(next);
                }
              }}
              style={{
                padding: "4px 8px",
                fontSize: 12,
                background: "#0d1117",
                color: "#e6edf3",
                border: "1px solid #30363d",
                borderRadius: 4,
              }}
            >
              {SFX_POLICY_VALUES.map((value) => (
                <option key={value} value={value}>
                  {SFX_POLICY_LABELS[value]}
                </option>
              ))}
            </select>
            <button
              data-testid="sfx-policy-save-btn"
              onClick={() => void saveDraft()}
              disabled={saving || !dirty}
              style={{
                padding: "4px 10px",
                fontSize: 12,
                background: "#21262d",
                color: "#c9d1d9",
                border: "1px solid #30363d",
                borderRadius: 4,
                cursor: saving || !dirty ? "not-allowed" : "pointer",
              }}
            >
              {saving ? "保存中..." : "保存"}
            </button>
          </div>

          <div style={{ fontSize: 12, color: "#8b949e", marginTop: 8 }}>
            <div>
              当前生效值：
              <span data-testid="sfx-policy-effective">{SFX_POLICY_LABELS[policy]}</span>
              {policy === DEFAULT_SFX_POLICY && "（默认）"}
            </div>
            <div data-testid="sfx-policy-scope-note" style={{ marginTop: 4 }}>
              {SFX_SCOPE_NOTE}
            </div>
          </div>

          {/* Save error state (explicit UI, follows the LibraryPanel error block) */}
          {saveError && (
            <div
              data-testid="sfx-save-error"
              style={{
                marginTop: 8,
                padding: 12,
                background: "#3c1618",
                border: "1px solid #f85149",
                borderRadius: 4,
                color: "#ff7b72",
              }}
            >
              <div style={{ fontWeight: "bold" }}>保存失败: {saveError}</div>
              <div style={{ fontSize: 12, marginTop: 4, color: "#e6edf3" }}>
                设置未写入，请重试（系统不会自动重试）。
              </div>
            </div>
          )}
        </fieldset>
      )}
    </section>
  );
}
