import { renderToString } from "react-dom/server";
import { act } from "react";
import { JSDOM } from "jsdom";
import { describe, expect, it, vi } from "vitest";
import { RegionOverlay } from "../region/RegionOverlay";
import type { RegionSummary } from "../region/types";
import type { ListenFn } from "../events";
import { ViewerPanel } from "./ViewerPanel";
import { TaskProgressPanel } from "./TaskProgressPanel";
import type { TaskProjection } from "./client";
import { WorkbenchPage } from "./WorkbenchPage";

/**
 * First-slice component smoke pins (M2-WORKBENCH-REACT-1). Component
 * structure and the read-only overlay math are asserted on the static
 * render; interaction/data coverage lives at the client layer
 * (region/client.test.ts), the established test split of this frontend.
 *
 * The container's data-loading effects do not run under renderToString by
 * design (React SSR semantics); WorkbenchPage therefore renders its honest
 * initial empty state here.
 */

// A page 100x50 letterboxed into a 200x100 container fills it exactly
// (aspect 2:1 both) — view = {x:0, y:0, w:200, h:100}. The normalized bbox
// [0.1, 0.2, 0.3, 0.4] projects to x=20, y=20, w=60, h=40.
const FRAME_REGION: RegionSummary = {
  region_id: "region-1",
  region_type: "sfx",
  sfx_policy: "translate",
  origin: "user",
  revision_no: 3,
  geometry: {
    bbox: [0.1, 0.2, 0.3, 0.4],
    polygon: [[0.1, 0.2], [0.4, 0.2], [0.4, 0.6], [0.1, 0.6]],
  },
};

const INTERACTIVE_REGION: RegionSummary = {
  region_id: "region-1",
  region_type: "speech",
  sfx_policy: "skip",
  origin: "user",
  revision_no: 1,
  geometry: { bbox: [0.1, 0.2, 0.3, 0.4], polygon: [] },
};

const PREVIEW_PNG_BYTES = Uint8Array.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
  0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52,
  0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
  0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4, 0x89,
  0x00, 0x00, 0x00, 0x0b, 0x49, 0x44, 0x41, 0x54,
  0x78, 0x9c, 0x63, 0x60, 0x00, 0x02, 0x00, 0x00, 0x05, 0x00, 0x01,
  0xa5, 0xf6, 0x45, 0x40,
  0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
]);

async function nextTurn() {
  for (let i = 0; i < 8; i += 1) await Promise.resolve();
}

async function mountInteractiveWorkbench(
  invoke: (command: string, args?: Record<string, unknown>) => Promise<unknown>,
  options: { resourceFetch?: typeof fetch; resolveDebounceMs?: number; regionDebounceMs?: number; listen?: ListenFn } = {},
) {
  const dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost" });
  Object.defineProperty(dom.window.HTMLElement.prototype, "clientWidth", {
    configurable: true,
    get: () => 200,
  });
  Object.defineProperty(dom.window.HTMLElement.prototype, "clientHeight", {
    configurable: true,
    get: () => 100,
  });
  const createdBlobs: Blob[] = [];
  const revokedUrls: string[] = [];
  const resourceReads: string[] = [];
  Object.defineProperty(dom.window.URL, "createObjectURL", {
    configurable: true,
    value: (blob: Blob) => {
      createdBlobs.push(blob);
      return `blob:rc4-preview-${createdBlobs.length}`;
    },
  });
  Object.defineProperty(dom.window.URL, "revokeObjectURL", {
    configurable: true,
    value: (url: string) => { revokedUrls.push(url); },
  });
  vi.stubGlobal("window", dom.window);
  vi.stubGlobal("document", dom.window.document);
  vi.stubGlobal("navigator", dom.window.navigator);
  vi.stubGlobal("Node", dom.window.Node);
  vi.stubGlobal("Element", dom.window.Element);
  vi.stubGlobal("HTMLElement", dom.window.HTMLElement);
  vi.stubGlobal("URL", dom.window.URL);
  vi.stubGlobal("fetch", options.resourceFetch ?? (async (input: RequestInfo | URL) => {
    resourceReads.push(String(input));
    return new Response(PREVIEW_PNG_BYTES.slice(), {
      status: 200,
      headers: { "content-type": "image/png" },
    });
  }));
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);

  const { createRoot } = await import("react-dom/client");
  const container = dom.window.document.createElement("div");
  dom.window.document.body.append(container);
  const root = createRoot(container);
  await act(async () => {
    // tests default to 0 (historical immediate resolve/region reads); the
    // debounce behavior itself is covered by dedicated fake-timer cases
    root.render(
      <WorkbenchPage
        invoke={invoke}
        listen={options.listen}
        resolveDebounceMs={options.resolveDebounceMs ?? 0}
        regionDebounceMs={options.regionDebounceMs ?? 0}
      />,
    );
    await nextTurn();
  });

  const click = async (testId: string) => {
    const target = container.querySelector(`[data-testid="${testId}"]`) as HTMLElement | null;
    if (!target) throw new Error(`missing test target: ${testId}`);
    await act(async () => {
      target.dispatchEvent(new dom.window.MouseEvent("click", {
        bubbles: true,
        cancelable: true,
        button: 0,
      }));
      await nextTurn();
    });
  };
  const input = async (testId: string, value: string) => {
    const target = container.querySelector(`[data-testid="${testId}"]`) as HTMLInputElement | null;
    if (!target) throw new Error(`missing input: ${testId}`);
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(dom.window.HTMLInputElement.prototype, "value")?.set;
      setter?.call(target, value);
      target.dispatchEvent(new dom.window.Event("input", { bubbles: true }));
      await nextTurn();
    });
  };
  const keyDown = async (testId: string, key: string, modifiers: KeyboardEventInit = {}) => {
    const target = container.querySelector(`[data-testid="${testId}"]`) as HTMLElement | null;
    if (!target) throw new Error(`missing key target: ${testId}`);
    await act(async () => {
      target.dispatchEvent(new dom.window.KeyboardEvent("keydown", { key, bubbles: true, cancelable: true, ...modifiers }));
      await nextTurn();
    });
  };
  const keyUp = async (testId: string, key: string) => {
    const target = container.querySelector(`[data-testid="${testId}"]`) as HTMLElement | null;
    if (!target) throw new Error(`missing key target: ${testId}`);
    await act(async () => {
      target.dispatchEvent(new dom.window.KeyboardEvent("keyup", { key, bubbles: true, cancelable: true }));
      await nextTurn();
    });
  };
  const unmount = async () => {
    await act(async () => root.unmount());
    dom.window.close();
    vi.useRealTimers();
    vi.unstubAllGlobals();
  };
  return { dom, container, click, input, keyDown, keyUp, createdBlobs, revokedUrls, resourceReads, unmount };
}

// M2-PAGE-NAV-PROJECTION-1 drill-down fixtures: TWO books so the
// switch-book reset and stale-reply cases (DSH r1 PR-06/PR-8) have a
// cross-book window to exercise.
const BOOK_A_ROW = {
  book_id: "book-a",
  title: "Manga A",
  original_title: "漫画A",
  is_favorite: false,
  is_archived: false,
  page_count: 1,
  created_at: "2026-10-07T00:00:00Z",
  updated_at: "2026-10-07T00:00:00Z",
};
const BOOK_B_ROW = { ...BOOK_A_ROW, book_id: "book-b", title: "Manga B" };

const TASK_PROJECTION: TaskProjection = {
  run_id: "run-1",
  run_status: "completed",
  run_title: "测试任务",
  overall_progress: 1,
  current_page_id: "page-1",
  current_step_type: "render",
  step_flow: [{ type: "render", label: "渲染", state: "completed" }],
  rows: [],
  tasks: [],
  counts: { total: 1, completed: 1, failed: 0, skipped: 0, blocked: 0, waiting: 0, processing: 0 },
  blocked_reasons: [],
  controls: { can_pause: false, can_stop: false, can_continue: false, can_restart: false, can_abandon: false, can_retry_failed: false },
};

