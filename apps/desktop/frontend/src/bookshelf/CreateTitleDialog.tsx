import { useState, type FormEvent } from "react";
import { tokens } from "../theme/tokens";

type CreateErrorKey =
  | "LIBRARY_INVALID_INPUT"
  | "LIBRARY_BOOK_NOT_FOUND"
  | "LIBRARY_WRITE_FAILED"
  | "LIBRARY_UNAVAILABLE"
  | "LIBRARY_OPERATION_FAILED";

const CREATE_ERROR_COPY: Record<CreateErrorKey, { category: string; message: string }> = {
  LIBRARY_INVALID_INPUT: { category: "校验失败", message: "标题不能为空，请修改后重试。" },
  LIBRARY_BOOK_NOT_FOUND: { category: "未找到作品", message: "所属作品不存在或已不可用，请重新选择作品后重试。" },
  LIBRARY_WRITE_FAILED: { category: "保存失败", message: "保存未完成，请检查书架后重试。" },
  LIBRARY_UNAVAILABLE: { category: "服务不可用", message: "书架服务当前不可用，请刷新书架后重试。" },
  LIBRARY_OPERATION_FAILED: { category: "操作未完成", message: "操作未完成，请刷新书架后重试。" },
};

function safeCreateError(raw: unknown) {
  const value = raw && typeof raw === "object"
    ? (raw as { code?: unknown; message_key?: unknown }).message_key ?? (raw as { code?: unknown }).code
    : raw;
  const key = typeof value === "string" && Object.prototype.hasOwnProperty.call(CREATE_ERROR_COPY, value)
    ? value as CreateErrorKey
    : "LIBRARY_OPERATION_FAILED";
  return CREATE_ERROR_COPY[key];
}

export function CreateTitleDialog({
  entity,
  onClose,
  onSubmit,
}: {
  entity: "作品" | "章节";
  onClose: () => void;
  onSubmit: (title: string) => Promise<void>;
}) {
  const [title, setTitle] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<{ category: string; message: string } | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    if (!title.trim()) {
      setError({ category: "校验失败", message: "标题不能为空，请修改后重试。" });
      return;
    }

    setBusy(true);
    try {
      await onSubmit(title);
      onClose();
    } catch (cause) {
      setError(safeCreateError(cause));
    } finally {
      setBusy(false);
    }
  };

  const inputId = `create-${entity}-title`;
  return (
    <div
      data-testid="create-title-dialog-backdrop"
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0, 0, 0, 0.45)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
    >
      <form
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-title-dialog-heading"
        data-testid="create-title-dialog"
        onSubmit={(event) => void handleSubmit(event)}
        style={{
          width: 420,
          boxSizing: "border-box",
          backgroundColor: tokens.color.surface.card,
          borderRadius: tokens.radius.card,
          boxShadow: "0 10px 25px rgba(0, 0, 0, 0.2)",
          padding: tokens.spacing.lg,
          display: "flex",
          flexDirection: "column",
          gap: tokens.spacing.md,
          color: tokens.color.text.primary,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 id="create-title-dialog-heading" style={{ margin: 0, fontSize: tokens.typography.size.panelTitle }}>
            新建{entity}
          </h3>
          <button
            type="button"
            data-testid="create-title-dialog-close-btn"
            aria-label="关闭"
            disabled={busy}
            onClick={onClose}
            style={{ border: 0, background: "none", fontSize: 18, cursor: busy ? "not-allowed" : "pointer" }}
          >
            ✕
          </button>
        </div>

        <label htmlFor={inputId} style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.xs }}>
          <span>{entity}标题</span>
          <input
            id={inputId}
            data-testid="create-title-input"
            type="text"
            required
            autoComplete="off"
            value={title}
            disabled={busy}
            onChange={(event) => setTitle(event.target.value)}
            onInput={(event) => setTitle(event.currentTarget.value)}
            style={{
              height: 34,
              boxSizing: "border-box",
              padding: "0 8px",
              border: `1px solid ${tokens.color.border.default}`,
              borderRadius: tokens.radius.button,
              backgroundColor: tokens.color.surface.card,
              color: tokens.color.text.primary,
              fontSize: tokens.typography.size.base,
            }}
          />
        </label>

        {error && (
          <div
            role="alert"
            data-testid="create-title-error"
            data-error-category={error.category}
            style={{ color: tokens.color.state.failed, fontSize: tokens.typography.size.secondary }}
          >
            {error.category}：{error.message}
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "flex-end", gap: tokens.spacing.sm }}>
          <button type="button" disabled={busy} onClick={onClose}>
            取消
          </button>
          <button type="submit" data-testid="create-title-submit-btn" disabled={busy}>
            {busy ? "正在创建…" : `创建${entity}`}
          </button>
        </div>
      </form>
    </div>
  );
}
