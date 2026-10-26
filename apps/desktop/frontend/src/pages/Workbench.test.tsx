// @vitest-environment jsdom
import { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ChapterNavSummary, PageNavSummary } from "../library/types";
import type { RegionSummary } from "../region/types";
import type { PageChrome, PageRuntime, RuntimeClients } from "../ui/types";
import type {
  PipelineCommand,
  PipelineScope,
  RunSnapshot,
  TaskProjection,
} from "../workbench/client";
import { Workbench } from "./Workbench";

/*
 * 运行时工作台页的取数契约测试。
 *
 * 这里全部用 mock 客户端（不连 Tauri / Core），只验证「页面把 IPC 数据渲染成
 * 什么」以及「没有 IPC 来源的字段不得编造」。Blob URL 在 jsdom 里没有实现，
 * 因此 `URL.createObjectURL / revokeObjectURL` 由本文件替换成可断言的桩。
 */

const CHAPTERS: ChapterNavSummary[] = [
  { chapter_id: "ch-1", title: "潮汐留下的名字", chapter_number: "012", sort_order: 1 },
  { chapter_id: "ch-2", title: "第七盏路灯", chapter_number: "011", sort_order: 2 },
];

const PAGES: PageNavSummary[] = [
  { page_id: "pg-1", source_filename: "p001.png", sort_order: 1 },
  { page_id: "pg-2", source_filename: "p002.png", sort_order: 2 },
  { page_id: "pg-3", source_filename: "p003.png", sort_order: 3 },
];

const REGIONS: RegionSummary[] = [
  {
    region_id: "rg-1",
    region_type: "speech",
    sfx_policy: "translate",
    origin: "machine",
    revision_no: 3,
  },
  {
    region_id: "rg-2",
    region_type: "sfx",
    sfx_policy: "skip",
    origin: "user",
    revision_no: 1,
  },
];

const PROJECTION: TaskProjection = {
  run_id: "run-1",
  run_status: "running",
  run_title: "本章翻译",
  overall_progress: 0.4,
  current_page_id: "pg-2",
  current_step_type: "translate",
  step_flow: [
    { type: "ocr", label: "识别", state: "completed" },
    { type: "translate", label: "翻译", state: "running" },
    { type: "typeset", label: "排版", state: "pending" },
  ],
  rows: [
    {
      page_id: "pg-1",
      page_order: 1,
      filename: "p001.png",
      status: "completed",
      is_locked: false,
      is_pipeline_current: false,
      error_code: null,
    },
    {
      page_id: "pg-2",
      page_order: 2,
      filename: "p002.png",
      status: "running",
      is_locked: false,
      is_pipeline_current: true,
      error_code: null,
    },
  ],
  tasks: [
    {
      task_id: "task-1",
      page_id: "pg-1",
      status: "completed",
      error_code: null,
      steps: [
        {
          step_run_id: "step-1",
          step_type: "ocr",
          status: "completed",
          retry_no: 0,
          error_code: null,
          provider: "local-ocr",
          model: "ocr-model",
          device: "cpu",
        },
      ],
    },
    {
      task_id: "task-2",
      page_id: "pg-2",
      status: "running",
      error_code: null,
      steps: [
        {
          step_run_id: "step-2",
          step_type: "translate",
          status: "running",
          retry_no: 0,
          error_code: null,
          provider: "provider-x",
          model: "model-y",
          device: "cuda",
        },
      ],
    },
  ],
  counts: { total: 2, completed: 1, failed: 0, skipped: 0, blocked: 0, waiting: 1, processing: 0 },
  blocked_reasons: [],
  controls: {
    can_pause: true,
    can_stop: true,
    can_continue: false,
    can_restart: false,
    can_abandon: false,
    can_retry_failed: false,
  },
};

const SNAPSHOT: RunSnapshot = {
  run_id: "run-1",
  command: "translate_untranslated",
  scope: { kind: "chapter", chapter_id: "ch-1" },
  status: "running",
};

interface RuntimeOptions {
  bookId?: string | null;
  chapterId?: string | null;
  commandOpen?: boolean;
  listChapters?: () => Promise<ChapterNavSummary[]>;
  listChapterPages?: (chapterId: string) => Promise<PageNavSummary[]>;
  resolvePageResource?: (pageId: string) => Promise<{ resource_id: string; revision: string }>;
  listRegions?: (
    pageId: string,
  ) => Promise<{ regions: RegionSummary[]; page_size?: { width: number; height: number } | null }>;
  startRun?: (
    command: PipelineCommand,
    scope: PipelineScope,
    idempotencyKey: string,
  ) => Promise<{ run_id: string; status: string }>;
  getRunSnapshot?: (runId: string) => Promise<RunSnapshot>;
  getTaskProjection?: (runId: string) => Promise<TaskProjection>;
}

