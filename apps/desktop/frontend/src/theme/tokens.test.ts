import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { TOKEN_THEMES, getTokenTheme, setTokenTheme, tokens } from "./tokens";

const css = readFileSync(resolve(process.cwd(), "src/design/tokens.css"), "utf8");

/** 抓取 `:root { ... }` 或 `:root[data-theme="x"] { ... }` 块内的变量声明。 */
function readVarsBlock(pattern: RegExp): Record<string, string> {
  const block = pattern.exec(css);
  if (!block) throw new Error(`tokens.css 缺少匹配 ${pattern} 的块`);
  const vars: Record<string, string> = {};
  for (const line of block[1].split(/\r?\n/)) {
    const match = /^\s*(--nm-[a-z0-9-]+)\s*:\s*([^;]+);/.exec(line);
    if (match) vars[match[1]] = match[2].trim();
  }
  return vars;
}

// 形状令牌（字号 / 圆角 / 间距 / 字族 / elevation / 栏高）在共享的 `:root` 块里，
// 因为它们不随主题变化；只有颜色放进 data-theme 块。
const BASE = readVarsBlock(/^:root\s*\{([\s\S]*?)\n\}/m);
const DARK = { ...BASE, ...readVarsBlock(/^:root\[data-theme="dark"\]\s*\{([\s\S]*?)\n\}/m) };
const LIGHT = { ...BASE, ...readVarsBlock(/^:root\[data-theme="light"\]\s*\{([\s\S]*?)\n\}/m) };

/**
 * TS 镜像 ↔ CSS 单一真相源的映射表。
 *
 * 每一条都是「内联样式组件读的 TS 字段」到「design/tokens.css 里真正定义它的
 * 变量」的连线。映射写死在这里而不是靠命名猜，是因为历史上出现过
 * `state.favorite` 这类在 v2 里没有同名变量的历史字段——猜命名会让守卫变成
 * 一条永远通过的假断言。
 */
const COLOR_MAP: ReadonlyArray<readonly [string, string, readonly string[], (set: any) => unknown]> = [
  ["bg.app", "--nm-bg-canvas", ["color", "bg", "app"], (s) => s.color.bg.app],
  ["bg.rail", "--nm-bg-mica", ["color", "bg", "rail"], (s) => s.color.bg.rail],
  ["bg.toolbar", "--nm-bg-layer", ["color", "bg", "toolbar"], (s) => s.color.bg.toolbar],
  ["surface.card", "--nm-bg-card", ["color", "surface", "card"], (s) => s.color.surface.card],
  ["surface.border", "--nm-line-control", ["color", "surface", "border"], (s) => s.color.surface.border],
  ["accent.primary", "--nm-accent-base", ["color", "accent", "primary"], (s) => s.color.accent.primary],
  ["accent.selected", "--nm-accent-muted", ["color", "accent", "selected"], (s) => s.color.accent.selected],
  ["accent.hover", "--nm-accent-hover", ["color", "accent", "hover"], (s) => s.color.accent.hover],
  ["text.primary", "--nm-text-primary", ["color", "text", "primary"], (s) => s.color.text.primary],
  ["text.secondary", "--nm-text-secondary", ["color", "text", "secondary"], (s) => s.color.text.secondary],
  ["text.muted", "--nm-text-tertiary", ["color", "text", "muted"], (s) => s.color.text.muted],
  ["text.inverse", "--nm-accent-on", ["color", "text", "inverse"], (s) => s.color.text.inverse],
  ["state.favorite", "--nm-status-blocked", ["color", "state", "favorite"], (s) => s.color.state.favorite],
  ["state.archived", "--nm-status-skipped", ["color", "state", "archived"], (s) => s.color.state.archived],
  ["state.running", "--nm-status-running", ["color", "state", "running"], (s) => s.color.state.running],
  ["state.completed", "--nm-status-done", ["color", "state", "completed"], (s) => s.color.state.completed],
  ["state.failed", "--nm-status-failed", ["color", "state", "failed"], (s) => s.color.state.failed],
  ["state.skipped", "--nm-status-skipped", ["color", "state", "skipped"], (s) => s.color.state.skipped],
  ["state.blocked", "--nm-status-blocked", ["color", "state", "blocked"], (s) => s.color.state.blocked],
  ["focus.ring", "--nm-accent-ring", ["color", "focus", "ring"], (s) => s.color.focus.ring],
  ["border.default", "--nm-line-control", ["color", "border", "default"], (s) => s.color.border.default],
  ["border.divider", "--nm-line-divider", ["color", "border", "divider"], (s) => s.color.border.divider],
  ["border.selected", "--nm-accent-base", ["color", "border", "selected"], (s) => s.color.border.selected],
];

