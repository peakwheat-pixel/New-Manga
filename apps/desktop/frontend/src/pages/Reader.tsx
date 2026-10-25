import { useEffect, useState } from "react";
import { Icon } from "../components/Icon";
import { PagePlaceholder } from "../components/PagePlaceholder";
import { PrimaryNav } from "../components/PrimaryNav";
import { StatusMark } from "../components/StatusMark";
import { useAcrylicBudget } from "../design/useAcrylicBudget";
import type { DesignPage, Theme } from "../design/types";

const TOTAL_PAGES = 24;

export interface ReaderProps {
  theme: Theme;
  onNavigate: (page: DesignPage) => void;
  onToggleTheme: () => void;
}

export function Reader({ theme, onNavigate, onToggleTheme }: ReaderProps) {
  const [page, setPage] = useState(12);
  const [spread, setSpread] = useState("single");
  const [direction, setDirection] = useState("ltr");
  const budget = useAcrylicBudget("reader-top", ["reader-top", "reader-bottom"]);

  const step = (delta: number) => {
    setPage((current) => Math.min(TOTAL_PAGES, Math.max(1, current + delta)));
  };

  /*
   * 底栏写着「← → 翻页」就必须真的能翻。骨架阶段只覆盖左右方向键；
   * 没实现的键（曾经的 F 全屏）不留提示，避免做出假承诺。
   */
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const typing =
        target?.tagName === "INPUT" ||
        target?.tagName === "TEXTAREA" ||
        target?.isContentEditable === true;
      if (typing || event.ctrlKey || event.metaKey || event.altKey) return;
      // 焦点在 tablist（一级切换栏 / 检查器 rail）里时，方向键归 tab 导航，
      // 不能再同时翻页——否则一次按键既切页又翻页。
      // 注意 target 可能是 window（测试里就是），必须先确认是 Element 再调 closest。
      if (target instanceof Element && target.closest('[role="tablist"]')) return;
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        step(-1);
      } else if (event.key === "ArrowRight") {
        event.preventDefault();
        step(1);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  return (
    <div className="nm-reader" data-testid="page-reader">
      <header className="nm-titlebar" data-testid="reader-titlebar">
        <div className="nm-titlebar__brand">
          <span className="nm-brand-mark" aria-hidden="true">
            NM
          </span>
          <span className="nm-brand-name">New Manga</span>
        </div>
        <PrimaryNav activePage="reader" onNavigate={onNavigate} />
        <div className="nm-titlebar__actions" style={{ justifyContent: "flex-end" }}>
          <div className="nm-window-buttons" aria-hidden="true">
            <span className="nm-window-btn">
              <Icon name="minus" size={12} />
            </span>
            <span className="nm-window-btn">
              <Icon name="maximize" size={11} />
            </span>
            <span className="nm-window-btn nm-window-btn--close">
              <Icon name="close" size={12} />
            </span>
          </div>
        </div>
      </header>

      <div className="nm-reader__body">
        <div className="nm-reader__page-area">
          <PagePlaceholder pageNumber={page} totalPages={TOTAL_PAGES} chapter="第 12 话" />
        </div>

        <div
          className={`nm-reader__top ${budget.className("reader-top", "acrylic-24")}`}
          data-testid="reader-top"
        >
          <button
            type="button"
            className="nm-btn nm-btn--ghost nm-btn--icon"
            onClick={() => onNavigate("shelf")}
            aria-label="返回书架"
            title="返回书架"
          >
            <Icon name="arrow-left" size={17} />
          </button>
          <span className="nm-reader__chapter">
            <span className="nm-reader__book">雾港来信</span>
            <span className="nm-reader__sep">·</span>
            <span>第 12 话</span>
          </span>
          <span className="nm-data nm-reader__pager">
            {String(page).padStart(3, "0")} / {String(TOTAL_PAGES).padStart(3, "0")}
          </span>
          <StatusMark state="running" />
          <span className="nm-divider" aria-hidden="true" />
          <div className="nm-segmented" role="group" aria-label="阅读模式">
            <button
              type="button"
              data-active={spread === "single"}
              aria-pressed={spread === "single"}
              onClick={() => setSpread("single")}
            >
              单页
            </button>
            <button
              type="button"
              data-active={spread === "double"}
              aria-pressed={spread === "double"}
              onClick={() => setSpread("double")}
            >
              双页
            </button>
          </div>
          <div className="nm-segmented" role="group" aria-label="阅读方向">
            <button
              type="button"
              data-active={direction === "ltr"}
              aria-pressed={direction === "ltr"}
              onClick={() => setDirection("ltr")}
            >
              左 → 右
            </button>
            <button
              type="button"
              data-active={direction === "rtl"}
              aria-pressed={direction === "rtl"}
              onClick={() => setDirection("rtl")}
            >
              右 → 左
            </button>
          </div>
          <span className="nm-reader__spacer" />
          <button
            type="button"
            className="nm-btn nm-btn--ghost nm-btn--icon"
            onClick={() => onNavigate("workbench")}
            aria-label="打开工作台"
            title="打开工作台"
          >
            <Icon name="tool" size={16} />
          </button>
          <button
            type="button"
            className="nm-btn nm-btn--ghost nm-btn--icon"
            aria-label={theme === "dark" ? "切换到浅色主题" : "切换到深色主题"}
            onClick={onToggleTheme}
          >
            <Icon name={theme === "dark" ? "sun" : "moon"} size={16} />
          </button>
          <button type="button" className="nm-btn">
            <Icon name="settings" size={14} />
            设置
          </button>
        </div>

        <button
          type="button"
          className="nm-reader__nav nm-reader__nav--prev"
          onClick={() => step(-1)}
          aria-label="上一页"
        >
          <Icon name="chevron-left" size={20} />
        </button>
        <button
          type="button"
          className="nm-reader__nav nm-reader__nav--next"
          onClick={() => step(1)}
          aria-label="下一页"
        >
          <Icon name="chevron-right" size={20} />
        </button>

        <div
          className={`nm-reader__bottom ${budget.className("reader-bottom", "acrylic-24")}`}
          data-testid="reader-bottom"
        >
          <span className="nm-caption nm-tertiary">本话完成度</span>
          <span className="nm-data">62%</span>
          <div className="nm-progress nm-reader__progress">
            <span style={{ width: "62%" }} />
          </div>
          <span className="nm-caption nm-tertiary">已校对 15 / 24 页</span>
          <span className="nm-reader__spacer" />
          <span className="nm-keyhint">
            <kbd className="nm-kbd">←</kbd>
            <kbd className="nm-kbd">→</kbd>
            翻页
          </span>
          <span className="nm-keyhint">
            <kbd className="nm-kbd">Esc</kbd>
            返回
          </span>
        </div>
      </div>
    </div>
  );
}