interface Harness {
  host: HTMLDivElement;
  runtime: PageRuntime;
  navigate: ReturnType<typeof vi.fn>;
  selectChapter: ReturnType<typeof vi.fn>;
  mocks: {
    listChapters: ReturnType<typeof vi.fn>;
    listChapterPages: ReturnType<typeof vi.fn>;
    resolvePageResource: ReturnType<typeof vi.fn>;
    listRegions: ReturnType<typeof vi.fn>;
    startRun: ReturnType<typeof vi.fn>;
    getRunSnapshot: ReturnType<typeof vi.fn>;
    getTaskProjection: ReturnType<typeof vi.fn>;
  };
}

let root: Root | undefined;
let container: HTMLDivElement | undefined;
let createObjectURL: ReturnType<typeof vi.fn>;
let revokeObjectURL: ReturnType<typeof vi.fn>;

function mount(element: React.ReactElement): HTMLDivElement {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
  act(() => {
    root?.render(element);
  });
  return container;
}

/** 让 React 提交 + 多级 promise 取数链跑完（章节 → 页面 → 图像 → 区域）。 */
async function flush(rounds = 8) {
  for (let index = 0; index < rounds; index += 1) {
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });
  }
}

async function mountRuntime(options: RuntimeOptions = {}): Promise<Harness> {
  const navigate = vi.fn();
  const selectChapter = vi.fn();
  const listChapters = vi.fn<() => Promise<ChapterNavSummary[]>>(async () => CHAPTERS);
  const listChapterPages = vi.fn<(chapterId: string) => Promise<PageNavSummary[]>>(
    async () => PAGES,
  );
  const resolvePageResource = vi.fn<
    (pageId: string) => Promise<{ resource_id: string; revision: string }>
  >(async () => ({ resource_id: "page-original-pg-1", revision: "rev-1" }));
  const listRegions = vi.fn<
    (
      pageId: string,
    ) => Promise<{ regions: RegionSummary[]; page_size?: { width: number; height: number } | null }>
  >(async () => ({ regions: REGIONS, page_size: { width: 1200, height: 1800 } }));
  const startRun = vi.fn<
    (
      command: PipelineCommand,
      scope: PipelineScope,
      idempotencyKey: string,
    ) => Promise<{ run_id: string; status: string }>
  >(async () => ({ run_id: "run-1", status: "running" }));
  const getRunSnapshot = vi.fn<(runId: string) => Promise<RunSnapshot>>(async () => SNAPSHOT);
  const getTaskProjection = vi.fn<(runId: string) => Promise<TaskProjection>>(async () => PROJECTION);

  if (options.listChapters) listChapters.mockImplementation(options.listChapters);
  if (options.listChapterPages) listChapterPages.mockImplementation(options.listChapterPages);
  if (options.resolvePageResource)
    resolvePageResource.mockImplementation(options.resolvePageResource);
  if (options.listRegions) listRegions.mockImplementation(options.listRegions);
  if (options.startRun) startRun.mockImplementation(options.startRun);
  if (options.getRunSnapshot) getRunSnapshot.mockImplementation(options.getRunSnapshot);
  if (options.getTaskProjection) getTaskProjection.mockImplementation(options.getTaskProjection);

  const chrome: PageChrome = {
    theme: "dark",
    activePage: "workbench",
    onNavigate: navigate,
    onToggleTheme: vi.fn(),
    onOpenCommand: vi.fn(),
    commandOpen: options.commandOpen ?? false,
    context: {
      bookId: options.bookId === undefined ? "bk-1" : options.bookId,
      chapterId: options.chapterId ?? null,
    },
    onOpenBook: vi.fn(),
    onSelectChapter: selectChapter,
  };
  const clients = {
    invoke: vi.fn(() => Promise.resolve(null)),
    library: { listChapters, listChapterPages, resolvePageResource },
    region: { listRegions },
    resource: {
      issue: vi.fn(async () => ({
        url: `http://m2res.localhost/m2id/${"a".repeat(43)}`,
        size: 4,
        opaqueId: "op-1",
      })),
      fetchAll: vi.fn(async () => new Blob([new Uint8Array([1, 2, 3, 4])])),
      fetchChunk: vi.fn(),
      revoke: vi.fn(),
    },
    workbench: { startRun, getRunSnapshot, getTaskProjection, controlRun: vi.fn() },
    reader: {},
    settings: {},
  } as unknown as RuntimeClients;
  const runtime: PageRuntime = { chrome, clients };

  const host = mount(
    <Workbench theme="dark" onNavigate={vi.fn()} onToggleTheme={vi.fn()} runtime={runtime} />,
  );
  await flush();
  return {
    host,
    runtime,
    navigate,
    selectChapter,
    mocks: {
      listChapters,
      listChapterPages,
      resolvePageResource,
      listRegions,
      startRun,
      getRunSnapshot,
      getTaskProjection,
    },
  };
}

