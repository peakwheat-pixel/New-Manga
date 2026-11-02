import { useCallback, useEffect, useState } from "react";
import { SettingsClient, SettingsClientError } from "./client";
import { projectSettingsError, type SettingsSurfaceError } from "./errors";
import {
  CAPABILITY_VALUES,
  validateProviderProfileDraft,
  type Capability,
  type NetworkProfile,
  type ProviderProfile,
} from "./types";
import { CredentialField } from "./CredentialField";
import { SettingsErrorBar } from "./SettingsErrorBar";
import { tokens } from "../theme/tokens";

/**
 * G21 Provider Profile panel (P15-C1 §3). The editable key set is exactly
 * the G25 whitelist: provider_id (create only), display_name,
 * capabilities, endpoint, model, network_profile_id, enabled.
 * credential_state / credential_hint are read-only projections and the
 * write payloads structurally cannot carry a Secret or CredentialRef.
 */
interface Draft {
  provider_id: string;
  display_name: string;
  capabilities: Capability[];
  endpoint: string;
  model: string;
  network_profile_id: string | null;
  enabled: boolean;
}

const EMPTY_DRAFT: Draft = {
  provider_id: "",
  display_name: "",
  capabilities: [],
  endpoint: "",
  model: "",
  network_profile_id: null,
  enabled: true,
};

function draftFromProfile(profile: ProviderProfile): Draft {
  return {
    provider_id: profile.provider_id,
    display_name: profile.display_name,
    capabilities: profile.capabilities,
    endpoint: profile.endpoint,
    model: profile.model,
    network_profile_id: profile.network_profile_id,
    enabled: profile.enabled,
  };
}