function makeInteractiveInvoke(options: {
  onBooks?: () => unknown;
  onListChapters?: (args: Record<string, unknown>) => Promise<unknown>;
  onListChapterPages?: (args: Record<string, unknown>) => Promise<unknown>;
  onRegions?: (args: Record<string, unknown>) => unknown;
  onRetype?: (args: Record<string, unknown>) => Promise<unknown>;
  onIssue?: (args: Record<string, unknown>) => Promise<unknown>;
  onResolvePage?: (args: Record<string, unknown>) => Promise<unknown>;
  onWorkbenchCommand?: (command: string, args: Record<string, unknown>) => Promise<unknown> | unknown;
  rerender?: () => unknown;
} = {}) {
  const rows = new Map<string, RegionSummary[]>([
    ["page-1", [{ ...INTERACTIVE_REGION }]],
    ["page-2", [{ ...INTERACTIVE_REGION, region_id: "region-2" }]],
  ]);
  const invoke = vi.fn(async (command: string, args: Record<string, unknown> = {}) => {
    if (command === "library_list_books") return options.onBooks?.() ?? [];
    // M2-PAGE-NAV-PROJECTION-1: the navigation projections default to
    // empty fail-soft lists so the historical flows below keep their
    // shape; the drill-down cases pass explicit handlers.
    if (command === "list_chapters") {
      if (options.onListChapters) return options.onListChapters(args);
      return { chapters: [] };
    }
    if (command === "list_chapter_pages") {
      if (options.onListChapterPages) return options.onListChapterPages(args);
      return { pages: [] };
    }
    if (command === "resolve_page_resource") {
      // M2-PAGE-RESOURCE-RESOLVE-1: reject unless a fixture supplies a
      // resolved page key. The rejection is a
      // BARE string, the shape the real Tauri invoke rejects with (DSH r1
      // PR-09: registered as an intentional fixture deviation -- the
      // default is the opposite of the product default path).
      if (options.onResolvePage) return options.onResolvePage(args);
      throw "PAGE_NOT_FOUND";
    }
    if (command === "list_regions" && options.onRegions) return options.onRegions(args);
    if (command === "list_regions") return {
      regions: rows.get(String(args.pageId)) ?? [],
      page_size: { width: 100, height: 50 },
    };
    if (command === "set_region_type") {
      if (options.onRetype) return options.onRetype(args);
      const regionId = String(args.regionId);
      const page = String(args.pageId ?? "page-1");
      const list = rows.get(page) ?? [];
      const old = list.find((row) => row.region_id === regionId) ?? INTERACTIVE_REGION;
      const next = { ...old, region_type: args.newRegionType as RegionSummary["region_type"], revision_no: old.revision_no + 1 };
      rows.set(page, list.map((row) => row.region_id === regionId ? next : row));
      return { region_id: regionId, revision_no: next.revision_no, region_type: next.region_type, sfx_policy: next.sfx_policy };
    }
    if (command === "restore_region_revision") {
      const regionId = String(args.regionId);
      const current = rows.get("page-1")?.[0] ?? INTERACTIVE_REGION;
      const next = { ...current, region_type: "speech" as const, origin: "restored" as const, revision_no: current.revision_no + 1 };
      rows.set("page-1", [next]);
      return { region_id: regionId, revision_no: next.revision_no, region_type: next.region_type, sfx_policy: next.sfx_policy };
    }
    if (command === "list_region_revisions") return {
      region_id: "region-1",
      current_revision_no: rows.get("page-1")?.[0]?.revision_no ?? 1,
      revisions: [
        {
          region_revision_id: "revision-1",
          revision_no: 1,
          origin: "user",
          review_state: "accepted",
          is_pinned: true,
          restored_from_revision_id: null,
          created_at: "2026-10-01T00:00:00Z",
          region_type: "speech",
          sfx_policy: "skip",
          is_current: false,
        },
        {
          region_revision_id: "revision-2",
          revision_no: rows.get("page-1")?.[0]?.revision_no ?? 1,
          origin: rows.get("page-1")?.[0]?.origin ?? "user",
          review_state: "needs_review",
          is_pinned: false,
          restored_from_revision_id: null,
          created_at: "2026-10-02T00:00:00Z",
          region_type: rows.get("page-1")?.[0]?.region_type ?? "speech",
          sfx_policy: "skip",
          is_current: true,
        },
      ],
    };
    if (command === "rerender_page") return options.rerender?.() ?? {
      page_id: "page-1",
      artifact_id: "artifact-1",
      revision_no: 8,
      reports: [],
      preview: { resource_id: "preview-1", revision: "rev-8" },
      preview_error: null,
    };
    if (command === "issue_resource_url") return {
      ...(await options.onIssue?.(args) ?? {
        url: `http://m2res.localhost/m2id/${String(args.resourceId)}`,
        size: PREVIEW_PNG_BYTES.byteLength,
        opaque_id: String(args.resourceId),
      }),
    };
    if (options.onWorkbenchCommand) {
      const result = await options.onWorkbenchCommand(command, args);
      if (result !== undefined) return result;
    }
    return null;
  });
  return { invoke, rows };
}

