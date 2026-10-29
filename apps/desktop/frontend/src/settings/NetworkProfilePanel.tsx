import { useCallback, useEffect, useState } from "react";
import { SettingsClient, SettingsClientError } from "./client";
import { localizeMessageKey, projectSettingsError, type SettingsSurfaceError } from "./errors";
import {
  NETWORK_MODE_VALUES,
  modeRequiresProxyEndpoint,
  validateNetworkProfileDraft,
  type NetworkMode,
  type NetworkProfile,
  type NetworkStage,
  type NetworkTestResult,
  type ProviderProfile,
  type StageResult,
} from "./types";
import { CredentialField } from "./CredentialField";
import { SettingsErrorBar } from "./SettingsErrorBar";
import { tokens } from "../theme/tokens";

/**
 * G23 Network Profile panel (P15-C1 §5). Rules frozen by the contract:
 * - HTTP/HTTPS/SOCKS5 need a mode-matching proxy endpoint; Direct/System
 *   must be null;
 * - verify_tls defaults to true; turning it OFF requires an explicit danger
 *   confirmation and the state stays visible (tls_verification_state);
 * - allow_proxy_failure_direct_fallback defaults to false — proxy failure
 *   never silently falls back to a direct connection;
 * - the staged connection test never falls back either
 *   (direct_fallback_used is constantly false) and shows all six stages
 *   with passed/failed/not_run/not_applicable.
 */
interface Draft {
  display_name: string;
  mode: NetworkMode;
  proxy_endpoint: string;
  verify_tls: boolean;
  tlsDangerConfirmed: boolean;
  allow_proxy_failure_direct_fallback: boolean;
}

const EMPTY_DRAFT: Draft = {
  display_name: "",
  mode: "Direct",
  proxy_endpoint: "",
  verify_tls: true,
  tlsDangerConfirmed: false,
  allow_proxy_failure_direct_fallback: false,
};

const STAGE_ORDER: readonly NetworkStage[] = ["Proxy", "DNS", "TCP", "TLS", "HTTP", "ProviderAuth"];

const STAGE_STATUS_TEXT: Record<string, string> = {
  passed: "通过",
  failed: "失败",
  not_run: "未执行",
  not_applicable: "不适用",
};

function draftFromProfile(profile: NetworkProfile): Draft {
  return {
    display_name: profile.display_name,
    mode: profile.mode,
    proxy_endpoint: profile.proxy_endpoint ?? "",
    verify_tls: profile.verify_tls,
    tlsDangerConfirmed: profile.tls_verification_state === "disabled_confirmed",
    allow_proxy_failure_direct_fallback: profile.allow_proxy_failure_direct_fallback,
  };
}

