import { useCallback, useLayoutEffect, useState } from "react";
import type { Theme } from "../design/types";
import { setTokenTheme } from "../theme/tokens";

const STORAGE_KEY = "nm.theme";

function readStoredTheme(): Theme | null {
  if (typeof window === "undefined") return null;
  try {
    const value = window.localStorage.getItem(STORAGE_KEY);
    return value === "light" || value === "dark" ? value : null;
  } catch {
    // 隐私模式 / 存储被禁用：主题回落到默认值，不阻断渲染。
    return null;
  }
}

function writeStoredTheme(theme: Theme): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    // 写不进去只影响下次启动的默认值，不影响本次切换。
  }
}

export interface ThemeController {
  theme: Theme;
  setTheme(theme: Theme): void;
  toggleTheme(): void;
}

/**
 * 运行时主题控制器。
 *
 * 关键点：`tokens.ts` 是 Proxy 快照，切换主题必须先 `setTokenTheme()` **再**
 * 触发 React 更新，否则本帧渲染出的内联样式仍是旧主题的颜色。这里在
 * `useLayoutEffect` 之前同步写一次，并在 setter 里先写后 set，保证首帧与后续
 * 切换都自洽；`<html data-theme>` 则交给 layout effect 同步到 CSS 变量层。
 */
export function useThemeController(initialTheme: Theme = "dark"): ThemeController {
  const [theme, setThemeState] = useState<Theme>(() => readStoredTheme() ?? initialTheme);

  // 渲染期同步令牌来源：即便 setter 没被走到（例如初始值来自 localStorage），
  // 首帧的 `tokens.*` 也已经是对应主题。
  setTokenTheme(theme);

  useLayoutEffect(() => {
    const root = document.documentElement;
    const previous = root.dataset.theme;
    root.dataset.theme = theme;
    return () => {
      if (previous === undefined) delete root.dataset.theme;
      else root.dataset.theme = previous;
    };
  }, [theme]);

  const setTheme = useCallback((next: Theme) => {
    setTokenTheme(next);
    writeStoredTheme(next);
    setThemeState(next);
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState((current) => {
      const next: Theme = current === "dark" ? "light" : "dark";
      setTokenTheme(next);
      writeStoredTheme(next);
      return next;
    });
  }, []);

  return { theme, setTheme, toggleTheme };
}