describe("<WorkbenchPage> five-zone skeleton (mapping-contract names)", () => {
  it("places the toolbar beneath the three-column work area and above fixed progress", () => {
    const html = renderToString(<WorkbenchPage invoke={async () => null} />);
    expect(html.indexOf('data-testid="workbench-main-layout"')).toBeLessThan(html.indexOf('data-testid="workbench-toolbar"'));
    expect(html.indexOf('data-testid="workbench-toolbar"')).toBeLessThan(html.indexOf('data-testid="task-progress-panel"'));
  });
  it("renders the five zones with their data-testid pins", () => {
    const html = renderToString(<WorkbenchPage invoke={async () => null} />);
    expect(html).toContain('data-testid="workbench-page"');
    expect(html).toContain('data-testid="workbench-toolbar"');
    expect(html).toContain('data-testid="page-list-panel"');
    expect(html).toContain('data-testid="viewer-panel"');
    expect(html).toContain('data-testid="region-inspector"');
    expect(html).toContain('data-testid="task-progress-panel"');
  });

  it("renders the honest empty states before any data channel resolves", () => {
    const html = renderToString(<WorkbenchPage invoke={async () => null} />);
    expect(html).toContain('data-testid="page-list-empty"');
    expect(html).toContain('data-testid="viewer-empty"');
    expect(html).toContain('data-testid="inspector-empty"');
    expect(html).toContain('data-testid="gap-g15-run-discovery"');
    expect(html).not.toContain('data-testid="workbench-error"');
  });

  it("replaces the first-slice reserved retype controls with the IMPL-1 dual entry (M2-SFX-MISROUTE-UI-IMPL-1)", () => {
    // IMPL-1 landed: BOTH reserved disabled controls (inspector + toolbar)
    // are replaced by the real dual entry (Inspector buttons + overlay
    // context menu). With NO region selected the Inspector still renders no
    // retype buttons — entries only exist inside a selected-region block
    // (SSR renders the empty state).
    const html = renderToString(<WorkbenchPage invoke={async () => null} />);
    expect(html).not.toContain('data-testid="inspector-retype-reserved"');
    expect(html).not.toContain('data-testid="toolbar-retype-reserved"');
    expect(html).not.toContain('data-testid="inspector-mark-sfx"');
    expect(html).toContain('data-testid="region-inspector"');
  });

  it("keeps G15 Run discovery visible and disabled without a ListRuns command", () => {
    const html = renderToString(<WorkbenchPage invoke={async () => null} />);
    expect(html).toContain("Core 尚无 ListRuns 查询");
    expect(html).toContain('data-testid="gap-g15-run-discovery"');
  });

  it.each(["chapters", "pages"] as const)("shows a full-area Core error card when %s projection is unavailable", async (projection) => {
    const { invoke } = makeInteractiveInvoke({
      onBooks: () => [BOOK_A_ROW],
      onListChapters: () => projection === "chapters"
        ? Promise.reject(new Error("CORE_UNAVAILABLE"))
        : Promise.resolve({ chapters: [{ chapter_id: "chapter-1", title: "第一章", chapter_number: "1", sort_order: 1 }] }),
      onListChapterPages: () => Promise.reject(new Error("CORE_UNAVAILABLE")),
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.click("book-tile-book-a");
      if (projection === "pages") await ui.click("chapter-tile-chapter-1");
      expect(ui.container.querySelector('[data-testid="workbench-error"]')).not.toBeNull();
      expect(ui.container.querySelector('[data-testid="page-list-panel"]')).toBeNull();
    } finally {
      await ui.unmount();
    }
  });

  it("renders every §7 disabled entrance with an unavailable button and visible reason", async () => {
    const { invoke } = makeInteractiveInvoke();
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      const ids = [
        "gap-g9-save-manual-translation", "gap-g10-create-region", "gap-g10-delete-region",
        "gap-g11-region-geometry", "gap-g12-region-lock", "gap-g13-revision-pin",
        "gap-g14-page-order", "gap-g15-run-discovery", "gap-g16-core-availability",
        "gap-g18-page-thumbnails", "gap-g26-import-progress",
      ];
      const reasons: Record<string, string> = {
        "gap-g9-save-manual-translation": "接口尚未冻结",
        "gap-g10-create-region": "CreateRegion",
        "gap-g10-delete-region": "DeleteRegion",
        "gap-g11-region-geometry": "wire 尚未冻结",
        "gap-g12-region-lock": "Lock 写入接口",
        "gap-g13-revision-pin": "Revision pin 写入接口",
        "gap-g14-page-order": "Core 投影结果",
        "gap-g15-run-discovery": "ListRuns 查询",
        "gap-g16-core-availability": "可用性查询",
        "gap-g18-page-thumbnails": "缩略图能力",
        "gap-g26-import-progress": "细分进度 snapshot",
      };
      for (const id of ids) {
        const feature = ui.container.querySelector(`[data-testid="${id}"]`);
        const button = feature?.querySelector("button");
        const reason = feature?.querySelector("small");
        expect(button?.disabled, id).toBe(true);
        expect(reason?.textContent?.trim().length, id).toBeGreaterThan(0);
        expect(reason?.textContent, id).toContain(reasons[id]);
        expect(button?.getAttribute("aria-describedby"), id).toBe(reason?.id);
      }
      expect(invoke.mock.calls.some(([command]) => /list.?runs/i.test(command))).toBe(false);
    } finally {
      await ui.unmount();
    }
  });

  it("keeps the current-page thumbnail gap disabled when a Run projection exists", () => {
    const html = renderToString(
      <TaskProgressPanel
        projection={TASK_PROJECTION}
        collapsed={false}
        onToggleCollapsed={() => {}}
        onControl={() => {}}
        onResumeBlocked={() => {}}
        onRetryFailed={() => {}}
        onFilterStatus={() => {}}
        onLocatePage={() => {}}
          onRetry={() => {}}
      />,
    );
    const document = new JSDOM(html).window.document;
    const feature = document.querySelector('[data-testid="gap-g18-current-page-thumbnail"]');
    const button = feature?.querySelector("button") as HTMLButtonElement | null;
    const reason = feature?.querySelector("small");
    expect(button?.disabled).toBe(true);
    expect(reason?.textContent).toContain("缩略图通道尚未接入");
    expect(button?.getAttribute("aria-describedby")).toBe(reason?.id);
  });

  it("retains title, percent, current page, step, and controls in the 44px collapsed panel", () => {
    const html = renderToString(
      <TaskProgressPanel
        projection={TASK_PROJECTION}
        collapsed
        onToggleCollapsed={() => {}}
        onControl={() => {}}
        onResumeBlocked={() => {}}
        onRetryFailed={() => {}}
        onFilterStatus={() => {}}
        onLocatePage={() => {}}
          onRetry={() => {}}
      />,
    );
    const panel = new JSDOM(html).window.document.querySelector('[data-testid="task-progress-panel"]');
    expect(html).toContain("height:44px");
    expect(panel?.textContent).toContain("测试任务");
    expect(panel?.textContent).toContain("当前页：page-1");
    expect(panel?.textContent).toContain("当前步骤：render");
    expect(html).toContain('data-testid="run-control-pause"');
    expect(html).toContain('data-testid="run-control-retry-failed"');
  });

  it("renders task details in a floating popover above the progress panel", () => {
    const html = renderToString(
      <TaskProgressPanel
        projection={TASK_PROJECTION}
        collapsed={false}
        onToggleCollapsed={() => {}}
        onControl={() => {}}
        onResumeBlocked={() => {}}
        onRetryFailed={() => {}}
        onFilterStatus={() => {}}
        onLocatePage={() => {}}
        onRetry={() => {}}
      />,
    );
    const details = new JSDOM(html).window.document.querySelector('[data-testid="task-detail-popover"]');
    expect((details?.querySelector("div") as HTMLDivElement | null)?.style.position).toBe("absolute");
  });

  it("shows disabled Run controls when no Run is known", () => {
    const html = renderToString(
      <TaskProgressPanel
        projection={null}
        collapsed={false}
        onToggleCollapsed={() => {}}
        onControl={() => {}}
        onResumeBlocked={() => {}}
        onRetryFailed={() => {}}
        onFilterStatus={() => {}}
        onLocatePage={() => {}}
        onRetry={() => {}}
      />,
    );
    const buttons = [...new JSDOM(html).window.document.querySelectorAll('[data-testid="run-controls"] button')];
    expect(buttons).toHaveLength(7);
    expect(buttons.every((button) => (button as HTMLButtonElement).disabled)).toBe(true);
  });

  it("treats Run events as invalidation hints and reloads snapshot plus projection", async () => {
    const handlers = new Map<string, (event: { payload: unknown }) => void>();
    const listen: ListenFn = async (event, handler) => {
      handlers.set(event, handler as (event: { payload: unknown }) => void);
      return () => handlers.delete(event);
    };
    let snapshotReads = 0;
    let projectionReads = 0;
    const { invoke } = makeInteractiveInvoke({
      onBooks: () => [BOOK_A_ROW],
      onListChapters: () => Promise.resolve({ chapters: [{ chapter_id: "chapter-1", title: "Chapter 1", chapter_number: "1", sort_order: 1 }] }),
      onWorkbenchCommand: (command) => {
        if (command === "library_start_run") return { run_id: "run-1", status: "completed" };
        if (command === "library_get_run_snapshot") {
          snapshotReads += 1;
          return { run_id: "run-1", command: "translate_all", scope: { kind: "chapter", chapter_id: "chapter-1" }, status: "completed" };
        }
        if (command === "library_get_task_projection") {
          projectionReads += 1;
          return { ...TASK_PROJECTION, run_title: `快照 ${projectionReads}` };
        }
        return undefined;
      },
    });
    const ui = await mountInteractiveWorkbench(invoke, { listen });
    try {
      await ui.click("book-tile-book-a");
      await ui.click("chapter-tile-chapter-1");
      await ui.click("start-run");
      expect(snapshotReads).toBe(1);
      expect(projectionReads).toBe(1);

      await act(async () => {
        handlers.get("core:RunCompleted")?.({ payload: { run_id: "run-1", status: "running" } });
        await nextTurn();
      });
      expect(snapshotReads).toBe(2);
      expect(projectionReads).toBe(2);
      expect(ui.container.textContent).toContain("快照 2");
      expect(ui.container.textContent).toContain("状态：completed");
      expect(ui.container.textContent).not.toContain("状态：running");
    } finally {
      await ui.unmount();
    }
  });

  it("moves the focused page selection with ArrowUp and ArrowDown", async () => {
    const { invoke } = makeInteractiveInvoke({
      onBooks: () => [BOOK_A_ROW],
      onListChapters: () => Promise.resolve({ chapters: [{ chapter_id: "chapter-1", title: "Chapter 1", chapter_number: "1", sort_order: 1 }] }),
      onListChapterPages: () => Promise.resolve({ pages: [
        { page_id: "page-1", source_filename: "001.png", sort_order: 1 },
        { page_id: "page-2", source_filename: "002.png", sort_order: 2 },
      ] }),
      onResolvePage: (args) => Promise.resolve({ resource_id: `page-original-${String(args.pageId)}`, revision: "original" }),
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.click("book-tile-book-a");
      await ui.click("chapter-tile-chapter-1");
      const firstPage = ui.container.querySelector('[data-testid="page-tile-page-1"]') as HTMLButtonElement;
      firstPage.focus();
      await ui.keyDown("page-nav-list", "ArrowDown");
      expect((ui.container.querySelector('[data-testid="page-id-input"]') as HTMLInputElement).value).toBe("page-2");
      expect(ui.dom.window.document.activeElement?.getAttribute("data-testid")).toBe("page-tile-page-2");
      await ui.keyDown("page-nav-list", "ArrowUp");
      expect((ui.container.querySelector('[data-testid="page-id-input"]') as HTMLInputElement).value).toBe("page-1");
    } finally {
      await ui.unmount();
    }
  });

  it("supports V/R mode shortcuts and temporary Space panning", async () => {
    const ui = await mountInteractiveWorkbench(async () => null);
    try {
      const stage = ui.container.querySelector('[data-testid="viewer-stage"]') as HTMLElement;
      await ui.keyDown("viewer-stage", "r");
      expect((ui.container.querySelector('[data-testid="viewer-mode"]') as HTMLSelectElement).value).toBe("region");
      expect(stage.style.cursor).toBe("default");
      await ui.keyDown("viewer-stage", " ");
      expect(stage.style.cursor).toBe("grab");
      await ui.keyUp("viewer-stage", " ");
      expect(stage.style.cursor).toBe("default");
      await ui.keyDown("viewer-stage", "v");
      expect((ui.container.querySelector('[data-testid="viewer-mode"]') as HTMLSelectElement).value).toBe("pan");
      expect(stage.style.cursor).toBe("grab");
    } finally {
      await ui.unmount();
    }
  });

  it("selects Region frames with Enter from the keyboard", async () => {
    const { invoke } = makeInteractiveInvoke();
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      const frame = ui.container.querySelector('[data-testid="region-frame-region-1"]') as SVGRectElement | null;
      expect(frame?.getAttribute("role")).toBe("button");
      expect(frame?.getAttribute("tabindex")).toBe("0");
      frame?.focus();
      await ui.keyDown("region-frame-region-1", "Enter");
      expect(ui.container.querySelector('[data-testid="inspector-row-region-1"]')).not.toBeNull();
    } finally {
      await ui.unmount();
    }
  });

  it("maps Ctrl+P to pause/continue and Ctrl+. to stop when enabled", async () => {
    const actions: string[] = [];
    let runStatus = "running";
    const { invoke } = makeInteractiveInvoke({
      onBooks: () => [BOOK_A_ROW],
      onListChapters: () => Promise.resolve({ chapters: [{ chapter_id: "chapter-1", title: "Chapter 1", chapter_number: "1", sort_order: 1 }] }),
      onWorkbenchCommand: (command, args) => {
        if (command === "library_start_run") return { run_id: "run-keys", status: runStatus };
        if (command === "library_control_run") {
          actions.push(String(args.action));
          runStatus = args.action === "pause" ? "paused" : args.action === "continue" ? "running" : "cancelled";
          return { run_id: "run-keys", status: runStatus };
        }
        if (command === "library_get_run_snapshot") return { run_id: "run-keys", command: "translate_all", scope: { kind: "chapter", chapter_id: "chapter-1" }, status: runStatus };
        if (command === "library_get_task_projection") return {
          ...TASK_PROJECTION,
          run_id: "run-keys",
          run_status: runStatus,
          controls: {
            can_pause: runStatus === "running", can_stop: ["running", "paused"].includes(runStatus),
            can_continue: runStatus === "paused", can_restart: false, can_abandon: false, can_retry_failed: false,
          },
        };
        return undefined;
      },
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.click("book-tile-book-a");
      await ui.click("chapter-tile-chapter-1");
      await ui.click("start-run");
      await ui.keyDown("task-progress-panel", "p", { ctrlKey: true });
      expect(actions).toEqual(["pause"]);
      await ui.keyDown("task-progress-panel", "p", { ctrlKey: true });
      expect(actions).toEqual(["pause", "continue"]);
      await ui.keyDown("task-progress-panel", ".", { ctrlKey: true });
      expect(actions).toEqual(["pause", "continue", "stop"]);
    } finally {
      await ui.unmount();
    }
  });

  it("shows pause pending immediately and only replaces it after the authoritative snapshot", async () => {
    let runStatus = "running";
    let resolveControl!: (value: unknown) => void;
    const controlPending = new Promise<unknown>((resolve) => { resolveControl = resolve; });
    const { invoke } = makeInteractiveInvoke({
      onBooks: () => [BOOK_A_ROW],
      onListChapters: () => Promise.resolve({ chapters: [{ chapter_id: "chapter-1", title: "Chapter 1", chapter_number: "1", sort_order: 1 }] }),
      onWorkbenchCommand: (command) => {
        if (command === "library_start_run") return { run_id: "run-pending", status: runStatus };
        if (command === "library_control_run") { runStatus = "paused"; return controlPending; }
        if (command === "library_get_run_snapshot") return { run_id: "run-pending", command: "translate_all", scope: { kind: "chapter", chapter_id: "chapter-1" }, status: runStatus };
        if (command === "library_get_task_projection") return {
          ...TASK_PROJECTION, run_id: "run-pending", run_status: runStatus,
          controls: { ...TASK_PROJECTION.controls, can_pause: runStatus === "running", can_continue: runStatus === "paused" },
        };
        return undefined;
      },
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.click("book-tile-book-a");
      await ui.click("chapter-tile-chapter-1");
      await ui.click("start-run");
      await ui.click("run-control-pause");
      expect(ui.container.querySelector('[data-testid="run-control-pending"]')?.textContent).toBe("正在暂停…");
      resolveControl({ run_id: "run-pending", status: "paused" });
      await act(async () => { await nextTurn(); });
      expect(ui.container.querySelector('[data-testid="run-control-pending"]')).toBeNull();
      expect(ui.container.textContent).toContain("状态：paused");
    } finally {
      resolveControl({ run_id: "run-pending", status: "paused" });
      await ui.unmount();
    }
  });
});

describe("E4 feedback bar (ViewerPanel, r1 P1-1 error branch)", () => {
  it("shows loaded versus total resource chunks in the Viewer", () => {
    const html = renderToString(
      <ViewerPanel
        imageUrl={null}
        imageError={null}
        isLoading
        imageProgress={{ loadedChunks: 2, totalChunks: 5 }}
        regions={[]}
        pageSize={null}
        selectedRegionId={null}
        onSelectRegion={() => {}}
      />,
    );
    expect(html).toContain("正在读取页图（2 / 5 块）");
  });

  it("renders the error variant with the fail border and NO action buttons (failure must be visible)", () => {
    const html = renderToString(
      <ViewerPanel
        imageUrl={null}
        imageError={null}
        regions={[]}
        pageSize={null}
        selectedRegionId={null}
        onSelectRegion={() => {}}
        relabelFeedback={{
          regionId: "rg-9",
          text: "改标失败：INPUT_REVISION_CHANGED（region 未变更；INPUT_REVISION_CHANGED 时刷新后重试）",
          isError: true,
        }}
      />,
    );
    expect(html).toContain('data-testid="relabel-feedback"');
    expect(html).toContain("改标失败：INPUT_REVISION_CHANGED");
    // error variant carries no disabled action buttons (they belong to the
    // success variant only)
    expect(html).not.toContain('data-testid="feedback-undo"');
    expect(html).not.toContain('data-testid="feedback-rerender"');
  });

  it("renders enabled success actions when their callbacks and eligibility are present", () => {
    const html = renderToString(
      <ViewerPanel
        imageUrl={null}
        imageError={null}
        regions={[
          {
            region_id: "rg-1",
            region_type: "sfx",
            sfx_policy: "skip",
            origin: "machine",
            revision_no: 5,
          },
        ]}
        pageSize={null}
        selectedRegionId={null}
        onSelectRegion={() => {}}
        relabelFeedback={{ regionId: "rg-1", text: "已标记为拟声词", isError: false }}
        undoAvailable
        onUndo={() => {}}
        canRerender
        onRerender={() => {}}
      />,
    );
    expect(html).toContain('data-testid="feedback-undo"');
    expect(html).toContain('data-testid="feedback-rerender"');
    expect(html).toContain("撤销");
    expect(html).toContain("重渲染本页");
    expect(html.match(/data-testid="feedback-(?:undo|rerender)" disabled/g)).toBeNull();
  });
});

describe("<RegionOverlay> mitigation layers (M2-SFX-MISROUTE-UI-IMPL-1, design §3.2)", () => {
  const SPEECH_REGION: RegionSummary = {
    ...FRAME_REGION,
    region_id: "speech-1",
    region_type: "speech",
    sfx_policy: "skip",
  };

  it("renders E1 warning outline + E2 warn pill ONLY for a suspect-flagged speech region", () => {
    const html = renderToString(
      <RegionOverlay
        regions={[SPEECH_REGION, FRAME_REGION]}
        pageSize={{ width: 100, height: 50 }}
        selectedRegionId={null}
        suspects={new Set(["speech-1"])}
        containerWidth={200}
        containerHeight={100}
      />,
    );
    expect(html).toContain('data-testid="region-warn-speech-1"');
    expect(html).toContain("疑似拟声词");
    // speech-only scope (R-015): the flagged sfx region gets NO warning —
    // the sfx region shows its E3 type pill instead.
    expect(html).not.toContain('data-testid="region-warn-region-1"');
    expect(html).toContain('data-testid="region-badge-region-1"');
    expect(html).toContain("SFX · 拟声词翻译链");
  });

  it("renders E3 pill copy per the region policy snapshot (skip variant)", () => {
    const html = renderToString(
      <RegionOverlay
        regions={[{ ...FRAME_REGION, sfx_policy: "skip" }]}
        pageSize={{ width: 100, height: 50 }}
        selectedRegionId={null}
        containerWidth={200}
        containerHeight={100}
      />,
    );
    expect(html).toContain("SFX · 保留原文");
  });

  it("triple coding: badge carries glyph + text (color alone never carries the state, A8)", () => {
    const html = renderToString(
      <RegionOverlay
        regions={[SPEECH_REGION]}
        pageSize={{ width: 100, height: 50 }}
        selectedRegionId={null}
        suspects={new Set(["speech-1"])}
        containerWidth={200}
        containerHeight={100}
      />,
    );
    expect(html).toContain("♪?");
    expect(html).toContain("疑似拟声词");
  });

  it("no suspect flag -> no warning layers, no badge on plain speech (default silence)", () => {
    const html = renderToString(
      <RegionOverlay
        regions={[SPEECH_REGION]}
        pageSize={{ width: 100, height: 50 }}
        selectedRegionId={null}
        suspects={new Set()}
        containerWidth={200}
        containerHeight={100}
      />,
    );
    expect(html).not.toContain("疑似拟声词");
    expect(html).not.toContain("region-badge-speech-1");
  });

  it("interaction handlers absent -> frames stay non-interactive (first-slice behavior preserved)", () => {
    const html = renderToString(
      <RegionOverlay
        regions={[FRAME_REGION]}
        pageSize={{ width: 100, height: 50 }}
        selectedRegionId={null}
        containerWidth={200}
        containerHeight={100}
      />,
    );
    expect(html).toContain('data-testid="region-frame-region-1"');
  });
});

describe("<RegionOverlay> read-only SVG frames (M2-UI1 hard rules)", () => {
  it("cycles Tab focus through regions in the Core-projected reading order", async () => {
    const second = { ...INTERACTIVE_REGION, region_id: "region-2" };
    const { invoke } = makeInteractiveInvoke({
      onRegions: () => ({ regions: [INTERACTIVE_REGION, second], page_size: { width: 100, height: 50 } }),
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      const first = ui.container.querySelector('[data-testid="region-frame-region-1"]') as SVGRectElement;
      const next = ui.container.querySelector('[data-testid="region-frame-region-2"]') as SVGRectElement;
      first.focus();
      await ui.keyDown("region-frame-region-1", "Tab");
      expect(ui.dom.window.document.activeElement).toBe(next);
      await ui.keyDown("region-frame-region-2", "Tab", { shiftKey: true });
      expect(ui.dom.window.document.activeElement).toBe(first);
    } finally {
      await ui.unmount();
    }
  });

  it("shows the empty-region overlay after an empty ListRegions projection", async () => {
    const { invoke } = makeInteractiveInvoke({ onRegions: () => ({ regions: [], page_size: null }) });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      expect(ui.container.querySelector('[data-testid="viewer-no-regions"]')?.textContent).toBe("本页暂无 Region");
    } finally {
      await ui.unmount();
    }
  });

  it("draws the frame from normalized geometry through the single math", () => {
    const html = renderToString(
      <RegionOverlay
        regions={[FRAME_REGION]}
        pageSize={{ width: 100, height: 50 }}
        selectedRegionId="region-1"
        containerWidth={200}
        containerHeight={100}
      />,
    );
    expect(html).toContain('data-testid="region-overlay"');
    expect(html).toContain('data-testid="region-frame-region-1"');
    expect(html).toContain('x="20"');
    expect(html).toContain('y="20"');
    expect(html).toContain('width="60"');
    expect(html).toContain('height="40"');
    // the polygon ring rides the same view (dashed detail line):
    // normalized ring x 0.1/0.4 -> 20/80, y 0.2/0.6 -> 20/60
    expect(html).toContain('data-testid="region-ring-region-1"');
    expect(html).toContain("20,20 80,20 80,60 20,60");
  });

  it("stays silent for rows without geometry (an older Core projection)", () => {
    const noGeometry: RegionSummary = {
      region_id: "region-old",
      region_type: "speech",
      sfx_policy: "skip",
      origin: "machine",
      revision_no: 1,
    };
    const html = renderToString(
      <RegionOverlay
        regions={[noGeometry]}
        pageSize={{ width: 100, height: 50 }}
        selectedRegionId={null}
        containerWidth={200}
        containerHeight={100}
      />,
    );
    expect(html).toContain('data-testid="region-overlay"');
    expect(html).not.toContain("region-frame-region-old");
  });

  it("renders no fabricated placement when the page projection is absent", () => {
    const html = renderToString(
      <RegionOverlay
        regions={[FRAME_REGION]}
        pageSize={null}
        selectedRegionId={null}
        containerWidth={200}
        containerHeight={100}
      />,
    );
    expect(html).not.toContain("region-frame-region-1");
  });

  it("renders no frame before the container has been measured", () => {
    const html = renderToString(
      <RegionOverlay
        regions={[FRAME_REGION]}
        pageSize={{ width: 100, height: 50 }}
        selectedRegionId={null}
        containerWidth={0}
        containerHeight={0}
      />,
    );
    expect(html).not.toContain("region-frame-region-1");
  });
});

describe("RC-4 Workbench actual DOM actions", () => {
  it("clicks relabel, undoes through guarded restore, confirms history restore, then loads the render preview", async () => {
    const { invoke } = makeInteractiveInvoke();
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      await ui.click("region-frame-region-1");
      expect(ui.container.textContent).toContain("撤销仅在改标后 10 秒内、当前页且没有新操作时可用");
      await ui.click("inspector-toggle-suspect");
      await ui.click("inspector-mark-sfx");
      expect(ui.container.querySelector('[data-testid="feedback-undo"]')).not.toBeNull();
      expect(invoke).toHaveBeenCalledWith("set_region_type", {
        regionId: "region-1",
        newRegionType: "sfx",
        expectedRevision: 1,
      });

      await ui.click("feedback-undo");
      expect(invoke).toHaveBeenCalledWith("restore_region_revision", {
        regionId: "region-1",
        revisionNo: 1,
        expectedRevision: 2,
      });
      expect(ui.container.textContent).toContain("疑似拟声词");
      expect(ui.container.querySelector('[data-testid="feedback-undo"]')).toBeNull();

      await ui.click("inspector-revision-history");
      expect(ui.container.textContent).toContain("revision 1");
      expect(ui.container.textContent).toContain("已固定");
      await ui.click("restore-revision-1");
      expect(ui.container.querySelector('[data-testid="revision-restore-target"]')?.textContent)
        .toContain("revision 1 · user · speech");
      expect(ui.container.querySelector('[data-testid="revision-restore-dialog"]')?.textContent)
        .toContain("文字、类型、策略与锁状态（可能回退当前锁）");
      await ui.click("revision-restore-confirm");
      expect(invoke).toHaveBeenCalledWith("restore_region_revision", {
        regionId: "region-1",
        revisionNo: 1,
        expectedRevision: 3,
      });
      expect(ui.container.textContent).toContain("新增 current restored revision 4");

      await ui.click("feedback-rerender");
      expect(invoke).toHaveBeenCalledWith("rerender_page", { pageId: "page-1" });
      expect(invoke).toHaveBeenCalledWith("issue_resource_url", {
        resourceId: "preview-1",
        revision: "rev-8",
      });
      expect(ui.container.querySelector('[data-testid="viewer-image"]')?.getAttribute("src"))
        .toBe("blob:rc4-preview-1");
      expect(ui.resourceReads).toContain("http://m2res.localhost/m2id/preview-1?chunk=0");
      expect(ui.createdBlobs).toHaveLength(1);
      expect(ui.createdBlobs[0].size).toBe(PREVIEW_PNG_BYTES.byteLength);
      expect(new Uint8Array(await ui.createdBlobs[0].arrayBuffer())).toEqual(PREVIEW_PNG_BYTES);
      expect(ui.container.textContent).toContain("已重渲染并加载预览");
    } finally {
      await ui.unmount();
    }
  });

  it("shows a typed retype failure after the actual Inspector click", async () => {
    const { invoke } = makeInteractiveInvoke({
      onRetype: async () => { throw "INPUT_REVISION_CHANGED"; },
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      await ui.click("region-frame-region-1");
      await ui.click("inspector-mark-sfx");
      expect(ui.container.textContent).toContain("改标失败：INPUT_REVISION_CHANGED");
      expect(invoke.mock.calls.filter(([command]) => command === "set_region_type")).toHaveLength(1);
      expect(ui.container.querySelector('[data-testid="feedback-undo"]')).toBeNull();
    } finally {
      await ui.unmount();
    }
  });

  it("expires the undo click affordance at ten seconds", async () => {
    vi.useFakeTimers();
    const { invoke } = makeInteractiveInvoke();
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      await ui.click("region-frame-region-1");
      await ui.click("inspector-mark-sfx");
      expect(ui.container.querySelector('[data-testid="feedback-undo"]')).not.toBeNull();
      await act(async () => { await vi.advanceTimersByTimeAsync(10_001); });
      expect(ui.container.querySelector('[data-testid="feedback-undo"]')).toBeNull();
      expect(ui.container.querySelector('[data-testid="feedback-rerender"]')).not.toBeNull();
      expect(invoke).not.toHaveBeenCalledWith("restore_region_revision", expect.anything());
    } finally {
      await ui.unmount();
    }
  });

  it("invalidates undo on page change and ignores a late result from the previous page", async () => {
    let resolveRetype!: (value: unknown) => void;
    const pending = new Promise<unknown>((resolve) => { resolveRetype = resolve; });
    const { invoke } = makeInteractiveInvoke({ onRetype: () => pending });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      await ui.click("region-frame-region-1");
      await ui.click("inspector-mark-sfx");
      await ui.input("page-id-input", "page-2");
      expect(ui.container.querySelector('[data-testid="feedback-undo"]')).toBeNull();
      expect((ui.container.querySelector('[data-testid="page-id-input"]') as HTMLInputElement).value).toBe("page-2");
      resolveRetype({ region_id: "region-1", revision_no: 2, region_type: "sfx", sfx_policy: "skip" });
      await act(async () => { await nextTurn(); });
      expect(ui.container.querySelector('[data-testid="relabel-feedback"]')).toBeNull();
      expect(ui.container.querySelector('[data-testid="region-frame-region-2"]')).not.toBeNull();
    } finally {
      resolveRetype(null);
      await ui.unmount();
    }
  });

  it("keeps the rerender preview when an earlier page-resource resolve finishes late", async () => {
    let resolvePage!: (value: unknown) => void;
    const pendingPage = new Promise<unknown>((resolve) => { resolvePage = resolve; });
    const { invoke } = makeInteractiveInvoke({ onResolvePage: () => pendingPage });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      await ui.click("region-frame-region-1");
      await ui.click("inspector-mark-sfx");
      await ui.click("feedback-rerender");
      const previewUrl = ui.container.querySelector('[data-testid="viewer-image"]')?.getAttribute("src");
      expect(previewUrl).toBe("blob:rc4-preview-1");
      expect(ui.resourceReads).toContain("http://m2res.localhost/m2id/preview-1?chunk=0");

      resolvePage({ resource_id: "page-original-page-1", revision: "original" });
      await act(async () => { await nextTurn(); });
      expect(ui.container.querySelector('[data-testid="viewer-image"]')?.getAttribute("src"))
        .toBe(previewUrl);
      expect(ui.resourceReads).not.toContain("http://m2res.localhost/m2id/page-original-page-1?chunk=0");
      expect(ui.container.textContent).toContain("已重渲染并加载预览");
    } finally {
      resolvePage(null);
      await ui.unmount();
    }
  });

  it("shows typed preview resource read failures without reporting render failure", async () => {
    const { invoke } = makeInteractiveInvoke();
    const ui = await mountInteractiveWorkbench(invoke, {
      resourceFetch: async () => new Response(JSON.stringify({ code: "REF_EXPIRED" }), {
        status: 410,
        headers: { "content-type": "application/json" },
      }),
    });
    try {
      await ui.input("page-id-input", "page-1");
      await ui.click("region-frame-region-1");
      await ui.click("inspector-mark-sfx");
      await ui.click("feedback-rerender");
      expect(ui.container.textContent).toContain("渲染已提交（revision 8），但预览读取失败：REF_EXPIRED");
      expect(ui.container.textContent).not.toContain("重渲染失败");
      expect(ui.container.querySelector('[data-testid="viewer-image"]')).toBeNull();
    } finally {
      await ui.unmount();
    }
  });

  it("keeps preview publication failure separate from committed render failure", async () => {
    const { invoke } = makeInteractiveInvoke({
      rerender: () => ({
        page_id: "page-1",
        artifact_id: "artifact-1",
        revision_no: 8,
        reports: [],
        preview: null,
        preview_error: "PREVIEW_UNAVAILABLE",
      }),
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      await ui.click("region-frame-region-1");
      await ui.click("inspector-mark-sfx");
      await ui.click("feedback-rerender");
      expect(ui.container.textContent).toContain("渲染已提交（revision 8），但预览不可用：PREVIEW_UNAVAILABLE");
      expect(ui.container.textContent).not.toContain("重渲染失败");
      expect(ui.container.querySelector('[data-testid="feedback-rerender"]')).not.toBeNull();
    } finally {
      await ui.unmount();
    }
  });

  it("resolves the page resource automatically and feeds the image loader (M2-PAGE-RESOURCE-RESOLVE-1)", async () => {
    const { invoke } = makeInteractiveInvoke({
      onResolvePage: (args) => Promise.resolve({
        resource_id: `page-original-${String(args.pageId)}`,
        revision: "original",
      }),
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      expect(invoke).toHaveBeenCalledWith("resolve_page_resource", { pageId: "page-1" });
      expect(ui.container.querySelector('[data-testid="resource-id-input"]')).toBeNull();
      expect(ui.container.textContent).not.toContain("page-original-page-1");
      expect(ui.container.querySelector('[data-testid="resource-resolve-error"]')).toBeNull();
      expect(ui.container.querySelector('[data-testid="resource-resolve-busy"]')).toBeNull();
      expect(ui.container.querySelector('[data-testid="viewer-image"]')?.getAttribute("src"))
        .toBe("blob:rc4-preview-1");
      expect(ui.resourceReads).toContain("http://m2res.localhost/m2id/page-original-page-1?chunk=0");
    } finally {
      await ui.unmount();
    }
  });

  it("surfaces a typed resolve failure without exposing a resource fallback (M2-PAGE-RESOURCE-RESOLVE-1)", async () => {
    const { invoke } = makeInteractiveInvoke();
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      expect(ui.container.querySelector('[data-testid="viewer-empty"]')?.textContent)
        .toContain("PAGE_NOT_FOUND");
      expect(ui.container.querySelector('[data-testid="resource-id-input"]')).toBeNull();
      expect(ui.resourceReads).toHaveLength(0);
      expect(invoke).not.toHaveBeenCalledWith("issue_resource_url", expect.anything());
    } finally {
      await ui.unmount();
    }
  });

  it("drops a stale page-resource resolve that answers a page already switched away (M2-PAGE-RESOURCE-RESOLVE-1)", async () => {
    // DSH r1 PR-04: the resolve effect must re-check the current page id
    // when its reply lands, exactly like the region/history/image loops.
    // A late page-1 reply that lands after page-2 committed must never
    // feed page-1's key into page-2's viewer.
    let resolvePage1!: (value: unknown) => void;
    const pendingPage1 = new Promise<unknown>((resolve) => { resolvePage1 = resolve; });
    const { invoke } = makeInteractiveInvoke({
      onResolvePage: (args) => String(args.pageId) === "page-1"
        ? pendingPage1
        : Promise.resolve({
            resource_id: `page-original-${String(args.pageId)}`,
            revision: "original",
          }),
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1"); // resolve hangs
      await ui.input("page-id-input", "page-2"); // its own resolve settles
      expect(ui.container.querySelector('[data-testid="resource-id-input"]')).toBeNull();
      expect(ui.container.textContent).not.toContain("page-original-page-2");

      // the stale page-1 reply lands after the page-2 commit
      resolvePage1({ resource_id: "page-original-page-1", revision: "original" });
      await act(async () => { await nextTurn(); });
      expect(ui.resourceReads).toContain("http://m2res.localhost/m2id/page-original-page-2?chunk=0");
      expect(ui.resourceReads).not.toContain("http://m2res.localhost/m2id/page-original-page-1?chunk=0");
    } finally {
      resolvePage1({ resource_id: "page-original-page-1", revision: "original" });
      await ui.unmount();
    }
  });

  it("drills book -> chapter -> page and auto-loads the image (M2-PAGE-NAV-PROJECTION-1)", async () => {
    // AC4 integration smoke: a page click from the drill-down must drive
    // the existing resolve -> image chain end to end (no manual input).
    const { invoke } = makeInteractiveInvoke({
      onBooks: () => [{
        book_id: "book-1",
        title: "Test Manga",
        original_title: "テスト漫画",
        is_favorite: false,
        is_archived: false,
        page_count: 1,
        created_at: "2026-10-07T00:00:00Z",
        updated_at: "2026-10-07T00:00:00Z",
      }],
      onListChapters: () => Promise.resolve({
        chapters: [{ chapter_id: "ch-1", title: "First", chapter_number: "1", sort_order: 1 }],
      }),
      onListChapterPages: () => Promise.resolve({
        pages: [{ page_id: "p-nav-1", source_filename: "001.png", sort_order: 1 }],
      }),
      onResolvePage: (args) => Promise.resolve({
        resource_id: `page-original-${String(args.pageId)}`,
        revision: "original",
      }),
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.click("book-tile-book-1");
      expect(invoke).toHaveBeenCalledWith("list_chapters", { bookId: "book-1" });
      await ui.click("chapter-tile-ch-1");
      expect(invoke).toHaveBeenCalledWith("list_chapter_pages", { chapterId: "ch-1" });
      await ui.click("page-tile-p-nav-1");
      expect(invoke).toHaveBeenCalledWith("resolve_page_resource", { pageId: "p-nav-1" });
      const idInput = ui.container.querySelector('[data-testid="page-id-input"]') as HTMLInputElement | null;
      expect(idInput?.value).toBe("p-nav-1");
      expect(ui.container.querySelector('[data-testid="resource-id-input"]')).toBeNull();
      expect(ui.container.textContent).not.toContain("page-original-p-nav-1");
      expect(ui.container.querySelector('[data-testid="viewer-image"]')).not.toBeNull();
      expect(ui.resourceReads).toContain("http://m2res.localhost/m2id/page-original-p-nav-1?chunk=0");
    } finally {
      await ui.unmount();
    }
  });

  it("collapses the drill-down when the open book or chapter is clicked again (M2-PAGE-NAV-PROJECTION-1)", async () => {
    const { invoke } = makeInteractiveInvoke({
      onBooks: () => [{
        book_id: "book-1",
        title: "Test Manga",
        original_title: "テスト漫画",
        is_favorite: false,
        is_archived: false,
        page_count: 1,
        created_at: "2026-10-07T00:00:00Z",
        updated_at: "2026-10-07T00:00:00Z",
      }],
      onListChapters: () => Promise.resolve({
        chapters: [{ chapter_id: "ch-1", title: "First", chapter_number: "1", sort_order: 1 }],
      }),
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.click("book-tile-book-1");
      expect(ui.container.querySelector('[data-testid="chapter-list"]')).not.toBeNull();
      await ui.click("book-tile-book-1");
      expect(ui.container.querySelector('[data-testid="chapter-list"]')).toBeNull();

      // re-opening rebuilds the level, and the chapter level toggles too
      await ui.click("book-tile-book-1");
      await ui.click("chapter-tile-ch-1");
      expect(ui.container.querySelector('[data-testid="page-nav-list"]')).not.toBeNull();
      await ui.click("chapter-tile-ch-1");
      expect(ui.container.querySelector('[data-testid="page-nav-list"]')).toBeNull();
    } finally {
      await ui.unmount();
    }
  });

  it("resets the chapter selection when switching books, so no stale chapter stays clickable (DSH r1 PR-06, r2 N-01)", async () => {
    // The regression window this test must exercise: book-b's reply has NOT
    // landed yet. If the switch-book branch only cleared the selection and
    // not the rows, book-a's stale rows would stay rendered and clickable
    // here (a click would re-introduce a dangling chapter id).
    let resolveBookB!: (value: unknown) => void;
    const pendingBookB = new Promise<unknown>((resolve) => { resolveBookB = resolve; });
    const { invoke } = makeInteractiveInvoke({
      onBooks: () => [BOOK_A_ROW, BOOK_B_ROW],
      onListChapters: (args) => String(args.bookId) === "book-a"
        ? Promise.resolve({
            chapters: [{ chapter_id: "ch-a", title: "A first", chapter_number: "1", sort_order: 1 }],
          })
        : pendingBookB,
      onListChapterPages: () => Promise.resolve({
        pages: [{ page_id: "p-a", source_filename: "a.png", sort_order: 1 }],
      }),
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.click("book-tile-book-a");
      await ui.click("chapter-tile-ch-a");
      expect(ui.container.querySelector('[data-testid="page-nav-list"]')).not.toBeNull();

      // switching books must collapse the page level and drop book-a's rows
      // IMMEDIATELY -- book-b's reply is still pending, so nothing but the
      // immediate clear can explain what the next assertions see
      await ui.click("book-tile-book-b");
      expect(ui.container.querySelector('[data-testid="page-nav-list"]')).toBeNull();
      expect(ui.container.querySelector('[data-testid="chapter-tile-ch-a"]')).toBeNull();
      expect(ui.container.querySelector('[data-testid="chapters-busy"]')).not.toBeNull();

      // book-b's reply lands and only its own rows render
      resolveBookB({ chapters: [{ chapter_id: "ch-b", title: "B first", chapter_number: "1", sort_order: 1 }] });
      await act(async () => { await nextTurn(); });
      expect(ui.container.querySelector('[data-testid="chapter-tile-ch-b"]')).not.toBeNull();
      expect(ui.container.querySelector('[data-testid="chapter-tile-ch-a"]')).toBeNull();
      expect(ui.container.querySelector('[data-testid="chapters-busy"]')).toBeNull();
    } finally {
      resolveBookB({ chapters: [] });
      await ui.unmount();
    }
  });

  it("drops a stale chapter-list reply for a book already switched away (DSH r1 PR-8)", async () => {
    let resolveBookA!: (value: unknown) => void;
    const pendingBookA = new Promise<unknown>((resolve) => { resolveBookA = resolve; });
    const { invoke } = makeInteractiveInvoke({
      onBooks: () => [BOOK_A_ROW, BOOK_B_ROW],
      onListChapters: (args) => String(args.bookId) === "book-a"
        ? pendingBookA
        : Promise.resolve({
            chapters: [{ chapter_id: "ch-b", title: "B first", chapter_number: "1", sort_order: 1 }],
          }),
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.click("book-tile-book-a"); // hangs
      expect(ui.container.querySelector('[data-testid="chapters-busy"]')).not.toBeNull();
      await ui.click("book-tile-book-b"); // its own reply settles
      expect(ui.container.querySelector('[data-testid="chapter-tile-ch-b"]')).not.toBeNull();

      // the stale book-a reply lands after book-b committed
      resolveBookA({ chapters: [{ chapter_id: "ch-a", title: "A first", chapter_number: "1", sort_order: 1 }] });
      await act(async () => { await nextTurn(); });
      expect(ui.container.querySelector('[data-testid="chapter-tile-ch-b"]')).not.toBeNull();
      expect(ui.container.querySelector('[data-testid="chapter-tile-ch-a"]')).toBeNull();
    } finally {
      resolveBookA({ chapters: [] });
      await ui.unmount();
    }
  });

  it("collapses per-keypress typing into ONE deferred resolve (M2-RESOLVE-DEBOUNCE-1)", async () => {
    // PAGE-RESOLVE r1 PR-10: typing a page id by hand used to fire one
    // resolve per keypress (with per-prefix PAGE_NOT_FOUND flicker and
    // pointless publish attempts). With the 300ms quiet period the four
    // keystrokes must cost exactly ONE invoke, fired only after the timer.
    vi.useFakeTimers();
    try {
      const { invoke } = makeInteractiveInvoke({
        onResolvePage: (args) => Promise.resolve({
          resource_id: `page-original-${String(args.pageId)}`,
          revision: "original",
        }),
      });
      const ui = await mountInteractiveWorkbench(invoke, { resolveDebounceMs: 300 });
      try {
        await act(async () => {
          // four keystrokes, each resetting the quiet period
          await ui.input("page-id-input", "p");
          await ui.input("page-id-input", "pa");
          await ui.input("page-id-input", "pag");
          await ui.input("page-id-input", "page-1");
        });
        const resolveCalls = invoke.mock.calls.filter(([command]) => command === "resolve_page_resource");
        expect(resolveCalls).toHaveLength(0);
        // frozen semantics (Task 冻结范围): the busy indicator shows during
        // the quiet window, not only after the invoke fires (DSH r1 PR-02)
        expect(ui.container.querySelector('[data-testid="resource-resolve-busy"]')).not.toBeNull();

        await act(async () => {
          vi.advanceTimersByTime(300);
          await nextTurn();
        });
        const firedResolves = invoke.mock.calls.filter(([command]) => command === "resolve_page_resource");
        expect(firedResolves).toHaveLength(1);
        expect(firedResolves[0]).toEqual(["resolve_page_resource", { pageId: "page-1" }]);
        expect(ui.container.querySelector('[data-testid="resource-id-input"]')).toBeNull();
        expect(ui.container.textContent).not.toContain("page-original-page-1");
      } finally {
        await ui.unmount();
      }
    } finally {
      vi.useRealTimers();
    }
  });

  it("cancels the pending resolve timer when the page changes mid-quiet-period (M2-RESOLVE-DEBOUNCE-1)", async () => {
    vi.useFakeTimers();
    try {
      const { invoke } = makeInteractiveInvoke({
        onResolvePage: (args) => Promise.resolve({
          resource_id: `page-original-${String(args.pageId)}`,
          revision: "original",
        }),
      });
      const ui = await mountInteractiveWorkbench(invoke, { resolveDebounceMs: 300 });
      try {
        await act(async () => {
          await ui.input("page-id-input", "page-1");
          // switch pages before the quiet period elapses
          await ui.input("page-id-input", "page-2");
        });
        await act(async () => {
          vi.advanceTimersByTime(1_000);
          await nextTurn();
        });
        const resolveCalls = invoke.mock.calls.filter(([command]) => command === "resolve_page_resource");
        expect(resolveCalls).toHaveLength(1);
        // the surviving invoke is the page-2 one; page-1's timer was cancelled
        expect(resolveCalls[0]).toEqual(["resolve_page_resource", { pageId: "page-2" }]);
      } finally {
        await ui.unmount();
      }
    } finally {
      vi.useRealTimers();
    }
  });

  it("collapses per-keypress typing into ONE deferred region read (M2-REGION-DEBOUNCE-1)", async () => {
    // RESOLVE-DEBOUNCE r1 C-1: the region read loop shares the same
    // per-keypress problem -- deps [clients, pageId, refreshRegions] with a
    // stable callback fire list_regions once per keystroke. With the 300ms
    // quiet period the four keystrokes must cost exactly ONE invoke.
    vi.useFakeTimers();
    try {
      const { invoke } = makeInteractiveInvoke();
      const ui = await mountInteractiveWorkbench(invoke, { regionDebounceMs: 300 });
      try {
        await act(async () => {
          await ui.input("page-id-input", "p");
          await ui.input("page-id-input", "pa");
          await ui.input("page-id-input", "pag");
          await ui.input("page-id-input", "page-1");
        });
        const regionCalls = invoke.mock.calls.filter(([command]) => command === "list_regions");
        expect(regionCalls).toHaveLength(0);

        await act(async () => {
          vi.advanceTimersByTime(300);
          await nextTurn();
        });
        const firedRegions = invoke.mock.calls.filter(([command]) => command === "list_regions");
        expect(firedRegions).toHaveLength(1);
        expect(firedRegions[0]).toEqual(["list_regions", { pageId: "page-1" }]);
      } finally {
        await ui.unmount();
      }
    } finally {
      vi.useRealTimers();
    }
  });

  it("pins the 0ms direct-call path: a retype write-refresh stays immediate (M2-REGION-DEBOUNCE-1, DSH r1 PR-01 scope note)", async () => {
    // Scope note (r1 PR-01): this case runs at 0ms, so it pins the
    // DIRECT-call path -- refreshRegions itself is untouched by the
    // debounce wrapper -- but it does NOT exercise the 300ms product
    // default; the "write-refresh stays immediate UNDER the debounce"
    // discrimination is registered as a residual (the fake-timer UI chain
    // to the Inspector retype buttons does not settle in this harness).
    // Structurally the wrapper only wraps the effect body, never the
    // function (refreshRegions body is byte-identical to base), so a
    // write-refresh cannot reach the timer.
    const { invoke } = makeInteractiveInvoke();
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      expect(invoke).toHaveBeenCalledWith("list_regions", { pageId: "page-1" });
      await ui.click("region-frame-region-1");
      await ui.click("inspector-mark-sfx");
      const refresh = invoke.mock.calls.filter(([command]) => command === "list_regions");
      expect(refresh.length).toBeGreaterThanOrEqual(2);
    } finally {
      await ui.unmount();
    }
  });

  it("displays the frozen preview code even when Core reports a different one", async () => {
    // RC4-13: the UI fail-closes on the frozen PREVIEW_UNAVAILABLE literal;
    // it must not echo an arbitrary Core-side preview_error back to the user.
    const { invoke } = makeInteractiveInvoke({
      rerender: () => ({
        page_id: "page-1",
        artifact_id: "artifact-1",
        revision_no: 8,
        reports: [],
        preview: null,
        preview_error: "CORE_INTERNAL_PREVIEW_CODE",
      }),
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      await ui.click("region-frame-region-1");
      await ui.click("inspector-mark-sfx");
      await ui.click("feedback-rerender");
      expect(ui.container.textContent).toContain("渲染已提交（revision 8），但预览不可用：PREVIEW_UNAVAILABLE");
      expect(ui.container.textContent).not.toContain("CORE_INTERNAL_PREVIEW_CODE");
      expect(ui.container.querySelector('[data-testid="feedback-rerender"]')).not.toBeNull();
    } finally {
      await ui.unmount();
    }
  });
});
