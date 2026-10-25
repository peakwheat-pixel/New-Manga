import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { Icon, type IconName } from "../components/Icon";
import { PrimaryNav } from "../components/PrimaryNav";
import { StatusMark, type StatusState } from "../components/StatusMark";
import { useAcrylicBudget } from "../design/useAcrylicBudget";
import type { DesignPage, Theme } from "../design/types";

interface Book {
  id: string;
  title: string;
  author: string;
  volume: string;
  chapters: number;
  pages: number;
  progress: number;
  updated: string;
  state: StatusState;
  tags: string[];
  coverA: string;
  coverB: string;
}

const BOOKS: Book[] = [
  {
    id: "b-01",
    title: "雾港来信",
    author: "南野灯",
    volume: "VOL.07",
    chapters: 42,
    pages: 1280,
    progress: 68,
    updated: "12 分钟前",
    state: "running",
    tags: ["悬疑", "周刊"],
    coverA: "#284867",
    coverB: "#101C29",
  },
  {
    id: "b-02",
    title: "白昼残响",
    author: "绫濑千景",
    volume: "VOL.03",
    chapters: 28,
    pages: 892,
    progress: 100,
    updated: "1 小时前",
    state: "done",
    tags: ["科幻", "完结"],
    coverA: "#5C3131",
    coverB: "#231012",
  },
  {
    id: "b-03",
    title: "春日构造",
    author: "远山青",
    volume: "VOL.02",
    chapters: 18,
    pages: 540,
    progress: 31,
    updated: "3 小时前",
    state: "queued",
    tags: ["日常", "治愈"],
    coverA: "#315643",
    coverB: "#0F1F18",
  },
  {
    id: "b-04",
    title: "铁与麦穗",
    author: "小坂井",
    volume: "VOL.11",
    chapters: 61,
    pages: 1904,
    progress: 84,
    updated: "昨天",
    state: "stale",
    tags: ["历史", "剧场"],
    coverA: "#5A4726",
    coverB: "#221A0D",
  },
  {
    id: "b-05",
    title: "夜航西飞",
    author: "三浦真白",
    volume: "VOL.05",
    chapters: 35,
    pages: 1042,
    progress: 12,
    updated: "昨天",
    state: "blocked",
    tags: ["航空", "群像"],
    coverA: "#443058",
    coverB: "#181020",
  },
  {
    id: "b-06",
    title: "深蓝回声",
    author: "橘朱里",
    volume: "VOL.09",
    chapters: 50,
    pages: 1512,
    progress: 47,
    updated: "2 天前",
    state: "running",
    tags: ["海洋", "悬疑"],
    coverA: "#274B57",
    coverB: "#0D1B20",
  },
  {
    id: "b-07",
    title: "无人车站",
    author: "冬月透",
    volume: "VOL.01",
    chapters: 12,
    pages: 360,
    progress: 0,
    updated: "3 天前",
    state: "notStarted",
    tags: ["短篇", "新作"],
    coverA: "#533040",
    coverB: "#211018",
  },
  {
    id: "b-08",
    title: "玻璃星图",
    author: "白鸟悠",
    volume: "VOL.04",
    chapters: 33,
    pages: 980,
    progress: 73,
    updated: "4 天前",
    state: "failed",
    tags: ["天文", "奇幻"],
    coverA: "#2E3F61",
    coverB: "#111827",
  },
  {
    id: "b-09",
    title: "午后三点",
    author: "森下葵",
    volume: "VOL.06",
    chapters: 39,
    pages: 1128,
    progress: 55,
    updated: "5 天前",
    state: "skipped",
    tags: ["校园", "连载"],
    coverA: "#4D4A2D",
    coverB: "#1C1B0F",
  },
  {
    id: "b-10",
    title: "黑箱手记",
    author: "九条莲",
    volume: "VOL.08",
    chapters: 44,
    pages: 1336,
    progress: 91,
    updated: "上周",
    state: "done",
    tags: ["推理", "完结"],
    coverA: "#3A3A3E",
    coverB: "#141416",
  },
];

const FILTERS = ["全部", "连载中", "待翻译", "已完成", "已归档"];

