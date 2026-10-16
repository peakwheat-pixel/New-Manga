import { tokens } from "../theme/tokens";
import type { ReaderLayout, ReaderStartPosition, ReadingMode } from "./types";

export interface ReaderToolbarProps {
  chapterTitle?: string | null;
  chapterId?: string | null;
  bookId?: string | null;
  mode: ReadingMode;
  layout: ReaderLayout;
  currentPageIndex: number; // 0-based
  totalPages: number;
  webtoonProgressPercent?: number;
  startPosition: ReaderStartPosition;
  onModeChange: (mode: ReadingMode) => void;
  onStartPositionChange?: (pos: ReaderStartPosition) => void;
  onPageChange?: (index: number) => void;
  onReturnToBookshelf?: () => void;
  isSaving?: boolean;
}

export function ReaderToolbar({
  chapterTitle,
  chapterId,
  bookId,
  mode,
  layout,
  currentPageIndex,
  totalPages,
  webtoonProgressPercent,
  startPosition,
  onModeChange,
  onStartPositionChange,
  onPageChange,
  onReturnToBookshelf,
  isSaving,
}: ReaderToolbarProps) {
  const isWebtoon = layout === "webtoon_vertical";
  const displayTitle = chapterTitle || (chapterId ? `章节: ${chapterId}` : "尚未选择章节");
  const fullTooltip = bookId ? `${displayTitle} (作品: ${bookId})` : displayTitle;

  return (
    <header
      data-testid="reader-toolbar"
      style={{
        height: 48,
        backgroundColor: tokens.color.bg.toolbar,
        borderBottom: `1px solid ${tokens.color.border.default}`,
        padding: `0 ${tokens.spacing.md}px`,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        boxSizing: "border-box",
        userSelect: "none",
        zIndex: 10,
        gap: tokens.spacing.md,
      }}
    >
      {/* Left: Return button & Title */}
      <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.md, minWidth: 0, flexShrink: 1 }}>
        <button
          type="button"
          data-testid="reader-return-btn"
          onClick={onReturnToBookshelf}
          title="返回书架 (Esc)"
          style={{
            padding: "4px 10px",
            fontSize: tokens.typography.size.base,
            backgroundColor: tokens.color.surface.card,
            color: tokens.color.text.primary,
            border: `1px solid ${tokens.color.border.default}`,
            borderRadius: tokens.radius.button,
            cursor: "pointer",
            flexShrink: 0,
          }}
        >
          ← 返回书架
        </button>

        <span
          data-testid="reader-chapter-title"
          title={fullTooltip}
          style={{
            fontWeight: 600,
            fontSize: tokens.typography.size.cardTitle,
            color: tokens.color.text.primary,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {displayTitle}
        </span>

        {isSaving && (
          <span
            data-testid="reader-saving-indicator"
            style={{
              fontSize: tokens.typography.size.secondary,
              color: tokens.color.text.muted,
              fontStyle: "italic",
            }}
          >
            保存中…
          </span>
        )}
      </div>

      {/* Center: Position indicator & Paged navigation controls */}
      <div
        data-testid="reader-position-control"
        style={{
          display: "flex",
          alignItems: "center",
          gap: tokens.spacing.sm,
          fontSize: tokens.typography.size.base,
          color: tokens.color.text.primary,
          flexShrink: 0,
        }}
      >
        {isWebtoon ? (
          <div data-testid="reader-webtoon-position" style={{ fontWeight: 500 }}>
            进度: {Math.round(webtoonProgressPercent ?? 0)}%
          </div>
        ) : totalPages > 0 ? (
          <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.xs }}>
            <button
              type="button"
              data-testid="reader-prev-page-btn"
              disabled={currentPageIndex <= 0}
              onClick={() => onPageChange?.(currentPageIndex - 1)}
              style={{
                padding: "2px 8px",
                fontSize: tokens.typography.size.secondary,
                backgroundColor: tokens.color.surface.card,
                color: currentPageIndex <= 0 ? tokens.color.text.muted : tokens.color.text.primary,
                border: `1px solid ${tokens.color.border.default}`,
                borderRadius: tokens.radius.button,
                cursor: currentPageIndex <= 0 ? "not-allowed" : "pointer",
              }}
            >
              {layout === "rtl" ? "下一页 (←)" : "上一页 (←)"}
            </button>
            <span data-testid="reader-page-number" style={{ fontWeight: 600, padding: "0 4px" }}>
              {currentPageIndex + 1} / {totalPages}
            </span>
            <button
              type="button"
              data-testid="reader-next-page-btn"
              disabled={currentPageIndex >= totalPages - 1}
              onClick={() => onPageChange?.(currentPageIndex + 1)}
              style={{
                padding: "2px 8px",
                fontSize: tokens.typography.size.secondary,
                backgroundColor: tokens.color.surface.card,
                color: currentPageIndex >= totalPages - 1 ? tokens.color.text.muted : tokens.color.text.primary,
                border: `1px solid ${tokens.color.border.default}`,
                borderRadius: tokens.radius.button,
                cursor: currentPageIndex >= totalPages - 1 ? "not-allowed" : "pointer",
              }}
            >
              {layout === "rtl" ? "上一页 (→)" : "下一页 (→)"}
            </button>
          </div>
        ) : null}
      </div>

      {/* Right: Mode Switch (Original / Translated) & Start Position (resume / beginning) */}
      <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.md, flexShrink: 0 }}>
        {/* Start Position Selector */}
        {onStartPositionChange && (
          <div
            data-testid="reader-start-position-switch"
            style={{
              display: "flex",
              border: `1px solid ${tokens.color.border.default}`,
              borderRadius: tokens.radius.button,
              overflow: "hidden",
            }}
          >
            <button
              type="button"
              data-testid="reader-pos-resume"
              data-active={startPosition === "resume"}
              onClick={() => onStartPositionChange("resume")}
              title="从上次阅读位置继续"
              style={{
                padding: "3px 8px",
                fontSize: tokens.typography.size.secondary,
                border: "none",
                backgroundColor: startPosition === "resume" ? tokens.color.accent.selected : tokens.color.surface.card,
                color: startPosition === "resume" ? tokens.color.accent.primary : tokens.color.text.secondary,
                fontWeight: startPosition === "resume" ? 600 : 400,
                cursor: "pointer",
              }}
            >
              继续
            </button>
            <button
              type="button"
              data-testid="reader-pos-beginning"
              data-active={startPosition === "beginning"}
              onClick={() => onStartPositionChange("beginning")}
              title="从章节开头开始（不改变已保存进度）"
              style={{
                padding: "3px 8px",
                fontSize: tokens.typography.size.secondary,
                border: "none",
                backgroundColor: startPosition === "beginning" ? tokens.color.accent.selected : tokens.color.surface.card,
                color: startPosition === "beginning" ? tokens.color.accent.primary : tokens.color.text.secondary,
                fontWeight: startPosition === "beginning" ? 600 : 400,
                cursor: "pointer",
              }}
            >
              从头开始
            </button>
          </div>
        )}

        {/* Mode Switch */}
        <div
          data-testid="reader-mode-switch"
          style={{
            display: "flex",
            border: `1px solid ${tokens.color.border.default}`,
            borderRadius: tokens.radius.button,
            overflow: "hidden",
          }}
        >
          <button
            type="button"
            data-testid="reader-mode-original"
            data-active={mode === "original"}
            onClick={() => onModeChange("original")}
            title="原文模式 (O)"
            style={{
              padding: "4px 12px",
              fontSize: tokens.typography.size.secondary,
              border: "none",
              backgroundColor: mode === "original" ? tokens.color.accent.selected : tokens.color.surface.card,
              color: mode === "original" ? tokens.color.accent.primary : tokens.color.text.secondary,
              fontWeight: mode === "original" ? 600 : 400,
              cursor: "pointer",
            }}
          >
            原文 (Original)
          </button>
          <button
            type="button"
            data-testid="reader-mode-translated"
            data-active={mode === "translated"}
            onClick={() => onModeChange("translated")}
            title="译文模式 (T)"
            style={{
              padding: "4px 12px",
              fontSize: tokens.typography.size.secondary,
              border: "none",
              backgroundColor: mode === "translated" ? tokens.color.accent.selected : tokens.color.surface.card,
              color: mode === "translated" ? tokens.color.accent.primary : tokens.color.text.secondary,
              fontWeight: mode === "translated" ? 600 : 400,
              cursor: "pointer",
            }}
          >
            译文 (Translated)
          </button>
        </div>
      </div>
    </header>
  );
}
