// @vitest-environment jsdom
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { DesignPage, Theme } from "../design/types";
import { LibraryClient } from "../library/client";
import { ReaderClient } from "../reader/client";
import { RegionClient } from "../region/client";
import { ResourceChannelClient } from "../resourceChannel/client";
import { SettingsClient } from "../settings/client";
import { WorkbenchClient } from "../workbench/client";
import type { InvokeFn, PageChrome, PageRuntime, RuntimeClients } from "../ui/types";
import { Reader } from "./Reader";

/**
 * UIUX-V2-RUNTIME-1 / 阅读器 v2 运行时接线。
 *
 * 覆盖：无跨页上下文空态（不出 IPC）、真实数据成功态（书名/章节名/页码/
 * 进度/页图全部来自 mock IPC）、←/→ 键盘翻页与边界、tablist 与下拉不劫持、
 * IPC 失败错误态 + 重试、投影不可用时进度显示「—」、命令面板打开时的亚克力
 * 预算降级、页图 Blob URL 的 revoke。
 */

const globalUrl = URL as unknown as {
  createObjectURL?: (blob: Blob) => string;
  revokeObjectURL?: (url: string) => void;
};

let root: Root | undefined;
let container: HTMLDivElement | undefined;
let createObjectUrl: ReturnType<typeof vi.fn>;
let revokeObjectUrl: ReturnType<typeof vi.fn>;
let blobSeq = 0;

function mount(element: React.ReactElement): HTMLDivElement {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
  act(() => {
    root?.render(element);
  });
  return container;
}

let host: HTMLDivElement | undefined;

async function flush(rounds = 4) {
  for (let index = 0; index < rounds; index += 1) {
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });
  }
}

function q(selector: string): HTMLElement | null {
  return host?.querySelector<HTMLElement>(selector) ?? null;
}

function text(selector: string): string {
  return q(selector)?.textContent?.trim() ?? "";
}

function keydownOn(target: EventTarget, key: string) {
  act(() => {
    target.dispatchEvent(new window.KeyboardEvent("keydown", { key, bubbles: true }));
  });
}

/** 资源通道的 mock fetch：fetchAll 只用到 ok / arrayBuffer / text。 */
const mockFetch = (async () => ({
  ok: true,
  arrayBuffer: async () => new Uint8Array([1, 2, 3, 4]).buffer,
  text: async () => "",
})) as unknown as typeof fetch;

interface InvokeOptions {
  failCommands?: Set<string>;
  respond?: (command: string, args: Record<string, unknown> | undefined) => unknown | undefined;
}

function makeInvoke(options: InvokeOptions = {}) {
  const calls: Array<{ command: string; args: Record<string, unknown> | undefined }> = [];
  const invoke: InvokeFn = vi.fn(async (command: string, args?: Record<string, unknown>) => {
    calls.push({ command, args });
    const custom = options.respond?.(command, args);
    if (custom !== undefined) return custom;
    if (options.failCommands?.has(command)) throw new Error("CORE_UNAVAILABLE");
    switch (command) {
      case "library_list_books":
        return [
          {
            book_id: "book-1",
            title: "雾港来信",
            original_title: "雾港来信",
            is_favorite: false,
            is_archived: false,
            page_count: 3,
            created_at: "2026-10-01T00:00:00+00:00",
            updated_at: "2026-10-02T00:00:00+00:00",
          },
        ];
      case "list_chapters":
        return {
          chapters: [
            {
              chapter_id: "chapter-1",
              title: "潮汐留下的名字",
              chapter_number: "第 12 话",
              sort_order: 0,
            },
            {
              chapter_id: "chapter-2",
              title: "第七盏路灯",
              chapter_number: "第 11 话",
              sort_order: 1,
            },
          ],
        };
      case "list_chapter_pages":
        return {
          pages: [
            { page_id: "page-1", source_filename: "01.png", sort_order: 0 },
            { page_id: "page-2", source_filename: "02.png", sort_order: 1 },
            { page_id: "page-3", source_filename: "03.png", sort_order: 2 },
          ],
        };
      case "library_get_reader_projection":
        return {
          book_id: "book-1",
          chapter_id: "chapter-1",
          mode: "original",
          layout: "ltr",
          pages: [],
          saved_progress: {
            book_id: "book-1",
            chapter_id: "chapter-1",
            mode: "original",
            last_page_id: "page-2",
            scroll_offset_y: 0,
            progress_percent: 40,
            last_read_at: null,
            total_read_seconds: 0,
          },
          initial_position: { page_id: "page-2", scroll_offset_y: 0 },
        };
      case "resolve_page_resource":
        return { resource_id: `resource-${String(args?.pageId ?? "")}`, revision: "rev-1" };
      case "issue_resource_url":
        return { url: "http://m2res.localhost/m2id/opaque", size: 4, opaque_id: "opaque" };
      case "library_save_reading_progress":
        return {
          book_id: "book-1",
          chapter_id: String(args?.chapterId ?? ""),
          mode: "original",
          last_page_id: String(args?.pageId ?? ""),
          scroll_offset_y: 0,
          progress_percent: 66.6,
          last_read_at: null,
          total_read_seconds: 0,
        };
      default:
        return null;
    }
  });
  return { invoke, calls };
}

