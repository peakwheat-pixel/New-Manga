import { useState } from "react";
import type { BookSummary } from "../library/types";
import { tokens } from "../theme/tokens";

export interface PermanentDeleteConfirmDialogProps {
  targets: BookSummary[];
  onClose: () => void;
  onConfirm: () => Promise<void>;
}

export function PermanentDeleteConfirmDialog({
  targets,
  onClose,
  onConfirm,
}: PermanentDeleteConfirmDialogProps) {
  const [understood, setUnderstood] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!understood || busy) return;
    setBusy(true);
    setError(null);
    try {
      await onConfirm();
      onClose();
    } catch (err) {
      const msg =
        err instanceof Error
          ? err.message
          : typeof err === "string"
          ? err
          : "永久删除失败，请重试";
      setError(msg);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div
      data-testid="permanent-delete-confirm-dialog-backdrop"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.65)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 2000,
      }}
    >
      <div
        data-testid="permanent-delete-confirm-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
        style={{
          width: 520,
          maxHeight: "85vh",
          backgroundColor: tokens.color.surface.card,
          border: `1px solid ${tokens.color.border.default}`,
          borderRadius: tokens.radius.card,
          boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "16px 20px",
            borderBottom: `1px solid ${tokens.color.border.default}`,
            backgroundColor: "#2a1515",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 20 }}>⚠️</span>
            <h3
              id="confirm-dialog-title"
              data-testid="confirm-dialog-title"
              style={{
                margin: 0,
                fontSize: 16,
                fontWeight: 600,
                color: "#ff6b6b",
              }}
            >
              永久删除确认（不可逆）
            </h3>
          </div>
          <button
            type="button"
            data-testid="cancel-permanent-delete-btn"
            onClick={onClose}
            disabled={busy}
            style={{
              background: "none",
              border: "none",
              color: tokens.color.text.muted,
              fontSize: 18,
              cursor: "pointer",
            }}
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div
          style={{
            padding: "20px",
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: 16,
          }}
        >
          {/* Target books list and total count */}
          <div>
            <div
              data-testid="confirm-targets-count"
              style={{
                fontSize: 14,
                fontWeight: 600,
                color: tokens.color.text.primary,
                marginBottom: 8,
              }}
            >
              即将永久删除 {targets.length} 部作品：
            </div>
            <ul
              data-testid="confirm-targets-list"
              style={{
                margin: 0,
                padding: "8px 12px 8px 28px",
                maxHeight: 140,
                overflowY: "auto",
                backgroundColor: tokens.color.bg.toolbar,
                borderRadius: tokens.radius.button,
                border: `1px solid ${tokens.color.border.default}`,
                fontSize: 13,
                color: tokens.color.text.secondary,
              }}
            >
              {targets.map((b) => (
                <li
                  key={b.book_id}
                  data-testid={`confirm-target-item-${b.book_id}`}
                  style={{ marginBottom: 4 }}
                >
                  <span style={{ fontWeight: 500, color: tokens.color.text.primary }}>
                    {b.title}
                  </span>
                  {b.original_title ? ` (${b.original_title})` : ""}
                </li>
              ))}
            </ul>
          </div>

          {/* Mandatory notices */}
          <div
            data-testid="permanent-delete-notices"
            style={{
              backgroundColor: "rgba(255, 107, 107, 0.08)",
              border: "1px solid rgba(255, 107, 107, 0.25)",
              borderRadius: tokens.radius.button,
              padding: "12px 14px",
              fontSize: 12,
              lineHeight: 1.6,
              color: "#ff9999",
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            <div data-testid="notice-irreversible">
              • <strong>App 回收站无法恢复</strong>：此操作将永久删除所选作品的数据库记录、章节、页面及受控 Managed Copy，不可撤销。
            </div>
            <div data-testid="notice-user-export">
              • <strong>用户导出目录内的文件会保留</strong>：已导出的作品文件不会被删除或修改。
            </div>
            <div data-testid="notice-history-backup">
              • <strong>全库历史备份不处理且可能含旧快照</strong>：此操作不会清理或改写全库历史备份，旧备份中可能仍保留删除前的数据快照。
            </div>
          </div>

          {/* Explicit checkbox confirmation */}
          <label
            data-testid="confirm-checkbox-label"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              cursor: "pointer",
              userSelect: "none",
              fontSize: 14,
              color: tokens.color.text.primary,
              fontWeight: 500,
              padding: "4px 0",
            }}
          >
            <input
              type="checkbox"
              data-testid="confirm-understand-checkbox"
              checked={understood}
              onChange={(e) => setUnderstood(e.target.checked)}
              disabled={busy}
              style={{ width: 16, height: 16, cursor: "pointer" }}
            />
            <span>我理解不可恢复</span>
          </label>

          {/* Error message */}
          {error && (
            <div
              data-testid="permanent-delete-error"
              style={{
                color: "#ff6b6b",
                fontSize: 13,
                backgroundColor: "rgba(255, 107, 107, 0.15)",
                padding: "8px 12px",
                borderRadius: tokens.radius.button,
              }}
            >
              {error}
            </div>
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: "12px 20px",
            borderTop: `1px solid ${tokens.color.border.default}`,
            backgroundColor: tokens.color.bg.toolbar,
            display: "flex",
            justifyContent: "flex-end",
            gap: 12,
          }}
        >
          <button
            type="button"
            data-testid="confirm-dialog-cancel-btn"
            onClick={onClose}
            disabled={busy}
            style={{
              padding: "6px 16px",
              fontSize: 13,
              backgroundColor: tokens.color.surface.card,
              border: `1px solid ${tokens.color.border.default}`,
              borderRadius: tokens.radius.button,
              color: tokens.color.text.secondary,
              cursor: "pointer",
            }}
          >
            取消
          </button>
          <button
            type="button"
            data-testid="confirm-permanent-delete-btn"
            onClick={handleSubmit}
            disabled={!understood || busy}
            style={{
              padding: "6px 18px",
              fontSize: 13,
              fontWeight: 600,
              backgroundColor: understood && !busy ? "#d32f2f" : "#4a2525",
              border: "none",
              borderRadius: tokens.radius.button,
              color: understood && !busy ? "#ffffff" : tokens.color.text.muted,
              cursor: understood && !busy ? "pointer" : "not-allowed",
              transition: "background-color 0.15s ease",
            }}
          >
            {busy ? "正在删除..." : "确认永久删除"}
          </button>
        </div>
      </div>
    </div>
  );
}
