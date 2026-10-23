import { useCallback, useEffect, useRef, useState } from "react";
import {
  SettingsClient,
  SettingsClientError,
  type BackupEntry,
  type BackupRestoreReport,
} from "./client";
import { tokens } from "../theme/tokens";

/**
 * SETTINGS-OPEN-C-2-BACKUP §3.4 — backup / restore partition.
 *
 * The real operation surface (no fake switches):
 *
 *   create  → `backup_create` (manual package into the Core's fixed backup
 *             root; the WebView never picks a directory);
 *   list    → `backup_list` (re-read after every mutation);
 *   restore → `backup_restore` after an explicit overwrite dialog — the Core
 *             additionally refuses while a Run is active and writes a
 *             `pre_restore` package first;
 *   delete  → `backup_delete` after a confirm dialog.
 *
 * Deliberately absent: automatic-backup schedules and retention keys. There is
 * no scheduler consumer for them, so the panel shows the read-only note
 * instead of fake controls (design §3.2, D3–D6 ruling).
 */

export interface BackupPanelClientLike {
  listBackups(): Promise<BackupEntry[]>;
  createBackup(): Promise<{ backup_id: string; verified: boolean }>;
  restoreBackup(backupId: string): Promise<BackupRestoreReport>;
  deleteBackup(backupId: string): Promise<{ removed: boolean }>;
}

type BusyOperation = "create" | "restore" | "delete" | null;

/** Map a rejected invoke's code onto fixed zh-CN copy. The raw Core message
 * (paths, internals) is never rendered. */
export function backupErrorMessage(error: unknown): string {
  const code = error instanceof SettingsClientError ? error.code : "";
  switch (code) {
    case "BACKUP_NOT_FOUND":
      return "备份不存在，可能已被删除或清理；请刷新列表后重试。";
    case "BACKUP_CORRUPT":
      return "备份包校验失败（可能已损坏），未执行恢复；当前数据未被改动。";
    case "BACKUP_RESTORE_BUSY":
      return "有任务正在运行，恢复已拒绝；请先停止任务或等待其结束后重试。";
    case "BACKUP_RESTORE_INCOMPLETE":
      return "数据已恢复到备份点，但部分 revision 引用缺失；请查看结果说明，必要时用恢复前备份回滚。";
    case "BACKUP_CREATE_FAILED":
      return "创建备份失败，请检查磁盘空间后重试。";
    case "BACKUP_MALFORMED":
      return "备份列表格式异常，请稍后重试。";
    case "CORE_UNAVAILABLE":
      return "备份服务当前不可用，请稍后重试。";
    default:
      return "备份操作失败，请稍后重试。";
  }
}

function shortId(backupId: string): string {
  return backupId.slice(0, 8);
}

