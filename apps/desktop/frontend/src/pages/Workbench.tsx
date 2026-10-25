import { useRef, useState, type CSSProperties, type KeyboardEvent } from "react";
import { Icon, type IconName } from "../components/Icon";
import { PrimaryNav } from "../components/PrimaryNav";
import { PagePlaceholder } from "../components/PagePlaceholder";
import { StatusMark, type StatusState } from "../components/StatusMark";
import { useAcrylicBudget } from "../design/useAcrylicBudget";
import type { DesignPage, Theme } from "../design/types";

interface Stage {
  id: string;
  label: string;
  state: StatusState;
}

const STAGES: Stage[] = [
  { id: "import", label: "导入", state: "done" },
  { id: "split", label: "切分", state: "done" },
  { id: "detect", label: "检测", state: "done" },
  { id: "ocr", label: "识别", state: "done" },
  { id: "translate", label: "翻译", state: "running" },
  { id: "typeset", label: "排版", state: "queued" },
  { id: "inpaint", label: "修复", state: "queued" },
  { id: "proof", label: "校对", state: "notStarted" },
  { id: "export", label: "导出", state: "notStarted" },
  { id: "done", label: "完成", state: "notStarted" },
];

const PAGES = Array.from({ length: 18 }, (_, index) => index + 1);

const REGIONS: Array<{ id: string; label: string; tone: string; state: StatusState; text: string }> = [
  { id: "r-01", label: "对白 01", tone: "var(--nm-accent-base)", state: "done", text: "先别回头。" },
  { id: "r-02", label: "对白 02", tone: "var(--nm-status-done)", state: "running", text: "就是这里。" },
  { id: "r-03", label: "旁白 01", tone: "var(--nm-status-stale)", state: "queued", text: "雾从港口漫上来。" },
  { id: "r-04", label: "拟声 01", tone: "var(--nm-status-blocked)", state: "blocked", text: "……" },
];

const RAIL: Array<{ id: string; label: string; icon: IconName }> = [
  { id: "layers", label: "图层", icon: "layers" },
  { id: "text", label: "文本", icon: "type" },
  { id: "image", label: "图像", icon: "image" },
  { id: "repair", label: "修复", icon: "wand" },
  { id: "export", label: "导出", icon: "export" },
];

function stageColor(state: StatusState): string {
  return state === "notStarted" ? "var(--nm-status-skipped)" : `var(--nm-status-${state})`;
}

export interface WorkbenchProps {
  theme: Theme;
  onNavigate: (page: DesignPage) => void;
  onToggleTheme: () => void;
}