function click(host: HTMLElement, selector: string) {
  const target = host.querySelector<HTMLElement>(selector);
  if (!target) throw new Error(`缺少元素：${selector}`);
  act(() => {
    target.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  });
}

beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  createObjectURL = vi.fn(() => "blob:mock-page");
  revokeObjectURL = vi.fn();
  Object.defineProperty(URL, "createObjectURL", {
    configurable: true,
    writable: true,
    value: createObjectURL,
  });
  Object.defineProperty(URL, "revokeObjectURL", {
    configurable: true,
    writable: true,
    value: revokeObjectURL,
  });
});

afterEach(() => {
  act(() => root?.unmount());
  container?.remove();
  root = undefined;
  container = undefined;
  delete (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT;
});

describe("运行时工作台：真实 IPC 数据", () => {
  it("renders chapters, real page indices, page image and regions from IPC", async () => {
    const { host, mocks } = await mountRuntime();

    // 章节：上下文没给 chapterId → 自动取 Core 返回的第一章。
    const select = host.querySelector<HTMLSelectElement>('[data-testid="workbench-chapter-select"]');
    expect(select?.value).toBe("ch-1");
    expect(select?.querySelectorAll("option")).toHaveLength(2);
    expect(mocks.listChapterPages).toHaveBeenCalledWith("ch-1");

    // 胶片条：页数是真实的 3 页，不是设计稿的 18 页。
    expect(host.querySelectorAll('[data-testid="filmstrip"] .nm-filmstrip__item')).toHaveLength(3);
    expect(host.querySelector('[data-testid="filmstrip"]')?.textContent).toContain("001");
    expect(host.querySelector('[data-testid="filmstrip"]')?.textContent).toContain("003");

    // 页图：resolve → issue → fetchAll 组成的 Blob URL。
    expect(mocks.resolvePageResource).toHaveBeenCalledWith("pg-1");
    expect(createObjectURL).toHaveBeenCalledTimes(1);
    const image = host.querySelector<HTMLImageElement>('[data-testid="workbench-page-image"]');
    expect(image?.getAttribute("src")).toBe("blob:mock-page");

    // 区域：真实字段（region_type / revision_no / origin），文本内容显示「未识别」。
    expect(mocks.listRegions).toHaveBeenCalledWith("pg-1");
    expect(host.querySelectorAll('[data-testid="workbench-region-list"] .nm-region')).toHaveLength(2);
    const regionText = host.querySelector('[data-testid="workbench-region-list"]')?.textContent ?? "";
    expect(regionText).toContain("对白 1");
    expect(regionText).toContain("拟声 2");
    expect(regionText).toContain("r3 · 机器");
    expect(regionText).toContain("未识别");

    // 没有 runId 时不得画假流水线：阻塞面 + 运行按钮，进度条不显示百分比。
    expect(host.querySelector('[data-testid="workbench-run-blocked"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="workbench-start-run"]')).not.toBeNull();
    expect(host.querySelector('[data-testid="pipeline"]')?.textContent).toContain("尚未开始运行");
    expect(host.querySelector('[data-testid="pipeline"] .nm-progress')).toBeNull();

    // 检查器在命令面板关闭时保留亚克力（同屏唯一一层）。
    expect(host.querySelector('[data-testid="inspector"]')?.classList.contains("nm-acrylic")).toBe(
      true,
    );
    expect(host.querySelectorAll(".nm-acrylic, .nm-acrylic-24, .nm-acrylic-strong")).toHaveLength(1);
  });

  it("never falls back to design fixtures when the runtime supplies data", async () => {
    const { host } = await mountRuntime();
    const text = host.textContent ?? "";
    // 设计稿 fixtures 里的假数据一律不得出现在运行时页面。
    for (const fabricated of [
      "雾港来信",
      "运行到校对",
      "先别回头",
      "manga-ocr",
      "0.94",
      "62%",
      "第 12 话",
    ]) {
      expect(text).not.toContain(fabricated);
    }
    // 缩略图通道不存在：只画未知占位，不画设计稿的漫画页图案。
    expect(host.querySelectorAll('[data-testid="workbench-thumb-unknown"]')).toHaveLength(3);
    expect(host.querySelectorAll('[data-testid="filmstrip"] .nm-filmstrip__mini')).toHaveLength(0);
  });

  it("renders the real run projection (task list, step flow, pipeline params) after startRun", async () => {
    const { host, mocks } = await mountRuntime();
    click(host, '[data-testid="workbench-start-run"]');
    await flush();

    expect(mocks.startRun).toHaveBeenCalledTimes(1);
    const [command, scope, key] = mocks.startRun.mock.calls[0];
    expect(command).toBe("translate_untranslated");
    expect(scope).toEqual({ kind: "chapter", chapter_id: "ch-1" });
    expect(typeof key).toBe("string");
    expect(key.length).toBeGreaterThan(0);

    // 真实任务列表 + 七态映射（completed → done，running → running）。
    expect(host.querySelectorAll('[data-testid="workbench-task-list"] .nm-wb-task')).toHaveLength(2);
    const taskList = host.querySelector('[data-testid="workbench-task-list"]');
    expect(taskList?.querySelector('.nm-status[data-state="done"]')).not.toBeNull();
    expect(taskList?.querySelector('.nm-status[data-state="running"]')).not.toBeNull();

    // 真实流水线阶段来自 step_flow（3 段），不是设计稿的 10 段。
    expect(host.querySelectorAll('[data-testid="pipeline"] .nm-stage')).toHaveLength(3);
    expect(host.querySelector('[data-testid="pipeline"]')?.textContent).toContain("识别");

    // 真实进度与真实流水线参数（provider / model / device）。
    expect(host.querySelector('[data-testid="pipeline"]')?.textContent).toContain("40%");
    const params = host.querySelector('[data-testid="workbench-pipeline-params"]');
    expect(params?.textContent).toContain("provider-x");
    expect(params?.textContent).toContain("model-y");
    expect(params?.textContent).toContain("cuda");

    // 运行中会轮询；卸载后必须清掉 interval（不会在 unmount 之后继续取数）。
    act(() => root?.unmount());
    root = undefined;
    const callsAfterUnmount = mocks.getRunSnapshot.mock.calls.length;
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 1200));
    });
    expect(mocks.getRunSnapshot.mock.calls.length).toBe(callsAfterUnmount);
  });

  it("shows the empty state when the book has no chapters", async () => {
    const { host } = await mountRuntime({ listChapters: vi.fn(async () => []) });
    expect(host.querySelector('[data-testid="workbench-chapters-empty"]')).not.toBeNull();
    expect(host.textContent).toContain("这本书还没有章节");
    expect(host.querySelector('[data-testid="filmstrip"]')).toBeNull();
  });

  it("shows the error state with a copyable IPC error code", async () => {
    const { host } = await mountRuntime({
      listChapters: vi.fn(async () => {
        throw { code: "CORE_UNAVAILABLE" };
      }),
    });
    const panel = host.querySelector('[data-testid="workbench-chapters-error"]');
    expect(panel).not.toBeNull();
    expect(panel?.getAttribute("role")).toBe("alert");
    expect(panel?.querySelector('[data-testid="page-error-code"]')?.textContent).toContain(
      "CORE_UNAVAILABLE",
    );
    expect(host.querySelector('[data-testid="page-error-retry"]')).not.toBeNull();
  });

  it("shows the image error code when the resource channel fails", async () => {
    const { host } = await mountRuntime({
      resolvePageResource: vi.fn(async () => {
        throw { code: "PAGE_NOT_FOUND" };
      }),
    });
    const panel = host.querySelector('[data-testid="workbench-image-error"]');
    expect(panel).not.toBeNull();
    expect(panel?.querySelector('[data-testid="page-error-code"]')?.textContent).toContain(
      "PAGE_NOT_FOUND",
    );
    expect(createObjectURL).not.toHaveBeenCalled();
  });

  it("renders the no-context empty state and routes back to the shelf", async () => {
    const { host, navigate } = await mountRuntime({ bookId: null });
    const empty = host.querySelector('[data-testid="workbench-no-book"]');
    expect(empty).not.toBeNull();
    expect(host.textContent).toContain("先在书架选择作品");
    click(host, '[data-testid="workbench-back-to-shelf"]');
    expect(navigate).toHaveBeenCalledWith("shelf");
  });

  it("downgrades the page acrylic layer while the command palette is open", async () => {
    const { host } = await mountRuntime({ commandOpen: true });
    const inspector = host.querySelector('[data-testid="inspector"]');
    expect(inspector?.classList.contains("nm-acrylic-off")).toBe(true);
    expect(inspector?.classList.contains("nm-acrylic")).toBe(false);
    // 同屏 backdrop-filter 层：命令面板占满预算，页面层全部降级。
    expect(host.querySelectorAll(".nm-acrylic, .nm-acrylic-24, .nm-acrylic-strong")).toHaveLength(0);
  });

  it("revokes the object URL when the selected page changes", async () => {
    const { host } = await mountRuntime();
    expect(createObjectURL).toHaveBeenCalledTimes(1);
    // 切到第 2 页 → 旧 Blob URL 必须 revoke，新 URL 重新生成。
    click(host, '[data-testid="filmstrip"] .nm-filmstrip__item:nth-child(2)');
    await flush();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:mock-page");
    expect(createObjectURL).toHaveBeenCalledTimes(2);
  });
});
