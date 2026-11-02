import { useCallback, useEffect, useRef, useState } from "react";
import {
  SettingsClient,
  SettingsClientError,
  type CleanupOutcome,
  type CleanupPreview,
} from "./client";
import { projectSettingsError, type SettingsSurfaceError } from "./errors";
import { SettingsErrorBar } from "./SettingsErrorBar";
import { tokens } from "../theme/tokens";

/**
 * SETTINGS-OPEN-B-2 §4.3 — cache / Revision partition. The ONLY real
 * operation surface here is preview + manual cleanup + pending retry:
 *
 *   preview → cleanup_preview (auto on mount) — "可清理 N 个文件 / X MB" plus
 *             the `pending_cleanups` ledger size;
 *   cleanup → cleanup_run — structured removed/failed/skipped counts and the
 *             per-file failure detail;
 *   retry   → cleanup_retry_pending — replays the persisted failure ledger
 *             through the same safe-prefix predicate.
 *
 * Deliberately absent: automatic-cleanup days and Revision retention policy.
 * There is no scheduler/storage consumer for them, so the panel shows the
 * read-only note instead of fake switches (design §4.3).
 */

type CleanupOperation = "cleanup" | "retry";

type PanelPhase = "loading" | "error" | "ready";

/** Project a rejected invoke into the closed §9 surface projection. The raw
 * payload (message text, paths, core internals) never reaches the DOM. */
function projectCleanupError(error: unknown): SettingsSurfaceError {
  const code = error instanceof SettingsClientError ? error.code : "";
  return projectSettingsError(code, "settings_resolution");
}

