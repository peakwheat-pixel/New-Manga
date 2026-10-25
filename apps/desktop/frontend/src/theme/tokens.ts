/**
 * 设计令牌的 TS 侧镜像（v2 / Fluent 材质路线）。
 *
 * 唯一真相源是 `src/design/tokens.css`；本文件是它的运行时镜像，供仍在用
 * 内联样式表达颜色的既有组件读取（React 内联样式无法直接写 `var(--nm-*)` 到
 * 需要具体色值的比较/计算场景，且 `style` 对象里塞 CSS 变量会让 jsdom 断言
 * 与既有快照完全失效）。
 *
 * 三条硬约束，由 `tokens.test.ts` 机械校验：
 *   1. dark/light 两套值必须与 `tokens.css` 里同名变量逐字节相等；
 *   2. 字号只能取 28 / 20 / 14 / 12 四档；
 *   3. 圆角只能取 8 / 4 / 2 / 0，间距只能取 4 / 8 / 12 / 16 / 24。
 *
 * 主题可切换：`tokens` 是 Proxy，每次属性访问都取当前激活主题的快照。切换时
 * 调 `setTokenTheme()`，再让 React 树重渲染一次，所有读 `tokens.*` 的内联样式
 * 就会跟着换色——不需要把每个组件改成 CSS 变量，也不需要 getComputedStyle
 * （jsdom 里后者拿不到样式表里的自定义属性）。
 */

export type TokenTheme = "dark" | "light";

/** 与 `--nm-font-ui` 逐项相同的字体族栈（CSS 写法带引号，这里不带）。 */
const FONT_UI = `"Segoe UI Variable Text", "Microsoft YaHei UI", system-ui, sans-serif`;
const FONT_DATA = `"Cascadia Mono", "Consolas", ui-monospace, monospace`;

const SHARED = {
  typography: {
    fontFamily: FONT_UI,
    monospace: FONT_DATA,
    /**
     * v2 字阶只有 28 / 20 / 14 / 12 四档（封面与漫画页等装饰字豁免）。
     * 历史组件用的 10 / 11 / 13 / 18 全部就近收敛：10、11 → 12；13 → 14；
     * 18 → 20。取值来源是 `--nm-text-*-size`，不在这里另造一套。
     */
    size: {
      badge: 12,
      secondary: 12,
      monospace: 12,
      base: 14,
      cardTitle: 14,
      panelTitle: 20,
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
    card: 8,
    pill: 2,
  },
  dimensions: {
    minAppWidth: 1024,
    minAppHeight: 680,
    railWidth: 64,
    bookshelfToolbarHeight: 48,
    bookDetailPanelWidth: 340,
    cardGridWidth: 168,
    cardGridHeight: 210,
    chapterRowHeight: 32,
  },
} as const;

const DARK_THEME = {
  color: {
    bg: {
      app: "#1B1B1B",
      rail: "#202020",
      toolbar: "#272727",
    },
    surface: {
      card: "#2B2B2B",
      border: "rgba(255,255,255,0.09)",
    },
    accent: {
      primary: "#60CDFF",
      selected: "rgba(96,205,255,0.16)",
      hover: "#9EF1FF",
    },
    text: {
      primary: "#FFFFFF",
      secondary: "rgba(255,255,255,0.79)",
      muted: "rgba(255,255,255,0.54)",
      inverse: "#000000",
    },
    state: {
      favorite: "#C8903F",
      archived: "#4A4F55",
      running: "#5B93B8",
      completed: "#6FA97D",
      failed: "#C9634F",
      skipped: "#4A4F55",
      blocked: "#C8903F",
    },
    focus: {
      ring: "rgba(96,205,255,0.45)",
    },
    border: {
      default: "rgba(255,255,255,0.09)",
      divider: "rgba(255,255,255,0.07)",
      selected: "#60CDFF",
    },
  },
} as const;

const LIGHT_THEME = {
  color: {
    bg: {
      app: "#EEEEEE",
      rail: "#F3F3F3",
      toolbar: "#FAFAFA",
    },
    surface: {
      card: "#FFFFFF",
      border: "rgba(0,0,0,0.09)",
    },
    accent: {
      primary: "#005FB8",
      selected: "rgba(0,95,184,0.10)",
      hover: "#0078D4",
    },
    text: {
      primary: "#1A1A1A",
      secondary: "rgba(0,0,0,0.79)",
      muted: "rgba(0,0,0,0.54)",
      inverse: "#FFFFFF",
    },
    state: {
      favorite: "#8A6A1F",
      archived: "#8A8F94",
      running: "#3D6E8E",
      completed: "#3F6B4F",
      failed: "#A8462F",
      skipped: "#8A8F94",
      blocked: "#8A6A1F",
    },
    focus: {
      ring: "rgba(0,95,184,0.40)",
    },
    border: {
      default: "rgba(0,0,0,0.09)",
      divider: "rgba(0,0,0,0.06)",
      selected: "#005FB8",
    },
  },
} as const;

export const TOKEN_THEMES = {
  dark: { ...SHARED, ...DARK_THEME },
  light: { ...SHARED, ...LIGHT_THEME },
} as const;

export type TokenSet = (typeof TOKEN_THEMES)["dark"];

let activeTheme: TokenTheme = "dark";

/** 切换 `tokens.*` 的取值来源；调用方负责随后触发一次重渲染。 */
export function setTokenTheme(theme: TokenTheme): void {
  activeTheme = theme;
}

/** 仅供测试/诊断：当前激活的令牌主题。 */
export function getTokenTheme(): TokenTheme {
  return activeTheme;
}

/**
 * 当前主题下的令牌快照。顶层属性每次读取都从激活主题取，嵌套对象是普通
 * 不可变对象，所以 `tokens.color.bg.app` 这种链式访问拿到的一定是同一主题的
 * 自洽值。
 */
export const tokens: TokenSet = new Proxy({} as TokenSet, {
  get(_target, property) {
    return TOKEN_THEMES[activeTheme][property as keyof TokenSet];
  },
  has(_target, property) {
    return property in TOKEN_THEMES[activeTheme];
  },
  ownKeys() {
    return Reflect.ownKeys(TOKEN_THEMES[activeTheme]);
  },
  getOwnPropertyDescriptor(_target, property) {
    return {
      enumerable: true,
      configurable: true,
      value: TOKEN_THEMES[activeTheme][property as keyof TokenSet],
    };
  },
});
