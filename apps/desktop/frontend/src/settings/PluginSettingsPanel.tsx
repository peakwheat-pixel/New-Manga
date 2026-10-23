import { useCallback, useEffect, useRef, useState } from "react";
import {
  SettingsClient,
  SettingsClientError,
  type PluginAuditEvent,
  type PluginEntry,
  type PluginsSnapshot,
} from "./client";
import { tokens } from "../theme/tokens";

/**
 * PLUGIN-RUNTIME-1 §4.1–§4.4 (user authorization 2026-10-23, D1–D6) — the
 * Plugin/Hooks management face.
 *
 * Real operations only:
 *
 *   list      → `plugins_list` (re-discovers `<data_root>/plugins` every
 *               read, so the panel always reflects the directory on disk);
 *   global    → `plugins_set_enabled` (the default-OFF kill switch);
 *   per-plugin→ `plugins_set_plugin_enabled` (the Core re-validates the
 *               manifest every call; a rejected plugin can never be enabled);
 *   audit     → `plugins_audit_list` (append-only `plugin_events`);
 *   open dir  → `plugins_open_directory` (Rust-local opener, not a Core
 *               command).
 *
 * First release only loads permission-free plugins (`permissions: []`);
 * hooks run in an isolated subprocess with a hard timeout, so a crashing
 * plugin is an audit row, never a Core failure.
 */

export interface PluginPanelClientLike {
  listPlugins(): Promise<PluginsSnapshot>;
  setPluginsEnabled(enabled: boolean): Promise<{ global_enabled: boolean }>;
  setPluginEnabled(
    pluginId: string,
    enabled: boolean,
  ): Promise<{ plugin_id: string; enabled: boolean }>;
  listPluginAudit(limit?: number): Promise<PluginAuditEvent[]>;
  openPluginDirectory(): Promise<void>;
}

/** Map a rejected invoke's code onto fixed zh-CN copy (no internals leak). */
export function pluginErrorMessage(error: unknown): string {
  const code = error instanceof SettingsClientError ? error.code : "";
  switch (code) {
    case "PLUGIN_NOT_FOUND":
      return "插件不存在：目录可能已被移动或删除，请刷新列表。";
    case "PLUGIN_NOT_LOADED":
      return "该插件未通过校验（manifest 被拒绝），不能启用；请查看拒绝原因并修正。";
    case "PLUGIN_INVALID_REQUEST":
      return "请求格式不正确，请刷新后重试。";
    case "PLUGIN_HOOK_TIMEOUT":
      return "插件 Hook 超时已被跳过；主流程未受影响。";
    case "PLUGIN_HOOK_FAILED":
      return "插件 Hook 执行失败已被跳过；主流程未受影响。";
    case "PLUGIN_DIRECTORY_UNAVAILABLE":
      return "无法打开插件目录，请稍后重试。";
    case "CORE_UNAVAILABLE":
      return "插件服务当前不可用，请稍后重试。";
    default:
      return "插件操作失败，请稍后重试。";
  }
}

const EVENT_LABELS: Record<string, string> = {
  load_ok: "加载成功",
  load_rejected: "拒绝加载",
  enabled: "已启用",
  disabled: "已禁用",
  hook_invoked: "Hook 调用",
  plugin_error: "Hook 错误",
};

function formatTime(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString("zh-CN", { hour12: false });
}

const cardStyle = {
  padding: tokens.spacing.lg,
  backgroundColor: tokens.color.surface.card,
  border: `1px solid ${tokens.color.border.default}`,
  borderRadius: tokens.radius.card,
  maxWidth: 820,
} as const;

const secondaryTextStyle = {
  fontSize: tokens.typography.size.secondary,
  color: tokens.color.text.secondary,
  lineHeight: tokens.typography.lineHeight,
} as const;

function buttonStyle(enabled: boolean, primary = false) {
  return {
    padding: "4px 14px",
    fontSize: tokens.typography.size.base,
    border: `1px solid ${enabled && primary ? tokens.color.accent.primary : tokens.color.border.default}`,
    borderRadius: tokens.radius.button,
    background: enabled && primary ? tokens.color.accent.selected : tokens.color.bg.toolbar,
    color: enabled ? tokens.color.text.primary : tokens.color.text.muted,
    cursor: enabled ? "pointer" : "not-allowed",
    opacity: enabled ? 1 : 0.45,
  } as const;
}

function statusLabel(entry: PluginEntry): { text: string; color: string } {
  if (entry.status === "rejected") return { text: "已拒绝", color: "#ff9999" };
  if (entry.status === "enabled") return { text: "已启用", color: tokens.color.state.completed };
  return { text: "已禁用", color: tokens.color.text.muted };
}