/** Human byte size for the preview summary (B / KB / MB, one decimal). */
function formatCleanupBytes(sizeBytes: number): string {
  if (!Number.isFinite(sizeBytes) || sizeBytes <= 0) return "0 B";
  if (sizeBytes < 1024) return `${Math.floor(sizeBytes)} B`;
  if (sizeBytes < 1024 * 1024) return `${(sizeBytes / 1024).toFixed(1)} KB`;
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
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

export function CacheRevisionPanel({ client }: { client: SettingsClient }) {
  const [phase, setPhase] = useState<PanelPhase>("loading");
  const [preview, setPreview] = useState<CleanupPreview | null>(null);
  const [loadError, setLoadError] = useState<SettingsSurfaceError | null>(null);
  const [busy, setBusy] = useState<CleanupOperation | null>(null);
  const [lastOperation, setLastOperation] = useState<CleanupOperation>("cleanup");
  const [actionError, setActionError] = useState<SettingsSurfaceError | null>(null);
  const [outcome, setOutcome] = useState<CleanupOutcome | null>(null);
  const [outcomeOperation, setOutcomeOperation] = useState<CleanupOperation | null>(null);
  // Synchronous re-entry guard: React state updates are async, so a rapid
  // second click could still observe `busy === null`; the ref cannot.
  const busyRef = useRef<CleanupOperation | null>(null);

  const loadPreview = useCallback(async () => {
    setPhase("loading");
    setLoadError(null);
    try {
      const next = await client.getCleanupPreview();
      setPreview(next);
      setPhase("ready");
    } catch (error) {
      setLoadError(projectCleanupError(error));
      setPhase("error");
    }
  }, [client]);

  useEffect(() => {
    void loadPreview();
  }, [loadPreview]);

  /** Post-operation re-read. A failure here must not replace the successful
   * action result with a load error, so the last known preview is kept. */
  const refreshPreview = useCallback(async () => {
    try {
      const next = await client.getCleanupPreview();
      setPreview(next);
      setPhase("ready");
      setLoadError(null);
    } catch {
      // Silent refresh: the action outcome above is already authoritative.
    }
  }, [client]);

  const execute = async (operation: CleanupOperation) => {
    if (busyRef.current) return;
    busyRef.current = operation;
    setBusy(operation);
    setLastOperation(operation);
    setActionError(null);
    setOutcome(null);
    setOutcomeOperation(null);
    try {
      const result =
        operation === "cleanup" ? await client.runCleanup() : await client.retryPendingCleanups();
      setOutcome(result);
      setOutcomeOperation(operation);
      await refreshPreview();
    } catch (error) {
      setActionError(projectCleanupError(error));
    } finally {
      busyRef.current = null;
      setBusy(null);
    }
  };

  const targetCount = preview?.targets.length ?? 0;
  const pendingCount = preview?.pending_cleanups ?? 0;
  const ready = phase === "ready" && preview !== null;
  const blocking = busy !== null;
  const canRunCleanup = ready && !blocking && targetCount > 0;
  const canRetryPending = ready && !blocking && pendingCount > 0;
  const failedItems = outcome?.items.filter((item) => item.status === "failed") ?? [];

  return (
    <section data-testid="cache-revision-panel" style={cardStyle}>
      <h3
        data-testid="cache-revision-panel-title"
        style={{
          margin: 0,
          marginBottom: tokens.spacing.sm,
          fontSize: tokens.typography.size.cardTitle,
          fontWeight: 600,
          color: tokens.color.text.primary,
        }}
      >
        缓存 / Revision
      </h3>
      <p
        data-testid="cache-revision-panel-description"
        style={{ ...secondaryTextStyle, margin: 0, marginBottom: tokens.spacing.xs }}
      >
        预览并手动清理可重建缓存；失败文件会写入挂起清单，可单独重试。清理只作用于安全缓存前缀，不触碰用户源文件与 current / pinned Revision。
      </p>
      <p
        data-testid="cache-revision-panel-policy-note"
        style={{ ...secondaryTextStyle, margin: 0, marginBottom: tokens.spacing.md }}
      >
        只读说明：Revision 保留策略与自动清理未开放——当前没有调度器与存储消费点，因此不提供自动清理天数或保留策略控件。
      </p>

      {phase === "loading" && (
        <div
          data-testid="cache-revision-panel-loading"
          aria-busy="true"
          style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.sm }}
        >
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              style={{
                height: 14,
                borderRadius: tokens.radius.button,
                background: tokens.color.bg.toolbar,
                width: `${70 - i * 15}%`,
              }}
            />
          ))}
        </div>
      )}

      {phase === "error" && loadError && (
        <SettingsErrorBar
          testId="cache-revision-panel-load-error"
          error={loadError}
          onRetry={() => void loadPreview()}
        />
      )}

      {ready && preview && (
        <>
          <div data-testid="cache-revision-panel-preview">
            <div
              data-testid="cache-revision-panel-summary"
              style={{ fontSize: tokens.typography.size.base, color: tokens.color.text.primary }}
            >
              可清理{" "}
              <strong data-testid="cache-revision-panel-file-count">{targetCount}</strong> 个文件 /{" "}
              <span data-testid="cache-revision-panel-total-bytes">
                {formatCleanupBytes(preview.total_bytes)}
              </span>
            </div>
            <div
              data-testid="cache-revision-panel-pending"
              style={{ ...secondaryTextStyle, marginTop: tokens.spacing.xs }}
            >
              挂起项：
              <span data-testid="cache-revision-panel-pending-count">{pendingCount}</span> 个
            </div>
            {targetCount === 0 && (
              <div
                data-testid="cache-revision-panel-empty"
                style={{
                  marginTop: tokens.spacing.md,
                  padding: tokens.spacing.md,
                  border: `1px dashed ${tokens.color.border.default}`,
                  borderRadius: tokens.radius.button,
                  ...secondaryTextStyle,
                }}
              >
                无可清理文件
              </div>
            )}
          </div>

          <div
            style={{
              marginTop: tokens.spacing.md,
              display: "flex",
              alignItems: "center",
              gap: tokens.spacing.md,
            }}
          >
            <button
              type="button"
              data-testid="cache-revision-panel-cleanup-btn"
              disabled={!canRunCleanup}
              aria-disabled={!canRunCleanup}
              onClick={() => void execute("cleanup")}
              style={actionButtonStyle(canRunCleanup, true)}
            >
              {busy === "cleanup" ? "清理中…" : "清理缓存"}
            </button>
            <button
              type="button"
              data-testid="cache-revision-panel-retry-btn"
              disabled={!canRetryPending}
              aria-disabled={!canRetryPending}
              onClick={() => void execute("retry")}
              style={actionButtonStyle(canRetryPending, false)}
            >
              {busy === "retry" ? "重试中…" : "重试挂起项"}
            </button>
            <span
              data-testid="cache-revision-panel-busy-state"
              style={{ fontSize: tokens.typography.size.secondary, color: tokens.color.text.secondary }}
            >
              {busy === "cleanup" ? "正在清理缓存…" : busy === "retry" ? "正在重试挂起项…" : ""}
            </span>
          </div>

          {actionError && (
            <div style={{ marginTop: tokens.spacing.md }}>
              <SettingsErrorBar
                testId="cache-revision-panel-action-error"
                error={actionError}
                onRetry={() => void execute(lastOperation)}
              />
            </div>
          )}

          {outcome && (
            <div
              data-testid="cache-revision-panel-result"
              data-operation={outcomeOperation ?? lastOperation}
              data-removed={outcome.removed}
              data-failed={outcome.failed}
              data-skipped={outcome.skipped}
              style={{
                marginTop: tokens.spacing.md,
                padding: tokens.spacing.md,
                border: `1px solid ${tokens.color.border.default}`,
                borderRadius: tokens.radius.button,
                backgroundColor: tokens.color.bg.toolbar,
              }}
            >
              <div
                data-testid="cache-revision-panel-result-counts"
                style={{ fontSize: tokens.typography.size.base, color: tokens.color.text.primary }}
              >
                {outcomeOperation === "retry" ? "重试结果：" : "清理结果："}成功{" "}
                <span data-testid="cache-revision-panel-removed">{outcome.removed}</span> 个 · 失败{" "}
                <span data-testid="cache-revision-panel-failed">{outcome.failed}</span> 个 · 跳过{" "}
                <span data-testid="cache-revision-panel-skipped">{outcome.skipped}</span> 个
              </div>
              {failedItems.length > 0 && (
                <ul
                  data-testid="cache-revision-panel-failures"
                  style={{ margin: `${tokens.spacing.sm}px 0 0`, paddingLeft: tokens.spacing.lg }}
                >
                  {failedItems.map((item, index) => (
                    <li
                      key={`${item.relative_path}-${index}`}
                      data-testid="cache-revision-panel-failure"
                      style={{
                        fontSize: tokens.typography.size.secondary,
                        color: tokens.color.state.failed,
                        wordBreak: "break-all",
                      }}
                    >
                      <span data-testid="cache-revision-panel-failure-path">
                        {item.relative_path}
                      </span>
                      {item.detail !== undefined && (
                        <span data-testid="cache-revision-panel-failure-detail">
                          {" — "}
                          {item.detail}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </>
      )}
    </section>
  );
}
