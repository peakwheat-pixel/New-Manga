import type { ChapterNavSummary } from "../library/types";
import { tokens } from "../theme/tokens";

export interface ChapterListProps {
  bookId: string;
  chapters: ChapterNavSummary[];
  chapterPageCounts: Record<string, number>;
  loading?: boolean;
  onEnterWorkbench?: (bookId: string, chapterId: string) => void;
  onEnterReader?: (bookId: string, chapterId: string) => void;
  onOpenImport?: (chapterId: string) => void;
}

export function ChapterList({
  bookId,
  chapters,
  chapterPageCounts,
  loading = false,
  onEnterWorkbench,
  onEnterReader,
  onOpenImport,
}: ChapterListProps) {
  if (loading) {
    return (
      <div
        data-testid="chapter-list-loading"
        style={{
          padding: tokens.spacing.md,
          fontSize: tokens.typography.size.secondary,
          color: tokens.color.text.secondary,
          textAlign: "center",
        }}
      >
        加载章节列表中...
      </div>
    );
  }

  if (chapters.length === 0) {
    return (
      <div
        data-testid="chapter-list-empty"
        style={{
          padding: tokens.spacing.md,
          fontSize: tokens.typography.size.secondary,
          color: tokens.color.text.muted,
          textAlign: "center",
        }}
      >
        暂无章节，请点击下方「导入页面」或「新建章节」
      </div>
    );
  }

  return (
    <div
      data-testid="chapter-list"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 4,
        overflowY: "auto",
        maxHeight: 320,
      }}
    >
      {chapters.map((ch) => {
        const pageCount = chapterPageCounts[ch.chapter_id];
        const pageCountText = typeof pageCount === "number" ? `${pageCount} 页` : "—";

        return (
          <div
            key={ch.chapter_id}
            data-testid={`chapter-item-${ch.chapter_id}`}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              height: tokens.dimensions.chapterRowHeight,
              padding: `0 ${tokens.spacing.sm}px`,
              borderRadius: tokens.radius.button,
              backgroundColor: tokens.color.bg.toolbar,
              border: `1px solid ${tokens.color.border.divider}`,
              fontSize: tokens.typography.size.base,
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: tokens.spacing.sm,
                overflow: "hidden",
                marginRight: tokens.spacing.sm,
              }}
            >
              <span
                style={{
                  fontSize: tokens.typography.size.secondary,
                  color: tokens.color.text.secondary,
                  fontVariantNumeric: "tabular-nums",
                  minWidth: 28,
                }}
              >
                {ch.chapter_number ? `#${ch.chapter_number}` : `#${ch.sort_order}`}
              </span>
              <span
                title={ch.title}
                style={{
                  fontWeight: 500,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {ch.title || "未命名章节"}
              </span>
              <span
                data-testid={`chapter-page-count-${ch.chapter_id}`}
                style={{
                  fontSize: tokens.typography.size.secondary,
                  color: tokens.color.text.secondary,
                  fontVariantNumeric: "tabular-nums",
                  whiteSpace: "nowrap",
                }}
              >
                ({pageCountText})
              </span>
            </div>

            {/* Row actions */}
            <div style={{ display: "flex", gap: 4, flexShrink: 0 }}>
              <button
                type="button"
                data-testid={`chapter-import-btn-${ch.chapter_id}`}
                title="导入页面到此章节"
                onClick={() => onOpenImport?.(ch.chapter_id)}
                style={{
                  fontSize: tokens.typography.size.secondary,
                  padding: "2px 6px",
                  borderRadius: tokens.radius.button,
                  border: `1px solid ${tokens.color.border.default}`,
                  backgroundColor: tokens.color.surface.card,
                  color: tokens.color.text.primary,
                  cursor: "pointer",
                }}
              >
                导入
              </button>
              <button
                type="button"
                data-testid={`chapter-enter-workbench-btn-${ch.chapter_id}`}
                title="进入工作台翻译"
                onClick={() => onEnterWorkbench?.(bookId, ch.chapter_id)}
                style={{
                  fontSize: tokens.typography.size.secondary,
                  padding: "2px 6px",
                  borderRadius: tokens.radius.button,
                  border: `1px solid ${tokens.color.accent.primary}`,
                  backgroundColor: tokens.color.accent.selected,
                  color: tokens.color.accent.primary,
                  cursor: "pointer",
                  fontWeight: 500,
                }}
              >
                翻译
              </button>
              <button
                type="button"
                data-testid={`chapter-enter-reader-btn-${ch.chapter_id}`}
                title="进入阅读器查看"
                onClick={() => onEnterReader?.(bookId, ch.chapter_id)}
                style={{
                  fontSize: tokens.typography.size.secondary,
                  padding: "2px 6px",
                  borderRadius: tokens.radius.button,
                  border: `1px solid ${tokens.color.border.default}`,
                  backgroundColor: tokens.color.surface.card,
                  color: tokens.color.text.primary,
                  cursor: "pointer",
                }}
              >
                阅读
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
