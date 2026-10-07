import { renderToString } from "react-dom/server";
import { act } from "react";
import { JSDOM } from "jsdom";
import { describe, expect, it, vi } from "vitest";
import { RegionOverlay } from "../region/RegionOverlay";
import type { RegionSummary } from "../region/types";
import { ViewerPanel } from "./ViewerPanel";
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
  options: { resourceFetch?: typeof fetch; resolveDebounceMs?: number; regionDebounceMs?: number } = {},
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
  const unmount = async () => {
    await act(async () => root.unmount());
    dom.window.close();
    vi.useRealTimers();
    vi.unstubAllGlobals();
  };
  return { dom, container, click, input, createdBlobs, revokedUrls, resourceReads, unmount };
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

function makeInteractiveInvoke(options: {
  onBooks?: () => unknown;
  onListChapters?: (args: Record<string, unknown>) => Promise<unknown>;
  onListChapterPages?: (args: Record<string, unknown>) => Promise<unknown>;
  onRetype?: (args: Record<string, unknown>) => Promise<unknown>;
  onIssue?: (args: Record<string, unknown>) => Promise<unknown>;
  onResolvePage?: (args: Record<string, unknown>) => Promise<unknown>;
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
      // M2-PAGE-RESOURCE-RESOLVE-1: default OFF (typed PAGE_NOT_FOUND) so
      // the manual/preview flows below keep their historical timing; the
      // auto-load cases pass onResolvePage explicitly. The rejection is a
      // BARE string, the shape the real Tauri invoke rejects with (DSH r1
      // PR-09: registered as an intentional fixture deviation -- the
      // default is the opposite of the product default path).
      if (options.onResolvePage) return options.onResolvePage(args);
      throw "PAGE_NOT_FOUND";
    }
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
    return null;
  });
  return { invoke, rows };
}

describe("<WorkbenchPage> five-zone skeleton (mapping-contract names)", () => {
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
    expect(html).toContain('data-testid="task-progress-placeholder"');
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

  it("keeps the task progress placeholder free of any new command face", () => {
    // the placeholder text documents WHY there is no data wire: standing up
    // a command face for a placeholder is explicitly forbidden (Task AC2)
    const html = renderToString(<WorkbenchPage invoke={async () => null} />);
    expect(html).toContain("占位不扩命令面");
  });
});

