import { useEffect, useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import { Icon } from "../components/Icon";
import { PrimaryNav } from "../components/PrimaryNav";
import { StatusMark } from "../components/StatusMark";
import { useAcrylicBudget } from "../design/useAcrylicBudget";
import type { DesignPage, Theme } from "../design/types";
import { BackupSettingsPanel } from "../settings/BackupSettingsPanel";
import { CacheRevisionPanel } from "../settings/CacheRevisionPanel";
import { CapabilityBindingPanel } from "../settings/CapabilityBindingPanel";
import { InpaintSettingsPanel } from "../settings/InpaintSettingsPanel";
import { ModelGpuSettingsPanel } from "../settings/ModelGpuSettingsPanel";
import { NetworkProfilePanel } from "../settings/NetworkProfilePanel";
import { OcrSettingsPanel } from "../settings/OcrSettingsPanel";
import { PluginSettingsPanel } from "../settings/PluginSettingsPanel";
import { ProviderProfilePanel } from "../settings/ProviderProfilePanel";
import { RecycleBinSettingsPanel } from "../settings/RecycleBinSettingsPanel";
// 只复用分节顺序常量与 id 类型；不 import / 不渲染 SettingsPage 本体。
import { SETTINGS_CATEGORY_ORDER, type SettingsCategoryId } from "../settings/SettingsPage";
import { SfxPolicyControl } from "../settings/SfxPolicyControl";
import { TasksSettingsPanel } from "../settings/TasksSettingsPanel";
import { TranslationParamsPanel } from "../settings/TranslationParamsPanel";
import { TypesetSettingsPanel } from "../settings/TypesetSettingsPanel";
import { SFX_POLICY_LABELS, type SfxPolicy } from "../settings/types";
import { PageBlocked, PageError, PageLoading } from "../ui/PageState";
import type { PageRuntime } from "../ui/types";
import "./reader-settings.css";

/**
 * 设置页（v2 语言）。
 *
 * 骨架：v2 标题栏（品牌 + 一级导航 + 主题切换 + 窗口按钮）+ 左侧分节导航 +
 * 右侧内容带。分节清单复用既有设置页的冻结顺序（`SETTINGS_CATEGORY_ORDER`），
 * 12 个分节全部映射到既有 panel 组件——**不重写、不复制**任何 panel。
 *
 * 数据与人设边界：
 *   - 整页 readiness 走 `settings_get`（`SettingsClient.getSfxSection()` 读单个
 *     `sfx` 分节：JSON null = 未设置，是 Core 的冻结语义，页面不会替它编造
 *     一个"默认值"）。失败 → PageError + 错误码 + 重试。
 *   - 下发到各分节的 client 是 `runtime.clients.settings`；回收站分节是例外：
 *     它的真实数据源是 `library_list_recycle_bin_books`，所以传
 *     `runtime.clients.library`（panel 的 client 是窄接口，二者结构兼容）。
 *   - 没有任何 IPC 来源的字段一律不渲染，不用占位数值填充；静态设计预览
 *     （`?view=design`，无 runtime）逐分节显式标注"预览不展示任何设置值"。
 *
 * 亚克力预算：本页只声明一层（左侧分节导航）。命令面板打开时它是页面里的低
 * 优先级层，按硬规则降级为 `.nm-acrylic-off`（页面 0 层 + 模态 1 层，同屏永不
 * 超过 2 层）；面板关闭后导航恢复 `.nm-acrylic`。写法与工作台一致。
 */

const SECTION_LABELS: Readonly<Record<SettingsCategoryId, string>> = {
  provider: "Provider",
  network: "网络/代理",
  ocr: "OCR",
  translation: "翻译",
  inpaint: "图片修复",
  typeset: "排版样式",
  model_gpu: "模型/GPU",
  task_concurrency: "任务/并发",
  cache_revision: "缓存/Revision",
  recycle_bin: "回收站",
  backup_restore: "备份/恢复",
  plugins: "Plugin/Hooks",
};

type LoadPhase = "loading" | "ready" | "error";

function errorCode(error: unknown): string {
  if (typeof error === "string" && error.length > 0) return error;
  if (error && typeof error === "object") {
    const code = (error as { code?: unknown }).code;
    if (typeof code === "string" && code.length > 0) return code;
    const message = (error as { message?: unknown }).message;
    if (typeof message === "string" && message.length > 0) return message;
  }
  return "SETTINGS_UNAVAILABLE";
}

/** 分节 → 既有 panel 的唯一映射（照抄 `settings/SettingsPage.tsx` 的 dispatch）。 */
function renderSettingsSection(section: SettingsCategoryId, runtime: PageRuntime): ReactNode {
  const { clients } = runtime;
  switch (section) {
    case "provider":
      return (
        <>
          <ProviderProfilePanel client={clients.settings} />
          <CapabilityBindingPanel client={clients.settings} />
        </>
      );
    case "network":
      return <NetworkProfilePanel client={clients.settings} />;
    case "ocr":
      return <OcrSettingsPanel client={clients.settings} />;
    case "translation":
      return (
        <>
          <SfxPolicyControl client={clients.settings} />
          <TranslationParamsPanel client={clients.settings} />
        </>
      );
    case "inpaint":
      return <InpaintSettingsPanel client={clients.settings} />;
    case "typeset":
      return (
        <>
          <TypesetSettingsPanel client={clients.settings} />
          {/* §3.4：阅读方向是书籍 / 章节属性，设置页只给指引，不给假控件。 */}
          <section className="nm-settings__note" data-testid="settings-reading-direction-note">
            阅读方向（rtl / ltr / vertical）是书籍 / 章节属性：请在书架或章节属性中修改；
            设置页不提供全局默认方向。若需要「新建章节默认方向」，另立契约后再开放。
          </section>
        </>
      );
    case "model_gpu":
      return <ModelGpuSettingsPanel client={clients.settings} />;
    case "task_concurrency":
      return <TasksSettingsPanel client={clients.settings} />;
    case "cache_revision":
      return <CacheRevisionPanel client={clients.settings} />;
    case "recycle_bin":
      return <RecycleBinSettingsPanel client={clients.library} />;
    case "backup_restore":
      return <BackupSettingsPanel client={clients.settings} />;
    case "plugins":
      return <PluginSettingsPanel client={clients.settings} />;
  }
}

export interface SettingsProps {
  theme: Theme;
  onNavigate: (page: DesignPage) => void;
  onToggleTheme: () => void;
  /** 真实运行时注入；缺省为设计预览（逐分节标注无 IPC 通道）。见 `ui/types.ts`。 */
  runtime?: PageRuntime;
}

export function Settings({ theme, onNavigate, onToggleTheme, runtime }: SettingsProps) {
  const [activeSection, setActiveSection] = useState<SettingsCategoryId>(SETTINGS_CATEGORY_ORDER[0]);
  const [phase, setPhase] = useState<LoadPhase>(runtime ? "loading" : "ready");
  const [loadErrorCode, setLoadErrorCode] = useState<string | null>(null);
  const [sfxPolicy, setSfxPolicy] = useState<SfxPolicy | null>(null);
  const [reloadNonce, setReloadNonce] = useState(0);
  const tabRefs = useRef<Partial<Record<SettingsCategoryId, HTMLButtonElement | null>>>({});

  const settingsClient = runtime?.clients.settings ?? null;
  const commandOpen = runtime?.chrome.commandOpen === true;
  /*
   * 亚克力预算（与工作台同一写法）：命令面板是 UiRoot 渲染的全屏模态层。
   * 打开时把模态层记作 active 且预算压到 1，分节导航这一层低优先级表面就会被
   * 降级成 `.nm-acrylic-off`；关闭时导航恢复 `.nm-acrylic`。任何时刻同屏
   * backdrop-filter 都不超过 2 层。
   */
  const acrylicLayers = commandOpen
    ? ["global-command-layer", "settings-nav"]
    : ["settings-nav"];
  const budget = useAcrylicBudget(
    commandOpen ? "global-command-layer" : "settings-nav",
    acrylicLayers,
    commandOpen ? 1 : 2,
  );

  // 整页 readiness：一次 `settings_get`（无 section → 整份投影）。
  useEffect(() => {
    if (!settingsClient) return;
    let active = true;
    setPhase("loading");
    setLoadErrorCode(null);
    void (async () => {
      try {
        const policy = await settingsClient.getSfxSection();
        if (!active) return;
        setSfxPolicy(policy);
        setPhase("ready");
      } catch (error) {
        if (!active) return;
        setLoadErrorCode(errorCode(error));
        setPhase("error");
      }
    })();
    return () => {
      active = false;
    };
  }, [settingsClient, reloadNonce]);

  /*
   * 分节导航的键盘语义：vertical tablist 的 roving tabindex。
   * 设置页内切分节只重挂内容带、不卸载外壳（tablist 本身一直在），所以可以
   * 同步 focus 到目标 tab；这与 PrimaryNav 切一级页面时需要的 pending-focus
   * 机制不同（那种切换会卸载整页）。
   */
  const focusSection = (section: SettingsCategoryId) => {
    setActiveSection(section);
    tabRefs.current[section]?.focus();
  };

  const onNavKeyDown = (event: KeyboardEvent<HTMLButtonElement>, current: SettingsCategoryId) => {
    const index = SETTINGS_CATEGORY_ORDER.indexOf(current);
    let nextIndex = -1;
    if (event.key === "ArrowDown") nextIndex = (index + 1) % SETTINGS_CATEGORY_ORDER.length;
    else if (event.key === "ArrowUp")
      nextIndex = (index - 1 + SETTINGS_CATEGORY_ORDER.length) % SETTINGS_CATEGORY_ORDER.length;
    else if (event.key === "Home") nextIndex = 0;
    else if (event.key === "End") nextIndex = SETTINGS_CATEGORY_ORDER.length - 1;
    if (nextIndex < 0) return;
    event.preventDefault();
    focusSection(SETTINGS_CATEGORY_ORDER[nextIndex]);
  };

  const activeLabel = SECTION_LABELS[activeSection];

  const content = (() => {
    if (!runtime) {
      // 静态设计预览：骨架与导航是真的，数值一个都不展示（没有 IPC 来源）。
      return (
        <div className="nm-settings__panel" data-testid={`settings-preview-${activeSection}`}>
          <PageBlocked
            title={`${activeLabel} · 设计预览`}
            message="静态设计预览（?view=design）没有真实 IPC 设置通道：本节不展示任何设置值，避免用占位数据冒充可用设置。"
            detail="DESIGN_PREVIEW_NO_RUNTIME"
            testId="settings-preview-blocked"
          />
        </div>
      );
    }
    if (phase === "loading") {
      return (
        <PageLoading
          label="正在读取设置"
          detail="settings_get · 读取 sfx 分节做通道探针"
          testId="settings-loading"
        />
      );
    }
    if (phase === "error") {
      return (
        <PageError
          title="设置读取失败"
          message="设置通道不可用，页面不会用占位数值替代真实设置；请重试。"
          code={loadErrorCode ?? undefined}
          retryable
          onRetry={() => setReloadNonce((nonce) => nonce + 1)}
          testId="settings-error"
        />
      );
    }
    return (
      <div
        className="nm-settings__panel"
        role="tabpanel"
        id="nm-settings-panel"
        aria-labelledby={`nm-settings-tab-${activeSection}`}
        data-testid={`settings-content-${activeSection}`}
      >
        {renderSettingsSection(activeSection, runtime)}
      </div>
    );
  })();

  return (
    <div className="nm-settings" data-testid="page-settings">
      <header className="nm-titlebar" data-testid="settings-titlebar">
        <div className="nm-titlebar__brand">
          <span className="nm-brand-mark" aria-hidden="true">
            NM
          </span>
          <span className="nm-brand-name">New Manga</span>
        </div>
        <PrimaryNav
          activePage={runtime?.chrome.activePage ?? "settings"}
          onNavigate={runtime?.chrome.onNavigate ?? onNavigate}
        />
        <div className="nm-titlebar__actions">
          {/* 四页标题栏统一提供命令入口（Shelf / Workbench / Reader / Settings）。 */}
          {runtime ? (
            <button
              type="button"
              className="nm-command-trigger"
              data-testid="command-trigger"
              onClick={() => runtime.chrome.onOpenCommand()}
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
          <button
            type="button"
            className="nm-btn nm-btn--ghost nm-btn--icon"
            aria-label={theme === "dark" ? "切换到浅色主题" : "切换到深色主题"}
            data-testid="theme-toggle"
            onClick={onToggleTheme}
          >
            <Icon name={theme === "dark" ? "sun" : "moon"} size={16} />
          </button>
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

      <div className="nm-settings__body">
        <aside
          className={`nm-settings__nav ${budget.className("settings-nav", "acrylic")}`}
          data-testid="settings-section-nav"
          aria-label="设置分节"
        >
          <div className="nm-settings__nav-head">系统设置</div>
          {/* tablist 只放 tab：标题和页脚是普通内容，不能塞进 tablist。 */}
          <div
            className="nm-settings__nav-list"
            role="tablist"
            aria-orientation="vertical"
            aria-label="设置分节"
          >
            {SETTINGS_CATEGORY_ORDER.map((section) => (
              <button
                key={section}
                ref={(element) => {
                  tabRefs.current[section] = element;
                }}
                type="button"
                role="tab"
                id={`nm-settings-tab-${section}`}
                aria-selected={activeSection === section}
                aria-controls="nm-settings-panel"
                tabIndex={activeSection === section ? 0 : -1}
                className="nm-settings__nav-item"
                data-active={activeSection === section}
                data-testid={`settings-category-${section}`}
                onClick={() => setActiveSection(section)}
                onKeyDown={(event) => onNavKeyDown(event, section)}
              >
                {SECTION_LABELS[section]}
              </button>
            ))}
          </div>
          {runtime && phase === "ready" ? (
            <div className="nm-settings__nav-foot" data-testid="settings-channel-status">
              <span className="nm-settings__status-line">
                <StatusMark state="done" showLabel={false} />
                <span className="nm-caption">settings_get 已同步</span>
              </span>
              <span className="nm-data nm-tertiary" data-testid="settings-sfx-policy">
                {sfxPolicy === null
                  ? "SFX 策略 · 未设置（按 Core 默认）"
                  : `SFX 策略 · ${SFX_POLICY_LABELS[sfxPolicy]}`}
              </span>
            </div>
          ) : null}
        </aside>

        <main className="nm-settings__content" data-testid="settings-content-panel">
          <div className="nm-settings__content-head">
            <h1 className="nm-title" data-testid="settings-section-title">
              {activeLabel}
            </h1>
            <span className="nm-caption nm-tertiary" data-testid="settings-section-id">
              {runtime ? `section · ${activeSection}` : "设计预览 · 无运行时"}
            </span>
          </div>
          {content}
        </main>
      </div>
    </div>
  );
}