export function NetworkProfilePanel({ client }: { client: SettingsClient }) {
  const [phase, setPhase] = useState<"loading" | "error" | "ready">("loading");
  const [profiles, setProfiles] = useState<NetworkProfile[]>([]);
  const [providerProfiles, setProviderProfiles] = useState<ProviderProfile[]>([]);
  const [loadError, setLoadError] = useState<SettingsSurfaceError | null>(null);
  const [resolved, setResolved] = useState<{ network_profile_id: string | null; mode: NetworkMode; source: string } | null>(null);
  const [editing, setEditing] = useState<null | { mode: "create" } | { mode: "edit"; networkProfileId: string }>(null);
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<SettingsSurfaceError | null>(null);
  const [confirmingDelete, setConfirmingDelete] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<SettingsSurfaceError | null>(null);
  const [globalBusy, setGlobalBusy] = useState(false);
  const [globalError, setGlobalError] = useState<SettingsSurfaceError | null>(null);
  const [globalPick, setGlobalPick] = useState("");
  const [testingId, setTestingId] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<{ profileId: string; result: NetworkTestResult } | null>(null);
  const [testProviderPick, setTestProviderPick] = useState("");
  const [testError, setTestError] = useState<SettingsSurfaceError | null>(null);

  const reload = useCallback(async () => {
    setPhase("loading");
    setLoadError(null);
    try {
      const list = await client.listNetworkProfiles();
      setProfiles(list);
      setPhase("ready");
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setLoadError(projectSettingsError(code, "network_proxy"));
      setPhase("error");
    }
  }, [client]);

  const reloadResolved = useCallback(async () => {
    try {
      const r = await client.resolveNetworkProfile();
      setResolved({ network_profile_id: r.network_profile_id, mode: r.mode, source: r.source });
    } catch {
      setResolved(null);
    }
  }, [client]);

  useEffect(() => {
    void reload();
    void reloadResolved();
    client
      .listProviderProfiles()
      .then(setProviderProfiles)
      .catch(() => setProviderProfiles([]));
  }, [reload, reloadResolved, client]);

  const openCreate = () => {
    setEditing({ mode: "create" });
    setDraft(EMPTY_DRAFT);
    setFieldErrors({});
    setSaveError(null);
  };

  const openEdit = (profile: NetworkProfile) => {
    setEditing({ mode: "edit", networkProfileId: profile.network_profile_id });
    setDraft(draftFromProfile(profile));
    setFieldErrors({});
    setSaveError(null);
  };

  const proxyEndpointForSubmit = (): string | null =>
    modeRequiresProxyEndpoint(draft.mode) ? draft.proxy_endpoint.trim() : null;

  const save = async () => {
    const errors = validateNetworkProfileDraft({
      display_name: draft.display_name,
      mode: draft.mode,
      proxy_endpoint: proxyEndpointForSubmit(),
      verify_tls: draft.verify_tls,
      tlsDangerConfirmed: draft.tlsDangerConfirmed,
    });
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) {
      return;
    }
    setSaving(true);
    setSaveError(null);
    const disablingTls = !draft.verify_tls;
    try {
      if (editing?.mode === "create") {
        await client.createNetworkProfile({
          display_name: draft.display_name.trim(),
          mode: draft.mode,
          proxy_endpoint: proxyEndpointForSubmit(),
          ...(draft.verify_tls !== true ? { verify_tls: draft.verify_tls } : {}),
          ...(disablingTls ? { confirm_disable_tls_verification: true } : {}),
          allow_proxy_failure_direct_fallback: draft.allow_proxy_failure_direct_fallback,
        });
      } else if (editing?.mode === "edit") {
        await client.updateNetworkProfile({
          network_profile_id: editing.networkProfileId,
          display_name: draft.display_name.trim(),
          mode: draft.mode,
          proxy_endpoint: proxyEndpointForSubmit(),
          verify_tls: draft.verify_tls,
          ...(disablingTls ? { confirm_disable_tls_verification: true } : {}),
          allow_proxy_failure_direct_fallback: draft.allow_proxy_failure_direct_fallback,
        });
      }
      setEditing(null);
      await reload();
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setSaveError(projectSettingsError(code, "network_proxy"));
      // Draft kept on failure (AC4).
    } finally {
      setSaving(false);
    }
  };

  const remove = async (networkProfileId: string) => {
    setSaving(true);
    setDeleteError(null);
    try {
      await client.deleteNetworkProfile(networkProfileId);
      setConfirmingDelete(null);
      await reload();
      await reloadResolved();
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setDeleteError(projectSettingsError(code, "network_proxy"));
      setConfirmingDelete(null);
    } finally {
      setSaving(false);
    }
  };

  const setGlobal = async () => {
    if (globalPick === "") return;
    setGlobalBusy(true);
    setGlobalError(null);
    try {
      await client.setGlobalNetworkProfile(globalPick);
      await reloadResolved();
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setGlobalError(projectSettingsError(code, "network_proxy"));
    } finally {
      setGlobalBusy(false);
    }
  };

  const clearGlobal = async () => {
    setGlobalBusy(true);
    setGlobalError(null);
    try {
      await client.clearGlobalNetworkProfile();
      await reloadResolved();
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setGlobalError(projectSettingsError(code, "network_proxy"));
    } finally {
      setGlobalBusy(false);
    }
  };

  const runTest = async (networkProfileId: string) => {
    setTestingId(networkProfileId);
    setTestError(null);
    setTestResult(null);
    try {
      const result = await client.testNetworkProfile(
        networkProfileId,
        testProviderPick === "" ? undefined : testProviderPick,
      );
      setTestResult({ profileId: networkProfileId, result });
    } catch (err) {
      const code = err instanceof SettingsClientError ? err.code : String(err);
      setTestError(projectSettingsError(code, "network_proxy"));
    } finally {
      setTestingId(null);
    }
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
      data-testid="network-profile-panel"
      style={{
        padding: tokens.spacing.lg,
        backgroundColor: tokens.color.surface.card,
        border: `1px solid ${tokens.color.border.default}`,
        borderRadius: tokens.radius.card,
        maxWidth: 760,
      }}
    >
      <h3 style={{ margin: 0, marginBottom: tokens.spacing.sm, fontSize: tokens.typography.size.cardTitle, fontWeight: 600, color: tokens.color.text.primary }}>
        网络 / 代理 Profile
      </h3>
      <p style={{ margin: 0, marginBottom: tokens.spacing.md, fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
        模式：Direct / System / HTTP / HTTPS / SOCKS5。连接失败不会静默回退直连；仅当显式打开「失败回退直连」且运行时按 P10 §6 允许时才回退，且留有可追溯结果。
      </p>

      {/* Global network source */}
      <div
        data-testid="network-global-section"
        style={{ padding: tokens.spacing.md, border: `1px solid ${tokens.color.border.divider}`, borderRadius: tokens.radius.button, marginBottom: tokens.spacing.md, display: "flex", flexDirection: "column", gap: tokens.spacing.xs }}
      >
        <div data-testid="network-global-resolved" style={{ fontSize: tokens.typography.size.base }}>
          当前生效网络来源：
          {resolved === null
            ? "—"
            : resolved.source === "global" && resolved.network_profile_id
              ? `全局 Profile（${resolved.network_profile_id}，${resolved.mode}）`
              : `${resolved.source}（${resolved.mode}）`}
        </div>
        <div style={{ display: "flex", gap: tokens.spacing.sm, alignItems: "center", flexWrap: "wrap" }}>
          <select
            data-testid="network-global-pick"
            value={globalPick}
            onChange={(e) => setGlobalPick(e.target.value)}
            style={{ ...fieldStyle(false), width: "auto" }}
          >
            <option value="">选择要设为全局的 Profile…</option>
            {profiles.map((p) => (
              <option key={p.network_profile_id} value={p.network_profile_id}>
                {p.display_name}（{p.mode}）
              </option>
            ))}
          </select>
          <button type="button" data-testid="network-global-set-btn" disabled={globalBusy || globalPick === ""} onClick={() => void setGlobal()} style={{ padding: "4px 12px", fontSize: tokens.typography.size.base, border: `1px solid ${tokens.color.accent.primary}`, borderRadius: tokens.radius.button, background: tokens.color.accent.selected, color: tokens.color.accent.primary, cursor: "pointer", opacity: globalBusy || globalPick === "" ? 0.45 : 1 }}>
            设为全局
          </button>
          <button type="button" data-testid="network-global-clear-btn" disabled={globalBusy} onClick={() => void clearGlobal()} style={{ padding: "4px 12px", fontSize: tokens.typography.size.base, border: `1px solid ${tokens.color.border.default}`, borderRadius: tokens.radius.button, background: tokens.color.surface.card, cursor: "pointer" }}>
            清除全局选择
          </button>
        </div>
        {globalError && <SettingsErrorBar testId="network-global-error" error={globalError} />}
      </div>

      {phase === "loading" && (
        <div data-testid="network-panel-loading" aria-busy="true" style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.sm }}>
          {[0, 1].map((i) => (
            <div key={i} style={{ height: 16, borderRadius: tokens.radius.button, background: tokens.color.bg.toolbar, width: `${76 - i * 20}%` }} />
          ))}
        </div>
      )}
      {phase === "error" && loadError && (
        <SettingsErrorBar testId="network-panel-error" error={loadError} onRetry={() => void reload()} />
      )}

      {phase === "ready" && (
        <>
          {/* Connection test controls */}
          <div style={{ display: "flex", gap: tokens.spacing.sm, alignItems: "center", marginBottom: tokens.spacing.sm, flexWrap: "wrap" }}>
            <label style={{ fontSize: tokens.typography.size.secondary }}>
              连接测试使用的 Provider Profile（可选，用于 ProviderAuth 阶段）
              <select
                data-testid="network-test-provider-pick"
                value={testProviderPick}
                onChange={(e) => setTestProviderPick(e.target.value)}
                style={{ ...fieldStyle(false), width: "auto", marginLeft: tokens.spacing.sm }}
              >
                <option value="">（不选择 → ProviderAuth 标记 not_run）</option>
                {providerProfiles.map((p) => (
                  <option key={p.profile_id} value={p.profile_id}>
                    {p.display_name}（{p.profile_id}）
                  </option>
                ))}
              </select>
            </label>
          </div>

          {profiles.length === 0 ? (
            <div data-testid="network-panel-empty" style={{ padding: tokens.spacing.md, border: `1px dashed ${tokens.color.border.default}`, borderRadius: tokens.radius.button, color: tokens.color.text.secondary }}>
              暂无网络 Profile。
            </div>
          ) : (
            <div data-testid="network-panel-list" style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.sm }}>
              {profiles.map((profile) => (
                <div
                  key={profile.network_profile_id}
                  data-testid={`network-row-${profile.network_profile_id}`}
                  style={{ padding: tokens.spacing.md, border: `1px solid ${tokens.color.border.divider}`, borderRadius: tokens.radius.button, display: "flex", flexDirection: "column", gap: tokens.spacing.xs }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.sm, flexWrap: "wrap" }}>
                    <strong>{profile.display_name}</strong>
                    <span style={{ fontFamily: tokens.typography.monospace, fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
                      {profile.network_profile_id}
                    </span>
                    <span data-testid={`network-row-${profile.network_profile_id}-mode`} style={{ fontSize: tokens.typography.size.badge, padding: "1px 8px", borderRadius: tokens.radius.pill, background: tokens.color.accent.selected, color: tokens.color.accent.primary }}>
                      {profile.mode}
                    </span>
                    <span
                      data-testid={`network-row-${profile.network_profile_id}-tls`}
                      style={{
                        fontSize: tokens.typography.size.badge,
                        padding: "1px 8px",
                        borderRadius: tokens.radius.pill,
                        background: profile.tls_verification_state === "enabled" ? "#e6f4ea" : "#fff8e6",
                        color: profile.tls_verification_state === "enabled" ? tokens.color.state.completed : tokens.color.state.blocked,
                        border: `1px solid ${profile.tls_verification_state === "enabled" ? tokens.color.state.completed : tokens.color.state.blocked}`,
                      }}
                    >
                      TLS 校验：{profile.tls_verification_state === "enabled" ? "开启" : "已关闭（经危险确认）"}
                    </span>
                  </div>
                  <div style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
                    endpoint：{profile.proxy_endpoint ?? "—（直连/系统代理）"} · 失败回退直连：{profile.allow_proxy_failure_direct_fallback ? "允许（显式开启）" : "关闭（默认）"}
                  </div>
                  <CredentialField
                    testId={`network-row-${profile.network_profile_id}-credential`}
                    client={client}
                    state={profile.credential_state}
                    hint={profile.credential_hint}
                    target={{ kind: "proxy_auth", network_profile_id: profile.network_profile_id }}
                    onCredentialChanged={() => void reload()}
                    phaseLabel="代理认证 "
                  />
                  <div style={{ display: "flex", gap: tokens.spacing.sm, flexWrap: "wrap" }}>
                    <button type="button" data-testid={`network-row-${profile.network_profile_id}-edit-btn`} onClick={() => openEdit(profile)} style={{ padding: "2px 10px", fontSize: tokens.typography.size.secondary, border: `1px solid ${tokens.color.border.default}`, borderRadius: tokens.radius.button, background: tokens.color.surface.card, cursor: "pointer" }}>
                      编辑
                    </button>
                    <button type="button" data-testid={`network-row-${profile.network_profile_id}-test-btn`} disabled={testingId !== null} onClick={() => void runTest(profile.network_profile_id)} style={{ padding: "2px 10px", fontSize: tokens.typography.size.secondary, border: `1px solid ${tokens.color.border.default}`, borderRadius: tokens.radius.button, background: tokens.color.surface.card, cursor: testingId !== null ? "not-allowed" : "pointer" }}>
                      {testingId === profile.network_profile_id ? "测试中…" : "测试连接"}
                    </button>
                    {confirmingDelete === profile.network_profile_id ? (
                      <>
                        <button type="button" data-testid={`network-row-${profile.network_profile_id}-delete-confirm-btn`} disabled={saving} onClick={() => void remove(profile.network_profile_id)} style={{ padding: "2px 10px", fontSize: tokens.typography.size.secondary, border: `1px solid ${tokens.color.state.failed}`, borderRadius: tokens.radius.button, background: "#fff1f0", color: tokens.color.state.failed, cursor: "pointer" }}>
                          确认删除（仍被引用的 Profile 会被拒绝）
                        </button>
                        <button type="button" data-testid={`network-row-${profile.network_profile_id}-delete-cancel-btn`} onClick={() => setConfirmingDelete(null)} style={{ padding: "2px 10px", fontSize: tokens.typography.size.secondary, border: `1px solid ${tokens.color.border.default}`, borderRadius: tokens.radius.button, background: tokens.color.surface.card, cursor: "pointer" }}>
                          取消
                        </button>
                      </>
                    ) : (
                      <button type="button" data-testid={`network-row-${profile.network_profile_id}-delete-btn`} onClick={() => setConfirmingDelete(profile.network_profile_id)} style={{ padding: "2px 10px", fontSize: tokens.typography.size.secondary, border: `1px solid ${tokens.color.state.failed}`, borderRadius: tokens.radius.button, background: "#fff1f0", color: tokens.color.state.failed, cursor: "pointer" }}>
                        删除
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {deleteError && <div style={{ marginTop: tokens.spacing.md }}><SettingsErrorBar testId="network-panel-delete-error" error={deleteError} /></div>}

          {/* Staged test result */}
          {testError && <div style={{ marginTop: tokens.spacing.md }}><SettingsErrorBar testId="network-test-error" error={testError} /></div>}
          {testResult && (
            <div
              data-testid={`network-test-result-${testResult.profileId}`}
              style={{ marginTop: tokens.spacing.md, padding: tokens.spacing.md, border: `1px solid ${testResult.result.status === "passed" ? tokens.color.state.completed : tokens.color.state.failed}`, borderRadius: tokens.radius.button }}
            >
              <div style={{ fontWeight: 600, marginBottom: tokens.spacing.xs }}>
                测试结果：{testResult.result.status === "passed" ? "全部通过" : `失败（失败阶段：${testResult.result.failed_stage ?? "—"}）`}
                <span data-testid={`network-test-result-${testResult.profileId}-fallback`} style={{ marginLeft: tokens.spacing.md, fontWeight: 400, fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
                  未回退直连（direct_fallback_used={String(testResult.result.direct_fallback_used)}）
                </span>
              </div>
              <div data-testid={`network-test-result-${testResult.profileId}-stages`} style={{ display: "flex", flexDirection: "column", gap: 2, fontSize: tokens.typography.size.secondary }}>
                {STAGE_ORDER.map((stage) => {
                  const entry: StageResult | undefined = testResult.result.stages.find((s) => s.stage === stage);
                  if (!entry) {
                    return (
                      <div key={stage}>
                        {stage}：未执行（upstream_stage_failed）
                      </div>
                    );
                  }
                  if (entry.status === "failed") {
                    return (
                      <div key={stage} style={{ color: tokens.color.state.failed }}>
                        {stage}：失败 — {localizeMessageKey(entry.failure.message_key)}
                      </div>
                    );
                  }
                  return (
                    <div key={stage} style={{ color: entry.status === "passed" ? tokens.color.state.completed : tokens.color.text.muted }}>
                      {stage}：{STAGE_STATUS_TEXT[entry.status]}
                      {entry.status === "not_run" || entry.status === "not_applicable" ? `（${entry.reason}）` : ""}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Create / edit form */}
          <div style={{ marginTop: tokens.spacing.md }}>
            {editing === null ? (
              <button type="button" data-testid="network-new-btn" onClick={openCreate} style={{ padding: "4px 12px", fontSize: tokens.typography.size.base, border: `1px solid ${tokens.color.accent.primary}`, borderRadius: tokens.radius.button, background: tokens.color.accent.selected, color: tokens.color.accent.primary, cursor: "pointer" }}>
                新建网络 Profile
              </button>
            ) : (
              <div data-testid="network-form" style={{ padding: tokens.spacing.md, border: `1px solid ${tokens.color.border.default}`, borderRadius: tokens.radius.button, display: "flex", flexDirection: "column", gap: tokens.spacing.sm, maxWidth: 520 }}>
                <div data-testid="network-form-title" style={{ fontWeight: 600 }}>
                  {editing.mode === "create" ? "新建网络 Profile" : "编辑网络 Profile"}
                </div>

                <label style={{ fontSize: tokens.typography.size.secondary, display: "flex", flexDirection: "column", gap: 2 }}>
                  display_name
                  <input
                    data-testid="network-form-display-name"
                    value={draft.display_name}
                    aria-invalid={Boolean(fieldErrors.display_name)}
                    onChange={(e) => setDraft({ ...draft, display_name: e.target.value })}
                    onInput={(e) => setDraft({ ...draft, display_name: (e.target as HTMLInputElement).value })}
                    style={fieldStyle(Boolean(fieldErrors.display_name))}
                  />
                </label>
                {fieldErrors.display_name && <FieldError testId="network-field-error-display-name" message={fieldErrors.display_name} />}

                <label style={{ fontSize: tokens.typography.size.secondary, display: "flex", flexDirection: "column", gap: 2 }}>
                  mode
                  <select
                    data-testid="network-form-mode"
                    value={draft.mode}
                    onChange={(e) => setDraft({ ...draft, mode: e.target.value as NetworkMode })}
                    style={fieldStyle(false)}
                  >
                    {NETWORK_MODE_VALUES.map((mode) => (
                      <option key={mode} value={mode}>
                        {mode}
                      </option>
                    ))}
                  </select>
                </label>

                <label style={{ fontSize: tokens.typography.size.secondary, display: "flex", flexDirection: "column", gap: 2 }}>
                  proxy_endpoint{modeRequiresProxyEndpoint(draft.mode) ? "（必填，scheme 须与 mode 一致）" : "（Direct/System 必须为空）"}
                  <input
                    data-testid="network-form-proxy-endpoint"
                    value={draft.proxy_endpoint}
                    disabled={!modeRequiresProxyEndpoint(draft.mode)}
                    aria-invalid={Boolean(fieldErrors.proxy_endpoint)}
                    onChange={(e) => setDraft({ ...draft, proxy_endpoint: e.target.value })}
                    onInput={(e) => setDraft({ ...draft, proxy_endpoint: (e.target as HTMLInputElement).value })}
                    placeholder={modeRequiresProxyEndpoint(draft.mode) ? `${draft.mode === "HTTP" ? "http" : draft.mode === "HTTPS" ? "https" : "socks5"}://host:port` : ""}
                    style={fieldStyle(Boolean(fieldErrors.proxy_endpoint))}
                  />
                </label>
                {fieldErrors.proxy_endpoint && <FieldError testId="network-field-error-proxy-endpoint" message={fieldErrors.proxy_endpoint} />}

                <label style={{ fontSize: tokens.typography.size.base, display: "flex", gap: tokens.spacing.xs, alignItems: "center" }}>
                  <input
                    type="checkbox"
                    data-testid="network-form-verify-tls"
                    checked={draft.verify_tls}
                    onChange={(e) => setDraft({ ...draft, verify_tls: e.target.checked, tlsDangerConfirmed: e.target.checked ? false : draft.tlsDangerConfirmed })}
                  />
                  verify_tls（TLS 证书校验）
                </label>

                {!draft.verify_tls && (
                  <div
                    data-testid="network-form-tls-danger"
                    style={{ padding: tokens.spacing.md, border: `1px solid ${tokens.color.state.blocked}`, background: "#fff8e6", borderRadius: tokens.radius.button, display: "flex", flexDirection: "column", gap: tokens.spacing.xs }}
                  >
                    <div style={{ color: tokens.color.state.blocked, fontWeight: 600 }}>
                      ⚠ 危险操作：关闭 TLS 校验会使连接容易受到中间人攻击。
                    </div>
                    <label style={{ fontSize: tokens.typography.size.base, display: "flex", gap: tokens.spacing.xs, alignItems: "center" }}>
                      <input
                        type="checkbox"
                        data-testid="network-form-tls-danger-confirm"
                        checked={draft.tlsDangerConfirmed}
                        onChange={(e) => setDraft({ ...draft, tlsDangerConfirmed: e.target.checked })}
                      />
                      我了解风险，确认关闭（提交时携带 confirm_disable_tls_verification: true）
                    </label>
                    {fieldErrors.verify_tls && <FieldError testId="network-field-error-verify-tls" message={fieldErrors.verify_tls} />}
                  </div>
                )}

                <label style={{ fontSize: tokens.typography.size.base, display: "flex", gap: tokens.spacing.xs, alignItems: "flex-start" }}>
                  <input
                    type="checkbox"
                    data-testid="network-form-fallback"
                    checked={draft.allow_proxy_failure_direct_fallback}
                    onChange={(e) => setDraft({ ...draft, allow_proxy_failure_direct_fallback: e.target.checked })}
                  />
                  <span>
                    失败回退直连（allow_proxy_failure_direct_fallback，默认关闭）
                    <br />
                    <span style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
                      仅显式开启后才允许运行时在代理失败时回退直连，且会留下可追溯结果；默认关闭（代理失败不静默直连）。
                    </span>
                  </span>
                </label>

                {saveError && <SettingsErrorBar testId="network-form-save-error" error={saveError} />}

                <div style={{ display: "flex", gap: tokens.spacing.sm }}>
                  <button
                    type="button"
                    data-testid="network-form-save-btn"
                    disabled={saving || (!draft.verify_tls && !draft.tlsDangerConfirmed)}
                    onClick={() => void save()}
                    style={{ padding: "4px 12px", fontSize: tokens.typography.size.base, border: `1px solid ${tokens.color.accent.primary}`, borderRadius: tokens.radius.button, background: tokens.color.accent.selected, color: tokens.color.accent.primary, cursor: "pointer", opacity: saving || (!draft.verify_tls && !draft.tlsDangerConfirmed) ? 0.45 : 1 }}
                  >
                    {saving ? "保存中…" : "保存"}
                  </button>
                  <button type="button" data-testid="network-form-cancel-btn" disabled={saving} onClick={() => setEditing(null)} style={{ padding: "4px 12px", fontSize: tokens.typography.size.base, border: `1px solid ${tokens.color.border.default}`, borderRadius: tokens.radius.button, background: tokens.color.surface.card, cursor: "pointer" }}>
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