export function Workbench({ theme, onNavigate, onToggleTheme }: WorkbenchProps) {
  const [selectedPage, setSelectedPage] = useState(12);
  const [activeRail, setActiveRail] = useState("layers");
  const budget = useAcrylicBudget("workbench-inspector", ["workbench-inspector"]);
  const railRefs = useRef<Record<string, HTMLButtonElement | null>>({});

  // 垂直 tablist 的 roving tabindex：上下方向键移动并同步焦点。
  const onRailKeyDown = (event: KeyboardEvent<HTMLButtonElement>, current: string) => {
    const index = RAIL.findIndex((item) => item.id === current);
    let next = -1;
    if (event.key === "ArrowDown") next = (index + 1) % RAIL.length;
    else if (event.key === "ArrowUp") next = (index - 1 + RAIL.length) % RAIL.length;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = RAIL.length - 1;
    if (next < 0) return;
    event.preventDefault();
    const target = RAIL[next];
    setActiveRail(target.id);
    railRefs.current[target.id]?.focus();
  };

  return (
    <div className="nm-workbench nm-mica" data-testid="page-workbench">
      <header className="nm-titlebar" data-testid="workbench-titlebar">
        <div className="nm-titlebar__brand">
          <span className="nm-brand-mark" aria-hidden="true">
            NM
          </span>
          <span className="nm-brand-name">New Manga</span>
        </div>
        <PrimaryNav activePage="workbench" onNavigate={onNavigate} />
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
      <div className="nm-workbench__body">
        <aside className="nm-filmstrip" data-testid="filmstrip" aria-label="胶片条">
          <button
            type="button"
            className="nm-filmstrip__back"
            onClick={() => onNavigate("shelf")}
            aria-label="返回书架"
            title="返回书架"
          >
            <Icon name="chevron-left" size={16} />
          </button>
          <div className="nm-filmstrip__list">
            {PAGES.map((page) => (
              <button
                key={page}
                type="button"
                className="nm-filmstrip__item"
                data-active={page === selectedPage}
                aria-pressed={page === selectedPage}
                aria-label={`第 ${page} 页`}
                onClick={() => setSelectedPage(page)}
              >
                <span className="nm-filmstrip__thumb" aria-hidden="true">
                  <span className="nm-filmstrip__mini" />
                </span>
                <span className="nm-filmstrip__no">{String(page).padStart(3, "0")}</span>
              </button>
            ))}
          </div>
        </aside>

        <main className="nm-canvas" data-testid="workbench-canvas">
          <div className="nm-canvas__bar">
            <button type="button" className="nm-btn nm-btn--ghost" onClick={() => onNavigate("shelf")}>
              <Icon name="chevron-left" size={14} />
              书架
            </button>
            <span className="nm-divider" aria-hidden="true" />
            <span className="nm-canvas__crumb">
              <span className="nm-truncate">雾港来信</span>
              <Icon name="chevron-right" size={12} />
              <span className="nm-truncate">第 12 话</span>
            </span>
            <span className="nm-tag">
              <Icon name="layers" size={12} />
              原稿层
            </span>
            <span className="nm-canvas__bar-spacer" />
            <StatusMark state="running" />
            <button
              type="button"
              className="nm-btn nm-btn--ghost nm-btn--icon"
              aria-label={theme === "dark" ? "切换到浅色主题" : "切换到深色主题"}
              onClick={onToggleTheme}
            >
              <Icon name={theme === "dark" ? "sun" : "moon"} size={15} />
            </button>
            <button type="button" className="nm-btn" onClick={() => onNavigate("reader")}>
              <Icon name="reader" size={14} />
              阅读器
            </button>
          </div>

          <div className="nm-canvas__stage" data-testid="canvas-stage">
            <PagePlaceholder pageNumber={selectedPage} totalPages={24} chapter="第 12 话" />
          </div>

          <div className="nm-canvas__tools" aria-label="缩放">
            <button type="button" className="nm-btn nm-btn--ghost nm-btn--icon" aria-label="缩小">
              <Icon name="zoom-out" size={14} />
            </button>
            <span className="nm-data">100%</span>
            <button type="button" className="nm-btn nm-btn--ghost nm-btn--icon" aria-label="放大">
              <Icon name="zoom-in" size={14} />
            </button>
            <span className="nm-divider" aria-hidden="true" />
            <button type="button" className="nm-btn nm-btn--ghost nm-btn--icon" aria-label="适配窗口">
              <Icon name="maximize" size={13} />
            </button>
          </div>
        </main>

        <aside
          className={`nm-inspector ${budget.className("workbench-inspector", "acrylic")}`}
          data-testid="inspector"
          aria-label="检查器"
        >
          <div className="nm-inspector__rail">
            {/*
             * tablist 里只能放 tab。主题切换与设置是普通按钮，原先混在
             * tablist 内属于 ARIA 结构违规，这里把它们移出分组。
             */}
            <div
              className="nm-rail-group"
              role="tablist"
              aria-label="检查器分类"
              aria-orientation="vertical"
            >
              {RAIL.map((item) => (
                <button
                  key={item.id}
                  ref={(element) => {
                    railRefs.current[item.id] = element;
                  }}
                  type="button"
                  role="tab"
                  aria-selected={activeRail === item.id}
                  tabIndex={activeRail === item.id ? 0 : -1}
                  aria-label={item.label}
                  title={item.label}
                  className="nm-rail-btn"
                  data-active={activeRail === item.id}
                  onClick={() => setActiveRail(item.id)}
                  onKeyDown={(event) => onRailKeyDown(event, item.id)}
                >
                  <Icon name={item.icon} size={17} />
                </button>
              ))}
            </div>
            <span className="nm-inspector__rail-spacer" />
            <button
              type="button"
              className="nm-rail-btn"
              aria-label={theme === "dark" ? "切换到浅色主题" : "切换到深色主题"}
              title="切换主题"
              onClick={onToggleTheme}
            >
              <Icon name={theme === "dark" ? "sun" : "moon"} size={17} />
            </button>
            <button type="button" className="nm-rail-btn" aria-label="设置" title="设置">
              <Icon name="settings" size={17} />
            </button>
          </div>

          <div className="nm-inspector__panel">
            <div className="nm-inspector__head">
              <div>
                <div className="nm-body-strong">检查器</div>
                <div className="nm-caption nm-tertiary">第 012 页 · 原稿</div>
              </div>
              <button type="button" className="nm-btn nm-btn--ghost nm-btn--icon" aria-label="收起检查器">
                <Icon name="panel" size={16} />
              </button>
            </div>

            <div className="nm-inspector__status">
              <StatusMark state="running" />
              <span className="nm-caption nm-tertiary">修订 7 · 2 分钟前</span>
            </div>

            <section className="nm-inspector__section">
              <div className="nm-inspector__section-head">
                <span className="nm-body-strong">识别结果</span>
                <button type="button" className="nm-detail__link">
                  <Icon name="refresh" size={12} />
                  重跑
                </button>
              </div>
              <div className="nm-ocr-box">
                <p>雾从港口漫上来，路灯一盏一盏地熄灭。</p>
                <p>「先别回头。」</p>
                <p>「就是这里。」</p>
                <span className="nm-ocr-box__meta nm-data">JA → ZH · 置信度 0.94</span>
              </div>
            </section>

            <section className="nm-inspector__section">
              <div className="nm-inspector__section-head">
                <span className="nm-body-strong">区域</span>
                <span className="nm-data nm-tertiary">{REGIONS.length}</span>
              </div>
              <ul className="nm-region-list">
                {REGIONS.map((region) => (
                  <li key={region.id}>
                    <button type="button" className="nm-region">
                      <span
                        className="nm-region__tone"
                        style={{ "--region-tone": region.tone } as CSSProperties}
                        aria-hidden="true"
                      />
                      <span className="nm-region__copy">
                        <span className="nm-region__label">{region.label}</span>
                        <span className="nm-region__text nm-truncate">{region.text}</span>
                      </span>
                      <StatusMark state={region.state} showLabel={false} />
                    </button>
                  </li>
                ))}
              </ul>
            </section>

            <section className="nm-inspector__section">
              <div className="nm-inspector__section-head">
                <span className="nm-body-strong">流水线参数</span>
              </div>
              <dl className="nm-kv">
                <div>
                  <dt>识别模型</dt>
                  <dd>manga-ocr · v3</dd>
                </div>
                <div>
                  <dt>目标语言</dt>
                  <dd>简体中文</dd>
                </div>
                <div>
                  <dt>排版策略</dt>
                  <dd>气泡内自动</dd>
                </div>
              </dl>
            </section>

            <div className="nm-inspector__actions">
              <button type="button" className="nm-btn nm-btn--primary">
                <Icon name="play" size={14} />
                运行到校对
              </button>
              <button type="button" className="nm-btn nm-btn--icon" aria-label="导出">
                <Icon name="export" size={15} />
              </button>
            </div>
          </div>
        </aside>
      </div>

      <footer className="nm-pipeline" data-testid="pipeline" aria-label="流水线">
        <div className="nm-pipeline__stages">
          {STAGES.map((stage) => (
            <div
              key={stage.id}
              className="nm-stage"
              data-state={stage.state}
              style={{ "--stage-color": stageColor(stage.state) } as CSSProperties}
            >
              <span className="nm-stage__dot" aria-hidden="true" />
              <span className="nm-stage__label">{stage.label}</span>
            </div>
          ))}
        </div>
        <div className="nm-pipeline__meter">
          <span className="nm-caption nm-tertiary">本话</span>
          <div className="nm-progress nm-pipeline__progress">
            <span style={{ width: "62%" }} />
          </div>
          <span className="nm-data">62%</span>
        </div>
      </footer>
    </div>
  );
}