describe("E4 feedback bar (ViewerPanel, r1 P1-1 error branch)", () => {
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
      expect(ui.container.textContent).toContain("page page-2");
      resolveRetype({ region_id: "region-1", revision_no: 2, region_type: "sfx", sfx_policy: "skip" });
      await act(async () => { await nextTurn(); });
      expect(ui.container.querySelector('[data-testid="relabel-feedback"]')).toBeNull();
      expect(ui.container.querySelector('[data-testid="region-frame-region-2"]')).not.toBeNull();
    } finally {
      resolveRetype(null);
      await ui.unmount();
    }
  });

  it("drops a manual resource read that completes after switching pages", async () => {
    let resolveManualIssue!: (value: unknown) => void;
    const manualIssue = new Promise<unknown>((resolve) => { resolveManualIssue = resolve; });
    const { invoke } = makeInteractiveInvoke({
      onIssue: (args) => String(args.resourceId) === "manual-A"
        ? manualIssue
        : Promise.resolve({
            url: `http://m2res.localhost/m2id/${String(args.resourceId)}`,
            size: PREVIEW_PNG_BYTES.byteLength,
            opaque_id: String(args.resourceId),
          }),
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      await ui.input("resource-id-input", "manual-A");
      expect(invoke).toHaveBeenCalledWith("issue_resource_url", {
        resourceId: "manual-A",
        revision: "current",
      });

      await ui.input("page-id-input", "page-2");
      expect(ui.container.querySelector('[data-testid="viewer-image"]')).toBeNull();

      resolveManualIssue({
        url: "http://m2res.localhost/m2id/manual-A",
        size: PREVIEW_PNG_BYTES.byteLength,
        opaque_id: "manual-A",
      });
      await act(async () => { await nextTurn(); });
      expect(ui.resourceReads).toContain("http://m2res.localhost/m2id/manual-A?chunk=0");
      expect(ui.container.querySelector('[data-testid="viewer-image"]')).toBeNull();
      expect(ui.revokedUrls).toContain("blob:rc4-preview-1");
      expect(ui.container.textContent).toContain("page page-2");
    } finally {
      resolveManualIssue(null);
      await ui.unmount();
    }
  });

  it("keeps the rerender preview when an earlier manual resource read finishes late", async () => {
    let resolveManualIssue!: (value: unknown) => void;
    const manualIssue = new Promise<unknown>((resolve) => { resolveManualIssue = resolve; });
    const { invoke } = makeInteractiveInvoke({
      onIssue: (args) => String(args.resourceId) === "manual-before-render"
        ? manualIssue
        : Promise.resolve({
            url: `http://m2res.localhost/m2id/${String(args.resourceId)}`,
            size: PREVIEW_PNG_BYTES.byteLength,
            opaque_id: String(args.resourceId),
          }),
    });
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      await ui.click("region-frame-region-1");
      await ui.click("inspector-mark-sfx");
      await ui.input("resource-id-input", "manual-before-render");

      await ui.click("feedback-rerender");
      const previewUrl = ui.container.querySelector('[data-testid="viewer-image"]')?.getAttribute("src");
      expect(previewUrl).toBe("blob:rc4-preview-1");
      expect(ui.resourceReads).toContain("http://m2res.localhost/m2id/preview-1?chunk=0");

      resolveManualIssue({
        url: "http://m2res.localhost/m2id/manual-before-render",
        size: PREVIEW_PNG_BYTES.byteLength,
        opaque_id: "manual-before-render",
      });
      await act(async () => { await nextTurn(); });
      expect(ui.resourceReads).toContain("http://m2res.localhost/m2id/manual-before-render?chunk=0");
      expect(ui.container.querySelector('[data-testid="viewer-image"]')?.getAttribute("src"))
        .toBe(previewUrl);
      expect(ui.revokedUrls).toContain("blob:rc4-preview-2");
      expect(ui.container.textContent).toContain("已重渲染并加载预览");
    } finally {
      resolveManualIssue(null);
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
      const idInput = ui.container.querySelector('[data-testid="resource-id-input"]') as HTMLInputElement | null;
      expect(idInput?.value).toBe("page-original-page-1");
      expect(ui.container.querySelector('[data-testid="resource-resolve-error"]')).toBeNull();
      expect(ui.container.querySelector('[data-testid="resource-resolve-busy"]')).toBeNull();
      expect(ui.container.querySelector('[data-testid="viewer-image"]')?.getAttribute("src"))
        .toBe("blob:rc4-preview-1");
      expect(ui.resourceReads).toContain("http://m2res.localhost/m2id/page-original-page-1?chunk=0");
    } finally {
      await ui.unmount();
    }
  });

  it("surfaces a typed resolve failure and keeps the manual resource fallback (M2-PAGE-RESOURCE-RESOLVE-1)", async () => {
    const { invoke } = makeInteractiveInvoke();
    const ui = await mountInteractiveWorkbench(invoke);
    try {
      await ui.input("page-id-input", "page-1");
      expect(ui.container.querySelector('[data-testid="resource-resolve-error"]')?.textContent)
        .toBe("resource: PAGE_NOT_FOUND");
      const idInput = ui.container.querySelector('[data-testid="resource-id-input"]') as HTMLInputElement | null;
      expect(idInput?.value).toBe("");
      expect(ui.resourceReads).toHaveLength(0);
      // the manual fallback still drives the existing image loader
      await ui.input("resource-id-input", "manual-fallback");
      expect(invoke).toHaveBeenCalledWith("issue_resource_url", {
        resourceId: "manual-fallback",
        revision: "current",
      });
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
    const resourceIdInput = () =>
      ui.container.querySelector('[data-testid="resource-id-input"]') as HTMLInputElement | null;
    try {
      await ui.input("page-id-input", "page-1"); // resolve hangs
      await ui.input("page-id-input", "page-2"); // its own resolve settles
      expect(resourceIdInput()?.value).toBe("page-original-page-2");

      // the stale page-1 reply lands after the page-2 commit
      resolvePage1({ resource_id: "page-original-page-1", revision: "original" });
      await act(async () => { await nextTurn(); });
      expect(resourceIdInput()?.value).toBe("page-original-page-2");
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
      const resourceInput = ui.container.querySelector('[data-testid="resource-id-input"]') as HTMLInputElement | null;
      expect(resourceInput?.value).toBe("page-original-p-nav-1");
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
        const resourceInput = ui.container.querySelector('[data-testid="resource-id-input"]') as HTMLInputElement | null;
        expect(resourceInput?.value).toBe("page-original-page-1");
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

  it("keeps write-refresh region reads immediate under the debounce (M2-REGION-DEBOUNCE-1)", async () => {
    // The debounce defers only the effect-driven read; the retype flow's
    // refreshRegions call must stay immediate (0ms config here, so this
    // pins the direct-call path is untouched by the deferred wrapper).
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
