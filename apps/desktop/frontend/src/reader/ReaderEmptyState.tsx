import { tokens } from "../theme/tokens";

export interface ReaderEmptyStateProps {
  title?: string;
  description?: string;
  onReturnToBookshelf?: () => void;
}

export function ReaderEmptyState({
  title = "尚未选择阅读章节",
  description = "请先在书架中选择一个作品及章节，然后点击「进入阅读」",
  onReturnToBookshelf,
}: ReaderEmptyStateProps) {
  return (
    <div
      data-testid="reader-empty"
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100%",
        width: "100%",
        textAlign: "center",
        color: tokens.color.text.muted,
        padding: tokens.spacing.xl,
        boxSizing: "border-box",
      }}
    >
      <div style={{ fontSize: 48, marginBottom: tokens.spacing.md }}>📖</div>
      <div
        data-testid="reader-empty-title"
        style={{
          fontSize: tokens.typography.size.panelTitle,
          fontWeight: 600,
          color: tokens.color.text.primary,
          marginBottom: tokens.spacing.xs,
        }}
      >
        {title}
      </div>
      <div
        data-testid="reader-empty-description"
        style={{
          fontSize: tokens.typography.size.secondary,
          color: tokens.color.text.secondary,
          maxWidth: 420,
          lineHeight: 1.5,
          marginBottom: tokens.spacing.lg,
        }}
      >
        {description}
      </div>
      {onReturnToBookshelf && (
        <button
          type="button"
          data-testid="reader-go-bookshelf-btn"
          onClick={onReturnToBookshelf}
          style={{
            padding: "8px 20px",
            fontSize: tokens.typography.size.base,
            backgroundColor: tokens.color.accent.primary,
            color: tokens.color.text.inverse,
            border: "none",
            borderRadius: tokens.radius.button,
            cursor: "pointer",
            fontWeight: 500,
          }}
        >
          前往书架
        </button>
      )}
    </div>
  );
}