function makeRuntime(
  invoke: InvokeFn,
  context: { bookId: string | null; chapterId: string | null },
  chromeOverrides: Partial<PageChrome> = {},
): PageRuntime {
  const chrome: PageChrome = {
    theme: "dark",
    activePage: "reader",
    onNavigate: vi.fn<(page: DesignPage) => void>(),
    onToggleTheme: vi.fn(),
    onOpenCommand: vi.fn(),
    commandOpen: false,
    context,
    onOpenBook: vi.fn(),
    onSelectChapter: vi.fn(),
    ...chromeOverrides,
  };
  const clients: RuntimeClients = {
    invoke,
    library: new LibraryClient(invoke),
    workbench: new WorkbenchClient(invoke),
    region: new RegionClient(invoke),
    resource: new ResourceChannelClient(invoke, mockFetch),
    reader: new ReaderClient(invoke),
    settings: new SettingsClient(invoke),
  };
  return { chrome, clients };
}

function renderReader(runtime: PageRuntime, theme: Theme = "dark") {
  host = mount(
    <Reader
      theme={theme}
      onNavigate={runtime.chrome.onNavigate}
      onToggleTheme={runtime.chrome.onToggleTheme}
      runtime={runtime}
    />,
  );
  return host;
}

beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  blobSeq = 0;
  createObjectUrl = vi.fn(() => `blob:mock-${++blobSeq}`);
  revokeObjectUrl = vi.fn();
  globalUrl.createObjectURL = createObjectUrl as unknown as (blob: Blob) => string;
  globalUrl.revokeObjectURL = revokeObjectUrl as unknown as (url: string) => void;
});

