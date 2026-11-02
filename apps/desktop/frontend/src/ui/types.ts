/**
 * v2 运行时契约（Lead 冻结）。
 *
 * 分工：
 *   - `UiRoot` 是唯一的运行时根：它持有主题、当前页、跨页上下文（bookId /
 *     chapterId）与命令面板，并把 `PageChrome` 发给当前页。
 *   - 每个一级页面（`pages/Shelf.tsx` 等）在**只给骨架 props** 时渲染设计预览
 *     的固定 fixtures；在额外拿到 `runtime` 时改渲染真实 IPC 数据。
 *   - 页面自己取数（容器职责在页内），不把客户端塞进每个子组件。
 */
import type { DesignPage, Theme } from "../design/types";
import type { LibraryClient } from "../library/client";
import type { ReaderClient } from "../reader/client";
import type { RegionClient } from "../region/client";
import type { ResourceChannelClient } from "../resourceChannel/client";
import type { SettingsClient } from "../settings/client";
import type { WorkbenchClient } from "../workbench/client";

export type { DesignPage, Theme };

export type InvokeFn = (command: string, args?: Record<string, unknown>) => Promise<unknown>;

/** 跨页导航上下文：进入工作台/阅读器时携带的书与章。 */
export interface NavContext {
  bookId: string | null;
  chapterId: string | null;
}

/** 一级页面共享的框架能力。页面可以只用其中一部分。 */
export interface PageChrome {
  theme: Theme;
  activePage: DesignPage;
  onNavigate(page: DesignPage): void;
  onToggleTheme(): void;
  onOpenCommand(): void;
  /**
   * 命令面板当前是否打开。页面必须据此把自身的亚克力层队列重新排序：
   * 全屏同屏最多两层 backdrop-filter，模态面板优先，页面内低优先级层降级为
   * `.nm-acrylic-off`（见 `design/useAcrylicBudget`）。
   */
  commandOpen: boolean;
  context: NavContext;
  /**
   * 从书架进入工作台或阅读器。`chapterId` 为 null 表示"该书下有章节时取第一章"，
   * 页面不得自行编造 target。
   */
  onOpenBook(bookId: string, chapterId: string | null, target: "workbench" | "reader"): void;
  /** 在当前书内换章（工作台胶片条 / 阅读器章节跳转用）。 */
  onSelectChapter(bookId: string, chapterId: string): void;
}

/** 真实 IPC 客户端集合；只有 `UiRoot` 构造它。 */
export interface RuntimeClients {
  invoke: InvokeFn;
  library: LibraryClient;
  workbench: WorkbenchClient;
  region: RegionClient;
  resource: ResourceChannelClient;
  reader: ReaderClient;
  settings: SettingsClient;
}

/** 页面在真实运行时收到的注入；缺省即静态设计预览。 */
export interface PageRuntime {
  chrome: PageChrome;
  clients: RuntimeClients;
}

/** 页面取数状态。四态互斥，任何一态都必须给出可见的编码。 */
export type PagePhase = "loading" | "ready" | "empty" | "error";

/** 页面标题栏共用的窗口按钮组（CSS 绘制，非真实系统按钮）。 */
export interface CommandSpec {
  id: string;
  label: string;
  hint?: string;
  /** 图标名来自 `components/Icon`。 */
  icon?: string;
  /** 命令是否可用；不可用要写明原因，不能静默禁用。 */
  disabledReason?: string;
  run(): void;
}