function formatBytes(sizeBytes: number): string {
  if (!Number.isFinite(sizeBytes) || sizeBytes <= 0) return "0 B";
  if (sizeBytes < 1024) return `${Math.floor(sizeBytes)} B`;
  if (sizeBytes < 1024 * 1024) return `${(sizeBytes / 1024).toFixed(1)} KB`;
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatCreatedAt(value: string): string {
  if (!value) return "—";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString("zh-CN", { hour12: false });
}

const cardStyle = {
  padding: tokens.spacing.lg,
  backgroundColor: tokens.color.surface.card,
  border: `1px solid ${tokens.color.border.default}`,
  borderRadius: tokens.radius.card,
  maxWidth: 780,
} as const;

const secondaryTextStyle = {
  fontSize: tokens.typography.size.secondary,
  color: tokens.color.text.secondary,
  lineHeight: tokens.typography.lineHeight,
} as const;

function actionButtonStyle(enabled: boolean, primary: boolean) {
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

function rowButtonStyle(enabled: boolean) {
  return {
    padding: "2px 10px",
    fontSize: tokens.typography.size.secondary,
    border: `1px solid ${tokens.color.border.default}`,
    borderRadius: tokens.radius.button,
    background: tokens.color.bg.toolbar,
    color: enabled ? tokens.color.text.primary : tokens.color.text.muted,
    cursor: enabled ? "pointer" : "not-allowed",
    opacity: enabled ? 1 : 0.45,
  } as const;
}

export function BackupSettingsPanel({
  client,
}: {
  client?: BackupPanelClientLike;
}) {
  const activeClient: BackupPanelClientLike = client ?? new SettingsClient();
  const [loading, setLoading] = useState(true);
  const [entries, setEntries] = useState<BackupEntry[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [busy, setBusy] = useState<BusyOperation>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [restoreTarget, setRestoreTarget] = useState<BackupEntry | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<BackupEntry | null>(null);
  // Synchronous re-entry guard: state updates are async, the ref is not.
  const busyRef = useRef<BusyOperation>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      setEntries(await activeClient.listBackups());
    } catch (error) {
      setLoadError(backupErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, [activeClient]);

  useEffect(() => {
    void load();
  }, [load]);

  const createBackup = async () => {
    if (busyRef.current) return;
    busyRef.current = "create";
    setBusy("create");
    setActionError(null);
    setNotice(null);
    try {
      const created = await activeClient.createBackup();
      setNotice(
        created.verified
          ? `已创建备份 ${shortId(created.backup_id)}（校验通过）。`
          : `已创建备份 ${shortId(created.backup_id)}，但校验未通过，请不要依赖它。`,
      );
      await load();
    } catch (error) {
      setActionError(backupErrorMessage(error));
    } finally {
      busyRef.current = null;
      setBusy(null);
    }
  };

  const confirmRestore = async () => {
    const target = restoreTarget;
    if (!target || busyRef.current) return;
    busyRef.current = "restore";
    setBusy("restore");
    setActionError(null);
    setNotice(null);
    try {
      const report = await activeClient.restoreBackup(target.backup_id);
      setNotice(
        `已从备份 ${shortId(report.restored_from)} 恢复（恢复前备份 ${shortId(
          report.pre_restore_backup_id,
        )}）。其他页面可能仍显示旧数据，请手动刷新。`,
      );
      setRestoreTarget(null);
      await load();
    } catch (error) {
      setActionError(backupErrorMessage(error));
    } finally {
      busyRef.current = null;
      setBusy(null);
    }
  };

  const confirmDelete = async () => {
    const target = deleteTarget;
    if (!target || busyRef.current) return;
    busyRef.current = "delete";
    setBusy("delete");
    setActionError(null);
    setNotice(null);
    try {
      await activeClient.deleteBackup(target.backup_id);
      setNotice(`已删除备份 ${shortId(target.backup_id)}。`);
      setDeleteTarget(null);
      await load();
    } catch (error) {
      setActionError(backupErrorMessage(error));
    } finally {
      busyRef.current = null;
      setBusy(null);
    }
  };

  return (
    <section
      data-testid="backup-settings-panel"
      style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.lg, maxWidth: 780 }}
    >
      <header style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.sm }}>
        <h2 style={{ margin: 0, fontSize: tokens.typography.size.panelTitle, color: tokens.color.text.primary }}>
          备份 / 恢复
        </h2>
        <p data-testid="backup-settings-description" style={{ margin: 0, ...secondaryTextStyle }}>
          备份包为单个 .nmbak 文件（库 + 受管文件 + 清单校验），保存在本机备份目录。恢复会覆盖当前全部数据，恢复前自动创建可回滚的
          pre_restore 备份。
        </p>
      </header>

      <div style={cardStyle}>
        <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.sm, flexWrap: "wrap" }}>
          <span data-testid="backup-settings-summary" style={{ ...secondaryTextStyle, marginRight: "auto" }}>
            备份：{entries.length} 个
          </span>
          <button
            type="button"
            data-testid="backup-settings-refresh-btn"
            onClick={() => void load()}
            disabled={loading || busy !== null}
            style={rowButtonStyle(!loading && busy === null)}
          >
            刷新
          </button>
          <button
            type="button"
            data-testid="backup-settings-create-btn"
            onClick={() => void createBackup()}
            disabled={loading || busy !== null}
            title="立即创建一份手动备份"
            style={actionButtonStyle(!loading && busy === null, true)}
          >
            {busy === "create" ? "正在备份…" : "立即备份"}
          </button>
        </div>

        {loading && (
          <div data-testid="backup-settings-loading" style={{ marginTop: tokens.spacing.sm, ...secondaryTextStyle }}>
            正在读取备份列表…
          </div>
        )}

        {!loading && loadError && (
          <div
            data-testid="backup-settings-load-error"
            style={{
              marginTop: tokens.spacing.sm,
              padding: tokens.spacing.md,
              border: `1px solid ${tokens.color.border.default}`,
              borderRadius: tokens.radius.card,
              ...secondaryTextStyle,
              color: "#ff9999",
              backgroundColor: "rgba(255, 107, 107, 0.08)",
            }}
          >
            {loadError}
          </div>
        )}

        {!loading && !loadError && entries.length === 0 && (
          <div data-testid="backup-settings-empty" style={{ marginTop: tokens.spacing.sm, ...secondaryTextStyle }}>
            还没有备份。点击「立即备份」创建第一份。
          </div>
        )}

        {!loading && !loadError && entries.length > 0 && (
          <ul
            data-testid="backup-settings-list"
            style={{ listStyle: "none", margin: `${tokens.spacing.sm}px 0 0`, padding: 0, display: "flex", flexDirection: "column", gap: 6 }}
          >
            {entries.map((entry) => (
              <li
                key={entry.backup_id}
                data-testid={`backup-settings-item-${entry.backup_id}`}
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
                <span style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.primary, minWidth: 88 }}>
                  {entry.backup_type}
                </span>
                <span style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
                  {formatCreatedAt(entry.created_at)}
                </span>
                <span style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}>
                  {formatBytes(entry.size_bytes)}
                </span>
                <span
                  data-testid={`backup-settings-verified-${entry.backup_id}`}
                  style={{
                    fontSize: tokens.typography.size.secondary,
                    color: entry.verified ? tokens.color.state.completed : "#ff9999",
                  }}
                >
                  {entry.verified ? "校验通过" : "校验未通过"}
                </span>
                <span style={{ marginLeft: "auto", display: "flex", gap: 6 }}>
                  <button
                    type="button"
                    data-testid={`backup-settings-restore-btn-${entry.backup_id}`}
                    onClick={() => {
                      setActionError(null);
                      setRestoreTarget(entry);
                    }}
                    disabled={busy !== null}
                    style={rowButtonStyle(busy === null)}
                  >
                    恢复
                  </button>
                  <button
                    type="button"
                    data-testid={`backup-settings-delete-btn-${entry.backup_id}`}
                    onClick={() => {
                      setActionError(null);
                      setDeleteTarget(entry);
                    }}
                    disabled={busy !== null}
                    style={rowButtonStyle(busy === null)}
                  >
                    删除
                  </button>
                </span>
              </li>
            ))}
          </ul>
        )}

        {notice && (
          <div
            data-testid="backup-settings-notice"
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
            data-testid="backup-settings-error"
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

      <div data-testid="backup-settings-policy-note" style={cardStyle}>
        <p style={{ margin: 0, ...secondaryTextStyle }}>
          只读说明：自动备份（定时 / 启动时）未开放——当前没有调度器消费自动备份计划与保留策略，因此本页只提供手动备份；
          恢复前自动创建的 pre_restore 备份也计入上方列表。
        </p>
      </div>

      {restoreTarget && (
        <div data-testid="backup-settings-restore-dialog" style={cardStyle}>
          <h3 style={{ margin: `0 0 ${tokens.spacing.sm}px`, fontSize: tokens.typography.size.cardTitle, color: tokens.color.text.primary }}>
            恢复备份（覆盖当前全部数据）
          </h3>
          <p style={{ margin: 0, ...secondaryTextStyle }}>
            将从备份 {shortId(restoreTarget.backup_id)}（{formatCreatedAt(restoreTarget.created_at)}）恢复：
            用备份中的数据库与受管文件覆盖当前数据；操作前会自动创建 pre_restore 备份，恢复失败可回滚。
            正在运行的任务会阻止恢复（请先停止任务）。
          </p>
          <div style={{ display: "flex", gap: tokens.spacing.sm, justifyContent: "flex-end", marginTop: tokens.spacing.md }}>
            <button
              type="button"
              data-testid="backup-settings-restore-cancel-btn"
              onClick={() => setRestoreTarget(null)}
              disabled={busy !== null}
              style={rowButtonStyle(busy === null)}
            >
              取消
            </button>
            <button
              type="button"
              data-testid="backup-settings-restore-confirm-btn"
              onClick={() => void confirmRestore()}
              disabled={busy !== null}
              style={actionButtonStyle(busy === null, true)}
            >
              {busy === "restore" ? "正在恢复…" : "覆盖并恢复"}
            </button>
          </div>
        </div>
      )}

      {deleteTarget && (
        <div data-testid="backup-settings-delete-dialog" style={cardStyle}>
          <h3 style={{ margin: `0 0 ${tokens.spacing.sm}px`, fontSize: tokens.typography.size.cardTitle, color: tokens.color.text.primary }}>
            删除备份
          </h3>
          <p style={{ margin: 0, ...secondaryTextStyle }}>
            将删除备份 {shortId(deleteTarget.backup_id)}（{formatCreatedAt(deleteTarget.created_at)}）。删除后无法用于恢复。
          </p>
          <div style={{ display: "flex", gap: tokens.spacing.sm, justifyContent: "flex-end", marginTop: tokens.spacing.md }}>
            <button
              type="button"
              data-testid="backup-settings-delete-cancel-btn"
              onClick={() => setDeleteTarget(null)}
              disabled={busy !== null}
              style={rowButtonStyle(busy === null)}
            >
              取消
            </button>
            <button
              type="button"
              data-testid="backup-settings-delete-confirm-btn"
              onClick={() => void confirmDelete()}
              disabled={busy !== null}
              style={actionButtonStyle(busy === null, true)}
            >
              {busy === "delete" ? "正在删除…" : "删除"}
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
