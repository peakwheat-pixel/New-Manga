/**
 * AD-001 四页 UI/UX 设计基线（§8 设计令牌，新架构自有取值）
 */

export const tokens = {
  color: {
    bg: {
      app: "#f5f5f4",
      rail: "#ececea",
      toolbar: "#f7f7f5",
    },
    surface: {
      card: "#ffffff",
      border: "#d9d9d6",
    },
    accent: {
      primary: "#4f6bed",
      selected: "#e8edff",
      hover: "#3d56ca",
    },
    text: {
      primary: "#1f2328",
      secondary: "#6b7280",
      muted: "#8c959f",
      inverse: "#ffffff",
    },
    state: {
      favorite: "#e2a400",
      archived: "#f0b429",
      running: "#4f6bed",
      completed: "#2da44e",
      failed: "#cf222e",
      skipped: "#8c959f",
      blocked: "#9a6700",
    },
    focus: {
      ring: "#4f6bed",
    },
    border: {
      default: "#d9d9d6",
      divider: "#e8e8e4",
      selected: "#4f6bed",
    },
  },
  typography: {
    fontFamily: `system-ui, "Segoe UI", "Microsoft YaHei UI", sans-serif`,
    monospace: `ui-monospace, Consolas, monospace`,
    size: {
      badge: 10,
      secondary: 11,
      monospace: 12,
      base: 13,
      cardTitle: 14,
      panelTitle: 18,
    },
    lineHeight: 1.5,
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
  },
  radius: {
    button: 4,
    card: 6,
    pill: 9999,
  },
  dimensions: {
    minAppWidth: 1024,
    minAppHeight: 680,
    railWidth: 64,
    bookshelfToolbarHeight: 48,
    bookDetailPanelWidth: 320,
    cardGridWidth: 168,
    cardGridHeight: 210,
    chapterRowHeight: 32,
  },
} as const;
