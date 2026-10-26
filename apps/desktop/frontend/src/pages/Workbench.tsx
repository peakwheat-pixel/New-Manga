import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ChangeEvent,
  type CSSProperties,
  type KeyboardEvent,
} from "react";
import { Icon, type IconName } from "../components/Icon";
import { PrimaryNav } from "../components/PrimaryNav";
import { PagePlaceholder } from "../components/PagePlaceholder";
import { StatusMark, type StatusState } from "../components/StatusMark";
import { useAcrylicBudget } from "../design/useAcrylicBudget";
import type { DesignPage, Theme } from "../design/types";
import type { ChapterNavSummary, PageNavSummary } from "../library/types";
import type { RegionOrigin, RegionSummary, RegionType } from "../region/types";
import { PageBlocked, PageEmpty, PageError, PageLoading } from "../ui/PageState";
import type { PageRuntime } from "../ui/types";
import {
  isSafeUiId,
  newIdempotencyKey,
  safeWorkbenchErrorCode,
  type RunSnapshot,
  type TaskProjection,
} from "../workbench/client";
import "./workbench.css";

/*
 * 工作台页有两副面孔，按 `runtime` 是否存在严格分流：
 *
 *   - 无 `runtime`：`?view=design` 的 v2 静态骨架，固定 fixtures（18 页、
 *     10 段流水线、示例区域）。这是冻结的视觉基线，不得因为接真实数据而退化。
 *   - 有 `runtime`：`UiRoot` 注入的运行时。本文件只经 `runtime.clients` 取
 *     Library / Region / ResourceChannel / Workbench 的真实 IPC 数据，经
 *     `runtime.chrome` 做导航与主题；**任何 fixtures 里的数字/文案都不许回填**
 *     ——没有 IPC 来源的字段显示「未识别」「—」或直接省略。
 *
 * 设计规则（冻结）：圆角只用 8/4/2/0，字号只用 28/20/14/12，间距只走
 * `var(--nm-space-*)`，颜色/描边/状态色只走 `var(--nm-*)`，不用 emoji，七态一律
 * 用 `StatusMark`（颜色 + 符号 + 文字）。
 */

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

interface RailEntry {
  id: string;
  label: string;
  icon: IconName;
}

const RAIL: RailEntry[] = [
  { id: "layers", label: "图层", icon: "layers" },
  { id: "text", label: "文本", icon: "type" },
  { id: "image", label: "图像", icon: "image" },
  { id: "repair", label: "修复", icon: "wand" },
  { id: "export", label: "导出", icon: "export" },
];

function stageColor(state: StatusState): string {
  return state === "notStarted" ? "var(--nm-status-skipped)" : `var(--nm-status-${state})`;
}

/* -------------------------------------------------------------------------
 * 两副面孔共用的框架件（标题栏 / 检查器导航轨道）
 * ---------------------------------------------------------------------- */

interface WorkbenchTitlebarProps {
  activePage: DesignPage;
  onNavigate: (page: DesignPage) => void;
  /** 运行时由 `chrome.onOpenCommand` 提供；设计预览不传（保持骨架原样）。 */
  onOpenCommand?: () => void;
  commandOpen?: boolean;
}

function WorkbenchTitlebar({
  activePage,
  onNavigate,
  onOpenCommand,
  commandOpen = false,
}: WorkbenchTitlebarProps) {
  return (
    <header className="nm-titlebar" data-testid="workbench-titlebar">
      <div className="nm-titlebar__brand">
        <span className="nm-brand-mark" aria-hidden="true">
          NM
        </span>
        <span className="nm-brand-name">New Manga</span>
      </div>
      <PrimaryNav activePage={activePage} onNavigate={onNavigate} />
      <div className="nm-titlebar__actions" style={{ justifyContent: "flex-end" }}>
        {onOpenCommand ? (
          <button
            type="button"
            className="nm-command-trigger"
            data-testid="workbench-command-trigger"
            onClick={onOpenCommand}
            aria-haspopup="dialog"
            aria-expanded={commandOpen}
          >
            <Icon name="search" size={14} />
            <span>搜索或执行命令</span>
            <span className="nm-command-trigger__keys">
              <kbd className="nm-kbd">Ctrl</kbd>
              <kbd className="nm-kbd">K</kbd>
            </span>
          </button>
        ) : null}
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
  );
}

interface InspectorRailProps {
  activeRail: string;
  onSelectRail: (id: string) => void;
  theme: Theme;
  onToggleTheme: () => void;
  onOpenSettings?: () => void;
}

function InspectorRail({
  activeRail,
  onSelectRail,
  theme,
  onToggleTheme,
  onOpenSettings,
}: InspectorRailProps) {
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
    onSelectRail(target.id);
    railRefs.current[target.id]?.focus();
  };

  return (
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
            onClick={() => onSelectRail(item.id)}
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
      <button
        type="button"
        className="nm-rail-btn"
        aria-label="设置"
        title="设置"
        onClick={onOpenSettings}
      >
        <Icon name="settings" size={17} />
      </button>
    </div>
  );
}

/* -------------------------------------------------------------------------
 * 设计预览（无 runtime）：冻结的 v2 静态骨架
 * ---------------------------------------------------------------------- */

interface DesignWorkbenchProps {
  theme: Theme;
  onNavigate: (page: DesignPage) => void;
  onToggleTheme: () => void;
}

