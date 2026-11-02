import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const css = readFileSync(resolve(process.cwd(), "src/design/base.css"), "utf8");

/** 去掉注释，避免注释里的示例选择器污染断言。 */
function stripComments(source: string): string {
  return source.replace(/\/\*[\s\S]*?\*\//g, "");
}

/**
 * 收集 CSS 中所有「规则块的 selector 列表」。
 *
 * 旧版守卫用的是 `^([^\s@/{}][^{}]*?)\s*\{`，有两个盲区：
 *   1. 缩进的选择器（行首有空白）永远匹配不到 → 加个两空格缩进就能绕过；
 *   2. `@media` / `@supports` 块内的规则同样匹配不到 → 把未作用域的
 *      元素选择器塞进 `@media` 就完全不会被检查。
 * 这里改成「取每个 `{` 之前最近的非空、不含 `{}` 的片段」，再做 at-rule
 * 判定，缩进和多层嵌套都不影响结果。
 */
function collectSelectors(source: string): string[] {
  const selectors: string[] = [];
  const body = stripComments(source);
  for (const match of body.matchAll(/([^{}]+)\{/g)) {
    const raw = match[1].trim();
    if (!raw) continue;
    if (raw.endsWith(";")) continue; // 声明块内部（@media 里的声明也会命中）
    if (raw.startsWith("@")) continue; // @media / @supports / @keyframes 帧
    for (const part of raw.split(",")) {
      const selector = part.trim();
      if (selector) selectors.push(selector);
    }
  }
  return selectors;
}

/**
 * base.css 里的元素级 reset 必须只作用于 v2 根，而且**不能提升特异性**。
 *
 * 背景：这些 reset 原本没有任何前缀，静默泄漏到冻结的 Tauri 运行时路径。
 * 加 `html[data-view]` 前缀能堵住泄漏，但会把特异性从 (0,0,1) 抬到 (0,1,1)，
 * 反超所有单类组件规则（`.nm-btn`、`.nm-tab` 都是 (0,1,0)），结果是按钮/
 * 卡片/胶囊的边框、底色、内边距被全部压掉——而 jsdom 不应用样式表，vitest
 * 全绿也发现不了。`:where()` 的特异性恒为 0，所以前缀必须用它。
 */
describe("base.css element resets", () => {
  it("never uses a bare html[data-view] prefix", () => {
    const body = stripComments(css);
    // 去掉所有合法的 :where(html[data-view]) 之后，不应再出现任何裸前缀。
    const stripped = body.replace(/:where\(\s*html\[data-view\]\s*\)/g, "");
    expect(stripped).not.toMatch(/html\[data-view/);
  });

  it("scopes every rule with zero-specificity :where()", () => {
    const selectors = collectSelectors(css);
    expect(selectors.length).toBeGreaterThan(0);

    const unscoped = selectors.filter(
      (selector) => !selector.startsWith(":where(") && !selector.startsWith("."),
    );
    // 两处显式例外，都必须带注释说明：
    //   1. @keyframes 帧（`from` / `to` / `0%`）不是选择器；
    //   2. 末尾 `@media (prefers-reduced-motion: reduce)` 里的通配降级
    //      (`*` / `*::before` / `*::after`) 是刻意的全局无障碍兜底——动效缩减
    //      必须对冻结的 probe/AC1 路径同样生效，不能只护 v2 根。
    const real = unscoped.filter(
      (selector) => !/^(from|to|-?\d+(?:\.\d+)?%)$/.test(selector) && !selector.startsWith("*"),
    );
    expect(real).toEqual([]);
  });

  it("checks rules nested inside @media/@supports blocks too", () => {
    // 守卫自指：确认收集器确实看得见 @media 内的选择器，否则本文件
    // 的 "没有裸元素选择器" 断言就是在自我安慰。
    const synthetic = "@media (min-width: 1px) {\n  :where(html[data-view]) button { color: red; }\n  html button { color: red; }\n}";
    expect(collectSelectors(synthetic)).toEqual([
      ":where(html[data-view]) button",
      "html button",
    ]);
  });

  it("still covers the full set of resets", () => {
    const prefixed = css.match(/:where\(html\[data-view\]\)/g) ?? [];
    // 22 处：*、html/body/#root、html、body、四个表单元素、button、disabled、
    // svg、::selection、:focus-visible、滚动条 4 条等。
    expect(prefixed.length).toBeGreaterThanOrEqual(20);
  });

  it("keys on attribute presence, not a single view value", () => {
    // 两个 v2 根共用这套 reset：DesignPreview 写 data-view="design"，
    // UiRoot 写 data-view="app"。一旦把值写死进选择器，运行时就会丢 reset。
    const body = stripComments(css);
    expect(body).not.toMatch(/data-view\s*=\s*["']/);
  });
});
