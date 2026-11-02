/**
 * 主题切换必须覆盖到"模块级样式常量"。
 *
 * 背景（UIUX-V2-RUNTIME-1 真机自查发现）：`settingsInputStyle` /
 * `settingsSelectStyle` 原本是模块级 `{ ...tokens.x }` 常量，import 那一刻就
 * 把深色值冻结下来了。运行时切到浅色主题后，设置页的下拉框仍是深色底，
 * 与页面其余部分打架——而 jsdom 不应用样式表，渲染测试全绿也发现不了这类
 * "值冻结"问题，只有直接断言常量本身才能拦住回退。
 */
import { afterEach, describe, expect, it } from "vitest";
import { settingsInputStyle, settingsSelectStyle } from "../settings/SectionField";
import { TOKEN_THEMES, setTokenTheme } from "./tokens";

afterEach(() => {
  setTokenTheme("dark");
});

describe("module-level style constants follow the active token theme", () => {
  it("settingsSelectStyle switches background with the theme", () => {
    setTokenTheme("dark");
    expect(settingsSelectStyle.background).toBe(TOKEN_THEMES.dark.color.surface.card);
    expect(settingsSelectStyle.color).toBe(TOKEN_THEMES.dark.color.text.primary);

    setTokenTheme("light");
    expect(settingsSelectStyle.background).toBe(TOKEN_THEMES.light.color.surface.card);
    expect(settingsSelectStyle.color).toBe(TOKEN_THEMES.light.color.text.primary);
    expect(settingsSelectStyle.background).toBe("#FFFFFF");
  });

  it("settingsInputStyle switches border with the theme", () => {
    setTokenTheme("dark");
    expect(settingsInputStyle.border).toContain(TOKEN_THEMES.dark.color.border.default);

    setTokenTheme("light");
    expect(settingsInputStyle.border).toContain(TOKEN_THEMES.light.color.border.default);
  });

  it("keeps enumerable keys stable across themes", () => {
    setTokenTheme("dark");
    const darkKeys = Object.keys(settingsSelectStyle).sort();
    setTokenTheme("light");
    const lightKeys = Object.keys(settingsSelectStyle).sort();
    expect(lightKeys).toEqual(darkKeys);
    // 行内样式要被 React 的 for...in 枚举到，键不能为空。
    expect(darkKeys.length).toBeGreaterThan(3);
  });
});
