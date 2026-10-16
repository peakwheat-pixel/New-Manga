import { useState } from "react";
import { tokens } from "../theme/tokens";

export interface ReaderPageProps {
  bookId?: string | null;
  chapterId?: string | null;
  chapterTitle?: string | null;
  onReturnToBookshelf?: () => void;
}

export function ReaderPage({
  bookId,
  chapterId,
  chapterTitle,
  onReturnToBookshelf,
}: ReaderPageProps) {
  const [displayMode, setDisplayMode] = useState<"original" | "translated">("original");

  return (
    <div
      data-testid="reader-page"
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        height: "100%",
        boxSizing: "border-box",
        backgroundColor: tokens.color.bg.app,
        overflow: "hidden",
      }}
    >
      {/* Reader Toolbar (height 48px per §4.2) */}
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
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.md }}>
          <button
            type="button"
            data-testid="reader-return-btn"
            onClick={onReturnToBookshelf}
            style={{
              padding: "4px 10px",
              fontSize: tokens.typography.size.base,
              backgroundColor: tokens.color.surface.card,
              color: tokens.color.text.primary,
              border: `1px solid ${tokens.color.border.default}`,
              borderRadius: tokens.radius.button,
              cursor: "pointer",
            }}
          >
            ← 返回书架
          </button>
          <span
            data-testid="reader-chapter-title"
            style={{ fontWeight: 600, fontSize: tokens.typography.size.cardTitle, color: tokens.color.text.primary }}
          >
            {chapterTitle || (chapterId ? `章节: ${chapterId}` : "尚未选择章节")}
          </span>
        </div>

        {/* Mode Switch: Original / Translated */}
        <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.sm }}>
          <div
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
              data-active={displayMode === "original"}
              onClick={() => setDisplayMode("original")}
              style={{
                padding: "4px 12px",
                fontSize: tokens.typography.size.secondary,
                border: "none",
                backgroundColor: displayMode === "original" ? tokens.color.accent.selected : tokens.color.surface.card,
                color: displayMode === "original" ? tokens.color.accent.primary : tokens.color.text.secondary,
                fontWeight: displayMode === "original" ? 600 : 400,
                cursor: "pointer",
              }}
            >
              原文 (Original)
            </button>
            <button
              type="button"
              data-testid="reader-mode-translated"
              data-active={displayMode === "translated"}
              onClick={() => setDisplayMode("translated")}
              style={{
                padding: "4px 12px",
                fontSize: tokens.typography.size.secondary,
                border: "none",
                backgroundColor: displayMode === "translated" ? tokens.color.accent.selected : tokens.color.surface.card,
                color: displayMode === "translated" ? tokens.color.accent.primary : tokens.color.text.secondary,
                fontWeight: displayMode === "translated" ? 600 : 400,
                cursor: "pointer",
              }}
            >
              译文 (Translated)
            </button>
          </div>
        </div>
      </header>

      {/* Reader Viewport */}
      <main
        data-testid="reader-viewport"
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#161b22",
          color: "#e6edf3",
          overflow: "auto",
          padding: tokens.spacing.lg,
        }}
      >
        {!chapterId ? (
          <div
            data-testid="reader-empty"
            style={{
              textAlign: "center",
              color: tokens.color.text.muted,
              fontSize: tokens.typography.size.base,
            }}
          >
            <div style={{ fontSize: 40, marginBottom: tokens.spacing.sm }}>📖</div>
            <div style={{ fontSize: tokens.typography.size.panelTitle, fontWeight: 600, color: "#c9d1d9" }}>
              尚未选择阅读章节
            </div>
            <div style={{ fontSize: tokens.typography.size.secondary, marginTop: 4 }}>
              请先在书架中选择一个作品及章节，然后点击「进入阅读」
            </div>
            {onReturnToBookshelf && (
              <button
                type="button"
                data-testid="reader-go-bookshelf-btn"
                onClick={onReturnToBookshelf}
                style={{
                  marginTop: tokens.spacing.md,
                  padding: "6px 16px",
                  fontSize: tokens.typography.size.base,
                  backgroundColor: tokens.color.accent.primary,
                  color: tokens.color.text.inverse,
                  border: "none",
                  borderRadius: tokens.radius.button,
                  cursor: "pointer",
                }}
              >
                前往书架
              </button>
            )}
          </div>
        ) : (
          <div
            data-testid="reader-content-frame"
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: tokens.spacing.md,
            }}
          >
            <div style={{ color: "#8b949e", fontSize: tokens.typography.size.secondary }}>
              {bookId ? `作品 ID: ${bookId} | ` : ""}当前模式: {displayMode === "original" ? "原文" : "译文"} | 章节 ID: {chapterId}
            </div>
            {displayMode === "translated" && (
              <div
                style={{
                  backgroundColor: "rgba(226, 164, 0, 0.2)",
                  border: "1px solid #e2a400",
                  borderRadius: tokens.radius.button,
                  padding: "4px 10px",
                  fontSize: tokens.typography.size.secondary,
                  color: "#f0b429",
                }}
              >
                未翻译页面将回退展示原文
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
