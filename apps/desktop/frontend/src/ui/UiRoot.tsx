import { useCallback, useEffect, useLayoutEffect, useMemo, useState } from "react";
import type { DesignPage, Theme } from "../design/types";
import { LibraryClient } from "../library/client";
import { ReaderClient } from "../reader/client";
import { RegionClient } from "../region/client";
import { ResourceChannelClient } from "../resourceChannel/client";
import { SettingsClient } from "../settings/client";
import { WorkbenchClient } from "../workbench/client";
import { Reader } from "../pages/Reader";
import { Settings } from "../pages/Settings";
import { Shelf } from "../pages/Shelf";
import { Workbench } from "../pages/Workbench";
import { CommandPalette } from "./CommandPalette";
import { useThemeController } from "./theme";
import type { CommandSpec, InvokeFn, NavContext, PageChrome, RuntimeClients } from "./types";
import "../design/tokens.css";
import "../design/base.css";
import "../design/acrylic.css";
import "../pages/pages.css";
import "./ui.css";

/**
 * v2 运行时根。
 *
 * 这是产品的**唯一** UI 入口：Tauri 生产窗（`App.tsx` 的 production 分支）与
 * 浏览器 dev 预览都落到这里。三个历史内联样式页面容器（`AppShell` /
 * `BookshelfPage` / `WorkbenchPage` / `ReaderPage` / `SettingsPage`）不再挂在
 * 任何路由上——`UiRoot.test.tsx` 有一条守卫断言盯着这件事，防止出现"两套 UI"。
 *
 * 职责刻意压到最小：主题、当前页、跨页上下文、命令面板、快捷键。取数在各页
 * 自己的容器里做，根只管把 `PageChrome`（框架能力）与 `RuntimeClients`（IPC
 * 客户端）发下去。
 */

export interface UiRootProps {
  invoke?: InvokeFn;
  initialPage?: DesignPage;
  initialTheme?: Theme;
  /** 测试与预览用：注入现成客户端，跳过 `invoke` 装配。 */
  clients?: RuntimeClients;
}

function bridgeMissing(): never {
  throw new Error("TAURI_BRIDGE_MISSING");
}

export function UiRoot({ invoke, initialPage = "shelf", initialTheme = "dark", clients }: UiRootProps) {
  const { theme, toggleTheme } = useThemeController(initialTheme);
  const [activePage, setActivePage] = useState<DesignPage>(initialPage);
  const [context, setContext] = useState<NavContext>({ bookId: null, chapterId: null });
  const [commandOpen, setCommandOpen] = useState(false);

  const runtimeClients = useMemo<RuntimeClients>(() => {
    if (clients) return clients;
    const invokeFn: InvokeFn = invoke ?? (bridgeMissing as unknown as InvokeFn);
    return {
      invoke: invokeFn,
      library: new LibraryClient(invokeFn),
      workbench: new WorkbenchClient(invokeFn),
      region: new RegionClient(invokeFn),
      resource: new ResourceChannelClient(invokeFn),
      reader: new ReaderClient(invokeFn),
      settings: new SettingsClient(invokeFn),
    };
  }, [clients, invoke]);

  // v2 元素级 reset 的作用域标记。App.tsx 的 probe/AC1 证据路径不设它，
  // 因此冻结的运行时路径不会有任何样式泄漏（见 design/base.css 头注释）。
  useLayoutEffect(() => {
    const root = document.documentElement;
    const previousView = root.dataset.view;
    const previousTheme = root.dataset.theme;
    root.dataset.view = "app";
    root.dataset.theme = theme;
    return () => {
      if (previousView === undefined) delete root.dataset.view;
      else root.dataset.view = previousView;
      if (previousTheme === undefined) delete root.dataset.theme;
      else root.dataset.theme = previousTheme;
    };
  }, [theme]);

  const navigate = useCallback((page: DesignPage) => {
    setCommandOpen(false);
    setActivePage(page);
  }, []);

  const openBook = useCallback(
    (bookId: string, chapterId: string | null, target: "workbench" | "reader") => {
      setContext({ bookId, chapterId });
      setActivePage(target);
    },
    [],
  );

  const selectChapter = useCallback((bookId: string, chapterId: string) => {
    setContext({ bookId, chapterId });
  }, []);

  const chrome: PageChrome = useMemo(
    () => ({
      theme,
      activePage,
      onNavigate: navigate,
      onToggleTheme: toggleTheme,
      onOpenCommand: () => setCommandOpen(true),
      commandOpen,
      context,
      onOpenBook: openBook,
      onSelectChapter: selectChapter,
    }),
    [activePage, commandOpen, context, navigate, openBook, selectChapter, theme, toggleTheme],
  );

  // 全局快捷键：Ctrl/Cmd+1..4 切页，Ctrl/Cmd+K 命令面板。
  // 输入框内不劫持 Ctrl+K 之外的组合键，避免和文本框自身的编辑操作打架。
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (!(event.ctrlKey || event.metaKey)) return;
      const target = event.target as HTMLElement | null;
      const typing =
        target?.tagName === "INPUT" ||
        target?.tagName === "TEXTAREA" ||
        target?.tagName === "SELECT" ||
        target?.isContentEditable === true;
      if (event.key.toLowerCase() === "k") {
        event.preventDefault();
        setCommandOpen((open) => !open);
        return;
      }
      if (typing) return;
      const map: Record<string, DesignPage> = {
        "1": "shelf",
        "2": "workbench",
        "3": "reader",
        "4": "settings",
      };
      const page = map[event.key];
      if (page) {
        event.preventDefault();
        navigate(page);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [navigate]);

  const commands: CommandSpec[] = useMemo(() => {
    const jump = (page: DesignPage, label: string, hint: string, icon: string): CommandSpec => ({
      id: `go-${page}`,
      label,
      hint,
      icon,
      disabledReason: activePage === page ? "已在当前页" : undefined,
      run: () => navigate(page),
    });
    return [
      jump("shelf", "前往书架", "浏览与导入作品", "book"),
      jump("workbench", "前往工作台", "页面编辑与流水线", "tool"),
      jump("reader", "前往阅读器", "继续阅读当前章节", "reader"),
      jump("settings", "前往设置", "识别 / 翻译 / 存储与插件", "settings"),
      {
        id: "toggle-theme",
        label: theme === "dark" ? "切换到浅色主题" : "切换到深色主题",
        hint: "Mica / Acrylic 同步换色",
        icon: theme === "dark" ? "sun" : "moon",
        run: toggleTheme,
      },
    ];
  }, [activePage, navigate, theme, toggleTheme]);

  const runtime = { chrome, clients: runtimeClients };

  return (
    <div className="nm-app" data-testid="app-root" data-page={activePage}>
      {activePage === "shelf" && (
        <Shelf
          activePage={activePage}
          theme={theme}
          onNavigate={navigate}
          onToggleTheme={toggleTheme}
          runtime={runtime}
        />
      )}
      {activePage === "workbench" && (
        <Workbench theme={theme} onNavigate={navigate} onToggleTheme={toggleTheme} runtime={runtime} />
      )}
      {activePage === "reader" && (
        <Reader theme={theme} onNavigate={navigate} onToggleTheme={toggleTheme} runtime={runtime} />
      )}
      {activePage === "settings" && (
        <Settings theme={theme} onNavigate={navigate} onToggleTheme={toggleTheme} runtime={runtime} />
      )}

      <CommandPalette
        open={commandOpen}
        onClose={() => setCommandOpen(false)}
        commands={commands}
      />
    </div>
  );
}