const CHAPTERS: Array<{ index: string; title: string; pages: number; state: StatusState }> = [
  { index: "012", title: "潮汐留下的名字", pages: 24, state: "running" },
  { index: "011", title: "第七盏路灯", pages: 22, state: "done" },
  { index: "010", title: "没有寄出的信", pages: 26, state: "done" },
  { index: "009", title: "雾中的仓库", pages: 20, state: "stale" },
  { index: "008", title: "雨夜访客", pages: 24, state: "done" },
];

interface Command {
  id: string;
  label: string;
  hint: string;
  icon: IconName;
  action: () => void;
}

export interface ShelfProps {
  activePage: DesignPage;
  theme: Theme;
  onNavigate: (page: DesignPage) => void;
  onToggleTheme: () => void;
}

function coverStyle(book: Book): CSSProperties {
  return {
    "--cover-a": book.coverA,
    "--cover-b": book.coverB,
  } as CSSProperties;
}

export function Shelf({ activePage, theme, onNavigate, onToggleTheme }: ShelfProps) {
  const [selectedId, setSelectedId] = useState(BOOKS[0].id);
  const [activeFilter, setActiveFilter] = useState(FILTERS[0]);
  const [query, setQuery] = useState("");
  const [paletteOpen, setPaletteOpen] = useState(false);

  const selected = useMemo(
    () => BOOKS.find((book) => book.id === selectedId) ?? BOOKS[0],
    [selectedId],
  );

  const layers = paletteOpen
    ? ["shelf-detail", "shelf-status", "shelf-command"]
    : ["shelf-detail", "shelf-status"];
  const budget = useAcrylicBudget(paletteOpen ? "shelf-command" : "shelf-detail", layers);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setPaletteOpen((open) => !open);
        return;
      }
      if (event.key === "Escape") setPaletteOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const commands: Command[] = [
    {
      id: "workbench",
      label: "打开工作台",
      hint: "当前作品 · 第 12 话",
      icon: "tool",
      action: () => onNavigate("workbench"),
    },
    {
      id: "reader",
      label: "进入阅读器",
      hint: "从第 12 页继续",
      icon: "reader",
      action: () => onNavigate("reader"),
    },
    {
      id: "theme",
      label: theme === "dark" ? "切换到浅色主题" : "切换到深色主题",
      hint: "Mica / Acrylic 同步换色",
      icon: theme === "dark" ? "sun" : "moon",
      action: onToggleTheme,
    },
    {
      id: "import",
      label: "导入本地文件夹",
      hint: "静态骨架 · 未接 IPC",
      icon: "upload",
      action: () => undefined,
    },
    {
      id: "new",
      label: "新建作品",
      hint: "从空白章节开始",
      icon: "plus",
      action: () => undefined,
    },
  ];

  const runCommand = (command: Command) => {
    setPaletteOpen(false);
    command.action();
  };

  return (
    <div className="nm-shelf nm-mica" data-testid="page-shelf">
      <header className="nm-titlebar" data-testid="shelf-titlebar">
        <div className="nm-titlebar__brand">
          <span className="nm-brand-mark" aria-hidden="true">
            NM
          </span>
          <span className="nm-brand-name">New Manga</span>
        </div>

        <PrimaryNav activePage={activePage} onNavigate={onNavigate} />

        <div className="nm-titlebar__actions">
          <button
            type="button"
            className="nm-command-trigger"
            data-testid="command-trigger"
            onClick={() => setPaletteOpen(true)}
            aria-haspopup="dialog"
            aria-expanded={paletteOpen}
          >
            <Icon name="search" size={14} />
            <span>搜索或执行命令</span>
            <span className="nm-command-trigger__keys">
              <kbd className="nm-kbd">Ctrl</kbd>
              <kbd className="nm-kbd">K</kbd>
            </span>
          </button>
          <button
            type="button"
            className="nm-btn nm-btn--ghost nm-btn--icon"
            aria-label={theme === "dark" ? "切换到浅色主题" : "切换到深色主题"}
            data-testid="theme-toggle"
            onClick={onToggleTheme}
          >
            <Icon name={theme === "dark" ? "sun" : "moon"} size={16} />
          </button>
          <div className="nm-window-buttons" data-testid="window-buttons" aria-hidden="true">
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

      <div className="nm-toolbar" data-testid="shelf-toolbar">
        <label className="nm-input nm-search">
          <Icon name="search" size={15} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="搜索书名、作者或章节"
            aria-label="搜索书架"
          />
          {query ? (
            <button
              type="button"
              className="nm-search__clear"
              aria-label="清除搜索"
              onClick={() => setQuery("")}
            >
              <Icon name="close" size={12} />
            </button>
          ) : (
            <span className="nm-data nm-tertiary">/</span>
          )}
        </label>

        <div className="nm-chips" role="group" aria-label="筛选">
          {FILTERS.map((filter) => (
            <button
              key={filter}
              type="button"
              className="nm-chip"
              data-active={activeFilter === filter}
              aria-pressed={activeFilter === filter}
              onClick={() => setActiveFilter(filter)}
            >
              {filter}
            </button>
          ))}
        </div>

        <div className="nm-toolbar__right">
          <label className="nm-select-wrap nm-sort">
            <span className="nm-sr-only">排序方式</span>
            <select className="nm-select" defaultValue="updated" aria-label="排序方式">
              <option value="updated">最近更新</option>
              <option value="title">书名 A–Z</option>
              <option value="progress">进度</option>
            </select>
            <Icon name="chevron-down" size={13} />
          </label>

          <div className="nm-segmented" role="group" aria-label="视图方式">
            <button type="button" data-active="true" aria-label="网格视图">
              <Icon name="grid" size={13} />
            </button>
            <button type="button" aria-label="列表视图">
              <Icon name="list" size={13} />
            </button>
          </div>

          <button type="button" className="nm-btn">
            <Icon name="upload" size={15} />
            导入
          </button>
          <button type="button" className="nm-btn nm-btn--primary">
            <Icon name="plus" size={15} />
            新建
          </button>
        </div>
      </div>

      <main className="nm-shelf__main">
        <section className="nm-shelf__library" aria-label="书架内容">
          <div className="nm-section-head">
            <div>
              <h1 className="nm-title">全部作品</h1>
              <p className="nm-caption nm-tertiary">24 部作品 · 10 部正在显示</p>
            </div>
            <div className="nm-section-head__meta">
              <span className="nm-tag">
                <Icon name="clock" size={12} />
                同步于 2 分钟前
              </span>
              <button type="button" className="nm-btn nm-btn--ghost nm-btn--icon" aria-label="更多操作">
                <Icon name="more" size={16} />
              </button>
            </div>
          </div>

          <div className="nm-book-grid" data-testid="shelf-grid">
            {BOOKS.map((book) => (
              <button
                key={book.id}
                type="button"
                className="nm-book-card"
                data-active={book.id === selectedId}
                aria-pressed={book.id === selectedId}
                data-testid={`book-${book.id}`}
                onClick={() => setSelectedId(book.id)}
              >
                <span className="nm-book-cover" style={coverStyle(book)}>
                  <span className="nm-book-cover__wash" aria-hidden="true" />
                  <span className="nm-book-cover__kicker">NEW MANGA</span>
                  <span className="nm-book-cover__title">{book.title}</span>
                  <span className="nm-book-cover__volume">{book.volume}</span>
                  <StatusMark state={book.state} showLabel={false} className="nm-book-cover__status" />
                </span>
                <span className="nm-book-meta">
                  <span className="nm-book-title">{book.title}</span>
                  <span className="nm-book-count">
                    {book.chapters} 话 · {book.pages} 页
                  </span>
                  <span className="nm-progress" aria-hidden="true">
                    <span style={{ width: `${book.progress}%` }} />
                  </span>
                  <span className="nm-book-foot">
                    <span>{book.updated}</span>
                    <span className="nm-data">{book.progress}%</span>
                  </span>
                </span>
              </button>
            ))}
          </div>
        </section>

        <aside
          className={`nm-detail ${budget.className("shelf-detail", "acrylic")}`}
          data-testid="shelf-detail"
          aria-label="作品详情"
        >
          <div className="nm-detail__head">
            <div className="nm-detail__cover" style={coverStyle(selected)} aria-hidden="true">
              <span>{selected.volume}</span>
            </div>
            <div className="nm-detail__identity">
              <StatusMark state={selected.state} />
              <h2 className="nm-detail__title">{selected.title}</h2>
              <p className="nm-caption nm-tertiary">{selected.author} · 连载中</p>
              <div className="nm-detail__tags">
                {selected.tags.map((tag) => (
                  <span key={tag} className="nm-tag">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="nm-detail__stats">
            <div className="nm-stat">
              <span className="nm-stat__value nm-data">{selected.chapters}</span>
              <span className="nm-stat__label">章节</span>
            </div>
            <div className="nm-stat">
              <span className="nm-stat__value nm-data">{selected.pages}</span>
              <span className="nm-stat__label">页数</span>
            </div>
            <div className="nm-stat">
              <span className="nm-stat__value nm-data">03</span>
              <span className="nm-stat__label">待处理</span>
            </div>
          </div>

          <div className="nm-detail__section-head">
            <span className="nm-body-strong">章节</span>
            <button type="button" className="nm-detail__link">
              查看全部
              <Icon name="chevron-right" size={13} />
            </button>
          </div>

          <ul className="nm-chapter-list" data-testid="chapter-list">
            {CHAPTERS.map((chapter) => (
              <li key={chapter.index}>
                <button type="button" className="nm-chapter" data-active={chapter.index === "012"}>
                  <span className="nm-chapter__index nm-data">{chapter.index}</span>
                  <span className="nm-chapter__title">{chapter.title}</span>
                  <span className="nm-chapter__pages nm-data">{chapter.pages}p</span>
                  <StatusMark state={chapter.state} showLabel={false} />
                </button>
              </li>
            ))}
          </ul>

          <div className="nm-detail__progress">
            <div className="nm-detail__section-head">
              <span className="nm-body-strong">翻译进度</span>
              <span className="nm-data nm-tertiary">{selected.progress}%</span>
            </div>
            <div className="nm-progress">
              <span style={{ width: `${selected.progress}%` }} />
            </div>
          </div>

          <div className="nm-detail__actions">
            <button type="button" className="nm-btn nm-btn--primary" onClick={() => onNavigate("reader")}>
              <Icon name="play" size={14} />
              继续阅读
            </button>
            <button type="button" className="nm-btn" onClick={() => onNavigate("workbench")}>
              <Icon name="tool" size={14} />
              工作台
            </button>
          </div>
        </aside>
      </main>

      <div
        className={`nm-floating-status ${budget.className("shelf-status", "acrylic-24")}`}
        data-testid="shelf-statusbar"
        role="status"
        aria-live="polite"
      >
        <StatusMark state="running" />
        <span className="nm-floating-status__text">流水线运行中</span>
        <span className="nm-data nm-tertiary">03 / 08</span>
        <div className="nm-floating-status__progress">
          <div className="nm-progress">
            <span style={{ width: "62%" }} />
          </div>
        </div>
        <span className="nm-caption nm-tertiary">第 3 话 · 翻译 62%</span>
        <span className="nm-floating-status__spacer" />
        <span className="nm-core">
          <span className="nm-core__dot" aria-hidden="true" />
          Core 正常
        </span>
        <span className="nm-divider" aria-hidden="true" />
        <span className="nm-data nm-tertiary">2 个任务</span>
      </div>

      {paletteOpen && (
        <div
          className="nm-command-backdrop"
          data-testid="command-backdrop"
          onMouseDown={() => setPaletteOpen(false)}
        >
          <div
            className={`nm-command ${budget.className("shelf-command", "acrylic-strong")}`}
            role="dialog"
            aria-modal="true"
            aria-label="命令面板"
            data-testid="command-palette"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="nm-command__input">
              <Icon name="search" size={16} />
              <input autoFocus placeholder="搜索命令、作品或章节" aria-label="搜索命令" />
              <span className="nm-kbd">Esc</span>
            </div>
            <div className="nm-command__list">
              {commands.map((command) => (
                <button
                  key={command.id}
                  type="button"
                  className="nm-command__item"
                  onClick={() => runCommand(command)}
                >
                  <span className="nm-command__icon">
                    <Icon name={command.icon} size={16} />
                  </span>
                  <span className="nm-command__copy">
                    <span>{command.label}</span>
                    <span className="nm-caption nm-tertiary">{command.hint}</span>
                  </span>
                  <Icon name="chevron-right" size={14} />
                </button>
              ))}
            </div>
            <div className="nm-command__foot">
              <span>
                <span className="nm-kbd">↑</span>
                <span className="nm-kbd">↓</span> 选择
              </span>
              <span>
                <span className="nm-kbd">Enter</span> 执行
              </span>
              <span>
                <span className="nm-kbd">Esc</span> 关闭
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