const SPACING_MAP: ReadonlyArray<readonly [string, string, number]> = [
  ["xs", "--nm-space-1", 4],
  ["sm", "--nm-space-2", 8],
  ["md", "--nm-space-3", 12],
  ["lg", "--nm-space-4", 16],
  ["xl", "--nm-space-5", 24],
];

const RADIUS_MAP: ReadonlyArray<readonly [string, string, number]> = [
  ["button", "--nm-radius-control", 4],
  ["card", "--nm-radius-overlay", 8],
  ["pill", "--nm-radius-cell", 2],
];

afterEach(() => {
  setTokenTheme("dark");
});

describe("theme tokens mirror design/tokens.css", () => {
  it("declares both themes in tokens.css", () => {
    expect(Object.keys(DARK).length).toBeGreaterThanOrEqual(37);
    expect(Object.keys(LIGHT).length).toBeGreaterThanOrEqual(37);
    expect(Object.keys(DARK).sort()).toEqual(Object.keys(LIGHT).sort());
  });

  it.each(COLOR_MAP)("%s equals %s in both themes", (_path, cssVar, tsPath, read) => {
    expect(DARK[cssVar], `dark ${cssVar} 未定义`).toBeDefined();
    expect(read(TOKEN_THEMES.dark), `dark ${tsPath.join(".")}`).toBe(DARK[cssVar]);
    expect(read(TOKEN_THEMES.light), `light ${tsPath.join(".")}`).toBe(LIGHT[cssVar]);
  });

  it("spacing tokens equal the v2 space scale", () => {
    for (const [name, cssVar, expected] of SPACING_MAP) {
      expect(DARK[cssVar]).toBe(`${expected}px`);
      expect(TOKEN_THEMES.dark.spacing[name as keyof typeof TOKEN_THEMES.dark.spacing]).toBe(expected);
    }
  });

  it("radius tokens equal the v2 radius scale", () => {
    for (const [name, cssVar, expected] of RADIUS_MAP) {
      expect(DARK[cssVar]).toBe(`${expected}px`);
      expect(TOKEN_THEMES.dark.radius[name as keyof typeof TOKEN_THEMES.dark.radius]).toBe(expected);
    }
  });

  it("typography sizes come from the 28/20/14/12 scale", () => {
    expect(DARK["--nm-text-display-size"]).toBe("28px");
    expect(DARK["--nm-text-title-size"]).toBe("20px");
    expect(DARK["--nm-text-body-size"]).toBe("14px");
    expect(DARK["--nm-text-caption-size"]).toBe("12px");

    const allowed = new Set([28, 20, 14, 12]);
    const sizes = TOKEN_THEMES.dark.typography.size;
    for (const value of Object.values(sizes)) {
      expect(allowed.has(value), `字号 ${value} 不在 28/20/14/12 四档内`).toBe(true);
    }
  });

  it("font stacks match the CSS font variables", () => {
    const normalize = (stack: string) =>
      stack
        .split(",")
        .map((part) => part.trim().replace(/^["']|["']$/g, "").toLowerCase())
        .join(",");
    const uiVar = /--nm-font-ui:\s*([^;]+);/.exec(css)?.[1] ?? "";
    const dataVar = /--nm-font-data:\s*([^;]+);/.exec(css)?.[1] ?? "";
    expect(normalize(TOKEN_THEMES.dark.typography.fontFamily)).toBe(normalize(uiVar));
    expect(normalize(TOKEN_THEMES.dark.typography.monospace)).toBe(normalize(dataVar));
  });

  it("exposes the active theme through the proxy and switches cleanly", () => {
    expect(getTokenTheme()).toBe("dark");
    expect(tokens.color.bg.app).toBe("#1B1B1B");

    setTokenTheme("light");
    expect(getTokenTheme()).toBe("light");
    expect(tokens.color.bg.app).toBe("#EEEEEE");
    expect(tokens.color.text.primary).toBe("#1A1A1A");

    setTokenTheme("dark");
    expect(tokens.color.bg.app).toBe("#1B1B1B");
  });
});