export function PluginSettingsPanel({ client }: { client?: PluginPanelClientLike }) {
  const activeClient: PluginPanelClientLike = client ?? new SettingsClient();
  const [loading, setLoading] = useState(true);
  const [snapshot, setSnapshot] = useState<PluginsSnapshot | null>(null);
  const [audit, setAudit] = useState<PluginAuditEvent[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const busyRef = useRef(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [nextSnapshot, nextAudit] = await Promise.all([
        activeClient.listPlugins(),
        activeClient.listPluginAudit(20),
      ]);
      setSnapshot(nextSnapshot);
      setAudit(nextAudit);
    } catch (error) {
      setLoadError(pluginErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, [activeClient]);

  useEffect(() => {
    void load();
  }, [load]);

  const refreshAudit = async () => {
    try {
      setAudit(await activeClient.listPluginAudit(20));
    } catch {
      // the audit read is best-effort; the main action already reported.
    }
  };

  const toggleGlobal = async (enabled: boolean) => {
    if (busyRef.current) return;
    busyRef.current = true;
    setBusy(true);
    setActionError(null);
    setNotice(null);
    try {
      const result = await activeClient.setPluginsEnabled(enabled);
      setNotice(
        result.global_enabled
          ? "插件系统已启用（默认关闭；启用后只有已启用且声明了该 Hook 的插件会被调用）。"
          : "插件系统已关闭：任何 Hook 都不会被调用。",
      );
      await load();
    } catch (error) {
      setActionError(pluginErrorMessage(error));
    } finally {
      busyRef.current = false;
      setBusy(false);
    }
  };

  const togglePlugin = async (entry: PluginEntry, enabled: boolean) => {
    if (busyRef.current) return;
    busyRef.current = true;
    setBusy(true);
    setActionError(null);
    setNotice(null);
    try {
      await activeClient.setPluginEnabled(entry.plugin_id, enabled);
      setNotice(
        enabled
          ? `已启用插件 ${entry.plugin_id}。`
          : `已禁用插件 ${entry.plugin_id}。`,
      );
      await load();
      await refreshAudit();
    } catch (error) {
      setActionError(pluginErrorMessage(error));
    } finally {
      busyRef.current = false;
      setBusy(false);
    }
  };

  const openDirectory = async () => {
    if (busyRef.current) return;
    busyRef.current = true;
    setBusy(true);
    setActionError(null);
    try {
      await activeClient.openPluginDirectory();
      setNotice("已打开插件目录：把插件目录（含 manifest.json）放进去后点「刷新」。");
    } catch (error) {
      setActionError(pluginErrorMessage(error));
    } finally {
      busyRef.current = false;
      setBusy(false);
    }
  };

  return (
    <section
      data-testid="plugin-settings-panel"
      style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.lg, maxWidth: 820 }}
    >
      <header style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.sm }}>
        <h2 style={{ margin: 0, fontSize: tokens.typography.size.panelTitle, color: tokens.color.text.primary }}>
          Plugin / Hooks
        </h2>
        <p data-testid="plugin-settings-description" style={{ margin: 0, ...secondaryTextStyle }}>
          本地目录插件（manifest v1）：默认全部禁用；首发只加载无权限插件（permissions: []）。
          每个 Hook 在独立受信任子进程中运行（超时或崩溃只跳过该次调用并记录审计，主流程继续）。
        </p>
      </header>

      <div style={cardStyle}>
        <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.sm, flexWrap: "wrap" }}>
          <label style={{ display: "flex", alignItems: "center", gap: 6, ...secondaryTextStyle, marginRight: "auto" }}>
            <input
              type="checkbox"
              data-testid="plugin-settings-global-toggle"
              checked={snapshot?.global_enabled === true}
              disabled={loading || busy || snapshot === null}
              onChange={(event) => void toggleGlobal(event.target.checked)}
            />
            启用插件系统（默认关闭）
          </label>
          <button
            type="button"
            data-testid="plugin-settings-open-dir-btn"
            onClick={() => void openDirectory()}
            disabled={busy}
            style={buttonStyle(!busy)}
          >
            打开插件目录
          </button>
          <button
            type="button"
            data-testid="plugin-settings-refresh-btn"
            onClick={() => void load()}
            disabled={loading || busy}
            style={buttonStyle(!loading && !busy)}
          >
            刷新
          </button>
        </div>

        {loading && (
          <div data-testid="plugin-settings-loading" style={{ marginTop: tokens.spacing.sm, ...secondaryTextStyle }}>
            正在读取插件目录…
          </div>
        )}

        {!loading && loadError && (
          <div
            data-testid="plugin-settings-load-error"
            style={{
              marginTop: tokens.spacing.sm,
              padding: tokens.spacing.md,
              borderRadius: tokens.radius.card,
              border: `1px solid ${tokens.color.border.default}`,
              ...secondaryTextStyle,
              color: "#ff9999",
              backgroundColor: "rgba(255, 107, 107, 0.08)",
            }}
          >
            {loadError}
          </div>
        )}

        {!loading && !loadError && snapshot && snapshot.plugins.length === 0 && (
          <div data-testid="plugin-settings-empty" style={{ marginTop: tokens.spacing.sm, ...secondaryTextStyle }}>
            还没有发现插件。点「打开插件目录」放入插件目录（含 manifest.json）后点「刷新」。
          </div>
        )}

        {!loading && !loadError && snapshot && snapshot.plugins.length > 0 && (
          <ul
            data-testid="plugin-settings-list"
            style={{ listStyle: "none", margin: `${tokens.spacing.sm}px 0 0`, padding: 0, display: "flex", flexDirection: "column", gap: 6 }}
          >
            {snapshot.plugins.map((entry) => {
              const label = statusLabel(entry);
              return (
                <li
                  key={entry.plugin_id}
                  data-testid={`plugin-settings-item-${entry.plugin_id}`}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: tokens.spacing.sm,
                    padding: "6px 8px",
                    border: `1px solid ${tokens.color.border.default}`,
                    borderRadius: tokens.radius.button,
                    flexWrap: "wrap",
                  }}
                >
                  <span style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.primary, minWidth: 150 }}>
                    {entry.name || entry.plugin_id}
                  </span>
                  <span style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
                    {entry.version || "—"}
                  </span>
                  <span
                    data-testid={`plugin-settings-status-${entry.plugin_id}`}
                    style={{ fontSize: tokens.typography.size.secondary, color: label.color }}
                  >
                    {label.text}
                  </span>
                  <span style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.muted }}>
                    {entry.hooks.length > 0 ? entry.hooks.join(", ") : "未声明 Hook"}
                  </span>
                  {entry.reason && (
                    <span
                      data-testid={`plugin-settings-reason-${entry.plugin_id}`}
                      style={{ fontSize: tokens.typography.size.secondary, color: "#ff9999", flexBasis: "100%" }}
                    >
                      拒绝原因：{entry.reason}
                    </span>
                  )}
                  <span style={{ marginLeft: "auto" }}>
                    <button
                      type="button"
                      data-testid={`plugin-settings-toggle-${entry.plugin_id}`}
                      onClick={() => void togglePlugin(entry, entry.status !== "enabled")}
                      disabled={busy || entry.status === "rejected"}
                      style={buttonStyle(!busy && entry.status !== "rejected", entry.status !== "enabled")}
                    >
                      {entry.status === "enabled" ? "禁用" : "启用"}
                    </button>
                  </span>
                </li>
              );
            })}
          </ul>
        )}

        {notice && (
          <div
            data-testid="plugin-settings-notice"
            style={{
              marginTop: tokens.spacing.sm,
              padding: "6px 10px",
              borderRadius: tokens.radius.button,
              ...secondaryTextStyle,
              backgroundColor: "rgba(80, 200, 120, 0.12)",
              color: tokens.color.state.completed,
            }}
          >
            {notice}
          </div>
        )}

        {actionError && (
          <div
            data-testid="plugin-settings-error"
            style={{
              marginTop: tokens.spacing.sm,
              padding: "6px 10px",
              borderRadius: tokens.radius.button,
              ...secondaryTextStyle,
              backgroundColor: "rgba(255, 107, 107, 0.08)",
              color: "#ff9999",
            }}
          >
            {actionError}
          </div>
        )}
      </div>

      <div data-testid="plugin-settings-audit-card" style={cardStyle}>
        <h3 style={{ margin: `0 0 ${tokens.spacing.sm}px`, fontSize: tokens.typography.size.cardTitle, color: tokens.color.text.primary }}>
          审计（最近 20 条）
        </h3>
        {audit.length === 0 ? (
          <p data-testid="plugin-settings-audit-empty" style={{ margin: 0, ...secondaryTextStyle }}>
            暂无审计记录。
          </p>
        ) : (
          <ul
            data-testid="plugin-settings-audit-list"
            style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 4 }}
          >
            {audit.map((event) => (
              <li
                key={event.event_id}
                data-testid={`plugin-settings-audit-${event.event_id}`}
                style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}
              >
                {formatTime(event.occurred_at)} · {EVENT_LABELS[event.event_type] ?? event.event_type} ·{" "}
                {event.plugin_id}
                {event.hook_name ? ` · ${event.hook_name}` : ""}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div data-testid="plugin-settings-policy-note" style={cardStyle}>
        <p style={{ margin: 0, ...secondaryTextStyle }}>
          安全说明：插件在 Windows AppContainer 中运行（容器 + Job Object，超时或关闭时整棵进程树被回收）。
          permissions: [] 时容器不具备任何网络能力，也无法读取数据目录/用户文件——只被授予只读访问
          本插件目录与 Python 运行时（解释器/DLLs/Lib 与 runner 属于只读例外）；插件之间共用同一容器（v1，不保证跨插件目录隔离）。
          子进程环境最小化（仅系统变量与 Python 标记；应用私有变量/代理/凭据不传递）。沙箱初始化失败会拒绝
          执行该次 Hook（fail-closed）并记审计。带权限声明的插件一律拒绝加载；启用状态与审计存放在本机数据库。
        </p>
      </div>
    </section>
  );
}