function DesignWorkbench({ theme, onNavigate, onToggleTheme }: DesignWorkbenchProps) {
  const [selectedPage, setSelectedPage] = useState(12);
  const [activeRail, setActiveRail] = useState(RAIL[0].id);
  const budget = useAcrylicBudget("workbench-inspector", ["workbench-inspector"]);

  return (
    <div className="nm-workbench nm-mica" data-testid="page-workbench">
      <WorkbenchTitlebar
        activePage="workbench"
        onNavigate={onNavigate}
      />
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
          <InspectorRail
            activeRail={activeRail}
            onSelectRail={setActiveRail}
            theme={theme}
            onToggleTheme={onToggleTheme}
          />

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

/* -------------------------------------------------------------------------
 * 运行时（有 runtime）：真实 IPC 数据
 * ---------------------------------------------------------------------- */

/** 取数四态；与 `ui/PageState` 的四个状态面一一对应。 */
type Phase = "loading" | "ready" | "empty" | "error";

const STATUS_STATE: Record<string, StatusState> = {
  queued: "queued",
  waiting: "queued",
  pending: "queued",
  created: "notStarted",
  not_started: "notStarted",
  running: "running",
  processing: "running",
  in_progress: "running",
  completed: "done",
  done: "done",
  succeeded: "done",
  failed: "failed",
  error: "failed",
  blocked: "blocked",
  paused: "blocked",
  skipped: "skipped",
  cancelled: "skipped",
  canceled: "skipped",
  stale: "stale",
};

/** Core 的字符串状态 → StatusMark 的七态（纯展示映射，不做决策）。 */
function toStatusState(raw: string | null | undefined): StatusState {
  if (!raw) return "notStarted";
  return STATUS_STATE[raw.toLowerCase()] ?? "queued";
}

const REGION_TYPE_LABEL: Record<RegionType, string> = {
  speech: "对白",
  narration: "旁白",
  sfx: "拟声",
  title: "标题",
  note: "备注",
  other: "其他",
};

/** 区域类型只映射到已冻结的 `--nm-*` 颜色，不写任何字面色值。 */
const REGION_TYPE_TONE: Record<RegionType, string> = {
  speech: "var(--nm-accent-base)",
  narration: "var(--nm-status-stale)",
  sfx: "var(--nm-status-blocked)",
  title: "var(--nm-status-done)",
  note: "var(--nm-status-skipped)",
  other: "var(--nm-status-queued)",
};

const ORIGIN_LABEL: Record<RegionOrigin, string> = {
  machine: "机器",
  user: "人工",
  imported: "导入",
  restored: "恢复",
};

function chapterLabel(chapter: ChapterNavSummary, index: number): string {
  const number = chapter.chapter_number.trim();
  const head = number.length > 0 ? `第 ${number} 话` : `第 ${index + 1} 话`;
  const title = chapter.title.trim();
  return title.length > 0 ? `${head} · ${title}` : head;
}

interface RuntimeWorkbenchProps {
  runtime: PageRuntime;
}

/**
 * v2 运行时工作台：章节 → 页面 → 资源通道页图 + 区域 + 运行投影。
 *
 * 数据纪律：这里出现的每个数字/标题都来自 IPC；没有来源的一律不渲染。
 * 例如页缩略图（Core 没有缩略图通道）只画未知占位，OCR 文本与置信度显示
 * 「未识别 / —」，流水线阶段用 `TaskProjection.step_flow` 而不是设计稿的十段。
 */
function RuntimeWorkbench({ runtime }: RuntimeWorkbenchProps) {
  const { chrome, clients } = runtime;
  const { library, region: regionClient, resource, workbench } = clients;
  const bookId = chrome.context.bookId;
  const contextChapterId = chrome.context.chapterId;
  const commandOpen = chrome.commandOpen === true;

  /*
   * 亚克力预算：命令面板是运行时根渲染的模态层（`.nm-acrylic-strong`）。
   * 它打开时页面只保留模态层，检查器这层低优先级亚克力必须降级
   * `.nm-acrylic-off`；关闭时检查器恢复 `.nm-acrylic`。任何时刻同屏
   * backdrop-filter 层都不超过 2。
   */
  const acrylicLayers = commandOpen
    ? ["global-command-layer", "workbench-inspector"]
    : ["workbench-inspector"];
  const budget = useAcrylicBudget(
    commandOpen ? "global-command-layer" : "workbench-inspector",
    acrylicLayers,
    commandOpen ? 1 : 2,
  );

  const [activeRail, setActiveRail] = useState(RAIL[0].id);

  // ---- 章节 ----
  const [chapters, setChapters] = useState<ChapterNavSummary[]>([]);
  const [chaptersPhase, setChaptersPhase] = useState<Phase>(bookId ? "loading" : "empty");
  const [chaptersError, setChaptersError] = useState<string | null>(null);
  const [chaptersRetry, setChaptersRetry] = useState(0);
  const [selectedChapterId, setSelectedChapterId] = useState<string | null>(contextChapterId);

  // ---- 页面列表 ----
  const [pages, setPages] = useState<PageNavSummary[]>([]);
  const [pagesPhase, setPagesPhase] = useState<Phase>("empty");
  const [pagesError, setPagesError] = useState<string | null>(null);
  const [pagesRetry, setPagesRetry] = useState(0);
  const [selectedPageId, setSelectedPageId] = useState<string | null>(null);

  // ---- 页图（资源通道） ----
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [imagePhase, setImagePhase] = useState<Phase>("empty");
  const [imageError, setImageError] = useState<string | null>(null);
  const [imageProgress, setImageProgress] = useState<{ loaded: number; total: number } | null>(null);
  const [imageRetry, setImageRetry] = useState(0);
  const [zoom, setZoom] = useState(100);
  const currentUrlRef = useRef<string | null>(null);

  // ---- 区域 ----
  const [regions, setRegions] = useState<RegionSummary[]>([]);
  const [regionsPhase, setRegionsPhase] = useState<Phase>("empty");
  const [regionsError, setRegionsError] = useState<string | null>(null);
  const [regionsRetry, setRegionsRetry] = useState(0);

  // ---- 运行（页面内 state；chrome 不提供 run 控制） ----
  const [runId, setRunId] = useState<string | null>(null);
  const [runSnapshot, setRunSnapshot] = useState<RunSnapshot | null>(null);
  const [projection, setProjection] = useState<TaskProjection | null>(null);
  const [runPhase, setRunPhase] = useState<Phase>("empty");
  const [runError, setRunError] = useState<string | null>(null);
  const [runBusy, setRunBusy] = useState(false);
  const runIdRef = useRef<string | null>(null);
  const runReadRef = useRef(false);

  const replaceImageUrl = useCallback((next: string | null) => {
    const previous = currentUrlRef.current;
    currentUrlRef.current = next;
    setImageUrl(next);
    if (previous && previous !== next) URL.revokeObjectURL(previous);
  }, []);

  // 上下文换章时同步页面选择（UiRoot 的 NavContext 是章入口的唯一来源）。
  useEffect(() => {
    setSelectedChapterId(contextChapterId);
  }, [contextChapterId, bookId]);

  // 章节列表：真实 list_chapters 投影。
  useEffect(() => {
    if (!bookId) {
      setChapters([]);
      setChaptersPhase("empty");
      setChaptersError(null);
      return;
    }
    let cancelled = false;
    setChaptersPhase("loading");
    setChaptersError(null);
    library
      .listChapters(bookId)
      .then((rows) => {
        if (cancelled) return;
        const safe = rows.filter((row) => isSafeUiId(row.chapter_id));
        if (safe.length !== rows.length) {
          setChapters([]);
          setChaptersPhase("error");
          setChaptersError("PAGE_NAV_MALFORMED");
          return;
        }
        setChapters(safe);
        setChaptersPhase(safe.length === 0 ? "empty" : "ready");
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        setChapters([]);
        setChaptersPhase("error");
        setChaptersError(safeWorkbenchErrorCode(error, "LIBRARY_UNAVAILABLE"));
      });
    return () => {
      cancelled = true;
    };
  }, [bookId, chaptersRetry, library]);

  // 上下文没给章（或给的章已不存在）时取第一章；不写回全局上下文。
  useEffect(() => {
    if (chaptersPhase !== "ready") return;
    setSelectedChapterId((current) =>
      current && chapters.some((chapter) => chapter.chapter_id === current)
        ? current
        : (chapters[0]?.chapter_id ?? null),
    );
  }, [chapters, chaptersPhase]);

  // 页面列表：真实 list_chapter_pages 投影（已按 sort_order 升序）。
  useEffect(() => {
    if (!selectedChapterId) {
      setPages([]);
      setPagesPhase("empty");
      setPagesError(null);
      setSelectedPageId(null);
      return;
    }
    let cancelled = false;
    setPages([]);
    setPagesPhase("loading");
    setPagesError(null);
    setSelectedPageId(null);
    library
      .listChapterPages(selectedChapterId)
      .then((rows) => {
        if (cancelled) return;
        const safe = rows.filter((row) => isSafeUiId(row.page_id));
        if (safe.length !== rows.length) {
          setPagesPhase("error");
          setPagesError("PAGE_NAV_MALFORMED");
          return;
        }
        setPages(safe);
        setPagesPhase(safe.length === 0 ? "empty" : "ready");
        setSelectedPageId(safe[0]?.page_id ?? null);
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        setPages([]);
        setPagesPhase("error");
        setPagesError(safeWorkbenchErrorCode(error, "PAGE_NAV_UNAVAILABLE"));
      });
    return () => {
      cancelled = true;
    };
  }, [selectedChapterId, pagesRetry, library]);

  // 页图：resolve_page_resource → resource channel issue → fetchAll → Blob URL。
  // 每次切换页/卸载都 revoke，绝不复用旧 opaque 引用。
  useEffect(() => {
    if (!selectedPageId) {
      replaceImageUrl(null);
      setImagePhase("empty");
      setImageError(null);
      setImageProgress(null);
      return;
    }
    let cancelled = false;
    let createdUrl: string | null = null;
    setImagePhase("loading");
    setImageError(null);
    setImageProgress(null);
    replaceImageUrl(null);
    const load = async () => {
      const resolved = await library.resolvePageResource(selectedPageId);
      if (cancelled) return;
      if (!isSafeUiId(resolved.resource_id) || !isSafeUiId(resolved.revision)) {
        throw { code: "PAGE_RESOURCE_MALFORMED" };
      }
      const issued = await resource.issue(resolved.resource_id, resolved.revision);
      if (cancelled) return;
      const blob = await resource.fetchAll(issued.url, issued.size, undefined, (loaded, total) => {
        if (!cancelled) setImageProgress({ loaded, total });
      });
      if (cancelled) return;
      const url = URL.createObjectURL(blob);
      createdUrl = url;
      replaceImageUrl(url);
      setImagePhase("ready");
      setImageProgress(null);
    };
    void load().catch((error: unknown) => {
      if (cancelled) return;
      replaceImageUrl(null);
      setImagePhase("error");
      setImageError(safeWorkbenchErrorCode(error, "RESOURCE_UNAVAILABLE"));
      setImageProgress(null);
    });
    return () => {
      cancelled = true;
      if (createdUrl) {
        URL.revokeObjectURL(createdUrl);
        if (currentUrlRef.current === createdUrl) currentUrlRef.current = null;
      }
    };
  }, [selectedPageId, imageRetry, library, resource, replaceImageUrl]);

  // 区域：真实 list_regions 投影。
  useEffect(() => {
    if (!selectedPageId) {
      setRegions([]);
      setRegionsPhase("empty");
      setRegionsError(null);
      return;
    }
    let cancelled = false;
    setRegions([]);
    setRegionsPhase("loading");
    setRegionsError(null);
    regionClient
      .listRegions(selectedPageId)
      .then((result) => {
        if (cancelled) return;
        const safe = result.regions.filter((row) => isSafeUiId(row.region_id));
        setRegions(safe);
        setRegionsPhase(safe.length === 0 ? "empty" : "ready");
      })
      .catch((error: unknown) => {
        if (cancelled) return;
        setRegions([]);
        setRegionsPhase("error");
        setRegionsError(safeWorkbenchErrorCode(error, "REGION_CHANNEL_UNAVAILABLE"));
      });
    return () => {
      cancelled = true;
    };
  }, [selectedPageId, regionsRetry, regionClient]);

  // 组件卸载时兜底回收当前 Blob URL。
  useEffect(
    () => () => {
      const url = currentUrlRef.current;
      currentUrlRef.current = null;
      if (url) URL.revokeObjectURL(url);
    },
    [],
  );

  useEffect(() => {
    runIdRef.current = runId;
  }, [runId]);

  // 换章后旧 Run 的归属已不成立；Core 没有 ListRuns 反查，只能回到「尚未运行」。
  useEffect(() => {
    setRunId(null);
    setRunSnapshot(null);
    setProjection(null);
    setRunPhase("empty");
    setRunError(null);
    setRunBusy(false);
  }, [selectedChapterId]);

  const refreshRun = useCallback(
    async (id: string) => {
      if (runReadRef.current) return;
      runReadRef.current = true;
      try {
        const [snapshot, taskProjection] = await Promise.all([
          workbench.getRunSnapshot(id),
          workbench.getTaskProjection(id),
        ]);
        if (snapshot.run_id !== id || taskProjection.run_id !== id) {
          if (runIdRef.current === id) {
            setRunError("WORKBENCH_RESPONSE_MALFORMED");
            setRunPhase("error");
          }
          return;
        }
        if (runIdRef.current !== id) return;
        setRunSnapshot(snapshot);
        setProjection(taskProjection);
        setRunError(null);
        setRunPhase("ready");
      } catch (error: unknown) {
        if (runIdRef.current !== id) return;
        setRunError(safeWorkbenchErrorCode(error, "CORE_UNAVAILABLE"));
        setRunPhase("error");
      } finally {
        runReadRef.current = false;
      }
    },
    [workbench],
  );

  const startRun = useCallback(async () => {
    if (!selectedChapterId || runBusy) return;
    setRunBusy(true);
    setRunPhase("loading");
    setRunError(null);
    try {
      const accepted = await workbench.startRun(
        "translate_untranslated",
        { kind: "chapter", chapter_id: selectedChapterId },
        newIdempotencyKey(),
      );
      runIdRef.current = accepted.run_id;
      setRunId(accepted.run_id);
      setRunSnapshot(null);
      setProjection(null);
      await refreshRun(accepted.run_id);
    } catch (error: unknown) {
      setRunPhase("error");
      setRunError(safeWorkbenchErrorCode(error, "CORE_UNAVAILABLE"));
    } finally {
      setRunBusy(false);
    }
  }, [refreshRun, runBusy, selectedChapterId, workbench]);

  const retryRun = useCallback(() => {
    if (runIdRef.current) void refreshRun(runIdRef.current);
    else void startRun();
  }, [refreshRun, startRun]);

  const runStatus = projection?.run_status ?? runSnapshot?.status ?? null;
  // runStatus 为 null 表示刚提交、投影还没到手：继续轮询，避免一次竞态把 UI
  // 卡在「正在读取运行状态」。
  const runPolling =
    runId !== null &&
    runError === null &&
    (runStatus === null || runStatus === "pending" || runStatus === "running");
  useEffect(() => {
    if (!runPolling || !runId) return;
    const timer = window.setInterval(() => {
      void refreshRun(runId);
    }, 1000);
    return () => {
      window.clearInterval(timer);
    };
  }, [runId, runPolling, refreshRun]);

  const onChapterChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const next = event.target.value;
    if (!next || !bookId) return;
    setSelectedChapterId(next);
    setSelectedPageId(null);
    chrome.onSelectChapter(bookId, next);
  };

  const onSelectPage = (pageId: string) => {
    setSelectedPageId(pageId);
    setZoom(100);
  };

  const chapterIndex = chapters.findIndex((chapter) => chapter.chapter_id === selectedChapterId);
  const selectedChapter = chapterIndex >= 0 ? chapters[chapterIndex] : null;
  const pageIndex = pages.findIndex((page) => page.page_id === selectedPageId);
  const selectedPage = pageIndex >= 0 ? pages[pageIndex] : null;
  const pageNumber = pageIndex >= 0 ? pageIndex + 1 : null;
  const percent = projection
    ? Math.round(Math.max(0, Math.min(1, projection.overall_progress)) * 100)
    : null;
  const detailStatus: StatusState =
    runPhase === "empty"
      ? "notStarted"
      : runPhase === "loading"
        ? "running"
        : runPhase === "error"
          ? "failed"
          : toStatusState(runStatus);

  const backToShelf = (
    <button
      type="button"
      className="nm-btn nm-btn--primary"
      data-testid="workbench-back-to-shelf"
      onClick={() => chrome.onNavigate("shelf")}
    >
      <Icon name="book" size={14} />
      返回书架
    </button>
  );

  // ---- 页面级状态面（没有作品 / 章节读不出来） ----
  if (!bookId) {
    return (
      <div className="nm-workbench nm-mica" data-testid="page-workbench">
        <WorkbenchTitlebar
          activePage={chrome.activePage}
          onNavigate={chrome.onNavigate}
          onOpenCommand={chrome.onOpenCommand}
          commandOpen={commandOpen}
        />
        <div className="nm-workbench__body nm-workbench__body--state">
          <PageEmpty
            icon="book"
            title="先在书架选择作品"
            description="工作台需要一部作品与章节作为上下文；回到书架选择作品后再进入。"
            action={backToShelf}
            testId="workbench-no-book"
          />
        </div>
      </div>
    );
  }

  if (chaptersPhase === "loading") {
    return (
      <div className="nm-workbench nm-mica" data-testid="page-workbench">
        <WorkbenchTitlebar
          activePage={chrome.activePage}
          onNavigate={chrome.onNavigate}
          onOpenCommand={chrome.onOpenCommand}
          commandOpen={commandOpen}
        />
        <div className="nm-workbench__body nm-workbench__body--state">
          <PageLoading label="正在读取章节" detail="读取该作品的章节列表" testId="workbench-chapters-loading" />
        </div>
      </div>
    );
  }

  if (chaptersPhase === "error") {
    return (
      <div className="nm-workbench nm-mica" data-testid="page-workbench">
        <WorkbenchTitlebar
          activePage={chrome.activePage}
          onNavigate={chrome.onNavigate}
          onOpenCommand={chrome.onOpenCommand}
          commandOpen={commandOpen}
        />
        <div className="nm-workbench__body nm-workbench__body--state">
          <PageError
            title="章节读取失败"
            message="无法从 Core 读取该作品的章节列表。"
            code={chaptersError ?? undefined}
            retryable
            onRetry={() => setChaptersRetry((value) => value + 1)}
            testId="workbench-chapters-error"
          />
        </div>
      </div>
    );
  }

  if (chaptersPhase === "empty") {
    return (
      <div className="nm-workbench nm-mica" data-testid="page-workbench">
        <WorkbenchTitlebar
          activePage={chrome.activePage}
          onNavigate={chrome.onNavigate}
          onOpenCommand={chrome.onOpenCommand}
          commandOpen={commandOpen}
        />
        <div className="nm-workbench__body nm-workbench__body--state">
          <PageEmpty
            icon="layers"
            title="这本书还没有章节"
            description="先导入漫画页面，再回到工作台开始流水线。"
            action={backToShelf}
            testId="workbench-chapters-empty"
          />
        </div>
      </div>
    );
  }

  const stepFlow = projection?.step_flow ?? [];

  return (
    <div className="nm-workbench nm-mica" data-testid="page-workbench">
      <WorkbenchTitlebar
        activePage={chrome.activePage}
        onNavigate={chrome.onNavigate}
        onOpenCommand={chrome.onOpenCommand}
        commandOpen={commandOpen}
      />

      <div className="nm-workbench__body">
        <aside className="nm-filmstrip" data-testid="filmstrip" aria-label="胶片条">
          <button
            type="button"
            className="nm-filmstrip__back"
            onClick={() => chrome.onNavigate("shelf")}
            aria-label="返回书架"
            title="返回书架"
          >
            <Icon name="chevron-left" size={16} />
          </button>
          <div className="nm-filmstrip__list">
            {pages.map((page, index) => {
              const active = page.page_id === selectedPageId;
              return (
                <button
                  key={page.page_id}
                  type="button"
                  className="nm-filmstrip__item"
                  data-active={active}
                  aria-pressed={active}
                  aria-label={`第 ${index + 1} 页`}
                  onClick={() => onSelectPage(page.page_id)}
                >
                  {/* Core 没有缩略图通道：这里只画未知占位，不用设计稿图案冒充页面。 */}
                  <span
                    className="nm-filmstrip__thumb nm-wb-thumb--unknown"
                    aria-hidden="true"
                    data-testid="workbench-thumb-unknown"
                  />
                  <span className="nm-filmstrip__no">{String(index + 1).padStart(3, "0")}</span>
                </button>
              );
            })}
          </div>
        </aside>

        <main className="nm-canvas" data-testid="workbench-canvas">
          <div className="nm-canvas__bar">
            <button type="button" className="nm-btn nm-btn--ghost" onClick={() => chrome.onNavigate("shelf")}>
              <Icon name="chevron-left" size={14} />
              书架
            </button>
            <span className="nm-divider" aria-hidden="true" />
            <span className="nm-canvas__crumb">
              <span className="nm-truncate">
                {selectedChapter ? chapterLabel(selectedChapter, chapterIndex) : "未选择章节"}
              </span>
              {pageNumber !== null ? (
                <>
                  <Icon name="chevron-right" size={12} />
                  <span className="nm-truncate">
                    第 {pageNumber} / {pages.length} 页
                  </span>
                </>
              ) : null}
            </span>
            <label className="nm-select-wrap nm-wb-chapter">
              <span className="nm-sr-only">切换章节</span>
              <select
                className="nm-select"
                value={selectedChapterId ?? ""}
                onChange={onChapterChange}
                aria-label="切换章节"
                data-testid="workbench-chapter-select"
              >
                {chapters.map((chapter, index) => (
                  <option key={chapter.chapter_id} value={chapter.chapter_id}>
                    {chapterLabel(chapter, index)}
                  </option>
                ))}
              </select>
              <Icon name="chevron-down" size={13} />
            </label>
            <span className="nm-canvas__bar-spacer" />
            <StatusMark state={detailStatus} />
            <button
              type="button"
              className="nm-btn nm-btn--ghost nm-btn--icon"
              aria-label={chrome.theme === "dark" ? "切换到浅色主题" : "切换到深色主题"}
              onClick={chrome.onToggleTheme}
            >
              <Icon name={chrome.theme === "dark" ? "sun" : "moon"} size={15} />
            </button>
            <button type="button" className="nm-btn" onClick={() => chrome.onNavigate("reader")}>
              <Icon name="reader" size={14} />
              阅读器
            </button>
          </div>

          <div className="nm-canvas__stage" data-testid="canvas-stage">
            {pagesPhase === "loading" ? (
              <PageLoading
                label="正在读取页面列表"
                detail="读取该章节的页面"
                skeletonRows={0}
                testId="workbench-pages-loading"
              />
            ) : null}
            {pagesPhase === "error" ? (
              <PageError
                title="页面列表读取失败"
                message="无法从 Core 读取该章节的页面。"
                code={pagesError ?? undefined}
                retryable
                onRetry={() => setPagesRetry((value) => value + 1)}
                testId="workbench-pages-error"
              />
            ) : null}
            {pagesPhase === "empty" ? (
              <PageEmpty
                icon="image"
                title="本章还没有页面"
                description="导入页面后，这里会按 Core 的排序显示真实页序。"
                testId="workbench-pages-empty"
              />
            ) : null}
            {pagesPhase === "ready" && imagePhase === "loading" ? (
              <PageLoading
                label="正在加载页面图像"
                detail={
                  imageProgress
                    ? `已读取 ${imageProgress.loaded} / ${imageProgress.total} 个分块`
                    : undefined
                }
                skeletonRows={0}
                testId="workbench-image-loading"
              />
            ) : null}
            {pagesPhase === "ready" && imagePhase === "error" ? (
              <PageError
                title="页面图像加载失败"
                message="资源通道未能返回该页图像。"
                code={imageError ?? undefined}
                retryable
                onRetry={() => setImageRetry((value) => value + 1)}
                testId="workbench-image-error"
              />
            ) : null}
            {pagesPhase === "ready" && imagePhase === "empty" ? (
              <PageEmpty
                icon="image"
                title="请选择页面"
                description="从左侧胶片条选择一页。"
                testId="workbench-image-empty"
              />
            ) : null}
            {pagesPhase === "ready" && imagePhase === "ready" && imageUrl ? (
              <img
                className="nm-wb-page-img"
                src={imageUrl}
                alt={pageNumber !== null ? `第 ${pageNumber} 页` : "页面图像"}
                data-testid="workbench-page-image"
                style={{ transform: `scale(${zoom / 100})` }}
              />
            ) : null}
          </div>

          {imagePhase === "ready" ? (
            <div className="nm-canvas__tools" aria-label="缩放">
              <button
                type="button"
                className="nm-btn nm-btn--ghost nm-btn--icon"
                aria-label="缩小"
                disabled={zoom <= 50}
                onClick={() => setZoom((value) => Math.max(50, value - 25))}
              >
                <Icon name="zoom-out" size={14} />
              </button>
              <span className="nm-data">{zoom}%</span>
              <button
                type="button"
                className="nm-btn nm-btn--ghost nm-btn--icon"
                aria-label="放大"
                disabled={zoom >= 200}
                onClick={() => setZoom((value) => Math.min(200, value + 25))}
              >
                <Icon name="zoom-in" size={14} />
              </button>
              <span className="nm-divider" aria-hidden="true" />
              <button
                type="button"
                className="nm-btn nm-btn--ghost nm-btn--icon"
                aria-label="适配窗口"
                onClick={() => setZoom(100)}
              >
                <Icon name="maximize" size={13} />
              </button>
            </div>
          ) : null}
        </main>

        <aside
          className={`nm-inspector ${budget.className("workbench-inspector", "acrylic")}`}
          data-testid="inspector"
          aria-label="检查器"
        >
          <InspectorRail
            activeRail={activeRail}
            onSelectRail={setActiveRail}
            theme={chrome.theme}
            onToggleTheme={chrome.onToggleTheme}
            onOpenSettings={() => chrome.onNavigate("settings")}
          />

          <div className="nm-inspector__panel">
            <div className="nm-inspector__head">
              <div>
                <div className="nm-body-strong">检查器</div>
                <div className="nm-caption nm-tertiary">
                  {selectedPage
                    ? `第 ${pageNumber ?? "—"} 页 · ${selectedPage.source_filename}`
                    : "未选择页面"}
                </div>
              </div>
            </div>

            <div className="nm-inspector__status" data-testid="workbench-run-status">
              <StatusMark state={detailStatus} />
              <span className="nm-caption nm-tertiary">
                {runId ? `Run ${runId}` : "尚未开始运行"}
              </span>
            </div>

            <section className="nm-inspector__section" data-testid="inspector-ocr">
              <div className="nm-inspector__section-head">
                <span className="nm-body-strong">识别结果</span>
                <span className="nm-data nm-tertiary">—</span>
              </div>
              <div className="nm-ocr-box">
                <p>未识别</p>
                <span className="nm-ocr-box__meta nm-data">
                  当前 IPC 未返回 OCR 文本与置信度
                </span>
              </div>
            </section>

            <section className="nm-inspector__section" data-testid="inspector-regions">
              <div className="nm-inspector__section-head">
                <span className="nm-body-strong">区域</span>
                {regionsPhase === "ready" ? (
                  <span className="nm-data nm-tertiary">{regions.length}</span>
                ) : null}
              </div>
              {regionsPhase === "loading" ? (
                <PageLoading
                  label="正在读取区域"
                  skeletonRows={2}
                  testId="workbench-regions-loading"
                />
              ) : null}
              {regionsPhase === "error" ? (
                <PageError
                  title="区域读取失败"
                  message="Core 未能返回该页的区域投影。"
                  code={regionsError ?? undefined}
                  retryable
                  onRetry={() => setRegionsRetry((value) => value + 1)}
                  testId="workbench-regions-error"
                />
              ) : null}
              {selectedPageId === null && regionsPhase === "empty" ? (
                <p className="nm-caption nm-tertiary">未选择页面</p>
              ) : null}
              {selectedPageId !== null && regionsPhase === "empty" ? (
                <PageEmpty
                  icon="layers"
                  title="本页没有区域"
                  description="识别完成后，这里会列出 Core 返回的真实区域。"
                  testId="workbench-regions-empty"
                />
              ) : null}
              {regionsPhase === "ready" ? (
                <ul className="nm-region-list" data-testid="workbench-region-list">
                  {regions.map((row, index) => (
                    <li key={row.region_id}>
                      <div className="nm-region">
                        <span
                          className="nm-region__tone"
                          style={
                            { "--region-tone": REGION_TYPE_TONE[row.region_type] } as CSSProperties
                          }
                          aria-hidden="true"
                        />
                        <span className="nm-region__copy">
                          <span className="nm-region__label">
                            {REGION_TYPE_LABEL[row.region_type]} {index + 1}
                          </span>
                          {/* OCR 文本没有 IPC 来源：显示「未识别」而不是编台词。 */}
                          <span className="nm-region__text nm-truncate">未识别</span>
                        </span>
                        <span className="nm-data nm-tertiary">
                          r{row.revision_no} · {ORIGIN_LABEL[row.origin]}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : null}
            </section>

            <section className="nm-inspector__section" data-testid="inspector-run">
              <div className="nm-inspector__section-head">
                <span className="nm-body-strong">运行</span>
                {runPhase === "ready" && runStatus ? (
                  <StatusMark state={toStatusState(runStatus)} />
                ) : null}
              </div>

              {runPhase === "empty" ? (
                <PageBlocked
                  title="尚未开始运行"
                  message="本章还没有运行记录；点击「运行」开始翻译流水线。"
                  testId="workbench-run-blocked"
                />
              ) : null}
              {runPhase === "loading" ? (
                <PageLoading
                  label="正在读取运行状态"
                  skeletonRows={0}
                  testId="workbench-run-loading"
                />
              ) : null}
              {runPhase === "error" ? (
                <PageError
                  title="运行状态读取失败"
                  message="Core 未能返回本次运行的有效投影。"
                  code={runError ?? undefined}
                  retryable
                  onRetry={retryRun}
                  testId="workbench-run-error"
                />
              ) : null}

              {runPhase === "ready" && projection ? (
                <div className="nm-wb-run" data-testid="workbench-run-detail">
                  <dl className="nm-kv">
                    <div>
                      <dt>整体进度</dt>
                      <dd className="nm-data">{percent !== null ? `${percent}%` : "—"}</dd>
                    </div>
                    <div>
                      <dt>任务总数</dt>
                      <dd className="nm-data">{projection.counts.total}</dd>
                    </div>
                    <div>
                      <dt>已完成</dt>
                      <dd className="nm-data">{projection.counts.completed}</dd>
                    </div>
                    <div>
                      <dt>失败</dt>
                      <dd className="nm-data">{projection.counts.failed}</dd>
                    </div>
                    <div>
                      <dt>阻塞</dt>
                      <dd className="nm-data">{projection.counts.blocked}</dd>
                    </div>
                  </dl>
                  <div className="nm-progress" aria-hidden="true">
                    <span style={{ width: `${percent ?? 0}%` }} />
                  </div>
                  {projection.blocked_reasons.length > 0 ? (
                    <ul className="nm-wb-run__reasons" aria-label="阻塞原因">
                      {projection.blocked_reasons.map((reason, index) => (
                        <li key={index} className="nm-wb-reason">
                          {reason}
                        </li>
                      ))}
                    </ul>
                  ) : null}
                  <ul className="nm-wb-task-list" data-testid="workbench-task-list">
                    {projection.tasks.slice(0, 8).map((task) => {
                      const row = projection.rows.find((item) => item.page_id === task.page_id);
                      return (
                        <li key={task.task_id} className="nm-wb-task">
                          <StatusMark state={toStatusState(task.status)} />
                          <span className="nm-wb-task__name nm-data nm-tertiary nm-truncate">
                            {row?.filename ?? task.page_id}
                          </span>
                        </li>
                      );
                    })}
                  </ul>
                  {projection.tasks.length > 8 ? (
                    <span className="nm-caption nm-tertiary">
                      另有 {projection.tasks.length - 8} 个任务未显示
                    </span>
                  ) : null}
                  {/* 流水线参数只渲染 IPC 真实返回的 provider/model/device。 */}
                  {(() => {
                    const allSteps = projection.tasks.flatMap((task) => task.steps);
                    const hasParams = (step: (typeof allSteps)[number]) =>
                      Boolean(step.provider || step.model || step.device);
                    const paramStep =
                      allSteps.find(
                        (step) =>
                          step.step_type === projection.current_step_type && hasParams(step),
                      ) ??
                      allSteps.find(hasParams) ??
                      null;
                    if (!paramStep) return null;
                    return (
                      <div data-testid="workbench-pipeline-params">
                        <div className="nm-caption nm-tertiary">
                          流水线参数 · {paramStep.step_type}
                        </div>
                        <dl className="nm-kv">
                          {paramStep.provider ? (
                            <div>
                              <dt>服务商</dt>
                              <dd>{paramStep.provider}</dd>
                            </div>
                          ) : null}
                          {paramStep.model ? (
                            <div>
                              <dt>模型</dt>
                              <dd>{paramStep.model}</dd>
                            </div>
                          ) : null}
                          {paramStep.device ? (
                            <div>
                              <dt>设备</dt>
                              <dd>{paramStep.device}</dd>
                            </div>
                          ) : null}
                        </dl>
                      </div>
                    );
                  })()}
                </div>
              ) : null}

              <div className="nm-inspector__actions">
                <button
                  type="button"
                  className="nm-btn nm-btn--primary"
                  data-testid="workbench-start-run"
                  disabled={runBusy || !selectedChapterId}
                  onClick={() => {
                    void startRun();
                  }}
                >
                  <Icon name="play" size={14} />
                  {runBusy ? "提交中…" : "运行"}
                </button>
              </div>
              <p className="nm-caption nm-tertiary" data-testid="workbench-run-command">
                本章 · 翻译未完成页（translate_untranslated）
              </p>
            </section>
          </div>
        </aside>
      </div>

      <footer className="nm-pipeline" data-testid="pipeline" aria-label="流水线">
        <div className="nm-pipeline__stages">
          {stepFlow.length > 0 ? (
            stepFlow.map((step, index) => {
              const state = toStatusState(step.state);
              return (
                <div
                  key={`${step.type}-${index}`}
                  className="nm-stage"
                  data-state={state}
                >
                  <StatusMark state={state} showLabel={false} />
                  <span className="nm-stage__label">{step.label}</span>
                </div>
              );
            })
          ) : (
            <div className="nm-stage" data-state="notStarted">
              <StatusMark state="notStarted" showLabel={false} />
              <span className="nm-stage__label">尚未开始运行</span>
            </div>
          )}
        </div>
        <div className="nm-pipeline__meter">
          {projection && percent !== null ? (
            <>
              <span className="nm-caption nm-tertiary">本话</span>
              <div className="nm-progress nm-pipeline__progress">
                <span style={{ width: `${percent}%` }} />
              </div>
              <span className="nm-data">{percent}%</span>
            </>
          ) : (
            <span className="nm-caption nm-tertiary">—</span>
          )}
        </div>
      </footer>
    </div>
  );
}

export interface WorkbenchProps {
  theme: Theme;
  onNavigate: (page: DesignPage) => void;
  onToggleTheme: () => void;
  /** 真实运行时注入；缺省为设计预览 fixtures。见 `ui/types.ts`。 */
  runtime?: PageRuntime;
}

/**
 * 工作台页入口：有 `runtime` 走真实 IPC，无 `runtime` 保持 v2 静态骨架。
 * 两副面孔是互斥的整页实现，不在同一棵树里混渲染，避免「半真半假」的字段。
 */
export function Workbench({ theme, onNavigate, onToggleTheme, runtime }: WorkbenchProps) {
  if (runtime) return <RuntimeWorkbench runtime={runtime} />;
  return <DesignWorkbench theme={theme} onNavigate={onNavigate} onToggleTheme={onToggleTheme} />;
}
