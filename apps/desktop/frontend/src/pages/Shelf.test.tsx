// @vitest-environment jsdom
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { BookSummary, ChapterNavSummary, PageNavSummary } from "../library/types";
import { Shelf } from "./Shelf";
import type { PageChrome, PageRuntime } from "../ui/types";

/**
 * 书架页「运行时不得回填 fixtures」的机械守卫。
 *
 * 背景（ZCode 独立审查 F-1，P1）：本 Task 的 AC8 把「跨书进度」写进诚实字段
 * 清单，但四页里只有书架页没有反断言。审查者做变异核验——把运行时
 * `progress: null` 改成 `progress: 42`——561 条测试全绿、零拦截，说明这条
 * 数据纪律当时只靠人工自查兜底。
 *
 * 本文件只做一件事：喂进真实形状的 IPC 数据，断言书卡上**不出现**任何 fixtures
 * 才有的字段（进度条 / 百分比 / VOL. 卷号 / 七态标记 / 假作者名）。
 */

let root: Root | undefined;
let container: HTMLDivElement | undefined;

const BOOKS: BookSummary[] = [
  {
    book_id: "book-1",
    title: "雾港来信",
    original_title: "霧港からの手紙",
    is_favorite: true,
    is_archived: false,
    page_count: 128,
    created_at: "2026-09-01T00:00:00Z",
    updated_at: new Date(Date.now() - 12 * 60_000).toISOString(),
  },
  {
    book_id: "book-2",
    title: "白昼残响",
    original_title: "",
    is_favorite: false,
    is_archived: true,
    page_count: null,
    created_at: "2026-09-02T00:00:00Z",
    updated_at: new Date(Date.now() - 60 * 60_000).toISOString(),
  },
];

const CHAPTERS: ChapterNavSummary[] = [
  { chapter_id: "ch-1", title: "潮汐留下的名字", chapter_number: "012", sort_order: 12 },
  { chapter_id: "ch-2", title: "第七盏路灯", chapter_number: "011", sort_order: 11 },
];

const PAGES: PageNavSummary[] = [
  { page_id: "p-1", source_filename: "page-001.png", sort_order: 1 },
  { page_id: "p-2", source_filename: "page-002.png", sort_order: 2 },
  { page_id: "p-3", source_filename: "page-003.png", sort_order: 3 },
];

function makeRuntime() {
  const library = {
    listBooks: vi.fn(async () => BOOKS),
    corePing: vi.fn(async () => ({
      status: "ok",
      protocol_version: { major: 2, minor: 1 },
      capabilities: ["library"],
    })),
    listChapters: vi.fn(async () => CHAPTERS),
    listChapterPages: vi.fn(async () => PAGES),
  };
  const chrome: PageChrome = {
    theme: "dark",
    activePage: "shelf",
    onNavigate: vi.fn(),
    onToggleTheme: vi.fn(),
    onOpenCommand: vi.fn(),
    commandOpen: false,
    context: { bookId: null, chapterId: null },
    onOpenBook: vi.fn(),
    onSelectChapter: vi.fn(),
  };
  const runtime = {
    chrome,
    clients: {
      invoke: vi.fn(async () => null),
      library,
      workbench: {},
      region: {},
      resource: {},
      reader: {},
      settings: {},
    },
  } as unknown as PageRuntime;
  return { runtime, library, chrome };
}

async function mountShelf(runtime: PageRuntime) {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
  await act(async () => {
    root?.render(
      <Shelf
        activePage="shelf"
        theme="dark"
        onNavigate={() => undefined}
        onToggleTheme={() => undefined}
        runtime={runtime}
      />,
    );
    // 两跳：listBooks → setState，然后 listChapters/listChapterPages → setState。
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();
  });
  return container;
}

beforeEach(() => {
  document.body.innerHTML = "";
});

afterEach(() => {
  act(() => root?.unmount());
  root = undefined;
  container = undefined;
});

