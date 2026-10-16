import { useEffect, useRef } from "react";
import type { BookshelfFilterState, BookshelfSortField } from "./types";
import { tokens } from "../theme/tokens";

export interface BookshelfToolbarProps {
  filter: BookshelfFilterState;
  onFilterChange: (update: Partial<BookshelfFilterState>) => void;
  onOpenImport: () => void;
}

export function BookshelfToolbar({ filter, onFilterChange, onOpenImport }: BookshelfToolbarProps) {
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Keyboard shortcut Ctrl+F to focus search input, Esc to clear
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "f") {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <header
      data-testid="bookshelf-toolbar"
      style={{
        height: tokens.dimensions.bookshelfToolbarHeight,
        boxSizing: "border-box",
        backgroundColor: tokens.color.bg.toolbar,
        borderBottom: `1px solid ${tokens.color.border.default}`,
        padding: `0 ${tokens.spacing.md}px`,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: tokens.spacing.md,
      }}
    >
      {/* Left operations: New book & Import book */}
      <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.sm }}>
        {/* GAP-G1: New Book is disabled */}
        <button
          type="button"
          data-testid="toolbar-new-book-btn"
          disabled
          title="新建作品（等待能力接入 GAP-G1）"
          style={{
            height: 30,
            padding: "0 10px",
            fontSize: tokens.typography.size.base,
            backgroundColor: tokens.color.surface.card,
            color: tokens.color.text.muted,
            border: `1px solid ${tokens.color.border.default}`,
            borderRadius: tokens.radius.button,
            cursor: "not-allowed",
            opacity: 0.6,
          }}
        >
          + 新建作品
        </button>

        <button
          type="button"
          data-testid="toolbar-import-btn"
          onClick={onOpenImport}
          style={{
            height: 30,
            padding: "0 12px",
            fontSize: tokens.typography.size.base,
            fontWeight: 500,
            backgroundColor: tokens.color.accent.primary,
            color: tokens.color.text.inverse,
            border: "none",
            borderRadius: tokens.radius.button,
            cursor: "pointer",
          }}
        >
          导入作品
        </button>
      </div>

      {/* Center: Search input */}
      <div style={{ flex: 1, maxWidth: 360, position: "relative" }}>
        <input
          ref={searchInputRef}
          type="text"
          data-testid="bookshelf-search-input"
          placeholder="搜索作品标题 / 原名 (Ctrl+F)"
          value={filter.search}
          onChange={(e) => onFilterChange({ search: e.target.value })}
          onInput={(e) => onFilterChange({ search: (e.target as HTMLInputElement).value })}
          onKeyDown={(e) => {
            if (e.key === "Escape") {
              onFilterChange({ search: "" });
            }
          }}
          style={{
            width: "100%",
            height: 30,
            boxSizing: "border-box",
            padding: "0 8px",
            fontSize: tokens.typography.size.base,
            borderRadius: tokens.radius.button,
            border: `1px solid ${tokens.color.border.default}`,
            backgroundColor: tokens.color.surface.card,
            color: tokens.color.text.primary,
            outline: "none",
          }}
        />
        {filter.search && (
          <button
            type="button"
            data-testid="bookshelf-clear-search-btn"
            title="清空搜索 (Esc)"
            onClick={() => onFilterChange({ search: "" })}
            style={{
              position: "absolute",
              right: 6,
              top: 5,
              background: "none",
              border: "none",
              color: tokens.color.text.muted,
              cursor: "pointer",
              fontSize: 12,
            }}
          >
            ✕
          </button>
        )}
      </div>

      {/* Right controls: Filter, Sort, View mode toggle */}
      <div style={{ display: "flex", alignItems: "center", gap: tokens.spacing.sm }}>
        {/* Favorite filter */}
        <button
          type="button"
          data-testid="toolbar-filter-favorite-btn"
          data-active={filter.favoriteOnly}
          onClick={() => onFilterChange({ favoriteOnly: !filter.favoriteOnly })}
          style={{
            height: 30,
            padding: "0 8px",
            fontSize: tokens.typography.size.secondary,
            backgroundColor: filter.favoriteOnly ? tokens.color.accent.selected : tokens.color.surface.card,
            color: filter.favoriteOnly ? tokens.color.state.favorite : tokens.color.text.secondary,
            border: `1px solid ${filter.favoriteOnly ? tokens.color.accent.primary : tokens.color.border.default}`,
            borderRadius: tokens.radius.button,
            cursor: "pointer",
            fontWeight: filter.favoriteOnly ? 600 : 400,
          }}
        >
          ★ 收藏
        </button>

        {/* Archived filter */}
        <button
          type="button"
          data-testid="toolbar-filter-archived-btn"
          data-active={filter.archivedOnly}
          onClick={() => onFilterChange({ archivedOnly: !filter.archivedOnly })}
          style={{
            height: 30,
            padding: "0 8px",
            fontSize: tokens.typography.size.secondary,
            backgroundColor: filter.archivedOnly ? tokens.color.accent.selected : tokens.color.surface.card,
            color: filter.archivedOnly ? tokens.color.state.archived : tokens.color.text.secondary,
            border: `1px solid ${filter.archivedOnly ? tokens.color.accent.primary : tokens.color.border.default}`,
            borderRadius: tokens.radius.button,
            cursor: "pointer",
            fontWeight: filter.archivedOnly ? 600 : 400,
          }}
        >
          归档
        </button>

        {/* Sort select */}
        <select
          data-testid="toolbar-sort-select"
          value={filter.sortBy}
          onChange={(e) => onFilterChange({ sortBy: e.target.value as BookshelfSortField })}
          style={{
            height: 30,
            padding: "0 6px",
            fontSize: tokens.typography.size.secondary,
            backgroundColor: tokens.color.surface.card,
            color: tokens.color.text.primary,
            border: `1px solid ${tokens.color.border.default}`,
            borderRadius: tokens.radius.button,
            cursor: "pointer",
            outline: "none",
          }}
        >
          <option value="title">按标题排序</option>
          <option value="updated_at">按更新时间</option>
        </select>

        {/* View mode toggle */}
        <div
          data-testid="toolbar-view-toggle"
          style={{
            display: "flex",
            border: `1px solid ${tokens.color.border.default}`,
            borderRadius: tokens.radius.button,
            overflow: "hidden",
          }}
        >
          <button
            type="button"
            data-testid="toolbar-view-grid-btn"
            data-active={filter.viewMode === "grid"}
            onClick={() => onFilterChange({ viewMode: "grid" })}
            title="网格视图"
            style={{
              height: 28,
              padding: "0 8px",
              fontSize: 12,
              border: "none",
              backgroundColor: filter.viewMode === "grid" ? tokens.color.accent.selected : tokens.color.surface.card,
              color: filter.viewMode === "grid" ? tokens.color.accent.primary : tokens.color.text.secondary,
              cursor: "pointer",
              fontWeight: filter.viewMode === "grid" ? 600 : 400,
            }}
          >
            ⊞
          </button>
          <button
            type="button"
            data-testid="toolbar-view-list-btn"
            data-active={filter.viewMode === "list"}
            onClick={() => onFilterChange({ viewMode: "list" })}
            title="列表视图"
            style={{
              height: 28,
              padding: "0 8px",
              fontSize: 12,
              border: "none",
              backgroundColor: filter.viewMode === "list" ? tokens.color.accent.selected : tokens.color.surface.card,
              color: filter.viewMode === "list" ? tokens.color.accent.primary : tokens.color.text.secondary,
              cursor: "pointer",
              fontWeight: filter.viewMode === "list" ? 600 : 400,
            }}
          >
            ☰
          </button>
        </div>
      </div>
    </header>
  );
}
