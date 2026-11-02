import type { BookSummary, ChapterNavSummary } from "../library/types";
import { ChapterList } from "./ChapterList";
import { tokens } from "../theme/tokens";

export interface BookDetailPanelProps {
  book: BookSummary | null;
  chapters: ChapterNavSummary[];
  chapterPageCounts: Record<string, number>;
  loadingChapters?: boolean;
  onEnterWorkbench?: (bookId: string, chapterId: string) => void;
  onEnterReader?: (bookId: string, chapterId: string) => void;
  onOpenImport?: (chapterId?: string | null) => void;
  onCreateChapter?: () => void;
}

export function BookDetailPanel({
  book,
  chapters,
  chapterPageCounts,
  loadingChapters = false,
  onEnterWorkbench,
  onEnterReader,
  onOpenImport,
  onCreateChapter,
}: BookDetailPanelProps) {
  if (!book) {
    return (
      <aside
        data-testid="book-detail-panel"
        style={{
          width: tokens.dimensions.bookDetailPanelWidth,
          height: "100%",
          boxSizing: "border-box",
          backgroundColor: tokens.color.surface.card,
          borderLeft: `1px solid ${tokens.color.surface.border}`,
          padding: tokens.spacing.lg,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          color: tokens.color.text.muted,
          fontSize: tokens.typography.size.base,
        }}
      >
        <div data-testid="book-detail-empty" style={{ textAlign: "center" }}>
          <div style={{ fontSize: 32, marginBottom: tokens.spacing.sm }}>📖</div>
          <div style={{ fontSize: tokens.typography.size.cardTitle, fontWeight: 600, color: tokens.color.text.secondary }}>
            未选择作品
          </div>
          <div style={{ fontSize: tokens.typography.size.secondary, marginTop: 4 }}>
            从左侧列表中点击选择一部漫画以查看章节和详情
          </div>
        </div>
      </aside>
    );
  }

  const pageCountText = book.page_count === null ? "—" : `${book.page_count} 页`;

  return (
    <aside
      data-testid="book-detail-panel"
      style={{
        width: tokens.dimensions.bookDetailPanelWidth,
        height: "100%",
        boxSizing: "border-box",
        backgroundColor: tokens.color.surface.card,
        borderLeft: `1px solid ${tokens.color.surface.border}`,
        padding: tokens.spacing.md,
        display: "flex",
        flexDirection: "column",
        overflowY: "auto",
        gap: tokens.spacing.md,
      }}
    >
      {/* Book header */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <h2
            data-testid="detail-book-title"
            style={{
              margin: 0,
              fontSize: tokens.typography.size.panelTitle,
              fontWeight: 600,
              color: tokens.color.text.primary,
              lineHeight: 1.3,
            }}
          >
            {book.title}
          </h2>
          {book.is_favorite && (
            <span
              title="已收藏"
              style={{ color: tokens.color.state.favorite, fontSize: 16 }}
            >
              ★
            </span>
          )}
        </div>

        {book.original_title && (
          <div
            data-testid="detail-original-title"
            style={{
              fontSize: tokens.typography.size.secondary,
              color: tokens.color.text.secondary,
              marginTop: 2,
            }}
          >
            {book.original_title}
          </div>
        )}
      </div>

      {/* Basic metadata */}
      <div
        style={{
          backgroundColor: tokens.color.bg.toolbar,
          borderRadius: tokens.radius.card,
          padding: tokens.spacing.sm,
          fontSize: tokens.typography.size.secondary,
          display: "flex",
          flexDirection: "column",
          gap: 6,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span style={{ color: tokens.color.text.secondary }}>总页数</span>
          <span style={{ fontWeight: 600, color: tokens.color.text.primary }}>
            {pageCountText}
          </span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span style={{ color: tokens.color.text.secondary }}>章节数</span>
          <span style={{ fontWeight: 600, color: tokens.color.text.primary }}>
            {chapters.length} 章
          </span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span style={{ color: tokens.color.text.secondary }}>更新时间</span>
          <span style={{ color: tokens.color.text.primary }}>
            {book.updated_at ? new Date(book.updated_at).toLocaleDateString() : "—"}
          </span>
        </div>
      </div>

      {/* Reading Summary (GAP-G5: book-level aggregate reading summary gap) */}
      <div
        style={{
          border: `1px dashed ${tokens.color.border.default}`,
          borderRadius: tokens.radius.card,
          padding: tokens.spacing.sm,
          fontSize: tokens.typography.size.secondary,
        }}
      >
        <div style={{ fontWeight: 600, marginBottom: 4, color: tokens.color.text.secondary }}>
          阅读摘要
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", color: tokens.color.text.muted }}>
          <span>最近阅读</span>
          <span title="阅读摘要数据（等待能力接入 GAP-G5）">—</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", color: tokens.color.text.muted, marginTop: 4 }}>
          <span>累计时长</span>
          <span title="阅读摘要数据（等待能力接入 GAP-G5）">—</span>
        </div>
      </div>

      {/* Actions & Gaps */}
      <div style={{ display: "flex", gap: tokens.spacing.sm }}>
        <button
          type="button"
          data-testid="detail-import-btn"
          onClick={() => onOpenImport?.(null)}
          style={{
            flex: 1,
            padding: "6px 12px",
            fontSize: tokens.typography.size.base,
            fontWeight: 500,
            backgroundColor: tokens.color.accent.primary,
            color: tokens.color.text.inverse,
            border: "none",
            borderRadius: tokens.radius.button,
            cursor: "pointer",
          }}
        >
          导入页面
        </button>

        {/* GAP-G2: Delete book is disabled */}
        <button
          type="button"
          data-testid="detail-delete-btn"
          disabled
          title="删除作品（等待能力接入 GAP-G2）"
          style={{
            padding: "6px 10px",
            fontSize: tokens.typography.size.base,
            backgroundColor: tokens.color.surface.card,
            color: tokens.color.text.muted,
            border: `1px solid ${tokens.color.border.default}`,
            borderRadius: tokens.radius.button,
            cursor: "not-allowed",
            opacity: 0.5,
          }}
        >
          删除作品
        </button>
      </div>

      {/* Constraints & Tag Gaps */}
      <div style={{ display: "flex", gap: 6 }}>
        <button
          type="button"
          data-testid="detail-tags-btn"
          disabled
          title="标签管理（等待能力接入 GAP-G7）"
          style={{
            flex: 1,
            padding: "4px 8px",
            fontSize: tokens.typography.size.secondary,
            backgroundColor: tokens.color.bg.toolbar,
            color: tokens.color.text.muted,
            border: `1px solid ${tokens.color.border.default}`,
            borderRadius: tokens.radius.button,
            cursor: "not-allowed",
            opacity: 0.6,
          }}
        >
          标签管理 (GAP-G7)
        </button>
        <button
          type="button"
          data-testid="detail-glossary-btn"
          disabled
          title="翻译约束维护（等待能力接入 GAP-G8）"
          style={{
            flex: 1,
            padding: "4px 8px",
            fontSize: tokens.typography.size.secondary,
            backgroundColor: tokens.color.bg.toolbar,
            color: tokens.color.text.muted,
            border: `1px solid ${tokens.color.border.default}`,
            borderRadius: tokens.radius.button,
            cursor: "not-allowed",
            opacity: 0.6,
          }}
        >
          翻译约束 (GAP-G8)
        </button>
      </div>

      {/* Chapter Section */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 180 }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: tokens.spacing.xs,
          }}
        >
          <span style={{ fontWeight: 600, fontSize: tokens.typography.size.base }}>
            章节列表
          </span>

          <button
            type="button"
            data-testid="new-chapter-btn"
            onClick={onCreateChapter}
            disabled={!onCreateChapter}
            title={!onCreateChapter ? "请选择作品后新建章节" : undefined}
            style={{
              padding: "2px 8px",
              fontSize: tokens.typography.size.secondary,
              backgroundColor: tokens.color.surface.card,
              color: tokens.color.text.muted,
              border: `1px solid ${tokens.color.border.default}`,
              borderRadius: tokens.radius.button,
              cursor: onCreateChapter ? "pointer" : "not-allowed",
              opacity: onCreateChapter ? 1 : 0.6,
            }}
          >
            + 新建章节
          </button>
        </div>

        <ChapterList
          bookId={book.book_id}
          chapters={chapters}
          chapterPageCounts={chapterPageCounts}
          loading={loadingChapters}
          onEnterWorkbench={onEnterWorkbench}
          onEnterReader={onEnterReader}
          onOpenImport={onOpenImport}
        />
      </div>
    </aside>
  );
}
