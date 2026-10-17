import { useEffect, useState } from "react";
import { LibraryClient } from "../library/client";
import type { BookSummary, ChapterNavSummary, ImportSummary } from "../library/types";
import { parseSemanticError, type SemanticErrorInfo } from "./error";
import type { DuplicatePolicy } from "./types";
import { tokens } from "../theme/tokens";

export interface ImportDialogProps {
  isOpen: boolean;
  books: BookSummary[];
  chapters: ChapterNavSummary[];
  initialBookId?: string | null;
  initialChapterId?: string | null;
  client?: LibraryClient;
  onClose: () => void;
  onImportSuccess?: (chapterId: string, summary: ImportSummary) => void;
}

export function ImportDialog({
  isOpen,
  books,
  chapters,
  initialBookId,
  initialChapterId,
  client,
  onClose,
  onImportSuccess,
}: ImportDialogProps) {
  const [selectedBookId, setSelectedBookId] = useState<string>(initialBookId || "");
  const [selectedChapterId, setSelectedChapterId] = useState<string>(initialChapterId || "");
  const [duplicatePolicy, setDuplicatePolicy] = useState<DuplicatePolicy>("skip");
  const [busy, setBusy] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [report, setReport] = useState<ImportSummary | null>(null);
  const [errorInfo, setErrorInfo] = useState<SemanticErrorInfo | null>(null);

  // Sync initial selection
  useEffect(() => {
    if (initialBookId) setSelectedBookId(initialBookId);
    if (initialChapterId) setSelectedChapterId(initialChapterId);
  }, [initialBookId, initialChapterId]);

  // Reset dialog state when opened
  useEffect(() => {
    if (isOpen) {
      setBusy(false);
      setStatusMessage(null);
      setReport(null);
      setErrorInfo(null);
      if (initialBookId) setSelectedBookId(initialBookId);
      if (initialChapterId) setSelectedChapterId(initialChapterId);
    }
  }, [isOpen, initialBookId, initialChapterId]);

  // Keyboard Esc handling
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !busy) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, busy, onClose]);

  if (!isOpen) return null;

  const activeClient = client || new LibraryClient();

  const handleImportFile = async () => {
    if (!selectedChapterId) return;
    setBusy(true);
    setStatusMessage("正在打开系统选择器并导入页面...");
    setErrorInfo(null);
    setReport(null);

    try {
      const summary = await activeClient.importFile(selectedChapterId, duplicatePolicy);
      if (summary.cancelled) {
        setStatusMessage("用户取消了文件选择。");
        setBusy(false);
        return;
      }
      setReport(summary);
      setStatusMessage("导入已完成。");
    } catch (err) {
      const parsed = parseSemanticError(err);
      setErrorInfo(parsed);
      setStatusMessage(null);
    } finally {
      setBusy(false);
    }
  };

  const handleImportFolder = async () => {
    if (!selectedChapterId) return;
    setBusy(true);
    setStatusMessage("正在打开系统选择器并导入文件夹...");
    setErrorInfo(null);
    setReport(null);

    try {
      const summary = await activeClient.importFolder(selectedChapterId, duplicatePolicy);
      if (summary.cancelled) {
        setStatusMessage("用户取消了文件夹选择。");
        setBusy(false);
        return;
      }
      setReport(summary);
      setStatusMessage("导入已完成。");
    } catch (err) {
      const parsed = parseSemanticError(err);
      setErrorInfo(parsed);
      setStatusMessage(null);
    } finally {
      setBusy(false);
    }
  };

  const handleFinish = () => {
    if (report && selectedChapterId) {
      onImportSuccess?.(selectedChapterId, report);
    }
    onClose();
  };

  return (
    <div
      data-testid="import-dialog-backdrop"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.45)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        data-testid="import-dialog"
        style={{
          width: 480,
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
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 style={{ margin: 0, fontSize: tokens.typography.size.panelTitle, fontWeight: 600 }}>
            导入页面到章节
          </h3>
          <button
            type="button"
            data-testid="import-dialog-close-btn"
            disabled={busy}
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              fontSize: 18,
              cursor: busy ? "not-allowed" : "pointer",
              color: tokens.color.text.secondary,
            }}
          >
            ✕
          </button>
        </div>

        {/* Target Book & Chapter picker */}
        <div style={{ display: "flex", flexDirection: "column", gap: tokens.spacing.sm }}>
          <div>
            <label
              style={{
                display: "block",
                fontSize: tokens.typography.size.secondary,
                fontWeight: 600,
                color: tokens.color.text.secondary,
                marginBottom: 4,
              }}
            >
              目标作品
            </label>
            <select
              data-testid="import-target-book-select"
              value={selectedBookId}
              disabled={busy || !!initialBookId}
              onChange={(e) => {
                setSelectedBookId(e.target.value);
                setSelectedChapterId("");
              }}
              style={{
                width: "100%",
                height: 32,
                borderRadius: tokens.radius.button,
                border: `1px solid ${tokens.color.border.default}`,
                padding: "0 8px",
                fontSize: tokens.typography.size.base,
                backgroundColor: tokens.color.surface.card,
                color: tokens.color.text.primary,
              }}
            >
              <option value="">-- 请选择作品 --</option>
              {books.map((b) => (
                <option key={b.book_id} value={b.book_id}>
                  {b.title}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label
              style={{
                display: "block",
                fontSize: tokens.typography.size.secondary,
                fontWeight: 600,
                color: tokens.color.text.secondary,
                marginBottom: 4,
              }}
            >
              目标章节
            </label>
            <select
              data-testid="import-target-chapter-select"
              value={selectedChapterId}
              disabled={busy || !!initialChapterId || chapters.length === 0}
              onChange={(e) => setSelectedChapterId(e.target.value)}
              style={{
                width: "100%",
                height: 32,
                borderRadius: tokens.radius.button,
                border: `1px solid ${tokens.color.border.default}`,
                padding: "0 8px",
                fontSize: tokens.typography.size.base,
                backgroundColor: tokens.color.surface.card,
                color: tokens.color.text.primary,
              }}
            >
              <option value="">
                {chapters.length === 0 ? "-- 当前作品暂无章节 --" : "-- 请选择章节 --"}
              </option>
              {chapters.map((ch) => (
                <option key={ch.chapter_id} value={ch.chapter_id}>
                  {ch.chapter_number ? `#${ch.chapter_number} ` : ""}
                  {ch.title || "未命名章节"}
                </option>
              ))}
            </select>
          </div>
        </div>

        {chapters.length === 0 && (
          <div
            role="status"
            aria-live="polite"
            data-testid="import-unavailable-notice"
            style={{
              padding: tokens.spacing.sm,
              borderRadius: tokens.radius.card,
              backgroundColor: tokens.color.bg.toolbar,
              color: tokens.color.text.secondary,
              fontSize: tokens.typography.size.secondary,
            }}
          >
            {books.length === 0
              ? "未开放：空书架暂不支持创建作品和章节，当前无法导入文件或文件夹。"
              : "未开放：当前没有可导入的目标章节，请准备可用章节后再选择文件或文件夹导入。"}
          </div>
        )}

        {/* Duplicate policy selection (Default: skip) */}
        <div style={{ backgroundColor: tokens.color.bg.toolbar, padding: tokens.spacing.sm, borderRadius: tokens.radius.card }}>
          <div style={{ fontSize: tokens.typography.size.secondary, fontWeight: 600, color: tokens.color.text.secondary, marginBottom: 6 }}>
            重复项策略 (Duplicate Policy)
          </div>
          <div style={{ display: "flex", gap: tokens.spacing.md }}>
            <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: tokens.typography.size.base, cursor: "pointer" }}>
              <input
                type="radio"
                name="duplicate_policy"
                value="skip"
                data-testid="import-policy-skip"
                checked={duplicatePolicy === "skip"}
                disabled={busy}
                onChange={() => setDuplicatePolicy("skip")}
              />
              跳过重复 (skip - 默认)
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: tokens.typography.size.base, cursor: "pointer" }}>
              <input
                type="radio"
                name="duplicate_policy"
                value="import_as_new"
                data-testid="import-policy-new"
                checked={duplicatePolicy === "import_as_new"}
                disabled={busy}
                onChange={() => setDuplicatePolicy("import_as_new")}
              />
              作为新页面导入 (import_as_new)
            </label>
          </div>
        </div>

        {/* Native picker launch buttons */}
        {!report && (
          <div style={{ display: "flex", gap: tokens.spacing.sm, marginTop: 4 }}>
            <button
              type="button"
              data-testid="import-file-btn"
              disabled={busy || !selectedChapterId}
              onClick={handleImportFile}
              title="系统文件对话框支持 Ctrl+A 全选当前目录的图片或 PDF"
              style={{
                flex: 1,
                height: 38,
                backgroundColor: tokens.color.accent.primary,
                color: tokens.color.text.inverse,
                border: "none",
                borderRadius: tokens.radius.button,
                fontSize: tokens.typography.size.base,
                fontWeight: 600,
                cursor: busy || !selectedChapterId ? "not-allowed" : "pointer",
                opacity: busy || !selectedChapterId ? 0.5 : 1,
              }}
            >
              📄 选择图片 / PDF 文件（可多选）
            </button>
            <button
              type="button"
              data-testid="import-folder-btn"
              disabled={busy || !selectedChapterId}
              onClick={handleImportFolder}
              title="只导入所选文件夹的直接子项，不递归子目录"
              style={{
                flex: 1,
                height: 38,
                backgroundColor: tokens.color.surface.card,
                color: tokens.color.accent.primary,
                border: `1px solid ${tokens.color.accent.primary}`,
                borderRadius: tokens.radius.button,
                fontSize: tokens.typography.size.base,
                fontWeight: 600,
                cursor: busy || !selectedChapterId ? "not-allowed" : "pointer",
                opacity: busy || !selectedChapterId ? 0.5 : 1,
              }}
            >
              📁 选择图片文件夹
            </button>
          </div>
        )}

        {!report && (
          <div data-testid="import-selection-hint" style={{ color: tokens.color.text.muted, fontSize: tokens.typography.size.secondary }}>
            支持 Ctrl+A 全选；文件夹导入仅读取直接子项，不递归子目录。
          </div>
        )}

        {/* Busy progress state */}
        {busy && (
          <div
            data-testid="import-progress-indicator"
            style={{
              padding: tokens.spacing.md,
              textAlign: "center",
              backgroundColor: tokens.color.accent.selected,
              borderRadius: tokens.radius.card,
              color: tokens.color.accent.primary,
              fontSize: tokens.typography.size.base,
            }}
          >
            <div style={{ fontWeight: 600, marginBottom: 4 }}>⏳ 正在导入中...</div>
            <div style={{ fontSize: tokens.typography.size.secondary }}>
              请在弹出的系统对话框中选择文件或文件夹，处理期间请勿关闭窗口
            </div>
          </div>
        )}

        {/* Cancellation or info note */}
        {!busy && statusMessage && !report && !errorInfo && (
          <div
            data-testid="import-status-message"
            style={{
              padding: tokens.spacing.sm,
              fontSize: tokens.typography.size.secondary,
              color: tokens.color.text.secondary,
              backgroundColor: tokens.color.bg.toolbar,
              borderRadius: tokens.radius.card,
              textAlign: "center",
            }}
          >
            {statusMessage}
          </div>
        )}

        {/* Error presentation (W28) */}
        {!busy && errorInfo && (
          <div
            data-testid="import-error-banner"
            style={{
              padding: tokens.spacing.sm,
              borderRadius: tokens.radius.card,
              backgroundColor: "#fef2f2",
              border: `1px solid ${tokens.color.state.failed}`,
              color: tokens.color.state.failed,
            }}
          >
            <div style={{ fontWeight: 600, fontSize: tokens.typography.size.base }}>
              {errorInfo.title} ({errorInfo.code})
            </div>
            <div style={{ fontSize: tokens.typography.size.secondary, marginTop: 2 }}>
              {errorInfo.message}
            </div>
          </div>
        )}

        {/* Completed aggregate report (keeps Core's per-file paths and errors private). */}
        {!busy && report && (
          <div
            data-testid="import-report-view"
            style={{
              border: `1px solid ${tokens.color.border.default}`,
              borderRadius: tokens.radius.card,
              padding: tokens.spacing.md,
              backgroundColor: tokens.color.bg.toolbar,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: tokens.spacing.sm,
              }}
            >
              <span style={{ fontWeight: 600, fontSize: tokens.typography.size.cardTitle }}>
                导入报告 (Import Report)
              </span>
              <span
                style={{
                  fontSize: tokens.typography.size.badge,
                  color: tokens.color.state.completed,
                  border: `1px solid ${tokens.color.state.completed}`,
                  borderRadius: tokens.radius.pill,
                  padding: "1px 6px",
                  fontWeight: 600,
                }}
              >
                完成
              </span>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: tokens.spacing.sm,
                fontSize: tokens.typography.size.base,
              }}
            >
              <div
                style={{
                  backgroundColor: tokens.color.surface.card,
                  padding: tokens.spacing.sm,
                  borderRadius: tokens.radius.button,
                  border: `1px solid ${tokens.color.border.divider}`,
                }}
              >
                <div style={{ color: tokens.color.text.secondary, fontSize: tokens.typography.size.secondary }}>
                  已导入 (imported)
                </div>
                <div
                  data-testid="report-imported-files"
                  style={{ fontSize: 18, fontWeight: 700, color: tokens.color.state.completed }}
                >
                  {report.imported_files}
                </div>
              </div>

              <div
                style={{
                  backgroundColor: tokens.color.surface.card,
                  padding: tokens.spacing.sm,
                  borderRadius: tokens.radius.button,
                  border: `1px solid ${tokens.color.border.divider}`,
                }}
              >
                <div style={{ color: tokens.color.text.secondary, fontSize: tokens.typography.size.secondary }}>
                  跳过重复 (skipped)
                </div>
                <div
                  data-testid="report-skipped-files"
                  style={{ fontSize: 18, fontWeight: 700, color: tokens.color.state.skipped }}
                >
                  {report.skipped_files}
                </div>
              </div>

              <div
                style={{
                  backgroundColor: tokens.color.surface.card,
                  padding: tokens.spacing.sm,
                  borderRadius: tokens.radius.button,
                  border: `1px solid ${tokens.color.border.divider}`,
                }}
              >
                <div style={{ color: tokens.color.text.secondary, fontSize: tokens.typography.size.secondary }}>
                  导入失败 (rejected)
                </div>
                <div
                  data-testid="report-rejected-files"
                  style={{
                    fontSize: 18,
                    fontWeight: 700,
                    color: report.rejected_files > 0 ? tokens.color.state.failed : tokens.color.text.muted,
                  }}
                >
                  {report.rejected_files}
                </div>
              </div>

              <div
                style={{
                  backgroundColor: tokens.color.surface.card,
                  padding: tokens.spacing.sm,
                  borderRadius: tokens.radius.button,
                  border: `1px solid ${tokens.color.border.divider}`,
                }}
              >
                <div style={{ color: tokens.color.text.secondary, fontSize: tokens.typography.size.secondary }}>
                  待处理 (pending)
                </div>
                <div
                  data-testid="report-pending-files"
                  style={{ fontSize: 18, fontWeight: 700, color: tokens.color.text.muted }}
                >
                  {report.pending_files}
                </div>
              </div>
            </div>

            {report.skipped_files > 0 && (
              <p data-testid="report-skipped-reason" style={{ margin: `${tokens.spacing.sm} 0 0`, color: tokens.color.text.secondary, fontSize: tokens.typography.size.secondary }}>
                已按“跳过重复”策略忽略重复内容。
              </p>
            )}
            {report.rejected_files > 0 && (
              <p data-testid="report-rejected-reason" style={{ margin: `${tokens.spacing.sm} 0 0`, color: tokens.color.state.failed, fontSize: tokens.typography.size.secondary }}>
                文件未通过导入校验，或处理时读取、保存失败；已隐藏原始错误详情。
              </p>
            )}
            {report.pending_files > 0 && (
              <p data-testid="report-pending-reason" style={{ margin: `${tokens.spacing.sm} 0 0`, color: tokens.color.text.secondary, fontSize: tokens.typography.size.secondary }}>
                导入中断，剩余文件尚未处理。
              </p>
            )}

            <div style={{ marginTop: tokens.spacing.md, display: "flex", justifyContent: "flex-end" }}>
              <button
                type="button"
                data-testid="import-finish-btn"
                onClick={handleFinish}
                style={{
                  padding: "6px 16px",
                  backgroundColor: tokens.color.accent.primary,
                  color: tokens.color.text.inverse,
                  border: "none",
                  borderRadius: tokens.radius.button,
                  fontSize: tokens.typography.size.base,
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                完成
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