afterEach(() => {
  act(() => root?.unmount());
  container?.remove();
  root = undefined;
  container = undefined;
  host = undefined;
  delete globalUrl.createObjectURL;
  delete globalUrl.revokeObjectURL;
  delete (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT;
});

describe("Reader v2 runtime", () => {
  it("renders the empty state and a back-to-shelf action when there is no book context, without any IPC", async () => {
    const { invoke } = makeInvoke();
    const runtime = makeRuntime(invoke, { bookId: null, chapterId: null });
    renderReader(runtime);
    await flush(2);

    expect(q('[data-testid="page-reader"]')).not.toBeNull();
    expect(q('[data-testid="reader-no-context"]')).not.toBeNull();
    expect(text('[data-testid="reader-no-context"]')).toContain("书架");
    // 没有 bookId 就不该发任何请求——空态不是"取数失败"。
    expect(invoke).not.toHaveBeenCalled();

    /*
     * 设计稿的阅读器是「48 标题栏 + 顶 48 浮层 + 底 40 浮层」：空态也保留两条
     * 浮层带，但值未知就写「—」，翻页按钮 disabled 并在 aria-label / title 里
     * 说明原因——不为了好看填假数据。
     */
    expect(q('[data-testid="reader-top"]')).not.toBeNull();
    expect(q('[data-testid="reader-bottom"]')).not.toBeNull();
    expect(text('[data-testid="reader-book-title"]')).toBe("—");
    expect(text('[data-testid="reader-chapter-title"]')).toBe("—");
    expect(text('[data-testid="reader-pager"]')).toBe("—/—");
    expect(text('[data-testid="reader-progress"]')).toBe("—");
    expect(text('[data-testid="reader-band-note"]')).toContain("当前没有可读章节");
    const prev = q('[data-testid="reader-prev"]') as HTMLButtonElement | null;
    const next = q('[data-testid="reader-next"]') as HTMLButtonElement | null;
    expect(prev?.disabled).toBe(true);
    expect(prev?.getAttribute("aria-label")).toContain("当前没有可读章节");
    expect(next?.disabled).toBe(true);
    expect(next?.getAttribute("title")).toContain("当前没有可读章节");

    // 命令入口与其余一级页面一致（标题栏 trigger → chrome.onOpenCommand）。
    const trigger = q('[data-testid="command-trigger"]');
    expect(trigger).not.toBeNull();
    expect(trigger?.getAttribute("aria-expanded")).toBe("false");
    act(() => {
      trigger?.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
    });
    expect(runtime.chrome.onOpenCommand).toHaveBeenCalledTimes(1);

    const back = q('[data-testid="reader-back-to-shelf"]');
    expect(back).not.toBeNull();
    act(() => {
      back?.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
    });
    expect(runtime.chrome.onNavigate).toHaveBeenCalledWith("shelf");
  });

  it("renders real chapter/page/progress data and pages with the arrow keys without overrunning the chapter", async () => {
    const { invoke, calls } = makeInvoke();
    const runtime = makeRuntime(invoke, { bookId: "book-1", chapterId: "chapter-1" });
    renderReader(runtime);
    await flush();

    // 书名 / 章节名 / 页码 / 进度 / 布局全部来自 mock IPC，不是 fixtures。
    expect(text('[data-testid="reader-book-title"]')).toBe("雾港来信");
    expect(text('[data-testid="reader-chapter-title"]')).toContain("潮汐留下的名字");
    expect(text('[data-testid="reader-chapter-title"]')).toContain("第 12 话");
    // 投影把初始页定在第 2 页（page-2），所以起始页码是 2 / 3。
    expect(text('[data-testid="reader-pager"]')).toBe("2 / 3");
    expect(text('[data-testid="reader-progress"]')).toBe("40%");
    expect(text('[data-testid="reader-layout"]')).toBe("左 → 右");
    expect(q('[data-testid="reader-page-image"]')?.getAttribute("src")).toMatch(/^blob:mock-/);
    expect(createObjectUrl).toHaveBeenCalledTimes(1);

    // 页图链路：resolve_page_resource → issue_resource_url → fetchAll。
    expect(calls.map((call) => call.command)).toEqual(
      expect.arrayContaining([
        "list_chapters",
        "list_chapter_pages",
        "library_get_reader_projection",
        "resolve_page_resource",
        "issue_resource_url",
      ]),
    );
    expect(calls.find((call) => call.command === "resolve_page_resource")?.args).toMatchObject({
      pageId: "page-2",
    });

    // 两个浮层都在亚克力预算内（2 层）。
    expect(q('[data-testid="reader-top"]')?.classList.contains("nm-acrylic-24")).toBe(true);
    expect(q('[data-testid="reader-bottom"]')?.classList.contains("nm-acrylic-24")).toBe(true);

    // → 下一页：页码前进，进度写回真实 page_id，进度百分比用 Core 返回的快照。
    keydownOn(window, "ArrowRight");
    expect(text('[data-testid="reader-pager"]')).toBe("3 / 3");
    await flush();
    expect(text('[data-testid="reader-progress"]')).toBe("67%");
    const saves = calls.filter((call) => call.command === "library_save_reading_progress");
    expect(saves).toHaveLength(1);
    expect(saves[0].args).toMatchObject({
      chapterId: "chapter-1",
      mode: "original",
      pageId: "page-3",
      scrollOffsetY: 0,
    });

    // 切页时旧 Blob URL 必须回收。
    expect(revokeObjectUrl).toHaveBeenCalledWith("blob:mock-1");

    // 章末不越界造页，也不再重复写回。
    keydownOn(window, "ArrowRight");
    await flush(2);
    expect(text('[data-testid="reader-pager"]')).toBe("3 / 3");
    expect(calls.filter((call) => call.command === "library_save_reading_progress")).toHaveLength(1);

    // ← 回到上一页。
    keydownOn(window, "ArrowLeft");
    await flush();
    expect(text('[data-testid="reader-pager"]')).toBe("2 / 3");

    // tablist 内的方向键归 tab 导航，不能再翻页。
    const pagerTab = q('[data-testid="tab-reader"]');
    expect(pagerTab).not.toBeNull();
    keydownOn(pagerTab as HTMLElement, "ArrowRight");
    expect(text('[data-testid="reader-pager"]')).toBe("2 / 3");

    // 章节下拉里按方向键属于下拉自身，也不能翻页。
    const select = q('[data-testid="reader-chapter-select"]');
    expect(select).not.toBeNull();
    keydownOn(select as HTMLElement, "ArrowLeft");
    expect(text('[data-testid="reader-pager"]')).toBe("2 / 3");

    // 换章走 chrome.onSelectChapter，由 UiRoot 更新跨页上下文。
    act(() => {
      const element = select as HTMLSelectElement;
      element.value = "chapter-2";
      element.dispatchEvent(new window.Event("change", { bubbles: true }));
    });
    expect(runtime.chrome.onSelectChapter).toHaveBeenCalledWith("book-1", "chapter-2");
  });

  it("downgrades the low-priority acrylic layer while the command palette is open", async () => {
    const { invoke } = makeInvoke();
    const runtime = makeRuntime(invoke, { bookId: "book-1", chapterId: "chapter-1" });
    renderReader(runtime);
    await flush();

    expect(q('[data-testid="reader-top"]')?.classList.contains("nm-acrylic-24")).toBe(true);
    expect(q('[data-testid="reader-bottom"]')?.classList.contains("nm-acrylic-24")).toBe(true);

    const openRuntime: PageRuntime = {
      ...runtime,
      chrome: { ...runtime.chrome, commandOpen: true },
    };
    await act(async () => {
      root?.render(
        <Reader
          theme="dark"
          onNavigate={openRuntime.chrome.onNavigate}
          onToggleTheme={openRuntime.chrome.onToggleTheme}
          runtime={openRuntime}
        />,
      );
    });

    expect(q('[data-testid="reader-top"]')?.classList.contains("nm-acrylic-24")).toBe(true);
    expect(q('[data-testid="reader-bottom"]')?.classList.contains("nm-acrylic-off")).toBe(true);
    // 同屏最多两层 backdrop-filter：降级后本页只剩一层。
    expect(host?.querySelectorAll(".nm-acrylic, .nm-acrylic-24, .nm-acrylic-strong")).toHaveLength(1);
    // 命令入口的展开态跟随 chrome.commandOpen。
    expect(q('[data-testid="command-trigger"]')?.getAttribute("aria-expanded")).toBe("true");
  });

  it("shows the IPC error code and recovers through the retry action", async () => {
    const failCommands = new Set(["list_chapters"]);
    const { invoke } = makeInvoke({ failCommands });
    const runtime = makeRuntime(invoke, { bookId: "book-1", chapterId: "chapter-1" });
    renderReader(runtime);
    await flush();

    expect(q('[data-testid="reader-error"]')).not.toBeNull();
    expect(text('[data-testid="page-error-code"]')).toContain("CORE_UNAVAILABLE");

    failCommands.clear();
    const retry = q('[data-testid="page-error-retry"]');
    expect(retry).not.toBeNull();
    act(() => {
      retry?.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
    });
    await flush();

    expect(q('[data-testid="reader-error"]')).toBeNull();
    expect(text('[data-testid="reader-pager"]')).toBe("2 / 3");
  });

  it("keeps paging when the projection is unavailable but never fabricates a progress percentage", async () => {
    const failCommands = new Set(["library_get_reader_projection"]);
    const { invoke } = makeInvoke({ failCommands });
    const runtime = makeRuntime(invoke, { bookId: "book-1", chapterId: "chapter-1" });
    renderReader(runtime);
    await flush();

    // 页序列仍来自 list_chapter_pages：可以从第 1 页开始翻。
    expect(text('[data-testid="reader-pager"]')).toBe("1 / 3");
    expect(text('[data-testid="reader-progress"]')).toBe("—");
    expect(text('[data-testid="reader-progress-unavailable"]')).toContain("CORE_UNAVAILABLE");

    keydownOn(window, "ArrowRight");
    expect(text('[data-testid="reader-pager"]')).toBe("2 / 3");
    await flush();
    // 写回成功才会得到真实百分比；否则保持未知。
    expect(text('[data-testid="reader-progress"]')).toBe("67%");
  });

  it("renders an explicit blocked state for webtoon_vertical chapters instead of faking paging", async () => {
    const { invoke, calls } = makeInvoke({
      respond: (command) =>
        command === "library_get_reader_projection"
          ? {
              book_id: "book-1",
              chapter_id: "chapter-1",
              mode: "original",
              layout: "webtoon_vertical",
              pages: [],
              saved_progress: null,
              initial_position: { page_id: "page-1", scroll_offset_y: 0 },
            }
          : undefined,
    });
    const runtime = makeRuntime(invoke, { bookId: "book-1", chapterId: "chapter-1" });
    renderReader(runtime);
    await flush();

    expect(q('[data-testid="reader-webtoon-blocked"]')).not.toBeNull();
    expect(text('[data-testid="reader-layout"]')).toBe("纵向条漫");
    // 纵向条漫没有"第 x / y 页"：页码写「—/—」，不渲染页图也不拉页图资源。
    expect(text('[data-testid="reader-pager"]')).toBe("—/—");
    expect(q('[data-testid="reader-page-image"]')).toBeNull();
    expect(text('[data-testid="reader-band-note"]')).toContain("纵向条漫");
    expect((q('[data-testid="reader-next"]') as HTMLButtonElement | null)?.disabled).toBe(true);
    expect(calls.some((call) => call.command === "resolve_page_resource")).toBe(false);
  });

  it("shows 「—」 for the book title when the book lookup fails instead of reusing a fixture name", async () => {
    const failCommands = new Set(["library_list_books"]);
    const { invoke } = makeInvoke({ failCommands });
    const runtime = makeRuntime(invoke, { bookId: "book-1", chapterId: "chapter-1" });
    renderReader(runtime);
    await flush();

    // 书名没有 IPC 来源时显示「—」，章节名/页码仍来自真实数据。
    expect(text('[data-testid="reader-book-title"]')).toBe("—");
    expect(text('[data-testid="reader-chapter-title"]')).toContain("潮汐留下的名字");
    expect(text('[data-testid="reader-pager"]')).toBe("2 / 3");
  });

  it("renders an empty state when the book has no chapters", async () => {
    const { invoke } = makeInvoke({
      respond: (command) => (command === "list_chapters" ? { chapters: [] } : undefined),
    });
    const runtime = makeRuntime(invoke, { bookId: "book-1", chapterId: null });
    renderReader(runtime);
    await flush();

    expect(q('[data-testid="reader-empty"]')).not.toBeNull();
    expect(text('[data-testid="reader-empty"]')).toContain("该书暂无章节");
  });
});