export function ProviderProfilePanel({ client }: { client: SettingsClient }) {
  const [phase, setPhase] = useState<"loading" | "error" | "ready">("loading");
  const [profiles, setProfiles] = useState<ProviderProfile[]>([]);
  const [loadError, setLoadError] = useState<SettingsSurfaceError | null>(null);
  const [networkProfiles, setNetworkProfiles] = useState<NetworkProfile[]>([]);
  const [editing, setEditing] = useState<null | { mode: "create" } | { mode: "edit"; profileId: string }>(null);
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<SettingsSurfaceError | null>(null);
  const [confirmingDelete, setConfirmingDelete] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<SettingsSurfaceError | null>(null);

  const reload = useCallback(async () => {
    setPhase("loading");
    setLoadError(null);
    try {
      const list = await client.listProviderProfiles();
      setProfiles(list);
      setPhase("ready");
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setLoadError(projectSettingsError(code, "profile"));
      setPhase("error");
    }
  }, [client]);

  useEffect(() => {
    void reload();
    // Network profiles only feed the association dropdown; a failure leaves
    // the "no association" option usable and never blocks the panel.
    client
      .listNetworkProfiles()
      .then(setNetworkProfiles)
      .catch(() => setNetworkProfiles([]));
  }, [reload, client]);

  const openCreate = () => {
    setEditing({ mode: "create" });
    setDraft(EMPTY_DRAFT);
    setFieldErrors({});
    setSaveError(null);
  };

  const openEdit = (profile: ProviderProfile) => {
    setEditing({ mode: "edit", profileId: profile.profile_id });
    setDraft(draftFromProfile(profile));
    setFieldErrors({});
    setSaveError(null);
  };

  const save = async () => {
    const errors = validateProviderProfileDraft(draft);
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) {
      return;
    }
    setSaving(true);
    setSaveError(null);
    try {
      if (editing?.mode === "create") {
        await client.createProviderProfile({
          provider_id: draft.provider_id.trim(),
          display_name: draft.display_name.trim(),
          capabilities: draft.capabilities,
          endpoint: draft.endpoint.trim(),
          model: draft.model.trim(),
          network_profile_id: draft.network_profile_id,
          enabled: draft.enabled,
        });
      } else if (editing?.mode === "edit") {
        await client.updateProviderProfile({
          profile_id: editing.profileId,
          display_name: draft.display_name.trim(),
          capabilities: draft.capabilities,
          endpoint: draft.endpoint.trim(),
          model: draft.model.trim(),
          network_profile_id: draft.network_profile_id,
          enabled: draft.enabled,
        });
      }
      setEditing(null);
      await reload();
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setSaveError(projectSettingsError(code, "profile"));
      // Draft kept: a failed save must not lose user input (AC4).
    } finally {
      setSaving(false);
    }
  };

  const remove = async (profileId: string) => {
    setSaving(true);
    setDeleteError(null);
    try {
      await client.deleteProviderProfile(profileId);
      setConfirmingDelete(null);
      await reload();
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setDeleteError(projectSettingsError(code, "profile"));
      setConfirmingDelete(null);
    } finally {
      setSaving(false);
    }
  };

  const toggleCapability = (capability: Capability) => {
    setDraft((prev) => ({
      ...prev,
      capabilities: prev.capabilities.includes(capability)
        ? prev.capabilities.filter((c) => c !== capability)
        : [...prev.capabilities, capability],
    }));
  };

  const fieldStyle = (hasError: boolean): React.CSSProperties => ({
    padding: "4px 8px",
    fontSize: tokens.typography.size.base,
    border: `1px solid ${hasError ? tokens.color.state.failed : tokens.color.border.default}`,
    borderRadius: tokens.radius.button,
    background: tokens.color.surface.card,
    color: tokens.color.text.primary,
    width: "100%",
    boxSizing: "border-box",
  });

  return (
    <section
      data-testid="provider-profile-panel"
      style={{
        padding: tokens.spacing.lg,
        backgroundColor: tokens.color.surface.card,
        border: `1px solid ${tokens.color.border.default}`,
        borderRadius: tokens.radius.card,
        maxWidth: 760,
      }}
    >
      <h3 style={{ margin: 0, marginBottom: tokens.spacing.sm, fontSize: tokens.typography.size.cardTitle, fontWeight: 600, color: tokens.color.text.primary }}>
        Provider Profile
      </h3>
      <p style={{ margin: 0, marginBottom: tokens.spacing.md, fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
        同一 Provider 类型可配置多个 Profile（以 profile_id 区分）；凭据只经专用一次性通道配置，永不回显明文。
      </p>

      {phase === "loading" && (
        <div data-testid="provider-panel-loading" aria-busy="true" style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.sm }}>
          {[0, 1, 2].map((i) => (
            <div key={i} style={{ height: 16, borderRadius: tokens.radius.button, background: tokens.color.bg.toolbar, width: `${80 - i * 18}%` }} />
          ))}
        </div>
      )}

      {phase === "error" && loadError && (
        <SettingsErrorBar testId="provider-panel-error" error={loadError} onRetry={() => void reload()} />
      )}

      {phase === "ready" && (
        <>
          {profiles.length === 0 ? (
            <div
              data-testid="provider-panel-empty"
              style={{ padding: tokens.spacing.md, border: `1px dashed ${tokens.color.border.default}`, borderRadius: tokens.radius.button, color: tokens.color.text.secondary }}
            >
              暂无 Provider Profile。
            </div>
          ) : (
            <div data-testid="provider-panel-list" style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.sm }}>
              {profiles.map((profile) => (
                <div
                  key={profile.profile_id}
                  data-testid={`provider-row-${profile.profile_id}`}
                  style={{ padding: tokens.spacing.md, border: `1px solid ${tokens.color.border.divider}`, borderRadius: tokens.radius.button, display: "flex", flexDirection: "column", gap: tokens.spacing.xs }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.sm, flexWrap: "wrap" }}>
                    <strong style={{ fontSize: tokens.typography.size.base }}>{profile.display_name}</strong>
                    <span style={{ fontFamily: tokens.typography.monospace, fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
                      {profile.provider_id} / {profile.profile_id}
                    </span>
                    <span
                      data-testid={`provider-row-${profile.profile_id}-enabled`}
                      style={{ fontSize: tokens.typography.size.badge, padding: "1px 8px", borderRadius: tokens.radius.pill, background: profile.enabled ? "#e6f4ea" : "#f0f0ef", color: profile.enabled ? tokens.color.state.completed : tokens.color.text.muted }}
                    >
                      {profile.enabled ? "已启用" : "已停用"}
                    </span>
                  </div>
                  <div style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
                    能力：{profile.capabilities.join("、") || "—"} · model：{profile.model} · endpoint：{profile.endpoint}
                    {profile.network_profile_id ? ` · 网络 Profile：${profile.network_profile_id}` : ""}
                  </div>
                  <CredentialField
                    testId={`provider-row-${profile.profile_id}-credential`}
                    client={client}
                    state={profile.credential_state}
                    hint={profile.credential_hint}
                    target={{ kind: "provider_api", profile_id: profile.profile_id }}
                    onCredentialChanged={() => void reload()}
                    phaseLabel="API "
                  />
                  <div style={{ display: "flex", gap: tokens.spacing.sm }}>
                    <button type="button" data-testid={`provider-row-${profile.profile_id}-edit-btn`} onClick={() => openEdit(profile)} style={{ padding: "2px 10px", fontSize: tokens.typography.size.secondary, border: `1px solid ${tokens.color.border.default}`, borderRadius: tokens.radius.button, background: tokens.color.surface.card, cursor: "pointer" }}>
                      编辑
                    </button>
                    {confirmingDelete === profile.profile_id ? (
                      <>
                        <button type="button" data-testid={`provider-row-${profile.profile_id}-delete-confirm-btn`} disabled={saving} onClick={() => void remove(profile.profile_id)} style={{ padding: "2px 10px", fontSize: tokens.typography.size.secondary, border: `1px solid ${tokens.color.state.failed}`, borderRadius: tokens.radius.button, background: "#fff1f0", color: tokens.color.state.failed, cursor: "pointer" }}>
                          确认删除（仍被绑定的 Profile 会被拒绝）
                        </button>
                        <button type="button" data-testid={`provider-row-${profile.profile_id}-delete-cancel-btn`} onClick={() => setConfirmingDelete(null)} style={{ padding: "2px 10px", fontSize: tokens.typography.size.secondary, border: `1px solid ${tokens.color.border.default}`, borderRadius: tokens.radius.button, background: tokens.color.surface.card, cursor: "pointer" }}>
                          取消
                        </button>
                      </>
                    ) : (
                      <button type="button" data-testid={`provider-row-${profile.profile_id}-delete-btn`} onClick={() => setConfirmingDelete(profile.profile_id)} style={{ padding: "2px 10px", fontSize: tokens.typography.size.secondary, border: `1px solid ${tokens.color.state.failed}`, borderRadius: tokens.radius.button, background: "#fff1f0", color: tokens.color.state.failed, cursor: "pointer" }}>
                        删除
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {deleteError && <div style={{ marginTop: tokens.spacing.md }}><SettingsErrorBar testId="provider-panel-delete-error" error={deleteError} /></div>}

          <div style={{ marginTop: tokens.spacing.md }}>
            {editing === null ? (
              <button type="button" data-testid="provider-new-btn" onClick={openCreate} style={{ padding: "4px 12px", fontSize: tokens.typography.size.base, border: `1px solid ${tokens.color.accent.primary}`, borderRadius: tokens.radius.button, background: tokens.color.accent.selected, color: tokens.color.accent.primary, cursor: "pointer" }}>
                新建 Profile
              </button>
            ) : (
              <div
                data-testid="provider-form"
                style={{ padding: tokens.spacing.md, border: `1px solid ${tokens.color.border.default}`, borderRadius: tokens.radius.button, display: "flex", flexDirection: "column", gap: tokens.spacing.sm, maxWidth: 520 }}
              >
                <div data-testid="provider-form-title" style={{ fontWeight: 600 }}>
                  {editing.mode === "create" ? "新建 Provider Profile" : "编辑 Provider Profile"}
                </div>

                <label style={{ fontSize: tokens.typography.size.secondary, display: "flex", flexDirection: "column", gap: 2 }}>
                  provider_id
                  <input
                    data-testid="provider-form-provider-id"
                    value={draft.provider_id}
                    disabled={editing.mode === "edit"}
                    aria-invalid={Boolean(fieldErrors.provider_id)}
                    onChange={(e) => setDraft({ ...draft, provider_id: e.target.value })}
                    // jsdom suites drive value changes via native setter +
                    // input events; onChange alone never fires there
                    // (same twin-handler pattern as BookshelfToolbar).
                    onInput={(e) => setDraft({ ...draft, provider_id: (e.target as HTMLInputElement).value })}
                    style={fieldStyle(Boolean(fieldErrors.provider_id))}
                  />
                </label>
                {fieldErrors.provider_id && <FieldError testId="provider-field-error-provider-id" message={fieldErrors.provider_id} />}

                <label style={{ fontSize: tokens.typography.size.secondary, display: "flex", flexDirection: "column", gap: 2 }}>
                  display_name
                  <input
                    data-testid="provider-form-display-name"
                    value={draft.display_name}
                    aria-invalid={Boolean(fieldErrors.display_name)}
                    onChange={(e) => setDraft({ ...draft, display_name: e.target.value })}
                    onInput={(e) => setDraft({ ...draft, display_name: (e.target as HTMLInputElement).value })}
                    style={fieldStyle(Boolean(fieldErrors.display_name))}
                  />
                </label>
                {fieldErrors.display_name && <FieldError testId="provider-field-error-display-name" message={fieldErrors.display_name} />}

                <fieldset style={{ border: `1px solid ${fieldErrors.capabilities ? tokens.color.state.failed : tokens.color.border.divider}`, borderRadius: tokens.radius.button, padding: tokens.spacing.sm, display: "flex", flexDirection: "column", gap: 2 }}>
                  <legend style={{ fontSize: tokens.typography.size.secondary }}>capabilities（至少一个）</legend>
                  {CAPABILITY_VALUES.map((capability) => (
                    <label key={capability} style={{ fontSize: tokens.typography.size.base, display: "flex", gap: tokens.spacing.xs, alignItems: "center" }}>
                      <input
                        type="checkbox"
                        data-testid={`provider-form-capability-${capability}`}
                        checked={draft.capabilities.includes(capability)}
                        onChange={() => toggleCapability(capability)}
                      />
                      {capability}
                    </label>
                  ))}
                </fieldset>
                {fieldErrors.capabilities && <FieldError testId="provider-field-error-capabilities" message={fieldErrors.capabilities} />}

                <label style={{ fontSize: tokens.typography.size.secondary, display: "flex", flexDirection: "column", gap: 2 }}>
                  endpoint（绝对 HTTP(S)，无 userinfo/query/fragment）
                  <input
                    data-testid="provider-form-endpoint"
                    value={draft.endpoint}
                    aria-invalid={Boolean(fieldErrors.endpoint)}
                    onChange={(e) => setDraft({ ...draft, endpoint: e.target.value })}
                    onInput={(e) => setDraft({ ...draft, endpoint: (e.target as HTMLInputElement).value })}
                    style={fieldStyle(Boolean(fieldErrors.endpoint))}
                  />
                </label>
                {fieldErrors.endpoint && <FieldError testId="provider-field-error-endpoint" message={fieldErrors.endpoint} />}

                <label style={{ fontSize: tokens.typography.size.secondary, display: "flex", flexDirection: "column", gap: 2 }}>
                  model
                  <input
                    data-testid="provider-form-model"
                    value={draft.model}
                    aria-invalid={Boolean(fieldErrors.model)}
                    onChange={(e) => setDraft({ ...draft, model: e.target.value })}
                    onInput={(e) => setDraft({ ...draft, model: (e.target as HTMLInputElement).value })}
                    style={fieldStyle(Boolean(fieldErrors.model))}
                  />
                </label>
                {fieldErrors.model && <FieldError testId="provider-field-error-model" message={fieldErrors.model} />}

                <label style={{ fontSize: tokens.typography.size.secondary, display: "flex", flexDirection: "column", gap: 2 }}>
                  network_profile_id（可选关联）
                  <select
                    data-testid="provider-form-network-profile"
                    value={draft.network_profile_id ?? ""}
                    onChange={(e) => setDraft({ ...draft, network_profile_id: e.target.value === "" ? null : e.target.value })}
                    style={fieldStyle(false)}
                  >
                    <option value="">（不关联，走全局网络来源）</option>
                    {networkProfiles.map((np) => (
                      <option key={np.network_profile_id} value={np.network_profile_id}>
                        {np.display_name}（{np.mode}）
                      </option>
                    ))}
                  </select>
                </label>

                <label style={{ fontSize: tokens.typography.size.base, display: "flex", gap: tokens.spacing.xs, alignItems: "center" }}>
                  <input
                    type="checkbox"
                    data-testid="provider-form-enabled"
                    checked={draft.enabled}
                    onChange={(e) => setDraft({ ...draft, enabled: e.target.checked })}
                  />
                  enabled
                </label>

                {saveError && <SettingsErrorBar testId="provider-form-save-error" error={saveError} />}

                <div style={{ display: "flex", gap: tokens.spacing.sm }}>
                  <button type="button" data-testid="provider-form-save-btn" disabled={saving} onClick={() => void save()} style={{ padding: "4px 12px", fontSize: tokens.typography.size.base, border: `1px solid ${tokens.color.accent.primary}`, borderRadius: tokens.radius.button, background: tokens.color.accent.selected, color: tokens.color.accent.primary, cursor: saving ? "not-allowed" : "pointer", opacity: saving ? 0.45 : 1 }}>
                    {saving ? "保存中…" : "保存"}
                  </button>
                  <button type="button" data-testid="provider-form-cancel-btn" disabled={saving} onClick={() => setEditing(null)} style={{ padding: "4px 12px", fontSize: tokens.typography.size.base, border: `1px solid ${tokens.color.border.default}`, borderRadius: tokens.radius.button, background: tokens.color.surface.card, cursor: "pointer" }}>
                    取消
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </section>
  );
}

function FieldError({ testId, message }: { testId: string; message: string }) {
  return (
    <div data-testid={testId} role="alert" style={{ color: tokens.color.state.failed, fontSize: tokens.typography.size.secondary }}>
      {message}
    </div>
  );
}
