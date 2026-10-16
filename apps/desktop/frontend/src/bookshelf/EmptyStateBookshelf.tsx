import { tokens } from "../theme/tokens";

export interface EmptyStateBookshelfProps {
  isFiltered?: boolean;
  onOpenImport?: () => void;
  onClearFilter?: () => void;
}

export function EmptyStateBookshelf({
  isFiltered = false,
  onOpenImport,
  onClearFilter,
}: EmptyStateBookshelfProps) {
  if (isFiltered) {
    return (
      <div
        data-testid="bookshelf-filtered-empty"
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: tokens.spacing.xl,
          height: "60%",
          color: tokens.color.text.secondary,
        }}
      >
        <div style={{ fontSize: 36, marginBottom: tokens.spacing.sm }}>🔍</div>
        <h3
          style={{
            margin: 0,
            fontSize: tokens.typography.size.panelTitle,
            fontWeight: 600,
            color: tokens.color.text.primary,
          }}
        >
          未找到匹配作品
        </h3>
        <p style={{ marginTop: tokens.spacing.xs, fontSize: tokens.typography.size.base }}>
          没有作品符合当前的搜索或过滤条件。
        </p>
        <button
          type="button"
          data-testid="bookshelf-clear-filter-btn"
          onClick={onClearFilter}
          style={{
            marginTop: tokens.spacing.md,
            padding: "6px 14px",
            fontSize: tokens.typography.size.base,
            backgroundColor: tokens.color.surface.card,
            color: tokens.color.accent.primary,
            border: `1px solid ${tokens.color.accent.primary}`,
            borderRadius: tokens.radius.button,
            cursor: "pointer",
          }}
        >
          清除所有过滤条件
        </button>
      </div>
    );
  }

  return (
    <div
      data-testid="bookshelf-empty-state"
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: tokens.spacing.xl,
        height: "60%",
        color: tokens.color.text.secondary,
      }}
    >
      <div style={{ fontSize: 48, marginBottom: tokens.spacing.sm }}>📚</div>
      <h3
        style={{
          margin: 0,
          fontSize: tokens.typography.size.panelTitle,
          fontWeight: 600,
          color: tokens.color.text.primary,
        }}
      >
        还没有作品
      </h3>
      <p style={{ marginTop: tokens.spacing.xs, fontSize: tokens.typography.size.base, maxWidth: 360, textAlign: "center" }}>
        书架当前为空。你可以通过导入已有的本地漫画文件或文件夹开始使用。
      </p>

      <div style={{ display: "flex", gap: tokens.spacing.md, marginTop: tokens.spacing.lg }}>
        <button
          type="button"
          data-testid="empty-import-btn"
          onClick={onOpenImport}
          style={{
            padding: "8px 18px",
            fontSize: tokens.typography.size.base,
            fontWeight: 600,
            backgroundColor: tokens.color.accent.primary,
            color: tokens.color.text.inverse,
            border: "none",
            borderRadius: tokens.radius.button,
            cursor: "pointer",
          }}
        >
          导入作品
        </button>

        {/* GAP-G1: Create Book is disabled */}
        <button
          type="button"
          data-testid="empty-new-book-btn"
          disabled
          title="新建作品（等待能力接入 GAP-G1）"
          style={{
            padding: "8px 18px",
            fontSize: tokens.typography.size.base,
            backgroundColor: tokens.color.surface.card,
            color: tokens.color.text.muted,
            border: `1px solid ${tokens.color.border.default}`,
            borderRadius: tokens.radius.button,
            cursor: "not-allowed",
            opacity: 0.6,
          }}
        >
          新建作品
        </button>
      </div>
    </div>
  );
}
