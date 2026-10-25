import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const css = readFileSync(resolve(process.cwd(), "src/design/base.css"), "utf8");

/**
 * base.css 里的元素级 reset 必须只作用于设计预览，而且**不能提升特异性**。
 *
 * 背景：这些 reset 原本没有任何前缀，静默泄漏到冻结的 Tauri 运行时路径。
 * 加 `html[data-view="design"]` 前缀能堵住泄漏，但会把特异性从 (0,0,1) 抬到
 * (0,1,2)，反超所有单类组件规则（`.nm-btn`、`.nm-tab` 都是 (0,1,0)），结果是
 * 设计视图里按钮/卡片/胶囊的边框、底色、内边距被全部压掉——而 jsdom 不应用
 * 样式表，vitest 全绿也发现不了。`:where()` 的特异性恒为 0，所以前缀必须用它。
 */
describe("base.css element resets", () => {
  it("never uses a bare html[data-view] prefix", () => {
    expect(css).not.toMatch(/^html\[data-view/m);
    expect(css).not.toMatch(/,\s*html\[data-view/m);
  });

  it("scopes every rule with zero-specificity :where()", () => {
    const rules = [...css.matchAll(/^([^\s@/{}][^{}]*?)\s*\{/gm)].map((match) => match[1].trim());
    expect(rules.length).toBeGreaterThan(0);

    const unscoped = rules.filter(
      (selector) => !selector.startsWith(":where(") && !selector.startsWith("."),
    );
    expect(unscoped).toEqual([]);
  });

  it("still covers the full set of resets", () => {
    const prefixed = css.match(/:where\(html\[data-view="design"\]\)/g) ?? [];
    // 22 处：*、html/body/#root、html、body、四个表单元素、button、disabled、
    // svg、::selection、:focus-visible、滚动条 4 条等。
    expect(prefixed.length).toBeGreaterThanOrEqual(20);
  });
});