describe("Shelf runtime data discipline（AC8 反 fixtures 回填）", () => {
  it("renders only IPC-backed fields and never fabricates progress/volume/state", async () => {
    const { runtime, library } = makeRuntime();
    const host = await mountShelf(runtime);

    // 真实数据确实渲染出来了（否则下面的"不出现"断言会因空页面而假通过）。
    expect(library.listBooks).toHaveBeenCalledTimes(1);
    const card = host.querySelector('[data-testid="book-book-1"]');
    expect(card).not.toBeNull();
    expect(card?.textContent).toContain("雾港来信");
    expect(card?.textContent).toContain("128 页");
    // 原名只出现在详情面板（书卡只放书名/页数/更新时间）。
    expect(host.querySelector('[data-testid="shelf-detail"]')?.textContent).toContain("霧港からの手紙");
    // 页数未知必须显式写"页数未知"，而不是编造 0 或沿用 fixtures 数值。
    expect(host.querySelector('[data-testid="book-book-2"]')?.textContent).toContain("页数未知");

    // 跨书进度没有 IPC 来源 → 既不画进度条也不显示百分比。
    expect(host.querySelectorAll(".nm-book-grid .nm-progress")).toHaveLength(0);
    expect(host.querySelector(".nm-book-grid")?.textContent).not.toMatch(/\d+\s*%/);

    // 卷号 / 跨书七态 / fixtures 假作者名与假计数同样不得出现。
    expect(host.textContent).not.toContain("VOL.");
    expect(host.querySelectorAll('.nm-book-grid [data-testid^="status-"]')).toHaveLength(0);
    for (const fake of ["南野灯", "绫濑千景", "18 话", "1280 页", "设计预览"]) {
      expect(host.textContent).not.toContain(fake);
    }
  });

  it("shows real chapters and page counts without inventing chapter states", async () => {
    const { runtime } = makeRuntime();
    const host = await mountShelf(runtime);

    const chapters = host.querySelectorAll('[data-testid="chapter-list"] li');
    expect(chapters).toHaveLength(CHAPTERS.length);
    expect(chapters[0].textContent).toContain("潮汐留下的名字");
    expect(chapters[0].textContent).toContain("012");
    // 每章页数来自 list_chapter_pages（3 页），不是 fixtures 的 24p/22p。
    expect(chapters[0].textContent).toContain("3p");
    expect(host.querySelector('[data-testid="chapter-list"]')?.textContent).not.toContain("24p");
    // 章节流水线状态同样无 IPC 来源 → 不画状态标记。
    expect(host.querySelectorAll('[data-testid="chapter-list"] [data-testid^="status-"]')).toHaveLength(0);
  });

  it("keeps the honest empty library state when Core returns no books", async () => {
    const { runtime, library } = makeRuntime();
    library.listBooks.mockResolvedValueOnce([]);
    const host = await mountShelf(runtime);

    expect(host.querySelector('[data-testid="shelf-empty"]')).not.toBeNull();
    expect(host.querySelectorAll(".nm-book-card")).toHaveLength(0);
  });

  /**
   * ZCode 审查期之外、由真机验收脚本 S3 抓到的缺陷回归守卫：
   * 运行时 `palette` 传 null（面板归 UiRoot 托管），标题栏那颗
   * 「搜索或执行命令」按钮当时 `onClick={() => palette?.onOpen()}`，
   * 对 null 静默无操作 —— 生产环境里是一颗点了没反应的假按钮，
   * 而且 aria-expanded 永远是 false。564 条 jsdom 测试全绿也没拦住它。
   */
  it("标题栏命令触发器在运行时真的能发出打开请求（不是死按钮）", async () => {
    const { runtime, chrome } = makeRuntime();
    const host = await mountShelf(runtime);

    const trigger = host.querySelector('[data-testid="command-trigger"]') as HTMLButtonElement | null;
    expect(trigger).not.toBeNull();
    expect(trigger?.getAttribute("aria-expanded")).toBe("false");

    await act(async () => {
      trigger?.click();
    });
    expect(chrome.onOpenCommand).toHaveBeenCalledTimes(1);
  });

  it("commandOpen=false 时触发器 aria-expanded 为 false", async () => {
    const { runtime, chrome } = makeRuntime();
    chrome.commandOpen = false;
    const host = await mountShelf(runtime);
    const trigger = host.querySelector('[data-testid="command-trigger"]') as HTMLButtonElement | null;
    expect(trigger?.getAttribute("aria-expanded")).toBe("false");
  });

  it("commandOpen=true 时触发器 aria-expanded 为 true", async () => {
    const { runtime, chrome } = makeRuntime();
    chrome.commandOpen = true;
    const host = await mountShelf(runtime);
    const trigger = host.querySelector('[data-testid="command-trigger"]') as HTMLButtonElement | null;
    expect(trigger?.getAttribute("aria-expanded")).toBe("true");
  });
});
